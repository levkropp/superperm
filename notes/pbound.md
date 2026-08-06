# CH3: an ordering-free bound that beats HPV

For years this repo recorded, in [`second_order.md`](second_order.md) §A3 and
[`lemma_arsenal.md`](lemma_arsenal.md) §2.7/§8, that **no ordering-free
invariant of the arc set can beat HPV**. That is false, and this note is the
correction plus what the corrected bound is worth.

The old argument was: the δ-graph gives `B ≥ comps`, hence `T ≥ S + comps`, and
`min(S + comps)` over arc sets is exactly `(n−2)!` — HPV. True, but it
generalises *one* invariant to *all* of them.

---

## 1. The bound

Two claims registered earlier this session supply a second ordering-free term:

* **`CH2`** — `Y ≥ p − 1`, where `p` is the fewest **free chains** covering the
  δ-components. Every chaining decomposes into maximal free chains, and every
  join *between* chains costs ≥ 1. (This once cited `CH1`, "free continuation
  is forced" — now **[REF]**, see §10a. The argument never needed it: it needs
  only chain *maximality*.)
* **`SIG2X`** — the minimum length is attained at `σ2 = 0`, where `B ≥ comps`
  does hold. A lower bound is only ever used against the optimum, so that is
  enough.

Together:

> **`CH3`.  `T ≥ S + comps + (p − 1)`.**

`S`, `comps` and `p` all read the arc **set**, so the bound is ordering-free.
`code/pbound.py` computes it; `p` is `chainer.min_chains`.

## 2. What it is worth

**Validity and tightness**, over the n = 6 census:

```
1030 strings: 0 violations, 1029 exactly tight
```

Not merely valid — it *equals* `T` on essentially every real string.

**At the rung where HPV binds**, over **all 10,068** exact covers at n = 6:

| bound | 29 | 30 | 31 | 32 | 33 |
|---|---|---|---|---|---|
| covers | 6351 | 3358 | 239 | 2 | 118 |

> **minimum 29**, against **HPV's 24** — and 29 is the true n = 6 optimum.

At an exact cover the bound evaluates to `(n−1)(n−3)! − 1`, the **Egan−1 line**
— the same number the Chain-Count Lemma and the Exposure Bound (`S5`) give
there, but reached without either's hypothesis (Chain-Count needs split-freeness,
`S5` needs a large all-full population `F`).

**At n = 7**, the known points:

| walk | `T` | bound | `S` | `comps` | `p` | |
|---|---|---|---|---|---|---|
| 5906 champion | 142 | **142** | 124 | 18 | 1 | **tight** |
| 5913 exact cover | 149 | 143 | 0 | 120 | 24 | slack 6 |
| 5908-egan | 144 | **144** | 143 | 1 | 1 | **tight** |
| HPV floor | — | 120 | | | | |

## 3. Why this matters, and exactly what is not claimed

5905 at n = 7 means `T = 141`. The champion sits at `T = 142` and the bound is
**tight** there; the exact-cover rung gives 143. So:

> **if the global minimum of `S + comps + (p−1)` over n = 7 arc sets is 142,
> then 5905 is excluded.**

That is a well-posed target and the bound is cheap enough to search against
(1–12 ms per arc set, ordering-free, no chaining). It is *not* a proof of
anything about 5905 yet, and this note will not claim otherwise:

* the n = 6 result **is** exhaustive at the exact-cover rung — all 10,068
  systems — but not over all arc sets;
* at n = 7 nothing is exhaustive.

**Errors run in the safe direction — but they wreck a naive search.**
`chainer.min_chains` falls back to the crude floor `⌈comps/longest⌉` when its
node cap bites. That floor is a *valid* lower bound on `p`, so `CH3` stays
sound; but it *understates* `p`, so a search minimising the bound will happily
run downhill into states where the chain search merely gave up.

That is not hypothetical. The first n = 7 run reported **140** — below the 141
that 5905 needs — at `v=122, S=12, comps=116, p=13`. Checking it:
`longest = 9`, so `⌈116/9⌉ = 13` **is exactly the floor**, and `min_chains`
returned it by timing out at both a 100k and a 3M node cap (`nodes` is not reset
between `pmax` levels). So `p = 13` was never a verified 13-chain cover, and
the 140 was an artefact of giving up, not a real dip.

`min_chains.exact` and `pbound.value.exact` now report this, and the search
tracks the best **verified** value separately. On the numbers above:

* the n = 7 calibration points are all verified (`p = 1` at the champion,
  `p = 24` at the exact cover);
* of 1,500 n = 6 exact covers, 1,433 verify and 67 fall back — and the fallbacks
  can only push the histogram *down*, so `minimum = 29` stands.

**The honest reading:** an unverified dip means nothing. Only the verified
figure estimates the true minimum, and only exhaustion proves it.

## 3a. What the searches actually returned

Annealing loop systems to *minimise* the bound — the objective the constructor's
annealers lacked, since it is ordering-free and needs no chaining:

| n | iterations | lowest found | lowest **verified** |
|---|---|---|---|
| 6 | 6,000 | **29** | 29 |
| 7 | 3,000 | 140 | **none** |

At n = 6 nothing goes below 29 — consistent with the exhaustive exact-cover
result and with 872 being optimal.

At n = 7 the search is **uninformative**, and cleanly so: it drifts into
`comps ≈ 116` states where `min_chains` cannot verify `p` within its node
budget, so every dip it reports is a floor. Not one verified improvement in
3,000 iterations.

> **So `CH3` does not currently say anything about 5905.** The bound is tight at
> the champion (142, verified) and gives 143 at the exact cover (verified), but
> to search the space between them we need `p` computable at `comps ~ 100`, and
> it is not.

## 3b. Fixing the floor: the packing bound

The bottleneck was `min_chains`' fallback. Exact minimum path cover is NP-hard
(it is Hamiltonian path at `p = 1`), so timeouts at `comps ~ 100` are expected;
what mattered was that the fallback was *worthless*, not that it existed.

Two replacements were tried.

**Maximum bipartite matching** on component links — `p ≥ comps − M`, since the
links a chain decomposition uses give every component ≤ 1 in and ≤ 1 out.
Valid, and **useless**: it returns 0 or 1 at every state tested, against the
crude floor's 13–24. It discards exactly the state-consistency coupling — a
component's break point fixes *both* its entry and its exit — that is the reason
chains are short in the first place. (`gen2` recorded the same failure when it
tried matching to *build* chains.)

**A packing bound** — take a set of components no two of which share a run;
each must land in a different chain, so its size lower-bounds `p`. Greedy,
lowest-degree-first, O(comps²). This works:

| state | comps | `⌈comps/longest⌉` | **packing** | true `p` |
|---|---|---|---|---|
| n=7 exact cover | 120 | 24 | **24** | 24 |
| the "140" state | 113 | 13 | **20** | ? |
| n=7 5906 champion | 18 | 1 | **1** | 1 |

Tight where the answer is known, and +7 where the crude floor was failing.
`min_chains` now starts its deepening at `max(⌈comps/longest⌉, packing)` — a
better answer on timeout *and* fewer levels to search.

**Re-running n = 7 with it, the artefact is gone:**

```
crude floor:    dips to 140 by iteration ~400
packing floor:  never leaves 143 in 250 iterations
```

143 is above the champion's 142 and well above the 141 that 5905 needs. And
because the packing bound is a *sound* lower bound rather than a give-up value,
this now says something real: **every loop system the search visited has
`CH3`-bound ≥ 143**.

## 3c. Loop space cannot see the n = 7 champions at all

The loop-space search was worse than slow — it was searching the wrong set.
`LOOP1` says a loop system has `A = 0`, and the A-spectrum at length 5906 is

```
A = 8:153   9:7   10:3   12:13   13:11   14:42   16:2   17:2   18:4
```

**No n = 7 optimum has `A = 0`.** So loop space provably excludes every known
n = 7 champion, and the 143 floor it reported was the floor of a subspace that
does not contain the answer. (At n = 6 this does not bite: `A = 0` optima exist
there, which is why the loop-space results in §3a are meaningful.)

Cut space contains them, and near a champion `comps = 18` is small enough that
`p` verifies in milliseconds. `pbound.minimise_cuts` seeds from a real string
and moves one class's cuts at a time.

| seed | bound at the seed | improvements found |
|---|---|---|
| n = 6 `houston_872` | **29** (`S=25 comps=4 p=1`, verified) | **0** |
| n = 7 `5906` champion | **142** (`S=124 comps=18 p=1`, verified) | **0** |

Both seed exactly at the champion's `T`, with `p` verified, and neither found a
single arc set below it before the time limit — the n = 7 run over ~4,000
attempted iterations, the n = 6 control over ~3,000.

**What that is and is not.** They are local explorations around one seed each,
not coverage. So: a consistency check, and not an exclusion of 5905.

## 3d. Making the bound cheap — and why that was not the bottleneck

`packing_lb` built its co-occurrence graph out of `runs`, which materialises a
frozenset for **every prefix of every forced path from every state** — thousands
of set constructions per evaluation. `packing_fast` skips all of it: when free
out-degree is ≤ 1 — which `CH1` claimed always and §10a refutes — the path from a state
is unique, so one forward walk per state gives the same graph, and bitmask ints
make the greedy independent set nearly free. It returns `None` under branching,
where a single walk would *miss* co-occurrences, shrink the adjacency, inflate
the independent set and make the bound unsound; the caller falls back.

