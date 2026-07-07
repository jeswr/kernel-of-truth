#!/bin/bash
# kot-e1 PULL-PATH user-data template (rendered by launch-e1-pull.sh;
# placeholders __LIKE_THIS__). Option B of poc/gpu/README.md applied to the
# E1 grid: NO credentials of any kind ever enter user-data. The box clones
# the PUBLIC repo over https, runs the full pre-registered E1 grid
# (poc/e1/run_all.sh full), optionally chains the E4 runner on the SAME boot
# (__WITH_E4__ = yes; docs/poc-design.md E4 rev 2, one box, sequential runs),
# publishes everything under /opt/e1/results/, touches /opt/e1/results/DONE,
# and then WAITS to be collected by poc/gpu/collect-e1.sh (which scps the
# results off over ssh and terminates the instance).
set -uxo pipefail
exec > /var/log/kot-e1-userdata.log 2>&1

# Failsafe cost cap: hard poweroff no matter what happened. Rendered as
# 2160 min (36 h) for E1 alone (~20 h expected wall — poc/gpu/README.md E1
# cost table) or 2520 min (42 h) when E4 is chained (~+2 h expected).
# (launch sets instance-initiated-shutdown-behavior=terminate, so this
# poweroff terminates the instance even if collection never happens.)
shutdown -h +__FAILSAFE_MIN__ "kot-e1 failsafe timeout" || true

REPO_HTTPS="https://github.com/__REPO__.git"
SRC_BRANCH="__BRANCH__"
WITH_E4="__WITH_E4__"   # yes|no

# ---- python env: prefer the DLAMI's preinstalled torch ----
PYBIN=python3
for act in /opt/pytorch/bin/activate /opt/conda/etc/profile.d/conda.sh; do
  [ -f "$act" ] || continue
  # shellcheck disable=SC1090
  source "$act" || true
  [ "$act" = /opt/conda/etc/profile.d/conda.sh ] && conda activate pytorch 2>/dev/null
  break
done
$PYBIN -c 'import torch, numpy' || $PYBIN -m pip install --quiet numpy torch

cd /opt || exit 1
git clone --depth 1 --branch "$SRC_BRANCH" "$REPO_HTTPS" kot
cd /opt/kot || exit 1

# ---- corpus: TinyStories train split (~1.9 GB) ----
curl -sL --retry 3 \
  https://huggingface.co/datasets/roneneldan/TinyStories/resolve/main/TinyStories-train.txt \
  -o /opt/TinyStories-train.txt
ls -la /opt/TinyStories-train.txt

# Determinism note (train_e1.py seeds everything substantive via SHA-256
# labels; this narrows CUDA kernel nondeterminism):
export CUBLAS_WORKSPACE_CONFIG=":4096:8"

nvidia-smi || true
E1_CORPUS=/opt/TinyStories-train.txt E1_WORK=/opt/e1work PYTHON=$PYBIN \
  bash poc/e1/run_all.sh full 2>&1 | tee /var/log/kot-e1-run.log
RC=${PIPESTATUS[0]}

# ---- optional E4 chain: same boot, sequential, consumes /opt/e1work ----
E4_RC=skipped
if [ "$WITH_E4" = yes ] && [ "$RC" -eq 0 ]; then
  E1_WORK=/opt/e1work E4_WORK=/opt/e4work PYTHON=$PYBIN \
    RESULTS_DIR=/opt/e4work/results \
    bash poc/e4/runner/run_e4.sh full 2>&1 | tee /var/log/kot-e4-run.log
  E4_RC=${PIPESTATUS[0]}
fi

# ---- publish results for pull collection (world-readable; DONE is LAST) ----
mkdir -p /opt/e1/results
cp -r /opt/kot/poc/e1/results/. /opt/e1/results/ 2>/dev/null || true
cp /opt/e1work/lr-selection.json /opt/e1/results/ 2>/dev/null || true
cp /var/log/kot-e1-run.log /opt/e1/results/ 2>/dev/null || true
if [ "$WITH_E4" = yes ]; then
  mkdir -p /opt/e1/results/e4
  cp -r /opt/e4work/results/. /opt/e1/results/e4/ 2>/dev/null || true
  cp /var/log/kot-e4-run.log /opt/e1/results/e4/ 2>/dev/null || true
fi
# snapshot of this bootstrap log (still being appended to; snapshot is enough)
cp /var/log/kot-e1-userdata.log /opt/e1/results/ 2>/dev/null || true
echo "rc=$RC e4_rc=$E4_RC" > /opt/e1/results/RUNNER_EXIT
chmod -R a+rX /opt/e1
sync
touch /opt/e1/results/DONE

echo "kot-e1 pull-path done rc=$RC e4_rc=$E4_RC — awaiting collect-e1.sh (failsafe poweroff still armed)"
# Deliberately NO shutdown here: collect-e1.sh terminates the instance after
# scp. If collection never happens, the failsafe above caps the cost.
