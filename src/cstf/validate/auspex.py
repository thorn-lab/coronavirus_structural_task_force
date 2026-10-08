"""AUSPEX integration for the validation pipeline.

Runs the AUSPEX command-line tool on an existing MTZ file and retains only
its amplitudes plot as validation/auspex/amplitudes.jpg.

The input MTZ is never copied into the AUSPEX output directory.
"""

from __future__ import annotations

import logging
import shutil
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


def _find_amplitudes_png(output_dir: Path) -> Path:
    """Locate AUSPEX's amplitudes PNG output."""
    candidates = [
        output_dir / "amplitudes.png",
        output_dir / "AUSPEX" / "amplitudes.png",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate

    matches = sorted(output_dir.rglob("*amplitudes*.png"))
    if matches:
        return matches[0]

    raise FileNotFoundError(
        "AUSPEX completed but no amplitudes PNG was found in {}".format(output_dir)
    )


def run_auspex(
    mtz_path: str,
    output_dir: str,
    output_jpg: str | None = None,
) -> Path:
    """Run AUSPEX and convert its amplitudes plot to JPEG.

    Args:
        mtz_path: Existing MTZ file used as AUSPEX input.
        output_dir: Directory in which AUSPEX writes its temporary outputs.
        output_jpg: Final JPEG path. Defaults to ``output_dir/amplitudes.jpg``.

    Returns:
        Path to the generated amplitudes JPEG.

    Raises:
        FileNotFoundError: if the MTZ or AUSPEX executable is missing, or
            if AUSPEX does not produce an amplitudes plot.
        RuntimeError: if AUSPEX exits unsuccessfully.
        ImportError: if Pillow is unavailable.
    """
    mtz = Path(mtz_path)
    out_dir = Path(output_dir)
    jpg = Path(output_jpg) if output_jpg else out_dir / "amplitudes.jpg"

    if not mtz.is_file():
        raise FileNotFoundError("MTZ input does not exist: {}".format(mtz))

    out_dir.mkdir(parents=True, exist_ok=True)

    executable = shutil.which("auspex")
    if executable is None:
        raise FileNotFoundError(
            "Could not find the 'auspex' executable. Install AUSPEX from "
            "https://github.com/YunyunGao/AUSPEX/tree/main."
        )

    # AUSPEX is invoked with the existing MTZ as input and writes its normal
    # diagnostic files into a temporary subdirectory. The MTZ itself remains
    # outside validation/auspex.
    work_dir = out_dir / "_auspex_tmp"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    work_dir.mkdir(parents=True)

    try:
        command = [executable, str(mtz), "-o", str(work_dir)]
        result = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(
                "AUSPEX failed with exit code {}:\n{}".format(
                    result.returncode,
                    result.stderr.strip() or result.stdout.strip(),
                )
            )

        amplitudes_png = _find_amplitudes_png(work_dir)

        try:
            from PIL import Image
        except ImportError as exc:
            raise ImportError(
                "Pillow is required to convert AUSPEX's amplitudes.png to JPEG."
            ) from exc

        jpg.parent.mkdir(parents=True, exist_ok=True)
        with Image.open(amplitudes_png) as image:
            # JPEG does not support RGBA/P/LA images reliably, so normalize
            # to RGB before saving.
            image.convert("RGB").save(jpg, "JPEG", quality=95)

        return jpg
    finally:
        # Keep validation/auspex clean: only amplitudes.jpg is retained.
        shutil.rmtree(work_dir, ignore_errors=True)
