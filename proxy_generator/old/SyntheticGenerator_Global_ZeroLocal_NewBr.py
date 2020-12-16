#!/usr/bin/python 

# Copyright (c) 2015 The University of Texas at Austin. 
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
 
__author__ = "Reena Panda, Alexander Shulyak"
__copyright__ = "Copyright 2015, The University of Texas at Austin"
__credits__ = ["Reena Panda", "Alexander Shulyak", "Lizy L. John"]
__license__ = "Apache License, Version 2.0"
__version__ = "0.0.1"

"""Generates synthetics code that mimics a source code's architectural characteristics.

SyntheticGenerator.py is a synthetics generator that takes parameters related to
a code architecture-independent characteristics and generates synthetic code that
mimics these characteristics. These characteristics include instruction mix,
register dependencies, memory access strides, basic block size, and branch behavior.
These characteristics are passed to the generator in the JSON format.
SyntheticGenerator.py creates a single C code file with inline assembly instructions.
It currently support the x86 ISA, but the ARM ISA will be included in future releases.
Adding your own ISA is relatively simple as well.

Example:
	This example shows how to run SyntheticGenerator.py. descriptions of input arguments
	are written in brackets (<>).

	python SyntheticGenerator.py --configFile=<JSON file with code characteristics> -o <output file. C code>

	More detailed descriptions of the input arguments
	can be viewed in ./README file or by executing

	python SyntheticGenerator.py -h

More detailed documentation can be found in the README file found in the source head directory.
"""

import datetime
import sys
import optparse
import random
import json
import copy
#from CodeGenerator import *
from CodeGenerator_Global_ZeroLocal_NewBr import *
from BblGenerator import *
from VerbosePrint import *

def jsonToGenerator(codeGen, overallTree):
	total_instructions = float(0)	
	for k, v in overallTree["instruction_mix"].items():
		if str(k) != "total":
			total_instructions += float(v)
	# total_instructions = overallTree["instruction_mix"]["total"]
	printV(3, "actual total instructions is ", total_instructions )
	extra_instructions = total_instructions - int(overallTree["instruction_mix"]["total"])
	overallTree["instruction_mix"]["integer_alu"] = int(overallTree["instruction_mix"]["integer_alu"]) - extra_instructions
	overallTree["instruction_mix"]["load"] = int(overallTree["instruction_mix"]["load"]) - extra_instructions
	codeGen.insMix = {str(k): float(v) / float(overallTree["instruction_mix"]["total"]) for k, v in overallTree["instruction_mix"].items()}
	codeGen.insMix["total"] = int(overallTree["instruction_mix"]["total"])
	printV(3, "input insmix:", overallTree["instruction_mix"])
	codeGen.insMix["load_alu"] = float(extra_instructions) / float(overallTree["instruction_mix"]["total"])
	rawSum = sum([int(v) for k, v in overallTree["raw"].items()]) - int(overallTree["raw"]["33"])
	codeGen.raw = {int(k): float(v) / float(rawSum) for k, v in overallTree["raw"].items()}
	del codeGen.raw[33]
	codeGen.rawRatio = rawSum / float(overallTree["instruction_mix"]["total"])
	codeGen.stride = {int(k): int(v) for k, v in overallTree["stride_dens"].items()}
	#TBD - localstrides temporarily commented out
	#localStrideSum = sum([int(v) for v in overallTree["local_stride_dens"].values()])
	codeGen.localStride = {int(k): int(v) for k, v in overallTree["local_stride_dens"].items()}
	codeGen.LocalStride = int(overallTree["dominant_local_stride"])
	codeGen.staticBbls = int(overallTree["static_basic_block_count"])
	#codeGen.staticBbls = 100
	codeGen.dynamicBbls = int(overallTree["dynamic_basic_block_count"])
	codeGen.avrBblSize = float(overallTree["avr_basic_block_size"])
	# codeGen.avrBblSize = float(total_instructions) / float(overallTree["instruction_mix"]["branch"])
	codeGen.avrSuccBbls = float(overallTree["avr_number_succ_bbl"])
	codeGen.brTrans = float(overallTree["branch_transitions"]) / float(overallTree["instruction_mix"]["branch"])
	codeGen.dataFootprint = int(overallTree["data_footprint"])
	return codeGen

FAIL = True
parser = optparse.OptionParser()
parser.add_option("--configFile", help="SFG and overall data in JSON format", metavar="FILE", dest="configFileName")
parser.add_option("-o", "--syntheticOutputFile", help="output C file for generated code", metavar="FILE", default="codegen.c", dest="outFileName")
parser.add_option("--inputFormat", help="format of input file (default=json)", default="json", dest="inputFormat")
parser.add_option("--isa", help="ISA to generate code for", default="x86", dest="isa")
parser.add_option("--bblGenerator", help="method for generating bbls (default = statistical)", default="statistical", dest="bblGenerator")
parser.add_option("--verbose", help="level of debug information printed out (0-3)", metavar="N", default=0, dest="verbose")
(options, args) = parser.parse_args()

setVerbosity(options.verbose)

