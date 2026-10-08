"""
clashscore.py

Open-source replacement for `phenix.clashscore`, built directly on the
mmtbx.validation.clashscore API (the same code phenix.clashscore calls).

Computes the MolProbity all-atom clashscore for a PDB/mmCIF model:
the number of serious steric clashes (>0.4 Angstrom overlap between
non-bonded atoms) per 1000 atoms.

Uses the integrated CCTBX Probe2 implementation; no external `probe`
executable is required.

Usage:
    python clashscore2.py model.pdb
    python clashscore2.py model.pdb --out clashscore.txt

As a library:
    from clashscore2 import run_clashscore
    result = run_clashscore("model.pdb")s
    print(result.get_clashscore())
"""

import argparse

from iotbx.data_manager import DataManager

from mmtbx.reduce.Optimizers import _philLike
from mmtbx.validation.clashscore2 import clashscore2


def run_clashscore(model_path, nuclear=False, keep_hydrogens=False, fast=False):

    data_manager = DataManager()
    data_manager.process_model_file(model_path)

    # clashscore2 passes this object to mmtbx.reduce.Optimizers.Optimizer
    # when hydrogens need to be placed and optimized.
    probe_parameters = _philLike()

    result = clashscore2(
        probe_parameters=probe_parameters,
        data_manager=data_manager,
        keep_hydrogens=keep_hydrogens,
        nuclear=nuclear,
        fast=fast,
        condensed_probe=True,
    )
    return result


def format_report(result, model_path):

    lines = []

    lines.append("clashscore analysis for {}".format(model_path))
    lines.append("-" * 60)
    lines.append("")

    lines.append("Bad Clashes >= 0.4 Angstrom:")

    for clash in result.results:
        lines.append(clash.format_old())

    lines.append("clashscore = {:.2f}".format(result.get_clashscore()))

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Calculate clashscore using CCTBX/mmtbx Probe2"
    )
    parser.add_argument("model", help="Input PDB file")
    parser.add_argument("--nuclear", action="store_true")
    parser.add_argument("--keep-hydrogens", action="store_true")
    parser.add_argument("--fast", action="store_true")

    args = parser.parse_args()

    result = run_clashscore(
        model_path=args.model,
        nuclear=args.nuclear,
        keep_hydrogens=args.keep_hydrogens,
        fast=args.fast,
    )

    print(f"Clashscore: {result.clashscore}")


if __name__ == "__main__":
    main()
