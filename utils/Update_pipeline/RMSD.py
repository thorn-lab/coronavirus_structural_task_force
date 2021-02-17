import itertools
import gemmi as gm
import numpy as np
import pandas as pd
import os

import string
abc_lst = string.ascii_uppercase
import prody as pry
pry.confProDy(verbosity='none')

def main (id_dict, path):
    """
    :param id_dict: dict: keys contain the proteins which have to be analysed
    :param path: string: path to repo
    :return:
    """
    #get all ids out of list.txt
    pdb_id = open(path + "/list.txt")
    pdb_id = pdb_id.read().split("\n")
    for protein in id_dict:
        #Here exceptions can be added, e.g. for proteins which have to many entries
        repo_path = path+"/"+protein
        file_walker(protein, pdb_id, repo_path+"/SARS-CoV-2/")

def file_walker(protein, pdb_id, repo_path):
    """
    :param protein: string: name of protein
    :param pdb_id: list: all pdb ids in the repo
    :param repo_path: string:path to the repo
    """
    protein_id = []
    #get all ids of the given proteins out of the list(pdb_id)
    for dirpath, dirnames, files in os.walk(repo_path):
        for key in pdb_id:
            if dirpath.endswith(key):
                protein_id.append(key)

    if len(protein_id) > 1:
        matrix_maker(protein, protein_id, repo_path)
    else: pass

def rmsdler (pdb1, pdb2, doc):
    """
    :param pdb1: Parsed pdb structure
    :param pdb2: Parsed pdb structure
    :param doc: .txt document
    :return: float: highest rmsd value, string: chain combination with best rmsd value, int: amount of atoms comapred in chains with highest rmsd
    """
    rmsd_lst, comb_lst, atom_lst = [], [], []
    #Get the combinations of all chains, each chain index has a respective alphabetic index
    #ToDo: Get the chain names directly from the pdb file
    combi_lst = abc_lst[:max(len(pdb1),len(pdb2))]
    iter_chain = np.asarray(list(itertools.combinations_with_replacement(combi_lst,2)))

    for comb in iter_chain:
        print(comb)
        try:
            chain1 = pdb1[comb[0]].get_polymer()
            chain2 = pdb2[comb[1]].get_polymer()
            #ToDo: minimum chain lenght dependend on len(sequence)
            if len(chain1) > 5 and len(chain2) > 5:
                ptype = chain1.check_polymer_type()
                sup = gm.calculate_superposition(chain1, chain2, ptype, gm.SupSelect.CaP)
                rmsd = round(sup.rmsd , 3)

                atom_lst.append(sup.count)
                comb_lst.append(comb)
                rmsd_lst.append(rmsd)
                doc.write("Chain[{}] superposed to Chain[{}]: {} \n".format(comb[0], comb[1],str(rmsd)))
        except ValueError: pass
    if rmsd_lst != [] and comb_lst != [] and atom_lst != []:
        i = 0
        #goes through rmsd list returns the highest rmsd value for which more than 5 atoms were superposed
        #ToDo: change higher than 5 to 50% of len(depposited_sequence)
        while i in range(len(rmsd_lst)):
            best_rmsd = sorted(rmsd_lst)[i]
            index_of_best = rmsd_lst.index(best_rmsd)
            atomn_of_best = atom_lst[index_of_best]
            if atomn_of_best > 5:
                comb_of_best =  comb_lst[index_of_best]
                return best_rmsd, comb_of_best, atomn_of_best
            i = i + 1


def matrix_maker (protein, pdb_id, repo_path):
    """
    :param protein: string: name of protein
    :param pdb_id: list: all pdb-ids of the given protein
    :param repo_path: path to protein/taxo folder
    """
    doc = open(repo_path + "{}_RMSD_by_chain.txt".format(protein), "w+")
    doc.write("This document contains the RMSD of every combination of chains of this protein."
              "Only use this document if you what you are searching for."
              "Search by STRG-F each combinations is only named once so if you dont find 7krx-7kr1 you might want to search for 7kr1-7krx"
              "If you want to looking for the similarity of the proteins we recommend using <protein>_best_RMSD")

    pdb_entrys = {}
    #Parse every PDB entry in a dict
    for id in pdb_id:
        try: pdb_entrys[id] = gm.read_structure(repo_path + id + "/{}.pdb".format(id))[0]
        except RuntimeError: pass

    #create product of all id combinations
    iter_id= itertools.combinations(pdb_id, 2)
    iter_id = np.asarray(list(iter_id))

    #Transfer the combinations to a pandas DataFrame
    id_arr = pd.DataFrame(columns=["PDB-1", "Chain-1","PDB-2","Chain-2","RMSD", "Aligned atoms"])
    id_arr["PDB-1"] = iter_id[:,0]
    id_arr["PDB-2"] = iter_id[:,1]
    rmsd_lst, best_chain_lst, n_atom_lst = [], [], []

    #superpose each combination of pdb to calculate rmsd
    for i in range(len(id_arr["PDB-1"])):
        doc.write("\n>{}-{}<\n".format(str(id_arr["PDB-1"][i]),str(id_arr["PDB-2"][i])))
        print(id_arr["PDB-1"][i], id_arr["PDB-2"][i])
        try:
            result = rmsdler(pdb_entrys[id_arr["PDB-1"][i]],pdb_entrys[id_arr["PDB-2"][i]],doc)
            if result != None:
                rmsd_lst.append(result[0])
                best_chain_lst.append(result[1])
                n_atom_lst.append(result[2])
            else:
                rmsd_lst.append(None)
                best_chain_lst.append([None,None])
                n_atom_lst.append(None)
        except KeyError:
            rmsd_lst.append(None)
            best_chain_lst.append([None,None])
            n_atom_lst.append(None)

    #save values to DataFrame
    id_arr["RMSD"] = np.asarray(rmsd_lst)
    id_arr["Aligned atoms"] = np.asarray(n_atom_lst)
    id_arr["Chain-1"] = np.asarray(best_chain_lst)[:,0]
    id_arr["Chain-2"] = np.asarray(best_chain_lst)[:,1]

    #this duplicates the table invers so the iteration-type changes from combination to permutation without calculation
    inv_id_arr = pd.DataFrame(columns=["PDB-1","Chain-1","PDB-2","Chain-2","RMSD","Aligned atoms"])
    inv_id_arr["PDB-1"] = id_arr["PDB-2"]
    inv_id_arr["PDB-2"] = id_arr["PDB-1"]
    inv_id_arr["RMSD"] = id_arr["RMSD"]
    inv_id_arr["Aligned atoms"] = id_arr["Aligned atoms"]
    inv_id_arr["Chain-1"] = id_arr["Chain-2"]
    inv_id_arr["Chain-2"] = id_arr["Chain-1"]
    id_arr = id_arr.append(inv_id_arr)

    id_arr = id_arr.sort_values(by=['RMSD'])
    id_arr.to_excel("{}{}_best_RMSD.xlsx".format(repo_path, protein), index=False)
    doc.close()
