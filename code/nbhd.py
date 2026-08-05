"""The complete single-cut neighbourhood of a champion, priced exactly.

`CH3 = S + comps + p - 1` is now unconditional (`A2` is a theorem), it equals
`T` at the n = 7 champion, and 5905 needs its minimum over arc sets to be 142.
The earlier n = 7 attempt was simulated annealing in cut space: it sampled a few
thousand neighbours of a wandering point and reported "0 improvements", which is
a statement about the sampler, not about the champion.

At `comps = 18` the exact bound costs 6 ms, and the champion has 720 classes of
<= n cuts each.  So the whole radius-1 neighbourhood -- every add or remove of a
single cut, ~5,000 arc sets -- can be priced EXACTLY in about half a minute.
That turns "the search found nothing" into a complete statement:

    the champion is / is not a strict local minimum of CH3 under single-cut
    moves, and here is the full histogram of what the neighbourhood contains.

`--descend` then iterates it: take the best strict improvement, repeat.  Since
each sweep is exhaustive this is steepest descent, not annealing -- it cannot
miss an improving neighbour, and it terminates at a certified local minimum.

Every value reported is the exact bound with `p` verified by
`chainer.min_chains`; unverified rows are counted and excluded, because an
unverified `p` understates the bound and is exactly what manufactured the
spurious "140" in notes/pbound.md 3.

Usage:
  python3 code/nbhd.py                      # n = 7 champion, radius 1
  python3 code/nbhd.py --n 6                # n = 6 control (houston 872)
  python3 code/nbhd.py --descend 8          # steepest descent, <= 8 sweeps
"""

import argparse
import collections
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pbound                                                     # noqa: E402
from gen2 import Gen, chi_from_string                             # noqa: E402
from permgraph import string_to_path                              # noqa: E402

SEEDS = {6: "data/houston_872.txt",
         7: "data/n7/7_5906_derived_025c4805fc39.txt"}


def price(g, chi):
    """(bound, S, comps, p, v, verified) for one cut system."""
    arcs = g.arcs_of(chi)
    b, S, C, p = pbound.value(g, arcs)
    v = len({g.st.loop_of[a[0]] for a in arcs})
    return b, S, C, p, v, pbound.value.exact


def sweep(g, chi, n, quiet=False):
    """Price every single-cut toggle.  Returns (histogram, best move, vp)."""
    hist = collections.Counter()
    vp = collections.defaultdict(list)
    unver = 0
    best = None
    for c in range(len(chi)):
        old = set(chi[c])
        for r in range(n):
            if r in old and len(old) == 1:
                continue
            chi[c] = (old - {r}) if r in old else (old | {r})
            b, S, C, p, v, ex = price(g, chi)
            if not ex:
                unver += 1
            else:
                hist[b] += 1
                vp[v].append(p)
                if best is None or b < best[0]:
                    best = (b, c, r, S, C, p, v)
            chi[c] = set(old)
        chi[c] = old
    if not quiet:
        print(f"    {sum(hist.values())} neighbours priced exactly, "
              f"{unver} unverified (excluded)")
    return hist, best, vp


