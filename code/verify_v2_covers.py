"""Verification V2: exact-cover enumeration.

Every v=24 path forces an exact cover of the 120 1-cycles (rotation
classes) by 24 disjoint 2-loops chosen from the 144-loop family.

This script independently enumerates all exact covers with a DLX-style
recursion and checks the count (10,068) against the shipped data file
`data/covers_10068.npz`.

Run: python code/verify_v2_covers.py   (from the repo root, ~1-2 min)
"""

import numpy as np
from permgraph import all_perms

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
for pi in perms:
    L = twoloop(pi)
    if L not in lids:
        lids[L] = len(loops)
        loops.append(L)
assert len(loops) == 144


def cid(u):
    return min(u[k:] + u[:k] for k in range(n))


class_ids = sorted({cid(p) for p in perms})
cidx = {c: k for k, c in enumerate(class_ids)}
assert len(class_ids) == 120
loop_classes = [sorted({cidx[cid(v)] for v in L}) for L in loops]
assert all(len(c) == 5 for c in loop_classes)

count = 0
collected = []
import sys
sys.setrecursionlimit(100000)


def dlx(chosen, used):
    global count
    if used == (1 << 120) - 1:
        count += 1
        collected.append(tuple(sorted(chosen)))
        return
    for c in range(120):
        if not (used >> c) & 1:
            break
    for li, lcs in enumerate(loop_classes):
        if c in lcs and all(not (used >> x) & 1 for x in lcs):
            dlx(chosen + [li], used | sum(1 << x for x in lcs))


dlx([], 0)
print(f"exact covers enumerated: {count}")
assert count == 10068, count

shipped = np.load("data/covers_10068.npz")["covers"]
mine = np.array(sorted(collected), dtype=np.uint16)
assert mine.shape == shipped.shape and (mine == shipped).all()
print("shipped data/covers_10068.npz matches re-enumeration exactly  [OK]")
print("V2 exact covers: PASS")
