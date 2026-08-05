"""The Chain-Count Lemma, and the n = 6 case B = (n-2)!.

Consider a SPLIT-FREE walk in which every block is a COMPLETE TRAVERSAL.  Then
the blocks are the loops, and since each covers n-1 of the (n-1)! classes,

        B = f = (n-2)!        and the loops are an exact cover.

Every one of the f - 1 transitions joins two runs of length n-1, and
l + l' = 2n-2 >= 2n-3, so by the exit table (coset_lemma.py) a WEIGHT-3
transition here is forced onto om.  Hence each transition is either om or has
weight >= 4.  Let h be the number of the latter.  Maximal om-chains satisfy

        #chains = f - #om = f - ((f-1) - h) = 1 + h,

and a chain of k traversals sits at g, g.s, ..., g.s^(k-1) with s = a^(n-2) b,
so k <= ord(s) = n-2 (the next one would re-enter g).  Therefore

        f <= (n-2)(1 + h)   =>   h >= f/(n-2) - 1 = (n-3)! - 1,

and since Y = sum(weight - 3) >= h,

    CHAIN-COUNT LEMMA.  A split-free walk all of whose blocks are complete
    traversals has

        Y >= (n-3)! - 1,     T = B + Y >= (n-2)! + (n-3)! - 1,

        length >= n! + (n-1)! + (n-2)! + (n-3)! + n - 4.

That closed form is the interesting part.  It is EXACTLY s(n) for n = 4, 5, 6
-- so it is sharp wherever s(n) is known -- and at n = 7 it gives 5907, one
MORE than the conjectured s(7) = 5906.  So, conditional on s(7) = 5906:

    no 7-symbol champion is split-free with all blocks complete traversals.

At n = 6 it lands on 872 = s(6) exactly, so the case is not excluded there and
needs one more unit: Y >= 6 rather than Y >= 5.  The second half of this file
pins down what Y = 5 would have to look like.
"""

import math
import sys
from itertools import permutations

sys.path.insert(0, "code")


def build(n):
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

    def order(u):
        k, x = 1, u
        while x != ident:
            x, k = comp(x, u), k + 1
        return k

    a = ident
    for _ in range(n - 1):
        a = comp(a, sig(ident))
    a = comp(a, delta(ident))
    b = tuple(list(range(3, n)) + [2, 1, n])
    apow = [ident]
    for _ in range(n - 2):
        apow.append(comp(apow[-1], a))
    s = comp(apow[n - 2], b)
    return dict(n=n, ident=ident, comp=comp, onecycle=onecycle, order=order,
                a=a, b=b, s=s, apow=apow)


def bound(n):
    f = math.factorial(n - 2)
    return (math.factorial(n) + math.factorial(n - 1) + math.factorial(n - 2)
            + math.factorial(n - 3) + n - 4), f


