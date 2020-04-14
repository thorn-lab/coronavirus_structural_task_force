from Bio import SeqIO
#Biopython: https://biopython.org/, pip install biopython
import requests
import os
import collections

'''
This script does this task:
<It will search for all compare all PDB entrys of a taxonomy with the protein sequences
in /FASTA Files and create a Repository of all PDB entrys which are alligned with the proteins sequences
and the taxonomy. Structure: protein_name/taxo_name/id. In each ID folder you will find a mtz, cif and pdb file>
And was written in 2020 by Kristopher Nolte, Thorn Lab, University of Wuerzburg
as part of the Coronavirus Structural Taskforce, insidecorona.net

Fasta Files/*.fasta is the document with  fasta entrys
The folders are named after the protein_name and the taxo_names in the fasta. You have to rename them there if you want. You can see at line 64 how they are seperated
'''

#where do you want to have your files downloaded:
root = "/CoV_Task_Force"

#reading the fasta
taxo = str(input("press 1 for SARS-CoV, press 2 for SARS-CoV2"))
if taxo == "1":
    seq_fasta = list(SeqIO.parse("Fasta Files/seq_SARS_1.fasta", "fasta"))
if taxo == "2":
    seq_fasta = list(SeqIO.parse("Fasta Files/seq_SARS_2.fasta", "fasta"))

def mk_dir(dir_path):
    #function to create new folders
    try:
        os.makedirs(dir_path)
    except FileExistsError:
        pass

def get_mtz (element, target):
    #downloads the mtz data
    url = "http://edmaps.rcsb.org/coefficients/{}.mtz".format(element)
    r = requests.get(url)
    with open(target+os.sep+"{}/{}.mtz".format(element,element), 'wb') as f:
        f.write(r.content)

def get_pdb (element,target,format):
    #downloads from pdb
    url = "https://files.rcsb.org/download/{}.{}".format(element,format)
    r = requests.get(url)
    with open(target+os.sep+"{}/{}.{}".format(element,element,format), 'wb') as f:
        f.write(r.content)

def org_search(taxo):
    #taxonomy search request
    if taxo == 1:
        taxo = "Severe acute respiratory syndrome coronavirus"
    if taxo == 2:
        taxo = "Severe acute respiratory syndrome coronavirus 2"
    elif __name__ == '__main__':
        url = 'http://www.rcsb.org/pdb/rest/search'
    org_query_text="""
<?xml version = "1.0" encoding = "UTF-8"?>
<orgPdbQuery>
<version> B0905 </version>
<queryType>org.pdb.query.simple.OrganismQuery</queryType>
<description></description>
<organismName>Severe acute respiratory syndrome coronavirus</organismName>
</orgPdbQuery>
"""
    header = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post(url, data=org_query_text, headers=header)
    if response.status_code == 200:
        temp = response.text.lower()
        temp = temp.split("\n")
        return temp[:-1]

def blast_search (i):
    #blast search request
    if __name__ == '__main__':
        url = 'http://www.rcsb.org/pdb/rest/search'
    blast_query_text = """
<?xml version="1.0" encoding="UTF-8"?>
<orgPdbQuery>
<queryType>org.pdb.query.simple.SequenceQuery</queryType>
<description></description>
<structureId></structureId>
<chainId></chainId>
<sequence>{}</sequence>
<eCutOff>10.0</eCutOff>
<searchTool>blast</searchTool>
<sequenceIdentityCutoff>30</sequenceIdentityCutoff>
</orgPdbQuery>
""".format(seq_fasta[i].seq)
    header = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post(url, data=blast_query_text, headers=header)
    if response.status_code == 200:
        temp = response.text
        temp = temp.lower()
        temp = temp.split("\n")
        for index, item in enumerate(temp): temp[index] = temp[index][0:4]
        #ignoring the chains
        return temp[:-1]
        #returns a list of pdb ids which mach the sequence

def namer (i):
    '''
    protein_name is the string between the seq.id and the brackets[]
    taxo_name is the string between the brackets[]
    '''
    protein_name = seq_fasta[i].description.split(" ", 1)
    protein_name = protein_name[1].split(" [", 1)[0]
    taxo_name = seq_fasta[i].description
    taxo_name = taxo_name[taxo_name.find("[") + 1:taxo_name.find("]")]
    return protein_name, taxo_name

def main():
    i = 0
    doc = open(root+"/matches_{}.txt".format(taxo), "w+")
    is_sorted = []
    pdb_id = org_search(taxo)
    while i in range(len(seq_fasta)):
        blast = blast_search(i)
        protein_name = namer(i)[0]
        taxo_name = namer(i)[1]
        if blast != None:
            #compare blast search with taxonomy
            match = list(set(blast) & set(pdb_id))
            if len(match) != 0:
                #creating folders protein/taxonomy/id
                target = root + os.sep + protein_name
                mk_dir(target)
                target += os.sep + taxo_name
                mk_dir(target)
                for element in match:
                    #creating a folder for the id an dowloading the relevant data
                    mk_dir(target+os.sep+element)
                    get_mtz(element,target)
                    get_pdb(element,target,"pdb")
                    get_pdb(element,target,"cif")
                is_sorted +=match
                match = ' '.join(map(str, match))
                doc.write(seq_fasta[i].description+":\n"+"{}>".format(i+1)+match)
                doc.write("\n")
        i +=1
        print("{} %".format(int((i/len(seq_fasta)*100))))

    #IDs which were assigned more than once
    doc.write("Assigned twice or more: \n>{}\n".format([item for item, count in collections.Counter(is_sorted).items() if count > 1]))

    #IDs which could not be assigned
    to_be_sorted = set(pdb_id).difference(is_sorted)
    to_be_sorted= ' '.join(map(str, to_be_sorted))
    doc.write("Not assigned: \n>{}".format(to_be_sorted))
    doc.close()

if __name__== '__main__':
    main()
