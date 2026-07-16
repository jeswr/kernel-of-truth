#!/usr/bin/env bash
# =============================================================================
# watchdog.sh — OPUS control-box durable teardown watchdog (runs on the EC2
# control box, detached via nohup; survives the launching session). It is the
# AUTHORITATIVE anti-orphan backstop: the VM was provisioned with --scopes
# storage-rw, so its metadata token CANNOT self-delete via gcloud; this
# control-box process (authed jwrightwho@gmail.com, full compute) does the real
# DELETE. Tears down the VM + local SSD on ANY of:
#   (1) heartbeat stage starts with "FAILED"  (worker/setup failed)
#   (2) VM status TERMINATED/STOPPING/STOPPED/SUSPENDED (guest self-halt or spot preemption)
#   (3) absolute deadline exceeded (hang cap)
# It does NOT delete on "DONE...READY-FOR-ONBOX-REVIEW": the VM is intentionally
# HELD so the coordinator can finalize dump preconditions (a)+(c) + the real
# affordability micro-benchmark ON-BOX (those cannot be validated blind). The
# deadline still caps that review window so nothing bills idle indefinitely.
# =============================================================================
set -uo pipefail
source ~/.config/kot/gcp.env
VM="kot-f1k-run"
ZONE="us-central1-a"
BUCKET="gs://kot-f1k-estate-85e2ca29"
DEADLINE_H="${1:-14}"
POLL_S="${2:-300}"
WLOG="${3:-/tmp/f1k-watchdog.log}"
RLOG_PY="/tmp/claude-1000/-home-ec2-user-css/85798a0b-4e71-4020-b0b9-ac1fed9631d0/scratchpad/rlog.py"
RUN_LOG="$(cat /tmp/claude-1000/-home-ec2-user-css/85798a0b-4e71-4020-b0b9-ac1fed9631d0/scratchpad/rlpath.txt 2>/dev/null)"
DEADLINE=$(( $(date +%s) + DEADLINE_H*3600 ))
log() { echo "[$(date -u +%FT%TZ)] $*" >> "$WLOG"; }
rlog() { [ -n "$RUN_LOG" ] && python3 "$RLOG_PY" "/home/ec2-user/css/kernel/kernel-of-truth/$RUN_LOG" "$1" >/dev/null 2>&1 || true; }

teardown() {
  local why="$1"
  log "TEARDOWN triggered: $why -> gcloud compute instances delete $VM"
  gcloud compute instances delete "$VM" --zone "$ZONE" --project "$KOT_GCP_PROJECT" --quiet >> "$WLOG" 2>&1
  local rc=$?
  log "delete exit=$rc"
  rlog "{\"event\":\"watchdog-teardown\",\"result\":\"VM-DELETED\",\"detail\":\"control-box watchdog deleted $VM ($ZONE) + local SSD; reason: $why; gcloud delete exit=$rc\"}"
  exit 0
}

log "watchdog START vm=$VM zone=$ZONE deadline=${DEADLINE_H}h poll=${POLL_S}s"
while true; do
  ST="$(gcloud compute instances describe "$VM" --zone "$ZONE" --project "$KOT_GCP_PROJECT" --format='value(status)' 2>/dev/null)"
  if [ -z "$ST" ]; then log "VM not found (already deleted). exiting."; rlog "{\"event\":\"watchdog-exit\",\"result\":\"VM-GONE\",\"detail\":\"describe empty; VM already deleted; watchdog exiting clean\"}"; exit 0; fi
  HB="$(gsutil -q cat "$BUCKET/f1k/bringup/heartbeat.json" 2>/dev/null | python3 -c 'import sys,json;
try: print(json.load(sys.stdin).get("stage",""))
except: print("")' 2>/dev/null)"
  NOW=$(date +%s)
  log "status=$ST heartbeat=\"$HB\" t_remaining=$(( (DEADLINE-NOW)/60 ))min"
  case "$HB" in
    FAILED*) teardown "heartbeat FAILED ($HB)";;
  esac
  case "$ST" in
    TERMINATED|STOPPING|STOPPED|SUSPENDED|SUSPENDING) teardown "VM status $ST (guest self-halt or spot preemption)";;
  esac
  if [ "$NOW" -ge "$DEADLINE" ]; then teardown "absolute deadline ${DEADLINE_H}h exceeded (hang cap)"; fi
  sleep "$POLL_S"
done