| state | comps | exact | fast | |
|---|---|---|---|---|
| n=7 exact cover | 120 | 143 in **3.17 s** | 143 in **0.022 s** | **144× faster, same value** |
| n=6 exact cover | 24 | 29 in 0.013 s | **27** in 0.007 s | weaker |
| n=7 champion | 18 | 142 | 142 | equal |

The n = 6 row is the warning: the fast bound is *sound* (27 ≤ 29) but weaker
wherever the exact chain search would have succeeded, so minimising it directly
would manufacture false dips — the crude-floor mistake in a new costume. So
`minimise_cuts` sweeps on the fast bound and **re-prices exactly before
accepting any new best**.

**And the searches still find nothing.** With the two-tier scoring, ~6,000
attempted iterations at n = 7 from the champion and the same at n = 6 from
houston_872: **zero** improvements over the seed in either. The 144× speedup
went into the sweep and did not change the answer, which says the cost was never
what was limiting the result — the neighbourhood of a champion simply has no arc
set with a smaller bound, as far as single-class moves reach.

The claim stands exactly this far — the bound is **sound**, it **beats HPV**
(29 against 24, exhaustively over all 10,068 n = 6 exact covers), it is **tight
at every known n = 6 and n = 7 optimum**, and **nothing found anywhere so far
dips below the champion**. Turning that last clause into a theorem needs the
global minimum, which no search delivers.

## 4. What replaced what

| record | was | now |
|---|---|---|
| `A3` | "the ordering-free bound EQUALS HPV" | true of `S + comps` only; `CH3` exceeds it |
| `lemma_arsenal` §8 | "ordering-free invariants past HPV — **[DEAD]**" | **revived**, kept as a note on how the over-generalisation happened |
| `second_order` §A3 | "no ordering-free invariant can beat HPV" | **retracted** in place, with the measurements above |

## 5. Can `min F ≥ 142` be argued structurally at n = 7?

Write `F = S + comps + (p−1)`. By `A2` (`comps ≥ v − S`, **[CONJ]** when this
section was written and **[THM]** since — §8),

> `F ≥ v + p − 1`

and this is **exactly tight at both known extremes** — champion `142+1−1 = 142`,
exact cover `120+24−1 = 143`. So the whole question becomes

> **is `v + p ≥ 143` at n = 7?**

Half of it is free: `p ≥ 1`, so any walk with `v ≥ 142` is done. The champion
sits exactly there. What is left is `v ≤ 141`, which needs `p ≥ 143 − v` — a
**v–p trade-off**: enter few loops and you must pay in free chains.

### The mechanism, and where it broke

The trade-off looked structural. Few loops entered ⟹ few partial arcs ⟹ many
all-full loops ⟹ (by `S1`) many δ-cycle components ⟹ many chains. Two steps:

**`FLOOP` [THM] — holds, 1275/1275.** At most `A` of the `v` entered loops are
unsaturated, and at most `n_partial = S + m ≤ 2S` loops contain a partial arc,
so `F_loops ≥ v − A − 2S`.

**`p ≥ ⌈F_loops/(n−2)⌉` — [REF], 171 violations.** Witness
`7_5906_derived_06f4ba2c8122`: `F_loops = 16`, `p = 1` (verified exact), against
a claimed 4.

The reason is worth recording, because the arsenal's phrasing invites the error.
`s = a^{n−2}·b`, so "om-chains cap at `ord(s) = n−2`" holds only when **every
block in the chain has that one length**. `S5` is sound because all-full loops
are uniform (`n−1` arcs each). But a chain may thread all-full components
together *through non-uniform blocks* and evade the cap completely. Measured at
the 5906 champion: block sizes are

```
[4, 4, 4, 4, 6, 6, 6, 6, 12, 12, 18, 24, 24, 30, 30, 60, 288, 306]
```

— every free join sits far above the forced-om threshold (`min l+l' = 16`
against `2n−3 = 11`), so each *is* the unique om exit, and yet all 18 components
chain into `p = 1`. There is no general cap.

> **So `CH3`'s reduction survives but has no mechanism below `v = 142`.**
> `v ≥ 142` is closed by `p ≥ 1`; `v ≤ 141` is wide open, and the natural
> bridge from `v` to `p` is now refuted rather than merely unproven.

### `RES` — the correct version of the cap

Chasing *why* `PFLOOP` failed produced a sharp law. Measuring the longest free
chain against the multiset of δ-component sizes gives a dichotomy, not a
gradient:

| component sizes | strings | longest |
|---|---|---|
| uniform | 11 | `1` or `n−2` |
| diverse | 1,264 | `= comps` in 1,244 of them (so `p = 1`) |

and the exceptions sharpen it. A string with *two* distinct sizes still capped
at `longest = 5`. The reason is that size only matters **mod `n−1`**: traversing
a component of `l` arcs applies `a^{l−1}`, then the free join applies `b`, so
each step of a free chain is the group element

```
g_r = a^r . b,      r = (l - 1) mod (n - 1)          [ord(a) = n-1]
```

Share a residue and every step is the *same* `g`, so `k` steps apply `g^k` and
the chain must close by `ord(g)`. Mix residues and nothing forces a stop.

> **`RES`.  If every component has `(size − 1) ≡ r (mod n−1)` for a single `r`,
> then `longest ≤ ord(a^r·b)`, hence `p ≥ ⌈comps/ord(a^r·b)⌉`. Mixed residues:
> no cap.**

Measured, and **tight**:

| n | `r` | cap `= ord(a^r·b)` | `longest` | strings |
|---|---|---|---|---|
| 6 | 4 | 4 | **4** | 2 |
| 7 | 5 | 5 | **5** | 6 |

0 violations, and the underlying dichotomy is exact in both directions,
**1269/1269**.

**This derives the cap instead of asserting it.** `r = n−2` in every uniform
case observed — components are whole loops of `n−1` arcs — and there
`a^{n−2}·b` *is* `s`, so the cap is `ord(s) = n−2` by §3.5 **[THM]**. The
arsenal's constant was the special case all along. Other residues give different
and sometimes far stronger caps: at n = 7, `ord(a^r·b)` for `r = 0…5` is
`[6, 4, 6, 5, 2, 5]`, so a uniform-residue-4 arc set would have `longest ≤ 2`
and `p ≥ ⌈comps/2⌉`.

It explains the two extremes at a stroke. The exact cover: every component is
one whole loop, `n−1` arcs, so `r = n−2` uniformly, `longest = ord(s) = n−2`,
`p = comps/(n−2)`. The 5906 champion: sizes
`[4,4,4,4,6,6,6,6,12,12,18,24,24,30,30,60,288,306]` give residues `{3, 5}` —
mixed, so no cap at all, `longest = comps = 18`, `p = 1`. Every free join is om
in both cases; what differs is only whether they are the *same* om step.

**For `CH3` this is a real bridge with a stated hypothesis.** It gives
`p ≥ ⌈comps/ord(a^r·b)⌉` under residue-uniformity, which holds at `S = 0` and
fails at champions.

### 5a. The residue conjecture, tested and refuted — and what replaced it

Grouping the n = 7 corpus by `v` looked like it handed over the missing step:

| v | uniform | mixed | `p` | residues |
|---|---|---|---|---|
| 120 | 4 | 0 | 24 | {5} |
| 140 | 2 | 0 | 4 | {5} |
| **142** | 0 | **237** | **1** | {2,3,4,5} |
| 144 | 2 | 0 | 1 | {4} |

Every corpus string with `v ≤ 141` uniform, mixing appearing exactly at
`v = 142` where the champions are. That would have closed `CH3`. But it rests on
**6 strings**, and generating arc sets directly kills it: adding random loops to
the n = 7 exact cover gives **mixed residues at every `v` from 121 to 145, 6 of
6 samples at each**, `v = 141` included. The corpus pattern was an artefact of
its own sparsity below 142.

**What the generated sets show instead is more useful.** Mixing removes the
*cap* but does not produce long chains:

```
v=121 p=24    v=130 p=21    v=135 p=23    v=140 p=22
v=141 p=23    v=142 p=21    v=145 p=20
```

At `v = 141`, `comps = 71` and `p = 23` — chains average ~3 components, neither
capped at 5 nor collapsing to 1. So `v + p ≈ 164`, far above the 143 that `CH3`
needs. **Generic arc sets are nowhere near the boundary; the champions are the
exceptional points.**

That relocates the question. `p = 1` means the free-join graph admits a single
path through every component. (It is *not* functional — `CH1` claimed that and
is refuted in §10a — but its **core** subgraph is, by `FORCE`.) A
Hamiltonian path in a functional graph is a fragile, exceptional property, and
the 5906 champion has one over its 18 components. So:

> **the open question is not "is `p` large at `v ≤ 141`" — generically it is —
> but "is `p = 1` reachable at `v ≤ 141` at all?"**

which is a question about when the free-join functional graph degenerates into
one path, not about residues.

### 5b. The first rung, closed by proof

`RES` does close one rung outright, with no search. At `v = (n−2)!`:

* `v = (n−2)!` forces `A = 0` and `S = 0` (§1: `R ≥ (n−1)!` and
  `R = (n−1)v − A`);
* `S = 0` ⟹ every class covered once ⟹ **every arc is full**;
* so every entered loop has `a_L = n−1` — saturated *and* all-full — and by
  `S1` each closes into a δ-cycle of `n−1` arcs;
