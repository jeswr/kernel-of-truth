#!/usr/bin/env python3
"""knull-v2 POST-RUN collector — turn the merged run FILES into the results-log
record BODIES that tools/registry/log-append.py appends and the FROZEN stdin
analysis adapter (analysis/knull_v3_stdin.py) consumes.

WHY THIS EXISTS: the knull-v2 run is already merged to file
(poc/knull/results-incoming/knull-v2-20260713/merged/run-records.jsonl, 36 SAP
CELL records, + merged/item-meta.json), but the honesty spine's ONLY writer is
tools/registry/log-append.py and the ONLY input the pinned analysis adapter
reads is eligible run records on stdin. The 36 cell records live under
results-incoming (results staging, not a durable pinned artifact), so — rather
than pinning a ROWS_PATH/ROWS_SHA256 into the frozen script (the rules-1-c
style) — the SAP cell records and the item-meta ride IN the log records (the
ufo-check-0 style; analysis/knull_v3_stdin.py INPUT CONTRACT): each eligible
record carries `metrics.rows` (its SAP cell record(s)) and `metrics.sidecar`
(the item-meta document). This tool emits exactly those record BODIES; the
coordinator feeds each to log-append (which stamps seq/prev_sha256/ts/runner/
schema_version/experiment/config_sha256 and chain-appends it), and verdict-gen
then pipes the eligible rows to the adapter.

RECORD BODY (per log-append: event/phase/config/metrics/exit + prereg_hash):
  { "event": "run", "phase": "final",
    "config": {"arm","cell","rung","seed"}   # cell granularity (default)
              | {}                             # run granularity (whole campaign)
    "metrics": {"rows": [<SAP cell record(s)>], "sidecar": <item-meta>},
    "prereg_hash": <frozen_sha256 of registry/experiments/knull-v2.json>,
    "exit": "ok" }
Metrics are RAW — the SAP records carry the run's cov/acc/flops/metric_vector
and the sidecar carries item-meta (types + prompt-token counts); NONE of the
carried keys is a derived/verdict statistic, so log-append's §2.4 forbidden-key
scan passes (all TOST/CI/Holm/p-value maths lives in the pinned adapter). No
stamped field (seq/prev_sha256/ts/runner/schema_version) and no config_sha256
is emitted — log-append owns those.

BYTE-PARITY (hard requirement): analyse() in knull_v3.py/knull_v3_stdin.py
groups records by (arm,cell,rung) and SORTS each group by seed, so the analysis
is a PURE, ORDER-INVARIANT function of the record SET — the adapter's
reconstructed record list (the eligible records' metrics.rows concatenated)
reproduces the CLI original's inputs exactly, so their outputs are
byte-identical. This tool nonetheless preserves file order (identity on the row
sequence) for auditability; the coordinator MUST append the emitted records in
the order this tool prints them.

Granularity is auditor's choice; both are byte-parity-equivalent:
  --granularity cell  (default) one record per (arm,cell,rung,seed) SAP cell —
                      mirrors the merged run's own emit unit; config carries the
                      cell axes; the item-meta sidecar rides in every record
                      (identical copies; the adapter de-dups and fails closed on
                      conflict).
  --granularity run   one record for the whole campaign (config {}); the single
                      record carries all rows + the sidecar.

The coordinator will RE-FREEZE knull-v2 (repinning analysis_script to
knull_v3_stdin.py), which changes frozen_sha256; pass the NEW hash via
--prereg-hash after the freeze so log-append's G-1 prereg check matches. The
default is the CURRENT frozen_sha256; a mismatch against the frozen index fails
closed (never emitting a stale hash silently).

$0, stdlib only. Reads files, writes JSONL bodies; never writes the log.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

# frozen_sha256 of registry/experiments/knull-v2.json (== frozen-index) at
# authoring time; the coordinator overrides this with the POST-refreeze hash.
DEFAULT_PREREG = ("d04e73649f5aaa64a778f316715601e2d1f68fd3b"
                  "ff23d9b32843db2fd569b9d")
CELL_KEYS = ("arm", "cell", "rung", "seed")


def load_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(ln) for ln in f if ln.strip()]


def group_cells(rows):
    """Contiguous (arm,cell,rung,seed) groups, PRESERVING FILE ORDER exactly.

    Starting a new group only at a key transition inserts record boundaries
    WITHOUT reordering any row — the concatenation of the groups is the identity
    on the file's row sequence (the same rows the CLI analysis reads). For the
    merged knull-v2 file each (arm,cell,rung,seed) is a unique cell, so each
    group holds exactly one SAP record."""
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
    for (arm, cell, rung, seed), cell_rows in group_cells(rows):
        bodies.append({
            "event": "run", "phase": "final",
            "config": {"arm": arm, "cell": cell, "rung": rung, "seed": seed},
            "metrics": {"rows": cell_rows, "sidecar": sidecar},
            "prereg_hash": prereg_hash, "exit": "ok",
        })
    return bodies


def main():
    ap = argparse.ArgumentParser(
        description="Collect knull-v2 merged run outputs into log record "
                    "bodies for log-append + the stdin analysis adapter.")
    ap.add_argument("--run-records", required=True,
                    help="merged/run-records.jsonl (the 36 SAP cell records)")
    ap.add_argument("--item-meta", required=True,
                    help="merged/item-meta.json (kernel.types + prompt tokens)")
    ap.add_argument("--out", default="-", help="JSONL out (default stdout)")
    ap.add_argument("--experiment", default="knull-v2")
    ap.add_argument("--prereg-hash", default=DEFAULT_PREREG,
                    help="frozen_sha256 to stamp as prereg_hash; pass the "
                         "POST-refreeze hash after the coordinator re-freezes")
    ap.add_argument("--granularity", choices=["cell", "run"], default="cell")
    ap.add_argument("--repo-root", default=None,
                    help="repo root for the frozen-index cross-check "
                         "(default: inferred from this file)")
    args = ap.parse_args()

    rows = load_jsonl(args.run_records)
    if not rows:
        sys.exit("ERR_KNULL_COLLECT_NO_ROWS: %s is empty" % args.run_records)
    with open(args.item_meta, encoding="utf-8") as f:
        sidecar = json.load(f)

    # Cross-check the prereg hash against the frozen index when reachable
    # (fail closed) so a stale hash can never be emitted silently.
    root = args.repo_root or os.path.normpath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     "..", "..", ".."))
    idx_path = os.path.join(root, "registry", "frozen-index.json")
    if os.path.isfile(idx_path):
        with open(idx_path, encoding="utf-8") as f:
            idx = json.load(f)
        want = idx.get(args.experiment)
        if want and want != args.prereg_hash:
            sys.exit("ERR_KNULL_COLLECT_PREREG: --prereg-hash %s != "
                     "frozen-index[%s] %s (refusing; pass the POST-refreeze "
                     "hash)" % (args.prereg_hash, args.experiment, want))

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
        "collected %d SAP cell row(s) into %d record bod%s [granularity=%s]\n"
        % (len(rows), len(bodies), "y" if len(bodies) == 1 else "ies",
           args.granularity))


if __name__ == "__main__":
    main()
