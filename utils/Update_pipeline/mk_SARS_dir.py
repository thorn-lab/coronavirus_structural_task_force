from Bio import SeqIO
import requests
import os
import shutil
import collections
import datetime
import ID_getter
import to_old
import mk_Alignment_strc_vs_seq
import RMSD
import organizer
import json
import os.path as osp

'''
Fasta Files/*.fasta is the document with  fasta entrys
The folders are named after the protein_name and the taxo_names in the fasta. You have to rename them there if you want. You can see at line 64 how they are seperated
'''

time = datetime.datetime.now()
time = "20"+time.strftime("%y-%m-%d")
repo_path = osp.abspath(osp.join(__file__ ,"../../..","pdb"))

seq_fasta = list(SeqIO.parse("Fasta_files/seq_SARS_2.fasta", "fasta"))

print("Starting the Wednesday-Update")
all_pdb_id = ID_getter.main(repo_path)
pdb_id = all_pdb_id[0]
pdb_id_rev = all_pdb_id[1]

def mk_dir(dir_path):
    #function to create new folders
    try:
        os.makedirs(dir_path)
    except FileExistsError:
        pass

def get_mtz (element, target):
    print("downloading mtz {}".format(str(element)))
    #downloads the mtz data
    url = "http://edmaps.rcsb.org/coefficients/{}.mtz".format(element)
    r = requests.get(url)
    with open(target+os.sep+"{}/{}.mtz".format(element,element), 'wb') as f:
        f.write(r.content)

def get_pdb (element,target,format):
    print("downloading pdb/cif {}".format(str(element)))
    #downloads from pdb
    url = "https://files.rcsb.org/download/{}.{}".format(element,format)
    r = requests.get(url)
    with open(target+os.sep+"{}/{}.{}".format(element,element,format), 'wb') as f:
        f.write(r.content)

def blast_search (i):
    #blast search request
    if __name__ == '__main__':
        url = 'http://www.rcsb.org/pdb/rest/search'
    seq_query = {
        "query": {
            "type": "terminal",
            "service": "sequence",
            "parameters": {
                "evalue_cutoff": 10,
                "target": "pdb_protein_sequence",
                "value": "{}".format(seq_fasta[i].seq)
            }
        },
        "request_options": {
            "return_all_hits": True
        },
        "return_type": "entry"
    }
    query = json.dumps(seq_query)
    return_arr = []
    url = 'http://search.rcsb.org/rcsbsearch/v1/query'
    response = requests.post(url, data=query)
    if response.status_code == 200:
        result = response.json()
        for entry in result["result_set"]: return_arr.append(entry['identifier'][:4].lower())
    return return_arr

def namer (i):
    '''
    protein_name is the string between the seq.id and the brackets []
    taxo_name is the string between the brackets []
    '''
    protein_name = seq_fasta[i].description.split(" ", 1)
    protein_name = protein_name[1].split(" [", 1)[0]
    taxo_name = seq_fasta[i].description
    taxo_name = taxo_name[taxo_name.find("[") + 1:taxo_name.find("]")]
    return protein_name, taxo_name

def main():
    i = 0
    #create a protocol .txt file
    doc = open("weekly_reports/new_structures_{}.txt".format(time), "w+")
    doc.write("{} revised structures: \n".format(len(pdb_id_rev)))
    doc.write("{}\n".format(", ".join(pdb_id_rev)))
    doc.write("{} new structures: \n".format(len(pdb_id)))
    is_sorted = []
    id_dict = {}
    while i in range(len(seq_fasta)):
        blast = blast_search(i)
        #get the names of the protein
        protein_name = namer(i)[0]
        #get the taxonomy of the protein
        taxo_name = namer(i)[1]
        if blast != None:
            # compare blast search with taxonomy
            match = list(set(blast) & set(pdb_id))
            if len(match) != 0:
                # creating folders protein/taxonomy/id
                target = repo_path + os.sep + protein_name
                mk_dir(target)
                target += os.sep + taxo_name
                mk_dir(target)
                for element in match:
                    mk_dir(target+os.sep+element)
                    # downloading files
                    get_mtz(element,target)
                    get_pdb(element,target,"pdb")
                    get_pdb(element,target,"cif")
                is_sorted += match
                match = ' '.join(map(str, match))
                doc.write(protein_name+":\n"+">"+match)
                id_dict[protein_name] = match.split(" ")
                doc.write("\n")
        i += 1
        print("{} %".format(int((i/len(seq_fasta)*100))))

    #IDs which were assigned more than once
    multi_ids = [item for item, count in collections.Counter(is_sorted).items() if count > 1]
    doc.write("Assigned twice or more: \n>{}\n".format(multi_ids))
    twice_assigned(id_dict, multi_ids)

    #IDs which could not be assigned
    not_assigned = set(pdb_id).difference(is_sorted)
    not_assigned = ' '.join(map(str, not_assigned))
    doc.write("Not assigned: \n>{}".format(not_assigned))
    doc.close()
    organizer.main(repo_path, not_assigned.split(" "), "not_assigned")
    print("Added new structures, now updating Alignment")

    #Clean up the dict, only keep dict keys which have entries
    for x in id_dict.copy():
        if id_dict[x] == []: del id_dict[x]

    #Make the structure alignment for the new structures
    mk_Alignment_strc_vs_seq.main(id_dict, pdb_id, repo_path)
    print("Alignment up to date, now updating RMSD")
    #Make RMSD
    RMSD.main(id_dict, repo_path)
    #Download not assigned



def twice_assigned (id_dict, multi_assign_ids):
    def mover (id, proteins, folder):
        for prot in proteins:
            try:
                shutil.copytree(repo_path+"/{}/SARS-CoV-2/{}".format(prot, id),repo_path+"/{}/SARS-CoV-2/{}".format(folder, id))
            except OSError: print("OS_Error")
            shutil.rmtree(repo_path+"/{}/SARS-CoV-2/{}".format(prot, id))

    def get_key(val):
        #gets the protein which saved the combined ids and deletes their dict entry
        multi_ids_prot = []
        for key, value in id_dict.items():
            print(key, val)
            if val in value:
                multi_ids_prot.append(key)
                value.remove(val)
                id_dict[key] = value
        return multi_ids_prot

    for id in multi_assign_ids:
        multi_ids_prot = get_key(id)
        #name of combined protein folder
        multi_prot_folder = "-".join(multi_ids_prot)
        #create new dict with combined proteins
        try: id_dict[multi_prot_folder] = id_dict[multi_prot_folder].append(id)
        except KeyError: id_dict[multi_prot_folder] = []
        mover(id, multi_ids_prot, multi_prot_folder)

main()
to_old.main(pdb_id_rev, repo_path)
print("Done")
