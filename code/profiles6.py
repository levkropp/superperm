"""The finite case list for "no n = 6 champion is split-free".

s(6) = 872 is known and a split-free walk has length 844 + E with
E = (B - 1) + Y, so a split-free champion needs E = 28, i.e.

        B + Y = 29,     B = #blocks,  Y = sum(weight - 3) over the B-1 jumps.

Write c_i for the number of blocks of length i (i = 1..5); a block is a run of
arcs joined by delta, confined to one 2-loop, so i <= n-1 = 5.  Then

        sum i*c_i = 120,        B = sum c_i.

Three further constraints, all proved elsewhere in the repo:

1. CHAIN COUNT.  A maximal om-linked chain of COMPLETE traversals sits at
   g, g.s, ..., g.s^(k-1) with s = a^(n-2)b of order n-2 = 4, so k <= 4.

   CAREFUL.  A chain is broken by ANY non-complete block, not just by a short
   one: the om step out of a block of length l is a^(l-1)b, a different group
   element for each l, so a length-4 block interrupts the s-orbit even when the
   transition into it is itself om (and (5,4) IS forced om, since 5+4 >= 2n-3).
   Hence the breakers are the B - c_5 non-complete blocks, plus the weight->=4
   jumps, plus the end of the walk:

        c_5 <= 4 * (1 + Y + (B - c_5)).

   [An earlier draft of this file used c_5 <= 4(1 + Y + c_1 + c_2 + c_3),
   counting only short blocks as breakers.  That is FALSE and it made the case
   list look far smaller than it is.  With the correct constraint the counting
   alone gives only B + Y >= 25, not 29.]

2. LOOP CAPACITY.  The c_5 complete traversals are c_5 distinct FULL loops.
   Every other loop supplies at most 4 classes and hosts at most 2 blocks (a
   proper subset of a 5-cycle has at most 2 maximal arcs), so with v loops
   entered,  120 - 5c_5 <= 4(v - c_5)  and  v <= c_5 + (B - c_5 + 1)//2 + ... ;
   both directions are checked below.

3. v <= B  (each block lies in one loop) and v >= 24 (loops hold 5 classes).

This file lists exactly the (c_1..c_5, Y, B, v) states that survive.  Each is
a case that must be killed to prove no n = 6 champion is split-free.
"""

import sys
from itertools import product

TOTAL = 120          # (n-1)! rotation classes
TARGET = 29          # B + Y for a champion


def states():
    out = []
    for c5 in range(TOTAL // 5 + 1):
        for c4 in range((TOTAL - 5 * c5) // 4 + 1):
            for c3 in range((TOTAL - 5 * c5 - 4 * c4) // 3 + 1):
                for c2 in range((TOTAL - 5 * c5 - 4 * c4 - 3 * c3) // 2 + 1):
                    c1 = TOTAL - 5 * c5 - 4 * c4 - 3 * c3 - 2 * c2
                    if c1 < 0:
                        continue
                    B = c1 + c2 + c3 + c4 + c5
                    Y = TARGET - B
                    if Y < 0:
                        continue
                    if 5 * c5 > 4 * (1 + Y + B):          # chain count
                        continue
                    # loops: c5 full ones, the rest supply <= 4 classes each
                    # and host <= 2 blocks each
                    lo_v = c5 + max(-(-(TOTAL - 5 * c5) // 4),
                                    -(-(B - c5) // 2))
                    if lo_v > B:
                        continue
                    out.append((c1, c2, c3, c4, c5, Y, B, lo_v))
    return out


if __name__ == "__main__":
    st = states()
    print(__doc__.split("This file lists")[0].strip())
    print(f"\nsurviving states with B + Y = {TARGET}: {len(st)}\n")
    print(f"{'c1':>3}{'c2':>4}{'c3':>4}{'c4':>4}{'c5':>4}"
          f"{'Y':>4}{'B':>4}{'v>=':>5}   note")
    for c1, c2, c3, c4, c5, Y, B, v in sorted(st, key=lambda r: (-r[4], r[6])):
        note = ""
        if c5 == 24:
            note = "v = 24, exact cover -- CLOSED (orbit TSPs, all >= 267)"
        print(f"{c1:>3}{c2:>4}{c3:>4}{c4:>4}{c5:>4}{Y:>4}{B:>4}{v:>5}   {note}")

    print(f"\nby c5 (= #complete traversals = #full loops):")
    from collections import Counter
    print("  ", sorted(Counter(s[4] for s in st).items()))
    print(f"\nby v lower bound: "
          f"{sorted(Counter(s[7] for s in st).items())}")
