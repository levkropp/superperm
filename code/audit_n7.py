"""Audit of the n=7 loop structure and the length/weight bookkeeping.

Independent of the repo's n=6 scripts: rebuilds the 2-loop structure at
n=7 from scratch, then checks (a) the covering claim behind the "141-loop
question" and (b) the v-coordinates of every published bound.
"""

from itertools import permutations

n = 7
perms = list(permutations(range(1, n + 1)))
idx = {p: i for i, p in enumerate(perms)}

sig = lambda u: u[1:] + u[:1]
delta = lambda u: u[2:] + (u[1], u[0])


def onecycle(u):
    """Canonical id of the rotation class of u."""
    best = u
    x = u
    for _ in range(n - 1):
        x = sig(x)
        if x < best:
            best = x
    return best


def twoloop(pi):
    seen, out = set(), []
    u = pi
    while u not in seen:
        seen.add(u)
        out.append(u)
        for _ in range(n - 1):
            u = sig(u)
            seen.add(u)
            out.append(u)
        u = delta(u)
    return frozenset(out)


lids, gen_of = {}, {}
for pi in perms:
    L = twoloop(pi)
    lids.setdefault(L, len(lids))
    gen_of[pi] = lids[L]

loops = [None] * len(lids)
for L, i in lids.items():
    loops[i] = L

gens_of_loop = {}
for pi in perms:
    gens_of_loop.setdefault(gen_of[pi], set()).add(pi)

print(f"permutations           : {len(perms)}")
print(f"2-loops                : {len(lids)}")
print(f"loop sizes             : {sorted({len(L) for L in loops})}")
print(f"generators per loop    : {sorted({len(g) for g in gens_of_loop.values()})}")

# one-cycles
ocs = sorted({onecycle(p) for p in perms})
oc_id = {c: i for i, c in enumerate(ocs)}
print(f"one-cycles             : {len(ocs)}")

loop_cycles = [frozenset(oc_id[onecycle(u)] for u in L) for L in loops]
print(f"one-cycles per 2-loop  : {sorted({len(c) for c in loop_cycles})}")

from collections import Counter
cnt = Counter()
for c in loop_cycles:
    for x in c:
        cnt[x] += 1
print(f"2-loops per one-cycle  : {sorted(set(cnt.values()))}")

# ---------------------------------------------------------------- covering
# The README calls this "the knife-edge question": can 141 two-loops cover
# all 720 one-cycles?  Each loop covers 6, so 120 would already suffice if
# an exact cover exists.  Greedy-with-backtracking on the least-covered cell.
print("\n--- exact cover of the 720 one-cycles by disjoint 2-loops ---")
cover_by = [[] for _ in ocs]
for i, c in enumerate(loop_cycles):
    for x in c:
        cover_by[x].append(i)

sol = []


def solve(uncovered):
    if not uncovered:
        return True
    cell = min(uncovered, key=lambda x: sum(
        1 for i in cover_by[x] if loop_cycles[i] <= uncovered))
    for i in cover_by[cell]:
        if loop_cycles[i] <= uncovered:
            sol.append(i)
            if solve(uncovered - loop_cycles[i]):
                return True
            sol.pop()
    return False


import sys
sys.setrecursionlimit(10000)
found = solve(frozenset(range(len(ocs))))
print(f"exact cover found      : {found}  (uses {len(sol)} loops)")
if found:
    assert len(sol) == 120
    union = set()
    for i in sol:
        assert not (union & loop_cycles[i]), "not disjoint"
        union |= loop_cycles[i]
    assert union == set(range(720))
    print("verified               : 120 pairwise-disjoint loops, union = all 720")
    print("=> 141 loops can cover all 720 one-cycles TRIVIALLY (120 + any 21).")

# ------------------------------------------------------------- bookkeeping
print("\n--- length / weight bookkeeping at n = 7 ---")
# min length = n + min Hamiltonian path weight
# HPV:  wt >= n! + ((n-1)!-1) + v - 2 = 5757 + v ; length = wt + 7 >= 5764 + v
BASE_WT, BASE_LEN = 5757, 5764
rows = [
    ("classical bound (HPV)", 5884, None),
    ("Hunter & Raudvere", 5888, None),
    ("Egan/Houston champion", 5906, 142),
    ("Coanda champion", 5907, 140),
    ("L2 champion", 5908, 144),
    ("hypothetical 5905", 5905, None),
]
print(f"{'':26} {'length':>7} {'wt':>6} {'v<=':>5} {'v':>5} {'slack':>6}")
for name, length, v in rows:
    wt = length - n
    vmax = wt - BASE_WT
    slack = "" if v is None else length - BASE_LEN - v
    print(f"{name:26} {length:7} {wt:6} {vmax:5} {str(v if v else ''):>5} {str(slack):>6}")

print(f"""
Reading:  length >= {BASE_LEN} + v, so a string of length L has v <= L - {BASE_LEN}.
  Hunter's 5888 sits at v <= 124 (NOT 131 -- 5757+131=5888 is a units error:
  5757 is a WEIGHT offset, 5888 is a LENGTH).
  A 5905 string has v <= 141, and v >= 120 (covering).  Defect budget = 22.
  n=6 analogue: length >= 843 + v, 871 => v <= 28, v >= 24, budget = 4.
""")
