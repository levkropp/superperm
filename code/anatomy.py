"""Coordinate anatomy of the optimum families, per n.

The question this file exists to answer: **what does 5906 do that no other
optimum does?**  Every optimum measured anywhere sits exactly on the Egan-1
line `v + Y = (n-1)(n-3)! - 1` except 5906, which is one below it.

The first thing to look at is the shape of each family in coordinate space.
They turn out to move along *different axes*:

    n = 6   three vectors, a line in Y/d,  A = 0 throughout
    n = 7   a line in A,   d = 22 and Y = 0 fixed,  B = 10 + A,  S = 132 - A
    n = 8   one vector,    A = 0

The n=7 line is one split traded for one block per unit of A -- exactly the
stitch/split exchange that `notes/a_cost_law.md` describes.

Usage:
  python3 code/anatomy.py
"""

import collections
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

BEST = {5: 153, 6: 872, 7: 5906, 8: 46204, 9: 408966}
SOURCES = ["data/census.json", "data/champions6.json"]


def load():
    rows = []
    for p in SOURCES:
        if os.path.exists(p):
            rows += json.load(open(p))
    return rows


def egan_line(n):
    return (n - 1) * math.factorial(n - 3) - 1


def families(rows):
    print("\n--- optimum families in (d, A, S, B, Y) ---")
    for n in sorted({r["n"] for r in rows}):
        opt = [r for r in rows if r["n"] == n and r["length"] == BEST.get(n)]
        if not opt:
            continue
        h = collections.Counter((r["d"], r["A"], r["S"], r["B"], r["Y"])
                                for r in opt)
        print(f"\n  n = {n}:  {len(opt)} optima of length {BEST[n]}, "
              f"{len(h)} distinct vectors")
        print(f"    {'d':>5} {'A':>5} {'S':>6} {'B':>5} {'Y':>4} "
              f"{'v+Y':>7} {'line':>7}   count")
        for key, cnt in sorted(h.items()):
            d, A, S, B, Y = key
            v = d + math.factorial(n - 2)
            mark = "" if v + Y >= egan_line(n) else "   <== PAST THE LINE"
            print(f"    {d:>5} {A:>5} {S:>6} {B:>5} {Y:>4} {v+Y:>7} "
                  f"{egan_line(n):>7}   {cnt}{mark}")
        # which coordinate actually varies?
        varying = [k for k, i in (("d", 0), ("A", 1), ("S", 2), ("B", 3),
                                  ("Y", 4))
                   if len({key[i] for key in h}) > 1]
        print(f"    axis: {', '.join(varying) if varying else 'single point'}")


def mod_gap(rows):
    """The A-values realised at n = 7, and the missing residues."""
    print("\n--- the A-spectrum at each n ---")
    for n in sorted({r["n"] for r in rows}):
        opt = [r for r in rows if r["n"] == n and r["length"] == BEST.get(n)]
        if not opt:
            continue
        As = sorted({r["A"] for r in opt})
        if len(As) < 2:
            print(f"  n = {n}: A = {As}")
            continue
        full = list(range(min(As), max(As) + 1))
        missing = [a for a in full if a not in As]
        print(f"  n = {n}: A in {As}")
        print(f"           missing inside the range: {missing or 'none'}")
        if missing:
            mods = {a % (n - 3) for a in missing}
            present = {a % (n - 3) for a in As}
            print(f"           missing residues mod (n-3)={n-3}: {sorted(mods)}"
                  f"   present: {sorted(present)}"
                  + ("   -> A never hits that residue"
                     if not (mods & present) else "   -> no clean residue rule"))


def line_check(rows):
    print("\n--- the Egan-1 line, over every measured string ---")
    for n in sorted({r["n"] for r in rows}):
        sub = [r for r in rows if r["n"] == n]
        below = [r for r in sub if r["v"] + r["Y"] < egan_line(n)]
        opt = [r for r in sub if r["length"] == BEST.get(n)]
        obelow = [r for r in opt if r["v"] + r["Y"] < egan_line(n)]
        print(f"  n = {n}: {len(sub):>6} strings, {len(below):>5} below the "
              f"line; of the {len(opt)} optima, {len(obelow)} below")


if __name__ == "__main__":
    print(__doc__.split("Usage:")[0].strip())
    rows = load()
    print(f"\n  loaded {len(rows)} measured strings")
    families(rows)
    mod_gap(rows)
    line_check(rows)
