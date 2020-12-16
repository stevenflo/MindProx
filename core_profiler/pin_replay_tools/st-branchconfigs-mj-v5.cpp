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
#include "pinplay.H"
PINPLAY_ENGINE pinplay_engine;
KNOB<BOOL> KnobPinPlayLogger(KNOB_MODE_WRITEONCE,
			     "pintool", "log", "0",
			     "Activate the pinplay logger");
KNOB<BOOL> KnobPinPlayReplayer(KNOB_MODE_WRITEONCE,
			       "pintool", "replay", "0",
			       "Activate the pinplay replayer");



UINT64 fast_fwd;
UINT64 total_ins;
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

class BranchStruct {
        public:
                ADDRINT inst_ptr;
                bool last_dir;
                UINT64 transition_count;
                UINT64 total_count;

                BranchStruct(ADDRINT ip, bool dir) {
                        last_dir = dir;
                        inst_ptr = ip;
                        transition_count = 0;   
                        total_count = 0;
                }

                VOID incr_count() {
                        total_count++;
                }

                VOID set_transibility(bool isTaken) {
                        if(last_dir != isTaken) {
                                transition_count++;
                        }
                        last_dir = isTaken;
                }
};

typedef map<ADDRINT, BranchStruct*> BranchInfo;
	
UINT64 icount;
UINT64 bblcount;
UINT64 tmp_icount;
UINT64 tmp_bblcount;
UINT64 cond_br;
UINT64 uncond_br;
UINT64 tk_branch;
UINT64 ack_cond_br;
UINT64 ack_uncond_br;
UINT64 ack_tk_branch;
//UINT64 global_last_accessed_address;
UINT64 last_ip;
BranchInfo BrInfo;
BranchInfo Interval_BrInfo;
UINT64 total_branches;
UINT64 thread_curr_ins;
bool start_recording;       

UINT32 interval_count = 0;

vector<COUNTER> global_branch_buckets; // =0 (rep), forward (1), backward(2)
vector<COUNTER> global_branch_transition_buckets;

vector<COUNTER> ack_global_branch_buckets; // =0 (rep), forward (1), backward(2)
 
void init_global_branch_buckets() {
     global_branch_buckets.resize(3);
     ack_global_branch_buckets.resize(3);
}

void init_global_transition_buckets() {
     global_branch_transition_buckets.resize(10);
}

void init_vars() 
{
    last_ip = 0;
    thread_curr_ins = 0;
    start_recording = 0;
    icount = 0;
    bblcount = 0;
    tmp_icount = 0;
    tmp_bblcount = 0;
    cond_br = 0;
    uncond_br = 0;
    tk_branch = 0;
    ack_cond_br = 0;
    ack_uncond_br = 0;
    ack_tk_branch = 0;

    init_global_branch_buckets();
    init_global_transition_buckets();
}

INT32 check_branch_bucket(ADDRINT new_addr, ADDRINT last_addr) {
	if(new_addr == last_addr) {
	    return 0;
	}
	else if(new_addr > last_addr) {
		return 1;
	}
	else if(new_addr < last_addr) {
		return 2;
	}
	else {
		*out << "Impossible branch bucket case reached\n";
		return -1;
	}    
}

VOID record_branch_transitions(ADDRINT inst_ptr, bool isTaken) {
	total_branches++;
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

	iter = Interval_BrInfo.find(inst_ptr);

	if(iter != Interval_BrInfo.end()) {
		iter->second->incr_count();
		iter->second->set_transibility(isTaken);
	}
	else {
		BranchStruct* br_new = new BranchStruct(inst_ptr, isTaken);

                br_new->incr_count();

                Interval_BrInfo[inst_ptr] = br_new;
        }
}   

