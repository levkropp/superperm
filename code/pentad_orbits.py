"""Cover rigidity at n = 7, v = 121: how many full om-chains can coexist?

The pinned state at v = 121, A = 0 (notes/block_count_lemma.md section 6) has
115 complete traversals in at most 25 om-chains.  Chains cap at
ord(s) = 5 with s = a^5 b, so

    115 <= 5 c5 + 4 (25 - c5)   =>   c5 >= 15,

i.e. AT LEAST FIFTEEN of the chains are full, of five traversals each.  A full
chain entered at g visits the generators g, gs, gs^2, gs^3, gs^4 -- a complete
<s>-ORBIT.  There are 5040/5 = 1008 such orbits, and by the sharpness half of
the Pentad Lemma the five 2-loops of one orbit are pairwise class-disjoint, so
a full chain consumes 5 loops and exactly 30 of the 720 rotation classes.

Now the covering side.  At v = 121, A = 0 every loop is saturated (a_L = 6),
so the 121 loops carry 726 class-slots over 720 classes: EXACTLY SIX classes
are covered twice, and those six are the S = 6 split classes.  Six collisions
is the entire budget for the whole walk.

So the question is sharp and finite:

    can 15 of the 1008 <s>-orbits be chosen with at most 6 class collisions
    between them?

15 orbits carry 450 class-slots.  If orbits typically overlap, C(15,2) = 105
pairs cannot fit inside a budget of 6 and the state dies.  This file computes
the answer instead of guessing it.
"""

import sys
from itertools import permutations

n = 7
ident = tuple(range(1, n + 1))
sig = lambda u: u[1:] + u[:1]
delta = lambda u: u[2:] + (u[1], u[0])
comp = lambda u, v: tuple(u[v[i] - 1] for i in range(n))


def onecycle(u):
    best, x = u, u
    for _ in range(n - 1):
        x = sig(x)
        best = min(best, x)
    return best


def end_of(g):
    u = g
    for _ in range(n - 1):
        u = sig(u)
    return u


def inv(u):
    w = [0] * n
    for i, x in enumerate(u):
        w[x - 1] = i + 1
    return tuple(w)


def order(u):
    k, x = 1, u
    while x != ident:
        x, k = comp(x, u), k + 1
    return k


# ---- the group elements ---------------------------------------------------
a = ident
for _ in range(n - 1):
    a = comp(a, sig(ident))
a = comp(a, delta(ident))
assert order(a) == n - 1
apow = [ident]
for _ in range(n - 2):
    apow.append(comp(apow[-1], a))


def exits(g, l):
    burned = {onecycle(x) for x in (comp(g, p) for p in apow[:l])}
    last = comp(g, apow[l - 1])
    tail = end_of(last)
    out = []
    for p in permutations(tail[:3]):
        h = tail[3:] + p
        cap, x = 0, h
        while cap < n - 1 and onecycle(x) not in burned:
            cap, x = cap + 1, comp(x, a)
        out.append((comp(inv(last), h), cap))
    return out


b = [mu for mu, k in exits(ident, n - 1) if k == n - 1]
assert len(b) == 1
b = b[0]
s = comp(apow[n - 2], b)
assert order(s) == n - 2, "the Pentad element"


if __name__ == "__main__":
    print(__doc__.strip())
    print(f"\na = {a}   b = {b}   s = a^{n-2}.b   ord(s) = {order(s)}")

    # ---- rotation classes as bit positions -------------------------------
    perms = list(permutations(range(1, n + 1)))
    cls_id, classes = {}, {}
    for p in perms:
        c = onecycle(p)
        if c not in classes:
            classes[c] = len(classes)
        cls_id[p] = classes[c]
    print(f"{len(classes)} rotation classes, {len(perms)} generators")

    loopmask = {}
    for g in perms:
        mask = 0
        for pw in apow:
            mask |= 1 << cls_id[comp(g, pw)]
        assert bin(mask).count("1") == n - 1, "a loop meets n-1 classes"
        loopmask[g] = mask

    # ---- <s>-orbits of generators ----------------------------------------
    seen, orbits = set(), []
    for g in perms:
        if g in seen:
            continue
        orb, x = [], g
        for _ in range(order(s)):
            orb.append(x)
            seen.add(x)
            x = comp(x, s)
        assert x == g
        orbits.append(orb)
    print(f"{len(orbits)} <s>-orbits of size {order(s)}")

    # ---- Pentad sharpness, on all 1008 orbits ----------------------------
    omask, bad = [], 0
    for orb in orbits:
        mask, tot = 0, 0
        for g in orb:
            mask |= loopmask[g]
            tot += n - 1
        if bin(mask).count("1") != tot:
            bad += 1
        omask.append(mask)
    print(f"orbits whose {order(s)} loops are NOT pairwise class-disjoint: "
          f"{bad} / {len(orbits)}")
    span = bin(omask[0]).count("1")
    print(f"a full chain therefore consumes {span} of the {len(classes)} "
          f"classes")

    # ---- how disjoint can a family of full chains be? --------------------
    print("\n--- pairwise overlaps between <s>-orbit class sets ---")
    from collections import Counter
    cnt = Counter()
    N = len(orbits)
    for i in range(N):
        mi = omask[i]
        for j in range(i + 1, N):
            cnt[bin(mi & omask[j]).count("1")] += 1
    tot = sum(cnt.values())
    for k in sorted(cnt)[:8]:
        print(f"  overlap {k:>3} classes : {cnt[k]:>8}  "
              f"({100.0 * cnt[k] / tot:.2f}%)")
    print(f"  disjoint pairs: {cnt.get(0, 0)} of {tot}")

    # ---- greedy + randomised search for a large disjoint family ----------
    import random
    print("\n--- largest family of pairwise class-disjoint full chains ---")
    best, bestset = 0, None
    random.seed(7)
    for trial in range(4000):
        order_ = list(range(N))
        random.shuffle(order_)
        used, fam = 0, []
        for i in order_:
            if used & omask[i] == 0:
                used |= omask[i]
                fam.append(i)
        if len(fam) > best:
            best, bestset = len(fam), fam
    print(f"  greedy/randomised best: {best} pairwise-disjoint orbits "
          f"({best * span} of {len(classes)} classes covered)")
    print(f"  ceiling from counting : {len(classes) // span}")

    need = 15
    print(f"\n  the v = 121 state needs >= {need} full chains inside a budget "
          f"of 6 class collisions")
    if best >= need:
        print(f"  => {best} >= {need}: cover rigidity alone does NOT kill it.")
    else:
        print(f"  => only {best} fit: the state is DEAD by cover rigidity.")
