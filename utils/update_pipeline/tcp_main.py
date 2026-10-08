import requests
import json
import os
import gemmi
import shutil
import pandas as pd
from datetime import date, timedelta
from Bio import SeqIO

def get_time():
    offset = (date.today().weekday() - 2) % 7
    latest_update = date.today() - timedelta(days=offset)
    latest_update = "20" + latest_update.strftime('%y-%m-%d')
    return latest_update

def get_id(taxonomy_id, negate_taxonomy_id = "6645"):
    """
    requests all PDB of this taxonomy since the time given
    """
    # JSON queries
    new_query = {
        "query": {
            "type": "group",
            "logical_operator": "and",
            "nodes": [
                {
                    "type": "terminal",
                    "service": "text",
                    "parameters": {
                        "attribute": "rcsb_accession_info.initial_release_date",
                        "operator": "equals",
                        "value": "{}T00:00:00Z".format(time)
                    }
                },
                {
                    "type": "terminal",
                    "service": "text",
                    "parameters": {
                        "operator": "exact_match",
                        "negation": False,
                        "value": taxonomy_id,
                        "attribute": "rcsb_entity_source_organism.taxonomy_lineage.id"
                    }
                },
                {
                    "type": "terminal",
                    "service": "text",
                    "parameters": {
                        "operator": "exact_match",
                        "negation": True,
                        "value": negate_taxonomy_id,
                        "attribute": "rcsb_entity_source_organism.taxonomy_lineage.id"
                    }
                }
            ]
        },
        "request_options": {
            "return_all_hits": True
        },
        "return_type": "entry"
    }

    rev_query = {
        "query": {
            "type": "group",
            "logical_operator": "and",
            "nodes": [
                {
                    "type": "terminal",
                    "service": "text",
                    "parameters": {
                        "attribute": "rcsb_accession_info.revision_date",
                        "operator": "equals",
                        "value": "{}T00:00:00Z".format(time)
                    }
                },
                {
                    "type": "terminal",
                    "service": "text",
                    "parameters": {
                        "operator": "exact_match",
                        "negation": False,
                        "value": taxonomy_id,
                        "attribute": "rcsb_entity_source_organism.taxonomy_lineage.id"
                    }
                },
                {
                    "type": "terminal",
                    "service": "text",
                    "parameters": {
                        "operator": "exact_match",
                        "negation": True,
                        "value": negate_taxonomy_id,
                        "attribute": "rcsb_entity_source_organism.taxonomy_lineage.id"
                    }
                }
            ]
        },
        "request_options": {
            "return_all_hits": True
        },
        "return_type": "entry"
    }

    def do_request(query):
        """
        request PDB IDs through RCSB PDB Search API --> https://search.rcsb.org/#search-api
        :param query: JSON query to PDB API
        :return: list of PDB IDs
        """
        query = json.dumps(query)
        pdb_list = []
        url = 'https://search.rcsb.org/rcsbsearch/v2/query'
        response = requests.post(url, data=query)
        if response.status_code == 200:
            result = response.json()
            for entry in result["result_set"]: pdb_list.append(entry['identifier'][:4].lower())
        return pdb_list

    def clean_lists(new_pdb_lst, rev_pdb_lst):
        """
        removes duplicates
        :param new_pdb_lst: list of pdb ids from the new deposition query
        :param rev_pdb_lst: list of pdb ids from the revision query
        :return: list of newly deposited pdbs, list of revised pdb
        """
        for x in list(set(rev_pdb_lst) & set(new_pdb_lst)): rev_pdb_lst.remove(x)

        return new_pdb_lst, rev_pdb_lst

    # get PDB IDs from the PDB API
    new_pdb_lst = do_request(new_query)
    rev_pdb_lst = do_request(rev_query)

    # clean list
    c_new_pdb_lst, c_rev_pdb_lst = clean_lists(new_pdb_lst, rev_pdb_lst)
    return c_new_pdb_lst, c_rev_pdb_lst

