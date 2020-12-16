#!/usr/bin/python3
import os
import shutil
import subprocess

#Paths to various software portion

software_dir = "./memory_profiler/"
proxygen_dir = "./proxy_generator/"
script_dir = "./core_profiler/pin_replay_tools/"

#paths that may change for the script
pin_dir = "/export/sflolid/software/new_pin/pinplay-drdebug-3.5-pin-3.5-97503-gac534ca30-gcc-linux/"
tool_dir = "extras/pinplay/bin/intel64/"
sim_dir = "/export/sflolid/data/reena_transfer/rpanda/reena/proxy-dir/l12-data-proxy/cache/"

#Experiment Information
experiment = "tutorial"
spec_directories = "./spec_proxies/"

#Workload Information
commands={"gcc":r"$CPU17/gcc_s/sgcc_base.gcc48-64bit-m64 $CPU17/gcc_s/gcc-pp.c -O5 -fipa-pta -o gcc-pp.opts-O5_-fipa-pta.s ",
           "perlbench":r"$CPU17/perlbench_s/perlbench_s_base.refspeed.gcc48-64bit-m64 -I$CPU17/perlbench_s/lib $CPU17/perlbench_s/checkspam.pl 2500 5 25 11 150 1 1 1 1",
           "mcf":r"$CPU17/mcf_s/mcf_s_base.refspeed.gcc48-64bit-m64 $CPU17/mcf_s/inp.in",
           "leela":r"$CPU17/leela_s/leela_s_base.refspeed.gcc48-64bit-m64 $CPU17/leela_s/ref.sgf",
           "deepsjeng":r"$CPU17/deepsjeng_s/deepsjeng_s_base.refspeed.gcc48-64bit-m64 $CPU17/deepsjeng_s/ref.txt",
          "xz":r"$CPU17/xz_s/xz_s_base.refspeed.gcc48-64bit-m64  $CPU17/xz_s/cpu2006docs.tar.xz 6643 055ce243071129412e9dd0b3b69a21654033a9b723d874b2015c774fac1553d9713be561ca86f74e4f16f22e664fc17a79f30caa5ad2c04fbc447549c2810fae 1036078272 1111795472 4",
          "x264":r"$CPU17/x264_s/x264_s_base.refspeed.gcc48-64bit-m64 --seek 500 --dumpyuv 200 --frames 1250 -o $CPU17/x264_s/BuckBunny_New.264 $CPU17/x264_s/BuckBunny.yuv 1280x720",
          "omnetpp":r"$CPU17/omnetpp_s/omnetpp_s_base.refspeed.gcc48-64bit-m64 -c General -r 0 ",
          "xchg2":r"$CPU17/exchange2_s/exchange2_s_base.refspeed.gcc48-64bit-m64 6",
          "xalancbmk":r"$CPU17/xalancbmk_s/xalancbmk_s_base.refspeed.gcc48-64bit-m64 -v $CPU17/xalancbmk_s/t5.xml $CPU17/xalancbmk_s/xalanc.xsl",
}

ratio = {"leela":".27", "deepsjeng":".33","mcf":".20","perlbench":".36","gcc":".26","xz":".5","x264":".16","xalancbmk":".2",
         "xchg2":".34","omnetpp":".35"
}

 


def prep_experiment(name):
    base_dir = spec_directories + name + "/" + experiment + "/"
    base = base_dir + name + "." + experiment + "."
    #Note the source needs to be manually updated currently
    source_exp = "V12"
    spec_source = "/backup/sflolid/data/MemTraceExp/spec_workloads/"
    source = spec_source + name + "/" + source_exp + "/" + name + "." + source_exp + "."
    try:
        os.mkdir(base_dir)
        print("Directory " , base_dir ,  " Created ") 
    except FileExistsError:
        print("Directory " , base_dir ,  " already exists")
    #files = ["1mil_trace", "halo_out", "log_scale_out", "linked_list_out", "i2b4.json", "proxy.c"]
    #files = ["30mil_trace", "i2b4.json"]
    #files = ["out.json", "out.h",  "log_scale_out", "json"]
    files = ["halo_out" ]
    #files = ["ll_in.json", "log_scale_out"]
    for file_name in files:
        #os.remove(base + file_name)
        try:
            shutil.copy(source + file_name, base + file_name )
            #shutil.copytree(source + file_name, base_dir+file_name)
        except:
            print("Failed to copy " + source + file_name + " to " + base + file_name)


