#!/bin/bash
# kot-e1 user-data template (rendered by launch-e1.sh; placeholders __LIKE_THIS__).
# Runs the full pre-registered E1 grid (docs/poc-design.md E1: 5 arms x 5 seeds
# + per-condition LR sweep) end-to-end on first boot, pushes eval results +
# verdict to a results/ branch, then powers off.
set -uxo pipefail
exec > /var/log/kot-e1-userdata.log 2>&1

# Failsafe cost cap: hard poweroff after 36 h no matter what happened
# (see poc/gpu/README.md E1 cost table; expected wall ~20 h).
shutdown -h +2160 "kot-e1 failsafe timeout" || true

RESULTS_BRANCH="__RESULTS_BRANCH__"
REPO_HTTPS="https://github.com/__REPO__.git"
REPO_SSH="git@github.com:__REPO__.git"
SRC_BRANCH="__BRANCH__"
PUSH="__PUSH__"   # yes|no

# ---- deploy key (write-scoped to this one repo; never in the repo itself) ----
if [ "$PUSH" = "yes" ]; then
  mkdir -p /root/.ssh
  echo "__DEPLOY_KEY_B64__" | base64 -d > /root/.ssh/kot-e1-deploy
  chmod 600 /root/.ssh/kot-e1-deploy
  ssh-keyscan github.com >> /root/.ssh/known_hosts 2>/dev/null
  export GIT_SSH_COMMAND="ssh -i /root/.ssh/kot-e1-deploy -o IdentitiesOnly=yes"
fi

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

cd /opt
git clone --depth 1 --branch "$SRC_BRANCH" "$REPO_HTTPS" kot
cd /opt/kot

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

# Always preserve whatever exists (even a failed run's partial log).
cp /var/log/kot-e1-run.log poc/e1/results/ 2>/dev/null || true
cp /opt/e1work/lr-selection.json poc/e1/results/ 2>/dev/null || true
if [ "$PUSH" = "yes" ]; then
  git config user.name "kot-e1-gpu-runner"
  git config user.email "kot-e1@users.noreply.github.com"
  git checkout -b "$RESULTS_BRANCH"
  git add -f poc/e1/results/
  git commit -m "E1 results ($RESULTS_BRANCH, runner rc=$RC)" || true
  git remote set-url origin "$REPO_SSH"
  git push -u origin "$RESULTS_BRANCH" || echo "PUSH FAILED — results remain on instance volume"
fi

echo "kot-e1 done rc=$RC"
shutdown -h now
