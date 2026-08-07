---
layout: math
title: "The lower bound at large n: s(n) ≥ Egan(n) − 1, and the one lemma it hangs on"
---

# The lower bound at large n: `s(n) ≥ Egan(n) − 1`, and the one lemma it hangs on

*Status: programme note (August 7, 2026). What is proved is tagged; what is
measured is tagged; the rest is the plan. Related: [the gain-one
note](gain_one_kernel) (the design side), [`pbound`](pbound) §§13–16
(RUNGEQ / PENTCAP / the ladder).*

## 1. The target, restated

With `s(n) ≤ Egan(n) − 1` for all `n ≥ 8` (verified here through n = 13),
the whole question at large n is now one-sided: **can the lower bound be
raised to `Egan(n) − 1`?** Current best lower bounds (Hunter & Raudvere,
Lean) sit at `Egan(8) − 102` and fall further behind as n grows; HPV is
`Egan(n) − (n−3)!`. A matching lower bound would pin
`s(n) = Egan(n) − 1` for all `n ≥ 8`.

**Honest caveat, stated up front.** Gain-*two* exists at n = 7 (the 5906
champions, `Egan(7) − 2`). So `s(n) = Egan(n) − 1` for all `n ≥ 8` is a
conjecture, and its negation is exactly the 46203 question at n = 8. The
two questions are the same coin; this note is the lower-bound side.

## 2. The ledger reduction (both sides of the coin)

With `T = length − base(n)`, `base(n) = n + n! + (n−1)! − 3`,

```
T = (n−1)(v − (n−2)!) + (B + Y − A),        gain over Egan = (B + Y − A)/(n−2)
```

— the last by the Split Identity and the Egan vertex `(v = (n−1)(n−3)!,
B+Y−A = 0)`. Every known word is HPV-tight, so this is exact. The gain
landscape:

| word | n | v | B+Y−A | gain |
|---|---|---|---|---|
| Egan | any | (n−1)(n−3)! | 0 | 0 |
| Houston 872 | 6 | 29 | 4 | 1 |
| 5906 champions | 7 | 142 | 10 | **2** |
| Raudvere 46204 | 8 | 839 | 6 | 1 |
| Echols 408965 | 9 | 5759 | 7 | 1 |

## 3. The equality shape, proved and measured

`RUNGEQ` **[THM]** (`pbound` §15): sitting one below the ladder's need at
any rung forces `B = comps`, `Y = p − 1`, all inter-chain links of weight
exactly 4, and average chain length exactly `n−2` (at `A = 0`; more with
accidents).

Measured on the actual gain-one words (this repo, August 7):

| word | T | S | comps | p | CH3 |
|---|---|---|---|---|---|
| Raudvere 46204 | 839 | 833 | **6 = n−2** | **1** (exact) | 839, **tight** |
| Echols 408965 | 5759 | 5752 | **7 = n−2** | **1** (exact) | 5759, **tight** |

So the gain-one design is *one free chain of `n−2` components joined at
weight 3*, and CH3 cannot see it — the bound reads exactly `T` there. (The
5906 is the same shape one level down: `comps = 18, p = 1`, one chain.)

## 4. The one lemma the lower bound hangs on — and a first theorem

`PENTCAP` **[EXH]** (`pbound` §16): weight-4-linked chains of pairwise
class-disjoint **complete Pentads** cap at `n−3` — exhaustive at n = 6, 7,
8 (caps 3, 4, 5). That kills `T = Egan_T − 2` at **rung 0** (every
component complete), which is why `v = (n−2)!` champions are excluded at
n = 6, 7, 8 (`EGAN1P`).

At rung `j > 0` the equality components **span several loops**, and
PENTCAP does not apply directly. The missing general lemma is the
multi-loop analogue (MLCAP): the same cap for chains whose components may
span several 2-loops.

**But a first multi-loop theorem already falls out of the pieces** — the
point of this note:

> **`RUNGJ` [THM]** *(conditional on PENTCAP's cap `n−3` at the given n —
> exhaustive at n = 6, 7, 8)*. If a complete walk at rung `j`
> (`v = (n−2)! + j`) has `T = Egan_T − 2`, then
>
> ```
> j · ((n−1)(n−2) + 1)  ≥  (n−3)! − (n−2) + A·(n−2),
> ```
>
> where `A` is the walk's accident count. Equivalently, **`T ≥ Egan_T − 1`
> at every rung `j < ((n−3)! − (n−2)) / ((n−1)(n−2) + 1)`** — a
> factorially-long proved prefix of the rung ladder, at general n.

**Proof.** At `T = Egan_T − 2`, `RUNGEQ` forces `B = comps`,
`Y = p − 1`, `p = (n−3)! − j − 1`, `comps = (n−2)! − (n−2)j + A`, all
intra-chain joins of weight exactly 3 and all inter-chain links of weight
exactly 4. The `p` free chains form a single weight-4-linked sequence in
walk order. A *pure* chain (all components complete Pentads) has its
intra-joins at weight 3, hence is an om-chain — an `⟨s⟩`-orbit segment
(Pentad Lemma, [THM]). A maximal run of pure chains therefore embeds as a
PENTCAP sequence over distinct orbits (distinct, because the segments are
pairwise class-disjoint), so **a pure run has at most `n−3` chains**.
Chains containing a multi-loop component are few: merges satisfy
`Σ(μ−1) = v − comps ≤ S = (n−1)j − A` (A2, [THM]), so there are at most
`S` mixed chains and at most `S + 1` pure runs. Hence
`p ≤ (S+1)(n−3) + S`, i.e.
`(n−3)! − j − 1 ≤ ((n−1)j − A + 1)(n−3) + (n−1)j − A`, which rearranges
to the stated inequality. ∎

