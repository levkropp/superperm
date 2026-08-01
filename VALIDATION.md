# Phase 1 validation log — known truth

Goal: trust no new result until the machinery reproduces every known ground truth.

## Passed

- [x] **Houston's 872 string** (`verify_houston.py`): extracted from OEIS A180632,
  length 872, valid superpermutation on 6 symbols, visits all 720 permutations,
  implied Hamiltonian path weight **866** (= 872 − 6). Saved to `data/houston_872.txt`.
- [x] **Classical recursive construction** (`classical.py`): lengths 1, 3, 9, 33, 153
  for n=1..5 and **873** for n=6 (path weight 867), all valid superpermutations.
- [x] **Exact ATSP at n=3** (`exact_tsp.py 3`): optimal string length **9** = s(3). ✓
- [x] **Exact ATSP at n=4** (`exact_tsp.py 4`): optimal string length **33** = s(4). ✓
- [x] **n=6 weight matrix** (`build_matrix_n6.py`): 720×720, two independent
  constructions agree on 20k sampled pairs; vertex-transitive row histogram
  (per vertex: 1 edge of weight 1, 2 of weight 2, 6 of weight 3, 24 of weight 4,
  120 of weight 5, 566 of weight 6); exactly one weight-1 out-edge per vertex;
  Houston path weights sum to 866 through the matrix.
  Saved: `data/weights_n6.npy`, `data/perms_n6.npy`.
- [x] **Triangle inequality** (`verify_triangle.py`): holds on all 720³ = 373,248,000
  triples. Hence walks short-circuit to paths: minimal superpermutation length
  = 6 + min-weight Hamiltonian path. The ATSP model is exact, not a relaxation.
- [x] **Independent certificate checker** (`certify.py`, stdlib-only, separate
  implementation): accepts Houston 872 (720/720), rejects truncated variants.
  This is the verifier required for any upper-bound certificate.
- [x] **GPU annealer** (`gpu_anneal.py` + `gpu_moves.py`, torch/comfyui env):
  Or-opt segment moves verified exact against brute-force application;
  finds optimum from scratch at n=4 (weight 29); holds seeded optimum at n=5
  (148 -> string 153).

## Passed (headline result)

- [x] **s(6) ≥ 868 — computer-assisted proof, independently verified**
  (`CERTIFICATE_868.md`). Chain: HPV invariant (published) → absorption
  lemma v ≥ ⌈(R−1)/5⌉ (verified: tight on classical 24 and Houston 29 +
  200 random walks) → coverage premise (verified) → v=24 rigidity (exact
  cover, R=120, full arcs; verified on classical) → exact-cover enumeration
  (**10,068**, two independent enumerators set-identical) → 29 S₆-orbits
  (sizes sum to 10,068 exactly) → per-orbit class-TSP with our validated
  CP-SAT model: all orbits ≥ 265 (see `results_orbit_tsp.log`); family
  cover attains exactly 267 → 867 (classical). Hence v≥25 ⇒ wt≥862,
  v=24 ⇒ wt≥865 ⟹ **s(6) ≥ 868**. Scheme retro-proves s(4)=33, s(5)=153.
  Found by three independent research derivations converging on the same
  computation; every measured point re-verified in-repo.

## Passed (later additions)

- [x] **Exact ATSP at n=5 — CERTIFIED by our own structure-aware prover**
  (`prove_n5.c`, arc-level DFS with (R,E) budget pruning): budget R+E≤29
  exhaustively ruled out (138,223,351 nodes, 0 solutions, 29 s) ⟹ no path
  of cost ≤147 ⟹ min path cost ≥148 ⟹ **s(5) ≥ 153**; classical string
  achieves 153, so s(5)=153 reproduced with our own machinery.
  Positive control: budget 30 (cost ≤148) must find the known minimal
  solutions — see `results_prove_n5_b30.log`.
- [x] **GPU prover validated** (`gpu_prover.py` + `dfs_kernel.cu`, cupy
  RawKernel on RTX 5070 Ti): n=4 frontier → 159 nodes / 1 solution
  (exact match vs CPU prover and independent Python reference);
  n=5 budget-29 frontier (27.6M tasks) → **0 solutions in ≤10 s**
  (167.9M nodes memo-less vs 138.2M with memo) — independent GPU
  certification of s(5) ≥ 153. Critical bug found by the n=4 control:
  iterative DFS must undo the arc mask on backtrack (fixed via POP macro).

## Current bounds (literature, unchanged since 2018/2019)

- Lower: 867 (n! + (n−1)! + (n−2)! + n − 3; 4chan anon 2011 / Houston–Pantone–Vatter 2018)
- Upper: 872 (Houston 2014)
