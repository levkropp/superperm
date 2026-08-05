# The lemma arsenal

Everything this repo can currently *use* as an ingredient, in one place, with
an explicit status on each item. The point is to stop re-deriving things, to
stop re-trying dead routes, and to have a single surface to brainstorm against.

**Status tags.**

| tag | meaning |
|---|---|
| **[ID]** | exact identity, proved by bookkeeping |
| **[THM]** | proved (algebra or finite exhaustive check), machine-asserted here |
| **[EXH]** | established by exhaustive computation in this repo |
| **[EXT]** | external result, not proved here |
| **[CONJ]** | conjecture with evidence, not proved |
| **[MEAS]** | measured on known strings only — no proof, may be a construction artefact |
| **[DEAD]** | tried and does not work; recorded so it is not retried |
| **[RETRACTED]** | was claimed here and is false |

---

## 0. Objects and notation

A minimal superpermutation of length L over n symbols is a Hamiltonian path in
the overlap digraph on the n! permutations, where `weight(u,v) = ` the number
of symbols to append to u to reach v. Along the path:

* **arc** — a maximal run of weight-1 steps. An arc lies inside a single
  **rotation class** (the n cyclic rotations of a permutation); a *full* arc
  covers all n of them. `R` = number of arcs.
* **rotation class** — `(n−1)!` of them. `σ(u) = u[1:]+u[:1]`.
* **2-loop** — the orbit of a permutation under σ and δ, where
  `δ(u) = u[2:]+(u[1],u[0])`. It has n(n−1) permutations and exactly
  **n−1 generators** (arc starts), one per each of its n−1 classes.
  There are `n!/(n−1)` two-loops. `v` = number entered.
* **block** — a maximal run of arcs joined by weight-2 jumps. `B` = count.
* **clean run** — a maximal run of arcs joined by *clean* weight-2 jumps (δ out
  of a **full** arc). `N` = count. A clean run lives in one 2-loop at
  consecutive generators. `dirty` = weight-2 jumps out of a partial arc.
* **splits** `S = R − (n−1)!` — extra arcs beyond one per class.
* **accidents** `A` — generators of entered loops covered mid-arc.
* `Y = Σ(weight − 3)` over the costly (weight ≥ 3) jumps.
* `E = Σ(weight − 2)` over all jumps; `T = S + B + Y`.
* Group elements: `c = σ`, `d = δ`, `a = c^(n−1)d` (order n−1, the
  arc-to-arc step), `b = (3,4,…,n−1,2,1,n)` (**om**, the class-disjoint
  weight-3 exit), `s = a^(n−2)b` (order **n−2**, the *Pentad* element),
  `u = a^(n−3)b`, `H = ⟨a,b⟩` (order (n−1)!).

---

## 1. Identities — all [ID], all machine-asserted on 604+ walks

Asserted by `code/blockcount.py:Model.measure` and `code/dirty.py:dissect`.

1. **Arc/jump.** `length = n + n! − 2 + R + E`.
2. **Split Identity.** `R = (n−1)v − A`, equivalently
   `S = (n−1)(v − (n−2)!) − A`. (`notes/split_identity.md`; proof is a
   three-way case split on how each generator of each entered loop is visited.)
3. **SBY.** `length = n + n! + (n−1)! − 3 + S + B + Y = base_n + T`.
   `base_6 = 843`, `base_7 = 5764`.
4. **Block/run.** `N = B + dirty`, `N = Σ_L r_L`, `R = Σ_L a_L`,
   `f = #{runs of length n−1} = #{L : a_L = n−1 and r_L = 1}`.
5. **E vs T.** For split-free walks `E = (B−1) + Y` and `T = B + Y = E + 1`.
6. **Partial arcs end runs** **[THM]**. A clean run's non-final arcs are all
   full, so a partial arc can only be the **last** arc of a run. Hence
   `N ≥ n_partial`, while also `dirty ≤ n_partial` — the fragmentation a split
   causes and the free loop switch it buys are bounded by the *same* quantity.
   Also `n_partial = S + m`, with m = #classes covered more than once, m ≤ S.
7. **The split ledger.** Writing `ν = N − n_partial ≥ 0`,
   > `T = S + Y + ν + (n_partial − dirty)`.

   Split-free walks have `n_partial = 0`, so `T = N + Y`: they pay the full run
   count. Splitting lets `n_partial` absorb runs, shrinking ν at a cost of S.
   Checked on every known string (`code/split_economy.py`).

**Consequences worth having at hand.**

* `s(6) = 872` ⟺ `T = 29`; `s(7) = 5906` ⟺ `T = 142`.
* Split-free `n = 6`: `length = 844 + E`. Split-free `n = 7`: `length = 5765 + E`.
* **`v = (n−2)!` ⟹ split-free.** `R ≥ (n−1)!` always (every class needs an
  arc), and `R = (n−1)v − A = (n−1)! − A`, so `A = 0`, `R = (n−1)!`, `S = 0`.
  The converse fails: split-free only gives `v = (n−2)! + A/(n−1) ≥ (n−2)!`.

---

## 2. The core inequalities

