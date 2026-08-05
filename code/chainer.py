"""Exact inner chainer: chaining is a path cover, not a TSP.

`gen2.py` splits the search into an outer arc set and an inner problem -- chain
the delta-components into one walk, paying `Y = sum (w-3)` over the `comps - 1`
joins.  It solves the inner problem by Held-Karp over (component, break-point)
states, which is exact only while `comps <= 12`; at the exact-cover seed
(`comps = 24` at n = 6) it falls back to a heuristic that returns `Y = 9`
against a true optimum of `6`, and costs ~1.4 s.  That is what stops the cold
start.

THE STRUCTURE THAT MAKES IT EASY.  Measure the FREE-JOIN digraph -- states are
(component, break-point) pairs, and there is an edge when the join costs
`max(0, w-3) = 0`:

    seed                        comps  states  free out-degree
    n=6 exact cover                24     120  1 for all 120  (a permutation,
                                                30 cycles of length 4 = ord(s))
    n=6 houston 872                 4     145  0 for 129, 1 for 16
    n=7 5906 champion              18     832  0 for 698, 1 for 134
    n=7 5913 exact cover          120     720  1 for all 720

**On every real walk measured, out-degree is at most 1** (claim `CH1`).  Free
joins have `w <= 3`; `w <= 2` between distinct components is impossible (they
would be one component), so a free join is a weight-3 jump, and of the <= 9
weight-<=3 targets of an arc end at most one is the entry of another component.
At an exact cover it is FORCED: every arc is full, so `l + l' = 2n >= 2n-3` puts
the exit on om (arsenal 3.2), which is unique -- and the graph is then exactly a
permutation whose cycles have length `ord(s) = n-2`, the "om-chains cap at n-2"
already on record.

**Off-distribution it is false**: arc sets an annealer wanders through reach
out-degree 3.  So `runs` branches instead of following a function.  Nothing else
changes, because what the argument actually needs is only that a chain is
MAXIMAL -- every free successor of its exit landing on a component the chain
already covers.  Then:

    every walk decomposes into maximal free CHAINS joined by costly jumps,
    every join BETWEEN chains costs at least 1, and

        Y  =  min over (partition into chains) + (ordering of chains),
        Y >= p - 1  for a partition into p chains.

Enumerate partitions by increasing `p`, order each by branch and bound, and stop
as soon as `Y = p - 1`.  Exact, and fast because `p` is small.

`min_chains` / `lower_bound` expose the `p - 1` bound on its own: it is
admissible where `ceil(comps/(n-2)) - 1` is not (claim `CHLB`, [REF]).

Usage:
  python3 code/chainer.py            # gate against gen2 on both seeds
"""

import argparse
import collections
import itertools
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from permgraph import weight                                      # noqa: E402


def cost(a, b):
    return max(0, weight(a, b) - 3)


def free_targets(x):
    """Every permutation reachable from x by a jump of weight <= 3."""
    n = len(x)
    out = {x[1:] + x[:1], x[2:] + (x[1], x[0]), x[2:] + x[:2]}
    for p in itertools.permutations(x[:3]):
        out.add(x[3:] + p)
    return out


def free_succ(opts):
    """state -> its zero-cost successor states.

    A state is (component, break-point); `opts[i][k] = (entry, exit, rot)`.
    On real walks this is single-valued (CH1) -- that is what makes the inner
    problem a path cover -- but it is NOT single-valued in general: arc sets an
    annealer wanders through reach out-degree 3.  So the list is returned and
    `runs` branches over it.
    """
    entry_of = collections.defaultdict(list)
    for i, os in enumerate(opts):
        for k, (en, _, _) in enumerate(os):
            entry_of[en].append((i, k))
    succ = {}
    for i, os in enumerate(opts):
        for k, (_, ex, _) in enumerate(os):
            hit = [s for t in free_targets(ex) for s in entry_of.get(t, ())
                   if s[0] != i]
            if hit:
                succ[(i, k)] = hit
    return succ


def runs(opts, succ, cap=200_000):
    """Every free chain: a run of states covering distinct components.

    Returns a list of (frozenset of components, entry perm, exit perm, states).
    Chains are enumerated by DFS along free edges, so a chain is maximal
    exactly when every free successor of its exit lands on a component it
    already covers -- which is what makes joins BETWEEN chains cost >= 1.
    """
    out = []
    for i, os in enumerate(opts):
        for k in range(len(os)):
            entry = os[k][0]
            stack = [((i, k), frozenset([i]), ((i, k),))]
            while stack:
                s, seen, states = stack.pop()
                out.append((seen, entry, opts[s[0]][s[1]][1], states))
                if len(out) >= cap:
                    return out
                for t in succ.get(s, ()):
                    if t[0] not in seen:
                        stack.append((t, seen | {t[0]}, states + (t,)))
    return out


