import requests
import json
import datetime
time = datetime.datetime.now()
time = str(time).split(" ")[0]
time = "2020-07-22"

taxo_query = {
    "query": {
    "type": "terminal",
    "service": "text",
    "parameters": {
      "attribute": "rcsb_entity_source_organism.taxonomy_lineage.name",
      "operator": "exact_match",
      "value": "Severe acute respiratory syndrome coronavirus 2"
    }
  },
    "request_options": {
        "return_all_hits": True
  },
    "return_type": "entry"
}

new_query = {
    "query": {
    "type": "terminal",
    "service": "text",
    "parameters": {
      "attribute": "rcsb_accession_info.initial_release_date",
      "operator": "greater",
      "value": "{}T00:00:00Z".format(time)
    }
  },
    "request_options": {
        "return_all_hits": True
  },
    "return_type": "entry"
}

rev_query = {
    "query": {
    "type": "terminal",
    "service": "text",
    "parameters": {
      "attribute": "rcsb_accession_info.revision_date",
      "operator": "greater",
      "value": "{}T00:00:00Z".format(time)
    }
  },
    "request_options": {
        "return_all_hits": True
  },
    "return_type": "entry"
}

seq_query = {
    "query": {
    "type": "terminal",
    "service": "sequence",
    "parameters": {
      "evalue_cutoff": 10,
      "target": "pdb_protein_sequence",
      "value": "SGFRKMAFPSGKVEGCMVQVTCGTTTLNGLWLDDVVYCPRHVICTSEDMLNPNYEDLLIRKSNHNFLVQAGNVQLRVIGHSMQNCVLKLKVDTANPKTPKYKFVRIQPGQTFSVLACYNGSPSGVYQCAMRPNFTIKGSFLNGSCGSVGFNIDYDCVSFCYMHHMELPTGVHAGTDLEGNFYGPFVDRQTAQAAGTDTTITVNVLAWLYAAVINGDRWFLNRFTTTLNDFNLVAMKYNYEPLTQDHVDILGPLSAQTGIAVLDMCASLKELLQNGMNGRTILGSALLEDEFTPFDVVRQCSGVTFQ"
    }
  },
    "request_options": {
        "return_all_hits": True
  },
    "return_type": "entry"
}

def search(query):
    query = json.dumps(query)
    return_arr = []
    url = 'http://search.rcsb.org/rcsbsearch/v1/query'
    response = requests.post(url, data=query)
    if response.status_code == 200:
        result = response.json()
        for entry in result["result_set"]: return_arr.append(entry['identifier'][:4].lower())
    return return_arr

print(search(seq_query))

