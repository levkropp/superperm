"""How much is left on the table at delta=12, and where it is.

Two questions, both answered against the real 332-row frontier.

1. WHY capacity plateaus.  The bundle measures each hard summary against
   F_c(G), a max-plus convolution of the partition-closure cap W over
   c = 1 + x + K chains.  Since W(0) = M_7(0) = 5, every chain contributes
   five macros at zero gap, so

       F_c(G)  ~  lambda * G  +  5c.

   Extending the exact table lowers lambda.  It cannot touch the 5c floor,
   because M_7(0) = 5 is already exact.  Rows whose cap is floor-dominated
   are therefore immune to any amount of table extension -- which is exactly
   the observed plateau.

2. WHAT attacks the floor.  The bundle's own full-endpoint tax (section 7 of
   A7_5896_PROOF_NOTE.md) replaces W by E(g) = max(0, W(g) - 1) on every
   pre-hard region, i.e. it shaves the floor from 5 to 4 on K of the c
   chains.  That is the one lever with the right shape.  At delta=11 it was
   licensed because capacity was tight enough to force every hard component
   full; at delta=12 only 230 of 1261 summaries are marked full and only 45
   carry a tax.  This script measures the ceiling: what if fullness were
   forced everywhere?
"""

import json
from capacity_dp import capacity, M7_PUBLISHED, M7_FULL
from frontier12 import make_F, load_rows

GMAX, CMAX = 90, 40


def make_T(W, cmax, gmax):
    """T[u][k][G]: u untaxed chains + k taxed chains, total gap <= G.

    Untaxed chains are capped by W, taxed ones by E(g) = max(0, W(g)-1).
    """
    E = [max(0, W[g] - 1) for g in range(gmax + 1)]
    base = {0: [0] * (gmax + 1)}
    for u in range(1, cmax + 1):
        prev, cur = base[u - 1], [0] * (gmax + 1)
        for G in range(gmax + 1):
            cur[G] = max(W[a] + prev[G - a] for a in range(G + 1))
        base[u] = cur
    T = {}
    for u in range(cmax + 1):
        T[u] = {0: base[u][:]}
        for k in range(1, cmax + 1):
            prev, cur = T[u][k - 1], [0] * (gmax + 1)
            for G in range(gmax + 1):
                cur[G] = max(E[a] + prev[G - a] for a in range(G + 1))
            T[u][k] = cur
    return T


def count(rows, cap_of):
    alive = 0
    for row in rows:
        x = int(row["x"])
        for s in json.loads(row["hard_summaries"]):
            if s["N"] <= cap_of(x, s):
                alive += 1
                break
    return alive


if __name__ == "__main__":
    rows = load_rows()
    print(f"delta=12 frontier rows: {len(rows)}\n")

    for label, table in [("published, exact to g=21", M7_PUBLISHED),
                         ("this work, exact to g=40", M7_FULL)]:
        W, _ = capacity(table, gmax=200)
        F = make_F(W, CMAX, GMAX)
        T = make_T(W, CMAX, GMAX)

        n_untaxed = count(rows, lambda x, s: F[1 + x + s["K"]][s["G"]])
        n_asis = count(rows, lambda x, s: (
            T[1 + x][s["K"]][s["G"]] if s["full"] else F[1 + x + s["K"]][s["G"]]))
        n_all = count(rows, lambda x, s: T[1 + x][s["K"]][s["G"]])

        print(f"--- {label}   (W(66) = {W[66]}) ---")
        print(f"  no tax                        : {n_untaxed:4d} survivors")
        print(f"  tax on summaries marked full  : {n_asis:4d} survivors")
        print(f"  tax everywhere (the ceiling)  : {n_all:4d} survivors")
        print()

    print("""Read: the gap between the first and last line of each block is what a
fullness-forcing argument is worth.  The gap between the two blocks is what
nineteen new exact capacity values are worth.  Neither alone clears
delta=12; the question is whether together they leave a residue small
enough to attack by hand, as the fourteen branches at delta=11 were.""")
