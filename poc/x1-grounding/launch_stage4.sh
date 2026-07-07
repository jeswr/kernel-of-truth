#!/usr/bin/env bash
# Stage 4 launcher (PREREG §4.4, N_MS=300 fallback per §9 Amendment 4).
# Very gentle nice (box at load ~17 + live server); checkpoints every 25,
# resumable (run_range skips completed seeds). On completion it aggregates and
# re-runs nsm_test (now with MinSets -> full E-ms/E-inv) + report.
# The §6 verdict is already FAIL (E-core & E-kern fail, stages 1-3); MinSets add
# the two non-verdict-changing secondaries + the scaffold m(v).
set -e
cd "$(dirname "$0")"
echo "[stage4] start $(date -u +%FT%TZ)"
nice -n 18 python3 minsets.py --seed-start 0 --seed-end 300
nice -n 18 python3 minsets.py --aggregate --n-ms 300
nice -n 18 python3 nsm_test.py
nice -n 18 python3 report.py
echo "[stage4] done $(date -u +%FT%TZ)"
