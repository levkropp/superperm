"""Can 24 disjoint Pentads be linked by 23 weight-4 jumps?  (n = 7)

`EGAN1L` [THM] gives `v = (n-2)!  =>  length >= Egan(n) - 1`, which at n = 7 is
5907 and already excludes the exact-cover rung for champions.  The `+1` would
make it 5908, and at n = 8 the same `+1` would take 46204 to 46205 and exclude
that rung there too, where the bound currently only ties the record.

At n = 6 the `+1` is a theorem: `T = 29` forces six full `<s>`-orbits covering
the 120 classes -- 8640 such covers -- linked by five weight-4 jumps, and **0 of
the 8640** can be so linked.  The n = 7 analogue is exactly:

    T = 143  forces  24 disjoint Pentads covering all 720 classes,
             one rotation chosen per Pentad,
             ordered into a path whose 23 links ALL have weight 4.

So it is a FEASIBILITY question, not an optimisation, and every edge of cost
!= 2 can simply be deleted.  That is what makes it tractable where the
optimisation was not: `code/pentad_search.py` had to price 1507 partitions one
at a time and could only ever be a search; this model quantifies over ALL
partitions at once.

    INFEASIBLE  ->  v = 120 => T >= 144, length >= 5908
    FEASIBLE    ->  a split-free 5907, which would BEAT the 5912 record

Both outcomes are worth having.  A feasible answer is checked by rebuilding the
string and validating it, because a solver bug that invents a superpermutation
is far likelier than a 5907.

Usage:
  python3 code/egan1p.py --seconds 900
"""

import argparse
import collections
import math
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pentad_search as ps                                        # noqa: E402
import sftsp                                                      # noqa: E402
from permgraph import weight                                      # noqa: E402
from superstruct import Struct                                    # noqa: E402


