#!/usr/bin/env bash
# =============================================================================
# f1k_worker.sh — runs ON the GCP Spot VM. Autonomous, resume-safe, fail-closed.
#
# SCOPE (this script deliberately STOPS at the affordability gate — it NEVER
# spends the construction/campaign dollars autonomously; those are separately
# gated on the measured bring-up + affordability result, per the frozen
# addendum-(7)/(6)/(5) ordering + the Fable addendum-6 inference-method
# handoff). It orchestrates ONLY already-authored, gate-0-reviewed artifacts:
#   1. STAGE   the GLM-5.2 int4 estate: restore from the same-region GCS
#      mirror if present (cheap, preemption-safe), else HF snapshot_download to
#      local NVMe then mirror to GCS. Pin the weight content hash.
#   2. BUILD   the SCORING engine (colibri + KaE patch ONLY, phase separation)
#      via bringup_gcp.sh, and the CONSTRUCTION engine (colibri + KaE + the
#      kot-f1k-dump patch) via the dump-patch real-checks.sh battery.
#   3. BRING-UP GATE (KaE): bringup_gcp.sh — 44/44 test_kae; objdump
#      inert-by-default checks are ADVISORY-ONLY on this box (bead f2uk /
#      ASM-2503: gcc-version-brittle even at reference flags; fail-closed
#      objdump lives off-box on the gcc-11.5 measurement basis). The
#      AUTHORITATIVE inertness proof is the FUNCTIONAL gate below.
#   4. DUMP BRING-UP GATE — the 3 PATCH-NOTES preconditions on the REAL binary:
#        (b) unarmed byte-identity vs the KaE-only engine + test_kae 44/44 +
#            test_kae_dump 43/43 + objdump per-function inertness on PRODUCTION
#            flags  [dump-patch/real-checks.sh, run here against the pinned
#            KaE tree built above];
#        (a) tiny real dump completes + kot-f1k-tok/1 token-id consistency;
#        (c) independent MoE-input sum cross-check on MIXED positions — the
#            hard content gate; the worker prepares the dumped sums; the RUNNER
#            finalizes the independent comparison ON-BOX (its correctness can
#            not be validated blind, so it is a runner-confirmed PASS, not an
#            autonomous one — see README "Dump bring-up gate").
#   5. REAL-CORPUS BRING-UP GATE INPUTS (F1K-BRINGUP-GATE-FIX.md v1, closing
#      GAP-1/2/3): tokenize the frozen corpora with the staged GLM-5.2
#      tokenizer (measured f + per-item T), realize the frozen stratified
#      timing sample, time it per-item (unpinned T1 -> bring-up pin file;
#      pinned T2), and write gate-inputs.json. The GREEN/STOP verdict is the
#      control box's `f1k_gcp.py gate` (kot-f1k-bringup-gate/2); the
#      synthetic functional-gate blend stays a SECONDARY diagnostic ONLY.
#      Then STOP + heartbeat DONE.
#
# Heartbeat + all artifacts are mirrored to GCS ($BUCKET/f1k/bringup) so a spot
# preemption just re-runs this script (idempotent; staging restores from GCS).
# =============================================================================
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

atomic_publish_file() {  # $1=complete temp file; $2=final path (same dir)
  [ "$#" -eq 2 ] || { echo "atomic_publish_file: expected SRC DEST" >&2; return 2; }
  local src="$1" dest="$2" src_dir dest_dir
  [ -f "$src" ] && [ ! -L "$src" ] && [ -s "$src" ] \
    || { echo "atomic_publish_file: source is not a nonempty regular file: $src" >&2; return 2; }
  src_dir=$(cd "$(dirname -- "$src")" && pwd -P) || return 2
  dest_dir=$(cd "$(dirname -- "$dest")" && pwd -P) || return 2
  [ "$src_dir" = "$dest_dir" ] \
    || { echo "atomic_publish_file: SRC and DEST must share a directory" >&2; return 2; }
  python3 - "$src" <<'PY'
import os, sys
with open(sys.argv[1], "rb") as handle:
    os.fsync(handle.fileno())
PY
  # Test-only preemption point: the complete temp remains; DEST is untouched.
  [ "${KOT_F1K_TEST_INTERRUPT_BEFORE_RENAME:-0}" != 1 ] || return 99
  python3 - "$src" "$dest" <<'PY'
import os, stat, sys
src, dest = sys.argv[1:]
try:
    mode = os.lstat(dest).st_mode
except FileNotFoundError:
    pass
else:
    if stat.S_ISLNK(mode) or not stat.S_ISREG(mode):
        raise SystemExit("refusing non-regular destination: %s" % dest)
os.replace(src, dest)
dir_fd = os.open(os.path.dirname(dest) or ".",
                 os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
try:
    os.fsync(dir_fd)
finally:
    os.close(dir_fd)
PY
}

write_timing_result() {  # $1=phase $2=sample_id $3=complete result temp
  [ "$#" -eq 3 ] || { echo "write_timing_result: expected PHASE SAMPLE_ID RESULT_TMP" >&2; return 2; }
  local phase="$1" sid="$2" result_tmp="$3" result_dir dest sha
  case "$phase" in t1|t2) ;; *) echo "write_timing_result: invalid phase $phase" >&2; return 2;; esac
  [[ "$sid" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ ]] \
    || { echo "write_timing_result: unsafe sample_id $sid" >&2; return 2; }
  result_dir="$GATE/$phase-results"
  mkdir -p "$result_dir"
  dest="$result_dir/$phase-$sid.json"
  [ -s "$result_tmp" ] \
    || { echo "write_timing_result: empty result temp $result_tmp" >&2; return 2; }
  sha=$(python3 - "$HERE" "$phase" "$sid" "$result_tmp" <<'PY'
import json, math, sys
sys.path.insert(0, sys.argv[1])
import f1k_ops
phase, sid, path = sys.argv[2:]
with open(path, encoding="utf-8") as handle:
    record = json.load(handle)
if not isinstance(record, dict) or record.get("phase") != phase \
        or record.get("sample_id") != sid:
    raise SystemExit("timing temp phase/sample_id mismatch")
seconds = record.get("s")
timer_n = record.get("timer_n")
boot_id = record.get("boot_id")
if isinstance(seconds, bool) or not isinstance(seconds, (int, float)) \
        or not math.isfinite(seconds) or seconds <= 0:
    raise SystemExit("timing temp has invalid s")
if isinstance(timer_n, bool) or not isinstance(timer_n, int) or timer_n < 1:
    raise SystemExit("timing temp has invalid timer_n")
if not isinstance(boot_id, str) or not boot_id.strip():
    raise SystemExit("timing temp has invalid boot_id")
if phase == "t2" and not isinstance(record.get("pin_evidence"), str):
    raise SystemExit("T2 timing temp has invalid pin_evidence")
print(f1k_ops.atomic_write_json(path, record, mode=0o600))
PY
) || return
  atomic_publish_file "$result_tmp" "$dest" || return
  echo "timing result published: $phase/$sid sha256=$sha"
}

validate_timing_results() {  # $1=phase $2=directory $3..=expected ids
  local phase="$1" directory="$2"
  shift 2
  python3 - "$HERE" "$directory" "$phase" "$@" <<'PY'
import sys
sys.path.insert(0, sys.argv[1])
from f1k_bringup_gate import _read_sample_results
_read_sample_results(sys.argv[2], phase=sys.argv[3], expected_ids=sys.argv[4:])
PY
}

emit_construction_ready() {
  local fixture_root="${KOT_F1K_READY_FIXTURE_ROOT:-}"
  local home_dir nvme_root payload_root gate_dir estate_dir scratch_dir build_dir
  local ready_path identity_fixture now_utc rundir workdir out
  if [ -n "$fixture_root" ]; then
    home_dir="$fixture_root/home"
    nvme_root="$fixture_root/mnt/nvme"
    identity_fixture="$fixture_root/identity.json"
    now_utc="${KOT_F1K_READY_TEST_NOW:-2026-07-18T12:00:00Z}"
  else
    home_dir="${HOME:-/home/ubuntu}"
    nvme_root="/mnt/nvme"
    identity_fixture=""
    now_utc=""
  fi
  payload_root="$home_dir/f1k"
  gate_dir="$home_dir/f1k-gate"
  estate_dir="$nvme_root/glm52_i4"
  scratch_dir="$nvme_root/kot-f1k/construction"
  build_dir="$home_dir"
  ready_path="$gate_dir/construction-ready.json"
  rundir="$gate_dir/guard"
  workdir="$scratch_dir/work"
  out="$scratch_dir/out"
  mkdir -p "$rundir" "$workdir" "$out"
  local python_bin
  python_bin=$(readlink -f -- "$(command -v python3)") || return 1

  python3 - "$HERE" "$ready_path" "$payload_root" \
    "$payload_root/bundle-manifest.json" \
    "$payload_root/data/f1k-carriers-v1/generator/construction-manifest.jsonl" \
    "$payload_root/poc/glm52-probe/f1k-harness/build_carriers.py" \
    "$build_dir/colibri-construct/c/glm" "$estate_dir" \
    "$payload_root/tok_glm52.py" \
    "$estate_dir/tokenizer.json" \
    "$payload_root/dump-patch/kot-f1k-dump.patch" \
    "$gate_dir/glm52-weights-hash.json" \
    "$gate_dir/gate-tokens/tokens-full.jsonl" \
    "$gate_dir/pin_bringup.stats" \
    "$gate_dir/gate-inputs.json" "$gate_dir/gate-sample/timing-sample.json" \
    "$gate_dir" "$python_bin" "$rundir" "$workdir" "$out" \
    "$identity_fixture" "$now_utc" <<'PY'
import datetime
import hashlib
import json
import math
import os
import re
import stat
import sys
from pathlib import Path

(here, ready_s, payload_s, bundle_s, source_s, builder_s, engine_s,
 estate_s, tok_wrapper_s, tok_artifact_s, dump_patch_s, weights_s, tokens_s,
 pin_s, gate_inputs_s, sample_s, gate_dir_s, python_s, rundir_s, workdir_s,
 out_s, identity_fixture_s, now_s) = sys.argv[1:]
sys.path.insert(0, here)
import f1k_ops
from f1k_bringup_gate import _read_sample_results

BUILDER_PIN = "a92be3e4fe535c1dfefc41e2a422e010d25e8e40cf8e4cc123e7d829d63e9e61"
SOURCE_PIN = "a8cb3a8aee9730107bf04749988cb7d3438132a39ad19095cecd5283109f906c"
DUMP_PATCH_PIN = "fb5d2f3558351f608afccb29ab974aac2a62182ad67f27ec5c3c5f3e9eab0097"
SHA_RE = re.compile(r"[0-9a-f]{64}\Z")
RFC3339_RE = re.compile(
    r"[0-9]{4}-[0-9]{2}-[0-9]{2}T"
    r"[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]+)?Z\Z"
)


class ReadyRefusal(RuntimeError):
    pass


def refuse(message):
    raise ReadyRefusal(message)


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def strict_path(raw, *, kind):
    if not isinstance(raw, str) or not raw or "\x00" in raw \
            or not os.path.isabs(raw) or os.path.normpath(raw) != raw:
        refuse("%s path is not normalized absolute: %r" % (kind, raw))
    path = Path(raw)
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current /= part
        try:
            mode = current.lstat().st_mode
        except OSError as exc:
            refuse("cannot lstat %s path %s: %s" % (kind, current, exc))
        if stat.S_ISLNK(mode):
            refuse("%s path is symlinked: %s" % (kind, current))
    mode = path.lstat().st_mode
    if kind == "directory":
        if not stat.S_ISDIR(mode):
            refuse("not a directory: %s" % path)
    elif not stat.S_ISREG(mode):
        refuse("not a regular file: %s" % path)
    return path


def strict_sha(value, field):
    if not isinstance(value, str) or SHA_RE.fullmatch(value) is None:
        refuse("%s is not a lowercase SHA-256" % field)
    return value


def load_json(path, field):
    try:
        with open(path, encoding="utf-8") as handle:
            value = json.load(handle)
    except (OSError, UnicodeError, ValueError) as exc:
        refuse("cannot load %s JSON %s: %s" % (field, path, exc))
    if not isinstance(value, dict):
        refuse("%s must be a JSON object" % field)
    return value


def clear_ready(path_text):
    if not os.path.isabs(path_text) or os.path.normpath(path_text) != path_text:
        refuse("ready destination is not normalized absolute")
    path = Path(path_text)
    strict_path(os.fspath(path.parent), kind="directory")
    try:
        mode = path.lstat().st_mode
    except FileNotFoundError:
        return path
    if not (stat.S_ISREG(mode) or stat.S_ISLNK(mode)):
        refuse("ready destination is neither regular nor symlink: %s" % path)
    path.unlink()
    dir_fd = os.open(
        os.fspath(path.parent),
        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0),
    )
    try:
        os.fsync(dir_fd)
    finally:
        os.close(dir_fd)
    return path


