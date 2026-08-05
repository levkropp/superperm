/* Exact capacities M_7(G) for the n=7 relaxed macro-chain system.
 *
 * Break state z = z0..z6, a permutation of 0..6.
 *   P(z)   = (z0, z6, z1, z2, z3, z4, z5)         marker z0 fixed
 *   A_g(z) = { rotClass(P^i z) : g <= i < 6 }     support, size 6-g
 *   I(z)   = (z2,z3,z4,z5),  O(z) = (z3,z4,z5,z6)
 *   macro (z,g): costs g, covers A_g(z), successor z' has I(z') = O(P^g z)
 *
 * M_7(G) = max macros in a chain of total gap <= G with pairwise-disjoint
 * supports.  Reproduces the a7 bundle table; --nodes gives unpruned node
 * counts for cross-checking.
 *
 * build: gcc -O3 -march=native -o macro7 macro7.c
 * usage: ./macro7 GMAX [--nodes] [--prune]
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define NS 5040          /* break states */
#define NC 720           /* rotation classes */
#define MW 12            /* 720 bits */

static int  perm[NS][7];
static int  sid_of[7][7][7][7][7][7][7];
static int  support[NS][6][6];      /* [state][gap] -> up to 6 class ids */
static int  supn[NS][6];
static int  succ[NS][6][6];

static uint64_t used[MW];
static long long nodes;
static int best;
static int use_prune;
static int Wcap[256];               /* valid upper bound on M_7(g) */

static int fact7[8] = {1,1,2,6,24,120,720,5040};

static int rotclass_id(const int *p)
{
    /* canonical rotation, then rank it by lexicographic index of the rep */
    int bestr[7], t[7], i, k, c;
    for (i = 0; i < 7; i++) bestr[i] = p[i];
    for (k = 1; k < 7; k++) {
        for (i = 0; i < 7; i++) t[i] = p[(i + k) % 7];
        for (c = 0; c < 7; c++) { if (t[c] != bestr[c]) break; }
        if (c < 7 && t[c] < bestr[c]) memcpy(bestr, t, sizeof t);
    }
    /* Lehmer rank of the canonical representative */
    int rank = 0;
    for (i = 0; i < 7; i++) {
        int less = 0;
        for (int j = i + 1; j < 7; j++) if (bestr[j] < bestr[i]) less++;
        rank += less * fact7[6 - i];
    }
    return rank;
}

static int classmap[5040];   /* Lehmer rank of canonical rep -> 0..719 */

static void build(void)
{
    int idx = 0, a,b,c,d,e,f,g;
    for (a=0;a<7;a++) for (b=0;b<7;b++) { if(b==a) continue;
    for (c=0;c<7;c++) { if(c==a||c==b) continue;
    for (d=0;d<7;d++) { if(d==a||d==b||d==c) continue;
    for (e=0;e<7;e++) { if(e==a||e==b||e==c||e==d) continue;
    for (f=0;f<7;f++) { if(f==a||f==b||f==c||f==d||f==e) continue;
    for (g=0;g<7;g++) { if(g==a||g==b||g==c||g==d||g==e||g==f) continue;
        perm[idx][0]=a;perm[idx][1]=b;perm[idx][2]=c;perm[idx][3]=d;
        perm[idx][4]=e;perm[idx][5]=f;perm[idx][6]=g;
        sid_of[a][b][c][d][e][f][g]=idx; idx++;
    }}}}}}
    if (idx != NS) { fprintf(stderr,"state build %d\n", idx); exit(1); }

    for (int i = 0; i < 5040; i++) classmap[i] = -1;
    int nclass = 0;
    for (int s = 0; s < NS; s++) {
        int r = rotclass_id(perm[s]);
        if (classmap[r] < 0) classmap[r] = nclass++;
    }
    if (nclass != NC) { fprintf(stderr,"classes %d\n", nclass); exit(1); }

    for (int s = 0; s < NS; s++) {
        int orb[6][7];
        memcpy(orb[0], perm[s], sizeof orb[0]);
        for (int i = 1; i < 6; i++) {
            const int *z = orb[i-1]; int *o = orb[i];
            o[0]=z[0]; o[1]=z[6]; o[2]=z[1]; o[3]=z[2];
            o[4]=z[3]; o[5]=z[4]; o[6]=z[5];
        }
        int cls[6];
        for (int i = 0; i < 6; i++) cls[i] = classmap[rotclass_id(orb[i])];
        for (int gp = 0; gp < 6; gp++) {
            supn[s][gp] = 6 - gp;
            for (int i = gp; i < 6; i++) support[s][gp][i-gp] = cls[i];
            const int *y = orb[gp];
            int pre[4] = { y[3], y[4], y[5], y[6] };
            int rest[3], nr = 0;
            for (int v = 0; v < 7; v++) {
                int in = 0;
                for (int i = 0; i < 4; i++) if (pre[i]==v) in = 1;
                if (!in) rest[nr++] = v;
            }
            int k = 0;
            for (int i = 0; i < 3; i++)
              for (int j = 0; j < 3; j++) {
                if (j==i) continue;
                int m = 3 - i - j;
                succ[s][gp][k++] =
                  sid_of[rest[i]][rest[j]][pre[0]][pre[1]][pre[2]][pre[3]][rest[m]];
              }
            if (k != 6) { fprintf(stderr,"succ %d\n", k); exit(1); }
        }
    }
}

