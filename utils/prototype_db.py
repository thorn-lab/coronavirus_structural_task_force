import csv
import os
import sqlite3
from gemmi import cif
import json

conn = sqlite3.connect("stats.db")

c = conn.cursor()

#c.execute("""CREATE TABLE stats (pdbid text,
#								datapath text,
 #                                github text,
  #                               protein text,
   #                              virus text,
    #                             method text,
     #                            hasRerefinement int,
      #                           resolution real,
         #                        rmsd real,
       #                          rwork real,
        #                         rfree real)""")

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
                    EM_values=(code, resolution)
                    general_values=(code, method, path, github, protein, virus, hasRerefinement)
                    MX_values=(code, rfree, resolution, rwork)
                    NML_values=(code, rmsd)
                    c.execute('INSERT INTO stats VALUES(?,?,?,?,?,?,?,?,?,?,?)',parsed_values)
                    c.execute('INSERT INTO EM VALUES(?,?)',EM_values) # Descriptions ?
                    c.execute('INSERT INTO General VALUES(?,?,?,?,?,?,?)',general_values)
                    c.execute('INSERT INTO MX VALUES(?,?,?,?)',MX_values)
                    c.execute('INSERT INTO stats VALUES(?,?)',NML_values)
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
    reader = csv.DictReader(csvfile)
    with conn:
        for row in c.execute('SELECT * FROM stats ORDER BY protein'):
            full_db.writerow(row)
print('Done!')

with open('EM.csv', 'w', newline='') as csvfile:
    full_db = csv.writer(csvfile, dialect='excel')
    full_db.writerow(['pdb', 'resolution'])
    with conn:
        for row in c.execute('SELECT * FROM EM ORDER BY resolution'):
            full_db.writerow(row)
print('Done!')

with open('General.csv', 'w', newline='') as csvfile:
    full_db = csv.writer(csvfile, dialect='excel')
    full_db.writerow(['pdb','description', 'method', 'datapath', 'github', 'protein', 'virus', 'hasRerefinement', 'Molprobity_score'])
    with conn:
        for row in c.execute('SELECT * FROM General ORDER BY method'):
            full_db.writerow(row)
print('Done!')

with open('MX.csv', 'w', newline='') as csvfile:
    full_db = csv.writer(csvfile, dialect='excel')
    full_db.writerow(['pdb', 'rfree', 'rwork', 'resolution'])
    with conn:
        for row in c.execute('SELECT * FROM MX ORDER BY resolution'):
            full_db.writerow(row)
print('Done!')

with open('NML.csv', 'w', newline='') as csvfile:
    full_db = csv.writer(csvfile, dialect='excel')
    full_db.writerow(['pdb', 'rmsd'])
    with conn:
        for row in c.execute('SELECT * FROM NML ORDER BY rmsd'):
            full_db.writerow(row)
print('Done!')
