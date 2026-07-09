#!/usr/bin/env python3
"""a5-llm pinned analysis — engine-vs-LLM head-to-head on the pinned a5
code-structure slice (DRAFT registry/experiments/a5-llm.json; prereg anchor
docs/design-a5-llm.md sections 5-6). Fills the record's
pins.analysis_script.output_fields slot; frozen by sha at prereg-freeze.

Eligible kot-log/1 run records on stdin (one JSON per line); analysis-output
JSON on stdout. Derived statistics live HERE and nowhere else (P2 G-4).
Stdlib only; deterministic (PRNG seed 20260709, B=10000 paired per-query BCa
bootstrap; float64 end-to-end — P8 C-7). The bootstrap size may be overridden
via env A5LLM_BOOTSTRAP_B for $0 mechanics checks ONLY; any override is made
visible in the output (/analysis/bootstrap_B) so a non-default B in a final
verdict artifact is self-announcing.

Input contract (tools/experiments/a5_llm_instrument.py raw metrics; the LAST
record per (arm, rung) cell wins — supersession is verdict-gen's job):
  9 cells: engine/abstain-all/answer-all @R0 (CPU, item_conj STRICT a5 rules
  for the engine; the engine record embeds metrics.a5_reference) and
  {llm-direct, llm-rag} x {R1,R2,R3} (item_conj under the pinned LENIENT
  pro-LLM instrument, ASM-0012). All item vectors are in the pinned a5-eval
  file order; item_class (1=covered) must be identical across all records.

PRIMARY (record endpoints[0], f2b-replicate discipline — ABSOLUTE, no
denominator): effect_size = conj_acc(engine) - conj_acc(best-LLM), best-LLM =
argmax conjunctive point estimate over the EXHAUSTIVE six-cell family
restricted to extraction-gate-valid cells (gate validity fixed full-sample;
the max is RESELECTED inside every bootstrap resample and every jackknife
replicate, so selection uncertainty is inside every CI — the f2b convention;
taking the max is conservative for the engine). Reject iff the one-sided 95%
BCa LOWER bound > 0.10. Ties in the max break by (conj, covered-exact,
control-refusal, cell name) — deterministic, documented, pro-LLM on the
covered-superiority secondary.

KILL MACHINERY (record kill_criterion_verbatim; booleans only — verdict-gen
applies the frozen rules):
  differentiator_within_kill: any gate-valid LLM cell with
    conj_acc(engine) - conj_acc(cell) <= 0.05 (point estimates);
  cost_ratio_min: min over the six LLM cells of usd/query(cell) /
    usd/query(engine), F0 section 3.3/3.5 accounting — engine = measured
    ns/query x pinned CPU core rate; LLM = metered GPU wall-seconds x pinned
    Modal class rate / 977. Rates pinned below; the CPU core rate 0.135
    usd/core-h is the Modal physical-core list rate already pinned in
    poc/modal/modal_e1e4_lib.py RATES — deliberately HIGH for a shared
    2-core box, which SHRINKS the ratio, i.e. is conservative against the
    >10^3 cost gate;
  primary_upper_onesided95 (kill c reads UB <= 0.10).

INSTRUMENT GATES (design section 5.4; instrument events, never hypothesis
events): /gates/instrument_valid = pins/strata checks AND engine-regression
(engine_matches_a5: the fresh engine record's comparable raw subset equals
the embedded a5_reference — the finest granularity a5 logged is per-family
counts; the fresh log additionally carries item_conj + a per-query outcome
digest for future regressions) AND per-cell extraction Wilson 95% LB >= 0.90
with >=1 rag AND >=1 direct cell passing AND retrieval_completeness_violations
== 0. /gates/separation_valid (f2b-style, gates ONLY scale_trend_rag):
conj(llm-direct-R3) - conj(llm-direct-R1) >= 0.05 AND one-sided 95% BCa
LB > 0; on failure scale_trend_rag leaves the Holm family BEFORE any p-value
comparison.

ONE Holm family F-secondary(a5-llm) at alpha=0.05, membership pre-declared:
covered_superiority, refusal_superiority, rag_lift_r3, fabrication_material,
plus (conditional on the separation gate) scale_trend_rag. fabrication's p is
the exact one-sided binomial tail at null rate 0.30 (stdlib, deterministic);
its member additionally requires the record's verbatim Wilson-LB > 0.30.
Everything else (per-cell tables, latency/FLOPs, truncation, trivial-arm
brackets) is DESCRIPTIVE — never Holm, never verdict-bearing.

Fixture: --selftest (constructed 977-shape cells; HAND-COMPUTED values in
comments at each assert).
"""
import json
import math
import os
import sys
from statistics import NormalDist

