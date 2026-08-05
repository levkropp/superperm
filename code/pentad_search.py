"""Search split-free n = 7 walks built from disjoint Pentads.

The 5913 walk decomposes exactly as the theory says it must:

    600 delta joins (cost 0)   96 free joins (cost 1)   23 links (cost >= 2)
    total 148   ->   T = 149

Its 24 free chains are complete `<s>`-orbits of 5 blocks -- the Pentad cap --
and its 23 links cost 52 against a floor of 46.  CP-SAT proves that 52 is
**optimal for that chain set**, so the slack is not in the ordering.  It is in
the COVER.

THE SEARCH SPACE, correctly.  `<s>` acts on GENERATORS, not on loops: the 5040
generators fall into 1008 orbits of 5, each orbit's chain covering exactly 30
classes and the class set being the same for all 5 rotations.  So

    choose 24 pairwise class-disjoint orbits covering all 720 classes
    choose, per orbit, which of its 5 rotations starts the chain
    order the 24 chains

The first two choices fix the cover and the chain endpoints; the third is a
24-node problem.  Together it is a GTSP with 24 clusters of 5 -- 120 states --
which CP-SAT solves exactly.

    T  =  1 + 96 + (link cost)        link cost >= 23 x 2 = 46
    T = 149 is the record;  T <= 147 beats 5912;  T = 144 matches Egan;
    T = 143 hits the floor, length 5907.

Usage:
  python3 code/pentad_search.py --tries 4000 --parts 40
"""

import argparse
import collections
import math
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sftsp                                                      # noqa: E402
from permgraph import weight                                      # noqa: E402
from superstruct import Struct                                    # noqa: E402

def orbits_of(st):
    """The 1008 <s>-orbits of generators, with their 30-class masks."""
    seen, out = set(), []
    for g in st.perms:
        if g in seen:
            continue
        o, x = [], g
        for _ in range(st.n - 2):
            o.append(x)
            seen.add(x)
            x = st.comp(x, st.s)
        cs, y = set(), g
        for _ in range(st.n - 2):
            h = y
            for _ in range(st.n - 1):
                cs.add(st.cls_id[h])
                h = st.comp(h, st.a)
            y = st.comp(y, st.s)
        out.append((o, frozenset(cs)))
    return out


def chain_ends(st, g):
    """(entry, exit) of the chain of complete traversals entered at g."""
    x = g
    for _ in range(st.n - 3):
        x = st.comp(x, st.s)
    return g, st.end_of(st.comp(x, st.apow[st.n - 2]))


def chain_starts(st, g):
    out, x = [], g
    for _ in range(st.n - 2):
        h = x
        for _ in range(st.n - 1):
            out.append(h)
            h = st.comp(h, st.a)
        x = st.comp(x, st.s)
    return out


def partitions(orbs, nclass, rng, tries):
    mask = [sum(1 << c for c in cs) for _, cs in orbs]
    full = (1 << nclass) - 1
    want = nclass // len(orbs[0][1])
    idx = list(range(len(orbs)))
    out, seenp = [], set()
    for _ in range(tries):
        rng.shuffle(idx)
        used, pick = 0, []
        for i in idx:
            if used & mask[i] == 0:
                used |= mask[i]
                pick.append(i)
                if len(pick) == want:
                    break
        if used == full:
            key = frozenset(pick)
            if key not in seenp:
                seenp.add(key)
                out.append(pick)
    return out


