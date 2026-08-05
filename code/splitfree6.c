/* splitfree6.c -- is there a SPLIT-FREE 6-symbol superpermutation of the
 * minimal length 872?
 *
 * s(6) = 872 is known, and length = n + n! - 2 + R + E = 844 + E once R = 120,
 * so every 6-superpermutation has E >= 28 and a champion has E = 28 exactly.
 * A walk is SPLIT-FREE when every rotation class is covered by ONE full arc,
 * i.e. R = (n-1)! = 120.  So the question is a single feasibility test:
 *
 *      is there a split-free walk over the 120 classes with E <= 28 ?
 *
 * If not, split-free => length >= 873 > 872, and NO n = 6 champion is
 * split-free -- the "champions must have splits" hypothesis, proved one
 * dimension down.
 *
 * Encoding.  A full arc is determined by its starting permutation p: it covers
 * all n permutations of p's rotation class and ends at sigma^(n-1)(p).  From
 * that end e the walk jumps to the next arc's start q at cost weight(e,q) - 2;
 * E is the total.  Weight 2 out of a full arc is exactly delta (sigma^2 lands
 * back inside the class just covered), so the cost-0 move is unique and is the
 * "stay in this 2-loop" move.
 *
 * Relabelling the symbols preserves all overlap weights and acts simply
 * transitively on the 720 permutations, so the first arc may be fixed to start
 * at the identity.
 *
 * Bound used for pruning: with rem classes still uncovered and the current
 * block able to absorb freecap = (n-1) - curlen of them for free, at least
 * ceil(max(0, rem - freecap) / (n-1)) further blocks are needed and each costs
 * at least 1.
 *
 * Build: gcc -O3 -march=native -o code/splitfree6 code/splitfree6.c
 * Run:   ./code/splitfree6 <budget> [nodecap]
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define N 6
#define NP 720            /* permutations   */
#define NC 120            /* rotation classes = (n-1)! */

static unsigned char P[NP][N];
static int idx_of(const unsigned char *p)
{
    for (int i = 0; i < NP; i++)
        if (!memcmp(P[i], p, N)) return i;
    return -1;
}

static int cls[NP];               /* class id of each permutation      */
static int aend[NP];              /* end of the full arc starting here */
static int dtar[NP];              /* delta out of an arc END           */
static int wt[NP][NP];            /* overlap weights                   */
static int *order[NP];            /* targets sorted by weight          */

static void gen_perms(void)
{
    unsigned char a[N];
    for (int i = 0; i < N; i++) a[i] = i + 1;
    int cnt = 0;
    /* plain lexicographic generation */
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
    if (cnt != NP) { fprintf(stderr, "perm count %d\n", cnt); exit(1); }
}

static void rot(const unsigned char *u, unsigned char *w)   /* sigma */
{
    for (int i = 0; i < N - 1; i++) w[i] = u[i + 1];
    w[N - 1] = u[0];
}

static int weight(const unsigned char *u, const unsigned char *w)
{
    for (int k = 1; k <= N; k++) {
        int ok = 1;
        for (int i = 0; i < N - k; i++)
            if (u[k + i] != w[i]) { ok = 0; break; }
        if (ok) return k;
    }
    return N;
}

static void build(void)
{
    gen_perms();

    /* rotation classes: orbit of sigma */
    for (int i = 0; i < NP; i++) cls[i] = -1;
    int nc = 0;
    for (int i = 0; i < NP; i++) {
        if (cls[i] >= 0) continue;
        unsigned char x[N];
        memcpy(x, P[i], N);
        for (int k = 0; k < N; k++) {
            cls[idx_of(x)] = nc;
            unsigned char y[N]; rot(x, y); memcpy(x, y, N);
        }
        nc++;
    }
    if (nc != NC) { fprintf(stderr, "classes %d\n", nc); exit(1); }

    /* arc end = sigma^(n-1)(p);  delta out of an end */
    for (int i = 0; i < NP; i++) {
        unsigned char x[N], y[N];
        memcpy(x, P[i], N);
        for (int k = 0; k < N - 1; k++) { rot(x, y); memcpy(x, y, N); }
        aend[i] = idx_of(x);
    }
    for (int e = 0; e < NP; e++) {
        unsigned char d[N];
        for (int i = 0; i < N - 2; i++) d[i] = P[e][i + 2];
        d[N - 2] = P[e][1];
        d[N - 1] = P[e][0];
        dtar[e] = idx_of(d);
    }

    for (int i = 0; i < NP; i++)
        for (int j = 0; j < NP; j++)
            wt[i][j] = weight(P[i], P[j]);

    /* per-end target ordering by increasing weight (counting sort) */
    for (int e = 0; e < NP; e++) {
        order[e] = malloc(sizeof(int) * NP);
        int k = 0;
        for (int w = 1; w <= N; w++)
            for (int q = 0; q < NP; q++)
                if (wt[e][q] == w) order[e][k++] = q;
    }
}

