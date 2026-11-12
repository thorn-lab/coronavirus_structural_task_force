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
    {path_in_repo}/validation/checkmymetal

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
from contextlib import nullcontext
from pathlib import Path

import pandas as pd

from cstf.validate import auspex as auspex_mod
from cstf.validate import haruspex as haruspex_mod
from cstf.validate.docker_service import ContainerService
from cstf.validate.base import Entry
from cstf.validate.auspex import AuspexStep
from cstf.validate.checkmymetal import CheckMyMetalStep
from cstf.validate.haruspex import HaruspexStep
from cstf.validate.pdb_redo import PDBRedoStep
from cstf.validate.phenix_replication.cablam import CablamStep
from cstf.validate.phenix_replication.charts import ChartsStep
from cstf.validate.phenix_replication.clashscore import ClashscoreStep
from cstf.validate.phenix_replication.molprobity import MolprobityStep
from cstf.validate.phenix_replication.reduce import ReduceStep
from cstf.validate.phenix_replication.xtriage import XtriageStep

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
    "checkmymetal",
]


def _step_factory(step_class, service_name=None):
    """Return a named-step factory with the shared constructor interface."""

    def create(*, skip_existing, auspex_service=None, haruspex_service=None):
        options = {"skip_existing": skip_existing}
        if service_name == "auspex":
            options["service"] = auspex_service
        elif service_name == "haruspex":
            options["service"] = haruspex_service
        return step_class(**options)

    return create


# Factories are kept here so the public step names, classes, and optional
# long-lived services are configured in one place.
STEP_FACTORIES = {
    "pdb_redo": _step_factory(PDBRedoStep),
    "auspex": _step_factory(AuspexStep, "auspex"),
    "haruspex": _step_factory(HaruspexStep, "haruspex"),
    "xtriage": _step_factory(XtriageStep),
    "cablam": _step_factory(CablamStep),
    "clashscore": _step_factory(ClashscoreStep),
    "reduce": _step_factory(ReduceStep),
    "molprobity": _step_factory(MolprobityStep),
    "charts": _step_factory(ChartsStep),
    "checkmymetal": _step_factory(CheckMyMetalStep),
}


def _selected_steps(steps):
    if steps is None:
        raise ValueError(
            "steps must be an iterable of step names; use STEP_NAMES for all"
        )
    selected = list(steps)
    unknown = set(selected) - set(STEP_NAMES)
    if unknown:
        raise ValueError(
            "Unknown validation step(s): {}. Choose from: {}".format(
                ", ".join(sorted(unknown)), ", ".join(STEP_NAMES)
            )
        )
    return list(dict.fromkeys(selected))


def _build_steps(steps, *, skip_existing, auspex_service=None, haruspex_service=None):
    return {
        name: STEP_FACTORIES[name](
            skip_existing=skip_existing,
            auspex_service=auspex_service,
            haruspex_service=haruspex_service,
        )
        for name in steps
    }


def find_structure_files(path_in_repo):
    """
    Locate the .pdb, .cif, and .mtz files in a directory.

    Returns a dict with keys 'pdb', 'cif', 'mtz', each either a Path
    or None if not found. Matching is by extension only (case
    insensitive), not by filename, since callers may use varying
    PDB-ID casing conventions (e.g. pdb_redo's lowercase entries).

    (Density maps for cryo-EM entries are discovered by HaruspexStep.)
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


def _process_entry(pdb_id, path_in_repo, *, exp_method, steps, validators):
    """Run already-initialised validators against a single entry."""
    path = Path(path_in_repo)
    entry = Entry(
        pdb_id=str(pdb_id),
        path=path,
        exp_method=exp_method,
        files=find_structure_files(path),
    )
    status = {step: "not_run" for step in steps}
    if entry.model_path is None:
        return {step: "no_input: no .pdb or .cif file found" for step in steps}

    for step_name in steps:
        try:
            status[step_name] = validators[step_name].run(entry)
        except Exception as exc:  # keep one failed step from stopping the rest
            logger.exception("%s failed for %s", step_name, pdb_id)
            status[step_name] = "error: {}".format(exc)
    return status


def run_pipeline(
    df,
    repo_path,
    path_column="path_in_repo",
    exp_method_column="exp_method",
    steps=STEP_NAMES,
    skip_existing=True,
    verbose=True,
):
    """
    Run the validation pipeline for every entry in df.

    Args:
        df: DataFrame indexed by PDB ID, with a column (default
            'path_in_repo') giving the directory containing that
            entry's files, and (optionally) an 'exp_method' column.
        steps: iterable of names from STEP_NAMES to run. Defaults to all
            steps; an empty iterable runs none.
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

    selected_steps = _selected_steps(steps)

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
    auspex_context = (
        ContainerService(auspex_mod.AUSPEX_IMAGE, auspex_mod.AUSPEX_PLATFORM, repo_path)
        if "auspex" in selected_steps
        else nullcontext(None)
    )
    haruspex_context = (
        ContainerService(
            haruspex_mod.HARUSPEX_IMAGE, haruspex_mod.HARUSPEX_PLATFORM, repo_path
        )
        if "haruspex" in selected_steps
        else nullcontext(None)
    )
    with auspex_context as auspex_svc, haruspex_context as haruspex_svc:
        validators = _build_steps(
            selected_steps,
            skip_existing=skip_existing,
            auspex_service=auspex_svc,
            haruspex_service=haruspex_svc,
        )
        for i, (pdb_id, row) in enumerate(df.iterrows(), start=1):
            if verbose:
                logger.info("[%d/%d] processing %s", i, total, pdb_id)
            try:
                records[pdb_id] = _process_entry(
                    pdb_id,
                    repo_path / row[path_column],
                    exp_method=row[exp_method_column] if has_exp_method else None,
                    steps=selected_steps,
                    validators=validators,
                )
            except Exception as exc:
                # _process_entry is designed not to raise, but guard here too
                # so one catastrophic entry (e.g. a permissions error
                # creating the validation dir) never aborts the batch.
                logger.error("Unhandled failure for %s: %s", pdb_id, exc)
                logger.debug(traceback.format_exc())
                records[pdb_id] = {
                    step: "error: unhandled failure - {}".format(exc)
                    for step in selected_steps
                }

    summary = pd.DataFrame.from_dict(records, orient="index")
    summary.index.name = df.index.name or "pdb_id"
    return summary[selected_steps]


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
        "--steps",
        nargs="*",
        choices=STEP_NAMES,
        default=STEP_NAMES,
        help="Validation steps to run; omit to run all steps",
    )
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
        steps=args.steps,
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
