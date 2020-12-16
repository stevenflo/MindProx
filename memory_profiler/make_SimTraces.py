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

def generate_proxies(options, jsons):

        for json in jsons:
                if os.path.exists(options.outDir + json):
                        printv(3, "Output Directory for", options.outDir + json, "already exists")
                else:
                        printv(2, "Creating output directory", options.outDir + json)
                        os.makedirs(options.outDir + json)
                        cmd = "./SimTrace.sh"
                        cmd += " --branch_model=v3_global --mem_model=ZL  --Pinball --seed=5 --verbose=2 "
                        cmd += " --configFile=" +  options.json_dir + json + "/" + json + "_new.json "
                        cmd += "-o " + options.outDir + json + "/" + json   + ".c"
                        cmd += " > " + options.outDir + json + "/" + json   + ".txt"
                        printv(2, "Running code generator:",cmd)
                        os.system(cmd)


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
        
