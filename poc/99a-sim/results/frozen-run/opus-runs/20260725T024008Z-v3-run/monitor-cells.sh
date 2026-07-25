#!/usr/bin/env bash
set -u
cd /home/ec2-user/css/kernel/kernel-of-truth/poc/99a-sim/results/frozen-run
set -a; source /home/ec2-user/.config/kot/modal3.env; set +a
MODAL=/home/ec2-user/css/kernel/kernel-of-truth/poc/99a-sim/venv/bin/modal
START=$(date +%s)
while :; do
  N=$("$MODAL" volume ls kot-99a-grid-v3-vol /cells 2>/dev/null | grep -c 'cell_' || true)
  N=${N:-0}
  EL=$(( $(date +%s) - START ))
  echo "$(date -u +%H:%M:%SZ) elapsed=${EL}s durable_cells=${N}"
  if [ "$N" -ge 3 ] 2>/dev/null; then echo "FIRST-CELLS-LANDED n=${N}"; break; fi
  if [ "$EL" -ge 2400 ]; then echo "MONITOR-TIMEOUT n=${N}"; break; fi
  sleep 90
done
