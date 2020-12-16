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

from BasicBlock import *
from Instruction import *
from Registers import *
from VerbosePrint import *
from collections import deque
from Memory import *
from Memory_HALO import Memory_HALO
from Branch import BranchBehaviors
import random
import datetime
# import optparse       # optparse is officially deprecated since python 2.7
import argparse         # actively maintained successor to optparse
import json
import copy
import sys
import os

insMixRemoveDens = {"load": 5, "store": 2, "integer_alu": 6}
rawRemoveDens = {1: 7, 2: 2}

globalStrideRemoveDens = {-12: 1, 12: 1, 0: 3, 256: 2}
localStrideRemoveDens = {0: 7}

def remove(dens, removeDens):
        for key in removeDens.keys():
                if dens.has_key(key):
                                if dens[key] >= removeDens[key]:
                                        dens[key] -= removeDens[key]
                                        removeDens[key] = 0
                                else:
                                        removeDens[key] -= dens[key]
                                        dens[key] = 0
                if removeDens[key] > 0:
                        for x in range(1, max([key, 33 - key])):
                                newKey = key + x
                                if dens.has_key(newKey):
                                        if dens[newKey] >= removeDens[key]:
                                                dens[newKey] -= removeDens[key]
                                                removeDens[key] = 0
                                                continue
                                        else:
                                                removeDens[key] -= dens[newKey]
                                                dens[newKey] = 0
                                newKey = key - x
                                if dens.has_key(newKey):
                                        if dens[newKey] >= removeDens[key]:
                                                dens[newKey] -= removeDens[key]
                                                removeDens[key] = 0
                                                continue
                                        else:
                                                removeDens[key] -= dens[newKey]
                                                dens[newKey] = 0
        return dens
"""
def removeStrides(dens, removeDens):
        for key in removeDens.keys():
                if key == 0:
                        if dens.has_key(0):
                                if dens[0] >= removeDens[key]:
                                        dens[0] -= removeDens[key]
                                        removeDens[key] = 0
                                else:
                                        removeDens[key] -= dens[0]
                                        dens[0] = 0
                else :
                        if dens.has_key(key):
                                if dens[key] >= removeDens[key]:
                                        dens[key] -= removeDens[key]
                                        removeDens[key] = 0
                                else:
                                        removeDens[key] -= dens[key]
                                        dens[key] = 0
                        if dens.has_key(-1 * key):
                                if dens[-1 * key] >= removeDens[key]:
                                        dens[-1 * key] -= removeDens[key]
                                        removeDens[key] = 0
                                else:
                                        removeDens[key] -= dens[-1 * key]
                                        dens[-1 * key] = 0
        return dens
"""
def nearest_idx(array, value):
        array = np.asarray(array)
        return (np.abs(array - value)).argmin()

