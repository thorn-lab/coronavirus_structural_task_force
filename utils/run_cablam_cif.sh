cd ../pdb

base=$(pwd)


for x in */*/* ;
do
    c=`basename $x`;
    echo $x
    e="${c,,}" ;
    cd $x ; 
    if [ -f  validation/molprobity/cablam.out ] ; then
	echo 'nothing to do here'
    else
	phenix.cablam $c.cif > validation/molprobity/cablam.out
	
    fi
    cd $base

done
