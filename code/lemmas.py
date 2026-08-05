"""Claim registry: every candidate lemma, evaluated against two corpora.

    data/census.json    182 real strings -- near-optimal but NARROW
                        (163 of the 169 n=7 entries are `5906_derived`)
    data/walkpool.json  constructed walks -- mediocre but WIDE

A relation can hold on all 182 records and still be false: `comps = v - S` did
exactly that, and three walks out of `mcolour` refuted it immediately.  So no
claim here is trusted on the census alone.

Status tags follow `notes/lemma_arsenal.md`:

    [THM]   elementary proof, given in `why`; a violation is a BUG and this
            file exits non-zero
    [CONJ]  survives both corpora, no proof yet
    [MEAS]  measured on records only, or known to be corpus-dependent
    [REF]   refuted -- kept with its witness so it is not re-proposed

Usage:
  python3 code/lemmas.py            # evaluate everything
  python3 code/lemmas.py --only A2  # one claim
"""

import argparse
import json
import math
import os
import sys

CENSUS, POOL = "data/census.json", "data/walkpool.json"
CHAMPS6 = "data/champions6.json"


def base(n):
    return n + math.factorial(n) + math.factorial(n - 1) - 3


def egan(n):
    return base(n) + (n - 1) * math.factorial(n - 3)


def F2(n):
    return math.factorial(n - 2)


# ---------------------------------------------------------------------------
# The registry.  Each claim: (id, tag, statement, why, applies, holds)
# `applies` filters rows; `holds` is the predicate that must be true.
# ---------------------------------------------------------------------------