def order_chains(chains, ub=1 << 30, node_cap=20_000):
    """Cheapest order for a fixed set of chains, or (ub, None) if none beats ub.

    Branch and bound, not Held-Karp.  Every join BETWEEN chains costs at least
    1: a maximal chain's free successors all land in components it already
    covers, so none can be another chain's head.  That
    gives the admissible bound `remaining joins <= remaining cost`, and since
    only a few per cent of joins cost exactly 1 the tree collapses at once --
    where Held-Karp paid a flat p*2^p at every one of the 100k+ leaves.
    """
    p = len(chains)
    if p == 1:
        return 0, [0]
    ent = [c[1] for c in chains]
    ext = [c[2] for c in chains]
    d = [[cost(ext[a], ent[b]) for b in range(p)] for a in range(p)]

    # warm start: without a finite bound the tree below is a full TSP, which is
    # what made this explode at p ~ 12 on A-line candidates
    greedy = _greedy_order(d, p)
    best = [ub, None]
    if greedy[0] < ub:
        best = [greedy[0], greedy[1]]

    order, used, nodes = [], [False] * p, [0]

    def rec(cur, acc, k):
        nodes[0] += 1
        if nodes[0] > node_cap:
            raise TimeoutError
        if acc + (p - 1 - k) >= best[0]:
            return
        if k == p - 1:
            best[0], best[1] = acc, list(order)
            return
        for b in range(p):
            if used[b]:
                continue
            used[b] = True
            order.append(b)
            rec(b, acc + d[cur][b], k + 1)
            order.pop()
            used[b] = False

    try:
        for a in range(p):
            used[a] = True
            order.append(a)
            rec(a, 0, 0)
            order.pop()
            used[a] = False
    except TimeoutError:
        pass
    return best[0], best[1]


def _greedy_order(d, p):
    """Nearest-neighbour from each start; the best of the p tours."""
    best = (1 << 30, None)
    for s in range(p):
        left, cur, order, Y = set(range(p)) - {s}, s, [s], 0
        while left:
            b = min(left, key=lambda x: d[cur][x])
            Y += d[cur][b]
            order.append(b)
            left.discard(b)
            cur = b
        if Y < best[0]:
            best = (Y, order)
    return best


def cheap_bound(opts):
    """O(states) admissible bound on Y -- tier 1, for the annealing sweep.

    A component none of whose break-points has a free successor must END its
    chain; one that no free edge reaches must START its chain.  So
    `p >= max(dead_out, dead_in)` and `Y >= that - 1`.  This skips `runs`
    entirely, which is where the cost of `min_chains` lives.
    """
    c = len(opts)
    if c <= 1:
        return 0
    succ = free_succ(opts)
    out_ok, in_ok = set(), set()
    for (i, _), hits in succ.items():
        out_ok.add(i)
        for j, _ in hits:
            in_ok.add(j)
    return max(0, max(c - len(out_ok), c - len(in_ok)) - 1)


def _prepare(opts):
    """(component -> runs through it, longest run) for the free-join graph."""
    allruns = runs(opts, free_succ(opts))
    by_comp = collections.defaultdict(list)
    for r in allruns:
        for i in r[0]:
            by_comp[i].append(r)
    return by_comp, max(len(r[0]) for r in allruns)


def packing_fast(opts):
    """`packing_lb` without materialising a single run.  None if not applicable.

    `runs` enumerates every PREFIX of every forced path from every state and
    builds a frozenset for each -- thousands of set constructions per call, and
    the reason an evaluation cost ~2.4 s.  The packing bound only needs the
    CO-OCCURRENCE graph: which pairs of components lie on a common run.  When
    free out-degree is <= 1 (CH1, true of every real walk) the forced path from
    a state is unique, so one forward walk per state gives that graph directly,
    and bitmask ints make the greedy independent set nearly free.

    Returns None when some state has out-degree > 1, because then a single
    forward walk would MISS co-occurrences, shrink the adjacency, and inflate
    the independent set -- which would make the bound too large and unsound.
    The caller falls back to the exact enumeration in that case.
    """
    c = len(opts)
    succ = free_succ(opts)
    if any(len(v) > 1 for v in succ.values()):
        return None
    adj = [0] * c
    for i, os in enumerate(opts):
        for k in range(len(os)):
            mask, s = 1 << i, (i, k)
            while True:
                nxt = succ.get(s)
                if not nxt:
                    break
                t = nxt[0]
                if (mask >> t[0]) & 1:
                    break
                mask |= 1 << t[0]
                s = t
            m = mask
            while m:
                b = m & -m
                adj[b.bit_length() - 1] |= mask
                m ^= b
    for i in range(c):
        adj[i] &= ~(1 << i)

    left, ind = (1 << c) - 1, 0
    while left:
        best, bestd, m = -1, 1 << 30, left
        while m:
            b = m & -m
            i = b.bit_length() - 1
            m ^= b
            d = (adj[i] & left).bit_count()
            if d < bestd:
                best, bestd = i, d
        ind += 1
        left &= ~(1 << best) & ~adj[best]
    return ind


