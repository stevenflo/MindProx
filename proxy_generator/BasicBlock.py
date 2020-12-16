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

from Instruction import *
from VerbosePrint import *
from Instruction import InsGenerator
import random

class BasicBlock:

	def __init__(self, size):
		self.insList = []
		self.size = size

	def insertIns(self, ins):
		self.insList.append(ins)

	def fillIns(self, insGenerator):
		for x in range(self.size-2):
			self.insList.insert(0, insGenerator.nextIns())
		printV(3, "in fillIns, ins list is", len(self.insList))


class BblGenerator:

	def __init__(self):
		insGenerator = None

	def nextBbl(self, size):
		newBbl = BasicBlock(size)
		# for x in range(size-2):
		# 	newBbl.insertIns(None)
			# newBbl.insertIns(self.insGenerator.nextIns())
		newBbl.insertIns(Instruction_x86("branch_test"))
		newBbl.insertIns(Instruction_x86("branch"))
		return newBbl
