#!/usr/bin/env bash
# Launch 4 codex draft calls CONCURRENTLY; measure each wall + total wall.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
declare -a TAGS=(03-v-run 05-v-go 09-a-bright 11-r-up)
START=$(date +%s.%N)
pids=()
for tag in "${TAGS[@]}"; do
  ( t0=$(date +%s.%N)
    bash "$HERE/run_codex_draft.sh" "$HERE/out/runs/$tag/prompt.txt" "$HERE/out/parallel/$tag" >/dev/null 2>&1
    t1=$(date +%s.%N)
    echo "$tag $(echo "$t1 - $t0" | bc)" >> "$HERE/out/parallel/times.txt"
  ) &
  pids+=($!)
done
for p in "${pids[@]}"; do wait "$p"; done
END=$(date +%s.%N)
echo "TOTAL_WALL $(echo "$END - $START" | bc)" >> "$HERE/out/parallel/times.txt"
