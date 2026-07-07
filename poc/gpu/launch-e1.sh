#!/usr/bin/env bash
# Launch the E1 GPU grid (docs/poc-design.md Phase E, E1: 5 arms x 5 seeds +
# LR sweeps) on a g5.xlarge (A10G) in eu-west-2: SPOT by default, on-demand
# via --on-demand or --fallback. Patterned on launch-e2.sh.
#
#   ./launch-e1.sh --dry-run                 # validate everything, launch nothing
#   ./launch-e1.sh                           # spot launch, push results branch
#   ./launch-e1.sh --on-demand               # skip spot entirely
#   ./launch-e1.sh --fallback                # spot first, on-demand if spot fails
#   ./launch-e1.sh --no-push                 # run without a deploy key
#
# Prereqs: aws cli v2 with EC2 permissions; pushing REUSES the existing
# kot-e2 deploy key (poc/gpu/setup-deploy-key.sh was run once for the E2
# campaign — do NOT mint or register a new key; override the path with
# KOT_E1_DEPLOY_KEY if the campaign rotates keys). The instance clones the
# PUBLIC repo over https, fetches TinyStories-train.txt, runs
# poc/e1/run_all.sh full (data build -> LR sweep -> 25-run grid -> evals ->
# pre-registered stats/verdict), commits poc/e1/results/ to branch
# results/e1-<UTC stamp>, pushes over ssh, and powers itself off
# (shutdown-behavior=terminate; 36 h failsafe). Cost: poc/gpu/README.md E1
# section (~$9-12 spot, ~$21 on-demand, $36 failsafe cap).
set -euo pipefail

REGION="${KOT_E1_REGION:-eu-west-2}"
REPO="${KOT_E1_REPO:-jeswr/kernel-of-truth}"
BRANCH="${KOT_E1_BRANCH:-main}"
KEY_FILE="${KOT_E1_DEPLOY_KEY:-$HOME/.ssh/kot-e2-deploy}"
INSTANCE_TYPE="g5.xlarge"
VOLUME_GB=125   # DLAMI root ~100 GB + corpus 2 GB + shards ~4.5 GB + ckpts ~7 GB

DRY_RUN=no; MARKET=spot; FALLBACK=no; PUSH=yes; SSH_KEY_NAME=""; AZ=""
while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRY_RUN=yes ;;
    --on-demand) MARKET=on-demand ;;
    --fallback) FALLBACK=yes ;;
    --no-push) PUSH=no ;;
    --key-name) SSH_KEY_NAME="$2"; shift ;;
    --az) AZ="$2"; shift ;;
    --branch) BRANCH="$2"; shift ;;
    *) echo "unknown flag: $1" >&2; exit 2 ;;
  esac
  shift
done

HERE="$(cd "$(dirname "$0")" && pwd)"
aws() { command aws --region "$REGION" "$@"; }

# ---- 1. current PyTorch DLAMI (newest first; queried, never hardcoded) ----
AMI_JSON=$(aws ec2 describe-images \
  --owners amazon \
  --filters "Name=name,Values=Deep Learning OSS Nvidia Driver AMI GPU PyTorch*" "Name=state,Values=available" \
  --query 'reverse(sort_by(Images,&CreationDate))[0].{Id:ImageId,Name:Name}' --output json)
AMI_ID=$(echo "$AMI_JSON" | sed -n 's/.*"Id": "\(ami-[a-z0-9]*\)".*/\1/p')
[ -n "$AMI_ID" ] || { echo "no PyTorch DLAMI found in $REGION" >&2; exit 1; }
echo "AMI: $AMI_JSON"

# ---- 2. subnet: a default-for-az subnet (optionally pinned via --az) ----
SUBNET_FILTERS=(Name=default-for-az,Values=true)
[ -n "$AZ" ] && SUBNET_FILTERS+=("Name=availability-zone,Values=$AZ")
SUBNET_ID=$(aws ec2 describe-subnets --filters "${SUBNET_FILTERS[@]}" \
  --query 'Subnets[0].SubnetId' --output text)
