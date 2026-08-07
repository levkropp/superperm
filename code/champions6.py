"""All 43,096 known n = 6 optima, measured in ledger coordinates.

Robin Houston's `872-treelike.txt.gz` holds **42,288** superpermutations of
length 872, plus 772 in `-slack1` and 36 in `-slack2`.  `census.py` reads one
string per file, so it silently measured only the first line of each -- this
file does the rest.

Why it matters: every conjecture in `docs/notes/second_order.md` was resting on
**seven** n = 6 strings.  Here the same claims meet 43,096, which is
(as far as anyone knows) essentially the complete set of standard-kernel
optima at n = 6.  A relation that survives this is no longer a champion
artefact in the way `lemma_arsenal.md` 6 warns about.

Usage:
  python3 code/champions6.py              # all of them, ~3 min
  python3 code/champions6.py --limit 2000
"""

import argparse
import collections
import gzip
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from build import coords, design_of                              # noqa: E402
from permgraph import string_to_path                             # noqa: E402

UP = "/home/lk/superperm-upstream/superpermutations/6"
FILES = ["872-treelike.txt.gz", "872-treelike-slack1.txt.gz",
         "872-treelike-slack2.txt"]
OUT = "data/champions6.json"


def strings(limit=None):
    for name in FILES:
        p = os.path.join(UP, name)
        if not os.path.exists(p):
            continue
        opener = gzip.open if p.endswith(".gz") else open
        with opener(p, "rt") as fh:
            for i, line in enumerate(fh):
                line = line.strip()
                if len(line) != 872 or not line.isdigit():
                    continue
                if limit and i >= limit:
                    break
                yield name, [int(c) for c in line]


def run(limit=None):
    rows, hist = [], collections.Counter()
    per_file = collections.Counter()
    for name, digits in strings(limit):
        c = coords(design_of(string_to_path(digits, 6)), 6)
        assert c["length"] == 872, c["length"]
        # the master identity, on every single one
        assert c["T"] == 5 * c["d"] + (c["B"] + c["Y"]) - c["A"]
        rows.append(c)
        per_file[name] += 1
        hist[(c["d"], c["A"], c["S"], c["B"], c["Y"])] += 1
    return rows, hist, per_file


def report(rows, hist, per_file):
    N = len(rows)
    print(f"\n--- {N} n = 6 optima, all of length 872 ---")
    for k, v in per_file.items():
        print(f"    {k:<32} {v}")

    print(f"\n  master identity T = 5d + (B+Y) - A:  {N}/{N}")

    def frac(name, pred):
        k = sum(1 for r in rows if pred(r))
        flag = "ALL" if k == N else f"{k}/{N}"
        print(f"    {name:<52} {flag}")
        return k

    print("\n  claims from docs/notes/second_order.md, now against 43k champions:")
    frac("S > 0  (every champion has splits)", lambda r: r["S"] > 0)
    frac("Y = 0", lambda r: r["Y"] == 0)
    frac("HPV-tight (T = v)", lambda r: r["hpv_tight"])
    frac("B + Y - A = 4  (the n=6 saving invariant)",
         lambda r: r["B"] + r["Y"] - r["A"] == 4)
    frac("A2:  comps >= v - S", lambda r: r["comps"] >= r["v"] - r["S"])
    frac("A2b: T >= v + Y", lambda r: r["T"] >= r["v"] + r["Y"])
    frac("A2c: dirty <= S + N - v",
         lambda r: r["dirty"] <= r["S"] + r["N"] - r["v"])
    frac("A3:  S + comps = v", lambda r: r["S"] + r["comps"] == r["v"])
    frac("B2:  mu_max <= 3", lambda r: r["mu_max"] <= 3)
    frac("dirty = 2S exactly", lambda r: r["dirty"] == 2 * r["S"])
    frac("n_partial = 2S  (m = S, all multiplicities exactly 2)",
         lambda r: r["n_partial"] == 2 * r["S"])

    print(f"\n  distinct coordinate vectors (d, A, S, B, Y): {len(hist)}")
    print(f"  {'d':>4} {'A':>4} {'S':>5} {'B':>5} {'Y':>4}   count")
    for key, cnt in sorted(hist.items(), key=lambda kv: -kv[1])[:14]:
        d, A, S, B, Y = key
        print(f"  {d:>4} {A:>4} {S:>5} {B:>5} {Y:>4}   {cnt}")

    for field in ("d", "S", "B", "A", "Y", "comps", "mu_max"):
        vals = collections.Counter(r[field] for r in rows)
        print(f"  {field:<7} range {min(vals)}..{max(vals)}   "
              f"{dict(sorted(vals.items())) if len(vals) <= 10 else '...'}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()
    print(__doc__.split("Usage:")[0].strip())
    rows, hist, per_file = run(args.limit)
    report(rows, hist, per_file)
    os.makedirs("data", exist_ok=True)
    keep = ["length", "T", "v", "d", "A", "S", "B", "Y", "N", "dirty",
            "n_partial", "comps", "mu_max", "m", "hpv_tight", "R", "n"]
    json.dump([{k: r[k] for k in keep} for r in rows], open(OUT, "w"))
    print(f"\n  wrote {OUT}")
