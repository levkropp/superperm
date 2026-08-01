"""Exact ATSP via OR-Tools CP-SAT with a circuit constraint.

Model: one dummy node, 0-weight edges to/from all nodes; a Hamiltonian cycle
through the extended graph is a Hamiltonian path through the original.
CP-SAT's AddCircuit handles 120+ nodes with multi-core search easily.

Usage: python cpsat_tsp.py N [max_seconds]
"""

import sys
from ortools.sat.python import cp_model
from permgraph import build_weight_matrix


def solve(n, max_seconds=300.0, workers=16):
    perms, W = build_weight_matrix(n)
    N = len(perms)
    D = N
    nodes = list(range(N + 1))

    def w(i, j):
        return 0 if (i == D or j == D) else W[i][j]

    model = cp_model.CpModel()
    arcs = []
    literals = {}
    for i in nodes:
        for j in nodes:
            if i == j:
                continue
            b = model.NewBoolVar(f"x_{i}_{j}")
            literals[i, j] = b
            arcs.append((i, j, b))
    model.AddCircuit(arcs)
    # path start fixed at identity (index 0) — symbol-relabelling symmetry
    model.Add(literals[D, 0] == 1)
    model.Minimize(sum(w(i, j) * literals[i, j] for (i, j) in literals))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = max_seconds
    solver.parameters.num_search_workers = workers
    solver.parameters.log_search_progress = True
    status = solver.Solve(model)
    name = solver.StatusName(status)
    obj = solver.ObjectiveValue() if status in (cp_model.OPTIMAL,
                                                cp_model.FEASIBLE) else None
    print(f"n={n}: status={name} bound={solver.BestObjectiveBound()} "
          f"path_weight={obj} -> string length="
          f"{None if obj is None else int(obj) + n}")
    return name, None if obj is None else int(obj) + n


if __name__ == "__main__":
    n = int(sys.argv[1])
    tl = float(sys.argv[2]) if len(sys.argv) > 2 else 300.0
    solve(n, tl)
