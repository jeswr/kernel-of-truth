#!/usr/bin/env bash
# =============================================================================
# f1k_worker.sh — runs ON the GCP Spot VM. Autonomous, resume-safe, fail-closed.
#
# SCOPE (this script deliberately STOPS at the affordability gate — it NEVER
# spends the construction/campaign dollars autonomously; those are separately
# gated on the measured bring-up + affordability result, per the frozen
# addendum-(7)/(6)/(5) ordering + the Fable addendum-6 inference-method
# handoff). It orchestrates ONLY already-authored, gate-0-reviewed artifacts:
#   1. STAGE   the GLM-5.2 int4 estate: restore from the same-region GCS
#      mirror if present (cheap, preemption-safe), else HF snapshot_download to
#      local NVMe then mirror to GCS. Pin the weight content hash.
#   2. BUILD   the SCORING engine (colibri + KaE patch ONLY, phase separation)
#      via bringup_gcp.sh, and the CONSTRUCTION engine (colibri + KaE + the
#      kot-f1k-dump patch) via the dump-patch real-checks.sh battery.
#   3. BRING-UP GATE (KaE): bringup_gcp.sh — 44/44 test_kae + clone-aware
#      inert-by-default proof.
#   4. DUMP BRING-UP GATE — the 3 PATCH-NOTES preconditions on the REAL binary:
#        (b) unarmed byte-identity vs the KaE-only engine + test_kae 44/44 +
#            test_kae_dump 43/43 + objdump per-function inertness on PRODUCTION
#            flags  [dump-patch/real-checks.sh, run here against the pinned
#            KaE tree built above];
#        (a) tiny real dump completes + kot-f1k-tok/1 token-id consistency;
#        (c) independent MoE-input sum cross-check on MIXED positions — the
#            hard content gate; the worker prepares the dumped sums; the RUNNER
#            finalizes the independent comparison ON-BOX (its correctness can
#            not be validated blind, so it is a runner-confirmed PASS, not an
#            autonomous one — see README "Dump bring-up gate").
#   5. AFFORDABILITY MICRO-BENCHMARK — time real scoring prefills -> blended
#      s/prefill; combined with the RECORDED spot rate -> the frozen-window
#      projection gate (f1k_gcp.py affordability). Writes addendum-7 inputs.
#      Then STOP + heartbeat DONE.
#
# Heartbeat + all artifacts are mirrored to GCS ($BUCKET/f1k/bringup) so a spot
# preemption just re-runs this script (idempotent; staging restores from GCS).
# =============================================================================
set -euo pipefail

BUCKET="${KOT_F1K_BUCKET:?set KOT_F1K_BUCKET=gs://... (same-region estate mirror + heartbeat)}"
COLIBRI_GIT_URL="${COLIBRI_GIT_URL:?coordinator-supplied colibri clone URL}"
SPOT_RATE="${KOT_F1K_SPOT_RATE:?record the ACTUAL assigned spot $/h (load-bearing for the affordability gate)}"
ESTATE_REPO="mateogrgic/GLM-5.2-colibri-int4-with-int8-mtp"
HOME_DIR="${HOME:-/home/ubuntu}"
SSD="/mnt/nvme"                 # the striped local NVMe mount (see f1k_gcp provision docs)
ESTATE_DIR="$SSD/glm52_i4"
GATE="$HOME_DIR/f1k-gate"       # bring-up outputs
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

mkdir -p "$GATE"
die() { echo "ERR_F1K_WORKER: $*" >&2; hb "FAILED: $*"; exit 1; }
step() { echo; echo "########## $* ##########"; }
hb() { # heartbeat to GCS
  echo "{\"ts\":\"$(date -u +%FT%TZ)\",\"stage\":\"$1\"}" > "$GATE/heartbeat.json"
  gsutil -q cp "$GATE/heartbeat.json" "$BUCKET/f1k/bringup/heartbeat.json" 2>/dev/null || true
}

