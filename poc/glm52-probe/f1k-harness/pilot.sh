#!/usr/bin/env bash
# =============================================================================
# pilot.sh — F1-K pilot bring-up: the (L,g) selection + the pre-test gates.
#
# RUN BY THE COORDINATOR on the bring-up'd instance (after bringup.sh and the
# documented model fetch + weight-hash pin). NOT run against a real model in
# the build pass; `pilot.sh --mock` exercises the identical code path against
# the stub engine for $0.
#
# What the pilot does (all frozen-protocol, implemented in f1k_driver.py
# --phase pilot; sources cited in that file's constants):
#   * scores the 3 layer-sets x 3 g grid on the 48-item stratified dev
#     subset over the 4-member FAMILY-BLIND carrier panel
#     {K-true, K-derangement (pilot seed 11), d2-family, d0-family (seed 7)}
#     [f1k.json design.n_planned.pilot; design §R4/§R-REV2.3]
#   * selection statistic = EQUAL FAMILY-LEVEL weight mean (carrier-blind:
#     invariant to mapping truth AND to carrier family) [§R-REV3.2/ASM-2113];
#     tie-break fewer spliced layers, then lower g [§R4]
#     NOTE: the grid's g values are MULTIPLIERS; realized KAE_G =
#     multiplier x mean native expert weight [design §2.3], and the pilot
#     dev subset is the freeze-manifest (A) COMMITTED id list
#   * freezes (L,g) -> addendum-5-frozen-lg.json (a deterministic argmax:
#     the pure-function addendum (5) of §R-REV2.4), after FULL panel
#     validation (seed 11 / d0 seed 7 / {2,1,1} family partition / carrier
#     identities / norm matching / derangement reconstruction)
#   * POST-FREEZE dev-96 passes (b0, K, d0-family, and REPLACE when the
#     engine supports it) at the frozen (L,g) [design §R3.2: dev inputs
#     come from dev-96 AFTER the freeze, never from the 48-item subset]
#   * bring-up measurements -> addendum-7-affordability.json: measured
#     s/prefill (resume-safe ledger), cost projection vs the $149 ceiling,
#     with the §R6 degradation order applied deterministically (R 5->3
#     pre-applied; defer REPLACE; then defer d3-text — HONORED in the test
#     schedule; then STOP), + the ASM-1971 semantics attestation
#   * addendum-6 INPUTS -> addendum-6-inputs.json: dev-96 delta-hat at its
#     one-sided 80% upper bound (z0.80 = 0.842 exact), n = 1440 EXACTLY
#     (§R-REV3.1 item 4), the dev-96 cluster-difference distribution for
#     the coordinator's sign-symmetry check (§R-REV4.1a — the driver
#     reports, the coordinator decides + commits inference.{method,pass}),
#     and the REPLACE run/defer gate (dev-96 delta_R -> n_NI <= 1440,
#     §R-REV4.3/ASM-2124)
#   * GATES (fail-closed pre-run returns):
#       power     : >= 65 clusters EACH with m >= 8, n == 1440 (ASM-2271)
#       placebo   : d0-family vs b0 one-sided cluster sign-flip p >= 0.05
#                   on dev-96 (ANY-magnitude alarm, ASM-2273)
#       semantics : colibri knob-semantics re-verification attested
#                   (ASM-1971; §R-REV4.2 step 3)
#       afford    : projected total <= $149 (glm52-f1k-cost-reduction.md)
#
# The frozen (L,g) the MAIN RUN uses is addendum-5; the coordinator commits
# addenda (5)/(7)/(6) per the §R-REV4.2 ordering BEFORE any test prefill.
# =============================================================================
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
  echo "usage: pilot.sh --config <run-config.json> --outdir <dir>" >&2
  echo "       pilot.sh --mock   (stub-engine validation, \$0)" >&2
  exit 2
}

CONFIG="" OUTDIR="" MOCK=0
while [ $# -gt 0 ]; do
  case "$1" in
    --config) CONFIG="$2"; shift 2 ;;
    --outdir) OUTDIR="$2"; shift 2 ;;
    --mock)   MOCK=1; shift ;;
    *) usage ;;
  esac
done

if [ "$MOCK" -eq 1 ]; then
  exec python3 "$HERE/f1k_driver.py" --mock
fi

[ -n "$CONFIG" ] && [ -n "$OUTDIR" ] || usage
[ -f "$CONFIG" ] || { echo "ERR_F1K_PILOT: config not found: $CONFIG" >&2; exit 2; }

# preflight: the pilot is the FIRST spend after construction; the (A)/(B0)
# freeze artifacts must already be committed (§R-REV3.3/§R-REV4.2). The
# driver re-checks these fail-closed from the config's freeze block at
# sidecar time; here we refuse to even start without the pins on disk.
python3 - "$CONFIG" <<'PYEOF'
import json, os, sys
cfg = json.load(open(sys.argv[1]))
missing = []
for k in ("engine", "eval_manifest", "carriers", "pilot"):
    if k not in cfg:
        missing.append(k)
argv = (cfg.get("engine") or {}).get("argv") or []
if not argv or not os.path.exists(argv[0]):
    missing.append("engine.argv[0] (colibri binary)")
if not os.path.exists(cfg.get("eval_manifest", "")):
    missing.append("eval_manifest (f1k-eval-v1 pin)")
flags = (cfg.get("freeze") or {}).get("manifest_flags") or {}
if not flags.get("pre_spend_committed") or not flags.get("b0_addendum_committed"):
    missing.append("freeze.manifest_flags.pre_spend_committed/"
                   "b0_addendum_committed ((A)+(B0) must precede pilot "
                   "spend, design §R-REV3.3/§R-REV4.2)")
if missing:
    print("ERR_F1K_PILOT: preflight failed, missing/invalid: %s" % missing,
          file=sys.stderr)
    sys.exit(2)
print("preflight OK")
PYEOF

exec python3 "$HERE/f1k_driver.py" --config "$CONFIG" --phase pilot --outdir "$OUTDIR"