* hence `comps = (n−2)!` with every component of size `n−1`, a single residue
  `r = n−2`, and by `RES` the cap is `ord(a^{n−2}·b) = ord(s) = n−2` (§3.5
  **[THM]**);
* so `p ≥ (n−2)!/(n−2) = (n−3)!` and

> **`CH3 = 0 + (n−2)! + (n−3)! − 1 = (n−1)(n−3)! − 1 = Egan_T − 1`, exactly.**

Matching measurement: **29** at n = 6, **143** at n = 7. At n = 7 that is
`143 > 141`, so **`v = 120` cannot produce a 5905** — the first rung of that
question closed by proof rather than search. It also explains why the Egan−1
line keeps surfacing at exact covers (`EGAN1`, Chain-Count, `S5`): it is the
residue cap, not a coincidence.

### 5c. The rung map — and I had the target backwards

`CH3 ≤ 141` needs `p ≤ 142 − v`. Against the generic `p ≈ 20…24` measured above:

| v | needs `p ≤` | generic `p` | gap |
|---|---|---|---|
| **120** | 22 | — | **closed by `RUNG0`** |
| **121** | **21** | ~24 | **3** ← most vulnerable |
| 125 | 17 | ~24 | 7 |
| 130 | 12 | ~21 | 9 |
| 135 | 7 | ~23 | 16 |
| 140 | 2 | ~22 | 20 |
| 141 | 1 | ~23 | 22 |

So the rung to attack is `v = 121`, not `v = 141` — the requirement tightens
faster than `p` falls, and my earlier instinct to search at the top of the range
was exactly backwards.

### 5d. `v = (n−2)!+1` closed too, exhaustively

At that rung every `A = 0` arc set is *an exact cover plus one loop*, so the
family is small enough to exhaust. Doing so for one base cover at each n:

| n | v | `(S, comps, p)` | CH3 | need | margin |
|---|---|---|---|---|---|
| 6 | 25 | `(5, 22, 6)` — **120/120** | **32** | ≤ 28 | 4 |
| 7 | 121 | `(6, 117, 24)` — **720/720** | **146** | ≤ 141 | 5 |

**Every single addition gives the identical value.** In closed form
`S = n−1`, `comps = (n−2)! − (n−4)`, `p = (n−3)!`, so

> `CH3 = (n−1) + (n−2)! − (n−4) + (n−3)! − 1 = Egan_T + 2`.

Caveat kept explicit: this is `A = 0` only. At this rung `S = n−1−A ≥ 0` allows
`A ≤ n−1`, and those are untested; by `A2` any such arc set has
`CH3 ≥ v + p − 1`, so closing it in general needs `p ≥ 22` at n = 7.

### 5e. The rung map was the wrong slicing

Tracking `CH3` across the `A = 0` loop systems sampled earlier:

```
v=120  143      v=121  146      v=130  174      v=141  219
```

**`CH3` grows with `v`, it does not fall.** The minimum over loop systems is at
the exact cover, and every rung above it is further from 141, not closer. So
"which `v` rung is vulnerable" was the wrong question: for `A = 0` the answer is
none of them.

The champion sits at `v = 142` with `CH3 = 142` — *below* every loop system —
and it does that with `A = 8`. Since `S = (n−1)d − A`, large `A` is what keeps
`S` small while `v` is large, and loop systems have `A = 0` by construction and
so cannot go there at all. This is the same wall as §3c from the other side:
**the low-`CH3` region is high-`A`, and every enumerable family here is `A = 0`.**

So the next enumerable slice should be indexed by `A`, not by `v`.

### 5f. `A = 1` does not help, and `v` is rigid — why every search failed

**`A = 1` first, since it was the obvious next slice.** Take a loop system and
drop one generator from a multiply-covered class: `v` is unchanged, `R → R−1`,
so `A: 0 → 1` and `S → S−1`. Measured at n = 7:

| v | loop system (`A=0`) | minus one generator (`A=1`) |
|---|---|---|
| 121 | `CH3=146  S=6 comps=117 p=24` | `CH3=144  S=5 comps=116 p=24` |
| 131 | `CH3=186  S=66 comps=99 p=22` | `CH3=183  S=65 comps=98 p=21` |
| 141 | `CH3=217  S=126 comps=71 p=21` | `CH3=215  S=125 comps=70 p=21` |

`A = 1` moves `CH3` by about 2 and leaves `comps` essentially untouched
(117 → 116). The chasm to the champion is `comps = 18`, and `A` does not
address it. Building the deficiency-1 enumerator would have been wasted work.

**What the numbers do give is the exact target.** `A2` is tight at every point
measured, so `CH3 = S + comps + p − 1 = v + p − 1` and the whole question is
`min(v + p) ≤ 142`. The champion gives 143 — one short. So:

> **target: `v = 141, S = 124, A = 2, comps = 17, p = 1` → `CH3 = 141`**
>
> the champion with one fewer loop entered and one fewer component.

**And that target is unreachable by the moves used so far.** At the champion the
loops hold 4 or 6 arc starts — 4 loops with 4, 138 saturated with 6, so
`A = 8 = 4 × 2`. Dropping `v` means *vacating* a loop, and the thinnest holds
four arc starts, so it takes **at least a 4-class coordinated re-cut**.
Measured: **3,588 single-class re-cuts, 0 of them change `v`**.

> So `v` is **rigid** under the 1-class move set, and every champion-seeded
> search in §3c and §3d was structurally incapable of reaching the target rather
> than merely unlucky.

This is `LOOP1` seen from the arc-set side — there, optima were ≥ 3 loop-swaps
apart; here, the champion cannot move in `v` at all without a 4-class move.

### 5g. The 4-class vacating move — impossible, not merely hard

The natural fix is exactly that move: vacate one of the four `a_L = 4` loops by
re-cutting all four of its classes at once. It fails, and completely.

At the champion 138 loops are saturated (`a_L = 6`) and exactly four hold
`a_L = 4`, so the **only free slots anywhere** are the 8 missing generators of
those four loops. Vacating `L` requires each of its 4 arc-start classes to have
*some* rotation that is a missing generator of another thin loop. Measured:

```
loop 422: usable alternatives per class = [0, 0, 0, 0]
loop  60: [0, 0, 0, 0]      loop 56: [0, 0, 0, 0]      loop 372: [0, 0, 0, 0]
```

**Zero in all 16 classes.** And the reason is structural — the four thin loops
are **pairwise class-disjoint**:

```
422&60: 0 shared    422&56: 0    422&372: 0
 60&56: 0            60&372: 0    56&372: 0
```

so the free slots sit in classes the other thin loops never meet. This is §3.5's
phenomenon again — loops in an `⟨s⟩`-orbit are pairwise class-disjoint.

> **So the target `v = 141, S = 124, comps = 17, p = 1` is unreachable from the
> champion by re-cutting at any move width.** Not a search failure and not a
> move-set failure: the champion's arc set is locked in `v`. Reaching `CH3 = 141`
> requires a *different* arc set, not a perturbation of this one.

That closes the perturbative line entirely. Four move sets have now been tried
against it — 1-class, graft, landing, prune (§9), and the 4-class vacate — and
the obstruction has been the same each time, stated most sharply here.

Two further caveats on the reduction itself: it rests on `A2`, whose one natural
proof route (contracting loops) is already `REF1`; and the escape region is only
narrow if one *has* a bridge, which we no longer do.

---

The lesson is the same one [`ordering.md`](ordering.md) §4 drew from `IN5`:
a verdict measured for one quantity had been promoted to a statement about a
whole class, and stood unchallenged because nothing in the corpus contradicted
it. Here the corpus could not have contradicted it — the claim was about a
*minimum over arc sets*, which no collection of strings tests.

---

## 6. Attacking `A2`, the conjecture the whole reduction rests on

> **Resolved in §8** — `A2` is a theorem. §§6–7 are the record of how it was
> attacked before that, and are kept because `A2PATH`/`A2RESCUE` are true and
> are what exposed the exit identity the proof turns on.

`CH3 ≥ v + p − 1` needs `A2` (`comps ≥ v − S`). Its one
recorded proof route is `REF1` — contract each loop and bound the quotient edges
by `S` — refuted by 5907-jupiter, 239 inter-loop edges against `S = 120`.

**`REF1` refuted the wrong statement.** The right frame is an exact
decomposition. Let `c_L` be the components of loop `L`'s arcs under *intra*-loop
δ-edges only. A full arc's exit is `start·a`, inside its own loop; a partial
arc's exit leaves the loop — indeed the family, by `FAM1`. So

```
sum_cL = R - e_intra + cyc_intra ,     cyc_intra = F        (by S1)
comps  = R - e_intra - e_inter + cyc
=>  comps = sum_cL - e_inter + (cyc - F)                    [A2DEC, exact]
```

and since `c_L ≥ 1` for each entered loop (`sum_cL ≥ v`),

> **`A2` ⟸ `e_inter − (cyc − F) ≤ S + Σ_L (c_L − 1)`.**

That is not what `REF1` tested. `e_inter ≤ S` is violated by 1270 of 1275
strings; the refined form is the live question.

### Why it still does not close

The natural bound is `e_inter ≤ n_partial = S + m` — only partial arcs leave
their loop. Feeding that in requires `Σ(c_L − 1) ≥ m`. Measured:

```
sum(c_L - 1) - m  :  min -13,  max 0,  mean -3.5     1275 strings
```

**The truth is the opposite inequality**, `Σ(c_L − 1) ≤ m`, with equality in
only 14 cases. So the crude chain overshoots by exactly `m − Σ(c_L−1) ≥ 0`.

