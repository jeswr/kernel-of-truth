#!/usr/bin/env python3
"""Transport helpers for the Modal port (poc/modal) — stdlib only, NO modal import.

Design contract (poc/modal/README.md, bead kernel-of-truth-0oj): the Modal
wrapper stages bytes, runs the UNCHANGED poc/e2/runner/e2_runner.py, and ships
the runner's output directory back as opaque bytes. Transport provenance goes
in SIDECAR files only (provenance-modal.json, kot-e2-run.log, RUNNER_EXIT) —
mirroring how the AWS pull path (poc/gpu/user-data-e2-pull.sh.tpl) publishes
nvidia-smi output + run logs + `rc=N` NEXT TO the runner's results instead of
editing them. Consequence: results-e2.json / verdict-e2.md round-trip
byte-identical across transports given the same runner + input bytes (enforced
here by the staged-manifest assertion); the only per-invocation difference is
the runner's own `date` field, which varies run-to-run on ANY transport.

Everything in this module is unit-testable without a Modal account/token
(poc/modal/test_modal_port.py) and is imported verbatim inside the Modal
container (shipped via Image.add_local_python_source).
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import subprocess
import sys

# Sidecar names — deliberately identical to the AWS pull path's artefacts
# (user-data-e2-pull.sh.tpl copies kot-e2-run.log + writes RUNNER_EXIT).
RUN_LOG_NAME = "kot-e2-run.log"
RUNNER_EXIT_NAME = "RUNNER_EXIT"
PROVENANCE_NAME = "provenance-modal.json"

# Environment capture policy: keep only Modal/GPU identifiers, and even then
# drop anything that smells like a credential. No token ever enters results.
_ENV_KEEP_PREFIXES = ("MODAL_", "NVIDIA_", "CUDA_")
_ENV_DROP_SUBSTRINGS = ("TOKEN", "SECRET", "KEY", "AUTH", "CREDENTIAL", "PASSWORD")


def utcnow_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat()


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def input_manifest(runner_py: str, requirements_txt: str, inputs_dir: str) -> dict:
    """sha256 manifest over the EXACT bytes the runner consumes.

    Keys are transport-independent relative names so the manifest computed on
    the coordinator box compares equal (`==`) to the one computed inside the
    Modal container over the staged copies. Any drift is a staging bug and the
    run fails closed (ERR_STAGING_MISMATCH in modal_e2.py).
    """
    man = {
        "runner/e2_runner.py": sha256_file(runner_py),
        "runner/requirements.txt": sha256_file(requirements_txt),
    }
    for name in sorted(os.listdir(inputs_dir)):
        p = os.path.join(inputs_dir, name)
        if os.path.isfile(p):
            man[f"inputs/{name}"] = sha256_file(p)
    return man


def run_runner(
    python_exe: str,
    runner_py: str,
    inputs_dir: str,
    out_dir: str,
    device: str = "cuda",
    mock: bool = False,
    n_perm: int | None = None,
    k_sets: int | None = None,
    echo: bool = True,
) -> tuple[int, str]:
    """Invoke the unchanged e2_runner.py as a subprocess; return (rc, log).

    n_perm/k_sets exist ONLY for the token-free local mock validation
    (test/validate paths); the Modal entrypoint never sets them, so real runs
    always use the pre-registered defaults baked into the runner.
    """
    cmd = [python_exe, runner_py, "--inputs-dir", inputs_dir, "--out-dir", out_dir, "--device", device]
    if mock:
        cmd.append("--mock")
    if n_perm is not None:
        cmd += ["--n-perm", str(n_perm)]
    if k_sets is not None:
        cmd += ["--k-sets", str(k_sets)]
    os.makedirs(out_dir, exist_ok=True)
    lines: list[str] = [f"$ {' '.join(cmd)}\n"]
    with subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1
    ) as proc:
        assert proc.stdout is not None
        for line in proc.stdout:
            lines.append(line)
            if echo:
                sys.stdout.write(line)
                sys.stdout.flush()
    rc = proc.returncode
    lines.append(f"[runner exit rc={rc}]\n")
    return rc, "".join(lines)


def collect_dir(results_dir: str) -> dict:
    """{relative posix path: bytes} for every file under results_dir."""
    out: dict = {}
    for root, _dirs, files in os.walk(results_dir):
        for name in sorted(files):
            p = os.path.join(root, name)
            rel = os.path.relpath(p, results_dir).replace(os.sep, "/")
            with open(p, "rb") as f:
                out[rel] = f.read()
    return dict(sorted(out.items()))


def package_results(results_dir: str, run_log: str, rc: int, provenance: dict) -> dict:
    """Runner outputs as opaque bytes + the three AWS-parity sidecars.

    The runner's own files are NEVER rewritten (byte-identity contract); the
    sidecar names are reserved and may not collide with runner output.
    """
    files = collect_dir(results_dir)
    for reserved in (RUN_LOG_NAME, RUNNER_EXIT_NAME, PROVENANCE_NAME):
        if reserved in files:
            raise SystemExit(f"ERR_SIDECAR_COLLISION: runner emitted reserved name {reserved!r}")
    files[RUN_LOG_NAME] = run_log.encode()
    files[RUNNER_EXIT_NAME] = f"rc={rc}\n".encode()  # same format as the AWS tpl
    files[PROVENANCE_NAME] = (json.dumps(provenance, indent=2, sort_keys=True) + "\n").encode()
    return files


def unpack_files(files: dict, dest_dir: str) -> list:
    """Write a returned {rel path: bytes} map under dest_dir. Fail closed on
    absolute paths / parent traversal (never trust remote-shaped keys)."""
    written = []
    dest_abs = os.path.abspath(dest_dir)
    for rel in sorted(files):
        if os.path.isabs(rel) or rel.startswith(("/", "\\")):
            raise SystemExit(f"ERR_UNPACK_PATH: absolute path in results: {rel!r}")
        target = os.path.abspath(os.path.join(dest_abs, rel))
        if not (target == dest_abs or target.startswith(dest_abs + os.sep)):
            raise SystemExit(f"ERR_UNPACK_PATH: path escapes destination: {rel!r}")
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "wb") as f:
            f.write(files[rel])
        written.append(target)
    return written


def verdict_outcome(results_dir: str) -> str:
    """Parse results-e2*.json and return its OUTCOME (mirrors collect-e2.sh's
    post-scp verification). Fails closed if no parseable results JSON exists."""
    cands = sorted(
        n for n in os.listdir(results_dir) if n.startswith("results-e2") and n.endswith(".json")
    )
    if "results-e2.json" in cands:  # prefer the real run over -mock if both exist
        cands = ["results-e2.json"] + [c for c in cands if c != "results-e2.json"]
    if not cands:
        raise SystemExit(f"ERR_NO_RESULTS: no results-e2*.json in {results_dir}")
    with open(os.path.join(results_dir, cands[0])) as f:
        j = json.load(f)
    outcome = j.get("outcome")
    if not outcome:
        raise SystemExit(f"ERR_NO_OUTCOME: {cands[0]} has no 'outcome' field")
    return str(outcome)


def redact_env(env: dict) -> dict:
    """Modal/GPU identifiers only; anything credential-shaped is dropped."""
    return {
        k: v
        for k, v in sorted(env.items())
        if k.startswith(_ENV_KEEP_PREFIXES)
        and not any(s in k.upper() for s in _ENV_DROP_SUBSTRINGS)
    }


def gpu_info() -> dict:
    """nvidia-smi summary (name/driver/memory), tolerant of absence."""
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,driver_version,memory.total", "--format=csv,noheader"],
            capture_output=True, text=True, timeout=30,
        )
        if out.returncode == 0 and out.stdout.strip():
            return {"available": True, "nvidia_smi": out.stdout.strip()}
        return {"available": False, "nvidia_smi_rc": out.returncode, "stderr": out.stderr.strip()[:500]}
    except (OSError, subprocess.TimeoutExpired) as e:
        return {"available": False, "error": str(e)}


def build_provenance(
    *,
    transport: str,
    gpu_requested: str,
    gpu_seen: dict,
    staged_manifest: dict,
    runner_exit: int,
    started_utc: str,
    finished_utc: str,
    packages: dict | None = None,
    environment: dict | None = None,
    notes: str | None = None,
) -> dict:
    """The sidecar provenance record. AWS-path parity: the pull path records
    GPU + environment in logs and rc in RUNNER_EXIT; here the same facts (plus
    the image/package pins Modal makes explicit) land in one JSON sidecar.
    The staged manifest doubles as the runner/input content pin."""
    prov = {
        "provenance_version": 1,
        "transport": transport,
        "gpu_requested": gpu_requested,
        "gpu_seen": gpu_seen,
        "python": sys.version,
        "packages": packages or {},
        "environment": environment or {},
        "staged_sha256": staged_manifest,
        "runner_exit": runner_exit,
        "started_utc": started_utc,
        "finished_utc": finished_utc,
    }
    if notes:
        prov["notes"] = notes
    return prov
