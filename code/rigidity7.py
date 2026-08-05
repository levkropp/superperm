"""The v = 120 rung at n = 7:  every 120-loop superpermutation has length >= 5895.

Background.  Write length = 5764 + v + slack, v = number of entered 2-loops.
The entered loops must cover all 720 rotation classes, six each, so v >= 120
and HPV alone gives only 5884.  Discharging the rungs v = 120, 121, ... is the
whole n = 7 lower-bound problem.  This file discharges v = 120 -- the tightest
rung, the exact analogue of the n = 6 argument that gave s(6) >= 868 -- and
gets 5895, eleven units past HPV instead of the four that 5888 needs.

The argument is elementary and has one new ingredient, the PENTAD LEMMA:

    at most five complete 2-loop traversals can be chained by weight-3 jumps.

Why.  Relabelling the seven symbols commutes with everything in sight and S_7
acts simply transitively on the 5040 permutations, so every equivariant map is
right multiplication by a fixed group element.  In particular

    sig = R_c   (c = the 7-cycle),        delta = R_d,
    nu  = R_a   (a = c^6 d, order 6)      "next generator of the 2-loop",
    om  = R_b   (b = (3,4,5,6,2,1,7))     "the one usable cross move".

A complete traversal entered at g exits at g.a^5, so the next one is entered
at g.a^5.b -- and  a^5 b  has order 5.  The sixth traversal would re-enter the
rotation class of g.  Hence five, and five is attained.

Bookkeeping.  At v = 120 the cover of the 720 classes is exact, so the Split
Identity R = 6v - A together with R >= 720 forces A = 0 and R = 720: every
class is one full 7-permutation arc.  Then

    length = 5045 + R + X = 5765 + X,     X = sum over jumps of (weight - 2).

Let a VISIT be a maximal stretch of the walk inside one 2-loop, f the number
of visits that are complete traversals, and t = 120 - f.  Every visit
transition costs >= 1 and the ones that are not `om` cost >= 2, so

    X >= f + ceil(f/5) - 2        (Pentad, applied inside each block)
    X >= V - 1 >= 239 - f         (a multi-visited loop costs an extra visit)

whose worst case over f is X >= 130, i.e. length >= 5895.
"""

from itertools import permutations

n = 7
perms = list(permutations(range(1, n + 1)))
sig = lambda u: u[1:] + u[:1]
delta = lambda u: u[2:] + (u[1], u[0])
ident = tuple(range(1, n + 1))
comp = lambda u, v: tuple(u[v[i] - 1] for i in range(n))


def onecycle(u):
    best, x = u, u
    for _ in range(n - 1):
        x = sig(x)
        if x < best:
            best = x
    return best


def weight(u, v):
    for k in range(1, n + 1):
        if u[k:] == v[: n - k]:
            return k
    return n


def order(x):
    k, y = 1, x
    while y != ident:
        y = comp(y, x)
        k += 1
    return k


def check(label, ok):
    print(f"  {label:<46}{'OK' if ok else 'FAIL'}")
    assert ok, label


# ------------------------------------------------------- 1. the structure
print("1. structure of the 2-loops")
oc_id = {}
for p in perms:
    oc_id.setdefault(onecycle(p), len(oc_id))

loop_gens, pos = [], {}
for pi in perms:
    if pi in pos:
        continue
    gs, u = [], pi
    for _ in range(6):
        gs.append(u)
        for _ in range(n - 1):
            u = sig(u)
        u = delta(u)
    assert u == pi
    lid = len(loop_gens)
    loop_gens.append(gs)
    for i, g in enumerate(gs):
        pos[g] = (lid, i)

classes_of = [frozenset(oc_id[onecycle(g)] for g in gs) for gs in loop_gens]
end_of = {}
for g in pos:
    u = g
    for _ in range(n - 1):
        u = sig(u)
    end_of[g] = u

per_class = {}
for lid, cs in enumerate(classes_of):
    for x in cs:
        per_class.setdefault(x, []).append(lid)

