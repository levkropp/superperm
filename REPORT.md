# Attacking the minimal superpermutation length s(6) — work report

*Status: in progress. Bounds to beat: 867 ≤ s(6) ≤ 872.*

## 1. The problem and prior art

A superpermutation on n symbols is a string containing every permutation as a
contiguous substring; s(n) is the minimal length. Known: s(1..5) = 1, 3, 9,
33, 153. For n=6 the published bounds are:

- **Lower 867** = n! + (n−1)! + (n−2)! + n − 3 — anonymous 4chan poster (2011),
  formalized by Houston, Pantone, Vatter (2018) via the invariant
  `wt ≥ p + c + v − 2` (permutations, completed 1-cycles, entered 2-loops).
- **Upper 872** — Houston (2014), ATSP heuristic (thousands of examples known).

Nothing has moved since Feb 2019 (n=7 records). This project attacks the gap
with validated machinery and n=6-specific structure.

## 2. Foundations (all verified, `VALIDATION.md`)

- Permutation overlap graph: 720 vertices, edge weight = symbols to append.
  Triangle inequality verified on all 720³ triples → **min superpermutation
  length = 6 + min-weight Hamiltonian path** (exact, not a relaxation).
- Houston's 872 string: valid, path weight 866. Classical construction: 873.
- Exact ATSP reproduces s(3)=9, s(4)=33 (CP-SAT) and **s(5)=153 by our own
  structure-aware prover** (138M nodes, 29 s; positive control: finds the
  known cost-148 solutions at the next budget).
- Independent stdlib-only certificate checker (`certify.py`).

## 3. The arc decomposition (the compression lever)

Weight-1 edges partition the vertices into 120 1-cycles (rotations). Any path
= arcs (weight-1 runs) joined by jumps (weight ≥ 2), giving the exact identity

    cost = N + R − 2 + E,   R = #arcs, E = Σ(jump − 2)

so cost ≤ C ⟺ R + E ≤ C − 718, a two-parameter budget that makes exhaustive
search practical. Measured decompositions:

- classical n=6 (867): R=120, E=29 (all full arcs, 96 w2 + 18 w3 + 4 w4 + 1 w5)
- Houston (866): R=145, E=3 (25 cycles split, 141 w2 + 3 w3 jumps)

## 4. The prover architecture

- **CPU prover** (`prove_par.c`): arc-level DFS with (R,E)-budget pruning,
  E-lookahead, per-thread memo hash, root-splitting over 16 threads,
  checkpoint/resume (SPCK0002 format + Python reader), streaming generation,
  mmap'd frontier, MemAvailable-based sizing (no more OOM kills).
- **GPU prover** (`gpu_prover.py` + `dfs_kernel.cu`, cupy RawKernel on
  RTX 5070 Ti): per-thread iterative arc-DFS, global task cursor, zero-copy
  live counters, chunked VRAM uploads from a memmap'd frontier.
- **GPU annealer** (`gpu_anneal.py`): 200k-walker Or-opt memetic search for
  the upper-bound side (verified move deltas; holds seeded optima).

Validation gates all passed: n=4 (159 nodes / 1 solution, exact match CPU),
n=5 budget 29 (**0 solutions**, 167,934,229 nodes — GPU matches CPU exactly).

## 5. Structural findings (the n=6-specific part)

- **δ-jump graph**: the 120 1-cycles form a 6-regular digraph under proper
  weight-2 jumps (720 pairs, no self-loops). Houston's whole trick: proper
  δ-jumps *across* 2-cycles at weight 2 — refutes the naive "w2 stays in the
  2-cycle" hypothesis (recorded honestly in `notes/phase23_findings.md`).
- **z-invariant dead end**: extending HPV's invariant with 3-loops
  (`wt ≥ p+c+v+z−3`) fails — classical n=5 violates it; Houston enters zero
  3-loops under the surviving rule. Documented in `notes/phase23_findings2.md`.
