# Joint fit of the VDP timing values in openMSX

The openMSX changes of the `vdp-status-race` documents rest on a handful of values that
can't be read from a measurement directly; they are fitted by running the same test
programs in openMSX and comparing with the machines. Several depend on each other, so they
are fitted here together, against all tests on all three machines at once, with the range
of each value that fits.

## The values

| value | what it is | depends on |
|---|---|---|
| F window (before, after) | a read of S#0 within this window around the moment openMSX sets F loses it | - |
| FH window (before, after) | the same for S#1 and FH | - |
| output delay | /INT of F and the picture follow the VDP's timing by this much | F window (the interrupt test starts at the lost window) |
| line interrupt delay | /INT of FH follows FH by this much | FH window |
| line latch | where in the line display mode, enable and sprite disable are taken | line interrupt delay (`HINTTOBL` counts from the interrupt) |
| R#23 lead | a mid-line R#23 write shows from the first 8-pixel group starting this long after it | output delay (the groups are the picture's) |

All in VDP cycles. The flag positions of `flag-positions.md` (where openMSX sets HR, VR, F,
FH) are measured more directly (`vdpmode`, to one Z80 cycle) and stay fixed here.

## The tests and how they are scored

Real results: the files of the other folders of this repository. Machines: Panasonic
FS-A1GT and Philips NMS 8250 (both V9958), Sony HB-F700D (V9938).

| test | machines | score |
|---|---|---|
| `vdprace`, text and SCREEN 5 (F, FH, VR) | all three (NMS 8250: text) | edge distance (below) |
| `vdpmode`: modes, mode switches, R#18 = 07h/08h | FS-A1GT, HB-F700D | edge distance |
| `vdpirq`, `vdpirqh`, `vdpirqh2` | all three | lost + pulse length, openMSX minus machine, Z80 cycles |
| `HINTTOBL` | all three | the last row with a blank line |
| R#23 staircase (`vdpline4`) | FS-A1GT, HB-F700D | the group from which the seam is at 144 and at 152 |
| `vdpfh` | FS-A1GT, HB-F700D | the stripe's columns against the photos |

**Edge distance** (`score_edges.py`): an edge is a read moment where the outcome of most
trials changes; its position is interpolated with the fraction of trials. Each of the
machine's edges is matched with openMSX's nearest edge of the same kind (from-outcome,
to-outcome); the distance counts in read moments (1 Z80 cycle), capped at 3. The NMS 8250's
CPU runs 116 ppm fast against its VDP, which moves all its read moments by a few: it is
compared at the shift that fits best.

**Three runs per setting.** `vdprace` doesn't choose its read moment; it measures, per
trial, where the read fell relative to HR. openMSX's CPU and VDP clocks are locked, so one
run gets trials at only some read moments, and an edge between two of them is only placed
somewhere in that gap: a run with a different start can put the same model's edge a read
moment further (`starts.edges`, five start delays: 11 to 21 summed on the FS-A1GT, for the
tests the setting can't affect). So every setting is run three times, each with a
different idle loop before the test (`-d13`, `-d29` disks), and the trials are merged
(`starts-merged.edges`). The HB-F700D's clocks are locked too, which is why its edges are
known only to within a read moment.

## Results

**F window** (`s1m.edges`, 5x5 grid in steps of 3, merged): before 7 to 10, after 15 to 18
fit (FS-A1GT + HB-F700D 17.9 to 18.2); before 4 or 13, or after 12 or 21, are 26 or more.

**FH window** (`s1m.edges`, `s1r.edges`): the flag tests alone allow before 17 to 22, after
9 to 10 (16.3 to 17.2; after 6: 27 or more). openMSX's reads fall on the Z80 grid, so 17
and 18 act the same, and 19 and 20.

**Output delay** (`s2a.score`): the interrupt tests put every machine within 0.5 Z80 cycles
for 27 to 29, within 0.7 for 30, 1.4 to 1.5 off for 24 and 33. The F window makes no
difference here. `vdpfh` (`s3c.score`): 27 to 29 put the FS-A1GT's stripe on its photo,
30 3 pixels left. The photos of `vdpline3` (`output-delay.md`): 28.9 to 30.5. Together:
28 to 29.

**Line interrupt delay** (`s2b.score`): with the FH window's 'before' at 18, 22 to 24 put
every machine within 0.9; with 19 to 21, 16 to 18 do. **`HINTTOBL`** (`s3a.score`): only
with 22 does one latch reproduce both the FS-A1GT (241) and the HB-F700D (242): latch 172
to 174 (20 and 24: no latch fits both). So: line interrupt delay 22, FH 'before' 17 to 18,
latch 172 to 174. The NMS 8250 then reads 242, where it showed 243 (its clocks aren't
locked; not explained further).

**R#23 lead** (`s3b*.score`): the seam depends on the lead minus the output delay. With 29
the HB-F700D (at 144 from group 1, at 152 from group 6) allows 24 to 27; the FS-A1GT, whose
groups 0 and 5 flip on the machine, allows a wider range.

| value | fits | chosen |
|---|---|---|
| F window | before 7 to 10, after 15 to 18 | 7, 15 |
| FH window | before 17 to 18, after 9 to 10 | 18, 9 |
| output delay | 28 to 29 | 29 |
| line interrupt delay | 22 | 22 |
| line latch | 172 to 174 | 173 |
| R#23 lead (with output delay 29) | 24 to 27 | 26 |

One value each for the V9938 and the V9958: no test asks for a difference between them.

**The chosen set, all tests together** (`fin.*`), against the values of the PRs before
this fit (per-chip FH windows 21/6 and 21/12, output delay 30; `finp.*`):

| | chosen | before |
|---|---|---|
| F edges (FS-A1GT, HB-F700D, NMS 8250) | 8.3, 9.8, 0.7 | 7.8, 9.8, 0.7 |
| FH edges | 4.7, 11.5, 0.6 | 16.1, 10.0, 0.6 |
| interrupt tests, largest deviation | 0.9 Z80 cycles | 1.5 |
| `HINTTOBL` | 241, 242, 242 | 241, 242, 242 |
| R#23 | FS-A1GT (0, 5), HB-F700D (1, 6) | the same |
| `vdpfh` | FS-A1GT 57-227 (photo 57-227), HB-F700D 52-219 (55-222) | 54-224, 52-219 |

## Reproduce

1. Apply `env-overrides.patch` to the openMSX stack (it was made on the slot-position PR's
   tip; it only adds environment overrides `FB FA FHB FHA OD LD LO RL` for the values
   above) and build it.
2. In `run.sh`, set `J` to this folder and `WT` to that build; `openmsx-bin.sh` is a
   wrapper that runs openMSX with its own settings folder, offscreen, without sound.
   `disks/hint` needs MSX-DOS (`MSXDOS.SYS`, `COMMAND.COM`) and `HINTTOBL.COM` from issue
   #1310 next to `HINTZ80.COM`.
3. Run a job list (`jobs/`) with `xargs -P <cores> -L 1 ./run.sh < jobs/<list>`, then the
   scorers: `score_edges.py STAGE --merge`, `score_irq.py STAGE`, `score_misc.py STAGE`.
   A full stage takes one to three hours on 32 cores.
