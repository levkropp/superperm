"""Measure every known n = 7 superpermutation against every lemma here.

Until now the n = 7 work could only be gated on algebra and on n <= 6 walks:
the repo had no 7-symbol string.  github.com/superpermutators/superperm has
139 of them -- 135 at the record 5906, plus 5907, 5908, 5912 and 5913 -- and
this file runs the whole apparatus over all of them.

For each string it checks:

  * the three identities of blockcount.py (arc/jump, split, block) and the
    SBY identity  length = n + n! + (n-1)! - 3 + S + B + Y;
  * every per-loop claim of dirty.py -- a clean run lives inside one 2-loop at
    consecutive generators, interior arcs of a run are full, N = sum r_L,
    f = #{L : a_L = n-1 and r_L = 1}, A = (n-1)v - R;
  * HPV in the form T >= v;
  * the rung bound of loop_runs.py at that string's own v.

Any violation means a lemma is wrong, not that a string is interesting.

Usage:  python3 code/n7_champions.py [directory]
        (default: data/n7, then the upstream clone if present)
"""

import math
import os
import sys
from collections import Counter

sys.path.insert(0, "code")
from blockcount import Model                                   # noqa: E402
from dirty import dissect                                      # noqa: E402
from permgraph import string_to_path                           # noqa: E402

SEARCH = ["data/n7",
          "/home/lk/superperm-upstream/superpermutations/7",
          "/home/lk/superperm-upstream/superpermutations/7/7_5906"]


def sources(argv):
    if len(argv) > 1:
        return [argv[1]]
    return [d for d in SEARCH if os.path.isdir(d)]


def load(dirs):
    out, seen = [], set()
    for d in dirs:
        for fn in sorted(os.listdir(d)):
            if not fn.endswith(".txt"):
                continue
            raw = open(os.path.join(d, fn)).read().strip()
            if not raw or any(c not in "1234567" for c in raw):
                continue
            if raw in seen:
                continue
            seen.add(raw)
            out.append((fn, [int(c) for c in raw]))
    return out


if __name__ == "__main__":
    print(__doc__.split("Usage:")[0].strip())
    dirs = sources(sys.argv)
    print(f"\nreading from: {dirs}")
    strings = load(dirs)
    print(f"{len(strings)} distinct 7-symbol strings")
    if not strings:
        sys.exit("no strings found")

    m = Model(7)
    base = 7 + math.factorial(7) + math.factorial(6) - 3      # 5764
    rows = []
    for fn, digits in strings:
        path = string_to_path(digits, 7)
        assert len(set(path)) == 5040, f"{fn} is not a superpermutation"
        d = dissect(m, path)
        m.measure(path)                    # the three blockcount identities
        assert d["length"] == base + d["SBY"], f"{fn} SBY identity"
        assert d["SBY"] >= d["v"], f"{fn} violates HPV"
        rows.append((fn, d))

    lens = Counter(r[1]["length"] for r in rows)
    print(f"\nlengths: {dict(sorted(lens.items()))}")
    print("all identities hold, and HPV (T >= v) holds, on every string")

    print(f"\n{'quantity':<12}{'min':>8}{'max':>8}   distribution (value:count)")
    for k in ("length", "R", "S", "v", "A", "B", "Y", "SBY", "N", "f",
              "dirty", "n_partial", "hpv_slack"):
        vals = [r[1][k] for r in rows]
        c = Counter(vals)
        top = "  ".join(f"{a}:{b}" for a, b in sorted(c.items())[:7])
        if len(c) > 7:
            top += "  ..."
        print(f"{k:<12}{min(vals):>8}{max(vals):>8}   {top}")

    # ---- the rung bound, checked at each string's own v -------------------
    print("\n--- the ladder, checked against reality ---")
    from loop_runs import rung                                 # noqa: E402
    cache, bad = {}, 0
    for fn, d in rows:
        v = d["v"]
        if v not in cache:
            # above v = 125 the refined lemma is monotonically below HPV
            # (131, 121, 110, 105, 100, 95, 90, ... at v = 120, 121, ...), so
            # rung = HPV there and the expensive search is pointless.
            cache[v] = rung(7, v) if v <= 125 else (v, "HPV")
        t, src = cache[v]
        if d["SBY"] < t:
            print(f"  VIOLATION {fn}: v={v} T={d['SBY']} < claimed {t} [{src}]")
            bad += 1
    for v in sorted(cache):
        t, src = cache[v]
        got = [d["SBY"] for _, d in rows if d["v"] == v]
        print(f"  v = {v:<5} claim T >= {t:<5} [{src:<13}]  "
              f"actual T in [{min(got)}, {max(got)}]  "
              f"({len(got)} strings, slack {min(got) - t})")
    assert bad == 0, f"{bad} strings violate the rung bound"

    print("\nALL LEMMAS HOLD ON ALL "
          f"{len(rows)} KNOWN 7-SYMBOL SUPERPERMUTATIONS")
