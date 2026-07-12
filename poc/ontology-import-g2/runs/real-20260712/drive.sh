#!/bin/bash
# ONT-TYPE-G2/1 driver — sequential per frozen runner_constraints (concurrency_cap 1).
# Any non-zero exit STOPS the whole campaign: 3=cap-stop, 4=blinding-abort, 2=pin/abort.
set -u
REPO=/home/ec2-user/css/kernel/kernel-of-truth
RUN=$REPO/poc/ontology-import-g2/runs/real-20260712
LOG=$RUN/driver.log
echo "DRIVER start $(date -u +%FT%TZ)" >> "$LOG"
for pk in pA pB; do
  for arm in a1 a2 a3; do
    for phase in real probe; do
      echo "BLOCK $pk $arm $phase start $(date -u +%FT%TZ)" >> "$LOG"
      nice -n 10 python3 "$REPO/poc/ontology-import-g2/run-ontg2.py" "$phase" "$pk" "$arm" "$RUN" >> "$LOG" 2>&1
      rc=$?
      echo "BLOCK $pk $arm $phase exit=$rc $(date -u +%FT%TZ)" >> "$LOG"
      if [ $rc -ne 0 ]; then
        echo "DRIVER STOP rc=$rc (3=cap-stop no-retry, 4=blinding-abort, 2=abort) $(date -u +%FT%TZ)" >> "$LOG"
        exit $rc
      fi
    done
  done
done
echo "DRIVER all blocks complete $(date -u +%FT%TZ)" >> "$LOG"
