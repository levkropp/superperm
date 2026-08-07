---
layout: math
title: "The A-cost law (as the evidence now reads)"
---

# The A-cost law (as the evidence now reads)

**Question.** Why does Egan/Houston's 5906 need A = 8 accidents with E = 17
while Coanda's 5907 pays A = 0 with E = 22?

**Finding 1 — accidents are free.** For every accident-affected loop, the
entry actually taken is the *minimum* available weight (weight 3 in all
four cases, computed against every unvisited generator). Accidents force
no extra E.

**Finding 2 — accidents come in adjacent pairs.** All 8 of Egan's
accidents form 4 pairs: two *adjacent* generators of one loop's generator
cycle, pre-covered mid-arc by another loop's arc, followed by a weight-3
entry at the *next* generator in the cycle. A coherent motif, a "stitch".

**The law (as now evidenced).**
A counts *stitches*: pre-covers of two adjacent generators of a loop,
closed by a weight-3 entry at the next generator. A stitch costs the same
excess (1) as the explicit split it replaces — it is **E-neutral**, a
repackaging of class coverage from an explicit split arc into the middle
of another loop's arc. It is not a cost; it is the mechanism that lets a
path carry one more loop entry within the same excess budget.

**Consequence for the champions.** Egan's 5906 = 4 stitches + 17
structural weight-3 entries (v = 142, splits = 124, E = 17). Coanda's
5907 = 0 stitches + 22 heavy joins (v = 140, splits = 120, E = 22). The
5906's slack-1 above the absorption floor is precisely its hand of
stitches: the nsk kernel's trick for buying the final unit below the
absorption diagonal.

**Search guidance.** A 5905 design should spend stitches deliberately:
they relocate excess, they don't create it. The stitched-entry motif
(two adjacent pre-covered generators, then w3 at the next) is an explicit,
checkable building block for the GPU annealer's move set.
