#!/usr/bin/env python3
"""modal_glm52_wave.py — GLM-5.2 colibri Wave-A 480-item expert-profiling run
(Stage 2, docs/next/design/glm52-expert-profiling-plan-sol-20260715.md). Reuses
the PROVEN backend-smoke machinery (poc/modal/modal_glm52_smoke.py — GO-FULL-GLM52
on acct4/OCI, 2026-07-15): same NON-AWS fail-closed gate, same direct-to-ephemeral
383.8 GB int4 staging (never a modal.Volume for the model), same RAM cap
(RAM_GB=55, CAP_RAISE=0). It runs the 480-item labelled teacher-forced corpus
traced (per-item reset, DRAFT=0) in ONE glm invocation instead of the 12 probes,
then aggregates the router trace into the atlas sufficient-statistics.

EXPLORATORY infra — rigor relaxed vs a frozen experiment. A $25 in-runner
stop-loss + a 20 h wall cap bound the spend (projection from the smoke: ~2.2 h /
~$2.51). Outputs (rtrace.jsonl.gz, agg.json, trace_summary.json, facts.json,
wave-report.json, corpus copy) are written to a NAMED OUTPUT VOLUME so they
survive the ephemeral app teardown; download with `modal volume get`.

Entrypoints (source a NON-CAPPED acct env first; acct4 = modal4.env, GO-proven):
  # $0 config assertion (no container)
  COLIBRI_GIT_URL=<url> poc/modal/.venv/bin/modal run poc/modal/modal_glm52_wave.py::plan
  # ~$0 tiny plumbing dry-run: real colibri + tiny oracle over all 480 items
  COLIBRI_GIT_URL=<url> poc/modal/.venv/bin/modal run poc/modal/modal_glm52_wave.py::tiny
  # THE Wave-A run: non-AWS/OCI, 4 cores/64 GiB, 900 GiB ephemeral, stage 383.8 GB
  COLIBRI_GIT_URL=<url> poc/modal/.venv/bin/modal run poc/modal/modal_glm52_wave.py
"""
from __future__ import annotations
import os, sys, time, subprocess, shutil, hashlib, json
from pathlib import Path

import modal

_HERE = Path(__file__).resolve().parent
try:
    REPO_ROOT = _HERE.parents[1]
    SMOKE_DIR = REPO_ROOT / "poc" / "glm52-probe" / "smoke"
    WAVE_DIR = REPO_ROOT / "poc" / "glm52-probe" / "wave-a"
except IndexError:
    REPO_ROOT = _HERE; SMOKE_DIR = _HERE; WAVE_DIR = _HERE
_IN_CONTAINER = bool(os.environ.get("MODAL_TASK_ID"))

# ----- pins (poc/glm52-probe/stage1-feasibility-manifest.md, smoke GO config) -----
COLIBRI_COMMIT = "a78a06fc5acc4b0dc0f9ef03987c66b0559d1250"
ESTATE_REPO    = "mateogrgic/GLM-5.2-colibri-int4-with-int8-mtp"
ESTATE_GB      = 383.8

# ----- resource config (identical to the GO-FULL-GLM52 smoke) -----
WAVE_CLOUD     = os.environ.get("WAVE_CLOUD", "oci")     # oci accepts 900 GiB ephemeral; NEVER aws
EPHEMERAL_GIB  = 900
CPU_CORES      = 4.0
MEM_MIB        = 65536                                    # 64 GiB
TIMEOUT_S      = 24 * 3600
STOP_LOSS_USD  = 25.0                                     # Wave-A hard stop-loss
WAVE_WALL_CAP_S = 20 * 3600                               # 20 h wall cap
RATE_PER_HR    = 1.15
RAM_GB         = "55"                                     # RSS<60 GB gate (smoke fix)
CAP_RAISE      = "0"

OUT_VOLUME_NAME = "kot-glm52-wave-a-out"
CORPUS_NAME     = "wave_a_corpus.json"


def _colibri_url() -> str:
    url = os.environ.get("COLIBRI_GIT_URL")
    if not url and not _IN_CONTAINER:
        raise SystemExit("ERR: export COLIBRI_GIT_URL=<colibri clone url> "
                         "(coordinator-supplied). Reference: github.com/JustVugg/colibri")
    return url or "unset-in-container"


