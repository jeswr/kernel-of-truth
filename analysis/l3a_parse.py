#!/usr/bin/env python3
"""l3a-parse pinned analysis — NL-boundary leg, family/world vertical
(HL3a clause 2; DRAFT record registry/experiments/l3a-parse.json).

Eligible run records on stdin (one JSON per line, kot-log/1 bodies from
tools/experiments/nlb/nlb_instrument.py); analysis-output JSON on stdout.
Derived statistics live HERE and nowhere else (P2 G-4). Self-contained by
design: no shared helper import, so the pinned sha is the complete analysis
artifact (byte-twin of analysis/a5_nl.py with per-record constants).

SHAPE-RECOVERABLE RE-SCOPE (FK-NLB-10, ASM-0420; design doc 14.2/14.6/14.7):
the recoverability audit measured that unmarked English cannot faithfully
render the unique-maker / made-lookup shapes (0.7167 strict recovery; 8/8
genuine shape misses land in exactly those two families). The gated
primary and S2 numerators are therefore scored over the 7 shape-recoverable
IN-SCOPE families only (n_scored = 527), as per-family BUCKET SUMS over the
score_nl by_family enrichment (ASM-0480). The run still EXECUTES all 600
covered phrasings; the 2 dropped families (unique-maker 43, made-lookup 30)
are reported DESCRIPTIVELY in /analysis/shape_ambiguous_stratum, never
gated, carved out of the envelope. Full-run descriptives (parse_ok_rate over
870, label strata, stage breakdown, dev, probe, cost) stay full-run.

Endpoints (design doc section 6 + 14.2, verdict rules in the record):
  primary   retained covered exactness == absolute covered-exact rate over
            the 527 shape-recoverable covered queries (gold ceiling MEASURED
            600/600), one-sided Wilson 95% LB (z=1.645) vs floor 0.90; UB
            feeds the FAIL rule.
  S1/S2     ONE Holm family (m=2, family alpha 0.05): control acceptable
            refusal (> 0.95 over 270, run-level totals unchanged) and covered
            wrong-answer over the 527 in-scope slice (UB < 0.02). Step-down:
            the smaller one-sided score-test p is tested at alpha/2 (Wilson
            bound at z=1.96), the other at alpha (z=1.645) only if the first
            passed. The S2 kill leg (covered_wrong_answer_wilson_lb, z=1.645)
            is exported unadjusted.
  descriptive: shape-ambiguous stratum, stage breakdown, label-verbatim vs
            paraphrase strata, dev abstention, synonym probe (never gated),
            front-end cost, audit-r1 reference.

Instrument gates G1-G6 (any failure => instrument_valid False):
  G1 arm presence + counts + per-family strata match the frozen manifest
     (600 covered / 270 control / 60 dev) PLUS the 14.7 counts-integrity
     extension: in-scope n_scored == 527; every covered family's bucket
     partition exact+wrong+refused_parse+refused_engine == n and exact == ok;
     covered-family bucket sums equal the run-level twins;
  G2 gold-replication parent-perfect (600/600 covered exact, 300/300
     strict-code control, zero wrong/answered);
  G3 phrasing-corpus lint receipt present + green (+ pinned corpus sha match
     once EXPECTED_PHRASINGS_SHA256 is set at freeze);
  G4 dev abstention <= 0.20 (12/60);
  G5 deranged-lexicon retained exactness < 0.10;
  G6 mapper-parse doubled pass byte-identical.

Fixtures (--selftest) sit ON the pre-computed decision boundaries of the
design doc section 14.2 power table (n=527; independently recomputed
2026-07-10): 486/527 -> LB 0.9008 > 0.90 vs 485 -> 0.8987; UB(462) 0.8983
<= 0.90 fires FAIL vs 463 -> 0.9001; S1 Holm-worst 264/270 -> LB(z=1.96)
0.9524 > 0.95 vs 263 -> 0.9475; S2 4/527 -> UB(z=1.96) 0.0194 < 0.02 vs
5 -> 0.0220; S2 kill 16/527 -> LB(z=1.645) 0.0203 >= 0.02 vs 15 -> 0.0187.
The gated numerators are BUCKET SUMS over the 7 in-scope families, so the
boundary fixtures place the varied counts in in-scope families; an isolation
fixture proves a wrong answer in a shape-ambiguous family moves no gate.
"""
import json
import sys

