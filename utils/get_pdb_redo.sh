#!/bin/bash


#x is the full path to the folder
#c is the pdb code
#e is the entry in lower case (for pdb_redo)


base=$(pwd)


for x in */*/* ;
do
    c=`basename $x`;
    echo $x
    e="${c,,}" ;
    cd $x ;
    cd validation
    ls
    if [ -d pdb-redo ] ; then
       echo "Nothing to do here"
    else
        echo 'missing stuff here!' 
	mkdir pdb-redo
	cd pdb-redo
	wget https://pdb-redo.eu/db/$e.zip
	unzip $e.zip
	rm $e.zip
    fi

cd $base
done

cd ..
   
