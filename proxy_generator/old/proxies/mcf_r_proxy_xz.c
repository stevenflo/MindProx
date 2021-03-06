/*************
File created on 2018-07-20 16:30:17.960297
input file: ../../data/mcf-profile/mcf.json
input statistics
****************/
#include<stdio.h>
#define MAX 255*1024 + 252*1024
#define ITERATIONS 236892
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
char* ptr0;
char* ptr1;
char* ptr2;
char* ptr3;
char* ptr4;
char* ptr5;
char* ptr6;
char* ptr7;
for (i = 1; i < ITERATIONS; i++) {
ptr0 = (char*) &X0[256 * i + 512];
ptr1 = (char*) &X1[0 * i + 0];
ptr2 = (char*) &X2[72 * i + 8];
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
"BBL0INS2: test $256, %%eax\n\t"
"BBL0INS3: jz BBL1INS0\n\t"
"BBL1INS0: add 0(%%rbp), %%ebx\n\t"
"BBL1INS1: mov %%ebx, -224(%%r8)\n\t"
"BBL1INS2: add 0(%%rbp), %%ecx\n\t"
"BBL1INS3: test $32, %%eax\n\t"
"BBL1INS4: jz BBL2INS0\n\t"
"BBL2INS0: add %%ecx, %%ecx\n\t"
"BBL2INS1: add %%ecx, %%ecx\n\t"
"BBL2INS2: add -32(%%r8), %%edx\n\t"
"BBL2INS3: test $4, %%eax\n\t"
"BBL2INS4: jz BBL3INS0\n\t"
"BBL3INS0: mov %%edx, -48(%%r8)\n\t"
"BBL3INS1: add 0(%%rbp), %%ecx\n\t"
"BBL3INS2: test $16, %%eax\n\t"
"BBL3INS3: jz BBL4INS0\n\t"
"BBL4INS0: add -64(%%r8), %%edx\n\t"
"BBL4INS1: add 0(%%rbp), %%edx\n\t"
"BBL4INS2: add -288(%%r8), %%edx\n\t"
"BBL4INS3: test $64, %%eax\n\t"
"BBL4INS4: jz BBL5INS0\n\t"
"BBL5INS0: add 0(%%rbp), %%edx\n\t"
"BBL5INS1: mov %%edx, -512(%%r8)\n\t"
"BBL5INS2: test $32, %%eax\n\t"
"BBL5INS3: jz BBL6INS0\n\t"
"BBL6INS0: add 0(%%rbp), %%ecx\n\t"
"BBL6INS1: add -480(%%r8), %%ebx\n\t"
"BBL6INS2: test $256, %%eax\n\t"
"BBL6INS3: jz BBL7INS0\n\t"
"BBL7INS0: add 0(%%rbp), %%ebx\n\t"
"BBL7INS1: add -256(%%r8), %%ebx\n\t"
"BBL7INS2: add %%ebx, %%ecx\n\t"
"BBL7INS3: test $2, %%eax\n\t"
"BBL7INS4: jz BBL8INS0\n\t"
"BBL8INS0: mov %%ecx, -480(%%r8)\n\t"
"BBL8INS1: add %%esp, %%ecx\n\t"
"BBL8INS2: test $32, %%eax\n\t"
"BBL8INS3: jz BBL9INS0\n\t"
"BBL9INS0: add 0(%%rbp), %%ecx\n\t"
"BBL9INS1: add %%ecx, %%edx\n\t"
"BBL9INS2: test $0, %%eax\n\t"
"BBL9INS3: jz BBL10INS0\n\t"
"BBL10INS0: add -288(%%r8), %%edx\n\t"
"BBL10INS1: add %%edx, %%edx\n\t"
"BBL10INS2: add 0(%%rbp), %%edx\n\t"
"BBL10INS3: test $64, %%eax\n\t"
"BBL10INS4: jz BBL11INS0\n\t"
"BBL11INS0: add -272(%%r8), %%ebx\n\t"
"BBL11INS1: add %%ebx, %%edx\n\t"
"BBL11INS2: add %%edx, %%edx\n\t"
"BBL11INS3: add %%edx, %%ecx\n\t"
"BBL11INS4: test $4, %%eax\n\t"
"BBL11INS5: jz BBL12INS0\n\t"
"BBL12INS0: add %%ecx, %%ebx\n\t"
"BBL12INS1: add 0(%%rbp), %%ebx\n\t"
"BBL12INS2: add -256(%%r8), %%ebx\n\t"
"BBL12INS3: test $2, %%eax\n\t"
"BBL12INS4: jz BBL13INS0\n\t"
"BBL13INS0: mov %%ebx, -480(%%r8)\n\t"
"BBL13INS1: add 0(%%rbp), %%ecx\n\t"
"BBL13INS2: add -256(%%r8), %%ebx\n\t"
"BBL13INS3: test $128, %%eax\n\t"
"BBL13INS4: jz BBL14INS0\n\t"
"BBL14INS0: add 0(%%rbp), %%edx\n\t"
"BBL14INS1: add %%edx, %%edx\n\t"
"BBL14INS2: test $16, %%eax\n\t"
"BBL14INS3: jz BBL15INS0\n\t"
"BBL15INS0: add -232(%%r8), %%edx\n\t"
"BBL15INS1: add %%edx, %%edx\n\t"
"BBL15INS2: add %%edx, %%ebx\n\t"
"BBL15INS3: test $128, %%eax\n\t"
"BBL15INS4: jz BBL16INS0\n\t"
"BBL16INS0: add 0(%%rbp), %%edx\n\t"
"BBL16INS1: add -288(%%r8), %%edx\n\t"
"BBL16INS2: add -512(%%r8), %%ecx\n\t"
"BBL16INS3: test $16, %%eax\n\t"
"BBL16INS4: jz BBL17INS0\n\t"
"BBL17INS0: add 256(%%r11), %%ebx\n\t"
"BBL17INS1: add 256(%%r10), %%ebx\n\t"
"BBL17INS2: add 216(%%r10), %%edx\n\t"
"BBL17INS3: test $128, %%eax\n\t"
"BBL17INS4: jz BBL18INS0\n\t"
"BBL18INS0: add -8(%%r10), %%ecx\n\t"
"BBL18INS1: add %%ecx, %%ecx\n\t"
"BBL18INS2: add 256(%%r13), %%ecx\n\t"
"BBL18INS3: test $64, %%eax\n\t"
"BBL18INS4: jz BBL19INS0\n\t"
"BBL19INS0: mov %%esp, 256(%%r15)\n\t"
"BBL19INS1: add 256(%%r14), %%ebx\n\t"
"BBL19INS2: test $32, %%eax\n\t"
"BBL19INS3: jz BBL20INS0\n\t"
"BBL20INS0: add %%ebx, %%ebx\n\t"
"BBL20INS1: add -256(%%r8), %%ebx\n\t"
"BBL20INS2: mov %%ebx, 512(%%r13)\n\t"
"BBL20INS3: test $64, %%eax\n\t"
"BBL20INS4: jz BBL21INS0\n\t"
"BBL21INS0: add 512(%%r14), %%edx\n\t"
"BBL21INS1: add 256(%%r12), %%ecx\n\t"
"BBL21INS2: test $0, %%eax\n\t"
"BBL21INS3: jz BBL22INS0\n\t"
"BBL22INS0: add %%ecx, %%ecx\n\t"
"BBL22INS1: add 288(%%r12), %%ecx\n\t"
"BBL22INS2: add %%edx, %%edx\n\t"
"BBL22INS3: test $128, %%eax\n\t"
"BBL22INS4: jz BBL23INS0\n\t"
"BBL23INS0: mov %%esp, 512(%%r11)\n\t"
"BBL23INS1: add 768(%%r11), %%ecx\n\t"
"BBL23INS2: test $16, %%eax\n\t"
"BBL23INS3: jz BBL24INS0\n\t"
"BBL24INS0: add %%ecx, %%edx\n\t"
"BBL24INS1: add 0(%%r8), %%ecx\n\t"
"BBL24INS2: add 256(%%r8), %%ecx\n\t"
"BBL24INS3: mov %%ecx, 248(%%r10)\n\t"
"BBL24INS4: test $128, %%eax\n\t"
"BBL24INS5: jz BBL25INS0\n\t"
"BBL25INS0: add %%edx, %%edx\n\t"
"BBL25INS1: mov %%ecx, 1024(%%r11)\n\t"
"BBL25INS2: test $64, %%eax\n\t"
"BBL25INS3: jz BBL26INS0\n\t"
"BBL26INS0: add %%esp, %%edx\n\t"
"BBL26INS1: add %%edx, %%ecx\n\t"
"BBL26INS2: add 512(%%r8), %%ebx\n\t"
"BBL26INS3: test $256, %%eax\n\t"
"BBL26INS4: jz BBL27INS0\n\t"
"BBL27INS0: add %%esp, %%ecx\n\t"
"BBL27INS1: add %%edx, %%ecx\n\t"
"BBL27INS2: add 568(%%r8), %%ecx\n\t"
"BBL27INS3: test $128, %%eax\n\t"
"BBL27INS4: jz BBL28INS0\n\t"
"BBL28INS0: add %%esp, %%edx\n\t"
"BBL28INS1: add 1280(%%r11), %%ebx\n\t"
"BBL28INS2: add 824(%%r8), %%ecx\n\t"
"BBL28INS3: test $32, %%eax\n\t"
"BBL28INS4: jz BBL29INS0\n\t"
"BBL29INS0: add 840(%%r8), %%edx\n\t"
"BBL29INS1: add 912(%%r8), %%ebx\n\t"
"BBL29INS2: add 1168(%%r8), %%edx\n\t"
"BBL29INS3: test $2, %%eax\n\t"
"BBL29INS4: jz BBL30INS0\n\t"
"BBL30INS0: add 1360(%%r8), %%ecx\n\t"
"BBL30INS1: add 1584(%%r8), %%ecx\n\t"
"BBL30INS2: test $256, %%eax\n\t"
"BBL30INS3: jz BBL31INS0\n\t"
"BBL31INS0: add 1528(%%r8), %%edx\n\t"
"BBL31INS1: add %%edx, %%ecx\n\t"
"BBL31INS2: add 1784(%%r8), %%ecx\n\t"
"BBL31INS3: test $32, %%eax\n\t"
"BBL31INS4: jz BBL32INS0\n\t"
"BBL32INS0: add %%ecx, %%edx\n\t"
"BBL32INS1: add 2008(%%r8), %%ecx\n\t"
"BBL32INS2: test $2, %%eax\n\t"
"BBL32INS3: jz BBL33INS0\n\t"
"BBL33INS0: add %%ecx, %%ebx\n\t"
"BBL33INS1: add %%ebx, %%edx\n\t"
"BBL33INS2: test $4, %%eax\n\t"
"BBL33INS3: jz BBL34INS0\n\t"
"BBL34INS0: add %%edx, %%ecx\n\t"
"BBL34INS1: add %%ecx, %%ebx\n\t"
"BBL34INS2: mov %%ebx, 1968(%%r8)\n\t"
"BBL34INS3: test $128, %%eax\n\t"
"BBL34INS4: jz BBL35INS0\n\t"
"BBL35INS0: add %%esp, %%ebx\n\t"
"BBL35INS1: add %%ecx, %%ebx\n\t"
"BBL35INS2: add %%ebx, %%edx\n\t"
"BBL35INS3: test $2, %%eax\n\t"
"BBL35INS4: jz BBL36INS0\n\t"
"BBL36INS0: add %%edx, %%edx\n\t"
"BBL36INS1: add 1992(%%r8), %%ecx\n\t"
"BBL36INS2: test $128, %%eax\n\t"
"BBL36INS3: jz BBL37INS0\n\t"
"BBL37INS0: add 1536(%%r11), %%ecx\n\t"
"BBL37INS1: add %%ecx, %%ecx\n\t"
"BBL37INS2: add 1752(%%r11), %%ebx\n\t"
"BBL37INS3: test $32, %%eax\n\t"
"BBL37INS4: jz BBL38INS0\n\t"
"BBL38INS0: mov %%ebx, 1792(%%r11)\n\t"
"BBL38INS1: add 504(%%r10), %%ebx\n\t"
"BBL38INS2: add 760(%%r10), %%ecx\n\t"
"BBL38INS3: test $0, %%eax\n\t"
"BBL38INS4: jz BBL39INS0\n\t"
"BBL39INS0: add 1016(%%r10), %%edx\n\t"
"BBL39INS1: add %%esp, %%ecx\n\t"
"BBL39INS2: test $1, %%eax\n\t"
"BBL39INS3: jz BBL40INS0\n\t"
"BBL40INS0: add %%esp, %%ebx\n\t"
"BBL40INS1: add %%esp, %%edx\n\t"
"BBL40INS2: add %%edx, %%ebx\n\t"
"BBL40INS3: add 1000(%%r10), %%edx\n\t"
"BBL40INS4: test $4, %%eax\n\t"
"BBL40INS5: jz BBL41INS0\n\t"
"BBL41INS0: add 1016(%%r10), %%ebx\n\t"
"BBL41INS1: add 1272(%%r10), %%edx\n\t"
"BBL41INS2: test $128, %%eax\n\t"
"BBL41INS3: jz BBL42INS0\n\t"
"BBL42INS0: add 1528(%%r10), %%edx\n\t"
"BBL42INS1: add %%edx, %%edx\n\t"
"BBL42INS2: add %%ebx, %%edx\n\t"
"BBL42INS3: test $16, %%eax\n\t"
"BBL42INS4: jz BBL43INS0\n\t"
"BBL43INS0: add 2248(%%r8), %%edx\n\t"
"BBL43INS1: add %%edx, %%ecx\n\t"
"BBL43INS2: test $4, %%eax\n\t"
"BBL43INS3: jz BBL44INS0\n\t"
"BBL44INS0: add 2504(%%r8), %%edx\n\t"
"BBL44INS1: add %%edx, %%ebx\n\t"
"BBL44INS2: test $16, %%eax\n\t"
"BBL44INS3: jz BBL45INS0\n\t"
"BBL45INS0: add 2488(%%r8), %%ecx\n\t"
"BBL45INS1: add %%ecx, %%edx\n\t"
"BBL45INS2: add 1784(%%r10), %%ebx\n\t"
"BBL45INS3: add %%edx, %%ecx\n\t"
"BBL45INS4: test $256, %%eax\n\t"
"BBL45INS5: jz BBL46INS0\n\t"
"BBL46INS0: add 2744(%%r8), %%ecx\n\t"
"BBL46INS1: add %%ecx, %%edx\n\t"
"BBL46INS2: add 3000(%%r8), %%edx\n\t"
"BBL46INS3: test $8, %%eax\n\t"
"BBL46INS4: jz BBL47INS0\n\t"
"BBL47INS0: add 3256(%%r8), %%ebx\n\t"
"BBL47INS1: add 3512(%%r8), %%edx\n\t"
"BBL47INS2: test $16, %%eax\n\t"
"BBL47INS3: jz BBL48INS0\n\t"
"BBL48INS0: add %%edx, %%ebx\n\t"
"BBL48INS1: mov %%edx, 3768(%%r8)\n\t"
"BBL48INS2: add %%ebx, %%ecx\n\t"
"BBL48INS3: test $64, %%eax\n\t"
"BBL48INS4: jz BBL49INS0\n\t"
"BBL49INS0: add 4024(%%r8), %%edx\n\t"
"BBL49INS1: add 4280(%%r8), %%ecx\n\t"
"BBL49INS2: add %%edx, %%edx\n\t"
"BBL49INS3: test $256, %%eax\n\t"
"BBL49INS4: jz BBL50INS0\n\t"
"BBL50INS0: add %%edx, %%edx\n\t"
"BBL50INS1: add 4536(%%r8), %%edx\n\t"
"BBL50INS2: add 512(%%r15), %%ecx\n\t"
"BBL50INS3: test $1, %%eax\n\t"
"BBL50INS4: jz BBL51INS0\n\t"
"BBL51INS0: mov %%ecx, 768(%%r15)\n\t"
"BBL51INS1: add %%edx, %%ecx\n\t"
"BBL51INS2: add 1024(%%r15), %%ebx\n\t"
"BBL51INS3: test $32, %%eax\n\t"
::"m"(i), "m"(ptr0), "m"(ptr1), "m"(ptr2), "m"(ptr3), "m"(ptr4), "m"(ptr5), "m"(ptr6), "m"(ptr7):"memory", "cc", "esp", "edi", "ebx", "ecx", "edx", "st", "eax", "r8", "r9", "r10", "r11", "r12", "r13", "r14", "r15");
}
}