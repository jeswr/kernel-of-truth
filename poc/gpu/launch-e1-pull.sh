#!/usr/bin/env bash
# Launch the E1 GPU grid — PULL-BASED results path (Option B; bead
# kernel-of-truth-cs2). Clone of the validated launch-e2-pull.sh flow: no
# standing credentials anywhere — not in the repo, not in user-data, not on
# the box. This RETIRES the deploy-key Option A path of launch-e1.sh for E1
# (kept only for unattended runs where no coordinator can collect).
#
#   ./launch-e1-pull.sh --dry-run     # keypair+SG for real, launch DryRun only
#   ./launch-e1-pull.sh               # spot launch; then collect-e1.sh <iid>
#   ./launch-e1-pull.sh --on-demand   # skip spot entirely
#   ./launch-e1-pull.sh --fallback    # spot first, on-demand if spot fails
#   ./launch-e1-pull.sh --with-e4     # chain the E4 runner after the E1 grid
#                                     # (same boot; failsafe 36 h -> 42 h)
#
# How results come back: the instance writes /opt/e1/results/ + a DONE marker
# and waits; poc/gpu/collect-e1.sh <instance-id> polls, scps the results into
# poc/e1/results-incoming/<stamp>/, and terminates the box. Everything here
# stays inside the approved IAM policy: RunInstances (g5, tagged at launch),
# key pairs named kernel-of-truth-*, security groups tagged
# Project=kernel-of-truth, Describe*, Terminate on Project-tagged instances.
set -euo pipefail

REGION="${KOT_E1_REGION:-eu-west-2}"
REPO="${KOT_E1_REPO:-jeswr/kernel-of-truth}"
BRANCH="${KOT_E1_BRANCH:-main}"
KEY_NAME="kernel-of-truth-e1"                       # policy: kernel-of-truth-*
KEY_FILE="${KOT_E1_EPHEMERAL_KEY:-$HOME/.ssh/kot-e1-ephemeral}"
SG_NAME="kot-e1-sg"
INSTANCE_TYPE="g5.xlarge"
VOLUME_GB=125   # DLAMI root ~100 GB + corpus 2 GB + shards ~4.5 GB + ckpts ~7 GB

DRY_RUN=no; MARKET=spot; FALLBACK=no; AZ=""; WITH_E4=no
while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRY_RUN=yes ;;
    --on-demand) MARKET=on-demand ;;
    --fallback) FALLBACK=yes ;;
    --with-e4) WITH_E4=yes ;;
    --az) AZ="$2"; shift ;;
    --branch) BRANCH="$2"; shift ;;
    *) echo "unknown flag: $1" >&2; exit 2 ;;
  esac
  shift
done
# 36 h failsafe covers E1's ~20 h grid (poc/gpu/README.md E1 cost table);
# +6 h headroom when the ~2 h E4 chain runs on the same boot.
FAILSAFE_MIN=2160
[ "$WITH_E4" = yes ] && FAILSAFE_MIN=2520

HERE="$(cd "$(dirname "$0")" && pwd)"
aws() { command aws --region "$REGION" "$@"; }

# ---- 1. ephemeral ssh keypair (local file + EC2 import, both idempotent) ----
if [ ! -f "$KEY_FILE" ]; then
  ssh-keygen -t ed25519 -N "" -C "kot-e1-ephemeral" -f "$KEY_FILE"
  echo "generated ephemeral key $KEY_FILE"
fi
# Fingerprint normalisation: ssh-keygen prints 'SHA256:<b64-no-padding>';
# EC2 stores imported ed25519 fingerprints as '<b64-with-padding>' (no prefix).
norm_fp() { printf '%s' "$1" | sed -e 's/^SHA256://' -e 's/=*$//'; }
LOCAL_FP=$(norm_fp "$(ssh-keygen -lf "$KEY_FILE.pub" | awk '{print $2}')")
REMOTE_FP=$(aws ec2 describe-key-pairs --key-names "$KEY_NAME" \
  --query 'KeyPairs[0].KeyFingerprint' --output text 2>/dev/null || echo ABSENT)
