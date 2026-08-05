"""The A = 1 case at n = 6: enumerating the loop systems, and what they decide.

`A1EQ` says every walk with exactly one accident is an Egan string, so no
length-872 walk has A = 1.  This file builds the machinery to attack that.

THE STRUCTURE.  A = sum over entered loops of (n-1 - a_L), so A = 1 means
**v-1 loops are saturated** (every one of their n-1 generators is an arc start)
and exactly one loop contributes n-2.  With the Split Identity R = 5v - 1 and
T = S+B+Y = 29 (length 872), the case splits into exactly five:

    v      25    26    27    28    29
    S       4     9    14    19    24
    B+Y    25    20    15    10     5

THE REDUCTION.  The set K of arc starts determines the whole arc set -- the
arcs of a class are the segments between consecutive members of K in that
class -- so `comps(K)` is computable from the loop system alone, and
`B >= comps` makes `T >= S + comps` an ORDERING-FREE test.

(`B >= comps` is no longer a theorem: a weight-2 jump can land on `sigma^2(u)`
instead of `delta(u)`, which `comps` does not follow.  But `SIG2X` shows the
MINIMUM length is attained with no such jump, so the test remains valid against
the optimum -- which is all this file uses it for.  See `notes/ordering.md`.)

WHAT THIS FILE FOUND.  That test is **vacuous here**, and the file exists partly
to demonstrate it rather than assert it: `S + comps` equals v on optimal
systems and v <= 29 for every case in the table, so `S + comps <= 29` can never
be violated.  It is HPV in disguise, and HPV does not exclude these rungs.
Excluding A = 1 needs a lower bound on Y -- the same missing ingredient as
everything else in `lemma_arsenal.md` 11.

Usage:
  python3 code/a1.py --gate        # reproduce the 10,068 exact covers (A=0)
  python3 code/a1.py --v 25        # enumerate A=1 systems at v = 25
"""

import argparse
import collections
import itertools
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from build import comps as delta_comps                          # noqa: E402
from superstruct import Struct                                  # noqa: E402


def setup(n):
    """Loops as (generator tuple, class-id tuple), plus the class rings."""
    st = Struct(n)
    rings = {}
    for cid in range(st.n_classes):
        rings[cid] = []
    for p in st.perms:
        rings[st.cls_id[p]].append(p)
    # order each class ring by sigma so cut positions make sense
    for cid, ps in rings.items():
        start = min(ps)
        ring, x = [], start
        for _ in range(n):
            ring.append(x)
            x = st.sig(x)
        rings[cid] = ring
    loops = [tuple(gs) for gs in st.loop_gens]
    cls_of = [tuple(st.cls_id[g] for g in gs) for gs in loops]
    return st, loops, cls_of, rings


def design_from_K(K, st, rings, n):
    """Arc list implied by an arc-start set K (the cut structure)."""
    byc = collections.defaultdict(list)
    for g in K:
        byc[st.cls_id[g]].append(g)
    design = []
    for cid, gs in byc.items():
        ring = rings[cid]
        pos = sorted(ring.index(g) for g in gs)
        for i, k in enumerate(pos):
            nxt = pos[(i + 1) % len(pos)]
            ln = (nxt - k) % n or n
            design.append((ring[k], ln))
    return design


