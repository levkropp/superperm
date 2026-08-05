# Lev's Lemmas

Five results from this repository, stated once, in one place, with their proofs
and their verification. Everything here is either **proved** or **exhaustively
certified**; the measurements and conjectures that surround them live in the
other notes and are deliberately not mixed in.

Each section says what is claimed, why it is true, how it was checked, and — the
part that is easiest to skip and most important to keep — **what it does not
give**.

| | result | status |
|---|---|---|
| **1** | **Split Identity** — `R = (n−1)v − A` | **[THM]** |
| **2** | **A-cost law** — `A` is free slots, and accidents are E-neutral stitches | **[THM]** + **[MEAS]** |
| **3** | **Pentad Lemma** — at most five complete traversals chain; `v = 120` ⟹ length ≥ 5895 | **[THM]** |
| **4** | **No n = 6 champion is split-free** | **[EXH]** |
| **5** | **`A2`** — `comps ≥ v − S` | **[THM]** |

---

## 0. The objects, once

A superpermutation on `n` symbols is read as a closed walk through the `n!`
permutations, where each step appends characters. The vocabulary below is used
throughout and is fixed by `code/superstruct.py`.

* **σ = c** the rotation `u ↦ u[1:]+u[0]` (weight 1); **δ = d** the weight-2 step
  `u ↦ u[2:]+u[1]+u[0]`.
* An **arc** is a maximal σ-run. `R` = number of arcs. An arc is **full** if it
  has length `n`, **partial** otherwise.
* A **rotation class** is a `⟨σ⟩`-orbit; there are `(n−1)!` of them. A class is
  **multiply covered** if more than one arc starts in it; `μ_C` is that count and
  `S = R − (n−1)!` is the number of **splits**.
* A **2-loop** is a coset `g⟨a⟩` where `a = c^{n−1}d` has order `n−1`. There are
  `n!/(n−1)` of them, each with `n−1` **generators**. `v` = loops **entered**,
  `a_L` = arc starts in loop `L`.
* An **accident** (`A`) is a generator of an entered loop covered *mid-arc* —
  visited, but not at an arc start.
* `T = length − base_n`, `base_n = n + n! + (n−1)! − 3`. `T = S + B + Y` with
  `B` = blocks and `Y = Σ(w−3)` over the joins. `E = B − 1 + Y`.
* The **δ-graph** on arcs: `u → v` when `v` starts at `δ(end u)`. `comps` = its
  components.

`H = ⟨a,b⟩` has order `(n−1)!` and index `n`; its `n` cosets are the
**families**, and `s = a^{n−2}b`.

---

## 1. The Split Identity

> **Theorem.** For every complete Hamiltonian path in the `n`-symbol permutation
> overlap graph,
>
> ```
> S  =  R − (n−1)!  =  (n−1)(v − (n−2)!) − A,        equivalently   R = (n−1)v − A.
> ```

**Proof.** Every generator of every entered 2-loop is visited exactly once, and
the visit is of exactly one of three kinds:

1. it is the **start vertex** — one generator, in the start loop only;
2. it is at an **arc start after a jump** — that is what *entering* means;
3. it is **mid-arc** — an accident.

Summing over the `v` entered loops, with `J = R − 1` jumps:

```
(n−1)v  =  J + A + 1  =  (R − 1) + A + 1        ⟹   R = (n−1)v − A.   ∎
```

**Verification.** Algebraic derivation, independent re-measurement from the raw
strings of all five known extremal walks, and a 400-walk random stress test
(400/400 exact). `code/census.py` asserts the master identity
`T = (n−1)d + (B+Y) − A` on all 44,564 corpus strings.

| string | `S` | `(n−1)(v−(n−2)!)` | `A` | |
|---|---|---|---|---|
| classical n = 6 (873) | 0 | 5·0 = 0 | 0 | ✓ |
| Houston n = 6 (872) | 25 | 5·5 = 25 | 0 | ✓ |
| L2 n = 7 (5908) | 143 | 6·24 = 144 | 1 | ✓ |
| Coanda n = 7 (5907) | 120 | 6·20 = 120 | 0 | ✓ |
| Egan/Houston n = 7 (5906) | 124 | 6·22 = 132 | 8 | ✓ |

**What it does not give.** `A ≥ 0` yields the absorption lemma
`S ≤ (n−1)(v − (n−2)!)`, but `A` is not bounded above a priori, so the identity
sharpens the analysis of candidate structures — it does not by itself lower-bound
length.

