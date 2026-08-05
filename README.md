# superperm — a research notebook on shortest superpermutations

> My own working notebook on the shortest-superpermutation problem. What I do
> here is narrow and I want to be plain about it: I look for **clean lemmas and
> structural patterns**, prove them, verify them exhaustively against every
> known extremal string, and build **independent** re-derivations of results the
> field already holds. Currently at $n = 6$ (done) and $n = 7$ (open).

**[Lev's Lemmas — the proved results, in one place](notes/levs_lemmas.md)** ·
**[Notebook front page](https://levkropp.github.io/superperm/)** ·
**[Lay explanation](LAYPERSON.md)** ·
**[Verify it yourself](#verify-it-yourself)**

A *superpermutation* on n symbols is a string containing every permutation of
the symbols as a contiguous substring; s(n) is the minimal length. Known
exactly: s(1..5) = 1, 3, 9, 33, 153.

| n | lower bound | upper bound | status |
|---|---|---|---|
| 6 | 872 (preliminary, vlad-ds) | 872 (Houston 2014) | **probably done** |
| 7 | 5888 (Hunter & Raudvere, Lean) | 5906 (Egan/Houston 2019) | the open frontier |
| 8 | 46103 (Hunter & Raudvere, Lean) | 46204 | wide open |

## Status of the problem — read first

Parts of this repo were written when I believed s(6) ≥ 868 was new. Days
earlier, three stronger results had already landed publicly:

- **s(6) ≥ 869, s(7) ≥ 5888, s(8) ≥ 46103** — Hunter & Raudvere, Lean-4
  machine-checked, completing Zach Hunter's 2019 draft:
  [urdvr/superpermutations-hunter](https://github.com/urdvr/superpermutations-hunter)
- **s(6) ≥ 868, s(7) ≥ 5886** (all n ≥ 5) — Raudvere, Lean-4 machine-checked:
  [urdvr/superperm-coeff2](https://github.com/urdvr/superperm-coeff2)
- **s(6) = 872 exactly** — vlad-ds, computer-assisted, Python + certificate
  ledger (preliminary, audits invited): [vlad-ds/a6-872](https://github.com/vlad-ds/a6-872)

So my 868 is **not** a new bound, and this repo's best unconditional elementary
bound at n = 7 (5885) is **below** the published Lean-checked 5888. This is a
complementary independent route, not the state of the art. Headline claims in
older files ("first improvement since 2011/2018") should be read with that in
mind.

---

## The results

Five results, with proofs, verification counts, and an explicit *what it does
not give* for each: **[`notes/levs_lemmas.md`](notes/levs_lemmas.md)**.

| | result | status |
|---|---|---|
| **1** | **Split Identity** — `R = (n−1)v − A` | **[THM]** |
| **2** | **A-cost law** — `A` is exactly the free-slot count; accidents are E-neutral stitches | **[THM]** + **[MEAS]** |
| **3** | **Pentad Lemma** — at most five complete traversals chain, so `v = 120` ⟹ length ≥ 5895 at n = 7 | **[THM]** |
| **4** | **No n = 6 champion is split-free** — the shortest split-free 6-superpermutation is exactly 873 | **[EXH]** |
| **5** | **`A2`** — `comps ≥ v − S`, via the loop quotient's cycle rank | **[THM]** |

Two more that came out of the same machinery:

* **`CH3`** — `T ≥ S + comps + p − 1`, **ordering-free**, and the first such
  bound here to beat HPV: minimum **29** over all 10,068 n = 6 exact covers
  against HPV's 24, where 29 is the true n = 6 optimum. This corrects a
  long-standing entry in this repo claiming no ordering-free invariant could
  beat HPV. [`notes/pbound.md`](notes/pbound.md)
* **`FORCE`** — the free-join digraph has at most one *core* (length-forced)
  out-edge per state, landing on `start·b`. 1463/1463.

### Where n = 7 stands

With `A2` proved, `CH3 = v + p − 1` with no slack on real strings, so
`s(7) = 5906` is *exactly* the question **"is `v + p ≥ 143`?"** — `v ≥ 142` is
closed by `p ≥ 1`, and `v ≤ 141` is **open**. What is missing is a lower bound
on `p` without a residue-uniformity hypothesis; [`notes/pbound.md`](notes/pbound.md)
§§9–10 records every route tried and why each one bounces.

## The claim registry

Every claim in this repo carries a status tag — **[THM]** proved, **[EXH]**
exhaustive, **[ID]** identity, **[MEAS]** measured only, **[CONJ]** conjecture,
**[REF]** refuted, **[DEAD]** dead end — and

```bash
python3 code/lemmas.py
```

re-checks the whole registry against **44,564 census strings** and 108
constructed walks, exiting non-zero if any **[THM]** is violated on either
corpus. Refuted claims are kept, with the witness that killed them, so the same
dead ends are not walked twice. [`notes/lemma_arsenal.md`](notes/lemma_arsenal.md)
is the index.

## Verify it yourself

Everything needed is in this repo — total download < 1 MB of data.

```bash
pip install -r requirements.txt          # numpy, scipy, ortools

# the registry and the main gates (minutes)
python code/lemmas.py                    # every claim vs 44,564 strings
python code/pbound.py --quick            # CH3: minimum 29 over the n=6 exact covers
python code/freejoin.py                  # FORCE: core out-degree <= 1, 1463/1463
python code/a2hall.py                    # A2's four-count slack, identically 0
python code/rigidity7.py                 # Pentad Lemma + the v = 120 rung (>= 5895)
python code/census.py                    # the master identity on every string on disk

# n = 6 certificate chain (seconds to ~30 min)
python code/certify.py --string data/houston_872.txt --n 6
python code/verify_v1_absorption.py      # absorption lemma (+ 200 random walks)
python code/verify_v2_covers.py          # re-enumerate all 10,068 covers
python code/verify_orbits_tsp.py         # all 29 orbits certify TSP >= 265

# structure and search
python code/nbhd.py --n 6                # champion is a certified local minimum of CH3
python code/vlock.py                     # no n=7 champion can lower v by re-cutting
python code/chain_count.py               # Chain-Count Lemma
python code/coset_lemma.py               # 7 families of 120 loops; the forced-om threshold
python code/pentad_orbits.py             # Pentad sharpness on all 1008 orbits
python code/split_free_5889.py           # split-free s(7) >= 5889
python code/sby_ladder.py                # the SBY ladder: s(6)>=868, s(7)>=5885
```

CI runs the fast + moderate n = 6 checks on every push (see
[Actions](../../actions)).

## Repository map

- **[`notes/levs_lemmas.md`](notes/levs_lemmas.md)** — the five proved results.
  Start here.
- **[`notes/lemma_arsenal.md`](notes/lemma_arsenal.md)** — every ingredient with
  its status, plus the rung-by-rung deficit for each target bound, and the list
  of dead ends and retractions.
- `notes/` — the working notes, roughly in order of how load-bearing they are:
  [`split_identity.md`](notes/split_identity.md),
  [`pbound.md`](notes/pbound.md) (`CH3`, the `A2` proof, and the open `p`
  question), [`pentad_lemma.md`](notes/pentad_lemma.md),
  [`block_count_lemma.md`](notes/block_count_lemma.md) (the SBY identity, and
  §12g: no split-free 872), [`ordering.md`](notes/ordering.md) (which
  quantities are ordering-free, and the Inflation Lemma),
  [`second_order.md`](notes/second_order.md),
  [`a_cost_law.md`](notes/a_cost_law.md),
  [`champion_anatomy.md`](notes/champion_anatomy.md),
  [`constructor.md`](notes/constructor.md),
  [`m7_capacity.md`](notes/m7_capacity.md) (the n = 7 capacity work),
  [`ledger_model.md`](notes/ledger_model.md),
  [`s7_baseline.md`](notes/s7_baseline.md),
  [`a1_argument.md`](notes/a1_argument.md),
  [`5905_exclusion.md`](notes/5905_exclusion.md),
  [`swarm_stitches_findings.md`](notes/swarm_stitches_findings.md),
  [`sig2_vs_accidents.md`](notes/sig2_vs_accidents.md).
  ⚠️ [`cross_read_872lean.md`](notes/cross_read_872lean.md) is **unreliable** —
  its description of the vlad-ds method is wrong; see the warning at its top.
- `code/` — the model (`permgraph.py`, `superstruct.py`, `build.py`), the claim
  registry (`lemmas.py`), the corpus (`census.py`), the `CH3` machinery
  (`pbound.py`, `chainer.py`, `freejoin.py`, `gen2.py`), the `A2` work
  (`a2hall.py`, `a2case3.py`), the n = 6 certificate chain (`verify_*.py`,
  `orbit28.py`/`.c`, `splitfree6*.c`), and the n = 7 machinery (`rigidity7.py`,
  `pentad_orbits.py`, `coset_lemma.py`, `macro7.c`, `capacity_dp.py`).
- `data/` — Houston's 872, the cover list, orbit reps, the split-free
  certificate (`e28_certificate.txt`), the 2018 HPV paper, and `n7/`.
- `CERTIFICATE_868.md`, `LAYPERSON.md`, `REPORT.md`, `VALIDATION.md` — the
  s(6) ≥ 868 certificate, the lay write-up, and the older research log.

## References

- Anonymous 4chan poster, R. Houston, J. Pantone, V. Vatter, *A lower bound on
  the length of the shortest superpattern*, OEIS A180632 (2018).
- R. Houston, *Tackling the minimal superpermutation problem*, arXiv:1408.5108
  (2014).
- M. Engen, V. Vatter, *Containing all permutations*, Amer. Math. Monthly 128
  (2021).
- G. Egan, *Superpermutations* (gregegan.net) — constructions and the n = 7
  records.
