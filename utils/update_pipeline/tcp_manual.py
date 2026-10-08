import os
import shutil
import pandas as pd
import argparse

"""
script to manually assign proteins in non_assigned folder, call main 
"""


def main(pdb_id, old_protein, old_taxo, new_protein, new_taxo):
    repo_path = os.path.abspath(os.path.join(__file__ ,"../../..","pdb"))
    move_n_del(repo_path, pdb_id, old_protein, old_taxo, new_protein, new_taxo)
    change_database_entry(pdb_id, old_protein, old_taxo, new_protein, new_taxo)

def move_n_del(repo_path, pdb_id, old_protein, old_taxo, new_protein, new_taxo):
    # copy folders to new location
    shutil.copytree(os.path.join(repo_path, old_protein, old_taxo, pdb_id),
                    os.path.join(repo_path, new_protein, new_taxo, pdb_id))
    # delete folders at old location
    shutil.rmtree(os.path.join(repo_path, old_protein, old_taxo, pdb_id))

def change_database_entry(pdb_id, old_protein, old_taxo, new_protein, new_taxo):
    # if both taxo ids are the same, modify entry in the same database
    # otherwise, delete it in old and create one in new database.
    if old_taxo == new_taxo:
        # load database
        df = pd.read_pickle("main_repo_database_" + old_taxo + ".pkl")
        # set new protein value
        df.loc[df["pdb_id"] == pdb_id, "protein"] = new_protein
        # set new repo path
        df.loc[df["pdb_id"] == pdb_id,"path_in_repo"] = os.path.join("pdb", new_protein, old_taxo, pdb_id)
        # write to db file
        df.to_pickle("main_repo_database_" + old_taxo + ".pkl")
    else:
        # load databases
        df_old = pd.read_pickle("main_repo_database_" + old_taxo + ".pkl")
        df_new = pd.read_pickle("main_repo_database_" + new_taxo + ".pkl")
        # load old entry and drop it from old dataframe
        entry = df_old.loc[df_old['pdb_id'] == pdb_id]
        df_old = df_old.drop(entry.index)
        # modify entry add add it to new dataframe
        print("old path: " + entry["path_in_repo"].item())
        entry["protein"] = new_protein
        entry["path_in_repo"] = os.path.join("pdb", new_protein, new_taxo, pdb_id)
        print("new path: " + entry["path_in_repo"].item())
        df_new = df_new.append(entry)
        # write to db files
        df_old.to_pickle("main_repo_database_" + old_taxo + ".pkl")
        df_new.to_pickle("main_repo_database_" + new_taxo + ".pkl")


if __name__ == '__main__':
    # handle input arguments
    parser = argparse.ArgumentParser(description='Run manual assignment after weekly update.')
    parser.add_argument('-pdb', '--pdb_id', type=str, required=True, help="Give the pdb_id")
    parser.add_argument('-op', '--old_protein', type=str, required=True, help="Give the protein where it is found now. Might be 'not_assigned'")
    parser.add_argument('-np', '--new_protein', type=str, required=True, help="Give the protein to which the id should be assigned to")
    parser.add_argument('-ot', '--old_taxonomy', type=str, required=True, help="Give the taxonomy where it is found now, either 'SARS-CoV' or 'SARS-CoV-2'")
    parser.add_argument('-nt', '--new_taxonomy', type=str, required=True, help="Give the taxonomy to which it should be assigned, either 'SARS-CoV' or 'SARS-CoV-2'")
    args = parser.parse_args()
    
    taxo_sars_cov = "SARS-CoV"
    taxo_sars_cov_2 = "SARS-CoV-2"
    
    if args.old_taxonomy != taxo_sars_cov and args.old_taxonomy != taxo_sars_cov_2:
        exit("ERROR: Wrong taxonomy, check typos!")
    if args.new_taxonomy != taxo_sars_cov and args.new_taxonomy != taxo_sars_cov_2:
        exit("ERROR: Wrong taxonomy, check typos!")
    
    main(args.pdb_id, args.old_protein, args.old_taxonomy, args.new_protein, args.new_taxonomy)


