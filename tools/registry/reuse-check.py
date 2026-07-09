#!/usr/bin/env python3
"""reuse-check.py — GPU-result artifact ledger builder + PRE-SPEND reuse gate.

Mechanism defined in docs/next/resource-optimization-plan.md §3 (bead
kernel-of-truth-utq; Fable design deliverable, 2026-07-09). This tool is a NEW
standalone surface: it does not modify the frozen honesty machinery
(prereg-freeze / log-append / verdict-gen are untouched). Wiring it INTO
prereg-freeze as a hard lint is delta D9 and is maintainer-gated (P2 §7 item 3,
same precedent as the D7 assumption-register lint).

Subcommands
-----------
build
    Regenerate registry/artifact-ledger.jsonl (schema kot-artifact/1) as a pure
    function of results-log/*.jsonl + registry/verdicts/. One line per logged
    final-phase run row: producer experiment, config cell (arm/rung/seed/...),
    per-item metric fields logged, item counts, observed pins, and whether the
    producer's data is already unblinded (a verdict exists). Deterministic:
    sorted by (experiment, seq).

check
    The PRE-SPEND GATE. Query the ledger for already-logged cells matching a
    proposed spend, either by explicit filters (--arm/--rung/--corpus/...) or
    by a draft record (--record registry/experiments/<id>.json, which expands
    the record's arm x rung grid and reports per-cell coverage). A non-empty
    result means: STOP — report to the coordinator/Fable before launching; the
    run may shrink to the uncovered cells, or the question may be answerable as
    a free (exploratory) re-analysis of logged data. Exit code 3 when --gate is
    set and any match is found, so run-scripts can fail closed.

Conventions: stdlib only; fail closed with ERR_* codes; no silent fallbacks.
"""

import argparse
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RESULTS_DIR = os.path.join(ROOT, "results-log")
VERDICTS_DIR = os.path.join(ROOT, "registry", "verdicts")
LEDGER_PATH = os.path.join(ROOT, "registry", "artifact-ledger.jsonl")

SCHEMA = "kot-artifact/1"

# config keys that identify a cell (order matters for display only)
CELL_KEYS = ("arm", "rung", "seed", "retry_budget", "escalation_budget")


def _die(code, msg):
    sys.stderr.write("%s: %s\n" % (code, msg))
    sys.exit(2)


def _load_jsonl(path):
    out = []
    with open(path, "r", encoding="utf-8") as fh:
        for i, line in enumerate(fh):
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError as e:
                _die("ERR_LEDGER_PARSE", "%s line %d: %s" % (path, i + 1, e))
    return out


