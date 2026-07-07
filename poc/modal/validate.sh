#!/usr/bin/env bash
# Token-FREE validation gate for the Modal port (bead kernel-of-truth-0oj).
# Never makes an authenticated Modal call; safe on the shared CPU box (niced).
#
#   bash poc/modal/validate.sh
#
# 1. unit suite (system python3, Modal STUBBED): staging/unpack/provenance
#    logic + a full wrapper round-trip against the REAL e2_runner.py --mock;
# 2. real-modal import (poc/modal/.venv): app/image/volume construction is
#    lazy in the modal client, so `import modal_e2` proves the wiring parses
#    against the PINNED client without any account;
# 3. CLI presence: `modal run modal_e2.py --help` resolves the entrypoint +
#    flags — the exact command a token-holder will run, minus execution.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
VENV="$HERE/.venv"
NICE="nice -n 10"

if [ ! -x "$VENV/bin/python" ]; then
  echo "== creating venv (one-time; pinned client from requirements.txt) =="
  python3 -m venv "$VENV"
  "$VENV/bin/pip" install --quiet -r "$HERE/requirements.txt"
fi

echo "== [1/3] unit suite (Modal stubbed; real e2_runner --mock round-trip) =="
$NICE python3 -m unittest discover -s "$HERE" -p 'test_*.py' -v

echo "== [2/3] tokenless import against the REAL pinned modal client =="
$NICE "$VENV/bin/python" -c "
import sys; sys.path.insert(0, '$HERE')
import modal, modal_e2, modal_e1e4
assert modal_e2.app.name == 'kot-e2' and modal_e1e4.app.name == 'kot-e1e4'
assert sorted(modal_e2.GPU_FUNCTIONS) == ['A10G', 'T4']
print('import OK against modal', modal.__version__)
"

echo "== [3/3] modal CLI presence + entrypoint resolution (no token) =="
"$VENV/bin/modal" --version
( cd "$HERE" && "$VENV/bin/modal" run modal_e2.py --help > /dev/null )
echo "modal run modal_e2.py --help OK"

echo
echo "ALL GREEN — once a token exists (modal token new), run:"
echo "  $VENV/bin/modal run $HERE/modal_e2.py --mock   # transport smoke, ~pennies"
echo "  $VENV/bin/modal run $HERE/modal_e2.py          # full pre-registered E2"
