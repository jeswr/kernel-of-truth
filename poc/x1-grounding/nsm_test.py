#!/usr/bin/env python3
"""
X1-grounding stage 5 (PREREG §5): the NSM test. Frequency-matched null,
the four T statistics, one-sided empirical p-values, enrichment ratios,
Holm-corrected secondaries, and the pre-registered verdict (§6).

This is the ONLY stage that joins primes to strata (no-peeking, §5.4). It
computes observed and null statistics in a single pass. It runs T_core/T_kern
from stages 1-3 alone; T_ms/T_inv additionally require minset-summary.json.

NOTE: gated by the T2 audit (§8). Do not run on the full graph while the T2
gate is tripped (see PREREG §9 Amendment 2).
"""
import argparse
import gzip
import json
import os
import random

import x1g_lib as L

N_NULL = 10000
NULL_SEED = 42


def load_inputs(graph_path, strata_path, primes_path, minset_path):
    with gzip.open(graph_path, "rt") as f:
        graph = json.loads(f.read())
    with gzip.open(strata_path, "rt") as f:
        strata = json.loads(f.read())
    primes = json.loads(open(primes_path).read())
    minsets = None
    if minset_path and os.path.exists(minset_path):
        minsets = json.loads(open(minset_path).read())
    return graph, strata, primes, minsets


def build_pools(vsw_nodes, outdeg, covar, prime_ids):
    """PREREG §5.2: per-prime candidate pool matched on `covar` value, widened
    1.25 -> 1.5 -> 2.0 until >=50 candidates. Returns {pid: (pool, width)}."""
    prime_set = set(prime_ids)
    pools = {}
    for p in prime_ids:
        d = covar[p]
        chosen = None
        for width in (1.25, 1.5, 2.0):
            lo, hi = d / width, d * width
            pool = [v for v in vsw_nodes
                    if v not in prime_set and lo <= covar[v] <= hi]
            if len(pool) >= 50:
                chosen = (pool, width)
                break
        if chosen is None:
            chosen = (pool, 2.0)  # final width, even if <50 (logged)
        pools[p] = chosen
    return pools


def draw_null(pools, prime_ids, rng):
    """One null draw: one control per prime (chartIndex order), without
    replacement within the draw. Returns (controls, fallback_used).

    Rejection sampling avoids an O(pool) rescan per prime per draw; collisions
    are rare (pools have >=50 candidates, <=50 already used). Falls back to a
    full scan only if 64 draws all collide."""
    used = set()
    controls = []
    fallback = 0
    for p in prime_ids:
        pool, _ = pools[p]
        n = len(pool)
        c = None
        for _ in range(64):
            cand = pool[rng.randrange(n)]
            if cand not in used:
                c = cand
                break
        if c is None:
            avail = [v for v in pool if v not in used]
            if not avail:
                avail = pool
                fallback = 1
            c = avail[rng.randrange(len(avail))]
        used.add(c)
        controls.append(c)
    return controls, fallback


def empirical_p(t_obs, t_null):
    ge = sum(1 for t in t_null if t >= t_obs)
    return (1 + ge) / (len(t_null) + 1)


def enrichment(t_obs, t_null):
    mean = sum(t_null) / len(t_null)
    if mean == 0:
        return float("inf"), mean
    return t_obs / mean, mean


def holm(pvals, alpha=0.05):
    """Holm step-down. pvals: {name: p}. Returns {name: reject_bool}."""
    order = sorted(pvals.items(), key=lambda kv: kv[1])
    m = len(order)
    reject = {}
    still = True
    for i, (name, p) in enumerate(order):
        thr = alpha / (m - i)
        if still and p < thr:
            reject[name] = True
        else:
            still = False
            reject[name] = False
    return reject


