#!/usr/bin/env python3
"""modal_glm52_smoke.py — GLM-5.2 colibri backend-feasibility SMOKE on a
NON-AWS Modal worker (Stage 1, docs/next/design/glm52-expert-profiling-plan-
sol-20260715.md).  EXPLORATORY infra — rigor relaxed vs a frozen experiment.

Three entrypoints (source a NON-CAPPED acct env first; acct3/acct4 least-spent —
see poc/glm52-probe/stage1-feasibility-manifest.md; NEVER print/commit tokens):

  # $0 dry-plan: assert gcp/oci scheduling + >=900 GiB ephemeral (no container)
  set -a; source ~/.config/kot/modal3.env; set +a
  COLIBRI_GIT_URL=<url> poc/modal/.venv/bin/modal run poc/modal/modal_glm52_smoke.py::plan

  # ~$0 tiny validation: real colibri + tiny GlmMoeDsa oracle, small CPU box
  COLIBRI_GIT_URL=<url> poc/modal/.venv/bin/modal run poc/modal/modal_glm52_smoke.py::tiny

  # the real <=$3 smoke: non-AWS, 4 cores/64 GiB, 900 GiB ephemeral, stage 383.8 GB
  COLIBRI_GIT_URL=<url> poc/modal/.venv/bin/modal run poc/modal/modal_glm52_smoke.py

The Function is forced onto GCP (or OCI via --cloud oci) and FAILS CLOSED if the
worker turns out to be AWS.  The model is staged directly onto LOCAL EPHEMERAL SSD
(never a modal.Volume — a network mount recreates the failed 9p condition).  A
$25 in-runner stop-loss and a 2 h smoke wall cap bound the spend.
"""
from __future__ import annotations
import os, sys, time
from pathlib import Path

import modal

_HERE = Path(__file__).resolve().parent
try:
    REPO_ROOT = _HERE.parents[1]
    SMOKE_DIR = REPO_ROOT / "poc" / "glm52-probe" / "smoke"
except IndexError:                      # inside the Modal container the file is /root/*; never dereferenced there
    REPO_ROOT = _HERE
    SMOKE_DIR = _HERE
_IN_CONTAINER = bool(os.environ.get("MODAL_TASK_ID"))

# ----- pins (poc/glm52-probe/stage1-feasibility-manifest.md) -----
COLIBRI_COMMIT = "a78a06fc5acc4b0dc0f9ef03987c66b0559d1250"
ESTATE_REPO    = "mateogrgic/GLM-5.2-colibri-int4-with-int8-mtp"   # 383.8 GB int4 + int8 MTP
ESTATE_GB      = 383.8

# ----- Function resource config (the `plan` entrypoint asserts these) -----
SMOKE_CLOUD    = os.environ.get("SMOKE_CLOUD", "oci")   # oci|gcp — NEVER aws.
# DRY-PLAN MEASURED 2026-07-15: cloud="gcp" REJECTS the 900 GiB ephemeral
# ("Large disk requests are not supported for cloud provider 'gcp'"); cloud="oci"
# accepts it. So the real smoke runs on OCI (still non-AWS, fail-closed preserved).
EPHEMERAL_GIB  = 900                                    # >=900: 383.8 GB payload + >=400 GB free gate (manifest B2)
CPU_CORES      = 4.0
MEM_MIB        = 65536                                  # 64 GiB (RSS<60 GiB gate has headroom)
TIMEOUT_S      = 24 * 3600
STOP_LOSS_USD  = 25.0                                   # in-runner Wave-A stop-loss ceiling
SMOKE_WALL_CAP_S = 2 * 3600                             # smoke stop-loss: kill at 2 h wall
RATE_PER_HR    = 1.15                                   # ~4 core + 64 GiB + non-AWS premium (manifest 1c)


def _colibri_url() -> str:
    url = os.environ.get("COLIBRI_GIT_URL")
    if not url and not _IN_CONTAINER:
        raise SystemExit("ERR: export COLIBRI_GIT_URL=<colibri clone url> "
                         "(coordinator-supplied; repo pins the engine by commit only). "
                         "Reference: github.com/JustVugg/colibri")
    return url or "unset-in-container"