| # | statement | status |
|---|---|---|
| 2.1 | **Absorption.** `A ≥ 0`, i.e. `R ≤ (n−1)v`, i.e. `v ≥ ⌈R/(n−1)⌉` | **[THM]** |
| 2.2 | **Covering.** `v ≥ (n−2)!` and `R ≥ (n−1)!` | **[THM]** |
| 2.3 | **HPV.** `T = S + B + Y ≥ v` | **[EXT]**, re-verified here |
| 2.4 | **Run cap.** every clean run has ≤ n−1 arcs (ord(a) = n−1) | **[THM]** |
| 2.5 | **Loop cap.** `a_L ≤ n−1`; two runs of length n−2 cannot share a loop | **[THM]** |
| 2.6 | `dirty ≤ n_partial`, and `clean ≤ R − v` | **[THM]** |
| 2.7 | **Ordering-free bound.** `B ≥ comps`, hence `T ≥ S + comps`. **False as stated** (2.7d) but **valid against the optimum** (2.7f): the minimum length is attained at `σ2 = 0`, where it does hold. `min(S + comps) = (n−2)!` — equal to HPV, but this does **not** mean no ordering-free invariant beats HPV; see 2.7g. [`notes/ordering.md`](ordering.md) | **[REF]** as stated; **[THM]** against the optimum |
| 2.7g | **CH3 — an ordering-free bound that BEATS HPV.** `CH2` adds a second ordering-free term, `p` = fewest free chains covering the δ-components, with `Y ≥ p−1`; with `B ≥ comps` (valid against the optimum by `SIG2X`) this gives **`T ≥ S + comps + (p−1)`**. Measured: **0 violations** and **1,029/1,030 exactly tight** on the n = 6 census; **minimum over all 10,068 exact covers = 29**, the true n = 6 optimum, against HPV's **24** at the same rung. At an exact cover it equals `(n−1)(n−3)! − 1`, the Egan−1 line, without Chain-Count's or `S5`'s hypotheses. `code/pbound.py`, [`notes/pbound.md`](pbound.md) | **[THM]** |
| 2.6a | **Free-Jump Inequality (A1u), no hypothesis.** With `k = B+Y−A`, ID1 gives `T = (n−1)d + k`; feeding `d = (T−k)/(n−1)` into HPV `T ≥ (n−2)! + d` gives `(n−2)T ≥ (n−1)(n−2)! − k`, i.e. **`T ≥ (n−1)(n−3)! − k/(n−2)`** — *saving `s` characters over Egan costs `B+Y−A ≥ (n−2)s`*. This is A1 without its HPV-tight hypothesis. Holds on all 44,672 rows, **exactly tight on 43,740** including **every record**: n=6 needs 4 has 4, n=7 needs 10 has 10, n=8 needs 6 has 6. So the n=7 champion invariant `B+Y−A = 10` is *forced*. A new n=8 record at 46203 needs `B+Y−A ≥ 12`. | **[THM]** |
| 2.6b | **Kick Identity / Kick Bound.** A *kick* = weight-2 jump out of a full arc (next village of the same 2-loop) = `clean` = `R − N`. Then `kicks = (n−1)! + 2S + Y − T − dirty`, hence **`kicks ≥ (n−1)! − T + Y`** with equality iff `dirty = 2S`: **every character saved costs at least one extra kick**. Egan uses exactly `(n−1)! − (n−2)! − (n−3)! + 1` (= 17, 91, 577, 4201, 34561 at n = 5…9). [`notes/second_order.md`](second_order.md) §E | **[THM]** |
| 2.6c | **`B = 1` ⟹ `Y = 0`, `T = S+1`, `F = 0`** (n ≥ 4). Corollary: the Exposure Bound is **identically vacuous on Egan**, which is why Egan sits *on* the Egan−1 line. The `comps = 1` clause came from 2.7 and is **withdrawn** (witness: a length-5914 walk with `B = 1`, `comps = 2`). 188/188 | **[THM]** |
| 2.7b | **S1 (δ-cycle lemma).** A *saturated* loop (all n−1 generators are arc starts) whose arcs are all *full* closes into a δ-cycle, so `F := #(all-full saturated loops) ≤ comps`. Tight on every exact-cover walk. The old second half `comps ≤ B` was 2.7 and is withdrawn. [`notes/a1_argument.md`](a1_argument.md) | **[THM]** |
| 2.6d | **Single-block bound (BLK1–3).** `B = 1` ⟺ the string is a word in `{σ, δ}` (σ appends 1 char, δ appends 2 and its intermediate window is *not* a permutation, so δ always wastes exactly one char; `R = W + 1` with `W` = wasted chars). Then `B1` + Split Identity + HPV give `(n−2)d ≥ (n−2)! + A − 1`, hence **`d ≥ (n−3)!`** and **`T ≥ (n−1)(n−3)!`** — Egan's `T`. **Corollary: every superpermutation shorter than Egan(n) has `B ≥ 2`**, the `k=0` base case of 2.8/A1 without HPV-tightness. At equality `d = (n−3)!` and `A = 1` are *forced* — the repaired half of `A1EQ`. 188/188. [`notes/ordering.md`](ordering.md) §5 | **[THM]** |
| 2.7d | **SIG2 / IN5b — the two weight-2 successors.** `weight(u,v) = 2` forces `v = u[2:] + {u[0],u[1]}`, so `v ∈ {δ(u), σ²(u)}` — **two** targets, and `comps` follows only `δ`. A `σ²` jump out of arc `i` requires the arc at `σ(end_i)` to have **length 1**, so none ever leaves a full arc. Repaired bound: **`B + σ2 ≥ comps`** with `σ2 ≤ #(length-1 arcs)`. Measured: **0 σ² jumps in 44,564 strings**, though 92 contain a length-1 arc — available, never taken. [`notes/ordering.md`](ordering.md) | **[THM]** |
| 2.7f | **SIG2X / SIG2Y — the σ² exchange.** If arc `A_p` ends at `e` and jumps `σ²` to `A_{p+1}`, the length-1 arc at `σ(e)` can be spliced out of its own slot and the three arcs merged into one: `R → R−2`, `Δlength = w(X,Z) − w1 − w2 ≤ 0` by subadditivity. `R` strictly falls and `R ≥ (n−1)!`, so **every walk has one of length ≤ it with `σ2 = 0`** — the minimum is attained there and **2.7 is valid against the optimum**. At an optimum the move is length-neutral, so `w(X,Z) = w1+w2 ≥ 4`: two jumps become one of weight ≥ 4, hence **an optimum with `σ2 ≥ 1` forces an optimum with strictly larger `Y` and `B`**. Scanning n = 6: 808 of the 43,096 optima carry a weight-≥4 jump, **0** admit the reverse move. `code/sig2x.py` | **[THM]** |
| 2.7e | **ORD / Inflation Lemma.** `R, S, v, d, A, comps, m, μ_max, n_partial` are ordering-free; `B, Y, T, clean, dirty, N, length` are not. Any walk with `B < R` reorders to `B+1`. **Audit rule: no ordering-free hypothesis can upper-bound `B`, `Y` or `T`** — only lower bounds survive. [`notes/ordering.md`](ordering.md) | **[THM]** |
| 2.7c | **Exposure Bound (S5).** With `F` = #all-full saturated loops, `F ≤ (n−2)(1+Y+B−F)` and hence `T ≥ S + ⌈(n−1)F/(n−2)⌉ − 1`, **ordering-free**. At the exact cover (`F = (n−2)!`, `S=0`) it gives exactly `(n−1)(n−3)!−1` — the Chain-Count value **without** the split-free hypothesis. 1463/1463 | **[THM]** |
| 2.8 | `comps ≥ v − S` ⟺ `S + B ≥ v` ⟺ **`T ≥ v + Y`** ⟺ `dirty ≤ S + N − v`. This is §11's schema at **ε = Y**; strengthens HPV only where `Y > 0`, so it does not move the binding rungs. 285/285 on both corpora | **[CONJ]** |

