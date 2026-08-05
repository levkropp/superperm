"""The family lens applied to the 7-symbol champions.

code/families6.py showed that the arc-to-arc delta step is right multiplication
by a, so a 2-loop is a coset g<a> and the n!/(n-1) loops fall into the n cosets
of H = <a,b>, the FAMILIES, each of which is an exact cover of the (n-1)!
rotation classes.  At n = 7 that is 840 loops = 7 families x 120.

Every known 5906 string has v = 142 and T = S + B + Y = 142 -- HPV is exactly
tight on all of them.  So the interesting question is not "how big is T" but
"what does HPV equality look like", and the family decomposition is a new
coordinate to ask that in.

For each string this reports, per family: how many of its 120 loops the walk
enters, how many arcs it takes from them, and how many rotation classes those
arcs cover.  Anything constant across all 136 champions is a candidate lemma.

Usage:  python3 code/n7_families.py [directory]
"""

import sys
from collections import Counter

sys.path.insert(0, "code")
from blockcount import Model                                    # noqa: E402
from permgraph import string_to_path                            # noqa: E402
from n7_champions import load, sources                          # noqa: E402

n = 7
ident = tuple(range(1, n + 1))
sig = lambda u: u[1:] + u[:1]
delta = lambda u: u[2:] + (u[1], u[0])
comp = lambda u, v: tuple(u[v[i] - 1] for i in range(n))
cid = lambda u: min(u[k:] + u[:k] for k in range(n))


def gens():
    a = ident
    for _ in range(n - 1):
        a = comp(a, sig(ident))
    a = comp(a, delta(ident))
    b = tuple(list(range(3, n)) + [2, 1, n])
    return a, b


def closure(gs):
    seen, fr = {ident}, [ident]
    while fr:
        x = fr.pop()
        for g in gs:
            y = comp(x, g)
            if y not in seen:
                seen.add(y)
                fr.append(y)
    return seen


def family_map():
    """perm -> family index, plus a check of the whole structure."""
    a, b = gens()
    H = closure((a, b))
    assert len(H) == 720, len(H)
    fid, fam = {}, {}
    import itertools
    for g in itertools.permutations(range(1, n + 1)):
        key = frozenset(comp(g, h) for h in H)
        if key not in fid:
            fid[key] = len(fid)
        fam[g] = fid[key]
    assert len(fid) == n, len(fid)
    # each family is an exact cover of the 720 classes
    seen = {f: set() for f in range(n)}
    for g, f in fam.items():
        seen[f].add(cid(g))
    for f in range(n):
        assert len(seen[f]) == 720, (f, len(seen[f]))
    return fam


def arcs_of(m, path):
    """Split the walk at weight >= 2 jumps; return the list of arcs."""
    arcs, cur = [], [path[0]]
    for u, w in zip(path, path[1:]):
        if m.weight(u, w) == 1:
            cur.append(w)
        else:
            arcs.append(cur)
            cur = [w]
    arcs.append(cur)
    return arcs


