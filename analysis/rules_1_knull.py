#!/usr/bin/env python3
"""rules-1-knull-ablation pre-registered analysis (pure function).

Design: docs/next/design/rules-1-knull-ablation.md (MD-7 / c5 realisation,
PROPOSED-ASM-1138 as resolved by this record; PROPOSED-ASM-1400..1419).

Inputs (all produced by poc/rules-1-knull/ablation_runner.py unless noted):
  --record        registry/experiments/rules-1-knull-ablation.json — the
                  REGISTERED digest source; every payload's attestation is
                  checked against it (ASM-1413): unattested or drifted
                  payloads => /gates/harness_pins_valid false.
  --k0-identity   k0-staging-identity.json  (ASM-1405 gate report)
  --k1            k1-certificate-result.json (knull-plain substituted run)
  --k2            k2-certificate-result.json (Sattolo-scrambled run)
  --lint          poc/rules-1-knull/inputs/lint-report.json (ASM-1402)
  --smoke         poc/rules-1-knull/inputs/parse-smoke.json (ASM-1414,
                  parse-only pre-freeze smoke)
  --mapping-review poc/rules-1-knull/inputs/mapping-review.json (ASM-1415,
                  independent definition->constraint mapping review)
  --parent-analysis OPTIONAL rules-1 pinned analysis output JSON; the
                  phase-2b leg is ACTIVATED only when its
                  /analysis/primary_pass is true (ASM-1407/1417).
  --hostlift      OPTIONAL phase-2b host-lift JSON (ASM-1407): per-item rows
                  for A1/A3 under kernel and knull TBoxes; absent => every
                  hostlift field is null (unevaluable, never a fail).

SURVIVAL PREDICATE (pinned, identical to the rules-1 certificate
precondition): success_asm_1131 AND gates_asm_1163_all_pass AND NOT
kill_a_fired.  k1 satisfying it => the non-inertness result SURVIVES the
knull substitution (verdict NULL: kernel necessity UNSHOWN against this one
plain-dictionary compilation channel); k1 failing it while every instrument
gate holds => COLLAPSE (verdict PASS =
KERNEL-ADVANTAGE-OVER-THIS-KNULL-COMPILATION).  A k1 load/run failure is
INSTRUMENT-INVALID (ASM-1408), never a collapse.

DISCRIMINATION GATE (ASM-1404/1412, review fix 3):
/gates/discrimination_valid = k2_tbox_loads AND NOT k2_certificate_success.
A k2 parse/load failure resolves INSTRUMENT-INVALID via /gates/k2_tbox_loads
— NEVER "successful discrimination": a trivially-unparseable scrambled
ruleset cannot masquerade as content sensitivity.

Phase-2b statistics (ASM-1407/1417): exactly 858 paired items x 3 seeds x
all four (host_tbox x host_arm) cells required — duplicates or missing rows
REJECT (rows_valid false, all stats null); per-item seed-averaged means;
paired BCa bootstrap B=10000, PRNG seed 20260712; Holm within {h1,h2} on
bootstrap p-values; TOST margin 0.05.
"""

import argparse
import json
import math
import random

OUTPUT_FIELDS = [
    "/gates/harness_pins_valid",
    "/gates/staging_identity_valid",
    "/gates/compilation_lint_valid",
    "/gates/k1_tbox_loads",
    "/gates/k2_tbox_loads",
    "/gates/discrimination_valid",
    "/analysis/k1_certificate_success",
    "/analysis/k1_survives",
    "/analysis/k1_collapses",
    "/analysis/k1_failure_mode",
    "/analysis/k1_cdec_stated",
    "/analysis/k1_cdec_entailed",
    "/analysis/k1_e3_wilson_lb",
    "/analysis/k1_e1_wilson_lb",
    "/analysis/k1_e5_refusal_wilson_lb",
    "/analysis/k1_gates_1163_pass",
    "/analysis/k1_kill_a_fired",
    "/analysis/k1_double_run_sha_match",
    "/analysis/k2_certificate_success",
    "/analysis/k2_cdec_stated",
    "/analysis/k2_e3_wilson_lb",
    "/analysis/k2_failure_mode",
    "/analysis/hostlift_ran",
    "/analysis/hostlift_parent_primary_pass",
    "/analysis/hostlift_rows_valid",
    "/analysis/hostlift_knull_lift_lb95",
    "/analysis/hostlift_knull_lift_pass",
    "/analysis/hostlift_kernel_minus_knull_ci90",
    "/analysis/hostlift_equiv_tost_pass",
    "/analysis/hostlift_h1_p",
    "/analysis/hostlift_h2_p",
    "/analysis/hostlift_holm_order",
    "/analysis/mock",
]

