#!/usr/bin/env python3
"""RULES-1 GPU arms on Modal serverless GPU (FROZEN record
registry/experiments/rules-1.json, frozen_sha256 0ef03ee16fdc278885b450500c
b674f4319c1154ad067995e0b491feae4bec6c).

Wraps poc/rules-1/rules1_runner.py UNCHANGED (modal_deconfb/modal_f2bt
pattern): stages bytes, asserts the staged manifest in-container (fail
closed, ERR_STAGING_MISMATCH), runs the runner, ships its output directory
back as opaque bytes with sidecar-only provenance.

IMAGE REUSE (PROPOSED-ASM-1106 discipline): the image is built from the SAME
poc/modal/requirements-image.txt (sha 0fac7243...) as the pinned f2b image
im-6uXR6RyVQV15h2B3gtpOG2 that the f2b-transfer stage-2 FULL run and the
deconf-b Stage B run executed on; RULES-1's only new code is repo-mounted
stdlib Python — NO new dependency, no image change. poc/f2b, poc/f2b-transfer
and poc/deconf-b trees are staged/reused BYTE-IDENTICAL (f2bt_runner.py is
imported for the HFLM scorer + seeded retry sampler + CellGuard bytes).

PINNING DIRECTION: the frozen record's pins.harness_manifest is a declared
PINNED-AT-INPUTS placeholder — the staged-bytes manifest sha printed by this
wrapper. The ops amendment records it (together with pins.model_revisions)
BEFORE the final run; ANY change to a staged byte after that amendment
requires a correction record.

    python3 poc/rules-1/modal/modal_rules1.py --print-manifest    # sha only, no modal, $0
    .venv/bin/modal run poc/rules-1/modal/modal_rules1.py --dry-plan   # cost plan, $0, local
    .venv/bin/modal run poc/rules-1/modal/modal_rules1.py --mock       # transport smoke, ~pennies
    .venv/bin/modal run poc/rules-1/modal/modal_rules1.py --gpu a10g   # the single-GPU final run

LAUNCH GATES (do NOT run the full path until ALL hold):
  1. registry/experiments/rules-1.json is FROZEN (it is: 0ef03ee1...) and the
     pinned CPU certificate PASSED (verified fail-closed by the runner:
     ERR_CERT_PRECONDITION — no GPU spend otherwise);
  2. ops amendment fills BOTH PINNED-AT-INPUTS pins: pins.harness_manifest =
     the sha printed here, pins.model_revisions = the R1/R3 revisions in
     poc/rules-1/inputs/rules1-manifest.json (provenance chain:
     f2b-replicate/f2b-transfer FROZEN records — the nsk1 registry record is
     DRAFT and carries no resolved shas);
  3. --dry-plan OK vs caps (registry usd_cap $10 / 6 GPU-h; coordinator
     outer ceiling $40, maintainer-approved) and green --mock;
  4. maintainer sign-off.
Modal hygiene (standing bd memory): launch long runs nohup+setsid;
`modal app stop ap-<id>` after killing ANY attached client.

Results land in poc/rules-1/results-incoming/<UTC stamp>-modal/ — NOT
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
    REPO_ROOT = _HERE.parents[2]
except IndexError:
    REPO_ROOT = _HERE  # container: local-path constants never dereferenced
_MODAL_TOOLS = REPO_ROOT / "poc" / "modal"
sys.path.insert(0, str(_MODAL_TOOLS))
import modal_common as mc  # noqa: E402  (stdlib-only helper, poc/modal)

RULES1_DIR = REPO_ROOT / "poc" / "rules-1"
RUNNER = RULES1_DIR / "rules1_runner.py"
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
REMOTE_OUT = "/tmp/rules1-results"
HF_CACHE_MOUNT = "/root/.cache/huggingface"
TIMEOUT_S = 12 * 3600
GPU_CHOICES = ("T4", "A10G", "A100")


def _image_pins() -> list:
    p = IMAGE_REQS
    if not p.exists():
        return []
    return [ln.strip() for ln in p.read_text().splitlines()
            if ln.strip() and not ln.strip().startswith("#")]


def _walk_manifest(man: dict, prefix: str, base: str) -> None:
    # __pycache__/*.pyc excluded on BOTH sides (same function computes local
    # and in-container manifests) — modal_deconfb convention.
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
    """pins.harness_manifest value (P2 §1.1 canonical-JSON convention)."""
    import hashlib
    blob = json.dumps(man, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _local_manifest() -> dict:
    return _manifest(str(RULES1_DIR), str(CERT_RESULT), str(RULES1_INPUTS),
                     str(F2BT_RUNNER), str(F0_DIR), str(NSK1_DIR),
                     str(AXV0_DIR), str(AXKIN_DIR), str(IMAGE_REQS))


def _outcome(results_dir: str) -> str:
    cands = sorted(n for n in os.listdir(results_dir)
                   if n.startswith("results-rules1") and n.endswith(".json"))
    if "results-rules1.json" in cands:
        cands = (["results-rules1.json"]
                 + [c for c in cands if c != "results-rules1.json"])
    if not cands:
        raise SystemExit(f"ERR_NO_RESULTS: no results-rules1*.json in {results_dir}")
    with open(os.path.join(results_dir, cands[0])) as f:
        j = json.load(f)
    outcome = j.get("outcome")
    if not outcome:
        raise SystemExit(f"ERR_NO_OUTCOME: {cands[0]} has no 'outcome' field")
    return str(outcome)


def _run_in_container(gpu_requested: str, mock: bool, arms: str,
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
        "--device", "cpu" if mock else "cuda",
        "--gpu-class", gpu_requested,
        "--arms", arms,
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
        notes="rules-1 GPU arms; runner outputs shipped as opaque bytes; "
              "sidecars only — see poc/modal/modal_common.py byte-identity "
              "contract; arms=%s" % arms,
    )
    files = cmc.package_results(REMOTE_OUT, run_log=log, rc=rc,
                                provenance=prov)
    try:
        hf_cache.commit()
    except Exception:  # noqa: BLE001
        pass
    return files


if modal is not None:
    app = modal.App("kot-rules1")

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
    def run_rules1_t4(mock: bool = False, arms: str = "A1,A3,A5,A7,c1",
                      local_manifest: dict = None) -> dict:  # noqa: RUF013
        return _run_in_container("T4", mock, arms, local_manifest or {})

    @app.function(image=image, gpu="A10G", volumes={HF_CACHE_MOUNT: hf_cache},
                  timeout=TIMEOUT_S)
    def run_rules1_a10g(mock: bool = False, arms: str = "A1,A3,A5,A7,c1",
                        local_manifest: dict = None) -> dict:  # noqa: RUF013
        return _run_in_container("A10G", mock, arms, local_manifest or {})

    @app.function(image=image, gpu="A100-40GB",
                  volumes={HF_CACHE_MOUNT: hf_cache}, timeout=TIMEOUT_S)
    def run_rules1_a100(mock: bool = False, arms: str = "A1,A3,A5,A7,c1",
                        local_manifest: dict = None) -> dict:  # noqa: RUF013
        return _run_in_container("A100", mock, arms, local_manifest or {})

    GPU_FUNCTIONS = {"T4": run_rules1_t4, "A10G": run_rules1_a10g,
                     "A100": run_rules1_a100}

    @app.local_entrypoint()
    def main(gpu: str = "A10G", mock: bool = False, dry_plan: bool = False,
             arms: str = "A1,A3,A5,A7,c1", out_root: str = "") -> None:
        gpu = gpu.upper()
        if gpu not in GPU_FUNCTIONS:
            raise SystemExit(f"ERR_GPU: --gpu must be one of {GPU_CHOICES}, got {gpu!r}")

        if dry_plan:
            import subprocess
            cmd = [sys.executable, str(RUNNER), "--dry-plan",
                   "--gpu-class", gpu, "--out-dir", "/tmp/rules1-dry-plan",
                   "--inputs-dir", str(RULES1_INPUTS),
                   "--data-root", str(REPO_ROOT / "data")]
            print(f"$ {' '.join(cmd)}")
            raise SystemExit(subprocess.call(cmd))

        local_manifest = _local_manifest()
        print(f"kot-rules1 via Modal: gpu={gpu} mock={mock} arms={arms} "
              f"({len(local_manifest)} staged files, runner "
              f"{local_manifest['poc/rules-1/rules1_runner.py'][:12]}…)")
        print(f"pins.harness_manifest (staged-bytes manifest sha, canonical "
              f"JSON): {_manifest_sha(local_manifest)}")
        if not mock:
            print("REMINDER: the printed sha MUST equal the ops-amendment "
                  "value in the FROZEN record's pins.harness_manifest, "
                  "pins.model_revisions must be ops-amended to the R1/R3 "
                  "revisions in rules1-manifest.json, dry-plan + mock must "
                  "be green, and maintainer sign-off must hold "
                  "(registry usd_cap $10; coordinator ceiling $40).")

        files = GPU_FUNCTIONS[gpu].remote(mock=mock, arms=arms,
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
            raise SystemExit(f"ERR_RUNNER: rules1_runner exited rc={rc} "
                             f"(partials + logs saved in {dest})")
        print("done — review and commit deliberately (results are NOT "
              "auto-committed); `modal app stop ap-<id>` after every "
              "attached run")


if __name__ == "__main__":
    # sha-only path: works with NO modal install, NO network, $0 — this is
    # what the pins.harness_manifest ops amendment records.
    if "--print-manifest" in sys.argv:
        man = _local_manifest()
        print(f"staged files: {len(man)}")
        print(f"pins.harness_manifest (staged-bytes manifest sha, canonical "
              f"JSON): {_manifest_sha(man)}")
        sys.exit(0)
    raise SystemExit("run via `modal run poc/rules-1/modal/modal_rules1.py ...` "
                     "or use --print-manifest")
