/*BEGIN_LEGAL 
Intel Open Source License 

Copyright (c) 2002-2014 Intel Corporation. All rights reserved.
 
Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

Redistributions of source code must retain the above copyright notice,
this list of conditions and the following disclaimer.  Redistributions
in binary form must reproduce the above copyright notice, this list of
conditions and the following disclaimer in the documentation and/or
other materials provided with the distribution.  Neither the name of
the Intel Corporation nor the names of its contributors may be used to
endorse or promote products derived from this software without
specific prior written permission.
 
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE INTEL OR
ITS CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
END_LEGAL */
/* ===================================================================== */
/*! @file This file contains a static and dynamic opcode/ISA extension/ISA
 *  category mix profiler
 *
 * This is derived from mix.cpp. Handles an arbitrary number of threads 
 * using TLS for data storage and avoids locking, except during I/O.
 */

#include "pin.H"
#include <vector>
#include <iostream>
#include <sstream>
#include <iomanip>
#include <fstream>
#include <cstdlib>
#include <map>
#include <utility> /* for pair */
#include <vector>
#include <algorithm>

UINT64 interval_ins;

/* ===================================================================== */
/* Commandline Switches */
/* ===================================================================== */
KNOB_COMMENT mix_knob_family("pintool:mix", "Mix knobs");
KNOB<string> KnobOutputFile(KNOB_MODE_WRITEONCE,         "pintool:mix",   "o", "mix.out", "specify profile file name");
KNOB<string> KnobIntervalOutputFile(KNOB_MODE_WRITEONCE,         "pintool:mix",   "io", "mix.i.out", "specify interval profile file name");
KNOB<UINT32> KnobTopBlocks(KNOB_MODE_WRITEONCE,         "pintool:mix",    "top_blocks", "20", "specify a maximal number of top blocks for which icounts are printed");
KNOB<BOOL>   KnobShowDisassembly(KNOB_MODE_WRITEONCE,   "pintool:mix",    "disas", "0", "Show disassembly for top blocks");
KNOB<BOOL>   KnobPid(KNOB_MODE_WRITEONCE,                "pintool:mix",   "i", "0", "append pid to output file name");
KNOB<BOOL>   KnobProfilePredicated(KNOB_MODE_WRITEONCE,  "pintool:mix",   "p", "0", "enable accurate profiling for predicated instructions");
KNOB<BOOL>   KnobProfileStaticOnly(KNOB_MODE_WRITEONCE,  "pintool:mix",   "s", "0", "terminate after collection of static profile for main image");
#ifndef TARGET_WINDOWS
KNOB<BOOL>   KnobProfileDynamicOnly(KNOB_MODE_WRITEONCE, "pintool:mix",   "d", "1", "Only collect dynamic profile");
#else
KNOB<BOOL>   KnobProfileDynamicOnly(KNOB_MODE_WRITEONCE, "pintool:mix",   "d", "1", "Only collect dynamic profile");
#endif
KNOB<BOOL>   KnobNoSharedLibs(KNOB_MODE_WRITEONCE,       "pintool:mix",   "no_shared_libs", "0", "do not instrument shared libraries");
KNOB<BOOL>   KnobDominantStride(KNOB_MODE_WRITEONCE,     "pintool:mix",   "stride", "1", "Compute dominant stride");
KNOB<BOOL>   KnobStream(KNOB_MODE_WRITEONCE,             "pintool:mix",   "stream", "0", "Compute dominant stream");
KNOB<BOOL>   KnobMapToFile(KNOB_MODE_WRITEONCE,          "pintool:mix",   "mapaddr", "0", "Map Addresses to File/Line information");
KNOB<BOOL>   KnobEarlyOut(KNOB_MODE_WRITEONCE,           "pintool:mix",   "early_out", "0" , "Exit after tracing the first region.");
KNOB<UINT64> KnobInterval(KNOB_MODE_WRITEONCE,         "pintool:mix",    "interval", "100000000", "specify instructions of an interval");

