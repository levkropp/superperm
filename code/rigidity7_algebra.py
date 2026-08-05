"""Algebra of the two cheap moves at the v = 120 rung of n = 7.

Setting (all established in rigidity7.py): at v = 120 the cover of the 720
rotation classes by entered 2-loops is exact, every class C has a unique
port p(C), and the class-to-class cost is

    w(end_of[g_j], g_{j+k}) = k + 1        (Stride Law, inside a loop)
    w(end_of[g],   out(g))  = 3            (the unique admissible cross move)

so with excess := weight - 2 the only moves of excess 0 or 1 are

    nu  = +1  inside the loop   (excess 0)
    nu^2 = +2 inside the loop   (excess 1)
    om  = out(g)                (excess 1)

and om is a bijection of the 5040 generators.  This file computes the group
structure of <nu, om> and the loop-level transition system, to bound the
length of a maximal excess-<=1 segment without an exponential path search.
"""

from itertools import permutations

n = 7
perms = list(permutations(range(1, n + 1)))
sig = lambda u: u[1:] + u[:1]
delta = lambda u: u[2:] + (u[1], u[0])


def onecycle(u):
    best, x = u, u
    for _ in range(n - 1):
        x = sig(x)
        if x < best:
            best = x
    return best


def twoloop(pi):
    gens, u = [], pi
    for _ in range(6):
        gens.append(u)
        for _ in range(n - 1):
            u = sig(u)
        u = delta(u)
    assert u == pi
    return gens


oc_id = {}
for p in perms:
    oc_id.setdefault(onecycle(p), len(oc_id))

loop_gens, pos = [], {}
for pi in perms:
    if pi in pos:
        continue
    gs = twoloop(pi)
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

nu = {g: loop_gens[pos[g][0]][(pos[g][1] + 1) % 6] for g in pos}
om = {}
for g in pos:
    lid = pos[g][0]
    u = end_of[g]
    good = [u[3:] + t for t in permutations(u[:3])
            if pos[u[3:] + t][0] != lid
            and not (classes_of[pos[u[3:] + t][0]] & classes_of[lid])]
    assert len(good) == 1
    om[g] = good[0]

inv_nu = {v: k for k, v in nu.items()}


def order(f, name):
    seen, cyc = set(), {}
    for g in f:
        if g in seen:
            continue
        k, x = 0, g
        while x not in seen:
            seen.add(x)
            x = f[x]
            k += 1
        cyc[k] = cyc.get(k, 0) + 1
    print(f"  {name:14} cycle type {sorted(cyc.items())}")
    return cyc


print("--- cycle types of om . nu^k ---")
for k in range(6):
    f = {}
    for g in pos:
        x = g
        for _ in range(k):
            x = nu[x]
        f[g] = om[x]
    order(f, f"om.nu^{k}")
print()
f = {g: om[inv_nu[g]] for g in pos}
order(f, "om.nu^-1")
order(om, "om")

# --------------------------------------------------- the loop-level picture
print("\n--- where om sends the 6 generators of a loop ---")
tgt_loops = [sorted({pos[om[g]][0] for g in gs}) for gs in loop_gens]
print(f"  distinct target loops per source loop: "
      f"{sorted({len(t) for t in tgt_loops})}")

# of the 6 target loops, how many are class-disjoint from the source?
# (all of them, by construction) -- but are they disjoint from EACH OTHER?
pw = {}
for lid, ts in enumerate(tgt_loops):
    k = sum(1 for a in range(len(ts)) for b in range(a + 1, len(ts))
            if not (classes_of[ts[a]] & classes_of[ts[b]]))
    pw[k] = pw.get(k, 0) + 1
print(f"  disjoint pairs among the 6 targets   : {sorted(pw.items())} of 15")

# the position om lands on, relative to the source position
print("\n--- landing position of om, inside the target loop ---")
ph = {}
for g in pos:
    ph[pos[om[g]][1]] = ph.get(pos[om[g]][1], 0) + 1
print(f"  target index histogram: {sorted(ph.items())}")
