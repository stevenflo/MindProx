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
from BblGenerator import *
from InsGenerator import *
from Registers import *
import random
import copy
from collections import deque
import sys

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

class CodeGenerator:

	memBlockSize = 256
	MAX_OFFSET = 32768

	def __init__(self):
		bblList = []
		insList = []
		insMix = None
		self.raw = None
		stride = None
		staticBbls = None
		dynamicBbls = None
		avrBblSize = None
		avrSuccBbls = None
		brTrans = None
		dataFootprint = None
		LocalStride = None
                array_used_list = []
                minArrOffset = []
		maxArrOffset = []
                numAvailableArrays = None

	def generateBbls(self):
		raise NotImplementedError("Please Implement this method")

	def generateBranchBehavior(self):
		raise NotImplementedError("Please Implement this method")

	def assignDependencies(self):
		raise NotImplementedError("Please Implement this method")

	def assignStrides(self):
		raise NotImplementedError("Please Implement this method")

	def generateCode(self):
		raise NotImplementedError("Please Implement this method")


class CodeGenerator_x86 (CodeGenerator):

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
		self.LocalStride = None
		# super(CodeGenerator_x86).__init__()
                self.array_used_list = []
                self.minArrOffset = []
		self.maxArrOffset = []	
                self.numAvailableArrays = None

	def generateBbls(self):
		print self.__class__.__name__
		stdev = self.avrBblSize / 8.0
		print "avrBblSize", self.avrBblSize
		print "staticBbls", self.staticBbls
		totalIns = 0
		for n in range(self.staticBbls):	
			# TODO: get bblSize
			size = float(((self.avrBblSize * self.staticBbls) - sum(insMixRemoveDens.values())) / self.staticBbls)
			size = int(random.gauss(size, stdev) + 0.5)
			totalIns += size
			print "bbl", n, "size", size
			newBbl = self.bblGenerator.nextBbl(size)
			self.bblList.append(newBbl)
		insGenerator = InsGenerator(self.insMix, totalIns + sum(insMixRemoveDens.values()))
		insGenerator.remove("integer_alu", self.staticBbls)
		for key in insMixRemoveDens.keys():
			insGenerator.remove(key, insMixRemoveDens[key])
		insGenerator.shuffle()
		self.bblGenerator.insGenerator = insGenerator
		for bbl in self.bblList:
			bbl.fillIns(insGenerator)
			self.insList.extend(bbl.insList)
		# print "leftover instructions", [str(ins) for ins in insGenerator.insList]
		del self.insList[-1]
		del self.bblList[-1].insList[-1]
		if len(self.insList) < len(insGenerator.insList):
			print "WARNING: generated fewer instructions than expected. wrong ins mix."
		for bblI in range(len(self.bblList)):
			for insI in range(len(self.bblList[bblI].insList)):
				self.bblList[bblI].insList[insI].label = "BBL" + str(bblI) + "INS" + str(insI)
				if self.bblList[bblI].insList[insI].insType == "branch":
					self.bblList[bblI].insList[insI].ptr = "BBL" + str(bblI + 1) + "INS0"
		print "len on insList:", len(self.insList)
		return False

	def generateRawRemoveDens(self):
		print "In generateRawRemoveDens, before"
                print rawRemoveDens

		for x in range(min(32, len(self.insList))):
			if self.insList[x].insType == "branch_test" and (x + self.numAvailableArrays + 1) <= 32:
				if rawRemoveDens.has_key(x + self.numAvailableArrays + 1):
					rawRemoveDens[x + self.numAvailableArrays + 1] += 1
				else:
					rawRemoveDens[x + self.numAvailableArrays + 1] = 1
			for operand in self.insList[x].operands:
				if operand.isMem():   #Needs to be updated based on stride register assignment - TBD
					print operand.reg
					if not (operand.reg == self.registers.zeroStrideR[0]):
						reg_idx = self.registers.strideR.index(operand.reg)	
						reg_raw_dist = self.numAvailableArrays - reg_idx
						if rawRemoveDens.has_key(x + reg_raw_dist):
							rawRemoveDens[x + reg_raw_dist] += 1
						else:
							rawRemoveDens[x + reg_raw_dist] = 1

		print "In generateRawRemoveDens"
		print rawRemoveDens
	
	'''
	def generateBranchBehavior(self):
		print "In generate Branch Behavior, ", self.brTrans, self.staticBbls
		# TODO: Reena handles this
		pBrTrans = int(self.brTrans * 100)
		BrBucketIds = deque()
		tempBrCt = self.staticBbls
		nActualBranches = self.staticBbls
		currBrTrans = 0
			
		br_transition_prob = 0
		#targ_pBrTrans = int(2 * self.brTrans * 100) for q19
		targ_pBrTrans = int(1 * self.brTrans * 100) #for q6
		targ_pBrTrans = targ_pBrTrans * 2
		temp_transitioning_br = 0
		print targ_pBrTrans

		while (tempBrCt > 0) :
			br_transition_prob = random.randint (0, 100)
			if (br_transition_prob > targ_pBrTrans) :
				BrBucketIds.append(0)
			else :
				BrBucketIds.append(1)
				temp_transitioning_br = temp_transitioning_br + 1
				
			tempBrCt = tempBrCt - 1

		print "Target Branch Transition rate is ", pBrTrans
		print "Target number of switch branches = ", targ_pBrTrans
		print "Actual number of switch branches assigned = ", temp_transitioning_br
		for ins in self.insList:
			if(ins.getType() == "branch_test"):
				for operand in ins.operands:
					if operand.isImmediate():
						operand.imm = BrBucketIds.popleft()	
		return False
	'''	
        def generateBranchBehavior(self):
                # TODO: Reena handles this
                pBrTrans = int(self.brTrans * 100)
                BrBucketIds = deque()
                br = self.staticBbls
                tempBrCt = self.staticBbls
                nActualBranches = self.staticBbls
                currBrTrans = 0
                tempcurrBrTrans = 0
                last_bucket_id = 0

                while (tempBrCt > 0) :
                        nTrials = 10
                        thisBrTr = 0
                        br_bucket_id = 0
                        while (nTrials > 0):
                                temp_bucket_id = 0
                                temp_br_tr = 0
                                tempcurrBrTrans = 0

                                temp_bucket_id = random.randint (0, 9)
                                if(temp_bucket_id == 0) :
                                        temp_br_tr = 0
                                else:
                                        temp_br_tr = int(( 100) / temp_bucket_id)

                                tempcurrBrTrans = (((currBrTrans * (nActualBranches - tempBrCt)) + temp_br_tr))/(nActualBranches - tempBrCt + 1)

                                if((tempcurrBrTrans >= (pBrTrans * 1)) and (tempcurrBrTrans <= (pBrTrans * 2))):
                                        if(temp_bucket_id != last_bucket_id):
                                                thisBrTr = temp_br_tr
                                                br_bucket_id = temp_bucket_id
                                                break
                                nTrials = nTrials - 1
                                if(nTrials == 0):
                                        if(tempcurrBrTrans <= pBrTrans) :
                                                br_bucket_id = 1
                                                thisBrTr = int((100) / br_bucket_id)
                                        else :
                                                br_bucket_id = 2;
                                                thisBrTr = 50;
                        last_bucket_id = br_bucket_id
                        if(br_bucket_id != 0) :
                                br_bucket_id = pow(2, (br_bucket_id - 1)        )
                        tempBrCt = tempBrCt - 1
                        currBrTrans = ( ( (currBrTrans * (nActualBranches - tempBrCt - 1)) + thisBrTr))/(nActualBranches - tempBrCt);
                        BrBucketIds.append(br_bucket_id)
                print "Current Branch Transition is ", currBrTrans

                for ins in self.insList:
                        if(ins.getType() == "branch_test"):
                                for operand in ins.operands:
                                        if operand.isImmediate():
                                                operand.imm = BrBucketIds.popleft()
                return False
	
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
			# print "WARNING: reusing register", self.registers.intDepR[0]
			# self.assign(regDepIndex, self.registers.intDepR[0], start, end)
			print "WARNING: all registers blocked"
			return None
		elif regType == "fpDepR":
			for reg in self.registers.fpDepR:
				if not self.isAssigned(regDepIndex, reg, start, end):
					self.assign(regDepIndex, reg, start, end)
					return reg
			# print "WARNING: reusing register", self.registers.fpDepR[0]
			# self.assign(regDepIndex, self.registers.fpDepR[0], start, end)
			print "WARNING: all registers blocked"
			return None
		else:
			sys.error("ERROR: no reg type " + str(regType))
			return None

					

	def assignDependencies(self):
		totalRaws = int(self.rawRatio * len(self.insList))
		rawsPerIns = int(self.rawRatio + 0.5)
		rawDens = {k: int(v * totalRaws) for k, v in self.raw.items()}
		print "raw before removal:", rawDens
		print "rawRemoveDens:", rawRemoveDens
		remove(rawDens, rawRemoveDens)
		# regDepIndex = {}
		foundBr = False
		print "raw percentages:", self.raw
		print "raw after removal:", rawDens
		totalRaws = sum(rawDens.values())
		print sum(rawDens.values()), "to be assigned."
		# print "First Pass done - debug"
		totalReg = 0
		trials = 0
		regDepIndex = [[] for x in range(len(self.insList))]
		while (sum(rawDens.values()) > 0) and trials < 100:
			trials += 1
			print "trials:", trials
			rInsList = copy.copy(self.insList)
			rInsList.reverse()
			for ins in rInsList:
				numRawsApplied = rawsPerIns
				for operand in ins.operands:
					if trials == 1:
						if operand.isRegRead() or operand.isRegWrite():
							totalReg += 1
					if ((operand.isRegRW()) if (trials == 1) else (operand.isRegRead() and not operand.isRegAssigned())):
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
						print "start:", start
						end = start - thisRaw
						if end < 0:
							break

						breakAll = False
						for x in range(30):
							if rawDens.has_key(thisRaw) and rawDens[thisRaw] != 0:
								for wOperand in self.insList[end].operands:
									if wOperand.isRegWrite() and wOperand.regType == operand.regType:
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
										numRawsApplied -= 1
										if rawDens[thisRaw] != 0:
											rawDens[thisRaw] -= 1
										breakAll = True
										print "assigned raw", thisRaw
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
		print totalReg, "registers are available."
		print "raw's were overwritten", self.registers.numRedundancies, "times."
		print sum(rawDens.values()), "/", totalRaws, "raws were not assigned."
		print tIndR, "registers are read independent."
		print tIndW, "registers are write independent."
		print tIndRW, "register are rw independent."
		return False

        def updateGlobalDens(self, strideDens):
                init_stride = 12
                diff_stride = 8
                running_arr_ct = self.numAvailableArrays - 1;
                while running_arr_ct > 0:
                        if(strideDens.has_key(init_stride + (running_arr_ct * diff_stride))) :
                                strideDens[(init_stride + (running_arr_ct * diff_stride))] += 1
                        else :
                                strideDens[(init_stride + (running_arr_ct * diff_stride))] = 1

                        if(strideDens.has_key(-(init_stride + (running_arr_ct * diff_stride)))) :
                                strideDens[-(init_stride + (running_arr_ct * diff_stride))] += 1
                        else :
                                strideDens[-(init_stride + (running_arr_ct * diff_stride))] = 1

                        if(strideDens.has_key(diff_stride)):
                                strideDens[diff_stride] += 1
                        else :
                                strideDens[diff_stride] = 1
                        running_arr_ct -= 1

                if(strideDens.has_key(-(init_stride + ((self.numAvailableArrays - 1) * diff_stride)))):
                        strideDens[-(init_stride + ((self.numAvailableArrays - 1) * diff_stride))] += 1
                else :
                        strideDens[-(init_stride + ((self.numAvailableArrays - 1) * diff_stride))] = 1

                print "In updateGlobalDens, updated stride density for num arrays ", self.numAvailableArrays
                print strideDens


        def fixNumAvailArrays(self, numMemIns) :
                if(numMemIns < 10) :
                        return 1
                elif(numMemIns < 80) :
                        return int (numMemIns/10) #+ 1
                else :
                        return 8

        def nextStride(self, strideDens):
                print strideDens.values()
                if sum(strideDens.values()) <= 0:
                        return CodeGenerator.memBlockSize
                i = random.randint(1,sum(strideDens.values()))
                print sum(strideDens.values())
                print i
                thisStride = None
                for strd in strideDens.items():
                        i -= strd[1]
                        if i <= 0:
                                print strd
                                thisStride = strd[0]
                                if thisStride > abs(CodeGenerator.memBlockSize):
                                        return CodeGenerator.memBlockSize
                                else:
                                        return thisStride

        def assignStrides(self):
                strideRatio = float(len(self.insList)) / float(self.insMix["total"])
                print strideRatio
                print self.stride

                total_strides = 0
                for k, v in self.stride.items() :
                        total_strides += v

                total_mem_inst = 0
                for ins in self.insList:
                        for operand in ins.operands:
                                if operand.isMem():
                                        total_mem_inst += 1

                print "Total memory instructions = ", total_mem_inst

                self.numAvailableArrays = self.fixNumAvailArrays(total_mem_inst) #8 TBD
                print "Num Available Arrays is ", self.numAvailableArrays

                self.updateGlobalDens(globalStrideRemoveDens)
                print "Updated Before Total globalStrideRemoveDens values is ", sum(globalStrideRemoveDens.values())

                relGlobalRemoveStrideNum = 0
                for key in globalStrideRemoveDens.keys():
                        #scaled_down_stride = int(float(self.stride[key] * (total_mem_inst + sum(globalStrideRemoveDens.values())) / float(total_strides)) + 0.5)
                        if self.stride.has_key(key) :
				scaled_down_stride = int(float(self.stride[key] * (total_mem_inst + sum(globalStrideRemoveDens.values())) / float(total_strides)) + 0.5)

                                if(scaled_down_stride >= globalStrideRemoveDens[key]) :
                                        relGlobalRemoveStrideNum += globalStrideRemoveDens[key]
                                else :
                                        relGlobalRemoveStrideNum += scaled_down_stride

                print "relGlobalRemoveStrideNum = ", relGlobalRemoveStrideNum

                strideDens = {k: int(float(float(v * (total_mem_inst + relGlobalRemoveStrideNum)) / float(total_strides)) + 0.5) for k, v in self.stride.items()}
                print "After scaling Total stride density values is ", sum(strideDens.values())
                strideDens[CodeGenerator.memBlockSize] += strideDens[-CodeGenerator.memBlockSize]
                del strideDens[-CodeGenerator.memBlockSize]

                print "Printing stride density before removing global strides"
                print strideDens

                strideDens = removeStrides(strideDens, globalStrideRemoveDens)
                print "Printing stride density after removing global strides"
                print strideDens
                print "Total sum of strideDens values = ", sum(strideDens.values())

		#Local Stride Calculations
		print "Target local stride ratio:", self.localStride

		total_local_strides = 0
                for k, v in self.localStride.items() :
                    total_local_strides += v
								
		relLocalRemoveStrideNum = 0
		print localStrideRemoveDens
		for key in localStrideRemoveDens.keys():
                    scaled_down_stride = int(float(self.localStride[key] * (total_mem_inst + sum(localStrideRemoveDens.values())) / float(total_local_strides)) + 0.5)
		    print "key is ", key
		    print "scaled down stride is ", scaled_down_stride
                    if self.localStride.has_key(key) :
			   print "localStrideRemoveDens key is ", localStrideRemoveDens[key]
                 	   if(scaled_down_stride >= localStrideRemoveDens[key]) :
                        	relLocalRemoveStrideNum += localStrideRemoveDens[key]
                           else :
                           	relLocalRemoveStrideNum += scaled_down_stride

                print "relLocalRemoveStrideNum = ", relLocalRemoveStrideNum

		localStrideDens = {k: int(float(float(v * (total_mem_inst + relLocalRemoveStrideNum)) / float(total_local_strides)) + 0.5) for k, v in self.localStride.items()}
		print "Printing local stride dens before remove:", localStrideDens
		localStrideDens = removeStrides(localStrideDens, localStrideRemoveDens)
		print "Printing local stride dens after remove:", localStrideDens
		print "Total sum of localstrideDens values = ", sum(localStrideDens.values())
		num_zero_strides = localStrideDens[0]

		print "num zero strides is ", num_zero_strides
		#Stride Algorithm
		prevInsCategory = None
                prevOffset = None
		prevInsZeroStride = "False"
				
                array_offset_list = [0, 0, 0, 0, 0, 0, 0, 0]
                self.array_used_list = [0, 0, 0, 0, 0, 0, 0, 0]
                self.minArrOffset = [0, 0, 0, 0, 0, 0, 0, 0]
		self.maxArrOffset = [0, 0, 0, 0, 0, 0, 0, 0]
				
                prevArr = 0
                running_arr_ct = 0

                for ins in self.insList:
                        for operand in ins.operands:
                                if operand.isMem():
					if num_zero_strides > 0:
						print "\nnum zero strides is ", num_zero_strides
						if "load" in ins.insType and prevInsCategory == None:
							print "none load case"
							prevInsCategory = "load"
							prevInsZeroStride = "False"
						elif "load" in ins.insType and prevInsCategory == "load":
							print "load load"
							prevInsCategory = "load"												
							operand.offset = 0
							operand.reg = self.registers.zeroStrideR[0]										
							if prevInsZeroStride == "True" and strideDens[0] > 0:
								print "load load case 1"
								strideDens[0] -= 1
								prevInsZeroStride = "True"
								num_zero_strides -= 1
								print "Mem instruction: ", str(ins)
								continue
							elif prevInsZeroStride == "False" and strideDens[CodeGenerator.memBlockSize] > 0:
								print "load load case 2"
								strideDens[CodeGenerator.memBlockSize] -= 1
								prevInsZeroStride = "True"
								num_zero_strides -= 1
								print "Mem instruction: ", str(ins)
								continue
							else :
								print strideDens
								print "Num_zero_strides not zero, could not find a suitable placement though - Proceed to get a different assignment"													
								#prevInsZeroStride = "False"
						elif "load" in ins.insType and prevInsCategory == "store":
							print "store load"
							prevInsCategory = "load"
							operand.reg = self.registers.zeroStrideR[0]
							operand.offset = 0																								
							if strideDens[CodeGenerator.memBlockSize] > 0:
								print "store load case 1"
								strideDens[CodeGenerator.memBlockSize] -= 1													
								num_zero_strides -= 1
								prevInsZeroStride = "True"
								print "Mem instruction: ", str(ins)
								continue
						elif ins.insType == "store":
							print "store curr"
							prevInsCategory = "store"
							if prevInsZeroStride == "True":
								print "store curr case 1"
								if strideDens[CodeGenerator.memBlockSize] > 0:
									strideDens[CodeGenerator.memBlockSize] -= 1
							#prevInsZeroStride = "False"
						else:
							print "Invalid case for mems, num_zero_strides = ", num_zero_strides
							num_zero_strides = -1					
                                        print "here"
                                        if prevOffset == None:
                                                print "prevOffset none case"
                                                prevOffset = 0
                                                operand.reg = self.registers.strideR[0]
                                                operand.offset = 0
                                                prevArr = 0
                                                array_offset_list[prevArr] = 0
                                                self.array_used_list[prevArr] = 1
                                                running_arr_ct += 1
						prevInsZeroStride = "False"
                                        else:
						for x in range(10):	
							print "x is ", x
                                                	tempOffset = self.nextStride(strideDens)
							#if(num_zero_strides > 0) and (x != 9):
							#	continue

                                                	print "prevoffset not none, tempoffset = ", tempOffset
                                                	if(abs(tempOffset) >= CodeGenerator.memBlockSize) :
                                                        	if(num_zero_strides > 0) and (x != 9):
                                                                	continue

                                                        	print "case 1"
                                                        	tempArr = random.randint(0, (self.numAvailableArrays-1))
                                                        	if(self.array_used_list[tempArr] == 0) :
                                                                	running_arr_ct += 1
                                                        	self.array_used_list[tempArr] = 1
                                                        	tempOffset = (array_offset_list[tempArr] + CodeGenerator.memBlockSize)
                                                        	if(abs(tempOffset) >= CodeGenerator_x86.MAX_OFFSET) :
                                                                	modtempOffset = abs(tempOffset) % CodeGenerator_x86.MAX_OFFSET
                                                                	if(tempOffset < 0) :
                                                                        	tempOffset = -modtempOffset
                                                                	else :
                                                                        	tempOffset = modtempOffset

                                                        	prevArr = tempArr
								prevOffset = tempOffset
                                                        	operand.reg = self.registers.strideR[prevArr]
                                                        	operand.offset = tempOffset
								self.maxArrOffset[prevArr] = max([tempOffset, self.maxArrOffset[prevArr]])
                                                        	array_offset_list[prevArr] = operand.offset
                                                        	if strideDens[CodeGenerator.memBlockSize] > 0 :
                                                                	strideDens[CodeGenerator.memBlockSize] -= 1
								prevInsZeroStride = "False"
								break
                                                	else :
                                                        	print "case 2"
                                                        	prevOffset = array_offset_list[prevArr]
                                                        	print "prevOffset = ", prevOffset
                                                        	if(tempOffset + prevOffset) < 0:
                                                                	self.minArrOffset[prevArr] = min([(prevOffset + tempOffset), self.minArrOffset[prevArr]])
                                                                	print "minArrOffset[prevArr] is ", self.minArrOffset[prevArr]

                                                        	if(abs(tempOffset + prevOffset) > CodeGenerator_x86.MAX_OFFSET) :
                                                                	print "abs of tempOffset and prevOffset is greater than CodeGenerator_x86.MAX_OFFSET, ", (tempOffset + prevOffset)
                                                                	if strideDens[CodeGenerator.memBlockSize] > 0 :
                                                                        	strideDens[CodeGenerator.memBlockSize] -= 1
                                                                	modtempOffset = abs(tempOffset + prevOffset) % CodeGenerator_x86.MAX_OFFSET
                                                                	if((prevOffset + tempOffset) < 0) :
                                                                        	prevOffset = -modtempOffset
                                                                	else :
                                                                        	prevOffset = modtempOffset
                                                        	else:
									if prevInsZeroStride == "True":
										if strideDens[CodeGenerator.memBlockSize] > 0 :
                                                                                	strideDens[CodeGenerator.memBlockSize] -= 1
                                                                	else:
										if strideDens[tempOffset] > 0:
                                                                        		strideDens[tempOffset] -= 1
                                                                	prevOffset += tempOffset

								self.maxArrOffset[prevArr] = max([prevOffset, self.maxArrOffset[prevArr]])
                                                        	operand.offset = prevOffset
                                                        	operand.reg = self.registers.strideR[prevArr]
                                                        	array_offset_list[prevArr] = prevOffset
								prevInsZeroStride = "False"
								break
						if x == 9:
							print "I am here, moving on to next instruction"
                                        print "Mem instruction: ", str(ins)
                                        print array_offset_list
                                        print "\n"
                return False

        def generateCode(self):
                string = "int i;\n"
		string += "int j;\n"
                arr_ct = 0
                for arr in range(len(self.array_used_list)):
                        if(self.array_used_list[arr] == 1) or (arr_ct < self.numAvailableArrays):
                                string += "char* ptr" + str(arr_ct) + ";\n"
                                arr_ct += 1

		string += "for (j = 0; j < 5; j++) {\n"
                string += "for (i = 1; i < ITERATIONS; i++) {\n"

                arr_ct = 0
                for arr in range(len(self.array_used_list)):
                        if(arr_ct < self.numAvailableArrays) :
                                string += "ptr" + str(arr_ct) + " = (char*) &X" + str(arr_ct) + "[" + str(self.LocalStride) + " * i + " + str(-1 * self.minArrOffset[arr_ct]) + "];\n" #\ string += "ptr = (int*) &X[" + str(CodeGenerator.MAX_OFFSET) + " * i];\n"
                                arr_ct += 1

                #       + str(self.dataFootprint - CodeGenerator.MAX_OFFSET) + "];\n"
                string += "__asm__ __volatile__ ("
                string += "\"mov %0, " + self.registers.brR[0] + "\\n\\t\"\n"
                arr_ct = 0
                for arr in range(len(self.array_used_list)):
                        if(arr_ct < self.numAvailableArrays):
                                string += "\"mov %" + str(arr_ct+1) + ", " + self.registers.strideR[arr_ct] + "\\n\\t\"\n"
                                arr_ct += 1
                for ins in self.insList:
                        string += "\"" + str(ins) + "\\n\\t\"\n"
                # string += "\"add $1, " + self.registers.strideR[0] + "\\n\\t\"\n"
                # string += "\"cmp 200(%1), " + self.registers.strideR[0] + "\\n\\t\"\n"
                # string += "\"jnz BBL0INS0\\n\\t\"\n"
                string += "::" + "\"m\"(i)"   #\"m\"(ptr)" + ":\"memory\", \"cc\", "
                ptrstring = ""
                arr_ct = 0
                print "debug - range of self.array_used_list is ", len(self.array_used_list)
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
