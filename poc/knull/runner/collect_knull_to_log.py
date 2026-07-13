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
    "config": {"store","cell","retry_budget","seed"}  # cell granularity (default)
              | {}                                     # run granularity (whole campaign)
    "metrics": {"rows": [<SAP cell record(s)>], "sidecar": <item-meta>},
    "prereg_hash": <frozen_sha256 of registry/experiments/knull-v2.json>,
    "exit": "ok" }

CONFIG IS KEYED BY THE DECLARED IV NAMES, WITH EXACT DECLARED LEVELS. This is
load-bearing: verdict-gen's select_eligible (tools/registry/verdict-gen.py)
builds iv_levels = {iv.name: iv.levels} from the FROZEN record's
/design/independent_vars and EXCLUDES any run record whose config[iv.name] is
not a member of that IV's declared levels. The SAP run records use the runner's
own axis vocabulary (arm/cell/rung/k/seed), which is NOT the declared level
text, so config must be TRANSLATED to the declared levels (read from the frozen
record — never hardcoded, so it stays correct if the design text changes) and
validated fail-closed:
  * config.store        = the declared `store` level equal to record.arm or
                          beginning `record.arm + "("` — kernel/plain/opaque map
                          to themselves; plain-padded maps to the full
                          parenthetical ASM-1086 level string.
  * config.cell         = the declared `cell` level for (record.cell,
                          record.rung): model-alone->"alone-<rung>", otherwise
                          "<record.cell>-<rung>", matched (equal-or-"(" prefix)
                          against the declared cell levels — so
                          (model-alone,R1)->alone-R1, (model-alone,R3)->alone-R3,
                          (verify-retry,R1)->verify-retry-R1,
                          (shuffled-verify-retry,R1)->the full
                          shuffled-verify-retry-R1(kernel store only) string.
  * config.retry_budget = record.k (must be an exact member of the declared
                          retry_budget levels: {0, 4}).
  * config.seed         = record.seed (exact member of the declared seed levels).
Any candidate that does not resolve to EXACTLY ONE declared level fails closed
(ERR_KNULL_COLLECT_IV) — no value outside the declared set is ever invented.

Metrics are RAW — the SAP records carry the run's cov/acc/flops/metric_vector
and the sidecar carries item-meta (types + prompt-token counts); NONE of the
carried keys is a derived/verdict statistic, so log-append's §2.4 forbidden-key
scan passes (all TOST/CI/Holm/p-value maths lives in the pinned adapter). No
stamped field (seq/prev_sha256/ts/runner/schema_version) and no config_sha256
is emitted — log-append owns those.

BYTE-PARITY (hard requirement, unaffected by the config keys): analyse() in
knull_v3.py/knull_v3_stdin.py groups records by (arm,cell,rung) and SORTS each
group by seed, so the analysis is a PURE, ORDER-INVARIANT function of the
record SET — the adapter's reconstructed record list (the eligible records'
metrics.rows concatenated) reproduces the CLI original's inputs exactly, so
their outputs are byte-identical. `config` is consumed only by verdict-gen's
eligibility filter; the analysis reads metrics.rows/metrics.sidecar. This tool
preserves file order (identity on the row sequence) for auditability; the
coordinator MUST append the emitted records in the order this tool prints them.

Granularity is auditor's choice:
  --granularity cell  (default) one record per (arm,cell,rung,seed) SAP cell —
                      mirrors the merged run's own emit unit; config carries the
                      DECLARED IV levels (so verdict-gen counts eligible_runs=36);
                      the item-meta sidecar rides in every record (identical
                      copies; the adapter de-dups and fails closed on conflict).
  --granularity run   one record for the whole campaign (config {}); the single
                      record carries all rows + the sidecar (eligible_runs=1;
                      verdict-parity-equivalent but does NOT reach the per-cell
                      completeness count).

RE-FREEZE: knull-v2 was re-frozen with the analysis_script repinned to
knull_v3_stdin.py, so frozen_sha256 changed; pass the CURRENT hash via
--prereg-hash (default below tracks the live frozen index). A mismatch against
the frozen index fails closed (never emitting a stale hash silently).

$0, stdlib only. Reads files, writes JSONL bodies; never writes the log.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

