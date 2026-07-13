#!/usr/bin/env python3
"""UFO-CHECK-0 arms on Modal serverless GPU (registry record
registry/experiments/ufo-check-0.json; design docs/next/design/ufo-check-0.md
§8; modal_rules1.py pattern VERBATIM).

Wraps poc/ufo-check-0/ufo_check0_runner.py UNCHANGED: stages bytes, asserts
the staged manifest in-container (fail closed, ERR_STAGING_MISMATCH), runs
the runner, ships its output directory back as opaque bytes with
sidecar-only provenance.

IMAGE REUSE (PROPOSED-ASM-1106 discipline): the image is built from the SAME
poc/modal/requirements-image.txt as the pinned f2b/rules-1 images — the only
new code is repo-mounted stdlib Python; NO new dependency, no image change.
poc/f2b-transfer, poc/rules-1 and poc/f0 trees are staged BYTE-IDENTICAL
(f2bt_runner.py for the HFLM scorer + seeded retry sampler; twin_engine.py
for the pinned owl-rl core).

PINNING: pins.harness_manifest = the staged-bytes manifest sha printed by
--print-manifest (canonical JSON, P2 §1.1). The registry record itself is
staged for the runner's ERR_RUNNER_ROLE check but is EXCLUDED from the
manifest bytes — its integrity is owned by frozen_sha256/frozen-index, and
including it would make the manifest circular over the freeze status flip.

    python3 poc/ufo-check-0/modal/modal_ufo_check0.py --print-manifest  # $0
    .venv/bin/modal run poc/ufo-check-0/modal/modal_ufo_check0.py --dry-plan
    .venv/bin/modal run poc/ufo-check-0/modal/modal_ufo_check0.py --mock
    .venv/bin/modal run poc/ufo-check-0/modal/modal_ufo_check0.py --gpu a10g

LAUNCH GATES (design §10): (1) maintainer issue-#22 decision; (2) record
FROZEN; (3) green --dry-plan vs caps + green --mock; (4) fixtures
determinism proof. Modal hygiene (standing bd memory): nohup+setsid for
long runs; `modal app stop ap-<id>` after killing ANY attached client.

Results land in poc/ufo-check-0/results-incoming/<UTC stamp>-modal/ — NOT
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

UFO0_DIR = REPO_ROOT / "poc" / "ufo-check-0"
UFO0_FILES = ("ufo_check0_runner.py", "twin_ufo.py", "materialise.py",
              "gen_items.py", "power_sim.py")
UFO0_INPUTS = UFO0_DIR / "inputs"
TWIN_ENGINE = REPO_ROOT / "poc" / "rules-1" / "twin_engine.py"
F2BT_RUNNER = REPO_ROOT / "poc" / "f2b-transfer" / "runner" / "f2bt_runner.py"
F0_DIR = REPO_ROOT / "poc" / "f0"
F0_FILES = ("__init__.py", "flop_meter.py")
ITEMS_DIR = REPO_ROOT / "data" / "ufo-sn3-items-v0"
IMAGE_REQS = _MODAL_TOOLS / "requirements-image.txt"
RECORD = REPO_ROOT / "registry" / "experiments" / "ufo-check-0.json"
INCOMING_ROOT = UFO0_DIR / "results-incoming"

REMOTE_ROOT = "/root/kot"
REMOTE_UFO0 = f"{REMOTE_ROOT}/poc/ufo-check-0"
REMOTE_OUT = "/tmp/ufo0-results"
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
    for root, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for name in sorted(files):
            if name.endswith(".pyc"):
                continue
            p = os.path.join(root, name)
            rel = os.path.relpath(p, base).replace(os.sep, "/")
            man[f"{prefix}/{rel}"] = mc.sha256_file(p)


def _manifest(ufo0_dir: str, inputs_dir: str, twin_engine: str,
              f2bt_runner: str, f0_dir: str, items_dir: str,
              image_reqs: str) -> dict:
    man = {
        "poc/rules-1/twin_engine.py": mc.sha256_file(twin_engine),
        "poc/f2b-transfer/runner/f2bt_runner.py":
            mc.sha256_file(f2bt_runner),
        "modal/requirements-image.txt": mc.sha256_file(image_reqs),
    }
    for name in UFO0_FILES:
        man[f"poc/ufo-check-0/{name}"] = mc.sha256_file(
            os.path.join(ufo0_dir, name))
    for name in F0_FILES:
        man[f"poc/f0/{name}"] = mc.sha256_file(os.path.join(f0_dir, name))
    _walk_manifest(man, "inputs", inputs_dir)
    _walk_manifest(man, "data/ufo-sn3-items-v0", items_dir)
    return man


def _manifest_sha(man: dict) -> str:
    """pins.harness_manifest value (P2 §1.1 canonical-JSON convention)."""
    import hashlib
    blob = json.dumps(man, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _local_manifest() -> dict:
    return _manifest(str(UFO0_DIR), str(UFO0_INPUTS), str(TWIN_ENGINE),
                     str(F2BT_RUNNER), str(F0_DIR), str(ITEMS_DIR),
                     str(IMAGE_REQS))


def _run_in_container(gpu_requested: str, mock: bool, arms: str,
                      local_manifest: dict) -> dict:
    import subprocess

    import modal_common as cmc

    started = cmc.utcnow_iso()
    staged = _manifest(
        REMOTE_UFO0,
        f"{REMOTE_UFO0}/inputs",
        f"{REMOTE_ROOT}/poc/rules-1/twin_engine.py",
        f"{REMOTE_ROOT}/poc/f2b-transfer/runner/f2bt_runner.py",
        f"{REMOTE_ROOT}/poc/f0",
        f"{REMOTE_ROOT}/data/ufo-sn3-items-v0",
        f"{REMOTE_ROOT}/poc/modal/requirements-image.txt",
    )
    if staged != local_manifest:
        diff = sorted(k for k in set(staged) | set(local_manifest)
                      if staged.get(k) != local_manifest.get(k))
        raise SystemExit(
            f"ERR_STAGING_MISMATCH: staged bytes differ from coordinator: "
            f"{diff}")

    # --- ensure the pinned SmolLM2 tokenizer.json is discoverable in-container
    # (ERR_TOKENIZER_PIN pre-step). The runner's find_tokenizer() REQUIRES a
    # sha-pinned tokenizer.json BEFORE model load — in --mock too (it is called
    # before the mock/real branch). The mounted kot-hf-cache volume is not
    # guaranteed to hold it at the manifest's search path (prior runs warmed the
    # 135M snapshot; the manifest's default paths name the 360M snapshot).
    # SmolLM2 shares ONE tokenizer across 135M/360M, so a single file (sha-equal
    # to the pin) satisfies both hosts: fetch just that one file at the pinned
    # r360 revision into the mounted cache — it lands EXACTLY at the manifest's
    # default search path — and also pass it explicitly via --tokenizer. This
    # touches ONLY the mounted volume + the runner CLI, never the staged bytes /
    # pins.harness_manifest (this wrapper is the client-side orchestrator and is
    # excluded from the manifest, like modal_knull_run.py).
    with open(f"{REMOTE_UFO0}/inputs/manifest.json", encoding="utf-8") as _mf:
        _rman = json.load(_mf)
    _want_sha = _rman["tokenizer"]["sha256"]
    _tspec = _rman["models"]["r360"]  # shared tokenizer; r360 = manifest default
    try:
        from huggingface_hub import hf_hub_download
        tok_path = hf_hub_download(
            repo_id=_tspec["repo"], filename="tokenizer.json",
            revision=_tspec["revision"],
            cache_dir=f"{HF_CACHE_MOUNT}/hub")
    except Exception as e:  # noqa: BLE001
        raise SystemExit(
            "ERR_TOKENIZER_FETCH: could not fetch the pinned SmolLM2 "
            "tokenizer.json in-container (HF Hub unreachable?): %r" % (e,))
    _got_sha = cmc.sha256_file(tok_path)
    if _got_sha != _want_sha:
        raise SystemExit(
            "ERR_TOKENIZER_PIN: fetched %s sha %s != manifest pin %s"
            % (tok_path, _got_sha, _want_sha))
    try:
        hf_cache.commit()  # persist the tokenizer for the real --gpu run/reruns
    except Exception:  # noqa: BLE001
        pass
    print("[tokenizer] pinned SmolLM2 tokenizer.json ready at %s (sha %s…)"
          % (tok_path, _got_sha[:16]), flush=True)

    cmd = [
        sys.executable, f"{REMOTE_UFO0}/ufo_check0_runner.py",
        "--inputs-dir", f"{REMOTE_UFO0}/inputs",
        "--items", f"{REMOTE_ROOT}/data/ufo-sn3-items-v0/items.jsonl",
        "--out-dir", REMOTE_OUT,
        "--device", "cpu" if mock else "cuda",
        "--gpu-class", gpu_requested,
        "--tokenizer", tok_path,
        "--frozen-record",
        f"{REMOTE_ROOT}/registry/experiments/ufo-check-0.json",
    ]
    if arms:
        cmd += ["--arms", arms]
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
    for name in ("numpy", "torch", "transformers", "tokenizers"):
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
        notes="ufo-check-0 arms; runner outputs shipped as opaque bytes; "
              "sidecars only — see poc/modal/modal_common.py byte-identity "
              "contract; registry record staged for ERR_RUNNER_ROLE but "
              "EXCLUDED from the pinned manifest (frozen_sha256 owns it); "
              "arms=%s" % (arms or "ALL"),
    )
    files = cmc.package_results(REMOTE_OUT, run_log=log, rc=rc,
                                provenance=prov)
    try:
        hf_cache.commit()
    except Exception:  # noqa: BLE001
        pass
    return files


if modal is not None:
    app = modal.App("kot-ufo-check0")

    image = (
        modal.Image.debian_slim(python_version="3.11")
        .pip_install(*_image_pins())
        .add_local_python_source("modal_common")
    )
    for _name in UFO0_FILES:
        image = image.add_local_file(UFO0_DIR / _name,
                                     f"{REMOTE_UFO0}/{_name}")
    image = (
        image
        .add_local_file(TWIN_ENGINE,
                        f"{REMOTE_ROOT}/poc/rules-1/twin_engine.py")
        .add_local_file(F2BT_RUNNER,
                        f"{REMOTE_ROOT}/poc/f2b-transfer/runner/"
                        f"f2bt_runner.py")
        .add_local_file(F0_DIR / "__init__.py",
                        f"{REMOTE_ROOT}/poc/f0/__init__.py")
        .add_local_file(F0_DIR / "flop_meter.py",
                        f"{REMOTE_ROOT}/poc/f0/flop_meter.py")
        .add_local_dir(UFO0_INPUTS, remote_path=f"{REMOTE_UFO0}/inputs")
        .add_local_dir(ITEMS_DIR,
                       remote_path=f"{REMOTE_ROOT}/data/ufo-sn3-items-v0")
        .add_local_file(IMAGE_REQS,
                        f"{REMOTE_ROOT}/poc/modal/requirements-image.txt")
        .add_local_file(RECORD,
                        f"{REMOTE_ROOT}/registry/experiments/"
                        f"ufo-check-0.json")
    )

    hf_cache = modal.Volume.from_name("kot-hf-cache", create_if_missing=True)

    @app.function(image=image, gpu="T4", volumes={HF_CACHE_MOUNT: hf_cache},
                  timeout=TIMEOUT_S)
    def run_ufo0_t4(mock: bool = False, arms: str = "",
                    local_manifest: dict = None) -> dict:  # noqa: RUF013
        return _run_in_container("T4", mock, arms, local_manifest or {})

    @app.function(image=image, gpu="A10G",
                  volumes={HF_CACHE_MOUNT: hf_cache}, timeout=TIMEOUT_S)
    def run_ufo0_a10g(mock: bool = False, arms: str = "",
                      local_manifest: dict = None) -> dict:  # noqa: RUF013
        return _run_in_container("A10G", mock, arms, local_manifest or {})

    @app.function(image=image, gpu="A100-40GB",
                  volumes={HF_CACHE_MOUNT: hf_cache}, timeout=TIMEOUT_S)
    def run_ufo0_a100(mock: bool = False, arms: str = "",
                      local_manifest: dict = None) -> dict:  # noqa: RUF013
        return _run_in_container("A100", mock, arms, local_manifest or {})

    GPU_FUNCTIONS = {"T4": run_ufo0_t4, "A10G": run_ufo0_a10g,
                     "A100": run_ufo0_a100}

    @app.local_entrypoint()
    def main(gpu: str = "A10G", mock: bool = False, dry_plan: bool = False,
             arms: str = "", out_root: str = "") -> None:
        gpu = gpu.upper()
        if gpu not in GPU_FUNCTIONS:
            raise SystemExit(f"ERR_GPU: --gpu must be one of {GPU_CHOICES}, "
                             f"got {gpu!r}")

        if dry_plan:
            import subprocess
            cmd = [sys.executable,
                   str(UFO0_DIR / "ufo_check0_runner.py"), "--dry-plan",
                   "--gpu-class", gpu, "--out-dir", "/tmp/ufo0-dry-plan",
                   "--inputs-dir", str(UFO0_INPUTS)]
            print(f"$ {' '.join(cmd)}")
            raise SystemExit(subprocess.call(cmd))

        local_manifest = _local_manifest()
        print(f"kot-ufo-check0 via Modal: gpu={gpu} mock={mock} "
              f"arms={arms or 'ALL'} ({len(local_manifest)} staged files)")
        print(f"pins.harness_manifest (staged-bytes manifest sha, canonical "
              f"JSON): {_manifest_sha(local_manifest)}")
        if not mock:
            print("REMINDER: the printed sha MUST equal the FROZEN record's "
                  "pins.harness_manifest; the record must be FROZEN "
                  "(ERR_RUNNER_ROLE enforces this in-container); dry-plan + "
                  "mock must be green; the issue-#22 HOLD must be released.")

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
        prov_path.write_text(json.dumps(prov, indent=2, sort_keys=True)
                             + "\n")

        rc = int((dest / mc.RUNNER_EXIT_NAME).read_text().strip()
                 .split("=", 1)[1])
        print(f"\nwrote {len(files)} files to {dest}")
        if rc != 0:
            raise SystemExit(f"ERR_RUNNER: ufo_check0_runner exited rc={rc} "
                             f"(partials + logs saved in {dest})")
        print("done — review and commit deliberately (results are NOT "
              "auto-committed); `modal app stop ap-<id>` after every "
              "attached run")


if __name__ == "__main__":
    # sha-only path: works with NO modal install, NO network, $0 — this is
    # what pins.harness_manifest records.
    if "--print-manifest" in sys.argv:
        man = _local_manifest()
        print(f"staged files: {len(man)}")
        print(f"pins.harness_manifest (staged-bytes manifest sha, canonical "
              f"JSON): {_manifest_sha(man)}")
        sys.exit(0)
    raise SystemExit("run via `modal run poc/ufo-check-0/modal/"
                     "modal_ufo_check0.py ...` or use --print-manifest")