def literal_pass(path, field):
    raw = path.read_bytes()
    if raw not in (b"PASS", b"PASS\n"):
        refuse("%s status is not literal PASS" % field)


def finite_positive(value, field):
    if isinstance(value, bool) or not isinstance(value, (int, float)) \
            or not math.isfinite(value) or value <= 0:
        refuse("%s must be finite and positive" % field)
    return value


def validate_argv(value, field):
    if not isinstance(value, list) or not value \
            or not all(isinstance(item, str) and item for item in value):
        refuse("%s must be a nonempty string argv" % field)
    if not os.path.isabs(value[0]):
        refuse("%s executable is relative" % field)
    strict_path(value[0], kind="file")
    return value


def read_results(directory, phase, expected, boot_id):
    strict_path(os.fspath(directory), kind="directory")
    by_id = _read_sample_results(
        os.fspath(directory), phase=phase, expected_ids=expected
    )
    records = []
    for sid in expected:
        strict_path(
            os.fspath(directory / ("%s-%s.json" % (phase, sid))),
            kind="file",
        )
        record = by_id[sid]
        if record.get("boot_id") != boot_id:
            refuse(
                "%s/%s boot_id does not match live identity" % (phase, sid)
            )
        records.append(record)
    return records


def main():
    ready = clear_ready(ready_s)
    payload = strict_path(payload_s, kind="directory")
    gate_dir = strict_path(gate_dir_s, kind="directory")
    estate = strict_path(estate_s, kind="directory")
    rundir = strict_path(rundir_s, kind="directory")
    workdir = strict_path(workdir_s, kind="directory")
    out = strict_path(out_s, kind="directory")

    file_paths = {
        "bundle": strict_path(bundle_s, kind="file"),
        "source": strict_path(source_s, kind="file"),
        "builder": strict_path(builder_s, kind="file"),
        "engine": strict_path(engine_s, kind="file"),
        "tok_wrapper": strict_path(tok_wrapper_s, kind="file"),
        "tok_artifact": strict_path(tok_artifact_s, kind="file"),
        "dump_patch": strict_path(dump_patch_s, kind="file"),
        "weights": strict_path(weights_s, kind="file"),
        "tokens": strict_path(tokens_s, kind="file"),
        "pin": strict_path(pin_s, kind="file"),
        "gate_inputs": strict_path(gate_inputs_s, kind="file"),
        "sample": strict_path(sample_s, kind="file"),
        "python": strict_path(python_s, kind="file"),
    }
    for key in ("engine", "python"):
        if not os.access(file_paths[key], os.X_OK):
            refuse("%s is not executable: %s" % (key, file_paths[key]))

    shas = {key: sha256_file(path) for key, path in file_paths.items()}
    if shas["builder"] != BUILDER_PIN:
        refuse(
            "build_carriers.py drift: %s != %s"
            % (shas["builder"], BUILDER_PIN)
        )
    if shas["source"] != SOURCE_PIN:
        refuse("construction manifest drift")
    if shas["dump_patch"] != DUMP_PATCH_PIN:
        refuse("dump patch drift")

    bundle = load_json(file_paths["bundle"], "bundle manifest")
    if not bundle:
        refuse("bundle manifest is empty")
    for rel, expected_sha in bundle.items():
        strict_sha(expected_sha, "bundle[%r]" % rel)
        if not isinstance(rel, str) or not rel or os.path.isabs(rel) \
                or os.path.normpath(rel) != rel or rel.startswith("../"):
            refuse("unsafe bundle manifest path: %r" % rel)
        bundled = strict_path(os.fspath(payload / rel), kind="file")
        if sha256_file(bundled) != expected_sha:
            refuse("bundle SHA mismatch: %s" % rel)
    required_bundle = {
        os.path.relpath(file_paths["source"], payload): SOURCE_PIN,
        os.path.relpath(file_paths["builder"], payload): BUILDER_PIN,
        os.path.relpath(
            file_paths["tok_wrapper"], payload
        ): shas["tok_wrapper"],
        os.path.relpath(file_paths["dump_patch"], payload): DUMP_PATCH_PIN,
    }
    for rel, expected_sha in required_bundle.items():
        if bundle.get(rel) != expected_sha:
            refuse(
                "bundle manifest does not bind required payload %s" % rel
            )

    status_paths = {
        "dump-a": strict_path(
            os.fspath(gate_dir / "tiny-dump.status"), kind="file"
        ),
        "dump-b": strict_path(
            os.fspath(gate_dir / "dump-b.status"), kind="file"
        ),
        "dump-c": strict_path(
            os.fspath(gate_dir / "moe-sum-crosscheck.status"), kind="file"
        ),
    }
    for name, path in status_paths.items():
        literal_pass(path, name)
    kae_log = strict_path(
        os.fspath(gate_dir / "kae-bringup.log"), kind="file"
    )
    if b"BRING-UP OK (KaE)" not in kae_log.read_bytes():
        refuse("KaE bring-up log has no PASS banner")
    dump_log = strict_path(
        os.fspath(gate_dir / "dump-realchecks.log"), kind="file"
    )
    dump_log_raw = dump_log.read_bytes()
    if b"test_kae: 44/44" not in dump_log_raw \
            or b"test_kae_dump: 43/43" not in dump_log_raw:
        refuse("dump real-check evidence is incomplete")
    functional_path = strict_path(
        os.fspath(gate_dir / "functional-inertness.json"), kind="file"
    )
    functional = load_json(functional_path, "functional inertness")
    if functional.get("verdict") != "PASS":
        refuse("functional inertness is not PASS")
    omp_num_threads = functional.get("omp_num_threads")
    if isinstance(omp_num_threads, bool) \
            or not isinstance(omp_num_threads, int) or omp_num_threads < 1:
        refuse("functional inertness has invalid omp_num_threads")
    omp = {
        "num_threads": omp_num_threads,
        "dynamic": "FALSE",
        "proc_bind": "close",
        "wait_policy": "active",
        "coli_omp_tuned": "1",
    }

    if identity_fixture_s:
        fixture_path = strict_path(identity_fixture_s, kind="file")
        fixture = load_json(fixture_path, "identity fixture")
        boot_path = strict_path(fixture.get("boot_id_path"), kind="file")
        f1k_ops._BOOT_ID_PATH = boot_path
        metadata = fixture.get("metadata")
        compute = fixture.get("compute")
        if not isinstance(metadata, dict) or not isinstance(compute, dict):
            refuse("identity fixture is malformed")

        def metadata_transport(path, timeout):
            del timeout
            return metadata[path]

        def compute_transport(**kwargs):
            del kwargs
            return dict(compute)

        identity = f1k_ops.resolve_live_instance_identity(
            metadata_transport=metadata_transport,
            compute_transport=compute_transport,
        )
    else:
        identity = f1k_ops.resolve_live_instance_identity()

    pin_sha = shas["pin"]
    tokens_sha = shas["tokens"]
    tok_sha = shas["tok_artifact"]
    weights_sha = shas["weights"]
    engine_sha = shas["engine"]
    tok_argv = [
        os.fspath(file_paths["python"]),
        os.fspath(file_paths["tok_wrapper"]),
        os.fspath(file_paths["tok_artifact"]),
    ]
    engine_argv = [
        os.fspath(file_paths["engine"]),
        "64",
        "4",
        "8",
    ]

    weights = load_json(file_paths["weights"], "weights evidence")
    strict_sha(
        weights.get("glm52_weights_manifest_sha256"),
        "weights content manifest",
    )
    if isinstance(weights.get("n_files"), bool) \
            or not isinstance(weights.get("n_files"), int) \
            or weights["n_files"] < 1:
        refuse("weights evidence has invalid n_files")

    sample = load_json(file_paths["sample"], "timing sample")
    t1_ids = sample.get("t1_sample_ids")
    entries = sample.get("entries")
    if not isinstance(t1_ids, list) or not t1_ids \
            or len(set(t1_ids)) != len(t1_ids) \
            or not all(isinstance(sid, str) and sid for sid in t1_ids):
        refuse("timing sample has invalid T1 IDs")
    if not isinstance(entries, list) or not entries:
        refuse("timing sample has no T2 entries")
    t2_ids = [
        entry.get("sample_id")
        for entry in entries
        if isinstance(entry, dict)
    ]
    if len(t2_ids) != len(entries) or len(set(t2_ids)) != len(t2_ids) \
            or not all(isinstance(sid, str) and sid for sid in t2_ids):
        refuse("timing sample has invalid T2 IDs")

    t1_records = read_results(
        gate_dir / "t1-results", "t1", t1_ids, identity["boot_id"]
    )
    t2_records = read_results(
        gate_dir / "t2-results", "t2", t2_ids, identity["boot_id"]
    )

    gate_inputs = load_json(file_paths["gate_inputs"], "gate inputs")
    if gate_inputs.get("schema") != \
            "kot-f1k-bringup-gate/2:gate-inputs":
        refuse("gate inputs schema mismatch; runner must re-run collect")
    token_counts = gate_inputs.get("token_counts") or {}
    if token_counts.get("schema") != \
            "kot-f1k-bringup-gate/2:token-counts":
        refuse("gate token-counts schema mismatch")
    if token_counts.get("tokenizer") != {
        "mode": "REAL",
        "mock_f": None,
        "sha256": tok_sha,
    }:
        refuse("gate tokenizer binding mismatch")
    corpus_shas = token_counts.get("corpus_sha256")
    if not isinstance(corpus_shas, dict) or set(corpus_shas) != {
        "construction-manifest.jsonl",
        "test.jsonl",
        "dev.jsonl",
        "guard.jsonl",
    }:
        refuse("gate corpus binding is incomplete")
    for name, value in corpus_shas.items():
        strict_sha(value, "timing corpus %s" % name)
        if bundle.get("gate-corpus/%s" % name) != value:
            refuse("gate corpus bytes do not match bundle: %s" % name)
    if corpus_shas["construction-manifest.jsonl"] != SOURCE_PIN:
        refuse("gate construction corpus drift")
    expected_timing_sample = {
        key: sample[key]
        for key in (
            "seed",
            "rule",
            "realized_bin_edges_Tp",
            "n",
            "t1_sample_ids",
            "entries",
        )
    }
    if gate_inputs.get("timing_sample") != expected_timing_sample:
        refuse("gate inputs timing sample is stale")

    dump_gate = gate_inputs.get("dump_gate") or {}
    if any(
        dump_gate.get(key) != "PASS"
        for key in ("a", "b", "c", "functional_inertness")
    ):
        refuse("re-collected gate inputs do not carry all PASS dump gates")
    gate_tokens_sha = strict_sha(
        gate_inputs.get("tokens_full_sha256"),
        "gate inputs tokens_full_sha256",
    )
    if gate_tokens_sha != tokens_sha:
        refuse("token sidecar SHA does not equal collected gate inputs")
    # collect owns this top-level SHA.  construction-continue/guard will later
    # cross-check it against the GREEN artifact's
    # model_bundle.tokens_full_sha256.
    gate_pin = gate_inputs.get("pin") or {}
    if gate_pin.get("pin_file_path") != os.fspath(file_paths["pin"]) \
            or gate_pin.get("pin_file_sha256") != pin_sha \
            or gate_pin.get("regime") != "pinned-bringup":
        refuse("gate pin binding mismatch")
    pin_gb = finite_positive(gate_pin.get("pin_gb"), "pin.pin_gb")
    if gate_inputs.get("t1_unpinned_runs") != t1_records \
            or gate_inputs.get("t2_pinned_runs") != t2_records:
        refuse("gate inputs are stale relative to the complete timing set")
    completed_result_set = {
        "t1_unpinned_runs": t1_records,
        "t2_pinned_runs": t2_records,
    }
    result_set_sha = hashlib.sha256(
        f1k_ops.canonical_json_bytes(completed_result_set)
    ).hexdigest()

    layers = list(range(3, 78))
    layers_csv = ",".join(str(layer) for layer in layers)
    builder_argv = [
        "python3",
        os.fspath(file_paths["builder"]),
        "construct",
        "--mode",
        "real",
        "--layers",
        layers_csv,
        "--tokenizer-sha",
        tok_sha,
        "--tokenizer-artifact",
        os.fspath(file_paths["tok_artifact"]),
        "--engine-weights-sha",
        weights_sha,
        "--engine-weights-artifact",
        os.fspath(file_paths["weights"]),
        "--dump-patch-sha",
        shas["dump_patch"],
        "--dump-patch-artifact",
        os.fspath(file_paths["dump_patch"]),
        "--out",
        os.fspath(out),
        "--workdir",
        os.fspath(workdir),
    ]
    forbidden = ("--engine-c", "--tokenizer-c")
    if any(token.startswith(forbidden) for token in builder_argv):
        refuse("builder argv contains guard-owned engine/tokenizer flags")

    environment = {
        "SNAP": os.fspath(estate),
        "TOK_SHA256": tok_sha,
        "OMP_NUM_THREADS": str(omp["num_threads"]),
        "OMP_DYNAMIC": str(omp["dynamic"]),
        "OMP_PROC_BIND": str(omp["proc_bind"]),
        "OMP_WAIT_POLICY": str(omp["wait_policy"]),
        "COLI_OMP_TUNED": str(omp["coli_omp_tuned"]),
    }
    tests = [
        ("kae", kae_log),
        ("dump-a", status_paths["dump-a"]),
        ("dump-b", dump_log),
        ("dump-c", status_paths["dump-c"]),
        ("functional-inertness", functional_path),
        ("tokenizer-engine-agreement", status_paths["dump-a"]),
    ]
    if now_s:
        created = now_s
    else:
        created = datetime.datetime.now(
            datetime.timezone.utc
        ).isoformat(timespec="seconds").replace("+00:00", "Z")
    if RFC3339_RE.fullmatch(created) is None:
        refuse("created_at_utc is not canonical UTC RFC3339")

    record = {
        "schema": "kot-f1k-construction-ready/1",
        "status": "READY",
        "created_at_utc": created,
        "instance": identity,
        "timing_results": {
            "boot_id": identity["boot_id"],
            "result_set_sha256": result_set_sha,
            "pin_sha256": pin_sha,
            "t1_sample_ids": t1_ids,
            "t2_sample_ids": t2_ids,
        },
        "payload": {
            "root": os.fspath(payload),
            "source_manifest": {
                "path": os.fspath(file_paths["source"]),
                "sha256": shas["source"],
            },
            "bundle_manifest": {
                "path": os.fspath(file_paths["bundle"]),
                "sha256": shas["bundle"],
                "file_count": len(bundle),
            },
        },
        "builder": {
            "path": os.fspath(file_paths["builder"]),
            "sha256": shas["builder"],
            "argv_base": builder_argv,
        },
        "engine": {
            "argv": engine_argv,
            "executable_path": os.fspath(file_paths["engine"]),
            "sha256": engine_sha,
            "weights_artifact_path": os.fspath(file_paths["weights"]),
            "weights_artifact_sha256": weights_sha,
        },
        "tokenizer": {
            "argv": tok_argv,
            "artifact_path": os.fspath(file_paths["tok_artifact"]),
            "sha256": tok_sha,
        },
        "dump_patch": {
            "artifact_path": os.fspath(file_paths["dump_patch"]),
            "sha256": shas["dump_patch"],
        },
        "token_sidecar": {
            "path": os.fspath(file_paths["tokens"]),
            "sha256": tokens_sha,
        },
        "pin": {
            "path": os.fspath(file_paths["pin"]),
            "sha256": pin_sha,
            "pin_gb": pin_gb,
        },
        "launch": {
            "layers": layers,
            "environment": environment,
        },
        "paths": {
            "rundir": os.fspath(rundir),
            "workdir": os.fspath(workdir),
            "out": os.fspath(out),
        },
        "engine_tests": [
            {
                "name": name,
                "path": os.fspath(path),
                "sha256": sha256_file(path),
                "verdict": "PASS",
            }
            for name, path in tests
        ],
    }
    serialized = json.dumps(record, sort_keys=True)
    if any(
        marker in serialized
        for marker in (
            "KOT_F1K_",
            "${",
            "<rundir>",
            "<workdir>",
            "<out>",
        )
    ):
        refuse("ready manifest contains an undefined placeholder")
    ready_sha = f1k_ops.atomic_write_json(ready, record, mode=0o600)
    print(
        "construction-ready written: %s sha256=%s"
        % (ready, ready_sha)
    )


