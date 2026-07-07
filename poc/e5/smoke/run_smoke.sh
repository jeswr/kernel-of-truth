#!/usr/bin/env bash
# E5 CPU end-to-end mock smoke (bead kernel-of-truth-c24; poc/e1/e4 house
# practice: disposable venv, niced, mechanics only — proves the pipeline +
# scoring + pre-registered stats end-to-end on a tiny random-init model, then
# runs INDEPENDENT assertions (runner/check_smoke.py). Evidence lands in
# poc/e5/results/.
set -euo pipefail
E5_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# Disk, not tmpfs: this box's /tmp is RAM-backed and small (CSS box constraints).
VENV="${E5_SMOKE_VENV:-$HOME/.e5-smoke-venv}"
OUT="$E5_DIR/results/smoke-out"
LOG="$E5_DIR/results/runner-smoke-log.txt"

mkdir -p "$E5_DIR/results"
if [ ! -x "$VENV/bin/python" ]; then
  echo "creating disposable venv at $VENV (torch CPU wheels)"
  python3 -m venv "$VENV"
  nice -n 10 "$VENV/bin/pip" install --quiet --upgrade pip
  nice -n 10 "$VENV/bin/pip" install --quiet numpy "transformers>=4.44,<5"
  nice -n 10 "$VENV/bin/pip" install --quiet torch --index-url https://download.pytorch.org/whl/cpu
fi

rm -rf "$OUT"
{
  echo "$ e5_runner.py --mock --device cpu  ($(date -u +%FT%TZ))"
  nice -n 10 "$VENV/bin/python" "$E5_DIR/runner/e5_runner.py" \
    --inputs-dir "$E5_DIR/inputs" --out-dir "$OUT" --device cpu --mock
  nice -n 10 "$VENV/bin/python" "$E5_DIR/runner/check_smoke.py" "$OUT"
} 2>&1 | tee "$LOG"

# keep the small evidence files in results/, drop the bulky per-run artifacts
cp "$OUT/verdict-e5-mock.md" "$E5_DIR/results/"
cp "$OUT/results-e5-mock.json" "$E5_DIR/results/"
echo "smoke evidence: results/verdict-e5-mock.md results/results-e5-mock.json $LOG"
