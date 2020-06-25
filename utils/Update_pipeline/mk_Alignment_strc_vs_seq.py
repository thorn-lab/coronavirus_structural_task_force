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

def pdb_reader(pdb_path):
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

def aligner (seq_p, seq_fasta, doc):
#compares the strings
    scoring = gemmi.prepare_blosum62_scoring()
    result = gemmi.align_string_sequences(list(seq_fasta), list(seq_p), [], scoring)
    doc.write("Identity: {}\n".format(round(result.calculate_identity(), 2)))
    doc.write("Score: {}\n".format(round(result.score), 2))
    doc.write("Alignment:\n{}\n".format(result.formatted(str(seq_fasta), str(seq_p))))

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
                pdb_path = dirpath+"/"+"{}.pdb".format(key)
                prot_seq = pdb_reader(pdb_path)
                while i in range(len(ncbi_seq)):
                    if taxo == "SARS-CoV-2":
                        seq_name = ncbi_seq[i].description.split(" ")[1]
                        doc.write("Reference genome: {}\n".format(seq_name))
                        aligner(prot_seq, ncbi_seq[i].seq, doc)
                        i += 2
    doc.close()

