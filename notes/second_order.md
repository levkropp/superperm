# Second-order results

Everything here is evaluated by [`code/lemmas.py`](../code/lemmas.py) against
**two** corpora, and the two-corpus discipline is the point of the file:

| corpus | what | why |
|---|---|---|
| `data/census.json` | 177 real strings (n = 5…7; 182 with n = 8, 9) | near-optimal but **narrow** — 163 of the 169 n=7 entries are `5906_derived` |
| `data/walkpool.json` | 108 constructed walks | mediocre but **wide** — T from 7 to 1433, all verified superpermutations |

The census alone is not enough, and that is not hypothetical: `comps = v − S`
held on all 179 measured strings and was refuted by three `mcolour` walks in
seconds. Every claim below carries its status tag, and `lemmas.py` exits
non-zero if anything tagged **[THM]** is violated on either corpus.

---

## A1. The Free-Jump Lemma — **[THM]**

> Let $W$ be HPV-tight ($T = v$) with length $\mathrm{Egan}(n) - k$. Then
> $$B + Y - A = (n-2)k, \qquad \text{costly jumps} \;=\; B - 1 \;=\; (n-2)k + A - Y - 1 .$$

*Proof.* HPV-tightness gives $T = v = (n-2)! + d$; the master identity gives
$T = (n-1)d + (B{+}Y) - A$. Subtracting, $(n-2)d = (n-2)! - (B{+}Y{-}A)$.
Since $(n-2)! + (n-3)! = (n-1)(n-3)!$, writing the length as
$\mathrm{Egan}(n) - k$ means $d = (n-3)! - k$, and substituting gives the
claim. Costly jumps are $B-1$ by definition of $B$. $\square$

Verified on **166 census + 13 pool** HPV-tight walks.

**Corollary — the framing correction.** Egan's construction has $B = 1$ at
every $n$ (measured: 873, 5908, 46205, 408966), i.e. **zero costly jumps —
100 % free**. Beating it by $k$ requires *buying* exactly $(n-2)k - 1$ costly
jumps when $A = Y = 0$. So "champions are ~98 % free" is the wrong reading of
the data: freeness is what Egan already has, and paying for weight-3 jumps is
precisely the mechanism by which a record improves on it.

| n | record | costly | Egan | costly |
|---|---|---|---|---|
| 6 | 872 | 3 | 873 | **0** |
| 7 | 5906 | 17 | 5908 | **0** |
| 8 | 46204 | 5 | 46205 | **0** |

## A2 / A2b / A2c — one theorem in three forms — **[THM]**

> $$\mathrm{comps} \;\ge\; v - S
> \quad\Longleftrightarrow\quad S + B \ge v
> \quad\Longleftrightarrow\quad T \ge v + Y
> \quad\Longleftrightarrow\quad \mathrm{dirty} \le S + N - v .$$

Survives **both** corpora (177/177 and 108/108). Equivalences: $N = B +
\mathrm{dirty}$ and $T = S+B+Y$ turn each into the next. The link from the
second form back to the first used to be $B \ge \mathrm{comps}$ (IN5), which is
**[REF]** — see §F. The repaired `IN5b` gives only
$S + B + \sigma_2 \ge v$, so the four forms are equivalent to each other but
not implied by the δ-graph.

**PROVED** since this was written, by a different route entirely: contract to
the **loop quotient** `Q` on the `v` entered loops. An arc of class `C` exits
into the loop of the *next* arc of `C`, so each multiply-covered class
contributes an edge-disjoint cycle to `Q`; `Q`'s **cycle rank** then forces
`v ≤ S + q` with `comps ≥ q`. Full proof in [`pbound.md`](pbound.md) §8.

Why it matters: `lemma_arsenal.md` §11 proves **HPV is precisely
`dirty ≤ S + N + Y − v`**, and states that any improvement must have the form
`dirty ≤ S + N + Y − v − ε`. **A2c is exactly ε = Y.** It was found twice
independently — once from the δ-graph, once by scanning `dirty ≤ αS+βN+γv`
over both corpora, where the tightest valid form came out at α=β=1, γ=−1 and
is *exactly attained* at the 872 record (dirty = 49 against 2S = 50).

**Honest assessment of its value.** A2b strengthens HPV by exactly $Y$. Every
known record has $Y = 0$, so it does **not** move the binding rungs. Where it
does bite is the split-free/exact-cover region: at $v = (n-2)!$ it gives
$T \ge (n-2)! + Y$, which with the Chain-Count Lemma's $Y \ge (n-3)!-1$
reproduces that lemma directly. **The useful corollary is negative:** the ε in
§11's schema cannot be $Y$ — that instance is already known-shaped and free.
A bound that actually beats HPV at the champions needs ε from somewhere else.

