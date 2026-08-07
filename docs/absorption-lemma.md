---
layout: math
title: "The absorption lemma"
---

# The absorption lemma
### — the counting argument behind $s(6) \ge 868$

*This note presents the new combinatorial lemma at the heart of the recent
improvement of the lower bound for the minimal superpermutation length
$s(6)$ from 867 to 868. The lemma was found in an agent-assisted research
session (Kimi) and is elementary: it counts how cheap transitions between
permutations can be shared by the cycles that cover the problem. Both known
extremal superpermutations saturate it exactly, which is what makes it the
"right" invariant of the problem.*

## 1. Setup

Fix $n = 6$. A **superpermutation** is a string over
$\{1,\dots,6\}$ containing every permutation of the six symbols as a
contiguous substring; $s(6)$ is the minimal length of such a string.

In the **overlap digraph** each vertex is a permutation $u$ of
$\{1,\dots,6\}$, and the weight of the edge $u \to v$ is

$$
w(u,v) \;=\; 6 - \max\{k : \operatorname{suffix}_k(u) = \operatorname{prefix}_k(v)\},
$$

the number of symbols one must append to $u$ (dropping the same number from
the front) to obtain $v$. Since $w$ satisfies the triangle inequality,
minimal superpermutations correspond exactly to minimum-weight Hamiltonian
paths:

$$
s(6) \;=\; 6 + \min_{\text{Hamiltonian paths } P} \operatorname{wt}(P).
$$

**Weight-1 edges** rotate: $u = (u_1,\dots,u_6) \mapsto \sigma(u) =
(u_2,\dots,u_6,u_1)$. They partition the 720 vertices into $120$
**1-cycles** (rotation classes) of 6 vertices. **Weight-2 edges** relevant
here are the *proper* ones, $u \mapsto \delta(u) = (u_3,\dots,u_6,u_2,u_1)$.

A **2-loop** is the orbit of the walk "$n-1$ weight-1 edges, then one
weight-2 edge," repeated; it contains $n(n-1) = 30$ vertices and has exactly
$n-1 = 5$ **generators** — the permutations obtained from any member $\pi$
by fixing its last entry and cyclically permuting the others (Houston,
Pantone & Vatter, Prop. 1). There are $144$ distinct 2-loops; each vertex
generates exactly one.

A walk is a sequence of **arcs** (maximal runs of weight-1 edges inside a
1-cycle) joined by **jumps** (edges of weight $\ge 2$). Writing $R$ for the
number of arcs, a walk has exactly $R - 1$ jumps. A walk **enters** a 2-loop
when it traverses an edge of weight $\ge 2$ and arrives at one of the loop's
generators. Write $v$ for the number of distinct 2-loops entered.

Houston, Pantone and Vatter proved the invariant

$$
\operatorname{wt} \;\ge\; p + c + v - 2,
$$

