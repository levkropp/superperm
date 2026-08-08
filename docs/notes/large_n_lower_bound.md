---
layout: math
title: "The lower bound at large n: s(n) ≥ Egan(n) − 1, and the one lemma it hangs on"
---

# The lower bound at large n: `s(n) ≥ Egan(n) − 1`, and the one lemma it hangs on

*Status: programme note (August 7, 2026). What is proved is tagged; what is
measured is tagged; the rest is the plan. Related: [the gain-one
note](gain_one_kernel) (the design side), [`pbound`](pbound) §§13–16
(RUNGEQ / PENTCAP / the ladder).*

## 1. The target, restated

With `s(n) ≤ Egan(n) − 1` for all `n ≥ 8` (verified here through n = 13),
the whole question at large n is now one-sided: **can the lower bound be
raised to `Egan(n) − 1`?** Current best lower bounds (Hunter & Raudvere,
Lean) sit at `Egan(8) − 102` and fall further behind as n grows; HPV is
`Egan(n) − (n−3)!`. A matching lower bound would pin
`s(n) = Egan(n) − 1` for all `n ≥ 8`.

**Honest caveat, stated up front.** Gain-*two* exists at n = 7 (the 5906
champions, `Egan(7) − 2`). So `s(n) = Egan(n) − 1` for all `n ≥ 8` is a
conjecture, and its negation is exactly the 46203 question at n = 8. The
two questions are the same coin; this note is the lower-bound side.

## 2. The ledger reduction (both sides of the coin)

With `T = length − base(n)`, `base(n) = n + n! + (n−1)! − 3`,

```
T = (n−1)(v − (n−2)!) + (B + Y − A),        gain over Egan = (B + Y − A)/(n−2)
```

— the last by the Split Identity and the Egan vertex `(v = (n−1)(n−3)!,
B+Y−A = 0)`. Every known word is HPV-tight, so this is exact. The gain
landscape:

| word | n | v | B+Y−A | gain |
|---|---|---|---|---|
| Egan | any | (n−1)(n−3)! | 0 | 0 |
| Houston 872 | 6 | 29 | 4 | 1 |
| 5906 champions | 7 | 142 | 10 | **2** |
| Raudvere 46204 | 8 | 839 | 6 | 1 |
| Echols 408965 | 9 | 5759 | 7 | 1 |

## 3. The equality shape, proved and measured

`RUNGEQ` **[THM]** (`pbound` §15): sitting one below the ladder's need at
any rung forces `B = comps`, `Y = p − 1`, all inter-chain links of weight
exactly 4, and average chain length exactly `n−2` (at `A = 0`; more with
accidents).

Measured on the actual gain-one words (this repo, August 7):

| word | T | S | comps | p | CH3 |
|---|---|---|---|---|---|
| Raudvere 46204 | 839 | 833 | **6 = n−2** | **1** (exact) | 839, **tight** |
| Echols 408965 | 5759 | 5752 | **7 = n−2** | **1** (exact) | 5759, **tight** |

So the gain-one design is *one free chain of `n−2` components joined at
weight 3*, and CH3 cannot see it — the bound reads exactly `T` there. (The
5906 is the same shape one level down: `comps = 18, p = 1`, one chain.)

## 3a. The champions' fringe anatomy — and the fringe-price route is dead

Splitting each walk into blocks (maximal weight-≤2 runs) and chains (split
at weight-≥4 joins), tagging every weight-3 join core/fringe by FORCE
(exit arc full and `tr + ld ≥ 2n−3`):

| word | gain | blocks | chains | core joins | fringe joins |
|---|---|---|---|---|---|
| Egan 5908 / 46205 | 0 | 1 | 1 | 0 | 0 |
| Houston 872 | 1 | 4 | 1 | 2 | 1 |
| Raudvere 46204 | 1 | 6 | 1 | 1 | 4 |
| Echols 408965 | 1 | 7 | 1 | 1 | 5 |
| **5906 champion** | **2** | **18** | **1** | **7** | **10** |
| 5913 exact cover | — | 120 | 24 | 96 | 0 |

