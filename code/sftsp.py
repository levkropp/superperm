"""Split-free walks are an asymmetric TSP, and the known ones are badly ordered.

`sigma(n)` is the shortest SPLIT-FREE superpermutation length.  n = 6 is the
only n where split-free champions are ruled out (`sigma(6) = 873 > 872`), and
`SFGAP`'s "they never return" was withdrawn -- `s(n-1)+n! - s(n)` only
UPPER-bounds the deficit.  Egan's near-optimality settles nothing either, since
Egan is not split-free (`B = 1` forces `S = T-1`).  What matters is how close
split-free can get to Egan.

THE REFORMULATION.  For a split-free walk `S = 0`, so `T = B + Y`.  A delta join
has `w = 2` and is free; a costly join of weight `w` adds 1 to `B` and `w-3` to
`Y`.  So

    T  =  1 + sum over joins of (w - 2),

and with the COVER fixed -- which rotation of each class starts its arc --
minimising the length over ORDERINGS is exactly an asymmetric TSP on
`(n-1)!` nodes with

    cost(u -> v)  =  weight(end u, start v) - 2  >=  0,

zero precisely on delta steps.  It reproduces both known n = 7 split-free walks:

    5913   B=120  Y=29   sum(w-2) = 119 + 29 = 148   T = 149
    5912   B=145  Y= 3   sum(w-2) = 144 +  3 = 147   T = 148

WHERE THE SLACK IS.  At an exact cover `comps = 120` forces >= 119 costly joins,
and Chain-Count caps free chains at `n-2 = 5`, so >= 24 chains and >= 23 joins
costing >= 2:  sum(w-2) >= 96 + 46 = 142, i.e. **T >= 143**.  The 5913 walk sits
at 149.  So up to six units may be available from RE-ORDERING a cover already in
hand, before touching the cover at all.

An upper bound needs a construction, not a proof, so a heuristic tour is enough
-- the resulting string is verified exactly afterwards.  That matters:
`chainer.solve` at `comps = 120` did not finish in 20 minutes.

Usage:
  python3 code/sftsp.py --gate      # model must reproduce 5912/5913 and n=6's 30
"""

import argparse
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from build import design_of, to_string                            # noqa: E402
from permgraph import is_superpermutation, string_to_path, weight  # noqa: E402
from superstruct import Struct                                    # noqa: E402


def base(n):
    return n + math.factorial(n) + math.factorial(n - 1) - 3


class Cover:
    """The 720 full arcs of a split-free walk, as ATSP nodes.

    A split-free walk covers each rotation class with exactly one FULL arc, so
    the walk is determined by (a) which rotation of each class starts its arc --
    the cover -- and (b) the order.  This class holds (a) and prices (b).
    """

    def __init__(self, n, starts):
        self.n = n
        self.st = Struct(n)
        self.starts = list(starts)
        assert len(self.starts) == math.factorial(n - 1), "not one arc per class"
        assert len({self.st.cls_id[s] for s in self.starts}) == len(self.starts)
        self.ends = [self.st.end_of(s) for s in self.starts]
        self.ix = {s: i for i, s in enumerate(self.starts)}
        # the unique zero-cost successor of each node, if it exists
        self.dfree = {}
        for i, e in enumerate(self.ends):
            j = self.ix.get(self.st.delta(e))
            if j is not None:
                self.dfree[i] = j

        self._m = None

    def matrix(self):
        """Full cost matrix.  (n-1)!^2 is 518k entries at n = 7 -- cheap once,
        and the local search touches it millions of times."""
        if self._m is None:
            st = self.starts
            self._m = [[weight(e, s) - 2 for s in st] for e in self.ends]
        return self._m

    def cost(self, i, j):
        return self.matrix()[i][j]

    def tour_cost(self, order):
        return sum(self.cost(a, b) for a, b in zip(order, order[1:]))

    def T(self, order):
        return 1 + self.tour_cost(order)

    def design(self, order):
        return [(self.starts[i], self.n) for i in order]

    def string(self, order):
        return to_string(self.design(order), self.n)


def cover_of(n, digits):
    """(Cover, walk order) read off a real split-free string."""
    path = string_to_path(digits, n)
    des = design_of(path)
    assert len(des) == math.factorial(n - 1), f"not split-free: R={len(des)}"
    assert all(ln == n for _, ln in des), "a split-free arc is not full"
    starts = [s for s, _ in des]
    cov = Cover(n, starts)
    return cov, [cov.ix[s] for s in starts]


