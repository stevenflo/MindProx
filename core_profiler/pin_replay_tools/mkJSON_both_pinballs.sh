#!/usr/bin/env bash

PINPATH=/export/sflolid/software/new_pin/pinplay-drdebug-3.5-pin-3.5-97503-gac534ca30-gcc-linux
PIN_ROOT=$PINPATH
SDE_ROOT=/export/sflolid/software/sde-external-8.16.0-2018-01-30-lin
TOOLPATH=$PINPATH/extras/pinplay/bin/intel64/
SCRIPT_HOME=/export/zachary/software/JSON_full
REPLAY="-xyzzy -reserve_memory $1.address "
NULLAPP="$PIN_ROOT/extras/pinplay/bin/intel64/nullapp"

if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ]
	then
		echo "Usage: ./mkJSON.sh <PINBALL PATH AND BASE NAME> <OUTPUT DIR PATH> <OUTPUT FILE PREFIX>"
		exit 1
fi
sed -e 's/^"//' -e 's/"$//' <<<"$1"
mkdir -p $2
echo "Running SDE..."
echo "$SDE_ROOT/sde -replay -replay:basename $1 -replay:addr_trans -mix -- $NULLAPP"
$SDE_ROOT/sde -replay -replay:basename $1 -replay:addr_trans -mix -- $NULLAPP
mv sde-mix-out.txt $2/.
echo "Extracting imix..."
/export/zachary/software/sde_parser/imix_new.py $2/sde-mix-out.txt $2/imix_new.out > $2/output.log
echo "Running PIN..."
$PINPATH/pin $REPLAY -t $TOOLPATH/st-imix-v5.so -replay -replay:basename $1 -o $2/imix_old.out -- $NULLAPP >> $2/output.log
echo "1/6"
$PINPATH/pin $REPLAY -t $TOOLPATH/st-branchconfigs-mj-v5.so -replay -replay:basename $1 -o $2/branch.out -- $NULLAPP >> $2/output.log
echo "2/6"
$PINPATH/pin $REPLAY -t $TOOLPATH/st-inst-data-footprint-mj-v5.so -replay -replay:basename $1 -o $2/footprint.out -- $NULLAPP >> $2/output.log
echo "3/6"
$PINPATH/pin $REPLAY -t $TOOLPATH/st-localstride256-mj-v5.so -replay -replay:basename $1 -o $2/lstride.out -- $NULLAPP >> $2/output.log
echo "4/6"
$PINPATH/pin $REPLAY -t $TOOLPATH/st-pnstride-mj-v5.so -replay -replay:basename $1 -o $2/pnstride.out -- $NULLAPP >> $2/output.log
echo "5/6"
$PINPATH/pin $REPLAY -t $TOOLPATH/st-regdist-mj-v5.so -replay -replay:basename $1 -o $2/regdist.out -- $NULLAPP >> $2/output.log
echo "6/6"
echo "Running the new branch profiler"
$PINPATH/pin $REPLAY -t $TOOLPATH/branchconfigs-correlation.so -replay -replay:basename $1 -o $2/branch_local.out -- $NULLAPP >> $2/output.log
#echo "Generating JSON data files..."
#$SCRIPT_HOME/jsongen.py --im $2/imix_old.out --br $2/branch.out --fp $2/footprint.out --ls $2/lstride.out --ps $2/pnstride.out --rd $2/regdist.out --o $2/$3\_old.json
$SCRIPT_HOME/jsongen.py --im $2/imix_new.out --br $2/branch_local.out --fp $2/footprint.out --ls $2/lstride.out --ps $2/pnstride.out --rd $2/regdist.out --o $2/$3
#$SCRIPT_HOME/jsongen.py --im $2/imix_old.out --br $2/branch.out --fp $2/footprint.out --ls $2/lstride.out --ps $2/pnstride.out --rd $2/regdist.out --o $2/old.json
#$SCRIPT_HOME/jsongen.py --im $2/imix_new.out --br $2/branch.out --fp $2/footprint.out --ls $2/lstride.out --ps $2/pnstride.out --rd $2/regdist.out --o $2/new.json
