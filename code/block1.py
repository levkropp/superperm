"""Single-block walks: enumerate them as words in {sigma, delta}.

`B = 1` means every jump has weight <= 2.  A weight-1 jump appends one character
and lands on `sigma(u)`; a weight-2 jump appends two and lands on `delta(u)` --
or on `sigma^2(u)`, but that is literally two sigma steps, since the
intermediate window `sigma(u)` is a permutation and is written to the string
either way.  So

    BLK1   B = 1  =>  the string is a WORD in {sigma, delta},
           length = n + #sigma + 2*#delta

**The converse is false**, and that is the point: a word whose sigma steps land
on three or more consecutive already-covered permutations produces a
weight->=3 jump in the path of first occurrences.  This search finds such a
word at n = 5.  So the word model is a SUPERSET of the single-block walks --
which is the direction a lower-bound search needs.

A `delta` step's intermediate window is NOT a permutation (reaching
`u[2:]+u[1]+u[0]` appends `u[1]` first, giving `u[1:]+u[1]`), so it covers one
new permutation for two characters and always wastes exactly one:

    length = n + (n! - 1) + W,      W = wasted characters,      R = W + 1

which makes W the right search parameter, and gives the free floor
`W = R - 1 >= (n-1)! - 1` before the search starts.

**The bound is already proved** (`BLK2` in `code/lemmas.py`): `B1` gives `Y = 0`
and `T = S+1`; feeding the Split Identity `S = (n-1)d - A` into HPV
`T >= v = (n-2)! + d` gives `(n-2)d >= (n-2)! + A - 1`, hence `d >= (n-3)!` and
`T >= (n-1)(n-3)!` -- Egan's T exactly.  So

    every superpermutation shorter than Egan(n) has B >= 2

and at equality (`BLK3`) the walk is forced to `A = 1, d = (n-3)!`.

**This file is the independent gate.**  At n = 5 it exhausts every
`{sigma,delta}` word by increasing waste and finds the first one at
`W = 30`, i.e. length 154 = Egan(5) -- so nothing shorter exists even in the
superset.

Usage:
  python3 code/block1.py --n 5
  python3 code/block1.py --n 6 --max-waste 40 --nodes 20000000
"""

import argparse
import itertools
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from build import coords, design_of                              # noqa: E402
from permgraph import is_superpermutation, string_to_path        # noqa: E402


def tables(n):
    """Index the permutations; precompute sigma, delta and the class of each.

    A sigma step appends one character and lands on a permutation.  A delta step
    appends two, and its INTERMEDIATE window is not a permutation: to reach
    `delta(u) = u[2:]+u[1]+u[0]` the first character appended is `u[1]`, giving
    the window `u[1:]+u[1]`, which repeats a symbol.  So a delta step covers one
    new permutation at a cost of two characters -- it always wastes exactly one.
    """
    perms = list(itertools.permutations(range(1, n + 1)))
    ix = {p: i for i, p in enumerate(perms)}
    sig = [ix[p[1:] + p[:1]] for p in perms]
    dlt = [ix[p[2:] + (p[1], p[0])] for p in perms]
    cls, seen = [0] * len(perms), {}
    for i, p in enumerate(perms):
        key = min(p[k:] + p[:k] for k in range(n))
        cls[i] = seen.setdefault(key, len(seen))
    return perms, sig, dlt, cls


def base(n):
    return n + math.factorial(n) + math.factorial(n - 1) - 3


def egan(n):
    return base(n) + (n - 1) * math.factorial(n - 3)


