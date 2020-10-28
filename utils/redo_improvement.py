import os
import csv
from gemmi import cif
import matplotlib.pyplot as plt
import numpy as np

start = []
redos = []
for root, dirs, files in os.walk('../pdb'):
    if root.count(os.sep) == 3:
        for f in dirs:
            folder = os.path.join(root,f)
            try:
                d = cif.read(folder+'/'+f+'.cif')
                block = d.sole_block()
                redo = cif.read(folder+'/validation/pdb-redo/'+f+'_final.cif')
                redo_block=redo.sole_block()
            except:
                break
            b = block.find_values('_exptl.method')
            method = b.str(0)
            rfree = 0
            rwork = 0
            rmsd = 0
            resolution = 0
            try:
                rfree = float(block.find_value('_refine.ls_R_factor_R_free'))
                rredo = float(redo_block.find_value('_refine.ls_R_factor_R_free'))
            except:
                print('fail')
            start.append(rfree)
            redos.append(rredo)

better = 0
worse = 0

for a, b in zip(start, redos):
    if a < b:
        worse +=1
    else:
        better +=1
print('we have improved %s structures'%(better/len(start)))
x = np.linspace(0, 1,100)
y = x
plt.figure()
plt.scatter(start, redos, 'x')
plt.plot(x, y)
plt.show()
