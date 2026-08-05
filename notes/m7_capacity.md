# Exact macro-chain capacities at n=7, past the published table

**New results (this repo):** `M_7(22..40) = 43, 44, 46, 47, 50, 51, 52, 54,
56, 57, 59, 60, 63, 64, 66, 66, 68, 69, 71`, extending the vlad-ds `a7`
bundle's exact table, which stops at `M_7(21) = 41`. Each value is certified
in both directions: a witness chain validated by an independent checker, and
an exhaustive pruned search showing nothing longer fits.

## Why this object matters

The strongest current attack on s(7) (vlad-ds `a6-872`, directory `a7/`,
conditional `a(7) >= 5896`) reduces every surviving case to a capacity test.
`M_7(G)` is the maximum number of *macros* in a chain of total gap `G` with
exact port equations and pairwise-disjoint class supports. Above the exact
table the bundle falls back on a conservative partition-closure relaxation
`W(g)`, and a case dies only when its block count `N` exceeds `F_c(G)`, a
max-plus convolution of `W`. Every unit shaved off `W` is a unit of pressure
on the frontier.

## The system (as reconstructed)

Break state `z = z_0..z_6`, a permutation of 0..6.

    P(z)   = (z_0, z_6, z_1, z_2, z_3, z_4, z_5)      marker z_0 fixed
    A_g(z) = { rotClass(P^i z) : g <= i < 6 }          support, size 6-g
    I(z)   = (z_2,z_3,z_4,z_5),   O(z) = (z_3,z_4,z_5,z_6)
    macro (z,g): costs g, covers A_g(z); successor z' has I(z') = O(P^g z)

Each `(z,g)` has exactly `3! = 6` physical successors.

## Reproduction of the published work

Rebuilt from the specification alone, sharing no code with the bundle:

- `M_7(0..21)` — all 22 values, including the irregular tail 36, 38, 40, 41.
- All **eleven unpruned node counts**: 31, 85, 349, 1231, 4573, 17143, 62875,
  227113, 827785, 2945461, 10465987. Exact agreement on node counts is a much
  stronger signal than agreement on the values alone.
- The partition-closure cap `W(g)`: 13/13 published values, including the
  decisive `W(66) = 130`.
- The `cap` field on **1261/1261** hard summaries of `A7_DELTA12_FRONTIER.csv`.

Code: `code/macro7.py` (reference), `code/macro7.c` (fast), `code/capacity_dp.py`,
`code/frontier12.py`.

## The algorithmic change: bootstrap pruning

The bundle reaches budget 21 by seam-normalized meet-in-the-middle (293,568
deduplicated mask pairs at budget 21; 794,286 across budgets 11-20). Instead:

> **Bootstrap.** When computing `M_7(G)`, prune with `depth + W(budget) <= best`,
> where `W` is the partition closure of *only the entries already proven at
> smaller budgets*. Seed `best` at `M_7(G-1)`, which is sound because `M_7` is
> nondecreasing and that length already has a witness.

Nothing is circular: the cap used at step `G` never reads any value at or above
`G`, and never reads the published table. It is also far cheaper — budget 21
falls in **188,485 nodes**, and the search stays tractable well past it:

| G | 21 | 22 | 23 | 24 | 25 | 26 | 27 | 28 | 29 | 30 |
|---|---|---|---|---|---|---|---|---|---|---|
| M_7(G) | 41 | **43** | **44** | **46** | **47** | **50** | **51** | **52** | **54** | **56** |
| nodes (k) | 188 | 159 | 546 | 223 | 983 | 88 | 554 | 1435 | 839 | 401 |

| G | 31 | 32 | 33 | 34 | 35 | 36 | 37 | 38 | 39 | 40 |
|---|---|---|---|---|---|---|---|---|---|---|
| M_7(G) | **57** | **59** | **60** | **63** | **64** | **66** | **66** | **68** | **69** | **71** |
| nodes (k) | 3236 | 1045 | 3884 | 406 | 2539 | 702 | 14489 | 7693 | 25316 | 14230 |

Growth over 21..40 is 30/19 = 1.58 macros per gap unit. Note `M_7(36) =
M_7(37) = 66`: the sequence does have flat steps this high up, which is
information the partition closure cannot represent — `W` is strictly
increasing by construction.

Witnesses are emitted to `witness.txt` and checked by `code/verify_witness.py`,
which recomputes the class map, P-orbits, supports, port equations and
disjointness from the spec and shares nothing with the prover.

