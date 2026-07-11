#!/usr/bin/env python3
"""
P3-D-POWER — coverage x max-gain paper-kill rig (G1 Delta_max computation).

Design: docs/next/design/POWER.md (revision 2, post GPT-5.6 review
poc/gpt56-review/rev-dPOWER-20260711). Tier-0, CPU-only, zero-GPU, stdlib-only,
deterministic (no RNG, no clock).

It computes, for a family F on a frozen index pin, the perfect-oracle upper
bound on index gain

    Delta_max(F) = sum_b W_b * min(cap_b, kappa_b * (1 - a_b_cov) / span_b)

on the CHANCE/CEILING-NORMALIZED index scale (EVAL.md §5.3), takes a
SIMULTANEOUS (Bonferroni-adjusted, one-sided) upper confidence bound on that
quantity, and fires the index-mover KILL only when even that joint upper bound
cannot reach the pre-registered margin delta_k. It NEVER licenses a win.

Kill-soundness contract (review rev-dPOWER-20260711, blocking findings 1-3):
  (1) The sum runs over EVERY component of the index pin, never over the census.
      An index benchmark absent from the census — or carrying a metric type
      with no registered max-gain functional — contributes its FULL HEADROOM
      (kappa_ub = 1, a_cov_lb = 0, capped at the benchmark's normalized-score
      headroom). A weighted domain with no enumerated benchmarks contributes
      domain_weight * 1.0 and marks the pin incomplete. No component is ever
      silently assigned zero possible gain.
  (2) A missing covered-slice baseline is imputed a_cov = 0 (the distribution-
      free lower bound; models can score below chance, and deliberately wrong
      predictions are perfectly correctable), never a_cov = chance.
  (3) All stochastic intervals in one run share a Bonferroni-split alpha
      (each one-sided at alpha/m), so the aggregate UCB is a valid
      simultaneous (1-alpha) upper bound by the union bound.
  (4) Uncertainty matches the census estimand: an EXHAUSTIVE census over the
      frozen suite yields an exact finite-suite kappa conditional on labels
      (no Wilson term); its residual uncertainty is the registered oracle-
      label false-negative allowance label_fn_ub. A SAMPLED census requires a
      registered sampling frame and gets Bonferroni-adjusted Wilson bounds.
  (5) A KILL verdict is emitted only on a verdict-eligible run: frozen index
      pin, complete census pin block, declared coverage lane, and a registered
      family-eligibility (non-interference) reference. Anything else runs in
      EXPLORATORY mode and emits ILLUSTRATIVE-ONLY — no G1 verdict.

Form B (firewall / wrong->abstain) is uncomputable until P3-D-INDEX registers
the abstention-scoring transform: requesting it fails closed
(ERR_FORM_B_UNREGISTERED).

Usage:
    python3 power.py --index INDEX_PIN.json --census CENSUS.json [--out OUT.json]
"""
import argparse
import json
import math
import sys
from statistics import NormalDist

ALPHA = 0.05  # one-sided family-wise level for the kill UCB

COVERAGE_LANES = ("mapper-parse", "oracle", "upper-sieve")
CENSUS_MODES = ("exhaustive", "sampled")
# Registered per-metric maximum-gain functionals. Form A (itemwise perfect
# correction, gain_raw = kappa*(1-a_cov)) is registered for itemwise accuracy
# ONLY (EVAL.md: the chance/ceiling transform is defined for accuracy-type
# metrics only). Every other metric type gets full headroom.
SUPPORTED_METRICS = ("accuracy",)
# Census pin block required for a verdict-eligible run (cross-rung reuse guard).
CENSUS_PIN_FIELDS = ("model_checkpoint", "harness_hash", "prompt_policy",
                     "seeds", "store_hash", "kernel_hash", "world_layer_hash",
                     "mapper_hash", "grammar_version", "benchmark_revisions")


def die(code, msg):
    print("FAIL %s: %s" % (code, msg), file=sys.stderr)
    sys.exit(2)