class CodeGenerator_x86( Memory_ZL, Memory_MA, Memory_ZS, Memory_HALO, BranchBehaviors ):
        memBlockSize = 256
        MAX_OFFSET = 32768

        def __init__(self):
                self.registers = Registers_x86("64bit")
                self.bblList = []
                self.insList = []
                self.insMix = None
                self.raw = None
                self.stride = None
                self.staticBbls = None
                self.dynamicBbls = None
                self.avrBblSize = None
                self.avrSuccBbls = None
                self.brTrans = None
                self.dataFootprint = None
                self.dominantStride = None
                self.localStride
                # super(CodeGenerator_x86).__init__()
                self.array_used_list = []
                self.minArrOffset = []
                self.maxArrOffset = []  
                self.numAvailableArrays = None
                self.mem_model = None
                self.has_local_branch_info = False
                self.local_branches = []
		self.has_branch_correlation_info = False
		self.branch_correlations = []
                self.branch_model = None
		self.trace_file = None
                self.linked_list = None
		self.llstr = ""
		self.ll_starts = []
                self.ll_json = None
		self.global_taken_rate = None

        def __init__(self, options):
                """Example function with PEP 484 type annotations.

            Args:
                options: a collection of options from parsing command line.
                Used primarily to specify the JSON file that has many settings
        
            Returns:
                An instanse of the CodeGenerator class based on the settings
                """
                self.registers = Registers_x86("64bit")
                self.bblList = []
                self.insList = []
                self.array_used_list = []
                self.minArrOffset = []
                self.maxArrOffset = []  
                self.numAvailableArrays = None
                self.mem_model = options.mem_model
                self.branch_model = options.branch_model
                self.has_local_branch_info = False
                self.local_branches = []
		self.has_branch_correlation_info = False
		self.branch_correlations = []
		self.trace_file = None
                self.linked_list = None
                self.multi_region = None
		self.llstr = ""
		self.ll_starts = []
                self.ll_json = None
		self.global_taken_rate = None

		if self.mem_model == "HALO":
			self.trace_file = options.traceFileName
                        self.linked_list = options.linked_list
                        self.multi_region = options.mem_multi_region
                        self.ll_json = options.ll_json
                        print("Linked list file name is: ",options.linked_list)
                
                        #Need to iterate on this more
                        memConfigFile = open(self.ll_json, "r")
                        memConfigTree = json.loads(memConfigFile.read())
                        self.ll_data = memConfigTree
                        memConfigFile.close()
                        mem_pretty_str = json.dumps(memConfigTree, indent=2)
                        #print(mem_pretty_str)
                        #print(memConfigTree["region3"]["array_store_ratio"])
                        #exit()

                 #converting the JSON file into a configTree
                configFile = open(options.configFileName, "r")
                configTree = json.loads(configFile.read())
                configFile.close()
                

                overallTree = configTree["overall"]

                #This command line option allows us to force the proxy
                #to produce identical outputs every time
                if options.seed != None:
                        #seed(int(options.seed))
                        random.seed(options.seed)

                total_instructions = float(0)   
                for k, v in overallTree["instruction_mix"].items():
                        if str(k) != "total" and str(k) != "load" and str(k) != "store":
                                total_instructions += float(v)
                # alternate option for computing otal instructions

                # total_instructions = overallTree["instruction_mix"]["total"]
                printV(3, "actual total instructions is ", total_instructions )
        
                #correcting loads and int_alu by extra instruction
		printV(3, "Before removing the extra instructions", overallTree["instruction_mix"])
                extra_instructions = total_instructions - int(overallTree["instruction_mix"]["total"])
		#Steven 6/7/19: This solution for extra instruction seems incorrect, gating on if number stays positive
                #Steven 7/10/19: New solution is to handle memory ops at the operand level
		#if int(overallTree["instruction_mix"]["integer_alu"]) > extra_instructions:
			#overallTree["instruction_mix"]["integer_alu"] = int(overallTree["instruction_mix"]["integer_alu"]) - extra_instructions
			#overallTree["instruction_mix"]["load"] = int(overallTree["instruction_mix"]["load"]) - extra_instructions
                #Adding a check if the extra instructions are greater than 10% of the total instructions
                if extra_instructions * 10 > overallTree["instruction_mix"]["total"]:
                        sys.error("Too many unaccounted for instructions")
                        exit(1)

                #8/13/19 Steven: removed the code because new implementation
                #does not count memory instructions in the total, similiar to the profiler
                #overallTree["instruction_mix"]["total"] = float(overallTree["instruction_mix"]["total"])
                #overallTree["instruction_mix"]["total"] -= float(overallTree["instruction_mix"]["load"])
                #overallTree["instruction_mix"]["total"] -= float(overallTree["instruction_mix"]["store"])
                if False: #This hack was to allow workloads to function for SimTrace, no longer needed
                        overallTree["instruction_mix"]["total"] -= float(overallTree["instruction_mix"]["integer_div"])
                        overallTree["instruction_mix"]["total"] -= float(overallTree["instruction_mix"]["fp_div"])
                        #overallTree["instruction_mix"]["total"] -= float(overallTree["instruction_mix"]["fp_alu"])
                        #overallTree["instruction_mix"]["total"] -= float(overallTree["instruction_mix"]["fp_mul"])
                        overallTree["instruction_mix"]["integer_div"] = 0
                        overallTree["instruction_mix"]["fp_div"] = 0
                        #overallTree["instruction_mix"]["fp_alu"] = 0
                        #overallTree["instruction_mix"]["fp_mul"] = 0
                        
                        
                #Scaling down to percentages

		self.global_taken_rate = float(overallTree["branch_taken"]) / float(overallTree["instruction_mix"]["branch"])

                self.insMix = {str(k): float(v) / float(overallTree["instruction_mix"]["total"]) for k, v in overallTree["instruction_mix"].items()}
                self.insMix["total"] = int(overallTree["instruction_mix"]["total"])
                printV(3, "input insmix after removing extra instructions:", overallTree["instruction_mix"])

                #Steven 7/10/19 no longer need a load alu, will instead insert mem ops as needed
                #self.insMix["load_alu"] = float(extra_instructions) / float(overallTree["instruction_mix"]["total"])
                

                rawSum = sum([int(v) for k, v in overallTree["raw"].items()]) - int(overallTree["raw"]["33"])
                self.raw = {int(k): float(v) / float(rawSum) for k, v in overallTree["raw"].items()}
                del self.raw[33]
                self.rawRatio = rawSum / float(overallTree["instruction_mix"]["total"])
		self.stride = {int(k): int(v) for k, v in overallTree["stride_dens"].items()}
                #TODO - localstrides temporarily commented out
                #localStrideSum = sum([int(v) for v in overallTree["local_stride_dens"].values()])
                self.localStride = {int(k): int(v) for k, v in overallTree["local_stride_dens"].items()}
                self.dominantStride = int(overallTree["dominant_local_stride"])
                self.staticBbls = int(overallTree["static_basic_block_count"])
                #self.staticBbls = 100
                self.dynamicBbls = int(overallTree["dynamic_basic_block_count"])
                self.avrBblSize = float(overallTree["avr_basic_block_size"])
                # self.avrBblSize = float(total_instructions) / float(overallTree["instruction_mix"]["branch"])
                self.avrSuccBbls = float(overallTree["avr_number_succ_bbl"])
                self.brTrans = float(overallTree["branch_transitions"]) / float(overallTree["instruction_mix"]["branch"])
                self.dataFootprint = int(overallTree["data_footprint"])
                self.bblGenerator = BblGenerator()
                
                if "local_branch_bins" in overallTree:
			printV(4, "Found local branch taken/transition data")
                        self.has_local_branch_info = True
		if all("correlations" in local_branch for local_branch in overallTree["local_branch_bins"]):
			printV(4, "Found local branch correlation data")
			self.has_branch_correlation_info = True
		elif any("correlations" in local_branch for local_branch in overallTree["local_branch_bins"]):
			# you tried to modify a JSON by hand, didn't you?
			sys.error("Correlation data present for some but not all branches. How did that even happen?")
			# anyway, it's nonfatal in of itself
		for branch_idx, local_branch in enumerate(overallTree["local_branch_bins"]):
		    	if self.has_local_branch_info:
				branch_count, taken_count, transition_count = [int(local_branch[x]) for x in ["encountered", "taken", "transitions"]]
				self.local_branches.append([branch_count, taken_count/float(branch_count), transition_count/float(branch_count)])
			if self.has_branch_correlation_info:
				self.branch_correlations.append(local_branch["correlations"])

        def generateBbls(self):
                """We use the profile information to generate basic blocks
        
                    Args:
                No arguments are needed 

                    Returns:
                No return arguments

                """
                printV(3, self.__class__.__name__)
                stdev = self.avrBblSize / 8.0
                printV(3, "avrBblSize", self.avrBblSize)
                printV(3, "staticBbls", self.staticBbls)
                totalIns = 0
                #generating the list of basic blocks for the proxy
                for n in range(self.staticBbls):        
                        size = float(((self.avrBblSize * self.staticBbls) - sum(insMixRemoveDens.values())) / self.staticBbls)
                        size = int(random.gauss(size, stdev) + 0.5)
                        totalIns += size
                        printV(3, "bbl", n, "size", size)
                        newBbl = self.bblGenerator.nextBbl(size)
                        self.bblList.append(newBbl)

                #Generating instruction distribution to sample from
                insGenerator = InsGenerator(self.insMix, totalIns + sum(insMixRemoveDens.values()))
                insGenerator.remove("integer_alu", self.staticBbls)
                for key in insMixRemoveDens.keys():
                        insGenerator.remove(key, insMixRemoveDens[key])
                insGenerator.shuffle()
                self.bblGenerator.insGenerator = insGenerator
                for bbl in self.bblList:
                        bbl.fillIns(insGenerator)
                        self.insList.extend(bbl.insList)
                # printV(3, "leftover instructions", [str(ins) for ins in insGenerator.insList])
                del self.insList[-1]
                del self.bblList[-1].insList[-1]
                if len(self.insList) < len(insGenerator.insList):
                        printV(3, "WARNING: generated fewer instructions than expected. wrong ins mix.")
                for bblI in range(len(self.bblList)):
                        for insI in range(len(self.bblList[bblI].insList)):
                                self.bblList[bblI].insList[insI].label = "BBL" + str(bblI) + "INS" + str(insI)
                                if self.bblList[bblI].insList[insI].insType == "branch":
                                        self.bblList[bblI].insList[insI].ptr = "BBL" + str(bblI + 1) + "INS0"
                printV(3, "len on insList:", len(self.insList))
                return False

        def generateRawRemoveDens(self):
                """Calculates the raw removes dens that are less than 32, aka any mem instructions that show up early
        
                    Args:
                Takes in the list of memory instructions

                    Returns:
                An updated rawRemoveDens accounting for early memory instructions

                """
                printV(3, "In generateRawRemoveDens, before")
                printV(3, rawRemoveDens)

                for x in range(min(32, len(self.insList))):
                        if self.insList[x].insType == "branch_test" and (x + self.numAvailableArrays + 1) <= 32:
                                if rawRemoveDens.has_key(x + self.numAvailableArrays + 1):
                                        rawRemoveDens[x + self.numAvailableArrays + 1] += 1 #Steven: this calculation is likely wrong
                                else:
                                        rawRemoveDens[x + self.numAvailableArrays + 1] = 1
                        for operand in self.insList[x].operands:
                                if operand.isMem() and self.mem_model != "HALO":   #Steven: reg_raw_dist is likely wrong
                                        printV(3, "Memory Model is: ", self.mem_model)
                                        printV(3, operand.reg)
                                        if not (operand.reg == self.registers.zeroStrideR[0]):
                                                reg_idx = self.registers.strideR.index(operand.reg)     
                                                reg_raw_dist = self.numAvailableArrays - reg_idx
                                                if rawRemoveDens.has_key(x + reg_raw_dist):
                                                        rawRemoveDens[x + reg_raw_dist] += 1
                                                else:
                                                        rawRemoveDens[x + reg_raw_dist] = 1

                printV(3, "In generateRawRemoveDens")
                printV(3, rawRemoveDens)

        def assign(self, regDepIndex, reg, start, end):
                for x in range(start + 1, end + 1, -1):
                        if reg not in regDepIndex[x]:
                                regDepIndex[x].append(reg)

        def isAssigned(self, regDepIndex, reg, start, end):
                for x in range(start + 1, end + 1, -1):
                        for blockList in regDepIndex[x]:
                                if reg in blockList:
                                        return True
                return False

        def nextReg(self, regDepIndex, regType, start, end):
                if regType == "intDepR":
                        for reg in self.registers.intDepR:
                                if not self.isAssigned(regDepIndex, reg, start, end):
                                        self.assign(regDepIndex, reg, start, end)
                                        return reg
                        # printV(3, "WARNING: reusing register", self.registers.intDepR[0])
                        # self.assign(regDepIndex, self.registers.intDepR[0], start, end)
                        printV(3, "WARNING: all registers blocked")
                        return None
                elif regType == "fpDepR":
                        for reg in self.registers.fpDepR:
                                if not self.isAssigned(regDepIndex, reg, start, end):
                                        self.assign(regDepIndex, reg, start, end)
                                        return reg
                        # printV(3, "WARNING: reusing register", self.registers.fpDepR[0])
                        # self.assign(regDepIndex, self.registers.fpDepR[0], start, end)
                        printV(3, "WARNING: all registers blocked")
                        return None
                else:
                        sys.error("ERROR: no reg type " + str(regType))
                        return None



        def canBeAssigned(self, ins, operand, ll=False):
                """
                This helper functions checks whether an operand can be assigned
                1/24/20 Steven: Only move instructions can read from memmory now
                """
                #Checking if instruction has already accessed memory
                if ins.memAccess:
                        return False

                #Checking if instruction type is okay for memory operands
                if ins.insType == "branch_test" or ins.insType == "integer_div":
                        return False

                #Certain Instructions cannot write to memory, only read
                if operand.isRegWrite() and (ins.insType == "fp_mul" or ins.insType == "integer_mul" or ins.insType == "fp_alu"):
                        return False
                #We cannot modify implicit registers
                if operand.visibility == "implicit":
                        return False
                
                #return True
                #1/24/20 Steven For linked lists, only mov instructions can read from memory
                if self.mem_model != "HALO" or ll == False:
                        return True
                if (ins.insType == "other" and (not operand.isRegWrite())):
                        return True
                if operand.isRegWrite():
                        return True


        def assignMemOps(self):
                """Use the profile data to certain operands as memory read and writes
                Note that the current version ignores information about the number of mem-ops per instruction
                Currently all profiles only tell us the number of instructions that access memory
        
                    Args:
                An instruction list for the proxy
                Profile data on percentage of instructions that read or write to memory

                    Returns:
                Updated instruction list that includes memory operands

                """
                target_loads = self.insMix["load"] * len(self.insList)
                target_stores = self.insMix["store"] * len(self.insList)
                print("Percentage loads " + str(self.insMix["load"]) + " % stores: " + str(self.insMix["store"]))
                print("Loads: " + str(target_loads) + " Stores: " + str(target_stores) + " AllIns: " + str(len(self.insList)))
                num_loads = 0
                num_stores = 0

                #assigning all stores first under the assumption that there are more reads than writes
                #1/24/20 Steven: Removed writes from code base to allow for linked list functionality
                #4/20/20 Steven: Bringing Writes back in
                while num_stores < target_stores:
                        for ins in self.insList:
                                for operand in ins.operands:
                                        if self.canBeAssigned(ins, operand):
                                                test = random.randint(0,len(self.insList))
                                                if operand.rw == "rw" and num_loads < target_loads and num_stores < target_stores:
                                                        if test < target_loads and test < target_stores:
                                                                printV("RW", 3)
                                                                operand.reg = None
			                                        operand.offset = None
                                                                operand.operandType = "mem"
                                                                num_loads += 1
                                                                num_stores +=1
                                                                ins.memAccess = True
                                                elif operand.rw == "w" and num_stores < target_loads: 
                                                        if  test < target_stores:
                                                                printV("Write", 3)
                                                                operand.reg = None
                                                                operand.offset = None
                                                                operand.offset_reg = None
                                                                operand.offset_scale = None
                                                                operand.operandType = "mem"
                                                                num_stores +=1
                                                                ins.memAccess = True

                attempts = 0
                while num_loads < target_loads and attempts < 100:
                        attempts = attempts + 1
                        for ins in self.insList:
                                for operand in ins.operands:
                                        if self.canBeAssigned(ins, operand, ll=True):
                                                test = random.randint(0,len(self.insList))
                                                if operand.rw == "r" and num_loads < target_loads:
                                                        if test < target_loads:
                                                                printV(3, "Read")
                                                                operand.reg = None
                                                                operand.offset = None
                                                                operand.offset_reg = None
                                                                operand.offset_scale = None
                                                                operand.operandType = "mem"
                                                                ins.ll = True #This tells generator to hold the other register
                                                                num_loads += 1
                                                                ins.memAccess = True

                while num_loads < target_loads:
                        for ins in self.insList:
                                for operand in ins.operands:
                                        if self.canBeAssigned(ins, operand, ll=False):
                                                test = random.randint(0,len(self.insList))
                                                if operand.rw == "r" and num_loads < target_loads:
                                                        if test < target_loads:
                                                                printV(3, "Read")
                                                                operand.reg = None
                                                                operand.offset = None
                                                                operand.offset_reg = None
                                                                operand.offset_scale = None
                                                                operand.operandType = "mem"
                                                                num_loads += 1
                                                                ins.memAccess = True

                if attempts == 100:
                        printV(3, "Failed to assign all mem ops")
                        printV(3, "Target number of loads: ", target_loads)

                printV(3, "Memory operations successfully assigned")
                printV(3, "Number of loads: " +str(num_loads) + " Number of stores: " + str(num_stores))

                                                



                

        def assignDependencies(self):
                """Use the profile data to assign register dependencies
        
                    Args:
                No arguments are needed 

                    Returns:
                No return arguments

                """
                totalRaws = int(self.rawRatio * len(self.insList))
		#rawsPerIns = int(self.rawRatio + 0.5) 6/14/19 this ratio is useless and not needed
		rawDens = {k: int(v * totalRaws) for k, v in self.raw.items()}
                printV(3, "raw before removal:", rawDens)
                printV(3, "rawRemoveDens:", rawRemoveDens)
                remove(rawDens, rawRemoveDens)
                # regDepIndex = {}
                foundBr = False
                printV(3, "raw percentages:", self.raw)
                printV(3, "raw after removal:", rawDens)
                totalRaws = sum(rawDens.values())
                printV(3, sum(rawDens.values()), "to be assigned.")
                # printV(3, "First Pass done - debug")
                totalReg = 0
                trials = 0
                regDepIndex = [[] for x in range(len(self.insList))]
                while (sum(rawDens.values()) > 0) and trials < 10:
                        trials += 1
                        printV(3, "trials:", trials)
                        rInsList = copy.copy(self.insList)
                        rInsList.reverse()
                        for ins in rInsList:
                                #numRawsApplied = rawsPerIns #never used
                                for operand in ins.operands:
                                        if trials == 1:
                                                if operand.isRegRead() or operand.isRegWrite() and operand.reg not in self.registers.index: #2/11 Trying to stop R10 from being used in this algorithm
                                                        totalReg += 1
                                        if ((operand.isRegRW()) if (trials == 1) else (operand.isRegRead() and not operand.isRegAssigned())): #Why is this if statement so difficult?
                                                #Trying to stop r10 from being used
                                                if operand.reg in self.registers.index:
                                                        break
                                                found_raw = False
                                                rawTrials = 0
                                                while rawTrials <= 30:
                                                        rawTrials += 1
                                                        num = random.random()
                                                        for i in self.raw.keys():
                                                                num -= self.raw[i]
                                                                if num <= 0:
                                                                        break
                                                        tempRaw = i
                                                        tempN = self.insList.index(ins) - tempRaw
                                                        if tempN >= 0:
                                                                found_raw = True
                                                                break
                                                if rawTrials == 30 and found_raw == False:
                                                        break
                                                
                                                thisRaw = tempRaw
                                                start = self.insList.index(ins)
                                                printV(3, "start:", start)
                                                end = start - thisRaw
                                                if end < 0:
                                                        break

                                                breakAll = False
                                                for x in range(30):
                                                        if rawDens.has_key(thisRaw) and rawDens[thisRaw] != 0:
                                                                for wOperand in self.insList[end].operands:
                                                                        if wOperand.isRegWrite() and wOperand.regType == operand.regType and wOperand.reg not in self.registers.index:
                                                                                if not wOperand.isRegAssigned() and not operand.isRegAssigned():
                                                                                        if "fp" in ins.insType:
                                                                                                wOperand.reg = operand.reg = self.nextReg(regDepIndex, "fpDepR", start, end)
                                                                                        else:
                                                                                                wOperand.reg = operand.reg = self.nextReg(regDepIndex, "intDepR", start, end)
                                                                                elif wOperand.isRegAssigned() and not operand.isRegAssigned():
                                                                                        operand.reg = wOperand.reg
                                                                                        self.assign(regDepIndex, wOperand.reg, start, end)
                                                                                elif not wOperand.isRegAssigned() and operand.isRegAssigned():
                                                                                        if not self.isAssigned(regDepIndex, operand.reg, end, start):
                                                                                                wOperand.reg = operand.reg
                                                                                                self.assign(regDepIndex, operand.reg, start, end)
                                                                                        else:
                                                                                                break
                                                                                else:
                                                                                                break
                                                                                #numRawsApplied -= 1
                                                                                if rawDens[thisRaw] != 0:
                                                                                        rawDens[thisRaw] -= 1
                                                                                breakAll = True
                                                                                printV(3, "assigned raw", thisRaw)
                                                                                break
                                                        if breakAll:
                                                                break
                                                        end -= 1
                                                        thisRaw += 1
                                                        if end <= 0:
                                                                break
                                if sum(rawDens.values()) <= 0:
                                        break

                tIndR = 0
                tIndW = 0
                tIndRW = 0
                rInsList = copy.copy(self.insList)
                rInsList.reverse()
                foundBr = False
                for ins in rInsList:

                        if ins.insType == "branch" or ins.insType == "branch_test":
                                continue

                        for operand in ins.operands:
                                if not operand.isRegAssigned():
                                        if operand.isRegRW():
                                                tIndRW += 1
                                                if "fp" in ins.insType:
                                                        operand.reg = self.registers.nextAvailReg("fpDepR")
                                                else:
                                                        operand.reg = self.registers.nextAvailReg("intDepR")
                                        elif operand.isRegRead():
                                                tIndR += 1
                                                if "fp" in ins.insType:
                                                        operand.reg = self.registers.fpIndR[0]
                                                else:
                                                        operand.reg = self.registers.intIndR[0]
                                        elif operand.isRegWrite():
                                                tIndW += 1
                                                if "fp" in ins.insType:
                                                        operand.reg = self.registers.fpIndR[1]
                                                else:
                                                        operand.reg = self.registers.intIndR[1]
                printV(3, totalReg, "registers are available.")
                printV(3, "raw's were overwritten", self.registers.numRedundancies, "times.")
                printV(3, sum(rawDens.values()), "/", totalRaws, "raws were not assigned.")
                printV(3, tIndR, "registers are read independent.")
                printV(3, tIndW, "registers are write independent.")
                printV(3, tIndRW, "register are rw independent.")
                return False


        def generateCode(self, options, iterations):
                """We use the bblList and insList to generate c code
        
                    Args:
                No arguments are needed 

                    Returns:
                No return arguments

                """

		vectorized_branch_models = ["v4_local", "v5_correlation"]

                string = "int i;\n"
                string += "int j;\n"

		if True or self.mem_model in ["ZL", "ZS", "MA"]:
		    arr_ct = 0
		    for arr in range(len(self.array_used_list)):
			    if(self.array_used_list[arr] == 1) or (arr_ct < self.numAvailableArrays):
				    string += "char* ptr" + str(arr_ct) + ";\n"
				    arr_ct += 1

		if self.mem_model == "HALO":
			# Define a series of macros used to repeat specified character(s) between 0 and 99,999,999,999 times (reduces source code size)
                        """
                        All of this functionality is now included in the header file
			string += "#define REP0(...)\n"
			string += "#define REP1(...) __VA_ARGS__\n"
			string += "#define REP2(...) REP1(__VA_ARGS__) __VA_ARGS__\n"
			string += "#define REP3(...) REP2(__VA_ARGS__) __VA_ARGS__\n"
			string += "#define REP4(...) REP3(__VA_ARGS__) __VA_ARGS__\n"
			string += "#define REP5(...) REP4(__VA_ARGS__) __VA_ARGS__\n"
			string += "#define REP6(...) REP5(__VA_ARGS__) __VA_ARGS__\n"
			string += "#define REP7(...) REP6(__VA_ARGS__) __VA_ARGS__\n"
			string += "#define REP8(...) REP7(__VA_ARGS__) __VA_ARGS__\n"
			string += "#define REP9(...) REP8(__VA_ARGS__) __VA_ARGS__\n"
			string += "#define REP10(...) REP9(__VA_ARGS__) __VA_ARGS__\n"
			string += "#define REPEAT(TB,B,HM,TM,M,HT,TT,T,H,t,O,...) \\\n"
			string += "\tREP##TB\t(REP10(REP10(REP10(REP10(REP10(REP10(REP10(REP10(REP10(REP10(REP10(__VA_ARGS__)))))))))))) \\\n"
			string += "\tREP##B\t(REP10(REP10(REP10(REP10(REP10(REP10(REP10(REP10(REP10(REP10(__VA_ARGS__))))))))))) \\\n"
			string += "\tREP##HM\t(REP10(REP10(REP10(REP10(REP10(REP10(REP10(REP10(REP10(__VA_ARGS__)))))))))) \\\n"
			string += "\tREP##TM\t(REP10(REP10(REP10(REP10(REP10(REP10(REP10(REP10(__VA_ARGS__))))))))) \\\n"
			string += "\tREP##M\t(REP10(REP10(REP10(REP10(REP10(REP10(REP10(__VA_ARGS__)))))))) \\\n"
			string += "\tREP##M\t(REP10(REP10(REP10(REP10(REP10(REP10(__VA_ARGS__))))))) \\\n"
			string += "\tREP##HT\t(REP10(REP10(REP10(REP10(REP10(__VA_ARGS__)))))) \\\n"
			string += "\tREP##TT\t(REP10(REP10(REP10(REP10(__VA_ARGS__))))) \\\n"
			string += "\tREP##T\t(REP10(REP10(REP10(__VA_ARGS__)))) \\\n"
			string += "\tREP##H\t(REP10(REP10(__VA_ARGS__))) \\\n"
			string += "\tREP##t\t(REP10(__VA_ARGS__)) \\\n"
			string += "\tREP##O\t(__VA_ARGS__)\n\n"
			string += "static uint32_t Memory[] = {" + self.llstr + "};\n"
			string += "uint32_t *read_base = &Memory[0];\n"
			string += "uint32_t *write_base = &Memory[1];\n"
			string += "unsigned long long entry_points[] = "

                        string += self.ll_starts + ";\n"
                        Steven 6/1/2020 this code is left over from old linked list generator

                        #x = 0
                        while x < len(self.ll_starts): 

                                start_point = int(self.ll_starts[x])
                                #if start_point % 2 == 1:
                                #        start_point = start_point + 1
                                string += str(start_point)
                                if x < len(self.ll_starts) - 1:
                                        string += ", "
                                x = x + 1
                        string += "};\n\n"
                        """
                        printV(3, "Using header file for information")

                if self.branch_model in vectorized_branch_models:
                        string += "unsigned long vector_low = 0x1;\n"
                        string += "unsigned long vector_high = 0x1;\n"
                #TODO: figure out why this is hardcoded to 5
                if self.mem_model == "HALO":
                        printV(3, "Giving information to proxy for HALO")
                        string += "ptr0 = (char*) ReadBase;\n"
                        string += "ptr1 = (char*) EntryPoints[0];\n"
                        string += "ptr2 = (char*) EntryPoints[1];\n"
                        string += "ptr3 = (char*) EntryPoints[2];\n"
                        string += "ptr4 = (char*) EntryPoints[3];\n"
                        string += "ptr5 = (char*) EntryPoints[4];\n"
                        string += "ptr6 = (char*) EntryPoints[5];\n"

                        


                if options.pinball == True:
                        string += "for (j = 0; j < 1; j++) {\n"
                        string += "for (i = 1; i < " + str(iterations)  + "; i++) {\n"
                else:
                        string += "for (j = 0; j < 5; j++) {\n"
                        string += "for (i = 1; i < ITERATIONS; i++) {\n"
                if self.branch_model in vectorized_branch_models:
                        string += "if (vector_low == 0x80000000){\n"
                        string += "if (vector_high == 0x80000000){\n"
                        string += "vector_high = 0x1;\n"
                        string += "}\n"
                        string += "else{\n"
                        string += "vector_high <<= 1;\n"
                        string += "}\n"
                        string += "vector_low = 0x1;\n"
                        string += "}\n"
                        string += "else{\n"
                        string += "vector_low <<= 1;\n"
                        string += "}\n"

                arr_ct = 0
                if self.mem_model != "HALO":
                        for arr in range(len(self.array_used_list)):
                                if(arr_ct < self.numAvailableArrays) :
                                        string += "ptr" + str(arr_ct) + " = (char*) &X" + str(arr_ct) + "[" + str(self.dominantStride) + " * i + " + str(-1 * self.minArrOffset[arr_ct]) + "];\n" #\ string += "ptr = (int*) &X[" + str(CodeGenerator.MAX_OFFSET) + " * i];\n" Older Version
                                #string += "ptr" + str(arr_ct) + " = (char*) &X" + str(arr_ct) + "[" + str(self.avail_arr_strides[arr_ct]) + " * i + " + str(-1 * self.minArrOffset[arr_ct]) + "];\n" # Newer version
                                arr_ct += 1

                #       + str(self.dataFootprint - CodeGenerator_x86.MAX_OFFSET) + "];\n"
                string += "__asm__ __volatile__ ("
                string += "\"mov %0, " + self.registers.brR[0] + "\\n\\t\"\n"
                string += "\"mov $-2, " + self.registers.constant[0] + "\\n\\t\"\n" #Setting constant to a large value
                arr_offset = 1
                if self.branch_model in vectorized_branch_models:
                        string += "\"mov %1, " + self.registers.brR[1] + "\\n\\t\"\n"
                        arr_offset = 2
                arr_ct = 0
                for arr in range(len(self.array_used_list)):
                        if(arr_ct < self.numAvailableArrays):
                                string += "\"mov %" + str(arr_ct+arr_offset) + ", " + self.registers.strideR[arr_ct] + "\\n\\t\"\n"
                                arr_ct += 1
                for ins in self.insList:
                        string += "\"" + str(ins) + "\\n\\t\"\n"
                printV(3, "Array used list length {}".format(len(self.array_used_list)))
                printV(3, "Available Arrays {}".format(self.numAvailableArrays))
                if self.mem_model == "HALO":
                        arr_ct = 2
                        for arr in range(2, len(self.array_used_list)):
                                if(arr_ct < self.numAvailableArrays):
                                        printV(3, "Adding a mov instruction")
                                        string += "\"mov " + self.registers.strideR[arr_ct]  + ", %" + str(arr_ct+arr_offset) +  "\\n\\t\"\n"
                                        arr_ct += 1

                # string += "\"add $1, " + self.registers.strideR[0] + "\\n\\t\"\n"
                # string += "\"cmp 200(%1), " + self.registers.strideR[0] + "\\n\\t\"\n"
                # string += "\"jnz BBL0INS0\\n\\t\"\n"
                if self.branch_model in vectorized_branch_models:
                        string += "::" + "\"m\"(vector_low)" + ", \"m\"(vector_high)"
                else:
                        string += "::" + "\"m\"(i)"   #\"m\"(ptr)" + ":\"memory\", \"cc\", "
                ptrstring = ""
                arr_ct = 0
                printV(3, "debug - range of self.array_used_list is ", len(self.array_used_list))

                for arr in range(len(self.array_used_list)):
                        if(arr_ct < self.numAvailableArrays):
                                ptrstring += ", \"m\"(ptr" + str(arr_ct) + ")"
                                arr_ct += 1
                string += ptrstring
                string += ":\"memory\", \"cc\", "
                regString = "\"" + "\", \"".join(self.registers.allRegs()) + "\""
                regString = regString.replace("%", "")
                string += regString
                string += ");\n"
                string += "}"
                string += "}"
                return string


        def Generate_Proxy(self):
                """We generate a proxy based on the configurations input to this codegenerator
                
                    Args:
                No arguments are needed, all configurations are already in class variables 
                
                    Returns:
                Nothing returned, bblList and insList are filled according to the profile
                
                """
                FAIL = True
                rtnval = self.generateBbls()
                if rtnval == FAIL:
                        sys.error("generateBbles funciton failed in codeGenerator")

                if self.branch_model == "v2_legacy":
                        rtnval = self.generateBranchBehavior_v2()
                        if rtnval == FAIL:
                                sys.error("generateBranchBehavior funciton failed in codeGenerator")
                elif self.branch_model == "v3_global":
                        rtnval = self.generateBranchBehavior_v3()
                        if rtnval == FAIL:
                                sys.error("generateBranchBehavior funciton failed in codeGenerator")
                if self.branch_model == "v4_local":
                        rtnval = self.generateBranchBehavior_v4()
                        if rtnval == FAIL:
                                sys.error("generateBranchBehavior funciton failed in codeGenerator")
                if self.branch_model == "v5_correlation":
                        rtnval = self.generateBranchBehavior_v5()
                        #rtnval = "Hi"
                        #print("Just Testing Mem, Skipping Branch")
                        if rtnval == FAIL:
                                sys.error("generateBranchBehavior funciton failed in codeGenerator")


                #assigning the memory operands to instructions
                rtnval = self.assignMemOps()
                
                #7/10/19 Steven: note that memory assignment should work even when there are no memory instructions?
                if self.mem_model == "ZL":
                        rtnval = self.assignStrides_ZL()
                        if rtnval == FAIL:
                                sys.error("assignStrides funciton failed in codeGenerator")
                elif self.mem_model == "ZS":
                        rtnval = self.assignStrides_ZS()
                        if rtnval == FAIL:
                                sys.error("assignStrides funciton failed in codeGenerator")
                elif self.mem_model == "MA":
                        rtnval = self.assignStrides_MA()
                        if rtnval == FAIL:
                                sys.error("assignStrides funciton failed in codeGenerator")
		elif self.mem_model == "HALO":
			rtnval = self.mkLinkedLists_HALO()
                        if rtnval == FAIL:
                                sys.error("mkLinkedLists funciton failed in codeGenerator")
			
			
			# TEMP --- TODO assign these properly
                        #rtnval = self.assignStrides_MA()
			rtnval = self.assignStrides_HALO(self.ll_data)
                        #2/04/20 This is a hack to allow the rest of the code to function
                        self.numAvailableArrays = 7
                        if rtnval == FAIL:
                                sys.error("assignStrides funciton failed in codeGenerator")

                else:
                        #sys.error("Memory model " + self.mem_model + " not recognized")
                        printV("Memory not assigned",3)
                        self.numAvailableArrays = 3


                self.generateRawRemoveDens()

                self.assignDependencies()
                if rtnval == FAIL:
                        sys.error("assignDependencies funciton failed in codeGenerator")



        def Get_Iterations(self, options):
                """Calculates the desired number of iterations
                
                    Args:
                No arguments are needed
                
                    Returns:
                iterations: the number of iterations needed
                
                """

		if self.mem_model == "HALO":
			return 100000000/len(self.insList)

                maxArrOffset = 0
                for arr in range(len(self.maxArrOffset)):
                        if(self.maxArrOffset[arr] > maxArrOffset) :
                                maxArrOffset = self.maxArrOffset[arr]
                printV(3, "Max array offset is ", maxArrOffset)

                minArrOffset = 0
                for arr in range(len(self.minArrOffset)):
                        if(self.minArrOffset[arr] < minArrOffset) :
                                minArrOffset = self.minArrOffset[arr]
                if minArrOffset < 0:
                        minArrOffset = -minArrOffset
                printV(3, "Min array offset is ", minArrOffset)

                scale_datafootprint = 1
                iterations = int(float(self.dataFootprint - maxArrOffset - minArrOffset) / float(self.dominantStride) + 0.5) * int(scale_datafootprint) # Older version

		#import pdb; pdb.set_trace()
                #iterations = int(float(self.dataFootprint - maxArrOffset - minArrOffset) / float(sum([abs(x) for x in self.avail_arr_strides]))) * int(scale_datafootprint) # Newer version
                #10/16/19 found a bug that causes iterations to be negative
                if iterations < 0:
                        iterations = 1
                if options.pinball == True:
                        iterations = (10000000/len(self.insList)) #Aiming to get roughly 100 million total instructions out of the loop
                return iterations


        def Output_Proxy(self, options):
                """We output the generated proxy to the output file specified in options.
                
                    Args:
                options: a collection of command line parameters, mainly JSON config file,
                desired output file, and level of verbosity
                
                    Returns:
                Nothing returned, output file now contains c code for proxy
                
                """
                iterations = self.Get_Iterations(options)

                code = []
                if options.pinball == False:
                        code.append ("/*************")
                        code.append ("File created on "+str(datetime.datetime.now()))
                        code.append("input file: " + options.configFileName)
                        code.append("input statistics")
                        code.append("****************/")
                        code.append("#include<stdio.h>")
                        code.append("#include<stdint.h>")
                        if self.mem_model == "HALO":
                                code.append('#include "{}"'.format(options.linked_list))
                        code.append("#define MAX 255*1024 + 252*1024")
                        code.append("#define ITERATIONS " + str(iterations)) # TODO: find new approach to determining iterations
		if self.mem_model in ["ZL", "ZS", "MA"]: # TODO: Figure out how to get the iteration count for HALO
		    arr_ct = 0
		    for arr in range(len(codeGenerator.array_used_list)):
			    if(codeGenerator.array_used_list[arr] == 1) or (arr_ct < codeGenerator.numAvailableArrays) :
				    size = codeGenerator.dataFootprint
				    if (codeGenerator.dataFootprint < iterations * self.dominantStride + self.maxArrOffset[arr]) and options.pinball:
					    printV(1, "Array too small!")
					    size = iterations * self.dominantStride + self.maxArrOffset[arr]        
				    code.append("char X" + str(arr_ct) + "[" + str(size) + "];")
				    arr_ct += 1
                func_name = os.path.basename(options.outFileName).split(".")[0]
                code.append ("void main (void)  {")
                
                # take generated assembly code from codeGenerator and embed it in output file
                code.append(codeGenerator.generateCode(options, iterations))
                code.append("}")

                outFile = open(options.outFileName, "w")
                outFile.write("\n".join(code))
                outFile.close()

                printV(3, "Done")


