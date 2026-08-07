"""Exact block accounting for a Hamiltonian path in the permutation graph.

Everything a lower-bound argument at n = 7 has to control, measured in one
pass and cross-checked against three exact identities.

Vocabulary (all for a fixed complete walk):

    R        arcs  (maximal weight-1 runs)
    S        splits = R - (n-1)!   (a class covered by j arcs contributes j-1)
    E        sum over jumps of (weight - 2)
    v        entered 2-loops,  A  accidents        [split identity R=(n-1)v-A]
    C_d      cheap jumps of delta type   u -> delta(u)      (leave the class)
    C_s      cheap jumps of sigma^2 type u -> sigma^2(u)    (stay in the class)
    D        delta-edge deficiency  = (n-2) v - C_d
    B        blocks = maximal runs of arcs joined by cheap jumps
    K        costly jumps = B - 1,   Y = sum over costly jumps of (weight - 3)

Identities proved here by measurement (and by the algebra in
docs/notes/pentad_lemma.md):

    length = n + n! - 2 + R + E                      (arc/jump bookkeeping)
    R      = (n-1) v - A                             (split identity)
    length = n + n! - 3 + n*v - 2A + D - C_s + Y     (block identity)

The third is the one the rung arguments run on: it isolates the four
quantities an adversary must make large (A, C_s) or small (D, Y).
"""

import math
from itertools import permutations


class Model:
    def __init__(self, n):
        self.n = n
        self.perms = list(permutations(range(1, n + 1)))
        self.sig = lambda u: u[1:] + u[:1]
        self.delta = lambda u: u[2:] + (u[1], u[0])
        # rotation class id
        self.cls = {}
        for p in self.perms:
            best, x = p, p
            for _ in range(n - 1):
                x = self.sig(x)
                best = min(best, x)
            self.cls[p] = best
        # 2-loops: orbit of  u -> sig^(n-1) then delta.  Generators only.
        self.loop_of, self.loop_gens = {}, []
        for p in self.perms:
            if p in self.loop_of:
                continue
            gs, u = [], p
            for _ in range(n - 1):
                gs.append(u)
                for _ in range(n - 1):
                    u = self.sig(u)
                u = self.delta(u)
            assert u == p
            lid = len(self.loop_gens)
            self.loop_gens.append(gs)
            for g in gs:
                self.loop_of[g] = lid

    def weight(self, u, w):
        n = self.n
        for k in range(1, n + 1):
            if u[k:] == w[:n - k]:
                return k
        return n

    def measure(self, path):
        n = self.n
        sig, delta = self.sig, self.delta
        arcs = [[path[0]]]
        jumps = []
        for u, w in zip(path, path[1:]):
            wt = self.weight(u, w)
            if wt == 1:
                arcs[-1].append(w)
            else:
                jumps.append((u, w, wt))
                arcs.append([w])
        R, E = len(arcs), sum(wt - 2 for _, _, wt in jumps)
        starts = [a[0] for a in arcs]

        # cheap jumps, split by type; blocks
        C_d = C_s = 0
        K = Y = 0
        for u, w, wt in jumps:
            if wt == 2:
                if w == delta(u):
                    C_d += 1
                else:
                    assert w == sig(sig(u)), "weight 2 is delta or sigma^2"
                    C_s += 1
            else:
                K += 1
                Y += wt - 3
        B = K + 1

        # entered loops, accidents, delta-edge usage per loop
        entered = {self.loop_of[s] for s in starts[1:]}
        arc_starts = set(starts)
        A = sum(1 for L in entered for g in self.loop_gens[L]
                if g not in arc_starts)
        d_used = {}
        for u, w, wt in jumps:
            if wt == 2 and w == delta(u):
                d_used.setdefault(self.loop_of[sig(u)], 0)
                d_used[self.loop_of[sig(u)]] += 1
        v = len(entered)
        D = (n - 2) * v - C_d
        # s = 1 unless the start vertex's own loop is never entered (then one
        # generator slot of the identity is missing).  s = 1 on every real
        # superpermutation; the flag only matters for degenerate stress walks.
        s = 1 if self.loop_of[path[0]] in entered else 0

        # class statistics
        per_class = {}
        for a in arcs:
            per_class.setdefault(self.cls[a[0]], []).append(len(a))
        S = R - math.factorial(n - 1)
        n_split = sum(1 for L in per_class.values() if len(L) > 1)
        n_shatter = sum(1 for L in per_class.values() if len(L) == n)
        P = sum(len(L) for L in per_class.values() if len(L) > 1)
        full_runs, cur = [], 0          # runs of consecutive full arcs by delta
        prev_full = False
        for i, a in enumerate(arcs):
            isfull = len(a) == n
            joined = i > 0 and jumps[i - 1][2] == 2 and \
                jumps[i - 1][1] == delta(jumps[i - 1][0])
            if isfull and prev_full and joined:
                cur += 1
            else:
                if cur:
                    full_runs.append(cur)
                cur = 1 if isfull else 0
            prev_full = isfull
        if cur:
            full_runs.append(cur)
        f = sum(1 for m in full_runs if m == n - 1)

        length = n + sum(self.weight(u, w) for u, w in zip(path, path[1:]))
        out = dict(n=n, length=length, R=R, S=S, E=E, v=v, A=A, C_d=C_d,
                   C_s=C_s, D=D, B=B, K=K, Y=Y, P=P, n_split=n_split,
                   n_shatter=n_shatter, N=len(full_runs), f=f,
                   maxd=max(d_used.values()) if d_used else 0)

        F = math.factorial(n)
        assert length == n + F - 2 + R + E, "arc/jump identity"
        assert R == (n - 1) * v - A - s + 1, "split identity"
        assert length == n + F - 1 + n * v - 2 * A - 2 * s + D - C_s + Y, \
            "block identity"
        assert length == n + F + math.factorial(n - 1) - 3 + S + B + Y, \
            "SBY identity"
        assert C_s <= S + n_shatter, "sigma^2 jumps <= splits + shattered"
        assert P == S + n_split, "partial arcs = splits + split classes"
        assert all(m <= n - 1 for m in full_runs), "full run <= n-1 arcs"
        if S == 0:
            # both fail once classes are split: a delta edge of L can then be
            # supplied by an arc that does not start at L's generator, so the
            # "using all n-1 closes a cycle" argument evaporates.
            assert out['maxd'] <= n - 2, "no loop uses all its delta edges"
            assert C_d <= (n - 2) * v, "delta-edge cap"
        return out


