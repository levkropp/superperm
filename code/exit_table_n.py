"""Exit caps and the block-count lemma for general n -- soundness check.

The n = 7 argument in split_free_5889.py rests on two computed objects:

    * the exit-cap rows: for a block of length l, the multiset of caps over
      the (n-1)! / (n-3)! ... i.e. the (n-1)(n-2)...  weight-3 targets;
    * the Pentad element s = a^(n-2) b and its order.

Both are defined for every n.  Running the whole scheme at n = 5 and n = 6,
where split-free walks are known to exist (the classical recursive
superpermutations have S = 0), checks that the machinery never proves
something false: the bound it returns must be <= the length of the classical
string.

    n = 5   classical 153, split-free, R = 24,  E = 6
    n = 6   classical 873, split-free, R = 120, E = 29
"""

from itertools import permutations
import math


def build(n):
    ident = tuple(range(1, n + 1))
    sig = lambda u: u[1:] + u[:1]
    delta = lambda u: u[2:] + (u[1], u[0])
    comp = lambda u, v: tuple(u[v[i] - 1] for i in range(n))

    def inv(u):
        w = [0] * n
        for i, x in enumerate(u):
            w[x - 1] = i + 1
        return tuple(w)

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

    def order(u):
        k, x = 1, u
        while x != ident:
            x, k = comp(x, u), k + 1
        return k

    a = ident
    for _ in range(n - 1):
        a = comp(a, sig(ident))
    a = comp(a, delta(ident))
    assert order(a) == n - 1, (n, order(a))
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

    return dict(n=n, ident=ident, comp=comp, order=order, a=a, apow=apow,
                exits=exits)


def report(n):
    M = build(n)
    ident, comp, order, apow = M['ident'], M['comp'], M['order'], M['apow']
    L = n - 1                       # generators per 2-loop = max block length
    F1 = math.factorial(n - 1)      # arcs in a split-free walk
    print(f"\n=== n = {n} ===   blocks have length 1..{L}, "
          f"total length {F1}")
    print(f"{'l':<4}{'caps over the six weight-3 exits':<44}"
          f"{'#cap-max':<10}{'unique?'}")
    rows = {}
    for l in range(1, L + 1):
        e = M['exits'](ident, l)
        caps = sorted(k for _, k in e)
        top = [m for m, k in e if k == L]
        rows[l] = (caps, top)
        print(f"{l:<4}{str(caps):<44}{len(top):<10}{len(top) == 1}")

    capsL, topL = rows[L]
    assert len(topL) == 1, "no unique om at the top row"
    b = topL[0]
    s = comp(apow[L - 1], b)
    print(f"  om = b = {b}")
    print(f"  Pentad element s = a^{L-1}.b has order {order(s)}   "
          f"(chains of complete traversals cap here)")
    return M, rows, b, s


def counting_bound(n, chain_cap, top_free):
    """Minimum E = (B-1)+Y allowed by the block-count lemma at this n.

    chain_cap  = ord(s), the longest chain of complete traversals
    top_free   = number of block lengths < L that a cap-(chain-ending) exit
                 can reach; here we only use the crude form used at n = 7:
                 a chain of chain_cap traversals must end the walk, hit a
                 block short enough for a non-om exit, or exit at weight >= 4.
    """
    L, F1 = n - 1, math.factorial(n - 1)
    best = None
    for Y in range(0, 60):
        for B in range(F1 // L, F1 + 1):
            E = (B - 1) + Y
            if best is not None and E >= best:
                continue
            ok = False
            for f in range(B + 1):
                for nL1 in range(B - f + 1):        # blocks of length L-1
                    m = B - f - nL1                 # blocks of length <= L-2
                    short = F1 - L * f - (L - 1) * nL1
                    if m == 0:
                        if short != 0:
                            continue
                    elif not (m <= short <= (L - 2) * m):
                        continue
                    c = (B - f) + Y + 1
                    if f <= (chain_cap - 1) * c + (m + Y + 1):
                        ok = True
                        break
                if ok:
                    break
            if ok:
                best = E
    return best


if __name__ == "__main__":
    print(__doc__.strip())
    known = {5: (153, 6), 6: (873, 29), 7: (None, None)}
    for n in (5, 6, 7):
        M, rows, b, s = report(n)
        cap = M['order'](s)
        E = counting_bound(n, cap, None)
        base = n + math.factorial(n) - 2 + math.factorial(n - 1)
        print(f"  block-count lemma: E >= {E}, so split-free length >= "
              f"{base + E}")
        if known[n][0]:
            print(f"  classical split-free string: length {known[n][0]}, "
                  f"E = {known[n][1]}   -> sound: "
                  f"{base + E <= known[n][0]}")
            assert base + E <= known[n][0], "UNSOUND"
