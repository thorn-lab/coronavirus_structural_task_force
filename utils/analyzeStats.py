import sqlite3
import matplotlib.pyplot as plt

conn = sqlite3.connect("stats.db")

c = conn.cursor()

outlist = open('mxList.txt', 'w') 
print('path, Rfree', file=outlist)


colors={'SARS-CoV':'blue', 'SARS-CoV-2':'red'}

plt.figure('fig1')
with conn:
    for row in c.execute('SELECT * FROM stats WHERE method=? ORDER BY protein, rfree',('X-RAY DIFFRACTION',)):
        if row[3] in colors.keys():
            plt.scatter(row[-2],row[-1], color=colors[row[3]])

#plt.show()
sars = []
covid19 = []


plt.figure('fig2')
with conn:
    for row in c.execute('SELECT * FROM stats WHERE method=?',('ELECTRON MICROSCOPY',)):
        if row[3] == 'SARS-CoV':
            sars.append(row[-3])
        elif row[3] == 'SARS-CoV-2':
            covid19.append(row[-3])
print(covid19)
print(sars)
plt.hist(covid19, color='red',  histtype='bar', stacked=False)
plt.hist(sars, color='blue',  histtype='bar', stacked=False)


plt.show()
