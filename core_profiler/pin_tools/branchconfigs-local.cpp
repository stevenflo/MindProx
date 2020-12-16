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

UINT64 fast_fwd;
UINT64 total_ins;
UINT64 interval_ins;

/* ===================================================================== */
/* Commandline Switches */
/* ===================================================================== */
KNOB_COMMENT mix_knob_family("pintool:mix", "Mix knobs");
KNOB<string> KnobOutputFile(KNOB_MODE_WRITEONCE,         "pintool:mix",   "o", "mix.out", "specify profile file name");
KNOB<string> KnobIntervalOutputFile(KNOB_MODE_WRITEONCE,         "pintool:mix",   "io", "mix.i.out", "specify interval profile file name");
KNOB<UINT32> KnobTopBlocks(KNOB_MODE_WRITEONCE,         "pintool:mix",    "top_blocks", "20", "specify a maximal number of top blocks for which DynInsCounts are printed");
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
KNOB<UINT64> KnobFastFwd(KNOB_MODE_WRITEONCE,         "pintool:mix",    "fast_forward", "0", "specify a fast forward number");
KNOB<UINT64> KnobTotalIns(KNOB_MODE_WRITEONCE,         "pintool:mix",    "total_instructions", "500000000", "specify total instructions");
KNOB<UINT64> KnobInterval(KNOB_MODE_WRITEONCE,         "pintool:mix",    "interval", "100000000", "specify instructions of an interval");

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

/* ===================================================================== */

static std::ofstream* out;
static std::ofstream* iout;

UINT64 DynInsCount;
UINT64 DynBblCount;
UINT64 GlobalCondCount;
UINT64 GlobalUncondCount;
UINT64 GlobalTkCount;
UINT64 GlobalTransCount;
UINT64 DynCondBrCount;

class BranchStruct {
        public:
                ADDRINT inst_ptr;
                bool last_taken;
                UINT64 transition_count;
                UINT64 total_count;
				UINT64 taken_count;

                BranchStruct(ADDRINT ip, bool isTaken) {
                        last_taken = isTaken;
                        inst_ptr = ip;
                        transition_count = 0;   
                        total_count = 0;
						taken_count = isTaken;
                }

                VOID incr_count() {
                        total_count++;
                }

                VOID set_transibility(bool isTaken) {
                        if(last_taken != isTaken) {
                                transition_count++;
								GlobalTransCount++;
                        }
                        last_taken = isTaken;
						taken_count += isTaken;
                }
};

typedef map<ADDRINT, BranchStruct*> BranchInfo;

BranchInfo BrInfo;
	
UINT32 interval_count = 0;

void init_vars() 
{
    DynInsCount = 0;
    DynBblCount = 0;
    GlobalCondCount = 0;
    GlobalUncondCount = 0;
    GlobalTkCount = 0;
	GlobalTransCount = 0;
}

VOID record_branch_transitions(ADDRINT inst_ptr, bool isTaken) {
	DynCondBrCount++;
	BranchInfo::iterator iter = BrInfo.find(inst_ptr);

	if(iter != BrInfo.end()) {
		iter->second->incr_count();
		iter->second->set_transibility(isTaken);
	}
	else {
		BranchStruct* br_new = new BranchStruct(inst_ptr, isTaken);

                br_new->incr_count();

                BrInfo[inst_ptr] = br_new;
        }
}   

VOID emit_stats(void); //forward prototype
VOID Fini(int, VOID * v);

VOID docount(THREADID tid, ADDRINT c) { 
	DynInsCount += c; 	//Dynamic Instruction Count	
	DynBblCount += 1;	
}

static VOID RecordBranchOrCall(THREADID tid, VOID * ip, VOID * target_addr, ADDRINT fall_thru_addr, BOOL isTaken, BOOL isCond) {
	//ADDRINT new_fallthru_addr = (ADDRINT) (fall_thru_addr);	
	ADDRINT inst_ptr = (ADDRINT) (ip);
	  
	if(isCond) {	
		record_branch_transitions(inst_ptr, isTaken);
		GlobalCondCount += 1;	
	}
	else {
		GlobalUncondCount += 1;
	}	

	if(isTaken) {
		GlobalTkCount += 1;
	} 
	/*else {
		ret_br_bk = check_branch_bucket(new_fallthru_addr, inst_ptr);
	}*/
}


VOID Trace(TRACE trace, VOID *v)
{
    if ( KnobNoSharedLibs.Value()
         && IMG_Type(SEC_Img(RTN_Sec(TRACE_Rtn(trace)))) == IMG_TYPE_SHAREDLIB)
        return;

    for (BBL bbl = TRACE_BblHead(trace); BBL_Valid(bbl); bbl = BBL_Next(bbl))
    {
	BBL_InsertCall(bbl, IPOINT_ANYWHERE, AFUNPTR(docount), IARG_THREAD_ID, IARG_UINT32, BBL_NumIns(bbl), IARG_END);
        const INS head = BBL_InsHead(bbl);
        if (! INS_Valid(head)) continue;

        for (INS ins = head; INS_Valid(ins); ins = INS_Next(ins))
        {

		if(INS_IsBranchOrCall(ins)) {   
       			INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)RecordBranchOrCall, IARG_THREAD_ID, IARG_INST_PTR, IARG_BRANCH_TARGET_ADDR, IARG_ADDRINT, INS_NextAddress(ins), IARG_BRANCH_TAKEN, IARG_BOOL, INS_HasFallThrough(ins), IARG_END);   
		}		
        }
    }
}

/* ===================================================================== */
VOID emit_stats(void)
{
    // emit the "normal" dynamic stats
    *out << "Dynamic_Instruction_Count: "<< DynInsCount << endl;
    *out << "Dynamic_Conditional_Branch_Count: " << GlobalCondCount << endl;
	*out << "Dynamic_Unconditional_Branch_Count: "<< GlobalUncondCount << endl;
	*out << "Total_Taken_Branches: " << GlobalTkCount << endl;
	*out << "Total_Branch_Transitions: " << GlobalTransCount << endl;

	*out << "\nLocal Branch Stats (Total Count; Taken Count; Transition Count)" << endl;
	BranchInfo::iterator iter = BrInfo.begin();
	while (iter != BrInfo.end()){
		*out << iter->second->total_count << " " << iter->second->taken_count << " " << iter->second->transition_count << endl;
		iter++;
	}
}

/* ===================================================================== */

VOID Fini(int, VOID * v) // only runs once for the application
{
    emit_stats();
    out->close();
    iout->close();
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
    *out << "# Branch output version 3" << endl;
    filename = KnobIntervalOutputFile.Value();
    iout = new std::ofstream(filename.c_str());

    fast_fwd = KnobFastFwd.Value();
    total_ins = KnobTotalIns.Value();
    interval_ins = KnobInterval.Value();

    // make sure that exactly one thing-to-count knob is specified.
    if (KnobDominantStride.Value() && KnobStream.Value()) {
        cerr << "Must have at most  one of: -stride or -stream " << "as a pintool option" << endl;             
        exit(1);
    }

    TRACE_AddInstrumentFunction(Trace, 0);
    PIN_AddFiniFunction(Fini, 0);

    PIN_StartProgram();    // Never returns
    return 0;
}

/* ===================================================================== */
/* eof */
/* ===================================================================== */