def parseCommandLine():
        """We parse the command line to fill in the options and set the verbosity
        
            Args:
        No arguments are needed, automatically parses the command line
        
            Returns:
        options: a collection of command line parameters, mainly JSON config file,
        desired output file, and level of verbosity
        
        """
        parser = argparse.ArgumentParser(description="Generate synthetic workload proxy from provided inputs")
        parser.add_argument("-i", "--configFile", dest="configFileName", metavar="FILE", required=True, help="SFG and overall data in JSON format")
        parser.add_argument("-o", "--syntheticOutputFile", dest="outFileName", metavar="FILE", default="codegen.c", help="output C file for generated code")
        parser.add_argument("--verbose", metavar="N", type=int, default=0, help="level of debug information printed out (0-3)")
        parser.add_argument("--mem_model", metavar="MM", choices=["ZL", "ZS", "MA", "HALO"], default="ZL", help="which memory model to use: legacy models are ZL, ZS, and MA. HALO model requires a trace file")
	parser.add_argument("--halo_trace", dest="traceFileName", help="Memory trace(s) presumably produced using HALO, used for HALO-driven memory model")
        parser.add_argument("--branch_model", metavar="BM", choices=["v2_legacy", "v3_global", "v4_local", "v5_correlation"], default="v3_global", help="Which branch model to use (v2_legacy, v3_global, v4_local, v5_correlation)")
        parser.add_argument("--seed", default=None, help="Seed to control the random processes of the widget generation")
        parser.add_argument("-p", "--Pinball", dest="pinball", action='store_true', default=False, help="Flag that switches to alternate pinball functionality")
        parser.add_argument("--linked_list", dest="linked_list", help="Linked lists(s) for use with HALO")
        parser.add_argument("--mem_multi_region", dest="mem_multi_region", help="Infor for inter-region reuse for use with HALO")
        parser.add_argument("--linked_list_json", dest="ll_json", help="Meta-Data Relating to Linked List Behavior")
        args = parser.parse_args()
	if args.mem_model == "HALO":
                if not args.ll_json :
                        parser.error("A trace file or linked list is required for the HALO memory model")
	if args.mem_model != "HALO" and args.traceFileName:
		parser.error("Trace files are only used for the HALO memory model")
        setVerbosity(args.verbose)
        return args

        
if __name__== "__main__":
        options = parseCommandLine()
        codeGenerator = CodeGenerator_x86(options)
        codeGenerator.Generate_Proxy()
        codeGenerator.Output_Proxy(options)     
