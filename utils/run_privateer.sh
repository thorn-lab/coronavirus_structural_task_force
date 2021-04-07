#!/bin/bash
#Script to run the privateer validations
#Please, run this from the utils folder
#x is the full path to the folder
#c is the pdb code
#e is the entry in lower case (for pdb_redo)

cd ../pdb

base=$(pwd)


for x in */*/* ;
do
    c=`basename $x`;
    echo $x
    e="${c,,}" ;
    cd $x ;
    if [ -f validation/privateer/privateer-results.py ] ; then
       echo 'nothing to do here!'
    else
    if [ -f $c.mtz ]; then
      echo 'reflections here'
      mkdir validation/privateer
      cd validation/privateer
      Privateer -pdbin ../../$c.pdb -mtzin ../../$c.mtz
     fi
    fi
cd $base
done

cd ..
   