def compile_software():

    cmds = [None] * 4
    
    cmds[0] = "g++"
    cmds[1] = "-o"
    cmds[2] = software_dir + "trace_to_log_converter"
    cmds[3] = software_dir + "trace_to_log_converter.cpp"
    
    command = subprocess.check_output(cmds)

def make_pinball(name):
    base = spec_directories + name + "/" + experiment + "/" + name + "." + experiment + "."


    
    cmds = [None] * 18
    cmds[0] = pin_dir + "pin"
    cmds[1] = "-t"
    cmds[2] = pin_dir + tool_dir + "pinplay-driver.so" 
    cmds[3] = "-log"
    cmds[4] = "-xyzzy"
    cmds[5] = "-log:basename"
    cmds[6] = base + "pinball"
    cmds[7] = "-log:skip"
    cmds[8] = "100000000000"
    cmds[9] = "-log:length"
    cmds[10] = "100000000"
    cmds[11] = "-log:mt"
    cmds[12] = "0"
    cmds[13] = "-log:compressed"
    cmds[14] = "bzip2"
    cmds[15] = "-log:syminfo"
    cmds[16] = "-log:pid"
    cmds[17] = "--"
    program = commands[name].split()
    for i in range(len(program)):
        program[i] = os.path.expandvars(program[i])

    cmds = cmds + program
    for word in cmds:
        print(word, end=" ")
    print("")

    output = open(base + "pinballs", "w")
    command = subprocess.Popen(cmds, stdout=output)

def make_JSON(name):
    base = spec_directories + name + "/" + experiment + "/" + name + "." + experiment + "."

    
    cmds = [None] * 4
    cmds[0] = script_dir + "mkJSON_both_pinballs.sh"
    cmds[1] = base + "pinball_" + pid
    cmds[2] = spec_directories + name + "/" + experiment + "/"
    cmds[3] = name + "." + experiment + ".json"
    for word in cmds:
        print(word, end=" ")
    print("")

    output = open(base + "json.std_out", "w")
    command = subprocess.Popen(cmds, stdout=output)
    

def visualize(name):
    base = spec_directories + name + "/" + experiment + "/" + name + "." + experiment + "."
    cmds = [None] * 2
    
    cmds[0] = "./visualize.py"
    cmds[1] = base + "trace_histogram"
    
    output = open(base + "proxy_halo_histogram", "w")
    command = subprocess.Popen(cmds, stdout=output)



def subdirs(path):
    dir = [d for d in os.listdir(path)
                   if not os.path.isfile(os.path.join(path,d))]
    return dir


def get_champ_trace(name):
    base = spec_directories + name + "/" + experiment + "/" + name + "." + experiment + "."


    
    cmds = [None] * 9
    cmds[0] = pin_dir + "pin"
    cmds[1] = "-t"
    cmds[2] = pin_dir + tool_dir + "champsim_tracer.so"
    cmds[3] = "-o"
    cmds[4] = base + "proxy_chtrace_out"
    cmds[5] = "-t"
    cmds[6] = "100000000"
    cmds[7] = "--"
    cmds[8] = base + "proxy"
    print(cmds)

    output = open(base + "champ_trace_log", "w")
    command = subprocess.Popen(cmds, stdout=output)
    #command.wait()

def compress_champ_trace(name):
    base = spec_directories + name + "/" + experiment + "/" + name + "." + experiment + "."
    cmds = [None] * 3
    cmds[0] = "xz"
    cmds[1] = "--compress"
    cmds[2] = base + "proxy_chtrace_out"
    print(cmds)
    command = subprocess.Popen(cmds)

def run_champ_trace(name):
    base = spec_directories + name + "/" + experiment + "/" + name + "." + experiment + "."
    tr_dir = spec_directories + name + "/" + experiment + "/"
    trace = name + "." + experiment + "." + "proxy_chtrace_out.xz"
    cmds = [None] * 6
    cmds[0] = "./champsim.sh"
    cmds[1] = "bimodal-no-no-no-no-lru-1core"
    cmds[2] = "0"
    cmds[3] = "100"
    cmds[4] = trace
    cmds[5] = tr_dir
    print(cmds)

    output = open(base + "champsim_log", "w")
    command = subprocess.Popen(cmds, stdout=output)


