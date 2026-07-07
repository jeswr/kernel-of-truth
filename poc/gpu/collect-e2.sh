#!/usr/bin/env bash
# Collect E2 pull-path results (Option B; counterpart of launch-e2-pull.sh).
#
#   ./collect-e2.sh <instance-id>                # poll, scp results, terminate
#   ./collect-e2.sh <instance-id> --cleanup      # ...then delete SG + key pair
#   ./collect-e2.sh --cleanup-only               # just delete SG + key pair
#   flags: --timeout-mins N (default 240, matching the box's 4 h failsafe)
#
# Success path: waits for /opt/e2/results/DONE on the instance, scps
# /opt/e2/results/ into poc/e2/results-incoming/<UTC stamp>/, verifies the
# runner's verdict JSON parses (echoes its OUTCOME line), terminates the box.
# Failure path: if DONE never appears, pulls /var/log/cloud-init-output.log +
# /var/log/kot-e2-userdata.log over ssh (or `aws ec2 get-console-output` if
# ssh is unreachable) into the same incoming dir BEFORE terminating, so a
# failed run always leaves a diagnosable trace.
# This script does NOT git-commit anything — the coordinator reviews
# results-incoming/ and commits deliberately.
set -euo pipefail

REGION="${KOT_E2_REGION:-eu-west-2}"
KEY_NAME="kernel-of-truth-e2"
KEY_FILE="${KOT_E2_EPHEMERAL_KEY:-$HOME/.ssh/kot-e2-ephemeral}"
SG_NAME="kot-e2-sg"
POLL_SECS=60

IID=""; CLEANUP=no; CLEANUP_ONLY=no; TIMEOUT_MINS=240
while [ $# -gt 0 ]; do
  case "$1" in
    --cleanup) CLEANUP=yes ;;
    --cleanup-only) CLEANUP_ONLY=yes ;;
    --timeout-mins) TIMEOUT_MINS="$2"; shift ;;
    i-*) IID="$1" ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
  shift
done

HERE="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$HERE/../.." && pwd)"
aws() { command aws --region "$REGION" "$@"; }

cleanup_aws() {
  echo "--- cleanup: EC2 key pair + security group ---"
  aws ec2 delete-key-pair --key-name "$KEY_NAME" 2>/dev/null \
    && echo "deleted key pair $KEY_NAME" \
    || echo "key pair $KEY_NAME absent or not deletable (fine)"
  local sg_id
  sg_id=$(aws ec2 describe-security-groups \
    --filters "Name=group-name,Values=$SG_NAME" \
    --query 'SecurityGroups[0].GroupId' --output text 2>/dev/null || echo None)
  if [ "$sg_id" != None ] && [ -n "$sg_id" ]; then
    # The SG stays attached until the instance finishes shutting down; retry.
    local i
    for i in $(seq 1 20); do
      if aws ec2 delete-security-group --group-id "$sg_id" 2>/dev/null; then
        echo "deleted security group $sg_id"
        return 0
      fi
      [ "$i" = 20 ] || { echo "SG $sg_id still in use, retrying (${i}/20)..."; sleep 15; }
    done
    echo "WARNING: could not delete SG $sg_id (still in use?) — retry later with --cleanup-only"
  else
    echo "security group $SG_NAME absent (fine)"
  fi
}

if [ "$CLEANUP_ONLY" = yes ]; then
  cleanup_aws
  exit 0
fi
[ -n "$IID" ] || { echo "usage: collect-e2.sh <instance-id> [--cleanup] [--timeout-mins N] | --cleanup-only" >&2; exit 2; }
[ -f "$KEY_FILE" ] || { echo "ephemeral key $KEY_FILE missing — launch-e2-pull.sh creates it" >&2; exit 1; }

# Per-run known_hosts: accept-new pins the host key for THIS session (blocks a
# mid-session swap) without polluting ~/.ssh/known_hosts — VPC private IPs get
# reused across ephemeral instances and a stale pin would hard-fail the ssh.
KNOWN_HOSTS=$(mktemp)
trap 'rm -f "$KNOWN_HOSTS"' EXIT
SSH_OPTS=(-i "$KEY_FILE" -o StrictHostKeyChecking=accept-new \
  -o "UserKnownHostsFile=$KNOWN_HOSTS" -o ConnectTimeout=10 -o BatchMode=yes -o IdentitiesOnly=yes)
STAMP=$(date -u +%Y%m%d-%H%M%S)
INCOMING="$REPO_ROOT/poc/e2/results-incoming/$STAMP"

instance_field() { # $1 = JMESPath under Instances[0]
  aws ec2 describe-instances --instance-ids "$IID" \
    --query "Reservations[0].Instances[0].$1" --output text 2>/dev/null || echo None
}

terminate_box() {
  echo "terminating $IID"
  aws ec2 terminate-instances --instance-ids "$IID" \
    --query 'TerminatingInstances[].{Id:InstanceId,State:CurrentState.Name}' --output table || true
}

