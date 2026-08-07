"""Split-free superpermutations from the standard recursion, and what they cost.

`WA1` guesses no champion is split-free for n > 5, and n = 6 proves it
(docs/notes/block_count_lemma.md 12g).  The natural follow-up is whether split-free
champions come BACK at some larger n.  The classical recursive superpermutation
has length `sum_{k<=n} k!` and is split-free, which would make the question a
race between `sum k!` and Egan's `n!+(n-1)!+(n-2)!+(n-3)!+n-3`.

That framing is wrong, because `sum k!` is NOT the shortest split-free string.
On disk at n = 7 there is a split-free superpermutation of length **5912**,
one shorter, and 5912 = 872 + 5040 -- the n = 6 CHAMPION plus 7!.  So the
recursion is not "classical -> classical"; it is

    ANY (n-1)-superpermutation  ->  a SPLIT-FREE n-superpermutation
    of length  L(n-1) + n!.

This file builds that map and checks both halves of the claim -- that the output
is a superpermutation, and that it is split-free -- from the real strings.

Consequences, if it holds:

    sigma(n) <= s(n-1) + n!          sigma = shortest split-free
    split-free champion at n   <=>   s(n) = s(n-1) + n!

and the gap `g(n) = s(n-1) + n! - s(n)` is exactly what must vanish.  Measured
`g = 0, 0, 1, 6` at n = 4, 5, 6, 7.

Usage:
  python3 code/sfrec.py
"""

import argparse
import math
import os
import sys
from itertools import permutations

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from build import design_of                                       # noqa: E402
from permgraph import is_superpermutation, string_to_path         # noqa: E402


def lift(word, m):
    """The standard recursion: an m-superpermutation from an (m-1) one.

    Walk `word` and read off its permutations of [m-1] in order of occurrence.
    Replace each `pi` by `pi . m . pi` and merge consecutive images with the
    overlap they already had, which is what keeps the total at L + m!.
    """
    seen, seq = set(), []
    for i in range(len(word) - (m - 2)):
        w = tuple(word[i:i + m - 1])
        if len(set(w)) == m - 1 and max(w) <= m - 1:
            if w not in seen:
                seen.add(w)
            seq.append(w)
    # de-duplicate consecutive repeats, keep first occurrences in order
    order, got = [], set()
    for w in seq:
        if w not in got:
            got.add(w)
            order.append(w)
    out = []
    for pi in order:
        block = list(pi) + [m] + list(pi)
        if not out:
            out = block
            continue
        k = min(len(out), len(block))
        while k > 0 and out[-k:] != block[:k]:
            k -= 1
        out += block[k:]
    return out


def report(n, word, label):
    m = n + 1
    got = lift(word, m)
    ok = is_superpermutation(got, m)
    exp = len(word) + math.factorial(m)
    S = None
    if ok and len(got) >= math.factorial(m):
        path = string_to_path(got, m)
        if len(path) == math.factorial(m):
            S = len(design_of(path)) - math.factorial(m - 1)
    print(f"  {label} (n={n}, len {len(word)})  ->  n={m}: len {len(got)}"
          f"   expected {exp} {'OK' if len(got) == exp else '<< MISMATCH'}")
    print(f"      valid superpermutation: {ok}     splits S = {S}"
          f"   {'SPLIT-FREE' if S == 0 else ''}")
    return ok and S == 0 and len(got) == exp


def main():
    import census
    best = {}
    for n, label, path in census.sources(9):
        if n > 6:
            continue
        for d in census.read_strings(path):
            if not d or max(d) != n or min(d) != 1:
                continue
            if len(string_to_path(d, n)) != math.factorial(n):
                continue
            if n not in best or len(d) < len(best[n][1]):
                best[n] = (label, d)
    print("\n  lifting the SHORTEST string on disk at each n:")
    allok = True
    for n in sorted(best):
        label, d = best[n]
        allok &= report(n, d, label)
    print("\n  sigma(n) <= s(n-1) + n!,  and the gap that must vanish for a")
    print("  split-free champion,  g(n) = s(n-1) + n! - s(n):")
    s = {1: 1, 2: 3, 3: 9, 4: 33, 5: 153, 6: 872}
    print("    n    s(n-1)+n!    s(n) known    g(n)")
    for n in range(4, 8):
        if n - 1 not in s:
            continue
        rec = s[n - 1] + math.factorial(n)
        sn = s.get(n)
        gn = (rec - sn) if sn else f">= {rec - 5906}"
        print(f"    {n}   {rec:9d}    {sn if sn else '<= 5906':>10}    {gn}")
    return 0 if allok else 1


if __name__ == "__main__":
    argparse.ArgumentParser().parse_args()
    print(__doc__.split("Usage:")[0].strip())
    sys.exit(main())
