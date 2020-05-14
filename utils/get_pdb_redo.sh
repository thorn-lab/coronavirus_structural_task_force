#!/bin/bash


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
    if [ -d validation/pdb-redo ] ; then
       echo "Nothing to do here"
    else
	wget https://pdb-redo.eu/db/$e.zip
    fi
    if [ -f $e.zip  ] ; then
        mkdir validation
	mkdir validation/pdb-redo
	mv $e.zip /validation/pdb-redo
	cd validation/pdb-redo
	unzip $e.zip
	rm $e.zip
    fi
cd $base
done

cd ..
   