def systems(n, v, cls_of, deficiency, cap=200000):
    """Loop systems: v-`deficiency`-free loops, one contributing n-2 classes.

    `deficiency = 0` reproduces `saturated6.saturated`; `deficiency = 1` is the
    A = 1 shape.  Items are (loop id, omitted generator index or None).
    """
    NC = max(max(cs) for cs in cls_of) + 1
    per = n - 1
    slack = per * v - deficiency - NC          # = S
    items = []                                  # (mask, loop, omit)
    for lid, cs in enumerate(cls_of):
        items.append((sum(1 << c for c in cs), lid, None))
    defs = []
    if deficiency:
        for lid, cs in enumerate(cls_of):
            for j in range(per):
                m = sum(1 << c for k, c in enumerate(cs) if k != j)
                defs.append((m, lid, j))
    FULL = (1 << NC) - 1

    out = []
    used_loops = set()

    def rec(cov, chosen, excess, last, have_def):
        if len(out) >= cap:
            return
        if len(chosen) == v:
            if cov == FULL and have_def == bool(deficiency):
                out.append(tuple(chosen))
            return
        missing = NC - bin(cov).count("1")
        if missing > per * (v - len(chosen)):
            return
        low = (~cov) & FULL
        pool = items if have_def or not deficiency else items + defs
        if low:
            c = (low & -low).bit_length() - 1
            cand = [it for it in pool if it[0] >> c & 1]
        else:
            cand = [it for it in pool]
        for mask, lid, omit in cand:
            if lid in used_loops:
                continue
            if omit is not None and have_def:
                continue
            new = bin(mask & ~cov).count("1")
            size = per - (1 if omit is not None else 0)
            e = excess + (size - new)
            if e > slack:
                continue
            used_loops.add(lid)
            chosen.append((lid, omit))
            rec(cov | mask, chosen, e, lid, have_def or omit is not None)
            chosen.pop()
            used_loops.discard(lid)
            if len(out) >= cap:
                return

    rec(0, [], 0, -1, False)
    return out, slack


def score(system, n, st, loops, rings):
    """S, comps and the S1/S3 counters for one loop system."""
    K = []
    for lid, omit in system:
        gs = loops[lid]
        K += [g for j, g in enumerate(gs) if j != omit]
    design = design_from_K(K, st, rings, n)
    R = len(design)
    S = R - math.factorial(n - 1)
    c = delta_comps(design, n)
    lens = {a[0]: a[1] for a in design}
    allfull = sum(1 for lid, omit in system
                  if omit is None and all(lens[g] == n for g in loops[lid]))
    return dict(R=R, S=S, comps=c, allfull=allfull, v=len(system),
                score=S + c)


def run(v, deficiency, cap, n=6):
    st, loops, cls_of, rings = setup(n)
    sysm, slack = systems(n, v, cls_of, deficiency, cap)
    capped = len(sysm) >= cap
    print(f"  v={v} deficiency={deficiency}: S={slack}, {len(sysm)} systems"
          + ("  (CAPPED)" if capped else "  (complete)"))
    if not sysm:
        return None
    best, hist = None, collections.Counter()
    for s in sysm:
        sc = score(s, n, st, loops, rings)
        hist[sc["score"]] += 1
        if best is None or sc["score"] < best["score"]:
            best = sc
    lo = min(hist)
    print(f"    S + comps: min {lo}, max {max(hist)}   "
          f"(need > 29 to exclude length 872)")
    print(f"    best system: S={best['S']} comps={best['comps']} "
          f"allfull={best['allfull']} (S1: allfull <= comps "
          f"{'OK' if best['allfull'] <= best['comps'] else 'FAIL'})")
    if lo <= 29:
        print(f"    => test is VACUOUS at this v: S+comps = {lo} <= 29, so "
              f"HPV cannot exclude it")
    return lo


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--v", type=int, default=None)
    ap.add_argument("--gate", action="store_true")
    ap.add_argument("--cap", type=int, default=20000)
    args = ap.parse_args()
    print(__doc__.split("Usage:")[0].strip())

    if args.gate:
        print("\n--- gate: A = 0, v = 24 must give the 10,068 exact covers ---")
        st, loops, cls_of, rings = setup(6)
        sysm, slack = systems(6, 24, cls_of, 0, cap=200000)
        print(f"  {len(sysm)} systems, S={slack}   "
              f"{'MATCHES the published 10,068' if len(sysm) == 10068 else 'MISMATCH'}")
        assert len(sysm) == 10068, len(sysm)
        sc = score(sysm[0], 6, st, loops, rings)
        print(f"  first cover: S={sc['S']} comps={sc['comps']} "
              f"allfull={sc['allfull']} S+comps={sc['score']}")
    if args.v:
        print(f"\n--- A = 1 systems at v = {args.v} ---")
        run(args.v, 1, args.cap)