CLAIMS = [
    ("ID1", "[THM]",
     "T = (n-1)d + (B+Y) - A",
     "Split Identity S = (n-1)d - A substituted into SBY T = S+B+Y.",
     lambda r: True,
     lambda r: r["T"] == (r["n"] - 1) * r["d"] + (r["B"] + r["Y"]) - r["A"]),

    ("ID2", "[THM]",
     "R = (n-1)v - A",
     "The Split Identity itself (notes/split_identity.md).",
     lambda r: True,
     lambda r: r["R"] == (r["n"] - 1) * r["v"] - r["A"]),

    ("ID3", "[THM]",
     "N = B + dirty",
     "A clean run ends at a block end or a dirty jump, nothing else.",
     lambda r: "N" in r,
     lambda r: r["N"] == r["B"] + r["dirty"]),

    ("ID4", "[THM]",
     "n_partial = S + m",
     "A class covered mu>=2 times contributes mu partial arcs and mu-1 to S.",
     lambda r: "m" in r,
     lambda r: r["n_partial"] == r["S"] + r["m"]),

    ("A1", "[THM]",
     "HPV-tight and length = Egan(n) - k  =>  B + Y - A = (n-2)k",
     "T = v = (n-2)! + d and ID1 give (n-2)d = (n-2)! - (B+Y-A); substitute "
     "d = (n-3)! - k and use (n-2)! + (n-3)! = (n-1)(n-3)!.",
     lambda r: r["hpv_tight"],
     lambda r: r["B"] + r["Y"] - r["A"]
     == (r["n"] - 2) * (egan(r["n"]) - r["length"])),

    ("A1u", "[THM]",
     "Free-Jump Inequality (no hypothesis):  B + Y - A >= (n-2) * "
     "(Egan(n) - length),  i.e. saving s characters over Egan costs "
     "B + Y - A >= (n-2)s",
     "A1 needs HPV-tightness; this does not.  Write k = B+Y-A.  ID1 says "
     "T = (n-1)d + k, so d = (T-k)/(n-1); feed that into HPV, T >= (n-2)! + d:\n"
     "    (n-1)T >= (n-1)(n-2)! + T - k   =>   (n-2)T >= (n-1)(n-2)! - k\n"
     "and (n-1)(n-2)!/(n-2) = (n-1)(n-3)! = Egan's T, giving\n"
     "    T >= (n-1)(n-3)! - k/(n-2).\n"
     "So the saving over Egan is at most k/(n-2).  Holds on all 44,672 rows of "
     "both corpora and is EXACTLY TIGHT on 43,740 of them -- including every "
     "record: n=6 needs k>=4 and has 4, n=7 needs 10 and has 10, n=8 needs 6 "
     "and has 6.  So the n = 7 champions' measured invariant B+Y-A = 10 is "
     "FORCED, not observed.  Two corollaries: BLK2 is the case k <= 1, and a "
     "new n = 8 record at 46203 requires B + Y - A >= 12 against the current "
     "record's 6.",
     lambda r: True,
     lambda r: r["B"] + r["Y"] - r["A"]
     >= (r["n"] - 2) * (egan(r["n"]) - r["length"])),

    ("A1c", "[THM]",
     "costly jumps = B - 1 = (n-2)k + A - Y - 1  (HPV-tight)",
     "Immediate from A1.  At A = Y = 0 beating Egan by k needs exactly "
     "(n-2)k - 1 weight->=3 jumps; Egan itself has B = 1, i.e. ZERO.",
     lambda r: r["hpv_tight"],
     lambda r: r["B"] - 1 == (r["n"] - 2) * (egan(r["n"]) - r["length"])
     + r["A"] - r["Y"] - 1),

    ("IN1", "[THM]",
     "A >= 0   (absorption)",
     "lemma_arsenal.md 2.1.",
     lambda r: True,
     lambda r: r["A"] >= 0),

    ("IN2", "[THM]",
     "v >= (n-2)!   (covering)",
     "lemma_arsenal.md 2.2.",
     lambda r: True,
     lambda r: r["v"] >= F2(r["n"])),

    ("IN3", "[THM]",
     "T >= v   (HPV)",
     "lemma_arsenal.md 2.3, external.",
     lambda r: True,
     lambda r: r["T"] >= r["v"]),

    ("IN4", "[THM]",
     "dirty <= n_partial <= 2S",
     "A dirty jump leaves a partial arc, injectively; and m <= S.",
     lambda r: "n_partial" in r,
     lambda r: r["dirty"] <= r["n_partial"] <= 2 * r["S"]),

    ("SIG2", "[THM]",
     "the weight-2 successors of u are exactly delta(u) and sigma^2(u); the "
     "latter needs a LENGTH-1 arc at sigma(u)",
     "weight(u,v) = 2 means u[2:] = v[:n-2], so v = u[2:] + {u[0],u[1]} in one "
     "of two orders: delta(u) = u[2:]+u[1]+u[0] and sigma^2(u) = u[2:]+u[0]+u[1]. "
     "For sigma^2(end_i) to START an arc, both sigma(end_i) and sigma^2(end_i) "
     "must be arc starts (the arcs of a class tile its ring, so sigma(end_i) is "
     "the next start after arc i), i.e. the arc at sigma(end_i) has length 1.  "
     "A full arc has mu_C = 1 and no second start in its class, so NO sigma^2 "
     "jump ever leaves a full arc.  Checked by `code/inflate.py` on every "
     "witness it builds.",
     lambda r: False,
     lambda r: True),

    ("IN5", "[MEAS]",
     "B >= comps   -- true on 44,564 strings, FALSE in general",
     "Was [THM] on the argument 'each block is a path in the delta-graph'.  "
     "That needs every weight-2 jump to be delta, and SIG2 says it need not be: "
     "a block taking a sigma^2 jump spans TWO delta-components.  Witnesses from "
     "`code/inflate.py`, both verified by blockcount/dirty on the re-parsed "
     "string: n=6 length 881 with B=2 < comps=3, and n=7 length 5914 with "
     "B=1 < comps=2.  Corpus scan: 0 of 44,564 strings take a sigma^2 jump, "
     "though 92 of them contain a length-1 arc, so the move is AVAILABLE and "
     "never taken.  `T >= S + comps` is therefore not an ordering-free theorem "
     "-- but SIG2X recovers it where it was used: the MINIMUM length is "
     "attained at sigma2 = 0, so the bound is valid against the optimum.",
     lambda r: "comps" in r,
     lambda r: r["B"] >= r["comps"]),

    ("IN5b", "[THM]",
     "B + sigma2 >= comps,  sigma2 = #sigma^2 jumps <= #(length-1 arcs)",
     "The repaired IN5.  Each block is a path in the free-jump graph, whose "
     "edges are the delta ones plus the sigma^2 ones (SIG2).  A block using j "
     "sigma^2 jumps splits into j+1 delta-paths, so the arcs are covered by "
     "B + sigma2 delta-paths and that is at least comps.  The bound "
     "sigma2 <= #(length-1 arcs) is SIG2, since distinct sigma^2 jumps sit at "
     "distinct length-1 arcs.  Not row-wise: sigma2 is not carried in the "
     "corpus rows; checked by `code/inflate.py`.",
     lambda r: False,
     lambda r: True),

    ("SIG2X", "[THM]",
     "the sigma^2 exchange: every walk has one of length <= it with sigma2 = 0. "
     "Hence min length IS attained at sigma2 = 0, and T >= S + comps is valid "
     "as a bound on the OPTIMUM.",
     "Let arc A_p end at e and jump sigma^2 to A_{p+1} at sigma^2(e).  By SIG2 "
     "there is a length-1 arc A_q at sigma(e), elsewhere in the walk.  In the "
     "ring of that class A_p, A_q, A_{p+1} are consecutive, so splicing A_q out "
     "of its own slot and letting the walk run straight through merges all "
     "three into ONE arc: R drops by 2.  Writing X, Z for A_q's old neighbours "
     "and w1 = w(X,sigma(e)), w2 = w(sigma(e),Z), the character count changes "
     "by w(X,Z) - w1 - w2 <= 0, since the string X -> sigma(e) -> Z is a "
     "witness of length w1+w2 for joining X to Z (weight is subadditive).  The "
     "merged arc fits because the three are disjoint segments of one n-element "
     "ring.  R strictly drops and R >= (n-1)!, so iterating terminates at a "
     "walk with no sigma^2 jump and no greater length.  This RESTORES the only "
     "use IN5 ever had: min length >= base(n) + min over arc sets of "
     "(S + comps).  Verified by `code/sig2x.py` at n = 6 and n = 7.",
     lambda r: False,
     lambda r: True),

    ("SIG2Y", "[THM]",
     "an OPTIMUM with sigma2 >= 1 implies an optimum with strictly larger Y "
     "and B; in particular some optimum has Y >= 1",
     "At an optimum SIG2X's exchange cannot shorten, so w(X,Z) = w1 + w2 "
     "exactly, with w1, w2 >= 2 (a weight-1 neighbour of the singleton would "
     "be the same arc).  So two jumps of weight >= 2 are replaced by one of "
     "weight >= 4: B gains 1 and Y gains (w1+w2-3) - (w1-3)+ - (w2-3)+ >= 1.  "
     "One step suffices for the statement; iterating is what SIG2X needs, and "
     "the step count is only bounded below by 1, since an exchange may create "
     "a fresh sigma^2 jump even as R falls.  "
     "CONSEQUENCE: a sigma^2-using optimum is reachable only by RUNNING THE "
     "EXCHANGE BACKWARDS from a sigma2 = 0 optimum, and each reverse step "
     "consumes a jump of weight >= 4, of which a walk has at most Y.  That "
     "makes the question decidable over a corpus, and `code/sig2x.py --corpus` "
     "decides it at n = 6: of 43,096 optima, 808 carry a weight->=4 jump and "
     "NONE admits a free reverse exchange.  Length-1 arcs are not the "
     "obstruction -- 872-nonstandard has 8, and 20 of the n = 7 champions "
     "have 1..12.",
     lambda r: False,
     lambda r: True),

    ("A2", "[THM]",
     "comps >= v - S   -- PROVED",
     "Let Q be the LOOP QUOTIENT multigraph: nodes the v entered loops, edges "
     "the live inter-loop delta-edges.\n"
     "(1) THE EXIT IDENTITY.  For any arc of class C ending at e, the next arc "
     "of C round the ring starts at s = sigma(e), so e = sigma^{-1}(s), and by "
     "the definition of a = c^(n-1)d, delta(sigma^{-1}(x)) = x.a.  Hence\n"
     "        delta(e) = s . a\n"
     "-- an arc exits into the LOOP OF THE NEXT ARC OF ITS OWN CLASS.  If "
     "mu_C = 1 the next arc is itself, so the edge is intra; if mu_C >= 2 the "
     "arcs of C lie in distinct loops (3.4) and the edge is inter.  Verified "
     "1275/1275.\n"
     "(2) CLASS CYCLES.  A multiply-covered class with all mu_C exits live "
     "contributes the closed cycle L_1 -> L_2 -> ... -> L_mu -> L_1 in Q.  "
     "Distinct classes use distinct arcs hence distinct edges, so these cycles "
     "are EDGE-DISJOINT and therefore independent in Q's cycle space.\n"
     "(3) CYCLE RANK.  Q has v nodes and e_inter = (S + m) - D edges "
     "(n_partial = S + m by ID4, less the D dead ones), so its cycle rank is "
     "(S + m - D) - v + q with q = #components of Q.  That is at least the "
     "number of fully-live multiply-covered classes, m - D'' where D'' <= D "
     "counts classes owning a dead arc.  Rearranging,\n"
     "        v <= S + q + (D'' - D) <= S + q.\n"
     "(4) comps >= q.  Every delta-component's loops lie in one Q-component "
     "(any inter edge inside it is a Q-edge), every Q-component contains at "
     "least one delta-component (its loops have arcs), and distinct "
     "Q-components have disjoint arc sets.\n"
     "Combining, comps >= q >= v - S.  QED\n"
     "Both steps verified: v <= S + q and comps >= q on 1275/1275 census "
     "strings (slack 0 on both -- that is A3) and with strict slack "
     "off-distribution.  A2 was [CONJ] for this repo's whole history and its "
     "one recorded proof route was REF1; the route that works is the quotient "
     "cycle rank, which REF1 never tried.",
     lambda r: "comps" in r,
     lambda r: r["comps"] >= r["v"] - r["S"]),

    ("A2b", "[THM]",
     "T >= v + Y   against the OPTIMUM  (strengthens HPV wherever Y > 0)",
     "T = S + B + Y >= S + comps + Y >= v + Y, the first step by B >= comps and "
     "the second by A2.  Both are now settled: A2 is [THM] (the loop-quotient "
     "cycle-rank proof) and B >= comps is IN5, false in general but valid "
     "against the OPTIMUM by SIG2X -- which is the only place a lower bound is "
     "used.  It went [CONJ] -> [REF]-dependent -> [THM] within this session as "
     "IN5 was refuted and then A2 was proved.  At the exact-cover rung it "
     "reproduces the Chain-Count Lemma.",
     lambda r: True,
     lambda r: r["T"] >= r["v"] + r["Y"]),

    ("A2c", "[CONJ]",
     "dirty <= S + N - v   (equivalent to A2b)",
     "lemma_arsenal.md 11 shows HPV is precisely `dirty <= S+N+Y-v`, and says "
     "any improvement must have the form `... - eps`.  This is eps = Y.  Found "
     "independently by scanning `dirty <= aS+bN+gv` over both corpora: the "
     "tightest valid form is a=b=1, g=-1, exactly attained at the 872 record "
     "(dirty 49 vs 2S = 50).",
     lambda r: "N" in r,
     lambda r: r["dirty"] <= r["S"] + r["N"] - r["v"]),

    ("EGAN1", "[REF]",
     "v + Y >= (n-1)(n-3)! - 1   -- the Egan-1 Law",
     "With A2b (T >= v+Y) this says s(n) >= Egan(n) - 1: no construction beats "
     "Egan by more than one character.  Holds with EQUALITY at the n = 5, 6, 8, "
     "9 records and on all 43,096 n=6 optima.  REFUTED at n = 7 by exactly 1: "
     "5906 has v+Y = 142 against the bound 143.  So 5906 is the only object "
     "known anywhere that beats Egan by more than 1, and the entire difficulty "
     "of the problem sits in that single unit.",
     lambda r: True,
     lambda r: r["v"] + r["Y"]
     >= (r["n"] - 1) * math.factorial(r["n"] - 3) - 1),

    ("C6a", "[REF]",
     "A = 0 at every n = 6 optimum   -- FALSE",
     "Held on the 43,096 standard-kernel optima, but the repaired census "
     "(census.py now reads every line of every file) turns up n = 6 optima "
     "with A = 2, 3, 4, 5.  So accidents are NOT what carries a walk past the "
     "Egan-1 line: n = 6 has plenty of them and every one of its 44,121 "
     "optima still sits exactly on the line.",
     lambda r: r["n"] == 6 and r["length"] == 872,
     lambda r: r["A"] == 0),

    ("MOD4", "[MEAS]",
     "at n = 7 every optimum has A = 8..18 with A != 3 (mod 4)",
     "237 optima, 9 vectors: A in {8,9,10, 12,13,14, 16,17,18} -- groups of "
     "three spaced by n-3 = 4, with residue 3 never realised.  At n = 6 the "
     "spectrum is A in {0,2,3,4,5}, i.e. A = 1 alone is missing.  Unexplained; "
     "consistent with accidents arriving in bundles rather than singly.",
     lambda r: r["n"] == 7 and r["length"] == 5906,
     lambda r: 8 <= r["A"] <= 18 and r["A"] % 4 != 3),

    ("A1EQF", "[REF]",
     "A = 1  =>  d = (n-3)!, B = 1, Y = 0   -- FALSE",
     "It was never provable: A = (n-1)v - R reads the arc-start SET, B reads "
     "consecutive pairs, so INFL inflates B while holding A fixed.  Witnesses "
     "from `code/inflate.py`, all verified superpermutations: rotating the "
     "5908-egan arc list gives length 5909 with A=1, B=2; unioning one "
     "unentered 2-loop into its arc-start set gives length 5914..5919 with "
     "A=1, d=25 and comps 2..6.  Same at n=6 (874, 878..881).  So all three "
     "conclusions fail, and the corpus evidence was an artefact of the corpus "
     "holding only near-optimal strings.",
     lambda r: False,
     lambda r: True),

    ("A1EQO", "[MEAS]",
     "at a KNOWN OPTIMUM or one above it, A = 1 <=> the Egan vertex",
     "The surviving content of the old A1EQ, with the guard it always needed. "
     "Every A = 1 walk in the 44,564-string corpus is an Egan string: "
     "154-tight-egan (n=5), 873-egan / 873-tight (n=6), 5908-egan (n=7) -- all "
     "with d = (n-3)!, B = 1, Y = 0, S = (n-1)(n-3)!-1.  So no length-872 "
     "string has A = 1, which is why A = 1 is the single gap in the n = 6 "
     "optimum spectrum {0,2,3,4,5}.  Still open, and now known to need a "
     "hypothesis on the ORDERING: see notes/ordering.md.",
     lambda r: r["A"] == 1,
     lambda r: r["B"] == 1 and r["Y"] == 0
     and r["d"] == math.factorial(r["n"] - 3)),

    ("ORD", "[THM]",
     "R, S, v, d, A, comps, m, mu_max, n_partial are ordering-free; "
     "B, Y, T, clean, dirty, N, length are not",
     "`build.coords` computes A = (n-1)v - R with v and R read off the arc "
     "starts, and comps from the delta-graph on the arc SET; B and Y come from "
     "weight(end of arc i, start of arc i+1).  Verified by permuting the arc "
     "list of a real string 40 ways in `code/inflate.py`: the first group never "
     "moves, the second always does.",
     lambda r: False,
     lambda r: True),

    ("INFL", "[THM]",
     "Inflation Lemma: any walk with B < R has a reordering with B' = B+1 and "
     "T' >= T+1 on the SAME arc set",
     "Cut the arc sequence at a point where consecutive arcs are joined by a "
     "free (weight <= 2) jump and swap the two pieces; the new junction is not "
     "a free edge, so it costs weight >= 3 and adds a block.  ORD keeps A, S, "
     "v, d, comps fixed.  COROLLARY, and the reason this is worth a claim: no "
     "implication of the form '(ordering-free hypothesis) => (upper bound on "
     "B, Y or T)' can be a theorem.  Only LOWER bounds on those three survive. "
     "Every claim here that bounds B, Y or T from above therefore needs an "
     "optimality guard -- see notes/ordering.md for the audit.",
     lambda r: False,
     lambda r: True),

    ("S1", "[THM]",
     "F := #(saturated loops with all arcs full) <= comps",
     "If loop L is saturated (all n-1 generators are arc starts) and every arc "
     "at a generator of L is full, then that arc ends at sigma^(n-1)(g) and "
     "delta of it is g.a -- the next generator of L, hence an arc start.  So "
     "L's n-1 arcs close into a directed delta-cycle: one whole component.  "
     "Verified 1463/1463 on the corpus, and TIGHT on the exact-cover walks "
     "(24 = 24 at n=6, 120 = 120 for 5913-palindromic).  The old second half "
     "'comps <= B' was IN5 and is now [REF] -- see SIG2.  Checked by "
     "`code/a1.py`, not row-wise here (the corpus rows do not carry the "
     "per-loop arc lengths).",
     lambda r: False,
     lambda r: True),

    ("B1", "[THM]",
     "B = 1  =>  Y = 0,  T = S+1,  and F = 0   (n >= 4)",
     "B = 1 + #{jumps of weight >= 3}, so B = 1 means there are none: Y is an "
     "empty sum, hence Y = 0 and T = S+B+Y = S+1.  For F: by S1 an all-full "
     "saturated loop is a delta-cycle, hence a whole delta-component, and its "
     "arcs are full so by SIG2 no sigma^2 edge touches them.  A walk can then "
     "only enter or leave that cycle by a weight->=3 jump, of which B = 1 says "
     "there are none -- so the cycle would have to BE the whole walk, forcing "
     "R = n-1 against R = (n-1)! + S > n-1 for n >= 4.  The clause 'comps = 1' "
     "used to be here, inherited from IN5, and is false: see B1c.",
     lambda r: r["B"] == 1,
     lambda r: r["Y"] == 0 and r["T"] == r["S"] + 1),

    ("BLK1", "[THM]",
     "B = 1  =>  the string is a word in {sigma, delta}  (append 1 char, or 2). "
     "The converse is FALSE.",
     "B = 1 says every jump has weight <= 2.  A weight-1 jump appends one "
     "character and lands on sigma(u).  A weight-2 jump appends two and lands "
     "on delta(u) or sigma^2(u) (SIG2); the sigma^2 case is literally two "
     "sigma steps, since its intermediate window sigma(u) is a permutation and "
     "is in the string either way.  So B = 1 walks are words in {sigma,delta} "
     "and length = n + #sigma + 2*#delta.  A delta step's intermediate window "
     "is NOT a permutation (reaching u[2:]+u[1]+u[0] appends u[1] first, giving "
     "u[1:]+u[1]), so delta covers one new permutation for two characters and "
     "always wastes exactly one: length = n + (n!-1) + W with R = W + 1.  "
     "CONVERSE FALSE: a word whose sigma steps land on three or more "
     "consecutive already-covered permutations produces a weight->=3 jump in "
     "the path of first occurrences, hence B >= 2 -- `code/block1.py` finds "
     "such a word at n = 5, W = 30, with B = 2.  The word model is therefore a "
     "SUPERSET of the single-block walks, which is the direction the search "
     "needs.",
     lambda r: False,
     lambda r: True),

    ("BLK2", "[THM]",
     "B = 1  =>  d >= (n-3)!  and  T >= (n-1)(n-3)!,  i.e. length >= Egan(n)",
     "The case k <= 1 of A1u.  B1 gives Y = 0, so k = B+Y-A = 1 - A <= 1 by "
     "IN1, and A1u caps the saving over Egan at k/(n-2) <= 1/(n-2) < 1.  The "
     "saving is an integer, so it is <= 0: T >= (n-1)(n-3)!.  Feeding that back "
     "through HPV, T >= (n-2)! + d, gives nothing new, but the Split Identity "
     "S = (n-1)d - A with T = S+1 gives (n-2)d >= (n-2)! + A - 1, hence "
     "d >= (n-3)! - 1/(n-2) and, d being an integer, d >= (n-3)!.  COROLLARY: "
     "**every "
     "superpermutation shorter than Egan(n) has B >= 2** -- it must pay at "
     "least one weight->=3 jump.  That is the k = 0 base case of the Free-Jump "
     "Lemma (A1) without A1's HPV-tightness hypothesis.",
     lambda r: r["B"] == 1,
     lambda r: r["d"] >= math.factorial(r["n"] - 3)
     and r["T"] >= (r["n"] - 1) * math.factorial(r["n"] - 3)),

    ("BLK3", "[THM]",
     "B = 1 and length = Egan(n)  =>  A = 1, d = (n-3)!, S = (n-1)(n-3)!-1",
     "The equality case of BLK2, and the surviving half of the old A1EQ.  "
     "T = (n-1)(n-3)! with T >= (n-2)! + d forces d <= (n-3)!, and BLK2 forces "
     "d >= (n-3)!, so d = (n-3)!.  Then S = T - 1 = (n-1)(n-3)! - 1 and the "
     "Split Identity S = (n-1)d - A gives A = 1.  So the Egan vertex is not a "
     "coincidence of the construction: it is the ONLY place a single block can "
     "sit at Egan length.  What is false is the converse, A = 1 => B = 1 "
     "(A1EQF).",
     lambda r: r["B"] == 1 and r["length"] == egan(r["n"]),
     lambda r: r["A"] == 1 and r["d"] == math.factorial(r["n"] - 3)
     and r["S"] == (r["n"] - 1) * math.factorial(r["n"] - 3) - 1),

    ("B1c", "[MEAS]",
     "B = 1  =>  comps = 1   -- true on the corpus, FALSE in general",
     "Followed from IN5, which SIG2 refutes.  Witness from `code/inflate.py`: "
     "the n = 7 walk of length 5914 built by unioning loop 5 into 5908-egan's "
     "arc-start set has B = 1 and comps = 2 -- a single block spanning two "
     "delta-components, joined by one sigma^2 jump.  Confirmed by "
     "blockcount/dirty on the re-parsed string.",
     lambda r: r["B"] == 1,
     lambda r: r.get("comps", 1) == 1),

    ("KICK1", "[THM]",
     "Kick Identity:  kicks = (n-1)! + 2S + Y - T - dirty",
     "A KICK is a weight-2 jump out of a FULL arc -- the move to the next "
     "village (rotation class) of the same 2-loop.  That is `clean`, and "
     "clean = R - N since a clean run of a arcs carries a-1 kicks.  Substitute "
     "R = (n-1)! + S, N = B + dirty and B = T - S - Y.  Pure bookkeeping.",
     lambda r: "N" in r,
     lambda r: r["R"] - r["N"] == math.factorial(r["n"] - 1) + 2 * r["S"]
     + r["Y"] - r["T"] - r["dirty"]),

    ("KICK2", "[THM]",
     "Kick Bound:  kicks >= (n-1)! - T + Y,  equality iff dirty = 2S",
     "Immediate from KICK1 and `dirty <= 2S` (IN4).  Since T = length - base_n, "
     "a SHORTER string forces MORE kicks: every character saved costs at least "
     "one extra kick.",
     lambda r: "N" in r,
     lambda r: r["R"] - r["N"] >= math.factorial(r["n"] - 1) - r["T"] + r["Y"]),

    ("KICK3", "[THM]",
     "Egan uses exactly (n-1)! - (n-2)! - (n-3)! + 1 kicks, at every n",
     "Egan sits at T = (n-1)(n-3)! = (n-2)! + (n-3)!, Y = 0 and dirty = 2S - 1 "
     "(one short of the cap), so KICK1 gives the count exactly.  Measured: "
     "17, 91, 577, 4201, 34561 at n = 5..9.  Hence a champion saving k "
     "characters needs at least kicks(Egan) + k - 1.",
     lambda r: False,
     lambda r: True),

    ("REF2", "[REF]",
     "dirty <= (2-eps)S for some fixed eps > 0   -- IMPOSSIBLE",
     "lemma_arsenal.md 11 calls `dirty <= 2S` the single most concrete open "
     "lever.  It is not a lever: `dirty = 2S` is ATTAINED EXACTLY by 12,672 of "
     "the 44,121 length-872 optima.  At n = 7, 8, 9 the records fall short by "
     "only 1..4 in absolute terms (ratios .9958, .9976, .9999 -- rising toward "
     "1), so any true bound is `dirty <= 2S - O(1)`, an additive constant, "
     "never a factor.  Since the closed-form ladder's denominator is "
     "(n-1)(c(3n-5)-(2n-3))-1 with c = n_partial/S, and Hunter's is the c = 1 "
     "value, the factor-4 gap to Hunter CANNOT be closed by tightening the "
     "dirty budget.  Hunter's advantage comes from somewhere structurally "
     "different.",
     lambda r: False,
     lambda r: True),

    ("REF3", "[REF]",
     "S - m (triply-covered classes) grows with n   -- FALSE",
     "Proposed as the way to force c < 2.  Measured across 44,564 strings: "
     "S - m is 0..3 at n = 6, 0..6 at n = 7, and exactly 0 at both the n = 8 "
     "and n = 9 records.  It does not scale, and optima with m = S exactly "
     "(every multiplicity 2) exist at every n.",
     lambda r: False,
     lambda r: True),

    ("S5", "[THM]",
     "Exposure Bound:  T >= S + ceil((n-1)F/(n-2)) - 1,  F = #all-full "
     "saturated loops",
     "By S1 each all-full saturated loop is a delta-cycle traversed as a block "
     "of n-1 arcs, so a weight-3 transition between two of them has "
     "l + l' = 2n-2 >= 2n-3 and is forced onto om (3.2); om-chains cap at "
     "ord(s) = n-2, giving the general chain form F <= (n-2)(1 + Y + B - F).  "
     "Solving for Y and substituting into T = S+B+Y makes **B cancel**, so the "
     "bound is ORDERING-FREE -- S and F both come from the arc set.  It "
     "survives the SIG2 correction: an all-full loop's arcs are full, so by "
     "SIG2 no sigma^2 edge touches them and their cycle is entered and left "
     "only by weight->=3 jumps, exactly as the derivation assumes.  Holds "
     "1463/1463.  It recovers the Chain-Count value at the exact-cover rung "
     "(F = (n-2)!, S = 0 gives exactly (n-1)(n-3)! - 1, the Egan-1 line) but "
     "WITHOUT the split-free hypothesis Chain-Count needs.  Checked by script, "
     "not row-wise (F is not carried in the corpus rows).",
     lambda r: False,
     lambda r: True),

    ("SYMM", "[THM]",
     "relabelling and reversal preserve the entire ledger vector",
     "Relabelling pi acts by u -> pi.u, which commutes with sigma and delta "
     "(they act on positions, pi on values), so classes, loops, arcs and all "
     "edge weights are carried across.  Reversal is verified equal on every "
     "coordinate at n = 6 and n = 8.  CONSEQUENCE: building more champions by "
     "symmetry adds strings but NO new coordinate vectors -- a second n = 8 "
     "vector needs a genuinely different construction.",
     lambda r: False,        # checked directly in the note, not row-wise
     lambda r: True),

    ("CH1", "[REF]",
     "the FREE-JOIN graph has out-degree <= 1  -- FALSE, and false on REAL "
     "strings, not just off-distribution; superseded by FORCE",
     "A free join costs max(0,w-3) = 0, so w <= 3; w <= 2 between distinct "
     "delta-components would merge them, so it is a weight-3 jump, and of the "
     "<= 9 weight-<=3 targets of an arc end at most one is another component's "
     "entry.  Measured out-degree: 1 for all 120 states at the n=6 exact cover "
     "(a permutation, 30 cycles of length 4 = ord(s)), 1 for all 720 at the "
     "n=7 exact cover, and 0-or-1 at the n=6 and n=7 champions.  At an exact "
     "cover it is FORCED: every arc is full, so l+l' = 2n >= 2n-3 puts the "
     "weight-3 exit on om (arsenal 3.2), which is unique.  Away from there it "
     "is measured, not proved.  `code/chainer.py` asserts it and exploits it: "
     "exact Y at the n=6 exact cover (6, against the old heuristic's 9) and at "
     "the n=7 champion (0 in 3 ms, where the old chainer returned 5 in 50 s).\n"
     "REFUTED, `code/freejoin.py`: out-degree exceeds 1 on the CENSUS, not "
     "merely on annealer states -- 19 states reach 2 at n = 6 and 38 reach 2 "
     "with 11 reaching 3 at n = 7.  The record already said 'away from an exact "
     "cover it is measured, not proved'; it is now measured FALSE.  Nothing in "
     "chainer.py depended on it (it branches over the successor list), and the "
     "correct length-gated statement is FORCE.",
     lambda r: False,
     lambda r: True),

    ("LOOP1", "[THM]",
     "A = 0  =>  the arc-start set is an EXACT UNION of whole 2-loops.  So "
     "optima move by loops, not by cuts.",
     "A = (n-1)v - R = sum over entered loops of (n-1 - a_L), so A = 0 forces "
     "a_L = n-1 for every entered loop: all n-1 generators are arc starts.  "
     "Measured 409/409 on sampled n = 6 optima.  CONSEQUENCE, and the reason "
     "every cut-level move set in `code/graft.py` fails: over the 43,096 n = 6 "
     "optima no two differ by a single relocation (43,096 connected components "
     "of size 1), 100% of pairwise distances among the S = 25 optima are "
     "multiples of n-1 = 5 with minimum 15, and counted in LOOPS the minimum "
     "is 3.  Optima are 3 loop-swaps apart and DISCONNECTED at cut-level "
     "radius 1.  The right search space is therefore sets of 2-loops covering "
     "every rotation class -- already implemented as "
     "`saturated6.saturated(n, v, cls_of)`.  Not universal: 872-nonstandard "
     "has A = 2..5 and is not a union of loops; but the whole 43,096-string "
     "treelike corpus has S in {15,20,25}, all multiples of n-1.",
     lambda r: False,
     lambda r: True),

    ("FAM1", "[MEAS]",
     "delta(end of arc) stays in the arc's FAMILY iff the arc is full",
     "Forward half is [THM]: a full arc ends at sigma^(n-1)(g) and delta of "
     "that is g.a with a in H = <a,b>, so it stays in the coset.  Converse "
     "measured over all 720 permutations at n = 6 and all n-1 partial lengths: "
     "length n gives family shift 0 every time, lengths 1..n-1 give shifts "
     "spread uniformly over 1..n-1 (144 each) and NEVER 0.  This is a sharper "
     "form of arsenal 3.4 (splits are never intra-family).  CONSEQUENCE, and "
     "the reason every search stalls at the exact cover: that arc set is one "
     "whole family with every arc full, so all its delta-exits stay inside the "
     "family and already land on arc starts -- its 24 components are 24 "
     "disjoint cycles.  Adding ONE cut makes a piece partial, its exit leaves "
     "the family, and no other family's loops are entered, so it lands on "
     "nothing.  Measured: over all 600 single cut additions delta(comps) = 0 "
     "every time.  So NO single-class move can reduce comps there, and the "
     "minimal move that can is the two-cut `graft` of `code/graft.py`.  "
     "Champions are family-mixed by contrast -- houston 872 spreads its arc "
     "starts 50/35/10/5/20/25 over all six families.",
     lambda r: False,
     lambda r: True),

    ("CH3", "[THM]",
     "T >= S + comps + (p - 1)  -- ordering-free, and it BEATS HPV",
     "CH2 gives Y >= p-1 and IN5 gives B >= comps; IN5 is false in general but "
     "SIG2X makes it valid against the OPTIMUM, which is the only place a lower "
     "bound is used.  Every term reads the arc SET, so the bound is "
     "ordering-free.  Measured by `code/pbound.py`: 0 violations on the 1,030 "
     "n = 6 census strings and 1,029 of them EXACTLY TIGHT; and the minimum "
     "over ALL 10,068 exact covers is 29 -- the true n = 6 optimum -- against "
     "HPV's floor of 24 at the same rung.  At an exact cover it evaluates to "
     "(n-1)(n-3)! - 1, the Egan-1 line, which Chain-Count and S5 also give "
     "there but only under their own hypotheses.  This is the first "
     "ordering-free bound here to beat HPV and it corrects A3; see "
     "notes/pbound.md.  Not row-wise: p is not carried in the corpus rows.",
     lambda r: False,
     lambda r: True),

    ("FLOOP", "[THM]",
     "F_loops >= v - A - 2S,  F_loops = #(saturated loops with all arcs full)",
     "A = sum over entered loops of (n-1 - a_L), so at most A of the v entered "
     "loops are unsaturated and #saturated >= v - A.  A saturated loop fails to "
     "be all-full only by containing a partial arc, and the number of loops "
     "containing one is at most n_partial = S + m (ID4), which is <= 2S since "
     "m <= S.  Subtracting gives the bound.  Holds 1275/1275 on the n = 6 and "
     "n = 7 census.",
     lambda r: False,
     lambda r: True),

    ("RES", "[MEAS]",
     "if every delta-component has (size - 1) = r (mod n-1) for a SINGLE r, "
     "then longest free chain <= ord(a^r . b); hence p >= ceil(comps/that).  "
     "Mixed residues: no cap.",
     "The correct version of what PFLOOP got wrong, and it DERIVES the cap "
     "instead of asserting it.  Traversing a component of l arcs applies "
     "a^(l-1), then the free join applies b, so each step of a free chain is "
     "the group element a^((l-1) mod (n-1)) . b -- ord(a) = n-1, so only the "
     "residue matters.  Share a residue and every step is the SAME element g, "
     "so k steps apply g^k and the chain must close by ord(g); mix residues and "
     "nothing forces a stop.\n"
     "Measured, and TIGHT: n=6 r=4 cap ord(a^4.b)=4 longest=4 (2 strings); "
     "n=7 r=5 cap ord(a^5.b)=5 longest=5 (6 strings); 0 violations.  The "
     "dichotomy itself is exact in both directions, 1269/1269 (n=6: 2 "
     "single-residue vs 1024 mixed; n=7: 6 vs 237).\n"
     "Note r = n-2 in every uniform case observed -- components are whole "
     "loops of n-1 arcs -- and there a^(n-2).b IS s, so the cap is ord(s) = "
     "n-2 by 3.5 [THM].  That recovers the arsenal's constant as the special "
     "case it always was.  Other residues give DIFFERENT and sometimes much "
     "stronger caps: ord(a^r.b) at n=7 is [6,4,6,5,2,5] for r=0..5, so a "
     "uniform-residue-4 arc set would have longest <= 2.\n"
     "The 5906 champion has residues {3,5} and hence no cap at all, which is "
     "how it reaches longest = comps = 18 with every free join still om.  "
     "CONSEQUENCE for CH3: the v-to-p bridge holds under residue-uniformity, "
     "true at S = 0 and false at champions, so v <= 141 stays open with a "
     "sharp statement of what must be shown.  Not row-wise: needs the "
     "component-size multiset.",
     lambda r: False,
     lambda r: True),

    ("RUNG0", "[THM]",
     "at v = (n-2)! the CH3 bound is EXACTLY (n-1)(n-3)! - 1 = Egan_T - 1",
     "A chain of existing pieces, no search.  v = (n-2)! forces A = 0 and S = 0 "
     "(arsenal 1: R >= (n-1)! always and R = (n-1)v - A = (n-1)! - A).  S = 0 "
     "means every class is covered once, so every arc is FULL; then every "
     "entered loop has a_L = n-1, i.e. saturated and all-full, and by S1 each "
     "closes into a delta-cycle of n-1 arcs.  So comps = (n-2)! and every "
     "component has n-1 arcs, giving the single residue r = n-2 -- and by RES "
     "the cap is ord(a^(n-2).b) = ord(s) = n-2 (3.5 [THM]).  Hence "
     "p >= (n-2)!/(n-2) = (n-3)! and\n"
     "    CH3 = 0 + (n-2)! + (n-3)! - 1 = (n-1)(n-3)! - 1 = Egan_T - 1.\n"
     "Matches measurement exactly: 29 at n = 6, 143 at n = 7.  CONSEQUENCE: at "
     "n = 7 this rung gives 143 > 141, so **v = 120 cannot produce a 5905** -- "
     "the first rung of that question closed by proof rather than by search.  "
     "It also explains why the Egan-1 line keeps appearing at exact covers: it "
     "is the residue cap, not a coincidence.",
     lambda r: False,
     lambda r: True),

    ("RUNG1", "[MEAS]",
     "at v = (n-2)!+1 with A = 0 the CH3 bound is EXACTLY Egan_T + 2",
     "Every arc set at this rung with A = 0 is an exact cover plus ONE loop, so "
     "the family is small enough to exhaust.  Done for one base cover at each "
     "n: **120/120 at n = 6 and 720/720 at n = 7, every single one identical** "
     "-- S = n-1, comps = (n-2)! - (n-4), p = (n-3)!, giving\n"
     "    CH3 = (n-1) + (n-2)! - (n-4) + (n-3)! - 1 = Egan_T + 2.\n"
     "32 at n = 6 (needs <= 28 to threaten 872: margin 4) and 146 at n = 7 "
     "(needs <= 141 to threaten 5906: margin 5).  So this rung is CLOSED for "
     "A = 0, exhaustively over the additions though for one base cover.  "
     "A > 0 at the same rung (A <= n-1 there, since S = n-1-A >= 0) is NOT "
     "covered; by A2 any v = (n-2)!+1 arc set has CH3 >= v + p - 1, so closing "
     "it in general needs p >= (n-3)! + ... i.e. p >= 22 at n = 7.",
     lambda r: False,
     lambda r: True),

    ("VRIG", "[MEAS]",
     "v is RIGID under single-class re-cuts at the n = 7 champion: 3588 tried, "
     "0 changed it",
     "Dropping v means VACATING a loop, and a single-class re-cut moves one arc "
     "start.  At the 5906 champion the loops hold 4 or 6 arc starts (4 loops "
     "with 4, 138 saturated with 6; A = 8 = 4 x 2), so emptying even the "
     "thinnest needs FOUR classes re-cut at once.  Measured: 3588 single-class "
     "re-cuts, none changes v.\n"
     "This is why every search in notes/pbound.md from the champion found "
     "nothing.  With A2 tight everywhere measured, CH3 = S + comps + p - 1 = "
     "v + p - 1, so beating the champion needs v + p <= 142 against its 143, "
     "and the precise target is\n"
     "    v = 141, S = 124, A = 2, comps = 17, p = 1  ->  CH3 = 141.\n"
     "That is the champion with one fewer loop entered and one fewer component. "
     "It is at least a 4-class move away, and the move set used was 1-class -- "
     "so those searches were structurally incapable of reaching it, not merely "
     "unlucky.  Compare LOOP1: optima are >= 3 loop-swaps apart, same rigidity "
     "seen from the arc-set side.",
     lambda r: False,
     lambda r: True),

    ("FORCE", "[THM]",
     "every free-join state has at most ONE core out-edge, and it lands "
     "exactly on start.b -- the correct, length-gated CH1.  1463/1463",
     "CH1 ('free-join out-degree <= 1') is false, even on the census.  The "
     "provable statement is LENGTH-GATED.  Struct.exits(g, l) returns the 3! "
     "weight-3 targets of a block of l arcs, each with a CAP -- how far the "
     "next block may run before re-entering a class this one burned -- and "
     "coset_lemma.py verifies that exactly one target survives cap >= l' "
     "precisely when l + l' >= 2n-3, the survivor being om.  Call an edge CORE "
     "when the exit arc is full and l + l' >= 2n-3, FRINGE otherwise.  Then om "
     "is a single group element, so the core target is the single permutation "
     "start.b, and distinct components have distinct arcs and hence distinct "
     "entries -- so at most one core out-edge per state.\n"
     "Gate (`code/freejoin.py`): max CORE out-degree is 1 at n = 5, 6 and 7, "
     "0 exceptions in 1463 strings, and every core edge lands on start.b.  "
     "NOTE the convention: exits() measures from the block's last ARC START, "
     "not its end, so the om target is start.b and end.b is simply the wrong "
     "group element.\n"
     "COROLLARY: out-degree >= 2 forces a FRINGE edge, and a fringe edge needs "
     "an incomplete block at one end (l = l' = n-1 gives 2n-2 >= 2n-3, always "
     "core).  That is the mechanism RES was reaching for through residues -- "
     "and lengths, unlike residues, do not go mixed at the champions.",
     lambda r: False,
     lambda r: True),

    ("FRINGE", "[MEAS]",
     "core-only free chains cap at exactly n-2, but fringe edges are ABUNDANT, "
     "so the core/fringe split explains p and does not bound it",
     "With FORCE in hand the natural bound is p >= (core-runs) - (fringe edges "
     "used) >= ceil(comps/(n-2)) - F_used, since core edges alone form a "
     "functional graph.  Measuring L(f) = the longest free chain, in "
     "components, reachable using exactly f fringe edges (`code/freejoin.py "
     "--chains`), over the whole corpus:\n"
     "    n = 5   f: 0->3  1->3  2->3\n"
     "    n = 6   f: 0->4  1->4  2->7  3->7  4->9  5->9  6->9\n"
     "    n = 7   f: 0->5  1->5  2->8  3->9  4->10  5->13  6->14  7->18 ...\n"
     "L(0) = n-2 EXACTLY at all three n -- the Pentad cap recovered as the "
     "f = 0 case, which is the honest content of RES and of CHLB.  Past that, "
     "L grows at roughly 1.4 components per fringe edge at n = 7.\n"
     "THE ROUTE FAILS, and cleanly.  The bound needs an upper bound on fringe "
     "edges, and there is none: fringe edges are 75% of all free edges across "
     "the corpus, and at the 5906 champion specifically there are **118 fringe "
     "against 16 core**, with the 18-component chain needing 10 of them.  A "
     "budget of 10 is not scarcity.  So the core/fringe split says WHY long "
     "chains are possible -- they buy fringe edges, which need incomplete "
     "blocks, which need splits -- but supplies no numerical bound.\n"
     "Compare Chain-Count's general form c_{n-1} <= (n-2)(1 + Y + (B - "
     "c_{n-1})), recorded in the arsenal as VACUOUS away from B = (n-2)!.  "
     "This is the same wall reached from the free-join side: the f = 0 case is "
     "sharp and everything above it is unbounded.  Registered so the route is "
     "not tried a third time.",
     lambda r: False,
     lambda r: True),

    ("SLOT", "[THM]",
     "A is exactly the number of FREE GENERATOR SLOTS in the entered loops: "
     "A = sum_L (n-1 - a_L).  1463/1463",
     "One line from the Split Identity R = (n-1)v - A: an entered loop has "
     "n-1 generator positions and a_L of them are arc starts, so the unused "
     "positions number sum_L (n-1 - a_L) = (n-1)v - R = A.  Verified on every "
     "string on disk, 1463/1463.\n"
     "It is worth stating because it turns A from a bookkeeping residual into "
     "the RESOURCE that every arc-set move spends.  Re-cutting a class moves "
     "one arc start, and it can only move into a free slot; there are exactly "
     "A of them.  Two consequences:\n"
     "  * Vacating a loop L -- the only way to lower v by re-cutting -- means "
     "relocating all a_L of its starts into free slots of OTHER entered loops. "
     "L itself owns n-1-a_L of the A slots and they die with it, so the move "
     "needs A - (n-1-a_L) >= a_L, i.e. **A >= n-1**.  Below that, v cannot "
     "fall at all, by counting alone.\n"
     "  * Lowering v by one costs exactly n-1 of A, since "
     "A' = (n-1)(v-1) - R = A - (n-1).  So from any arc set, re-cutting can "
     "lower v at most floor(A/(n-1)) times.\n"
     "This is the general form of VLOCK, which measured the finer obstruction. "
     "At the 5906 champion A = 8 >= 6, so counting does NOT forbid the move -- "
     "the four thin loops hold 2 free slots each, and what blocks it is that "
     "they are class-disjoint, so no displaced start has a rotation landing in "
     "another's slot.  Counting says which arc sets are even candidates; "
     "VLOCK says none of the 237 champions is one.",
     lambda r: False,
     lambda r: True),

    ("CH3LOC", "[EXH]",
     "both champions are STRICT local minima of CH3: every single-cut "
     "neighbour is worse, 625/625 at n = 6 and 4442/4442 at n = 7",
     "VRIG measured that single-class re-cuts cannot move `v` at the n = 7 "
     "champion.  That is one coordinate; `code/nbhd.py` prices the whole "
     "radius-1 neighbourhood EXACTLY -- every add or remove of a single cut, "
     "with `p` verified by chainer.min_chains, no fallbacks admitted -- and "
     "gets the complete histogram:\n"
     "    n = 6  houston 872  CH3 = 29 : neighbourhood {30: 42, 31: 583}\n"
     "    n = 7  5906 champ   CH3 = 142: neighbourhood {143: 145, 144: 3122, "
     "145: 1175}\n"
     "So neither champion has even a TYING neighbour, let alone a better one.  "
     "This replaces 'the annealer found nothing' (notes/pbound.md 3c), which "
     "was a statement about the sampler, with a complete statement about the "
     "point: 142 is a certified local minimum of CH3 under single-cut moves.\n"
     "The sharper reading is the trade-off table, which is the same at both n:\n"
     "    n = 6:  v = 29 -> min p = 2,   v = 30 -> min p = 1\n"
     "    n = 7:  v = 142 -> min p = 2,  v = 143 -> min p = 1\n"
     "The champion itself is v = 142, p = 1.  So `p = 1` at the champion's `v` "
     "is an ISOLATED point: every neighbour that holds `v` fixed breaks the "
     "single free chain, and every neighbour that keeps `p = 1` pays a loop.  "
     "That is exactly the v-p trade-off CH3 needs, seen locally and off the "
     "census -- and it is why the bound is tight here and nowhere near tight "
     "generically (5a).  No neighbour has v <= 141 at all, which is VRIG "
     "re-measured over the complete neighbourhood rather than 3588 of it.",
     lambda r: False,
     lambda r: True),

    ("VPMIN", "[MEAS]",
     "min (v + p) over EVERY string on disk is T_opt + 1: 8 at n = 5, 30 at "
     "n = 6, 143 at n = 7",
     "`CH3 <= T` bounds `v + p` from ABOVE, so nothing in the theory stops a "
     "long, sloppy superpermutation from having a small `v + p` -- and one with "
     "`v + p < 143` at n = 7 would put min CH3 below 142 and kill the whole "
     "reduction.  `code/vplus.py` prices all 1,463 strings on disk, optimal or "
     "not, with `p` verified (0 unverified rows at any n):\n"
     "    n = 5   188 strings   min v+p =   8   at 153-chaffin  (v=6,  p=2)\n"
     "    n = 6  1030 strings   min v+p =  30   at houston 872  (v=29, p=1)\n"
     "    n = 7   245 strings   min v+p = 143   at the champion (v=142,p=1)\n"
     "No refutation, so the programme survives -- but note WHY this was never "
     "going to refute it: CH3 is exactly tight on 1,458 of the 1,463, so a real "
     "string cannot have v + p - 1 below its own T, and every string has "
     "T >= T_opt.  The measurement is a consistency check, not evidence.\n"
     "What IS evidence is the per-v floor, which is off-distribution wherever "
     "the corpus is thin:\n"
     "    n = 5   v: 6->p 2   7->1   8->1\n"
     "    n = 6   v: 24->6   28->2   29->1   30->1\n"
     "    n = 7   v: 120->24  140->4  142->1  144->1\n"
     "`p >= T_opt + 1 - v` fits every row and is EXACT at n = 5 and n = 6 at "
     "every v -- but at n = 7 it is slack by 1 at v = 120 and v = 140 and tight "
     "only at v = 142.  So the law that would close 5905 is pinned by a single "
     "point, the champion, and the corpus is empty on 121 <= v <= 139.",
     lambda r: False,
     lambda r: True),

    ("VLOCK", "[MEAS]",
     "NO n = 7 champion can lower v by re-cutting -- 237/237, and the "
     "class-disjointness mechanism covers only 211 of them",
     "VRIG showed single-class moves cannot change v.  The natural fix is the "
     "4-class move that VACATES a thin loop.  Vacating loop L means re-cutting "
     "each of L's arc-start classes so its start lands in a free generator "
     "slot -- and the slot must belong to an already-ENTERED loop, since "
     "landing in an unentered one just puts back the v it removed.  Saturated "
     "loops have no free slot, so the targets are exactly the other THIN "
     "loops.\n"
     "At the 5906 champion: 138 loops saturated (a_L = 6), four with a_L = 4, "
     "and **0 usable alternatives in all 16 classes**.  The reason there is "
     "that the four thin loops are PAIRWISE CLASS-DISJOINT -- 0 shared classes "
     "in all six pairs -- so the free slots sit in classes the other thin "
     "loops never meet.  Compare 3.5: loops in an <s>-orbit are pairwise "
     "class-disjoint, the same phenomenon.\n"
     "CORRECTION, `code/vlock.py` over all 237 census champions: that "
     "mechanism is NOT universal.  Class-disjointness of the thin loops holds "
     "in 211 of the 237, and the other 26 do have usable alternatives -- 3 of "
     "them in 15 strings, 6 in 11.  So the one-witness version of this claim "
     "was reading a property of the point as a property of length 5906.\n"
     "The lock survives anyway, for a sharper reason.  Vacating L needs EVERY "
     "one of its starts to have somewhere to go, and the best any string "
     "manages is `movable - needed = -3`, in all 26 -- one start of a "
     "four-start thin loop can move and the other three cannot.  So NO thin "
     "loop is fully movable in ANY champion: **237/237 locked**.\n"
     "CONSEQUENCE: the CH3 target v=141, S=124, comps=17, p=1 is unreachable "
     "by re-cutting from any known n = 7 optimum, at any move width.  Getting "
     "there needs a different arc set entirely, not a perturbation of these.",
     lambda r: False,
     lambda r: True),

    ("A2DEC", "[THM]",
     "exact decomposition: comps = sum_L c_L - e_inter + (cyc - F), so A2 <=> "
     "e_inter - (cyc - F) <= S + sum_L (c_L - 1)",
     "c_L = components of loop L's arcs under INTRA-loop delta edges only.  A "
     "full arc's exit is start.a, inside its own loop; a partial arc's exit "
     "leaves the loop (indeed the family, FAM1).  So the intra-only graph has "
     "sum_cL = R - e_intra + cyc_intra components, and cyc_intra = F by S1 (an "
     "all-full saturated loop is exactly an intra cycle).  Subtracting from "
     "comps = R - e_intra - e_inter + cyc gives the identity.  Since c_L >= 1 "
     "for every entered loop, sum_cL >= v, and A2 follows from the stated "
     "inequality.  This is the honest frame for A2; REF1 refuted only the crude "
     "form `e_inter <= S` (1270/1275 violate it), which is not what A2 needs.",
     lambda r: False,
     lambda r: True),

    ("A2LOC", "[THM]",
     "A2 is EQUIVALENT to the local counting inequality "
     "m <= sum_L (c_L - 1) + D + (cyc - F), with equality iff A3",
     "From A2DEC, e_inter = n_partial - D = S + m - D where D counts partial "
     "arcs whose delta-exit is not an arc start.  Substituting:\n"
     "    comps = sum_cL - S - m + D + (cyc - F)\n"
     "so comps >= v - S is exactly m <= (sum_cL - v) + D + (cyc - F), and "
     "comps = v - S (A3) is exactly equality.  Verified both ways: on the 1275 "
     "n=6,7 census strings the two sides agree EXACTLY, 0 gap on every one "
     "(which is A3); on off-distribution loop systems where A3 fails the slack "
     "is strictly positive and grows -- 2, 10, 28, 60 at v = 121, 125, 131, "
     "141.\n"
     "WHY THIS IS PROGRESS: 'comps >= v - S' compares two global graph "
     "quantities and every bounding attempt (REF1, CLM) has failed because A3 "
     "makes it tight.  The restatement is a count of LOCAL objects -- each "
     "multiply-covered class must be matched by an intra-loop fragmentation, a "
     "dead partial exit, or an excess delta-cycle.  That is an injection to "
     "look for, not a bound to prove, and it is the first form of A2 that "
     "admits one.",
     lambda r: False,
     lambda r: True),

    ("A2FOUR", "[THM]",
     "A2  <=>  v <= S + W + D + cyc,  four elementary counts",
     "Call g in K BROKEN if its arc is partial or g.a is not an arc start.  Loop "
     "L then has a_L - b_L intra edges, so c_L = b_L when b_L >= 1 and c_L = 1 "
     "(a cycle) when b_L = 0 -- and b_L = 0 is exactly the all-full saturated "
     "loops, F of them.  Hence sum(c_L - 1) = sum b_L - (v - F) = "
     "(n_partial + W) - v + F, where W counts FULL arcs whose next loop "
     "generator is not an arc start.  Substituting into A2LOC with "
     "n_partial = S + m, the m and the F both cancel and A2 becomes\n"
     "    v <= S + W + D + cyc.\n"
     "Verified: 1275/1275 census strings with slack EXACTLY 0 (which is A3), "
     "and strictly positive slack off-distribution -- 2, 10, 28, 60 at "
     "v = 121, 125, 131, 141, agreeing with the A2LOC numbers term for term.\n"
     "This is A2 stripped to counting.  What a proof now needs is a CHARGING "
     "of each entered loop to one of the four: an all-full saturated loop pays "
     "with its own delta-cycle; any other loop has a broken generator, paying "
     "to W if the break is a gap after a full arc and to S if it is a partial "
     "arc.  The gap is that a multiply-covered class C has mu_C partial arcs in "
     "mu_C distinct loops but only contributes mu_C - 1 to S, so ONE loop per "
     "such class is unpaid -- and must be absorbed by D or by an excess cycle.  "
     "That residue is exactly m - sum(c_L - 1), measured at 0..13.",
     lambda r: False,
     lambda r: True),

    ("PATHTAIL", "[THM]",
     "comps = cyc + W + D",
     "The delta-graph has in- and out-degree <= 1, so every component is a path "
     "or a cycle, and every PATH has exactly one tail -- an arc with no "
     "delta-successor in K.  The tails are precisely the W arcs (full, with "
     "g.a not in K) and the D arcs (partial, dead), since those are the two ways "
     "an arc's exit can miss K.  Hence #paths = W + D and comps = cyc + W + D.  "
     "Verified 1275/1275 on the n=6,7 census.  This makes A2FOUR "
     "(v <= S + W + D + cyc) an immediate restatement of A2 (comps >= v - S) "
     "rather than a separate derivation.",
     lambda r: False,
     lambda r: True),

    ("SHARE", "[THM]",
     "two SATURATED loops with b_L = 1 sharing a multiply-covered class C share "
     "no other class",
     "Saturation means every generator of the loop is an arc start, so a shared "
     "class D would carry an arc start in both loops, giving mu_D >= 2 -- so "
     "both arcs at D are partial, hence broken.  Each loop would then have two "
     "broken generators (D's and C's), contradicting b_L = 1.  So the only "
     "shared class is C.\n"
     "THE HYPOTHESIS IS REAL: b_L = 1 does NOT force saturation.  An unsaturated "
     "loop with a single run of present generators also has b_L = 1, its one "
     "broken generator being the run end, and then it can meet a class without "
     "having an arc start there.  Measured over the 581 dangerous classes of "
     "A2RESCUE: the sharing conclusion holds for 577 and FAILS for 4, and the "
     "4 are exactly the unsaturated ones.  Recorded because the first draft of "
     "this lemma omitted the hypothesis.",
     lambda r: False,
     lambda r: True),

    ("A2PATH", "[THM]",
     "b_L = 1  =>  L's arcs form a single intra-path ending at the broken arc, "
     "and every inter edge into L lands on that path's HEAD",
     "Two elementary facts, both needed for the last step of A2.\n"
     "(1) b_L = 1 means exactly one generator of K n L is broken, so every "
     "other h has arc(h) full and h.a in K, giving an intra edge h -> h.a.  "
     "That is |K n L| - 1 edges on |K n L| arcs, and the broken one has no "
     "intra out-edge, so they chain into a single PATH ending at it -- no cycle. "
     "Verified 32,358/32,358 such loops in the n=6,7 census.\n"
     "(2) The delta-graph has in-degree <= 1 (delta is injective and arc starts "
     "are distinct).  Every arc of that path except the head already has an "
     "intra in-edge, so an inter edge into L can only target the HEAD.  "
     "Verified: 30,518 inter edges into b_L = 1 loops, every one into the head, "
     "ZERO into the middle.\n"
     "CONSEQUENCE, and the reason this matters: for a dangerous class the mu "
     "paths P_1..P_mu have out-degree <= 1 (only the broken arc exits L) and "
     "in-degree <= 1 (only the head receives), so they form disjoint CHAINS AND "
     "CYCLES.  If they close among themselves that is a delta-cycle and A2RESCUE "
     "holds; if they chain, the last exit is dead and A2RESCUE holds.  The "
     "remaining gap is to rule out all mu paths chaining OUT of X with live "
     "exits -- see notes/pbound.md 7e.",
     lambda r: False,
     lambda r: True),

    ("A2RESCUE", "[THM]",
     "PROVED: a multiply-covered class whose loops ALL have b_L = 1 meets a "
     "delta-cycle or a dead exit",
     "PROOF.  Let C's arcs be alpha_1..alpha_mu in cyclic order round C's ring, "
     "alpha_p in loop L_p with start s_p and end e_p.  Consecutive arcs tile the "
     "ring, so s_{p+1} = sigma(e_p), i.e. e_p = sigma^{-1}(s_{p+1}).  By the "
     "DEFINITION of a = c^(n-1)d we have delta(sigma^{-1}(x)) = x.a for every x "
     "(verified 120/120, 720/720, 5040/5040 at n = 5, 6, 7), hence\n"
     "        delta(e_p) = delta(sigma^{-1}(s_{p+1})) = s_{p+1} . a.\n"
     "Case (i): s_{p+1}.a not in K for some p.  Then alpha_p's delta-exit misses "
     "K, so alpha_p is a dead partial arc in L_p -- a dead exit meeting C.  "
     "Done.\n"
     "Case (ii): s_{p+1}.a in K for every p.  Since a acts within a loop, "
     "s_{p+1}.a is an arc start of L_{p+1}.  By A2PATH the arcs of L_{p+1} form "
     "a single intra-path ending at s_{p+1}, and its head is the unique arc with "
     "no intra in-edge; an arc at h has one iff h.a^{-1} is in K and unbroken, "
     "and s_{p+1} is the only broken generator, so the head is exactly "
     "s_{p+1}.a.  Thus alpha_p's exit lands on P_{p+1}'s head.  Holding for "
     "every p, the paths close: P_1 -> P_2 -> ... -> P_mu -> P_1 is a "
     "delta-cycle meeting every L_p.  Done. QED\n"
     "(The two cases are exhaustive and (ii) forces saturation: an unsaturated "
     "b_L = 1 loop must have its gap immediately after s_{p+1}, i.e. "
     "s_{p+1}.a not in K, which is case (i).)\n"
     "Measured beforehand at 581/581 -- 533 by cycle, 48 by dead exit, 0 by "
     "neither -- and the instrumentation showed all 581 have mu = 2, every exit "
     "landing on the other path's head in ONE hop, which is what exposed the "
     "identity.\n"
     "WHAT IT SETTLES.  It kills the EXTREME case of Hall: no class in C(X) can "
     "have all its loops at b_L = 1, since such a class brings a private token "
     "(a cycle or a dead exit) to X.  So every class in C(X) has at least one "
     "loop with b_L >= 2.  It does NOT by itself prove Hall -- an earlier note "
     "called this 'the whole Hall condition', which was an overstatement.  What "
     "remains is that those surpluses must cover all of C(X) without contention: "
     "a loop with b_L = k can absorb k-1 classes, so Hall in general is a "
     "CAPACITY-MATCHING statement one level down.  See notes/pbound.md 7g.",
     lambda r: False,
     lambda r: True),

    ("A2MATCH", "[MEAS]",
     "the A2 charging admits a PERFECT matching on every string tested -- Hall "
     "holds, so the injection strategy is viable",
     "A2FOUR reduces A2 to v <= S + W + D + cyc; the natural proof injects the v "
     "entered loops into those tokens.  A2HALL showed 1.11% of multiply-covered "
     "classes have no locally alternative charge, so it was genuinely open "
     "whether Hall's condition survives contention between classes.  It does.  "
     "`code/a2hall.py` builds the bipartite token graph (S tokens shared by a "
     "class's mu_C loops; W, D private; cycles shared by the loops they touch) "
     "and runs Kuhn's algorithm: **deficiency v - (matching size) = 0 on all "
     "213 census strings tested**, and since slack is identically 0 there "
     "(that is A3) these are PERFECT matchings.\n"
     "Structure of the obstruction, from the alternating closure: the minimal "
     "tight sets PARTITION the loops -- 18 blocks at the n = 7 champion with "
     "sizes 1x8, 2x2, 3, 4x2, 5x2, 10, 48, 51 summing to v = 142, and 4 blocks "
     "at houston 872.  Singleton blocks are loops owning a private token (a W "
     "gap or their own delta-cycle); the large blocks are where S tokens chain "
     "loops together.  So proving A2 by charging now needs exactly: every tight "
     "block X has |N(X)| >= |X|.  That is a statement about one block, not the "
     "whole arc set.",
     lambda r: False,
     lambda r: True),

    ("A2SEARCH", "[MEAS]",
     "no A2 counterexample found: slack S + W + D + cyc - v never went below 0 "
     "in 12,000 directed iterations",
     "A2 is the load-bearing conjecture under CH3's reduction, so before "
     "attempting a proof it was worth trying to refute it.  A2FOUR makes the "
     "slack computable in one pass, so `code/a2hall.py --search` minimises it "
     "directly by re-cutting classes.  Seeded at the n = 7 champion and at "
     "houston 872, 6,000 iterations each: the lowest slack found was **0** in "
     "both, never negative.  Combined with 1275/1275 census strings at slack 0 "
     "and strictly positive slack off-distribution, A2 survives every attempt "
     "made here to break it.",
     lambda r: False,
     lambda r: True),

    ("A2HALL", "[MEAS]",
     "98.9% of multiply-covered classes have a loop with an alternative charge; "
     "1.1% do not, so A2's charging is a MATCHING problem, not a local argument",
     "A2FOUR reduces A2 to charging each entered loop to one of S, W, D, cyc.  "
     "The only obstruction is that a multiply-covered class C has mu_C partial "
     "arcs in mu_C distinct loops but funds only mu_C - 1 of them, so one loop "
     "per class needs an ALTERNATIVE charge: a second broken generator in that "
     "loop (b_L >= 2), a dead exit, or a spare cycle.  Measured over 52,318 "
     "multiply-covered classes in 1,275 census strings:\n"
     "    0 of its loops have an alternative:    581  (1.11%)\n"
     "    1                                   29,093  (55.61%)\n"
     "    2                                   22,493  (42.99%)\n"
     "    3                                      151  (0.29%)\n"
     "So the local charge exists for 98.9% of classes but NOT all -- the 1.1% "
     "must be absorbed by D or an excess cycle.  CONSEQUENCE: A2 cannot be "
     "proved by a purely local per-class argument.  What is needed is Hall's "
     "condition on the bipartite graph (multiply-covered classes) x (available "
     "charges), since distinct classes may also contend for the SAME "
     "alternative loop.  That is the precise remaining obstacle, and it is a "
     "matching statement rather than a counting one.",
     lambda r: False,
     lambda r: True),

    ("CLM", "[MEAS]",
     "sum_L (c_L - 1) <= m,  1275/1275  -- and this is why A2 resists",
     "Measured on the n=6,7 census: slack `sum(c_L - 1) - m` runs from -13 to "
     "**0**, never positive, mean -3.5.  The natural bound on the inter-loop "
     "edge count is e_inter <= n_partial = S + m (only partial arcs leave their "
     "loop).  Feeding that into A2DEC would need `sum(c_L - 1) >= m` -- and the "
     "truth is the OPPOSITE inequality.  So the crude chain overshoots by "
     "exactly m - sum(c_L - 1) >= 0.\n"
     "The deeper reason A2 resists proof: A3 says comps = v - S EXACTLY on "
     "every corpus string, so A2 is an equality in disguise and NO chain of "
     "inequalities carrying slack can establish it.  What is missing is "
     "precisely e_inter <= S + sum(c_L - 1) + (cyc - F), an exact accounting of "
     "the inter-loop edges, not a bound on them.",
     lambda r: False,
     lambda r: True),

    ("PFLOOP", "[REF]",
     "p >= ceil(F_loops/(n-2))   -- FALSE",
     "The attempted bridge from `v` to `p` for CH3: if few loops are entered "
     "then many are all-full (FLOOP), each is a delta-cycle (S1), and chains "
     "among them were supposed to cap at ord(s) = n-2.  Measured: **171 "
     "violations** on the n=6,7 census.  Witness 7_5906_derived_06f4ba2c8122 "
     "has F_loops = 16 and p = 1 (verified exact) against a claimed 4.  The "
     "cap is LENGTH-SPECIFIC: s = a^(n-2).b, so 'om-chains cap at ord(s)' needs "
     "every block in the chain to have that one length, which is why S5's "
     "derivation is sound for all-full loops (uniform, n-1 arcs) and why this "
     "generalisation is not -- a chain can thread all-full components together "
     "through non-uniform blocks and evade the cap entirely.  With this dead, "
     "CH3's reduction to `v + p >= 143` at n = 7 has no mechanism for v <= 141.",
     lambda r: False,
     lambda r: True),

    ("CHLB", "[REF]",
     "Y >= ceil(comps/(n-2)) - 1   -- NOT admissible",
     "The bound `gen2.evaluate(fast=True)` annealed against, on the grounds "
     "that om-chains cap at ord(s) = n-2.  That cap only binds where the "
     "weight-3 exit is FORCED onto om, i.e. l + l' >= 2n-3 (arsenal 3.2); at a "
     "champion the arcs are partial, nothing is forced, and free chains run "
     "long -- the n = 7 champion's 18 delta-components form ONE chain.  Fails "
     "on 1,273 of 44,672 rows (n=6: 1024, n=7: 247, n=5: 2); worst is "
     "5912-derived with comps = 120, Y = 3 against a claimed 23.  It is worse "
     "than merely loose: it OVER-prices champions (n = 7 record at T = 145 "
     "against a true 142) while UNDER-pricing the exact cover (29 against 30), "
     "so the search was steered toward the exact cover by 4.  Replaced by CH2.",
     lambda r: "comps" in r,
     lambda r: r["Y"] >= max(0, -(-r["comps"] // (r["n"] - 2)) - 1)),

    ("CH2", "[THM]",
     "Y >= p - 1,  p = fewest free chains covering the delta-components; "
     "hence T >= S + comps + p - 1 against the optimum",
     "By CH1 the free-join graph has out-degree <= 1, so free continuation is "
     "forced and any chaining decomposes into maximal free chains.  Every join "
     "BETWEEN chains costs at least 1: a chain's free successor is unique and "
     "lands in a component the chain already covers, so it is never another "
     "chain's head.  With p the minimum chain count, Y >= p - 1.  Adding "
     "B >= comps -- valid against the optimum by SIG2X -- gives the T form.  "
     "This is admissible where CHLB is not: it returns 0 at the n = 7 champion "
     "(true Y = 0) and 5 at the n = 6 exact cover (true 6), in ~1-4 ms.  It "
     "does NOT beat HPV: champions have p = 1, so it collapses to T >= v, "
     "exactly as A3 predicts.  Its value is as a search bound, and as the "
     "characterisation **Y = 0 <=> p = 1 <=> the delta-components thread into "
     "a single weight-3 chain**.  `code/chainer.py: min_chains/lower_bound`.",
     lambda r: False,
     lambda r: True),

    ("C6b", "[CONJ]",
     "B = comps at an optimum (the delta-graph is saturated)",
     "An optimum uses every available free delta-edge; a spare one would mean "
     "paying a costly jump where a free one was on offer.  43,096/43,096 at "
     "n = 6 and every record in the census.",
     lambda r: "comps" in r and r["length"] <= BEST.get(r["n"], 0),
     lambda r: r["B"] == r["comps"]),

    ("REF1", "[REF]",
     "inter-loop delta-edges <= S   -- FALSE",
     "The natural route to proving A2 (contract each loop, bound the quotient "
     "edges).  Refuted by 5907-jupiter: 239 inter-loop edges against S = 120.",
     lambda r: False,
     lambda r: True),

    ("A3", "[MEAS]",
     "S + comps = v   (this PARTICULAR ordering-free quantity equals HPV)",
     "True on all 179 measured strings, FALSE on constructed walks -- kept as "
     "a record-only regularity.  Its one-sided half is A2.  IMPORTANT "
     "CORRECTION: this used to be read as 'no ordering-free invariant beats "
     "HPV', which is FALSE.  It says only that `S + comps`, whose minimum over "
     "arc sets is exactly (n-2)! = HPV, cannot.  Adding the free-chain count "
     "gives CH3, `T >= S + comps + p - 1`, still ordering-free, whose minimum "
     "over all 10,068 n = 6 exact covers is 29 against HPV's 24.",
     lambda r: "comps" in r,
     lambda r: r["S"] + r["comps"] == r["v"]),

    ("B2", "[MEAS]",
     "no rotation class is covered more than 3 times",
     "lemma_arsenal.md 3.4 records this for champions only.",
     lambda r: "mu_max" in r,
     lambda r: r["mu_max"] <= 3),

    ("B3", "[CONJ]",
     "an optimum never sits at the d = 0 vertex (n >= 6)",
     "Chain-Count gives it at the exact-cover rung; tested here as "
     "'d = 0 => length > best known for that n'.",
     lambda r: r["n"] >= 6 and r["d"] == 0,
     lambda r: r["length"] > BEST.get(r["n"], 0)),
]

BEST = {5: 153, 6: 872, 7: 5906, 8: 46204, 9: 408966}


def load(path):
    if not os.path.exists(path):
        print(f"  ({path} missing -- skipped)")
        return []
    return json.load(open(path))


def evaluate(rows, claim, corpus):
    cid, tag, stmt, why, applies, holds = claim
    seen = fail = 0
    tight = 0
    witness = None
    for r in rows:
        if not applies(r):
            continue
        seen += 1
        if holds(r):
            continue
        fail += 1
        if witness is None:
            witness = r.get("label", "?")
    return seen, fail, witness


def main(only=None):
    census, pool = load(CENSUS), load(POOL)
    census = census + load(CHAMPS6)      # 43,096 n=6 optima
    print(f"\n  corpora: census+champions6 {len(census)} strings, pool "
          f"{len(pool)} constructed walks\n")
    hdr = f"  {'id':<5} {'tag':<8} {'census':>14} {'pool':>14}   statement"
    print(hdr)
    print("  " + "-" * (len(hdr) + 20))
    broken = []
    for claim in CLAIMS:
        cid, tag, stmt, why, _, _ = claim
        if only and cid != only:
            continue
        cs, cf, cw = evaluate(census, claim, "census")
        ps, pf, pw = evaluate(pool, claim, "pool")
        cstr = f"{cs - cf}/{cs}" if cs else "-"
        pstr = f"{ps - pf}/{ps}" if ps else "-"
        flag = ""
        if tag == "[THM]" and (cf or pf):
            flag = "  <== THEOREM VIOLATED"
            broken.append((cid, cw or pw))
        elif cf or pf:
            flag = f"  refuted by {pw or cw}"
        print(f"  {cid:<5} {tag:<8} {cstr:>14} {pstr:>14}   {stmt}{flag}")
        if only:
            print(f"\n    why: {why}")
    if broken:
        print(f"\n  FAILED: {broken}")
        return 1
    print("\n  no [THM] violated on either corpus")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default=None)
    args = ap.parse_args()
    print(__doc__.split("Usage:")[0].strip())
    sys.exit(main(args.only))
