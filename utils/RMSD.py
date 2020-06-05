from prody import *
import itertools
import numpy as np
import seaborn as sb
import matplotlib.pyplot as plt
import os

def id_giver ():
    #RMSD is not done for nsp3, 3c_like_proteinase, surface_glycoprotein
    all_proteins = ['nsp10', 'nsp8-nsp7', 'methyltransferase-nsp10', 'rna_polymerase',
           'nucleocapsid_protein', 'endornase', 'leader_protein', 'rna_polymerase-nsp7-nsp8',
           'exonuclease', 'nsp7', 'nsp9', 'helicase', 'protein_e', 'hypothetical_protein_sars7a']

    test = ["nsp3"]

    path = "/Users/kristophernolte/Documents/ThornLab/coronavirus_structural_task_force/pdb/"
    #for protein in all_proteins:
    for protein in test:
        repo_path = path+protein
        pdb_id = open(path+"list.txt")
        pdb_id = pdb_id.read().split("\n")
        file_walker(protein, pdb_id, repo_path+"/SARS-CoV/", "1")
        #file_walker(protein, pdb_id, repo_path+"/SARS-CoV-2/", "2")

def file_walker(protein, pdb_id, repo_path, taxo):
    protein_id = []
    for dirpath, dirnames, files in os.walk(repo_path):
        for key in pdb_id:
            if dirpath.endswith(key):
                protein_id.append(key)

    if len(protein_id) != 0:
        matrix_maker(protein, protein_id, repo_path, taxo)
    else: pass

def matrix_maker (protein, pdb_id, repo_path, taxo):
    temp = pdb_id[0]
    doc = open(repo_path+"heatmap_{}.txt".format(protein), "w+")
    matrix = []
    liste = []
    pdb_entrys = {}
    #Parse all .pdb files
    for iden in pdb_id:
        pdb_entrys[iden] = parsePDB(repo_path + iden + "/{}.pdb".format(iden))

    for a, b in itertools.product(pdb_id, repeat = 2):
        # If a changes, a new row starts
        if a != temp:
            # All elements have the same lenght
            liste.extend((len(pdb_id) - len(liste) - 1) * "X")
            matrix.append(liste)
            liste = []

        try:
            #open PDBs
            pdb1 = pdb_entrys[a]
            pdb2 = pdb_entrys[b]
            #align structures
            try:
                #mobile, t1_chA, t2_chA, seqid, overlap = matchAlign(pdb1, pdb2)
                t1_chA, t2_chA, seqid, overlap = matchChains(pdb1, pdb2)[0]
                t2_chA, transformation = superpose(t2_chA, t1_chA)
                # Calculate RMSD
                rmsd = calcRMSD(t1_chA, t2_chA)
                # (RMSD/overlap*1/100)
                liste.append((round(rmsd / overlap * 100, 2)))
                temp = a
                # Write in .txt file
                doc.write(a + "-" + b + " \nRMSD: " + str(rmsd) + ("\n"))
                doc.write("seqid: {} \n".format(seqid))
                doc.write("overlap: {}\n".format(overlap))
                doc.write("weighted-RMSD: {}\n".format((round(rmsd / overlap * 100, 2))))

            except TypeError:
                temp = a
                doc.write(a + "-" + b + ": \n")
                doc.write("TYPE_ERROR\n")
                liste.append("X")

        except OSError:
            temp = a
            doc.write(a + "-" + b + ": \n")
            doc.write("OSError\n")
            liste.append("X")

    liste.extend((len(pdb_id) - len(liste) - 1) * "X")
    matrix.append(liste)
    doc.close()
    with open ("/Users/kristophernolte/Documents/Heatmap_arrays/{}_heatmap_CoV-{}.npy".format(protein,taxo), "wb") as f:
        np.save(f, matrix)
    heatmap(matrix[:len(pdb_id)+1], "viridis", pdb_id, protein, repo_path)

def heatmap (matrix, color, pdb_id, protein, repo_path):
    harvest = np.array(matrix)
    harvest = np.where(harvest=="X", np.nan, harvest)
    harvest = harvest.astype(float)

    #CREATING HEATMAP
    fig, ax = plt.subplots()

    #colorbar
    heat_map = sb.heatmap(harvest,  cmap= color, annot=True, cbar=True, cbar_kws={'label': '[Å]', "orientation":"vertical"})
    #linewidth=0.5

    #Lenght of Label
    heat_map.set_xticks(np.arange(len(pdb_id))+0,5)
    heat_map.set_yticks(np.arange(len(pdb_id))+0,5)

    #Labels
    heat_map.set_xticklabels(pdb_id, rotation = 0)
    heat_map.set_yticklabels(pdb_id, rotation = 0)
    ax.set_title("{} overlap weighted RMSD".format(protein))

    #Show and Save
    plt.show()
    figure = heat_map.get_figure()
    figure.savefig(repo_path+'heatmap_{}.png'.format(protein), dpi=800)

id_giver()
print("done")