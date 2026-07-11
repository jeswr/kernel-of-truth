#!/usr/bin/env python3
"""f2b-transfer STAGE 2 on Modal serverless GPU (Tier-1; registry record
registry/experiments/f2b-transfer.json).

Wraps poc/f2b-transfer/runner/f2bt_runner.py UNCHANGED (modal_f2b pattern):
stages bytes, asserts the staged manifest in-container (fail closed,
ERR_STAGING_MISMATCH), runs the runner, ships its output directory back as
opaque bytes with sidecar-only provenance.

PINNING DIRECTION (matches the frozen record, differs from f2b-replicate):
the frozen record's pins.harness_manifest is a declared PINNED-AT-INPUTS
placeholder — "staged-bytes-manifest-sha-of-poc/f2b-transfer-printed-by-its-
modal-wrapper-filled-by-ops-amendment-before-any-final-phase-run". Every
launch (and `--print-manifest`) prints the sha; the ops amendment records it
BEFORE the final run, and ANY change to a staged byte after that amendment
requires a correction record before any final-phase run.

    python3 poc/f2b-transfer/modal/modal_f2bt.py --print-manifest   # sha only, no modal, $0
    .venv/bin/modal run poc/f2b-transfer/modal/modal_f2bt.py --dry-plan            # cost plan, $0, local
    .venv/bin/modal run poc/f2b-transfer/modal/modal_f2bt.py --mock                # transport smoke, ~pennies
    .venv/bin/modal run poc/f2b-transfer/modal/modal_f2bt.py --gpu a100            # the single-GPU final run

LAUNCH GATES (do NOT run the full path until ALL hold — frozen
stage_discipline + runner_constraints):
  1. stage-1 adjudication record + verdict-gen read are in the results log
     (they are: INCOMPLETE-DATA, endorsement LB 0.9395 > 0.70);
  2. reuse-check recorded pre-spend (pre-committed fresh-runs decision),
     dry-plan vs caps OK, green mock;
  3. the printed staged-bytes sha has been written into pins.harness_manifest
     by ops amendment;
  4. maintainer sign-off (auto-authorization under $100 applies ONLY after
     sign-off of this design); usd_cap $15, gpu_hours_cap 4 h, Tier-1 cap $80.

Results land in poc/f2b-transfer/results-incoming/<UTC stamp>-modal/ — NOT
auto-committed. Single GPU (A100-40GB or A10G per runner_constraints);
concurrency cap honoured trivially (one container). 12 h function timeout.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

try:
    import modal
except ImportError:  # --print-manifest works without a modal install
    modal = None

_HERE = Path(__file__).resolve().parent
try:
    REPO_ROOT = _HERE.parents[2]
except IndexError:
    REPO_ROOT = _HERE  # container: local-path constants never dereferenced
_MODAL_TOOLS = REPO_ROOT / "poc" / "modal"
sys.path.insert(0, str(_MODAL_TOOLS))
sys.path.insert(0, str(_HERE))
import modal_common as mc  # noqa: E402  (stdlib-only helper, poc/modal)

F2BT_DIR = REPO_ROOT / "poc" / "f2b-transfer"
RUNNER = F2BT_DIR / "runner" / "f2bt_runner.py"
RUNNER_REQS = F2BT_DIR / "runner" / "requirements.txt"
F2BT_INPUTS = F2BT_DIR / "inputs"
F0_DIR = REPO_ROOT / "poc" / "f0"
DQAT_DIR = REPO_ROOT / "data" / "d-qa-t"
DADJT_DIR = REPO_ROOT / "data" / "d-adj-t"
DQA_DIR = REPO_ROOT / "data" / "d-qa"
DXIF_DIR = REPO_ROOT / "data" / "d-xif"
KERNEL_DIR = REPO_ROOT / "data" / "kernel-v0"
MOLECULES_DIR = REPO_ROOT / "data" / "molecules-v0"
IMAGE_REQS = _MODAL_TOOLS / "requirements-image.txt"
INCOMING_ROOT = F2BT_DIR / "results-incoming"

REMOTE_F2BT = "/root/kot/poc/f2b-transfer"
REMOTE_F0 = "/root/kot/poc/f0"
REMOTE_DATA = "/root/kot/data"
REMOTE_OUT = "/tmp/f2bt-results"
HF_CACHE_MOUNT = "/root/.cache/huggingface"
TIMEOUT_S = 12 * 3600  # dry-plan worst case is far below; results ship at exit
GPU_CHOICES = ("T4", "A10G", "A100")


def _image_pins() -> list:
    p = IMAGE_REQS
    if not p.exists():
        return []
    lines = p.read_text().splitlines()
    return [ln.strip() for ln in lines if ln.strip() and not ln.strip().startswith("#")]


def _walk_manifest(man: dict, prefix: str, base: str) -> None:
    # __pycache__/*.pyc are volatile interpreter artifacts — NOT corpus bytes;
    # excluded on BOTH sides (this same function computes the local and the
    # in-container manifest). NOTE: the data/ corpora contain no __pycache__
    # by construction, so their kot-corpus-hash pins are unaffected.
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


def _manifest(runner: str, reqs: str, inputs_dir: str, f0_dir: str,
              dqat: str, dadjt: str, dqa: str, kernel: str, molecules: str,
              dxif: str, image_reqs: str) -> dict:
    man = {
        "runner/f2bt_runner.py": mc.sha256_file(runner),
        "runner/requirements.txt": mc.sha256_file(reqs),
        "modal/requirements-image.txt": mc.sha256_file(image_reqs),
    }
    for name in F0_FILES:
        man[f"poc/f0/{name}"] = mc.sha256_file(os.path.join(f0_dir, name))
    _walk_manifest(man, "inputs", inputs_dir)
    _walk_manifest(man, "data/d-qa-t", dqat)
    _walk_manifest(man, "data/d-adj-t", dadjt)
    _walk_manifest(man, "data/d-qa", dqa)
    _walk_manifest(man, "data/kernel-v0", kernel)
    _walk_manifest(man, "data/molecules-v0", molecules)
    _walk_manifest(man, "data/d-xif", dxif)
    return man


def _manifest_sha(man: dict) -> str:
    """pins.harness_manifest value (P2 section 1.1 canonical-JSON convention:
    sha256 over the sorted, compact, UTF-8 JSON of the staged-bytes manifest)."""
    import hashlib
    blob = json.dumps(man, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _local_manifest() -> dict:
    return _manifest(str(RUNNER), str(RUNNER_REQS), str(F2BT_INPUTS),
                     str(F0_DIR), str(DQAT_DIR), str(DADJT_DIR), str(DQA_DIR),
                     str(KERNEL_DIR), str(MOLECULES_DIR), str(DXIF_DIR),
                     str(IMAGE_REQS))


def _outcome(results_dir: str) -> str:
    cands = sorted(
        n for n in os.listdir(results_dir)
        if n.startswith("results-f2bt") and n.endswith(".json")
    )
    if "results-f2bt.json" in cands:
        cands = ["results-f2bt.json"] + [c for c in cands if c != "results-f2bt.json"]
    if not cands:
        raise SystemExit(f"ERR_NO_RESULTS: no results-f2bt*.json in {results_dir}")
    with open(os.path.join(results_dir, cands[0])) as f:
        j = json.load(f)
    outcome = j.get("outcome")
    if not outcome:
        raise SystemExit(f"ERR_NO_OUTCOME: {cands[0]} has no 'outcome' field")
    return str(outcome)


def _run_in_container(gpu_requested: str, mock: bool, local_manifest: dict) -> dict:
    import subprocess

    import modal_common as cmc

    started = cmc.utcnow_iso()
    staged = _manifest(
        f"{REMOTE_F2BT}/runner/f2bt_runner.py",
        f"{REMOTE_F2BT}/runner/requirements.txt",
        f"{REMOTE_F2BT}/inputs",
        REMOTE_F0,
        f"{REMOTE_DATA}/d-qa-t",
        f"{REMOTE_DATA}/d-adj-t",
        f"{REMOTE_DATA}/d-qa",
        f"{REMOTE_DATA}/kernel-v0",
        f"{REMOTE_DATA}/molecules-v0",
        f"{REMOTE_DATA}/d-xif",
        "/root/kot/poc/modal/requirements-image.txt",
    )
    if staged != local_manifest:
        diff = sorted(
            k for k in set(staged) | set(local_manifest)
            if staged.get(k) != local_manifest.get(k)
        )
        raise SystemExit(f"ERR_STAGING_MISMATCH: staged bytes differ from coordinator: {diff}")

    cmd = [
        sys.executable, f"{REMOTE_F2BT}/runner/f2bt_runner.py",
        "--inputs-dir", f"{REMOTE_F2BT}/inputs",
        "--dqat-dir", f"{REMOTE_DATA}/d-qa-t",
        "--dadjt-dir", f"{REMOTE_DATA}/d-adj-t",
        "--dqa-dir", f"{REMOTE_DATA}/d-qa",
        "--dxif-dir", f"{REMOTE_DATA}/d-xif",
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


if modal is not None:
    app = modal.App("kot-f2bt")

    image = (
        modal.Image.debian_slim(python_version="3.11")
        .pip_install(*_image_pins())
        .add_local_python_source("modal_common")
        .add_local_file(RUNNER, f"{REMOTE_F2BT}/runner/f2bt_runner.py")
        .add_local_file(RUNNER_REQS, f"{REMOTE_F2BT}/runner/requirements.txt")
        .add_local_file(F0_DIR / "__init__.py", f"{REMOTE_F0}/__init__.py")
        .add_local_file(F0_DIR / "flop_meter.py", f"{REMOTE_F0}/flop_meter.py")
        .add_local_dir(F2BT_INPUTS, remote_path=f"{REMOTE_F2BT}/inputs")
        .add_local_dir(DQAT_DIR, remote_path=f"{REMOTE_DATA}/d-qa-t")
        .add_local_dir(DADJT_DIR, remote_path=f"{REMOTE_DATA}/d-adj-t")
        .add_local_dir(DQA_DIR, remote_path=f"{REMOTE_DATA}/d-qa")
        .add_local_dir(KERNEL_DIR, remote_path=f"{REMOTE_DATA}/kernel-v0")
        .add_local_dir(MOLECULES_DIR, remote_path=f"{REMOTE_DATA}/molecules-v0")
        .add_local_dir(DXIF_DIR, remote_path=f"{REMOTE_DATA}/d-xif")
        .add_local_file(IMAGE_REQS, "/root/kot/poc/modal/requirements-image.txt")
    )

    hf_cache = modal.Volume.from_name("kot-hf-cache", create_if_missing=True)

    @app.function(image=image, gpu="T4", volumes={HF_CACHE_MOUNT: hf_cache},
                  timeout=TIMEOUT_S)
    def run_f2bt_t4(mock: bool = False, local_manifest: dict = None) -> dict:  # noqa: RUF013
        return _run_in_container("T4", mock, local_manifest or {})

    @app.function(image=image, gpu="A10G", volumes={HF_CACHE_MOUNT: hf_cache},
                  timeout=TIMEOUT_S)
    def run_f2bt_a10g(mock: bool = False, local_manifest: dict = None) -> dict:  # noqa: RUF013
        return _run_in_container("A10G", mock, local_manifest or {})

    @app.function(image=image, gpu="A100-40GB", volumes={HF_CACHE_MOUNT: hf_cache},
                  timeout=TIMEOUT_S)
    def run_f2bt_a100(mock: bool = False, local_manifest: dict = None) -> dict:  # noqa: RUF013
        return _run_in_container("A100", mock, local_manifest or {})

    GPU_FUNCTIONS = {"T4": run_f2bt_t4, "A10G": run_f2bt_a10g, "A100": run_f2bt_a100}

    @app.local_entrypoint()
    def main(gpu: str = "A100", mock: bool = False, dry_plan: bool = False,
             out_root: str = "") -> None:
        gpu = gpu.upper()
        if gpu not in GPU_FUNCTIONS:
            raise SystemExit(f"ERR_GPU: --gpu must be one of {GPU_CHOICES}, got {gpu!r}")

        # --dry-plan: the runner's stdlib cost plan vs the frozen caps. Runs
        # LOCALLY (no container, no GPU, no network, $0). Never a measurement.
        if dry_plan:
            import subprocess
            cmd = [sys.executable, str(RUNNER), "--dry-plan", "--gpu-class", gpu,
                   "--out-dir", "/tmp/f2bt-dry-plan",
                   "--inputs-dir", str(F2BT_INPUTS),
                   "--dqat-dir", str(DQAT_DIR), "--dadjt-dir", str(DADJT_DIR),
                   "--dqa-dir", str(DQA_DIR)]
            print(f"$ {' '.join(cmd)}")
            raise SystemExit(subprocess.call(cmd))

        local_manifest = _local_manifest()
        print(f"kot-f2bt via Modal: gpu={gpu} mock={mock} "
              f"({len(local_manifest)} staged files, runner "
              f"{local_manifest['runner/f2bt_runner.py'][:12]}…)")
        print(f"pins.harness_manifest (staged-bytes manifest sha, canonical JSON): "
              f"{_manifest_sha(local_manifest)}")
        if not mock:
            print("REMINDER: the printed sha MUST equal the value the ops "
                  "amendment wrote into the frozen record's "
                  "pins.harness_manifest (PINNED-AT-INPUTS placeholder), the "
                  "stage-1 record must already be in the results log, and "
                  "maintainer sign-off must hold before any final-phase run.")

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
            raise SystemExit(f"ERR_RUNNER: f2bt_runner exited rc={rc} (partials + logs saved in {dest})")
        print("done — review and commit deliberately (results are NOT auto-committed)")


if __name__ == "__main__":
    # sha-only path: works with NO modal install, NO network, $0 — this is
    # what the harness_manifest ops amendment records.
    if "--print-manifest" in sys.argv:
        man = _local_manifest()
        print(f"staged files: {len(man)}")
        print(f"pins.harness_manifest (staged-bytes manifest sha, canonical JSON): "
              f"{_manifest_sha(man)}")
        sys.exit(0)
    raise SystemExit("run via `modal run poc/f2b-transfer/modal/modal_f2bt.py ...` "
                     "or use --print-manifest")
