---
layout: math
title: "The 5905 question — retracted, and what replaces it"
---

# The 5905 question

### — an earlier framing of mine that was wrong, and the correct obligation

*This page used to pose a dichotomy: "can 141 two-loops cover all 720
one-cycles? Yes ⟹ a 5905-string; No ⟹ $s(7) \ge 5906$." Both halves are
wrong. I'm leaving the page up with the error stated plainly, because the
corrected version is the actual roadmap for $n = 7$.*

## The setup (this part was right)

The 5040 permutations of 7 symbols group into 720 one-cycles of 7 (plain
rotations), and into 840 **2-loops** of 42 vertices each — think of a 2-loop
as a bus route serving 6 of the small cycles. Every 2-loop has exactly **6
stops where you may hop on** (its generators). The absorption lemma is the
punchline: a journey with $R$ route-segments uses $R-1$ hops, so it must ride
at least $\lceil (R-1)/6 \rceil$ distinct routes.

Weigh the champion (5906) on it: 844 segments, **142** routes ridden, floor
$\lceil 843/6 \rceil = 141$. One route above the minimum — and it is
HPV-tight, $\mathrm{wt} = 5757 + 142$.

## What was wrong

**1. The covering question is trivially "yes".** Not 141 — **120** two-loops
suffice, and they can be made pairwise disjoint. $120 \times 6 = 720$ exactly,
and explicit exact covers are exhibited in
[`code/pentad_orbits.py`](https://github.com/levkropp/superperm/blob/main/code/pentad_orbits.py)
(24 pairwise class-disjoint $\langle s \rangle$-orbits = 120 loops, partitioning
all 720 classes).
So "no 141-route cover can work" was never a live branch, and the "⟹ $s(7) \ge
5906$" half of the dichotomy is a non sequitur.

**2. The inequality was pointing the wrong way.** HPV gives
$\mathrm{wt} \ge 5757 + v$, i.e.

$$\mathrm{length} \;\ge\; 5764 + v .$$

That bounds $v$ from **above** for a given length. A 5905-string has
$v \le 141$; it does not "need $v \ge 141$." (This page also wrote the tight
length as $5757 + v$, mixing weight and length units — it is $5764 + v$.)
Curiously the repo has the direction right at $n = 6$, where it says any
871-string has $v \le 28$; the sign flipped only when the argument was carried
to $n = 7$.

## What actually has to be discharged

Covering forces $v \ge 120$. Length forces $v \le L - 5764$. So proving
$s(7) \ge 5906$ is not one question but a **ladder of 22 rungs**:

$$v = 120, 121, \dots, 141, \qquad \text{rung } v \text{ needs slack} \ \ge 142 - v .$$

Low rungs are easy — a $v = 120$ string would have to waste 22 units of slack
and nothing else, which is heavily over-constrained. The rungs get harder as
$v$ climbs toward 141, where the champion lives. This is exactly the
obligation vlad-ds's `a7` bundle indexes by $\delta = \mathrm{length} - 5884$;
they have discharged $\delta \le 11$ (conditional $s(7) \ge 5896$) and are
stuck at $\delta = 12$ with 332 surviving cases.

## Where I am on it

I rebuilt the bundle's capacity machinery from its specification and
reproduced it exactly, then extended its exact table past where it stopped —
see [the notebook front page](./) and
[`notes/m7_capacity.md`](notes/m7_capacity).
The headline there is a *negative* result worth as much as the positive one:
sharpening capacity does not clear $\delta = 12$. The surviving rows fall
from 332 to 253 with the extended table and then plateau at 252, no matter
how good the capacity bound gets. That rung needs a new **structural**
necessary condition, not a better count.
