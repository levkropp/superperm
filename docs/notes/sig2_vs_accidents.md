---
layout: math
title: "The σ² ban vs. accidents — a resolved (negative) candidate"
---

# The σ² ban vs. accidents — a resolved (negative) candidate

**Candidate.** Does banning improper weight-2 jumps (σ², within-class
re-entries) bound the accident count A?

**Answer: no.** The two objects are orthogonal:

- An *accident* is a generator of an entered 2-loop covered **mid-arc**:
  the arc in its class started at a different generator. It is a fact about
  which generator of a class is the arc start vs. which loop gets entered.
- A σ² jump is a weight-2 re-entry into a partially covered class — a fact
  about *splits*, already priced by the split identity
  (splits = (n−1)(v − (n−2)!) − A).

**Counterexample from the champions themselves:** Egan/Houston's 5906 uses
zero improper jumps (it is fully normalized) **and** has A = 8. A σ²-free
champion with 8 accidents exists, so no ban on improper jumps can force
A below 8 at n=7. (Conversely Houston's 872 is σ²-free with A = 0, so the
ban doesn't force accidents up either.)

**What survives.** The σ² ban stands as a pure search optimization:
validated on n=5 (s(5) ≥ 153 certified in 16.2 s / 118.4M nodes with the
ban, vs 29 s / 138.2M without), deployed in `prove_n5_ban.c` and
`prove_par.c`. It cuts the search tree for free but says nothing about
accidents.

Recorded so the candidate isn't re-derived: the champions answer it.
