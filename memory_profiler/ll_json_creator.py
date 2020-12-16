import json
import re, os, sys

input_file = sys.argv[1]
output_file = sys.argv[2]
store_ratio = sys.argv[3]



def proxy_offset_collector(input_file, output_file):
    data = {}
    data["min_array_access_ratio"] = .2
    data["trace_data"] = {}


    lines = open(input_file, 'r')
    read = lines.readlines()
    lines.close()

    

    for line in read:
        values = re.search(r"(^\d+):(.*$)", line)
        if(values):
            offsets = []
            region = "region" + str(values.group(1)) 
            data["trace_data"][region] = {}
            string_offsets = values.group(2)
            offsets = [int(x) for x in string_offsets.split(' ')]
            data["trace_data"][region]["strides"] = offsets
            data["trace_data"][region]["store_ratio"] = store_ratio
            

    with open(output_file, 'w') as f:
        json.dump(data, f)
    return



proxy_offset_collector(input_file, output_file)