try:
    main()
except (
    OSError,
    KeyError,
    TypeError,
    ValueError,
    ReadyRefusal,
    f1k_ops.F1KOpsError,
) as exc:
    print("ERR_F1K_READY: %s" % exc, file=sys.stderr)
    raise SystemExit(1)
PY
}

worker_selftest() {
  local td checks=0 fails=0 rc final before after held duplicate fixture ready_file
  td=$(mktemp -d) || return 1
  GATE="$td/gate"
  mkdir -p "$GATE/t2-results"
  echo "== selftest: f1k_worker atomic timing artifacts (mock files only) =="

  worker_check() {
    checks=$((checks + 1))
    if "$@"; then
      echo "  ok:  $WORKER_CHECK_MSG"
    else
      echo "  FAIL: $WORKER_CHECK_MSG"
      fails=$((fails + 1))
    fi
  }
  mock_result_tmp() {
    local path="$1" sid="$2"
    python3 - "$HERE" "$path" "$sid" <<'PY'
import os, sys
sys.path.insert(0, sys.argv[1])
import f1k_ops
record = {"phase": "t2", "sample_id": sys.argv[3], "s": 1.25,
          "timer_n": 1, "pin_evidence": "[PIN] mock",
          "boot_id": "11111111-1111-4111-8111-111111111111"}
payload = f1k_ops.canonical_json_bytes(record)
with open(sys.argv[2], "wb") as handle:
    handle.write(payload)
    handle.flush()
    os.fsync(handle.fileno())
PY
  }

  final="$GATE/t2-results/t2-s000.json"
  local staged="$GATE/t2-results/.t2-s000.interrupted.tmp"
  mock_result_tmp "$staged" s000
  rc=0
  KOT_F1K_TEST_INTERRUPT_BEFORE_RENAME=1 \
    write_timing_result t2 s000 "$staged" >/dev/null 2>&1 || rc=$?
  WORKER_CHECK_MSG="injected interruption leaves no final and a complete temp"
  worker_check test "$rc" -eq 99 -a ! -e "$final" -a -s "$staged"

  write_timing_result t2 s000 "$staged" >/dev/null
  WORKER_CHECK_MSG="successful publish exposes one complete canonical record"
  worker_check python3 - "$HERE" "$final" <<'PY'
import json, sys
sys.path.insert(0, sys.argv[1])
import f1k_ops
raw = open(sys.argv[2], "rb").read()
raise SystemExit(0 if raw == f1k_ops.canonical_json_bytes(json.loads(raw)) else 1)
PY

  staged="$GATE/t2-results/.t2-s001.complete.tmp"
  mock_result_tmp "$staged" s001
  write_timing_result t2 s001 "$staged" >/dev/null
  WORKER_CHECK_MSG="complete expected set is consumable"
  worker_check validate_timing_results t2 "$GATE/t2-results" s000 s001

  held="$GATE/t2-results/.t2-s001.held.tmp"
  mv -f "$GATE/t2-results/t2-s001.json" "$held"
  WORKER_CHECK_MSG="partial set is not consumable"
  if validate_timing_results t2 "$GATE/t2-results" s000 s001 >/dev/null 2>&1; then
    worker_check false
  else
    worker_check true
  fi
  mv -f "$held" "$GATE/t2-results/t2-s001.json"

  duplicate="$GATE/t2-results/t2-duplicate.json"
  cp -f "$final" "$duplicate"
  WORKER_CHECK_MSG="duplicate sample_id is not consumable"
  if validate_timing_results t2 "$GATE/t2-results" s000 s001 >/dev/null 2>&1; then
    worker_check false
  else
    worker_check true
  fi
  rm -f "$duplicate"

  before=$(sha256sum "$final" | awk '{print $1}')
  staged="$GATE/t2-results/.t2-s000.repeat.tmp"
  mock_result_tmp "$staged" s000
  write_timing_result t2 s000 "$staged" >/dev/null
  after=$(sha256sum "$final" | awk '{print $1}')
  WORKER_CHECK_MSG="complete-set republish is byte-deterministic"
  worker_check test "$before" = "$after"

  echo
  echo "== selftest: construction-ready manifest (mock files only) =="
  fixture="$td/ready-fixture"
  ready_file="$fixture/home/f1k-gate/construction-ready.json"
  export KOT_F1K_READY_FIXTURE_ROOT="$fixture"
  export KOT_F1K_READY_TEST_NOW="2026-07-18T12:00:00Z"

  ready_fixture_reset() {
    rm -rf "$fixture"
    python3 - "$HERE" "$fixture" <<'PY'
import hashlib
import os
import shutil
import sys
from pathlib import Path

here, fixture_s = sys.argv[1:]
sys.path.insert(0, here)
import f1k_ops

fixture = Path(fixture_s)
repo = Path(here).parents[1]
home = fixture / "home"
payload = home / "f1k"
gate = home / "f1k-gate"
scratch = fixture / "mnt/nvme/kot-f1k/construction"
build = home
estate = fixture / "mnt/nvme/glm52_i4"
for directory in (
    payload,
    gate / "gate-tokens",
    gate / "gate-sample",
    gate / "t1-results",
    gate / "t2-results",
    gate / "guard",
    scratch / "work",
    scratch / "out",
    build / "colibri-construct/c",
    estate,
):
    directory.mkdir(parents=True, exist_ok=True)


def copy(rel, source):
    dest = payload / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, dest)
    return dest


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    f1k_ops.atomic_write_json(path, value, mode=0o600)


builder = copy(
    "poc/glm52-probe/f1k-harness/build_carriers.py",
    repo / "poc/glm52-probe/f1k-harness/build_carriers.py",
)
wrapper = copy(
    "tok_glm52.py",
    repo / "poc/glm52-probe/f1k-harness/tok_glm52.py",
)
dump_patch = copy(
    "dump-patch/kot-f1k-dump.patch",
    repo
    / "poc/glm52-probe/f1k-harness/dump-patch/kot-f1k-dump.patch",
)
source = copy(
    "data/f1k-carriers-v1/generator/construction-manifest.jsonl",
    repo / "data/f1k-carriers-v1/generator/construction-manifest.jsonl",
)
corpus_dir = payload / "gate-corpus"
corpus_dir.mkdir()
shutil.copy2(source, corpus_dir / "construction-manifest.jsonl")
corpus = {
    "construction-manifest.jsonl":
        sha(corpus_dir / "construction-manifest.jsonl")
}
for name in ("test.jsonl", "dev.jsonl", "guard.jsonl"):
    path = corpus_dir / name
    path.write_text('{"fixture":true}\n', encoding="utf-8")
    corpus[name] = sha(path)
bundle = {
    path.relative_to(payload).as_posix(): sha(path)
    for path in sorted(payload.rglob("*"))
    if path.is_file()
}
write_json(payload / "bundle-manifest.json", bundle)

engine = build / "colibri-construct/c/glm"
engine.write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
engine.chmod(0o700)
tokenizer = estate / "tokenizer.json"
tokenizer.write_text('{"fixture":"tokenizer"}\n', encoding="utf-8")
weights = gate / "glm52-weights-hash.json"
write_json(
    weights,
    {
        "glm52_weights_manifest_sha256": "9" * 64,
        "n_files": 1,
        "total_gb": 1,
    },
)
tokens = gate / "gate-tokens/tokens-full.jsonl"
tokens.write_text(
    '{"key":"fixture","ids":[1]}\n',
    encoding="utf-8",
)
pin = gate / "pin_bringup.stats"
pin.write_text("0 0\n", encoding="ascii")
for name in (
    "tiny-dump.status",
    "dump-b.status",
    "moe-sum-crosscheck.status",
):
    (gate / name).write_text("PASS\n", encoding="ascii")
(gate / "kae-bringup.log").write_text(
    "BRING-UP OK (KaE)\n",
    encoding="ascii",
)
(gate / "dump-realchecks.log").write_text(
    "test_kae: 44/44\n"
    "test_kae_dump: 43/43\n"
    "CHECKS OK\n",
    encoding="ascii",
)
write_json(
    gate / "functional-inertness.json",
    {"verdict": "PASS", "omp_num_threads": 8},
)

boot_id = "11111111-1111-4111-8111-111111111111"
boot_path = fixture / "boot_id"
boot_path.write_text(boot_id + "\n", encoding="ascii")
metadata = {
    "instance/id": "1234567890123456789",
    "instance/name": "kot-f1k-run",
    "project/project-id": "test-project",
    "project/numeric-project-id": "987654321",
    "instance/zone": "projects/987654321/zones/us-central1-a",
    "instance/machine-type":
        "projects/987654321/machineTypes/n2d-highmem-8",
}
compute = {
    "id": metadata["instance/id"],
    "name": metadata["instance/name"],
    "zone":
        "https://www.googleapis.com/compute/v1/"
        "projects/test-project/zones/us-central1-a",
    "machineType":
        "https://www.googleapis.com/compute/v1/"
        "projects/test-project/zones/us-central1-a/"
        "machineTypes/n2d-highmem-8",
    "selfLink":
        "https://www.googleapis.com/compute/v1/"
        "projects/test-project/zones/us-central1-a/"
        "instances/kot-f1k-run",
    "scheduling": {"provisioningModel": "SPOT"},
    "lastStartTimestamp": "2026-07-17T17:00:00.123456-07:00",
}
write_json(
    fixture / "identity.json",
    {
        "boot_id_path": str(boot_path),
        "metadata": metadata,
        "compute": compute,
    },
)
identity = {
    "instance_id": metadata["instance/id"],
    "name": metadata["instance/name"],
    "project_id": metadata["project/project-id"],
    "project_number": metadata["project/numeric-project-id"],
    "zone": "us-central1-a",
    "machine_type": "n2d-highmem-8",
    "provisioning_model": "SPOT",
    "last_start_timestamp": "2026-07-18T00:00:00.123456Z",
    "boot_id": boot_id,
}
sample = {
    "schema": "kot-f1k-bringup-gate/2:timing-sample",
    "seed": 20260718,
    "rule": {"fixture": True},
    "realized_bin_edges_Tp": [1, 1],
    "n": 1,
    "t1_sample_ids": ["s000"],
    "entries": [{"sample_id": "s000"}],
}
write_json(gate / "gate-sample/timing-sample.json", sample)
def result(phase):
    return {
        "phase": phase,
        "sample_id": "s000",
        "s": 1.25,
        "timer_n": 1,
        "pin_evidence": "[PIN] mock",
        "boot_id": boot_id,
    }


t1 = result("t1")
t2 = result("t2")
write_json(gate / "t1-results/t1-s000.json", t1)
write_json(gate / "t2-results/t2-s000.json", t2)
gate_inputs = {
    "schema": "kot-f1k-bringup-gate/2:gate-inputs",
    "token_counts": {
        "schema": "kot-f1k-bringup-gate/2:token-counts",
        "tokenizer": {
            "mode": "REAL",
            "mock_f": None,
            "sha256": sha(tokenizer),
        },
        "corpus_sha256": corpus,
    },
    "tokens_full_sha256": sha(tokens),
    "timing_sample": {
        key: sample[key]
        for key in (
            "seed",
            "rule",
            "realized_bin_edges_Tp",
            "n",
            "t1_sample_ids",
            "entries",
        )
    },
    "t1_unpinned_runs": [t1],
    "t2_pinned_runs": [t2],
    "pin": {
        "pin_file_path": str(pin),
        "pin_file_sha256": sha(pin),
        "pin_gb": 40,
        "regime": "pinned-bringup",
    },
    "dump_gate": {
        "a": "PASS",
        "b": "PASS",
        "c": "PASS",
        "functional_inertness": "PASS",
    },
}
write_json(gate / "gate-inputs.json", gate_inputs)
PY
  }

  expect_ready_refusal() {
    if emit_construction_ready >/dev/null 2>&1; then
      return 1
    fi
    [ ! -e "$ready_file" ] && [ ! -L "$ready_file" ]
  }

  ready_happy() {
    emit_construction_ready >/dev/null 2>&1 || return 1
    local sha1 sha2
    sha1=$(sha256sum "$ready_file" | awk '{print $1}') || return 1
    python3 - "$HERE" "$ready_file" "$fixture" <<'PY'
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, sys.argv[1])
import f1k_ops

