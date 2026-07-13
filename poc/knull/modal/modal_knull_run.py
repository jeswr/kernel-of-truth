#!/usr/bin/env python3
"""knull-v2 CAMPAIGN on Modal serverless GPU — the verdict-bearing run
transport for the FROZEN record registry/experiments/knull-v2.json.

Wraps poc/knull/runner/knull_runner_v2.py UNCHANGED (the modal_f2b pattern):
stages bytes, asserts the staged manifest in-container (fail closed,
ERR_STAGING_MISMATCH), runs the runner as a subprocess, ships its output
directory back as opaque bytes with sidecar-only provenance
(provenance-modal.json, run log, RUNNER_EXIT). The runner re-verifies every
frozen pin in-container before touching a model (KNULL2_ERR_*), so a stale
or tampered staging can never produce records.

GPU: A100-40GB — knull-v2.json runner_constraints.hardware verbatim
("1x A100-40GB (f2b image, I-MODAL rebuild)"); image built from the pinned
poc/modal/requirements-image.txt (the f2b image recipe). Models load at the
record-pinned revisions (SmolLM2-135M verify host / 1.7B bridge baseline)
from the shared kot-hf-cache volume (already warm from f2b).

CHECKPOINT/RESUME across containers: the runner's per-item checkpoint dir
lives on the kot-knull-v2-ckpt Volume under /ckpt/<tag>/<arms-slug>, with a
background committer thread persisting it every 120 s — a preempted or
killed container is relaunched with the SAME --tag and --arms and resumes at
the first missing item ($~0 rework).

ACCOUNT FAN (README-knull-v2-run.md): one process per Modal account, each a
disjoint --arms slice (kernel / plain / plain-padded / opaque); slices are
merged by poc/knull/runner/merge_knull_slices.py, which fail-closes unless
the union is exactly the frozen 36-cell plan.

    # $0, no modal import, no network — staged-bytes sha for the run log:
    python3 poc/knull/modal/modal_knull_run.py --print-manifest

    # $0 local cost plan vs the frozen caps (usd 60 / gpu-h 8 / wall 24):
    poc/modal/.venv/bin/modal run poc/knull/modal/modal_knull_run.py --dry-plan

    # transport smoke, CPU container, stub LM (~pennies, loudly MOCK):
    poc/modal/.venv/bin/modal run poc/knull/modal/modal_knull_run.py --mock

    # THE CAMPAIGN (coordinator only; frozen record + caps enforced):
    poc/modal/.venv/bin/modal run poc/knull/modal/modal_knull_run.py \
        --confirm-spend --arms kernel --tag <campaign-tag>

Results land in poc/knull/results-incoming/<UTC stamp>-modal-knull2-<slug>/
— NOT auto-committed. Standing memory (E5 lesson): a killed client does NOT
stop the remote task — `modal app stop ap-<id>` under the launching
account's env; launch long runs with nohup+setsid.
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

KNULL_DIR = REPO_ROOT / "poc" / "knull"
RUNNER = KNULL_DIR / "runner" / "knull_runner_v2.py"
F2B_RUNNER = REPO_ROOT / "poc" / "f2b" / "runner" / "f2b_runner.py"
F2B_INPUTS = REPO_ROOT / "poc" / "f2b" / "inputs"
F0_DIR = REPO_ROOT / "poc" / "f0"
F0_FILES = ("__init__.py", "flop_meter.py")   # staged file-by-file (no pyc)
INPUTS_V4 = KNULL_DIR / "inputs-v4"
KERNEL_DIR = REPO_ROOT / "data" / "kernel-v0"
MOLECULES_DIR = REPO_ROOT / "data" / "molecules-v0"
RECORD = REPO_ROOT / "registry" / "experiments" / "knull-v2.json"
FROZEN_INDEX = REPO_ROOT / "registry" / "frozen-index.json"
SAP = REPO_ROOT / "analysis" / "knull_v3.py"
IMAGE_REQS = _MODAL_TOOLS / "requirements-image.txt"
INCOMING_ROOT = KNULL_DIR / "results-incoming"

REMOTE_ROOT = "/root/kot"
REMOTE_OUT = "/tmp/knull2-out"
CKPT_MOUNT = "/ckpt"
HF_CACHE_MOUNT = "/root/.cache/huggingface"
TIMEOUT_S = 12 * 3600   # << wall_clock_cap_hours 24 (knull-v2.json budget)
VALID_ARMS = ("kernel", "plain", "plain-padded", "opaque")


def _image_pins() -> list:
    lines = IMAGE_REQS.read_text().splitlines()
    return [ln.strip() for ln in lines
            if ln.strip() and not ln.strip().startswith("#")]


def _walk_manifest(man: dict, prefix: str, base: str) -> None:
    """__pycache__/*.pyc excluded on BOTH sides (volatile, not corpus bytes)."""
    for root, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for name in sorted(files):
            if name.endswith(".pyc"):
                continue
            p = os.path.join(root, name)
            rel = os.path.relpath(p, base).replace(os.sep, "/")
            man[f"{prefix}/{rel}"] = mc.sha256_file(p)


def _manifest(runner, f2b_runner, f2b_inputs, f0_dir, inputs_v4, kernel,
              molecules, record, frozen_index, sap, image_reqs) -> dict:
    man = {
        "runner/knull_runner_v2.py": mc.sha256_file(runner),
        "f2b/runner/f2b_runner.py": mc.sha256_file(f2b_runner),
        "registry/experiments/knull-v2.json": mc.sha256_file(record),
        "registry/frozen-index.json": mc.sha256_file(frozen_index),
        "analysis/knull_v3.py": mc.sha256_file(sap),
        "modal/requirements-image.txt": mc.sha256_file(image_reqs),
    }
    for name in F0_FILES:
        man[f"poc/f0/{name}"] = mc.sha256_file(os.path.join(f0_dir, name))
    _walk_manifest(man, "f2b/inputs", f2b_inputs)
    _walk_manifest(man, "inputs-v4", inputs_v4)
    _walk_manifest(man, "data/kernel-v0", kernel)
    _walk_manifest(man, "data/molecules-v0", molecules)
    return man


def _local_manifest() -> dict:
    return _manifest(str(RUNNER), str(F2B_RUNNER), str(F2B_INPUTS),
                     str(F0_DIR), str(INPUTS_V4), str(KERNEL_DIR),
                     str(MOLECULES_DIR), str(RECORD), str(FROZEN_INDEX),
                     str(SAP), str(IMAGE_REQS))


def _manifest_sha(man: dict) -> str:
    """Canonical-JSON sha of the staged-bytes manifest — record this value in
    the campaign run-log at launch (the f2b re-pin-at-campaign-start pattern
    the frozen record's harness_manifest anticipates)."""
    import hashlib
    blob = json.dumps(man, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _arms_slug(arms: str) -> str:
    return "-".join(a.strip().replace("plain-padded", "plainpadded")
                    for a in arms.split(",") if a.strip())


def _run_in_container(mock: bool, arms: str, tag: str,
                      local_manifest: dict, ckpt_vol=None) -> dict:
    import subprocess
    import threading

    import modal_common as cmc

    started = cmc.utcnow_iso()
    staged = _manifest(
        f"{REMOTE_ROOT}/poc/knull/runner/knull_runner_v2.py",
        f"{REMOTE_ROOT}/poc/f2b/runner/f2b_runner.py",
        f"{REMOTE_ROOT}/poc/f2b/inputs",
        f"{REMOTE_ROOT}/poc/f0",
        f"{REMOTE_ROOT}/poc/knull/inputs-v4",
        f"{REMOTE_ROOT}/data/kernel-v0",
        f"{REMOTE_ROOT}/data/molecules-v0",
        f"{REMOTE_ROOT}/registry/experiments/knull-v2.json",
        f"{REMOTE_ROOT}/registry/frozen-index.json",
        f"{REMOTE_ROOT}/analysis/knull_v3.py",
        f"{REMOTE_ROOT}/poc/modal/requirements-image.txt",
    )
    if staged != local_manifest:
        diff = sorted(k for k in set(staged) | set(local_manifest)
                      if staged.get(k) != local_manifest.get(k))
        raise SystemExit("ERR_STAGING_MISMATCH: staged bytes differ from "
                         f"coordinator: {diff}")

    ckpt_dir = os.path.join(CKPT_MOUNT, "knull-v2", tag, _arms_slug(arms))
    os.makedirs(ckpt_dir, exist_ok=True)

    # background committer: persist per-item checkpoints across preemption
    stop = threading.Event()

    def _committer():
        while not stop.wait(120.0):
            if ckpt_vol is not None:
                try:
                    ckpt_vol.commit()
                except Exception:  # noqa: BLE001
                    pass

    t = threading.Thread(target=_committer, daemon=True)
    t.start()

    cmd = [sys.executable,
           f"{REMOTE_ROOT}/poc/knull/runner/knull_runner_v2.py",
           "--arms", arms, "--out-dir", REMOTE_OUT,
           "--checkpoint-dir", ckpt_dir]
    if mock:
        cmd += ["--mock", "--items", "60", "--device", "cpu"]
    else:
        cmd += ["--real", "--confirm-spend", "--device", "cuda",
                "--gpu-class", "A100"]
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
    stop.set()

    packages = {}
    for name in ("numpy", "torch", "transformers"):
        try:
            packages[name] = __import__(name).__version__
        except Exception as e:  # noqa: BLE001
            packages[name] = f"unavailable: {e}"

    prov = cmc.build_provenance(
        transport="modal",
        gpu_requested="none (CPU mock)" if mock else "A100-40GB",
        gpu_seen=cmc.gpu_info(),
        staged_manifest=staged,
        runner_exit=rc,
        started_utc=started,
        finished_utc=cmc.utcnow_iso(),
        packages=packages,
        environment=cmc.redact_env(dict(os.environ)),
        notes="knull-v2 campaign slice arms=%s tag=%s; runner outputs "
              "shipped as opaque bytes, sidecars only; per-item checkpoints "
              "on the kot-knull-v2-ckpt volume at %s" % (arms, tag, ckpt_dir),
    )
    files = cmc.package_results(REMOTE_OUT, run_log="".join(lines), rc=rc,
                                provenance=prov)
    for vol in (ckpt_vol, hf_cache if not mock else None):
        try:
            if vol is not None:
                vol.commit()
        except Exception:  # noqa: BLE001
            pass
    return files


if modal is not None:
    app = modal.App("kot-knull-v2")

    image = (
        modal.Image.debian_slim(python_version="3.11")
        .pip_install(*_image_pins())
        .add_local_python_source("modal_common")
        .add_local_file(RUNNER,
                        f"{REMOTE_ROOT}/poc/knull/runner/knull_runner_v2.py")
        .add_local_file(F2B_RUNNER,
                        f"{REMOTE_ROOT}/poc/f2b/runner/f2b_runner.py")
        .add_local_file(F0_DIR / "__init__.py",
                        f"{REMOTE_ROOT}/poc/f0/__init__.py")
        .add_local_file(F0_DIR / "flop_meter.py",
                        f"{REMOTE_ROOT}/poc/f0/flop_meter.py")
        .add_local_dir(F2B_INPUTS, remote_path=f"{REMOTE_ROOT}/poc/f2b/inputs")
        .add_local_dir(INPUTS_V4,
                       remote_path=f"{REMOTE_ROOT}/poc/knull/inputs-v4")
        .add_local_dir(KERNEL_DIR, remote_path=f"{REMOTE_ROOT}/data/kernel-v0")
        .add_local_dir(MOLECULES_DIR,
                       remote_path=f"{REMOTE_ROOT}/data/molecules-v0")
        .add_local_file(RECORD,
                        f"{REMOTE_ROOT}/registry/experiments/knull-v2.json")
        .add_local_file(FROZEN_INDEX,
                        f"{REMOTE_ROOT}/registry/frozen-index.json")
        .add_local_file(SAP, f"{REMOTE_ROOT}/analysis/knull_v3.py")
        .add_local_file(IMAGE_REQS,
                        f"{REMOTE_ROOT}/poc/modal/requirements-image.txt")
    )

    hf_cache = modal.Volume.from_name("kot-hf-cache", create_if_missing=True)
    ckpt_vol = modal.Volume.from_name("kot-knull-v2-ckpt",
                                      create_if_missing=True)

    @app.function(image=image, gpu="A100-40GB", timeout=TIMEOUT_S,
                  volumes={HF_CACHE_MOUNT: hf_cache, CKPT_MOUNT: ckpt_vol})
    def run_knull_a100(arms: str, tag: str,
                       local_manifest: dict = None) -> dict:  # noqa: RUF013
        return _run_in_container(False, arms, tag, local_manifest or {},
                                 ckpt_vol=ckpt_vol)

    @app.function(image=image, cpu=8.0, memory=8192, timeout=TIMEOUT_S,
                  volumes={CKPT_MOUNT: ckpt_vol})
    def run_knull_mock(arms: str, tag: str,
                       local_manifest: dict = None) -> dict:  # noqa: RUF013
        return _run_in_container(True, arms, tag, local_manifest or {},
                                 ckpt_vol=ckpt_vol)

    @app.local_entrypoint()
    def main(arms: str = "kernel,plain,plain-padded,opaque",
             mock: bool = False, dry_plan: bool = False,
             confirm_spend: bool = False, tag: str = "campaign-1",
             out_root: str = "") -> None:
        bad = [a for a in arms.split(",") if a.strip() not in VALID_ARMS]
        if bad or not arms.strip():
            raise SystemExit(f"ERR_ARMS: unknown arms {bad} "
                             f"(valid: {VALID_ARMS})")

        if dry_plan:
            import subprocess
            cmd = [sys.executable, str(RUNNER), "--dry-plan", "--arms", arms]
            print(f"$ {' '.join(cmd)}")
            raise SystemExit(subprocess.call(cmd))

        local_manifest = _local_manifest()
        sha = _manifest_sha(local_manifest)
        print(f"kot-knull-v2 via Modal: arms={arms} mock={mock} tag={tag} "
              f"({len(local_manifest)} staged files)")
        print(f"staged-bytes manifest sha (record in the campaign run-log): "
              f"{sha}")
        if not mock:
            if not confirm_spend:
                raise SystemExit(
                    "ERR_SPEND: real campaign requires --confirm-spend "
                    "(coordinator only; knull-v2 caps usd 60 / gpu-h 8 / "
                    "wall 24 h; maintainer sign-off per "
                    "runner_constraints.gate)")
            print("REMINDER: registry/experiments/knull-v2.json is FROZEN; "
                  "the in-container runner fail-closes on every pin "
                  "(KNULL2_ERR_*). Do not edit staged bytes mid-campaign.")
            files = run_knull_a100.remote(arms=arms, tag=tag,
                                          local_manifest=local_manifest)
        else:
            files = run_knull_mock.remote(arms=arms, tag=tag,
                                          local_manifest=local_manifest)

        stamp = time.strftime("%Y%m%d-%H%M%S", time.gmtime())
        slug = ("mock-" if mock else "") + _arms_slug(arms)
        dest = (Path(out_root) if out_root else INCOMING_ROOT) / \
            f"{stamp}-modal-knull2-{slug}"
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
            "staged_manifest_sha": sha,
            "local_manifest_matched": True,
            "campaign_tag": tag,
            "arms": arms,
            "collected_utc": mc.utcnow_iso(),
        }
        prov_path.write_text(json.dumps(prov, indent=2, sort_keys=True) + "\n")

        rc = int((dest / mc.RUNNER_EXIT_NAME).read_text()
                 .strip().split("=", 1)[1])
        print(f"\nwrote {len(files)} files to {dest}")
        if rc != 0:
            raise SystemExit(
                f"ERR_RUNNER: knull_runner_v2 exited rc={rc} — partials + "
                f"logs saved in {dest}; per-item checkpoints persist on the "
                f"kot-knull-v2-ckpt volume: relaunch with the SAME --tag and "
                f"--arms to resume")
        print("slice complete — merge all four slices with "
              "poc/knull/runner/merge_knull_slices.py, then run the pinned "
              "analysis/knull_v3.py (results are NOT auto-committed)")


if __name__ == "__main__":
    if "--print-manifest" in sys.argv:
        man = _local_manifest()
        print(f"staged files: {len(man)}")
        print(f"manifest sha: {_manifest_sha(man)}")
        for k, v in sorted(man.items()):
            if not k.startswith(("data/", "inputs-v4/stores",
                                 "inputs-v4/items")):
                print(f"  {k}  {v}")
        sys.exit(0)
    raise SystemExit("run via `modal run poc/knull/modal/modal_knull_run.py "
                     "[--mock|--dry-plan|--confirm-spend] [--arms ...]` or "
                     "use --print-manifest")
