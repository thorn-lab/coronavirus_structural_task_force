"""X-ray reflection diagnostics for one PDB entry."""

from pathlib import Path

from cstf.validate.base import Entry, ValidationStep
from iotbx.reflection_file_reader import any_reflection_file
from mmtbx.scaling import xtriage


class XtriageStep(ValidationStep):
    """Select observed intensities and run the xtriage analysis."""

    name = "xtriage"

    def check_input(self, entry: Entry):
        if entry.is_em:
            return "not_applicable: xtriage needs X-ray reflection data"
        return None if entry.files.get("mtz") else "no_input: no .mtz file found"

    def output_dir(self, entry: Entry) -> Path:
        return entry.validation_dir

    def target(self, entry: Entry) -> Path:
        return entry.validation_dir / "Xtriage_output.log"

    def is_complete(self, entry: Entry) -> bool:
        target = self.target(entry)
        return target.is_file() and target.stat().st_size > 0

    @staticmethod
    def _choose_observed_array(mtz_path):
        """Return (obs_labels, description) of the observed data to analyse.

        Intensities are preferred; files that only carry amplitudes (e.g.
        PanDDA group depositions with just FP,SIGFP) fall back to those, as
        xtriage itself does. A single candidate is used as is; otherwise the
        merged, non-anomalous array (e.g. IMEAN,SIGIMEAN rather than
        I(+),SIGI(+),I(-),SIGI(-)) wins.
        """
        arrays = [
            array
            for array in any_reflection_file(mtz_path).file_content().as_miller_arrays()
            if array.info() is not None and array.sigmas() is not None
        ]
        candidates = [a for a in arrays if a.is_xray_intensity_array()] or [
            a for a in arrays if a.is_xray_amplitude_array()
        ]
        if not candidates:
            raise RuntimeError(
                "No observed X-ray intensity or amplitude arrays found in {}".format(
                    mtz_path
                )
            )
        if len(candidates) > 1:
            merged = [array for array in candidates if not array.anomalous_flag()]
            if len(merged) != 1:
                raise RuntimeError(
                    "Multiple observed data arrays found in {}:\n  {}\n"
                    "Unable to choose an observed array automatically.".format(
                        mtz_path,
                        "\n  ".join(a.info().label_string() for a in candidates),
                    )
                )
            candidates = merged
        info = candidates[0].info()
        return info.labels[0], info.label_string()

    def execute(self, entry: Entry):
        mtz_path = str(entry.files["mtz"])
        labels, description = self._choose_observed_array(mtz_path)
        with self.target(entry).open("w") as stream:
            print("Xtriage observed data: {}".format(description), file=stream)
            # Do not pass data_file_name: xtriage pickles its raw data to that
            # path, which previously overwrote the input MTZ.
            result = xtriage.run(
                args=[
                    mtz_path,
                    "scaling.input.xray_data.obs_labels={}".format(labels),
                ],
                command_name="xtriage.py",
                return_result=True,
                out=stream,
            )
        return result, description

    def summarize(self, entry: Entry, result) -> dict:
        analyses, description = result
        summary = analyses.data_summary
        d_max, d_min = summary.d_max_min
        return {
            "log": entry.rel(self.target(entry)),
            "observed_array": description,
            "d_min": float(d_min),
            "d_max": float(d_max),
            "completeness": _percent(summary.completeness),
            "i_over_sigma": float(analyses.data_strength_and_completeness.overall_i_sig_i),
            "space_group": str(summary.space_group),
        }


def _percent(fraction):
    return None if fraction is None else 100.0 * float(fraction)
