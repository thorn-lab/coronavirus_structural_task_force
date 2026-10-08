#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 26 15:08:08 2022

Check all sequences of certain folder (protein + taxonomy) and check its name
for potential misassignments.

@author: Maximilian Edich
"""

import os
import argparse

# argparse
parser = argparse.ArgumentParser(description="Example: python3 scan_for_missassignment.py -t SARS-CoV-2 -p nucleocapsid_protein -n orf9")
parser.add_argument('-t', '--taxonomy', type=str, required=True, help="Either 'SARS-CoV-2' or 'SARS-CoV'.")
parser.add_argument('-p', '--protein', type=str, required=True, help="Target protein, whose entries are scanned.")
parser.add_argument('-n', '--name', type=str, required=True, help="Name checked in entries.")
args = parser.parse_args()

name = args.name


# get list of entries
# # get path of target folder
cwd = os.path.dirname(os.path.join(os.path.realpath(__file__)))
cwd = os.path.dirname(cwd)
cwd = os.path.dirname(cwd)
cwd = os.path.join(cwd, "pdb", args.protein, args.taxonomy)

# loop over folders of entries
for folder in os.listdir(cwd):
    path = os.path.join(cwd, folder)
    if os.path.isdir(path):
        # load pdb file
        pdb_file = open(os.path.join(path, folder + ".pdb"), 'r')
        content = pdb_file.readlines()
        pdb_file.close()
        
        # extract title lines
        title = ""
        for line in content:
            if line[0:5] == "TITLE":
                title += line.strip()[10:]
            elif title != "":
                break
        if title.find(str(name).upper()) > -1:
            print(folder + " | " + title)
