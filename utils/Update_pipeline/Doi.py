import datetime
time = datetime.datetime.now()
time = time.strftime("%d")+"_"+time.strftime("%m")

"""
Searches for _pdbx_related_exp_data_set.data_reference in cif files
"""
def main (dropbox_path, dirpath, key):
    f_all = open(dropbox_path+"weekly_updates/all_DOI.txt", "r+")
    f_all = f_all.readlines()
    for line in f_all:
        if line[:4] == key: return

    f = open(dirpath+"/{}.{}".format(key,"cif"), "r")
    f = f.readlines()
    doi_txt = open(dropbox_path+"weekly_updates/new_DOI_{}.txt".format(time), "w+")
    for line in f:
        if line.startswith("_pdbx_related_exp_data_set.data_reference"):
            doi_txt = open(dropbox_path+"weekly_updates/new_DOI_{}.txt".format(time), "a+")
            doi_txt.write(">"+key+": "+line+"\n")
            all_doi_txt = open(dropbox_path+"weekly_updates/all_DOI.txt", "a+")
            all_doi_txt.write(key+"\n")
            all_doi_txt.close()

    doi_txt.close()

