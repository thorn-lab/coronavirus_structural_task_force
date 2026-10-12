"""
orchestrator.py

Runs the open-source validation pipeline (pdb-redo, AUSPEX, Haruspex,
xtriage, cablam, clashscore, reduce, molprobity, charts) over a batch of PDB
entries described by a DataFrame indexed by PDB ID with a `path_in_repo`
column pointing at a directory containing one .pdb, .cif, and .mtz file each
(cryo-EM entries: a .pdb/.cif model plus a .mrc/.map/.ccp4 density map) --
the same layout the original run_xtriage.sh / run_cablam.sh /
run_molprobity.sh scripts walked.

Outputs are written to :
    {path_in_repo}/validation/pdb_redo
    {path_in_repo}/validation/Xtriage_output.log
    {path_in_repo}/validation/molprobity/cablam.out
    {path_in_repo}/validation/molprobity/clashscore.txt
    {path_in_repo}/validation/molprobity/{pdb_id}.H.pdb
    {path_in_repo}/validation/molprobity/molprobity.out
    {path_in_repo}/validation/molprobity/{pdb_id}_rama.pdf
    {path_in_repo}/validation/molprobity/{pdb_id}_multichart.pdf
    {path_in_repo}/validation/auspex/amplitudes.jpg
    {path_in_repo}/validation/haruspex/...            (EM entries only)

The two PDFs replace the original run_molprobity.sh's `rama_chart_pdf` and
`multichart` calls. They are matplotlib re-implementations (see charts.py),
so they carry the same information but are not pixel-identical to the
Phenix/MolProbity originals.

AUSPEX and Haruspex run in Docker (images built by
setup-validation-docker.sh). Each image is started ONCE per run_pipeline()
call as a long-lived container and reused via `docker exec` for every entry.
Containers start lazily, so Haruspex's container never starts if the batch
contains no ELECTRON MICROSCOPY entries.

Haruspex runs only for entries whose `exp_method` column equals
"ELECTRON MICROSCOPY" (case/whitespace-insensitive).

Usage:
    import pandas as pd
    from pathlib import Path
    from orchestrator import run_pipeline

    df = pd.DataFrame(
        {
            "path_in_repo": [...],
            "exp_method": ["X-RAY DIFFRACTION", "ELECTRON MICROSCOPY"],
        },
        index=["1abc", "2xyz"],
    )
    summary = run_pipeline(df, repo_path=Path("/data/repo"))
    summary.to_csv("validation_run_summary.csv")
"""

import logging
import sys
import traceback
from pathlib import Path

import pandas as pd

from cstf.validate import pdb_redo as pdb_redo_mod
from cstf.validate.phenix_replication import xtriage as xtriage_mod
from cstf.validate.phenix_replication import cablam as cablam_mod
from cstf.validate.phenix_replication import clashscore as clashscore_mod
from cstf.validate.phenix_replication import reduce as reduce_mod
from cstf.validate.phenix_replication import molprobity as molprobity_mod
from cstf.validate.phenix_replication import fmodel_builder as fmodel_mod
from cstf.validate.phenix_replication import charts as charts_mod
from cstf.validate import auspex as auspex_mod
from cstf.validate import haruspex as haruspex_mod
from cstf.validate.docker_service import ContainerService

log_dir = Path("logs/validation_runs")  # Relative or absolute path
log_dir.mkdir(parents=True, exist_ok=True)  # Creates folder structure if missing

log_file_path = log_dir / "xtal_validation.log"

logger = logging.getLogger("xtal_validation.orchestrator")
logger.setLevel(logging.INFO)
logger.propagate = False
if logger.hasHandlers():
    logger.handlers.clear()

file_handler = logging.FileHandler(log_file_path, mode="w")
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

logger.info(f"Log saved to: {log_file_path.resolve()}")

STEP_NAMES = [
    "pdb_redo",
    "auspex",
    "haruspex",
    "xtriage",
    "cablam",
    "clashscore",
    "reduce",
    "molprobity",
    "charts",
]

EM_METHOD = "ELECTRON MICROSCOPY"


