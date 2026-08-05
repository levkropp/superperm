"""The n=7 relaxed macro-chain system (a6-872 / a7 bundle, section 2).

M_7(G) = max number of macros in a chain with total gap <= G, exact port
equations at every boundary, and pairwise-disjoint class supports.

Break state z = z_0..z_6 (a permutation of 0..6).
    P(z)   = (z_0, z_6, z_1, z_2, z_3, z_4, z_5)      -- marker z_0 fixed
    Inc(z) = { rotClass(P^i z) : 0 <= i < 6 }         -- 6 classes
    A_g(z) = { rotClass(P^i z) : g <= i < 6 }         -- support, size 6-g
    I(z)   = (z_2, z_3, z_4, z_5)
    O(z)   = (z_3, z_4, z_5, z_6)
    macro (z,g): costs g, covers A_g(z), successor z' has I(z') = O(P^g z)

Reference values to reproduce (a7/bundle_v2/A7_5896_PROOF_NOTE.md 3.1):
    M_7(0..10) = 5,5,9,9,13,13,16,16,20,20,24
    nodes      = 31, 85, 349, 1231, 4573, 17143, 62875, 227113,
                 827785, 2945461, 10465987
"""

from itertools import permutations
import sys

N = 7

# ---------------------------------------------------------------- classes
_rotclass = {}
for p in permutations(range(N)):
    best = min(tuple(p[i:] + p[:i]) for i in range(N))
    _rotclass[p] = best
_cls_id = {c: i for i, c in enumerate(sorted(set(_rotclass.values())))}
assert len(_cls_id) == 720, len(_cls_id)
ROT = {p: _cls_id[_rotclass[p]] for p in _rotclass}


def P(z):
    return (z[0], z[6], z[1], z[2], z[3], z[4], z[5])


# --------------------------------------------------- precomputed macro table
# for each break state z and gap g: (support tuple, successor list)
STATES = list(permutations(range(N)))
SID = {z: i for i, z in enumerate(STATES)}

SUPPORT = [[None] * 6 for _ in range(len(STATES))]
SUCC = [[None] * 6 for _ in range(len(STATES))]

for z in STATES:
    zi = SID[z]
    orbit = [z]
    for _ in range(5):
        orbit.append(P(orbit[-1]))
    cls = [ROT[w] for w in orbit]
    assert len(set(cls)) == 6, "loop should meet 6 distinct classes"
    for g in range(6):
        SUPPORT[zi][g] = tuple(cls[g:])
        y = orbit[g]
        pref = (y[3], y[4], y[5], y[6])          # O(P^g z)
        rest = [s for s in range(N) if s not in pref]
        succ = []
        for a, b, c in permutations(rest):
            # z' = (z'_0, z'_1, pref...) with I(z')=(z'_2..z'_5)=pref
            zp = (a, b) + pref[:4]
            zp = (a, b, pref[0], pref[1], pref[2], pref[3])
            zp = zp + (c,)
            assert (zp[2], zp[3], zp[4], zp[5]) == pref
            succ.append(SID[zp])
        assert len(succ) == 6
        SUCC[zi][g] = tuple(succ)


# ------------------------------------------------------------------- search
def M7(G, verbose=False):
    """Exact max chain length with total gap <= G. Returns (best, nodes)."""
    root = SID[tuple(range(N))]
    best = 0
    nodes = 0
    used = bytearray(720)
    stack = [(root, G, 0, 0)]  # (state, gap left, depth, next gap to try)

    # explicit DFS with undo
    def rec(z, budget, depth):
        nonlocal best, nodes
        nodes += 1
        if depth > best:
            best = depth
        for g in range(min(5, budget) + 1):
            sup = SUPPORT[z][g]
            if any(used[c] for c in sup):
                continue
            for c in sup:
                used[c] = 1
            for zp in SUCC[z][g]:
                rec(zp, budget - g, depth + 1)
            for c in sup:
                used[c] = 0

    sys.setrecursionlimit(100000)
    rec(root, G, 0)
    return best, nodes


if __name__ == "__main__":
    ref_M = [5, 5, 9, 9, 13, 13, 16, 16, 20, 20, 24]
    ref_nodes = [31, 85, 349, 1231, 4573, 17143, 62875, 227113,
                 827785, 2945461, 10465987]
    hi = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    print(f"{'G':>3} {'M_7(G)':>7} {'ref':>4} {'nodes':>12} {'ref nodes':>12}  ok")
    for G in range(hi + 1):
        m, nd = M7(G)
        rm = ref_M[G] if G < len(ref_M) else None
        rn = ref_nodes[G] if G < len(ref_nodes) else None
        ok = "?" if rm is None else ("OK" if (m == rm and nd == rn) else "MISMATCH")
        print(f"{G:3} {m:7} {str(rm):>4} {nd:12} {str(rn):>12}  {ok}")
