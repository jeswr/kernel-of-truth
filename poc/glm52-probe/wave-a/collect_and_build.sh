#!/usr/bin/env bash
# collect_and_build.sh — after the Modal Wave-A run finishes, pull its outputs
# off the named output Volume and build the Stage-2 expert atlas locally ($0).
# EXPLORATORY infra. Usage:  bash collect_and_build.sh [full|tiny]
set -euo pipefail
SUB="${1:-full}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../../.." && pwd)"
MODAL="$REPO/poc/modal/.venv/bin/modal"
RAW="$HERE/raw/$SUB"
OUT="$HERE/atlas"
VOL="kot-glm52-wave-a-out"

set -a; source ~/.config/kot/modal4.env; set +a
mkdir -p "$RAW"
for fn in agg.json trace_summary.json facts.json wave-report.json trace_manifest.txt \
          rtrace.jsonl.gz wave_a_corpus.json; do
  "$MODAL" volume get --force "$VOL" "$SUB/$fn" "$RAW/$fn" || echo "WARN: $fn missing"
done

python3 "$HERE/build_atlas.py" \
  --agg "$RAW/agg.json" \
  --corpus "$RAW/wave_a_corpus.json" \
  --corpus-manifest "$HERE/corpus/corpus_manifest.json" \
  --ledger "$REPO/poc/glm52-probe/expert_ledger.csv" \
  --integrity "$RAW/trace_summary.json" \
  --out-dir "$OUT"
echo "atlas written to $OUT"
