#!/usr/bin/env python3
# ENGINE-INF deterministic engine harness — BOTH question of design §0 in one
# run: per-item closure-correctness rows for all 5 arms + the oracle arm,
# checked against the pinned gold, plus the divergence certificates
# (the ASM-1851 leg-1 analog, design §2.3). NO LLM anywhere; the entire
# instrument is pinned bytes -> certified engine -> string-equality scoring.
#
#   python3 engineinf_runner.py --dry-plan     # plan + worst-case cost, no run
#   python3 engineinf_runner.py                # full run (CPU, ~seconds, $0)
#
# Emits: results/rows.jsonl                per item x arm decision rows
#        results/divergence-certificate.json  Div(K,b) full+decision, per-op/
#                                              per-lemma composition (pinned)
#        results/run-result.json           pins, counts, double-run sha
#
# Certificate discipline (rules-1): deterministic => no seeds; the WHOLE
# decision payload is computed twice and must be byte-identical.

import argparse
import json
import time
from pathlib import Path

from engineinf_lib import (ARM_NAMES, WN, arm_relation, arm_tbox_paths,
                           canon_sha, divergence, kernel_inventory, load_tbox,
                           neutral_world, run_item, score, sha256_file,
                           MODULE, ROOT)

HERE = Path(__file__).resolve().parent
OUT = HERE / "results"