def assign_protein(c_new_pdb_lst, taxo):
    """
    Assigns each ID all proteins which have a matching sequence and are in the fasta file
    """
    def get_name(prot_seq):
        '''
        assigns protein sequences names according to fasta/seq_taxo.fasta
        protein_name is the string between the ()
        '''
        prot_description = prot_seq.description
        protein_name = prot_description[prot_description.find("(") + 1:prot_description.find(")")]
        return protein_name

    def get_blast(prot_seq):
        """
        :param prot_seq: Bio.SeqRecord.SeqRecord
        requests a blast search from rcsb pdb.
        returns of list of IDs which belong to sequence
        """
        # blast search request
        seq_query = {
            "query": {
                "type": "terminal",
                "service": "sequence",
                "parameters": {
                    "evalue_cutoff": 10,
                    "target": "pdb_protein_sequence",
                    "value": "{}".format(prot_seq.seq)
                }
            },
            "request_options": {
                "return_all_hits": True
            },
            "return_type": "entry"
        }
        query = json.dumps(seq_query)
        blast_ids = []
        url = 'https://search.rcsb.org/rcsbsearch/v2/query'
        response = requests.post(url, data=query)

        if response.status_code == 200:
            result = response.json()
            for entry in result["result_set"]: blast_ids.append(entry['identifier'][:4].lower())
        return blast_ids

    def not_assigned (pdb_protein_dict):
        # compares c_new_pdb_lst and already assigned pdb_ids, marks non assigned as such
        keys_list = list(pdb_protein_dict.keys())
        not_assigned_ids = list(set(c_new_pdb_lst)-set(keys_list))
        for pdb_id in not_assigned_ids:
            pdb_protein_dict[pdb_id] = "not_assigned"
        return pdb_protein_dict

    fasta = list(SeqIO.parse("fasta/seq_{}.fasta".format(taxo), "fasta"))
    pdb_protein_dict = {}

    for prot_seq in fasta:
        # compares the sequence search with new pdb list
        prot_name = get_name(prot_seq)
        blast_ids = get_blast(prot_seq)
        match_list = list(set(blast_ids) & set(c_new_pdb_lst))

        for match in match_list:
            # saves protein assignment in dict
            pdb_protein_dict.setdefault(match,[])
            pdb_protein_dict[match].append(prot_name)

    for key in pdb_protein_dict:
        # converts array back to string
        # combines protein names alphabeticly if they are more than one
        if len(pdb_protein_dict[key]) > 1:
            pdb_protein_dict[key] = "-".join(sorted(pdb_protein_dict[key]))
        if len(pdb_protein_dict[key]) == 1:
            pdb_protein_dict[key] = pdb_protein_dict[key][0]

    #mark not assigned pdb_ids as such
    pdb_protein_dict = not_assigned(pdb_protein_dict)

    return pdb_protein_dict

def update_files(repo_path, taxo, pdb_protein_dict, c_rev_pdb_lst, df):
    """
    1. Downloads relevant files of new structures
    2. Archives revised structures, deletes superseded strcutures and reports this to the database
    """
    def mk_dir(path):
        # function to create new folders
        try: os.makedirs(path)
        except FileExistsError: pass

    def get_mtz(pdb_id, id_path):
        # downloads the mtz data
        url = "https://edmaps.rcsb.org/coefficients/{}.mtz".format(pdb_id)
        r = requests.get(url)
        print("download mtz: " + url)
        with open(id_path + os.sep +"{}.mtz".format(pdb_id, pdb_id), 'wb') as f:
            f.write(r.content)

    def get_pdb(pdb_id, id_path, format):
        # downloads from pdb
        url = "https://files.rcsb.org/download/{}.{}".format(pdb_id, format)
        r = requests.get(url)
        print("download pdb: " + url)
        with open(id_path + os.sep +"{}.{}".format(pdb_id, format), 'wb') as f:
            f.write(r.content)

    def to_old(pdb_id, id_path, form):
        # function to archive already revised files to archive
        df.loc[df["pdb_id"] == pdb_id, "last_revision"] = time
        df.loc[df["pdb_id"] == pdb_id, "version"] += 1
        old_path = os.path.join(id_path, "old")
        mk_dir(old_path)
        try:
            revision_path = os.path.join(id_path, pdb_id+".{}".format(form))
            archive_path = os.path.join(old_path, pdb_id+"_{}.{}".format(time,form))
            os.replace(revision_path, archive_path)
        except FileNotFoundError:
            pass

    def superseded_finder(pdb_id, id_path):
        # function to check if structure was superseded and if this is True the complete entry is deleted.
        pdb_path = os.path.join(id_path, pdb_id + ".pdb")
        try:
            with open(pdb_path) as f:
                for line in f:
                    if line.startswith("SPRSDE"):
                        sprs_id = line.split("     ")[2][1:].lower()
                        sprs_path = id_path[:-4] + "/" + sprs_id

                        df.loc[df["pdb_id"] == pdb_id, "superseded_by"] = sprs_id

                        shutil.rmtree(sprs_path)
        except FileNotFoundError:
            pass

    # get new files
    for pdb_id, protein_name in pdb_protein_dict.items():
        # create protein folder
        folder_path = os.path.join(repo_path, protein_name, taxo)
        mk_dir(folder_path)
        # create pdb_id folder
        id_path = os.path.join(repo_path, protein_name, taxo, pdb_id)
        mk_dir(id_path)
        print("id_path - ", id_path)
        # download relevant files
        get_mtz(pdb_id, id_path)
        get_pdb(pdb_id, id_path, "pdb")
        get_pdb(pdb_id, id_path, "cif")

    # revise files
    for pdb_id in c_rev_pdb_lst:
        # get path to entry
        try:
            print(df.loc[df["pdb_id"] == pdb_id]["path_in_repo"].item())
            if str(df.loc[df["pdb_id"] == pdb_id]["path_in_repo"].item()).find("SARS-CoV-1") > -1:
                # replace SARS-CoV-1 in path in database to SARS-CoV
                print("Contains SARS-CoV-1, automatic fix performed")
                old_path = df.loc[df["pdb_id"] == pdb_id]["path_in_repo"].item()
                new_path = old_path.replace("SARS-CoV-1", "SARS-CoV")
                df["path_in_repo"] = df["path_in_repo"].replace(old_path, new_path)
                
            id_path = os.path.join(repo_path[:repo_path.find("/pdb")], df.loc[df["pdb_id"] == pdb_id]["path_in_repo"].item())
            # moves the old files in old
            print("rev id_path - ", id_path)
            to_old(pdb_id, id_path, "cif")
            to_old(pdb_id, id_path, "pdb")
            to_old(pdb_id, id_path, "mtz")
            # download relevant files
            get_mtz(pdb_id, id_path)
            get_pdb(pdb_id, id_path, "pdb")
            get_pdb(pdb_id, id_path, "cif")
            # check if structure got superseded
            superseded_finder(pdb_id, id_path)
        except ValueError: print(pdb_id)

