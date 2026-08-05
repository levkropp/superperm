"""Shared n-generic group and loop structure for the permutation overlap graph.

Seven files in this repo (`coset_lemma`, `rung124`, `exit_table`, `loop_runs`,
`after_traversal`, `chain_count`, `pentad_orbits`) each re-derive sigma, delta,
composition, `a`, `b` and `s` from scratch.  Those files carry verified results
and published rung values, so they are deliberately left alone; this module
exists for NEW code (the constructor) and asserts that it agrees with them.

Everything follows `notes/lemma_arsenal.md`:

  sigma(u) = u[1:] + u[:1]                rotation, order n
  delta(u) = u[2:] + (u[1], u[0])         arc-to-arc step
  a = c^(n-1) d                           order n-1, walks a 2-loop's generators
  b = om                                  the class-disjoint weight-3 exit
  s = a^(n-2) b                           order n-2, the Pentad element
  H = <a, b>                              order (n-1)!, index n -- the FAMILIES

  rotation class   n permutations,  (n-1)! of them
  2-loop           coset g<a>, n-1 generators (one per class), n!/(n-1) of them
  family           coset gH, (n-2)! loops, and an EXACT COVER of the classes
  <s>-orbit        n-2 loops, pairwise class-disjoint  (Pentad Lemma)

Usage:
  python3 code/superstruct.py           # self-check at n = 5, 6, 7
  python3 code/superstruct.py --n 8     # add n = 8
"""

import argparse
import math
from itertools import permutations


class Struct:
    """All of the above for one n, built once."""

    def __init__(self, n):
        self.n = n
        self.ident = tuple(range(1, n + 1))
        self.perms = list(permutations(range(1, n + 1)))
        self.index = {p: i for i, p in enumerate(self.perms)}

        self.a = self._mk_a()
        self.apow = [self.ident]
        for _ in range(n - 2):
            self.apow.append(self.comp(self.apow[-1], self.a))
        self.b = self._mk_b()
        self.s = self.comp(self.apow[n - 2], self.b)

        self._classes()
        self._loops()
        self._families()

    # ---- group operations -------------------------------------------------

    @staticmethod
    def sig(u):
        return u[1:] + u[:1]

    @staticmethod
    def delta(u):
        return u[2:] + (u[1], u[0])

    @staticmethod
    def comp(u, v):
        return tuple(u[v[i] - 1] for i in range(len(u)))

    @staticmethod
    def inv(u):
        w = [0] * len(u)
        for i, x in enumerate(u):
            w[x - 1] = i + 1
        return tuple(w)

    def order(self, u):
        k, x = 1, u
        while x != self.ident:
            x, k = self.comp(x, u), k + 1
        return k

    def onecycle(self, u):
        """Canonical representative of u's rotation class."""
        best, x = u, u
        for _ in range(self.n - 1):
            x = self.sig(x)
            if x < best:
                best = x
        return best

    def end_of(self, g):
        """Last permutation of the full arc starting at g."""
        u = g
        for _ in range(self.n - 1):
            u = self.sig(u)
        return u

    # ---- the distinguished elements ---------------------------------------

    def _mk_a(self):
        a = self.ident
        for _ in range(self.n - 1):
            a = self.comp(a, self.sig(self.ident))
        a = self.comp(a, self.delta(self.ident))
        assert self.order(a) == self.n - 1, "ord(a) = n-1"
        return a

    def exits(self, g, l):
        """The 3! weight-3 targets from a block of length l entered at g.

        Each is returned as (group element, cap) where cap is how far the next
        block can run before re-entering a class this block already burned.
        """
        n = self.n
        burned = {self.onecycle(self.comp(g, p)) for p in self.apow[:l]}
        last = self.comp(g, self.apow[l - 1])
        tail = self.end_of(last)
        out = []
        for p in permutations(tail[:3]):
            h = tail[3:] + p
            cap, x = 0, h
            while cap < n - 1 and self.onecycle(x) not in burned:
                cap, x = cap + 1, self.comp(x, self.a)
            out.append((self.comp(self.inv(last), h), cap))
        return out

    def _mk_b(self):
        """om: the unique weight-3 exit from a full block that burns nothing."""
        cands = [mu for mu, k in self.exits(self.ident, self.n - 1)
                 if k == self.n - 1]
        assert len(cands) == 1, "om is unique out of a complete traversal"
        return cands[0]

    # ---- classes, loops, families -----------------------------------------

    def _classes(self):
        self.cls_id, seen = {}, {}
        for p in self.perms:
            c = self.onecycle(p)
            if c not in seen:
                seen[c] = len(seen)
            self.cls_id[p] = seen[c]
        self.n_classes = len(seen)

    def _loops(self):
        """2-loops as cosets g<a>; loop_of[g] and loop_gens[lid]."""
        self.loop_of, self.loop_gens = {}, []
        for p in self.perms:
            if p in self.loop_of:
                continue
            gs, x = [], p
            for _ in range(self.n - 1):
                gs.append(x)
                x = self.comp(x, self.a)
            assert x == p, "the a-orbit closes after n-1 steps"
            lid = len(self.loop_gens)
            self.loop_gens.append(gs)
            for g in gs:
                self.loop_of[g] = lid
        self.n_loops = len(self.loop_gens)

    def _orbit_partition(self, gens):
        """Partition S_n into orbits of right multiplication by `gens`."""
        lab, out = {}, []
        for p in self.perms:
            if p in lab:
                continue
            k, stack, orb = len(out), [p], []
            lab[p] = k
            while stack:
                x = stack.pop()
                orb.append(x)
                for g in gens:
                    y = self.comp(x, g)
                    if y not in lab:
                        lab[y] = k
                        stack.append(y)
            out.append(orb)
        return lab, out

    def _families(self):
        """Cosets of H = <a, b>: the n families of loops."""
        self.fam_of_perm, cosets = self._orbit_partition([self.a, self.b])
        self.n_families = len(cosets)
        self.H_size = len(cosets[0])
        # a family as a set of loop ids
        self.fam_loops = [set() for _ in range(self.n_families)]
        for g, f in self.fam_of_perm.items():
            self.fam_loops[f].add(self.loop_of[g])
        self.fam_of_loop = {}
        for f, ls in enumerate(self.fam_loops):
            for lid in ls:
                self.fam_of_loop[lid] = f

    def s_orbits(self):
        """<s>-orbits of loops (Pentads): lists of n-2 loop ids."""
        seen, out = set(), []
        for g in self.perms:
            lid = self.loop_of[g]
            if lid in seen:
                continue
            orb, x = [], g
            for _ in range(self.n - 2):
                orb.append(self.loop_of[x])
                x = self.comp(x, self.s)
            if len(set(orb)) != self.n - 2:
                continue
            seen.update(orb)
            out.append(orb)
        return out

    def loop_classes(self, lid):
        return {self.cls_id[g] for g in self.loop_gens[lid]}