def compute_rows(wn, items, gold, minted, arms_dir):
    tboxes = {a: load_tbox(p) for a, p in sorted(arm_tbox_paths(arms_dir).items())}
    rows_by_arm = {a: {} for a in ARM_NAMES}
    oracle = {}
    for it in items:
        world = neutral_world(wn, it)
        g = gold[it["id"]]
        for arm in ARM_NAMES:
            rel = arm_relation(arm, it, minted)
            verdict, refusal, derived = run_item(tboxes[arm], world, rel)
            from engineinf_lib import derived_sides
            correct, pen = score(g, verdict)
            rows_by_arm[arm][it["id"]] = {
                "item": it["id"], "kind": it["kind"], "lemma": it["lemma"],
                "gold_rule": g["gold_rule"], "gold_verdict": g["verdict"],
                "arm": arm, "relation": rel, "verdict": verdict,
                "refusal": refusal, "derived_cls": derived,
                "derived_sides": derived_sides(derived),
                "correct": bool(correct), "honesty_penalty": pen}
        # oracle arm (PC-5): gold verdicts injected through the PINNED scorer
        ov = g["verdict"]
        ocorrect, open_ = score(g, ov)
        oracle[it["id"]] = {"item": it["id"], "kind": it["kind"],
                            "lemma": it["lemma"], "gold_rule": g["gold_rule"],
                            "gold_verdict": g["verdict"], "arm": "oracle",
                            "relation": None, "verdict": ov, "refusal": None,
                            "derived_cls": [], "derived_sides": [],
                            "correct": bool(ocorrect), "honesty_penalty": open_}
    return rows_by_arm, oracle


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-plan", action="store_true")
    args = ap.parse_args()

    items_doc = json.load(open(OUT / "items.json"))
    items = items_doc["items"]
    gold = json.load(open(OUT / "gold.json"))["gold"]
    minted, _, _ = kernel_inventory()

    plan = {
        "experiment": "engine-inference",
        "arms": list(ARM_NAMES) + ["oracle"],
        "items": len(items),
        "decisions": len(items) * (len(ARM_NAMES) + 1) * 2,
        "channel": "DETERMINISTIC (pinned bytes -> certified twin engine -> "
                   "string-equality scoring vs third-party-derived gold); "
                   "no LLM, no host, no judge, no network",
        "worst_case_usd": 0.0,
        "compute": "CPU-only, single process, nice-appropriate; the rules-1 "
                   "certificate closed 958 worlds in <2s on this box — this "
                   "run is the same order",
    }
    if args.dry_plan:
        print(json.dumps({"dry_plan": plan}, indent=1, sort_keys=True))
        return

    t0 = time.time()
    wn = WN()
    rows_by_arm, oracle = compute_rows(wn, items, gold, minted, HERE / "arms")
    # determinism: full second pass, byte-identity required
    rows2, oracle2 = compute_rows(wn, items, gold, minted, HERE / "arms")
    sha1 = canon_sha({"rows": rows_by_arm, "oracle": oracle})
    sha2 = canon_sha({"rows": rows2, "oracle": oracle2})

    items_by_id = {it["id"]: it for it in items}
    certs = {b: divergence(rows_by_arm, b, items_by_id)
             for b in ARM_NAMES if b != "K"}

    with open(OUT / "rows.jsonl", "w") as f:
        for arm in ARM_NAMES:
            for iid in sorted(rows_by_arm[arm]):
                f.write(json.dumps(rows_by_arm[arm][iid], sort_keys=True) + "\n")
        for iid in sorted(oracle):
            f.write(json.dumps(oracle[iid], sort_keys=True) + "\n")

    cert_doc = {
        "schema": "kot-engineinf-divergence/1",
        "role": ("Divergence certificate (design §2.3; the ASM-1851 leg-1 "
                 "analog): committed BEFORE any contrast is interpreted; "
                 "'full' = verdict-or-derived-side-set differs (ASM-1994 "
                 "signature), 'decision' = engine verdict differs. A "
                 "committed non-empty certificate over this inventory is the "
                 "ASM-1851 mechanical re-activation artifact for the "
                 "rules-2-shaped train-time twin (ASM-1965)."),
        "divergence": {b: {"n_full": len(c["full"]),
                           "n_decision": len(c["decision"]),
                           "full": c["full"], "decision": c["decision"],
                           "composition": c["composition"]}
                       for b, c in sorted(certs.items())},
    }
    (OUT / "divergence-certificate.json").write_text(
        json.dumps(cert_doc, indent=1, sort_keys=True) + "\n")

    per_arm = {}
    for arm in ARM_NAMES:
        rs = rows_by_arm[arm]
        per_arm[arm] = {
            "n": len(rs),
            "correct": sum(1 for r in rs.values() if r["correct"]),
            "honesty_penalty_sum": round(sum(r["honesty_penalty"]
                                             for r in rs.values()), 2),
            "refusals": sum(1 for r in rs.values() if r["verdict"] == "REFUSE"),
            "anomalous": sum(1 for r in rs.values()
                             if r["verdict"] == "ANOMALOUS")}
    per_arm["oracle"] = {"n": len(oracle),
                         "correct": sum(1 for r in oracle.values()
                                        if r["correct"])}

    pins = {
        "items_json": sha256_file(OUT / "items.json"),
        "gold_json": sha256_file(OUT / "gold.json"),
        "rows_jsonl": sha256_file(OUT / "rows.jsonl"),
        "divergence_certificate": sha256_file(OUT / "divergence-certificate.json"),
        "arm_manifest": sha256_file(HERE / "arms" / "arm-manifest.json"),
        "twin_engine_py": sha256_file(ROOT / "poc/rules-1/twin_engine.py"),
        "engineinf_lib_py": sha256_file(HERE / "engineinf_lib.py"),
        "engineinf_runner_py": sha256_file(HERE / "engineinf_runner.py"),
        "module_manifest": sha256_file(MODULE / "manifest.json"),
    }
    result = {
        "schema": "kot-engineinf-run/1",
        "status": ("PRE-FREEZE EXPLORATORY execution of the pinned "
                   "deterministic harness (mock/pilot posture). NO "
                   "feasibility conclusion is stated; verdicts belong to "
                   "verdict-gen over the FROZEN record's registered run."),
        "plan": plan,
        "per_arm": per_arm,
        "divergence_counts": {b: {"full": len(c["full"]),
                                  "decision": len(c["decision"])}
                              for b, c in sorted(certs.items())},
        "determinism": {"double_run_sha_match": sha1 == sha2,
                        "decision_payload_sha256": sha1},
        "pins": pins,
        "timing_seconds": round(time.time() - t0, 3),
    }
    (OUT / "run-result.json").write_text(
        json.dumps(result, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: result[k] for k in
                      ("per_arm", "divergence_counts", "determinism",
                       "timing_seconds")}, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
