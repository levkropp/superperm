"""FAMILY QUANTISATION: an exact cover takes loops from each family in
multiples of n-2.

Setting (code/families6.py).  The arc-to-arc delta step is right multiplication
by a = c^(n-1)d, so a 2-loop is a coset g<a> and the n!/(n-1) loops fall into
the n cosets of H = <a,b>, the FAMILIES.  Each family has (n-2)! loops and is
an exact cover of the (n-1)! rotation classes.

A split-free walk with B = (n-2)! -- every block a complete traversal -- picks
(n-2)! pairwise class-disjoint loops, an EXACT COVER.  Such a cover need not
lie in one family; at n = 6 the 10068 covers spread over 1 to 6 families.  But
they do not spread freely:

    CONJECTURE (Family Quantisation).  In every exact cover of the (n-1)!
    classes by (n-2)! two-loops, the number of loops taken from each family is
    divisible by n-2 -- equivalently each family supplies a multiple of
    (n-1)(n-2) classes.

n-2 is exactly ord(s) for s = a^(n-2)b, the element whose orbits are the
Pentads.  This file enumerates ALL exact covers at n = 4, 5, 6 and checks it.
At n = 6 the 10068 covers reduce to 29 relabelling orbits, and S_n permutes the
families, so the multiset of per-family counts is an orbit invariant -- the 29
representatives settle all 10068.
"""

import sys
from collections import Counter
from itertools import permutations

sys.path.insert(0, "code")


def setup(n):
    ident = tuple(range(1, n + 1))
    sig = lambda u: u[1:] + u[:1]
    delta = lambda u: u[2:] + (u[1], u[0])
    comp = lambda u, v: tuple(u[v[i] - 1] for i in range(n))
    cid = lambda u: min(u[k:] + u[:k] for k in range(n))

    a = ident
    for _ in range(n - 1):
        a = comp(a, sig(ident))
    a = comp(a, delta(ident))
    b = tuple(list(range(3, n)) + [2, 1, n])

    def closure(gs):
        seen, fr = {ident}, [ident]
        while fr:
            x = fr.pop()
            for g in gs:
                y = comp(x, g)
                if y not in seen:
                    seen.add(y)
                    fr.append(y)
        return seen

    perms = list(permutations(range(1, n + 1)))
    A, H = closure((a,)), closure((a, b))
    assert len(A) == n - 1 and len(H) * n == len(perms)

    lid, loops = {}, []
    fid = {}
    fam_of, cls_of = [], []
    for g in perms:
        L = frozenset(comp(g, h) for h in A)
        if L not in lid:
            lid[L] = len(loops)
            loops.append(L)
    for L in loops:
        fs = {frozenset(comp(g, h) for h in H) for g in L}
        assert len(fs) == 1
        F = fs.pop()
        fid.setdefault(F, len(fid))
        fam_of.append(fid[F])
        cls_of.append(frozenset(cid(g) for g in L))
    assert len(fid) == n
    for L, cs in zip(loops, cls_of):
        assert len(cs) == n - 1          # a loop meets n-1 distinct classes
    return loops, fam_of, cls_of


def exact_covers(n, cls_of):
    """All partitions of the (n-1)! classes into loops, as loop-id tuples."""
    classes = sorted({c for cs in cls_of for c in cs})
    cix = {c: i for i, c in enumerate(classes)}
    masks = []
    for cs in cls_of:
        m = 0
        for c in cs:
            m |= 1 << cix[c]
        masks.append(m)
    FULL = (1 << len(classes)) - 1
    by_low = {}
    for i, m in enumerate(masks):
        low = (m & -m).bit_length() - 1
        by_low.setdefault(low, []).append(i)

    out = []

    def rec(cov, chosen):
        if cov == FULL:
            out.append(tuple(chosen))
            return
        low = (~cov) & FULL
        low = (low & -low).bit_length() - 1
        for i in by_low.get(low, []):
            if masks[i] & cov:
                continue
            chosen.append(i)
            rec(cov | masks[i], chosen)
            chosen.pop()

    rec(0, [])
    return out


def main():
    print(__doc__.split("CONJECTURE")[0].strip())
    print("\n    CONJECTURE (Family Quantisation).  In every exact cover of the")
    print("    (n-1)! classes by (n-2)! two-loops, each family contributes a")
    print("    number of loops divisible by n-2.\n")
    for n in (4, 5, 6):
        loops, fam_of, cls_of = setup(n)
        covers = exact_covers(n, cls_of)
        splits = Counter()
        ok = True
        for cov in covers:
            c = Counter(fam_of[i] for i in cov)
            splits[tuple(sorted(c.values(), reverse=True))] += 1
            if any(v % (n - 2) for v in c.values()):
                ok = False
        print(f"n = {n}:  {len(loops)} loops, {n} families of "
              f"{len(loops)//n}, {len(covers)} exact covers")
        print(f"  splits: {dict(sorted(splits.items(), key=lambda x: -x[1]))}")
        print(f"  every family count divisible by n-2 = {n-2}:  {ok}")
        assert ok, n
    print("\nQuantisation holds at n = 4, 5, 6 -- exhaustively.")


if __name__ == "__main__":
    main()
