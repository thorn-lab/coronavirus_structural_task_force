#!/usr/bin/env python3

"""
Set up the CCTBX chem_data reference data for a uv-managed project.

The data is kept in the project directory, not inside .venv.

For CCTBX 2025.11 this script downloads the matching chem_data
Conda package, verifies its SHA256 checksum, extracts it, and then
creates:

    .venv/lib/pythonX.Y/site-packages/chem_data
        -> <project>/chem_data

Finally, the CaBLAM .stat files are converted to .pickle files using
the CCTBX CaBLAM cache builder.
"""

from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CCTBX_VERSION = "2025.11"

CHEM_DATA_FILENAME = "chem_data-2025.11-pyhe0d8492_0.conda"

CHEM_DATA_URL = (
    "https://github.com/cctbx/cctbx_project/releases/download/"
    f"v{CCTBX_VERSION}/{CHEM_DATA_FILENAME}"
)

CHEM_DATA_SHA256 = "b157567eeb89a7228c2aa9f9c6a4e6fa4a04250ff063d733950fa6b0d1b5e8f9"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CHEM_DATA = PROJECT_ROOT / "chem_data"

# Keep the downloaded archive outside the repository data directory.
CACHE_DIR = PROJECT_ROOT / ".cache"
ARCHIVE_PATH = CACHE_DIR / CHEM_DATA_FILENAME


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------


def sha256(path: Path) -> str:
    h = hashlib.sha256()

    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)

    return h.hexdigest()


def download(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)

    print(f"Downloading:\n  {url}")
    print(f"To:\n  {destination}")

    urllib.request.urlretrieve(url, destination)


def verify_sha256(path: Path, expected: str) -> None:
    print("Checking SHA256...")

    actual = sha256(path)

    if actual != expected:
        raise RuntimeError(
            "SHA256 mismatch!\n" f"Expected: {expected}\n" f"Actual:   {actual}\n"
        )

    print("SHA256 OK.")


def extract_chem_data_archive(archive: Path, destination: Path) -> None:
    """
    Extract the package payload from a .conda archive.

    A .conda file is a ZIP containing a pkg-*.tar.zst payload.
    We use Python's zstandard package temporarily via uv.
    """

    print(f"Extracting {archive}...")

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)

        with zipfile.ZipFile(archive) as zf:
            pkg_members = [
                name
                for name in zf.namelist()
                if name.startswith("pkg-") and name.endswith(".tar.zst")
            ]

            if len(pkg_members) != 1:
                raise RuntimeError(
                    "Could not identify the package payload in "
                    f"{archive.name}: {pkg_members}"
                )

            pkg_member = pkg_members[0]
            pkg_path = tmp / Path(pkg_member).name

            print(f"Package payload: {pkg_member}")

            with zf.open(pkg_member) as src, pkg_path.open("wb") as dst:
                shutil.copyfileobj(src, dst)

        # Import only here so the script can bootstrap zstandard through uv.
        try:
            import zstandard
        except ImportError:
            raise RuntimeError(
                "The Python package 'zstandard' is required for extraction.\n"
                "Run this script with:\n\n"
                "  uv run --with zstandard python scripts/setup_chem_data.py\n"
            )

        extracted = tmp / "extracted"
        extracted.mkdir()

        dctx = zstandard.ZstdDecompressor()

        tar_path = tmp / "package.tar"

        with pkg_path.open("rb") as src, tar_path.open("wb") as dst:
            dctx.copy_stream(src, dst)

        import tarfile

        with tarfile.open(tar_path, "r") as tar:
            tar.extractall(extracted)

        # The archive contains site-packages/chem_data.
        source = extracted / "site-packages" / "chem_data"

        if not source.is_dir():
            # Be a little defensive in case the package layout changes.
            candidates = list(extracted.rglob("chem_data"))

            candidates = [
                p for p in candidates if p.is_dir() and (p / "cablam_data").is_dir()
            ]

            if len(candidates) != 1:
                raise RuntimeError(
                    "Could not find chem_data/cablam_data in extracted "
                    "package.\nCandidates:\n" + "\n".join(str(p) for p in candidates)
                )

            source = candidates[0]

        print(f"Installing project chem_data from:\n  {source}")

        if destination.exists():
            raise RuntimeError(
                f"Refusing to overwrite existing directory: {destination}"
            )

        shutil.copytree(source, destination)


