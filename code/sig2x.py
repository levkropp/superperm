"""The sigma^2 exchange: why the optimum can always be taken with sigma2 = 0.

`IN5` (`B >= comps`, hence `T >= S + comps`) is false because a weight-2 jump
has two targets, `delta(u)` and `sigma^2(u)`, and `comps` follows only the first
(see `code/inflate.py` and `notes/ordering.md`).  Losing it costs the repo its
only ordering-free lower bound.  This file gets it back.

THE MOVE.  Suppose arc `A_p` ends at `e` and the walk jumps `sigma^2` to
`A_{p+1}` starting at `sigma^2(e)`.  By SIG2 there is a LENGTH-1 arc `A_q` at
`sigma(e)`, sitting somewhere else in the walk.  In the ring of the class those
three arcs are consecutive:

    [ A_p .... e ] [ sigma(e) ] [ sigma^2(e) .... A_{p+1} ]

so splicing `A_q` out of its own position and letting the walk run straight
through merges all three into ONE arc.  Write `X, Z` for the arcs that flanked
`A_q`, and `w1 = w(X, sigma(e))`, `w2 = w(sigma(e), Z)`.  Then

    R' = R - 2                       three arcs became one
    length' - length = w(X,Z) - w1 - w2   <= 0

because weight is subadditive: the string `X -> sigma(e) -> Z` is a witness of
length `w1 + w2` for joining `X` to `Z`.  The merged arc fits, since `A_p`,
`A_q`, `A_{p+1}` are disjoint segments of one n-element ring.

THE CONSEQUENCE.  `R` strictly drops by 2 and is bounded below by `(n-1)!`, so
iterating terminates, at a walk with no `sigma^2` jump and no greater length:

    every superpermutation has one of length <= it with sigma2 = 0.

Hence the MINIMUM is attained at `sigma2 = 0`, where `IN5` does hold, and

    min length  >=  base(n) + min over arc sets K of ( S(K) + comps(K) )

is valid again -- as a bound on the optimum, which is the only place it was
ever used.

AT AN OPTIMUM the exchange must be free, `w(X,Z) = w1 + w2`, and then it pays
for itself in the other coordinates: two jumps `w1, w2 >= 2` become one of
weight `>= 4`, so

    SIG2Y   an optimum with sigma2 = k implies an optimum with Y >= k and
            B >= B + k.

Both witnesses below hit exactly this: `w1 = w2 = 2`, `w(X,Z) = 4`, length
unchanged, `Y` and `B` each up by one.  So a `sigma^2`-using optimum can only be
reached from a `sigma2 = 0` optimum by *reversing* the move, which consumes a
jump of weight `>= 4` -- and there are at most `Y` of those.

That makes the question decidable over the known corpus, and `--corpus` decides
it: of the 43,096 n = 6 optima, **808 carry a weight->=4 jump and not one of
them admits a free reverse exchange**.  So the known 872 set is closed under the
move in both directions.  Note that length-1 arcs are NOT the obstruction --
`872-nonstandard` has 8 and 20 of the n = 7 champions have 1..12; the
obstruction is that the heavy jump never splits at a permutation interior to an
arc.

Usage:
  python3 code/sig2x.py
  python3 code/sig2x.py --corpus
  python3 code/sig2x.py --n 7 --src data/n7/5908-egan.txt
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from build import canonical, coords, to_string                    # noqa: E402
from gen2 import Gen                                              # noqa: E402
from inflate import (EGAN6, arcs_from_starts, ends_of,            # noqa: E402
                     load_design, sane, sigma2_jumps)
from permgraph import is_superpermutation, weight                 # noqa: E402
from superstruct import Struct                                    # noqa: E402

KEYS = ["length", "R", "T", "S", "A", "B", "Y", "comps"]


def exchange(design, n, st):
    """Apply one sigma^2 exchange.  Returns (new design, w1, w2, w_direct)."""
    js = sigma2_jumps(design, st)
    if not js:
        return None
    p = js[0]
    E = ends_of(design, st)
    e = E[p]
    m = st.sig(e)
    q = next(i for i, a in enumerate(design) if a == (m, 1))
    assert q not in (p, p + 1), "the singleton cannot be its own neighbour"

    merged = (design[p][0], design[p][1] + 1 + design[p + 1][1])
    assert merged[1] <= n, ("the three arcs do not fit one ring", merged)

    # the jumps that vanish when A_q is spliced out
    w1 = weight(E[q - 1], m) if q > 0 else None
    w2 = weight(m, design[q + 1][0]) if q + 1 < len(design) else None

    out = []
    for i, a in enumerate(design):
        if i == q or i == p + 1:
            continue
        out.append(merged if i == p else a)

    # the join that replaces them
    if w1 is None:
        wd = 0                     # A_q was the first arc: its exit just goes
    elif w2 is None:
        wd = 0                     # A_q was the last arc: its entry just goes
    else:
        nq = out.index(design[q + 1]) if design[q + 1] in out else None
        wd = weight(E[q - 1], design[q + 1][0]) if nq is not None else None
    return canonical(out, n), w1, w2, wd


def reverse_slots(design, n, st):
    """Zero-cost ways to CREATE a sigma^2 jump: the exchange run backwards.

    Split an arc of length >= 3 into (piece, singleton, piece) -- the two pieces
    are then joined by a sigma^2 jump at no cost, since two sigma steps and a
    weight-2 jump both cost two characters -- and re-insert the singleton `m`
    between some adjacent pair `X, Z`.  That is free exactly when
    `w(X,m) + w(m,Z) = w(X,Z)`, which needs `w(X,Z) >= 4`; there are at most `Y`
    such jumps in the walk.
    """
    E = ends_of(design, st)
    heavy = [j for j in range(len(design) - 1)
             if weight(E[j], design[j + 1][0]) >= 4]
    out = []
    for j in heavy:
        X, Z = E[j], design[j + 1][0]
        wd = weight(X, Z)
        for i, (g, L) in enumerate(design):
            if L < 3 or i == j:
                continue
            m = g
            for a in range(1, L - 1):
                m = st.sig(m)
                w1, w2 = weight(X, m), weight(m, Z)
                if w1 >= 2 and w2 >= 2 and w1 + w2 == wd:
                    out.append((i, L, a, j, w1, w2, wd))
    return out, len(heavy)


def scan_optima():
    """Can any known n = 6 optimum be pushed into using a sigma^2 jump?"""
    import champions6
    from build import design_of
    from permgraph import string_to_path
    st = Struct(6)
    heavy_strings = slots = total = 0
    for _, digits in champions6.strings():
        total += 1
        des = design_of(string_to_path(digits, 6))
        found, nheavy = reverse_slots(des, 6, st)
        if nheavy:
            heavy_strings += 1
        slots += len(found)
    return total, heavy_strings, slots


def report(tag, design, n, st):
    c = coords(design, n)
    c["sigma2"] = len(sigma2_jumps(design, st))
    print(f"  {tag:<12} " + "  ".join(f"{k}={c[k]}" for k in KEYS)
          + f"  sigma2={c['sigma2']}")
    return c


def witnesses(src, n, st, g, want):
    """Walks that actually take a sigma^2 jump, built by enlarging Egan's K."""
    design = load_design(src, n)
    entered = {st.loop_of[a[0]] for a in design}
    base = {a[0] for a in design}
    out = []
    for lid in range(len(st.loop_gens)):
        if lid in entered:
            continue
        arcs = arcs_from_starts(base | set(st.loop_gens[lid]), st, n)
        comps, ends = g.components(arcs)
        _, order, rots = g.chain(arcs, comps, ends)
        des = g.design(arcs, comps, order, rots)
        if not sane(des, n, st) or not sigma2_jumps(des, st):
            continue
        out.append((lid, des))
        if len(out) >= want:
            break
    return out


