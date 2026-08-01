"""V3 verification: per-orbit class-TSP certification for the s(6) >= 868 scheme.

For each of the 29 orbit-representative exact covers (from /tmp/sp/orbits6.pkl,
cross-checked against our own DLX enumeration), build the 120-city matrix:
  entry of class C = its cover loop's generator g_C (unique per class),
  exit  = sig^5(g_C) (the rotation predecessor of g_C in C),
  jump(C, C') = weight(exit_C, entry_C').
Min Hamiltonian path weight over the 120 classes (dummy-node cycle trick,
path start fixed at class 0).  The v=24 path weight = 600 + TSP.

Certify TSP >= 265 on EVERY orbit (agent claim: 267 except two orbits at
certified 265).  Any orbit below 265 breaks the scheme's fallback; at 265+
the bound s(6) >= 868 holds via the v>=25 channel.
"""

import json
import sys
import numpy as np
from ortools.sat.python import cp_model

from permgraph import all_perms, weight

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


lids, loops = {}, []
gen_of = {}
for pi in perms:
    L = twoloop(pi)
    if L not in lids:
        lids[L] = len(loops)
        loops.append(L)
    gen_of[pi] = lids[L]

# generator set per loop: the 5 vertices that generate it (HPV Prop 1)
loop_gens = [set() for _ in loops]
for pi in perms:
    loop_gens[gen_of[pi]].add(pi)


def cid(u):
    return min(u[k:] + u[:k] for k in range(n))


def build_matrix(cover):
    """cover: tuple of 24 loop ids. Returns (classes, W) with classes the
    120 class-canonical ids, W[i][j] = jump weight i->j."""
    gen_of_class = {}
    for li in cover:
        for g in loop_gens[li]:
            gen_of_class.setdefault(cid(g), g)
    assert len(gen_of_class) == 120, len(gen_of_class)
    classes = sorted(gen_of_class)
    N = len(classes)
    W = np.zeros((N, N), dtype=np.int32)
    for i, ci in enumerate(classes):
        exit_i = gen_of_class[ci][1:] + gen_of_class[ci][:1]  # sig? no:
        exit_i = gen_of_class[ci][-1:] + gen_of_class[ci][:-1]  # sig^5
        for j, cj in enumerate(classes):
            if i != j:
                W[i, j] = weight(exit_i, gen_of_class[cj])
    return classes, W, gen_of_class


def solve_tsp(W, time_limit=300.0):
    N = W.shape[0]
    D = N
    model = cp_model.CpModel()
    lits = {}
    arcs = []
    for i in range(N + 1):
        for j in range(N + 1):
            if i == j:
                continue
            b = model.NewBoolVar(f"x_{i}_{j}")
            lits[i, j] = b
            arcs.append((i, j, b))
    model.AddCircuit(arcs)
    model.Add(lits[D, 0] == 1)

    def w(i, j):
        return 0 if (i == D or j == D) else int(W[i, j])
    model.Minimize(sum(w(i, j) * lits[i, j] for (i, j) in lits))
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.num_search_workers = 15
    status = solver.Solve(model)
    return (solver.StatusName(status),
            solver.ObjectiveValue() if status in (cp_model.OPTIMAL,
                                                  cp_model.FEASIBLE) else None,
            solver.BestObjectiveBound())


def main():
    reps = json.load(open("data/orbits29.json"))
    limit = float(sys.argv[1]) if len(sys.argv) > 1 else 300.0
    results = []
    for k, rep in enumerate(reps):
        classes, W, _ = build_matrix(tuple(rep["cover"]))
        name, obj, bound = solve_tsp(W, limit)
        line = (f"orbit {k:2d} (size {rep['orbit_size']}): status={name} "
                f"obj={obj} certified_bound={bound}")
        print(line, flush=True)
        results.append({"orbit": k, "orbit_size": rep["orbit_size"],
                        "status": name, "objective": obj,
                        "certified_bound": bound})
    bad = [r for r in results if r["certified_bound"] < 265]
    print(f"\nALL {len(results)} orbits certified >= 265: {not bad}",
          flush=True)
    assert not bad, f"BELOW 265: {bad}"
    print("V3 per-orbit class-TSP: PASS", flush=True)


if __name__ == "__main__":
    main()
