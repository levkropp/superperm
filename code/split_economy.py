"""The economics of a split: does the warm-up tax outgrow the saving with n?

HYPOTHESIS UNDER TEST.  The advantage a split buys shrinks as n grows, so past
some n every champion is split-free.

THE LEDGER.  T = S + B + Y and B = N - dirty, so

        T = S + N - dirty + Y.

Splits can only help through `dirty`, the free loop switches: a partial arc's
delta exit lands on a generator of a DIFFERENT loop, so the block is no longer
confined to one loop.

THE TAX, exactly.  A clean run's non-final arcs are all full (asserted in
dirty.py), so a partial arc can only ever be the LAST arc of a run -- every
partial arc TERMINATES a run.  Hence

        N >= n_partial = S + m        (m = #classes covered more than once)

while at the same time  dirty <= n_partial.  The fragmentation a split causes
and the loop switch it buys are bounded by the SAME quantity.  So the question
is quantitative: which one wins, and does the balance move with n?

Two diagnostics, both well defined per string, no reference walk needed:

    eta = dirty / n_partial       how much of the split is actually cashed in
    nu  = N - n_partial           run fragmentation beyond the forced minimum

and B = nu + (n_partial - dirty), so T = S + Y + nu + (n_partial - dirty).
Splits pay off only when eta is near 1 AND nu stays small.

Usage:  python3 code/split_economy.py
"""

import math
import os
import sys
from collections import Counter

sys.path.insert(0, "code")
from blockcount import Model                                    # noqa: E402
from permgraph import string_to_path                            # noqa: E402

SRC6 = ["data", "/home/lk/superperm-upstream/superpermutations/6"]
SRC7 = ["data/n7", "/home/lk/superperm-upstream/superpermutations/7",
        "/home/lk/superperm-upstream/superpermutations/7/7_5906"]


def load(dirs, n):
    alpha = "".join(str(i) for i in range(1, n + 1))
    out, seen = [], set()
    for d in dirs:
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            if not fn.endswith(".txt"):
                continue
            try:
                raw = open(os.path.join(d, fn)).read().strip()
            except Exception:
                continue
            if not raw or any(c not in alpha for c in raw):
                continue
            if len(raw) < math.factorial(n):
                continue
            if raw in seen:
                continue
            seen.add(raw)
            out.append((fn, [int(c) for c in raw]))
    return out


def ledger(m, n, path):
    """Recompute the split economy of one walk from the raw path."""
    cid = lambda u: min(u[k:] + u[:k] for k in range(n))
    arcs, cur = [], [path[0]]
    for u, w in zip(path, path[1:]):
        if m.weight(u, w) == 1:
            cur.append(w)
        else:
            arcs.append(cur)
            cur = [w]
    arcs.append(cur)
    jumps = [(a[-1], b[0], m.weight(a[-1], b[0]))
             for a, b in zip(arcs, arcs[1:])]

    R = len(arcs)
    S = R - math.factorial(n - 1)
    kc = Counter(cid(a[0]) for a in arcs)
    mm = sum(1 for c in kc.values() if c >= 2)          # split classes
    n_partial = sum(1 for a in arcs if len(a) < n)

    clean = dirty = 0
    for i, (u, w, wt) in enumerate(jumps):
        if wt != 2:
            continue
        if len(arcs[i]) == n and w == m.delta(u):
            clean += 1
        else:
            dirty += 1
    N = 1 + sum(1 for i, (u, w, wt) in enumerate(jumps)
                if not (wt == 2 and len(arcs[i]) == n and w == m.delta(u)))
    B = 1 + sum(1 for _, _, wt in jumps if wt >= 3)
    Y = sum(wt - 3 for _, _, wt in jumps if wt >= 3)
    length = n + sum(m.weight(u, w) for u, w in zip(path, path[1:]))
    assert N == B + dirty
    assert n_partial == S + mm, (n_partial, S, mm)
    assert N >= n_partial, "a partial arc must end a run"
    assert dirty <= n_partial
    return dict(length=length, R=R, S=S, m=mm, npart=n_partial,
                dirty=dirty, N=N, B=B, Y=Y, T=S + B + Y)


if __name__ == "__main__":
    print(__doc__.split("Usage:")[0].strip())
    for n, src in ((6, SRC6), (7, SRC7)):
        strings = load(src, n)
        if not strings:
            print(f"\nn = {n}: no strings found")
            continue
        mo = Model(n)
        rows = []
        for fn, digits in strings:
            path = string_to_path(digits, n)
            if len(set(path)) != math.factorial(n):
                continue
            rows.append((fn, ledger(mo, n, path)))
        print(f"\n=== n = {n}: {len(rows)} strings "
              f"(n_partial = S + m and N >= n_partial asserted on every one)")
        best = min(r[1]["length"] for r in rows)
        print(f"{'string':30}{'len':>6}{'S':>5}{'m':>5}{'nprt':>6}{'dirty':>7}"
              f"{'N':>6}{'B':>5}{'Y':>4}{'T':>5}{'eta':>7}{'nu':>5}")
        for fn, d in sorted(rows, key=lambda r: r[1]["length"])[:12]:
            eta = d["dirty"] / d["npart"] if d["npart"] else 0.0
            nu = d["N"] - d["npart"]
            print(f"{fn[:29]:30}{d['length']:>6}{d['S']:>5}{d['m']:>5}"
                  f"{d['npart']:>6}{d['dirty']:>7}{d['N']:>6}{d['B']:>5}"
                  f"{d['Y']:>4}{d['T']:>5}{eta:>7.3f}{nu:>5}")
        champs = [d for _, d in rows if d["length"] == best]
        free = [d for _, d in rows if d["S"] == 0]
        print(f"  shortest = {best}; split-free present: "
              f"{sorted({d['length'] for d in free}) if free else 'none'}")
        if champs:
            e = [d["dirty"] / d["npart"] for d in champs if d["npart"]]
            if e:
                print(f"  eta over the shortest strings: "
                      f"min {min(e):.3f}  max {max(e):.3f}")
        if free:
            tf = min(d["T"] for d in free)
            tc = min(d["T"] for _, d in rows)
            sc = [d["S"] for _, d in rows if d["T"] == tc][0]
            print(f"  best split-free T = {tf}; best overall T = {tc} "
                  f"at S = {sc}")
            if sc:
                print(f"  ADVANTAGE of splits = {tf - tc}; "
                      f"exchange rate (drop in B+Y)/S = "
                      f"{(tf - (tc - sc)) / sc:.4f}")
