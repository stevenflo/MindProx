#!/usr/bin/env python2

# TODO: Smarter prefix handling
# e.g. V<opcode>, <opcode>_NEAR, <opcode>_LOCK

import re
import sys
import os

block_re = re.compile(r"BLOCK:\s*([0-9a-f]+).*EXECUTIONS:\s*([0-9]+)")
global_stats_header_re = re.compile(r"\$global-dynamic-counts")
ins_count_re = re.compile(r"(\S+)\s+([0-9]+)")
mem_read_re = re.compile(r"\*mem-read-")
mem_write_re = re.compile(r"\*mem-write-")
data_xfer_re = re.compile(r"\*category-DATAXFER")
total_re = re.compile(r"\*total")

################################################################################
#                                                                              #
#                   Rules for categorizing instructions                        #
#                                                                              #
################################################################################

insCategories = ["IntCount", "IntMulCount", "IntDivCount", "FPCount", \
	"FPMulCount", "FPDivCount", "LdCount", "StCount", "Br/CallCount", \
	"CondBrCount", "OtherCount", "SysCallCount"]

insMappings = {
	"ADC": ["IntCount"],
	"ADD": ["IntCount"],
	"ADDSS": ["FPCount"],
        "ADDSD": ["FPCount"],
	"AND": ["IntCount"],
	"BSF": ["IntCount"],
	"BSR": ["IntCount"],
	"CALL": ["Br/CallCount"],
	"CALL_NEAR": ["Br/CallCount"],
	"CMP": ["IntCount"],
        "COMISD": ["FPCount"],
	"DEC": ["IntCount"],
	"DIV": ["IntDivCount"],
	"DIVSS": ["FPDivCount"],
	"IDIV": ["IntDivCount"],
	"IMUL": ["IntMulCount"],
	"INC": ["IntCount"],
	"JB": ["Br/CallCount", "CondBrCount"],
	"JBE": ["Br/CallCount", "CondBrCount"],
	"JL": ["Br/CallCount", "CondBrCount"],
	"JLE": ["Br/CallCount", "CondBrCount"],
	"JMP": ["Br/CallCount"], # Unconditional
	"JNB": ["Br/CallCount", "CondBrCount"],
	"JNBE": ["Br/CallCount", "CondBrCount"],
	"JNL": ["Br/CallCount", "CondBrCount"],
	"JNLE": ["Br/CallCount", "CondBrCount"],
	"JNS": ["Br/CallCount", "CondBrCount"],
	"JNZ": ["Br/CallCount", "CondBrCount"],
	"JS": ["Br/CallCount", "CondBrCount"],
	"JZ": ["Br/CallCount", "CondBrCount"],
	"LEA": ["IntCount"], # LEA doesn't actually access memory, so this seems reasonable
	# Loads, stores, and data movement are computed from metadata; the mov instructions themselves should probably be ignored
	"MOV": [],
	"MOVAPD": [],
	"MOVAPS": [],
	"MOVD": [],
	"MOVDQA": [],
	"MOVDQU": [],
	"MOVQ": [],
	"MOVSD_XMM": [],
	"MOVSS": [],
	"MOVSX": [],
	"MOVSXD": [],
	"MOVZX": [],
	"MUL": ["IntMulCount"],
	"MULSS": ["FPMulCount"],
        "MULSD": ["FPMulCount"],
	"NEG": ["IntCount"],
	#"NOP": [],	# Counting NOPs as "OtherCount" - uncommenting this would make them ignored
	"NOT": ["IntCount"],
	"OR": ["IntCount"],
	# Pushes and pops look to be subsumed in the memory access metadata
	"POP": [],
	"POR": ["IntCount"],
	"PUSH": [],
	"PXOR": ["IntCount"],
	"RET": ["Br/CallCount"],
	"RET_NEAR": ["Br/CallCount"],
	"ROL": ["IntCount"],
	"ROR": ["IntCount"],
	"SAR": ["IntCount"],
	"SBB": ["IntCount"],
	"SHL": ["IntCount"],
	"SHLD": ["IntCount"],
	"SHR": ["IntCount"],
	"SHRD": ["IntCount"],
	"STOSB": [],
	"STOSD": [],
	"STOSQ": [],
	"SUB": ["IntCount"],
        "SUBSD": ["FPCount"],
	"SYSCALL": ["Br/CallCount", "SysCallCount"],
	"TEST": ["IntCount"],
	"TZCNT": ["IntCount"],
	"VADDSD": ["FPCount"],
	"VMOVAPD": [],
	"VMOVDQA": [],
	"VMOVQ": [],
	"VMOVSD": [],
	"VMULSD": ["FPMulCount"],
	"VPADDQ": ["IntCount"],
	"VPSLLQ": ["IntCount"],
	"XCHG": [],
	"XOR": ["IntCount"],
}

