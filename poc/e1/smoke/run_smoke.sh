#!/usr/bin/env bash
# E1 mock smoke test (bead kernel-of-truth-bk0): tiny CPU end-to-end run on
# the TinyStories sample slice, then independent checkpoint-level assertions
# (frozen-row bit-identity etc.). NEVER a result — pipeline mechanics only.
#
# Usage: E1_CORPUS=<TinyStories-valid.txt> [PYTHON=...] [E1_WORK=...] run_smoke.sh
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
E1="$(dirname "$HERE")"
export E1_WORK="${E1_WORK:-/tmp/e1work-smoke}"
export PYTHON="${PYTHON:-python3}"
: "${E1_CORPUS:?set E1_CORPUS to the TinyStories sample slice (.txt)}"

nice -n 10 bash "$E1/run_all.sh" mock

nice -n 10 "$PYTHON" "$HERE/check_smoke.py" "$E1_WORK/ckpts" "$E1/results" 0,1
echo "smoke work dir: $E1_WORK (delete when done: rm -rf $E1_WORK)"