def wilson_bounds(k, n, z):
    """Wilson score interval at normal quantile z. n==0 => (0,1): a census that
    measured nothing constrains nothing."""
    if n <= 0:
        return (0.0, 1.0)
    phat = k / n
    z2 = z * z
    denom = 1.0 + z2 / n
    center = (phat + z2 / (2 * n)) / denom
    half = (z * math.sqrt((phat * (1 - phat) + z2 / (4 * n)) / n)) / denom
    return (max(0.0, center - half), min(1.0, center + half))


# ---------------------------------------------------------------------------
# Validation (fail closed; review: "lacks schema/range/weight/completeness
# validation")
# ---------------------------------------------------------------------------
def validate_index(index):
    for key in ("delta_k", "domains", "benchmarks"):
        if key not in index:
            die("ERR_PIN_SCHEMA", "index pin missing required key %r" % key)
    dk = index["delta_k"]
    if not (isinstance(dk, (int, float)) and 0 < dk <= 1):
        die("ERR_PIN_SCHEMA", "delta_k must be in (0,1], got %r" % dk)
    wsum = 0.0
    for d, dom in index["domains"].items():
        w = dom.get("weight")
        if not (isinstance(w, (int, float)) and 0 <= w <= 1):
            die("ERR_PIN_SCHEMA", "domain %s weight must be in [0,1], got %r" % (d, w))
        wsum += w
    if abs(wsum - 1.0) > 1e-9:
        die("ERR_PIN_SCHEMA", "domain weights must sum to 1, got %.6f" % wsum)
    within = {}
    for name, b in index["benchmarks"].items():
        d = b.get("domain")
        if d not in index["domains"]:
            die("ERR_PIN_SCHEMA", "benchmark %s: unknown domain %r" % (name, d))
        if "metric_type" not in b:
            die("ERR_PIN_SCHEMA", "benchmark %s: metric_type is required "
                "(accuracy | loss | logprob | generation | ...)" % name)
        ch, ce = b.get("chance"), b.get("ceiling")
        if b["metric_type"] in SUPPORTED_METRICS:
            if not (isinstance(ch, (int, float)) and isinstance(ce, (int, float))
                    and 0.0 <= ch < ce <= 1.0):
                die("ERR_PIN_SCHEMA", "benchmark %s: need 0 <= chance < ceiling <= 1, "
                    "got chance=%r ceiling=%r" % (name, ch, ce))
        ww = b.get("within_domain_weight")
        if ww is not None:
            within.setdefault(d, []).append((name, ww))
    for d, pairs in within.items():
        members = [n for n, b in index["benchmarks"].items() if b["domain"] == d]
        if len(pairs) != len(members):
            die("ERR_PIN_SCHEMA", "domain %s: within_domain_weight set on some but "
                "not all members" % d)
        s = sum(w for _, w in pairs)
        if abs(s - 1.0) > 1e-9:
            die("ERR_PIN_SCHEMA", "domain %s: within_domain_weights sum to %.6f, "
                "not 1" % (d, s))


