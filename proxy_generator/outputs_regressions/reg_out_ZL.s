	.file	"reg_out_ZL.c"
	.comm	X0,197099520,32
	.comm	X1,197099520,32
	.comm	X2,197099520,32
	.comm	X3,197099520,32
	.comm	X4,197099520,32
	.comm	X5,197099520,32
	.comm	X6,197099520,32
	.comm	X7,197099520,32
	.text
	.globl	main
	.type	main, @function
main:
.LFB0:
	.cfi_startproc
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset 6, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register 6
	pushq	%r15
	pushq	%r14
	pushq	%r13
	pushq	%r12
	pushq	%rbx
	.cfi_offset 15, -24
	.cfi_offset 14, -32
	.cfi_offset 13, -40
	.cfi_offset 12, -48
	.cfi_offset 3, -56
	movl	$0, -108(%rbp)
	jmp	.L2
.L5:
	movl	$1, -112(%rbp)
	jmp	.L3
.L4:
	movl	-112(%rbp), %eax
	addl	$7, %eax
	sall	$6, %eax
	cltq
	addq	$X0, %rax
	movq	%rax, -104(%rbp)
	movl	-112(%rbp), %eax
	sall	$6, %eax
	cltq
	addq	$X1, %rax
	movq	%rax, -96(%rbp)
	movl	-112(%rbp), %eax
	sall	$6, %eax
	cltq
	addq	$X2, %rax
	movq	%rax, -88(%rbp)
	movl	-112(%rbp), %eax
	sall	$6, %eax
	cltq
	addq	$X3, %rax
	movq	%rax, -80(%rbp)
	movl	-112(%rbp), %eax
	sall	$6, %eax
	cltq
	addq	$X4, %rax
	movq	%rax, -72(%rbp)
	movl	-112(%rbp), %eax
	sall	$6, %eax
	cltq
	addq	$X5, %rax
	movq	%rax, -64(%rbp)
	movl	-112(%rbp), %eax
	sall	$6, %eax
	cltq
	addq	$X6, %rax
	movq	%rax, -56(%rbp)
	movl	-112(%rbp), %eax
	sall	$6, %eax
	cltq
	addq	$X7, %rax
	movq	%rax, -48(%rbp)
#APP
# 38 "reg_out_ZL.c" 1
	mov -112(%rbp), %eax
	mov -104(%rbp), %r8
	mov -96(%rbp), %r9
	mov -88(%rbp), %r10
	mov -80(%rbp), %r11
	mov -72(%rbp), %r12
	mov -64(%rbp), %r13
	mov -56(%rbp), %r14
	mov -48(%rbp), %r15
	BBL0INS1: mov %ebx, (%r8,%r15,4)
	BBL51INS2: test $1, %eax
	
# 0 "" 2
#NO_APP
	movl	-112(%rbp), %eax
	addl	$1, %eax
	movl	%eax, -112(%rbp)
.L3:
	movl	-112(%rbp), %eax
	cmpl	$3079643, %eax
	jle	.L4
	addl	$1, -108(%rbp)
.L2:
	cmpl	$4, -108(%rbp)
	jle	.L5
	popq	%rbx
	popq	%r12
	popq	%r13
	popq	%r14
	popq	%r15
	popq	%rbp
	.cfi_def_cfa 7, 8
	ret
	.cfi_endproc
.LFE0:
	.size	main, .-main
	.ident	"GCC: (Ubuntu 4.8.4-2ubuntu1~14.04.4) 4.8.4"
	.section	.note.GNU-stack,"",@progbits
