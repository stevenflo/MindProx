/*************
File created on 2019-01-17 10:50:31.975803
input file: ../profiler/profile_out/mcf_r_profile_cpy/out.json
input statistics
****************/
#include<stdio.h>
#define MAX 255*1024 + 252*1024
#define ITERATIONS 236891
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
ptr0 = (char*) &X0[256 * i + 376];
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
"BBL0INS1: add 0(%%rbp), %%edx\n\t"
"BBL0INS2: add 72(%%r8), %%ecx\n\t"
"BBL0INS3: test $256, %%eax\n\t"
"BBL0INS4: jz BBL1INS0\n\t"
"BBL1INS0: add 0(%%rbp), %%ecx\n\t"
"BBL1INS1: add 112(%%r8), %%ebx\n\t"
"BBL1INS2: add %%ebx, %%edx\n\t"
"BBL1INS3: add 0(%%rbp), %%ecx\n\t"
"BBL1INS4: test $4, %%eax\n\t"
"BBL1INS5: jz BBL2INS0\n\t"
"BBL2INS0: add -112(%%r8), %%ecx\n\t"
"BBL2INS1: add 0(%%rbp), %%ebx\n\t"
"BBL2INS2: add -152(%%r8), %%ecx\n\t"
"BBL2INS3: test $256, %%eax\n\t"
"BBL2INS4: jz BBL3INS0\n\t"
"BBL3INS0: mov %%ecx, -376(%%r8)\n\t"
"BBL3INS1: add %%esp, %%ecx\n\t"
"BBL3INS2: add 0(%%rbp), %%ecx\n\t"
"BBL3INS3: test $4, %%eax\n\t"
"BBL3INS4: jz BBL4INS0\n\t"
"BBL4INS0: add -344(%%r8), %%ebx\n\t"
"BBL4INS1: add %%ebx, %%edx\n\t"
"BBL4INS2: test $64, %%eax\n\t"
"BBL4INS3: jz BBL5INS0\n\t"
"BBL5INS0: add %%esp, %%edx\n\t"
"BBL5INS1: test $16, %%eax\n\t"
"BBL5INS2: jz BBL6INS0\n\t"
"BBL6INS0: add %%ebx, %%ebx\n\t"
"BBL6INS1: add 0(%%rbp), %%edx\n\t"
"BBL6INS2: test $0, %%eax\n\t"
"BBL6INS3: jz BBL7INS0\n\t"
"BBL7INS0: add %%edx, %%edx\n\t"
"BBL7INS1: add -272(%%r8), %%edx\n\t"
"BBL7INS2: add 0(%%rbp), %%ebx\n\t"
"BBL7INS3: test $64, %%eax\n\t"
"BBL7INS4: jz BBL8INS0\n\t"
"BBL8INS0: add %%ebx, %%ebx\n\t"
"BBL8INS1: add %%ebx, %%ebx\n\t"
"BBL8INS2: test $4, %%eax\n\t"
"BBL8INS3: jz BBL9INS0\n\t"
"BBL9INS0: add %%esp, %%ebx\n\t"
"BBL9INS1: add %%ebx, %%ecx\n\t"
"BBL9INS2: add -48(%%r8), %%ebx\n\t"
"BBL9INS3: test $16, %%eax\n\t"
"BBL9INS4: jz BBL10INS0\n\t"
"BBL10INS0: add 0(%%rbp), %%ebx\n\t"
"BBL10INS1: add %%esp, %%ebx\n\t"
"BBL10INS2: test $2, %%eax\n\t"
"BBL10INS3: jz BBL11INS0\n\t"
"BBL11INS0: add %%esp, %%ebx\n\t"
"BBL11INS1: add 176(%%r8), %%ebx\n\t"
"BBL11INS2: test $64, %%eax\n\t"
"BBL11INS3: jz BBL12INS0\n\t"
"BBL12INS0: add %%esp, %%edx\n\t"
"BBL12INS1: add %%edx, %%edx\n\t"
"BBL12INS2: test $2, %%eax\n\t"
"BBL12INS3: jz BBL13INS0\n\t"
"BBL13INS0: add 0(%%rbp), %%edx\n\t"
"BBL13INS1: mov %%edx, 192(%%r8)\n\t"
"BBL13INS2: add 0(%%rbp), %%edx\n\t"
"BBL13INS3: test $8, %%eax\n\t"
"BBL13INS4: jz BBL14INS0\n\t"
"BBL14INS0: mov %%esp, 224(%%r8)\n\t"
"BBL14INS1: add 0(%%rbp), %%edx\n\t"
"BBL14INS2: test $128, %%eax\n\t"
"BBL14INS3: jz BBL15INS0\n\t"
"BBL15INS0: add %%esp, %%edx\n\t"
"BBL15INS1: add %%edx, %%ebx\n\t"
"BBL15INS2: add 256(%%r8), %%ecx\n\t"
"BBL15INS3: test $0, %%eax\n\t"
"BBL15INS4: jz BBL16INS0\n\t"
"BBL16INS0: add 256(%%r12), %%ebx\n\t"
"BBL16INS1: mov %%ebx, 256(%%r14)\n\t"
"BBL16INS2: add 256(%%r15), %%ebx\n\t"
"BBL16INS3: test $4, %%eax\n\t"
"BBL16INS4: jz BBL17INS0\n\t"
"BBL17INS0: add %%ebx, %%ebx\n\t"
"BBL17INS1: add %%esp, %%ebx\n\t"
"BBL17INS2: test $16, %%eax\n\t"
"BBL17INS3: jz BBL18INS0\n\t"
"BBL18INS0: add %%ebx, %%ebx\n\t"
"BBL18INS1: add %%esp, %%edx\n\t"
"BBL18INS2: add 512(%%r14), %%ebx\n\t"
"BBL18INS3: test $4, %%eax\n\t"
"BBL18INS4: jz BBL19INS0\n\t"
"BBL19INS0: add 256(%%r13), %%ecx\n\t"
"BBL19INS1: add %%ecx, %%ebx\n\t"
"BBL19INS2: add 32(%%r13), %%edx\n\t"
"BBL19INS3: test $8, %%eax\n\t"
"BBL19INS4: jz BBL20INS0\n\t"
"BBL20INS0: add 512(%%r12), %%ebx\n\t"
"BBL20INS1: add %%ebx, %%ecx\n\t"
"BBL20INS2: test $256, %%eax\n\t"
"BBL20INS3: jz BBL21INS0\n\t"
"BBL21INS0: add %%ecx, %%edx\n\t"
"BBL21INS1: add 256(%%r11), %%edx\n\t"
"BBL21INS2: add 256(%%r9), %%edx\n\t"
"BBL21INS3: test $0, %%eax\n\t"
"BBL21INS4: jz BBL22INS0\n\t"
"BBL22INS0: add 512(%%r8), %%ebx\n\t"
"BBL22INS1: add %%ebx, %%ecx\n\t"
"BBL22INS2: test $4, %%eax\n\t"
"BBL22INS3: jz BBL23INS0\n\t"
"BBL23INS0: add 528(%%r8), %%ebx\n\t"
"BBL23INS1: add 472(%%r8), %%ecx\n\t"
"BBL23INS2: test $64, %%eax\n\t"
"BBL23INS3: jz BBL24INS0\n\t"
"BBL24INS0: add 512(%%r9), %%ecx\n\t"
"BBL24INS1: add %%ecx, %%ebx\n\t"
"BBL24INS2: test $4, %%eax\n\t"
"BBL24INS3: jz BBL25INS0\n\t"
"BBL25INS0: add 728(%%r8), %%ebx\n\t"
"BBL25INS1: add 712(%%r8), %%ebx\n\t"
"BBL25INS2: add %%ebx, %%edx\n\t"
"BBL25INS3: test $2, %%eax\n\t"
"BBL25INS4: jz BBL26INS0\n\t"
"BBL26INS0: add %%edx, %%edx\n\t"
"BBL26INS1: add 936(%%r8), %%edx\n\t"
"BBL26INS2: add 1192(%%r8), %%edx\n\t"
"BBL26INS3: test $64, %%eax\n\t"
"BBL26INS4: jz BBL27INS0\n\t"
"BBL27INS0: add 968(%%r8), %%edx\n\t"
"BBL27INS1: add 1008(%%r8), %%ecx\n\t"
"BBL27INS2: test $0, %%eax\n\t"
"BBL27INS3: jz BBL28INS0\n\t"
"BBL28INS0: add 992(%%r8), %%ebx\n\t"
"BBL28INS1: add 768(%%r9), %%ebx\n\t"
"BBL28INS2: add %%ebx, %%ebx\n\t"
"BBL28INS3: add 752(%%r9), %%edx\n\t"
"BBL28INS4: test $1, %%eax\n\t"
"BBL28INS5: jz BBL29INS0\n\t"
"BBL29INS0: add %%esp, %%ecx\n\t"
"BBL29INS1: add 712(%%r9), %%edx\n\t"
"BBL29INS2: add 728(%%r9), %%ecx\n\t"
"BBL29INS3: test $4, %%eax\n\t"
"BBL29INS4: jz BBL30INS0\n\t"
"BBL30INS0: add 760(%%r9), %%ebx\n\t"
"BBL30INS1: add 952(%%r9), %%ecx\n\t"
"BBL30INS2: add 1208(%%r9), %%ecx\n\t"
"BBL30INS3: test $2, %%eax\n\t"
"BBL30INS4: jz BBL31INS0\n\t"
"BBL31INS0: add %%esp, %%ecx\n\t"
"BBL31INS1: add %%ecx, %%ebx\n\t"
"BBL31INS2: add 984(%%r9), %%ecx\n\t"
"BBL31INS3: test $128, %%eax\n\t"
"BBL31INS4: jz BBL32INS0\n\t"
"BBL32INS0: add %%esp, %%ecx\n\t"
"BBL32INS1: add %%ecx, %%edx\n\t"
"BBL32INS2: add %%ecx, %%ecx\n\t"
"BBL32INS3: test $0, %%eax\n\t"
"BBL32INS4: jz BBL33INS0\n\t"
"BBL33INS0: add %%ecx, %%ebx\n\t"
"BBL33INS1: add 1240(%%r9), %%ecx\n\t"
"BBL33INS2: add %%ebx, %%ecx\n\t"
"BBL33INS3: test $2, %%eax\n\t"
"BBL33INS4: jz BBL34INS0\n\t"
"BBL34INS0: mov %%esp, 512(%%r11)\n\t"
"BBL34INS1: add 1248(%%r8), %%ecx\n\t"
"BBL34INS2: mov %%esp, 1504(%%r8)\n\t"
"BBL34INS3: test $0, %%eax\n\t"
"BBL34INS4: jz BBL35INS0\n\t"
"BBL35INS0: add %%esp, %%ebx\n\t"
"BBL35INS1: add 1728(%%r8), %%edx\n\t"
"BBL35INS2: test $64, %%eax\n\t"
"BBL35INS3: jz BBL36INS0\n\t"
"BBL36INS0: add %%esp, %%ebx\n\t"
"BBL36INS1: add %%ebx, %%ebx\n\t"
"BBL36INS2: add %%ebx, %%edx\n\t"
"BBL36INS3: test $1, %%eax\n\t"
"BBL36INS4: jz BBL37INS0\n\t"
"BBL37INS0: add 768(%%r11), %%ecx\n\t"
"BBL37INS1: add 1984(%%r8), %%ebx\n\t"
"BBL37INS2: add 1024(%%r11), %%ecx\n\t"
"BBL37INS3: test $4, %%eax\n\t"
"BBL37INS4: jz BBL38INS0\n\t"
"BBL38INS0: add %%ecx, %%edx\n\t"
"BBL38INS1: mov %%edx, 2240(%%r8)\n\t"
"BBL38INS2: add 2496(%%r8), %%ebx\n\t"
"BBL38INS3: test $1, %%eax\n\t"
"BBL38INS4: jz BBL39INS0\n\t"
"BBL39INS0: add %%ebx, %%ecx\n\t"
"BBL39INS1: add %%ecx, %%edx\n\t"
"BBL39INS2: test $2, %%eax\n\t"
"BBL39INS3: jz BBL40INS0\n\t"
"BBL40INS0: add 2752(%%r8), %%ebx\n\t"
"BBL40INS1: add 2712(%%r8), %%ecx\n\t"
"BBL40INS2: mov %%ecx, 2968(%%r8)\n\t"
"BBL40INS3: test $0, %%eax\n\t"
"BBL40INS4: jz BBL41INS0\n\t"
"BBL41INS0: add 2992(%%r8), %%ecx\n\t"
"BBL41INS1: add 3064(%%r8), %%ecx\n\t"
"BBL41INS2: add %%ecx, %%ecx\n\t"
"BBL41INS3: test $32, %%eax\n\t"
"BBL41INS4: jz BBL42INS0\n\t"
"BBL42INS0: add 1280(%%r11), %%ecx\n\t"
"BBL42INS1: add %%ecx, %%ecx\n\t"
"BBL42INS2: add 1496(%%r11), %%edx\n\t"
"BBL42INS3: add %%edx, %%ebx\n\t"
"BBL42INS4: test $128, %%eax\n\t"
"BBL42INS5: jz BBL43INS0\n\t"
"BBL43INS0: add 1752(%%r11), %%ecx\n\t"
"BBL43INS1: add 3320(%%r8), %%edx\n\t"
"BBL43INS2: add %%edx, %%ebx\n\t"
"BBL43INS3: test $16, %%eax\n\t"
"BBL43INS4: jz BBL44INS0\n\t"
"BBL44INS0: add %%esp, %%ecx\n\t"
"BBL44INS1: add 2008(%%r11), %%edx\n\t"
"BBL44INS2: test $32, %%eax\n\t"
"BBL44INS3: jz BBL45INS0\n\t"
"BBL45INS0: mov %%edx, 3576(%%r8)\n\t"
"BBL45INS1: add %%esp, %%ebx\n\t"
"BBL45INS2: add %%ecx, %%ebx\n\t"
"BBL45INS3: add %%ebx, %%edx\n\t"
"BBL45INS4: test $0, %%eax\n\t"
"BBL45INS5: jz BBL46INS0\n\t"
"BBL46INS0: add %%edx, %%edx\n\t"
"BBL46INS1: add %%edx, %%ecx\n\t"
"BBL46INS2: test $4, %%eax\n\t"
"BBL46INS3: jz BBL47INS0\n\t"
"BBL47INS0: add %%ecx, %%ebx\n\t"
"BBL47INS1: add %%ecx, %%ecx\n\t"
"BBL47INS2: add 3632(%%r8), %%ebx\n\t"
"BBL47INS3: test $1, %%eax\n\t"
"BBL47INS4: jz BBL48INS0\n\t"
"BBL48INS0: mov %%ebx, 3888(%%r8)\n\t"
"BBL48INS1: add %%ebx, %%ecx\n\t"
"BBL48INS2: mov %%edx, 4144(%%r8)\n\t"
"BBL48INS3: test $2, %%eax\n\t"
"BBL48INS4: jz BBL49INS0\n\t"
"BBL49INS0: add %%esp, %%ecx\n\t"
"BBL49INS1: add %%edx, %%ecx\n\t"
"BBL49INS2: add 4400(%%r8), %%ebx\n\t"
"BBL49INS3: mov %%ecx, 4656(%%r8)\n\t"
"BBL49INS4: test $1, %%eax\n\t"
"BBL49INS5: jz BBL50INS0\n\t"
"BBL50INS0: add 4912(%%r8), %%ebx\n\t"
"BBL50INS1: add 5168(%%r8), %%ebx\n\t"
"BBL50INS2: mov %%ebx, 512(%%r15)\n\t"
"BBL50INS3: test $256, %%eax\n\t"
"BBL50INS4: jz BBL51INS0\n\t"
"BBL51INS0: add 768(%%r15), %%ebx\n\t"
"BBL51INS1: add 1024(%%r15), %%ebx\n\t"
"BBL51INS2: test $64, %%eax\n\t"
::"m"(i), "m"(ptr0), "m"(ptr1), "m"(ptr2), "m"(ptr3), "m"(ptr4), "m"(ptr5), "m"(ptr6), "m"(ptr7):"memory", "cc", "esp", "edi", "ebx", "ecx", "edx", "st", "eax", "r8", "r9", "r10", "r11", "r12", "r13", "r14", "r15");
}
}