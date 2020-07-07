import os
import glob
import shutil

_prefix = '/data/id30a3/inhouse/gianluca/'    
wc_folder = glob.glob(os.path.join(_prefix, 'coronavirus_structural_task_force/pdb/**/pdb-redo/wc/'),recursive=True)
dssp = glob.glob(os.path.join(_prefix, 'coronavirus_structural_task_force/pdb/**/pdb-redo/*.dssp'),recursive=True)
gz = glob.glob(os.path.join(_prefix, 'coronavirus_structural_task_force/pdb/**/pdb-redo/*.gz'),recursive=True)
bz2 = glob.glob(os.path.join(_prefix, 'coronavirus_structural_task_force/pdb/**/pdb-redo/*.bz2'),recursive=True)
finalpy = glob.glob(os.path.join(_prefix, 'coronavirus_structural_task_force/pdb/**/pdb-redo/*_final.py'),recursive=True)  
finalscm = glob.glob(os.path.join(_prefix, 'coronavirus_structural_task_force/pdb/**/pdb-redo/*_final.scm'),recursive=True)
finaltot = glob.glob(os.path.join(_prefix, 'coronavirus_structural_task_force/pdb/**/pdb-redo/*_final_tot.pdb'),recursive=True)
datatxt = glob.glob(os.path.join(_prefix, 'coronavirus_structural_task_force/pdb/**/pdb-redo/data.txt'),recursive=True)
html = glob.glob(os.path.join(_prefix, 'coronavirus_structural_task_force/pdb/**/pdb-redo/index.html'),recursive=True)
pdbejson = glob.glob(os.path.join(_prefix, 'coronavirus_structural_task_force/pdb/**/pdb-redo/pdbe.json'),recursive=True)
versions = glob.glob(os.path.join(_prefix, 'coronavirus_structural_task_force/pdb/**/pdb-redo/versions.txt'),recursive=True)
for _ in wc_folder:
    shutil.rmtree(_)
for _ in dssp:
    os.remove(_)
for _ in gz:
    os.remove(_)
for _ in bz2:
    os.remove(_)
for _ in finalpy:
    os.remove(_)
for _ in finalscm:
    os.remove(_)
for _ in finaltot:
    os.remove(_)
for _ in datatxt:
    os.remove(_)
for _ in html:
    os.remove(_)
for _ in pdbejson:
    os.remove(_)
for _ in versions:
    os.remove(_)

