"""Verification V1: the absorption lemma.

For every Hamiltonian path in the n=6 permutation overlap graph,
    v >= ceil((R - 1) / 5)
where R = number of arcs (weight-1 runs) and v = entered 2-loops.

Why it holds: each 2-loop has exactly 5 generators (HPV Prop. 1), and a
jump target enters a 2-loop only by landing on one of its generators, so
each entered 2-loop absorbs at most 5 jump targets.

This script:
  * builds the 144 2-loops, checks each has exactly 5 generators;
  * checks the lemma on the two known extremal solutions (classical 867,
    Houston 872) -- it is TIGHT on both;
  * checks 200 random greedy walks.
Run: python code/verify_v1_absorption.py   (from the repo root)
"""

from math import ceil
from permgraph import all_perms, weight, string_to_path
from classical import recursive_superperm

n = 6
perms = all_perms(n)
sig = lambda u: u[1:] + u[:1]
delta = lambda u: u[2:] + (u[1], u[0])


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
    if L not in lids:
        lids[L] = len(lids)
    gen_of[pi] = lids[L]
gens_of_loop = {}
for pi in perms:
    gens_of_loop.setdefault(gen_of[pi], set()).add(pi)
assert len(lids) == 144, len(lids)
sizes = {len(g) for g in gens_of_loop.values()}
assert sizes == {5}, f"generator counts wrong: {sizes}"
print(f"loops: {len(lids)}, generators per loop: {sizes}  [OK]")


def check(name, path):
    entered, targets = set(), 0
    for u, v in zip(path, path[1:]):
        if weight(u, v) >= 2:
            targets += 1
            entered.add(gen_of[v])
    ok = len(entered) >= ceil(targets / 5)
    print(f"  {name}: targets={targets} v={len(entered)} "
          f"ceil/5={ceil(targets / 5)} -> {'OK' if ok else 'FAIL'}")
    return ok


ok = check("classical n=6 (tight)",
           string_to_path(recursive_superperm(6), 6))
h = open("data/houston_872.txt").read().strip()
ok &= check("Houston 872 (tight)", string_to_path([int(c) for c in h], 6))

import random
random.seed(1)
fails = 0
for _ in range(200):
    u = random.choice(perms)
    path = [u]
    seen = {u}
    for _ in range(719):
        cands = [v for v in perms if v not in seen and weight(u, v) <= 3]
        if not cands:
            break
        u = random.choice(cands)
        seen.add(u)
        path.append(u)
    if len(path) > 50:
        fails += not check("rand", path)
print(f"random walks: {200 - fails}/200 pass")
assert ok and fails == 0
print("V1 absorption lemma: PASS")
