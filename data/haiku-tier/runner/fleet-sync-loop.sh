#!/bin/bash
# Pull minted records home from the whole minting fleet every 5 min so they
# merge into the local master (which checkpoint-loop.sh then ships off-box).
# Content-addressed records => union is safe. Replaces worker-sync-loop.sh
# (which covered only the single g4dn worker). Detached; survives session events.
set -u
KEY=/home/ec2-user/.ssh/kernel-of-truth-haiku
REPO=/home/ec2-user/css/kernel/kernel-of-truth
SSH="ssh -i $KEY -o StrictHostKeyChecking=no -o ConnectTimeout=12"
LOG=$REPO/data/haiku-tier/volume/fleet-sync.log
# g4dn worker (old acct) + the c6i CPU boxes (new acct)
FLEET="172.31.25.207 172.31.21.19 172.31.28.223 172.31.24.46 172.31.28.251"
while true; do
  for IP in $FLEET; do
    rsync -az --timeout=90 -e "$SSH" \
      "ec2-user@$IP:/home/ec2-user/kernel-of-truth/data/haiku-tier/records/" \
      "$REPO/data/haiku-tier/records/" >/dev/null 2>>"$LOG"
  done
  n=$(ls "$REPO/data/haiku-tier/records/" 2>/dev/null | wc -l)
  echo "$(date -u +%FT%TZ) fleet-sync done, master records=$n" >> "$LOG"
  sleep 300
done
