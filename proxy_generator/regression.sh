 

export file="/export/zachary/data/spec_avg_proxies/mcf_s/mcf_s_br4/mcf_s_newimix_br4.json"
output_dir="/export/sflolid/software/SimTrace/scratch/regressions/"
rm $output_dir/reg_out_*


./CodeGenerator.py --configFile=$file --branch_model=v4_local --mem_model=ZL --seed=5 -o $output_dir/reg_out_ZL.c --verbose=3 > $output_dir/reg_out_ZL.txt
./CodeGenerator.py --configFile=$file --branch_model=v4_local --mem_model=MA --seed=5 -o $output_dir/reg_out_MA.c --verbose=3 > $output_dir/reg_out_MA.txt
./CodeGenerator.py --configFile=$file --branch_model=v4_local --mem_model=ZS --seed=5 -o $output_dir/reg_out_ZS.c --verbose=3 > $output_dir/reg_out_ZS.txt
./CodeGenerator.py --configFile=$file --branch_model=v4_local --mem_model=HALO --halo_trace=/export/zachary/software/pg/test_tiny  --seed=5 -o $output_dir/reg_out_HALO.c --verbose=3 > $output_dir/reg_out_HALO.txt



##Checking for differences
if [ -e $output_dir/reg_out_MA.c ] && \
    [ -e $output_dir/reg_out_ZL.c ] && \
    [ -e $output_dir/reg_out_MA.c ]
then
diff $output_dir/reg_out_MA.c $output_dir/golden_copies/reg_out_MA.c
diff $output_dir/reg_out_ZL.c $output_dir/golden_copies/reg_out_ZL.c
diff $output_dir/reg_out_ZS.c $output_dir/golden_copies/reg_out_ZS.c
fi
rm *.pyc
