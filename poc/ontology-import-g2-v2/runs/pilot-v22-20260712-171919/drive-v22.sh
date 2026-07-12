#!/bin/bash
set -u
cd /home/ec2-user/css/kernel/kernel-of-truth
H=poc/ontology-import-g2-v2/run-ontg2v2.py
RUN=poc/ontology-import-g2-v2/runs/pilot-v22-20260712-171919; LOG=$RUN/driver.log
echo "V22 PILOT start $(date -u +%FT%TZ)" >> "$LOG"
for pk in pA pB; do
  nice -n 10 python3 $H preflight $pk "$RUN" --rubric v22 >> "$LOG" 2>&1
  rc=$?; echo "PREFLIGHT $pk exit=$rc" >> "$LOG"; [ $rc -ne 0 ] && { echo "STOP preflight rc=$rc" >> "$LOG"; exit $rc; }
done
for pk in pA pB; do
  nice -n 10 python3 $H pilot $pk "$RUN" --rubric v22 >> "$LOG" 2>&1
  rc=$?; echo "PILOT $pk exit=$rc" >> "$LOG"; [ $rc -ne 0 ] && { echo "STOP pilot rc=$rc" >> "$LOG"; exit $rc; }
done
nice -n 10 python3 $H pilotgate "$RUN" --rubric v22 >> "$LOG" 2>&1
echo "PILOTGATE exit=$? $(date -u +%FT%TZ)" >> "$LOG"
echo "V22 PILOT done $(date -u +%FT%TZ)" >> "$LOG"