**A refuted route — [REF].** The natural proof of A2 is to contract each
entered loop and bound the quotient's edges by `interloop ≤ S`. That is
**false**: 5907-jupiter has 239 inter-loop δ-edges against `S = 120`. Recorded
so it is not retried.

## A3. The ordering-free ceiling — **[THM]** for the bound, **[MEAS]** for the identity

The δ-graph on arcs (arc $u \to v$ when $v$ starts at $\delta(\text{end } u)$)
has in- and out-degree $\le 1$, since $\delta$ is injective and arc starts are
distinct. So it is a disjoint union of paths and cycles **determined by the arc
set alone**, every block of the walk is a path in it, and

> $$B \ge \mathrm{comps}, \qquad\text{hence}\qquad T \ge S + \mathrm{comps}$$

with no reference to the ordering — **[THM]**, 285/285.

But this ceiling is exactly HPV. The minimum of $S + \mathrm{comps}$ over all
arc sets is $(n-2)!$, attained by the exact cover ($S = 0$,
$\mathrm{comps} = (n-2)!$), and $S + \mathrm{comps} = v$ on all 177 census
strings — though **not** on constructed walks (67/108), so the identity is
**[MEAS]**, not a theorem.

> **RETRACTED: "no ordering-free invariant of the arc set can beat HPV."** What is true is only that *this* quantity cannot: `min(S +
> comps) = (n−2)!`, exactly HPV. The conclusion was over-generalised from one
> invariant to all of them, and it is false.

**The correction.** `CH2` supplies a second ordering-free term — `p`, the fewest
free chains covering the δ-components — with `Y ≥ p − 1`. Since `B ≥ comps`
holds against the optimum (`SIG2X`),

> $$T \;\ge\; S + \mathrm{comps} + (p-1) \qquad\text{(CH3)}$$

is still read off the arc set alone, and it **does** beat HPV. Measured by
[`code/pbound.py`](../code/pbound.py):

| check | result |
|---|---|
| validity over the 1,030 n = 6 census strings | **0 violations**, 1,029 **exactly tight** |
| minimum over **all 10,068** exact covers | **29** — the true n = 6 optimum |
| HPV floor at that rung | **24** |

At an exact cover it evaluates to `(n−1)(n−3)! − 1`, the Egan−1 line — the same
value the Chain-Count Lemma and the Exposure Bound (`S5`) produce there, but
reached without either's hypothesis. So the δ-graph relaxation was not the
ceiling; it was missing a term. See [`notes/pbound.md`](pbound.md).

## B2. Multiplicity — **[MEAS]**, now on both corpora

> No rotation class is covered more than 3 times.

`lemma_arsenal.md` §3.4 records this for champions only. It now holds on
**285/285** walks including badly suboptimal ones (T up to 1433), which makes
it noticeably more likely to be structural than a champion artefact. Still
**[MEAS]** — no proof, and $\mu \le n$ is the only proved bound.

## B3. The d = 0 vertex — **[CONJ]**

> No optimum sits at $d = 0$ (exact cover) for $n \ge 6$.

29/29 across both corpora. At the exact-cover rung this is the Chain-Count
Lemma; the n = 9 string 409113 is the measured witness ($d = 0$, $Y = 867$
against the floor $(n-3)!-1 = 719$).

---

## Status summary

| id | claim | status | census | pool |
|---|---|---|---|---|
| A1 | `B+Y−A = (n−2)k`, `costly = (n−2)k+A−Y−1` | **[THM]** | 166/166 | 13/13 |
| IN5 | `B ≥ comps` (ordering-free) | **[REF]** — see §F and [`ordering.md`](ordering.md) §3; repaired to `B + σ2 ≥ comps` | 177/177 | 108/108 |
| A2/b/c | `comps ≥ v−S` ⟺ `T ≥ v+Y` ⟺ `dirty ≤ S+N−v` | **[THM]** — [`pbound.md`](pbound.md) §8 | 177/177 | 108/108 |
| A3 | `S + comps = v` | **[MEAS]** | 177/177 | 67/108 |
| B2 | `μ_max ≤ 3` | **[MEAS]** | 177/177 | 108/108 |
| B3 | no optimum at `d = 0` | **[CONJ]** | 5/5 | 24/24 |
| REF1 | `interloop ≤ S` | **[REF]** | — | 5907-jupiter: 239 > 120 |
| EGAN1 | `v+Y ≥ (n−1)(n−3)!−1` (⟹ `s(n) ≥ Egan−1`) | **[REF]** | equality at n=5,6,8,9 and all 43,096 | **5906 alone violates it, by 1** |
| C6a | `A = 0` at every n=6 optimum | **[REF]** | all 43,096 standard-kernel | `872-nonstandard` has A=2 |
| C6b | `B = comps` at an optimum | **[CONJ]** | 43,266/43,266 | 27/27 |

