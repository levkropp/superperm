"""The ledger model: T = (n-1)d + (B+Y) - A, and what it permits at n >= 8.

Rewrites the SBY bookkeeping in coordinates that make the upper-bound question
a single scalar objective.  Put

    d = v - (n-2)!          excess 2-loops entered beyond an exact cover

and substitute the Split Identity  S = (n-1)(v - (n-2)!) - A  into T = S+B+Y:

    MASTER IDENTITY        T = (n-1) d + (B + Y) - A .

It is an identity, not a bound, and it holds on every measured walk.  Two
things fall straight out of it.

1.  EGAN IS ONE POINT -- and `code/census.py` pins down which.  Every Egan
    string measured, at n = 6, 7, 8 and 9, sits at exactly

        A = 1,  B = 1,  Y = 0,  d = (n-3)!,  S = (n-1)(n-3)! - 1,

    i.e. a SINGLE BLOCK with maximal splits, and B+Y-A = 0.  Since
    (n-2)! + (n-3)! = (n-1)(n-3)!, that is the zero-saving vertex.  The
    abstract complete-traversal construction (d = 0, B = (n-2)!, Y ~ (n-3)!)
    is a DIFFERENT vertex, realised by the n = 9 string 409113.

2.  THE OBJECTIVE.  Every record measured is exactly HPV-tight (T = v):
    872, 5906, 46204, 408966.  Imposing T = v on the identity gives

        d = (n-3)! - (B+Y-A)/(n-2),      saving over Egan = (B+Y-A)/(n-2).

    So beating Egan by k costs exactly k(n-2) units of B+Y-A -- and since
    B <= T, the saving is capped at (n-3)!, i.e. at the HPV bound.  Note the
    exchange rate WORSENS with n: n-2 blocks per character saved.

WHAT THIS FILE DOES.

  * asserts the master identity on every walk the repo has coordinates for;
  * checks that B+Y-A is invariant across the 136 champions even though A and
    S individually scatter (lemma_arsenal.md 6);
  * sweeps the HPV-TIGHT FRONTIER -- the smallest d at which a walk with T = v
    is not excluded by the arsenal -- at n = 6, 7, 8, 9;
  * prints the forced parameter vector a record must have at n = 8 and 9.

THE FRONTIER IS THE INTERESTING OUTPUT.  It is d_min = 1, 1, 5, ... at
n = 6, 7, 8 -- so the model's own constraints DO tighten with n, and at n = 8
they already exclude the four cheapest rungs outright.  The mechanism is the
dirty budget: HPV-tightness needs T = v, which forces N <= v + S, while the
chain constraint needs Y large unless dirty = 2S = 2(n-1)d is large.  Those
two only reconcile once d is a constant fraction of (n-3)!/(n-1).

It is still far too loose to predict.  At n = 6 and 7 it permits savings of 5
and 23 where truth delivers 1 and 2.  So this is a CONSTRUCTION model -- it
says exactly what to build -- and not a bound model.

Usage:  python3 code/ledger.py
"""

import json
import math
import os
import sys

sys.path.insert(0, "code")
from loop_runs import base, realizable, CEIL                     # noqa: E402


# --------------------------------------------------------------------------
# 1.  The master identity on every walk with published coordinates.
#     Sources: notes/lemma_arsenal.md 6 (measured), 1 (identities).
# --------------------------------------------------------------------------

# MEASURED by `code/census.py`, not transcribed.  An earlier hand-entered
# version of this table put Egan 5908 at (d=0, B=120, Y=24); that describes the
# abstract complete-traversal construction, NOT the actual 5908 string, which
# is a SINGLE BLOCK.  The census caught it.  Every Egan string at every n turns
# out to sit at the same vertex: A = 1, B = 1, Y = 0, d = (n-3)!.
WALKS = [
    # name                     n   length   v     A    S     B+Y   Y
    ("Houston 872",            6,    872,     29,   0,    25,    4,   0),
    ("Egan 873",               6,    873,     30,   1,    29,    1,   0),
    ("Egan 5908",              7,   5908,    144,   1,   143,    1,   0),
    ("jupiter 5907",           7,   5907,    140,   0,   120,   23,   3),
    ("champion 5906",          7,   5906,    142,   8,   124,   18,   0),
    ("Raudvere 46204",         8,  46204,    839,   0,   833,    6,   0),
    ("Egan 46205",             8,  46205,    840,   1,   839,    1,   0),
    ("Egan 408966",            9, 408966,   5760,   1,  5759,    1,   0),
    ("409113 (d = 0 vertex)",  9, 409113,   5040,   0,     0, 5907, 867),
]

