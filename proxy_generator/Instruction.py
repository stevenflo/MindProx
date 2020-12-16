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
#Note that gcc creates assembly by default in AT&T syntax, which is the syntax used for this code generator

import copy
import random
from VerbosePrint import *

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
			self.offset_reg = None
                        self.offset_scale = None
		elif operandType == "imm":
			self.reg = None
			self.imm = None
		elif operandType == "hex32_imm":
			self.imm = None
		elif operandType == "hex64_imm":
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
		return self.operandType == "imm" or self.operandType == "hex32_imm" or self.operandType == "hex64_imm"

	def __str__(self):
		if self.operandType == "mem":
                        try:
                                if self.offset_reg is not None:
                                        if self.offset is not None:

                                                return str(self.offset)+"(" + str(self.reg) + ", " + str(self.offset_reg) + ", " + str(self.offset_scale)  + ")"
                                        else:
                                                return "(" + str(self.reg) + ", " + str(self.offset_reg) + ", " + str(self.offset_scale)  + ")"
                                return  str(self.offset) + "(" + str(self.reg) + ")"
                        except AttributeError:
                                return  str(self.offset) + "(" + str(self.reg) + ")"

		elif self.operandType == "reg":
			return str(self.reg)
		elif self.operandType == "imm":
			return "$" + str(self.imm)
		elif self.operandType == "hex32_imm":
			return "$" + "{0:#0{1}x}".format(self.imm,10)
		elif self.operandType == "hex64_imm":
			return "$" + "{0:#0{1}x}".format(self.imm,18)
	


class InsGenerator:

	def __init__(self, insMix, numIns):
		self.insList = []
		printV(3, insMix)
		printV(3, "In InsGenerator init, numIns", numIns)
		for key in insMix.keys():
			if key == "branch" or key == "total" or key == "load" or key == "store":#We are now ignoring loads and stores
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

class Instruction_x86:
	insMap = {"integer_alu": "add", "integer_mul": "imul", "integer_div": "div",\
                  "load":"movw","store":"movw",\
		"fp_alu": "addsd", "fp_mul": "mulsd", "fp_div": "divsd", "branch_test": "test",\
                  "branch": "jnz", "other": "mov", "load_alu": "add"}

	def __init__(self, insType):
                #7/11/19 Steven Instruction is intialized to all register accesses
                #assignMemOps switches some register accesses to memory accesses
                #x86 only allows one operand to access memory generally, hence the new memAccess 
		self.insType = insType
		self.opcode = Instruction_x86.insMap[insType]
		self.label = None
                self.memAccess = False
                self.ll = False
		if self.insType == "integer_alu":
			self.operands = [Operand("reg", "general", "r", "explicit"), Operand("reg", "general", "rw", "explicit")]
		elif insType == "integer_mul":
			self.operands = [Operand("reg", "general", "r", "explicit"), Operand("reg", "general", "rw", "explicit")]
		elif insType == "integer_div":
			self.operands = [Operand("reg", "general", "r", "explicit"), Operand("reg", "general", "rw", "implicit"), Operand("reg", "general", "rw", "implicit")]
                        self.operands[0].reg = "%%r15" #To avoid overflow we always divide by esi which is a large value
			self.operands[1].reg = "%%eax"
			self.operands[2].reg = "%%edx"
		elif insType == "fp_alu":
			self.operands = [Operand("reg", "fp", "r", "explicit"), Operand("reg", "fp", "rw", "explicit")]
		elif insType == "fp_mul":
			self.operands = [Operand("reg", "fp", "r", "explicit"),Operand("reg", "fp", "rw", "explicit")]
		elif insType == "fp_div":
			self.operands = [Operand("reg", "fp", "r", "explicit"),Operand("reg", "fp", "rw", "explicit")]
		elif insType == "load":
			self.operands = [Operand("mem", "general", "r", "explicit"), Operand("reg", "general", "w", "explicit")]
		elif insType == "store":
			self.operands = [Operand("reg", "general", "r", "explicit"), Operand("mem", "general", "w", "explicit")]
		elif insType == "branch_test":
			self.operands = [Operand("hex32_imm", "general", "r", "explicit"), Operand("reg", "general", "r", "explicit")]
			self.operands[1].reg = "%%ecx" #Bug Steven 8/14 this should be referencing the registers from REgister.py
		elif insType == "other":
			self.operands = [Operand("reg", "general", "r", "explicit"), Operand("reg", "general", "rw", "explicit")]
		elif insType == "load_alu":
			self.operands = [Operand("mem", "general", "r", "explicit"), Operand("reg", "general", "rw", "explicit")]
		elif insType == "branch":
			self.ptr = None
			self.operands = []
		else:
			self.operands = []

	def getType(self):
		return self.insType


	def __str__(self):
		if self.insType == "branch":
			return str(self.label) + ": " + str(self.opcode) + " " + str(self.ptr)
		else:
			operandList = [(str(operand) if (operand.visibility == "explicit") else "") for operand in self.operands]
			operandList = filter(None, operandList)
			return self.label + ": " + self.opcode + " " + ", ".join(operandList)

