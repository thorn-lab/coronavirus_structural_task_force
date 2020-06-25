from Bio import SeqIO
import requests
import os
import collections
import datetime
import ID_getter
import to_old
import mk_Alignment_strc_vs_seq
import RMSD_pipeline
import organizer

'''
Fasta Files/*.fasta is the document with  fasta entrys
The folders are named after the protein_name and the taxo_names in the fasta. You have to rename them there if you want. You can see at line 64 how they are seperated
'''

time = datetime.datetime.now()
time = time.strftime("%d")+"_"+time.strftime("%m")

repo_path = "/Users/kristophernolte/Documents/ThornLab/coronavirus_structural_task_force/pdb"
dropbox_path = "/Users/kristophernolte/Dropbox (University of Wuerzburg)/insidecorona_thornlab/task_force/"
seq_fasta = list(SeqIO.parse("Fasta_Files/seq_SARS_2.fasta", "fasta"))

print("Starting the Wednesday-Update")
all_pdb_id = ID_getter.main()
pdb_id = all_pdb_id[0]
pdb_id_rev = all_pdb_id[1]

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
    doc = open(dropbox_path+"weekly_updates/new_structures_{}.txt".format(time), "w+")
    is_sorted = []
    id_dict = {}
    while i in range(len(seq_fasta)-10):
        blast = blast_search(i)
        protein_name = namer(i)[0]
        taxo_name = namer(i)[1]
        if blast != None:
            #compare blast search with taxonomy
            match = list(set(blast) & set(pdb_id))
            if len(match) != 0:
                #creating folders protein/taxonomy/id
                target = repo_path + os.sep + protein_name
                mk_dir(target)
                target += os.sep + taxo_name
                mk_dir(target)
                for element in match:
                    mk_dir(target+os.sep+element)
                    get_mtz(element,target)
                    get_pdb(element,target,"pdb")
                    get_pdb(element,target,"cif")
                is_sorted += match
                match = ' '.join(map(str, match))
                doc.write(seq_fasta[i].description+":\n"+"{}>".format(i+1)+match)
                id_dict[protein_name] = match.split(" ")
                doc.write("\n")
        i +=1
        print("{} %".format(int((i/len(seq_fasta)*100))))

    #IDs which were assigned more than once
    doc.write("Assigned twice or more: \n>{}\n".format([item for item, count in collections.Counter(is_sorted).items() if count > 1]))
    twice_assigned(pdb_id, id_dict)

    #IDs which could not be assigned
    not_assigned = set(pdb_id).difference(is_sorted)
    not_assigned= ' '.join(map(str, not_assigned))
    doc.write("Not assigned: \n>{}".format(not_assigned))
    doc.close()
    print("Added new structures, now updating Alignment")

    #Clean up the dict
    for x in id_dict.copy():
        if id_dict[x] == []: del id_dict[x]

    #Make the structure alignment for the new structures
    mk_Alignment_strc_vs_seq.main(id_dict, pdb_id)
    print("Alignment up to date, now updating RMSD")
    #Make RMSD
    RMSD_pipeline.main(id_dict)
    #Download not assigned
    organizer.main(not_assigned.split(" "), "not_assigned")


def twice_assigned (pdb_id, id_dict):
    #If id is twiced assigned it gets moved to the multi_protein folders
    #I am sure theres a smarter way for this but I am lazy
    def mover (key, proteins, folder):
        id_dict[folder].append(key)
        for prot in proteins:
            id_dict[prot].remove(key)
            try:
                try: os.replace(repo_path+"/{}/SARS-CoV-2/{}".format(prot, key),repo_path+"/{}/SARS-CoV-2/{}".format(folder, key))
                except OSError: pass
            except FileNotFoundError: pass

    for id in pdb_id:
        try:
            if id_dict["rna_polymerase"] != None:
                if id in id_dict["rna_polymerase"] and id in id_dict["nsp8"] and id in id_dict["nsp7"]:
                    id_dict["rna_polymerase-nsp7-nsp8"] = []
                    mover(id,["rna_polymerase","nsp8","nsp7"], "rna_polymerase-nsp7-nsp8")
        except KeyError: pass

        try:
            if id_dict["nsp8"] != None and id_dict["nsp7"]!= None:
                if id in id_dict["nsp8"] and id in id_dict["nsp7"]:
                        id_dict["nsp8-nsp7"] = []
                        mover(id,["nsp8","nsp7"], "nsp8-nsp7")
        except KeyError: pass

        try:
            if id_dict["nsp10"] != None and id_dict["methyltransferase"]!= None:
                if id in id_dict["methyltransferase"] and id in id_dict["nsp10"]:
                        id_dict["methyltransferase-nsp10"] = []
                        mover(id,["methyltransferase", "nsp10"] , "methyltransferase-nsp10")
        except KeyError: pass


main()
print("RMSD up to date, starting Revision")
to_old.main(pdb_id_rev, dropbox_path)
print("Done")