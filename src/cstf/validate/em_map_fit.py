"""Score an electron-microscopy model against its experimental map."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path

from cstf.validate.base import Entry, ValidationStep
from cstf.validate.haruspex import HaruspexStep

REPORT_NAME = "model_map_validation.txt"
DEFAULT_RESOLUTION = 3.0
SMOC_WINDOW = 11


class EMMapFitStep(ValidationStep):
    """Calculate FSC, CCC, MI, and per-residue SMOC for an EM entry."""

    name = "em_map_fit"

    def __init__(self, *, skip_existing=True, **options):
        super().__init__(skip_existing=skip_existing, **options)
        self.map_path = None

    def check_input(self, entry: Entry):
        if not (
            isinstance(entry.exp_method, str)
            and entry.exp_method.strip().upper() == "ELECTRON MICROSCOPY"
        ):
            return "not_applicable: exp_method is {!r}".format(entry.exp_method)
        if entry.model_path is None:
            return "no_input: no .pdb or .cif model found"
        self.map_path = HaruspexStep.find_map(entry.path)
        return None if self.map_path else "no_input: no .mrc/.map/.ccp4 file found"

    def output_dir(self, entry: Entry) -> Path:
        return entry.em_validation_dir

    def report_path(self, entry: Entry) -> Path:
        return self.output_dir(entry) / REPORT_NAME

    def is_complete(self, entry: Entry) -> bool:
        return self.report_path(entry).is_file()

    def execute(self, entry: Entry) -> Path:
        uv = shutil.which(self.options.get("uv_executable", "uv"))
        if uv is None:
            raise RuntimeError("uv is required to run isolated EM scoring dependencies")

        model_path = Path(entry.model_path).resolve()
        resolution = self._resolution(model_path)
        resolution_source = "model metadata"
        if resolution is None:
            resolution = float(self.options.get("resolution", DEFAULT_RESOLUTION))
            resolution_source = "configured fallback"
        report = self.report_path(entry)
        worker = Path(__file__).with_name("em_map_fit_worker.py").resolve()
        command = [
            uv,
            "run",
            "--no-project",
            "--script",
            str(worker),
            "--model",
            str(model_path),
            "--map",
            str(Path(self.map_path).resolve()),
            "--report",
            str(report.resolve()),
            "--pdb-id",
            entry.pdb_id,
            "--resolution",
            str(resolution),
            "--resolution-source",
            resolution_source,
            "--smoc-window",
            str(int(self.options.get("smoc_window", SMOC_WINDOW))),
        ]
        # The worker's isolated env lacks the caller's matplotlib backends
        # (e.g. Jupyter's matplotlib_inline), so force a headless one.
        env = {**os.environ, "MPLBACKEND": "Agg"}
        try:
            process = subprocess.run(
                command,
                cwd=str(entry.path.resolve()),
                env=env,
                capture_output=True,
                text=True,
                timeout=self.options.get("timeout", 3600),
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError("EM map scoring exceeded its configured timeout") from exc
        if process.returncode != 0:
            detail = (process.stderr or process.stdout or "").strip()[-3000:]
            raise RuntimeError("Isolated EM map scoring failed: {}".format(detail))
        if not report.is_file():
            raise RuntimeError("EM map scoring finished without producing its report")
        return report

    def format_result(self, result: Path) -> str:
        return "done ({})".format(result.name)

    @staticmethod
    def _resolution(model_path: Path):
        """Read a nominal resolution from common PDB/mmCIF metadata fields."""
        try:
            text = Path(model_path).read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return None
        patterns = (
            r"(?im)^REMARK\s+2\s+RESOLUTION\.\s*([0-9.]+)\s+ANGSTROMS",
            r"(?im)^\s*_em_3d_reconstruction\.resolution\s+['\"]?([0-9.]+)",
            r"(?im)^\s*_refine\.ls_d_res_high\s+['\"]?([0-9.]+)",
        )
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                value = float(match.group(1))
                if value > 0:
                    return value
        return None
