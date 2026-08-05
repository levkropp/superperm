"""The graft: the smallest move that can add a delta-edge to an arc set.

WHY A SINGLE-CLASS MOVE CANNOT.  `gen2`'s annealer re-cuts one class at a time
and, seeded at the exact cover, never improves in 6,000 iterations.  That is not
a tuning failure -- it is forced, and the reason is the family structure.

    FAM1.  delta(end of arc) lies in the SAME family as the arc iff the arc is
           FULL.  Measured over all 720 permutations at n = 6: arc length n
           gives family shift 0 every time; lengths 1..n-1 give shifts
           uniformly spread over 1..n-1 and never 0.

    Reason: a full arc ends at sigma^(n-1)(g), and delta of that is g.a with
    a in H = <a,b>, so it stays in the coset.  A partial arc's exit is
    delta(sigma^(l-1)(g)) for l < n, which leaves H.

The exact cover is one whole family with every arc full.  So every delta-exit
stays inside the family and already lands on an arc start -- that is exactly why
its 24 components are 24 disjoint cycles (S1).  Add ONE cut anywhere: the piece
before it becomes partial, its exit leaves the family, and no loop of any other
family is entered, so the exit lands on nothing.  Measured: over all 600 single
cut additions, **delta(comps) = 0 every time** and every exit lands in families
1..5, 120 each.

    => no single-class move can ever reduce comps at the exact cover.

THE GRAFT is therefore the minimal useful move: TWO cuts, in two different
families, coordinated so that the first one's new dirty exit lands exactly on
the arc start the second one creates.

    cut class C at position k   -> new partial arc, dirty exit P
    cut class(P) at P           -> P becomes an arc start
    => the delta-edge (new arc) -> (arc at P) now exists

Champions are family-mixed -- houston 872 spreads its arc starts 50/35/10/5/20/25
over all six families -- while the exact cover is family-pure, so the distance
between them is inherently multi-class.

Usage:
  python3 code/graft.py                 # the barrier, measured from the exact cover
  python3 code/graft.py --steps 8
"""

import argparse
import collections
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import chainer                                                    # noqa: E402
from gen2 import Gen, family_chi                                  # noqa: E402


def pos_of(g):
    """permutation -> (class id, index in its ring)."""
    out = {}
    for cid, ring in enumerate(g.rings):
        for k, q in enumerate(ring):
            out[q] = (cid, k)
    return out


def grafts(g, chi, pos):
    """Every two-cut move that creates a delta-edge.

    Returns (class, cut, target class, target cut) quadruples.  The first cut
    makes an arc partial; FAM1 sends its exit out of the family, and the second
    cut turns that exit into an arc start.
    """
    st, n = g.st, g.n
    out = []
    for cid, cuts in enumerate(chi):
        ring = g.rings[cid]
        for k0 in sorted(cuts):
            for ln in range(1, n):
                k = (k0 + ln) % n
                if k in cuts:
                    continue                  # that cut already exists
                end = ring[(k0 + ln - 1) % n]
                tc, tk = pos[st.delta(end)]
                if tc == cid or tk in chi[tc]:
                    continue                  # already an arc start: no gain
                out.append((cid, k, tc, tk))
    return out


def landings(g, chi, pos):
    """One-cut moves: cut exactly where an EXISTING dirty exit already points.

    A graft costs two splits per delta-edge.  Champions cannot afford that --
    houston 872 buys 20 components' worth of merging with only 25 splits, i.e.
    1.25 splits per edge.  The cheaper move exists as soon as partial arcs do:
    if a partial arc's exit `delta(end)` is not yet an arc start, cutting there
    creates the edge for ONE split.  The exact cover has no partial arcs, which
    is why it needs a graft to bootstrap; every state after that has landings.

    Returns (target class, target cut) pairs.
    """
    st = g.st
    out = set()
    for a in g.arcs_of(chi):
        if a[1] == g.n:
            continue                              # full arc: exit is in-family
        x = a[0]
        for _ in range(a[1] - 1):
            x = st.sig(x)
        tc, tk = pos[st.delta(x)]
        if tk not in chi[tc]:
            out.add((tc, tk))
    return sorted(out)


def edge_map(g, chi):
    """(arc starts, ends by start, set of starts that HAVE an in-edge)."""
    st = g.st
    arcs = g.arcs_of(chi)
    starts = {a[0] for a in arcs}
    ends, has_in = {}, set()
    for a in arcs:
        x = a[0]
        for _ in range(a[1] - 1):
            x = st.sig(x)
        ends[a[0]] = x
    for s, e in ends.items():
        t = st.delta(e)
        if t in starts:
            has_in.add(t)
    return starts, ends, has_in


def prunes(g, chi, pos):
    """Cuts whose removal destroys no delta-edge -- so `S` AND `comps` both drop.

    Removing the cut at `P` merges the arc ending just before `P` with the arc
    starting at `P`: `R` falls by one.  Two edges can be lost by that merge --
    the in-edge of `P`, and the out-edge of the arc that ended just before it.
    If NEITHER exists the edge count is unchanged, so

        Delta(comps) = Delta(R) - Delta(e) = -1,   Delta(S) = -1

    and `T = S + comps + Y` falls by **2**.  A cut like that is pure waste, and
    an optimum can have none -- which is the assertion in `main`.
    """
    st, n = g.st, g.n
    starts, ends, has_in = edge_map(g, chi)
    out = []
    for cid, cuts in enumerate(chi):
        if len(cuts) < 2:
            continue
        ring, ks = g.rings[cid], sorted(cuts)
        for k in ks:
            if ring[k] in has_in:
                continue                       # something points at it
            prev = max(ks, key=lambda j: (k - j) % n if j != k else -1)
            if st.delta(ring[(k - 1) % n]) in starts:
                continue                       # the merge would kill an edge
            assert prev != k
            out.append((cid, k))
    return out


