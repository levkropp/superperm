"""Split-free superpermutations at n = 7:  length >= 5888, and >= 5895 at v=120.

SUPERSEDED for the global bound by code/split_free_5889.py, which gets 5889
without mentioning v at all (see notes/block_count_lemma.md).  Kept because
the per-rung table below is still the right picture of where the difficulty
sits: rungs v = 123 and v = 124 are the two that stop the ladder one short.

A walk is SPLIT-FREE if no rotation class is covered by more than one arc,
i.e. R = 720.  Equivalently (split identity R = 6v - A) it has A = 6(v-120):
every class is a single full 7-permutation arc, and the whole walk is 720
full arcs joined by 719 jumps.  The v = 120 rung is the special case A = 0.

In that world the accounting closes completely and by hand-free search:

  * the arc starts are 720 permutations, one per class; each generates
    exactly one 2-loop, so loop L is hit m_L in 1..6 times and
        sum m_L = 720,   v = #{L hit},   A = sum (6 - m_L) = 6v - 720.
  * the only weight-2 jump available is delta (sigma^2 needs a split), and
    delta out of a full arc at generator g lands on g.a -- the next generator
    of the SAME loop.  So a BLOCK (maximal cheap run) sits inside one loop
    and occupies consecutive generator positions: length <= 6.
  * a block of length 6 is a complete traversal; the PENTAD LEMMA
    (notes/pentad_lemma.md) caps chains of them at five.

Writing B for the number of blocks and f for the number of complete
traversals,  length = 5765 + E  with  E = (B-1) + Y, and this file minimises
that over every integer state the structure permits.  The answer:

        v = 120        length >= 5895
        v = 121        length >= 5893
        v = 122        length >= 5891
        v = 123..124   length >= 5888
        v >= 125       length >= 5889   (B >= v alone)

so split-free strings obey s(7) >= 5888 -- an elementary, cover-independent
re-derivation of the Hunter-Raudvere bound on this slice -- and the two rungs
that stop it one short are v = 123 and v = 124.
"""

CEIL = lambda p, q: -(-p // q)


def min_excess(v, verbose=False):
    """Minimum E = (B-1) + Y over split-free states with this many loops."""
    A = 6 * v - 720                      # forced: R = 720 = 6v - A
    if A < 0:
        return None
    best, arg = None, None
    # f  = loops traversed complete (m=6, one block)
    # v6 = loops hit 6 times but broken into >= 2 blocks
    # vl = loops hit m <= 5 times            (>= 1 block each)
    for f in range(0, 121):
        for vl in range(0, v - f + 1):
            v6 = v - f - vl
            if v6 < 0:
                continue
            # A is spread over the vl short loops, 1..5 missing generators each
            if not (vl <= A <= 5 * vl) and not (A == 0 and vl == 0):
                continue
            if 6 * f + 6 * v6 + (6 * vl - A) != 720:
                continue
            B = f + 2 * v6 + vl           # smallest block count consistent
            # Pentad: the f complete traversals sit in at most (B-f)+1 maximal
            # runs; each run splits into om-stretches of at most five, and
            # every break costs a jump of weight >= 4, i.e. +1 of Y.
            Y = max(0, CEIL(f, 5) - (B - f) - 1)
            E = (B - 1) + Y
            if best is None or E < best:
                best, arg = E, (f, v6, vl, B, Y)
    if verbose:
        print(f"  v={v:4} A={A:3}  worst state (f,v6,vl,B,Y)={arg}  E>={best}"
              f"  length>={5765 + best}")
    return best


if __name__ == "__main__":
    print(__doc__.split("In that world")[0].strip())
    print("\n--- minimum over every split-free state ---")
    worst = None
    for v in range(120, 132):
        e = min_excess(v, verbose=True)
        L = 5765 + e
        worst = L if worst is None else min(worst, L)
    print(f"\nsplit-free lower bound over all v : {worst}")
    assert min_excess(120) == 130, "v=120 must reproduce the Pentad rung"
    assert worst == 5888
    print("v = 120 reproduces notes/pentad_lemma.md exactly (E >= 130).")
    print("Split-free s(7) >= 5888.  Short of 5889 only at v = 123 and 124.")
