#!/usr/bin/env bash
# E4 end-to-end runner driver (docs/poc-design.md E4 rev 2; bead
# kernel-of-truth-hkp). Consumes an E1 trainer work dir (READ-ONLY:
# $E1_WORK/data from poc/e1/pipeline/build_data.py + $E1_WORK/ckpts from
# poc/e1/train/train_e1.py) and the COMMITTED poc/e4 prep artifacts (never
# regenerated here) and runs: pin gates -> emission-shard build -> emission
# fine-tune (3 arms x paired seeds, E1 freezing discipline) -> 1,054-way
# candidate-restricted eval -> pre-registered stats + verdict.
#
#   run_e4.sh mock   tiny CPU end-to-end check (d=64, 2 seeds, --smoke data
#                    subset, MOCK tables): proves plumbing + frozen-row
#                    bit-identity THROUGH emission fine-tuning via
#                    runner/check_smoke.py — NEVER a result. Generates a mock
#                    E1 checkpoint with poc/e1's own trainer (tiny config) if
#                    $E1_WORK has none (poc/e1's mock smoke leaves one at
#                    /tmp/e1work-smoke; it is reused when present).
#   run_e4.sh full   the pre-registered E4 (GPU box, chained after the E1
#                    grid by poc/gpu/launch-e1-pull.sh --with-e4).
#
# FAIL-CLOSED PINS (before anything runs): sha-256(inputs/glosses.jsonl) must
# equal GLOSS-HASH.txt AND the holdout manifest's recorded hash (MAJOR 6);
# sha-256(inputs/vector-tables-manifest.json) must equal the holdout
# manifest's recorded vectorManifestSha256. build_emission.py re-verifies the
# gloss pin itself; finetune_e4.py sha-verifies every .f32 table it loads.
#
# Env: E1_WORK (default: full /opt/e1work; mock /tmp/e1work-smoke if it has
# the mock ckpts, else /tmp/e1work-e4smoke), E4_WORK (scratch), PYTHON,
# RESULTS_DIR (default: mock poc/e4/results — committed evidence; full
# $E4_WORK/results — published by the pull path). CPU-heavy work is nice'd.
set -euo pipefail

MODE="${1:?usage: run_e4.sh mock|full}"
HERE="$(cd "$(dirname "$0")" && pwd)"
E4="$(dirname "$HERE")"
E1="$(cd "$E4/../e1" && pwd)"
PYTHON="${PYTHON:-python3}"
NICE="nice -n 10"

# ---- [0/6] fail-closed pre-registration pins --------------------------------
PIN=$(sed -n 's/.*= \([0-9a-f]\{64\}\).*/\1/p' "$E4/GLOSS-HASH.txt" | head -1)
GOT=$(sha256sum "$E4/inputs/glosses.jsonl" | awk '{print $1}')
if [ -z "$PIN" ] || [ "$GOT" != "$PIN" ]; then
  echo "ERR_GLOSS_PIN: sha256(inputs/glosses.jsonl) = $GOT != published $PIN" \
       "(GLOSS-HASH.txt; a different gloss set is a NEW pre-registration)" >&2
  exit 1
fi
VSHA=$(sha256sum "$E4/inputs/vector-tables-manifest.json" | awk '{print $1}')
$NICE "$PYTHON" - "$E4/inputs/holdout-manifest.json" "$GOT" "$VSHA" <<'PYEOF'
import json, sys
m = json.load(open(sys.argv[1]))
assert m["artifact"] == "e4-holdout-manifest", "ERR_ARTIFACT: holdout manifest"
if m["inputs"]["glossesSha256"] != sys.argv[2]:
    raise SystemExit("ERR_GLOSS_PIN: holdout manifest pinned a different gloss set")
if m["inputs"]["vectorManifestSha256"] != sys.argv[3]:
    raise SystemExit("ERR_TABLES_PIN: holdout manifest pinned a different vector-tables manifest")
print("pins OK: glosses.jsonl + vector-tables-manifest.json match the pre-registration")
PYEOF

if [ "$MODE" = mock ]; then
  SEEDS="0,1"; SEED_LIST="0 1"
  if [ -z "${E1_WORK:-}" ]; then
    if [ -f /tmp/e1work-smoke/ckpts/ckpt-kernel-frozen-seed1-100pct.pt ]; then
      E1_WORK=/tmp/e1work-smoke
    else
      E1_WORK=/tmp/e1work-e4smoke
    fi
  fi
  E4_WORK="${E4_WORK:-/tmp/e4work-runner-smoke}"
  RESULTS="${RESULTS_DIR:-$E4/results}"
  BUILD_ARGS=(--seeds "$SEEDS" --exposure-per-concept 2 --smoke 30)
  FT_ARGS=(--batch-size 8 --total-tokens 200000 --lr 1e-3 --device cpu)
  STATS_EXTRA=(--mock)
  OUT_PREFIX="$RESULTS/verdict-e4-mock"
