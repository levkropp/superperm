"""The free-join digraph, split into a forced core and an unforced fringe.

`CH1` was recorded as "the free-join graph has out-degree <= 1".  That is
measured, not true: `chainer.py` already notes that arc sets an annealer wanders
through reach out-degree 3.  Chasing it as a theorem would be chasing a
falsehood.

The provable statement is **length-gated**.  `Struct.exits(g, l)` returns the 3!
weight-3 targets of a block of `l` arcs, each with a **cap** -- how far the next
block can run before re-entering a class this one already burned -- and
`coset_lemma.py` verifies that exactly one target survives `cap >= l'` precisely
when `l + l' >= 2n-3`, and that the survivor is om.  So:

> **`FORCE`.**  A free join out of a block of `l` FULL arcs into a block of `l'`
> arcs has a unique admissible exit, necessarily om, whenever `l + l' >= 2n-3`.

Call an edge of the free-join digraph **core** when it satisfies that, and
**fringe** otherwise.  Two consequences, and the second is the point:

  * om is a single group element, so the core target of a state is the single
    permutation `end . b`, and distinct components have distinct arcs and hence
    distinct entries.  **Every state has at most ONE core out-edge** -- the
    correct, provable version of `CH1`.
  * therefore out-degree >= 2 forces at least one FRINGE edge, and a fringe edge
    needs a SHORT block at one end.  Short blocks come from partial arcs, and
    partial arcs are what splits are made of.  That is the mechanism by which a
    long free chain has to pay -- which is what `RES` was reaching for through
    residues, and residues go mixed at exactly the champions.

This file measures all of it and gates the "at most one core out-edge" claim.
It computes NO `p` values: nothing here needs the min-path-cover search, so
nothing here can be poisoned by its fallback.

Usage:
  python3 code/freejoin.py             # n = 5, 6, 7 census
  python3 code/freejoin.py --n 7       # one n
"""

import argparse
import collections
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import chainer                                                    # noqa: E402
from build import design_of                                       # noqa: E402
from gen2 import Gen                                              # noqa: E402
from permgraph import string_to_path                              # noqa: E402


def arc_order(run, k):
    """The arcs of a component, in the order the walk takes them at break k."""
    L = len(run)
    return [run[(k + j) % L] for j in range(L)]


def block_lengths(g, arcs, order):
    """(leading block length, trailing block length) in arcs, by loop identity.

    A full arc's delta-successor starts at `s.a`, the next generator of the SAME
    loop; a partial arc's starts in a different loop.  So a maximal run of
    consecutive arcs sharing a loop is exactly a block, and its length is what
    `Struct.exits` calls `l`.
    """
    lo = [g.st.loop_of[arcs[i][0]] for i in order]
    head = 1
    while head < len(lo) and lo[head] == lo[0]:
        head += 1
    tail = 1
    while tail < len(lo) and lo[-1 - tail] == lo[-1]:
        tail += 1
    return head, tail


def graph(g, arcs):
    """Every free edge, tagged core/fringe, plus per-state block lengths.

    Returns (edges, ldat, nstates) where
        edges[(i,k)] = [(j, k', core?), ...]
        ldat[(i,k)]  = (entry block l', exit block l, exit arc is full)
    """
    n = g.n
    comps, ends = g.components(arcs)
    opts = g.options(arcs, comps, ends)
    ldat = {}
    for i, run in enumerate(comps):
        for k in range(len(opts[i])):
            order = arc_order(run, opts[i][k][2])
            head, tail = block_lengths(g, arcs, order)
            ldat[(i, k)] = (head, tail, arcs[order[-1]][1] == n,
                            arcs[order[-1]][0])
    succ = chainer.free_succ(opts)
    edges = {}
    for s, hits in succ.items():
        _, l, full, _ = ldat[s]
        out = []
        for t in hits:
            lp = ldat[t][0]
            out.append((t[0], t[1], bool(full and l + lp >= 2 * n - 3)))
        edges[s] = out
    return edges, ldat, sum(len(o) for o in opts)


def om_target(g, ldat, s):
    """Where the om exit of state `s` lands.

    `Struct.exits` returns each target as `inv(last) . h` with `last` the block's
    last ARC START -- not its end -- so the om target is `start . b`, and using
    the end instead is simply the wrong group element.
    """
    return g.st.comp(ldat[s][3], g.st.b)


