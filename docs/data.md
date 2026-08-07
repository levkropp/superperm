---
layout: math
title: "data/ manifest"
---

# data/ manifest

Everything a verification script reads, and where it comes from.

## Certificate inputs (required, no in-repo regenerator)

| file | what it is | read by |
|---|---|---|
| `houston_872.txt` | Houston's length-872 6-superpermutation (the record string) | `certify.py`, `verify_v1_absorption.py`, `census.py` |
| `covers_10068.npz` | all 10,068 exact covers of the 120 rotation classes by 24 disjoint 2-loops at n = 6 (`(10068, 24)` uint16) | `verify_v2_covers.py` — independently re-enumerates and byte-compares |
| `orbits29.json` | the 29 S₆-orbit representatives of the covers | `verify_orbits_tsp.py`, `orbit28.py` |
| `orbit28_starts.txt` | fixed arc starts for the orbit-28 branch-and-bound | `orbit28b.c` |
| `e28_certificate.txt` | text certificate: no split-free 6-superpermutation has E ≤ 28 (the 2.98×10¹³-node sharded run) | cited throughout the notebook; produced by `splitfree6b/c/d.c` + `e28_run.sh` |
| `hpv_lower_bound.pdf` | the 2018 Houston–Pantone–Vatter paper (reference) | — |

## Result records

| file | what it is |
|---|---|
| `orbit_tsp_results.json` | recorded per-orbit V3 outcomes: 28 orbits OPTIMAL at 267–274, one certified 265 |

## Corpora (regenerable; shipped files include the optional upstream corpus)

| file | what it is | regenerator |
|---|---|---|
| `census.json` | ledger-coordinate measurements of the ~182 published strings (n = 5–9) | `code/census.py` (without the upstream clone it covers `data/` only) |
| `champions6.json` | ledger coordinates of the 43,096 known n = 6 optima | `code/champions6.py` (needs the upstream corpus) |
| `walkpool.json` | 108 constructed/annealed walks — the wide, mediocre complement to the census | `code/walkpool.py` |

## n = 7 corpus

`n7/` — the published n = 7 strings from the upstream superpermutations
project (provenance: `n7/Readme.txt`, KernelFinder + PermutationChains). Read
as a directory by `census.py`, `n7_champions.py`, and (via `census.sources`)
`a2hall.py`, `freejoin.py`, `vlock.py`. The `twoCycles_*` files are the same
solutions in Mathematica notation; the digit parsers skip them.
