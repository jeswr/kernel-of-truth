#!/usr/bin/env bash
# Token-FREE validation gate for the Modal port (beads kernel-of-truth-0oj E2,
# kernel-of-truth-af7 E1+E4). Never makes an authenticated Modal call; safe on
# the shared CPU box (niced).
#
#   bash poc/modal/validate.sh              # unit suites + imports + dry-plan
#   bash poc/modal/validate.sh --mock-e2e   # ...plus the tiny-config CPU mock
#                                           # of BOTH E1+E4 stages through the
#                                           # wrapper (needs torch: provisions
#                                           # a DISPOSABLE venv under /tmp,
#                                           # ~900 MB, delete after — poc/e1
#                                           # house practice; never installed
#                                           # into the repo or system python)
#
# 1. E2 unit suite (system python3, Modal STUBBED): staging/unpack/provenance
#    logic + a full wrapper round-trip against the REAL e2_runner.py --mock;
# 2. E1+E4 unit suite (Modal STUBBED): wiring, driver-fidelity (bash arrays +
#    heredocs parsed from run_all.sh / run_e4.sh), fail-closed gates
#    (staging manifest, GLOSS-HASH, tables pin), dry-plan; the mock-E2E class
#    auto-skips without torch and runs under --mock-e2e;
# 3. real-modal import (poc/modal/.venv): app/image/volume construction is
#    lazy in the modal client, so importing both apps proves the wiring
#    parses against the PINNED client without any account;
# 4. CLI presence: `modal run modal_e2.py --help` resolves entrypoint+flags;
# 5. --dry-plan for E1+E4 via the pinned client: call graph + GPU-h + $.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
VENV="$HERE/.venv"
NICE="nice -n 10"
MOCK_E2E=no
[ "${1:-}" = "--mock-e2e" ] && MOCK_E2E=yes

if [ ! -x "$VENV/bin/python" ]; then
  echo "== creating venv (one-time; pinned client from requirements.txt) =="
  python3 -m venv "$VENV"
  "$VENV/bin/pip" install --quiet -r "$HERE/requirements.txt"
fi

echo "== [1/5] E2 unit suite (Modal stubbed; real e2_runner --mock round-trip) =="
$NICE python3 -m unittest discover -s "$HERE" -p 'test_modal_port.py' -v

echo "== [2/5] E1+E4 unit suite (Modal stubbed; torch tests skip if absent) =="
E1E4_PY=python3
if [ "$MOCK_E2E" = yes ]; then
  MOCKVENV="${KOT_MOCK_VENV:-${TMPDIR:-/tmp}/kot-e1e4-mockvenv}"
  if [ ! -x "$MOCKVENV/bin/python" ]; then
    echo "-- provisioning DISPOSABLE torch venv at $MOCKVENV (delete after) --"
    python3 -m venv "$MOCKVENV"
    $NICE "$MOCKVENV/bin/pip" install --quiet --no-cache-dir \
      --index-url https://download.pytorch.org/whl/cpu \
      --extra-index-url https://pypi.org/simple \
      "numpy>=1.24" "torch>=2.2"
  fi
  E1E4_PY="$MOCKVENV/bin/python"
fi
( cd "$HERE" && $NICE "$E1E4_PY" -m unittest test_modal_e1e4 -v )
if [ "$MOCK_E2E" = yes ]; then
  echo "-- mock E2E ran under $E1E4_PY; disposable venv can now be deleted:"
  echo "   rm -rf $MOCKVENV"
fi

echo "== [3/5] tokenless import against the REAL pinned modal client =="
$NICE "$VENV/bin/python" -c "
import sys; sys.path.insert(0, '$HERE')
import modal, modal_e2, modal_e1e4, modal_e1e4_lib
assert modal_e2.app.name == 'kot-e2' and modal_e1e4.app.name == 'kot-e1e4'
assert sorted(modal_e2.GPU_FUNCTIONS) == ['A10G', 'T4']
assert sorted(modal_e1e4.FUNCTION_SETS) == ['A10G', 'T4']
import os
missing = [r for r in modal_e1e4_lib.STAGE_FILES
           if not os.path.isfile(os.path.join('$HERE', '..', '..', r))]
assert not missing, f'staged files missing: {missing}'
print('import OK against modal', modal.__version__)
"

echo "== [4/5] modal CLI presence + entrypoint resolution (no token) =="
"$VENV/bin/modal" --version
( cd "$HERE" && "$VENV/bin/modal" run modal_e2.py --help > /dev/null )
echo "modal run modal_e2.py --help OK"
( cd "$HERE" && "$VENV/bin/modal" run modal_e1e4.py --help > /dev/null )
echo "modal run modal_e1e4.py --help OK"

echo "== [5/5] E1+E4 --dry-plan (real client, zero Modal calls) =="
$NICE "$VENV/bin/python" "$HERE/modal_e1e4.py" --dry-plan

echo
echo "ALL GREEN — once a token exists (modal token new), run:"
echo "  $VENV/bin/modal run $HERE/modal_e2.py --mock     # E2 transport smoke"
echo "  $VENV/bin/modal run $HERE/modal_e2.py            # full pre-registered E2"
echo "  $VENV/bin/modal run $HERE/modal_e1e4.py --mock   # E1+E4 transport smoke"
echo "  $VENV/bin/modal run $HERE/modal_e1e4.py          # full E1 grid + E4 chain"