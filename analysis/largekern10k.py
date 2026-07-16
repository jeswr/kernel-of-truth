#!/usr/bin/env python3
"""largekern-10k pinned analysis — WordNet-10k GPT-5.6 drafting pilot PROCEED gate.

Design: docs/next/design/gpt56-draft-pipeline-large-kernel.md (r5, GO-TO-FREEZE)
§10.3 frozen endpoints, denominators, decision rule; §10.2 kill ladder; as amended
by the maintainer P7 ruling (kernel-of-truth issue #48, 2026-07-16, option 2):
straight to 10k; the $c = $0.05 per-accepted ceiling is ADVISORY for this one-time
feasibility pilot (reported at equal prominence, never gating); the $500 total API
cap is HARD (atomic pre-submit reservation + kill ladder). ASM-2468/2473/2492/2501.

Eligible FINAL run records on stdin (JSONL); analysis-output JSON on stdout.
The verdict is a pure function of this output + the frozen record (P2 §3.1).

Input metric contract — RAW COUNTS ONLY (P2 §2.4), computed by the runner from
the COMMITTED ledger export (data/kernel-v1-draft/draft-ledger.jsonl) and the
blind endorsement review sheet; micro-pilot rows are EXCLUDED from terminal
counts (spec §5.3) but micro-pilot spend IS included in spend.total_usd:

  metrics.terminal      {accepted, quarantined, provider_failed, worklist_total,
                         nonterminal_rows, unsettled_jobs}
  metrics.usage         {cached_input_tokens, input_tokens_total, output_tokens}
                        (Batch usage sums — the ONLY transport, spec §6.0)
  metrics.spend         {total_usd, cap_usd, reserved_unreleased_usd,
                         micro_pilot_usd}  (ALL pilot API spend: micro-pilot +
                         calibration + every failed/quarantined/repair call)
  metrics.kill_ladder   {aborted}  (true iff any §10.2 checkpoint aborted or the
                         $500 hard-abort fired)
  metrics.human_review  {n_planned, n_reviewed, n_pass, blind}  (blind 4-binary,
                         n = 200 seeded stratified sample; ABSENT in any
                         mechanics-only/mock context — then no PROCEED exists)
  metrics.preconditions {p1_frame, p2_exemplars, p3_micropilot,
                         p4a_shard_benchmark, p4b_record_sizes, p5_crash_tests,
                         p6_preflight, p7_maintainer, p8_family_disjoint}
                        (each a bool attestation that the named §10.6 artifact
                         is on file; P4a/P4b are satisfied INLINE on the run's
                         first real batch per the issue #48 ruling)

Endpoints (spec §10.3 as amended):
  1 accept-rate  alpha = accepted / attempted, attempted = worklist_total −
    provider_failed (PROVIDER_FAILED excluded from attempted, reported
    separately; abstentions / malformed / repair-exhausted stay INSIDE the
    denominator).  Wilson 95% LOWER BOUND, z = 1.96 (two-sided-95% form — the
    form under which the spec's h-floor equivalence "h >= 0.60 <=> observed >=
    134/200" holds EXACTLY; selftested below).  Floor alpha = 0.70.  GATES.
  2 kappa = cached_input_tokens / input_tokens_total (input-only denominator,
    Batch usage sums; deterministic point value).  Floor kappa = 0.70.  GATES.
  3 $/accepted = spend.total_usd / accepted (point value).  $c = $0.05
    ADVISORY (issue #48): /analysis/cost_advisory_breach is reported at equal
    prominence and NEVER gates PROCEED.  The $500 cap stays HARD (gate).
  4 human-pass on the n = 200 blind sample: Wilson 95% LB (z = 1.96), floor
    h = 0.60 (<=> observed >= 134/200).  GATES; N/A in any mock — absence of
    the review block is INSTRUMENT-INVALID, never a PROCEED.

PROCEED (record verdict PASS) iff /gates/instrument_valid AND endpoints 1, 2, 4
hold (/analysis/proceed_gate).  Any floor miss -> FAIL (NO-GO/reassess).
Instrument failure (PROVIDER_FAILED > 2% of worklist, kill-ladder abort,
terminal-accounting mismatch, missing human review, spend over cap, missing
precondition artifact, or not exactly one final record) -> INSTRUMENT-INVALID
(the spec's INVALID-RERUN: no scientific verdict; a re-run needs a fresh id).
The kot-reg/1 single-primary slot rides endpoint 1 (the ASM-2434 unmeasured
volume accept-rate — the thing this pilot exists to measure); the conjunction
lives at /analysis/proceed_gate (the f1k structural pattern).

Output fields:
  /gates/instrument_valid /gates/single_final_record
  /gates/terminal_accounting_ok /gates/provider_failed_ok
  /gates/kill_ladder_clean /gates/budget_within_cap
  /gates/preconditions_ok /gates/human_review_present
  /analysis/attempted /analysis/accept_rate /analysis/accept_rate_wilson_lb
  /analysis/kappa_cache_read /analysis/cost_per_accepted_usd
  /analysis/cost_advisory_breach /analysis/human_pass_observed
  /analysis/human_pass_wilson_lb /analysis/provider_failed_frac
  /analysis/spend_total_usd /analysis/proceed_gate

--selftest: hand-computed fixtures, including the 134/200-passes / 133/200-fails
Wilson equivalence and every INSTRUMENT-INVALID channel.  $0, no network.
"""
import json
import sys

