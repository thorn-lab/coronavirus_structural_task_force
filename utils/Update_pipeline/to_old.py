import os
import requests
import datetime
import Doi

time = datetime.datetime.now()
time = time.strftime("%d")+"_"+time.strftime("%m")
'''
This script does this task:
<Takes a list of revised structures and replaces them in the repository with ne >
And was written in 2020 by Kristopher Nolte, Thorn Lab, University of Wuerzburg
as part of the Coronavirus Structural Taskforce, insidecorona.net
'''

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
    try: os.replace(dirpath+"/"+key+".{}".format(form), dirpath+"/old/"+key+"_{}.{}".format(time,form))
    except FileNotFoundError: pass

def main (pdb_id, repo_path):
    print("New DOIs for: ")
    for dirpath, dirnames, files in os.walk(repo_path):
        for key in pdb_id:
            if dirpath.endswith(key):
                #moves the old files in old
                to_old(key,dirpath, "cif")
                to_old(key, dirpath, "pdb")
                to_old(key, dirpath, "mtz")
                #downloads the new files
                get_mtz(key,dirpath)
                get_pdb(key, dirpath,"pdb")
                get_pdb(key, dirpath,"cif")
                #Doi.main(dirpath, key)
    print("{} have been revised".format(pdb_id))

#old1 = 22.04 and before
#old2 = 29.04
#old3 = 06.05
#old4 = 13.05
#old5 = 20.05
#old6 = 27.05
#old7 = 03.06
#old8 = 10-06
#old9 = 17.06