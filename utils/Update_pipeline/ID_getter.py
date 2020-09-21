import requests
from datetime import date, timedelta
import json
yesterday = date.today() - timedelta(days=1)
time = yesterday.strftime('%y-%m-%d')

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

def search(query):
    query = json.dumps(query)
    return_arr = []
    url = 'http://search.rcsb.org/rcsbsearch/v1/query'
    response = requests.post(url, data=query)
    if response.status_code == 200:
        result = response.json()
        for entry in result["result_set"]: return_arr.append(entry['identifier'][:4].lower())
    return return_arr

def main (repo_path):
    taxo_id = search(taxo_query)
    rev_id = search(rev_query)
    new_id = search(new_query)

    new_strc = list(set(taxo_id) & set(new_id))
    rev_strc = list(set(taxo_id) & set(rev_id))
    for x in list(set(rev_strc) & set(new_strc)): rev_strc.remove(x)

    ltxt = open(repo_path + "/list.txt", "a")
    for x in new_strc: ltxt.write("\n"+x)
    ltxt.close()

    print("new: ",new_strc)
    print("rev: ",rev_strc)
    return new_strc, rev_strc
