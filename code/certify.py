"""Independent certificate checker for superpermutation claims.

Deliberately implemented from scratch (stdlib only, no permgraph imports)
so that a certificate does not depend on the machinery that produced the
candidate.

Usage:
  python certify.py --string data/houston_872.txt --n 6
  python certify.py --path data/anneal_n6_best.pt   # torch save with 'path'

Checks:
  * string length reported;
  * every one of the n! permutations of 1..n occurs as a contiguous window
    (verified by a sort-based counting pass, not set membership);
  * for --path: the induced string is rebuilt by direct simulation and its
    length must equal n + sum of edge weights.
"""

import argparse
import itertools
import sys


def check_string(s, n):
    count = 0
    seen = set()
    for i in range(len(s) - n + 1):
        w = tuple(sorted(s[i:i + n]))
        if w == tuple(range(1, n + 1)):
            seen.add(tuple(s[i:i + n]))
    total = 1
    for k in range(2, n + 1):
        total *= k
    ok = len(seen) == total
    print(f"string length : {len(s)}")
    print(f"distinct perms: {len(seen)} / {total}")
    print(f"VERDICT: {'VALID superpermutation' if ok else 'INVALID'}")
    return ok, len(s)


def path_to_string_sim(path, n):
    """Rebuild the string from a vertex sequence by direct simulation."""
    s = list(path[0])
    for u, v in zip(path, path[1:]):
        # largest k with suffix of u == prefix of v
        k = 0
        for kk in range(1, n):
            if u[n - kk:] == v[:kk]:
                k = kk
        add = n - k
        s.extend(v[n - add:])
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--string")
    ap.add_argument("--path")
    ap.add_argument("--n", type=int)
    args = ap.parse_args()

    if args.string:
        n = args.n
        s = [int(c) for c in open(args.string).read() if c.isdigit()]
        ok, L = check_string(s, n)
        sys.exit(0 if ok else 1)

    if args.path:
        import torch  # only needed to read the artifact
        d = torch.load(args.path, weights_only=False)
        n = d["n"]
        perms = list(itertools.permutations(range(1, n + 1)))
        path = [perms[int(k)] for k in d["path"]]
        # every vertex exactly once?
        assert len(set(path)) == len(path), "path revisits a vertex"
        fact = 1
        for k in range(2, n + 1):
            fact *= k
        assert len(path) == fact, f"path has {len(path)} vertices, need {fact}"
        s = path_to_string_sim(path, n)
        print(f"rebuilt string from path: length {len(s)} "
              f"(claimed cost {d['cost']} + n = {d['cost'] + n})")
        assert len(s) == d["cost"] + n, "length/cost mismatch"
        ok, L = check_string(s, n)
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
