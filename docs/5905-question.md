---
layout: math
title: "The 5905 question"
---

# The 5905 question
### — can the absorption lemma settle n = 7 one way or the other?

*The n = 7 record is a string of length 5906 (Egan & Houston, 2019). The
best proven lower bound is 5888 (Hunter & Raudvere, Lean-checked). Between
those two numbers there is exactly one question, and it comes from the
absorption lemma.*

## The setup in one minute

The 5040 permutations of 7 symbols group into 720 little cycles of 7 (the
1-cycles, plain rotations), and into 840 "2-loops" of 42 vertices each —
think of each 2-loop as a bus route serving 6 of the small cycles. Every
2-loop has exactly **6 stops where you're allowed to hop on** (its
generators). The absorption lemma is just the punchline of that sentence:
a journey with $R$ route-segments uses $R-1$ hops, so you must ride at
least $\lceil (R-1)/6 \rceil$ distinct routes.

Now weigh the champion (the 5906-string) on it: it makes 844 segments and
rides **142** routes. The lemma's floor for 844 segments is
$\lceil 843/6 \rceil =$ **141**. It spent exactly one route above the
minimum — and that one route is literally the difference between 5906
and 5905, because for journeys that waste nothing elsewhere, the length is
$5757 + v$.

## The question

> **Can 141 bus routes cover all 720 small cycles?**

The champion's 142-route cover is *robust*: we checked, and every one of
its 142 routes is carrying at least two passengers nobody else carries —
you cannot simply delete a route and keep the map working. So a 141-route
cover, if it exists, is a genuinely different map.

There are two outcomes, both valuable:

- **A 141-route cover exists and can be toured cheaply** → a string of
  length **5905**: a new world record (that's an *upper* bound win, like
  Houston's 872 at n = 6).
- **No 141-route cover can work** → **s(7) ≥ 5906**: the record is proven
  optimal, n = 7 is *settled* (a *lower* bound win).

## Why we can actually compute this

Every 141-route cover = a perfectly non-overlapping set of 120 routes
(120 × 6 = 720 cycles exactly) **plus** 21 more routes. So the search
starts with a clean enumeration problem: list all "exact covers" at n = 7.
We have that running on 16 CPU threads right now, and once the count is
known, the 141-loop question either dies or turns into a small
traveling-salesman puzzle — the same trick that proved $s(6) \ge 868$.

Status log and the decomposition tables:
[notes/s7_baseline.md](https://github.com/levkropp/superperm/blob/main/notes/s7_baseline.md)

*Check back here for the answer. One route out of 142 is all that's at
stake.*
