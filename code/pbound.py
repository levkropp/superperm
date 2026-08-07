"""An ORDERING-FREE lower bound that beats HPV.

`lemma_arsenal.md` 2.7 and `second_order.md` A3 record the verdict *"no
ordering-free invariant beats HPV"*.  That was measured for `S + comps`, whose
minimum over arc sets is exactly `(n-2)!` = HPV.  Adding one more ordering-free
term changes it.

    CH2   Y >= p - 1,   p = fewest FREE CHAINS covering the delta-components
    IN5   B >= comps    -- false in general, but SIG2X makes it valid against
                           the OPTIMUM, which is the only place it is used

    =>    T = S + B + Y  >=  S + comps + (p - 1)              (CH3)

Every term reads the arc SET, so the bound is ordering-free.  What it is worth:

    validity, 1,030 n=6 census strings   0 violations, 1,029 EXACTLY TIGHT
    minimum over all 10,068 exact covers 29   = the true n=6 optimum
    HPV floor at the same rung           24

So at the rung that binds it is **5 above HPV**.  Its value at an exact cover is
`(n-1)(n-3)! - 1`, the Egan-1 line -- the same number the Chain-Count Lemma and
the Exposure Bound (S5) produce there, but reached without either's hypothesis.

WHY THE ERRORS RUN THE SAFE WAY.  `chainer.min_chains` falls back to a crude
floor when its node cap bites, which UNDER-states `p` and so under-states the
bound.  A minimum observed over a search is therefore an under-estimate: the
true minimum is `>=` what is reported.

WHAT THIS IS AIMED AT.  5905 at n = 7 means `T = 141`.  The 5906 champion has
`S=124, comps=18, p=1`, so the bound reads 142 there -- tight.  If the global
minimum at n = 7 is 142, then 5905 is excluded.  Searching for an arc set below
142 is NOT a proof either way; see `docs/notes/pbound.md` for what is claimed.

Usage:
  python3 code/pbound.py                 # validity + the exact-cover minimum
  python3 code/pbound.py --quick         # skip the 10,068-cover sweep
  python3 code/pbound.py --n 7 --calibrate
"""

import argparse
import collections
import math
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import chainer                                                    # noqa: E402
from build import coords, design_of                               # noqa: E402
from gen2 import Gen                                              # noqa: E402
from permgraph import string_to_path                              # noqa: E402


def value(g, arcs, node_cap=100_000, bound_only=False):
    """(bound, S, comps, p) for an arc set.  All four are ordering-free.

    `value.exact` says whether `p` is the true minimum chain count or only
    `chainer.min_chains`' crude floor `ceil(comps/longest)`.  The floor is a
    VALID lower bound, so the bound stays sound either way -- but a search that
    minimises this will otherwise chase states where the chain search merely
    gave up, which is exactly what happened at n = 7 (a reported 140 at
    comps = 116, where p = 13 was the floor and not a verified cover).
    """
    arcs = [tuple(a) for a in arcs]
    S = len(arcs) - g.F1
    comps, ends = g.components(arcs)
    p = chainer.min_chains(g.options(arcs, comps, ends),
                           node_cap=node_cap, bound_only=bound_only)
    value.exact = chainer.min_chains.exact
    return S + len(comps) + p - 1, S, len(comps), p


def of_string(g, digits):
    return value(g, design_of(string_to_path(digits, g.n)))


# ---------------------------------------------------------------------------

def validity(n=6):
    """The bound must never exceed T on a real string."""
    import census
    g = Gen(n)
    seen = viol = tight = 0
    worst = None
    for m, _, path in census.sources(9):
        if m != n:
            continue
        for digits in census.read_strings(path):
            if not digits or max(digits) != n or min(digits) != 1:
                continue
            p_ = string_to_path(digits, n)
            if len(p_) != math.factorial(n):
                continue
            des = design_of(p_)
            c = coords(des, n)
            b, S, C, p = value(g, des)
            seen += 1
            if b > c["T"]:
                viol += 1
                if worst is None or b - c["T"] > worst[0]:
                    worst = (b - c["T"], c["T"], b)
            elif b == c["T"]:
                tight += 1
    return seen, viol, tight, worst


def exact_cover_min(n=6, limit=None):
    """Minimum of the bound over every exact cover -- the rung HPV binds at."""
    from loopsearch import arcs_of, setup
    from quantise import setup as qsetup
    from saturated6 import saturated
    g, st, _, _ = setup(n)
    _, _, cls_of = qsetup(n)
    sysx, slack = saturated(n, math.factorial(n - 2), cls_of, cap=400000)
    hist = collections.Counter()
    for i, lids in enumerate(sysx):
        if limit and i >= limit:
            break
        hist[value(g, arcs_of(st, n, lids))[0]] += 1
    return len(sysx), slack, hist


