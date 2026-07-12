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
    python3 poc/rules-2/modal/modal_rules2.py --print-jobs        # shard plan, $0
    .venv/bin/modal run poc/rules-2/modal/modal_rules2.py --dry-plan          # cost plan, $0, local
    .venv/bin/modal run poc/rules-2/modal/modal_rules2.py --mock              # transport smoke, ~pennies
    .venv/bin/modal run poc/rules-2/modal/modal_rules2.py --gpu a10g          # DEFAULT R1 tier (all 14 shards, parallel)
    .venv/bin/modal run poc/rules-2/modal/modal_rules2.py --gpu a10g --jobs b2-r1-s1,b2-r1-s2   # subset (multi-account split)
    .venv/bin/modal run poc/rules-2/modal/modal_rules2.py --gpu a10g --rungs R2 --authorize-r2  # R2 tier (second launch)

SHARDED PARALLEL LAUNCH (REWORK-2, review item 9 + the standing
parallel-launch directive): the campaign is a set of INDEPENDENT jobs —
one per (FT arm x seed), one per eval-only arm (see --print-jobs; B4 is
STRUCK per the maintainer's issue #24 decision (C) + the blocking pilot's
IP-4 vacuity flag) — spawned CONCURRENTLY as separate Modal function calls.
No single job approaches the 12 h function timeout (worst ~1.3 h planned).
--jobs runs a named subset, so the shard set can be split across Modal
accounts/workspaces; every shard ships its own results directory and
poc/rules-2/merge_shards.py reconstructs the canonical results pair for
the pinned analysis (fail-closed cross-shard pin/surface assertions).

