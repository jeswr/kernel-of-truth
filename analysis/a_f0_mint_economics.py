#!/usr/bin/env python3
"""a_f0_mint_economics — pinned analysis for registry experiment a-f0-mint-economics.

    python3 analysis/a_f0_mint_economics.py [--input poc/a-f0/results/run-log.jsonl]

Pure function: reads the runner's raw per-call / per-concept log, emits the
declared output-field JSON on stdout. No network, no randomness, stdlib only.
Every USD figure is usage-fields x the frozen price table below (ASM-0601);
raw usage is never discarded, so costs are reconvertible under a corrected
table by re-running this script only.

Input: one JSON object per line, three kinds (spec docs/next/
a-f0-mint-economics-spec.md S7):

  {"kind":"meta", "prefix_token_count":{"ad":int,"bc":int}, "aborted":bool,
   "abort_reason":str|null, "model":str, ...}
  {"kind":"call", "arm":"a|b|c|d", "concept":str, "call_kind":"draft|repair",
   "batch_index":int, "latency_s":float,
   "usage":{"input_tokens":int, "cache_creation_input_tokens":int,
            "cache_read_input_tokens":int, "output_tokens":int}}
  {"kind":"concept", "arm":str, "concept":str, "attempted":bool,
   "outcome":"legal|gate-fail|cannot-formalise|parse-fail", "calls":int}

Verdict semantics (frozen, ASM-0602): lawful arm = >=55 concepts processed
AND >=5 legal records; PASS iff best lawful usd_per_legal_record <= 0.05850
(0.75 x the s1-G baseline 0.078); FAIL iff a lawful arm exists and the
minimum lawful usd_per_legal_record >= 0.078; instrument gates (ASM-0605)
override everything to INSTRUMENT-INVALID via the record's verdict rules.
"""

import argparse
import json
import sys

# ---------------------------------------------------------------- price table
# ASM-0601 (STIPULATED): claude-haiku-4-5 pricing + caching multipliers,
# checked 2026-07-10 against the current Claude API reference (models table
# cached 2026-06-24 + prompt-caching reference), consistent with the N-IOC
# section-2.2 live-docs verification of 2026-07-09. USD per token.
PRICE_TABLE_VERSION = "a-f0/1 (2026-07-10)"
USD_PER_INPUT_TOKEN = 1.00 / 1e6      # uncached input
USD_PER_OUTPUT_TOKEN = 5.00 / 1e6     # output; thinking tokens bill as output
USD_PER_CACHE_READ_TOKEN = 0.10 / 1e6   # 0.1x input
USD_PER_CACHE_WRITE_TOKEN = 1.25 / 1e6  # 1.25x input, 5-minute TTL
BATCH_DISCOUNT_MULTIPLIER = 0.5       # derived projection only, never measured

# ASM-0602 (STIPULATED): decision constants.
BASELINE_USD_PER_LEGAL_RECORD = 0.078   # s1-G, MEASURED (s1-report.md)
PASS_MARGIN = 0.75                      # PASS threshold = 0.75 x baseline
PASS_THRESHOLD = round(BASELINE_USD_PER_LEGAL_RECORD * PASS_MARGIN, 5)  # 0.05850
LAWFUL_MIN_CONCEPTS = 55
LAWFUL_MIN_LEGAL = 5

# ASM-0605 (STIPULATED): instrument-gate constants.
MIN_CACHEABLE_PREFIX_TOKENS = 4096
CACHE_READ_POSITIVE_SHARE = 0.90
BUDGET_HARD_CAP_USD = 10.00

ARMS = ("a", "b", "c", "d")
PREFIX_GROUPS = {"a": "ad", "d": "ad", "b": "bc", "c": "bc"}
AMORT_KS = (1, 5, 10, 20, 40, 60)
STEADY_STATE_TAIL = 20


def call_usd(u):
    return (u.get("input_tokens", 0) * USD_PER_INPUT_TOKEN
            + u.get("cache_read_input_tokens", 0) * USD_PER_CACHE_READ_TOKEN
            + u.get("cache_creation_input_tokens", 0) * USD_PER_CACHE_WRITE_TOKEN
            + u.get("output_tokens", 0) * USD_PER_OUTPUT_TOKEN)


def mean(xs):
    return (sum(xs) / len(xs)) if xs else None


