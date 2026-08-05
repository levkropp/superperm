"""Split-free superpermutations at n = 7 have length >= 5889.

One better than Hunter-Raudvere on this slice, and v-INDEPENDENT: no
rung-by-rung ladder, no reference to the number of entered 2-loops at all.
This supersedes the 5888 of rung_split_free.py.

SETTING.  A walk is split-free if no rotation class is covered by more than
one arc, so R = 720 and every arc is a full 7-permutation arc.  The only
weight-2 move available is then delta, and delta out of a full arc at
generator g lands on g.a  (a = c^6 d, order 6), the next generator of the SAME
2-loop.  So a BLOCK -- a maximal run of arcs joined by weight-2 jumps --
occupies consecutive generators of one loop and has length 1..6, a block of
length 6 being a complete traversal.  With B blocks, hence B-1 costly jumps,
and Y = sum over them of (weight - 3),

        length = 5765 + (B - 1) + Y  =  5765 + E.

So 5889 is exactly  E >= 124.

INGREDIENT 1 -- THE BLOCK-COUNT LEMMA (`feasible`, pure integer counting).
Write f = #blocks of length 6, n5 = #blocks of length 5, m4 = #blocks of
length <= 4, and `short` for the total length of those m4 blocks.  Call a
maximal stretch of consecutive length-6 blocks joined by weight-3 jumps an
OM-CHAIN, and let c be their number.  Then

  (i)    6f + 5*n5 + short = 720,     m4 <= short <= 4*m4,     B = f+n5+m4;
  (ii)   c <= (B - f) + Y + 1
         -- each om-chain after the first is opened by a transition out of a
            6-block that is not a weight-3 6->6 jump: either it lands on a
            non-6 block (at most B-f of those) or it has weight >= 4 (at most
            Y of those), plus the walk's own first block;
  (iii)  f <= 4c + (m4 + Y + 1)
         -- EXIT TRICHOTOMY (exit_table.py row l = 6): of the six weight-3
            exits of a complete traversal, three are dead and two cap the
            next block at length 4, so a weight-3 jump between two blocks of
            length >= 5 must take the unique cap-6 exit om.  om is right
            multiplication by b, and ord(a^5 b) = 5 (PENTAD LEMMA), so an
            om-chain has at most 5 traversals, and exactly 5 only if it is
            not followed by another block of length >= 5 by a weight-3 jump:
            it ends the walk, or lands on a short block, or exits at weight
            >= 4.

Together these force  E >= 123, attained only at  (B, Y) = (124, 0)  and only
by the single profile  f = 100 sixes, n5 = 24 fives, m4 = 0.

INGREDIENT 2 -- THE PERIOD MAP.  That profile is rigid enough to kill.  With
Y = 0 and m4 = 0 every transition in the walk is a weight-3 jump between
blocks of length >= 5, hence om; and no om-chain of five traversals can be
followed by anything, so the block sequence is 25 om-chains separated by 24
isolated length-5 blocks.  A chain of k traversals followed by a five
advances the chain start by right multiplication by

        Q_k = s^k u,     s = a^5 b  (ord 5),     u = a^4 b  (ord 2),

using the fact -- checked here at all 5040 entry points -- that the unique
cap-6 exit of a length-5 block is the same b.  The chain-length vector is
25 x 4  or  23 x 4 + one 3 + a final 5, and ord(Q_4) = 6 kills both: the
seventh chain re-enters the loop of the first.

Hence E >= 124 and every split-free 7-symbol superpermutation has length
>= 5889.
"""

from itertools import permutations

# ---------------------------------------------------------------------------
# INGREDIENT 1 -- the block-count lemma, as a finite integer search
# ---------------------------------------------------------------------------


def profiles(B, Y):
    """Block-length profiles of B blocks with excess Y surviving (i)-(iii)."""
    out = []
    for f in range(B + 1):
        for n5 in range(B - f + 1):
            m4 = B - f - n5
            short = 720 - 6 * f - 5 * n5
            if m4 == 0:
                if short != 0:
                    continue
            elif not (m4 <= short <= 4 * m4):
                continue
            c = (B - f) + Y + 1                    # (ii)
            if f > 4 * c + (m4 + Y + 1):           # (iii)
                continue
            out.append((f, n5, m4, short))
    return out


def min_excess():
    """Minimum E = (B-1) + Y over everything counting allows."""
    best, arg = None, None
    for Y in range(0, 40):
        for B in range(120, 200):
            E = (B - 1) + Y
            if best is not None and E >= best:
                continue
            if profiles(B, Y):
                best, arg = E, (B, Y)
    return best, arg


# ---------------------------------------------------------------------------
# INGREDIENT 2 -- the period map, rebuilt from the permutation definitions
# ---------------------------------------------------------------------------

n = 7
ident = tuple(range(1, n + 1))
sig = lambda u: u[1:] + u[:1]
delta = lambda u: u[2:] + (u[1], u[0])
comp = lambda u, v: tuple(u[v[i] - 1] for i in range(n))


def inv(u):
    w = [0] * n
    for i, x in enumerate(u):
        w[x - 1] = i + 1
    return tuple(w)


def onecycle(u):
    best, x = u, u
    for _ in range(n - 1):
        x = sig(x)
        best = min(best, x)
    return best


def end_of(g):
    u = g
    for _ in range(n - 1):
        u = sig(u)
    return u


def order(u):
    k, x = 1, u
    while x != ident:
        x, k = comp(x, u), k + 1
    return k


a = ident
for _ in range(6):
    a = comp(a, sig(ident))