def validate_census(index, census):
    for key in ("family", "rung", "coverage_lane", "census_mode", "coverage"):
        if key not in census:
            die("ERR_CENSUS_SCHEMA", "census missing required key %r" % key)
    if census["coverage_lane"] not in COVERAGE_LANES:
        die("ERR_CENSUS_SCHEMA", "coverage_lane %r not in %s"
            % (census["coverage_lane"], "/".join(COVERAGE_LANES)))
    if census["census_mode"] not in CENSUS_MODES:
        die("ERR_CENSUS_SCHEMA", "census_mode %r not in %s"
            % (census["census_mode"], "/".join(CENSUS_MODES)))
    if census["census_mode"] == "exhaustive" and "label_fn_ub" not in census:
        die("ERR_CENSUS_SCHEMA", "exhaustive census requires label_fn_ub (registered "
            "upper bound on the oracle-label false-negative rate; 0.0 only for a "
            "deterministic mechanical classifier)")
    if census["census_mode"] == "sampled" and not census.get("sampling_frame"):
        die("ERR_CENSUS_SCHEMA", "sampled census requires an explicit sampling_frame "
            "(frame + stratification)")
    for name, cov in census["coverage"].items():
        if name not in index["benchmarks"]:
            die("ERR_CENSUS_SCHEMA", "censused benchmark %r is not in the index pin "
                "(no silent extras)" % name)
        n, c = cov.get("n_total"), cov.get("covered_count")
        if not (isinstance(n, int) and n >= 0 and isinstance(c, int) and 0 <= c <= n):
            die("ERR_CENSUS_SCHEMA", "%s: need integer 0 <= covered_count <= n_total, "
                "got covered_count=%r n_total=%r" % (name, c, n))
        if ("correct_cov" in cov) != ("n_cov" in cov):
            die("ERR_CENSUS_SCHEMA", "%s: correct_cov and n_cov must appear together "
                "(integer counts, not a rounded rate)" % name)
        if "a_cov" in cov:
            die("ERR_CENSUS_SCHEMA", "%s: float a_cov is not accepted; supply integer "
                "correct_cov / n_cov" % name)
        if "correct_cov" in cov:
            k, m = cov["correct_cov"], cov["n_cov"]
            if not (isinstance(k, int) and isinstance(m, int) and 0 <= k <= m):
                die("ERR_CENSUS_SCHEMA", "%s: need integer 0 <= correct_cov <= n_cov"
                    % name)


def verdict_eligibility(index, census):
    """A KILL verdict may only be emitted on a fully pinned run. Returns
    (eligible: bool, reasons: [str])."""
    reasons = []
    if index.get("frozen") is not True:
        reasons.append("index pin is not a P3-D-INDEX freeze (frozen != true)")
    pin = census.get("pin") or {}
    missing = [f for f in CENSUS_PIN_FIELDS if not pin.get(f)]
    if missing:
        reasons.append("census pin block missing: %s" % ", ".join(missing))
    elig = census.get("family_eligibility") or {}
    if elig.get("form") != "A" or not elig.get("noninterference_ref"):
        reasons.append("no registered Form-A family eligibility "
                       "(noninterference/covered-support argument) declared")
    return (not reasons), reasons


# ---------------------------------------------------------------------------
# The computation
# ---------------------------------------------------------------------------
def eff_weight(name, bench, index):
    """W_b = domain_weight(d) * within_domain_weight(b); equal within-domain
    split by default (the weights are the P3-D-INDEX normative choice)."""
    d = bench["domain"]
    members = [n for n, b in index["benchmarks"].items() if b["domain"] == d]
    ww = bench.get("within_domain_weight")
    if ww is None:
        ww = 1.0 / len(members)
    return index["domains"][d]["weight"] * ww


def count_intervals(index, census):
    """m = number of stochastic intervals the run will take, for the Bonferroni
    split. Exhaustive-census kappa is exact given labels (no interval);
    sampled-census kappa takes one per censused benchmark; every measured
    covered-slice baseline takes one."""
    m = 0
    sampled = census["census_mode"] == "sampled"
    for name in index["benchmarks"]:
        cov = census["coverage"].get(name)
        if cov is None:
            continue
        if sampled and cov["n_total"] > 0:
            m += 1
        if "correct_cov" in cov and cov["n_cov"] > 0:
            m += 1
    return m


