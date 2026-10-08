#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  2 14:07:29 2021

This contains functions used to analyze the data frame or to fix bugs.

@author: Maximilian Edich
"""

import os
import pandas as pd

from update_pipeline import io


db_string_1 = "main_repo_database_SARS-CoV.pkl"
df_SC1 = pd.read_pickle(db_string_1)
db_string_2 = "main_repo_database_SARS-CoV-2.pkl"
df_SC2 = pd.read_pickle(db_string_2)



# # # Remove duplicates
def scan_for_duplicates(taxonomy):
    """
    Look for duplicates but do not modify the database.
    Returns: Number of relevant cases.
    """
    # specify used data frame
    if taxonomy == "SARS-CoV-2":
        df = df_SC2
    else:
        df = df_SC1
    
    duplicates = []
    for entry in df['pdb_id']:
        if len(df.loc[df['pdb_id'] == entry]) != 1:
            if not (entry in duplicates):
                duplicates.append(entry)
    print("List of pdb_ids with duplicates in data base:")
    print(duplicates)
    print("Number of duplicates: " + str(len(duplicates)))
    print("Total number of database entries: " + str(len(df)))
    
    return len(duplicates)
    

def remove_duplicates(taxonomy):
    """
    Look for duplicates, drop them from the database and apply the changes.
    Returns: None
    """
    # specify used data frame
    if taxonomy == "SARS-CoV-2":
        df = df_SC2
        db_string = db_string_2
    else:
        df = df_SC1
        db_string = db_string_1
    
    # locate duplicates
    duplicates = []
    for entry in df['pdb_id']:
        if len(df.loc[df['pdb_id'] == entry]) != 1:
            if not (entry in duplicates):
                duplicates.append(entry)
    print(duplicates)
    print(len(duplicates))
    
    print(len(df))
    
    # drop duplicates
    nf = df.drop_duplicates()
    
    for dupe in duplicates:
        prot = nf.loc[nf['pdb_id'] == dupe]
        print(prot)
    
    print(len(nf))
    nf.to_pickle(db_string)


# # # Change path of not assigned
def scan_for_not_assigned(taxonomy):
    """
    Look for entries containing 'not_assigned' in their path.
    Does not apply any changes to the database.
    Returns: Number of relevant cases.
    """
    # specify used data frame
    if taxonomy == "SARS-CoV-2":
        df = df_SC2
    else:
        df = df_SC1
        
    # find entries with 'not_assigned' in their path
    print("Entries containing 'not_assigned':")
    not_assigned = []
    for entry in df['path_in_repo']:
        if str(entry).find('not_assigned') >= 0:
            prot = df.loc[df['path_in_repo'] == entry, 'protein'].iloc[0]
            pdb_id = df.loc[df['path_in_repo'] == entry, 'pdb_id'].iloc[0]
            print(entry)
            not_assigned.append(entry)
    print("Number of such cases: " + str(len(not_assigned)))
    
    return len(not_assigned)


def update_path_of_not_assigned(taxonomy):
    """
    Look for entries containing 'not_assigned' in their path.
    Fix their path, if they are in fact assigned and apply changes to
    database.
    Returns: None
    """
    # specify used data frame
    if taxonomy == "SARS-CoV-2":
        df = df_SC2
        db_string = db_string_2
    else:
        df = df_SC1
        db_string = db_string_1
        
    # find entries with 'not_assigned' in their path
    not_assigned = []
    for entry in df['path_in_repo']:
        if str(entry).find('not_assigned') >= 0:
            prot = df.loc[df['path_in_repo'] == entry, 'protein'].iloc[0]
            pdb_id = df.loc[df['path_in_repo'] == entry, 'pdb_id'].iloc[0]
            print("entry:" + entry)
            print("prot:" + prot)
            
            if prot == "not_assigned":
                # pdb has to be assigned manually
                not_assigned.append(pdb_id)
                print(prot)
            else:
                # update path
                new_path = os.path.join("pdb", prot, taxonomy, pdb_id)
                print(new_path)
                df.loc[df["pdb_id"] == pdb_id,"path_in_repo"] = new_path
                print(df.loc[df["pdb_id"] == pdb_id,"path_in_repo"])
            print()
            
    print(len(not_assigned))
    print(not_assigned)
    print("these pdbs have to be assigned manually")
    df.to_pickle(db_string)
    

def assign_protein_to_data_frame_entry(pdb_id, protein, taxonomy):
    """
    Assign a protein to a certain database entry and save changes.
    Used for not_assigned proteins which have the files in correct place.
    Returns: None
    """
    # specify used data frame
    if taxonomy == "SARS-CoV-2":
        df = df_SC2
        db_string = db_string_2
    else:
        df = df_SC1
        db_string = db_string_1
        
    df.loc[df["pdb_id"] == pdb_id, "protein"] = protein
    df.to_pickle(db_string)

def delete_entry_from_database(pdb_id, taxonomy):
    """
    Use this function to delete entries which do not correspong to SARS-CoV
    or SARS-CoV-2.
    One example is 7f8l, which was somehow classified as SARS-CoV
    """
    # specify used data frame
    if taxonomy == "SARS-CoV-2":
        df = df_SC2
        db_string = db_string_2
    else:
        df = df_SC1
        db_string = db_string_1
        
    print("Total number of database entries: " + str(len(df)))
    # load old entry and drop it from old dataframe
    entry = df.loc[df['pdb_id'] == pdb_id]
    df_new = df.drop(entry.index)
    print("Total number of database entries: " + str(len(df_new)))
    df_new.to_pickle(db_string)
    
def print_entry(pdb_id, taxonomy):
    """
    Prints the entry with the given id.
    """
    # specify used data frame
    if taxonomy == "SARS-CoV-2":
        df = df_SC2
    else:
        df = df_SC1
        
    entry = df.loc[df['pdb_id'] == pdb_id]
    print(entry['protein'])


def run(taxonomy):
    print("Perform scans for errors in database.")
    errors = scan_for_duplicates(taxonomy)
    errors += scan_for_not_assigned(taxonomy)
    if errors == 0:
        print("Scan was succesful, no errors found!\n")
    else:
        print("Scan finished. Scan revealed " + str(errors) + " errors!\n")
        print("look into code of 'analyze_and_fix_dataframe.py' to perform manual "
              + "fixing with the respective functions!")
    # for fixing the errors, call the respective functions from above


def change_df_dtype(taxonomy, invert_superseded_by=False, repo_path=None):
    """
    This function was used to change the dtypes of the columns of
    the dataframes, and invert the superseded logic. Previously, the
    for an id i, the superseded_by column recorded which id j it superseded.
    After running the function with invert_superseded_by, the superseded_by column
    of entry j says i, indicating that j was superseded by i.
    """
    if taxonomy == "SARS-CoV-2":
        df = df_SC2
    else:
        df = df_SC1

    df = df.set_index("pdb_id")
    df["release_date"] = pd.to_datetime(df["release_date"]).dt.date
    df["last_revision"] = pd.to_datetime(df["last_revision"]).dt.date
    # Replace SARS-CoV-1 with SARS-CoV in paths
    mask = df["path_in_repo"].str.contains("SARS-CoV-1", na=False)
    df.loc[mask, "path_in_repo"] = df.loc[mask, "path_in_repo"].str.replace(
        "SARS-CoV-1", "SARS-CoV"
    )
    df.loc[:, ["version", "resolution"]] = df.loc[:, ["version", "resolution"]].astype(
        float
    )
    df[["protein", "path_in_repo"]] = df[["protein", "path_in_repo"]].replace(" ", "_")
    if invert_superseded_by:
        ids = df.index[pd.notna(df.superseded_by)].tolist()
        df.loc[ids, "superseded_by"] = float("NaN")
        io.download_files(ids, df, repo_path)
        io.delete_superseded(ids, df, repo_path)
    df.to_pickle(f"main_repo_database_{taxonomy}_copy.pkl")
    return df