Z95 = 1.96  # two-sided-95% Wilson LB; pins the spec's ">= 134/200" equivalence
WORKLIST_TOTAL = 10000
ALPHA_FLOOR = 0.70
KAPPA_FLOOR = 0.70
COST_ADVISORY_USD = 0.05   # ADVISORY per issue #48 option 2 — never gates
HUMAN_FLOOR = 0.60
HUMAN_N = 200
CAP_USD = 500.0
PROVIDER_FAILED_BOUND = 0.02
PRECONDITION_KEYS = (
    "p1_frame", "p2_exemplars", "p3_micropilot", "p4a_shard_benchmark",
    "p4b_record_sizes", "p5_crash_tests", "p6_preflight", "p7_maintainer",
    "p8_family_disjoint",
)


def wilson_lb(successes, n, z=Z95):
    """Wilson score interval lower bound (z=1.96: two-sided 95%)."""
    if n <= 0:
        return 0.0
    p = successes / n
    z2 = z * z
    centre = p + z2 / (2 * n)
    spread = z * ((p * (1 - p) / n + z2 / (4 * n * n)) ** 0.5)
    return (centre - spread) / (1 + z2 / n)


def _ints(d, keys):
    """Every key present as a non-bool, non-negative int — else None."""
    out = {}
    for k in keys:
        v = d.get(k)
        if isinstance(v, bool) or not isinstance(v, int) or v < 0:
            return None
        out[k] = v
    return out


