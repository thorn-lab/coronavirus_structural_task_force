import sqlite3


conn = sqlite3.connect("stats.db")

c = conn.cursor()

outlist = open('mxList.txt', 'w') 
print('path, Rfree', file=outlist)
with conn:
    for row in c.execute('SELECT * FROM stats WHERE method=? ORDER BY protein, rfree',('X-RAY DIFFRACTION',)):
        print(row[1],row[-1])
print('Done!')

