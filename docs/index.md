---
layout: math
title: "Superpermutation notebook — lemmas, patterns, independent proofs"
---

# Superpermutation notebook
### *lemmas, patterns, and independent proofs at $n = 6$ and $n = 7$*

This is my working research notebook on the shortest-superpermutation
problem. If you don't know it: it's the question that was born on 4chan's
/sci/ board in 2011 — what's the shortest string that contains every
possible ordering of $n$ episodes as a contiguous binge-watch? People call
them superpermutations; $s(n)$ is the answer.

<iframe width="100%" height="400" src="https://www.youtube.com/embed/wJGE4aEWc28" frameborder="0" allowfullscreen></iframe>

*A video explains it a lot better.*

What I'm actually doing here is narrow and I want to be plain about it: I
look for **clean lemmas and structural patterns**, I prove them, I verify
them exhaustively against every known extremal string, and I build
**independent** re-derivations of results the field already holds. In
computer-assisted mathematics that second thing is worth real money —
a bound that three unrelated methods reach is a bound you can build on.

## What's here

**The absorption lemma** ($n = 6$). Every 2-loop has exactly five doors in,
so a walk with $R$ segments must enter at least $\lceil (R-1)/5 \rceil$ of
them. Both champion constructions hit it *exactly*, which is how you know
it's the right invariant. With a rigidity argument and an exhaustive check
of all 10,068 covers it gives $s(6) \ge 868$ — independently of the three
machine-checked proofs that landed the same week.
[The full writeup](absorption-lemma) is the one page I'd genuinely
recommend reading.

**The Split Identity** (all $n$). The absorption lemma turned out to be the
$A \ge 0$ corollary of an exact bookkeeping identity,
$R = (n-1)v - A$, where $A$ counts *accidents* — generators covered mid-arc
instead of entered cleanly. It is exact on all five champion strings at
$n = 6$ and $n = 7$.
[Details](notes/split_identity).

**The Pentad Lemma** ($n = 7$). At most *five* complete 2-loop
traversals can be chained by weight-3 jumps, because the map that advances
the entry point, $a^5 b \in S_7$, has order 5. It is sharp and it is
cover-independent. It is the seed of the now-settled exact-cover rung:
**$v = 120 \Rightarrow$ length $\ge 5908$** at $n = 7$, with the same
settlement at $n = 6$ (873) and $n = 8$ (46205) — that rung is excluded
for champions at all three. See below.

**The CH3 bound and `A2`** (all $n$). The first ordering-free lower bound
here to beat HPV: $T \ge S + \mathrm{comps} + p - 1$, worth 29 against
HPV's 24 over all 10,068 exact covers at $n = 6$ — and 29 is the true
optimum. Its load-bearing step $\mathrm{comps} \ge v - S$ (`A2`) was a
conjecture for most of this notebook's life and is now **proved**, via the
cycle rank of the loop quotient. With it, $s(7) = 5906$ is *exactly* the
question "is $v + p \ge 143$?"
[Details](notes/pbound).

**The SBY identity and the block-count lemma** (new). An exact rewriting,
$\mathrm{length} = n + n! + (n-1)! - 3 + S + B + Y$, under which the HPV bound
becomes simply $S + B + Y \ge (n-2)!$. Three linear counting constraints plus
one order-6 group element give **length $\ge 5889$ for every split-free
7-symbol superpermutation**. Fed back through the split identity it also
yields a **four-line $s(6) \ge 868$** with no cover enumeration at all, and
$s(7) \ge 5885$; it reproduces $s(5) = 153$ exactly, and it pins the remaining
obligation down to one rung at $n = 6$ and four at $n = 7$. See below.

**The macro-chain capacity table** ($n = 7$). Nineteen new exact values of
$M_7$, and a diagnosis of why capacity alone plateaus.

**Two retractions**, recorded rather than quietly deleted: [the 5905
question](5905-question) (I posed a dichotomy whose both halves were wrong)
and, in the repo's claim registry, a wrong description of vlad-ds's method
as a Lean proof it isn't. If a page here is unreliable it says so at the
top.