And the deeper reason is now visible. `A3` says `comps = v − S` **exactly** on
every corpus string, so `A2` is an equality in disguise — **no chain of
inequalities carrying slack can ever establish it**. Every step has to be exact.
What is missing is precisely

> `e_inter ≤ S + Σ(c_L − 1) + (cyc − F)`

an exact accounting of the inter-loop edges, not a bound on them. That is a
sharper statement of the open problem than "prove `A2`", and it explains why
five years of bounding arguments have not touched it.

### 6a. `A2` restated as a local count — the first form that admits a proof

Pushing the decomposition one step further closes the loop. `e_inter` is not
just bounded by `n_partial`; it *equals* it minus the dead exits:

```
e_inter = n_partial - D = S + m - D        D = partial arcs whose exit is not an arc start
```

Substituting into `A2DEC`:

```
comps = sum_cL - S - m + D + (cyc - F)
```

so `comps ≥ v − S` becomes, with nothing lost:

> **`A2`  ⟺  `m ≤ Σ_L (c_L − 1) + D + (cyc − F)`**
> and `A3` (`comps = v − S`) is exactly the **equality** case.

Verified both ways:

| set | result |
|---|---|
| 1,275 n=6,7 census strings | **exact equality on every one** — which *is* `A3` |
| off-distribution loop systems | strict slack, growing: **2, 10, 28, 60** at v = 121, 125, 131, 141 |

**Why this is progress.** `comps ≥ v − S` compares two global graph quantities,
and every bounding attempt has failed for the same reason — `A3` makes it tight,
so any slack in the chain kills it (`REF1`, then `CLM` above). The restatement is
a count of **local** objects:

> every multiply-covered class must be matched by an intra-loop fragmentation,
> a dead partial exit, or an excess δ-cycle.

That is an **injection to construct**, not an inequality to bound — the first
form of `A2` that admits one. The three terms are exactly the three ways a class
being covered twice can pay for itself: it fragments a loop's intra chain, it
strands a partial arc's exit, or it closes a cycle that is not an all-full loop.

Measured distributions at n = 6, 7 say which term does the work: `D` is 0 on
1,044 of 1,275 strings and never exceeds 3, while `cyc − F` sits at 0…5. So on
real strings the burden falls almost entirely on `Σ(c_L − 1)` and the excess
cycles, with dead exits a rounding term.

### 6b. `A2` stripped to counting: `v ≤ S + W + D + cyc`

One more substitution removes `m`, `F` and `comps` entirely. Call `g ∈ K`
**broken** if its arc is partial or `g·a` is not an arc start. Loop `L` then has
`a_L − b_L` intra edges, so

```
c_L = b_L   when b_L >= 1,        c_L = 1 (a cycle)   when b_L = 0
```

and `b_L = 0` is exactly the all-full saturated loops. Hence
`Σ(c_L − 1) = Σb_L − (v − F) = (n_partial + W) − v + F`, with

> `W` = number of **full** arcs whose next loop generator is not an arc start

Substituting into `A2LOC` with `n_partial = S + m`, both `m` and `F` cancel:

> ## `A2`  ⟺  `v ≤ S + W + D + cyc`

Four elementary counts: loops entered, splits, gaps after full arcs, dead
partial exits, δ-cycles.

| set | result |
|---|---|
| 1,275 census strings (n = 6, 7) | **0 violations, slack exactly 0** — i.e. `A3` |
| off-distribution loop systems | slack **2, 10, 28, 60** at v = 121, 125, 131, 141 |

matching the `A2LOC` numbers term for term. Off-distribution `W = D = 0` and
`cyc` carries everything (117, 105, 93, 75); on real strings the slack vanishes.

### 6c. What a proof now needs

The form suggests its own charging argument — assign each entered loop to one of
the four counts:

* an **all-full saturated** loop pays with its own δ-cycle (`F ≤ cyc`, by `S1`);
* any other loop has a broken generator: pay to `W` if the break is a gap after
  a full arc, to `S` if it is a partial arc.

**The gap is the double-count.** A multiply-covered class `C` has `μ_C` partial
arcs lying in `μ_C` *distinct* loops (§3.4) but contributes only `μ_C − 1` to
`S`. So one loop per multiply-covered class goes unpaid, and must be absorbed by
`D` or by an excess cycle. That residue is exactly `m − Σ(c_L − 1)`, measured at
**0…13**.

So the whole of `A2` now sits on one question: *why can every multiply-covered
class find a second broken generator, a dead exit, or a spare cycle to charge
to?* That is a finite, local statement about one class and its `μ_C ≤ 3` loops
(`B2`), which is a far smaller object than the graph inequality we started with.

### 6d. The charging is a matching problem, and that is where it stops

Testing the charge directly: for each multiply-covered class, how many of its
loops carry an **alternative** charge (`b_L ≥ 2` — a second broken generator, so
the loop need not be paid for by this class)? Over 52,318 multiply-covered
classes in 1,275 census strings:

| loops with an alternative | classes | |
|---|---|---|
| 0 | **581** | **1.11 %** |
| 1 | 29,093 | 55.61 % |
| 2 | 22,493 | 42.99 % |
| 3 | 151 | 0.29 % |

So the local charge exists for **98.9 %** of classes — but not all. The 1.1 %
must be absorbed by `D` or an excess cycle.

> **`A2` therefore cannot be proved by a purely local, per-class argument.**
> What it needs is Hall's condition on the bipartite graph
> (multiply-covered classes) × (available charges), because distinct classes may
> also contend for the *same* alternative loop.

That is the precise remaining obstacle, and it is a **matching** statement, not
a counting one. It is also where this line of attack stops being measurement and
becomes a proof obligation: Hall's condition on that graph is not something the
corpus can settle, since it must hold for *all* arc sets, not the ones we have.

**Status of the chain.** Every link below `CH3` is now either proved or reduced
to one clean statement:

| step | status |
|---|---|
| `CH3 = S + comps + p − 1 ≤ T` | **[THM]**, beats HPV |
| `CH3 ≥ v + p − 1` | needs `A2` |
| `A2` ⟺ `m ≤ Σ(c_L−1) + D + (cyc−F)` | **[THM]** (`A2LOC`) |
| ⟺ `v ≤ S + W + D + cyc` | **[THM]** (`A2FOUR`) |
| ⟸ a charging of loops to those four counts | 98.9 % local, rest needs Hall |

## 7. The Hall attempt

`A2` is the only unproved link under `CH3`, so it got a dedicated attack
([`code/a2hall.py`](../code/a2hall.py)). Two questions, in order.

### 7a. Is `A2` even true? — survives

`A2FOUR` makes the slack `S + W + D + cyc − v` computable in one pass, so before
attempting a proof it was worth trying to **refute** it. Minimising the slack
directly by re-cutting classes, seeded at the n = 7 champion and at
`houston_872`, 6,000 iterations each:

```
lowest slack found = 0   in both.   Never negative.
```

Together with 1275/1275 census strings at slack 0, and strictly positive slack
off-distribution, `A2` survives every attempt made here to break it.

### 7b. Does Hall hold? — yes, and this was genuinely open

The charging injects the `v` loops into the `S + W + D + cyc` tokens (`S` shared
by a class's `μ_C` loops; `W`, `D` private; cycles shared by the loops they
touch). §6d had shown 1.11 % of multiply-covered classes have no *locally*
alternative charge, so whether Hall survives contention between classes was
open. It does:

> **deficiency `v − (matching size)` = 0 on all 213 census strings tested** —
> and since the slack is identically 0 there, these are **perfect** matchings.

So the injection strategy is viable. That was not a foregone conclusion.

### 7c. What a proof now needs — one block, not the whole arc set

Taking the alternating closure of each loop gives the **minimal tight sets**, and
they **partition** the loops:

| string | blocks | sizes |
|---|---|---|
| n=7 5906 champion | 18 | 1×8, 2×2, 3, 4×2, 5×2, 10, 48, 51 (Σ = 142 = v) |
| n=6 houston 872 | 4 | 1×2, 2, 25 (Σ = 29 = v) |

Singleton blocks are loops owning a **private** token — a `W` gap or their own
δ-cycle. The large blocks are where `S` tokens chain loops together.

> So proving `A2` by charging reduces to: **every tight block `X` has
> `|N(X)| ≥ |X|`.** That is a statement about a single block and the classes
> spanning it, not about the whole arc set.

**Where this leaves the chain.** Every link under `CH3` is now proved or reduced
to that one block statement, and the two things that could have killed the route
— `A2` being false, or Hall failing — have both been tested and did not. What
remains is genuine mathematics: no amount of matching data proves Hall's
condition, because it must hold for *all* arc sets and the corpus only supplies
some.

### 7d. The Hall condition reduces to one local lemma

Working out *which* sets could break Hall pins it down completely. If `X` has no
private token then every `L ∈ X` has all its broken generators as live partial
arcs, and for a **closed** `X` the condition becomes

> `Σ_{L∈X} (b_L − 1) ≥ |𝒞(X)|`

so Hall fails precisely when a closed block is made of `b_L = 1` loops — surplus
zero but `|𝒞(X)| > 0`. For a saturated loop, `b_L = 1` means it meets exactly
**one** multiply-covered class. And that is the plurality case:

