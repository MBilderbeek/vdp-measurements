# VDPLINE 4 in openMSX: raw screenshot while the staircase runs (PC in C000h-C7FFh, C00Bh = 1).
set throttle off
proc r23_wait {} {
	set pc [reg pc]
	if {$pc >= 0xC000 && $pc < 0xC800 && [peek 0xC00B] == 1} {
		set ::throttle on; after time 1 { screenshot -raw $::env(OUT)/shot.png; exit }
	} else { after time 0.5 r23_wait }
}
after time 20 r23_wait
after time 600 exit
