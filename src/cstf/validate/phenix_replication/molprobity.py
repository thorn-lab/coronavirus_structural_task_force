from __future__ import annotations

from pathlib import Path
from typing import Optional
from io import StringIO

from libtbx import phil
from iotbx import pdb
from iotbx.data_manager import DataManager

from mmtbx import model
from mmtbx.model import statistics as model_statistics
from mmtbx.reduce.Optimizers import _philLike
from mmtbx.programs import reduce2

# from mmtbx.reduce import reduce_hydrogen
from mmtbx.programs.reduce2 import reduce_hydrogen
from mmtbx.validation.clashscore2 import clashscore2
from mmtbx.validation import molprobity as molprobity_module
from mmtbx.validation import clashscore


def _probe2_geometry_clash(self):
    """
    Replacement for mmtbx.model.statistics.geometry.clash().

    CCTBX 2025.11's MolProbity geometry code still expects the older
    clashscore interface, while the installed clash machinery is Probe2
    (clashscore2).  Serialize the current hierarchy into a DataManager and
    run clashscore2 through that interface.
    """
    if self.cached_clash is None:
        pdb_string = self.pdb_hierarchy.as_pdb_string(
            crystal_symmetry=self.model.crystal_symmetry()
        )

        data_manager = DataManager()
        data_manager.process_model_str(
            "molprobity_internal_model.pdb",
            pdb_string,
        )

        self.cached_clash = clashscore2(
            probe_parameters=_philLike(),
            data_manager=data_manager,
            fast=self.fast_clash,
            condensed_probe=self.condensed_probe,
            keep_hydrogens=self.use_hydrogens,
            nuclear=self.model.is_neutron(),
        )

    return model_statistics.group_args(
        score=self.cached_clash.get_clashscore(),
        clashes=self.cached_clash,
    )


def _find_flips_in_output_string(output_string, mover_type):
    """
    Extract FlipMoverState objects from Optimizers.getInfo() output.

    This mirrors mmtbx.programs.reduce2._FindFlipsInOutputString().
    """
    ret = []
    model_id = None
    alt_id = None
    in_block = False

    for line in output_string.splitlines():
        words = line.split()

        if not words:
            continue

        if in_block:
            if words[0:2] == ["END", "REPORT"]:
                in_block = False

            elif words[0] == mover_type:
                ret.append(
                    reduce2.Optimizers.FlipMoverState(
                        mover_type,
                        model_id,
                        alt_id,
                        words[3],
                        words[4],
                        words[5],
                        words[14] == "Flipped",
                        words[15] == "AnglesAdjusted",
                    )
                )

        else:
            if words[0:2] == ["BEGIN", "REPORT:"]:
                model_id = int(words[3])

                # Remove the single-quote and colon characters from AltId.
                trim = words[5].replace("'", "")
                trim = trim.replace(":", "")
                alt_id = trim

                in_block = True

    return ret


def _run_reduce2_nqh_flips(pdb_hierarchy):
    """
    Run the installed Reduce2 Python implementation and return
    N/Q/H flip information in the form expected by MolProbity.

    The old MolProbity implementation invokes:

        molprobity.reduce -BUILD -

    That executable is not installed in this CCTBX environment.
    Reduce2 provides the equivalent functionality through its Python API.
    """
    # Program.master_phil_str is a class-level PHIL definition in the
    # installed reduce2 implementation.
    master_phil = phil.parse(reduce2.Program.master_phil_str)
    params = master_phil.extract()

    params.approach = "add"
    params.add_flip_movers = True
    params.output.write_files = False

    # Construct a DataManager from the hierarchy.
    pdb_string = pdb_hierarchy.as_pdb_string()

    data_manager = DataManager()
    data_manager.process_model_str(
        "molprobity_reduce2_input.pdb",
        pdb_string,
    )

    reduce_model = data_manager.get_model()

    # Match reduce2.Program.run(): remove unknown element X atoms.
    reduce_model.get_hierarchy().atoms().extract_element() != "X"

    atoms = reduce_model.get_hierarchy().atoms()
    keep = atoms.extract_element() != "X"
    reduce_model.get_hierarchy().atoms().select(keep)

    # Match Program.run()'s crystal symmetry setup.
    reduce_model.add_crystal_symmetry_if_necessary(
        crystal_symmetry=data_manager.get_model().crystal_symmetry()
    )

    # Reproduce the Reduce2 hydrogen-placement stage.
    reduce_add_h_obj = reduce_hydrogen.place_hydrogens(
        model=reduce_model,
        use_neutron_distances=params.use_neutron_distances,
        n_terminal_charge=params.n_terminal_charge,
        exclude_water=True,
        stop_for_unknowns=params.stop_on_any_missing_hydrogen,
        keep_existing_H=params.keep_existing_H,
    )

    reduce_add_h_obj.run()

    missed_residues = set(reduce_add_h_obj.no_H_placed_mlq)

    if not params.ignore_missing_restraints:
        if len(missed_residues) > 0:
            bad = ""
            for res in missed_residues:
                bad += " " + res
            raise RuntimeError(
                "Restraints were not found for the following residues:" + bad
            )

    insufficient_restraints = list(reduce_add_h_obj.site_labels_no_para)

    if params.stop_on_any_missing_hydrogen and len(insufficient_restraints) > 0:
        bad = insufficient_restraints[0]
        for res in insufficient_restraints[1:]:
            bad += "," + res

        raise RuntimeError(
            "Insufficient restraints were found for the following atoms:" + bad
        )

    reduce_model = reduce_add_h_obj.get_model()

    if not reduce_model.has_hd():
        raise RuntimeError(
            "It was not possible to place any H atoms. " "Is this a single atom model?"
        )

    # Match Reduce2's conditional reinterpretation.
    if not hasattr(reduce_model, "_type_energies"):
        reduce_model.get_hierarchy().sort_atoms_in_place()
        reduce_model.get_hierarchy().atoms().reset_serial()

        interpretation_params = reduce_hydrogen.get_reduce_pdb_interpretation_params(
            params.use_neutron_distances
        )

        interpretation_params.pdb_interpretation.disable_uc_volume_vs_n_atoms_check = (
            True
        )

        interpretation_params.pdb_interpretation.flip_symmetric_amino_acids = False

        reduce_model.set_stop_for_unknowns(params.stop_on_any_missing_hydrogen)

        reduce_model.process(
            make_restraints=True,
            pdb_interpretation_params=interpretation_params,
        )

    # This is the same Optimizers construction used by Reduce2.Program.run().
    opt = reduce2.Optimizers.Optimizer(
        params.probe,
        params.add_flip_movers,
        reduce_model,
        altID=params.alt_id,
        preferenceMagnitude=params.preference_magnitude,
        bondedNeighborDepth=4,
        nonFlipPreference=params.non_flip_preference,
        skipBondFixup=params.skip_bond_fix_up,
        flipStates=params.set_flip_states,
        verbosity=params.verbosity,
        cliqueOutlineFileName=params.output.clique_outline_file_name,
        fillAtomDump=params.output.print_atom_info,
    )

    output_string = opt.getInfo()

    amide_flips = _find_flips_in_output_string(
        output_string,
        "AmideFlip",
    )

    his_flips = _find_flips_in_output_string(
        output_string,
        "HisFlip",
    )

    return reduce_model, amide_flips, his_flips