CENSUS = "data/census.json"


def identity_check():
    print("--- master identity  T = (n-1)d + (B+Y) - A ---")
    for name, n, length, v, A, S, BY, Y in WALKS:
        F2 = math.factorial(n - 2)
        T = length - base(n)
        d = v - F2
        rhs = (n - 1) * d + BY - A
        split = (n - 1) * (v - F2) - A          # Split Identity, gives S
        sby = S + BY                            # SBY, gives T
        ok = (T == rhs == sby) and split == S
        print(f"  {name:<22} n={n}  T={T:<6} d={d:<5} B+Y={BY:<5} A={A:<3}"
              f"  ->  {rhs:<6} {'OK' if ok else 'MISMATCH'}")
        assert ok, name
    print(f"  all {len(WALKS)} consistent with Split Identity + SBY")

    if os.path.exists(CENSUS):
        rows = json.load(open(CENSUS))
        for r in rows:
            assert r["T"] == (r["n"] - 1) * r["d"] + (r["B"] + r["Y"]) - r["A"]
        print(f"  census: identity re-checked on all {len(rows)} measured "
              f"strings ({CENSUS})")
    else:
        print(f"  ({CENSUS} absent -- run `python3 code/census.py`)")


def champion_invariant():
    """A and S scatter across the 136 champions; B+Y-A must not.

    lemma_arsenal.md 6: every champion has T = v = 142 and A = 132 - S with
    S in 114..124.  HPV-tightness then forces B+Y = T - S = 142 - S, so
    B+Y-A = (142-S) - (132-S) = 10 identically.
    """
    print("\n--- B+Y-A across the 136 n=7 champions (T = v = 142) ---")
    vals = set()
    for S in range(114, 125):
        A = 132 - S
        BY = 142 - S
        vals.add(BY - A)
    print(f"  S ranges 114..124, A ranges {132-124}..{132-114}, "
          f"B+Y ranges {142-124}..{142-114}")
    print(f"  B+Y-A takes values {sorted(vals)}   "
          f"{'INVARIANT' if len(vals) == 1 else 'NOT INVARIANT'}")
    assert vals == {10}
    print(f"  saving = (B+Y-A)/(n-2) = 10/5 = 2   (5908 -> 5906)  OK")


# --------------------------------------------------------------------------
# 2.  The HPV-tight frontier.
#
# A walk with T = v exists at rung v only if the refined lemma's floor at that
# rung is <= v.  min_T(n, v) IS that floor, so the frontier is the smallest v
# with min_T(n, v) <= v, and the permitted saving is (n-3)! - (v - (n-2)!).
# --------------------------------------------------------------------------

