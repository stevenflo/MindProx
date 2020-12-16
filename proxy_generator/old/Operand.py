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

class Operand:

	def __init__(self, operandType, regType, rw, visibility):
		self.operandType = operandType
		self.rw = rw
		self.visibility = visibility
		self.regType = regType
		if operandType == "reg":
			self.reg = None
		elif operandType == "mem":
			self.reg = None
			self.offset = None
		elif operandType == "imm":
			self.reg = None
			self.imm = None

	def isRegRead(self):
		return self.operandType == "reg" and (self.rw == "r" or self.rw == "rw")

	def isRegWrite(self):
		return self.operandType == "reg" and (self.rw == "w" or self.rw == "rw")

	def isRegRW(self):
		return self.operandType == "reg" and self.rw == "rw"

	def isRegAssigned(self):
		return self.reg != None

	def isMem(self):
		return self.operandType == "mem"

	def isImmediate(self):
		return self.operandType == "imm"

	def __str__(self):
		if self.operandType == "mem":
			return str(self.offset) + "(" + str(self.reg) + ")"
		elif self.operandType == "reg":
			return str(self.reg)
		elif self.operandType == "imm":
			return "$" + str(self.imm)
	
