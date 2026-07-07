#!/usr/bin/env bash
# E1 end-to-end driver (docs/poc-design.md E1; bead kernel-of-truth-bk0).
#
#   run_all.sh mock   tiny CPU pipeline check on the sample slice (2 layers,
#                     d=64, 200 steps, seeds 0-1, MOCK vector tables) — proves
#                     plumbing + freezing-mask bit-identity, NEVER a result.
#   run_all.sh full   the pre-registered grid (GPU box): data build (5 seeds),
#                     per-condition LR sweep on seed 0 (Common rule 5),
#                     5 arms x 5 seeds, evals incl. step-0 baselines, stats,
#                     verdict.
#
# Env: E1_CORPUS (TinyStories txt; REQUIRED), E1_WORK (scratch dir, default
# /tmp/e1work), PYTHON (default python3). Everything CPU-heavy is nice'd.
set -euo pipefail

MODE="${1:?usage: run_all.sh mock|full}"
HERE="$(cd "$(dirname "$0")" && pwd)"
PYTHON="${PYTHON:-python3}"
WORK="${E1_WORK:-/tmp/e1work}"
CORPUS="${E1_CORPUS:?set E1_CORPUS to a TinyStories .txt split}"
RESULTS="$HERE/results"
mkdir -p "$WORK" "$RESULTS"
NICE="nice -n 10"

if [ "$MODE" = mock ]; then
  SEEDS="0,1"; SEED_LIST="0 1"
  TABLES="$WORK/vector-tables-mock-d64.json"
  MODEL_ARGS=(--n-layer 2 --n-head 2 --d-model 64 --d-ff 128 --seq-len 128
              --batch-size 16 --total-tokens 409600 --allow-any-size --device cpu)
  DATA_ARGS=(--vocab-size 4000 --max-train-tokens 500000)
  LRS=(1e-3)   # no sweep in mock: fixed LR, machinery exercised by the grid itself
  STATS_EXTRA=(--mock)
  OUT_PREFIX="$RESULTS/verdict-e1-mock"
elif [ "$MODE" = full ]; then
  SEEDS="0,1,2,3,4"; SEED_LIST="0 1 2 3 4"
  TABLES="$HERE/inputs/vector-tables-d512.json"
  MODEL_ARGS=(--n-layer 4 --n-head 8 --d-model 512 --d-ff 2048 --seq-len 256
              --batch-size 64 --total-tokens 200000000)
  DATA_ARGS=(--vocab-size 8000 --max-train-tokens 210000000)
  LRS=(3e-4 6e-4 1e-3)  # per-condition sweep grid, seed 0, half budget
  STATS_EXTRA=()
  OUT_PREFIX="$RESULTS/verdict-e1"
else
  echo "unknown mode: $MODE" >&2; exit 2
fi

ARMS=(kernel-frozen shuffled-frozen random-frozen trainable kernel-init)
DATA="$WORK/data"
CKPTS="$WORK/ckpts"
EVALS="$WORK/evals"
mkdir -p "$CKPTS" "$EVALS"

echo "=== [1/5] data pipeline (seeds $SEEDS) ==="
$NICE "$PYTHON" "$HERE/pipeline/build_data.py" --corpus "$CORPUS" --out "$DATA" \
  --seeds "$SEEDS" "${DATA_ARGS[@]}"

if [ "$MODE" = mock ]; then
  echo "=== [1b] MOCK vector tables (d=64) ==="
  $NICE "$PYTHON" "$HERE/pipeline/mock_tables.py" --d 64 --out "$TABLES" --seeds "$SEEDS"
fi

