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

import copy
import random
from Instruction import *
from VerbosePrint import *

class InsGenerator:

	def __init__(self, insMix, numIns):
		self.insList = []
		printV(3, insMix)
		printV(3, "In InsGenerator init, numIns", numIns)
		for key in insMix.keys():
			if key == "branch" or key == "total":
				continue
			insMix[key] = int(float( insMix[key]) * float(numIns) + 0.5)
			for x in range(insMix[key]):
				self.insList.append(Instruction_x86(key))
		printV(3, "numIns is:", numIns)
		printV(3, "InsGenerator, insMix:", insMix)
		self.ptr = 0

	def remove(self, insType, numIns):
		iterator = range(len(self.insList))
		iterator.reverse()
		for x in iterator:
			if self.insList[x].getType() == insType:
				del self.insList[x]
				numIns -= 1
				if numIns == 0:
					break
		iterator = range(len(self.insList))
		iterator.reverse()
		if numIns > 0:
			for x in iterator:
				if self.insList[x].getType() == "other":
					del self.insList[x]
					numIns -= 1
					if numIns == 0:
						break

	def shuffle(self):
		random.shuffle(self.insList)

	def nextIns(self):
		thisIns = self.insList[self.ptr]
		self.ptr = (self.ptr + 1) % len(self.insList)
		return copy.deepcopy(thisIns)