def search(n, waste_lo, waste_cap, node_cap, want=1):
    """Single-block walks by increasing waste; returns the first ones found.

    Returns (waste, words, nodes, exhausted).  Prunes on

        remaining waste >= #(classes still holding an uncovered permutation),
                           less one if the current class is among them

    -- sigma never leaves a rotation class, so every other class still needing
    a permutation costs at least one delta, and every delta wastes at least one
    character.
    """
    perms, sig, dlt, cls = tables(n)
    N, NC = len(perms), math.factorial(n - 1)
    covered = bytearray(N)
    uncov = [n] * NC                # uncovered permutations per rotation class
    found, nodes, limit = [], 0, waste_lo

    def dfs(u, ncov, w, run, word):
        nonlocal nodes
        nodes += 1
        if nodes > node_cap:
            raise TimeoutError
        if ncov == N:
            found.append("".join(word))
            return
        need = uncov.count(0)                       # classes fully covered
        need = (NC - need) - (1 if uncov[cls[u]] else 0)
        if w + need > limit:
            return
        for mv in ("s", "d"):
            if mv == "s":
                if run + 1 >= n:                    # sigma^n returns to u
                    continue
                land, cost, nrun = sig[u], 1, run + 1
            else:
                land, cost, nrun = dlt[u], 2, 0
            new = 0 if covered[land] else 1
            if w + cost - new > limit:
                continue
            covered[land] += 1
            uncov[cls[land]] -= new
            word.append(mv)
            dfs(land, ncov + new, w + cost - new, nrun, word)
            word.pop()
            uncov[cls[land]] += new
            covered[land] -= 1
            if len(found) >= want:
                return

    for limit in range(waste_lo, waste_cap + 1):
        covered[:] = bytearray(N)
        covered[0] = 1
        uncov[:] = [n] * NC
        uncov[cls[0]] -= 1
        try:
            dfs(0, 1, 0, 0, [])
        except TimeoutError:
            return limit, found, nodes, False
        if found:
            return limit, found, nodes, True
        print(f"    W = {limit}: none  ({nodes:,} nodes so far)", flush=True)
    return None, [], nodes, True


def word_to_string(n, word):
    perms, sig, dlt, _ = tables(n)
    s = list(perms[0])
    u = 0
    for mv in word:
        if mv == "s":
            u = sig[u]
            s.append(perms[u][-1])
        else:
            u = dlt[u]
            s.extend(perms[u][-2:])
    return s


def main(n, waste_cap, node_cap, want):
    target = egan(n) - n - math.factorial(n) + 1
    lo = math.factorial(n - 1) - 1
    print(f"\n--- n = {n}: single-block walks by increasing waste ---")
    print(f"  length = {n} + ({math.factorial(n)} - 1) + W;  BLK2 predicts the "
          f"first walk at W = {target} (length {egan(n)} = Egan)")
    if waste_cap is None:
        waste_cap = target
    print(f"  every delta wastes >= 1 and R = W + 1 >= (n-1)!, so W >= {lo}")
    print(f"  searching W = {lo} .. {waste_cap}, node cap {node_cap:,}")

    w, words, nodes, done = search(n, lo, waste_cap, node_cap, want=want)
    print(f"  {nodes:,} nodes")
    if not words:
        state = "exhausted" if done else "hit the node cap"
        print(f"  no single-block walk with W <= {waste_cap} ({state})")
        if done:
            print(f"  => confirms BLK2 down to length "
                  f"{n + math.factorial(n) - 1 + waste_cap}")
        return 0

    assert w == target, f"BLK2 predicted the first word at W = {target}, got {w}"
    print(f"  first words at W = {w} (length {n + math.factorial(n) - 1 + w} "
          f"= Egan): {len(words)} sampled")
    spectrum = {}
    for word in words:
        s = word_to_string(n, word)
        assert is_superpermutation(s, n), "the word did not produce a superperm"
        c = coords(design_of(string_to_path(s, n)), n)
        assert c["length"] == len(s)
        assert c["T"] >= (n - 1) * math.factorial(n - 3), "BLK2 violated"
        if c["B"] == 1:
            assert c["A"] == 1 and c["d"] == math.factorial(n - 3), "BLK3"
        spectrum[(c["B"], c["A"], c["d"])] = \
            spectrum.get((c["B"], c["A"], c["d"]), 0) + 1
    for (B, A, d), k in sorted(spectrum.items()):
        print(f"    B={B} A={A} d={d}   x{k}"
              + ("   <-- single block, Egan vertex" if B == 1 else ""))
    print(f"  => nothing below Egan length exists even in the SUPERSET of "
          f"{{sigma,delta}} words, which is BLK2 with room to spare")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=5)
    ap.add_argument("--max-waste", type=int, default=None)
    ap.add_argument("--nodes", type=int, default=20_000_000)
    ap.add_argument("--want", type=int, default=200)
    args = ap.parse_args()
    print(__doc__.split("Usage:")[0].strip())
    sys.exit(main(args.n, args.max_waste, args.nodes, args.want))
