"""Census: every superpermutation on disk, measured in ledger coordinates.

This repo had no place where the known strings were measured together.  The
four walks quoted in `ledger.py` were hand-entered from `lemma_arsenal.md` 6,
all at n <= 7.  This file measures everything it can find and asserts the
MASTER IDENTITY

    T  =  (n-1) d  +  (B + Y)  -  A,        d = v - (n-2)!,

on each one, so the ledger model is backed by machine measurement rather than
transcription.  It also records HPV-tightness (T == v), which is the hypothesis
the whole design table rests on.

Reuses, and deliberately does not reimplement:
  permgraph.string_to_path   string -> walk
  blockcount.Model.measure   length, R, S, v, A, ...  (asserts 4 identities)
  dirty.dissect              B, Y, clean, dirty, n_partial, N, f

Sources scanned (upstream is optional and skipped if absent):
  data/n7/, data/houston_872.txt
  /home/lk/superperm-upstream/superpermutations/{5,6,7,8,9}/

Usage:
  python3 code/census.py               # everything, writes data/census.json
  python3 code/census.py --max-n 8     # skip n = 9 (slow)
  python3 code/census.py --summary     # re-read the json, print the table
"""

import argparse
import glob
import gzip
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from blockcount import Model                                     # noqa: E402
from dirty import dissect                                        # noqa: E402
from permgraph import string_to_path                             # noqa: E402

UPSTREAM = "/home/lk/superperm-upstream/superpermutations"
OUT = "data/census.json"


def base(n):
    return n + math.factorial(n) + math.factorial(n - 1) - 3


def hpv(n):
    return (math.factorial(n) + math.factorial(n - 1)
            + math.factorial(n - 2) + n - 3)


def read_text(path):
    """Decoded text of a file, or None.  Sniffs magic bytes, not extensions."""
    try:
        with open(path, "rb") as fh:
            head = fh.read(2)
            fh.seek(0)
            if head == b"\x1f\x8b":
                return gzip.decompress(fh.read()).decode("ascii", "ignore")
            if head == b"PK":
                return None                      # zip archive, not a string
            return fh.read().decode("ascii", "ignore")
    except OSError:
        return None


def read_strings(path):
    """EVERY superpermutation in a file, one per line.

    Files here hold anything from one string to 42,288 of them
    (`872-treelike.txt.gz`), and the n=7 `nsk*` files hold up to 52.  Reading
    only the first line -- which this function used to do -- silently threw
    away most of the corpus.
    """
    raw = read_text(path)
    if raw is None:
        return []
    out = []
    for line in raw.split():
        line = line.strip()
        if line.isdigit() and len(line) > 4:
            out.append([int(c) for c in line])
    return out


def read_string(path):
    """First superpermutation in a file (kept for callers that want one)."""
    got = read_strings(path)
    return got[0] if got else None


# Ferried to `champions6.py` instead: 43,096 strings would swamp this census.
BULK6 = {"872-treelike.txt.gz", "872-treelike-slack1.txt.gz",
         "872-treelike-slack2.txt"}


def sources(max_n):
    """(n, label, path) for every candidate file."""
    out = []
    for p in sorted(glob.glob("data/n7/*.txt")):
        out.append((7, "local/" + os.path.basename(p), p))
    for p in sorted(glob.glob("data/n9/*.txt")):
        out.append((9, "local/" + os.path.basename(p), p))
    if os.path.exists("data/houston_872.txt"):
        out.append((6, "local/houston_872.txt", "data/houston_872.txt"))
    for n in range(5, max_n + 1):
        d = os.path.join(UPSTREAM, str(n))
        if not os.path.isdir(d):
            continue
        for name in sorted(os.listdir(d)):
            p = os.path.join(d, name)
            if os.path.isfile(p) and name not in BULK6:
                out.append((n, f"up{n}/{name}", p))
    return out


