---
layout: math
title: "The 14-episode puzzle, explained for everyone"
---

# The 14-episode puzzle, explained for everyone

## The puzzle

Imagine an anime series with episodes you want to watch **in every possible
order**. What is the shortest binge that covers all orderings?

This is the famous "Haruhi problem," and it's how this whole corner of
mathematics became internet-famous: in 2011 an anonymous 4chan user asked
exactly that question about the 14-episode first season of *The Melancholy
of Haruhi Suzumiya*, which originally aired out of order.

Mathematicians call the string a **superpermutation**. For 6 "episodes"
there are 720 possible watch-orders, and the question is: how short can the
binge be?

## What was known

- For 1–5 episodes the exact answers were known: 1, 3, 9, 33, 153.
- For 6 episodes, the answer was trapped between **867** and **872**:
  - In 2011 the anonymous 4chan proof showed you *can't* do better than 867
    (formalized by mathematicians in 2018).
  - In 2014 Robin Houston *found* a string of length 872 — but nobody knew
    if something shorter exists.

And there it sat. For over a decade, nobody moved either number.

## What's new: the 6-episode question is settled

*Updated 7 August 2026.*

In one remarkable week at the end of July 2026, three independent results
landed and closed the question for 6 episodes:

- **The answer is 872** — vlad-ds, computer-assisted proof with a
  certificate ledger (preliminary, audits invited): no shorter binge exists.
- **You can't do better than 869** — Hunter & Raudvere, with the proof
  machine-checked in Lean 4, the strongest guarantee mathematics knows how
  to give.
- **You can't do better than 868** — Raudvere again, Lean-checked, by an
  independent method.

This repository's own contribution, **a proof that you can't do better than
868**, was found in the same week by a different, purely structural route —
it was *not* the first, and we say so plainly. Independent confirmations
matter in computer-assisted mathematics: a bound reached by four unrelated
methods is a bound you can build on.

## How our route worked

Instead of brute force, we used a structural insight about how watch-orders
are organized:

1. Orders come in natural families ("2-loops" of 30 related orders). Any
   complete binge must *enter* at least 24 of these families.
2. Each family can "absorb" at most 5 cheap transitions — so cheap
   transitions are a limited resource, and you run out of them fast.
3. If the binge uses the minimum 24 families, those families can't overlap
   at all, which turns the problem into a small, finite puzzle ("visit 120
   groups in the cheapest order") that a computer can settle *completely*:
   all 10,068 ways to choose the families cost more than the old bound.

Every other possibility needs 25+ families, which already costs more than
867 on its own. Either way, 867 is impossible — you need at least 868.

The same machinery also proved something about the *shape* of any champion:
**no shortest 6-symbol string can be "split-free"** — the cheapest
well-behaved arrangement costs exactly 873, one more than the answer.

## Can I trust a computer proof?

Our proof has a short logical spine (two lemmas you can read on one page)
plus a small, fully re-checkable computation: the list of all 10,068 family
choices (included, 80 KB) and an exact solver run on each of 29 symmetry
classes (scripts included). The same machinery *reproves* the known answers
for 4 and 5 episodes exactly, and Houston's 872 string is verified by an
independent checker here too. Every step is in this repository, and CI runs
the fast checks automatically.

## What happens next

The frontier has moved to **7 episodes**: the answer is between **5888**
(Lean-checked) and **5906** (the best known string, found in 2019). That is
where this repository now works — with a set of proved structural lemmas
(see [Lev's Lemmas](notes/levs_lemmas)) that have already excluded the most symmetric
possibility for a champion, and reduced the whole question to a single
missing lemma about how chains of families can link up.

*Happy watching.*