raw = open(sys.argv[2], "rb").read()
record = json.loads(raw)
fixture = Path(sys.argv[3])
gate_inputs = json.loads(
    (fixture / "home/f1k-gate/gate-inputs.json").read_text()
)
completed = {
    "t1_unpinned_runs": gate_inputs["t1_unpinned_runs"],
    "t2_pinned_runs": gate_inputs["t2_pinned_runs"],
}
expected_result_sha = hashlib.sha256(
    f1k_ops.canonical_json_bytes(completed)
).hexdigest()
ok = (
    raw == f1k_ops.canonical_json_bytes(record)
    and record["schema"] == "kot-f1k-construction-ready/1"
    and record["status"] == "READY"
    and record["payload"]["root"] == str(fixture / "home/f1k")
    and record["builder"]["path"] == str(
        fixture / "home/f1k/poc/glm52-probe/f1k-harness/build_carriers.py"
    )
    and record["builder"]["sha256"]
        == "a92be3e4fe535c1dfefc41e2a422e010d25e8e40cf8e4cc123e7d829d63e9e61"
    and record["builder"]["argv_base"][:3]
        == ["python3", record["builder"]["path"], "construct"]
    and not any(
        value.startswith(("--engine-c", "--tokenizer-c"))
        for value in record["builder"]["argv_base"]
    )
    and record["dump_patch"]["artifact_path"] == str(
        fixture / "home/f1k/dump-patch/kot-f1k-dump.patch"
    )
    and record["token_sidecar"]["sha256"]
        == gate_inputs["tokens_full_sha256"]
    and record["timing_results"]["boot_id"]
        == record["instance"]["boot_id"]
    and record["timing_results"]["result_set_sha256"]
        == expected_result_sha
    and record["timing_results"]["pin_sha256"] == record["pin"]["sha256"]
    and record["paths"] == {
        "rundir": str(fixture / "home/f1k-gate/guard"),
        "workdir": str(fixture / "mnt/nvme/kot-f1k/construction/work"),
        "out": str(fixture / "mnt/nvme/kot-f1k/construction/out"),
    }
    and record["launch"]["layers"] == list(range(3, 78))
    and "epoch_id" not in raw.decode()
    and "KOT_F1K_" not in raw.decode()
    and "${" not in raw.decode()
)
raise SystemExit(0 if ok else 1)
PY
    emit_construction_ready >/dev/null 2>&1 || return 1
    sha2=$(sha256sum "$ready_file" | awk '{print $1}') || return 1
    [ "$sha1" = "$sha2" ]
  }

  ready_fixture_reset
  WORKER_CHECK_MSG="actual-layout PASS fixture emits deterministic READY with python3 argv, boot/result/pin timing binding, required token SHA, and no epoch"
  worker_check ready_happy

  ready_fixture_reset
  echo "FAIL" > "$fixture/home/f1k-gate/tiny-dump.status"
  WORKER_CHECK_MSG="non-PASS dump status leaves no READY file"
  worker_check expect_ready_refusal

  ready_fixture_reset
  python3 - "$HERE" "$fixture/home/f1k-gate/gate-inputs.json" <<'PY'