The 5906's 10 fringe joins match the corpus's earlier figure exactly, and
its core stretches are `[1,2,1,3,1,2,1,3,1,2,1]` — all within the n−2
core cap. The read across the table: **fringe joins are cheap and
abundant, and the champions use few**. One fringe join buys a whole extra
core stretch of up to `n−2` components, so the count-price of a chain is
tiny (the 5906's 18 blocks cost 10), and the available fringe at champions
is ~`S` (hundreds). No scarcity ⟹ no bound. This confirms §10c of
`pbound` ("the route fails, and cleanly") on the full current champion
set: **the fringe-price route to a lower bound is dead in every
count-based form**; its structural content is exactly the cap theorems
already proved (CORECAP/PENTCAP). What remains open is the top band
itself — the equality case's realizability, which is the fill question.

## 4. The one lemma the lower bound hangs on — and a first theorem

`PENTCAP` **[EXH]** (`pbound` §16): weight-4-linked chains of pairwise
class-disjoint **complete Pentads** cap at `n−3` — exhaustive at n = 6, 7,
8 (caps 3, 4, 5). That kills `T = Egan_T − 2` at **rung 0** (every
component complete), which is why `v = (n−2)!` champions are excluded at
n = 6, 7, 8 (`EGAN1P`).

At rung `j > 0` the equality components **span several loops**, and
PENTCAP does not apply directly. The missing general lemma is the
multi-loop analogue (MLCAP): the same cap for chains whose components may
span several 2-loops.

**But a first multi-loop theorem already falls out of the pieces** — the
point of this note:

> **`RUNGJ` [THM]** *(conditional on PENTCAP's cap `n−3` at the given n —
> exhaustive at n = 6, 7, 8)*. If a complete walk at rung `j`
> (`v = (n−2)! + j`) has `T = Egan_T − 2`, then
>
> ```
> j · ((n−1)(n−2) + 1)  ≥  (n−3)! − (n−2) + A·(n−2),
> ```
>
> where `A` is the walk's accident count. Equivalently, **`T ≥ Egan_T − 1`
> at every rung `j < ((n−3)! − (n−2)) / ((n−1)(n−2) + 1)`** — a
> factorially-long proved prefix of the rung ladder, at general n.

**Proof.** At `T = Egan_T − 2`, `RUNGEQ` forces `B = comps`,
`Y = p − 1`, `p = (n−3)! − j − 1`, `comps = (n−2)! − (n−2)j + A`, all
intra-chain joins of weight exactly 3 and all inter-chain links of weight
exactly 4. The `p` free chains form a single weight-4-linked sequence in
walk order. A *pure* chain (all components complete Pentads) has its
intra-joins at weight 3, hence is an om-chain — an `⟨s⟩`-orbit segment
(Pentad Lemma, [THM]). A maximal run of pure chains therefore embeds as a
PENTCAP sequence over distinct orbits (distinct, because the segments are
pairwise class-disjoint), so **a pure run has at most `n−3` chains**.
Chains containing a multi-loop component are few: merges satisfy
`Σ(μ−1) = v − comps ≤ S = (n−1)j − A` (A2, [THM]), so there are at most
`S` mixed chains and at most `S + 1` pure runs. Hence
`p ≤ (S+1)(n−3) + S`, i.e.
`(n−3)! − j − 1 ≤ ((n−1)j − A + 1)(n−3) + (n−1)j − A`, which rearranges
to the stated inequality. ∎

**The boundary** (rung `j` up to which `T ≥ Egan_T − 1` is proved, A = 0):

| n | rungs proved (`j ≤`) | top rung (champions) |
|---|---|---|
| 6 | 0 | 5 (Houston, A=0) |
| 7 | 0 | 22 (5906, A=8) |
| 8 | **2** | 119 (Raudvere) |
| 9 | **12** | 719 (Echols) |
| 10 | **70** | 5039 |
| 12 | **3,330** | 362,879 |

Consistency checks: the 5906 (`j = 22, A = 8`) needs `22·31 ≥ 19 + 40` —
holds (638 ≥ 59); Houston (`j = 5, A = 0, n = 6`) and both gain-one words
sit far above their boundaries, as they must. At n = 7 the boundary is 0 —
the method cannot see rung 1 there, which is exactly where the small-n
exception lives.

The theorem converts "the rung ladder" into: a proved prefix growing like
`(n−3)!/n²`, then an open band of width roughly `(n−3)!` where champions
currently live. **Any word beating `Egan(n) − 1` must sit within that top
band, or spend accidents** (each accident buys `(n−2)/((n−1)(n−2)+1)`
rungs of slack). It is the first general-n rung theorem since RUNGEQ, and
it is unconditional at n = 6, 7, 8 (PENTCAP exhaustive there).

**What MLCAP would add.** If mixed chains also cap below `n−3`, the
boundary moves up; if pure-and-mixed chains jointly cap at `n−3`, the
proved prefix extends to essentially the whole ladder and
`s(n) ≥ Egan(n) − 1` follows at large n.

## 4b. The core cap is a theorem at general n (CORECAP [EXH] → [THM])

The input the whole fringe instrument rests on — the core cap `n−2`,
previously only *exhaustive* at n = 5, 6, 7 (§12b) — is now proved at
general n. The proof is elementary algebra from the explicit forms plus
the repo's exit structure ([THM] FORCE: the unique core exit is om, and
two consecutive length-`n−2` blocks never chain).

**The elements, made explicit** (direct from their definitions; verified
numerically at n = 5–10):