def get_mem_trace(name):
    base = spec_directories + name + "/" + experiment + "/" + name + "." + experiment + "."

    
    cmds = [None] * 6
    cmds[0] = pin_dir + "pin"
    cmds[1] = "-t"
    cmds[2] = pin_dir + tool_dir + "mt-l1access-mj.so"
    cmds[3] = "-o"
    cmds[4] = base + "mem_trace_out"
    cmds[5] = "--"
    #cmds[6] = base + "proxy"
    program = commands[name].split()
    for i in range(len(program)):
        program[i] = os.path.expandvars(program[i])

    cmds = cmds + program
    for word in cmds:
        print(word, end=" ")
    print("")


    output = open(base + "mem_trace_log", "w")
    command = subprocess.Popen(cmds, stdout=output)
    #command.wait()

def get_proxy_mem_trace(name):
    base = spec_directories + name + "/" + experiment + "/" + name + "." + experiment + "."


    
    cmds = [None] * 7
    cmds[0] = pin_dir + "pin"
    cmds[1] = "-t"
    cmds[2] = pin_dir + tool_dir + "mt-l1access-full.so"
    cmds[3] = "-o"
    cmds[4] = base + "proxy_mem_trace_out"
    cmds[5] = "--"
    cmds[6] = base + "proxy"
    for word in cmds:
        print(word, end=" ")
    print("")


    output = open(base + "mem_trace_log", "w")
    command = subprocess.Popen(cmds, stdout=output)
    #command.wait()


def trim(name):
    #Need to refactor this
    base = spec_directories + name + "/" + experiment + "/" + name + "." + experiment + "."
    mem_trace = base + "mem_trace_out"
    try:
        f = open(mem_trace)
    except:
        print("\033[93m No memtrace for: ", mem_trace, "\033[0m")
        return None
    dir = mem_trace[0:-13]
    out_name = base + "trimmed_trace"
    output = open(out_name, "w")
    #ignoring the head lines
    for x in range(3):
        next(f)
    #head = [next(f) for x in range(1000000)]
    for line in f:
        output.write(line)

def clean_mem_trace(name):
    base = spec_directories + name + "/" + experiment + "/" + name + "." + experiment + "."    
    cmds = [None] * 3
    cmds[0] = software_dir + "clean_trace.py"
    cmds[1] = base + "mem_trace_out"
    cmds[2] = base + "mem_trace_clean"
    print(cmds)

    output = open(base + "proxy_clean_trace_log", "w")
    command = subprocess.Popen(cmds, stdout=output)
    #command.wait()

def halo_trace(name):
    base = spec_directories + name + "/" + experiment + "/" + name + "." + experiment + "."
    cmd = software_dir + "proxy_rand_reuse_delta_v4_5"
    #arg1 = base + "1mil_trace"
    arg1 = base + "trimmed_trace"
    #arg1 = base + "proxy_trace_out"
    arg2 = base + "halo_log"
    output = open(base + "halo_out", "w")
    print(cmd, " ", arg1, " ", arg2, " > ", base + "halo_out")
    #print("DOING HALO FOR THE PROXY!")
    command = subprocess.Popen([cmd,arg1,arg2],stdout=output)
    return command

def log_convert(name):
    HALO = True
    base = spec_directories + name + "/" + experiment + "/" + name + "." + experiment + "."
    cmd = software_dir + "trace_to_log_converter"
    if(HALO):
        arg1 = base + "halo_out"
        output = open(base + "log_scale_out", "w")
        print("Doing HALO log_conversion!")
    else:
        arg1 = base + "proxy_mem_trace_out"
        output = open(base + "proxy_halo_hist", "w")
        print("Doing Trace log_conversion!")
    arg2 = base + "log_scale_log"


    print(cmd, " ", arg1, " ", arg2, " > ", base + output)
    if(HALO):
        command = subprocess.Popen([cmd,arg1,arg2],stdout=output)
    else:
        command = subprocess.Popen([cmd,arg1,arg2,"0","0"],stdout=output)
    return command

