import os, csv, re, sys
from os import listdir, path


#Program takes 3 parameters to run: filepath, where to save file, and which version to run... will change to write every version to one csv soon.

#opens pasted file location...should work for windows/linux

data = os.path.join(sys.argv[1])


#sets where file is saved
path_to_save = os.path.join(sys.argv[2])
psave = os.path.join(path_to_save,"TAU_data.csv")
csave = os.path.join(path_to_save,"cache_data.csv")

#some csv test formatting
with open(psave, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["BENCHMARK","EXPERIMENT","PAPI_TOT_INS", "PAPI_L1_DCM", "PAPI_L1_ICM", "PAPI_L1_TCM"])

file.close()


with open(csave, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["WorkLoad", "Experiment", "L1 Cache Size", "L1 Assoc", "Instructions", "L1 Misses", "L2 Misses", "L1MPKI", "L2MPKI"])

file.close()

def TAU_parser(benchmark, experiment):

        ins = ""
        dcm = ""
        icm = ""
        tcm = ""

        my_path = os.path.join(data, "spec_workloads", benchmark, experiment, "TAU")

        if(path.isdir(my_path)):        

            for f in os.listdir(my_path):

                    match = re.search(r"(.raw)", f)
                    p = os.path.join(my_path,f)
                    if(os.path.isfile(p)):
                            if(match):
                            #written to csv
                                    lines = open(p, 'r')
                                    read = lines.readlines()
                                    lines.close()




                            #looks for line of text that contains matching numbers
                                    for line in read:
                                            values = (re.search(r"((\d+) (\d+) (\d+) (\d+) \| \d+)$", line))
                                            if(values):
                                                    ins = values.group(2)
                                                    dcm = values.group(3)
                                                    icm = values.group(4)
                                                    tcm = values.group(5)

                                                    file = open(psave, "a")
                                                    file.write(benchmark + "," + experiment + "," + ins + "," + dcm + "," + icm + "," + tcm + "\n")
                                                    file.close()
                                                    break
        else:
            print("Could Not find " + my_path + "\n")
        return


def cache_parser(benchmark, experiment):
        
        benchmark = os.path.join(data, "spec_workloads", benchmark, experiment)
    


        for f in os.listdir(benchmark):

                bm_name = ""
                bm_type = ""

                bm_names = re.search(r"^([^.]+)",f).group(1)
                bm_type = re.search(r"((proxy)|(orig))",f)
                if(bm_type):
                        new_workload = bm_names + " " + bm_type.group(1)
                else:
                        continue

                p = os.path.join(benchmark,f)
                if(os.path.isfile(p)):
                        match = re.search(r"(_(\d)_(\d))$", f)
                        if(match):


                                #written to csv
                                name_size = match.group(1)
                                name_assoc = match.group(2)
                                lines = open(p, 'r')
                                read = lines.readlines()
                                lines.close()
                                size_match = []
                                load_accesses = ""
                                L1M_misses = ""
                                L2M_misses = ""
                                miss_rate = ""

                                #checks for parity between filename and file size/assoc
                                for line in read:
                                        size_match = re.search(r"(Cache Size:\s*)(\d)", line)
                                        if(size_match):
                                                if(size_match.group(2) != name_size):
                                                        sys.exit("WARNING: mismatch between cache size in filename and cache size in file", f,"... Exiting program ")
                                                else:
                                                        assoc_match = re.search(r"(Associativity:\s*)(\d)", line)
                                                        if(assoc_match):
                                                                if(assoc_match.group(2) != name_assoc):
                                                                        sys.exit("WARNING: mismatch between associativity in file name and associativity in file", f,"... Exiting program")

                                        break


                                L1M_flag = 0    #flag used for both L1 and L2 misses
                                access_flag = 0
                                miss_flag = 0

                                for line in read:

                                        #gets accesses data                             
                                        load_access = re.search(r"(^\s*LOAD\s*Accesses:\s*)(\d+)", line)
                                        if(load_access and access_flag == 0):
                                                load_accesses = load_access.group(2)
                                                access_flag = 1

                                        #gets L1 misses
                                        L_miss = re.search(r"(^\s*LOAD\s*Misses:\s*)(\d+)", line)
                                        if(L_miss and L1M_flag == 0):
                                                L1M_misses = L_miss.group(2)
                                                L1M_flag = 1

                                        #Gets L2 misses
                                        elif(L_miss and L1M_flag == 1):
                                                L2M_misses = L_miss.group(2)
                                                L1M_flag += 1



                                        #Gets L1 miss rate
                                        miss_rate1 = re.search(r"(^\s*LOAD\s*Miss Rate:\s*)([0-9]\.[0-9]+)", line)
                                        if(miss_rate1 and miss_flag == 0):
                                                miss_rate = miss_rate1.group(2)
                                                miss_flag = 1

                                #writes to csv
                                file = open(csave, "a")
                                file.write(new_workload + "," + experiment + "," + name_size + "," + name_assoc + "," + load_accesses + "," + L1M_misses + "," + L2M_misses + "," + miss_rate + "," + str(float(int(L2M_misses) / int(load_accesses))) + "\n")
                                file.close()

        return

def benchmark_parser(benchmark):

    new_path = os.path.join(data, "spec_workloads", benchmark)
        
    for f in os.listdir(new_path):
            experiment = re.search(r"(^V[\d]*)", f)
            if(experiment):
                    cache_parser(benchmark,experiment.group(1))
                    TAU_parser(benchmark, experiment.group(1))
    
    return

benchmark_parser("perlbench")
benchmark_parser("gcc")
benchmark_parser("deepsjeng")
benchmark_parser("leela")
benchmark_parser("mcf")
print("done")