```
a = (1 2 … n−1)              the (n−1)-cycle fixing n; ord(a) = n−1
b: i ↦ i+2 (i ≤ n−3),  n−2 ↦ 2,  n−1 ↦ 1,  n ↦ n
s = a^{n−2}b = (1 2 … n−2)   ⟹ ord(s) = n−2 — the Pentad order is a one-line computation
u = a^{n−3}b                 ⟹ u² = e   (four-case check: b a^{n−3} b = a²)
```

**The two identities the collision mechanisms rest on.** With
`s = a·u` (definitional): `s·u = a·u² = a`, and
`u·s^{n−3} = u·s^{−1} = u²·a^{−1} = a^{−1} = a^{n−2}` (using
`ord(s) = n−2`).

**The word game.** A core chain's blocks have length `n−1` (an s-step)
or `n−2` (a u-step), never two u's in a row (FORCE). Three mechanisms,
each now a proved identity:

- **M1** (`s·u` must be terminal): after steps `s, u` the position is
  `(block m−1's start)·a` (since `s·u = a`), which block `m−1` burned at
  power 1 — any further block dies at its first generator. So an `s.u`
  factor is always terminal.
- **M3′** (pure-s boundary): `s^{n−2} = e` returns the position to the
  start; any extension's first class is the start's own class, burned by
  block 1.
- **M2** (`u` then a long s-run): after prefix `u·s^{n−3}` the position
  is `a^{−1}` (the second identity); the next block's second generator is
  the start's class, burned by block 1.

**Classification and cap.** No-`uu` plus M1 forces every valid word into
one of four shapes — `S^a (a ≤ n−2)`, `S^a.u (a ≤ n−3)`,
`u.S^a (a ≤ n−3)`, `u.S^a.u (a ≤ n−4)` — and each shape's boundary
extension dies by M1, M2 or M3′. Hence **a core-only chain of single
blocks covers at most `n−2` blocks, at every `n`**; the Pentad chain
`S^{n−2}` attains it. ∎  The exhaustive evidence agrees everywhere:
the cap `n−2` was computed at n = 5–8 (witnesses `[3,4,3]`, `[4,5,5,4]`,
`[5,6,6,6,5]`, `[6,7,7,7,7,6]`), the four-shape census at n = 5, 6, 7
(10/14/18 words, no fourth mechanism), and the identities at n = 5–10.

**Consequence.** `PFRINGE` (`p ≥ ⌈comps/c⌉ − F`, §12c) now stands on a
theorem at general `n`: `p ≥ ⌈comps/(n−2)⌉ − F` unconditionally. The
fringe price is proved — a fringe edge's freedom costs a short block,
and short-block (core) runs cap at `n−2` by proof, not by enumeration.

**And PENTCAP is a theorem too (§4c below)** — the weight-4 orbit-chain
cap `n−3` is proved at general n, so `RUNGJ` is now unconditional.

**Measured, and the naive form of MLCAP is dead** (August 7, exhaustive
DFS, exit model made generous in the sound direction): components of 1–2
loops
weight-4-chain to **≥ 20 at n = 6, ≥ 84 at n = 7, ≥ 416 at n = 8** — no
cap below Pentad size exists, and 2-loop components chain *longer* than
single loops. PENTCAP's cap is a property of *complete* Pentads (big
burns), not of class-disjointness alone. So a cap stated over δ-components
plus weight-4 links is **false already at n = 6** — registered as a dead
end with its witness chains. The viable MLCAP must instead use the RUNGEQ
equality structure itself (weight-3 om intra-chain joins — the cap lives
in the core, where `CORECAP` already gives `n−2` exhaustively), i.e. a
statement about how many *fringe* doors the equality case can afford —
`FRINGE`/`PCOUPLE` measured: fringe edges are abundant exactly at
champions, zero at `S = 0`.

## 4c. The weight-4 cap is a theorem at general n (PENTCAP [EXH] → [THM])

`RUNGJ`'s remaining input is now proved too: a weight-4-linked sequence of
pairwise class-disjoint `⟨s⟩`-orbits has at most `n−3` of them, at every
`n` — and the mechanism is transparent, not just enumerated. All gates in
`code/pentcap_thm.py`.

**Setup.** A chain visits orbits one at a time; each orbit is entered at
some `g` and left by a weight-4 door. Everything is right multiplication,
so the chain-end exit is `x = g·E` for a fixed group element `E`.

**1. The E-form (derived, was G1).** From the explicit forms of §4b, with
`c = (1 2 … n)` the rotation (`end_of(u) = u·c^{−1}`),

```
E = s^{n−3} · a^{n−2} · c^{−1} = s^{−1} ∘ a^{−1} ∘ c^{−1}
  = (n, n−1, n−2, 1, 2, …, n−3),
```

