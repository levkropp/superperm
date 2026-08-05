"""The partition-closure cap W(g) and its sensitivity to the exact table.

From a7/bundle_v2/A7_5896_PROOF_NOTE.md section 4:

    r(k) = min{ g : M_7(g) >= k }          for k <= 41
    r(42) >= 22                            (since M_7(21) = 41)
    D(0) = 0,  D(L) = max_{1<=k<=min(KMAX,L)} ( r(k) + D(L-k) )
    W(g) = max{ L : D(L) <= g }            then M_7(g) <= W(g)

The a7 bundle's decisive value is W(66) = 130; the delta=12 frontier
survives because the derived caps still exceed the block counts N.

This script (a) reproduces their W table from M_7(0..21), and (b) asks the
leverage question: if the exact table were pushed past 21, how far does
W(66) fall?
"""

# g = 0..21: the a7 bundle's published exact table (reproduced by macro7.c).
M7_PUBLISHED = [5, 5, 9, 9, 13, 13, 16, 16, 20, 20, 24, 24,
                27, 27, 31, 31, 34, 34, 36, 38, 40, 41]

# g = 22..40: new, proven here by macro7.c under bootstrap pruning.  Each is
# certified both ways -- a witness checked by code/verify_witness.py, and an
# exhaustive pruned search showing nothing longer fits.
M7_NEW = [43, 44, 46, 47, 50, 51, 52, 54, 56, 57, 59,
          60, 63, 64, 66, 66, 68, 69, 71]

M7_EXACT = M7_PUBLISHED                      # bundle baseline, for reproduction
M7_FULL = M7_PUBLISHED + M7_NEW              # g = 0..40, everything proven

REF_W = {21: 41, 30: 61, 36: 71, 38: 75, 42: 82, 48: 95,
         54: 106, 60: 117, 62: 120, 63: 122, 64: 124, 65: 125, 66: 130}


def build_r(table):
    """r(k) for k = 1..max(table); table[g] = M_7(g) exactly."""
    top = table[-1]
    r = {}
    for k in range(1, top + 1):
        r[k] = next(g for g, m in enumerate(table) if m >= k)
    # one certified step past the exact table: a chain of top+1 macros needs
    # strictly more than the last exact budget
    r[top + 1] = len(table)
    return r


def capacity(table, gmax=80):
    r = build_r(table)
    kmax = max(r)
    D = [0] * (gmax * 4 + 2)
    L = 0
    Ds = [0]
    while True:
        L += 1
        best = max(r[k] + Ds[L - k] for k in range(1, min(kmax, L) + 1))
        Ds.append(best)
        if best > gmax:
            break
    W = {}
    for g in range(gmax + 1):
        W[g] = max(L for L in range(len(Ds)) if Ds[L] <= g)
    return W, r


if __name__ == "__main__":
    W, r = capacity(M7_EXACT)
    print("--- reproduce the a7 bundle's conservative cap W(g) ---")
    print(f"  r(42) = {r[42]}  (bundle states r(42) >= 22)")
    bad = 0
    for g, want in sorted(REF_W.items()):
        got = W[g]
        ok = "OK" if got == want else "MISMATCH"
        bad += got != want
        print(f"  W({g:2}) = {got:4}   bundle says {want:4}   {ok}")
    print("  => reproduced exactly" if not bad else f"  => {bad} mismatches")

    print("\n--- leverage: the exact table extended past g = 21 (proven here) ---")
    print(f"\n  {'exact to g':>10} {'last entry':>12} {'W(66)':>7} {'gain':>5}")
    base = W[66]
    print(f"  {21:>10} {'M_7(21)=41':>12} {base:>7} {0:>5}")
    for top in range(22, len(M7_FULL)):
        t = M7_FULL[: top + 1]
        Wx, _ = capacity(t)
        print(f"  {top:>10} {'M_7(%d)=%d' % (top, t[-1]):>12} "
              f"{Wx[66]:>7} {base - Wx[66]:>5}")

    print("""
  Read: W(66) is what the delta=12 cells are measured against.  The
  frontier rows survive with margins of only a few units (e.g. N=131 vs
  cap=135), so a handful of units off W propagates directly into kills.
""")