static int curz[128], curg[128], bestz[128], bestg[128], bestlen;

static void rec(int z, int budget, int depth)
{
    nodes++;
    if (depth > best) {
        best = depth;
        bestlen = depth;
        memcpy(bestz, curz, sizeof(int) * depth);
        memcpy(bestg, curg, sizeof(int) * depth);
    }
    if (use_prune && depth + Wcap[budget] <= best) return;
    int gmax = budget < 5 ? budget : 5;
    for (int gp = 0; gp <= gmax; gp++) {
        const int *sup = support[z][gp];
        int n = supn[z][gp], i, ok = 1;
        for (i = 0; i < n; i++)
            if (used[sup[i] >> 6] >> (sup[i] & 63) & 1ULL) { ok = 0; break; }
        if (!ok) continue;
        for (i = 0; i < n; i++) used[sup[i] >> 6] |= 1ULL << (sup[i] & 63);
        curz[depth] = z; curg[depth] = gp;
        for (i = 0; i < 6; i++) rec(succ[z][gp][i], budget - gp, depth + 1);
        for (i = 0; i < n; i++) used[sup[i] >> 6] &= ~(1ULL << (sup[i] & 63));
    }
}

int main(int argc, char **argv)
{
    int gmax = argc > 1 ? atoi(argv[1]) : 10;
    int show_nodes = 0, seed = 0, only = -1;
    for (int i = 2; i < argc; i++) {
        if (!strcmp(argv[i], "--nodes")) show_nodes = 1;
        if (!strcmp(argv[i], "--prune")) use_prune = 1;
        if (!strcmp(argv[i], "--seed")) seed = atoi(argv[++i]);
        if (!strcmp(argv[i], "--only")) only = atoi(argv[++i]);
    }
    build();

    static const int refM[] = {5,5,9,9,13,13,16,16,20,20,24,24,
                               27,27,31,31,34,34,36,38,40,41};
    const int nref = (int)(sizeof refM / sizeof refM[0]);

    /* Bootstrap: exact[0..g-1] are values this program has already PROVEN.
     * The pruning cap at step g is the partition closure of that verified
     * prefix only -- never of the published table -- so nothing is circular. */
    int exact[256], nex = 0;

    printf("%3s %8s %6s %14s   %s\n", "G", "M_7(G)", "ref",
           show_nodes ? "nodes" : "", "prune cap source");
    for (int G = 0; G <= gmax; G++) {
        if (nex == 0) {
            use_prune = 0;                    /* G=0 has no prefix to lean on */
        } else {
            int r[512], top = exact[nex - 1];
            for (int k = 1; k <= top; k++) { int gg = 0; while (exact[gg] < k) gg++; r[k] = gg; }
            r[top + 1] = nex;                 /* certified: needs budget >= nex */
            static int D[8192];
            D[0] = 0;
            for (int L = 1; L < 8192; L++) {
                int b = -1;
                for (int k = 1; k <= top + 1 && k <= L; k++) {
                    int t = r[k] + D[L - k];
                    if (t > b) b = t;
                }
                D[L] = b;
            }
            for (int g = 0; g < 256; g++) {
                int m = 0;
                for (int l = 0; l < 8192; l++) if (D[l] <= g) m = l;
                Wcap[g] = m;
            }
            use_prune = 1;
        }
        /* seeding with the previous exact value is sound: M_7 is nondecreasing
         * and that length was already realised by a witness. */
        int s0 = (only >= 0 && seed) ? seed : (nex ? exact[nex - 1] - 1 : 0);
        if (only >= 0 && G != only) continue;

        memset(used, 0, sizeof used);
        nodes = 0; best = s0;
        rec(sid_of[0][1][2][3][4][5][6], G, 0);

        const char *tag = (G < nref) ? (best == refM[G] ? "OK" : "MISMATCH") : "NEW";
        if (show_nodes)
            printf("%3d %8d %6s %14lld   cap from M_7(0..%d)\n",
                   G, best, tag, nodes, nex - 1);
        else
            printf("%3d %8d %6s %14s   cap from M_7(0..%d)\n",
                   G, best, tag, "", nex - 1);
        fflush(stdout);
        if (only >= 0 || G == gmax) {
            FILE *f = fopen("witness.txt", "w");
            fprintf(f, "%d %d\n", G, bestlen);
            for (int i = 0; i < bestlen; i++) {
                for (int k = 0; k < 7; k++) fprintf(f, "%d", perm[bestz[i]][k]);
                fprintf(f, " %d\n", bestg[i]);
            }
            fclose(f);
        }
        exact[nex++] = best;
    }
    return 0;
}
