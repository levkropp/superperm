"""Walk builder: turn a DESIGN into a superpermutation, and back.

Nothing in this repo built a walk before -- every other program either proves a
bound or measures a string someone else produced.  This is the missing half.

THE DESIGN.  A walk is a sequence of arcs, and an arc is fully described by
where it starts and how long it runs:

    design = [(start_permutation, arc_length), ...]      1 <= length <= n

Everything else is forced.  Inside an arc every step is sigma (weight 1).
Between arc i and arc i+1 the jump weight is whatever the overlap graph says,
so blocks, clean runs, dirty jumps, splits and accidents are all READ OFF the
design rather than chosen.  That is what makes it the right handle for search:
the only free variables are which arcs, in which order.

    build(design)      -> path            expand arcs into permutations
    design_of(path)    -> design          the inverse
    coords(design)     -> ledger vector   computed independently of blockcount

`coords` deliberately re-derives R, S, v, A, B, Y, clean, dirty, N from the
design alone, using `superstruct` rather than `blockcount`/`dirty`.  The gate
below then cross-checks it against those verified modules on every string in
the census -- two independent implementations agreeing on ~190 real strings.

Usage:
  python3 code/build.py                 # round-trip + coordinate gate
  python3 code/build.py --max-n 7       # skip the slow n = 8, 9 strings
"""

import argparse
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from blockcount import Model                                     # noqa: E402
from dirty import dissect                                        # noqa: E402
from permgraph import path_to_string, string_to_path, weight     # noqa: E402
from superstruct import Struct                                   # noqa: E402

_CACHE = {}


def struct(n):
    if n not in _CACHE:
        _CACHE[n] = Struct(n)
    return _CACHE[n]


# ---------------------------------------------------------------------------
# design <-> path
# ---------------------------------------------------------------------------

def build(design, n):
    """Expand [(start, length), ...] into the permutation path."""
    st = struct(n)
    path = []
    for start, ln in design:
        assert 1 <= ln <= n, ("arc length out of range", ln)
        x = start
        for _ in range(ln):
            path.append(x)
            x = st.sig(x)
    return path


def design_of(path):
    """Group a path into maximal sigma-runs: the inverse of `build`."""
    n = len(path[0])
    st = struct(n)
    design, start, ln = [], path[0], 1
    for u, w in zip(path, path[1:]):
        if w == st.sig(u):
            ln += 1
        else:
            design.append((start, ln))
            start, ln = w, 1
    design.append((start, ln))
    return design


def to_string(design, n):
    return path_to_string(build(design, n))


def canonical(design, n):
    """Merge any two arcs the ordering placed in sigma-succession.

    A search is free to put arc v immediately after arc u with
    v.start == sigma(u.end); that jump has weight 1, so the two are really one
    arc and R (hence S, hence T) was overcounted.  Re-deriving the design from
    the path merges them, which both fixes the bookkeeping and lowers T.
    """
    return design_of(build(design, n))


# ---------------------------------------------------------------------------
# ledger coordinates, computed from the design alone
# ---------------------------------------------------------------------------

def coords(design, n):
    st = struct(n)
    F1, F2 = math.factorial(n - 1), math.factorial(n - 2)

    R = len(design)
    S = R - F1
    starts = [d[0] for d in design]
    lens = [d[1] for d in design]

    entered = {st.loop_of[g] for g in starts}
    v = len(entered)
    A = (n - 1) * v - R                      # Split Identity

    ends = [st.comp(g, ()) if False else _arc_end(st, g, ln)
            for g, ln in design]

    B, Y, clean, dirty = 1, 0, 0, 0
    for i in range(len(design) - 1):
        w = weight(ends[i], starts[i + 1])
        assert w != 1, ("non-canonical design: consecutive arcs in sigma-"
                        "succession are one arc; call build.canonical first")
        if w >= 3:
            B += 1
            Y += w - 3
        elif w == 2:
            if lens[i] == n and starts[i + 1] == st.delta(ends[i]):
                clean += 1
            else:
                dirty += 1

    n_partial = sum(1 for ln in lens if ln < n)
    N = B + dirty
    T = S + B + Y

    # class multiplicities: how many arcs cover each rotation class
    mu = {}
    for g in starts:
        c = st.cls_id[g]
        mu[c] = mu.get(c, 0) + 1
    mu_max = max(mu.values())
    m = sum(1 for x in mu.values() if x >= 2)     # multiply-covered classes

    length = n + math.factorial(n) + math.factorial(n - 1) - 3 + T
    return dict(n=n, length=length, R=R, S=S, v=v, d=v - F2, A=A, B=B, Y=Y, T=T,
                clean=clean, dirty=dirty, n_partial=n_partial, N=N,
                BYA=B + Y - A, hpv_tight=(T == v),
                comps=comps(design, n), mu_max=mu_max, m=m)


