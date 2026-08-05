# The ordering, and the two theorems it broke

The target was to promote `A1EQ` to **[THM]**: *A = 1 ⟹ the Egan vertex
(`d = (n−3)!`, `B = 1`, `Y = 0`)*, measured on all 44,564 corpus strings.

It cannot be promoted, it is false, and chasing the witness turned up a second
and larger error in `IN5`. Both are now witnessed by verified superpermutations
built by [`code/inflate.py`](../code/inflate.py).

---

## 1. `A` is ordering-free and `B` is not

Read `build.coords` directly. `A` comes from the arc-start **set**:

```python
entered = {st.loop_of[g] for g in starts}
v = len(entered)
A = (n - 1) * v - R                      # Split Identity
```

while `B` and `Y` come from consecutive pairs:

```python
for i in range(len(design) - 1):
    w = weight(ends[i], starts[i + 1])
    if w >= 3:
        B += 1
        Y += w - 3
```

Permuting the arc list therefore cannot move `A`, and generically does move
`B`. Measured over 40 arc permutations of `5908-egan`:

| ordering-**free** — never moved | ordering-**dependent** — always moved |
|---|---|
| `R, S, v, d, A, comps, m, mu_max, n_partial` | `B, Y, T, clean, dirty, N, length` |

registered as **`ORD` [THM]**.

**`INFL` [THM] — the Inflation Lemma.** Any walk with `B < R` has a reordering
of the same arc set with `B' = B+1` and `T' ≥ T+1`: cut the arc sequence where
two arcs are joined by a free (weight ≤ 2) jump and swap the two pieces; the new
junction is not a free edge, so it costs weight ≥ 3.

> **Audit rule.** No implication of the form *(ordering-free hypothesis) ⟹
> (upper bound on `B`, `Y` or `T`)* can be a theorem. Only **lower** bounds on
> those three survive.

`A1EQ`'s forward direction was exactly of the forbidden shape.

## 2. The witnesses

All verified with `permgraph.is_superpermutation`, and the ledger re-measured
from the **re-parsed string** with the independent `blockcount`/`dirty` modules,
not just from the design.

**Rotate the arc list** — same arc set, `A` fixed, `B` inflated:

| n | source | result |
|---|---|---|
| 6 | `873-egan` | length **874**, `A=1, B=2` |
| 7 | `5908-egan` | length **5909**, `A=1, B=2` (k = 100, 200, 431) |

**Union one unentered 2-loop into `K`** — `v` rises by 1 and `R` by `n−1`, so
`A = (n−1)v − R` is unchanged, but `d` and `comps` both move:

| n | result |
|---|---|
| 6 | length 878…881, `A=1`, **`d=7`**, `comps ∈ {1,3}` |
| 7 | length 5914…5919, `A=1`, **`d=25`**, `comps ∈ {2,6}` |

So all three conclusions of `A1EQ` fail — `B = 1`, `Y = 0` and `d = (n−3)!`.
Registered as **`A1EQF` [REF]**; the surviving guarded version is **`A1EQO`
[MEAS]**.

The corpus was not lying, it was narrow: it holds only near-optimal strings,
and `A1EQ` is a statement about **optima**, not about walks.

## 3. The bigger casualty: `IN5` was never a theorem

`IN5` (`B ≥ comps`) rested on *"a block is a path in the δ-graph"*, which needs
every weight-2 jump to be `δ`. It is not. From `weight(u,v) = 2` we get
`u[2:] = v[:n−2]`, so `v = u[2:]` followed by `{u[0], u[1]}` in one of **two**
orders:

```
delta(u)    = u[2:] + u[1] + u[0]
sigma^2(u)  = u[2:] + u[0] + u[1]
```

`build.comps` follows only `δ`. A block that takes a `σ²` jump therefore spans
**two** δ-components, and `B < comps`.

**`SIG2` [THM] — when the σ² jump is available.** For `σ²(end_i)` to *start* an
arc, both `σ(end_i)` and `σ²(end_i)` must be arc starts; since the arcs of a
class tile its ring, `σ(end_i)` is the next start after arc `i`, so

> a `σ²` jump out of arc `i` requires the arc at `σ(end_i)` to have **length 1**.
> In particular **no `σ²` jump ever leaves a full arc** (a full arc has
> `μ_C = 1`, so its class has no second start).

**`IN5b` [THM] — the repair.** A block using `j` of these splits into `j+1`
δ-paths, so

> `B + σ2 ≥ comps`,  with  `σ2 ≤ #{arcs of length 1}`.

