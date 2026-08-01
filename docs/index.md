---
layout: math
title: "AI ripped superpermutations wide open"
---

# AI ripped superpermutations wide open
### — two weeks in the life of a 15-year-old problem

*A field report from inside the storm: how the minimal superpermutation
problem went from a decade of silence to (preliminary) total victory in
fourteen days — told by a team that arrived three days late and still
found something worth keeping.*

## 1. The problem in one breath

A **superpermutation** is a string containing every permutation of $n$
symbols as a contiguous substring; $s(n)$ is its minimal length. Exact
answers were known only for $n \le 5$: 1, 3, 9, 33, 153. For $n = 6$ the
world has known since 2014 that $s(6) \le 872$ (Robin Houston's explicit
string), and since 2011/2018 that $s(6) \ge 867$ (the anonymous 4chan
poster / Houston–Pantone–Vatter lower bound — the proof born as a question
about watching *Haruhi* in every possible order).

For ten years, nothing moved. [The layperson's version of the story](layperson).

## 2. August 2026: fourteen days

| date | result | method |
|---|---|---|
| Jul 17 | $s(6) \ge 868$, $s(7) \ge 5886$, all $n \ge 5$ | Raudvere, **Lean 4 machine-checked** ([coeff2](https://github.com/urdvr/superperm-coeff2)) |
| Jul 28 | $s(6) \ge 869$, $s(7) \ge 5888$, $s(8) \ge 46103$ | Hunter & Raudvere, **Lean 4**, completing Hunter's 2019 draft ([hunter](https://github.com/urdvr/superpermutations-hunter)) |
| Jul 29 | **$s(6) = 872$ exactly** | vlad-ds, computer-assisted partition exhaustion, adversarially audited, *preliminary* ([a6-872](https://github.com/vlad-ds/a6-872)) |
| Aug 1 | $s(6) \ge 868$, independently | **this project** — the elementary one: absorption lemma + rigidity + exhaustive cover TSP |

All four efforts were substantially AI-assisted. The last decade produced
zero progress; the last fortnight produced (provisionally) the answer.

## 3. Our proof — the one you can actually read

Our independent $s(6) \ge 868$ is deliberately built from elementary
pieces, and it is (we claim) the easiest of the four to understand end to
end:

1. **The absorption lemma.** Every "2-loop" (a 30-vertex cycle structure)
   has exactly 5 ports of entry. A path with $R$ segments uses $R-1$
   transitions, so the number $v$ of 2-loops you must enter satisfies
   $$v \ge \lceil (R-1)/5 \rceil.$$
   Both champion strings — the classical one *and* Houston's record — hit
   this bound **exactly**. It is the right invariant. ([The full article,
   with the math rendered](absorption-lemma).)
2. **Rigidity at the minimum.** If you enter the minimum 24 loops, they
   cannot overlap — so the whole problem collapses to a finite
   traveling-salesman puzzle over 120 classes.
3. **Finite computation.** All **10,068** possible covers, solved: every
   one costs more than the old bound. Done.

Same conclusion as coeff2 (868), proven independently, with every artifact
under 100 KB and a 30-minute laptop verification path.
[The certificate](certificate) · [Repo](https://github.com/levkropp/superperm)

## 4. Why our proof "doesn't matter" — and why it does

Three days before we finished, the Lean monsters landed: coeff2's
factorial-gain criterion covering all $n \ge 5$ at once, then Hunter &
Raudvere at 869/5888, then the partition proof of $s(6) = 872$. All of
them machine-checked or machine-audited at a level our CP-SAT certificate
does not match.

So the 868 here is a **second, independent confirmation** — which in
computer-assisted mathematics is a feature, not a consolation prize. And
the machinery built for it (validated GPU BFS prover, exhaustive cover
pipeline, the absorption lemma itself) is reusable for the next frontier:
$s(7)$, where the gap is $5888 \le s(7) \le 5906$ and nobody — yet —
claims victory.

## 5. The map now

- $s(6) = 872$ (preliminary; audits invited — the authors *want* adversaries).
- $s(7)$: **5888 ≤ s(7) ≤ 5906** — the open frontier.
- $s(8)$: 46103 ≤ s(8) ≤ 46204.
- The next decade of the problem: tightening from both sides, with AI in
  the loop everywhere.

*Read next: [the absorption lemma](absorption-lemma) (our piece),
[coeff2](https://github.com/urdvr/superperm-coeff2) and
[hunter](https://github.com/urdvr/superpermutations-hunter) (the Lean
proofs), [a6-872](https://github.com/vlad-ds/a6-872) (the claimed finish
line).*
