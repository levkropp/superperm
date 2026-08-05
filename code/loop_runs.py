"""The block-count lemma with the per-loop run partition.

`sby_ladder.py:min_T_dirty` relaxes the loop structure to `N >= v` and is
therefore far too weak: its v = 121 witness at n = 7 wants 111 complete
traversals AND 12 runs of length 5, which needs 12 non-traversal loops when
only 10 exist.  This file puts the missing constraint back.

THE CONSTRAINT.  Every arc start is a generator of exactly one 2-loop.  Loop L
holds a_L <= n-1 of them, and a CLEAN RUN (a maximal stretch of arcs joined by
delta-out-of-a-full-arc) occupies consecutive generators of one loop.  So L's
arc starts partition into r_L >= 1 clean runs whose lengths sum to a_L, and

    N = sum r_L,     R = sum a_L,     A = (n-1)v - R,

with the sharp consequence that a run of length n-1 uses up a WHOLE loop:

    f := #runs of length n-1  =  #{L : a_L = n-1 and r_L = 1}   <=  v.

Every one of these is asserted on real walks by `code/dirty.py:dissect`.

WHAT THE SEARCH ENFORCES.  Write w = v - f for the non-traversal loops.  They
carry the other N - f runs, each of length <= n-2, with total length R-(n-1)f:

    (cap)    R - (n-1) f <= (n-1) w          each loop holds <= n-1 arc starts
    (fill)   N - f >= w                      each loop holds >= 1 run
    (big)    n5 <= w                         two runs of length n-2 cannot
                                             share a loop (2(n-2) > n-1)

plus the chain constraints already used in split_free_5889.py, widened by the
dirty escape as in sby_ladder.py:

    (ii)  c <= (N - f) + Y + dirty + 1
    (iii) f <= (n-3) c + (m + Y + dirty + 1)
          dirty <= n_partial = S + n_split <= 2S,   dirty <= N - 1

T = S + B + Y with B = N - dirty is minimised over all of it.  Taking
n_split = S and dirty maximal is the correct relaxation: T decreases in dirty
and every constraint is loosened by it.
"""

import math