/* ---- search ------------------------------------------------------------- */
static int budget, covered_cnt, found, maxw;
static unsigned char covered[NC];
static long long nodes, node_cap;
static int trail[NC];

static void dfs(int e, int cost, int curlen, int depth)
{
    if (found || ++nodes > node_cap) return;
    if (covered_cnt == NC) { found = 1; return; }

    int rem = NC - covered_cnt;
    int freecap = (N - 1) - curlen;
    int need = rem - freecap; if (need < 0) need = 0;
    if (cost + (need + N - 2) / (N - 1) > budget) return;

    /* cost-0 move: delta, staying inside this 2-loop */
    int q = dtar[e];
    if (!covered[cls[q]] && curlen < N - 1) {
        covered[cls[q]] = 1; covered_cnt++; trail[depth] = q;
        dfs(aend[q], cost, curlen + 1, depth + 1);
        covered_cnt--; covered[cls[q]] = 0;
        if (found) return;
    }
    /* costed moves, cheapest first.
     * NOTE the bound here must be the one that applies AFTER the move: the
     * new block has curlen = 1, so its free capacity is (n-1)-1 = n-2 and one
     * more class is covered.  Using the pre-move `need` (which is computed
     * from the CURRENT block's capacity) over-prunes and can discard real
     * solutions -- that bug made the E = 29 soundness gate fail. */
    int need2 = rem - 1 - (N - 2); if (need2 < 0) need2 = 0;
    int lo2 = (need2 + N - 2) / (N - 1);
    for (int t = 0; t < NP; t++) {
        int r = order[e][t];
        int w = wt[e][r];
        if (w < 3) continue;
        if (w > maxw) break;                 /* sorted by weight */
        int c = cost + w - 2;
        if (c + lo2 > budget) break;                       /* sorted by w */
        if (covered[cls[r]]) continue;
        covered[cls[r]] = 1; covered_cnt++; trail[depth] = r;
        dfs(aend[r], c, 1, depth + 1);
        covered_cnt--; covered[cls[r]] = 0;
        if (found) return;
    }
}

int main(int argc, char **argv)
{
    budget = (argc > 1) ? atoi(argv[1]) : 28;
    node_cap = (argc > 2) ? atoll(argv[2]) : 100000000000LL;
    maxw     = (argc > 3) ? atoi(argv[3]) : N;   /* cap on jump weight */
    build();

    printf("n = 6, split-free: %d classes, one full arc each\n", NC);
    printf("length = 844 + E;  s(6) = 872 means a champion has E = 28\n");
    printf("budget E <= %d  (length <= %d), max jump weight %d, node cap %lld\n",
           budget, 844 + budget, maxw, node_cap);
    if (maxw == 3)
        printf("  maxw = 3 => every jump costs exactly 1 => E = B-1, Y = 0.\n"
               "  With E <= 28 that is the case B <= 29, Y = 0; and since\n"
               "  s(6) = 872, any solution must have B = 29 exactly.\n");

    memset(covered, 0, sizeof covered);
    covered[cls[0]] = 1; covered_cnt = 1; trail[0] = 0;   /* start at identity */
    nodes = 0; found = 0;
    dfs(aend[0], 0, 1, 1);

    printf("nodes = %lld%s\n", nodes,
           nodes > node_cap ? "  (CAP HIT -- inconclusive)" : "");
    if (found) {
        printf("FEASIBLE: a split-free walk with E <= %d exists "
               "(length <= %d)\n", budget, 844 + budget);
        printf("first arc starts: ");
        for (int i = 0; i < 8; i++) {
            for (int k = 0; k < N; k++) printf("%d", P[trail[i]][k]);
            printf(" ");
        }
        printf("...\n");
    } else if (nodes <= node_cap) {
        printf("IMPOSSIBLE: no split-free walk has E <= %d, "
               "so split-free => length >= %d\n", budget, 845 + budget);
    }
    return 0;
}
