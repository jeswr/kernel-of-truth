#!/usr/bin/env python3
"""E8 kernel<->SAE alignment extraction on Modal (bead kernel-of-truth-u0x).

Design pin: poc/e8/README.md (fixed before build). Transport pattern:
modal_e2_reanalysis.py — same pinned image (requirements-image.txt UNCHANGED;
safetensors + huggingface_hub arrive transitively via transformers), same
kot-hf-cache volume, sha-asserted staging, provenance sidecars. The container
subprocesses the UNCHANGED poc/e8/runner/e8_runner.py; NO statistics happen
on the GPU — analysis runs on the CPU box (poc/e8/analyze.py), auditable and
re-runnable without spend.

    .venv/bin/python poc/modal/modal_e8.py --dry-plan   # plan + $ — NO token
    .venv/bin/modal run poc/modal/modal_e8.py --mock    # transport smoke, ~pennies
    .venv/bin/modal run poc/modal/modal_e8.py           # THE run (T4, ~$0.10-0.50)
    .venv/bin/modal run poc/modal/modal_e8.py --ext1    # extension 1: family C only
                                                        # (then poc/e8/analyze_ext1.py)

Results land in poc/e8/results-incoming/<UTC stamp>-modal/ — NOT
auto-committed; review, run analyze.py, commit deliberately (E2 discipline).
"""

from __future__ import annotations

import json
import subprocess
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
E8_DIR = REPO_ROOT / "poc" / "e8"
E8_RUNNER = E8_DIR / "runner" / "e8_runner.py"
E8_MANIFEST = E8_DIR / "inputs" / "e8-manifest.json"
E8_MANIFEST_EXT1 = E8_DIR / "inputs" / "e8-manifest-ext1.json"
E2_RUNNER = REPO_ROOT / "poc" / "e2" / "runner" / "e2_runner.py"
E2_ITEMS = REPO_ROOT / "poc" / "e2" / "inputs" / "items.json"
E2_CONTEXTS = REPO_ROOT / "poc" / "e2" / "inputs" / "contexts.json"
INCOMING_ROOT = E8_DIR / "results-incoming"

# ---- container-side layout ---------------------------------------------------
REMOTE_KOT = "/root/kot/poc"
REMOTE_E8_RUNNER = f"{REMOTE_KOT}/e8/runner/e8_runner.py"
REMOTE_E8_MANIFEST = f"{REMOTE_KOT}/e8/inputs/e8-manifest.json"
REMOTE_E8_MANIFEST_EXT1 = f"{REMOTE_KOT}/e8/inputs/e8-manifest-ext1.json"
REMOTE_E2_RUNNER = f"{REMOTE_KOT}/e2/runner/e2_runner.py"
REMOTE_E2_INPUTS = f"{REMOTE_KOT}/e2/inputs"
REMOTE_OUT = "/tmp/e8-out"
HF_CACHE_MOUNT = "/root/.cache/huggingface"
TIMEOUT_S = 3600  # extraction is minutes; 1 h failsafe

# Cost model for --dry-plan (Modal on-demand list prices, 2026-07: T4
# $0.000164/s ~= $0.59/h; + CPU/mem overhead — call it $0.75/h loaded).
DOLLARS_PER_HOUR_LOADED = 0.75
COLD_MINUTES = (5, 15)   # downloads ~1.28 GB (volume) + extraction
WARM_MINUTES = (2, 8)


def _staged_manifest() -> dict:
    return {
        "e8/runner/e8_runner.py": mc.sha256_file(str(E8_RUNNER)),
        "e8/inputs/e8-manifest.json": mc.sha256_file(str(E8_MANIFEST)),
        "e8/inputs/e8-manifest-ext1.json": mc.sha256_file(str(E8_MANIFEST_EXT1)),
        "e2/runner/e2_runner.py": mc.sha256_file(str(E2_RUNNER)),
        "e2/inputs/items.json": mc.sha256_file(str(E2_ITEMS)),
        "e2/inputs/contexts.json": mc.sha256_file(str(E2_CONTEXTS)),
    }


def _image_pins() -> list:
    p = _HERE / "requirements-image.txt"
    if not p.exists():  # container-side re-import: image already built
        return []
    return [ln.strip() for ln in p.read_text().splitlines()
            if ln.strip() and not ln.strip().startswith("#")]


