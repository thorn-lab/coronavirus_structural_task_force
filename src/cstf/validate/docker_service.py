"""
docker_service.py

A long-lived Docker container used via `docker exec`, so each validation tool
image is started once per pipeline run instead of once per PDB entry.

How it works:
  * the image is started idle (`--entrypoint sleep infinity`)
  * `mount_root` (the repo root) is bind-mounted at the SAME path inside the
    container, so host paths can be passed to the tool unchanged
  * the image's own ENTRYPOINT is read once and prepended to every exec, so
    callers only supply the tool's arguments
  * start is lazy: nothing runs until the first exec()

Use as a context manager so the container is always stopped:

    with ContainerService("auspex:amd64", "linux/amd64", repo_root) as svc:
        svc.exec(["-f", "/data/repo/1abc/1abc.mtz"], workdir="/data/repo/1abc/validation/auspex")
"""

import atexit
import json
import logging
import os
import subprocess
import uuid
from pathlib import Path

logger = logging.getLogger("xtal_validation.orchestrator.docker")


class DockerServiceError(RuntimeError):
    pass


class ContainerService:
    def __init__(self, image, platform, mount_root, env=None, name=None):
        self.image = image
        self.platform = platform
        self.mount_root = Path(mount_root).resolve()
        base = image.split(":")[0].replace("/", "_")
        self.name = name or "xtal-{}-{}".format(base, uuid.uuid4().hex[:8])
        self.env = {"HOME": "/tmp", "MPLCONFIGDIR": "/tmp/mpl", "MPLBACKEND": "Agg"}
        self.env.update(env or {})
        self._entrypoint = None

    # -- lifecycle ---------------------------------------------------------

    def __enter__(self):
        return self  # lazy: containers start on first exec()

    def __exit__(self, *exc):
        self.stop()

    def _docker(self, args, **kw):
        try:
            return subprocess.run(
                ["docker"] + args, capture_output=True, text=True, **kw
            )
        except FileNotFoundError:
            raise DockerServiceError("docker executable not found")

    def is_running(self):
        r = self._docker(["inspect", "-f", "{{.State.Running}}", self.name])
        return r.returncode == 0 and r.stdout.strip() == "true"

    def start(self):
        if self.is_running():
            return

        r = self._docker(
            ["image", "inspect", "-f", "{{json .Config.Entrypoint}}", self.image]
        )
        if r.returncode != 0:
            raise DockerServiceError(
                "Docker image {} not found; run setup-validation-docker.sh".format(
                    self.image
                )
            )
        self._entrypoint = json.loads(r.stdout.strip() or "null") or []

        root = str(self.mount_root)
        cmd = [
            "run",
            "-d",
            "--rm",
            "--name",
            self.name,
            "--platform",
            self.platform,
            "--user",
            "{}:{}".format(os.getuid(), os.getgid()),
            "--entrypoint",
            "sleep",
            "-v",
            "{0}:{0}".format(root),
            "-w",
            root,
        ]
        for k, v in self.env.items():
            cmd += ["-e", "{}={}".format(k, v)]
        cmd += [self.image, "infinity"]

        r = self._docker(cmd)
        if r.returncode != 0:
            raise DockerServiceError(
                "Could not start {}: {}".format(self.image, r.stderr.strip()[-500:])
            )
        atexit.register(
            self.stop
        )  # safety net if the caller never exits the with-block
        logger.info("Started container %s (%s)", self.name, self.image)

    def stop(self):
        self._docker(["stop", "-t", "2", self.name])  # --rm removes it; ignore errors

    # -- use ---------------------------------------------------------------

    def check_inside(self, *paths):
        """Raise if any path is not under the mounted root (it would not exist
        inside the container)."""
        for p in paths:
            try:
                Path(p).resolve().relative_to(self.mount_root)
            except ValueError:
                raise DockerServiceError(
                    "{} is outside the container mount root {}".format(
                        p, self.mount_root
                    )
                )

    def exec(self, args, workdir=None, timeout=None):
        """
        Run the image's entrypoint with `args` inside the container.
        Returns the CompletedProcess (text mode). Does not raise on non-zero
        exit; the caller inspects returncode. On timeout the container is
        stopped (to kill the runaway process) and DockerServiceError raised;
        the next exec() restarts it.
        """
        self.start()
        workdir = Path(workdir).resolve() if workdir else self.mount_root
        self.check_inside(workdir)

        cmd = (
            ["exec", "-w", str(workdir), self.name]
            + self._entrypoint
            + [str(a) for a in args]
        )
        logger.info("%s exec: %s", self.name, " ".join(cmd[4:]))
        try:
            return self._docker(cmd, timeout=timeout)
        except subprocess.TimeoutExpired:
            self.stop()
            raise DockerServiceError(
                "{} timed out after {}s".format(self.image, timeout)
            )
