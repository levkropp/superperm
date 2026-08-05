# The SBY identity, the block-count lemma, and split-free s(7) ≥ 5889

*Verified by [`code/blockcount.py`](../code/blockcount.py),
[`code/exit_table.py`](../code/exit_table.py),
[`code/exit_table_n.py`](../code/exit_table_n.py),
[`code/split_free_5889.py`](../code/split_free_5889.py).*

---

## 1. The SBY identity

Fix a complete walk in the permutation overlap graph on n symbols and measure
four things:

| | |
|---|---|
| **S** | *splits* = R − (n−1)!, where R is the number of arcs (maximal weight-1 runs). A rotation class covered by j arcs contributes j − 1. |
| **B** | *blocks* = maximal runs of arcs joined by weight-2 jumps. |
| **Y** | Σ over the B − 1 costly jumps of (weight − 3). |

Then, by pure bookkeeping,

> **length = n + n! + (n−1)! − 3 + S + B + Y.**

*Proof.* length = n + n! − 2 + R + E with E = Σ_jumps (weight − 2)
(arc/jump identity). Cheap jumps contribute 0 to E; the B − 1 costly jumps
contribute (B − 1) + Y. Substitute R = (n−1)! + S. ∎

Asserted on every walk `blockcount.py` measures — n = 4, 5, 6 classical,
Houston 872, and 600 random complete n = 5 walks.

### The Houston–Pantone–Vatter bound, restated

HPV is length ≥ n! + (n−1)! + (n−2)! + n − 3, and the base of the SBY
identity is exactly `HPV − (n−2)!`. So

> **HPV ⟺ S + B + Y ≥ (n−2)!.**

n = 7: HPV ⟺ **S + B + Y ≥ 120**. Improving the n = 7 lower bound by k is
exactly proving S + B + Y ≥ 120 + k. Some values:

| string | S | B | Y | S+B+Y | length |
|---|---|---|---|---|---|
| classical 5 (153) | 0 | 6 | 1 | 7 | 152 + 1 |
| classical 6 (873) | 0 | 24 | 6 | 30 | 867 + 6 |
| Houston 872 | 25 | 4 | 0 | 29 | 867 + 5 |
| Egan/Houston 5906 | 124 | 18 | 0 | 142 | 5884 + 22 |

The two n = 6 strings are the two extremes: the classical one pays nothing in
splits and everything in blocks; Houston's 872 buys its way down to **four
blocks** by spending 25 splits. That trade is the whole difficulty of the
problem, and it is why the split-free slice is the tractable one.

---

## 2. Split-free walks

A walk is **split-free** if S = 0: every rotation class is a single full
n-permutation arc, R = (n−1)!. Then length = n + n! + (n−1)! − 3 + B + Y, and
at n = 7

> **length = 5764 + B + Y.**

Split-freeness rigidifies the structure completely.

* The only weight-2 move out of a *full* arc is δ, and δ out of the full arc
  at generator g lands on **g·a**, where a = c^(n−1) d has order n − 1: the
  next generator of the **same** 2-loop. (σ² is unavailable — it needs a
  split.)
* So a block occupies **consecutive generators of one loop**, and its length
  is between 1 and n − 1. A block of length n − 1 is a **complete traversal**.

### The exit table

From the end of a block of length l there are six weight-3 targets. For each,
compute the **cap**: how many generators the *next* block can run before it
re-enters a rotation class the departing block just burned. (Other blocks burn
other classes, so caps are upper bounds — the direction a lower bound needs.)
Everything in sight is relabelling-equivariant and S_n is simply transitive on
the n! permutations, so one entry point settles all of them; the scripts assert
that over all 5040 at n = 7.

| l | n = 5 | n = 6 | n = 7 |
|---|---|---|---|
| 1 | 0 2 3 4 4 4 | 0 3 4 5 5 5 | 0 4 5 6 6 6 |
| 2 | 0 1 3 4 4 4 | 0 2 4 5 5 5 | 0 3 5 6 6 6 |
| 3 | 0 0 2 3 3 4 | 0 1 4 5 5 5 | 0 2 5 6 6 6 |
| 4 | 0 0 0 2 2 4 | 0 0 3 4 4 5 | 0 1 5 6 6 6 |
| 5 | | 0 0 0 3 3 5 | 0 0 4 5 5 6 |
| 6 | | | 0 0 0 4 4 6 |

The shape is uniform in n. Two rows matter.

> **Exit trichotomy** (row l = n−1). Of the six weight-3 exits of a complete
> traversal, **three are dead** (the +2 stride re-enters the loop; two cross
> moves land directly in a class the traversal just spent), **two cap the next
> block at n − 3**, and **one is om** — the unique class-disjoint move, right
> multiplication by b = (3,4,…,n−1,2,1,n). So a complete traversal is followed
> by om, or by a block of length ≤ n − 3, or by a jump of weight ≥ 4.

> **Row l = n−2.** Two dead exits, one capping at n − 3, two at n − 2, and
> again a **unique** cap-(n−1) exit — *the same element b*.

Combined with the Pentad Lemma (ord(a^(n−2) b) = n − 2; see
[`pentad_lemma.md`](pentad_lemma.md)), these are the only local facts used
below.

---

## 3. The block-count lemma

Let f = #blocks of length n−1, n₅ = #blocks of length n−2, m = #blocks of
length ≤ n−3, and let *short* be the total length of those m blocks. Call a
maximal stretch of consecutive length-(n−1) blocks joined by **weight-3** jumps
an **om-chain**, and let c be their number. Then:

1. **(n−1)f + (n−2)n₅ + short = (n−1)!**, with m ≤ short ≤ (n−3)m, and
   B = f + n₅ + m.
2. **c ≤ (B − f) + Y + 1.** Every om-chain but the first is opened by a
   transition out of a length-(n−1) block that is *not* a weight-3 jump into
   another one: it lands on a shorter block (at most B − f of those) or it has
   weight ≥ 4 (at most Y of those).
3. **f ≤ (n−3)c + (m + Y + 1).** By the exit trichotomy a weight-3 jump
   between two blocks of length ≥ n−2 must take the unique cap-(n−1) exit om;
   by the Pentad Lemma an om-chain has at most n−2 traversals, and exactly
   n−2 only if it is not followed by another long block at weight 3 — i.e. it
   ends the walk, lands on a short block, or exits at weight ≥ 4.

These are three linear constraints on five integers. Minimising B + Y over
them is a finite search (`split_free_5889.py`, `profiles`). Results:

| n | min B + Y | resulting split-free bound | shortest known split-free string |
|---|---|---|---|
| 5 | 7 | **153** | 153 (classical) — **tight** |
| 6 | 26 | 869 | 873 (classical) |
| 7 | 124 | 5888 | — |

The n = 5 row is the soundness check that matters: the lemma reproduces
s(5) = 153 exactly, with no slack to hide an error in.

---

## 4. Killing the last n = 7 state: the period map

At n = 7 the counting leaves **exactly one** state at B + Y = 124:

> B = 124, Y = 0, and the profile is **100 complete traversals + 24 blocks of
> length 5, with no shorter block at all**.

That state is rigid enough to kill outright. Y = 0 and m = 0 mean *every*
transition in the walk is a weight-3 jump between blocks of length ≥ 5, hence
om; and an om-chain of five traversals cannot be followed by anything at all.
So the block sequence is forced to read

```
[T T T T  S]  [T T T T  S]  …  [T T T T]
```

— 25 om-chains of complete traversals, separated by 24 *isolated* length-5
blocks. A chain of k traversals followed by a five advances the chain start by
right multiplication by

> **Q_k = s^k · u**, with **s = a⁵b** (ord 5, the Pentad element) and
> **u = a⁴b** (ord 2),

using the fact that the unique cap-6 exit of a length-5 block is *the same* b.
The chain-length vector is 25 × 4, or 23 × 4 + one 3 + a final 5 — and

> **ord(Q_4) = 6.**

Six chains and the walk is back where it started, on a 2-loop it has already
burned. All 25 admissible chain-length vectors are enumerated and every one of
them repeats a loop. Hence B + Y ≥ 125 and

> ### Every split-free 7-symbol superpermutation has length ≥ 5889.

