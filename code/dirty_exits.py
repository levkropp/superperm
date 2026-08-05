"""Where does delta out of a PARTIAL arc land?  The dirty exit table.

Everything elementary about superpermutation lower bounds collapses at the
same point: a split lets the walk leave a class early, and delta out of the
resulting partial arc lands in an unrelated 2-loop.  That "free loop switch"
is what makes blocks unbounded (Houston's 872 has four of them) and it is why
sby_ladder.py's generalised lemma falls below HPV inside the band.

But free is an assumption, not a measurement.  This file measures it.

Setting.  A CLEAN RUN of length l entered at generator g occupies the arcs at
g, g.a, ..., g.a^(l-1); its first l-1 arcs are FULL (that is what makes the
delta jumps clean) and its last arc may be partial, covering k < n of the n
permutations of its class.  The run's cheap exit is then

        t = g.a^(l-1).c^(k-1).d          (k = n gives the clean t = g.a^l)

and the next clean run starts at t.  For each (l, k) this file reports:

  own    - is t inside the loop the run just traversed?
  hit    - is t itself in a class the run has already fully covered?  (then
           the exit is impossible: t would be an already-visited vertex)
  cap    - how many generators the NEXT clean run can advance before it meets
           a class this run fully covered.  An upper bound, as always, since
           other runs cover other classes.

Only classes the run covered FULLY count as burned: the partial last arc
leaves the rest of its own class available (that is the whole point of a
split), so the run burns l-1 classes, not l.
"""

from itertools import permutations
import math


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

    c, d = sig(ident), delta(ident)
    a = ident
    for _ in range(n - 1):
        a = comp(a, c)
    a = comp(a, d)
    assert order(a) == n - 1
    apow, cpow = [ident], [ident]
    for _ in range(n - 2):
        apow.append(comp(apow[-1], a))
    for _ in range(n - 1):
        cpow.append(comp(cpow[-1], c))
    return dict(n=n, ident=ident, comp=comp, onecycle=onecycle, a=a, d=d,
                apow=apow, cpow=cpow, order=order)


def table(M, g, l, k):
    """One (l, k) cell of the dirty exit table for the run entered at g."""
    n, comp, apow, cpow = M['n'], M['comp'], M['apow'], M['cpow']
    onecycle, a, d = M['onecycle'], M['a'], M['d']
    run = [comp(g, p) for p in apow[:l]]
    burned = {onecycle(x) for x in run[:l - 1]}          # FULL arcs only
    loop = {comp(g, p) for p in apow}
    last = run[l - 1]
    t = comp(comp(last, cpow[k - 1]), d)
    # vertices this run actually visited
    seen = set()
    for i, h in enumerate(run):
        span = n if i < l - 1 else k
        x = h
        for _ in range(span):
            seen.add(x)
            x = comp(x, cpow[1])
    cap, x = 0, t
    while cap < n - 1 and onecycle(x) not in burned:
        cap, x = cap + 1, comp(x, a)
    return dict(t=t, own=t in loop, hit=t in seen, cap=cap)


def report(n):
    M = build(n)
    ident, L = M['ident'], n - 1
    print(f"\n=== n = {n} ===   (l = run length, k = perms in the last arc; "
          f"k = {n} is the clean case)")
    print(f"    {'l\\k':<6}" + "".join(f"{k:<10}" for k in range(1, n + 1)))
    rows = {}
    for l in range(1, L + 1):
        cells = []
        for k in range(1, n + 1):
            c = table(M, ident, l, k)
            tag = "HIT" if c['hit'] else ("own" if c['own'] else "")
            cells.append(f"{c['cap']}{('/' + tag) if tag else '':<6}")
        rows[l] = [table(M, ident, l, k) for k in range(1, n + 1)]
        print(f"    {l:<6}" + "".join(f"{x:<10}" for x in cells))
    return M, rows


if __name__ == "__main__":
    print(__doc__.strip())
    print("\nlegend:  cap value, then HIT = target already visited "
          "(exit impossible), own = target inside the same 2-loop")
    for n in (5, 6, 7):
        M, rows = report(n)
        L = n - 1
        # equivariance spot-check on the full traversal row
        for g in list(permutations(range(1, n + 1)))[:400]:
            for k in range(1, n + 1):
                r = table(M, g, L, k)
                assert (r['cap'], r['own'], r['hit']) == (
                    rows[L][k - 1]['cap'], rows[L][k - 1]['own'],
                    rows[L][k - 1]['hit'])
        dead = [k for k in range(1, n) if rows[L][k - 1]['hit']]
        print(f"    complete traversal (l = {L}): dirty exits with k = "
              f"{dead} are IMPOSSIBLE (target already visited)")
        caps = [rows[L][k - 1]['cap'] for k in range(1, n)]
        print(f"    surviving dirty caps by k: "
              f"{[(k, rows[L][k-1]['cap']) for k in range(1, n) if k not in dead]}")