def p90(xs):
    if not xs:
        return None
    s = sorted(xs)
    return s[min(len(s) - 1, int(round(0.9 * (len(s) - 1))))]


def rnd(x, nd=6):
    return None if x is None else round(x, nd)


def analyse(lines):
    meta = {}
    calls = []
    concepts = []
    for obj in lines:
        kind = obj.get("kind")
        if kind == "meta":
            meta = obj
        elif kind == "call":
            calls.append(obj)
        elif kind == "concept":
            concepts.append(obj)

    # ---------------------------------------------------------------- gates
    ptc = meta.get("prefix_token_count", {})
    prefix_valid = all(
        isinstance(ptc.get(g), int) and ptc[g] >= MIN_CACHEABLE_PREFIX_TOKENS
        for g in ("ad", "bc"))

    # cache integrity: exclude the first call of each prefix group (file order).
    seen_first = set()
    post_first = []
    for c in calls:
        g = PREFIX_GROUPS.get(c.get("arm"))
        if g is None:
            continue
        if g not in seen_first:
            seen_first.add(g)
            continue
        post_first.append(c)
    n_cache_pos = sum(
        1 for c in post_first
        if c.get("usage", {}).get("cache_read_input_tokens", 0) > 0)
    cache_read_share = (n_cache_pos / len(post_first)) if post_first else 0.0
    cache_valid = bool(post_first) and cache_read_share >= CACHE_READ_POSITIVE_SHARE

    per_arm_concepts = {a: [c for c in concepts if c.get("arm") == a] for a in ARMS}
    completeness_valid = all(
        len(per_arm_concepts[a]) >= LAWFUL_MIN_CONCEPTS for a in ARMS)

    spend_total = sum(call_usd(c.get("usage", {})) for c in calls)
    budget_valid = (spend_total <= BUDGET_HARD_CAP_USD
                    and not meta.get("aborted", False))

    # ------------------------------------------------------------- per arm
    arm_out = {}
    lawful = {}
    for a in ARMS:
        acalls = [c for c in calls if c.get("arm") == a]
        aconc = per_arm_concepts[a]
        n_concepts = len(aconc)
        n_attempted = sum(1 for c in aconc if c.get("attempted"))
        n_legal = sum(1 for c in aconc if c.get("outcome") == "legal")
        n_cf = sum(1 for c in aconc if c.get("outcome") == "cannot-formalise")
        n_pf = sum(1 for c in aconc if c.get("outcome") == "parse-fail")
        usd = sum(call_usd(c.get("usage", {})) for c in acalls)
        lat = [c.get("latency_s") for c in acalls if isinstance(c.get("latency_s"), (int, float))]

        def umean(field):
            vals = [c.get("usage", {}).get(field, 0) for c in acalls]
            return mean(vals)

        lawful[a] = (n_concepts >= LAWFUL_MIN_CONCEPTS and n_legal >= LAWFUL_MIN_LEGAL)
        upc = (usd / n_concepts) if n_concepts else None
        uplr = (usd / n_legal) if n_legal else None

        # cost per concept in batch order (draft + its repair), for amortization
        order = []
        seen = {}
        for c in acalls:
            k = c.get("concept")
            if k not in seen:
                seen[k] = 0.0
                order.append(k)
            seen[k] += call_usd(c.get("usage", {}))
        costs_in_order = [seen[k] for k in order]
        cum = []
        run = 0.0
        for i, x in enumerate(costs_in_order, start=1):
            run += x
            cum.append(run / i)
        cum_at_k = {str(k): rnd(cum[k - 1]) if len(cum) >= k else None for k in AMORT_KS}
        steady = mean(costs_in_order[-STEADY_STATE_TAIL:]) if len(costs_in_order) >= STEADY_STATE_TAIL else None

        arm_out[a] = {
            "n_concepts": n_concepts,
            "n_attempted": n_attempted,
            "n_legal": n_legal,
            "gate_pass_attempted": rnd(n_legal / n_attempted) if n_attempted else None,
            "cf_rate": rnd(n_cf / n_concepts) if n_concepts else None,
            "parse_fail_rate": rnd(n_pf / n_concepts) if n_concepts else None,
            "calls_per_concept": rnd(len(acalls) / n_concepts) if n_concepts else None,
            "usd_total": rnd(usd),
            "usd_per_concept": rnd(upc),
            "usd_per_legal_record": rnd(uplr),
            "lawful": lawful[a],
            "mean_latency_s": rnd(mean(lat), 3),
            "p90_latency_s": rnd(p90(lat), 3),
            "mean_uncached_input_tokens_per_call": rnd(umean("input_tokens"), 1),
            "mean_cache_read_tokens_per_call": rnd(umean("cache_read_input_tokens"), 1),
            "mean_cache_write_tokens_per_call": rnd(umean("cache_creation_input_tokens"), 1),
            "mean_output_tokens_per_call": rnd(umean("output_tokens"), 1),
            "cum_usd_per_concept_at_k": cum_at_k,
            "steady_state_marginal_usd_per_concept": rnd(steady),
            "derived_batch_projected_usd_per_concept": rnd(upc * BATCH_DISCOUNT_MULTIPLIER) if upc is not None else None,
        }

    # ------------------------------------------------------- decision facts
    lawful_arms = [a for a in ARMS if lawful[a]
                   and arm_out[a]["usd_per_legal_record"] is not None]
    any_lawful = bool(lawful_arms)
    best_arm = min(lawful_arms, key=lambda a: arm_out[a]["usd_per_legal_record"]) if any_lawful else None
    best_uplr = arm_out[best_arm]["usd_per_legal_record"] if best_arm else None
    clears = bool(best_uplr is not None and best_uplr <= PASS_THRESHOLD)
    kill = bool(any_lawful and best_uplr is not None
                and best_uplr >= BASELINE_USD_PER_LEGAL_RECORD)

    # ------------------------------------------------------------ paradoxes
    def uplr_of(a):
        return arm_out[a]["usd_per_legal_record"] if lawful[a] else None

    ofp = None
    if lawful["a"] and lawful["b"]:
        ob = arm_out["b"]["mean_output_tokens_per_call"]
        oa = arm_out["a"]["mean_output_tokens_per_call"]
        if ob is not None and oa is not None:
            ofp = bool(ob < oa and (
                (uplr_of("b") is not None and uplr_of("a") is not None
                 and uplr_of("b") >= uplr_of("a"))
                or (arm_out["b"]["mean_latency_s"] is not None
                    and arm_out["a"]["mean_latency_s"] is not None
                    and arm_out["b"]["mean_latency_s"] >= arm_out["a"]["mean_latency_s"])))

    d_da = (uplr_of("d") - uplr_of("a")) if (uplr_of("d") is not None and uplr_of("a") is not None) else None
    d_cb = (uplr_of("c") - uplr_of("b")) if (uplr_of("c") is not None and uplr_of("b") is not None) else None
    off = [x for x in (uplr_of("a"), uplr_of("b")) if x is not None]
    on = [x for x in (uplr_of("c"), uplr_of("d")) if x is not None]
    thinking_helps = (min(on) < min(off)) if (on and off) else None

    return {
        "gates": {
            "prefix_min_cacheable_valid": prefix_valid,
            "cache_integrity_valid": cache_valid,
            "run_completeness_valid": completeness_valid,
            "budget_within_cap": budget_valid,
        },
        "analysis": {
            "price_table_version": PRICE_TABLE_VERSION,
            "spend_usd_total": rnd(spend_total, 4),
            "cache_read_positive_share": rnd(cache_read_share, 4),
            "n_calls_total": len(calls),
            "baseline_usd_per_legal_record": BASELINE_USD_PER_LEGAL_RECORD,
            "pass_threshold_usd_per_legal_record": PASS_THRESHOLD,
            "arm": arm_out,
            "any_lawful_arm": any_lawful,
            "best_lawful_arm": best_arm,
            "best_lawful_usd_per_legal_record": best_uplr,
            "clears_baseline_with_margin": clears,
            "kill_condition": kill,
            "paradox": {
                "output_form_paradox": ofp,
                "thinking_uplr_delta_d_minus_a": rnd(d_da),
                "thinking_uplr_delta_c_minus_b": rnd(d_cb),
                "thinking_helps_cost": thinking_helps,
            },
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="poc/a-f0/results/run-log.jsonl")
    args = ap.parse_args()
    lines = []
    with open(args.input, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                lines.append(json.loads(line))
    print(json.dumps(analyse(lines), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