def oropt(cov, order, maxseg=3, rounds=200, verbose=False):
    """Or-opt on the Hamiltonian PATH: relocate a segment, orientation kept.

    2-opt is avoided deliberately.  This is an ASYMMETRIC instance, so reversing
    a segment re-prices every edge inside it; Or-opt moves a segment intact and
    touches exactly three edges, so its delta is O(1) and always correct.

    Seeded from a real walk, this can only improve on it -- which is the point:
    the known n = 7 split-free strings may simply be badly ordered.
    """
    c = cov.cost
    N = len(order)
    for rnd in range(rounds):
        best = None
        for L in range(1, maxseg + 1):
            for i in range(N - L + 1):
                j = i + L - 1
                sf, sl = order[i], order[j]
                p = order[i - 1] if i > 0 else None
                q = order[j + 1] if j + 1 < N else None
                gain = 0
                if p is not None:
                    gain += c(p, sf)
                if q is not None:
                    gain += c(sl, q)
                if p is not None and q is not None:
                    gain -= c(p, q)
                if gain <= 0:
                    continue
                # insert between consecutive nodes outside [i..j], or at an end
                for k in range(-1, N):
                    if i - 1 <= k <= j:
                        continue
                    a = order[k] if k >= 0 else None
                    b = order[k + 1] if k + 1 < N else None
                    if b is not None and i <= k + 1 <= j:
                        continue
                    add = 0
                    if a is not None:
                        add += c(a, sf)
                    if b is not None:
                        add += c(sl, b)
                    if a is not None and b is not None:
                        add -= c(a, b)
                    d = add - gain
                    if d < 0 and (best is None or d < best[0]):
                        best = (d, i, j, k)
        if best is None:
            if verbose:
                print(f"    local optimum after {rnd} moves")
            return order
        _d, i, j, k = best
        seg = order[i:j + 1]
        rest = order[:i] + order[j + 1:]
        # k indexes into the ORIGINAL list; translate to `rest`
        pos = (k + 1) if k < i else (k + 1 - (j - i + 1))
        order = rest[:pos] + seg + rest[pos:]
        if verbose:
            print(f"    move {rnd}: seg[{i}:{j}] -> {pos}   "
                  f"T = {cov.T(order)}", flush=True)
    return order


def blocks_of(cov):
    """The delta-cycles of the cover: at an exact cover, (n-2)! cycles of n-1.

    `dfree` is the zero-cost successor and is injective, so it is a partial
    permutation of the arcs -- its orbits ARE the blocks.
    """
    seen, out = set(), []
    for i in range(len(cov.starts)):
        if i in seen:
            continue
        run, x = [], i
        while x is not None and x not in seen:
            seen.add(x)
            run.append(x)
            x = cov.dfree.get(x)
        out.append(run)
    return out


def block_order_of(cov, order, blocks):
    """Read (block, break) pairs off an arc order that keeps blocks intact."""
    where = {}
    for bi, b in enumerate(blocks):
        for k, a in enumerate(b):
            where[a] = (bi, k)
    sol, i, L = [], 0, len(blocks[0])
    while i < len(order):
        bi, k = where[order[i]]
        if order[i:i + L] != [blocks[bi][(k + t) % L] for t in range(L)]:
            return None                    # blocks are fragmented; not this model
        sol.append((bi, k))
        i += L
    return sol


