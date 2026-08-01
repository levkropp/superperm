# The Split Identity — a lemma built on the absorption lemma

**Statement (verified computationally on all known extremal strings).**
For a Hamiltonian path in the n-symbol permutation overlap graph, let

- $R$ = number of arcs (weight-1 runs), splits $= R - (n-1)!$,
- $v$ = number of entered 2-loops,
- $A$ = **accidents**: generators of entered 2-loops that are covered
  mid-arc (i.e., NOT at an arc start).

Then

$$\mathrm{splits} = (n-1)\,\bigl(v - (n-2)!\bigr) - A.$$

Equivalently, since $R - 1 = (n-1)v - a$ with $a = A + [\text{start loop
entered}]$ (the absorption accounting identity), the split identity is the
same statement re-centered at the start vertex. The absorption lemma
$v \ge \lceil (R-1)/(n-1) \rceil$ is the corollary obtained by noting
$a \ge 0$.

## Verification (exact match on all five)

| string | splits | $(n-1)(v-(n-2)!)$ | $A$ | $\checkmark$ |
|---|---|---|---|---|
| classical n=6 (873) | 0 | $5 \times 0 = 0$ | 0 | ✓ |
| Houston n=6 (872) | 25 | $5 \times 5 = 25$ | 0 | ✓ |
| L2 n=7 (5908) | 143 | $6 \times 24 = 144$ | 1 | ✓ |
| Coanda n=7 (5907) | 120 | $6 \times 20 = 120$ | 0 | ✓ |
| Egan/Houston n=7 (5906) | 124 | $6 \times 22 = 132$ | **8** | ✓ |

Measured directly from the strings (arc segmentation + generator sets),
not algebraically assumed.

## Consequences

1. **splits ≤ (n−1)(v − (n−2)!)** — a new necessary R–v coupling, strictly
   stronger than the absorption lemma wherever A > 0.
2. wt at n=7: $wt = 5038 + 6v - A + E$ (checked on all three champions).
   Combined with HPV ($wt \ge 5757 + v$): **5v + E ≥ 719 + A**, with
   slack σ = 5v + E − 719 − A ≥ 0 (Coanda: 3, L2: 0, Egan: 0 — Egan is
   exactly tight at 727 = 719 + 8).
3. **The 5905 design target is pinned**: a string of length 5905
   (wt = 5898, tight) needs **(v = 141, splits = 124, A = 2, E = 16)** —
   from wt = 5038 + 6v − A + E and splits = 6(v−120) − A. Note E = 16,
   one *below* the champion's 17: the 5905 path must be cheaper in every
   coordinate, not just v.

## Where it points

- The 141-family enumeration now filters: look for 141-loop covers whose
  traversal has exactly 2 accidents. The accident count is computable per
  family+traversal, making the prover's prune budget sharper.
- Open: is there a cost identity wt = 5757 + v + g(A, E) that *explains*
  why the champion needed A = 8? (Coanda: A=0, σ=+3; Egan: A=8, σ=0.)
