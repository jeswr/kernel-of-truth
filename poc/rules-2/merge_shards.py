#!/usr/bin/env python3
"""RULES-2 shard merge (REWORK-2, cross-vendor prereg review item 9 + the
standing parallel-launch directive; PROPOSED-ASM-1459 merge protocol).

The RULES-2 campaign runs as INDEPENDENT Modal jobs (one per FT arm x seed
x rung; one per B4 seed; one per eval-only arm) so that no single job
approaches the 12 h Modal function timeout and jobs can run concurrently
across containers and across Modal accounts. Each job writes
run-records-rules2-<tag>[-mock].jsonl + results-rules2-<tag>[-mock].json
via rules2_runner.py --arms/--seeds/--shard-tag.

This tool reconstructs the CANONICAL pair the pinned analysis
(analysis/rules_2.py) consumes:

  run-records-rules2[-mock].jsonl   all shard rows, canonically ordered
  results-rules2[-mock].json        merged results (ledgers/repeat united)

FAIL-CLOSED assertions (any failure => no merged output):
  * every shard carries IDENTICAL pins, certificate precondition, c8 gate,
    prompt-surface shas (S-out + gap23), mode, canonical_first_seed,
    strata counts and USD table — shards from mismatched harness bytes or
    corpora can NEVER be pooled;
  * ledger/repeat keys are pairwise DISJOINT across shards and row-level
    (arm, rung, seed, cell, item_id) tuples are globally unique — a cell
    ran exactly once;
  * per FT arm/rung present: the union of seeds equals the design's FT-seed
    set, and the canonical first seed's strata + repeat cells are present —
    a sharded launch covers exactly the cells a monolithic one would.

Row order in the merged records file is the CANONICAL sort
(arm, rung, seed, cell, item_id) — disclosed in merge_note; the analysis is
order-independent and the per-shard record shas are preserved in the
shards ledger. This module states NO feasibility conclusion.

Usage:
  python3 merge_shards.py --out-dir <merged-dir> <shard-dir> [<shard-dir> ...]
"""

from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os

ARM_ORDER = {a: i for i, a in enumerate(
    ("B0", "B1", "B2", "B3", "B4", "B5", "c1p"))}
CELL_ORDER = {c: i for i, c in enumerate(
    ("entailed", "entailed23", "control", "s_mem", "s_held", "stated",
     "refusal_train", "timeout"))}

# results fields that MUST be byte-identical across every shard
INVARIANT_FIELDS = (
    "experiment", "mode", "outcome", "outcome_note", "device",
    "gpu_class_assumed_for_usd", "n_sout_covered", "n_sout_control",
    "strata_eval_counts", "usd_per_hour_table",
    "sout_prompt_surface_sha256", "gap23_prompt_surface_sha256",
    "prompt_surface_note", "efficiency_constants", "pins", "pins_verified",
    "certificate_precondition", "c8_gate", "corpus_manifest_mode",
    "canonical_first_seed", "ft_seeds_design", "repeat_note",
    "eval_ledger_note", "shard_note",
)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_shard(d):
    res_files = sorted(glob.glob(os.path.join(d, "results-rules2*.json")))
    if len(res_files) != 1:
        raise SystemExit("ERR_MERGE: %s has %d results-rules2*.json files "
                         "(need exactly 1)" % (d, len(res_files)))
    res = json.load(open(res_files[0]))
    rec_path = os.path.join(d, res["records_file"])
    if not os.path.exists(rec_path):
        raise SystemExit("ERR_MERGE: %s missing records file %s"
                         % (d, res["records_file"]))
    if sha256_file(rec_path) != res["records_sha256"]:
        raise SystemExit("ERR_MERGE: %s records sha mismatch vs its own "
                         "results json" % d)
    rows = [json.loads(x) for x in open(rec_path)]
    if len(rows) != res["n_rows"]:
        raise SystemExit("ERR_MERGE: %s n_rows %d != %d rows on disk"
                         % (d, res["n_rows"], len(rows)))
    return res, rows


