#!/usr/bin/env python3
"""a5_instrument — A5 code world-layer + code-structure-oracle run (registry
id `a5`; idea-code-worldlayer-cpg; HA5 engine leg, deterministic extraction).

    python3 tools/experiments/a5_instrument.py --arm engine|abstain-all|answer-all \
        [--root <repo>] [--phase final]

RAW OUTPUT ONLY (P2 §2.4): emits one complete kot-log/1 record BODY (counts,
pins, config) on stdout for log-append; renders NO verdict and knows nothing
about the pre-registered thresholds (frozen in registry/experiments/a5.json,
applied by verdict-gen through analysis/a5.py).

Arms (design doc §5; all three are final-phase records, one per arm):
  engine       the kot-query-code/1 oracle (tools/axiom/kot_code.py) over the
               UNCHANGED kot-axiom/1 v0 engine: named-op desugaring, licensed
               deterministic index lookups, provenance + license on every
               answer, named ERR_* refusal otherwise.
  abstain-all  trivial-policy baseline 1: refuses every query (code ABSTAIN).
  answer-all   trivial-policy baseline 2: never refuses. Where the oracle
               refuses, it fabricates deterministically from the same indexes
               (first/all candidate edges / asserted-class boolean / None).
               The conjunctive primary requires both covered exactness AND
               correct refusals; neither trivial policy can satisfy it.

Scoring (pre-registered, design doc §5):
  covered exact   = status answer AND value == expected AND (engine arm only)
                    non-empty provenance within world ids + non-empty license
  control correct = status refuse AND code == expected code (STRICT)

Deterministic: no RNG anywhere (the extractor/generator is RNG-free; seed 0 is
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
import kot_code  # noqa: E402
import kot_common  # noqa: E402

ARMS = ("engine", "abstain-all", "answer-all")
GLOBAL_DEFAULT_GUESS = None  # answer-all's guess when it has nothing at all


def file_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def policy_answer_all(oracle, query):
    """Never refuses; fabricates deterministically where the oracle refuses."""
    r = oracle.query(query)
    if r["status"] == "answer":
        return r
    core = oracle.desugar(query)
    value = GLOBAL_DEFAULT_GUESS
    if core.get("status") != "refuse":
        try:
            if core["op"] in ("unique", "lookup"):
                edges = oracle.engine._edges(core["rel"], core["subject"], core["direction"])
                objs = sorted(set(o for (o, _ref) in edges))
                value = (objs[0] if objs else GLOBAL_DEFAULT_GUESS) \
                    if core["op"] == "unique" else objs
            elif core["op"] == "instance":
                value = core["concept"] in oracle.engine.classes.get(core["entity"], {})
        except Exception:
            value = GLOBAL_DEFAULT_GUESS
    return {"status": "answer", "value": value, "provenance": [], "license": ["fabricated"]}


def run_arm(oracle, queries, arm):
    results = []
    for rec in queries:
        if arm == "engine":
            results.append(oracle.query(rec["query"]))
        elif arm == "abstain-all":
            results.append({"status": "refuse", "code": "ABSTAIN", "reason": "policy"})
        else:
            results.append(policy_answer_all(oracle, rec["query"]))
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

    oracle = kot_code.build_code_oracle(root)
    with open(os.path.join(root, "data", "a5-eval", "queries.jsonl"), "r",
              encoding="utf-8") as f:
        queries = [json.loads(l) for l in f if l.strip()]

    t0 = time.perf_counter_ns()
    results = run_arm(oracle, queries, args.arm)
    t1 = time.perf_counter_ns()
    results2 = run_arm(oracle, queries, args.arm)
    deterministic = json.dumps(results, sort_keys=True) == json.dumps(results2, sort_keys=True)

    eng = oracle.engine
    metrics = score(queries, results, args.arm, eng.world_ids)
    from collections import Counter
    vio = Counter(v["code"] for v in eng.violations)
    with open(os.path.join(root, "data", "code-world-v0", "world.jsonl"),
              "r", encoding="utf-8") as f:
        n_world = sum(1 for l in f if l.strip())
    metrics["store"] = {
        "n_axiom_records": len(eng.axioms),
        "n_world_records": n_world,
        "n_entities": len(eng.entities),
        "n_violations": len(eng.violations),
        "violations_by_code": dict(sorted(vio.items())),
        "n_incomplete_pairs": len(eng.incomplete),
    }
    metrics["engine_total_ns"] = t1 - t0
    metrics["n_queries"] = len(queries)
    metrics["deterministic_repeat_identical"] = bool(deterministic)
    metrics["coverage_note"] = ("eval authored against the deterministically-extracted "
                                "code-world-v0 records - coverage is by construction "
                                "(design doc section 5); no m0b concept-coverage gate "
                                "applies to this engine-only rung")

    inst_path = os.path.join(_HERE, "a5_instrument.py")
    prereg_hash = None
    idx_path = os.path.join(root, "registry", "frozen-index.json")
    if os.path.isfile(idx_path):
        with open(idx_path, "r", encoding="utf-8") as f:
            prereg_hash = json.load(f).get("a5")

    pins_observed = {"_recipe": kot_common.CORPUS_RECIPE}
    for corpus in ("code-v0", "code-corpus-v0", "code-axioms-v0", "code-world-v0",
                   "a5-eval", "kernel-v0"):
        pins_observed["corpus_%s" % corpus] = {
            "observed": kot_common.corpus_hash(root, corpus),
            "recipe": "kot-corpus-hash/1"}
    pins_observed["instrument"] = {"observed": file_sha256(inst_path)}
    pins_observed["engine"] = {
        "observed": file_sha256(os.path.join(root, "tools", "axiom", "kot_axiom.py"))}
    pins_observed["code_layer"] = {
        "observed": file_sha256(os.path.join(root, "tools", "axiom", "kot_code.py"))}
    pins_observed["extractor"] = {
        "observed": file_sha256(os.path.join(root, "tools", "axiom", "gen_a5_corpora.py"))}
    pins_observed["analysis_script"] = {
        "observed": file_sha256(os.path.join(root, "analysis", "a5.py"))}

    body = {
        "event": "run",
        "experiment": "a5",
        "phase": args.phase,
        "config": {
            "arm": args.arm,
            "seed": 0,
            "rung": "R0",
            "instrument": "tools/experiments/a5_instrument.py",
            "instrument_sha256": pins_observed["instrument"]["observed"],
            "engine_sha256": pins_observed["engine"]["observed"],
            "code_layer_sha256": pins_observed["code_layer"]["observed"],
            "extractor_version": "kot-code-extract/1",
            "extractor_sha256": pins_observed["extractor"]["observed"],
            "python_version": platform.python_version(),
            "hardware": "r0-local-cpu shared 2-core box, nice -n 10, foreground",
            "scope_note": "HA5 ENGINE LEG ONLY (closed kot-query-code/1 grammar over the "
                          "deterministically-extracted code world layer); the claim that "
                          "LLMs fail such queries is LIT-BACKED motivation, NOT re-measured "
                          "here - no LLM arm exists in this record and no head-to-head "
                          "claim is licensed",
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
