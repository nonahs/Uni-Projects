; signed 30 bit arithmetic with carry and overflow checking

        	.orig   x3000
		lea 	r0, start
		jmp	r0

op1_lsw .fill b101010101010101
op1_msw .fill b100000000000000
op2_lsw .fill b111111111111111
op2_msw .fill b101111111111111

start		ld      r0, op1_lsw	; r0 is op1
	        ld      r1, op2_lsw	; r1 is op2
		and	r4, r4, #0	; counter
		st	r4, ari_count
		brnzp 	arithmetic

start_msw	ld	r0, op1_msw
		ld	r1, op2_msw
; now the arithmetic
arithmetic     	add     r2, r0, r1	; r2 is cresult
		ld	r3, mask
		and	r3, r2, r3	; r3 is result
		ld	r4, carry_lsw	; carry from lsw 0 if currently doing lsw
		add	r3, r3, r4	; add carry from lsw
	      	st      r3, result
;carry sec
		and	r3, r3, #0	; clear r3, carry
		ld	r4, carrybit	; r4 is carrybit
        	and     r4, r2, r4
		brz	nocarry
		add	r3, r3, #1
nocarry        	st      r3, carry
; overflow
		and	r3, r3, #0
		ld	r4, signbit	; r4 is signbit
		and	r0, r0, r4	; r0 no longer op1
		brz	plus1
		add	r3, r3, #1
plus1		add	r0, r3, #0	; r0 sign1
		and	r3, r3, #0
		and	r1, r1, r4	; r1 no longer op1
		brz	plus2
		add	r3, r3, #1
plus2		add	r1, r3, #0	; r1 sign2
		and	r3, r3, #0
		and	r2, r2, r4	; r2 no longer cresult
		brz	plus3
		add	r3, r3, #1
plus3		add	r2, r3, #0	; r2 is signres
		and	r3, r3, #0
; we need to compare sign1(r0) with sign2(r1)
		not	r0, r0
		add	r0, r0, #1	; 2's complement
		add	r1, r1, r0	; subtraction
		brnp	different
; compare signres(r2) with sign1(r0)
		and 	r3, r3, #0
		add	r2, r2, r0	; subtraction
		brz	different	; actually the same
		add	r3, r3, #1
different	add	r3, r3, #-1
		st	r3, overflow
;check which word and save result
		ld 	r4, ari_count
		brp	print_section	; positive if done
		add	r4, r4, #1
		st	r4, ari_count
		ld	r1, carry
		st	r1, carry_lsw	; copy carry
		ld	r1, result
		st	r1, result_lsw	; copy result
		brnzp	start_msw
		
print_section
		ld	r1, op1_msw
		jsr 	output		; print op1_msw
		ld	r1, op1_lsw
		jsr	output		; print op1_lsw
		ld	r0, new_line	
		out			; linebreak
		ld	r1, op2_msw
		jsr	output		; print op2_msw
		ld 	r1, op2_lsw
		jsr 	output		; print op2_lsw
		ld	r0, new_line
		out			; linebreak
		lea	r0, divider
		puts			; print divier
		ld	r0, space
		out			; print space
		lea	r0, divider
		puts			; print divier
		ld	r0, new_line
		out			; linebreak
		ld	r1, result
		jsr	output		; print result
		ld	r1, result_lsw	
		jsr	output		; print lsw result
		ld	r1, carry
		brz	space_before	; skip to space if no carry
		ld	r0, carry_letter
		out			; print carry
		brnzp 	print_overflow
space_before	ld	r0, space
		out			; print space
print_overflow	ld	r0, space
		out
		ld	r1, overflow
		brz	finished	; skip to end if no overflow
		ld	r0, overflow_letter
		out			; print overflow
		brnzp 	finished
; output sub, outputs whatever is in r1
output		st	r7, return_loc
		ld	r3, bitsize	; number of bits
		and	r4, r4, #0	; r4 is counter
loop
		add	r5, r3, r4	; add counter to bitsize to check if done
		brz	end
		lea	r5, masks
		add	r5, r5, r4	; add mask address with counter
		add	r4, r4, #1	; increase counter
		ldr	r6, r5, #0	; load mask
		and	r6, r6, r1	; and mask with op1
		brp	outone

outzero		ld 	r0, zero
		out
		brnzp	loop
outone
		ld 	r0, one
		out	
		brnzp	loop
end
		ld	r0, space
		out			; print space
		ld	r7, return_loc
		ret			; end of sub

finished
		HALT

mask		.fill	b111111111111111
signbit		.fill	b100000000000000
carrybit	.fill	b1000000000000000
zero		.fill	x30
one		.fill	x31
bitsize		.fill	#-15
new_line	.fill	x0A
space		.fill	x20
carry_letter	.fill	x63
overflow_letter	.fill	x76
masks		.fill	b100000000000000
		.fill	b010000000000000
		.fill	b001000000000000
		.fill	b000100000000000
		.fill	b000010000000000
		.fill	b000001000000000
		.fill	b000000100000000
		.fill	b000000010000000
		.fill	b000000001000000
		.fill	b000000000100000
		.fill	b000000000010000
		.fill	b000000000001000
		.fill	b000000000000100
		.fill	b000000000000010
		.fill	b000000000000001
result  	.blkw   1
carry   	.blkw   1
overflow    	.blkw   1
return_loc	.blkw	1
ari_count	.blkw	1
carry_lsw	.blkw	1
result_lsw	.blkw	1
divider		.stringz "==============="

		.end