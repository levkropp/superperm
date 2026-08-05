"""The FAMILY REFORMULATION: a split-free walk is a 6-colouring of the classes.

The Coset Lemma (code/coset_lemma.py) says H = <a,b> has order (n-1)! and
index n, and that H and each of its n right cosets meets every rotation class
exactly once.  Since a in H and the arc-to-arc delta step is exactly right
multiplication by a, a 2-loop is a right coset of <a> -- so the n! / (n-1)
loops fall into n FAMILIES of (n-2)!, one per right coset of H, and

    each family is an exact cover of the (n-1)! classes.

At n = 6: 144 loops = 6 families x 24, each family covering the 120 classes.

The consequence is a change of variables.  A split-free walk covers each class
by exactly one full arc; that arc starts at one of the class's n permutations,
each lying in a different family.  So

    A SPLIT-FREE WALK IS EXACTLY AN n-COLOURING OF THE (n-1)! CLASSES
    (colour of C = which family supplies C), TOGETHER WITH AN ORDERING.

The loops used, v, and the block count B are all read off the colouring alone:
inside family f the classes coloured f sit in f's 24 disjoint 5-cycles, and

    B = sum over families f, over loops L of f, of
        #(maximal delta-arcs of the f-coloured classes of L).

The v = 24 case is the monochromatic-per-loop extreme.  This file verifies the
whole picture and measures min B over colourings.
"""

import sys
from itertools import permutations

sys.path.insert(0, "code")

n = 6
ident = tuple(range(1, n + 1))
sig = lambda u: u[1:] + u[:1]
delta = lambda u: u[2:] + (u[1], u[0])
comp = lambda u, v: tuple(u[v[i] - 1] for i in range(n))
cid = lambda u: min(u[k:] + u[:k] for k in range(n))


def gens():
    a = ident
    for _ in range(n - 1):
        a = comp(a, sig(ident))
    a = comp(a, delta(ident))
    b = tuple(list(range(3, n)) + [2, 1, n])
    return a, b


def closure(gs):
    seen, frontier = {ident}, [ident]
    while frontier:
        x = frontier.pop()
        for g in gs:
            y = comp(x, g)
            if y not in seen:
                seen.add(y)
                frontier.append(y)
    return seen


def main():
    perms = list(permutations(range(1, n + 1)))
    a, b = gens()

    # the delta step between consecutive arc starts IS right multiplication by a
    for g in perms:
        u = g
        for _ in range(n - 1):
            u = sig(u)
        assert delta(u) == comp(g, a), g
    print("delta(sigma^(n-1)(g)) == g.a  for all 720 g")

    H = closure((a, b))
    A = closure((a,))
    print(f"|<a>| = {len(A)} = n-1,  |H| = |<a,b>| = {len(H)} = (n-1)!,"
          f"  index {len(perms) // len(H)} = n")
    assert len(A) == n - 1 and len(H) * n == len(perms)

    # loops = right cosets of <a>;  families = right cosets of H
    def coset(sub, x):
        # the walk moves by RIGHT multiplication (g -> g.a, g -> g.b), so the
        # invariant sets are x.Sub, not Sub.x
        return frozenset(comp(x, h) for h in sub)

    loops, lid = [], {}
    for g in perms:
        L = coset(A, g)
        if L not in lid:
            lid[L] = len(loops)
            loops.append(L)
    fams, fid = [], {}
    for g in perms:
        F = coset(H, g)
        if F not in fid:
            fid[F] = len(fams)
            fams.append(F)
    print(f"loops: {len(loops)} = n!/(n-1),  families: {len(fams)} = n")
    assert len(loops) == len(perms) // (n - 1) and len(fams) == n

    fam_of_loop = {}
    for L in loops:
        fs = {fid[coset(H, g)] for g in L}
        assert len(fs) == 1, "a loop straddles two families"
        fam_of_loop[lid[L]] = fs.pop()
    from collections import Counter
    sizes = Counter(fam_of_loop.values())
    print(f"loops per family: {sorted(set(sizes.values()))} "
          f"(expect [(n-2)!] = [{24}])")
    assert set(sizes.values()) == {24}

    # each family is an exact cover of the classes
    for f, F in enumerate(fams):
        cs = [cid(g) for g in F]
        assert len(set(cs)) == len(perms) // n, f
    print("every family is an EXACT COVER of the 120 classes")

    # so each class meets each family in exactly one permutation: the port
    port = {}
    for g in perms:
        key = (cid(g), fid[coset(H, g)])
        assert key not in port
        port[key] = g
    print("each class has exactly one arc start per family -> "
          "a walk = a 6-colouring")

    # loop structure inside a family: 24 disjoint 5-cycles under g -> g.a
    classes = sorted({cid(g) for g in perms})
    cix = {c: i for i, c in enumerate(classes)}
    fam_cycles = []
    for f in range(n):
        seen, cyc = set(), []
        for c in classes:
            g = port[(c, f)]
            if g in seen:
                continue
            ring, x = [], g
            while x not in seen:
                seen.add(x)
                ring.append(cix[cid(x)])
                x = comp(x, a)
            assert len(ring) == n - 1
            cyc.append(ring)
        assert len(cyc) == 24
        fam_cycles.append(cyc)
    print(f"each family splits the 120 classes into 24 delta-5-cycles")

    # B(colouring) and the minimum over colourings
    def blocks(colour):
        tot = 0
        for f in range(n):
            for ring in fam_cycles[f]:
                m = [colour[c] == f for c in ring]
                k = sum(m)
                if k == 0:
                    continue
                tot += 1 if k == n - 1 else sum(
                    1 for i in range(n - 1) if m[i] and not m[i - 1])
        return tot

    mono = [0] * len(classes)
    print(f"\nB(all one family) = {blocks(mono)}  (the v = 24 extreme)")

    import random
    random.seed(1)
    best = min(blocks([random.randrange(n) for _ in classes])
               for _ in range(2000))
    print(f"B(best of 2000 random colourings) = {best}")
    print("\nMin B over colourings is 24, attained by the exact covers; the")
    print("live question is which colourings reach B + Y = 29 with an order.")


if __name__ == "__main__":
    main()
