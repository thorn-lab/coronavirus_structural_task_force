import gemmi
import os
from Bio import SeqIO

'''
This script does this task:
<Compares the amino acid sequence of the strcuture with the reference sequence>
And was written in 2020 by Kristopher Nolte, Thorn Lab, University of Wuerzburg
as part of the Coronavirus Structural Taskforce, insidecorona.net
'''

def main (id_dict, pdb_id):
    for element in id_dict:
        file_walker(protein_chooser(element),pdb_id)

def protein_chooser (prot_name):
    #which protein should be compared
    path_repo = "/Users/kristophernolte/Documents/ThornLab/coronavirus_structural_task_force/pdb/{}".format(prot_name)
    return path_repo

def seq_finder (path_repo):
    #gets the sequence out of fasta
    seq_fasta = list(SeqIO.parse(path_repo+"/sequence_info.fasta", "fasta"))
    return seq_fasta

def structure_reader(pdb_path):
#reads the pdb-file and returns an alignable string
# reads the pdb-file and returns an alignable string
    try: pdb_data = gemmi.read_structure(pdb_path)[0]
    except RuntimeError: return ""
    i = 0
    seq = ""
    while True:
        try:
            temp = pdb_data[i].get_polymer()
            temp_list = ([res.name for res in temp])
            temp = [gemmi.find_tabulated_residue(res).one_letter_code for res in temp_list]
            temp = ''.join((code if code.isupper() else 'X') for code in temp)
            seq += temp

            i += 1
        except IndexError: return seq

def pdb_seq_reader(pdb_path):
#reads the pdb-file and returns an alignable string
    i = 0
    try: st = gemmi.read_pdb(pdb_path)
    except RuntimeError: return ""
    seq = list()
    while True:
        try:
            seq += st.entities[i].full_sequence
            i += 1
        except IndexError:
            seq = [gemmi.find_tabulated_residue(resname).one_letter_code for resname in seq]
            seq = ''.join((code if code.isupper() else 'X') for code in seq)
            return seq

def aligner (seq_1, seq_2, doc, model_seq):
#compares the strings
    scoring = gemmi.prepare_blosum62_scoring()
    result = gemmi.align_string_sequences(list(seq_1), list(seq_2), [], scoring)
    identity = result.calculate_identity()
    #if identity != "100.0" and  depo == False:
    doc.write("Identity: {}\n".format(round(identity,2)))
    doc.write("Score: {}\n".format(round(result.score), 2))
    doc.write("Alignment:\n{}\n".format(result.formatted(str(seq_1), str(seq_2))))

    if model_seq == True:
        i = 1
        mismatch = result.match_string
        gap_list = []
        mismatch_list = []
        while i < len(mismatch):
            if mismatch[i - 1] != "|":
                if mismatch[i-1] ==".": mismatch_list.append(i)
                else: gap_list.append(i)
            i += 1
        doc.write("Mismatch in {}\n".format(mismatch_list))
        doc.write("Unmodelled in {}\n\n".format(gap_list))

def file_walker (path_repo, pdb_id):
    taxo = "SARS-CoV-2"
    ncbi_seq = seq_finder(path_repo)
    doc = open(path_repo+"/{}/structure_sequence_alignment.txt".format(taxo), "a+")
    doc.write("This is the alignment of sequence in the pdb_file and the reference genome.\n"
                  "For the alignment the python tool gemmi [https://gemmi.readthedocs.io/en/latest/index.html] was used.\n"
                  "Scoring is done by a BLOSUM62 matrix\n")
    for dirpath, dirnames, files in os.walk(path_repo+"/"+taxo):
        for key in pdb_id:
            if dirpath.endswith(key):
                i = 1
                doc.write(">>>"+key+":\n")
                cif_path = dirpath + "/" + "{}.cif".format(key)
                pdb_path = dirpath + "/" + "{}.pdb".format(key)
                prot_seq = structure_reader(cif_path)
                seq_depo = pdb_seq_reader(pdb_path)

                while i in range(len(ncbi_seq)):
                    if taxo == "SARS-CoV-2":
                        seq_name = ncbi_seq[i].description.split(" ")[1]
                        doc.write(">Reference genome ({}) against deposited genome:\n".format(seq_name))
                        aligner(ncbi_seq[i].seq, seq_depo, doc, False)
                        doc.write(">Deposited genome against structure sequence:\n")
                        aligner(seq_depo, prot_seq, doc, True)
                        i += 2
    doc.close()