def main(src, n, want):
    st, g = Struct(n), Gen(n)
    print(f"\n=== n = {n}, seeded from {os.path.basename(src)} ===")
    cases = witnesses(src, n, st, g, want)
    if not cases:
        print("  no sigma^2 witness found from this seed")
        return 0
    deltas = []
    for lid, des in cases:
        print(f"\n  --- witness: +loop {lid} ---")
        before = report("before", des, n, st)
        assert is_superpermutation(to_string(des, n), n)
        cur, steps = des, 0
        while sigma2_jumps(cur, st):
            nxt, w1, w2, wd = exchange(cur, n, st)
            steps += 1
            c0, c1 = coords(cur, n), coords(nxt, n)
            d = c1["length"] - c0["length"]
            deltas.append(d)
            print(f"    step {steps}: w1={w1} w2={w2} w(X,Z)={wd}  "
                  f"R {c0['R']} -> {c1['R']}   length {d:+d}   "
                  f"Y {c0['Y']} -> {c1['Y']}   B {c0['B']} -> {c1['B']}")
            assert c1["R"] <= c0["R"] - 2, "R must drop by at least 2"
            assert d <= 0, f"length rose by {d}: the exchange is not free"
            if d == 0:                                   # SIG2Y
                assert c1["Y"] > c0["Y"] and c1["B"] > c0["B"], \
                    "a free exchange must pay in Y and B"
            cur = nxt
        after = report("after", cur, n, st)
        assert is_superpermutation(to_string(cur, n), n), "exchange broke it"
        assert after["sigma2"] == 0
        assert after["length"] <= before["length"]
        assert after["T"] >= after["S"] + after["comps"], "IN5 must hold now"
        print(f"    => sigma2 0, length {before['length']} -> "
              f"{after['length']}, and T >= S + comps holds again "
              f"({after['T']} >= {after['S']} + {after['comps']})")
    print(f"\n  {len(deltas)} exchanges, length changes: "
          f"{sorted(set(deltas))}")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=None)
    ap.add_argument("--n", type=int, default=None)
    ap.add_argument("--want", type=int, default=3)
    ap.add_argument("--corpus", action="store_true")
    args = ap.parse_args()
    print(__doc__.split("Usage:")[0].strip())
    pairs = ([(args.src, args.n)] if args.src
             else [(EGAN6, 6), ("data/n7/5908-egan.txt", 7)])
    rc = 0
    for s, k in pairs:
        rc |= main(s, k, args.want)
    if args.corpus:
        print("\n=== can any known n = 6 optimum be pushed into a sigma^2 "
              "jump? ===")
        total, heavy, slots = scan_optima()
        print(f"  {total} optima, {heavy} carry a weight->=4 jump, "
              f"{slots} free reverse-exchange slots")
        assert slots == 0, "found one -- the corpus fact is selection bias"
        print("  => none.  The known 872 set is closed under the exchange in "
              "BOTH directions.")
    sys.exit(rc)