EXPERIMENT = "l3a-parse"
Z_PRIMARY = 1.645   # one-sided 95%, matches kot_common.wilson_lower_bound
Z_HOLM_FIRST = 1.96  # alpha/2 leg of the m=2 Holm step-down
FLOOR = 0.90
S1_GATE = 0.95
S2_GATE = 0.02
DERANGED_MAX = 0.10
DEV_MAX_ABSTENTION = 0.20

PLANNED_COVERED = 600
PLANNED_CONTROL = 270
PLANNED_DEV = 60
# FK-NLB-10 / ASM-0420: the gated slice is the 7 shape-recoverable families
# (n_scored = 527); the 2 shape-ambiguous families are descriptive only.
IN_SCOPE_FAMILIES = ("children-lookup", "count-maker",
                     "instance-false-disjoint", "instance-true",
                     "part-lookup", "unique-father", "unique-mother")
SHAPE_AMBIGUOUS_FAMILIES = ("unique-maker", "made-lookup")
N_SCORED = 527
PLANNED_COVERED_STRATA = {
    "children-lookup": 100, "count-maker": 43, "instance-false-disjoint": 40,
    "instance-true": 50, "made-lookup": 30, "part-lookup": 50,
    "unique-father": 122, "unique-maker": 43, "unique-mother": 122}
PLANNED_CONTROL_STRATA = {
    "conflict": 20, "instance-no-record": 20, "no-record": 60,
    "out-of-scope-rel": 60, "unknown-entity": 40, "unlicensed-count": 30,
    "unlicensed-unique": 40}
GOLD_PERFECT = {"n_covered": 600, "n_covered_exact": 600,
                "n_control": 300, "n_control_refused_correct_code": 300,
                "n_covered_answered_wrong": 0, "n_control_answered": 0}
AUDIT_R1_REF = {
    "path": "data/nlb-phrasings-l3a/audit-recoverability-r1.json",
    "sha256": ("57e9d8d12826ae6ba28da4289fcc703109b2fb"
               "9994ef99eb589655874ea6da6d")}
# EVAL corpus pinned 2026-07-10 (EVAL-BUILD-SPEC step 6): sha256 of
# data/nlb-phrasings-l3a/eval.jsonl, checked against the run's observed
# phrasings_file in G3. None would disable ONLY the sha-equality sub-check.
EXPECTED_PHRASINGS_SHA256 = \
    "832828d892260ee53aff51d648998e3656a2d5dc16b26c55713b638964858d8a"

ARMS = ("mapper-parse", "gold-replication", "deranged-lexicon",
        "abstain-all", "answer-all")


def wilson(p, n, z, upper=False):
    if n <= 0:
        return 1.0 if upper else 0.0
    z2 = z * z
    centre = p + z2 / (2 * n)
    spread = z * ((p * (1 - p) / n + z2 / (4 * n * n)) ** 0.5)
    return (centre + spread if upper else centre - spread) / (1 + z2 / n)


def score_z(p_hat, p0, n, direction):
    """One-sided score-test statistic used ONLY to order the two Holm
    hypotheses (larger z == smaller p). direction 'gt': H1 p > p0;
    'lt': H1 p < p0."""
    se = (p0 * (1 - p0) / n) ** 0.5 if n > 0 else 1.0
    z = (p_hat - p0) / se if se > 0 else 0.0
    return z if direction == "gt" else -z


