# Cross-read: the vlad-ds 872 proof vs. our lemmas

> ## ⚠️ Reliability warning — read before using this note
>
> This note was written from second-hand impressions, and its description of
> the vlad-ds method is **substantially wrong**. Having since cloned
> [vlad-ds/a6-872](https://github.com/vlad-ds/a6-872) and read it:
>
> - It is **not** a Lean-4 machine-checked proof. It is Python plus a
>   certificate ledger, and the author explicitly labels it preliminary and
>   invites audits. (The Lean-4 work at n=6 is Raudvere's `superperm-coeff2`
>   and Hunter & Raudvere's `superpermutations-hunter` — different repos,
>   different method.)
> - There is **no Jacques genus identity** and no "defect equation
>   m + a + b + η = 4" anywhere in it.
> - The coordinates are **(e, l, s, j)**, not (r, q, p).
> - There is no "3600-row pool".
>
> The n=7 half of the bundle (`a7/`) reduces surviving cases to a
> **macro-chain capacity test**, which is the object I actually reproduced
> and extended — see [`m7_capacity.md`](m7_capacity.md). That note is
> grounded in the source; this one is not.
>
> Keeping this file only as a record of a wrong reading, so it isn't
> re-derived. The "what transfers" items below were checked against our own
> data and stand on their own; the method summary does not.

## Their method in one paragraph *(this paragraph is the incorrect part)*

Normalize away improper weight-2 edges (Lemma 2: an optimal path avoiding
σ² always exists), delete cost ≥ 4 edges, and describe the remaining cheap
cover by (r, q, p) with Lc = 842 + r + q + p ≤ 871. An orbit inequality
r + q ≥ 24 + ⌈r/5⌉ pins the frontier r + q + p = 29, a permutation-pair
genus identity (Jacques) gives the defect equation m + a + b + η = 4, and
the 21 families / 152 cases are eliminated by capacity tables over a
3600-row pool (machine-checked in Lean 4).

## What transfers to us

1. **Normalization is empirically universal**: all five known champions
   (classical, Houston, L2, Coanda, Egan/Houston) use **zero** improper
   weight-2 jumps. We verified this directly (census: w2_proper only).
   Consequence: our prover may **ban σ² jumps** without losing the optimum
   — killing the whole "re-enter a class via a within-class jump" branch
   class; partial classes can then only be re-entered by weight ≥ 3 jumps.
2. **Their orbit inequality is our absorption lemma** in another
   coordinate system: r + q ≥ 24 + ⌈r/5⌉ ↔ v ≥ ⌈(R−1)/5⌉ (same 5-port
   absorption structure, derived via orbit components). Two independent
   proofs, one invariant.
3. **Why they stop at n=6**: the defect budget (frontier − orbit floor)
   is 4 at n=6 (21 families) but **22 at n=7** — the case space explodes
   past capacity-table elimination. The open n=7 territory is precisely
   where genus-defect methods fail and accident accounting (our split
   identity) still works.

## Lemma candidate: normalization ⟹ accident coupling

With σ² banned (safe by their Lemma 2), accidents can only be produced by
proper-δ or weight ≥ 3 arcs. The split identity then reads tight paths'
accident counts off (R, v) alone: A = (n−1)(v − (n−2)!) − splits.
Open: does banning σ² yield an a priori bound on A? If yes, the 5905
family at n=7 collapses to accident-free candidates (A = 0) — the
cleanest possible design space.

## Note on the genus machinery

Jacques' theorem (c(F) + c(A) + c(FA) = |U| + 2k − 2g) is the one tool in
their proof we don't yet have an analog for. At n=7 the run-start
permutation A and the first-return map FA might admit a similar identity,
but the defect budget of 22 makes it unlikely to close the problem the
same way — recorded so nobody re-derives the dead end.
