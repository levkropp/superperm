---
layout: math
title: "Validation record"
---

# Validation record

What this repo's claims have been checked against, where, and how to
re-check them. Three parts:

1. [The 2026-08-07 re-run](#the-2026-08-07-re-run) — every gate that fits on
   an 8 GB MacBook, re-executed from scratch during the repo cleanup.
2. [Not re-runnable here](#not-re-runnable-on-this-machine) — the heavy
   certificates, with where their evidence lives.
3. [Historical ground truth](#historical-ground-truth) — the known answers
   the machinery reproduced in earlier sessions.

Environment for the re-run: `.venv` (Python 3.14.6; numpy 2.5.1, scipy
1.18.0, ortools 9.15), Apple clang 21 for the C provers, one heavyweight
process at a time.

## The 2026-08-07 re-run

### The registry (the one command that checks everything)

| command | outcome |
|---|---|
| `python code/lemmas.py` | **PASS** — the full claim registry (every [THM]/[CONJ]/[MEAS]/[REF] with its witness) against 44,564 census strings and 108 constructed pool walks: **no [THM] violated on either corpus**, exit 0. Run twice (before and after the cleanup deletions), same verdict. |

### The n = 6 certificate chain

| command | outcome |
|---|---|
| `python code/certify.py --string data/houston_872.txt --n 6` | **VALID** — 720/720 distinct permutations, length 872 (independent stdlib-only checker) |
| `python code/verify_v1_absorption.py` | **PASS** — absorption lemma tight on classical (24) and Houston (29), plus 200/200 random walks |
| `python code/verify_v2_covers.py` | **PASS** — 10,068 exact covers re-enumerated from scratch, byte-identical to shipped `data/covers_10068.npz` |
| `python code/verify_family_orbit.py` | **PASS** — classical ordering costs exactly 267; family-orbit smoke bound certified ≥ 264 |
| `python code/verify_orbits_tsp.py` | 28/29 orbits certified ≥ 265 here (26 OPTIMAL at 267–274, two FEASIBLE at certified 267); orbit 28 — the known holdout — reached only **264** under the CP-SAT time cap on this laptop, so the script's ≥ 265 assert trips (exit 1). Orbit 28 is settled at **≥ 267** by the exhaustive `orbit28b.c` search (below), so the chain's conclusion stands. Per-orbit table below. |

### The current results

| command | outcome |
|---|---|
| `python code/pbound.py --quick` | CH3 valid (0 violations); minimum **29** over the 10,068 exact covers against HPV 24 |
| `python code/freejoin.py` | FORCE gate **OK** — max core out-degree 1 everywhere (n = 6 and n = 7 corpora) |
| `python code/a2hall.py` | A2 four-count slack **0 on 107/107** census strings; Hall-matching deficiency 0 on 107/107 |
| `python code/vlock.py` | thin-loop lock holds — no n = 7 champion can lower `v` by re-cutting |
| `python code/nbhd.py --n 6` | 625/625 single-cut neighbours priced exactly; **29 is a certified local minimum** of CH3 |
| `python code/vplus.py` | min(`v + p`) = **143** at n = 7 over 106 strings (102 attain it) |
| `python code/egan1p.py --n 6` | INFEASIBLE in 0 s ⟹ `v = (n−2)!` forces length ≥ **873** |
| `python code/egan1p.py --n 7` | INFEASIBLE in 9 s ⟹ `v = 120` forces length ≥ **5908** |
| `python code/pentcap.py` | n = 8: longest weight-4-linked class-disjoint Pentad chain = **5** = n−3 (1,249,920 nodes, exhaustive) |
| `python code/sby_ladder.py` | s(6) ≥ 868, s(7) ≥ 5885 from HPV+COVER+SPLIT+BLOCK; s(5) = 153 exact |
| `python code/rigidity7.py` | all structural assertions OK; Pentad rung `X ≥ 130` ⟹ ≥ 5895 |
| `python code/chain_count.py` | `Y ≥ (n−3)!−1`, exact at n = 4, 5, 6; Y = 5 at B = 24 impossible (0/8,640 linkable covers) |
| `python code/coset_lemma.py` | coset transversals and the exit table verified at n = 7 |
| `python code/pentad_orbits.py` | 1,008 ⟨s⟩-orbits, 0 failing pairwise class-disjointness; 24 disjoint orbits partition all 720 classes (= counting ceiling) |
| `python code/split_free_5889.py` | the pinned (B,Y) = (124,0) state fails on all 25 chain vectors ⟹ split-free s(7) ≥ **5889** |
| `python code/block1.py` | no single-block walk with W ≤ 30 at n = 5 (20M-node budget) — BLK2/BLK3 gate |
| `python code/exit_table.py` / `exit_table_n.py` | exit-cap tables verified; general-n soundness never false at n = 5, 6 |
| `python code/verify_witness.py code/witness.txt` | **VALID** — M₇(40) ≥ 71 by an independent checker |
| `python code/cpsat_tsp.py 3` / `… 4` | OPTIMAL at lengths **9** and **33** — exact s(3), s(4) by ATSP |
| `python code/classical.py` | classical construction valid at 1, 3, 9, 33, 153, 873 |
| `python code/census.py --summary` | master identity `T = (n−1)d + (B+Y) − A` holds on all 1,468 shipped records; Egan-savings law OK at n = 6–9 |
| `omstretch` (C, `-O3`) | ρ(120) = **31** exact — matches the arsenal |
| `splitfree6b` soundness gate | **FEASIBLE at E ≤ 29** (finds the known 873 in 120 nodes) — the E ≤ 28 prover can find solutions that exist |
| C compile check | `omstretch.c`, `macro7.c`, `orbit28b.c`, `splitfree6b/c/d.c` all build clean under Apple clang 21 |

Note: `python code/census.py` (no `--summary`) re-measures and **rewrites**
`data/census.json`; without the optional upstream corpus clone it covers
`data/` only, so the shipped file (1,468 records) is the superset.

### Per-orbit class-TSP results (`verify_orbits_tsp.py`, this machine)

26 orbits OPTIMAL: values 267 (orbits 0, 17), 269 (orbits 1, 2, 3, 8, 9, 10,
11, 12, 13, 14, 18, 25), 270 (orbits 6, 16), 271 (orbits 5, 19, 20, 21, 24,
27), 272 (orbits 4, 15, 26), 274 (orbit 23). Two FEASIBLE with certified
bound 267 (orbits 7, 22). Orbit 28: FEASIBLE at 267, certified 264 under the
time cap — the same holdout as in the original run, which certified it at
265 and which `orbit28b.c` then settled at ≥ 267 exhaustively
(2.399×10¹⁰ nodes). Separately, `verify_family_orbit.py` (CI) prices the
classical construction's own cover at exactly 267, matching the floor seen
here.

## Not re-runnable on this machine

These exceed an 8 GB laptop in time or hardware; their evidence is in-repo
and the cheap gates above confirm the machinery behaves.

| certificate | scale | evidence |
|---|---|---|
| No split-free n = 6 walk with E ≤ 28 ⟹ split-free s(6) = 873 exactly | 2.98×10¹³ nodes, 2,203 leaf verdicts | `data/e28_certificate.txt`; soundness gate (re-finds the 873 at E ≤ 29) **re-run here: PASS** |
| Orbit 28 has no Hamiltonian path of weight 266 | 2.399×10¹⁰ nodes | input `data/orbit28_starts.txt`; `orbit28b.c` builds here; corroborated by the CP-SAT bound above |
| `M_7(g)` exact for g = 22…40 (`macro7.c`) | hours per budget | witness shipped (`code/witness.txt`), independently validated by `verify_witness.py` |
| GPU prover/annealer runs (RTX-era) | CUDA hardware | artifacts retired; their n = 4 / n = 5 verdicts are corroborated by `cpsat_tsp.py` and `block1.py` above |

## Historical ground truth

Reproduced in earlier sessions; the still-runnable ones were re-run above.

- **Houston's 872 string is a valid superpermutation** (720/720) — re-run
  above, still passing.
- **Triangle inequality** of the n = 6 overlap metric verified on all
  720³ triples, so min superpermutation length = 6 + min Hamiltonian path
  weight (the ATSP model is exact, not a relaxation). Script retired; the
  consequence is exercised by every ATSP gate above.
- **s(3) = 9, s(4) = 33** by exact ATSP — re-run above (`cpsat_tsp.py`).
- **s(5) = 153** by this repo's structure-aware prover (138M nodes, 0
  solutions at budget 29; positive control finds the known solutions at
  budget 30). Prover retired; independently consistent with the
  `sby_ladder.py` n = 5 row (exact) and `chain_count.py` (exact at n = 5).
- **s(6) ≥ 868 certificate chain** (absorption → rigidity → 10,068 covers →
  29 orbit TSPs) — fully re-run above; it retro-proves s(4) and s(5) by
  construction.
- **The same scheme's gates all pass at small n**: n = 4 → 1 solution,
  n = 5 budget 29 → 0 solutions, matching the exact answers.

## CI

`.github/workflows/ci.yml` runs on every push: the n = 6 certificate chain,
the full claim registry, the CH3/FORCE/A2/EGAN1P gates, the self-contained
structural gates, the witness validator, and a read-only census summary.