def make_ll_json(name):
    base = spec_directories + name + "/" + experiment + "/" + name + "." + experiment + "."
    program = "python3"
    cmd = software_dir + "ll_json_creator.py"
    arg1 = base + "log_scale_out"
    arg2 = base + "ll_in.json"
    arg3 = ratio[name]
    output = open(base + "linked_list_log", "w")
    print(program, " ", cmd, " ", arg1, " ", arg2, " > ", base + "linked_list_log")
    try :
        command = subprocess.Popen([program,cmd,arg1,arg2,arg3], stdout=output)
    except:
        print("Workload: ", name, " failed to make linked list")

    

def make_linked_list(name):
    base = spec_directories + name + "/" + experiment + "/" + name + "." + experiment + "."
    """
    cmds = [None] * 8
    cmds[0] = software_dir + "trace2ll.py"
    cmds[1] = "-i"
    cmds[2] = base + "ll_in.json"
    cmds[3] = "-e"
    cmds[4] = base + "out.h"
    cmds[5] = "-m"
    cmds[6] = base + "out.json"
    cmds[7] = "-c"
    """

    cmds = [None] * 10
    cmds[0] = software_dir + "trace2ll.py"
    cmds[1] = "-i"
    cmds[2] = base + "ll_in.json"
    cmds[3] = "-e"
    cmds[4] = base + "out.h"
    cmds[5] = "-m"
    cmds[6] = base + "out.json"
    cmds[7] = "-c"
    cmds[8] = "-v"
    cmds[9] = spec_directories + name + "/" + experiment + "/visualiztions/"

    for word in cmds:
        print(word, end=" ")
    print("")

    output = open(base + "trace2ll.log", "w")


    try :
        command = subprocess.Popen(cmds, stdout=output)
    except:
        print("Workload: ", name, " failed to make linked list")
    return command


def get_cache_stats(name):
    base = spec_directories + name + "/" + experiment + "/" + name + "." + experiment + "."



    cmds = [None] * 5
    cmds[0] = sim_dir + "a.out"
    size = 8 
    assoc = 8

    if(1):
        #Note this stuff is a little wonky!!!
        cmds[1] = base + "proxy_clean_trace_log"
        output = open(base + "cache_proxy_"+str(size)+"_"+str(assoc), "w")
    else:
        cmds[1] = base + "clean_trace_log"
        output = open(base + "cache_orig_"+str(size)+"_"+str(assoc), "w")
    cmds[2] = str(size)
    cmds[3] = str(assoc)
    cmds[4] = "64"
    print(cmds)


    command = subprocess.Popen(cmds, stdout=output)
    #command.wait()





def make_proxy(name):
    base = spec_directories + name + "/" + experiment + "/" + name + "." + experiment + "."
    cmds = [None] * 10
    
    cmds[0] = proxygen_dir + "CodeGenerator.py"
    cmds[2] = "--configFile=" + base + "json"
    cmds[1] = "--branch_model=v5_correlation"
    cmds[3] = "--mem_model=HALO"
    cmds[4] = "--linked_list=" + base + "out.h"
    cmds[5] = "--seed=5"
    cmds[6] = "--verbose=3"
    cmds[7] = "--syntheticOutputFile=" + base + "proxy.c"
    cmds[8] = "--mem_multi_region=" + base + "log_scale_out"
    cmds[9] = "--linked_list_json=" + base + "out.json"
    for word in cmds:
        print(word, end=" ")
    print("")

    output = open(base + "proxy_log", "w")
    command = subprocess.Popen(cmds, stdout=output)
    #command.wait()


def compile_proxy(name):
    base = spec_directories + name + "/" + experiment + "/" + name + "." + experiment + "."
    cmds = [None] * 6
    
    cmds[0] = "gcc"
    cmds[1] = "-g"
    cmds[2] = "-o"
    cmds[3] = base + "proxy"
    cmds[4] = "--freestanding"
    #cmds[5] = "--nostdlib"
    cmds[5] = base + "proxy.c"
    
    #command = subprocess.check_output(cmds)
    command = subprocess.Popen(cmds)

    return command
    