# ---- 1. wait until running + private IP (SG only admits our private /32) ----
echo "waiting for $IID to run (region $REGION)..."
IP=""
DEADLINE=$(( $(date +%s) + TIMEOUT_MINS * 60 ))
while :; do
  STATE=$(instance_field 'State.Name')
  case "$STATE" in
    running)
      IP=$(instance_field PrivateIpAddress)
      [ "$IP" != None ] && break
      ;;
    pending) : ;;
    *) echo "instance is '$STATE' before results were collected — going to failure path" ;;
  esac
  if [ "$STATE" != pending ] && [ "$STATE" != running ]; then break; fi
  [ "$(date +%s)" -lt "$DEADLINE" ] || { echo "timed out waiting for running state"; break; }
  sleep 15
done

SSH_USER=""
detect_user() { # DLAMI is Ubuntu- or AL2023-based depending on the AMI picked
  local u
  for u in ubuntu ec2-user; do
    if ssh "${SSH_OPTS[@]}" "$u@$IP" true 2>/dev/null; then SSH_USER=$u; return 0; fi
  done
  return 1
}

# ---- 2. poll for /opt/e2/results/DONE ----
DONE=no
if [ -n "$IP" ] && [ "$IP" != None ]; then
  echo "instance running at private IP $IP; polling for DONE every ${POLL_SECS}s (timeout ${TIMEOUT_MINS}m)"
  while [ "$(date +%s)" -lt "$DEADLINE" ]; do
    STATE=$(instance_field 'State.Name')
    if [ "$STATE" != running ]; then
      echo "instance left running state ($STATE) before DONE"; break
    fi
    if [ -z "$SSH_USER" ]; then detect_user || { sleep "$POLL_SECS"; continue; }; echo "ssh user: $SSH_USER"; fi
    if ssh "${SSH_OPTS[@]}" "$SSH_USER@$IP" 'test -f /opt/e2/results/DONE' 2>/dev/null; then
      DONE=yes; break
    fi
    sleep "$POLL_SECS"
  done
fi

mkdir -p "$INCOMING"

# ---- 3a. success: scp results, verify verdict JSON ----
RC=0
if [ "$DONE" = yes ]; then
  echo "DONE marker present — collecting into $INCOMING"
  scp -r "${SSH_OPTS[@]}" "$SSH_USER@$IP:/opt/e2/results/." "$INCOMING/"
  echo "collected: $(ls "$INCOMING" | tr '\n' ' ')"
  VJSON=$(ls "$INCOMING"/results-e2*.json 2>/dev/null | head -1 || true)
  if [ -n "$VJSON" ] && python3 - "$VJSON" <<'EOF'
import json, sys
j = json.load(open(sys.argv[1]))
print(f"verdict JSON OK: {sys.argv[1]}")
print(f"OUTCOME: {j['outcome']}  (mock={j.get('mock')})")
EOF
  then :; else
    echo "WARNING: no parseable results-e2*.json in $INCOMING — inspect manually" >&2
    RC=1
  fi
else
  # ---- 3b. failure: leave a diagnosable trace BEFORE terminating ----
  echo "no DONE marker — collecting diagnostics into $INCOMING" >&2
  GOT_LOGS=no
  if [ -n "$IP" ] && [ "$IP" != None ] && { [ -n "$SSH_USER" ] || detect_user; }; then
    for f in /var/log/cloud-init-output.log /var/log/kot-e2-userdata.log /var/log/kot-e2-run.log; do
      if ssh "${SSH_OPTS[@]}" "$SSH_USER@$IP" "sudo cat $f 2>/dev/null || cat $f" \
          > "$INCOMING/$(basename "$f")" 2>/dev/null \
          && [ -s "$INCOMING/$(basename "$f")" ]; then
        GOT_LOGS=yes
      fi
    done
    # partial results are better than none
    scp -r "${SSH_OPTS[@]}" "$SSH_USER@$IP:/opt/e2/results/." "$INCOMING/" 2>/dev/null || true
  fi
  if [ "$GOT_LOGS" = no ]; then
    echo "ssh unreachable — falling back to get-console-output" >&2
    aws ec2 get-console-output --instance-id "$IID" --latest --output text \
      > "$INCOMING/console-output.txt" 2>/dev/null \
      || aws ec2 get-console-output --instance-id "$IID" --output text \
      > "$INCOMING/console-output.txt" 2>/dev/null \
      || echo "get-console-output also failed" >&2
  fi
  echo "diagnostics saved: $(ls "$INCOMING" 2>/dev/null | tr '\n' ' ')"
  RC=1
fi

# ---- 4. terminate; optional AWS cleanup ----
terminate_box
[ "$CLEANUP" = yes ] && cleanup_aws

echo
echo "results dir: $INCOMING"
echo "NOT committed — review and commit deliberately (coordinator step)."
exit $RC
