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


#define MAX_NUM_REGS 256
#define MAX_REG_BUCKETS 34

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

static std::ofstream* out;
static std::ofstream* iout;

bool start_recording;   
UINT64 icount;
UINT64 bblcount;
UINT64 last_ip;
UINT64 thread_curr_ins;
UINT64 tmp_icount;
UINT64 tmp_bblcount;
    
UINT32 interval_count = 0;

vector<BOOL> regRef; 
vector<ADDRINT> regWriteTable; 
vector<ADDRINT> regReadTable; 
vector<ADDRINT> RAWDistr; 
vector<ADDRINT> WAWDistr; 
vector<ADDRINT> WARDistr;      

vector<ADDRINT> tmp_RAWDistr; 
vector<ADDRINT> tmp_WAWDistr; 
vector<ADDRINT> tmp_WARDistr;      

void init_vars() {
	last_ip = 0;
        thread_curr_ins = 0;
        start_recording = 0;
        icount = 0;
        bblcount = 0;
        tmp_icount = 0;
        tmp_bblcount = 0;
}
 
void init_reg_buckets() {
	regRef.resize(MAX_NUM_REGS);
	regWriteTable.resize(MAX_NUM_REGS);
	regReadTable.resize(MAX_NUM_REGS);
	RAWDistr.resize(MAX_REG_BUCKETS);
	WAWDistr.resize(MAX_REG_BUCKETS);
	WARDistr.resize(MAX_REG_BUCKETS);
	tmp_RAWDistr.resize(MAX_REG_BUCKETS);
	tmp_WAWDistr.resize(MAX_REG_BUCKETS);
	tmp_WARDistr.resize(MAX_REG_BUCKETS);
}
	
void register_read(REG reg_idx, UINT32 i_offset) {
	//std::cout<<"read icount is "<<thread_curr_ins<<std::endl;
	if(regRef[reg_idx]) {
		//check for raw
		UINT64 raw_dist = thread_curr_ins - regWriteTable[reg_idx];
		if(raw_dist >= MAX_REG_BUCKETS-1){
			raw_dist = MAX_REG_BUCKETS-1; 
		}
		if(raw_dist >= 0)
			tmp_RAWDistr[raw_dist] += 1;
	}
	regReadTable[reg_idx] = thread_curr_ins;
	regRef[reg_idx] = true;
}

void register_write(REG reg_idx, UINT32 i_offset) {
	//std::cout<<"write icount is "<<thread_curr_ins << std::endl;
	if(regRef[reg_idx]) {
		//Check for WAR
		UINT64 war_dist = thread_curr_ins - regReadTable[reg_idx];
		if(war_dist >= MAX_REG_BUCKETS-1) 
			war_dist = MAX_REG_BUCKETS-1;
		if(war_dist >= 0)
			tmp_WARDistr[war_dist] += 1;		
	
		//Check for WAW
		UINT64 waw_dist = thread_curr_ins - regWriteTable[reg_idx];
		if(waw_dist >= MAX_REG_BUCKETS-1) 
			waw_dist = MAX_REG_BUCKETS-1;
		if(waw_dist >= 0)
			tmp_WAWDistr[waw_dist] += 1;
	}
	regWriteTable[reg_idx] = thread_curr_ins; 
	regRef[reg_idx] = true;
}

VOID calculate_final_transitions() {
	

}         

/****************************************************/
VOID emit_stats(THREADID tid); //forward prototype
VOID zero_stats(THREADID tid); //forward prototype
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

static VOID do_RegRead(THREADID tid, VOID * ip, REG reg_idx, UINT32 i_offset) {
    ADDRINT inst_ptr = (ADDRINT) ip;

    register_read(reg_idx, i_offset);
    last_ip = inst_ptr;
}

static VOID do_RegWrite(THREADID tid, VOID * ip, REG reg_idx, UINT32 i_offset) {
   ADDRINT inst_ptr = (ADDRINT) ip;
   register_write(reg_idx, i_offset);
   last_ip = inst_ptr;
}


static VOID do_ins_count(THREADID tid) {
	thread_curr_ins = thread_curr_ins + 1;
	if(!start_recording) { // && (thread_curr_ins > fast_fwd) && (thread_curr_ins < (fast_fwd + total_ins))){
		start_recording = 1;
	}
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
	
    for(int i = 0; i < MAX_REG_BUCKETS; i++) 
        *iout << "RAWdep[ "<< i << "] = " << tmp_RAWDistr[i]<< endl;

    *iout << endl;

    for(int i = 0; i < MAX_REG_BUCKETS; i++) 
        *iout << "WAWdep[ "<< i << "] = " << tmp_WAWDistr[i]<< endl;

    *iout << endl;
	
    for(int i = 0; i < MAX_REG_BUCKETS; i++) 
        *iout << "WARdep[ "<< i << "] = " << tmp_WARDistr[i]<< endl;

    *iout << endl;
    *iout << endl;
    //DumpStats(*out, cstats, KnobProfilePredicated, "$dynamic-counts",tid);

    //"0": "0",
    //for(int i = 0; i < MAX_REG_BUCKETS; i++)
//	*out << "\t\t" << "\"" << i << "\": \"" << RAWDistr[i] << "\"," << endl;
    
    *iout << endl;
    *iout << endl;
    
    //accumulate the counts and clear temperory counts
    interval_count ++;
    for(int i = 0; i < MAX_REG_BUCKETS; i++)
    {
	    RAWDistr[i] += tmp_RAWDistr[i];
	    tmp_RAWDistr[i] = 0;
	    WARDistr[i] += tmp_WARDistr[i];
	    tmp_WARDistr[i] = 0;
	    WAWDistr[i] += tmp_WAWDistr[i];
	    tmp_WAWDistr[i] = 0;
    }

	}
	
}

