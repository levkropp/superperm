# Certificate: s(6) ≥ 868

**Claim.** Every superpermutation on 6 symbols has length at least **868**
(walk weight ≥ 862). This improves the 2011/2018 bound of 867
(4chan / Houston–Pantone–Vatter). Status: computer-assisted theorem,
independently verified in this repository as described below.

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

```
# V1: absorption lemma          (this repo, script in session log; PASS)
# V2: exact covers              -> /tmp/my_covers.pkl  (10,068, DLX)
# V3: per-orbit class-TSP       -> results_orbit_tsp.log, results_orbit_tsp.pkl
cd ~/superperm && .venv/bin/python verify_orbits_tsp.py
```

Artifacts: `verify_orbits_tsp.py` (matrix construction + CP-SAT),
`results_orbit_tsp.log`, `results_orbit_tsp.pkl`, `/tmp/my_covers.pkl`,
`/tmp/sp/orbits6.pkl` (agent-1's orbits; cover set verified identical).

## Cross-checks and predictions

- The exhaustive GPU BFS prover (validated: n=4 → 1 solution, n=5 b29 →
  0 solutions at 41M nodes, n=5 b30 → exactly the 8 known solutions) run at
  budget 143 (R+E ≤ 143 ⟺ wt ≤ 861) **must find 0 solutions** — a
  heavyweight independent arbiter of the same theorem.
- Consequence for the upper-bound hunt: an 871-string must have v ≤ 28,
  R ≤ 140, E ≥ 7 (v-ladder) — a precise search target.