Absorption is tight on both n = 6 extremal strings and on two of three n = 7
records; the 5906 champion sits **one above** the absorption floor (v = 142 vs
141) — the only known case anywhere of the frontier dipping below the diagonal.

---

## 3. Structure of the transition graph

### 3.1 The exit table — **[THM]**, `code/exit_table.py`

From an arc end there are exactly **n** weight-3 targets. For a block of length
l, each target carries a hard **cap** on the next block's length. Sorted caps:

| n = 6, l = | caps | | n = 7, l = | caps |
|---|---|---|---|---|
| 1 | `0 3 4 5 5 5` | | 5 | `0 0 4 5 5 6` |
| 2 | `0 2 4 5 5 5` | | 6 | `0 0 0 4 4 6` |
| 3 | `0 1 4 5 5 5` | | | |
| 4 | `0 0 3 4 4 5` | | | |
| 5 | `0 0 0 3 3 5` | | | |

### 3.2 Forced-om threshold — **[THM]**, derived not asserted

A weight-3 jump from a run of length l to a run of length l′ has a **unique**
admissible exit — necessarily **om** — exactly when

> **l + l′ ≥ 2n − 3.**

n = 7: (6,6), (6,5), (5,6). n = 6: (5,5), (5,4), (4,5). **Not (5,5) at n = 7,
not (4,4) at n = 6.** See §8 for the retraction attached to this.

### 3.3 The Coset Lemma and families — **[THM]**, `code/coset_lemma.py`, `code/families6.py`

`H = ⟨a,b⟩ = ⟨s,u⟩` has order `(n−1)!` and index n. The δ step between
consecutive arc starts **is right multiplication by a** (checked on all n!
permutations). Therefore:

* a 2-loop is a coset `g⟨a⟩`;
* the `n!/(n−1)` loops fall into the **n cosets of H — the FAMILIES** — of
  `(n−2)!` loops each;
* `|H|` is coprime to `n = |⟨c⟩|` and classes are cosets of `⟨c⟩`, so **each
  family is an exact cover of the (n−1)! classes**: one arc start per class.

n = 6: 144 loops = 6 × 24. n = 7: 840 loops = 7 × 120.

**Reformulation.** A split-free walk **is** an n-colouring of the (n−1)!
classes (colour of C = which family supplies C) plus an ordering; v and B are
functions of the colouring alone. Monochromatic gives B = (n−2)!; random
colourings at n = 6 give B ≈ 86 against a budget of 29.

### 3.4 Splits are never intra-family — **[THM]**, `code/n7_families.py`

A family meets each class once and a minimal walk visits each permutation once,
so two arcs whose starts share a family lie in **different** classes. Hence:

* the arcs covering one class have pairwise **distinct** families;
* a class is covered by at most **n** arcs;
* `arcs from family f = classes covered from family f`, exactly;
* `A` splits as `A_f = (n−1)ℓ_f − c_f ≥ 0`.

Checked on all 140 known n = 7 strings. Empirically no champion has a class
covered more than 3 times.

### 3.5 Pentads — **[THM]**, `code/pentad_orbits.py`

`ord(s) = n − 2`. An `⟨s⟩`-orbit of loops (a **Pentad** at n = 7: 5 loops) has
its loops **pairwise class-disjoint**, covering `(n−1)(n−2)` classes. At n = 7
all 1008 orbits verify this, and **24 disjoint orbits exactly partition the 720
classes**.

> **Read `ord(s) = n − 2` narrowly.** `s = a^{n−2}·b`, so the statement
> "om-chains cap at `ord(s)`" applies only to chains in which **every block has
> that one length**. §2.7c/`S5` is sound because all-full loops are uniform
> (`n−1` arcs each). Generalised to arbitrary blocks it is **false**: the 5906
> champion has block sizes `4…306`, every free join above the forced-om
> threshold and therefore om, and yet all 18 components chain into a single free
> chain. Registered as `PFLOOP` **[REF]** — 171 violations — after it was used
> to try to bridge `v` to `p` for `CH3`. See [`notes/pbound.md`](pbound.md) §5.

