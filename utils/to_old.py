import os
import requests

'''
This script does this task:
<Takes a list of revised structures and replaces them in the repository with the new structures >
And was written in 2020 by Kristopher Nolte, Thorn Lab, University of Wuerzburg
as part of the Coronavirus Structural Taskforce, insidecorona.net
'''

path = '/coronavirus_structural_task_force/pdb'
data = []

#Here you can add the IDs which have to be replaced
pdb_id = ""
pdb_id = pdb_id.lower()
pdb_id = pdb_id.replace(" ", "")
pdb_id = pdb_id.split(",")
print(pdb_id)

def mk_dir(dir_path):
    #function to create new folders
    try:
        os.makedirs(dir_path)
    except FileExistsError:
        pass

def get_mtz (element, dirpath):
    #downloads the mtz data
    url = "http://edmaps.rcsb.org/coefficients/{}.mtz".format(element)
    r = requests.get(url)
    with open(dirpath+"/{}.mtz".format(element,element), 'wb') as f:
        f.write(r.content)

def get_pdb (element,dirpath,format):
    #downloads from pdb
    url = "https://files.rcsb.org/download/{}.{}".format(element,format)
    r = requests.get(url)
    with open(dirpath+"/{}.{}".format(element,format), 'wb') as f:
        f.write(r.content)

def to_old (key,dirpath,form):
    mk_dir(dirpath+"/old")
    try: os.replace(dirpath+"/"+key+".{}".format(form), dirpath+"/old/"+key+"_old2.{}".format(form))
    except FileNotFoundError: pass


for dirpath, dirnames, files in os.walk(path):
    for key in pdb_id:
        print(key)
        if dirpath.endswith(key):
            print(key)
            #moves the old files in old
            to_old(key,dirpath, "cif")
            to_old(key, dirpath, "pdb")
            to_old(key, dirpath, "mtz")
            #downloads the new files
            get_mtz(key,dirpath)
            get_pdb(key, dirpath,"pdb")
            get_pdb(key, dirpath,"cif")

print("Done")

