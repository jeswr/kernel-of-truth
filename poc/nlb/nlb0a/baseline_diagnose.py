#!/usr/bin/env python3
"""NLB-0-A step 1 — baseline reproduction + dangerous-class diagnosis.

DIAGNOSTIC, design-phase (docs/next/design/NLB.md §7.1, ASM-0904(2)/ASM-0944):
re-runs the PINNED, UNMODIFIED front-end (tools/experiments/nlb/nlb_frontend.py
— not edited; sha verified against the frozen a5-nl record pins) over the
committed legacy a5-nl phrasing corpus (data/nlb-phrasings-a5/eval.jsonl,
outcomes public in registry/verdicts/a5-nl.json — disclosed post-outcome
analysis, never a gate) and:

  1. FAIL-CLOSED IDENTITY CHECK: recomputed aggregate counters must equal the
     frozen results-log mapper-parse final row byte-for-byte on every shared
     counter, and the pinned input file sha256s must match the frozen row's
     pins_observed. Any mismatch -> exit 3, no diagnosis emitted.
  2. Per-item diagnosis of every covered answered-wrong item (the S2
     dangerous class): parsed query vs gold query, mechanism bucket.

Output: poc/nlb/nlb0a/results/baseline.json. Deterministic, no RNG, CPU only.
"""

import hashlib
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(_ROOT, "tools", "axiom"))
sys.path.insert(0, os.path.join(_ROOT, "tools", "experiments", "nlb"))

import kot_code  # noqa: E402
import nlb_frontend  # noqa: E402
import nlb_instrument  # noqa: E402


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fail_closed(msg):
    print(json.dumps({"status": "FAIL_CLOSED", "error": msg}, indent=1))
    sys.exit(3)


def frozen_row(root):
    rows = []
    with open(os.path.join(root, "results-log", "a5-nl.jsonl")) as f:
        for line in f:
            if line.strip():
                r = json.loads(line)
                if (r.get("config", {}).get("arm") == "mapper-parse"
                        and r.get("phase") == "final"
                        and r.get("exit") == "ok"):
                    rows.append(r)
    if len(rows) != 1:
        fail_closed("expected exactly 1 mapper-parse final row, got %d"
                    % len(rows))
    return rows[0]


def main():
    root = _ROOT
    row = frozen_row(root)

    # --- pin verification (fail closed on any drift) ---------------------
    pins = row["pins_observed"]
    checks = {
        "nlb_frontend.py": os.path.join(
            root, "tools", "experiments", "nlb", "nlb_frontend.py"),
        "nlb_map.mjs": os.path.join(
            root, "tools", "experiments", "nlb", "nlb_map.mjs"),
        "corpus_file_eval.jsonl": os.path.join(
            root, "data", "nlb-phrasings-a5", "eval.jsonl"),
    }
    pin_report = {}
    for key, path in checks.items():
        want = pins[key]["observed"]
        got = sha256(path)
        pin_report[key] = {"frozen": want, "observed": got, "match": want == got}
        if want != got:
            fail_closed("pin mismatch on %s: frozen %s != observed %s"
                        % (key, want, got))
    eng_want = pins["engine"]["observed"]
    eng_got = sha256(os.path.join(root, "tools", "axiom", "kot_axiom.py"))
    pin_report["engine(kot_axiom.py)"] = {
        "frozen": eng_want, "observed": eng_got, "match": eng_want == eng_got}
    code_want = pins["code_layer"]["observed"]
    code_got = sha256(os.path.join(root, "tools", "axiom", "kot_code.py"))
    pin_report["code_layer(kot_code.py)"] = {
        "frozen": code_want, "observed": code_got, "match": code_want == code_got}
    if eng_want != eng_got or code_want != code_got:
        fail_closed("engine/code-layer pin mismatch")

    # --- re-run the PINNED front-end over the committed corpus -----------
    oracle = kot_code.build_code_oracle(root)
    ev = nlb_instrument.load_eval(root, "a5")
    included = [r for r in ev if r["family"] != "malformed"]
    phr = nlb_instrument.load_phrasings(
        os.path.join(root, "data", "nlb-phrasings-a5", "eval.jsonl"))
    phrasings = [{"qid": r["qid"], "text": phr[r["qid"]]} for r in included]
    parses = nlb_frontend.parse_all(phrasings, "a5", oracle.engine.entities,
                                    derange=False, root=root)
    outcomes = {}
    for r in included:
        p = parses[r["qid"]]
        outcomes[r["qid"]] = p if p["status"] == "refuse" \
            else oracle.query(p["query"])
    metrics = nlb_instrument.score_nl(
        included, outcomes, "mapper-parse", oracle.engine.world_ids,
        labelmap=nlb_instrument.build_labelmap(root, "a5", ev), texts=phr)

    # --- identity check vs the frozen row --------------------------------
    fm = row["metrics"]
    identity = {}
    for k in ("n_covered", "n_covered_exact", "n_covered_answered_wrong",
              "n_covered_refused_parse", "n_covered_refused_engine",
              "n_control", "n_control_refused_acceptable",
              "n_control_answered", "parse_stage_breakdown", "by_family",
              "label_strata"):
        identity[k] = (metrics[k] == fm[k])
    if not all(identity.values()):
        fail_closed("recomputed counters diverge from frozen row: %s"
                    % json.dumps({k: v for k, v in identity.items() if not v}))

    # --- diagnose the dangerous class ------------------------------------
    wrong = []
    for r in included:
        if r["class"] != "covered":
            continue
        out = outcomes[r["qid"]]
        if out.get("status") != "answer":
            continue
        exact = (out["value"] == r["expected"]["value"]
                 and bool(out.get("provenance")) and bool(out.get("license"))
                 and all(p in oracle.engine.world_ids
                         for p in out["provenance"]))
        if exact:
            continue
        parsed_q = parses[r["qid"]]["query"]
        gold_q = r["query"]
        if parsed_q.get("op") != gold_q.get("op"):
            bucket = "op-flip:%s->%s" % (gold_q.get("op"), parsed_q.get("op"))
        elif parsed_q.get("of", parsed_q.get("entity")) != \
                gold_q.get("of", gold_q.get("entity")):
            bucket = "entity-mismatch"
        else:
            bucket = "other"
        wrong.append({"qid": r["qid"], "family": r["family"],
                      "text": phr[r["qid"]], "gold_query": gold_q,
                      "parsed_query": parsed_q, "bucket": bucket})

    buckets = {}
    for w in wrong:
        buckets[w["bucket"]] = buckets.get(w["bucket"], 0) + 1

    result = {
        "schema": "nlb0a-baseline/1",
        "status": "OK",
        "identity_check": "PASS (all recomputed counters == frozen "
                          "results-log mapper-parse final row)",
        "pin_report": pin_report,
        "aggregates": {k: metrics[k] for k in
                       ("n_covered", "n_covered_exact",
                        "n_covered_answered_wrong",
                        "n_covered_refused_parse",
                        "n_covered_refused_engine",
                        "parse_stage_breakdown")},
        "wrong_bucket_counts": buckets,
        "wrong_items": wrong,
    }
    os.makedirs(os.path.join(_HERE, "results"), exist_ok=True)
    out_path = os.path.join(_HERE, "results", "baseline.json")
    with open(out_path, "w") as f:
        json.dump(result, f, indent=1, sort_keys=True)
        f.write("\n")
    print(json.dumps({"status": "OK", "wrong_bucket_counts": buckets,
                      "n_wrong": len(wrong), "out": out_path}, indent=1,
                     sort_keys=True))


if __name__ == "__main__":
    main()
