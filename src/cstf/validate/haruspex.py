"""
haruspex.py

Runs Haruspex on a cryo-EM density map inside the persistent
``haruspex:arm64`` container (see docker_service.ContainerService).

Haruspex is EM-only in this pipeline: the orchestrator calls it only when
exp_method == "ELECTRON MICROSCOPY", and the input is the entry's map file
(.mrc / .map / .ccp4), not an MTZ.

!! Verify the CLI once:  docker run --rm haruspex:arm64 --help
   and adjust HARUSPEX_ARGS below if the flags differ from what is assumed.

Public API:
    find_map(path) -> Path | None
    run_haruspex(map_path, output_dir, service=None, ...) -> list[Path]
"""

import logging
import os
from pathlib import Path

from cstf.validate.docker_service import ContainerService, DockerServiceError

logger = logging.getLogger("xtal_validation.orchestrator.haruspex")

HARUSPEX_IMAGE = os.environ.get("HARUSPEX_IMAGE", "haruspex:arm64")
HARUSPEX_PLATFORM = os.environ.get("HARUSPEX_PLATFORM", "linux/arm64")

# Args passed to the image's entrypoint. {map} -> map path, {out} -> output dir.
# ASSUMPTION: map is a positional argument and results go to the working dir.
HARUSPEX_ARGS = ["{map}"]

MAP_EXTS = (".mrc", ".map", ".ccp4")
SKIP_IN_NAME = ("half", "mask", "msk")  # prefer the full map over half maps/masks
LOG_NAMES = {"haruspex_stdout.log", "haruspex_stderr.log"}


class HaruspexError(RuntimeError):
    pass


def find_map(path):
    """Return the primary density map in `path` (or None). Full maps are
    preferred over half maps and masks; compressed maps (.gz) are ignored,
    so gunzip them first."""
    path = Path(path)
    if not path.is_dir():
        return None
    maps = sorted(
        f for f in path.iterdir() if f.is_file() and f.name.lower().endswith(MAP_EXTS)
    )
    if not maps:
        return None
    primary = [f for f in maps if not any(s in f.name.lower() for s in SKIP_IN_NAME)]
    return (primary or maps)[0]


def _snapshot(directory):
    return {p: p.stat().st_mtime_ns for p in directory.iterdir() if p.is_file()}


def run_haruspex(map_path, output_dir, service=None, timeout=3600, extra_args=None):
    """
    Run Haruspex on a map and return the files it produced in output_dir.

    Args:
        service: ContainerService for HARUSPEX_IMAGE (shared across entries).
            If None, a temporary container is started and stopped.

    Raises HaruspexError on failure, including "ran but wrote nothing".
    """
    in_map = Path(map_path).resolve()
    out_dir = Path(output_dir).resolve()
    if not in_map.is_file():
        raise HaruspexError("Map not found: {}".format(in_map))
    out_dir.mkdir(parents=True, exist_ok=True)

    own = service is None
    if own:
        root = os.path.commonpath([str(in_map), str(out_dir)])
        service = ContainerService(HARUSPEX_IMAGE, HARUSPEX_PLATFORM, root)

    try:
        before = _snapshot(out_dir)
        args = [a.format(map=str(in_map), out=str(out_dir)) for a in HARUSPEX_ARGS]
        args += list(extra_args or [])
        try:
            proc = service.exec(args, workdir=out_dir, timeout=timeout)
        except DockerServiceError as exc:
            raise HaruspexError(str(exc)) from exc
    finally:
        if own:
            service.stop()

    (out_dir / "haruspex_stdout.log").write_text(proc.stdout or "")
    (out_dir / "haruspex_stderr.log").write_text(proc.stderr or "")

    if proc.returncode != 0:
        tail = (proc.stderr or proc.stdout or "").strip()[-1500:]
        raise HaruspexError(
            "Haruspex exited with code {}: {}".format(proc.returncode, tail)
        )

    after = _snapshot(out_dir)
    produced = sorted(
        p for p, t in after.items() if before.get(p) != t and p.name not in LOG_NAMES
    )
    if not produced:
        raise HaruspexError(
            "Haruspex exited cleanly but wrote no output files "
            "(check HARUSPEX_ARGS and haruspex_stdout.log)"
        )
    return produced
