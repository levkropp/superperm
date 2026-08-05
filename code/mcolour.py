"""Multi-colouring search: construct walks by choosing cuts, then ordering arcs.

THE REFORMULATION.  `lemma_arsenal.md` 3.3 observes that a SPLIT-FREE walk is
an n-colouring of the (n-1)! rotation classes.  The general case has never been
written down.  Here it is.

A rotation class C is a cyclic sequence of n permutations.  A walk covers C
with mu_C >= 1 contiguous arcs, i.e. it chooses a nonempty set of CUT POSITIONS

    chi(C)  subset of  Z_n,     mu_C = |chi(C)|,     S = sum (mu_C - 1),

each cut being an arc start.  By 3.4 the arcs of one class lie in pairwise
distinct families, so chi is a genuine set-valued colouring; |chi(C)| = 1 is
the split-free case and recovers 3.3 exactly.

THE COST COLLAPSES.  With T = S + B + Y, B = 1 + #{w >= 3} and Y = sum(w-3):

    T  =  S  +  1  +  sum over consecutive arcs of  f(w),   f(w) = max(0, w-2)

because a weight-2 jump is free, a weight-3 jump costs 1 (a block) and a
weight-w jump costs 1 + (w-3) = w-2.  So once the cuts are fixed the problem is
an ASYMMETRIC TSP on the arcs with cost f(weight(end_u, start_v)), and the
whole objective is `S + 1 + tour cost`.

That is the point of the arc representation: the tour is over R ~ (n-1)! nodes,
not n!.  At n = 6 that is 120 nodes, at n = 7 720, at n = 8 5040 -- against
720 / 5040 / 40320 for the permutation graph.

SEARCH.  Simulated annealing over both levels: Or-opt segment moves on the
order (2-opt is invalid here, the graph is asymmetric), plus split / merge /
shift moves on chi.  Validity is automatic -- any chi with every class nonempty
gives arcs partitioning all n! permutations.

GATE.  Must reach T = 29 at n = 6, the true optimum (s(6) = 872 = 843 + 29).

Usage:
  python3 code/mcolour.py --n 6 --iters 400000
  python3 code/mcolour.py --n 6 --seed-from data/houston_872.txt   # perturb a champion
"""

import argparse
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from build import canonical, coords, design_of, to_string        # noqa: E402
from permgraph import is_superpermutation, string_to_path, weight  # noqa: E402
from superstruct import Struct                                   # noqa: E402


def f(w):
    """Cost of a jump of weight w, in units of T."""
    return w - 2 if w > 2 else 0


class Problem:
    def __init__(self, n):
        self.n = n
        self.st = Struct(n)
        # class id -> the n permutations in sigma order, starting at the
        # canonical representative
        self.cls = []
        seen = set()
        for p in self.st.perms:
            c = self.st.onecycle(p)
            if c in seen:
                continue
            seen.add(c)
            ring, x = [], c
            for _ in range(n):
                ring.append(x)
                x = self.st.sig(x)
            self.cls.append(ring)
        assert len(self.cls) == math.factorial(n - 1)

    # ---- chi -> arcs ---------------------------------------------------

    def arcs_of(self, chi):
        """[(start, length)] for the whole walk, unordered."""
        out = []
        for cid, cuts in enumerate(chi):
            ring, ks = self.cls[cid], sorted(cuts)
            for i, k in enumerate(ks):
                nxt = ks[(i + 1) % len(ks)]
                ln = (nxt - k) % self.n or self.n
                out.append((ring[k], ln))
        return out

    def end_of_arc(self, arc):
        x = arc[0]
        for _ in range(arc[1] - 1):
            x = self.st.sig(x)
        return x

    # ---- objective -----------------------------------------------------

    def tour_cost(self, order, ends, starts):
        return sum(f(weight(ends[order[i]], starts[order[i + 1]]))
                   for i in range(len(order) - 1))

    def T_of(self, chi, order, ends, starts):
        S = sum(len(c) for c in chi) - len(chi)
        return S + 1 + self.tour_cost(order, ends, starts)

    def family_chi(self, fam):
        """Monochromatic colouring: every arc start taken from one family.

        A family is an exact cover of the classes (3.3), so this is well
        defined and gives exactly one full arc per class -- the split-free
        complete-traversal seed, B = (n-2)!.
        """
        pos = {}
        for cid, ring in enumerate(self.cls):
            for k, q in enumerate(ring):
                pos[q] = (cid, k)
        chi = [set() for _ in self.cls]
        for g, fm in self.st.fam_of_perm.items():
            if fm == fam:
                cid, k = pos[g]
                chi[cid].add(k)
        assert all(len(c) == 1 for c in chi), "family is an exact cover"
        return chi