typedef enum { measure_global_stride=0, measure_local_stride=1, measure_stream=2 } measurement_t;
measurement_t measurement = measure_global_stride;

/* ===================================================================== */

INT32 Usage()
{
    cerr << "This pin tool computes a dominant stride or stream \n\n";
    cerr << KNOB_BASE::StringKnobSummary();
    cerr << endl;
    cerr << "The default is to do stride profiling" << endl;
    cerr << "At most one of -iform, -ilen or  -category is allowed" << endl;
    cerr << endl;
    return -1;
}

/* ===================================================================== */
/* ===================================================================== */
typedef UINT64 COUNTER;

static std::ofstream* out;
static std::ofstream* iout;

typedef map<ADDRINT, ADDRINT> LOCAL_BBL_STRUCT;
typedef map<ADDRINT, ADDRINT> LOCAL_DATA_STRUCT;

LOCAL_BBL_STRUCT loc_bbl;
std::vector <ADDRINT> bblcount_vector;
LOCAL_BBL_STRUCT interval_loc_bbl;
std::vector <ADDRINT> interval_bblcount_vector;

UINT64 icount;
UINT64 bblcount;
UINT64 ack_bblcount;

ADDRINT target_bbl_count;
ADDRINT running_dyn_bbl_count;
ADDRINT final_static_bbl_count;

LOCAL_DATA_STRUCT loc_datapage;
std::vector <ADDRINT> pagecount_vector;
LOCAL_DATA_STRUCT interval_loc_datapage;
std::vector <ADDRINT> interval_pagecount_vector;
UINT64 total_page_count;
UINT64 ack_total_page_count;

ADDRINT target_page_count;
ADDRINT target_50page_count;
ADDRINT running_dyn_page_count;
ADDRINT final_static_page_count;
ADDRINT found_fifty_count;

UINT64 ins_count;
UINT64 interval_count = 0;

void init_vars() {
	loc_bbl.clear();
	bblcount_vector.clear();
	interval_loc_bbl.clear();
	interval_bblcount_vector.clear();

	icount = 0;
	bblcount = 0;
	ack_bblcount = 0;

	target_bbl_count = 0;
	running_dyn_bbl_count = 0;
	final_static_bbl_count = 0;

	loc_datapage.clear();
	pagecount_vector.clear();
	interval_loc_datapage.clear();
	interval_pagecount_vector.clear();

	total_page_count = 0;
	ack_total_page_count = 0;

	target_page_count = 0;
	target_50page_count = 0;
        running_dyn_page_count = 0;
        final_static_page_count = 0;
        found_fifty_count = 0;

	ins_count = 0;

}

/****************************************************/
VOID emit_stats(THREADID tid); //forward prototype
VOID Fini(int, VOID * v);

/* ===================================================================== */

VOID docount(THREADID tid, ADDRINT c, ADDRINT ins_addr) { 
	icount += c; 	//Dynamic Instruction Count	
	bblcount += 1;
	
	ADDRINT bbl_start_addr = (ADDRINT) (ins_addr);

	LOCAL_BBL_STRUCT::iterator map_iter;

	map_iter = loc_bbl.find(bbl_start_addr);

	if(map_iter == loc_bbl.end()) {
		loc_bbl[bbl_start_addr] = bblcount_vector.size();
		bblcount_vector.push_back(1);
		//OutFile << "In docount, new bbl addr is " << bbl_start_addr << ", Vector position is " << loc_bbl[bbl_start_addr] << endl;
	}
	else {
		bblcount_vector[(loc_bbl[bbl_start_addr])] += 1;
	}

	map_iter = interval_loc_bbl.find(bbl_start_addr);

	if(map_iter == interval_loc_bbl.end()) {
		interval_loc_bbl[bbl_start_addr] = interval_bblcount_vector.size();
		interval_bblcount_vector.push_back(1);
		//OutFile << "In docount, new bbl addr is " << bbl_start_addr << ", Vector position is " << loc_bbl[bbl_start_addr] << endl;
	}
	else {
		interval_bblcount_vector[(interval_loc_bbl[bbl_start_addr])] += 1;
	}
}

