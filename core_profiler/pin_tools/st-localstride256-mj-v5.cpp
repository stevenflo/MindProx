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
#include <cassert>
#include <map>
#include <utility> /* for pair */
#include <vector>

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

typedef map<ADDRINT, ADDRINT> LOCAL_STRIDE_DS;

LOCAL_STRIDE_DS local_ip_addr_read;
UINT64 icount;
UINT64 bblcount;
UINT64 tmp_icount;
UINT64 tmp_bblcount;

UINT64 ins_count;
UINT64 interval_count = 0;
	
vector<COUNTER> local_byte_stride_buckets; //<0, 0, 1, 2, 2-8,8-32, 32-64, >64
vector<COUNTER> local_cache_stride_buckets;
vector<COUNTER> ack_local_byte_stride_buckets; 
vector<COUNTER> ack_local_cache_stride_buckets;

void init_vars() 
{
	local_ip_addr_read.clear();
	icount = 0;
	bblcount = 0;
	ins_count = 0;
	tmp_icount = 0;
	tmp_bblcount = 0;
}
	
void init_stride_buckets() {
	local_byte_stride_buckets.resize(257);
	local_cache_stride_buckets.resize(257);
	ack_local_byte_stride_buckets.resize(257);
	ack_local_cache_stride_buckets.resize(257);
	
	for(UINT32 i = 0; i < 257; i++) {
		local_byte_stride_buckets[i] = 0;
		local_cache_stride_buckets[i] = 0;
		ack_local_byte_stride_buckets[i] = 0;
		ack_local_cache_stride_buckets[i] = 0;
	}
}

INT32 check_stride_bucket(ADDRINT new_addr, ADDRINT last_addr) {
	ADDRINT this_str;
        if(new_addr == last_addr) {
		this_str = 0;
        }
	else if(new_addr > last_addr) {
		this_str = new_addr - last_addr;
	}
	else if(last_addr > new_addr) {
                this_str = last_addr - new_addr;
	}
	else {
		assert(0);
	}
	assert(this_str >= 0);
	if(this_str > 256) {
		this_str = 256;
	}
	//cout << "New addr = " << new_addr << ", Last addr = " << last_addr << ", this_str = " << this_str << endl;

	return this_str;	
}

/****************************************************/
VOID emit_stats(THREADID tid); //forward prototype
VOID Fini(int, VOID * v);

/* ===================================================================== */

VOID docount(THREADID tid, ADDRINT c) { 
	icount += c; 	//Dynamic Instruction Count	
	bblcount += 1;
	tmp_icount += c; 	//Dynamic Instruction Count	
	tmp_bblcount += 1;
}

static VOID RecordMem(THREADID tid, VOID * ip, VOID * addr, INT32 size, BOOL isPrefetch, BOOL isRead)
{
        ADDRINT full_addr = (ADDRINT) addr;
        ADDRINT new_cache_addr = ((ADDRINT) (addr)) >> 6;               //64-byte blocks
        ADDRINT inst_ptr = (ADDRINT) (ip);

        if (!isPrefetch) {
                LOCAL_STRIDE_DS::iterator iter;
		//if(isRead) {
		INT32 byte_str_bucket_id = -1;
		INT32 cache_str_bucket_id = -1;
					
		//Local Stride
		iter = local_ip_addr_read.find(inst_ptr);
		if(iter == local_ip_addr_read.end()) {
			local_ip_addr_read[inst_ptr] = full_addr;
		}
		else {
			byte_str_bucket_id = check_stride_bucket(full_addr, iter->second);
			local_byte_stride_buckets[byte_str_bucket_id] += 1;
					
			cache_str_bucket_id = check_stride_bucket(new_cache_addr, ((iter->second) >> 6));
			local_cache_stride_buckets[cache_str_bucket_id] += 1;				
			iter->second = full_addr;		
		}
    }
}

