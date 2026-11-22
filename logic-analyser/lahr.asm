; LAHR (MSX2, V9938/V9958): for a logic-analyser capture of HR as the VDP
; drives it on the CPU data bus, against the VRAM access slots. SCREEN 5 with
; the display on and sprites off (set by LA.BAS). R#15 = 2 is set once; then
; an endless loop, with interrupts off, of reads of S#2:
; - 32 x IN A,(99h), each 12 Z80 cycles after the one before,
; - back to the start: the first read of the next round comes 11 + 12 = 23
;   Z80 cycles after the last one; one round is 32 x 12 + 11 = 395 Z80 cycles.
; S#2 bit 5 (CD5) is HR, bit 6 (CD6) is VR.
; Reset to stop. Cycle counts include the MSX M1 wait state (+1 per M1 cycle).

	output	"LAHR.BIN"
	org	0C000h - 7
	db	0FEh
	dw	start, end, start

start:	di
	ld	a,2		; R#15 = 2: port 99h reads S#2
	out	(99h),a
	ld	a,80h + 15
	out	(99h),a

loop:	rept	32
	in	a,(99h)		; 12
	endr
	jp	loop		; 11

end:
