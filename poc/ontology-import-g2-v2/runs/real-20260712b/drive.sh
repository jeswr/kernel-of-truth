#!/bin/bash
set -u
REPO=/home/ec2-user/css/kernel/kernel-of-truth; cd "$REPO"
RUN=poc/ontology-import-g2-v2/runs/real-20260712b; LOG=$RUN/driver.log
echo "DRIVER start $(date -u +%FT%TZ)" >> "$LOG"
for pk in pA pB; do
  echo "PREFLIGHT $pk $(date -u +%FT%TZ)" >> "$LOG"
  nice -n 10 python3 poc/ontology-import-g2-v2/run-ontg2v2.py preflight $pk "$RUN" >> "$LOG" 2>&1
  rc=$?; echo "PREFLIGHT $pk exit=$rc" >> "$LOG"; [ $rc -ne 0 ] && { echo "DRIVER STOP preflight rc=$rc" >> "$LOG"; exit $rc; }
done
for pk in pA pB; do for arm in a1 a2 a3; do for phase in real probe; do
  echo "BLOCK $pk $arm $phase start $(date -u +%FT%TZ)" >> "$LOG"
  nice -n 10 python3 poc/ontology-import-g2-v2/run-ontg2v2.py $phase $pk $arm "$RUN" >> "$LOG" 2>&1
  rc=$?; echo "BLOCK $pk $arm $phase exit=$rc" >> "$LOG"
  [ $rc -ne 0 ] && { echo "DRIVER STOP rc=$rc" >> "$LOG"; exit $rc; }
done; done; done
nice -n 10 python3 poc/ontology-import-g2-v2/run-ontg2v2.py assemble "$RUN" >> "$LOG" 2>&1
echo "DRIVER all blocks complete $(date -u +%FT%TZ)" >> "$LOG"
