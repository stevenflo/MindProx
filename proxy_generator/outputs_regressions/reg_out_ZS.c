/*************
File created on 2019-04-19 14:05:28.777592
input file: /export/zachary/data/spec_avg_proxies/mcf_r/mcf_r_initial/mcf_r_new.json
input statistics
****************/
#include<stdio.h>
#define MAX 255*1024 + 252*1024
#define ITERATIONS 3079621
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
"mov %1, %%r8\n\t"
"mov %2, %%r9\n\t"
"mov %3, %%r10\n\t"
"mov %4, %%r11\n\t"
"mov %5, %%r12\n\t"
"mov %6, %%r13\n\t"
"mov %7, %%r14\n\t"
"mov %8, %%r15\n\t"
"BBL0INS0: add %%esp, %%ebx\n\t"
"BBL0INS1: mov 0(%%r8), %%edi\n\t"
"BBL0INS2: add %%ebx, %%ebx\n\t"
"BBL0INS3: test $4, %%eax\n\t"
"BBL0INS4: jz BBL1INS0\n\t"
"BBL1INS0: mov 0(%%rbp), %%ebx\n\t"
"BBL1INS1: mov 0(%%rbp), %%edi\n\t"
"BBL1INS2: mov %%ebx, -224(%%r8)\n\t"
"BBL1INS3: mov 0(%%rbp), %%ebx\n\t"
"BBL1INS4: test $32, %%eax\n\t"
"BBL1INS5: jz BBL2INS0\n\t"
"BBL2INS0: mov %%ebx, -448(%%r8)\n\t"
"BBL2INS1: mov 0(%%rbp), %%edi\n\t"
"BBL2INS2: mov -232(%%r8), %%edi\n\t"
"BBL2INS3: test $64, %%eax\n\t"
"BBL2INS4: jz BBL3INS0\n\t"
"BBL3INS0: mov 0(%%rbp), %%edi\n\t"
"BBL3INS1: mov -248(%%r8), %%edi\n\t"
"BBL3INS2: mov 0(%%rbp), %%ebx\n\t"
"BBL3INS3: mov %%ebx, -264(%%r8)\n\t"
"BBL3INS4: test $256, %%eax\n\t"
"BBL3INS5: jz BBL4INS0\n\t"
"BBL4INS0: add 0(%%rbp), %%ebx\n\t"
"BBL4INS1: mov -376(%%r8), %%edi\n\t"
"BBL4INS2: test $64, %%eax\n\t"
"BBL4INS3: jz BBL5INS0\n\t"
"BBL5INS0: mov 0(%%rbp), %%edx\n\t"
"BBL5INS1: mov -160(%%r8), %%ecx\n\t"
"BBL5INS2: mov 0(%%rbp), %%edi\n\t"
"BBL5INS3: test $-1, %%eax\n\t"
"BBL5INS4: jz BBL6INS0\n\t"
"BBL6INS0: mov -176(%%r8), %%edi\n\t"
"BBL6INS1: mov 0(%%rbp), %%ebx\n\t"
"BBL6INS2: mov 40(%%r8), %%edi\n\t"
"BBL6INS3: test $32, %%eax\n\t"
"BBL6INS4: jz BBL7INS0\n\t"
"BBL7INS0: mov %%ecx, 24(%%r8)\n\t"
"BBL7INS1: mov 0(%%rbp), %%ecx\n\t"
"BBL7INS2: test $16, %%eax\n\t"
"BBL7INS3: jz BBL8INS0\n\t"
"BBL8INS0: add %%ecx, %%ecx\n\t"
"BBL8INS1: mov 56(%%r8), %%ecx\n\t"
"BBL8INS2: mov 0(%%rbp), %%edi\n\t"
"BBL8INS3: test $256, %%eax\n\t"
"BBL8INS4: jz BBL9INS0\n\t"
"BBL9INS0: mov 280(%%r8), %%edi\n\t"
"BBL9INS1: add %%ecx, %%ebx\n\t"
"BBL9INS2: mov %%ecx, 224(%%r8)\n\t"
"BBL9INS3: mov 0(%%rbp), %%ebx\n\t"
"BBL9INS4: test $2, %%eax\n\t"
"BBL9INS5: jz BBL10INS0\n\t"
"BBL10INS0: mov %%ebx, 184(%%r8)\n\t"
"BBL10INS1: mov %%edx, 256(%%r8)\n\t"
"BBL10INS2: mov 0(%%rbp), %%edi\n\t"
"BBL10INS3: test $256, %%eax\n\t"
"BBL10INS4: jz BBL11INS0\n\t"
"BBL11INS0: mov %%ebx, 216(%%r8)\n\t"
"BBL11INS1: mov 0(%%rbp), %%ebx\n\t"
"BBL11INS2: mov %%ebx, 432(%%r8)\n\t"
"BBL11INS3: test $32, %%eax\n\t"
"BBL11INS4: jz BBL12INS0\n\t"
"BBL12INS0: mov 0(%%rbp), %%edi\n\t"
"BBL12INS1: mov 656(%%r8), %%edi\n\t"
"BBL12INS2: mov 0(%%rbp), %%ebx\n\t"
"BBL12INS3: test $4, %%eax\n\t"
"BBL12INS4: jz BBL13INS0\n\t"
"BBL13INS0: add %%ecx, %%ebx\n\t"
"BBL13INS1: mov 616(%%r8), %%ebx\n\t"
"BBL13INS2: test $128, %%eax\n\t"
"BBL13INS3: jz BBL14INS0\n\t"
"BBL14INS0: add %%ebx, %%ebx\n\t"
"BBL14INS1: mov 0(%%rbp), %%edi\n\t"
"BBL14INS2: mov 672(%%r8), %%ebx\n\t"
"BBL14INS3: test $16, %%eax\n\t"
"BBL14INS4: jz BBL15INS0\n\t"
"BBL15INS0: mov 0(%%rbp), %%ecx\n\t"
"BBL15INS1: add %%ecx, %%ecx\n\t"
"BBL15INS2: test $256, %%eax\n\t"
"BBL15INS3: jz BBL16INS0\n\t"
"BBL16INS0: mov 704(%%r8), %%edx\n\t"
"BBL16INS1: add %%ecx, %%ebx\n\t"
"BBL16INS2: mov 0(%%rbp), %%ebx\n\t"
"BBL16INS3: test $32, %%eax\n\t"
"BBL16INS4: jz BBL17INS0\n\t"
"BBL17INS0: mov 688(%%r8), %%edi\n\t"
"BBL17INS1: mov 0(%%rbp), %%ecx\n\t"
"BBL17INS2: mov %%ebx, 632(%%r8)\n\t"
"BBL17INS3: test $4, %%eax\n\t"
"BBL17INS4: jz BBL18INS0\n\t"
"BBL18INS0: mov 0(%%rbp), %%edi\n\t"
"BBL18INS1: mov 624(%%r8), %%ebx\n\t"
"BBL18INS2: test $-1, %%eax\n\t"
"BBL18INS3: jz BBL19INS0\n\t"
"BBL19INS0: mov 0(%%rbp), %%edi\n\t"
"BBL19INS1: mov 640(%%r8), %%edi\n\t"
"BBL19INS2: mov 0(%%rbp), %%edi\n\t"
"BBL19INS3: mov 416(%%r8), %%edi\n\t"
"BBL19INS4: test $32, %%eax\n\t"
"BBL19INS5: jz BBL20INS0\n\t"
"BBL20INS0: mov %%edx, 192(%%r8)\n\t"
"BBL20INS1: mov 0(%%rbp), %%edi\n\t"
"BBL20INS2: mov 80(%%r8), %%edi\n\t"
"BBL20INS3: mov 0(%%rbp), %%edx\n\t"
"BBL20INS4: test $8, %%eax\n\t"
"BBL20INS5: jz BBL21INS0\n\t"
"BBL21INS0: add %%edx, %%ebx\n\t"
"BBL21INS1: mov 336(%%r8), %%edi\n\t"
"BBL21INS2: mov %%ecx, 256(%%r13)\n\t"
"BBL21INS3: mov 280(%%r13), %%edx\n\t"
"BBL21INS4: test $64, %%eax\n\t"
"BBL21INS5: jz BBL22INS0\n\t"
"BBL22INS0: mov 312(%%r13), %%edi\n\t"
"BBL22INS1: mov 256(%%r15), %%ecx\n\t"
"BBL22INS2: mov 256(%%r14), %%ebx\n\t"
"BBL22INS3: test $8, %%eax\n\t"
"BBL22INS4: jz BBL23INS0\n\t"
"BBL23INS0: mov 288(%%r14), %%edi\n\t"
"BBL23INS1: mov 592(%%r8), %%edi\n\t"
"BBL23INS2: mov %%ecx, 544(%%r14)\n\t"
"BBL23INS3: test $-1, %%eax\n\t"
"BBL23INS4: jz BBL24INS0\n\t"
"BBL24INS0: mov 256(%%r12), %%ecx\n\t"
"BBL24INS1: add %%ecx, %%ebx\n\t"
"BBL24INS2: mov 256(%%r11), %%ecx\n\t"
"BBL24INS3: test $4, %%eax\n\t"
"BBL24INS4: jz BBL25INS0\n\t"
"BBL25INS0: mov 848(%%r8), %%edi\n\t"
"BBL25INS1: mov 624(%%r8), %%edi\n\t"
"BBL25INS2: add 640(%%r8), %%ecx\n\t"
"BBL25INS3: test $16, %%eax\n\t"
"BBL25INS4: jz BBL26INS0\n\t"
"BBL26INS0: mov 656(%%r8), %%ebx\n\t"
"BBL26INS1: add %%edx, %%ebx\n\t"
"BBL26INS2: mov 712(%%r8), %%edx\n\t"
"BBL26INS3: test $128, %%eax\n\t"
"BBL26INS4: jz BBL27INS0\n\t"
"BBL27INS0: mov %%edx, 672(%%r8)\n\t"
"BBL27INS1: mov 720(%%r8), %%ebx\n\t"
"BBL27INS2: mov %%ebx, 256(%%r10)\n\t"
"BBL27INS3: add %%edx, %%ecx\n\t"
"BBL27INS4: test $256, %%eax\n\t"
"BBL27INS5: jz BBL28INS0\n\t"
"BBL28INS0: mov 240(%%r10), %%edi\n\t"
"BBL28INS1: mov 256(%%r10), %%edi\n\t"
"BBL28INS2: mov 512(%%r12), %%ecx\n\t"
"BBL28INS3: test $16, %%eax\n\t"
"BBL28INS4: jz BBL29INS0\n\t"
"BBL29INS0: mov 288(%%r12), %%edx\n\t"
"BBL29INS1: add %%ebx, %%ebx\n\t"
"BBL29INS2: add %%edx, %%ebx\n\t"
"BBL29INS3: test $0, %%eax\n\t"
"BBL29INS4: jz BBL30INS0\n\t"
"BBL30INS0: mov %%ecx, 512(%%r11)\n\t"
"BBL30INS1: mov %%ebx, 768(%%r11)\n\t"
"BBL30INS2: mov 512(%%r10), %%ebx\n\t"
"BBL30INS3: test $128, %%eax\n\t"
"BBL30INS4: jz BBL31INS0\n\t"
"BBL31INS0: mov 496(%%r10), %%edi\n\t"
"BBL31INS1: mov %%ebx, 688(%%r10)\n\t"
"BBL31INS2: mov 680(%%r10), %%ebx\n\t"
"BBL31INS3: test $64, %%eax\n\t"
"BBL31INS4: jz BBL32INS0\n\t"
"BBL32INS0: mov 904(%%r10), %%ecx\n\t"
"BBL32INS1: mov 1160(%%r10), %%edi\n\t"
"BBL32INS2: mov %%ecx, 1376(%%r10)\n\t"
"BBL32INS3: test $8, %%eax\n\t"
"BBL32INS4: jz BBL33INS0\n\t"
"BBL33INS0: mov 1416(%%r10), %%edx\n\t"
"BBL33INS1: mov %%ecx, 1672(%%r10)\n\t"
"BBL33INS2: mov 1928(%%r10), %%ecx\n\t"
"BBL33INS3: test $-1, %%eax\n\t"
"BBL33INS4: jz BBL34INS0\n\t"
"BBL34INS0: add %%ecx, %%ebx\n\t"
"BBL34INS1: mov 2144(%%r10), %%ebx\n\t"
"BBL34INS2: add %%ebx, %%ecx\n\t"
"BBL34INS3: test $1, %%eax\n\t"
"BBL34INS4: jz BBL35INS0\n\t"
"BBL35INS0: mov 976(%%r8), %%ecx\n\t"
"BBL35INS1: add %%edx, %%ecx\n\t"
"BBL35INS2: test $8, %%eax\n\t"
"BBL35INS3: jz BBL36INS0\n\t"
"BBL36INS0: mov 864(%%r8), %%ecx\n\t"
"BBL36INS1: mov %%ecx, 808(%%r8)\n\t"
"BBL36INS2: mov %%ebx, 864(%%r8)\n\t"
"BBL36INS3: test $16, %%eax\n\t"
"BBL36INS4: jz BBL37INS0\n\t"
"BBL37INS0: add %%ecx, %%ecx\n\t"
"BBL37INS1: mov 1056(%%r8), %%edx\n\t"
"BBL37INS2: add %%ecx, %%ebx\n\t"
"BBL37INS3: test $32, %%eax\n\t"
"BBL37INS4: jz BBL38INS0\n\t"
"BBL38INS0: mov %%ebx, 832(%%r8)\n\t"
"BBL38INS1: mov 816(%%r8), %%ebx\n\t"
"BBL38INS2: add %%ebx, %%ebx\n\t"
"BBL38INS3: test $2, %%eax\n\t"
"BBL38INS4: jz BBL39INS0\n\t"
"BBL39INS0: mov 1072(%%r8), %%ebx\n\t"
"BBL39INS1: mov %%ebx, 1328(%%r8)\n\t"
"BBL39INS2: mov %%ebx, 2400(%%r10)\n\t"
"BBL39INS3: test $64, %%eax\n\t"
"BBL39INS4: jz BBL40INS0\n\t"
"BBL40INS0: mov 1024(%%r11), %%ecx\n\t"
"BBL40INS1: mov %%edx, 1016(%%r11)\n\t"
"BBL40INS2: add %%ecx, %%ebx\n\t"
"BBL40INS3: mov 1584(%%r8), %%edi\n\t"
"BBL40INS4: test $4, %%eax\n\t"
"BBL40INS5: jz BBL41INS0\n\t"
"BBL41INS0: mov 1576(%%r8), %%edi\n\t"
"BBL41INS1: mov 1832(%%r8), %%ecx\n\t"
"BBL41INS2: mov %%ecx, 1792(%%r8)\n\t"
"BBL41INS3: test $4, %%eax\n\t"
"BBL41INS4: jz BBL42INS0\n\t"
"BBL42INS0: mov 2016(%%r8), %%ebx\n\t"
"BBL42INS1: mov %%ebx, 2272(%%r8)\n\t"
"BBL42INS2: add %%ebx, %%ebx\n\t"
"BBL42INS3: test $16, %%eax\n\t"
"BBL42INS4: jz BBL43INS0\n\t"
"BBL43INS0: mov 2256(%%r8), %%ebx\n\t"
"BBL43INS1: add %%ebx, %%ecx\n\t"
"BBL43INS2: test $4, %%eax\n\t"
"BBL43INS3: jz BBL44INS0\n\t"
"BBL44INS0: mov 2032(%%r8), %%edi\n\t"
"BBL44INS1: mov 2288(%%r8), %%edi\n\t"
"BBL44INS2: mov 2544(%%r8), %%edi\n\t"
"BBL44INS3: test $128, %%eax\n\t"
"BBL44INS4: jz BBL45INS0\n\t"
"BBL45INS0: mov %%ecx, 1272(%%r11)\n\t"
"BBL45INS1: mov 2800(%%r8), %%ecx\n\t"
"BBL45INS2: test $64, %%eax\n\t"
"BBL45INS3: jz BBL46INS0\n\t"
"BBL46INS0: mov 3056(%%r8), %%edi\n\t"
"BBL46INS1: mov 1528(%%r11), %%edx\n\t"
"BBL46INS2: test $32, %%eax\n\t"
"BBL46INS3: jz BBL47INS0\n\t"
"BBL47INS0: add %%edx, %%ecx\n\t"
"BBL47INS1: mov %%ecx, 3312(%%r8)\n\t"
"BBL47INS2: test $256, %%eax\n\t"
"BBL47INS3: jz BBL48INS0\n\t"
"BBL48INS0: mov 1784(%%r11), %%edi\n\t"
"BBL48INS1: add %%ecx, %%ecx\n\t"
"BBL48INS2: mov 2040(%%r11), %%edi\n\t"
"BBL48INS3: add %%ecx, %%ebx\n\t"
"BBL48INS4: test $16, %%eax\n\t"
"BBL48INS5: jz BBL49INS0\n\t"
"BBL49INS0: mov 2296(%%r11), %%edi\n\t"
"BBL49INS1: mov %%ebx, 2552(%%r11)\n\t"
"BBL49INS2: test $32, %%eax\n\t"
"BBL49INS3: jz BBL50INS0\n\t"
"BBL50INS0: mov 512(%%r15), %%edi\n\t"
"BBL50INS1: mov 768(%%r15), %%edi\n\t"
"BBL50INS2: mov 1024(%%r15), %%ebx\n\t"
"BBL50INS3: test $64, %%eax\n\t"
"BBL50INS4: jz BBL51INS0\n\t"
"BBL51INS0: mov %%ebx, 1280(%%r15)\n\t"
"BBL51INS1: mov %%ebx, 1536(%%r15)\n\t"
"BBL51INS2: test $1, %%eax\n\t"
::"m"(i), "m"(ptr0), "m"(ptr1), "m"(ptr2), "m"(ptr3), "m"(ptr4), "m"(ptr5), "m"(ptr6), "m"(ptr7):"memory", "cc", "esp", "edi", "ebx", "ecx", "edx", "st", "eax", "r8", "r9", "r10", "r11", "r12", "r13", "r14", "r15");
}}
}