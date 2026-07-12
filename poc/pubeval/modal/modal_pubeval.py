#!/usr/bin/env python3
"""poc/pubeval GPU arms on Modal serverless GPU (modal_rules1 pattern).

Wraps poc/pubeval/pubeval_runner.py UNCHANGED: stages bytes, asserts the
staged manifest in-container (fail closed, ERR_STAGING_MISMATCH), runs the
runner, ships its output directory back as opaque bytes with sidecar-only
provenance (poc/modal/modal_common.py byte-identity contract).

IMAGE REUSE (PROPOSED-ASM-1106 discipline): built from the SAME
poc/modal/requirements-image.txt (sha 0fac7243…) as the pinned f2b image —
pubeval's code is repo-mounted stdlib Python; NO new dependency, no image
change. This is also why lm-evaluation-harness is not wired (README).

STATUS: exploratory infrastructure, NOT a frozen experiment — no registry
record, no pins.harness_manifest amendment; the printed staged-bytes sha is
recorded in the results sidecar for reproducibility only.

COST (inference only, LOW): A10G ≈ $1.10/h on Modal. Conservative batch-1
estimates for the full suite (folio+arc_e+arc_c+gsm8k, full splits, 5-shot;
gsm8k generation dominates — drop it or use --n for cheap passes):
    smollm2-135m ≈ 2.4 GPU-h ≈ $2.6
    smollm2-360m ≈ 3.2 GPU-h ≈ $3.6
    smollm2-1.7b ≈ 6.4 GPU-h ≈ $7.0
  Proposed worst-case cap: $10/run — --dry-plan fails closed above it.

  python3 poc/pubeval/modal/modal_pubeval.py --print-manifest      # $0, no modal
  .venv/bin/modal run poc/pubeval/modal/modal_pubeval.py --dry-plan  # $0, local
  .venv/bin/modal run poc/pubeval/modal/modal_pubeval.py --mock      # transport smoke, pennies
  .venv/bin/modal run poc/pubeval/modal/modal_pubeval.py \
      --model smollm2-135m --gpu a10g                              # real eval
  .venv/bin/modal run poc/pubeval/modal/modal_pubeval.py \
      --model smollm2-1.7b --gpu a10g \
      --transform /root/kot/poc/pubeval/transforms.py:magnitude_prune \
      --transform-kwargs '{"fraction":0.5}'                        # variant arm

Before a real run: `python3 poc/pubeval/fetch_data.py` locally so data/ is
staged (the wrapper fails closed if a non-mock run has no data directory).
Modal hygiene (standing bd memory): launch long runs nohup+setsid;
`modal app stop ap-<id>` after killing ANY attached client.

Results land in poc/pubeval/results-incoming/<UTC stamp>-modal/ — NOT
auto-committed.
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

PUBEVAL_DIR = REPO_ROOT / "poc" / "pubeval"
PUBEVAL_FILES = ("pubeval_runner.py", "benchmarks.py", "transforms.py",
                 "fetch_data.py", "test_boundary_regression.py")
DATA_DIR = PUBEVAL_DIR / "data"
IMAGE_REQS = _MODAL_TOOLS / "requirements-image.txt"
INCOMING_ROOT = PUBEVAL_DIR / "results-incoming"

REMOTE_ROOT = "/root/kot"
REMOTE_PUBEVAL = f"{REMOTE_ROOT}/poc/pubeval"
REMOTE_OUT = "/tmp/pubeval-results"
HF_CACHE_MOUNT = "/root/.cache/huggingface"
TIMEOUT_S = 8 * 3600
GPU_CHOICES = ("T4", "A10G")

_HAVE_DATA = DATA_DIR.is_dir() and any(DATA_DIR.glob("*.jsonl"))


def _image_pins() -> list:
    p = IMAGE_REQS
    if not p.exists():
        return []
    return [ln.strip() for ln in p.read_text().splitlines()
            if ln.strip() and not ln.strip().startswith("#")]


def _manifest(pubeval_dir: str, image_reqs: str, have_data: bool) -> dict:
    man = {"modal/requirements-image.txt": mc.sha256_file(image_reqs)}
    for name in PUBEVAL_FILES:
        man[f"poc/pubeval/{name}"] = mc.sha256_file(
            os.path.join(pubeval_dir, name))
    if have_data:
        data = os.path.join(pubeval_dir, "data")
        for name in sorted(os.listdir(data)):
            p = os.path.join(data, name)
            if os.path.isfile(p):
                man[f"data/{name}"] = mc.sha256_file(p)
    return man


def _manifest_sha(man: dict) -> str:
    import hashlib
    blob = json.dumps(man, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _local_manifest() -> dict:
    return _manifest(str(PUBEVAL_DIR), str(IMAGE_REQS), _HAVE_DATA)


def _run_in_container(gpu_requested: str, mock: bool, model: str,
                      benchmarks: str, n: int, shots: int, transform: str,
                      transform_kwargs: str, local_manifest: dict) -> dict:
    import subprocess

    import modal_common as cmc

    started = cmc.utcnow_iso()
    have_data = os.path.isdir(f"{REMOTE_PUBEVAL}/data")
    staged = _manifest(REMOTE_PUBEVAL,
                       f"{REMOTE_ROOT}/poc/modal/requirements-image.txt",
                       have_data)
    if staged != local_manifest:
        diff = sorted(k for k in set(staged) | set(local_manifest)
                      if staged.get(k) != local_manifest.get(k))
        raise SystemExit(
            f"ERR_STAGING_MISMATCH: staged bytes differ from coordinator: {diff}")
    if not mock and not have_data:
        raise SystemExit("ERR_NO_DATA: non-mock run but no staged data/ — "
                         "run poc/pubeval/fetch_data.py locally first")

    # Boundary-drift regression gate (cross-vendor review 2026-07-12 finding
    # #1): the torch parts (B, real brute-force loglikelihood) can only run
    # where torch exists, i.e. HERE — fail closed before spending GPU time.
    reg = subprocess.run(
        [sys.executable, f"{REMOTE_PUBEVAL}/test_boundary_regression.py"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    sys.stdout.write(reg.stdout)
    if reg.returncode != 0:
        raise SystemExit("ERR_REGRESSION_TEST: test_boundary_regression.py "
                         "rc=%d — refusing to eval" % reg.returncode)

    cmd = [
        sys.executable, f"{REMOTE_PUBEVAL}/pubeval_runner.py",
        "--model", model, "--benchmarks", benchmarks,
        "--n", str(n), "--shots", str(shots),
        "--data-dir", f"{REMOTE_PUBEVAL}/data",
        "--out-dir", REMOTE_OUT,
        "--device", "cpu" if mock else "cuda",
    ]
    if mock:
        cmd.append("--mock")
    if transform:
        cmd += ["--transform", transform]
    if transform_kwargs:
        cmd += ["--transform-kwargs", transform_kwargs]
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
        notes="pubeval public-benchmark harness (exploratory infrastructure, "
              "no frozen record); model=%s benchmarks=%s n=%d shots=%d "
              "transform=%r" % (model, benchmarks, n, shots, transform),
    )
    files = cmc.package_results(REMOTE_OUT, run_log=log, rc=rc,
                                provenance=prov)
    try:
        hf_cache.commit()
    except Exception:  # noqa: BLE001
        pass
    return files


def _dry_plan(model: str, benchmarks: str, n: int, shots: int) -> None:
    """$0 local cost plan (rough, documented assumptions; README table)."""
    sizes = {"folio": 203, "arc_easy": 2376, "arc_challenge": 1172,
             "gsm8k": 1319}
    opts = {"folio": 3, "arc_easy": 4, "arc_challenge": 4}
    man = DATA_DIR / "manifest.json"
    if man.exists():
        pinned = json.loads(man.read_text())
        for k, files in (("folio", "folio_validation.jsonl"),
                         ("arc_easy", "arc_easy_test.jsonl"),
                         ("arc_challenge", "arc_challenge_test.jsonl"),
                         ("gsm8k", "gsm8k_test.jsonl")):
            if files in pinned:
                sizes[k] = pinned[files]["rows"]
    names = [b.strip() for b in benchmarks.split(",") if b.strip()]
    fwd = gen_items = 0
    for b in names:
        count = min(sizes.get(b, 1000), n) if n > 0 else sizes.get(b, 1000)
        if b == "gsm8k":
            gen_items += count
            fwd += count  # gold-solution ppl pass
        else:
            fwd += count * opts.get(b, 4)
    # Assumptions (conservative batch-1): ~600-token forward passes; A10G
    # ~8/5/3 fwd/s for 135m/360m/1.7b; generation ~200 tok @ ~40/25/15 tok/s.
    rates = {"smollm2-135m": (8.0, 40.0), "smollm2-360m": (5.0, 25.0),
             "smollm2-1.7b": (3.0, 15.0)}
    r_fwd, r_gen = rates.get(model, (3.0, 15.0))
    hours = (fwd / r_fwd + gen_items * 200.0 / r_gen) / 3600.0
    usd = hours * 1.10
    print("DRY PLAN (rough): model=%s benchmarks=%s n=%s" % (model, benchmarks,
                                                             n or "full"))
    print("  forced-choice forwards ~%d, generations ~%d" % (fwd, gen_items))
    print("  est A10G time ~%.1f h, est cost ~$%.2f (rate $1.10/h)"
          % (hours, usd))
    print("  proposed worst-case cap: $10/run — abort if estimate exceeds it")
    if usd > 10:
        raise SystemExit("ERR_COST_CAP: estimate $%.2f > $10 cap — subsample "
                         "with --n or split the run" % usd)


if modal is not None:
    app = modal.App("kot-pubeval")

    image = (
        modal.Image.debian_slim(python_version="3.11")
        .pip_install(*_image_pins())
        .add_local_python_source("modal_common")
    )
    for _name in PUBEVAL_FILES:
        image = image.add_local_file(PUBEVAL_DIR / _name,
                                     f"{REMOTE_PUBEVAL}/{_name}")
    if _HAVE_DATA:
        image = image.add_local_dir(DATA_DIR,
                                    remote_path=f"{REMOTE_PUBEVAL}/data")
    image = image.add_local_file(IMAGE_REQS,
                                 f"{REMOTE_ROOT}/poc/modal/requirements-image.txt")

    hf_cache = modal.Volume.from_name("kot-hf-cache", create_if_missing=True)

    @app.function(image=image, gpu="T4", volumes={HF_CACHE_MOUNT: hf_cache},
                  timeout=TIMEOUT_S)
    def run_pubeval_t4(mock: bool = False, model: str = "smollm2-135m",
                       benchmarks: str = "folio,arc_easy,arc_challenge,gsm8k",
                       n: int = 0, shots: int = 5, transform: str = "",
                       transform_kwargs: str = "",
                       local_manifest: dict = None) -> dict:  # noqa: RUF013
        return _run_in_container("T4", mock, model, benchmarks, n, shots,
                                 transform, transform_kwargs,
                                 local_manifest or {})

    @app.function(image=image, gpu="A10G", volumes={HF_CACHE_MOUNT: hf_cache},
                  timeout=TIMEOUT_S)
    def run_pubeval_a10g(mock: bool = False, model: str = "smollm2-135m",
                         benchmarks: str = "folio,arc_easy,arc_challenge,gsm8k",
                         n: int = 0, shots: int = 5, transform: str = "",
                         transform_kwargs: str = "",
                         local_manifest: dict = None) -> dict:  # noqa: RUF013
        return _run_in_container("A10G", mock, model, benchmarks, n, shots,
                                 transform, transform_kwargs,
                                 local_manifest or {})

    GPU_FUNCTIONS = {"T4": run_pubeval_t4, "A10G": run_pubeval_a10g}

    @app.local_entrypoint()
    def main(gpu: str = "A10G", mock: bool = False, dry_plan: bool = False,
             model: str = "smollm2-135m",
             benchmarks: str = "folio,arc_easy,arc_challenge,gsm8k",
             n: int = 0, shots: int = 5, transform: str = "",
             transform_kwargs: str = "", out_root: str = "") -> None:
        gpu = gpu.upper()
        if gpu not in GPU_FUNCTIONS:
            raise SystemExit(f"ERR_GPU: --gpu must be one of {GPU_CHOICES}, "
                             f"got {gpu!r}")
        if dry_plan:
            _dry_plan(model, benchmarks, n, shots)
            return
        if not mock and not _HAVE_DATA:
            raise SystemExit("ERR_NO_DATA: run poc/pubeval/fetch_data.py "
                             "before a non-mock Modal run")

        local_manifest = _local_manifest()
        print(f"kot-pubeval via Modal: gpu={gpu} mock={mock} model={model} "
              f"benchmarks={benchmarks} n={n} shots={shots} "
              f"({len(local_manifest)} staged files)")
        print(f"staged-bytes manifest sha (canonical JSON): "
              f"{_manifest_sha(local_manifest)}")

        files = GPU_FUNCTIONS[gpu].remote(
            mock=mock, model=model, benchmarks=benchmarks, n=n, shots=shots,
            transform=transform, transform_kwargs=transform_kwargs,
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

        rc = int((dest / mc.RUNNER_EXIT_NAME).read_text().strip()
                 .split("=", 1)[1])
        res_name = ("results-pubeval-mock.json" if mock
                    else "results-pubeval.json")
        res = dest / res_name
        print(f"\nwrote {len(files)} files to {dest}")
        if res.exists():
            j = json.loads(res.read_text())
            print("AGGREGATE macro_acc = %.4f"
                  % j["aggregate"]["macro_acc"])
        if rc != 0:
            raise SystemExit(f"ERR_RUNNER: pubeval_runner exited rc={rc} "
                             f"(logs saved in {dest})")
        print("done — results NOT auto-committed; `modal app stop ap-<id>` "
              "after every attached run")


if __name__ == "__main__":
    if "--print-manifest" in sys.argv:
        man = _local_manifest()
        print(f"staged files: {len(man)}")
        print(f"staged-bytes manifest sha (canonical JSON): "
              f"{_manifest_sha(man)}")
        sys.exit(0)
    raise SystemExit("run via `modal run poc/pubeval/modal/modal_pubeval.py "
                     "...` or use --print-manifest")