def _is_em(exp_method):
    """True if exp_method is 'ELECTRON MICROSCOPY' (tolerates NaN/None,
    case and surrounding whitespace)."""
    return isinstance(exp_method, str) and exp_method.strip().upper() == EM_METHOD


def find_structure_files(path_in_repo):
    """
    Locate the .pdb, .cif, and .mtz files in a directory.

    Returns a dict with keys 'pdb', 'cif', 'mtz', each either a Path
    or None if not found. Matching is by extension only (case
    insensitive), not by filename, since callers may use varying
    PDB-ID casing conventions (e.g. pdb_redo's lowercase entries).

    (Density maps for cryo-EM entries are located separately by
    haruspex_mod.find_map.)
    """
    path = Path(path_in_repo)
    found = {"pdb": None, "cif": None, "mtz": None}
    if not path.is_dir():
        return found

    for f in path.iterdir():
        if not f.is_file():
            continue
        suffix = f.suffix.lower()
        if suffix == ".pdb" and found["pdb"] is None:
            found["pdb"] = f
        elif suffix == ".cif" and found["cif"] is None:
            found["cif"] = f
        elif suffix == ".mtz" and found["mtz"] is None:
            found["mtz"] = f
    return found


def _model_path(files):
    """Prefer .pdb over .cif for the model input, matching the
    original scripts' behavior of operating on the .pdb file."""
    return files["pdb"] or files["cif"]


