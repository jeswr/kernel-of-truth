#!/usr/bin/env python3
"""E5 adapter + shuffled-kernel control on Modal serverless GPU (bead
kernel-of-truth-c24).

Wraps poc/e5/runner/e5_runner.py UNCHANGED — no forked analysis logic
(modal_e2.py pattern). Same runner bytes + same input bytes as any future AWS
path, enforced by a sha256 staged-manifest assertion inside the container
(fail closed, ERR_STAGING_MISMATCH); runner outputs ship back as opaque
bytes with sidecar-only transport provenance (modal_common contract).

    .venv/bin/modal run poc/modal/modal_e5.py --mock       # transport smoke, ~pennies
    .venv/bin/modal run poc/modal/modal_e5.py              # full pre-registered E5 (A10G)
    .venv/bin/modal run poc/modal/modal_e5.py --gpu t4     # T4 flavour (fp32, ~3x slower — timeout risk)

Results land in poc/e5/results-incoming/<UTC stamp>-modal/ — NOT
auto-committed; reviewed and committed deliberately. SmolLM2-135M weights
persist in the shared Volume `kot-hf-cache` (already warm from E2).

Budget: ~2-2.5 A10G-h expected (~$2.5-3); 4 h hard timeout caps the worst
case at ~$4.4 — inside the authorized <= $8 (poc/e5/README.md).
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
import modal_common as mc  # noqa: E402  (stdlib-only; shipped into the image below)

# ---- local (coordinator-side) paths ----------------------------------------
try:
    REPO_ROOT = _HERE.parents[1]
except IndexError:
    REPO_ROOT = _HERE  # container: local-path constants are never dereferenced
E5_DIR = REPO_ROOT / "poc" / "e5"
RUNNER = E5_DIR / "runner" / "e5_runner.py"
RUNNER_REQS = E5_DIR / "runner" / "requirements.txt"
INPUTS_DIR = E5_DIR / "inputs"
INCOMING_ROOT = E5_DIR / "results-incoming"

# ---- container-side layout ---------------------------------------------------
REMOTE_E5 = "/root/kot/poc/e5"
REMOTE_OUT = "/tmp/e5-results"
HF_CACHE_MOUNT = "/root/.cache/huggingface"
TIMEOUT_S = 4 * 3600                     # hard budget cap (README cost guard)
GPU_CHOICES = ("T4", "A10G")             # A10G default: fp32 training, T4 ~3x slower


def _image_pins() -> list:
    p = _HERE / "requirements-image.txt"
    if not p.exists():  # container-side re-import: the image is already built
        return []
    lines = p.read_text().splitlines()
    return [ln.strip() for ln in lines if ln.strip() and not ln.strip().startswith("#")]


def _manifest() -> dict:
    """sha256 manifest over the exact bytes the runner consumes — RECURSIVE
    over inputs/ (E5 ships vectors/*.f32 in a subdirectory, unlike E2)."""
    man = {
        "runner/e5_runner.py": mc.sha256_file(str(RUNNER)),
        "runner/requirements.txt": mc.sha256_file(str(RUNNER_REQS)),
    }
    base = str(INPUTS_DIR)
    for root, _dirs, files in os.walk(base):
        for name in sorted(files):
            p = os.path.join(root, name)
            rel = os.path.relpath(p, base).replace(os.sep, "/")
            man[f"inputs/{rel}"] = mc.sha256_file(p)
    return man


def _manifest_container(inputs_dir: str, runner_py: str, reqs: str) -> dict:
    import modal_common as cmc

    man = {
        "runner/e5_runner.py": cmc.sha256_file(runner_py),
        "runner/requirements.txt": cmc.sha256_file(reqs),
    }
    for root, _dirs, files in os.walk(inputs_dir):
        for name in sorted(files):
            p = os.path.join(root, name)
            rel = os.path.relpath(p, inputs_dir).replace(os.sep, "/")
            man[f"inputs/{rel}"] = cmc.sha256_file(p)
    return man


def _outcome(results_dir: str) -> str:
    """results-e5*.json OUTCOME echo (mc.verdict_outcome is E2-named)."""
    cands = sorted(
        n for n in os.listdir(results_dir) if n.startswith("results-e5") and n.endswith(".json")
    )
    if "results-e5.json" in cands:
        cands = ["results-e5.json"] + [c for c in cands if c != "results-e5.json"]
    if not cands:
        raise SystemExit(f"ERR_NO_RESULTS: no results-e5*.json in {results_dir}")
    with open(os.path.join(results_dir, cands[0])) as f:
        j = json.load(f)
    outcome = j.get("outcome")
    if not outcome:
        raise SystemExit(f"ERR_NO_OUTCOME: {cands[0]} has no 'outcome' field")
    return str(outcome)


app = modal.App("kot-e5")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(*_image_pins())
    .add_local_python_source("modal_common")
    .add_local_file(RUNNER, f"{REMOTE_E5}/runner/e5_runner.py")
    .add_local_file(RUNNER_REQS, f"{REMOTE_E5}/runner/requirements.txt")
    .add_local_dir(INPUTS_DIR, remote_path=f"{REMOTE_E5}/inputs")
)

hf_cache = modal.Volume.from_name("kot-hf-cache", create_if_missing=True)


def _run_in_container(gpu_requested: str, mock: bool, local_manifest: dict) -> dict:
    import modal_common as cmc

    started = cmc.utcnow_iso()
    staged = _manifest_container(
        f"{REMOTE_E5}/inputs",
        f"{REMOTE_E5}/runner/e5_runner.py",
        f"{REMOTE_E5}/runner/requirements.txt",
    )
    if staged != local_manifest:
        diff = sorted(
            k for k in set(staged) | set(local_manifest)
            if staged.get(k) != local_manifest.get(k)
        )
        raise SystemExit(f"ERR_STAGING_MISMATCH: staged bytes differ from coordinator: {diff}")

    rc, log = cmc.run_runner(
        sys.executable,
        f"{REMOTE_E5}/runner/e5_runner.py",
        f"{REMOTE_E5}/inputs",
        REMOTE_OUT,
        device="cuda",
        mock=mock,
    )

    packages = {}
    for name in ("numpy", "torch", "transformers"):
        try:
            packages[name] = __import__(name).__version__
        except Exception as e:  # provenance must never kill a finished run
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
def run_e5_t4(mock: bool = False, local_manifest: dict = None) -> dict:  # noqa: RUF013
    return _run_in_container("T4", mock, local_manifest or {})


@app.function(image=image, gpu="A10G", volumes={HF_CACHE_MOUNT: hf_cache}, timeout=TIMEOUT_S)
def run_e5_a10g(mock: bool = False, local_manifest: dict = None) -> dict:  # noqa: RUF013
    return _run_in_container("A10G", mock, local_manifest or {})


GPU_FUNCTIONS = {"T4": run_e5_t4, "A10G": run_e5_a10g}


@app.local_entrypoint()
def main(gpu: str = "A10G", mock: bool = False, out_root: str = "") -> None:
    gpu = gpu.upper()
    if gpu not in GPU_FUNCTIONS:
        raise SystemExit(f"ERR_GPU: --gpu must be one of {GPU_CHOICES}, got {gpu!r}")

    local_manifest = _manifest()
    print(f"kot-e5 via Modal: gpu={gpu} mock={mock} "
          f"({len(local_manifest)} staged files, runner "
          f"{local_manifest['runner/e5_runner.py'][:12]}…)")

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
        "local_manifest_matched": True,  # container failed closed otherwise
        "collected_utc": mc.utcnow_iso(),
    }
    prov_path.write_text(json.dumps(prov, indent=2, sort_keys=True) + "\n")

    outcome = _outcome(str(dest))
    rc = int((dest / mc.RUNNER_EXIT_NAME).read_text().strip().split("=", 1)[1])
    print(f"\nwrote {len(files)} files to {dest}")
    print(f"OUTCOME: {outcome}")
    if rc != 0:
        raise SystemExit(f"ERR_RUNNER: e5_runner exited rc={rc} (partials + logs saved in {dest})")
    print("done — review and commit deliberately (results are NOT auto-committed)")