VOID do_ins_count(THREADID tid)
{

    ins_count++;
    if(0 == ins_count % interval_ins)
    {
	// emit the "normal" dynamic stats 
	*iout << "# EMIT_DYNAMIC_STATS" << endl;
    
	*iout << "Interval Number = " << interval_count++ << endl;
	
	*iout << "# instructions = "<< tmp_icount<< ", basic blocks = " << tmp_bblcount << std::endl;
    tmp_icount = tmp_bblcount = 0;
	   
	*iout << "ins_count = "<< ins_count << endl;
		
	for(int i = 0; i < 257; i++)  {  
		*iout << "Local Byte Stride Bucket "<< i << " is equal to " << local_byte_stride_buckets[i] - ack_local_byte_stride_buckets[i] << endl;
		ack_local_byte_stride_buckets[i] = local_byte_stride_buckets[i];
	}	
	*iout << std::endl;
	for(int i = 0; i < 257; i++) {   
		*iout << "Local Cache Stride Bucket "<< i << " is equal to " << local_cache_stride_buckets[i] - ack_local_cache_stride_buckets[i] << endl;
		ack_local_cache_stride_buckets[i] = local_cache_stride_buckets[i];
	}

	*iout << std::endl;
	*iout << std::endl;

	//DumpStats(*out, cstats, KnobProfilePredicated, "$dynamic-counts",tid);
	*iout << "# END_DYNAMIC_STATS" <<  endl;
    }
}

/************************************************************************************/

VOID Trace(TRACE trace, VOID *v)
{
    BOOL isRead = 1, isWrite = 0;
    //static UINT32 basic_blocks = 0;
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
            if (INS_IsMemoryRead(ins)) {
                INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)RecordMem, IARG_THREAD_ID, IARG_INST_PTR, IARG_MEMORYREAD_EA, IARG_MEMORYREAD_SIZE, IARG_BOOL, INS_IsPrefetch(ins), IARG_BOOL, isRead, IARG_END);
            }

            if (INS_HasMemoryRead2(ins)) {
                INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)RecordMem, IARG_THREAD_ID, IARG_INST_PTR, IARG_MEMORYREAD2_EA, IARG_MEMORYREAD_SIZE, IARG_BOOL, INS_IsPrefetch(ins), IARG_BOOL, isRead, IARG_END);
            }

	    if( INS_IsMemoryWrite(ins) ){ // instruction has memory write operand
		INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)RecordMem, IARG_THREAD_ID, IARG_INST_PTR, IARG_MEMORYWRITE_EA, IARG_MEMORYWRITE_SIZE, IARG_BOOL, INS_IsPrefetch(ins), IARG_BOOL, isWrite, IARG_END);
	    }
	    
	    INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)do_ins_count, IARG_THREAD_ID, IARG_END);
	    
        }
    }
}

/* ===================================================================== */
VOID emit_stats(THREADID tid)
{
    // emit the "normal" dynamic stats 
    *out << "# EMIT_DYNAMIC_STATS FOR TID " << tid << endl;
	
    *out << "# instructions = "<< icount<< ", basic blocks = " << bblcount << std::endl;
		
    for(int i = 0; i < 257; i++)  {  
        *out << "Local Byte Stride Bucket "<< i << " is equal to " << local_byte_stride_buckets[i] << endl;
    }	
    *out << std::endl;
    for(int i = 0; i < 257; i++) {   
        *out << "Local Cache Stride Bucket "<< i << " is equal to " << local_cache_stride_buckets[i] << endl;
    }

    *out << std::endl;
    *out << std::endl;

    for(int i = 0; i < 257; i++)  {
        *out << "            \""<< i << "\": \"" << local_byte_stride_buckets[i] << "\"," << endl;
    }

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
    iout->close();
}
   
/* ===================================================================== */

int main(int argc, CHAR **argv)
{
    PIN_InitSymbols();
    if( PIN_Init(argc,argv) )
        return Usage();

    init_vars();
    init_stride_buckets();

    string filename =  KnobOutputFile.Value();
    out = new std::ofstream(filename.c_str());
    *out << "# Mix output version 2" << endl;
    filename = KnobIntervalOutputFile.Value();
    iout = new std::ofstream(filename.c_str());

    interval_ins = KnobInterval.Value();

    TRACE_AddInstrumentFunction(Trace, 0);
    PIN_AddFiniFunction(Fini, 0);

    //if( !KnobProfileDynamicOnly.Value() )
    //    IMG_AddInstrumentFunction(Image, 0);

    PIN_StartProgram();    // Never returns
    return 0;
}

/* ===================================================================== */
/* eof */
/* ===================================================================== */
