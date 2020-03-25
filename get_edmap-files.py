import requests
"""
Insert PDB-ID in Data as 1 String in data (Exp.: 3WU2,6Y7M,...) call function at line 39 or 40 !
--> downloads the the requested files from edmaps.
"""

data = ""
data = data.lower()
data = data.split(",")
print(data)

def Get_dsn6 ():
    for element in data:
        url = "http://edmaps.rcsb.org/dsn6/{}/{}/{}_2fo.dsn6.gz".format(element[2:4],element,element)
        url = url.replace(" ","")
        r = requests.get(url)
        with open("dsn6_{}.gz".format(element), 'wb') as f:
            f.write(r.content)

def Get_mtz (data):
    for element in data:
        url = "http://edmaps.rcsb.org/coefficients/{}.mtz".format(element)
        url = url.replace(" ","")
        print(url)
        r = requests.get(url)
        with open("mtz_{}.mtz".format(element), 'wb') as f:
            f.write(r.content)

#Get_mtz(data)
#Get_dsn6(data)