#!/bin/bash
# kot-e2 PULL-PATH user-data template (rendered by launch-e2-pull.sh;
# placeholders __LIKE_THIS__). Option B of poc/gpu/README.md: NO credentials
# of any kind ever enter user-data. The box clones the PUBLIC repo over https,
# runs E2, writes results to /opt/e2/results/, touches /opt/e2/results/DONE,
# and then WAITS to be collected by poc/gpu/collect-e2.sh (which scps the
# results off over ssh and terminates the instance). Cost cap: the 4 h
# failsafe poweroff below + shutdown-behavior=terminate set at launch.
set -uxo pipefail
exec > /var/log/kot-e2-userdata.log 2>&1

# Failsafe cost cap: hard poweroff after 4 h no matter what happened.
# (launch sets instance-initiated-shutdown-behavior=terminate, so this
# poweroff terminates the instance even if collection never happens.)
shutdown -h +240 "kot-e2 failsafe timeout" || true

REPO_HTTPS="https://github.com/__REPO__.git"
SRC_BRANCH="__BRANCH__"

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

# ---- publish results for pull collection (world-readable; DONE is LAST) ----
mkdir -p /opt/e2/results
cp -r /opt/kot/poc/e2/results/. /opt/e2/results/ 2>/dev/null || true
cp /var/log/kot-e2-run.log /opt/e2/results/ 2>/dev/null || true
# snapshot of this bootstrap log (still being appended to; snapshot is enough)
cp /var/log/kot-e2-userdata.log /opt/e2/results/ 2>/dev/null || true
echo "rc=$RC" > /opt/e2/results/RUNNER_EXIT
chmod -R a+rX /opt/e2
sync
touch /opt/e2/results/DONE

echo "kot-e2 pull-path done rc=$RC — awaiting collect-e2.sh (failsafe poweroff still armed)"
# Deliberately NO shutdown here: collect-e2.sh terminates the instance after
# scp. If collection never happens, the 4 h failsafe above caps the cost.