---

## 2. The A-cost law

`A` appears in the Split Identity as a residual. It is not one. Two independent
readings, one proved and one measured, say what it is.

### 2a. `A` is the free-slot count — **[THM]**

> **Theorem (`SLOT`).** `A = Σ_L (n−1 − a_L)`, summed over entered loops. **`A` is
> exactly the number of free generator slots.**

**Proof.** An entered loop has `n−1` generator positions of which `a_L` are arc
starts, so the unused positions number `Σ_L (n−1 − a_L) = (n−1)v − R`, which is
`A` by §1. ∎  *Verified 1463/1463 on every string on disk.*

This makes `A` the **resource that every arc-set move spends**. Re-cutting a
class relocates one arc start, and it can only land in a free slot — of which
there are `A`. Two corollaries:

* **Vacating a loop `L`** (the only way to lower `v` by re-cutting) must relocate
  all `a_L` of its starts into free slots of *other* entered loops. `L` owns
  `n−1−a_L` of the `A` slots and they die with it, so the move needs
  `A − (n−1−a_L) ≥ a_L`, i.e. **`A ≥ n−1`**. Below that, `v` cannot fall at all,
  by counting alone.
* **Lowering `v` by one costs exactly `n−1` of `A`**, since
  `A′ = (n−1)(v−1) − R = A − (n−1)`. So re-cutting can lower `v` at most
  `⌊A/(n−1)⌋` times from any given arc set.

### 2b. Accidents are E-neutral stitches — **[MEAS]**

The motivating question: why does the 5906 champion need `A = 8` with `E = 17`,
while Coanda's 5907 pays `A = 0` with `E = 22`?

* **Accidents are free.** For every accident-affected loop, the entry actually
  taken is the *minimum* available weight — weight 3 in all four cases, computed
  against every unvisited generator. Accidents force no extra `E`.
* **Accidents come in adjacent pairs.** All 8 of the champion's accidents form 4
  **stitches**: two *adjacent* generators of one loop's generator cycle,
  pre-covered mid-arc by another loop's arc, closed by a weight-3 entry at the
  *next* generator in the cycle.

> **The law.** A stitch costs the same excess (1) as the explicit split it
> replaces. It is **E-neutral** — a repackaging of class coverage from an
> explicit split arc into the middle of another loop's arc. `A` is not a cost;
> it is the mechanism that lets a walk carry one more loop entry inside the same
> excess budget.

The two readings are the same fact from opposite ends: a stitch *is* the act of
spending a free slot, and §2a says there are exactly `A` of them.

**Consequence.** 5906 = 4 stitches + 17 structural weight-3 entries
(`v=142, S=124, E=17`); 5907 = 0 stitches + 22 heavy joins (`v=140, S=120,
E=22`). The 5906's slack of 1 below the absorption diagonal is precisely its
hand of stitches.

**What it does not give.** §2b is a measurement over the known champions, not a
theorem: nothing here proves accidents *must* pair, only that in every case
examined they do. §2a is proved and unconditional.

---

## 3. The Pentad Lemma

> **Lemma.** In any Hamiltonian path in the n = 7 permutation graph, at most
> **five** complete 2-loop traversals can be chained by weight-3 jumps.

A *complete traversal* is the `n−1` full class-arcs of one loop joined by
weight-2 moves: entered at generator `g`, it covers all six classes of `gA` and
exits at `g·a^5`.

**Proof.** Let a complete traversal of `L` be followed at weight 3 by a complete
traversal of `L′`. `L` has used all six of its classes, so `L′` must be
class-disjoint from `L`; the only weight-3 target with that property is **om**.
Hence the entry point advances by

```
g  ↦  g·a^5 b,        ord(a^5 b) = 5.
```

After five steps the entry point is `g` again, whose class is already covered. ∎

**Five is attained**, so the lemma is sharp: the five loops of one `a^5b`-orbit
are pairwise class-disjoint. Note the lemma is **cover-independent** — it never
mentions `v` and holds for every Hamiltonian path.

**Consequence — the `v = 120` rung at n = 7.** At `v = 120` the entered loops
carry `6 × 120 = 720` generator slots for 720 classes, so the cover is exact;
`R = 6v − A` with `R ≥ 720` forces `A = 0, R = 720`, every class a single full
arc, and `length = 5765 + X`. Splitting each group of consecutive complete
traversals into om-stretches of at most five, and trading that against the cost
of breaking loops into multiple visits, gives