# --- DIAGNOSTIC PRESERVATION (runner-7) ------------------------------------
# Under `set -euo pipefail`, a build failure inside step 2+3 (the tee'd
# bringup_gcp.sh pipe) trips pipefail and exits BEFORE the `|| die` and BEFORE
# the DONE-step mirror (line ~167) ever run — so on the failing path the on-VM
# build logs ($GATE/kae-bringup.log, dump-realchecks.log, etc.) were NEVER
# mirrored to GCS, and the watchdog then deleted the VM, LOSING the diagnostic.
# This EXIT trap fires on EVERY exit path (normal, `set -e`/pipefail, signal,
# die()) and best-effort mirrors the WHOLE $GATE dir to $BUCKET/f1k/bringup/ so
# any failure is diagnosable off-box. Best-effort only: it never changes the
# exit code (re-exits with the original rc) and never hangs teardown.
_mirror_gate_on_exit() {
  local rc=$?
  trap - EXIT   # disarm so this runs at most once
  if [ -d "$GATE" ]; then
    echo "{\"ts\":\"$(date -u +%FT%TZ)\",\"stage\":\"EXIT rc=$rc (gate mirrored)\",\"rc\":$rc}" \
      > "$GATE/exit-status.json" 2>/dev/null || true
    gsutil -q -m cp -r "$GATE" "$BUCKET/f1k/bringup/" 2>/dev/null || true
    gsutil -q cp "$GATE/exit-status.json" "$BUCKET/f1k/bringup/exit-status.json" 2>/dev/null || true
  fi
  exit "$rc"
}
trap _mirror_gate_on_exit EXIT
# ---------------------------------------------------------------------------

step "0/5 preflight: non-AWS + tools + NVMe"
# non-AWS gate (this box must be the GCP VM, never AWS)
if curl -s --max-time 1 http://169.254.169.254/latest/meta-data/instance-id >/dev/null 2>&1 \
   && ! curl -s --max-time 1 -H 'Metadata-Flavor: Google' \
        http://metadata.google.internal/computeMetadata/v1/instance/zone >/dev/null 2>&1; then
  die "worker looks like AWS — refuse (frozen target is the GCP Spot VM)"
fi
for t in git gcc make objdump python3 sha256sum gsutil curl; do
  command -v "$t" >/dev/null 2>&1 || { sudo apt-get update -qq && sudo apt-get install -y -qq git build-essential binutils python3 curl; break; }
done
[ -d "$SSD" ] || die "local NVMe mount $SSD missing (provision must RAID+mount the 3 local SSD)"
hb "preflight-ok"

step "1/5 stage estate (GCS mirror -> else HF -> local NVMe, then mirror to GCS)"
mkdir -p "$ESTATE_DIR"
if gsutil -q ls "$BUCKET/f1k/estate/COMPLETE" 2>/dev/null; then
  echo "estate mirror present in GCS — restoring to $ESTATE_DIR"
  gsutil -q -m rsync -r "$BUCKET/f1k/estate" "$ESTATE_DIR"
else
  echo "no GCS mirror — HF snapshot_download $ESTATE_REPO"
  pip3 -q install "huggingface_hub[hf_transfer]>=0.24" hf_transfer 2>/dev/null || true
  HF_HUB_ENABLE_HF_TRANSFER=1 python3 - <<PY
from huggingface_hub import snapshot_download
snapshot_download(repo_id="$ESTATE_REPO", local_dir="$ESTATE_DIR",
                  local_dir_use_symlinks=False, max_workers=8)
print("staged")
PY
  # mirror to GCS so a preempted VM restores instead of re-downloading
  gsutil -q -m rsync -r "$ESTATE_DIR" "$BUCKET/f1k/estate"
  echo "ok" | gsutil -q cp - "$BUCKET/f1k/estate/COMPLETE"
fi
# weight content hash (ASM-1971 PINNED-AT-INPUTS): sorted rel-path + size digest
python3 - "$ESTATE_DIR" > "$GATE/glm52-weights-hash.json" <<'PY'
import sys, hashlib, os
root = sys.argv[1]; lines = []; total = 0
for dp, _, fs in os.walk(root):
    for fn in fs:
        p = os.path.join(dp, fn); sz = os.path.getsize(p); total += sz
        lines.append("%s %d" % (os.path.relpath(p, root), sz))
lines.sort()
import json
print(json.dumps({"glm52_weights_manifest_sha256":
                  hashlib.sha256("\n".join(lines).encode()).hexdigest(),
                  "n_files": len(lines), "total_gb": round(total/1e9, 2)}))
PY
cat "$GATE/glm52-weights-hash.json"
gsutil -q cp "$GATE/glm52-weights-hash.json" "$BUCKET/f1k/bringup/" || true
hb "staged"

step "2+3/5 build SCORING engine (KaE-only) + KaE bring-up gate"
KAE_PATCH_DIR="$HERE/kae-patch-draft" COLIBRI_WORK="$HOME_DIR/colibri-score" \
  COLIBRI_GIT_URL="$COLIBRI_GIT_URL" bash "$HERE/bringup_gcp.sh" 2>&1 | tee "$GATE/kae-bringup.log"
