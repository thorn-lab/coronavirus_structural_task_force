#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  9 14:36:05 2022
This module iterates over all new structures and checks their assignments
on errors by checking also the title, taxonomy, and so on.

@author: localadmin
"""

import os
import pandas as pd


def main(taxononomy, c_new_pdb_lst):
    """
    Parameters
    ----------
    taxnonomy : String
        Value is either 'SARS-CoV' or 'SARS-CoV-2'.
    c_new_pdb_lst : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    print("scan!")
    print(c_new_pdb_lst)
    print("scan off.")
    
    repo_path = os.path.abspath(os.path.join(__file__ ,"..", "..", ".."))
    df = pd.read_pickle("main_repo_database_{}.pkl".format(taxononomy))
    
    # iterate over each entry and keept track of warnings
    # entries are string of PDB id
    warnings = []
    for pdb_id in c_new_pdb_lst:
        # TODO if title taxonomy and real taxonomy do not agree, store warning
        db_entry = df.loc[df['pdb_id'] == pdb_id]
        
        # get path from entry
        entry_path = db_entry['path_in_repo'].values[0]
        pdb_path = os.path.join(repo_path, entry_path, pdb_id + ".pdb")
        print(pdb_path)
        
        # get pdb file from path
        pdb_file = open(pdb_path, 'r')
        pdb_file_content = pdb_file.readlines()
        pdb_file.close()
        
        # look for title lines
        title = ""
        for line in pdb_file_content:
            if line.find("TITLE") > -1:
                title += line[10:].strip() + " "
            elif title != "":
                # title already red, nothing more to come
                break
        title = title.strip().capitalize()
        print(title)
        
        # check for SARS-CoV-2 in title of SARS-CoV structure
        if taxononomy == "SARS-CoV":
            if (title.find("SARS-COV-2") > -1
                    or title.find("SARS-CORONAVIRUS-2") > -1
                    or title.find("SARS CORONAVIRUS 2") > -1
                    or title.find("SARS CORONAVIRUS-2") > -1):
                warnings.append([pdb_id], "contains wrong taxonomy in title!")
    
    # print out warnings
    # may adapt structure if more warnings per pdb id
    print("Warnings in total: " + str(len(warnings)))
    for warn in warnings:
        print(warn[0] + ": " + warn[1])
    
    return

