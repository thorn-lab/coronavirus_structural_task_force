"""
auspex.py

Runs AUSPEX (reflection-data diagnostics) inside the persistent ``auspex:amd64``
container (see docker_service.ContainerService) and leaves a single
``amplitudes.jpg`` at the requested location.

!! Verify the CLI once:  docker run --rm auspex:amd64 --help
   and adjust AUSPEX_ARGS below if the flags differ from what is assumed.

Public API:
    run_auspex(mtz_path, output_dir, output_jpg, service=None, ...) -> Path
"""

import logging
import os
import shutil
from pathlib import Path

from cstf.validate.docker_service import ContainerService, DockerServiceError

logger = logging.getLogger("xtal_validation.orchestrator.auspex")

AUSPEX_IMAGE = os.environ.get("AUSPEX_IMAGE", "auspex:amd64")
AUSPEX_PLATFORM = os.environ.get("AUSPEX_PLATFORM", "linux/amd64")

# Args passed to the image's entrypoint (the `auspex` binary), matching
# `auspex --help`: output directory via --directory, reflection file as the
# positional HKLIN argument (placed last).
#   {out} -> output directory, {mtz} -> reflection file (both host paths,
#   which are identical inside the container).
AUSPEX_ARGS = ["--directory", "{out}", "{mtz}"]

IMAGE_EXTS = {".jpg", ".jpeg", ".png"}


class AuspexError(RuntimeError):
    pass


def _snapshot(directory):
    return {p: p.stat().st_mtime_ns for p in directory.iterdir() if p.is_file()}


def _to_jpeg(src, dst):
    if src.suffix.lower() in {".jpg", ".jpeg"}:
        shutil.copyfile(src, dst)
        return
    try:
        from PIL import Image
    except ImportError as exc:
        raise AuspexError(
            "AUSPEX produced {} but Pillow is needed to convert it to JPEG".format(
                src.name
            )
        ) from exc
    with Image.open(src) as im:
        im.convert("RGB").save(dst, "JPEG", quality=95)


def run_auspex(
    mtz_path,
    output_dir,
    output_jpg,
    service=None,
    timeout=1800,
    extra_args=None,
    keep_extra=False,
):
    """
    Run AUSPEX on an MTZ and write the amplitudes plot to output_jpg.

    Args:
        service: a running-or-lazy ContainerService for AUSPEX_IMAGE. Pass the
            one the orchestrator owns so the container is reused. If None, a
            temporary container is started and stopped for this call.
        keep_extra: keep other files AUSPEX produced (default: delete the ones
            newly created by this run so only amplitudes.jpg remains)

    Raises AuspexError on any failure.
    """
    mtz = Path(mtz_path).resolve()
    out_dir = Path(output_dir).resolve()
    out_jpg = Path(output_jpg).resolve()
    if not mtz.is_file():
        raise AuspexError("MTZ not found: {}".format(mtz))
    out_dir.mkdir(parents=True, exist_ok=True)

    own = service is None
    if own:
        root = os.path.commonpath([str(mtz), str(out_dir), str(out_jpg)])
        service = ContainerService(AUSPEX_IMAGE, AUSPEX_PLATFORM, root)

    try:
        before = _snapshot(out_dir)
        base = [a.format(mtz=str(mtz), out=str(out_dir)) for a in AUSPEX_ARGS]
        # Options must precede the positional HKLIN, which is the last element.
        args = base[:-1] + list(extra_args or []) + base[-1:]
        try:
            proc = service.exec(args, workdir=out_dir, timeout=timeout)
        except DockerServiceError as exc:
            raise AuspexError(str(exc)) from exc
    finally:
        if own:
            service.stop()

    if proc.returncode != 0:
        tail = (proc.stderr or proc.stdout or "").strip()[-1500:]
        raise AuspexError(
            "AUSPEX exited with code {}: {}".format(proc.returncode, tail)
        )

    after = _snapshot(out_dir)
    new_files = [p for p, t in after.items() if before.get(p) != t]
    plots = sorted(
        (p for p in new_files if p.suffix.lower() in IMAGE_EXTS and p != out_jpg),
        key=lambda p: p.name,
    )
    if not plots:
        raise AuspexError(
            "AUSPEX ran but wrote no image files. stdout: {}".format(
                (proc.stdout or "").strip()[-500:]
            )
        )

    amp = [p for p in plots if "amplitude" in p.name.lower()]
    chosen = (amp or plots)[0]
    if not amp:
        logger.warning(
            "AUSPEX: no *amplitude* file; using %s (candidates: %s)",
            chosen.name,
            [p.name for p in plots],
        )

    _to_jpeg(chosen, out_jpg)

    if not keep_extra:
        for p in new_files:
            if p != out_jpg and p.exists():
                p.unlink()
    return out_jpg