[ "$SUBNET_ID" != "None" ] || { echo "no default-for-az subnet in $REGION $AZ" >&2; exit 1; }
echo "subnet: $SUBNET_ID"

# ---- 3. user-data (deploy key embedded at launch time; never committed) ----
STAMP=$(date -u +%Y%m%d-%H%M)
UD_FILE=$(mktemp)
trap 'rm -f "$UD_FILE"' EXIT
KEY_B64=""
if [ "$PUSH" = yes ]; then
  if [ ! -f "$KEY_FILE" ]; then
    echo "deploy key $KEY_FILE missing — the E2 campaign key is reused; run poc/gpu/setup-deploy-key.sh (once, coordinator) or pass --no-push" >&2
    exit 1
  fi
  KEY_B64=$(base64 -w0 < "$KEY_FILE")
fi
sed -e "s|__REPO__|$REPO|g" \
    -e "s|__BRANCH__|$BRANCH|g" \
    -e "s|__RESULTS_BRANCH__|results/e1-$STAMP|g" \
    -e "s|__PUSH__|$PUSH|g" \
    -e "s|__DEPLOY_KEY_B64__|$KEY_B64|g" \
    "$HERE/user-data-e1.sh.tpl" > "$UD_FILE"

# ---- 4. run-instances ----
run_instances() { # $1 = spot|on-demand, $2 = yes|no (dry run)
  local args=(
    ec2 run-instances
    --image-id "$AMI_ID"
    --instance-type "$INSTANCE_TYPE"
    --subnet-id "$SUBNET_ID"
    --count 1
    --instance-initiated-shutdown-behavior terminate
    --block-device-mappings "[{\"DeviceName\":\"/dev/sda1\",\"Ebs\":{\"VolumeSize\":$VOLUME_GB,\"VolumeType\":\"gp3\",\"DeleteOnTermination\":true}}]"
    --tag-specifications
      'ResourceType=instance,Tags=[{Key=Project,Value=kernel-of-truth},{Key=Name,Value=kot-e1}]'
      'ResourceType=volume,Tags=[{Key=Project,Value=kernel-of-truth},{Key=Name,Value=kot-e1}]'
    --user-data "file://$UD_FILE"
  )
  [ -n "$SSH_KEY_NAME" ] && args+=(--key-name "$SSH_KEY_NAME")
  if [ "$1" = spot ]; then
    args+=(--instance-market-options 'MarketType=spot,SpotOptions={SpotInstanceType=one-time,InstanceInterruptionBehavior=terminate}')
  fi
  [ "$2" = yes ] && args+=(--dry-run)
  aws "${args[@]}"
}

if [ "$DRY_RUN" = yes ]; then
  echo "--- DRY RUN ($MARKET) ---"
  set +e
  OUT=$(run_instances "$MARKET" yes 2>&1)
  RC=$?
  set -e
  echo "$OUT"
  if echo "$OUT" | grep -q DryRunOperation; then
    echo "DRY RUN OK: request would have succeeded"
    exit 0
  fi
  echo "DRY RUN FAILED (rc=$RC)"
  exit 1
fi

set +e
OUT=$(run_instances "$MARKET" no 2>&1)
RC=$?
set -e
if [ $RC -ne 0 ] && [ "$MARKET" = spot ] && [ "$FALLBACK" = yes ]; then
  echo "spot launch failed, falling back to on-demand:" >&2
  echo "$OUT" >&2
  OUT=$(run_instances on-demand no)
  RC=$?
fi
[ $RC -eq 0 ] || { echo "$OUT" >&2; exit $RC; }
echo "$OUT"
IID=$(echo "$OUT" | sed -n 's/.*"InstanceId": "\(i-[a-z0-9]*\)".*/\1/p' | head -1)
echo
echo "launched $IID (results branch: results/e1-$STAMP)"
echo "watch:      aws ec2 describe-instances --region $REGION --instance-ids $IID --query 'Reservations[].Instances[].State.Name'"
echo "terminate:  aws ec2 terminate-instances --region $REGION --instance-ids $IID"
echo "The instance powers itself off when done (max 36 h failsafe)."
