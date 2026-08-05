"""The Coset Lemma: an om-stretch can enter at most (n-2)! two-loops.

A run of length l whose exit is om advances the next run's start by right
multiplication by  a^(l-1) b.  Every such element lies in

        H := <a, b>,

so a maximal OM-STRETCH -- a maximal stretch of consecutive runs all of whose
transitions are om -- has all of its generators inside a single right coset
g.H.  This file computes H and reads off the consequence.  At n = 7:

    |H| = 720 = 5040/7, and it contains a, so it is a union of 120 complete
    2-loops.  Its order is coprime to 7 = |<c>|, and the rotation classes are
    exactly the left cosets of <c>, so H meets EVERY ONE of the 720 classes
    exactly once -- and so does every right coset g.H.

Two consequences, both sharp:

  (1) inside an om-stretch the runs' rotation classes are automatically
      distinct: the coset is a transversal of the classes;

  (2) an om-stretch enters at most |H| / (n-1) = (n-2)! = 120 distinct
      2-loops, because that is all the coset contains.

WHEN IS A TRANSITION FORCED ONTO OM?  Not as often as an earlier version of
this file claimed.  Reading the exit table (exit_table.py), a weight-3 jump
from a run of length l to a run of length l' needs an exit whose cap is >= l',
and the number of such exits is computed below.  It is unique -- hence om --
exactly when

        l + l' >= 2n - 3 ,      at n = 7:  (6,6), (6,5), (5,6).

*** CORRECTION.  (5,5) is NOT forced.  The l = 5 row is [0,0,4,5,5,6]: two of
its exits have cap 5, so a run of length n-2 may be followed by another run of
length n-2 without using om.  An earlier version of this file asserted that
any jump between two runs of length >= n-2 is om, and concluded that a
split-free state with all runs of length >= n-2 and Y = 0 is a single
om-stretch with v <= (n-2)!.  That conclusion is withdrawn in general, and so
is the ladder bound v <= (n-2)!*(1 + 2m + Y) derived from it.

What survives, unchanged:
  * all of the group theory above, and the family/collision arithmetic at the
    bottom of this file -- those never used the om-forcing claim;
  * the argument in split_free_5889.py, whose counting independently forces
    the length-5 runs to be ISOLATED, so no (5,5) transition occurs there;
    that state really is a single om-stretch and the Coset Lemma kills it
    (v <= 120 < 124) more cleanly than the period map does.

The correct general rule is

        #om-stretches  <=  1 + Y + #(adjacent run pairs with l + l' <= 2n-4)

and hence  v <= (n-2)! * #om-stretches.
"""

import math
from itertools import permutations

import sys
sys.path.insert(0, "code")
from pentad_orbits import (a, b, s, comp, ident, order, apow,   # noqa: E402
                           onecycle, inv, n)


def closure(gens):
    seen, frontier = {ident}, [ident]
    while frontier:
        nxt = []
        for x in frontier:
            for g in gens:
                y = comp(x, g)
                if y not in seen:
                    seen.add(y)
                    nxt.append(y)
        frontier = nxt
    return seen


