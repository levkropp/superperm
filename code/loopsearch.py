"""Search LOOP SYSTEMS, not cut structures.

`notes/constructor.md` 10 measured why every cut-level move set fails at n = 6:

  * all 43,096 optima are distinct arc sets, and **no two differ by a single
    relocation** -- 43,096 connected components of size 1;
  * 100% of pairwise distances among the S = 25 optima are multiples of
    n-1 = 5, minimum 15; counted in LOOPS the minimum is 3;
  * `A = 0` forces every entered loop to be saturated (LOOP1), so an optimum's
    arc-start set is an exact union of whole 2-loops -- 409/409 measured.

So the state is a SET OF 2-LOOPS covering every rotation class, and the arc set
is a function of it.  That has three consequences worth stating, because they
make the search much better posed than the cut-level one:

    R = (n-1)v   exactly, so   S = (n-1)v - (n-1)! = (n-1)d

`S` is determined by `v` alone -- it is no longer something to search.  The
objective collapses to

    T = (n-1)d + comps + Y

so a loop system is judged purely on how few delta-components it has and how
cheaply they chain.  And the space is small: 144 loops at n = 6, of which a
covering system needs 24 (the exact cover) to ~29 (a champion).

Every class is met by exactly n loops, so coverage is a set-cover constraint
with n candidates per class.

Usage:
  python3 code/loopsearch.py                 # gate: reproduce known optima
  python3 code/loopsearch.py --iters 4000
"""

import argparse
import collections
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import chainer                                                    # noqa: E402
from build import coords, canonical, design_of, to_string         # noqa: E402
from gen2 import Gen                                              # noqa: E402
from inflate import arcs_from_starts                              # noqa: E402
from permgraph import is_superpermutation, string_to_path         # noqa: E402


def setup(n):
    g = Gen(n)
    st = g.st
    nl = len(st.loop_gens)
    cls_of = [frozenset(st.cls_id[x] for x in st.loop_gens[l]) for l in range(nl)]
    by_class = collections.defaultdict(list)
    for l, cs in enumerate(cls_of):
        for c in cs:
            by_class[c].append(l)
    return g, st, cls_of, by_class


def covers(cls_of, lids, nclass):
    seen = set()
    for l in lids:
        seen |= cls_of[l]
    return len(seen) == nclass


def arcs_of(st, n, lids):
    K = set()
    for l in lids:
        K.update(st.loop_gens[l])
    return arcs_from_starts(K, st, n)


def price(g, st, lids, mode="exact"):
    """(T, S, comps, Y) for a loop system.

    Three modes, and in loop space the middle one is the right default for the
    sweep.  Measured at n = 6, per move: `cheap` 1 ms, `bound` 225 ms, `exact`
    2.3 s -- and at the exact cover they read 24, 29 and 30 against the
    champion's 29.  So `cheap` is actively wrong here (it makes the exact cover
    look 5 BETTER than a champion, because with Y invisible the objective is
    just S + comps, which A3 says the exact cover minimises), `bound` ties them,
    and only `exact` separates them.  `bound` is the affordable one that is not
    misleading.
    """
    arcs = arcs_of(st, g.n, lids)
    S = len(arcs) - g.F1
    comps, ends = g.components(arcs)
    opts = g.options(arcs, comps, ends)
    if mode == "cheap":
        return S + len(comps) + chainer.cheap_bound(opts), S, len(comps), None
    if mode == "bound":
        return S + len(comps) + chainer.lower_bound(opts), S, len(comps), None
    Y, order, rots = chainer.solve(opts)
    return S + len(comps) + Y, S, len(comps), Y


def realise(g, st, lids):
    """Emit the actual superpermutation for a loop system."""
    arcs = arcs_of(st, g.n, lids)
    comps, ends = g.components(arcs)
    _, order, rots = chainer.solve(opts := g.options(arcs, comps, ends))
    des = canonical(g.design(arcs, comps, order, rots), g.n)
    s = to_string(des, g.n)
    return s, coords(des, g.n), is_superpermutation(s, g.n)


# ---------------------------------------------------------------------------
# moves: swap / add / drop a whole loop, keeping coverage
# ---------------------------------------------------------------------------

