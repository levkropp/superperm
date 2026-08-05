"""How much does a split actually buy?  Measuring dirty cheap jumps.

A cheap (weight-2) jump is CLEAN if it is delta out of a FULL arc.  A full arc
starting at u ends at u.c^(n-1), and delta sends that to u.a -- the next
generator of u's own 2-loop.  So a maximal run of arcs joined by clean jumps
(a CLEAN RUN) sits at consecutive generators of one loop and has at most n-1
arcs.  Every other cheap jump is DIRTY: it leaves a partial arc, and
u.c^(k-1).d for k < n is a generator of some unrelated loop.  Dirty jumps are
the free loop switches that splits pay for, and they are the reason every
elementary argument that works at S = 0 collapses at S > 0.

Two exact counts:

    #clean runs = B + dirty              (a block breaks at its dirty jumps)
    clean       = R - (B + dirty)

and one structural bound proved here by measurement: inside a single loop L
with a_L arc starts, the clean jumps used form a union of paths in the
(n-1)-cycle of generators, so

    clean jumps in L <= a_L - 1,   hence   clean <= R - v,   B + dirty >= v.

That last line is the whole difficulty in one place.  Since

    length = n + n! + (n-1)! - 3 + S + B + Y,

a bound  dirty <= S  would give  S + B >= v  and hence length >= base + v,
which is EXACTLY the Houston-Pantone-Vatter bound.  Anything better than HPV
by this route needs  dirty <= S - k.

This file measures dirty on every walk it can get its hands on.
"""

import math
import random
import sys
from itertools import permutations

sys.path.insert(0, "code")
from blockcount import Model                                   # noqa: E402


def dissect(m, path):
    """Arc/jump dissection with the clean-vs-dirty split."""
    n = m.n
    arcs, jumps = [[path[0]]], []
    for u, w in zip(path, path[1:]):
        wt = m.weight(u, w)
        if wt == 1:
            arcs[-1].append(w)
        else:
            jumps.append((u, w, wt))
            arcs.append([w])
    R = len(arcs)
    starts = [a[0] for a in arcs]
    B = 1 + sum(1 for _, _, wt in jumps if wt >= 3)
    Y = sum(wt - 3 for _, _, wt in jumps if wt >= 3)
    S = R - math.factorial(n - 1)

    clean = dirty = 0
    per_loop = {}
    for i, (u, w, wt) in enumerate(jumps):
        if wt != 2:
            continue
        if len(arcs[i]) == n and w == m.delta(u):
            clean += 1
            per_loop[m.loop_of[starts[i]]] = \
                per_loop.get(m.loop_of[starts[i]], 0) + 1
        else:
            dirty += 1

    entered = {m.loop_of[s] for s in starts}
    v = len(entered)
    a_L = {}
    for s in starts:
        a_L[m.loop_of[s]] = a_L.get(m.loop_of[s], 0) + 1

    # the per-loop clean bound
    for L, k in per_loop.items():
        assert k <= a_L[L] - 1, ("per-loop clean bound", L, k, a_L[L])
    assert clean <= R - v, "clean <= R - v"
    assert clean + dirty == R - B, "cheap jump count"

    P = sum(len(a) for a in arcs if len(a) < n)       # partial arcs
    n_partial = sum(1 for a in arcs if len(a) < n)
    assert dirty <= n_partial, "a dirty jump leaves a partial arc"

    # ---- clean runs, and the per-loop run partition ------------------------
    # Every arc start is a generator of exactly one 2-loop; pos[] is its index
    # along that loop, so g.a sits at pos+1 (mod n-1).
    pos = {}
    for lid, gs in enumerate(m.loop_gens):
        for i, g in enumerate(gs):
            pos[g] = i
    runs, cur = [], [0]
    for i, (u, w, wt) in enumerate(jumps):
        if wt == 2 and len(arcs[i]) == n and w == m.delta(u):
            cur.append(i + 1)
        else:
            runs.append(cur)
            cur = [i + 1]
    runs.append(cur)
    N = len(runs)

    r_L = {}
    for run in runs:
        lids = {m.loop_of[starts[i]] for i in run}
        assert len(lids) == 1, "a clean run lives inside one 2-loop"
        lid = lids.pop()
        r_L[lid] = r_L.get(lid, 0) + 1
        ps = [pos[starts[i]] for i in run]
        for x, y in zip(ps, ps[1:]):
            assert y == (x + 1) % (n - 1), "clean run = consecutive generators"
        assert len(run) <= n - 1, "a clean run has at most n-1 arcs"
        for i in run[:-1]:
            assert len(arcs[i]) == n, "interior arcs of a clean run are full"

    assert N == B + dirty, "N = B + dirty"
    assert N == sum(r_L.values()), "N = sum of per-loop run counts"
    assert sum(a_L.values()) == R and max(a_L.values()) <= n - 1
    # a run of length n-1 IS a loop with all its arc starts in one run
    f_runs = sum(1 for run in runs if len(run) == n - 1)
    f_loops = sum(1 for L in a_L if a_L[L] == n - 1 and r_L[L] == 1)
    assert f_runs == f_loops, ("complete traversals are loops",
                               f_runs, f_loops)
    A_all = (n - 1) * v - R
    assert A_all >= 0, "accidents are non-negative"

    length = n + sum(m.weight(u, w) for u, w in zip(path, path[1:]))
    base = n + math.factorial(n) + math.factorial(n - 1) - 3
    assert length == base + S + B + Y
    return dict(n=n, length=length, R=R, S=S, v=v, B=B, Y=Y,
                clean=clean, dirty=dirty, n_partial=n_partial,
                SBY=S + B + Y, hpv_slack=S + B + Y - v,
                dirty_minus_S=dirty - S, N=N, f=f_runs, A=A_all,
                Nmv=N - v, maxr=max(r_L.values()))