def process_one(
    pdb_id,
    path_in_repo,
    skip_existing=True,
    exp_method=None,
    auspex_service=None,
    haruspex_service=None,
):
    """
    Run the full validation pipeline for a single PDB entry.

    Args:
        pdb_id: identifier, used for output filenames (e.g. the
            {pdb_id}.H.pdb hydrogenated model)
        path_in_repo: directory containing the entry's .pdb/.cif/.mtz
            (and, for cryo-EM entries, the density map)
        skip_existing: if True (default, matching the original bash
            scripts), skip a step whose output file already exists
            rather than recomputing it
        exp_method: the entry's experimental method. Haruspex only runs
            when this is "ELECTRON MICROSCOPY".
        auspex_service / haruspex_service: ContainerService instances
            shared across entries by run_pipeline(). If None, the tool
            wrappers start a temporary container for the single call.

    Returns:
        a dict with one status entry per step in STEP_NAMES, each
        either 'done', 'skipped', 'no_input' (required input file
        missing), 'not_applicable' (step doesn't apply to this
        experimental method), or 'error: <message>'. Never raises -- a
        failure in one step is recorded and the remaining steps for that
        entry are still attempted where feasible, and failures in one
        entry never stop processing of other entries in run_pipeline().
    """
    path = Path(path_in_repo)
    status = {step: "not_run" for step in STEP_NAMES}

    files = find_structure_files(path)
    model_path = _model_path(files)

    validation_dir = path / "validation"
    auspex_dir = validation_dir / "auspex"
    haruspex_dir = validation_dir / "haruspex"
    molprobity_dir = validation_dir / "molprobity"

    if model_path is None:
        for step in STEP_NAMES:
            status[step] = "no_input: no .pdb or .cif file found"
        return status

    validation_dir.mkdir(exist_ok=True)
    auspex_dir.mkdir(exist_ok=True)
    molprobity_dir.mkdir(exist_ok=True)

    # Results kept in memory so the charts step can reuse them when the
    # corresponding step actually ran in this call (they are None when a
    # step was skipped because its output already existed, or failed).
    cablam_result = None
    clash_result = None
    mp_result = None

    # --- pdb-redo ---
    try:
        redo_result = pdb_redo_mod.prepare_entry(
            pdb_id=pdb_id,
            entry_path=path,
            skip_existing=skip_existing,
        )
        status["pdb_redo"] = redo_result.status
    except Exception as exc:  # defensive guard
        status["pdb_redo"] = f"error: {exc}"

    # --- xtriage: needs reflection data ---
    xtriage_log = validation_dir / "Xtriage_output.log"
    if files["mtz"] is None:
        status["xtriage"] = "no_input: no .mtz file found"
    elif skip_existing and xtriage_log.exists():
        status["xtriage"] = "skipped"
    else:
        try:
            with open(xtriage_log, "w") as fh:
                xtriage_mod.run_xtriage(
                    str(files["mtz"]),
                    # model_path=str(model_path),
                    out_stream=fh,
                )
            status["xtriage"] = "done"
        except Exception as exc:  # noqa: BLE001
            status["xtriage"] = "error: {}".format(exc)
            logger.warning("xtriage failed for %s: %s", pdb_id, exc)
            logger.debug(traceback.format_exc())

    # --- cablam ---
    cablam_out = molprobity_dir / "cablam.out"
    if skip_existing and cablam_out.exists():
        status["cablam"] = "skipped"
    else:
        try:
            cablam_result = cablam_mod.run_cablam(str(model_path))
            report = cablam_mod.format_report(cablam_result, str(model_path))
            cablam_out.write_text(report + "\n")
            status["cablam"] = "done"
        except Exception as exc:  # noqa: BLE001
            status["cablam"] = "error: {}".format(exc)
            logger.warning("cablam failed for %s: %s", pdb_id, exc)
            logger.debug(traceback.format_exc())

    # --- clashscore ---
    clashscore_txt = molprobity_dir / "clashscore.txt"
    if skip_existing and clashscore_txt.exists():
        status["clashscore"] = "skipped"
    else:
        try:
            clash_result = clashscore_mod.run_clashscore(str(model_path))
            report = clashscore_mod.format_report(clash_result, str(model_path))
            clashscore_txt.write_text(report + "\n")
            status["clashscore"] = "done"
        except Exception as exc:  # noqa: BLE001
            status["clashscore"] = "error: {}".format(exc)
            logger.warning("clashscore failed for %s: %s", pdb_id, exc)
            logger.debug(traceback.format_exc())

    # --- reduce (add hydrogens) ---
    h_pdb = molprobity_dir / "{}.H.pdb".format(pdb_id)
    if skip_existing and h_pdb.exists():
        status["reduce"] = "skipped"
    else:
        try:
            backend = reduce_mod.add_hydrogens(str(model_path), str(h_pdb))
            status["reduce"] = "done ({})".format(backend)
        except Exception as exc:  # noqa: BLE001
            status["reduce"] = "error: {}".format(exc)
            logger.warning("reduce failed for %s: %s", pdb_id, exc)
            logger.debug(traceback.format_exc())

    # --- molprobity aggregate report ---
    molprobity_out = molprobity_dir / "molprobity.out"
    if skip_existing and molprobity_out.exists():
        status["molprobity"] = "skipped"
    else:
        try:
            mtz_arg = str(files["mtz"]) if files["mtz"] else None
            fmodel = None
            if mtz_arg:
                fmodel = fmodel_mod.build_fmodel(
                    model_path=str(model_path),
                    mtz_path=mtz_arg,
                )

            mp_result = molprobity_mod.run_molprobity(
                str(model_path),
                fmodel=fmodel,
            )

            report = molprobity_mod.format_report(mp_result, str(model_path))

            molprobity_out.write_text(report + "\n")

            status["molprobity"] = "done" + (
                "" if fmodel is not None else " (model-only, no .mtz found)"
            )
        except Exception as exc:  # noqa: BLE001
            status["molprobity"] = "error: {}".format(exc)
            logger.warning("molprobity failed for %s: %s", pdb_id, exc)
            logger.debug(traceback.format_exc())
            print(traceback.format_exc())

    # --- charts (replaces rama_chart_pdf + multichart) ---
    rama_pdf = molprobity_dir / "{}_rama.pdf".format(pdb_id)
    multi_pdf = molprobity_dir / "{}_multichart.pdf".format(pdb_id)
    if skip_existing and rama_pdf.exists() and multi_pdf.exists():
        status["charts"] = "skipped"
    else:
        try:
            # If the molprobity step didn't run in this call (skipped or
            # failed) there is no in-memory result, so compute one. Charts
            # don't need map/R-factor statistics, so model-only is enough.
            if mp_result is None:
                mp_result = molprobity_mod.run_molprobity(str(model_path), fmodel=None)

            # Attribute names follow mmtbx.validation.molprobity.molprobity;
            # adjust here if your run_molprobity wrapper exposes them
            # differently. cablam/clashes fall back to the standalone
            # steps' results when the aggregate doesn't carry them.
            rama = getattr(mp_result, "ramalyze", None)
            rota = getattr(mp_result, "rotalyze", None)
            cbeta = getattr(mp_result, "cbetadev", None)
            clashes = getattr(mp_result, "clashes", None) or clash_result
            cablam = getattr(mp_result, "cablam", None) or cablam_result

            import iotbx.pdb  # deferred: only needed for this step

            hierarchy = iotbx.pdb.input(file_name=str(model_path)).construct_hierarchy()

            written = charts_mod.write_charts(
                pdb_id,
                hierarchy,
                molprobity_dir,
                rama=rama,
                rota=rota,
                cbeta=cbeta,
                clashes=clashes,
                cablam=cablam,
            )
            # write_charts logs and swallows per-chart failures, so judge
            # success by which files actually came back.
            missing = {"rama", "multichart"} - set(written)
            if missing:
                status["charts"] = "partial: missing {} (see log)".format(
                    ", ".join(sorted(missing))
                )
            else:
                status["charts"] = "done"
        except Exception as exc:  # noqa: BLE001
            status["charts"] = "error: {}".format(exc)
            logger.warning("charts failed for %s: %s", pdb_id, exc)
            logger.debug(traceback.format_exc())

    # --- AUSPEX: amplitudes diagnostic plot ---
    # AUSPEX uses the existing MTZ as input. It does not copy the MTZ into
    # validation/auspex; the only output retained by this pipeline is
    # amplitudes.jpg. Runs in the shared AUSPEX container.
    amplitudes_jpg = auspex_dir / "amplitudes.jpg"
    if files["mtz"] is None:
        status["auspex"] = "no_input: no .mtz file found"
    elif skip_existing and amplitudes_jpg.exists():
        status["auspex"] = "skipped"
    else:
        try:
            auspex_mod.run_auspex(
                mtz_path=str(files["mtz"]),
                output_dir=str(auspex_dir),
                output_jpg=str(amplitudes_jpg),
                service=auspex_service,
                keep_extra=True,  # Change this after confirming exact output
            )
            if amplitudes_jpg.exists():
                status["auspex"] = "done"
            else:
                status["auspex"] = "error: AUSPEX did not produce amplitudes.jpg"
        except Exception as exc:  # noqa: BLE001
            status["auspex"] = "error: {}".format(exc)
            logger.warning("AUSPEX failed for %s: %s", pdb_id, exc)
            logger.debug(traceback.format_exc())
            print(traceback.format_exc())

    # --- Haruspex: cryo-EM entries only, run on the deposited density map ---
    # Runs in the shared Haruspex container. Skipped entirely (and the
    # container never started) for non-EM entries.
    if not _is_em(exp_method):
        status["haruspex"] = "not_applicable: exp_method is {!r}".format(exp_method)
    else:
        em_map = haruspex_mod.find_map(path)
        if em_map is None:
            status["haruspex"] = "no_input: no .mrc/.map/.ccp4 file found"
        elif skip_existing and (haruspex_dir / "haruspex_stdout.log").exists():
            status["haruspex"] = "skipped"
        else:
            try:
                haruspex_dir.mkdir(exist_ok=True)
                produced = haruspex_mod.run_haruspex(
                    map_path=str(em_map),
                    output_dir=str(haruspex_dir),
                    service=haruspex_service,
                )
                status["haruspex"] = "done ({} files)".format(len(produced))
            except Exception as exc:  # noqa: BLE001
                status["haruspex"] = "error: {}".format(exc)
                logger.warning("Haruspex failed for %s: %s", pdb_id, exc)
                logger.debug(traceback.format_exc())

    return status


