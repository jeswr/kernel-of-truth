#!/usr/bin/env python3
"""build-dxif — deterministic assembly of the d-xif corpus (P10 sections 3-4)
from a completed modal_f2_xif.py pilot run.

    python3 data/d-xif/build-dxif.py --from poc/f2/results-incoming/<stamp>-modal-xif

What it does (all fail-closed, no LLM in the loop, no number trusted):
  1. copies the per-output labelled records (xif-outputs-r{1,2}.jsonl), the
     runner's summary (results-xif.json), the Modal provenance sidecar and
     the run log into this directory;
  2. RECOMPUTES the extraction-failure gate arithmetic and the IF-1 fork
     statistics FROM THE PER-OUTPUT RECORDS (re-deriving parse flags from
     gen_text with the pinned IFA-PARSE/1 / GOLD-ANN/1 rules, re-checking
     stored flags) and fails closed (ERR_DXIF_MISMATCH) if anything disagrees
     with the runner's summary — the committed gate.json / if1-fork.json are
     the RE-DERIVED numbers;
  3. copies the builder bytes (poc/f2/runner/xif_runner.py,
     poc/modal/modal_f2_xif.py) into builder/ so the corpus is
     self-describing under kot-corpus-hash/1 (d-qa / d-ext discipline);
  4. writes manifest.json (spec kot-dxif/1) with per-file sha256s, the model
     revision pins used, and the source run stamp.

Determinism: this script adds no wall-clock or randomness to any hashed
byte except the source-run identifiers already fixed by the pilot run; a
re-run over the same results directory reproduces every generated file
byte-identically.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "poc", "f2", "runner"))
import xif_runner as xr  # the pinned gate/fork arithmetic + parser rules


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def die(msg):
    raise SystemExit("ERR_DXIF_MISMATCH: %s" % msg)


def approx(a, b, tol=1e-12):
    if isinstance(a, float) or isinstance(b, float):
        return abs(float(a) - float(b)) <= tol
    return a == b


def deep_check(got, want, path="$"):
    if isinstance(want, dict):
        for k, v in want.items():
            if k not in got:
                die("missing %s.%s" % (path, k))
            deep_check(got[k], v, "%s.%s" % (path, k))
    elif isinstance(want, list):
        if len(got) != len(want):
            die("length %s" % path)
        for i, v in enumerate(want):
            deep_check(got[i], v, "%s[%d]" % (path, i))
    else:
        if not approx(got, want):
            die("%s: recomputed %r != runner %r" % (path, got, want))


def load_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="src", required=True,
                    help="results-incoming/<stamp>-modal-xif directory")
    args = ap.parse_args()
    src = os.path.abspath(args.src)

    with open(os.path.join(src, "results-xif.json"), encoding="utf-8") as f:
        summary = json.load(f)
    if summary.get("mode") != "REAL":
        die("refusing to build d-xif from a %r run — the labelled set must "
            "be real model outputs (P10 section 4)" % summary.get("mode"))

    os.makedirs(os.path.join(HERE, "outputs"), exist_ok=True)
    os.makedirs(os.path.join(HERE, "builder"), exist_ok=True)

    # 1. copy the raw artefacts byte-identically
    copies = {
        "outputs/r1.jsonl": os.path.join(src, "xif-outputs-r1.jsonl"),
        "outputs/r2.jsonl": os.path.join(src, "xif-outputs-r2.jsonl"),
        "results-xif.json": os.path.join(src, "results-xif.json"),
        "provenance-modal.json": os.path.join(src, "provenance-modal.json"),
        "run-log.txt": os.path.join(src, "kot-e2-run.log"),
        "builder/xif_runner.py": os.path.join(
            REPO, "poc", "f2", "runner", "xif_runner.py"),
        "builder/modal_f2_xif.py": os.path.join(
            REPO, "poc", "modal", "modal_f2_xif.py"),
        "builder/build-dxif.py": os.path.abspath(__file__),
    }
    for rel, spath in copies.items():
        dpath = os.path.join(HERE, rel)
        if os.path.abspath(spath) != os.path.abspath(dpath):
            shutil.copyfile(spath, dpath)

    # 2. recompute gate + IF-1 from the per-output records, fail closed
    gate, if1 = {}, {}
    for rung, rel in (("R1", "outputs/r1.jsonl"), ("R2", "outputs/r2.jsonl")):
        outputs = load_jsonl(os.path.join(HERE, rel))
        # re-derive the parse/annotation flags from the raw gen_text with the
        # pinned rules — the stored flags must be reproducible
        items_by_id = {}
        for ipath, key in (("d-qa/items/covered.jsonl", "covered"),
                           ("d-qa/items/control.jsonl", "control")):
            for it in load_jsonl(os.path.join(REPO, "data", ipath)):
                items_by_id[it["id"]] = it
        for o in outputs:
            it = items_by_id.get(o["id"]) or die("unknown item id %s" % o["id"])
            if xr.ifa_parse(it, o["gen_text"]) != o["ifa_parsed"]:
                die("%s %s: stored ifa_parsed not reproducible" % (rung, o["id"]))
            if xr.gold_annotate(it, o["gen_text"]) != o["gold_annotation"]:
                die("%s %s: stored gold_annotation not reproducible" % (rung, o["id"]))
        g = xr.gate_stats(outputs)
        s = xr.if1_stats(outputs)
        deep_check(g, summary["gate"][rung], "gate.%s" % rung)
        deep_check(s, summary["if1"][rung], "if1.%s" % rung)
        gate[rung], if1[rung] = g, s
    fork = xr.fork_decision(if1)
    deep_check(fork, summary["if1_fork"], "if1_fork")

    with open(os.path.join(HERE, "gate.json"), "w", encoding="utf-8") as f:
        json.dump({"spec": "kot-dxif/1", "gate": gate,
                   "recomputed_by": "build-dxif.py (fail-closed against the "
                                    "runner summary and the raw outputs)"},
                  f, indent=2, sort_keys=True)
        f.write("\n")
    with open(os.path.join(HERE, "if1-fork.json"), "w", encoding="utf-8") as f:
        json.dump({"spec": "kot-dxif/1", "if1": if1, "fork": fork,
                   "recomputed_by": "build-dxif.py (fail-closed against the "
                                    "runner summary and the raw outputs)"},
                  f, indent=2, sort_keys=True)
        f.write("\n")

    # 4. manifest
    manifest = {
        "spec": "kot-dxif/1",
        "what": "P10 held-out labelled extraction set (d-xif) + IF-1 fork "
                "pilot record for F2 (and, per P10, the same interface "
                "governs E9): >=300 real model outputs per rung under the "
                "IF-C constrained surface AND unconstrained greedy free "
                "decode from identical prompts, extraction success/failure "
                "labelled mechanically",
        "source_run": os.path.basename(src),
        "models": summary["models"],
        "constants": summary["constants"],
        "date_utc": summary["date"],
        "files": {rel: sha256_file(os.path.join(HERE, rel))
                  for rel in sorted(list(copies) + ["gate.json", "if1-fork.json"])},
        "n_outputs": {r: {"covered": sum(1 for o in load_jsonl(
                              os.path.join(HERE, "outputs/%s.jsonl" % r.lower()))
                              if o["slice"] == "covered"),
                          "total": len(load_jsonl(
                              os.path.join(HERE, "outputs/%s.jsonl" % r.lower())))}
                      for r in ("R1", "R2")},
        "gate_pass": {r: gate[r]["gate_pass"] for r in gate},
        "fork_choice": fork["choice"],
    }
    with open(os.path.join(HERE, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)
        f.write("\n")

    print("d-xif assembled: gate_pass=%s fork=%s (n: %s)"
          % (manifest["gate_pass"], fork["choice"], manifest["n_outputs"]))


if __name__ == "__main__":
    main()