def blockopt(cov, blocks, sol, rounds=4000, verbose=False, seed=0):
    """Local search over (block order, break point) -- the real move set.

    Arc-level Or-opt cannot help here: a block is `n-1` arcs and its break point
    fixes entry AND exit together, so the only moves that matter re-choose the
    break at the same time as they move the block.  Three moves:

        rebreak   change one block's break point
        relocate  move a block elsewhere, trying every break
        swap      exchange two blocks, trying every break
    """
    import random
    rng = random.Random(seed)
    M = cov.matrix()
    L = len(blocks[0])

    def entry(bi, k):
        return blocks[bi][k]

    def exit_(bi, k):
        return blocks[bi][(k - 1) % L]

    def link(a, b):
        return M[exit_(*a)][entry(*b)]

    def total(s):
        return sum(link(s[t], s[t + 1]) for t in range(len(s) - 1))

    cur = total(sol)
    N = len(sol)
    for rnd in range(rounds):
        improved = False
        # 1) rebreak a single block
        for t in range(N):
            bi, k = sol[t]
            for k2 in range(L):
                if k2 == k:
                    continue
                d = 0
                if t > 0:
                    d += link(sol[t - 1], (bi, k2)) - link(sol[t - 1], (bi, k))
                if t + 1 < N:
                    d += link((bi, k2), sol[t + 1]) - link((bi, k), sol[t + 1])
                if d < 0:
                    sol[t] = (bi, k2)
                    cur += d
                    improved = True
                    break
        # 2) relocate a block, choosing its break at the destination
        for t in rng.sample(range(N), N):
            bi, k = sol[t]
            gain = 0
            if t > 0:
                gain += link(sol[t - 1], sol[t])
            if t + 1 < N:
                gain += link(sol[t], sol[t + 1])
            if t > 0 and t + 1 < N:
                gain -= link(sol[t - 1], sol[t + 1])
            if gain <= 0:
                continue
            rest = sol[:t] + sol[t + 1:]
            best = None
            for pos in range(len(rest) + 1):
                a = rest[pos - 1] if pos > 0 else None
                b = rest[pos] if pos < len(rest) else None
                for k2 in range(L):
                    add = 0
                    if a is not None:
                        add += link(a, (bi, k2))
                    if b is not None:
                        add += link((bi, k2), b)
                    if a is not None and b is not None:
                        add -= link(a, b)
                    if add - gain < 0 and (best is None or add < best[0]):
                        best = (add, pos, k2)
            if best is not None:
                add, pos, k2 = best
                sol = rest[:pos] + [(bi, k2)] + rest[pos:]
                cur += add - gain
                improved = True
                if verbose:
                    print(f"    relocate -> T = {1 + 119 + cur - 119 + 120}",
                          end="\r")
        if not improved:
            if verbose:
                print(f"    block local optimum after {rnd} rounds, "
                      f"cost {cur}")
            break
    return sol, cur


def arc_order_of(blocks, sol):
    L = len(blocks[0])
    out = []
    for bi, k in sol:
        out += [blocks[bi][(k + t) % L] for t in range(L)]
    return out


def cpsat(cov, seed_order=None, seconds=300.0, workers=8, verbose=True):
    """Exact-capable ATSP over the arcs, via CP-SAT AddCircuit.

    The 720-node instance is the WHOLE problem -- block structure, break points
    and fragmentation all fall out of it, because a tour of the arcs is priced
    by `sum (w-2)` whatever shape it takes.  The hand-written Or-opt could not
    move off the seed; CP-SAT with a warm start can, and any solution it returns
    is a construction that gets validated as a string afterwards.

    A Hamiltonian PATH is modelled as a circuit through a dummy depot with
    zero-cost edges to and from every arc.

    Only EDGES worth using are created: an arc's out-edges are capped at the
    cheapest `deg` targets (plus its free delta successor).  Full density is
    720^2 = 518k literals, which CP-SAT will chew on for ever.
    """
    from ortools.sat.python import cp_model
    M = cov.matrix()
    N = len(cov.starts)
    DEP = N

    deg = 12
    keep = []
    for i in range(N):
        row = sorted(range(N), key=lambda j: M[i][j])
        near = [j for j in row if j != i][:deg]
        f = cov.dfree.get(i)
        if f is not None and f not in near:
            near.append(f)
        if seed_order is not None:
            pass
        keep.append(near)
    if seed_order is not None:
        for a, b in zip(seed_order, seed_order[1:]):
            if b not in keep[a]:
                keep[a].append(b)

    model = cp_model.CpModel()
    lits, arcs = {}, []
    for i in range(N):
        for j in keep[i]:
            v = model.NewBoolVar(f"x{i}_{j}")
            lits[(i, j)] = v
            arcs.append((i, j, v))
    for i in range(N):
        v = model.NewBoolVar(f"s{i}")
        lits[(DEP, i)] = v
        arcs.append((DEP, i, v))
        w = model.NewBoolVar(f"e{i}")
        lits[(i, DEP)] = w
        arcs.append((i, DEP, w))
    model.AddCircuit(arcs)
    model.Minimize(sum(M[i][j] * lits[(i, j)]
                       for i in range(N) for j in keep[i]))

    if seed_order is not None:
        hint = set(zip(seed_order, seed_order[1:]))
        hint.add((DEP, seed_order[0]))
        hint.add((seed_order[-1], DEP))
        for key, var in lits.items():
            model.AddHint(var, 1 if key in hint else 0)

    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = seconds
    s.parameters.num_search_workers = workers
    s.parameters.log_search_progress = False
    st = s.Solve(model)
    if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        if verbose:
            print(f"    CP-SAT: no solution ({s.StatusName(st)})")
        return None, None
    nxt = {}
    for (i, j), v in lits.items():
        if s.Value(v):
            nxt[i] = j
    order, x = [], nxt[DEP]
    while x != DEP:
        order.append(x)
        x = nxt[x]
    if verbose:
        print(f"    CP-SAT {s.StatusName(st)}  cost={int(s.ObjectiveValue())} "
              f"bound={int(s.BestObjectiveBound())}  T={1+int(s.ObjectiveValue())}"
              f"  {s.WallTime():.0f}s")
    return order, int(s.BestObjectiveBound())


