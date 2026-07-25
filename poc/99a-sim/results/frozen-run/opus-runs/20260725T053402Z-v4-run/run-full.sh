#!/usr/bin/env bash
# OPUS run-script (kern/opus-runner-1): launch the 99a v4 FULL grid (114 cells),
# rep-parallel cell-per-container, hardened exact-REML (reml_composite b13f22e0),
# FRESH durable Volume kot-99a-grid-v4-vol on modal3 (jesse-70413). Detached;
# each container writes its cell durably (resumable) even if this driver dies.
# LAUNCH ONLY ON EXPLICIT COORDINATOR GO.
set -euo pipefail
cd /home/ec2-user/css/kernel/kernel-of-truth/poc/99a-sim/results/frozen-run
set -a; source /home/ec2-user/.config/kot/modal3.env; set +a
exec /home/ec2-user/css/kernel/kernel-of-truth/poc/99a-sim/venv/bin/modal \
  run kot_99a_grid_v4.py::main --mode full
