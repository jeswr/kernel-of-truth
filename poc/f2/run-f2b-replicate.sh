#!/usr/bin/env bash
# run-f2b-replicate.sh — the SINGLE reproducible end-to-end launcher for the
# advisor RIGHT-SIZED f2b-replicate experiment (Opus-execution practice 2).
#
# A Fable agent must be able to run exactly this one script and audit
# inputs -> outputs. Everything is pinned:
#   frozen record sha  : registry/frozen-index.json[f2b-replicate]  (== record.frozen_sha256)
#   harness manifest   : record.pins.harness_manifest (staged-bytes sha; the
#                        Modal wrapper reprints it and the in-container check
#                        fails closed, ERR_STAGING_MISMATCH, on any drift)
#   corpus + models    : record.pins.corpus_hashes / record.pins.model_revisions
#                        (also mirrored in poc/f2b/inputs/f2b-manifest.json)
#
# Outputs (NOT auto-committed; review then commit deliberately):
#   run records : poc/f2b/results-incoming/<UTC-stamp>-modal/run-records-f2b.jsonl
#   provenance  : poc/f2b/results-incoming/<UTC-stamp>-modal/provenance.json
# Downstream (separate, run-vs-audit-separated) steps compute the verdict:
#   analysis    : analysis/f2b_replicate.py  (pinned; sha in the record)
#   verdict     : tools/registry/verdict-gen.py -> registry/verdicts/f2b-replicate.json
#   results-log : results-log/f2b-replicate.jsonl (append-only)
#
# LAUNCH GATES (all must hold; this script checks the mechanical ones):
#   1. record FROZEN and frozen_sha256 == frozen-index entry;
#   2. printed harness-manifest sha == record.pins.harness_manifest;
#   3. maintainer Tier-1 go (usd_cap $60, Tier-1 cap $80) — HUMAN gate, not
#      checkable here; the script refuses to launch without KOT_TIER1_GO=1.
#
# Usage:
#   poc/f2/run-f2b-replicate.sh --dry-plan     # $0 cost plan (default; safe)
#   KOT_TIER1_GO=1 poc/f2/run-f2b-replicate.sh --run   # the real A100 launch
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
MODAL="$ROOT/poc/modal/.venv/bin/modal"
PY="$ROOT/poc/modal/.venv/bin/python"
REC="registry/experiments/f2b-replicate.json"
GPU="a100"
MODE="${1:---dry-plan}"

echo "== f2b-replicate launcher =="
echo "repo root: $ROOT"

# --- gate 1: record FROZEN and sha matches the frozen index ------------------
"$PY" - "$ROOT" <<'PY'
import json, os, sys
root = sys.argv[1]
rec = json.load(open(os.path.join(root, "registry/experiments/f2b-replicate.json")))
idx = json.load(open(os.path.join(root, "registry/frozen-index.json")))
assert rec["status"] == "FROZEN", "record is not FROZEN (status=%s)" % rec["status"]
assert rec["frozen_sha256"] == idx["f2b-replicate"], "frozen_sha256 != frozen-index entry"
print("gate 1 OK: FROZEN, sha", rec["frozen_sha256"])
print("           harness_manifest pin", rec["pins"]["harness_manifest"])
print("           models", ", ".join("%s@%s" % (k, v.split("@")[-1][:12])
      for k, v in sorted(rec["pins"]["model_revisions"].items()) if isinstance(v, str) and "@" in v))
PY

# --- registry integrity (also re-verifies corpus pins reproduce) -------------
python3 tools/registry/registry-check.py >/dev/null && echo "gate: registry-check PASS"

if [ "$MODE" = "--dry-plan" ]; then
  echo "== --dry-plan (no GPU, no network, \$0) =="
  exec "$MODAL" run poc/modal/modal_f2b.py --gpu "$GPU" --dry-plan
fi

if [ "$MODE" != "--run" ]; then
  echo "usage: $0 [--dry-plan|--run]" >&2; exit 2
fi

# --- gate 3: maintainer Tier-1 go (human) ------------------------------------
if [ "${KOT_TIER1_GO:-0}" != "1" ]; then
  echo "REFUSING: set KOT_TIER1_GO=1 to confirm the maintainer Tier-1 go" >&2
  exit 3
fi

echo "== LAUNCH: single A100-40GB (the Modal wrapper reprints + in-container"
echo "   asserts the harness-manifest sha; ERR_STAGING_MISMATCH on any drift) =="
exec "$MODAL" run poc/modal/modal_f2b.py --gpu "$GPU"