def measure(g, arcs):
    """Counts for one arc set."""
    n = g.n
    comps, ends = g.components(arcs)
    opts = g.options(arcs, comps, ends)
    edges, ldat, nstates = graph(g, arcs)
    outdeg = collections.Counter()
    coredeg = collections.Counter()
    ncore = nfringe = 0
    bad = []
    for s in ldat:
        es = edges.get(s, [])
        outdeg[len(es)] += 1
        c = sum(1 for e in es if e[2])
        coredeg[c] += 1
        ncore += c
        nfringe += len(es) - c
        if c > 1:
            bad.append(s)
        # a core edge must land exactly on the om target
        if c == 1:
            tgt = om_target(g, ldat, s)
            j, k, _ = [e for e in es if e[2]][0]
            if opts[j][k][0] != tgt:
                bad.append(('om', s, opts[j][k][0], tgt))
    return dict(outdeg=outdeg, coredeg=coredeg, ncore=ncore, nfringe=nfringe,
                nstates=nstates, comps=len(comps), bad=bad)


def chain_law(g, arcs, cap=400_000):
    """L(f) = longest free chain, in components, using exactly f fringe edges.

    Core edges alone are a function (FORCE), so a core-only chain is a walk in a
    functional graph and must close or die; the interesting quantity is how much
    LONGER a chain gets per fringe edge bought.  If that is sublinear, then a
    chain over k components needs many fringe edges, fringe edges need short
    blocks, and short blocks need splits -- the v-to-p bridge.
    """
    edges, ldat, _ = graph(g, arcs)
    best = collections.Counter()
    nodes = 0
    for s0 in ldat:
        stack = [(s0, frozenset([s0[0]]), 0)]
        while stack:
            s, seen, f = stack.pop()
            nodes += 1
            if nodes > cap:
                return best, False
            if len(seen) > best[f]:
                best[f] = len(seen)
            for (j, k, core) in edges.get(s, ()):
                if j not in seen:
                    stack.append(((j, k), seen | {j}, f + (0 if core else 1)))
    return best, True


def relaxed_p(g, arcs, cap=300_000):
    """Min path cover of the COMPONENT graph, ignoring break-point consistency.

    A state is (component, break-point) and the break point fixes the entry AND
    the exit together.  Drop that coupling -- keep only "some break of i can
    free-join to some break of j" -- and the problem becomes an ordinary min
    path cover on `comps` nodes.  The gap between this and the exact `p` is
    exactly what the coupling costs.

    That gap is the whole question.  `pbound.md` 3b already found that the
    matching relaxation for `p` is useless because it "discards exactly the
    state-consistency coupling"; this measures how much that coupling is
    actually carrying.
    """
    edges, ldat, _ = graph(g, arcs)
    comps, _ = g.components(arcs)
    N = len(comps)
    cg = collections.defaultdict(set)
    for s, es in edges.items():
        for (j, _k, _c) in es:
            cg[s[0]].add(j)
    best = [N + 1]
    nodes = [0]

    def dfs(cur, seen, chains):
        if chains >= best[0]:
            return
        nodes[0] += 1
        if nodes[0] > cap:
            raise TimeoutError
        if len(seen) == N:
            best[0] = chains
            return
        ext = [j for j in cg.get(cur, ()) if j not in seen]
        for j in ext:
            dfs(j, seen | {j}, chains)
        if not ext:
            for j in range(N):
                if j not in seen:
                    dfs(j, seen | {j}, chains + 1)
                    break

    try:
        for s0 in range(N):
            dfs(s0, frozenset([s0]), 1)
            if best[0] == 1:
                break
    except TimeoutError:
        return None
    return best[0]


def main_relax(ns, limit=None):
    import census
    import pbound
    cache, rows = {}, collections.defaultdict(list)
    for n, label, path in census.sources(9):
        if n not in ns:
            continue
        for digits in census.read_strings(path):
            if not digits or max(digits) != n or min(digits) != 1:
                continue
            p_ = string_to_path(digits, n)
            if len(p_) != math.factorial(n):
                continue
            g = cache.setdefault(n, Gen(n))
            arcs = [tuple(a) for a in design_of(p_)]
            rp = relaxed_p(g, arcs)
            if rp is None:
                continue
            b, S, C, p = pbound.value(g, arcs)
            if not pbound.value.exact:
                continue
            v = len({g.st.loop_of[a[0]] for a in arcs})
            rows[n].append((v, C, rp, p))
            if limit and len(rows[n]) >= limit:
                break
    for n in sorted(rows):
        rs = rows[n]
        gap = collections.Counter(p - rp for _v, _C, rp, p in rs)
        rpd = collections.Counter(rp for _v, _C, rp, _p in rs)
        print(f"\n  n = {n}: {len(rs)} strings with both values exact")
        print(f"    relaxed p (no coupling):  {dict(sorted(rpd.items()))}")
        print(f"    exact p - relaxed p:      {dict(sorted(gap.items()))}")
        byv = collections.defaultdict(lambda: [99, 99])
        for v, _C, rp, p in rs:
            byv[v][0] = min(byv[v][0], rp)
            byv[v][1] = min(byv[v][1], p)
        print("    v -> (min relaxed p, min exact p):")
        print("      " + "  ".join(f"{v}:({a},{b})"
                                   for v, (a, b) in sorted(byv.items())))
    return 0