def run_molprobity(
    model_path: str,
    fmodel=None,
    keep_hydrogens: bool = False,
):
    """
    Run CCTBX/Phenix-style MolProbity validation.

    Parameters
    ----------
    model_path
        Path to the PDB/mmCIF model.

    fmodel
        Optional mmtbx fmodel object.  If supplied, MolProbity can
        calculate the validation statistics that depend on experimental
        data.

    keep_hydrogens
        Whether hydrogen atoms should be retained in the validation
        calculation.

    Returns
    -------
    The mmtbx.validation.molprobity.molprobity result object.
    """
    model_path = str(Path(model_path))

    pdb_input = pdb.input(file_name=model_path)

    model_manager = model.manager(
        model_input=pdb_input,
    )

    # ------------------------------------------------------------------
    # MolProbity's nqh_flips class still invokes the removed legacy
    # "molprobity.reduce" executable.
    #
    # Replace that small component with Reduce2.
    # ------------------------------------------------------------------
    # original_nqh_flips = molprobity_module.nqh_flips
    original_nqh_flips = clashscore.nqh_flips

    class _Reduce2NqhFlips:
        """
        Drop-in replacement for mmtbx.validation.clashscore.nqh_flips.

        The installed CCTBX 2025.11 MolProbity code expects the legacy
        molprobity.reduce -BUILD - executable. This environment has Reduce2
        instead, so run Reduce2 through its Python API and convert its
        FlipMoverState objects into the legacy nqh_flip validation objects.
        """

        def __init__(self, pdb_hierarchy):
            self.results = []
            self.n_outliers = 0

            (
                _reduce_model,
                amide_flips,
                his_flips,
            ) = _run_reduce2_nqh_flips(pdb_hierarchy)

            from mmtbx.validation import utils

            use_segids = utils.use_segids_in_place_of_chainids(hierarchy=pdb_hierarchy)

            for flip in amide_flips + his_flips:
                if not flip.flipped:
                    continue

                result = clashscore.nqh_flip(
                    chain_id=flip.chain,
                    segid=None,
                    resseq=flip.resId,
                    icode=flip.iCode,
                    altloc=flip.altId,
                    resname=flip.resName,
                    outlier=True,
                )

                self.results.append(result)
                self.n_outliers += 1

        def show(self, out=None, prefix=""):
            if out is None:
                import sys

                out = sys.stdout

            for result in self.results:
                print(
                    prefix + result.as_string(),
                    file=out,
                )

    # ------------------------------------------------------------------
    # The installed MolProbity implementation calls geometry.clash(),
    # which in CCTBX 2025.11 still points at the legacy clashscore path.
    # Temporarily replace that one method with the Probe2 adapter.
    # ------------------------------------------------------------------
    original_nqh_flips = clashscore.nqh_flips
    original_geometry_clash = model_statistics.geometry.clash

    clashscore.nqh_flips = _Reduce2NqhFlips
    model_statistics.geometry.clash = _probe2_geometry_clash

    try:
        result = molprobity_module.molprobity(
            model=model_manager,
            fmodel=fmodel,
            keep_hydrogens=keep_hydrogens,
            nuclear=False,
            save_probe_unformatted_file=None,
        )
    finally:
        clashscore.nqh_flips = original_nqh_flips
        model_statistics.geometry.clash = original_geometry_clash

    out = StringIO()
    result.show(
        out=out,
        outliers_only=False,
        suppress_summary=False,
    )

    text = out.getvalue()
    print(text)

    return result


def format_report(result, model_path: str) -> str:
    from io import StringIO

    out = StringIO()

    result.show(
        out=out,
        outliers_only=False,
        suppress_summary=False,
    )

    return out.getvalue()
