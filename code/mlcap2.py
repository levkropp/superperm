#!/usr/bin/env python3
"""MLCAP2: caps of weight-4-linked, pairwise class-disjoint chains of
delta-components, generalising PENTCAP (code/pentcap.py) from complete
Pentads to small delta-components.

COMPONENT MODEL (model B, the task's literal model)

  A 1-loop component is one complete 2-loop L.  Its BURN SET is L's n-1
  rotation classes.  Entry positions: any generator of L (the walk may
  enter the loop at any entry).  Exit positions: any of L's n-1 arc ends
  end_of(g.a^k)  (a weight-4 door may leave from any arc end).

  A 2-loop component is a delta-linked ordered pair (L1, L2, f), exactly
  the way a real row hangs off its parent loop (certificate.py's
  oriented_row): f is a generator of L2, and the delta edge is the
  weight-2 door  x -> f  with x = comp(f, inv(d)) (f = door(x, 2) =
  delta(x));  we require classes(L1) n classes(L2) = {cls(x)}  -- the two
  loops share exactly the parent orbit, as oriented_row enforces.  Burn
  set: classes(L1) union (classes(L2) minus cls(x)) = 2n-3 classes
  (the walk covers the parent orbit during L1's arc and the n-2
  child classes during the row arcs).  Entry positions: any generator of
  L1.  Exit positions: any arc end of L1 or of L2's traversed arcs.

CHAIN: a sequence of components, pairwise burn-disjoint, consecutive
components joined by a genuine weight-4 edge from an exit position of A
to an entry position of B:  t = ex[4:] + q  for q in S_4 with
weight(ex, t) == 4  (the same link semantics as pentcap.py).

All entries of one component are equivalent for chaining (the traversal
covers the same classes and offers the same exit set), so states are
components, not component x entry.

Usage: python3 mlcap2.py --n 8 --ell 2 [--node-cap 60000000]
"""
import argparse
import os
import sys
from itertools import permutations

sys.path.insert(0, '/Users/neo/superperm/code')
from permgraph import weight          # noqa: E402
from superstruct import Struct        # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('--n', type=int, default=6)
ap.add_argument('--ell', type=int, default=1, choices=(1, 2))
ap.add_argument('--node-cap', type=int, default=60_000_000)
args = ap.parse_args()
n = args.n

st = Struct(n)
d = st.delta(st.ident)
dinv = st.inv(d)

# ---- class ids and loop classes --------------------------------------------
loop_cls = [frozenset(st.loop_classes(lid)) for lid in range(st.n_loops)]
loops_of_class = [[] for _ in range(st.n_classes)]
for lid, cs in enumerate(loop_cls):
    for c in cs:
        loops_of_class[c].append(lid)

# ---- components --------------------------------------------------------------
# a component: dict with keys burn (frozenset of class ids), first_loops
# (tuple of loop ids whose generators are entry positions), exits (tuple of
# perms = arc ends), label (for printing)
comps = []
for lid in range(st.n_loops):
    gens = st.loop_gens[lid]
    exits = tuple(st.end_of(g) for g in gens)
    comps.append({
        'burn': loop_cls[lid],
        'first_loops': (lid,),
        'exits': exits,
        'label': f'L{lid}',
    })

if args.ell == 2:
    for lid2 in range(st.n_loops):
        cls2 = loop_cls[lid2]
        for f in st.loop_gens[lid2]:
            x = st.comp(f, dinv)          # delta edge x -> f (door(x,2)=f)
            pc = st.cls_id[x]             # parent orbit class
            for lid1 in loops_of_class[pc]:
                if lid1 == lid2:
                    continue
                cls1 = loop_cls[lid1]
                if len(cls1 & cls2) != 1:
                    continue              # must share exactly the parent orbit
                burn = cls1 | (cls2 - {pc})
                gens1 = st.loop_gens[lid1]
                # exit positions: arc ends of L1 and of L2's child arcs
                # (L2's arcs from f through f.a^{n-3}; the arc of f.a^{n-2}
                # is the parent orbit, covered by L1)
                exits = [st.end_of(g) for g in gens1]
                y = f
                for _ in range(n - 2):
                    exits.append(st.end_of(y))
                    y = st.comp(y, st.a)
                comps.append({
                    'burn': burn,
                    'first_loops': (lid1,),
                    'exits': tuple(exits),
                    'label': f'({lid1},{lid2},f)',
                })

ncomp = len(comps)
# burn sets as integer bitmasks for fast disjointness checks
for cp in comps:
    m = 0
    for c in cp['burn']:
        m |= 1 << c
    cp['mask'] = m
print(f'n={n} ell<={args.ell}: {ncomp} components '
      f'({st.n_loops} single loops)', flush=True)

# ---- entry index: generator -> components that can be entered there --------
ent = {}
for j, cp in enumerate(comps):
    for lid in cp['first_loops']:
        for g in st.loop_gens[lid]:
            ent.setdefault(g, []).append(j)

# ---- DFS --------------------------------------------------------------------
best = [0]
nodes = [0]
best_path = []

_tcache = {}


def targets_of(ex):
    """All genuine weight-4 targets from arc end ex (pentcap semantics)."""
    ts = _tcache.get(ex)
    if ts is None:
        ts = []
        for q in permutations(ex[:4]):
            t = ex[4:] + q
            if weight(ex, t) == 4:
                ts.append(t)
        _tcache[ex] = ts
    return ts


def succ(i):
    out = []
    seen_j = set()
    for ex in comps[i]['exits']:
        for t in targets_of(ex):
            for j in ent.get(t, ()):
                if j != i and j not in seen_j:
                    seen_j.add(j)
                    out.append(j)
    return out


def dfs(i, used, d, path):
    nodes[0] += 1
    if nodes[0] > args.node_cap:
        raise TimeoutError
    if d > best[0]:
        best[0] = d
        best_path.clear()
        best_path.extend(path)
        print(f'  n={n} ell<={args.ell} depth {d} (nodes {nodes[0]})',
              flush=True)
    for j in succ(i):
        bj = comps[j]['mask']
        if used & bj:
            continue
        dfs(j, used | bj, d + 1, path + [j])


done = True
try:
    for i0 in range(ncomp):
        dfs(i0, comps[i0]['mask'], 1, [i0])
except TimeoutError:
    done = False

print(f'RESULT n={n} ell<={args.ell}: cap = {best[0]}  nodes = {nodes[0]}  '
      f'exhaustive = {done}')
if best_path:
    labels = [comps[j]['label'] for j in best_path]
    print('example chain:', labels[:30])
    # loop ids involved
    lid_list = []
    for j in best_path:
        lid_list.append([int(x) for x in
                         str(comps[j]['label']).replace('(', '').replace(')', '')
                         .replace('L', '').split(',') if x.strip().lstrip('-').isdigit()])
    print('loops per chain element:', lid_list[:30])
