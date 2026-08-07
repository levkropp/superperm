---
layout: math
title: "The 5905 kernel candidate and the 2019 exclusion sweep"
---

# The 5905 kernel candidate and the 2019 exclusion sweep

*Everything below was re-verified against primary sources in Aug 2026:
the `superpermutators` Google Group threads, and by compiling and re-running
Egan's own `KernelFinder.c` and `PermutationChains`. An earlier version of
this note overstated the verdict; the corrections are marked.*

## The framework and the score law

Houston's kernel notation
([thread VRwU2OIuRhM](https://groups.google.com/g/superpermutators/c/VRwU2OIuRhM),
Feb 2019): a kernel traverses only *complete* 1-cycles and never re-enters a
2-cycle. One digit per 2-cycle segment = number of 1-cycles traversed before
leaving; a space = a weight-4 edge. Score = Σ(digit − (n−2)) − (n−2)·#spaces.
A kernel of score k(n−2) is arithmetically completable to

    n! + (n−1)! + (n−2)! + (n−3)! + (n−3) − k

At **n = 7**: score 5 → 5907, **score 10 → 5906**, **score 15 → 5905**,
score 20 → 5904. The 5906 champion's kernel is the nsk word
`666646664466646666` (length 18, score 10).

Caveat on "the kernel class": Houston later showed
([thread -EVIY36Dnyk](https://groups.google.com/g/superpermutators/c/-EVIY36Dnyk),
June 2019) that *every* superpermutation decomposes uniquely as a kernel
(path in the alternating graph Aₙ) plus extension cycles. So kernel+tree is
not a restricted class in general. What *is* restricted is the searchable
subclass — complete-1-cycle kernels in the digit notation — and the length
bound on the sweep.

## What the 2019 sweeps actually covered

Egan, [thread Ya-H_wwt_HY](https://groups.google.com/g/superpermutators/c/Ya-H_wwt_HY)
(March 2019). Both kernel counts reproduced exactly by recompiling
`KernelFinder.c`:

| sweep | scope | kernels | reproduced | outcome |
|---|---|---|---|---|
| Search 1 | palindromic, score ≥ 10, length ≤ 60 | 1,572,390 | 1,227,781 + 344,609 ✓ | 7 fruitful kernels (all score 10, lengths 18–26), **83 solutions**, all length 5906 |
| Search 2 | fully generic, score ≥ 15, length ≤ 35 | 13,294 | 13,294 ✓ | **never reported** — see below |

Notes on Search 2: at length ≤ 35 the max score is 19 and only multiples of 5
are emitted, so "score ≥ 15" means *score exactly 15*. The list is **not**
reversal-deduped — every reverse is present — so it is **6,669 kernels up to
reversal**. Length distribution: 27:5, 29:21, 30:48, 31:149, 32:392, 33:1224,
34:3042, 35:8413.

## Correction 1 — Search 2 was never reported as completed

> **Erratum.** This note previously asserted "13,294 kernels, zero
> completions" as a verified fact. Egan's own words are *"the search is still
> ongoing… it looks as if the result will be to exclude."* **No
> zero-completion result was ever posted.** The only later statement is
> secondary — [Seaburg, March 2025](https://www.loganseaburg.com/blog/superpermutations):
> "All kernels of length 35 or less were exhaustively searched, but the only
> thing stopping anyone from doing more was compute." Seaburg gives no
> independent counts; he cites Egan.

So the honest status of the ≤35 generic sweep is: *believed complete,
believed negative, not documented*. That is a re-derivable gap, not a
citation.

## Correction 2 — the K=27 candidate, and the "crash"

The unique palindromic length-27 kernel `666646664664666466466646666`
(score 15) **is in the 13,294** — one of only five length-27 kernels, and the
only palindrome among them. So it falls inside the swept range either way.

> **Erratum.** This note previously recorded that `PermutationChains` crashed
> on it. It does not. Running
> `./pc 7 nsk666646664664666466466646666 symmPairs fullSymm` gives a clean
> exit with `Exclusion of 2-cycle 726 is unviable` — a **correct
> infeasibility abort**, not a crash. It is the odd-length-palindrome
> obstruction Seaburg notes: palindromic kernels with an odd number of
> symbols are unviable and are excluded very quickly. Consistent with this,
> all 7 fruitful Search-1 kernels have **even** length (18–26). Generic mode
> (no symmetry flags) runs on the same kernel without error.

## Consequences

1. The candidate is not a live target under the symmetric search, for a
   structural reason (odd palindrome), and it lies inside the generic swept
   range regardless. Not worth compute.
2. **s(7) = 5906 is NOT proven by any of this.** The sweeps cover kernels of
   length ≤ 35 (generic) and ≤ 60 (palindromic only). The skip-floor law
   (B_min ≈ K/2 − 2) leaves arithmetically legal 5905-shapes at K ≈ 37–42,
   outside both. The certified lower bound remains 5888 (Hunter & Raudvere,
   Lean).
3. What the sweeps do establish: the champion region is saturated in the
   searchable class, so any record-beating construction must go above
   length-35 generic kernels or outside the class.
4. **Scale of the unsearched frontier.** Re-running the generator: score ≥ 15,
   length ≤ 39 gives **490,771** kernels — 37× the ≤35 set, ~10 min to
   generate. Length ≤ 42 is plausibly ~10⁷. Egan's own benchmarks: n=6 →
   42,288 solutions in ~1 min; the only n=7 run known to finish in reasonable
   time is `7 fullSymm limStab ffc` → 762 solutions in ~30 min. Barren kernels
   terminate very fast; fruitful ones dominate runtime. Seaburg reproduced
   Search 1 on an M4 Mac mini in ~12 h on 6 cores.

## Post-2019 activity (searched, none found)

The group was dead 2020–2023 and revived in 2025–2026 with threads on n=8
(46204), Lean-verified s(6) = 872 candidates, HPV lower-bound improvements
(Raudvere), and a July 2026 5906 variant. **No thread on n=7 upper bounds and
no kernel search past length 35 anywhere.** Coanda ("Charlie Vane", 5907,
Feb 2019) used the *ancestor* of PermutationChains — inside the class, not
outside it.

## Durable results retained from the episode

The skip-floor law B_min(K), the K=27 uniqueness argument (a good template
for any future candidate), the stitch neutrality theorem, and the Stride Law
(w(σ⁻¹g_j, g_{j+k}) = k+1 — chain stitches are never profitable).
