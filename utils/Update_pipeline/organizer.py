import requests
import os

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

def main(repo_path, pdb_id, name):
    target = repo_path+os.sep+name
    mk_dir(target)
    for element in pdb_id:
        if len(element) == 4:
            mk_dir(target+os.sep+element)
            get_mtz(element,target)
            get_pdb(element,target,"pdb")
            get_pdb(element,target,"cif")
    print(pdb_id, "were not assigned, assign them manually. Files downloaded to {}".format(target))