def comps(design, n):
    """Components of the delta-graph on arcs -- an ORDERING-FREE quantity.

    Arc u -> arc v when v starts at delta(end u).  delta is injective and arc
    starts are distinct, so in- and out-degree are both <= 1: the graph is a
    disjoint union of paths and cycles, fixed by the arc SET alone.

    A block is ALMOST a path in it, but not quite: the weight-2 successors of u
    are delta(u) AND sigma^2(u), and only the first is followed here, so a block
    that takes a sigma^2 jump spans two components and `B >= comps` fails.  The
    repaired form is `B + sigma2 >= comps`.  For LOWER BOUNDS nothing is lost:
    the sigma^2 jump can always be exchanged away without lengthening the walk,
    so the minimum is attained where `T >= S + comps` does hold.  See
    `notes/ordering.md` and `code/sig2x.py`.
    """
    st = struct(n)
    start_ix = {a[0]: i for i, a in enumerate(design)}
    nxt = {}
    for i, (g, ln) in enumerate(design):
        t = st.delta(_arc_end(st, g, ln))
        if t in start_ix:
            nxt[i] = start_ix[t]
    heads = set(range(len(design))) - set(nxt.values())
    seen, c = set(), 0
    for i in list(heads) + list(range(len(design))):   # paths first, then cycles
        if i in seen:
            continue
        c += 1
        x = i
        while x is not None and x not in seen:
            seen.add(x)
            x = nxt.get(x)
    return c


def _arc_end(st, start, ln):
    x = start
    for _ in range(ln - 1):
        x = st.sig(x)
    return x


# ---------------------------------------------------------------------------
# gate
# ---------------------------------------------------------------------------

def check_one(n, digits, label):
    """Round trip and coordinate agreement for one string."""
    path = string_to_path(digits, n)
    design = design_of(path)

    # --- round trip ------------------------------------------------------
    assert build(design, n) == path, f"{label}: build o design_of != id"
    rebuilt = path_to_string(path)
    assert rebuilt == digits[:len(rebuilt)], f"{label}: string round trip"

    # --- independent coordinates vs blockcount / dirty -------------------
    c = coords(design, n)
    m = Model(n)
    core = m.measure(path)
    dis = dissect(m, path)
    for key, ref in (("R", core["R"]), ("S", core["S"]), ("v", core["v"]),
                     ("A", core["A"]), ("B", dis["B"]), ("Y", dis["Y"]),
                     ("clean", dis["clean"]), ("dirty", dis["dirty"]),
                     ("n_partial", dis["n_partial"]), ("N", dis["N"])):
        assert c[key] == ref, f"{label}: {key} {c[key]} != {ref}"
    assert c["T"] == (n - 1) * c["d"] + (c["B"] + c["Y"]) - c["A"], \
        f"{label}: master identity"
    return c


def gate(max_n):
    import census
    rows = census.sources(max_n)
    ok, seen_n = 0, {}
    for n, label, path in rows:
        digits = census.read_string(path)
        if digits is None:
            continue
        if max(digits) != n or min(digits) != 1:
            continue
        if len(string_to_path(digits, n)) != math.factorial(n):
            continue
        c = check_one(n, digits, label)
        ok += 1
        seen_n[n] = seen_n.get(n, 0) + 1
        if seen_n[n] <= 2:
            print(f"  {label:<42} R={c['R']:<7} v={c['v']:<6} d={c['d']:<5} "
                  f"B={c['B']:<6} Y={c['Y']:<4} T={c['T']:<6} OK", flush=True)
    print(f"\n  round trip + independent coordinates agree on {ok} strings "
          f"({', '.join(f'n={k}: {v}' for k, v in sorted(seen_n.items()))})")
    return ok


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-n", type=int, default=9)
    args = ap.parse_args()
    print(__doc__.split("Usage:")[0].strip())
    print("\n--- gate: design_of / build / coords against every known string ---")
    gate(args.max_n)
