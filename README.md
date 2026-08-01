# The absorption lemma — an elementary proof that s(6) ≥ 868

> **An elementary, fully-verified proof that every superpermutation on 6
> symbols has length at least 868** — built from one counting idea (the
> absorption lemma) that both champion superpermutations saturate exactly.
> Independently discovered here; the bound was also reached days earlier by
> two machine-checked efforts (see the status note below).

**[Lay explanation](LAYPERSON.md)** · **[Full proof](CERTIFICATE_868.md)** · **[The absorption lemma](https://levkropp.github.io/superperm/absorption-lemma)** ·
**[Verification & reproduction](#verify-it-yourself)**

A *superpermutation* on n symbols is a string containing every permutation
of the symbols as a contiguous substring; s(n) is the minimal length. Known
exactly: s(1..5) = 1, 3, 9, 33, 153. For n = 6 the best published bounds
were 867 ≤ s(6) ≤ 872. This repository contains the complete machinery,
data, and scripts that establish the new lower bound, plus the research
log of how it was found (GPU provers, exact TSP machinery, structural
lemmas, and the dead ends that were ruled out).


## ⚠️ Status of the problem (July–August 2026) — read first

This repository was written when we believed s(6) ≥ 868 was new. Days
earlier, three stronger results had already landed publicly:

- **s(6) ≥ 869, s(7) ≥ 5888, s(8) ≥ 46103** — Hunter & Raudvere,
  Lean-4 machine-checked, completing Zach Hunter's 2019 draft:
  [urdvr/superpermutations-hunter](https://github.com/urdvr/superpermutations-hunter)
- **s(6) ≥ 868, s(7) ≥ 5886** (all n ≥ 5) — Raudvere, Lean-4
  machine-checked: [urdvr/superperm-coeff2](https://github.com/urdvr/superperm-coeff2)
- **s(6) = 872 exactly** — vlad-ds, computer-assisted (preliminary,
  audits invited): [vlad-ds/a6-872](https://github.com/vlad-ds/a6-872)

**What this repository is, then:** an *independent* proof of s(6) ≥ 868 by
a different method (absorption lemma + v=24 rigidity + exhaustive cover
TSP), with every step verified — a second, independent confirmation of a
bound the field now holds three ways. It is no longer the first proof of
that bound, and the headline claims elsewhere in these files ("first
improvement since 2011/2018") should be read with the date above in mind.

---

## The proof in one paragraph

In the permutation overlap graph (720 vertices; edge weight = symbols to
append), minimal length = 6 + min Hamiltonian path weight. The
Houston–Pantone–Vatter invariant gives wt ≥ p + c + v − 2 (permutations,
completed 1-cycles, entered 2-loops). Two new ingredients close the gap:

1. **Absorption lemma** — every 2-loop has exactly 5 generators, and jump
   targets enter a loop only by landing on one, so `v ≥ ⌈(R−1)/5⌉`
   (tight on both known extremal strings).
2. **Rigidity of v = 24** — 24 entered 30-vertex loops covering 720
   vertices must be an *exact cover*; each 1-cycle then has a unique
   "port" (generator), forcing R = 120 full arcs and
   `wt = 600 + TSP(cover)` over the 120 classes. All **10,068** exact
   covers (29 S₆-orbits) have class-TSP **≥ 265** (CP-SAT certified).

So: v ≥ 25 ⇒ wt ≥ 837 + 25 = **862**, and v = 24 ⇒ wt ≥ 600 + 265 =
**865**. Every complete walk has wt ≥ 862, hence **s(6) = 6 + wt ≥ 868**. ∎

The same scheme **retro-proves s(4) = 33 and s(5) = 153** exactly — the
strongest soundness check available.

## Verify it yourself

Everything needed is in this repo — total download < 1 MB of data. **No
gigabyte checkpoints are required**: the certificate is the 10,068-cover
list (80 KB compressed), 29 orbit representatives, and exact-solver runs
that take minutes on a laptop.

```bash
pip install -r requirements.txt          # numpy, scipy, ortools

# fast checks (seconds)
python code/certify.py --string data/houston_872.txt --n 6   # 872 is valid
python code/verify_v1_absorption.py      # absorption lemma (+ 200 random walks)

# moderate (a few minutes)
python code/verify_v2_covers.py          # re-enumerate all 10,068 covers
python code/verify_family_orbit.py       # class-TSP on the family orbit

# the full certificate (~30 min, 15 threads)
python code/verify_orbits_tsp.py         # all 29 orbits certify TSP >= 265
```

CI runs the fast+moderate checks on every push (see
[Actions](../../actions)).

## Repository map

- `CERTIFICATE_868.md` — the proof with every link in the chain.
- `LAYPERSON.md` — the result explained without prerequisites.
- `REPORT.md`, `VALIDATION.md` — the research log: machinery, findings,
  dead ends (including why every LP relaxation caps at 840, and why the
  outer automorphism of S₆ cannot help).
- `code/` — the verification scripts plus the full toolset: the overlap
  graph model (`permgraph.py`), exact ATSP (`cpsat_tsp.py`, `exact_tsp.py`),
  the CPU arc-prover (`prove_par.c`), and the GPU BFS prover
  (`gpu_bfs.py`) that certifies s(5) = 153 with 41M nodes and finds exactly
  the 8 known minimal solutions at the next budget.
- `data/` — Houston's 872 string, the cover list, orbit reps, the TSP
  results table, and the 2018 HPV lower-bound paper (PDF).
- `notes/` (in the research log repo) — structural findings: the δ-jump
  graph is the Coxeter Cayley graph of S₅ with an icosahedral 24-block
  quotient; the v-ladder constraining any 871-string to v ≤ 28, E ≥ 7.

## Ongoing: s(7) (5888 ≤ s(7) ≤ 5906)

The same machinery is now pointed at n=7 — see
[`notes/s7_baseline.md`](notes/s7_baseline.md): the absorption lemma holds
at n=7 (840 2-loops, 6 generators each) and the decomposition of all three
known champions shows the 5906 record is the only known string anywhere
that does *not* saturate it (v=142 vs floor 141) — the signature of the
non-standard kernel, and the first thing to understand.

## What would move the bound next

- **869**: the v = 25 channel (R ≤ 125) or GTSP-min over all covers
  (~6 CPU-hours with the beam route sketched in REPORT).
- **871/872 (settling s(6))**: the exact 720-city ATSP has never been
  solved to optimality (Concorde crashed in 2014); the instance is in
  `data/` (weights matrix) — a certified optimum of 866 would prove
  s(6) = 872 exactly.

## References

- Anonymous 4chan poster, R. Houston, J. Pantone, V. Vatter, *A lower
  bound on the length of the shortest superpattern*, OEIS A180632 (2018).
- R. Houston, *Tackling the minimal superpermutation problem*,
  arXiv:1408.5108 (2014).
- M. Engen, V. Vatter, *Containing all permutations*, Amer. Math. Monthly
  128 (2021).
- G. Egan, *Superpermutations* (gregegan.net) — constructions and the
  n = 7 records.