### 3.6 The om-stretch primitive ρ(c) — **[EXH]**, `code/omstretch.c`/`.py`

Inside an om-stretch all generators lie in one coset of H, so a stretch is a
simple path in `Cay(H; {a,b})`: `g→g·a` continues a run free, `g→g·b` costs a
run. `ρ(c)` = fewest runs covering c classes. Vertex-transitive, so WLOG start
at the identity; the **arc bound** (unvisited vertices of a loop form maximal
a-arcs, each needing its own run) is what makes it close.

`ρ(24) = 8` (n=5), `ρ(120) = 31` (n=6), `ρ(720) ≥ 128` (n=7, K = 120…127
certified impossible). n = 6 partial: ρ(20,25,40,60,80,100,110,120) =
4,6,9,14,19,24,27,31.

---

## 4. Counting lemmas

### 4.1 Block-count / per-loop refinement — **[THM]**, `code/loop_runs.py`

Complete traversals are *loops*, not free parameters. With `N = Σ r_L`,
`R = Σ a_L`, `f = #{L : a_L = n−1, r_L = 1}` and packing conditions on how a
loop's arc starts partition into runs, the ladder is:

| n | v = (n−2)! | +1 | +2 | +3 | ⟹ |
|---|---|---|---|---|---|
| 5 | 7 | 7 | 8 | 9 | **153** (exact) |
| 6 | **27** | 25 | 26 | 27 | **868** |
| 7 | **131** | **121** | 122 | 123 | **5885** |

The n = 5 gate returning exactly 7 is the soundness check that matters.

### 4.2 Chain-Count Lemma — **[THM]** but narrow, `code/chain_count.py`

For a split-free walk in which **every block is a complete traversal**
(equivalently `B = v = (n−2)!`): chains of complete traversals are `⟨s⟩`-orbits
so cap at n−2, giving

> `Y ≥ (n−3)! − 1`, `T ≥ (n−2)! + (n−3)! − 1`,
> `length ≥ n! + (n−1)! + (n−2)! + (n−3)! + n − 4`.

= 33, 153, 872, **5907** at n = 4, 5, 6, 7 — exactly s(n) where known, and one
*more* than 5906. So conditional on s(7) = 5906, **no 7-symbol champion is
split-free with all blocks complete traversals.**

**General form** (any split-free walk): a chain is broken by **any**
non-complete block, since the om step out of a length-l block is `a^(l−1)b`,
a different group element per l. So

> `c_{n−1} ≤ (n−2)·(1 + Y + (B − c_{n−1}))`,

which at n = 6, B + Y = 29 reduces to `c_5 ≤ 24` — already implied by
`5c_5 ≤ 120`. **The chain count is vacuous away from B = (n−2)!.**

---

## 5. Exhaustive computational results

