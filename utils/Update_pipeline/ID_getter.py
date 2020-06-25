import requests
import datetime
time = datetime.datetime.now()
time = str(time).split(" ")[0]

repo_path="/Users/kristophernolte/Documents/ThornLab/coronavirus_structural_task_force/pdb/"

taxo_query = """
<?xml version = "1.0" encoding = "UTF-8"?>
<orgPdbQuery>
<version> B0905 </version>
<queryType>org.pdb.query.simple.OrganismQuery</queryType>
<description></description>
<organismName>Severe acute respiratory syndrome coronavirus 2</organismName>
</orgPdbQuery>"""

rev_query = """<orgPdbQuery>
<queryType>org.pdb.query.simple.ReviseDateQuery</queryType>
<pdbx_audit_revision_history.revision_date.comparator>between</pdbx_audit_revision_history.revision_date.comparator>
<pdbx_audit_revision_history.revision_date.min>{}</pdbx_audit_revision_history.revision_date.min>
<pdbx_audit_revision_history.ordinal.value>1</pdbx_audit_revision_history.ordinal.value>
</orgPdbQuery>""".format(time)

new_query = """<orgPdbQuery>
<queryType>org.pdb.query.simple.ReleaseDateQuery</queryType>
<pdbx_audit_revision_history.revision_date.comparator>between</pdbx_audit_revision_history.revision_date.comparator>
<pdbx_audit_revision_history.revision_date.min>{}</pdbx_audit_revision_history.revision_date.min>
<pdbx_audit_revision_history.ordinal.value>1</pdbx_audit_revision_history.ordinal.value>
</orgPdbQuery>""".format(time)

def search(query):
    url = 'http://www.rcsb.org/pdb/rest/search'
    header = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post(url, data=query, headers=header)
    if response.status_code == 200:
        temp = response.text.lower()
        temp = temp.split("\n")
        return temp[:-1]

def main ():
    taxo_id = search(taxo_query)
    rev_id = search(rev_query)
    new_id = search(new_query)

    new_strc = list(set(taxo_id) & set(new_id))
    rev_strc = list(set(taxo_id) & set(rev_id))
    for x in list(set(rev_strc) & set(new_strc)): rev_strc.remove(x)
    print(new_strc)
    print(rev_strc)

    ltxt = open(repo_path + "list.txt", "a")
    for x in new_strc: ltxt.write("\n"+x)
    ltxt.close()

    return new_strc, rev_strc

main()