#!/usr/bin/env python3
"""E9-defl deflationary control kernel on Modal serverless GPU (bead
kernel-of-truth-xj2).

Wraps poc/e9/runner/e9_runner.py UNCHANGED (modal_e2/modal_e5 pattern), which
itself imports poc/e5/runner/e5_runner.py READ-ONLY — so BOTH runners and
BOTH input trees are staged and sha-asserted in-container (fail closed,
ERR_STAGING_MISMATCH). Results ship back as opaque bytes with sidecar-only
provenance.

    .venv/bin/modal run poc/modal/modal_e9.py --mock       # transport smoke, ~pennies
    .venv/bin/modal run poc/modal/modal_e9.py              # full pre-registered E9-defl (A10G)
    .venv/bin/modal run poc/modal/modal_e9.py --gpu t4     # T4 flavour (fp32, ~3x slower)

Results land in poc/e9/results-incoming/<UTC stamp>-modal/ — NOT
auto-committed. Budget: ~1.7-1.9 A10G-h (~$2, same shape as E5's measured
1.74 h); 4 h hard timeout (~$4.4 worst case) — inside the <=$5 auto-proceed
envelope (poc/e9/README.md).
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
E9_DIR = REPO_ROOT / "poc" / "e9"
E5_DIR = REPO_ROOT / "poc" / "e5"
RUNNER = E9_DIR / "runner" / "e9_runner.py"
RUNNER_REQS = E9_DIR / "runner" / "requirements.txt"
E5_RUNNER = E5_DIR / "runner" / "e5_runner.py"
E9_INPUTS = E9_DIR / "inputs"
E5_INPUTS = E5_DIR / "inputs"
INCOMING_ROOT = E9_DIR / "results-incoming"

REMOTE_E9 = "/root/kot/poc/e9"
REMOTE_E5 = "/root/kot/poc/e5"
REMOTE_OUT = "/tmp/e9-results"
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


def _manifest(e9_runner: str, reqs: str, e5_runner: str, e9_inputs: str, e5_inputs: str) -> dict:
    man = {
        "runner/e9_runner.py": mc.sha256_file(e9_runner),
        "runner/requirements.txt": mc.sha256_file(reqs),
        "e5runner/e5_runner.py": mc.sha256_file(e5_runner),
    }
    _walk_manifest(man, "e9inputs", e9_inputs)
    _walk_manifest(man, "e5inputs", e5_inputs)
    return man


def _outcome(results_dir: str) -> str:
    cands = sorted(
        n for n in os.listdir(results_dir) if n.startswith("results-e9") and n.endswith(".json")
    )
    if "results-e9.json" in cands:
        cands = ["results-e9.json"] + [c for c in cands if c != "results-e9.json"]
    if not cands:
        raise SystemExit(f"ERR_NO_RESULTS: no results-e9*.json in {results_dir}")
    with open(os.path.join(results_dir, cands[0])) as f:
        j = json.load(f)
    outcome = j.get("outcome")
    if not outcome:
        raise SystemExit(f"ERR_NO_OUTCOME: {cands[0]} has no 'outcome' field")
    return str(outcome)


app = modal.App("kot-e9")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(*_image_pins())
    .add_local_python_source("modal_common")
    .add_local_file(RUNNER, f"{REMOTE_E9}/runner/e9_runner.py")
    .add_local_file(RUNNER_REQS, f"{REMOTE_E9}/runner/requirements.txt")
    .add_local_file(E5_RUNNER, f"{REMOTE_E5}/runner/e5_runner.py")
    .add_local_dir(E9_INPUTS, remote_path=f"{REMOTE_E9}/inputs")
    .add_local_dir(E5_INPUTS, remote_path=f"{REMOTE_E5}/inputs")
)

hf_cache = modal.Volume.from_name("kot-hf-cache", create_if_missing=True)


def _run_in_container(gpu_requested: str, mock: bool, local_manifest: dict) -> dict:
    import modal_common as cmc

    started = cmc.utcnow_iso()
    staged = _manifest(
        f"{REMOTE_E9}/runner/e9_runner.py",
        f"{REMOTE_E9}/runner/requirements.txt",
        f"{REMOTE_E5}/runner/e5_runner.py",
        f"{REMOTE_E9}/inputs",
        f"{REMOTE_E5}/inputs",
    )
    if staged != local_manifest:
        diff = sorted(
            k for k in set(staged) | set(local_manifest)
            if staged.get(k) != local_manifest.get(k)
        )
        raise SystemExit(f"ERR_STAGING_MISMATCH: staged bytes differ from coordinator: {diff}")

    # e9_runner's --e5-inputs-dir default resolves to /root/kot/poc/e5/inputs
    # from the staged layout, so mc.run_runner's fixed CLI works unchanged.
    rc, log = cmc.run_runner(
        sys.executable,
        f"{REMOTE_E9}/runner/e9_runner.py",
        f"{REMOTE_E9}/inputs",
        REMOTE_OUT,
        device="cuda",
        mock=mock,
    )

    packages = {}
    for name in ("numpy", "torch", "transformers"):
        try:
            packages[name] = __import__(name).__version__
        except Exception as e:
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
    except Exception:
        pass
    return files


@app.function(image=image, gpu="T4", volumes={HF_CACHE_MOUNT: hf_cache}, timeout=TIMEOUT_S)
def run_e9_t4(mock: bool = False, local_manifest: dict = None) -> dict:  # noqa: RUF013
    return _run_in_container("T4", mock, local_manifest or {})


@app.function(image=image, gpu="A10G", volumes={HF_CACHE_MOUNT: hf_cache}, timeout=TIMEOUT_S)
def run_e9_a10g(mock: bool = False, local_manifest: dict = None) -> dict:  # noqa: RUF013
    return _run_in_container("A10G", mock, local_manifest or {})


GPU_FUNCTIONS = {"T4": run_e9_t4, "A10G": run_e9_a10g}


@app.local_entrypoint()
def main(gpu: str = "A10G", mock: bool = False, out_root: str = "") -> None:
    gpu = gpu.upper()
    if gpu not in GPU_FUNCTIONS:
        raise SystemExit(f"ERR_GPU: --gpu must be one of {GPU_CHOICES}, got {gpu!r}")

    local_manifest = _manifest(str(RUNNER), str(RUNNER_REQS), str(E5_RUNNER),
                               str(E9_INPUTS), str(E5_INPUTS))
    print(f"kot-e9 via Modal: gpu={gpu} mock={mock} "
          f"({len(local_manifest)} staged files, runner "
          f"{local_manifest['runner/e9_runner.py'][:12]}…)")

    files = GPU_FUNCTIONS[gpu].remote(mock=mock, local_manifest=local_manifest)

    stamp = time.strftime("%Y%m%d-%H%M%S", time.gmtime()) + "-modal"
    dest = Path(out_root) / stamp if out_root else INCOMING_ROOT / stamp
    mc.unpack_files(files, str(dest))

    prov_path = dest / mc.PROVENANCE_NAME
    prov = json.loads(prov_path.read_text())
    try:
        image_id = image.object_id
    except Exception:
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
        raise SystemExit(f"ERR_RUNNER: e9_runner exited rc={rc} (partials + logs saved in {dest})")
    print("done — review and commit deliberately (results are NOT auto-committed)")