def neighbours(cls_of, by_class, lids, nclass, rng, k=1):
    """A random coverage-preserving move: swap, add, or drop one loop."""
    cur = set(lids)
    r = rng.random()
    if r < 0.55 and len(cur) > 1:                     # swap
        out = rng.choice(sorted(cur))
        cand = [l for l in range(len(cls_of)) if l not in cur]
        for _ in range(12):
            inn = rng.choice(cand)
            trial = (cur - {out}) | {inn}
            if covers(cls_of, trial, nclass):
                return frozenset(trial)
    elif r < 0.8:                                     # add
        cand = [l for l in range(len(cls_of)) if l not in cur]
        return frozenset(cur | {rng.choice(cand)})
    else:                                             # drop
        for _ in range(12):
            out = rng.choice(sorted(cur))
            trial = cur - {out}
            if trial and covers(cls_of, trial, nclass):
                return frozenset(trial)
    return None


def anneal(g, st, cls_of, by_class, lids, iters, rng, t0=2.0, t1=0.05, log=None):
    nclass = g.F1
    cur = frozenset(lids)
    curT = price(g, st, cur, mode="bound")[0]
    bestcheap = curT
    bestT, best = price(g, st, cur)[0], cur
    for it in range(iters):
        temp = t0 * (t1 / t0) ** (it / max(1, iters - 1))
        nxt = neighbours(cls_of, by_class, cur, nclass, rng)
        if nxt is None:
            continue
        newT = price(g, st, nxt, mode="bound")[0]
        if newT <= curT or rng.random() < math.exp((curT - newT) / temp):
            cur, curT = nxt, newT
            # tier 3 only when the cheap score reaches a new low; pricing every
            # accepted move exactly is far too slow to anneal against
            if curT <= bestcheap:
                bestcheap = curT
                t = price(g, st, cur)[0]
                if t < bestT:
                    bestT, best = t, cur
                    if log:
                        log(it, t, len(cur))
    return bestT, best


# ---------------------------------------------------------------------------

def gate(n=6):
    g, st, cls_of, by_class = setup(n)
    print(f"  {len(cls_of)} loops, {g.F1} classes, "
          f"each class met by {len(by_class[0])} loops")
    ok = True
    for tag, path, want in (("houston 872", "data/houston_872.txt", 29),):
        d = [int(c) for c in open(path).read() if c.isdigit()]
        des = design_of(string_to_path(d, n))
        lids = frozenset(st.loop_of[a[0]] for a in des)
        T, S, C, Y = price(g, st, lids)
        s, c, valid = realise(g, st, lids)
        good = T == want and c["length"] == 872 and valid
        ok &= good
        print(f"  {tag:<16} v={len(lids):<4} T={T} (S={S} comps={C} Y={Y})  "
              f"-> length {c['length']} valid={valid}  "
              f"{'OK' if good else 'MISMATCH'}")
    # the exact cover: one whole family
    fam = collections.defaultdict(list)
    for l in range(len(cls_of)):
        fam[st.fam_of_loop[l]].append(l)
    lids = frozenset(fam[0])
    T, S, C, Y = price(g, st, lids)
    good = T == 30
    ok &= good
    print(f"  {'exact cover':<16} v={len(lids):<4} T={T} (S={S} comps={C} Y={Y})"
          f"  {'OK' if good else 'MISMATCH'}")
    return ok, (g, st, cls_of, by_class)


def main(n, iters, seed):
    print("\n--- gate: known optima must price correctly in loop space ---")
    ok, (g, st, cls_of, by_class) = gate(n)
    if not ok:
        return 1
    if not iters:
        return 0
    rng = random.Random(seed)
    fam = collections.defaultdict(list)
    for l in range(len(cls_of)):
        fam[st.fam_of_loop[l]].append(l)
    start = frozenset(fam[0])
    print(f"\n--- annealing loop systems, {iters} iterations, "
          f"from the exact cover ---")

    def log(it, T, v):
        print(f"    it {it:>7}  T = {T}   v = {v}", flush=True)

    bestT, best = anneal(g, st, cls_of, by_class, start, iters, rng, log=log)
    s, c, valid = realise(g, st, best)
    print(f"\n  best T = {bestT}   v = {len(best)}   length = {len(s)}   "
          f"valid: {valid}")
    print("  coords: " + str({k: c[k] for k in
                              ("R", "S", "v", "d", "A", "B", "Y", "comps")}))
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=6)
    ap.add_argument("--iters", type=int, default=0)
    ap.add_argument("--seed", type=int, default=1)
    args = ap.parse_args()
    print(__doc__.split("Usage:")[0].strip())
    sys.exit(main(args.n, args.iters, args.seed))