# ---------------------------------------------------------------------------

def selfcheck(n, verbose=True):
    """Every structural fact lemma_arsenal.md 3.3 / 3.5 asserts, re-derived."""
    st = Struct(n)
    F1, F2 = math.factorial(n - 1), math.factorial(n - 2)

    assert st.order(st.a) == n - 1, "ord(a) = n-1"
    assert st.order(st.s) == n - 2, "ord(s) = n-2 (Pentad element)"
    assert st.n_classes == F1, "(n-1)! rotation classes"
    assert st.n_loops == math.factorial(n) // (n - 1), "n!/(n-1) two-loops"
    assert st.H_size == F1, "|H| = (n-1)!"
    assert st.n_families == n, "H has index n"

    for lid in range(st.n_loops):
        assert len(st.loop_classes(lid)) == n - 1, "a loop meets n-1 classes"

    # each family is an exact cover of the (n-1)! classes
    for f in range(n):
        assert len(st.fam_loops[f]) == F2, "family holds (n-2)! loops"
        cov = []
        for lid in st.fam_loops[f]:
            cov.extend(st.loop_classes(lid))
        assert len(cov) == F1 and len(set(cov)) == F1, \
            "family is an exact cover of the classes"

    # Pentads: an <s>-orbit's loops are pairwise class-disjoint
    orbs = st.s_orbits()
    for orb in orbs:
        cov = []
        for lid in orb:
            cov.extend(st.loop_classes(lid))
        assert len(cov) == len(set(cov)) == (n - 1) * (n - 2), \
            "Pentad loops are pairwise class-disjoint"

    if verbose:
        print(f"  n = {n}:  a ord {st.order(st.a)},  s ord {st.order(st.s)},  "
              f"{st.n_classes} classes, {st.n_loops} loops, "
              f"{st.n_families} families x {F2}, "
              f"{len(orbs)} full <s>-orbits   ALL CHECKS PASS")
    return st


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=7,
                    help="highest n to self-check (default 7)")
    args = ap.parse_args()

    print(__doc__.split("Usage:")[0].strip())
    print("\n--- self-check against lemma_arsenal.md 3.3 / 3.5 ---")
    for n in range(5, args.n + 1):
        selfcheck(n)
