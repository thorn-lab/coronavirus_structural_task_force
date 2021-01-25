from prody import *
confProDy(verbosity='none')
import itertools
import numpy as np
import seaborn as sb
import matplotlib.pyplot as plt
import os

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
    try:
        t1_chA, t2_chA, seqid, overlap = matchChains(pdb1, pdb2)[0]
        t2_chA, transformation = superpose(t2_chA, t1_chA)
        # Calculate RMSD
        rmsd = calcRMSD(t1_chA, t2_chA)
        rmsd_weighted = round(rmsd / overlap * 100, 2)
        doc.write("RMSD: " + str(rmsd) + "\n")
        doc.write("seqid: {} \n".format(seqid))
        doc.write("overlap: {}\n".format(overlap))
        doc.write("weighted-RMSD: {}\n".format(rmsd_weighted))
        return rmsd_weighted
    except TypeError:
        doc.write("ProDy could not calculate a RMSD value\n")
        return None

def matrix_maker (protein, pdb_id, repo_path, taxo):
    pdb_entrys = {}
    doc = open(repo_path + "heatmap_{}.txt".format(protein), "w+")
    #Parse all .pdb files
    for iden in pdb_id:
        pdb_entrys[iden] = parsePDB(repo_path + iden + "/{}.pdb".format(iden))

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
                rmsd_matrix[i][j] = rmsdler(pdb1, pdb2, doc)
            except OSError:
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