---

## C6. The 43,096 n = 6 optima — and the Egan−1 Law

Robin Houston's `872-treelike.txt.gz` holds **42,288** length-872
superpermutations, plus 772 and 36 in the two slack files:
[`code/champions6.py`](../code/champions6.py) measures all **43,096**.
`census.py` had been reading one string per file, so this corpus was sitting
unmeasured on disk.

**Extreme rigidity — only three coordinate vectors among 43,096 strings:**

| $d$ | $A$ | $S$ | $B$ | $Y$ | $v{+}Y$ | count |
|---|---|---|---|---|---|---|
| 5 | 0 | 25 | 4 | 0 | 29 | 42,288 |
| 4 | 0 | 20 | 8 | 1 | 29 | 772 |
| 3 | 0 | 15 | 12 | 2 | 29 | 36 |

They lie on a single line: $S = 5d$, $B = 24-4d$, $Y = 5-d$, $A = 0$, and so
$T = 29$ and $v + Y = 29$ throughout. Also **$B = \mathrm{comps}$ on every
one** — an optimum saturates the δ-graph, using every free edge on offer
(claim C6b, now 43,266/43,266 plus the whole census).

And **A2b is tight on all of them**: $T = v + Y$ exactly, at every optimum.
So A2b can never separate an optimum from a near-miss — which independently
confirms the negative in §A2.

### The Egan−1 Law — **[REF]**, and this is the headline

> $$v + Y \;\ge\; (n-1)(n-3)! - 1$$

Together with A2b ($T \ge v+Y$) this says **$s(n) \ge \mathrm{Egan}(n) - 1$**:
no construction beats Egan by more than one character. Against the records:

| $n$ | $v+Y$ | bound | |
|---|---|---|---|
| 5 | 7 | 7 | equality |
| 6 | 29 | 29 | equality, **and on all 43,096** |
| 7 | **142** | **143** | **violated by exactly 1** |
| 8 | 839 | 839 | equality |
| 9 | 5760 | 5759 | holds |

It also fails on 8 of 108 pool walks, so it is not a theorem-in-waiting for
arbitrary walks — but at the *optima* it is exact everywhere except n = 7.

**This relocates the entire question.** The ε that beats HPV at the champions
is not a generic improvement waiting to be found: every optimum known anywhere
— 43,096 at n = 6, plus n = 5, 8, 9 — sits exactly **on** the Egan−1 line.
**5906 is the unique object that gets past it, and by exactly one character.**
The research question is therefore not "what is ε" in the abstract but:

* what does 5906 have that 43,096 n = 6 optima and the n = 8 record do not?
* the measured difference is **accidents**: every standard-kernel n = 6 optimum
  has $A = 0$, `872-nonstandard` has $A = 2$, and every n = 7 champion has
  $A \in 8\ldots16$ (claim C6a, refuted in general precisely by the
  non-standard string);
* by A1, $k = (B{+}Y{-}A)/(n-2)$, so $k = 2$ at n = 8 needs
  $B{+}Y{-}A = 12$ — the n = 7 champion reaches 10 with $B = 18, A = 8$.
  That is `ledger.design(8, [2])` and it is a concrete, checkable target.

---

## D. The `dirty ≤ 2S` lever is dead — measured, not argued

`lemma_arsenal.md` §11 closes with: *"This is the single most concrete open
lever in the whole file."* It is not a lever. Measured over the repaired
corpus:

| n | optima | with `dirty = 2S` exactly | max `dirty/2S` |
|---|---|---|---|
| 5 | 6 | 0 | 0.8750 |
| 6 | 44,121 | **12,672** | **1.0000** |
| 7 | 237 | 0 | 0.9958 |
| 8 | 1 | 0 | 0.9976 |
| 9 | 2 | 0 | 0.9999 |

`dirty = 2S` is **attained exactly** by 12,672 length-872 optima. At n = 7, 8,
9 the records fall short by only 1–4 *in absolute terms*, and the ratio rises
toward 1 as n grows. So the strongest true statement is
`dirty ≤ 2S − O(1)` — an additive constant, never a factor.

