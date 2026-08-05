"""Is `v + p` bounded below, and by what?

`A2` is now a theorem, so `CH3 = S + comps + p - 1 >= v + p - 1` holds with no
hypothesis, and on every real string `S + comps = v` exactly (`A3`).  So the
whole bound has collapsed to one quantity:

    5905 is excluded  <=>  v + p >= 143  over every n = 7 arc set.

Before searching for that, ask the question that can kill the programme in one
pass.  `CH3 <= T` bounds `v + p` from ABOVE, so a long, sloppy superpermutation
is free to have a small `v + p` -- nothing in the theory forbids it.  If one
does, then `min(v + p)` over arc sets is below 143 and `CH3` can never reach
142, no matter how the search is run.

So: measure `v + p` on EVERY string on disk, optimal or not, and look at the
minimum per `n`.  A real string with `v + p < 143` at n = 7 refutes the
programme outright; a floor that holds across 44,000 strings of wildly varying
quality is evidence the floor is structural.

`p` is reported only when `chainer.min_chains` VERIFIED it.  An unverified `p`
is a lower bound, so it can only understate `v + p` -- exactly the direction
that would manufacture a false refutation.  Those rows are counted separately.

Usage:
  python3 code/vplus.py               # n = 5, 6, 7
  python3 code/vplus.py --n 7         # one n
"""

import argparse
import collections
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pbound                                                     # noqa: E402
from build import design_of                                       # noqa: E402
from gen2 import Gen                                              # noqa: E402
from permgraph import string_to_path                              # noqa: E402


def row(g, digits, n):
    """(T, v, S, comps, p, verified) for one string, or None."""
    p_ = string_to_path(digits, n)
    if len(p_) != math.factorial(n):
        return None
    arcs = [tuple(a) for a in design_of(p_)]
    b, S, C, p = pbound.value(g, arcs)
    v = len({g.st.loop_of[a[0]] for a in arcs})
    T = len(digits) - (n + math.factorial(n) + math.factorial(n - 1) - 3)
    return T, v, S, C, p, pbound.value.exact


def scan(ns, limit=None):
    import census
    cache, out = {}, collections.defaultdict(list)
    for n, label, path in census.sources(9):
        if n not in ns:
            continue
        for digits in census.read_strings(path):
            if not digits or max(digits) != n or min(digits) != 1:
                continue
            g = cache.setdefault(n, Gen(n))
            r = row(g, digits, n)
            if r is not None:
                out[n].append((label,) + r)
                if limit and len(out[n]) >= limit:
                    break
    return out


def main(ns, limit):
    res = scan(ns, limit)
    for n in sorted(res):
        rows = res[n]
        ok = [r for r in rows if r[6]]
        un = len(rows) - len(ok)
        vp = [r[2] + r[5] for r in ok]
        print(f"\n  n = {n}: {len(rows)} strings, {un} with p unverified "
              f"(excluded)")
        if not vp:
            continue
        lo = min(vp)
        arg = [r for r in ok if r[2] + r[5] == lo][0]
        print(f"    min (v + p) = {lo}   at {arg[0]}  "
              f"T={arg[1]} v={arg[2]} S={arg[3]} comps={arg[4]} p={arg[5]}")
        hist = collections.Counter(vp)
        print(f"    v + p histogram: "
              f"{dict(sorted(hist.items())[:12])}"
              f"{' ...' if len(hist) > 12 else ''}")
        # the trade-off itself: p against v
        by_v = collections.defaultdict(list)
        for r in ok:
            by_v[r[2]].append(r[5])
        print("    v -> min p over strings at that v:")
        cells = [f"{v}:{min(ps)}" for v, ps in sorted(by_v.items())]
        for i in range(0, len(cells), 10):
            print("      " + "  ".join(cells[i:i + 10]))
        tight = sum(1 for r in ok if r[2] + r[5] - 1 == r[1])
        print(f"    CH3 exactly tight (v + p - 1 == T): {tight}/{len(ok)}")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, action="append")
    ap.add_argument("--limit", type=int)
    args = ap.parse_args()
    print(__doc__.split("Usage:")[0].strip())
    sys.exit(main(args.n or [5, 6, 7], args.limit))
