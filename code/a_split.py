"""The ladder rungs v = 121..124 at n = 7, broken out by A.

`loop_runs.min_T(n, v)` minimises T over ALL accident counts A at once, which
throws away information: the Split Identity ties A to S by S = (n-1)(v-(n-2)!) - A,
and the refined lemma behaves very differently at the two ends.  §6 of the note
does the split at v = 121 and finds only A = 0 survives.  Rungs 122 and 123 have
never been refined at all -- the ladder there is pure HPV -- so this file redoes
the split at every rung that matters.

WHY THESE RUNGS.  length = 5764 + T, and HPV gives T >= v, so every rung
v >= t is free for a target of 5764 + t.  Rung v = 120 is already 131.  Hence:

    target 5888 (= Lean, Hunter & Raudvere)   needs T >= 124   at v = 121,122,123
    target 5889                               needs T >= 125   at v = 121..124

GATE.  The v = 121 row must reproduce the published
T >= 121, 122, 123, 125, 126, 128, 129 for A = 0..6.

Usage:  python3 code/a_split.py
"""

import math
import sys

sys.path.insert(0, "code")
from loop_runs import CEIL, _score, realizable                  # noqa: E402


def min_T_at_A(n, v, A, brute=False):
    """Minimum T over profiles with this exact accident count."""
    L, F1 = n - 1, math.factorial(n - 1)
    R = L * v - A
    S = R - F1
    if S < 0:
        return None, None
    best, arg = None, None
    for f in range(0, min(v, R // L) + 1):
        w = v - f
        rem = R - L * f
        if rem < 0 or rem > L * w:
            continue
        if w == 0 and rem != 0:
            continue
        hi5 = min(w, rem // (L - 1)) if L > 1 else 0
        for n5 in range(0, hi5 + 1):
            short = rem - (L - 1) * n5
            if short < 0:
                continue
            if short == 0:
                cands = [0]
            else:
                if L - 2 < 1:
                    continue
                m_lo = max(CEIL(short, L - 2), 1)
                m_hi = short
                if m_lo > m_hi:
                    continue
                if brute:
                    cands = range(m_lo, m_hi + 1)
                else:
                    cands, x = [], m_lo
                    while x <= m_hi and len(cands) < 5:
                        if realizable(n, v, f, n5, x, short):
                            cands.append(x)
                        x += 1
                    cands.append(m_hi)
            for m in cands:
                T = _score(n, v, A, R, S, f, n5, m, short)
                if T is not None and (best is None or T < best):
                    best = T
                    N = f + n5 + m
                    dirty = min(2 * S, N - 1)
                    arg = dict(A=A, S=S, f=f, n5=n5, m=m, short=short,
                               N=N, dirty=dirty, B=N - dirty,
                               Y=T - S - (N - dirty))
    return best, arg


if __name__ == "__main__":
    print(__doc__.split("Usage:")[0].strip())
    n = 7
    L, F2 = n - 1, math.factorial(n - 2)

    print("\n--- GATE: v = 121 must reproduce 121,122,123,125,126,128,129 ---")
    want = [121, 122, 123, 125, 126, 128, 129]
    got = [min_T_at_A(n, 121, A)[0] for A in range(7)]
    print(f"  published {want}")
    print(f"  computed  {got}")
    assert got == want, "GATE FAILED -- the A-split does not reproduce §6"
    print("  GATE OK")

    for target, name in ((124, "5888  (= Lean, Hunter & Raudvere)"),
                         (125, "5889")):
        print(f"\n=== target T >= {target}  ->  s(7) >= {5764 + target} "
              f"{name} ===")
        allclear = True
        for v in range(121, target + 1):
            S_max = L * (v - F2)
            row, bad = [], []
            for A in range(0, S_max + 1):
                T, arg = min_T_at_A(n, v, A)
                if T is None:
                    continue
                row.append((A, T))
                if T < target:
                    bad.append((A, T, arg))
            lo = min(t for _, t in row)
            print(f"  v = {v}:  A = 0..{S_max},  min T = {lo}"
                  f"{'   CLEARS' if lo >= target else ''}")
            if bad:
                allclear = False
                print(f"    surviving states ({len(bad)} of {len(row)}): "
                      f"{[(A, T) for A, T, _ in bad]}")
                for A, T, arg in bad[:3]:
                    print(f"      A={A}: T={T}  S={arg['S']} f={arg['f']} "
                          f"n5={arg['n5']} m={arg['m']} N={arg['N']} "
                          f"dirty={arg['dirty']} B={arg['B']} Y={arg['Y']}")
        print(f"  => target {5764 + target} "
              f"{'REACHED' if allclear else 'not reached by this lemma'}")