def arc_end(st, arc):
    x = arc[0]
    for _ in range(arc[1] - 1):
        x = st.sig(x)
    return x


class Walk:
    """State = an ORDERED list of arcs partitioning all n! permutations.

    chi is implicit: the arcs of a class are its cuts.  Keeping the order as
    the primary object (rather than chi plus a separate permutation of arc
    indices) means a split/merge move can splice locally instead of rebuilding
    and destroying the annealed order -- which is what stalled the first
    version at the split-free optimum.
    """

    def __init__(self, p, arcs):
        self.p, self.st = p, p.st
        self.order = list(arcs)
        self.end = {a: arc_end(p.st, a) for a in self.order}
        self.F1 = math.factorial(p.n - 1)

    def e(self, u, v):
        return f(weight(self.end[u], v[0]))

    def cost(self):
        o = self.order
        return sum(self.e(o[i], o[i + 1]) for i in range(len(o) - 1))

    def T(self):
        return (len(self.order) - self.F1) + 1 + self.cost()

    def delta_remove(self, i, ln):
        o = self.order
        seg = o[i:i + ln]
        a0 = o[i - 1] if i > 0 else None
        a1 = o[i + ln] if i + ln < len(o) else None
        d = 0
        if a0 is not None:
            d -= self.e(a0, seg[0])
        if a1 is not None:
            d -= self.e(seg[-1], a1)
        if a0 is not None and a1 is not None:
            d += self.e(a0, a1)
        return d

    def delta_insert(self, rest, j, seg):
        b0 = rest[j - 1] if j > 0 else None
        b1 = rest[j] if j < len(rest) else None
        d = 0
        if b0 is not None:
            d += self.e(b0, seg[0])
        if b1 is not None:
            d += self.e(seg[-1], b1)
        if b0 is not None and b1 is not None:
            d -= self.e(b0, b1)
        return d

    def best_insert(self, rest, seg, rng, sample=None):
        """Cheapest insertion point for seg, scanning (a sample of) positions."""
        idxs = range(len(rest) + 1)
        if sample and len(rest) > sample:
            idxs = rng.sample(range(len(rest) + 1), sample)
        bj, bd = None, None
        for j in idxs:
            d = self.delta_insert(rest, j, seg)
            if bd is None or d < bd:
                bj, bd = j, d
                if bd == 0:
                    break
        return bj, bd


def greedy_order(p, arcs):
    """Nearest-neighbour seed under f."""
    starts = [a[0] for a in arcs]
    ends = [p.end_of_arc(a) for a in arcs]
    m = len(arcs)
    unused = set(range(m))
    cur = 0
    unused.discard(0)
    order = [0]
    while unused:
        best, bc = None, None
        for j in unused:
            c = f(weight(ends[cur], starts[j]))
            if bc is None or c < bc:
                best, bc = j, c
                if bc == 0:
                    break
        order.append(best)
        unused.discard(best)
        cur = best
    return [arcs[i] for i in order]


