"""CORECAP [THM]: the core cap is n-2 at general n -- the proof's gates.

The theorem (docs/notes/large_n_lower_bound.md section 4b): a core-only
free chain of single blocks covers at most n-2 blocks at every n.

The proof rests on explicit forms and three identities, all asserted here
directly from the definitions:

    a = (1 2 ... n-1)          ord n-1
    s = a^(n-2)b = (1 2 ... n-2)   ord n-2
    u = a^(n-3)b,  u^2 = e     (b a^(n-3) b = a^2)
    s.u = a,  u.s^(n-3) = a^(-1) = a^(n-2)

and then re-runs the exhaustive cap search (freejoin.corecap) at
n = 5..8, which must return exactly n-2 with mixed-length witnesses.

Usage: python3 code/corecap.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from superstruct import Struct
from freejoin import corecap


def check_identities(n):
    st = Struct(n)
    a, b, s = st.a, st.b, st.s
    u = st.comp(st.apow[n - 3], b)
    a_exp = tuple(list(range(2, n)) + [1, n])
    s_exp = tuple(list(range(2, n - 1)) + [1, n - 1, n])
    assert a == a_exp, f"n={n}: a is not the (n-1)-cycle"
    assert s == s_exp, f"n={n}: s is not the (n-2)-cycle"
    assert st.order(s) == n - 2, f"n={n}: ord(s) != n-2"
    assert st.comp(u, u) == st.ident, f"n={n}: u^2 != e"
    assert st.comp(s, u) == a, f"n={n}: s.u != a"
    sp = st.ident
    for _ in range(n - 3):
        sp = st.comp(sp, s)
    assert st.comp(u, sp) == st.apow[n - 2], f"n={n}: u.s^(n-3) != a^(n-2)"
    print(f"  n={n}: explicit forms, ord(s)=n-2, u^2=e, "
          f"s.u=a, u.s^(n-3)=a^(n-2)   OK")


def main():
    print("CORECAP proof gates: the three identities from the definitions")
    for n in range(5, 11):
        check_identities(n)
    print("\nExhaustive cap search (freejoin.corecap), must be exactly n-2:")
    for n in range(5, 9):
        c, w = corecap(n)
        assert c == n - 2, f"n={n}: core cap {c} != {n-2}"
        assert len(set(w)) > 1 or n == 5, f"n={n}: witness not mixed"
        print(f"  n={n}: longest core-only chain = {c} = n-2   witness {w}")
    print("\nCORECAP [THM]: all gates pass")


if __name__ == "__main__":
    main()
