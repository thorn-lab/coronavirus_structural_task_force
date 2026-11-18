"""Shared context and interface for per-entry validation steps."""

from __future__ import annotations

import json
import logging
import shutil
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger("xtal_validation.orchestrator")

SUMMARY_NAME = "validation_summary.json"
EM_METHOD = "ELECTRON MICROSCOPY"
# Status prefixes that mean a step produced no usable results.
UNSUCCESSFUL = ("error", "no_input", "not_applicable")


def succeeded(status: str) -> bool:
    return not str(status).startswith(UNSUCCESSFUL)


@dataclass
class Entry:
    """Resolved paths and shared results for one structure entry."""

    pdb_id: str
    path: Path
    exp_method: str | None = None
    files: dict[str, Path | None] = field(default_factory=dict)
    # In-memory results shared between steps of one run (e.g. molprobity -> charts).
    results: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.path = Path(self.path)
        self.validation_dir = self.path / "validation"
        self.auspex_dir = self.validation_dir / "auspex"
        self.haruspex_dir = self.validation_dir / "haruspex"
        self.em_validation_dir = self.validation_dir / "em_validation"
        self.molprobity_dir = self.validation_dir / "molprobity"
        self.summary_path = self.validation_dir / SUMMARY_NAME
        self.model_path = self.files.get("pdb") or self.files.get("cif")

    @property
    def is_em(self) -> bool:
        return (
            isinstance(self.exp_method, str)
            and self.exp_method.strip().upper() == EM_METHOD
        )

    def rel(self, path) -> str:
        """Path relative to the entry directory, as stored in summaries."""
        path = Path(path)
        try:
            return path.resolve().relative_to(self.path.resolve()).as_posix()
        except ValueError:
            return str(path)

    def load_summary(self) -> dict[str, dict]:
        """Persisted per-step results from this and all earlier runs."""
        try:
            return json.loads(self.summary_path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return {}
        except (OSError, ValueError) as exc:
            logger.warning("Unreadable %s (%s); starting afresh", self.summary_path, exc)
            return {}

    def has_result(self, step_name: str) -> bool:
        record = self.load_summary().get(step_name)
        return bool(record) and succeeded(record.get("status", ""))

    def record(self, step_name: str, status: str, data: dict | None = None) -> None:
        """Store a step's outcome, never replacing an earlier success with a failure."""
        store = self.load_summary()
        previous = store.get(step_name)
        if not succeeded(status) and previous and succeeded(previous.get("status", "")):
            return
        store[step_name] = {
            "status": status,
            "data": data or {},
            "updated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }
        self.validation_dir.mkdir(parents=True, exist_ok=True)
        temporary = self.summary_path.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(store, indent=2, sort_keys=True), encoding="utf-8")
        temporary.replace(self.summary_path)


class ValidationStep:
    """Template interface shared by validators.

    ``run`` owns the common lifecycle; concrete steps implement the hooks
    rather than putting input handling, caching, and execution in one method.

    ``summarize`` turns the value returned by ``execute`` into a small
    JSON-serialisable dict. ``run`` persists it in the entry's
    ``validation_summary.json`` so later steps (and later runs) can read a
    step's findings without re-parsing its output files.
    """

    name = ""
    record_result = True

    def __init__(self, *, skip_existing: bool = True, **options):
        self.skip_existing = skip_existing
        self.options = options

    def run(self, entry: Entry) -> str:
        reason = self.check_input(entry)
        if reason:
            self._record(entry, reason)
            return reason
        if self.skip_existing and self.is_complete(entry):
            if not self.record_result or entry.has_result(self.name):
                return "skipped"
            logger.info(
                "%s output exists for %s but has no stored summary; re-running",
                self.name,
                entry.pdb_id,
            )

        output_dir = self.output_dir(entry)
        existed = output_dir.exists() if output_dir else True
        before = set(output_dir.rglob("*")) if output_dir and existed else set()
        try:
            self.prepare(entry)
            result = self.execute(entry)
            status = self.format_result(result)
            data = self.summarize(entry, result) if succeeded(status) else None
        except Exception as exc:
            logger.exception("%s failed for %s", self.name, entry.pdb_id)
            status, data = "error: {}".format(exc), None
        if status.startswith("error"):
            self.cleanup(entry, output_dir, existed, before)
        self._record(entry, status, data)
        return status

    def _record(self, entry: Entry, status: str, data: dict | None = None) -> None:
        if self.record_result:
            entry.record(self.name, status, data)

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

    def summarize(self, entry: Entry, result) -> dict:
        """Findings worth reporting; values must be JSON-serialisable."""
        return {}

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
