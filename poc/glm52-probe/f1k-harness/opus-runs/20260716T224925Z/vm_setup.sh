#!/usr/bin/env bash
# =============================================================================
# vm_setup.sh — OPUS ops launch wrapper (UNCOMMITTED). Runs ON the GCP Spot VM
# over SSH. It provisions the on-box environment the COMMITTED f1k_worker.sh
# needs, arms the anti-orphan backstops, and launches the committed worker
# VERBATIM (sha-pinned) autonomously. It designs/changes NO science: it only
# supplies environment + file layout + safety, exactly the plumbing the
# committed harness assumes (README step 2 "RAID0+mount, scp, launch detached")
# plus the validated dump-precondition(b) COLIBRI_TREE env-fix.
# =============================================================================
set -euo pipefail
LOG="$HOME/f1k-setup.log"
exec > >(tee -a "$LOG") 2>&1
echo "########## vm_setup start $(date -u +%FT%TZ)  user=$USER home=$HOME ##########"

BUCKET="gs://kot-f1k-estate-85e2ca29"
SPOT_RATE="0.17394"   # 2-SSD all-in (right-sized from infeasible 3; in-window)
COLIBRI_URL="https://github.com/JustVugg/colibri"
COLIBRI_COMMIT="a78a06fc5acc4b0dc0f9ef03987c66b0559d1250"
PRISTINE_BLOB="1d74f7886022baaf3fa936602f9db3a4d82f7f21"
MAXLIFE_SEC=$((15*3600))   # guest hard self-halt cap (anti-idle backstop #2)
GATE="$HOME/f1k-gate"
fail() { echo "ERR_VM_SETUP: $*" >&2; mkdir -p "$GATE"; \
  echo "{\"ts\":\"$(date -u +%FT%TZ)\",\"stage\":\"FAILED: setup: $*\"}" > "$GATE/heartbeat.json"; exit 1; }

echo "=== backstop #2: guest max-lifetime self-halt (root nohup ${MAXLIFE_SEC}s) ==="
sudo bash -c "setsid nohup bash -c 'sleep $MAXLIFE_SEC; wall f1k-maxlife-reached-powering-off; shutdown -h now' >/var/log/f1k-maxlife.log 2>&1 < /dev/null &"
echo "armed guest max-life self-halt (~15h)."

echo "=== install tools (google-cloud-cli for gsutil, mdadm, build tools) ==="
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -qq
sudo apt-get install -y -qq apt-transport-https ca-certificates gnupg curl mdadm build-essential git binutils python3 python3-pip >/dev/null
if ! command -v gsutil >/dev/null 2>&1; then
  curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg
  echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee /etc/apt/sources.list.d/google-cloud-sdk.list >/dev/null
  sudo apt-get update -qq
  sudo apt-get install -y -qq google-cloud-cli >/dev/null
fi
command -v gsutil >/dev/null 2>&1 || fail "gsutil still missing after install"
echo "gsutil: $(command -v gsutil)"

echo "=== RAID0 + mount local NVMe SSD at /mnt/nvme (count-agnostic; estate 383.8GB) ==="
mapfile -t DEVS < <(ls -1 /dev/disk/by-id/google-local-nvme-ssd-* 2>/dev/null | sort)
N="${#DEVS[@]}"
echo "local nvme devices ($N): ${DEVS[*]:-none}"
[ "$N" -ge 2 ] || fail "need >=2 local nvme (estate 383.8GB > 375GB single), got $N"
if [ ! -e /dev/md0 ]; then
  sudo mdadm --create /dev/md0 --level=0 --raid-devices="$N" "${DEVS[@]}" --run --force
  sudo mkfs.ext4 -F -m 0 /dev/md0 >/dev/null 2>&1
fi
sudo mkdir -p /mnt/nvme
mountpoint -q /mnt/nvme || sudo mount /dev/md0 /mnt/nvme
sudo chown -R "$USER":"$(id -gn)" /mnt/nvme
df -h /mnt/nvme | tail -1