def minimise(n, iters, seed=1, quiet=False):
    """Anneal loop systems to MINIMISE the bound.

    This is the objective the annealers of `docs/notes/constructor.md` 11 lacked: it
    is ordering-free, so no chaining is needed, and the target is a global
    minimum rather than a champion -- flatness near optima does not matter, only
    the floor does.
    """
    import random

    from loopsearch import arcs_of, covers, neighbours, setup
    g, st, cls_of, by_class = setup(n)
    fam = collections.defaultdict(list)
    for l in range(len(cls_of)):
        fam[st.fam_of_loop[l]].append(l)
    rng = random.Random(seed)
    cur = frozenset(fam[0])
    curv = value(g, arcs_of(st, n, cur))[0]
    best, bestv, bestex = cur, curv, value.exact
    bestverified = curv if value.exact else 1 << 30
    t0, t1 = 3.0, 0.05
    for it in range(iters):
        temp = t0 * (t1 / t0) ** (it / max(1, iters - 1))
        nxt = neighbours(cls_of, by_class, cur, g.F1, rng)
        if nxt is None:
            continue
        b, S, C, p = value(g, arcs_of(st, n, nxt))
        ex = value.exact
        if b <= curv or rng.random() < math.exp((curv - b) / temp):
            cur, curv = nxt, b
            if curv < bestv:
                best, bestv, bestex = cur, curv, ex
                if not quiet:
                    print(f"    it {it:>7}  bound = {bestv}   "
                          f"v={len(cur)} S={S} comps={C} p={p}"
                          f"{'' if ex else '   <-- p is the FLOOR, not verified'}",
                          flush=True)
            if b < bestverified and ex:
                bestverified = b
    return bestv, best, bestverified


def minimise_cuts(n, src, iters, seed=1, quiet=False):
    """Minimise the bound in CUT space, seeded from a real string.

    Loop space cannot be used at n = 7: `LOOP1` says a loop system has `A = 0`,
    and no n = 7 optimum does -- the A spectrum at length 5906 starts at **8**.
    So `loopsearch` was exploring a subspace that provably excludes every known
    n = 7 champion, which is why it never came near 142.  Cut space contains
    them, and near a champion `comps` is small enough (18) that `p` verifies in
    milliseconds.
    """
    import random

    from gen2 import chi_from_string
    g = Gen(n)
    digits = [int(c) for c in open(src).read() if c.isdigit()]
    chi = chi_from_string(g, string_to_path(digits, n))
    rng = random.Random(seed)

    def score(ch):
        """Fast bound, for the SWEEP only -- never for the verdict.

        `bound_only` is 144x faster at high `comps` and identical there, but it
        is weaker wherever the exact chain search would have succeeded: at the
        n = 6 exact cover it reads 27 against the exact 29.  So every apparent
        new best is re-priced exactly below, or the search manufactures dips
        exactly the way the crude floor did.
        """
        b, S, C, p = value(g, g.arcs_of(ch), bound_only=True)
        return b, S, C, p, value.exact

    cur = score(chi)
    seed_b, _, _, seed_p = value(g, g.arcs_of(chi))
    best, bestchi, bestex = seed_b, [set(c) for c in chi], value.exact
    cur = (seed_b,) + cur[1:3] + (seed_p, value.exact)
    print(f"  seed {os.path.basename(src)}: bound={cur[0]} "
          f"(S={cur[1]} comps={cur[2]} p={cur[3]} verified={cur[4]})", flush=True)
    t0, t1 = 1.5, 0.03
    for it in range(iters):
        temp = t0 * (t1 / t0) ** (it / max(1, iters - 1))
        cid = rng.randrange(len(chi))
        old = set(chi[cid])
        r = rng.random()
        if r < 0.4 and len(old) < n:
            chi[cid].add(rng.randrange(n))
        elif r < 0.7 and len(old) > 1:
            chi[cid].discard(rng.choice(sorted(old)))
        else:
            chi[cid].discard(rng.choice(sorted(old)))
            chi[cid].add(rng.randrange(n))
        if not chi[cid] or chi[cid] == old:
            chi[cid] = old
            continue
        b, S, C, p, ex = score(chi)
        if b <= cur[0] or rng.random() < math.exp((cur[0] - b) / temp):
            cur = (b, S, C, p, ex)
            if b < best:
                # the fast bound only says "worth pricing"; the exact one decides
                eb, eS, eC, ep = value(g, g.arcs_of(chi))
                if eb < best:
                    best, bestchi, bestex = eb, [set(c) for c in chi], value.exact
                    if not quiet:
                        print(f"    it {it:>7}  bound = {eb}   "
                              f"S={eS} comps={eC} p={ep}"
                              f"{'' if value.exact else '  <-- p NOT verified'}",
                              flush=True)
        else:
            chi[cid] = old
    return best, bestchi, bestex


