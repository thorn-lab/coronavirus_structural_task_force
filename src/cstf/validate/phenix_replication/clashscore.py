"""MolProbity all-atom clashscore validation for one model."""

from pathlib import Path

from cstf.validate.base import Entry, ValidationStep
from iotbx.data_manager import DataManager
from mmtbx.reduce.Optimizers import _philLike
from mmtbx.validation.clashscore2 import clashscore2


class ClashscoreStep(ValidationStep):
    """Calculate the all-atom clashscore and save its text report."""

    name = "clashscore"

    def check_input(self, entry: Entry):
        return None if entry.model_path else "no_input: no model file found"

    def output_dir(self, entry: Entry) -> Path:
        return entry.molprobity_dir

    def target(self, entry: Entry) -> Path:
        return entry.molprobity_dir / "clashscore.txt"

    def is_complete(self, entry: Entry) -> bool:
        return self.target(entry).is_file()

    def execute(self, entry: Entry):
        data_manager = DataManager()
        data_manager.process_model_file(str(entry.model_path))
        result = clashscore2(
            probe_parameters=_philLike(),
            data_manager=data_manager,
            keep_hydrogens=self.options.get("keep_hydrogens", False),
            nuclear=self.options.get("nuclear", False),
            fast=self.options.get("fast", False),
            condensed_probe=True,
        )
        self.target(entry).write_text(self._format_report(result, entry.model_path) + "\n")
        entry.results[self.name] = result
        return result

    @staticmethod
    def _format_report(result, model_path):
        lines = [
            "clashscore analysis for {}".format(model_path),
            "-" * 60,
            "",
            "Bad Clashes >= 0.4 Angstrom:",
        ]
        lines.extend(clash.format_old() for clash in result.results)
        lines.append("clashscore = {:.2f}".format(result.get_clashscore()))
        return "\n".join(lines)