| `b_L` | 0 | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|---|
| loops | 5,156 | **32,358** | 15,453 | 6,398 | 2,497 | 1,359 | 1,332 |
| | 7.99 % | **50.13 %** | 23.94 % | 9.91 % | 3.87 % | 2.11 % | 2.06 % |

Half of all 64,553 entered loops carry **zero surplus**. So the dangerous
configuration is a class `C` all of whose `μ_C` loops have `b_L = 1`: then
`X = C's loops` has `|N(X)| = μ_C − 1 < μ_C = |X|` unless something else charges
it. Measured:

```
581 such classes:   533 touched by a delta-cycle
                     48 touched by a dead exit
                      0 by neither
```

and matching confirms it — all 48 strings carrying an *un-cycled* dangerous class
still saturate. (My first pass checked only cycles and wrongly flagged those 48
as unrescued; the dead exits are the other half of the dichotomy.)

> ## The whole Hall condition reduces to:
> **a multiply-covered class whose loops all have `b_L = 1` must meet a δ-cycle
> or a dead exit.**

Proving that proves `A2`, hence `CH3`'s reduction, hence that `v ≥ 142` closes
the 5905 question. It is a **local** claim — one class and its `μ_C ≤ 3` loops
(`B2`) — with 581 confirming instances and no exceptions.

**Why it should be true, informally.** A loop with `b_L = 1` has all `n−1` of its
arcs chained by intra δ-edges into a single path ending at its one partial arc.
If every loop of `C` is like that, the arcs of `C` are the *only* exits from a
set of otherwise-closed paths, so the walk entering that region must either
close it into a cycle or dead-end inside it. That is the shape of the argument;
turning it into a proof is the remaining work.

### 7e. Proving the lemma: two steps done, one to go

**`A2PATH` [THM] — the machinery.** Two elementary facts, both now proved and
verified with no exceptions:

1. **`b_L = 1` ⟹ `L`'s arcs form a single intra-path ending at the broken arc.**
   Exactly one generator of `K ∩ L` is broken, so every other `h` has `arc(h)`
   full and `h·a ∈ K`, giving an intra edge `h → h·a`. That is `|K∩L| − 1` edges
   on `|K∩L|` arcs, and the broken one has no out-edge, so they chain into a
   path — no cycle. *Verified 32,358 / 32,358.*
2. **Every inter edge into such an `L` lands on that path's HEAD.** The δ-graph
   has in-degree ≤ 1 (`δ` injective, arc starts distinct), and every arc of the
   path except the head already has an intra in-edge. *Verified: 30,518 inter
   edges into `b_L = 1` loops, every one into the head, **zero** into the middle.*

**What that buys.** For a dangerous class the `μ` paths `P_1 … P_μ` have

* **out-degree ≤ 1** — only the broken arc `α_i` exits `L_i`;
* **in-degree ≤ 1** — only the head receives.

So they form **disjoint chains and cycles**. Two of the three cases now close
themselves:

| case | outcome |
|---|---|
| the paths close among themselves | that is a δ-cycle → `A2RESCUE` holds |
| they chain and the last exit is dead | that is a `D` token → `A2RESCUE` holds |
| **they all chain OUT of `X` with live exits** | **not yet excluded** |

**The remaining gap, stated exactly.** Rule out: every `α_i` exits to an arc
outside `X = {L_1…L_μ}`, and no δ-cycle passes through any `L_i`. Empirically
this never happens — 581 dangerous classes, 533 closed by a cycle, 48 by a dead
exit, none by neither — but that is measurement, not proof.

This is where the argument stands. Two of three cases are theorems; the third is
open. I have not proved `A2`, and nothing above should be read as claiming
otherwise.

### 7f. Case 3 is impossible — `A2RESCUE` is a theorem

Instrumenting the 581 instances made the answer visible. All of them have
`μ = 2`; every chain leaving `α_i` returns to `X` or dies in **one hop**
(`min 0, max 1`); and the rescuing cycle is always **confined to `X`**. Testing
the obvious guess: **all 1,162 exits land on the other path's head.** That is an
identity, and here it is.

**Theorem.** *A multiply-covered class `C` all of whose loops have `b_L = 1`
meets a δ-cycle or a dead exit.*

*Proof.* Let `C`'s arcs be `α_1 … α_μ` in cyclic order round `C`'s ring, `α_p` in
loop `L_p` with start `s_p` and end `e_p`. Consecutive arcs tile the ring, so
`s_{p+1} = σ(e_p)`, i.e. `e_p = σ^{-1}(s_{p+1})`. By the **definition** of
`a = c^{n−1}d`, `δ(σ^{-1}(x)) = x·a` for every `x` — so

```
δ(e_p) = δ(σ^{-1}(s_{p+1})) = s_{p+1} · a
```

*Case (i): `s_{p+1}·a ∉ K` for some `p`.* Then `α_p`'s δ-exit misses `K`, so
`α_p` is a dead partial arc in `L_p` — a dead exit meeting `C`. ∎

*Case (ii): `s_{p+1}·a ∈ K` for every `p`.* Since `a` acts within a loop,
`s_{p+1}·a` is an arc start of `L_{p+1}`. By `A2PATH` the arcs of `L_{p+1}` form
a single intra-path ending at `s_{p+1}`, and its head is the unique arc with no
intra in-edge — an arc at `h` has one iff `h·a^{-1} ∈ K` and is unbroken, and
`s_{p+1}` is the *only* broken generator, so the head is exactly `s_{p+1}·a`.
So `α_p`'s exit lands on `P_{p+1}`'s head. Holding for every `p`, the paths
close: `P_1 → P_2 → … → P_μ → P_1` is a δ-cycle meeting every `L_p`. ∎

The cases are exhaustive, and (ii) forces saturation on its own: an *unsaturated*
`b_L = 1` loop must have its gap immediately after `s_{p+1}` — otherwise the
generator before the gap is a second broken one — and that is `s_{p+1}·a ∉ K`,
i.e. case (i). The 48 dead-exit rescues are exactly the unsaturated instances.

**Verified:** `δ(σ^{-1}(x)) = x·a` on 120/120, 720/720 and 5040/5040
permutations at n = 5, 6, 7.

### 7g. What this does and does not settle

`A2RESCUE` is now **[THM]**, and case 3 of §7e is closed — it cannot occur.

**But it does not by itself prove Hall, and §7d overstated when it called this
"the whole Hall condition".** Hall needs `|N(X)| ≥ |X|` for *every* `X`. For a
closed `X` with no private token that is `Σ_{L∈X}(b_L − 1) ≥ |𝒞(X)|`.
`A2RESCUE` kills the extreme case — no class in `𝒞(X)` can have *all* its loops
at `b_L = 1`, since such a class brings a private token. So every
`C ∈ 𝒞(X)` has at least one loop with `b_L ≥ 2`. What remains is that those
surpluses must cover all of `𝒞(X)` without contention — a **capacity-matching**
statement one level down, where a loop with `b_L = k` can absorb `k − 1` classes.

So the ladder now reads:

| step | status |
|---|---|
| `CH3` beats HPV | **[THM]** |
| `A2LOC`, `A2FOUR`, `PATHTAIL`, `A2PATH`, `SHARE` | **[THM]** |
| `A2RESCUE` — the extreme case of Hall | **[THM]** *(this section)* |
| Hall in general — the capacity matching | **open** |
| `A2` | follows from Hall |

---

## 8. `A2` is proved

The `A2RESCUE` proof used the identity `δ(σ^{-1}(x)) = x·a` on one special
configuration. It is not special — it applies to **every** arc, and following it
gives `A2` outright.

**Theorem (`A2`).** `comps ≥ v − S`.

Let `Q` be the **loop quotient** multigraph: nodes the `v` entered loops, edges
the live inter-loop δ-edges.

**(1) The exit identity.** For any arc of class `C` ending at `e`, the next arc
of `C` round the ring starts at `s = σ(e)`, so `e = σ^{-1}(s)`, and by the
definition of `a = c^{n−1}d`,

```
δ(e) = δ(σ^{-1}(s)) = s · a
```

— **an arc exits into the loop of the next arc of its own class.** If `μ_C = 1`
the next arc is itself, so the edge is intra; if `μ_C ≥ 2` the arcs of `C` lie in
distinct loops (§3.4) and the edge is inter. *Verified 1275/1275.*

**(2) Class cycles.** A multiply-covered class with all `μ_C` exits live
contributes the closed cycle `L_1 → L_2 → … → L_μ → L_1` in `Q`. Distinct
classes use distinct arcs, hence distinct edges, so these cycles are
**edge-disjoint** and therefore independent in `Q`'s cycle space.

**(3) Cycle rank.** `Q` has `v` nodes and `e_inter = (S + m) − D` edges
(`n_partial = S + m` by `ID4`, less the `D` dead ones), so its cycle rank is
`(S + m − D) − v + q` where `q = #components of Q`. That is at least the number
of fully-live multiply-covered classes, `m − D″` with `D″ ≤ D` counting classes
that own a dead arc. Rearranging,

```
v <= S + q + (D'' - D)  <=  S + q
```

**(4) `comps ≥ q`.** Every δ-component's loops lie in a single `Q`-component (any
inter edge inside it is a `Q`-edge); every `Q`-component contains at least one
δ-component (its loops have arcs); distinct `Q`-components have disjoint arc
sets.

Combining, **`comps ≥ q ≥ v − S`**. ∎

