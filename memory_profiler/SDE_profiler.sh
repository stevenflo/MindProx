#!/bin/bash

TOOLPATH=$PINPATH/source/tools/Mix/obj-intel64/
SCRIPT_HOME="/export/sflolid/software/SimTrace/proxy_gen_upgrades/"

if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ]
	then
		echo "Usage: ./mkJSON.sh <INPUT CMD> <OUTPUT DIR PATH> <OUTPUT FILE PREFIX>"
		exit 1
fi
sed -e 's/^"//' -e 's/"$//' <<<"$1"
mkdir -p $2

#Running Imix for bv4a
echo "Running SDE..."
$SDE_ROOT/sde -mix -- $1
mv sde-mix-out.txt $2/.
echo "Extracting imix..."
$SCRIPT_HOME/profiler/imix_new.py $2/sde-mix-out.txt $2/imix_new.out > $2/output.log

PROFILE=false
if [ "$PROFILE" = true ] ; then
    echo "Running SDE..."
    $SDE_ROOT/sde -mix -- $1
    mv sde-mix-out.txt $2/.
    echo "Extracting imix..."
    $SCRIPT_HOME/profiler/imix_new.py $2/sde-mix-out.txt $2/imix_new.out > $2/output.log
    echo "Running PIN..."
    $PINPATH/pin -t $TOOLPATH/st-imix-v5.so -o $2/imix_old.out -- $1 >> $2/output.log
    echo "1/6"
    $PINPATH/pin -t $TOOLPATH/st-branchconfigs-mj-v5.so -o $2/branch.out -- $1 >> $2/output.log
    echo "2/6"
    $PINPATH/pin -t $TOOLPATH/st-inst-data-footprint-mj-v5.so -o $2/footprint.out -- $1 >> $2/output.log
    echo "3/6"
    $PINPATH/pin -t $TOOLPATH/st-localstride256-mj-v5.so -o $2/lstride.out -- $1 >> $2/output.log
    echo "4/6"
    $PINPATH/pin -t $TOOLPATH/st-pnstride-mj-v5.so -o $2/pnstride.out -- $1 >> $2/output.log
    echo "5/6"
    $PINPATH/pin -t $TOOLPATH/st-regdist-mj-v5.so -o $2/regdist.out -- $1 >> $2/output.log
    echo "6/6"
    echo "Running the new branch profiler"
    $PINPATH/pin -t $TOOLPATH/branchconfigs-local.so -o $2/branch_local.out -- $1 >> $2/output.log
fi

JSON=false
if [ "$JSON" = true ] ; then
    echo "Generating JSON data files..."
    $SCRIPT_HOME/jsongen/jsongen.py --im $2/imix_old.out --br $2/branch_local.out --fp $2/footprint.out --ls $2/lstride.out --ps $2/pnstride.out --rd $2/regdist.out --o $2/$3.bv3.old.json
    $SCRIPT_HOME/jsongen/jsongen.py --im $2/imix_new.out --br $2/branch_local.out --fp $2/footprint.out --ls $2/lstride.out --ps $2/pnstride.out --rd $2/regdist.out --o $2/$3.bv3.new.json
fi