def pentad_covers(st, rng, tries=200):
    """Partitions of the (n-1)! classes into (n-3)! disjoint <s>-orbits.

    The 5913 walk decomposes into 24 free chains of 5 blocks each -- complete
    <s>-orbits, the Pentad cap.  So ANY cover built from disjoint Pentads gives
    (n-3)! chains, the minimum, and the only remaining cost is linking them.
    Randomised greedy over the 1008 orbits; each is a set of 30 classes.
    """
    orbits = st.s_orbits()
    ocls = []
    for orb in orbits:
        cs = set()
        for lid in orb:
            cs |= st.loop_classes(lid)
        ocls.append(frozenset(cs))
    need = len({st.cls_id[p] for p in st.perms})
    mask = [sum(1 << c for c in cs) for cs in ocls]
    full = (1 << need) - 1
    span = len(ocls[0])
    want = need // span
    out, idx = [], list(range(len(orbits)))
    for _ in range(tries):
        rng.shuffle(idx)
        used, pick = 0, []
        for i in idx:
            if used & mask[i] == 0:
                used |= mask[i]
                pick.append(i)
                if len(pick) == want:
                    break
        if used == full:
            out.append([orbits[i] for i in pick])
    return out


def chain_from_orbit(st, g):
    """The chain of complete traversals entered at `g`: g, gs, ..., gs^(n-3).

    Returns (arc starts covering the orbit, chain entry, chain exit).
    """
    n = st.n
    starts, x = [], g
    for _ in range(n - 2):
        h = x
        for _ in range(n - 1):
            starts.append(h)
            h = st.comp(h, st.a)
        x = st.comp(x, st.s)
    last = st.comp(g, st.apow[0])
    # exit = end of the final block's last arc
    fin = st.comp(g, st.s)
    for _ in range(n - 4):
        fin = st.comp(fin, st.s)
    tail = st.comp(fin, st.apow[n - 2])
    return starts, g, st.end_of(tail)


def link_atsp(C, seconds=60.0, workers=8):
    """Exact ATSP over the chains (tiny: (n-3)! nodes)."""
    from ortools.sat.python import cp_model
    K = len(C)
    m = cp_model.CpModel()
    lits, arcs = {}, []
    for i in range(K):
        for j in range(K):
            if i == j:
                continue
            v = m.NewBoolVar(f"x{i}_{j}")
            lits[(i, j)] = v
            arcs.append((i, j, v))
        a = m.NewBoolVar(f"s{i}")
        lits[(K, i)] = a
        arcs.append((K, i, a))
        b = m.NewBoolVar(f"e{i}")
        lits[(i, K)] = b
        arcs.append((i, K, b))
    m.AddCircuit(arcs)
    m.Minimize(sum(C[i][j] * lits[(i, j)]
                   for i in range(K) for j in range(K) if i != j))
    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = seconds
    s.parameters.num_search_workers = workers
    st_ = s.Solve(m)
    from ortools.sat.python import cp_model as cm
    if st_ not in (cm.OPTIMAL, cm.FEASIBLE):
        return None, None
    nxt = {i: j for (i, j), v in lits.items() if s.Value(v)}
    seq, x = [], nxt[K]
    while x != K:
        seq.append(x)
        x = nxt[x]
    return int(s.ObjectiveValue()), seq


