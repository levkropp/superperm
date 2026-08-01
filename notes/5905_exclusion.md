# The 5905 kernel candidate and the 2019 exclusion sweep

**Verdict (verified).** The unique palindromic K=27 candidate kernel
(`666646664664666466466646666`, score 15) from the swarm's skip-floor
analysis is **already excluded**: the 2019 exhaustive sweep searched all
kernels of length ≤ 35 with score ≥ 15 (13,294 kernels, zero
completions), and the ~1.6M-kernel palindromic search produced exactly 7
completions, all of score 10 (the 5906 champion class). Sources: Greg
Egan's Superpermutations page and Logan Seaburg's search-history
deep-dive (loganseaburg.com/blog/superpermutations, March 2025).

**Consequences.**

1. The candidate kernel is dead — running its completion would repeat a
   known zero. The completion runs were stopped before any real compute
   was spent.
2. **p(7) = 5906 is NOT proven by this.** The sweep covers kernels of
   length ≤ 35 inside the kernel+tree construction class only. The
   skip-floor law (B_min ≈ K/2 − 2) leaves arithmetically legal
   5905-shapes at K ≈ 37–42, outside the swept range and never searched.
   Coanda-type designs sit outside the class entirely. The certified
   lower bound remains 5888 (Hunter & Raudvere, Lean).
3. What the sweep does establish: the champion region is saturated in the
   standard class, so any record-beating construction must go above
   length-35 kernels or outside the class. That is the honest frontier
   map for the 5905 question going forward.

**Durable results retained from the episode:** the skip-floor law
(B_min(K)), the K=27 uniqueness argument (a good template for any future
candidate), the stitch neutrality theorem, and the Stride Law
(w(σ⁻¹g_j, g_{j+k}) = k+1, chain stitches never profitable).
