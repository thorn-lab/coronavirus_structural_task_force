#! /bin/bash

base=$(pwd)

while IFS= read -r line ; do 


cd  "$line" ; 
pwd ; 
pdbin=$(ls | grep pdb)
mtzin=$(ls | grep mtz)
pdb_redo.csh --local --xyzin=$pdbin --mtzin=$mtzin --nproc=7 --dirout=pdb-redo
echo $mtzin
cd $base  ; 

done < isolde_refinements.txt 


