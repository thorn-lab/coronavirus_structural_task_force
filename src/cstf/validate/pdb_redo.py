"""
pdb_redo.py

Download and prepare PDB-REDO data for PDB entries.

Expected entry layout:

    <repo>/<entry>/
        <original PDB/CIF/MTZ files...>

After preparation:

    <repo>/<entry>/validation/pdb-redo/
        <pdb_id>.zip contents...

The module intentionally keeps the individual operations synchronous.
This makes them easy to call from the current synchronous orchestrator,
while also making them straightforward to wrap in an async orchestrator
later.

Example:

    from pathlib import Path
    from pdb_redo import prepare_entry

    result = prepare_entry(
        pdb_id="1abc",
        entry_path=Path("/data/pdb/ab/cd/1abc"),
    )

"""

from __future__ import annotations

import logging
import shutil
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger("xtal_validation.pdb_redo")


PDB_REDO_URL = "https://pdb-redo.eu/db/{entry}/zipped"


@dataclass(frozen=True)
class PDBRedoResult:
    """Result of preparing PDB-REDO data for one PDB entry."""

    pdb_id: str
    entry_path: Path
    status: str
    archive_path: Path | None = None
    pdb_redo_path: Path | None = None
    error: str | None = None


def pdb_redo_path(entry_path: Path) -> Path:
    """Return the PDB-REDO output directory for an entry."""
    return Path(entry_path) / "validation" / "pdb-redo"


def archive_path(entry_path: Path, pdb_id: str) -> Path:
    """Return the temporary PDB-REDO ZIP path."""
    return pdb_redo_path(entry_path) / f"{pdb_id.lower()}.zip"


def pdb_redo_exists(entry_path: Path) -> bool:
    """
    Return True if PDB-REDO has already been prepared.

    This mirrors the original shell script's condition:

        if [ -d validation/pdb-redo ]

    """
    return pdb_redo_path(entry_path).is_dir()


def download_archive(
    pdb_id: str,
    entry_path: Path,
    *,
    timeout: int = 120,
) -> Path:
    """
    Download the PDB-REDO archive.

    The archive is written directly into validation/pdb-redo.

    Raises:
        urllib.error.URLError / OSError:
            If the download fails.
    """
    entry_path = Path(entry_path)

    redo_dir = pdb_redo_path(entry_path)
    redo_dir.mkdir(parents=True, exist_ok=True)

    archive = archive_path(entry_path, pdb_id)
    url = PDB_REDO_URL.format(entry=pdb_id.lower())

    logger.info("Downloading PDB-REDO for %s from %s", pdb_id, url)

    # Write to a temporary file first so a failed/interrupted download
    # doesn't leave a file that looks like a complete archive.
    tmp_archive = archive.with_suffix(".zip.tmp")

    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            with open(tmp_archive, "wb") as fh:
                shutil.copyfileobj(response, fh)

        tmp_archive.replace(archive)

    except Exception:
        tmp_archive.unlink(missing_ok=True)
        raise

    return archive


def extract_archive(
    pdb_id: str,
    entry_path: Path,
    *,
    remove_archive: bool = True,
) -> Path:
    """
    Extract an already-downloaded PDB-REDO archive.

    Returns:
        Path to validation/pdb-redo.

    Raises:
        FileNotFoundError:
            If the expected archive doesn't exist.
        zipfile.BadZipFile:
            If the archive is invalid.
    """
    entry_path = Path(entry_path)
    redo_dir = pdb_redo_path(entry_path)
    archive = archive_path(entry_path, pdb_id)

    if not archive.is_file():
        raise FileNotFoundError(f"PDB-REDO archive not found: {archive}")

    logger.info("Extracting PDB-REDO archive for %s", pdb_id)

    with zipfile.ZipFile(archive) as zf:
        _safe_extract(zf, redo_dir)

    if remove_archive:
        archive.unlink()

    return redo_dir


def _safe_extract(archive: zipfile.ZipFile, destination: Path) -> None:
    """
    Extract a ZIP while preventing path traversal.

    This is preferable to calling `unzip` through a shell command.
    """
    destination = destination.resolve()

    for member in archive.infolist():
        member_path = (destination / member.filename).resolve()

        try:
            member_path.relative_to(destination)
        except ValueError as exc:
            raise ValueError(
                f"Unsafe path in PDB-REDO archive: {member.filename}"
            ) from exc

    archive.extractall(destination)


def prepare_entry(
    pdb_id: str,
    entry_path: Path,
    *,
    skip_existing: bool = True,
    timeout: int = 120,
) -> PDBRedoResult:
    """
    Download and extract PDB-REDO data for one PDB entry.

    Args:
        pdb_id:
            PDB identifier, e.g. ``1abc`` or ``1ABC``.

        entry_path:
            Directory containing the PDB entry.

        skip_existing:
            If True, do nothing when validation/pdb-redo already exists.
            This matches the original shell script.

        timeout:
            HTTP download timeout in seconds.

    Returns:
        PDBRedoResult.

    This function does not raise for normal per-entry failures. Instead,
    failures are represented in the result, matching the behavior of
    the existing validation orchestrator.
    """
    entry_path = Path(entry_path)
    pdb_id = str(pdb_id)
    redo_dir = pdb_redo_path(entry_path)

    if skip_existing and pdb_redo_exists(entry_path):
        logger.info("PDB-REDO already exists for %s", pdb_id)

        return PDBRedoResult(
            pdb_id=pdb_id,
            entry_path=entry_path,
            status="skipped",
            pdb_redo_path=redo_dir,
        )

    try:
        archive = archive_path(entry_path, pdb_id)

        # Support a partially completed previous run. If the archive
        # already exists, don't download it again.
        if not archive.is_file():
            archive = download_archive(
                pdb_id,
                entry_path,
                timeout=timeout,
            )
        else:
            logger.info(
                "Using existing PDB-REDO archive for %s",
                pdb_id,
            )

        extract_archive(
            pdb_id,
            entry_path,
            remove_archive=True,
        )

        return PDBRedoResult(
            pdb_id=pdb_id,
            entry_path=entry_path,
            status="done",
            pdb_redo_path=redo_dir,
        )

    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "PDB-REDO failed for %s: %s",
            pdb_id,
            exc,
        )

        return PDBRedoResult(
            pdb_id=pdb_id,
            entry_path=entry_path,
            status=f"error: {exc}",
            error=str(exc),
        )