if __name__ == "__main__":
    print(__doc__.split("Usage:")[0].strip())
    strings = load(sources(sys.argv))
    print(f"\n{len(strings)} distinct 7-symbol strings")

    fam = family_map()
    print("family structure verified: 7 families, each an exact cover of 720 "
          "classes")

    m = Model(n)
    fam_of_loop = {}
    for lid, gs in enumerate(m.loop_gens):
        fs = {fam[g] for g in gs}
        assert len(fs) == 1, ("loop straddles families", lid)
        fam_of_loop[lid] = fs.pop()
    per_fam = Counter(fam_of_loop.values())
    print(f"loops: {len(m.loop_gens)},  per family: "
          f"{sorted(set(per_fam.values()))} (expect [(n-2)!] = [120])")

    rows, mult = [], {}
    for fn, digits in strings:
        path = string_to_path(digits, n)
        arcs = arcs_of(m, path)
        starts = [a[0] for a in arcs]
        loops = [m.loop_of[s] for s in starts]
        nloops = Counter()          # loops entered, per family
        narcs = Counter()           # arcs taken, per family
        ncls = {f: set() for f in range(n)}
        seen_loops = set()
        for s, L in zip(starts, loops):
            f = fam_of_loop[L]
            narcs[f] += 1
            if L not in seen_loops:
                seen_loops.add(L)
                nloops[f] += 1
        for a in arcs:
            f = fam_of_loop[m.loop_of[a[0]]]
            for u in a:
                ncls[f].add(cid(u))
        # COROLLARY OF THE COSET LEMMA, checked here: a family meets each class
        # exactly once, and the walk's arc starts are distinct permutations, so
        # two arcs whose starts share a family lie in DIFFERENT classes.  Hence
        # the arcs covering one class have pairwise distinct families, and a
        # class is covered by at most n arcs.
        by_class = {}
        for a in arcs:
            f = fam_of_loop[m.loop_of[a[0]]]
            by_class.setdefault(cid(a[0]), []).append(f)
        for c, fs in by_class.items():
            assert len(fs) == len(set(fs)), ("split inside one family", fn, c)
            assert len(fs) <= n
        mult[tuple(sorted(Counter(len(v) for v in by_class.values()).items()))] \
            = mult.get(tuple(sorted(Counter(len(v)
                       for v in by_class.values()).items())), 0) + 1

        length = n + sum(m.weight(u, w) for u, w in zip(path, path[1:]))
        # keep the per-family vectors ALIGNED by family index; sorting each
        # one separately would pair a family's loop count with a different
        # family's arc count.
        lp = [nloops.get(f, 0) for f in range(n)]
        ar = [narcs.get(f, 0) for f in range(n)]
        cl = [len(ncls[f]) for f in range(n)]
        rows.append((fn, length, len(seen_loops), lp, ar, cl))

    champs = [r for r in rows if r[1] == 5906]
    print(f"\n{len(champs)} champions at 5906; v distribution: "
          f"{dict(Counter(r[2] for r in champs))}")

    print("\nfamilies actually used (of 7), over the champions:")
    print("  ", dict(Counter(sum(1 for x in r[3] if x) for r in champs)))

    print("\nloops per family (sorted, descending) -- distinct patterns:")
    for pat, k in Counter(tuple(sorted(r[3], reverse=True))
                          for r in champs).most_common(12):
        print(f"   {str(pat):34} x{k}")

    print("\narcs per family -- distinct patterns:")
    for pat, k in Counter(tuple(sorted(r[4], reverse=True))
                          for r in champs).most_common(8):
        print(f"   {str(pat):40} x{k}")

    print("\nclasses covered per family -- distinct patterns:")
    for pat, k in Counter(tuple(sorted(r[5], reverse=True))
                          for r in champs).most_common(8):
        print(f"   {str(pat):40} x{k}")

    # ---- where do the accidents live? -----------------------------------
    # A = (n-1)v - R counts arc slots of entered loops that the walk did NOT
    # use.  It splits over families as A_f = (n-1)*loops_f - arcs_f >= 0, since
    # a family meets each class once so its arcs are in distinct classes.
    print("\naccidents A = (n-1)v - R, split over families:")
    conc = Counter()
    Avals = Counter()
    for fn, length, v, lp, ar, cl in rows:
        if length != 5906:
            continue
        Af = sorted((6 * l - a for l, a in zip(lp, ar)), reverse=True)
        A = sum(Af)
        Avals[A] += 1
        conc[sum(1 for x in Af if x > 0)] += 1
    print(f"  A over the champions      : {dict(Avals)}")
    print(f"  #families carrying A_f > 0: {dict(sorted(conc.items()))}")
    print("  (A_f > 0 in exactly one family means every OTHER family has all "
          "its\n   entered loops completely traversed)")

    print("\narcs per class (multiplicity k, count) -- forced: the k arcs on a")
    print("class lie in k DISTINCT families, so k <= n = 7.  Checked above.")
    for pat, k in sorted(mult.items(), key=lambda x: -x[1])[:6]:
        print(f"   {str(pat):46} x{k}")

    print("\nnon-champions, for contrast:")
    for r in sorted(rows, key=lambda r: r[1]):
        if r[1] != 5906:
            print(f"   {r[0][:34]:36} len {r[1]}  v={r[2]}  "
                  f"loops/fam {sorted(r[3], reverse=True)}  "
                  f"A/fam {sorted((6*l-a for l, a in zip(r[3], r[4])), reverse=True)}")