def analyze(records):
    gates = {
        "single_final_record": len(records) == 1,
        "terminal_accounting_ok": False,
        "provider_failed_ok": False,
        "kill_ladder_clean": False,
        "budget_within_cap": False,
        "preconditions_ok": False,
        "human_review_present": False,
    }
    analysis = {
        "attempted": 0,
        "accept_rate": 0.0,
        "accept_rate_wilson_lb": 0.0,
        "kappa_cache_read": 0.0,
        "cost_per_accepted_usd": None,
        "cost_advisory_breach": False,
        "human_pass_observed": None,
        "human_pass_wilson_lb": None,
        "provider_failed_frac": 1.0,
        "spend_total_usd": None,
        "proceed_gate": False,
    }
    out = {"gates": gates, "analysis": analysis}
    if not gates["single_final_record"]:
        gates["instrument_valid"] = False
        return out
    m = records[0].get("metrics", {})

    # --- terminal accounting (§10.3 PROCEED precondition #0) ---------------
    term = _ints(m.get("terminal", {}), (
        "accepted", "quarantined", "provider_failed", "worklist_total",
        "nonterminal_rows", "unsettled_jobs"))
    if term is not None:
        gates["terminal_accounting_ok"] = (
            term["worklist_total"] == WORKLIST_TOTAL
            and term["accepted"] + term["quarantined"] + term["provider_failed"]
            == term["worklist_total"]
            and term["nonterminal_rows"] == 0
            and term["unsettled_jobs"] == 0)
        analysis["provider_failed_frac"] = (
            term["provider_failed"] / term["worklist_total"]
            if term["worklist_total"] > 0 else 1.0)
        gates["provider_failed_ok"] = (
            analysis["provider_failed_frac"] <= PROVIDER_FAILED_BOUND)
        attempted = term["worklist_total"] - term["provider_failed"]
        analysis["attempted"] = attempted
        if attempted > 0:
            analysis["accept_rate"] = term["accepted"] / attempted
            analysis["accept_rate_wilson_lb"] = wilson_lb(term["accepted"], attempted)

    # --- usage / kappa (Batch usage sums; input-only denominator) ----------
    usage = _ints(m.get("usage", {}), (
        "cached_input_tokens", "input_tokens_total", "output_tokens"))
    if usage is not None and usage["input_tokens_total"] > 0 \
            and usage["cached_input_tokens"] <= usage["input_tokens_total"]:
        analysis["kappa_cache_read"] = (
            usage["cached_input_tokens"] / usage["input_tokens_total"])

    # --- spend / HARD cap / advisory $c -------------------------------------
    spend = m.get("spend", {})
    total_usd = spend.get("total_usd")
    reserved = spend.get("reserved_unreleased_usd")
    if isinstance(total_usd, (int, float)) and not isinstance(total_usd, bool) \
            and isinstance(reserved, (int, float)) and not isinstance(reserved, bool) \
            and total_usd >= 0:
        analysis["spend_total_usd"] = float(total_usd)
        gates["budget_within_cap"] = (
            total_usd <= CAP_USD and reserved == 0
            and spend.get("cap_usd") == CAP_USD)
        if term is not None and term["accepted"] > 0:
            analysis["cost_per_accepted_usd"] = total_usd / term["accepted"]
            analysis["cost_advisory_breach"] = (
                analysis["cost_per_accepted_usd"] > COST_ADVISORY_USD)

    # --- kill ladder ---------------------------------------------------------
    kl = m.get("kill_ladder", {})
    gates["kill_ladder_clean"] = kl.get("aborted") is False

    # --- §10.6 precondition attestations (P4a/P4b inline per issue #48) -----
    pre = m.get("preconditions", {})
    gates["preconditions_ok"] = all(pre.get(k) is True for k in PRECONDITION_KEYS)

    # --- human review (endpoint 4; REQUIRED for any real PROCEED) -----------
    hr = _ints(m.get("human_review", {}), ("n_planned", "n_reviewed", "n_pass"))
    if hr is not None and m.get("human_review", {}).get("blind") is True \
            and hr["n_planned"] == HUMAN_N and hr["n_reviewed"] == HUMAN_N \
            and hr["n_pass"] <= hr["n_reviewed"]:
        gates["human_review_present"] = True
        analysis["human_pass_observed"] = hr["n_pass"] / hr["n_reviewed"]
        analysis["human_pass_wilson_lb"] = wilson_lb(hr["n_pass"], hr["n_reviewed"])

    gates["instrument_valid"] = all((
        gates["single_final_record"], gates["terminal_accounting_ok"],
        gates["provider_failed_ok"], gates["kill_ladder_clean"],
        gates["budget_within_cap"], gates["preconditions_ok"],
        gates["human_review_present"]))

    analysis["proceed_gate"] = bool(
        gates["instrument_valid"]
        and analysis["accept_rate_wilson_lb"] >= ALPHA_FLOOR
        and analysis["kappa_cache_read"] >= KAPPA_FLOOR
        and analysis["human_pass_wilson_lb"] is not None
        and analysis["human_pass_wilson_lb"] >= HUMAN_FLOOR)
    return out


def _fixture(**over):
    m = {
        "terminal": {"accepted": 9521, "quarantined": 453, "provider_failed": 26,
                     "worklist_total": 10000, "nonterminal_rows": 0,
                     "unsettled_jobs": 0},
        "usage": {"cached_input_tokens": 91312000, "input_tokens_total": 105740003,
                  "output_tokens": 8246755},
        "spend": {"total_usd": 382.50, "cap_usd": 500.0,
                  "reserved_unreleased_usd": 0, "micro_pilot_usd": 12.10},
        "kill_ladder": {"aborted": False},
        "human_review": {"n_planned": 200, "n_reviewed": 200, "n_pass": 150,
                         "blind": True},
        "preconditions": {k: True for k in PRECONDITION_KEYS},
    }
    m.update(over)
    return {"metrics": m}


