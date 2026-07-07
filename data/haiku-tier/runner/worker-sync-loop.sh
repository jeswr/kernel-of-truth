#!/bin/bash
# Detached worker->local record sync. Survives Claude session/account events
# (harness Monitor tasks kept dying on the account switch). Pulls the worker's
# minted records + volume logs home every 5 min so nothing is lost when the
# worker box is eventually terminated. Idempotent rsync; safe to run alongside
# the local runner (records/ is a shared content-addressed dir, disjoint lemmas).
set -u
KEY=/home/ec2-user/.ssh/kernel-of-truth-haiku
WORKER=ec2-user@172.31.25.207
REPO=/home/ec2-user/css/kernel/kernel-of-truth
SSH="ssh -i $KEY -o StrictHostKeyChecking=no -o ConnectTimeout=12"
LOG=$REPO/data/haiku-tier/volume/worker-sync.log
mkdir -p "$REPO/data/haiku-tier/volume/worker-import"
while true; do
  ts=$(date -u +%FT%TZ)
  rsync -az --timeout=90 -e "$SSH" \
    "$WORKER:/home/ec2-user/kernel-of-truth/data/haiku-tier/records/" \
    "$REPO/data/haiku-tier/records/" >/dev/null 2>>"$LOG"
  rc1=$?
  rsync -az --timeout=90 -e "$SSH" \
    "$WORKER:/home/ec2-user/kernel-of-truth/data/haiku-tier/volume/" \
    "$REPO/data/haiku-tier/volume/worker-import/" >/dev/null 2>>"$LOG"
  n=$(ls "$REPO/data/haiku-tier/records/" 2>/dev/null | wc -l)
  echo "$ts sync rc=$rc1 local_records=$n" >> "$LOG"
  sleep 300
done
