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
    if [ -f validation/molprobity/molprobity.out ] && [ -f validation/molprobity/clashscore.txt ] ; then
    	echo "Done ${c}"
    	cd $base
    	continue
    else
    	if [ ! -f validation/molprobity/molprobity.out ] && [ -f validation/molprobity/clashscore.txt ] ; then
 	phenix.molprobity $c.cif	    
	rm molprobity_probe.txt
	mv molprobity* validation/molprobity/
	cd $base
	continue
	fi   	
    fi
    if [ -f validation/molprobity/clashscore.txt ] ; then
	phenix.reduce -NOFLIP $c.cif > validation/molprobity/$c.H.pdb
	cd validation/molprobity/
	rama_chart_pdf $c.H.pdb
	multichart $c.H.pdb
    else
	if [ -f validation/molprobity/molprobity.out ] ; then
	    phenix.clashscore $c.cif > validation/molprobity/clashscore.txt
	    rm validation/molprobity/molprobity_probe.txt
       	    phenix.reduce -NOFLIP $c.cif > validation/molprobity/$c.H.pdb
	    cd validation/molprobity/
	    rama_chart_pdf $c.H.pdb
	    multichart $c.H.pdb
	else
#	    if [ -f $c.mtz ]; then
	    echo 'reflections here'
	    mkdir validation
	    mkdir validation/molprobity
	    phenix.molprobity $c.cif	    
	    rm molprobity_probe.txt
	    mv molprobity* validation/molprobity/
	    phenix.clashscore $c.cif > validation/molprobity/clashscore.txt
    	    phenix.reduce -NOFLIP $c.cif > validation/molprobity/$c.H.pdb
	    cd validation/molprobity/
	    rama_chart_pdf $c.H.pdb
	    multichart $c.H.pdb
#            fi
        fi
    fi

cd $base
done

cd ..
   