**Witnesses**, both `σ2 = 1`:

| n | length | `B` | `comps` | how |
|---|---|---|---|---|
| 6 | 881 | **2** | **3** | `873-egan` + loop 34 |
| 7 | 5914 | **1** | **2** | `5908-egan` + loop 5 |

The n = 7 one is a genuine single block spanning two δ-components — it also
refutes the `comps = 1` clause of `B1` (now **`B1c` [MEAS]**).

**And yet no real string does it.** Corpus scan:

```
44564 strings: 0 take a sigma^2 jump, 92 contain a length-1 arc
```

So the move is **available** in real strings — length-1 arcs occur at n = 5, 6
and 7 — and is **never taken**. `B ≥ comps` is a fact about optima with no proof,
which is precisely the status `C6b` (`B = comps` at an optimum) already had.

**Consequence.** `T ≥ S + comps` is not an ordering-free theorem. It was used
as the exclusion test in [`a1_argument.md`](a1_argument.md) §4; that section's
conclusion was *"the test is vacuous anyway"*, so nothing there is lost.

## 3a. Getting the bound back: the σ² exchange

`T ≥ S + comps` was the repo's only ordering-free lower bound, and every use of
it was against the *optimum*. That use is recoverable, because the σ² jump can
always be exchanged away.

**`SIG2X` [THM].** Let arc `A_p` end at `e` and jump `σ²` to `A_{p+1}` at
`σ²(e)`. By `SIG2` there is a length-1 arc `A_q` at `σ(e)`, sitting elsewhere in
the walk. In the ring of that class the three are consecutive:

```
[ A_p .... e ] [ sigma(e) ] [ sigma^2(e) .... A_{p+1} ]
```

so splice `A_q` out of its own slot and let the walk run straight through: all
three merge into **one** arc. Writing `X, Z` for `A_q`'s old neighbours and
`w1 = w(X,σ(e))`, `w2 = w(σ(e),Z)`,

> `R' = R − 2`  and  `length' − length = w(X,Z) − w1 − w2 ≤ 0`,

the inequality because weight is subadditive — the string `X → σ(e) → Z` is a
witness of length `w1+w2` for joining `X` to `Z`. The merged arc fits, since the
three are disjoint segments of one `n`-element ring. `R` strictly drops and
`R ≥ (n−1)!`, so iterating terminates. Hence

> **every superpermutation has one of length ≤ it with `σ2 = 0`.**

So the **minimum is attained at `σ2 = 0`**, where `IN5` does hold, and

> `min length ≥ base(n) + min over arc sets K of ( S(K) + comps(K) )`

is valid again. The tool is back, in the only form it was ever used.

**`SIG2Y` [THM] — and it explains the corpus.** At an optimum the exchange
cannot shorten, so `w(X,Z) = w1 + w2` exactly. Both `w1, w2 ≥ 2` (a weight-1
neighbour of the singleton would be the same arc), so two jumps become one of
weight ≥ 4:

> an optimum with `σ2 ≥ 1` implies an optimum with strictly larger `Y` and `B`
> — in particular some optimum has **`Y ≥ 1`**.

(Only *strictly larger*, not `Y ≥ σ2`: an exchange can create a fresh σ² jump
even as `R` falls, so the step count is bounded below by 1 and no more.)

Both witnesses hit exactly this, with `w1 = w2 = 2, w(X,Z) = 4`:

| n | length | before | after |
|---|---|---|---|
| 6 | 881 | `R=154 Y=2 B=2 σ2=1` | `R=152 Y=3 B=3 σ2=0` |
| 7 | 5914 | `R=869 Y=0 B=1 σ2=1` | `R=867 Y=1 B=2 σ2=0` |

Run backwards, this makes the question **decidable over a corpus**: a
σ²-using optimum is reachable only by reversing the exchange from a `σ2 = 0`
optimum, and each reverse step consumes a jump of weight ≥ 4 — of which a walk
has at most `Y`. Scanning all 43,096 n = 6 optima:

```
43096 optima, 808 carry a weight->=4 jump, 0 free reverse-exchange slots
```

**The known 872 set is closed under the move in both directions.** And length-1
arcs are *not* the obstruction: `872-nonstandard` has 8 of them and 20 of the
n = 7 champions have 1…12, so the σ² move is genuinely on offer at real optima
and still refused. The obstruction is finer — the heavy jump never splits at a
permutation interior to an arc.

## 4. Registry audit