B = 10000
SEED = 20260712
TOST_MARGIN = 0.05
ALPHA = 0.05
N_ITEMS = 858
SEEDS = (0, 1, 2)
TBOXES = ("kernel", "knull")
ARMS = ("A1", "A3")


def survival(payload):
    cr = payload.get("certificate_result", {})
    return bool(cr.get("success_asm_1131") and
                cr.get("gates_asm_1163_all_pass") and
                not cr.get("kill_a_fired"))


def failure_mode(payload):
    if payload.get("run_failed"):
        return "load_or_run_failure (rc=%s)" % payload.get("returncode")
    cr = payload.get("certificate_result", {})
    g = payload.get("grid", {})
    es = payload.get("engine_soundness", {})
    modes = []
    if g.get("C_dec_stated") != 1.0:
        modes.append("stated_cells_not_exact")
    if g.get("C_dec_entailed") == 1.0:
        modes.append("entailed_cells_projection_reproducible")
    e3 = es.get("e3_vs_third_party_clutrr_gold", {})
    if e3.get("wilson_lb95", 0.0) < 0.98:
        modes.append("e3_soundness_below_bar")
    if not cr.get("gates_asm_1163_all_pass"):
        modes.append("counterfactual_gates_failed")
    if cr.get("kill_a_fired"):
        modes.append("kill_a")
    return ";".join(modes) if modes else None


def attestation_valid(payload, arm, record):
    """ASM-1413 (review fix 2): reject unattested or post-freeze-drifted
    payloads. The attestation must name THIS record, THIS arm, carry the
    pinned rules-1 harness shas, and (k1/k2) the registered TBox dir-digest
    both as the registered pin AND as the recomputed source digest."""
    at = payload.get("attestation")
    if not isinstance(at, dict):
        return False
    ah = record.get("pins", {}).get("artifact_hashes", {})
    pin_key = {
        "k1": "tbox-knull(dir-digest, kot-corpus-hash/1 recipe over "
              "poc/rules-1-knull/inputs/tbox-knull)",
        "k2": "tbox-scrambled(dir-digest, kot-corpus-hash/1 recipe over "
              "poc/rules-1-knull/inputs/tbox-scrambled)",
    }.get(arm)
    ok = (at.get("record_id") == record.get("id") and
          at.get("arm") == arm and
          isinstance(at.get("harness_sha256"), dict) and
          at["harness_sha256"].get("certificate.py") ==
          ah.get("rules1-certificate-py(poc/rules-1/certificate.py)") and
          at["harness_sha256"].get("twin_engine.py") ==
          ah.get("rules1-twin-engine(poc/rules-1/twin_engine.py)") and
          at.get("pinned_decision_payload_sha256") ==
          ah.get("rules1-decision-payload-sha256"))
    if not ok:
        return False
    if pin_key is not None:
        want = ah.get(pin_key)
        tb = at.get("tbox") or {}
        if not (isinstance(tb, dict) and want and
                tb.get("registered_pin") == want and
                tb.get("source_dir_digest") == want):
            return False
    return True