import json
import sys

sys.path.insert(0, sys.argv[1])
import f1k_ops

path = sys.argv[2]
record = json.load(open(path))
record["tokens_full_sha256"] = "0" * 64
f1k_ops.atomic_write_json(path, record)
PY
  WORKER_CHECK_MSG="required SHA mismatch leaves no READY file"
  worker_check expect_ready_refusal

  ready_fixture_reset
  rm -f "$fixture/home/f1k-gate/t2-results/t2-s000.json"
  WORKER_CHECK_MSG="missing completed timing result leaves no READY file"
  worker_check expect_ready_refusal

  ready_fixture_reset
  rm -f "$fixture/home/f1k-gate/pin_bringup.stats"
  WORKER_CHECK_MSG="missing campaign pin leaves no READY file"
  worker_check expect_ready_refusal

  ready_fixture_reset
  python3 - "$HERE" "$fixture/home/f1k-gate/gate-inputs.json" <<'PY'
import json
import sys

sys.path.insert(0, sys.argv[1])
import f1k_ops

path = sys.argv[2]
record = json.load(open(path))
record["pin"]["pin_file_path"] = "relative/pin_bringup.stats"
f1k_ops.atomic_write_json(path, record)
PY
  WORKER_CHECK_MSG="relative required path leaves no READY file"
  worker_check expect_ready_refusal

  ready_fixture_reset
  mv -f \
    "$fixture/mnt/nvme/glm52_i4/tokenizer.json" \
    "$fixture/mnt/nvme/glm52_i4/tokenizer.real.json"
  ln -s "tokenizer.real.json" "$fixture/mnt/nvme/glm52_i4/tokenizer.json"
  WORKER_CHECK_MSG="symlinked required path leaves no READY file"
  worker_check expect_ready_refusal

  ready_fixture_reset
  echo "# drift" >> \
    "$fixture/home/f1k/poc/glm52-probe/f1k-harness/build_carriers.py"
  WORKER_CHECK_MSG="mutated build_carriers.py leaves no READY file"
  worker_check expect_ready_refusal

  rm -rf "$td"
  echo
  echo "WORKER SELFTEST: $((checks - fails))/$checks $([ "$fails" -eq 0 ] && echo PASS || echo FAILED)"
  [ "$fails" -eq 0 ]
}

case "${1:-}" in
  --selftest)
    shift
    [ "$#" -eq 0 ] || {
      echo "usage: $0 [--selftest|--finalize-ready]" >&2
      exit 2
    }
    worker_selftest
    exit $?
    ;;
  --finalize-ready)
    shift
    [ "$#" -eq 0 ] || {
      echo "usage: $0 [--selftest|--finalize-ready]" >&2
      exit 2
    }
    emit_construction_ready
    exit $?
    ;;
  "") ;;
  *)
    echo "usage: $0 [--selftest|--finalize-ready]" >&2
    exit 2
    ;;
esac

BUCKET="${KOT_F1K_BUCKET:?set KOT_F1K_BUCKET=gs://... (same-region estate mirror + heartbeat)}"
COLIBRI_GIT_URL="${COLIBRI_GIT_URL:?coordinator-supplied colibri clone URL}"
SPOT_RATE="${KOT_F1K_SPOT_RATE:?record the ACTUAL assigned spot $/h (load-bearing for the affordability gate)}"
ESTATE_REPO="mateogrgic/GLM-5.2-colibri-int4-with-int8-mtp"
HOME_DIR="${HOME:-/home/ubuntu}"
SSD="/mnt/nvme"                 # the striped local NVMe mount (see f1k_gcp provision docs)
ESTATE_DIR="$SSD/glm52_i4"
GATE="$HOME_DIR/f1k-gate"       # bring-up outputs

mkdir -p "$GATE"
die() { echo "ERR_F1K_WORKER: $*" >&2; hb "FAILED: $*"; exit 1; }
step() { echo; echo "########## $* ##########"; }
hb() { # heartbeat to GCS
  echo "{\"ts\":\"$(date -u +%FT%TZ)\",\"stage\":\"$1\"}" > "$GATE/heartbeat.json"
  gsutil -q cp "$GATE/heartbeat.json" "$BUCKET/f1k/bringup/heartbeat.json" 2>/dev/null || true
}

# --- DIAGNOSTIC PRESERVATION (runner-7) ------------------------------------
# Under `set -euo pipefail`, a build failure inside step 2+3 (the tee'd
# bringup_gcp.sh pipe) trips pipefail and exits BEFORE the `|| die` and BEFORE
# the DONE-step mirror (line ~167) ever run — so on the failing path the on-VM
# build logs ($GATE/kae-bringup.log, dump-realchecks.log, etc.) were NEVER
# mirrored to GCS, and the watchdog then deleted the VM, LOSING the diagnostic.
# This EXIT trap fires on EVERY exit path (normal, `set -e`/pipefail, signal,
# die()) and best-effort mirrors the WHOLE $GATE dir to $BUCKET/f1k/bringup/ so
# any failure is diagnosable off-box. Best-effort only: it never changes the
# exit code (re-exits with the original rc) and never hangs teardown.
_mirror_gate_on_exit() {
  local rc=$?
  trap - EXIT   # disarm so this runs at most once
  if [ -d "$GATE" ]; then
    echo "{\"ts\":\"$(date -u +%FT%TZ)\",\"stage\":\"EXIT rc=$rc (gate mirrored)\",\"rc\":$rc}" \
      > "$GATE/exit-status.json" 2>/dev/null || true
    gsutil -q -m cp -r "$GATE" "$BUCKET/f1k/bringup/" 2>/dev/null || true
    gsutil -q cp "$GATE/exit-status.json" "$BUCKET/f1k/bringup/exit-status.json" 2>/dev/null || true
  fi
  exit "$rc"
}
trap _mirror_gate_on_exit EXIT
# ---------------------------------------------------------------------------

step "0/5 preflight: non-AWS + tools + NVMe"
# non-AWS gate (this box must be the GCP VM, never AWS)
if curl -s --max-time 1 http://169.254.169.254/latest/meta-data/instance-id >/dev/null 2>&1 \
   && ! curl -s --max-time 1 -H 'Metadata-Flavor: Google' \
        http://metadata.google.internal/computeMetadata/v1/instance/zone >/dev/null 2>&1; then
  die "worker looks like AWS — refuse (frozen target is the GCP Spot VM)"
fi
for t in git gcc make objdump python3 sha256sum curl; do
  command -v "$t" >/dev/null 2>&1 || { sudo apt-get update -qq && sudo apt-get install -y -qq git build-essential binutils python3 curl; break; }
done
# [REV-B F4] fresh-worker dependency VERIFICATION (gate-fix review #5): the
# GCS mirror/heartbeat path is load-bearing throughout (staging, resume,
# diagnostics), so gsutil is REQUIRED — bringup-deploy's remote prep
# installs google-cloud-cli when the image lacks it; refuse to run blind.
# pip3 likewise (tokenizers + HF staging below).
command -v gsutil >/dev/null 2>&1 \
  || sudo apt-get install -y -qq google-cloud-cli 2>/dev/null || true
command -v gsutil >/dev/null 2>&1 \
  || die "gsutil MISSING and google-cloud-cli install failed — every GCS seam (estate mirror, heartbeat, campaign-pin persistence) is dead; fix the image/deploy (bringup-deploy remote prep)"
command -v pip3 >/dev/null 2>&1 \
  || sudo apt-get install -y -qq python3-pip 2>/dev/null || true
command -v pip3 >/dev/null 2>&1 || die "pip3 MISSING (python3-pip)"
# [REV-B F4] MOUNTPOINT guard, not directory existence (review #5): after a
# reboot /mnt/nvme exists as a bare dir on the BOOT DISK — staging ~384 GB
# there would silently fill it. Require a real mount.
mountpoint -q "$SSD" \
  || die "local NVMe $SSD is NOT a mountpoint (bare dir = boot disk!) — bringup-deploy must RAID0 (/dev/md0) + mount the local SSDs first"
hb "preflight-ok"

step "1/5 stage estate (GCS mirror -> else HF -> local NVMe, then mirror to GCS)"
mkdir -p "$ESTATE_DIR"
if gsutil -q ls "$BUCKET/f1k/estate/COMPLETE" 2>/dev/null; then
  echo "estate mirror present in GCS — restoring to $ESTATE_DIR"
  gsutil -q -m rsync -r "$BUCKET/f1k/estate" "$ESTATE_DIR"
else
  echo "no GCS mirror — HF snapshot_download $ESTATE_REPO"
  pip3 -q install "huggingface_hub[hf_transfer]>=0.24" hf_transfer 2>/dev/null || true
  HF_HUB_ENABLE_HF_TRANSFER=1 python3 - <<PY
from huggingface_hub import snapshot_download
snapshot_download(repo_id="$ESTATE_REPO", local_dir="$ESTATE_DIR",
                  local_dir_use_symlinks=False, max_workers=8)
print("staged")
PY
  # mirror to GCS so a preempted VM restores instead of re-downloading
  gsutil -q -m rsync -r "$ESTATE_DIR" "$BUCKET/f1k/estate"
  echo "ok" | gsutil -q cp - "$BUCKET/f1k/estate/COMPLETE"
fi
# weight content hash (ASM-1971 PINNED-AT-INPUTS): sorted rel-path + size digest
python3 - "$ESTATE_DIR" > "$GATE/glm52-weights-hash.json" <<'PY'
import sys, hashlib, os
root = sys.argv[1]; lines = []; total = 0
for dp, _, fs in os.walk(root):
    for fn in fs:
        p = os.path.join(dp, fn); sz = os.path.getsize(p); total += sz
        lines.append("%s %d" % (os.path.relpath(p, root), sz))
lines.sort()
import json
print(json.dumps({"glm52_weights_manifest_sha256":
                  hashlib.sha256("\n".join(lines).encode()).hexdigest(),
                  "n_files": len(lines), "total_gb": round(total/1e9, 2)}))
PY
cat "$GATE/glm52-weights-hash.json"
gsutil -q cp "$GATE/glm52-weights-hash.json" "$BUCKET/f1k/bringup/" || true
hb "staged"

step "2+3/5 build SCORING engine (KaE-only) + PRISTINE engine + KaE bring-up gate"
KAE_PATCH_DIR="$HERE/kae-patch-draft" COLIBRI_WORK="$HOME_DIR/colibri-score" GATE="$GATE" \
  COLIBRI_GIT_URL="$COLIBRI_GIT_URL" bash "$HERE/bringup_gcp.sh" 2>&1 | tee "$GATE/kae-bringup.log"