app = modal.App("kot-e8")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(*_image_pins())
    .add_local_python_source("modal_common")
    .add_local_file(E8_RUNNER, REMOTE_E8_RUNNER)
    .add_local_file(E8_MANIFEST, REMOTE_E8_MANIFEST)
    .add_local_file(E8_MANIFEST_EXT1, REMOTE_E8_MANIFEST_EXT1)
    .add_local_file(E2_RUNNER, REMOTE_E2_RUNNER)
    .add_local_file(E2_ITEMS, f"{REMOTE_E2_INPUTS}/items.json")
    .add_local_file(E2_CONTEXTS, f"{REMOTE_E2_INPUTS}/contexts.json")
)

hf_cache = modal.Volume.from_name("kot-hf-cache", create_if_missing=True)


def _run_in_container(local_manifest: dict, mock: bool, ext1: bool = False) -> dict:
    import os

    import modal_common as cmc

    started = cmc.utcnow_iso()
    staged = {
        "e8/runner/e8_runner.py": cmc.sha256_file(REMOTE_E8_RUNNER),
        "e8/inputs/e8-manifest.json": cmc.sha256_file(REMOTE_E8_MANIFEST),
        "e8/inputs/e8-manifest-ext1.json": cmc.sha256_file(REMOTE_E8_MANIFEST_EXT1),
        "e2/runner/e2_runner.py": cmc.sha256_file(REMOTE_E2_RUNNER),
        "e2/inputs/items.json": cmc.sha256_file(f"{REMOTE_E2_INPUTS}/items.json"),
        "e2/inputs/contexts.json": cmc.sha256_file(f"{REMOTE_E2_INPUTS}/contexts.json"),
    }
    if staged != local_manifest:
        diff = sorted(k for k in set(staged) | set(local_manifest)
                      if staged.get(k) != local_manifest.get(k))
        raise SystemExit(f"ERR_STAGING_MISMATCH: staged bytes differ from coordinator: {diff}")

    # transitive-dep sanity: fail before any download if the pinned image
    # unexpectedly lacks what direct-safetensors loading needs
    import huggingface_hub  # noqa: F401
    import safetensors  # noqa: F401

    cmd = [sys.executable, REMOTE_E8_RUNNER,
           "--e2-inputs-dir", REMOTE_E2_INPUTS,
           "--manifest", REMOTE_E8_MANIFEST_EXT1 if ext1 else REMOTE_E8_MANIFEST,
           "--out-dir", REMOTE_OUT,
           "--device", "cpu" if mock else "cuda"]
    if mock:
        cmd.append("--mock")
    lines = [f"$ {' '.join(cmd)}\n"]
    with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                          text=True, bufsize=1) as proc:
        assert proc.stdout is not None
        for line in proc.stdout:
            lines.append(line)
            print(line, end="", flush=True)
    rc = proc.returncode
    lines.append(f"[runner exit rc={rc}]\n")
    if rc != 0:
        raise SystemExit(f"ERR_RUNNER: e8_runner exited rc={rc}")

    packages = {}
    for pkg in ("numpy", "torch", "transformers", "safetensors", "huggingface_hub"):
        try:
            packages[pkg] = __import__(pkg).__version__
        except Exception as e:  # provenance must never kill a finished run
            packages[pkg] = f"unavailable: {e}"

    prov = cmc.build_provenance(
        transport="modal",
        gpu_requested="T4" if not mock else "T4 (mock: cpu extraction)",
        gpu_seen=cmc.gpu_info(),
        staged_manifest=staged,
        runner_exit=rc,
        started_utc=started,
        finished_utc=cmc.utcnow_iso(),
        packages=packages,
        environment=cmc.redact_env(dict(os.environ)),
        notes="E8 extraction only; statistics run on the CPU box (poc/e8/analyze.py); "
              "SAE + model HF revisions pinned in e8-manifest.json and echoed in "
              "e8-extraction.json 'resolved' blocks",
    )
    files = cmc.package_results(REMOTE_OUT, run_log="".join(lines), rc=rc, provenance=prov)
    try:
        hf_cache.commit()
    except Exception:
        pass
    return files


