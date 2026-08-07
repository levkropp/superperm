"""Case 3 of the A2 rescue lemma: what stops the chains escaping?

`A2RESCUE` (docs/notes/pbound.md 7d): a multiply-covered class C whose loops all have
`b_L = 1` must meet a delta-cycle or a dead exit.  581/581, no exceptions.
`A2PATH` [THM] discharges two of its three cases -- the mu paths `P_1..P_mu`
have in- and out-degree <= 1, so they form disjoint chains and cycles, and

    they close among themselves     -> a delta-cycle    -> done
    they chain, last exit is dead   -> a D token        -> done
    they all chain OUT of X, alive  -> OPEN

By `PATHTAIL` (comps = cyc + W + D) each `P_i` in the open case sits in a path
component whose single tail is a W or D arc, and that tail must lie OUTSIDE
X = {L_1..L_mu} or it would itself be a token for X.

This file instruments the 581 instances to find the invariant that forbids that:

  * is the rescuing cycle INSIDE X (the paths closing on each other) or does it
    run through arcs outside?
  * how many of X's loops does it touch, and how long is it?
  * in the 48 dead-exit rescues, which alpha_i dies?
  * how far does the chain leaving alpha_i travel before returning or dying?

Usage:
  python3 code/a2case3.py
"""

import argparse
import collections
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from build import _arc_end, design_of                            # noqa: E402
from gen2 import Gen                                             # noqa: E402
from permgraph import string_to_path                             # noqa: E402


def graph(g, arcs):
    """(nxt, loop, broken-count per loop, cycle arc set)."""
    st = g.st
    K = {a[0] for a in arcs}
    ix = {a[0]: i for i, a in enumerate(arcs)}
    nxt = {}
    for i, (s, ln) in enumerate(arcs):
        t = st.delta(_arc_end(st, s, ln))
        if t in ix:
            nxt[i] = ix[t]
    loop = [st.loop_of[a[0]] for a in arcs]
    b = collections.Counter()
    for i, (s, ln) in enumerate(arcs):
        if ln < g.n or st.comp(s, st.a) not in K:
            b[loop[i]] += 1
    heads = set(range(len(arcs))) - set(nxt.values())
    seen, cycarcs = set(), set()
    for i in list(heads) + list(range(len(arcs))):
        if i in seen:
            continue
        run, x = [], i
        while x is not None and x not in seen:
            seen.add(x)
            run.append(x)
            x = nxt.get(x)
        if i not in heads:
            cycarcs |= set(run)
    return nxt, loop, b, cycarcs


def instances(g, arcs):
    """Every dangerous class: (class, its arc indices, its loops)."""
    st = g.st
    nxt, loop, b, cycarcs = graph(g, arcs)
    bycls = collections.defaultdict(list)
    for i, (s, ln) in enumerate(arcs):
        bycls[st.cls_id[s]].append(i)
    out = []
    for c, xs in bycls.items():
        if len(xs) < 2:
            continue
        Ls = [loop[i] for i in xs]
        if all(b.get(L, 0) == 1 for L in Ls):
            out.append((c, xs, Ls))
    return out, nxt, loop, b, cycarcs


def analyse(g, arcs):
    inst, nxt, loop, b, cycarcs = instances(g, arcs)
    rows = []
    for c, xs, Ls in inst:
        Xloops = set(Ls)
        Xarcs = {i for i in range(len(arcs)) if loop[i] in Xloops}
        # follow the chain out of each alpha_i
        hops, returns, dead = [], 0, 0
        for i in xs:
            x, k = nxt.get(i), 0
            while x is not None and k < 4 * len(arcs):
                k += 1
                if loop[x] in Xloops:
                    returns += 1
                    break
                x = nxt.get(x)
            else:
                if x is None:
                    dead += 1
            if x is None:
                dead += 1
            hops.append(k)
        oncyc = [L for L in Ls if any(loop[j] == L for j in cycarcs)]
        # is the cycle (if any) confined to X?
        cyc_in_X = None
        if oncyc:
            cyc_arcs_here = {j for j in cycarcs if loop[j] in Xloops}
            reach = set()
            for j in cyc_arcs_here:
                x, k = j, 0
                while x is not None and k <= len(arcs):
                    reach.add(x)
                    x = nxt.get(x)
                    k += 1
                    if x == j:
                        break
            cyc_in_X = all(loop[j] in Xloops for j in reach if j in cycarcs)
        rows.append(dict(mu=len(xs), on_cycle=len(oncyc), cyc_in_X=cyc_in_X,
                         returns=returns, dead=dead, hops=hops))
    return rows


def main():
    import census
    cache, all_rows = {}, []
    for n, label, path in census.sources(9):
        if n not in (6, 7):
            continue
        for digits in census.read_strings(path):
            if not digits or max(digits) != n or min(digits) != 1:
                continue
            p_ = string_to_path(digits, n)
            if len(p_) != math.factorial(n):
                continue
            g = cache.setdefault(n, Gen(n))
            arcs = [tuple(a) for a in design_of(p_)]
            all_rows += analyse(g, arcs)

    print(f"\n  {len(all_rows)} dangerous-class instances (expect 581)")
    print(f"  mu distribution: "
          f"{dict(sorted(collections.Counter(r['mu'] for r in all_rows).items()))}")
    print(f"  loops of X on a cycle: "
          f"{dict(sorted(collections.Counter(r['on_cycle'] for r in all_rows).items()))}")
    print(f"  cycle confined to X: "
          f"{dict(collections.Counter(str(r['cyc_in_X']) for r in all_rows))}")
    print(f"  chains that RETURN to X: "
          f"{dict(sorted(collections.Counter(r['returns'] for r in all_rows).items()))}")
    print(f"  chains that DIE: "
          f"{dict(sorted(collections.Counter(r['dead'] for r in all_rows).items()))}")
    hops = [h for r in all_rows for h in r['hops']]
    print(f"  hops before returning/dying: min {min(hops)} max {max(hops)} "
          f"mean {sum(hops)/len(hops):.1f}")
    esc = sum(1 for r in all_rows if r['returns'] == 0 and r['dead'] == 0)
    print(f"\n  instances where EVERY chain escapes X and none dies: {esc}")
    print("  (that is case 3; if it is 0 here, case 3 is empirically vacuous)")
    return 0


if __name__ == "__main__":
    argparse.ArgumentParser().parse_args()
    print(__doc__.split("Usage:")[0].strip())
    sys.exit(main())