def validate(cov, order, n, expect_T=None):
    """A candidate is only real if the STRING round-trips."""
    s = cov.string(order)
    digits = [int(ch) for ch in s]
    ok = is_superpermutation(digits, n)
    path = string_to_path(digits, n)
    full = len(path) == math.factorial(n)
    S = len(design_of(path)) - math.factorial(n - 1) if full else None
    T = len(digits) - base(n)
    good = ok and full and S == 0 and (expect_T is None or T == expect_T)
    print(f"    validate: len={len(digits)} superperm={ok} "
          f"all-perms={full} S={S} T={T}"
          f"   {'OK' if good else '<== INVALID'}")
    return good, digits, T


def gate():
    """The model must reproduce real walks exactly, or nothing below matters."""
    import census
    ok = True
    print("\n--- gate: re-cost real split-free walks ---")
    seen = set()
    for n, label, path in census.sources(9):
        if n not in (5, 6, 7):
            continue
        for d in census.read_strings(path):
            if not d or max(d) != n or min(d) != 1:
                continue
            p_ = string_to_path(d, n)
            if len(p_) != math.factorial(n):
                continue
            if len(design_of(p_)) != math.factorial(n - 1):
                continue
            key = (n, len(d))
            if key in seen:
                continue
            seen.add(key)
            cov, order = cover_of(n, d)
            T = cov.T(order)
            Texp = len(d) - base(n)
            rebuilt = cov.string(order)
            same = [int(c) for c in rebuilt] == list(d)
            good = (T == Texp) and same
            ok &= good
            print(f"  n={n} len={len(d)}  T(model)={T}  T(actual)={Texp}  "
                  f"sum(w-2)={T-1}  rebuild={'exact' if same else 'DIFFERS'}"
                  f"   {'OK' if good else '<== MODEL WRONG'}")
    print("\n  the model reproduces every known split-free walk"
          if ok else "\n  MODEL IS WRONG -- stop here")
    return 0 if ok else 1


def improve(n, maxseg, rounds):
    """Seed from every known split-free walk at `n` and Or-opt it."""
    import census
    seen, out = set(), []
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
            if len(d) in seen:
                continue
            seen.add(len(d))
            cov, order = cover_of(n, d)
            T0 = cov.T(order)
            print(f"\n  seed {label}  len={len(d)}  T={T0}")
            order = oropt(cov, order, maxseg=maxseg, rounds=rounds,
                          verbose=True)
            T1 = cov.T(order)
            print(f"    T: {T0} -> {T1}   length {base(n)+T0} -> {base(n)+T1}")
            good, digits, T = validate(cov, order, n, expect_T=T1)
            out.append((label, T0, T1, good, digits))
    return out


FLOOR = {5: 7, 6: 30}       # PROVED optimal split-free T; going below is a bug


def main(do_gate, n, maxseg, rounds):
    if do_gate:
        rc = gate()
        if rc:
            return rc
        print("\n--- gate: the solver must not beat a PROVED optimum ---")
        res = improve(6, maxseg, rounds)
        bad = [r for r in res if r[2] < FLOOR[6]]
        for label, T0, T1, good, _ in res:
            print(f"  n=6 {label}: T {T0} -> {T1}   floor {FLOOR[6]}"
                  f"   {'OK' if T1 >= FLOOR[6] and good else '<== BUG'}")
        if bad:
            print("  SOLVER WENT BELOW A PROVED OPTIMUM -- the model is wrong")
            return 1
        print("  solver respects the n = 6 floor")
        return 0
    res = improve(n, maxseg, rounds)
    best = min((r[2] for r in res), default=None)
    if best is not None:
        print(f"\n  best T at n = {n}: {best}   length {base(n)+best}")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--gate", action="store_true")
    ap.add_argument("--n", type=int, default=7)
    ap.add_argument("--maxseg", type=int, default=3)
    ap.add_argument("--rounds", type=int, default=200)
    args = ap.parse_args()
    print(__doc__.split("Usage:")[0].strip())
    sys.exit(main(args.gate, args.n, args.maxseg, args.rounds))
