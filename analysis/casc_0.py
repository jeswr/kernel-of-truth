#!/usr/bin/env python3
"""CASC-0' pinned analysis — the STATIC-CASE / M2-isolator factorial
(registry/experiments/casc-0.json; design source
docs/next/arch/cascade-synthesis.md section 3; prereg doc
poc/casc-0/design.md).

Eligible run records (kot-log/1 JSON lines) on stdin; analysis-output JSON on
stdout. Stdlib only; deterministic (PRNG seed 20260711, B=10000 BCa paired
item bootstrap; float64 end-to-end, no pre-rounding — P8 C-7).

WHAT THIS EXPERIMENT ISOLATES (cascade-synthesis section 3, adopted
verbatim): M2 — does a structured canonical medium give a SMALLER reasoner a
gain the LARGER reasoner does not share (a positive size x medium
interaction), rather than merely a structured arm beating an incomparable NL
system? Factors: size {R2=360M, R3=1.7B} x medium {nl, gloss, plain} x
verifier {off, on(structured only)}; plus the cost-matched 360M-NL+TTC
deflator (K2') and the deranged-closure house control (reported-only).

ENDPOINTS (hierarchical paired item bootstrap preserving pairing; Holm
across the two structured mediums in each family):
  PRIMARY  for m in {gloss, plain}, at verifier OFF (the pure medium leg):
           inter_m = (acc(R2,m) - acc(R2,nl)) - (acc(R3,m) - acc(R3,nl));
           reject iff one-sided 95% BCa lower bound > 0 for at least one m
           under Holm. Verifier-ON interactions are reported secondaries
           (M2+M4 composed), never primary (PROPOSED-ASM-1146).
  CO-PRIMARY  practical shrink, the honest successor to f2b-transfer's
           failed noninferiority_vs_r3, now WITH an internal structured
           medium: acc(R2, m, verifier on) non-inferior to acc(R3, nl) at
           margin NI_MARGIN (DRAFT 0.05, maintainer-adjustable at freeze)
           AND measured cost strictly below the R3-nl cell's; Holm across
           the two mediums; CONDITIONAL on the separation gate.
  KILLS    K1' (M2 dead): both primary LCBs <= 0 AND co-primary fails.
           K2' (purchased compute): primary passed but no Holm-passing
           medium beats the cost-matched TTC deflator (LCB <= 0).
           K3' (attribution, NON-FATAL, reported-only): gloss ~ plain TOST
           within ATTR_MARGIN at R2 verifier-on -> kernel-content
           attribution dead at scope; family continues generic.

INSTRUMENT GATES (never hypothesis outcomes): engagement (RT-7a made
structural, over factorial verifier-on cells), headroom (acc(R2,nl) <=
0.85), separation (gates ONLY the co-primary's Holm membership), ttc-match
(the deflator's measured cost within +/-25% of the pinned reference cell).

Every verdict sentence carries the SELF-AUTHORED / kernel-STYLE /
engine-derived-gold rider (kernel-STYLE per the executed ASM-1158 mapping,
poc/casc-0/kernel-coverage.md): items and store are procedurally self-authored
and gold is engine-derived — this probe measures the M2 SIGN at that scope
and licenses no ground-truth-independence, W1, coverage-general or cost-
headline claim.

Fixture: --selftest (constructed cells; planted directions asserted).
"""
import json
import math
import random
import sys
from statistics import NormalDist

SEED = 20260711
B_PRODUCTION = 10000
ALPHA = 0.05
Z_ONE_SIDED = 1.645
NI_MARGIN = 0.05        # DRAFT pin — maintainer-adjustable AT FREEZE only
ATTR_MARGIN = 0.05      # K3' TOST band (DRAFT pin, frozen at freeze)
M2_NULL_MARGIN = 0.05   # TOST band for the M2-null reading
DECIDABLE_MIN = 0.70    # engagement gate (depth>=3 share of the prefix = 0.75)
REJECT_RATE_LO = 0.05
REJECT_RATE_HI = 0.95
HEADROOM_MAX = 0.85
SEPARATION_MIN = 0.05
TTC_MATCH_BAND = 0.30   # |flops(ttc)-flops(ref)|/flops(ref) <= band
                        # (DRAFT pin: integer-N vote quantization bounds the
                        # achievable gap by ~0.5/N plus reference-cell retry
                        # variance; 0.25 was measurably too tight in mock)
