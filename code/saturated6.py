"""Does Family Quantisation survive collisions?

THE TARGET.  The single cheapest open +1 on s(7) is the v = 121, A = 0 state
(code/loop_runs.py): every other rung already gives T >= 122, and this one
gives exactly 121.  A = (n-1)v - R = 0 means every entered loop is FULLY
traversed, so the state is a set of 121 loops whose class-sets cover all 720
rotation classes with total multiplicity 726 -- an exact cover with exactly
S = 6 COLLISIONS.

THE HOOK.  Family Quantisation (code/quantise.py) says an EXACT cover takes a
multiple of n-2 loops from each family.  If that survived collisions, v = 121
would be impossible outright: 121 is not a multiple of n-2 = 5.

But it cannot survive arbitrarily many: jupiter (5907) has A = 0, v = 140 and
families (61, 41, 26, 9, 3), none a multiple of 5 -- with S = 120 collisions.
So the question is quantitative: HOW MANY collisions does quantisation tolerate?

n = 6 is enumerable, so ask it there.  Define a SATURATED SYSTEM of size v: a
set of v two-loops whose 5-element class-sets cover all 120 classes, with total
multiplicity 5v, i.e. exactly S = 5v - 120 collisions.  v = 24 is an exact
cover (S = 0) and quantisation holds.  This file walks v = 24, 25, 26 and
reports the per-family loop counts mod n-2 = 4.

The n = 7 state of interest is the analogue at v = 121, S = 6; its n = 6
counterpart is v = 25, S = 5.
"""

import sys
from collections import Counter

sys.path.insert(0, "code")
from quantise import setup                                      # noqa: E402


def saturated(n, v, cls_of, cap=200000):
    """All size-v saturated systems, as tuples of loop ids."""
    classes = sorted({c for cs in cls_of for c in cs})
    cix = {c: i for i, c in enumerate(classes)}
    NC = len(classes)
    masks = [sum(1 << cix[c] for c in cs) for cs in cls_of]
    FULL = (1 << NC) - 1
    per = n - 1                       # classes per loop
    slack = per * v - NC              # collisions allowed

    by_class = {}
    for i, m in enumerate(masks):
        for c in range(NC):
            if m >> c & 1:
                by_class.setdefault(c, []).append(i)

    out = []
    inuse = [False] * len(masks)

    def rec(cov, used, excess, last):
        if len(out) >= cap:
            return
        if len(used) == v:
            if cov == FULL:
                out.append(tuple(used))
            return
        # every remaining loop adds at most `per` new classes
        missing = NC - bin(cov).count("1")
        if missing > per * (v - len(used)):
            return
        low = (~cov) & FULL
        if low == 0:
            # everything covered but loops still to place: they may be any
            # unused loops, all of whose classes collide
            for i in range(last + 1, len(masks)):
                if inuse[i]:
                    continue
                e = excess + per
                if e > slack:
                    continue
                used.append(i); inuse[i] = True
                rec(cov, used, e, i)
                used.pop(); inuse[i] = False
                if len(out) >= cap:
                    return
            return
        c = (low & -low).bit_length() - 1
        for i in by_class[c]:
            if inuse[i]:
                continue
            new = bin(masks[i] & ~cov).count("1")
            e = excess + (per - new)
            if e > slack:
                continue
            used.append(i); inuse[i] = True
            rec(cov | masks[i], used, e, i)
            used.pop(); inuse[i] = False
            if len(out) >= cap:
                return

    rec(0, [], 0, -1)
    return out, slack


if __name__ == "__main__":
    print(__doc__.split("THE TARGET")[0].strip())
    n = 6
    loops, fam_of, cls_of = setup(n)
    q = n - 2
    print(f"\nn = {n}: {len(loops)} loops, {n} families of {len(loops)//n}, "
          f"quantum n-2 = {q}\n")
    print(f"{'v':>4}{'S':>4}{'systems':>10}   per-family counts mod "
          f"{q}: all zero?")
    for v in (24, 25, 26):
        systems, slack = saturated(n, v, cls_of)
        if not systems:
            print(f"{v:>4}{slack:>4}{0:>10}   (none)")
            continue
        allz = True
        residues = Counter()
        for sysm in systems:
            c = Counter(fam_of[i] for i in sysm)
            r = tuple(sorted(x % q for x in c.values()))
            residues[r] += 1
            if any(x % q for x in c.values()):
                allz = False
        print(f"{v:>4}{slack:>4}{len(systems):>10}   {allz}")
        for r, k in residues.most_common(4):
            print(f"                        residues {str(r):22} x{k}")
    print("\nv = 24 is the exact-cover case, where quantisation is proved "
          "exhaustively.")
    print("v = 25 (S = 5) is the n = 6 analogue of the n = 7 v = 121, S = 6 "
          "state.")
