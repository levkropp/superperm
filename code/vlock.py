"""Is the thin-loop lock universal, or a property of one champion?

`VLOCK` says the n = 7 5906 champion cannot lower `v` by re-cutting: the only
free generator slots in the whole arc set belong to its four thin loops, and
those four are pairwise class-disjoint, so no class of one thin loop has a
rotation sitting in another's free slot.  Since `CH3 = v + p - 1` wherever `A2`
is tight, and 5905 needs `v + p <= 142` against the champion's 143, the target
is `v = 141` -- and `VLOCK` says it is unreachable from here at ANY move width.

That was measured on ONE string.  The census holds 237 n = 7 champions, and if
the lock is a property of the point rather than of length-5906 walks in general,
then some other champion is a better place to start a search.  So test it on
every one of them.

The argument, restated as the three things this file measures:

  (1) which entered loops have a free slot at all -- `a_L < n-1`;
  (2) whether those thin loops are pairwise CLASS-DISJOINT;
  (3) for each thin loop `L`, whether any class with an arc start in `L` has
      another rotation lying in a free slot of a DIFFERENT entered loop.

Moving a start into an UNENTERED loop is not an escape: it raises `v` by one
exactly as vacating `L` lowered it.  So (3) is the whole move set, and 0
usable alternatives means `v` cannot fall.

Usage:
  python3 code/vlock.py            # every n = 7 census string
  python3 code/vlock.py --n 6      # the n = 6 control
"""

import argparse
import collections
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from build import design_of                                       # noqa: E402
from gen2 import Gen                                              # noqa: E402
from permgraph import string_to_path                              # noqa: E402


def lock(g, arcs):
    """(v, thin sizes, pairwise-disjoint?, usable alternatives)."""
    st = g.st
    starts = {a[0] for a in arcs}
    per = collections.defaultdict(set)
    for (s, ln) in arcs:
        per[st.loop_of[s]].add(s)
    v = len(per)
    thin = {L: gs for L, gs in per.items() if len(gs) < g.n - 1}
    # free slots: generators of an ENTERED loop that are not arc starts
    free = collections.defaultdict(set)
    for L, gs in per.items():
        for x in st.loop_gens[L]:
            if x not in starts:
                free[L].add(x)
    # (2) are the thin loops pairwise class-disjoint?
    cls = {L: {st.cls_id[x] for x in st.loop_gens[L]} for L in thin}
    disjoint = all(not (cls[L] & cls[M])
                   for L in thin for M in thin if L < M)
    # (3) can any thin loop be vacated?  A start may only move to a free slot
    # of another ENTERED loop; landing in an unentered loop just moves v back.
    usable = 0
    vacatable = []
    for L, gs in thin.items():
        movable = 0
        for x in gs:
            c = st.cls_id[x]
            alts = 0
            for y in st.perms:
                if st.cls_id[y] != c or y == x:
                    continue
                M = st.loop_of[y]
                if M != L and y in free.get(M, ()):
                    alts += 1
            usable += alts
            movable += alts > 0
        # vacating L needs EVERY one of its starts to have somewhere to go
        vacatable.append((L, movable, len(gs)))
    return (v, sorted(len(gs) for gs in thin.values()), disjoint, usable,
            vacatable)


def main(n):
    import census
    g = Gen(n)
    rows = []
    for _n, label, path in census.sources(9):
        if _n != n:
            continue
        for digits in census.read_strings(path):
            if not digits or max(digits) != n or min(digits) != 1:
                continue
            p_ = string_to_path(digits, n)
            if len(p_) != math.factorial(n):
                continue
            T = len(digits) - (n + math.factorial(n)
                               + math.factorial(n - 1) - 3)
            rows.append((label, T) + lock(g, [tuple(a)
                                             for a in design_of(p_)]))
    print(f"\n  {len(rows)} strings at n = {n}")
    byT = collections.defaultdict(list)
    for r in rows:
        byT[r[1]].append(r)
    for T in sorted(byT):
        rs = byT[T]
        vs = collections.Counter(r[2] for r in rs)
        thins = collections.Counter(tuple(r[3]) for r in rs)
        dis = sum(1 for r in rs if r[4])
        stuck = sum(1 for r in rs if r[5] == 0)
        alts = collections.Counter(r[5] for r in rs)
        print(f"\n  T = {T}   ({len(rs)} strings)   v = {dict(vs)}")
        print(f"    thin-loop size multisets: "
              f"{dict(list(thins.items())[:4])}"
              f"{' ...' if len(thins) > 4 else ''}")
        print(f"    thin loops pairwise class-disjoint: {dis}/{len(rs)}")
        print(f"    usable alternatives (0 = v cannot fall): {dict(alts)}")
        print(f"    LOCKED by having no alternative at all: {stuck}/{len(rs)}")
        # the necessary condition: SOME thin loop has every start movable
        full = [r for r in rs
                if any(mv == tot for _, mv, tot in r[6])]
        gaps = collections.Counter(
            max((mv - tot for _, mv, tot in r[6]), default=None)
            for r in rs if r[5] > 0)
        print(f"    of the {len(rs) - stuck} unlocked: best (movable - needed) "
              f"per string = {dict(gaps)}")
        print(f"    strings where some thin loop is FULLY movable: {len(full)}")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=7)
    args = ap.parse_args()
    print(__doc__.split("Usage:")[0].strip())
    sys.exit(main(args.n))
