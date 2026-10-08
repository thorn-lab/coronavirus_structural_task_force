from prody import *
confProDy(verbosity='none')
import itertools
import numpy as np
import seaborn as sb
import matplotlib.pyplot as plt
import os
import string
import gemmi as gm
abc_lst = string.ascii_uppercase

def main (id_dict, path):
    #RMSD is not done for 3c_like_proteinase, surface_glycoprotein, nsp3
    #for protein in all_proteins:
    pdb_id = open(path + "/list.txt")
    pdb_id = pdb_id.read().split("\n")
    for protein in id_dict:
        #Here exceptions can be added, e.g. for proteins which have to many entries
        if protein == "surface_glycoprotein" or protein == "3c_like_proteinase" or protein == "nsp3":
            pass
        else:
            repo_path = path+"/"+protein
            file_walker(protein, pdb_id, repo_path+"/SARS-CoV-2/", "SARS-CoV-2")

def file_walker(protein, pdb_id, repo_path, taxo):
    protein_id = []
    for dirpath, dirnames, files in os.walk(repo_path):
        for key in pdb_id:
            if dirpath.endswith(key):
                protein_id.append(key)

    if len(protein_id) != 0:
        matrix_maker(protein, protein_id, repo_path, taxo)
    else: pass

def rmsdler (pdb1, pdb2, doc):
    """
        :param pdb1: Parsed pdb structure
        :param pdb2: Parsed pdb structure
        :param doc: .txt document
        :return: float: highest rmsd value, string: chain combination with best rmsd value, int: amount of atoms comapred in chains with highest rmsd
        """
    rmsd_lst, comb_lst, atom_lst = [], [], []
    # Get the combinations of all chains, each chain index has a respective alphabetic index
    # ToDo: Get the chain names directly from the pdb file
    combi_lst = abc_lst[:max(len(pdb1), len(pdb2))]
    iter_chain = np.asarray(list(itertools.combinations_with_replacement(combi_lst, 2)))

    for comb in iter_chain:
        print(comb)
        try:
            chain1 = pdb1[comb[0]].get_polymer()
            chain2 = pdb2[comb[1]].get_polymer()
            # ToDo: minimum chain lenght dependend on len(sequence)
            if len(chain1) > 5 and len(chain2) > 5:
                ptype = chain1.check_polymer_type()
                sup = gm.calculate_superposition(chain1, chain2, ptype, gm.SupSelect.CaP)
                rmsd = round(sup.rmsd, 3)

                atom_lst.append(sup.count)
                comb_lst.append(comb)
                rmsd_lst.append(rmsd)
                doc.write("Chain[{}] superposed to Chain[{}]: {} \n".format(comb[0], comb[1], str(rmsd)))
        except ValueError:
            pass
    if rmsd_lst != [] and comb_lst != [] and atom_lst != []:
        i = 0
        # goes through rmsd list returns the highest rmsd value for which more than 5 atoms were superposed
        # ToDo: change higher than 5 to 50% of len(depposited_sequence)
        while i in range(len(rmsd_lst)):
            best_rmsd = sorted(rmsd_lst)[i]
            index_of_best = rmsd_lst.index(best_rmsd)
            atomn_of_best = atom_lst[index_of_best]
            if atomn_of_best > 5:
                comb_of_best = comb_lst[index_of_best]
                return best_rmsd, comb_of_best, atomn_of_best
            i = i + 1

def matrix_maker (protein, pdb_id, repo_path, taxo):
    pdb_entrys = {}
    doc = open(repo_path + "heatmap_{}.txt".format(protein), "w+")
    #Parse all .pdb files
    for id in pdb_id:
        try:
            pdb_entrys[id] = gm.read_structure(repo_path + id + "/{}.pdb".format(id))[0]
        except RuntimeError:
            pass

    l = itertools.product(pdb_id, repeat=2)
    matrix = np.array(list(l))
    matrix = np.array_split(matrix, len(pdb_id))
    rmsd_matrix = np.full((len(pdb_id),len(pdb_id)),None)
    for i, row in enumerate(matrix):
        for j, element in enumerate(row):
            doc.write(element[0] + "-" + element[1] + " \n")
            try:
                pdb1 = pdb_entrys[element[0]]
                pdb2 = pdb_entrys[element[1]]
                rmsd_matrix[i][j] = rmsdler(pdb1, pdb2, doc)[0]
            except (OSError, KeyError):
                doc.write("OSError\n")
                rmsd_matrix[i][j] = None

    doc.close()
    heatmap(rmsd_matrix[:len(pdb_id) + 1], "viridis", pdb_id, protein, repo_path)

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


id_dict = {}
id_dict["endornase"] = []
import os.path as osp
main(id_dict, osp.abspath(osp.join(__file__ ,"../../..","pdb")))