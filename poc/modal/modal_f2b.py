#!/usr/bin/env python3
"""f2b-replicate on Modal serverless GPU (Tier-1; registry record
registry/experiments/f2b-replicate.json).

Wraps poc/f2b/runner/f2b_runner.py UNCHANGED (modal_f2 pattern): stages
bytes, asserts the staged manifest in-container (fail closed,
ERR_STAGING_MISMATCH), runs the runner, ships its output directory back as
opaque bytes with sidecar-only provenance.

PINNING DIRECTION (differs from F2): the frozen record pins
pins.harness_manifest to this file's staged-bytes manifest sha DIRECTLY at
freeze time (no PINNED-AT-INPUTS placeholder). The launch reprints the sha;
a run is valid only if the printed value equals the frozen pin — ANY change
to a staged byte after the freeze requires a correction record BEFORE any
final-phase run.

    .venv/bin/modal run poc/modal/modal_f2b.py --gpu a100 --dry-plan  # cost plan, $0, local
    .venv/bin/modal run poc/modal/modal_f2b.py --mock                 # transport smoke, ~pennies
    .venv/bin/modal run poc/modal/modal_f2b.py --gpu a100             # RIGHT-SIZED run (single A100-40GB)
    .venv/bin/modal run poc/modal/modal_f2b.py --gpu t4               # T4 flavour

LAUNCH GATES (do NOT run the full path until ALL hold):
  1. registry/experiments/f2b-replicate.json FROZEN and the printed
     harness-manifest sha equals its pins.harness_manifest;
  2. maintainer Tier-1 go (P1 section 5; usd_cap $60, Tier-1 cap $80).

Results land in poc/f2b/results-incoming/<UTC stamp>-modal/ — NOT
auto-committed. Budget (from --dry-plan, A10G): see the runner's printout;
the advisor estimate is ~$8-15 and the shuffled arm is the one cost NOT to
cut. Profile: jmwright-045 (06-resources.md); 12 h function timeout.
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
F2B_DIR = REPO_ROOT / "poc" / "f2b"
RUNNER = F2B_DIR / "runner" / "f2b_runner.py"
RUNNER_REQS = F2B_DIR / "runner" / "requirements.txt"
F2B_INPUTS = F2B_DIR / "inputs"
F0_DIR = REPO_ROOT / "poc" / "f0"
DQA_DIR = REPO_ROOT / "data" / "d-qa"
DQAR_DIR = REPO_ROOT / "data" / "d-qa-r"
DXIF_DIR = REPO_ROOT / "data" / "d-xif"
DEXT_DIR = REPO_ROOT / "data" / "d-ext"
KERNEL_DIR = REPO_ROOT / "data" / "kernel-v0"
MOLECULES_DIR = REPO_ROOT / "data" / "molecules-v0"
INCOMING_ROOT = F2B_DIR / "results-incoming"

REMOTE_F2B = "/root/kot/poc/f2b"
REMOTE_F0 = "/root/kot/poc/f0"
REMOTE_DATA = "/root/kot/data"
REMOTE_OUT = "/tmp/f2b-results"
HF_CACHE_MOUNT = "/root/.cache/huggingface"
TIMEOUT_S = 12 * 3600  # dry-plan worst case is far below; results ship at exit
GPU_CHOICES = ("T4", "A10G", "A100")


def _image_pins() -> list:
    p = _HERE / "requirements-image.txt"
    if not p.exists():
        return []
    lines = p.read_text().splitlines()
    return [ln.strip() for ln in lines if ln.strip() and not ln.strip().startswith("#")]


def _walk_manifest(man: dict, prefix: str, base: str) -> None:
    # __pycache__/*.pyc are volatile interpreter artifacts (regenerated on any
    # import, python-version dependent) — they are NOT corpus bytes and would
    # make the pinned manifest sha irreproducible; excluded on BOTH sides
    # (this same function computes the local and the in-container manifest).
    for root, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for name in sorted(files):
            if name.endswith(".pyc"):
                continue
            p = os.path.join(root, name)
            rel = os.path.relpath(p, base).replace(os.sep, "/")
            man[f"{prefix}/{rel}"] = mc.sha256_file(p)


# the shared F0 package is staged file-by-file (never as a directory walk:
# a local __pycache__/ would poison the staged-bytes identity check)
F0_FILES = ("__init__.py", "flop_meter.py")


def _manifest(runner: str, reqs: str, inputs_dir: str, f0_dir: str, dqa: str,
              dqar: str, kernel: str, molecules: str, dxif: str, dext: str,
              image_reqs: str) -> dict:
    man = {
        "runner/f2b_runner.py": mc.sha256_file(runner),
        "runner/requirements.txt": mc.sha256_file(reqs),
        "modal/requirements-image.txt": mc.sha256_file(image_reqs),
    }
    for name in F0_FILES:
        man[f"poc/f0/{name}"] = mc.sha256_file(os.path.join(f0_dir, name))
    _walk_manifest(man, "inputs", inputs_dir)
    _walk_manifest(man, "data/d-qa", dqa)
    _walk_manifest(man, "data/d-qa-r", dqar)
    _walk_manifest(man, "data/kernel-v0", kernel)
    _walk_manifest(man, "data/molecules-v0", molecules)
    _walk_manifest(man, "data/d-xif", dxif)
    _walk_manifest(man, "data/d-ext", dext)
    return man


def _manifest_sha(man: dict) -> str:
    """pins.harness_manifest value (P2 section 1.1 canonical-JSON convention:
    sha256 over the sorted, compact, UTF-8 JSON of the staged-bytes manifest)."""
    import hashlib
    blob = json.dumps(man, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _outcome(results_dir: str) -> str:
    cands = sorted(
        n for n in os.listdir(results_dir)
        if n.startswith("results-f2b") and n.endswith(".json")
    )
    if "results-f2b.json" in cands:
        cands = ["results-f2b.json"] + [c for c in cands if c != "results-f2b.json"]
    if not cands:
        raise SystemExit(f"ERR_NO_RESULTS: no results-f2b*.json in {results_dir}")
    with open(os.path.join(results_dir, cands[0])) as f:
        j = json.load(f)
    outcome = j.get("outcome")
    if not outcome:
        raise SystemExit(f"ERR_NO_OUTCOME: {cands[0]} has no 'outcome' field")
    return str(outcome)


app = modal.App("kot-f2b")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(*_image_pins())
    .add_local_python_source("modal_common")
    .add_local_file(RUNNER, f"{REMOTE_F2B}/runner/f2b_runner.py")
    .add_local_file(RUNNER_REQS, f"{REMOTE_F2B}/runner/requirements.txt")
    .add_local_file(F0_DIR / "__init__.py", f"{REMOTE_F0}/__init__.py")
    .add_local_file(F0_DIR / "flop_meter.py", f"{REMOTE_F0}/flop_meter.py")
    .add_local_dir(F2B_INPUTS, remote_path=f"{REMOTE_F2B}/inputs")
    .add_local_dir(DQA_DIR, remote_path=f"{REMOTE_DATA}/d-qa")
    .add_local_dir(DQAR_DIR, remote_path=f"{REMOTE_DATA}/d-qa-r")
    .add_local_dir(KERNEL_DIR, remote_path=f"{REMOTE_DATA}/kernel-v0")
    .add_local_dir(MOLECULES_DIR, remote_path=f"{REMOTE_DATA}/molecules-v0")
    .add_local_dir(DXIF_DIR, remote_path=f"{REMOTE_DATA}/d-xif")
    .add_local_dir(DEXT_DIR, remote_path=f"{REMOTE_DATA}/d-ext")
    .add_local_file(_HERE / "requirements-image.txt",
                    "/root/kot/poc/modal/requirements-image.txt")
)

hf_cache = modal.Volume.from_name("kot-hf-cache", create_if_missing=True)


def _run_in_container(gpu_requested: str, mock: bool, local_manifest: dict) -> dict:
    import subprocess

    import modal_common as cmc

    started = cmc.utcnow_iso()
    staged = _manifest(
        f"{REMOTE_F2B}/runner/f2b_runner.py",
        f"{REMOTE_F2B}/runner/requirements.txt",
        f"{REMOTE_F2B}/inputs",
        REMOTE_F0,
        f"{REMOTE_DATA}/d-qa",
        f"{REMOTE_DATA}/d-qa-r",
        f"{REMOTE_DATA}/kernel-v0",
        f"{REMOTE_DATA}/molecules-v0",
        f"{REMOTE_DATA}/d-xif",
        f"{REMOTE_DATA}/d-ext",
        "/root/kot/poc/modal/requirements-image.txt",
    )
    if staged != local_manifest:
        diff = sorted(
            k for k in set(staged) | set(local_manifest)
            if staged.get(k) != local_manifest.get(k)
        )
        raise SystemExit(f"ERR_STAGING_MISMATCH: staged bytes differ from coordinator: {diff}")

    cmd = [
        sys.executable, f"{REMOTE_F2B}/runner/f2b_runner.py",
        "--inputs-dir", f"{REMOTE_F2B}/inputs",
        "--dqa-dir", f"{REMOTE_DATA}/d-qa",
        "--dqar-dir", f"{REMOTE_DATA}/d-qa-r",
        "--dxif-dir", f"{REMOTE_DATA}/d-xif",
        "--dext-dir", f"{REMOTE_DATA}/d-ext",
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
def run_f2b_t4(mock: bool = False, local_manifest: dict = None) -> dict:  # noqa: RUF013
    return _run_in_container("T4", mock, local_manifest or {})


@app.function(image=image, gpu="A10G", volumes={HF_CACHE_MOUNT: hf_cache}, timeout=TIMEOUT_S)
def run_f2b_a10g(mock: bool = False, local_manifest: dict = None) -> dict:  # noqa: RUF013
    return _run_in_container("A10G", mock, local_manifest or {})


@app.function(image=image, gpu="A100-40GB", volumes={HF_CACHE_MOUNT: hf_cache}, timeout=TIMEOUT_S)
def run_f2b_a100(mock: bool = False, local_manifest: dict = None) -> dict:  # noqa: RUF013
    return _run_in_container("A100", mock, local_manifest or {})


GPU_FUNCTIONS = {"T4": run_f2b_t4, "A10G": run_f2b_a10g, "A100": run_f2b_a100}


@app.local_entrypoint()
def main(gpu: str = "A10G", mock: bool = False, dry_plan: bool = False,
         out_root: str = "") -> None:
    gpu = gpu.upper()
    if gpu not in GPU_FUNCTIONS:
        raise SystemExit(f"ERR_GPU: --gpu must be one of {GPU_CHOICES}, got {gpu!r}")

    # --dry-plan: the runner's stdlib cost plan vs the frozen caps. Runs LOCALLY
    # (no container, no GPU, no network, $0) — a Modal launch is unnecessary to
    # inventory cells. Honours --gpu <class> for the planning throughput/price
    # table. Never emits a measurement.
    if dry_plan:
        import subprocess
        cmd = [sys.executable, str(RUNNER), "--dry-plan", "--gpu-class", gpu,
               "--out-dir", "/tmp/f2b-dry-plan",
               "--dqar-dir", str(DQAR_DIR), "--dqa-dir", str(DQA_DIR),
               "--inputs-dir", str(F2B_INPUTS)]
        print(f"$ {' '.join(cmd)}")
        raise SystemExit(subprocess.call(cmd))

    local_manifest = _manifest(str(RUNNER), str(RUNNER_REQS), str(F2B_INPUTS),
                               str(F0_DIR), str(DQA_DIR), str(DQAR_DIR),
                               str(KERNEL_DIR), str(MOLECULES_DIR),
                               str(DXIF_DIR), str(DEXT_DIR),
                               str(_HERE / "requirements-image.txt"))
    print(f"kot-f2b via Modal: gpu={gpu} mock={mock} "
          f"({len(local_manifest)} staged files, runner "
          f"{local_manifest['runner/f2b_runner.py'][:12]}…)")
    print(f"pins.harness_manifest (staged-bytes manifest sha, canonical JSON): "
          f"{_manifest_sha(local_manifest)}")
    if not mock:
        print("REMINDER: the printed sha MUST equal the FROZEN record's "
              "pins.harness_manifest and the maintainer Tier-1 go must hold "
              "before any final-phase run.")

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
        raise SystemExit(f"ERR_RUNNER: f2b_runner exited rc={rc} (partials + logs saved in {dest})")
    print("done — review and commit deliberately (results are NOT auto-committed)")