# frozen_sha256 of registry/experiments/knull-v2.json (== frozen-index) AFTER
# the reset-refreeze that repinned analysis_script to knull_v3_stdin.py.
DEFAULT_PREREG = ("2ba87b11e55a108b84ed7707b29930a9e2049fe2"
                  "b0bf171deba5f7d98d75d0db")
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
    group holds exactly one SAP record; all rows in a group share the config."""
    groups = []
    for r in rows:
        key = tuple(r[k] for k in CELL_KEYS)
        if not groups or groups[-1][0] != key:
            groups.append((key, []))
        groups[-1][1].append(r)
    return groups


def _read_iv_levels(record_path):
    """Load {iv_name: levels} from the FROZEN record's design — the SAME source
    verdict-gen.select_eligible reads, so config is validated against exactly
    the levels the eligibility check will enforce (fail closed if absent)."""
    try:
        with open(record_path, encoding="utf-8") as f:
            rec = json.load(f)
    except OSError as e:
        sys.exit("ERR_KNULL_COLLECT_RECORD: cannot read %s: %s"
                 % (record_path, e))
    ivs = (rec.get("design") or {}).get("independent_vars")
    if not ivs:
        sys.exit("ERR_KNULL_COLLECT_RECORD: %s has no /design/independent_vars"
                 % record_path)
    levels = {iv["name"]: iv["levels"] for iv in ivs}
    for need in ("store", "cell", "retry_budget", "seed"):
        if need not in levels:
            sys.exit("ERR_KNULL_COLLECT_RECORD: declared IVs missing %r "
                     "(have %s)" % (need, sorted(levels)))
    return levels


def _match_level(candidate, levels, iv_name, seed):
    """Return the UNIQUE declared level equal to `candidate` or beginning
    `candidate + '('` (the parenthetical-qualified declaration). Fail closed if
    not exactly one — never invent a value outside the declared set."""
    hits = [lv for lv in levels
            if lv == candidate
            or (isinstance(lv, str) and lv.startswith(candidate + "("))]
    if len(hits) != 1:
        sys.exit("ERR_KNULL_COLLECT_IV: seed=%r %s candidate %r matched %d of "
                 "declared levels %r (need exactly 1; refusing to invent)"
                 % (seed, iv_name, candidate, len(hits), levels))
    return hits[0]


def _require_member(value, levels, iv_name, seed):
    """Return `value` iff it is an exact member of the declared levels; else
    fail closed (never coerce/round/invent)."""
    if value not in levels:
        sys.exit("ERR_KNULL_COLLECT_IV: seed=%r %s value %r not in declared "
                 "levels %r (refusing to invent)"
                 % (seed, iv_name, value, levels))
    return value


def derive_config(row, iv_levels):
    """Translate one SAP cell record's runner axes (arm/cell/rung/k/seed) into
    a config keyed by the DECLARED IV names with EXACT declared-level values."""
    seed = row.get("seed")  # error context only; log-append stamps seq
    store = _match_level(row["arm"], iv_levels["store"], "store", seed)
    raw_cell, rung = row["cell"], row["rung"]
    base = ("alone-" + rung) if raw_cell == "model-alone" \
        else ("%s-%s" % (raw_cell, rung))
    cell = _match_level(base, iv_levels["cell"], "cell", seed)
    retry_budget = _require_member(row["k"], iv_levels["retry_budget"],
                                   "retry_budget", seed)
    seed_lvl = _require_member(row["seed"], iv_levels["seed"], "seed", seed)
    return {"store": store, "cell": cell,
            "retry_budget": retry_budget, "seed": seed_lvl}


def build_bodies(rows, sidecar, prereg_hash, granularity, iv_levels):
    if granularity == "run":
        return [{
            "event": "run", "phase": "final", "config": {},
            "metrics": {"rows": rows, "sidecar": sidecar},
            "prereg_hash": prereg_hash, "exit": "ok",
        }]
    bodies = []
    for _key, cell_rows in group_cells(rows):
        config = derive_config(cell_rows[0], iv_levels)
        bodies.append({
            "event": "run", "phase": "final", "config": config,
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
                         "CURRENT frozen hash (default tracks the live index)")
    ap.add_argument("--granularity", choices=["cell", "run"], default="cell")
    ap.add_argument("--record-path", default=None,
                    help="frozen record JSON to read /design/independent_vars "
                         "from (default registry/experiments/<experiment>.json)")
    ap.add_argument("--repo-root", default=None,
                    help="repo root for the frozen-index cross-check + default "
                         "record path (default: inferred from this file)")
    args = ap.parse_args()

    rows = load_jsonl(args.run_records)
    if not rows:
        sys.exit("ERR_KNULL_COLLECT_NO_ROWS: %s is empty" % args.run_records)
    with open(args.item_meta, encoding="utf-8") as f:
        sidecar = json.load(f)

    root = args.repo_root or os.path.normpath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     "..", "..", ".."))

    # Cross-check the prereg hash against the frozen index when reachable
    # (fail closed) so a stale hash can never be emitted silently.
    idx_path = os.path.join(root, "registry", "frozen-index.json")
    if os.path.isfile(idx_path):
        with open(idx_path, encoding="utf-8") as f:
            idx = json.load(f)
        want = idx.get(args.experiment)
        if want and want != args.prereg_hash:
            sys.exit("ERR_KNULL_COLLECT_PREREG: --prereg-hash %s != "
                     "frozen-index[%s] %s (refusing; pass the CURRENT frozen "
                     "hash)" % (args.prereg_hash, args.experiment, want))

    record_path = args.record_path or os.path.join(
        root, "registry", "experiments", "%s.json" % args.experiment)
    iv_levels = _read_iv_levels(record_path)

    bodies = build_bodies(rows, sidecar, args.prereg_hash, args.granularity,
                          iv_levels)

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