Every claim, against the audit rule and against the `SIG2` correction.

| claim | hypothesis | conclusion | verdict |
|---|---|---|---|
| `ID1`–`ID4`, `KICK1` | — | identities | safe |
| `IN1`, `IN2` | — | ordering-free | safe |
| `IN3` (HPV), `KICK2` | — | **lower** bound on `T` / kicks | safe under `INFL` |
| `S5` (Exposure Bound) | — | lower bound on `T` | safe, and safe under `SIG2` too: an all-full loop's arcs are full, so by `SIG2` no `σ²` edge touches them and its δ-cycle is entered and left only by weight-≥3 jumps — exactly what the derivation assumes |
| `A2b` (`T ≥ v + Y`) | — | lower bound on `T` | statement safe under `INFL`, but its **derivation** went through `IN5`. Now a bare `[CONJ]` again; via `IN5b` the most one gets is `T ≥ v + Y − σ2` |
| `IN4` (`dirty ≤ n_partial ≤ 2S`) | — | ordering-dependent bounded **above** by ordering-free | safe: inflation only *lowers* `dirty` |
| `IN5` (`B ≥ comps`) | ordering-free | forces `B` up, so `T ≥ S + comps` | **[REF]** — killed by `SIG2`, not by `INFL`; **recovered against the optimum** by `SIG2X` |
| `A1EQF` (`A=1 ⟹ B=1`) | ordering-free | **upper** bound on `B`, `Y` | **[REF]** — killed by `INFL` |
| `B1` | `B = 1` — ordering-**dependent** | — | safe; `comps = 1` clause dropped |
| `C6b` (`B = comps`), `B3` | optimality guard | upper bound on `B` | safe **only** because of the guard; the unguarded forms are refuted by `INFL` |
| `MOD4`, `A3`, `B2`, `A1EQO` | corpus-narrow | — | measured on optima; `A3` already fails on the pool (67/108) |
| `A2` (`comps ≥ v − S`) | ordering-free | ordering-free | untouched |
| `S1`, `SYMM`, `A1`, `A1c` | — | — | untouched (`S1` loses its `≤ B` half, which was `IN5`) |

Two general lessons, both now cheap to apply:

1. **Guard or die.** Any claim bounding `B`, `Y` or `T` from above needs an
   optimality hypothesis in its statement, not just in its evidence.
2. **The corpus is all optima.** `IN5` survived 44,564 strings because optima
   never take the `σ²` jump. Testing a claim only against
   `data/census.json` + `data/champions6.json` cannot distinguish "theorem"
   from "property of optima" — that is what `data/walkpool.json` is for, and it
   is currently only 108 walks.

## 5. What survives, and it is better than what was lost

`B = 1` is an *ordering-dependent* hypothesis, so `INFL` does not touch it. Read
in that direction the question has a two-line answer.

**`BLK1` [THM] — the word model.** A weight-1 jump appends one character and
lands on `σ(u)`. A weight-2 jump appends two: the first must be `u[0]`
(anything else repeats a symbol), so the intermediate window is `σ(u)`… and to
land on `δ(u) = u[2:]+u[1]+u[0]` the first appended character is `u[1]`, whose
window `u[1:]+u[1]` is *not* a permutation. So a `δ` step covers **one** new
permutation for **two** characters — it always wastes exactly one — while
`σ²` is just two `σ` steps. Hence a single-block walk is a word in `{σ, δ}`,
`length = n + #σ + 2·#δ`, and

> `length = n + (n!−1) + W`, `W` = wasted characters, and **`R = W + 1`**.

**`BLK2` [THM] — single-block walks cannot beat Egan.** `B1` gives `Y = 0` and
`T = S+1`. Put the Split Identity `S = (n−1)d − A` into HPV `T ≥ v = (n−2)! + d`:

```
(n-1)d - A + 1  >=  (n-2)! + d      =>      (n-2)d >= (n-2)! + A - 1
```

With `A ≥ 0` that is `d ≥ (n−3)! − 1/(n−2)`, and `d` is an integer, so

> **`d ≥ (n−3)!`  and  `T ≥ (n−2)! + (n−3)! = (n−1)(n−3)!`  —  Egan's `T` exactly.**

**Corollary: every superpermutation shorter than `Egan(n)` has `B ≥ 2`.** It
must pay at least one weight-≥3 jump. That is the `k = 0` base case of the
Free-Jump Lemma (`A1`) *without* `A1`'s HPV-tightness hypothesis.