def new_to_database(repo_path, taxo, pdb_protein_dict, df):

    def get_meta(id_path):
        # reads cif file to get meta data
        cif = gemmi.read_structure(id_path)
        title = cif.info["_struct.title"]
        exp_method = cif.info["_exptl.method"]
        res = cif.resolution
        #ToDo add meta data
        return title, exp_method, res

    # update new structures
    for pdb_id, protein_name in pdb_protein_dict.items():
        id_path = os.path.join(repo_path,protein_name,taxo,pdb_id)
        try:
            title, exp_method, res = get_meta(os.path.join(id_path,pdb_id+".cif"))
            df = df.append({"pdb_id": pdb_id,
                            "protein": protein_name,
                            "release_date": time,
                            "last_revision": time,
                            "version": 1,
                            "title": title,
                            "exp_method": exp_method,
                            "resolution": res,
                            "path_in_repo":id_path[id_path.find("pdb"):]},
                            ignore_index=True)
        except ValueError:
            # file not downloaded properly, gemmi fails opening it
            pass

    return df

def give_txt_report(taxo, pdb_protein_dict,c_new_pdb_lst, c_rev_pdb_lst):
    """
    writes .txt file which summarizes the update
    """
    doc = open("weekly_reports/{}_update_report_{}.txt".format(time,taxo), "w+")
    doc.write("{} weekly report for {}\n".format(time, taxo))
    doc.write("##### {} revised structures #####\n".format(len(c_rev_pdb_lst)))
    doc.write(", ".join(c_rev_pdb_lst) + "\n\n")

    doc.write("##### {} new structures #####\n".format(len(c_new_pdb_lst)))
    doc.write(", ".join(c_new_pdb_lst) + "\n\n")

    doc.write("##### new structures by protein #####")
    # sort dict by proteins
    sorted_protein_dict = {k: v for k, v in sorted(pdb_protein_dict.items(), key=lambda item: item[1])}
    temp = ""
    for key, value in sorted_protein_dict.items():
        if value != temp: doc.write("\n"+value+"\n>")
        doc.write("{} ".format(key))
        temp = value

    doc.close()

def main(taxonomy_id, negate_taxonomy_id, taxo, rerun=False):
    repo_path = os.path.abspath(os.path.join(__file__ ,"../../..","pdb"))
    df = pd.read_pickle("main_repo_database_{}.pkl".format(taxo))

    global time
    if not rerun:
        time = get_time()

    # request pdb_id update report form pdb
    c_new_pdb_lst, c_rev_pdb_lst = get_id(taxonomy_id,negate_taxonomy_id)
    # get protein assignment for pdb ids through blast search
    pdb_protein_dict = assign_protein(c_new_pdb_lst, taxo)

    # download new and revised files
    update_files(repo_path, taxo, pdb_protein_dict, c_rev_pdb_lst, df)
    # add new pdb_ids to database
    df = new_to_database(repo_path, taxo, pdb_protein_dict, df)
    # create txt report of the update
    give_txt_report(taxo, pdb_protein_dict, c_new_pdb_lst, c_rev_pdb_lst)

    df.to_pickle("main_repo_database_{}.pkl".format(taxo))

    return c_new_pdb_lst, pd.unique(list(pdb_protein_dict.values()))

def rerun(taxonomy_id, negate_taxonomy_id, taxo):
    #This function can be used to start a repository beginning from var: time. time has to be set to a Wednesday (the day the pdb updates their entries)
    global time
    time = date(year=2021, month=3, day=17)
    while time < date.today():
        print(time)
        main(taxonomy_id, negate_taxonomy_id, taxo, True)
        time += timedelta(days=7)
