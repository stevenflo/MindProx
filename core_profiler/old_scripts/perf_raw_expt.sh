

# params
input="/root/avmashru/proxy_branch_expt/gcc/gcc-brexpt"
output="/root/avmashru/proxy_branch_expt/gcc/gcc-brexpt.perf"

perf stat -o $output -e  instructions,cycles,branch-misses,branches,cache-misses,cache-references $input


#params
input="/root/avmashru/proxy_branch_expt/mcf/mcf-brexpt"
output="/root/avmashru/proxy_branch_expt/mcf/mcf-brexpt.perf"

perf stat -o $output -e  instructions,cycles,branch-misses,branches,cache-misses,cache-references $input

# params
input="/root/avmashru/proxy_branch_expt/perlbench/perlbench-brexpt"
output="/root/avmashru/proxy_branch_expt/perlbench/perlbench-brexpt.perf"

perf stat -o $output -e  instructions,cycles,branch-misses,branches,cache-misses,cache-references $input

# params
input="/root/avmashru/proxy_branch_expt/cactus/cactus-brexpt"
output="/root/avmashru/proxy_branch_expt/cactus/cactus-brexpt.perf"

perf stat -o $output -e  instructions,cycles,branch-misses,branches,cache-misses,cache-references $input

# params
input="/root/avmashru/proxy_branch_expt/povray/povray-brexpt"
output="/root/avmashru/proxy_branch_expt/povray/povray-brexpt.perf"

perf stat -o $output -e  instructions,cycles,branch-misses,branches,cache-misses,cache-references $input


