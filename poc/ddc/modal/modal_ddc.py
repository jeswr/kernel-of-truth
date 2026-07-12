#!/usr/bin/env python3
"""DDC campaign on Modal serverless GPU (DRAFT records
registry/experiments/ddc0.json + ddc1.json — the coordinator freezes
BEFORE any final-phase run). Mirrors poc/rules-2/modal/modal_rules2.py.

Wraps poc/ddc/{ddc_runner.py, g0_runner.py} UNCHANGED: stages bytes,
asserts the staged manifest in-container (fail closed,
ERR_STAGING_MISMATCH), runs the runner, ships its output directory back
as opaque bytes with sidecar-only provenance.

IMAGE REUSE (PROPOSED-ASM-1106 lineage / ASM-1655): built from the SAME
poc/modal/requirements-image.txt (sha 0fac7243…) as the pinned f2b image —
NO new dependency, no image change (numpy/torch/transformers cover the
whole surgery + eval stack; the G0 stats stage is numpy-only and runs on
a CPU-ONLY function so GPU-hours stay inside the ddc0 2 GPU-h carve-out).

PINNING DIRECTION: the DRAFT records' pins.harness_manifest carry the
staged-bytes manifest sha printed by --print-manifest. Corpora
(data/ddc-*) are staged when present; landing them at T0 CHANGES the sha
— the coordinator re-pins at T0 (PINNED-AT-INPUTS discipline) and any
byte change after freeze requires a correction record.

    python3 poc/ddc/modal/modal_ddc.py --print-manifest          # $0
    python3 poc/ddc/modal/modal_ddc.py --print-jobs --tier s1    # $0
    .venv/bin/modal run poc/ddc/modal/modal_ddc.py --dry-plan --tier s1  # $0
    .venv/bin/modal run poc/ddc/modal/modal_ddc.py --mock        # pennies
    .venv/bin/modal run poc/ddc/modal/modal_ddc.py --tier t0     # A0 baseline
    .venv/bin/modal run poc/ddc/modal/modal_ddc.py --tier ddc0   # G0 (2 jobs)
    .venv/bin/modal run poc/ddc/modal/modal_ddc.py --tier s1 \
        --jobs s1-a1-rho0p75-s0,s1-m1-rho0p75-s0        # subset (multi-account)
    .venv/bin/modal run poc/ddc/modal/modal_ddc.py --tier s2 --authorize-s2

SHARDED PARALLEL LAUNCH: every tier is a set of INDEPENDENT jobs (one per
(rung, arm, rho, seed) cell; --print-jobs) spawned concurrently as
separate Modal function calls, splittable across the modal2/modal3/modal4
workspaces via --jobs. Worst planned single job ≈ 1.6 h — far below the
12 h function timeout. Shards land under poc/ddc/results-incoming/; run
poc/ddc/merge_shards.py over ALL collected shard dirs (across tiers)
to reconstruct the canonical analysis inputs.

LAUNCH GATES — programmatic, fail-closed (_launch_gates), full path only:
  1. the tier's registry record is FROZEN (ddc0 for --tier ddc0; ddc1 for
     s1/s2) and the staged-bytes sha is recorded in pins.harness_manifest;
  2. sequencing: s1/s2 need registry/verdicts/ddc0.json to exist (G0
     routes the A2 arm; A2 jobs are only built when it read out PASS);
  3. a green pinned mock artifact (poc/ddc/results/mock-validation.json)
     whose harness sha matches the staged bytes;
  4. --dry-plan green for the requested tier (fail-closed $60 campaign
     ceiling, $5/2GPU-h ddc0 carve-out, 12 h per-job bound);
  5. --tier s2 additionally requires --authorize-s2 (the §8 promotion
     rule, confirmed from the S1 readout by the runner identity).
Modal hygiene (standing bd memory): launch long runs nohup+setsid;
`modal app stop ap-<id>` after killing ANY attached client.

Results are NOT auto-committed. This module states NO feasibility
conclusion.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

try:
    import modal
except ImportError:  # --print-manifest/--print-jobs work without modal
    modal = None

_HERE = Path(__file__).resolve().parent
try:
    REPO_ROOT = _HERE.parents[2]
except IndexError:
    REPO_ROOT = _HERE  # container: local-path constants never dereferenced
_MODAL_TOOLS = REPO_ROOT / "poc" / "modal"
sys.path.insert(0, str(_MODAL_TOOLS))
sys.path.insert(0, str(_HERE.parent))
import modal_common as mc  # noqa: E402  (stdlib-only helper, poc/modal)

DDC_DIR = REPO_ROOT / "poc" / "ddc"
DDC_FILES = ("ddc_runner.py", "g0_runner.py", "g0_stats.py",
             "ddc_selection.py", "ddc_surgery.py", "ddc_common.py",
             "merge_shards.py", "validate_mock.py", "power_sim_ddc1.py")
DDC_INPUTS = DDC_DIR / "inputs"
PUBEVAL_DIR = REPO_ROOT / "poc" / "pubeval"
PUBEVAL_FILES = ("pubeval_runner.py", "benchmarks.py", "transforms.py",
                 "fetch_data.py", "test_boundary_regression.py")
PUBEVAL_DATA = PUBEVAL_DIR / "data"
ANALYSIS_FILES = ("ddc0.py", "ddc1.py")   # pinned analyses ride along so
                                          # the staged sha covers them
CORPORA_DIRS = ("ddc-kernel-static-v1", "ddc-kernel-hybrid-v1",
                "ddc-c4-sample-v1", "ddc-knull-render-v1",
                "ddc-shuffled-kernel-v1", "ddc-probe-fixture-v1",
                "ddc-eval-subset-v1")
IMAGE_REQS = _MODAL_TOOLS / "requirements-image.txt"
INCOMING_ROOT = DDC_DIR / "results-incoming"
MOCK_ARTIFACT = DDC_DIR / "results" / "mock-validation.json"

REMOTE_ROOT = "/root/kot"
REMOTE_DDC = f"{REMOTE_ROOT}/poc/ddc"
REMOTE_PUBEVAL = f"{REMOTE_ROOT}/poc/pubeval"
REMOTE_DATA = f"{REMOTE_ROOT}/data"
REMOTE_OUT = "/tmp/ddc-results"
HF_CACHE_MOUNT = "/root/.cache/huggingface"
ARTIFACT_MOUNT = "/artifacts"
TIMEOUT_S = 12 * 3600
GPU_CHOICES = ("T4", "A10G")
TIERS = ("t0", "ddc0", "s1", "s2")


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


def _manifest(ddc_dir: str, ddc_inputs: str, pubeval_dir: str,
              analysis_dir: str, data_root: str, image_reqs: str) -> dict:
    man = {"modal/requirements-image.txt": mc.sha256_file(image_reqs)}
    for name in DDC_FILES:
        p = os.path.join(ddc_dir, name)
        if os.path.exists(p):
            man[f"poc/ddc/{name}"] = mc.sha256_file(p)
    for name in PUBEVAL_FILES:
        man[f"poc/pubeval/{name}"] = mc.sha256_file(
            os.path.join(pubeval_dir, name))
    for name in ANALYSIS_FILES:
        p = os.path.join(analysis_dir, name)
        if os.path.exists(p):
            man[f"analysis/{name}"] = mc.sha256_file(p)
    _walk_manifest(man, "inputs", ddc_inputs)
    pub_data = os.path.join(pubeval_dir, "data")
    if os.path.isdir(pub_data):
        for name in sorted(os.listdir(pub_data)):
            p = os.path.join(pub_data, name)
            if os.path.isfile(p):
                man[f"pubeval-data/{name}"] = mc.sha256_file(p)
    for cname in CORPORA_DIRS:
        cdir = os.path.join(data_root, cname)
        if os.path.isdir(cdir):
            _walk_manifest(man, f"data/{cname}", cdir)
    return man


def _manifest_sha(man: dict) -> str:
    import hashlib
    blob = json.dumps(man, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _local_manifest() -> dict:
    return _manifest(str(DDC_DIR), str(DDC_INPUTS), str(PUBEVAL_DIR),
                     str(REPO_ROOT / "analysis"), str(REPO_ROOT / "data"),
                     str(IMAGE_REQS))


def build_jobs(tier: str) -> list:
    sys.path.insert(0, str(DDC_DIR))
    import ddc_common as C
    manifest = C.load_manifest()
    if tier == "ddc0":
        return [{"tag": "ddc0-probe", "kind": "g0-probe"},
                {"tag": "ddc0-stats", "kind": "g0-stats"}]
    return [dict(j, kind="cell") for j in C.build_jobs(manifest, tier)]


def _launch_gates(tier: str, authorize_s2: bool, staged_sha: str) -> None:
    import subprocess
    record = "ddc0" if tier == "ddc0" else "ddc1"
    rec_path = REPO_ROOT / "registry" / "experiments" / f"{record}.json"
    rec = json.loads(rec_path.read_text())
    if tier != "t0" and rec.get("status") != "FROZEN":
        raise SystemExit(
            "ERR_GATE_FREEZE: registry/experiments/%s.json status is %r, "
            "not FROZEN — the coordinator freezes before any final-phase "
            "run" % (record, rec.get("status")))
    hm = json.dumps(rec.get("pins", {}).get("harness_manifest", ""))
    if tier != "t0" and staged_sha not in hm:
        raise SystemExit(
            "ERR_GATE_MANIFEST: staged-bytes sha %s is not recorded in the "
            "%s record's pins.harness_manifest — staged bytes drifted "
            "since the pin (T0 re-pin or correction record required)"
            % (staged_sha[:16], record))
    if tier in ("s1", "s2"):
        vpath = REPO_ROOT / "registry" / "verdicts" / "ddc0.json"
        if not vpath.exists():
            raise SystemExit(
                "ERR_GATE_SEQUENCING: no ddc0 verdict exists — G0 routes "
                "the A2 arm; the arm campaign launches only after the "
                "ddc0 readout lands (DDC.md section 8)")
    if not MOCK_ARTIFACT.exists():
        raise SystemExit("ERR_GATE_MOCK: poc/ddc/results/mock-validation"
                         ".json missing — pin a green mock before any GPU "
                         "spend")
    mv = json.loads(MOCK_ARTIFACT.read_text())
    if not mv.get("green"):
        raise SystemExit("ERR_GATE_MOCK: pinned mock artifact is not green")
    if mv.get("harness_manifest_sha256") != staged_sha:
        raise SystemExit(
            "ERR_GATE_MOCK: pinned mock artifact was validated against "
            "harness sha %s, staged bytes are %s — re-run "
            "poc/ddc/validate_mock.py"
            % (str(mv.get("harness_manifest_sha256"))[:16],
               staged_sha[:16]))
    if tier == "s2" and not authorize_s2:
        raise SystemExit(
            "ERR_GATE_S2: S2 is conditional on the §8 promotion rule read "
            "out from S1 — pass --authorize-s2 only under that reading")
    cmd = [sys.executable, str(DDC_DIR / "ddc_runner.py"), "--dry-plan",
           "--tier", tier, "--out-dir", "/tmp/ddc-dry-plan"]
    if subprocess.call(cmd) != 0:
        raise SystemExit("ERR_GATE_DRYPLAN: --dry-plan failed for tier %s "
                         "— caps would be exceeded; DO NOT LAUNCH" % tier)
    print("launch gates: ALL GREEN (freeze, manifest, pinned mock, "
          "dry-plan%s)" % (", S2 authorization" if tier == "s2" else ""))


def _run_in_container(gpu_requested: str, job: dict, mock: bool,
                      local_manifest: dict) -> dict:
    import subprocess

    import modal_common as cmc

    started = cmc.utcnow_iso()
    staged = _manifest(REMOTE_DDC, f"{REMOTE_DDC}/inputs", REMOTE_PUBEVAL,
                       f"{REMOTE_ROOT}/analysis", REMOTE_DATA,
                       f"{REMOTE_ROOT}/poc/modal/requirements-image.txt")
    if staged != local_manifest:
        diff = sorted(k for k in set(staged) | set(local_manifest)
                      if staged.get(k) != local_manifest.get(k))
        raise SystemExit("ERR_STAGING_MISMATCH: staged bytes differ from "
                         f"coordinator: {diff}")

    kind = job.get("kind", "cell")
    if kind == "g0-probe":
        cmd = [sys.executable, f"{REMOTE_DDC}/g0_runner.py",
               "--stage", "probe", "--out-dir",
               f"{ARTIFACT_MOUNT}/ddc0" if not mock else REMOTE_OUT,
               "--data-root", REMOTE_DATA,
               "--device", "cpu" if mock else "cuda"]
        if mock:
            cmd.append("--mock")
    elif kind == "g0-stats":
        cmd = [sys.executable, f"{REMOTE_DDC}/g0_runner.py",
               "--stage", "stats", "--out-dir", REMOTE_OUT,
               "--artifact", f"{ARTIFACT_MOUNT}/ddc0",
               "--data-root", REMOTE_DATA,
               "--workers", str(max(1, (os.cpu_count() or 2) - 1))]
        if mock:
            cmd = [sys.executable, f"{REMOTE_DDC}/g0_runner.py", "--mock",
                   "--out-dir", REMOTE_OUT]
    else:
        cmd = [sys.executable, f"{REMOTE_DDC}/ddc_runner.py",
               "--out-dir", REMOTE_OUT,
               "--rungs", job["rung"], "--arms", job["arm"],
               "--rhos", "%g" % job["rho"], "--seeds", str(job["seed"]),
               "--shard-tag", job["tag"],
               "--data-root", REMOTE_DATA,
               "--device", "cpu" if mock else "cuda"]
        if mock:
            cmd.append("--mock")
        else:
            t0_path = f"{REMOTE_DDC}/inputs/t0-block.json"
            if os.path.exists(t0_path):
                cmd += ["--t0-block", t0_path]
            if job["arm"] == "A2":
                cmd += ["--ddc0-analysis",
                        f"{REMOTE_DDC}/inputs/ddc0-analysis.json",
                        "--ddc0-directions",
                        f"{REMOTE_DDC}/inputs/a2-directions-ddc0.json"]
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
        notes="ddc campaign job %s (%s); runner outputs shipped as opaque "
              "bytes; sidecars only" % (job.get("tag"), kind),
    )
    files = cmc.package_results(REMOTE_OUT, run_log=log, rc=rc,
                                provenance=prov)
    try:
        hf_cache.commit()
        ddc_artifacts.commit()
    except Exception:  # noqa: BLE001
        pass
    return files


if modal is not None:
    app = modal.App("kot-ddc")

    image = (
        modal.Image.debian_slim(python_version="3.11")
        .pip_install(*_image_pins())
        .add_local_python_source("modal_common")
    )
    for _name in DDC_FILES:
        _p = DDC_DIR / _name
        if _p.exists():
            image = image.add_local_file(_p, f"{REMOTE_DDC}/{_name}")
    for _name in PUBEVAL_FILES:
        image = image.add_local_file(PUBEVAL_DIR / _name,
                                     f"{REMOTE_PUBEVAL}/{_name}")
    for _name in ANALYSIS_FILES:
        _p = REPO_ROOT / "analysis" / _name
        if _p.exists():
            image = image.add_local_file(_p,
                                         f"{REMOTE_ROOT}/analysis/{_name}")
    image = image.add_local_dir(DDC_INPUTS,
                                remote_path=f"{REMOTE_DDC}/inputs")
    if PUBEVAL_DATA.is_dir() and any(PUBEVAL_DATA.iterdir()):
        image = image.add_local_dir(PUBEVAL_DATA,
                                    remote_path=f"{REMOTE_PUBEVAL}/data")
    for _cname in CORPORA_DIRS:
        _cdir = REPO_ROOT / "data" / _cname
        if _cdir.is_dir():
            image = image.add_local_dir(_cdir,
                                        remote_path=f"{REMOTE_DATA}/{_cname}")
    image = image.add_local_file(
        IMAGE_REQS, f"{REMOTE_ROOT}/poc/modal/requirements-image.txt")

    hf_cache = modal.Volume.from_name("kot-hf-cache",
                                      create_if_missing=True)
    ddc_artifacts = modal.Volume.from_name("kot-ddc-artifacts",
                                           create_if_missing=True)
    _VOLS = {HF_CACHE_MOUNT: hf_cache, ARTIFACT_MOUNT: ddc_artifacts}

    @app.function(image=image, gpu="T4", volumes=_VOLS, timeout=TIMEOUT_S)
    def run_ddc_t4(job: dict, mock: bool = False,
                   local_manifest: dict = None) -> dict:  # noqa: RUF013
        return _run_in_container("T4", job, mock, local_manifest or {})

    @app.function(image=image, gpu="A10G", volumes=_VOLS,
                  timeout=TIMEOUT_S)
    def run_ddc_a10g(job: dict, mock: bool = False,
                     local_manifest: dict = None) -> dict:  # noqa: RUF013
        return _run_in_container("A10G", job, mock, local_manifest or {})

    @app.function(image=image, volumes=_VOLS, timeout=TIMEOUT_S, cpu=8.0)
    def run_ddc_cpu(job: dict, mock: bool = False,
                    local_manifest: dict = None) -> dict:  # noqa: RUF013
        # CPU-ONLY: the ddc0 stats stage (numpy) — keeps GPU-hours inside
        # the 2 GPU-h carve-out
        return _run_in_container("none", job, mock, local_manifest or {})

    GPU_FUNCTIONS = {"T4": run_ddc_t4, "A10G": run_ddc_a10g}

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
        rc = int((dest / mc.RUNNER_EXIT_NAME).read_text()
                 .strip().split("=", 1)[1])
        print(f"  {dest.name}: rc={rc} ({len(files)} files)")
        return rc

    @app.local_entrypoint()
    def main(gpu: str = "A10G", mock: bool = False, dry_plan: bool = False,
             tier: str = "s1", jobs: str = "",
             authorize_s2: bool = False, out_root: str = "") -> None:
        gpu = gpu.upper()
        if gpu not in GPU_FUNCTIONS:
            raise SystemExit(f"ERR_GPU: --gpu must be one of {GPU_CHOICES},"
                             f" got {gpu!r}")
        if tier not in TIERS:
            raise SystemExit(f"ERR_TIER: --tier must be one of {TIERS}")
        if dry_plan:
            import subprocess
            raise SystemExit(subprocess.call(
                [sys.executable, str(DDC_DIR / "ddc_runner.py"),
                 "--dry-plan", "--tier", tier,
                 "--out-dir", "/tmp/ddc-dry-plan"]))

        local_manifest = _local_manifest()
        staged_sha = _manifest_sha(local_manifest)
        print(f"kot-ddc via Modal: gpu={gpu} mock={mock} tier={tier} "
              f"({len(local_manifest)} staged files)")
        print(f"pins.harness_manifest (staged-bytes manifest sha, "
              f"canonical JSON): {staged_sha}")

        stamp = time.strftime("%Y%m%d-%H%M%S", time.gmtime()) + "-modal"
        root = Path(out_root) / stamp if out_root else INCOMING_ROOT / stamp

        if mock:
            # transport smoke: ONE small mock cell shard + the mock G0 —
            # NO freeze gates, ~pennies
            for job in ({"tag": "mock-cell", "kind": "cell",
                         "rung": "r135", "arm": "A1", "rho": 0.75,
                         "seed": 0},
                        {"tag": "mock-g0", "kind": "g0-stats"}):
                files = GPU_FUNCTIONS[gpu].remote(
                    job=job, mock=True, local_manifest=local_manifest)
                rc = _collect(files, root / job["tag"])
                if rc != 0:
                    raise SystemExit(f"ERR_RUNNER: mock job "
                                     f"{job['tag']} rc={rc}")
            print("mock transport smoke done — `modal app stop ap-<id>` "
                  "after every attached run")
            return

        _launch_gates(tier, authorize_s2, staged_sha)
        all_jobs = build_jobs(tier)
        if jobs:
            want = {j.strip() for j in jobs.split(",") if j.strip()}
            unknown = want - {j["tag"] for j in all_jobs}
            if unknown:
                raise SystemExit(f"ERR_JOBS: unknown job tag(s) "
                                 f"{sorted(unknown)}; see --print-jobs")
            all_jobs = [j for j in all_jobs if j["tag"] in want]
        print(f"spawning {len(all_jobs)} independent job(s) (12 h timeout "
              f"each): {[j['tag'] for j in all_jobs]}")

        # ddc0's two stages are SEQUENTIAL (probe -> stats via the
        # artifact volume); everything else spawns concurrently
        if tier == "ddc0":
            seq = [j for j in all_jobs if j["kind"] == "g0-probe"] + \
                  [j for j in all_jobs if j["kind"] == "g0-stats"]
            failures = []
            for j in seq:
                fn = GPU_FUNCTIONS[gpu] if j["kind"] == "g0-probe" \
                    else run_ddc_cpu
                try:
                    rc = _collect(fn.remote(job=j, mock=False,
                                            local_manifest=local_manifest),
                                  root / j["tag"])
                except Exception as e:  # noqa: BLE001
                    failures.append((j["tag"], str(e)))
                    break
                if rc != 0:
                    failures.append((j["tag"], f"rc={rc}"))
                    break
            if failures:
                raise SystemExit("ERR_SHARDS: ddc0 stage failed: %s"
                                 % failures)
        else:
            calls = [(j, GPU_FUNCTIONS[gpu].spawn(
                job=j, mock=False, local_manifest=local_manifest))
                for j in all_jobs]
            failures = []
            for j, call in calls:
                try:
                    rc = _collect(call.get(), root / j["tag"])
                except Exception as e:  # noqa: BLE001
                    failures.append((j["tag"], str(e)))
                    continue
                if rc != 0:
                    failures.append((j["tag"], f"rc={rc}"))
            if failures:
                raise SystemExit(
                    "ERR_SHARDS: %d/%d job(s) failed: %s — relaunch ONLY "
                    "the failed tags with --jobs (completed shards kept)"
                    % (len(failures), len(calls), failures))
        print(f"\nall jobs green -> {root}")
        print("merge across ALL collected tiers when the grid is complete:"
              "\n  python3 poc/ddc/merge_shards.py --out-dir <merged> "
              "<shard dirs...>")
        print("done — results NOT auto-committed; `modal app stop ap-<id>`"
              " after every attached run")


if __name__ == "__main__":
    if "--print-manifest" in sys.argv:
        man = _local_manifest()
        print(f"staged files: {len(man)}")
        print(f"pins.harness_manifest (staged-bytes manifest sha, "
              f"canonical JSON): {_manifest_sha(man)}")
        sys.exit(0)
    if "--print-jobs" in sys.argv:
        tier = "s1"
        if "--tier" in sys.argv:
            tier = sys.argv[sys.argv.index("--tier") + 1]
        for j in build_jobs(tier):
            print("%-22s %s" % (j["tag"], json.dumps(
                {k: v for k, v in j.items() if k != "tag"},
                sort_keys=True)))
        sys.exit(0)
    raise SystemExit("run via `modal run poc/ddc/modal/modal_ddc.py ...` "
                     "or use --print-manifest / --print-jobs")
