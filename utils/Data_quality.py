import sqlite3
import os
import csv
from gemmi import cif

conn = sqlite3.connect(":memory:")

c = conn.cursor()

c.execute("""CREATE TABLE stats (pdbid text, 
                                 datapath text,
                                 protein text,
                                 virus text,
                                 method text, 
                                 hasRerefinement real,
                                 highRes real,
                                 lowRes real, 
                                 rmsd real,
                                 rwork real, 
                                 rfree real,
                                 rmerge real,
                                 sigmaI real,
                                 sigmaF real,
                                 redundancy real,
                                  completeness real)""")

conn.commit()
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
                    path = folder
                    virus = l[-1]
                    protein = l[-2]
                    b = block.find_values('_exptl.method')
                    method = b.str(0)
                    rfree = 0
                    rwork = 0
                    rmsd = 0
                    resolution = 0
                    lowres = 0
                    rmerge = 0
                    sigmaI = 0
                    sigmaF = 0
                    redundancy = 0
                    if method == 'X-RAY DIFFRACTION':
                        rfree = float(block.find_value('_refine.ls_R_factor_R_free'))
                        rwork = float(block.find_value('_refine.ls_R_factor_R_work'))
                        rmsd = None
                        #fsc = mmcif_dict['_entry_for_fsc']
                        try:
                            resolution = float(block.find_value('_reflns.d_resolution_high'))
                        except:
                            resolution = None
                        try:
                            lowres = float(block.find_value('_reflns.d_resolution_low'))
                        except:
                            lowres = None                        
                        try:
                            rmerge = float(block.find_value('_reflns.pdbx_Rmerge_I_obs'))
                        except:
                            rmerge = None 
                        try:
                            sigmaF = float(block.find_value('_reflns.observed_criterion_sigma_F'))
                        except:
                            sigmaF = None
                        try:
                            sigmaI = float(block.find_value('_reflns.observed_criterion_sigma_I'))
                        except:
                            sigmaI = None
                        try:
                            redundancy = float(block.find_value('_reflns.pdbx_redundancy'))
                        except:
                            redundancy = None
                        try:
                            completeness = float(block.find_value('_reflns.percent_possible_obs'))
                        except:
                            completeness = None

                         
                    parsed_values=(code, path, protein, virus , method, hasRerefinement, resolution , lowres, rmsd, rwork, rfree, rmerge, sigmaI, sigmaF, redundancy, completeness)                    
                    c.execute('INSERT INTO stats VALUES(?,?,?,?,?,?,?,?,?,?, ?,?,?,?, ?,?)',parsed_values)
pwd = os.getcwd()
print(pwd)
fillTheDB(pwd)





with open('mxStats.csv', 'w', newline='') as csvfile:
    full_db = csv.writer(csvfile, dialect='excel')
    full_db.writerow(['pdb', 'path', 'protein', 'virus' , 'method','rerefinement', 'highRes', 'lowRes' ,'rmsd', 'rwork', 'rfree', 'rmerge', 'sigmaI', 'sigmaF', 'redundancy','completeness'])
    with conn:
        for row in c.execute('SELECT * FROM stats WHERE method=? ORDER BY protein, rfree',('X-RAY DIFFRACTION',)):
            full_db.writerow(row)
print('Done!')