a direct telescoping: `E(i) = i−3` for `i ≥ 4`, `E(1) = n`, `E(2) = n−1`,
`E(3) = n−2`. Verified at n = 6–10.

**2. Suffix and state laws (from the E-form).** `(g·E)[4:] = g[1:n−3]` —
the door-preserved suffix of the exit equals the entry's positions
`1..n−4` — and with `T(g) := g[0:n−3]`, a door-entered next entry has
`T(g′) = (T(g)[1:], q[0])`: the state rotates one step per orbit.

**3. Ordered-target law (proved).** "Ordered" = the canonical rep has
`2,3,…,(n−3)` in increasing relative order — a cyclic-order property of
the arrangement, rotation-invariant. If `T(g)` is a rotation of
`(1,…,n−3)`, then **every** weight-4 door target of `g·E` lands in an
ordered class: the target is `(k+2,…,n−3,1,…,k, q)` where `q` permutes a
set that always contains `k+1`, so `2..(n−3)` stay cyclically increasing
for every `q`.

**4. Mask law (proved, was G2).** `s` and `a` are single position-cycles
(the `(n−2)`- and `(n−1)`-cycles), and a single position-cycle preserves
the cyclic order of every symbol subset. So orderedness survives every
orbit step: an entry with `2..(n−3)` cyclically ordered has its entire
orbit burning ordered classes. Verified exhaustively at n = 6–8
(18/18, 24/24, 30/30 such entries) and at n = 6–9 on random entries.

**5. The budget.** Ordered classes number
`(n−1)!/(n−4)! = (n−3)(n−1)(n−2)` (counted in the gate). Each chain orbit
burns `(n−1)(n−2)` of them, and chain orbits are pairwise class-disjoint —
so **at most `n−3` orbits per chain**, attained (the maximal chains of the
exhaustive searches). ∎  And now the mechanism is visible: the state
rotates one step per orbit through a 4-cycle, so after `n−3` orbits every
door lands on an ordered — already burned — class. The chain dies of
**unreachability**, not scarcity: the burned fraction is only
`1/(n−4)!`.

**Consequence.** `RUNGJ` is now unconditional at every `n` (both cap
inputs are theorems), and the `EGAN1P` CP-SAT certificates at n = 6, 7, 8
have a combinatorial proof of the same fact.

A plausible route is **defect counting**: at rung `j` only a bounded
number of components can be multi-loop (each split class costs a merge),
so for small `j` most chains are pure Pentad chains, capped at `n−3`, and
the RUNGEQ average `n−2` is unreachable. The argument weakens as `j`
grows — at the top rungs nearly all components are multi-loop — which is
exactly where the gain-two constructions (n = 7, and the n = 8 kernel
candidates of the gain-one note) live. Partial versions (rung `j ≤ J`)
still tighten the lower bound conditionally, in the style of the 22-rung
ladder at n = 7.

## 5. Why not the other routes

- **HPV/CH3**: both are *tight* on the gain-one words (§3) — no
  ordering-free bound of this family can exclude them.
- **The SBY ladder** (`block_count_lemma`): gives `T ≥ (n−2)! + 1` at
  best — `Egan − (n−3)! + 1`, far short.
- **Lean certificates (Hunter & Raudvere)**: the strongest lower bounds,
  but a different method; their improvements over HPV grow slowly
  (+2, +4, +18 at n = 6, 7, 8) and do not obviously reach `Egan − 1` at
  any n ≥ 7.

The chain-cap route is the only one whose proven pieces (RUNGEQ's shape,
PENTCAP's cap) already sit at the right scale.

## 6. Status and next steps

- **[THM]** RUNGEQ equality shape; **[THM]** **PENTCAP at general n** (§4c,
  the weight-4 orbit cap `n−3` proved);
  **[MEAS]** gain-one words are single-chain, CH3-tight (§3).
- **[THM]** **`RUNGJ`** (§4): `T ≥ Egan_T − 1` on a factorially-long rung
  prefix — registered and corpus-gated (`code/lemmas.py`, 237/237), now
  **unconditional** at every n.
- **[THM]** **`CORECAP` at general n** (§4b): the core cap `n−2` is now
  proved, not enumerated — gates in `code/corecap.py`, and `PFRINGE` is
  unconditional with it.
- **[DEAD]** **naive MLCAP** (§4): no cap over δ-components + weight-4
  links below Pentad size exists (measured chains ≥ 416 at n = 8).
- **Next**: the multi-block component case of CORECAP, and then the
  top-band question (where champions live): with both caps proved, the
  lower bound at large n hinges on the equality case's fringe pricing.
- **Either outcome is a result**: a fringe-priced chain lemma tightens the
  lower bound at large n; a counterexample fill at n = 8 is a new record
  (46203) and reshapes the conjecture `s(n) = Egan(n) − 1`.
