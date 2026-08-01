"""Kernel v3: BFS over arc-layers as batched cupy tensor ops (chunked).

Frontier = flat state arrays (mask[words], z[zwords], e, E, v, more).
Each layer expands all (jump target, arc-length) children under the budget
filters (in state-chunks to bound VRAM), counts full-cover children as
solutions, then dedups on (mask, z, e) keeping min E.

Validation gates:
  n=4 budget 7  -> exactly 1 solution
  n=5 budget 29 -> 0 solutions (certifies cost >= 148)
  n=5 budget 30 -> >= 1 solution (positive control)

Usage: python gpu_bfs.py N BUDGET [--no-dedup] [--chunk K]
"""

import sys
import time

import cupy as cp
import numpy as np

from permgraph import all_perms, weight
from gpu_prover import NLOOPS


def build_tables(n):
    perms = all_perms(n)
    N = len(perms)
    idx = {p: i for i, p in enumerate(perms)}
    sig = lambda u: u[1:] + u[:1]
    nxt = np.array([idx[sig(u)] for u in perms], dtype=np.int32)
    from math import factorial
    ncyc = factorial(n - 1)
    cycid = np.empty(N, dtype=np.int32)
    cym = np.zeros((ncyc, (N + 63) // 64), dtype=np.uint64)
    seen = np.zeros(N, dtype=bool)
    nc = 0
    for i in range(N):
        if seen[i]:
            continue
        j = i
        while not seen[j]:
            seen[j] = True
            cycid[j] = nc
            cym[nc, j // 64] |= np.uint64(1) << np.uint64(j % 64)
            j = nxt[j]
        nc += 1
    outw = np.zeros((N, N - 1), dtype=np.int32)
    outt = np.zeros((N, N - 1), dtype=np.int32)
    outn = np.zeros(N, dtype=np.int32)
    for i, u in enumerate(perms):
        edges = []
        for j, v in enumerate(perms):
            if i != j:
                w = weight(u, v)
                if w >= 2:
                    edges.append((w, j))
        edges.sort()
        outn[i] = len(edges)
        for k, (w, j) in enumerate(edges):
            outw[i, k] = w
            outt[i, k] = j
    words = (N + 63) // 64
    arcm = np.zeros((N, n, words), dtype=np.uint64)
    arce = np.zeros((N, n), dtype=np.int32)
    for s in range(N):
        m = np.zeros(words, dtype=np.uint64)
        j = s
        for L in range(n):
            m[j // 64] |= np.uint64(1) << np.uint64(j % 64)
            arcm[s, L] = m.copy()
            arce[s, L] = j
            j = nxt[j]
    return {"perms": perms, "N": N, "ncyc": nc, "cycid": cycid, "cym": cym,
            "outw": outw, "outt": outt, "outn": outn, "arcm": arcm,
            "arce": arce, "words": words}


class BFS:
    def __init__(self, n, budget, chunk=100_000):
        tb = build_tables(n)
        self.tb = tb
        self.n = n
        self.budget = budget
        self.chunk = chunk
        self.N = tb["N"]
        self.ncyc = tb["ncyc"]
        self.words = tb["words"]
        nloops = NLOOPS[n]
        self.zwords = (nloops + 63) // 64
        self.vcap = budget - self.ncyc + 1
        self.outw = cp.asarray(tb["outw"])
        self.outt = cp.asarray(tb["outt"])
        self.arcm = cp.asarray(tb["arcm"])
        self.arce = cp.asarray(tb["arce"])
        self.cym = cp.asarray(tb["cym"])
        self.cycid = cp.asarray(tb["cycid"])
        self.gen2 = cp.asarray(np.fromfile(f"gen2_n{n}.bin", dtype=np.int32))
        fw = np.zeros(self.words, dtype=np.uint64)
        fw[:-1] = np.uint64(0xFFFFFFFFFFFFFFFF)
        rem = self.N & 63
        fw[-1] = np.uint64((1 << rem) - 1) if rem else \
            np.uint64(0xFFFFFFFFFFFFFFFF)
        self.FULL = cp.asarray(fw)

    def root_frontier(self):
        n = self.n
        mask0 = self.tb["arcm"][0]
        sc0 = self.tb["cycid"][0]
        z0 = np.zeros((n, self.zwords), dtype=np.uint64)
        e0 = self.tb["arce"][0].astype(np.int32)
        E0 = np.zeros(n, dtype=np.int32)
        v0 = np.zeros(n, dtype=np.int32)
        more0 = np.array([
            self.ncyc - int((mask0[L] & self.tb["cym"][sc0]
                             == self.tb["cym"][sc0]).all())
            for L in range(n)], dtype=np.int32)
        return (cp.asarray(mask0), cp.asarray(z0), cp.asarray(e0),
                cp.asarray(E0), cp.asarray(v0), cp.asarray(more0))

    def expand(self, st, R):
        gmask, gz, ge, gE, gv, gmore = st
        n = self.n
        w_c = self.outw[ge]                      # (S, T)
        s_c = self.outt[ge]
        ne = gE[:, None] + (w_c - 2)
        viable = (R + gmore[:, None] + ne) <= self.budget
        rows = cp.arange(gmask.shape[0])[:, None]
        wsel = gmask[rows, s_c >> 6]
        viable &= ((wsel >> (s_c & 63).astype(cp.uint64)) & 1) == 0
        zb = self.gen2[s_c]
        zsel = gz[rows, zb >> 6]
        znew = ((zsel >> (zb & 63).astype(cp.uint64)) & 1) == 0
        vnew = gv[:, None] + znew
        viable &= vnew <= self.vcap
        children = []
        okL = None
        solutions = 0
        for L in range(n):
            am = self.arcm[s_c, L]               # (S, T, words)
            inter = (am & gmask[:, None, :]).any(axis=2)
            okL = ~inter if okL is None else (okL & ~inter)
            nm = gmask[:, None, :] | am
            sc = self.cycid[s_c]
            cov = ((nm & self.cym[sc]) == self.cym[sc]).all(axis=2)
            more2 = gmore[:, None] - cov
            ok = viable & okL & ((R + 1 + more2 + ne) <= self.budget)
            fullm = (nm == self.FULL).all(axis=2)
            solutions += int((ok & fullm).sum())
            ok &= ~fullm
            ii, jj = cp.nonzero(ok)
            if ii.shape[0] == 0:
                continue
            cm = nm[ii, jj]
            cz = gz[ii].copy()
            ns = znew[ii, jj]
            if bool(ns.any()):
                rows2 = cp.nonzero(ns)[0]
                bz = zb[ii, jj][rows2]
                cz[rows2, bz >> 6] |= cp.left_shift(
                    cp.uint64(1), (bz & 63).astype(cp.uint64))
            children.append((cm, cz,
                             self.arce[s_c[ii, jj], L].astype(cp.int32),
                             ne[ii, jj], vnew[ii, jj], more2[ii, jj]))
        if not children:
            return solutions, None
        return solutions, (cp.concatenate([c[0] for c in children]),
                           cp.concatenate([c[1] for c in children]),
                           cp.concatenate([c[2] for c in children]),
                           cp.concatenate([c[3] for c in children]),
                           cp.concatenate([c[4] for c in children]),
                           cp.concatenate([c[5] for c in children]))

    def dedup_cpu(self, st):
        gmask, gz, ge, gE, gv, gmore = st
        S = gmask.shape[0]
        if S == 0:
            return st
        cols = [gE.astype(np.int64), ge.astype(np.int64)]
        for w_ in range(self.zwords - 1, -1, -1):
            cols.append(gz[:, w_].astype(np.int64))
        for w_ in range(self.words - 1, -1, -1):
            cols.append(gmask[:, w_].astype(np.int64))
        order = np.lexsort(np.stack(cols))
        gmask, gz, ge = gmask[order], gz[order], ge[order]
        gE, gv, gmore = gE[order], gv[order], gmore[order]
        first = np.ones(S, dtype=bool)
        first[1:] = ((gmask[1:] != gmask[:-1]).any(axis=1) |
                     (gz[1:] != gz[:-1]).any(axis=1) |
                     (ge[1:] != ge[:-1]))
        return (gmask[first], gz[first], ge[first],
                gE[first], gv[first], gmore[first])

    def run(self, dedup=True):
        st = self.root_frontier()
        solutions = 0
        total_nodes = st[0].shape[0]
        R = 1
        t0 = time.time()
        while st[0].shape[0]:
            parts = []
            S = st[0].shape[0]
            # VRAM-adaptive chunk: expansion tensors cost ~(T*words*8*4)B/state
            free = cp.cuda.Device().mem_info[0]
            per_state = self.outw.shape[1] * self.words * 8 * 4 + 4096
            dyn_chunk = max(10_000, min(self.chunk,
                                        int(free * 0.5 / per_state)))
            for c0 in range(0, S, dyn_chunk):
                c1 = min(c0 + dyn_chunk, S)
                sub = tuple(x[c0:c1] for x in st)
                sol, kids = self.expand(sub, R)
                solutions += sol
                if sol:
                    print(f"[bfs] +{sol} SOLUTIONS at layer R={R+1}",
                          flush=True)
                if kids:
                    parts.append(tuple(cp.asnumpy(x) for x in kids))
                cp.get_default_memory_pool().free_all_blocks()
            if not parts:
                break
            # assemble + dedup next layer on CPU (big RAM), upload after
            st_cpu = tuple(np.concatenate([p[i] for p in parts])
                           for i in range(6))
            total_nodes += st_cpu[0].shape[0]
            del parts
            if dedup:
                st_cpu = self.dedup_cpu(st_cpu)
            st = tuple(cp.asarray(x) for x in st_cpu)
            R += 1
            print(f"[bfs] R={R}: frontier={st[0].shape[0]} "
                  f"solutions={solutions} nodes={total_nodes} "
                  f"elapsed={time.time()-t0:.1f}s", flush=True)
        print(f"[bfs] DONE: solutions={solutions} nodes={total_nodes} "
              f"elapsed={time.time()-t0:.1f}s", flush=True)
        if solutions == 0:
            print(f"[bfs] CERTIFIED: no path with R+E <= {self.budget} "
                  f"(cost <= {self.N + self.budget - 2})", flush=True)
        return solutions, total_nodes


def main():
    n = int(sys.argv[1])
    budget = int(sys.argv[2])
    dedup = "--no-dedup" not in sys.argv
    b = BFS(n, budget)
    print(f"[bfs] n={n} budget={budget} vcap={b.vcap} dedup={dedup}",
          flush=True)
    b.run(dedup)


if __name__ == "__main__":
    main()
