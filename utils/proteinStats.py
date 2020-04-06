class pdbEntry:
    def __init__(self,
                 pdbid,
                 path,
                 method,
                 rfree):
        self.pdbid = pdbid
        self.path = path
        self.method = method
        #self.rwork = rwork
        self.rfree = rfree
        #self.resolution = resolution

    def __repr__(self):
        return ("Protein: ({},{},{})".format(self.pdbid, self.path, self.rfree))
    
    
