#!/usr/bin/env python3
"""score_irq.py STAGE: per run label, for vdpirq (F), vdpirqh and vdpirqh2 (FH):
openMSX's minus the machine's distance (Z80 cycles) from where the lost window
starts to where "before" comes back, both interpolated over the trials (the
pulselen measure, which doesn't depend on the read moments' offset, so the
NMS 8250 compares directly). Prints per label the differences and the largest."""
import glob, os, sys

J = os.path.dirname(os.path.abspath(__file__))
R = "/home/manuel/git/openMSX-Claude.git/.claude-data/vdp-measurements/vdp-status-race/output-delay"
MACH = {"Panasonic_FS-A1GT": ("fs-a1gt", 1), "Sony_HB-F700D": ("hb-f700d", 0),
        "Philips_NMS_8250_V9958": ("nms8250-v9958", 0)}
# disk -> (emulated file prefix, real file infix, flag)
TESTS = {"irq": ("i", "irq", "F"), "irqh": ("h", "irqh", "FH"), "irqh2": ("j", "irqh2", "FH")}


def cross(rows, i0, rising):
    for i in range(i0, len(rows) - 1):
        (e1, b1), (e2, b2) = rows[i], rows[i + 1]
        if (b1 < .5 <= b2) if rising else (b1 >= .5 > b2):
            return e1 + (e2 - e1) * (.5 - b1) / (b2 - b1), i + 1
    return None, None


def dist(ps):
    """One file or several (trials added up per e)."""
    acc = {}
    for p in ([ps] if isinstance(ps, str) else ps):
        for l in open(p, "rb").read().split(b"\x1a")[0].decode(errors="replace").splitlines():
            t = l.split()
            if len(t) == 5 and all(x.isdigit() for x in t):
                c = list(map(int, t[1:]))
                if sum(c) and int(t[0]) >= 25:
                    acc[int(t[0])] = [a + b for a, b in zip(acc.get(int(t[0]), [0] * 4), c)]
    rows = [(e, c[2] / sum(c)) for e, c in sorted(acc.items())]
    s, i = cross(rows, 0, False)
    if s is None:
        return None
    e, _ = cross(rows, i, True)
    return None if e is None else e - s


def score(stage):
    """Labels 'setting@variant' are merged per setting."""
    groups = {}
    for lab in sorted(os.listdir(f"{J}/out/{stage}")):
        groups.setdefault(lab.split("@")[0], []).append(lab)
    res = {}
    for key, labs in groups.items():
        emus = {}
        for lab in labs:
            for d in glob.glob(f"{J}/out/{stage}/{lab}/*-irq*"):
                if not os.path.isdir(d):
                    continue
                m, kind = os.path.basename(d).rsplit("-", 1)
                name, w = MACH[m]
                pre, infix, flag = TESTS[kind]
                for scr, fn in (("screen5", "gg"), ("text", "tt")):
                    real = f"{R}/{name}-{infix}-{scr}.txt"
                    emu = f"{d}/{pre}{fn}w{w}.txt"
                    if os.path.exists(real) and os.path.exists(emu):
                        emus.setdefault((f"{name[:6]}-{infix}-{scr[:2]}", real), []).append(emu)
        out = {}
        for (k, real), es in emus.items():
            a, b = dist(es), dist(real)
            if a is not None and b is not None:
                out[k] = a - b
        res[key] = out
    return res


if __name__ == "__main__":
    for lab, out in score(sys.argv[1]).items():
        if out:
            mx = max(abs(v) for v in out.values())
            print(f"{lab:14} max|d| {mx:4.1f}  " + " ".join(f"{k}:{v:+.1f}" for k, v in sorted(out.items())))