def ensure_chem_data() -> None:
    """
    Ensure project/chem_data exists and contains CaBLAM source data.
    """

    cablam_data = CHEM_DATA / "cablam_data"

    required = [
        "cablam.8000.expected.general.stat",
        "cablam.8000.expected.gly.stat",
        "cablam.8000.expected.transpro.stat",
        "cablam.8000.expected.cispro.stat",
    ]

    if all((cablam_data / f).is_file() for f in required):
        print("chem_data already contains the required CaBLAM data.")
        return

    if CHEM_DATA.exists():
        raise RuntimeError(
            f"{CHEM_DATA} exists, but the expected CaBLAM data is missing.\n"
            "Refusing to overwrite it."
        )

    if not ARCHIVE_PATH.exists():
        download(CHEM_DATA_URL, ARCHIVE_PATH)
    else:
        print(f"Using cached archive:\n  {ARCHIVE_PATH}")

    verify_sha256(ARCHIVE_PATH, CHEM_DATA_SHA256)

    extract_chem_data_archive(ARCHIVE_PATH, CHEM_DATA)


def create_cctbx_symlink() -> None:
    """
    Make chem_data visible to the installed CCTBX environment.
    """

    # Locate the site-packages directory used by this Python.
    site_packages = None

    for p in sys.path:
        if p.endswith("site-packages") and Path(p).is_dir():
            site_packages = Path(p)
            break

    if site_packages is None:
        raise RuntimeError(
            "Could not determine the active Python site-packages directory."
        )

    target = site_packages / "chem_data"

    print(f"\nCCTBX site-packages:")
    print(f"  {site_packages}")

    print(f"CCTBX chem_data path:")
    print(f"  {target}")

    if target.is_symlink():
        existing = target.resolve()

        if existing == CHEM_DATA.resolve():
            print("Symlink already correct.")
            return

        print(f"Removing incorrect symlink: {target}")
        target.unlink()

    elif target.exists():
        raise RuntimeError(f"Refusing to overwrite existing path:\n  {target}")

    target.symlink_to(CHEM_DATA.resolve(), target_is_directory=True)

    print(f"Created:\n  {target} -> {target.resolve()}")


def rebuild_cablam_cache() -> None:
    """
    Convert the CaBLAM .stat tables into the .pickle files expected by
    mmtbx.validation.cablam.
    """

    print("\nRebuilding CaBLAM cache...")

    command = [
        sys.executable,
        "-m",
        "mmtbx.command_line.rebuild_cablam_cache",
    ]

    subprocess.run(command, cwd=PROJECT_ROOT, check=True)


def verify() -> None:
    """
    Verify that mmtbx.validation.cablam can actually load the tables.
    """

    print("\nVerifying CaBLAM...")

    import libtbx.load_env

    from mmtbx.validation.cablam import fetch_peptide_expectations

    data = fetch_peptide_expectations()

    expected = {"general", "gly", "transpro", "cispro"}

    if set(data) != expected:
        raise RuntimeError(f"Unexpected CaBLAM categories: {sorted(data)}")

    print("CaBLAM data loaded successfully:")

    for key, value in data.items():
        print(f"  {key}: {type(value).__name__}")


def main() -> int:
    print("=" * 70)
    print("CCTBX / CaBLAM chem_data setup")
    print("=" * 70)
    print(f"CCTBX version: {CCTBX_VERSION}")
    print(f"Project:       {PROJECT_ROOT}")

    ensure_chem_data()
    create_cctbx_symlink()
    rebuild_cablam_cache()
    verify()

    print("\n" + "=" * 70)
    print("SUCCESS")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
