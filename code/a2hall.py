"""Is A2 true, and can it be proved by a charging argument?

`CH3` (`T >= S + comps + p - 1`) is the first ordering-free bound here to beat
HPV, and its reduction to the 5905 question rests on `A2` (`comps >= v - S`),
still [CONJ].  This session reduced A2 through three proved equivalences
(notes/pbound.md 6) to four elementary counts:

    A2FOUR    A2  <=>  v <= S + W + D + cyc

    W    full arcs whose next loop generator is not an arc start
    D    partial arcs whose delta-exit is not an arc start
    cyc  delta-cycle components
    F    all-full saturated loops   (F <= cyc, by S1)

THE NATURAL PROOF is a CHARGING: inject the v entered loops into the
S + W + D + cyc tokens.  Ownership:

    cyc   F of them are an all-full loop's own cycle -- PRIVATE to that loop;
          the other cyc-F span several loops -- SHARED by the loops they touch
    W, D  a specific gap / dead arc -- PRIVATE to one loop
    S     class C owns mu_C - 1 tokens -- SHARED by C's mu_C loops

By Hall the injection exists iff every set X of loops has |N(X)| >= |X|, and the
failure mode is explicit: a set of loops closed under the class relation whose
only tokens are S-tokens of classes wholly inside X has
|N(X)| = |X| - #classes < |X|.  `A2HALL` measured that 1.11% of
multiply-covered classes have no loop with an alternative charge, so such closed
sets are not obviously impossible.

THIS FILE ANSWERS TWO QUESTIONS, in order.

  Stage 0   is A2 even true?  `slack` is computable in one pass, so hunt for a
            negative.  A negative refutes A2 and collapses CH3's reduction.
  Stage 1   does Hall hold?  Build the token graph, run maximum matching, and
            report the deficiency v - (matching size), which by Koenig equals
            max_X (|X| - |N(X)|).

Usage:
  python3 code/a2hall.py             # gate + matching over the census
  python3 code/a2hall.py --search    # Stage 0: hunt an A2 counterexample
"""

import argparse
import collections
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from build import _arc_end, coords, design_of                    # noqa: E402
from gen2 import Gen                                             # noqa: E402
from permgraph import string_to_path                             # noqa: E402


def counts(g, arcs):
    """(S, W, D, cyc, F, v) -- the four counts of A2FOUR plus F and v."""
    st = g.st
    K = {a[0] for a in arcs}
    ix = {a[0]: i for i, a in enumerate(arcs)}
    nxt = {}
    for i, (s, ln) in enumerate(arcs):
        t = st.delta(_arc_end(st, s, ln))
        if t in ix:
            nxt[i] = ix[t]
    W = sum(1 for (s, ln) in arcs if ln == g.n and st.comp(s, st.a) not in K)
    D = sum(1 for i, (s, ln) in enumerate(arcs) if ln < g.n and i not in nxt)
    heads = set(range(len(arcs))) - set(nxt.values())
    seen, cyc, cycles = set(), 0, []
    for i in list(heads) + list(range(len(arcs))):
        if i in seen:
            continue
        run, x = [], i
        while x is not None and x not in seen:
            seen.add(x)
            run.append(x)
            x = nxt.get(x)
        if i not in heads:
            cyc += 1
            cycles.append(run)
    per = collections.defaultdict(list)
    for (s, ln) in arcs:
        per[st.loop_of[s]].append((s, ln))
    F = sum(1 for l, xs in per.items()
            if len(xs) == g.n - 1 and all(ln == g.n for _, ln in xs))
    S = len(arcs) - g.F1
    return S, W, D, cyc, F, len(per), cycles, nxt


def slack(g, arcs):
    """S + W + D + cyc - v.  A2 says this is >= 0."""
    S, W, D, cyc, F, v, _, _ = counts(g, arcs)
    return S + W + D + cyc - v, (S, W, D, cyc, F, v)


# ---------------------------------------------------------------------------
# Stage 1: the token graph and its matching
# ---------------------------------------------------------------------------