SEED = 20260709
B_PRODUCTION = 10000
ALPHA = 0.05
Z = 1.645  # one-sided 95%, matches tools/registry/kot_common.py
ND = NormalDist()

N_QUERIES = 977
N_COVERED = 855
N_CONTROL = 122
SEOI = 0.10                 # smallest effect of interest (absolute conj diff)
KILL_MARGIN = 0.05          # differentiator kill (a)
COST_GATE = 1000.0          # HL3a cost clause
EXTRACTION_LB = 0.90        # P10-analogue per-cell gate
FABRICATION_BAR = 0.30      # H-FAB Wilson bar
SEPARATION_MIN = 0.05       # separation instrument gate

# Pinned a5-eval strata (data/a5-eval/manifest.json, frozen in a5 + reused
# verbatim by the a5-llm record).
PLANNED_STRATA = {
    "callees-of": 73, "callers-of": 74, "conflict": 5, "contained-in": 201,
    "contains": 41, "imported-by": 2, "imports-of": 9,
    "instance-false-disjoint": 38, "instance-true": 216, "malformed": 16,
    "no-record-callees": 15, "no-record-callers": 15, "no-record-contains": 10,
    "no-record-imported-by": 10, "no-record-imports": 6,
    "out-of-scope-concept": 6, "unknown-entity": 24, "unlicensed-unique": 15,
    "where-defined": 201,
}

# Pinned corpus digests (identical to the frozen a5 record; copied unchanged
# into registry/experiments/a5-llm.json pins.corpus_hashes — prereg-freeze
# recomputes and must agree with these constants).
CORPUS_PINS = {
    "a5-eval": "3676d689277660f80f7cfac9823ecb7b9b40a73777ad538623405c5c1e903843",
    "code-axioms-v0": "dc930b4fdeb95994828d8b7b0a184e5d96714a3b7f51269f7d46cba5b14e39e3",
    "code-corpus-v0": "1063ad50ff694d8548296f42c17f296027768a87dba98f534e9f2ea7f7c5fea3",
    "code-v0": "01009b1fc0c6e34b0c49b294e0cb159695831070fbe6808957694f46d03abd83",
    "code-world-v0": "b8a8a50a3111425685cb2041061f72e4d0d89da17cb073fdffe11b338f26aef9",
    "kernel-v0": "8209cadabcfc2eaa11631c5c1100c04a48f33673516780b1f36cbf957217c809",
}

# Cost pins (F0 section 3.5 discipline; the record's usd_per_query DV).
CPU_CORE_USD_PER_HOUR = 0.135   # poc/modal/modal_e1e4_lib.py RATES["cpu_core_h"]
GPU_USD_PER_HOUR = {"T4": 0.59, "A10G": 1.10, "A100": 2.10}  # f2b-manifest pins
# Nominal params per rung (descriptive FLOPs ~ 2*N*tokens only).
N_PARAMS = {"R1": 1.35e8, "R2": 3.6e8, "R3": 1.7e9}

LLM_CELLS = [("llm-direct", "R1"), ("llm-direct", "R2"), ("llm-direct", "R3"),
             ("llm-rag", "R1"), ("llm-rag", "R2"), ("llm-rag", "R3")]

A5_REFERENCE_KEYS = (
    "n_covered", "n_covered_exact", "n_covered_refused",
    "n_covered_answered_wrong", "n_control", "n_control_refused_correct_code",
    "n_control_refused_other_code", "n_control_answered",
    "n_control_refused_any", "provenance_checked", "provenance_all_valid",
    "by_family", "store")


def cell_name(arm, rung):
    return "%s-%s" % (arm, rung)


def wilson(p, n, upper=False, z=Z):
    if n <= 0:
        return 1.0 if upper else 0.0
    z2 = z * z
    centre = p + z2 / (2 * n)
    spread = z * ((p * (1 - p) / n + z2 / (4 * n * n)) ** 0.5)
    return (centre + spread if upper else centre - spread) / (1 + z2 / n)


def binom_sf_p(x, n, p0):
    """Exact one-sided binomial p for H0: rate <= p0 vs > p0: P(X >= x)."""
    if x <= 0:
        return 1.0
    total = 0.0
    for k in range(x, n + 1):
        total += math.comb(n, k) * (p0 ** k) * ((1 - p0) ** (n - k))
    return min(1.0, total)