def perf_proxy(name):
    base = spec_directories + name + "/" + experiment + "/" + name + "." + experiment + "."
    #"perf stat -o $output -e instructions,cycles,branch-misses,branches,cache-misses,cache-references $orig_workload"

    cmds = [None] * 7
    
    cmds[0] = "perf"
    cmds[1] = "stat"
    cmds[2] = "-o"
    cmds[3] = base + "perfstat"
    cmds[4] = "-e"
    cmds[5] = "instructions,cycles,branch-misses,branches,cache-misses,cache-references"
    cmds[6] = base + "proxy"
    print(cmds)




    output = open(base + "perf_log", "w")
    command = subprocess.Popen(cmds, stdout=output)
    command.wait()
    return command

def tau_proxy(name):
    #NOTE THIS FUNCTION DOES NOT WORK, TAU ONLY WORKS FROM COMMAND LINE AT THE MOMENT
    #NEED TO DEBUG LIBRAY LINKAGE
    base = spec_directories + name + "/" + experiment + "/" + name + "." + experiment + "."
    tau_base = spec_directories + name + "/TAU_WRITE"
    #tau_base = spec_directories + name + "/TAU"

    try:
        os.mkdir(tau_base)
    except:
        print("TAU directory already exists")
    os.chdir(tau_base)

    my_env = os.environ.copy()
    my_env["TAU_PROFILE"] = "0"
    my_env["TAU_TRACE"] = "1"
    my_env["TAU_METRICS"] = "PAPI_L1_DCM,PAPI_L1_ICM,PAPI_L1_TCM"
    cmds = [None] * 7
    cmds[0] = "tau_exec"
    cmds[1] = "stat"
    cmds[2] = "-T"
    cmds[3] = "serial,papi"
    cmds[4] = "-ebs_source=PAPI_TOT_INS"
    cmds[5] = "-ebs_period=100000000"
    cmds[6] = base + "proxy"
    #cmds[6] = base + "proxy"
    print(cmds)

    output = open(base + "tau_log", "w")
    command = subprocess.Popen(cmds, stdout=output, env=my_env)
    command.wait()
    return 0

def sde_proxy(name):
    base = spec_directories + name + "/" + experiment + "/" + name + "." + experiment + "."
    sde_base = spec_directories + name + "/" + experiment + "/SDE"

    try:
        os.mkdir(sde_base)
    except:
        print("SDE directory already exists or path broken")
    os.chdir(sde_base)

    cmds = [None] * 4
    cmds[0] = software_dir + "SDE_profiler.sh"
    cmds[1] = base + "proxy"
    cmds[2] = sde_base
    cmds[3] = name
    print(cmds)

    output = open(base + "sde_log", "w")
    command = subprocess.Popen(cmds, stdout=output)
    #command.wait()
    return 0

def measure_histogram(name):
    base = spec_directories + name + "/" + experiment + "/" + name + "." + experiment + "."
    cmds = [None] * 7
    cmds[0] = software_dir + "measure_hist.py"
    cmds[1] = "--initial"
    cmds[2] = base + "log_scale_out"
    cmds[3] = "--linked"
    cmds[4] = base + "linked_list_out"
    cmds[5] = "--output"
    cmds[6] = base + ".histogram"
    print(cmds)

    output = open(base + "tau_log", "w")
    command = subprocess.Popen(cmds)
    command.wait()



#uncomment this line to recompile all cpp programs
#compile_software()

pid = "18579"
#for name in ["deepsjeng", "gcc", "leela", "mcf","perlbench"]
for name in ["deepsjeng"]:


    prep_experiment(name)
    ########################
    ###Profiling Workload###
    ########################
    #make_pinball(name)
    #make_JSON(name)
    #get_mem_trace(name)
    #trim(name)
    #halo_trace(name)

    #Steps included in tutorial
    #log_convert(name)
    #make_ll_json(name)
    #make_linked_list(name)

    ##########################
    ###CREATING PROXIES#######
    ##########################
    #make_proxy(name)
    #compile_proxy(name)

    ##########################
    ###ANALYZING RUNS#########
    ##########################
    #perf_proxy(name)
    #get_proxy_mem_trace(name)
    #sde_proxy(name)
    #measure_histogram(name)
    #visualize(name)
    #get_cache_stats(name)    
    ###CHAMPSIM RELATED#######
    #clean_mem_trace(name)
    #get_champ_trace(name)
    #compress_champ_trace(name)
    #run_champ_trace(name)

