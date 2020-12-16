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

UINT64 icount = 0;
UINT64 bblcount = 0;
UINT64 tmp_icount = 0;
UINT64 tmp_bblcount = 0;

UINT64 ins_count = 0;

UINT64 tmp_loadcount = 0;
UINT64 tmp_storecount = 0;
UINT64 tmp_controlcount = 0;
UINT64 tmp_condBrcount = 0;
UINT64 tmp_fpcount = 0;
UINT64 tmp_fpmulcount = 0;
UINT64 tmp_fpdivcount = 0;
UINT64 tmp_intcount = 0;
UINT64 tmp_intmulcount = 0;
UINT64 tmp_intdivcount = 0;
UINT64 tmp_othercount = 0;
UINT64 tmp_syscallcount = 0;       

UINT64 loadcount = 0;
UINT64 storecount = 0;
UINT64 controlcount = 0;
UINT64 condBrcount = 0;
UINT64 fpcount = 0;
UINT64 fpmulcount = 0;
UINT64 fpdivcount = 0;
UINT64 intcount = 0;
UINT64 intmulcount = 0;
UINT64 intdivcount = 0;
UINT64 othercount = 0;
UINT64 syscallcount = 0;       

UINT32 interval_count = 0;

/****************************************************/
VOID emit_stats(THREADID tid); //forward prototype
VOID Fini(int, VOID * v);


/* ===================================================================== */
static VOID docount(THREADID tid, ADDRINT c) { 
	icount += c; 	//Dynamic Instruction Count	
	tmp_icount += c; 	//Dynamic Instruction Count	
	bblcount += 1;
    tmp_bblcount += 1;
}

static VOID do_loadcount(THREADID tid) {
        tmp_loadcount += 1;
}

static VOID do_storecount(THREADID tid) {
        tmp_storecount += 1;
}

static VOID do_controlcount(THREADID tid) {
        tmp_controlcount += 1;
}

static VOID do_condBrcount(THREADID tid) {
        tmp_condBrcount += 1;
}

static VOID do_fpcount(THREADID tid) {
        tmp_fpcount += 1;
}

static VOID do_fpdivcount(THREADID tid) {
        tmp_fpdivcount += 1;
}
static VOID do_fpmulcount(THREADID tid) {
        tmp_fpmulcount += 1;
}

static VOID do_intcount(THREADID tid) {
        tmp_intcount += 1;
}

static VOID do_intdivcount(THREADID tid) {
        tmp_intdivcount += 1;
}

static VOID do_intmulcount(THREADID tid) {
        tmp_intmulcount += 1;
}

static VOID do_othercount(THREADID tid) {
        tmp_othercount += 1;
}

static VOID do_syscallcount(THREADID tid) {
        tmp_syscallcount += 1;
}

static VOID do_ins_count(THREADID tid) {
	ins_count += 1;
	if(0 == ins_count % interval_ins)
	{
    // emit the "normal" dynamic stats 
    *iout << "Interval Number = " << interval_count << std::endl;
    *iout << "Dynamic Instruction Count = " << tmp_icount <<", Dyn BBL Count = " << tmp_bblcount << std::endl;
	
    //*iout << "<DynInsCount> " << icount << std::endl;
    //*iout << "<BBLCount>" << bblcount << std::endl;
    *iout << "<TotInsCount>" << ins_count << std::endl;
    *iout << "<IntCount> " << tmp_intcount<< std::endl;
    *iout << "<IntMulCount > " << tmp_intmulcount << std::endl;
    *iout << "<IntDivCount > " << tmp_intdivcount << std::endl;
    *iout << "<FPCount> " << tmp_fpcount << std::endl;
    *iout << "<FPMulCount> " << tmp_fpmulcount << std::endl;
    *iout << "<FPDivCount> " << tmp_fpdivcount << std::endl;
    *iout << "<LdCount> " << tmp_loadcount << std::endl;
    *iout << "<StCount> " << tmp_storecount << std::endl;
    *iout << "<Br/CallCount> " << tmp_controlcount << std::endl;
    *iout << "<CondBrCount> " << tmp_condBrcount << std::endl;
    *iout << "<OtherCount> " << tmp_othercount << std::endl;
    *iout << "<SysCallCount> " << tmp_syscallcount << std::endl;

    *iout << std::endl;
    
    //accumulate the counts
    interval_count ++;
    loadcount    += tmp_loadcount    ;
    storecount   += tmp_storecount   ;
    controlcount += tmp_controlcount ;
    condBrcount  += tmp_condBrcount  ;
    fpcount      += tmp_fpcount      ;
    fpmulcount   += tmp_fpmulcount   ;
    fpdivcount   += tmp_fpdivcount   ;
    intcount     += tmp_intcount     ;
    intmulcount  += tmp_intmulcount  ;
    intdivcount  += tmp_intdivcount  ;
    othercount   += tmp_othercount   ;
    syscallcount += tmp_syscallcount ;       

    //clear temperory counts
    tmp_icount = 0;
    tmp_bblcount = 0;
    tmp_loadcount    = 0;
    tmp_storecount   = 0;
    tmp_controlcount = 0;
    tmp_condBrcount  = 0;
    tmp_fpcount      = 0;
    tmp_fpmulcount   = 0;
    tmp_fpdivcount   = 0;
    tmp_intcount     = 0;
    tmp_intmulcount  = 0;
    tmp_intdivcount  = 0;
    tmp_othercount   = 0;
    tmp_syscallcount = 0;
	}
}
/* ===================================================================== */