def bca_bounds(theta_hat, thetas, jack, levels):
    """BCa bounds at the given lower-tail levels (per-query jackknife).
    Same machinery as analysis/f2b_replicate.py (the house convention)."""
    if not thetas:
        return [None] * len(levels)
    b = len(thetas)
    below = sum(1 for t in thetas if t < theta_hat)
    z0 = ND.inv_cdf(min(max(below / b, 1.0 / (b + 1)), b / (b + 1.0)))
    jack = [j for j in jack if j is not None]
    if len(jack) >= 2:
        jbar = sum(jack) / len(jack)
        num = sum((jbar - j) ** 3 for j in jack)
        den = 6.0 * (sum((jbar - j) ** 2 for j in jack) ** 1.5)
        a = 0.0 if den == 0 else num / den
    else:
        a = 0.0
    out = []
    srt = sorted(thetas)
    for lv in levels:
        z = ND.inv_cdf(lv)
        adj = ND.cdf(z0 + (z0 + z) / (1 - a * (z0 + z)))
        pos = min(max(int(adj * b), 0), b - 1)
        out.append(srt[pos])
    return out


def one_sided_p(boot, null=0.0):
    """Bootstrap one-sided p: share of resampled statistics <= the null."""
    b = len(boot)
    if b == 0:
        return 1.0
    return (1 + sum(1 for d in boot if d <= null)) / (b + 1)


def holm(pvals, alpha=ALPHA):
    order = sorted(range(len(pvals)), key=lambda i: pvals[i])
    reject = [False] * len(pvals)
    m = len(pvals)
    for rank, i in enumerate(order):
        if pvals[i] <= alpha / (m - rank):
            reject[i] = True
        else:
            break
    return reject


def percentile(values, q):
    """Nearest-rank percentile (pinned convention)."""
    if not values:
        return None
    srt = sorted(values)
    idx = max(0, math.ceil(q * len(srt)) - 1)
    return srt[idx]


# ----------------------------------------------------------------- gathering
def gather(records):
    by_cell = {}
    for r in records:
        cfg = r.get("config", {})
        key = (cfg.get("arm"), cfg.get("rung"))
        by_cell[key] = r  # last per cell wins
    return by_cell


def corpus_pins_ok(rec):
    pins = rec.get("pins_observed", {})
    for corpus, want in CORPUS_PINS.items():
        got = pins.get("corpus_%s" % corpus, {}).get("observed")
        if got != want:
            return False
    return True


def strata_ok(metrics):
    fam = metrics.get("by_family", {})
    if set(fam) != set(PLANNED_STRATA):
        return False
    return all(fam[k].get("n") == v for k, v in PLANNED_STRATA.items())


def engine_matches_a5(eng_metrics):
    ref = eng_metrics.get("a5_reference")
    if not isinstance(ref, dict) or "metrics" not in ref:
        return 0
    if eng_metrics.get("deterministic_repeat_identical") is not True:
        return 0
    want = ref["metrics"]
    for k in A5_REFERENCE_KEYS:
        if k not in want:
            return 0
        if json.dumps(eng_metrics.get(k), sort_keys=True) != \
                json.dumps(want[k], sort_keys=True):
            return 0
    return 1


def usd_per_query_engine(m):
    n = m.get("n_queries") or 0
    if not n:
        return None
    ns_per_query = m.get("engine_total_ns", 0) / n
    return ns_per_query * CPU_CORE_USD_PER_HOUR / 3.6e12


def usd_per_query_llm(rec):
    m, cfg = rec["metrics"], rec.get("config", {})
    rate = GPU_USD_PER_HOUR.get(cfg.get("gpu_class"))
    wall = m.get("gpu_wall_seconds")
    n = m.get("n_queries") or 0
    if rate is None or wall is None or not n:
        return None
    return wall * (rate / 3600.0) / n