**Verified.** `v ≤ S + q` and `comps ≥ q` both hold on 1275/1275 census strings
— with slack 0 on each, which is exactly `A3` — and with strict slack
off-distribution (`v=121, S=6, q=116, comps=117`; `v=141, S=126, q=60,
comps=81`).

### What it settles

`A2` was **[CONJ]** for this repo's entire history, and its one recorded proof
route was `REF1` (contract the loops, bound the quotient edges by `S`) — refuted
by 5907-jupiter, 239 inter edges against `S = 120`. The route that works is the
same quotient, but counting its **cycle rank** instead of bounding its edges.
`REF1` was measuring the right object and asking the wrong question of it.

Consequences, all now unconditional:

| claim | before | now |
|---|---|---|
| `A2` — `comps ≥ v − S` | [CONJ] | **[THM]** |
| `A2b` — `T ≥ v + Y` | [CONJ], then IN5-dependent | **[THM]** against the optimum |
| `CH3 ≥ v + p − 1` | conditional on `A2` | **unconditional** |

So the reduction of §5 stands on its own: `CH3 ≥ v + p − 1`, tight at both n = 7
extremes, and the 5905 question is exactly *"is `v + p ≥ 143`?"* — with `v ≥ 142`
already closed by `p ≥ 1`.

The Hall/charging programme of §7 is now **unnecessary** for `A2`. It is kept
because `A2RESCUE` and `A2PATH` are true and were what exposed the identity in
(1); the capacity-matching gap of §7g no longer blocks anything.

---

## 9. Where `v + p ≥ 143` actually stands

With `A2` proved the bound has no hypotheses left, so the remaining question is
purely one of *values*: is `min(v + p)` over n = 7 arc sets equal to 143? This
section reports three measurements that between them say what is known, and
corrects one claim that was resting on a single string.

### 9a. The census cannot refute the programme — and cannot support it either

`CH3 ≤ T` bounds `v + p` from **above**, so nothing in the theory forbids a
long, sloppy superpermutation from having a small `v + p`. One with
`v + p < 143` at n = 7 would put `min CH3` below 142 and kill the reduction
outright, so this is worth one pass. `code/vplus.py` prices every string on
disk — optimal or not — with `p` verified by `chainer.min_chains`:

| n | strings | `min(v + p)` | attained at |
|---|---|---|---|
| 5 | 188 | **8** | 153-chaffin, `v=6 p=2` |
| 6 | 1030 | **30** | houston 872, `v=29 p=1` |
| 7 | 245 | **143** | the 5906 champion, `v=142 p=1` |

No refutation. But the reason it could not have refuted is worth stating: `CH3`
is exactly tight on 1,458 of the 1,463, so a real string cannot have
`v + p − 1` below its own `T`, and every string has `T ≥ T_opt`. **The
minimum is `T_opt + 1` by construction, not by evidence.**

What *is* informative is the per-`v` floor, since it is off-distribution
wherever the corpus is thin:

```
n = 5   v: 6→2   7→1   8→1
n = 6   v: 24→6  28→2  29→1  30→1
n = 7   v: 120→24  140→4  142→1  144→1
```

`p ≥ T_opt + 1 − v` fits every row, and at n = 5 and n = 6 it is **exact at
every `v`**. At n = 7 it is slack by 1 at `v = 120` and `v = 140` and tight only
at `v = 142`. So the law that would close 5905 is pinned by a **single point**,
the champion, and the corpus is empty on `121 ≤ v ≤ 139`.

### 9b. Both champions are certified local minima — the complete neighbourhood

§3c reported that cut-space annealing "found no improvement in ~4,000
iterations". That is a statement about the sampler. At `comps = 18` the exact
bound costs 6 ms, so the whole radius-1 neighbourhood — every add or remove of a
single cut — can simply be priced. `code/nbhd.py`, every value exact and every
`p` verified, no fallbacks admitted:

| seed | `CH3` | the complete neighbourhood |
|---|---|---|
| n = 6 houston 872 | 29 | `{30: 42, 31: 583}` — 625 arc sets |
| n = 7 5906 champion | 142 | `{143: 145, 144: 3122, 145: 1175}` — 4442 arc sets |

Neither champion has even a **tying** neighbour. So `142` is a *certified* local
minimum of `CH3` under single-cut moves, not merely an unbeaten one.

**The sharper reading is the trade-off, and it is identical at both `n`:**

```
n = 6:  v = 29  → min p = 2      v = 30  → min p = 1
n = 7:  v = 142 → min p = 2      v = 143 → min p = 1
```

The champion itself is `v = v*, p = 1`. So **`p = 1` at the champion's `v` is an
isolated point**: every neighbour that holds `v` fixed breaks the single free
chain, and every neighbour that keeps `p = 1` pays a loop. That is exactly the
`v`–`p` trade-off `CH3` needs, seen locally and off the census — and it is why
the bound is tight here and nowhere near tight generically (§5a). Registered as
`CH3LOC`.

Note also what the neighbourhood does *not* contain: no arc set with `v ≤ 141`.
That is `VRIG` re-measured over the complete neighbourhood instead of 3,588 of
it.

### 9c. `VLOCK` was right, but not for the reason recorded

`VLOCK` said the champion cannot lower `v` because its four thin loops are
pairwise class-disjoint, so the only free generator slots sit in classes the
other thin loops never meet. That was measured on **one** string. Over all 237
n = 7 champions (`code/vlock.py`):

> **class-disjointness of the thin loops holds in 211 of 237.** The other 26
> *do* have usable alternatives — 3 of them in 15 strings, 6 in 11.

So the recorded mechanism was a property of the point, not of length-5906
walks. The lock survives anyway, for a sharper reason. Vacating a thin loop `L`
needs **every** one of its starts to have somewhere to go — a free slot of
another *entered* loop, since landing in an unentered one just restores the `v`
it removed. The best any of the 26 manages is

```
movable − needed  =  −3        in all 26
```

— one start of a four-start thin loop can move; the other three cannot. **No
thin loop is fully movable in any champion: 237/237 locked.**

The consequence is unchanged but now properly founded: the target
`v = 141, S = 124, comps = 17, p = 1` is unreachable by re-cutting from *any*
known n = 7 optimum, at any move width. Reaching it needs a different arc set
entirely.

### 9d. `A` is the free-slot count — why every search stalls

`code/v141.py` stops starting from the answer: it drags the walk into `v ≤ 141`
with a penalty and minimises `CH3` *there*. It never arrives. In 600 iterations
from the champion the only `v` ever accepted were 142 and 143 — `v` goes **up**,
never down. That is not a tuning failure, and the reason is a one-line
consequence of the Split Identity `R = (n−1)v − A`:

> **`SLOT` [THM].** An entered loop has `n−1` generator positions of which `a_L`
> are arc starts, so the unused positions number
> `Σ_L (n−1 − a_L) = (n−1)v − R = A`. **`A` is exactly the number of free
> generator slots.** *1463/1463.*

That turns `A` from a bookkeeping residual into the *resource every arc-set move
spends*. Re-cutting a class moves one arc start, and it can only move into a
free slot — of which there are `A` in all. Two consequences:

* **Vacating a loop `L`** — the only way to lower `v` by re-cutting — must
  relocate all `a_L` of its starts into free slots of *other* entered loops.
  `L` owns `n−1−a_L` of the `A` slots and they die with it, so the move needs
  `A − (n−1−a_L) ≥ a_L`, i.e. **`A ≥ n−1`**. Below that `v` cannot fall at all,
  by counting alone.
* **Lowering `v` by one costs exactly `n−1` of `A`**, since
  `A′ = (n−1)(v−1) − R = A − (n−1)`. So re-cutting can lower `v` at most
  `⌊A/(n−1)⌋` times from any starting arc set.

This is the general form of `VLOCK`. At the champion `A = 8 ≥ 6`, so counting
does *not* forbid the move — the four thin loops hold two free slots each. What
blocks it is the finer, class-level obstruction of §9c. **Counting says which
arc sets are even candidates; §9c says none of the 237 champions is one.**

### 9e. The residue, stated plainly

The 5905 question is `min(v + p) ≥ 143` over n = 7 arc sets, and every route
tried has bounced off the same wall from a different side:

| route | verdict |
|---|---|
| `RES`, the residue cap `p ≥ ⌈comps/ord(a^r b)⌉` | **[THM]**, but needs residue-uniformity, which fails at exactly the champions (§5a) |
| `PFLOOP`, `p ≥ ⌈F_loops/(n−2)⌉` | **[REF]**, 171 violations |
| loop-space search | searches `A = 0`, which excludes every n = 7 optimum (§3c) |
| cut-space annealing | champion is a certified strict local minimum (§9b) |
| vacating a thin loop | impossible in all 237 champions (§9c) |
| living in `v ≤ 141` and minimising there | the walk cannot get in — `A` is the free-slot budget and it is 8 (§9d) |
| the corpus | tells us nothing — `CH3` is tight on it by construction (§9a) |

What would actually settle it is a lower bound on `p` valid **without** the
residue-uniformity hypothesis. §5a localised that correctly: `p = 1` means the
free-join graph — a *functional* graph, out-degree ≤ 1 by `CH1` — admits a
Hamiltonian path over all `comps` components. §9b now adds that this property is
**isolated**: it survives no single-cut perturbation at fixed `v`, at either
`n`. That is a strong hint that Hamiltonicity of the free-join graph is
obstructed at low `v`, and no hint at all as to why.

`A2` is proved; this is not, and nothing above should be read as if it were.

---

## 10. `FORCE`: the correct `CH1`, and why it still does not bound `p`

