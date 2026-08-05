"""Independent validator for a macro-chain witness produced by macro7.c.

Recomputes the class map, the P-orbit, the supports and the port equations
straight from the spec -- shares no code with the C prover or macro7.py.

Checks, for a witness (z_i, g_i) i = 0..L-1:
  1. z_0 is the normalised root 0123456
  2. every gap g_i lies in 0..5
  3. total gap <= G
  4. the port equation I(z_{i+1}) = O(P^{g_i} z_i) holds at every boundary
  5. all supports A_{g_i}(z_i) are pairwise disjoint
  6. |A_g(z)| = 6 - g throughout
"""

import sys
from itertools import permutations

N = 7


def rotclass(p):
    return min(tuple(p[i:] + p[:i]) for i in range(N))


def P(z):
    return (z[0], z[6], z[1], z[2], z[3], z[4], z[5])


def orbit(z):
    out = [z]
    for _ in range(5):
        out.append(P(out[-1]))
    return out


def support(z, g):
    return [rotclass(w) for w in orbit(z)[g:]]


def I(z):
    return (z[2], z[3], z[4], z[5])


def O(z):
    return (z[3], z[4], z[5], z[6])


def main(path):
    lines = open(path).read().split()
    G = int(lines[0])
    L = int(lines[1])
    toks = lines[2:]
    macros = []
    for i in range(L):
        z = tuple(int(c) for c in toks[2 * i])
        g = int(toks[2 * i + 1])
        macros.append((z, g))

    print(f"witness: budget G = {G}, length L = {L}")
    fails = []

    if macros[0][0] != tuple(range(N)):
        fails.append(f"root is {macros[0][0]}, expected {tuple(range(N))}")

    for i, (z, g) in enumerate(macros):
        if sorted(z) != list(range(N)):
            fails.append(f"macro {i}: {z} is not a permutation of 0..6")
        if not 0 <= g <= 5:
            fails.append(f"macro {i}: gap {g} out of range")

    total = sum(g for _, g in macros)
    if total > G:
        fails.append(f"total gap {total} exceeds budget {G}")

    for i in range(L - 1):
        z, g = macros[i]
        want = O(orbit(z)[g])
        got = I(macros[i + 1][0])
        if want != got:
            fails.append(f"port equation fails at boundary {i}: "
                         f"I(z_{i+1})={got} vs O(P^{g} z_{i})={want}")

    seen = {}
    for i, (z, g) in enumerate(macros):
        sup = support(z, g)
        if len(sup) != 6 - g:
            fails.append(f"macro {i}: support size {len(sup)} != {6-g}")
        if len(set(sup)) != len(sup):
            fails.append(f"macro {i}: support has repeats")
        for c in sup:
            if c in seen:
                fails.append(f"macro {i}: class {c} already used by macro {seen[c]}")
            seen[c] = i

    print(f"  total gap        : {total}  (budget {G})")
    print(f"  macros           : {L}")
    print(f"  classes consumed : {len(seen)} of 720")
    print(f"  port equations   : {L-1} boundaries")
    if fails:
        print("\nFAILED:")
        for f in fails[:20]:
            print("  -", f)
        return 1
    print(f"\nVALID: a {L}-macro chain of total gap {total} exists "
          f"=> M_7({G}) >= {L}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "witness.txt"))