| result | scope | status |
|---|---|---|
| **corpus repaired**: `census.py` read only the first line of each file; reading every line takes it from 177 to **44,564** strings (n=5: 188, n=6: 44,126, n=7: 245). [`notes/champion_anatomy.md`](champion_anatomy.md) | n = 5..9 | **[EXH]** |
| **n = 6 has 44,121 optima in 8 coordinate vectors** with `A ∈ {0,2,3,4,5}` — and **every one sits exactly on the Egan−1 line** `v+Y = 29`. n = 7 has 237 optima in 9 vectors, `d = 22`, `Y = 0`, `B = 10+A`, `S = 132−A`, and **every one is past the line** at `v+Y = 142` | n = 6, 7 | **[EXH]** |
| **being past the Egan−1 line is a property of n, not of a string** — 0/44,121 at n = 6 (and 872 is optimal, so none can be), 237/237 at n = 7. There is no exceptional string to dissect; the discontinuity is between n = 6 and n = 7 | n = 6, 7 | **[EXH]** |
| **`A ≢ 3 (mod 4)` at n = 7**: `A ∈ {8,9,10, 12,13,14, 16,17,18}`, groups of three spaced by `n−3`. At n = 6 only `A = 1` is missing | n = 6, 7 | **[MEAS]** |
| **all 43,096 n = 6 optima measured** (`872-treelike.txt.gz` 42288 + slack1 772 + slack2 36; `code/champions6.py`). Only **three** coordinate vectors exist, on one line `S = 5d, B = 24−4d, Y = 5−d, A = 0`: (d,A,S,B,Y) = (5,0,25,4,0)×42288, (4,0,20,8,1)×772, (3,0,15,12,2)×36 | n = 6 | **[EXH]** |
| **`v + Y = 29` and `T = v + Y` on every one of the 43,096** — so `T ≥ v+Y` (§2.8) is *tight at every optimum* and can never separate one from a near-miss | n = 6 | **[EXH]** |
| **`B = comps` at every optimum** — an optimum saturates the δ-graph, using every free edge available (43,266/43,266 plus all census records) | n = 5..9 | **[CONJ]** |
| **the Egan−1 Law** `v + Y ≥ (n−1)(n−3)!−1`, i.e. with §2.8 `s(n) ≥ Egan(n) − 1`: **equality** at the n = 5, 6, 8, 9 records and on all 43,096, **refuted only by 5906** (142 vs 143). 5906 is the unique object known anywhere that beats Egan by more than one character | all n | **[REF]** |
| **`F` is the chain-count exposure, and champions minimise it**: `F = 120` at the n=7 exact cover, `F ∈ 2…19` (mostly 4–6) at n=7 optima, `0…8` at n=6 optima, and `F = 0` for Egan at every n. The Exposure Bound is slack by ~19× at the champion, so a *lower* bound on F would be needed to beat HPV there — and the spectra show none can be strong | n = 5..7 | **[MEAS]** |
| **Free-Jump Lemma.** HPV-tight with length `Egan(n) − k` ⟹ `B+Y−A = (n−2)k` and `costly jumps = B−1 = (n−2)k + A − Y − 1`. Egan itself has **B = 1, zero costly jumps** at every n; beating it means *buying* weight-3 jumps | all n | **[THM]** |
| **two-corpus lemma harness** — `code/lemmas.py` over `data/census.json` (177 records) + `data/walkpool.json` (108 constructed walks); every claim tagged, `[THM]` violations fail the run | n = 5..9 | **[EXH]** |
| `μ_max ≤ 3` (no class covered more than 3 times) now holds on **285/285** including badly suboptimal walks, not just champions | n = 5..7 | **[MEAS]** |
| **constructor framework** — `census.py` (182 strings, master identity 182/182), `superstruct.py` (n-generic structure, self-checked n=5..8), `build.py` (arc-list design, round trip + independent coordinates on 179 strings), `mcolour.py` (set-valued colouring search). [`notes/constructor.md`](constructor.md) | n = 5..9 | **[EXH]** |
| **cost collapse**: `T = S + 1 + sum f(w)`, `f(w) = max(0, w−2)` — with cuts fixed the problem is an asymmetric TSP on R ≈ (n−1)! **arcs**, not n! permutations | all n | **[ID]** |
| every **Egan** string measured (873, 5908, 46205, 408966) sits at `A=1, B=1, Y=0, d=(n−3)!` — a single block. The abstract complete-traversal vertex (`d=0`) is a *different* point, realised by n=9 409113 with `Y=867 ≥ (n−3)!−1` | n = 6..9 | **[EXH]** |
| champions are ~98% free jumps: costly jumps are 3/144, 17/843, 5/5872 at n = 6,7,8 | n = 6..8 | **[MEAS]** |
| **ledger model**: `T = (n−1)d + (B+Y) − A` with `d = v − (n−2)!`; saving over Egan `= (B+Y−A)/(n−2)` under HPV-tightness. [`notes/ledger_model.md`](ledger_model.md), `code/ledger.py` | all n | **[ID]** |
| `B+Y−A ≡ 10` on all 169 measured n=7 champions, invariant while A and S scatter | n = 7 | **[ID]** |
| **Balance Bound** at the exact-cover rung: `T ≥ ⌈(2(n−1)(n−2)! − (n−2))/(2n−3)⌉`, i.e. `g₀ ~ (n−3)!/2` — half of Egan's excess, closed form | all n | **[THM]** |
| **Rung Bound**: `T ≥ ⌈(2(n−1)(n−2)! − (n−1)(4n−9)d − (n−2))/(2n−3)⌉`; derived collapse slope `(n−1)(4n−9)/(2n−3) ~ 2n−3`; exact on all six searched n = 8 rungs | all n | **[THM]** |
| HPV-tight frontier `d_min = 1, 1, 5` at n = 6,7,8 (n = 9 sweep: `d ≤ 15` excluded, closed form predicts 22) | n ≤ 8 | **[EXH]** |
| ladder at n = 8 (never previously run): rungs 775, 763, 751, 738, 726, 713 ⟹ `s(8) ≥ 46090` | n = 8 | **[EXH]** |
| `s(6) ≥ 868` from the SBY ladder, no cover enumeration | n = 6 | **[EXH]** |
| all 29 exact-cover orbits have class-TSP optimum ≥ 267 ⟹ **no n = 6 champion is split-free with B = 24** | n = 6 | **[EXH]** |
| orbit 28 optimum is exactly 267 (2.4×10¹⁰ nodes, `code/orbit28b.c`) | n = 6 | **[EXH]** |
| no split-free n = 6 walk with E ≤ 26, and ≤ 27 (partial) | n = 6 | **[EXH]** |
| **no split-free walk has E ≤ 28** ⟹ split-free ⟹ length ≥ 873, so **no 872 champion is split-free** (2203 leaf verdicts, 2.98×10¹³ nodes) | n = 6 | **[EXH]** |
| 10068 exact covers of the 120 classes by 24 loops; 29 relabelling orbits | n = 6 | **[EXH]** |
| every identity + lemma holds on all 140 known n = 7 strings | n = 7 | **[EXH]** |

### Family Quantisation — **[CONJ]**, `code/quantise.py`

> In every **exact cover** of the (n−1)! classes by (n−2)! two-loops, the number
> of loops taken from each family is divisible by **n − 2**.

Exhaustive at n = 4 (4 covers), n = 5 (25), n = 6 (10068 — eleven splits, every
entry a multiple of 4). Mechanism open; it is *not* "covers are unions of
⟨s⟩-orbits". **Tolerance is exactly zero collisions** — see §8.

---

## 6. Measured-only facts about known strings — **[MEAS]**

Caveat for all of these: the 136 champions are all `7_5906_derived_*` and may
share provenance, so a shared pattern may be a construction signature.

* **Accidents do NOT separate the two regimes** — retracted. It looked that
  way when only the 43,096 standard-kernel optima were measured (all `A = 0`).
  The repaired corpus has 1,024 n = 6 optima with `A = 2…5`, every one still
  exactly on the Egan−1 line. Accidents are available at n = 6 and buy nothing.
* (superseded) **Accidents separate the two regimes.** Every one of the 43,096
  standard-kernel n = 6 optima has `A = 0`; `872-nonstandard` has `A = 2`; every
  n = 7 champion has `A ∈ 8…16`. Accidents are what the non-standard
  constructions buy, and 5906 is the only object past the Egan−1 line.
* All 136 have **v = 142 and T = 142** — HPV exactly tight. HPV slack is 0 on
  137 of 140 strings.
