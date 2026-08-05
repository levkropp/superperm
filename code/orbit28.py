"""Orbit 28: is there a split-free 6-superpermutation of length 872?

Every one of the 29 S_6-orbits of exact covers except orbit 28 was certified
OPTIMAL >= 267 by code/verify_orbits_tsp.py.  Orbit 28 came back FEASIBLE at
267 with only 265 proved, so its true optimum is 266 or 267, and since

        length = 844 + E,       E = TSP - 238,

TSP = 266 <=> E = 28 <=> length = 872 = s(6).  So the whole v = 24 case of
"no n = 6 champion is split-free" is this one decision:

        is there a Hamiltonian path of weight 266 over orbit 28's 120 nodes?

The nodes are FIXED: an exact cover assigns each rotation class C a unique
loop, hence a unique generator g_C, hence a unique full arc g_C -> sig^5(g_C).
Only the order of the 120 arcs is free.

ANSWER: NO.  code/orbit28b.c settles it exhaustively -- 2.399e10 nodes over
all 120 possible start nodes, no walk with E <= 28.  Orbit 28's optimum is
267, so all 29 orbits are >= 267 and the v = 24 case is closed:

    no n = 6 champion is split-free with v = 24.

This CP-SAT model is the independent cross-check.  It is slow here: AddCircuit
on 121 nodes with a 90-minute limit does not close the gap, so orbit28b.c is
the primary and this is corroboration.

NOTE ON THE MODEL.  verify_orbits_tsp.py pinned the path start to class 0
(`lits[D,0] == 1`).  Orbit 28's stabilizer has order 6, so that is NOT WLOG:
it shrinks the feasible set and can only push the objective up.  Here the
dummy node is left free, which is the honest Hamiltonian-path relaxation.

Run:  .venv/bin/python code/orbit28.py [seconds]
"""

import json
import sys

import numpy as np
from ortools.sat.python import cp_model

sys.path.insert(0, "code")
from permgraph import all_perms, weight

n = 6
ORBIT = 28
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


def build():
    lids, loops, gen_of = {}, [], {}
    for pi in perms:
        L = twoloop(pi)
        if L not in lids:
            lids[L] = len(loops)
            loops.append(L)
        gen_of[pi] = lids[L]
    loop_gens = [set() for _ in loops]
    for pi in perms:
        loop_gens[gen_of[pi]].add(pi)
    return loop_gens


def cid(u):
    return min(u[k:] + u[:k] for k in range(n))


def matrix(cover, loop_gens):
    # loop_gens[li] holds exactly the 5 generators of loop li, one per class
    # (HPV Prop 1), so each class gets a unique arc start -- no choice here.
    gen_of_class = {}
    for li in cover:
        assert len(loop_gens[li]) == 5, len(loop_gens[li])
        for g in loop_gens[li]:
            assert cid(g) not in gen_of_class
            gen_of_class[cid(g)] = g
    assert len(gen_of_class) == 120, len(gen_of_class)
    classes = sorted(gen_of_class)
    W = np.zeros((120, 120), dtype=np.int32)
    for i, ci in enumerate(classes):
        g = gen_of_class[ci]
        end = g[-1:] + g[:-1]                    # sig^5(g), the arc's last perm
        for j, cj in enumerate(classes):
            if i != j:
                W[i, j] = weight(end, gen_of_class[cj])
    return classes, W, gen_of_class


def model_for(W, ub):
    """Hamiltonian path over 120 nodes, free endpoints, via a dummy node.

    Always MINIMIZE.  A pure satisfaction model (`Add(cost <= b)` with no
    objective) leaves AddCircuit's search unguided and times out even at the
    budget where a solution is known to exist.
    """
    N, D = 120, 120
    m = cp_model.CpModel()
    lits, arcs = {}, []
    for i in range(N + 1):
        for j in range(N + 1):
            if i == j:
                continue
            b = m.NewBoolVar(f"x{i}_{j}")
            lits[i, j] = b
            arcs.append((i, j, b))
    m.AddCircuit(arcs)
    cost = sum(int(W[i, j]) * lits[i, j]
               for (i, j) in lits if i != D and j != D)
    m.Add(cost <= ub)          # 267 is known feasible, so this is valid
    m.Minimize(cost)
    return m


def validate(gen_of_class):
    """The instance itself, checked without reference to how it was built.

    An exact cover must give one arc start per class whose 120 full arcs tile
    all 720 permutations, and delta out of the arc ends must close up into 24
    five-cycles -- the cover loops.  This is what makes the arc starts FIXED,
    and it is also exactly the structure code/orbit28b.c prunes with.
    """
    starts = list(gen_of_class.values())
    assert len({cid(g) for g in starts}) == 120

    seen = []
    for g in starts:
        u = g
        for _ in range(n):
            seen.append(u)
            u = sig(u)
    assert len(seen) == 720 and len(set(seen)) == 720, "arcs do not tile S_6"

    S = set(starts)
    nxt = {}
    for g in starts:
        d = delta(g[-1:] + g[:-1])       # delta out of sig^5(g), the arc end
        assert d in S, "delta leaves the cover"
        nxt[g] = d
    cyc, done = [], set()
    for g in starts:
        if g in done:
            continue
        c, x = 0, g
        while x not in done:
            done.add(x)
            c += 1
            x = nxt[x]
        cyc.append(c)
    assert sorted(set(cyc)) == [5] and len(cyc) == 24, cyc
    print("  instance OK: 120 arcs tile S_6, delta closes 24 five-cycles")


def run(m, seconds):
    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = seconds
    s.parameters.num_search_workers = 15
    st = s.Solve(m)
    return s.StatusName(st), s


if __name__ == "__main__":
    secs = float(sys.argv[1]) if len(sys.argv) > 1 else 600.0
    reps = json.load(open("data/orbits29.json"))
    cover = tuple(reps[ORBIT]["cover"])
    print(f"orbit {ORBIT}: stabilizer {reps[ORBIT]['stabilizer']}, "
          f"cover {list(cover)}")

    loop_gens = build()
    classes, W, gen_of_class = matrix(cover, loop_gens)
    validate(gen_of_class)
    off = W[np.triu_indices(120, 1)]
    print(f"jump weights present: {sorted(set(W.flatten().tolist()) - {0})}, "
          f"min off-diagonal {off.min()}")

    st, s = run(model_for(W, 267), secs)
    obj = s.ObjectiveValue() if st in ("OPTIMAL", "FEASIBLE") else None
    print(f"\nstatus={st}  objective={obj}  bound={s.BestObjectiveBound()}")

    # Gate: 267 is known achievable, so anything else is a modelling error.
    assert st != "INFEASIBLE", "GATE FAILED: 267 is known feasible"

    if st == "OPTIMAL" and obj == 267:
        print("  => orbit 28's optimum is 267, so E >= 29 and length >= 873.")
        print("     With the other 28 orbits already >= 267, v = 24 is CLOSED.")
    elif obj is not None and obj <= 266:
        print("  => a split-free 872 EXISTS: the hypothesis is FALSE at n = 6.")
    else:
        print("  => inconclusive (time limit); rerun with more seconds.")
