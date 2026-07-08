#!/usr/bin/env python3
"""d-xif builder + IF-1 fork pilot on Modal serverless GPU (P10 sections 3-4;
the pre-final-phase instrument measurement for F2 — operational DAG
d-xif < f2.iface < f2.run).

Wraps poc/f2/runner/xif_runner.py (which imports the FROZEN harness's own
extraction/verifier/constrained-surface machinery from f2_runner.py) in the
modal_f2 staging pattern: stage bytes, assert the staged manifest
in-container (fail closed, ERR_STAGING_MISMATCH), run the runner, ship the
output directory back as opaque bytes with sidecar-only provenance.

    .venv/bin/modal run poc/modal/modal_f2_xif.py --mock    # transport smoke
    .venv/bin/modal run poc/modal/modal_f2_xif.py           # real pilot (A10G)

Cost: R1 135M + R2 360M, 650 items x (constrained scoring + 24-token greedy
free decode) per rung — well under 1 GPU-h on A10G (< ~$1.10; inside the
frozen f2 usd_cap $60 / Tier-1 $80 with enormous margin).

Results land in poc/f2/results-incoming/<UTC stamp>-modal-xif/ — NOT
auto-committed. The d-xif corpus under data/d-xif/ is then assembled from
these outputs by a deterministic local step and pinned by ops amendment.
Profile: jmwright-045 (06-resources.md).
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
XIF_RUNNER = F2_DIR / "runner" / "xif_runner.py"
RUNNER_REQS = F2_DIR / "runner" / "requirements.txt"
F2_INPUTS = F2_DIR / "inputs"
F0_DIR = REPO_ROOT / "poc" / "f0"
DQA_DIR = REPO_ROOT / "data" / "d-qa"
KERNEL_DIR = REPO_ROOT / "data" / "kernel-v0"
MOLECULES_DIR = REPO_ROOT / "data" / "molecules-v0"
INCOMING_ROOT = F2_DIR / "results-incoming"

REMOTE_F2 = "/root/kot/poc/f2"
REMOTE_F0 = "/root/kot/poc/f0"
REMOTE_DATA = "/root/kot/data"
REMOTE_OUT = "/tmp/xif-results"
HF_CACHE_MOUNT = "/root/.cache/huggingface"
TIMEOUT_S = 2 * 3600

F0_FILES = ("__init__.py", "flop_meter.py")


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


def _manifest(runner: str, xif_runner: str, reqs: str, inputs_dir: str,
              f0_dir: str, dqa: str, kernel: str, molecules: str) -> dict:
    man = {
        "runner/f2_runner.py": mc.sha256_file(runner),
        "runner/xif_runner.py": mc.sha256_file(xif_runner),
        "runner/requirements.txt": mc.sha256_file(reqs),
    }
    for name in F0_FILES:
        man[f"poc/f0/{name}"] = mc.sha256_file(os.path.join(f0_dir, name))
    _walk_manifest(man, "inputs", inputs_dir)
    _walk_manifest(man, "data/d-qa", dqa)
    _walk_manifest(man, "data/kernel-v0", kernel)
    _walk_manifest(man, "data/molecules-v0", molecules)
    return man


app = modal.App("kot-f2-xif")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(*_image_pins())
    .add_local_python_source("modal_common")
    .add_local_file(RUNNER, f"{REMOTE_F2}/runner/f2_runner.py")
    .add_local_file(XIF_RUNNER, f"{REMOTE_F2}/runner/xif_runner.py")
    .add_local_file(RUNNER_REQS, f"{REMOTE_F2}/runner/requirements.txt")
    .add_local_file(F0_DIR / "__init__.py", f"{REMOTE_F0}/__init__.py")
    .add_local_file(F0_DIR / "flop_meter.py", f"{REMOTE_F0}/flop_meter.py")
    .add_local_dir(F2_INPUTS, remote_path=f"{REMOTE_F2}/inputs")
    .add_local_dir(DQA_DIR, remote_path=f"{REMOTE_DATA}/d-qa")
    .add_local_dir(KERNEL_DIR, remote_path=f"{REMOTE_DATA}/kernel-v0")
    .add_local_dir(MOLECULES_DIR, remote_path=f"{REMOTE_DATA}/molecules-v0")
)

hf_cache = modal.Volume.from_name("kot-hf-cache", create_if_missing=True)


@app.function(image=image, gpu="A10G", volumes={HF_CACHE_MOUNT: hf_cache},
              timeout=TIMEOUT_S)
def run_xif(mock: bool = False, local_manifest: dict = None) -> dict:  # noqa: RUF013
    import subprocess

    import modal_common as cmc

    started = cmc.utcnow_iso()
    staged = _manifest(
        f"{REMOTE_F2}/runner/f2_runner.py",
        f"{REMOTE_F2}/runner/xif_runner.py",
        f"{REMOTE_F2}/runner/requirements.txt",
        f"{REMOTE_F2}/inputs",
        REMOTE_F0,
        f"{REMOTE_DATA}/d-qa",
        f"{REMOTE_DATA}/kernel-v0",
        f"{REMOTE_DATA}/molecules-v0",
    )
    local_manifest = local_manifest or {}
    if staged != local_manifest:
        diff = sorted(
            k for k in set(staged) | set(local_manifest)
            if staged.get(k) != local_manifest.get(k)
        )
        raise SystemExit(f"ERR_STAGING_MISMATCH: staged bytes differ from coordinator: {diff}")

    cmd = [
        sys.executable, f"{REMOTE_F2}/runner/xif_runner.py",
        "--inputs-dir", f"{REMOTE_F2}/inputs",
        "--dqa-dir", f"{REMOTE_DATA}/d-qa",
        "--records-root", "/root/kot",
        "--out-dir", REMOTE_OUT,
        "--device", "cpu" if mock else "cuda",
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
        gpu_requested="A10G",
        gpu_seen=cmc.gpu_info(),
        staged_manifest=staged,
        runner_exit=rc,
        started_utc=started,
        finished_utc=cmc.utcnow_iso(),
        packages=packages,
        environment=cmc.redact_env(dict(os.environ)),
        notes="d-xif / IF-1 pilot (P10) — runner outputs shipped as opaque "
              "bytes; sidecars only (modal_common byte-identity contract)",
    )
    files = cmc.package_results(REMOTE_OUT, run_log=log, rc=rc, provenance=prov)
    try:
        hf_cache.commit()
    except Exception:  # noqa: BLE001
        pass
    return files


def _outcome(results_dir: str) -> str:
    cands = sorted(
        n for n in os.listdir(results_dir)
        if n.startswith("results-xif") and n.endswith(".json")
    )
    if not cands:
        raise SystemExit(f"ERR_NO_RESULTS: no results-xif*.json in {results_dir}")
    with open(os.path.join(results_dir, cands[0])) as f:
        j = json.load(f)
    outcome = j.get("outcome")
    if not outcome:
        raise SystemExit(f"ERR_NO_OUTCOME: {cands[0]} has no 'outcome' field")
    return str(outcome)


@app.local_entrypoint()
def main(mock: bool = False, out_root: str = "") -> None:
    local_manifest = _manifest(str(RUNNER), str(XIF_RUNNER), str(RUNNER_REQS),
                               str(F2_INPUTS), str(F0_DIR), str(DQA_DIR),
                               str(KERNEL_DIR), str(MOLECULES_DIR))
    print(f"kot-f2-xif via Modal: gpu=A10G mock={mock} "
          f"({len(local_manifest)} staged files, xif_runner "
          f"{local_manifest['runner/xif_runner.py'][:12]}…)")

    files = run_xif.remote(mock=mock, local_manifest=local_manifest)

    stamp = time.strftime("%Y%m%d-%H%M%S", time.gmtime()) + "-modal-xif"
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
        raise SystemExit(f"ERR_RUNNER: xif_runner exited rc={rc} (partials + logs saved in {dest})")
    print("done — assemble data/d-xif/ deliberately (results are NOT auto-committed)")
