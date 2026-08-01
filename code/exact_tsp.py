"""Exact ATSP solve of the permutation overlap graph via PuLP/CBC.

Minimal superpermutation length = n + min-weight Hamiltonian path.
Model: add a dummy node with 0-weight edges to/from every node; a min-weight
Hamiltonian cycle through the extended graph = min-weight Hamiltonian path
through the original.  Symbol-relabelling symmetry lets us fix the node
right after the dummy (path start) to the identity permutation.

Usage: python exact_tsp.py N [time_limit_seconds]
"""

import sys
import pulp
from permgraph import build_weight_matrix


def solve(n, time_limit=None, msg=True):
    perms, W = build_weight_matrix(n)
    N = len(perms)
    D = N  # index of dummy node
    nodes = list(range(N + 1))

    def w(i, j):
        if i == D or j == D:
            return 0
        return W[i][j]

    prob = pulp.LpProblem("superperm_atsp", pulp.LpMinimize)
    x = {(i, j): pulp.LpVariable(f"x_{i}_{j}", cat="Binary")
         for i in nodes for j in nodes if i != j}
    prob += pulp.lpSum(w(i, j) * x[i, j] for (i, j) in x)

    for i in nodes:
        prob += pulp.lpSum(x[i, j] for j in nodes if j != i) == 1
        prob += pulp.lpSum(x[j, i] for j in nodes if j != i) == 1

    # fix path start: dummy -> identity (index 0)
    prob += x[D, 0] == 1

    # MTZ subtour elimination on real nodes
    u = {i: pulp.LpVariable(f"u_{i}", lowBound=1, upBound=N) for i in range(N)}
    for i in range(N):
        for j in range(N):
            if i != j:
                prob += u[i] - u[j] + N * x[i, j] <= N - 1

    solver = pulp.PULP_CBC_CMD(msg=msg, timeLimit=time_limit) if time_limit \
        else pulp.PULP_CBC_CMD(msg=msg)
    status = prob.solve(solver)
    status_str = pulp.LpStatus[prob.status]
    obj = pulp.value(prob.objective)
    if msg:
        print(f"n={n}: status={status_str} path_weight={obj} "
              f"-> string length={None if obj is None else int(obj) + n}")
    return status_str, (None if obj is None else int(obj) + n)


if __name__ == "__main__":
    n = int(sys.argv[1])
    tl = int(sys.argv[2]) if len(sys.argv) > 2 else None
    solve(n, tl)