isMetaOp = lambda op : op[0] == "*"


################################################################################



if len(sys.argv) not in range(2, 4):
	print "Usage: ./imix_new.py <input file> [output name]"
	exit(-1)

in_fname = sys.argv[1]
if len(sys.argv) == 3:
	out_fname = sys.argv[2]
else:
	out_fname = "imix.out"

insCounts = {category: 0 for category in insCategories}

sde_fp = open(in_fname, "r")

last_block = -1
dyn_block_count = 0
load_count = 0
store_count = 0
mem_meta_count = 0
found_header = False
unknowns = {}
for line in sde_fp:
	if not found_header:
		if global_stats_header_re.search(line) is not None:
			found_header = True
		match = block_re.match(line) 
		if match is not None:
			bnum = int(match.group(1), 16)
			if bnum > last_block:
				last_block = bnum
				dyn_block_count += int(match.group(2))
				print "Block " + hex(bnum) + ": Count: " + match.group(2) + ", Running Total: " + str(dyn_block_count)
		continue
	match = ins_count_re.match(line)
	if match is not None:
		opcode = match.group(1)
		if opcode.startswith("REP_"):
			print "Opcode " + opcode + " has repeat prefix; discarding prefix"
			opcode = opcode[4:]
		count = int(match.group(2))
		if isMetaOp(opcode):
			if mem_read_re.match(opcode):
				print "Load metaop: " + opcode
				load_count += count
				#insCounts["LdCount"] += count
			elif mem_write_re.match(opcode):
				print "Store metaop: " + opcode
				store_count += count
				#insCounts["StCount"] += count
			elif data_xfer_re.match(opcode):
				print "Xfer metaop: " + opcode
				insCounts["OtherCount"] += count
			elif total_re.match(opcode):
				print "Total metaop: " + opcode
				dyn_ins_count = count
			continue
		if opcode in insMappings:
			for category in insMappings[opcode]:
				#if category is "_MEM_META":
				#	mem_meta_count += count
				#else:
				#	insCounts[category] += count
				insCounts[category] += count

		else:
			print "Unrecognized opcode " + opcode + ", classifying as \"other\""
			insCounts["OtherCount"] += count
			unknowns.update({opcode: count})

#insCounts["LdCount"] += int((load_count/float(load_count+store_count)) * mem_meta_count)
#insCounts["StCount"] += int((store_count/float(load_count+store_count)) * mem_meta_count)
insCounts["LdCount"] += load_count
insCounts["StCount"] += store_count
#other_movs = mov_count - (load_count + store_count)
#print "\"Other\" MOVs: " + str(other_movs)
#insCounts["OtherCount"] += other_movs

sde_fp.close()
print "\nDone parsing file"

total_count = 0
for category, value in insCounts.iteritems():
	total_count += value

# Debug prints
print "\n\"Other\" ratio: " + str((100*insCounts["OtherCount"])/float(total_count)) + "%"
print "Sum category count: " + str(total_count)
print "Static BBL count: " + str(last_block+1)

out_string = "# FINI: end of program\n"
out_string += "Dynamic Instruction Count = " + str(dyn_ins_count) + ", Dyn BBL Count = " + str(dyn_block_count) + "\n"
out_string += "<DynInsCount> " + str(dyn_ins_count) + "\n"
out_string += "<BBLCount> " + str(dyn_block_count) + "\n"
out_string += "<TotInsCount> " + str(dyn_ins_count) + "\n" # Why did the old script print this same info three times? Who knows!
for category in insCategories:
	out_string += "<" + category + "> " + str(insCounts[category]) + "\n"
out_string += "\n# END_DYNAMIC_STATS"

print "\n" + out_string

print "\n\nSaving to file " + out_fname + "\n\n"
out_fp = open(out_fname, "w")
out_fp.write(out_string)
out_fp.close()

unknown_fname = os.path.splitext(out_fname)[0] + "_unknowns.txt"
out_string = "Dynamic instruction count: " + str(dyn_ins_count) + "\n"
out_string += "\nUnknown Opcodes:\n"
for (opcode, count) in sorted(unknowns.iteritems(), key=lambda x: x[1], reverse=True):
	out_string += opcode + " "*(20-len(opcode)) + str(count) + " "*(20-len(str(count))) + str((100*count)/float(dyn_ins_count)) + "%\n"
total_unknowns = sum(unknowns.values())
out_string += "Total" + " "*15 + str(total_unknowns) + " "*(20-len(str(total_unknowns))) + str((100*total_unknowns)/float(dyn_ins_count)) + "%"
uk_fp = open(unknown_fname, "w")
uk_fp.write(out_string)
uk_fp.close()