def _image() -> modal.Image:
    if _IN_CONTAINER:
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
        .add_local_dir(str(SMOKE_DIR), "/smoke", copy=True,
                       ignore=["mock-out", "__pycache__", "*.o", "results"])
        .add_local_dir(str(WAVE_DIR), "/wave", copy=True,
                       ignore=["raw", "atlas", "__pycache__", "*.o"])
        .run_commands(
            "set -eu; git clone \"$COLIBRI_GIT_URL\" /colibri",
            "cd /colibri && git checkout \"$COLIBRI_COMMIT\" && test \"$(git rev-parse HEAD)\" = \"$COLIBRI_COMMIT\"",
            "cp /smoke/rtrace.h /colibri/c/rtrace.h",
            "cp /smoke/test_rtrace.c /colibri/c/tests/test_rtrace.c",
            "cd /colibri && git apply --check /smoke/rtrace-add-path.patch && git apply /smoke/rtrace-add-path.patch",
            "cd /colibri/c && make -s glm ARCH=native && make -s iobench",
            "cd /colibri/c && gcc -O2 -Wall -Wextra -Wno-unused-function -o /tmp/test_rtrace tests/test_rtrace.c -lm && /tmp/test_rtrace /tmp/fix.jsonl | tail -1",
        )
    )


app = modal.App("kot-glm52-wave-a")
IMAGE = _image()
OUT_VOL = modal.Volume.from_name(OUT_VOLUME_NAME, create_if_missing=True)


# --------------------------- shared helpers (in-container) ------------------
def _assert_non_aws():
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
    aws_tok = _get("http://169.254.169.254/latest/api/token")
    provider = "gcp" if gcp else ("oci" if oci else ("aws" if (aws or aws_tok) else "unknown"))
    if provider == "aws" or (aws and not gcp and not oci):
        raise RuntimeError(f"ABORT non-AWS gate: worker looks like AWS. provider={provider}")
    return {"provider": provider, "gcp_zone_present": bool(gcp), "oci_present": bool(oci)}