VOID calculate_interval_transitions() {
	
	for(int i = 0; i < 10; i++)    
		global_branch_transition_buckets[i] = 0;
        for(BranchInfo::iterator iter = Interval_BrInfo.begin(); (iter != Interval_BrInfo.end()); ++iter) {
                int temp = (iter->second->transition_count * 100) / iter->second->total_count;
                if((temp >= 0) && (temp < 10)) {
                        global_branch_transition_buckets[0] = global_branch_transition_buckets[0] + iter->second->total_count; 
                }
                else if((temp >= 10) && (temp < 20)) {
                        global_branch_transition_buckets[1] = global_branch_transition_buckets[1] + iter->second->total_count; 
                }
                else if((temp >= 20) && (temp < 30)) {
                        global_branch_transition_buckets[2] = global_branch_transition_buckets[2] + iter->second->total_count;  
                }
                else if((temp >= 30) && (temp < 40)) {
                        global_branch_transition_buckets[3] = global_branch_transition_buckets[3] + iter->second->total_count;  
                }
                else if((temp >= 40) && (temp < 50)) {
                        global_branch_transition_buckets[4] = global_branch_transition_buckets[4] + iter->second->total_count;  
                }
                else if((temp >= 50) && (temp < 60)) {
                        global_branch_transition_buckets[5] = global_branch_transition_buckets[5] + iter->second->total_count; 
                }
                else if((temp >= 60) && (temp < 70)) {
                        global_branch_transition_buckets[6] = global_branch_transition_buckets[6] + iter->second->total_count;  
                }
                else if((temp >= 70) && (temp < 80)) {
                        global_branch_transition_buckets[7] = global_branch_transition_buckets[7] + iter->second->total_count;  
                }
                else if((temp >= 80) && (temp < 90)) {
                        global_branch_transition_buckets[8] = global_branch_transition_buckets[8] + iter->second->total_count;  
                }
                else if((temp >= 90) && (temp < 100)) {
                        global_branch_transition_buckets[9] = global_branch_transition_buckets[9] + iter->second->total_count;  
                }
                else {
                        //Invalid
                }
        }
}         

VOID calculate_final_transitions() {
	for(int i = 0; i < 10; i++)    
		global_branch_transition_buckets[i] = 0;
        for(BranchInfo::iterator iter = BrInfo.begin(); (iter != BrInfo.end()); ++iter) {
                int temp = (iter->second->transition_count * 100) / iter->second->total_count;
                if((temp >= 0) && (temp < 10)) {
                        global_branch_transition_buckets[0] = global_branch_transition_buckets[0] + iter->second->total_count; 
                }
                else if((temp >= 10) && (temp < 20)) {
                        global_branch_transition_buckets[1] = global_branch_transition_buckets[1] + iter->second->total_count; 
                }
                else if((temp >= 20) && (temp < 30)) {
                        global_branch_transition_buckets[2] = global_branch_transition_buckets[2] + iter->second->total_count;  
                }
                else if((temp >= 30) && (temp < 40)) {
                        global_branch_transition_buckets[3] = global_branch_transition_buckets[3] + iter->second->total_count;  
                }
                else if((temp >= 40) && (temp < 50)) {
                        global_branch_transition_buckets[4] = global_branch_transition_buckets[4] + iter->second->total_count;  
                }
                else if((temp >= 50) && (temp < 60)) {
                        global_branch_transition_buckets[5] = global_branch_transition_buckets[5] + iter->second->total_count; 
                }
                else if((temp >= 60) && (temp < 70)) {
                        global_branch_transition_buckets[6] = global_branch_transition_buckets[6] + iter->second->total_count;  
                }
                else if((temp >= 70) && (temp < 80)) {
                        global_branch_transition_buckets[7] = global_branch_transition_buckets[7] + iter->second->total_count;  
                }
                else if((temp >= 80) && (temp < 90)) {
                        global_branch_transition_buckets[8] = global_branch_transition_buckets[8] + iter->second->total_count;  
                }
                else if((temp >= 90) && (temp < 100)) {
                        global_branch_transition_buckets[9] = global_branch_transition_buckets[9] + iter->second->total_count;  
                }
                else {
                        //Invalid
                }
        }
}         

VOID emit_stats(THREADID tid); //forward prototype
VOID zero_stats(); //forward prototype
VOID Fini(int, VOID * v);

VOID ExitAnalysis(void) {
    *out << "# FINI: Early end of program, fast_fwd = " << fast_fwd <<" total ins=" << total_ins << endl;
    emit_stats(1);
    out->close();
    exit(0);

}

VOID docount(THREADID tid, ADDRINT c) { 
	icount += c; 	//Dynamic Instruction Count	
	bblcount += 1;	
	tmp_icount += c; 	//Dynamic Instruction Count	
	tmp_bblcount += 1;	
}

static VOID RecordBranchOrCall(THREADID tid, VOID * ip, VOID * target_addr, ADDRINT fall_thru_addr, BOOL isTaken, BOOL isCond) {
	ADDRINT new_target_addr = (ADDRINT) (target_addr);
	//ADDRINT new_fallthru_addr = (ADDRINT) (fall_thru_addr);	
	ADDRINT inst_ptr = (ADDRINT) (ip);
	  
	INT32 ret_br_bk;
	if(isCond) {	
		record_branch_transitions(inst_ptr, isTaken);
		cond_br += 1;	
	}
	else {
		uncond_br += 1;
	}	

	if(isTaken) {
		tk_branch += 1;
		ret_br_bk = check_branch_bucket(new_target_addr, inst_ptr);
		global_branch_buckets[ret_br_bk] += 1;
	} 
	/*else {
		ret_br_bk = check_branch_bucket(new_fallthru_addr, inst_ptr);
	}*/
	last_ip = inst_ptr;
}