§9e said the missing piece is a lower bound on `p` without the
residue-uniformity hypothesis. This section reports the attempt: one new
theorem, one refuted claim, and one route closed with a reason.

### 10a. `CH1` is false — on the census, not just off it

`CH1` was recorded as "the free-join digraph on `(component, break-point)`
states has out-degree ≤ 1". Its own entry admitted "away from an exact cover it
is measured, not proved". It is now measured **false**, and not only on the
annealer states `chainer.py` already warned about — on real strings:

```
n = 6   out-degree {0: 107808, 1: 27516, 2: 19}
n = 7   out-degree {0: 123848, 1: 37112, 2: 38, 3: 11}
```

Nothing depended on it: `chainer.free_succ` returns a *list* and `runs`
branches over it. `CH1` → **[REF]**.

### 10b. `FORCE` [THM] — the length-gated version

`Struct.exits(g, l)` returns the `3!` weight-3 targets of a block of `l` arcs,
each with a **cap**: how far the next block may run before re-entering a class
this one already burned. `coset_lemma.py` verifies that exactly one target
survives `cap ≥ l′` precisely when `l + l′ ≥ 2n−3`, and that the survivor is om.

> **`FORCE`.** Call a free edge **core** when the exit arc is full and
> `l + l′ ≥ 2n−3`, **fringe** otherwise. Then om is a single group element, so
> the core target is the single permutation `start·b`; distinct components have
> distinct arcs and hence distinct entries. **Every state has at most one core
> out-edge, and it lands on `start·b`.** *1463/1463, zero exceptions.*

One convention trap, recorded because it cost a run: `exits()` measures from the
block's last **arc start**, not its end, so the om target is `start·b`. Using
`end·b` is simply the wrong group element and fails on 243 of 245 n = 7 strings.

So out-degree ≥ 2 forces a **fringe** edge, and a fringe edge needs an
incomplete block at one end — `l = l′ = n−1` gives `2n−2 ≥ 2n−3` and is always
core. That is the mechanism `RES` was reaching for through residues, and
*lengths, unlike residues, do not go mixed at the champions*.

### 10c. The chain-length law, and why the bound is not there

With `FORCE` the natural bound is

```
p ≥ (number of core-runs) − (fringe edges used) ≥ ⌈comps/(n−2)⌉ − F_used,
```

since core edges alone form a functional graph. Measuring `L(f)` — the longest
free chain, in components, reachable using exactly `f` fringe edges — over the
whole corpus:

| n | `L(0)` | `L(1)` | `L(2)` | `L(3)` | `L(4)` | `L(5)` | `L(6)` | `L(7)` |
|---|---|---|---|---|---|---|---|---|
| 5 | **3** | 3 | 3 | | | | | |
| 6 | **4** | 4 | 7 | 7 | 9 | 9 | 9 | |
| 7 | **5** | 5 | 8 | 9 | 10 | 13 | 14 | 18 |

`L(0) = n−2` **exactly** at all three `n`. That is the Pentad cap recovered as
the `f = 0` case — the honest content of `RES`, and of `CHLB` before it was
refuted. Past `f = 0`, `L` grows at roughly **1.4 components per fringe edge**
at n = 7.

**The route fails, and cleanly.** The bound needs an upper bound on fringe
edges, and there is none:

* fringe edges are **75%** of all free edges across the corpus;
* at the 5906 champion specifically there are **118 fringe against 16 core**,
  and its 18-component chain needs **10** of them.

A budget of 10 out of 118 available is not scarcity. So the core/fringe split
says *why* long chains are possible — they buy fringe edges, which need
incomplete blocks, which need splits — and supplies no number.

**Checked against what already existed**, as the plan required. Chain-Count's
general form `c_{n−1} ≤ (n−2)(1 + Y + (B − c_{n−1}))` is recorded in the arsenal
as **vacuous away from `B = (n−2)!`**. This is the same wall reached from the
free-join side: the `f = 0` case is sharp and everything above it is unbounded.
Registered as `FRINGE` **[MEAS]** so the route is not attempted a third time.

### 10d. What is left

`FORCE` is banked and `CH1` is corrected, but the residue of §9e is unchanged:
**no lower bound on `p` without residue-uniformity is in sight.** The three
things now known to be sharp and simultaneously useless are the same fact in
three languages — Pentad (`ord(s) = n−2`), `RES` (`ord(a^r b)` under uniform
residue), and `FRINGE` (`L(0) = n−2`). Each is exact at `f = 0` and silent
above it.

---

## 11. `p` is a break-point phenomenon, and nothing else

§10 closed the core/fringe route. This section reports what replaced it, which
is not a bound but is the most useful thing learned about `p` so far: it says
where the bound *cannot* be, and it does so exhaustively.

### 11a. The measurement

A state is `(component, break-point)`, and the break point fixes the entry
**and** the exit together. Drop that coupling — keep only "some break of `i` can
free-join to some break of `j`" — and `p` becomes an ordinary min path cover on
`comps` nodes. `code/freejoin.py --relax` computes both:

| n | strings | relaxed `p` | exact `p` − relaxed `p` |
|---|---|---|---|
| 5 | 188 | 1 on **187** | 0 on 186, 1 on 2 |
| 6 | 1030 | 1 on **all 1030** | 0 on 1011, 1 on 18, 5 on 1 |
| 7 | 241 | 1 on **all 241** | 0 on 239, 3 on 2 |

Per `v`, as `(min relaxed p, min exact p)`:

```
n = 6    24:(1,6)   28:(1,2)   29:(1,1)   30:(1,1)
n = 7   140:(1,4)  142:(1,1)  144:(1,1)
```

> **`PCOUPLE`.** Component-level connectivity is **never** the obstruction.
> Every arc set measured — 1459 of them — has a component-level Hamiltonian
> path. What stops `p = 1` is that the breaks cannot be chosen consistently
> along it.

The n = 6 `v = 28` strings are the cleanest witness: `S = 18, comps = 10,
p = 2`, and their ten components *do* admit a Hamiltonian path at component
level. If the breaks could be made consistent, `CH3 = 18 + 10 + 1 − 1 = 28` and
the bound would permit 871. They cannot.

### 11b. What this rules out, and what it leaves

**It closes the matching relaxation properly.** §3b recorded that maximum
bipartite matching "returns 0 or 1 at every state tested" and diagnosed it as
discarding the state-consistency coupling. That diagnosis was right and is now
quantified: matching is not weak — *the relaxed problem's answer is identically
1*. Any lower bound on `p` read off the component graph, its degrees, its
connectivity, or its packing structure is **provably worthless**, because that
graph's min path cover is 1 on every arc set measured.

That retires, in one stroke, the whole family of attacks that forget the break
point — including the one §10 was building toward, since `L(f)` is also a
statement about edges rather than about consistent break selection.

**And it says where a bound must live.** `RES` and the Pentad Lemma are already
consistency statements in disguise: at an exact cover a component is a whole
loop, its break point *determines* its om successor, and the `⟨s⟩`-orbit closes
after `ord(s) = n−2`. That is the only known mechanism that survives `PCOUPLE`,
and generalising it away from uniform residue is the open problem — now stated
in the right language.

So the target has sharpened from

> *"lower-bound `p`"*  to  *"lower-bound the number of chains in a
> break-consistent path cover, given that the unconstrained one is 1"*.

Nothing above is a bound, and `v + p ≥ 143` at n = 7 remains open.

---

## 12. The core cap is a theorem, and it closes the `v = 121` rung

§10 concluded that the core/fringe split "supplies no number". That conclusion
was drawn from champion arc sets and **is wrong at small `S`**. This section
corrects it and turns the split into a bound that closes a rung.

### 12a. Where §10 went wrong

Fringe count is not a constant fraction — it scales with `S`:

| n | at `S = 0` | at the champion |
|---|---|---|
| 6 | 120 core, **0 fringe** | 8 core, 8 fringe |
| 7 | 720 core, **0 fringe** | 8 core, 7 fringe |

At an exact cover every block is a complete traversal, so `l = l′ = n−1`,
`l + l′ = 2n−2 ≥ 2n−3`, and **every edge is core**. The "75% of edges are
fringe" figure in §10c is a corpus average dominated by champions. Fringe
abundance is a property of the high-`S` regime, and §5c says the 5905
requirement is tightest at *low* `v`, which is exactly where `S` is small.

### 12b. `CORECAP` [EXH] — the cap is `n−2`, and it is not the Pentad cap

The bound needs an upper bound on how many components one core-only chain can
cover. A core edge needs `l + l′ ≥ 2n−3` with `l, l′ ≤ n−1`, so both blocks have
length `n−2` or `n−1` and two consecutive `(n−2)`s are impossible. The om step
out of a length-`l` block is `a^{l−1}b`, so a core chain is a word in
`s = a^{n−2}b` and `u = a^{n−3}b` — and `⟨s,u⟩ = H` has order `(n−1)!`, so
**nothing caps it by group order.** What caps it is class burning.

Exhausted directly (left multiplication permutes classes and commutes with right
multiplication by `a` and `b`, so the chain may start at the identity WLOG):

| n | longest core-only chain | extremal block lengths |
|---|---|---|
| 5 | **3** = n−2 | `[3, 4, 3]` |
| 6 | **4** = n−2 | `[4, 5, 5, 4]` |
| 7 | **5** = n−2 | `[5, 6, 6, 6, 5]` |

