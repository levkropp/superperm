"""How many disjoint Pentads can weight-4 jumps link?  Far fewer than needed.

`EGAN1P` settled rung 0 at n = 6, 7, 8 with CP-SAT infeasibility certificates,
but gave no reason.  The reason is much blunter than "infeasible", and it is
this: a weight-4-linked sequence of pairwise class-disjoint Pentads is capped at
a tiny constant, while the rung needs `(n-3)!` of them.

    n     chains needed (n-3)!     longest weight-4-linked sequence
    6                        6                                   3
    7                       24                                   4
    8                      120                                   5

i.e. the cap is **n - 3**, against `(n-3)!` -- so rung 0 fails by a factor that
grows factorially, not by a hair.  Each search runs to completion (5,040 /
75,600 / 1,249,920 nodes), so these are exact, not bounds.

Two candidate explanations were killed first, cheaply, and are worth recording:

  * a SUBGROUP obstruction.  By homogeneity a chain entered at `g` exits at
    `g.E` for fixed `E`, so chain entries walk a Cayley graph with steps
    `F = E.c^(n-1).mu` over the weight-4 `mu`.  If `<F>` were proper the walk
    would be confined -- but `<F>` is ALL of `S_n` at n = 5, 6, 7.  Dead.
  * a FAMILY/parity obstruction.  Weight-4 jumps preserve the H-coset 25% of
    the time and shift it by every nonzero amount otherwise, so there is no
    parity invariant to exploit.  Dead.

What actually bites is class-disjointness: each Pentad burns `(n-1)(n-2)`
classes, and after a few links there is no weight-4 target left whose Pentad
avoids all of them.

Usage:
  python3 code/pentcap.py --n 8
"""

import argparse
import collections
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pentad_search as ps
from superstruct import Struct
from permgraph import weight
from itertools import permutations
_ap=argparse.ArgumentParser(); _ap.add_argument("--n",type=int,default=8)
n=_ap.parse_args().n
st=Struct(n); orbs=ps.orbits_of(st)
K=len({st.cls_id[p] for p in st.perms})//len(orbs[0][1])
oc={oi:frozenset(cs) for oi,(r,cs) in enumerate(orbs)}
states=[]
for oi,(rots,_cs) in enumerate(orbs):
    for g in rots: states.append((oi,g))
ent={}
for i,(oi,g) in enumerate(states): ent.setdefault(g,[]).append(i)
succ=collections.defaultdict(list)
for i,(oi,g) in enumerate(states):
    _e,ex=ps.chain_ends(st,g)
    for q in permutations(ex[:4]):
        t=ex[4:]+q
        if weight(ex,t)!=4: continue
        for j in ent.get(t,()):
            if states[j][0]!=oi: succ[i].append(j)
print(f'  n={n}: {len(states)} states, {sum(len(v) for v in succ.values())} links',flush=True)
best=[0]; nodes=[0]
def dfs(i,used,cls,d):
    nodes[0]+=1
    if nodes[0]>60_000_000: raise TimeoutError
    if d>best[0]:
        best[0]=d; print(f'    depth {d}',flush=True)
    for j in succ.get(i,()):
        oj=states[j][0]
        if oj in used or (cls & oc[oj]): continue
        dfs(j,used|{oj},cls|oc[oj],d+1)
try:
    for s0 in range(len(states)): dfs(s0,{states[s0][0]},set(oc[states[s0][0]]),1)
    done=True
except TimeoutError: done=False
print(f'  n={n}: need {K}.  Longest = {best[0]}  (n-3 = {n-3})  nodes={nodes[0]} exhaustive={done}')