def packing_lb(c, allruns):
    """`p >=` any set of components no two of which share a run.

    Each member of such a set must land in a DIFFERENT chain of any partition,
    so its size lower-bounds `p`.  Greedy, lowest-degree-first, O(c^2).

    This is the bound that makes the free-chain count usable at large `comps`,
    where the exact search cannot finish.  Two relaxations were tried first and
    are much worse:

      * `ceil(comps/longest)` -- 13 at an n = 7 state where this gives **20**;
      * maximum bipartite matching on component links (`p >= comps - M`) -- 0 or
        1 everywhere, useless, because it discards the state-consistency
        coupling (a component's break point fixes BOTH its entry and its exit)
        that is the whole reason chains are short.
    """
    adj = [set() for _ in range(c)]
    for r in allruns:
        m = sorted(r[0])
        for a in range(len(m)):
            for b in range(a + 1, len(m)):
                adj[m[a]].add(m[b])
                adj[m[b]].add(m[a])
    left, ind = set(range(c)), 0
    while left:
        i = min(left, key=lambda x: len(adj[x] & left))
        ind += 1
        left.discard(i)
        left -= adj[i]
    return ind


def min_chains(opts, node_cap=100_000, bound_only=False):
    """Fewest free chains that partition the components.  Gives `Y >= p - 1`.

    Every chaining decomposes into maximal free chains, and every join BETWEEN
    chains costs at least 1 (a chain's free successor lands in a component the
    chain already covers), so `p - 1` is an admissible lower bound on Y.

    This REPLACES `ceil(comps/(n-2)) - 1`, which is not admissible: the cap
    `ord(s) = n-2` on chain length only applies where the weight-3 exit is
    forced onto om (`l + l' >= 2n-3`, arsenal 3.2).  At a champion the arcs are
    partial, nothing is forced, and the chains run long -- the n = 7 champion's
    18 components form ONE chain, where that bound claims at least 4.
    """
    c = len(opts)
    if c <= 1:
        min_chains.exact = True
        return 1
    if bound_only:
        fast = packing_fast(opts)
        if fast is not None:
            min_chains.exact = False       # a bound, not the true minimum
            return fast
    allruns = runs(opts, free_succ(opts))
    by_comp = collections.defaultdict(list)
    for r in allruns:
        for i in r[0]:
            by_comp[i].append(r)
    longest = max(len(r[0]) for r in allruns)
    nodes = [0]

    def feasible(covered, k, pmax):
        nodes[0] += 1
        if nodes[0] > node_cap:
            raise TimeoutError
        left = c - len(covered)
        if not left:
            return True
        if k + -(-left // longest) > pmax:
            return False
        need = left - (pmax - k - 1) * longest
        i = next(j for j in range(c) if j not in covered)
        for r in by_comp[i]:
            if len(r[0]) < need or r[0] & covered:
                continue
            if feasible(covered | r[0], k + 1, pmax):
                return True
        return False

    # start the deepening at the best cheap lower bound, not the crude one:
    # it is both a tighter answer on timeout and fewer levels to search
    floor = max(-(-c // longest), packing_lb(c, allruns))
    min_chains.exact = True
    for pmax in range(floor, c + 1):
        try:
            if feasible(frozenset(), 0, pmax):
                return pmax
        except TimeoutError:
            # `floor` is still a VALID lower bound on p (hence on Y), but it is
            # not the true minimum -- say so, or a caller minimising the bound
            # will chase states where the search merely gave up.
            min_chains.exact = False
            return floor
    return c


def lower_bound(opts, node_cap=100_000):
    """Admissible `Y >=` bound: the better of the two free-chain arguments.

    Neither dominates.  At the n = 6 exact cover the chain cover gives 5 and
    `cheap_bound` gives 0; at a random 102-component colouring `cheap_bound`
    gives 47 while the chain cover degrades to its crude floor of 16, because
    `min_chains` runs out of nodes there.  Taking the max costs nothing.
    """
    return max(cheap_bound(opts), min_chains(opts, node_cap) - 1, 0)


def _greedy_cover(c, by_comp):
    """A valid chain partition, longest-run-first.  Never fails."""
    covered, chosen = frozenset(), []
    while len(covered) < c:
        i = next(j for j in range(c) if j not in covered)
        r = max((r for r in by_comp[i] if not r[0] & covered),
                key=lambda r: len(r[0]))
        chosen.append(r)
        covered |= r[0]
    return chosen


def solve(opts, node_cap=300_000):
    """Minimum Y, exact unless the node cap bites.

    Returns (Y, order of components, rotations).  A greedy cover seeds the
    incumbent first, so this ALWAYS returns a valid chaining -- important
    because the caller's fallback (gen2's Held-Karp/greedy split) costs ~50 s at
    comps = 18.  `solved_exactly()` reports whether the search finished.
    """
    c = len(opts)
    by_comp, longest = _prepare(opts)

    seed = _greedy_cover(c, by_comp)
    Y0, o0 = order_chains(seed)
    best = [[seed[i] for i in o0], Y0]
    nodes = [0]
    solve.exact = True

    class Optimal(Exception):
        pass

    def search(covered, chosen, pmax):
        nodes[0] += 1
        if nodes[0] > node_cap:
            raise TimeoutError
        left = c - len(covered)
        if len(chosen) + -(-left // longest) > pmax:
            return
        if not left:
            Y, order = order_chains(chosen, ub=best[1])
            if order is not None:
                best[0], best[1] = [chosen[i] for i in order], Y
                if Y <= pmax - 1:       # meets the floor: cannot do better
                    raise Optimal
            return
        # with `budget` chains left for `left` components, and every chain at
        # most `longest` long, this chain cannot be shorter than:
        budget = pmax - len(chosen)
        need = left - (budget - 1) * longest
        i = next(j for j in range(c) if j not in covered)
        for r in by_comp[i]:
            if len(r[0]) < need or r[0] & covered:
                continue
            chosen.append(r)
            search(covered | r[0], chosen, pmax)
            chosen.pop()

    for pmax in range(-(-c // longest), c + 1):
        if best[1] <= pmax - 1:         # Y >= p-1, so no deeper p can win
            break
        try:
            search(frozenset(), [], pmax)
        except Optimal:
            break
        except TimeoutError:
            solve.exact = False
            break

    order, rots = [], []
    for chain in best[0]:
        for (i, k) in chain[3]:
            order.append(i)
            rots.append(opts[i][k][2])
    return best[1], order, rots


# ---------------------------------------------------------------------------
# gate
# ---------------------------------------------------------------------------

def gate():
    from build import coords, design_of
    from gen2 import Gen, family_chi
    from permgraph import string_to_path

    ok = True
    cases = [("n=6 houston 872", 6, "data/houston_872.txt", 0),
             ("n=7 5906 champion", 7,
              "data/n7/7_5906_derived_025c4805fc39.txt", 0)]
    for tag, n, path, want in cases:
        g = Gen(n)
        digits = [int(ch) for ch in open(path).read() if ch.isdigit()]
        arcs = [tuple(a) for a in design_of(string_to_path(digits, n))]
        comps, ends = g.components(arcs)
        opts = g.options(arcs, comps, ends)
        Y, order, rots = solve(opts)
        des = g.design(arcs, comps, order, rots)
        c = coords(des, n)
        good = Y == want and c["Y"] == want
        ok &= good
        print(f"  {tag:<20} comps={len(comps):<4} Y={Y}  "
              f"rebuilt: length={c['length']} T={c['T']} Y={c['Y']}  "
              f"{'OK' if good else 'MISMATCH'}")

    print()
    for n, want in ((6, 6),):
        g = Gen(n)
        arcs = g.arcs_of(family_chi(g, 0))
        comps, ends = g.components(arcs)
        opts = g.options(arcs, comps, ends)
        Yg, _, _ = g._greedy(opts, len(comps))     # gen2's ORIGINAL fallback
        Y, order, rots = solve(opts)
        des = g.design(arcs, comps, order, rots)
        c = coords(des, n)
        good = Y == want and c["Y"] == want
        ok &= good
        print(f"  n={n} exact cover     comps={len(comps):<4} "
              f"gen2 heuristic Y={Yg}  ->  exact Y={Y}  "
              f"rebuilt: length={c['length']} T={c['T']} Y={c['Y']}  "
              f"{'OK' if good else 'MISMATCH (want %d)' % want}")
    return 0 if ok else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.parse_args()
    print(__doc__.split("Usage:")[0].strip())
    print("\n--- gate: exact chainer against gen2's known answers ---")
    sys.exit(gate())