LAUNCH GATES — ENFORCED PROGRAMMATICALLY by _launch_gates() (fail-closed;
review item 9 replaced the old advisory reminder), full path only:
  1. registry/experiments/rules-2.json status FROZEN and the staged-bytes
     manifest sha recorded in its pins.harness_manifest;
  2. sequencing (PROPOSED-ASM-1420/1807 as RE-REGISTERED by the
     maintainer's issue #24 decision (C), PROPOSED-ASM-1847): the
     rules-1-c mechanical readout must EXIST
     (registry/verdicts/rules-1-c.json) AND the frozen rules-2 record must
     carry the sequencing_gate re-registration block citing issue #24 (C)
     — the landed rules-1-c verdict is INSTRUMENT-INVALID and decision (C)
     designates rules-2 (train-time internalisation, B4/s3' struck) as the
     host-integration slot's replacement instrument;
  3. a green pinned mock artifact (poc/rules-2/results/mock-validation.json)
     whose harness sha matches the staged bytes;
  4. --dry-plan green for the requested tier (registry usd_cap $18 /
     14 GPU-h for R1; coordinator outer ceiling $35);
  5. the R2 rung additionally requires --authorize-r2 (the coordinator-
     authorized SECOND launch, MD-R2-3a).
Modal hygiene (standing bd memory): launch long runs nohup+setsid;
`modal app stop ap-<id>` after killing ANY attached client.

Results land in poc/rules-2/results-incoming/<UTC stamp>-modal/<job>/ (+
merged/) — NOT auto-committed. 12 h function timeout per job.
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
RULES2_FILES = ("rules2_runner.py", "materialise_closure.py",
                "merge_shards.py")
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
DEFAULT_ARMS = "B0,B1,B2,B3,B5,c1p"  # B4 STRUCK (issue #24 (C))


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


def build_jobs(rungs: str) -> list:
    """The canonical shard set (rules2-manifest.json sharded_launch): one
    job per (FT arm x seed x rung), one per eval-only arm (B4 STRUCK).
    Job tags are stable identifiers for --jobs subsetting across accounts."""
    man = json.loads((RULES2_INPUTS / "rules2-manifest.json").read_text())
    dc = man["design_constants_from_design_doc"]
    jobs = []
    rung_list = [r.strip() for r in rungs.split(",") if r.strip()]
    for rung in rung_list:
        if rung not in ("R1", "R2"):
            raise SystemExit(f"ERR_RUNGS: unknown rung {rung!r}")
        ft = dc["ft_arms"] if rung == "R1" else \
            [a for a in dc["rungs_r2_arms"] if a in dc["ft_arms"]]
        for arm in ft:
            for seed in dc["ft_seeds"]:
                jobs.append({"tag": f"{arm.lower()}-{rung.lower()}-s{seed}",
                             "arms": arm, "rungs": rung, "seeds": str(seed)})
        for seed in dc["eval_only_seeds"]["B0"]:
            jobs.append({"tag": f"b0-{rung.lower()}-s{seed}", "arms": "B0",
                         "rungs": rung, "seeds": str(seed)})
    if "R1" in rung_list:
        for seed in dc["eval_only_seeds"]["B5"]:
            jobs.append({"tag": f"b5-r3-s{seed}", "arms": "B5",
                         "rungs": "R1", "seeds": str(seed)})
    return jobs


def _launch_gates(gpu: str, rungs: str, authorize_r2: bool,
                  staged_sha: str) -> None:
    """Programmatic fail-closed launch gates for the FULL (non-mock) path
    (REWORK-2, review item 9: the old code only PRINTED a reminder)."""
    import subprocess

    rec_path = REPO_ROOT / "registry" / "experiments" / "rules-2.json"
    rec = json.loads(rec_path.read_text())
    if rec.get("status") != "FROZEN":
        raise SystemExit("ERR_GATE_FREEZE: registry/experiments/rules-2.json "
                         "status is %r, not FROZEN — the coordinator freezes "
                         "before any final-phase run" % rec.get("status"))
    hm = str(rec.get("pins", {}).get("harness_manifest", ""))
    if staged_sha not in hm:
        raise SystemExit("ERR_GATE_MANIFEST: staged-bytes sha %s is not "
                         "recorded in the frozen record's "
                         "pins.harness_manifest — staged bytes drifted "
                         "since freeze (correction record required)"
                         % staged_sha[:16])

    verdict_path = REPO_ROOT / "registry" / "verdicts" / "rules-1-c.json"
    if not verdict_path.exists():
        raise SystemExit("ERR_GATE_SEQUENCING (PROPOSED-ASM-1420 as "
                         "corrected by PROPOSED-ASM-1807): no rules-1-c "
                         "verdict exists yet — RULES-2's GPU path is blocked "
                         "until the RULES-1-C mechanical readout lands "
                         "(rules-1-b was superseded pre-GPU by rules-1-c, "
                         "2026-07-12; a rules-1-b verdict will never exist). "
                         "GPU is additionally HELD pending the maintainer's "
                         "issue #24 host-integration slot decision.")
    verdict = json.loads(verdict_path.read_text()).get("verdict")
    if verdict != "PASS":
        # PROPOSED-ASM-1420/1807 as amended by PROPOSED-ASM-1847: under any
        # non-PASS rules-1-c branch the gate opens ONLY via the maintainer's
        # issue #24 slot decision, carried as a machine-readable
        # re-registration block in the FROZEN rules-2 record (decision (C):
        # rules-2, with B4/s3' struck, is the host-integration slot's
        # replacement instrument). Lives under runner_constraints (the
        # kot-reg/2 root is additionalProperties:false).
        sg = rec.get("runner_constraints", {}).get("sequencing_gate", {})
        if not (sg.get("reregistered") and "issue #24" in
                str(sg.get("authority", "")) and sg.get("decision") == "C"):
            raise SystemExit("ERR_GATE_SEQUENCING (PROPOSED-ASM-1420/1807/"
                             "1847): rules-1-c verdict is %r (non-PASS) and "
                             "the frozen rules-2 record carries no "
                             "sequencing_gate re-registration block citing "
                             "the maintainer's issue #24 decision (C) — no "
                             "spend on any branch without that." % verdict)

    mv_path = RULES2_DIR / "results" / "mock-validation.json"
    if not mv_path.exists():
        raise SystemExit("ERR_GATE_MOCK: poc/rules-2/results/"
                         "mock-validation.json missing — pin a green mock "
                         "before any GPU spend")
    mv = json.loads(mv_path.read_text())
    if not mv.get("green"):
        raise SystemExit("ERR_GATE_MOCK: pinned mock artifact is not green")
    if mv.get("harness_manifest_sha256") != staged_sha:
        raise SystemExit("ERR_GATE_MOCK: pinned mock artifact was validated "
                         "against harness sha %s, staged bytes are %s — "
                         "re-run the mock validation"
                         % (str(mv.get("harness_manifest_sha256"))[:16],
                            staged_sha[:16]))

    if "R2" in rungs and not authorize_r2:
        raise SystemExit("ERR_GATE_R2: the R2 rung is the coordinator-"
                         "authorized SECOND launch (MD-R2-3a) — pass "
                         "--authorize-r2 only under that authorization")

    cmd = [sys.executable, str(RUNNER), "--dry-plan",
           "--gpu-class", gpu, "--out-dir", "/tmp/rules2-dry-plan",
           "--inputs-dir", str(RULES2_INPUTS),
           "--data-root", str(REPO_ROOT / "data"),
           "--corpus-dir", str(R2TRAIN_DIR), "--rungs", rungs]
    if subprocess.call(cmd) != 0:
        raise SystemExit("ERR_GATE_DRYPLAN: --dry-plan failed for the "
                         "requested tier — caps or the 12 h per-job bound "
                         "would be exceeded; DO NOT LAUNCH")
    print("launch gates: ALL GREEN (freeze, sequencing, pinned mock, "
          "dry-plan%s)" % (", R2 authorization" if "R2" in rungs else ""))


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
                      local_manifest: dict, seeds: str = "",
                      shard_tag: str = "") -> dict:
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
    if seeds:
        cmd += ["--seeds", seeds]
    if shard_tag:
        cmd += ["--shard-tag", shard_tag]
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
              "byte-identity contract; arms=%s rungs=%s seeds=%s shard=%s"
              % (arms, rungs, seeds or "all", shard_tag or "-"),
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
        .add_local_file(RULES2_DIR / "merge_shards.py",
                        f"{REMOTE_RULES2}/merge_shards.py")
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
                      rungs: str = "R1", seeds: str = "",
                      shard_tag: str = "",
                      local_manifest: dict = None) -> dict:  # noqa: RUF013
        return _run_in_container("T4", mock, arms, rungs,
                                 local_manifest or {}, seeds, shard_tag)

    @app.function(image=image, gpu="A10G", volumes={HF_CACHE_MOUNT: hf_cache},
                  timeout=TIMEOUT_S)
    def run_rules2_a10g(mock: bool = False, arms: str = DEFAULT_ARMS,
                        rungs: str = "R1", seeds: str = "",
                        shard_tag: str = "",
                        local_manifest: dict = None) -> dict:  # noqa: RUF013
        return _run_in_container("A10G", mock, arms, rungs,
                                 local_manifest or {}, seeds, shard_tag)

    @app.function(image=image, gpu="A100-40GB",
                  volumes={HF_CACHE_MOUNT: hf_cache}, timeout=TIMEOUT_S)
    def run_rules2_a100(mock: bool = False, arms: str = DEFAULT_ARMS,
                        rungs: str = "R1", seeds: str = "",
                        shard_tag: str = "",
                        local_manifest: dict = None) -> dict:  # noqa: RUF013
        return _run_in_container("A100", mock, arms, rungs,
                                 local_manifest or {}, seeds, shard_tag)

    GPU_FUNCTIONS = {"T4": run_rules2_t4, "A10G": run_rules2_a10g,
                     "A100": run_rules2_a100}

    def _collect(files: dict, dest: Path) -> int:
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
        outcome = _outcome(str(dest))
        rc = int((dest / mc.RUNNER_EXIT_NAME).read_text()
                 .strip().split("=", 1)[1])
        print(f"  {dest.name}: OUTCOME={outcome} rc={rc} "
              f"({len(files)} files)")
        return rc

    @app.local_entrypoint()
    def main(gpu: str = "A10G", mock: bool = False, dry_plan: bool = False,
             arms: str = "", rungs: str = "R1", jobs: str = "",
             authorize_r2: bool = False, out_root: str = "") -> None:
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
        staged_sha = _manifest_sha(local_manifest)
        print(f"kot-rules2 via Modal: gpu={gpu} mock={mock} rungs={rungs} "
              f"({len(local_manifest)} staged files, runner "
              f"{local_manifest['poc/rules-2/rules2_runner.py'][:12]}…)")
        print(f"pins.harness_manifest (staged-bytes manifest sha, canonical "
              f"JSON): {staged_sha}")

        stamp = time.strftime("%Y%m%d-%H%M%S", time.gmtime()) + "-modal"
        root = Path(out_root) / stamp if out_root else INCOMING_ROOT / stamp

        if mock:
            # transport smoke: one monolithic mock container (arms
            # overridable), NO freeze/sequencing gates, ~pennies
            files = GPU_FUNCTIONS[gpu].remote(
                mock=True, arms=arms or DEFAULT_ARMS, rungs=rungs,
                local_manifest=local_manifest)
            rc = _collect(files, root)
            if rc != 0:
                raise SystemExit(f"ERR_RUNNER: mock exited rc={rc}")
            print("mock transport smoke done — `modal app stop ap-<id>` "
                  "after every attached run")
            return

        if arms:
            raise SystemExit("ERR_ARGS: the full path is SHARDED — select "
                             "shards with --jobs (see --print-jobs), not "
                             "--arms")
        _launch_gates(gpu, rungs, authorize_r2, staged_sha)

        all_jobs = build_jobs(rungs)
        if jobs:
            want = {j.strip() for j in jobs.split(",") if j.strip()}
            unknown = want - {j["tag"] for j in all_jobs}
            if unknown:
                raise SystemExit(f"ERR_JOBS: unknown job tag(s) {sorted(unknown)}; "
                                 f"see --print-jobs")
            all_jobs = [j for j in all_jobs if j["tag"] in want]
        print(f"spawning {len(all_jobs)} independent shard jobs "
              f"(parallel; 12 h timeout each): "
              f"{[j['tag'] for j in all_jobs]}")

        calls = [(j, GPU_FUNCTIONS[gpu].spawn(
            mock=False, arms=j["arms"], rungs=j["rungs"], seeds=j["seeds"],
            shard_tag=j["tag"], local_manifest=local_manifest))
            for j in all_jobs]
        failures = []
        shard_dirs = []
        for j, call in calls:
            dest = root / j["tag"]
            try:
                rc = _collect(call.get(), dest)
            except Exception as e:  # noqa: BLE001
                failures.append((j["tag"], str(e)))
                continue
            if rc != 0:
                failures.append((j["tag"], f"rc={rc}"))
            else:
                shard_dirs.append(str(dest))
        if failures:
            raise SystemExit("ERR_SHARDS: %d/%d shard job(s) failed: %s — "
                             "relaunch ONLY the failed tags with --jobs "
                             "(completed shards are kept; merge after)"
                             % (len(failures), len(calls), failures))

        import subprocess
        merged = root / "merged"
        rc = subprocess.call([sys.executable,
                              str(RULES2_DIR / "merge_shards.py"),
                              "--out-dir", str(merged)] + shard_dirs)
        if rc != 0:
            raise SystemExit("ERR_MERGE: merge_shards.py failed — shards "
                             f"kept in {root}")
        print(f"\nall {len(shard_dirs)} shards green; merged -> {merged}")
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
    if "--print-jobs" in sys.argv:
        rungs = "R1"
        if "--rungs" in sys.argv:
            rungs = sys.argv[sys.argv.index("--rungs") + 1]
        for j in build_jobs(rungs):
            print("%-12s arms=%-4s rungs=%-3s seeds=%s"
                  % (j["tag"], j["arms"], j["rungs"], j["seeds"]))
        sys.exit(0)
    raise SystemExit("run via `modal run poc/rules-2/modal/modal_rules2.py ...` "
                     "or use --print-manifest / --print-jobs")