def selftest():
    ok = True

    def check(name, cond):
        nonlocal ok
        print("%s %s" % ("PASS" if cond else "FAIL", name))
        ok = ok and cond

    # Wilson h-floor equivalence (spec §10.3: h = 0.60 WLB <=> >= 134/200).
    check("wilson 134/200 >= 0.60", wilson_lb(134, 200) >= HUMAN_FLOOR)
    check("wilson 133/200 <  0.60", wilson_lb(133, 200) < HUMAN_FLOOR)
    # alpha floor at the e2e-shaped counts: 9521/9974 -> LB ~0.9521-... > 0.70
    check("wilson 9521/9974 > 0.94", wilson_lb(9521, 9974) > 0.94)

    r = analyze([_fixture()])
    check("happy: instrument_valid", r["gates"]["instrument_valid"] is True)
    check("happy: proceed_gate", r["analysis"]["proceed_gate"] is True)
    check("happy: kappa 0.8636", abs(r["analysis"]["kappa_cache_read"] - 0.863551) < 1e-3)
    check("happy: cost advisory not breached at $382.50/9521 (~$0.0402)",
          r["analysis"]["cost_advisory_breach"] is False)

    r = analyze([_fixture(spend={"total_usd": 495.0, "cap_usd": 500.0,
                                 "reserved_unreleased_usd": 0,
                                 "micro_pilot_usd": 12.10})])
    check("advisory: $495/9521 (~$0.052) breaches $c but STILL proceeds",
          r["analysis"]["cost_advisory_breach"] is True
          and r["analysis"]["proceed_gate"] is True)

    r = analyze([_fixture(human_review={"n_planned": 200, "n_reviewed": 200,
                                        "n_pass": 133, "blind": True})])
    check("h 133/200: FAIL path (valid instrument, no proceed)",
          r["gates"]["instrument_valid"] is True
          and r["analysis"]["proceed_gate"] is False)

    r = analyze([_fixture(human_review={})])
    check("human review absent -> INSTRUMENT-INVALID channel",
          r["gates"]["human_review_present"] is False
          and r["gates"]["instrument_valid"] is False
          and r["analysis"]["proceed_gate"] is False)

    r = analyze([_fixture(terminal={"accepted": 9300, "quarantined": 400,
                                    "provider_failed": 300,
                                    "worklist_total": 10000,
                                    "nonterminal_rows": 0, "unsettled_jobs": 0})])
    check("provider_failed 3% -> gate false",
          r["gates"]["provider_failed_ok"] is False
          and r["gates"]["instrument_valid"] is False)

    r = analyze([_fixture(terminal={"accepted": 9521, "quarantined": 453,
                                    "provider_failed": 26,
                                    "worklist_total": 10000,
                                    "nonterminal_rows": 3, "unsettled_jobs": 0})])
    check("nonterminal rows -> terminal accounting false",
          r["gates"]["terminal_accounting_ok"] is False)

    r = analyze([_fixture(kill_ladder={"aborted": True})])
    check("kill-ladder abort -> INSTRUMENT-INVALID channel",
          r["gates"]["kill_ladder_clean"] is False
          and r["gates"]["instrument_valid"] is False)

    r = analyze([_fixture(spend={"total_usd": 501.0, "cap_usd": 500.0,
                                 "reserved_unreleased_usd": 0,
                                 "micro_pilot_usd": 12.10})])
    check("spend over HARD cap -> budget gate false",
          r["gates"]["budget_within_cap"] is False)

    pre = {k: True for k in PRECONDITION_KEYS}
    pre["p4b_record_sizes"] = False
    r = analyze([_fixture(preconditions=pre)])
    check("missing P4b artifact -> preconditions gate false",
          r["gates"]["preconditions_ok"] is False)

    r = analyze([_fixture(), _fixture()])
    check("two final records -> not single_final_record",
          r["gates"]["single_final_record"] is False
          and r["gates"]["instrument_valid"] is False)

    check("string counts rejected (strict ints)",
          analyze([_fixture(terminal={"accepted": "9521", "quarantined": 453,
                                      "provider_failed": 26,
                                      "worklist_total": 10000,
                                      "nonterminal_rows": 0,
                                      "unsettled_jobs": 0})]
                  )["gates"]["terminal_accounting_ok"] is False)

    print("SELFTEST", "OK" if ok else "FAILED")
    return 0 if ok else 1


def main():
    if "--selftest" in sys.argv[1:]:
        sys.exit(selftest())
    records = []
    for line in sys.stdin:
        line = line.strip()
        if line:
            records.append(json.loads(line))
    json.dump(analyze(records), sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
