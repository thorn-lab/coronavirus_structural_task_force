"""X-ray reflection diagnostics for one PDB entry."""

from pathlib import Path

from cstf.validate.base import Entry, ValidationStep
from iotbx.reflection_file_reader import any_reflection_file
from mmtbx.scaling import xtriage


class XtriageStep(ValidationStep):
    """Select observed intensities and run the xtriage analysis."""

    name = "xtriage"

    def check_input(self, entry: Entry):
        return None if entry.files.get("mtz") else "no_input: no .mtz file found"

    def output_dir(self, entry: Entry) -> Path:
        return entry.validation_dir

    def target(self, entry: Entry) -> Path:
        return entry.validation_dir / "Xtriage_output.log"

    def is_complete(self, entry: Entry) -> bool:
        return self.target(entry).is_file()

    @staticmethod
    def _get_observed_arrays(mtz_path):
        """Return candidate observed X-ray arrays from an MTZ."""
        hkl_in = any_reflection_file(mtz_path)
        arrays = hkl_in.file_content().as_miller_arrays()
        candidates = []
        for miller_array in arrays:
            if not miller_array.is_xray_intensity_array():
                continue
            info = miller_array.info()
            if info is not None:
                candidates.append(
                    (miller_array, info.labels, info.label_string())
                )
        return candidates

    @classmethod
    def _choose_observed_array(cls, mtz_path):
        """Choose a conventional merged I/SIGI array when possible."""
        candidates = cls._get_observed_arrays(mtz_path)
        if not candidates:
            raise RuntimeError(
                "No observed X-ray intensity arrays found in {}".format(mtz_path)
            )

        for _, labels, label_string in candidates:
            labels_lower = [label.lower() for label in labels]
            if any("intensity_meas" in label for label in labels_lower) and not any(
                "plus" in label or "minus" in label for label in labels_lower
            ):
                return "intensity_meas", label_string

        for _, labels, label_string in candidates:
            if len(labels) == 2:
                labels_lower = [label.lower() for label in labels]
                if any("intensity" in label for label in labels_lower) and any(
                    "sigma" in label for label in labels_lower
                ):
                    return labels[0], label_string

        if len(candidates) == 1:
            _, labels, label_string = candidates[0]
            return labels[0], label_string

        descriptions = [candidate[2] for candidate in candidates]
        raise RuntimeError(
            "Multiple observed intensity arrays found in {}:\n  {}\n"
            "Unable to choose an observed array automatically.".format(
                mtz_path, "\n  ".join(descriptions)
            )
        )

    def execute(self, entry: Entry):
        mtz_path = str(entry.files["mtz"])
        labels, description = self._choose_observed_array(mtz_path)
        target = self.target(entry)
        with target.open("w") as stream:
            print("Xtriage observed data: {}".format(description), file=stream)
            return xtriage.run(
                args=[
                    mtz_path,
                    "scaling.input.xray_data.obs_labels={}".format(labels),
                ],
                command_name="xtriage.py",
                return_result=True,
                out=stream,
                data_file_name=mtz_path,
            )