# ------------------------------------------------------------------- analyse
def analyze(records, B=None):
    import random
    if B is None:
        B = int(os.environ.get("A5LLM_BOOTSTRAP_B", B_PRODUCTION))
    rng = random.Random(SEED)
    by_cell = gather(records)
    out = {"gates": {"instrument_valid": False, "separation_valid": False},
           "analysis": {"holm": {}}}
    a = out["analysis"]
    a["bootstrap_B"] = B

    eng = by_cell.get(("engine", "R0"))
    ab = by_cell.get(("abstain-all", "R0"))
    aa = by_cell.get(("answer-all", "R0"))
    llm = {c: by_cell.get(c) for c in LLM_CELLS}
    if eng is None:
        return out  # unresolvable fields => INCOMPLETE-DATA downstream
    em = eng["metrics"]

    # --- pins / strata / alignment gate --------------------------------------
    all_present = (ab is not None and aa is not None
                   and all(v is not None for v in llm.values()))
    cls = em.get("item_class")
    pins_ok = bool(
        all_present
        and isinstance(cls, list) and len(cls) == N_QUERIES
        and sum(cls) == N_COVERED
        and em.get("n_queries") == N_QUERIES
        and strata_ok(em)
        and corpus_pins_ok(eng) and corpus_pins_ok(ab) and corpus_pins_ok(aa)
    )
    pack_shas = set()
    if all_present:
        for c, rec in llm.items():
            m = rec["metrics"]
            pins_ok = pins_ok and bool(
                m.get("n_queries") == N_QUERIES
                and m.get("item_class") == cls
                and strata_ok(m)
                and corpus_pins_ok(rec))
            pack_shas.add(rec.get("config", {}).get("pack_sha256"))
        pins_ok = pins_ok and len(pack_shas) == 1 and None not in pack_shas
        pins_ok = pins_ok and ab["metrics"].get("item_class") == cls \
            and aa["metrics"].get("item_class") == cls

    # --- engine regression gate ----------------------------------------------
    a["engine_matches_a5"] = engine_matches_a5(em)

    # --- retrieval completeness ----------------------------------------------
    viol = None
    if all_present:
        vals = [llm[("llm-rag", r)]["metrics"].get("retrieval_completeness_violations")
                for r in ("R1", "R2", "R3")]
        if all(v is not None for v in vals):
            viol = max(vals)
    a["retrieval_completeness_violations"] = viol

    # --- per-cell extraction gate (P10 analogue) ------------------------------
    gate_pass = {}
    if all_present:
        for c, rec in llm.items():
            m = rec["metrics"]
            n = m.get("n_queries") or 0
            succ = m.get("n_extraction_success", 0)
            lb = wilson(succ / n, n) if n else 0.0
            gate_pass[c] = lb >= EXTRACTION_LB
    rag_pass = any(gate_pass.get(("llm-rag", r)) for r in ("R1", "R2", "R3"))
    dir_pass = any(gate_pass.get(("llm-direct", r)) for r in ("R1", "R2", "R3"))

    out["gates"]["instrument_valid"] = bool(
        pins_ok and a["engine_matches_a5"] == 1 and rag_pass and dir_pass
        and viol == 0)

    a["n_queries"] = em.get("n_queries")
    a["n_covered"] = em.get("n_covered")
    a["n_control"] = em.get("n_control")

    # --- point estimates -------------------------------------------------------
    ev = em.get("item_conj")
    if not (isinstance(ev, list) and isinstance(cls, list)
            and len(ev) == len(cls) == N_QUERIES and all_present):
        return out
    n = N_QUERIES
    nc, ng = sum(cls), n - sum(cls)
    vecs = {c: llm[c]["metrics"]["item_conj"] for c in LLM_CELLS}
    if any(not isinstance(v, list) or len(v) != n for v in vecs.values()):
        return out

    def acc(vec, idx=None):
        if idx is None:
            return sum(vec) / n
        return sum(vec[i] for i in idx) / len(idx)

    def cov_ctl(vec, idx=None):
        if idx is None:
            cov = sum(v for v, c in zip(vec, cls) if c)
            return cov / nc, (sum(vec) - cov) / ng
        covn = covs = ctln = ctls = 0
        for i in idx:
            if cls[i]:
                covn += 1
                covs += vec[i]
            else:
                ctln += 1
                ctls += vec[i]
        return (covs / covn if covn else 0.0), (ctls / ctln if ctln else 0.0)

    eng_conj = acc(ev)
    eng_cov, eng_ctl = cov_ctl(ev)
    a["engine_conj_acc"] = eng_conj
    a["engine_covered_exact_rate"] = eng_cov
    a["engine_control_refusal_rate"] = eng_ctl
    a["engine_usd_per_query"] = usd_per_query_engine(em)

    # deterministic full-sample cell ordering (also the in-resample tie rank)
    def order_key(c):
        v = vecs[c]
        cov, ctl = cov_ctl(v)
        return (acc(v), cov, ctl, cell_name(*c))

    ranked = sorted(LLM_CELLS, key=order_key, reverse=True)
    rank_of = {c: i for i, c in enumerate(ranked)}
    valid_cells = [c for c in LLM_CELLS if gate_pass.get(c)]

    # --- cells table (descriptive) + cost/latency -----------------------------
    eng_lat_ms = None
    lat_ns = em.get("latency_ns")
    if isinstance(lat_ns, list) and lat_ns:
        eng_lat_ms = percentile([x / 1e6 for x in lat_ns], 0.50)
    cells_tbl = {}
    cost_ratios, lat_ratios = [], []
    e_usd = a["engine_usd_per_query"]
    for c in LLM_CELLS:
        rec = llm[c]
        m = rec["metrics"]
        cov, ctl = cov_ctl(vecs[c])
        usd = usd_per_query_llm(rec)
        lat = m.get("latency_ms") if isinstance(m.get("latency_ms"), list) else []
        p50 = percentile(lat, 0.50)
        p95 = percentile(lat, 0.95)
        tok = None
        flops = None
        if m.get("tokens_prompt_total") is not None and \
                m.get("tokens_decode_total") is not None:
            tok = (m["tokens_prompt_total"] + m["tokens_decode_total"]) / n
            flops = 2.0 * N_PARAMS[c[1]] * tok
        cells_tbl[cell_name(*c)] = {
            "arm": c[0], "rung": c[1],
            "conj_acc": acc(vecs[c]),
            "covered_exact_rate": cov,
            "control_refused_any_rate": ctl,
            "control_fabricated_rate": m.get("n_control_fabricated", 0) / ng,
            "extraction_success_rate": m.get("n_extraction_success", 0) / n,
            "extraction_gate_pass": bool(gate_pass.get(c)),
            "usd_per_query": usd,
            "latency_ms_p50": p50, "latency_ms_p95": p95,
            "mean_tokens_per_query": tok, "flops_per_query_2N": flops,
            "truncation_count": m.get("truncation_count"),
        }
        if usd is not None and e_usd:
            cost_ratios.append(usd / e_usd)
        if p50 is not None and eng_lat_ms:
            lat_ratios.append(p50 / eng_lat_ms)
    for arm_r0, name in ((eng, "engine-R0"), (ab, "abstain-all-R0"),
                         (aa, "answer-all-R0")):
        m = arm_r0["metrics"]
        v = m.get("item_conj", [])
        cov, ctl = cov_ctl(v) if len(v) == n else (None, None)
        cells_tbl[name] = {
            "arm": arm_r0["config"]["arm"], "rung": "R0",
            "conj_acc": acc(v) if len(v) == n else None,
            "covered_exact_rate": cov, "control_refused_any_rate":
                m.get("n_control_refused_any", 0) / ng,
            "note": ("STRICT a5 rules (engine) / descriptive bracket "
                     "(trivial arms; control conjunct = refused-any)"),
        }
    a["cells"] = cells_tbl
    a["cost_ratio_min"] = min(cost_ratios) if len(cost_ratios) == 6 else None
    a["latency_ratio_min"] = min(lat_ratios) if len(lat_ratios) == 6 else None
    a["truncation_counts"] = {cell_name(*c): llm[c]["metrics"].get("truncation_count")
                              for c in LLM_CELLS}

    # --- best-LLM selection (point) -------------------------------------------
    if not valid_cells:
        # no gate-valid cell: primary unresolvable; instrument gate already
        # false (needs >=1 rag AND >=1 direct) => INSTRUMENT-INVALID upstream
        return out
    best = min(valid_cells, key=lambda c: rank_of[c])
    a["best_llm_cell"] = cell_name(*best)
    best_conj = acc(vecs[best])
    a["best_llm_conj_acc"] = best_conj
    a["effect_size"] = eng_conj - best_conj

    # differentiator kill (a): point estimates, gate-valid cells only
    a["differentiator_within_kill"] = bool(any(
        eng_conj - acc(vecs[c]) <= KILL_MARGIN + 1e-12 for c in valid_cells))

    # fabrication (fixed point-selected best cell; denominator = all controls)
    fab_x = llm[best]["metrics"].get("n_control_fabricated", 0)
    fab_rate = fab_x / ng
    a["fabrication_rate_best_llm"] = fab_rate

    # --- separation gap (point) ------------------------------------------------
    d_r3, d_r1 = vecs[("llm-direct", "R3")], vecs[("llm-direct", "R1")]
    sep_pt = acc(d_r3) - acc(d_r1)
    a["separation_gap"] = sep_pt

    # --- statistics per index multiset -----------------------------------------
    r3g, r1g = vecs[("llm-rag", "R3")], vecs[("llm-rag", "R1")]

    def stats_for(idx=None):
        """Point statistics on an index multiset (None = full sample);
        best-LLM RESELECTED here — inside every resample and jackknife."""
        accs = {c: acc(vecs[c], idx) for c in valid_cells}
        b = min(valid_cells, key=lambda c: (-accs[c], rank_of[c]))
        e_conj = acc(ev, idx)
        e_cov, e_ctl = cov_ctl(ev, idx)
        b_cov, b_ctl = cov_ctl(vecs[b], idx)
        return {
            "effect": e_conj - accs[b],
            "covered_sup": e_cov - b_cov,
            "refusal_sup": e_ctl - b_ctl,
            "rag_lift": acc(r3g, idx) - acc(d_r3, idx),
            "scale_trend": acc(r3g, idx) - acc(r1g, idx),
            "sep": acc(d_r3, idx) - acc(d_r1, idx),
        }

    pt = stats_for()

    boot = {k: [] for k in pt}
    for _ in range(B):
        idx = [rng.randrange(n) for _ in range(n)]
        s = stats_for(idx)
        for k in pt:
            boot[k].append(s[k])

    jack = {k: [] for k in pt}
    idx_all = list(range(n))
    for i in range(n):
        idx = idx_all[:i] + idx_all[i + 1:]
        s = stats_for(idx)
        for k in pt:
            jack[k].append(s[k])

    # --- separation gate --------------------------------------------------------
    (sep_lb,) = bca_bounds(pt["sep"], boot["sep"], jack["sep"], [ALPHA])
    sep_valid = (pt["sep"] >= SEPARATION_MIN - 1e-12
                 and sep_lb is not None and sep_lb > 0.0)
    out["gates"]["separation_valid"] = bool(sep_valid)

    # --- PRIMARY -----------------------------------------------------------------
    p_lo, p_hi = bca_bounds(pt["effect"], boot["effect"], jack["effect"],
                            [ALPHA, 1 - ALPHA])
    a["primary_lower_onesided95"] = p_lo
    a["primary_upper_onesided95"] = p_hi
    a["primary_reject"] = bool(p_lo is not None and p_lo > SEOI)
    a["primary_p"] = one_sided_p(boot["effect"], SEOI)

    # --- Holm family F-secondary(a5-llm) ------------------------------------------
    members = [
        ("covered_superiority", one_sided_p(boot["covered_sup"], 0.0)),
        ("refusal_superiority", one_sided_p(boot["refusal_sup"], 0.0)),
        ("rag_lift_r3", one_sided_p(boot["rag_lift"], 0.0)),
        ("fabrication_material", binom_sf_p(fab_x, ng, FABRICATION_BAR)),
    ]
    p_scale = one_sided_p(boot["scale_trend"], 0.0)
    if sep_valid:
        members.append(("scale_trend_rag", p_scale))
    rejects = holm([p for _, p in members])
    for (name, p), rej in zip(members, rejects):
        ok = bool(rej)
        if name == "fabrication_material":
            # record verbatim: Wilson 95% lower bound > 0.30 required too
            ok = ok and wilson(fab_rate, ng) > FABRICATION_BAR
        a["holm"][name] = ok
        a["holm"][name + "_p"] = p
    if "scale_trend_rag" not in a["holm"]:
        # separation gate failed: INSTRUMENT-INVALID member, excluded from
        # the family BEFORE any p comparison; reported as non-reject (f2b
        # convention)
        a["holm"]["scale_trend_rag"] = False
        a["holm"]["scale_trend_rag_p"] = p_scale
    return out


