#!/bin/bash
# PROVISIONAL-ON-FABLE-PROXY-pA driver (kernel-of-truth-29nb).
# pA=claude-fable-5 via --pa-proxy fable; pB=haiku (frozen machinery).
# Per-judge lanes run in parallel; each lane is sequential + checkpointed;
# any nonzero rc stops that lane fail-closed (cap-stop rc=3 resumable).
set -u
REPO=/home/ec2-user/css/kernel/kernel-of-truth; cd "$REPO"
RUN=poc/ontology-import-g2-v2/runs/real-20260712-FABLEPROXY-PROVISIONAL
HARNESS=poc/ontology-import-g2-v2/run-ontg2v2.py
LOG=$RUN/driver.log
run_phase() {  # run_phase <lanelog> <args...>
  local ll=$1; shift
  echo "PHASE [$*] start $(date -u +%FT%TZ)" >> "$ll"
  nice -n 10 python3 "$HARNESS" "$@" --pa-proxy fable >> "$ll" 2>&1
  local rc=$?; echo "PHASE [$*] exit=$rc $(date -u +%FT%TZ)" >> "$ll"
  return $rc
}
lane_pre() {  # preflight + pilot for one judge
  local pk=$1 ll=$RUN/lane-$1.log
  run_phase "$ll" preflight "$pk" "$RUN" || return $?
  run_phase "$ll" pilot "$pk" "$RUN" || return $?
}
lane_full() {  # real+probe (a1..a3) + hedgeflip (a2,a3) for one judge
  local pk=$1 ll=$RUN/lane-$1.log
  for arm in a1 a2 a3; do
    for phase in real probe; do
      run_phase "$ll" "$phase" "$pk" "$arm" "$RUN" || return $?
    done
  done
  for arm in a2 a3; do
    run_phase "$ll" hedgeflip "$pk" "$arm" "$RUN" || return $?
  done
}
echo "DRIVER start $(date -u +%FT%TZ)" >> "$LOG"
lane_pre pA & PA=$!
lane_pre pB & PB=$!
wait $PA; RA=$?; wait $PB; RB=$?
echo "PRE lanes done pA=$RA pB=$RB $(date -u +%FT%TZ)" >> "$LOG"
[ $RA -ne 0 ] || [ $RB -ne 0 ] && { echo "DRIVER STOP pre-lane failure" >> "$LOG"; exit 3; }
run_phase "$LOG" pilotgate "$RUN" || { echo "DRIVER STOP pilotgate not GREEN (pilot-only assembly written)" >> "$LOG"; exit 4; }
lane_full pA & PA=$!
lane_full pB & PB=$!
wait $PA; RA=$?; wait $PB; RB=$?
echo "FULL lanes done pA=$RA pB=$RB $(date -u +%FT%TZ)" >> "$LOG"
[ $RA -ne 0 ] || [ $RB -ne 0 ] && { echo "DRIVER STOP full-lane failure" >> "$LOG"; exit 3; }
run_phase "$LOG" assemble "$RUN" || { echo "DRIVER STOP assemble failure" >> "$LOG"; exit 5; }
echo "DRIVER COMPLETE $(date -u +%FT%TZ)" >> "$LOG"
