"""Shared context and interface for per-entry validation steps."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import logging

logger = logging.getLogger("xtal_validation.orchestrator")


@dataclass
class Entry:
    """Resolved paths and shared results for one structure entry."""

    pdb_id: str
    path: Path
    exp_method: str | None = None
    files: dict[str, Path | None] = field(default_factory=dict)
    results: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.path = Path(self.path)
        self.validation_dir = self.path / "validation"
        self.auspex_dir = self.validation_dir / "auspex"
        self.haruspex_dir = self.validation_dir / "haruspex"
        self.em_validation_dir = self.validation_dir / "em_validation"
        self.molprobity_dir = self.validation_dir / "molprobity"
        self.model_path = self.files.get("pdb") or self.files.get("cif")


class ValidationStep:
    """Template interface shared by validators.

    ``run`` owns the common lifecycle; concrete steps implement the hooks
    rather than putting input handling, caching, and execution in one method.
    """

    name = ""

    def __init__(self, *, skip_existing: bool = True, **options):
        self.skip_existing = skip_existing
        self.options = options

    def run(self, entry: Entry) -> str:
        reason = self.check_input(entry)
        if reason:
            return reason
        if self.skip_existing and self.is_complete(entry):
            return "skipped"

        output_dir = self.output_dir(entry)
        existed = output_dir.exists() if output_dir else True
        before = set(output_dir.rglob("*")) if output_dir and existed else set()
        try:
            self.prepare(entry)
            result = self.execute(entry)
            status = self.format_result(result)
            if status.startswith("error"):
                self.cleanup(entry, output_dir, existed, before)
            return status
        except Exception as exc:
            logger.exception("%s failed for %s", self.name, entry.pdb_id)
            self.cleanup(entry, output_dir, existed, before)
            return "error: {}".format(exc)

    def check_input(self, entry: Entry) -> str | None:
        return None

    def is_complete(self, entry: Entry) -> bool:
        return False

    def output_dir(self, entry: Entry) -> Path | None:
        return None

    def prepare(self, entry: Entry) -> None:
        output_dir = self.output_dir(entry)
        if output_dir is not None:
            output_dir.mkdir(parents=True, exist_ok=True)

    def execute(self, entry: Entry):
        raise NotImplementedError

    def format_result(self, result) -> str:
        return "done"

    def cleanup(
        self,
        entry: Entry,
        output_dir: Path | None,
        existed: bool,
        before: set[Path],
    ) -> None:
        # Preserve prior successful output while removing artifacts created
        # by this failed attempt, including partial files in shared folders.
        if output_dir is not None and output_dir.exists():
            import shutil

            for path in sorted(output_dir.rglob("*"), reverse=True):
                if path not in before:
                    if path.is_dir():
                        shutil.rmtree(path, ignore_errors=True)
                    else:
                        path.unlink(missing_ok=True)
            if not existed and output_dir.exists():
                shutil.rmtree(output_dir, ignore_errors=True)
            elif existed and output_dir.exists() and not any(output_dir.iterdir()):
                output_dir.rmdir()