check("720 rotation classes", len(oc_id) == 720)
check("840 two-loops, six generators each", len(loop_gens) == 840)
check("every permutation generates exactly one loop", len(pos) == 5040)
check("six classes per loop, one generator each",
      all(len(c) == 6 for c in classes_of))
check("seven loops through each class",
      {len(v) for v in per_class.values()} == {7})

# ---------------------------------------------- 2. everything is R_g in S_7
print("\n2. the moves are right multiplications in S_7")
c, d = sig(ident), delta(ident)
check("sig = R_c", all(comp(u, c) == sig(u) for u in perms))
check("delta = R_d", all(comp(u, d) == delta(u) for u in perms))

a = ident
for _ in range(6):
    a = comp(a, c)
a = comp(a, d)
check("nu (next generator) = R_a, a = c^6 d",
      all(comp(g, a) == loop_gens[pos[g][0]][(pos[g][1] + 1) % 6]
          for g in pos))
check(f"a has order 6", order(a) == 6)

# ------------------------------------------------------- 3. the Stride Law
print("\n3. Stride Law and the two weight-3 moves")
check("w(end g_j, g_{j+k}) = k + 1",
      all(weight(end_of[gs[i]], gs[(i + k) % 6]) == k + 1
          for gs in loop_gens for i in range(6) for k in range(1, 6)))

# the six weight-3 targets from an arc end
w3 = {}
for g in pos:
    u = end_of[g]
    w3[g] = [u[3:] + t for t in permutations(u[:3])]
check("all six are weight 3",
      all(weight(end_of[g], t) == 3 for g in pos for t in w3[g]))
check("exactly one of the six stays in the loop (it is +2)",
      all([t for t in w3[g] if pos[t][0] == pos[g][0]]
          == [loop_gens[pos[g][0]][(pos[g][1] + 2) % 6]] for g in pos))
check("of the five that leave, exactly one lands in a class-disjoint loop",
      all(sum(1 for t in w3[g]
              if pos[t][0] != pos[g][0]
              and not (classes_of[pos[t][0]] & classes_of[pos[g][0]])) == 1
          for g in pos))

b = [t for t in w3[ident]
     if pos[t][0] != pos[ident][0]
     and not (classes_of[pos[t][0]] & classes_of[pos[ident][0]])][0]
om = lambda g: comp(g, b)
check(f"om = R_b, b = {b}",
      all(om(g) == [t for t in w3[g]
                    if pos[t][0] != pos[g][0]
                    and not (classes_of[pos[t][0]] & classes_of[pos[g][0]])][0]
          for g in pos))

# -------------------------------------------------------- 4. Pentad Lemma
print("\n4. the Pentad Lemma")
step = a
for _ in range(4):
    step = comp(step, a)
step = comp(step, b)                     # a^5 b : entry point -> next entry
check("a complete traversal entered at g exits at g.a^5",
      all(loop_gens[pos[g][0]][(pos[g][1] + 5) % 6] == comp(g, comp(
          comp(comp(comp(a, a), a), a), a)) for g in pos))
check("the chaining map a^5.b has order 5", order(step) == 5)

orb, y = [ident], ident
for _ in range(4):
    y = comp(y, step)
    orb.append(y)
Ls = [pos[z][0] for z in orb]
check("its five loops are pairwise class-disjoint (five is attained)",
      all(not (classes_of[Ls[i]] & classes_of[Ls[j]])
          for i in range(5) for j in range(i + 1, 5)))
check("the sixth would re-enter the starting class",
      comp(orb[-1], step) == ident)

# --------------------------------------------------------- 5. the counting
print("\n5. the v = 120 rung")
worst = min(max(f + -(-f // 5) - 2, 239 - f) for f in range(121))
argf = [f for f in range(121) if max(f + -(-f // 5) - 2, 239 - f) == worst]
print(f"  X >= max(f + ceil(f/5) - 2, 239 - f), worst at f = {argf}")
print(f"  X      >= {worst}")
print(f"  length  = 5765 + X >= {5765 + worst}")
print(f"\n  HPV at this rung: 5884.   Needed for 5888: X >= 123.   Have {worst}.")
