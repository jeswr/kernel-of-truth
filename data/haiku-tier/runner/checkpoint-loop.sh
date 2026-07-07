#!/bin/bash
# Continuous off-box durability for minted records. Every 10 min: snapshot
# records/ + volume logs to a rotating tarball and rsync it to the worker box
# (a second machine) so a total loss of THIS box costs at most ~10 min of
# minting. Account loss is already lossless (per-record write + resumable
# skip-set in run-volume.py) — this covers box loss too. No git bloat, no
# public surface, no roborev noise.
set -u
REPO=/home/ec2-user/css/kernel/kernel-of-truth
CKDIR=/home/ec2-user/haiku-checkpoints
KEY=/home/ec2-user/.ssh/kernel-of-truth-haiku
WORKER=ec2-user@172.31.25.207
SSH="ssh -i $KEY -o StrictHostKeyChecking=no -o ConnectTimeout=12"
LOG=$REPO/data/haiku-tier/volume/checkpoint.log
mkdir -p "$CKDIR"
while true; do
  stamp=$(date -u +%Y%m%d-%H%M%S)
  f=$CKDIR/records-$stamp.tar.zst
  tar --zstd -cf "$f" -C "$REPO/data/haiku-tier" \
    records volume/failures.jsonl volume/cannot-formalise.jsonl volume/usage-log.jsonl 2>/dev/null
  n=$(ls "$REPO/data/haiku-tier/records/" 2>/dev/null | wc -l)
  sz=$(du -h "$f" 2>/dev/null | cut -f1)
  rsync -az --timeout=90 -e "$SSH" "$f" "$WORKER:/home/ec2-user/haiku-checkpoints/" >/dev/null 2>>"$LOG"
  rc=$?
  echo "$(date -u +%FT%TZ) checkpoint records=$n size=$sz off_box_rsync_rc=$rc" >> "$LOG"
  # keep only the newest 6 local checkpoints
  ls -1t "$CKDIR"/records-*.tar.zst 2>/dev/null | tail -n +7 | xargs -r rm -f
  sleep 600
done