def measure_one(n, digits):
    """Full ledger coordinate vector for one string, with the identity check."""
    if max(digits) != n or min(digits) != 1:
        return None
    path = string_to_path(digits, n)
    if len(path) != math.factorial(n):
        return None                       # not a superpermutation
    m = Model(n)
    core = m.measure(path)                # asserts arc/jump, split, block, SBY
    dis = dissect(m, path)

    F2 = math.factorial(n - 2)
    v, A, S = core["v"], core["A"], core["S"]
    B, Y = dis["B"], dis["Y"]
    T = S + B + Y
    d = v - F2

    # ---- the master identity ------------------------------------------
    assert T == (n - 1) * d + (B + Y) - A, ("master identity", n, T)
    assert core["length"] == base(n) + T, ("SBY", n)

    # build.coords re-derives the same vector from the arc list alone, and
    # adds the ordering-free quantities (comps) and the multiplicity data.
    from build import coords, design_of
    c = coords(design_of(path), n)
    for k, ref in (("R", core["R"]), ("S", S), ("v", v), ("A", A),
                   ("B", B), ("Y", Y), ("N", dis["N"]),
                   ("dirty", dis["dirty"]), ("n_partial", dis["n_partial"])):
        assert c[k] == ref, (k, c[k], ref)

    return dict(n=n, length=core["length"], T=T, v=v, d=d, A=A, S=S,
                B=B, Y=Y, BYA=B + Y - A, R=core["R"], N=dis["N"],
                dirty=dis["dirty"], n_partial=dis["n_partial"], f=dis["f"],
                comps=c["comps"], mu_max=c["mu_max"], m=c["m"],
                hpv_tight=(T == v), excess=core["length"] - hpv(n))


def run(max_n, cap_per_file=None):
    rows, skipped = [], []
    for n, label, path in sources(max_n):
        got = read_strings(path)
        if not got:
            skipped.append((label, "unreadable"))
            continue
        if cap_per_file:
            got = got[:cap_per_file]
        kept = 0
        for i, digits in enumerate(got):
            try:
                r = measure_one(n, digits)
            except AssertionError as e:
                print(f"  !! {label}[{i}]: IDENTITY FAILURE {e}", flush=True)
                raise
            if r is None:
                continue
            r["label"] = label if len(got) == 1 else f"{label}#{i}"
            rows.append(r)
            kept += 1
        if kept == 0:
            skipped.append((label, "not a superpermutation"))
            continue
        r = rows[-1]
        note = "" if kept == 1 else f"  [{kept} strings]"
        print(f"  {label:<44} len={r['length']:<7} T={r['T']:<6} "
              f"d={r['d']:<5} A={r['A']:<4} S={r['S']:<6} B={r['B']:<6} "
              f"Y={r['Y']:<5} B+Y-A={r['BYA']:<6} "
              f"{'tight' if r['hpv_tight'] else 'slack'}{note}", flush=True)
    return rows, skipped


def summarise(rows):
    print(f"\n--- census: {len(rows)} strings, master identity holds on all "
          f"{len(rows)} ---")
    print(f"  {'n':>3} {'strings':>8} {'best len':>10} {'HPV(n)':>10} "
          f"{'excess':>8} {'tight':>7} {'B+Y-A at best':>15}")
    for n in sorted({r["n"] for r in rows}):
        sub = [r for r in rows if r["n"] == n]
        best = min(sub, key=lambda r: r["length"])
        tight = sum(1 for r in sub if r["hpv_tight"])
        print(f"  {n:>3} {len(sub):>8} {best['length']:>10} {hpv(n):>10} "
              f"{best['excess']:>8} {tight:>4}/{len(sub):<3} {best['BYA']:>15}")

    print("\n  saving over Egan = (B+Y-A)/(n-2), checked at each record:")
    for n in sorted({r["n"] for r in rows}):
        sub = [r for r in rows if r["n"] == n]
        best = min(sub, key=lambda r: r["length"])
        egan = base(n) + (n - 1) * math.factorial(n - 3) if n >= 4 else None
        if egan is None or not best["hpv_tight"]:
            continue
        pred = best["BYA"] / (n - 2)
        actual = egan - best["length"]
        ok = abs(pred - actual) < 1e-9
        print(f"    n={n}: (B+Y-A)/(n-2) = {best['BYA']}/{n-2} = {pred:g}"
              f"   Egan {egan} - record {best['length']} = {actual}"
              f"   {'OK' if ok else 'MISMATCH'}")
        assert ok, (n, pred, actual)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-n", type=int, default=9)
    ap.add_argument("--summary", action="store_true")
    args = ap.parse_args()

    if args.summary:
        rows = json.load(open(OUT))
        summarise(rows)
        sys.exit(0)

    print(__doc__.split("Reuses,")[0].strip())
    print()
    rows, skipped = run(args.max_n)
    summarise(rows)
    if skipped:
        print(f"\n  skipped {len(skipped)}: "
              + ", ".join(f"{a} ({b})" for a, b in skipped[:8])
              + (" ..." if len(skipped) > 8 else ""))
    os.makedirs("data", exist_ok=True)
    json.dump(rows, open(OUT, "w"), indent=1)
    print(f"\n  wrote {OUT}")
