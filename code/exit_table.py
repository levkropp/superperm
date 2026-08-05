"""Exit table: what can follow a cheap block of length l at n = 7.

A block is a maximal run of arcs joined by weight-2 moves.  In a split-free
walk every arc is a full class arc, so the cheap move out of the arc of
generator g is g -> g.a (a = c^6 d, order 6): a block entered at g of length
l occupies the generators g, g.a, ..., g.a^(l-1) of one 2-loop and burns the
l rotation classes of those generators.

Leaving the block costs weight >= 3.  There are exactly six weight-3 targets
from an arc end.  This file classifies them for each l, and for each target
reports a hard cap on the length of the NEXT block: the number of steps the
next block can run before it re-enters one of the l classes this block just
burned.  (Other classes are burned elsewhere in the walk, so these caps are
upper bounds, which is the direction a lower-bound proof needs.)

S_7 is simply transitive on the 5040 permutations and everything in sight is
relabelling-equivariant, so the single block entered at the identity settles
all of them; the script asserts that.
"""

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


a = ident
for _ in range(6):
    a = comp(a, sig(ident))
a = comp(a, delta(ident))
apow = [ident]
for _ in range(5):
    apow.append(comp(apow[-1], a))
assert comp(apow[5], a) == ident, "a has order 6"

gens = lambda g: [comp(g, p) for p in apow]


def table(g, l):
    """Block entered at g, length l.  Returns list of (target, cap)."""
    burned = {onecycle(x) for x in gens(g)[:l]}
    last = gens(g)[l - 1]
    tail = end_of(last)
    out = []
    for t in permutations(tail[:3]):
        h = tail[3:] + t
        cap, x = 0, h
        while cap < 6 and onecycle(x) not in burned:
            cap += 1
            x = comp(x, a)
        out.append((h, cap))
    return out


print("caps on the next block, by length l of the block being left")
print(f"{'l':<4}{'multiset of caps over the six weight-3 targets':<50}"
      f"{'best non-om'}")
summary = {}
for l in range(1, 7):
    caps = sorted(c for _, c in table(ident, l))
    # om = the unique target landing in a loop sharing no class with this one
    #      (only meaningful at l = 6, where the block burned all six)
    best_non_om = sorted(caps)[-2]
    summary[l] = caps
    print(f"{l:<4}{str(caps):<50}{best_non_om}")

# the same for all 5040 entry points -- equivariance check
for l in (5, 6):
    ref = summary[l]
    for g in permutations(range(1, n + 1)):
        assert sorted(c for _, c in table(g, l)) == ref, (g, l)
print("\ncaps are identical for all 5040 entry points (S_7-equivariance)  OK")

print("""
Reading of the l = 6 row -- the EXIT TRICHOTOMY.  A complete traversal has
burned all six classes of its loop, so of its six weight-3 exits:
  * three are dead on arrival (cap 0): the +2 stride re-enters the loop, and
    two of the cross moves land directly in a class the traversal just spent;
  * two land in loops sharing classes, and cap the next block at 4;
  * one is om, the class-disjoint move, and caps nothing.
So a complete traversal is followed either by om, or by a block of length
<= 4, or by a jump of weight >= 4.""")