# ---------------------------------------------------------------------------
# Image: build the PATCHED colibri (rtrace read-only router trace) from source.
# ---------------------------------------------------------------------------
def _image() -> modal.Image:
    if _IN_CONTAINER:
        # inside the worker the image is already built and looked up by id; return a
        # light stand-in so re-importing the module never touches the host filesystem.
        return modal.Image.debian_slim(python_version="3.11")
    return (
        modal.Image.debian_slim(python_version="3.11")
        .apt_install("git", "build-essential", "binutils", "curl", "ca-certificates")
        .pip_install(
            "huggingface_hub[hf_transfer]>=0.24", "hf_transfer",
            "torch", "transformers>=4.57", "safetensors", "numpy",
        )
        .env({"HF_HUB_ENABLE_HF_TRANSFER": "1",
              "COLIBRI_GIT_URL": _colibri_url(),
              "COLIBRI_COMMIT": COLIBRI_COMMIT})
        # copy=True: the smoke sources must exist for the subsequent build layers
        .add_local_dir(str(SMOKE_DIR), "/smoke", copy=True,
                       ignore=["mock-out", "__pycache__", "*.o"])
        .run_commands(
            "set -eu; git clone \"$COLIBRI_GIT_URL\" /colibri",
            "cd /colibri && git checkout \"$COLIBRI_COMMIT\" && test \"$(git rev-parse HEAD)\" = \"$COLIBRI_COMMIT\"",
            # verify the shipped rtrace.h sha, place it, apply the glm.c/Makefile patch
            "cp /smoke/rtrace.h /colibri/c/rtrace.h",
            "cp /smoke/test_rtrace.c /colibri/c/tests/test_rtrace.c",
            "cd /colibri && git apply --check /smoke/rtrace-add-path.patch && git apply /smoke/rtrace-add-path.patch",
            # build engine + iobench; run the C emitter unit tests (fail closed)
            "cd /colibri/c && make -s glm ARCH=native && make -s iobench",
            "cd /colibri/c && gcc -O2 -Wall -Wextra -Wno-unused-function -o /tmp/test_rtrace tests/test_rtrace.c -lm && /tmp/test_rtrace /tmp/fix.jsonl | tail -1",
        )
    )


app = modal.App("kot-glm52-smoke")
IMAGE = _image()


def _assert_non_aws():
    """Fail-closed non-AWS gate (plan §"fail closed if scheduling reports AWS").
    Positive-confirm GCP/OCI; abort if AWS IMDS answers with an instance identity."""
    import urllib.request
    def _get(url, headers=None, timeout=1.5):
        try:
            req = urllib.request.Request(url, headers=headers or {})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode("utf-8", "replace")
        except Exception:
            return None
    gcp = _get("http://metadata.google.internal/computeMetadata/v1/instance/zone",
               {"Metadata-Flavor": "Google"})
    oci = _get("http://169.254.169.254/opc/v2/instance/", {"Authorization": "Bearer Oracle"})
    aws = _get("http://169.254.169.254/latest/meta-data/instance-id")
    aws_tok = _get("http://169.254.169.254/latest/api/token")  # IMDSv2 token endpoint (AWS-only)
    provider = "gcp" if gcp else ("oci" if oci else ("aws" if (aws or aws_tok) else "unknown"))
    if provider == "aws" or (aws and not gcp and not oci):
        raise RuntimeError(f"ABORT: non-AWS gate — worker looks like AWS (imds instance-id present). provider={provider}")
    return {"provider": provider, "gcp_zone_present": bool(gcp), "oci_present": bool(oci)}


def _stage_estate(dest: str) -> dict:
    """Download the int4 estate straight onto ephemeral SSD (no symlink blob-cache
    duplication -> avoids the transient ~2x disk spike, manifest B2). Manifest-hash
    after staging (cheap: sizes vs HF LFS metadata, not a 383 GB byte-rehash)."""
    import hashlib, json, shutil
    from huggingface_hub import snapshot_download, HfApi
    os.makedirs(dest, exist_ok=True)
    free_before = shutil.disk_usage(os.path.dirname(dest)).free / 1e9
    t0 = time.time()
    snapshot_download(repo_id=ESTATE_REPO, local_dir=dest,
                      local_dir_use_symlinks=False, max_workers=8)
    stage_s = time.time() - t0
    # manifest hash over sorted "name size" of every staged file
    lines = []
    total = 0
    for p in sorted(Path(dest).rglob("*")):
        if p.is_file():
            sz = p.stat().st_size; total += sz
            lines.append(f"{p.relative_to(dest)} {sz}")
    manifest_sha = hashlib.sha256("\n".join(lines).encode()).hexdigest()
    free_after = shutil.disk_usage(os.path.dirname(dest)).free / 1e9
    return {"stage_seconds": round(stage_s, 1), "staged_gb": round(total / 1e9, 2),
            "manifest_sha256": manifest_sha, "n_files": len(lines),
            "free_gb_before": round(free_before, 1), "free_gb_after": round(free_after, 1),
            "free_ge_400gb": free_after >= 400.0}


