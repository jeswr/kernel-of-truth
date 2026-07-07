#!/usr/bin/env python3
"""E1 core-freezing grid + chained E4 emission test on Modal serverless GPU
(bead kernel-of-truth-af7; scaffold shape from kernel-of-truth-0oj).

Wraps poc/e1 (build_data / train_e1 / eval_e1 / stats_e1) and poc/e4/runner
(build_emission / finetune_e4 / eval_e4 / stats_e4) UNCHANGED — every stage of
poc/e1/run_all.sh full + poc/e4/runner/run_e4.sh full becomes a Modal function
that subprocesses the same script with the same argv (parsed out of the staged
driver bytes — see modal_e1e4_lib.py), and the pre-registered 5-arms x 5-seeds
grid becomes parallel calls instead of a serial loop on one box:

    AWS g5.xlarge serial (poc/gpu/README.md E1 cost table)     ~20-23 h
    Modal parallel: build ~4 h (CPU fn) + sweep 15-way starmap + grid 25-way
    starmap + evals 35-way + E4 chain 15-way                    ~5-6 h wall

Parallel arms/seeds are sound because run order is immaterial by construction
(Common rule 1: shards, story order, substitution draws and batch schedule are
functions of the seed index only); the single cross-job dependency — Common
rule 5's LR-selection barrier — is an explicit sync point below, executed with
run_all.sh's OWN selection snippet.

    .venv/bin/python poc/modal/modal_e1e4.py --dry-plan      # NO token needed
    .venv/bin/modal run poc/modal/modal_e1e4.py --mock       # transport smoke
    .venv/bin/modal run poc/modal/modal_e1e4.py              # full E1+E4, A10G
    .venv/bin/modal run poc/modal/modal_e1e4.py --gpu t4     # T4 (see README!)
    .venv/bin/modal run poc/modal/modal_e1e4.py --skip-e4    # E1 only

Persistent state lives in Modal Volume `kot-e1-work` (corpus, uint16 shards,
checkpoints, eval JSONs — the /opt/e1work of the AWS path); stages are
idempotent via stamps keyed on (argv, staged-manifest digest), so re-running
the entrypoint after a partial failure resumes instead of retraining. Only
results (verdicts, evals, lr-selection, logs, provenance — never checkpoints)
ship back as bytes into poc/e1/results-incoming/<UTC stamp>-modal/ with the
AWS pull-path layout (E4 under e4/, RUNNER_EXIT `rc=N e4_rc=M`), transport
provenance in SIDECARS only. NOT auto-committed — the coordinator reviews and
commits deliberately, exactly like poc/gpu/collect-e1.sh.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import modal

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
import modal_common as mc  # noqa: E402  (stdlib-only; shipped into the image)
import modal_e1e4_lib as lib  # noqa: E402  (stdlib-only; shipped into the image)

# ---- coordinator-side paths --------------------------------------------------
# Container mount is /root (no second parent); only REMOTE_* paths are used there.
try:
    REPO_ROOT = _HERE.parents[1]
except IndexError:
    REPO_ROOT = _HERE  # container: local-path constants are never dereferenced
INCOMING_ROOT = REPO_ROOT / "poc" / "e1" / "results-incoming"

# ---- container-side layout ---------------------------------------------------
REMOTE_ROOT = "/root/kot"        # mirrors the AWS clone at /opt/kot
WORK = "/vol/e1work"             # Volume mount — the /opt/e1work of the AWS path
GPU_CHOICES = ("A10G", "T4")     # A10G default (g5.xlarge parity); T4 opt-in

PROVENANCE_NAME = "provenance-modal.json"
E1_LOG_NAME = "kot-e1-run.log"   # same names as the AWS pull path
E4_LOG_NAME = "kot-e4-run.log"


def _pins() -> list:
    p = _HERE / "requirements-image.txt"
    if not p.exists():  # container-side re-import: the image is already built
        return []
    lines = p.read_text().splitlines()
    return [ln.strip() for ln in lines if ln.strip() and not ln.strip().startswith("#")]


app = modal.App("kot-e1e4")

# Pinned image (requirements-image.txt on pinned python) + the exact bytes of
# every E1/E4 script and input (modal_e1e4_lib.STAGE_FILES). add_local_* layers
# attach at container start, so editing sources never invalidates the pip
# layer; content integrity comes from the in-container manifest assertion.
_image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(*_pins())
    .add_local_python_source("modal_common", "modal_e1e4_lib")
)
for _rel in lib.STAGE_FILES:
    _src = REPO_ROOT / _rel
    if _src.exists():  # absent only on container-side re-import (see _pins)
        _image = _image.add_local_file(_src, f"{REMOTE_ROOT}/{_rel}")
image = _image

work_vol = modal.Volume.from_name("kot-e1-work", create_if_missing=True)
_VOL = {WORK: work_vol}


# ---------------------------------------------------------------------------
# Container-side plumbing (fail closed everywhere)
# ---------------------------------------------------------------------------


def _vol_reload() -> None:
    try:
        work_vol.reload()
    except Exception:
        pass  # unhydrated/local-stub volume


def _vol_commit() -> None:
    try:
        work_vol.commit()
    except Exception:
        pass


def _assert_staging(local_manifest: dict) -> dict:
    staged = lib.tree_manifest(REMOTE_ROOT)
    if staged != (local_manifest or {}):
        diff = sorted(k for k in set(staged) | set(local_manifest or {})
                      if staged.get(k) != (local_manifest or {}).get(k))
        raise SystemExit(f"ERR_STAGING_MISMATCH: staged bytes differ from coordinator: {diff}")
    return staged


def _stamp_path(key: str) -> str:
    return os.path.join(WORK, "stamps", f"{key}.json")


def _stamp_ok(key: str, payload: dict, outputs: list) -> bool:
    p = _stamp_path(key)
    if not os.path.exists(p):
        return False
    try:
        with open(p) as f:
            old = json.load(f)
    except (OSError, ValueError):
        return False
    return old.get("payload") == payload and all(os.path.exists(o) for o in outputs)


def _stamp_write(key: str, payload: dict) -> None:
    os.makedirs(os.path.dirname(_stamp_path(key)), exist_ok=True)
    with open(_stamp_path(key), "w") as f:
        json.dump({"payload": payload, "completed_utc": mc.utcnow_iso()}, f, indent=2)


def _package_versions() -> dict:
    out = {}
    for name in ("numpy", "torch"):
        try:
            out[name] = __import__(name).__version__
        except Exception as e:  # provenance must never kill a finished run
            out[name] = f"unavailable: {e}"
    return out


def _run(run_id: str, argv: list, *, manifest: dict, gpu_requested: str,
         stage: str, mock: bool, check: bool = True) -> int:
    """Subprocess one unchanged E1/E4 script; stream + persist the log and a
    per-run provenance sidecar on the Volume (AWS parity: logs + nvidia-smi
    facts live NEXT TO results, never inside them)."""
    started = mc.utcnow_iso()
    env = dict(os.environ)
    # user-data-e1-pull.sh.tpl parity: narrow CUDA kernel nondeterminism.
    env.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")
    lines = [f"$ {' '.join(argv)}\n"]
    with subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                          text=True, bufsize=1, env=env, cwd=REMOTE_ROOT) as proc:
        assert proc.stdout is not None
        for line in proc.stdout:
            lines.append(line)
            sys.stdout.write(line)
            sys.stdout.flush()
    rc = proc.returncode
    lines.append(f"[{run_id} exit rc={rc}]\n")
    log = "".join(lines)

    os.makedirs(os.path.join(WORK, "logs"), exist_ok=True)
    with open(os.path.join(WORK, "logs", f"{run_id}.log"), "w") as f:
        f.write(log)
    prov = mc.build_provenance(
        transport="modal", gpu_requested=gpu_requested, gpu_seen=mc.gpu_info(),
        staged_manifest=manifest, runner_exit=rc, started_utc=started,
        finished_utc=mc.utcnow_iso(), packages=_package_versions(),
        environment=mc.redact_env(dict(os.environ)),
        notes="per-run sidecar; script outputs shipped as opaque bytes "
              "(poc/modal/modal_common.py byte-identity contract)")
    prov.update({"stage": stage, "runId": run_id, "argv": argv, "mock": mock})
    os.makedirs(os.path.join(WORK, "prov"), exist_ok=True)
    with open(os.path.join(WORK, "prov", f"{run_id}.json"), "w") as f:
        json.dump(prov, f, indent=2, sort_keys=True)

    if check and rc != 0:
        tail = "".join(lines[-25:])
        _vol_commit()  # keep the failure trace collectable (salvage/volume)
        raise SystemExit(f"ERR_STAGE: {run_id} exited rc={rc}; log tail:\n{tail}")
    return rc


# ---------------------------------------------------------------------------
# Stage bodies (shared by the A10G/T4 registrations)
# ---------------------------------------------------------------------------


def _fetch_corpus_body(local_manifest: dict, mock: bool) -> dict:
    _vol_reload()
    manifest = _assert_staging(local_manifest)
    path = lib.corpus_path(WORK, mock)
    meta_path = os.path.join(WORK, "corpus", "corpus-meta.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if os.path.exists(path) and os.path.exists(meta_path):
        with open(meta_path) as f:
            meta = json.load(f)
        rec = meta.get(os.path.basename(path))
        if rec and mc.sha256_file(path) == rec["sha256"]:
            print(f"corpus present + sha-verified, skipping fetch: {path}")
            return {"skipped": True, **rec}
    started = mc.utcnow_iso()
    if mock:
        # run_e4.sh's OWN gloss-free synthetic corpus generator, verbatim.
        _run("00-fetch-corpus-mock", [sys.executable, "-c",
             lib.mock_corpus_code(REMOTE_ROOT), path],
             manifest=manifest, gpu_requested="none", stage="fetch_corpus", mock=mock)
    else:
        # user-data-e1-pull.sh.tpl parity (curl -sL --retry 3 <URL>). Like the
        # AWS path there is NO pre-registered corpus pin; the sha is recorded
        # here and again by build_data.py in data/meta.json.
        last = None
        for attempt in range(3):
            try:
                with urllib.request.urlopen(lib.CORPUS_URL, timeout=120) as r, \
                        open(path + ".part", "wb") as f:
                    while True:
                        chunk = r.read(1 << 20)
                        if not chunk:
                            break
                        f.write(chunk)
                os.replace(path + ".part", path)
                last = None
                break
            except Exception as e:  # noqa: BLE001 — retried, then fails closed
                last = e
                time.sleep(5 * (attempt + 1))
        if last is not None:
            raise SystemExit(f"ERR_FETCH: corpus download failed after 3 tries: {last}")
    rec = {"url": None if mock else lib.CORPUS_URL, "sha256": mc.sha256_file(path),
           "bytes": os.path.getsize(path), "fetched_utc": started, "mock": mock}
    meta = {}
    if os.path.exists(meta_path):
        with open(meta_path) as f:
            meta = json.load(f)
    meta[os.path.basename(path)] = rec
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)
    _vol_commit()
    return rec


def _build_data_body(local_manifest: dict, mock: bool) -> dict:
    _vol_reload()
    manifest = _assert_staging(local_manifest)
    mode = lib.e1_mode(REMOTE_ROOT, WORK, mock)
    argv = lib.build_data_argv(sys.executable, REMOTE_ROOT, WORK, mode, mock)
    corpus_sha = mc.sha256_file(lib.corpus_path(WORK, mock))
    payload = {"argv": argv, "corpusSha256": corpus_sha,
               "manifestDigest": lib.manifest_digest(manifest)}
    key = "build-data-mock" if mock else "build-data"
    outputs = [os.path.join(WORK, "data", "meta.json"),
               os.path.join(WORK, "data", "vocab.json")] + \
              [os.path.join(WORK, "data", f"seed{s}", split)
               for s in mode["seed_list"] for split in ("train.bin", "val.bin")]
    if mock:
        outputs.append(mode["tables"])
    if _stamp_ok(key, payload, outputs):
        print(f"data build stamped + outputs present, skipping ({key})")
        return {"skipped": True}
    if os.path.isdir(os.path.join(WORK, "data")):
        import shutil
        shutil.rmtree(os.path.join(WORK, "data"))  # never mix configs
    _run("10-build-data", argv, manifest=manifest, gpu_requested="none",
         stage="build_data", mock=mock)
    if mock:
        # run_all.sh [1b]: clearly-stamped MOCK vector tables (d=64).
        _run("12-mock-tables", lib.mock_tables_argv(sys.executable, REMOTE_ROOT,
             WORK, mode), manifest=manifest, gpu_requested="none",
             stage="build_data", mock=mock)
    _stamp_write(key, payload)
    _vol_commit()
    with open(os.path.join(WORK, "data", "meta.json")) as f:
        meta = json.load(f)
    return {"skipped": False, "attestedInAllSeeds": len(meta["attestedInAllSeeds"])}


def _lr_sweep_body(arm: str, lr: str, local_manifest: dict, mock: bool,
                   gpu_requested: str) -> dict:
    _vol_reload()
    manifest = _assert_staging(local_manifest)
    mode = lib.e1_mode(REMOTE_ROOT, WORK, mock)
    argv = lib.train_argv(sys.executable, REMOTE_ROOT, WORK, mode, arm, 0, lr,
                          sweep=True)  # run_all.sh sweeps seed 0 only (rule 5)
    summary = os.path.join(WORK, "ckpts", "sweep", lib.summary_name(arm, 0, lr, True))
    payload = {"argv": argv, "manifestDigest": lib.manifest_digest(manifest)}
    key = f"sweep-{arm}-lr{lr}" + ("-mock" if mock else "")
    if _stamp_ok(key, payload, [summary]):
        print(f"sweep stamped + outputs present, skipping ({key})")
    else:
        _run(f"20-sweep-{arm}-lr{lr}", argv, manifest=manifest,
             gpu_requested=gpu_requested, stage="lr_sweep", mock=mock)
        _stamp_write(key, payload)
        _vol_commit()
    with open(summary) as f:
        return json.load(f)


def _select_lrs_body(local_manifest: dict, mock: bool) -> dict:
    _vol_reload()
    manifest = _assert_staging(local_manifest)
    mode = lib.e1_mode(REMOTE_ROOT, WORK, mock)
    lrsel = os.path.join(WORK, "lr-selection.json")
    if len(mode["lrs"]) > 1:
        # run_all.sh's OWN Common-rule-5 snippet: best of sweep by val loss.
        argv = [sys.executable, "-c", lib.lr_selection_code(REMOTE_ROOT),
                os.path.join(WORK, "ckpts", "sweep"), lrsel]
    else:
        # run_all.sh's OWN mock fixed-LR snippet.
        argv = [sys.executable, "-c", lib.fixed_lr_code(REMOTE_ROOT),
                lrsel, mode["lrs"][0]]
    _run("30-select-lrs", argv, manifest=manifest, gpu_requested="none",
         stage="select_lrs", mock=mock)
    with open(lrsel) as f:
        sel = json.load(f)["selected"]
    missing = [a for a in mode["arms"] if a not in sel]
    if missing:
        raise SystemExit(f"ERR_LR_SELECTION: no sweep summaries for arms {missing}")
    _vol_commit()
    return sel


def _train_body(arm: str, seed: int, lr: str, local_manifest: dict, mock: bool,
                gpu_requested: str) -> dict:
    _vol_reload()
    manifest = _assert_staging(local_manifest)
    mode = lib.e1_mode(REMOTE_ROOT, WORK, mock)
    argv = lib.train_argv(sys.executable, REMOTE_ROOT, WORK, mode, arm, seed, lr)
    summary = os.path.join(WORK, "ckpts", lib.summary_name(arm, seed, lr, False))
    outputs = [summary] + [os.path.join(WORK, "ckpts", f"ckpt-{arm}-seed{seed}-{t}.pt")
                           for t in ("step0", "50pct", "100pct")]
    payload = {"argv": argv, "manifestDigest": lib.manifest_digest(manifest)}
    key = f"train-{arm}-seed{seed}" + ("-mock" if mock else "")
    if _stamp_ok(key, payload, outputs):
        print(f"train stamped + outputs present, skipping ({key})")
    else:
        _run(f"40-train-{arm}-seed{seed}", argv, manifest=manifest,
             gpu_requested=gpu_requested, stage="train_arm_seed", mock=mock)
        _stamp_write(key, payload)
        _vol_commit()
    with open(summary) as f:
        return json.load(f)


def _eval_body(arm: str, seed: int, tag: str, local_manifest: dict, mock: bool,
               gpu_requested: str) -> dict:
    _vol_reload()
    manifest = _assert_staging(local_manifest)
    ckpt = os.path.join(WORK, "ckpts", f"ckpt-{arm}-seed{seed}-{tag}.pt")
    if not os.path.exists(ckpt):  # run_all.sh eval_one parity: fail closed
        raise SystemExit(f"ERR_MISSING_CKPT: {ckpt} — grid incomplete")
    argv = lib.eval_argv(sys.executable, REMOTE_ROOT, WORK, arm, seed, tag)
    out = os.path.join(WORK, "evals", f"eval-{arm}-seed{seed}-{tag}.json")
    payload = {"argv": argv, "manifestDigest": lib.manifest_digest(manifest),
               "ckptSha256": mc.sha256_file(ckpt)}
    key = f"eval-{arm}-seed{seed}-{tag}" + ("-mock" if mock else "")
    if _stamp_ok(key, payload, [out]):
        print(f"eval stamped + output present, skipping ({key})")
    else:
        os.makedirs(os.path.dirname(out), exist_ok=True)
        _run(f"50-eval-{arm}-seed{seed}-{tag}", argv, manifest=manifest,
             gpu_requested=gpu_requested, stage="eval_ckpt", mock=mock)
        _stamp_write(key, payload)
        _vol_commit()
    return {"arm": arm, "seed": seed, "tag": tag, "eval": os.path.basename(out)}


def _collect_bundle(results_dir: str, extra: dict, log_prefixes: tuple,
                    log_name: str) -> dict:
    """{rel: bytes}: a results dir + assembled run log + per-run provenance
    sidecars. Script outputs are NEVER rewritten (byte-identity contract)."""
    files = mc.collect_dir(results_dir)
    for rel, data in extra.items():
        if rel in files:
            raise SystemExit(f"ERR_SIDECAR_COLLISION: {rel!r} emitted by a script")
        files[rel] = data
    logs_dir = os.path.join(WORK, "logs")
    parts = []
    if os.path.isdir(logs_dir):
        for name in sorted(os.listdir(logs_dir)):
            if name.startswith(log_prefixes):
                with open(os.path.join(logs_dir, name)) as f:
                    parts.append(f"===== {name} =====\n" + f.read())
    files[log_name] = "".join(parts).encode()
    prov_dir = os.path.join(WORK, "prov")
    if os.path.isdir(prov_dir):
        for name in sorted(os.listdir(prov_dir)):
            if name.startswith(log_prefixes):
                with open(os.path.join(prov_dir, name), "rb") as f:
                    files[f"provenance/{name}"] = f.read()
    return dict(sorted(files.items()))


E1_LOG_PREFIXES = ("00-", "10-", "12-", "20-", "30-", "40-", "50-", "60-")
E4_LOG_PREFIXES = ("70-", "72-", "80-", "90-", "95-")


def _stats_body(local_manifest: dict, mock: bool) -> dict:
    _vol_reload()
    manifest = _assert_staging(local_manifest)
    mode = lib.e1_mode(REMOTE_ROOT, WORK, mock)
    results = os.path.join(WORK, "results")
    os.makedirs(results, exist_ok=True)
    _run("60-stats-verdict", lib.stats_argv(sys.executable, REMOTE_ROOT, WORK, mode),
         manifest=manifest, gpu_requested="none", stage="stats_verdict", mock=mock)

    # run_all.sh [5/5] result copies, verbatim semantics.
    import shutil
    suffix = "mock" if mock else "full"
    shutil.copy(os.path.join(WORK, "lr-selection.json"),
                os.path.join(results, f"lr-selection-{suffix}.json"))
    # user-data-e1-pull.sh.tpl also publishes the raw lr-selection.json.
    shutil.copy(os.path.join(WORK, "lr-selection.json"),
                os.path.join(results, "lr-selection.json"))
    shutil.copy(os.path.join(WORK, "data", "meta.json"),
                os.path.join(results, f"data-meta-{suffix}.json"))
    evals_dir = os.path.join(WORK, "evals")
    for name in sorted(os.listdir(evals_dir)):
        if name.startswith("eval-") and name.endswith(".json"):
            dst = f"mock-{name}" if mock else name  # never shadowed by full runs
            shutil.copy(os.path.join(evals_dir, name), os.path.join(results, dst))

    if mock:
        # poc/e1/smoke parity: independent checkpoint-level assertions — the
        # frozen-row bit-identity proof runs against WRAPPER-produced ckpts.
        _run("60-check-smoke", lib.e1_check_smoke_argv(sys.executable, REMOTE_ROOT,
             WORK, mode), manifest=manifest, gpu_requested="none",
             stage="stats_verdict", mock=mock)

    # Train summaries (additive vs the AWS bundle: ckpts stay on the Volume,
    # so wallSeconds/frozenRowsBitIdentical would otherwise be uncollectable).
    extra = {}
    ckpts = os.path.join(WORK, "ckpts")
    for sub, prefix in ((ckpts, "summaries/"), (os.path.join(ckpts, "sweep"),
                                                "summaries/sweep/")):
        if os.path.isdir(sub):
            for name in sorted(os.listdir(sub)):
                if name.startswith("summary-") and name.endswith(".json"):
                    with open(os.path.join(sub, name), "rb") as f:
                        extra[prefix + name] = f.read()
    files = _collect_bundle(results, extra, E1_LOG_PREFIXES, E1_LOG_NAME)
    _vol_commit()
    return files


def _e4_build_body(local_manifest: dict, mock: bool) -> dict:
    _vol_reload()
    manifest = _assert_staging(local_manifest)
    mode = lib.e4_mode(REMOTE_ROOT, WORK, mock)

    # run_e4.sh [0/6] fail-closed pre-registration pins, in-container.
    pin = lib.gloss_pin(REMOTE_ROOT)
    got = mc.sha256_file(os.path.join(REMOTE_ROOT, "poc/e4/inputs/glosses.jsonl"))
    if got != pin:
        raise SystemExit(
            f"ERR_GLOSS_PIN: sha256(inputs/glosses.jsonl) = {got} != published {pin} "
            "(GLOSS-HASH.txt; a different gloss set is a NEW pre-registration)")
    vsha = mc.sha256_file(os.path.join(REMOTE_ROOT,
                                       "poc/e4/inputs/vector-tables-manifest.json"))
    _run("70-e4-pin-gate", [sys.executable, "-c", lib.pin_check_code(REMOTE_ROOT),
         os.path.join(REMOTE_ROOT, "poc/e4/inputs/holdout-manifest.json"), got, vsha],
         manifest=manifest, gpu_requested="none", stage="e4_build_emission", mock=mock)

    # run_e4.sh [1/6] parity: E4 consumes the E1 grid read-only; fail closed.
    for seed in mode["seed_list"]:
        ck = os.path.join(WORK, "ckpts", f"ckpt-kernel-frozen-seed{seed}-100pct.pt")
        if not os.path.exists(ck):
            raise SystemExit(f"ERR_MISSING_E1_CKPT: {ck} — run the E1 grid first")

    if mock:
        # run_e4.sh [3/6] mock: MOCK e4 tables (authored rows = E1 mock rows).
        _run("72-e4-mock-tables", lib.e4_mock_tables_argv(sys.executable,
             REMOTE_ROOT, WORK, mode), manifest=manifest, gpu_requested="none",
             stage="e4_build_emission", mock=mock)

    argv = lib.e4_build_argv(sys.executable, REMOTE_ROOT, WORK, mode)
    payload = {"argv": argv, "manifestDigest": lib.manifest_digest(manifest)}
    key = "e4-build" + ("-mock" if mock else "")
    outputs = [os.path.join(WORK, "e4data", n) for n in ("meta.json", "e4-vocab.json",
                                                         "eval.jsonl")]
    if _stamp_ok(key, payload, outputs):
        print(f"e4 emission build stamped + outputs present, skipping ({key})")
    else:
        _run("70-e4-build-emission", argv, manifest=manifest, gpu_requested="none",
             stage="e4_build_emission", mock=mock)
        _stamp_write(key, payload)
    # run_e4.sh [2/6]: publish the data meta (records the gloss OOV rate).
    import shutil
    os.makedirs(os.path.join(WORK, "e4results"), exist_ok=True)
    suffix = "mock" if mock else "full"
    shutil.copy(os.path.join(WORK, "e4data", "meta.json"),
                os.path.join(WORK, "e4results", f"e4-data-meta-{suffix}.json"))
    _vol_commit()
    with open(os.path.join(WORK, "e4data", "meta.json")) as f:
        meta = json.load(f)
    return {"counts": meta.get("counts", {}), "mock": bool(meta.get("mock"))}


def _e4_ft_body(arm: str, seed: int, local_manifest: dict, mock: bool,
                gpu_requested: str) -> dict:
    _vol_reload()
    manifest = _assert_staging(local_manifest)
    mode = lib.e4_mode(REMOTE_ROOT, WORK, mock)
    argv = lib.e4_ft_argv(sys.executable, REMOTE_ROOT, WORK, mode, arm, seed)
    summary = os.path.join(WORK, "e4ckpts", f"summary-e4-{arm}-seed{seed}.json")
    outputs = [summary, os.path.join(WORK, "e4ckpts", f"ckpt-e4-{arm}-seed{seed}-final.pt")]
    payload = {"argv": argv, "manifestDigest": lib.manifest_digest(manifest)}
    key = f"e4-ft-{arm}-seed{seed}" + ("-mock" if mock else "")
    if _stamp_ok(key, payload, outputs):
        print(f"e4 fine-tune stamped + outputs present, skipping ({key})")
    else:
        _run(f"80-e4-ft-{arm}-seed{seed}", argv, manifest=manifest,
             gpu_requested=gpu_requested, stage="e4_finetune", mock=mock)
        _stamp_write(key, payload)
        _vol_commit()
    with open(summary) as f:
        return json.load(f)


def _e4_eval_body(arm: str, seed: int, local_manifest: dict, mock: bool,
                  gpu_requested: str) -> dict:
    _vol_reload()
    manifest = _assert_staging(local_manifest)
    ckpt = os.path.join(WORK, "e4ckpts", f"ckpt-e4-{arm}-seed{seed}-final.pt")
    if not os.path.exists(ckpt):
        raise SystemExit(f"ERR_MISSING_CKPT: {ckpt} — E4 fine-tune incomplete")
    argv = lib.e4_eval_argv(sys.executable, REMOTE_ROOT, WORK, arm, seed)
    out = os.path.join(WORK, "e4evals", f"eval-e4-{arm}-seed{seed}.json")
    payload = {"argv": argv, "manifestDigest": lib.manifest_digest(manifest),
               "ckptSha256": mc.sha256_file(ckpt)}
    key = f"e4-eval-{arm}-seed{seed}" + ("-mock" if mock else "")
    if _stamp_ok(key, payload, [out]):
        print(f"e4 eval stamped + output present, skipping ({key})")
    else:
        os.makedirs(os.path.dirname(out), exist_ok=True)
        _run(f"90-e4-eval-{arm}-seed{seed}", argv, manifest=manifest,
             gpu_requested=gpu_requested, stage="e4_eval", mock=mock)
        _stamp_write(key, payload)
        _vol_commit()
    return {"arm": arm, "seed": seed, "eval": os.path.basename(out)}


def _e4_stats_body(local_manifest: dict, mock: bool) -> dict:
    _vol_reload()
    manifest = _assert_staging(local_manifest)
    mode = lib.e4_mode(REMOTE_ROOT, WORK, mock)
    results = os.path.join(WORK, "e4results")
    os.makedirs(results, exist_ok=True)
    _run("95-e4-stats", lib.e4_stats_argv(sys.executable, REMOTE_ROOT, WORK, mode),
         manifest=manifest, gpu_requested="none", stage="e4_stats", mock=mock)

    import shutil
    evals_dir = os.path.join(WORK, "e4evals")
    if mock:
        for name in sorted(os.listdir(evals_dir)):
            shutil.copy(os.path.join(evals_dir, name),
                        os.path.join(results, f"mock-{name}"))
        # run_e4.sh mock tail: independent frozen-row-through-fine-tune proof.
        _run("95-e4-check-smoke", lib.e4_check_smoke_argv(sys.executable,
             REMOTE_ROOT, WORK, mode), manifest=manifest, gpu_requested="none",
             stage="e4_stats", mock=mock)
    else:
        for name in sorted(os.listdir(evals_dir)):
            shutil.copy(os.path.join(evals_dir, name), os.path.join(results, name))
        ck = os.path.join(WORK, "e4ckpts")
        for name in sorted(os.listdir(ck)):
            if (name.startswith("summary-e4-") and name.endswith(".json")) or \
               (name.startswith("train-e4-") and name.endswith(".jsonl")):
                shutil.copy(os.path.join(ck, name), os.path.join(results, name))
    files = _collect_bundle(results, {}, E4_LOG_PREFIXES, E4_LOG_NAME)
    _vol_commit()
    return files


def _salvage_body() -> dict:
    """Failure-trace parity with collect-e1.sh: whatever logs/provenance/
    partial results exist on the Volume, as bytes (never checkpoints)."""
    _vol_reload()
    files = {}
    for sub in ("logs", "prov", "results", "e4results"):
        d = os.path.join(WORK, sub)
        if os.path.isdir(d):
            for rel, data in mc.collect_dir(d).items():
                files[f"{sub}/{rel}"] = data
    return dict(sorted(files.items()))


# ---------------------------------------------------------------------------
# Modal function registrations. GPU stages come in A10G (default; g5.xlarge
# parity) and T4 flavours — same unchanged scripts, only the GPU differs.
# Timeouts: cost-table estimate x1.5 (+5 min overhead); modal_e1e4_lib.EST_MIN.
# ---------------------------------------------------------------------------

def _t(stage, gpu="A10G"):
    return lib.timeout_s(stage, gpu)


@app.function(image=image, volumes=_VOL, timeout=_t("fetch_corpus"), cpu=2, memory=4096)
def fetch_corpus(local_manifest: dict = None, mock: bool = False) -> dict:  # noqa: RUF013
    return _fetch_corpus_body(local_manifest or {}, mock)


@app.function(image=image, volumes=_VOL, timeout=_t("build_data"), cpu=4, memory=32768)
def build_data(local_manifest: dict = None, mock: bool = False) -> dict:  # noqa: RUF013
    return _build_data_body(local_manifest or {}, mock)


@app.function(image=image, volumes=_VOL, gpu="A10G", timeout=_t("lr_sweep"),
              cpu=4, memory=16384)
def lr_sweep(arm: str, lr: str, local_manifest: dict = None, mock: bool = False) -> dict:  # noqa: RUF013
    return _lr_sweep_body(arm, lr, local_manifest or {}, mock, "A10G")


@app.function(image=image, volumes=_VOL, gpu="T4", timeout=_t("lr_sweep", "T4"),
              cpu=4, memory=16384)
def lr_sweep_t4(arm: str, lr: str, local_manifest: dict = None, mock: bool = False) -> dict:  # noqa: RUF013
    return _lr_sweep_body(arm, lr, local_manifest or {}, mock, "T4")


@app.function(image=image, volumes=_VOL, timeout=_t("select_lrs"), cpu=2, memory=4096)
def select_lrs(local_manifest: dict = None, mock: bool = False) -> dict:  # noqa: RUF013
    return _select_lrs_body(local_manifest or {}, mock)


@app.function(image=image, volumes=_VOL, gpu="A10G", timeout=_t("train_arm_seed"),
              cpu=4, memory=16384)
def train_arm_seed(arm: str, seed: int, lr: str, local_manifest: dict = None,  # noqa: RUF013
                   mock: bool = False) -> dict:
    return _train_body(arm, seed, lr, local_manifest or {}, mock, "A10G")


@app.function(image=image, volumes=_VOL, gpu="T4", timeout=_t("train_arm_seed", "T4"),
              cpu=4, memory=16384)
def train_arm_seed_t4(arm: str, seed: int, lr: str, local_manifest: dict = None,  # noqa: RUF013
                      mock: bool = False) -> dict:
    return _train_body(arm, seed, lr, local_manifest or {}, mock, "T4")


@app.function(image=image, volumes=_VOL, gpu="A10G", timeout=_t("eval_ckpt"),
              cpu=2, memory=8192)
def eval_ckpt(arm: str, seed: int, tag: str, local_manifest: dict = None,  # noqa: RUF013
              mock: bool = False) -> dict:
    return _eval_body(arm, seed, tag, local_manifest or {}, mock, "A10G")


@app.function(image=image, volumes=_VOL, gpu="T4", timeout=_t("eval_ckpt", "T4"),
              cpu=2, memory=8192)
def eval_ckpt_t4(arm: str, seed: int, tag: str, local_manifest: dict = None,  # noqa: RUF013
                 mock: bool = False) -> dict:
    return _eval_body(arm, seed, tag, local_manifest or {}, mock, "T4")


@app.function(image=image, volumes=_VOL, timeout=_t("stats_verdict"), cpu=4, memory=8192)
def stats_verdict(local_manifest: dict = None, mock: bool = False) -> dict:  # noqa: RUF013
    return _stats_body(local_manifest or {}, mock)


@app.function(image=image, volumes=_VOL, timeout=_t("e4_build_emission"),
              cpu=4, memory=8192)
def e4_build_emission(local_manifest: dict = None, mock: bool = False) -> dict:  # noqa: RUF013
    return _e4_build_body(local_manifest or {}, mock)


@app.function(image=image, volumes=_VOL, gpu="A10G", timeout=_t("e4_finetune"),
              cpu=4, memory=16384)
def e4_finetune(arm: str, seed: int, local_manifest: dict = None,  # noqa: RUF013
                mock: bool = False) -> dict:
    return _e4_ft_body(arm, seed, local_manifest or {}, mock, "A10G")


@app.function(image=image, volumes=_VOL, gpu="T4", timeout=_t("e4_finetune", "T4"),
              cpu=4, memory=16384)
def e4_finetune_t4(arm: str, seed: int, local_manifest: dict = None,  # noqa: RUF013
                   mock: bool = False) -> dict:
    return _e4_ft_body(arm, seed, local_manifest or {}, mock, "T4")


@app.function(image=image, volumes=_VOL, gpu="A10G", timeout=_t("e4_eval"),
              cpu=2, memory=8192)
def e4_eval(arm: str, seed: int, local_manifest: dict = None,  # noqa: RUF013
            mock: bool = False) -> dict:
    return _e4_eval_body(arm, seed, local_manifest or {}, mock, "A10G")


@app.function(image=image, volumes=_VOL, gpu="T4", timeout=_t("e4_eval", "T4"),
              cpu=2, memory=8192)
def e4_eval_t4(arm: str, seed: int, local_manifest: dict = None,  # noqa: RUF013
               mock: bool = False) -> dict:
    return _e4_eval_body(arm, seed, local_manifest or {}, mock, "T4")


@app.function(image=image, volumes=_VOL, timeout=_t("e4_stats"), cpu=4, memory=8192)
def e4_stats(local_manifest: dict = None, mock: bool = False) -> dict:  # noqa: RUF013
    return _e4_stats_body(local_manifest or {}, mock)


@app.function(image=image, volumes=_VOL, timeout=_t("salvage"), cpu=2, memory=4096)
def salvage() -> dict:
    return _salvage_body()


FUNCTION_SETS = {
    "A10G": {"fetch_corpus": fetch_corpus, "build_data": build_data,
             "lr_sweep": lr_sweep, "select_lrs": select_lrs,
             "train_arm_seed": train_arm_seed, "eval_ckpt": eval_ckpt,
             "stats_verdict": stats_verdict, "e4_build_emission": e4_build_emission,
             "e4_finetune": e4_finetune, "e4_eval": e4_eval, "e4_stats": e4_stats},
    "T4": {"fetch_corpus": fetch_corpus, "build_data": build_data,
           "lr_sweep": lr_sweep_t4, "select_lrs": select_lrs,
           "train_arm_seed": train_arm_seed_t4, "eval_ckpt": eval_ckpt_t4,
           "stats_verdict": stats_verdict, "e4_build_emission": e4_build_emission,
           "e4_finetune": e4_finetune_t4, "e4_eval": e4_eval_t4, "e4_stats": e4_stats},
}


# ---------------------------------------------------------------------------
# Orchestration (coordinator side)
# ---------------------------------------------------------------------------


def _orchestrate(fns: dict, manifest: dict, mock: bool, skip_e4: bool):
    m1 = lib.e1_mode(str(REPO_ROOT), WORK, mock)
    fns["fetch_corpus"].remote(manifest, mock)
    print("== [1] corpus staged ==")
    build = fns["build_data"].remote(manifest, mock)
    print(f"== [2] data build done: {build} ==")
    if len(m1["lrs"]) > 1:
        jobs = [(a, lr, manifest, mock) for a in m1["arms"] for lr in m1["lrs"]]
        print(f"== [3] LR sweep: {len(jobs)} parallel runs (Common rule 5) ==")
        list(fns["lr_sweep"].starmap(jobs))
    else:
        print("== [3] single-LR mode: sweep skipped (run_all.sh parity) ==")
    sel = fns["select_lrs"].remote(manifest, mock)
    print(f"== [4] LR selection: "
          f"{json.dumps({a: sel[a]['lr'] for a in sorted(sel)})} ==")
    grid = [(a, s, str(sel[a]["lr"]), manifest, mock)
            for a in m1["arms"] for s in m1["seed_list"]]
    print(f"== [5] training grid: {len(grid)} parallel runs ==")
    summaries = list(fns["train_arm_seed"].starmap(grid))
    bad = [s for s in summaries if s.get("frozen") and
           s.get("frozenRowsBitIdentical") is not True]
    if bad:
        raise SystemExit(f"ERR_FROZEN_SUMMARY: {bad}")
    ev = [(a, s, t, manifest, mock) for (a, s, t) in lib.eval_jobs(m1["seed_list"])]
    print(f"== [6] evals: {len(ev)} parallel runs (incl. step-0 baselines) ==")
    list(fns["eval_ckpt"].starmap(ev))
    print("== [7] pre-registered statistics + verdict ==")
    e1_files = fns["stats_verdict"].remote(manifest, mock)
    e4_files = None
    if not skip_e4:
        m4 = lib.e4_mode(str(REPO_ROOT), WORK, mock)
        print("== [8] E4 chain: pin gates + emission data build ==")
        fns["e4_build_emission"].remote(manifest, mock)
        ft = [(a, s, manifest, mock) for a in m4["arms"] for s in m4["seed_list"]]
        print(f"== [9] E4 emission fine-tunes: {len(ft)} parallel runs ==")
        list(fns["e4_finetune"].starmap(ft))
        print(f"== [10] E4 evals: {len(ft)} parallel runs ==")
        list(fns["e4_eval"].starmap(ft))
        print("== [11] E4 pre-registered statistics + verdict ==")
        e4_files = fns["e4_stats"].remote(manifest, mock)
    return e1_files, e4_files


def _echo_verdict(dest: Path, prefix: str, label: str) -> None:
    """collect-e1.sh check_verdict parity: parse + echo, fail closed."""
    cands = sorted(p for p in dest.glob(f"{prefix}*.json"))
    if not cands:
        raise SystemExit(f"ERR_NO_VERDICT: no {prefix}*.json in {dest}")
    j = json.loads(cands[0].read_text())
    print(f"{label} verdict JSON OK: {cands[0]}")
    print(f"VERDICT: {j['verdict']}  (mock={j.get('mock')})")


def _print_plan(gpu: str, mock: bool, skip_e4: bool) -> None:
    plan = lib.build_plan(str(REPO_ROOT), gpu, mock, skip_e4)
    tot = lib.plan_totals(plan, gpu, mock)
    print(f"kot-e1e4 --dry-plan  (gpu={gpu} mock={mock} skip_e4={skip_e4}; "
          f"NO authenticated Modal call is made)")
    print(f"{'stage':<20}{'kind':<6}{'calls':>6}{'est min/call':>14}"
          f"{'timeout min':>13}  example calls")
    for stage, kind, n, est, calls in plan:
        t_min = lib.timeout_s(stage, gpu if kind == "gpu" else "A10G") // 60
        ex = ", ".join(str(c) for c in calls[:3]) + (" ..." if len(calls) > 3 else "")
        print(f"{stage:<20}{kind:<6}{n:>6}{est:>14.1f}{t_min:>13}  {ex}")
    print(f"\ntotals: {tot['gpu_h']:.1f} {gpu}-h (parallel; wall ~{tot['wall_h']:.1f} h "
          f"— serial AWS path is ~20-23 h), {tot['cpu_h']:.1f} CPU-stage-h")
    print(f"estimate: ~${tot['gpu_cost']:.0f} GPU + ~${tot['cpu_cost']:.0f} CPU/mem "
          f"= ~${tot['total_cost']:.0f} "
          f"(rates {json.dumps(lib.RATES)}; verify at modal.com/pricing)")
    print(f"worst case if EVERY GPU call ran to its sized timeout: "
          f"~${tot['worst_case_gpu_cost']:.0f} GPU "
          f"(AWS failsafe analogue: ~$42 at 42 h on-demand)")
    if mock:
        print("mock mode: tiny CPU-device configs — minutes of container time, "
              "~$0.10-0.50 total")


@app.local_entrypoint()
def main(gpu: str = "A10G", mock: bool = False, skip_e4: bool = False,
         dry_plan: bool = False, out_root: str = "") -> None:
    gpu = gpu.upper()
    if gpu not in GPU_CHOICES:
        raise SystemExit(f"ERR_GPU: --gpu must be one of {GPU_CHOICES}, got {gpu!r}")
    if dry_plan:
        _print_plan(gpu, mock, skip_e4)
        return

    manifest = lib.tree_manifest(str(REPO_ROOT))
    print(f"kot-e1e4 via Modal: gpu={gpu} mock={mock} skip_e4={skip_e4} "
          f"({len(manifest)} staged files, manifest {lib.manifest_digest(manifest)[:12]}…)")
    fns = FUNCTION_SETS[gpu]

    stamp = time.strftime("%Y%m%d-%H%M%S", time.gmtime()) + "-modal"
    dest = Path(out_root) / stamp if out_root else INCOMING_ROOT / stamp
    try:
        e1_files, e4_files = _orchestrate(fns, manifest, mock, skip_e4)
    except Exception:
        # collect-e1.sh failure-trace parity: pull whatever logs/provenance/
        # partials exist off the Volume BEFORE surfacing the failure.
        try:
            trace = salvage.remote()
            fdest = dest.parent / (dest.name + "-FAILED")
            mc.unpack_files(trace, str(fdest))
            (fdest / "RUNNER_EXIT").write_text(
                lib.runner_exit_text(1, "skipped" if skip_e4 else 1))
            print(f"FAILED — salvaged {len(trace)} trace files to {fdest}", file=sys.stderr)
        except Exception as se:  # noqa: BLE001 — the original error must surface
            print(f"FAILED — salvage also failed: {se}", file=sys.stderr)
        raise

    mc.unpack_files(e1_files, str(dest))
    if e4_files is not None:
        mc.unpack_files(e4_files, str(dest / "e4"))
    (dest / "RUNNER_EXIT").write_text(  # user-data-e1-pull.sh.tpl format
        lib.runner_exit_text(0, "skipped" if skip_e4 else 0))

    # Coordinator-side provenance sidecar (per-run sidecars are already under
    # provenance/): modal client + image id + the staged manifest. No tokens.
    try:
        image_id = image.object_id
    except Exception:
        image_id = None
    prov = {
        "provenance_version": 1, "transport": "modal", "experiment": "E1+E4",
        "gpu_requested": gpu, "mock": mock, "skip_e4": skip_e4,
        "staged_sha256": manifest,
        "coordinator": {"modal_client": modal.__version__,
                        "image_object_id": image_id,
                        "local_manifest_matched": True,  # containers failed closed otherwise
                        "collected_utc": mc.utcnow_iso()},
    }
    (dest / PROVENANCE_NAME).write_text(json.dumps(prov, indent=2, sort_keys=True) + "\n")

    n = len(e1_files) + (len(e4_files) if e4_files else 0) + 2
    print(f"\nwrote {n} files to {dest}")
    _echo_verdict(dest, "verdict-e1", "E1")
    if e4_files is not None:
        _echo_verdict(dest / "e4", "verdict-e4", "E4")
    print("done — review and commit deliberately (results are NOT auto-committed); "
          "checkpoints/shards remain on Volume kot-e1-work "
          "(`modal volume delete kot-e1-work` after the campaign)")


if __name__ == "__main__":
    # Token-free entry: `python3 modal_e1e4.py --dry-plan [--gpu t4] [--mock]`
    # prints the full call graph + GPU-h + $ estimate with ZERO Modal calls.
    import argparse
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-plan", action="store_true")
    ap.add_argument("--gpu", default="A10G")
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--skip-e4", action="store_true")
    args = ap.parse_args()
    if not args.dry_plan:
        raise SystemExit("direct execution supports --dry-plan only; "
                         "use `modal run poc/modal/modal_e1e4.py` for real runs")
    _print_plan(args.gpu.upper(), args.mock, args.skip_e4)