@app.function(image=image, gpu="T4", volumes={HF_CACHE_MOUNT: hf_cache}, timeout=TIMEOUT_S)
def run_e8_t4(local_manifest: dict = None, mock: bool = False, ext1: bool = False) -> dict:  # noqa: RUF013
    return _run_in_container(local_manifest or {}, mock, ext1)


def _print_plan() -> None:
    man = json.loads(E8_MANIFEST.read_text())
    staged = _staged_manifest()
    dl = man["downloadPlanBytes"]
    total_gb = (dl["models"] + dl["saes"]) / 1e9
    print("kot-e8 --dry-plan (NO Modal calls)")
    print(f"  staged files ({len(staged)}):")
    for k, v in staged.items():
        print(f"    {k}  sha256 {v[:12]}…")
    print("  families:")
    for name, fam in man["families"].items():
        print(f"    {name}: {fam['model_id']} @ {fam['model_revision'][:10]} + "
              f"{fam['sae_repo']}:{fam['sae_file']} @ {fam['sae_revision'][:10]} "
              f"({fam['sae_file_bytes'] / 1e6:.0f} MB, {fam['sae_arch']})")
    print(f"  downloads: {total_gb:.2f} GB -> Modal volume kot-hf-cache (NOT this box)")
    print("  call graph: run_e8_t4.remote() -> staging assert -> subprocess e8_runner.py "
          "-> package_results -> unpack to poc/e8/results-incoming/<stamp>-modal/")
    lo = COLD_MINUTES[0] * DOLLARS_PER_HOUR_LOADED / 60
    hi = COLD_MINUTES[1] * DOLLARS_PER_HOUR_LOADED / 60
    wlo = WARM_MINUTES[0] * DOLLARS_PER_HOUR_LOADED / 60
    whi = WARM_MINUTES[1] * DOLLARS_PER_HOUR_LOADED / 60
    print(f"  estimate (T4, ~${DOLLARS_PER_HOUR_LOADED:.2f}/h loaded): "
          f"cold {COLD_MINUTES[0]}-{COLD_MINUTES[1]} min ~= ${lo:.2f}-{hi:.2f}; "
          f"warm {WARM_MINUTES[0]}-{WARM_MINUTES[1]} min ~= ${wlo:.2f}-{whi:.2f}")
    print("  run: .venv/bin/modal run poc/modal/modal_e8.py    (coordinator-gated)")
    print("  then: python3 poc/e8/analyze.py poc/e8/results-incoming/<stamp>-modal")
    if E8_MANIFEST_EXT1.exists():
        m1 = json.loads(E8_MANIFEST_EXT1.read_text())
        dl1 = m1["downloadPlanBytes"]
        print(f"  ext1 (family C only, {(dl1['models'] + dl1['saes']) / 1e9:.2f} GB): "
              "run with --ext1, then poc/e8/analyze_ext1.py; pairs "
              f"{m1['pairs']}")


@app.local_entrypoint()
def main(mock: bool = False, ext1: bool = False, out_root: str = "") -> None:
    local_manifest = _staged_manifest()
    print(f"kot-e8 via Modal: T4, {len(local_manifest)} staged files, "
          f"manifest {local_manifest['e8/inputs/e8-manifest.json'][:12]}… mock={mock} ext1={ext1}")

    files = run_e8_t4.remote(local_manifest=local_manifest, mock=mock, ext1=ext1)

    stamp = (time.strftime("%Y%m%d-%H%M%S", time.gmtime())
             + ("-mock" if mock else "") + ("-ext1" if ext1 else "") + "-modal")
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
    print(f"\nwrote {len(files)} files to {dest}")
    print(f"next: python3 poc/e8/{'analyze_ext1' if ext1 else 'analyze'}.py " + str(dest))


if __name__ == "__main__":
    # Token-free entry: `python3 modal_e8.py --dry-plan` prints staged pins,
    # download plan and the $ estimate with ZERO Modal calls.
    import argparse
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-plan", action="store_true")
    args = ap.parse_args()
    if not args.dry_plan:
        raise SystemExit("direct execution supports --dry-plan only; "
                         "use `modal run poc/modal/modal_e8.py` for real runs")
    _print_plan()