def gtsp(st, orbs, pick, cap=4, seconds=60.0, workers=8):
    """Exact GTSP: one rotation per orbit, then order the chains."""
    from ortools.sat.python import cp_model
    states = []
    for ci, oi in enumerate(pick):
        for g in orbs[oi][0]:
            en, ex = chain_ends(st, g)
            states.append((ci, g, en, ex))
    K = len(states)
    DEP = K
    m = cp_model.CpModel()
    lits, arcs = {}, []
    skip = []
    for i in range(K):
        v = m.NewBoolVar(f"u{i}")            # visited
        skip.append(v)
        arcs.append((i, i, v.Not()))         # self-loop == not visited
    for i in range(K):
        for j in range(K):
            if states[i][0] == states[j][0]:
                continue
            c = weight(states[i][3], states[j][2]) - 2
            if c > cap:
                continue
            b = m.NewBoolVar(f"x{i}_{j}")
            lits[(i, j)] = (b, c)
            arcs.append((i, j, b))
    for i in range(K):
        a = m.NewBoolVar(f"s{i}")
        lits[(DEP, i)] = (a, 0)
        arcs.append((DEP, i, a))
        b = m.NewBoolVar(f"e{i}")
        lits[(i, DEP)] = (b, 0)
        arcs.append((i, DEP, b))
    m.AddCircuit(arcs)
    byc = collections.defaultdict(list)
    for i, s_ in enumerate(states):
        byc[s_[0]].append(i)
    for _c, idxs in byc.items():
        m.AddExactlyOne([skip[i] for i in idxs])
    m.Minimize(sum(c * b for (b, c) in lits.values() if c))
    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = seconds
    s.parameters.num_search_workers = workers
    stt = s.Solve(m)
    if stt not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None, None, s.StatusName(stt)
    nxt = {}
    for (i, j), (b, _c) in lits.items():
        if s.Value(b):
            nxt[i] = j
    seq, x = [], nxt.get(DEP)
    while x is not None and x != DEP:
        seq.append(x)
        x = nxt.get(x)
    return int(s.ObjectiveValue()), [states[i][1] for i in seq], s.StatusName(stt)


def main(n, tries, parts, seconds, cap):
    N = n
    st = Struct(N)
    rng = random.Random(11)
    orbs = orbits_of(st)
    nclass = len({st.cls_id[p] for p in st.perms})
    span = len(orbs[0][1])
    blocks = math.factorial(N - 2)
    chains = math.factorial(N - 3)
    freej = blocks - chains
    floor = 2 * (chains - 1)
    egan = (N - 1) * math.factorial(N - 3)
    print(f"\n  n = {N}: {len(orbs)} <s>-orbits of {span} classes, "
          f"{nclass} classes, {nclass // span} per partition")
    print(f"  {blocks} blocks, {chains} chains, {freej} free joins, "
          f"{chains-1} links")
    print(f"  T = {1+freej} + linkcost;  floor linkcost {floor} -> T {1+freej+floor}"
          f"  (= Egan_T - 1 = {egan-1});  Egan_T = {egan}")
    ps = partitions(orbs, nclass, rng, tries)
    print(f"  {len(ps)} distinct Pentad partitions found")
    best = (10 ** 9, None)
    t0 = time.time()
    for k, pick in enumerate(ps[:parts]):
        cost, gs, status = gtsp(st, orbs, pick, cap=cap, seconds=seconds)
        if cost is None:
            print(f"   part {k:3d}: {status}", flush=True)
            continue
        T = 1 + freej + cost
        flag = ""
        if T < best[0]:
            best = (T, gs)
            flag = "  <-- best"
        print(f"   part {k:3d}: link cost {cost:3d}   T = {T}   "
              f"length {sftsp.base(N)+T}   [{status}]{flag}", flush=True)
    print(f"\n  n = {N}: best T = {best[0]}   length {sftsp.base(N)+best[0]}"
          f"   floor {1+freej+floor}   EXCESS over floor = "
          f"{best[0]-(1+freej+floor)}   Egan_T = {egan}   ({time.time()-t0:.0f}s)")
    known = {5: 7, 6: 30, 7: 148}      # best split-free T known
    if best[1] is not None and best[0] <= known.get(N, 10**9):
        starts = []
        for g in best[1]:
            starts += chain_starts(st, g)
        cov = sftsp.Cover(N, sorted(set(starts), key=starts.index))
        order = [cov.ix[s] for s in starts]
        good, digits, T = sftsp.validate(cov, order, N)
        if good:
            path = f"data/sf{N}_{len(digits)}.txt"
            print(f"  writing {path}")
            with open(path, "w") as fh:
                fh.write("".join(map(str, digits)) + "\n")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=7)
    ap.add_argument("--tries", type=int, default=4000)
    ap.add_argument("--parts", type=int, default=40)
    ap.add_argument("--seconds", type=float, default=60.0)
    ap.add_argument("--cap", type=int, default=4)
    args = ap.parse_args()
    print(__doc__.split("Usage:")[0].strip())
    sys.exit(main(args.n, args.tries, args.parts, args.seconds, args.cap))