**`BLK3` [THM] — the equality case is the repaired `A1EQ`.** At
`T = (n−1)(n−3)!`, HPV also forces `d ≤ (n−3)!`, so `d = (n−3)!`; then
`S = T−1 = (n−1)(n−3)!−1` and the Split Identity gives **`A = 1`**. So

> a single block at Egan length is *forced* to the Egan vertex.

The Egan vertex is therefore not an accident of the construction. What is false
is only the converse, `A = 1 ⟹ B = 1` (`A1EQF`). All three hold on 188/188
single-block rows of the corpus.

**The gate — [EXH] at n = 5.** `code/block1.py` enumerates `{σ, δ}` words by
increasing waste. `BLK1` gives the search two gifts: the floor
`W = R − 1 ≥ (n−1)! − 1 = 23`, and the fact that the word model is a *superset*
of the single-block walks, so an emptiness result there is stronger than needed.

| W | length | result |
|---|---|---|
| 23…29 | 147…153 | **none** — exhausted, 35.9 M nodes |
| 30 | **154 = Egan(5)** | first words appear; of 156 sampled, **140 have `B=1, A=1, d=2`** and 16 have `B=2, A=2, d=2` |

So at n = 5 nothing below Egan length exists even in the superset, and every
single-block walk at Egan length sits on the Egan vertex — `BLK2` and `BLK3`
confirmed independently of their proof.

n = 6 is out of reach this way: the floor is `W ≥ 119` and Egan(6) is at
`W = 148`, a 29-level gap where n = 5's 7-level gap already cost 192 M nodes.
The theorem covers it; the search does not need to.

## 6. Status

| item | status |
|---|---|
| `ORD` — the coordinate partition | **[THM]**, 40 permutations |
| `INFL` — the Inflation Lemma | **[THM]** |
| `SIG2` — two weight-2 successors, `σ²` needs a length-1 arc | **[THM]** |
| `IN5b` — `B + σ2 ≥ comps` | **[THM]** |
| `A1EQ` forward direction | **[REF]**, witnesses at n = 6 and 7 |
| `IN5` — `B ≥ comps` | **[REF]** as a theorem, **[MEAS]** on 44,564 strings |
| `SIG2X` — min length is attained at `σ2 = 0` | **[THM]**; restores `T ≥ S + comps` against the optimum |
| `SIG2Y` — an optimum with `σ2 ≥ 1` forces an optimum with larger `Y` | **[THM]**; 0 free reverse slots in 43,096 n = 6 optima |
| `B1c` — `B = 1 ⟹ comps = 1` | **[MEAS]** only |
| `BLK1` — single-block walks are `{σ, δ}` words | **[THM]** |
| `BLK2` — `B = 1 ⟹ length ≥ Egan(n)` | **[THM]**, 188/188 |
| `BLK3` — `B = 1` at Egan length ⟹ `A = 1`, `d = (n−3)!` | **[THM]**, 188/188 |
| *why* optima never take a `σ²` jump | **answered for the purpose** — see below |

**Where the σ² question actually landed.** It had two halves and they came apart:

* *"Is `T ≥ S + comps` usable as a lower bound?"* — **yes**, by `SIG2X`. The
  minimum is attained at `σ2 = 0`, which is the only thing any use of the bound
  ever needed. This half is closed.
* *"Must every individual optimum have `σ2 = 0`?"* — **still open, and now
  known to be delicate.** `SIG2X`'s exchange is length-*neutral* at an optimum,
  not length-reducing, so nothing forbids a σ²-using optimum on cost grounds.
  What `SIG2Y` gives instead is a reachability criterion: such an optimum would
  have to be a free reverse exchange of a `σ2 = 0` optimum, consuming a
  weight-≥4 jump. Of the 43,096 n = 6 optima, 808 have such a jump and none
  admits the move.

The natural next question is why: `w(X,Z) = w(X,m) + w(m,Z)` is the *generic*
case of subadditivity, and for a weight-4 jump at n = 6 there are exactly four
permutations `Z` that would permit it (`δδ`, `δσ²`, `σ²δ`, `σ²σ²` from `X`).
That none of the 808 heavy jumps lands on one of them is either a real
constraint on where heavy jumps sit in an optimum, or a small-numbers accident.

At n = 7 the criterion bites differently: all 237 known 5906s have `Y = 0`, so
by `SIG2Y` a σ²-using 5906 would require a 5906 with `Y ≥ 1`, and none is
known. That is not a proof — 237 is nowhere near all of them — but it is the
same conclusion reached from an independent direction.