grep -q "BRING-UP OK (KaE)" "$GATE/kae-bringup.log" || die "KaE bring-up gate FAILED"
hb "kae-bringup-ok"

step "4/5 build CONSTRUCTION engine (KaE + dump patch) + DUMP bring-up gate (b)"
# real-checks.sh applies KaE THEN the dump patch on a pristine tree, builds,
# test_kae 44/44 + test_kae_dump 43/43, objdump per-function inertness.
( cd "$HERE/dump-patch" && COLIBRI_GIT_URL="$COLIBRI_GIT_URL" \
    COLIBRI_WORK="$HOME_DIR/colibri-construct" bash real-checks.sh ) 2>&1 \
  | tee "$GATE/dump-realchecks.log"
grep -qiE "REAL-SOURCE CHECKS OK|CHECKS OK" "$GATE/dump-realchecks.log" \
  || die "dump bring-up precondition (b) FAILED (real-checks.sh)"
hb "dump-precond-b-ok"

step "4/5 DUMP bring-up gate (a): tiny real dump + token-id consistency"
# A few manifest lines at a small layer subset; kot-f1k-tok/1 ids must equal the
# ids the real engine prefills.  build_carriers manifest is (A)-time; a tiny
# construct DUMP is the smallest real exercise of the dump path.
: > "$GATE/tiny-dump.status"
python3 - <<PY 2>&1 | tee "$GATE/tiny-dump.log" || true
print("SCAFFOLD: the runner runs a tiny real KAE_DUMP over a few manifest")
print("lines (small KAE_DUMP_LAYERS) with KAE_SEED=20260716 and asserts the")
print("engine [KAE-DUMP] armed echo seed==20260716, then compares tok_glm52.py")
print("ids for the same texts to the ids the engine actually prefilled.")
print("This is finalized ON-BOX with the real construction binary + weights.")
PY
echo "RUNNER-CONFIRM-REQUIRED" > "$GATE/tiny-dump.status"
hb "dump-precond-a-scaffolded"

step "4/5 DUMP bring-up gate (c): independent MoE-input sum cross-check (RUNNER-CONFIRMED)"
echo "RUNNER-CONFIRM-REQUIRED" > "$GATE/moe-sum-crosscheck.status"
echo "SCAFFOLD: capture the engine's dumped moe()-input sum over >=1 MIXED" \
     "gated/ungated line, and an INDEPENDENT sum (separate path, not kae_dump.h);" \
     "assert cell-for-cell equality after the f32 cast. Correctness of the" \
     "independent path cannot be validated blind -> runner-confirmed PASS." \
     > "$GATE/moe-sum-crosscheck.log"
hb "dump-precond-c-scaffolded"

step "5/5 affordability micro-benchmark (blended s/prefill) -> frozen-window gate"
# Time a small batch of REAL scoring prefills (KAE_SCORE path) on representative
# items; blended s/prefill feeds the frozen-window projection.  SCAFFOLD: the
# runner points this at the scoring binary + a representative eval sample.
echo "RUNNER-RUN-REQUIRED" > "$GATE/affordability.status"
cat > "$GATE/affordability-README.txt" <<EOF
Measure blended s/prefill: run N (>=20) real KAE_SCORE prefills spanning the
short (b0) and long (d3-text prepend) arms on the scoring binary, take the mean
wall-seconds/prefill.  Then:
  python3 poc/gcp/f1k_gcp.py affordability --rate $SPOT_RATE --s-per-prefill <MEAN>
which projects the 19964-prefill ledger and FAILS CLOSED if the projection
lands outside instance_hours [260.6,900] h or usd_total [\$73,\$155] (the FLOOR
binds below \$0.28/h).  A GO here (and ONLY a GO) licenses construction spend.
EOF
cat "$GATE/affordability-README.txt"
hb "affordability-pending-runner"

step "DONE (bring-up scaffolded; STOP before construction spend)"
echo "Bring-up artifacts in $GATE/ (mirrored to $BUCKET/f1k/bringup/)."
echo "NEXT (gated): finalize dump preconditions (a)+(c) + the affordability"
echo "micro-benchmark on-box; a GO affordability verdict licenses construction."
gsutil -q -m cp -r "$GATE" "$BUCKET/f1k/bringup/" || true
hb "DONE-bringup-scaffold"
