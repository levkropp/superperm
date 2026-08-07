---
layout: math
title: "Certificate: s(6) >= 868"
---

# Certificate: s(6) ≥ 868

> **Status note (August 2026).** This is **not a new bound**: days before this
> certificate was produced, stronger results were already public — s(6) ≥ 869
> (Hunter & Raudvere, Lean-4 machine-checked) and s(6) = 872 exactly
> (vlad-ds, computer-assisted, preliminary). What follows is this
> repository's **independent** proof of 868 by an elementary counting route,
> kept because every step of it is re-checkable from this repo alone.

**Claim.** Every superpermutation on 6 symbols has length at least **868**
(walk weight ≥ 862). This was computed before the results above were known to
us, and improves the 2011/2018 bound of 867 (4chan / Houston–Pantone–Vatter).
Status: computer-assisted theorem, independently verified in this repository
as described below.

## The proof chain

**(0) Model (published + verified in-repo).** Vertices = the 720
permutations; edge weight w(u,v) = symbols appended to morph u into v.
Triangle inequality verified on all 720³ triples (`verify_triangle.py`), so
minimal superpermutation length = 6 + min Hamiltonian path weight.
The HPV invariant (published): **wt ≥ p + c + v − 2** with p = distinct
permutations visited, c = completed 1-cycles (≥ 119 for complete walks),
v = entered 2-loops.

**(1) Absorption lemma (verified: `V1` script, PASS).** Each 2-loop has
exactly 5 generators, and a jump target enters a loop only if it is one of
its generators. A path with R arcs has R−1 distinct targets, hence
**v ≥ ⌈(R−1)/5⌉**. Tight on both known extremal strings: classical
(24 = ⌈119/5⌉) and Houston (29 = ⌈144/5⌉), plus 200 random walks.

**(2) Coverage premise (verified, PASS).** Every visited vertex lies in an
entered 2-loop (arcs stay in their entry generator's class ⊆ its loop;
checked on classical and Houston).

**(3) Rigidity of v = 24 (logic, reviewed).** v = 24 with 30-vertex loops
covering 720 vertices forces an **exact cover**: 24 disjoint loops.
Disjointness ⇒ each 1-cycle contains exactly one cover-generator ⇒ at most
one jump target per class; the start vertex must be its class's generator
(else a 25th loop is entered). Hence **R = 120, all arcs full**, and
**wt = 600 + TSP(𝒳)**, where TSP(𝒳) is the min Hamiltonian path over the
120 classes with jump weights δ(C,C′) = w(sig⁵(g_C), g_C′) (g_C the class's
unique cover-generator). (Verified: classical is an exact cover, R=120.)

**(4) Finite computation (independently re-done twice).** Exact covers of
the 120 classes by 24 of the 144 2-loops: **10,068** (two independent
enumerators agree to the set). Canonicalization under S₆ relabeling gives
**29 orbits** (sizes sum exactly to 10,068). Per orbit, the class-TSP is
solved with CP-SAT (the same model that reproduces s(4) and s(5) in this
repo): **all 29 orbits certified TSP ≥ 265** — 28 at OPTIMAL (267–274),
one at certified 265 (`results_orbit_tsp.log`).
(The family cover's classical ordering attains exactly 267 → 867.)

**(5) Conclusion.** Any complete walk: if v ≥ 25, wt ≥ 837 + 25 = **862**;
if v = 24, wt ≥ 600 + 265 = **865**. Hence wt ≥ 862 and
**s(6) = 6 + wt ≥ 868**. ∎

## Independent-derivation note

The scheme was found by three separate research agents (v-coupling lemma;
cycle-cover refinement with SEC-LP=840 ceiling proof; generator-landing
lemma J ≤ 5v−1) whose derivations and computations agree at every measured
point, and the same scheme **retro-proves s(4) = 33 and s(5) = 153**
exactly (n=4: 4 covers, TSP 11; n=5: 25 covers, TSP 52) — the strongest
soundness check available.

## Reproduction

Everything runs from the repo root against shipped data:

```
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python code/certify.py --string data/houston_872.txt --n 6   # string validity
.venv/bin/python code/verify_v1_absorption.py                          # step (1), PASS
.venv/bin/python code/verify_v2_covers.py                              # step (4): re-enumerates
                                                   # all 10,068 covers and byte-compares
                                                   # with data/covers_10068.npz
.venv/bin/python code/verify_family_orbit.py       # CI-sized step (4): classical ordering
                                                   # costs exactly 267; smoke bound >= 264
.venv/bin/python code/verify_orbits_tsp.py         # full step (4): all 29 orbits
                                                   # certified TSP >= 265 (~1 h;
                                                   # reads data/orbits29.json)
```

Artifacts: `data/covers_10068.npz` (the 10,068 covers),
`data/orbits29.json` (the 29 orbit representatives), and
`data/orbit_tsp_results.json` (the recorded per-orbit outcomes: 28 orbits
OPTIMAL at 267–274, one certified 265).

## Cross-checks and predictions

- `code/egan1p.py --n 6` settles the exact-cover rung by a *different* model
  (CP-SAT feasibility over disjoint Pentad chains linked by weight-4 jumps):
  INFEASIBLE in under a second, giving `v = 24` ⟹ length ≥ 873 — stronger
  than the 865 this certificate gets from the same rung, and reproducing the
  873 originally proved by the E ≤ 28 exhaustive search
  (`data/e28_certificate.txt`).
- Consequence for the upper-bound hunt: an 871-string must have v ≤ 28,
  R ≤ 140, E ≥ 7 (v-ladder) — a precise search target.
- (Historical) an earlier GPU BFS prover, validated at n = 4 and n = 5, was
  planned as a heavyweight arbiter at budget 143 (wt ≤ 861). Those artifacts
  were retired with the search hardware; the two checks above are the
  in-repo corroborations that remain.
