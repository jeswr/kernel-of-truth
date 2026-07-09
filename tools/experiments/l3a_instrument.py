#!/usr/bin/env python3
"""l3a_instrument — L3a rules-engine-oracle run (HL3a engine leg, gold parse).

    python3 tools/experiments/l3a_instrument.py --arm engine|abstain-all|answer-all \
        [--root <repo>] [--phase final]

RAW OUTPUT ONLY (P2 §2.4): emits one complete kot-log/1 record BODY (counts,
pins, config) on stdout for log-append; renders NO verdict and knows nothing
about the pre-registered thresholds (frozen in registry/experiments/l3a.json,
applied by verdict-gen through analysis/l3a.py).

Arms (design doc §5.3; all three are final-phase records, one per arm):
  engine       the kot-axiom/1 v0 oracle (tools/axiom/kot_axiom.py): licensed
               deterministic index lookups, provenance + axiom license on every
               answer, named ERR_* refusal otherwise.
  abstain-all  trivial-policy baseline 1: refuses every query (code ABSTAIN).
               Perfect refusal-by-count, zero covered answers — defeats any
               refusal-only reading of the primary.
  answer-all   trivial-policy baseline 2: never refuses. Where the engine
               refuses, it fabricates deterministically from the same indexes
               (first candidate edge / asserted count / asserted-class boolean /
               False). High covered exactness, zero refusals — defeats any
               answer-only reading. The conjunctive primary requires both.

Scoring (pre-registered, design doc §5.2):
  covered exact   = status answer AND value == expected AND (engine arm only)
                    non-empty provenance + license
  control correct = status refuse AND code == expected code (STRICT code match
                    for the engine; baselines additionally report refused-any)

Deterministic: no RNG anywhere (the corpus generator is RNG-free; seed 0 is
the registered placeholder). The full eval pass is run TWICE and byte-compared
(metrics.deterministic_repeat_identical).
"""

import argparse
import hashlib
import json
import os
import platform
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(_HERE), "axiom"))
sys.path.insert(0, os.path.join(os.path.dirname(_HERE), "registry"))
import kot_axiom  # noqa: E402
import kot_common  # noqa: E402

ARMS = ("engine", "abstain-all", "answer-all")
GLOBAL_DEFAULT_GUESS = None  # answer-all's guess when it has nothing at all


def file_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def policy_answer_all(eng, query):
    """Never refuses; fabricates deterministically where the engine refuses."""
    r = eng.query(query)
    if r["status"] == "answer":
        return r
    op = query.get("op")
    try:
        if op in ("unique", "lookup", "count"):
            edges = eng._edges(query.get("rel", ""), query.get("subject", ""),
                               query.get("direction", "forward"))
            objs = sorted(set(o for (o, _ref) in edges))
            if op == "unique":
                value = objs[0] if objs else GLOBAL_DEFAULT_GUESS
            elif op == "lookup":
                value = objs
            else:
                value = len(eng._qualified_edges(query.get("rel", ""),
                                                 query.get("subject", ""),
                                                 query.get("direction", "forward"),
                                                 query.get("qualifier")))
        elif op == "instance":
            value = query.get("concept") in eng.classes.get(query.get("entity", ""), {})
        else:
            value = GLOBAL_DEFAULT_GUESS
    except Exception:
        value = GLOBAL_DEFAULT_GUESS
    return {"status": "answer", "value": value, "provenance": [], "license": ["fabricated"]}


def run_arm(eng, queries, arm):
    results = []
    for rec in queries:
        if arm == "engine":
            results.append(eng.query(rec["query"]))
        elif arm == "abstain-all":
            results.append({"status": "refuse", "code": "ABSTAIN", "reason": "policy"})
        else:
            results.append(policy_answer_all(eng, rec["query"]))
    return results


