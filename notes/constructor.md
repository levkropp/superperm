# The constructor framework

Until now this repo could only *bound* superpermutations, never *build* one.
An audit of all 60+ files in `code/` found no program that emits a string.
This note records the framework that closes that gap, what it validated, and —
importantly — where it currently falls short.

| file | role |
|---|---|
| [`code/census.py`](../code/census.py) | measure every string on disk in ledger coordinates |
| [`code/superstruct.py`](../code/superstruct.py) | n-generic group / loop / family / Pentad structure |
| [`code/build.py`](../code/build.py) | design ↔ walk ↔ string, with independent coordinates |
| [`code/mcolour.py`](../code/mcolour.py) | the multi-colouring search |

---

## 1. Census — 182 strings, one identity

`census.py` reads `data/n7/`, `data/houston_872.txt` and the upstream clone
(n = 5…9), measures each with the *existing* verified machinery
(`permgraph.string_to_path`, `blockcount.Model.measure`, `dirty.dissect`) and
asserts the master identity `T = (n−1)d + (B+Y) − A`.

**182 strings, identity holds on 182.** Summary:

| n | strings | best | HPV(n) | excess | HPV-tight |
|---|---|---|---|---|---|
| 5 | 1 | 153 | 152 | 1 | 0/1 |
| 6 | 7 | 872 | 867 | 5 | 3/7 |
| 7 | 169 | 5906 | 5884 | 22 | 163/169 |
| 8 | 2 | 46204 | 46085 | 119 | 2/2 |
| 9 | 3 | 408966 | 408246 | 720 | 2/3 |

Four things it settled that were previously inferred:

1. **The Egan vertex is uniform in n.** Every Egan string — 873, 5908, 46205,
   408966 — sits at exactly `A=1, B=1, Y=0, d=(n−3)!, S=(n−1)(n−3)!−1`, i.e. a
   **single block** with maximal splits. An earlier hand-entered row had 5908
   at `(d=0, B=120, Y=24)`; that describes the abstract complete-traversal
   construction, not the string. The census caught the error.
2. **409113 (n=9) is the d=0 vertex** — the first walk measured anywhere here
   with an exact cover. Its `Y=867` confirms the Chain-Count floor
   `Y ≥ (n−3)!−1 = 719` empirically.
3. **The champion invariant is measured, not inferred**: all 169 length-5906
   strings have `B+Y−A = 10` exactly, while `A` ranges 8…16 and `S` 116…124.
4. **HPV-tightness is not necessary for optimality** — 4 of the 7 length-872
   strings are slack (`d = 3, 4`) yet still reach `T = 29`.

The saving formula `(B+Y−A)/(n−2)` checks against `Egan − record` at every n:
1, 2, 1, 0 for n = 6, 7, 8, 9.

## 2. Structure library and builder

`superstruct.py` self-checks at n = 5…8 (0.4 s at n = 8) against
`lemma_arsenal.md` §3.3/§3.5: `ord(a)=n−1`, `ord(s)=n−2`, n!/(n−1) loops, n
families of (n−2)! each, every family an exact cover, Pentad loops pairwise
class-disjoint.

`build.py` represents a walk as its **arc list** `[(start, length)]` — the
minimal faithful design — and re-derives R, S, v, A, B, Y, clean, dirty,
n_partial, N from it *without* using `blockcount`/`dirty`. The gate runs the
round trip `string → path → design → build → string` and compares both
coordinate implementations: **179 strings (n = 5…8), all exact.**

## 3. The multi-colouring search — and the cost collapse

A class C is a cyclic ring of n permutations; a walk covers it with `mu_C ≥ 1`
contiguous arcs, i.e. a nonempty set of cut positions `chi(C) ⊆ Z_n`, with
`S = Σ(mu_C − 1)`. Since §3.4 forces the arcs of one class into distinct
families, `chi` is a genuine set-valued colouring, and `|chi(C)| = 1` recovers
the split-free n-colouring of §3.3.

The objective then collapses to a pure asymmetric TSP:

> **`T = S + 1 + Σ f(w)`,  where `f(w) = max(0, w−2)`**

— a weight-2 jump is free, weight-3 costs 1 (a block), weight-w costs w−2. So
with the cuts fixed the problem is a TSP over **R ≈ (n−1)! arcs, not n!
permutations**: 120 / 720 / 5040 nodes at n = 6/7/8 against 720 / 5040 / 40320.

