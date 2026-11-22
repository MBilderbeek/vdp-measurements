#!/usr/bin/env python3
"""score_edges.py STAGE [--detail LABEL]: per run label, how far openMSX's edges
lie from the machines' edges, in read moments (e, 1 Z80 cycle), summed per flag
(F, FH, other) and machine, over vdprace (text, SCREEN 5) and vdpmode.

An edge is a change of the outcome that most trials have; its position is
interpolated with the fraction of trials (where the new outcome's fraction
crosses one half). Each of the machine's edges is matched with openMSX's edge
of the same kind (from-outcome, to-outcome) nearest to it; the distance counts,
up to 3; an edge with no partner counts 3. The NMS 8250 (CPU 116 ppm fast) is
compared at the shift of its e (-8..8) that fits best.

Unlike a count of differing read moments, this doesn't jump when an edge's
fraction is near one half, and it says by how much an edge is off."""
import glob, os, sys

J = os.path.dirname(os.path.abspath(__file__))
R = "/home/manuel/git/openMSX-Claude.git/.claude-data/vdp-measurements/vdp-status-race"
MACH = {"Panasonic_FS-A1GT": ("fs-a1gt", 1), "Sony_HB-F700D": ("hb-f700d", 0),
        "Philips_NMS_8250_V9958": ("nms8250-v9958", 0)}
FLAG = {0: "F", 1: "FH", 2: "other", 3: "other"}
CAP = 3.0


def counts(p):
    d = {}
    for l in open(p, "rb").read().split(b"\x1a")[0].decode(errors="replace").splitlines():
        t = l.split()
        if len(t) >= 4 and all(x.isdigit() for x in t[:4]):
            c = list(map(int, t[1:4]))
            if sum(c):
                d[int(t[0])] = [a + b for a, b in zip(d.get(int(t[0]), [0, 0, 0]), c)]
    return d


def load(ps):
    """One file, or several (their trials added up per e)."""
    d = {}
    for p in ([ps] if isinstance(ps, str) else ps):
        for e, c in counts(p).items():
            d[e] = [a + b for a, b in zip(d.get(e, [0, 0, 0]), c)]
    return [(e, [x / sum(c) for x in c]) for e, c in sorted(d.items())]


def edges(rows):
    out = []
    for (e1, f1), (e2, f2) in zip(rows, rows[1:]):
        a = max(range(3), key=lambda i: f1[i])
        b = max(range(3), key=lambda i: f2[i])
        if a != b:
            x1, x2 = f1[b], f2[b]
            pos = e1 + (e2 - e1) * ((.5 - x1) / (x2 - x1) if x2 != x1 else .5)
            out.append((pos, a, b))
    return out


def dist(real, emu, shift):
    er, eo = edges(load(real)), edges(load(emu))
    best = None
    for s in (range(-8, 9) if shift else [0]):
        tot = 0.0
        for p, a, b in er:
            c = [abs(q - s - p) for q, x, y in eo if (x, y) == (a, b)]
            tot += min([CAP] + c)
        best = tot if best is None else min(best, tot)
    return best, len(er)


def pairs(rundir, m, kind):
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


def score(stage, detail=None, merge=False):
    """Labels 'setting@variant' are merged per setting if merge is set."""
    groups = {}
    for lab in sorted(os.listdir(f"{J}/out/{stage}")):
        key = lab.split("@")[0] if merge else lab
        groups.setdefault(key, []).append(lab)
    res = {}
    for key, labs in groups.items():
        s = {}
        emus = {}
        for lab in labs:
            for d in glob.glob(f"{J}/out/{stage}/{lab}/*-*"):
                if not os.path.isdir(d):
                    continue
                m, kind = os.path.basename(d).rsplit("-", 1)
                if m not in MACH:
                    continue
                for fl, r, e in pairs(d, m, kind):
                    emus.setdefault((fl, r, m), []).append(e)
        for (fl, r, m), es in emus.items():
                v, n = dist(r, es, m.startswith("Philips"))
                k = (fl, MACH[m][0])
                s[k] = s.get(k, 0.0) + v
                if detail == key and v >= 1:
                    print(f"  {os.path.basename(r):40} {v:4.1f} over {n} edges")
        res[key] = s
    return res


if __name__ == "__main__":
    a = sys.argv[1:]
    merge = "--merge" in a
    det = a[a.index("--detail") + 1] if "--detail" in a else None
    res = score(a[0], det, merge)
    cols = [(f, m) for f in ("F", "FH", "other") for m in ("fs-a1gt", "hb-f700d", "nms8250-v9958")]
    print("label  " + " ".join(f"{f}:{m[:6]:>6}" for f, m in cols))
    for lab, s in res.items():
        print(f"{lab:6} " + " ".join(f"{s[c]:9.1f}" if c in s else f"{'-':>9}" for c in cols))