```
X ≥ min_f max( f + ⌈f/5⌉ − 2,  239 − f ) = 130     (at f = 109, 110)
```

> **`v = 120` ⟹ length ≥ 5895.**

HPV gives only 5884 at that rung and Hunter–Raudvere needs 5888, so the tightest
rung of the n = 7 ladder is clear by eleven units rather than the four required.

**Verification.** `code/rigidity7.py` rebuilds the structure from scratch and
asserts each step (`ord(a^5b) = 5`, the five loops pairwise class-disjoint, the
sixth re-entering the start class, and the `X ≥ 130` optimisation).
`code/pentad_orbits.py` adds the global picture at n = 7: **1008** `⟨s⟩`-orbits
of size 5 with **0 / 1008** failing pairwise class-disjointness, each consuming
30 of the 720 classes, and **24 pairwise-disjoint orbits exactly partitioning all
720** — matching the counting ceiling of 24.

**The general-`n` shape.** `s = a^{n−2}b` has `ord(s) = n−2`, so at an exact
cover `comps = (n−2)!` components of `n−1` arcs each and

```
p ≥ (n−2)!/(n−2) = (n−3)!    and    T ≥ (n−2)! + (n−3)! − 1 = (n−1)(n−3)! − 1,
```

which is where the Egan−1 line comes from.

**What it does not give.** Read `ord(s) = n−2` **narrowly**. The cap applies only
to chains in which every block has that one length. Generalised to arbitrary
blocks it is **false**: the 5906 champion has block sizes `4…306`, every free
join is om, and yet all 18 components chain into a *single* free chain. The
correct general statement is the residue law — a free chain's step is
`g_r = a^r b` with `r = (l−1) mod (n−1)`, so **uniform residue caps the chain at
`ord(a^r b)` and mixed residues cap nothing.** The champion's residues are
`{3,5}`, mixed. The version that ignored this is registered `PFLOOP` **[REF]**,
171 violations.

---

## 4. No n = 6 champion is split-free

> **Theorem.** No split-free 6-symbol superpermutation has `E ≤ 28`. Since
> `length = 844 + E` for a split-free walk and `s(6) = 872 = 844 + 28`,
>
> **split-free ⟹ length ≥ 873.**
>
> The classical 873 *is* split-free, so this is **exact**: the shortest
> split-free 6-superpermutation is 873, and **every 872 champion has splits.**

**Method.** Exhaustive branch-and-bound over split-free walks with `E ≤ 28`.
Certificate: [`data/e28_certificate.txt`](../data/e28_certificate.txt).

```
2203 leaf verdicts      2.98 × 10¹³ nodes      zero FEASIBLE      zero cap hits
```

The search is a deterministic partition, so a shard is either resolved directly
or delegated to a refinement that is itself complete. Every refinement was
verified **exact by node accounting before being used** — work below each cut
computed both ways: 1,784,777 at depth 8; 370,586,159 at depth 16; 70,566,880 at
depth 24. Nothing double-counted, nothing lost to a gap in the partition. Three
binaries were involved (`sf6c`, `sf6d`, `sf6e`, differing only in how many cut
levels the parallel decomposition uses); all three produce identical node counts
and all three still find the known `E = 29` walk.

**One trap worth recording.** Modular refinement at a fixed depth can never split
the hot region. The filter keeps node `j` iff `j % N == myshard`, and
`0 % N == 0` for every `N`, so node 0's subtree stays whole in piece 0 at *every*
modulus — and node 0 is the all-δ spine, the walks that stay inside loops as long
as possible, exactly the region the bound prunes least. It consumed 5.13 × 10¹²
nodes alone. It has to be cut **deeper**, which is why the search grew a second
and then a third cut level.

**What it does not give.** This is `n = 6` only. The natural generalisation
("champions are split-free for large `n`") is **unsupported and the evidence runs
the other way**: the advantage of splits grows from 1 at n = 6 to 6 at n = 7, and
split-free walks must pay either the Chain-Count tax `Y ≥ (n−3)! − 1` (5, 23,
119, 719 at n = 6…9) or a `B`-tax to fragment out of it, while *every* champion
has `Y = 0`. Champion split-freeness by `n` runs: free, free, **split**,
**split** (n = 4, 5, 6, 7).

