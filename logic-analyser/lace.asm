; LACE (MSX2, V9938/V9958): for a logic-analyser capture of the end of a short
; command. SCREEN 5 with the display off (set by LA.BAS). Endless loop, with
; interrupts off, one command run per round:
; - R#38 (DY low) = 0 and R#42 (NY low) = 1: two OUTs to port 99h each
;   (HMMV and LMMV move DY one line on, and may leave NY at 0, which means
;   1024 lines; PSET changes neither, but gets the same writes so that all
;   three loops have the same timing),
; - R#46 = the command: two OUTs to port 99h; the command starts at the 2nd
;   of them, the 6th /CSW of the round,
; - 8 x IN A,(99h) reading S#2 (CE = bit 0, TR = bit 7), one every 12 Z80
;   cycles, the first starting 14 cycles after the start of the OUT that
;   starts the command,
; - back to the start: one round is 8 + 6 x 14 + 8 x 12 + 11 = 199 Z80
;   cycles.
; The registers R#36-R#45 are set once from REGS; CMD (C003h) selects the
; command: 0 = HMMV 1 byte, 1 = LMMV 1 dot, 2 = PSET. Reset to stop.
; Cycle counts include the MSX M1 wait state (+1 per M1 cycle).

	output	"LACE.BIN"
	org	0C000h - 7
	db	0FEh
	dw	start, end, start

start:	jp	main
cmd:	db	0		; C003h: 0 = HMMV, 1 = LMMV, 2 = PSET

; R#36-R#46 per command: DX (2), DY (2), NX (2), NY (2), CLR, ARG, CMD
tab:	db	0, 0, 0, 1, 2, 0, 1, 0, 055h, 0, 0C0h	; HMMV, 1 byte (2 dots)
	db	0, 0, 0, 1, 1, 0, 1, 0, 005h, 0, 080h	; LMMV, 1 dot, IMP
	db	0, 0, 0, 1, 0, 0, 0, 0, 005h, 0, 050h	; PSET, IMP

main:	di
	ld	a,(cmd)		; HL = tab + 11 * cmd
	ld	l,a
	add	a,a
	add	a,l		; 3 * cmd
	add	a,a
	add	a,a		; 12 * cmd
	sub	l		; 11 * cmd
	ld	e,a
	ld	d,0
	ld	hl,tab
	add	hl,de
	ld	c,99h
	ld	a,36		; R#17 = 36, auto-increment
	out	(c),a
	ld	a,80h + 17
	out	(c),a
	ld	b,10		; R#36-R#45 through port 9Bh
	ld	c,9Bh
	otir
	ld	c,99h
	ld	a,(hl)		; the command byte
	ld	e,a
	ld	a,2		; R#15 = 2: S#2
	out	(c),a
	ld	a,80h + 15
	out	(c),a
	ld	h,0		; R#38 = 0
	ld	l,80h + 38
	ld	d,80h + 46
	ld	b,1		; R#42 = 1
.wait:	in	a,(c)		; wait for CE = 0
	rrca
	jr	c,.wait

loop:	out	(c),h		; 14: R#38 = 0
	out	(c),l		; 14
	ld	a,80h + 42	; 8
	out	(c),b		; 14: R#42 = 1
	out	(c),a		; 14
	out	(c),e		; 14: the command
	out	(c),d		; 14: R#46, the command starts
	rept	8
	in	a,(99h)		; 12 each: S#2
	endr
	jp	loop		; 11

end:
