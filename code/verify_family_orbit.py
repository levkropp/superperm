"""CI-sized V3 check: the class-TSP on the family orbit must be >= 265.

Runs the same matrix construction and CP-SAT model as
code/verify_orbits_tsp.py but only on the family cover (all 24 loops whose
generators end in symbol 6), the orbit that attains the classical 867.
"""

from verify_orbits_tsp import build_matrix, solve_tsp, loops, loop_gens

"""CI-sized V3 check: the class-TSP on the family orbit.

Two parts:
  1. deterministic control: the classical construction's class ordering
     costs exactly 267 through the matrix (proves optimum <= 267; no solver
     needed);
  2. smoke-level CP-SAT certified bound >= 260 within the time limit.
The FULL certificate (all 29 orbits certified >= 265) is
code/verify_orbits_tsp.py (local run, ~30 min).
"""

from verify_orbits_tsp import build_matrix, solve_tsp, loops, loop_gens, cid
from classical import recursive_superperm
from permgraph import string_to_path

fam = tuple(i for i, L in enumerate(loops)
            if all(g[-1] == 6 for g in loop_gens[i]))
assert len(fam) == 24, len(fam)
classes, W, _ = build_matrix(fam)
cidx = {c: k for k, c in enumerate(classes)}

# 1) deterministic: classical class ordering costs exactly 267
s = recursive_superperm(6)
path = string_to_path(s, 6)
order, seen = [], set()
for v in path:
    c = cid(v)
    if c not in seen:
        seen.add(c)
        order.append(c)
tot = sum(int(W[cidx[a], cidx[b]]) for a, b in zip(order, order[1:]))
print(f"classical ordering cost: {tot} (+600 = {tot + 600})")
assert tot == 267, tot

# 2) smoke-level certified bound (full certificate: verify_orbits_tsp.py)
name, obj, bound = solve_tsp(W, 300.0)
print(f"family orbit: status={name} obj={obj} certified_bound={bound}")
assert obj is not None and bound >= 260.0, \
    f"family orbit smoke check failed: {name} {obj} {bound}"
print("family orbit class-TSP: PASS "
      "(full certificate: code/verify_orbits_tsp.py)")
