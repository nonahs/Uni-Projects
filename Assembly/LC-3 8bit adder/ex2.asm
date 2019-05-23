; Shanon Altments salt280 562463901
; signed 8 bit arithmetic with carry and overflow checking

        	.orig   x3000
		lea 	r0, start
		jmp	r0

op1     	.fill   b01000000	; must be < 256, treating as -128 to 127
op2     	.fill   b01100000	; must be < 256, treating as -128 to 127

start		ld      r0, op1		; r0 is op1
	        ld      r1, op2		; r1 is op2

; now the arithmetic

        	add     r2, r0, r1	; r2 is cresult
		ld	r3, mask
		and	r3, r2, r3	; r3 is result
        	st      r3, result
; carry
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
		add	r2, r2, r0	; subtraction
		brz	different	; actually the same
		add	r3, r3, #1
different	st	r3, overflow
;print section
		ld	r1, op1
		jsr 	output		; print op1
		ld	r0, new_line	
		out			; linebreak
		ld	r1, op2
		jsr	output		; print op2
		ld	r0, new_line
		out			; linebreak
		lea	r0, divider
		puts			; print divier
		ld	r0, new_line
		out			; linebreak
		ld	r1, result
		jsr	output		; print result
		ld	r0, space
		out			; print space
		ld	r1, carry
		brz	space_before	; print space if no carry
		ld	r0, carry_letter
		out			; print carry
		brnzp 	print_overflow
space_before	ld	r0, space
		out			; print space
print_overflow	ld	r0, space
		out
		ld	r1, overflow
		brz	finished
		ld	r0, overflow_letter
		out			; print overflow
		brnzp 	finished
;output sub
output		st	r7, return_loc
		ld	r3, bitsize	; number of bits
		and	r4, r4, #0
loop
		add	r5, r3, r4	; add counter to bitsize to check if done
		brz	end
		lea	r5, masks
		add	r5, r5, r4	; r4 is our index
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
		ld	r7, return_loc
		ret			;end of sub

finished
		HALT

mask		.fill	b11111111
signbit		.fill	b10000000
carrybit	.fill	b100000000
zero		.fill	x30
one		.fill	x31
bitsize		.fill	#-8
new_line	.fill	x0A
space		.fill	x20
carry_letter	.fill	x63
overflow_letter	.fill	x76
masks		.fill	b10000000
		.fill	b01000000
		.fill	b00100000
		.fill	b00010000
		.fill	b00001000
		.fill	b00000100
		.fill	b00000010
		.fill	b00000001
result  	.blkw   1
carry   	.blkw   1
overflow    	.blkw   1
return_loc	.blkw	1
divider		.stringz "========"

		.end