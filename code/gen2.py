"""Two-level generator: search arc sets, get the ordering almost for free.

WHY REBUILD.  `mcolour.py` anneals the ORDER of ~850 arcs with Or-opt moves and
stalls at the split-free optimum (T = 30 at n = 6, against the true 29).  That
effort is largely wasted, because the corpus says the ordering is nearly
determined by the arc set:

    B = comps  on 44,370 / 44,370 optima          (claim C6b)

i.e. an optimum uses EVERY free delta-edge available to it.  So the blocks are
not something to search for -- they are the delta-components of the arc set,
computable directly.

THE SPLIT.

    outer   search the arc set K (equivalently the cut structure chi), which
            fixes S and the delta-components;
    inner   chain those components into one walk.

The inner problem is tiny.  At champion parameters the component count IS B:
**4 at n = 6, 6 at n = 8, 18 at n = 7** -- an exact TSP on ~20 nodes rather
than a heuristic over ~850.  So it is solved exactly (Held-Karp) whenever it is
small enough, and greedily otherwise (those states are bad anyway).

    T = S + comps + Y,      Y = sum over the comps-1 chaining jumps of (w-3)

Inter-component jumps automatically have w >= 3: if a free (w <= 2) edge existed
between two components they would be one component.

CYCLE BREAK POINTS MATTER.  A cycle component can be broken at any of its
places, and the choice is not cosmetic: breaking the n = 6 champion's cycles
canonically costs Y = 9 where the right break costs 0.  So the inner problem is
a generalized TSP over (component, break-point) states, solved exactly by
Held-Karp when small enough.

WHERE IT STANDS.  Seeded at a champion it reproduces it exactly (T = 29,
length 872, S=25 v=29 A=0 B=4 Y=0 comps=4), so the architecture and the pricing
are right.  Cold-start it does NOT reach 29 -- and the reason is structural, not
a tuning failure:

  * every ORDERING-FREE objective is minimised by the exact cover
    (`min (S + comps) = (n-2)!`, notes/second_order.md A3 -- and `T >= S+comps`
    is valid against the optimum, notes/ordering.md 3a);
  * adding the admissible chain bound `Y >= ceil(comps/(n-2)) - 1` scores the
    exact cover at 0 + 24 + 5 = 29 at n = 6 -- exactly the true optimum -- so
    the search sees no gradient away from it;
  * the gradient toward champions lives only in the EXACT Y, which costs ~1.4 s
    per evaluation at comps = 24 and cannot be annealed against.

That is the same wall as A3 in a new guise: no ordering-free invariant beats
HPV, and none can steer a search off the exact cover either.  Closing it needs
a fast exact chainer, not a better annealer.

KNOWN GAP.  The inner chainer is exact (Held-Karp over (component, break-point)
states) only while `comps <= 12` and the state count stays under CHOICE_LIMIT.
That covers the CHAMPION regime -- comps is 4 at n = 6, 6 at n = 8, 18 at n = 7
-- but not the exact-cover seed, where comps = (n-2)! = 24 at n = 6.  There the
heuristic returns Y = 14 against a true optimum of 6, so intermediate states are
scored pessimistically and the outer search is misled.  Closing this needs an
exact small-GTSP solver for ~24 components x 5 break points; a bipartite-matching
formulation (maximise free om joins) is the natural route and was tried but not
got right.

Usage:
  python3 code/gen2.py --n 6 --iters 20000
  python3 code/gen2.py --n 6 --seed-from data/houston_872.txt
"""

import argparse
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import chainer                                                   # noqa: E402
from build import canonical, coords, design_of, to_string        # noqa: E402
from permgraph import is_superpermutation, string_to_path, weight  # noqa: E402
from superstruct import Struct                                   # noqa: E402

EXACT_LIMIT = 12          # Held-Karp above this gets too slow in Python
CHOICE_LIMIT = 400        # cap on total (component, break-point) states