def bca(diffs, rng, lo_q, hi_q):
    """BCa bootstrap CI over per-item paired differences; also returns the
    bootstrap distribution for p-value computation."""
    n = len(diffs)
    mean = sum(diffs) / n
    boots = []
    for _ in range(B):
        s = 0.0
        for _ in range(n):
            s += diffs[rng.randrange(n)]
        boots.append(s / n)
    boots.sort()
    prop = sum(1 for b_ in boots if b_ < mean) / B
    prop = min(max(prop, 1.0 / B), 1 - 1.0 / B)
    z0 = _ppf(prop)
    jack = [(sum(diffs) - d) / (n - 1) for d in diffs]
    jm = sum(jack) / n
    num = sum((jm - j) ** 3 for j in jack)
    den = 6.0 * (sum((jm - j) ** 2 for j in jack) ** 1.5)
    a = num / den if den else 0.0

    def q(alpha):
        z = _ppf(alpha)
        adj = z0 + (z0 + z) / (1 - a * (z0 + z))
        p = _cdf(adj)
        idx = min(max(int(p * B), 0), B - 1)
        return boots[idx]
    return q(lo_q), q(hi_q), mean, boots


def _cdf(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def _ppf(p):
    lo, hi = -10.0, 10.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if _cdf(mid) < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def validate_rows(rows):
    """ASM-1417 (review fix): EXACT design grid required — 858 unique items,
    each with all 12 (tbox x arm x seed) cells, no duplicates, no extras,
    correct in {0,1}. Anything else => rows_valid false, all stats null
    (complete-case dropping is a preregistration violation)."""
    seen = set()
    items = set()
    for r in rows:
        key = (r.get("item_id"), r.get("tbox"), r.get("arm"), r.get("seed"))
        if (key in seen or r.get("tbox") not in TBOXES or
                r.get("arm") not in ARMS or r.get("seed") not in SEEDS or
                r.get("correct") not in (0, 1)):
            return False, None
        seen.add(key)
        items.add(r["item_id"])
    if len(items) != N_ITEMS:
        return False, None
    if len(seen) != N_ITEMS * len(TBOXES) * len(ARMS) * len(SEEDS):
        return False, None
    for it in items:
        for t in TBOXES:
            for a in ARMS:
                for s in SEEDS:
                    if (it, t, a, s) not in seen:
                        return False, None
    return True, sorted(items)


def hostlift(path):
    """Phase-2b (ASM-1407/1417). Input JSON: {"rows": [{item_id, tbox in
    {kernel,knull}, arm in {A1,A3}, seed, correct}]}. Paired per-item
    seed-averaged lifts; BCa B=10000 seed 20260712; Holm within {h1,h2} on
    one-sided bootstrap p-values; TOST margin 0.05. The (kernel, A1) and
    (kernel, A3) rows are REUSED verbatim from the frozen rules-1 campaign
    run-records (never regenerated); the knull cells are fresh."""
    doc = json.loads(open(path).read())
    rows = doc["rows"]
    rows_valid, items = validate_rows(rows)
    if not rows_valid:
        return {"rows_valid": False}
    acc = {}
    for r in rows:
        acc.setdefault((r["tbox"], r["arm"], r["item_id"]), []).append(
            r["correct"])

    def m(tbox, arm, it):
        v = acc[(tbox, arm, it)]
        return sum(v) / len(v)

    knull_diffs, gap_diffs = [], []
    for it in items:
        vals = {(t, a): m(t, a, it) for t in TBOXES for a in ARMS}
        knull_diffs.append(vals[("knull", "A3")] - vals[("knull", "A1")])
        gap_diffs.append((vals[("kernel", "A3")] - vals[("kernel", "A1")]) -
                         (vals[("knull", "A3")] - vals[("knull", "A1")]))
    rng = random.Random(SEED)
    lb95, _, _, boots1 = bca(knull_diffs, rng, 0.05, 0.95)
    rng = random.Random(SEED + 1)
    lo90, hi90, _, boots2 = bca(gap_diffs, rng, 0.05, 0.95)  # two 5% tails
    # bootstrap p-values (add-one smoothing): h1 one-sided H0: lift <= 0;
    # h2 TOST p = max of the two one-sided interval hypotheses.
    p1 = (1 + sum(1 for b_ in boots1 if b_ <= 0.0)) / (B + 1)
    p2_hi = (1 + sum(1 for b_ in boots2 if b_ >= TOST_MARGIN)) / (B + 1)
    p2_lo = (1 + sum(1 for b_ in boots2 if b_ <= -TOST_MARGIN)) / (B + 1)
    p2 = max(p2_hi, p2_lo)
    # Holm within {h1, h2} (registered): smallest p tested at alpha/2, the
    # other at alpha only if the first rejects.
    ps = sorted([("h1", p1), ("h2", p2)], key=lambda t: t[1])
    holm = {}
    thresholds = [ALPHA / 2, ALPHA]
    alive = True
    for (name, p), th in zip(ps, thresholds):
        holm[name] = bool(alive and p < th)
        alive = holm[name]
    # pass = the registered CI criterion AND the Holm-adjusted rejection
    return {
        "rows_valid": True,
        "knull_lift_lb95": lb95,
        "knull_lift_pass": bool(lb95 > 0 and holm["h1"]),
        "kernel_minus_knull_ci90": [lo90, hi90],
        "equiv_tost_pass": bool(-TOST_MARGIN < lo90 and hi90 < TOST_MARGIN
                                and holm["h2"]),
        "h1_p": p1,
        "h2_p": p2,
        "holm_order": [name for name, _ in ps],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--record", required=True,
                    help="registry/experiments/rules-1-knull-ablation.json")
    ap.add_argument("--k0-identity", required=True)
    ap.add_argument("--k1", required=True)
    ap.add_argument("--k2", required=True)
    ap.add_argument("--lint", required=True)
    ap.add_argument("--smoke", required=True)
    ap.add_argument("--mapping-review", required=True)
    ap.add_argument("--parent-analysis",
                    help="rules-1 pinned analysis output; phase-2b activates "
                         "only on /analysis/primary_pass true (ASM-1417)")
    ap.add_argument("--hostlift")
    args = ap.parse_args()

    record = json.loads(open(args.record).read())
    k0 = json.loads(open(args.k0_identity).read())
    k1 = json.loads(open(args.k1).read())
    k2 = json.loads(open(args.k2).read())
    lint = json.loads(open(args.lint).read())
    smoke = json.loads(open(args.smoke).read())
    mapping = json.loads(open(args.mapping_review).read())
    parent = (json.loads(open(args.parent_analysis).read())
              if args.parent_analysis else None)
    hl_doc = json.loads(open(args.hostlift).read()) if args.hostlift else None

    mock = bool(k1.get("MOCK") or k2.get("MOCK") or k0.get("MOCK") or
                (k1.get("attestation") or {}).get("MOCK") or
                (k2.get("attestation") or {}).get("MOCK") or
                (hl_doc or {}).get("MOCK") or
                (parent or {}).get("MOCK"))
    staging = bool(k0.get("pass"))
    # harness pins (ASM-1413): the runner fail-closes on any pin mismatch
    # BEFORE a result exists, AND every payload must carry an attestation
    # naming this record/arm with the registered harness shas + TBox
    # dir-digests. Unattested or drifted payloads are REJECTED here — a
    # payload produced off the registered inputs can never be graded.
    k0_at = attestation_valid(k0, "k0", record)
    pins_valid = (staging and k0_at and
                  attestation_valid(k1, "k1", record) and
                  attestation_valid(k2, "k2", record))
    # compilation-fidelity gate (ASM-1402/1414/1415, review fix 4): the
    # span lint alone does not establish a competent comparator — the
    # pre-freeze parse-only smoke AND the independent definition->constraint
    # mapping review are mandatory components.
    lint_valid = bool(lint.get("pass") and smoke.get("pass") and
                      mapping.get("pass"))
    k1_loads = not k1.get("run_failed", True)
    k2_loads = not k2.get("run_failed", True)
    k1_success = survival(k1) if k1_loads else False
    k2_success = survival(k2) if k2_loads else False
    # discrimination (ASM-1404/1412, review fix 3): the scrambled arm must
    # LOAD and then fail the survival predicate. k2 surviving => the
    # certificate cannot distinguish content => INSTRUMENT-INVALID. k2
    # FAILING TO LOAD => /gates/k2_tbox_loads false => INSTRUMENT-INVALID
    # (an unparseable comparator proves nothing about content sensitivity
    # and must never read as successful discrimination).
    discrimination = bool(k2_loads and not k2_success)

    gates_all = (pins_valid and staging and lint_valid and k1_loads and
                 k2_loads and discrimination)
    k1_survives = bool(gates_all and k1_success)
    k1_collapses = bool(gates_all and not k1_success)

    # phase-2b (ASM-1407/1417): activated ONLY when the pinned parent
    # rules-1 analysis carries /analysis/primary_pass true.
    parent_pp = (bool(parent.get("/analysis/primary_pass"))
                 if parent is not None else None)
    hl = None
    if hl_doc is not None and parent_pp:
        hl = hostlift(args.hostlift)
    hl_rows_valid = (hl.get("rows_valid") if hl is not None
                     else (False if hl_doc is not None and parent_pp
                           else None))
    hl_ok = bool(hl and hl.get("rows_valid"))

    def g(payload, *path, default=None):
        cur = payload
        for k in path:
            if not isinstance(cur, dict) or k not in cur:
                return default
            cur = cur[k]
        return cur

    out = {
        "/gates/harness_pins_valid": pins_valid,
        "/gates/staging_identity_valid": staging,
        "/gates/compilation_lint_valid": lint_valid,
        "/gates/k1_tbox_loads": k1_loads,
        "/gates/k2_tbox_loads": k2_loads,
        "/gates/discrimination_valid": discrimination,
        "/analysis/k1_certificate_success": k1_success,
        "/analysis/k1_survives": k1_survives,
        "/analysis/k1_collapses": k1_collapses,
        "/analysis/k1_failure_mode": failure_mode(k1) if k1_loads or
            k1.get("run_failed") else None,
        "/analysis/k1_cdec_stated": g(k1, "grid", "C_dec_stated"),
        "/analysis/k1_cdec_entailed": g(k1, "grid", "C_dec_entailed"),
        "/analysis/k1_e3_wilson_lb": g(k1, "engine_soundness",
                                       "e3_vs_third_party_clutrr_gold",
                                       "wilson_lb95"),
        "/analysis/k1_e1_wilson_lb": g(k1, "engine_soundness",
                                       "e1_vs_held_out_world_v0_edge",
                                       "wilson_lb95"),
        "/analysis/k1_e5_refusal_wilson_lb": g(k1, "engine_soundness",
                                               "e5_control_refusal",
                                               "wilson_lb95"),
        "/analysis/k1_gates_1163_pass": g(k1, "certificate_result",
                                          "gates_asm_1163_all_pass"),
        "/analysis/k1_kill_a_fired": g(k1, "certificate_result",
                                       "kill_a_fired"),
        "/analysis/k1_double_run_sha_match": g(k1, "determinism",
                                               "double_run_sha_match"),
        "/analysis/k2_certificate_success": k2_success,
        "/analysis/k2_cdec_stated": g(k2, "grid", "C_dec_stated"),
        "/analysis/k2_e3_wilson_lb": g(k2, "engine_soundness",
                                       "e3_vs_third_party_clutrr_gold",
                                       "wilson_lb95"),
        "/analysis/k2_failure_mode": failure_mode(k2),
        "/analysis/hostlift_ran": hl_ok,
        "/analysis/hostlift_parent_primary_pass": parent_pp,
        "/analysis/hostlift_rows_valid": hl_rows_valid,
        "/analysis/hostlift_knull_lift_lb95":
            hl["knull_lift_lb95"] if hl_ok else None,
        "/analysis/hostlift_knull_lift_pass":
            hl["knull_lift_pass"] if hl_ok else None,
        "/analysis/hostlift_kernel_minus_knull_ci90":
            hl["kernel_minus_knull_ci90"] if hl_ok else None,
        "/analysis/hostlift_equiv_tost_pass":
            hl["equiv_tost_pass"] if hl_ok else None,
        "/analysis/hostlift_h1_p": hl["h1_p"] if hl_ok else None,
        "/analysis/hostlift_h2_p": hl["h2_p"] if hl_ok else None,
        "/analysis/hostlift_holm_order": hl["holm_order"] if hl_ok else None,
        "/analysis/mock": mock,
    }
    assert set(out.keys()) == set(OUTPUT_FIELDS), "output-field drift"
    print(json.dumps(out, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
