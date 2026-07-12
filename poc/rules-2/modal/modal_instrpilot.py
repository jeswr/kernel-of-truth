#!/usr/bin/env python3
"""RULES-2 INSTRUMENT PILOT on Modal serverless GPU (pre-freeze validity
gate; PROPOSED-ASM-1814..1819; docs/next/analysis/
correctness-track-instrument-assessment.md SS2.2 + SS4 item 1).

Wraps poc/rules-2/instr_pilot.py UNCHANGED (modal_rules2 pattern): stages
the SAME pinned campaign bytes plus the pilot runner, asserts the staged
manifest in-container (fail closed, ERR_STAGING_MISMATCH), runs the pilot,
ships its output directory back as opaque bytes with sidecar provenance.

WHY A SEPARATE WRAPPER (not a modal_rules2.py mode): the campaign's
pins.harness_manifest / pinned green mock are tied to the exact staged byte
set; the pilot must not perturb them. This wrapper's manifest ADDS
instr_pilot.py, so it has its OWN staged-bytes sha, and modal_rules2.py's
sha (d37640b2... at build time) is byte-identical before and after the
pilot build.

LAUNCH GATES — enforced by _pilot_gates(), fail-closed:
  1. a green PINNED pilot mock artifact
     (poc/rules-2/results/instrpilot-mock-validation.json) whose
     harness sha matches the staged bytes: the normal mock PASSes, the
     planted-DEGENERATE mock FAILs (the pilot's own gates have teeth), and
     the dry-plan is green;
  2. --dry-plan green at launch time: worst-case cost <= the $2 pilot cap
     (instr_pilot.PILOT_USD_CAP, exit-code enforced).
DELIBERATELY ABSENT gates (documented, not forgotten):
  - NO freeze gate: this pilot IS the pre-freeze validity check — freezing
    first would repeat the rules-1-c failure mode (freeze, spend, then
    discover the instrument was invalid). PROPOSED-ASM-1814.
  - NO rules-1-c-PASS sequencing gate: that gate (ASM-1420/1807) holds the
    CAMPAIGN's GPU tier; the assessment's ranked recommendation is explicit
    that "GPU launch stays held on #24, but the pilot ... need not wait"
    (SS4 item 1). The pilot is bounded at $2 worst-case and its result is
    an instrument-validity datum, never campaign evidence.
The CAMPAIGN launch path (modal_rules2.py) and all its gates are untouched.

    python3 poc/rules-2/modal/modal_instrpilot.py --print-manifest   # sha, $0
    .venv/bin/modal run poc/rules-2/modal/modal_instrpilot.py --dry-plan   # $0, local
    .venv/bin/modal run poc/rules-2/modal/modal_instrpilot.py --mock       # transport smoke, ~pennies
    .venv/bin/modal run poc/rules-2/modal/modal_instrpilot.py --gpu a10g   # THE pilot (single job, worst ~$0.27)

Modal hygiene (standing bd memory): nohup+setsid for the launch;
`modal app stop ap-<id>` after killing ANY attached client.
Results land in poc/rules-2/results-incoming/<UTC stamp>-instrpilot/ — NOT
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

RULES2_DIR = REPO_ROOT / "poc" / "rules-2"
PILOT_RUNNER = RULES2_DIR / "instr_pilot.py"
# campaign byte set (modal_rules2.py convention) + the pilot runner
RULES2_FILES = ("rules2_runner.py", "materialise_closure.py",
                "merge_shards.py", "instr_pilot.py")
RULES2_INPUTS = RULES2_DIR / "inputs"
C8_RESULT = RULES2_DIR / "results" / "c8-result.json"
PILOT_MOCK_ARTIFACT = RULES2_DIR / "results" / \
    "instrpilot-mock-validation.json"
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
REMOTE_OUT = "/tmp/instrpilot-results"
HF_CACHE_MOUNT = "/root/.cache/huggingface"
TIMEOUT_S = 4 * 3600  # a 4 h ceiling on a ~15 min pilot fails closed early
GPU_CHOICES = ("T4", "A10G", "A100")


def _image_pins() -> list:
    if not IMAGE_REQS.exists():
        return []
    return [ln.strip() for ln in IMAGE_REQS.read_text().splitlines()
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


def _pilot_gates(gpu: str, staged_sha: str) -> None:
    """Fail-closed pilot launch gates (see module docstring for the two
    DELIBERATELY absent campaign gates and their on-record rationale)."""
    import subprocess

    if not PILOT_MOCK_ARTIFACT.exists():
        raise SystemExit("ERR_GATE_PILOT_MOCK: %s missing — run "
                         "poc/rules-2/validate_instrpilot.py first"
                         % PILOT_MOCK_ARTIFACT)
    mv = json.loads(PILOT_MOCK_ARTIFACT.read_text())
    if not mv.get("green"):
        raise SystemExit("ERR_GATE_PILOT_MOCK: pinned pilot mock artifact "
                         "is not green")
    if mv.get("pilot_harness_manifest_sha256") != staged_sha:
        raise SystemExit("ERR_GATE_PILOT_MOCK: pinned pilot mock was "
                         "validated against harness sha %s, staged bytes "
                         "are %s — re-run validate_instrpilot.py"
                         % (str(mv.get("pilot_harness_manifest_sha256"))
                            [:16], staged_sha[:16]))

    cmd = [sys.executable, str(PILOT_RUNNER), "--dry-plan",
           "--gpu-class", gpu, "--out-dir", "/tmp/instrpilot-dry-plan",
           "--inputs-dir", str(RULES2_INPUTS),
           "--data-root", str(REPO_ROOT / "data"),
           "--corpus-dir", str(R2TRAIN_DIR)]
    if subprocess.call(cmd) != 0:
        raise SystemExit("ERR_GATE_DRYPLAN: pilot --dry-plan failed — the "
                         "$2 pilot cap would be exceeded; DO NOT LAUNCH")
    print("pilot launch gates: ALL GREEN (pinned pilot mock, dry-plan; "
          "freeze/sequencing gates deliberately absent per "
          "PROPOSED-ASM-1814 — this IS the pre-freeze gate)")


def _run_in_container(gpu_requested: str, mock: bool,
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
        sys.executable, f"{REMOTE_RULES2}/instr_pilot.py",
        "--inputs-dir", f"{REMOTE_RULES2}/inputs",
        "--data-root", REMOTE_DATA,
        "--corpus-dir", f"{REMOTE_DATA}/rules2-train",
        "--out-dir", REMOTE_OUT,
        "--device", "cpu" if mock else "cuda",
        "--gpu-class", gpu_requested,
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
    lines.append(f"[pilot exit rc={rc}]\n")
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
        notes="rules-2 INSTRUMENT PILOT (pre-freeze validity gate, "
              "PROPOSED-ASM-1814..1819); rc=3 means PILOT-FAIL (gates "
              "computed, freeze blocked) — the output bytes are shipped "
              "either way; instrument-validity rows only, never campaign "
              "evidence",
    )
    files = cmc.package_results(REMOTE_OUT, run_log=log, rc=rc,
                                provenance=prov)
    try:
        hf_cache.commit()
    except Exception:  # noqa: BLE001
        pass
    return files


if modal is not None:
    app = modal.App("kot-rules2-instrpilot")

    image = (
        modal.Image.debian_slim(python_version="3.11")
        .pip_install(*_image_pins())
        .add_local_python_source("modal_common")
        .add_local_file(RULES2_DIR / "rules2_runner.py",
                        f"{REMOTE_RULES2}/rules2_runner.py")
        .add_local_file(RULES2_DIR / "materialise_closure.py",
                        f"{REMOTE_RULES2}/materialise_closure.py")
        .add_local_file(RULES2_DIR / "merge_shards.py",
                        f"{REMOTE_RULES2}/merge_shards.py")
        .add_local_file(PILOT_RUNNER, f"{REMOTE_RULES2}/instr_pilot.py")
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
    def run_pilot_t4(mock: bool = False,
                     local_manifest: dict = None) -> dict:  # noqa: RUF013
        return _run_in_container("T4", mock, local_manifest or {})

    @app.function(image=image, gpu="A10G", volumes={HF_CACHE_MOUNT: hf_cache},
                  timeout=TIMEOUT_S)
    def run_pilot_a10g(mock: bool = False,
                       local_manifest: dict = None) -> dict:  # noqa: RUF013
        return _run_in_container("A10G", mock, local_manifest or {})

    @app.function(image=image, gpu="A100-40GB",
                  volumes={HF_CACHE_MOUNT: hf_cache}, timeout=TIMEOUT_S)
    def run_pilot_a100(mock: bool = False,
                       local_manifest: dict = None) -> dict:  # noqa: RUF013
        return _run_in_container("A100", mock, local_manifest or {})

    GPU_FUNCTIONS = {"T4": run_pilot_t4, "A10G": run_pilot_a10g,
                     "A100": run_pilot_a100}

    @app.local_entrypoint()
    def main(gpu: str = "A10G", mock: bool = False, dry_plan: bool = False,
             out_root: str = "") -> None:
        gpu = gpu.upper()
        if gpu not in GPU_FUNCTIONS:
            raise SystemExit(f"ERR_GPU: --gpu must be one of {GPU_CHOICES}, "
                             f"got {gpu!r}")

        if dry_plan:
            import subprocess
            cmd = [sys.executable, str(PILOT_RUNNER), "--dry-plan",
                   "--gpu-class", gpu,
                   "--out-dir", "/tmp/instrpilot-dry-plan",
                   "--inputs-dir", str(RULES2_INPUTS),
                   "--data-root", str(REPO_ROOT / "data"),
                   "--corpus-dir", str(R2TRAIN_DIR)]
            print(f"$ {' '.join(cmd)}")
            raise SystemExit(subprocess.call(cmd))

        local_manifest = _local_manifest()
        staged_sha = _manifest_sha(local_manifest)
        print(f"kot-rules2-instrpilot via Modal: gpu={gpu} mock={mock} "
              f"({len(local_manifest)} staged files, pilot runner "
              f"{local_manifest['poc/rules-2/instr_pilot.py'][:12]}…)")
        print(f"pilot staged-bytes manifest sha: {staged_sha}")

        if not mock:
            _pilot_gates(gpu, staged_sha)

        stamp = time.strftime("%Y%m%d-%H%M%S", time.gmtime()) + "-instrpilot"
        root = Path(out_root) / stamp if out_root else INCOMING_ROOT / stamp
        files = GPU_FUNCTIONS[gpu].remote(mock=mock,
                                          local_manifest=local_manifest)
        mc.unpack_files(files, str(root))
        rc = int((root / mc.RUNNER_EXIT_NAME).read_text()
                 .strip().split("=", 1)[1])
        res_name = ("instrpilot-result-mock.json" if mock
                    else "instrpilot-result.json")
        res_path = root / res_name
        verdict = (json.loads(res_path.read_text()).get("verdict")
                   if res_path.exists() else "MISSING-RESULT")
        print(f"\npilot done: rc={rc} verdict={verdict} -> {root}")
        print("rc semantics: 0 = gates PASS; 3 = PILOT-FAIL (freeze "
              "BLOCKED). Results are NOT auto-committed; `modal app stop "
              "ap-<id>` after every attached run")
        if rc not in (0, 3):
            raise SystemExit(f"ERR_PILOT: pilot exited rc={rc} "
                             "(neither PASS nor a computed PILOT-FAIL)")


if __name__ == "__main__":
    if "--print-manifest" in sys.argv:
        man = _local_manifest()
        print(f"staged files: {len(man)}")
        print(f"pilot staged-bytes manifest sha (canonical JSON): "
              f"{_manifest_sha(man)}")
        sys.exit(0)
    raise SystemExit("run via `modal run poc/rules-2/modal/"
                     "modal_instrpilot.py ...` or use --print-manifest")