echo "=== unpack committed harness bundle -> \$HOME/f1k (+ ../../kae-patch-draft copy) ==="
mkdir -p "$HOME/f1k"
tar -xzf "$HOME/f1k-bundle.tgz" -C "$HOME/f1k"
# dump-precondition(b) fix: real-checks.sh reads KAE_DIR=$HERE/../../kae-patch-draft
cp -r "$HOME/f1k/kae-patch-draft" "$HOME/kae-patch-draft"
[ -f "$HOME/f1k/f1k_worker.sh" ] || fail "worker not in bundle"

echo "=== dump-precondition(b) fix: pre-clone PRISTINE colibri as COLIBRI_TREE ==="
if [ ! -d "$HOME/colibri-pristine/.git" ]; then
  git clone --quiet "$COLIBRI_URL" "$HOME/colibri-pristine"
fi
( cd "$HOME/colibri-pristine" && git fetch --all --quiet || true && git checkout --quiet "$COLIBRI_COMMIT" )
BLOB="$(git -C "$HOME/colibri-pristine" hash-object c/glm.c)"
[ "$BLOB" = "$PRISTINE_BLOB" ] || fail "pristine glm.c blob $BLOB != $PRISTINE_BLOB"
echo "pristine colibri @ $COLIBRI_COMMIT (glm.c blob verified)"

echo "=== write run-worker.sh (env + on-exit backstop #1) ==="
cat > "$HOME/run-worker.sh" <<WEOF
#!/usr/bin/env bash
export KOT_F1K_BUCKET="$BUCKET"
export COLIBRI_GIT_URL="$COLIBRI_URL"
export KOT_F1K_SPOT_RATE="$SPOT_RATE"
export COLIBRI_TREE="\$HOME/colibri-pristine"
export HF_HUB_ENABLE_HF_TRANSFER=1
mkdir -p "$GATE"
cd "\$HOME/f1k"
echo "== committed f1k_worker.sh START \$(date -u +%FT%TZ) =="
bash "\$HOME/f1k/f1k_worker.sh"; rc=\$?
echo "== committed f1k_worker.sh EXIT rc=\$rc \$(date -u +%FT%TZ) =="
if [ \$rc -ne 0 ]; then
  echo "{\"ts\":\"\$(date -u +%FT%TZ)\",\"stage\":\"FAILED: worker exit \$rc\"}" > "$GATE/heartbeat.json"
  gsutil -q cp "$GATE/heartbeat.json" "$BUCKET/f1k/bringup/heartbeat.json" || true
  echo "WORKER FAILED (rc=\$rc). Powering off in 2 min to stop billing; staging artifacts (if any) are in $BUCKET."
  sudo shutdown -h +2
else
  echo "{\"ts\":\"\$(date -u +%FT%TZ)\",\"stage\":\"DONE-bringup-scaffold-READY-FOR-ONBOX-REVIEW\"}" > "$GATE/heartbeat.json"
  gsutil -q cp "$GATE/heartbeat.json" "$BUCKET/f1k/bringup/heartbeat.json" || true
  echo "WORKER DONE. Autonomous bring-up scaffold complete. VM HELD for coordinator on-box (a)+(c)+affordability finalization. Anti-idle: 15h guest self-halt + control-box watchdog (14h) + coordinator teardown."
fi
WEOF
chmod +x "$HOME/run-worker.sh"

echo "=== launch committed worker (detached, autonomous) ==="
setsid nohup bash "$HOME/run-worker.sh" > "$HOME/f1k-worker.log" 2>&1 < /dev/null &
WPID=$!
sleep 2
echo "WORKER_LAUNCHED pid=$WPID  log=\$HOME/f1k-worker.log"
mkdir -p "$GATE"
echo "{\"ts\":\"$(date -u +%FT%TZ)\",\"stage\":\"setup-complete-worker-launched\"}" > "$GATE/heartbeat.json"
gsutil -q cp "$GATE/heartbeat.json" "$BUCKET/f1k/bringup/heartbeat.json" || true
echo "########## SETUP COMPLETE $(date -u +%FT%TZ) ##########"
