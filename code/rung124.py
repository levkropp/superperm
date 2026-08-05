"""The split-free rungs v = 123 and v = 124 at n = 7, closed by a period map.

rung_split_free.py leaves exactly two split-free states at length 5888:

    v = 124   (f, v6, vl, B, Y) = (100, 0, 24, 124, 0)
    v = 123   (f, v6, vl, B, Y) = (104,  1, 18, 124, 0)

This file rules out the v = 124 one outright.  The argument is forced at every
step, so there is nothing to search:

 1. Y = 0 means every costly jump has weight exactly 3, and A = 24 spread over
    vl = 24 short loops means every short loop misses exactly one generator,
    i.e. every short block has length exactly 5.  So the 124 blocks are 100 of
    length 6 (complete traversals) and 24 of length 5, and every jump between
    consecutive blocks has weight exactly 3.

 2. EXIT TRICHOTOMY (exit_table.py, row l = 6).  Of the six weight-3 exits
    from a complete traversal, three are dead and two cap the next block at
    length 4.  Every block here has length >= 5, so every complete traversal
    that is not the final block exits by om.

 3. om is right multiplication by s = a^5 b, and ord(s) = 5.  A run of k
    consecutive complete traversals therefore sits at g, g.s, ..., g.s^(k-1),
    and if k = 5 the fifth would have to exit om into g -- a loop it has
    already burned.  So k <= 4 (k <= 5 only for a run ending the walk).

 4. The 24 short blocks cut the block sequence into at most 25 runs of
    complete traversals, so 100 <= 4 * 25 = 100.  Equality: there are exactly
    25 runs, each of exactly four traversals, and the walk reads

        [T T T T  S] x 24   [T T T T].

 5. EXIT ROW l = 5 (exit_table.py).  Of the six weight-3 exits from a length-5
    block, two are dead, one caps the next block at 4, two at 5.  The next
    block here is a complete traversal, so only the cap-6 exit survives, and
    it is unique: right multiplication by a fixed t computed below.

 6. So the run-to-run map is right multiplication by the single fixed element

        P = s^4 . a^4 . t

    and the 25 run starts are g, g.P, ..., g.P^24.  This file computes ord(P).
    If ord(P) <= 24 the 25 runs cannot occupy 25 distinct loops and the state
    is dead.
"""

from itertools import permutations

n = 7
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
        x = comp(x, u)
        k += 1
    return k


c, d = sig(ident), delta(ident)
a = ident
for _ in range(6):
    a = comp(a, c)
a = comp(a, d)                                  # a = c^6 d, "next generator"
assert order(a) == 6

apow = [ident]
for _ in range(5):
    apow.append(comp(apow[-1], a))
gens = lambda g: [comp(g, p) for p in apow]


def exits(g, l):
    """Weight-3 exits of the block of length l entered at g, with caps."""
    burned = {onecycle(x) for x in gens(g)[:l]}
    last = gens(g)[l - 1]
    tail = end_of(last)
    out = []
    for p in permutations(tail[:3]):
        h = tail[3:] + p
        cap, x = 0, h
        while cap < 6 and onecycle(x) not in burned:
            cap += 1
            x = comp(x, a)
        # h = last . m  (everything in sight is right multiplication)
        m = comp(inv(last), h)
        assert comp(last, m) == h
        out.append((m, cap))
    return out


# ---- om: the unique cap-6 exit from a complete traversal --------------------
e6 = exits(ident, 6)
caps6 = sorted(k for _, k in e6)
assert caps6 == [0, 0, 0, 4, 4, 6], caps6
om = [m for m, k in e6 if k == 6]
assert len(om) == 1, "om must be unique"
om = om[0]
s = comp(apow[5], om)                            # traversal at g -> next at g.s
assert order(s) == 5, "the Pentad Lemma element"

# ---- t: the unique cap-6 exit from a length-5 block ------------------------
e5 = exits(ident, 5)
caps5 = sorted(k for _, k in e5)
assert caps5 == [0, 0, 4, 5, 5, 6], caps5
t = [m for m, k in e5 if k == 6]
assert len(t) == 1, "the cap-6 exit of a length-5 block must be unique"
t = t[0]

# ---- equivariance: the same two elements work from every entry point -------
for g in permutations(range(1, n + 1)):
    o6 = exits(g, 6)
    assert sorted(k for _, k in o6) == caps6
    assert [m for m, k in o6 if k == 6] == [om]
    o5 = exits(g, 5)
    assert sorted(k for _, k in o5) == caps5
    assert [m for m, k in o5 if k == 6] == [t]

# ---- the period map --------------------------------------------------------
s4 = comp(comp(s, s), comp(s, s))
P = comp(comp(s4, apow[4]), t)
op = order(P)

print("n = 7, split-free rung v = 124")
print(f"  om            = {om}      ord(a^5.om) = {order(s)}")
print(f"  t (l=5 exit)  = {t}")
print(f"  period map  P = s^4 . a^4 . t = {P}")
print(f"  ord(P)        = {op}")
print()
print("the state needs 25 runs at g, g.P, ..., g.P^24, all in distinct loops")
if op <= 24:
    print(f"  ord(P) = {op} <= 24, so run {op + 1} re-enters the loop of run 1")
    print("  => v = 124 admits no split-free walk of length 5888.")
else:
    print(f"  ord(P) = {op} > 24 -- the period map does not close the rung.")
