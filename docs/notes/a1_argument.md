---
layout: math
title: "Trying to prove no 872-string has A = 1"
---

# Trying to prove no 872-string has A = 1

`A1EQ` (**[MEAS]**, 44,564 strings): every walk with exactly one accident is an
Egan string — `d = (n−3)!`, `B = 1`, `Y = 0`. In particular no length-872 walk
at n = 6 has `A = 1`, the single gap in the n = 6 optimum spectrum
`A ∈ {0,2,3,4,5}`.

This note reports an attempt to prove it. **The attempt did not succeed, and it
failed in an informative way**: the whole ordering-free apparatus is provably
vacuous on this question. One new lemma came out of it that is worth keeping on
its own account.

---

## 1. The case structure — pure algebra

Length 872 ⟺ `T = 29`. With `A = 1`:

* Split Identity `R = (n−1)v − A` gives `R = 5v − 1` and `S = 5v − 121`;
* `T = S + B + Y = 29` gives `B + Y = 150 − 5v`;
* `S ≥ 0` forces `v ≥ 25`, `B ≥ 1` forces `v ≤ 29`.

So exactly five sub-cases:

| v | 25 | 26 | 27 | 28 | 29 |
|---|---|---|---|---|---|
| S | 4 | 9 | 14 | 19 | 24 |
| B+Y | 25 | 20 | 15 | 10 | 5 |

`A = Σ_L (n−1−a_L) = 1` also pins the shape: **v−1 loops saturated** (all n−1
generators are arc starts), one loop contributing n−2.

## 2. Lemma S1 — **[THM]**, and worth having regardless

> Let `L` be a saturated loop in which every arc starting at a generator of `L`
> is full. Then `L`'s n−1 arcs form a directed cycle in the δ-graph.
> Consequently
> $$\#\{\text{saturated loops with all arcs full}\} \;\le\; \mathrm{comps} \;\le\; B.$$

*Proof.* The arc at generator `g` is full, so it ends at `σ^{n−1}(g)`, and
`δ(σ^{n−1}(g)) = g·a` — the next generator of `L` in its `⟨a⟩`-orbit. `L` is
saturated, so `g·a` is an arc start, i.e. the δ-edge exists and stays inside
`L`. Applying this to all n−1 generators closes the orbit into a cycle, which
is a whole component of the δ-graph since in- and out-degree there are ≤ 1
(`IN5`). Each block of the walk is a path in the δ-graph, so `B ≥ comps`. ∎

Verified **1463/1463** on the corpus, and **tight** exactly where expected — on
the exact-cover walks, where every loop is all-full: `24 = 24` at n = 6 and
`120 = 120` for `5913-palindromic`.

## 3. Lemma S2 — the collision bound

An arc is partial iff its class is multiply covered, so a saturated loop fails
to be all-full only if it contains a multiply-covered class. With `m` such
classes and `Σ_C(μ_C−1) = S`, and the arcs of one class lying in distinct
families hence distinct loops, at most `Σ_C μ_C = S + m ≤ 2S` loops contain a
partial arc. With S1:

> `B ≥ (v − 1) − 2S = 241 − 9v`.

At v = 25 that is `B ≥ 16` against `B + Y = 25` — no contradiction, and it is
vacuous from v = 27 on. Honest floor, not an answer.

## 4. Why the whole approach is vacuous here — **the actual finding**

The plan rested on the ordering-free test `T ≥ S + comps` (`IN5`), which is
computable from the arc-start set alone. `code/a1.py` implements the A = 1
system enumerator and evaluates it.

**Gate first:** at `A = 0, v = 24` the enumerator reproduces the published
**10,068 exact covers** exactly, with `S = 0`, `comps = 24`, `allfull = 24` —
S1 tight.

**Then the result.** At `v = 25, A = 1` (4,000 systems sampled):

```
S + comps: min 27, max 29        need > 29 to exclude length 872
best system: S=4 comps=23 allfull=20
```

Every system sits at or below 29. And this is not an artefact of sampling — it
is forced. `S + comps = v` on optimal systems (`A3`), and `v ≤ 29` in every
sub-case of the table, so `S + comps ≤ 29` **can never be violated**.

> **The ordering-free test is HPV in disguise, and HPV does not exclude any of
> the five rungs.** No amount of enumeration over arc-start sets can prove
> `A = 1` impossible at 872.

This is the same wall as `notes/second_order.md` §A3 — but note the wall was
mis-described there and here. The retracted claim was *"no ordering-free
invariant of the arc set can beat HPV"*; what is actually true is only that
`S + comps` cannot, since `min(S + comps) = (n−2)!` exactly. `CH3` adds the
free-chain count `p` and **does** beat HPV — 29 against 24 at the n = 6
exact-cover rung ([`pbound.md`](pbound)). The `A = 1` question really is
blocked, but by the Inflation Lemma, not by this.

## 5. What a proof would actually need

`T = S + B + Y` and `B ≥ comps` bound the `S + B` part and nothing else. To
exclude the five rungs one needs a **lower bound on `Y`** valid away from the
exact-cover rung — precisely the generalisation of the Chain-Count Lemma that
`lemma_arsenal.md` §10 asks for and §11 identifies as the single open lever.
Concretely, excluding A = 1 at 872 needs

| v | 25 | 26 | 27 | 28 | 29 |
|---|---|---|---|---|---|
| would need Y > | 25 − B | 20 − B | 15 − B | 10 − B | 5 − B |