**Why that settles the factor-4 gap to Hunter.** The closed-form ladder
(`notes/ledger_model.md` §4c) has denominator
`(n−1)(c(3n−5) − (2n−3)) − 1` where `c = n_partial/S`; ours is the `c = 2`
value `(n−2)(4n−3)`, Hunter's is the `c = 1` value `n²−3n+1`. Since `c → 2` at
optima, **the gap cannot be closed by tightening the dirty budget at all.**
Hunter's advantage is structurally different, not a sharper `n_partial` bound.
Finding out what it actually is becomes the priority.

**The repair route also fails.** `n_partial = S + m ≤ 2S` is tight when every
multiply-covered class has `μ = 2`, so the natural fix is to force
triply-covered classes. Measured `S − m` (= their count, given `μ_max ≤ 3`):
`0…3` at n = 6, `0…6` at n = 7, and **exactly 0 at both the n = 8 and n = 9
records**. It does not scale, and optima with `m = S` exist at every n.
Registered `REF3`.

**And the same wall explains the exposure route.** §7 of
`notes/a1_argument.md` wanted a *lower* bound on `F`. One exists —
`F ≥ v − A − 2S`, tight at the exact cover (n=7: `120 − 0 − 0 = 120`) — but the
`2S` makes it vacuous at every champion (n=7: `142 − 8 − 248 < 0`).

> **Four independent routes — the ladder's collapse slope, the proof of A2, the
> A = 1 enumeration, and the exposure bound — all fail at exactly one point:
> `n_partial ≤ 2S`, which is attained at optima.** That is now a measured fact
> rather than a suspected looseness, and it closes the direction rather than
> leaving it open.

---

## E. Kicks — the cost of saving a character

A **kick** is a weight-2 jump out of a *full* arc: the move to the next village
(rotation class) of the same 2-loop. Formally it is `clean`, and since a clean
run of `a` arcs carries `a−1` kicks, **kicks = R − N**.

### E1. The Kick Identity — **[THM]**, 44,564/44,564 + 108/108

Substituting `R = (n−1)! + S`, `N = B + dirty` and `B = T − S − Y`:

> $$\text{kicks} \;=\; (n-1)!\;+\;2S\;+\;Y\;-\;T\;-\;\text{dirty}$$

Pure bookkeeping, no hypotheses.

### E2. The Kick Bound — **[THM]**

With `dirty ≤ 2S` (IN4):

> $$\text{kicks} \;\ge\; (n-1)! \;-\; T \;+\; Y, \qquad
> \text{equality iff } \text{dirty} = 2S.$$

Since `T = length − base_n`, this says something clean:

> **A shorter string needs more kicks. Every character saved costs at least one
> extra kick.**

Equality is attained — 12,672 of the 44,121 length-872 optima have
`dirty = 2S` and hit the bound exactly.

### E3. Egan's kick count is exact — **[THM]**

Egan sits at `T = (n−1)(n−3)! = (n−2)! + (n−3)!`, `Y = 0`, and
`dirty = 2S − 1` (one short of the cap), so

> $$\text{kicks}(\mathrm{Egan}) \;=\; (n-1)! - (n-2)! - (n-3)! + 1 .$$

| n | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|
| predicted | 17 | 91 | 577 | 4,201 | 34,561 |
| measured | 17 | 91 | 577 | 4,201 | 34,561 |

Combining with E2, a champion of length `Egan(n) − k` needs

> $$\text{kicks} \;\ge\; \text{kicks}(\mathrm{Egan}) + k - 1 .$$

Measured, champion minus Egan:

| n | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|
| k | 1 | 1 | 2 | 1 | 0 |
| kicks(record) − kicks(Egan) | 1 | 0…5 | 2…11 | 4 | 0 |
| bound `k−1` | 0 | 0 | 1 | 0 | 0 |

### E4. Reading

Kicks are the *cheap* structural move — they cost nothing in `T` — and Egan
already spends nearly all of them: `(n−1)! − (n−2)! − (n−3)! + 1` out of a
theoretical ceiling of `R − v` (IN4/§2.6). Beating Egan means spending **more**
kicks, not fewer, and the extra kicks come from the `2S − dirty` slack, which
§D showed is `O(1)`. So the kick budget is essentially saturated at every
known optimum, and the identity says exactly where the remaining room is:
`2S − dirty`, which is 1 for Egan and 1–8 for the records.

---

## F. `B = 1` forces most of the Egan vertex — **[THM]**

`census.py` measured that every Egan string, at every n, sits at
`A = 1, B = 1, Y = 0, d = (n−3)!`. Three of those four coordinates are
consequences of `B = 1` alone.