# ------------------------------------------------------------------ selftest
def _pins():
    p = {"_recipe": "kot-corpus-hash/1 (fixture)"}
    for c, h in CORPUS_PINS.items():
        p["corpus_%s" % c] = {"observed": h, "recipe": "kot-corpus-hash/1"}
    return p


def _families_vec():
    """A deterministic item order consistent with PLANNED_STRATA: covered
    families first (855 items), then controls (122)."""
    covered_f = ("callers-of", "callees-of", "where-defined", "imports-of",
                 "imported-by", "contains", "contained-in", "instance-true",
                 "instance-false-disjoint")
    fams = []
    for f in covered_f:
        fams += [f] * PLANNED_STRATA[f]
    for f in sorted(PLANNED_STRATA):
        if f not in covered_f:
            fams += [f] * PLANNED_STRATA[f]
    assert len(fams) == N_QUERIES
    return fams


_FAMS = _families_vec()
_CLS = [1 if i < N_COVERED else 0 for i in range(N_QUERIES)]


def _by_family(conj):
    fam = {}
    for f, c in zip(_FAMS, conj):
        d = fam.setdefault(f, {"n": 0, "ok": 0})
        d["n"] += 1
        d["ok"] += c
    return fam


def _mk_llm(arm, rung, cov_ok, ctl_ref, ctl_fab, ext_fail, gpu_s=240.0):
    """Prefix-structured cell: first cov_ok covered items conj=1; first
    ctl_ref control items conj=1; ctl_fab fabricated; ext_fail extraction
    failures placed on always-conj-0 items (covered tail)."""
    conj = [1 if i < cov_ok else 0 for i in range(N_COVERED)] + \
           [1 if i < ctl_ref else 0 for i in range(N_CONTROL)]
    m = {"n_queries": N_QUERIES, "n_covered": N_COVERED, "n_control": N_CONTROL,
         "n_covered_exact": cov_ok, "n_control_refused_any": ctl_ref,
         "n_control_fabricated": ctl_fab,
         "n_extraction_success": N_QUERIES - ext_fail,
         "n_extraction_failure": ext_fail,
         "item_conj": conj, "item_class": list(_CLS),
         "by_family": _by_family(conj),
         "latency_ms": [250.0] * N_QUERIES, "truncation_count": 0,
         "tokens_prompt_total": 700 * N_QUERIES,
         "tokens_decode_total": 60 * N_QUERIES,
         "gpu_wall_seconds": gpu_s,
         "retrieval_completeness_violations": 0 if arm == "llm-rag" else None}
    return {"config": {"arm": arm, "rung": rung, "gpu_class": "A100",
                       "pack_sha256": "f" * 64},
            "metrics": m, "pins_observed": _pins()}


