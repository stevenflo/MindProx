/*************
File created on 2018-07-20 16:31:06.827644
input file: ../../data/mcf-profile/mcf.json
input statistics
****************/
#include<stdio.h>
#define MAX 255*1024 + 252*1024
#define ITERATIONS 236889
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
ptr0 = (char*) &X0[256 * i + 0];
ptr1 = (char*) &X1[72 * i + 0];
ptr2 = (char*) &X2[0 * i + 0];
ptr3 = (char*) &X3[8 * i + 0];
ptr4 = (char*) &X4[216 * i + 0];
ptr5 = (char*) &X5[104 * i + 0];
ptr6 = (char*) &X6[32 * i + 0];
ptr7 = (char*) &X7[144 * i + 0];
__asm__ __volatile__ ("mov %0, %%eax\n\t"
"mov %1, %%r8\n\t"
"mov %2, %%r9\n\t"
"mov %3, %%r10\n\t"
"mov %4, %%r11\n\t"
"mov %5, %%r12\n\t"
"mov %6, %%r13\n\t"
"mov %7, %%r14\n\t"
"mov %8, %%r15\n\t"
"BBL0INS0: add 0(%%r8), %%ebx\n\t"
"BBL0INS1: add %%ebx, %%ebx\n\t"
"BBL0INS2: test $0, %%eax\n\t"
"BBL0INS3: jz BBL1INS0\n\t"
"BBL1INS0: mov %%ebx, 256(%%r13)\n\t"
"BBL1INS1: add %%esp, %%edx\n\t"
"BBL1INS2: add %%edx, %%ebx\n\t"
"BBL1INS3: test $0, %%eax\n\t"
"BBL1INS4: jz BBL2INS0\n\t"
"BBL2INS0: add 256(%%r8), %%ebx\n\t"
"BBL2INS1: add %%ebx, %%ebx\n\t"
"BBL2INS2: add %%ebx, %%ecx\n\t"
"BBL2INS3: test $0, %%eax\n\t"
"BBL2INS4: jz BBL3INS0\n\t"
"BBL3INS0: add 256(%%r15), %%ecx\n\t"
"BBL3INS1: add %%ecx, %%edx\n\t"
"BBL3INS2: add 256(%%r14), %%edx\n\t"
"BBL3INS3: test $0, %%eax\n\t"
"BBL3INS4: jz BBL4INS0\n\t"
"BBL4INS0: add 200(%%r14), %%ebx\n\t"
"BBL4INS1: mov %%ebx, 512(%%r13)\n\t"
"BBL4INS2: test $1, %%eax\n\t"
"BBL4INS3: jz BBL5INS0\n\t"
"BBL5INS0: add %%esp, %%edx\n\t"
"BBL5INS1: add 256(%%r12), %%ecx\n\t"
"BBL5INS2: test $0, %%eax\n\t"
"BBL5INS3: jz BBL6INS0\n\t"
"BBL6INS0: add %%ecx, %%ecx\n\t"
"BBL6INS1: add %%ecx, %%ebx\n\t"
"BBL6INS2: mov %%ecx, 280(%%r12)\n\t"
"BBL6INS3: test $0, %%eax\n\t"
"BBL6INS4: jz BBL7INS0\n\t"
"BBL7INS0: add %%esp, %%ecx\n\t"
"BBL7INS1: add 256(%%r11), %%ecx\n\t"
"BBL7INS2: test $1, %%eax\n\t"
"BBL7INS3: jz BBL8INS0\n\t"
"BBL8INS0: add 256(%%r10), %%ecx\n\t"
"BBL8INS1: add 512(%%r11), %%ebx\n\t"
"BBL8INS2: add 512(%%r10), %%ecx\n\t"
"BBL8INS3: test $0, %%eax\n\t"
"BBL8INS4: jz BBL9INS0\n\t"
"BBL9INS0: add %%ecx, %%ecx\n\t"
"BBL9INS1: add 768(%%r10), %%ecx\n\t"
"BBL9INS2: add %%ecx, %%edx\n\t"
"BBL9INS3: test $0, %%eax\n\t"
"BBL9INS4: jz BBL10INS0\n\t"
"BBL10INS0: add %%edx, %%edx\n\t"
"BBL10INS1: add %%edx, %%edx\n\t"
"BBL10INS2: add 256(%%r9), %%ecx\n\t"
"BBL10INS3: test $0, %%eax\n\t"
"BBL10INS4: jz BBL11INS0\n\t"
"BBL11INS0: add 768(%%r11), %%edx\n\t"
"BBL11INS1: add %%edx, %%edx\n\t"
"BBL11INS2: add 728(%%r11), %%ebx\n\t"
"BBL11INS3: test $0, %%eax\n\t"
"BBL11INS4: jz BBL12INS0\n\t"
"BBL12INS0: mov %%ebx, 1024(%%r10)\n\t"
"BBL12INS1: add %%esp, %%ecx\n\t"
"BBL12INS2: add %%ecx, %%ecx\n\t"
"BBL12INS3: add 512(%%r9), %%ecx\n\t"
"BBL12INS4: test $0, %%eax\n\t"
"BBL12INS5: jz BBL13INS0\n\t"
"BBL13INS0: add 768(%%r9), %%ecx\n\t"
"BBL13INS1: add 1280(%%r10), %%ecx\n\t"
"BBL13INS2: test $0, %%eax\n\t"
"BBL13INS3: jz BBL14INS0\n\t"
"BBL14INS0: add %%esp, %%edx\n\t"
"BBL14INS1: add 512(%%r8), %%edx\n\t"
"BBL14INS2: add %%edx, %%edx\n\t"
"BBL14INS3: test $0, %%eax\n\t"
"BBL14INS4: jz BBL15INS0\n\t"
"BBL15INS0: add 768(%%r8), %%ebx\n\t"
"BBL15INS1: add 1024(%%r9), %%edx\n\t"
"BBL15INS2: test $0, %%eax\n\t"
"BBL15INS3: jz BBL16INS0\n\t"
"BBL16INS0: add %%edx, %%edx\n\t"
"BBL16INS1: add 984(%%r11), %%ebx\n\t"
"BBL16INS2: test $1, %%eax\n\t"
"BBL16INS3: jz BBL17INS0\n\t"
"BBL17INS0: add 1000(%%r11), %%edx\n\t"
"BBL17INS1: add 1216(%%r11), %%edx\n\t"
"BBL17INS2: add 1536(%%r10), %%ecx\n\t"
"BBL17INS3: test $1, %%eax\n\t"
"BBL17INS4: jz BBL18INS0\n\t"
"BBL18INS0: add 1024(%%r8), %%ebx\n\t"
"BBL18INS1: add 800(%%r8), %%edx\n\t"
"BBL18INS2: add 1792(%%r10), %%ecx\n\t"
"BBL18INS3: test $0, %%eax\n\t"
"BBL18INS4: jz BBL19INS0\n\t"
"BBL19INS0: add 2048(%%r10), %%ecx\n\t"
"BBL19INS1: add %%ebx, %%ecx\n\t"
"BBL19INS2: add %%ecx, %%ebx\n\t"
"BBL19INS3: test $0, %%eax\n\t"
"BBL19INS4: jz BBL20INS0\n\t"
"BBL20INS0: add %%ebx, %%edx\n\t"
"BBL20INS1: add 1280(%%r9), %%ecx\n\t"
"BBL20INS2: test $0, %%eax\n\t"
"BBL20INS3: jz BBL21INS0\n\t"
"BBL21INS0: add %%ecx, %%ebx\n\t"
"BBL21INS1: add %%ebx, %%edx\n\t"
"BBL21INS2: test $0, %%eax\n\t"
"BBL21INS3: jz BBL22INS0\n\t"
"BBL22INS0: add %%ebx, %%ecx\n\t"
"BBL22INS1: mov %%ecx, 1056(%%r8)\n\t"
"BBL22INS2: add 832(%%r8), %%ecx\n\t"
"BBL22INS3: add 1088(%%r8), %%ebx\n\t"
"BBL22INS4: test $0, %%eax\n\t"
"BBL22INS5: jz BBL23INS0\n\t"
"BBL23INS0: add 1072(%%r8), %%ebx\n\t"
"BBL23INS1: add %%ebx, %%ebx\n\t"
"BBL23INS2: add %%ecx, %%ecx\n\t"
"BBL23INS3: test $0, %%eax\n\t"
"BBL23INS4: jz BBL24INS0\n\t"
"BBL24INS0: add %%esp, %%ebx\n\t"
"BBL24INS1: mov %%ebx, 1328(%%r8)\n\t"
"BBL24INS2: test $0, %%eax\n\t"
"BBL24INS3: jz BBL25INS0\n\t"
"BBL25INS0: add %%esp, %%ecx\n\t"
"BBL25INS1: add %%ecx, %%ecx\n\t"
"BBL25INS2: add 1584(%%r8), %%ebx\n\t"
"BBL25INS3: test $1, %%eax\n\t"
"BBL25INS4: jz BBL26INS0\n\t"
"BBL26INS0: add 1640(%%r8), %%ebx\n\t"
"BBL26INS1: add %%ecx, %%edx\n\t"
"BBL26INS2: test $1, %%eax\n\t"
"BBL26INS3: jz BBL27INS0\n\t"
"BBL27INS0: add 1672(%%r8), %%ebx\n\t"
"BBL27INS1: add %%ebx, %%edx\n\t"
"BBL27INS2: add 1536(%%r9), %%ecx\n\t"
"BBL27INS3: test $0, %%eax\n\t"
"BBL27INS4: jz BBL28INS0\n\t"
"BBL28INS0: mov %%ecx, 1552(%%r9)\n\t"
"BBL28INS1: add 1928(%%r8), %%ebx\n\t"
"BBL28INS2: test $1, %%eax\n\t"
"BBL28INS3: jz BBL29INS0\n\t"
"BBL29INS0: add %%ebx, %%ecx\n\t"
"BBL29INS1: add %%ecx, %%ebx\n\t"
"BBL29INS2: test $0, %%eax\n\t"
"BBL29INS3: jz BBL30INS0\n\t"
"BBL30INS0: add 2184(%%r8), %%ebx\n\t"
"BBL30INS1: add %%ebx, %%ebx\n\t"
"BBL30INS2: add %%ebx, %%ecx\n\t"
"BBL30INS3: test $0, %%eax\n\t"
"BBL30INS4: jz BBL31INS0\n\t"
"BBL31INS0: add 2376(%%r8), %%ebx\n\t"
"BBL31INS1: add %%ebx, %%ecx\n\t"
"BBL31INS2: test $0, %%eax\n\t"
"BBL31INS3: jz BBL32INS0\n\t"
"BBL32INS0: mov %%ecx, 1808(%%r9)\n\t"
"BBL32INS1: add %%esp, %%edx\n\t"
"BBL32INS2: add %%ebx, %%ecx\n\t"
"BBL32INS3: test $0, %%eax\n\t"
"BBL32INS4: jz BBL33INS0\n\t"
"BBL33INS0: add 2064(%%r9), %%edx\n\t"
"BBL33INS1: test $0, %%eax\n\t"
"BBL33INS2: jz BBL34INS0\n\t"
"BBL34INS0: add 1840(%%r9), %%ecx\n\t"
"BBL34INS1: test $0, %%eax\n\t"
"BBL34INS2: jz BBL35INS0\n\t"
"BBL35INS0: add %%ecx, %%ecx\n\t"
"BBL35INS1: add 2632(%%r8), %%edx\n\t"
"BBL35INS2: add 2888(%%r8), %%ecx\n\t"
"BBL35INS3: test $0, %%eax\n\t"
"BBL35INS4: jz BBL36INS0\n\t"
"BBL36INS0: add 3144(%%r8), %%ecx\n\t"
"BBL36INS1: add %%ecx, %%ecx\n\t"
"BBL36INS2: test $1, %%eax\n\t"
"BBL36INS3: jz BBL37INS0\n\t"
"BBL37INS0: add %%esp, %%ecx\n\t"
"BBL37INS1: add 3400(%%r8), %%edx\n\t"
"BBL37INS2: add %%edx, %%ecx\n\t"
"BBL37INS3: add %%ecx, %%ebx\n\t"
"BBL37INS4: test $1, %%eax\n\t"
"BBL37INS5: jz BBL38INS0\n\t"
"BBL38INS0: add 3624(%%r8), %%ecx\n\t"
"BBL38INS1: add %%ecx, %%edx\n\t"
"BBL38INS2: test $0, %%eax\n\t"
"BBL38INS3: jz BBL39INS0\n\t"
"BBL39INS0: add 3608(%%r8), %%ebx\n\t"
"BBL39INS1: add 3864(%%r8), %%edx\n\t"
"BBL39INS2: test $0, %%eax\n\t"
"BBL39INS3: jz BBL40INS0\n\t"
"BBL40INS0: add %%edx, %%ebx\n\t"
"BBL40INS1: add %%ebx, %%edx\n\t"
"BBL40INS2: add %%ebx, %%ebx\n\t"
"BBL40INS3: test $1, %%eax\n\t"
"BBL40INS4: jz BBL41INS0\n\t"
"BBL41INS0: mov %%ebx, 3848(%%r8)\n\t"
"BBL41INS1: test $1, %%eax\n\t"
"BBL41INS2: jz BBL42INS0\n\t"
"BBL42INS0: add 4104(%%r8), %%edx\n\t"
"BBL42INS1: add %%edx, %%ebx\n\t"
"BBL42INS2: add %%ebx, %%edx\n\t"
"BBL42INS3: test $0, %%eax\n\t"
"BBL42INS4: jz BBL43INS0\n\t"
"BBL43INS0: add 4360(%%r8), %%ebx\n\t"
"BBL43INS1: add 4616(%%r8), %%ebx\n\t"
"BBL43INS2: test $1, %%eax\n\t"
"BBL43INS3: jz BBL44INS0\n\t"
"BBL44INS0: add %%ebx, %%ebx\n\t"
"BBL44INS1: add 4872(%%r8), %%ebx\n\t"
"BBL44INS2: add 5128(%%r8), %%ecx\n\t"
"BBL44INS3: test $0, %%eax\n\t"
"BBL44INS4: jz BBL45INS0\n\t"
"BBL45INS0: add 5200(%%r8), %%ebx\n\t"
"BBL45INS1: add %%ebx, %%edx\n\t"
"BBL45INS2: add %%edx, %%ecx\n\t"
"BBL45INS3: test $0, %%eax\n\t"
"BBL45INS4: jz BBL46INS0\n\t"
"BBL46INS0: add %%ebx, %%edx\n\t"
"BBL46INS1: add 5456(%%r8), %%edx\n\t"
"BBL46INS2: test $0, %%eax\n\t"
"BBL46INS3: jz BBL47INS0\n\t"
"BBL47INS0: add %%edx, %%edx\n\t"
"BBL47INS1: add %%ebx, %%edx\n\t"
"BBL47INS2: mov %%ebx, 5712(%%r8)\n\t"
"BBL47INS3: test $0, %%eax\n\t"
"BBL47INS4: jz BBL48INS0\n\t"
"BBL48INS0: add 5968(%%r8), %%ebx\n\t"
"BBL48INS1: add %%ebx, %%ecx\n\t"
"BBL48INS2: add 6224(%%r8), %%ecx\n\t"
"BBL48INS3: test $1, %%eax\n\t"
"BBL48INS4: jz BBL49INS0\n\t"
"BBL49INS0: add %%ebx, %%ebx\n\t"
"BBL49INS1: add 6480(%%r8), %%ebx\n\t"
"BBL49INS2: add 6736(%%r8), %%ebx\n\t"
"BBL49INS3: test $0, %%eax\n\t"
"BBL49INS4: jz BBL50INS0\n\t"
"BBL50INS0: add %%edx, %%ebx\n\t"
"BBL50INS1: add 6992(%%r8), %%ebx\n\t"
"BBL50INS2: add 7248(%%r8), %%ebx\n\t"
"BBL50INS3: test $0, %%eax\n\t"
"BBL50INS4: jz BBL51INS0\n\t"
"BBL51INS0: add 7504(%%r8), %%ebx\n\t"
"BBL51INS1: add 2304(%%r10), %%ebx\n\t"
"BBL51INS2: add 768(%%r13), %%ebx\n\t"
"BBL51INS3: test $0, %%eax\n\t"
::"m"(i), "m"(ptr0), "m"(ptr1), "m"(ptr2), "m"(ptr3), "m"(ptr4), "m"(ptr5), "m"(ptr6), "m"(ptr7):"memory", "cc", "esp", "edi", "ebx", "ecx", "edx", "st", "eax", "r8", "r9", "r10", "r11", "r12", "r13", "r14", "r15");
}}
}