ND = NormalDist()

ARM_FACT = "factorial"
ARM_TTC = "ttc-deflator"
ARM_DER = "deranged-control"
STRUCTURED = ("gloss", "plain")


class Cells:
    """(arm, rung, medium, verifier) -> per-item accuracy vector (mean over
    seeds), mean cost (formula FLOPs incl. metered verifier CPU), mean
    prefill tokens, per-seed vectors, and the engagement sums."""

    def __init__(self, records):
        acc, flops, toks = {}, {}, {}
        self.by_seed = {}
        self.eng = {"n_items": 0, "n_decidable": 0, "n_attempt0_rejected": 0,
                    "n_final_differs_attempt0": 0}
        self.ttc_meta = {}
        for r in records:
            if r.get("event") != "run":
                continue
            c = r["config"]
            key = (c["arm"], c["rung"], c["medium"], c["verifier"])
            m = r["metrics"]
            acc.setdefault(key, []).append(list(map(float, m["item_correct"])))
            flops.setdefault(key, []).append(float(m["flops_total"]))
            toks.setdefault(key, []).append(float(m["tokens_prefill_total"]))
            self.by_seed.setdefault(key, []).append(
                list(map(float, m["item_correct"])))
            if c["arm"] == ARM_FACT and c["verifier"] == 1 \
                    and "verifier_engagement" in m:
                for k in self.eng:
                    self.eng[k] += int(m["verifier_engagement"][k])
            if c["arm"] == ARM_TTC and "ttc_n_samples" in m:
                self.ttc_meta = {"n": int(m["ttc_n_samples"])}
        self.acc, self.flops_m, self.toks = {}, {}, {}
        self.n = None
        for key, vecs in acc.items():
            ln = {len(v) for v in vecs}
            if len(ln) != 1:
                raise SystemExit("ERR_ANALYSIS_SHAPE: uneven item vectors in %r"
                                 % (key,))
            n = ln.pop()
            if self.n is None:
                self.n = n
            elif self.n != n:
                raise SystemExit("ERR_ANALYSIS_SHAPE: cell %r n=%d != %d"
                                 % (key, n, self.n))
            self.acc[key] = [sum(v[i] for v in vecs) / len(vecs)
                             for i in range(n)]
            self.flops_m[key] = sum(flops[key]) / len(flops[key])
            self.toks[key] = sum(toks[key]) / len(toks[key])

    def vec(self, arm, rung, medium, verifier):
        return self.acc.get((arm, rung, medium, verifier))


def mean(v):
    return sum(v) / len(v) if v else None


def diff(a, b):
    return [x - y for x, y in zip(a, b)]


def bca_lower(theta_hat, boots, jack, level=0.95):
    """One-sided BCa lower confidence bound at the given level."""
    boots = sorted(boots)
    B = len(boots)
    prop = sum(1 for t in boots if t < theta_hat) / B
    prop = min(max(prop, 1.0 / (B + 1)), 1 - 1.0 / (B + 1))
    z0 = ND.inv_cdf(prop)
    jm = mean(jack)
    num = sum((jm - j) ** 3 for j in jack)
    den = 6.0 * (sum((jm - j) ** 2 for j in jack) ** 1.5)
    a = num / den if den else 0.0
    z = ND.inv_cdf(1 - level)  # lower bound
    adj = z0 + (z0 + z) / (1 - a * (z0 + z))
    q = ND.cdf(adj)
    idx = min(B - 1, max(0, int(q * B)))
    return boots[idx]