def _mk_engine(cov_ok=N_COVERED, ctl_ok=N_CONTROL, tamper_ref=False):
    conj = [1 if i < cov_ok else 0 for i in range(N_COVERED)] + \
           [1 if i < ctl_ok else 0 for i in range(N_CONTROL)]
    m = {"n_queries": N_QUERIES, "n_covered": N_COVERED, "n_control": N_CONTROL,
         "n_covered_exact": cov_ok, "n_covered_refused": 0,
         "n_covered_answered_wrong": N_COVERED - cov_ok,
         "n_control_refused_correct_code": ctl_ok,
         "n_control_refused_other_code": 0,
         "n_control_answered": N_CONTROL - ctl_ok,
         "n_control_refused_any": ctl_ok,
         "provenance_checked": N_COVERED, "provenance_all_valid": True,
         "by_family": _by_family(conj),
         "store": {"n_axiom_records": 5, "n_world_records": 889,
                   "n_entities": 402, "n_violations": 3,
                   "violations_by_code": {}, "n_incomplete_pairs": 0},
         "engine_total_ns": 7642000, "n_queries_": None,
         "latency_ns": [7821] * N_QUERIES,
         "item_conj": conj, "item_class": list(_CLS),
         "deterministic_repeat_identical": True}
    del m["n_queries_"]
    ref = {k: json.loads(json.dumps(m[k])) for k in A5_REFERENCE_KEYS}
    if tamper_ref:
        ref["n_covered_exact"] = cov_ok - 1
    m["a5_reference"] = {"source": "results-log/a5.jsonl", "source_seq": 0,
                         "metrics": ref}
    return {"config": {"arm": "engine", "rung": "R0"}, "metrics": m,
            "pins_observed": _pins()}


