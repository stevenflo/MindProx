
declare -a workloads=("gcc" "mcf" "perlbench" "511.povray_r" "507.cactuBSSN_r")
#declare -a workloads=("mcf" )

for workload in "${workloads[@]}"
do
    
    ./CodeGenerator.py --configFile=/root/avmashru/spec_2017_profiles/$workload/$workload.bv3.new.json --branch_model=v4_local --mem_model=ZL --seed=5 -o /root/avmashru/spec_2017_profiles/$workload/$workload.zl_i2_bv4b.c --verbose=3
    gcc /root/avmashru/spec_2017_profiles/$workload/$workload.zl_i2_bv4b.c -o /root/avmashru/spec_2017_profiles/$workload/$workload.zl_i2_bv4b
done
rm *.pyc

