#!/bin/bash
# Archaeology Worker Runner — Phase 1
# Called by cron nightly 01:00-05:30
# Pure Python, zero tokens
# Phase 1: 92 texts downloaded, needs co-occurrence + vectors

set -e

cd "$(dirname "$0")"

# Check control file
CONTROL=$(cat control 2>/dev/null || echo "run")
if [ "$CONTROL" != "run" ]; then
    echo "Control signal is '$CONTROL' — not starting worker"
    exit 0
fi

# Load gate: check system load and memory
LOAD=$(awk '{print $1}' /proc/loadavg)
LOAD_INT=${LOAD%.*}
MEM_AVAIL=$(free -m | awk '/^Mem:/{print $7}')
MEM_TOTAL=$(free -m | awk '/^Mem:/{print $2}')
MEM_PCT=$(echo "scale=2; $MEM_AVAIL / $MEM_TOTAL" | bc)

echo "Load: $LOAD | Mem avail: ${MEM_AVAIL}MB / ${MEM_TOTAL}MB (${MEM_PCT}%)"

if [ "$LOAD_INT" -ge 2 ]; then
    echo "Load too high ($LOAD) — skipping this window"
    exit 0
fi

if [ "$(echo "$MEM_PCT < 0.25" | bc)" -eq 1 ]; then
    echo "Memory too low (${MEM_PCT}%) — skipping this window"
    exit 0
fi

echo "Starting archaeology Phase 1 worker..."

# Phase 1: Build co-occurrence matrix from downloaded texts
# (92 texts downloaded, 8000 vocab built — needs cooc + vectors)
echo "Step 1: Building co-occurrence matrix (streaming)..."
python3 worker/streaming_cooccurrence.py cooc

echo "Step 2: Building word vectors..."
python3 worker/streaming_cooccurrence.py vectors

echo "Worker run complete."