echo "=== [2/5] per-condition LR selection (Common rule 5) ==="
LRSEL="$WORK/lr-selection.json"
if [ ${#LRS[@]} -gt 1 ]; then
  for ARM in "${ARMS[@]}"; do
    for LR in "${LRS[@]}"; do
      echo "--- sweep: $ARM lr=$LR (seed 0, half budget) ---"
      $NICE "$PYTHON" "$HERE/train/train_e1.py" --data "$DATA" --tables "$TABLES" \
        --arm "$ARM" --seed 0 --lr "$LR" --out "$CKPTS/sweep" \
        --budget-frac 0.5 --no-checkpoints "${MODEL_ARGS[@]}"
    done
  done
  $NICE "$PYTHON" - "$CKPTS/sweep" "$LRSEL" <<'PYEOF'
import glob, json, sys
sweep_dir, out = sys.argv[1], sys.argv[2]
best = {}
for p in glob.glob(f"{sweep_dir}/summary-*.json"):
    s = json.load(open(p))
    k = s["arm"]
    v = s["final"]["valLoss"]
    if k not in best or v < best[k][1]:
        best[k] = (s["lr"], v)
sel = {k: {"lr": v[0], "valLoss": v[1]} for k, v in best.items()}
json.dump({"rule": "seed 0 only, best of sweep by val loss, then fixed for all seeds "
                   "(poc-design Common rule 5)", "selected": sel}, open(out, "w"), indent=2)
print(json.dumps(sel, indent=2))
PYEOF
else
  $NICE "$PYTHON" - "$LRSEL" "${LRS[0]}" <<'PYEOF'
import json, sys
lr = float(sys.argv[2])
sel = {a: {"lr": lr, "valLoss": None} for a in
       ("kernel-frozen", "shuffled-frozen", "random-frozen", "trainable", "kernel-init")}
json.dump({"rule": f"mock mode: fixed lr={lr}, no sweep", "selected": sel},
          open(sys.argv[1], "w"), indent=2)
PYEOF
fi
cp "$LRSEL" "$RESULTS/lr-selection-$MODE.json"

echo "=== [3/5] training grid: ${#ARMS[@]} arms x seeds ($SEED_LIST) ==="
for ARM in "${ARMS[@]}"; do
  LR=$("$PYTHON" -c "import json,sys; print(json.load(open('$LRSEL'))['selected']['$ARM']['lr'])")
  for SEED in $SEED_LIST; do
    echo "--- train: $ARM seed=$SEED lr=$LR ---"
    $NICE "$PYTHON" "$HERE/train/train_e1.py" --data "$DATA" --tables "$TABLES" \
      --arm "$ARM" --seed "$SEED" --lr "$LR" --out "$CKPTS" "${MODEL_ARGS[@]}"
  done
done

echo "=== [4/5] evals (incl. step-0 circularity baselines) ==="
eval_one() { # arm seed tag
  local f="$CKPTS/ckpt-$1-seed$2-$3.pt"
  [ -f "$f" ] || { echo "missing checkpoint $f" >&2; exit 1; }
  $NICE "$PYTHON" "$HERE/eval/eval_e1.py" --ckpt "$f" --data "$DATA" \
    --out "$EVALS/eval-$1-seed$2-$3.json"
}
for SEED in $SEED_LIST; do
  eval_one kernel-frozen "$SEED" step0
  eval_one kernel-frozen "$SEED" 50pct
  eval_one kernel-frozen "$SEED" 100pct
  eval_one shuffled-frozen "$SEED" 100pct
  eval_one random-frozen "$SEED" 100pct
  eval_one trainable "$SEED" 100pct
  eval_one kernel-init "$SEED" 100pct
done

echo "=== [5/5] pre-registered statistics + verdict ==="
$NICE "$PYTHON" "$HERE/eval/stats_e1.py" --evals "$EVALS" --seeds "$SEEDS" \
  --out-prefix "$OUT_PREFIX" "${STATS_EXTRA[@]}"
cp "$DATA/meta.json" "$RESULTS/data-meta-$MODE.json"
for f in "$EVALS"/eval-*.json; do
  [ -e "$f" ] || continue
  if [ "$MODE" = mock ]; then
    cp "$f" "$RESULTS/mock-$(basename "$f")"   # never shadowed by full-run evals
  else
    cp "$f" "$RESULTS/"
  fi
done

echo "=== done: $OUT_PREFIX.{json,md} ==="
