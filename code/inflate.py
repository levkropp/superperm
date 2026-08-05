"""What the ORDERING can move -- and the two [THM]s that turned out to be false.

`build.coords` computes

    A = (n-1)v - R          from the arc-start SET alone
    B, Y                    from weight(end of arc i, start of arc i+1)

so `A` is a function of the arc set and `B` is not.  Consequently **B can
always be inflated**: reorder the arcs so one free edge goes unused and the walk
gains a weight->=3 jump, while `A`, `S`, `v`, `d`, `comps` all stay put.  That
kills any claim of the shape

    (ordering-free hypothesis)  =>  (upper bound on B, Y or T)

and `A1EQ`'s forward direction -- "A = 1 => B = 1, Y = 0, d = (n-3)!" -- was
exactly of that shape.

Chasing the witnesses turned up a second, larger error.  `IN5` ("B >= comps")
rests on "every weight-2 jump is delta".  It is not.  From a permutation u the
weight-2 successors are *two*:

    delta(u) = u[2:] + u[1] + u[0]        and        sigma^2(u) = u[2:] + u[0] + u[1]

`build.comps` follows only delta, so a block that takes a sigma^2 jump spans two
delta-components and **B < comps**.  Witnesses below at n = 6 and n = 7,
confirmed by `blockcount`/`dirty` on the re-parsed string.

The sigma^2 jump is not always available: sigma(u) must already be covered, and
since the arcs of a class tile its ring that forces

    SIG2:  a sigma^2 jump out of arc i requires the arc at sigma(end_i) to have
           LENGTH 1.  In particular no sigma^2 jump leaves a full arc.

Measured: **0 sigma^2 jumps in all 44,564 corpus strings**, though length-1 arcs
are present at n = 5, 6, 7.  So `B >= comps` is true of optima and false of
walks -- [MEAS], not [THM].

Usage:
  python3 code/inflate.py
  python3 code/inflate.py --src data/n7/5908-egan.txt --n 7
  python3 code/inflate.py --corpus        # count sigma^2 jumps over all strings
"""

import argparse
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from build import _arc_end, canonical, coords, design_of, to_string  # noqa: E402
from gen2 import Gen                                                 # noqa: E402
from permgraph import (is_superpermutation, string_to_path,          # noqa: E402
                       weight)
from superstruct import Struct                                       # noqa: E402

FREE = ["R", "S", "v", "d", "A", "comps", "m", "mu_max", "n_partial"]
DEPENDENT = ["B", "Y", "T", "clean", "dirty", "N", "length"]

KEYS = ["length", "T", "S", "A", "B", "Y", "d", "v", "comps"]

EGAN6 = "/home/lk/superperm-upstream/superpermutations/6/873-egan.txt"


def load_design(path, n):
    digits = [int(c) for c in open(path).read() if c.isdigit()]
    return design_of(string_to_path(digits, n))


def arcs_from_starts(K, st, n):
    """The arcs a set of starts induces: segments between consecutive members.

    Each rotation class is a cyclic ring of n permutations; the arcs covering it
    run from one member of K to the next.  This is the inverse of taking arc
    starts, and it is what makes `A` and `comps` functions of K alone.
    """
    out = []
    for g in K:
        x, ln = st.sig(g), 1
        while x not in K and ln < n:
            x, ln = st.sig(x), ln + 1
        out.append((g, ln))
    return out


def ends_of(design, st):
    return [_arc_end(st, g, ln) for g, ln in design]


def sane(design, n, st):
    """The design is faithful: re-parsing its string returns the same arcs."""
    return canonical(design, n) == design


def sigma2_jumps(design, st):
    """Indices i where arc i -> arc i+1 is the sigma^2 weight-2 jump, not delta."""
    E = ends_of(design, st)
    return [i for i in range(len(design) - 1)
            if weight(E[i], design[i + 1][0]) == 2
            and design[i + 1][0] == st.sig(st.sig(E[i]))]