- **The productive invariant (v-tracking)**: Houston is *tight* for HPV:
  866 = 720 + 119 + 29 − 2 with v=29 entered 2-loops. Any walk of weight
  ≤ 865 must have v ≤ 28; weight ≤ 860 needs v ≤ 23 < 24 (impossible — that
  is the 867 bound). The prover now tracks the entered-2-loop set (144 bits)
  and prunes `v > B − 119` — directly cutting Houston-style split-heavy
  branches at budget 143+.

## 6. Why the GPU isn't (yet) crushing the CPU

Honest analysis, since the numbers demand it (~250M–1.7B nodes/s GPU vs ~5M/s
on 16 CPU threads — good, but not the 100× intuition expects):

1. **Divergence**: every thread explores a differently-shaped subtree; warps
   execute the union of branch paths. Irregular backtracking is the worst GPU
   workload; CPUs are built for it.
2. **Memo**: the CPU's per-thread dominance hash (`(e, mask) → best R,E`)
   prunes ~20%+ of the tree; GPU v1/v2 has none — a global VRAM hash is
   planned but hash contention eats the gains at this size.
3. **Local-memory stacks**: 160-frame DFS stacks spill to DRAM; CPU holds
   them in L1.

The way to actually unlock GPU throughput is to make the search *regular*:
**frontier BFS as batched tensor ops** (expand = gather, filter = mask,
dedup = GPU sort/hash — the dominance relation made bulk-synchronous).
That design plays to the hardware instead of fighting it; it's the next
kernel iteration.

## 6b. Kernel v3 — BFS over arc-layers with global dedup (the real lever)

Reformulating the search as **BFS over arc-layers with global dedup after
every layer** (dedup key (mask, z, e) keeping min E — the dominance relation,
done globally instead of per-thread) changed the game:

- n=5 budget 29 certified with **41M nodes** vs 138M (CPU DFS with memo) /
  168M (GPU DFS memo-less) — 3.4–4× fewer nodes, and compounding with depth.
- Peak working set at n=5: 1.5M states (fits easily in VRAM).
- Memory regime: GPU expands in adaptive chunks; CPU RAM assembles/dedups.
- Gates: n=4 = 1 solution ✓, n=5 b29 = 0 solutions + CERTIFIED ✓.

Kernel v4 (in progress): fused-CUDA expansion kernel + on-GPU hash dedup
(exact keys, atomicMin on E — false-positive-free by construction) to keep
the whole BFS on-GPU at full rate.

## 7. The "lossy / 99.99%" question — candid assessment

Can we trade exactness for speed and claim "99.99% sure s(6) ≥ X"?

- **Bloom/sketch dedup is unsound for lower bounds**: a false positive prunes
  a state we never saw. To keep P(any false prune) ≤ 1e-4 over ~1e15 queries
  needs per-query error ≤ 1e-19 — no sketch gets there. A quantified but weak
  version exists ("we covered everything but an ε-fraction"), yet ε comes out
  far above 1e-4 at our scale.
- **Monte Carlo can only prove upper bounds**: sampling walks finds solutions;
  absence-of-witness claims need density of witnesses, and a single
  871-string is a unique needle — concentration arguments don't apply.
- **What is exact and fast**: LP/MIP dual certificates and exhaustive search
  with aggressive valid pruning. Our route stays exact; the probabilistic
  machinery (annealer) stays on the upper-bound side where it belongs.

## 8. Current runs and next steps

- GPU proof of budget 142 (reproducing s(6) ≥ 867 independently) — running.
- CPU worker phase on the same frontier — running, checkpointed.
- Next: budget 143 frontier (v-cap 24) → **new bound s(6) ≥ 868**;
  BFS-tensor GPU kernel for regular-op throughput; Phase 2 structural mining
  (outer automorphism of S₆, classification of the 872s).

## 9. Engineering lessons (for the record)

- Positive controls caught three proof-invalidating bugs: iterative-DFS mask
  not undone on backtrack; hash-table full → infinite probe; task-set
  truncation at the memory cap.
- mmap + truncating checkpoint = SIGBUS; checkpoints now write only
  header + done-map in place.
- numpy dtype without C-struct alignment = garbage tasks (the "crawl").
- Every heavyweight process must budget against *available* RAM, and only one
  giant allocation per machine at a time.