VOID Trace(TRACE trace, VOID *v)
{
    xed_iclass_enum_t iclass;	
    //static UINT32 basic_blocks = 0;

    if ( KnobNoSharedLibs.Value()
         && IMG_Type(SEC_Img(RTN_Sec(TRACE_Rtn(trace)))) == IMG_TYPE_SHAREDLIB)
        return;

    for (BBL bbl = TRACE_BblHead(trace); BBL_Valid(bbl); bbl = BBL_Next(bbl))
    {
	BBL_InsertCall(bbl, IPOINT_ANYWHERE, AFUNPTR(docount), IARG_THREAD_ID, IARG_UINT32, BBL_NumIns(bbl), IARG_END);
        const INS head = BBL_InsHead(bbl);
        if (! INS_Valid(head)) continue;
        
	for (INS ins = head; INS_Valid(ins); ins = INS_Next(ins)) {
            INS_InsertCall(ins, IPOINT_BEFORE, AFUNPTR(do_ins_count), IARG_THREAD_ID, IARG_END);

            iclass = static_cast<xed_iclass_enum_t>(INS_Opcode(ins));

            if(INS_IsMemoryRead(ins) || INS_HasMemoryRead2(ins)) {
                INS_InsertCall(ins, IPOINT_BEFORE, AFUNPTR(do_loadcount), IARG_THREAD_ID, IARG_END);
            }
            if(INS_IsMemoryWrite(ins)) {
                INS_InsertCall(ins, IPOINT_BEFORE, AFUNPTR(do_storecount), IARG_THREAD_ID, IARG_END);
            }
            if(INS_IsBranchOrCall(ins)) {
                INS_InsertCall(ins, IPOINT_BEFORE, AFUNPTR(do_controlcount), IARG_THREAD_ID, IARG_END);
                if(INS_IsBranch(ins)) {
                    INS_InsertCall(ins, IPOINT_BEFORE, AFUNPTR(do_condBrcount), IARG_THREAD_ID, IARG_END);
                }
            }
            if((INS_Category(ins) == XED_CATEGORY_FCMOV) || (INS_Category(ins) == XED_CATEGORY_X87_ALU) || (INS_Category(ins) == XED_CATEGORY_LOGICAL_FP)) {//An issue was found for this on 10/15/2018 that no floating point instructions were being processed
	      //Steven changed this if statement to reflect the 
                if ((iclass == XED_ICLASS_FDIV) || (iclass == XED_ICLASS_FDIVR) || (iclass == XED_ICLASS_FDIVRP) || (iclass == XED_ICLASS_FDIVP))
                    INS_InsertCall(ins, IPOINT_BEFORE, AFUNPTR(do_fpdivcount), IARG_THREAD_ID, IARG_END);
                else if ((iclass == XED_ICLASS_FMUL) || (iclass == XED_ICLASS_PFMUL) || (iclass == XED_ICLASS_FMULP))
                    INS_InsertCall(ins, IPOINT_BEFORE, AFUNPTR(do_fpmulcount), IARG_THREAD_ID, IARG_END);
                 else
                    INS_InsertCall(ins, IPOINT_BEFORE, AFUNPTR(do_fpcount), IARG_THREAD_ID, IARG_END);
            }
            else if((INS_Category(ins) == XED_CATEGORY_LOGICAL) || (INS_Category(ins) == XED_CATEGORY_BINARY) || (INS_Category(ins) == XED_CATEGORY_BITBYTE) || (INS_Category(ins) == XED_CATEGORY_FLAGOP)) {
                if((iclass == XED_ICLASS_IMUL) || (iclass == XED_ICLASS_MUL) || (iclass == XED_ICLASS_PMULLW) || (iclass == XED_ICLASS_PMULUDQ) || (iclass == XED_ICLASS_PMULHUW) || (iclass == XED_ICLASS_PMULHW) || (iclass == XED_ICLASS_MULPS) || (iclass == XED_ICLASS_MULSS) || (iclass == XED_ICLASS_MULPD) || (iclass == XED_ICLASS_MULSD))
                     INS_InsertCall(ins, IPOINT_BEFORE, AFUNPTR(do_intmulcount), IARG_THREAD_ID, IARG_END);
                else if ((iclass == XED_ICLASS_DIV) || (iclass == XED_ICLASS_IDIV) || (iclass == XED_ICLASS_DIVPS) || (iclass == XED_ICLASS_DIVSS) || (iclass == XED_ICLASS_DIVPD) || (iclass == XED_ICLASS_DIVSD))
                    INS_InsertCall(ins, IPOINT_BEFORE, AFUNPTR(do_intdivcount), IARG_THREAD_ID, IARG_END);
                else
                    INS_InsertCall(ins, IPOINT_BEFORE, AFUNPTR(do_intcount), IARG_THREAD_ID, IARG_END);
            }
            else {
                INS_InsertCall(ins, IPOINT_BEFORE, AFUNPTR(do_othercount), IARG_THREAD_ID, IARG_END);
            }
            if( INS_IsSyscall(ins) )
            {
                INS_InsertCall(ins, IPOINT_BEFORE, AFUNPTR(do_syscallcount), IARG_THREAD_ID, IARG_END);
            }
        }
    }
}