CEIL = lambda p, q: -(-p // q)
BETA = {5: 7, 6: 26, 7: 125}            # split-free floor on B+Y (BLOCK)


def base(n):
    return n + math.factorial(n) + math.factorial(n - 1) - 3


def realizable(n, v, f, n5, m, short):
    """Can v loops of capacity n-1 carry exactly this run profile?

    f runs of length n-1 each eat a whole loop.  The remaining w = v - f loops
    carry the n5 runs of length n-2 and the m runs of length <= n-3 (total
    length `short`).  Since 2(n-2) > n-1, no loop holds two (n-2)-runs, and a
    loop that holds one has exactly ONE unit of capacity left -- so it can take
    at most a single run of length 1 and nothing else.  Let x be how many of
    the n5 loops do that; the rest of the short runs must fill the remaining
    w - n5 loops, each non-empty and of capacity n-1.

    Only necessary conditions are used, so this is a relaxation: it can accept
    a profile that is not truly packable, which keeps the resulting bound a
    valid lower bound.
    """
    L = n - 1
    w = v - f
    if w < 0 or n5 > w or m < 0 or short < 0:
        return False
    for x in range(0, min(n5, m) + 1):
        wp, mp, sp = w - n5, m - x, short - x
        if wp < 0 or mp < 0 or sp < 0:
            continue
        if mp == 0:
            if sp == 0 and wp == 0:
                return True
            continue
        if wp < 1 or wp > mp:            # every remaining loop needs a run
            continue
        if not (mp <= sp <= (L - 2) * mp):
            continue
        if sp > L * wp:                  # capacity of the remaining loops
            continue
        # A loop holding t arc starts in runs of length <= L-2 needs
        # ceil(t/(L-2)) runs -- in particular a loop with a full t = L is NOT
        # a traversal here, so it needs at least two.  Minimising over the
        # split of sp into wp loop totals of at most L gives:
        if mp < wp + max(0, CEIL(sp - (L - 2) * wp, 2)):
            continue
        return True
    return False


def _score(n, v, A, R, S, f, n5, m, short):
    """T for one fully specified profile, or None if it is infeasible."""
    L = n - 1
    if m < 0 or short < 0:
        return None
    if short == 0:
        if m != 0:
            return None
    else:
        if not (m <= short <= (L - 2) * m):
            return None
    if not realizable(n, v, f, n5, m, short):
        return None
    N = f + n5 + m
    if N < 1:
        return None
    dirty = min(2 * S, N - 1)
    B = N - dirty
    if B < 1:
        return None
    # (ii)+(iii) solved for Y
    need = f - (L - 2) * (n5 + m) - m - (L - 1) * (dirty + 1)
    Y = max(0, CEIL(need, L - 1))
    return S + B + Y


def min_T(n, v, brute=False):
    """Minimum of T = S+B+Y at this v under the refined lemma."""
    L, F1 = n - 1, math.factorial(n - 1)
    best, arg = None, None
    for A in range(0, L * v - F1 + 1):
        R = L * v - A
        S = R - F1
        if S < 0:
            continue
        for f in range(0, min(v, R // L) + 1):
            w = v - f
            rem = R - L * f                       # arc starts outside them
            if rem < 0 or rem > L * w:            # (cap)
                continue
            if w == 0 and rem != 0:
                continue
            hi5 = min(w, rem // (L - 1)) if L > 1 else 0      # (big)
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
                        # With dirty pinned at 2S, T(m) is flat and then has
                        # slope +1, so the minimum sits at the smallest
                        # REALIZABLE m.  Take the first few of those, plus the
                        # top of the range, to cover the dirty = N-1 corner.
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
                        arg = dict(A=A, R=R, S=S, f=f, n5=n5, m=m,
                                   short=short, N=f + n5 + m,
                                   dirty=min(2 * S, f + n5 + m - 1))
    if best is not None:
        arg['B'] = arg['N'] - arg['dirty']
        arg['Y'] = best - arg['S'] - arg['B']
    return best, arg


def rung(n, v, lemma=None):
    """Best available lower bound on T at this v: HPV, BLOCK, or the lemma."""
    F2 = math.factorial(n - 2)
    if lemma is None:
        lemma, _ = min_T(n, v)
    cands = [(v, "HPV")]
    if v == F2:
        cands.append((BETA[n], "BLOCK"))
    if lemma is not None:
        cands.append((lemma, "refined lemma"))
    return max(cands)


if __name__ == "__main__":
    print(__doc__.split("WHAT THE SEARCH")[0].strip())

    # ---- soundness: the candidate-m shortcut must agree with brute force --
    print("\n--- shortcut vs brute force (n = 5, 6) ---")
    for n in (5, 6):
        F2 = math.factorial(n - 2)
        for v in range(F2, F2 + 3):
            a, _ = min_T(n, v)
            b, _ = min_T(n, v, brute=True)
            print(f"  n={n} v={v:<4} shortcut {a}   brute {b}   "
                  f"{'OK' if a == b else 'MISMATCH'}")
            assert a == b, (n, v, a, b)

    # ---- the ladder ------------------------------------------------------
    print("\n--- the ladder, rung by rung ---")
    known = {5: 153, 6: 872, 7: None}
    for n in (5, 6, 7):
        F2 = math.factorial(n - 2)
        print(f"\n  n = {n}   base {base(n)}   covering floor v >= {F2}")
        worst = None
        for v in range(F2, F2 + 6):
            lem, _ = min_T(n, v)
            t, src = rung(n, v, lem)
            print(f"    v = {v:<5} T >= {t:<5} [{src:<13}]"
                  f"  length >= {base(n) + t:<6}  lemma alone: {lem}")
            worst = t if worst is None else min(worst, t)
        print(f"    => s({n}) >= {base(n) + worst}")
        if known[n]:
            assert base(n) + worst <= known[n], "UNSOUND"

    # ---- the binding state at n = 7, v = 121 -----------------------------
    print("\n--- n = 7, v = 121, broken out by A (S = 6 - A) ---")
    for A in range(0, 7):
        best, arg = None, None
        R, S = 726 - A, 6 - A
        for f in range(0, 122):
            w = 121 - f
            rem = R - 6 * f
            if rem < 0 or rem > 6 * w or (w == 0 and rem != 0):
                continue
            for n5 in range(0, min(w, rem // 5) + 1):
                short = rem - 5 * n5
                lo, hi = (0, 0) if short == 0 else (max(CEIL(short, 4), 1),
                                                    short)
                for m in range(lo, hi + 1):
                    T = _score(7, 121, A, R, S, f, n5, m, short)
                    if T is None:
                        continue
                    if best is None or T < best:
                        N = f + n5 + m
                        d = min(2 * S, N - 1)
                        best, arg = T, dict(f=f, n5=n5, m=m, short=short,
                                            N=N, dirty=d, B=N - d,
                                            Y=T - S - (N - d))
                    break            # T is non-decreasing in m
        print(f"    A = {A}  S = {S}   min T = {best}   {arg}")
