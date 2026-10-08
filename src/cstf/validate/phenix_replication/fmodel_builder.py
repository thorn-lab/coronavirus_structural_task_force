"""
fmodel_builder.py

Build a scaled mmtbx.f_model.manager ("fmodel") from a model +
reflection-data pair using CCTBX's mmtbx.command_line loader.

The loader handles:
  - model/data input
  - crystal-symmetry reconciliation
  - observed data selection
  - R-free flag interpretation
  - f_model construction

The resulting fmodel is explicitly rescaled with update_all_scales().

Usage as a library:
    from fmodel_builder import build_fmodel
    fmodel = build_fmodel("model.pdb", "data.mtz")
    print(fmodel.r_work(), fmodel.r_free())

Usage as a script:
    python fmodel_builder.py model.pdb data.mtz
    python fmodel_builder.py model.pdb data.mtz --twin-law "-h,-k,l"
"""

import argparse
import sys


def build_fmodel(
    model_path,
    mtz_path,
    twin_law=None,
    prefer_anomalous=False,
):
    from mmtbx.command_line import (
        generate_master_phil_with_inputs,
        load_model_and_data,
    )

    master_phil = generate_master_phil_with_inputs(
        phil_string="",
        enable_twin_law=True,
    )

    args = [
        model_path,
        mtz_path,
    ]

    if twin_law:
        args.append("twin_law={}".format(twin_law))

    try:
        cmdline = load_model_and_data(
            args=args,
            master_phil=master_phil,
            process_pdb_file=False,
            require_data=True,
            create_fmodel=True,
            prefer_anomalous=prefer_anomalous,
            out=sys.stderr,
        )
    except Exception as exc:
        raise RuntimeError(
            "Could not build fmodel from {} + {}: {}".format(
                model_path,
                mtz_path,
                exc,
            )
        ) from exc

    fmodel = cmdline.fmodel

    if fmodel is None:
        raise RuntimeError(
            "load_model_and_data() did not create an fmodel "
            "for {} + {}".format(model_path, mtz_path)
        )

    fmodel.update_all_scales()

    return fmodel


def summarize(fmodel):
    lines = [
        "R-work: {:.4f}".format(fmodel.r_work()),
        "R-free: {:.4f}".format(fmodel.r_free()),
        "Resolution range: {:.2f} - {:.2f} A".format(*fmodel.f_obs().d_max_min()),
    ]

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument(
        "model",
        help="Path to PDB/mmCIF model file",
    )

    parser.add_argument(
        "mtz",
        help="Path to reflection file",
    )

    parser.add_argument(
        "--twin-law",
        help='Twin law, e.g. "-h,-k,l", if Xtriage flagged twinning',
    )

    parser.add_argument(
        "--prefer-anomalous",
        action="store_true",
        help="Prefer anomalous data if multiple suitable arrays exist",
    )

    args = parser.parse_args()

    try:
        fmodel = build_fmodel(
            args.model,
            args.mtz,
            twin_law=args.twin_law,
            prefer_anomalous=args.prefer_anomalous,
        )
    except RuntimeError as exc:
        sys.stderr.write("Error building fmodel: {}\n".format(exc))
        sys.exit(1)

    print(summarize(fmodel))


if __name__ == "__main__":
    main()
