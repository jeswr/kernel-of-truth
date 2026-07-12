#!/usr/bin/env python3
"""DECONF/1 Stage B on Modal serverless GPU (registry record
registry/experiments/deconf-b.json, DRAFT until frozen).

Wraps poc/deconf-b/stageb_runner.py UNCHANGED (modal_f2bt pattern): stages
bytes, asserts the staged manifest in-container (fail closed,
ERR_STAGING_MISMATCH), runs the runner, ships its output directory back as
opaque bytes with sidecar-only provenance.

IMAGE REUSE (PROPOSED-ASM-1106): the image is built from the SAME
poc/modal/requirements-image.txt (sha 0fac7243...) as the pinned f2b image
im-6uXR6RyVQV15h2B3gtpOG2 the f2b-transfer stage-2 FULL run executed on;
Stage B's only new code is repo-mounted stdlib Python — NO new dependency,
no image change. Co-schedule in the same session family as other f2b-image
runs; `modal app stop ap-<id>` after every attached run; nohup+setsid per
the standing memory.

PINNING DIRECTION: the record's pins.harness_manifest is a declared
PINNED-AT-INPUTS placeholder — the staged-bytes manifest sha printed by this
wrapper. The ops amendment records it BEFORE the final run; ANY change to a
staged byte after that amendment requires a correction record.

    python3 poc/deconf-b/modal_deconfb.py --print-manifest      # sha only, no modal, $0
    .venv/bin/modal run poc/deconf-b/modal_deconfb.py --dry-plan            # cost plan, $0, local
    .venv/bin/modal run poc/deconf-b/modal_deconfb.py --mock                # transport smoke, ~pennies
    .venv/bin/modal run poc/deconf-b/modal_deconfb.py --gpu a100            # the single-GPU final run
    .venv/bin/modal run poc/deconf-b/modal_deconfb.py --gpu a100 --kernel-arm reinstate
                                        # PROPOSED-ASM-1105 fallback ONLY

LAUNCH GATES (do NOT run the full path until ALL hold):
  1. registry/experiments/deconf-b.json FROZEN by the experiment-designer
     role (prereg-freeze) with PROPOSED-ASM-1100..1109 registered;
  2. reuse-check recorded pre-spend (fresh-runs pre-commitment), dry-plan vs
     caps OK, green mock;
  3. the printed staged-bytes sha written into pins.harness_manifest by ops
     amendment;
  4. --kernel-arm matches the frozen record's arm decision (omit iff the A1
     registration landed; reinstate otherwise — PROPOSED-ASM-1105);
  5. maintainer sign-off; usd_cap $25, gpu_hours_cap 3 h.

Results land in poc/deconf-b/results-incoming/<UTC stamp>-modal/ — NOT
auto-committed. Single GPU; 12 h function timeout.
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
    REPO_ROOT = _HERE.parents[1]
except IndexError:
    REPO_ROOT = _HERE  # container: local-path constants never dereferenced
_MODAL_TOOLS = REPO_ROOT / "poc" / "modal"
sys.path.insert(0, str(_MODAL_TOOLS))
sys.path.insert(0, str(_HERE))
import modal_common as mc  # noqa: E402  (stdlib-only helper, poc/modal)

DECONFB_DIR = REPO_ROOT / "poc" / "deconf-b"
RUNNER = DECONFB_DIR / "stageb_runner.py"
DECONFB_INPUTS = DECONFB_DIR / "inputs"
F2B_RUNNER = REPO_ROOT / "poc" / "f2b" / "runner" / "f2b_runner.py"
F2BT_RUNNER = REPO_ROOT / "poc" / "f2b-transfer" / "runner" / "f2bt_runner.py"
A1_DIR = REPO_ROOT / "poc" / "deconf-a1"
A1_FILES = ("audit_a1.py", "gs-a.jsonl", "gsa-manifest.json")
F0_DIR = REPO_ROOT / "poc" / "f0"
F0_FILES = ("__init__.py", "flop_meter.py")
DQAT_DIR = REPO_ROOT / "data" / "d-qa-t"
DADJT_DIR = REPO_ROOT / "data" / "d-adj-t"
DQA_DIR = REPO_ROOT / "data" / "d-qa"
DXIF_DIR = REPO_ROOT / "data" / "d-xif"
KERNEL_DIR = REPO_ROOT / "data" / "kernel-v0"
MOLECULES_DIR = REPO_ROOT / "data" / "molecules-v0"
IMAGE_REQS = _MODAL_TOOLS / "requirements-image.txt"
INCOMING_ROOT = DECONFB_DIR / "results-incoming"

REMOTE_ROOT = "/root/kot"
REMOTE_DECONFB = f"{REMOTE_ROOT}/poc/deconf-b"
REMOTE_DATA = f"{REMOTE_ROOT}/data"
REMOTE_OUT = "/tmp/deconfb-results"
HF_CACHE_MOUNT = "/root/.cache/huggingface"
TIMEOUT_S = 12 * 3600
GPU_CHOICES = ("T4", "A10G", "A100")


def _image_pins() -> list:
    p = IMAGE_REQS
    if not p.exists():
        return []
    lines = p.read_text().splitlines()
    return [ln.strip() for ln in lines
            if ln.strip() and not ln.strip().startswith("#")]


def _walk_manifest(man: dict, prefix: str, base: str) -> None:
    # __pycache__/*.pyc are volatile interpreter artifacts, excluded on BOTH
    # sides (this same function computes local and in-container manifests).
    for root, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for name in sorted(files):
            if name.endswith(".pyc"):
                continue
            p = os.path.join(root, name)
            rel = os.path.relpath(p, base).replace(os.sep, "/")
            man[f"{prefix}/{rel}"] = mc.sha256_file(p)


def _manifest(runner: str, inputs_dir: str, f2b_runner: str, f2bt_runner: str,
              a1_dir: str, f0_dir: str, dqat: str, dadjt: str, dqa: str,
              kernel: str, molecules: str, dxif: str, image_reqs: str) -> dict:
    man = {
        "runner/stageb_runner.py": mc.sha256_file(runner),
        "poc/f2b/runner/f2b_runner.py": mc.sha256_file(f2b_runner),
        "poc/f2b-transfer/runner/f2bt_runner.py": mc.sha256_file(f2bt_runner),
        "modal/requirements-image.txt": mc.sha256_file(image_reqs),
    }
    for name in A1_FILES:
        man[f"poc/deconf-a1/{name}"] = mc.sha256_file(os.path.join(a1_dir, name))
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
    """pins.harness_manifest value (P2 §1.1 canonical-JSON convention)."""
    import hashlib
    blob = json.dumps(man, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _local_manifest() -> dict:
    return _manifest(str(RUNNER), str(DECONFB_INPUTS), str(F2B_RUNNER),
                     str(F2BT_RUNNER), str(A1_DIR), str(F0_DIR),
                     str(DQAT_DIR), str(DADJT_DIR), str(DQA_DIR),
                     str(KERNEL_DIR), str(MOLECULES_DIR), str(DXIF_DIR),
                     str(IMAGE_REQS))


def _outcome(results_dir: str) -> str:
    cands = sorted(
        n for n in os.listdir(results_dir)
        if n.startswith("results-deconfb") and n.endswith(".json")
    )
    if "results-deconfb.json" in cands:
        cands = (["results-deconfb.json"]
                 + [c for c in cands if c != "results-deconfb.json"])
    if not cands:
        raise SystemExit(f"ERR_NO_RESULTS: no results-deconfb*.json in {results_dir}")
    with open(os.path.join(results_dir, cands[0])) as f:
        j = json.load(f)
    outcome = j.get("outcome")
    if not outcome:
        raise SystemExit(f"ERR_NO_OUTCOME: {cands[0]} has no 'outcome' field")
    return str(outcome)


def _run_in_container(gpu_requested: str, mock: bool, kernel_arm: str,
                      local_manifest: dict) -> dict:
    import subprocess

    import modal_common as cmc

    started = cmc.utcnow_iso()
    staged = _manifest(
        f"{REMOTE_DECONFB}/stageb_runner.py",
        f"{REMOTE_DECONFB}/inputs",
        f"{REMOTE_ROOT}/poc/f2b/runner/f2b_runner.py",
        f"{REMOTE_ROOT}/poc/f2b-transfer/runner/f2bt_runner.py",
        f"{REMOTE_ROOT}/poc/deconf-a1",
        f"{REMOTE_ROOT}/poc/f0",
        f"{REMOTE_DATA}/d-qa-t",
        f"{REMOTE_DATA}/d-adj-t",
        f"{REMOTE_DATA}/d-qa",
        f"{REMOTE_DATA}/kernel-v0",
        f"{REMOTE_DATA}/molecules-v0",
        f"{REMOTE_DATA}/d-xif",
        f"{REMOTE_ROOT}/poc/modal/requirements-image.txt",
    )
    if staged != local_manifest:
        diff = sorted(
            k for k in set(staged) | set(local_manifest)
            if staged.get(k) != local_manifest.get(k)
        )
        raise SystemExit(
            f"ERR_STAGING_MISMATCH: staged bytes differ from coordinator: {diff}")

    cmd = [
        sys.executable, f"{REMOTE_DECONFB}/stageb_runner.py",
        "--inputs-dir", f"{REMOTE_DECONFB}/inputs",
        "--dqat-dir", f"{REMOTE_DATA}/d-qa-t",
        "--dadjt-dir", f"{REMOTE_DATA}/d-adj-t",
        "--dqa-dir", f"{REMOTE_DATA}/d-qa",
        "--dxif-dir", f"{REMOTE_DATA}/d-xif",
        "--records-root", REMOTE_ROOT,
        "--out-dir", REMOTE_OUT,
        "--device", "cpu" if mock else "cuda",
        "--gpu-class", gpu_requested,
        "--kernel-arm", kernel_arm,
    ]
    if mock:
        cmd.append("--mock")
    os.makedirs(REMOTE_OUT, exist_ok=True)
    lines = [f"$ {' '.join(cmd)}\n"]
    with subprocess.Popen(cmd, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT, text=True,
                          bufsize=1) as proc:
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
        notes="deconf-b Stage B; runner outputs shipped as opaque bytes; "
              "sidecars only — see poc/modal/modal_common.py byte-identity "
              "contract; kernel_arm=%s" % kernel_arm,
    )
    files = cmc.package_results(REMOTE_OUT, run_log=log, rc=rc, provenance=prov)
    try:
        hf_cache.commit()
    except Exception:  # noqa: BLE001
        pass
    return files


if modal is not None:
    app = modal.App("kot-deconfb")

    image = (
        modal.Image.debian_slim(python_version="3.11")
        .pip_install(*_image_pins())
        .add_local_python_source("modal_common")
        .add_local_file(RUNNER, f"{REMOTE_DECONFB}/stageb_runner.py")
        .add_local_file(F2B_RUNNER, f"{REMOTE_ROOT}/poc/f2b/runner/f2b_runner.py")
        .add_local_file(F2BT_RUNNER,
                        f"{REMOTE_ROOT}/poc/f2b-transfer/runner/f2bt_runner.py")
        .add_local_file(A1_DIR / "audit_a1.py",
                        f"{REMOTE_ROOT}/poc/deconf-a1/audit_a1.py")
        .add_local_file(A1_DIR / "gs-a.jsonl",
                        f"{REMOTE_ROOT}/poc/deconf-a1/gs-a.jsonl")
        .add_local_file(A1_DIR / "gsa-manifest.json",
                        f"{REMOTE_ROOT}/poc/deconf-a1/gsa-manifest.json")
        .add_local_file(F0_DIR / "__init__.py",
                        f"{REMOTE_ROOT}/poc/f0/__init__.py")
        .add_local_file(F0_DIR / "flop_meter.py",
                        f"{REMOTE_ROOT}/poc/f0/flop_meter.py")
        .add_local_dir(DECONFB_INPUTS, remote_path=f"{REMOTE_DECONFB}/inputs")
        .add_local_dir(DQAT_DIR, remote_path=f"{REMOTE_DATA}/d-qa-t")
        .add_local_dir(DADJT_DIR, remote_path=f"{REMOTE_DATA}/d-adj-t")
        .add_local_dir(DQA_DIR, remote_path=f"{REMOTE_DATA}/d-qa")
        .add_local_dir(KERNEL_DIR, remote_path=f"{REMOTE_DATA}/kernel-v0")
        .add_local_dir(MOLECULES_DIR, remote_path=f"{REMOTE_DATA}/molecules-v0")
        .add_local_dir(DXIF_DIR, remote_path=f"{REMOTE_DATA}/d-xif")
        .add_local_file(IMAGE_REQS,
                        f"{REMOTE_ROOT}/poc/modal/requirements-image.txt")
    )

    hf_cache = modal.Volume.from_name("kot-hf-cache", create_if_missing=True)

    @app.function(image=image, gpu="T4", volumes={HF_CACHE_MOUNT: hf_cache},
                  timeout=TIMEOUT_S)
    def run_deconfb_t4(mock: bool = False, kernel_arm: str = "omit",
                       local_manifest: dict = None) -> dict:  # noqa: RUF013
        return _run_in_container("T4", mock, kernel_arm, local_manifest or {})

    @app.function(image=image, gpu="A10G", volumes={HF_CACHE_MOUNT: hf_cache},
                  timeout=TIMEOUT_S)
    def run_deconfb_a10g(mock: bool = False, kernel_arm: str = "omit",
                         local_manifest: dict = None) -> dict:  # noqa: RUF013
        return _run_in_container("A10G", mock, kernel_arm, local_manifest or {})

    @app.function(image=image, gpu="A100-40GB",
                  volumes={HF_CACHE_MOUNT: hf_cache}, timeout=TIMEOUT_S)
    def run_deconfb_a100(mock: bool = False, kernel_arm: str = "omit",
                         local_manifest: dict = None) -> dict:  # noqa: RUF013
        return _run_in_container("A100", mock, kernel_arm, local_manifest or {})

    GPU_FUNCTIONS = {"T4": run_deconfb_t4, "A10G": run_deconfb_a10g,
                     "A100": run_deconfb_a100}

    @app.local_entrypoint()
    def main(gpu: str = "A100", mock: bool = False, dry_plan: bool = False,
             kernel_arm: str = "omit", out_root: str = "") -> None:
        gpu = gpu.upper()
        if gpu not in GPU_FUNCTIONS:
            raise SystemExit(f"ERR_GPU: --gpu must be one of {GPU_CHOICES}, got {gpu!r}")
        if kernel_arm not in ("omit", "reinstate"):
            raise SystemExit(f"ERR_KERNEL_ARM: {kernel_arm!r}")

        if dry_plan:
            import subprocess
            cmd = [sys.executable, str(RUNNER), "--dry-plan", "--gpu-class", gpu,
                   "--out-dir", "/tmp/deconfb-dry-plan",
                   "--kernel-arm", kernel_arm,
                   "--inputs-dir", str(DECONFB_INPUTS),
                   "--dqat-dir", str(DQAT_DIR), "--dadjt-dir", str(DADJT_DIR),
                   "--dqa-dir", str(DQA_DIR)]
            print(f"$ {' '.join(cmd)}")
            raise SystemExit(subprocess.call(cmd))

        local_manifest = _local_manifest()
        print(f"kot-deconfb via Modal: gpu={gpu} mock={mock} "
              f"kernel_arm={kernel_arm} ({len(local_manifest)} staged files, "
              f"runner {local_manifest['runner/stageb_runner.py'][:12]}…)")
        print(f"pins.harness_manifest (staged-bytes manifest sha, canonical "
              f"JSON): {_manifest_sha(local_manifest)}")
        if not mock:
            print("REMINDER: the printed sha MUST equal the ops-amendment "
                  "value in the FROZEN record's pins.harness_manifest, the "
                  "record must be FROZEN (prereg-freeze) with "
                  "PROPOSED-ASM-1100..1109 registered, reuse-check recorded "
                  "pre-spend, --kernel-arm must match the frozen arm "
                  "decision, and maintainer sign-off must hold.")

        files = GPU_FUNCTIONS[gpu].remote(mock=mock, kernel_arm=kernel_arm,
                                          local_manifest=local_manifest)

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
            raise SystemExit(f"ERR_RUNNER: stageb_runner exited rc={rc} "
                             f"(partials + logs saved in {dest})")
        print("done — review and commit deliberately (results are NOT "
              "auto-committed); `modal app stop ap-<id>` after every attached run")


if __name__ == "__main__":
    # sha-only path: works with NO modal install, NO network, $0 — this is
    # what the harness_manifest ops amendment records.
    if "--print-manifest" in sys.argv:
        man = _local_manifest()
        print(f"staged files: {len(man)}")
        print(f"pins.harness_manifest (staged-bytes manifest sha, canonical "
              f"JSON): {_manifest_sha(man)}")
        sys.exit(0)
    raise SystemExit("run via `modal run poc/deconf-b/modal_deconfb.py ...` "
                     "or use --print-manifest")