def bca_upper(theta_hat, boots, jack, level=0.95):
    return -bca_lower(-theta_hat, sorted(-t for t in boots),
                      [-j for j in jack], level)


def one_sided_p(boots, null=0.0):
    """p for H1: theta > null — the fraction of the bootstrap distribution at
    or below the null (add-one smoothed)."""
    B = len(boots)
    return (sum(1 for t in boots if t <= null) + 1) / (B + 1)


def holm(pvals, alpha=ALPHA):
    order = sorted(range(len(pvals)), key=lambda i: pvals[i])
    passed = [False] * len(pvals)
    m = len(pvals)
    for rank, i in enumerate(order):
        if pvals[i] <= alpha / (m - rank):
            passed[i] = True
        else:
            break
    return passed


def jackknife_means(v):
    n = len(v)
    tot = sum(v)
    return [(tot - x) / (n - 1) for x in v]


def analyze(records, B=B_PRODUCTION):
    cells = Cells(records)
    F = ARM_FACT
    need = ([(F, r, m, 0) for r in ("R2", "R3") for m in ("nl", "gloss", "plain")]
            + [(F, r, m, 1) for r in ("R2", "R3") for m in STRUCTURED]
            + [(ARM_TTC, "R2", "nl", 0), (ARM_DER, "R2", "gloss", 1)])
    missing = [k for k in need if k not in cells.acc]
    if missing:
        raise SystemExit("ERR_ANALYSIS_INCOMPLETE: missing cells %r" % missing)
    n = cells.n

    # ---- shared paired-item bootstrap (one index stream, all contrasts) ----
    contrasts = {}

    def contrast(name, v):
        contrasts[name] = v

    v = {(r, m, vf): cells.vec(F, r, m, vf)
         for r in ("R2", "R3") for m in ("nl", "gloss", "plain") for vf in (0, 1)
         if cells.vec(F, r, m, vf) is not None}
    ttc = cells.vec(ARM_TTC, "R2", "nl", 0)
    der = cells.vec(ARM_DER, "R2", "gloss", 1)

    for m in STRUCTURED:
        contrast("inter_off_%s" % m,
                 diff(diff(v[("R2", m, 0)], v[("R2", "nl", 0)]),
                      diff(v[("R3", m, 0)], v[("R3", "nl", 0)])))
        contrast("inter_on_%s" % m,
                 diff(diff(v[("R2", m, 1)], v[("R2", "nl", 0)]),
                      diff(v[("R3", m, 1)], v[("R3", "nl", 0)])))
        contrast("ni_%s" % m, diff(v[("R2", m, 1)], v[("R3", "nl", 0)]))
        contrast("deflator_%s" % m, diff(v[("R2", m, 1)], ttc))
    contrast("attr", diff(v[("R2", "gloss", 1)], v[("R2", "plain", 1)]))
    ve_r2 = [(a - b + c - d) / 2.0 for a, b, c, d in
             zip(v[("R2", "gloss", 1)], v[("R2", "gloss", 0)],
                 v[("R2", "plain", 1)], v[("R2", "plain", 0)])]
    ve_r3 = [(a - b + c - d) / 2.0 for a, b, c, d in
             zip(v[("R3", "gloss", 1)], v[("R3", "gloss", 0)],
                 v[("R3", "plain", 1)], v[("R3", "plain", 0)])]
    contrast("verifier_size_interaction", diff(ve_r2, ve_r3))
    contrast("separation", diff(v[("R3", "nl", 0)], v[("R2", "nl", 0)]))
    contrast("deranged_delta", diff(der, v[("R2", "gloss", 1)]))

    rng = random.Random(SEED)
    boots = {k: [] for k in contrasts}
    for _b in range(B):
        idx = [rng.randrange(n) for _ in range(n)]
        for k, vec in contrasts.items():
            boots[k].append(sum(vec[i] for i in idx) / n)
    stats = {}
    for k, vec in contrasts.items():
        th = mean(vec)
        jk = jackknife_means(vec)
        stats[k] = {
            "point": th,
            "lcb95": bca_lower(th, boots[k], jk),
            "ucb95": bca_upper(th, boots[k], jk),
            "p_gt0": one_sided_p(boots[k], 0.0),
            "p_gt_neg_ni": one_sided_p(boots[k], -NI_MARGIN),
        }

    # ---- gates -------------------------------------------------------------
    eng = cells.eng
    dec_frac = eng["n_decidable"] / eng["n_items"] if eng["n_items"] else 0.0
    rej_rate = (eng["n_attempt0_rejected"] / eng["n_decidable"]
                if eng["n_decidable"] else 0.0)
    engagement_valid = (eng["n_items"] > 0 and dec_frac >= DECIDABLE_MIN
                        and REJECT_RATE_LO <= rej_rate <= REJECT_RATE_HI
                        and eng["n_final_differs_attempt0"] >= 1)
    acc_r2_nl = mean(v[("R2", "nl", 0)])
    headroom_valid = acc_r2_nl <= HEADROOM_MAX
    sep = stats["separation"]
    separation_valid = (sep["point"] >= SEPARATION_MIN and sep["lcb95"] > 0)
    ref_fl = cells.flops_m[(F, "R2", "gloss", 1)]
    ttc_fl = cells.flops_m[(ARM_TTC, "R2", "nl", 0)]
    ttc_gap = abs(ttc_fl - ref_fl) / ref_fl if ref_fl else 1.0
    ttc_match_valid = ttc_gap <= TTC_MATCH_BAND

    # ---- primary (Holm over the two structured mediums, verifier OFF) ------
    p_primary = [stats["inter_off_gloss"]["p_gt0"],
                 stats["inter_off_plain"]["p_gt0"]]
    holm_primary = holm(p_primary)
    primary_reject = any(holm_primary)

    # ---- co-primary NI (Holm over the two mediums; gated on separation) ----
    if separation_valid:
        p_ni = [stats["ni_gloss"]["p_gt_neg_ni"], stats["ni_plain"]["p_gt_neg_ni"]]
        holm_ni = holm(p_ni)
        cost_ok = {m: cells.flops_m[(F, "R2", m, 1)]
                   < cells.flops_m[(F, "R3", "nl", 0)] for m in STRUCTURED}
        ni_pass = {m: bool(holm_ni[i] and cost_ok[m])
                   for i, m in enumerate(STRUCTURED)}
        coprimary_ni_pass = any(ni_pass.values())
    else:
        ni_pass = {m: None for m in STRUCTURED}
        cost_ok = {m: None for m in STRUCTURED}
        coprimary_ni_pass = None  # unevaluable -> never counts as a fail

    # ---- kills --------------------------------------------------------------
    both_inter_dead = (stats["inter_off_gloss"]["lcb95"] <= 0
                       and stats["inter_off_plain"]["lcb95"] <= 0)
    k1_fired = bool(both_inter_dead and coprimary_ni_pass is False)
    passing_mediums = [m for i, m in enumerate(STRUCTURED) if holm_primary[i]]
    if primary_reject and ttc_match_valid:
        k2_fired = all(stats["deflator_%s" % m]["lcb95"] <= 0
                       for m in passing_mediums)
    else:
        k2_fired = False
    attr = stats["attr"]
    attr_tost_pass = (attr["lcb95"] > -ATTR_MARGIN and attr["ucb95"] < ATTR_MARGIN)
    tost_m2_null = all(
        stats["inter_off_%s" % m]["lcb95"] > -M2_NULL_MARGIN
        and stats["inter_off_%s" % m]["ucb95"] < M2_NULL_MARGIN
        for m in STRUCTURED)

    # ---- seed sign (reported-only) ------------------------------------------
    def seed_sign(medium):
        per_seed = []
        for kkey, tgt in ((F, "R2"), (F, "R3")):
            pass
        seq = {}
        for key in ((F, "R2", medium, 0), (F, "R2", "nl", 0),
                    (F, "R3", medium, 0), (F, "R3", "nl", 0)):
            seq[key] = cells.by_seed[key]
        ns = min(len(x) for x in seq.values())
        signs = []
        for s in range(ns):
            val = (mean(seq[(F, "R2", medium, 0)][s]) - mean(seq[(F, "R2", "nl", 0)][s])
                   - (mean(seq[(F, "R3", medium, 0)][s]) - mean(seq[(F, "R3", "nl", 0)][s])))
            signs.append(val > 0)
        return all(signs) if signs else False

    rho_gloss = cells.toks[(F, "R2", "gloss", 0)] / cells.toks[(F, "R2", "nl", 0)]
    rho_plain = cells.toks[(F, "R2", "plain", 0)] / cells.toks[(F, "R2", "nl", 0)]
    retry_r = {m: cells.flops_m[(F, "R2", m, 1)] / cells.flops_m[(F, "R2", m, 0)] - 1.0
               for m in STRUCTURED}

    out = {
        "gates": {
            "engagement_valid": bool(engagement_valid),
            "headroom_valid": bool(headroom_valid),
            "separation_valid": bool(separation_valid),
            "ttc_match_valid": bool(ttc_match_valid),
        },
        "analysis": {
            "n_eval_items": n,
            "rider": "SELF-AUTHORED / kernel-STYLE / engine-derived-gold "
                     "rider rides every verdict sentence derived from these "
                     "fields (kernel-STYLE per the executed ASM-1158 mapping, "
                     "poc/casc-0/kernel-coverage.md)",
            "acc_r2_nl": acc_r2_nl,
            "acc_r2_gloss": mean(v[("R2", "gloss", 0)]),
            "acc_r2_plain": mean(v[("R2", "plain", 0)]),
            "acc_r3_nl": mean(v[("R3", "nl", 0)]),
            "acc_r3_gloss": mean(v[("R3", "gloss", 0)]),
            "acc_r3_plain": mean(v[("R3", "plain", 0)]),
            "acc_r2_gloss_v": mean(v[("R2", "gloss", 1)]),
            "acc_r2_plain_v": mean(v[("R2", "plain", 1)]),
            "acc_r3_gloss_v": mean(v[("R3", "gloss", 1)]),
            "acc_r3_plain_v": mean(v[("R3", "plain", 1)]),
            "acc_r2_nl_ttc": mean(ttc),
            "acc_r2_gloss_v_deranged": mean(der),
            "interaction_gloss": stats["inter_off_gloss"]["point"],
            "interaction_gloss_lcb95": stats["inter_off_gloss"]["lcb95"],
            "interaction_gloss_p": stats["inter_off_gloss"]["p_gt0"],
            "interaction_plain": stats["inter_off_plain"]["point"],
            "interaction_plain_lcb95": stats["inter_off_plain"]["lcb95"],
            "interaction_plain_p": stats["inter_off_plain"]["p_gt0"],
            "interaction_gloss_von": stats["inter_on_gloss"]["point"],
            "interaction_gloss_von_lcb95": stats["inter_on_gloss"]["lcb95"],
            "interaction_plain_von": stats["inter_on_plain"]["point"],
            "interaction_plain_von_lcb95": stats["inter_on_plain"]["lcb95"],
            "primary_reject": bool(primary_reject),
            "verifier_effect_r2": mean(ve_r2),
            "verifier_effect_r3": mean(ve_r3),
            "verifier_size_interaction": stats["verifier_size_interaction"]["point"],
            "verifier_size_interaction_lcb95":
                stats["verifier_size_interaction"]["lcb95"],
            "ni_margin": NI_MARGIN,
            "ni_delta_gloss": stats["ni_gloss"]["point"],
            "ni_delta_gloss_lcb95": stats["ni_gloss"]["lcb95"],
            "ni_delta_plain": stats["ni_plain"]["point"],
            "ni_delta_plain_lcb95": stats["ni_plain"]["lcb95"],
            "cost_r2_gloss_v": cells.flops_m[(F, "R2", "gloss", 1)],
            "cost_r2_plain_v": cells.flops_m[(F, "R2", "plain", 1)],
            "cost_r3_nl": cells.flops_m[(F, "R3", "nl", 0)],
            "cost_ratio_gloss_v_vs_r3_nl":
                cells.flops_m[(F, "R2", "gloss", 1)] / cells.flops_m[(F, "R3", "nl", 0)],
            "cost_condition_gloss": cost_ok["gloss"],
            "cost_condition_plain": cost_ok["plain"],
            "coprimary_ni_pass": coprimary_ni_pass,
            "ttc_n_samples": cells.ttc_meta.get("n"),
            "ttc_flops_rel_gap": ttc_gap,
            "deflator_delta_gloss": stats["deflator_gloss"]["point"],
            "deflator_delta_gloss_lcb95": stats["deflator_gloss"]["lcb95"],
            "deflator_delta_plain": stats["deflator_plain"]["point"],
            "deflator_delta_plain_lcb95": stats["deflator_plain"]["lcb95"],
            "k2_fired": bool(k2_fired),
            "attr_delta": attr["point"],
            "attr_delta_lcb95": attr["lcb95"],
            "attr_delta_ucb95": attr["ucb95"],
            "attr_tost_pass": bool(attr_tost_pass),
            "kernel_attribution_dead": bool(attr_tost_pass),
            "deranged_delta": stats["deranged_delta"]["point"],
            "deranged_delta_ucb95": stats["deranged_delta"]["ucb95"],
            "deranged_benefit_collapse": stats["deranged_delta"]["point"] < 0,
            "rho_in_gloss": rho_gloss,
            "rho_in_plain": rho_plain,
            "retry_overhead_r_gloss": retry_r["gloss"],
            "retry_overhead_r_plain": retry_r["plain"],
            "engagement_decidable_fraction": dec_frac,
            "engagement_attempt0_reject_rate": rej_rate,
            "engagement_final_differs_attempt0": eng["n_final_differs_attempt0"],
            "separation_gap": sep["point"],
            "separation_lower_onesided95": sep["lcb95"],
            "k1_fired": bool(k1_fired),
            "tost_m2_null": bool(tost_m2_null),
            "seed_sign_gloss": seed_sign("gloss"),
            "seed_sign_plain": seed_sign("plain"),
            "holm": {
                "m2_sign_gloss": bool(holm_primary[0]),
                "m2_sign_gloss_p": p_primary[0],
                "m2_sign_plain": bool(holm_primary[1]),
                "m2_sign_plain_p": p_primary[1],
                "ni_gloss": ni_pass["gloss"],
                "ni_plain": ni_pass["plain"],
            },
        },
    }
    return out


