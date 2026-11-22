; LAWR (MSX2, V9938/V9958): for a logic-analyser capture of two CPU VRAM
; writes in quick succession. SCREEN 0 width 80 with the display on (set by
; LA.BAS). Endless loop, with interrupts off, one pair per round:
; - VRAM write address = 02000h: two OUTs to port 99h (R#14 = 0 is set once),
; - OUT (C),A with AAh, then OUT (C),B with 55h to port 98h: the second
;   starts 14 Z80 cycles after the first (the 3rd and 4th /CSW of the round),
;   the first to 02000h, the second to 02001h if its request isn't lost,
; - 4 x NOP, so that the 55h's access is done before the next address write,
; - back to the start: one round is 14 + 14 + 5 + 14 + 14 + 4 x 5 + 5 + 11
;   = 97 Z80 cycles.
; Reset to stop. Cycle counts include the MSX M1 wait state (+1 per M1 cycle).

	output	"LAWR.BIN"
	org	0C000h - 7
	db	0FEh
	dw	start, end, start

start:	di
	ld	c,99h
	xor	a		; R#14 = 0: A16-A14 of the VRAM address
	out	(c),a
	ld	a,80h + 14
	out	(c),a
	ld	d,000h		; address 02000h, write: 00h, then 40h + 20h
	ld	e,060h
	ld	a,0AAh
	ld	b,055h

loop:	out	(c),d		; 14: address low
	out	(c),e		; 14: address high, write mode
	dec	c		; 5: C = 98h
	out	(c),a		; 14: AAh
	out	(c),b		; 14: 55h, 14 cycles after the AAh
	nop			; 4 x 5
	nop
	nop
	nop
	inc	c		; 5: C = 99h
	jp	loop		; 11

end:
