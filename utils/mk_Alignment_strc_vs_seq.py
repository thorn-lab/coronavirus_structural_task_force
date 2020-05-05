import gemmi
import os
from Bio import SeqIO

'''
This script does this task:
<Compares the amino acid sequence of the strcuture with the reference sequence>
And was written in 2020 by Kristopher Nolte, Thorn Lab, University of Wuerzburg
as part of the Coronavirus Structural Taskforce, insidecorona.net
'''

#get a list of all IDs
f = open("/coronavirus_structural_task_force/pdb/list.txt")
pdb_id = f.read().split("\n")

def main ():
    all = ['hypothetical_protein_sars7a', 'nsp10', 'surface_glycoprotein', 'nsp8-nsp7', 'methyltransferase-nsp10', 'nsp3', 'rna_polymerase', 'nucleocapsid_protein', 'endornase', 'leader_protein', '3c_like_proteinase', 'rna_polymerase-nsp7-nsp8', 'exonuclease', 'nsp7', 'nsp9', 'helicase', 'protein_e']
    for element in all:
        file_walker(protein_chooser(element))

def protein_chooser (prot_name):
    #which protein should be compared
    path_repo = "/coronavirus_structural_task_force/pdb/{}".format(prot_name)
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
            return (seq)

def aligner (seq_p, seq_fasta, doc):
#compares the strings
    j = 50
    scoring = gemmi.AlignmentScoring()
    scoring.match = 5
    scoring.mismatch = -1
    scoring.gapo = -10
    scoring.gape = -1
    result = gemmi.align_string_sequences(list(seq_p), list(seq_fasta), [], scoring)
    doc.write("Identity: {}\n".format(round(result.calculate_identity(),2)))
    doc.write("Score: {}\n".format(round(result.score),2))
    doc.write("\nAlignment:\n{}\n".format(result.formatted(str(seq_p),str(seq_fasta))))

def file_walker (path_repo):
    taxo_list = ["SARS-CoV","SARS-CoV-2"]
    ncbi_seq = seq_finder(path_repo)
    for taxo in taxo_list:
        try:
            doc = open(path_repo+"/{}/structure_sequence_alignment.txt".format(taxo), "w+")
        except FileNotFoundError: pass
        doc.write("This is the alignment of sequence in the pdb_file and the reference genome.\n"
                  "For the alignment the python tool gemmi [https://gemmi.readthedocs.io/en/latest/index.html] was used.\n"
                  "Scoring is +5 for match, -1 for mismatch, -10 for gap opening, and -1 for each residue in the gap.\n\n")
        for dirpath, dirnames, files in os.walk(path_repo+"/"+taxo):
            for key in pdb_id[:-1]:
                if dirpath.endswith(key):
                    i = 0
                    doc.write(">>>"+key+":\n")
                    pdb_path = dirpath+"/"+"{}.pdb".format(key)
                    prot_seq = pdb_reader(pdb_path)
                    while i in range(len(ncbi_seq)):
                        if taxo == "SARS-CoV":
                            seq_name = ncbi_seq[i].description.split(" ")[1]
                            doc.write("Reference genome: {}\n".format(seq_name))
                            aligner(prot_seq, ncbi_seq[i].seq, doc)
                            i += 2
                        if taxo == "SARS-CoV-2":
                            seq_name = ncbi_seq[i].description.split(" ")[1]
                            doc.write("Reference genome: {}\n".format(seq_name))
                            aligner(prot_seq, ncbi_seq[i].seq, doc)
                            i += 2
    doc.close()

if __name__== '__main__':
    main()