Elementary, cover-independent, and one better than Hunter–Raudvere on this
slice. It supersedes the rung-by-rung 5888 of
[`code/rung_split_free.py`](../code/rung_split_free.py), and unlike that
argument it never mentions v, the number of entered 2-loops, at all.

---

## 5. The SBY ladder: an elementary s(6) ≥ 868, and s(7) ≥ 5885

*[`code/sby_ladder.py`](../code/sby_ladder.py).*

Write β_n for the split-free floor on B + Y: **β₅ = 7, β₆ = 26, β₇ = 125**
(the first two from §3, the last from §4). Four inputs — three standard, one
new — now close n = 6 with no case analysis at all:

| | |
|---|---|
| **HPV** | T := S + B + Y ≥ v. *(Houston–Pantone–Vatter, cited.)* |
| **COVER** | v ≥ (n−2)!: the entered loops must cover all (n−1)! classes, n−1 each. |
| **SPLIT** | R = (n−1)v − A with A ≥ 0, i.e. S = (n−1)(v − (n−2)!) − A. |
| **BLOCK** | split-free ⟹ B + Y ≥ β_n. |

The point is what SPLIT does to the bottom rung. At v = (n−2)! it gives
S = −A ≤ 0, and S ≥ 0 forces **A = S = 0**: the walk is *split-free*, exactly
where BLOCK applies. Above that rung HPV takes over. So

> T ≥ min(β_n, (n−2)! + 1),

with no ladder, no cover enumeration, and no case analysis:

| n | β_n | (n−2)!+1 | T ≥ | length ≥ | HPV alone |
|---|---|---|---|---|---|
| 5 | 7 | 7 | 7 | **153** *(exact)* | 152 |
| 6 | 26 | 25 | 25 | **868** | 867 |
| 7 | 125 | 121 | 121 | **5885** | 5884 |

The n = 5 row is exact — s(5) = 153 — so the chain has no slack anywhere to
hide an error in.