## Where things actually stand

| $n$ | lower bound | upper bound | status |
|---|---|---|---|
| 6 | 872 (preliminary, vlad-ds) | 872 (Houston 2014) | **probably done** |
| 7 | 5888 (Hunter & Raudvere, Lean) | 5906 (Egan/Houston 2019) | the open frontier |
| 8 | 46103 (Hunter & Raudvere, Lean) | 46204 | wide open |

A wave of AI-assisted work hit this problem in July 2026 — Raudvere's
Lean-4 [coeff2](https://github.com/urdvr/superperm-coeff2) (July 17),
Hunter & Raudvere's Lean-4
[completion](https://github.com/urdvr/superpermutations-hunter) of the 2019
draft (July 28), and vlad-ds's computer-assisted
[a6-872](https://github.com/vlad-ds/a6-872) (July 29). My 868 is not a new
bound; it's an independent proof of one the field got days earlier by three
other methods. I'd rather say that plainly than dress it up.

## The $n = 7$ frontier, stated correctly

Write $\mathrm{length} = 5764 + v$ + slack, where $v$ is the number of
entered 2-loops. HPV forces $v \ge 120$ (the entered loops have to cover all
720 rotation classes, six each), and a string of length $L$ has
$v \le L - 5764$. So proving $s(7) \ge 5906$ means discharging a **ladder of
22 rungs**, $v = 120, \dots, 141$, showing rung $v$ has slack $\ge 142 - v$.
That is the same 22-level obligation that vlad-ds's `a7` bundle indexes by
$\delta = \mathrm{length} - 5884$.

*(An earlier version of this page ran that inequality the wrong way and
claimed a 5905-string needs $v \ge 141$, and that the whole question reduced
to whether 141 two-loops can cover the 720 classes. Both were wrong: the
bound is $v \le 141$, and 120 disjoint loops already cover everything —
`code/pentad_orbits.py` exhibits 24 pairwise class-disjoint $\langle s
\rangle$-orbits partitioning all 720 classes. The honest statement is
the 22-rung ladder above.)*

## The elementary route: the Pentad Lemma at the tightest rung

*This was the first clearance of the $v = 120$ rung, at 5895 — since
superseded by the exact 5908 settlement in the next section. It stays
because the Pentad Lemma itself is load-bearing throughout the notebook.*

Rung $v = 120$ is the hard one — it is where HPV is exactly tight, and it is
the direct analogue of the $n = 6$ rigidity argument behind $s(6) \ge 868$.

At $v = 120$ the 120 entered loops carry exactly $6 \times 120 = 720$
generator slots for 720 rotation classes, so the cover is **exact**. The
Split Identity $R = 6v - A$ plus $R \ge 720$ then forces $A = 0$ and
$R = 720$: every class is one full seven-permutation arc, and

$$\mathrm{length} = 5765 + X, \qquad X = \sum_{\text{jumps}}(\text{weight}-2).$$

The naive floor here is $X \ge 119$, i.e. 5884 — HPV on the nose. And it is
not killed locally: from every run end there really are five weight-3 exits.
It is killed *globally*.

Relabelling the seven symbols commutes with everything, and $S_7$ acts simply
transitively on the 5040 permutations, so every equivariant map is right
multiplication by a fixed group element. Writing $a = c^6 d$ for "next
generator of the loop" and $b = (3,4,5,6,2,1,7)$ for the unique weight-3 move
into a class-disjoint loop:

> **Pentad Lemma.** At most five complete 2-loop traversals can be chained by
> weight-3 jumps — because a complete traversal entered at $g$ exits at
> $g a^5$, the next is entered at $g a^5 b$, and $\mathrm{ord}(a^5 b) = 5$.

Five is attained (those five loops are pairwise class-disjoint), so the lemma
is sharp. Feeding it into the visit count, with $f$ the number of loops
traversed in one piece,

$$X \ \ge\ \max\Bigl(f + \bigl\lceil \tfrac f5 \bigr\rceil - 2,\ 239 - f\Bigr)
\ \ge\ 130 ,$$

giving **length $\ge 5895$ at $v = 120$**. Keeping every loop whole costs 142
because the lemma forces 23 expensive jumps; breaking loops up dodges that
but pays a visit each time; the adversary's optimum is to break about ten and
it still costs 130.

Everything is checked by `code/rigidity7.py`, which rebuilds the structure
from the definitions and asserts each step on all 5040 permutations.
[Full writeup](notes/pentad_lemma).

**What this is not.** It is one rung. A string of length $L$ has
$v \le L - 5764$, so a complementary elementary proof of $s(7) \ge 5889$ also
needs slack $\ge 4, 3, 2, 1$ at $v = 121, \dots, 124$ ($v \ge 125$ is
automatic). The Pentad Lemma applies there verbatim — it never mentions $v$ —
but the bound on the number of complete traversals is currently too weak, and
that is the open piece.

## Settled: the exact-cover rung is excluded at $n = 6, 7, 8$

The 5895 above left the rung short of the champion. The settlement came from
re-posing the equality case as **one feasibility model**. At $v = (n-2)!$
the cover is exact, every class a single full arc, and the one-below target
is exactly the statement "$(n-3)!$ pairwise class-disjoint Pentads linked by
weight-4 jumps". CP-SAT over all orbit-chain assignments at once:

| $n$ | states | weight-4 edges | time | verdict | bound |
|---|---|---|---|---|---|
| 6 | 233 | 2,540 | 0 s | INFEASIBLE | **873** |
| 7 | 3,431 | 61,874 | 22 s | INFEASIBLE | **5908** |
| 8 | 35,989 | 770,536 | 66 s | INFEASIBLE | **46205** |

against best-known $s(n) = 872, 5906, 46204$ — **the exact-cover rung is
excluded for champions at $n = 6, 7$ and $8$** (`code/egan1p.py`; the $n=6,7$
models re-run in seconds on a laptop).

The certificate now has a combinatorial reason as well: **PENTCAP** —
weight-4-linked sequences of pairwise class-disjoint Pentads cap at exactly
$n - 3$ (exhaustively: 3, 4, 5 at $n = 6, 7, 8$), against the $(n-3)!$ the
rung needs. Rung 0 does not fail by a hair; it fails factorially
(`code/pentcap.py`).

And the whole ladder turns out to be one lemma. **RUNGEQ**: at *every*
rung, sitting one below the ladder's need forces the rung-0 shape — every
component traversed whole, all chain links of weight exactly 4, average
chain length exactly $n-2$. So a single statement — *a free chain of
components, joined at weight 3, covers at most $n-2$ components* — closes
every rung at once, giving $s(n) = \mathrm{Egan}(n)$ for $n \ge 9$ and
$s(8) = 46204$ exactly. The core-only case of that lemma is proved
(CORECAP, exhaustive at $n = 5, 6, 7$); the fringe case is the open piece,
and it is now the whole problem.
[Details](notes/pbound).

## New result: split-free strings, and what HPV really says

The rung ladder above is awkward because $v$ is doing two jobs at once. There
is a rewriting in which it disappears. Let $S$ be the number of **splits**
(arcs minus $(n-1)!$; a rotation class covered by $j$ arcs contributes
$j - 1$), let $B$ be the number of **blocks** — maximal runs of arcs joined by
weight-2 jumps — and let $Y = \sum(\text{weight} - 3)$ over the $B - 1$ costly
jumps. Then pure bookkeeping gives

$$\mathrm{length} \;=\; n + n! + (n-1)! - 3 \;+\; S + B + Y ,$$

and the base of that is *exactly* $\mathrm{HPV} - (n-2)!$. So

> **HPV $\iff$ $S + B + Y \ge (n-2)!$.**

At $n = 7$: HPV is the statement $S + B + Y \ge 120$, and proving
$s(7) \ge 5884 + k$ is proving $S + B + Y \ge 120 + k$. Nothing else. The two
$n = 6$ champions sit at the two extremes of that trade — the classical 873
pays $0 + 24 + 6$, all in blocks, while Houston's 872 pays $25 + 4 + 0$,
buying its way down to **four blocks** by spending 25 splits. That trade is
the entire difficulty.

**Split-free walks** are the slice where $S = 0$, so every class is one full
seven-permutation arc. There the structure is completely rigid: the only
weight-2 move out of a full arc is $\delta$, which lands on the *next
generator of the same 2-loop*, so a block occupies consecutive generators of
one loop and has length at most 6.

Compute, for a block of length $l$, the **cap** of each of its six weight-3
exits — how far the next block can run before re-entering a class this one
just burned. The table has the same shape at every $n$, and two rows carry
the argument:

> **Exit trichotomy.** Of the six weight-3 exits of a *complete traversal*,
> three are dead on arrival, two cap the next block at length 4, and one is
> om — the unique class-disjoint move, right multiplication by
> $b = (3,4,5,6,2,1,7)$.
>
> **Length-5 row.** Two dead, one capping at 4, two at 5, and again a
> *unique* cap-6 exit — **the same $b$**.

So any weight-3 jump between two blocks of length $\ge 5$ is forced to be om.
With the Pentad Lemma ($\mathrm{ord}(a^5b) = 5$) that yields three linear
counting constraints, and minimising $B + Y$ over them is a finite search. It
returns **$B + Y \ge 124$** at $n = 7$ — and, as a soundness check with no
slack to hide in, it returns exactly **153** at $n = 5$, where a split-free
champion exists.

The counting leaves precisely *one* state at $B + Y = 124$: 100 complete
traversals, 24 blocks of length 5, nothing shorter, $Y = 0$. That state is
rigid enough to kill by hand. Every transition in it is forced to be om, so
the walk must read 25 om-chains of traversals separated by 24 isolated
length-5 blocks, and a chain of $k$ traversals followed by a five advances the
chain's starting point by right multiplication by $Q_k = s^k u$, where
$s = a^5 b$ has order 5 and $u = a^4 b$ has order 2. The chain-length vector
is forced to be $25 \times 4$ or $23 \times 4 + 3 + 5$, and

$$\mathrm{ord}(Q_4) = 6 .$$

Six chains and the walk is back on a 2-loop it has already burned. All 25
admissible vectors fail. Hence $B + Y \ge 125$ and

> **every split-free 7-symbol superpermutation has length $\ge 5889$.**

### The ladder that falls out: $s(6) \ge 868$ in four lines

Write $\beta_n$ for that split-free floor on $B + Y$: $\beta_5 = 7$,
$\beta_6 = 26$, $\beta_7 = 125$. Four inputs — three standard, one new — close
$n = 6$ with **no case analysis at all**:

- **HPV** — $T := S+B+Y \ge v$ (cited);
- **COVER** — $v \ge (n-2)!$, since the entered loops cover all $(n-1)!$ classes;
- **SPLIT** — $R = (n-1)v - A$ with $A \ge 0$, i.e. $S = (n-1)(v - (n-2)!) - A$;
- **BLOCK** — split-free $\Rightarrow B + Y \ge \beta_n$.

SPLIT is the hinge. At the bottom rung $v = (n-2)!$ it gives $S = -A \le 0$,
so $A = S = 0$ and the walk is *split-free* — precisely where BLOCK bites.
Above that rung HPV takes over. Hence $T \ge \min(\beta_n, (n-2)!+1)$:

| $n$ | $\beta_n$ | $(n-2)!+1$ | $T \ge$ | length $\ge$ | HPV alone |
|---|---|---|---|---|---|
| 5 | 7 | 7 | 7 | **153** (exact) | 152 |
| 6 | 26 | 25 | 25 | **868** | 867 |
| 7 | 125 | 121 | 121 | **5885** | 5884 |

The $n = 5$ row is exact, so the chain has nowhere to hide an error. 868 is
not a new bound — but the *route* is: four lines of bookkeeping plus one
finite search, where [the certificate](certificate) needs the absorption
lemma, the rigidity of $v = 24$, all 10,068 exact covers and 29 CP-SAT
class-TSP runs. The two proofs share nothing but HPV. And $s(7) \ge 5885$ is
one better than HPV, three short of the certified 5888.

**Exactly what is left.** A target $T \ge (n-2)!+k$ is free at the bottom rung
and free at $v \ge (n-2)!+k$. What survives is the band
$(n-2)! < v < (n-2)!+k$ with $1 \le S \le (n-1)k-1$:

- $s(6) \ge 869$ needs the *single* case $v = 25$, $1 \le S \le 5$ — and the
  split-free sub-case there is already cleared, so the rung that bottlenecks
  **both** proofs of 868 is now partially discharged;
- $s(7) \ge 5889$ needs $v = 121..124$, $1 \le S \le 24$.

Same band, same obstruction, at both $n$.

**And why the local route can't get in.** Generalising the block-count lemma
to allow *dirty* cheap jumps — $\delta$ out of a partial arc — comes out
**below** HPV everywhere in the band. The exit table for partial arcs says
why: where a weight-3 exit of a complete traversal has caps
`0 0 0 4 4 6`, nearly all dead ends, a dirty cheap exit has caps
`4 6 6 6 6 dead`. The free loop switch is real and almost unobstructed. The
only structural fact it yields is that a partial arc covering exactly $n-1$ of
its class, at the end of a run of length $\ge 2$, has **no cheap exit at
all**. One bit, and not enough. Getting into the band needs a global argument
about how the splits sit in the cover — the analogue, one rung up, of the
$v = 24$ rigidity behind $s(6) \ge 868$. At $v = 25$ that object is a
near-exact cover of the 120 classes by 25 loops with exactly five doubled,
and there are far too many of those to enumerate the way 10,068 was.

**None of this bounds $s(7)$ at the frontier** — the champions are nowhere
near split-free (Egan/Houston 5906 has $S = 124$ and about 18 blocks).

### The per-loop refinement: $s(7) \ge 5886$ is down to one state

Complete traversals are *loops*, not free parameters. Every arc start
generates exactly one 2-loop, loop $L$ holds $a_L \le n-1$ of them, and a
clean run occupies **consecutive** generators of one loop — so $L$'s arc
starts partition into $r_L \ge 1$ runs summing to $a_L$, and

$$N = \sum r_L, \quad R = \sum a_L, \quad
f := \#\{\text{runs of length } n-1\} = \#\{L : a_L = n-1,\ r_L = 1\}.$$

Every clause is asserted on 604 real walks. Putting it back into the counting
lemma raises the split-free floor ($\beta_6$: 26 → 27) and, at $n = 7$,
$v = 120$, gives $T \ge 131$ — **length $\ge 5895$**, exactly the rung the
Pentad Lemma reaches by a completely different route. At $v = 121$ it returns
**121**, up from 117 and now equal to HPV: the counting reproduces HPV at the
one rung that binds, without citing it.

$s(7) \ge 5886$ needs $T \ge 122$ everywhere, and every rung but $v = 121$
already clears it. Breaking $v = 121$ out by $A$ (with $S = 6-A$) gives
$T \ge 121, 122, 123, 125, 126, 128, 129$ for $A = 0 \dots 6$ — so **only
$A = 0$ survives, short by exactly one**, with a completely pinned state: all
121 loops saturated, 115 traversed complete, 6 broken into two runs each,
$N = 127$ clean runs, 12 dirty jumps, $B = 115$, $Y = 0$.

Transition counting gets within **2** of killing it. Every costly
traversal-to-traversal transition is forced to be om; om-chains cap at
$\mathrm{ord}(a^5b) = 5$, so $\#\text{chains} \ge 23$; and
$\#\text{chains} = \#\text{T-blocks} + \#(\text{dirty T}\to\text{T})
\le 13 + 12 = 25$. No contradiction. Closing that gap of 2 is worth exactly
**+1 on $s(7)$** — and it is harder than the split-free case, because the 12
dirty transitions make the period map branch instead of being a single group
element.

[Full writeup](notes/block_count_lemma).

## Settled: no $n = 6$ champion is split-free

For a split-free walk $\text{length} = 844 + E$, and $s(6) = 872 = 844 + 28$.
An exhaustive search found **no split-free walk with $E \le 28$**, so

> **split-free $\Rightarrow$ length $\ge 873$.** The classical 873 *is*
> split-free, so this is exact: the shortest split-free 6-superpermutation is
> **873**, and **every 872 champion has splits**.

2203 leaf verdicts, $2.98 \times 10^{13}$ nodes, zero feasible, zero cap hits.

Two things make that trustworthy rather than merely large. Every refinement of
the search was verified **exact by node accounting before being used** — work
below the cut computed both ways gave 1,784,777 at depth 8; 370,586,159 at
depth 16; 70,566,880 at depth 24 — so nothing was double-counted or lost
through a gap in the partition. And all three binaries involved still **find**
the known $E = 29$ walk while returning identical node counts, confirming the
extra cut levels changed the parallel decomposition only, never the pruning.
That last gate is the one that matters: an exhaustive "no solution exists" is
worth exactly as much as the proof that the search can still find the solutions
that do exist.

The cost was wildly unbalanced — shard 0's region alone took $5.13\times10^{12}$
nodes, a quarter of the other 1998 combined. The reason is structural, and
worth recording: modular sharding at a *fixed* depth can never split the
leftmost all-$\delta$ spine, because $0 \bmod N = 0$ keeps node 0 whole in
piece 0 at every modulus. It has to be cut *deeper*, not finer, which is why
the search grew a second cut at depth 16 and a third at depth 24.

This promotes the working assumption to a theorem at $n = 6$. It stays open at
$n \ge 7$ — and the split-economy measurements argue against extending it, since
the advantage of splits *grows* from 1 at $n = 6$ to 6 at $n = 7$.

## Must a champion have splits? $n = 6$, and $v = 24$ falls

No known champion at any $n$ is split-free above $n = 5$, and the shortest
split-free strings are conspicuously long — 873 at $n = 6$, 5912 at $n = 7$.
Is that forced? At $n = 6$ the question is finite, because $s(6) = 872$ is
known. Split-free gives $S = 0$ and $\text{length} = 844 + E$ with
$E = B - 1 + Y$, so a split-free champion needs $E = 28$, i.e. $B + Y = 29$.
HPV then bounds $v \le 29$, and covering the 120 classes by loops of 5 forces
$v \ge 24$. Six cases.

The base case is $v = 24$, which means **the 24 loops are an exact cover**.
(It is the same case as $B = 24$: with 24 loops and 120 classes every loop is
full, so every block is a complete traversal, and conversely $B \ge v \ge 24$.
What follows is an *independent* proof of it — no om theory, no chain count,
and every $Y$ at once.) An exact cover fixes everything but the order. There are 144 two-loops at
$n = 6$, each of size 30, each permutation lying in 6 of them, and each loop
has exactly **5 generators, one per class**. So assigning a class to a cover
loop pins its arc's starting permutation. All 120 full arcs are determined,
every $(B, Y)$ compatible with $v = 24$ collapses at once, and what is left is
a single

$$\textbf{minimum-weight Hamiltonian path over 120 fixed nodes},\qquad
E = \mathrm{TSP} - 238 .$$

Up to relabelling there are 29 such covers. Twenty-eight were already
certified optimal at $\ge 267$. The lone holdout, **orbit 28**, sat at
feasible 267 with only 265 proved — so its optimum was 266 or 267, and 266 is
exactly length 872. A branch-and-bound over $E$, using the arc-counting bound
(cost-0 moves are $\delta$ and never leave a loop, so the uncovered classes of
each loop form circular arcs that each need their own block), settles it:

> **No Hamiltonian path of weight 266 exists.** Exhaustive over all 120 start
> nodes, $2.399 \times 10^{10}$ nodes.

So every one of the 29 orbits is optimal at $\ge 267$: $B = 24$ forces
$E \ge 29$ and length $\ge 873 > 872$. **No $n = 6$ champion is split-free
with $B = 24$.**

What remains is $B = 25 \dots 29$, and it is genuinely open. Enumerating the
run-length profiles $(c_1 \dots c_5, Y)$ with $\sum i\,c_i = 120$ and
$B + Y = 29$ leaves **377 states, exactly one of which has $B = 24$** — so 376
remain. Counting cannot trim them: the chain count generalises to
$c_5 \le (n-2)(1 + Y + (B - c_5))$, since a chain of complete traversals is
broken by *any* non-complete block — the om step out of a length-$l$ block is
$a^{l-1}b$, a different group element for each $l$ — and at $n = 6$ with
$B + Y = 29$ that reduces to $c_5 \le 24$, which $5c_5 \le 120$ already gives.
The chain count is **vacuous away from $B = 24$**, and pure counting yields
only $B + Y \ge 25$.

Brute force, though, **is** in reach — after a $550\times$ correction. The
natural analogue of the arc bound (a length-5 run is an entire loop, so it
needs one of the 144 loops still wholly uncovered) turns out to be worth
essentially nothing, and splitting the search by $(B, Y)$ is worth nothing in
aggregate either. What was decisive is mundane: the target loop scanned all 720
candidates per node, because $\text{cost} + w - 2$ alone never exceeds the
budget while cost is small and ~600 targets have weight 6. Hoisting a
target-independent floor on the post-move block bound out of the loop cuts that
to a couple of dozen — node counts byte-identical, only the constant changes.
$E \le 25$ went from 134 s to 0.24 s. Growth is $\approx 114\times$ per unit,
so the decisive run $E \le 28$ is $\approx 4 \times 10^{12}$ nodes, about
13 hours on 20 cores. **It has since completed**: no split-free walk with
$E \le 28$ exists (`data/e28_certificate.txt`), which is the "Settled"
result above.

What the Coset Lemma does give is a change of variables. The $\delta$ step is
right multiplication by $a$, so a 2-loop is a coset of $\langle a \rangle$ and
the 144 loops fall into **6 families of 24, each an exact cover of the 120
classes**. Each class therefore has exactly one arc start per family, and

> a split-free walk **is** an $n$-colouring of the $(n-1)!$ classes — colour of
> $C$ = which family supplies $C$ — together with an ordering,

with $v$ and $B$ readable from the colouring alone. Monochromatic gives
$B = 24$; the best of 2000 random colourings gives $B = 86$. So $B \le 29$ is a
severe rigidity condition on the colouring, and that is where the remaining
leverage most plausibly sits.

### A new conjecture: Family Quantisation

The $B = 24$ walks are exactly the exact covers, and a cover need not sit
inside one family — at $n = 6$ the 10068 covers spread over 1 to 6 families.
But they do not spread freely.

> **Family Quantisation.** In every exact cover of the $(n-1)!$ rotation
> classes by $(n-2)!$ two-loops, the number of loops taken from each family is
> divisible by $n-2$ — equivalently, each family supplies a multiple of
> $(n-1)(n-2)$ classes.

Enumerating *all* exact covers checks it exhaustively: at $n = 4$ the single
split is $(2)$; at $n = 5$ the 25 covers split $(3,3)$ or $(6)$; at $n = 6$ the
10068 covers realise eleven splits — $(12,8,4)$, $(8,8,4,4)$, $(12,4,4,4)$,
$(16,4,4)$, $(8,8,8)$, $(8,4,4,4,4)$, $(16,8)$, $(12,12)$, $(20,4)$,
$(4,4,4,4,4,4)$, $(24)$ — every entry a multiple of 4. A second reading of the
same fact: the distinct *sets* of family-$f$ loops occurring across all covers
number 1612 at $n = 6$, with sizes exactly $4, 8, 12, 16, 20, 24$.

$n-2$ is exactly $\mathrm{ord}(s)$ for the Pentad element $s = a^{n-2}b$, which
is why it looks like the right invariant. It is **not** simply "covers are
unions of $\langle s \rangle$-orbits" — $\langle s \rangle$ does not act on
loops, since a loop's $n-1$ generators lie in different $\langle s \rangle$-orbits,
and the 66 minimal 4-element restricted sets at $n = 6$ overlap rather than
partitioning a family's 24 loops. The mechanism is open; the fact is
exhaustive at $n = 4, 5, 6$.

It does not by itself close $B \ge 25$, which needs partial loops. A
partial-loop version is the natural next target.

## Exact macro-chain capacities past the published table

The strongest current attack on $n = 7$ (vlad-ds's `a7` bundle, conditional
$s(7) \ge 5896$) bottlenecks on one computable object: $M_7(G)$, the longest
chain of "macros" that fits in a gap budget $G$. Their exact table stops at
$M_7(21) = 41$; everything above that uses a conservative partition-closure
relaxation $W(g)$, and the surviving cases are measured against it.

I rebuilt that system from its specification and it reproduces their work
exactly — all of $M_7(0..21)$, **all eleven unpruned node counts**
(31 … 10,465,987), the full $W(g)$ table including the decisive
$W(66) = 130$, and the `cap` field on **1261 of 1261** hard summaries of
their $\delta = 12$ frontier.

Then I changed the algorithm. Instead of meet-in-the-middle over seam masks,
bootstrap the search: at each budget, prune with the partition closure of
only those entries already *proven at smaller budgets*. Nothing is circular —
the cap used at budget $G$ never reads a value at or above $G$, and never
reads the published table — and it is far faster: budget 21 falls in 188,485
nodes where the published route needed 293,568 deduplicated mask pairs. That
buys **nineteen new exact values**, $g = 22$ through $40$:

$$M_7(22 \ldots 40) = 43, 44, 46, 47, 50, 51, 52, 54, 56, 57, 59, 60, 63, 64, 66, 66, 68, 69, 71$$

Each comes with a witness chain validated by a separate checker
(`code/verify_witness.py`) that recomputes the class map, orbits, ports,
supports and disjointness from the specification and shares nothing with the
prover. Together they drop $W(66)$ from **130 to 119**.

**And a negative result to go with it, which turned out to be the useful
half.** I re-ran their entire $\delta = 12$ frontier under the sharpened
capacities. It helps — 332 surviving rows fall to 253 — and then it stops
dead. Feeding in a *hypothetical* exact $M_7$ extrapolated to $g = 95$ at any
growth rate down to 1.0 per unit, pushing $W(66)$ as low as 97, moves the
frontier from 253 to **252**. That is a wall, not an asymptote.

The reason is explicit. Each case is measured against $F_c(G)$, a max-plus
convolution of $W$ over $c$ chains, and since $W(0) = M_7(0) = 5$,

$$F_c(G) \;\approx\; \lambda G + 5c .$$

Extending the exact table lowers $\lambda$. It **cannot touch the $5c$ term**,
because $M_7(0) = 5$ is already exact. The immune rows are the ones whose cap
is dominated by that floor rather than by the slope — up to 46% of it at
$c = 11$. So: *capacity-immune = floor-dominated.*

**What does attack the floor** is already in the bundle: the **full-endpoint
tax**, which replaces $5$ by $4$ on the $K$ pre-hard chains. I reimplemented
its DP (it reproduces their published $\delta = 11$ values 4/4) and measured
the two levers jointly:

| | no tax | tax where already forced | tax everywhere (ceiling) |
|---|---|---|---|
| published table ($g = 21$) | 332 | 298 | 184 |
| **this work ($g = 40$)** | 253 | 222 | **78** |

They are strongly **complementary, not additive** — 332 → 253 alone,
332 → 184 alone, 332 → **78** together. Tightening capacity is what makes the
fullness hypothesis forceable in the first place, and the tax is what
converts it into kills on rows capacity can never reach. 78 residual cases is
the same order as the 14 branches finished by hand at $\delta = 11$.

That was the state of play when the notebook pivoted to the ordering-free
bounds above (`CH3`, the `A2` proof, and the rung settlement); the capacity
table and the plateau diagnosis stand as the record of this route, and the
19 new exact $M_7$ values remain the sharpest public table.

---

The repo with all the verification machinery:
[github.com/levkropp/superperm](https://github.com/levkropp/superperm).
The lemma, properly typeset: [here](absorption-lemma).