def analyze(records):
    by_arm = {}
    for r in records:
        if r.get("experiment") not in (None, EXPERIMENT):
            continue
        by_arm[r.get("config", {}).get("arm") or r.get("arm")] = r
    out = {"gates": {"instrument_valid": False}, "analysis": {}}
    mp = by_arm.get("mapper-parse")
    gold = by_arm.get("gold-replication")
    der = by_arm.get("deranged-lexicon")
    if mp is None:
        return out
    m = mp["metrics"]
    nc, ng = m.get("n_covered", 0), m.get("n_control", 0)
    n_exact = m.get("n_covered_exact", 0)
    n_wrong = m.get("n_covered_answered_wrong", 0)
    n_rparse = m.get("n_covered_refused_parse", 0)
    n_rengine = m.get("n_covered_refused_engine", 0)
    n_ctl_acc = m.get("n_control_refused_acceptable", 0)
    dev_n = m.get("dev_n", 0)
    dev_ref = m.get("dev_parse_refused", 0)
    fam = m.get("by_family", {})

    def buck(k, key):
        return fam.get(k, {}).get(key, 0)

    # ---- gated numerators: bucket sums over the 7 in-scope families only
    # (FK-NLB-10, ASM-0420; NOT the run-level totals — the two dropped
    # families' outcomes never enter a gate).
    n_scored = sum(buck(k, "n") for k in IN_SCOPE_FAMILIES)
    exact_in = sum(buck(k, "exact") for k in IN_SCOPE_FAMILIES)
    wrong_in = sum(buck(k, "wrong") for k in IN_SCOPE_FAMILIES)

    # ---- instrument gates
    strata_ok = all(fam.get(k, {}).get("n") == v for k, v in
                    list(PLANNED_COVERED_STRATA.items()) +
                    list(PLANNED_CONTROL_STRATA.items()))
    # 14.7 G1 counts-integrity extension (any failure => instrument-invalid):
    # (i) in-scope n_scored == 527
    scored_ok = (n_scored == N_SCORED)
    # (ii) per covered family the bucket partition holds and exact == ok
    partition_ok = all(
        (buck(k, "exact") + buck(k, "wrong") + buck(k, "refused_parse") +
         buck(k, "refused_engine")) == fam.get(k, {}).get("n") and
        buck(k, "exact") == fam.get(k, {}).get("ok")
        for k in PLANNED_COVERED_STRATA)
    # (iii) covered-family bucket sums equal the run-level twins
    twins_ok = (
        sum(buck(k, "exact") for k in PLANNED_COVERED_STRATA) == n_exact and
        sum(buck(k, "wrong") for k in PLANNED_COVERED_STRATA) == n_wrong and
        sum(buck(k, "refused_parse") for k in PLANNED_COVERED_STRATA)
        == n_rparse and
        sum(buck(k, "refused_engine") for k in PLANNED_COVERED_STRATA)
        == n_rengine)
    g1 = (all(a in by_arm for a in ARMS) and nc == PLANNED_COVERED and
          ng == PLANNED_CONTROL and dev_n == PLANNED_DEV and strata_ok and
          scored_ok and partition_ok and twins_ok)
    gm = gold["metrics"] if gold else {}
    g2 = all(gm.get(k) == v for k, v in GOLD_PERFECT.items())
    lint = (mp.get("pins_observed", {}) or {}).get("phrasings_lint", {})
    g3 = bool(lint.get("green"))
    if EXPECTED_PHRASINGS_SHA256 is not None:
        pf = (mp.get("pins_observed", {}) or {}).get("phrasings_file", {})
        g3 = g3 and pf.get("observed") == EXPECTED_PHRASINGS_SHA256
    g4 = dev_n > 0 and (dev_ref / float(dev_n)) <= DEV_MAX_ABSTENTION
    dm = der["metrics"] if der else {}
    der_rate = (dm.get("n_covered_exact", 0) / float(nc)) if nc else 1.0
    g5 = der_rate < DERANGED_MAX
    g6 = m.get("deterministic_repeat_identical") is True
    out["gates"].update({"g1_counts": g1, "g2_gold_replication": g2,
                         "g3_phrasing_lints": g3, "g4_dev_abstention": g4,
                         "g5_deranged_collapse": g5, "g6_determinism": g6})
    out["gates"]["instrument_valid"] = all((g1, g2, g3, g4, g5, g6))

    # ---- primary (retained == absolute over the 527 in-scope slice;
    # measured gold ceiling 600/600)
    a = out["analysis"]
    cov = exact_in / float(N_SCORED) if N_SCORED else 0.0
    a["n_covered_run"] = nc          # 600 executed (replaces n_covered)
    a["n_covered_scored"] = N_SCORED  # 527 gated (FK-NLB-10)
    a["n_control"], a["n_dev"] = ng, dev_n
    a["retained_covered_exact_rate"] = cov
    a["retained_covered_exact_wilson_lb"] = wilson(cov, N_SCORED, Z_PRIMARY)
    a["retained_covered_exact_wilson_ub"] = wilson(cov, N_SCORED, Z_PRIMARY,
                                                   True)

    # ---- secondaries (one Holm family, m=2): S1 run-level over 270,
    # S2 over the 527 in-scope slice
    ctl = n_ctl_acc / float(ng) if ng else 0.0
    wrong = wrong_in / float(N_SCORED) if N_SCORED else 1.0
    a["control_refusal_acceptable_rate"] = ctl
    a["control_refusal_acceptable_wilson_lb"] = wilson(ctl, ng, Z_PRIMARY)
    a["control_refusal_strict_engine_code_rate"] = (
        m.get("n_control_refused_strict_engine_code", 0) / float(ng)
        if ng else 0.0)
    a["covered_wrong_answer_rate"] = wrong
    a["covered_wrong_answer_wilson_ub"] = wilson(wrong, N_SCORED, Z_PRIMARY,
                                                 True)
    a["covered_wrong_answer_wilson_lb"] = wilson(wrong, N_SCORED, Z_PRIMARY)

    def s1_pass_at(z):
        return wilson(ctl, ng, z) > S1_GATE

    def s2_pass_at(z):
        return wilson(wrong, N_SCORED, z, upper=True) < S2_GATE

    z_s1 = score_z(ctl, S1_GATE, ng, "gt")
    z_s2 = score_z(wrong, S2_GATE, N_SCORED, "lt")
    if z_s1 >= z_s2:  # S1 has the smaller p -> tested at alpha/2
        s1 = s1_pass_at(Z_HOLM_FIRST)
        s2 = s1 and s2_pass_at(Z_PRIMARY)
    else:
        s2 = s2_pass_at(Z_HOLM_FIRST)
        s1 = s2 and s1_pass_at(Z_PRIMARY)
    a["holm_s1_pass"] = bool(s1)
    a["holm_s2_pass"] = bool(s2)

    # ---- shape-ambiguous stratum (FK-NLB-10, ASM-0420): DESCRIPTIVE ONLY,
    # never gated, carved out of the envelope.
    sa = {k: {"n": buck(k, "n"), "exact": buck(k, "exact"),
              "wrong": buck(k, "wrong"),
              "refused_parse": buck(k, "refused_parse"),
              "refused_engine": buck(k, "refused_engine"),
              "exact_rate": (buck(k, "exact") / float(buck(k, "n")))
              if buck(k, "n") else None}
          for k in SHAPE_AMBIGUOUS_FAMILIES}
    sa["note"] = ("descriptive only; never gated; carved out of the "
                  "envelope (FK-NLB-10, ASM-0420)")
    a["shape_ambiguous_stratum"] = sa
    a["audit_r1_ref"] = dict(AUDIT_R1_REF)

    # ---- baselines / instruments (descriptive; full-run unless noted)
    a["gold_replication_identical"] = bool(g2)
    a["deranged_retained_exact_rate"] = der_rate
    a["dev_abstention_rate"] = (dev_ref / float(dev_n)) if dev_n else 1.0
    n_parse_ref = (m.get("n_covered_refused_parse", 0) +
                   m.get("n_control_refused_parse", 0))
    a["parse_ok_rate"] = (1.0 - n_parse_ref / float(nc + ng)) \
        if (nc + ng) else 0.0
    a["parse_stage_breakdown"] = m.get("parse_stage_breakdown", {})
    ls = m.get("label_strata")
    if ls:
        a["label_verbatim_vs_paraphrase"] = {
            k: {"n": v["n"], "exact": v["exact"],
                "exact_rate": (v["exact"] / float(v["n"])) if v["n"] else None}
            for k, v in ls.items()}
    else:
        a["label_verbatim_vs_paraphrase"] = None
    if m.get("probe_n"):
        a["synonym_probe"] = {
            "probe_n": m["probe_n"], "probe_parse_ok": m["probe_parse_ok"],
            "probe_exact": m["probe_exact"],
            "parse_ok_rate": m["probe_parse_ok"] / float(m["probe_n"]),
            "exact_rate": m["probe_exact"] / float(m["probe_n"]),
            "note": "descriptive only; never gated (FK-NLB-8)"}
    else:
        a["synonym_probe"] = None
    a["frontend_mean_us_per_query"] = (
        m.get("frontend_total_ns", 0) / float(nc + ng) / 1000.0
        if (nc + ng) else 0.0)
    return out