grep -q "BRING-UP OK (KaE)" "$GATE/kae-bringup.log" || die "KaE bring-up gate FAILED"
[ -x "$HOME_DIR/colibri-score/c/glm" ]          || die "scoring engine glm not built by bringup_gcp.sh"
[ -x "$HOME_DIR/colibri-score/c/glm_pristine" ] || die "pristine engine glm_pristine not built by bringup_gcp.sh (functional-gate reference)"
hb "kae-bringup-ok"

step "4/5 build CONSTRUCTION engine (KaE + dump patch) + DUMP bring-up gate (b)"
# real-checks.sh applies KaE THEN the dump patch on a pristine tree, builds,
# test_kae 44/44 + test_kae_dump 43/43, objdump per-function inertness.
# OPS (bead kernel-of-truth-f2uk / ASM-2503 amendment / resolution memo §5):
# real-checks.sh's FINAL step (6/6 objdump per-function equivalence at
# -O2 -march=x86-64-v3) is gcc-VERSION-brittle — MEASURED for the KaE patch
# (runner-8, 20260717T015601Z): the VM's Ubuntu gcc spills neighbouring
# functions outside the allowed set EVEN AT the reference flags. On this box
# that ONE failure signature is demoted to ADVISORY (logged to
# $GATE/objdump-dump-advisory.log, bring-up continues): rc!=0 is tolerated
# ONLY IF steps 1-5 provably passed (patch shas + build + test_kae 44/44 +
# test_kae_dump 43/43 lines present) AND the only ERR is the step-6
# "functions differ OUTSIDE the allowed set" spill (NOT "functions REMOVED").
# real-checks.sh itself is UNTOUCHED (gate-0-reviewed); its step-6 proof
# stands fail-closed OFF-BOX on the gcc-11.5 measurement basis. ANY other
# failure stays fail-closed here.
# [REV-B F4, gate-fix review #5] real-checks.sh's ACTUAL contract, met
# explicitly (it was invoked dead-on-arrival before):
#   - COLIBRI_TREE (real-checks.sh:43) = a PRISTINE checkout whose c/glm.c
#     is at the pinned base blob (:47 verifies fail-closed) — the
#     bringup_gcp.sh tree is PATCHED, so clone a fresh one at the same
#     pinned commit (bringup_gcp.sh:24 a78a06fc);
#   - the KaE patch at dump-patch/../../kae-patch-draft (real-checks.sh:37)
#     — with the bundle at ~/f1k that resolves to ~/kae-patch-draft, so
#     provide it there (symlink) and verify before invoking.
COLIBRI_PRISTINE="$HOME_DIR/colibri-pristine"
if [ ! -d "$COLIBRI_PRISTINE/.git" ]; then
  git clone "$COLIBRI_GIT_URL" "$COLIBRI_PRISTINE"
fi
( cd "$COLIBRI_PRISTINE" \
  && { git fetch --all --quiet || true; } \
  && git checkout --quiet a78a06fc5acc4b0dc0f9ef03987c66b0559d1250 \
  && git diff --quiet ) \
  || die "pristine colibri checkout for COLIBRI_TREE failed (real-checks.sh:43 contract)"
ln -sfn "$HERE/kae-patch-draft" "$(dirname "$HERE")/kae-patch-draft"
[ -f "$(dirname "$HERE")/kae-patch-draft/kae-add-path.patch" ] \
  || die "kae-add-path.patch not reachable at real-checks.sh's expected ../../kae-patch-draft location"
set +e
( cd "$HERE/dump-patch" && COLIBRI_GIT_URL="$COLIBRI_GIT_URL" \
    COLIBRI_TREE="$COLIBRI_PRISTINE" \
    COLIBRI_WORK="$HOME_DIR/colibri-construct" bash real-checks.sh ) \
  > "$GATE/dump-realchecks.log" 2>&1
RC_B=$?
set -e
cat "$GATE/dump-realchecks.log"
if [ "$RC_B" -eq 0 ]; then
  grep -qiE "REAL-SOURCE CHECKS OK|CHECKS OK" "$GATE/dump-realchecks.log" \
    || die "dump bring-up precondition (b): rc=0 but no OK banner (real-checks.sh)"
elif grep -q "test_kae: 44/44" "$GATE/dump-realchecks.log" \
  && grep -q "test_kae_dump: 43/43" "$GATE/dump-realchecks.log" \
  && grep -q "functions differ OUTSIDE the allowed set" "$GATE/dump-realchecks.log" \
  && ! grep -q "functions REMOVED by the patch" "$GATE/dump-realchecks.log" \
  && [ "$(grep -c 'ERR_F1K_DUMP_CHECK' "$GATE/dump-realchecks.log")" -eq 1 ]; then
  grep -E "shared functions:|functions differ OUTSIDE" "$GATE/dump-realchecks.log" \
    > "$GATE/objdump-dump-advisory.log" || true
  echo "ADVISORY (bead f2uk): real-checks.sh steps 1-5 PASSED; step-6 objdump spill" \
       "on this box's gcc demoted per ASM-2503 (fail-closed proof stands off-box @ gcc 11.5)." \
    | tee -a "$GATE/objdump-dump-advisory.log"
else
  die "dump bring-up precondition (b) FAILED (real-checks.sh rc=$RC_B, not the demoted objdump-spill signature)"
fi
echo "PASS" > "$GATE/dump-b.status"    # (b) is fail-closed above; reaching here proves it
hb "dump-precond-b-ok"

step "4/5 DUMP bring-up gate (a): tiny real dump + token-id consistency"
# A few manifest lines at a small layer subset; kot-f1k-tok/1 ids must equal the
# ids the real engine prefills.  build_carriers manifest is (A)-time; a tiny
# construct DUMP is the smallest real exercise of the dump path.
: > "$GATE/tiny-dump.status"
python3 - <<PY 2>&1 | tee "$GATE/tiny-dump.log" || true
print("SCAFFOLD: the runner runs a tiny real KAE_DUMP over a few manifest")
print("lines (small KAE_DUMP_LAYERS) with KAE_SEED=20260716 and asserts the")
print("engine [KAE-DUMP] armed echo seed==20260716, then compares tok_glm52.py")
print("ids for the same texts to the ids the engine actually prefilled.")
print("This is finalized ON-BOX with the real construction binary + weights.")
PY
echo "RUNNER-CONFIRM-REQUIRED" > "$GATE/tiny-dump.status"
hb "dump-precond-a-scaffolded"

step "4/5 DUMP bring-up gate (c): independent MoE-input sum cross-check (RUNNER-CONFIRMED)"
echo "RUNNER-CONFIRM-REQUIRED" > "$GATE/moe-sum-crosscheck.status"
echo "SCAFFOLD: capture the engine's dumped moe()-input sum over >=1 MIXED" \
     "gated/ungated line, and an INDEPENDENT sum (separate path, not kae_dump.h);" \
     "assert cell-for-cell equality after the f32 cast. Correctness of the" \
     "independent path cannot be validated blind -> runner-confirmed PASS." \
     > "$GATE/moe-sum-crosscheck.log"
hb "dump-precond-c-scaffolded"

# =============================================================================
# FUNCTIONAL inert-by-default gate (KAE unset) — AUTHORITATIVE, FAIL-CLOSED.
# (bead kernel-of-truth-nf5n / docs/next/design/f1k-inertness-gate-resolution.md
#  §3.2). With KAE/KAE_SCORE/KAE_DUMP UNSET and OMP_NUM_THREADS pinned, the
#  KaE-patched PRODUCTION binary's teacher-forced scoring output MUST be
#  byte-identical to the pristine (pre-patch) engine's on real weights + identical
#  inputs, preceded by a same-binary determinism pre-check. This is the direct
#  measurement of the property the demoted objdump proxy only bounds; it is the
#  registered SS2.5/SS7.4 guard byte-identity instrument exercised at bring-up.
#  The shared path is run_score (SCORE=<manifest>, teacher-forced, present in BOTH
#  binaries); inertness is INPUT-INDEPENDENT, so a deterministic arbitrary-token
#  sample at short+long prefill shapes both PROVES inertness and (via the engine's
#  own scoring timer, load excluded) yields the affordability s/prefill sample.
#  Any mismatch -> ERR_F1K_BRINGUP_FUNC, die (EXIT trap preserves $GATE).
# =============================================================================
step "FUNCTIONAL inert-by-default gate (KAE unset) — AUTHORITATIVE"
SCORE_ENGINE="$HOME_DIR/colibri-score/c/glm"
PRISTINE_ENGINE="$HOME_DIR/colibri-score/c/glm_pristine"
[ -x "$SCORE_ENGINE" ]    || die "ERR_F1K_BRINGUP_FUNC: scoring engine missing: $SCORE_ENGINE"
[ -x "$PRISTINE_ENGINE" ] || die "ERR_F1K_BRINGUP_FUNC: pristine engine missing: $PRISTINE_ENGINE"
[ -d "$ESTATE_DIR" ]      || die "ERR_F1K_BRINGUP_FUNC: estate dir missing: $ESTATE_DIR"
FUNC_OMP="${KOT_F1K_OMP:-$(nproc)}"                       # pinned thread count (both binaries, all runs)
FUNC_N_SHORT="${KOT_F1K_FUNC_N_SHORT:-10}"; FUNC_T_SHORT="${KOT_F1K_FUNC_T_SHORT:-96}"
FUNC_N_LONG="${KOT_F1K_FUNC_N_LONG:-10}";  FUNC_T_LONG="${KOT_F1K_FUNC_T_LONG:-384}"
N_ITEMS=$((FUNC_N_SHORT + FUNC_N_LONG))
[ "$N_ITEMS" -ge 20 ] || die "ERR_F1K_BRINGUP_FUNC: functional sample $N_ITEMS < 20 required"
SAMPLE="$GATE/func-score-sample.txt"
python3 - "$SAMPLE" "$FUNC_N_SHORT" "$FUNC_T_SHORT" "$FUNC_N_LONG" "$FUNC_T_LONG" <<'PY'
import sys
out = sys.argv[1]; N_S, T_S, N_L, T_L = map(int, sys.argv[2:6])
# run_score manifest line: "ctxlen contlen id_0 ... id_{ctxlen+contlen-1}"
# deterministic ids in a safe in-vocab range [10,190); contlen=8 scored positions.
def ids(seed, T):
    xs = []; s = seed & 0xffffffff
    for _ in range(T):
        s = (1103515245 * s + 12345) & 0x7fffffff
        xs.append(10 + s % 180)
    return xs
lines = []
for i in range(N_S):
    ctx = T_S - 8; lines.append("%d %d %s" % (ctx, 8, " ".join(map(str, ids(1000 + i, T_S)))))
for i in range(N_L):
    ctx = T_L - 8; lines.append("%d %d %s" % (ctx, 8, " ".join(map(str, ids(9000 + i, T_L)))))