def row_key(r):
    return (ARM_ORDER.get(r.get("arm"), 99), str(r.get("rung")),
            int(r.get("seed", -1)),
            CELL_ORDER.get(r.get("cell"), 99), str(r.get("item_id")))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("shard_dirs", nargs="+")
    args = ap.parse_args()

    shards = [(d,) + load_shard(d) for d in args.shard_dirs]
    res0 = shards[0][1]

    # 1) invariants byte-identical across shards
    for d, res, _rows in shards[1:]:
        for f in INVARIANT_FIELDS:
            if json.dumps(res.get(f), sort_keys=True) != \
                    json.dumps(res0.get(f), sort_keys=True):
                raise SystemExit("ERR_MERGE: shard %s field %r differs from "
                                 "shard %s — mismatched harness/corpus "
                                 "bytes can never be pooled"
                                 % (d, f, shards[0][0]))

    # 2) disjoint ledgers / repeat entries; globally unique row tuples
    merged = {"training_ledger": {}, "eval_ledger": {}, "repeat_shas": {}}
    for d, res, _rows in shards:
        for field in merged:
            for k, v in (res.get(field) or {}).items():
                if k in merged[field]:
                    raise SystemExit("ERR_MERGE: duplicate %s key %r "
                                     "(shard %s) — a cell ran twice"
                                     % (field, k, d))
                merged[field][k] = v
    all_rows, seen = [], set()
    for d, _res, rows in shards:
        for r in rows:
            k = row_key(r)
            if k in seen:
                raise SystemExit("ERR_MERGE: duplicate row %r (shard %s)"
                                 % (k, d))
            seen.add(k)
            all_rows.append(r)
    all_rows.sort(key=row_key)

    # 3) coverage: per FT arm/rung, seeds == design; canonical-seed strata +
    #    repeat present (B4 exempt from repeat per PROPOSED-ASM-1450)
    design_seeds = set(res0["ft_seeds_design"])
    canon = res0["canonical_first_seed"]
    by_arm_rung = {}
    for r in all_rows:
        by_arm_rung.setdefault((r["arm"], r["rung"]), set()).add(r["seed"])
    ft_arms = ("B1", "B2", "B3", "c1p")
    for (arm, rung), seeds in sorted(by_arm_rung.items()):
        if arm in ft_arms:
            if seeds != design_seeds:
                raise SystemExit("ERR_MERGE: %s/%s seeds %s != design %s "
                                 "(incomplete shard set)"
                                 % (arm, rung, sorted(seeds),
                                    sorted(design_seeds)))
            key = "%s/%s/seed=%s" % (arm, rung, canon)
            if key not in merged["repeat_shas"]:
                raise SystemExit("ERR_MERGE: missing repeat entry %s" % key)
            strata_cells = {r["cell"] for r in all_rows
                            if r["arm"] == arm and r["rung"] == rung
                            and r["seed"] == canon}
            for c in ("s_mem", "s_held", "stated", "refusal_train"):
                if c not in strata_cells:
                    raise SystemExit("ERR_MERGE: %s/%s canonical seed %s "
                                     "missing stratum %r"
                                     % (arm, rung, canon, c))

    # 4) canonical outputs
    os.makedirs(args.out_dir, exist_ok=True)
    suffix = "-mock" if res0["mode"] == "MOCK" else ""
    rec_path = os.path.join(args.out_dir,
                            "run-records-rules2%s.jsonl" % suffix)
    with open(rec_path, "w") as f:
        for r in all_rows:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    decision_rows = [{k: v for k, v in r.items() if k != "engine_us"}
                     for r in all_rows]
    out = dict(res0)
    out.update(merged)
    out["arms"] = sorted({r["arm"] for r in all_rows},
                         key=lambda a: ARM_ORDER.get(a, 99))
    out["rungs"] = sorted({r["rung"] for r in all_rows})
    out["ft_seeds"] = sorted(design_seeds)
    out["seeds_filter"] = None
    out["shard_tag"] = None
    out["n_rows"] = len(all_rows)
    out["records_file"] = os.path.basename(rec_path)
    out["records_sha256"] = sha256_file(rec_path)
    out["decision_sha256"] = hashlib.sha256(json.dumps(
        decision_rows, sort_keys=True, separators=(",", ":"))
        .encode()).hexdigest()
    out["wallClockHours"] = sum(res["wallClockHours"]
                                for _d, res, _r in shards)
    out["merge_note"] = ("merged by poc/rules-2/merge_shards.py from %d "
                         "shards; rows canonically ordered by (arm, rung, "
                         "seed, cell, item_id); per-shard record shas in "
                         "/shards; the pinned analysis is row-order-"
                         "independent" % len(shards))
    out["shards"] = [{
        "dir": os.path.basename(os.path.normpath(d)),
        "shard_tag": res.get("shard_tag"),
        "arms": res["arms"], "rungs": res["rungs"],
        "seeds_filter": res.get("seeds_filter"),
        "n_rows": res["n_rows"],
        "records_sha256": res["records_sha256"],
        "decision_sha256": res["decision_sha256"],
        "wallClockHours": res["wallClockHours"],
    } for d, res, _r in shards]
    res_path = os.path.join(args.out_dir, "results-rules2%s.json" % suffix)
    with open(res_path, "w") as f:
        json.dump(out, f, indent=2, sort_keys=True)
    print("merged %d shards -> %s (%d rows, records sha %s)"
          % (len(shards), args.out_dir, len(all_rows),
             out["records_sha256"][:12]))


if __name__ == "__main__":
    main()
