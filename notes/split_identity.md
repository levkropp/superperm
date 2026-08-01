# The Split Identity (theorem)

**Theorem.** For every complete Hamiltonian path in the n-symbol
permutation overlap graph, let R = number of arcs (weight-1 runs),
v = number of entered 2-loops, and A = *accidents* (generators of entered
2-loops covered mid-arc, i.e. not at an arc start). Then

$$\mathrm{splits} = R - (n-1)! = (n-1)\,\bigl(v - (n-2)!\bigr) - A,$$

equivalently R = (n−1)v − A.

**Proof (pure bookkeeping).** Every generator of every entered 2-loop is
visited exactly once (the path is Hamiltonian), and the visit happens in
exactly one of three ways:

1. it is the start vertex — happens for exactly one generator of the
   start loop;
2. it is at an arc start after a jump — then it is a jump target entering
   its loop (this is what "entering" means);
3. it is mid-arc — an accident.

So each entered loop's (n−1) generators split into
(targets absorbed) + (accidents) + (1 for the start loop, 0 otherwise).
Summing over the v entered loops, with J = R − 1 jumps:

$$(n-1)\,v = J + A + 1 = (R-1) + A + 1
\;\Longrightarrow\; R = (n-1)v - A. \qquad \blacksquare$$

The **absorption lemma** is the corollary A ≥ 0: R ≤ (n−1)v, i.e.
v ≥ ⌈(R−1)/(n−1)⌉ (the +1 gives the tight form J ≤ (n−1)v − 1).

**Status: proven**, and verified independently three ways: the algebraic
derivation above, re-measurement from raw data of all five known extremal
strings, and a 400-walk random stress test (400/400 exact).

## Verification table (exact on all five, re-measured from raw strings)

| string | splits | (n−1)(v−(n−2)!) | A | check |
|---|---|---|---|---|
| classical n=6 (873) | 0 | 5·0 = 0 | 0 | ✓ |
| Houston n=6 (872) | 25 | 5·5 = 25 | 0 | ✓ |
| L2 n=7 (5908) | 143 | 6·24 = 144 | 1 | ✓ |
| Coanda n=7 (5907) | 120 | 6·20 = 120 | 0 | ✓ |
| Egan/Houston n=7 (5906) | 124 | 6·22 = 132 | 8 | ✓ |

## Consequences

1. **splits ≤ (n−1)(v − (n−2)!)** — strictly stronger than absorption
   wherever A > 0. Caveat (stated plainly): A is not bounded a priori, so
   this sharpens the analysis of candidate structures rather than lower
   bounds directly.
2. **wt = N + (n−1)! − 2 + splits + E**, and with splits from the
   identity: at n=7, **wt = 5038 + 6v − A + E** (exact on all three
   champions: 5901, 5900, 5899). Combined with HPV (wt ≥ 5757 + v):
   **5v + E ≥ 719 + A**, with slack σ = 5v + E − 719 − A ≥ 0
   (L2: 0, Coanda: 3, Egan: 0 — exactly tight at 727 = 719 + 8).
3. **The 5905 family (one parameter, not a single point).** A string of
   length 5905 (wt = 5898, tight) needs v ≥ 141, and at v = 141 the
   identities give the one-parameter family

   > splits = 126 − A,  E = 14 + A,  R = 846 − A.

   Any A with A ≤ splits is algebraically admissible: (A=0, splits=126,
   E=14), (A=2, splits=124, E=16), (A=8, splits=118, E=22), etc.
   Nothing in the lemma selects one — each is a different search target.
   The A = 0 member (no accidents, fewest heavy jumps) is arguably the
   most elegant target; the A = 2 member keeps the champion's arc count
   R = 844 exactly.

## Open questions

- Is there a cost law for A? (Why does Egan need A = 8 while Coanda pays
  none? An accident-vs-E tradeoff law would price the 5905 designs.)
- Can the A = 0 accident-free rigidity be strengthened into a full
  classification of tight paths (Coanda-style) at n=7?
