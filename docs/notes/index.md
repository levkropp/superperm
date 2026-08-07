---
layout: math
title: "The notebook"
---

# The notebook

The full working notebook. Every claim carries a status tag — **[THM]**
proved, **[EXH]** exhaustive, **[ID]** identity, **[MEAS]** measured only,
**[CONJ]** conjecture, **[REF]** refuted (kept with its witness, so the same
dead ends are not walked twice), **[DEAD]** dead end.

## Start here

- **[Lev's Lemmas](levs_lemmas)** — the five proved results, each with
  proof, verification counts, and an explicit *what it does not give*.
- **[The claim arsenal](lemma_arsenal)** — every ingredient with its
  status, the rung-by-rung deficit for each target bound, and the list of
  dead ends and retractions.

## The notes, in order of how load-bearing they are

- [split_identity](split_identity) — the Split Identity `R = (n−1)v − A`.
- [pbound](pbound) — `CH3`, the `A2` proof, EGAN1P / RUNGEQ / PENTCAP,
  and the open `p` question that is the whole `s(7) = 5906` problem.
- [pentad_lemma](pentad_lemma) — at most five complete traversals chain.
- [block_count_lemma](block_count_lemma) — the SBY identity, the
  split-free bounds, and §12g: no split-free 872.
- [ordering](ordering) — which quantities are ordering-free; the
  Inflation Lemma.
- [second_order](second_order) — the two-corpus harness and the
  free-jump inequality.
- [a_cost_law](a_cost_law) — accidents are E-neutral stitches.
- [champion_anatomy](champion_anatomy) — the corpus repair and what the
  44,564 champions look like.
- [constructor](constructor) — the constructor framework, and why
  local search stalls at n = 6.
- [m7_capacity](m7_capacity) — the n = 7 macro-chain capacity work:
  nineteen new exact `M_7` values and the plateau diagnosis.
- [ledger_model](ledger_model) — the master identity
  `T = (n−1)d + (B+Y) − A`.
- [a1_argument](a1_argument) — a failed proof attempt with two banked
  theorems.
- [5905_exclusion](5905_exclusion) — what the 2019 kernel sweeps did
  and did not settle.
- [swarm_stitches_findings](swarm_stitches_findings) — the stitch
  neutrality theorem and the Stride Law.
- [sig2_vs_accidents](sig2_vs_accidents) — a resolved negative: the σ²
  ban cannot bound accidents.

The registry that re-checks every tagged claim against 44,564 census strings
and 108 pool walks is
[`code/lemmas.py`](https://github.com/levkropp/superperm/blob/main/code/lemmas.py);
the re-run record is on the [validation page](../validation).