class Gen:
    def __init__(self, n):
        self.n = n
        self.st = Struct(n)
        self.rings = []
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
            self.rings.append(ring)
        self.F1 = math.factorial(n - 1)
        assert len(self.rings) == self.F1

    # ---- chi -> arcs ---------------------------------------------------

    def arcs_of(self, chi):
        out = []
        for cid, cuts in enumerate(chi):
            ring, ks = self.rings[cid], sorted(cuts)
            for i, k in enumerate(ks):
                nxt = ks[(i + 1) % len(ks)]
                out.append((ring[k], (nxt - k) % self.n or self.n))
        return out

    def end_of(self, arc):
        x = arc[0]
        for _ in range(arc[1] - 1):
            x = self.st.sig(x)
        return x

    # ---- arc set -> delta-components -----------------------------------

    def components(self, arcs):
        """Ordered arc-runs of the delta-graph: the blocks, for free."""
        ix = {a[0]: i for i, a in enumerate(arcs)}
        ends = [self.end_of(a) for a in arcs]
        nxt = {}
        for i, a in enumerate(arcs):
            t = self.st.delta(ends[i])
            if t in ix:
                nxt[i] = ix[t]
        heads = set(range(len(arcs))) - set(nxt.values())
        seen, comps = set(), []
        for i in list(heads) + list(range(len(arcs))):
            if i in seen:
                continue
            run, x = [], i
            while x is not None and x not in seen:
                seen.add(x)
                run.append(x)
                x = nxt.get(x)
            comps.append(run)
        return comps, ends

    # ---- inner problem: chain the components ---------------------------

    def options(self, arcs, comps, ends):
        """Per component, the admissible (entry, exit, rotation) triples.

        A path component has one.  A CYCLE has n-1 of them -- one per place you
        break it -- and the choice matters enormously: breaking the n=6
        champion's cycles canonically costs Y = 9 where the right break costs 0.
        """
        ix = {a[0]: i for i, a in enumerate(arcs)}
        out = []
        for run in comps:
            tail = ends[run[-1]]
            is_cycle = ix.get(self.st.delta(tail)) == run[0]
            if not is_cycle:
                out.append([(arcs[run[0]][0], tail, 0)])
            else:
                L = len(run)
                out.append([(arcs[run[i]][0], ends[run[(i - 1) % L]], i)
                            for i in range(L)])
        return out

    def chain(self, arcs, comps, ends, node_cap=None):
        """Min sum of (w-3) over the comps-1 joins; returns (Y, order, rots).

        `chainer.solve` is exact at any `comps` and is the default: the
        free-join graph has out-degree <= 1, so free continuation is forced and
        the problem is a path cover, not a TSP.  It is also far faster here --
        3 s at the comps = 24 exact cover, 3 ms at the n = 7 champion, where the
        old Held-Karp/greedy split took 50 s AND returned Y = 5 instead of 0.
        The old path is kept as the fallback for instances the exact search
        cannot finish.
        """
        opts = self.options(arcs, comps, ends)
        c = len(comps)
        if c == 1:
            return 0, [0], [0]
        try:
            if node_cap is None:
                return chainer.solve(opts)
            return chainer.solve(opts, node_cap=node_cap)
        except (TimeoutError, RuntimeError, AssertionError):
            pass
        total = sum(len(o) for o in opts)
        if c <= EXACT_LIMIT and total <= CHOICE_LIMIT:
            return self._gtsp(opts, c)
        return self._greedy(opts, c)

    @staticmethod
    def _cost(a, b):
        return max(0, weight(a, b) - 3)

    def _gtsp(self, opts, c):
        """Held-Karp over (component, break-point) states."""
        INF = float("inf")
        states = [(i, k) for i in range(c) for k in range(len(opts[i]))]
        sid = {s: t for t, s in enumerate(states)}
        NS = len(states)
        dp = [[INF] * NS for _ in range(1 << c)]
        par = [[-1] * NS for _ in range(1 << c)]
        for (i, k) in states:
            dp[1 << i][sid[(i, k)]] = 0
        for mask in range(1 << c):
            row = dp[mask]
            for (i, k) in states:
                t = sid[(i, k)]
                d = row[t]
                if d == INF or not mask >> i & 1:
                    continue
                exit_i = opts[i][k][1]
                for (j, l) in states:
                    if mask >> j & 1:
                        continue
                    nd = d + self._cost(exit_i, opts[j][l][0])
                    u = sid[(j, l)]
                    nm = mask | 1 << j
                    if nd < dp[nm][u]:
                        dp[nm][u] = nd
                        par[nm][u] = t
        full = (1 << c) - 1
        bt = min(range(NS), key=lambda t: dp[full][t])
        seq, mask, t = [], full, bt
        while t != -1:
            i, k = states[t]
            seq.append((i, k))
            p = par[mask][t]
            mask ^= 1 << i
            t = p
        seq.reverse()
        return dp[full][bt], [i for i, _ in seq], \
            [opts[i][k][2] for i, k in seq]

    def _greedy(self, opts, c, rounds=3):
        """Cover the components by realisable free chains, then order those.

        The earlier attempts failed for a structural reason.  A component's
        break point fixes BOTH its entry and its exit, so a free (om) join is
        not an independent choice -- which is exactly why om-chains cap at
        ord(s) = n-2.  A bipartite matching relaxes that coupling away and
        produces chains that cannot be realised (Y = 15 against an optimum of
        6); plain greedy + Or-opt on the order gets stuck at 11.

        So work on STATES (component, break point): enumerate the chains that
        are actually realisable by following free edges, then cover the
        components greedily longest-first.  Each chain becomes one block-run;
        joins between chains cost >= 1, and `_score_seq` prices the result
        exactly.
        """
        states = [(i, k) for i in range(c) for k in range(len(opts[i]))]
        nxt = {}
        for (i, k) in states:
            ex = opts[i][k][1]
            nxt[(i, k)] = [(j, l) for (j, l) in states
                           if j != i and self._cost(ex, opts[j][l][0]) == 0]

        # Depth cap: free joins are weight-3, and om-chains cap at ord(s)=n-2,
        # so long free chains are rare.  Without a cap this DFS is exponential
        # -- it ran past 900 s on a single n = 7 arc set.
        depth_cap = 2 * (self.n - 2)

        def extend(chain, used):
            if len(chain) >= depth_cap:
                return chain
            best = chain
            for (j, l) in nxt[chain[-1]]:
                if j in used:
                    continue
                cand = extend(chain + [(j, l)], used | {j})
                if len(cand) > len(best):
                    best = cand
                if len(best) >= depth_cap:
                    break
            return best

        remaining, chains = set(range(c)), []
        while remaining:
            best = None
            for (i, k) in states:
                if i not in remaining:
                    continue
                ch = extend([(i, k)], {i})
                ch = [st for st in ch if st[0] in remaining]
                if best is None or len(ch) > len(best):
                    best = ch
            chains.append(best)
            remaining -= {i for i, _ in best}

        order = [i for ch in chains for i, _ in ch]
        tot, rots = self._score_seq(opts, order)
        tot, order, rots = self._oropt(opts, order, rots, tot, passes=120)
        return tot, order, rots

    def _score_seq(self, opts, order, _unused=None):
        """Exact cost of a component sequence: for a FIXED order the optimal
        break points are a shortest path, so this is a chain DP, not a greedy
        left-to-right pick (which was costing ~8 units of Y at n = 6)."""
        INF = float("inf")
        prev = [0.0] * len(opts[order[0]])
        back = []
        for i in range(1, len(order)):
            a, b = order[i - 1], order[i]
            cur = [INF] * len(opts[b])
            bk = [-1] * len(opts[b])
            for l in range(len(opts[b])):
                head = opts[b][l][0]
                for k in range(len(opts[a])):
                    d = prev[k] + self._cost(opts[a][k][1], head)
                    if d < cur[l]:
                        cur[l], bk[l] = d, k
            prev, _ = cur, back.append(bk)
        end = min(range(len(prev)), key=lambda k: prev[k])
        tot = prev[end]
        ks = [end]
        for bk in reversed(back):
            ks.append(bk[ks[-1]])
        ks.reverse()
        return int(tot), [opts[ci][k][2] for ci, k in zip(order, ks)]

    def _oropt(self, opts, order, rots, tot, passes=2):
        """Move one component elsewhere in the sequence while it helps."""
        for _ in range(passes):
            improved = False
            for i in range(len(order)):
                seg = order[i]
                rest = order[:i] + order[i + 1:]
                for j in range(len(rest) + 1):
                    if j == i:
                        continue
                    cand = rest[:j] + [seg] + rest[j:]
                    t, r = self._score_seq(opts, cand, None)
                    if t < tot:
                        tot, order, rots, improved = t, cand, r, True
                        break
                if improved:
                    break
            if not improved:
                break
        return tot, order, rots

    # ---- objective -----------------------------------------------------

    def evaluate(self, chi, fast=False):
        """Objective S + comps + Y.

        `fast=True` replaces the exact chaining by `chainer.cheap_bound`, an
        O(states) admissible bound: a component no free edge can leave must end
        its chain, one no free edge can reach must start one, so
        `Y >= max(dead_out, dead_in) - 1`.  That is tier 1 of three -- the
        sweep uses it, `chainer.lower_bound` sharpens it, and the exact chainer
        prices anything worth keeping.  It costs ~0.4 ms where the chain-cover
        bound costs 110 ms at the 102-component states a random start passes
        through, and is *tighter* there (47 against 16).

        It used to use `Y >= ceil(comps/(n-2)) - 1`, which is NOT admissible and
        was steering this search away from champions.  That cap is `ord(s)`, and
        it only binds where the weight-3 exit is forced onto om; at a champion
        the arcs are partial and the chains run long.  Measured, it fails on
        1,273 of 44,672 corpus rows -- including the n = 7 record, which it
        prices at T = 145 against a true 142, while pricing the exact cover at
        29 against a true 30.  So the proxy made the exact cover look better
        than the champion by 4.
        """
        arcs = self.arcs_of(chi)
        S = len(arcs) - self.F1
        comps, ends = self.components(arcs)
        if fast:
            c = len(comps)
            lb = chainer.cheap_bound(self.options(arcs, comps, ends))
            return S + c + lb, arcs, comps, None, None
        Y, order, rots = self.chain(arcs, comps, ends)
        return S + len(comps) + Y, arcs, comps, order, rots

    def design(self, arcs, comps, order, rots):
        out = []
        for ci, rot in zip(order, rots):
            run = comps[ci]
            run = run[rot:] + run[:rot]        # break the cycle where chosen
            out += [arcs[i] for i in run]
        return out