static VOID do_ins_count(THREADID tid) {
	thread_curr_ins = thread_curr_ins + 1;
	//if (thread_curr_ins > (fast_fwd + total_ins)) {
		//exit
	//	ExitAnalysis();
	//}
	if(0 == thread_curr_ins % interval_ins)
	{
	    // emit the "normal" dynamic stats
	    *iout << "# EMIT_DYNAMIC_STATS" << std::endl;
	    *iout << "Interval Number = " << interval_count << std::endl;
	    *iout << "ins = "<< thread_curr_ins << endl;

	    *iout << "Dynamic Instruction Count = " << tmp_icount <<", Dyn BBL Count = " << tmp_bblcount << std::endl;
        tmp_icount = tmp_bblcount = 0;
	
	    *iout << "Branch Stats: Cond Branches = " << cond_br - ack_cond_br << " Uncond branches = "<< uncond_br - ack_uncond_br << " Tk branches = " << tk_branch - ack_tk_branch << endl;

	    ack_cond_br = cond_br;
	    ack_uncond_br = uncond_br;
	    ack_tk_branch = tk_branch;

	    for(int i = 0; i < 3; i++)    
		    *iout << "Branch Bucket "<< i << " is equal to " << global_branch_buckets[i] - ack_global_branch_buckets[i] << endl;

	    calculate_interval_transitions();
	    for(int i = 0; i < 10; i++)    
		    *iout << "Branch Transition Bucket "<< i << " is equal to " << global_branch_transition_buckets[i] << endl;
	    //accumulate the counts and clear temperory counts
	    interval_count ++;
	    for(int i = 0; i < 3; i++)    
		    ack_global_branch_buckets[i] = global_branch_buckets[i];

        for(BranchInfo::iterator iter = Interval_BrInfo.begin(); (iter != Interval_BrInfo.end()); ++iter) {
            delete iter->second;
        }
	    Interval_BrInfo.clear();

	}
}
/* ===================================================================== */

VOID zero_stats()
{
    last_ip = 0;    
    for(UINT32 i = 0; i < 3; i++) 
        global_branch_buckets[i] = 0;

    for(UINT32 i = 0; i < 10; i++) 
        global_branch_transition_buckets[i] = 0;
}

/************************************************************************************/

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
		INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)do_ins_count, IARG_THREAD_ID, IARG_END);	

		if(INS_IsBranchOrCall(ins)) {   
       			INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)RecordBranchOrCall, IARG_THREAD_ID, IARG_INST_PTR, IARG_BRANCH_TARGET_ADDR, IARG_ADDRINT, INS_NextAddress(ins), IARG_BRANCH_TAKEN, IARG_BOOL, INS_HasFallThrough(ins), IARG_END);   
		}		
        }
    }
}

/* ===================================================================== */
VOID emit_stats(THREADID tid)
{
    // emit the "normal" dynamic stats 
    *out << "# EMIT_DYNAMIC_STATS: instructions = "<< thread_curr_ins << endl;
    *out << "Branch Stats: Cond Branches = " << cond_br << " Uncond branches = "<< uncond_br<< " Tk branches = " << tk_branch << endl;

    for(int i = 0; i < 3; i++)    
        *out << "Branch Bucket "<< i << " is equal to " << global_branch_buckets[i] << endl;

    calculate_final_transitions();
    for(int i = 0; i < 10; i++)    
        *out << "Branch Transition Bucket "<< i << " is equal to " << global_branch_transition_buckets[i] << endl;

    //DumpStats(*out, cstats, KnobProfilePredicated, "$dynamic-counts",tid);
    *out << "# END_DYNAMIC_STATS" <<  endl;
}

/* ===================================================================== */

VOID Fini(int, VOID * v) // only runs once for the application
{
    *out << "# FINI: end of program" << endl;
    emit_stats(1);
    out->close();
    iout->close();
}
   
/* ===================================================================== */

int main(int argc, CHAR **argv)
{
    PIN_InitSymbols();
    if( PIN_Init(argc,argv) )
        return Usage();
    pinplay_engine.Activate(argc, argv,
			    KnobPinPlayLogger, KnobPinPlayReplayer);


    init_vars();
    zero_stats();

    string filename =  KnobOutputFile.Value();
    out = new std::ofstream(filename.c_str());
    *out << "# Mix output version 2" << endl;
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
