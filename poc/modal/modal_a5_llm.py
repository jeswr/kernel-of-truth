#!/usr/bin/env python3
"""a5-llm on Modal serverless GPU (Tier-1; registry record
registry/experiments/a5-llm.json).

Wraps poc/a5-llm/runner/a5_llm_runner.py UNCHANGED (modal_f2b pattern): stages
bytes, asserts the staged manifest in-container (fail closed,
ERR_STAGING_MISMATCH), runs the runner over the six LLM cells
({llm-direct,llm-rag} x {R1,R2,R3}), and ships the runner's output directory
back as opaque bytes with sidecar-only provenance. The CPU arms
(engine/abstain-all/answer-all) run locally via the instrument, not here.

PINNING DIRECTION (f2b-replicate convention): the frozen record pins
pins.harness_manifest to THIS wrapper's staged-bytes manifest sha DIRECTLY at
freeze time (no placeholder). The launch reprints the sha and the in-container
check fails closed on any drift; a run is valid only if the printed value
equals the frozen pin. Compute it for the freeze WITHOUT a Modal connection:

    poc/modal/.venv/bin/python poc/modal/modal_a5_llm.py --print-manifest

Then:

    poc/modal/.venv/bin/python poc/modal/modal_a5_llm.py --dry-plan --gpu a10g   # $0 cost plan, local
    .venv/bin/modal run poc/modal/modal_a5_llm.py --mock                         # transport smoke, ~pennies
    .venv/bin/modal run poc/modal/modal_a5_llm.py --gpu a10g                     # RIGHT-SIZED run (single A10G)

LAUNCH GATES (do NOT run the full path until ALL hold):
  1. registry/experiments/a5-llm.json FROZEN and the printed harness-manifest
     sha equals its pins.harness_manifest;
  2. the reuse-check --gate + dry-plan-vs-caps pre-spend gates pass;
  3. maintainer Tier-1 go (bead lbv sign-off; usd_cap $25, gpu_hours_cap 4 h).

Results land in poc/a5-llm/results-incoming/<UTC stamp>-modal/ — NOT
auto-committed. Budget (from --dry-plan): the design estimate is ~$3-8; the
runner's per-cell CellGuard + whole-run GPU-hours guard bound the worst case.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
import modal_common as mc  # noqa: E402

try:
    REPO_ROOT = _HERE.parents[1]
except IndexError:
    REPO_ROOT = _HERE  # container: local-path constants never dereferenced
A5_DIR = REPO_ROOT / "poc" / "a5-llm"
RUNNER = A5_DIR / "runner" / "a5_llm_runner.py"
RUNNER_REQS = A5_DIR / "runner" / "requirements.txt"
PACK = A5_DIR / "inputs" / "a5-llm-pack.jsonl"
MANIFEST = A5_DIR / "inputs" / "a5-llm-manifest.json"
IMAGE_REQS = _HERE / "requirements-image.txt"
INCOMING_ROOT = A5_DIR / "results-incoming"

REMOTE_A5 = "/root/kot/poc/a5-llm"
REMOTE_MODAL = "/root/kot/poc/modal"
REMOTE_OUT = "/tmp/a5-llm-results"
HF_CACHE_MOUNT = "/root/.cache/huggingface"
TIMEOUT_S = 12 * 3600
GPU_CHOICES = ("T4", "A10G", "A100")

# stable relname -> local path (the exact staged-bytes set; the manifest sha
# over these is pins.harness_manifest). Kept small on purpose: the pack is
# self-contained, so no corpora/tools are staged.
STAGED = {
    "runner/a5_llm_runner.py": RUNNER,
    "runner/requirements.txt": RUNNER_REQS,
    "modal/requirements-image.txt": IMAGE_REQS,
    "inputs/a5-llm-pack.jsonl": PACK,
    "inputs/a5-llm-manifest.json": MANIFEST,
}
REMOTE_OF = {
    "runner/a5_llm_runner.py": f"{REMOTE_A5}/runner/a5_llm_runner.py",
    "runner/requirements.txt": f"{REMOTE_A5}/runner/requirements.txt",
    "modal/requirements-image.txt": f"{REMOTE_MODAL}/requirements-image.txt",
    "inputs/a5-llm-pack.jsonl": f"{REMOTE_A5}/inputs/a5-llm-pack.jsonl",
    "inputs/a5-llm-manifest.json": f"{REMOTE_A5}/inputs/a5-llm-manifest.json",
}


def _image_pins() -> list:
    if not IMAGE_REQS.exists():
        return []
    lines = IMAGE_REQS.read_text().splitlines()
    return [ln.strip() for ln in lines if ln.strip() and not ln.strip().startswith("#")]


def _manifest(path_of: dict) -> dict:
    """sha256 of each staged file, keyed by the transport-independent relname
    so the coordinator manifest == the in-container manifest (any drift => run
    fails closed, ERR_STAGING_MISMATCH)."""
    return {rel: mc.sha256_file(str(path_of[rel])) for rel in sorted(path_of)}


def _manifest_sha(man: dict) -> str:
    """pins.harness_manifest value (canonical-JSON sha256 over the staged-bytes
    manifest; f2b-replicate convention)."""
    import hashlib
    blob = json.dumps(man, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _outcome(results_dir: str) -> str:
    cands = sorted(n for n in os.listdir(results_dir)
                   if n.startswith("results-a5-llm") and n.endswith(".json"))
    if "results-a5-llm.json" in cands:
        cands = ["results-a5-llm.json"] + [c for c in cands if c != "results-a5-llm.json"]
    if not cands:
        raise SystemExit(f"ERR_NO_RESULTS: no results-a5-llm*.json in {results_dir}")
    with open(os.path.join(results_dir, cands[0])) as f:
        j = json.load(f)
    outcome = j.get("outcome")
    if not outcome:
        raise SystemExit(f"ERR_NO_OUTCOME: {cands[0]} has no 'outcome' field")
    return str(outcome)


import modal  # noqa: E402

app = modal.App("kot-a5-llm")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(*_image_pins())
    .add_local_python_source("modal_common")
    .add_local_file(RUNNER, REMOTE_OF["runner/a5_llm_runner.py"])
    .add_local_file(RUNNER_REQS, REMOTE_OF["runner/requirements.txt"])
    .add_local_file(IMAGE_REQS, REMOTE_OF["modal/requirements-image.txt"])
    .add_local_file(PACK, REMOTE_OF["inputs/a5-llm-pack.jsonl"])
    .add_local_file(MANIFEST, REMOTE_OF["inputs/a5-llm-manifest.json"])
)

hf_cache = modal.Volume.from_name("kot-hf-cache", create_if_missing=True)


def _run_in_container(gpu_requested: str, mock: bool, local_manifest: dict) -> dict:
    import subprocess

    import modal_common as cmc

    started = cmc.utcnow_iso()
    staged = _manifest(REMOTE_OF)
    if staged != local_manifest:
        diff = sorted(k for k in set(staged) | set(local_manifest)
                      if staged.get(k) != local_manifest.get(k))
        raise SystemExit(f"ERR_STAGING_MISMATCH: staged bytes differ from coordinator: {diff}")

    cmd = [
        sys.executable, REMOTE_OF["runner/a5_llm_runner.py"],
        "--pack", REMOTE_OF["inputs/a5-llm-pack.jsonl"],
        "--manifest", REMOTE_OF["inputs/a5-llm-manifest.json"],
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
        transport="modal", gpu_requested=gpu_requested, gpu_seen=cmc.gpu_info(),
        staged_manifest=staged, runner_exit=rc, started_utc=started,
        finished_utc=cmc.utcnow_iso(), packages=packages,
        environment=cmc.redact_env(dict(os.environ)),
        notes="a5-llm-raw/1 cells shipped as opaque bytes; sidecars only — the "
              "instrument --score computes the record bodies locally (run-vs-"
              "audit separation)")
    files = cmc.package_results(REMOTE_OUT, run_log=log, rc=rc, provenance=prov)
    try:
        hf_cache.commit()
    except Exception:  # noqa: BLE001
        pass
    return files


@app.function(image=image, gpu="T4", volumes={HF_CACHE_MOUNT: hf_cache}, timeout=TIMEOUT_S)
def run_a5_t4(mock: bool = False, local_manifest: dict = None) -> dict:  # noqa: RUF013
    return _run_in_container("T4", mock, local_manifest or {})


@app.function(image=image, gpu="A10G", volumes={HF_CACHE_MOUNT: hf_cache}, timeout=TIMEOUT_S)
def run_a5_a10g(mock: bool = False, local_manifest: dict = None) -> dict:  # noqa: RUF013
    return _run_in_container("A10G", mock, local_manifest or {})


@app.function(image=image, gpu="A100-40GB", volumes={HF_CACHE_MOUNT: hf_cache}, timeout=TIMEOUT_S)
def run_a5_a100(mock: bool = False, local_manifest: dict = None) -> dict:  # noqa: RUF013
    return _run_in_container("A100", mock, local_manifest or {})


GPU_FUNCTIONS = {"T4": run_a5_t4, "A10G": run_a5_a10g, "A100": run_a5_a100}


@app.local_entrypoint()
def main(gpu: str = "A10G", mock: bool = False, dry_plan: bool = False,
         out_root: str = "") -> None:
    gpu = gpu.upper()
    if gpu not in GPU_FUNCTIONS:
        raise SystemExit(f"ERR_GPU: --gpu must be one of {GPU_CHOICES}, got {gpu!r}")

    if dry_plan:
        import subprocess
        cmd = [sys.executable, str(RUNNER), "--dry-plan", "--gpu-class", gpu,
               "--pack", str(PACK), "--manifest", str(MANIFEST)]
        print(f"$ {' '.join(cmd)}")
        raise SystemExit(subprocess.call(cmd))

    local_manifest = _manifest(STAGED)
    print(f"kot-a5-llm via Modal: gpu={gpu} mock={mock} "
          f"({len(local_manifest)} staged files, runner "
          f"{local_manifest['runner/a5_llm_runner.py'][:12]}…)")
    print(f"pins.harness_manifest (staged-bytes manifest sha, canonical JSON): "
          f"{_manifest_sha(local_manifest)}")
    if not mock:
        print("REMINDER: the printed sha MUST equal the FROZEN record's "
              "pins.harness_manifest, the pre-spend gates (reuse-check --gate + "
              "dry-plan) must pass, and the maintainer Tier-1 go must hold "
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
        "modal_client": modal.__version__, "image_object_id": image_id,
        "local_manifest_matched": True, "collected_utc": mc.utcnow_iso()}
    prov_path.write_text(json.dumps(prov, indent=2, sort_keys=True) + "\n")

    outcome = _outcome(str(dest))
    rc = int((dest / mc.RUNNER_EXIT_NAME).read_text().strip().split("=", 1)[1])
    print(f"\nwrote {len(files)} files to {dest}")
    print(f"OUTCOME: {outcome}")
    if rc != 0:
        raise SystemExit(f"ERR_RUNNER: a5_llm_runner exited rc={rc} (partials + logs saved in {dest})")
    print("done — score with the instrument + log-append deliberately (results are NOT auto-committed)")


# Local (no-Modal-connection) helpers: --print-manifest for the freeze pin and
# --dry-plan for the $0 cost plan, runnable with `python3 modal_a5_llm.py ...`.
if __name__ == "__main__":
    if "--print-manifest" in sys.argv:
        man = _manifest(STAGED)
        print(json.dumps({"staged_files": man,
                          "harness_manifest_sha256": _manifest_sha(man)},
                         indent=2, sort_keys=True))
    elif "--dry-plan" in sys.argv:
        import subprocess
        gpu = "A10G"
        if "--gpu" in sys.argv:
            gpu = sys.argv[sys.argv.index("--gpu") + 1].upper()
        raise SystemExit(subprocess.call(
            [sys.executable, str(RUNNER), "--dry-plan", "--gpu-class", gpu,
             "--pack", str(PACK), "--manifest", str(MANIFEST)]))
    else:
        print("usage: python3 modal_a5_llm.py --print-manifest | --dry-plan "
              "[--gpu A10G]\n   or: modal run poc/modal/modal_a5_llm.py "
              "[--gpu a10g] [--mock] [--dry-plan]", file=sys.stderr)
        sys.exit(2)