The witnesses matter: they **mix** `n−2` and `n−1` blocks and start and end on a
short one. So this is strictly stronger than the Pentad Lemma and `RES`, which
cap chains of *complete* traversals at `ord(s) = n−2`. The same number arises
from a different mechanism. `code/freejoin.py --corecap`.

**Gap, stated.** This exhausts chains of *single blocks*. A component with two
or more blocks has a head block and a tail block joined by an arbitrary group
displacement, so the argument does not cover it. Measured `L(0) = n−2` anyway on
all 1463 census strings **and off the corpus** — constructed `v = 121` arc sets
at every `A`, and annealer-perturbed sets — but that part is `[MEAS]`.

### 12c. `PFRINGE` [THM]

Chain `i` splits into `f_i + 1` core-runs separated by its `f_i` fringe edges,
each run covering at most `c` components. Summing over a decomposition into `p`
chains covering `comps` components, `comps ≤ c(F_used + p)`, so

> **`PFRINGE`.  `p ≥ ⌈comps/c⌉ − F`**, with `c` the core cap and `F` the
> available fringe edges.

At `S = 0` this reads `p ≥ comps/(n−2) = (n−3)!` — which **is `RUNG0`**, now
recovered as a special case rather than a separate argument.

### 12d. `v = 121` closes for every `A`, over the cover-plus-one-loop family

`RUNG1` (§5d) closed this rung for `A = 0` only, and said so. Adding just *some*
of a fresh loop's `n−1` generators gives `S = k`, `A = (n−1) − k`, so sweeping
every nonempty subset sweeps every `A`. A 5905 at `v = 121` needs `p ≤ 21`:

| `A` | 5 | 4 | 3 | 2 | 1 | 0 |
|---|---|---|---|---|---|---|
| fringe `F` | 1 | 1 | 1 | 2 | 3 | 45 |
| `PFRINGE` bound on `p` | 23 | 23 | 23 | **22** | 21 | — |
| verdict | closed | closed | closed | closed | *short by 1* | §5d |

`A = 1` is short by exactly one — and then closes anyway on the **packing**
floor, which returns `p ≥ 24` there. So the rung does not actually need
`PFRINGE` at `A = 1`; the two sound floors close different parts of it.

`code/rung7.py` prices the family **exhaustively** — all 720 fresh loops × 63
generator subsets = 45,360 arc sets per base cover, on all four base covers on
disk, **181,440 in total** — every value a sound *lower* bound on `CH3` (the
packing floor understates `p`, which understates the bound, so a minimum
computed this way is safe to conclude from):

```
CH3 floor histogram   {144: 12240, 145: 2160, 146: 22320, 147: 3572, 148: 5068}
minimum               144            (a 5905 needs 141)
```

The histogram is **identical on all four bases**, and the minimiser is the same
arc set every time (`S=1, comps=120, p=24, A=5`). The margin is 3.

> **No 5905 in the cover-plus-one-loop family at `v = 121`, at any `A`.**

**Scope, stated plainly.** This is exhaustive over *exact cover + one partial
fresh loop*. It is **not** exhaustive over all `v = 121` arc sets: for `A > 0`
the 121 entered loops need not contain an exact cover, and nothing here rules
that out. `RUNG1`'s "every `A = 0` arc set is a cover plus one loop" holds only
at `A = 0`. So §5d's caveat is narrowed, not removed.

---

## 13. The Egan−1 line, consolidated — and the `+1` that would sharpen it

`RUNG0`, the Chain-Count Lemma, the Exposure Bound `S5` and `EGAN1` are four
records of **one statement**. Worth saying once.

### 13a. `EGAN1L` [THM]

`v = (n−2)!` forces `A = 0` and `S = 0` (from `R ≥ (n−1)!` with
`R = (n−1)v − A`), so every class is a single full arc, every entered loop is
saturated and all-full, and by `S1` each closes into a δ-cycle of `n−1` arcs.
Then `comps = (n−2)!` with a single residue `r = n−2`, the cap is
`ord(a^{n−2}b) = ord(s) = n−2`, so `p ≥ (n−3)!` and

```
CH3 = 0 + (n−2)! + (n−3)! − 1 = (n−1)(n−3)! − 1 = Egan_T − 1.
```

| n | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|
| bound length | 33 | 153 | 872 | **5907** | 46204 | 408965 |
| with the `+1` (§13d–e) | — | — | **873** | **5908** | **46205** | ? |

### 13b. What it excludes — and what it does not

The bound applies **only at that rung**, and the records do not sit there for
n ≥ 6:

| n | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|
| record `v` | 2 | 6 | 29 | 142 | 839 | 5760 |
| `(n−2)!` | 2 | 6 | 24 | 120 | 720 | 5040 |
| at the rung? | yes | yes | **no** | **no** | **no** | **no** |

So it excludes only where the bound *exceeds* the record — **n = 7**, where
`5907 > 5906`:

> **No n = 7 champion enters exactly 120 loops.**

At n = 4, 5, 6, 8 the bound *equals* the record, so one more unit would exclude
there too. At n = 9 it is one below.

This also supersedes a stale headline of our own:
[`pentad_lemma.md`](pentad_lemma.md) advertises **5895** for this same rung —
twelve worse, by an independent route. That note now says so at the top.

### 13c. The `+1`, which is the real prize

At n = 6 the extra unit is a **theorem**. `T = 29` would force six om-chains of
exactly 4 traversals — six full `⟨s⟩`-orbits exactly covering the 120 classes,
of which 8640 exist — with all five connecting jumps of weight exactly 4. **0 of
the 8640 can be so linked**, so `T ≥ 30` and `v = 24 ⟹ length ≥ 873`.

The n = 7 analogue is *the same question*: `T = 143` forces 24 chains of 5 — a
Pentad partition of the 720 classes — with all 23 links of weight 4, i.e. link
cost 46. `code/pentad_search.py` solves the linking **exactly per partition**,
and over **1507 distinct Pentad partitions**:

```
link cost   52 (867)   54 (503)   55 (137)      never 46, never below 52
```

If no partition reaches 46, then `v = 120 ⟹ T ≥ 144`, length ≥ **5908**. And
the same `+1` at n = 8 would take 46204 to 46205 and **exclude the exact-cover
rung there**, where the bound currently only ties the record.

### 13d. Settled: `v = 120 ⟹ length ≥ 5908`

The search over partitions could never have closed this. But the `+1` is a
**feasibility** question, so every edge of cost ≠ 2 can be deleted and the whole
thing posed as **one** model quantifying over all partitions at once — orbit
selection, exact cover, rotation choice and ordering together
(`code/egan1p.py`).

The equality case is forced exactly, with every step a registered theorem:

```
T = 143  needs  B + Y = 143,  B ≥ comps = 120,  Y ≥ p − 1 = 23
         ⟹  B = 120 and Y = 23 EXACTLY
   B = comps  ⟹  every block is a complete traversal
   Y = p − 1  ⟹  exactly 24 chains, 96 free joins of weight 3
   Y = Σ(w−3) = 23 over 23 links  ⟹  every link has weight 4
```

So `T = 143` at `v = 120` **is** the statement "24 disjoint Pentads linked by 23
weight-4 jumps". CP-SAT returns **INFEASIBLE in 239 s** — 5040 states, 115,920
weight-4 edges. Therefore

> **`v = 120` ⟹ `T ≥ 144`, length ≥ 5908 = Egan(7).**

**The gate that makes this believable:** the same model at n = 6 returns
INFEASIBLE in **one second** and reproduces the known theorem (873) — a result
that originally required enumerating all 8640 covers. The encoding is checked
against a case whose answer we already knew.

Dependence stated plainly: this rests on CP-SAT's infeasibility certificate,
the same standing as the n = 6 branch-and-bound it reproduces.

### 13e. The same `+1` at n = 6, 7 and 8 — a new exclusion at n = 8

The symmetry reduction is what made n = 8 reachable. Left multiplication is a
relabelling of symbols — it preserves weights, permutes classes, and commutes
with right multiplication by `a` and `b`, all three checked directly — so **WLOG
the path's first chain starts at the identity**. That is an `n!`-fold reduction,
and it also prunes every orbit clashing with that fixed chain.

*(Decomposing by **family** would have been unsound: a partition may mix chains
from different families, so checking monochromatic ones proves nothing.)*

| n | states | weight-4 edges | time | verdict | bound |
|---|---|---|---|---|---|
| 6 | 233 | 2,540 | 0 s | INFEASIBLE | **873** |
| 7 | 3,431 | 61,874 | 22 s | INFEASIBLE | **5908** |
| 8 | 35,989 | 770,536 | 66 s | INFEASIBLE | **46205** |

Against best-known `s(n) = 872, 5906, 46204`:

> **The exact-cover rung is excluded for champions at n = 6, 7 and 8.**

At n = 8 that is **new** — the Egan−1 line alone only *tied* the record there
(46204), so the `+1` is exactly what turns a tie into an exclusion.

Two things made it tractable. The symmetry above (35,989 states instead of
40,320, and 3 GB instead of the 23.8 GB that got the first attempt OOM-killed),
and generating weight-4 targets directly as the `4!` permutations of the first
four symbols rather than scanning all `n!` — at n = 8 the difference between
`8.6 × 10⁵` and `1.45 × 10⁹` weight evaluations. The fast version reproduces the
slow one's edge counts exactly, which is how it is checked.

`EGAN1P` **[EXH]**. n = 9 is running; there the `+1` would only tie 408966.
