"""PDB-REDO preparation as a standalone validation step."""

from __future__ import annotations

import logging
import shutil
import urllib.request
import zipfile
from pathlib import Path

from cstf.validate.base import Entry, ValidationStep

logger = logging.getLogger("xtal_validation.pdb_redo")
PDB_REDO_URL = "https://pdb-redo.eu/db/{entry}/zipped"


class PDBRedoStep(ValidationStep):
    """Download and safely extract PDB-REDO data for one entry."""

    name = "pdb_redo"

    def check_input(self, entry: Entry):
        if entry.is_em:
            return "not_applicable: PDB-REDO covers X-ray structures only"
        return None

    def output_dir(self, entry: Entry) -> Path:
        return self._redo_path(entry.path)

    def is_complete(self, entry: Entry) -> bool:
        output_dir = self.output_dir(entry)
        return output_dir.is_dir() and any(
            path.is_file() and path.suffix.lower() not in {".zip", ".tmp"}
            for path in output_dir.rglob("*")
        )

    def execute(self, entry: Entry) -> Path:
        archive = self._archive_path(entry.pdb_id, entry.path)
        if not archive.is_file():
            self._download_archive(entry.pdb_id, entry.path, self.options.get("timeout", 120))
        return self._extract_archive(entry.pdb_id, entry.path)

    def summarize(self, entry: Entry, result: Path) -> dict:
        return {"directory": entry.rel(result)}

    @classmethod
    def _archive_path(cls, pdb_id: str, entry_path: Path) -> Path:
        return cls._redo_path(entry_path) / "{}.zip".format(pdb_id.lower())

    @staticmethod
    def _redo_path(entry_path: Path) -> Path:
        return Path(entry_path) / "validation" / "pdb-redo"

    def _download_archive(self, pdb_id: str, entry_path: Path, timeout=120) -> Path:
        redo_dir = self._redo_path(entry_path)
        redo_dir.mkdir(parents=True, exist_ok=True)
        archive = self._archive_path(pdb_id, entry_path)
        url = PDB_REDO_URL.format(entry=pdb_id.lower())
        logger.info("Downloading PDB-REDO for %s from %s", pdb_id, url)
        temporary = archive.with_suffix(".zip.tmp")
        try:
            with urllib.request.urlopen(url, timeout=timeout) as response:
                with temporary.open("wb") as output:
                    shutil.copyfileobj(response, output)
            temporary.replace(archive)
        except Exception:
            temporary.unlink(missing_ok=True)
            raise
        return archive

    def _extract_archive(self, pdb_id: str, entry_path: Path) -> Path:
        redo_dir = self._redo_path(entry_path)
        archive = self._archive_path(pdb_id, entry_path)
        if not archive.is_file():
            raise FileNotFoundError("PDB-REDO archive not found: {}".format(archive))
        with zipfile.ZipFile(archive) as zipped:
            self._safe_extract(zipped, redo_dir)
        archive.unlink()
        return redo_dir

    @staticmethod
    def _safe_extract(archive: zipfile.ZipFile, destination: Path) -> None:
        destination = destination.resolve()
        for member in archive.infolist():
            member_path = (destination / member.filename).resolve()
            try:
                member_path.relative_to(destination)
            except ValueError as exc:
                raise ValueError(
                    "Unsafe path in PDB-REDO archive: {}".format(member.filename)
                ) from exc
        archive.extractall(destination)
