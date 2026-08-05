"""What can follow a complete 2-loop traversal at n = 7?

A complete traversal of L burns all six rotation classes of L.  The walk then
leaves the arc end at weight >= 3.  There are exactly six weight-3 targets;
this file classifies them and, for each, measures how long the NEXT block can
possibly be before it runs into a class L has already spent.

Blocks are cheap runs, so a block entered at h occupies the consecutive
generators h, h.a, h.a^2, ... and the classes of those generators.  The
answer is a hard cap on the next block's length.

Everything is equivariant under relabelling and S_7 is simply transitive on
the 5040 permutations, so one source loop settles all 840.
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


c = sig(ident)
d = delta(ident)
a = ident
for _ in range(6):
    a = comp(a, c)
a = comp(a, d)                                   # a = c^6 d, order 6

loop = lambda g: [comp(g, pw) for pw in
                  [ident, a, comp(a, a), comp(comp(a, a), a),
                   comp(comp(comp(a, a), a), a),
                   comp(comp(comp(comp(a, a), a), a), a)]]
classes = lambda g: {onecycle(x) for x in loop(g)}

L = loop(ident)
LC = classes(ident)
assert len(LC) == 6

# the traversal is entered at ident and exits from the arc end of ident.a^5
last = L[5]
tail = end_of(last)
targets = [tail[3:] + t for t in permutations(tail[:3])]
b = None
rows = []
for h in targets:
    same_loop = h in L
    hc = classes(h)
    shared = LC & hc
    if not same_loop and not shared:
        b = comp(last, comp(ident, ident)) and h        # the om target
    # how far can the block from h run before meeting a class of L?
    cap, x = 0, h
    while cap < 6 and onecycle(x) not in LC:
        cap += 1
        x = comp(x, a)
    rows.append((h, same_loop, len(shared), cap))

print("targets of the weight-3 exit from a complete traversal of L")
print(f"{'target':<26}{'in L?':<8}{'|classes shared with L|':<26}"
      f"{'max next block'}")
for h, s, k, cap in rows:
    tag = "om" if (not s and k == 0) else ("+2 stride" if s else "")
    print(f"{str(h):<26}{str(s):<8}{k:<26}{cap:<4} {tag}")

caps = [cap for h, s, k, cap in rows if not s]
print(f"\nnon-om exits: max next block length in {sorted(set(caps))}")
print("om exit      : max next block length 6 (class-disjoint by definition)")
