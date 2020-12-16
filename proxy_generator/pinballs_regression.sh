rm ./test
rm ./outputs_regressions/pinballs/SimTrace_Proxy
#rm ./outputs_regressions/pinballs/t0* -r

#gcc func_ptr.c -o test
##Checking the file output
./make_SimTraceProxy.py -i ../profiler/pinball_out/ -t /export/sflolid/data/spec_runs/leela/100M/leela.try_33426.Data/t.labels  -o ./outputs_regressions/pinballs/ -v 2
gcc ./outputs_regressions/pinballs/SimTrace_Proxy.c -o ./outputs_regressions/pinballs/SimTrace_Proxy




##Checking for differences
if [ -e ./outputs_regressions/pinballs/SimTrace_Proxy ]
then
./outputs_regressions/pinballs/SimTrace_Proxy
fi

