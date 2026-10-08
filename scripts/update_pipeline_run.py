import argparse
import pandas as pd
from pathlib import Path
from rcsbapi.search import search_attributes as attrs
from cstf.update import config, utils, query, io, report

"""
executable script for weekly update
"""

# handle input arguments
parser = argparse.ArgumentParser(description="Run weekly update.")
parser.add_argument(
    "-t",
    "--taxonomy",
    type=str,
    required=True,
    help="Give the taxonomy, either 'SARS-CoV' or 'SARS-CoV-2'",
)
parser.add_argument(
    "-db",
    "--database",
    action="store_true",
    help="If given, the database will be updated as well",
)
args = parser.parse_args()

data_path = Path(__file__).parents[1] / "data"
repo_path = data_path
print(repo_path)
fasta_path = data_path / "fasta" / f"seq_{args.taxonomy}.fasta"
df = pd.read_pickle(
    data_path / "dataframes" / f"repo_database_{args.taxonomy}_id_index.pkl"
)
start = end = str(utils.get_time())
# start = "2025-03-12"
# end = "2025-05-12"
rcsb_queries = {k: v for k, v in config.taxonomy_query.items() if k in args.taxonomy}
attributes = ["version_1", "version_2", "exp_method", "resolution", "title"]
attributes = {k: v for k, v in config.rcsb_data_attributes.items() if k in attributes}
functions = [
    "version=version_1+version_2",
    "path_in_repo",
    "exp_method",
    "superseded_by",
]
functions = {
    k: v for k, v in config.functions_to_combine_columns.items() if k in functions
}

print("getting ids...")
ids_by_taxonomy = query.get_ids(start, end, rcsb_queries)
print("doing protein assigment...")
ids_by_taxonomy_and_proteins = query.get_proteins(ids_by_taxonomy, fasta_path)
print("updating dataframe...")
df = query.get_df(ids_by_taxonomy_and_proteins, attributes, functions, df)
print("downloading files...")
io.download_files(df, start, end, repo_path)
print("checking for superseded...")
io.delete_superseded(df, start, end, repo_path)
print("writing reports...")
report.write_reports(df, start, end, repo_path)

# new_df = df[ids]
# c_new_pdb_lst = new_df[new_df.version == 1].index
# changed_prot_list = pd.unique(list(proteins.values()))

"""
print("Doing sequence aligntment")
align.main(changed_prot_list, c_new_pdb_lst, repo_path, args.taxonomy)
print("Calculating RMSD")
RMSD.main(changed_prot_list, repo_path)

# check for common errors in the data base. These are currently:
# entries with wrong path containing 'not_assigned' after assignment
# entries not assigned to a protein at all
analyze_and_fix_dataframe.run(args.taxonomy)

# check for common errors in the assignment and give warnings, so the
# user can handle those manually.
tcp_scan_results.main(args.taxonomy, c_new_pdb_lst)

latest_report_path = (
    repo_path / "weekly_reports" / f"latest_update_report_{args.taxonomy}.txt"
)
report_content = ""
with open(latest_report_path, "r") as f:
    report_content = f.read()
# check for new nsp3
if report_content.find("nsp3") > -1:
    print("New Nsp3 structure: perform domain classification...")
    domain_classifier.main(args.taxo, "nsp3")


# if database flag given, update database
if args.database:
    # adding database folder to the system path
    sys.path.insert(0, Path.cwd().parent / "lib" / "database")
    # import module and automatically execute its main function
    from database import populate_database2

# read df to pickle
"""
