/* blockstruct6.c -- how many BLOCK STRUCTURES does a split-free n = 6 walk
 * have to choose from?
 *
 * Strip the ordering away.  A split-free walk covers each of the 120 rotation
 * classes by one full arc, and its arcs group into blocks: maximal runs joined
 * by delta.  A block is delta-consecutive inside one 2-loop, so it is an ARC
 * of that loop's 5-cycle of classes.  Hence the walk induces
 *
 *      a partition of the 120 classes into B delta-arcs,
 *
 * and a champion needs B + Y = 29 with Y >= 0, i.e. B <= 29.  This file counts
 * those partitions.  The pieces are (loop, start, length) for the 144 loops:
 * 5 arcs of each length 1..4 plus the whole loop, 21 per loop, 3024 in all.
 * Pieces are kept DISTINCT even when they cover the same classes (a singleton
 * class is an arc of all 6 of its loops), because the loop fixes the arc's
 * starting permutation and so the jump weights.
 *
 * B = 24 forces every piece to be a whole loop, so it must reproduce the 10068
 * known exact covers -- that is the gate.
 *
 * Build: gcc -O3 -march=native -o code/bs6 code/blockstruct6.c
 * Run:   ./code/bs6 <Bmax> [solution cap]
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define N 6
#define NP 720
#define NC 120
#define NL 144
#define NB (NL * 21)

static unsigned char P[NP][N];
static int idx_of(const unsigned char *p)
{
    for (int i = 0; i < NP; i++)
        if (!memcmp(P[i], p, N)) return i;
    return -1;
}

static int cls[NP], aend[NP], dtar[NP], lid[NP];
static int loopcls[NL][N - 1];      /* the 5 classes of a loop, in delta order */

static void gen_perms(void)
{
    unsigned char a[N];
    for (int i = 0; i < N; i++) a[i] = i + 1;
    int cnt = 0;
    while (1) {
        memcpy(P[cnt++], a, N);
        int i = N - 2;
        while (i >= 0 && a[i] >= a[i + 1]) i--;
        if (i < 0) break;
        int j = N - 1;
        while (a[j] <= a[i]) j--;
        unsigned char t = a[i]; a[i] = a[j]; a[j] = t;
        for (int l = i + 1, r = N - 1; l < r; l++, r--) { t = a[l]; a[l] = a[r]; a[r] = t; }
    }
    if (cnt != NP) exit(1);
}

static void rot(const unsigned char *u, unsigned char *w)
{
    for (int i = 0; i < N - 1; i++) w[i] = u[i + 1];
    w[N - 1] = u[0];
}

typedef struct { unsigned long long a, b; } Mask;
static Mask bmask[NB];
static int bloop[NB], bstart[NB], blen[NB], nblocks;
static int byclass[NC][256], ncand[NC];

static void build(void)
{
    gen_perms();
    for (int i = 0; i < NP; i++) cls[i] = -1;
    int nc = 0;
    for (int i = 0; i < NP; i++) {
        if (cls[i] >= 0) continue;
        unsigned char x[N], y[N];
        memcpy(x, P[i], N);
        for (int k = 0; k < N; k++) {
            cls[idx_of(x)] = nc;
            rot(x, y); memcpy(x, y, N);
        }
        nc++;
    }
    if (nc != NC) exit(1);
    for (int i = 0; i < NP; i++) {
        unsigned char x[N], y[N];
        memcpy(x, P[i], N);
        for (int k = 0; k < N - 1; k++) { rot(x, y); memcpy(x, y, N); }
        aend[i] = idx_of(x);
    }
    for (int e = 0; e < NP; e++) {
        unsigned char d[N];
        for (int i = 0; i < N - 2; i++) d[i] = P[e][i + 2];
        d[N - 2] = P[e][1]; d[N - 1] = P[e][0];
        dtar[e] = idx_of(d);
    }
    for (int i = 0; i < NP; i++) lid[i] = -1;
    int nl = 0;
    for (int i = 0; i < NP; i++) {
        if (lid[i] >= 0) continue;
        int x = i, k = 0;
        do { lid[x] = nl; loopcls[nl][k] = cls[x]; k++; x = dtar[aend[x]]; }
        while (x != i);
        if (k != N - 1) exit(1);
        nl++;
    }
    if (nl != NL) { fprintf(stderr, "loops %d\n", nl); exit(1); }

    nblocks = 0;
    for (int L = 0; L < NL; L++)
        for (int len = 1; len <= N - 1; len++) {
            int nst = (len == N - 1) ? 1 : N - 1;
            for (int s = 0; s < nst; s++) {
                Mask m = {0, 0};
                for (int j = 0; j < len; j++) {
                    int c = loopcls[L][(s + j) % (N - 1)];
                    if (c < 64) m.a |= 1ULL << c; else m.b |= 1ULL << (c - 64);
                }
                bmask[nblocks] = m; bloop[nblocks] = L;
                bstart[nblocks] = s; blen[nblocks] = len;
                nblocks++;
            }
        }
    printf("pieces: %d (expect %d)\n", nblocks, NL * 21);

    for (int c = 0; c < NC; c++) ncand[c] = 0;
    for (int b = 0; b < nblocks; b++)
        for (int j = 0; j < blen[b]; j++) {
            int c = loopcls[bloop[b]][(bstart[b] + j) % (N - 1)];
            byclass[c][ncand[c]++] = b;
        }
    printf("pieces through a class: %d\n", ncand[0]);
}

static int Bmax;
static long long sols, cap, nodes;
static long long by_b[64];

static void dfs(Mask cov, int used, int rem)
{
    nodes++;
    if (rem == 0) { sols++; by_b[used]++; return; }
    if (used + (rem + N - 2) / (N - 1) > Bmax) return;
    if (sols >= cap) return;

    int c = -1;
    for (int i = 0; i < NC; i++) {
        unsigned long long bit = (i < 64) ? (cov.a >> i & 1) : (cov.b >> (i - 64) & 1);
        if (!bit) { c = i; break; }
    }
    for (int t = 0; t < ncand[c]; t++) {
        int b = byclass[c][t];
        if ((bmask[b].a & cov.a) || (bmask[b].b & cov.b)) continue;
        Mask nx = { cov.a | bmask[b].a, cov.b | bmask[b].b };
        dfs(nx, used + 1, rem - blen[b]);
        if (sols >= cap) return;
    }
}

int main(int argc, char **argv)
{
    Bmax = (argc > 1) ? atoi(argv[1]) : 24;
    cap  = (argc > 2) ? atoll(argv[2]) : 100000000LL;
    build();
    printf("counting block structures with B <= %d (cap %lld)\n", Bmax, cap);
    Mask z = {0, 0};
    sols = nodes = 0;
    memset(by_b, 0, sizeof by_b);
    dfs(z, 0, NC);
    printf("nodes = %lld,  structures = %lld%s\n", nodes, sols,
           sols >= cap ? "  (CAP HIT)" : "");
    for (int b = 0; b < 64; b++)
        if (by_b[b]) printf("  B = %2d : %lld\n", b, by_b[b]);
    return 0;
}
