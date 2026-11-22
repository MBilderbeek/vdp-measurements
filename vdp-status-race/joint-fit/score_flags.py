#!/usr/bin/env python3
"""score_flags.py STAGE: per run label of out/STAGE, the number of read moments
where openMSX's majority outcome differs from the real machine's, summed per
flag (F, FH, other) and machine, over vdprace (text, SCREEN 5) and vdpmode.

The NMS 8250's CPU runs 116 ppm fast against its VDP, which moves all its read
moments by a few e: it is compared at the shift (-8..8) that fits best.
Prints one line per label; '-' where a run is missing."""
import glob, os, re, sys

J = os.path.dirname(os.path.abspath(__file__))
R = "/home/manuel/git/openMSX-Claude.git/.claude-data/vdp-measurements/vdp-status-race"
MACH = {"Panasonic_FS-A1GT": ("fs-a1gt", 1), "Sony_HB-F700D": ("hb-f700d", 0),
        "Philips_NMS_8250_V9958": ("nms8250-v9958", 0)}
FLAG = {0: "F", 1: "FH", 2: "other", 3: "other"}


def load(p):
    d = {}
    for l in open(p, "rb").read().split(b"\x1a")[0].decode(errors="replace").splitlines():
        t = l.split()
        if len(t) >= 4 and all(x.isdigit() for x in t[:4]):
            c = list(map(int, t[1:4]))
            if sum(c):
                d[int(t[0])] = max(range(3), key=lambda i: c[i])
    return d


def mism(real, emu, shift):
    r, o = load(real), load(emu)
    rng = range(-8, 9) if shift else [0]
    return min(sum(1 for e in r if e + s in o and o[e + s] != r[e]) for s in rng)


def pairs(rundir, m, kind):
    """(flag, real file, emulated file) of one run directory."""
    name, w = MACH[m]
    out = []
    if kind == "race":
        for md, fl in ((0, "f"), (1, "fh"), (2, "vr")):
            out.append((md, f"{R}/flag-race/{name}-{fl}.txt", f"{rundir}/f7v4m{md}.txt"))
    elif kind == "s5":
        for md, fl in ((0, "f"), (1, "fh"), (2, "vr")):
            out.append((md, f"{R}/flag-positions/{name}-{fl}-screen5.txt", f"{rundir}/r5m{md}w{w}.txt"))
    elif kind == "mode":
        for f in glob.glob(f"{rundir}/x*.txt"):
            n = os.path.basename(f)
            md, ab, j = int(n[1]), n[2:4], n[4]
            suf = "" if j == "n" else f"-r18-{j}"
            out.append((md, f"{R}/flag-positions/{name}-mode-{md}-{ab}{suf}.txt", f))
    return [(FLAG[md], r, e) for md, r, e in out if os.path.exists(r) and os.path.exists(e)]


def score(stage):
    res = {}
    for lab in sorted(os.listdir(f"{J}/out/{stage}")):
        s = {}
        for d in glob.glob(f"{J}/out/{stage}/{lab}/*-*"):
            if not os.path.isdir(d):
                continue
            m, kind = os.path.basename(d).rsplit("-", 1)
            if m not in MACH:
                continue
            for fl, r, e in pairs(d, m, kind):
                k = (fl, MACH[m][0])
                s[k] = s.get(k, 0) + mism(r, e, m.startswith("Philips"))
        res[lab] = s
    return res


if __name__ == "__main__":
    res = score(sys.argv[1])
    cols = [(f, m) for f in ("F", "FH", "other") for m in ("fs-a1gt", "hb-f700d", "nms8250-v9958")]
    print("label  " + " ".join(f"{f}:{m[:6]:6}" for f, m in cols))
    for lab, s in res.items():
        print(f"{lab:6} " + " ".join(f"{str(s.get(c, '-')):>9}" for c in cols))