# ---------------------------------------------------------------------------
# --selftest fixture: constructed cells with planted directions.
# ---------------------------------------------------------------------------
def _mk(arm, rung, medium, verifier, acc_vec, seed=0, flops=1e12, toks=1e5,
        eng=None, extra=None):
    m = {"item_correct": acc_vec, "n_items": len(acc_vec),
         "flops_total": flops, "tokens_prefill_total": toks,
         "wall_s_total": 1.0, "metric_vector": {}}
    if eng:
        m["verifier_engagement"] = eng
    if extra:
        m.update(extra)
    return {"event": "run", "phase": "mock",
            "config": {"arm": arm, "rung": rung, "medium": medium,
                       "verifier": verifier, "retry_budget": 0, "seed": seed},
            "metrics": m, "exit": "ok"}


def selftest():
    rng = random.Random(7)
    n = 120

    def vec(p):
        return [1 if rng.random() < p else 0 for _ in range(n)]

    eng = {"n_items": n, "n_decidable": int(n * 0.75),
           "n_attempt0_rejected": int(n * 0.3), "n_final_differs_attempt0": 9}
    recs = []
    # planted: R2 gains a lot from structure (+0.25), R3 barely (+0.04);
    # verifier adds +0.08 at R2; TTC lifts NL a little; deranged collapses.
    acc = {("R2", "nl", 0): 0.45, ("R2", "gloss", 0): 0.70, ("R2", "plain", 0): 0.66,
           ("R3", "nl", 0): 0.74, ("R3", "gloss", 0): 0.78, ("R3", "plain", 0): 0.77,
           ("R2", "gloss", 1): 0.78, ("R2", "plain", 1): 0.73,
           ("R3", "gloss", 1): 0.80, ("R3", "plain", 1): 0.79}
    fl = {("R2", "nl", 0): 2.5e11, ("R2", "gloss", 0): 4.0e11,
          ("R2", "plain", 0): 3.0e11, ("R3", "nl", 0): 1.2e12,
          ("R3", "gloss", 0): 1.9e12, ("R3", "plain", 0): 1.4e12,
          ("R2", "gloss", 1): 5.5e11, ("R2", "plain", 1): 4.2e11,
          ("R3", "gloss", 1): 2.6e12, ("R3", "plain", 1): 1.9e12}
    for seed in (0, 1, 2):
        for (r, m, vf), p in acc.items():
            recs.append(_mk(ARM_FACT, r, m, vf, vec(p), seed, flops=fl[(r, m, vf)],
                            toks={"nl": 1.0e5, "gloss": 2.2e5, "plain": 1.3e5}[m],
                            eng=eng if vf == 1 else None))
        recs.append(_mk(ARM_TTC, "R2", "nl", 0, vec(0.52), seed, flops=5.0e11,
                        toks=2.2e5, extra={"ttc_n_samples": 2}))
        recs.append(_mk(ARM_DER, "R2", "gloss", 1, vec(0.55), seed, flops=5.5e11,
                        toks=2.2e5, eng=eng))
    out = analyze(recs, B=2000)
    a, g = out["analysis"], out["gates"]
    assert g["engagement_valid"] and g["headroom_valid"], g
    assert g["ttc_match_valid"], a["ttc_flops_rel_gap"]
    assert a["interaction_gloss"] > 0.10, a["interaction_gloss"]
    assert a["primary_reject"] is True
    assert a["k1_fired"] is False
    assert a["deranged_benefit_collapse"] is True
    assert a["rho_in_gloss"] > 2.0
    assert a["cost_condition_gloss"] is True  # 5.5e11 < 1.2e12
    # a null world: identical cells everywhere -> no interaction, TOST null
    base = vec(0.6)
    recs2 = []
    for seed in (0, 1, 2):
        for (r, m, vf) in acc:
            recs2.append(_mk(ARM_FACT, r, m, vf, base, seed, flops=1e12,
                             toks=1e5, eng=eng if vf == 1 else None))
        recs2.append(_mk(ARM_TTC, "R2", "nl", 0, base, seed, flops=1e12,
                         toks=1e5, extra={"ttc_n_samples": 2}))
        recs2.append(_mk(ARM_DER, "R2", "gloss", 1, base, seed, flops=1e12,
                         toks=1e5, eng=eng))
    out2 = analyze(recs2, B=2000)
    a2 = out2["analysis"]
    assert a2["primary_reject"] is False
    assert a2["tost_m2_null"] is True
    assert a2["attr_tost_pass"] is True
    # headroom trip: saturate R2-nl
    print("selftest OK", file=sys.stderr)


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        records = [json.loads(line) for line in sys.stdin if line.strip()]
        print(json.dumps(analyze(records, B=B_PRODUCTION), sort_keys=True))