* `A = 132 − S` is **not** constant: A ∈ {8,9,10,12,13,14,17,18}, so
  S ∈ {114…124} and B + Y moves to compensate.
* Accidents **concentrate**: `A_f > 0` in exactly one family for 112/136 and
  exactly two for 24/136 — never three.
* Families used: 6 (88 strings), 7 (47), 5 (1).
* No known string has v in 121…139. Known: v = 120 (T = 148, 149),
  140 (143), 142 (142), 144 (144).
* Both split-free n = 7 strings (5912, 5913) are **single-family exact
  covers** — the monochromatic case of Family Quantisation.
* Egan's 5908 uses six families with exactly 24 loops each.
* jupiter 5907: v = 140, **A = 0**, S = 120, B + Y = 23.
* **Every champion has Y = 0** — 1/1 at n = 6, **136/136** at n = 7. Every
  split-free string has Y > 0.
* The split economy (`code/split_economy.py`):

  | | n = 6 | n = 7 |
  |---|---|---|
  | efficiency `η = dirty/n_partial` | 0.980 | 0.972 – 0.996 |
  | best split-free T | 30 | 148 |
  | best overall T | 29 (S = 25) | 142 (S = 124) |
  | **advantage of splits** | **1** | **6** |
  | exchange rate (drop in B+Y)/S | 1.0400 | 1.0484 |

* All five known champions use **zero** improper weight-2 (σ²) jumps.
* `D = −S` exactly on both n = 6 extremal strings (only `D ≥ −P` is proved).

---

## 7. External baselines — **[EXT]**