def check_sig2_rule(design, st):
    """SIG2: every sigma^2 jump has a length-1 arc sitting at sigma(end)."""
    E = ends_of(design, st)
    by_start = {a[0]: a[1] for a in design}
    for i in sigma2_jumps(design, st):
        if by_start.get(st.sig(E[i])) != 1:
            return False
    return True


# ---------------------------------------------------------------------------
# witness 1 -- reorder the arcs, keep the arc set
# ---------------------------------------------------------------------------

def rotate_witness(design, n, k):
    des = canonical(design[k:] + design[:k], n)
    c = coords(des, n)
    c["valid"] = is_superpermutation(to_string(des, n), n)
    return c


# ---------------------------------------------------------------------------
# witness 2 -- enlarge the arc set, keep A
# ---------------------------------------------------------------------------

def loop_witness(design, n, st, g, lid):
    """Union an unentered 2-loop into K, then chain the result into a walk.

    v rises by 1 and R by n-1, so A = (n-1)v - R is UNCHANGED.  The delta-graph
    is not: the new arcs cut classes that were covered once, and the components
    they belonged to fall apart.  Returns None when the chainer produces a
    design that re-parses to different arcs, since that would silently change
    the very arc set under test.
    """
    K = {a[0] for a in design} | set(st.loop_gens[lid])
    arcs = arcs_from_starts(K, st, n)
    comps, ends = g.components(arcs)
    _, order, rots = g.chain(arcs, comps, ends)
    des = g.design(arcs, comps, order, rots)
    if not sane(des, n, st):
        return None
    c = coords(des, n)
    c["valid"] = is_superpermutation(to_string(des, n), n)
    c["sigma2"] = len(sigma2_jumps(des, st))
    c["sig2rule"] = check_sig2_rule(des, st)
    c["lid"] = lid
    return c


# ---------------------------------------------------------------------------
# the classification
# ---------------------------------------------------------------------------

def classify(design, n, st, trials, seed=0):
    """Permute the arc list; report which coordinates ever move."""
    rng = random.Random(seed)
    ref = coords(design, n)
    moved, tried = set(), 0
    while tried < trials:
        perm = list(design)
        rng.shuffle(perm)
        if not sane(perm, n, st):
            continue                      # would merge arcs, changing the SET
        tried += 1
        c = coords(perm, n)
        moved |= {k for k in FREE + DEPENDENT if c.get(k) != ref.get(k)}
    return ref, moved, tried


# ---------------------------------------------------------------------------
# corpus scan
# ---------------------------------------------------------------------------

def corpus_sigma2():
    """How many real strings take a sigma^2 jump, and how many have a len-1 arc."""
    import math

    import census
    import champions6
    cache, tot, took, has1 = {}, 0, 0, 0

    def scan(n, des):
        nonlocal tot, took, has1
        st = cache.setdefault(n, Struct(n))
        tot += 1
        took += bool(sigma2_jumps(des, st))
        has1 += any(ln == 1 for _, ln in des)

    for n, _, path in census.sources(9):
        for digits in census.read_strings(path):
            if not digits or max(digits) != n or min(digits) != 1:
                continue
            p = string_to_path(digits, n)
            if len(p) != math.factorial(n):
                continue
            scan(n, design_of(p))
    for _, digits in champions6.strings():
        scan(6, design_of(string_to_path(digits, 6)))
    return tot, took, has1


# ---------------------------------------------------------------------------

def show(tag, c):
    extra = ""
    if "sigma2" in c:
        extra = f"  sigma2={c['sigma2']}"
    print(f"  {tag:<12} " + "  ".join(f"{q}={c[q]}" for q in KEYS)
          + f"  valid={c['valid']}{extra}")


