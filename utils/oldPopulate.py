import sqlite3
import os
import csv
from gemmi import cif

conn = sqlite3.connect("stats.db")

c = conn.cursor()

c.execute("""CREATE TABLE stats (pdbid text, 
								datapath text,
                                 github text,
                                 protein text,
                                 virus text,
                                 method text, 
                                 hasRerefinement int,
                                 resolution real, 
                                 rmsd real,
                                 rwork real, 
                                 rfree real)""")

conn.commit()
url = 'https://github.com/thorn-lab/coronavirus_structural_task_force/tree/master'

#function to walk the data structure and fill the database

def fillTheDB(workdir):
    for root, dirs, files in os.walk('../pdb'):
        if root.count(os.sep) == 3:
            for f in dirs:
                folder = os.path.join(root,f)
                l = root.split('/')
                if os.path.exists(folder+'/isolde'):
                    hasRerefinement = 1
                else:
                    hasRerefinement = 0
                with conn:
                    try:
                        d = cif.read(folder+'/'+f+'.cif')
                        block = d.sole_block()
                    except:
                        break
                    code = f
                    github = url+folder[2:]
                    path = folder
                    virus = l[-1]
                    protein = l[-2]
                    b = block.find_values('_exptl.method')
                    method = b.str(0)
                    rfree = 0
                    rwork = 0
                    rmsd = 0
                    resolution = 0
                    if method == 'X-RAY DIFFRACTION':
                        rfree = float(block.find_value('_refine.ls_R_factor_R_free'))
                        rwork = float(block.find_value('_refine.ls_R_factor_R_work'))
                        rmsd = None
                        #fsc = mmcif_dict['_entry_for_fsc']
                        try:
                            resolution = float(block.find_value('_reflns.d_resolution_high'))
                        except:
                            resolution = None
                    elif method =='ELECTRON MICROSCOPY':
                        rfree = None
                        rwork = None
                        rmsd = None
                        #fsc = mmcif_dict['_entry_for_fsc']
                        resolution = block.find_value('_em_3d_reconstruction.resolution')
                    elif method == 'SOLUTION NMR':
                        rfree = None
                        rwork = None
                        rmsd = block.find_value('pdbx_nmr_ensemble_rms')
                        #fsc = mmcif_dict['_entry_for_fsc']
                        resolution = None
                    else:
                        print('something terribly wrong here')
                    parsed_values=(code, path, github, protein, virus , method, hasRerefinement, resolution , rmsd, rwork, rfree)                    
                    c.execute('INSERT INTO stats VALUES(?,?,?,?,?,?,?,?,?,?,?)',parsed_values)
pwd = os.getcwd()
print(pwd)
fillTheDB(pwd)



outlist = open('mxList.txt', 'w') 
print('path, Rfree', file=outlist)
with conn:
    for row in c.execute('SELECT * FROM stats WHERE method=? ORDER BY protein, rfree',('X-RAY DIFFRACTION',)):
        print(row[1],row[-1], file=outlist)
print('Done!')

emlist = open('emList.txt', 'w') 
print('path, resolution', file=emlist)
with conn:
    for row in c.execute('SELECT * FROM stats WHERE method=? ORDER BY protein, resolution',('ELECTRON MICROSCOPY',)):
        print(row[1],row[-4], file=emlist)
print('Done!')




# print('pdb, path, protein, virus , method, resolution ,rmsd rwork, rfree', file=full_db)

with open('stats.csv', 'w', newline='') as csvfile:
    full_db = csv.writer(csvfile, dialect='excel')
    full_db.writerow(['pdb', 'path','url', 'protein', 'virus' , 'method', 'resolution' ,'rmsd', 'rwork', 'rfree'])
    with conn:
        for row in c.execute('SELECT * FROM stats ORDER BY protein'):
            full_db.writerow(row)
print('Done!')
