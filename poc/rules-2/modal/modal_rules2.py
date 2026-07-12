#!/usr/bin/env python3
"""RULES-2 fine-tune + eval arms on Modal serverless GPU (DRAFT record
registry/experiments/rules-2.json — the coordinator freezes BEFORE any
final-phase run).

Wraps poc/rules-2/rules2_runner.py UNCHANGED (modal_rules1/modal_f2b
pattern): stages bytes, asserts the staged manifest in-container (fail
closed, ERR_STAGING_MISMATCH), runs the runner, ships its output directory
back as opaque bytes with sidecar-only provenance.

IMAGE: poc/rules-2/modal/requirements-image.txt = the pinned f2b/rules-1
image dep set + peft (LoRA). poc/modal/requirements-image.txt is NOT
modified; poc/rules-1, poc/f2b-transfer trees are staged BYTE-IDENTICAL
(rules1_runner/twin_engine/certificate/f2bt_runner are imported, never
edited).

PINNING DIRECTION: the DRAFT record's pins.harness_manifest is a declared
PINNED-AT-INPUTS placeholder — the staged-bytes manifest sha printed by this
wrapper. The coordinator's freeze/ops amendment records it BEFORE the final
run; ANY change to a staged byte after that requires a correction record.

    python3 poc/rules-2/modal/modal_rules2.py --print-manifest    # sha only, no modal, $0
    .venv/bin/modal run poc/rules-2/modal/modal_rules2.py --dry-plan          # cost plan, $0, local
    .venv/bin/modal run poc/rules-2/modal/modal_rules2.py --mock              # transport smoke, ~pennies
    .venv/bin/modal run poc/rules-2/modal/modal_rules2.py --gpu a10g          # DEFAULT R1 tier
    .venv/bin/modal run poc/rules-2/modal/modal_rules2.py --gpu a10g --rungs R1,R2  # R2 tier (extra authorization)

LAUNCH GATES (do NOT run the full path until ALL hold):
  1. registry/experiments/rules-2.json FROZEN by the coordinator and the
     printed sha recorded in pins.harness_manifest;
  2. the RULES-1 GPU readout exists and its branch permits RULES-2
     (PROPOSED-ASM-1420 sequencing gate; KILL-b there => explicit maintainer
     re-authorization required, s3' struck);
  3. --dry-plan OK vs caps (registry usd_cap $18 / 14 GPU-h for the R1 tier;
     coordinator outer ceiling $35) and green --mock;
  4. maintainer sign-off.
Modal hygiene (standing bd memory): launch long runs nohup+setsid;
`modal app stop ap-<id>` after killing ANY attached client.

Results land in poc/rules-2/results-incoming/<UTC stamp>-modal/ — NOT
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

RULES2_DIR = REPO_ROOT / "poc" / "rules-2"
RUNNER = RULES2_DIR / "rules2_runner.py"
RULES2_FILES = ("rules2_runner.py", "materialise_closure.py")
RULES2_INPUTS = RULES2_DIR / "inputs"
C8_RESULT = RULES2_DIR / "results" / "c8-result.json"
RULES1_DIR = REPO_ROOT / "poc" / "rules-1"
RULES1_FILES = ("rules1_runner.py", "twin_engine.py", "certificate.py")
CERT_RESULT = RULES1_DIR / "results" / "certificate-result.json"
RULES_N3 = RULES1_DIR / "results" / "rules.n3"
RULES1_INPUTS = RULES1_DIR / "inputs"
F2BT_RUNNER = REPO_ROOT / "poc" / "f2b-transfer" / "runner" / "f2bt_runner.py"
F0_DIR = REPO_ROOT / "poc" / "f0"
F0_FILES = ("__init__.py", "flop_meter.py")
NSK1_DIR = REPO_ROOT / "data" / "nsk1-clutrr"
AXV0_DIR = REPO_ROOT / "data" / "axioms-v0"
AXKIN_DIR = REPO_ROOT / "data" / "axioms-kinship-v1"
R2TRAIN_DIR = REPO_ROOT / "data" / "rules2-train"
IMAGE_REQS = _HERE / "requirements-image.txt"
INCOMING_ROOT = RULES2_DIR / "results-incoming"

REMOTE_ROOT = "/root/kot"
REMOTE_RULES2 = f"{REMOTE_ROOT}/poc/rules-2"
REMOTE_RULES1 = f"{REMOTE_ROOT}/poc/rules-1"
REMOTE_DATA = f"{REMOTE_ROOT}/data"
REMOTE_OUT = "/tmp/rules2-results"
HF_CACHE_MOUNT = "/root/.cache/huggingface"
TIMEOUT_S = 12 * 3600
GPU_CHOICES = ("T4", "A10G", "A100")
DEFAULT_ARMS = "B0,B1,B2,B3,B4,B5,c1p"


def _image_pins() -> list:
    if not IMAGE_REQS.exists():
        return []
    return [ln.strip() for ln in IMAGE_REQS.read_text().splitlines()
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


def _manifest(rules2_dir: str, rules2_inputs: str, c8_result: str,
              rules1_dir: str, cert_result: str, rules_n3: str,
              rules1_inputs: str, f2bt_runner: str, f0_dir: str, nsk1: str,
              axv0: str, axkin: str, r2train: str, image_reqs: str) -> dict:
    man = {
        "poc/f2b-transfer/runner/f2bt_runner.py": mc.sha256_file(f2bt_runner),
        "poc/rules-1/results/certificate-result.json":
            mc.sha256_file(cert_result),
        "poc/rules-1/results/rules.n3": mc.sha256_file(rules_n3),
        "poc/rules-2/results/c8-result.json": mc.sha256_file(c8_result),
        "modal/requirements-image.txt": mc.sha256_file(image_reqs),
    }
    for name in RULES2_FILES:
        man[f"poc/rules-2/{name}"] = mc.sha256_file(
            os.path.join(rules2_dir, name))
    for name in RULES1_FILES:
        man[f"poc/rules-1/{name}"] = mc.sha256_file(
            os.path.join(rules1_dir, name))
    for name in F0_FILES:
        man[f"poc/f0/{name}"] = mc.sha256_file(os.path.join(f0_dir, name))
    _walk_manifest(man, "inputs", rules2_inputs)
    _walk_manifest(man, "rules1-inputs", rules1_inputs)
    _walk_manifest(man, "data/nsk1-clutrr", nsk1)
    _walk_manifest(man, "data/axioms-v0", axv0)
    _walk_manifest(man, "data/axioms-kinship-v1", axkin)
    _walk_manifest(man, "data/rules2-train", r2train)
    return man


def _manifest_sha(man: dict) -> str:
    """pins.harness_manifest value (P2 SS1.1 canonical-JSON convention)."""
    import hashlib
    blob = json.dumps(man, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _local_manifest() -> dict:
    return _manifest(str(RULES2_DIR), str(RULES2_INPUTS), str(C8_RESULT),
                     str(RULES1_DIR), str(CERT_RESULT), str(RULES_N3),
                     str(RULES1_INPUTS), str(F2BT_RUNNER), str(F0_DIR),
                     str(NSK1_DIR), str(AXV0_DIR), str(AXKIN_DIR),
                     str(R2TRAIN_DIR), str(IMAGE_REQS))


def _outcome(results_dir: str) -> str:
    cands = sorted(n for n in os.listdir(results_dir)
                   if n.startswith("results-rules2") and n.endswith(".json"))
    if "results-rules2.json" in cands:
        cands = (["results-rules2.json"]
                 + [c for c in cands if c != "results-rules2.json"])
    if not cands:
        raise SystemExit(f"ERR_NO_RESULTS: no results-rules2*.json in {results_dir}")
    with open(os.path.join(results_dir, cands[0])) as f:
        j = json.load(f)
    outcome = j.get("outcome")
    if not outcome:
        raise SystemExit(f"ERR_NO_OUTCOME: {cands[0]} has no 'outcome' field")
    return str(outcome)


def _run_in_container(gpu_requested: str, mock: bool, arms: str, rungs: str,
                      local_manifest: dict) -> dict:
    import subprocess

    import modal_common as cmc

    started = cmc.utcnow_iso()
    staged = _manifest(
        REMOTE_RULES2,
        f"{REMOTE_RULES2}/inputs",
        f"{REMOTE_RULES2}/results/c8-result.json",
        REMOTE_RULES1,
        f"{REMOTE_RULES1}/results/certificate-result.json",
        f"{REMOTE_RULES1}/results/rules.n3",
        f"{REMOTE_RULES1}/inputs",
        f"{REMOTE_ROOT}/poc/f2b-transfer/runner/f2bt_runner.py",
        f"{REMOTE_ROOT}/poc/f0",
        f"{REMOTE_DATA}/nsk1-clutrr",
        f"{REMOTE_DATA}/axioms-v0",
        f"{REMOTE_DATA}/axioms-kinship-v1",
        f"{REMOTE_DATA}/rules2-train",
        f"{REMOTE_ROOT}/poc/rules-2/modal/requirements-image.txt",
    )
    if staged != local_manifest:
        diff = sorted(k for k in set(staged) | set(local_manifest)
                      if staged.get(k) != local_manifest.get(k))
        raise SystemExit(
            f"ERR_STAGING_MISMATCH: staged bytes differ from coordinator: {diff}")

    cmd = [
        sys.executable, f"{REMOTE_RULES2}/rules2_runner.py",
        "--inputs-dir", f"{REMOTE_RULES2}/inputs",
        "--data-root", REMOTE_DATA,
        "--corpus-dir", f"{REMOTE_DATA}/rules2-train",
        "--out-dir", REMOTE_OUT,
        "--device", "cpu" if mock else "cuda",
        "--gpu-class", gpu_requested,
        "--arms", arms,
        "--rungs", rungs,
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
    for name in ("numpy", "torch", "transformers", "peft"):
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
        notes="rules-2 fine-tune+eval arms; runner outputs shipped as opaque "
              "bytes; sidecars only — see poc/modal/modal_common.py "
              "byte-identity contract; arms=%s rungs=%s" % (arms, rungs),
    )
    files = cmc.package_results(REMOTE_OUT, run_log=log, rc=rc,
                                provenance=prov)
    try:
        hf_cache.commit()
    except Exception:  # noqa: BLE001
        pass
    return files


if modal is not None:
    app = modal.App("kot-rules2")

    image = (
        modal.Image.debian_slim(python_version="3.11")
        .pip_install(*_image_pins())
        .add_local_python_source("modal_common")
        .add_local_file(RULES2_DIR / "rules2_runner.py",
                        f"{REMOTE_RULES2}/rules2_runner.py")
        .add_local_file(RULES2_DIR / "materialise_closure.py",
                        f"{REMOTE_RULES2}/materialise_closure.py")
        .add_local_file(C8_RESULT, f"{REMOTE_RULES2}/results/c8-result.json")
        .add_local_file(RULES1_DIR / "rules1_runner.py",
                        f"{REMOTE_RULES1}/rules1_runner.py")
        .add_local_file(RULES1_DIR / "twin_engine.py",
                        f"{REMOTE_RULES1}/twin_engine.py")
        .add_local_file(RULES1_DIR / "certificate.py",
                        f"{REMOTE_RULES1}/certificate.py")
        .add_local_file(CERT_RESULT,
                        f"{REMOTE_RULES1}/results/certificate-result.json")
        .add_local_file(RULES_N3, f"{REMOTE_RULES1}/results/rules.n3")
        .add_local_file(F2BT_RUNNER,
                        f"{REMOTE_ROOT}/poc/f2b-transfer/runner/f2bt_runner.py")
        .add_local_file(F0_DIR / "__init__.py",
                        f"{REMOTE_ROOT}/poc/f0/__init__.py")
        .add_local_file(F0_DIR / "flop_meter.py",
                        f"{REMOTE_ROOT}/poc/f0/flop_meter.py")
        .add_local_dir(RULES2_INPUTS, remote_path=f"{REMOTE_RULES2}/inputs")
        .add_local_dir(RULES1_INPUTS, remote_path=f"{REMOTE_RULES1}/inputs")
        .add_local_dir(NSK1_DIR, remote_path=f"{REMOTE_DATA}/nsk1-clutrr")
        .add_local_dir(AXV0_DIR, remote_path=f"{REMOTE_DATA}/axioms-v0")
        .add_local_dir(AXKIN_DIR,
                       remote_path=f"{REMOTE_DATA}/axioms-kinship-v1")
        .add_local_dir(R2TRAIN_DIR,
                       remote_path=f"{REMOTE_DATA}/rules2-train")
        .add_local_file(IMAGE_REQS,
                        f"{REMOTE_ROOT}/poc/rules-2/modal/requirements-image.txt")
    )

    hf_cache = modal.Volume.from_name("kot-hf-cache", create_if_missing=True)

    @app.function(image=image, gpu="T4", volumes={HF_CACHE_MOUNT: hf_cache},
                  timeout=TIMEOUT_S)
    def run_rules2_t4(mock: bool = False, arms: str = DEFAULT_ARMS,
                      rungs: str = "R1",
                      local_manifest: dict = None) -> dict:  # noqa: RUF013
        return _run_in_container("T4", mock, arms, rungs, local_manifest or {})

    @app.function(image=image, gpu="A10G", volumes={HF_CACHE_MOUNT: hf_cache},
                  timeout=TIMEOUT_S)
    def run_rules2_a10g(mock: bool = False, arms: str = DEFAULT_ARMS,
                        rungs: str = "R1",
                        local_manifest: dict = None) -> dict:  # noqa: RUF013
        return _run_in_container("A10G", mock, arms, rungs,
                                 local_manifest or {})

    @app.function(image=image, gpu="A100-40GB",
                  volumes={HF_CACHE_MOUNT: hf_cache}, timeout=TIMEOUT_S)
    def run_rules2_a100(mock: bool = False, arms: str = DEFAULT_ARMS,
                        rungs: str = "R1",
                        local_manifest: dict = None) -> dict:  # noqa: RUF013
        return _run_in_container("A100", mock, arms, rungs,
                                 local_manifest or {})

    GPU_FUNCTIONS = {"T4": run_rules2_t4, "A10G": run_rules2_a10g,
                     "A100": run_rules2_a100}

    @app.local_entrypoint()
    def main(gpu: str = "A10G", mock: bool = False, dry_plan: bool = False,
             arms: str = DEFAULT_ARMS, rungs: str = "R1",
             out_root: str = "") -> None:
        gpu = gpu.upper()
        if gpu not in GPU_FUNCTIONS:
            raise SystemExit(f"ERR_GPU: --gpu must be one of {GPU_CHOICES}, got {gpu!r}")

        if dry_plan:
            import subprocess
            cmd = [sys.executable, str(RUNNER), "--dry-plan",
                   "--gpu-class", gpu, "--out-dir", "/tmp/rules2-dry-plan",
                   "--inputs-dir", str(RULES2_INPUTS),
                   "--data-root", str(REPO_ROOT / "data"),
                   "--corpus-dir", str(R2TRAIN_DIR),
                   "--rungs", rungs]
            print(f"$ {' '.join(cmd)}")
            raise SystemExit(subprocess.call(cmd))

        local_manifest = _local_manifest()
        print(f"kot-rules2 via Modal: gpu={gpu} mock={mock} arms={arms} "
              f"rungs={rungs} ({len(local_manifest)} staged files, runner "
              f"{local_manifest['poc/rules-2/rules2_runner.py'][:12]}…)")
        print(f"pins.harness_manifest (staged-bytes manifest sha, canonical "
              f"JSON): {_manifest_sha(local_manifest)}")
        if not mock:
            print("REMINDER: registry/experiments/rules-2.json must be "
                  "FROZEN with this sha in pins.harness_manifest, the "
                  "RULES-1 sequencing gate (PROPOSED-ASM-1420) must permit "
                  "the run, dry-plan + mock must be green, and maintainer "
                  "sign-off must hold (registry usd_cap $18; coordinator "
                  "ceiling $35; R2 rung needs its own authorization).")

        files = GPU_FUNCTIONS[gpu].remote(mock=mock, arms=arms, rungs=rungs,
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
            raise SystemExit(f"ERR_RUNNER: rules2_runner exited rc={rc} "
                             f"(partials + logs saved in {dest})")
        print("done — review and commit deliberately (results are NOT "
              "auto-committed); `modal app stop ap-<id>` after every "
              "attached run")


if __name__ == "__main__":
    # sha-only path: works with NO modal install, NO network, $0 — this is
    # what the pins.harness_manifest freeze/ops amendment records.
    if "--print-manifest" in sys.argv:
        man = _local_manifest()
        print(f"staged files: {len(man)}")
        print(f"pins.harness_manifest (staged-bytes manifest sha, canonical "
              f"JSON): {_manifest_sha(man)}")
        sys.exit(0)
    raise SystemExit("run via `modal run poc/rules-2/modal/modal_rules2.py ...` "
                     "or use --print-manifest")