static VOID RecordMem(THREADID tid, VOID * ip, VOID * addr)
{
	ADDRINT new_page_addr = ((ADDRINT) (addr)) >> 12;               //4k-byte blocks
	//ADDRINT inst_ptr = (ADDRINT) (ip);

	LOCAL_DATA_STRUCT::iterator map_iter;

	map_iter = loc_datapage.find(new_page_addr);

	total_page_count++;

	if(map_iter == loc_datapage.end()) { //no found
		loc_datapage[new_page_addr] = pagecount_vector.size();//page id
		pagecount_vector.push_back(1);
	}
	else {
		pagecount_vector[(loc_datapage[new_page_addr])] += 1;
	}
	//OutFile << "In docount,  page mem address is " << new_page_addr << ", Vector position is " << loc_datapage[new_page_addr]

	map_iter = interval_loc_datapage.find(new_page_addr);

	if(map_iter == interval_loc_datapage.end()) { //no found
		interval_loc_datapage[new_page_addr] = interval_pagecount_vector.size();//page id
		interval_pagecount_vector.push_back(1);
	}
	else {
		interval_pagecount_vector[(interval_loc_datapage[new_page_addr])] += 1;
	}
	//OutFile << "In docount,  page mem address is " << new_page_addr << ", Vector position is " << loc_datapage[new_page_addr]
}

VOID do_ins_count(THREADID tid)
{

    ins_count++;
    if(0 == ins_count % interval_ins)
    {
	// emit the "normal" dynamic stats 
	*iout << "# EMIT_DYNAMIC_STATS" << endl;
    
	*iout << "Interval Number = " << interval_count++ << endl;
	
	*iout << "# instructions = "<< icount<< ", basic blocks = " << bblcount << std::endl;
	   
	*iout << "ins_count = "<< ins_count << endl;
		
	target_bbl_count = ((bblcount-ack_bblcount) * 90) / 100;
	running_dyn_bbl_count = 0;
	final_static_bbl_count = 0;

	UINT64 last_staticbb_dynct = 0;
	
	std::sort(interval_bblcount_vector.begin(), interval_bblcount_vector.end());
	std::vector<ADDRINT>::reverse_iterator rit;
	
	//OutFile << "Printing the sorted count vector. target_bbl_count = " << target_bbl_count << ", bblcount = " << bblcount << std::endl;
	for (rit = interval_bblcount_vector.rbegin(); rit!= interval_bblcount_vector.rend(); ++rit) {
		final_static_bbl_count++;
		running_dyn_bbl_count += (*rit);
	    //OutFile << "Current Dyn count is " << *rit << ", running_dyn_bbl_count is " << running_dyn_bbl_count << ", final_static_bbl_count is " << final_static_bbl_count << std::endl;
		if((running_dyn_bbl_count >= target_bbl_count) && ((*rit) < last_staticbb_dynct)) {
			break;
		}
		last_staticbb_dynct = *rit;
	}
	*iout << "Interval 90% static basic block count is " << final_static_bbl_count << ", interval dynamic basic block count is " << running_dyn_bbl_count << std::endl;
		
	//for (rit = interval_bblcount_vector.rbegin(); rit!= interval_bblcount_vector.rend(); ++rit) {
	//	static UINT32 i = 0;
	//	*out << "\t" << i++ << "\t" << *rit << std::endl;
	//}
	
	*iout << std::endl;
	*iout << std::endl;

	*iout << "Data statistics" << endl;
    *iout << "Interval page count is " << total_page_count - ack_total_page_count << endl;
 
	target_page_count = ((total_page_count - ack_total_page_count) * 90) / 100;
	target_50page_count = ((total_page_count - ack_total_page_count) * 50) / 100;
    *iout << "Target page counts are " << target_page_count << " and " << target_50page_count << endl;
	running_dyn_page_count = 0;
	final_static_page_count = 0;

	UINT64 last_datapage_dynct = 0;
        //OutFile << "Printing the sorted count vector, size of pagecount_vector is " << pagecount_vector.size() << std::endl;

	std::sort(interval_pagecount_vector.begin(), interval_pagecount_vector.end());
	std::vector<ADDRINT>::reverse_iterator r_rit;
	
	int found_fifty = 0;
	found_fifty_count = 0;

	*iout << "Interval touched static pages, size of pagecount_vector is " << interval_pagecount_vector.size() << std::endl;
	for (r_rit = interval_pagecount_vector.rbegin(); r_rit!= interval_pagecount_vector.rend(); ++r_rit) {
		final_static_page_count++;
		running_dyn_page_count += (*r_rit);
	    //OutFile << "Current Dyn count is " << *rit << ", running_dyn_page_count is " << running_dyn_page_count << ", final_static_page_count is " << final_static_page_count << std::endl;
		if((found_fifty == 0) and (running_dyn_page_count >= target_50page_count)) {	
			found_fifty = 1;
			found_fifty_count = final_static_page_count;
		}

		if((running_dyn_page_count >= target_page_count) && ((*r_rit) < last_datapage_dynct)) {
			break;
		}

		last_datapage_dynct = *r_rit;
	}
	*iout << "Interval 90% static data page count is " << final_static_page_count << ", interval dynamic page count is " << running_dyn_page_count << std::endl;
	*iout << "Interval 50% static data page count is " << found_fifty_count << std::endl;

	//for (rit = interval_pagecount_vector.rbegin(); rit!= interval_pagecount_vector.rend(); ++rit) {
	//	static UINT32 i = 0;
	//	*out << "\t" << i++ << "\t" << *rit << std::endl;
	//}
	*iout << std::endl;
	*iout << std::endl;

	//DumpStats(*out, cstats, KnobProfilePredicated, "$dynamic-counts",tid);
	*iout << "# END_DYNAMIC_STATS" <<  endl;

	interval_loc_bbl.clear();
	interval_bblcount_vector.clear();
	interval_loc_datapage.clear();
	interval_pagecount_vector.clear();
	ack_bblcount = bblcount;
	ack_total_page_count = total_page_count;
	//out->close();
	//exit(0);
    }
}

