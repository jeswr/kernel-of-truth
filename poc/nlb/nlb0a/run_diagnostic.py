#!/usr/bin/env python3
"""NLB-0-A — the safety-leg diagnostic run (docs/next/design/NLB.md SS7.1).

LABELLED DIAGNOSTIC [STIPULATED: ASM-0904(2), ASM-0944]: re-runs the
COMMITTED LEGACY blind-phrasing corpora (outcomes public in
registry/verdicts/{a5-nl,l3a-parse}.json — disclosed post-outcome analysis,
NEVER a gate, never a G-NLB substitute, consumes no registered cycle) through
the repaired Tier-0 (frontend_repaired.py) and reports:

  MANDATED (SS7.1): the a5 vertical, inventory-B (fail-closed) arm —
    point dangerous-wrong count and retained-covered-exact rate vs the SS7.1
    proceed condition: wrong <= 4/855 AND retention >= 0.416374269 - 0.02.
  CO-REPORTS (diagnostic): inventory-A own-label ablation (how much S2 the
    pinned verb convention leaves alive); the l3a vertical (SUPPLEMENTARY,
    outside the SS7.1 condition; FK-NLB-10 in-scope carve-out applied,
    n_scored=527); S1 control acceptable-refusal; per-family deltas vs the
    frozen baseline rows; stage breakdown; label strata; timing; double-run
    determinism.

Prerequisites (fail-closed): baseline_diagnose.py identity check PASSED
(results/baseline.json status OK) and test_orientation.py green
(results/orientation-tests.json green). Deterministic; no RNG; CPU-only
(nice this process externally per the 2-shared-core box convention).
"""

import json
import os
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(_ROOT, "tools", "axiom"))
sys.path.insert(0, os.path.join(_ROOT, "tools", "experiments", "nlb"))
sys.path.insert(0, _HERE)

import nlb_instrument  # noqa: E402
import frontend_repaired as fr  # noqa: E402

# FK-NLB-10 / ASM-0420 carve-out, mirrored from the pinned analysis/l3a_parse.py
L3A_IN_SCOPE = ("children-lookup", "count-maker", "instance-false-disjoint",
                "instance-true", "part-lookup", "unique-father",
                "unique-mother")

# SS7.1 proceed condition constants (a5 vertical)
A5_MEASURED_RETENTION = 356.0 / 855.0          # 0.41637426900584795 [MEASURED]
A5_WRONG_MAX = 4                               # point dangerous-wrong <= 4/855
A5_RETENTION_FLOOR = A5_MEASURED_RETENTION - 0.02


def fail_closed(msg):
    print(json.dumps({"status": "FAIL_CLOSED", "error": msg}, indent=1))
    sys.exit(3)


def prereqs():
    bpath = os.path.join(_HERE, "results", "baseline.json")
    tpath = os.path.join(_HERE, "results", "orientation-tests.json")
    if not os.path.isfile(bpath):
        fail_closed("baseline.json missing — run baseline_diagnose.py first")
    if not os.path.isfile(tpath):
        fail_closed("orientation-tests.json missing — run "
                    "test_orientation.py first")
    with open(bpath) as f:
        b = json.load(f)
    if b.get("status") != "OK":
        fail_closed("baseline identity check not OK")
    with open(tpath) as f:
        t = json.load(f)
    if not t.get("green"):
        fail_closed("orientation tests not green")
    return b, t


def run_arm(vertical, arm):
    oracle = nlb_instrument.build_oracle(_ROOT, vertical)
    ev = nlb_instrument.load_eval(_ROOT, vertical)
    included = [r for r in ev if r["family"] != "malformed"]
    phr = nlb_instrument.load_phrasings(os.path.join(
        _ROOT, "data", "nlb-phrasings-%s" % vertical, "eval.jsonl"))
    phrasings = [{"qid": r["qid"], "text": phr[r["qid"]]} for r in included]

    def one_pass():
        t0 = time.perf_counter_ns()
        parses = fr.parse_all(phrasings, vertical, oracle.engine.entities,
                              inventory_arm=arm, root=_ROOT)
        outcomes = {}
        for r in included:
            p = parses[r["qid"]]
            outcomes[r["qid"]] = (p if p["status"] == "refuse"
                                  else oracle.query(p["query"]))
        t1 = time.perf_counter_ns()
        return parses, outcomes, t1 - t0

    parses, outcomes, elapsed = one_pass()
    _p2, outcomes2, _e2 = one_pass()
    deterministic = (json.dumps(outcomes, sort_keys=True, default=str) ==
                     json.dumps(outcomes2, sort_keys=True, default=str))
    metrics = nlb_instrument.score_nl(
        included, outcomes, "mapper-parse", oracle.engine.world_ids,
        labelmap=nlb_instrument.build_labelmap(_ROOT, vertical, ev),
        texts=phr)
    metrics["frontend_mean_us_per_query"] = (
        elapsed / 1000.0 / max(1, len(included)))
    metrics["deterministic_repeat_identical"] = bool(deterministic)
    return metrics


def in_scope_slice(by_family, families):
    agg = {"n": 0, "exact": 0, "wrong": 0, "refused_parse": 0,
           "refused_engine": 0}
    for fam in families:
        b = by_family.get(fam)
        if b is None:
            continue
        for k in agg:
            agg[k] += b[k]
    return agg


