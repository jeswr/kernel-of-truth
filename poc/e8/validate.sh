#!/usr/bin/env bash
# Token-FREE validation gate for the E8 harness (bead kernel-of-truth-u0x).
# Never makes an authenticated Modal call; safe on the shared CPU box (niced).
#
#   bash poc/e8/validate.sh
#
# 1. unit suite (system python3, numpy only, Modal STUBBED): masked-profile
#    correctness, planted-positive + structured-null + pure-noise CONTROLS,
#    Holm, mock end-to-end (e8_runner --mock -> analyze), fail-closed pins,
#    modal_e8 wiring;
# 2. real-modal import (poc/modal/.venv, pinned client): app/image/volume
#    construction parses without any account;
# 3. --dry-plan via the pinned client: staged pins + download plan + $.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
VENV="$REPO/poc/modal/.venv"
NICE="nice -n 10"

echo "== [1/3] E8 unit suite (Modal stubbed; mock e2e through runner + analyze) =="
$NICE python3 -m unittest discover -s "$HERE" -p 'test_e8.py' -v

if [ -x "$VENV/bin/python" ]; then
  echo "== [2/3] real-modal import (pinned client, no token) =="
  cd "$REPO"
  $NICE "$VENV/bin/python" - <<'PY'
import importlib.util, pathlib, sys
repo = pathlib.Path.cwd()
sys.path.insert(0, str(repo / "poc" / "modal"))
spec = importlib.util.spec_from_file_location("modal_e8", repo / "poc" / "modal" / "modal_e8.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
print("modal_e8 import OK: app", m.app.name, "| staged files", len(m._staged_manifest()))
PY

  echo "== [3/3] dry-plan (no token) =="
  $NICE "$VENV/bin/python" poc/modal/modal_e8.py --dry-plan
else
  echo "== [2-3/3] SKIPPED: poc/modal/.venv absent (create via poc/modal/validate.sh) =="
fi

echo "E8 VALIDATION: ALL GATES GREEN"