def family_chi(g, fam):
    pos = {}
    for cid, ring in enumerate(g.rings):
        for k, q in enumerate(ring):
            pos[q] = (cid, k)
    chi = [set() for _ in g.rings]
    for q, f in g.st.fam_of_perm.items():
        if f == fam:
            cid, k = pos[q]
            chi[cid].add(k)
    return chi


def chi_from_string(g, path):
    pos = {}
    for cid, ring in enumerate(g.rings):
        for k, q in enumerate(ring):
            pos[q] = (cid, k)
    chi = [set() for _ in g.rings]
    for start, _ln in design_of(path):
        cid, k = pos[start]
        chi[cid].add(k)
    return chi


def search(g, chi, iters, rng, t0=1.2, t1=0.02, log=None):
    """Anneal on the tier-1 bound; price exactly whenever the incumbent moves.

    The sweep needs a cheap score and the answer needs a true one, and the two
    cannot be the same function: `evaluate(fast=True)` is a LOWER bound, so a
    chi that scores well there may price badly.  So `best` (tier 1) drives the
    annealing and `best_true` (exact) is what gets returned.
    """
    cur = g.evaluate(chi, fast=True)[0]
    best, best_chi = cur, [set(c) for c in chi]
    best_true = g.evaluate(chi)[0]
    n = g.n
    for it in range(iters):
        temp = t0 * (t1 / t0) ** (it / max(1, iters - 1))
        cid = rng.randrange(len(chi))
        old = set(chi[cid])
        r = rng.random()
        if r < 0.4 and len(old) < n:
            chi[cid].add(rng.randrange(n))
        elif r < 0.7 and len(old) > 1:
            chi[cid].discard(rng.choice(sorted(old)))
        else:
            chi[cid].discard(rng.choice(sorted(old)))
            chi[cid].add(rng.randrange(n))
        if not chi[cid] or chi[cid] == old:
            chi[cid] = old
            continue
        new = g.evaluate(chi, fast=True)[0]
        if new <= cur or rng.random() < math.exp((cur - new) / temp):
            cur = new
            if cur < best:
                best = cur
                true = g.evaluate(chi)[0]        # tier 3: the honest price
                if true < best_true:
                    best_true, best_chi = true, [set(c) for c in chi]
                    if log:
                        log(it, best_true, best)
        else:
            chi[cid] = old
    return best_true, best_chi


