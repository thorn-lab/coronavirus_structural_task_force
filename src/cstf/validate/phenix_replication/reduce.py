"""Add hydrogens to a model using the available Reduce2 backend."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

from cstf.validate.base import Entry, ValidationStep


class ReduceStep(ValidationStep):
    """Add and optimize hydrogen atoms for one model."""

    name = "reduce"

    def check_input(self, entry: Entry):
        return None if entry.model_path else "no_input: no model file found"

    def output_dir(self, entry: Entry) -> Path:
        return entry.molprobity_dir

    def target(self, entry: Entry) -> Path:
        return entry.molprobity_dir / "{}.H.pdb".format(entry.pdb_id)

    def is_complete(self, entry: Entry) -> bool:
        return self.target(entry).is_file()

    def execute(self, entry: Entry) -> str:
        mode = self.options.get("mode", "nuclear")
        if self._try_api_backend(str(entry.model_path), str(self.target(entry)), mode):
            return "api"
        self._try_subprocess_backend(str(entry.model_path), str(self.target(entry)), mode)
        return "subprocess"

    def format_result(self, result: str) -> str:
        return "done ({})".format(result)

    @staticmethod
    def _try_api_backend(model_path, out_path, mode="nuclear"):
        """Try the Reduce2 Python API; return false when fallback is needed."""
        try:
            from mmtbx.command_line import reduce2
        except ImportError:
            return False

        try:
            import iotbx.pdb
            import mmtbx.model

            pdb_input = iotbx.pdb.input(file_name=model_path)
            model = mmtbx.model.manager(model_input=pdb_input)
            model = model.remove_hydrogens()
            model_with_h = reduce2(model=model, mode=mode)
            with open(out_path, "w") as output:
                output.write(model_with_h.model_as_pdb())
            return True
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(
                "Reduce2 API failed ({}); falling back to subprocess.\n".format(exc)
            )
            return False

    @staticmethod
    def _try_subprocess_backend(model_path, out_path, mode="nuclear"):
        """Invoke an installed Reduce2 or legacy Phenix executable."""
        candidates = ["mmtbx.reduce2", "phenix.reduce"]
        executable = next((name for name in candidates if shutil.which(name)), None)
        if executable is None:
            raise RuntimeError(
                "No reduce-family executable found on PATH (tried: {})".format(
                    ", ".join(candidates)
                )
            )
        if executable == "mmtbx.reduce2":
            subprocess.run(
                [
                    executable,
                    model_path,
                    "approach=add",
                    "output.filename={}".format(out_path),
                ],
                check=True,
            )
        else:
            with open(out_path, "w") as output:
                subprocess.run([executable, model_path], stdout=output, check=True)

    @staticmethod
    def check_backends():
        report = []
        try:
            from mmtbx.command_line import reduce2  # noqa: F401
            report.append("mmtbx.command_line.reduce2 Python API: available")
        except ImportError as exc:
            report.append(
                "mmtbx.command_line.reduce2 Python API: NOT available ({})".format(exc)
            )
        for executable in ("mmtbx.reduce2", "phenix.reduce"):
            report.append(
                "{} executable: {}".format(
                    executable, shutil.which(executable) or "NOT found"
                )
            )
        return "\n".join(report)