def build(n, seconds, workers, verbose=True, fix_first=True):
    """Feasibility model.  `fix_first` applies the symmetry reduction.

    Left multiplication by any g is a relabelling of symbols: it preserves
    weights, permutes classes, and commutes with right multiplication by a and
    b -- all three verified directly.  So the group acts transitively on the
    possible starting generators, and WLOG **the path's first chain starts at
    the identity**.  That is a sound n!-fold reduction, and it also prunes: any
    orbit sharing a class with the identity's chain can never be chosen, so its
    states are never created at all.  That is the memory win -- the n = 8 model
    was OOM-killed at 23.8 GB without it.
    """
    from ortools.sat.python import cp_model
    st = Struct(n)
    orbs = ps.orbits_of(st)
    nclass = len({st.cls_id[p] for p in st.perms})
    span = len(orbs[0][1])
    K = nclass // span                     # chains needed
    if verbose:
        print(f"\n  n = {n}: {len(orbs)} orbits x {len(orbs[0][0])} rotations, "
              f"{nclass} classes, need {K} disjoint chains")

    first_oi = None
    dead = set()
    if fix_first:
        for oi, (rots, cs) in enumerate(orbs):
            if st.ident in rots:
                first_oi, first_cs = oi, cs
                break
        assert first_oi is not None
        for oi, (_r, cs) in enumerate(orbs):
            if oi != first_oi and (cs & first_cs):
                dead.add(oi)
        if verbose:
            print(f"  symmetry: first chain fixed at the identity; "
                  f"{len(dead)} of {len(orbs)} orbits pruned as class-clashing")

    states = []                            # (orbit, rotation g, entry, exit)
    for oi, (rots, _cs) in enumerate(orbs):
        if oi in dead:
            continue
        for g in rots:
            if oi == first_oi and g != st.ident:
                continue               # the fixed chain has its rotation fixed
            en, ex = ps.chain_ends(st, g)
            states.append((oi, g, en, ex))
    S = len(states)
    entry_at = {}
    for i, (_oi, _g, en, _ex) in enumerate(states):
        entry_at.setdefault(en, []).append(i)

    m = cp_model.CpModel()
    use = [m.NewBoolVar(f"u{i}") for i in range(S)]          # state selected
    pick = [m.NewBoolVar(f"o{i}") for i in range(len(orbs))]  # orbit selected

    byorb = collections.defaultdict(list)
    for i, s_ in enumerate(states):
        byorb[s_[0]].append(i)
    for oi, idxs in byorb.items():
        m.Add(sum(use[i] for i in idxs) == pick[oi])
    for oi in dead:
        assert oi not in byorb

    for oi in dead:
        m.Add(pick[oi] == 0)
    bycls = collections.defaultdict(list)
    for oi, (_r, cs) in enumerate(orbs):
        if oi in dead:
            continue
        for c in cs:
            bycls[c].append(oi)
    for c, ois in bycls.items():
        m.AddExactlyOne([pick[oi] for oi in ois])            # exact cover
    m.Add(sum(pick) == K)
    if first_oi is not None:
        m.Add(pick[first_oi] == 1)

    arcs, nedge = [], 0
    for i in range(S):
        arcs.append((i, i, use[i].Not()))
    # A weight-4 target of `ex` is ex[4:] + (a permutation of ex[:4]); there are
    # 4! = 24 candidates, against 40,320 if the whole group is scanned.  At n = 8
    # that is the difference between 1.45e9 weight() calls and 8.6e5.
    from itertools import permutations as _perms
    for i, (oi, _g, _en, ex) in enumerate(states):
        for q in _perms(ex[:4]):
            t = ex[4:] + q
            if weight(ex, t) != 4:                            # cost 2 ONLY
                continue
            for j in entry_at.get(t, ()):
                if states[j][0] == oi:
                    continue
                b = m.NewBoolVar(f"x{i}_{j}")
                arcs.append((i, j, b))
                m.AddImplication(b, use[i])
                m.AddImplication(b, use[j])
                nedge += 1
    DEP = S
    for i in range(S):
        a = m.NewBoolVar(f"s{i}")
        arcs.append((DEP, i, a))
        m.AddImplication(a, use[i])
        if first_oi is not None:
            m.Add(a == (1 if states[i][0] == first_oi else 0))
        z = m.NewBoolVar(f"e{i}")
        arcs.append((i, DEP, z))
        m.AddImplication(z, use[i])
    m.AddCircuit(arcs)

    if verbose:
        print(f"  {S} states, {nedge} weight-4 edges "
              f"({nedge/max(1,S):.1f} per state)")
    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = seconds
    s.parameters.num_search_workers = workers
    t0 = time.time()
    status = s.Solve(m)
    name = s.StatusName(status)
    if verbose:
        print(f"  CP-SAT: {name}   ({time.time()-t0:.0f}s)")
    if status == cp_model.INFEASIBLE:
        return name, None
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return name, None
    chosen = [i for i in range(S) if s.Value(use[i])]
    return name, [states[i][1] for i in chosen]


def main(n, seconds, workers):
    name, gs = build(n, seconds, workers)
    egan1 = math.factorial(n - 2) + math.factorial(n - 3) - 1
    if name == "INFEASIBLE":
        print(f"\n  INFEASIBLE: no {math.factorial(n-3)} disjoint chains can be "
              f"linked by weight-4 jumps alone.")
        print(f"  => v = (n-2)! forces T >= {egan1+1}, "
              f"length >= {sftsp.base(n)+egan1+1}   (was {sftsp.base(n)+egan1})")
        return 0
    if gs is None:
        print(f"\n  {name}: undecided in the time limit -- no conclusion")
        return 0
    print(f"\n  FEASIBLE -- rebuilding and validating the witness")
    st = Struct(n)
    starts = []
    for g in gs:
        starts += ps.chain_starts(st, g)
    if len(set(starts)) != len(starts):
        print("  witness repeats an arc start -- REJECTED")
        return 1
    cov = sftsp.Cover(n, starts)
    order = [cov.ix[x] for x in starts]
    good, digits, T = sftsp.validate(cov, order, n)
    print(f"  T = {T}, length {len(digits)}   valid={good}")
    return 0 if good else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=7)
    ap.add_argument("--seconds", type=float, default=900.0)
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()
    print(__doc__.split("Usage:")[0].strip())
    sys.exit(main(args.n, args.seconds, args.workers))
