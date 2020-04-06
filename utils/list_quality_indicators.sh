#!/bin/bash

#p is the protein folder
#x is the virus/pdbid path to the folder
#c is the pdb code

cd pdb

if [ -e list_quality_indicators.txt ]
then
    rm list_quality_indicators.txt
fi
touch list_quality_indicators.txt

for p in $(ls -d */) ;
do
    echo -e "\n\n################################################" >> list_quality_indicators.txt
    echo ${p%?} >> list_quality_indicators.txt
    echo -e "################################################\n" >> list_quality_indicators.txt
    cd $p
     for x in $(ls -d */*/) ;
     do
         c=`basename $x`
         cd $x
         echo ${x%?}
        
         # method
         temp=$(grep "_exptl.method " ${c}.cif)
         r_free="     "
         method="     "
         resolution="    "
         temp2=""
         temp3=""
         if echo "$temp" | grep "ELECTRON MICROSCOPY"; then
            method="em   "
            
            # em resolution
              temp3=$(grep "_em_3d_reconstruction.resolution " ${c}*.cif)
            if [ ! -z "$temp3" ]
            then
                resolution=${temp3:53:53}
            else
                resolution="N/A  "   
            fi

         elif echo "$temp" | grep "X-RAY DIFFRACTION"; then
            method="cryst"
            
            # cryst r_free
            temp2=$(grep "_refine.ls_R_factor_R_free " ${c}.cif)
            if [ ! -z "$temp2" ]
            then
                r_free=${temp2:54:54}
            else
                r_free="N/A  "
            fi
            
            # cryst resolution
            temp2=$(grep "_reflns.d_resolution_high  " ${c}.cif)
            if [ ! -z "$temp2" ]
            then
                resolution=${temp2:43:43}
            else
                resolution="N/A  "   
            fi

                
         elif echo "$temp" | grep "SOLUTION NMR"; then
            method="nmr  "
            
         else
            method="other"            
         fi
         line=${x%?}$'\t'$method$'\t'${resolution}$'\t'${r_free}         
         cd ../..
         echo $line >> ../list_quality_indicators.txt
     done
     cd ..
done
cd ..
