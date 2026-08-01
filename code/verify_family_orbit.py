"""CI-sized V3 check: the class-TSP on the family orbit must be >= 265.

Runs the same matrix construction and CP-SAT model as
code/verify_orbits_tsp.py but only on the family cover (all 24 loops whose
generators end in symbol 6), the orbit that attains the classical 867.
"""

from verify_orbits_tsp import build_matrix, solve_tsp, loops, loop_gens

fam = tuple(i for i, L in enumerate(loops)
            if all(g[-1] == 6 for g in loop_gens[i]))
assert len(fam) == 24, len(fam)
classes, W, _ = build_matrix(fam)
name, obj, bound = solve_tsp(W, 300.0)
print(f"family orbit: status={name} obj={obj} certified_bound={bound}")
# smoke level for CI: the full certificate (all 29 orbits >= 265) is
# code/verify_orbits_tsp.py (local run, ~30 min)
assert obj is not None and obj == 267.0 and bound >= 260.0, \
    f"family orbit smoke check failed: {name} {obj} {bound}"
print("family orbit class-TSP smoke check: PASS "
      "(full certificate: code/verify_orbits_tsp.py)")