def _fam(n, exact=None, wrong=0, rparse=0, rengine=0):
    """One covered family's enriched bucket record; exact defaults to the
    residual so the partition exact+wrong+refused_parse+refused_engine == n
    holds and exact == ok."""
    if exact is None:
        exact = n - wrong - rparse - rengine
    return {"n": n, "ok": exact, "exact": exact, "wrong": wrong,
            "refused_parse": rparse, "refused_engine": rengine}


def _rec(arm, covered=None, control_accept=270, control_strict=230,
         control_parse=40, **kw):
    # Covered families default to all-exact; `covered` overrides named
    # families with explicit buckets (run-level covered twins are DERIVED
    # from by_family so G1 twins-integrity holds by construction).
    cov = {k: _fam(v) for k, v in PLANNED_COVERED_STRATA.items()}
    for k, b in (covered or {}).items():
        assert b["n"] == PLANNED_COVERED_STRATA[k], (k, b)
        cov[k] = b
    fam = dict(cov)
    for k, v in PLANNED_CONTROL_STRATA.items():
        fam[k] = {"n": v, "ok": v, "exact": 0, "wrong": 0,
                  "refused_parse": 0, "refused_engine": 0}
    ce = sum(cov[k]["exact"] for k in cov)
    cw = sum(cov[k]["wrong"] for k in cov)
    cp = sum(cov[k]["refused_parse"] for k in cov)
    cg = sum(cov[k]["refused_engine"] for k in cov)
    m = {"n_covered": 600, "n_covered_exact": ce,
         "n_covered_refused_parse": cp, "n_covered_refused_engine": cg,
         "n_covered_answered_wrong": cw, "n_control": 270,
         "n_control_refused_acceptable": control_accept,
         "n_control_refused_strict_engine_code": control_strict,
         "n_control_refused_parse": control_parse, "n_control_refused_other": 0,
         "n_control_answered": 0, "n_control_refused_any": control_accept,
         "by_family": fam, "parse_stage_breakdown": {},
         "label_strata": {"verbatim": {"n": 300, "exact": 300},
                          "paraphrase": {"n": 300, "exact": 300}},
         "dev_n": 60, "dev_parse_refused": 7,
         "deterministic_repeat_identical": True,
         "frontend_total_ns": 600000000}
    m.update(kw)
    body = {"experiment": EXPERIMENT, "config": {"arm": arm}, "metrics": m,
            "pins_observed": {"phrasings_lint": {"green": True},
                              "phrasings_file":
                              {"observed": EXPECTED_PHRASINGS_SHA256}}}
    if arm == "gold-replication":
        body["metrics"] = dict(GOLD_PERFECT)
        body["metrics"]["deterministic_repeat_identical"] = True
    if arm == "deranged-lexicon":
        m2 = dict(m)
        m2.update({"n_covered_exact": 0, "n_covered_answered_wrong": 20})
        body["metrics"] = m2
    return body


