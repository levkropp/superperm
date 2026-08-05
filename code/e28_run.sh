#!/bin/sh
# Resume-aware driver for the n = 6 split-free decision run: is there a
# split-free walk with E <= 28, i.e. a split-free 6-superpermutation of the
# minimal length 872?
#
# The search is split into NSHARDS deterministic shards: every worker walks the
# identical tree down to DEPTH and then keeps every NSHARDS-th node at that
# depth.  The partition depends only on (binary, budget, maxw, NSHARDS, DEPTH),
# so a shard that finished is finished for good and never needs redoing.  That
# makes the run resumable at shard granularity: rerun exactly those shards whose
# log lacks a completion line.
#
# A shard killed mid-flight leaves a log with no completion line and is simply
# redone.  Shard sizes are very uneven (1e8 to 1e11 nodes), so losing the worst
# one costs a few hours -- raise NSHARDS if that matters.
#
# GUARD: resume is only valid while the binary is unchanged, since a different
# bound changes which nodes land in which shard.  The checksum used for the
# first run is recorded in $WORK/binary.md5 and checked on every resume.
#
#   ./code/e28_run.sh            resume (or start) the run
#   ./code/e28_run.sh status     progress only, start nothing

set -e
cd "$(dirname "$0")/.."

BIN=code/sf6c
WORK=${E28_WORK:-.e28}
NSHARDS=${NSHARDS:-2000}
DEPTH=${DEPTH:-8}
BUDGET=${BUDGET:-28}
MAXW=6
NODECAP=2000000000000
JOBS=${JOBS:-20}

mkdir -p "$WORK"
[ -x "$BIN" ] || { echo "missing $BIN -- gcc -O3 -march=native -o $BIN code/splitfree6b.c"; exit 1; }
SUM=$(md5sum "$BIN" | awk '{print $1}')

# `grep -l` exits 1 when nothing matches, which is the normal case here, so
# every call is guarded -- otherwise set -e aborts the script on good news.
done_shards() { grep -l "IMPOSSIBLE on this shard\|FEASIBLE" "$WORK"/*.log 2>/dev/null | wc -l || true; }
feasible()    { grep -l "FEASIBLE" "$WORK"/*.log 2>/dev/null || true; }

status() {
    set +e
    d=$(done_shards)
    n=$(grep -h '^nodes = ' "$WORK"/*.log 2>/dev/null | awk '{s+=$3} END {printf "%.3e", s+0}')
    echo "shards finished : $d / $NSHARDS"
    echo "nodes so far    : ${n:-0}"
    echo "workers alive   : $(pgrep -c -x "$(basename $BIN)" 2>/dev/null || echo 0)"
    f=$(feasible)
    if [ -n "$f" ]; then
        echo "*** FEASIBLE -- a split-free 872 EXISTS.  See: $f"
    elif [ "$d" -ge "$NSHARDS" ]; then
        echo "*** COMPLETE: every shard IMPOSSIBLE at E <= $BUDGET."
        echo "    split-free => E >= $((BUDGET + 1)), i.e. length >= $((845 + BUDGET))."
        if [ "$BUDGET" -ge 28 ]; then
            echo "    Since s(6) = 872 = 844 + 28, that closes it:"
            echo "    NO n = 6 CHAMPION IS SPLIT-FREE."
        else
            echo "    (Only the full BUDGET = 28 run settles the champion question;"
            echo "     s(6) = 872 already gives E >= 28 for free.)"
        fi
    fi
    set -e
    return 0
}

[ "$1" = status ] && { status; exit 0; }


if [ -f "$WORK/binary.md5" ]; then
    OLD=$(cat "$WORK/binary.md5")
    if [ "$OLD" != "$SUM" ]; then
        echo "REFUSING TO RESUME: $BIN has changed since the finished shards were"
        echo "computed ($OLD -> $SUM).  The shard partition depends on the bound,"
        echo "so old results are not comparable.  Delete $WORK to start over."
        exit 1
    fi
else
    echo "$SUM" > "$WORK/binary.md5"
fi

# Soundness gate: the search must still FIND the classical 873 at E <= 29.
# Every over-pruning bug in this project was caught here and nowhere else.
if ! "$BIN" 29 20000000000 | grep -q FEASIBLE; then
    echo "GATE FAILED: $BIN cannot find the known E = 29 walk.  Refusing to run."
    exit 1
fi

todo=$(mktemp)
i=0
while [ "$i" -lt "$NSHARDS" ]; do
    if ! grep -q "IMPOSSIBLE on this shard\|FEASIBLE" "$WORK/$i.log" 2>/dev/null; then
        echo "$i" >> "$todo"
    fi
    i=$((i + 1))
done
echo "resuming: $(wc -l < "$todo") shards left of $NSHARDS, $JOBS at a time"

xargs -P "$JOBS" -I{} sh -c \
    "$BIN $BUDGET $NODECAP $MAXW $NSHARDS {} $DEPTH > $WORK/{}.log 2>&1" < "$todo"
rm -f "$todo"
status