HDR = ("length", "R", "S", "v", "A", "B", "Y", "SBY", "clean", "dirty",
       "n_partial", "N", "f", "Nmv", "hpv_slack")


def show(name, d):
    print(f"{name:20}" + "".join(f"{k}={d[k]:<7}" for k in HDR))


if __name__ == "__main__":
    from permgraph import string_to_path
    from classical import recursive_superperm

    print(__doc__.split("This file")[0].strip())
    print("\n" + "=" * 118)
    worst = []
    for n in (4, 5, 6):
        m = Model(n)
        d = dissect(m, string_to_path(recursive_superperm(n), n))
        show(f"classical {n}", d)
        worst.append(d)
        if n == 6:
            h = [int(c) for c in open("data/houston_872.txt").read().strip()]
            d = dissect(m, string_to_path(h, 6))
            show("Houston 872", d)
            worst.append(d)

    # ---- stress: random and greedy complete walks at n = 5 and n = 6 ------
    print("\n--- stress: is  dirty <= S  a law? ---")
    random.seed(11)
    for n in (5, 6):
        m = Model(n)
        allp = m.perms
        rows = []
        for t in range(120 if n == 5 else 30):
            if t % 3 == 0:
                p = allp[:]
                random.shuffle(p)
            else:
                rest = set(allp)
                u = random.choice(allp)
                rest.discard(u)
                p = [u]
                while rest:
                    lo = min(m.weight(u, w) for w in rest)
                    cands = [w for w in rest if m.weight(u, w) <= lo + (t % 3)]
                    u = random.choice(cands)
                    rest.discard(u)
                    p.append(u)
            rows.append(dissect(m, p))
        bad = [r for r in rows if r['dirty'] > r['S']]
        mx = max(r['dirty_minus_S'] for r in rows)
        mn = min(r['hpv_slack'] for r in rows)
        print(f"  n={n}  {len(rows)} walks: max(dirty - S) = {mx:>4}, "
              f"violations of dirty <= S: {len(bad):>3}, "
              f"min HPV slack (S+B+Y-v) = {mn}")
        worst += rows

    print("\n  over everything measured: "
          f"max(dirty - S) = {max(r['dirty_minus_S'] for r in worst)}, "
          f"min(S+B+Y - v) = {min(r['hpv_slack'] for r in worst)}")