## Payoff, measured on the real frontier

Re-running the bundle's 332-row `delta = 12` frontier under sharpened capacity:

| exact table | W(66) | delta=12 survivors |
|---|---|---|
| published, to g=21 | 130 | 332 |
| this work, to g=22 | 127 | 330 |
| this work, to g=25 | 126 | 299 |
| this work, to g=28 | 125 | 284 |
| this work, to g=32 | 123 | 282 |
| this work, to g=36 | 120 | 256 |
| this work, to g=40 | 119 | **253** |

## Why capacity alone plateaus, exactly

Nineteen new exact entries buy 11 units off `W(66)` and 79 of the 332 rows,
and then stop. Replacing the extended table with a *hypothetical* exact `M_7`
extrapolated all the way to `g = 95` at any growth rate from 1.55 down to 1.0
per unit — pushing `W(66)` as low as **97**, far below anything the real
sequence will deliver — moves the frontier from 253 survivors to **252**. The
plateau is not asymptotic; it is a wall.

Here is the reason, and it is completely explicit. Each hard summary is
measured against `F_c(G)`, the max-plus convolution of `W` over
`c = 1 + x + K` chains. Since `W(0) = M_7(0) = 5`,

    F_c(G)  ~  lambda * G  +  5c,

with `lambda` the growth rate of `W`. Extending the exact table lowers
`lambda`. **It cannot touch the `5c` term, because `M_7(0) = 5` is already
exact.** For the 252 immune rows the binding summaries all have `c` in 3..11
against gaps `G/c` of 3..22, so a large fraction of their cap is that
irreducible floor — up to 46% at `c = 11`. Those rows were never going to die
from a better table.

That is the characterisation of the capacity-immune set: **floor-dominated,
not slope-dominated.**

## What actually attacks the floor

The lever with the right shape is already in the bundle: the **full-endpoint
tax** (proof note section 7). If a hard component is *full*, its boundary loop
supplies an appendable full macro `(z,0)`, so a pre-hard run of budget `g` has
length `L <= W(g) - 1`. In other words the tax replaces `5` by `4` on `K` of
the `c` chains — it attacks the floor directly, which capacity cannot.

`code/tax12.py` implements the tax DP `T` (untaxed chains capped by `W`,
pre-hard regions by `E(g) = max(0, W(g) - 1)`) and reproduces the bundle's
published `delta = 11` values **4/4**: `T_8(38) = 112`, `T_8(36) = 109`,
`T_10(30) = 105`, `T_12(24) = 101`.

At `delta = 11` the tax was *licensed* because capacity was tight enough to
force every hard component full. At `delta = 12` it is not: only 230 of 1261
summaries are marked full, and only 45 carry a tax. So the two levers are
coupled — and measuring them jointly gives the real picture:

| | no tax | tax where already forced | tax everywhere (ceiling) |
|---|---|---|---|
| published table (g=21) | 332 | 298 | 184 |
| **this work (g=40)** | 253 | 222 | **78** |

They are strongly **complementary, not additive**. Table extension alone:
332 → 253. Tax alone: 332 → 184. Both: 332 → **78**. Tightening capacity is
what makes the fullness hypothesis forceable, and the tax is what converts
tighter capacity into kills on the floor-dominated rows that capacity cannot
reach by itself.

78 residual rows is the same order as the 14 branches that were finished by
hand at `delta = 11`.

## Open

- **The live problem:** force fullness at `delta = 12`. The ceiling row above
  is conditional on every hard component being full; making that a theorem
  (or bounding the deficiency spend) is what turns 253 into something near 78.
- How far does bootstrap pruning go? Node counts are noisy but not yet
  exploding at 40 (worst so far is budget 39 at 25.3M nodes; 40 came back in
  half that).
- Is there a direct (non-partition-closure) upper bound on `M_7` at large `g`?
  The exact data grows at ~1.58/unit while `W` grows at ~2.0/unit. Worth
  doing on its own merits, but note the analysis above: it buys `lambda`, not
  the floor, so on its own it is worth at most one more row.
- Does global class-disjointness *across* the `c` chains bite? `F_c` treats
  the chains independently, but their supports must be disjoint in the same
  720 classes. At the observed sizes (`30c` classes for floor chains, `c <=
  21`) it looks slack, but it has not been checked.