with $p$ = distinct permutations visited ($720$ for complete walks) and
$c$ = completed 1-cycles ($\ge 119$). Every visited vertex lies in an
entered 2-loop (an arc stays in the 1-cycle of its entry generator, and
each 1-cycle is contained in that generator's loop), whence $v \ge
\lceil 720/30 \rceil = 24$ and the classical bound $\operatorname{wt} \ge 720 +
119 + 24 - 2 = 861$.

## 2. The lemma

<div class="thm">
<span class="tag">Absorption lemma.</span>
<em>For any Hamiltonian path in the $n=6$ overlap digraph, the number $v$ of
entered 2-loops and the number $R$ of arcs satisfy</em>

$$
v \;\ge\; \left\lceil \frac{R-1}{5} \right\rceil .
$$
</div>

**Proof.** A path with $R$ arcs has $R-1$ jumps, hence $R-1$ *distinct*
jump targets (the path visits no vertex twice). A 2-loop is entered only by
arriving at one of its generators, and each 2-loop has exactly $5$
generators. So each entered 2-loop absorbs **at most 5** of the targets,
and covering all $R-1$ targets requires $v \ge \lceil (R-1)/5 \rceil$. $\blacksquare$

Equivalently (and this is the form in which it was first noticed), if $J$
denotes the number of jumps and $v$ the number of entered loops, then

$$
J \;\le\; 5v - 1,
$$

since the start vertex is itself a generator of the start loop and is never
landed on. The two statements are the same inequality.

The general-$n$ form is $v \ge \lceil (R-1)/(n-1) \rceil$.

## 3. The lemma is *tight* — and that is the point

A counting lemma like this would be unremarkable if it were loose. It is
not. Both known extremal constructions saturate it, at opposite ends of the
$R$-spectrum:

- **The classical construction** (string length 873): $R = 120$, $J = 119$,
  $v = 24$, and $\lceil 119/5 \rceil = 24$. Every 2-loop absorbs the
  maximum 5 targets (one loop takes 4, the start loop).
- **Houston's 872-string** (the record): $R = 145$, $J = 144$, $v = 29$,
  and $\lceil 144/5 \rceil = 29$. Again every entered loop is filled to
  capacity.

Houston's construction is in fact tight for the whole HPV invariant:
$\operatorname{wt} = 866 = 720 + 119 + 29 - 2$ with *zero* slack — the
absorption lemma is exactly the counting identity that forces its shape
($v - 24 = 5$ extra loops for its $25$ split 1-cycles: $25 = 5 \times 5$).

## 4. The consequence: a rigidity theorem at $v = 24$

Combined with the HPV invariant, the lemma gives the *v-ladder*: a path of
weight $\operatorname{wt}$ has $v \le \operatorname{wt} - 837$, and by the
absorption lemma $R \le 5v + 1$. But the real power is at the boundary
$v = 24$:

<div class="thm">
<span class="tag">Rigidity.</span>
<em>If a complete walk enters exactly $v = 24$ two-loops, then the 24 loops
are pairwise disjoint (an **exact cover** of the 120 1-cycles), every
1-cycle is traversed as a single full arc of 6 vertices ($R = 120$), and</em>

$$
\operatorname{wt} \;=\; 600 + \operatorname{TSP}(\mathcal{X}),
$$

<em>where $\mathcal{X}$ is the cover and $\operatorname{TSP}(\mathcal{X})$
is the minimum over orderings of the 120 1-cycles of the sum of jump
weights — a finite combinatorial quantity per cover.</em>
</div>

*Why.* The entered loops cover all 720 visited vertices and each has 30
vertices, so $24 \times 30 = 720$ forces disjointness. Disjointness gives
each 1-cycle a **unique port** (the one cover-generator it contains); every
jump into a class must land on the port, so each class is entered at most
once, and the start vertex must itself be its class's port. Hence full arcs
only, $600$ weight-1 edges in total, and the jumps reduce to a class-order
problem. $\blacksquare$

## 5. The computation

Exact covers of the 120 1-cycles by 24 of the 144 2-loops:

$$
\#\{\text{exact covers}\} = 10{,}068,
$$

falling into $29$ orbits under the $S_6$ relabeling action (orbit sizes sum
to $10{,}068$ exactly). For each orbit, the class-TSP was solved with
CP-SAT:

$$
\operatorname{TSP}(\mathcal{X}) \;\ge\; 265
\quad\text{for every exact cover } \mathcal{X},
$$

with 28 orbits at optimal values $267$–$274$ and the family orbit (the one
attained by the classical construction) at exactly $267$.

**Theorem (computer-assisted).** *Every superpermutation on 6 symbols has
length at least $868$.*

*Proof.* If $v \ge 25$, then $\operatorname{wt} \ge 837 + 25 = 862$. If
$v = 24$, rigidity gives $\operatorname{wt} \ge 600 + 265 = 865$. Hence
$\operatorname{wt} \ge 862$ always, and $s(6) = 6 + \operatorname{wt} \ge
868$. $\blacksquare$

The same scheme retro-proves $s(4) = 33$ (4 covers, TSP $= 11$) and
$s(5) = 153$ (25 covers, TSP $= 52$) — the classical bound is *exactly* the
TSP-over-covers bound at those $n$.

## 6. Why the older machinery could not do this

Every polynomial relaxation of the instance collapses far below the target:
the assignment relaxation is $720$, the undirected MST bound is $838$, the
Held–Karp 1-tree ascent is $839$, and the subtour-elimination LP is
**exactly $840$** (certified by an explicit fractional point). The 2-loop
constraint — *distinct loops entered*, a set-cover condition — is precisely
what these relaxations dissolve. The absorption lemma is the first
invariant that prices that constraint correctly.

## 7. What it pointed to next

Both items on the original roadmap are now settled elsewhere: $s(6) \ge 869$
was proved by Hunter & Raudvere (Lean-4 machine-checked), and $s(6) = 872$
exactly by vlad-ds (computer-assisted, preliminary). What survived of this
route is the *structure*: the $v$-ladder pricing of the channels, and the
exact-cover rigidity idea, which reappears one rung up — at $n = 7$, $v = 120$,
where the same argument shape now gives length $\ge 5908$ and excludes the
exact-cover rung for champions (see the
[notebook](index)). The absorption lemma itself is the $A \ge 0$ corollary of
the all-$n$ Split Identity $R = (n-1)v - A$ proved in the repository.

---

*Verification artifacts (enumeration scripts, cover lists, solver logs, and
the independent checker) live in the repository; see the
[certificate](certificate) for the full chain.*

**Note (August 2026):** this lemma, found independently here, was published
days after stronger machine-checked results already covered the same bound
(coeff2: s(6) ≥ 868, and Hunter–Raudvere: s(6) ≥ 869). It remains the
elementary form of the counting argument — tight on both extremal strings —
and the route we used to *verify* the bound independently.