open(out, "w").write("\n".join(lines) + "\n")
print("functional sample: %d items (%d short T=%d + %d long T=%d) -> %s"
      % (N_S + N_L, N_S, T_S, N_L, T_L, out))
PY

# run the shared teacher-forced scorer with KAE FULLY UNSET, OMP pinned + tuned
# deterministically, and the engine's self-re-exec skipped (COLI_OMP_TUNED=1).
run_score_engine() {   # $1=binary  $2=stdout  $3=stderr
  env -u KAE -u KAE_G -u KAE_SCORE -u KAE_DUMP -u KAE_CARRIER -u KAE_SPANS \
      -u KAE_MODE -u KAE_SEED -u KAE_DUMP_LAYERS \
      SNAP="$ESTATE_DIR" SCORE="$SAMPLE" \
      OMP_NUM_THREADS="$FUNC_OMP" OMP_DYNAMIC=FALSE OMP_PROC_BIND=close \
      OMP_WAIT_POLICY=active COLI_OMP_TUNED=1 \
      "$1" 64 4 8 >"$2" 2>"$3"
}
RES='^-?[0-9]+\.[0-9]{6} [0-9]+ [01]$'    # run_score result line: "<logprob> <contlen> <greedy>"

echo "-- (i) determinism pre-check: patched binary, 2 runs, byte-identical --"
run_score_engine "$SCORE_ENGINE" "$GATE/func-patched-1.out" "$GATE/func-patched-1.err" \
  || die "ERR_F1K_BRINGUP_FUNC: patched scoring run #1 failed (see func-patched-1.err)"
run_score_engine "$SCORE_ENGINE" "$GATE/func-patched-2.out" "$GATE/func-patched-2.err" \
  || die "ERR_F1K_BRINGUP_FUNC: patched scoring run #2 failed (see func-patched-2.err)"
grep -E "$RES" "$GATE/func-patched-1.out" > "$GATE/func-patched-1.res" || true
grep -E "$RES" "$GATE/func-patched-2.out" > "$GATE/func-patched-2.res" || true
NRES=$(wc -l < "$GATE/func-patched-1.res")
[ "$NRES" -eq "$N_ITEMS" ] \
  || die "ERR_F1K_BRINGUP_FUNC: patched run #1 emitted $NRES result lines != $N_ITEMS items (engine/model-load failure — see func-patched-1.err)"
cmp -s "$GATE/func-patched-1.res" "$GATE/func-patched-2.res" \
  || die "ERR_F1K_BRINGUP_FUNC: determinism pre-check FAILED — patched binary not byte-identical across 2 runs at OMP_NUM_THREADS=$FUNC_OMP (the registered guard byte-identity instrument would be void; STOP before spend)"
echo "  determinism PASS: $N_ITEMS items byte-identical across 2 patched runs"

echo "-- (ii) pristine vs KaE-patched (KAE unset), byte-identical --"
run_score_engine "$PRISTINE_ENGINE" "$GATE/func-pristine.out" "$GATE/func-pristine.err" \
  || die "ERR_F1K_BRINGUP_FUNC: pristine scoring run failed (see func-pristine.err)"
grep -E "$RES" "$GATE/func-pristine.out" > "$GATE/func-pristine.res" || true
NRESP=$(wc -l < "$GATE/func-pristine.res")
[ "$NRESP" -eq "$N_ITEMS" ] \
  || die "ERR_F1K_BRINGUP_FUNC: pristine run emitted $NRESP result lines != $N_ITEMS items (see func-pristine.err)"
if cmp -s "$GATE/func-pristine.res" "$GATE/func-patched-1.res"; then
  echo "  FUNCTIONAL INERTNESS PASS: pristine == KaE-patched (KAE unset), $N_ITEMS items byte-identical"
  echo "{\"gate\":\"functional_inertness\",\"verdict\":\"PASS\",\"n_items\":$N_ITEMS,\"omp_num_threads\":$FUNC_OMP,\"determinism\":\"byte-identical\",\"pristine_vs_patched\":\"byte-identical\"}" > "$GATE/functional-inertness.json"
else
  diff "$GATE/func-pristine.res" "$GATE/func-patched-1.res" > "$GATE/func-byte-diff.txt" 2>&1 || true
  echo "{\"gate\":\"functional_inertness\",\"verdict\":\"FAIL\",\"n_items\":$N_ITEMS}" > "$GATE/functional-inertness.json"
  die "ERR_F1K_BRINGUP_FUNC: pristine vs KaE-patched forward/scoring output DIFFERS with KAE unset (see func-byte-diff.txt) — patch is NOT inert-by-default on this box"
fi

# affordability timing side-benefit: parse the engine's OWN scoring timer from
# run #1 stderr ("[score N req | Xs |"), which EXCLUDES model-load time.
TIMER=$(grep -oE '\[score [0-9]+ req \| [0-9.]+s' "$GATE/func-patched-1.err" | tail -1 || true)
SCORED_N=$(echo "$TIMER" | grep -oE '[0-9]+ req' | grep -oE '[0-9]+' || true)
SCORED_S=$(echo "$TIMER" | grep -oE '\| [0-9.]+s' | grep -oE '[0-9.]+' || true)
python3 - "$GATE/affordability-measured.json" "${SCORED_N:-0}" "${SCORED_S:-0}" \
         "$N_ITEMS" "$SPOT_RATE" "$FUNC_OMP" "$FUNC_T_SHORT" "$FUNC_T_LONG" <<'PY'
import sys, json
p = sys.argv[1]; sn = int(sys.argv[2]); ss = float(sys.argv[3])
n, rate, omp, ts, tl = int(sys.argv[4]), sys.argv[5], int(sys.argv[6]), int(sys.argv[7]), int(sys.argv[8])
spp = round(ss / sn, 4) if sn > 0 else None
json.dump({"blended_s_per_prefill_measured": spp,
           "scored_items_timed": sn, "scoring_wall_seconds": round(ss, 2),
           "sample_n_items": n, "spot_rate_usd_per_hour": rate,
           "omp_num_threads": omp, "sample_shapes": {"short_T": ts, "long_T": tl},
           "note": "run_score teacher-forced prefill timing on the PATCHED scoring binary, model-load EXCLUDED (engine scoring timer). Blended over short+long shapes. Feeds f1k_gcp.py affordability --rate <rate> --s-per-prefill <this>; the runner refines per-arm on-box. NULL blended => engine emitted no timer line; runner measures on-box."},
          open(p, "w"), indent=2)
print("affordability: measured blended s/prefill = %s over %s timed items -> %s" % (spp, sn, p))
PY
cat "$GATE/affordability-measured.json"
hb "functional-inertness-PASS"

step "5/5 REAL-CORPUS bring-up gate inputs (GAP-1/2/3 fix) -> gate-inputs.json"
# The synthetic functional-gate blend above (affordability-measured.json) is a
# SECONDARY diagnostic ONLY (v2 review finding 4: it mis-prices the gate in
# both directions). The construction-LICENSE inputs below are REAL-corpus:
# measured f (GAP-2), the frozen deterministic stratified per-item timing
# sample (GAP-1), per-item token counts for the token-aware projection
# (GAP-3). Rule + estimator: poc/gcp/F1K-BRINGUP-GATE-FIX.md v1 (frozen).
GATEPY="$HERE/f1k_bringup_gate.py"
[ -f "$GATEPY" ] || die "f1k_bringup_gate.py missing from the pushed poc/gcp dir"
CORPUS="$HERE/gate-corpus"     # pushed by the coordinator (poc/gcp/README.md step 2)
for f in construction-manifest.jsonl test.jsonl dev.jsonl guard.jsonl; do
  [ -f "$CORPUS/$f" ] || die "gate corpus file missing: $CORPUS/$f (push step)"
done
TOK_WRAPPER="${KOT_F1K_TOK_WRAPPER:-$(find "$HOME_DIR" -maxdepth 4 -name tok_glm52.py 2>/dev/null | head -1)}"
[ -n "$TOK_WRAPPER" ] || die "tok_glm52.py not found (push f1k-harness or set KOT_F1K_TOK_WRAPPER)"
TOKJSON="$(find "$ESTATE_DIR" -maxdepth 2 -name tokenizer.json | head -1)"
[ -n "$TOKJSON" ] || die "tokenizer.json not found in estate $ESTATE_DIR (ASM-1971 bring-up pin)"
pip3 -q install tokenizers 2>/dev/null || true
python3 "$GATEPY" fcount --corpus-dir "$CORPUS" --tok-wrapper "$TOK_WRAPPER" \
  --tokenizer "$TOKJSON" --out "$GATE/gate-tokens" || die "gate fcount FAILED"
python3 "$GATEPY" realize --tokens "$GATE/gate-tokens" --out "$GATE/gate-sample" \
  || die "gate realize FAILED"
hb "gate-tokenized"

# PIN_GB fixed at bring-up from MEASURED free-RAM headroom (plan §5 semantics;
# recording + truthful-attestation mechanics: F1K-PIN-FILE-FIX.md v5 — this
# step only FIXES the number and derives the BRING-UP pin; it never fakes one).
MEM_AVAIL_GB=$(awk '/MemAvailable/ {printf "%d", $2/1048576}' /proc/meminfo)
PIN_GB="${KOT_F1K_PIN_GB:-$(( MEM_AVAIL_GB - 8 ))}"
[ "$PIN_GB" -gt 50 ] && PIN_GB=50
[ "$PIN_GB" -ge 24 ] || die "PIN_GB headroom $PIN_GB GB < 24 (MemAvailable ${MEM_AVAIL_GB} GB) — outside the M4-measured 40-50 GB band's floor; STOP"

