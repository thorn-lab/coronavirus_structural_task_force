#!/bin/bash

code=6y2e
nummer=1

pdbin=${code}_${nummer}.pdb
hklin=${code}_${nummer}.mtz
#hklin=../${code}_original.mtz
pdbout=${code}_${nummer}_out.pdb
hklout=${code}_${nummer}_out.mtz

refmac5 HKLIN $hklin XYZIN $pdbin HKLOUT $hklout XYZOUT $pdbout << eof
make hydrogen ALL hout NO peptide NO cispeptide YES           ssbridge YES   connectivity YES link NO
make newligand continue
refi type REST resi MLKF meth CGMAT bref ISOT
refi tlsc 10
tlsd waters exclude
ncyc 100
scal type SIMP lssc function a sigma n
solvent YES
solvent vdwprobe 1.1 ionprobe 0.9 rshrink 0.9
weight  MATRIX 0.07
monitor MEDIUM torsion 10.0 distance 10.0 angle 10.0 plane 10.0 chiral 10.0  bfactor 10.0 bsphere  10.0 rbond 10.0 ncsr  10.0
temp 0.50
blim 2.0 999.0
end
eof
