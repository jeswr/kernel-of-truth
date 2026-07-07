#!/usr/bin/env python3
"""E2 geometry-alignment probe on Modal serverless GPU (bead kernel-of-truth-0oj).

Wraps poc/e2/runner/e2_runner.py UNCHANGED — no forked analysis logic. Same
runner bytes + same input bytes as the AWS path (poc/gpu), enforced by a
sha256 staged-manifest assertion inside the container, so results-e2.json /
verdict-e2.md round-trip byte-identical across transports (the runner's own
`date` field is the only per-invocation difference, on any transport).

    .venv/bin/modal run poc/modal/modal_e2.py --mock       # transport smoke, ~pennies
    .venv/bin/modal run poc/modal/modal_e2.py              # full pre-registered E2, T4
    .venv/bin/modal run poc/modal/modal_e2.py --gpu a10g   # optional faster GPU

Needs a one-time `modal token new` pairing (poc/modal/README.md); no AWS
quota, per-second billing, 4 h hard timeout mirroring the AWS failsafe.
Results land in poc/e2/results-incoming/<UTC stamp>-modal/ — the same
convention as poc/gpu/collect-e2.sh, `-modal` suffixed. NOT auto-committed:
the coordinator reviews and commits deliberately, exactly like the AWS path.

HF model downloads persist in Modal Volume `kot-hf-cache`, so repeat runs
skip the download (the AWS path re-downloads on every ephemeral box).
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
# In the container Modal mounts this file at /root, which has no second parent;
# only the REMOTE_* constants are dereferenced there, so import must not crash.
try:
    REPO_ROOT = _HERE.parents[1]
except IndexError:
    REPO_ROOT = _HERE  # container: local-path constants are never dereferenced
E2_DIR = REPO_ROOT / "poc" / "e2"
RUNNER = E2_DIR / "runner" / "e2_runner.py"
RUNNER_REQS = E2_DIR / "runner" / "requirements.txt"
INPUTS_DIR = E2_DIR / "inputs"
INCOMING_ROOT = E2_DIR / "results-incoming"

# ---- container-side layout ---------------------------------------------------
REMOTE_E2 = "/root/kot/poc/e2"           # mirrors the AWS clone at /opt/kot
REMOTE_OUT = "/tmp/e2-results"           # container-local; shipped back as bytes
HF_CACHE_MOUNT = "/root/.cache/huggingface"
TIMEOUT_S = 4 * 3600                     # parity with the AWS 4 h failsafe poweroff
GPU_CHOICES = ("T4", "A10G")             # T4 default; A10G optional (--gpu a10g)


def _image_pins() -> list:
    p = _HERE / "requirements-image.txt"
    if not p.exists():  # container-side re-import: the image is already built,
        return []       # only the coordinator needs the pins (kernel-of-truth-af7 fix)
    lines = p.read_text().splitlines()
    return [ln.strip() for ln in lines if ln.strip() and not ln.strip().startswith("#")]


app = modal.App("kot-e2")

# Pinned image: exact pip pins (requirements-image.txt) on a pinned python.
# add_local_* layers are attached at container start (copy=False), so editing
# runner/inputs does NOT invalidate the cached pip layer; content integrity is
# guaranteed by the manifest assertion, not by image rebuilds.
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(*_image_pins())
    .add_local_python_source("modal_common")
    .add_local_file(RUNNER, f"{REMOTE_E2}/runner/e2_runner.py")
    .add_local_file(RUNNER_REQS, f"{REMOTE_E2}/runner/requirements.txt")
    .add_local_dir(INPUTS_DIR, remote_path=f"{REMOTE_E2}/inputs")
)

hf_cache = modal.Volume.from_name("kot-hf-cache", create_if_missing=True)


def _run_in_container(gpu_requested: str, mock: bool, local_manifest: dict) -> dict:
    """Container body: assert staging, run the unchanged runner, package bytes."""
    import modal_common as cmc  # container-side import (add_local_python_source)

    started = cmc.utcnow_iso()
    staged = cmc.input_manifest(
        f"{REMOTE_E2}/runner/e2_runner.py",
        f"{REMOTE_E2}/runner/requirements.txt",
        f"{REMOTE_E2}/inputs",
    )
    if staged != local_manifest:
        diff = sorted(
            k for k in set(staged) | set(local_manifest)
            if staged.get(k) != local_manifest.get(k)
        )
        raise SystemExit(f"ERR_STAGING_MISMATCH: staged bytes differ from coordinator: {diff}")

    rc, log = cmc.run_runner(
        sys.executable,
        f"{REMOTE_E2}/runner/e2_runner.py",
        f"{REMOTE_E2}/inputs",
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
    try:  # persist any new HF downloads for the next run
        hf_cache.commit()
    except Exception:
        pass
    # Like the AWS path, a failed run still returns its partials + logs + rc
    # (diagnosable trace); the local entrypoint exits non-zero on rc != 0.
    return files


@app.function(image=image, gpu="T4", volumes={HF_CACHE_MOUNT: hf_cache}, timeout=TIMEOUT_S)
def run_e2_t4(mock: bool = False, local_manifest: dict = None) -> dict:  # noqa: RUF013
    return _run_in_container("T4", mock, local_manifest or {})


@app.function(image=image, gpu="A10G", volumes={HF_CACHE_MOUNT: hf_cache}, timeout=TIMEOUT_S)
def run_e2_a10g(mock: bool = False, local_manifest: dict = None) -> dict:  # noqa: RUF013
    return _run_in_container("A10G", mock, local_manifest or {})


GPU_FUNCTIONS = {"T4": run_e2_t4, "A10G": run_e2_a10g}


@app.local_entrypoint()
def main(gpu: str = "T4", mock: bool = False, out_root: str = "") -> None:
    gpu = gpu.upper()
    if gpu not in GPU_FUNCTIONS:
        raise SystemExit(f"ERR_GPU: --gpu must be one of {GPU_CHOICES}, got {gpu!r}")

    local_manifest = mc.input_manifest(str(RUNNER), str(RUNNER_REQS), str(INPUTS_DIR))
    print(f"kot-e2 via Modal: gpu={gpu} mock={mock} "
          f"({len(local_manifest)} staged files, runner "
          f"{local_manifest['runner/e2_runner.py'][:12]}…)")

    files = GPU_FUNCTIONS[gpu].remote(mock=mock, local_manifest=local_manifest)

    stamp = time.strftime("%Y%m%d-%H%M%S", time.gmtime()) + "-modal"
    dest = Path(out_root) / stamp if out_root else INCOMING_ROOT / stamp
    mc.unpack_files(files, str(dest))

    # Merge coordinator-side provenance into the sidecar (image digest becomes
    # known here once the app has hydrated it; never any token material).
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

    # collect-e2.sh parity: verify the results JSON parses + echo OUTCOME.
    outcome = mc.verdict_outcome(str(dest))
    rc = int((dest / mc.RUNNER_EXIT_NAME).read_text().strip().split("=", 1)[1])
    print(f"\nwrote {len(files)} files to {dest}")
    print(f"OUTCOME: {outcome}")
    if rc != 0:
        raise SystemExit(f"ERR_RUNNER: e2_runner exited rc={rc} (partials + logs saved in {dest})")
    print("done — review and commit deliberately (results are NOT auto-committed)")