def build(args):
    if not os.path.isdir(RESULTS_DIR):
        _die("ERR_NO_RESULTS_LOG", RESULTS_DIR)
    verdicts = {
        os.path.splitext(os.path.basename(p))[0]
        for p in glob.glob(os.path.join(VERDICTS_DIR, "*.json"))
    }
    rows = []
    for path in sorted(glob.glob(os.path.join(RESULTS_DIR, "*.jsonl"))):
        exp = os.path.splitext(os.path.basename(path))[0]
        for rec in _load_jsonl(path):
            phase = rec.get("phase")
            if phase != "final" and not args.all:
                continue
            metrics = rec.get("metrics") or {}
            config = rec.get("config") or {}
            # per-item fields: list-valued metrics are the re-analysable assets
            per_item = sorted(
                k for k, v in metrics.items() if isinstance(v, list)
            )
            n_items = None
            for k in ("item_correct", "record_caught"):
                if isinstance(metrics.get(k), list):
                    n_items = len(metrics[k])
                    break
            pins = rec.get("pins_observed") or {}
            entry = {
                "schema_version": SCHEMA,
                "experiment": exp,
                "log_path": os.path.relpath(path, ROOT),
                "seq": rec.get("seq"),
                "phase": phase,
                "event": rec.get("event"),
                "config": config,
                "n_items": n_items,
                "metrics_logged": sorted(metrics.keys()),
                "per_item_fields": per_item,
                "pins": {
                    "encoder_hash": pins.get("encoder_hash"),
                    "corpus_hashes": pins.get("corpus_hashes"),
                    "model_revisions": pins.get("model_revisions"),
                    "other_pins": sorted(
                        k
                        for k in pins
                        if k
                        not in ("encoder_hash", "corpus_hashes", "model_revisions")
                    ),
                },
                "prereg_hash": rec.get("prereg_hash"),
                "unblinded": exp in verdicts,
                "ts": rec.get("ts"),
            }
            rows.append(entry)
    rows.sort(key=lambda r: (r["experiment"], r["seq"] if r["seq"] is not None else -1))
    with open(LEDGER_PATH, "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, sort_keys=True) + "\n")
    print(
        "artifact-ledger: wrote %d rows from %d experiments -> %s"
        % (len(rows), len({r["experiment"] for r in rows}), os.path.relpath(LEDGER_PATH, ROOT))
    )
    return 0


def _cell_str(cfg):
    return " ".join(
        "%s=%s" % (k, cfg[k]) for k in CELL_KEYS if k in cfg and cfg[k] is not None
    )


def _match(entry, args):
    cfg = entry.get("config") or {}
    if args.arm and cfg.get("arm") != args.arm:
        return False
    if args.rung and cfg.get("rung") != args.rung:
        return False
    if args.seed is not None and cfg.get("seed") != args.seed:
        return False
    if args.producer and entry.get("experiment") != args.producer:
        return False
    if args.metric and args.metric not in entry.get("metrics_logged", []):
        return False
    if args.corpus:
        ch = (entry.get("pins") or {}).get("corpus_hashes") or {}
        if args.corpus not in ch and args.corpus not in ch.values():
            return False
    if args.model_revision:
        mr = (entry.get("pins") or {}).get("model_revisions") or {}
        if args.model_revision not in mr and args.model_revision not in [
            str(v) for v in mr.values()
        ]:
            return False
    return True


def _report_matches(matches):
    by_cell = {}
    for m in matches:
        key = (m["experiment"], _cell_str(m.get("config") or {}))
        by_cell.setdefault(key, []).append(m)
    for (exp, cell), ms in sorted(by_cell.items()):
        m0 = ms[0]
        print(
            "  MATCH producer=%s cell[%s] rows=%d n_items=%s per_item=%s unblinded=%s log=%s"
            % (
                exp,
                cell,
                len(ms),
                m0.get("n_items"),
                ",".join(m0.get("per_item_fields") or []) or "-",
                m0.get("unblinded"),
                m0.get("log_path"),
            )
        )


def check(args):
    if not os.path.exists(LEDGER_PATH):
        _die("ERR_NO_LEDGER", "run `reuse-check.py build` first: " + LEDGER_PATH)
    ledger = _load_jsonl(LEDGER_PATH)
    matches = []

    if args.record:
        rec = json.load(open(args.record, "r", encoding="utf-8"))
        design = rec.get("design") or {}
        ivs = {iv["name"]: iv["levels"] for iv in design.get("independent_vars", [])}
        arms = ivs.get("arm", [])
        rungs = ivs.get("rung", design.get("scale_rungs", []))
        deps = rec.get("depends_on", [])
        print(
            "pre-spend reuse check for record %s (%d arms x %d rungs; depends_on=%s)"
            % (args.record, len(arms), len(rungs), ",".join(deps))
        )
        covered, uncovered = 0, 0
        for arm in arms:
            for rung in rungs:
                cell = [
                    e
                    for e in ledger
                    if (e.get("config") or {}).get("arm") == arm
                    and (e.get("config") or {}).get("rung") == rung
                ]
                if cell:
                    covered += 1
                    matches.extend(cell)
                    producers = sorted({e["experiment"] for e in cell})
                    print(
                        "  LOGGED   arm=%-42s rung=%-3s rows=%3d producers=%s"
                        % (arm, rung, len(cell), ",".join(producers))
                    )
                else:
                    uncovered += 1
        print(
            "cells with same-name logged data: %d; cells with none: %d" % (covered, uncovered)
        )
        if covered:
            print(
                "NOTE: name-level matches only. Reuse is licensed ONLY under RC-1..RC-6"
                " (docs/next/resource-optimization-plan.md §3.4): exact pin identity"
                " (corpus/slice hash, model revision, arm config, seeds) must be"
                " verified against each producer row's pins, and already-unblinded"
                " rows carry the RC-4 comparator-only restriction."
            )
    else:
        matches = [e for e in ledger if _match(e, args)]
        if matches:
            print("pre-spend reuse check: %d matching logged rows" % len(matches))
            _report_matches(matches)
        else:
            print("pre-spend reuse check: no matching logged cells")

    if matches and args.gate:
        print(
            "GATE: matching logged results exist — STOP and record a Fable/coordinator"
            " reuse decision in the run-log before any spend (exit 3)."
        )
        return 3
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build", help="regenerate registry/artifact-ledger.jsonl")
    b.add_argument(
        "--all",
        action="store_true",
        help="include non-final phases (exploratory rows are quarantined/uncitable; "
        "listed only so re-analysis work is visible)",
    )
    b.set_defaults(func=build)

    c = sub.add_parser("check", help="query the ledger before authorising a spend")
    c.add_argument("--record", help="a registry/experiments/<id>.json to expand and check")
    c.add_argument("--arm")
    c.add_argument("--rung")
    c.add_argument("--seed", type=int)
    c.add_argument("--corpus", help="corpus name or sha256 pin")
    c.add_argument("--model-revision", help="model name or revision pin")
    c.add_argument("--producer", help="restrict to one producer experiment id")
    c.add_argument("--metric", help="require this metric key to be logged")
    c.add_argument(
        "--gate",
        action="store_true",
        help="exit 3 when matches are found (fail-closed pre-spend gate for run-scripts)",
    )
    c.set_defaults(func=check)

    args = ap.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