* **`5888 ≤ s(7) ≤ 5906`.** Lower: Hunter & Raudvere, **Lean-4 checked**
  ([urdvr/superpermutations-hunter](https://github.com/urdvr/superpermutations-hunter));
  they also give s(6) ≥ 869 and s(8) ≥ 46103. Upper: Egan/Houston 2019.
* `s(7) ≥ 5886`, all n ≥ 5 — Raudvere, Lean-4 checked
  ([urdvr/superperm-coeff2](https://github.com/urdvr/superperm-coeff2)); also
  s(6) ≥ 868, the bound this repo re-proves independently.

### 7.1 The general-*n* shape of both Lean bounds — **[EXT]**, read from source

Both are **general-n theorems**, not per-n computations, and both have excess
over HPV of order **(n−4)!**. Writing `HPV(n) = n! + (n−1)! + (n−2)! + n − 3`:

| bound | excess over HPV | asymptotic |
|---|---|---|
| **Hunter & Raudvere** | `((n−2)! − (n−2)) / (n² − 3n + 1)` | `~ (n−4)!` |
| **Raudvere coeff2** | `⌈((n−3)! − 1)/(2n−1)⌉`; uniform form `⌈(n−4)!/3⌉` | `~ (n−4)!/2` |
| **this repo** (`ledger.py`) | `((n−2)! − (n−2)) / ((n−2)(4n−3))` | `~ (n−4)!/4` |

Point values of the excess:

| n | 6 | 7 | 8 | 9 | 10 | 11 |
|---|---|---|---|---|---|---|
| Hunter | 2 | 4 | 18 | 92 | 568 | 4078 |
| coeff2 | 1 | 2 | 8 | 43 | 266 | 1920 |
| ours | 1 | 1 | 5 | 22 | 137 | 984 |

Three things follow, and they should govern how effort is spent here.

1. **"coeff2" is not a coefficient on n.** It names the criterion's
   `2k(n−1)+1` coefficient. Its own `half_wall` lemma proves that criterion
   cannot exceed `(n−4)!/2` — a hard ceiling on that route.
2. **Our ladder has the same numerator as Hunter's** and differs only in the
   denominator, `(n−2)(4n−3)` against `n²−3n+1`, a factor → 4. We are
   dominated at every n ≥ 6 (tie at 6) and **never overtake**. Any future
   `s(n) ≥ …` from this repo should be reported as an independent
   re-derivation, not a record.
3. **Every known lower bound is Θ((n−4)!) and Egan is Θ((n−3)!).** The ratio
   is Θ(n) in all directions, so the absolute gap grows factorially and no
   current method closes the problem at any n.
* `s(6) = 872` (Houston upper 2014; the matching lower is vlad-ds, preliminary).
* `s(4) = 33`, `s(5) = 153`.
* **Reliability note.** `vlad-ds/a6-872` is **not** a Lean-4 proof — it is
  Python plus a certificate ledger and its author labels it preliminary and
  invites audits. Its n = 7 half (`a7/`) is a macro-chain capacity test giving
  a *conditional* `s(7) ≥ 5896`. The Lean-4 n = 6 work is Raudvere's
  `superperm-coeff2` and Hunter & Raudvere's `superpermutations-hunter`.
  (`notes/cross_read_872lean.md` carries the full retraction of an earlier
  wrong reading.)

**So our own unconditional elementary bound (5885) is currently *below* the
published Lean bound.** This machinery is a complementary independent route,
not the state of the art.

---

## 8. Dead ends and retractions — do not retry

| item | status |
|---|---|
| "Any weight-3 jump between runs of length ≥ n−2 is om", and the ladder `v ≤ 120(1+2m+Y)` derived from it | **[RETRACTED]** — the l=5 row has two cap-5 exits, so (5,5) is not forced at n=7. Published 5889 never depended on it. |
| `c_5 ≤ (n−2)(1+Y+c_1+c_2+c_3)` (only short blocks break chains) | **[RETRACTED]** — length-(n−2) blocks break chains too; this had "proved" a bogus `B+Y ≥ 143` at n = 7 |
| `dirty ≤ S` | **[RETRACTED]** — Houston 872 has dirty = 49, S = 25 |
| "brute force cannot reach E ≤ 28 at n = 6" | **[RETRACTED]** — that was a per-node constant-factor artefact; a hoisted bound gave **550×** and it is now running |
| Family Quantisation surviving collisions | **[DEAD]** — exact cover **+ one redundant loop** is a legal saturated system and breaks it; tolerance is 0 collisions. This construction *is* the n = 7 v = 121, A = 0 state. |
| rigidity of the v = 121 A = 0 loop system | **[DEAD]** — collisions can be spread *or* concentrated (both realised at n = 6, v = 25) |
| ρ / om-stretch route for `B ≥ (n−2)!+1` | **[DEAD]** — ρ(c) = ⌈c/(n−1)⌉ for c ≤ 20, so once k ≥ 6 stretches the constraint is the trivial bound, and k cannot be forced below 6 |
| the full-loop bound (track U = wholly-uncovered loops) in the n = 6 search | **[DEAD]** — 14483 vs 14483 nodes |
| splitting the n = 6 search by (B, Y) | **[DEAD]** for pruning — identical aggregate node count; useful only for parallelising by case |
| block-structure enumeration (ordering-free) past B = 24 | **[DEAD]** — does not terminate at B = 25 |
| re-deriving HPV to combine additively with the counting lemma | **[DEAD]** — one state saturates both at v = 121 |
| the dirty exit table as a source of constraint | **[DEAD]** — caps `4 6 6 6 6 dead` at n = 7, nearly free |
| the A-split at rungs v ≥ 122 | **[DEAD]** — see §11; the refined lemma is *below* HPV there and falls off fast (121, 110, 105, 100 at v = 121…124), so splitting by A adds nothing |
| inter-loop δ-edges `≤ S` (the natural route to proving `comps ≥ v − S` by contracting loops) | **[REF]** — 5907-jupiter has 239 inter-loop edges against `S = 120` |
| excluding `A = 1` at length 872 by enumerating arc-start systems | **[DEAD]** — the test `T ≥ S + comps` is HPV in disguise and `S + comps = v ≤ 29` in all five sub-cases (v = 25…29), so it can never be violated. Demonstrated, not assumed: `code/a1.py` at v = 25 gives `S+comps ∈ [27,29]` over 4,000 systems. Excluding A = 1 needs a **Y** lower bound off the exact-cover rung — §10/§11's open lever. |
| ~~any **ordering-free** invariant of the arc set as a route past HPV~~ | **REVIVED** — this was recorded [DEAD] on the grounds that the best such bound is `T ≥ S + comps`, minimum `(n−2)!` = HPV. That generalised one invariant to all of them and is wrong. §2.7g's `CH3` adds the free-chain count `p` and reaches **29 against HPV's 24** at the n = 6 exact-cover rung, with 0 violations and 1,029/1,030 exactly tight on the census. The entry is kept as a reminder of how the over-generalisation happened. |
| Hamiltonian path in the **weight-3 port digraph** on complete traversals (→ HPV exactly), and the "minimum path-cover of the weight-3 arc set" dial below it | **[DEAD]** — from a complete traversal's exit, `l + l′ = 2n−2 ≥ 2n−3` forces the unique om exit (§3.2), so that digraph has **out-degree 1** and is a disjoint union of `(n−3)!` cycles of length `n−2`. Path cover is exactly `(n−3)!`, no search needed. Kills the whole "3 weight-3 successors give slack" family of arguments; raw out-degree A003319 = 1,1,3,13,71 is right but not the binding quantity. |
| GTSP/GLKH with one entry per 1-cycle and forced full traversal | **[DEAD]** as posed — that model is split-free with no partial arcs, so it provably cannot represent the n=7 champion (R = 844 arcs over 720 classes, S = 124). Solver class is fine; the instance must let a class be covered 1..n times. |
| this repo's ladder as a route to a **record** lower bound | **[DEAD]** — §7.1: same numerator as Hunter, denominator 4× worse, never overtakes. |
| `A = 1 ⟹ B = 1` (and the rest of `A1EQ`'s forward direction) | **[REF]** — `A` is ordering-free, `B` is not, so the Inflation Lemma refutes it: rotating `5908-egan`'s arc list gives a verified superpermutation of length **5909** with `A = 1, B = 2`. Adding one unentered 2-loop to its arc-start set keeps `A = 1` while moving `d` to 25 and `comps` to 2…6, killing the other two conclusions. §2.7e, [`notes/ordering.md`](ordering.md). **General rule: no ordering-free hypothesis can upper-bound `B`, `Y` or `T`.** |
| `B ≥ comps` (the ordering-free lower bound on `T`) | **[REF]** *as stated* — a weight-2 jump has **two** targets, `δ(u)` and `σ²(u)`, and `comps` follows only the first. Witnesses: n = 6 length 881 with `B = 2 < comps = 3`, n = 7 length 5914 with `B = 1 < comps = 2`. Repaired to `B + σ2 ≥ comps` (§2.7d). **Not a dead end**: §2.7f shows the minimum length is attained at `σ2 = 0`, so `T ≥ S + comps` is valid against the optimum, which is the only place it was used. |
| "the advantage of splits shrinks with n, so champions are split-free for large n" | **evidence points the other way** — advantage 1 (n=6) → 6 (n=7), exchange rate 1.0400 → 1.0484, η flat at ≈0.98. Mechanism: split-free walks must pay **either** the Chain-Count tax `Y ≥ (n−3)! − 1` (= 5, 23, 119, 719 at n = 6,7,8,9) **or** a B-tax to fragment out of it (5913: B=120, Y=29; 5912: B=145, Y=3), while *every* champion has Y = 0. The thing splits buy grows factorially. Not refuted — the n = 7 split-free optimum is unknown, only 125 ≤ · ≤ 148 — but unsupported. Champion split-freeness by n: free, free, **split**, **split** (n = 4,5,6,7). |

---

## 9. Working assumption

**(WA1) No minimal-length superpermutation is split-free, for n > 5.**

**PROVED AT n = 6** (§12g of the note; `data/e28_certificate.txt`): the shortest
split-free 6-superpermutation is exactly 873, so every 872 champion has splits.
**Still open for n ≥ 7**, and §6's split-economy measurements argue against it —
the advantage of splits grows from 1 at n = 6 to 6 at n = 7.

What it buys, stated honestly: since `v = (n−2)! ⟹ split-free` (§1), WA1
**eliminates the v = 120 rung outright** at n = 7. But that rung already gives
T ≥ 131, well above the binding rung. The binding rung is v = 121, whose
surviving state has **S = 6 ≠ 0** — so WA1 does **not** touch it. *WA1 does not
improve the n = 7 bound.*

---

## 10. What each target actually requires

`length = 5764 + T`, so a bound of `5764 + t` needs `T ≥ t` at **every** rung
v = (n−2)! … t−1. Current ladder: 131 at v = 120, then essentially `T ≥ v`.

| target | needs | rungs still short (deficit) |
|---|---|---|
| 5885 | T ≥ 121 | — (achieved) |
| 5886 (= Raudvere, Lean) | T ≥ 122 | v=121 (+1) |
| **5888** (match Hunter & Raudvere, Lean) | T ≥ 124 | v=121 (+3), 122 (+2), 123 (+1) |
| **5889** (beat it by one) | T ≥ 125 | v=121 (+4), 122 (+3), 123 (+2), 124 (+1) |
| **5896** (match the vlad-ds conditional, unconditionally) | T ≥ 132 | v=120 (+1), v=121…131 (+11 … +1) |
| 5906 | T ≥ 142 | v=120…141 (+11 … +1) |

Two things this table makes obvious:

1. **Matching the Lean bound is three rungs, not one.** Chasing +1 at v = 121
   alone gets 5886 and stops. The right unit of work is a lemma that lifts a
   *band* of rungs.
2. **v = 120 gives 131 — one short of 132.** So even the 5896 target needs the
   Pentad/v=120 rung improved by one, and every rung from 121 to 131 lifted to
   132. Any lemma of the shape "T ≥ v + g(v)" with g decreasing from ~12 at
   v = 120 to 0 at v = 142 would do the whole job at once; the measured data
   (T = 148/149 at v = 120, 143 at v = 140, 142 at v = 142) is consistent with
   exactly such a shape, and proving *any* nontrivial g is the open problem.

---

## 11. Why the ladder stalls above v = 121 — the `dirty ≤ 2S` leak

`code/a_split.py` redoes §6's A-split at every rung that matters. It reproduces
the published v = 121 row exactly (`121, 122, 123, 125, 126, 128, 129` for
A = 0…6) as a gate, and then finds that **the refined lemma collapses above
v = 121**:

| v | 121 | 122 | 123 | 124 |
|---|---|---|---|---|
| min T (refined lemma, over all A) | **121** | 110 | 105 | 100 |
| HPV (T ≥ v) | 121 | 122 | 123 | 124 |

So for v ≥ 122 the lemma is *below* HPV and the ladder falls back on HPV — the
A-split adds nothing there. Recorded as a dead end.

**The cause is completely explicit in the witnesses.** At every rung the
minimiser is A = 0 (so S is maximal), f = v (every loop a complete traversal),
N = v, and `dirty = 2S`:

| v | S | N | dirty | B | T |
|---|---|---|---|---|---|
| 122 | 12 | 122 | 24 | 98 | 110 |
| 123 | 18 | 123 | 36 | 87 | 105 |
| 124 | 24 | 124 | 48 | 76 | 100 |

i.e. exactly `T = S + (N − 2S) = v − S`. Each unit of S is allowed to buy
**two** free loop switches, so B falls twice as fast as S rises and T slides
downhill at slope −1 in S.

### What this pins down

Using the split ledger (§1.7), `T = S + N − dirty + Y`, so

> **HPV is precisely the statement `dirty ≤ S + N + Y − v`**,

and it is *exactly tight* on the n = 7 champion (S = 124, N = 258, Y = 0,
v = 142, dirty = 240). So any bound beating HPV is a bound of the form
`dirty ≤ S + N + Y − v − ε`.

The naive `dirty ≤ n_partial = S + m ≤ 2S` cannot supply it: measurement says
`η = dirty/n_partial ≈ 0.98` at both n = 6 and n = 7, so **`dirty ≈ 2S` really
is achieved** — the factor 2 is not slack in the model, it is real. The
improvement therefore has to come from *coupling* `dirty` to N (equivalently,
forcing N up as S rises), not from lowering `dirty` on its own. Note
`N ≥ n_partial` (§1.6) is far from binding here: at v = 122 it gives only
N ≥ 24 against N = 122.

~~**This is the single most concrete open lever in the whole file**~~ —
**[REF], see [`notes/second_order.md`](second_order.md) §D.** It is not a lever:
`dirty = 2S` is **attained exactly** by 12,672 of the 44,121 length-872 optima,
and the n = 7, 8, 9 records fall short by only 1–4 absolute (ratios .9958,
.9976, .9999, rising toward 1). Any true bound is `dirty ≤ 2S − O(1)`, additive
not multiplicative — so the factor-4 gap to Hunter cannot be closed here at all.
The repair (force triply-covered classes, i.e. `m < S`) also fails: `S − m` is
0…3 at n=6, 0…6 at n=7, and **0** at both the n=8 and n=9 records.
