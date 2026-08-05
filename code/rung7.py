"""The n = 7 v = 121 rung, exhausted over the cover-plus-one-loop family.

`RUNG1` (notes/pbound.md 5d) closed `v = (n-2)!+1` by exhausting the arc sets
with `A = 0` -- at that rung every `A = 0` arc set is an exact cover plus one
whole loop, 720 of them, all giving `CH3 = 146`.  Its caveat was explicit:

    "this is A = 0 only.  At this rung S = n-1-A >= 0 allows A <= n-1, and
     those are untested."

This file removes that caveat over the same family.  Adding only SOME of a fresh
loop's `n-1` generators gives `S = k` and `A = (n-1) - k`, so sweeping every
nonempty subset of every fresh loop sweeps every `A` from 0 to `n-2`:

    720 fresh loops  x  63 nonempty generator subsets  =  45,360 arc sets
    per base cover, and every one is priced.

WHAT IS AND IS NOT EXHAUSTED.  This is exhaustive over *cover + one partial
fresh loop*.  It is NOT exhaustive over all `v = 121` arc sets: for `A > 0` the
entered loops need not contain an exact cover at all, and nothing here rules
that out.  `RUNG1`'s own claim that "every A = 0 arc set is a cover plus one
loop" applies only at `A = 0`.  The result is stated at that scope.

SOUNDNESS.  `p` is the packing floor (`bound_only=True`), which is a valid LOWER
bound on `p`, so `S + comps + p - 1` is a valid lower bound on `CH3` and hence
on `T`.  Understating `p` can only understate the bound, so a MINIMUM computed
this way is safe to conclude from -- the opposite direction to the fallback that
manufactured the spurious "140" of notes/pbound.md 3.

Usage:
  python3 code/rung7.py                # every base cover on disk
  python3 code/rung7.py --limit 60     # quick smoke test
"""

import argparse
import collections
import math
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pbound                                                     # noqa: E402
from build import design_of                                       # noqa: E402
from gen2 import Gen, chi_from_string                             # noqa: E402
from permgraph import string_to_path                              # noqa: E402

TARGET = 142          # a 5905 needs T = 141, so CH3 >= 142 excludes it


def base_covers(g, n):
    """Every exact-cover arc set on disk, as a cut system."""
    import census
    out = []
    for _n, label, path in census.sources(9):
        if _n != n:
            continue
        for d in census.read_strings(path):
            if not d or max(d) != n or min(d) != 1:
                continue
            p_ = string_to_path(d, n)
            if len(p_) != math.factorial(n):
                continue
            if len(design_of(p_)) != math.factorial(n - 1):
                continue
            out.append((label, chi_from_string(g, p_)))
    return out


def sweep(g, n, chi0, limit=None):
    """Price cover + every nonempty generator subset of every fresh loop."""
    st = g.st
    entered = {st.loop_of[a[0]] for a in g.arcs_of(chi0)}
    fresh = [L for L in range(st.n_loops) if L not in entered]
    if limit:
        fresh = fresh[:limit]
    ring_ix = {}
    lo, hist, seen = (10**9, None), collections.Counter(), 0
    for L in fresh:
        gens = st.loop_gens[L]
        pos = []
        for x in gens:
            c = st.cls_id[x]
            if (c, x) not in ring_ix:
                ring_ix[(c, x)] = g.rings[c].index(x)
            pos.append((c, ring_ix[(c, x)]))
        for mask in range(1, 1 << (n - 1)):
            chi = [set(c) for c in chi0]
            ok = True
            for i in range(n - 1):
                if not (mask >> i) & 1:
                    continue
                c, r = pos[i]
                if r in chi[c]:
                    ok = False
                    break
                chi[c].add(r)
            if not ok:
                continue
            arcs = g.arcs_of(chi)
            v = len({st.loop_of[a[0]] for a in arcs})
            if v != math.factorial(n - 2) + 1:
                continue
            b, S, C, p = pbound.value(g, arcs, bound_only=True)
            A = (n - 1) * v - len(arcs)
            seen += 1
            hist[b] += 1
            if b < lo[0]:
                lo = (b, (S, C, p, A, L, mask))
    return seen, hist, lo


def main(n, limit):
    g = Gen(n)
    covers = base_covers(g, n)
    print(f"\n  {len(covers)} exact-cover base(s) on disk at n = {n}")
    worst = (10**9, None, None)
    for label, chi0 in covers:
        t0 = time.time()
        seen, hist, lo = sweep(g, n, chi0, limit)
        print(f"\n  base {label}")
        print(f"    {seen} arc sets at v = {math.factorial(n-2)+1}, "
              f"{time.time() - t0:.0f}s")
        print(f"    CH3 floor histogram: {dict(sorted(hist.items()))}")
        print(f"    MINIMUM = {lo[0]}   (S,comps,p,A,loop,mask) = {lo[1]}")
        if lo[0] < worst[0]:
            worst = (lo[0], label, lo[1])
    print(f"\n  worst over all bases: CH3 >= {worst[0]}  at {worst[1]}")
    if worst[0] >= TARGET:
        print(f"  >= {TARGET}: no 5905 in the cover-plus-one-loop family at "
              f"this rung, for ANY A")
        return 0
    print(f"  BELOW {TARGET} -- this family is not excluded")
    return 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=7)
    ap.add_argument("--limit", type=int)
    args = ap.parse_args()
    print(__doc__.split("Usage:")[0].strip())
    sys.exit(main(args.n, args.limit))
