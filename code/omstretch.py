"""Independent cross-check of code/omstretch.c, and the meaning of rho.

`omstretch.c` computes rho(c) = the fewest runs needed to cover c rotation
classes inside a single OM-STRETCH.  This file rebuilds the same object from
the Python definitions used everywhere else in the repo -- sharing no code
with the C -- and checks the two agree at n = 5 and n = 6.

The reduction (see code/coset_lemma.py).  Inside an om-stretch every
transition is om, so all generators stay in one right coset of H = <a,b>,
|H| = (n-1)!, and that coset meets each rotation class exactly once.  In a
SPLIT-FREE walk every class is used at most once, so a stretch is exactly a
simple path in the right Cayley graph Cay(H; {a, b}):

    g -> g.a   continues the current run   (free)
    g -> g.b   ends it, starts a new one   (one run)

Runs cap at n-1 by themselves, because ord(a) = n-1 makes the (n-1)-st a-step
revisit the run's own start.  H acts on itself by left multiplication without
disturbing the right-multiplication edges, so the graph is vertex-transitive
and every path may be assumed to start at the identity.

Known values:

    n = 5   rho(24)  = 8      exact
    n = 6   rho(120) = 31     exact
    n = 7   rho(720) >= 128   partial

The n = 5 and n = 6 values are exact: the search proves every smaller run
count infeasible.  At n = 7 the same search certified K = 120 ... 127 all
impossible (the K = 127 level alone took 1.3e11 nodes) before the node cap
stopped it at K = 128, so rho(720) >= 128 is proved and the exact value is
open.
"""

import sys
from itertools import permutations

sys.path.insert(0, "code")

RHO = {5: 8, 6: 31}


def build(n):
    ident = tuple(range(1, n + 1))
    sig = lambda u: u[1:] + u[:1]
    delta = lambda u: u[2:] + (u[1], u[0])
    comp = lambda u, v: tuple(u[v[i] - 1] for i in range(n))
    a = ident
    for _ in range(n - 1):
        a = comp(a, sig(ident))
    a = comp(a, delta(ident))
    b = tuple(list(range(3, n)) + [2, 1, n])
    return ident, comp, a, b


def graph(n):
    """Vertices of H = <a,b>, with the two out-edges, indexed 0..(n-1)!-1."""
    ident, comp, a, b = build(n)
    idx, verts = {ident: 0}, [ident]
    head = 0
    while head < len(verts):
        x = verts[head]
        for g in (a, b):
            y = comp(x, g)
            if y not in idx:
                idx[y] = len(verts)
                verts.append(y)
        head += 1
    sa = [idx[comp(v, a)] for v in verts]
    sb = [idx[comp(v, b)] for v in verts]
    return len(verts), sa, sb


def loops(nv, sa, n):
    """a-cycles of the coset: the (n-2)! two-loops."""
    lid, pos = [-1] * nv, [0] * nv
    nl = 0
    for i in range(nv):
        if lid[i] >= 0:
            continue
        x, k = i, 0
        while True:
            lid[x], pos[x] = nl, k
            k += 1
            x = sa[x]
            if x == i:
                break
        assert k == n - 1, (k, n)
        nl += 1
    return nl, lid, pos


def arcs(mask, ln):
    """maximal circular arcs of set bits -- each needs its own run."""
    if mask == 0:
        return 0
    if mask == (1 << ln) - 1:
        return 1
    return sum(1 for i in range(ln)
               if (mask >> i & 1) and not (mask >> ((i - 1) % ln) & 1))


def rho_full(n, verbose=True):
    """Exact rho((n-1)!) by iterative deepening on the number of runs."""
    nv, sa, sb = graph(n)
    nl, lid, pos = loops(nv, sa, n)
    ln = n - 1
    table = [arcs(m, ln) for m in range(1 << ln)]

    for K in range(nl, nv + 1):
        vis = [False] * nv
        lmask = [(1 << ln) - 1] * nl
        state = {"arcsum": nl, "hit": False}

        def take(g):
            vis[g] = True
            L = lid[g]
            state["arcsum"] -= table[lmask[L]]
            lmask[L] &= ~(1 << pos[g])
            state["arcsum"] += table[lmask[L]]

        def give(g):
            L = lid[g]
            state["arcsum"] -= table[lmask[L]]
            lmask[L] |= 1 << pos[g]
            state["arcsum"] += table[lmask[L]]
            vis[g] = False

        def dfs(g, cov, runs, runlen):
            if cov == nv:
                state["hit"] = True
                return True
            if runs + state["arcsum"] - 1 > K:
                return False
            if runlen < ln:
                h = sa[g]
                if not vis[h]:
                    take(h)
                    if dfs(h, cov + 1, runs, runlen + 1):
                        return True
                    give(h)
            if runs < K:
                h = sb[g]
                if not vis[h]:
                    take(h)
                    if dfs(h, cov + 1, runs + 1, 1):
                        return True
                    give(h)
            return False

        take(0)
        ok = dfs(0, 1, 1, 1)
        if verbose:
            print(f"    K = {K:3}  {'FEASIBLE' if ok else 'impossible'}")
        if ok:
            return K
    return None


if __name__ == "__main__":
    print(__doc__.split("Known values:")[0].strip())
    for n in (5, 6):
        nv, sa, sb = graph(n)
        nl, _, _ = loops(nv, sa, n)
        import math
        print(f"\nn = {n}:  |H| = {nv} = (n-1)!, "
              f"{nl} loops = (n-2)!")
        assert nv == math.factorial(n - 1) and nl == math.factorial(n - 2)
        r = rho_full(n)
        print(f"  rho({nv}) = {r}   "
              f"{'MATCHES omstretch.c' if r == RHO[n] else 'MISMATCH!'}")
        assert r == RHO[n], (n, r, RHO[n])
    print("\nPython and C agree at n = 5 and n = 6.")