def token_graph(g, arcs):
    """loops -> the tokens they may be charged to.  Returns (loops, adjacency).

    Tokens are labelled ('S', class), ('W', arc), ('D', arc), ('C', cycle id).
    """
    st = g.st
    S, W, D, cyc, F, v, cycles, nxt = counts(g, arcs)
    K = {a[0] for a in arcs}
    ix = {a[0]: i for i, a in enumerate(arcs)}
    loops = sorted({st.loop_of[a[0]] for a in arcs})
    li = {L: i for i, L in enumerate(loops)}
    adj = collections.defaultdict(set)

    bycls = collections.defaultdict(list)
    for (s, ln) in arcs:
        bycls[st.cls_id[s]].append(s)
    for c, xs in bycls.items():
        if len(xs) < 2:
            continue
        for t in range(len(xs) - 1):              # mu_C - 1 tokens
            for s in xs:
                adj[li[st.loop_of[s]]].add(('S', c, t))
    for (s, ln) in arcs:
        if ln == g.n and st.comp(s, st.a) not in K:
            adj[li[st.loop_of[s]]].add(('W', s))
        if ln < g.n and ix[s] not in nxt:
            adj[li[st.loop_of[s]]].add(('D', s))
    for ci, run in enumerate(cycles):
        for i in run:
            adj[li[st.loop_of[arcs[i][0]]]].add(('C', ci))
    return loops, adj


def max_matching(nloops, adj):
    """Kuhn's algorithm.  Returns the size of a maximum matching."""
    match = {}
    def try_k(u, seen):
        for t in adj.get(u, ()):
            if t in seen:
                continue
            seen.add(t)
            if t not in match or try_k(match[t], seen):
                match[t] = u
                return True
        return False
    return sum(try_k(u, set()) for u in range(nloops))


# ---------------------------------------------------------------------------

def gate(max_n=7):
    import census
    cache, rows = {}, []
    bad = 0
    for n, label, path in census.sources(9):
        if n not in (6, 7):
            continue
        for digits in census.read_strings(path):
            if not digits or max(digits) != n or min(digits) != 1:
                continue
            p_ = string_to_path(digits, n)
            if len(p_) != math.factorial(n):
                continue
            g = cache.setdefault(n, Gen(n))
            arcs = [tuple(a) for a in design_of(p_)]
            sl, parts = slack(g, arcs)
            bad += sl < 0
            rows.append((n, label, sl, parts, g, arcs))
    print(f"  {len(rows)} census strings (n = 6, 7): {bad} with slack < 0")
    hist = collections.Counter(r[2] for r in rows)
    print(f"  slack histogram: {dict(sorted(hist.items()))}")
    assert bad == 0, "A2 VIOLATED on a census string"
    assert set(hist) == {0}, "slack must be identically 0 on the census (that is A3)"
    return rows


def hall(rows, sample=200):
    print(f"\n--- Hall: maximum matching of loops into tokens ---")
    defic = collections.Counter()
    worst = None
    step = max(1, len(rows) // sample)
    tested = 0
    for n, label, sl, parts, g, arcs in rows[::step]:
        loops, adj = token_graph(g, arcs)
        mm = max_matching(len(loops), adj)
        d = len(loops) - mm
        defic[d] += 1
        tested += 1
        if d > 0 and worst is None:
            worst = (label, len(loops), mm, d, parts)
    print(f"  {tested} strings tested")
    print(f"  deficiency (v - matching size) histogram: {dict(sorted(defic.items()))}")
    if worst:
        print(f"  first non-saturating: {worst[0]}  v={worst[1]} matched={worst[2]} "
              f"deficiency={worst[3]}  (S,W,D,cyc,F,v)={worst[4]}")
    return defic


def search(n, iters, seed=1):
    """Stage 0: minimise the slack, hunting for a negative."""
    import random

    from gen2 import chi_from_string
    g = Gen(n)
    src = ("data/houston_872.txt" if n == 6
           else "data/n7/7_5906_derived_025c4805fc39.txt")
    digits = [int(c) for c in open(src).read() if c.isdigit()]
    chi = chi_from_string(g, string_to_path(digits, n))
    rng = random.Random(seed)
    cur = slack(g, g.arcs_of(chi))[0]
    best = cur
    print(f"  seed {os.path.basename(src)}: slack = {cur}")
    for it in range(iters):
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
        s = slack(g, g.arcs_of(chi))[0]
        if s <= cur:
            cur = s
            if s < best:
                best = s
                print(f"    it {it:>7}  slack = {s}", flush=True)
                if s < 0:
                    print("    *** A2 REFUTED ***")
                    return best
        else:
            chi[cid] = old
    print(f"  lowest slack found = {best}   (A2 says >= 0)")
    return best


def main(do_search, n, iters):
    if do_search:
        print(f"\n--- Stage 0: hunting an A2 counterexample at n = {n} ---")
        return 0 if search(n, iters) >= 0 else 1
    print("\n--- gate: the four-count slack must be 0 on the census ---")
    rows = gate()
    hall(rows)
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--search", action="store_true")
    ap.add_argument("--n", type=int, default=7)
    ap.add_argument("--iters", type=int, default=4000)
    args = ap.parse_args()
    print(__doc__.split("Usage:")[0].strip())
    sys.exit(main(args.search, args.n, args.iters))