/* ===================================================================== */

VOID zero_stats()
{
	for(UINT32 i = 0; i < MAX_NUM_REGS; i++) {
		regRef[i] = 0;
		regWriteTable[i] = 0;
		regReadTable[i] = 0;
	}
	
	for(UINT32 j = 0; j < MAX_REG_BUCKETS; j++) {
		RAWDistr[j] = 0;
		WAWDistr[j] = 0;
		WARDistr[j] = 0;
	}	
}

/************************************************************************************/

VOID Trace(TRACE trace, VOID *v)
{
    UINT64 reg_ctr, maxNumRegsWrit, maxNumRegsRead;
    UINT64 inst_offset = 0;
    REG reg;
	
    //static UINT32 basic_blocks = 0;

    if (KnobNoSharedLibs.Value()
         && IMG_Type(SEC_Img(RTN_Sec(TRACE_Rtn(trace)))) == IMG_TYPE_SHAREDLIB)
        return;

    for (BBL bbl = TRACE_BblHead(trace); BBL_Valid(bbl); bbl = BBL_Next(bbl))
    {
	inst_offset = 0;

	BBL_InsertCall(bbl, IPOINT_ANYWHERE, AFUNPTR(docount), IARG_THREAD_ID, IARG_UINT32, BBL_NumIns(bbl), IARG_END);
        const INS head = BBL_InsHead(bbl);
        if (! INS_Valid(head)) continue;

        for (INS ins = head; INS_Valid(ins); ins = INS_Next(ins))
        {
		INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)do_ins_count, IARG_THREAD_ID, IARG_END);	

		maxNumRegsRead = INS_MaxNumRRegs(ins);
		for(reg_ctr = 0; reg_ctr < maxNumRegsRead; reg_ctr++) { 
			reg = INS_RegR(ins,reg_ctr);
			//if(REG_valid(reg) && (REG_is_fr(reg) || REG_is_mm(reg) || REG_is_xmm(reg) || REG_is_gr(reg) || REG_is_gr8(reg) || REG_is_gr16(reg) || REG_is_gr32(reg) || REG_is_gr64(reg))){
			if((reg >= 1) && (reg < MAX_NUM_REGS)) {
				INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)do_RegRead, IARG_THREAD_ID, IARG_INST_PTR, IARG_ADDRINT, reg, IARG_UINT32, inst_offset, IARG_END);
			}
		}
			
		maxNumRegsWrit = INS_MaxNumWRegs(ins);
		for(reg_ctr = 0; reg_ctr < maxNumRegsWrit; reg_ctr++) {
			reg = INS_RegW(ins, reg_ctr);
			//if(REG_valid(reg) && (REG_is_fr(reg) || REG_is_mm(reg) || REG_is_xmm(reg) || REG_is_gr(reg) || REG_is_gr8(reg) || REG_is_gr16(reg) || REG_is_gr32(reg) || REG_is_gr64(reg))){
			if((reg >= 1) && (reg < MAX_NUM_REGS)) {
				INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)do_RegWrite, IARG_THREAD_ID, IARG_INST_PTR, IARG_ADDRINT, reg, IARG_UINT32, inst_offset, IARG_END);
			}
		}
		inst_offset++;	
        }
    }
}

/* ===================================================================== */

VOID emit_stats(THREADID tid)
{
    *out << "# EMIT_DYNAMIC_STATS FOR TID " << tid << ", ins = "<< thread_curr_ins << endl;

    *out << "Dynamic Instruction Count = " << icount <<", Dyn BBL Count = " << bblcount << std::endl;
	
    //accumulate the counts
    for(int i = 0; i < MAX_REG_BUCKETS; i++)
    {
	    RAWDistr[i] += tmp_RAWDistr[i];
	    WARDistr[i] += tmp_WARDistr[i];
	    WAWDistr[i] += tmp_WAWDistr[i];
    }

    for(int i = 0; i < MAX_REG_BUCKETS; i++) 
        *out << "RAWdep[ "<< i << "] = " << RAWDistr[i]<< endl;

    *out << endl;

    for(int i = 0; i < MAX_REG_BUCKETS; i++) 
        *out << "WAWdep[ "<< i << "] = " << WAWDistr[i]<< endl;

    *out << endl;
	
    for(int i = 0; i < MAX_REG_BUCKETS; i++) 
        *out << "WARdep[ "<< i << "] = " << WARDistr[i]<< endl;

    *out << endl;
    *out << endl;
    //DumpStats(*out, cstats, KnobProfilePredicated, "$dynamic-counts",tid);

    //"0": "0",
    for(int i = 0; i < MAX_REG_BUCKETS; i++)
	*out << "\t\t" << "\"" << i << "\": \"" << RAWDistr[i] << "\"," << endl;
    
    *out << endl;
    *out << endl;

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
    init_reg_buckets();
    zero_stats();

    interval_ins = KnobInterval.Value();

    string filename =  KnobOutputFile.Value();
    out = new std::ofstream(filename.c_str());
    *out << "# Mix output version 2" << endl;
    filename = KnobIntervalOutputFile.Value();
    iout = new std::ofstream(filename.c_str());

    fast_fwd = KnobFastFwd.Value();
    total_ins = KnobTotalIns.Value();

    TRACE_AddInstrumentFunction(Trace, 0);
    PIN_AddFiniFunction(Fini, 0);

    PIN_StartProgram();    // Never returns
    return 0;
}

/* ===================================================================== */
/* eof */
/* ===================================================================== */
