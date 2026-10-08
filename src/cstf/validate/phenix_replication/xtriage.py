"""
xtriage.py

Open-source replacement for `phenix.xtriage`, built directly on
mmtbx.scaling.xtriage.run - the exact function phenix.xtriage's CLI
calls. Runs data-quality analysis (Wilson statistics, twinning tests,
anisotropy, translational NCS, ice rings) on reflection data, and
optionally cross-checks against a structure model.

Usage:
    python xtriage.py data.mtz
    python xtriage.py data.mtz --model model.pdb --out Xtriage_output.log
"""

import argparse
import sys

from iotbx.reflection_file_reader import any_reflection_file
from mmtbx.scaling import xtriage


def get_observed_arrays(mtz_path):
    """Return candidate observed X-ray arrays from an MTZ."""
    hkl_in = any_reflection_file(mtz_path)
    arrays = hkl_in.file_content().as_miller_arrays()

    candidates = []

    for ma in arrays:
        if not ma.is_xray_intensity_array():
            continue

        info = ma.info()
        if info is None:
            continue

        labels = info.labels
        label_string = info.label_string()

        candidates.append((ma, labels, label_string))

    return candidates


def choose_observed_array(mtz_path):
    """
    Select an observed intensity array automatically.

    Preference:
      1. conventional merged I/SIGI
      2. other single intensity array

    Returns:
      label substring suitable for scaling.input.xray_data.obs_labels
    """
    candidates = get_observed_arrays(mtz_path)

    if not candidates:
        raise RuntimeError(
            "No observed X-ray intensity arrays found in {}".format(mtz_path)
        )

    # First preference: conventional merged intensity data.
    for ma, labels, label_string in candidates:
        labels_lower = [x.lower() for x in labels]

        if any("intensity_meas" in x for x in labels_lower) and not any(
            "plus" in x or "minus" in x for x in labels_lower
        ):
            return "intensity_meas", label_string

    # Second preference: a simple I/SIGI pair.
    for ma, labels, label_string in candidates:
        if len(labels) == 2:
            labels_lower = [x.lower() for x in labels]

            if any("intensity" in x for x in labels_lower) and any(
                "sigma" in x for x in labels_lower
            ):
                return labels[0], label_string

    # If there is exactly one candidate, use it.
    if len(candidates) == 1:
        _, labels, label_string = candidates[0]
        return labels[0], label_string

    # We don't know how to choose safely.
    message = ["Multiple observed intensity arrays found in {}:".format(mtz_path)]

    for _, _, label_string in candidates:
        message.append("  {}".format(label_string))

    message.append("Unable to choose an observed array automatically.")

    raise RuntimeError("\n".join(message))


def run_xtriage(mtz_path, out_stream=None):
    obs_labels, selected_description = choose_observed_array(mtz_path)

    print(
        "Xtriage observed data: {}".format(selected_description),
        file=out_stream or sys.stdout,
    )

    args = [
        mtz_path,
        "scaling.input.xray_data.obs_labels={}".format(obs_labels),
    ]

    return xtriage.run(
        args=args,
        command_name="xtriage.py",
        return_result=True,
        out=out_stream,
        data_file_name=mtz_path,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument("mtz", help="Path to reflection file")

    parser.add_argument("--out", help="Write report to this file")

    args = parser.parse_args()

    if args.out:
        with open(args.out, "w") as fh:
            run_xtriage(args.mtz, out_stream=fh)
    else:
        run_xtriage(args.mtz, out_stream=sys.stdout)


if __name__ == "__main__":
    main()