elif [ "$MODE" = full ]; then
  SEEDS="0,1,2,3,4"; SEED_LIST="0 1 2 3 4"
  E1_WORK="${E1_WORK:-/opt/e1work}"
  E4_WORK="${E4_WORK:-/tmp/e4work}"
  RESULTS="${RESULTS_DIR:-$E4_WORK/results}"
  BUILD_ARGS=(--seeds "$SEEDS")
  # Fixed fine-tune budget + LR, identical across arms (arms differ only in
  # frozen-row content, so the choice is arm-symmetric — no confound).
  FT_ARGS=(--batch-size 64 --total-tokens 10000000 --lr 1e-4)
  STATS_EXTRA=()
  OUT_PREFIX="$RESULTS/verdict-e4"
else
  echo "unknown mode: $MODE" >&2; exit 2
fi

ARMS=(kernel shuffled random)
E4DATA="$E4_WORK/e4data"
CKPTS="$E4_WORK/ckpts"
EVALS="$E4_WORK/evals"
mkdir -p "$E4_WORK" "$CKPTS" "$EVALS" "$RESULTS"

# ---- [1/6] mock only: an E1 kernel-frozen checkpoint to fine-tune ----------
if [ "$MODE" = mock ] && { [ ! -f "$E1_WORK/ckpts/ckpt-kernel-frozen-seed1-100pct.pt" ] \
    || [ ! -f "$E1_WORK/data/vocab.json" ] \
    || [ ! -f "$E1_WORK/vector-tables-mock-d64.json" ]; }; then
  echo "=== [1/6] generating mock E1 checkpoints (poc/e1 trainer, tiny config) ==="
  mkdir -p "$E1_WORK"
  # Mock corpus: generic simple-English sentences; NO gloss text (glosses must
  # never enter the LM-corpus side, even in a smoke) — poc/e4/smoke pattern.
  $NICE "$PYTHON" - "$E1_WORK/corpus.txt" <<'EOF'
import sys
sents = []
subj = ["the little dog", "a happy child", "the old man", "mom", "tom", "the bird",
        "a small cat", "the teacher", "grandma", "the boy"]
verb = ["saw", "found", "made", "took", "gave", "liked", "helped", "wanted", "heard", "knew"]
obj = ["a big red ball", "the shiny stone", "some sweet cake", "a new toy", "the open door",
       "a warm blanket", "the tall tree", "some cold water", "a funny hat", "the green book"]
tail = ["in the park", "at home", "near the river", "after lunch", "one sunny day",
        "before bed", "with a smile", "very fast", "again and again", "for a while"]
# 600 stories (~24k train tokens): enough for the e1 trainer's 128-token
# val/train windows (the poc/e4 data smoke's 60-story corpus is too small
# to TRAIN on — its val split is under one window).
for i in range(2400):
    sents.append(f"{subj[i % 10]} {verb[(i // 10) % 10]} {obj[(i // 100) % 10]} {tail[i % 7]} .")
stories = []
for i in range(0, len(sents), 4):
    stories.append(" ".join(sents[i:i + 4]))
with open(sys.argv[1], "w") as f:
    f.write("\n<|endoftext|>\n".join(stories) + "\n")
print(f"mock corpus: {len(stories)} stories")
EOF
  $NICE "$PYTHON" "$E1/pipeline/build_data.py" --corpus "$E1_WORK/corpus.txt" \
    --out "$E1_WORK/data" --seeds "$SEEDS" --vocab-size 4000
  $NICE "$PYTHON" "$E1/pipeline/mock_tables.py" --d 64 \
    --out "$E1_WORK/vector-tables-mock-d64.json" --seeds "$SEEDS"
  for SEED in $SEED_LIST; do
    $NICE "$PYTHON" "$E1/train/train_e1.py" --data "$E1_WORK/data" \
      --tables "$E1_WORK/vector-tables-mock-d64.json" \
      --arm kernel-frozen --seed "$SEED" --lr 1e-3 --out "$E1_WORK/ckpts" \
      --n-layer 2 --n-head 2 --d-model 64 --d-ff 128 --seq-len 128 \
      --batch-size 16 --total-tokens 409600 --allow-any-size --device cpu
  done
