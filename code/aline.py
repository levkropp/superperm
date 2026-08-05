"""Walking the A-line: champion -> champion by the stitch/split exchange.

THE LINE.  The 237 known n = 7 optima are not scattered.  They lie on a single
one-parameter family with `d = 22` and `Y = 0` fixed and

    B = 10 + A,      S = 132 - A,      A in {8,9,10, 12,13,14, 16,17,18}

so `T = S + B + Y = 142` throughout.  One unit of A trades one split for one
block.

THE MOVE, read off the corpus.  Comparing an A = 12 champion with an A = 13
champion, their arc sets differ in exactly **three** arcs -- remove two, add one:

    removed   ((1,2,4,3,6,7,5), 6)    a generator of loop 27
    removed   ((5,1,2,4,3,6,7), 1)    a generator of loop 26
    added     ((5,1,2,4,3,6,7), 7)    the same class, now one FULL arc

That is precisely `notes/a_cost_law.md`'s stitch: a class covered by two arcs is
merged into one full arc, and the generator that started the second arc is no
longer an arc start -- it becomes an ACCIDENT, covered mid-arc.  Hence

    S -> S-1,   A -> A+1,   B -> B+1,   T unchanged.

THE RESULT, once `chainer.py` made the inner problem exact and fast enough to
run this at n = 7: the first three hold exactly, and **T does NOT**.

    step   A    S    B    Y    T
     -     8  124   18    0  142     the 5906 champion
     1     9  123   19    1  143
     2    10  122   20    2  144
     3    11  121   21    4  146
     4    12  120   22    6  148
     5    13  119   23    7  149

Every step lands on the predicted `(A, S, B)` -- `B = 10 + A` and `S = 132 - A`,
exactly the champion line -- and then pays for it in `Y`.  The chosen first
merge prices at `Y = 1`, and that is **exact and proven optimal** (`chainer`
finishes the search in milliseconds at two node budgets), so it is not a
chaining failure: the arc set this move produces genuinely cannot be chained
free.  An `A = 9` champion with `Y = 0, T = 142` does exist in the corpus, so it
uses a DIFFERENT arc set.

**So the stitch is not T-neutral at n = 7, and the A-line is not traversed by
this local move.**  The line of 237 champions is real; walking it needs a move
that also repairs the chaining, not just the arc set.

Usage:
  python3 code/aline.py --from data/n7/7_5906_derived_025c4805fc39.txt --n 7
"""

import argparse
import collections
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from build import canonical, coords, design_of, to_string        # noqa: E402
from gen2 import Gen                                             # noqa: E402
from permgraph import is_superpermutation, string_to_path        # noqa: E402


def merges(design, n, st):
    """Every class covered by 2 arcs whose union is the whole class.

    Returns (class id, kept_arc, dropped_arc, merged_arc).  `kept` is the arc
    whose start survives; `dropped` is the one whose start becomes an accident.
    """
    byc = collections.defaultdict(list)
    for a in design:
        byc[st.cls_id[a[0]]].append(a)
    out = []
    for cid, arcs in byc.items():
        if len(arcs) != 2:
            continue
        for keep, drop in ((arcs[0], arcs[1]), (arcs[1], arcs[0])):
            x = keep[0]
            for _ in range(keep[1]):
                x = st.sig(x)
            if x == drop[0] and keep[1] + drop[1] == n:
                out.append((cid, keep, drop, (keep[0], n)))
    return out


def apply_merge(design, keep, drop, merged):
    out = [a for a in design if a != keep and a != drop]
    return out + [merged]


SCAN_CAP = 4000        # node budget while ranking candidates
PICK_CAP = 300000      # node budget for the one we keep


def rechain(g, arcs, n, node_cap=SCAN_CAP):
    """Order an arc set into a walk using the two-level chainer.

    A step ranks ~240 merge candidates, so the chainer runs on a SMALL node
    budget here and the winner is re-priced exactly.  Without that the
    exact search spends seconds on the hard candidates -- 500 s per step.
    """
    comps, ends = g.components(arcs)
    Y, order, rots = g.chain(arcs, comps, ends, node_cap=node_cap)
    return canonical(g.design(arcs, comps, order, rots), n)


def walk(path_file, n, steps=8):
    g = Gen(n)
    st = g.st
    digits = [int(c) for c in open(path_file).read() if c.isdigit()]
    design = design_of(string_to_path(digits, n))
    c = coords(design, n)
    print(f"  start: {os.path.basename(path_file)}  len={c['length']} "
          f"T={c['T']} A={c['A']} S={c['S']} B={c['B']} Y={c['Y']}")

    seen_A = {c["A"]}
    for step in range(steps):
        cands = merges(design, n, st)
        if not cands:
            print("    no merge available -- line ends here")
            break
        best = None
        for cid, keep, drop, merged in cands:
            arcs = apply_merge(design, keep, drop, merged)
            des2 = rechain(g, arcs, n)
            c2 = coords(des2, n)
            if best is None or c2["T"] < best[0]["T"]:
                best = (c2, des2, cid, (keep, drop, merged))
        c2, des2, cid, mv = best
        des2 = rechain(g, apply_merge(design, *mv), n, node_cap=PICK_CAP)
        c2 = coords(des2, n)
        s = to_string(des2, n)
        ok = is_superpermutation(s, n)
        flag = "" if c2["T"] == c["T"] else f"   T moved {c['T']} -> {c2['T']}"
        print(f"    step {step+1}: merged class {cid:<4} -> "
              f"len={len(s)} T={c2['T']} A={c2['A']} S={c2['S']} "
              f"B={c2['B']} Y={c2['Y']} comps={c2['comps']} "
              f"valid={ok}{flag}", flush=True)
        design, c = des2, c2
        seen_A.add(c2["A"])
        if not ok:
            print("    !! not a superpermutation -- stopping")
            break
    print(f"  A values visited: {sorted(seen_A)}")
    return design


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="src",
                    default="data/n7/7_5906_derived_025c4805fc39.txt")
    ap.add_argument("--n", type=int, default=7)
    ap.add_argument("--steps", type=int, default=8)
    args = ap.parse_args()
    print(__doc__.split("Usage:")[0].strip())
    print(f"\n--- walking the A-line from {args.src} ---")
    walk(args.src, args.n, args.steps)
