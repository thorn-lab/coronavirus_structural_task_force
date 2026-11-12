import argparse
from pathlib import Path

import pandas as pd

from cstf.update import config, utils, query, io, report
from cstf.validate import orchestrator


def parse_args():
    parser = argparse.ArgumentParser(description="Run weekly update.")
    parser.add_argument(
        "-t",
        "--taxonomy",
        nargs="+",
        action="extend",
        required=True,
        choices=sorted(config.taxonomy_query),
        help="One or more taxonomies to update.",
    )
    parser.add_argument(
        "--steps",
        nargs="*",
        choices=orchestrator.STEP_NAMES,
        default=orchestrator.STEP_NAMES,
        help="Validation steps to run; omit to run all steps.",
    )
    parser.add_argument(
        "--start",
        default=None,
        help="Inclusive start date (YYYY-MM-DD); defaults to today.",
    )
    parser.add_argument(
        "--end",
        default=None,
        help="Inclusive end date (YYYY-MM-DD); defaults to today.",
    )
    parser.add_argument(
        "--repo-path",
        type=Path,
        default=Path(__file__).parents[1] / "data",
        help="Data/repository root (defaults to the project's data directory).",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    repo_path = args.repo_path
    taxonomies = list(dict.fromkeys(args.taxonomy))
    today = str(utils.get_time())
    start = args.start or today
    end = args.end or today
    if start > end:
        raise SystemExit("--start must be on or before --end")

    fasta_paths = [
        repo_path / "fasta" / f"seq_{taxonomy}.fasta" for taxonomy in taxonomies
    ]
    dataframes_path = repo_path / "dataframes"
    old_dfs = [
        pd.read_pickle(dataframes_path / f"repo_database_{taxonomy}_id_index.pkl")
        for taxonomy in taxonomies
    ]
    # Keep the first existing row if the same entry occurs in multiple databases.
    df = pd.concat(old_dfs, axis=0).loc[
        lambda data: ~data.index.duplicated(keep="first")
    ]

    rcsb_queries = config.Presets().queries(*taxonomies)
    attributes = config.Presets().attributes(
        "version_1", "version_2", "exp_method", "resolution", "title"
    )
    functions = config.Presets().functions(
        "version=version_1+version_2", "path_in_repo", "exp_method", "superseded_by"
    )

    print(f"repository path: {repo_path}")
    print("getting ids...")
    ids_by_taxonomy = query.get_ids(start, end, rcsb_queries)
    print("doing protein assignment...")
    ids_by_taxonomy_and_proteins = query.get_proteins(ids_by_taxonomy, fasta_paths)
    print("updating dataframe...")
    df = query.get_df(ids_by_taxonomy_and_proteins, attributes, functions, df)
    print("downloading files...")
    io.download_files(df, start, end, repo_path)
    print("checking for superseded...")
    io.delete_superseded(df, start, end, repo_path)
    print("writing reports...")
    report.write_reports(df, start, end, repo_path)
    orchestrator.run_pipeline(df, repo_path=repo_path, steps=args.steps)


if __name__ == "__main__":
    main()