def compute(index, census):
    validate_index(index)
    validate_census(index, census)
    delta_k = index["delta_k"]
    lane = census["coverage_lane"]
    exhaustive = census["census_mode"] == "exhaustive"
    label_fn_ub = float(census.get("label_fn_ub", 0.0))

    m = count_intervals(index, census)
    z = NormalDist().inv_cdf(1.0 - ALPHA / m) if m > 0 else None

    rows = []
    incomplete = []  # pin/census completeness notes (any entry => not fully censused)
    for name, b in index["benchmarks"].items():
        W = eff_weight(name, b, index)
        metric = b["metric_type"]
        if metric in SUPPORTED_METRICS:
            chance, ceiling = b["chance"], b["ceiling"]
            span = ceiling - chance
            span_lb = max(1e-9, span - float(b.get("ceiling_slack", 0.0)))
            # headroom cap: a raw score never exceeds 1, so the normalized gain
            # never exceeds (1 - chance)/span (with clamped indices, 1.0).
            cap = 1.0 if index.get("clamp_normalized", False) else (1.0 - chance) / span_lb
        else:
            chance = ceiling = span = span_lb = None
            cap = 1.0  # normalized component score is capped at 1 by definition

        cov = census["coverage"].get(name)
        row = {"benchmark": name, "domain": b["domain"], "W_eff": W,
               "metric_type": metric, "chance": chance, "ceiling": ceiling,
               "span": span}

        if metric not in SUPPORTED_METRICS:
            # Review "other substantive gaps" (Form A not universal): a metric
            # with no registered max-gain functional gets FULL headroom.
            row.update(status="FULL-HEADROOM (metric %r has no registered "
                              "max-gain functional)" % metric,
                       contrib_hat=W * cap, contrib_ucb=W * cap,
                       kappa_star=None)
            incomplete.append("%s: metric %r unsupported -> full headroom"
                              % (name, metric))
        elif cov is None or cov["n_total"] == 0:
            # Blocking finding 1: uncensused component => full headroom, never 0.
            row.update(status="FULL-HEADROOM (not censused)",
                       n_total=(0 if cov is None else cov["n_total"]),
                       covered_count=None, kappa_hat=None, kappa_ub=1.0,
                       a_cov_hat=None, a_cov_lb=0.0,
                       contrib_hat=W * cap, contrib_ucb=W * cap,
                       kappa_star=None)
            incomplete.append("%s: no census entry -> full headroom" % name)
        else:
            N, covered = cov["n_total"], cov["covered_count"]
            kappa_hat = covered / N
            if exhaustive:
                # finite-suite kappa is exact conditional on labels; the residual
                # uncertainty is the registered label false-negative allowance.
                kappa_ub = min(1.0, kappa_hat + label_fn_ub)
            else:
                _, kappa_ub = wilson_bounds(covered, N, z)
            if "correct_cov" in cov and cov["n_cov"] > 0:
                k_ok, n_cov = cov["correct_cov"], cov["n_cov"]
                a_cov_hat = k_ok / n_cov
                a_cov_lb, _ = wilson_bounds(k_ok, n_cov, z)
            else:
                # Blocking finding 2: the distribution-free lower bound is 0,
                # not chance (below-chance baselines exist and are perfectly
                # correctable).
                a_cov_hat, a_cov_lb = 0.0, 0.0
            gain_hat = kappa_hat * (1.0 - a_cov_hat)
            gain_ucb = kappa_ub * (1.0 - a_cov_lb)
            contrib_hat = W * min(cap, gain_hat / span)
            contrib_ucb = W * min(cap, gain_ucb / span_lb)
            # per-benchmark required coverage if b alone carried delta_k:
            denom = W * (1.0 - a_cov_hat) / span
            kappa_star = (delta_k / denom) if denom > 0 else float("inf")
            row.update(status="censused",
                       n_total=N, covered_count=covered,
                       kappa_hat=kappa_hat, kappa_ub=kappa_ub,
                       a_cov_hat=a_cov_hat, a_cov_lb=a_cov_lb,
                       contrib_hat=contrib_hat, contrib_ucb=contrib_ucb,
                       kappa_star=kappa_star)
        rows.append(row)

    # weighted domains with no enumerated benchmarks: full headroom, and the
    # pin is by definition incomplete (a freeze must enumerate every domain).
    empty_domains = []
    for d, dom in index["domains"].items():
        if dom["weight"] > 0 and not any(b["domain"] == d
                                         for b in index["benchmarks"].values()):
            empty_domains.append({"domain": d, "weight": dom["weight"],
                                  "contrib": dom["weight"] * 1.0})
            incomplete.append("domain %s: weight %.3f, no benchmarks enumerated "
                              "-> full headroom" % (d, dom["weight"]))

    scalar_hat = sum(r["contrib_hat"] for r in rows) + sum(e["contrib"] for e in empty_domains)
    scalar_ucb = sum(r["contrib_ucb"] for r in rows) + sum(e["contrib"] for e in empty_domains)

    domains = {}
    for r in rows:
        d = domains.setdefault(r["domain"], {"delta_max_hat": 0.0, "delta_max_ucb": 0.0,
                                             "fully_censused": True})
        d["delta_max_hat"] += r["contrib_hat"]
        d["delta_max_ucb"] += r["contrib_ucb"]
        if r["status"] != "censused":
            d["fully_censused"] = False
    for dname, d in domains.items():
        w = index["domains"][dname]["weight"]
        d["delta_k_domain"] = index.get("delta_k_domain", {}).get(dname, delta_k)
        d["delta_max_hat_ownaxis"] = d["delta_max_hat"] / w if w else 0.0
        d["delta_max_ucb_ownaxis"] = d["delta_max_ucb"] / w if w else 0.0

    # uniform required-kappa inversion over the censusable accuracy components
    per_unit = sum(r["W_eff"] * (1.0 - r["a_cov_hat"]) / r["span"]
                   for r in rows
                   if r["status"] == "censused" and r["span"])
    kappa_required = (delta_k / per_unit) if per_unit > 0 else float("inf")

    eligible, reasons = verdict_eligibility(index, census)
    kill_arith = scalar_ucb < delta_k
    if not eligible:
        verdict_str = "ILLUSTRATIVE-ONLY — no G1 verdict (run not verdict-eligible)"
    elif kill_arith:
        verdict_str = ("KILL index-mover claim (zero GPU) — CONTINGENT on the oracle census"
                       if lane == "mapper-parse" else
                       "KILL index-mover claim (zero GPU) — UNCONDITIONAL (lane: %s)" % lane)
    else:
        verdict_str = "NO KILL — ceiling not excluded; proceed to G2 and P3-D-POWER-SIZE sizing"

    return {
        "rows": rows,
        "empty_domains": empty_domains,
        "domains": domains,
        "incomplete": incomplete,
        "alpha_one_sided": ALPHA,
        "n_intervals_bonferroni": m,
        "z_per_interval": z,
        "verdict": {
            "family": census["family"],
            "rung": census["rung"],
            "coverage_lane": lane,
            "census_mode": census["census_mode"],
            "delta_k": delta_k,
            "delta_max_scalar_hat": scalar_hat,
            "delta_max_scalar_ucb": scalar_ucb,
            "ucb_is_simultaneous": True,
            "kill_arithmetic": kill_arith,
            "verdict_eligible": eligible,
            "ineligibility_reasons": reasons,
            "verdict": verdict_str,
            "kappa_required_uniform": kappa_required,
            "kappa_required_reachable": kappa_required <= 1.0,
            "kappa_star_note": "kappa* is a coverage TARGET only after KOT-LIFE/1 "
                               "costing (bytes, authoring/review hours, B_k "
                               "admissibility); it is not actionable naked.",
            "store_pin_echo": {k: (census.get("pin") or {}).get(k)
                               for k in ("store_hash", "kernel_hash",
                                         "world_layer_hash", "store_version")},
        },
    }