def _mk_trivial(arm):
    if arm == "abstain-all":
        conj = [0] * N_COVERED + [1] * N_CONTROL
        m = {"n_covered_exact": 0, "n_control_refused_any": N_CONTROL}
    else:
        conj = [1] * N_COVERED + [0] * N_CONTROL
        m = {"n_covered_exact": N_COVERED, "n_control_refused_any": 0}
    m.update({"n_queries": N_QUERIES, "n_covered": N_COVERED,
              "n_control": N_CONTROL, "item_conj": conj,
              "item_class": list(_CLS), "by_family": _by_family(conj)})
    return {"config": {"arm": arm, "rung": "R0"}, "metrics": m,
            "pins_observed": _pins()}


def _green():
    return [
        _mk_engine(),
        _mk_trivial("abstain-all"), _mk_trivial("answer-all"),
        # direct: R1 conj = (17+85)/977 ~ .1044; R3 = (154+49)/977 ~ .2078
        _mk_llm("llm-direct", "R1", 17, 85, 30, 7),
        _mk_llm("llm-direct", "R2", 34, 67, 48, 7),
        _mk_llm("llm-direct", "R3", 154, 49, 67, 6),
        # rag: R1 conj = (299+61)/977 ~ .3685; R3 = (513+49)/977 ~ .5752
        _mk_llm("llm-rag", "R1", 299, 61, 55, 6),
        _mk_llm("llm-rag", "R2", 385, 55, 61, 6),
        _mk_llm("llm-rag", "R3", 513, 49, 67, 6),
    ]