def search(p, arcs, iters, t0=1.5, t1=0.02, rng=None, log=None, sample=64):
    rng = rng or random.Random(0)
    n, st = p.n, p.st
    w = Walk(p, greedy_order(p, arcs))
    cur = w.T()
    best, best_order = cur, list(w.order)

    for it in range(iters):
        temp = t0 * (t1 / t0) ** (it / max(1, iters - 1))
        m = len(w.order)
        r = rng.random()

        if r < 0.7:                       # ---- Or-opt on the order --------
            if m < 6:
                continue
            ln = rng.randint(1, 3)
            i = rng.randrange(0, m - ln)
            seg = w.order[i:i + ln]
            d1 = w.delta_remove(i, ln)
            rest = w.order[:i] + w.order[i + ln:]
            j = rng.randrange(0, len(rest) + 1)
            d2 = w.delta_insert(rest, j, seg)
            d = d1 + d2
            if d <= 0 or rng.random() < math.exp(-d / temp):
                w.order = rest[:j] + seg + rest[j:]
                cur += d

        elif r < 0.85:                    # ---- split an arc ---------------
            i = rng.randrange(m)
            a = w.order[i]
            if a[1] < 2:
                continue
            k = rng.randrange(1, a[1])
            left = (a[0], k)
            right = (arc_end(st, (a[0], k + 1)), a[1] - k)
            w.end.setdefault(left, arc_end(st, left))
            w.end.setdefault(right, arc_end(st, right))
            d1 = w.delta_remove(i, 1)
            rest = w.order[:i] + w.order[i + 1:]
            j0, d2 = w.best_insert(rest, [left], rng, sample)
            rest2 = rest[:j0] + [left] + rest[j0:]
            j1, d3 = w.best_insert(rest2, [right], rng, sample)
            d = d1 + d2 + d3 + 1          # +1: S goes up by one
            if d <= 0 or rng.random() < math.exp(-d / temp):
                w.order = rest2[:j1] + [right] + rest2[j1:]
                cur += d

        else:                             # ---- merge two arcs of a class --
            i = rng.randrange(m)
            a = w.order[i]
            tgt = st.sig(w.end[a])        # the arc continuing a's class
            k = next((x for x, b in enumerate(w.order) if b[0] == tgt), None)
            if k is None or k == i or a[1] + w.order[k][1] > n:
                continue
            merged = (a[0], a[1] + w.order[k][1])
            w.end.setdefault(merged, arc_end(st, merged))
            drop = {i, k}
            rest = [b for x, b in enumerate(w.order) if x not in drop]
            j, _ = w.best_insert(rest, [merged], rng, sample)
            saved, w.order = w.order, rest[:j] + [merged] + rest[j:]
            newT = w.T()                  # merges are rare; full rescore is fine
            d = newT - cur
            if d <= 0 or rng.random() < math.exp(-d / temp):
                cur = newT
            else:
                w.order = saved

        if cur < best:
            best, best_order = cur, list(w.order)
            if log:
                log(it, best)
    return best, best_order


def seed_arcs(p, rng, seed_from=None, seed_family=None):
    """Initial arc set: from a known string, from one family, or random."""
    if seed_from:
        digits = [int(c) for c in open(seed_from).read() if c.isdigit()]
        arcs = design_of(string_to_path(digits, p.n))
        print(f"  seeded from {seed_from}: R = {len(arcs)}, "
              f"S = {len(arcs) - math.factorial(p.n - 1)}")
        return arcs
    if seed_family is not None:
        chi = p.family_chi(seed_family)
        print(f"  seeded monochromatic from family {seed_family} "
              f"(split-free, one full arc per class)")
        return p.arcs_of(chi)
    print("  seeded from a random split-free colouring")
    return p.arcs_of([{rng.randrange(p.n)} for _ in p.cls])


def run(n, iters, seed, seed_from=None, seed_family=None, quiet=False):
    p = Problem(n)
    rng = random.Random(seed)
    arcs = seed_arcs(p, rng, seed_from, seed_family)

    def log(it, T):
        if not quiet:
            print(f"    it {it:>9}  T = {T}", flush=True)

    T, design = search(p, arcs, iters, rng=rng, log=log)
    design = canonical(design, n)     # merge accidental sigma-successions
    c = coords(design, n)
    T = c["T"]                        # canonicalisation can only lower T
    s = to_string(design, n)
    valid = is_superpermutation(s, n)
    assert len(s) == n + math.factorial(n) + math.factorial(n - 1) - 3 + T
    print(f"\n  best T = {T}   length = {len(s)}   "
          f"valid superpermutation: {valid}")
    print(f"  coords: {({k: c[k] for k in ('R','S','v','d','A','B','Y','T')})}")
    return T, design, s, valid


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=6)
    ap.add_argument("--iters", type=int, default=200000)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--seed-from", default=None)
    ap.add_argument("--family", type=int, default=None,
                    help="seed monochromatic from this family (0..n-1)")
    args = ap.parse_args()
    print(__doc__.split("Usage:")[0].strip())
    print(f"\n--- n = {args.n}, {args.iters} iterations ---")
    run(args.n, args.iters, args.seed, args.seed_from, args.family)
