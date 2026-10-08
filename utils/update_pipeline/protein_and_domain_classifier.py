#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  4 17:31:27 2021

This script iterates through all entries in a certain folder of a protein 
and classifies each PDB to the corresponding domain.
Classification of domains is based on a sequence alignment.
You may have to create a fasta file first, which contains all sequences of
the domains.
At the end, an xcel sheet is given out, containing all relevant information.

@author: localadmin
"""

import os
from os.path import join
import argparse
import gemmi

from Bio import pairwise2
from Bio import BiopythonWarning
import warnings
with warnings.catch_warnings():
    warnings.simplefilter('ignore', BiopythonWarning)
    from Bio import SeqIO
    from Bio.PDB import MMCIFParser
    from Bio.PDB import PPBuilder


import xlsxwriter


def main(taxonomy, protein):
    """
    Main script.

    Parameters
    ----------
    taxonomy : String
        either SARS-CoV or SARS-CoV-2.
    protein : String
        Name of the protein.

    Returns
    -------
    None.
    """

    taxo_sars_cov = "SARS-CoV"
    taxo_sars_cov_2 = "SARS-CoV-2"
    
    sars_cov_1_2_id = "694009" #SARS-CoV-1 & SARS-CoV-2
    sars_cov_2_id = "2697049" #SARS-CoV-2
    
    if taxonomy != taxo_sars_cov and taxonomy != taxo_sars_cov_2:
        exit("ERROR: Wrong taxonomy, check typos!")
    
    try:
        os.chdir(join("..", "..", "pdb", protein, taxonomy))
    except FileNotFoundError:
        exit("ERROR: path not found. Check your -p input.")
    print("work with files from:")
    print(os.getcwd())
    
    # load domain sequences from fasta file
    try:
        fasta_sequences = SeqIO.parse(open(join(os.getcwd(), "sequence_domain_info.fasta")),'fasta')
    except FileNotFoundError:
        exit("ERROR: no file called 'sequence_domain_info.fasta' found in target folder.")
    fasta_seq_domains_iter = []
    for fasta in fasta_sequences:
        domain_name, domain_sequence = fasta.id, str(fasta.seq)
        fasta_seq_domains_iter.append((domain_name, domain_sequence))
    
    # lists for final results
    entries_and_domains = []
    organisms = []
    
    # init parser for mmcif files
    parser = MMCIFParser()
    ppb = PPBuilder()
    
    print("iterate over entries...")
    # iterate over all entries in dir
    for entry in os.listdir():
        if os.path.isdir(join(os.getcwd(), entry)):
            entry_pdb_path = join(os.getcwd(), entry, entry + ".pdb")
            entry_cif_path = join(os.getcwd(), entry, entry + ".cif")
            # load model from pdb
            # try to load pdb structure via gemmi
            try:
                pdb_entry = gemmi.read_pdb(entry_pdb_path)
            except:
                entry_pdb_path = join(os.getcwd(), entry, entry + "_false.pdb")
                pdb_entry = gemmi.read_pdb(entry_pdb_path)
            
            # load fasta file from pdb
            try:
                pdb_file = open(entry_pdb_path, 'r')
            except:
                entry_pdb_path = join(os.getcwd(), entry, entry + "_false.pdb")
                pdb_file = open(entry_pdb_path, 'r')
            
            # parse cif model
            structure = parser.get_structure(entry, entry_cif_path)
            cif_model = structure[0]
            
            sequences = []
            try:
                for record in SeqIO.parse(pdb_file, 'pdb-atom'):
                    sequences.append([record.id, record.seq])
                    rec_annotations = record
            except:
                print("ERROR: ??? unknown parsing error.")
                print(entry)
                continue
            
            # check if entry has non-viral interaction partners
            for x in range(len(rec_annotations.annotations.get("source"))):
                organism = rec_annotations.annotations.get("source").get(str(x+1)).get("organism_scientific")
                added = False
                for k in organisms:
                    if k[0] == organism:
                        k[1].append(entry)
                        added = True
                if not added:
                    organisms.append([organism, [entry]])
            
            # for each chain, load sequence if polypeptide
            best_chain_domain = "None"
            domain_hits = []
            for chain in cif_model:                
                # get polypeptide from chain
                try:
                    pp = ppb.build_peptides(chain)[0]
                except IndexError:
                    print("ERROR: no model from pp builder")
                    print(entry)
                    continue
                
                chain_sequence = str(pp.get_sequence()).replace('-', '')
                # do sequence alignment for each sequence from fasta and track best
                for fasta in fasta_seq_domains_iter:
                    domain_name, domain_sequence = fasta
                    result = gemmi.align_string_sequences(list(chain_sequence), list(domain_sequence), [])
                    # if high identity, save domain as hit
                    if result.calculate_identity() > 95:
                        hit_added = False
                        for hit in domain_hits:
                            if hit == domain_name:
                                hit_added = True
                                break
                        if not hit_added:
                            domain_hits.append(domain_name)
                            print(entry, domain_name, result.calculate_identity())
                
                
            if len(domain_hits) > 0:
                best_chain_domain = ""
                for hit in domain_hits:
                    best_chain_domain += hit + "_"
                
                
            # check if domain was already added to final results
            save_entry = [entry, pdb_entry.resolution, 0, 0, 0]
            for key, value in pdb_entry.info.items():
                if key == "_struct.title":
                    save_entry[2] = value
                if key == "_exptl.method":
                    save_entry[3] = value
                if key == "_pdbx_database_status.recvd_initial_deposition_date":
                    save_entry[4] = value
            
            domain_added = False
            for result_list in entries_and_domains:
                if result_list[0] == best_chain_domain:
                    domain_added = True
                    result_list[1].append(save_entry)
                    break
            if not domain_added:
                entries_and_domains.append([best_chain_domain, [save_entry]])
    
    # print out results
    total = 0
    for result_list in entries_and_domains:
        print(result_list[0] + ": " + str(len(result_list[1])))
        total += len(result_list[1])
    print("total: " + str(total))
    
    # write excel
    workbook_path = join(os.getcwd(), "domains_and_infos_of_" + protein + '.xlsx')
    workbook = xlsxwriter.Workbook(workbook_path)
    print("wrote results to:")
    print(workbook_path)
    
    # write core results to excel
    counter = 0
    for result_list in entries_and_domains:
        if len(result_list[0]) >= 30:
            counter += 1
            worksheet = workbook.add_worksheet("multi-domain" + str(counter))
        else:
            worksheet = workbook.add_worksheet(result_list[0])
            
        worksheet.write(0, 0, result_list[0])
        worksheet.write(1, 0, "PDB")
        worksheet.write(1, 1, "resolution")
        worksheet.write(1, 2, "title")
        worksheet.set_column('C:C', 110)
        worksheet.write(1, 3, "method")
        worksheet.set_column('D:D', 20)
        worksheet.write(1, 4, "date")
        worksheet.set_column('E:E', 12)
        row = 2
        for entry in result_list[1]:
            for x in range(5):
                worksheet.write(row, x, entry[x])
            row += 1
    
    # write organism information to excel
    worksheet = workbook.add_worksheet("Organisms")
    worksheet.write(0, 0, "Lists all PDBs which contain sequences of a certain organism.")
    worksheet.write(1, 0, "Organism")
    worksheet.write(1, 1, "PDB")
    worksheet.set_column('A:A', 40)
    row = 2
    for entry in organisms:
        worksheet.write(row, 0, entry[0])
        for x in range(len(entry[1])):
            worksheet.write(row, 1, entry[1][x])
            row += 1
        row += 1
    
    workbook.close()

if __name__ == '__main__':
    # handle input arguments
    parser = argparse.ArgumentParser(description='Run weekly update.')
    parser.add_argument('-t', '--taxonomy', type=str, required=True, help="Give the taxonomy, either 'SARS-CoV' or 'SARS-CoV-2'")
    parser.add_argument('-p', '--protein', type=str, required=True, help="Give the protein folder name")
    args = parser.parse_args()
    
    main(args.taxonomy, args.protein)
