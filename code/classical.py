"""Classical recursive superpermutation construction (length 1!+2!+...+n!)."""

from permgraph import all_perms, is_superpermutation


def recursive_superperm(n):
    """Build the classical superpermutation on 1..n via the recursive algorithm.

    Returns a list of ints.
    """
    if n == 1:
        return [1]
    prev = recursive_superperm(n - 1)
    # split prev into its (n-1)! permutation frames, in order of appearance
    frames = []
    m = len(prev)
    for i in range(m - (n - 1) + 1):
        w = tuple(prev[i:i + n - 1])
        if len(set(w)) == n - 1:
            frames.append(w)
            # frames are consecutive permutations; skip ahead is wrong:
            # the recursive algorithm lists each permutation once in order
    # dedupe while preserving order (each frame appears once already in a
    # minimal string, but be safe)
    seen = set()
    uniq = []
    for f in frames:
        if f not in seen:
            seen.add(f)
            uniq.append(f)
    # build: f + [n] + f for each, then squeeze using maximal overlaps
    out = []
    for i, f in enumerate(uniq):
        block = list(f) + [n] + list(f)
        if i == 0:
            out.extend(block)
        else:
            k = max(k for k in range(len(block) + 1)
                    if k == 0 or out[-k:] == block[:k])
            out.extend(block[k:])
    return out


def expected_length(n):
    from math import factorial
    return sum(factorial(i) for i in range(1, n + 1))


if __name__ == "__main__":
    for n in range(1, 7):
        s = recursive_superperm(n)
        ok = is_superpermutation(s, n)
        print(f"n={n}: length={len(s)} expected={expected_length(n)} "
              f"valid={ok}")
        assert len(s) == expected_length(n), f"length mismatch at n={n}"
        assert ok, f"not a superpermutation at n={n}"
    print("classical construction OK")