### What it achieves

| seed | result | coords | valid? |
|---|---|---|---|
| monochromatic family, n=6 | **T = 30, length 873** | d=0, S=0, B=24, Y=6 | yes |
| Houston 872, n=6 | **T = 29, length 872** (holds) | d=5, S=25, B=4, Y=0 | yes |
| random colouring, n=6 | T ≈ 158, length 985 | — | yes |
| monochromatic family, n=7 | **T = 149, length 5913** | d=0, S=0, B=120, Y=29 | yes |

So the repo can now build superpermutations. Two independent confirmations
that the representation and objective are right:

* seeded at the champion the search *scores and holds* T = 29 and re-emits a
  valid 872;
* cold-start at n = 7 it lands on `B = 120, Y = 29` — exactly the coordinates
  `lemma_arsenal.md` §8 records for the known split-free 5913, rediscovered
  from a family seed with no knowledge of that string.

### Where it falls short — the gate is NOT met

**Cold-start it reaches only T = 30**, the split-free optimum, not the true
optimum 29.

An earlier draft of this note read the diagnosis as "champions are ~98 % free
jumps". [`notes/second_order.md`](second_order.md) A1 shows that is the wrong
way round. Egan's construction has `B = 1` at every n — **zero** costly jumps,
100 % free — and the Free-Jump Lemma says a record beating it by k must *buy*
exactly `(n−2)k + A − Y − 1` costly jumps:

| n | Egan | costly | record | costly |
|---|---|---|---|---|
| 6 | 873 | **0** | 872 | 3 |
| 7 | 5908 | **0** | 5906 | 17 |
| 8 | 46205 | **0** | 46204 | 5 |

So freeness is what the *baseline* has; improving on it means paying for
weight-3 jumps in exactly the right places. That is a needle, not a basin — a
split costs +1 immediately and only repays if both halves land on free edges —
which is why annealing from a split-free seed never crosses the barrier.

**The next step follows directly**: stop searching orderings and search the
**free-jump digraph** — build the digraph on candidate arcs whose edges are the
weight-≤2 moves (the unique δ successor, plus the dirty exits out of every
partial arc, which `lemma_arsenal.md` §8 measured as "nearly free"), and look
for long paths there. Costly jumps are then the *residue* to be minimised
rather than an edge cost to anneal against. That is the structural analogue of
what the ledger already says: minimise `v`, the number of 2-loops entered.

## 4. Status

Built and validated: the census, the structure library, the builder with its
round-trip gate. Built but under-powered: the search. No new record; none was
expected at laptop scale, and the plan said so up front. The concrete deficit
is one unit of `T` at n = 6, and the reason for it is now measured rather than
guessed.

---

## 5. The two-level rebuild — `code/gen2.py`

`B = comps` on 44,370/44,370 optima says the ordering is nearly determined by
the arc set, so `gen2.py` searches **only arc sets** and takes the blocks as the
δ-components. The inner problem — chaining those components — is then tiny:
`comps` is 4 at n=6, 6 at n=8, 18 at n=7.

**Validated.** Seeded at the n=6 champion it reproduces it exactly: T = 29,
length 872, `S=25 v=29 A=0 B=4 Y=0 comps=4`.

**One real discovery along the way.** Cycle components must be broken at the
*right* place, not a canonical one: breaking the champion's cycles canonically
costs `Y = 9` where the right break costs `0`. So the inner problem is a
generalized TSP over (component, break-point) states, exact by Held-Karp while
`comps ≤ 12`.

**Chainer progress at the exact-cover seed** (comps = 24, true optimum Y = 6):

| method | Y |
|---|---|
| greedy | 19 |
| greedy + Or-opt + exact break DP | 11 |
| bipartite matching on free joins | 15 |
| **realisable free-chain cover** | **9** |

The matching does badly for a structural reason worth recording: a component's
break point fixes *both* its entry and its exit, so a free om join is not an
independent choice — which is exactly why om-chains cap at `ord(s) = n−2`.
Matching relaxes that coupling and yields chains that cannot be realised.

**Cold start still fails, and the reason is A3 again.** Every ordering-free
objective is minimised by the exact cover, and even adding the admissible chain
bound `Y ≥ ⌈comps/(n−2)⌉ − 1` scores the exact cover at `0 + 24 + 5 = 29` — the
true optimum — so the search has no gradient away from it. The gradient lives
only in the exact `Y`, which costs ~1.4 s per evaluation at `comps = 24`.
Closing this needs a **fast exact chainer**, not a better annealer.