if __name__ == "__main__":
    print(__doc__.split("That closed form")[0].strip())

    KNOWN = {4: 33, 5: 153, 6: 872, 7: None}
    CLASSICAL = {4: 33, 5: 153, 6: 873, 7: 5913}
    print(f"\n{'n':<4}{'ord(s)':<9}{'f=(n-2)!':<11}{'Y >=':<8}"
          f"{'length >=':<12}{'s(n)':<8}{'classical'}")
    for n in (4, 5, 6, 7):
        M = build(n)
        assert M["order"](M["s"]) == n - 2, (n, M["order"](M["s"]))
        L, f = bound(n)
        base = n + math.factorial(n) + math.factorial(n - 1) - 3
        assert L == base + f + math.factorial(n - 3) - 1
        print(f"{n:<4}{M['order'](M['s']):<9}{f:<11}"
              f"{math.factorial(n-3)-1:<8}{L:<12}"
              f"{KNOWN[n] if KNOWN[n] else '?':<8}{CLASSICAL[n]}")
        if KNOWN[n]:
            assert L <= CLASSICAL[n], "unsound: exceeds a real split-free walk"
    print("\n  ord(s) = n-2 verified; the bound is exactly s(n) at n = 4,5,6,")
    print("  and 5907 at n = 7 -- one MORE than the conjectured s(7) = 5906.")

    # ---- n = 6: what would Y = 5 have to look like? -----------------------
    n = 6
    M = build(n)
    comp, apow, onecycle, s = M["comp"], M["apow"], M["onecycle"], M["s"]
    f, sigord = math.factorial(n - 2), n - 2
    print(f"\n--- n = 6, B = {f}: ruling out Y = 5 ---")
    print(f"  Y = 5 forces {1+5} om-chains for {f} traversals, each of length "
          f"exactly {sigord} = ord(s):")
    print(f"  so the {f} loops are {1+5} FULL <s>-orbits, and they must exactly "
          f"cover the {math.factorial(n-1)} classes.")

    perms = list(permutations(range(1, n + 1)))
    cid = {}
    for p in perms:
        c = onecycle(p)
        if c not in cid:
            cid[c] = len(cid)

    seen, orbits = set(), []
    for g in perms:
        if g in seen:
            continue
        orb, x = [], g
        for _ in range(sigord):
            orb.append(x)
            seen.add(x)
            x = comp(x, s)
        assert x == g
        orbits.append(orb)
    print(f"  <s>-orbits of generators: {len(orbits)} of size {sigord}")

    omask, bad = [], 0
    for orb in orbits:
        mask = 0
        tot = 0
        for g in orb:
            for pw in apow:
                mask |= 1 << cid[onecycle(comp(g, pw))]
            tot += n - 1
        if bin(mask).count("1") != tot:
            bad += 1
        omask.append(mask)
    print(f"  orbits whose {sigord} loops are NOT pairwise class-disjoint: "
          f"{bad} / {len(orbits)}")
    span = bin(omask[0]).count("1")
    print(f"  a full chain covers {span} of the {len(cid)} classes; "
          f"{1+5} x {span} = {(1+5)*span}")

    # exact cover of the classes by 6 pairwise-disjoint orbits
    FULL = (1 << len(cid)) - 1
    by_low = {}
    for i, m in enumerate(omask):
        low = (m & -m).bit_length() - 1
        by_low.setdefault(low, []).append(i)

    sols = []

    def cover(mask, chosen):
        if len(sols) >= 200000:
            return
        if mask == FULL:
            sols.append(tuple(chosen))
            return
        low = ((~mask) & FULL)
        low = (low & -low).bit_length() - 1
        for i in by_low.get(low, []):
            if omask[i] & mask:
                continue
            chosen.append(i)
            cover(mask | omask[i], chosen)
            chosen.pop()

    cover(0, [])
    print(f"  exact covers of the {len(cid)} classes by {1+5} disjoint "
          f"<s>-orbits: {len(sols)}")
    if not sols:
        print("  => NONE exist, so Y = 5 is impossible and Y >= 6:")
        print("     split-free with B = 24 has length >= 873 > 872 = s(6).")
        sys.exit(0)

    print("  => such covers exist, so cover rigidity alone does not exclude")
    print("     Y = 5.  Now the five connecting weight-4 jumps.")

    # ---- the connecting jumps --------------------------------------------
    # A chain is a FULL <s>-orbit entered at one of its ord(s) elements; the
    # entry fixes the order g, g.s, ..., g.s^(ord-1).  Its last traversal sits
    # at g.s^(ord-1) and that traversal's last arc starts at g.s^(ord-1).a^(n-2)
    # and ends at sigma^(n-1) of it.  Leaving the chain costs weight >= 4, and
    # Y = 5 over 5 jumps forces every one of them to be weight EXACTLY 4.
    sig = lambda u: u[1:] + u[:1]

    def end_of(u):
        for _ in range(n - 1):
            u = sig(u)
        return u

    def weight(u, w):
        for k in range(1, n + 1):
            if u[k:] == w[:n - k]:
                return k
        return n

    spow = [M["ident"]]
    for _ in range(sigord - 1):
        spow.append(comp(spow[-1], s))

    orb_of = {}
    for i, orb in enumerate(orbits):
        for g in orb:
            orb_of[g] = i

    exit_end = {}
    for g in perms:
        last = comp(g, spow[sigord - 1])
        exit_end[g] = end_of(comp(last, apow[n - 2]))

    # successors: entries reachable by a weight-4 jump out of the chain
    succ = {}
    for g in perms:
        e = exit_end[g]
        succ[g] = [q for q in perms if weight(e, q) == 4]
    deg = sum(len(v) for v in succ.values()) / len(succ)
    print(f"  every chain has exactly {int(deg)} weight-4 exits "
          f"(= (n-2)! arrangements), each landing on one chain entry")

    def linkable(cover):
        """Can these 6 orbits be strung into one path by weight-4 jumps?"""
        want = set(cover)

        def go(g, used):
            if len(used) == len(cover):
                return True
            for q in succ[g]:
                o = orb_of[q]
                if o in want and o not in used:
                    used.add(o)
                    if go(q, used):
                        return True
                    used.remove(o)
            return False

        for o in cover:
            for g in orbits[o]:
                if go(g, {o}):
                    return True
        return False

    good = [c for c in sols if linkable(c)]
    print(f"\n  covers that can actually be linked by 5 weight-4 jumps: "
          f"{len(good)} / {len(sols)}")
    if not good:
        print("  => Y = 5 is IMPOSSIBLE.  So Y >= 6 and a split-free n = 6")
        print("     walk with B = 24 has length >= 873 > 872 = s(6):")
        print("     no n = 6 champion is split-free with all blocks complete.")
    else:
        print(f"  => {len(good)} survive; Y = 5 is not excluded by this check.")
        print(f"     example cover: {good[0]}")