def tight_witness(n, v, cap=None):
    """A profile at rung v with T <= cap (default cap = v), or None.

    With cap = v this decides HPV-tightness.  Sweeping cap upward gives the
    rung minimum min_T(n, v), which is what the ladder needs.  Exact, and fast.

    The speed comes from two prunes that only hold in the HPV-tight regime.

        (window)  T >= S + (N - dirty) >= N - S because dirty <= 2S, so
                  T <= v forces  ceil(R/(n-1)) <= N <= v + S.  At small d
                  that window has width O((n-1)d), not O((n-1)!).

        (slack)   let E = (n-1)N - R be the unused arc capacity.  A run of
                  length n-1 wastes 0 of it, one of length n-2 wastes 1, and
                  a short run of length l wastes (n-1)-l >= 2.  Hence
                      E = n5 + (n-1)m - short,   n5 <= E,   2m <= E,
                  so the profile search is O(E^2) instead of O(v^2).

    Scoring below is `loop_runs._score` inlined: dirty maximal at min(2S,N-1),
    Y forced by the chain constraints (ii)+(iii).
    """
    L, F1 = n - 1, math.factorial(n - 1)
    if cap is None:
        cap = v
    for A in range(0, L * v - F1 + 1):
        R = L * v - A
        S = R - F1
        if S < 0:
            continue
        for N in range(CEIL(R, L), cap + S + 1):
            E = L * N - R
            if E < 0:
                continue
            dirty0 = min(2 * S, N - 1)
            if S + N - dirty0 > cap:              # T >= S+B > v even at Y = 0
                continue
            # Y <= v - S - N + dirty is forced, and substituting f = N-n5-m
            # into the chain constraint turns that into
            #     (L-1) n5 + L m >= K.
            # Subject to n5 + (L-1) m <= E (which short >= m forces), the left
            # side maxes out at (L-1)E, so this rung dies early if K is bigger.
            W = (L - 1) * (cap - S - N + dirty0)
            K = N - W - (L - 1) * (dirty0 + 1)
            if (L - 1) * E < K:
                continue
            for n5 in range(E, -1, -1):
                for m in range(0, E // 2 + 1):
                    short = L * m - E + n5
                    f = N - n5 - m
                    if f < 0 or short < 0:
                        continue
                    if short == 0:
                        if m != 0:
                            continue
                    elif not (m <= short <= (L - 2) * m):
                        continue
                    if f > v or n5 > v - f:            # (big), f eats a loop
                        continue
                    if not realizable(n, v, f, n5, m, short):
                        continue
                    dirty = min(2 * S, N - 1)
                    B = N - dirty
                    if B < 1:
                        continue
                    need = (f - (L - 2) * (n5 + m) - m
                            - (L - 1) * (dirty + 1))
                    Y = max(0, CEIL(need, L - 1))
                    T = S + B + Y
                    if T <= cap:
                        return dict(A=A, S=S, N=N, f=f, n5=n5, m=m,
                                    short=short, dirty=dirty, B=B, Y=Y, T=T)
    return None


def frontier(n, span=4):
    F2 = math.factorial(n - 2)
    rows = []
    for d in range(0, span):
        v = F2 + d
        w = tight_witness(n, v)
        rows.append((d, v, w))
    return rows


def frontier_report(n, span=4):
    F2, F3 = math.factorial(n - 2), math.factorial(n - 3)
    print(f"\n--- n = {n}:  HPV-tight frontier  (Egan T = {(n-1)*F3}) ---")
    hit = None
    for d, v, w in frontier(n, span):
        mark = "HPV-TIGHT FEASIBLE" if w else "EXCLUDED"
        print(f"  d={d}  v={v:<5} {mark}")
        if w and hit is None:
            hit = (d, v, w)
    if hit is None:
        print(f"  no HPV-tight rung with d < {span}")
        return None
    d, v, w = hit
    saving = F3 - d
    print(f"  => model permits saving {saving} = (n-3)! - {d}, "
          f"length {base(n) + v}")
    print(f"     witness: A={w['A']} S={w['S']} f={w['f']} n5={w['n5']} "
          f"m={w['m']} N={w['N']} dirty={w['dirty']} B={w['B']} Y={w['Y']} "
          f"T={w['T']}")
    return saving


# --------------------------------------------------------------------------
# 2c.  The Rung Bound -- the Balance Bound extended off the exact-cover rung,
#      which turns the whole ladder into a closed form.
#
# At v = (n-2)! + d write A for the accidents, S = (n-1)d - A, and let u be the
# loops with a_L < n-1 (each wastes a generator, so u <= A).  Then
#
#   (runs)   N >= 2v - f - u >= 2v - f - A;
#   (chain)  f <= (n-2)(N - f + Y + dirty + 1);
#   (dirty)  dirty <= 2S, and taking it maximal only helps both of the above.
#
# T = S + (N - dirty) + Y is then bounded below by
#     max( 2v - f - A - S,  (n-1)f/(n-2) - 3S - 1 ),
# falling and rising in f.  At the crossing the A-dependence cancels (it
# survives only inside f*, which decreases in A), so A = 0 is optimal and
#
#     T >= ceil( (2(n-1)(n-2)! - (n-1)(4n-9)d - (n-2)) / (2n-3) ).
#
# d = 0 recovers the Balance Bound.  The per-rung collapse rate is therefore
# not fitted but DERIVED:  slope = (n-1)(4n-9)/(2n-3) ~ 2n-3.
#
# Setting T = v and solving gives the crossing, hence the whole ladder:
#
#     d* = ((n-2)! - (n-2)) / ((n-2)(4n-3)),
#     s(n) >= HPV(n) + ceil(d*)      ~   HPV(n) + (n-4)!/4 .
# --------------------------------------------------------------------------

def rung_bound(n, d):
    """Closed-form floor on T at rung v = (n-2)! + d.  Exact at d = 0."""
    F2 = math.factorial(n - 2)
    return CEIL(2 * (n - 1) * F2 - (n - 1) * (4 * n - 9) * d - (n - 2),
                2 * n - 3)


def rung_slope(n):
    return (n - 1) * (4 * n - 9) / (2 * n - 3)


def dmin_closed(n):
    """ceil of the crossing d* where the rung bound meets HPV."""
    return CEIL(math.factorial(n - 2) - (n - 2), (n - 2) * (4 * n - 3))


def hpv(n):
    return (math.factorial(n) + math.factorial(n - 1)
            + math.factorial(n - 2) + n - 3)


def closed_ladder(upto=12):
    print("\n--- closed-form ladder:  s(n) >= HPV(n) + ceil(d*) ---")
    known = {5: 153, 6: 868, 7: 5885, 8: 46090}      # searched values above
    print(f"  {'n':>3} {'HPV(n)':>12} {'d*':>8} {'bound':>12} "
          f"{'searched':>10} {'slope':>7}")
    for n in range(5, upto + 1):
        dm = dmin_closed(n)
        b = hpv(n) + dm
        k = known.get(n)
        assert k is None or b == k, (n, b, k)
        print(f"  {n:>3} {hpv(n):>12} {dm:>8} {b:>12} "
              f"{(k if k else '-'):>10} {rung_slope(n):>7.2f}")
    print("  n = 5 returns s(5) = 153 exactly -- the soundness gate.")
    print("  d* ~ (n-2)!/(4n^2) = Theta((n-4)!/4), so the bound sits")
    print("  factorially above HPV, but a factor ~4n below Egan's (n-3)!.")


# --------------------------------------------------------------------------
# 3.  What a record must look like -- pure arithmetic from the identity.
# --------------------------------------------------------------------------

def min_T_at(n, v, lo=None, hi=None):
    """Rung minimum: smallest T with a feasible profile at v.  Binary search."""
    lo = v - 40 if lo is None else lo
    hi = v + 300 if hi is None else hi
    best = None
    while lo <= hi:
        mid = (lo + hi) // 2
        if tight_witness(n, v, cap=mid):
            best, hi = mid, mid - 1
        else:
            lo = mid + 1
    return best


GATE = {                      # published rung minima, lemma_arsenal.md 4.1/11
    6: {24: 27, 25: 20},
    7: {120: 131, 121: 121, 122: 110, 123: 105, 124: 100},
}


def ladder(n, span=10):
    """min over rungs of max(v, min_T(n,v)) -- the elementary lower bound."""
    F2, B0 = math.factorial(n - 2), base(n)
    print(f"\n--- n = {n}: ladder rungs (bound = min of max(v, min_T)) ---")
    best = None
    for v in range(F2, F2 + span):
        mt = min_T_at(n, v)
        r = max(v, mt if mt is not None else 10 ** 9)
        best = r if best is None else min(best, r)
        want = GATE.get(n, {}).get(v)
        flag = "" if want is None else (" GATE OK" if want == mt else
                                        f" GATE FAIL want {want}")
        assert want is None or want == mt, (n, v, mt, want)
        print(f"  v={v:<6} min_T={mt}   rung={r}{flag}", flush=True)
    print(f"  => s({n}) >= {B0} + {best} = {B0 + best}")
    return B0 + best


# --------------------------------------------------------------------------
# 2b.  The Balance Bound -- a closed form for the exact-cover rung.
#
# At v = (n-2)! the rung is completely rigid: R = (n-1)v = (n-1)!, so A = 0,
# S = 0, every loop is fully used (a_L = n-1), dirty <= 2S = 0 and B = N.
# Write f for the number of complete traversals (loops with r_L = 1).  Then
#
#   (runs)   a non-complete loop needs >= 2 runs, so   N >= 2v - f;
#   (chain)  f <= (n-2)(1 + Y + N - f)  gives   Y >= (n-1)f/(n-2) - N - 1.
#
# T = N + Y is therefore >= max(2v - f, (n-1)f/(n-2) - 1).  The first falls
# and the second rises in f, so the bound is worst at the crossing, and
#
#       T  >=  ceil( (2(n-1)v - (n-2)) / (2n-3) ),
#       g0 :=  T - v  >=  ceil( ((n-2)! - (n-2)) / (2n-3) )  ~  (n-3)!/2 .
#
# So AT THIS ONE RUNG the elementary bound already exceeds HPV by half of
# Egan's whole excess.  Pure algebra -- no search.  The ladder then takes the
# minimum over rungs, and that is where it is lost.
# --------------------------------------------------------------------------

def balance_bound(n, v=None):
    """Closed-form floor on T at the exact-cover rung v = (n-2)!."""
    if v is None:
        v = math.factorial(n - 2)
    return CEIL(2 * (n - 1) * v - (n - 2), 2 * n - 3)


def balance_report(upto=12):
    print("\n--- Balance Bound at the exact-cover rung v = (n-2)! ---")
    print(f"  {'n':>3} {'v=(n-2)!':>10} {'T >=':>9} {'g0':>8} "
          f"{'(n-3)!':>9} {'g0/(n-3)!':>10}")
    for n in range(5, upto + 1):
        v = math.factorial(n - 2)
        t = balance_bound(n)
        F3 = math.factorial(n - 3)
        print(f"  {n:>3} {v:>10} {t:>9} {t-v:>8} {F3:>9} {(t-v)/F3:>10.3f}")
    print("  g0/(n-3)! -> 1/2: at the exact-cover rung the elementary bound")
    print("  reaches half of Egan's excess, for every n, with no computation.")


def design(n, savings):
    F2, F3 = math.factorial(n - 2), math.factorial(n - 3)
    egan = base(n) + (n - 1) * F3
    print(f"\n--- n = {n}: forced parameters at each saving "
          f"(Y = A = 0)   Egan = {egan} ---")
    print(f"  {'save':>6} {'length':>9} {'d':>5} {'v=T':>6} {'S':>6} "
          f"{'B':>6} {'R':>7} {'arcs/blk':>9}")
    for k in savings:
        d = F3 - k
        if d < 0:
            continue
        v = F2 + d
        T = v
        S = (n - 1) * d
        B = F2 - (n - 2) * d                    # = (n-2)k
        R = math.factorial(n - 1) + S
        apb = R / B if B > 0 else float('inf')
        print(f"  {k:>6} {base(n)+T:>9} {d:>5} {v:>6} {S:>6} "
              f"{B:>6} {R:>7} {apb:>9.2f}")
    print(f"  arcs/block -> n-1 = {n-1} exactly at saving {F3}, where every")
    print(f"  block is a complete traversal -- the configuration the")
    print(f"  Chain-Count Lemma excludes.  The model closes on itself there.")


if __name__ == "__main__":
    print(__doc__.split("Usage:")[0].strip())
    print()
    identity_check()
    champion_invariant()

    # spans chosen from the known frontier: d_min = 1, 1, 5 at n = 6, 7, 8.
    for n, span in ((6, 3), (7, 3), (8, 7)):
        frontier_report(n, span)

    balance_report()
    closed_ladder()
    for n, span in ((6, 6), (7, 6), (8, 8)):
        ladder(n, span)

    design(8, [0, 1, 5, 30, 60, 100, 115, 119, 120])
    design(9, [0, 1, 30, 100, 360, 600, 719, 720])

    print("\n  n = 9 frontier is slow (minutes per rung); run it directly:")
    print("    python3 -c \"import sys;sys.path.insert(0,'code');"
          "import ledger,math;print(ledger.tight_witness(9,5040+d))\"")
