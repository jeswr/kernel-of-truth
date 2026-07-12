#!/usr/bin/env python3
"""Merge the two rules-1-b HOST-VALIDITY pilots into ONE gate-readable dir.

The launcher's sec-host-validity-gate (launch_rules1b_parallel.sh --launch)
reads exactly one results-rules1-pilot.json + its records file and floors
acc(A7) >= 0.30 AND acc(A5) >= 0.15 on entailed rows. The A1+A7 pilot ran on
this CPU box (pilot-20260712-cpu); the A5 (R3-1.7B) pilot ran on Modal A10G
via modal_rules1_pilot.py (1.7B fp32 does not fit the 7 GB CPU box). This
script concatenates the row files, cross-checks the pins/certificate fields
agree between the two pilots (fail closed), and writes a merged
results-rules1-pilot.json with per-source provenance. Pilot rows remain
instrument validation ONLY — never final-phase rows.

Usage:
  python3 merge_pilot_hostvalidity.py --cpu <dir> --gpu <dir> --out <dir>
"""

import argparse
import hashlib
import json
import os
import shutil
import sys


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_pilot(d):
    rp = os.path.join(d, "results-rules1-pilot.json")
    with open(rp) as f:
        res = json.load(f)
    if res.get("outcome") != "PILOT-HARNESS-COMPLETE":
        sys.exit("ERR_MERGE: %s outcome %r != PILOT-HARNESS-COMPLETE"
                 % (d, res.get("outcome")))
    rec = os.path.join(d, res["records_file"])
    if sha256_file(rec) != res["records_sha256"]:
        sys.exit("ERR_MERGE: records sha mismatch in %s" % d)
    rows = [json.loads(l) for l in open(rec) if l.strip()]
    return res, rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cpu", required=True, help="A1+A7 CPU pilot dir")
    ap.add_argument("--gpu", required=True, help="A5 Modal GPU pilot dir")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    cpu_res, cpu_rows = load_pilot(a.cpu)
    gpu_res, gpu_rows = load_pilot(a.gpu)

    # fail-closed cross-checks: same frozen inputs, models, shuffle, cert
    for key in ("pins", "models", "certificate_precondition", "k_retry"):
        if cpu_res[key] != gpu_res[key]:
            sys.exit("ERR_MERGE: %r differs between the two pilots" % key)
    if cpu_res["shuffle"]["map_sha256"] != gpu_res["shuffle"]["map_sha256"]:
        sys.exit("ERR_MERGE: shuffle map sha differs")
    dup = ({(r["arm"], r["seed"]) for r in cpu_rows}
           & {(r["arm"], r["seed"]) for r in gpu_rows})
    if dup:
        sys.exit("ERR_MERGE: overlapping (arm, seed) cells %s" % sorted(dup))

    os.makedirs(a.out, exist_ok=True)
    merged_rows = cpu_rows + gpu_rows  # deterministic: CPU pilot then GPU
    rec_path = os.path.join(a.out, "run-records-rules1-pilot.jsonl")
    with open(rec_path, "w") as f:
        for r in merged_rows:
            f.write(json.dumps(r, sort_keys=True, separators=(",", ":")))
            f.write("\n")

    arms = sorted({r["arm"] for r in merged_rows})
    merged = dict(cpu_res)
    merged.update({
        "arms": arms,
        # older pilot results (pre --cells field) derive cells from arms x seeds
        "cells": sorted(set(cpu_res.get("cells") or
                            ["%s:%d" % (a, s) for a in cpu_res["arms"]
                             for s in cpu_res["seeds"]])
                        | set(gpu_res.get("cells") or
                              ["%s:%d" % (a, s) for a in gpu_res["arms"]
                               for s in gpu_res["seeds"]])),
        "device": "merged (see merge_sources)",
        "n_rows": len(merged_rows),
        "n_covered": cpu_res["n_covered"],
        "records_file": os.path.basename(rec_path),
        "records_sha256": sha256_file(rec_path),
        "merge_sources": {
            "cpu_pilot": {"dir": os.path.basename(os.path.normpath(a.cpu)),
                          "arms": cpu_res["arms"], "device": cpu_res["device"],
                          "dtype": cpu_res["pilot"]["dtype"],
                          "records_sha256": cpu_res["records_sha256"],
                          "n_rows": len(cpu_rows)},
            "gpu_pilot": {"dir": os.path.basename(os.path.normpath(a.gpu)),
                          "arms": gpu_res["arms"], "device": gpu_res["device"],
                          "dtype": gpu_res["pilot"]["dtype"],
                          "records_sha256": gpu_res["records_sha256"],
                          "n_rows": len(gpu_rows)},
            "note": "host-validity pilot merge (A1+A7 CPU + A5 Modal A10G): "
                    "rows concatenated verbatim, disjoint (arm, seed) cells "
                    "asserted; pins/models/shuffle/certificate cross-checked "
                    "equal. Instrument validation ONLY — never final-phase "
                    "rows."},
    })
    # decision sha over the merged decision rows (engine_us stripped),
    # mirroring the runner's comparator convention
    dec = [{k: v for k, v in r.items() if k != "engine_us"}
           for r in merged_rows]
    merged["decision_sha256"] = hashlib.sha256(json.dumps(
        dec, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    with open(os.path.join(a.out, "results-rules1-pilot.json"), "w") as f:
        json.dump(merged, f, indent=2, sort_keys=True)
        f.write("\n")
    shutil.copy2(os.path.join(a.cpu, "shuffle-map-rules1.json"),
                 os.path.join(a.out, "shuffle-map-rules1.json"))

    for arm in ("A1", "A7", "A5"):
        ent = [r for r in merged_rows
               if r["arm"] == arm and r["cell"] == "entailed"]
        if ent:
            acc = sum(r["item_correct_ext"] for r in ent) / len(ent)
            print("merged pilot acc(%s) = %.4f (n=%d entailed)"
                  % (arm, acc, len(ent)))
    print("wrote %s (%d rows, sha %s)"
          % (rec_path, len(merged_rows), merged["records_sha256"][:12]))


if __name__ == "__main__":
    main()
