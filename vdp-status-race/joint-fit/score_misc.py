#!/usr/bin/env python3
"""score_misc.py STAGE: per run label, the tests that are read from the screen:
- hint: HINTTOBL, the last row with a blank line (209 + row), over 60 frames;
  machines: FS-A1GT 241, HB-F700D 242, NMS 8250 243 (filmed; clocks not locked);
- r23: the R#23 staircase, from which group on the seam is at 144 and at 152;
  machines: HB-F700D 1 and 6; FS-A1GT 0 or 1 and 5 or 6 (groups 0 and 5 flip);
- fh: vdpfh, the stripe's first and last display x; photos: FS-A1GT 57-227
  (wobbling a few pixels), HB-F700D 55-222."""
import glob, os, subprocess, sys

J = os.path.dirname(os.path.abspath(__file__))
SHORT = {"Panasonic_FS-A1GT": "GT", "Sony_HB-F700D": "HB", "Philips_NMS_8250_V9958": "8250"}


def img(f):
    d = subprocess.run(["pngtopnm", f], capture_output=True).stdout
    p = d.split(b"\n", 3)
    w, h = map(int, p[1].split())
    return w, h, p[3]


def hint(d):
    mx = []
    for f in sorted(glob.glob(d + "/f*.png")):
        w, h, a = img(f)
        px = lambda x, y: a[3 * (w * y + x):3 * (w * y + x) + 3]
        bord = px(2, 2)
        tops = [y for y in range(h) if px(40, y) != bord]
        if not tops:
            continue
        top = tops[0]
        bl = [y - top for y in range(top, min(h, top + 192))
              if all(px(x, y) == bord for x in range(0, w, 4))]
        mx.append(max(bl) // 4 if bl else -1)
    return 209 + max(mx) if mx else None


def r23(d):
    f = d + "/shot.png"
    if not os.path.exists(f):
        return None
    w, h, a = img(f)
    g = lambda x, y: a[3 * (y * w + x)] > 128
    seams = []
    for y in range(h):
        tr = [x - 32 for x in range(33, 288) if g(x, y) != g(x - 1, y)]
        if len(tr) == 1 and y >= 100:
            seams.append(tr[0])
    # 64 stair lines in groups of 8: the seam per group
    groups = [seams[i:i + 8] for i in range(0, min(64, len(seams)), 8)]
    per = [max(set(gr), key=gr.count) for gr in groups if gr]
    first = lambda v: next((i for i, s in enumerate(per) if s >= v), None)
    return first(144), first(152)


def fh(d):
    f = d + "/shot-fh.png"
    if not os.path.exists(f):
        return None
    w, h, a = img(f)
    res = {}
    for y in range(h):
        row = [a[3 * (y * w + x):3 * (y * w + x) + 3] for x in range(w)]
        xs = [x for x in range(w) if row[x] != row[2]]
        if len(xs) > w // 4:
            k = (xs[0] - 32, xs[-1] - 32)
            res[k] = res.get(k, 0) + 1
    return max(res, key=res.get) if res else None


if __name__ == "__main__":
    st = sys.argv[1]
    for lab in sorted(os.listdir(f"{J}/out/{st}")):
        out = []
        for d in sorted(glob.glob(f"{J}/out/{st}/{lab}/*-*")):
            if not os.path.isdir(d):
                continue
            m, kind = os.path.basename(d).rsplit("-", 1)
            fn = {"hint": hint, "r23": r23, "fh": fh}.get(kind)
            if fn:
                out.append(f"{kind}:{SHORT.get(m, m)}={fn(d)}")
        if out:
            print(f"{lab:22} " + " ".join(out))