else
  echo "=== [1/6] E1 checkpoints: $E1_WORK/ckpts (reused, read-only) ==="
fi
for SEED in $SEED_LIST; do
  CK="$E1_WORK/ckpts/ckpt-kernel-frozen-seed$SEED-100pct.pt"
  [ -f "$CK" ] || { echo "missing E1 checkpoint $CK — run the E1 grid first" >&2; exit 1; }
done

# ---- [2/6] emission shards against the REAL e1 vocab (gloss pin re-checked) -
echo "=== [2/6] emission data build (seeds $SEEDS) ==="
$NICE "$PYTHON" "$E4/pipeline/build_emission.py" \
  --e1-vocab "$E1_WORK/data/vocab.json" --out "$E4DATA" "${BUILD_ARGS[@]}"
cp "$E4DATA/meta.json" "$RESULTS/e4-data-meta-$MODE.json"   # records the gloss OOV rate

# ---- [3/6] vector tables -----------------------------------------------------
if [ "$MODE" = mock ]; then
  echo "=== [3/6] MOCK e4 vector tables (d=64; authored rows = E1 mock kernel rows) ==="
  $NICE "$PYTHON" "$HERE/mock_tables_e4.py" --d 64 \
    --e1-tables "$E1_WORK/vector-tables-mock-d64.json" \
    --out "$E4_WORK/e4tables" --seeds "$SEEDS"
  TABLES="$E4_WORK/e4tables/vector-tables-mock-manifest.json"
else
  echo "=== [3/6] pinned e4 vector tables (kot-enc-Bq/1 @512) ==="
  TABLES="$E4/inputs/vector-tables-manifest.json"
fi

# ---- [4/6] emission fine-tune: 3 arms x paired seeds ------------------------
echo "=== [4/6] emission fine-tuning grid: ${#ARMS[@]} arms x seeds ($SEED_LIST) ==="
for ARM in "${ARMS[@]}"; do
  for SEED in $SEED_LIST; do
    echo "--- fine-tune: $ARM seed=$SEED ---"
    $NICE "$PYTHON" "$HERE/finetune_e4.py" \
      --e1-ckpt "$E1_WORK/ckpts/ckpt-kernel-frozen-seed$SEED-100pct.pt" \
      --e1-data "$E1_WORK/data" --e4-data "$E4DATA" --tables "$TABLES" \
      --arm "$ARM" --seed "$SEED" --out "$CKPTS" "${FT_ARGS[@]}"
  done
done

# ---- [5/6] 1,054-way candidate-restricted eval ------------------------------
echo "=== [5/6] evals ==="
for ARM in "${ARMS[@]}"; do
  for SEED in $SEED_LIST; do
    $NICE "$PYTHON" "$HERE/eval_e4.py" \
      --ckpt "$CKPTS/ckpt-e4-$ARM-seed$SEED-final.pt" --e4-data "$E4DATA" \
      --out "$EVALS/eval-e4-$ARM-seed$SEED.json"
  done
done

# ---- [6/6] pre-registered statistics + verdict ------------------------------
echo "=== [6/6] pre-registered statistics + verdict ==="
$NICE "$PYTHON" "$HERE/stats_e4.py" --evals "$EVALS" --meta "$E4DATA/meta.json" \
  --seeds "$SEEDS" --out-prefix "$OUT_PREFIX" "${STATS_EXTRA[@]}"

if [ "$MODE" = mock ]; then
  for f in "$EVALS"/eval-e4-*.json; do
    cp "$f" "$RESULTS/mock-$(basename "$f")"    # never shadowed by full-run evals
  done
  echo "=== independent runner smoke assertions ==="
  $NICE "$PYTHON" "$HERE/check_smoke.py" --e1-ckpts "$E1_WORK/ckpts" \
    --e4-ckpts "$CKPTS" --e4-data "$E4DATA" --evals "$EVALS" --tables "$TABLES" \
    --verdict "$OUT_PREFIX.json" --results "$RESULTS" --seeds "$SEEDS"
  echo "smoke work dirs: $E1_WORK $E4_WORK (delete when done)"
else
  cp "$EVALS"/eval-e4-*.json "$RESULTS/" 2>/dev/null || true
  cp "$CKPTS"/summary-e4-*.json "$CKPTS"/train-e4-*.jsonl "$RESULTS/" 2>/dev/null || true
fi

echo "=== done: $OUT_PREFIX.{json,md} ==="