def score(queries, results, arm, world_ids):
    m = {"n_covered": 0, "n_covered_exact": 0, "n_covered_refused": 0,
         "n_covered_answered_wrong": 0,
         "n_control": 0, "n_control_refused_correct_code": 0,
         "n_control_refused_other_code": 0, "n_control_answered": 0,
         "by_family": {}}
    prov_checked, prov_ok = 0, True
    for rec, r in zip(queries, results):
        fam = m["by_family"].setdefault(rec["family"], {"n": 0, "ok": 0})
        fam["n"] += 1
        exp = rec["expected"]
        if rec["class"] == "covered":
            m["n_covered"] += 1
            if r["status"] != "answer":
                m["n_covered_refused"] += 1
            else:
                exact = r["value"] == exp["value"]
                if arm == "engine":
                    prov_checked += 1
                    good_prov = (bool(r.get("provenance")) and bool(r.get("license"))
                                 and all(p in world_ids for p in r["provenance"]))
                    prov_ok = prov_ok and good_prov
                    exact = exact and good_prov
                if exact:
                    m["n_covered_exact"] += 1
                    fam["ok"] += 1
                else:
                    m["n_covered_answered_wrong"] += 1
        else:
            m["n_control"] += 1
            if r["status"] == "answer":
                m["n_control_answered"] += 1
            elif r["code"] == exp["code"]:
                m["n_control_refused_correct_code"] += 1
                fam["ok"] += 1
            else:
                m["n_control_refused_other_code"] += 1
    # baselines also report refused-any on control (fairness to abstain-all)
    m["n_control_refused_any"] = m["n_control_refused_correct_code"] + \
        m["n_control_refused_other_code"]
    m["provenance_checked"] = prov_checked
    m["provenance_all_valid"] = bool(prov_ok)
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", required=True, choices=ARMS)
    ap.add_argument("--root", default=None)
    ap.add_argument("--phase", default="final")
    args = ap.parse_args()
    root = args.root or os.path.dirname(os.path.dirname(_HERE))

    axioms, world = kot_axiom.load_corpora(root)
    eng = kot_axiom.Engine(axioms, world)
    with open(os.path.join(root, "data", "l3a-eval", "queries.jsonl"), "r",
              encoding="utf-8") as f:
        queries = [json.loads(l) for l in f if l.strip()]

    t0 = time.perf_counter_ns()
    results = run_arm(eng, queries, args.arm)
    t1 = time.perf_counter_ns()
    results2 = run_arm(eng, queries, args.arm)
    deterministic = json.dumps(results, sort_keys=True) == json.dumps(results2, sort_keys=True)

    metrics = score(queries, results, args.arm, eng.world_ids)
    from collections import Counter
    vio = Counter(v["code"] for v in eng.violations)
    metrics["store"] = {
        "n_axiom_records": len(eng.axioms),
        "n_world_records": len(world),
        "n_entities": len(eng.entities),
        "n_violations": len(eng.violations),
        "violations_by_code": dict(sorted(vio.items())),
        "n_incomplete_pairs": len(eng.incomplete),
    }
    metrics["engine_total_ns"] = t1 - t0
    metrics["n_queries"] = len(queries)
    metrics["deterministic_repeat_identical"] = bool(deterministic)
    metrics["coverage_note"] = ("eval authored against the world-layer records — "
                                "coverage is by construction (design doc §5.1); no m0b "
                                "concept-coverage gate applies to this engine-only rung")

    inst_path = os.path.join(_HERE, "l3a_instrument.py")
    prereg_hash = None
    idx_path = os.path.join(root, "registry", "frozen-index.json")
    if os.path.isfile(idx_path):
        with open(idx_path, "r", encoding="utf-8") as f:
            prereg_hash = json.load(f).get("l3a")

    pins_observed = {"_recipe": kot_common.CORPUS_RECIPE}
    for corpus in ("axioms-v0", "world-v0", "l3a-eval", "kernel-v0", "molecules-v0"):
        pins_observed["corpus_%s" % corpus] = {
            "observed": kot_common.corpus_hash(root, corpus),
            "recipe": "kot-corpus-hash/1"}
    pins_observed["instrument"] = {"observed": file_sha256(inst_path)}
    pins_observed["engine"] = {
        "observed": file_sha256(os.path.join(root, "tools", "axiom", "kot_axiom.py"))}
    pins_observed["analysis_script"] = {
        "observed": file_sha256(os.path.join(root, "analysis", "l3a.py"))}

    body = {
        "event": "run",
        "experiment": "l3a",
        "phase": args.phase,
        "config": {
            "arm": args.arm,
            "seed": 0,
            "rung": "R0",
            "instrument": "tools/experiments/l3a_instrument.py",
            "instrument_sha256": pins_observed["instrument"]["observed"],
            "engine_sha256": pins_observed["engine"]["observed"],
            "python_version": platform.python_version(),
            "hardware": "r0-local-cpu shared 2-core box, nice -n 10, foreground",
            "scope_note": "HL3a ENGINE LEG ONLY (gold-parsed closed-grammar queries); "
                          "NL-parse and LLM/RAG comparison arms register under a "
                          "successor id per the frozen record's n_planned.successors",
        },
        "metrics": metrics,
        "pins_observed": pins_observed,
        "cost": {"usd": 0},
        "exit": "ok",
        "error": None,
    }
    if prereg_hash:
        body["prereg_hash"] = prereg_hash
    body["config_sha256"] = hashlib.sha256(
        json.dumps(body["config"], sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    print(json.dumps(body, sort_keys=True))


if __name__ == "__main__":
    main()