---

## 6. The exact chainer — [`code/chainer.py`](../code/chainer.py)

The inner problem is not a TSP. Measure the **free-join** digraph, whose states
are (component, break-point) pairs and whose edges are the joins costing
`max(0, w−3) = 0`:

| seed | comps | states | free out-degree |
|---|---|---|---|
| n=6 exact cover | 24 | 120 | **1** for all — a permutation, 30 cycles of length 4 |
| n=6 houston 872 | 4 | 145 | 0 for 129, 1 for 16 |
| n=7 5906 champion | 18 | 832 | 0 for 698, 1 for 134 |
| n=7 5913 exact cover | 120 | 720 | **1** for all |

**Out-degree is never more than 1.** A free join has `w ≤ 3`, and `w ≤ 2`
between distinct components would merge them, so it is a weight-3 jump; of the
≤ 9 weight-≤3 targets of an arc end, at most one is another component's entry.
At an exact cover every arc is full, so `l + l′ = 2n ≥ 2n−3` forces the om exit
(§3.2) and the graph is exactly a permutation — with cycles of length
`ord(s) = n−2`, which *is* the "om-chains cap at n−2" already on record.

So free continuation is **forced**, and every walk decomposes into maximal free
chains joined by costly jumps. The chainer enumerates chain partitions by
increasing `p`, orders each by branch and bound, and stops the moment it hits
the floor `Y = p − 1`. Two prunes carry it: every inter-chain join costs ≥ 1
(a chain's free successor lands in a component it already covers), and with
`budget` chains left for `left` components no chain may be shorter than
`left − (budget−1)·longest`.

| seed | comps | old gen2 | exact chainer |
|---|---|---|---|
| n=6 houston 872 | 4 | Y=0, 0.04 s | Y=0, **0.0005 s** |
| n=7 5906 champion | 18 | **Y=5**, 50 s | **Y=0**, 0.003 s |
| n=6 exact cover | 24 | Y=9, 1.1 s | **Y=6**, 3.3 s |

Two things worth separating. At the n = 6 exact cover it finds the true `Y = 6`
where the four earlier attempts got 19 / 11 / 15 / 9 — that gap is closed. And
at the n = 7 champion the old chainer was not merely slow but **wrong**: it
scored a known optimum at `Y = 5`, i.e. 5 characters worse than it is. Any
search steered by that was being lied to.

A greedy cover seeds the incumbent before the exact search starts, so the
chainer always returns a valid chaining; `solve.exact` reports whether the
search finished. That matters because the fallback it replaces costs 50 s.

### What it unblocked, and what that showed

`aline.py` could not complete a single step at n = 7 (one merge exceeded 900 s).
It now runs — with a two-tier budget, a small node cap to rank the ~240 merge
candidates and an exact re-price for the winner. **The result is negative**, and
cleanly so:

| step | A | S | B | Y | T |
|---|---|---|---|---|---|
| — | 8 | 124 | 18 | 0 | **142** |
| 1 | 9 | 123 | 19 | 1 | 143 |
| 2 | 10 | 122 | 20 | 2 | 144 |
| 5 | 13 | 119 | 23 | 7 | 149 |

Every step lands exactly on the champion line in `(A, S, B)` — `B = 10 + A`,
`S = 132 − A` — and then pays in `Y`. The first merge prices at `Y = 1`, **exact
and proven optimal** at two node budgets, so this is not a chaining failure: the
arc set the stitch produces cannot be chained free. An `A = 9` champion with
`Y = 0, T = 142` does exist, so it uses a different arc set.

**The stitch is not T-neutral at n = 7.** The A-line of 237 champions is real,
but this local move does not traverse it — walking it needs a move that repairs
the chaining as well as the arc set. That is a sharper statement of the open
problem than "the chainer is too slow", and it is the kind of thing only an
exact inner solver could establish.

---

## 7. The proxy the cold start was annealing against was wrong

§5 blamed the cold-start failure on "no gradient": the fast objective
`S + comps + ⌈comps/(n−2)⌉ − 1` scored the exact cover at `0 + 24 + 5 = 29`,
the true optimum, so there was nothing to descend. That diagnosis was too
generous. **The bound is not admissible**, and the gradient pointed the wrong
way:

```
Y >= ceil(comps/(n-2)) - 1   fails on 1273 of 44672 rows  (n=6: 1024, n=7: 247, n=5: 2)
worst: 5912-derived   comps=120  Y=3   claimed >= 23
n=7 record:           comps=18   Y=0   claimed >= 3
```

The cap `n−2` is `ord(s)`, and it only binds where the weight-3 exit is **forced
onto om** (`l + l′ ≥ 2n−3`, §3.2). Champions have partial arcs, nothing is
forced, and their chains run long — the n = 7 champion's 18 δ-components form a
**single** chain. So the proxy priced the n = 7 record at `T = 145` against a
true 142 while pricing the exact cover at 29 against a true 30: the exact cover
was made to look **4 better** than it is relative to the champion. Registered as
`CHLB` **[REF]**.

**The replacement, `CH2` [THM].** Every chaining decomposes into maximal free
chains, and each join *between* chains costs ≥ 1 (a maximal chain's free
successors all land on components it already covers, so none is another chain's
head). With `p` the fewest free chains covering the components,

> `Y ≥ p − 1`,  hence  `T ≥ S + comps + p − 1` — valid against the optimum via `SIG2X`.

It returns 0 at the n = 7 champion (true 0) and 5 at the n = 6 exact cover
(true 6), in 1–4 ms. It does **not** beat HPV — champions have `p = 1`, so it
collapses to `T ≥ v`, exactly as `A3` says it must. Its value is as a search
bound, and as a characterisation:

> **`Y = 0` ⟺ `p = 1` ⟺ the δ-components thread into a single weight-3 chain.**

That is a design criterion rather than a bound, and with `A1u` it specifies what
a record search should look for: an arc set with `B+Y−A ≥ (n−2)s` whose
components form one free chain.

**`CH1` is false**, not merely corpus-narrow — see [`pbound.md`](pbound.md)
§10a. Free out-degree exceeds 1 on the census itself (19 states reach 2 at
n = 6; 38 reach 2 and 11 reach 3 at n = 7), and the annealer reaches **3**.
The correct length-gated statement is `FORCE`: at most one *core* out-edge. The chainer now branches instead of following a
function; the argument is unaffected, since it needs only chain *maximality*.
This is the third time in this repo a regularity true on all 44,564 corpus
strings has failed off-distribution — cf. [`notes/ordering.md`](ordering.md) §4.

## 8. The three-tier objective, and what it settles

`CH2` is admissible but not cheap: `min_chains` runs out of nodes at the
~100-component states a random start passes through, costing 110 ms and
degrading to a crude floor. So the sweep uses a third bound.

**`cheap_bound` — O(states).** A component none of whose break-points has a
free successor must **end** its chain; one no free edge can reach must **start**
one. Hence `p ≥ max(dead_out, dead_in)` and `Y ≥ that − 1`. It skips `runs`
entirely, which is where all the cost lives.

Neither bound dominates, so `lower_bound` takes the max:

| state | comps | true `Y` | `cheap_bound` | `CH2` |
|---|---|---|---|---|
| n=6 exact cover | 24 | 6 | 0 (0.8 ms) | **5** (1.5 ms) |
| n=6 houston 872 | 4 | 0 | 0 | 0 |
| n=7 5906 champion | 18 | 0 | 0 (2.8 ms) | 0 (3.9 ms) |
| n=6 random colouring | 102 | — | **47** (0.4 ms) | 16 (110 ms) |

So: **tier 1** `cheap_bound` for the annealing sweep, **tier 2** `lower_bound`,
**tier 3** the exact chainer for anything worth keeping. `search` anneals on
tier 1 and re-prices on tier 3 whenever the incumbent moves — the two cannot be
the same function, since a lower bound will happily like a `chi` that prices
badly. The reported best is now honest: `best T` equals `realised T`.

**Results at n = 6, 15 iterations/s:**

| seed | before | now |
|---|---|---|
| champion | reproduced exactly, T = 29 | unchanged |
| random split-free colouring | `mcolour`: T ≈ 158, length 985 | **T = 57, length 900** (20,000 its, valid) |
| monochromatic family (exact cover) | T = 30 | **T = 30 — zero improvements in 6,000 iterations** |

**So the mispricing was real but not the whole story.** With `CHLB` the search
was steered *toward* the exact cover by 4; that is fixed, and the exact cover
now prices honestly at 30 against the champion's 29. A gradient exists. The
annealer still cannot follow it: from the exact cover it never improves once.

The reason is the **move set**, and §9 makes it exact.

---

## 9. Why one class is never enough — and the graft

**`FAM1`.** `delta(end of arc)` stays in the arc's family **iff the arc is
full**. Forward half is a theorem: a full arc ends at `σ^{n−1}(g)` and `δ` of
that is `g·a` with `a ∈ H = ⟨a,b⟩`, so it stays in the coset. The converse is
measured over all 720 permutations at n = 6 and all partial lengths — length `n`
gives family shift 0 every time, lengths 1…n−1 give shifts spread uniformly over
1…n−1 (144 each) and **never** 0. This is a sharper form of §3.4.

That settles the barrier. The exact cover is one whole family with every arc
full, so all its δ-exits stay in-family and already land on arc starts — which
is why its 24 components are 24 disjoint cycles (`S1`). Add **one** cut
anywhere: the piece before it becomes partial, `FAM1` sends its exit out of the
family, and no other family's loops are entered, so the exit lands on nothing.
Measured over all 600 single cut additions:

```
delta(comps) = 0 in 600 of 600;  exits land in families 1..5, 120 each
```

> **No single-class move can reduce `comps` at the exact cover.** It is not a
> local optimum the annealer merely fails to escape — it has no downhill and no
> flat neighbour in the whole move class.

Champions are family-mixed by contrast: houston 872 spreads its arc starts
50 / 35 / 10 / 5 / 20 / 25 over all six families.

**The graft** ([`code/graft.py`](../code/graft.py)) is therefore the minimal
move that can work: **two** cuts in two different families, coordinated so the
first one's new dirty exit lands exactly on the arc start the second creates.
600 are available at the exact cover.

It does what it was designed to do — and that is not enough:

| step | S | comps | Y | T |
|---|---|---|---|---|
| — | 0 | 24 | 6 | **30** |
| 4 | 8 | 19 | 6 | 33 |
| 8 | 16 | 14 | 7 | 37 |
| 12 | 24 | 7 | 13 | 44 |
| *champion* | *25* | *4* | *0* | *29* |

`comps` falls 24 → 7 exactly as intended, and `S` arrives almost exactly where
the champion has it (24 against 25). **`Y` is the whole problem**: it goes to 13
where the champion has 0.

One trap worth recording, because the first attempt fell into it: scoring grafts
by `S + comps` walks the *wrong way*. The champion has the **higher** `S + comps`
of the two (29 against the exact cover's 24) and wins entirely on `Y`, so any
key that ignores `Y` heads back toward the exact cover. Scoring by
`S + comps + lower_bound` fixes the direction but not the outcome.

### The exchange rate, and why the move set is too rigid

The graft costs **two splits per δ-edge**. Champions cannot afford that: houston
872 buys 20 components' worth of merging with only 25 splits — **1.25** splits
per edge. So the graft is the wrong currency, and the arithmetic says so:
20 grafts would land at `S = 40, comps = 4`, i.e. `S + comps = 44` against the
champion's 29.

The cheap move exists in principle. Call it a **landing**: if a *partial* arc's
exit `δ(end)` is not yet an arc start, cutting there creates the edge for **one**
split. The exact cover has no partial arcs at all, which is exactly why it needs
a graft to bootstrap — but every state after that should have landings.

It does, and only just. Measured after one graft:

```
4 partial arcs:  3 have exits that are already arc starts,  1 FREE landing
landings offered at each of the first three steps:  0, 1, 1
```

The reason is that a cut splits one full arc into two pieces and **both inherit
used exits**: the first piece's exit is the graft target (just consumed), and
the second piece's exit is the original full arc's in-family exit, which was
already an arc start. Only the *target* class's split leaves one new dirty exit
free. So each graft manufactures exactly one landing, and the search never
accumulates cheap moves.

Greedy descent with both moves, exact-priced over a shortlist, still climbs:

```
start  T=30           0 land /  600 graft
step 1 T=31  S=2  comps=23     took graft
step 2 T=31  S=4  comps=21     took graft
step 3 T=33  S=6  comps=20     took graft
```

**So the diagnosis has sharpened four times and is now specific:** not "the
chainer is too slow" (fixed, §6), not "the proxy is wrong" (fixed, §7–8), not
"single-class moves can't merge components" (`FAM1`, fixed by the graft) — but
**the move set has the wrong exchange rate**. Merging components two-splits-at-a-
time overshoots `S` long before `comps` comes down, and the one-split move that
would fix it is starved: each graft creates exactly one.

### The prune, and the wall showing up inside the move set

The `S`-neutral direction turns out to settle the question, via the move that
goes the *other* way. Removing the cut at `P` merges the arc ending just before
`P` with the arc starting at `P`, so `R` falls by one. At most two edges die
with it: `P`'s in-edge, and the out-edge of the arc that ended just before it.
Since `Δcomps = ΔR − Δe`:

| edges lost | `Δ comps` | `Δ S` | `Δ(S + comps)` |
|---|---|---|---|
| 0 | −1 | −1 | **−2** |
| 1 | 0 | −1 | **−1** |
| 2 | +1 | −1 | **0** |

**Every cut removal is non-increasing in `S + comps`.** That is `A3` reappearing
at the level of the move set: `S + comps` is minimised by the exact cover, so
*any* local rule that descends it walks back there. It also explains every
failure above at once — the graft, the landing and the greedy key were all
fighting a potential whose minimum is in the wrong place.

The zero-loss case (`Δ = −2`) is a strict improvement, so an optimum can have
none. `graft.py` asserts exactly that, and it holds: houston 872 offers **0**
prunes. That is the consistency check the move set needed.

### The reformulation

Champions do not beat the exact cover on `S + comps` — they lose it, 29 to 24.
They win **only** on `Y`, and `CH2` says `Y = 0 ⟺ p = 1`: the δ-components
thread into a single weight-3 chain. 43,295 of the 44,121 n = 6 optima have
`Y = 0`.

So the search should not minimise `T` over all arc sets. It should

> **restrict to the `Y = 0` manifold — arc sets whose components form one free
> chain — and minimise `S + comps` inside it.**

Inside that manifold `S + comps = T`, so the objective and the wall finally
point the same way, and the exact cover (which has `Y = 6`, `p = 6`) is simply
not a member. `chainer.min_chains` supplies the membership test.

But before building that search it was worth asking whether the manifold is
even *connected* under local moves — and the answer changes the whole picture.

---

## 10. The move unit is a LOOP, not a cut

Three measurements over the 43,096 n = 6 optima.

**They are all distinct arc sets.** 43,096 strings, 43,096 distinct arc-start
sets. Nothing is a re-ordering of anything else.

**No two differ by a single relocation.** Hashing every "arc set minus one cut"
and unioning collisions gives

```
connected components: 43096      largest: 1 of 43096
```

so the optima form 43,096 isolated points at move-radius 1. Any local search
over cut structures is dead on arrival at n = 6.

**Distances are quantised by `n − 1`.** Over a 497-sample of the `S = 25`
optima, **100 %** of pairwise relocation distances are multiples of 5, minimum
**15**. Counted in *loops entered* instead of cuts, the minimum is **3**.

The reason is immediate from the ledger. `A = (n−1)v − R = Σ_L (n−1−a_L)`, so
`A = 0` forces every entered loop to be **saturated** — all `n−1` of its
generators are arc starts. An `A = 0` arc-start set is therefore an *exact union
of whole 2-loops*. Measured: **409 of 409** sampled optima are exactly that.

> **So the move unit is a loop.** Optima differ by whole 2-loops swapped in and
> out, `n−1` arc starts at a time, and the nearest two are 3 loop-swaps apart.
> Every move class in §9 — graft, landing, prune — operates on single cuts, a
> granularity at which the optima are not merely far apart but *disconnected*.

That also collapses the search space. Instead of cut structures — `n` choices
per class over `(n−1)!` classes — the right space is **sets of 2-loops covering
every rotation class**: choose 29 loops from 144 at n = 6. That space is already
implemented, in [`code/saturated6.py`](../code/saturated6.py)
(`saturated(n, v, cls_of)`), which is what enumerated the 10,068 exact covers,
and in [`code/a1.py`](../code/a1.py) for the deficiency-1 case.

**Caveat, stated precisely.** `A = 0` is not universal: `872-nonstandard` has
`A = 2…5` and is *not* a union of whole loops. The clean statement is that
`A = 0` **forces** the union-of-loops structure, and every optimum in the
43,096-string treelike corpus has `A ≡ 0 (mod n−1)` — its `R` spectrum is
`{135, 140, 145}`, i.e. `S ∈ {15, 20, 25}`, all multiples of `n−1`. A loop-level
search would therefore reach the `A = 0` optima and would need extending to
catch the rest.

---

## 11. Loop space — built, gated, and the landscape is a golf course

[`code/loopsearch.py`](../code/loopsearch.py) searches sets of 2-loops. The
state is a covering loop system; the arc set is a *function* of it, and

    R = (n-1)v   exactly, so   S = (n-1)v - (n-1)! = (n-1)d

so **`S` is no longer a search variable** — it is fixed by `v`. The objective
collapses to `T = (n−1)d + comps + Y`: a loop system is judged only on how few
δ-components it has and how cheaply they chain. At n = 6 the space is 144 loops,
120 classes, every class met by exactly 6 loops.

**The gate passes.** Houston 872's loop system prices at `T = 29`
(`S=25 comps=4 Y=0`) and re-emits a valid 872; the exact cover prices at
`T = 30`. So the space represents both known points exactly.

**But it cannot be annealed.** Per move at n = 6, and what each reads at the
exact cover against the champion's 29:

| price | cost / move | at exact cover |
|---|---|---|
| `cheap_bound` | 1 ms | **24** — makes the exact cover look 5 *better* |
| `lower_bound` (`CH2`) | 225 ms | **29** — ties |
| exact | 2.3 s | **30** — separates, by 1 |

`cheap_bound` is actively wrong here: with `Y` invisible the objective is just
`S + comps`, which `A3` says the exact cover minimises. `CH2` is honest but
flat. Only the exact price separates the two, by **one unit out of thirty**, at
2.3 s a move.

Runs from the exact cover: 8,000 iterations on `cheap_bound` and 5,000 on `CH2`
both finish at `T = 30, v = 24` — they never leave.

> **So the failure has moved off the move set entirely.** The geometry is now
> right (loops), the space is right (`S` eliminated), the price is right
> (`chainer` is exact). What is left is that the objective is **flat to within
> the resolution of every affordable bound**, and the true gap between the exact
> cover and a champion is 1 in 30. There is nothing for a local search to
> descend.

**That closes local search as an approach at n = 6.** The obvious alternative is
filtered enumeration, and it is worth writing down why that is closed too.

## 12. Filtered enumeration — costed, and not feasible

For a loop system `A = 0`, so `R = (n−1)v` and `S = (n−1)d`. Requiring
`T = S + comps + Y ≤ 29` with `comps ≥ 1` and `Y ≥ 0` pins the whole search:

| v | d | S | `comps` must be ≤ | |
|---|---|---|---|---|
| 24 | 0 | 0 | 29 | **excluded**: `S1` forces `comps ≥ F = 24`… but `S = 0` makes every loop all-full, so `F = 24` and `Y > 0` |
| 25 | 1 | 5 | 24 | |
| 26 | 2 | 10 | 19 | |
| 27 | 3 | 15 | 14 | |
| 28 | 4 | 20 | 9 | |
| 29 | 5 | 25 | **4** | the champion sits here |
| ≥30 | ≥6 | ≥30 | ≤ −1 | **impossible** |

A clean, finite case split — and then the counting kills it:

```
v=24  S=0   10,068 systems   1.2 s   (exhaustive, matches the known count)
v=25  S=5   >400,000         353 s   (hit the cap, not exhaustive)
```

At least a 40× blow-up per unit of `v`, so `v = 29` is of order `10¹²`
systems. Enumerate-then-filter is out by many orders of magnitude.

And the filter cannot be pushed into the DFS, which is what would rescue it:
`comps` is a property of the δ-graph on the *whole* arc set, not a per-loop
quantity, so there is nothing to prune on until a system is complete. The one
decomposable necessary condition available is `S1` (`F ≤ comps`), which at
v = 29 says at most 4 of the 29 loops may be all-full — real, but nowhere near
enough to cut `10¹²` down.

> **So both halves are closed at n = 6.** Local search has no gradient at any
> affordable resolution (§11); enumeration has no tractable filter (§12). What
> remains is the classical approach the records were actually found by —
> *connectivity-first* construction, growing a δ-connected arc set rather than
> enumerating covers and testing connectivity afterwards. That is Houston's
> search, and beating it is not a laptop-scale target.

The honest summary of the constructor program: it now **measures** correctly
(census, `build`, `chainer` exact at any `comps`), it **represents** correctly
(loop space, with `S` eliminated), it **prices** correctly (`CH2`, `SIG2X`), and
it reproduces every known optimum it is seeded with. It does not find new ones,
and §§11–12 say why in terms that are quantitative rather than anecdotal.
