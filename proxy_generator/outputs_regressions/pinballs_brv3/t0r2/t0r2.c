char X0[2666912];
char X1[2666624];
char X2[2666624];
char X3[2666624];
char X4[2666624];
char X5[2666624];
char X6[2666624];
char X7[2666624];
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
for (j = 0; j < 1; j++) {
for (i = 1; i < 41666; i++) {
ptr0 = (char*) &X0[64 * i + 172];
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
"BBL0INS0: add 0(%%r8), %%ebx\n\t"
"BBL0INS1: add %%ebx, %%ebx\n\t"
"BBL0INS2: add 0(%%rbp), %%ebx\n\t"
"BBL0INS3: add 0(%%rbp), %%ebx\n\t"
"BBL0INS4: add %%ebx, %%ebx\n\t"
"BBL0INS5: mov %%ebx, 64(%%r8)\n\t"
"BBL0INS6: mov %%ebx, 56(%%r8)\n\t"
"BBL0INS7: test $0x00000040, %%eax\n\t"
"BBL0INS8: jz BBL1INS0\n\t"
"BBL1INS0: add 0(%%rbp), %%ecx\n\t"
"BBL1INS1: add 0(%%rbp), %%ebx\n\t"
"BBL1INS2: add %%ebx, %%ebx\n\t"
"BBL1INS3: add 0(%%rbp), %%ecx\n\t"
"BBL1INS4: add %%ebx, %%ebx\n\t"
"BBL1INS5: add %%ecx, %%ecx\n\t"
"BBL1INS6: add 0(%%rbp), %%ebx\n\t"
"BBL1INS7: mov %%ebx, 132(%%r8)\n\t"
"BBL1INS8: test $0x00000004, %%eax\n\t"
"BBL1INS9: jz BBL2INS0\n\t"
"BBL2INS0: add 0(%%rbp), %%ebx\n\t"
"BBL2INS1: add %%ebx, %%ebx\n\t"
"BBL2INS2: add 0(%%rbp), %%ebx\n\t"
"BBL2INS3: add 124(%%r8), %%ecx\n\t"
"BBL2INS4: add 0(%%rbp), %%ecx\n\t"
"BBL2INS5: add 164(%%r8), %%ecx\n\t"
"BBL2INS6: add 0(%%rbp), %%ebx\n\t"
"BBL2INS7: test $-0x0000001, %%eax\n\t"
"BBL2INS8: jz BBL3INS0\n\t"
"BBL3INS0: add 160(%%r8), %%ebx\n\t"
"BBL3INS1: add 0(%%rbp), %%ebx\n\t"
"BBL3INS2: add %%esp, %%ebx\n\t"
"BBL3INS3: add 156(%%r8), %%ebx\n\t"
"BBL3INS4: add 0(%%rbp), %%ebx\n\t"
"BBL3INS5: add 188(%%r8), %%ebx\n\t"
"BBL3INS6: add 0(%%rbp), %%ebx\n\t"
"BBL3INS7: add %%ebx, %%ebx\n\t"
"BBL3INS8: test $0x00000040, %%eax\n\t"
"BBL3INS9: jz BBL4INS0\n\t"
"BBL4INS0: add %%ebx, %%ebx\n\t"
"BBL4INS1: add %%ebx, %%ebx\n\t"
"BBL4INS2: add 156(%%r8), %%ebx\n\t"
"BBL4INS3: add %%ebx, %%ebx\n\t"
"BBL4INS4: add %%ebx, %%ebx\n\t"
"BBL4INS5: test $0x00000002, %%eax\n\t"
"BBL4INS6: jz BBL5INS0\n\t"
"BBL5INS0: mov %%ebx, 148(%%r8)\n\t"
"BBL5INS1: add 0(%%rbp), %%ebx\n\t"
"BBL5INS2: add %%ebx, %%ebx\n\t"
"BBL5INS3: add %%ebx, %%ebx\n\t"
"BBL5INS4: add %%ebx, %%ebx\n\t"
"BBL5INS5: add 144(%%r8), %%ebx\n\t"
"BBL5INS6: mov %%ebx, 140(%%r8)\n\t"
"BBL5INS7: test $0x00000008, %%eax\n\t"
"BBL5INS8: jz BBL6INS0\n\t"
"BBL6INS0: mov %%esp, 96(%%r8)\n\t"
"BBL6INS1: add 0(%%rbp), %%ebx\n\t"
"BBL6INS2: add %%ebx, %%ebx\n\t"
"BBL6INS3: add 80(%%r8), %%ebx\n\t"
"BBL6INS4: mov %%ebx, 48(%%r8)\n\t"
"BBL6INS5: mov %%ebx, 44(%%r8)\n\t"
"BBL6INS6: mov %%ebx, 28(%%r8)\n\t"
"BBL6INS7: test $0x00000040, %%eax\n\t"
"BBL6INS8: jz BBL7INS0\n\t"
"BBL7INS0: add %%esp, %%ecx\n\t"
"BBL7INS1: mov %%ecx, -4(%%r8)\n\t"
"BBL7INS2: add %%ecx, %%ebx\n\t"
"BBL7INS3: add %%ebx, %%ebx\n\t"
"BBL7INS4: add %%ebx, %%ebx\n\t"
"BBL7INS5: add %%ebx, %%ecx\n\t"
"BBL7INS6: test $0x00000020, %%eax\n\t"
"BBL7INS7: jz BBL8INS0\n\t"
"BBL8INS0: add 0(%%rbp), %%ebx\n\t"
"BBL8INS1: add -16(%%r8), %%ebx\n\t"
"BBL8INS2: add 0(%%rbp), %%ecx\n\t"
"BBL8INS3: add 16(%%r8), %%ebx\n\t"
"BBL8INS4: add 0(%%rbp), %%ebx\n\t"
"BBL8INS5: add 8(%%r8), %%ebx\n\t"
"BBL8INS6: add 0(%%rbp), %%ebx\n\t"
"BBL8INS7: test $0x00000040, %%eax\n\t"
"BBL8INS8: jz BBL9INS0\n\t"
"BBL9INS0: add %%esp, %%ebx\n\t"
"BBL9INS1: add 4(%%r8), %%ebx\n\t"
"BBL9INS2: add 0(%%rbp), %%ebx\n\t"
"BBL9INS3: add 44(%%r8), %%ebx\n\t"
"BBL9INS4: add 76(%%r8), %%ebx\n\t"
"BBL9INS5: mov %%ebx, 72(%%r8)\n\t"
"BBL9INS6: add 64(%%r8), %%ebx\n\t"
"BBL9INS7: mov %%ebx, 68(%%r8)\n\t"
"BBL9INS8: add 48(%%r8), %%ebx\n\t"
"BBL9INS9: test $0x00000002, %%eax\n\t"
"BBL9INS10: jz BBL10INS0\n\t"
"BBL10INS0: add 88(%%r8), %%ebx\n\t"
"BBL10INS1: add 84(%%r8), %%ebx\n\t"
"BBL10INS2: add -4(%%r8), %%ecx\n\t"
"BBL10INS3: mov %%ecx, -48(%%r8)\n\t"
"BBL10INS4: add -52(%%r8), %%ebx\n\t"
"BBL10INS5: add %%ebx, %%ecx\n\t"
"BBL10INS6: test $0x00000010, %%eax\n\t"
"BBL10INS7: jz BBL11INS0\n\t"
"BBL11INS0: add -24(%%r8), %%ebx\n\t"
"BBL11INS1: add %%esp, %%ebx\n\t"
"BBL11INS2: mov %%ebx, -68(%%r8)\n\t"
"BBL11INS3: add -72(%%r8), %%ebx\n\t"
"BBL11INS4: add -88(%%r8), %%ebx\n\t"
"BBL11INS5: add -48(%%r8), %%ebx\n\t"
"BBL11INS6: add -8(%%r8), %%ebx\n\t"
"BBL11INS7: test $0x00000008, %%eax\n\t"
"BBL11INS8: jz BBL12INS0\n\t"
"BBL12INS0: add -12(%%r8), %%ebx\n\t"
"BBL12INS1: mov %%ebx, 0(%%r8)\n\t"
"BBL12INS2: add -16(%%r8), %%ebx\n\t"
"BBL12INS3: mov %%ebx, -12(%%r8)\n\t"
"BBL12INS4: add -16(%%r8), %%ebx\n\t"
"BBL12INS5: mov %%ebx, -28(%%r8)\n\t"
"BBL12INS6: test $0x00000000, %%eax\n\t"
"BBL12INS7: jz BBL13INS0\n\t"
"BBL13INS0: add %%esp, %%ecx\n\t"
"BBL13INS1: add -32(%%r8), %%edx\n\t"
"BBL13INS2: add %%edx, %%edx\n\t"
"BBL13INS3: mov %%ecx, -64(%%r8)\n\t"
"BBL13INS4: mov %%edx, 16(%%r8)\n\t"
"BBL13INS5: test $0x00000004, %%eax\n\t"
"BBL13INS6: jz BBL14INS0\n\t"
"BBL14INS0: add %%esp, %%edx\n\t"
"BBL14INS1: add 4(%%r8), %%edx\n\t"
"BBL14INS2: add %%edx, %%ebx\n\t"
"BBL14INS3: add %%ebx, %%ebx\n\t"
"BBL14INS4: add 0(%%r8), %%edx\n\t"
"BBL14INS5: mov %%ebx, -88(%%r8)\n\t"
"BBL14INS6: add -84(%%r8), %%edx\n\t"
"BBL14INS7: test $0x00000100, %%eax\n\t"
"BBL14INS8: jz BBL15INS0\n\t"
"BBL15INS0: add %%edx, %%ebx\n\t"
"BBL15INS1: add %%ebx, %%edx\n\t"
"BBL15INS2: add %%edx, %%edx\n\t"
"BBL15INS3: mov %%edx, -128(%%r8)\n\t"
"BBL15INS4: add %%edx, %%edx\n\t"
"BBL15INS5: test $0x00000010, %%eax\n\t"
"BBL15INS6: jz BBL16INS0\n\t"
"BBL16INS0: add %%esp, %%edx\n\t"
"BBL16INS1: add -136(%%r8), %%edx\n\t"
"BBL16INS2: add -144(%%r8), %%ebx\n\t"
"BBL16INS3: add -156(%%r8), %%edx\n\t"
"BBL16INS4: add %%edx, %%edx\n\t"
"BBL16INS5: add %%edx, %%edx\n\t"
"BBL16INS6: mov %%edx, -172(%%r8)\n\t"
"BBL16INS7: test $0x00000004, %%eax\n\t"
"BBL16INS8: jz BBL17INS0\n\t"
"BBL17INS0: mov %%esp, -84(%%r8)\n\t"
"BBL17INS1: add -88(%%r8), %%ecx\n\t"
"BBL17INS2: add %%ecx, %%ebx\n\t"
"BBL17INS3: mov %%ecx, -124(%%r8)\n\t"
"BBL17INS4: add %%ebx, %%edx\n\t"
"BBL17INS5: add %%edx, %%edx\n\t"
"BBL17INS6: add -120(%%r8), %%ebx\n\t"
"BBL17INS7: add -12(%%r8), %%edx\n\t"
"BBL17INS8: test $0x00000040, %%eax\n\t"
"BBL17INS9: jz BBL18INS0\n\t"
"BBL18INS0: add %%edx, %%ebx\n\t"
"BBL18INS1: add 24(%%r8), %%edx\n\t"
"BBL18INS2: add 52(%%r8), %%ecx\n\t"
"BBL18INS3: add %%ecx, %%ecx\n\t"
"BBL18INS4: mov %%ecx, 44(%%r8)\n\t"
"BBL18INS5: add 56(%%r8), %%ecx\n\t"
"BBL18INS6: test $0x00000008, %%eax\n\t"
"BBL18INS7: jz BBL19INS0\n\t"
"BBL19INS0: mov %%ecx, 68(%%r8)\n\t"
"BBL19INS1: add 108(%%r8), %%ebx\n\t"
"BBL19INS2: add %%ebx, %%ecx\n\t"
"BBL19INS3: mov %%ebx, 60(%%r8)\n\t"
"BBL19INS4: add %%ecx, %%ebx\n\t"
"BBL19INS5: add %%ecx, %%ecx\n\t"
"BBL19INS6: add 56(%%r8), %%edx\n\t"
"BBL19INS7: add 96(%%r8), %%ecx\n\t"
"BBL19INS8: test $0x00000080, %%eax\n\t"
"BBL19INS9: jz BBL20INS0\n\t"
"BBL20INS0: add 88(%%r8), %%ecx\n\t"
"BBL20INS1: add 84(%%r8), %%ecx\n\t"
"BBL20INS2: add 64(%%r8), %%ecx\n\t"
"BBL20INS3: add %%ecx, %%ebx\n\t"
"BBL20INS4: add 40(%%r8), %%ecx\n\t"
"BBL20INS5: add -36(%%r8), %%edx\n\t"
"BBL20INS6: add %%edx, %%ebx\n\t"
"BBL20INS7: add 4(%%r8), %%ecx\n\t"
"BBL20INS8: mov %%ecx, -4(%%r8)\n\t"
"BBL20INS9: test $0x00000100, %%eax\n\t"
"BBL20INS10: jz BBL21INS0\n\t"
"BBL21INS0: add %%esp, %%edx\n\t"
"BBL21INS1: add %%edx, %%edx\n\t"
"BBL21INS2: add -12(%%r8), %%ecx\n\t"
"BBL21INS3: add %%ecx, %%ebx\n\t"
"BBL21INS4: add %%ebx, %%ecx\n\t"
"BBL21INS5: add %%ecx, %%edx\n\t"
"BBL21INS6: add 28(%%r8), %%ecx\n\t"
"BBL21INS7: mov %%ecx, 52(%%r8)\n\t"
"BBL21INS8: test $0x00000020, %%eax\n\t"
"BBL21INS9: jz BBL22INS0\n\t"
"BBL22INS0: add 48(%%r8), %%edx\n\t"
"BBL22INS1: add 52(%%r8), %%edx\n\t"
"BBL22INS2: add 116(%%r8), %%ecx\n\t"
"BBL22INS3: add 216(%%r8), %%edx\n\t"
"BBL22INS4: add %%ecx, %%ecx\n\t"
"BBL22INS5: add 212(%%r8), %%ebx\n\t"
"BBL22INS6: add 288(%%r8), %%edx\n\t"
"BBL22INS7: test $0x00000004, %%eax\n\t"
"BBL22INS8: jz BBL23INS0\n\t"
"BBL23INS0: mov %%edx, 264(%%r8)\n\t"
"BBL23INS1: add %%esp, %%ecx\n\t"
"BBL23INS2: add 220(%%r8), %%ebx\n\t"
"BBL23INS3: add %%ecx, %%edx\n\t"
"BBL23INS4: add 216(%%r8), %%ecx\n\t"
"BBL23INS5: add 220(%%r8), %%ebx\n\t"
"BBL23INS6: add 204(%%r8), %%edx\n\t"
"BBL23INS7: test $0x00000040, %%eax\n\t"
"BBL23INS8: jz BBL24INS0\n\t"
"BBL24INS0: add %%edx, %%ecx\n\t"
"BBL24INS1: add 200(%%r8), %%edx\n\t"
"BBL24INS2: add %%ecx, %%edx\n\t"
"BBL24INS3: add 192(%%r8), %%ecx\n\t"
"BBL24INS4: add %%ecx, %%edx\n\t"
"BBL24INS5: add %%ecx, %%ecx\n\t"
"BBL24INS6: add 188(%%r8), %%edx\n\t"
"BBL24INS7: test $0x00000010, %%eax\n\t"
"BBL24INS8: jz BBL25INS0\n\t"
"BBL25INS0: add %%edx, %%ecx\n\t"
"BBL25INS1: add %%ecx, %%edx\n\t"
"BBL25INS2: add 180(%%r8), %%edx\n\t"
"BBL25INS3: add 152(%%r8), %%ebx\n\t"
"BBL25INS4: mov %%edx, 148(%%r8)\n\t"
"BBL25INS5: add 44(%%r8), %%edx\n\t"
"BBL25INS6: add %%ebx, %%edx\n\t"
"BBL25INS7: test $0x00000080, %%eax\n\t"
"BBL25INS8: jz BBL26INS0\n\t"
"BBL26INS0: add 240(%%r8), %%ebx\n\t"
"BBL26INS1: add 228(%%r8), %%edx\n\t"
"BBL26INS2: add 196(%%r8), %%edx\n\t"
"BBL26INS3: add 184(%%r8), %%ecx\n\t"
"BBL26INS4: add %%ecx, %%ecx\n\t"
"BBL26INS5: add 136(%%r8), %%ebx\n\t"
"BBL26INS6: test $0x00000004, %%eax\n\t"
::"m"(i), "m"(ptr0), "m"(ptr1), "m"(ptr2), "m"(ptr3), "m"(ptr4), "m"(ptr5), "m"(ptr6), "m"(ptr7):"memory", "cc", "esp", "edi", "ebx", "ecx", "edx", "st", "eax", "esi", "r8", "r9", "r10", "r11", "r12", "r13", "r14", "r15");
}}
}