---
layout: math
title: "Swarm findings on stitches (August 2026) — durable results"
---

# Swarm findings on stitches (August 2026) — durable results

## 1. The unique 5905 kernel candidate (agent-17)

In the kernel+tree normal form (length = 5908 + K − Σd/5, verified on all
five extremal strings), a 5905-string needs Σd = 5K + 15 with skip
B ≥ B_min(K) (exhaustively computed floor: all-complete kernel chains die
at K = 5; B_min(18) = 8 = nsk's skip).

- K ≤ 26: **impossible** (skip floor exceeded).
- K = 27 with exactly B = 12 (= B_min(27), six 2-class stitches) is the
  minimal 5905 kernel shape; symmetric designs need odd K (skip parity).
- **Unique palindromic candidate (up to relabeling):**
  `666646664664666466466646666`
  (4s at {5, 9, 12, 16, 19, 23}; Σd = 150, A = 12, E = 26, v = 141,
  splits = 114, R = 834 → length 5905.)

> **Erratum (Aug 2026).** This paragraph read: "The 5905 question is now a
> single symmetric completion run on that skeleton… Egan's
> PermutationChains crashes on it (and on the champion kernel too — tool
> issue, not the candidate)." Both halves are wrong, verified by compiling
> and running the tool:
>
> - It does **not** crash. `./pc 7 nsk<candidate> symmPairs fullSymm` exits
>   cleanly with `Exclusion of 2-cycle 726 is unviable` — a correct
>   infeasibility abort. Palindromic kernels of **odd** length are
>   structurally unviable; all 7 fruitful kernels in Egan's 2019 palindromic
>   sweep have even length (18–26). Our candidate has K = 27.
> - The "crash on the champion kernel" was the tool correctly reporting
>   `Kernel is NOT palindromic` for a non-palindromic input under
>   `symmPairs`.
> - The candidate is not a live single-run target, and it already lies
>   inside Egan's swept generic range (it is one of only five length-27
>   kernels of score 15, all 13,294 of which were generated for the ≤35
>   sweep).
>
> Details and primary sources: [`5905_exclusion.md`](5905_exclusion).

## 2. Stitch neutrality theorem (agent-16)

With the free digraph component count `comp ≥ v − splits` (equality
characterized), the accident count A **cancels identically** from
`R + comp − 1`: stitches/splits/seam-widths are bound-neutral; their whole
effect is on **slack** (availability of weight-3 connectors). All three
champions saturate `length = 5764 + v + slack` exactly. Egan's 4 motifs
are load-bearing slack-eliminators (~5 units each vs naive
alternatives).

## 3. Stride Law (agent-15, proven)

For a loop's generator cycle, w(σ⁻¹g_j, g_{j+k}) = k + 1. Hence skipping
k − 1 generators along the natural chain costs exactly k − 1 for k − 1
accidents: **chain stitches are never profitable at any n.** Egan's 4
profitable stitches are non-chain (reuse of already-forced weight-3
entries). Retrofitting a stitch into an existing champion costs ≥ +(n−1)
(Houston: +5, Coanda: +6, measured on every possible move) — which is why
annealing/local search never improves champions; stitches must be
co-designed.

## 4. The (N, D, G) calculus (agent-14)

Exact σ=0 move catalog (only three jump types: N = w2 first-entry with
feeder split, C = free w2 re-entry, D = w3 first-entry) and the exact
5905 family (σ=0, v=141, G=0):
(R, A, D) = (846, 0, 14), (845, 1, 15), (844, 2, 16), (843, 3, 17),
(842, 4, 18). Open: the global "seed economy" — can a v=141 feeding web
be rooted at ≤ 14–18 D-seeds? Egan's palindromic kernel forces A = 8,
hence v = 142: the one symbol between 5906 and 5905 lives exactly there.