/* ===================================================================== */

VOID Trace(TRACE trace, VOID *v)
{
    //static UINT32 basic_blocks = 0;
    if ( KnobNoSharedLibs.Value()
         && IMG_Type(SEC_Img(RTN_Sec(TRACE_Rtn(trace)))) == IMG_TYPE_SHAREDLIB)
        return;

    for (BBL bbl = TRACE_BblHead(trace); BBL_Valid(bbl); bbl = BBL_Next(bbl))
    {
	BBL_InsertCall(bbl, IPOINT_ANYWHERE, AFUNPTR(docount), IARG_THREAD_ID, IARG_UINT32, BBL_NumIns(bbl), IARG_ADDRINT, BBL_Address(bbl), IARG_END);
		
        const INS head = BBL_InsHead(bbl);
        if (! INS_Valid(head)) continue;
	for (INS ins = head; INS_Valid(ins); ins = INS_Next(ins)) {
		if(INS_IsMemoryRead(ins) || INS_IsMemoryWrite(ins)) {
			UINT64 memOperands = INS_MemoryOperandCount(ins);
			if (memOperands > 0) {
				for (UINT32 memOp = 0; memOp < memOperands; memOp++) {
					INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR) RecordMem, IARG_THREAD_ID, IARG_INST_PTR, IARG_MEMORYOP_EA, memOp, IARG_END);
				}
			}
		}
		INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)do_ins_count, IARG_THREAD_ID, IARG_END);
	}

    }
}