def plateau(g, chi, n, b0):
    """Radius 2 along the best plateau: sweep every neighbour attaining `lo`.

    Radius 2 in full is 4442^2 ~ 2e7 prices, days of work.  But a descent to
    `b0 - 1` two moves out has to pass through SOME first move, and the first
    move's value is what the sweep already measured -- so the cheap and honest
    version is to re-sweep only the first moves that stayed lowest.  It is a
    beam, not an exhaustion, and is reported as one.
    """
    front = []
    for c in range(len(chi)):
        old = set(chi[c])
        for r in range(n):
            if r in old and len(old) == 1:
                continue
            chi[c] = (old - {r}) if r in old else (old | {r})
            b, S, C, p, v, ex = price(g, chi)
            if ex and b == b0 + 1:
                front.append((c, r))
            chi[c] = set(old)
        chi[c] = old
    print(f"    plateau at {b0 + 1}: {len(front)} first moves to re-sweep")
    lo, lov, seen = b0 + 1, collections.Counter(), 0
    for k, (c, r) in enumerate(front):
        old = set(chi[c])
        chi[c] = (old - {r}) if r in old else (old | {r})
        h, best, vp = sweep(g, chi, n, quiet=True)
        chi[c] = old
        seen += sum(h.values())
        lov.update({v: min(ps) for v, ps in vp.items()})
        if min(h) < lo:
            lo = min(h)
            print(f"      *** move {k} ({c},{r}) reaches {lo}", flush=True)
        if k % 20 == 0:
            print(f"      {k}/{len(front)}  best so far {lo}", flush=True)
    print(f"    {seen} radius-2 arc sets priced; minimum {lo} "
          f"(need < {b0} to threaten 5905)")
    print(f"    v values seen at radius 2: "
          f"{sorted(lov)[:4]} ... {sorted(lov)[-4:]}")
    return lo


def main(n, descend):
    src = SEEDS[n]
    digits = [int(ch) for ch in open(src).read() if ch.isdigit()]
    g = Gen(n)
    chi = chi_from_string(g, string_to_path(digits, n))
    b0, S0, C0, p0, v0, ex0 = price(g, chi)
    print(f"\n  seed {os.path.basename(src)} (n = {n})")
    print(f"    CH3 = {b0}   S={S0} comps={C0} p={p0} v={v0} "
          f"verified={ex0}")

    cur = b0
    for step in range(max(1, descend)):
        print(f"\n  --- sweep {step}: every single-cut toggle ---")
        hist, best, vp = sweep(g, chi, n)
        lo = min(hist)
        print(f"    CH3 over the neighbourhood: "
              f"{dict(sorted(hist.items())[:10])}"
              f"{' ...' if len(hist) > 10 else ''}")
        print(f"    minimum in the neighbourhood: {lo}   "
              f"(current {cur}, {hist[lo]} attaining it)")
        print("    v -> min p  (the trade-off, off the census):")
        cells = [f"{v}:{min(ps)}" for v, ps in sorted(vp.items())]
        for i in range(0, len(cells), 8):
            print("      " + "  ".join(cells[i:i + 8]))
        viol = [(v, min(ps)) for v, ps in sorted(vp.items())
                if v + min(ps) - 1 < b0]
        print(f"    neighbours with v + p - 1 < {b0}: "
              f"{viol if viol else 'none'}")
        if best is None or best[0] >= cur:
            print(f"    NO strict improvement -> {cur} is a certified local "
                  f"minimum under single-cut moves")
            break
        b, c, r, S, C, p, v = best
        print(f"    step: class {c} toggle {r}  ->  CH3 = {b}  "
              f"S={S} comps={C} p={p} v={v}")
        if r in chi[c]:
            chi[c] = chi[c] - {r}
        else:
            chi[c] = chi[c] | {r}
        cur = b
        if not descend:
            break
    print(f"\n  final CH3 = {cur}   (5905 needs the global minimum to be 142)")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=7)
    ap.add_argument("--descend", type=int, default=0)
    ap.add_argument("--plateau", action="store_true")
    args = ap.parse_args()
    print(__doc__.split("Usage:")[0].strip())
    if args.plateau:
        src = SEEDS[args.n]
        digits = [int(ch) for ch in open(src).read() if ch.isdigit()]
        g = Gen(args.n)
        chi = chi_from_string(g, string_to_path(digits, args.n))
        b0 = price(g, chi)[0]
        print(f"\n  radius-2 plateau beam from {os.path.basename(src)}, "
              f"CH3 = {b0}")
        sys.exit(0 if plateau(g, chi, args.n, b0) >= b0 else 1)
    sys.exit(main(args.n, args.descend))