def _build_tiny_oracle():
    r = subprocess.run([sys.executable, "/colibri/c/tools/make_glm_oracle.py"],
                       cwd="/colibri/c", stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    tiny = "/colibri/c/glm_tiny"
    ok = Path(tiny).exists() and Path("/colibri/c/ref_glm.json").exists()
    return ok, tiny, r.stderr[-500:] if not ok else ""


def _stage_estate(dest: str) -> dict:
    from huggingface_hub import snapshot_download
    os.makedirs(dest, exist_ok=True)
    free_before = shutil.disk_usage(os.path.dirname(dest)).free / 1e9
    t0 = time.time()
    snapshot_download(repo_id=ESTATE_REPO, local_dir=dest,
                      local_dir_use_symlinks=False, max_workers=8)
    stage_s = time.time() - t0
    lines = []; total = 0
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


def _run_driver(mode, snap, glm_dir, tiny_dir, corpus, out_dir, trace_dir, max_seconds):
    cmd = [sys.executable, "/wave/wave_driver.py", "--mode", mode, "--glm-dir", glm_dir,
           "--snap", snap, "--corpus", corpus, "--smoke-dir", "/smoke", "--atlas-dir", "/wave",
           "--out-dir", out_dir, "--trace-dir", trace_dir,
           "--price-per-hr", str(RATE_PER_HR), "--max-seconds", str(max_seconds)]
    if tiny_dir:
        cmd += ["--tiny-dir", tiny_dir]
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        return json.loads(p.stdout)
    except Exception:
        return {"error": "driver output unparseable", "stdout_tail": p.stdout[-1200:],
                "stderr_tail": p.stderr[-1200:]}


def _finalize(driver_out_dir, trace_dir, corpus_path, subdir):
    """gzip the (big) raw trace + copy compact artifacts to the OUTPUT VOLUME."""
    dest = Path("/out") / subdir
    dest.mkdir(parents=True, exist_ok=True)
    raw = Path(trace_dir) / "rtrace.jsonl"
    gz = dest / "rtrace.jsonl.gz"
    trace_bytes = raw.stat().st_size if raw.exists() else 0
    if raw.exists():
        # shell gzip (fast); keep the raw for the in-run agg already done
        subprocess.run(f"gzip -1 -c {raw} > {gz}", shell=True, check=True)
    for name in ("agg.json", "trace_summary.json", "facts.json", "wave-report.json",
                 "trace_manifest.txt"):
        src = Path(driver_out_dir) / name
        if src.exists():
            shutil.copy(src, dest / name)
    if Path(corpus_path).exists():
        shutil.copy(corpus_path, dest / CORPUS_NAME)
    OUT_VOL.commit()
    return {"volume": OUT_VOLUME_NAME, "subdir": subdir,
            "raw_trace_bytes": trace_bytes,
            "gz_bytes": gz.stat().st_size if gz.exists() else 0,
            "files": sorted(p.name for p in dest.iterdir())}


# --------------------------- FULL Wave-A -----------------------------------
@app.function(image=IMAGE, cloud=WAVE_CLOUD, cpu=CPU_CORES, memory=MEM_MIB,
              ephemeral_disk=EPHEMERAL_GIB * 1024, timeout=TIMEOUT_S,
              volumes={"/out": OUT_VOL})
def wave_a() -> dict:
    started = time.time()
    placement = _assert_non_aws()
    oracle_ok, tiny_dir, oracle_err = _build_tiny_oracle()
    dest = "/ephemeral/glm52_i4"
    os.makedirs("/ephemeral", exist_ok=True)
    stage = _stage_estate(dest)
    if (time.time() - started) / 3600.0 * RATE_PER_HR > STOP_LOSS_USD:
        return {"placement": placement, "stage": stage, "verdict": "ABORT",
                "aborted": "stop-loss $25 reached during staging"}
    os.environ["RAM_GB"] = RAM_GB
    os.environ["CAP_RAISE"] = CAP_RAISE
    # driver wall ceiling = min(20 h cap, remaining $25 budget)
    budget_s = (STOP_LOSS_USD / RATE_PER_HR) * 3600.0
    elapsed = time.time() - started
    max_seconds = int(min(WAVE_WALL_CAP_S, budget_s - elapsed))
    corpus = f"/wave/corpus/{CORPUS_NAME}"
    report = _run_driver("full", dest, "/colibri/c", tiny_dir if oracle_ok else None,
                         corpus, "/tmp/wave-out", "/ephemeral", max_seconds)
    report["placement"] = placement
    report["oracle_built"] = oracle_ok
    report["ram_cap"] = {"RAM_GB": RAM_GB, "CAP_RAISE": CAP_RAISE}
    report["stage"] = stage
    report["outputs"] = _finalize("/tmp/wave-out", "/ephemeral", corpus, "full")
    report["elapsed_hr"] = round((time.time() - started) / 3600.0, 3)
    report["est_cost_usd"] = round(report["elapsed_hr"] * RATE_PER_HR, 2)
    report["over_stop_loss"] = report["est_cost_usd"] > STOP_LOSS_USD
    # trim big fields from the returned dict (full copies are on the Volume)
    for k in ("integrity_errors",):
        if isinstance(report.get(k), list) and len(report[k]) > 5:
            report[k] = report[k][:5] + [f"...(+{len(report[k])-5} more on volume)"]
    return report


# --------------------------- TINY plumbing dry-run -------------------------
@app.function(image=IMAGE, cloud=WAVE_CLOUD, cpu=2.0, memory=8192, timeout=3600,
              volumes={"/out": OUT_VOL})
def wave_a_tiny() -> dict:
    started = time.time()
    placement = _assert_non_aws()
    oracle_ok, tiny, oracle_err = _build_tiny_oracle()
    if not oracle_ok:
        return {"placement": placement, "verdict": "ABORT",
                "note": "tiny oracle build failed", "oracle_stderr": oracle_err}
    corpus = f"/wave/corpus/{CORPUS_NAME}"
    report = _run_driver("tiny", tiny, "/colibri/c", tiny, corpus,
                         "/tmp/wave-tiny", "/tmp/wave-tiny", 3000)
    report["placement"] = placement
    report["outputs"] = _finalize("/tmp/wave-tiny", "/tmp/wave-tiny", corpus, "tiny")
    report["elapsed_hr"] = round((time.time() - started) / 3600.0, 4)
    return report


# --------------------------- entrypoints -----------------------------------
@app.local_entrypoint()
def main():
    out = wave_a.remote()
    print(json.dumps(out, indent=2))
    print("\n==== WAVE-A gonogo:", out.get("trace_summary_gonogo", {}).get("verdict"),
          "· cost≈$", out.get("est_cost_usd"), "· agg:", out.get("agg_meta", {}).get("n_rows"), "rows ====")


@app.local_entrypoint()
def tiny():
    out = wave_a_tiny.remote()
    print(json.dumps(out, indent=2))
    print("\n==== TINY DRY-RUN gonogo:", out.get("trace_summary_gonogo", {}).get("verdict"), "====")


@app.local_entrypoint()
def plan():
    cfg = {"cloud": WAVE_CLOUD, "ephemeral_gib": EPHEMERAL_GIB, "cpu_cores": CPU_CORES,
           "mem_gib": MEM_MIB/1024, "timeout_h": TIMEOUT_S/3600, "gpu": None,
           "stop_loss_usd": STOP_LOSS_USD, "wall_cap_h": WAVE_WALL_CAP_S/3600,
           "ram_gb": RAM_GB, "cap_raise": CAP_RAISE, "estate_repo": ESTATE_REPO,
           "estate_gb": ESTATE_GB, "colibri_commit": COLIBRI_COMMIT,
           "out_volume": OUT_VOLUME_NAME, "uses_volume_for_model": False}
    print(json.dumps(cfg, indent=2))
    assert cfg["cloud"] in ("gcp", "oci"), "cloud must be non-AWS"
    assert cfg["ephemeral_gib"] >= 900, "ephemeral >=900 GiB"
    assert cfg["gpu"] is None, "CPU-only"
    print("\nDRY-PLAN OK: OCI + 900 GiB ephemeral + no-model-Volume + $25 stop-loss + output Volume.")
