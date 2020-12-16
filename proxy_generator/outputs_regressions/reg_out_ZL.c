/*************
File created on 2019-04-19 14:05:28.423652
input file: /export/zachary/data/spec_avg_proxies/mcf_r/mcf_r_initial/mcf_r_new.json
input statistics
****************/
#include<stdio.h>
#define MAX 255*1024 + 252*1024
#define ITERATIONS 3079644
char X0[197099520];
char X1[197099520];
char X2[197099520];
char X3[197099520];
char X4[197099520];
char X5[197099520];
char X6[197099520];
char X7[197099520];
void main (void)  {
int i;
int j;
char* ptr0;
char* ptr1;
char* ptr2;
char* ptr3;
char* ptr4;
char* ptr5;
char* ptr6;
char* ptr7;
for (j = 0; j < 5; j++) {
for (i = 1; i < ITERATIONS; i++) {
ptr0 = (char*) &X0[64 * i + 448];
ptr1 = (char*) &X1[64 * i + 0];
ptr2 = (char*) &X2[64 * i + 0];
ptr3 = (char*) &X3[64 * i + 0];
ptr4 = (char*) &X4[64 * i + 0];
ptr5 = (char*) &X5[64 * i + 0];
ptr6 = (char*) &X6[64 * i + 0];
ptr7 = (char*) &X7[64 * i + 0];
__asm__ __volatile__ ("mov %0, %%eax\n\t"
"mov %1, %%r8d\n\t"
"mov %2, %%r9d\n\t"
"mov %3, %%r10d\n\t"
"mov %4, %%r11d\n\t"
"mov %5, %%r12d\n\t"
"mov %6, %%r13d\n\t"
"mov %7, %%r14d\n\t"
"mov %8, %%r15d\n\t"
"BBL0INS1: mov %%ebx, (%%r8,%%r15,4)\n\t"
"BBL51INS2: test $1, %%eax\n\t"
::"m"(i), "m"(ptr0), "m"(ptr1), "m"(ptr2), "m"(ptr3), "m"(ptr4), "m"(ptr5), "m"(ptr6), "m"(ptr7):"memory", "cc", "esp", "edi", "ebx", "ecx", "edx", "st", "eax", "r8", "r9", "r10", "r11", "r12", "r13", "r14", "r15");
}}
}
