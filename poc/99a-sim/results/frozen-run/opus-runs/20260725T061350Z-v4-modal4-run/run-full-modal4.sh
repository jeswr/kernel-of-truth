#!/usr/bin/env bash
# OPUS run-script (kern/opus-runner-1): RESUME the 99a v4 full grid on MODAL4
# (jeswrsolidserver) after modal3 was spend-disabled at 25/114. Fresh empty
# kot-99a-grid-v4-vol in modal4's workspace -> runs all 114. Same Option-A
# topology, durable, resumable. Detached.
set -euo pipefail
cd /home/ec2-user/css/kernel/kernel-of-truth/poc/99a-sim/results/frozen-run
set -a; source /home/ec2-user/.config/kot/modal4.env; set +a
exec /home/ec2-user/css/kernel/kernel-of-truth/poc/99a-sim/venv/bin/modal \
  run kot_99a_grid_v4.py::main --mode full
