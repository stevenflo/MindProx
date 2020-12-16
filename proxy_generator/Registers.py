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
from VerbosePrint import *

class Registers:
	random = None



class Registers_x86(Registers):

	numRedundancies = 0

	def __init__(self, regType):
		if regType == "64bit":
			self.intIndR = ["%%esp", "%%edi"]  #esp is only read from, edi is only written to
			self.freeIntIndR = copy.copy(self.intIndR)
			self.busyIntIndR = []
			self.intDepR = ["%%eax", "%%ebx", "%%edx"]#7/10 Switched eax to general purpose, as divide writes to it
			# cannot us %%ebp
			self.freeIntDepR = copy.copy(self.intDepR)
			self.busyIntDepR = []
			#self.fpIndR = ["%%st"]
			#self.fpDepR = ["%%st"]
			#self.fpIndR = ["%%st(6)", "%%st(7)"]
			#self.fpDepR = ["%%st(0)", "%%st(1)", "%%st(2)", "%%st(3)", "%%st(4)", "%%st(5)"]
                        self.fpIndR = ["%%xmm15","%%xmm14"] #xmm15 is only written to, xmm14 is only read from
                        self.fpDepR = ["%%xmm0","%%xmm1","%%xmm2","%%xmm3","%%xmm4","%%xmm5","%%xmm6","%%xmm7"]
			self.freeFpDepR = copy.copy(self.fpDepR)
			self.busyFpDepR = []
			self.brR = ["%%ecx", "%%esi"]
                        self.constant = ["%%r15"] #This is used for divide instructions
			#self.strideR = ["%%esi"] 
			self.strideR = ["%%r8", "%%r9", "%%r10", "%%r11", "%%r12", "%%r13", "%%r14"] #7/10/19 Stole r15 for constants for divide
                        #1/24/20 Steven: using r8 as read base, r9 as write base, and r10 as the linked list index
                        #6/1/20 Steven: Using double word to avoid overwriting linked list with writes
                        self.readBase = ["%%r8d"]
                        #self.writeBase = ["%%r9d"]
                        self.index = ["%%r9d","%%r10d", "%%r11d", "%%r12d", "%%r13d", "%%r14d"]
			self.zeroStrideR = ["%%ebp"]
		elif regtype == "32bit":
			self.intIndR = ["%%rax"]
			self.intDepR = ["%%rbx"]
			self.fpIndR = ["%%rcx"]
			self.fpDepR = ["%%rdx"]
			self.brR = ["%%rsi"]
			self.strideR = ["%%rdi"]

	def nextAvailReg(self, regType):
		if regType == "intDepR":
			if len(self.freeIntDepR) <= 0:
				printV(3, "WARNING: register dependencies overwritten.")
				Registers_x86.numRedundancies += 1
				return self.intDepR[0]
			else:
				thisReg = self.freeIntDepR.pop(0)
				self.busyIntDepR.append(thisReg)
				return thisReg
		elif regType == "fpDepR":
			if len(self.freeFpDepR) <= 0:
				printV(3, "WARNING: register dependencies overwritten.")
				Registers_x86.numRedundancies += 1
				return self.fpDepR[0]
			else:
				thisReg = self.freeFpDepR.pop(0)
				self.busyFpDepR.append(thisReg)
				return thisReg


        def allRegs(self):
		printV(3, self.intIndR)
		printV(3, self.intDepR)
		printV(3, self.brR)
		printV(3, self.strideR)
		return self.intIndR + self.intDepR + ["%%st"] + self.brR + self.strideR + self.constant

'''
	def freeReg(self, regType, thisReg):
		if regType == "intDepR":
			if thisReg in self.busyIntDepR:
				self.busyIntDepR.remove(thisReg)
				self.freeIntDepR.append(thisReg)
			else:
				printV(3, "Warning: no register: " + str(thisReg) + "in busyIntDepR list.")
				printV(3, "intDepR", self.intDepR)
				printV(3, "busyIntDepR", self.busyIntDepR)
				return True
		if regType == "fpDepR":
			if thisReg in self.busyFpDepR:
				self.busyFpDepR.remove(thisReg)
				self.freeFpDepR.append(thisReg)
			else:
				printV(3, "Warning: no register: " + str(thisReg) + "in busyFpDepR list.")
				printV(3, "intDepR", self.fpDepR)
				printV(3, "busyIntDepR", self.busyFpDepR)
				return True

	def blockReg(self, regType, thisReg):
		if regType == "intDepR":
			if thisReg in self.freeIntDepR:
				self.busyIntDepR.append(thisReg)
				self.freeIntDepR.remove(thisReg)
			else:
				printV(3, "Warning: no register: " + str(thisReg) + "in freeIntDepR list.")
				self.allRegs();
				return True
		if regType == "fpDepR":
			if thisReg in self.freeFpDepR:
				self.busyFpDepR.append(thisReg)
				self.freeFpDepR.remove(thisReg)
			else:
				printV(3, "Warning: no register: " + str(thisReg) + "in freeFpDepR list.")
				self.allRegs();
				return True

	def allFreeRegs(self):
		printV(3, self.freeIntDepR)

	def allBusyRegs(self):
		printV(3, self.busyIntDepR)

	def regType(self, reg):
		if reg in self.intIndR:
			return "intIndR"
		elif reg in self.intDepR:
			return "intDepR"
		elif reg in self.fpIndR:
			return "fpIndR"
		elif reg in self.fpDepR:
			return "fpDepR"
		elif reg in self.brR:
			return "brR"
		elif reg in self.strideR:
			return "strideR"

	def reset(self):
		self.freeIntDepR.extend(self.busyIntDepR)
		self.busyIntDepR = []
		self.freeFpDepR.extend(self.busyFpDepR)
		self.busyFpDepR = []

	def isAnyIntRegFree(self):
		return len(self.freeIntDepR)
'''