GATE_MAX_S="${KOT_F1K_GATE_MAX_S:-10800}"   # fail-closed timing budget (3 h)
GATE_T0=$(date +%s)
BOOT_ID=$(tr -d '\n' < /proc/sys/kernel/random/boot_id)
[ -n "$BOOT_ID" ] || die "cannot read boot_id for timing result binding"
run_gate_sample() {   # $1=phase $2=sample_id $3=result dir $4..=extra env
  local phase="$1" sid="$2" resdir="$3"; shift 3
  local man="$GATE/gate-sample/sample-$sid.score"
  local run_out="$GATE/gate-run-$phase-$sid.out"
  local run_err="$GATE/gate-run-$phase-$sid.err"
  [ $(( $(date +%s) - GATE_T0 )) -lt "$GATE_MAX_S" ] \
    || die "gate timing exceeded KOT_F1K_GATE_MAX_S=$GATE_MAX_S s (fail-closed: no silent truncation — raise the budget or STOP)"
  env -u KAE -u KAE_G -u KAE_SCORE -u KAE_DUMP -u KAE_CARRIER -u KAE_SPANS \
      -u KAE_MODE -u KAE_SEED -u KAE_DUMP_LAYERS \
      SNAP="$ESTATE_DIR" SCORE="$man" \
      OMP_NUM_THREADS="$FUNC_OMP" OMP_DYNAMIC=FALSE OMP_PROC_BIND=close \
      OMP_WAIT_POLICY=active COLI_OMP_TUNED=1 "$@" \
      "$SCORE_ENGINE" 64 4 8 > "$run_out" 2> "$run_err" \
    || die "gate timing run $phase/$sid FAILED (see $run_err)"
  local timer n s pin_ev result_tmp
  timer=$(grep -oE '\[score [0-9]+ req \| [0-9.]+s' "$run_err" | tail -1 || true)
  n=$(echo "$timer" | grep -oE '[0-9]+ req' | grep -oE '[0-9]+' || true)
  s=$(echo "$timer" | grep -oE '\| [0-9.]+s' | grep -oE '[0-9.]+' || true)
  { [ -n "$s" ] && [ "${n:-0}" -ge 1 ]; } || die "gate run $phase/$sid: engine emitted no scoring timer (see $run_err)"
  # [REV-B F3] engagement evidence VERBATIM: the [PIN] banner/marker lines
  # (armed banner grammar = the LANDED driver's PIN_ARMED_RE, ASM-2513;
  # wording fetch-grade ASM-1971 — a real-engine divergence is aligned in
  # the DRIVER regex once, and the control-box check follows). The gate
  # verdict REQUIRES a coherent armed banner per pinned T2 run.
  pin_ev=$(grep -E '\[PIN\]|pinning DISABLED' "$run_err" | head -5 | tr -d '"' | tr '\n' ';' || true)
  mkdir -p "$resdir"
  result_tmp=$(mktemp "$resdir/.$phase-$sid.XXXXXX.tmp")
  python3 - "$HERE" "$result_tmp" "$phase" "$sid" "$s" "$n" \
          "$pin_ev" "$BOOT_ID" <<'PY'
import os, sys
sys.path.insert(0, sys.argv[1])
import f1k_ops
record = {"phase": sys.argv[3], "sample_id": sys.argv[4],
          "s": float(sys.argv[5]), "timer_n": int(sys.argv[6]),
          "pin_evidence": sys.argv[7], "boot_id": sys.argv[8]}
payload = f1k_ops.canonical_json_bytes(record)
with open(sys.argv[2], "wb") as handle:
    handle.write(payload)
    handle.flush()
    os.fsync(handle.fileno())
PY
  write_timing_result "$phase" "$sid" "$result_tmp" \
    || die "gate timing result publish failed for $phase/$sid"
}

# T1: UNPINNED runs over the t1 subset with engine usage stats ON.
# [REV-B F1, gate-fix review #2] the engine interface is STATS=<file>
# (kae-add-path.patch:175/:180/:183: `stats=getenv("STATS")` ->
# `stats_dump(&m, stats)` writes THE named file) — the old `STATS=1` made
# every run overwrite one file named `1`, deriving the pin from the LAST
# item, not the T1 union. Now: ONE stats file PER RUN (rm'd first —
# correct whether stats_dump truncates or appends, which stays
# fetch-grade [ASM-1971]), asserted non-empty after the run, listed in an
# EXPLICIT manifest; the merge (`pinfile`) is fail-closed on any
# missing/empty/malformed file and records per-file sha provenance.
T1_IDS=$(python3 -c "import json;print(' '.join(json.load(open('$GATE/gate-sample/timing-sample.json'))['t1_sample_ids']))")
T1_CWD="$GATE/t1-cwd"; mkdir -p "$T1_CWD"
T1_RESULTS_DIR="$GATE/t1-results"; mkdir -p "$T1_RESULTS_DIR"
T1_STATS_DIR="${KOT_F1K_STATS_DIR:-$GATE/t1-stats}"; mkdir -p "$T1_STATS_DIR"
: > "$GATE/t1-stats.manifest"
for sid in $T1_IDS; do
  SFILE="$T1_STATS_DIR/stats-$sid.txt"
  SFILE_TMP=$(mktemp "$T1_STATS_DIR/.stats-$sid.XXXXXX.tmp")
  rm -f "$SFILE_TMP"  # fresh whether the engine opens STATS append or truncate
  ( cd "$T1_CWD" && run_gate_sample t1 "$sid" "$T1_RESULTS_DIR" STATS="$SFILE_TMP" )
  [ -s "$SFILE_TMP" ] || die "T1 run $sid wrote NO usage stats at $SFILE_TMP (STATS=<file>, kae-add-path.patch:175) — the pin never derives from a partial T1 union; STOP (maintainer surface; re-verify the STATS knob at the (7) semantic gate)"
  atomic_publish_file "$SFILE_TMP" "$SFILE" \
    || die "T1 run $sid stats atomic publish failed"
  echo "$SFILE" >> "$GATE/t1-stats.manifest"
done
validate_timing_results t1 "$T1_RESULTS_DIR" $T1_IDS \
  || die "T1 timing result set incomplete/invalid before pin derivation"
hb "gate-t1-done"

# bring-up pin file at PIN_GB from the EXPLICIT T1 stats manifest.
# [REV-B F3] an underivable pin is a fail-closed STOP: shape (ii)
# (unpinned) was REJECTED (SSA3.5) and the gate REFUSES regime "unpinned"
# — running 30 unlicensable T2 timings would only burn budget.
PIN_REGIME="pinned-bringup"; PIN_FILE="$GATE/pin_bringup.stats"; PIN_SHA=""
python3 "$GATEPY" pinfile --stats-manifest "$GATE/t1-stats.manifest" \
     --pin-gb "$PIN_GB" --out "$PIN_FILE" > "$GATE/pinfile.json" 2>&1 \
  || die "bring-up pin underivable (see pinfile.json) — shape (i) is the ONLY licensable regime (unpinned was REJECTED, fix memo SSA3.5/SSB); mandatory maintainer surface"
PIN_SHA=$(sha256sum "$PIN_FILE" | awk '{print $1}')

# T2: the LICENSE timing — every sample text, per-item engine timer (model
# load excluded), ALWAYS pinned (evidence per run; the control-box verdict
# verifies an armed banner per run against the bound sha/PIN_GB).
T2_RESULTS_DIR="$GATE/t2-results"; mkdir -p "$T2_RESULTS_DIR"
ALL_IDS=$(python3 -c "import json;print(' '.join(e['sample_id'] for e in json.load(open('$GATE/gate-sample/timing-sample.json'))['entries']))")
for sid in $ALL_IDS; do
  run_gate_sample t2 "$sid" "$T2_RESULTS_DIR" PIN="$PIN_FILE" PIN_GB="$PIN_GB"
done
validate_timing_results t2 "$T2_RESULTS_DIR" $ALL_IDS \
  || die "T2 timing result set incomplete/invalid before collect"
hb "gate-t2-done"

python3 "$GATEPY" collect --sample "$GATE/gate-sample/timing-sample.json" \
  --tokens "$GATE/gate-tokens" --t2 "$T2_RESULTS_DIR" \
  --t1 "$T1_RESULTS_DIR" --rate "$SPOT_RATE" \
  --pin-sha "$PIN_SHA" --pin-gb "$PIN_GB" --pin-regime "$PIN_REGIME" \
  --pin-path "$PIN_FILE" \
  --pin-derivation "$PIN_FILE.derivation.json" \
  --dump-a "$(cat "$GATE/tiny-dump.status" 2>/dev/null || echo MISSING)" \
  --dump-b "$(cat "$GATE/dump-b.status" 2>/dev/null || echo MISSING)" \
  --dump-c "$(cat "$GATE/moe-sum-crosscheck.status" 2>/dev/null || echo MISSING)" \
  --functional "$(python3 -c "import json;print(json.load(open('$GATE/functional-inertness.json')).get('verdict','MISSING'))" 2>/dev/null || echo MISSING)" \
  --out "$GATE/gate-inputs.json" || die "gate collect FAILED"
# The bring-up pin IS the construction-phase CAMPAIGN pin (fix memo SSA3
# C-decision): persist it VERIFIED — [REV-B F3, gate-fix review #4] no
# `|| true`: upload, RE-READ from GCS, and require the byte-exact sha; a
# licensed pin that failed to persist is a dead campaign, fail closed.
gsutil -q cp "$PIN_FILE" "$BUCKET/f1k/bringup/campaign-pin.stats" \
  || die "campaign-pin upload FAILED (gsutil cp)"
gsutil -q cp "$PIN_FILE.derivation.json" "$BUCKET/f1k/bringup/campaign-pin.stats.derivation.json" \
  || die "campaign-pin derivation upload FAILED"
REMOTE_PIN_SHA=$(gsutil -q cat "$BUCKET/f1k/bringup/campaign-pin.stats" | sha256sum | awk '{print $1}')
[ "$REMOTE_PIN_SHA" = "$PIN_SHA" ] \
  || die "campaign-pin GCS re-read sha $REMOTE_PIN_SHA != local $PIN_SHA — persisted bytes differ from the licensed pin; fail closed"
echo "CONTROL-BOX-VERDICT-REQUIRED" > "$GATE/bringup-gate.status"
cat > "$GATE/bringup-gate-README.txt" <<EOF
REAL-CORPUS gate inputs ready: $GATE/gate-inputs.json (mirrored to GCS).
Pull it and run the MECHANICAL verdict on the control box:
  python3 poc/gcp/f1k_gcp.py gate --inputs <pulled gate-inputs.json>
GREEN -> construction proceeds without re-surfacing (plan §7 standing
authorization). STOP (exit 2 ERR_F1K_BRINGUP_GATE) -> MANDATORY maintainer
surface. The synthetic blend (affordability-measured.json) is a SECONDARY
diagnostic; \`f1k_gcp.py affordability\` licenses NOTHING (exit 3 even on GO).
HARD CONJUNCTS (v3-review): dump preconditions (a)/(b)/(c) + the functional
gate must be recorded PASS in gate-inputs.json or the verdict STOPs. After
the on-box confirmations, the RUNNER overwrites tiny-dump.status and
moe-sum-crosscheck.status with the literal PASS and RE-RUNS the collect
command above (cheap; no re-timing) before pulling gate-inputs.json.
The caps are tested RESERVE-INCLUSIVE (+\$8 / +8/rate hours) on the control
box; the verdict also REQUIRES per-run pin-ENGAGEMENT evidence for the bound
pin sha/PIN_GB and REFUSES regime "unpinned" [REV-B]. The campaign pin for
construction is campaign-pin.stats (sha-verified persisted, derivation
sidecar alongside); construction fetches it via \`f1k_gcp.py pin-fetch\`
(byte-verified export of PIN/PIN_GB — never ambient env), bound per
F1K-PIN-FILE-FIX.md v5.
EOF
cat "$GATE/bringup-gate-README.txt"
hb "gate-inputs-ready"

step "DONE (bring-up scaffolded; STOP before construction spend)"
echo "Bring-up artifacts in $GATE/ (mirrored to $BUCKET/f1k/bringup/)."
echo "NEXT (gated): finalize dump preconditions (a)+(c) on-box; pull"
echo "gate-inputs.json and run \`f1k_gcp.py gate\` on the control box — a"
echo "GREEN bringup-gate.json verdict (and ONLY that) licenses construction."
gsutil -q -m cp -r "$GATE" "$BUCKET/f1k/bringup/" || true
hb "DONE-bringup-scaffold"
