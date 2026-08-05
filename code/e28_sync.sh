#!/bin/sh
# Mirror COMPLETED shard logs from the live run's scratch dir into the durable
# checkpoint dir, so a /tmp cleanup (or a reboot) cannot lose finished work.
# Only logs carrying a completion line are copied; partial ones are left out so
# that code/e28_run.sh correctly treats them as still to do.
SRC=${1:-/tmp/e28}
DST=${2:-.e28}
cd "$(dirname "$0")/.."
mkdir -p "$DST"
while :; do
    grep -l "IMPOSSIBLE on this shard\|FEASIBLE" "$SRC"/*.log 2>/dev/null \
        | xargs -r -I{} cp -u {} "$DST"/ 2>/dev/null
    sleep 180
done
