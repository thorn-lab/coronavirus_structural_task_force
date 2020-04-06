import sqlite3


conn = sqlite3.connect("stats.db")

c = conn.cursor()

with conn:
    for row in c.execute('SELECT * FROM stats WHERE method=?',('ELECTRON MICROSCOPY',)):
        print(row)
        print('hi!')
print('Done!')