def run(graph, strata, primes, minsets, covar_name="outdeg"):
    nodes = graph["nodes"]
    outdeg = graph["outdeg"]
    usage = graph["usage"]
    single_word = graph["single_word"]
    covar = outdeg if covar_name == "outdeg" else usage

    kernel = set(strata["kernel"])
    core = set(strata["core"])
    vsw_nodes = [v for v in range(len(nodes)) if single_word[v]]

    rows = primes["evaluable"]
    prime_ids = [r["nodeId"] for r in sorted(rows, key=lambda r: r["chartIndex"])]
    k = len(prime_ids)

    have_ms = minsets is not None
    m_map = {}
    i09 = set()
    if have_ms:
        m_map = {int(kk): vv for kk, vv in minsets["m"].items()}
        i09 = set(minsets["I09"])

    def stat_core(ids):
        return sum(1 for v in ids if v in core) / len(ids)

    def stat_kern(ids):
        return sum(1 for v in ids if v in kernel) / len(ids)

    def stat_ms(ids):
        return sum(m_map.get(v, 0.0) for v in ids) / len(ids)

    def stat_inv(ids):
        return sum(1 for v in ids if v in i09) / len(ids)

    stats = {"T_core": stat_core, "T_kern": stat_kern}
    if have_ms:
        stats["T_ms"] = stat_ms
        stats["T_inv"] = stat_inv

    obs = {name: fn(prime_ids) for name, fn in stats.items()}

    pools = build_pools(vsw_nodes, outdeg, covar, prime_ids)
    pool_widths = {}
    for r in rows:
        p = r["nodeId"]
        pool, width = pools[p]
        pool_widths[r["prime"]] = {"width": width, "poolSize": len(pool),
                                   "outdeg": outdeg[p]}

    rng = random.Random(NULL_SEED)
    null_vals = {name: [] for name in stats}
    fallback_total = 0
    for _ in range(N_NULL):
        controls, fb = draw_null(pools, prime_ids, rng)
        fallback_total += fb
        for name, fn in stats.items():
            null_vals[name].append(fn(controls))

    results = {}
    for name in stats:
        p = empirical_p(obs[name], null_vals[name])
        er, mean = enrichment(obs[name], null_vals[name])
        sv = sorted(null_vals[name])
        results[name] = {
            "observed": obs[name],
            "nullMean": mean,
            "null95th": sv[int(0.95 * len(sv))],
            "nullMax": sv[-1],
            "p": p,
            "ER": er if er != float("inf") else "inf",
        }

    # Endpoints (§5.4).
    secondary_p = {}
    if "T_kern" in results:
        secondary_p["E-kern"] = results["T_kern"]["p"]
    if "T_ms" in results:
        secondary_p["E-ms"] = results["T_ms"]["p"]
    if "T_inv" in results:
        secondary_p["E-inv"] = results["T_inv"]["p"]
    holm_reject = holm(secondary_p) if len(secondary_p) == 3 else {
        k2: (v < 0.05) for k2, v in secondary_p.items()}  # raw if preliminary

    def er_val(name):
        er = results[name]["ER"]
        return float("inf") if er == "inf" else er

    e_core = (results["T_core"]["p"] < 0.01 and er_val("T_core") >= 1.5)
    endpoints = {"E-core": {"holds": e_core, "primary": True,
                            "p": results["T_core"]["p"], "ER": results["T_core"]["ER"]}}
    if "T_kern" in results:
        endpoints["E-kern"] = {
            "holds": bool(holm_reject.get("E-kern", False) and er_val("T_kern") >= 1.25),
            "holmReject": holm_reject.get("E-kern", False),
            "p": results["T_kern"]["p"], "ER": results["T_kern"]["ER"],
            "pRaw_lt_0.01_and_ER_ge_1.5": (results["T_kern"]["p"] < 0.01 and er_val("T_kern") >= 1.5)}
    if have_ms:
        endpoints["E-ms"] = {
            "holds": bool(holm_reject.get("E-ms", False) and er_val("T_ms") >= 1.5),
            "holmReject": holm_reject.get("E-ms", False),
            "p": results["T_ms"]["p"], "ER": results["T_ms"]["ER"]}
        endpoints["E-inv"] = {
            "holds": bool(holm_reject.get("E-inv", False) and er_val("T_inv") >= 1.5),
            "holmReject": holm_reject.get("E-inv", False),
            "p": results["T_inv"]["p"], "ER": results["T_inv"]["ER"]}

    verdict = compute_verdict(endpoints, primes, have_ms, results, er_val)

    return {
        "covariate": covar_name,
        "evaluableCount": k,
        "observed": obs,
        "results": results,
        "endpoints": endpoints,
        "verdict": verdict,
        "poolWidths": pool_widths,
        "nullFallbackDraws": fallback_total,
        "preliminary_no_minsets": not have_ms,
    }


