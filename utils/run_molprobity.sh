#!/bin/bash

#Script to run the missing phenix.striage validations
#runs if no xtriage log exist and structure has an mtz.
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
    if [ -f validation/molprobity/molprobity.out ] ; then
       echo "Nothing to do here"
    else
	if [ -f $c.mtz ] ; then
	    echo 'reflections here'
	    mkdir validation
	    mkdir validation/molprobity
	    phenix.molprobity $c.pdb
	    rm molprobity_probe.txt
	    mv molprobity* validation/molprobity/
	    phenix.clashscore $c.pdb
        fi
    fi

cd $base
done

cd ..
   