def main_chains(ns):
    import census
    cache, agg = {}, collections.defaultdict(collections.Counter)
    part = collections.Counter()
    for n, label, path in census.sources(9):
        if n not in ns:
            continue
        for digits in census.read_strings(path):
            if not digits or max(digits) != n or min(digits) != 1:
                continue
            p_ = string_to_path(digits, n)
            if len(p_) != math.factorial(n):
                continue
            g = cache.setdefault(n, Gen(n))
            law, done = chain_law(g, [tuple(a) for a in design_of(p_)])
            if not done:
                part[n] += 1
                continue
            for f, L in law.items():
                agg[n][f] = max(agg[n][f], L)
    for n in sorted(agg):
        print(f"\n  n = {n}   (partial, node-capped: {part[n]} strings)")
        print("    f (fringe edges) -> longest chain in components:")
        cells = [f"{f}:{L}" for f, L in sorted(agg[n].items())]
        for i in range(0, len(cells), 9):
            print("      " + "  ".join(cells[i:i + 9]))
        z = agg[n].get(0, 0)
        print(f"    core-only chains (f = 0) reach {z} components; "
              f"ord(s) = n-2 = {n - 2}")
    return 0


def main(ns):
    import census
    cache = {}
    agg = {}
    for n in ns:
        agg[n] = dict(outdeg=collections.Counter(),
                      coredeg=collections.Counter(),
                      ncore=0, nfringe=0, strings=0, bad=0, badwit=None)
    for n, label, path in census.sources(9):
        if n not in ns:
            continue
        for digits in census.read_strings(path):
            if not digits or max(digits) != n or min(digits) != 1:
                continue
            p_ = string_to_path(digits, n)
            if len(p_) != math.factorial(n):
                continue
            g = cache.setdefault(n, Gen(n))
            m = measure(g, [tuple(a) for a in design_of(p_)])
            a = agg[n]
            a['outdeg'] += m['outdeg']
            a['coredeg'] += m['coredeg']
            a['ncore'] += m['ncore']
            a['nfringe'] += m['nfringe']
            a['strings'] += 1
            if m['bad']:
                a['bad'] += 1
                a['badwit'] = a['badwit'] or (label, m['bad'][:2])

    fail = 0
    for n in sorted(agg):
        a = agg[n]
        if not a['strings']:
            continue
        print(f"\n  n = {n}: {a['strings']} strings")
        print(f"    free out-degree:      "
              f"{dict(sorted(a['outdeg'].items()))}")
        print(f"    CORE out-degree:      "
              f"{dict(sorted(a['coredeg'].items()))}")
        print(f"    edges: {a['ncore']} core, {a['nfringe']} fringe "
              f"({100 * a['ncore'] / max(1, a['ncore'] + a['nfringe']):.1f}% core)")
        hi = max(a['outdeg'])
        print(f"    max free out-degree {hi}; max CORE out-degree "
              f"{max(a['coredeg'])}")
        if a['bad']:
            fail += 1
            print(f"    *** {a['bad']} strings VIOLATE 'at most one core "
                  f"out-edge, landing on om': {a['badwit']}")
        else:
            print(f"    FORCE gate: every state has <= 1 core out-edge and it "
                  f"lands on end.b   OK")
    if fail:
        print("\n  FORCE VIOLATED -- the lemma is wrong as stated")
        return 1
    print("\n  FORCE holds on every string measured")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, action="append")
    ap.add_argument("--chains", action="store_true")
    ap.add_argument("--relax", action="store_true")
    args = ap.parse_args()
    print(__doc__.split("Usage:")[0].strip())
    ns = args.n or [5, 6, 7]
    if args.relax:
        sys.exit(main_relax(ns))
    sys.exit(main_chains(ns) if args.chains else main(ns))
