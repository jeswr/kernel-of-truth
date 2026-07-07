#!/bin/bash
# kot-e2 user-data template (rendered by launch-e2.sh; placeholders __LIKE_THIS__).
# Runs E2 end-to-end on first boot, pushes results to a results/ branch, then
# powers off (instance-initiated-shutdown-behavior=terminate makes that final).
set -uxo pipefail
exec > /var/log/kot-e2-userdata.log 2>&1

# Failsafe cost cap: hard poweroff after 4 h no matter what happened.
shutdown -h +240 "kot-e2 failsafe timeout" || true

RESULTS_BRANCH="__RESULTS_BRANCH__"
REPO_HTTPS="https://github.com/__REPO__.git"
REPO_SSH="git@github.com:__REPO__.git"
SRC_BRANCH="__BRANCH__"
PUSH="__PUSH__"   # yes|no

# ---- deploy key (write-scoped to this one repo; never in the repo itself) ----
if [ "$PUSH" = "yes" ]; then
  mkdir -p /root/.ssh
  echo "__DEPLOY_KEY_B64__" | base64 -d > /root/.ssh/kot-e2-deploy
  chmod 600 /root/.ssh/kot-e2-deploy
  ssh-keyscan github.com >> /root/.ssh/known_hosts 2>/dev/null
  export GIT_SSH_COMMAND="ssh -i /root/.ssh/kot-e2-deploy -o IdentitiesOnly=yes"
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
if ! $PYBIN -c 'import torch' 2>/dev/null; then
  echo "torch not preinstalled in active env; pip will fetch it (slower, works)"
fi

cd /opt
git clone --depth 1 --branch "$SRC_BRANCH" "$REPO_HTTPS" kot
cd /opt/kot

$PYBIN -m pip install --quiet -r poc/e2/runner/requirements.txt

nvidia-smi || true
$PYBIN poc/e2/runner/e2_runner.py --device cuda 2>&1 | tee /var/log/kot-e2-run.log
RC=${PIPESTATUS[0]}

# Always try to preserve whatever exists (even a failed run's partial log).
cp /var/log/kot-e2-run.log poc/e2/results/ 2>/dev/null || true
if [ "$PUSH" = "yes" ]; then
  git config user.name "kot-e2-gpu-runner"
  git config user.email "kot-e2@users.noreply.github.com"
  git checkout -b "$RESULTS_BRANCH"
  git add -f poc/e2/results/
  git commit -m "E2 results ($RESULTS_BRANCH, runner rc=$RC)" || true
  git remote set-url origin "$REPO_SSH"
  git push -u origin "$RESULTS_BRANCH" || echo "PUSH FAILED — results remain on instance volume"
fi

echo "kot-e2 done rc=$RC"
shutdown -h now
