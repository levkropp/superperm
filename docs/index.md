---
layout: math
title: "AI ripped superpermutations wide open"
---

# AI ripped superpermutations wide open
### *(and what I was doing while it happened)*

After seeing the Jacobian conjecture and the Maxwell conjecture proven
false, I decided to try Kimi K3 on the 4chan problem. If you don't know it:
it's the question that was born on 4chan's /sci/ board in 2011, what's the
shortest string that contains every possible ordering of $n$ episodes as a
contiguous binge-watch? People call them superpermutations; $s(n)$ is the
answer. For $n = 6$ it's been stuck between 867 and 872 for over a decade.

<iframe width="100%" height="400" src="https://www.youtube.com/embed/wJGE4aEWc28" frameborder="0" allowfullscreen></iframe>

*A video explains it a lot better.*

Kimi did research and didn't find any new improvements at the time, so I
went ahead and tried to improve the bounds myself. And we actually found
something: a neat, human-understandable lemma I'm calling the **absorption
lemma**. It says every "2-loop" in the problem has exactly five doors in,
so if your walk has $R$ segments you must have entered at least
$\lceil (R-1)/5 \rceil$ of those loops. The two best constructions anyone
has ever found both hit that bound *exactly*, which is how you know it's
the right invariant. Combined with a rigidity argument and an exhaustive
check of all 10,068 possible covers, it proves $s(6) \ge 868$.
[The full writeup with the math is here](absorption-lemma), and it's the
one page of all this that I'd genuinely recommend reading.

Then I went looking for someone to tell about it, and that's when I found
the Superpermutators Google group, and my heart sank a little. Not only was
$s(6) \ge 868$ essentially known since an unpublished 2019 draft by Zach
Hunter, but in the two weeks right before we finished, a wave of
AI-assisted work had hit the problem:

- **July 17** : Raudvere drops a Lean-4 machine-checked proof of
  $s(6) \ge 868$ (and 5886 for $n = 7$, for *every* $n \ge 5$):
  [superperm-coeff2](https://github.com/urdvr/superperm-coeff2)
- **July 28** : Hunter & Raudvere finish the 2019 draft properly, Lean
  again: $s(6) \ge 869$, $s(7) \ge 5888$:
  [superpermutations-hunter](https://github.com/urdvr/superpermutations-hunter)
- **July 29** : vlad-ds posts a computer-assisted proof that
  $s(6) = 872$ *exactly*: [a6-872](https://github.com/vlad-ds/a6-872).
  Preliminary, audits invited, but if it holds up, the n = 6 story is over.

So my 868 is not a new lower bound. It's an *independent* proof of
something the field got three days earlier by three different methods. In
computer-assisted math, independent confirmations genuinely matter, but
let's be honest about what happened here: AI ripped superpermutations wide
open, and I got to watch it happen in real time from about three days
behind the wave.

And since everyone loves the punchline: **you need to watch 872 episodes of
the first 6 Haruhi episodes back to back in order to have watched every way
you could have arranged them during the binge itself.** That's what ten
years of silence and two weeks of chaos were about.

---

### Where things actually stand

| $n$ | lower bound | upper bound | status |
|---|---|---|---|
| 6 | 872 (preliminary, vlad-ds) | 872 (Houston 2014) | **probably done** |
| 7 | 5888 (Hunter & Raudvere, Lean) | 5906 (Coanda/Egan/Houston 2019) | the open frontier |
| 8 | 46103 (Hunter & Raudvere, Lean) | 46204 | wide open |

The n = 7 gap is where the game is now. Our [baseline
notes](https://github.com/levkropp/superperm/blob/main/notes/s7_baseline.md)
already have one fun observation in them: the absorption lemma holds at
$n = 7$ too, and the current 5906 champion is the only known string
anywhere that *doesn't* saturate it (it's off by exactly one). Make of
that what you will.

The repo with all the verification machinery:
[github.com/levkropp/superperm](https://github.com/levkropp/superperm).
The lemma, properly typeset: [here](absorption-lemma).
