# Logic-analyser test programs (for the NMS 8280)

`la.dsk` (720 KB, Disk BASIC) starts `AUTOEXEC.BAS`, a menu of five tests. Each test is an
endless loop with interrupts off; reset the machine to stop it and choose the next one.
The 8280's CPU and VDP clocks aren't locked, so the rounds fall at all phases of the VDP's
slots: no trigger is needed, any capture of 3 lines will do.

Sources: `lace.asm` (tests 1 to 3), `lawr.asm` (test 4), `lahr.asm` (test 5), `la.bas` (the menu), assembled
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

## Test 5: where HR changes, relative to the VRAM access slots (#2314, #2313)

SCREEN 5 with the display on and sprites off. R#15 = 2 is set once. Then an endless loop of
`IN A,(99h)`, which reads S#2: 32 reads 12 Z80 cycles apart, then 23 to the next round's
first. Nothing else happens on the CPU side: no writes, no interrupts.

HR (S#2 bit 5) changes twice in every line, so every capture of 3 lines holds about 6 HR
edges, in the display area or in the border.

**Pins (16):**
- /RAS, /CAS0, /CAS1, R/W;
- AD0 to AD7;
- /CSR;
- CD5 (HR) and CD6 (VR), as the VDP drives them during each read;
- HSYNC.

**Captures:** about 10, for about 60 HR edges.

**What to look for:**
- For each HR edge: the last read with the old value and the first with the new one, both
  against the slot grid (the refresh /RAS, and in the display area the data bursts) and
  HSYNC. One edge only brackets the change to 12 Z80 cycles, but the 8280's clocks aren't
  locked, so the reads fall at all phases, and many edges together narrow it down.
- Where CD5 changes during a read, if it does: that shows when the VDP takes the value.
- **The question:** does HR fall about 181 VDP cycles after HSYNC goes active (as the CPU
  tests put it, through an assumed delay of a CPU access) or about 210 (as IKA9958 has it,
  and as the first display data read at 227 needs, with the photos of `vdpline3`)?
  The reasoning is in the comment on openMSX PR #2314.