def _suite(**mp_kw):
    return [_rec("mapper-parse", **mp_kw), _rec("gold-replication"),
            _rec("deranged-lexicon"), _rec("abstain-all"),
            _rec("answer-all")]


def selftest():
    base = analyze(_suite())
    assert base["gates"]["instrument_valid"] is True, base["gates"]
    a = base["analysis"]
    assert a["n_covered_run"] == 600 and a["n_covered_scored"] == 527, a
    assert a["retained_covered_exact_rate"] == 1.0
    assert a["holm_s1_pass"] and a["holm_s2_pass"]
    assert a["synonym_probe"] is None
    # shape-ambiguous stratum present, descriptive, all-exact in the base
    assert a["shape_ambiguous_stratum"]["unique-maker"]["n"] == 43
    assert a["shape_ambiguous_stratum"]["made-lookup"]["n"] == 30
    assert a["audit_r1_ref"]["sha256"].startswith("57e9d8d1")
    # primary decision boundary (section 14.2 table, n=527): the varied
    # counts sit in an IN-SCOPE family (unique-father) as refusals.
    hi = analyze(_suite(covered={"unique-father": _fam(122, exact=81,
                                                       rparse=41)}))["analysis"]
    lo = analyze(_suite(covered={"unique-father": _fam(122, exact=80,
                                                       rparse=42)}))["analysis"]
    assert hi["retained_covered_exact_wilson_lb"] > FLOOR, hi
    assert lo["retained_covered_exact_wilson_lb"] <= FLOOR, lo
    kill = analyze(_suite(covered={"unique-father": _fam(122, exact=57,
                                                         rparse=65)}))
    nokill = analyze(_suite(covered={"unique-father": _fam(122, exact=58,
                                                           rparse=64)}))
    assert kill["analysis"]["retained_covered_exact_wilson_ub"] <= FLOOR, kill
    assert nokill["analysis"]["retained_covered_exact_wilson_ub"] > FLOOR, \
        nokill
    # S1 boundary at the HOLM-WORST level: with S2 at 5/527 (z ~1.72), S1
    # wins the ordering at both 264/270 (z ~2.09) and 263/270 (z ~1.81) and
    # is therefore tested at alpha/2 (z=1.96) — 264 passes, 263 fails (and
    # blocks S2). w=5 is the unique in-scope wrong count that keeps S1 first
    # AND lets S2 pass at nominal when S1 passes (UB(5/527,1.645)=0.0194).
    s1hi = analyze(_suite(control_accept=264,
                          covered={"unique-father": _fam(122, exact=117,
                                                         wrong=5)}))["analysis"]
    s1lo = analyze(_suite(control_accept=263,
                          covered={"unique-father": _fam(122, exact=117,
                                                         wrong=5)}))["analysis"]
    assert s1hi["holm_s1_pass"] is True and s1hi["holm_s2_pass"] is True, s1hi
    assert s1lo["holm_s1_pass"] is False and s1lo["holm_s2_pass"] is False, \
        s1lo
    # S1 at the nominal-alpha leg (S2 dominant at 0/527): 263/270 passes
    s1nom = analyze(_suite(control_accept=263))["analysis"]
    assert s1nom["holm_s1_pass"] is True, s1nom
    # S2 Holm-worst boundary (4 vs 5 wrong at z=1.96), asserted directly
    assert wilson(4 / 527.0, 527, Z_HOLM_FIRST, True) < S2_GATE
    assert wilson(5 / 527.0, 527, Z_HOLM_FIRST, True) > S2_GATE
    s2a = analyze(_suite(covered={"unique-father": _fam(122, exact=118,
                                                        wrong=4)}))["analysis"]
    assert s2a["holm_s2_pass"] is True, s2a
    # S2 kill boundary, unadjusted z=1.645 (fires from 16/527)
    s2c = analyze(_suite(covered={"unique-father": _fam(122, exact=106,
                                                        wrong=16)}))["analysis"]
    s2d = analyze(_suite(covered={"unique-father": _fam(122, exact=107,
                                                        wrong=15)}))["analysis"]
    assert s2c["covered_wrong_answer_wilson_lb"] >= S2_GATE, s2c
    assert s2d["covered_wrong_answer_wilson_lb"] < S2_GATE, s2d
    # Holm step-down: a failed first hypothesis blocks the second
    both = analyze(_suite(control_accept=200))["analysis"]
    assert both["holm_s1_pass"] is False and both["holm_s2_pass"] is True, both
    # ISOLATION (14.7 step 5): a wrong answer in a SHAPE-AMBIGUOUS family
    # moves NO gate and NO gated numerator; it appears ONLY in the
    # shape_ambiguous_stratum descriptive.
    iso = analyze(_suite(covered={"unique-maker": _fam(43, exact=33,
                                                       wrong=10)}))
    ia = iso["analysis"]
    assert iso["gates"]["instrument_valid"] is True, iso["gates"]
    assert ia["retained_covered_exact_rate"] == 1.0, ia
    assert ia["covered_wrong_answer_rate"] == 0.0, ia
    assert ia["holm_s2_pass"] is True, ia
    assert ia["shape_ambiguous_stratum"]["unique-maker"]["wrong"] == 10, ia
    assert ia["shape_ambiguous_stratum"]["made-lookup"]["wrong"] == 0, ia
    # G1 counts-integrity: a broken bucket partition => instrument-invalid
    broken = analyze(_suite(covered={"unique-father": {
        "n": 122, "ok": 122, "exact": 100, "wrong": 0,
        "refused_parse": 0, "refused_engine": 0}}))
    assert broken["gates"]["instrument_valid"] is False, broken["gates"]
    assert broken["gates"]["g1_counts"] is False, broken["gates"]
    # gates: broken determinism / deranged leak / missing lint / dev gate
    bad = analyze(_suite(deterministic_repeat_identical=False))
    assert bad["gates"]["instrument_valid"] is False
    recs = _suite()
    recs[2]["metrics"]["n_covered_exact"] = 100
    assert analyze(recs)["gates"]["g5_deranged_collapse"] is False
    recs = _suite()
    recs[0]["pins_observed"] = {}
    assert analyze(recs)["gates"]["g3_phrasing_lints"] is False
    recs = _suite()
    recs[0]["metrics"]["dev_parse_refused"] = 13
    assert analyze(recs)["gates"]["g4_dev_abstention"] is False
    print("l3a-parse selftest OK")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        records = [json.loads(l) for l in sys.stdin if l.strip()]
        print(json.dumps(analyze(records), sort_keys=True))