def run_pipeline(
    df,
    repo_path,
    path_column="path_in_repo",
    exp_method_column="exp_method",
    skip_existing=True,
    verbose=True,
):
    """
    Run the validation pipeline for every entry in df.

    Args:
        df: DataFrame indexed by PDB ID, with a column (default
            'path_in_repo') giving the directory containing that
            entry's files, and (optionally) an 'exp_method' column.
        repo_path: root that each path_column value is joined onto. It is
            also the directory mounted into the AUSPEX/Haruspex
            containers, so every entry directory must live under it.
        path_column: name of the column holding the directory path
        exp_method_column: name of the column holding the experimental
            method. Haruspex runs only where it equals
            "ELECTRON MICROSCOPY". If the column is missing, Haruspex is
            marked not_applicable for every entry.
        skip_existing: skip steps whose output already exists,
            matching the original bash scripts' caching behavior
        verbose: log a line per entry as it's processed

    Returns:
        a DataFrame indexed the same as df, with one column per
        pipeline step (see STEP_NAMES) holding a status string for that
        step. Never raises for individual-entry failures -- check the
        returned DataFrame for 'error: ...' values to find problem
        entries.
    """
    if path_column not in df.columns:
        raise ValueError("df must have a '{}' column".format(path_column))

    has_exp_method = exp_method_column in df.columns
    if not has_exp_method:
        logger.warning(
            "No '%s' column in df; Haruspex will be skipped for all entries",
            exp_method_column,
        )

    repo_path = Path(repo_path).resolve()
    records = {}
    total = len(df)

    # One container per tool for the whole batch. Both start lazily on their
    # first exec() and are stopped when the with-block exits (even on error).
    with (
        ContainerService(
            auspex_mod.AUSPEX_IMAGE, auspex_mod.AUSPEX_PLATFORM, repo_path
        ) as auspex_svc,
        ContainerService(
            haruspex_mod.HARUSPEX_IMAGE, haruspex_mod.HARUSPEX_PLATFORM, repo_path
        ) as haruspex_svc,
    ):
        for i, (pdb_id, row) in enumerate(df.iterrows(), start=1):
            if verbose:
                logger.info("[%d/%d] processing %s", i, total, pdb_id)
            try:
                records[pdb_id] = process_one(
                    pdb_id,
                    repo_path / row[path_column],
                    skip_existing=skip_existing,
                    exp_method=row[exp_method_column] if has_exp_method else None,
                    auspex_service=auspex_svc,
                    haruspex_service=haruspex_svc,
                )
            except Exception as exc:  # noqa: BLE001
                # process_one is designed not to raise, but guard here too
                # so one catastrophic entry (e.g. a permissions error
                # creating the validation dir) never aborts the batch.
                logger.error("Unhandled failure for %s: %s", pdb_id, exc)
                logger.debug(traceback.format_exc())
                records[pdb_id] = {
                    step: "error: unhandled failure - {}".format(exc)
                    for step in STEP_NAMES
                }

    summary = pd.DataFrame.from_dict(records, orient="index")
    summary.index.name = df.index.name or "pdb_id"
    return summary[STEP_NAMES]


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Run the validation pipeline over a CSV with "
        "pdb_id, path_in_repo and (optionally) exp_method columns."
    )
    parser.add_argument(
        "csv", help="CSV with pdb_id (as index), path_in_repo and exp_method columns"
    )
    parser.add_argument(
        "--repo-path",
        required=True,
        help="Root directory that path_in_repo values are relative to "
        "(mounted into the AUSPEX/Haruspex containers)",
    )
    parser.add_argument("--path-column", default="path_in_repo")
    parser.add_argument("--exp-method-column", default="exp_method")
    parser.add_argument(
        "--no-skip-existing",
        action="store_true",
        help="Recompute steps even if output exists",
    )
    parser.add_argument("--out", default="validation_run_summary.csv")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        stream=sys.stderr,
    )

    df = pd.read_csv(args.csv, index_col=0)
    summary = run_pipeline(
        df,
        repo_path=Path(args.repo_path),
        path_column=args.path_column,
        exp_method_column=args.exp_method_column,
        skip_existing=not args.no_skip_existing,
    )
    summary.to_csv(args.out)
    logger.info("Summary written to %s", args.out)

    n_errors = summary.apply(lambda col: col.str.startswith("error").sum()).sum()
    if n_errors:
        logger.warning(
            "%d step-level errors across the batch; see %s", n_errors, args.out
        )


if __name__ == "__main__":
    main()