def compute_verdict(endpoints, primes, have_ms, results, er_val):
    if primes["coverageGate"] != "OK":
        return "INCONCLUSIVE-BY-COVERAGE"
    e_core = endpoints["E-core"]["holds"]
    e_kern = endpoints.get("E-kern", {}).get("holds", False)
    secs = [endpoints[e]["holds"] for e in ("E-kern", "E-ms", "E-inv") if e in endpoints]
    n_sec = sum(secs)
    # §6 FAIL depends ONLY on E-core and E-kern (both from stages 1-3); it is
    # decidable without MinSets. Report it as locked even in the preliminary run.
    if (not e_core) and (not e_kern):
        return "FAIL"
    if not have_ms:
        return "PRELIMINARY (E-core=%s, E-kern=%s; T_ms/T_inv pending MinSets)" % (
            e_core, e_kern)
    e_kern_strong = endpoints.get("E-kern", {}).get("pRaw_lt_0.01_and_ER_ge_1.5", False)
    if e_core and n_sec >= 2:
        return "PASS"
    if (e_core and n_sec < 2) or ((not e_core) and e_kern_strong):
        return "PARTIAL"
    if (not e_core) and not endpoints.get("E-kern", {}).get("holds", False):
        return "FAIL"
    return "PARTIAL"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--graph", default=os.path.join(L.HERE, "graph.json.gz"))
    ap.add_argument("--strata", default=os.path.join(L.HERE, "strata.json.gz"))
    ap.add_argument("--primes", default=os.path.join(L.HERE, "primes-mapping.json"))
    ap.add_argument("--minsets", default=os.path.join(L.HERE, "minset-summary.json"))
    ap.add_argument("--out", default=os.path.join(L.HERE, "results", "x1g-results.json"))
    ap.add_argument("--force-despite-t2", action="store_true",
                    help="override the T2 halt guard (coordinator use only)")
    args = ap.parse_args()

    t2 = os.path.join(L.HERE, "t2-audit-result.json")
    if os.path.exists(t2):
        tr = json.loads(open(t2).read())
        if tr.get("gateTripped") and not args.force_despite_t2:
            raise SystemExit(
                "ERR_X1G_T2_GATE: T2 audit gate tripped (%.0f%%). nsm_test is held "
                "pending a §9 amendment (PREREG §8). Re-run with --force-despite-t2 "
                "only after coordinator sign-off." % (tr["errorRateStrict"] * 100))

    graph, strata, primes, minsets = load_inputs(
        args.graph, args.strata, args.primes, args.minsets)
    primary = run(graph, strata, primes, minsets, covar_name="outdeg")
    sensitivity = run(graph, strata, primes, minsets, covar_name="usage")

    out = {
        "schema": "x1g-results/1",
        "inputsSha256": graph.get("inputsSha256", {}),
        "census": {"V": strata["V"], "V_sw": strata["V_sw"],
                   "kernelSize": strata["kernelSize"], "coreSize": strata["coreSize"]},
        "corridorGates": strata["gates"],
        "primaryNull_outdeg": primary,
        "sensitivityNull_usage": sensitivity,
        "sensitivityAgreesDirection":
            (primary["endpoints"]["E-core"]["holds"] ==
             sensitivity["endpoints"]["E-core"]["holds"]),
        "verdict": primary["verdict"],
    }
    L.dump_json_pretty(out, args.out)
    print("nsm_test verdict:", primary["verdict"])
    for name, r in sorted(primary["results"].items()):
        print("  %-7s obs=%.4f nullMean=%.4f p=%.5f ER=%s" % (
            name, r["observed"], r["nullMean"], r["p"], r["ER"]))


if __name__ == "__main__":
    main()