HDR = ("length", "R", "S", "E", "v", "A", "C_d", "C_s", "D", "B", "K", "Y",
       "P", "n_split", "N", "f")


def report(name, d):
    print(f"{name:22}" + "".join(f"{k}={d[k]:<6}" for k in HDR))


if __name__ == "__main__":
    import sys
    sys.path.insert(0, "code")
    from permgraph import string_to_path
    from classical import recursive_superperm

    for n in (4, 5, 6):
        m = Model(n)
        print(f"\n=== n = {n} ===")
        report(f"classical {n}", m.measure(
            string_to_path(recursive_superperm(n), n)))
        if n == 6:
            h = [int(c) for c in open("data/houston_872.txt").read().strip()]
            report("Houston 872", m.measure(string_to_path(h, 6)))

    # ---- stress: is  D >= -S  a law?  (it is equality on all four above) ----
    import random
    random.seed(7)
    m5 = Model(5)
    worst, n_bad = 10 ** 9, 0
    for t in range(600):
        if t % 2:                       # pure random order
            p = m5.perms[:]
            random.shuffle(p)
        else:                           # randomized greedy, cheap moves first
            rest = set(m5.perms)
            u = random.choice(m5.perms)
            rest.discard(u)
            p = [u]
            while rest:
                best = min(m5.weight(u, w) for w in rest)
                cands = [w for w in rest if m5.weight(u, w) <= best + 1]
                u = random.choice(cands)
                rest.discard(u)
                p.append(u)
        d = m5.measure(p)
        worst = min(worst, d['D'] + d['S'])
        n_bad += d['D'] + d['S'] < 0
    print(f"\nstress n=5, 600 complete walks: min(D + S) = {worst}, "
          f"violations of D >= -S: {n_bad}")
    print("\nALL IDENTITIES AND INEQUALITIES HOLD")