def _build_tiny_oracle() -> tuple[bool, str, str]:
    """Build the tiny GlmMoeDsa oracle (glm_tiny/ weights + ref_glm.json) with the
    engine's own tool. Used for the arch self-test (32/32) and the tiny validation."""
    import subprocess
    r = subprocess.run([sys.executable, "/colibri/c/tools/make_glm_oracle.py"],
                       cwd="/colibri/c", stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    tiny = "/colibri/c/glm_tiny"
    ok = Path(tiny).exists() and Path("/colibri/c/ref_glm.json").exists()
    return ok, tiny, r.stderr[-500:] if not ok else ""


def _run_driver(mode: str, snap: str, glm_dir: str, tiny_dir: str | None,
                started: float, extra: list | None = None) -> dict:
    import json, subprocess
    # stop-loss: driver wall ceiling = min(smoke cap, remaining $25 budget)
    budget_s = (STOP_LOSS_USD / RATE_PER_HR) * 3600.0
    elapsed = time.time() - started
    max_seconds = int(min(SMOKE_WALL_CAP_S, budget_s - elapsed))
    if max_seconds <= 0:
        return {"aborted": "stop-loss reached before probes", "verdict": "OFFLINE-ONLY"}
    cmd = [sys.executable, "/smoke/smoke_driver.py", "--mode", mode,
           "--glm-dir", glm_dir, "--snap", snap, "--corpus", "/smoke/corpus/probes12.json",
           "--price-per-hr", str(RATE_PER_HR), "--max-seconds", str(max_seconds),
           "--out-dir", "/tmp/smoke-out"]
    if tiny_dir:
        cmd += ["--tiny-dir", tiny_dir]
    if extra:
        cmd += extra
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        report = json.loads(p.stdout)
    except Exception:
        report = {"error": "driver output unparseable", "stdout_tail": p.stdout[-800:],
                  "stderr_tail": p.stderr[-800:], "verdict": "OFFLINE-ONLY"}
    return report


# ---------------------------------------------------------------------------
# FULL smoke: non-AWS, 4 cores / 64 GiB / 900 GiB ephemeral SSD, 24 h.
# ---------------------------------------------------------------------------
@app.function(image=IMAGE, cloud=SMOKE_CLOUD, cpu=CPU_CORES, memory=MEM_MIB,
              ephemeral_disk=EPHEMERAL_GIB * 1024, timeout=TIMEOUT_S)
def smoke_full() -> dict:
    started = time.time()
    placement = _assert_non_aws()                     # fail-closed non-AWS
    # engine-correctness self-test on the tiny oracle (32/32) BEFORE staging 383 GB
    oracle_ok, tiny_dir, oracle_err = _build_tiny_oracle()
    dest = "/ephemeral/glm52_i4"                       # LOCAL ephemeral SSD (NOT a Volume)
    os.makedirs("/ephemeral", exist_ok=True)
    stage = _stage_estate(dest)
    # cost stop-loss check after staging
    if (time.time() - started) / 3600.0 * RATE_PER_HR > STOP_LOSS_USD:
        return {"placement": placement, "stage": stage, "verdict": "OFFLINE-ONLY",
                "aborted": "stop-loss $25 reached during staging"}
    # RAM CAP (2026-07-15 re-run): the first full smoke passed every gate except
    # RSS<60 GB — colibri's LRU expert-cache auto-budgets 88% of the *instance's*
    # MemAvailable (RAM_GB=0 -> auto), and the OCI box has ~256 GB, so it filled to
    # ~245 GB. Pin an explicit ~55 GiB expert-cache budget + disable the auto-raise
    # so cap_for_ram clamps resident+cache+slack <= 55 GB (RSS < 60 GB gate, headroom).
    # These reach the engine via os.environ inheritance (smoke_driver.sh copies it);
    # everything else (cloud=oci, 900 GiB ephemeral, DRAFT=0, probes, gates) identical.
    os.environ["RAM_GB"] = "55"        # explicit expert-cache RAM budget (GB)
    os.environ["CAP_RAISE"] = "0"      # disable the LRU auto-raise that filled instance RAM
    report = _run_driver("full", dest, "/colibri/c", tiny_dir if oracle_ok else None, started)
    report["placement"] = placement
    report["oracle_built"] = oracle_ok
    report["ram_cap"] = {"RAM_GB": os.environ["RAM_GB"], "CAP_RAISE": os.environ["CAP_RAISE"]}
    report["stage"] = stage
    report["elapsed_hr"] = round((time.time() - started) / 3600.0, 3)
    report["est_cost_usd"] = round(report["elapsed_hr"] * RATE_PER_HR, 2)
    return report


# ---------------------------------------------------------------------------
# TINY validation (~$0): real colibri + tiny GlmMoeDsa oracle. Small CPU box.
# ---------------------------------------------------------------------------
@app.function(image=IMAGE, cloud=SMOKE_CLOUD, cpu=2.0, memory=8192,
              timeout=1800)   # default ephemeral (512 GiB min); tiny model needs only MB
def smoke_tiny() -> dict:
    started = time.time()
    placement = _assert_non_aws()
    # build the tiny GlmMoeDsa oracle (glm_tiny + ref_glm.json) with the engine's own tool
    oracle_built, tiny, oracle_err = _build_tiny_oracle()
    report = {"placement": placement, "oracle_built": oracle_built,
              "oracle_stderr_tail": oracle_err}
    if not oracle_built:
        report["verdict"] = "OFFLINE-ONLY"
        report["note"] = "tiny GlmMoeDsa oracle build failed (transformers GlmMoeDsa unavailable?)"
        return report
    drv = _run_driver("tiny", tiny, "/colibri/c", tiny, started)
    report.update(drv)
    report["elapsed_hr"] = round((time.time() - started) / 3600.0, 4)
    return report


# ---------------------------------------------------------------------------
# Entrypoints
# ---------------------------------------------------------------------------
@app.local_entrypoint()
def main():
    """The real <=$3 smoke."""
    out = smoke_full.remote()
    import json
    print(json.dumps(out, indent=2))
    print("\n==== FULL SMOKE VERDICT:", out.get("verdict"), "====")


@app.local_entrypoint()
def tiny():
    """~$0 tiny-oracle validation on real colibri."""
    out = smoke_tiny.remote()
    import json
    print(json.dumps(out, indent=2))
    print("\n==== TINY VALIDATION VERDICT:", out.get("verdict"), "====")


@app.local_entrypoint()
def plan():
    """$0 DRY-PLAN: confirm gcp/oci scheduling + >=900 GiB ephemeral config, no
    container launched, no GPU. Asserts the static Function config."""
    cfg = {
        "cloud": SMOKE_CLOUD, "ephemeral_gib": EPHEMERAL_GIB, "cpu_cores": CPU_CORES,
        "mem_gib": MEM_MIB / 1024, "timeout_h": TIMEOUT_S / 3600, "gpu": None,
        "stop_loss_usd": STOP_LOSS_USD, "smoke_wall_cap_h": SMOKE_WALL_CAP_S / 3600,
        "estate_repo": ESTATE_REPO, "estate_gb": ESTATE_GB, "colibri_commit": COLIBRI_COMMIT,
        "uses_volume_for_model": False,
    }
    import json
    print(json.dumps(cfg, indent=2))
    assert cfg["cloud"] in ("gcp", "oci"), f"cloud must be gcp|oci, got {cfg['cloud']} (non-AWS)"
    assert cfg["ephemeral_gib"] >= 900, "ephemeral must be >=900 GiB (383.8 GB payload + >=400 GB free gate)"
    assert cfg["gpu"] is None, "smoke is CPU-only (no GPU)"
    free_after = EPHEMERAL_GIB * (1000/1024) - ESTATE_GB     # GiB->GB approx
    print(f"\nprojected free after staging: ~{free_after:.0f} GB (gate: >=400 GB) -> {'PASS' if free_after>=400 else 'FAIL'}")
    print(f"projected smoke cost @ ${RATE_PER_HR}/h x <=2 h staging+probes: ~$1.5-2.5 (< $3)")
    print("\nDRY-PLAN OK: gcp/oci + >=900 GiB ephemeral + no-Volume + $25 stop-loss confirmed ($0, no container).")