**On n = 6.** 868 is not a new bound (three groups reached ≥ 868 in July 2026,
and this repo's own certificate reaches it). What is new is the *route*: four
lines of bookkeeping plus one finite integer search, where
[`CERTIFICATE_868.md`](../CERTIFICATE_868.md) needs the absorption lemma, the
rigidity of v = 24, an enumeration of all 10,068 exact covers and 29 CP-SAT
class-TSP runs. The two proofs share nothing but HPV.

**On n = 7.** 5885 is one better than HPV and three short of Hunter–Raudvere's
certified 5888. Also elementary, also cover-independent.

### Exactly what is left

A target T ≥ (n−2)! + k is free at v = (n−2)! (whenever β_n ≥ (n−2)!+k) and
free at v ≥ (n−2)! + k (HPV). What survives is the narrow band

> (n−2)! < v < (n−2)! + k, with 1 ≤ S ≤ (n−1)k − 1.

- **s(6) ≥ 869** needs the single case **v = 25, 1 ≤ S ≤ 5**. (The split-free
  sub-case S = 0, i.e. A = 5, is already cleared by BLOCK — so the v = 25 rung
  that bottlenecks *both* proofs of 868 is now partially discharged.)
- **s(7) ≥ 5889** needs **v = 121…124, 1 ≤ S ≤ 24**.

Same band, same obstruction, at both n.

### Why the local route does not get into the band

`sby_ladder.py` runs the block-count lemma generalised to allow **dirty** cheap
jumps — δ out of a partial arc — replacing blocks by *clean runs*
(N = B + dirty, dirty ≤ n_partial = S + n_split ≤ 2S). It comes out **below**
HPV everywhere in the band: T ≥ 20 against HPV's 25 at n = 6, v = 25; T ≥ 100
against 124 at n = 7, v = 124. So it adds nothing.

The reason is measured in [`code/dirty_exits.py`](../code/dirty_exits.py),
which computes the exit table for partial arcs: for a clean run of length l
whose last arc covers k < n permutations, the cheap exit is
t = g·a^(l−1)·c^(k−1)·d, and the table reports whether t is already visited and
how far the next run can then advance. At n = 7:

| l \ k | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| 2 | 6 | 6 | 6 | 6 | 6 | **dead** |
| 3 | 6 | 6 | 6 | 6 | 6 | **dead** |
| 4 | 6 | 6 | 6 | 6 | 6 | **dead** |
| 5 | 6 | 6 | 6 | 6 | 6 | **dead** |
| 6 | 4 | 6 | 6 | 6 | 6 | **dead** |

Compare the costly rows in §2, which are `0 0 0 4 4 6` and `0 0 4 5 5 6`. A
weight-3 exit is *nearly all dead ends*; a dirty cheap exit is **nearly all
cap-6**. The free loop switch is real and it is almost unobstructed. The only
structural fact the table produces is:

> **k = n−1 is impossible.** A partial arc covering exactly n−1 of the n
> permutations of its class, sitting at the end of a clean run of length ≥ 2,
> has no cheap exit at all: its δ-target has already been visited.

That is one bit, and it is not enough. Getting into the band needs a *global*
argument about how the splits sit in the cover — the analogue, one rung up, of
the v = 24 exact-cover rigidity behind s(6) ≥ 868. At v = 25 the object is a
near-exact cover of the 120 classes by 25 loops with exactly 5 doubled
classes, and unlike the 10,068 exact covers at v = 24 there are far too many
of those to enumerate.

## 6. The per-loop refinement, and the last state standing at n = 7

*[`code/loop_runs.py`](../code/loop_runs.py), validated by
[`code/dirty.py`](../code/dirty.py).*

§5's generalised lemma relaxes the loop structure to `N ≥ v`, and that is far
too weak: its v = 121 witness wants 111 complete traversals *and* 12 runs of
length 5, which needs 12 non-traversal loops when only 10 exist. The missing
constraint is that **complete traversals are loops, not free parameters**.

Every arc start is a generator of exactly one 2-loop; loop L holds
`a_L ≤ n−1` of them, and a clean run occupies *consecutive* generators of one
loop. So L's arc starts partition into `r_L ≥ 1` clean runs summing to `a_L`:

> `N = Σ r_L`, `R = Σ a_L`, `A = (n−1)v − R`, and
> **f := #runs of length n−1 = #{L : a_L = n−1 and r_L = 1}**.

All of it — including "a clean run lives in one loop at consecutive
generators" and "interior arcs of a clean run are full" — is asserted on 604
real walks by `dirty.py:dissect`. Feeding it back as packing conditions (two
runs of length n−2 cannot share a loop since 2(n−2) > n−1; a loop holding
t arc starts in runs of length ≤ n−3 needs ⌈t/(n−3)⌉ of them, so a
*non-traversal* loop with a_L = n−1 needs at least two) gives a strictly
stronger lemma. Only necessary conditions are used, so it stays a valid
relaxation; the candidate-m shortcut is checked against brute force at
n = 5, 6.

**It raises the split-free floor.** β₆ goes 26 → 27, and at n = 7, v = 120:

> the refined counting lemma alone gives **T ≥ 131**, i.e. **length ≥ 5895**.

That is exactly the v = 120 rung the Pentad Lemma reaches in
[`pentad_lemma.md`](pentad_lemma.md) by a completely different route — an
independent confirmation of 5895, and 6 better than §4's 5889 on that rung.

**And it reproduces HPV at the binding rung.** The ladder now reads:

| n | v = (n−2)! | (n−2)!+1 | +2 | +3 | s(n) ≥ |
|---|---|---|---|---|---|
| 5 | 7 | 7 | 8 | 9 | **153** (exact) |
| 6 | **27** | 25 | 26 | 27 | **868** |
| 7 | **131** | **121** | 122 | 123 | **5885** |

At n = 7, v = 121 the lemma alone returns **121** — up from 117, and now
*equal* to HPV. So the counting reproduces HPV at the one rung that binds,
without citing it.

### s(7) ≥ 5886 is down to a single state

`s(7) ≥ 5886` ⟺ T ≥ 122 everywhere, and every rung except v = 121 already
clears it. Splitting v = 121 by A (with S = 6 − A):

| A | 0 | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|---|
| S | 6 | 5 | 4 | 3 | 2 | 1 | 0 |
| T ≥ | **121** | 122 | 123 | 125 | 126 | 128 | 129 |

Only **A = 0** survives, and it is short by exactly one. Its extremal state is
completely pinned:

> **v = 121, A = 0, S = 6.** All 121 loops saturated (a_L = 6). 115 of them
> traversed complete; 6 broken into two clean runs each, both parts ≤ n−3 = 4
> (so `(4,2)`, `(2,4)` or `(3,3)`). N = 127 clean runs, 12 partial arcs all
> making dirty cheap exits, B = 115 blocks, Y = 0 — every one of the 114
> costly jumps has weight exactly 3.

### The near-miss, stated exactly

Transition counting on that state gets within **2**. Write T for a complete
traversal and S for a short run; the 127 runs give 126 transitions, 114 costly
(all weight 3) and 12 dirty.

- Every **costly T→T** transition is forced to be **om**: the next run has
  length 6, and by the exit trichotomy only the cap-6 exit reaches it.
- om-chains of traversals cap at **ord(a⁵b) = 5**, so
  `#chains ≥ ⌈115/5⌉ = 23`.
- A T-block (maximal stretch of consecutive traversals) containing j dirty
  T→T transitions splits into j+1 chains, so
  `#chains = #T-blocks + #(dirty T→T) ≤ 13 + 12 = 25`,
  the 13 because 12 short runs cut the sequence into at most 13 blocks.

**25 ≥ 23**: no contradiction, slack 2. Killing the state needs
`#chains ≤ 22`, i.e. `#T-blocks + #(dirty T→T) ≤ 21` where the counting only
delivers ≤ 24. Closing that gap — by an order/period argument on the 25
chains, as in §4, or by any lemma forcing short runs to cluster or dirty jumps
to avoid T→T — is exactly worth **+1 on s(7)**.

Why it is harder than §4: there the 25 chains were rigid (a single repeating
`[T T T T S]` pattern with one period map, `ord(Q₄) = 6`), whereas here the 12
dirty transitions each choose an exit multiplier from the partial-arc table
and can sit anywhere, so the period map branches instead of being a single
element.

## 7. Validation against all 140 known 7-symbol superpermutations

*[`code/n7_champions.py`](../code/n7_champions.py); strings from
[superpermutators/superperm](https://github.com/superpermutators/superperm),
a sample kept in `data/n7/`.*

Until now the n = 7 work could only be gated on algebra and on n ≤ 6 walks —
this repo had no 7-symbol string. There are 140 of them publicly available
(136 at the record 5906, plus 5907, 5908, 5912, 5913). Every identity and
every lemma above was re-run over all of them, and **all hold**.

| | min | max | distribution |
|---|---|---|---|
| length | 5906 | 5913 | 5906:136 5907:1 5908:1 5912:1 5913:1 |
| v | 120 | 144 | **120:2  140:1  142:136  144:1** |
| S | 0 | 143 | **0:2**  114:4 115:2 118:29 119:10 … |
| Y | 0 | 29 | 0:137 3:2 29:1 |
| T = S+B+Y | 142 | 149 | 142:136 143:1 144:1 148:1 149:1 |
| HPV slack T−v | 0 | 29 | **0:137** 3:1 28:1 29:1 |

Three things worth reading off:

- **HPV is exactly tight on the record strings.** All 136 strings of length
  5906 have v = 142 and T = 142. So at the top of the ladder HPV already
  proves what those strings achieve, and there is nothing to win there — the
  entire problem lives at low v, where a hypothetical 5888-string must sit
  (v ≤ 5888 − 5764 = 124).
- **Split-free 7-symbol superpermutations exist**, but they are long: the two
  with S = 0, R = 720, v = 120 are the 5912 and 5913 strings. §4 proves
  ≥ 5889 and §6 proves ≥ 5895 at v = 120; the shortest known is 5912, so the
  remaining gap on that slice is 17.
- **No known string has v in 121…124** — the band the ladder still needs is
  empty of examples, in either direction.

## 8. Cover rigidity at v = 121, and the collision budget

*[`code/pentad_orbits.py`](../code/pentad_orbits.py).*

The pinned state of §6 has 115 traversals in at most 25 om-chains, so
115 ≤ 5c₅ + 4(25 − c₅) forces **c₅ ≥ 15** full chains of five. A full chain
entered at g visits g, gs, …, gs⁴ — a complete **⟨s⟩-orbit** of generators.
There are 5040/5 = 1008 of them, and the computation confirms the sharpness
half of the Pentad Lemma **on all 1008**: the five 2-loops of an orbit are
always pairwise class-disjoint, so a full chain consumes exactly 30 of the 720
rotation classes.

A pretty corollary drops out: **24 pairwise class-disjoint orbits exist and
exactly partition all 720 classes** (24 × 30 = 720). That is the v = 120 exact
cover seen through the om structure.

It also means cover rigidity **alone does not kill v = 121**: the state needs
only 15 full chains and 24 fit comfortably.

### What does bite: the collision budget

At v = 121, A = 0 every loop is saturated (a_L = n−1 = 6), so 121 loops carry
726 class-slots over 720 classes — **exactly six classes are covered twice**,
and those six are the S = 6 split classes. Six is the collision budget for the
entire walk. Now:

- a **full** chain cannot end on om, because om from its fifth traversal
  targets the chain's own starting generator, already spent;
- so it ends on a **cap-4 exit**, a **dirty** jump, or the walk end;
- and the two cap-4 exits of a complete traversal land in loops sharing 1 or 2
  classes with the departing loop (`after_traversal.py`) — each one **spends
  collision budget**.

That gives `c₅ ≤ 6 + d_T + 1` with d_T = #dirty jumps out of a traversal ≤ 12,
against the old bound of 25. Combined with
`C = #T-blocks + d_TT ≤ 13 + d_TT`:

> 115 ≤ 4C + c₅ ≤ 4(13 + d_TT) + 6 + d_T + 1 ≤ 59 + 5·12 = **119**.

Still ≥ 115, so the state survives — but the slack has come down from **10 to
4**. Four more units, from any source, kill the state and give s(7) ≥ 5886.

### And the diagnostic that closes off one route

At v = 121 HPV and the refined lemma both return 121, and the lemma's own
extremal state has T = 121 = v — so **one hypothetical state saturates both
bounds simultaneously**. Re-deriving HPV inside the SBY framework in order to
*add* the two bounds therefore cannot gain anything at the rung that binds:
any gain has to come from proving that state impossible, which is the kill
itself. That route is closed.

## 9. Must a champion have splits?

The shortest known split-free 7-symbol strings are 5912 and 5913 (§7), while
the record is 5906 — so empirically champions do have splits, heavily
(S ≈ 118, B ≈ 18, v = 142). Proving it would mean **split-free ⟹ length
≥ 5907**, i.e. B + Y ≥ 143.

Running the refined lemma along the split-free line S = 0 (equivalently
A = 6(v−120), R = 720) gives:

| v | 120 | 121 | 122 | 123 | **124** | 125 | 126 | … | 140 |
|---|---|---|---|---|---|---|---|---|---|
| B+Y ≥ | 131 | 129 | 128 | 126 | **124** | 125 | 126 | … | 140 |

The minimum is **124, attained only at v = 124** — and that state is
`f = 100` traversals plus `n5 = 24` runs of length 5, which is exactly the
state §4 kills with `ord(s⁴u) = 6`. The two arguments compose, so split-free
⟹ B + Y ≥ 125, length ≥ 5889, with the extremum now localised.

Getting from 125 to 143 would mean killing ~19 successive rungs of that
ladder. The family is uniform — at every v ≥ 124 the state is
`f = 720 − 5v` complete traversals plus `n5 = 6v − 720` runs of length 5, one
per loop, with Y = 0 and B = N = v — so a single generalised period-map
argument might take several rungs at once. But it is a long way.

**And it would not help the lower bound.** In the band that actually blocks
s(7) ≥ 5886, the binding sub-case is A = 0, i.e. the *maximum* number of
splits (S = 6 at v = 121, giving T ≥ 121), while the split-free sub-case there
gives T ≥ 129 — cleared with 7 to spare. Split-freeness is the *easy* side and
it is already discharged at every rung. The hard side is many splits.

Worth noting how strange the blocking state is: it has v = 121, S = 6,
B = 115, whereas every known champion has v = 142, S ≈ 118, B ≈ 18 — the
opposite corner of the space, and nothing observed lies anywhere near it. That
suggests the missing 4 units are more likely to come from a *realizability*
obstruction than from further counting.

## 10. The Coset Lemma

*[`code/coset_lemma.py`](../code/coset_lemma.py).*

Chasing §9 produced the best structural lemma in this file. Recall that a
weight-3 jump between two runs of length ≥ n−2 is forced to be **om**, and
that a run of length l followed by om advances the next run's start by
`a^(l−1) b`. So an **om-stretch** — a maximal run of consecutive runs of
length ≥ n−2 joined by weight-3 jumps — has its starting generators confined
to a single right coset of

> **H := ⟨s, u⟩**, with s = a^(n−2)b (ord 5) and u = a^(n−3)b (ord 2).

The computation:

> **|H| = 720 = 5040/7 — an index-7 subgroup, not all of S₇.**

And it has exactly the right shape. H contains a, so it is a union of complete
2-loops: **120** of them. Its order 720 is coprime to 7 = |⟨c⟩|, and the
rotation classes are precisely the left cosets of ⟨c⟩, so H meets **every one
of the 720 classes exactly once** — and so does each of the 7 right cosets
(all verified). Hence:

> **Coset Lemma.** The 840 two-loops of S₇ partition into **7 families of
> 120**, and *each family is an exact cover of the 720 rotation classes*. An
> om-stretch lives inside one family. Therefore
> (i) the runs of an om-stretch are automatically class-disjoint, and
> (ii) an om-stretch enters at most **(n−2)! = 120** distinct 2-loops.

### When is a transition forced onto om — and a correction

⚠️ **Correction.** An earlier version of this section claimed that *any*
weight-3 jump between two runs of length ≥ n−2 must be om, and concluded that
every split-free ladder state at v ≥ 121 with m = 0, Y = 0 dies, giving
`v ≤ 120(1 + 2m + Y)`. **That is wrong**, and both the conclusion and the
ladder table derived from it are withdrawn.

`coset_lemma.py` now *derives* the forcing condition from the exit table
instead of asserting it. A weight-3 jump from a length-l run to a length-l′
run needs an exit of cap ≥ l′, and the count of such exits is unique — hence
om — exactly when

> **l + l′ ≥ 2n − 3**, at n = 7: **(6,6), (6,5), (5,6)** — and **not (5,5)**.

The l = 5 row is `[0, 0, 4, 5, 5, 6]`: two of its exits have cap 5, so a
length-5 run may be followed by another length-5 run *without* using om. The
correct general rule is

> #om-stretches ≤ 1 + Y + #(adjacent pairs with l + l′ ≤ 2n−4),
> and v ≤ (n−2)! · #om-stretches.

In aggregate counting that is too weak to bite at v ≥ 124, so **the split-free
ladder reverts to its §9 values** (minimum 124 at v = 124).

**What survives, and why the published bound is unaffected.** The group theory
above never used the forcing claim, nor does the collision arithmetic below.
And §4's argument is intact: its counting *independently forces* the 24
length-5 runs to be **isolated**, so no (5,5) transition occurs there — that
state genuinely is a single om-stretch, and the Coset Lemma kills it
(v ≤ 120 < 124) more cleanly than the period map does. So split-free
⟹ B + Y ≥ 125, length ≥ **5889**, exactly as before. Only the intermediate
claim about where the minimum sits was wrong.

### The collision arithmetic it produces

Because each family is an exact cover, a loop *outside* a family has its 6
classes covered exactly once each *by* that family — so:

> a foreign loop collides with a full family in **exactly 6 class-slots**
> (spread over five loops: four sharing one class, one sharing two).

Six is *precisely* the collision budget of the v = 121, A = 0 state (§8). So
writing t for the number of loops of the majority family left unused, that
state needs 121 = (120 − t) + (t + 1) loops and:

- **t = 0** — the entire cover is *one full family plus a single foreign
  loop*, spending exactly the 6 collisions. Feasible, and completely rigid.
- **t = 1** — two foreign loops, each still colliding ≥ 4 times: ≥ 8 > 6.
  **Dead.**
- **t = 2, 3** — ≥ 9 and ≥ 8 collisions. **Dead.**
- t ≥ 4 — the crude count no longer closes.

So the main blocking state is squeezed toward an extremely rigid shape: all
120 loops of one coset family, plus one loop from another, with the foreign
loop's runs necessarily entered and left by non-om transitions (an om-stretch
cannot leave its family). Turning t ≥ 4 into a contradiction, or killing the
t = 0 configuration, is now the concrete target.

## 11. The om-stretch primitive ρ(c), exactly

*[`code/omstretch.c`](../code/omstretch.c), cross-checked by
[`code/omstretch.py`](../code/omstretch.py).*

The Coset Lemma turns "what can one om-stretch do?" into a finite,
self-contained question. Inside a stretch all generators lie in one right
coset of H = ⟨a,b⟩, and that coset meets each rotation class exactly once; in
a split-free walk each class is used at most once. So **a stretch is exactly a
simple path in the right Cayley graph Cay(H; {a,b})** on (n−1)! vertices, of
out-degree 2:

> `g → g·a` continues the current run (free);
> `g → g·b` ends it and starts a new one (costs one run).

Runs cap at n−1 for free — ord(a) = n−1, so an (n−1)-st a-step would revisit
the run's own start. Define

> **ρ(c) = the fewest runs over simple paths covering c vertices.**

Two things make this tractable. Left multiplication by h ∈ H preserves the
right-Cayley edges, so the graph is **vertex-transitive** and every path may be
assumed to start at the identity. And the a-edges cut the coset into (n−2)!
cycles — the 2-loops — so the unvisited vertices of a loop fall into maximal
a-consecutive **arcs**, each needing a run of its own:

> remaining runs ≥ Σ_loops (#unvisited arcs) − 1.

That bound (rather than ⌈remaining/(n−1)⌉) is what makes the search close.
Iterative deepening on the run count turns each failed level into a proof:

| n | vertices (n−1)! | loops (n−2)! | **ρ((n−1)!)** | nodes |
|---|---|---|---|---|
| 5 | 24 | 6 | **8** | 180 |
| 6 | 120 | 24 | **31** | 21 M |
| 7 | 720 | 120 | **≥ 128** | 1.3e11 at K = 127 |

The first two are exact — every smaller run count is proved infeasible. A bespoke C
branch-and-bound does the search and an independent Python re-implementation,
sharing no code with it, reproduces both values.

### What ρ says about the trade-off

At n = 6 a split-free walk that is a *single* om-stretch costs ρ(120) = 31
runs, so T = 31. But the classical 873 is split-free with N = 24, Y = 6,
T = 30 — it is *cheaper* to pay Y = 6 and break into several stretches than to
stay inside one coset. So the om structure is not merely a constraint the
adversary suffers: **leaving the coset family is something an optimal
split-free walk actively wants to do**, and Y is the price. That is the honest
shape of the problem, and it explains why the single-stretch bound alone will
not reach 5907: any real ladder has to price the stretch count against ρ of
the pieces.

## 12. The Chain-Count Lemma

*[`code/chain_count.py`](../code/chain_count.py).*

Take a split-free walk in which **every block is a complete traversal**. Then
the blocks *are* the loops, each covering n−1 of the (n−1)! classes, so
B = f = (n−2)! and the loops form an exact cover. Every one of the f−1
transitions joins two runs of length n−1, and l + l′ = 2n−2 ≥ 2n−3, so by §10 a
weight-3 transition here is **forced onto om**. Each transition is therefore om
or has weight ≥ 4; write h for the number of the latter. Then

> #chains = f − #om = f − ((f−1) − h) = **1 + h**,

and a chain of k traversals sits at g, g·s, …, g·s^(k−1) with s = a^(n−2)b, so
k ≤ ord(s) = **n−2** (the next would re-enter g). Hence
f ≤ (n−2)(1+h), giving h ≥ (n−3)! − 1, and Y ≥ h:

> **Chain-Count Lemma.** A split-free walk all of whose blocks are complete
> traversals has Y ≥ (n−3)! − 1 and T ≥ (n−2)! + (n−3)! − 1, i.e.
>
> **length ≥ n! + (n−1)! + (n−2)! + (n−3)! + n − 4.**

That closed form is the striking part:

| n | ord(s) | f = (n−2)! | Y ≥ | length ≥ | s(n) | classical |
|---|---|---|---|---|---|---|
| 4 | 2 | 2 | 0 | **33** | 33 | 33 |
| 5 | 3 | 6 | 1 | **153** | 153 | 153 |
| 6 | 4 | 24 | 5 | **872** | 872 | 873 |
| 7 | 5 | 120 | 23 | **5907** | ? | 5913 |

It is **exactly s(n) for n = 4, 5, 6** — sharp wherever s(n) is known — and at
n = 7 it gives **5907, one more than the conjectured 5906**. So:

> Conditional on s(7) = 5906, **no 7-symbol champion is split-free with all
> blocks complete traversals.**

That is the first proved instance of the "champions must have splits"
hypothesis, on the sub-case where the walk is most rigid.

### n = 6: what Y = 5 would have to be

At n = 6 the bound lands on 872 = s(6) exactly, so the case survives and needs
one more unit — Y ≥ 6 instead of ≥ 5. Y = 5 forces 6 om-chains for 24
traversals, each of length exactly 4 = ord(s), so the 24 loops are **six full
⟨s⟩-orbits** which must exactly cover the 120 classes. Computed: there are 180
⟨s⟩-orbits, **all 180** have their 4 loops pairwise class-disjoint (the n = 6
analogue of Pentad sharpness), each covering 20 classes, and 6 × 20 = 120
exactly. And **8640 such exact covers exist** — so cover rigidity alone does
*not* kill Y = 5.

The five connecting jumps do. Y = 5 spread over h = 5 heavy transitions forces
each to have weight **exactly 4**. A chain entered at g runs g, g·s, g·s², g·s³;
its last traversal's final arc starts at g·s³·a⁴ and ends at σ⁵ of that, and
every chain has exactly 24 = (n−2)! weight-4 exits, each landing on one chain
entry. Requiring the six chains to be strung into a single path by five such
jumps:

> **0 of the 8640 covers are linkable.**

So Y = 5 is impossible, Y ≥ 6, and T = 24 + 6 = 30:

> ### No n = 6 champion is split-free with all blocks complete traversals.
>
> Split-free with B = 24 forces length ≥ 873 > 872 = s(6).

That closes the case B = 24 — the exact-cover case, and the one the repo's own
s(6) certificate reaches only as far as E ≥ 27. The remaining cases for a full
n = 6 result are B = 25…29 (equivalently Y = 4…0), where the blocks are no
longer all complete traversals and the Chain-Count Lemma does not apply
directly.

## 12b. ρ for partial coverage, and why B ≥ 25 is different

`omstretch.c` now takes a coverage target, so ρ(c) — the fewest runs to cover
*c* classes inside one om-stretch — is computable for every c, not just
c = (n−1)!. At n = 6:

| c | 20 | 25 | 40 | 60 | 80 | 100 | 110 | 120 |
|---|---|---|---|---|---|---|---|---|
| **ρ(c)** | 4 | 6 | 9 | 14 | 19 | 24 | 27 | **31** |
| ⌈c/5⌉ | 4 | 5 | 8 | 12 | 16 | 20 | 22 | 24 |

(The arc bound is only valid when the path must cover *everything* — for a
partial target the path can simply avoid the awkward arcs — so the search falls
back to the capacity bound there. Getting that wrong, or forgetting that the
current run can still grow, over-prunes and silently loses solutions; both
mistakes were caught by re-deriving the known ρ(120) = 31.)

**Why B = 24 closed and B ≥ 25 does not.** Redo the chain count for a general
split-free profile: maximal om-linked runs of complete traversals still cap at
ord(s) = n−2, and such a run ends at a shorter block, a weight-≥4 jump, or the
walk end, so

> f ≤ (n−2)[(B − f) + Y + 1] ⟹ f ≤ (4(B+Y) + 4)/5 = **24** when B + Y = 29.

But f ≤ 24 is automatic (5f ≤ 120). So the chain count is *exactly tight* at
B + Y = 29 — it bites only where f = 24 is forced, i.e. **B = 24**, which is
why that case fell and the others do not.

For B ≥ 25 the binding constraint is instead the stretch trade. A split-free
walk splits into k om-stretches covering c₁ + … + c_k = 120 classes with
B ≥ Σ ρ(c_i), and k − 1 ≤ Y + #(non-om weight-3 transitions). Since
ρ(120) = 31 > 29 ≥ B, **k ≥ 2 always** — but ρ(60) + ρ(60) = 28 and
ρ(40)·3 = 27, so two or three stretches already fit inside B ≤ 29. But the route bottoms
out. ρ(c) = ⌈c/5⌉ already for c ≤ 20, so a walk split into six stretches of 20
classes has Σρ(c_i) = 24 — the trivial bound. **The ρ constraint therefore adds
nothing once k ≥ 6**, and k cannot be forced below 6: k − 1 ≤ Y + #(non-om
weight-3 transitions), and the B ≥ 25 profiles contain many length-4 blocks
whose (4,4) adjacencies admit two non-om weight-3 exits each (the l = 4 row is
`[0,0,3,4,4,5]`, so three exits reach a length-4 block and only one is om).

So the stretch/ρ route **cannot close B = 25…29**, and neither can the chain
count (tight only at B = 24). Recorded as a negative result: the remaining
cases need a genuinely different technique — a much stronger search, or the
generalized-TSP formulation (120 class-clusters × 6 rotations = 720 nodes) fed
to the LKH/Concorde tooling in the superpermutators repo. It also remains
entirely possible that the hypothesis is **false** at n = 6 and a split-free
872 exists; nothing here rules it out.

## 12c. B = 24 closed again, independently: the class-TSP over a fixed cover

A split-free 872 has S = 0 and `length = 844 + E` with `E = B − 1 + Y`, so
E = 28 and B + Y = 29; HPV gives v ≤ B + Y = 29, and covering 120 classes with
loops of 5 classes gives v ≥ 24.

**v = 24 and B = 24 are the same case**, not nested ones. Σ_L a_L = 120 over v
loops with a_L ≤ 5 forces a_L = 5 for every loop when v = 24, hence r_L = 1 and
B = 24; conversely B = Σ r_L ≥ v ≥ 24 forces v = 24. So v = 24 ⟺ B = 24 ⟺
every block is a complete traversal — exactly §12's case. What follows is a
*second, independent* proof of it: it uses no om theory, no Coset Lemma and no
chain count, and it disposes of every Y at once rather than just Y = 5.

The point is that an exact cover fixes *everything except the order*. There are
144 two-loops at n = 6, each of size 30; a permutation lies in 6 of them, and
each loop has exactly **5 generators, one per class** (HPV Prop 1). So once a
class is assigned to a cover loop, its arc's starting permutation is determined
— all 120 full arcs are fixed, and only their sequence is free. Every B and Y
compatible with v = 24 collapses into one question:

> **minimum-weight Hamiltonian path over 120 fixed nodes**, with
> `jump(C, C′) = weight(σ⁵(g_C), g_{C′})` and `E = TSP − 238`.

Up to relabelling there are 29 such covers (`data/orbits29.json`).
`code/verify_orbits_tsp.py` certified 28 of them OPTIMAL with minimum ≥ 267;
**orbit 28** came back FEASIBLE at 267 with only 265 proved, so its optimum was
266 or 267 — and 266 is exactly E = 28, exactly length 872.

`code/orbit28b.c` settles it. It reads the 120 arc starts, rebuilds the jump
matrix from scratch, and does branch-and-bound on E with the arc-counting bound
of §11: cost-0 moves are δ and never leave a loop, each loop is a 5-cycle of
classes under δ, the uncovered classes of a loop form maximal circular arcs
each needing its own block, and the current block can run into at most one of
them for free, so `remaining cost ≥ arcsum − 1`.

> **No Hamiltonian path of weight 266 exists.** Exhaustive over all 120 start
> nodes, 2.399 × 10¹⁰ nodes. Orbit 28's optimum is therefore exactly **267**.

Guards, since two over-pruning bugs were caught this way earlier:

* the search *finds* the known 267 solution in 120 nodes, so it is not simply
  failing to see solutions;
* the instance is validated on its own terms — the 120 arcs tile all 720
  permutations exactly once and δ out of the arc ends closes into 24 five-cycles
  (`validate()` in `code/orbit28.py`);
* a second implementation carrying only the naive capacity bound agrees at
  every budget it can reach: exhaustively IMPOSSIBLE at E ≤ 23, 24, 25, 26 and
  27 (the last at 4.72 × 10¹⁰ nodes). E ≤ 26 independently reproduces CP-SAT's
  previously certified 265.

CP-SAT itself is not usable at this size: `AddCircuit` over 121 nodes does not
close the gap even given hours, which is why the branch-and-bound is primary
and `code/orbit28.py` is kept only as the model of record.

**All 29 orbits are now OPTIMAL ≥ 267, so B = 24 forces E ≥ 29 and length
≥ 873 > 872**, with no appeal to the chain count.

What remains is **B = 25 … 29**, where the loops overlap, the arc starts are no
longer pinned by a cover, and the space stops being a fixed 120-node TSP.

### The case list, and why counting cannot shorten it

`code/profiles6.py` enumerates the run-length profiles (c₁…c₅, Y) with
Σ i·cᵢ = 120 and B + Y = 29. **377 survive, and exactly one has B = 24** — the
case just closed. So 376 profiles remain, spread over c₅ = 4 … 23.

Counting cannot trim that list, and it is worth being exact about why. The
chain count generalises to

> c₅ ≤ (n−2)·(1 + Y + (B − c₅)),

because a chain of complete traversals is broken by **any** non-complete block,
not merely a short one: the om step out of a block of length l is a^(l−1)b, a
*different* group element for each l, so a length-(n−2) block interrupts the
s-orbit even though the (n−1, n−2) transition is itself forced om. At n = 6
with B + Y = 29 that reads 5c₅ ≤ 4·30, i.e. c₅ ≤ 24 — which 5c₅ ≤ 120 already
gives. **The chain count is vacuous away from B = 24.** Combined with
Σ i·cᵢ = 120 it yields only B + Y ≥ 25, far short of the 30 needed.

(A draft of `profiles6.py` used c₅ ≤ (n−2)(1 + Y + c₁+c₂+c₃), counting only
*short* blocks as breakers. That is false, and it made the case list look far
smaller than it is. §12b's form is the correct one.)

### Brute force, and a 550× correction

`code/splitfree6b.c` adds the natural analogue of the arc bound to the full
720-node search: a length-5 run is an *entire* loop, so it needs one of the 144
loops still wholly uncovered. Tracking U = #such loops gives
`blocks ≥ ⌈(need − min(U, ⌊need/5⌋))/4⌉`. It is sound but worth essentially
nothing (14483 vs 14483 nodes at E ≤ 24): U stays above need/5 throughout the
region the search visits.

**Splitting by (B, Y) also buys nothing in aggregate.** Since E = (B−1) + Y,
the single constraint E ≤ 28 lets blocks and excess weight trade; fixing B
gives the two separate constraints `#blocks + future ≤ B` and `Y ≤ 29 − B`,
which look strictly stronger. Measured at E ≤ 26 the four cases cost
0.8 M + 55 M + 443 M + 830 M = 1.329 × 10⁹ nodes against 1.325 × 10⁹ unsplit —
the same. What it does show is that the work concentrates at **large B, small
Y**, and it is a clean way to parallelise by case.

What *was* decisive is embarrassingly mundane. The target loop scanned all 720
candidates at every node, because `cost + w − 2` alone never exceeds the budget
while cost is small, and ~600 of the 720 targets have weight 6. Hoisting a
target-independent floor on the post-move block bound out of the loop —

    f2min = lo_blocks(rem − 1 − (n−2), U),   break once w > budget − cost + 2 − f2min

— cuts the scan to a couple of dozen. Node counts are **byte-identical**; only
the constant changes. E ≤ 25 went from **134 s to 0.24 s: a 550× speedup.**

So the earlier verdict was an artefact of the constant factor, not of the
search tree, and it is withdrawn. With growth ≈ 114× per unit
(1.3 × 10⁹ at E ≤ 26, ≈ 1.5 × 10¹¹ at E ≤ 27), the decisive run **E ≤ 28** is
roughly 4 × 10¹² nodes — about 13 hours on 20 cores. It is running.

Two process notes, both of which cost time here:

* **Shard depth matters more than shard count.** Every shard re-explores the
  tree above the cut, so a cut at depth 12 with branching ~7 wastes ~10¹⁰ nodes
  *per shard* — more than the entire E ≤ 26 tree. Depth 8 with 2000 shards puts
  the redundant work at well under 0.1%.
* Using `U − 6` rather than `U` in `f2min` inverts the bound: `lo_blocks_u` is
  *decreasing* in u, so `U − 6` gives an upper bound on the post-move value and
  silently over-prunes. The E ≤ 29 gate caught it at once — the classical 873
  disappeared. Same class of bug as the two earlier ones, same gate caught it.

## 12d. The family reformulation, and Family Quantisation

The Coset Lemma is really a change of variables, and saying it that way exposes
something new.

The arc-to-arc δ step **is** right multiplication by a — `δ(σ^(n-1)(g)) = g·a`
for all n! generators (`code/families6.py` checks this). So a 2-loop is a coset
g⟨a⟩, and since a ∈ H = ⟨a,b⟩ the n!/(n−1) loops fall into the n cosets of H,
the **families**. Each family has (n−2)! loops and, by the Coset Lemma, is an
exact cover of the (n−1)! classes. Hence every class has exactly **one arc
start per family**, and:

> **A split-free walk is an n-colouring of the (n−1)! classes** — the colour of
> C being which family supplies C — **together with an ordering.**

Both v and B are functions of the colouring alone:
B = Σ_f Σ_{L ∈ f} #(maximal δ-arcs of the f-coloured classes of L). At n = 6
the monochromatic colouring gives B = 24, and the best of 2000 random
colourings gives B = 86 — so B ≤ 29 is a severe rigidity condition, which is
where the remaining leverage most plausibly sits.

### Family Quantisation

The B = 24 walks are exactly the exact covers, and a cover need not sit inside
one family: at n = 6 the 10068 covers spread over 1 to 6 families. But they do
not spread freely.

> **CONJECTURE (Family Quantisation).** In every exact cover of the (n−1)!
> rotation classes by (n−2)! two-loops, the number of loops taken from each
> family is divisible by **n − 2** — equivalently, each family supplies a
> multiple of (n−1)(n−2) classes.

`code/quantise.py` enumerates *all* exact covers and checks it exhaustively:

| n | loops | families | covers | family splits |
|---|---|---|---|---|
| 4 | 8   | 4 × 2  | 4     | (2) |
| 5 | 30  | 5 × 6  | 25    | (3,3)×20, (6)×5 |
| 6 | 144 | 6 × 24 | 10068 | (12,8,4)×2880, (8,8,4,4)×1800, (12,4,4,4)×1680, (16,4,4)×1080, (8,8,8)×1080, (8,4,4,4,4)×540, (16,8)×450, (12,12)×300, (20,4)×180, (4,4,4,4,4,4)×72, (24)×6 |

Every entry is a multiple of n − 2. A second, independent reading of the same
fact: collect the distinct *sets* of family-f loops that occur across all
covers — at n = 6 there are 1612 of them, with sizes exactly
4, 8, 12, 16, 20, 24, and at n = 5 exactly 3 and 6.

n − 2 is precisely ord(s) for s = a^(n−2)b, the Pentad element, which is why
this looks like the right invariant. It is *not*, however, simply "covers are
unions of ⟨s⟩-orbits": ⟨s⟩ does not act on loops (a loop has n−1 generators
lying in different ⟨s⟩-orbits), and at n = 6 the 66 minimal 4-element
restricted sets overlap rather than partitioning a family's 24 loops. The
mechanism is open; the fact is exhaustive at n = 4, 5, 6.

This does not by itself close B ≥ 25 — it is a statement about exact covers,
and B ≥ 25 walks use partial loops. A version of it for partial loops is the
natural next target.

### Block structures do not enumerate either

`code/blockstruct6.c` strips the ordering away entirely and counts the
*partitions of the 120 classes into δ-arcs* — the pieces being the 144 × 21 =
3024 arcs of the loops, kept distinct even when they cover the same classes,
since the loop fixes the arc's starting permutation. At B = 24 every piece must
be a whole loop and it returns **10068**, matching the independent DLX count.
At B ≤ 25 it does not terminate. So the ordering-free relaxation is no smaller
than the walk search, and that route is closed too.

## 12e. The family lens on the 7-symbol champions

`code/n7_families.py` runs the §12d family decomposition over all 140 known
7-symbol strings. At n = 7 the structure is 840 loops = **7 families × 120**,
each family an exact cover of the 720 rotation classes (asserted, not assumed).

### A theorem that falls straight out

A family meets each class exactly once, and a minimal walk visits each of the
5040 permutations once, so its arc starts are distinct permutations. Two arcs
whose starts share a family therefore lie in **different** classes. Hence:

> **Splits are never intra-family.** The arcs covering a rotation class have
> pairwise distinct families, so a class is covered by at most **n** arcs, and
> `arcs from family f = classes covered from family f` exactly.

Checked on all 140 strings. It also makes `A = (n−1)v − R` split cleanly over
families as `A_f = (n−1)ℓ_f − c_f ≥ 0`, with ℓ_f loops entered and c_f arcs
taken from family f.

Empirically the bound k ≤ n is loose: **no champion has a class covered more
than 3 times**, with typical profiles like 598 classes once, 120 twice, 2
thrice.

### What the champions look like

All 136 have v = 142 and T = 142 — HPV exactly tight. Beyond that they are
*not* uniform:

* families used: 6 (88 strings), 7 (47), 5 (1);
* loops per family varies widely — (50,27,23,22,18,2), (41,41,32,12,6,5,5),
  (58,25,25,18,8,8), … — dozens of distinct patterns;
* `A = 132 − S` takes eight values over the 136: A = 8 (82 strings), 14 (29),
  13 (10), 9 (5), 18 (4), 12 (3), 17 (2), 10 (1). So S is *not* constant
  either — S ∈ {114 … 124} — and B + Y moves to compensate, keeping T = 142.

The one sharp pattern:

> **The accidents concentrate.** A_f > 0 in exactly one family for 112 of the
> 136 champions and in exactly two for the other 24 — never three. So at least
> five of the seven families have **every entered loop completely traversed**.

Caveat, and it matters: these 136 strings are all `7_5906_derived_*`, so they
may share provenance, and a pattern common to them may be a signature of one
construction rather than a theorem. This is recorded as an observation to try
to prove or break, not as a lemma.

### The non-champions are the interesting contrast

| string | length | v | loops per family | A |
|---|---|---|---|---|
| jupiter | 5907 | 140 | (61,41,26,9,3) | **0** |
| Egan | 5908 | 144 | (24,24,24,24,24,24) | 1 |
| derived-from-872 | 5912 | 120 | (120) | 0 |
| palindromic | 5913 | 120 | (120) | 0 |

Both split-free strings are **single-family exact covers** — the monochromatic
case of Family Quantisation, one dimension up. Egan's 5908 uses six families
with exactly 24 loops each, which is a construction signature worth
understanding. And jupiter reaches A = 0 at v = 140: every entered loop fully
traversed, S = 120, B + Y = 23, T = 143.

### Why this does not yet move the bound

The per-family counting reproduces what is already known and no more.
`c_f ≤ (n−1)ℓ_f` summed over f is exactly `A ≥ 0`, i.e. `v ≥ R/(n−1) =
120 + S/6`; with HPV that gives `T ≥ 120 + S/6`, which is §13's weak
`S + B ≥ 120 − 5S/6` again. Family *changes* are not obviously costly either:
an om jump (right multiplication by b) stays inside a family and costs the same
weight 3 as a family-changing weight-3 jump, so the only handle is the
forced-om threshold `l + l' ≥ 2n−3 = 11`, which at n = 7 constrains only
(6,6), (6,5), (5,6).

The live question this raises: the measured minimum of T sits at v = 142
(T = 142), rising to 143 at v = 140 and 148–149 at v = 120. If that shape
— T bounded below by something that *increases* as v falls away from 142 —
can be proved rather than observed, it is exactly what the ladder needs.

## 12f. Quantisation does not reach v = 121 — and the sharpened target

The cheapest open +1 on s(7) is the **v = 121, A = 0** state (§6): every other
rung already yields T ≥ 122, this one yields exactly 121. A = 0 forces every
entered loop to be fully traversed, so as a *loop system* the state is 121 loops
covering all 720 classes with multiplicity 726 — an exact cover with exactly
S = 6 collisions. Since 121 ≢ 0 (mod n−2 = 5), Family Quantisation would kill it
outright if it survived collisions.

It does not. **Take any exact cover and add one more loop.** All classes are
still covered, the multiplicity is (n−1)(v+1), so it is a legitimate saturated
system with exactly n−1 collisions — and the family counts pick up a 1. At
n = 6 that turns [24] into [24, 1], residues [0, 1]. Quantisation is an
*exact-cover-only* phenomenon; the tolerance is zero collisions, not "somewhere
below jupiter's 120". The same construction at n = 7 — exact cover of 120 loops
plus one redundant loop — *is* the v = 121, A = 0 state.

Nor is the state rigid the other way: a search at n = 6 finds a size-25
saturated system in which **no** loop is wholly redundant, so the collisions can
be spread as well as concentrated. Loop combinatorics alone says nothing here.
(`code/saturated6.py`.)

### The sharpened target

What the exercise does yield is a much better-posed version of the open problem.
The repo's transition count gives 23 ≤ #chains ≤ 25 — chains of complete
traversals cap at ord(s) = n−2 = 5, so #chains ≥ ⌈115/5⌉ = 23, while
#chains = #T-blocks + #(dirty T→T) ≤ 13 + 12 = 25. "Close a gap of 2" is vague.
Sharpen it by counting the *full* chains. If k chains have exactly 5 traversals
and the rest at most 4, then with C = #chains,

        115 ≤ 5k + 4(C − k) = 4C + k,

so C ≤ 25 forces **k ≥ 15**, and conversely **k ≤ 14 forces C ≥ 26 > 25** — a
contradiction, and the state dies. A chain of exactly 5 complete traversals is a
full ⟨s⟩-orbit, i.e. a **Pentad**, whose 5 loops are pairwise class-disjoint and
cover 30 classes (verified on all 1008 orbits in `code/pentad_orbits.py`). So:

> **TARGET.** In the v = 121, A = 0 state, show that at most **14** of the
> om-chains can be full Pentads. Equivalently: rule out 15 pairwise
> class-disjoint Pentads occurring simultaneously as om-chains there.

This is finite, sharp, and worth exactly +1 on s(7) (5885 → 5886). Note that
disjointness alone will not do it — 24 disjoint Pentads exist and partition the
720 classes, so 15 of them is not in itself an obstruction. The obstruction, if
there is one, has to come from the om-linkage geometry together with the six
two-run loops and the six collisions.

## 12g. SETTLED: no n = 6 champion is split-free

> **Theorem.** No split-free 6-symbol superpermutation has E ≤ 28. Since
> `length = 844 + E` for a split-free walk and `s(6) = 872 = 844 + 28`,
>
> **split-free ⟹ length ≥ 873.**
>
> The classical 873 *is* split-free, so this is exact: the shortest split-free
> 6-superpermutation is **873**, and **every 872 champion has splits**.

Exhaustive, by the search of §12c/§12f with the hoisted bound:
**2203 leaf verdicts, 2.98 × 10¹³ nodes, zero FEASIBLE, zero cap hits.**
Certificate: [`data/e28_certificate.txt`](../data/e28_certificate.txt).

### The coverage tree

The search is a deterministic partition, so a shard is either resolved directly
or delegated to a refinement — and a refinement counts only if it is itself
complete. Resolved bottom-up:

```
2000 shards @depth 8              1998 direct verdicts
 |- shard 1199 -> 20 of 40000     19 direct + piece 19199
 |    `- 19199 -> 48 @depth 16    48 direct
 `- shard 0    -> 20 of 40000     19 direct + piece 0
      `- 0 -> 48 @depth 16        47 direct + piece 0
           `- 0 -> 16 of 768      14 direct + pieces 0, 720
                `- {0,720} -> 8 each of 6144    14 direct + 0, 1488
                     |- 1488 -> 8  @depth 24     8 direct
                     `- 0    -> 18 @depth 24    16 direct + pieces 5, 16
                          `- {5,16} -> 9 each of 162    18 direct
```

Every refinement was verified **exact by node accounting before being used** —
work below the cut computed both ways: 1,784,777 at depth 8; 370,586,159 at
depth 16; 70,566,880 at depth 24. Nothing double-counted, nothing lost through
a gap in the partition.

### Why it needed six levels of refinement

The cost is wildly unbalanced: shard 0's region alone consumed 5.13 × 10¹²
nodes, a quarter of what the other 1998 shards took together. The reason is
structural — the leftmost branch is the all-δ spine, the walks that stay inside
loops as long as possible, which is exactly the region the bound prunes least.

And there is a trap worth recording: **modular refinement at a fixed depth can
never split it.** The filter keeps node j iff `j % N == myshard`, and
`0 % N == 0` for every N, so node 0's subtree stays whole in piece 0 at every
modulus. Refining finer at the same depth splits the *other* pieces and leaves
the spine untouched. It has to be cut **deeper**, which is why the binary grew
a second cut (depth 16) and then a third (depth 24). Each new level composes
inside the previous one, so no completed work is discarded.

### Soundness

Three binaries were involved: `sf6c` (one cut), `sf6d` (two), `sf6e` (three).
The extra levels change only the parallel decomposition, never the pruning —
asserted, not assumed:

* all three return **identical node counts** (14483, 5357787, 77386900 on the
  shared cases);
* all three still **FIND** the known E = 29 walk (the classical 873).

That last gate is the one that matters. An exhaustive "no solution exists" is
worth exactly as much as the proof that the search can still find the solutions
that *do* exist — three separate over-pruning bugs in this project were caught
by it and by nothing else.

### Consequence for the working assumption

WA1 ("no minimal-length superpermutation is split-free, n > 5") is now a
**theorem at n = 6**. It remains open at n ≥ 7, and §12e's split-economy
measurements argue *against* extending it: the advantage of splits grows from
1 at n = 6 to 6 at n = 7.

## 13. What this does **not** do

It does not bound s(7). Split-freeness is a real restriction, and the known
n = 7 champions are nowhere near it — Egan/Houston 5906 has S = 124, R = 844,
and only ~18 blocks. The reason the argument stops there is visible in the SBY
identity: a split buys a **free loop switch**. δ out of a *partial* arc at
u·c^(k−1) lands on u·c^(k−1)d, which for k < n is a generator of a *different*
loop, so a block is no longer confined to one loop and the length-≤6 cap
evaporates. Houston's 872 is the extreme case: 25 splits collapse 120 blocks
into 4.

The natural next target is therefore a lower bound on **S + B** — the SBY
identity says s(7) ≥ 5889 is exactly `S + B + Y ≥ 125`. The best elementary
bound I have in that direction is far too weak. Writing P = S + n_split for
the number of partial arcs (proved in `blockcount.py`), at most P cheap jumps
can be "dirty" (out of a partial arc), the walk's arcs therefore fall into
B + dirty clean runs each confined to one loop and so of length ≤ n−1, and
R ≤ 6(B + 2S) gives only S + B ≥ 120 − 5S/6. Recovering even HPV from that
route needs the per-loop δ-edge count, and it does not go past it.

Two other facts measured along the way, recorded here because they are the
kind of thing a sharper argument would use:

* **D = −S exactly** on both n = 6 extremal strings, where D = (n−2)v − C_d is
  the δ-edge deficiency and C_d counts δ-type cheap jumps. Only D ≥ −P is
  proved; D ≥ −S survived 600 random n = 5 walks with slack 108.
* The per-loop bound "no loop uses all n−1 of its δ edges" and the cap
  C_d ≤ (n−2)v **both fail once classes split** — Houston 872 has
  C_d = 141 > 4·29. With a split, a δ edge of loop L can be supplied by an arc
  that does not start at L's generator, and the "using them all closes a
  cycle" argument evaporates.

---

## 13. Do split-free champions come back at large `n`?

§12g proved none exists at n = 6. The natural hope is that they return once `n`
is large, since the *relative* advantage of splitting shrinks. This section
settles the shape of that question. The short answer is **no, and the reasoning
that suggests otherwise conflates two different quantities.**

### 13a. `σ(n) ≤ s(n−1) + n!` — and `Σ k!` is not the split-free optimum

Write `σ(n)` for the shortest split-free length. The classical string has length
`Σ_{k≤n} k!` and is split-free, which invites the guess `σ(n) = Σ k!`. That
guess is **false at n = 7**: on disk there is a split-free superpermutation of
length **5912**, one shorter than `Σ k! = 5913` — and

```
5912  =  872 + 5040  =  (the n = 6 CHAMPION) + 7!
```

So the standard recursion is not classical-to-classical. Read off the
permutations of `[n−1]` in order of first occurrence, replace each `π` by
`π · n · π`, and merge consecutive images at their existing overlap: the output
has length `L + n!` and is **split-free whatever the input was**.
`code/sfrec.py` builds it and checks both halves:

| input | output | valid | `S` |
|---|---|---|---|
| 153-chaffin (n = 5) | n = 6, length **873** | ✓ | **0** |
| houston 872 (n = 6) | n = 7, length **5912** | ✓ | **0** |

> **`SFREC`.** `σ(n) ≤ s(n−1) + n!`, and it is tight at n = 4, 5, 6
> (`σ(6) = 873` is §12g).

Immediately: **a split-free champion exists at `n` iff `s(n) = s(n−1) + n!`.**

### 13b. The gap grows factorially, even as the ratio vanishes

Define `g(n) = s(n−1) + n! − s(n) ≥ 0`. A split-free champion needs `g(n) = 0`.

| n | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
|---|---|---|---|---|---|---|---|---|---|
| `g(n)` | 1 | **0** | 1 | 6 | 22 | 118 | 719 | 5039 | 40319 |
| `g(n)/s(n)` | 3e−2 | 0 | 1.1e−3 | 1.0e−3 | 4.8e−4 | 2.9e−4 | 1.8e−4 | 1.1e−4 | 7.7e−5 |

and if `s(n) = Egan(n)` exactly then in closed form

```
g(n) = (n−4)! − 1.
```

**Both readings are correct and they point opposite ways.** The relative
advantage `g(n)/s(n)` really does vanish — it decays like `n^{-4}`, since
`(n−4)!/n! = 1/(n(n−1)(n−2)(n−3))`. But championship is an **exact** question
about the absolute gap, and that grows factorially. "Splits matter less and less
as `n` grows" is true of the *ratio* and false of the *count*: a split-free walk
loses 719 characters at n = 10 and 40,319 at n = 12.

> So split-free champions exist at **n = 5** only (n ≤ 3 trivially; n = 4 has
> `g = 1`), n = 6 is proved negative, and nothing here suggests a return.
> There is no threshold `n ≥ 9` past which split-freeness stops costing.

### 13c. What would refute this

Two one-sided inputs, both of which could move:

* `g(n)` uses the **best-known** `s(n)`, so for n ≥ 7 it is an upper bound on
  the truth. A shorter champion raises `g`, making split-freeness cost *more*.
* `σ(n) ≤ s(n−1) + n!` is a construction, hence one-sided. A **better
  split-free construction** would lower `σ` and could close the gap.

The second is the live one, and it is not idle: the length-5912 string is
exactly such an improvement over the `Σ k!` guess, worth 1. Refuting `SFGAP`
means finding one worth `(n−4)!`. Nothing known does that, and the mechanism
argues against it — a split-free walk pays either the Chain-Count tax
`Y ≥ (n−3)! − 1` or a `B`-tax to fragment out of it, while every champion has
`Y = 0`.

**Note the one genuinely open case.** At n = 7, `σ(7) ∈ [5889, 5912]` — the
lower bound is §11's split-free ladder, the upper is the 5912 above — and
`s(7) ≤ 5906` sits *inside* that interval. So "no split-free champion at n = 7"
is **not** proved; it needs `σ(7) ≥ 5907`, i.e. the split-free floor `β₇` raised
from 125 to 143. That is 18 units, and it is the concrete open problem behind
this section.
