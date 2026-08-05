"""Off-distribution walk pool: constructed walks, as a counterexample corpus.

The census is provenance-biased -- 163 of its 169 n=7 strings are
`5906_derived`, so a relation can hold on all 182 records and still be false.
That is not hypothetical: `comps = v - S` held on every one of the 179 measured
strings and was refuted in seconds by three walks out of `mcolour`
(97 vs 71, 97 vs 79, 620 vs 525).

So every candidate lemma gets tested against TWO corpora:

    data/census.json    real records, near-optimal, narrow
    data/walkpool.json  constructed walks, mediocre, wide

This file builds the second.  Walks are produced by `mcolour.search` from three
seed types (random colouring / monochromatic family / perturbed record) at a
range of iteration budgets, so the pool spans T from near-optimal to badly
suboptimal.  Every entry is a genuine superpermutation -- validity is asserted,
not assumed.

Usage:
  python3 code/walkpool.py                 # default spread over n = 5, 6, 7
  python3 code/walkpool.py --n 6 --count 60
"""

import argparse
import json
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from build import canonical, coords, design_of, to_string        # noqa: E402
from mcolour import Problem, search                              # noqa: E402
from permgraph import is_superpermutation, string_to_path        # noqa: E402

OUT = "data/walkpool.json"


def one(p, rng, kind, iters, record=None):
    n = p.n
    if kind == "random":
        arcs = p.arcs_of([{rng.randrange(n)} for _ in p.cls])
    elif kind == "family":
        arcs = p.arcs_of(p.family_chi(rng.randrange(n)))
    else:                                    # perturbed record
        arcs = list(record)
        for _ in range(rng.randint(1, 12)):  # knock it off the optimum
            i = rng.randrange(len(arcs))
            g, ln = arcs[i]
            if ln < 2:
                continue
            k = rng.randrange(1, ln)
            x = g
            for _ in range(k):
                x = p.st.sig(x)
            arcs[i] = (g, k)
            arcs.append((x, ln - k))
    _T, design = search(p, arcs, iters, rng=rng)
    design = canonical(design, n)     # merge accidental sigma-successions
    c = coords(design, n)
    return c, design


def build(ns, count, seed, verbose=True):
    rows = []
    rng = random.Random(seed)
    for n in ns:
        p = Problem(n)
        record = None
        path = f"data/n7/7_5906_nsk666466646646664666_2SYMM_FS.txt" if n == 7 \
            else "data/houston_872.txt" if n == 6 else None
        if path and os.path.exists(path):
            digits = [int(ch) for ch in open(path).read() if ch.isdigit()]
            record = design_of(string_to_path(digits, n))
        kinds = ["random", "family"] + (["perturb"] if record else [])
        per = max(1, count // len(kinds))
        for kind in kinds:
            for j in range(per):
                iters = rng.choice([0, 200, 2000, 20000])
                c, design = one(p, rng, kind, iters, record)
                # validity is asserted, never assumed
                s = to_string(design, n)
                assert is_superpermutation(s, n), (n, kind, j)
                assert len(s) == (n + math.factorial(n)
                                  + math.factorial(n - 1) - 3 + c["T"])
                c["kind"], c["iters"] = kind, iters
                c["label"] = f"pool/n{n}-{kind}-{j}"
                rows.append(c)
                if verbose and j == 0:
                    print(f"  n={n} {kind:<8} iters={iters:<6} T={c['T']:<7} "
                          f"S={c['S']:<6} B={c['B']:<6} Y={c['Y']:<6} "
                          f"comps={c['comps']}", flush=True)
    return rows


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, action="append", default=None)
    ap.add_argument("--count", type=int, default=30)
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()
    ns = args.n or [5, 6, 7]
    print(__doc__.split("Usage:")[0].strip())
    print(f"\n--- building pool over n = {ns}, ~{args.count} per n ---")
    rows = build(ns, args.count, args.seed)
    os.makedirs("data", exist_ok=True)
    json.dump(rows, open(OUT, "w"), indent=1)
    Ts = {}
    for r in rows:
        Ts.setdefault(r["n"], []).append(r["T"])
    print(f"\n  {len(rows)} constructed walks, all verified superpermutations")
    for n in sorted(Ts):
        print(f"    n={n}: {len(Ts[n]):>4} walks, T from {min(Ts[n])} "
              f"to {max(Ts[n])}")
    print(f"  wrote {OUT}")
