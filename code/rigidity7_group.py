"""The v = 120 rung of n = 7, in its natural group-theoretic clothing.

Everything in the rung (rotation classes, 2-loops, the Stride Law, the unique
cross move) is equivariant under relabelling the seven symbols, and S_7 acts
simply transitively on the 5040 permutations.  So every equivariant map on
permutations is right multiplication by a fixed element of S_7.  Concretely,
writing permutations as bijections [7] -> [7]:

    sig(u)   = u . c        c = the 7-cycle on positions
    delta(u) = u . d
    nu(u)    = u . a        a = c^6 d,  the "next generator of the loop"
    om(u)    = u . b        b = the unique admissible cross move

Then, with A = <a> (order 6) and C = <c> (order 7):

    rotation class of u  =  u C      (720 of them)
    2-loop of u          =  u A      (840 of them)
    classes met by uA    =  the classes inside u A C

so two loops are class-disjoint iff their AC-sets are disjoint.  If <a, c> is
a group of order 42 -- the Frobenius group F_42 = AGL(1,7) -- then AC = F_42
and an exact cover of the 720 classes by disjoint loops is precisely a choice
of ONE loop inside each of the 120 left cosets of F_42.  This file checks all
of that.
"""

from itertools import permutations

n = 7
perms = list(permutations(range(1, n + 1)))
S = set(perms)


def comp(u, v):
    """u . v : apply v to positions first (u[v[i]-1])."""
    return tuple(u[v[i] - 1] for i in range(n))


ident = tuple(range(1, n + 1))
sig = lambda u: u[1:] + u[:1]
delta = lambda u: u[2:] + (u[1], u[0])

c = sig(ident)
d = delta(ident)
assert all(comp(u, c) == sig(u) for u in perms), "sig is right mult by c"
assert all(comp(u, d) == delta(u) for u in perms), "delta is right mult by d"
print("sig = R_c, delta = R_d          : True")

a = ident
for _ in range(6):
    a = comp(a, c)
a = comp(a, d)                       # a = c^6 d


def gen(elts):
    grp, frontier = {ident}, [ident]
    while frontier:
        x = frontier.pop()
        for y in elts:
            z = comp(x, y)
            if z not in grp:
                grp.add(z)
                frontier.append(z)
    return grp


def ordr(x):
    k, y = 1, x
    while y != ident:
        y = comp(y, x)
        k += 1
    return k


A = gen([a])
C = gen([c])
F = gen([a, c])
print(f"order of a                      : {ordr(a)}   |A| = {len(A)}")
print(f"order of c                      : {ordr(c)}   |C| = {len(C)}")
print(f"<a, c>                          : order {len(F)}"
      f"  ({'F_42 = AGL(1,7)' if len(F) == 42 else 'NOT 42'})")
inv_a = tuple(sorted(range(1, n + 1), key=lambda t: a[t - 1]))
assert comp(a, inv_a) == ident
print(f"a normalises C                  : "
      f"{all(comp(comp(inv_a, x), a) in C for x in C)}")

# --------------------------------------------------------------- find b = om
def onecycle(u):
    best, x = u, u
    for _ in range(n - 1):
        x = sig(x)
        if x < best:
            best = x
    return best


loop_of = {}
for u in perms:
    if u in loop_of:
        continue
    x, gs = u, []
    for _ in range(6):
        gs.append(x)
        x = comp(x, a)
    for g in gs:
        loop_of[g] = frozenset(gs)

cls_of = {u: onecycle(u) for u in perms}
loopcls = {L: frozenset(cls_of[g] for g in L) for L in set(loop_of.values())}

u = ident
end = u
for _ in range(n - 1):
    end = sig(end)
cands = [end[3:] + t for t in permutations(end[:3])
         if loop_of[end[3:] + t] != loop_of[u]
         and not (loopcls[loop_of[end[3:] + t]] & loopcls[loop_of[u]])]
assert len(cands) == 1
b = cands[0]
print(f"\nb = om(identity)                : {b}   order {ordr(b)}")
print(f"b in F_42                       : {b in F}")

# verify om = R_b globally
ok = True
for u in perms:
    e = u
    for _ in range(n - 1):
        e = sig(e)
    good = [e[3:] + t for t in permutations(e[:3])
            if loop_of[e[3:] + t] != loop_of[u]
            and not (loopcls[loop_of[e[3:] + t]] & loopcls[loop_of[u]])]
    if len(good) != 1 or good[0] != comp(u, b):
        ok = False
        break
print(f"om = R_b for all 5040 u         : {ok}")

print("\norders of a^k b (the visit-then-exit moves):")
x = ident
for k in range(6):
    print(f"  k = {k}:  order {ordr(comp(x, b))}")
    x = comp(x, a)

# --------------------------------------------------------- THE RUNG LEMMA
# A "visit" is a maximal stretch of the walk inside one 2-loop; it is FULL if
# it covers all 6 classes of that loop, which (no class twice) forces its five
# moves to be nu, nu, nu, nu, nu -- entry at g, exit at g.a^5.  The next visit
# then starts at g.a^5.b.  So consecutive full visits advance the entry point
# by right multiplication by a^5 b, whose order is 5: the SIXTH would re-enter
# the class of g.  Hence at most five consecutive full visits.

full_step = comp(comp(ident, a), ident)
x = ident
for _ in range(5):
    x = comp(x, a)
full_step = comp(x, b)
print(f"\n--- the rung lemma ---")
print(f"entry map of a full visit, a^5.b: order {ordr(full_step)}")

orb = [ident]
y = ident
for _ in range(ordr(full_step) - 1):
    y = comp(y, full_step)
    orb.append(y)
Ls = [loop_of[z] for z in orb]
pair_disjoint = all(not (loopcls[Ls[i]] & loopcls[Ls[j]])
                    for i in range(len(Ls)) for j in range(i + 1, len(Ls)))
print(f"its {len(orb)} loops pairwise class-disjoint : {pair_disjoint}"
      f"   (so five IS attained)")

# excess = sum over jumps of (weight - 2);  length = 4327 + 1438 + excess.
#   in-visit moves cost 0 (nu) or 1 (nu^2)
#   the V-1 visit transitions cost >= 1, and >= 2 unless they are om
#   f = #loops visited exactly once  (their single visit is full)
#   t = 120 - f  multi-visited loops  =>  V >= 120 + t,  q := V - f
# The f full visits sit in <= q+1 maximal blocks of consecutive full visits,
# each of which splits into om-stretches of <= 5, so
#   #expensive >= ceil(f/5) - (q+1)   and   excess >= (V-1) + ceil(f/5) - q - 1
#                                            = f + ceil(f/5) - 2.
# Independently excess >= V - 1 >= 239 - f.
print("\n--- excess >= max(f + ceil(f/5) - 2, 239 - f) over f = 0..120 ---")
bound = min(max(f + -(-f // 5) - 2, 239 - f) for f in range(121))
arg = [f for f in range(121) if max(f + -(-f // 5) - 2, 239 - f) == bound]
print(f"  worst f              : {arg}")
print(f"  excess >= {bound}")
print(f"  T      >= {1438 + bound}")
print(f"  length >= {4327 + 1438 + bound}    (HPV at v=120 gives 5884)")
