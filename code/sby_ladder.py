"""The SBY ladder: an elementary s(6) >= 868, and exactly what is left.

With  length = n + n! + (n-1)! - 3 + S + B + Y  (docs/notes/block_count_lemma.md)
everything is a lower bound on  T := S + B + Y.  Four inputs, three of them
standard and one new, already close n = 6:

  [HPV]     T >= v.                       Houston-Pantone-Vatter, cited.
  [COVER]   v >= (n-2)!.                  the entered loops must cover all
                                          (n-1)! rotation classes, n-1 each.
  [SPLIT]   R = (n-1)v - A,  A >= 0.      the split identity (docs/notes/).
            With R = (n-1)! + S this reads  S = (n-1)(v - (n-2)!) - A,  so
            v = (n-2)! forces A = S = 0 -- the walk is SPLIT-FREE.
  [BLOCK]   split-free  =>  B + Y >= beta_n.   the block-count lemma:
            beta_5 = 7, beta_6 = 26, beta_7 = 125.

Because [SPLIT] makes the bottom rung of the ladder split-free, [BLOCK] lands
exactly where HPV is weakest:

        v = (n-2)!        T >= beta_n           (split-free)
        v > (n-2)!        T >= v                (HPV)

so  T >= min(beta_n, (n-2)! + 1)  with no case analysis at all.

    n = 5:  min(7, 7)     = 7    ->  s(5) >= 153.   EXACT.
    n = 6:  min(26, 25)   = 25   ->  s(6) >= 868.
    n = 7:  min(125, 121) = 121  ->  s(7) >= 5885.  (HPV alone: 5884.)

The n = 6 line is the point.  868 falls out of four lines of bookkeeping plus
one finite search -- no exact-cover enumeration, no 10,068 covers, no CP-SAT
class-TSP.  It is an independent re-derivation of the repo's own headline by a
route that shares nothing with it.

And the ladder now says precisely what is missing.  A target T >= (n-2)! + k
is free at v = (n-2)! (if beta_n >= (n-2)!+k) and free at v >= (n-2)!+k (HPV).
What is left is the narrow band

        (n-2)! < v < (n-2)! + k,     1 <= S <= (n-1)k - 1.

    s(6) >= 869 :  the single case  v = 25,  1 <= S <= 5.
    s(7) >= 5889:  v = 121..124,  1 <= S <= 24.

`min_T_dirty` below runs the block-count lemma generalised to allow DIRTY
cheap jumps -- delta out of a partial arc, which lands in an unrelated 2-loop
and is exactly what a split buys.  It is far too weak to close the band, and
the printout says by how much.  That gap is the real open problem, and it is
the same problem at both n.
"""

import math

CEIL = lambda p, q: -(-p // q)
# beta_n = the split-free floor on B + Y.  beta_5, beta_6 and the counting
# part of beta_7 come from exit_table_n.py (which returns 7, 26, 124); the
# last unit of beta_7 is the period-map argument in split_free_5889.py.
BETA = {5: 7, 6: 26, 7: 125}


def base(n):
    return n + math.factorial(n) + math.factorial(n - 1) - 3


def unconditional(n):
    """min over v of the per-rung bound on T, using HPV + SPLIT + BLOCK."""
    F2 = math.factorial(n - 2)
    return min(BETA[n], F2 + 1)


def min_T_dirty(n, v):
    """Lower bound on T at this v, block-count lemma + dirty cheap jumps.

    A CLEAN RUN is a maximal stretch of arcs joined by delta-out-of-a-full-arc;
    it sits at consecutive generators of one loop, so 1 <= length <= n-1.  Runs
    are separated by costly jumps (B-1) or dirty cheap jumps (`dirty`), so
    N = B + dirty with dirty <= n_partial = S + n_split <= 2S.  T is decreasing
    in dirty and every constraint is loosened by it, so dirty = 2S is the
    correct relaxation for a lower bound.
    """
    L, F1 = n - 1, math.factorial(n - 1)
    best, arg = None, None
    A_max = (n - 1) * v - F1
    for A in range(0, A_max + 1):
        R = (n - 1) * v - A
        S = R - F1
        if S < 0:
            continue
        dirty = 2 * S
        for Y in range(0, 12):
            for f in range(0, R // L + 1):
                rem = R - L * f
                for n4 in range(0, rem // (L - 1) + 1):
                    short = rem - (L - 1) * n4
                    m_lo = 0 if short == 0 else CEIL(short, L - 2)
                    # (ii)+(iii): f <= (L-2)*c + m + Y + dirty + 1 with
                    #             c <= (n4 + m) + Y + dirty + 1
                    m = m_lo
                    while m <= short:
                        c = n4 + m + Y + dirty + 1
                        if f <= (L - 2) * c + m + Y + dirty + 1:
                            break
                        m += 1
                    else:
                        continue
                    N = f + n4 + m
                    if N < v or N < 2 * S + 1:
                        N = max(v, 2 * S + 1)
                    T = S + (N - dirty) + Y
                    if best is None or T < best:
                        best, arg = T, dict(A=A, S=S, R=R, dirty=dirty, Y=Y,
                                            f=f, n4=n4, m=m, N=N, B=N - dirty)
    return best, arg


if __name__ == "__main__":
    print(__doc__.split("`min_T_dirty`")[0].strip())

    print("\n" + "=" * 72)
    print("UNCONDITIONAL, from HPV + COVER + SPLIT + BLOCK")
    print("=" * 72)
    known = {5: 153, 6: 872, 7: None}
    for n in (5, 6, 7):
        F2 = math.factorial(n - 2)
        T = unconditional(n)
        hpv = base(n) + F2
        print(f"  n = {n}:  beta_{n} = {BETA[n]:<4} (n-2)!+1 = {F2 + 1:<4} "
              f"T >= {T:<4} length >= {base(n) + T:<6} "
              f"(HPV alone: {hpv})")
        if known[n]:
            assert base(n) + T <= known[n], "UNSOUND"
    assert base(5) + unconditional(5) == 153, "n=5 must be exact"
    assert base(6) + unconditional(6) == 868
    assert base(7) + unconditional(7) == 5885
    print("  n = 5 is exact (s(5) = 153), so the chain has no slack to hide "
          "an error in.")

    print("\n" + "=" * 72)
    print("WHAT IS LEFT, and how far the dirty-jump lemma gets")
    print("=" * 72)
    for n, k in ((6, 2), (7, 5)):
        F2 = math.factorial(n - 2)
        target = base(n) + F2 + k
        print(f"\n  n = {n}, target length {target} "
              f"(T >= {F2 + k}); band v = {F2 + 1}..{F2 + k - 1}")
        for v in range(F2 + 1, F2 + k):
            T, arg = min_T_dirty(n, v)
            hpvT = v
            print(f"    v = {v:<5} HPV: T >= {hpvT:<5} "
                  f"dirty-lemma: T >= {T:<5} best: T >= {max(T, hpvT):<5} "
                  f"length >= {base(n) + max(T, hpvT):<6} "
                  f"short by {target - base(n) - max(T, hpvT)}")
            if T < hpvT:
                print(f"        (lemma weaker than HPV here; witness {arg})")
