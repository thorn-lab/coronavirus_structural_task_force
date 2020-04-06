import Bio.PDB as bio
import sqlite3
import os


conn = sqlite3.connect("stats.db")

c = conn.cursor()

c.execute("""CREATE TABLE stats (pdbid text, datapath text,
                                 protein text,
                                 virus text,
                                 method text, 
                                 resolution real, rwork real, rfree real)""")

conn.commit()


#function to walk the data structure and fill the database

def fillTheDB(workdir):
    for root, dirs, files in os.walk('../pdb'):
        if root.count(os.sep) == 3:
            for f in dirs:
                folder = os.path.join(root,f)
                l = root.split('/')
                with conn:
                    try:
                        mmcif_dict = bio.MMCIF2Dict.MMCIF2Dict(folder+'/'+f+'_original.cif')

                        # c.execute('INSERT INTO stats VALUES (?,?,?,?,?,?,?)', parsed_values)
                    except:
                        mmcif_dict = bio.MMCIF2Dict.MMCIF2Dict(folder+'/'+f+'.cif')
                    code = f
                    path = folder
                    virus = l[-1]
                    protein = l[-2]
                    method =  mmcif_dict['_exptl.method']
                    if method == 'X-RAY DIFFRACTION':
                        rfree = float(mmcif_dict['_refine.ls_R_factor_R_free'])
                        rwork = float(mmcif_dict['_refine.ls_R_factor_R_work'])
                        #fsc = mmcif_dict['_entry_for_fsc']
                        try:
                            resolution = float(mmcif_dict['_reflns.d_resolution_high'])
                        except:
                            resolution = None
                        
                    elif method =='ELECTRON MICROSCOPY':
                        rfree = None
                        rwork = None
                        #fsc = mmcif_dict['_entry_for_fsc']
                        resolution = mmcif_dict['_em_3d_reconstruction.resolution']
                    elif method == 'SOLUTION NMR':
                        rfree = None
                        rwork = None
                        #fsc = mmcif_dict['_entry_for_fsc']
                        resolution = None
                    parsed_values=(code, path, protein, virus , method, resolution , rwork, rfree)                    
                    c.execute('INSERT INTO stats VALUES(?,?,?,?,?,?,?,?)',parsed_values)
pwd = os.getcwd()
fillTheDB(pwd)

with conn:
    for row in c.execute('SELECT * FROM stats WHERE method = ELECTRON MICROSCOPY'):
        print(row)
        print('hi!')
print('Done!')



