# superperm — a research notebook on shortest superpermutations

> My own working notebook on the shortest-superpermutation problem. What I do
> here is narrow and I want to be plain about it: I look for **clean lemmas
> and structural patterns**, prove them, verify them exhaustively against
> every known extremal string, and build **independent** re-derivations of
> results the field already holds. Currently at $n = 6$ (done) and $n = 7$
> (open).

**[Notebook front page](https://levkropp.github.io/superperm/)** ·
**[The absorption lemma](https://levkropp.github.io/superperm/absorption-lemma)** ·
**[Lay explanation](LAYPERSON.md)** · **[The s(6) ≥ 868 certificate](CERTIFICATE_868.md)** ·
**[Verify it yourself](#verify-it-yourself)**

A *superpermutation* on n symbols is a string containing every permutation of
the symbols as a contiguous substring; s(n) is the minimal length. Known
exactly: s(1..5) = 1, 3, 9, 33, 153.

| n | lower bound | upper bound | status |
|---|---|---|---|
| 6 | 872 (preliminary, vlad-ds) | 872 (Houston 2014) | **probably done** |
| 7 | 5888 (Hunter & Raudvere, Lean) | 5906 (Egan/Houston 2019) | the open frontier |
| 8 | 46103 (Hunter & Raudvere, Lean) | 46204 | wide open |

## Status of the problem (July–August 2026) — read first

Parts of this repo were written when I believed s(6) ≥ 868 was new. Days
earlier, three stronger results had already landed publicly:

- **s(6) ≥ 869, s(7) ≥ 5888, s(8) ≥ 46103** — Hunter & Raudvere, Lean-4
  machine-checked, completing Zach Hunter's 2019 draft:
  [urdvr/superpermutations-hunter](https://github.com/urdvr/superpermutations-hunter)
- **s(6) ≥ 868, s(7) ≥ 5886** (all n ≥ 5) — Raudvere, Lean-4 machine-checked:
  [urdvr/superperm-coeff2](https://github.com/urdvr/superperm-coeff2)
- **s(6) = 872 exactly** — vlad-ds, computer-assisted, Python + certificate
  ledger (preliminary, audits invited):
  [vlad-ds/a6-872](https://github.com/vlad-ds/a6-872)

So my 868 is **not** a new bound. It is an independent proof, by an unrelated
method, of one the field got three other ways in the same week. In
computer-assisted mathematics that is still worth something — a bound three
unrelated methods reach is a bound you can build on — but headline claims
elsewhere in these files ("first improvement since 2011/2018") should be read
with the date above in mind.

---

## Part 1 — the absorption lemma, and s(6) ≥ 868

In the permutation overlap graph (720 vertices; edge weight = symbols to
append), minimal length = 6 + min Hamiltonian path weight. The
Houston–Pantone–Vatter invariant gives wt ≥ p + c + v − 2 (permutations,
completed 1-cycles, entered 2-loops). Two ingredients close the gap:

1. **Absorption lemma** — every 2-loop has exactly 5 generators, and jump
   targets enter a loop only by landing on one, so `v ≥ ⌈(R−1)/5⌉` (tight on
   both known extremal strings, which is how you know it's the right
   invariant).
2. **Rigidity of v = 24** — 24 entered 30-vertex loops covering 720 vertices
   must be an *exact cover*; each 1-cycle then has a unique "port"
   (generator), forcing R = 120 full arcs and `wt = 600 + TSP(cover)` over
   the 120 classes. All **10,068** exact covers (29 S₆-orbits) have class-TSP
   **≥ 265** (CP-SAT certified).

So: v ≥ 25 ⇒ wt ≥ 837 + 25 = **862**, and v = 24 ⇒ wt ≥ 600 + 265 = **865**.
Every complete walk has wt ≥ 862, hence **s(6) = 6 + wt ≥ 868**. ∎

The same scheme **retro-proves s(4) = 33 and s(5) = 153** exactly — the
strongest soundness check available.

## Part 2 — the Split Identity (all n)

The absorption lemma turned out to be the `A ≥ 0` corollary of an exact
bookkeeping identity. Let R = arcs, v = entered 2-loops, and A = *accidents*
(generators of entered loops covered mid-arc rather than entered cleanly):

> **R = (n−1)v − A**, equivalently splits = (n−1)(v − (n−2)!) − A.

Proven by pure bookkeeping, and exact on all five known extremal strings at
n = 6 and n = 7. Details: [`notes/split_identity.md`](notes/split_identity.md).

## Part 3 — n = 7, stated correctly

Write `length = 5764 + v + slack`, where v is the number of entered 2-loops.
Covering forces **v ≥ 120** (the entered loops must cover all 720 rotation
classes, six each), and a string of length L has **v ≤ L − 5764**. So proving
s(7) ≥ 5906 means discharging a **ladder of 22 rungs**, v = 120..141, showing
rung v has slack ≥ 142 − v. That is the same 22-level obligation vlad-ds's
`a7` bundle indexes by δ = length − 5884.

> **Erratum.** Earlier versions of this README and of
> [`docs/5905-question.md`](docs/5905-question.md) ran that inequality the
> wrong way — claiming a 5905-string "needs v ≥ 141" — and posed a
> "knife-edge question": can 141 two-loops cover all 720 one-cycles? Both
> were wrong. The bound is v ≤ 141, and the covering question is trivially
> yes: **120 disjoint loops already suffice**, with an explicit exact cover
> built in [`code/audit_n7.py`](code/audit_n7.py). The advertised dichotomy
> ("No ⟹ s(7) ≥ 5906") was a non sequitur. The 22-rung ladder above is the
> honest statement.

### New result: the Pentad Lemma clears rung v = 120 by eleven

Rung v = 120 is the tight one — HPV is exactly tight there — and it is the
direct analogue of the n = 6 rigidity argument behind s(6) ≥ 868.

At v = 120 the 120 entered loops carry exactly 720 generator slots for 720
classes, so the cover is **exact**. The Split Identity R = 6v − A with R ≥ 720
then forces **A = 0, R = 720**: every class is one full 7-permutation arc, and
`length = 5765 + X` with X the total jump excess over weight 2. The naive
floor is X ≥ 119, i.e. 5884 — HPV on the nose — and it is *not* killed
locally: every run end really does have five weight-3 exits.

It is killed globally. Relabelling symbols commutes with everything and S₇
acts simply transitively on the 5040 permutations, so every equivariant map is
right multiplication by a fixed element. With a = c⁶d ("next generator") and
b = (3,4,5,6,2,1,7) (the unique weight-3 move into a class-disjoint loop):

> **Pentad Lemma.** At most **five** complete 2-loop traversals can be chained
> by weight-3 jumps — a complete traversal entered at g exits at g·a⁵, the
> next is entered at g·a⁵b, and **ord(a⁵b) = 5**.

Sharp: those five loops are pairwise class-disjoint. With f the number of
loops traversed in one piece, counting visits gives
X ≥ max(f + ⌈f/5⌉ − 2, 239 − f) ≥ **130**, hence

> **every 7-symbol superpermutation with v = 120 has length ≥ 5895.**

`code/rigidity7.py` rebuilds the structure from the definitions and asserts
every step on all 5040 permutations. Write-up:
[`notes/pentad_lemma.md`](notes/pentad_lemma.md).

**This is one rung, not a bound on s(7).** A string of length L has
v ≤ L − 5764, so a complementary elementary proof of s(7) ≥ 5889 also needs
slack ≥ 4, 3, 2, 1 at v = 121..124 (v ≥ 125 is automatic). The Pentad Lemma is
cover-independent and applies there verbatim; what is missing is a strong
enough lower bound on the number of complete traversals.

For the **split-free** slice those remaining rungs are now discharged — see
the next section, which replaces the ladder entirely with a v-free argument.

### New result: the SBY identity, and split-free s(7) ≥ 5889

The rung ladder is awkward because v does two jobs at once. There is a
rewriting in which it disappears. Let S = splits (arcs − (n−1)!), B = blocks
(maximal runs of arcs joined by weight-2 jumps), Y = Σ(weight − 3) over the
B − 1 costly jumps. Then, by bookkeeping,

> **length = n + n! + (n−1)! − 3 + S + B + Y**,

and that base is exactly HPV − (n−2)!. So **HPV ⟺ S + B + Y ≥ (n−2)!**; at
n = 7, proving s(7) ≥ 5884 + k *is* proving S + B + Y ≥ 120 + k. The two n = 6
champions bracket the trade: classical 873 pays 0 + 24 + 6, Houston 872 pays
25 + 4 + 0 — 25 splits buy it down to **four blocks**.

**Split-free** walks (S = 0) are the rigid slice: every class is one full arc,
the only weight-2 move is δ, δ lands on the next generator of the *same*
2-loop, so a block is confined to one loop and has length ≤ 6. Computing the
**cap** of each weight-3 exit of a length-l block gives a table with the same
shape at every n, and two rows carry everything:

> **Exit trichotomy.** Of the six weight-3 exits of a complete traversal,
> three are dead, two cap the next block at 4, and one is om — the unique
> class-disjoint move, b = (3,4,5,6,2,1,7).
> **Length-5 row.** Two dead, one capping at 4, two at 5, one unique cap-6
> exit — *the same b*.

So a weight-3 jump between blocks of length ≥ 5 is forced to be om. With the
Pentad Lemma that gives three linear counting constraints; minimising B + Y
over them is a finite search returning **B + Y ≥ 124** at n = 7, and — the
soundness check that matters — exactly **153** at n = 5, where a split-free
champion exists.

Counting leaves exactly one state at 124: 100 complete traversals, 24 blocks
of length 5, nothing shorter, Y = 0. Every transition in it is forced to be
om, so the walk must read 25 om-chains separated by 24 isolated fives, and a
chain of k traversals followed by a five advances the chain start by
Q_k = s^k·u with s = a⁵b (ord 5) and u = a⁴b (ord 2). The chain-length vector
is forced to be 25×4 or 23×4 + 3 + 5, and **ord(Q₄) = 6** — six chains and the
walk re-enters a loop it has burned. All 25 admissible vectors fail. Hence

> **every split-free 7-symbol superpermutation has length ≥ 5889** —
> one better than Hunter–Raudvere on that slice, elementary and
> cover-independent.

### The SBY ladder: a four-line s(6) ≥ 868, and s(7) ≥ 5885

Write β_n for the split-free floor on B + Y just proved: **β₅ = 7, β₆ = 26,
β₇ = 125**. Four inputs — three standard, one new — then close n = 6 with *no
case analysis*:

- **HPV** — T := S + B + Y ≥ v (cited);
- **COVER** — v ≥ (n−2)!, since the entered loops cover all (n−1)! classes;
- **SPLIT** — R = (n−1)v − A, A ≥ 0, i.e. S = (n−1)(v − (n−2)!) − A;
- **BLOCK** — split-free ⟹ B + Y ≥ β_n.

SPLIT is the hinge: at v = (n−2)! it gives S = −A ≤ 0, so **A = S = 0** and the
walk is *split-free* — exactly where BLOCK bites. Above that rung HPV takes
over. Hence **T ≥ min(β_n, (n−2)!+1)**:

| n | β_n | (n−2)!+1 | T ≥ | length ≥ | HPV alone |
|---|---|---|---|---|---|
| 5 | 7 | 7 | 7 | **153** (exact) | 152 |
| 6 | 26 | 25 | 25 | **868** | 867 |
| 7 | 125 | 121 | 121 | **5885** | 5884 |

The n = 5 row is exact, so the chain has no slack to hide an error in. 868 is
not a new bound — but the *route* is: four lines of bookkeeping and one finite
search, where [`CERTIFICATE_868.md`](CERTIFICATE_868.md) needs the absorption
lemma, the rigidity of v = 24, all 10,068 exact covers and 29 CP-SAT class-TSP
runs. The two proofs share nothing but HPV.

**Exactly what is left.** A target T ≥ (n−2)!+k is free at v = (n−2)! and free
at v ≥ (n−2)!+k. What survives is the band (n−2)! < v < (n−2)!+k with
1 ≤ S ≤ (n−1)k−1:

- **s(6) ≥ 869** needs the single case **v = 25, 1 ≤ S ≤ 5** — and the
  split-free sub-case there (S = 0) is already cleared, so the rung that
  bottlenecks *both* proofs of 868 is now partially discharged;
- **s(7) ≥ 5889** needs **v = 121..124, 1 ≤ S ≤ 24**.

Same band, same obstruction, both n.

**Why the local route can't get in.** Generalising the block-count lemma to
allow *dirty* cheap jumps (δ out of a partial arc) comes out **below** HPV
everywhere in the band. [`code/dirty_exits.py`](code/dirty_exits.py) says why:
where a weight-3 exit of a complete traversal has caps `0 0 0 4 4 6` — nearly
all dead ends — a dirty cheap exit has caps `4 6 6 6 6 dead`. The free loop
switch is real and almost unobstructed. The one fact it yields is that a
partial arc covering exactly n−1 of its class, at the end of a run of length
≥ 2, has **no cheap exit at all**. That is one bit, and it is not enough:
getting into the band needs a global argument about how splits sit in the
cover — the analogue, one rung up, of the v = 24 rigidity behind s(6) ≥ 868.

**None of this bounds s(7) at the frontier.** The champions are nowhere near
split-free (Egan/Houston 5906 has S = 124, ~18 blocks). Write-up:
[`notes/block_count_lemma.md`](notes/block_count_lemma.md).

### New result: the per-loop refinement, and s(7) >= 5886 down to one state

Complete traversals are *loops*, not free parameters. Every arc start is a
generator of exactly one 2-loop, loop L holds a_L <= n-1 of them, and a clean
run occupies **consecutive** generators of one loop — so L's arc starts
partition into r_L >= 1 runs summing to a_L, and

> N = sum r_L,  R = sum a_L,  A = (n-1)v - R, and
> **f := #runs of length n-1 = #{L : a_L = n-1 and r_L = 1}**.

Every clause is asserted on 604 real walks by `code/dirty.py`. Putting it back
into the counting lemma ([`code/loop_runs.py`](code/loop_runs.py)) does two
things:

- it **raises the split-free floor** — beta_6 from 26 to 27, and at n = 7,
  v = 120 the counting alone gives **T >= 131, i.e. length >= 5895**, which is
  exactly the rung the Pentad Lemma reaches by a completely different route;
- at n = 7, **v = 121 it returns 121** — up from 117, and now *equal* to HPV.
  The counting reproduces HPV at the one rung that binds, without citing it.

s(7) >= 5886 needs T >= 122 everywhere, and every rung except v = 121 already
clears it. Breaking v = 121 out by A (with S = 6 - A) gives
T >= 121, 122, 123, 125, 126, 128, 129 for A = 0..6 — so **only A = 0 survives,
short by exactly one**, and its state is completely pinned: all 121 loops
saturated, 115 traversed complete, 6 broken into two runs each, N = 127,
12 dirty jumps, B = 115, Y = 0.

Transition counting gets close but not there. Every costly T-to-T transition
is forced to be om, and om-chains cap at ord(a^5 b) = 5, so at least 15 of the
25 chains are **full** (five traversals). A full chain visits g, gs, ..., gs^4
-- a complete **<s>-orbit** of generators.

### New result: validated on all 140 known n = 7 superpermutations

The n = 7 work could previously only be gated on algebra and n <= 6 walks. The
140 public 7-symbol strings ([superpermutators/superperm](https://github.com/superpermutators/superperm),
sample in `data/n7/`) now run through the whole apparatus, and **every
identity and lemma holds on all of them**
([`code/n7_champions.py`](code/n7_champions.py)). Three readings:

- **HPV is exactly tight on the record strings** — all 136 strings of length
  5906 have v = 142 and T = 142. Nothing to win at the top of the ladder; the
  whole problem is at low v, where a 5888-string must sit (v <= 124).
- **Split-free 7-symbol superpermutations exist but are long**: the two with
  S = 0, v = 120 are the 5912 and 5913 strings. We prove >= 5895 at v = 120,
  so the gap on that slice is 17.
- **No known string has v in 121..124** — the band the ladder needs is empty
  of examples in either direction.

### New result: the collision budget

[`code/pentad_orbits.py`](code/pentad_orbits.py) confirms the sharpness half
of the Pentad Lemma **on all 1008 <s>-orbits** — the five loops of an orbit
are always pairwise class-disjoint, so a full chain consumes exactly 30 of the
720 classes. Corollary: **24 disjoint orbits exactly partition all 720
classes** (24 x 30 = 720), which is the v = 120 exact cover seen through the
om structure. Since only 15 full chains are needed, cover rigidity *alone*
does not kill v = 121.

What does bite is the **collision budget**. At v = 121, A = 0 every loop is
saturated, so 121 loops carry 726 class-slots over 720 classes: exactly six
classes are covered twice, and those six are the S = 6 splits. A full chain
cannot end on om (om targets its own starting generator, already spent), so it
ends on a cap-4 exit, a dirty jump, or the walk end -- and each cap-4 exit
lands in a loop *sharing* classes with the departing one, spending budget.
That drops the bound from 25 to `c5 <= 6 + d_T + 1`, and

> 115 <= 4C + c5 <= 4(13 + d_TT) + 6 + d_T + 1 <= 59 + 5*12 = **119**.

Still >= 115, so the state survives -- but the slack is down from **10 to 4**.
Four more units kill it and give s(7) >= 5886.

**And one route is now closed.** At v = 121 HPV and the refined lemma both
return 121, and the lemma's extremal state has T = 121 = v, so a single
hypothetical state saturates *both* bounds. Re-deriving HPV in order to add
the two together cannot gain anything at the binding rung; any gain must come
from killing that state directly.

### New result: the Coset Lemma

A weight-3 jump between two runs of length >= n-2 is forced to be om, and a
run of length l followed by om advances the next start by `a^(l-1) b`. So an
**om-stretch** -- a maximal stretch of consecutive long runs joined by
weight-3 jumps -- is confined to one right coset of `H := <s, u>`, where
`s = a^5 b` (ord 5) and `u = a^4 b` (ord 2). The computation
([`code/coset_lemma.py`](code/coset_lemma.py)):

> **|H| = 720 = 5040/7** -- an index-7 subgroup, not all of S_7.

And it has exactly the right shape: H contains a, so it is a union of 120
complete 2-loops; its order is coprime to 7 = |<c>|, and rotation classes are
the left cosets of <c>, so H meets **every one of the 720 classes exactly
once** -- as does each of the 7 right cosets.

> **Coset Lemma.** The 840 two-loops partition into **7 families of 120**, and
> *each family is an exact cover of the 720 rotation classes*. An om-stretch
> lives inside one family, so its runs are automatically class-disjoint and it
> enters at most **(n-2)! = 120** two-loops.

**When is a jump forced onto om?** `coset_lemma.py` now *derives* this from
the exit table rather than asserting it: a weight-3 jump from a length-l run
to a length-l' run has a unique admissible exit -- hence om -- exactly when
`l + l' >= 2n-3`, i.e. (6,6), (6,5), (5,6) at n = 7. **Not (5,5)**: the l = 5
row is `[0,0,4,5,5,6]`, so two exits have cap 5 and a length-5 run may follow
a length-5 run without om.

> ⚠️ **Correction.** An earlier version of this section claimed any jump
> between two runs of length >= n-2 is om, and derived
> `v <= 120(1 + 2m + Y)`, localising the split-free minimum to v = 124, 125.
> Both are withdrawn. The correct rule is
> `#om-stretches <= 1 + Y + #(adjacent pairs with l+l' <= 2n-4)`, which is too
> weak in aggregate counting to bite at v >= 124, so the split-free ladder
> reverts to its earlier values.


### New result: the Chain-Count Lemma

Take a split-free walk in which **every block is a complete traversal**. Then
the blocks *are* the loops, so B = f = (n-2)! and they exactly cover the
classes. Every transition joins two runs of length n-1, and l+l' = 2n-2 >=
2n-3, so a weight-3 transition here is **forced onto om**. With h = the number
of weight->=4 transitions, #chains = 1 + h; and a chain of k traversals sits at
g, g.s, ..., g.s^(k-1), so k <= ord(s) = n-2. Hence f <= (n-2)(1+h), so
h >= (n-3)! - 1, and Y >= h:

> **Chain-Count Lemma.** A split-free walk all of whose blocks are complete
> traversals has `Y >= (n-3)! - 1`, hence
> **length >= n! + (n-1)! + (n-2)! + (n-3)! + n - 4.**

| n | ord(s) | f = (n-2)! | Y >= | length >= | s(n) | classical |
|---|---|---|---|---|---|---|
| 4 | 2 | 2 | 0 | **33** | 33 | 33 |
| 5 | 3 | 6 | 1 | **153** | 153 | 153 |
| 6 | 4 | 24 | 5 | **872** | 872 | 873 |
| 7 | 5 | 120 | 23 | **5907** | ? | 5913 |

The closed form is **exactly s(n) for n = 4, 5, 6** -- sharp wherever s(n) is
known -- and at n = 7 gives **5907, one more than the conjectured 5906**. So
conditional on s(7) = 5906, **no 7-symbol champion is split-free with all
blocks complete traversals** -- the first proved instance of the "champions
must have splits" hypothesis. ([`code/chain_count.py`](code/chain_count.py))

At n = 6 the bound lands on 872 exactly, so that case needed one more unit --
and it closes. Y = 5 forces six om-chains of exactly 4 traversals, i.e. the 24
loops are six full `<s>`-orbits exactly covering the 120 classes; all 180
`<s>`-orbits do have their 4 loops pairwise class-disjoint (20 classes each,
6 x 20 = 120), and **8640 such exact covers exist**. But Y = 5 also forces all
five connecting jumps to weight exactly 4, and

> **0 of the 8640 covers can be linked into a path by five weight-4 jumps.**

So Y >= 6, T = 30, and **no n = 6 champion is split-free with all blocks
complete traversals** (split-free with B = 24 forces length >= 873 > 872).
That closes the exact-cover case, which the repo's own s(6) certificate reaches
only as far as E >= 27.

### New result: B = 24 closed a second time, independently

A split-free 872 has `E = B - 1 + Y = 28`, HPV gives `v <= B + Y = 29`, and
covering forces `v >= 24`.  Note **v = 24 and B = 24 are the same case**: with
24 loops and 120 classes every loop is full, so every block is a complete
traversal, and conversely `B = sum r_L >= v >= 24`.  So what follows is a
*second, independent* proof of the case above -- one that uses no om theory, no
Coset Lemma and no chain count, and settles every Y at once instead of Y = 5.

An exact cover fixes everything but the order. There are 144 two-loops at
n = 6, each of size 30, each permutation in 6 of them, and each loop has
exactly **5 generators, one per class**. So assigning a class to a cover loop
determines its arc's starting permutation: all 120 full arcs are pinned, and
every (B, Y) compatible with v = 24 collapses into a single **minimum-weight
Hamiltonian path over 120 fixed nodes**, with `E = TSP - 238`.

Up to relabelling there are 29 such covers. 28 were already certified OPTIMAL
at >= 267. The lone holdout, **orbit 28**, sat at FEASIBLE 267 / certified 265
-- so its optimum was 266 or 267, and 266 is exactly length 872.

> **No Hamiltonian path of weight 266 exists over orbit 28's 120 arcs.**
> Exhaustive branch-and-bound, all 120 start nodes, 2.399e10 nodes.
> ([`code/orbit28b.c`](code/orbit28b.c), CP-SAT model in
> [`code/orbit28.py`](code/orbit28.py))

So all 29 orbits are OPTIMAL >= 267: **B = 24 forces E >= 29 and length >= 873
> 872**, with no appeal to the chain count.

Guards, because two over-pruning bugs were caught this way earlier in the
project: the search *finds* the known 267 solution in 120 nodes; the instance
is validated on its own terms (the 120 arcs tile all 720 permutations exactly
once, and delta out of the arc ends closes into 24 five-cycles); and a second
implementation carrying only the naive capacity bound agrees at every budget it
can reach -- exhaustively IMPOSSIBLE at E <= 23, 24, 25, 26, 27, the last at
4.72e10 nodes, and E <= 26 independently reproducing CP-SAT's certified 265.
CP-SAT itself does not scale here: `AddCircuit` over 121 nodes never closes the
gap, so the branch-and-bound is primary.

Remaining for a full n = 6 result: **B = 25..29**, where loops overlap, arc
starts are no longer pinned, and the problem is not a fixed 120-node TSP.

### The case list, and two routes that do NOT reach it

[`code/profiles6.py`](code/profiles6.py) enumerates the run-length profiles
(c_1..c_5, Y) with sum i*c_i = 120 and B + Y = 29.  **377 survive; exactly one
has B = 24**, the case just closed.  376 remain, over c_5 = 4..23.

Counting cannot trim them.  The chain count generalises to
`c_5 <= (n-2)(1 + Y + (B - c_5))`, because a chain of complete traversals is
broken by ANY non-complete block -- the om step out of a length-l block is
`a^(l-1)b`, a different group element for each l, so a length-(n-2) block
interrupts the s-orbit even though the (n-1, n-2) transition is itself forced
om.  At n = 6 with B + Y = 29 that says c_5 <= 24, which `5c_5 <= 120` already
gives: **the chain count is vacuous away from B = 24**, and the counting alone
yields only B + Y >= 25.

Brute force, on the other hand, **is** in reach -- after a 550x correction.
[`code/splitfree6b.c`](code/splitfree6b.c) adds the analogue of the arc bound
to the full 720-node search (a length-5 run is an entire loop, so it needs one
of the 144 loops still wholly uncovered).  That bound is worth nothing in
practice, and splitting the search by (B, Y) is worth nothing in aggregate
either -- measured at E <= 26 the four cases total 1.329e9 nodes against
1.325e9 unsplit, though it does show the work concentrates at large B / small
Y.

What was decisive is mundane: the target loop scanned all 720 candidates per
node, since `cost + w - 2` alone never exceeds the budget while cost is small
and ~600 targets have weight 6.  Hoisting a target-independent floor on the
post-move block bound out of the loop cuts the scan to a couple of dozen.  Node
counts are **byte-identical**; only the constant changes.  **E <= 25 went from
134 s to 0.24 s.**

So the growth is ~114x per unit (1.3e9 at E <= 26, ~1.5e11 at E <= 27) and the
decisive run **E <= 28 is ~4e12 nodes, about 13 hours on 20 cores** -- now
running.  Two traps worth recording: shard *depth* matters far more than shard
count (every shard re-explores the tree above the cut, so depth 12 wastes ~1e10
nodes per shard, more than the whole E <= 26 tree); and using `U - 6` instead
of `U` in the hoisted bound inverts it, since `lo_blocks_u` is decreasing in u
-- the E <= 29 gate caught that immediately.

### The family reformulation

[`code/families6.py`](code/families6.py) turns the Coset Lemma into a change of
variables.  Since `a` in H and the arc-to-arc delta step is exactly right
multiplication by `a`, a 2-loop is a coset of `<a>` and the 144 loops fall into
**6 families of 24, each an exact cover of the 120 classes** -- so each class
has exactly one arc start per family.  Hence

> a split-free walk IS an n-colouring of the (n-1)! classes (colour of C =
> which family supplies C), plus an ordering,

and v and B are read off the colouring alone.  The monochromatic colouring
gives B = 24; the best of 2000 random colourings gives B = 86.  So `B <= 29` is
a severe rigidity condition on the colouring, which is where the remaining
leverage most likely sits.

### Settled: no n = 6 champion is split-free

`length = 844 + E` for a split-free walk and `s(6) = 872 = 844 + 28`.  An
exhaustive search found **no split-free walk with E <= 28**, so

> **split-free => length >= 873.**  The classical 873 IS split-free, so this is
> exact: the shortest split-free 6-superpermutation is **873**, and **every 872
> champion has splits**.

2203 leaf verdicts, **2.98e13 nodes**, zero FEASIBLE, zero cap hits.
Certificate: [`data/e28_certificate.txt`](data/e28_certificate.txt).

Two things make the result trustworthy rather than merely large.  Every
refinement of the search was verified **exact by node accounting before use**
(work below the cut computed both ways: 1784777 at depth 8, 370586159 at depth
16, 70566880 at depth 24), and all three binaries involved still **FIND** the
known E = 29 walk while returning identical node counts -- the extra cut levels
changed parallel decomposition only, never pruning.

A trap worth recording: modular sharding at a *fixed* depth can never split the
leftmost all-delta spine, because `0 % N == 0` keeps node 0 whole in piece 0 at
every modulus.  Shard 0's region alone took 5.13e12 nodes, a quarter of the
other 1998 combined, and it had to be cut *deeper* (depths 16 then 24), not
finer.

### The lemma arsenal

Everything the repo can use as an ingredient, in one place, with an explicit
status on each item -- identity / proved / exhaustive / external / conjecture /
measured-only / dead end / retracted -- plus the exact rung-by-rung deficit for
each target bound:
**[`notes/lemma_arsenal.md`](notes/lemma_arsenal.md)**.

Two things it makes obvious.  Our own unconditional elementary bound (5885) is
**below** the published Lean-checked 5888, so this machinery is a complementary
independent route, not the state of the art.  And matching 5888 is **three**
rungs, not one: v = 121, 122, 123 short by 3, 2, 1.  Chasing +1 at v = 121
alone reaches 5886 and stops -- the right unit of work is a lemma lifting a
whole band of rungs.

### New conjecture: Family Quantisation

The B = 24 walks are exactly the exact covers, and a cover need not sit in one
family -- at n = 6 the 10068 covers spread over 1 to 6 families.  But not
freely:

> **Family Quantisation.**  In every exact cover of the (n-1)! rotation classes
> by (n-2)! two-loops, the number of loops taken from each family is divisible
> by **n - 2** -- equivalently each family supplies a multiple of (n-1)(n-2)
> classes.

[`code/quantise.py`](code/quantise.py) enumerates *all* exact covers and checks
it exhaustively:

| n | loops | families | covers | family splits |
|---|---|---|---|---|
| 4 | 8   | 4 x 2  | 4     | (2) |
| 5 | 30  | 5 x 6  | 25    | (3,3) x20, (6) x5 |
| 6 | 144 | 6 x 24 | 10068 | (12,8,4) x2880, (8,8,4,4) x1800, (12,4,4,4) x1680, (16,4,4) x1080, (8,8,8) x1080, (8,4,4,4,4) x540, (16,8) x450, (12,12) x300, (20,4) x180, (4,4,4,4,4,4) x72, (24) x6 |

Every entry is a multiple of n-2.  Independently: the distinct *sets* of
family-f loops occurring across all covers number 1612 at n = 6, with sizes
exactly 4, 8, 12, 16, 20, 24, and at n = 5 exactly 3 and 6.

`n-2` is exactly `ord(s)` for the Pentad element `s = a^(n-2)b`, which is why
this looks like the right invariant.  It is **not** simply "covers are unions
of `<s>`-orbits": `<s>` does not act on loops (a loop's n-1 generators lie in
different `<s>`-orbits), and the 66 minimal 4-element restricted sets at n = 6
overlap rather than partitioning a family's 24 loops.  Mechanism open; the fact
is exhaustive at n = 4, 5, 6.

It does not by itself close B >= 25, since that needs partial loops -- a
partial-loop version is the natural next target.

### New result: the om-stretch primitive rho(c), exactly

The Coset Lemma turns "what can one om-stretch do?" into a finite question.
Inside a stretch all generators lie in one right coset of H = <a,b>, and that
coset meets each class exactly once; split-free uses each class at most once.
So **a stretch is exactly a simple path in the right Cayley graph
Cay(H; {a,b})** on (n-1)! vertices, out-degree 2: `g -> g.a` continues the
current run (free), `g -> g.b` starts a new one (costs a run). Runs cap at
n-1 for free, since ord(a) = n-1. Define

> **rho(c) = the fewest runs over simple paths covering c vertices.**

Two things make it tractable: left multiplication by H preserves the edges, so
the graph is **vertex-transitive** and paths may start at the identity; and the
a-edges cut the coset into (n-2)! loops, so unvisited vertices form maximal
a-arcs, each needing its own run -- giving
`remaining runs >= sum(#unvisited arcs) - 1`, far stronger than
`ceil(remaining/(n-1))`. Iterative deepening then makes each failed level a
proof:

| n | vertices (n-1)! | loops (n-2)! | **rho((n-1)!)** | nodes |
|---|---|---|---|---|
| 5 | 24 | 6 | **8** | 180 |
| 6 | 120 | 24 | **31** | 21 M |

Both exact. A bespoke C branch-and-bound ([`code/omstretch.c`](code/omstretch.c))
does the search; an independent Python re-implementation
([`code/omstretch.py`](code/omstretch.py)) sharing no code with it reproduces
both.

**What it says about the trade-off.** At n = 6 a split-free walk that is a
*single* om-stretch costs rho(120) = 31 runs, so T = 31 -- but the classical
873 is split-free with N = 24, Y = 6, T = 30. It is *cheaper* to pay Y and
break into several stretches than to stay inside one coset. So leaving the
coset family is something an optimal split-free walk actively **wants** to do,
and Y is the price. That is why the single-stretch bound alone will not reach
5907: a real ladder has to price the stretch count against rho of the pieces.

**The published bound is unaffected.** The group theory and the collision
arithmetic never used the forcing claim, and the split_free_5889.py argument
is intact -- its counting *independently forces* the 24 length-5 runs to be
isolated, so no (5,5) occurs there. That state really is a single om-stretch
and the Coset Lemma kills it (v <= 120 < 124) more cleanly than the period map
does. So split-free ==> length >= **5889**, exactly as before.

It also produces exact collision arithmetic. Since each family is an exact
cover, a loop *outside* a family collides with a full family in **exactly 6
class-slots** -- and 6 is precisely the collision budget of the v = 121,
A = 0 blocking state. Writing t for the loops of the majority family left
unused, that state needs 121 = (120-t) + (t+1) loops, and t = 1, 2, 3 all
force >= 8, >= 9, >= 8 collisions -- **dead**. Only `t = 0` (one full coset
family plus a single foreign loop, spending exactly 6) and `t >= 4` survive.
Killing those is now the concrete target.

### New result: exact macro-chain capacities past the published table

The strongest current attack on n = 7 (the `a7` bundle, conditional
s(7) ≥ 5896) bottlenecks on one computable object: **M₇(G)**, the longest
chain of "macros" that fits in a gap budget G. Their exact table stops at
M₇(21) = 41; above that everything uses a conservative partition-closure
relaxation W(g), and surviving cases are measured against it.

I rebuilt that system from its specification, sharing no code with the
bundle, and it reproduces their work exactly — all of M₇(0..21), **all eleven
unpruned node counts** (31 … 10,465,987), the full W(g) table including the
decisive W(66) = 130, and the `cap` field on **1261 of 1261** hard summaries
of their δ = 12 frontier.

Then I changed the algorithm — *bootstrap pruning*: at each budget, prune
with the partition closure of only those entries already proven at smaller
budgets. Nothing is circular, and it is far cheaper. That buys nineteen new
exact values:

> **M₇(22..40) = 43, 44, 46, 47, 50, 51, 52, 54, 56, 57, 59, 60, 63, 64, 66,
> 66, 68, 69, 71**

each with a witness chain validated by an independent checker
([`code/verify_witness.py`](code/verify_witness.py)). Together they drop
W(66) from **130 to 119**.

**And the negative result that goes with it — which turned out to be the
useful half.** Re-running their δ = 12 frontier under sharpened capacity takes
332 surviving rows to 253, then stops dead: a *hypothetical* exact M₇
extrapolated to g = 95 at any growth rate down to 1.0/unit, pushing W(66) as
low as 97, moves it 253 → 252. That's a wall, not an asymptote, and the reason
is explicit — each case is measured against a max-plus convolution over c
chains, and since W(0) = M₇(0) = 5,

> **F_c(G) ≈ λG + 5c.**  Extending the table lowers λ. It cannot touch the
> 5c floor, because M₇(0) = 5 is already exact.

So *capacity-immune = floor-dominated*. What attacks the floor is the bundle's
own **full-endpoint tax**, which replaces 5 by 4 on the K pre-hard chains. I
reimplemented its DP (reproduces their published δ = 11 values 4/4) and
measured both levers together:

| | no tax | tax where already forced | tax everywhere (ceiling) |
|---|---|---|---|
| published table (g=21) | 332 | 298 | 184 |
| **this work (g=40)** | 253 | 222 | **78** |

Strongly **complementary, not additive**: 332 → 253 alone, 332 → 184 alone,
332 → **78** together. Tightening capacity is what makes the fullness
hypothesis forceable; the tax is what converts it into kills on rows capacity
can never reach. 78 residual cases is the same order as the 14 branches
finished by hand at δ = 11. Forcing fullness at δ = 12 is the live problem.

Write-up: [`notes/m7_capacity.md`](notes/m7_capacity.md).

## Verify it yourself

Everything needed is in this repo — total download < 1 MB of data. No
gigabyte checkpoints: the s(6) certificate is the 10,068-cover list (80 KB
compressed), 29 orbit representatives, and exact-solver runs that take
minutes on a laptop.

```bash
pip install -r requirements.txt          # numpy, scipy, ortools

# n = 6, fast checks (seconds)
python code/certify.py --string data/houston_872.txt --n 6   # 872 is valid
python code/verify_v1_absorption.py      # absorption lemma (+ 200 random walks)

# n = 6, moderate (a few minutes)
python code/verify_v2_covers.py          # re-enumerate all 10,068 covers
python code/verify_family_orbit.py       # class-TSP on the family orbit

# n = 6, the full certificate (~30 min, 15 threads)
python code/verify_orbits_tsp.py         # all 29 orbits certify TSP >= 265

# n = 7
python code/rigidity7.py                 # Pentad Lemma + the v = 120 rung (>= 5895)
python code/rigidity7_algebra.py         # supporting group data
python code/audit_n7.py                  # loop structure + explicit 120-loop cover
python code/blockcount.py                # the three identities, measured on 604 walks
python code/exit_table.py                # exit caps by block length, all 5040 entries
python code/exit_table_n.py              # same at n = 5,6,7 (n = 5 reproduces 153)
python code/split_free_5889.py           # split-free s(7) >= 5889
python code/sby_ladder.py                # the SBY ladder: s(6)>=868, s(7)>=5885
python code/dirty.py                     # dirty-jump census (dirty <= S is false)
python code/dirty_exits.py               # exit table for partial arcs
python code/loop_runs.py                 # per-loop refinement; the v=121 state
python code/pentad_orbits.py             # Pentad sharpness on all 1008 orbits
python code/coset_lemma.py               # the Coset Lemma: 7 families of 120 loops
gcc -O3 -march=native -DNSYM=6 -o code/omstretch code/omstretch.c
./code/omstretch                         # rho(120) = 31, exact
python code/omstretch.py                 # independent cross-check of rho
python code/chain_count.py               # Chain-Count Lemma; n=6 Y=5 structure
python code/n7_champions.py              # all lemmas vs 140 real n=7 strings
python code/vladder.py                   # both identities, re-measured from raw strings
gcc -O3 -march=native -o code/macro7 code/macro7.c
./code/macro7 21 --nodes                 # reproduce the a7 table AND its node counts
./code/macro7 40 --nodes                 # extend it (writes witness.txt)
python code/verify_witness.py witness.txt
python code/capacity_dp.py               # W(g), 13/13 published values
python code/frontier12.py                # delta=12 frontier (needs a6-872 cloned)
python code/tax12.py                     # endpoint-tax DP + the two-lever table
```

CI runs the fast+moderate n = 6 checks on every push (see
[Actions](../../actions)).

## Repository map

- `CERTIFICATE_868.md` — the s(6) proof with every link in the chain.
- `LAYPERSON.md` — the result explained without prerequisites.
- `REPORT.md`, `VALIDATION.md` — the research log: machinery, findings, dead
  ends (including why every LP relaxation caps at 840, and why the outer
  automorphism of S₆ cannot help).
- `notes/` — the structural findings.
  [`split_identity.md`](notes/split_identity.md) (the theorem),
  [`pentad_lemma.md`](notes/pentad_lemma.md) (the n = 7 rung-120 proof),
  [`block_count_lemma.md`](notes/block_count_lemma.md) (the SBY identity and
  split-free s(7) ≥ 5889),
  [`m7_capacity.md`](notes/m7_capacity.md) (the n = 7 capacity work),
  [`s7_baseline.md`](notes/s7_baseline.md) (decompositions of the three n = 7
  champions), [`a_cost_law.md`](notes/a_cost_law.md),
  [`sig2_vs_accidents.md`](notes/sig2_vs_accidents.md).
  ⚠️ [`cross_read_872lean.md`](notes/cross_read_872lean.md) is **unreliable**
  — its description of the vlad-ds method is wrong; see the warning at the
  top of that file.
- `code/` — verification scripts plus the toolset: the overlap graph model
  (`permgraph.py`), exact ATSP (`cpsat_tsp.py`, `exact_tsp.py`), the CPU
  arc-prover (`prove_par.c`), the GPU BFS prover (`gpu_bfs.py`) that
  certifies s(5) = 153 with 41M nodes, and the n = 7 machinery
  (`rigidity7.py`, `rigidity7_algebra.py`, `rigidity7_group.py`,
  `audit_n7.py`, `vladder.py`, `blockcount.py`, `exit_table.py`,
  `exit_table_n.py`, `after_traversal.py`, `rung_split_free.py`, `loop_runs.py`,
  `rung124.py`, `split_free_5889.py`, `sby_ladder.py`, `dirty.py`,
  `pentad_orbits.py`, `n7_champions.py`, `coset_lemma.py`,
  `omstretch.c`, `omstretch.py`, `chain_count.py`, `splitfree6.c`,
  `dirty_exits.py`, `macro7.py`, `macro7.c`,
  `verify_witness.py`, `capacity_dp.py`, `frontier12.py`, `tax12.py`).
- `data/` — Houston's 872 string, the cover list, orbit reps, the TSP results
  table, the 2018 HPV lower-bound paper (PDF), and `n7/` (a sample of the
  public 7-symbol strings; the full set of 140 is at
  [superpermutators/superperm](https://github.com/superpermutators/superperm)).

## References

- Anonymous 4chan poster, R. Houston, J. Pantone, V. Vatter, *A lower bound
  on the length of the shortest superpattern*, OEIS A180632 (2018).
- R. Houston, *Tackling the minimal superpermutation problem*,
  arXiv:1408.5108 (2014).
- M. Engen, V. Vatter, *Containing all permutations*, Amer. Math. Monthly 128
  (2021).
- G. Egan, *Superpermutations* (gregegan.net) — constructions and the n = 7
  records.
