#!/usr/bin/env bash
# Terminate every kot-e2 instance (tag Name=kot-e2) in eu-west-2.
set -euo pipefail
REGION="${KOT_E2_REGION:-eu-west-2}"

IDS=$(aws ec2 describe-instances --region "$REGION" \
  --filters "Name=tag:Name,Values=kot-e2" \
            "Name=instance-state-name,Values=pending,running,stopping,stopped" \
  --query 'Reservations[].Instances[].InstanceId' --output text)

if [ -z "$IDS" ]; then
  echo "no live kot-e2 instances in $REGION"
  exit 0
fi
echo "terminating: $IDS"
if [ "${1:-}" != "--yes" ]; then
  read -r -p "confirm [y/N] " ans
  [ "$ans" = y ] || { echo "aborted"; exit 1; }
fi
# shellcheck disable=SC2086
aws ec2 terminate-instances --region "$REGION" --instance-ids $IDS \
  --query 'TerminatingInstances[].{Id:InstanceId,State:CurrentState.Name}' --output table