if __name__ == "__main__":
    print(__doc__.split("This file computes")[0].strip())

    u = comp(apow[n - 3], b)
    print(f"\ns = a^{n-2}.b  ord {order(s)}     u = a^{n-3}.b  ord {order(u)}")

    H = closure([s, u])
    F1, F2 = math.factorial(n - 1), math.factorial(n - 2)
    print(f"|<s,u>| = {len(H)}   (|S_{n}| = {math.factorial(n)}, "
          f"index {math.factorial(n) // len(H)})")
    assert len(H) == F1, "expected order (n-1)!"

    # it contains a, hence is a union of complete 2-loops
    assert a in H, "a must lie in <s,u>"
    loops = {frozenset(comp(h, p) for p in apow) for h in H}
    print(f"a in <s,u>: True  =>  it is a union of {len(loops)} complete "
          f"2-loops  ({len(H)} / {n-1})")
    assert len(loops) == F2

    # order coprime to n  =>  meets every rotation class exactly once
    print(f"gcd(|<s,u>|, {n}) = {math.gcd(len(H), n)}  =>  <s,u> is a "
          f"transversal of the {F1} rotation classes")
    hit = {}
    for h in H:
        hit.setdefault(onecycle(h), []).append(h)
    assert len(hit) == F1 and all(len(x) == 1 for x in hit.values())
    print(f"verified: <s,u> meets each of the {F1} classes exactly once")

    # ... and so does every right coset
    print("\nchecking all right cosets g.<s,u> are class transversals too")
    reps, seen = [], set()
    for g in permutations(range(1, n + 1)):
        if g in seen:
            continue
        cos = {comp(g, h) for h in H}
        seen |= cos
        reps.append(g)
        cl = {onecycle(x) for x in cos}
        assert len(cl) == F1, "coset is not a class transversal"
        lp = {frozenset(comp(x, p) for p in apow) for x in cos}
        assert len(lp) == F2
    print(f"  all {len(reps)} right cosets: each meets every class exactly "
          f"once and holds exactly {F2} loops   OK")

    # ---- WHEN is a weight-3 transition forced onto om? --------------------
    from pentad_orbits import exits                             # noqa: E402
    print("\n--- how many weight-3 exits of a length-l run reach a length-l' "
          "run? ---")
    rows = {l: exits(ident, l) for l in range(1, n)}
    b_mult = {}
    print("    l\\l'  " + "".join(f"{lp:>5}" for lp in range(1, n)))
    for l in range(1, n):
        cells = []
        for lp in range(1, n):
            ok = [mu for mu, cap in rows[l] if cap >= lp]
            cells.append(f"{len(ok):>5}")
            if len(ok) == 1:
                b_mult[(l, lp)] = ok[0]
        print(f"    {l:<6}" + "".join(cells))
    forced = sorted(b_mult)
    print(f"  forced onto a single exit: {forced}")
    assert all(b_mult[k] == b for k in forced), "the forced exit must be om"
    thresh = min(l + lp for l, lp in forced)
    assert forced == [(l, lp) for l in range(1, n) for lp in range(1, n)
                      if l + lp >= thresh], "forced set is not a threshold set"
    print(f"  i.e. exactly when l + l' >= {thresh} = 2n-3   "
          f"-- and ({n-2},{n-2}) is NOT forced")
    assert (n - 2, n - 2) not in b_mult

    # ---- the 7 families, and what it costs to mix them -------------------
    print("\n--- the 7 loop families and cross-family class collisions ---")
    cid = {}
    for p in permutations(range(1, n + 1)):
        c = onecycle(p)
        if c not in cid:
            cid[c] = len(cid)
    fams = []
    for g in reps:
        lp = {}
        for h in H:
            x = comp(g, h)
            key = frozenset(comp(x, p) for p in apow)
            lp.setdefault(key, frozenset(cid[onecycle(y)] for y in key))
        fams.append(list(lp.values()))
    assert all(len(f) == F2 for f in fams)
    for f in fams:
        assert len(set().union(*f)) == F1
        assert all(not (x & y) for i, x in enumerate(f) for y in f[i + 1:])
    print(f"  {len(fams)} families of {F2} loops; each family's loops are "
          f"pairwise class-disjoint and cover all {F1} classes")

    from collections import Counter
    c01 = Counter(len(x & y) for x in fams[0] for y in fams[1])
    print(f"  cross-family loop overlaps (family 0 vs 1): {dict(sorted(c01.items()))}")
    tot = Counter()
    for L in fams[1]:
        tot[sum(len(L & y) for y in fams[0])] += 1
    print(f"  class-slots a single foreign loop shares with a FULL family: "
          f"{dict(tot)}")
    assert set(tot) == {n - 1}, "a foreign loop must collide exactly n-1 times"
    print(f"""  -- forced, and worth stating: a loop L outside a family has its
     {n-1} classes covered exactly once each BY that family, so L collides
     with a full family in exactly {n-1} class-slots (spread over 5 loops:
     four sharing one class, one sharing two).""")

    print(f"""
COSET LEMMA (n = {n}).  The starting generators of an om-stretch lie in one
right coset of <s,u>.  That coset contains exactly {F2} two-loops and meets
each of the {F1} rotation classes exactly once.  Therefore

    * the runs of an om-stretch are automatically class-disjoint, and
    * an om-stretch enters at most {F2} distinct 2-loops.

COROLLARY (corrected).  A stretch of runs whose consecutive length pairs all
satisfy l + l' >= {2*n-3} is a single om-stretch, hence enters at most {F2}
two-loops.  In particular a split-free state whose runs have lengths in
{{{n-2}, {n-1}}} and in which NO two runs of length {n-2} are adjacent is one
om-stretch, so v <= {F2}.  That is exactly the configuration
split_free_5889.py forces at v = 124, which the lemma therefore kills.

NOT a corollary: dropping the non-adjacency condition.  ({n-2},{n-2}) is not
forced onto om, so a state with adjacent length-{n-2} runs may break into many
om-stretches.  The general bound is

    #om-stretches <= 1 + Y + #(adjacent pairs with l + l' <= {2*n-4}),
    v <= {F2} * #om-stretches.""")
