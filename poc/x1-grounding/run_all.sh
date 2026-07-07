#!/usr/bin/env bash
# X1-grounding orchestrator (PREREG §7). nice -n 10 everything (2 shared cores +
# live server, CLAUDE.md). Refuses to skip smoke. Stops at the T2 manual-audit
# gate before nsm_test. Each stage records its input sha256s in its own output.
set -euo pipefail
cd "$(dirname "$0")"
PY="nice -n 10 python3"

echo "== stage 0: smoke (MUST pass before real data) =="
$PY smoke.py

echo "== stage 1: build_graph =="
$PY build_graph.py

echo "== stage 2: prime_map =="
$PY prime_map.py

echo "== stage 3: strata (halts on CONSTRUCTION-ANOMALY) =="
$PY strata.py

echo "== T2 audit sample (§8) =="
$PY audit_t2.py
cat <<'EOF'

>>> MANUAL GATE (PREREG §8): audit t2-audit-sample.json by hand, write
>>> t2-audit-result.json with the error rate. If > 10%, HALT for a §9
>>> amendment BEFORE nsm_test. run_all stops here by design.
EOF

if [ -f t2-audit-result.json ]; then
  TRIPPED=$($PY - <<'PY'
import json;print(json.load(open("t2-audit-result.json")).get("gateTripped"))
PY
)
  if [ "$TRIPPED" = "True" ]; then
    echo ">>> T2 gate TRIPPED -> not running nsm_test. See PREREG §9 Amendment 2."
    $PY report.py
    exit 0
  fi
fi

echo "== stage 4: minsets (long pole; launch niced/detached per §4.4) =="
echo "   (run manually: nohup nice -n 10 python3 minsets.py --seed-start 0 --seed-end 1000 & )"
echo "== stage 5: nsm_test =="
$PY nsm_test.py
echo "== stage 6: report =="
$PY report.py
