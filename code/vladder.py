"""The v-ladder: the exact statement a lower-bound proof has to discharge.

For a complete Hamiltonian path in the n-symbol overlap graph write
    R      = arcs (maximal weight-1 runs)
    E      = sum over jumps of (weight - 2)
    v      = entered 2-loops
    A      = accidents (generators of entered loops covered mid-arc)
    splits = R - (n-1)!

Identities (exact, not bounds):
    length = n + wt,  wt = n! + (n-1)! - 2 + splits + E
    R = (n-1)v - A                                   [split identity]
    => length = n + n! - 2 + (n-1)v - A + E

HPV bound:  wt >= n! + ((n-1)!-1) + v - 2,  i.e. length >= LB0(n) + v.
So a string of length L has  v <= L - LB0(n)  -- an UPPER bound on v.
Since covering forces v >= (n-2)!, proving length >= L+1 means discharging
every v in [(n-2)!, L - LB0(n)]: the ladder.
"""

from itertools import permutations


class Model:
    def __init__(self, n):
        self.n = n
        self.perms = list(permutations(range(1, n + 1)))
        sig = lambda u: u[1:] + u[:1]
        delta = lambda u: u[2:] + (u[1], u[0])
        self.sig, self.delta = sig, delta
        lids, gen_of = {}, {}
        for pi in self.perms:
            seen, u = set(), pi
            while u not in seen:
                seen.add(u)
                for _ in range(n - 1):
                    u = sig(u)
                    seen.add(u)
                u = delta(u)
            L = frozenset(seen)
            lids.setdefault(L, len(lids))
            gen_of[pi] = lids[L]
        self.gen_of = gen_of
        self.nloops = len(lids)
        # loop -> its generators
        self.gens = {}
        for pi in self.perms:
            self.gens.setdefault(gen_of[pi], set()).add(pi)

    def weight(self, u, v):
        n = self.n
        if u == v:
            return 0
        for k in range(n - 1, 0, -1):
            if u[n - k:] == v[:k]:
                return n - k
        return n

    def lb0(self):
        """length >= lb0 + v."""
        import math
        n = self.n
        return n + math.factorial(n) + (math.factorial(n - 1) - 1) - 2

    def measure(self, path):
        n = self.n
        R = 1
        E = 0
        entered = set()
        targets = []
        for u, w in zip(path, path[1:]):
            wt = self.weight(u, w)
            if wt >= 2:
                R += 1
                E += wt - 2
                entered.add(self.gen_of[w])
                targets.append(w)
        # accidents: generators of entered loops that are NOT arc starts
        arc_starts = {path[0]} | set(targets)
        A = 0
        for L in entered:
            for g in self.gens[L]:
                if g not in arc_starts:
                    A += 1
        wt_total = sum(self.weight(u, w) for u, w in zip(path, path[1:]))
        import math
        return dict(R=R, E=E, v=len(entered), A=A,
                    splits=R - math.factorial(n - 1),
                    wt=wt_total, length=wt_total + n)


def report(m, name, path):
    import math
    d = m.measure(path)
    n = m.n
    lb0 = m.lb0()
    pred = n + math.factorial(n) - 2 + (n - 1) * d['v'] - d['A'] + d['E']
    si = (n - 1) * d['v'] - d['A']
    print(f"{name:26} len={d['length']:5} wt={d['wt']:5} R={d['R']:4} "
          f"E={d['E']:3} v={d['v']:4} A={d['A']:3} splits={d['splits']:4} "
          f"slack={d['length']-lb0-d['v']:3}")
    print(f"{'':26}   split identity R=(n-1)v-A : {d['R']} == {si}  "
          f"{'OK' if d['R']==si else 'FAIL'}")
    print(f"{'':26}   length identity           : {d['length']} == {pred}  "
          f"{'OK' if d['length']==pred else 'FAIL'}")
    return d['R'] == si and d['length'] == pred


if __name__ == "__main__":
    import sys, math
    sys.path.insert(0, "code")
    from permgraph import string_to_path
    from classical import recursive_superperm

    ok = True
    for n in (4, 5, 6):
        m = Model(n)
        print(f"\n=== n = {n}   loops={m.nloops}  lb0={m.lb0()} "
              f"(length >= {m.lb0()} + v),  v >= {math.factorial(n-2)} ===")
        ok &= report(m, f"classical n={n}",
                     string_to_path(recursive_superperm(n), n))
        if n == 6:
            h = [int(c) for c in open("data/houston_872.txt").read().strip()]
            ok &= report(m, "Houston 872", string_to_path(h, 6))

    m6 = Model(6)
    lb0 = m6.lb0()
    print(f"\n--- the n=6 ladder (what a proof of s(6) >= L+1 must discharge) ---")
    for L in (867, 871):
        print(f"  length {L}: v in [24, {L - lb0}]  "
              f"({L - lb0 - 24 + 1} rungs); rung v needs slack >= {L+1-lb0}-v")
    print("\n--- the n=7 ladder ---")
    lb7 = 7 + 5040 + 719 - 2
    print(f"  lb0(7) = {lb7};  length 5905: v in [120, {5905 - lb7}] "
          f"({5905 - lb7 - 120 + 1} rungs)")
    print(f"  rung v must be shown to have slack >= {5906 - lb7} - v "
          f"(i.e. >= 1 at v=141, >= 22 at v=120)")
    print("\nALL IDENTITY CHECKS PASS" if ok else "\nIDENTITY CHECK FAILED")
