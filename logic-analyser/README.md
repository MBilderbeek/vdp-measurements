# Logic-analyser test programs (for the NMS 8280)

`la.dsk` (720 KB, Disk BASIC) starts `AUTOEXEC.BAS`, a menu of four tests. Each test is an
endless loop with interrupts off; reset the machine to stop it and choose the next one.
The 8280's CPU and VDP clocks aren't locked, so the rounds fall at all phases of the VDP's
slots: no trigger is needed, any capture of 3 lines will do.

Sources: `lace.asm` (tests 1 to 3), `lawr.asm` (test 4), `la.bas` (the menu), assembled
with sjasmplus. Cycle counts are Z80 cycles including the MSX M1 wait state.

## Tests 1 to 3: when CE clears after a short command (#2304)

SCREEN 5 with the display off. The command's registers are set once. Then every round of
199 Z80 cycles:

| /CSW or /CSR | what |
|---|---|
| /CSW 1, 2 | R#38 (DY low) = 0 |
| /CSW 3, 4 | R#42 (NY low) = 1 |
| /CSW 5, 6 | R#46 = the command: **it starts at /CSW 6** |
| /CSR 1 to 8 | S#2 (R#15 = 2), the first 14 Z80 cycles after the start of /CSW 6's OUT, then one every 12 |

The commands, one per test:
1. HMMV of one byte (2 dots) at (0, 256), colour 55h;
2. LMMV of one dot at (0, 256), colour 5, IMP;
3. PSET at (0, 256), colour 5, IMP.

Its access is in the VRAM area of line 256: address 8000h.

**Pins (16):**
- /RAS, /CAS0, /CAS1, R/W;
- AD0 to AD7;
- /CSW, /CSR;
- CD0 (CE) and CD7 (TR).

**Captures:** a capture of 3 lines holds about 3 rounds; about 5 captures per test.

**What to look for:**
- In each round, the command's accesses after /CSW 6, and the first /CSR with CD0 = 0.
- Whether anything happens on the VRAM bus between the last access and that read.
- With CD7: when TR is set.

## Test 4: two VRAM writes in quick succession (#2303)

SCREEN 0 width 80 with the display on. Every round of 97 Z80 cycles:

| /CSW | what |
|---|---|
| 1, 2 (port 99h) | VRAM write address 02000h |
| 3 (port 98h) | AAh, for 02000h |
| 4 (port 98h) | 55h, starting 14 Z80 cycles after /CSW 3; for 02001h, unless its request is lost |

**Pins (16):**
- /RAS, /CAS0, /CAS1, R/W;
- AD0 to AD7;
- /CSW;
- RD0, RD1 and RD3. During a write, the VDP drives the byte there:
  - RD0 and RD1 tell 00h, 55h and AAh apart;
  - RD3 catches some partial bytes.

**Captures:** a capture of 3 lines holds about 7 rounds; about 10 captures.

**What to look for:**
- Which writes happen, to which address (02000h or 02001h), with which byte, against the moment of /CSW 4.
- The rounds where the first write's access comes after /CSW 4 are the ones that matter. On the machines, both writes then often store 55h.