if [ "$REMOTE_FP" != ABSENT ] && [ "$(norm_fp "$REMOTE_FP")" != "$LOCAL_FP" ]; then
  echo "EC2 key pair $KEY_NAME fingerprint differs from $KEY_FILE — reimporting"
  aws ec2 delete-key-pair --key-name "$KEY_NAME"
  REMOTE_FP=ABSENT
fi
if [ "$REMOTE_FP" = ABSENT ]; then
  aws ec2 import-key-pair --key-name "$KEY_NAME" \
    --public-key-material "fileb://$KEY_FILE.pub" \
    --tag-specifications 'ResourceType=key-pair,Tags=[{Key=Project,Value=kernel-of-truth}]' \
    --query 'KeyName' --output text
fi
echo "key pair: $KEY_NAME (local: $KEY_FILE)"

# ---- 2. security group: ssh ONLY from this box's PRIVATE ip (same VPC) ----
TOKEN=$(curl -s -X PUT "http://169.254.169.254/latest/api/token" \
  -H "X-aws-ec2-metadata-token-ttl-seconds: 300")
MY_IP=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" \
  http://169.254.169.254/latest/meta-data/local-ipv4)
case "$MY_IP" in
  *.*.*.*) : ;;
  *) echo "could not fetch private IP from IMDSv2 (got: '$MY_IP')" >&2; exit 1 ;;
esac
VPC_ID=$(aws ec2 describe-vpcs --filters Name=is-default,Values=true \
  --query 'Vpcs[0].VpcId' --output text)
[ "$VPC_ID" != None ] || { echo "no default VPC in $REGION" >&2; exit 1; }
SG_ID=$(aws ec2 describe-security-groups \
  --filters "Name=group-name,Values=$SG_NAME" "Name=vpc-id,Values=$VPC_ID" \
  --query 'SecurityGroups[0].GroupId' --output text)
if [ "$SG_ID" = None ]; then
  SG_ID=$(aws ec2 create-security-group --group-name "$SG_NAME" \
    --description "kernel-of-truth E1 pull path: ssh from coordinator private IP only" \
    --vpc-id "$VPC_ID" \
    --tag-specifications "ResourceType=security-group,Tags=[{Key=Project,Value=kernel-of-truth},{Key=Name,Value=$SG_NAME}]" \
    --query GroupId --output text)
  echo "created security group $SG_ID"
fi
SSH_CIDRS=$(aws ec2 describe-security-groups --group-ids "$SG_ID" \
  --query "SecurityGroups[0].IpPermissions[?IpProtocol=='tcp' && FromPort==\`22\` && ToPort==\`22\`].IpRanges[].CidrIp" \
  --output text)
if ! printf '%s\n' "$SSH_CIDRS" | tr '\t' '\n' | grep -qxF "$MY_IP/32"; then
  aws ec2 authorize-security-group-ingress --group-id "$SG_ID" \
    --protocol tcp --port 22 --cidr "$MY_IP/32" \
    --query 'Return' --output text
  echo "authorised 22/tcp from $MY_IP/32"
fi
echo "security group: $SG_ID (ssh only from $MY_IP/32; default all-egress)"

# ---- 3. current PyTorch DLAMI (newest first; queried, never hardcoded) ----
AMI_JSON=$(aws ec2 describe-images \
  --owners amazon \
  --filters "Name=name,Values=Deep Learning OSS Nvidia Driver AMI GPU PyTorch*" "Name=state,Values=available" \
  --query 'reverse(sort_by(Images,&CreationDate))[0].{Id:ImageId,Name:Name}' --output json)
AMI_ID=$(echo "$AMI_JSON" | sed -n 's/.*"Id": "\(ami-[a-z0-9]*\)".*/\1/p')
[ -n "$AMI_ID" ] || { echo "no PyTorch DLAMI found in $REGION" >&2; exit 1; }
echo "AMI: $AMI_JSON"