a = comp(a, delta(ident))
assert order(a) == 6
apow = [ident]
for _ in range(5):
    apow.append(comp(apow[-1], a))

loop = lambda g: frozenset(comp(g, p) for p in apow)


def exits(g, l):
    """(right-multiplier, cap) for the six weight-3 exits of a length-l block.

    cap = how many generators the NEXT block can run before it re-enters a
    rotation class this block just burned.  An upper bound, which is the
    direction a lower-bound proof needs.
    """
    burned = {onecycle(x) for x in (comp(g, p) for p in apow[:l])}
    last = comp(g, apow[l - 1])
    tail = end_of(last)
    out = []
    for p in permutations(tail[:3]):
        h = tail[3:] + p
        cap, x = 0, h
        while cap < 6 and onecycle(x) not in burned:
            cap, x = cap + 1, comp(x, a)
        out.append((comp(inv(last), h), cap))
    return out


def walk_ok(chain_lengths, s_pow, u):
    """Lay out the forced B=124 walk; True iff it never repeats a 2-loop.

    chain_lengths[i] = number of complete traversals in om-chain i.  Every
    chain but the last is followed by one isolated length-5 block.
    """
    g, seen = ident, set()
    for i, k in enumerate(chain_lengths):
        for j in range(k):                       # the k complete traversals
            L = loop(comp(g, s_pow[j]))
            if L in seen:
                return False
            seen.add(L)
        if i == len(chain_lengths) - 1:          # final chain: no trailing 5
            break
        L = loop(comp(g, s_pow[k]))              # the length-5 block
        if L in seen:
            return False
        seen.add(L)
        g = comp(comp(g, s_pow[k]), u)
    return True


if __name__ == "__main__":
    print(__doc__.split("SETTING.")[0].strip())

    # --- (1) counting ------------------------------------------------------
    print("\n--- (1) block-count lemma ---")
    for Y in range(0, 4):
        row = []
        for B in range(120, 127):
            row.append(f"{B}:{len(profiles(B, Y))}")
        print(f"  Y = {Y}   #profiles by B   " + "  ".join(row))
    E0, (B0, Y0) = min_excess()
    print(f"  minimum E allowed by counting alone: E = {E0} at (B,Y) = "
          f"{(B0, Y0)}   length >= {5765 + E0}")
    assert (E0, B0, Y0) == (123, 124, 0)
    assert profiles(124, 0) == [(100, 24, 0, 0)], profiles(124, 0)
    print("  the ONLY state at E = 123: B = 124, Y = 0, "
          "100 traversals + 24 fives, no short block.")

    # --- (2) the exit rows, at all 5040 entry points -----------------------
    print("\n--- (2) exit rows (verified S_7-equivariant) ---")
    e6, e5 = exits(ident, 6), exits(ident, 5)
    c6 = sorted(k for _, k in e6)
    c5 = sorted(k for _, k in e5)
    assert c6 == [0, 0, 0, 4, 4, 6] and c5 == [0, 0, 4, 5, 5, 6]
    b6 = [m for m, k in e6 if k == 6]
    b5 = [m for m, k in e5 if k == 6]
    assert len(b6) == len(b5) == 1 and b6 == b5
    b = b6[0]
    for g in permutations(range(1, n + 1)):
        for l, cs in ((6, c6), (5, c5)):
            o = exits(g, l)
            assert sorted(k for _, k in o) == cs
            assert [m for m, k in o if k == 6] == [b]
    print(f"  l = 6 caps {c6}      l = 5 caps {c5}")
    print(f"  unique cap-6 exit of BOTH rows: om = b = {b}")

    s = comp(apow[5], b)                     # traversal -> next block start
    u = comp(apow[4], b)                     # length-5  -> next block start
    assert order(s) == 5 and order(u) == 2
    print(f"  s = a^5.b  ord {order(s)}      u = a^4.b  ord {order(u)}")

    # --- (3) killing the E = 123 state -------------------------------------
    print("\n--- (3) the (B,Y) = (124,0) profile is not realisable ---")
    spow = [ident]
    for _ in range(5):
        spow.append(comp(spow[-1], s))
    print(f"  Q_3 = s^3.u ord {order(comp(spow[3], u))}    "
          f"Q_4 = s^4.u ord {order(comp(spow[4], u))}")
    assert order(comp(spow[4], u)) == 6

    # m4 = 0 and Y = 0, so an om-chain of five traversals can only be the LAST
    # chain of the walk.  24 fives give at most 25 chains, and f = 100 with
    # chains <= 4 needs at least 25, so: exactly 25 chains, the 24 fives all
    # isolated, walk starting and ending with a chain of traversals.
    layouts = []
    for last in (4, 5):
        rest = 100 - last
        for p in range(24):                  # index of the one non-4 chain
            for k in range(1, 5):
                if 4 * 23 + k == rest:
                    v = [4] * 24
                    v[p] = k
                    layouts.append(tuple(v + [last]))
        if 4 * 24 == rest:
            layouts.append(tuple([4] * 24 + [last]))
    layouts = sorted(set(layouts))
    assert all(sum(v) == 100 and len(v) == 25 for v in layouts)
    print(f"  {len(layouts)} admissible chain-length vectors; "
          "checking each for a repeated 2-loop")
    survivors = [v for v in layouts if walk_ok(v, spow, u)]
    for v in layouts[:2]:
        print(f"    e.g. {v[:6]}...{v[-2:]}  -> repeats a loop: "
              f"{not walk_ok(v, spow, u)}")
    assert not survivors, survivors
    print("  every one of them repeats a 2-loop.")

    print("\n  So E >= 124 and split-free s(7) >= 5765 + 124 = 5889.")