**The boundary** (rung `j` up to which `T ≥ Egan_T − 1` is proved, A = 0):

| n | rungs proved (`j ≤`) | top rung (champions) |
|---|---|---|
| 6 | 0 | 5 (Houston, A=0) |
| 7 | 0 | 22 (5906, A=8) |
| 8 | **2** | 119 (Raudvere) |
| 9 | **12** | 719 (Echols) |
| 10 | **70** | 5039 |
| 12 | **3,330** | 362,879 |

Consistency checks: the 5906 (`j = 22, A = 8`) needs `22·31 ≥ 19 + 40` —
holds (638 ≥ 59); Houston (`j = 5, A = 0, n = 6`) and both gain-one words
sit far above their boundaries, as they must. At n = 7 the boundary is 0 —
the method cannot see rung 1 there, which is exactly where the small-n
exception lives.

The theorem converts "the rung ladder" into: a proved prefix growing like
`(n−3)!/n²`, then an open band of width roughly `(n−3)!` where champions
currently live. **Any word beating `Egan(n) − 1` must sit within that top
band, or spend accidents** (each accident buys `(n−2)/((n−1)(n−2)+1)`
rungs of slack). It is the first general-n rung theorem since RUNGEQ, and
it is unconditional at n = 6, 7, 8 (PENTCAP exhaustive there).

**What MLCAP would add.** If mixed chains also cap below `n−3`, the
boundary moves up; if pure-and-mixed chains jointly cap at `n−3`, the
proved prefix extends to essentially the whole ladder and
`s(n) ≥ Egan(n) − 1` follows at large n.

**Measured, and the naive form is dead** (August 7, exhaustive DFS, exit
model made generous in the sound direction): components of 1–2 loops
weight-4-chain to **≥ 20 at n = 6, ≥ 84 at n = 7, ≥ 416 at n = 8** — no
cap below Pentad size exists, and 2-loop components chain *longer* than
single loops. PENTCAP's cap is a property of *complete* Pentads (big
burns), not of class-disjointness alone. So a cap stated over δ-components
plus weight-4 links is **false already at n = 6** — registered as a dead
end with its witness chains. The viable MLCAP must instead use the RUNGEQ
equality structure itself (weight-3 om intra-chain joins — the cap lives
in the core, where `CORECAP` already gives `n−2` exhaustively), i.e. a
statement about how many *fringe* doors the equality case can afford —
`FRINGE`/`PCOUPLE` measured: fringe edges are abundant exactly at
champions, zero at `S = 0`.

A plausible route is **defect counting**: at rung `j` only a bounded
number of components can be multi-loop (each split class costs a merge),
so for small `j` most chains are pure Pentad chains, capped at `n−3`, and
the RUNGEQ average `n−2` is unreachable. The argument weakens as `j`
grows — at the top rungs nearly all components are multi-loop — which is
exactly where the gain-two constructions (n = 7, and the n = 8 kernel
candidates of the gain-one note) live. Partial versions (rung `j ≤ J`)
still tighten the lower bound conditionally, in the style of the 22-rung
ladder at n = 7.

## 5. Why not the other routes

- **HPV/CH3**: both are *tight* on the gain-one words (§3) — no
  ordering-free bound of this family can exclude them.
- **The SBY ladder** (`block_count_lemma`): gives `T ≥ (n−2)! + 1` at
  best — `Egan − (n−3)! + 1`, far short.
- **Lean certificates (Hunter & Raudvere)**: the strongest lower bounds,
  but a different method; their improvements over HPV grow slowly
  (+2, +4, +18 at n = 6, 7, 8) and do not obviously reach `Egan − 1` at
  any n ≥ 7.

The chain-cap route is the only one whose proven pieces (RUNGEQ's shape,
PENTCAP's cap) already sit at the right scale.

## 6. Status and next steps

- **[THM]** RUNGEQ equality shape; **[EXH]** PENTCAP at n = 6–8;
  **[MEAS]** gain-one words are single-chain, CH3-tight (§3).
- **[THM]** **`RUNGJ`** (§4): `T ≥ Egan_T − 1` on a factorially-long rung
  prefix — registered and corpus-gated (`code/lemmas.py`, 237/237).
- **[DEAD]** **naive MLCAP** (§4): no cap over δ-components + weight-4
  links below Pentad size exists (measured chains ≥ 416 at n = 8).
- **Next**: the core-side version — bound the *fringe* doors available in
  the equality case (`CORECAP` caps core-only chains at `n−2`
  exhaustively; the 5906's own chain uses fringe, so the statement must
  price fringe edges against `A`, the accidents that create them).
- **Either outcome is a result**: a fringe-priced chain lemma tightens the
  lower bound at large n; a counterexample fill at n = 8 is a new record
  (46203) and reshapes the conjecture `s(n) = Egan(n) − 1`.
