---
layout: math
title: "The gain-one design, the kernel arithmetic, and the gain-two question"
---

# The gain-one design, the kernel arithmetic, and the gain-two question

*Status: external results **[EXT]** independently verified in this repo
(August 7, 2026); our measurements **[MEAS]**; the gain-two hunt is
in progress. Claims about Raudvere's `formal/` Lean development are as
reported by its README (no Lean toolchain here); every word-level claim
below was re-checked on this machine.*

## 1. The July–August 2026 construction wave

In the same two weeks that the lower bounds moved, the *constructions*
moved too — answering the long-standing conjecture that Egan's bound could
be beaten at every large n:

- **s(8) ≤ 46204** — Uku Raudvere, July 26
  ([thread](https://groups.google.com/g/superpermutators/c/TBZsctlczM4);
  [examples repo](https://github.com/urdvr/superpermutation-examples)).
- **s(9) ≤ 408,965, s(10) ≤ 4,037,046** — William Echols, July 27
  ([repo](https://github.com/WilliamEchols/superpermutations)), one day
  later, the same design.
- **s(n) ≤ Egan(n) − 1 for all n ≥ 8** — Raudvere's
  [`formal/`](https://github.com/urdvr/superpermutation-examples), a Lean
  development with a kernel-checked degree-8 base and a uniform
  certificate lift; concrete verified words through n = 13
  (s(11) ≤ 43,948,807, s(12) ≤ 522,910,088, s(13) ≤ 6,749,568,009).

So the upper-bound landscape is now: **Egan − 1 everywhere from n = 8 on**,
with n = 7 sitting at Egan − 2 (the 5906 champions) and n = 6 settled at
Egan − 1 = 872. This note translates the design into this repo's ledger
vocabulary and states exactly what is open.

## 2. The certificate model, in one screen

A word of the new design is a **certificate**:

- **Kernel**: `|K|` marked 2-loops, chained by `|K|−1` **hop doors** — each
  a cost-3 move `door(u,3) = u[3:] + u[:3] reversed` replacing a cost-2
  splice of its loop. The kernel loops are orbit-disjoint; their
  `(n−1)|K|` rotation classes are the **roots**.
- **Rows**: oriented 2-loops. Each row has one **parent orbit** (shared
  with its parent loop) and covers `n−2` **child classes**; the children
  partition the non-root classes exactly, and parent pointers form a
  forest rooted in the kernel.
- **Disabled splices** (optional): a cost-2 splice replaced by a cost-1
  orbit edge — this repo's **stitches** (the A-cost law, `a_cost_law`).

Raudvere's `certificate.py` compiles a certificate to the word
deterministically and validates every constraint; extraction is the
inverse. Both round-trips were re-run here **byte-exact** for the 5906
champion and Raudvere's 46204.

## 3. The kernel arithmetic

Counting classes: `|K|` kernel loops root `(n−1)|K|` classes; rows cover
the rest, `n−2` each. Hence

```
v(|K|) = |K| + ⌈ ((n−1)! − (n−1)|K|) / (n−2) ⌉  ≈  (n−1)(n−3)! − |K|/(n−2)
```

— **every n−2 kernel loops save one character** — and with the ledger
identity, `length = base(n) + T`,

```
T = (n−1)(v − (n−2)!) + (B + Y − A),   base(n) = n + n! + (n−1)! − 3 .
```

The arithmetic against reality:

| design | n | `|K|` | formula floor v | achieved v | T | length |
|---|---|---|---|---|---|---|
| Egan/Williams | 8 | 1 | 840 | 840 | 840 | 46205 |
| Raudvere | 8 | 6 = n−2 | 839 | 839 | 839 | 46204 |
| Echols/Raudvere | 9 | 7 | 5759 | 5759 | 5759 | 408965 |
| **5906 champions** | 7 | **18** | **141** | **142** | 142 | **5906** |
| split-free | 8 | 720 | 720 | T = B+Y ≥ 839 | ≥ 839 | ≥ 46204 |

Two things to notice. The split-free end (`|K| = (n−2)!`, no rows) meets
the kernel end *at the same T* — the block-count lemma's β-floor closes
exactly where the kernel arithmetic lands. And the **5905 question is
visible**: at n = 7 the floor for `|K| ∈ [15, 18]` is v = 141, but the
champions achieve 142. `s(7) = 5905` ⟺ "does a certificate at the floor
exist?" — one row short.

## 4. Verified in this repo (August 7, 2026)

- Echols' **408,965** word: `code/certify.py` — **VALID**, 362,880/362,880;
  ledger anatomy `v = 5759, A = 0, B = 7, Y = 0`, HPV-tight — the textbook
  gain-one vertex.
- Echols' **4,037,046** word: independent rank-bitmap scan — **VALID**,
  3,628,800/3,628,800 (0.1 s).
- Raudvere's **43,948,807** (n = 11) and **522,910,088** (n = 12) words:
  same scan — **VALID**, 39,916,800 and 479,001,600 permutations complete
  (1 s and 15 s). The liftable-structure check (kernel-cut groups = n−2,
  T3 hops = n−3, rooted exact cover) **passes** at n = 9, 10 and 11.
- **The whole lift pipeline, re-run here**: the search-free `fast_lift`
  from the degree-8 seed (hash matches the Lean-literal seed) regenerates
  the published certificates **row-set-identically** at every level through
  **n = 13** (43,545,588 rows) — the entire "for all n ≥ 8" mechanism,
  end to end, in 1.5 seconds.
- Raudvere's search engine, run here: a valid 872 at n = 6 in **0.07 s**.
- The 5906 and 46204 certificates: extraction → compilation round-trips
  byte-exact.
- Echols' word added to the verification corpus (`data/n9/408965-echols.txt`,
  `census.json`): the claim registry re-ran clean on 44,565 strings.

## 5. The gain-two question (= T ≤ 838 at n = 8, i.e. ≤ 46203)

Three routes, and only three:

1. **v = 838** — a kernel of `|K| = 12` pivot-8 loops (roots 84 classes,
   rows exactly 826), same block/stitch budget as Raudvere.
2. **v = 839, B+Y−A = 5** — Raudvere's cover with one fewer block or one
   stitch.
3. **v = 840, B+Y−A = −2** — all of Egan's loops, two net stitches (the
   5906's mechanism, `A = 8`).

The obstruction lives in the chain. A cost-3 door out of a *complete* loop
that lets the next loop also run full is exactly **om** (the repo's FORCE),
and om-chains of complete loops cap at **n−2** (CORECAP — 6 at n = 8). A
12-loop chain therefore needs **stitch-broken loops** whose fringe doors
link stretches of ≤ 6 complete loops. The 5906 shows the pattern at n = 7:
18 loops, 4 stitch sites, stretches [3, 3, 2, 3, 3] all ≤ 5. How rare such
kernels are: the n = 7 corpus came from **7 working kernels in 1,572,390**
palindromic candidates.

The arithmetic envelope (if a 12-loop chain with a row fill exists):

| `|K|` | stitches s | v | T = 7(v−720) + \|K\| − 2s | length |
|---|---|---|---|---|
| 12 | 0 | 838 | 838 | **46203** |
| 12 | 1 | 838 | 836 | 46201 |
| 18 | 3 | 837 | 831 | 46196 |

*The envelope assumes the row fill hits its floor; at n = 7 it misses by
one (the 5905 gap), so treat these as upper bounds on what the design
could give, not predictions.*

## 6. The hunt so far (August 7, 2026 — in progress)

**Stitch mechanics, pinned by replaying the 5906.** A stitch loop is a
kernel loop whose 6 entries split into a 4-entry traversed segment and 2
skipped entries; the skipped entries' splices are disabled (cost-1
fallback), and the 2 skipped classes are covered as child orbits of rows.
The class accounting at n = 8 is therefore `5040 = 7K + 6·rows − 2s`,
forcing **`K − 2s ≡ 0 (mod 6)`** — the integrality condition every gain-two
design must satisfy.

**The chain stage is complete.** At n = 8 the 720 pivot-8 loops partition
the 5040 classes, and every cost-3 swap door from a pivot-8 arc-end lands
in another pivot-8 loop, so chain feasibility reduces to distinct loops
plus the om-stretch cap. The cap was recomputed exhaustively: **exactly 6**
at n = 8 (CORECAP/Pentad). Consequences:

| `K` | stitches | est. length | chain exists? |
|---|---|---|---|
| 12 | 0 | 46203 | **no** — om-cap 6 (exhaustive) |
| 18 | 3 | **46203** | **yes** — stretches 2-4-4-5 |
| 24 | 3 | 46202 | **no** (exhaustive, 100,800 trials) |
| 30 | 6 | 46202 | yes |
| 36 | 6 | 46201 | yes |

**The fill stage is open.** The K=18 instance (126 roots, 6 slack classes,
4,920 columns, 820 rows, 36,981 candidate rows) resisted ~2.5M Python-DLX
nodes, ~70M C-DLX nodes, CP-SAT (420 s) and MILP within the first compute
budget — but plain DLX is demonstrably too weak for this cover family at
n = 8 (it cannot even recover the standard kernel's known cover), so this
is engine weakness, not evidence of infeasibility. What is proved: the
46204's cover cannot be *locally* repaired into the new kernel's cover —
the residual is global. A longer solve, or a smarter chain screen, is next.
**A fill would be a new record (46203); an infeasibility proof for the
820-row cover would be the first hard obstruction to gain-two.**

**The Hall/LP analysis (August 7) — why the fill fails, in numbers.** Two
relaxations of the K=18 instance, against the 5906's own fill as control:

- **Matching (Hall) level**: max-flow with loop-distinctness saturates
  **all 4,920 columns** — there is no Hall violator. Scarcity of candidate
  rows is *not* the obstruction. (Control at n = 7: saturates too, as
  expected of a feasible instance.)
- **Fractional exact cover (LP)**: the n = 7 control LP is feasible (sum
  124 = the champion's own count). The n = 8 LP is **feasible** (HiGHS
  interior-point, support 4,920, sum exactly **820.000** = the target row
  count).

**Verdict: the fill is unobstructed at every testable relaxation** —
matching saturates, and the fractional exact cover exists with the exact
row count. What makes it hard is integrality plus the rooted-forest
constraint, not any scarcity we can find. Two readings: (construction)
gain-two at n = 8 is probably *real* and merely needs a cluster-scale
solve — 46203 is the most likely place a record is currently hiding;
(lower bound) a clean "gain-two fills die at n ≥ 8" theorem cannot come
from scarcity or fractional arguments — it would have to live in the
integrality or the forest, so `s(n) = Egan(n) − 1` for all n ≥ 8 is now
the *less* likely side of the conjecture. The one relaxation never yet
tested is the forest (no engine reached a cover to check); that is the
only place a clean obstruction could still live.
The 5905 gap says the n = 7 fill missed its own floor by one row; whether
n = 8 misses by a hair or by a wall is the deciding fact.

**The forest probe (August 7) — also clean.** The rooted-forest constraint
was the last untested relaxation, and it yields nothing either:

- **Reachability**: every one of the 4,920 columns is reachable from the
  kernel through candidate parent links (depth ≤ 3; level sizes 6 / 1,363
  / 3,272 / 279). The champion's own n = 7 instance is shallower (depth
  ≤ 2) — the n = 8 instance's depth-3 tail (279 columns) is its hardest
  region, but far from starved (48 candidates each).
- **Scarcity by level**: the scarcest columns are the six stitch-slack
  classes (13 candidate rows each — the known pinch, the stitch-skipped
  classes), then level-1 columns at 15–16. Nothing anywhere near zero.
- A purpose-built forest-first exact-cover search (rows placed
  parent-first from the kernel, so every partial state is acyclic) failed
  to recover even the *n = 7 champion's own* cover within 2M nodes — while
  a control run with the champion's rows as the only candidates finds it
  in 125 nodes. So the fill's difficulty is engine weakness on this cover
  family (plain DLX likewise cannot recover the standard 46,204 cover),
  not a measurable obstruction.

**Brainstorm verdict.** Every testable relaxation of the gain-two fill is
clean: matching saturates, LP feasible at the exact row count, forest
fully reachable, scarcity nowhere near zero. The cover is simply hard
(NP-hard core: integral exact cover under a forest order). Two
consequences, stated plainly: the 46,203 word is probably *real* and
awaits a cluster-scale solve (or a port of the trade-repair machinery);
and no "gain-two fills die at n ≥ 8" theorem can come from cover theory —
the lower-bound side of `s(n) = Egan(n) − 1` at large n must come from
elsewhere.

## 7. What this does not say

- Nothing here bounds s(n) from below: the best lower bounds remain
  Hunter & Raudvere's Lean-checked 869 / 5888 / 46103 at n = 6, 7, 8.
- The Lean `formal/` development is reported, not re-verified here; the
  word-level evidence (through n = 10, verified independently) is
  consistent with it.
- The gain-two hunt at n = 8 is **open**; this note will carry the outcome
  either way.
