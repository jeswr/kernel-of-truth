#!/usr/bin/env python3
"""RULES-1-B GPU host-validity PILOT wrapper (registry/experiments/
rules-1-b.json, FROZEN 2b81375e...).

PURPOSE (2026-07-12): the mandatory real-model pilot ran A1+A7 on CPU
(poc/rules-1/results-incoming/pilot-20260712-cpu) but the parallel launcher's
sec-host-validity-gate ALSO floors acc(A5) >= 0.15, and the 1.7B A5 arm does
not fit this 7 GB CPU box in fp32. This wrapper runs rules1_runner.py
--pilot-n on a Modal GPU — SAME staged bytes as modal_rules1.py (identical
manifest computation, fail-closed ERR_STAGING_MISMATCH), SAME image reqs —
only the runner flags differ (--pilot-n N --arms <arms> --device cuda).
Pilot rows are instrument validation ONLY, never final-phase rows.

    python3 modal_rules1_pilot.py --print-manifest      # $0, must equal modal_rules1.py's sha
    .venv/bin/modal run modal_rules1_pilot.py --gpu a10g --arms A5 --pilot-n 24 \
        --out-root <dir>

Modal hygiene (standing bd memory): nohup+setsid; `modal app stop ap-<id>`
after killing ANY attached client.
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
import modal_common as mc  # noqa: E402  (stdlib-only helper, poc/modal)

RULES1_DIR = REPO_ROOT / "poc" / "rules-1"
RULES1_FILES = ("rules1_runner.py", "twin_engine.py", "certificate.py")
CERT_RESULT = RULES1_DIR / "results" / "certificate-result.json"
RULES1_INPUTS = RULES1_DIR / "inputs"
F2BT_RUNNER = REPO_ROOT / "poc" / "f2b-transfer" / "runner" / "f2bt_runner.py"
F0_DIR = REPO_ROOT / "poc" / "f0"
F0_FILES = ("__init__.py", "flop_meter.py")
NSK1_DIR = REPO_ROOT / "data" / "nsk1-clutrr"
AXV0_DIR = REPO_ROOT / "data" / "axioms-v0"
AXKIN_DIR = REPO_ROOT / "data" / "axioms-kinship-v1"
IMAGE_REQS = _MODAL_TOOLS / "requirements-image.txt"
INCOMING_ROOT = RULES1_DIR / "results-incoming"

REMOTE_ROOT = "/root/kot"
REMOTE_RULES1 = f"{REMOTE_ROOT}/poc/rules-1"
REMOTE_DATA = f"{REMOTE_ROOT}/data"
REMOTE_OUT = "/tmp/rules1-pilot-results"
HF_CACHE_MOUNT = "/root/.cache/huggingface"
TIMEOUT_S = 4 * 3600  # pilot is tiny; 12 h would be a defect
GPU_CHOICES = ("T4", "A10G", "A100")


def _image_pins() -> list:
    p = IMAGE_REQS
    if not p.exists():
        return []
    return [ln.strip() for ln in p.read_text().splitlines()
            if ln.strip() and not ln.strip().startswith("#")]


def _walk_manifest(man: dict, prefix: str, base: str) -> None:
    # __pycache__/*.pyc excluded on BOTH sides — modal_rules1.py convention,
    # byte-identical logic so the manifest sha MUST match modal_rules1.py's.
    for root, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for name in sorted(files):
            if name.endswith(".pyc"):
                continue
            p = os.path.join(root, name)
            rel = os.path.relpath(p, base).replace(os.sep, "/")
            man[f"{prefix}/{rel}"] = mc.sha256_file(p)


def _manifest(rules1_dir: str, cert_result: str, inputs_dir: str,
              f2bt_runner: str, f0_dir: str, nsk1: str, axv0: str,
              axkin: str, image_reqs: str) -> dict:
    man = {
        "poc/f2b-transfer/runner/f2bt_runner.py": mc.sha256_file(f2bt_runner),
        "poc/rules-1/results/certificate-result.json":
            mc.sha256_file(cert_result),
        "modal/requirements-image.txt": mc.sha256_file(image_reqs),
    }
    for name in RULES1_FILES:
        man[f"poc/rules-1/{name}"] = mc.sha256_file(
            os.path.join(rules1_dir, name))
    for name in F0_FILES:
        man[f"poc/f0/{name}"] = mc.sha256_file(os.path.join(f0_dir, name))
    _walk_manifest(man, "inputs", inputs_dir)
    _walk_manifest(man, "data/nsk1-clutrr", nsk1)
    _walk_manifest(man, "data/axioms-v0", axv0)
    _walk_manifest(man, "data/axioms-kinship-v1", axkin)
    return man


def _manifest_sha(man: dict) -> str:
    import hashlib
    blob = json.dumps(man, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _local_manifest() -> dict:
    return _manifest(str(RULES1_DIR), str(CERT_RESULT), str(RULES1_INPUTS),
                     str(F2BT_RUNNER), str(F0_DIR), str(NSK1_DIR),
                     str(AXV0_DIR), str(AXKIN_DIR), str(IMAGE_REQS))


def _run_pilot_in_container(gpu_requested: str, arms: str, pilot_n: int,
                            local_manifest: dict) -> dict:
    import subprocess

    import modal_common as cmc

    started = cmc.utcnow_iso()
    staged = _manifest(
        REMOTE_RULES1,
        f"{REMOTE_RULES1}/results/certificate-result.json",
        f"{REMOTE_RULES1}/inputs",
        f"{REMOTE_ROOT}/poc/f2b-transfer/runner/f2bt_runner.py",
        f"{REMOTE_ROOT}/poc/f0",
        f"{REMOTE_DATA}/nsk1-clutrr",
        f"{REMOTE_DATA}/axioms-v0",
        f"{REMOTE_DATA}/axioms-kinship-v1",
        f"{REMOTE_ROOT}/poc/modal/requirements-image.txt",
    )
    if staged != local_manifest:
        diff = sorted(k for k in set(staged) | set(local_manifest)
                      if staged.get(k) != local_manifest.get(k))
        raise SystemExit(
            f"ERR_STAGING_MISMATCH: staged bytes differ from coordinator: {diff}")

    cmd = [
        sys.executable, f"{REMOTE_RULES1}/rules1_runner.py",
        "--inputs-dir", f"{REMOTE_RULES1}/inputs",
        "--data-root", REMOTE_DATA,
        "--out-dir", REMOTE_OUT,
        "--device", "cuda",
        "--gpu-class", gpu_requested,
        "--arms", arms,
        "--pilot-n", str(pilot_n),
        # dtype stays the fp32 default: an A10G fits the 1.7B in fp32, so the
        # pilot exercises the SAME numeric path as the frozen full run.
    ]
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
        notes="rules-1-b HOST-VALIDITY PILOT (never final-phase rows); "
              "arms=%s pilot_n=%d; staged bytes identical to modal_rules1.py"
              % (arms, pilot_n),
    )
    files = cmc.package_results(REMOTE_OUT, run_log=log, rc=rc,
                                provenance=prov)
    try:
        hf_cache.commit()
    except Exception:  # noqa: BLE001
        pass
    return files


if modal is not None:
    app = modal.App("kot-rules1-pilot")

    image = (
        modal.Image.debian_slim(python_version="3.11")
        .pip_install(*_image_pins())
        .add_local_python_source("modal_common")
        .add_local_file(RULES1_DIR / "rules1_runner.py",
                        f"{REMOTE_RULES1}/rules1_runner.py")
        .add_local_file(RULES1_DIR / "twin_engine.py",
                        f"{REMOTE_RULES1}/twin_engine.py")
        .add_local_file(RULES1_DIR / "certificate.py",
                        f"{REMOTE_RULES1}/certificate.py")
        .add_local_file(CERT_RESULT,
                        f"{REMOTE_RULES1}/results/certificate-result.json")
        .add_local_file(F2BT_RUNNER,
                        f"{REMOTE_ROOT}/poc/f2b-transfer/runner/f2bt_runner.py")
        .add_local_file(F0_DIR / "__init__.py",
                        f"{REMOTE_ROOT}/poc/f0/__init__.py")
        .add_local_file(F0_DIR / "flop_meter.py",
                        f"{REMOTE_ROOT}/poc/f0/flop_meter.py")
        .add_local_dir(RULES1_INPUTS, remote_path=f"{REMOTE_RULES1}/inputs")
        .add_local_dir(NSK1_DIR, remote_path=f"{REMOTE_DATA}/nsk1-clutrr")
        .add_local_dir(AXV0_DIR, remote_path=f"{REMOTE_DATA}/axioms-v0")
        .add_local_dir(AXKIN_DIR,
                       remote_path=f"{REMOTE_DATA}/axioms-kinship-v1")
        .add_local_file(IMAGE_REQS,
                        f"{REMOTE_ROOT}/poc/modal/requirements-image.txt")
    )

    hf_cache = modal.Volume.from_name("kot-hf-cache", create_if_missing=True)

    @app.function(image=image, gpu="T4", volumes={HF_CACHE_MOUNT: hf_cache},
                  timeout=TIMEOUT_S)
    def run_pilot_t4(arms: str = "A5", pilot_n: int = 24,
                     local_manifest: dict = None) -> dict:  # noqa: RUF013
        return _run_pilot_in_container("T4", arms, pilot_n,
                                       local_manifest or {})

    @app.function(image=image, gpu="A10G", volumes={HF_CACHE_MOUNT: hf_cache},
                  timeout=TIMEOUT_S)
    def run_pilot_a10g(arms: str = "A5", pilot_n: int = 24,
                       local_manifest: dict = None) -> dict:  # noqa: RUF013
        return _run_pilot_in_container("A10G", arms, pilot_n,
                                       local_manifest or {})

    @app.function(image=image, gpu="A100-40GB",
                  volumes={HF_CACHE_MOUNT: hf_cache}, timeout=TIMEOUT_S)
    def run_pilot_a100(arms: str = "A5", pilot_n: int = 24,
                       local_manifest: dict = None) -> dict:  # noqa: RUF013
        return _run_pilot_in_container("A100", arms, pilot_n,
                                       local_manifest or {})

    GPU_FUNCTIONS = {"T4": run_pilot_t4, "A10G": run_pilot_a10g,
                     "A100": run_pilot_a100}

    @app.local_entrypoint()
    def main(gpu: str = "A10G", arms: str = "A5", pilot_n: int = 24,
             out_root: str = "") -> None:
        gpu = gpu.upper()
        if gpu not in GPU_FUNCTIONS:
            raise SystemExit(f"ERR_GPU: --gpu must be one of {GPU_CHOICES}, got {gpu!r}")
        if pilot_n < 1 or pilot_n > 100:
            raise SystemExit(f"ERR_PILOT_N: implausible --pilot-n {pilot_n}")

        local_manifest = _local_manifest()
        print(f"kot-rules1-pilot via Modal: gpu={gpu} arms={arms} "
              f"pilot_n={pilot_n} ({len(local_manifest)} staged files, "
              f"runner {local_manifest['poc/rules-1/rules1_runner.py'][:12]}…)")
        print(f"staged-bytes manifest sha (must equal modal_rules1.py "
              f"--print-manifest): {_manifest_sha(local_manifest)}")
        print("PILOT: instrument validation only — rows are NEVER "
              "measurements or final-phase rows.")

        files = GPU_FUNCTIONS[gpu].remote(arms=arms, pilot_n=pilot_n,
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

        rc = int((dest / mc.RUNNER_EXIT_NAME).read_text().strip().split("=", 1)[1])
        print(f"\nwrote {len(files)} files to {dest}")
        if rc != 0:
            raise SystemExit(f"ERR_RUNNER: rules1_runner exited rc={rc} "
                             f"(partials + logs saved in {dest})")
        print("done — pilot rows land in results-rules1-pilot.json / "
              "run-records-rules1-pilot.jsonl; `modal app stop ap-<id>` "
              "after every attached run")


if __name__ == "__main__":
    if "--print-manifest" in sys.argv:
        man = _local_manifest()
        print(f"staged files: {len(man)}")
        print(f"staged-bytes manifest sha (canonical JSON): "
              f"{_manifest_sha(man)}")
        sys.exit(0)
    raise SystemExit("run via `modal run poc/rules-1/modal/modal_rules1_pilot.py ...` "
                     "or use --print-manifest")
