#!/usr/bin/env bash
# OPUS run-script (kern/opus-runner-1): launch the 99a v3 FULL grid (114 cells)
# on the hardened exact-REML estimator (commit b13f22e0), FRESH durable Volume
# kot-99a-grid-v3-vol on Modal workspace jesse-70413 (modal3). Detached; Modal-
# side run_grid_batch keeps banking durably even if this local driver dies.
set -euo pipefail
cd /home/ec2-user/css/kernel/kernel-of-truth/poc/99a-sim/results/frozen-run
set -a; source /home/ec2-user/.config/kot/modal3.env; set +a
exec /home/ec2-user/css/kernel/kernel-of-truth/poc/99a-sim/venv/bin/modal \
  run kot_99a_grid_v3.py::main --mode full
