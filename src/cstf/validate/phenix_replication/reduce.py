"""
reduce.py

Open-source replacement for `phenix.reduce`, which adds hydrogen atoms
to a model (needed before clashscore/probe analysis can see H-related
clashes) and optimizes Asn/Gln/His flips.

The correct API lives at `mmtbx.command_line.reduce2` (NOT
`mmtbx.reduce2`, a mistake in an earlier draft of this module) and is
used as a plain callable that takes an `mmtbx.model.manager` object
and returns a new manager with hydrogens added -- it is not a class
you instantiate. This module tries that API first and falls back to
invoking a `reduce2`/`phenix.reduce` executable via subprocess if the
API import fails, so it degrades gracefully across CCTBX versions.

Runtime dependency note: reduce2 calls probe2 internally, which needs
monomer-library restraint data (the `geostd` repo). If you get a
runtime error about missing restraint/mod definitions rather than an
ImportError, set the MMTBX_CCP4_MONOMER_LIB environment variable to
point at a local geostd checkout -- that's a data-path issue, not a
code issue.

Usage:
    python reduce.py model.pdb -o model.H.pdb
    python reduce.py model.pdb -o model.H.pdb --mode electron_cloud
    python reduce.py --check   # report which backend is available
"""

import argparse
import shutil
import subprocess
import sys


def _try_api_backend(model_path, out_path, mode="nuclear"):
    """
    Attempt to add hydrogens using the mmtbx.command_line.reduce2 API.
    Returns True on success, False if the API isn't available/usable
    so the caller can fall back to a subprocess call.
    """
    try:
        from mmtbx.command_line import reduce2
    except ImportError:
        return False

    try:
        import iotbx.pdb
        import mmtbx.model

        pdb_input = iotbx.pdb.input(file_name=model_path)
        model = mmtbx.model.manager(model_input=pdb_input)

        # Strip any existing H before re-adding, matching phenix.reduce's
        # default behavior of a clean re-placement.
        model = model.remove_hydrogens()

        model_with_h = reduce2(model=model, mode=mode)

        with open(out_path, "w") as fh:
            fh.write(model_with_h.model_as_pdb())
        return True
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(
            "mmtbx.command_line.reduce2 API call failed ({}); "
            "falling back to subprocess backend.\n".format(exc)
        )
        return False


def _try_subprocess_backend(model_path, out_path, mode="nuclear"):
    """
    Fall back to whatever reduce-family executable is on PATH:
    tries `mmtbx.reduce2`, then the legacy `phenix.reduce`.
    (mmtbx.reduce2 is a CLI entry point installed alongside the
    Python package; it's distinct from the nonexistent
    `mmtbx.reduce2` *import* path this module used to (wrongly) try.)
    """
    candidates = ["mmtbx.reduce2", "phenix.reduce"]
    exe = next((c for c in candidates if shutil.which(c)), None)
    if exe is None:
        raise RuntimeError(
            "No reduce-family executable found on PATH "
            "(tried: {})".format(", ".join(candidates))
        )

    if exe == "mmtbx.reduce2":
        cmd = [exe, model_path, "approach=add",
               "output.filename={}".format(out_path)]
        subprocess.run(cmd, check=True)
    else:
        cmd = [exe, model_path]
        with open(out_path, "w") as out_fh:
            subprocess.run(cmd, stdout=out_fh, check=True)


def add_hydrogens(model_path, out_path, mode="nuclear"):
    """
    Add hydrogens to model_path, writing the result to out_path.
    Tries the CCTBX Python API first, then falls back to subprocess.

    Args:
        mode: 'nuclear' (X-H distances for neutron-style geometry,
            the modern reduce2 default) or 'electron_cloud' (shorter
            X-H distances matching X-ray scattering, closer to legacy
            phenix.reduce's default).
    """
    if _try_api_backend(model_path, out_path, mode=mode):
        return "api"
    _try_subprocess_backend(model_path, out_path, mode=mode)
    return "subprocess"


def check_backends():
    report = []
    try:
        from mmtbx.command_line import reduce2  # noqa: F401
        report.append("mmtbx.command_line.reduce2 Python API: available")
    except ImportError as exc:
        report.append(
            "mmtbx.command_line.reduce2 Python API: NOT available "
            "({})".format(exc))

    for exe in ("mmtbx.reduce2", "phenix.reduce"):
        report.append(
            "{} executable: {}".format(
                exe, shutil.which(exe) or "NOT found"
            )
        )
    return "\n".join(report)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("model", nargs="?", help="Path to input PDB file")
    parser.add_argument("-o", "--out", help="Path to output PDB with H")
    parser.add_argument("--mode", default="nuclear",
                         choices=["nuclear", "electron_cloud"],
                         help="X-H distance convention (default: nuclear)")
    parser.add_argument("--check", action="store_true",
                         help="Report which reduce backend is available "
                              "and exit")
    args = parser.parse_args()

    if args.check:
        print(check_backends())
        return

    if not args.model or not args.out:
        parser.error("model and --out are required unless using --check")

    backend = add_hydrogens(args.model, args.out, mode=args.mode)
    sys.stderr.write("Hydrogens added using '{}' backend -> {}\n".format(
        backend, args.out))


if __name__ == "__main__":
    main()