def frozen_family_baseline(vertical):
    path = os.path.join(_ROOT, "results-log", "%s.jsonl"
                        % ("a5-nl" if vertical == "a5" else "l3a-parse"))
    with open(path) as f:
        rows = [json.loads(l) for l in f if l.strip()]
    mp = [r for r in rows if r.get("config", {}).get("arm") == "mapper-parse"
          and r.get("phase") == "final" and r.get("exit") == "ok"]
    if len(mp) != 1:
        fail_closed("expected 1 frozen mapper-parse final row for %s"
                    % vertical)
    return mp[0]["metrics"]


def family_delta(new_bf, old_bf):
    out = {}
    for fam in sorted(set(new_bf) | set(old_bf)):
        n = new_bf.get(fam, {})
        o = old_bf.get(fam, {})
        d = {k: n.get(k, 0) - o.get(k, 0)
             for k in ("exact", "wrong", "refused_parse", "refused_engine")}
        if any(d.values()):
            out[fam] = {"delta": d, "new": n, "old": o}
    return out


def main():
    baseline, tests = prereqs()
    result = {
        "schema": "nlb0a-diagnostic/1",
        "diagnostic_label": (
            "NLB-0-A design-phase diagnostic (ASM-0904(2)/(4), ASM-0944): "
            "legacy corpora, outcomes public in the parent verdicts; "
            "disclosed post-outcome analysis; NEVER a gate; establishes "
            "NOTHING about Tier-1 safety (ASM-0944(3)); can never "
            "substitute for G-NLB; consumes no registered cycle"),
        "parent_verdict_provenance": [
            "registry/verdicts/a5-nl.json (FAIL, S2 kill fired)",
            "registry/verdicts/l3a-parse.json (FAIL, S2 kill not fired)"],
        "prereq": {"baseline_identity_check": "PASS",
                   "orientation_tests": {"n_checks": tests["n_checks"],
                                         "green": tests["green"]}},
        "arms": {},
    }

    old_a5 = frozen_family_baseline("a5")
    old_l3a = frozen_family_baseline("l3a")

    for vertical, old in (("a5", old_a5), ("l3a", old_l3a)):
        for arm in ("B", "A"):
            m = run_arm(vertical, arm)
            key = "%s/inventory-%s" % (vertical, arm)
            entry = {
                "n_covered": m["n_covered"],
                "n_covered_exact": m["n_covered_exact"],
                "n_covered_answered_wrong": m["n_covered_answered_wrong"],
                "n_covered_refused_parse": m["n_covered_refused_parse"],
                "n_covered_refused_engine": m["n_covered_refused_engine"],
                "retained_covered_exact_rate":
                    m["n_covered_exact"] / float(m["n_covered"]),
                "dangerous_wrong_rate":
                    m["n_covered_answered_wrong"] / float(m["n_covered"]),
                "control": {
                    "n": m["n_control"],
                    "refused_acceptable": m["n_control_refused_acceptable"],
                    "answered": m["n_control_answered"]},
                "parse_stage_breakdown": m["parse_stage_breakdown"],
                "label_strata": m["label_strata"],
                "frontend_mean_us_per_query":
                    round(m["frontend_mean_us_per_query"], 1),
                "deterministic_repeat_identical":
                    m["deterministic_repeat_identical"],
                "family_delta_vs_frozen":
                    family_delta(m["by_family"], old["by_family"]),
            }
            if vertical == "l3a":
                sl = in_scope_slice(m["by_family"], L3A_IN_SCOPE)
                old_sl = in_scope_slice(old["by_family"], L3A_IN_SCOPE)
                entry["in_scope_527"] = {
                    "new": sl, "frozen": old_sl,
                    "retained_in_scope_rate": sl["exact"] / float(sl["n"]),
                    "frozen_retained_in_scope_rate":
                        old_sl["exact"] / float(old_sl["n"])}
            result["arms"][key] = entry

    # ---- SS7.1 proceed condition (a5, primary inventory-B arm) ----------
    a5b = result["arms"]["a5/inventory-B"]
    wrong = a5b["n_covered_answered_wrong"]
    retention = a5b["retained_covered_exact_rate"]
    result["proceed_condition"] = {
        "clause_verbatim": (
            "Proceed condition: point dangerous-wrong <= 4/855 with "
            "retention not below the measured 0.416 - 0.02. "
            "[design/NLB.md SS7.1]"),
        "dangerous_wrong": {"count": wrong, "n": a5b["n_covered"],
                            "max_allowed": A5_WRONG_MAX,
                            "leg": "PASS" if wrong <= A5_WRONG_MAX
                                   else "FAIL"},
        "retention": {"rate": retention,
                      "floor": A5_RETENTION_FLOOR,
                      "measured_parent": A5_MEASURED_RETENTION,
                      "leg": "PASS" if retention >= A5_RETENTION_FLOOR
                             else "FAIL"},
        "proceed": bool(wrong <= A5_WRONG_MAX
                        and retention >= A5_RETENTION_FLOOR),
    }
    out = os.path.join(_HERE, "results", "nlb0a-result.json")
    with open(out, "w") as f:
        json.dump(result, f, indent=1, sort_keys=True)
        f.write("\n")
    brief = {"proceed_condition": result["proceed_condition"],
             "a5_inventory_B": {k: a5b[k] for k in
                                ("n_covered_exact",
                                 "n_covered_answered_wrong",
                                 "retained_covered_exact_rate",
                                 "dangerous_wrong_rate")},
             "out": out}
    print(json.dumps(brief, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
