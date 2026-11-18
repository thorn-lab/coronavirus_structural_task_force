# /// script
# requires-python = ">=3.10,<3.11"
# dependencies = [
#     "biotempy==2.1.1",
#     "emda==1.1.6.post2",
# ]
#
# # emda pins gemmi==0.5.4 and numpy<=1.19, which conflicts with BioTEMPy's
# # gemmi==0.5.6 and has no Python 3.10 wheels; both pins are over-strict.
# [tool.uv]
# override-dependencies = ["gemmi==0.5.6", "numpy<2"]
#
# # emda ships only an sdist whose setup.py imports numpy.distutils without
# # declaring numpy, and needs the stdlib distutils (msvccompiler) to build.
# [tool.uv.extra-build-dependencies]
# emda = ["numpy<2"]
#
# [tool.uv.extra-build-variables]
# emda = { SETUPTOOLS_USE_DISTUTILS = "stdlib" }
# ///
"""Isolated uv script for EMDA/TEMPy model-map scoring."""

from __future__ import annotations

import argparse
from pathlib import Path


def score(
    model_path,
    map_path,
    report_path,
    pdb_id,
    resolution,
    resolution_source,
    smoc_window,
):
    try:
        import emda_methods
    except ImportError:
        from emda import emda_methods

    from TEMPy.maps.map_parser import MapParser
    from TEMPy.protein.scoring_functions import FastSMOC, ScoringFunctions
    from TEMPy.protein.structure_blurrer import StructureBlurrer
    from TEMPy.protein.structure_parser import PDBParser, mmCIFParser

    model_path = Path(model_path)
    if model_path.suffix.lower() in {".cif", ".mmcif"}:
        model = mmCIFParser.read_mmCIF_file(str(model_path), hetatm=True)
    else:
        model = PDBParser.read_PDB_file(pdb_id, str(model_path), hetatm=True)
    exp_map = MapParser.readMRC(str(map_path))

    # Simulate density on the experimental map's grid for corresponding voxels.
    blurrer = StructureBlurrer(with_vc=True)
    sim_map = blurrer.gaussian_blur_real_space(model, resolution, exp_map)
    unit_cell, experimental_density, _origin = emda_methods.read_map(str(map_path))
    simulated_density = sim_map.fullMap
    if experimental_density.shape != simulated_density.shape:
        raise RuntimeError(
            "TEMPy simulated map shape {} does not match experimental map {}".format(
                simulated_density.shape, experimental_density.shape
            )
        )
    resolutions, fsc_values = emda_methods.get_fsc(
        experimental_density, simulated_density, unit_cell
    )

    scorer = ScoringFunctions()
    ccc = scorer.CCC(exp_map, sim_map)
    mutual_information = scorer.MI(exp_map, sim_map)

    smoc = FastSMOC(model, exp_map, resolution, sim_map=sim_map)
    smoc_by_chain = {
        str(chain): smoc.score_chain_contig(chain, smoc_window)
        for chain in model.get_chain_list()
    }

    report_path = Path(report_path)
    with report_path.open("w", encoding="utf-8") as out:
        out.write("Electron microscopy model-map validation\n")
        out.write("PDB ID: {}\n".format(pdb_id))
        out.write("Model: {}\nMap: {}\n".format(model_path, map_path))
        out.write(
            "Resolution (A): {:.3f} ({})\n\n".format(resolution, resolution_source)
        )
        out.write("Global scores (TEMPy)\n")
        out.write("CCC: {}\n".format(ccc))
        out.write("Mutual information: {}\n\n".format(mutual_information))
        out.write("Fourier shell correlation (EMDA)\n")
        out.write("Resolution_A\tFSC\n")
        for shell_resolution, fsc in zip(resolutions, fsc_values):
            out.write("{:.6g}\t{:.8g}\n".format(float(shell_resolution), float(fsc)))
        out.write("\nSegment Manders overlap coefficient (SMOC; TEMPy)\n")
        out.write("Chain\tResidue\tSMOC\n")
        for chain, scores in smoc_by_chain.items():
            for residue, value in _score_items(scores):
                out.write("{}\t{}\t{:.8g}\n".format(chain, residue, value))


def _score_items(scores):
    """Yield residue and numeric score pairs across TEMPy return types."""
    items = scores.items() if isinstance(scores, dict) else enumerate(scores)
    for residue, value in items:
        if isinstance(value, (tuple, list)) and len(value) >= 2:
            residue, value = value[0], value[-1]
        try:
            yield residue, float(value)
        except (TypeError, ValueError):
            continue


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--map", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--pdb-id", required=True)
    parser.add_argument("--resolution", type=float, required=True)
    parser.add_argument("--resolution-source", required=True)
    parser.add_argument("--smoc-window", type=int, default=11)
    args = parser.parse_args()
    score(
        args.model,
        args.map,
        args.report,
        args.pdb_id,
        args.resolution,
        args.resolution_source,
        args.smoc_window,
    )


if __name__ == "__main__":
    main()
