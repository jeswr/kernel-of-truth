#!/usr/bin/env python3
"""ufo-check-0 POST-RUN collector — turn the runner's FILE outputs into the
results-log record BODIES that tools/registry/log-append.py appends and the
FROZEN stdin analysis adapter (analysis/ufo_check_0_stdin.py) consumes.

WHY THIS EXISTS: ufo_check0_runner.py writes its results as FILES
(run-records-ufo0[-mock].jsonl + run-sidecar[-mock].json), but the honesty
spine's ONLY writer is tools/registry/log-append.py and the ONLY input the
pinned analysis adapter reads is eligible run records on stdin. ufo-check-0
has never run, so — unlike rules-1-c / rules-2 whose stdin successors pin an
already-materialised campaign file — the heavy per-item rows and the campaign
sidecar must ride IN the log records (analysis/ufo_check_0_stdin.py docstring,
INPUT CONTRACT): each eligible record carries `metrics.rows` (its per-item
rows) and `metrics.sidecar` (the campaign sidecar). This tool emits exactly
those record BODIES; the coordinator feeds each to log-append (which stamps
seq/prev_sha256/ts/runner/schema_version/experiment/config_sha256 and
chain-appends it), and verdict-gen then pipes the eligible rows to the adapter.

RECORD BODY (per log-append: event/phase/config/metrics/exit + prereg_hash):
  { "event": "run", "phase": "final",
    "config": {"arm","host","seed"}   # cell granularity (default)
              | {}                      # run granularity (one whole-campaign row)
    "metrics": {"rows": [<per-item rows>], "sidecar": <campaign sidecar>},
    "prereg_hash": <frozen_sha256 of registry/experiments/ufo-check-0.json>,
    "exit": "ok" }
Metrics are RAW — the rows and sidecar carry NO derived/verdict statistics, so
log-append's §2.4 forbidden-key scan passes (all verdict maths lives in the
pinned adapter). No stamped field (seq/prev_sha256/ts/runner/schema_version)
and no config_sha256 is emitted — log-append owns those.

BYTE-PARITY (hard requirement): the pinned analysis is a PURE FUNCTION of the
eligible set whose row list is the eligible records' `metrics.rows`
concatenated IN STDIN ORDER (adapter docstring), and several reductions are
float-order-sensitive (e.g. cost_ledger.checker_us_mean, the per-item AU
floor). verdict-gen streams eligible rows in log (append) order, so this tool
MUST NOT reorder a single row. It splits the file into CONTIGUOUS
(host,arm,seed) groups — the runner emits each cell's rows contiguously, so
inserting record boundaries at cell transitions is the identity on the file's
row sequence. The coordinator MUST append the emitted records in the order
this tool prints them (file order). Result: the adapter's reconstructed row
list is byte-for-byte the file the CLI original (analysis/ufo_check_0.py)
reads, so their outputs are byte-identical (validated at $0 on the mock).

Granularity is auditor's choice; both are byte-parity-equivalent:
  --granularity cell  (default) one record per (host,arm,seed) cell — mirrors
                      the runner's own checkpoint/emit unit; config carries the
                      cell axes; the sidecar rides in every record (identical
                      copies; the adapter de-dups and fails closed on conflict).
  --granularity run   one record for the whole campaign (config {}); the single
                      record carries all rows + the sidecar.

$0, stdlib only. Reads files, writes JSONL bodies; never writes the log.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

# frozen_sha256 of registry/experiments/ufo-check-0.json (== frozen-index).
DEFAULT_PREREG = ("9e3b58b8479d90f0955e1f6c90951a0313e8a8c51aac3cae1b02f1"
                  "529fcd497e")
CELL_KEYS = ("host", "arm", "seed")


def load_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(ln) for ln in f if ln.strip()]


def group_cells(rows):
    """Contiguous (host,arm,seed) groups, PRESERVING FILE ORDER exactly.

    The runner emits each cell's rows contiguously (one emit_rows per cell), so
    starting a new group only at a key transition inserts record boundaries
    WITHOUT reordering any row — the concatenation of the groups is the
    identity on the file's row sequence. This holds even under checkpoint
    resume (cells written in a different cell-order stay individually
    contiguous), because the tool faithfully preserves whatever order the file
    already has (the same file the CLI analysis reads)."""
    groups = []
    for r in rows:
        key = tuple(r[k] for k in CELL_KEYS)
        if not groups or groups[-1][0] != key:
            groups.append((key, []))
        groups[-1][1].append(r)
    return groups


def build_bodies(rows, sidecar, prereg_hash, granularity):
    if granularity == "run":
        return [{
            "event": "run", "phase": "final", "config": {},
            "metrics": {"rows": rows, "sidecar": sidecar},
            "prereg_hash": prereg_hash, "exit": "ok",
        }]
    bodies = []
    for (host, arm, seed), cell_rows in group_cells(rows):
        bodies.append({
            "event": "run", "phase": "final",
            "config": {"arm": arm, "host": host, "seed": seed},
            "metrics": {"rows": cell_rows, "sidecar": sidecar},
            "prereg_hash": prereg_hash, "exit": "ok",
        })
    return bodies


def main():
    ap = argparse.ArgumentParser(
        description="Collect ufo-check-0 runner outputs into log record bodies.")
    ap.add_argument("--run-records", required=True,
                    help="run-records-ufo0[-mock].jsonl from the runner")
    ap.add_argument("--sidecar", required=True,
                    help="run-sidecar[-mock].json from the runner")
    ap.add_argument("--out", default="-", help="JSONL out (default stdout)")
    ap.add_argument("--experiment", default="ufo-check-0")
    ap.add_argument("--prereg-hash", default=DEFAULT_PREREG)
    ap.add_argument("--granularity", choices=["cell", "run"], default="cell")
    ap.add_argument("--repo-root", default=None,
                    help="repo root for the frozen-index cross-check "
                         "(default: inferred from this file)")
    args = ap.parse_args()

    rows = load_jsonl(args.run_records)
    if not rows:
        sys.exit("ERR_UFO0_COLLECT_NO_ROWS: %s is empty" % args.run_records)
    with open(args.sidecar, encoding="utf-8") as f:
        sidecar = json.load(f)

    # Cross-check the prereg hash against the frozen index when reachable
    # (fail closed) so a stale hash can never be emitted silently.
    root = args.repo_root or os.path.normpath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
    idx_path = os.path.join(root, "registry", "frozen-index.json")
    if os.path.isfile(idx_path):
        with open(idx_path, encoding="utf-8") as f:
            idx = json.load(f)
        want = idx.get(args.experiment)
        if want and want != args.prereg_hash:
            sys.exit("ERR_UFO0_COLLECT_PREREG: --prereg-hash %s != "
                     "frozen-index[%s] %s (refusing)"
                     % (args.prereg_hash, args.experiment, want))

    bodies = build_bodies(rows, sidecar, args.prereg_hash, args.granularity)

    out = sys.stdout if args.out == "-" else open(args.out, "w",
                                                  encoding="utf-8")
    try:
        for b in bodies:
            out.write(json.dumps(b, sort_keys=True) + "\n")
    finally:
        if out is not sys.stdout:
            out.close()
    sys.stderr.write(
        "collected %d row(s) into %d record bod%s [granularity=%s]\n"
        % (len(rows), len(bodies), "y" if len(bodies) == 1 else "ies",
           args.granularity))


if __name__ == "__main__":
    main()