def calibrate(n):
    """The bound at the known n-point(s), against T and HPV."""
    g = Gen(n)
    hpv = math.factorial(n - 2)
    rows = {6: [("houston 872", "data/houston_872.txt"),
                ("873-palindromic",
                 "/home/lk/superperm-upstream/superpermutations/6/873-palindromic.txt")],
            7: [("5906 champion", "data/n7/7_5906_derived_025c4805fc39.txt"),
                ("5913 exact cover", "data/n7/5913-palindromic.txt"),
                ("5908-egan", "data/n7/5908-egan.txt")]}.get(n, [])
    print(f"  HPV floor (n-2)! = {hpv}")
    for tag, path in rows:
        if not os.path.exists(path):
            print(f"  {tag:<20} (missing)")
            continue
        digits = [int(c) for c in open(path).read() if c.isdigit()]
        t = time.time()
        b, S, C, p = of_string(g, digits)
        c = coords(design_of(string_to_path(digits, n)), n)
        flag = "TIGHT" if b == c["T"] else f"slack {c['T'] - b}"
        print(f"  {tag:<20} T={c['T']:<5} bound={b:<5} "
              f"(S={S} comps={C} p={p})  {flag}   [{time.time()-t:.1f}s]",
              flush=True)


def main(n, quick, cal, iters, src):
    if cal:
        print(f"\n--- n = {n}: the bound at known points ---")
        calibrate(n)
        return 0

    if iters and src:
        print(f"\n--- n = {n}: minimising in CUT space from {os.path.basename(src)}, "
              f"{iters} iterations ---")
        best, _, ex = minimise_cuts(n, src, iters)
        print(f"  lowest bound found = {best}   (verified p: {ex})")
        return 0

    if iters:
        print(f"\n--- n = {n}: minimising the bound, {iters} iterations ---")
        hpv = math.factorial(n - 2)
        bestv, best, bestver = minimise(n, iters)
        print(f"  lowest bound found          = {bestv}   (HPV = {hpv})")
        print(f"  lowest with p VERIFIED exact = "
              f"{bestver if bestver < (1 << 30) else 'none'}")
        print("  (an unverified p is the crude floor ceil(comps/longest); it "
              "keeps the\n   bound VALID but understates it, so only the "
              "verified figure is meaningful\n   as an estimate of the true "
              "minimum)")
        return 0

    print(f"\n--- validity: the bound must never exceed T (n = {n}) ---")
    seen, viol, tight, worst = validity(n)
    print(f"  {seen} strings: {viol} violations, {tight} exactly tight")
    assert viol == 0, f"CH3 violated on {viol} strings, worst {worst}"

    print(f"\n--- the exact-cover rung, where HPV binds ---")
    if quick:
        tot, slack, hist = exact_cover_min(n, limit=500)
        print(f"  {tot} exact covers (S = {slack}); sampled 500")
    else:
        t = time.time()
        tot, slack, hist = exact_cover_min(n)
        print(f"  all {tot} exact covers (S = {slack}) in {time.time()-t:.0f}s")
    print(f"  bound histogram: {dict(sorted(hist.items()))}")
    lo = min(hist)
    hpv = math.factorial(n - 2)
    egan1 = (n - 1) * math.factorial(n - 3) - 1
    print(f"  MINIMUM = {lo}   against HPV = {hpv}   "
          f"(Egan-1 line = {egan1})")
    assert lo > hpv, "the bound did not beat HPV -- the whole direction is void"
    print(f"  => beats HPV by {lo - hpv} at the binding rung")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=6)
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--calibrate", action="store_true")
    ap.add_argument("--iters", type=int, default=0)
    ap.add_argument("--from", dest="src", default=None)
    args = ap.parse_args()
    print(__doc__.split("Usage:")[0].strip())
    sys.exit(main(args.n, args.quick, args.calibrate, args.iters, args.src))
