import sqlite3
import os
import csv
from gemmi import cif
from math import *
import matplotlib.pyplot as plt

conn = sqlite3.connect("stats.db")

c = conn.cursor()

rfree = []
test = []
result = []
#get all mx structures
with conn:
    for row in c.execute('SELECT * FROM stats WHERE method=? ORDER BY protein, rfree',('X-RAY DIFFRACTION',)):
        rObs = row[-1]/row[-2]
        B = cif.read(row[1]+'/'+row[0]+".cif")
        block = B.sole_block()
        try:
            s = float(block.find_value('_exptl_crystal.density_percent_sol'))/100
            N = float(block.find_value('_reflns.number_obs'))
            Na= float(block.find_value('_refine_hist.number_atoms_total'))*1.5
            d = row[-4]
            Q = 0.025*1.5*d**3*(1-s)
            print(N, Na)
            T = sqrt((N+Na)/(N-Na))
            rExp = sqrt((1+Q)/(1-Q))
            print(row[0], rExp-rObs)
            rfree.append(d)
            test.append(T-rExp)
            result.append(rExp/rObs)
        except:
            print('oops')
    plt.figure()
    plt.xlabel('Resolution')
    plt.ylabel('Ratio expected - observed')
    #plt.scatter(rfree, result)
    plt.scatter(rfree, test)
    plt.show()
print('Done!')