# ---- 4. subnet: a default-for-az subnet in the default VPC ----
SUBNET_FILTERS=("Name=default-for-az,Values=true" "Name=vpc-id,Values=$VPC_ID")
[ -n "$AZ" ] && SUBNET_FILTERS+=("Name=availability-zone,Values=$AZ")
SUBNET_ID=$(aws ec2 describe-subnets --filters "${SUBNET_FILTERS[@]}" \
  --query 'Subnets[0].SubnetId' --output text)
[ "$SUBNET_ID" != "None" ] || { echo "no default-for-az subnet in $REGION $AZ" >&2; exit 1; }
echo "subnet: $SUBNET_ID"

# ---- 5. user-data: rendered from the PULL template; NO credentials ----
UD_FILE=$(mktemp)
trap 'rm -f "$UD_FILE"' EXIT
sed -e "s|__REPO__|$REPO|g" \
    -e "s|__BRANCH__|$BRANCH|g" \
    -e "s|__WITH_E4__|$WITH_E4|g" \
    -e "s|__FAILSAFE_MIN__|$FAILSAFE_MIN|g" \
    "$HERE/user-data-e1-pull.sh.tpl" > "$UD_FILE"
if grep -qiE 'BEGIN (OPENSSH|RSA|EC) PRIVATE KEY|aws_secret|ghp_|github_pat_' "$UD_FILE"; then
  echo "REFUSING TO LAUNCH: rendered user-data appears to contain a credential" >&2
  exit 1
fi

# ---- 6. run-instances ----
run_instances() { # $1 = spot|on-demand, $2 = yes|no (dry run)
  local args=(
    ec2 run-instances
    --image-id "$AMI_ID"
    --instance-type "$INSTANCE_TYPE"
    --subnet-id "$SUBNET_ID"
    --security-group-ids "$SG_ID"
    --key-name "$KEY_NAME"
    --count 1
    --instance-initiated-shutdown-behavior terminate
    --block-device-mappings "[{\"DeviceName\":\"/dev/sda1\",\"Ebs\":{\"VolumeSize\":$VOLUME_GB,\"VolumeType\":\"gp3\",\"DeleteOnTermination\":true}}]"
    --tag-specifications
      'ResourceType=instance,Tags=[{Key=Project,Value=kernel-of-truth},{Key=Name,Value=kot-e1}]'
      'ResourceType=volume,Tags=[{Key=Project,Value=kernel-of-truth},{Key=Name,Value=kot-e1}]'
    --user-data "file://$UD_FILE"
  )
  if [ "$1" = spot ]; then
    args+=(--instance-market-options 'MarketType=spot,SpotOptions={SpotInstanceType=one-time,InstanceInterruptionBehavior=terminate}')
  fi
  [ "$2" = yes ] && args+=(--dry-run)
  aws "${args[@]}"
}

if [ "$DRY_RUN" = yes ]; then
  echo "--- DRY RUN ($MARKET, with-e4=$WITH_E4, failsafe ${FAILSAFE_MIN}m) ---"
  set +e
  OUT=$(run_instances "$MARKET" yes 2>&1)
  RC=$?
  set -e
  echo "$OUT"
  if echo "$OUT" | grep -q DryRunOperation; then
    echo "DRY RUN OK: request would have succeeded"
    echo "(keypair + SG were created for real; collect-e1.sh --cleanup-only removes them)"
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
echo "launched $IID (pull path — no credentials on the box; with-e4=$WITH_E4)"
echo "collect:    $HERE/collect-e1.sh $IID"
echo "watch:      aws ec2 describe-instances --region $REGION --instance-ids $IID --query 'Reservations[].Instances[].State.Name'"
echo "terminate:  aws ec2 terminate-instances --region $REGION --instance-ids $IID"
echo "The box waits for collection when done; ${FAILSAFE_MIN} min failsafe poweroff caps cost."
