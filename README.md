# VDP measurements: raw results

Raw results of tests run on real MSX machines, measuring how the V9938 and V9958 VDPs time
things. The tests themselves, how to run them, how to read their results, a summary and the
conclusions are in openMSX's repository, under `doc/internal/`; this repository only keeps
the full results, so that the conclusions can be checked against all of them.

Each folder here belongs to a test in openMSX's `doc/internal/`:

| folder | test (in openMSX) | what it measures |
|---|---|---|
| `vdp-vram-timing/cpu-write-pairs` | `doc/internal/vdp-vram-timing/cpu-write-pairs` | two CPU writes to VRAM in quick succession: which byte lands where |
| `vdp-vram-timing/command-slots` | `doc/internal/vdp-vram-timing/command-slots` | when a short command finishes, relative to HR |
| `vdp-vram-timing/command-end` | `doc/internal/vdp-vram-timing/command-end` | when CE clears after a command |
| `vdp-status-race/flag-race` | `doc/internal/vdp-status-race` | a status read that loses F or FH being set |
| `vdp-status-race/output-delay` | `doc/internal/vdp-status-race/output-delay.md` | the interrupt line and the picture lag the status flags |
| `vdp-status-race/flag-positions` | `doc/internal/vdp-status-race/flag-positions.md` | where in the line HR, VR, F and FH change |
| `vdp-status-race/r23-groups` | `doc/internal/vdp-status-race/r23-groups.md` | a mid-line R#23 write takes effect per 8-pixel group (photos) |
| `vdp-status-race/line-latch` | `doc/internal/vdp-status-race/line-latch.md` | the line counter reset (vdplc) |
| `vdp-status-race/yjk-timing` | `doc/internal/vdp-status-race/yjk-timing.md` | YJK moves the picture, not the timing; the latch moves with R#18 |
| `vdp-status-race/yjk-gap` | `doc/internal/vdp-status-race/yjk-gap.md` | the 4 pixels before a YJK picture (photos) |
| `vdp-status-race/nt-field` | `doc/internal/vdp-status-race/nt-field.md` | an NT write in the middle of a field |

Machines: Panasonic FS-A1GT (V9958, with the S1990's extra wait on VDP I/O), Sony HB-F700D
(V9938), Philips NMS 8250 with its V9938 replaced by a V9958 (no extra wait). Files are
named after the machine: `fs-a1gt`, `hb-f700d`, `nms8250-v9958`.

The file formats are described in the README of each test in openMSX, and the scripts there
(`summary.py`, `fit.py`) read these files.

`vdp-status-race/flag-positions/<machine>-edge-m3-*.txt` and `-edge-m4-*.txt` are `vdpedge`
modes 3 and 4: two CPU writes to VRAM in quick succession (AAh, then 55h, 14 Z80 cycles
apart; columns: mode 3 second write lost, both written, other; mode 4 (55h, 00h, 00h),
(AAh, 55h, 00h), other, plus all byte triples read back as `T` lines). The question they
answer is the one of `vdp-vram-timing/cpu-write-pairs`, which measured it in full.
