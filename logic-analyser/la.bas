10 ' LA: test programs for logic-analyser captures (LACE.ASM, LAWR.ASM, LAHR.ASM).
20 ' Each runs an endless loop with interrupts off: reset to stop.
30 CLEAR 300,&HBFFF:SCREEN 0:WIDTH 80:KEY OFF:COLOR 15,4,4
40 PRINT "1: CE after a 1-byte HMMV   (SCREEN 5, display off)"
50 PRINT "2: CE after a 1-dot LMMV    (SCREEN 5, display off)"
60 PRINT "3: CE after a PSET          (SCREEN 5, display off)"
70 PRINT "4: two VRAM writes, AAh then 55h, 14 Z80 cycles apart (SCREEN 0 width 80, display on)"
75 PRINT "5: S#2 read back to back (SCREEN 5, display on, sprites off)"
80 PRINT:INPUT "Test (1-5)";T:IF T<1 OR T>5 THEN 80
90 IF T=4 THEN 200
95 IF T=5 THEN 300
100 BLOAD "LACE.BIN":POKE &HC003,T-1:DEFUSR=&HC000
110 SCREEN 5:VDP(1)=VDP(1) AND &HBF:X=USR(0)
200 BLOAD "LAWR.BIN":DEFUSR=&HC000
210 PRINT "Running test 4; reset to stop.":X=USR(0)
300 BLOAD "LAHR.BIN":DEFUSR=&HC000
310 SCREEN 5:VDP(9)=VDP(9) OR 2:X=USR(0)
