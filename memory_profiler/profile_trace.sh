#!/bin/bash
TOOLPATH=$PINPATH/source/tools/Mix/obj-intel64/

if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ]
	then
		echo "Usage: ./profile_trace.sh <INPUT CMD> <OUTPUT DIR PATH> <OUTPUT FILE PREFIX>"
		exit 1
fi
sed -e 's/^"//' -e 's/"$//' <<<"$1"



echo "Tracing memory accesses"
echo "    $PINPATH/pin -t $TOOLPATH/mt-l1access-mj.so -o $2/mem_trace.out -- $1 >> $2/mem_trace.log"
$PINPATH/pin -t $TOOLPATH/mt-l1access-mj.so -o $2/mem_trace.out -- $1 >> $2/mem_trace.log

