#!/usr/bin/python

# Copyright (c) 2019 The University of Texas at Austin. 
#     All rights reserved.
 
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
 
#       http://www.apache.org/licenses/LICENSE-2.0
 
#   Unless required by applicable law or agreed to in writing,
#   software distributed under the License is distributed on an "AS
#   IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
#   express or implied.  See the License for the specific language
#   governing permissions and limitations under the License.
 
#  For more about this software visit:
 
#       http://lca.ece.utexas.edu
import argparse		# actively maintained successor to optparse
import json
import copy
import sys
import os
import subprocess




###Helper Functions###
VERB = 0

def printv(level, *args):
	if VERB >= level:
		for i in args:
			print i,
		print ''


def setVerbosity(verbose):
	global VERB
	VERB = int(verbose)
	printv(2, "Verbosity = ", VERB)


def parseCommandLine():
	"""We parse the command line to fill in the options and set the verbosity
	
	    Args:
	No arguments are needed, automatically parses the command line
	
	    Returns:
	options: a collection of command line parameters, mainly JSON config file,
	desired output file, and level of verbosity
	
	"""

	parser = argparse.ArgumentParser(description="Generate a SimTrace proxy based on a collection of JSONS and a region trace")
	parser.add_argument("-i", "--JSONS", dest="json_dir", metavar="DIR", required=True, help="Directory containing JSONS to be used")
        parser.add_argument("-t", "--Trace", dest="trace", metavar="FILE", required=True, help="File containing the trace to be read in")
	parser.add_argument("-o", "--OutDir", dest="outDir", metavar="FILE", required=True, help="Output Directory for profiles, multiple subdirectories will be created for each Pinballs")
	parser.add_argument("-v", "--verbose", metavar="N", type=int, dest="Verb", default=0, help="level of debug information printed out (0-3)")
	args = parser.parse_args()
        setVerbosity(args.Verb)
	return args

def readTrace(file_name):
        trace = []
        with open(file_name) as f:
                for line in f:
                        words = line.split(' ')
                        trace.append(int(words[0]))
                        printv(3, words[0])
        printv(3, trace)
        printv(3, min(trace))
        printv(3, max(trace))
        return trace


def readJsons(loc):
        files = os.listdir(loc)
        printv(3, files)
        jsons = []
        for f in files:
                printv(3,loc+f)
                if os.path.isdir(loc + f):
                        jsons.append(f)
        printv(2,"Directories being used",jsons)
        return jsons

def generate_proxies(options, jsons):

        for json in jsons:
                if os.path.exists(options.outDir + json):
                        printv(3, "Output Directory for", options.outDir + json, "already exists")
                else:
                        printv(2, "Creating output directory", options.outDir + json)
                        os.makedirs(options.outDir + json)
                        cmd = "./CodeGenerator.py"
                        cmd += " --branch_model=v4_local --mem_model=ZL  --Pinball --seed=5 --verbose=2 "
                        cmd += " --configFile=" +  options.json_dir + json + "/" + json + "_new.json "
                        cmd += "-o " + options.outDir + json + "/" + json   + ".c"
                        cmd += " > " + options.outDir + json + "/" + json   + ".txt"
                        printv(2, "Running code generator:",cmd)
                        os.system(cmd)


def stitch_together(options, trace_array, jsons):
        with open(options.outDir +  "SimTrace_Proxy.c", 'w') as final_proxy:
                data = "#include<stdio.h>\n"
                final_proxy.write(data)
                for json in jsons:
                        with open(options.outDir + json + "/" + json   + ".c", 'r') as small_proxy:
                                data = small_proxy.read()
                                data = data.replace("BBL", json+"_BBL")
                                data = data.replace("X", json+"_X")
                                data = data.replace("main", "main_"+json)
                                final_proxy.write(data)
                data = """
int main() 
{ 
  // fun_ptr_arr is an array of function pointers 
  void (*fun_ptr_arr[])() = {"""
                for x in xrange(1,len(jsons)+1):
                        data += "main_t0r" + str(x) + ", "
                data  = data[:-2]
                data +="""};
  int array[] = {"""
                for e in trace_array:
                        data +=str(e) + ", "
                data  = data[:-2]
                data +=r'''};
  static int trace_length = sizeof(array)/sizeof(array[0]);
  static int x;
               
  while(x < trace_length){
    //printf("About to execute: %d with index %d\n", array[x]+1, x);
    (*fun_ptr_arr[array[x]])(); 
    //printf("On iteration: %d of %d\n", x, trace_length);
    x++;
  }

  return 0; 
} 
'''
                final_proxy.write(data)


        

if __name__== "__main__":
	options = parseCommandLine()
        printv(3, "Hello World")
        printv(2, "Input Directory:", options.json_dir)
        printv(2, "Trace Directory:", options.trace)
        printv(2, "Output Directory:", options.outDir)
        trace_array = readTrace(options.trace)
        json_dirs = readJsons(options.json_dir)
        generate_proxies(options, json_dirs)
        stitch_together(options, trace_array, json_dirs)
        
