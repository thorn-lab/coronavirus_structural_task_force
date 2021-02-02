import itertools
import gemmi as gm
import numpy as np
import os.path as osp
import seaborn as sb
import matplotlib.pyplot as plt
import pandas as pd
import os

import string
abc_lst = string.ascii_uppercase
import prody as pry
pry.confProDy(verbosity='none')

def main (id_dict, path):
    #RMSD is not done for 3c_like_proteinase, surface_glycoprotein, nsp3
    #for protein in all_proteins:
    pdb_id = open(path + "/list.txt")
    pdb_id = pdb_id.read().split("\n")
    for protein in id_dict:
        #Here exceptions can be added, e.g. for proteins which have to many entries
        repo_path = path+"/"+protein
        file_walker(protein, pdb_id, repo_path+"/SARS-CoV-2/", "SARS-CoV-2")

def file_walker(protein, pdb_id, repo_path, taxo):
    protein_id = []
    for dirpath, dirnames, files in os.walk(repo_path):
        for key in pdb_id:
            if dirpath.endswith(key):
                protein_id.append(key)

    if len(protein_id) > 1:
        matrix_maker(protein, protein_id, repo_path)
    else: pass

def rmsdler (pdb1, pdb2, doc):
    rmsd_lst, comb_lst, atom_lst = [], [], []
    combi_lst = abc_lst[:max(len(pdb1),len(pdb2))]
    iter_chain = np.asarray(list(itertools.permutations(combi_lst,2)))
    for comb in iter_chain:
        try:
            chain1 = pdb1[comb[0]].get_polymer()
            chain2 = pdb2[comb[1]].get_polymer()
            ptype = chain1.check_polymer_type()
            sup = gm.calculate_superposition(chain1, chain2, ptype, gm.SupSelect.CaP)
            rmsd = round(sup.rmsd , 3)

            atom_lst.append(sup.count)
            comb_lst.append(comb)
            rmsd_lst.append(rmsd)
            doc.write("Chain[{}] superposed to Chain[{}]: {} \n".format(comb[0], comb[1],str(rmsd)))
        except ValueError: pass
    if rmsd_lst != [] and comb_lst != [] and atom_lst != []:
        return min(rmsd_lst),  comb_lst[rmsd_lst.index(min(rmsd_lst))], atom_lst[rmsd_lst.index(min(rmsd_lst))]

def matrix_maker (protein, pdb_id, repo_path):
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

    for i in range(len(id_arr["PDB-1"])):
        doc.write("\n>{}-{}<\n".format(str(id_arr["PDB-1"][i]),str(id_arr["PDB-2"][i])))
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

def heatmap (matrix, color, pdb_id, protein, repo_path):
    if len(pdb_id) > 1:
        harvest = np.array(matrix)
        harvest = np.where(harvest=="X", np.nan, harvest)
        harvest = harvest.astype(float)

        #CREATING HEATMAP
        fig, ax = plt.subplots()

        #colorbar
        if len(pdb_id) > 12:
            heat_map = sb.heatmap(harvest, cmap= color, annot=False, cbar=True, cbar_kws={'label': '[Å]', "orientation":"vertical"})
            plt.xticks(rotation=90)
        else:
            heat_map = sb.heatmap(harvest, cmap=color, annot=True, cbar=True, cbar_kws={'label': '[Å]', "orientation": "vertical"})
        #linewidth=0.5

        #Lenght of Label
        heat_map.set_xticks(np.arange(len(pdb_id))+0.5)
        heat_map.set_yticks(np.arange(len(pdb_id))+0.5)

        #Labels
        heat_map.set_xticklabels(pdb_id, rotation = 45)
        heat_map.set_yticklabels(pdb_id, rotation = 0)
        ax.set_title("{} overlap weighted RMSD".format(protein))

        #Show and Save
        plt.show()
        figure = heat_map.get_figure()
        figure.savefig(repo_path+'heatmap_{}.png'.format(protein), dpi=800)
        figure.savefig(repo_path+'heatmap_{}.pdf'.format(protein), dpi=800)

repo_path = osp.abspath(osp.join(__file__ ,"../../..","pdb"))
id_dict = {}
id_dict["endornase"] = []
id_dict["3c_like_proeinase"] = []
id_dict["exonuclease-nsp10"] = []
id_dict["helicase"] = []
id_dict["hypothetical_protein_sars7a"] = []
id_dict["leader_protein"] = []
id_dict["methyltransferase-nsp10"] = []
id_dict["nsp10"] = []
id_dict["nsp3"] = []
id_dict["nsp7"] = []
id_dict["nsp8-nsp7"] = []
id_dict["nsp8"] = []
id_dict["nsp9"] = []
id_dict["nucleocapsid_protein"] = []
id_dict["orf3a_protein"] = []
id_dict["orf8"] = []
id_dict["orf9b"] = []
id_dict["protein_e"] = []
id_dict["rna_polymerase-nsp7-nsp8"] = []
id_dict["rna_polymerase-nsp8"] = []
id_dict["rna"] = []
id_dict["helicase-rna_polymerase-nsp7-nsp8"] = []
id_dict["rna_polymerase"] = []
id_dict["surface_glycoprotein"] = []
main(id_dict, repo_path)