and the Chain-Count Lemma supplies such a bound only at `v = (n−2)! = 24`,
which is not among these.

## 6. Status

| item | status |
|---|---|
| the five-sub-case algebra | **[THM]** |
| S1, `#all-full ≤ comps ≤ B` | **[THM]**, 1463/1463, tight on exact covers |
| S2, `B ≥ 241 − 9v` | **[THM]**, vacuous for v ≥ 27 |
| A = 1 excluded at 872 | **open** — and provably not reachable by any ordering-free argument |
| `A1EQ` in general | **[MEAS]**, 44,564 strings |

The A = 1 gap is real and the conjecture is well supported, but it is not a
soft target: it is the main open problem wearing a different hat.

---

## 7. Follow-up probe: does S1 give a Y-bound off the exact-cover rung?

It does, and the answer is a new theorem plus a clean explanation of why it
still cannot supply ε.

**The Exposure Bound — [THM].** Let `F` be the number of **all-full saturated
loops**. By S1 each is a δ-cycle, traversed as a block of `n−1` arcs, so a
weight-3 transition between two of them has `l + l' = 2n−2 ≥ 2n−3` and is
*forced* onto om (§3.2); om-chains cap at `ord(s) = n−2`, giving

> `F ≤ (n−2)(1 + Y + B − F)`   — holds **1463/1463**.

Solving for `Y` and substituting into `T = S + B + Y`, **`B` cancels**:

> $$T \;\ge\; S + \left\lceil \tfrac{(n-1)F}{n-2} \right\rceil - 1$$

— fully **ordering-free**, since `S` and `F` both come from the arc set. Holds
**1463/1463**.

**It beats HPV on the exact-cover side, by a lot:**

| walk | n | F | S | T | Exposure Bound | HPV (v) |
|---|---|---|---|---|---|---|
| `5913-palindromic` | 7 | 120 | 0 | 149 | **143** | 120 |
| `873-palindromic` | 6 | 24 | 0 | 30 | **29** | 24 |
| `houston_872` | 6 | 2 | 25 | 29 | 27 | 29 |
| `5906` champion | 7 | 4 | 124 | 142 | 128 | 142 |
| `5908-egan` | 7 | 0 | 143 | 144 | 142 | 144 |

At the exact-cover rung (`F = (n−2)!`, `S = 0`) it evaluates to exactly
`(n−1)(n−3)! − 1` — **the Egan−1 line** — recovering the Chain-Count value
*without* Chain-Count's split-free hypothesis. That is a genuine strengthening
of that lemma's scope.

**Why it still cannot supply ε.** `F` is the *chain-count exposure*, and
champions evade the tax by keeping it tiny:

| | F |
|---|---|
| exact cover (n=7) | 120 |
| n=7 optima | 2…19, mostly 4–6 |
| n=6 optima | 0…8, mostly 1–4 |
| Egan (any n) | **0** |

At the n = 7 champion `F = 4` against a chain cap of 75 — slack by a factor of
19. Even the most exposed champions (`F = 19`) give a bound of `S + 22 = 136`
against `v = 142`. To beat HPV at n = 7 one would need `F ≥ 16` *and* `S` near
124 simultaneously, which the `B+Y−A = 10` invariant forbids.

> **So the mechanism is real, now quantified, and provably the wrong lever:
> the champions' escape from the chain count is precisely to minimise F.**
> Supplying ε needs a *lower* bound on F — a reason a walk must contain many
> all-full saturated loops — and the measured spectra above show no such bound
> can be strong.

---

## 8. Postscript: `A1EQ` is false, and so was the test used here

The next step after this note was to promote `A1EQ` — *A = 1 ⟹ the Egan
vertex* — to **[THM]**. It is false. See [`notes/ordering.md`](ordering);
the short version:

* `A = (n−1)v − R` reads the arc-start **set**, `B` reads consecutive pairs.
  Rotating the arc list of `5908-egan` gives a verified superpermutation of
  length **5909** with `A = 1, B = 2`.
* Unioning one unentered 2-loop into that arc-start set leaves `A = 1` while
  moving `d` to 25 and `comps` to 2…6 — so `d = (n−3)!` and `comps = 1` fail
  as well.

The corpus evidence was an artefact of the corpus holding only near-optimal
strings. `A1EQ` survives as **`A1EQO` [MEAS]**, guarded by optimality, and the
n = 6 question this note was written about — *no 872-string has A = 1* — is
unchanged and still open.

**One thing here does need amending.** §4 leans on `T ≥ S + comps` (`IN5`) as
the ordering-free exclusion test. `IN5` is also false: a weight-2 jump has two
possible targets, `δ(u)` and `σ²(u)`, and `comps` follows only the first, so a
single block can span two δ-components (`SIG2`, `IN5b` in the registry). The
conclusion of §4 is untouched — the test was found to be *vacuous* there, and a
vacuous test that is also invalid excludes nothing either way.

The inequality itself is **recovered** for the use §4 makes of it. `SIG2X`: the
σ² jump can always be exchanged away at no cost in length (`R` drops by 2 and
`Δlength = w(X,Z) − w1 − w2 ≤ 0`), so the minimum length is attained at
`σ2 = 0`, where `B ≥ comps` does hold. Since every exclusion argument here is
aimed at the *optimum*, `T ≥ S + comps` remains a legitimate test — it is just
still HPV in disguise, so §4's verdict stands.
