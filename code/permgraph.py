"""Core machinery for the minimal superpermutation problem.

A superpermutation on n symbols is a string containing every permutation of
range(1, n+1) as a contiguous substring.  The standard graph model: vertices
are the n! permutations; the weight of edge (u, v) is the number of symbols
that must be appended to u (dropping the same number from the front) to
obtain v.  For distinct u, v this is n - k where k is the longest suffix of u
matching a prefix of v (k in 0..n-1).  Weights satisfy the triangle
inequality, so minimal superpermutation length = n + minimum-weight
Hamiltonian path in this digraph.

All permutations here are tuples of ints drawn from 1..n.
"""

from itertools import permutations


def all_perms(n):
    """All permutations of 1..n as tuples, in lexicographic order."""
    return list(permutations(range(1, n + 1)))


def weight(u, v):
    """Edge weight: symbols appended to turn permutation u into v."""
    n = len(u)
    if u == v:
        return 0
    for k in range(n - 1, 0, -1):
        if u[n - k:] == v[:k]:
            return n - k
    return n


def build_weight_matrix(n):
    """Full n! x n! weight matrix as a list of lists (dense, ints)."""
    perms = all_perms(n)
    m = len(perms)
    W = [[0] * m for _ in range(m)]
    for i, u in enumerate(perms):
        for j, v in enumerate(perms):
            if i != j:
                W[i][j] = weight(u, v)
    return perms, W


def path_to_string(path):
    """Convert a Hamiltonian path (sequence of permutation tuples) to its string."""
    s = list(path[0])
    for u, v in zip(path, path[1:]):
        w = weight(u, v)
        s.extend(v[len(v) - w:] if w else ())
    return s


def string_to_path(s, n):
    """Extract the sequence of permutation frames from a superpermutation string.

    Returns the ordered list of *first occurrences* of each distinct
    permutation appearing as a length-n window, i.e. the implied walk through
    the permutation graph.
    """
    seen = []
    seen_set = set()
    for i in range(len(s) - n + 1):
        window = tuple(s[i:i + n])
        if len(set(window)) == n and window not in seen_set:
            seen_set.add(window)
            seen.append(window)
    return seen


def is_superpermutation(s, n):
    """True iff string s (sequence of ints) contains every permutation of 1..n."""
    need = {p for p in permutations(range(1, n + 1))}
    for i in range(len(s) - n + 1):
        window = tuple(s[i:i + n])
        if window in need:
            need.discard(window)
        if not need:
            return True
    return not need


def path_weight(path):
    """Total weight of a sequence of permutations."""
    return sum(weight(u, v) for u, v in zip(path, path[1:]))


def triangle_inequality_holds(n):
    """Sanity check: weights satisfy the triangle inequality (spot exhaustive for small n)."""
    perms = all_perms(n)
    for u in perms:
        for v in perms:
            w_uv = weight(u, v)
            for x in perms:
                if weight(u, x) + weight(x, v) < w_uv:
                    return False
    return True
