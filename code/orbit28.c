/* orbit28.c -- independent cross-check of code/orbit28.py.
 *
 * Orbit 28 is the one S_6-orbit of exact covers that verify_orbits_tsp.py left
 * unresolved (FEASIBLE 267, certified only 265).  An exact cover fixes one
 * generator per rotation class, so the 120 full arcs are FIXED and only their
 * order is free.  The question is whether they can be strung into a walk of
 * total jump weight 266, i.e. E = 28, i.e. length 872 = s(6).
 *
 * This shares no code with the CP-SAT model: it reads the 120 generators from
 * data/orbit28_starts.txt and runs a plain branch-and-bound over E.
 *
 * Out of an arc end e the unique weight-2 (cost-0) successor is delta(e),
 * which lies in the same 2-loop; every other move costs weight - 2 >= 1.
 * Runs therefore cap at 5 = n-1, and with rem classes still uncovered and
 * freecap = 5 - curlen absorbable for free, at least ceil((rem-freecap)/5)
 * further blocks are needed, each costing >= 1.
 *
 * Build: gcc -O3 -march=native -o code/orbit28bb code/orbit28.c
 * Run:   ./code/orbit28bb <budget E> [nodecap]
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define N 6
#define NC 120

static unsigned char G[NC][N];      /* the fixed arc starts               */
static unsigned char END[NC][N];    /* sig^5 of each start = the arc end  */
static int wt[NC][NC];
static int freesucc[NC];            /* unique cost-0 successor, or -1     */
static int ord[NC][NC];             /* targets sorted by weight           */

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

static void load(void)
{
    FILE *f = fopen("data/orbit28_starts.txt", "r");
    if (!f) { fprintf(stderr, "need data/orbit28_starts.txt\n"); exit(1); }
    char line[64];
    int c = 0;
    while (c < NC && fgets(line, sizeof line, f)) {
        for (int i = 0; i < N; i++) G[c][i] = line[i] - '0';
        c++;
    }
    fclose(f);
    if (c != NC) { fprintf(stderr, "read %d starts\n", c); exit(1); }

    for (int i = 0; i < NC; i++) {           /* END = sig^5 = last rotation */
        END[i][0] = G[i][N - 1];
        for (int k = 1; k < N; k++) END[i][k] = G[i][k - 1];
    }
    for (int i = 0; i < NC; i++) {
        freesucc[i] = -1;
        for (int j = 0; j < NC; j++) {
            wt[i][j] = (i == j) ? 0 : weight(END[i], G[j]);
            if (i != j && wt[i][j] == 2) {
                if (freesucc[i] >= 0) { fprintf(stderr, "two free succs\n"); exit(1); }
                freesucc[i] = j;
            }
        }
    }
    for (int i = 0; i < NC; i++) {
        int k = 0;
        for (int w = 3; w <= N; w++)
            for (int j = 0; j < NC; j++)
                if (i != j && wt[i][j] == w) ord[i][k++] = j;
        while (k < NC) ord[i][k++] = -1;
    }
}

static int budget, cov, found;
static unsigned char used[NC];
static long long nodes, cap;
static int trail[NC];

static void dfs(int at, int cost, int curlen, int depth)
{
    if (found || ++nodes > cap) return;
    if (cov == NC) { found = 1; return; }

    int rem = NC - cov;
    int freecap = (N - 1) - curlen;
    int need = rem - freecap; if (need < 0) need = 0;
    if (cost + (need + N - 2) / (N - 1) > budget) return;

    int q = freesucc[at];
    if (q >= 0 && !used[q] && curlen < N - 1) {
        used[q] = 1; cov++; trail[depth] = q;
        dfs(q, cost, curlen + 1, depth + 1);
        cov--; used[q] = 0;
        if (found) return;
    }
    /* the bound below must hold AFTER the move: the new block has curlen = 1
     * and one more class is covered, so its free capacity is N-2. */
    int need2 = rem - 1 - (N - 2); if (need2 < 0) need2 = 0;
    int lo2 = (need2 + N - 2) / (N - 1);
    for (int t = 0; t < NC; t++) {
        int r = ord[at][t];
        if (r < 0) break;
        int c = cost + wt[at][r] - 2;
        if (c + lo2 > budget) break;            /* sorted by weight */
        if (used[r]) continue;
        used[r] = 1; cov++; trail[depth] = r;
        dfs(r, c, 1, depth + 1);
        cov--; used[r] = 0;
        if (found) return;
    }
}

int main(int argc, char **argv)
{
    budget = (argc > 1) ? atoi(argv[1]) : 28;
    cap = (argc > 2) ? atoll(argv[2]) : 200000000000LL;
    load();

    printf("orbit 28: %d fixed arcs, free start, budget E <= %d "
           "(total jump weight <= %d, length <= %d)\n",
           NC, budget, budget + 238, 844 + budget);

    int lo = (argc > 3) ? atoi(argv[3]) : 0;      /* start-node range, so the */
    int hi = (argc > 4) ? atoi(argv[4]) : NC;     /* 120 starts can be split  */
    nodes = 0; found = 0;
    for (int s0 = lo; s0 < hi && !found && nodes <= cap; s0++) {
        memset(used, 0, sizeof used);
        used[s0] = 1; cov = 1; trail[0] = s0;
        dfs(s0, 0, 1, 1);
    }
    printf("nodes = %lld%s\n", nodes, nodes > cap ? "  (CAP HIT)" : "");
    if (found) {
        printf("FEASIBLE: E <= %d achievable on orbit 28\n", budget);
        printf("  first arcs:");
        for (int i = 0; i < 8; i++) {
            printf(" ");
            for (int k = 0; k < N; k++) printf("%d", G[trail[i]][k]);
        }
        printf(" ...\n");
    } else if (nodes <= cap) {
        printf("IMPOSSIBLE: orbit 28 has no walk with E <= %d, so its TSP "
               "optimum is >= %d\n", budget, budget + 239);
    }
    return 0;
}
