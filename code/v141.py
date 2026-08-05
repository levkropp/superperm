"""Attack the target region directly: minimise CH3 subject to `v <= 141`.

Every previous n = 7 search started somewhere and hoped to arrive.  `VLOCK`
(notes/pbound.md 9c) now says that cannot work from a champion: no thin loop is
fully movable in ANY of the 237 known optima, so `v` cannot fall below 142 by
re-cutting, at any move width.  And `CH3LOC` says the champion is a certified
strict local minimum, so there is nothing to descend to either.

So stop starting from the answer.  5905 needs an arc set with

    v <= 141   AND   v + p <= 142,

so go and live in `v <= 141` and minimise the bound *there*.  A penalty term
drags the walk into the region and the objective inside it is `CH3` itself.

WHAT EACH OUTCOME MEANS.

  a verified `CH3 <= 141` at `v <= 141`   the arc-set minimum is below 142, so
                                          CH3 can never exclude 5905 -- the
                                          whole reduction is dead, and this is
                                          the cheapest way to find that out
  the walk lives at `v <= 141` and the
  best VERIFIED bound stays >= 143        agrees with 5a's generated sets
                                          (`v = 141` gave `p = 23`) and says the
                                          region is far from the boundary

Only VERIFIED values count.  `chainer.min_chains` returns the sound packing
floor when its node budget runs out, which UNDERSTATES `p` and so understates
the bound -- exactly the direction that manufactures a false refutation, and
exactly how the spurious "140" of notes/pbound.md 3 happened.  The fast bound
is used to steer and never to conclude.

Usage:
  python3 code/v141.py                    # 4000 iterations, target v <= 141
  python3 code/v141.py --target 130       # a different rung
"""

import argparse
import collections
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pbound                                                     # noqa: E402
from gen2 import Gen, chi_from_string                             # noqa: E402
from permgraph import string_to_path                              # noqa: E402

SEED7 = "data/n7/7_5906_derived_025c4805fc39.txt"


def vee(g, chi):
    return len({g.st.loop_of[a[0]] for a in g.arcs_of(chi)})


def run(n, target, iters, lam, seed):
    g = Gen(n)
    digits = [int(c) for c in open(SEED7).read() if c.isdigit()]
    chi = chi_from_string(g, string_to_path(digits, n))
    rng = random.Random(seed)

    def score(ch):
        arcs = g.arcs_of(ch)
        b, S, C, p = pbound.value(g, arcs, bound_only=True)
        v = len({g.st.loop_of[a[0]] for a in arcs})
        return b + lam * max(0, v - target), b, v, S, C, p

    cur = score(chi)
    print(f"  seed: CH3={cur[1]} v={cur[2]}  target v <= {target}, "
          f"penalty {lam}/loop")
    best_in = None                    # best VERIFIED bound with v <= target
    minp = {}                         # v -> min p seen (fast; steering only)
    reached = 0
    t0, t1 = 3.0, 0.05
    for it in range(iters):
        temp = t0 * (t1 / t0) ** (it / max(1, iters - 1))
        cid = rng.randrange(len(chi))
        old = set(chi[cid])
        r = rng.random()
        if r < 0.45 and len(old) < n:
            chi[cid] = old | {rng.randrange(n)}
        elif r < 0.75 and len(old) > 1:
            chi[cid] = old - {rng.choice(sorted(old))}
        else:
            chi[cid] = (old - {rng.choice(sorted(old))}) | {rng.randrange(n)}
        if not chi[cid] or chi[cid] == old:
            chi[cid] = old
            continue
        s = score(chi)
        if s[0] <= cur[0] or rng.random() < math.exp((cur[0] - s[0]) / temp):
            cur = s
            _, b, v, S, C, p = s
            minp[v] = min(minp.get(v, 10**9), p)
            if v <= target:
                reached += 1
                eb, eS, eC, ep = pbound.value(g, g.arcs_of(chi))
                if pbound.value.exact and (best_in is None or eb < best_in[0]):
                    best_in = (eb, v, eS, eC, ep)
                    print(f"    it {it:>6}  v={v}  CH3={eb} VERIFIED  "
                          f"S={eS} comps={eC} p={ep}", flush=True)
                    if eb <= target:
                        print("    *** CH3 <= target at v <= target: the "
                              "reduction cannot exclude 5905 ***")
                        return best_in, minp, reached
        else:
            chi[cid] = old
        if it % 500 == 0:
            print(f"    it {it:>6}  cur CH3={cur[1]} v={cur[2]}  "
                  f"(in-region hits {reached})", flush=True)
    return best_in, minp, reached


def main(n, target, iters, lam, seed):
    best, minp, reached = run(n, target, iters, lam, seed)
    print(f"\n  states accepted with v <= {target}: {reached}")
    if best is None:
        print("  no VERIFIED bound inside the region -- the walk either never "
              "got there or p never verified there")
    else:
        print(f"  best VERIFIED bound at v <= {target}: CH3 = {best[0]}   "
              f"v={best[1]} S={best[2]} comps={best[3]} p={best[4]}")
    lo = min((v for v in minp), default=None)
    if lo is not None:
        cells = [f"{v}:{p}" for v, p in sorted(minp.items())]
        print("  v -> min p seen (FAST bound, steering only, not a verdict):")
        for i in range(0, len(cells), 8):
            print("    " + "  ".join(cells[i:i + 8]))
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=7)
    ap.add_argument("--target", type=int, default=141)
    ap.add_argument("--iters", type=int, default=4000)
    ap.add_argument("--lam", type=int, default=8)
    ap.add_argument("--seed", type=int, default=1)
    args = ap.parse_args()
    print(__doc__.split("Usage:")[0].strip())
    sys.exit(main(args.n, args.target, args.iters, args.lam, args.seed))
