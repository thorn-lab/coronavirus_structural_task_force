"""Run AUSPEX reflection diagnostics for one structure entry."""

import logging
import os
import shutil
from pathlib import Path

from cstf.validate.base import Entry, ValidationStep
from cstf.validate.docker_service import ContainerService, DockerServiceError

logger = logging.getLogger("xtal_validation.orchestrator.auspex")
AUSPEX_IMAGE = os.environ.get("AUSPEX_IMAGE", "auspex:amd64")
AUSPEX_PLATFORM = os.environ.get("AUSPEX_PLATFORM", "linux/amd64")
AUSPEX_ARGS = ["--directory", "{out}", "{mtz}"]
IMAGE_EXTS = {".jpg", ".jpeg", ".png"}


class AuspexStep(ValidationStep):
    """Run AUSPEX and retain the amplitude plot."""

    name = "auspex"

    def __init__(self, *, skip_existing=True, service=None, **options):
        super().__init__(skip_existing=skip_existing, **options)
        self.service = service

    def check_input(self, entry: Entry):
        return None if entry.files.get("mtz") else "no_input: no .mtz file found"

    def output_dir(self, entry: Entry) -> Path:
        return entry.auspex_dir

    def target(self, entry: Entry) -> Path:
        return entry.auspex_dir / "amplitudes.jpg"

    def is_complete(self, entry: Entry) -> bool:
        return self.target(entry).is_file()

    def execute(self, entry: Entry) -> Path:
        mtz = Path(entry.files["mtz"]).resolve()
        out_dir = entry.auspex_dir.resolve()
        out_jpg = self.target(entry).resolve()
        if not mtz.is_file():
            raise FileNotFoundError("MTZ not found: {}".format(mtz))
        out_dir.mkdir(parents=True, exist_ok=True)

        service = self.service
        owns_service = service is None
        if owns_service:
            root = os.path.commonpath([str(mtz), str(out_dir), str(out_jpg)])
            service = ContainerService(AUSPEX_IMAGE, AUSPEX_PLATFORM, root)

        try:
            before = self._snapshot(out_dir)
            base_args = [arg.format(mtz=str(mtz), out=str(out_dir)) for arg in AUSPEX_ARGS]
            args = (
                base_args[:-1]
                + list(self.options.get("extra_args") or [])
                + base_args[-1:]
            )
            try:
                process = service.exec(
                    args,
                    workdir=out_dir,
                    timeout=self.options.get("timeout", 1800),
                )
            except DockerServiceError as exc:
                raise RuntimeError(str(exc)) from exc
        finally:
            if owns_service:
                service.stop()

        if process.returncode != 0:
            tail = (process.stderr or process.stdout or "").strip()[-1500:]
            raise RuntimeError("AUSPEX exited with code {}: {}".format(process.returncode, tail))

        after = self._snapshot(out_dir)
        changed = [path for path, stamp in after.items() if before.get(path) != stamp]
        plots = sorted(
            (path for path in changed if path.suffix.lower() in IMAGE_EXTS and path != out_jpg),
            key=lambda path: path.name,
        )
        if not plots:
            raise RuntimeError(
                "AUSPEX ran but wrote no image files. stdout: {}".format(
                    (process.stdout or "").strip()[-500:]
                )
            )
        amplitude_plots = [path for path in plots if "amplitude" in path.name.lower()]
        chosen = (amplitude_plots or plots)[0]
        if not amplitude_plots:
            logger.warning("AUSPEX: no amplitude-named plot; using %s", chosen.name)
        self._to_jpeg(chosen, out_jpg)
        if not self.options.get("keep_extra", True):
            for path in changed:
                if path != out_jpg and path.exists():
                    path.unlink()
        return out_jpg

    @staticmethod
    def _snapshot(directory: Path):
        return {path: path.stat().st_mtime_ns for path in directory.iterdir() if path.is_file()}

    @staticmethod
    def _to_jpeg(source: Path, destination: Path):
        if source.suffix.lower() in {".jpg", ".jpeg"}:
            shutil.copyfile(source, destination)
            return
        try:
            from PIL import Image
        except ImportError as exc:
            raise RuntimeError(
                "AUSPEX produced {} but Pillow is needed to convert it to JPEG".format(source.name)
            ) from exc
        with Image.open(source) as image:
            image.convert("RGB").save(destination, "JPEG", quality=95)
