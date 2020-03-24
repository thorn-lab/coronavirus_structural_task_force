#!/bin/bash
echo "##############################################################"
echo "this script runs WHATCHECK on specified PDB and generates PDF."
echo "##############################################################"
code=6m03

file_in=../${code}_original.cif
echo $file_in

if [ -e whatcheck ] ; then
    echo "Folder whatcheck already exists! Aborting."
else
    mkdir whatcheck
    cd whatcheck/
    pwd
    /usr/local/whatcheck/bin/whatcheck ${file_in}
    if [ -e pdbout.tex ] ; then
        echo "Success in running WHATCHECK!"
    else
        echo "WHATCHECK failed. Aborting."
    fi
    latex pdbout
    dvipdf pdbout
    if [ -e pdbout.pdf ] ; then
        echo "Success in making a PDF!"
    else
        echo "Could not make PDF. Aborting."
    fi
fi