> **Theorem.** Let a walk have `B = 1` and `n ≥ 4`. Then
> $$Y = 0, \qquad T = S + 1, \qquad F = 0 .$$

*Proof.* `B = 1 + \#\{\text{jumps of weight} \ge 3\}`, so `B = 1` says there
are none; `Y = Σ(w−3)` over exactly those jumps is an empty sum, giving
`Y = 0` and `T = S + B + Y = S + 1`.

For `F`: by **S1** an all-full saturated loop *is* a δ-cycle, and since the
δ-graph has in- and out-degree `≤ 1` a cycle is a whole component. Its arcs are
full, so by **SIG2** no `σ²` edge touches them either — the cycle can be entered
or left only by a weight-≥3 jump, of which `B = 1` says there are none. So if
`F ≥ 1` the cycle would have to *be* the whole walk, forcing `R = n−1` against
`R = (n−1)! + S > n−1` for `n ≥ 4`. Hence `F = 0`. ∎

Verified on all **188** `B = 1` walks in the corpus (n = 5…9): `Y = 0`
188/188, `T = S+1` 188/188.

> **Correction.** A fourth clause, `comps = 1`, used to sit in this theorem,
> derived from `IN5` (`B ≥ comps`). **`IN5` is false** — a weight-2 jump has two
> possible targets, `δ(u)` and `σ²(u)`, and `comps` follows only the first, so a
> single block can span two δ-components. Witness: an n = 7 walk of length 5914
> with `B = 1, comps = 2`. See [`notes/ordering.md`](ordering.md) §3. The proof
> of `F = 0` above has been rewritten to avoid `IN5`; the rest stands.

**Three things this settles.**

1. Egan's `F = 0` is *forced*, not a design choice — and since the Exposure
   Bound (S5) reads `T ≥ S + ⌈(n−1)F/(n−2)⌉ − 1`, it is **identically vacuous
   on Egan**. That is exactly why Egan sits *on* the Egan−1 line rather than
   above it, and it closes the loop with §7 of
   [`a1_argument.md`](a1_argument.md): champions evade the chain tax by
   minimising `F`, and Egan achieves the minimum for a structural reason.
2. Pushing further (`BLK2`): feeding the Split Identity into HPV gives
   `(n−2)d ≥ (n−2)! + A − 1`, hence `d ≥ (n−3)!` and `T ≥ (n−1)(n−3)!`. So
   **`B = 1` ⟹ length ≥ Egan(n)**: every superpermutation shorter than Egan
   must pay a weight-≥3 jump. At equality (`BLK3`) `d = (n−3)!` and `A = 1` are
   both forced — the Egan vertex is the *only* place a single block can sit at
   Egan length.
3. `A1EQ` ("A = 1 ⟺ the Egan vertex") is settled, and negatively. The ⟹
   direction is **false**: `A = (n−1)v − R` is ordering-free while `B` is not,
   so rotating Egan's arc list gives a valid superpermutation with `A = 1,
   B = 2`. See [`notes/ordering.md`](ordering.md). What survives is the ⟸
   direction, now a theorem via `BLK2`/`BLK3`.

### F1. A reformulation of A2, for the record

Writing `comps = R − e + cyc` with `e` the number of δ-edges, and using
`v = (R+A)/(n−1)`, `A2` (`comps ≥ v − S`) becomes an edge count. *This framing
is what refuted the first proof attempt and is kept for that reason; the proof
that works counts the quotient's cycle rank instead —* [`pbound.md`](pbound.md)
*§8.*

> $$\textbf{A2} \iff \#\{\delta\text{-escapes}\} + \mathrm{cyc}
> \;\ge\; (n-2)! - \tfrac{n-2}{n-1}S + \tfrac{A}{n-1}$$

where a *δ-escape* is an arc whose δ-successor is not an arc start. At the
exact cover (`S = A = 0`) this reads `escapes + cycles ≥ (n−2)!`, and `cyc`
equals `(n−2)!` exactly — tight. This counts *local* failures of the δ-map
rather than inter-loop edges, so it is a different handle from the
loop-contraction route refuted as `REF1`.

### F2. A corollary worth stating

Combining the Kick Bound `kicks ≥ (n−1)! − T + Y` with the ceiling
`kicks ≤ R − v` (§2.6) gives

> `v ≤ 2S + B`,

tight exactly at the exact cover (`0 + (n−2)! = v`). Implied by
`comps ≥ v − 2S`, so not independent, but this is its cleanest form.