if not len(args) <= 0 and not options.configFileName:
	parser.error("configuration json File required (python SyntheticGenerator.py <configuation json File>")

configFile = open(options.configFileName, "r")
configTree = json.loads(configFile.read())

if options.isa == "x86":
	codeGenerator = CodeGenerator_x86()
	# if options.bblGenerator == "statistical":
	# 	bblGenerator = bblGenerator_stat_x86()
else:
	parser.error("ISA for output code not recognized. (default x86)")

bblGenerator = BblGenerator()

codeGenerator = jsonToGenerator(codeGenerator, configTree["overall"])

codeGenerator.bblGenerator = bblGenerator

rtnval = codeGenerator.generateBbls()
if rtnval == FAIL:
	sys.error("generateBbls function failed in codeGenerator")

rtnval = codeGenerator.generateBranchBehavior()
if rtnval == FAIL:
	sys.error("generateBranchBehavior function failed in codeGenerator")

rtnval = codeGenerator.assignStrides()
if rtnval == FAIL:
        sys.error("assignStrides function failed in codeGenerator")

codeGenerator.generateRawRemoveDens()

rtnval = codeGenerator.assignDependencies()
if rtnval == FAIL:
	sys.error("assignDependencies function failed in codeGenerator")

#rtnval = codeGenerator.assignStrides()
#if rtnval == FAIL:
#	sys.error("assignStrides function failed in codeGenerator")



maxArrOffset = 0
for arr in range(len(codeGenerator.maxArrOffset)):
	if(codeGenerator.maxArrOffset[arr] > maxArrOffset) :
		maxArrOffset = codeGenerator.maxArrOffset[arr]
printV(3, "Max array offset is ", maxArrOffset)

minArrOffset = 0
for arr in range(len(codeGenerator.minArrOffset)):
        if(codeGenerator.minArrOffset[arr] < minArrOffset) :
                minArrOffset = codeGenerator.minArrOffset[arr]
if minArrOffset < 0:
	minArrOffset = -minArrOffset
printV(3, "Min array offset is ", minArrOffset)

scale_datafootprint = 1
iterations = int(float(codeGenerator.dataFootprint - maxArrOffset - minArrOffset) / float(codeGenerator.LocalStride) + 0.5) * int(scale_datafootprint)
#iterations = int(float(codeGenerator.dataFootprint - maxArrOffset - minArrOffset) / float(sum([abs(x) for x in codeGenerator.avail_arr_strides]))) * int(scale_datafootprint)

"""output code"""
code = []
code.append ("/*************")
code.append ("File created on "+str(datetime.datetime.now()))
code.append("input file: " + options.configFileName)
code.append("input statistics")
code.append("****************/")
code.append("#include<stdio.h>")
code.append("#define MAX 255*1024 + 252*1024")
code.append("#define ITERATIONS " + str(iterations)) # DOTO: find new approach to determining iterations
# printV(3, min([thisOff[1] for thisOff in Strides.offset.items()]))
# code.append("#define OFFSET " + str(-1 * min([thisOff[1] for thisOff in Strides.offset.items()])))
# code.append ("int X[ITERATIONS * " + str(max([thisStride[0] for thisStride in Strides.register.items()])) + " + OFFSET];")
#code.append("char X[" + str(codeGenerator.dataFootprint) + "];")
arr_ct = 0
for arr in range(len(codeGenerator.array_used_list)):
        if(codeGenerator.array_used_list[arr] == 1) or (arr_ct < codeGenerator.numAvailableArrays) :
                code.append("char X" + str(arr_ct) + "[" + str(codeGenerator.dataFootprint) + "];")
                arr_ct += 1

code.append ("void main (void)  {")
# code.append ("int i;")
# dummy_string = "register int "
# dummy_string += ", ".join(depR) + ", "
# dummy_string += ", ".join(indR) + ", "
# dummy_string += ", ".join(brR)
# dummy_string += ";"
# code.append(dummy_string)
# dummy_string = "register long "
# dummy_string += ", ".join([thisReg[1] for thisReg in Strides.register.items()])
# dummy_string += ";"
# code.append(dummy_string)
# code.append("for (i=0;i<ITERATIONS;i++) {")
# for stride in Strides.register.items():
# 	code.append(str(stride[1]) + " = &X[i * " + str(stride[0]) + " + OFFSET];")
# code.append("__asm__ __volatile__ (")

# take generated assembly code from codeGenerator and embed it in output file
code.append(codeGenerator.generateCode())

# code.append(":::\"memory\", \"cc\", ")
# code.append("\"" + "\", \"".join(indR) + "\",")
# code.append("\"" + "\", \"".join(depR) + "\",")
# code.append("\"" + "\", \"".join(brR) + "\",")
# code.append("\"" + "\", \"".join([thisReg[1] for thisReg in Strides.register.items()]) + "\"")
# code.append(");")
code.append("}")
# code.append("}")

outFile = open(options.outFileName, "w")
outFile.write("\n".join(code))

outFile.close()
configFile.close()

printV(3, "Done")