/* ===================================================================== */
VOID emit_stats(THREADID tid)
{
        *out << "# EMIT_DYNAMIC_STATS FOR TID " << tid << endl;
	
	*out << "# instructions = "<< icount<< ", basic blocks = " << bblcount << std::endl;
	
	target_bbl_count = (bblcount * 90) / 100;
	running_dyn_bbl_count = 0;
	final_static_bbl_count = 0;

	UINT64 last_staticbb_dynct = 0;
	
	std::sort(bblcount_vector.begin(), bblcount_vector.end());
	std::vector<ADDRINT>::reverse_iterator rit;
	
	//OutFile << "Printing the sorted count vector. target_bbl_count = " << target_bbl_count << ", bblcount = " << bblcount << std::endl;
	for (rit = bblcount_vector.rbegin(); rit!= bblcount_vector.rend(); ++rit) {
		final_static_bbl_count++;
		running_dyn_bbl_count += (*rit);
	    //OutFile << "Current Dyn count is " << *rit << ", running_dyn_bbl_count is " << running_dyn_bbl_count << ", final_static_bbl_count is " << final_static_bbl_count << std::endl;
		if((running_dyn_bbl_count >= target_bbl_count) && ((*rit) < last_staticbb_dynct)) {
			break;
		}
		last_staticbb_dynct = *rit;
	}
	*out << "Final 90% static basic block count is " << final_static_bbl_count << ", final dynamic basic block count is " << running_dyn_bbl_count << std::endl;
		
	*out << std::endl;
	*out << std::endl;

	*out << "Data statistics" << endl;
        *out << "Total page count is " << total_page_count << endl;
 
	target_page_count = (total_page_count * 90) / 100;
	target_50page_count = (total_page_count * 50) / 100;
	running_dyn_page_count = 0;
	final_static_page_count = 0;

	UINT64 last_datapage_dynct = 0;
        //OutFile << "Printing the sorted count vector, size of pagecount_vector is " << pagecount_vector.size() << std::endl;

	std::sort(pagecount_vector.begin(), pagecount_vector.end());
	std::vector<ADDRINT>::reverse_iterator r_rit;
	
	int found_fifty = 0;
	found_fifty_count = 0;

	*out << "Total touched static pages, size of pagecount_vector is " << pagecount_vector.size() << std::endl;
	for (r_rit = pagecount_vector.rbegin(); r_rit!= pagecount_vector.rend(); ++r_rit) {
		final_static_page_count++;
		running_dyn_page_count += (*r_rit);
	    //OutFile << "Current Dyn count is " << *rit << ", running_dyn_page_count is " << running_dyn_page_count << ", final_static_page_count is " << final_static_page_count << std::endl;
		if((found_fifty == 0) and (running_dyn_page_count >= target_50page_count)) {	
			found_fifty = 1;
			found_fifty_count = final_static_page_count;
		}

		if((running_dyn_page_count >= target_page_count) && ((*r_rit) < last_datapage_dynct)) {
			break;
		}

		last_datapage_dynct = *r_rit;
	}
	*out << "Final 90% static data page count is " << final_static_page_count<< ", final dynamic page count is " << running_dyn_page_count<< std::endl;
	*out << "Final 50% static data page count is " << found_fifty_count<< std::endl;

	*out << std::endl;
	*out << std::endl;
	
	//DumpStats(*out, cstats, KnobProfilePredicated, "$dynamic-counts",tid);
    	*out << "# END_DYNAMIC_STATS" <<  endl;
}

/* ===================================================================== */

VOID Fini(int, VOID * v) // only runs once for the application
{
    *out << "# FINI: end of program" << endl;
    emit_stats(1);
    out->close();
}
   
/* ===================================================================== */

int main(int argc, CHAR **argv)
{
    PIN_InitSymbols();
    if( PIN_Init(argc,argv) )
        return Usage();

    init_vars();

    string filename =  KnobOutputFile.Value();
    out = new std::ofstream(filename.c_str());
    *out << "# Mix output version 2" << endl;
    filename = KnobIntervalOutputFile.Value();
    iout = new std::ofstream(filename.c_str());

    interval_ins = KnobInterval.Value();

    TRACE_AddInstrumentFunction(Trace, 0);
    PIN_AddFiniFunction(Fini, 0);

    PIN_StartProgram();    // Never returns
    return 0;
}

/* ===================================================================== */
/* eof */
/* ===================================================================== */
