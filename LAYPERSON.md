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

## What's new — with an important correction

*This page was written on 1 August 2026. Two days earlier, independent
teams had already posted **stronger** results: s(6) ≥ 869 (Hunter &
Raudvere, Lean-checked) and even s(6) = 872 exactly (vlad-ds,
preliminary). The 868 bound below is therefore an independent confirmation
by a different method — not the first proof. The story of how fast this
problem is moving is itself remarkable.*

**We proved you can't do better than 868.** The binge needs at least 868
episodes of runtime. The gap is now 868–872.

Why is that a big deal for a "one-point" improvement? Because the lower
bound had resisted every attack since 2011 — including industrial-scale
computer searches (over 100 million CPU-hours trying to find shorter
strings came up empty). The new proof doesn't come from brute force; it
comes from a *structural* insight about how watch-orders are organized:

1. Orders come in natural families ("2-loops" of 30 related orders). Any
   complete binge must *enter* at least 24 of these families.
2. We show each family can "absorb" at most 5 cheap transitions — so cheap
   transitions are a limited resource, and you run out of them fast.
3. If the binge uses the minimum 24 families, those families can't overlap
   at all, which turns the problem into a small, finite puzzle ("visit 120
   groups in the cheapest order") that a computer can settle *completely*:
   all 10,068 ways to choose the families cost more than the old bound.

Every other possibility needs 25+ families, which already costs more than
867 on its own. Either way, 867 is impossible — you need at least 868.

## Can I trust a computer proof?

The proof has a short logical spine (two lemmas you can read on one page)
plus a small, fully re-checkable computation: the list of all 10,068
family choices (80 KB, included) and an exact solver run on each of 29
symmetry classes (~30 minutes on a laptop, scripts included). The same
machinery *reproves* the known answers for 4 and 5 episodes exactly, and
Houston's 872 string is verified by an independent checker here too. Every
step is in this repository, and CI runs the fast checks automatically.

## What happens next

The answer for 6 episodes is now between 868 and 872. To close it we need
either one more point on the lower bound (the roadmap for 869 is sketched
in the repo) or a certified solution of the full "traveling salesman"
instance on all 720 orders — a computation that crashed the best solver in
2014 but is within reach of today's hardware. Meanwhile, Houston's 872
string remains the champion binge.

*Happy watching.*