def run(n, iters, seed, seed_from=None, fam=None, quiet=False):
    g = Gen(n)
    rng = random.Random(seed)
    if seed_from:
        digits = [int(c) for c in open(seed_from).read() if c.isdigit()]
        chi = chi_from_string(g, string_to_path(digits, n))
        print(f"  seeded from {seed_from}")
    elif fam is not None:
        chi = family_chi(g, fam)
        print(f"  seeded monochromatic from family {fam}")
    else:
        chi = [{rng.randrange(n)} for _ in g.rings]
        print("  seeded from a random split-free colouring")

    def log(it, T, lb):
        if not quiet:
            print(f"    it {it:>8}  T = {T}   (tier-1 bound {lb})", flush=True)

    T, chi = search(g, chi, iters, rng, log=log)
    score, arcs, comps, order, rots = g.evaluate(chi)
    design = canonical(g.design(arcs, comps, order, rots), n)
    c = coords(design, n)
    s = to_string(design, n)
    ok = is_superpermutation(s, n)
    print(f"\n  best T = {T}   realised T = {c['T']}   length = {len(s)}   "
          f"valid: {ok}")
    print(f"  coords: " + str({k: c[k] for k in
                               ("R", "S", "v", "d", "A", "B", "Y", "comps")}))
    return c["T"], design, s, ok


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=6)
    ap.add_argument("--iters", type=int, default=20000)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--seed-from", default=None)
    ap.add_argument("--family", type=int, default=None)
    args = ap.parse_args()
    print(__doc__.split("Usage:")[0].strip())
    print(f"\n--- n = {args.n}, {args.iters} iterations ---")
    run(args.n, args.iters, args.seed, args.seed_from, args.family)
