#!/usr/bin/env python3
"""Merge DISJOINT rules-1-b slice run-records into ONE canonical
run-records-rules1b.jsonl (parallel 4-account Modal launch, maintainer
directive 2026-07-12; orchestrated by launch_rules1b_parallel.sh).

Each slice is one modal_rules1.py --cells run (or a local --mock run in the
launcher's validation path). This script:

  1. verifies every slice completed (results-rules1*.json outcome
     *-HARNESS-COMPLETE; RUNNER_EXIT rc=0 when the Modal sidecar is present;
     recomputed records sha == the slice's recorded records_sha256);
  2. verifies all slices agree on pins and on the c1 derangement
     (shuffle-map sha identical — one Sattolo map for the whole campaign);
  3. merges rows DEDUP-SAFELY: the row key is (item_id, arm, rung, seed,
     cell). Re-collected byte-equivalent duplicates (identical decision
     payload, i.e. identical after stripping the volatile engine_us timing)
     collapse to the first-seen row; the SAME key with a DIFFERENT decision
     payload is a hard ERR_MERGE_CONFLICT (never silently resolved);
  4. fails closed on any cell="timeout" row, on missing grid cells, on
     unexpected cells, and on wrong per-cell row counts (858 entailed / 100
     control full; 60 / 10 mock — read from rules1-manifest.json, never
     hard-coded);
  5. writes rows in a DETERMINISTIC canonical order — sort key (arm, rung,
     seed, cell, item_id), each line json.dumps(row, sort_keys=True), the
     exact RowEmitter serialization — so the merged bytes are a pure
     function of the row set, independent of slice assignment or arrival
     order;
  6. writes merge-manifest-rules1b*.json: per-slice provenance (source dir,
     cells, records/decision shas, provenance-modal.json sha) plus a
     per-cell -> slice provenance map for verdict-gen/audit, and the merged
     records sha + canonical decision-payload sha.

REPEAT-GATE NOTE (frozen /gates/repeat_byte_identical): the runner's
decision_sha256 is computed over rows in EMISSION order, so byte-identical
repeats must be compared PER SLICE (same --cells, same account class) using
the slices' own decision_sha256 values, or at merge level using this
script's decision_sha256_canonical (emission-order-free). Both are recorded.

$0, stdlib-only, no network. Exit 0 == MERGE OK.
"""

from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_RULES1 = os.path.normpath(os.path.join(_HERE, ".."))

ROW_KEY = ("item_id", "arm", "rung", "seed", "cell")
ENGINE_ARMS = ("A3", "A7")  # the arms that emit E5 control rows
OK_OUTCOMES = {"FULL": "HARNESS-COMPLETE", "MOCK": "MOCK-HARNESS-COMPLETE"}


def fail(msg):
    raise SystemExit(msg)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def decision_payload(row):
    """The runner's decision-sha recipe: strip the volatile engine_us
    wall-clock timing (rules1_runner.py, decision_sha_note)."""
    return {k: v for k, v in row.items() if k != "engine_us"}