/* ===================================================================== */
VOID emit_stats()
{
    //accumulate the counts
    loadcount    += tmp_loadcount    ;
    storecount   += tmp_storecount   ;
    controlcount += tmp_controlcount ;
    condBrcount  += tmp_condBrcount  ;
    fpcount      += tmp_fpcount      ;
    fpmulcount   += tmp_fpmulcount   ;
    fpdivcount   += tmp_fpdivcount   ;
    intcount     += tmp_intcount     ;
    intmulcount  += tmp_intmulcount  ;
    intdivcount  += tmp_intdivcount  ;
    othercount   += tmp_othercount   ;
    syscallcount += tmp_syscallcount ;       

    // emit the "normal" dynamic stats 
    *out << "Dynamic Instruction Count = " << icount <<", Dyn BBL Count = " << bblcount << std::endl;
	
    *out << "<DynInsCount> " << icount << std::endl;
    *out << "<BBLCount>" << bblcount << std::endl;
    *out << "<TotInsCount>" << ins_count << std::endl;
    *out << "<IntCount> " << intcount<< std::endl;
    *out << "<IntMulCount > " << intmulcount << std::endl;
    *out << "<IntDivCount > " << intdivcount << std::endl;
    *out << "<FPCount> " << fpcount << std::endl;
    *out << "<FPMulCount> " << fpmulcount << std::endl;
    *out << "<FPDivCount> " << fpdivcount << std::endl;
    *out << "<LdCount> " << loadcount << std::endl;
    *out << "<StCount> " << storecount << std::endl;
    *out << "<Br/CallCount> " << controlcount << std::endl;
    *out << "<CondBrCount> " << condBrcount << std::endl;
    *out << "<OtherCount> " << othercount << std::endl;
    *out << "<SysCallCount> " << syscallcount << std::endl;

    *out << endl;
    *out << "# END_DYNAMIC_STATS" <<  endl;
}

VOID Fini(int, VOID * v) // only runs once for the application
{
    *out << "# FINI: end of program" << endl;
    emit_stats();
    out->close();
    iout->close();
}
   
/* ===================================================================== */

int main(int argc, CHAR **argv)
{
    PIN_InitSymbols();//?? Initialize symbol table. the symbol table of the exe?
    if( PIN_Init(argc,argv) )
        return Usage();

    string filename =  KnobOutputFile.Value();
    out = new std::ofstream(filename.c_str());
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
