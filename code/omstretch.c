/* omstretch.c -- the om-stretch primitive rho(c), exactly.
 *
 * Inside a single om-stretch every transition is om, so (Coset Lemma,
 * code/coset_lemma.py) all generators stay in one right coset of
 * H = <a,b>, |H| = (n-1)!, and that coset meets every rotation class
 * exactly once.  In a SPLIT-FREE walk each class is used at most once, so a
 * stretch is exactly a SIMPLE PATH in the right Cayley graph
 *
 *      Cay(H; {a, b}) on (n-1)! vertices, out-degree 2:
 *          g -> g.a   continues the current run   (free)
 *          g -> g.b   ends it and starts a new one (costs one run)
 *
 * Runs cap at n-1 automatically: ord(a) = n-1, so an (n-1)-st a-step would
 * revisit the run's own start.
 *
 *      rho(c) := min number of runs over simple paths covering c vertices
 *              =  1 + min number of b-edges.
 *
 * Left multiplication by h in H preserves right-Cayley edges, so the graph is
 * vertex-transitive and every path may be assumed to start at the identity.
 *
 * Build:  gcc -O3 -march=native -DNSYM=6 -o code/omstretch code/omstretch.c
 * Run:    ./code/omstretch [budget]
 *         with no budget it reports rho(c) for every c it can prove.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifndef NSYM
#define NSYM 6
#endif

#define N NSYM

static int NV;                 /* (n-1)!  vertices */
static int *succ_a, *succ_b;   /* the two out-edges */
static unsigned char *vis;
static int *bestrun;           /* bestrun[c] = min runs proven to cover c */
static long long nodes;
static long long node_cap;

/* ---- permutation helpers ------------------------------------------------ */
typedef struct { unsigned char p[N]; } perm;

static perm pcomp(perm u, perm v)            /* (u.v)[i] = u[v[i]] */
{
    perm w;
    for (int i = 0; i < N; i++) w.p[i] = u.p[v.p[i] - 1];
    return w;
}
static int peq(perm x, perm y) { return memcmp(x.p, y.p, N) == 0; }

static perm pident(void)
{
    perm u;
    for (int i = 0; i < N; i++) u.p[i] = i + 1;
    return u;
}
static perm psig(perm u)                     /* rotate left */
{
    perm w;
    for (int i = 0; i < N - 1; i++) w.p[i] = u.p[i + 1];
    w.p[N - 1] = u.p[0];
    return w;
}
static perm pdelta(perm u)
{
    perm w;
    for (int i = 0; i < N - 2; i++) w.p[i] = u.p[i + 2];
    w.p[N - 2] = u.p[1];
    w.p[N - 1] = u.p[0];
    return w;
}

/* ---- build a and b, then the coset graph -------------------------------- */
static perm A_, B_;

static void build_ab(void)
{
    perm id = pident(), c = psig(id), d = pdelta(id);
    perm a = id;
    for (int i = 0; i < N - 1; i++) a = pcomp(a, c);
    a = pcomp(a, d);                          /* a = c^(n-1) d, ord n-1 */
    A_ = a;

    /* b = the unique weight-(3) exit of a complete traversal whose cap is
     * n-1.  Rebuilding the cap test here would duplicate exit_table.py; the
     * element is characterised far more simply and is verified against the
     * Python side by omstretch.py:  b = (3,4,...,n-1,2,1,n).            */
    perm b;
    for (int i = 0; i < N - 3; i++) b.p[i] = i + 3;
    b.p[N - 3] = 2;
    b.p[N - 2] = 1;
    b.p[N - 1] = N;
    B_ = b;
}

static void build_graph(void)
{
    /* closure of <a,b> by BFS, indexing vertices in discovery order */
    int cap = 1;
    for (int i = 2; i <= N - 1; i++) cap *= i;      /* (n-1)! */
    NV = cap;

    perm *verts = malloc(sizeof(perm) * NV);
    succ_a = malloc(sizeof(int) * NV);
    succ_b = malloc(sizeof(int) * NV);

    int cnt = 0;
    verts[cnt++] = pident();
    for (int head = 0; head < cnt; head++) {
        perm x = verts[head];
        perm ys[2] = { pcomp(x, A_), pcomp(x, B_) };
        for (int k = 0; k < 2; k++) {
            int found = -1;
            for (int j = 0; j < cnt; j++)
                if (peq(verts[j], ys[k])) { found = j; break; }
            if (found < 0) {
                if (cnt >= NV) { fprintf(stderr, "closure exceeded (n-1)!\n"); exit(1); }
                verts[cnt] = ys[k];
                found = cnt++;
            }
            if (k == 0) succ_a[head] = found; else succ_b[head] = found;
        }
    }
    if (cnt != NV) { fprintf(stderr, "closure = %d, expected %d\n", cnt, NV); exit(1); }
    free(verts);
}

/* ---- loop decomposition, for the arc bound ------------------------------
 * The a-edges cut the coset into (n-2)! cycles of length n-1 (the 2-loops).
 * A run never leaves its loop, and the UNVISITED vertices of a loop fall into
 * maximal a-consecutive arcs -- each of which needs a run of its own.  So
 *
 *      remaining runs  >=  sum over loops of (#unvisited arcs)  -  1
 *
 * (the -1 because the run in progress may extend into one of them).  That is
 * far stronger than ceil(remaining / (n-1)).
 */
static int *loop_of, *pos_in_loop;
static int NL;                          /* (n-2)! loops */
static int *lmask;                      /* unvisited bitmask per loop */
static unsigned char arcs_of[1 << (N - 1)];
static int arcsum;                      /* sum of arcs_of[lmask[.]] */