def selftest():
    B = 500
    out = analyze(_green(), B=B)
    g, a = out["gates"], out["analysis"]
    assert g["instrument_valid"] is True
    assert a["engine_matches_a5"] == 1
    assert a["retrieval_completeness_violations"] == 0
    # HAND: engine conj = 977/977 = 1.0
    assert abs(a["engine_conj_acc"] - 1.0) < 1e-12
    # HAND: best cell = llm-rag-R3, conj = (513+49)/977 = 562/977 = 0.575230...
    assert a["best_llm_cell"] == "llm-rag-R3"
    assert abs(a["best_llm_conj_acc"] - 562 / 977) < 1e-12
    # HAND: effect = 1 - 562/977 = 415/977 = 0.424769...
    assert abs(a["effect_size"] - 415 / 977) < 1e-12
    assert a["primary_reject"] is True and a["primary_p"] < 0.05
    assert a["primary_lower_onesided95"] > SEOI
    assert a["differentiator_within_kill"] is False
    # HAND: separation = (154+49)/977 - (17+85)/977 = 101/977 = 0.10337...
    assert abs(a["separation_gap"] - 101 / 977) < 1e-12
    assert g["separation_valid"] is True
    # HAND: engine usd/query = (7642000/977) ns * 0.135/3.6e12
    #     = 7821.9... * 3.75e-14 = 2.9332...e-10
    assert abs(a["engine_usd_per_query"] - (7642000 / 977) * 0.135 / 3.6e12) < 1e-24
    # HAND: llm usd/query = 240 * (2.10/3600) / 977 = 1.43296...e-4
    #       ratio = 1.43296e-4 / 2.9332e-10 = 488,529... > 1000
    want_llm_usd = 240 * (2.10 / 3600) / 977
    assert abs(a["cost_ratio_min"] - want_llm_usd / a["engine_usd_per_query"]) < 1e-6
    assert a["cost_ratio_min"] > COST_GATE
    # HAND: latency ratio = 250 ms / (7821 ns = 0.007821 ms) = 31965.2...
    assert abs(a["latency_ratio_min"] - 250.0 / 0.007821) < 1e-6
    # Holm family: all five members should reject on this construction
    for mname in ("covered_superiority", "refusal_superiority", "rag_lift_r3",
                  "scale_trend_rag", "fabrication_material"):
        assert a["holm"][mname] is True, (mname, a["holm"])
    # HAND: fabrication rate best cell = 67/122 = 0.54918; Wilson LB(z=1.645)
    # ~ 0.4746 > 0.30
    assert abs(a["fabrication_rate_best_llm"] - 67 / 122) < 1e-12

    # differentiator-kill flip: a rag cell within 0.05 of the engine
    recs = _green()
    recs[8] = _mk_llm("llm-rag", "R3", 833, 118, 4, 6)  # conj = 951/977 = .9734
    out2 = analyze(recs, B=200)
    assert out2["analysis"]["differentiator_within_kill"] is True
    # primary UB on ~0.026 effect must sit at/below the 0.10 margin (kill c)
    assert out2["analysis"]["primary_upper_onesided95"] <= SEOI

    # extraction-gate flip: every rag cell fails => INSTRUMENT-INVALID; the
    # failing cells leave best-LLM selection
    recs = _green()
    for i, rung in ((6, "R1"), (7, "R2"), (8, "R3")):
        recs[i] = _mk_llm("llm-rag", rung, 299, 61, 30, 200)  # 200/977 failures
    out3 = analyze(recs, B=200)
    assert out3["gates"]["instrument_valid"] is False
    assert out3["analysis"]["best_llm_cell"].startswith("llm-direct")

    # single-cell exclusion: only rag-R3 fails => still valid, best moves to
    # the next-highest gate-valid cell (rag-R2)
    recs = _green()
    recs[8] = _mk_llm("llm-rag", "R3", 513, 49, 67, 200)
    out4 = analyze(recs, B=200)
    assert out4["gates"]["instrument_valid"] is True
    assert out4["analysis"]["best_llm_cell"] == "llm-rag-R2"

    # engine-regression flip
    recs = _green()
    recs[0] = _mk_engine(tamper_ref=True)
    out5 = analyze(recs, B=200)
    assert out5["analysis"]["engine_matches_a5"] == 0
    assert out5["gates"]["instrument_valid"] is False

    # cost-kill visibility: tiny GPU wall time drives the ratio under 10^3
    recs = _green()
    for i, (arm, rung) in ((3, ("llm-direct", "R1")), (4, ("llm-direct", "R2")),
                           (5, ("llm-direct", "R3")), (6, ("llm-rag", "R1")),
                           (7, ("llm-rag", "R2")), (8, ("llm-rag", "R3"))):
        cell = _green()[i]
        cell["metrics"]["gpu_wall_seconds"] = 0.0001
        recs[i] = cell
    out6 = analyze(recs, B=200)
    assert out6["analysis"]["cost_ratio_min"] <= COST_GATE

    # separation-gate failure: direct R3 == R1 => scale_trend_rag leaves the
    # family (reported False), the absolute primary still reads
    recs = _green()
    recs[5] = _mk_llm("llm-direct", "R3", 17, 85, 30, 7)
    out7 = analyze(recs, B=300)
    assert out7["gates"]["separation_valid"] is False
    assert out7["analysis"]["holm"]["scale_trend_rag"] is False
    assert out7["analysis"]["primary_reject"] is True

    # missing-cell path: no llm records => gates false, primary unresolvable
    out8 = analyze([_mk_engine(), _mk_trivial("abstain-all"),
                    _mk_trivial("answer-all")], B=100)
    assert out8["gates"]["instrument_valid"] is False
    assert "effect_size" not in out8["analysis"]
    print("a5-llm selftest OK (B=%d)" % B)


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        records = [json.loads(l) for l in sys.stdin if l.strip()]
        print(json.dumps(analyze(records), sort_keys=True))
