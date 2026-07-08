#!/usr/bin/env python3
"""m0b pinned analysis — kernel-vocabulary coverage census + NICHE-SCOPE gate
(P1 §5 required gate; P3 §1.1 m0b.* / m0b.gate, RT-7b; P2 G-7).

Correction c-m0b-1 (2026-07-08, pre-sign-off): coverage is now a DETERMINISTIC
on-box census (tools/experiments/m0b_instrument.py) — the fraction of the
pre-declared target-task content-word token mass
(data/task-family-tinystories/, TinyStories validation) whose lemma is in the
kernel vocabulary at each rung. The earlier design's human spot-check (GATE-H)
and 2000-token sampling + Wilson machinery are dropped WITH the sampling they
existed to police: a census has no sampling error, and count-based criteria
carry no statistical test (P1 common rules). The judgment-based
"plausibly-explicable" estimate remains exploratory context (mapper/m0/).

Eligible run records on stdin; analysis-output JSON on stdout.

Input metric contract (instrument keys; one record carries all rungs):
  metrics.rungs[]              [{coverage_rung, n_covered, n_tokens_total}, ...]
  metrics.coverage             {fraction, rung} (P-8 restatement block)

PRIMARY RUNG (fixed at freeze): "molecules-v0" — the deepest authored kernel
content; "wn31-aligned" is the AxiomsOnly-reachable band, reported only in
coverage_by_rung and never quoted as explicated coverage.

Output fields:
  /gates/instrument_valid    primary rung present with positive totals AND
                             coverage monotone non-decreasing over the rung
                             ladder kernel-v0 <= molecules-v0 <= wn31-aligned
                             (vocabularies are supersets by construction; a
                             violation is an instrument bug)
  /analysis/coverage_fraction  (primary rung; the NICHE-SCOPE gate number)
  /analysis/coverage_by_rung   {rung: fraction}
  /analysis/coverage_rung      the primary rung label (restated everywhere, P2 G-7)
  /analysis/n_tokens_total     census denominator (full content-word mass)

Verdict mapping (frozen record): PASS iff coverage_fraction > 0.20 (the
pre-declared NICHE-SCOPE default X = 20% of the target task family's
content-word mass — maintainer ratifies X at GNG-0 signing); FAIL iff
coverage_fraction <= 0.20 (the NICHE-SCOPE banner binds every later verdict
template and any frontier-pitch route must carry a coverage-growth cost line).

Fixture (--selftest, HAND-COMPUTED): 605599/1709765 covered -> 0.35420...;
non-monotone rungs -> instrument_valid False.
"""
import json
import sys

PRIMARY_RUNG = "molecules-v0"
LADDER = ("kernel-v0", "molecules-v0", "wn31-aligned")


def analyze(records):
    rungs = {}
    for r in records:
        for entry in r["metrics"].get("rungs", []):
            s = rungs.setdefault(entry["coverage_rung"], {"covered": 0, "total": 0})
            s["covered"] += int(entry["n_covered"])
            s["total"] += int(entry["n_tokens_total"])
    by_rung = {k: v["covered"] / v["total"] for k, v in sorted(rungs.items()) if v["total"] > 0}

    ladder_vals = [by_rung[r] for r in LADDER if r in by_rung]
    monotone = all(a <= b + 1e-12 for a, b in zip(ladder_vals, ladder_vals[1:]))
    valid = (PRIMARY_RUNG in by_rung) and rungs[PRIMARY_RUNG]["total"] > 0 and monotone

    out = {"gates": {"instrument_valid": valid}, "analysis": {}}
    if by_rung:
        out["analysis"]["coverage_by_rung"] = by_rung
    if PRIMARY_RUNG in by_rung:
        out["analysis"].update({
            "coverage_fraction": by_rung[PRIMARY_RUNG],
            "coverage_rung": PRIMARY_RUNG,
            "n_tokens_total": rungs[PRIMARY_RUNG]["total"],
        })
    return out


def selftest():
    recs = [{"metrics": {"rungs": [
        {"coverage_rung": "kernel-v0", "n_covered": 377899, "n_tokens_total": 1709765},
        {"coverage_rung": "molecules-v0", "n_covered": 605599, "n_tokens_total": 1709765},
        {"coverage_rung": "wn31-aligned", "n_covered": 1340670, "n_tokens_total": 1709765},
    ]}}]
    out = analyze(recs)
    a = out["analysis"]
    assert abs(a["coverage_fraction"] - 605599 / 1709765) < 1e-12
    assert abs(a["coverage_fraction"] - 0.354200) < 5e-6
    assert a["coverage_rung"] == "molecules-v0"
    assert a["n_tokens_total"] == 1709765
    assert out["gates"]["instrument_valid"] is True
    # non-monotone ladder -> instrument bug -> gate closed
    bad = [{"metrics": {"rungs": [
        {"coverage_rung": "kernel-v0", "n_covered": 900, "n_tokens_total": 1000},
        {"coverage_rung": "molecules-v0", "n_covered": 100, "n_tokens_total": 1000},
    ]}}]
    assert analyze(bad)["gates"]["instrument_valid"] is False
    assert analyze([])["gates"]["instrument_valid"] is False
    print("m0b selftest OK")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        records = [json.loads(l) for l in sys.stdin if l.strip()]
        print(json.dumps(analyze(records), sort_keys=True))