def canon(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def load_slice(idx, d):
    """Read one slice output dir (a <stamp>-modal unpack or a local runner
    out dir); return (rows, meta). Fail closed on anything off-contract."""
    res_cands = sorted(glob.glob(os.path.join(d, "results-rules1*.json")))
    if len(res_cands) != 1:
        fail("ERR_MERGE_RESULTS: slice %d (%s): want exactly one "
             "results-rules1*.json, found %s" % (idx, d, res_cands or "none"))
    with open(res_cands[0], encoding="utf-8") as f:
        results = json.load(f)
    mode = results.get("mode")
    if mode not in OK_OUTCOMES:
        fail("ERR_MERGE_MODE: slice %d (%s): mode %r is not mergeable "
             "(PILOT rows are never final-phase rows)" % (idx, d, mode))
    if results.get("outcome") != OK_OUTCOMES[mode]:
        fail("ERR_MERGE_OUTCOME: slice %d (%s): outcome %r != %s"
             % (idx, d, results.get("outcome"), OK_OUTCOMES[mode]))

    exit_path = os.path.join(d, "RUNNER_EXIT")
    if os.path.exists(exit_path):  # Modal sidecar (absent on local mock runs)
        rc = open(exit_path).read().strip()
        if rc != "rc=0":
            fail("ERR_MERGE_RC: slice %d (%s): RUNNER_EXIT %r != rc=0"
                 % (idx, d, rc))

    rec_path = os.path.join(d, results["records_file"])
    if not os.path.exists(rec_path):
        fail("ERR_MERGE_RECORDS: slice %d (%s): records file %s missing"
             % (idx, d, results["records_file"]))
    got_sha = sha256_file(rec_path)
    if got_sha != results["records_sha256"]:
        fail("ERR_MERGE_SHA: slice %d (%s): recomputed records sha %s != "
             "recorded %s" % (idx, d, got_sha, results["records_sha256"]))

    rows = []
    with open(rec_path, encoding="utf-8") as f:
        for ln, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            missing = [k for k in ROW_KEY if k not in row]
            if missing:
                fail("ERR_MERGE_ROW: slice %d %s:%d: row missing %s"
                     % (idx, results["records_file"], ln, missing))
            if row["cell"] == "timeout":
                fail("ERR_MERGE_TIMEOUT: slice %d (%s) contains a "
                     "cell='timeout' instrument-event row — the slice run "
                     "aborted; re-run that slice before merging" % (idx, d))
            rows.append(row)

    shuffle_path = os.path.join(d, "shuffle-map-rules1.json")
    if not os.path.exists(shuffle_path):
        fail("ERR_MERGE_SHUFFLE: slice %d (%s): shuffle-map-rules1.json "
             "missing" % (idx, d))
    with open(shuffle_path, encoding="utf-8") as f:
        shuffle_sha = json.load(f)["sha256_of_map"]

    prov_path = os.path.join(d, "provenance-modal.json")
    meta = {
        "slice": idx,
        "dir": os.path.relpath(d),
        "records_file": results["records_file"],
        "records_sha256": results["records_sha256"],
        "decision_sha256_emission_order": results["decision_sha256"],
        "mode": mode,
        "cells": results.get("cells",
                             ["%s:%d" % (a, s) for a in results["arms"]
                              for s in results["seeds"]]),
        "n_rows": len(rows),
        "shuffle_map_sha256": shuffle_sha,
        "pins": results["pins"],
        "provenance_modal_sha256":
            sha256_file(prov_path) if os.path.exists(prov_path) else None,
    }
    return rows, meta


def expected_grid(inputs_dir, mode):
    """(arms, seeds, n_covered, n_control) from the pinned manifest."""
    with open(os.path.join(inputs_dir, "rules1-manifest.json"),
              encoding="utf-8") as f:
        man = json.load(f)
    dc = man["design_constants_from_frozen_record"]
    if mode == "MOCK":
        return (dc["arms_built_here"], man["mock"]["seeds"],
                man["mock"]["n_covered"], man["mock"]["n_control"])
    return (dc["arms_built_here"], dc["seeds"],
            dc["n_covered_entailed"], dc["n_control"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slices", nargs="+", required=True,
                    help="slice output dirs (each one modal_rules1.py "
                         "--cells unpack, or a local --mock out dir)")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--inputs-dir",
                    default=os.path.join(_RULES1, "inputs"),
                    help="pinned rules1-manifest.json location (grid + "
                         "count expectations; never hard-coded)")
    args = ap.parse_args()

    slices = []
    all_rows = []
    for idx, d in enumerate(args.slices, 1):
        rows, meta = load_slice(idx, d)
        slices.append(meta)
        for row in rows:
            all_rows.append((idx, row))

    # cross-slice agreement: one mode, one pin set, one derangement
    modes = {m["mode"] for m in slices}
    if len(modes) != 1:
        fail("ERR_MERGE_MODE_MIX: slices disagree on mode: %s" % sorted(modes))
    mode = modes.pop()
    if len({canon(m["pins"]) for m in slices}) != 1:
        fail("ERR_MERGE_PINS: slices disagree on pins — different harness "
             "bytes were staged; nothing here is mergeable")
    if len({m["shuffle_map_sha256"] for m in slices}) != 1:
        fail("ERR_MERGE_SHUFFLE: slices disagree on the c1 derangement map "
             "sha — the campaign did not share one Sattolo map")

    # dedup-safe key merge with per-cell provenance
    by_key = {}          # key tuple -> (slice_idx, row)
    cell_prov = {}       # "arm:seed/cell" -> slice idx
    n_dup = 0
    for idx, row in all_rows:
        key = tuple(row[k] for k in ROW_KEY)
        if key in by_key:
            prev_idx, prev_row = by_key[key]
            if canon(decision_payload(prev_row)) == canon(decision_payload(row)):
                n_dup += 1  # re-collected duplicate; keep first (engine_us volatile)
                continue
            fail("ERR_MERGE_CONFLICT: key %s appears in slice %d and slice "
                 "%d with DIFFERENT decision payloads — slices were not "
                 "disjoint/deterministic; do not merge" % (key, prev_idx, idx))
        by_key[key] = (idx, row)
        ckey = "%s:%s/%s" % (row["arm"], row["seed"], row["cell"])
        prev = cell_prov.get(ckey)
        if prev is not None and prev != idx:
            fail("ERR_MERGE_SPLIT_CELL: cell %s has rows in slice %d and "
                 "slice %d — a cell is the atomic slice unit" % (ckey, prev, idx))
        cell_prov[ckey] = idx

    # completeness vs the pinned grid
    arms, seeds, n_cov, n_ctl = expected_grid(args.inputs_dir, mode)
    expected = {}
    for a in arms:
        for s in seeds:
            expected["%s:%s/entailed" % (a, s)] = n_cov
            if a in ENGINE_ARMS:
                expected["%s:%s/control" % (a, s)] = n_ctl
    counts = {}
    for (item_id, a, rung, s, cell), _v in ((k, v) for k, v in by_key.items()):
        counts["%s:%s/%s" % (a, s, cell)] = \
            counts.get("%s:%s/%s" % (a, s, cell), 0) + 1
    missing = sorted(set(expected) - set(counts))
    extra = sorted(set(counts) - set(expected))
    wrong = sorted(k for k in set(expected) & set(counts)
                   if counts[k] != expected[k])
    if missing or extra or wrong:
        fail("ERR_MERGE_GRID: missing cells %s; unexpected cells %s; wrong "
             "counts %s" % (missing, extra,
                            {k: (counts[k], expected[k]) for k in wrong}))

    # canonical deterministic order + canonical bytes (RowEmitter recipe)
    merged = sorted(by_key.items(),
                    key=lambda kv: (kv[0][1], kv[0][2], kv[0][3],
                                    kv[0][4], kv[0][0]))
    os.makedirs(args.out_dir, exist_ok=True)
    suffix = "-mock" if mode == "MOCK" else ""
    out_path = os.path.join(args.out_dir,
                            "run-records-rules1b%s.jsonl" % suffix)
    with open(out_path, "w", encoding="utf-8") as f:
        for _key, (_idx, row) in merged:
            f.write(json.dumps(row, sort_keys=True) + "\n")
    merged_sha = sha256_file(out_path)
    decision_sha = hashlib.sha256(canon(
        [decision_payload(row) for _k, (_i, row) in merged]
    ).encode()).hexdigest()

    manifest = {
        "merge_tool": "poc/rules-1/modal/merge_rules1b_slices.py",
        "mode": mode,
        "slices": [{k: v for k, v in m.items() if k != "pins"}
                   for m in slices],
        "pins": slices[0]["pins"],
        "shuffle_map_sha256": slices[0]["shuffle_map_sha256"],
        "cell_provenance": {k: {"slice": v, "dir": slices[v - 1]["dir"]}
                            for k, v in sorted(cell_prov.items())},
        "n_rows_merged": len(merged),
        "n_duplicate_rows_collapsed": n_dup,
        "merged_records_file": os.path.basename(out_path),
        "merged_records_sha256": merged_sha,
        "decision_sha256_canonical": decision_sha,
        "decision_sha_note":
            "canonical (emission-order-free) decision-payload sha over the "
            "merged rows with the volatile engine_us stripped, in the sort "
            "order (arm, rung, seed, cell, item_id). For the frozen "
            "repeat_byte_identical gate compare EITHER per-slice "
            "decision_sha256_emission_order values across byte-identical "
            "slice repeats, OR two of THESE canonical shas across full "
            "parallel repeats.",
        "order_note": "rows sorted by (arm, rung, seed, cell, item_id); "
                      "each line json.dumps(row, sort_keys=True) — the "
                      "RowEmitter serialization; merged bytes are a pure "
                      "function of the row set.",
    }
    man_path = os.path.join(args.out_dir,
                            "merge-manifest-rules1b%s.json" % suffix)
    with open(man_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)
        f.write("\n")

    print("MERGE OK: %d rows (%d duplicates collapsed) from %d slices -> %s "
          "(sha %s…)" % (len(merged), n_dup, len(slices),
                         out_path, merged_sha[:12]))
    print("merge manifest: %s" % man_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