static int count_arcs(int mask, int len)
{
    if (mask == 0) return 0;
    if (mask == (1 << len) - 1) return 1;          /* full cycle: one arc */
    int a = 0;
    for (int i = 0; i < len; i++) {
        int prev = (i + len - 1) % len;
        if ((mask >> i & 1) && !(mask >> prev & 1)) a++;
    }
    return a;
}

static void build_loops(void)
{
    loop_of = malloc(sizeof(int) * NV);
    pos_in_loop = malloc(sizeof(int) * NV);
    for (int i = 0; i < NV; i++) loop_of[i] = -1;
    NL = 0;
    for (int i = 0; i < NV; i++) {
        if (loop_of[i] >= 0) continue;
        int x = i, k = 0;
        do { loop_of[x] = NL; pos_in_loop[x] = k++; x = succ_a[x]; } while (x != i);
        if (k != N - 1) { fprintf(stderr, "a-cycle of length %d\n", k); exit(1); }
        NL++;
    }
    lmask = malloc(sizeof(int) * NL);
    for (int i = 0; i < NL; i++) lmask[i] = (1 << (N - 1)) - 1;
    for (int m = 0; m < (1 << (N - 1)); m++) arcs_of[m] = count_arcs(m, N - 1);
    arcsum = NL;                        /* every loop is one full arc */
}

static inline void take(int g)
{
    vis[g] = 1;
    int L = loop_of[g];
    arcsum -= arcs_of[lmask[L]];
    lmask[L] &= ~(1 << pos_in_loop[g]);
    arcsum += arcs_of[lmask[L]];
}
static inline void give(int g)
{
    int L = loop_of[g];
    arcsum -= arcs_of[lmask[L]];
    lmask[L] |= (1 << pos_in_loop[g]);
    arcsum += arcs_of[lmask[L]];
    vis[g] = 0;
}

/* ---- branch and bound --------------------------------------------------- */
static int target;             /* vertices we are trying to cover */
static int best;               /* best #runs found for `target` */

static void dfs(int g, int cov, int runs, int runlen)
{
    if (++nodes > node_cap) return;
    if (runs < bestrun[cov]) bestrun[cov] = runs;
    if (cov == target) { if (runs < best) best = runs; return; }

    /* Coverage bound.  The arc bound (every unvisited arc needs its own run)
     * is only valid when the path must cover EVERY vertex; for a partial
     * target the path may simply avoid the awkward arcs, so fall back to the
     * capacity bound there. */
    int freecap = (N - 1) - runlen;          /* the current run can still grow */
    int need = target - cov - freecap; if (need < 0) need = 0;
    int lo = runs + (need + N - 2) / (N - 1);
    if (target == NV) {
        int alt = runs + arcsum - 1;
        if (alt > lo) lo = alt;
    }
    if (lo >= best) return;

    if (runlen < N - 1) {
        int h = succ_a[g];
        if (!vis[h]) {
            take(h);
            dfs(h, cov + 1, runs, runlen + 1);
            give(h);
            if (nodes > node_cap) return;
        }
    }
    if (runs + 1 < best) {
        int h = succ_b[g];
        if (!vis[h]) {
            take(h);
            dfs(h, cov + 1, runs + 1, 1);
            give(h);
        }
    }
}

int main(int argc, char **argv)
{
    node_cap = (argc > 1) ? atoll(argv[1]) : 200000000LL;

    build_ab();
    build_graph();
    printf("n = %d   |<a,b>| = %d   (expected (n-1)! )\n", N, NV);
    printf("node cap = %lld\n", node_cap);

    vis = calloc(NV, 1);
    build_loops();
    bestrun = malloc(sizeof(int) * (NV + 1));
    for (int i = 0; i <= NV; i++) bestrun[i] = 1 << 20;
    printf("loops = %d (expected (n-2)!)\n", NL);

    /* iterative deepening on the number of runs: the first K that admits a
     * Hamiltonian path IS rho(NV), and each infeasible K is a proof. */
    target = (argc > 2) ? atoi(argv[2]) : NV;
    if (target < 1 || target > NV) { fprintf(stderr, "bad target\n"); exit(1); }
    int lb = (target == NV) ? NL : (target + N - 2) / (N - 1);
    int found = 0;
    for (int K = lb; K <= NV && !found; K++) {
        for (int i = 0; i < NV; i++) vis[i] = 0;
        for (int i = 0; i < NL; i++) lmask[i] = (1 << (N - 1)) - 1;
        arcsum = NL;
        best = K + 1;                   /* accept any solution with <= K runs */
        nodes = 0;
        take(0);
        dfs(0, 1, 1, 1);
        int capped = nodes > node_cap;
        printf("  c = %3d  K = %3d : %-12s nodes %lld%s\n", target, K,
               best <= K ? "FEASIBLE" : (capped ? "unknown" : "impossible"),
               nodes, capped ? "  (CAP HIT)" : "");
        if (best <= K) { found = 1; printf("rho(%d) = %d   (exact)\n", target, K); }
        else if (capped) { printf("cap hit at K = %d; rho(%d) > %d unproven\n", K, target, K - 1); break; }
    }

    printf("\n  c    rho(c) <=\n");
    for (int c = 1; c <= NV; c++)
        if (bestrun[c] < (1 << 20) &&
            (c % (N - 1) == 0 || c == NV || c <= 12))
            printf("%5d %9d\n", c, bestrun[c]);
    return 0;
}
