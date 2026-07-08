#!/usr/bin/env python3
"""F2 verifier-offload pivot on Modal serverless GPU (Tier-1; registry record
registry/experiments/f2.json, FROZEN).

Wraps poc/f2/runner/f2_runner.py UNCHANGED (modal_e2/e5/e9 pattern): stages
bytes, asserts the staged manifest in-container (fail closed,
ERR_STAGING_MISMATCH), runs the runner, ships its output directory back as
opaque bytes with sidecar-only provenance. The staged-bytes manifest printed
at launch is the value the frozen record's pins.harness_manifest
("PINNED-AT-INPUTS:f2.inputs") must be resolved to by ops amendment BEFORE
any final-phase run.

    .venv/bin/modal run poc/modal/modal_f2.py --mock       # transport smoke, ~pennies
    .venv/bin/modal run poc/modal/modal_f2.py              # full pre-registered F2 (A10G)
    .venv/bin/modal run poc/modal/modal_f2.py --gpu t4     # T4 flavour

LAUNCH GATES (do NOT run the full path until ALL hold):
  1. d-xif labelled extraction set built + pinned (P10; runner fails closed);
  2. d-ext external eval slice built + pinned (RT-7a; else the frozen
     external-slice secondary is unresolvable and verdict-gen fails closed);
  3. R3 (SmolLM2-1.7B) + PRM revisions pinned by ops amendment;
  4. harness_manifest ops amendment written from this file's printed manifest;
  5. maintainer Tier-1 go (P1 section 5; cap $80, registry usd_cap $60).

Results land in poc/f2/results-incoming/<UTC stamp>-modal/ — NOT
auto-committed. Budget (from --dry-plan, A10G): point ~$4, worst ~$8,
hard ceiling $26.40 (24 GPU-h cap x $1.10/h) — inside every cap.
Profile: jmwright-045 (06-resources.md); 4 h function timeout.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import modal

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
import modal_common as mc  # noqa: E402

try:
    REPO_ROOT = _HERE.parents[1]
except IndexError:
    REPO_ROOT = _HERE  # container: local-path constants never dereferenced
F2_DIR = REPO_ROOT / "poc" / "f2"
RUNNER = F2_DIR / "runner" / "f2_runner.py"
RUNNER_REQS = F2_DIR / "runner" / "requirements.txt"
F2_INPUTS = F2_DIR / "inputs"
DQA_DIR = REPO_ROOT / "data" / "d-qa"
KERNEL_DIR = REPO_ROOT / "data" / "kernel-v0"
MOLECULES_DIR = REPO_ROOT / "data" / "molecules-v0"
INCOMING_ROOT = F2_DIR / "results-incoming"

REMOTE_F2 = "/root/kot/poc/f2"
REMOTE_DATA = "/root/kot/data"
REMOTE_OUT = "/tmp/f2-results"
HF_CACHE_MOUNT = "/root/.cache/huggingface"
TIMEOUT_S = 4 * 3600
GPU_CHOICES = ("T4", "A10G")


def _image_pins() -> list:
    p = _HERE / "requirements-image.txt"
    if not p.exists():
        return []
    lines = p.read_text().splitlines()
    return [ln.strip() for ln in lines if ln.strip() and not ln.strip().startswith("#")]


def _walk_manifest(man: dict, prefix: str, base: str) -> None:
    for root, _dirs, files in os.walk(base):
        for name in sorted(files):
            p = os.path.join(root, name)
            rel = os.path.relpath(p, base).replace(os.sep, "/")
            man[f"{prefix}/{rel}"] = mc.sha256_file(p)


def _manifest(runner: str, reqs: str, inputs_dir: str, dqa: str,
              kernel: str, molecules: str) -> dict:
    man = {
        "runner/f2_runner.py": mc.sha256_file(runner),
        "runner/requirements.txt": mc.sha256_file(reqs),
    }
    _walk_manifest(man, "inputs", inputs_dir)
    _walk_manifest(man, "data/d-qa", dqa)
    _walk_manifest(man, "data/kernel-v0", kernel)
    _walk_manifest(man, "data/molecules-v0", molecules)
    return man


def _outcome(results_dir: str) -> str:
    cands = sorted(
        n for n in os.listdir(results_dir) if n.startswith("results-f2") and n.endswith(".json")
    )
    if "results-f2.json" in cands:
        cands = ["results-f2.json"] + [c for c in cands if c != "results-f2.json"]
    if not cands:
        raise SystemExit(f"ERR_NO_RESULTS: no results-f2*.json in {results_dir}")
    with open(os.path.join(results_dir, cands[0])) as f:
        j = json.load(f)
    outcome = j.get("outcome")
    if not outcome:
        raise SystemExit(f"ERR_NO_OUTCOME: {cands[0]} has no 'outcome' field")
    return str(outcome)


app = modal.App("kot-f2")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(*_image_pins())
    .add_local_python_source("modal_common")
    .add_local_file(RUNNER, f"{REMOTE_F2}/runner/f2_runner.py")
    .add_local_file(RUNNER_REQS, f"{REMOTE_F2}/runner/requirements.txt")
    .add_local_dir(F2_INPUTS, remote_path=f"{REMOTE_F2}/inputs")
    .add_local_dir(DQA_DIR, remote_path=f"{REMOTE_DATA}/d-qa")
    .add_local_dir(KERNEL_DIR, remote_path=f"{REMOTE_DATA}/kernel-v0")
    .add_local_dir(MOLECULES_DIR, remote_path=f"{REMOTE_DATA}/molecules-v0")
)

hf_cache = modal.Volume.from_name("kot-hf-cache", create_if_missing=True)


def _run_in_container(gpu_requested: str, mock: bool, local_manifest: dict) -> dict:
    import subprocess

    import modal_common as cmc

    started = cmc.utcnow_iso()
    staged = _manifest(
        f"{REMOTE_F2}/runner/f2_runner.py",
        f"{REMOTE_F2}/runner/requirements.txt",
        f"{REMOTE_F2}/inputs",
        f"{REMOTE_DATA}/d-qa",
        f"{REMOTE_DATA}/kernel-v0",
        f"{REMOTE_DATA}/molecules-v0",
    )
    if staged != local_manifest:
        diff = sorted(
            k for k in set(staged) | set(local_manifest)
            if staged.get(k) != local_manifest.get(k)
        )
        raise SystemExit(f"ERR_STAGING_MISMATCH: staged bytes differ from coordinator: {diff}")

    # f2_runner has its own CLI shape (dqa/records-root flags), so invoke it
    # directly here instead of through mc.run_runner's fixed e2-style CLI.
    cmd = [
        sys.executable, f"{REMOTE_F2}/runner/f2_runner.py",
        "--inputs-dir", f"{REMOTE_F2}/inputs",
        "--dqa-dir", f"{REMOTE_DATA}/d-qa",
        "--records-root", "/root/kot",
        "--out-dir", REMOTE_OUT,
        "--device", "cpu" if mock else "cuda",
        "--gpu-class", gpu_requested,
    ]
    if mock:
        cmd.append("--mock")
    os.makedirs(REMOTE_OUT, exist_ok=True)
    lines = [f"$ {' '.join(cmd)}\n"]
    with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                          text=True, bufsize=1) as proc:
        assert proc.stdout is not None
        for line in proc.stdout:
            lines.append(line)
            sys.stdout.write(line)
            sys.stdout.flush()
    rc = proc.returncode
    lines.append(f"[runner exit rc={rc}]\n")
    log = "".join(lines)

    packages = {}
    for name in ("numpy", "torch", "transformers"):
        try:
            packages[name] = __import__(name).__version__
        except Exception as e:  # noqa: BLE001
            packages[name] = f"unavailable: {e}"

    prov = cmc.build_provenance(
        transport="modal",
        gpu_requested=gpu_requested,
        gpu_seen=cmc.gpu_info(),
        staged_manifest=staged,
        runner_exit=rc,
        started_utc=started,
        finished_utc=cmc.utcnow_iso(),
        packages=packages,
        environment=cmc.redact_env(dict(os.environ)),
        notes="runner outputs shipped as opaque bytes; sidecars only — "
              "see poc/modal/modal_common.py byte-identity contract",
    )
    files = cmc.package_results(REMOTE_OUT, run_log=log, rc=rc, provenance=prov)
    try:
        hf_cache.commit()
    except Exception:  # noqa: BLE001
        pass
    return files


@app.function(image=image, gpu="T4", volumes={HF_CACHE_MOUNT: hf_cache}, timeout=TIMEOUT_S)
def run_f2_t4(mock: bool = False, local_manifest: dict = None) -> dict:  # noqa: RUF013
    return _run_in_container("T4", mock, local_manifest or {})


@app.function(image=image, gpu="A10G", volumes={HF_CACHE_MOUNT: hf_cache}, timeout=TIMEOUT_S)
def run_f2_a10g(mock: bool = False, local_manifest: dict = None) -> dict:  # noqa: RUF013
    return _run_in_container("A10G", mock, local_manifest or {})


GPU_FUNCTIONS = {"T4": run_f2_t4, "A10G": run_f2_a10g}


@app.local_entrypoint()
def main(gpu: str = "A10G", mock: bool = False, out_root: str = "") -> None:
    gpu = gpu.upper()
    if gpu not in GPU_FUNCTIONS:
        raise SystemExit(f"ERR_GPU: --gpu must be one of {GPU_CHOICES}, got {gpu!r}")

    local_manifest = _manifest(str(RUNNER), str(RUNNER_REQS), str(F2_INPUTS),
                               str(DQA_DIR), str(KERNEL_DIR), str(MOLECULES_DIR))
    print(f"kot-f2 via Modal: gpu={gpu} mock={mock} "
          f"({len(local_manifest)} staged files, runner "
          f"{local_manifest['runner/f2_runner.py'][:12]}…)")
    if not mock:
        print("REMINDER: final-phase launch gates (module docstring) must ALL "
              "hold; the runner fails closed on missing d-xif / unpinned models.")

    files = GPU_FUNCTIONS[gpu].remote(mock=mock, local_manifest=local_manifest)

    stamp = time.strftime("%Y%m%d-%H%M%S", time.gmtime()) + "-modal"
    dest = Path(out_root) / stamp if out_root else INCOMING_ROOT / stamp
    mc.unpack_files(files, str(dest))

    prov_path = dest / mc.PROVENANCE_NAME
    prov = json.loads(prov_path.read_text())
    try:
        image_id = image.object_id
    except Exception:  # noqa: BLE001
        image_id = None
    prov["coordinator"] = {
        "modal_client": modal.__version__,
        "image_object_id": image_id,
        "local_manifest_matched": True,
        "collected_utc": mc.utcnow_iso(),
    }
    prov_path.write_text(json.dumps(prov, indent=2, sort_keys=True) + "\n")

    outcome = _outcome(str(dest))
    rc = int((dest / mc.RUNNER_EXIT_NAME).read_text().strip().split("=", 1)[1])
    print(f"\nwrote {len(files)} files to {dest}")
    print(f"OUTCOME: {outcome}")
    if rc != 0:
        raise SystemExit(f"ERR_RUNNER: f2_runner exited rc={rc} (partials + logs saved in {dest})")
    print("done — review and commit deliberately (results are NOT auto-committed)")