---

## 5. `A2`

> **Theorem.** `comps ≥ v − S`.

`A2` was a conjecture for this repository's entire history. It is the load-bearing
step under `CH3` (`T ≥ S + comps + p − 1`), the first ordering-free bound here to
beat HPV — 29 against HPV's 24 over all 10,068 n = 6 exact covers, where 29 is
the true n = 6 optimum.

Let `Q` be the **loop quotient** multigraph: nodes the `v` entered loops, edges
the live inter-loop δ-edges.

**(1) The exit identity.** For any arc of class `C` ending at `e`, the next arc
of `C` round the ring starts at `s = σ(e)`, so `e = σ^{-1}(s)`, and by
`a = c^{n−1}d`,

```
δ(e) = δ(σ^{-1}(s)) = s·a
```

— **an arc exits into the loop of the next arc of its own class.** If `μ_C = 1`
the next arc is itself and the edge is intra; if `μ_C ≥ 2` the arcs of `C` lie in
distinct loops (families are class-transversals) and the edge is inter.
*Verified 1275/1275.*

**(2) Class cycles.** A multiply-covered class with all `μ_C` exits live
contributes the closed cycle `L_1 → L_2 → … → L_μ → L_1` in `Q`. Distinct classes
use distinct arcs, hence distinct edges, so these cycles are **edge-disjoint** and
therefore independent in `Q`'s cycle space.

**(3) Cycle rank.** `Q` has `v` nodes and `e_inter = (S + m) − D` edges
(`n_partial = S + m`, less the `D` dead ones), so its cycle rank is
`(S + m − D) − v + q` with `q` = number of components of `Q`. That is at least the
number of fully-live multiply-covered classes, `m − D″` with `D″ ≤ D` counting
classes that own a dead arc. Rearranging,

```
v  ≤  S + q + (D″ − D)  ≤  S + q.
```

**(4) `comps ≥ q`.** Every δ-component's loops lie in a single `Q`-component (any
inter edge inside it is a `Q`-edge); every `Q`-component contains at least one
δ-component (its loops have arcs); distinct `Q`-components have disjoint arc
sets.

Combining, **`comps ≥ q ≥ v − S`**. ∎

**Verification.** `v ≤ S + q` and `comps ≥ q` both hold 1275/1275 on the census
with slack 0 on each, and with strict slack off-distribution (`v=121, S=6, q=116,
comps=117`; `v=141, S=126, q=60, comps=81`). `A2` itself: 44,564/44,564 census,
108/108 pool.

**The route that failed, and why.** The one previously recorded proof attempt was
`REF1` — contract the loops, bound the quotient's edges by `S` — refuted by
5907-jupiter with 239 inter edges against `S = 120`. The route that works is the
*same quotient*, counting its **cycle rank** instead of bounding its edges.
`REF1` was measuring the right object and asking the wrong question of it.

**What it does not give.** `A2` makes `CH3 ≥ v + p − 1` unconditional, and on
real strings `S + comps = v` exactly, so the bound has no slack left anywhere
except `p`. The n = 7 question `s(7) = 5906` is therefore *exactly*
**"is `v + p ≥ 143`?"** — with `v ≥ 142` closed by `p ≥ 1` and `v ≤ 141` open.
`A2` does not touch that, and nothing above should be read as if it did.

---

## Provenance

| result | note | code |
|---|---|---|
| Split Identity | [`split_identity.md`](split_identity.md) | `census.py`, `blockcount.py` |
| A-cost law | [`a_cost_law.md`](a_cost_law.md), [`pbound.md`](pbound.md) §9d | `lemmas.py` (`SLOT`) |
| Pentad Lemma | [`pentad_lemma.md`](pentad_lemma.md), [`lemma_arsenal.md`](lemma_arsenal.md) §3.5 | `rigidity7.py`, `pentad_orbits.py` |
| No split-free 872 | [`block_count_lemma.md`](block_count_lemma.md) §12g | `splitfree6b/c/d.c`, `data/e28_certificate.txt` |
| `A2` | [`pbound.md`](pbound.md) §8 | `a2hall.py`, `a2case3.py`, `lemmas.py` |

`python3 code/lemmas.py` re-checks the whole claim registry against 44,564
census strings and 108 constructed walks, and exits non-zero if any **[THM]** is
violated on either corpus.