def apply_prune(chi, mv):
    cid, k = mv
    out = [set(c) for c in chi]
    out[cid].discard(k)
    return out


def apply_cuts(chi, cuts):
    out = [set(c) for c in chi]
    for cid, k in cuts:
        out[cid].add(k)
    return out


def apply_graft(chi, mv):
    cid, k, tc, tk = mv
    return apply_cuts(chi, [(cid, k), (tc, tk)])


def price(g, chi, exact=True):
    arcs = g.arcs_of(chi)
    S = len(arcs) - g.F1
    comps, ends = g.components(arcs)
    opts = g.options(arcs, comps, ends)
    if not exact:
        return S + len(comps) + chainer.lower_bound(opts), S, len(comps), None
    Y, _, _ = chainer.solve(opts)
    return S + len(comps) + Y, S, len(comps), Y


def descend(g, steps, shortlist=40, quiet=False):
    """Greedy graft descent, shortlisted cheaply and then priced exactly.

    Two earlier keys both failed, for instructive reasons:

      * `S + comps` walks the WRONG WAY.  The champion has the higher
        `S + comps` of the two (29 against the exact cover's 24) and wins
        entirely on Y, so ignoring Y heads back toward the exact cover.
      * `S + comps + lower_bound` has the right direction but is far too loose
        here: `Y >= p - 1` counts the joins and not their cost, and the grafts
        this picks leave components whose joins cost ~2.2 each -- at `comps = 7`
        the bound reads 6 against a true Y of 13.

    Only the exact Y separates a good graft from a bad one, and it is too slow
    for all ~600 candidates.  So: shortlist on the cheap bound, price the top
    `shortlist` exactly, take the best true T.
    """
    pos = pos_of(g)
    chi = family_chi(g, 0)
    T, S, C, Y = price(g, chi)
    print(f"  start (exact cover)   T={T}  S={S} comps={C} Y={Y}")
    for step in range(steps):
        land = [[c] for c in landings(g, chi, pos)]
        graf = [[(m[0], m[1]), (m[2], m[3])] for m in grafts(g, chi, pos)]
        cand = land + graf                # one-cut moves first: half the price
        if not cand:
            print("    no move available")
            break
        rough = []
        for mv in cand:
            arcs = g.arcs_of(apply_cuts(chi, mv))
            comps, ends = g.components(arcs)
            lb = chainer.cheap_bound(g.options(arcs, comps, ends))
            rough.append(((len(arcs) - g.F1) + len(comps) + lb, len(mv), mv))
        rough.sort(key=lambda x: (x[0], x[1]))

        best = None
        for _, _, mv in rough[:shortlist]:
            c2 = apply_cuts(chi, mv)
            t, s, c, y = price(g, c2)
            if best is None or (t, c) < (best[0], best[2]):
                best, best_chi, best_mv = (t, s, c, y), c2, mv
        chi = best_chi
        T, S, C, Y = best
        if not quiet:
            kind = "land " if len(best_mv) == 1 else "graft"
            print(f"    step {step+1:>3}: {len(land):>4} land / {len(graf):>4} "
                  f"graft   took {kind}   T={T}  S={S} comps={C} Y={Y}",
                  flush=True)
    return chi, T


def main(steps, shortlist=40):
    g = Gen(6)
    print("\n--- single-class moves at the exact cover ---")
    pos = pos_of(g)
    chi = family_chi(g, 0)
    base_comps = len(g.components(g.arcs_of(chi))[0])
    hist = collections.Counter()
    for cid, cuts in enumerate(chi):
        for k in range(g.n):
            if k in cuts:
                continue
            c2 = [set(x) for x in chi]
            c2[cid].add(k)
            hist[len(g.components(g.arcs_of(c2))[0]) - base_comps] += 1
    print(f"  delta(comps) over {sum(hist.values())} single cut additions: "
          f"{dict(sorted(hist.items()))}")
    assert set(hist) == {0}, "a single cut merged components -- FAM1 is wrong"
    print("  => none of them creates an edge, exactly as FAM1 predicts")

    print("\n--- prunes: cuts whose removal destroys no edge ---")
    from gen2 import chi_from_string
    from permgraph import string_to_path
    d = [int(c) for c in open("data/houston_872.txt").read() if c.isdigit()]
    champ = chi_from_string(g, string_to_path(d, g.n))
    T, S, C, Y = price(g, champ)
    npr = len(prunes(g, champ, pos))
    print(f"  houston 872 (optimum): T={T} S={S} comps={C} Y={Y}   "
          f"prunes = {npr}")
    assert npr == 0, "an optimum has a pruneable cut -- T would drop by 2"
    print("  => none, as an optimum must have.  But see the note: EVERY cut "
          "removal is\n     non-increasing in S + comps, which is the A3 wall "
          "showing up in the move set.")

    print(f"\n--- grafts (two coordinated cuts) ---")
    print(f"  {len(grafts(g, chi, pos))} available at the exact cover")
    descend(g, steps, shortlist)
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--steps", type=int, default=6)
    ap.add_argument("--shortlist", type=int, default=40)
    args = ap.parse_args()
    print(__doc__.split("Usage:")[0].strip())
    sys.exit(main(args.steps, args.shortlist))
