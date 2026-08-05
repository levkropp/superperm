"""Recompute the a7 delta=12 frontier under a sharpened capacity function.

Reads a7/bundle_v2/A7_DELTA12_FRONTIER.csv (332 surviving branches), first
reproducing each row's `cap` from the bundle's own W, then re-testing every
row against caps derived from a hypothetically extended exact M_7 table.

A row dies when N > cap for EVERY admissible hard summary.
"""

import csv, json, sys
from capacity_dp import M7_EXACT, M7_FULL, capacity

CSV = "/home/lk/a6-872/a7/bundle_v2/A7_DELTA12_FRONTIER.csv"


def convolve(W, gmax):
    """F_c(G) tables: F[c][G] = max sum of W over c parts totalling <= G."""
    F = [[0] * (gmax + 1)]                       # c = 0
    cur = [W[g] for g in range(gmax + 1)]        # c = 1
    F.append(cur[:])
    return F, cur


def make_F(W, cmax, gmax):
    F = {0: [0] * (gmax + 1)}
    F[1] = [W[g] for g in range(gmax + 1)]
    for c in range(2, cmax + 1):
        prev, cur = F[c - 1], [0] * (gmax + 1)
        for G in range(gmax + 1):
            best = 0
            for a in range(G + 1):
                t = W[a] + prev[G - a]
                if t > best:
                    best = t
            cur[G] = best
        F[c] = cur
    return F


def load_rows():
    with open(CSV) as f:
        return list(csv.DictReader(f))


def analyse(table, label, rows, F=None):
    W, _ = capacity(table, gmax=90)
    gmax = 90
    cmax = 40
    F = make_F(W, cmax, gmax)
    survivors, repro_ok, repro_tot = [], 0, 0
    for row in rows:
        x = int(row["x"])
        summaries = json.loads(row["hard_summaries"])
        alive = False
        for s in summaries:
            qA, h, G, Nn = s["qA"], s["h"], s["G"], s["N"]
            K = s["K"]
            c = 1 + x + K
            if G < 0 or G > gmax or c > cmax:
                alive = True
                continue
            cap = F[c][G]
            if s.get("cap") is not None:
                repro_tot += 1
                repro_ok += (cap == s["cap"])
            if Nn <= cap:
                alive = True
        if alive:
            survivors.append(row)
    return survivors, repro_ok, repro_tot, W


if __name__ == "__main__":
    rows = load_rows()
    print(f"delta=12 frontier rows: {len(rows)}")

    surv, ok, tot, W = analyse(M7_EXACT, "bundle", rows)
    print(f"\n--- baseline (bundle's own W, exact table to g=21) ---")
    print(f"  reproduced `cap` field on {ok}/{tot} hard summaries")
    print(f"  W(66) = {W[66]};  surviving rows = {len(surv)} / {len(rows)}")

    print(f"\n--- with the exact table extended (all values proven here) ---")
    print(f"  {'exact to':>9} {'last entry':>28} {'W(66)':>6} {'survivors':>10}")
    for top in (22, 25, 28, 32, 36, 40):
        t = M7_FULL[: top + 1]
        s2, _, _, W2 = analyse(t, str(top), rows)
        lbl = "M_7(%d) = %d" % (top, t[-1])
        print(f"  {top:>9} {lbl:>28} {W2[66]:>6} {len(s2):>10}")
