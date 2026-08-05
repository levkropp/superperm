# s(7) baseline — decompositions and the absorption lemma at n=7

Bounds: **5888 ≤ s(7) ≤ 5906** (lower: Hunter & Raudvere, Lean-checked;
upper: Egan/Houston 2019).

## The absorption lemma at n=7: v ≥ ⌈(R−1)/6⌉ (6 generators per 2-loop)

Verified structures: 840 2-loops (n(n−2)!), 42 vertices each, exactly 6
generators each.

| string | length | wt | R | E | v | absorption floor | slack |
|---|---|---|---|---|---|---|---|
| L2 (Williams/Egan), 5908 | 5908 | 5901 | 863 | 0 | 144 | 144 | **0 (tight)** |
| Coanda ("Charlie Vane"), 5907 | 5907 | 5900 | 840 | 22 | 140 | 140 | **0 (tight)** |
| Egan/Houston, 5906 | 5906 | 5899 | 844 | 17 | 142 | 141 | **1** |

Findings:

- The lemma holds on all three (and is tight on two of three).
- **The current champion (5906) is the only one that does NOT saturate
  absorption** (v=142 vs floor 141). Its HPV slack is 0
  (5899 = 5757 + 142 exactly) — so the extra loop entry is what the
  non-standard kernel (palindromic nsk word, 2-fold symmetry) bought.
  Interpretation: at n=7 the frontier dips *below* the absorption diagonal
  by one — the only known example of that happening anywhere.
- HPV accounting at n=7: wt ≥ 5757 + v, i.e. **length ≥ 5764 + v**. Note the
  direction: the invariant bounds v from *above* for a given length, it does
  not force v up. A string of length L has v ≤ L − 5764.

  *(Erratum. An earlier version of this file read "hunter's 5888 = 5757+131",
  mixing units: 5757 is a **weight** offset and 5888 is a **length**. The
  arithmetic 5757+131 = 5888 is true but meaningless. Correctly: length 5888
  → wt 5881 → v ≤ 124.)*

- What actually has to be discharged. Covering forces v ≥ 120 (720 classes,
  six per entered loop), and length L forces v ≤ L − 5764. So proving
  s(7) ≥ 5906 is a **ladder of 22 rungs**, v = 120..141, each needing
  slack ≥ 142 − v. This is the same 22-level obligation the vlad-ds `a7`
  bundle indexes by δ = length − 5884. See
  [`m7_capacity.md`](m7_capacity.md) for the current state of that attack.

## Comparison with the n=6 ladder

- n=6: both extremal strings saturate absorption; the champion (Houston)
  is HPV-tight with v=29 = floor.
- n=7: the champion is HPV-tight but sits 1 *above* the absorption floor.
  So either (a) absorption is exactly the binding constraint at n=6 but
  only near-binding at n=7, or (b) there's a refined account (weighted
  ports? per-class generator capacity) under which 5906 is also tight.
