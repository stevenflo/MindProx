#Currently supported workloads, entries must be made in workloads, orig_worloads, and proxies for a new workload to function
#Please ensure that all orig_workloads can run to completion from the run_dir (move implicitly dependentfiles there)

#Directory roots
#9/27/19 Steven: Still in progress of adding proper roots and version names
WORKLOAD_ROOT="/root/sflolid/...."
OUTPUT_ROOT="/root/sflolid/...."
PROFILE_VERS="v2.0"
PROXY_VERS="v5.0"

declare -a workloads=("gcc" "perlbench" "mcf" "511.povray_r" "507.cactuBSSN_r")
#declare -a workloads=("mcf")

#Note: in the long run the root of the orig_workloads should be its own variable
#For example orig_base="/root/avmashru/cpu2017/benchspec/CPU/"
declare -a orig_workloads=("/root/avmashru/cpu2017/benchspec/CPU/502.gcc_r/exe/cpugcc_r_base.gcc8.1.0-lin-O2-rate-20180626 /root/avmashru/cpu2017/benchspec/CPU/502.gcc_r/run/run_base_refrate_gcc8.1.0-lin-O2-rate-20180626.0000/ref32.c -O3 -fselective-scheduling -fselective-scheduling2 -o ref32.opts-O3_-fselective-scheduling_-fselective-scheduling2.s"
			   "/root/avmashru/cpu2017/benchspec/CPU/505.mcf_r/run/run_base_refrate_gcc8.1.0-lin-O2-rate-20180626.0002/mcf_r_base.gcc8.1.0-lin-O2-rate-20180626 /root/avmashru/cpu2017/benchspec/CPU/505.mcf_r/run/run_base_refrate_gcc8.1.0-lin-O2-rate-20180626.0002/inp.in"
			   "/root/avmashru/cpu2017/benchspec/CPU/500.perlbench_r/run/run_base_refrate_gcc8.1.0-lin-O2-rate-20180626.0002/perlbench_r_base.gcc8.1.0-lin-O2-rate-20180626 -I/root/avmashru/cpu2017/benchspec/CPU/500.perlbench_r/run/run_base_refrate_gcc8.1.0-lin-O2-rate-20180626.0002/lib /root/avmashru/cpu2017/benchspec/CPU/500.perlbench_r/run/run_base_refrate_gcc8.1.0-lin-O2-rate-20180626.0002/checkspam.pl 2500 5 25 11 150 1 1 1 1 > checkspam.2500.5.25.11.150.1.1.1.1.out 2>> checkspam.2500.5.25.11.150.1.1.1.1.err"
			   "/root/avmashru/cpu2017/benchspec/CPU/511.povray_r/run/run_base_refrate_gcc8.1.0-lin-O2-rate-20180626.0000/povray_r_base.gcc8.1.0-lin-O2-rate-20180626 /root/avmashru/cpu2017/benchspec/CPU/511.povray_r/run/run_base_refrate_gcc8.1.0-lin-O2-rate-20180626.0000/SPEC-benchmark-ref.ini"
			   "/root/avmashru/cpu2017/benchspec/CPU/507.cactuBSSN_r/run/run_base_refrate_gcc8.1.0-lin-O2-rate-20180626.0000/cactusBSSN_r_base.gcc8.1.0-lin-O2-rate-20180626 /root/avmashru/cpu2017/benchspec/CPU/507.cactuBSSN_r/run/run_base_refrate_gcc8.1.0-lin-O2-rate-20180626.0000/spec_ref.par")

#Measuring perf of workloads
ORIGS=true
if [ "$ORIGS" = true ] ; then
    for i in {0..2};#Note that the indexing is done manually, must update if new workloads added
    do
	workload="${workloads[i]}"
	orig_workload="${orig_workloads[i]}"
	output="/backup/sflolid/data/MemTraceExp/spec_workloads/$workload/$workload.orig.perf"
	echo "perf stat -o $output -e instructions,cycles,branch-misses,branches,cache-misses,cache-references $orig_workload"
	perf stat -o $output.t0 -e instructions,cycles,branch-misses,branches,cache-misses,cache-references $orig_workload &

	perf stat -o $output.t1 -e instructions,cycles,branch-misses,branches,cache-misses,cache-references $orig_workload
    done
fi

#Profiling original workloads
PROFILE=false
if [ "$PROFILE" = true ] ; then
    for i in {0..4};#Note that the indexing is done manually, must update if new workloads added
    do
	workload="${workloads[i]}"
	orig_workload="${orig_workloads[i]}"
	output="/root/avmashru/spec_2017_profiles/$workload/${workload}.orig.perf"
	echo "./mkJSON_both.sh $input $output $output_name"
	./mkJSON_both.sh $input $output $output_name.fixed
    done
fi


#Measuring perf of proxies
PROXIES=false
if [ "$PROXIES" = true ] ; then
    for workload in "${workloads[@]}"
    do
	
	input="/root/avmashru/spec_2017_profiles/$workload/${workload}.zl_i2_bv4b"
	output="/root/avmashru/spec_2017_profiles/$workload/${workload}.zl_i2_bv4b.perf"
	echo "	gcc $input.c -o $input"
	gcc $input.c -o $input
	echo "perf stat -o $output -e instructions,cycles,branch-misses,branches,cache-misses,cache-references $input"
	#perf stat -o $output.t0 -e instructions,cycles,branch-misses,branches,cache-misses,cache-references $input &
	perf stat -o $output.1C1T.fixed -e instructions,cycles,branch-misses,branches,cache-misses,cache-references $input
    done
fi
    
#Profiling proxies
PROXY_PROF=true
if [ "$PROXY_PROF" = true ] ; then
    for workload in "${workloads[@]}"
    do
	
	input="/root/avmashru/spec_2017_profiles/$workload/${workload}.zl_i2_bv4b"
	output="/root/avmashru/spec_2017_profiles/$workload/${workload}.zl_i2_bv4b.profile/"
	output_name="${workload}_proxy_bv4b"
	echo "	gcc $input.c -o $input"
	gcc $input.c -o $input
	echo "./mkJSON_both.sh $input $output $output_name"
	./mkJSON_both.sh $input $output $output_name.fixed
    done
fi