def fmt(x, p=4):
    if x is None:
        return "n/a"
    if isinstance(x, float):
        return "inf" if math.isinf(x) else f"{x:.{p}f}"
    return str(x)


def report(res):
    v = res["verdict"]
    L = []
    L.append(f"FAMILY {v['family']}  |  RUNG {v['rung']}  |  lane {v['coverage_lane']} "
             f"({v['census_mode']})  |  delta_k = {fmt(v['delta_k'])}")
    L.append(f"simultaneous UCB: one-sided alpha={res['alpha_one_sided']}, "
             f"Bonferroni over m={res['n_intervals_bonferroni']} interval(s)"
             + (f", z={res['z_per_interval']:.4f}" if res["z_per_interval"] else
                " (finite-suite exact given labels; no sampling intervals)"))
    L.append("-" * 112)
    L.append(f"{'benchmark':30s} {'dom':4s} {'N':>6s} {'cov':>5s} {'kappa^':>7s} {'kUB':>6s} "
             f"{'a_cov':>6s} {'contrib':>8s} {'contribUB':>9s} {'kappa*_b':>8s}  status")
    for r in res["rows"]:
        L.append(f"{r['benchmark']:30s} {r['domain']:4s} {fmt(r.get('n_total'),0):>6s} "
                 f"{fmt(r.get('covered_count'),0):>5s} {fmt(r.get('kappa_hat')):>7s} "
                 f"{fmt(r.get('kappa_ub'),3):>6s} {fmt(r.get('a_cov_hat'),3):>6s} "
                 f"{r['contrib_hat']:8.5f} {r['contrib_ucb']:9.5f} "
                 f"{fmt(r.get('kappa_star'),3):>8s}  {r['status']}")
    for e in res["empty_domains"]:
        L.append(f"{'(no benchmarks enumerated)':30s} {e['domain']:4s} {'':6s} {'':5s} "
                 f"{'':7s} {'':6s} {'':6s} {e['contrib']:8.5f} {e['contrib']:9.5f} "
                 f"{'n/a':>8s}  FULL-HEADROOM (empty weighted domain)")
    L.append("-" * 112)
    L.append(f"Delta_max (scalar, point)      = {fmt(v['delta_max_scalar_hat'])}")
    L.append(f"Delta_max (scalar, simUCB95)   = {fmt(v['delta_max_scalar_ucb'])}   [kill uses this]")
    for dname in sorted(res["domains"]):
        d = res["domains"][dname]
        L.append(f"Delta_max ({dname}, own axis)       = point {fmt(d['delta_max_hat_ownaxis'])} / "
                 f"simUCB95 {fmt(d['delta_max_ucb_ownaxis'])}  vs delta_k^d = "
                 f"{fmt(d['delta_k_domain'])}"
                 + ("" if d["fully_censused"] else "   [domain NOT fully censused]"))
    L.append(f"kappa* required (uniform)      = {fmt(v['kappa_required_uniform'])}"
             f"   reachable(<=1)? {v['kappa_required_reachable']}"
             f"   [target only after KOT-LIFE/1 costing]")
    if res["incomplete"]:
        L.append("")
        L.append("full-headroom imputations (completeness — nothing contributes silent zero):")
        for note in res["incomplete"]:
            L.append(f"  - {note}")
    L.append("")
    L.append(f">>> VERDICT: {v['verdict']}")
    L.append(f"    arithmetic: simUCB95(Delta_max) < delta_k  ->  "
             f"{fmt(v['delta_max_scalar_ucb'])} < {fmt(v['delta_k'])} = {v['kill_arithmetic']}")
    if not v["verdict_eligible"]:
        L.append("    not verdict-eligible because:")
        for r in v["ineligibility_reasons"]:
            L.append(f"      * {r}")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--index", required=True)
    ap.add_argument("--census", required=True)
    ap.add_argument("--form", default=None, help="A (corrector; default) or B (firewall)")
    ap.add_argument("--out")
    a = ap.parse_args()
    census = json.load(open(a.census))
    form = a.form or (census.get("family_eligibility") or {}).get("form", "A")
    if form == "B":
        die("ERR_FORM_B_UNREGISTERED",
            "Form B (firewall wrong->abstain ceiling) is uncomputable until "
            "P3-D-INDEX registers the abstention-scoring transform; on an "
            "accuracy-only index Form B == 0 by construction (POWER.md §1.3).")
    if form != "A":
        die("ERR_FORM_UNKNOWN", "form must be A or B, got %r" % form)
    index = json.load(open(a.index))
    res = compute(index, census)
    print(report(res))
    if a.out:
        json.dump(res, open(a.out, "w"), indent=2)
        print(f"\n[wrote {a.out}]", file=sys.stderr)


if __name__ == "__main__":
    main()
