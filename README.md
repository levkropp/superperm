# superperm — shortest-superpermutation research

A research notebook on the shortest-superpermutation problem: clean lemmas
and structural patterns, proved, verified exhaustively against every known
extremal string, and used to build **independent** re-derivations of results
the field already holds.

**Everything is on the website: [levkropp.github.io/superperm](https://levkropp.github.io/superperm/)** —
the results with proofs, the lay explanation, the full notebook, and the
validation record. This repo is the code, data, and CI behind it.

A *superpermutation* on n symbols is a string containing every permutation
of the symbols as a contiguous substring; s(n) is the minimal length. Known
exactly: s(1..5) = 1, 3, 9, 33, 153.

| n | lower bound | upper bound | status |
|---|---|---|---|
| 6 | 872 (preliminary, vlad-ds) | 872 (Houston 2014) | **probably done** |
| 7 | 5888 (Hunter & Raudvere, Lean) | 5906 (Egan/Houston 2019) | the open frontier |
| 8 | 46103 (Hunter & Raudvere, Lean) | 46204 (Raudvere 2026) | Egan−1; gain-2 open |
| 9 | 408246 (HPV 2018) | 408,965 (Echols 2026) | Egan−1 |
| 10 | 4,032,007 (HPV 2018) | 4,037,046 (Echols 2026) | Egan−1 |
| ≥ 8 | … | **Egan(n) − 1 for all n ≥ 8** (Raudvere, Lean lift) | words through n = 13 |

This repo's s(6) ≥ 868 certificate was **not** the first — stronger results
(Hunter & Raudvere's Lean-checked 869, vlad-ds's preliminary s(6) = 872)
landed days earlier. It is an independent proof by an elementary counting
route, and every step is re-checkable here.
[The honest status page](https://levkropp.github.io/superperm/#where-things-actually-stand).

The upper bounds moved too (July 2026): Raudvere's 46204 at n = 8, Echols'
408,965 and 4,037,046 at n = 9, 10, and **s(n) ≤ Egan(n) − 1 for all n ≥ 8**
(Raudvere, Lean-verified lift) — the n = 9/10 words independently verified
on this machine. The design, translated into this repo's ledger vocabulary,
and the new open question — **gain-two at n = 8**, a 46203 — are in
[the gain-one note](https://levkropp.github.io/superperm/notes/gain_one_kernel).

## The results, in one breath

- **Split Identity** `R = (n−1)v − A` — **[THM]**, all n.
- **A-cost law** — `A` is exactly the free-slot count; accidents are
  E-neutral stitches — **[THM]** + **[MEAS]**.
- **Pentad Lemma** — at most five complete 2-loop traversals chain — **[THM]**.
- **No n = 6 champion is split-free** — the shortest split-free
  6-superpermutation is exactly 873 — **[EXH]**.
- **`A2`** — `comps ≥ v − S`, via the loop quotient's cycle rank — **[THM]**.
- **`CH3`** — `T ≥ S + comps + p − 1`, the first ordering-free bound to beat
  HPV (29 vs 24 over all 10,068 n = 6 exact covers) — **[THM]**.
- **`EGAN1P` / `PENTCAP` / `RUNGEQ`** — the exact-cover rung is excluded for
  champions at n = 6, 7, 8 (`v = (n−2)!` ⟹ length ≥ Egan(n): 873, 5908,
  46205), with a combinatorial reason, and the whole rung ladder reduced to
  one chain-length lemma — **[EXH]** + **[THM]**.

Proofs and the open `s(7) = 5906` question ("is `v + p ≥ 143`?"):
**[Lev's Lemmas](https://levkropp.github.io/superperm/notes/levs_lemmas)** and
**[the notebook](https://levkropp.github.io/superperm/notes/)**.

## Verify it yourself

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt

.venv/bin/python code/lemmas.py            # the claim registry vs 44,564 strings + 108 walks
.venv/bin/python code/pbound.py --quick    # CH3: minimum 29 over the n=6 exact covers
.venv/bin/python code/freejoin.py          # FORCE: at most one core out-edge per state
.venv/bin/python code/a2hall.py            # A2's four-count slack, identically 0
.venv/bin/python code/egan1p.py --n 7      # v = 120 => length >= 5908 (CP-SAT infeasible)

# the n = 6 certificate chain
.venv/bin/python code/certify.py --string data/houston_872.txt --n 6
.venv/bin/python code/verify_v1_absorption.py
.venv/bin/python code/verify_v2_covers.py  # re-enumerate all 10,068 covers
.venv/bin/python code/verify_orbits_tsp.py # 29-orbit class-TSP (the ~1 h one)
```

The full record of what was re-run, where, and what it found:
**[validation](https://levkropp.github.io/superperm/validation)**.
CI runs the certificate chain, the registry, and the fast gates on every
push (see [Actions](../../actions)).

## Repository layout

- `code/` — the model (`permgraph.py`, `superstruct.py`, `build.py`), the
  claim registry (`lemmas.py`), the CH3/A2 machinery, the n = 6 certificate
  chain (`verify_*.py`, `orbit28b.c`, `splitfree6*.c`), and the n = 7
  machinery (`egan1p.py`, `pentcap.py`, `rigidity7.py`, `macro7.c`, …).
- `data/` — Houston's 872, the cover list, orbit reps, the split-free
  certificate, the corpora.
  [Manifest](https://levkropp.github.io/superperm/data).
- `docs/` — the website (GitHub Pages).
- `.github/workflows/ci.yml` — the gates above, on every push.

## References

- Anonymous 4chan poster, R. Houston, J. Pantone, V. Vatter, *A lower bound
  on the length of the shortest superpattern*, OEIS A180632 (2018).
- R. Houston, *Tackling the minimal superpermutation problem*,
  arXiv:1408.5108 (2014).
- M. Engen, V. Vatter, *Containing all permutations*, Amer. Math. Monthly
  128 (2021).
- G. Egan, *Superpermutations* (gregegan.net) — constructions and the n = 7
  records.
