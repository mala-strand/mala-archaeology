#!/usr/bin/env bash
# Generate a random dream and store it in the database.
# Intended for cron or hobby-block use.
set -e
cd "$(dirname "$0")"
python3 worker/dream.py --length 300 --temperature 1.3 --era-jump-prob 0.06 --store "$@"
