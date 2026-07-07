#!/usr/bin/env bash
# E9-defl CPU end-to-end mock smoke + planted/null stat controls (poc/e9
# README "Controls before real spend"; bead kernel-of-truth-xj2). Disposable
# venv on DISK (this box's /tmp is RAM-backed), niced, mechanics only.
set -euo pipefail
E9_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="${E9_SMOKE_VENV:-$HOME/.e5-smoke-venv}"   # same disposable venv as poc/e5's smoke
OUT="$E9_DIR/results/smoke-out"
LOG="$E9_DIR/results/runner-smoke-log.txt"

mkdir -p "$E9_DIR/results"
if [ ! -x "$VENV/bin/python" ]; then
  echo "creating disposable venv at $VENV (torch CPU wheels)"
  python3 -m venv "$VENV"
  nice -n 10 "$VENV/bin/pip" install --quiet --upgrade pip
  nice -n 10 "$VENV/bin/pip" install --quiet numpy "transformers>=4.44,<5"
  nice -n 10 "$VENV/bin/pip" install --quiet torch --index-url https://download.pytorch.org/whl/cpu
fi

rm -rf "$OUT"
{
  echo "$ e9_runner.py --mock --device cpu  ($(date -u +%FT%TZ))"
  nice -n 10 "$VENV/bin/python" "$E9_DIR/runner/e9_runner.py" \
    --inputs-dir "$E9_DIR/inputs" --out-dir "$OUT" --device cpu --mock
  nice -n 10 "$VENV/bin/python" "$E9_DIR/runner/check_smoke.py" "$OUT"
} 2>&1 | tee "$LOG"

cp "$OUT/verdict-e9-mock.md" "$E9_DIR/results/"
cp "$OUT/results-e9-mock.json" "$E9_DIR/results/"
echo "smoke evidence: results/verdict-e9-mock.md results/results-e9-mock.json $LOG"
echo "delete the venv when done: rm -rf $VENV"