def run_source(src, n, trials):
    st = Struct(n)
    design = load_design(src, n)
    ref = coords(design, n)
    print(f"\n=== source: {os.path.basename(src)} ===")
    print("  " + "  ".join(f"{k}={ref[k]}" for k in KEYS))

    print("\n  -- witness 1: same arc set, rotated order --")
    for k in (100, 200, 431):
        if k >= len(design):
            continue
        c = rotate_witness(design, n, k)
        assert c["valid"], f"rotation by {k} is not a superpermutation"
        assert (c["A"], c["S"], c["v"]) == (ref["A"], ref["S"], ref["v"])
        show(f"rot {k}", c)
    print(f"     => A = {ref['A']} with B = 2 is a REAL superpermutation, so "
          f"'A = 1 => B = 1' is false")

    print("\n  -- witness 2: A unchanged, arc set enlarged --")
    g = Gen(n)
    entered = {st.loop_of[a[0]] for a in design}
    free = [l for l in range(len(st.loop_gens)) if l not in entered]
    shown, in5 = 0, None
    for lid in free:
        c = loop_witness(design, n, st, g, lid)
        if c is None:
            continue
        assert c["valid"], f"loop {lid} witness is not a superpermutation"
        assert c["A"] == ref["A"], (c["A"], ref["A"])
        assert c["sig2rule"], f"loop {lid}: a sigma^2 jump without a len-1 arc"
        if c["B"] < c["comps"] and in5 is None:
            in5 = c
        if shown < 3:
            show(f"+loop {lid}", c)
            shown += 1
        if shown >= 3 and in5 is not None:
            break
    assert shown, "no enlarged arc set survived the faithfulness check"
    print(f"     => A = {ref['A']} with comps > 1 and d = {ref['d'] + 1}, so "
          f"'A = 1 => comps = 1' and 'A = 1 => d = (n-3)!' are false too")

    if in5 is not None:
        print(f"\n  -- witness 3: IN5 (B >= comps) refuted --")
        show(f"+loop {in5['lid']}", in5)
        print(f"     B = {in5['B']} < comps = {in5['comps']}, using "
              f"{in5['sigma2']} sigma^2 jump(s); SIG2 rule holds "
              f"(each sits at a length-1 arc)")
    return design, st, ref


def main(sources, trials, do_corpus):
    for src, n in sources:
        if not os.path.exists(src):
            print(f"\n=== {src} missing -- skipped ===")
            continue
        design, st, _ = run_source(src, n, trials)

    print(f"\n=== classification: {trials} arc permutations ===")
    _, moved, tried = classify(design, st.n, st, trials)
    print(f"  ordering-free (never moved): "
          f"{', '.join(k for k in FREE if k not in moved)}")
    print(f"  ordering-dependent (moved):  "
          f"{', '.join(k for k in DEPENDENT if k in moved)}")
    bad_free = [k for k in FREE if k in moved]
    bad_dep = [k for k in DEPENDENT if k not in moved]
    assert not bad_free, f"claimed ordering-free but moved: {bad_free}"
    assert not bad_dep, f"claimed ordering-dependent but never moved: {bad_dep}"
    print(f"  partition holds over {tried} permutations")

    if do_corpus:
        print("\n=== corpus scan ===")
        tot, took, has1 = corpus_sigma2()
        print(f"  {tot} strings: {took} take a sigma^2 jump, "
              f"{has1} contain a length-1 arc")
        print("  => the move is AVAILABLE in real strings and never TAKEN, so "
              "'B >= comps' is a fact about optima, not a theorem about walks")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=None)
    ap.add_argument("--n", type=int, default=7)
    ap.add_argument("--trials", type=int, default=40)
    ap.add_argument("--corpus", action="store_true")
    args = ap.parse_args()
    srcs = ([(args.src, args.n)] if args.src
            else [(EGAN6, 6), ("data/n7/5908-egan.txt", 7)])
    print(__doc__.split("Usage:")[0].strip())
    sys.exit(main(srcs, args.trials, args.corpus))
