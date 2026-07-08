#!/usr/bin/env python3
"""f2 pinned analysis — HE1 verifier-offload (+HE2 cascade, HC3 PRM, HS12 rider).

Implements the P8 §3.2 worked-example SAP for experiment F2
(P1 §3 HE1/HE2/HC3; kill text incl. the P7 RT-2 arm-10 amendment; P10
extraction-failure instrument gate). Eligible run records (kot-log/1 JSON
lines) on stdin; analysis-output JSON on stdout. Stdlib only; deterministic
(PRNG seed 20260708, B=10000 BCa bootstrap; float64 end-to-end, no
pre-rounding — P8 C-7).

Input contract (config keys are declared IVs; item vectors are RAW 0/1 lists —
P2 §2.4 allows per-item outcomes, forbids derived stats):
  config.arm     one of the frozen arm levels (see ARM_* constants)
  config.rung    R1|R2|R3 (host-model rung; cascades logged at the small rung)
  config.retry_budget       k in {0,1,2,4} (0 = arm has no retry loop)
  config.escalation_budget  cascade expected-large-call budget in {0, 0.1, 0.25, 0.5}
  config.seed    registered sampling seed
  metrics.item_correct            [0/1 ...] kernel-covered slice, pinned item order
  metrics.item_correct_external   [0/1 ...] D-EXT external slice (RT-7a secondary)
  metrics.metric_vector.inference_compute.flops_per_query   (F0 §3.3 accounting)
  arm "extraction-instrument" runs instead carry
  metrics.n_labelled / metrics.n_extraction_failures  (P10 held-out labelled set)

Estimand (P8 §1.2, verbatim discipline): gap_closed(s,S) =
(acc_verify − acc_s)/(acc_S − acc_s), accuracies = mean per-item kernel-covered
accuracy, verify at the best pre-registered retry budget k in {1,2,4} selected
on accuracy (tie -> smaller k = fewer FLOPs); the selection runs INSIDE every
bootstrap resample so selection uncertainty is inside the CI (P8 §1.7).

Output fields — the frozen record's pins.analysis_script.output_fields list.
Missing arms/cells make fields unresolvable and the verdict INCOMPLete-DATA
(fail closed at verdict-gen step 7); nothing is imputed (P8 §1.7).

Fixture: --selftest (constructed cells; HAND-COMPUTED point values:
gap_R1R2 = (0.8-0.5)/(0.9-0.5) = 0.75; gap_R2R3 = (0.93-0.9)/(0.95-0.9) = 0.6;
cost_ratio 2e11/4e11 = 0.5; extraction 15/300 -> Wilson lb 0.03259 <= 0.10).
"""
import json
import math
import sys
from statistics import NormalDist

SEED = 20260708
B_PRODUCTION = 10000
Z_ONE_SIDED = 1.645
ALPHA = 0.05
GAP_BAR = 0.5           # kill clause (a): <50% of the s->S gap closed
TOST_MARGIN_H = 0.2     # P8 §1.5 paired-proportion margin
IFACE_FAIL_BOUND = 0.10  # P10: extraction-failure Wilson-LB > 10% => INSTRUMENT-INVALID
ND = NormalDist()

ARM_ALONE = "model-alone"
ARM_VERIFY = "kernel-verify-retry"
ARM_TEXT = "kernel-as-text"
ARM_RAG = "rag-over-text"
ARM_SC = "self-consistency-flop-matched"
ARM_SELFV = "gloss-self-verify-retry"
ARM_PRM = "prm-verifier"
ARM_INT4 = "int4-quantized"
ARM_CV = "cascade-verifier-gated-135m-1p7b"
ARM_CL = "cascade-logprob-gated-135m-1p7b"
ARM_CT = "cascade-text-self-check-gated-135m-1p7b"
ARM_CD = "cascade-in-decode-gated-135m-1p7b"
ARM_IFACE = "extraction-instrument"
RETRY_KS = (1, 2, 4)


def wilson_lb(p, n, z=Z_ONE_SIDED):
    if n <= 0:
        return 0.0
    z2 = z * z
    centre = p + z2 / (2 * n)
    spread = z * ((p * (1 - p) / n + z2 / (4 * n * n)) ** 0.5)
    return (centre - spread) / (1 + z2 / n)


def cohens_h(p1, p2):
    clamp = lambda p: min(max(p, 0.0), 1.0)
    return 2 * math.asin(math.sqrt(clamp(p1))) - 2 * math.asin(math.sqrt(clamp(p2)))


class Cells:
    """(arm, rung, k_or_budget) -> per-item accuracy vector (mean over seeds) + flops."""

    def __init__(self, records):
        acc, acc_ext = {}, {}
        self.flops = {}
        self.iface = {}
        self.by_seed = {}
        for r in records:
            cfg, m = r["config"], r["metrics"]
            arm, rung = cfg["arm"], cfg["rung"]
            if arm == ARM_IFACE:
                s = self.iface.setdefault(rung, {"n": 0, "fail": 0})
                s["n"] += int(m["n_labelled"])
                s["fail"] += int(m["n_extraction_failures"])
                continue
            key = (arm, rung, int(cfg.get("retry_budget", 0) or 0),
                   float(cfg.get("escalation_budget", 0) or 0))
            acc.setdefault(key, []).append([int(x) for x in m["item_correct"]])
            self.by_seed.setdefault(key, {})[cfg.get("seed", 0)] = [
                int(x) for x in m["item_correct"]]
            if "item_correct_external" in m:
                acc_ext.setdefault(key, []).append(
                    [int(x) for x in m["item_correct_external"]])
            fl = m.get("metric_vector", {}).get("inference_compute", {}).get("flops_per_query")
            if fl is not None:
                self.flops.setdefault(key, []).append(float(fl))
        self.items, self.items_ext = {}, {}
        for src, dst in ((acc, self.items), (acc_ext, self.items_ext)):
            for key, seed_vecs in src.items():
                n = len(seed_vecs[0])
                if any(len(v) != n for v in seed_vecs):
                    print("f2-analysis: item-vector length mismatch in cell %r" % (key,),
                          file=sys.stderr)
                    sys.exit(1)
                dst[key] = [sum(v[i] for v in seed_vecs) / len(seed_vecs)
                            for i in range(n)]

    def vec(self, arm, rung, k=0, b=0.0, ext=False):
        key = (arm, rung, k, float(b))
        return (self.items_ext if ext else self.items).get(key)

    def mean_flops(self, arm, rung, k=0, b=0.0):
        v = self.flops.get((arm, rung, k, float(b)))
        return sum(v) / len(v) if v else None


def acc_of(vec, idx=None):
    if idx is None:
        return sum(vec) / len(vec)
    return sum(vec[i] for i in idx) / len(idx)


def best_k(cells, arm, rung, idx=None):
    """Accuracy-max retry-budget selection, tie -> smaller k (fewer FLOPs)."""
    best, best_acc = None, -1.0
    for k in RETRY_KS:
        v = cells.vec(arm, rung, k=k)
        if v is None:
            continue
        a = acc_of(v, idx)
        if a > best_acc + 1e-15:
            best, best_acc = k, a
    return best, best_acc


def gap_fraction(cells, s_rung, S_rung, verify_arm_rung, idx=None):
    a_s = cells.vec(ARM_ALONE, s_rung)
    a_S = cells.vec(ARM_ALONE, S_rung)
    if a_s is None or a_S is None:
        return None, None
    k, acc_v = best_k(cells, ARM_VERIFY, verify_arm_rung, idx)
    if k is None:
        return None, None
    acc_s, acc_S = acc_of(a_s, idx), acc_of(a_S, idx)
    denom = acc_S - acc_s
    if abs(denom) < 1e-12:
        return None, k
    return (acc_v - acc_s) / denom, k


def bca_bounds(theta_hat, thetas, jack, levels):
    """BCa bounds at the given lower-tail levels (P8 §1.7: BCa from item jackknife)."""
    b = len(thetas)
    below = sum(1 for t in thetas if t < theta_hat)
    z0 = ND.inv_cdf(min(max(below / b, 1.0 / (b + 1)), b / (b + 1.0)))
    jbar = sum(jack) / len(jack)
    num = sum((jbar - j) ** 3 for j in jack)
    den = 6.0 * (sum((jbar - j) ** 2 for j in jack) ** 1.5)
    a = 0.0 if den == 0 else num / den
    out = []
    srt = sorted(thetas)
    for lv in levels:
        z = ND.inv_cdf(lv)
        adj = ND.cdf(z0 + (z0 + z) / (1 - a * (z0 + z)))
        pos = min(max(int(adj * b), 0), b - 1)
        out.append(srt[pos])
    return out


def one_sided_p(diffs_boot, observed_null=0.0):
    """Bootstrap one-sided p: share of resampled statistics <= the null value."""
    b = len(diffs_boot)
    return (1 + sum(1 for d in diffs_boot if d <= observed_null)) / (b + 1)


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


def analyze(records, B=B_PRODUCTION):
    import random
    rng = random.Random(SEED)
    cells = Cells(records)
    out = {"gates": {}, "analysis": {"holm": {}}}
    a = out["analysis"]

    # --- P10 extraction-failure instrument gate (RT-3): failures are instrument
    # events; the gate must be measured (>=300 labelled outputs) at every rung
    # where the verifier arm ran, and its failure-rate Wilson-LB must be <= 10%.
    verify_rungs = {rung for (arm, rung, _, _) in cells.items if arm == ARM_VERIFY}
    iface_ok = bool(verify_rungs)
    for rung in verify_rungs:
        st = cells.iface.get(rung)
        if not st or st["n"] < 300:
            iface_ok = False
            break
        if wilson_lb(st["fail"] / st["n"], st["n"]) > IFACE_FAIL_BOUND:
            iface_ok = False
            break
    out["gates"]["instrument_valid"] = iface_ok

    # --- point estimates -------------------------------------------------
    gap12, k12 = gap_fraction(cells, "R1", "R2", "R1")
    gap23, k23 = gap_fraction(cells, "R2", "R3", "R2")
    if gap12 is None:
        return out  # unresolvable pointers => INCOMPLETE-DATA downstream (fail closed)
    a["gap_closed_fraction_R1R2"] = gap12
    a["best_retry_budget"] = k12
    if gap23 is not None:
        a["gap_closed_fraction_R2R3"] = gap23
    a["gap_below_half"] = gap12 < GAP_BAR

    n_items = len(cells.vec(ARM_ALONE, "R1"))
    a["n_items"] = n_items
    idx_all = list(range(n_items))

    # kill clause (b): does any matched-budget competitor close as much gap at
    # <= the verifier's FLOPs/query? (point estimates + F0 FLOPs ledger)
    v_flops = cells.mean_flops(ARM_VERIFY, "R1", k=k12)
    acc_s = acc_of(cells.vec(ARM_ALONE, "R1"))
    acc_S = acc_of(cells.vec(ARM_ALONE, "R2"))
    closes = False
    for arm in (ARM_TEXT, ARM_SC, ARM_SELFV):
        kk = 0
        vec = cells.vec(arm, "R1")
        if vec is None and arm == ARM_SELFV:
            kk, _ = best_k(cells, ARM_SELFV, "R1")
            vec = cells.vec(arm, "R1", k=kk) if kk else None
        if vec is None:
            continue
        gap_c = (acc_of(vec) - acc_s) / (acc_S - acc_s)
        fl_c = cells.mean_flops(arm, "R1", k=kk)
        if gap_c >= gap12 - 1e-12 and (fl_c is not None and v_flops is not None
                                       and fl_c <= v_flops * (1 + 1e-9)):
            closes = True
    a["competitor_closes_asmuch"] = closes

    S_flops = cells.mean_flops(ARM_ALONE, "R2")
    if v_flops is not None and S_flops:
        a["cost_ratio_vs_S"] = v_flops / S_flops

    # --- paired bootstrap (items resampled; best-k reselected per resample) --
    boot_gap12, boot_gap23 = [], []
    diffs = {"text_null": [], "self_verify": [], "prm": [], "external": []}
    cascade_budgets = sorted({key[3] for key in cells.items
                              if key[0] == ARM_CV and key[3] > 0})
    boot_cascade = {b_: [] for b_ in cascade_budgets}
    v_vec_bestk = cells.vec(ARM_VERIFY, "R1", k=k12)
    sv_k, _ = best_k(cells, ARM_SELFV, "R1")
    for _ in range(B):
        idx = [rng.randrange(n_items) for _ in range(n_items)]
        g12, _k = gap_fraction(cells, "R1", "R2", "R1", idx)
        if g12 is not None:
            boot_gap12.append(g12)
        g23, _k = gap_fraction(cells, "R2", "R3", "R2", idx)
        if g23 is not None:
            boot_gap23.append(g23)
        _kb, acc_vb = best_k(cells, ARM_VERIFY, "R1", idx)
        for name, arm, k in (("text_null", ARM_TEXT, 0),
                             ("self_verify", ARM_SELFV, sv_k or 0),
                             ("prm", ARM_PRM, 0)):
            vec = cells.vec(arm, "R1", k=k)
            if vec is not None:
                diffs[name].append(acc_vb - acc_of(vec, idx))
        ev, e1 = (cells.vec(ARM_VERIFY, "R1", k=k12, ext=True),
                  cells.vec(ARM_ALONE, "R1", ext=True))
        if ev is not None and e1 is not None:
            n_ext = len(ev)
            eidx = [rng.randrange(n_ext) for _ in range(n_ext)]
            diffs["external"].append(acc_of(ev, eidx) - acc_of(e1, eidx))
        for b_ in cascade_budgets:
            cv = cells.vec(ARM_CV, "R1", b=b_)
            comp = [cells.vec(arm_, "R1", b=b_) for arm_ in (ARM_CL, ARM_CT)]
            comp = [c for c in comp if c is not None]
            if cv is not None and comp:
                boot_cascade[b_].append(
                    acc_of(cv, idx) - max(acc_of(c, idx) for c in comp))

    # primary: one-sided test that gap12 clears the 0.5 bar (CI-bound discipline)
    jack = []
    for i in range(n_items):
        idx = idx_all[:i] + idx_all[i + 1:]
        g, _ = gap_fraction(cells, "R1", "R2", "R1", idx)
        jack.append(g if g is not None else gap12)
    lo95, lo90, hi90, hi95 = bca_bounds(gap12, boot_gap12, jack,
                                        [0.025, 0.05, 0.95, 0.975])
    a["primary_reject"] = lo90 > GAP_BAR   # one-sided 95% lower bound clears the bar
    a["primary_p"] = one_sided_p(boot_gap12, GAP_BAR)
    a["effect_size"] = gap12
    a["effect_ci_low"], a["effect_ci_high"] = lo95, hi95

    # secondaries: one pre-declared Holm family (P8 §1.4 F-secondary(f2))
    sec = []
    if diffs["text_null"]:
        sec.append(("beats_text_null", one_sided_p(diffs["text_null"])))
    if diffs["self_verify"]:
        sec.append(("beats_gloss_self_verify", one_sided_p(diffs["self_verify"])))
    if boot_gap23:
        sec.append(("pair_r2r3", one_sided_p(boot_gap23, GAP_BAR)))
    if cascade_budgets and all(boot_cascade[b_] for b_ in cascade_budgets):
        # HE2 dominance = IUT across budgets: the family p is the worst budget p
        sec.append(("cascade_dominance",
                    max(one_sided_p(boot_cascade[b_]) for b_ in cascade_budgets)))
    if diffs["prm"]:
        sec.append(("prm_beaten", one_sided_p(diffs["prm"])))
    if diffs["external"]:
        sec.append(("external_slice", one_sided_p(diffs["external"])))
    rejects = holm([p for _, p in sec])
    for (name, p), rej in zip(sec, rejects):
        a["holm"][name] = bool(rej)
        a["holm"][name + "_p"] = p
    a["beats_text_null"] = a["holm"].get("beats_text_null", False)
    a["beats_gloss_self_verify"] = a["holm"].get("beats_gloss_self_verify", False)

    # TOST vs the strongest active text baseline (arm 10) at margin h = 0.2:
    # 90% bootstrap CI of the h-difference inside (-0.2, 0.2) => equivalence.
    sv_vec = cells.vec(ARM_SELFV, "R1", k=sv_k or 0)
    if sv_vec is not None and v_vec_bestk is not None:
        hs = []
        for _ in range(B):
            idx = [rng.randrange(n_items) for _ in range(n_items)]
            hs.append(cohens_h(acc_of(v_vec_bestk, idx), acc_of(sv_vec, idx)))
        hs.sort()
        lo = hs[max(0, int(0.05 * len(hs)) - 1)]
        hi = hs[min(len(hs) - 1, int(0.95 * len(hs)))]
        a["tost_equivalence_pass"] = -TOST_MARGIN_H < lo and hi < TOST_MARGIN_H
    else:
        a["tost_equivalence_pass"] = False

    # seed robustness (C-4: >=4/5 seeds same-direction verifier lift; not a test)
    v_seeds = cells.by_seed.get((ARM_VERIFY, "R1", k12, 0.0), {})
    a_seeds = cells.by_seed.get((ARM_ALONE, "R1", 0, 0.0), {})
    common = sorted(set(v_seeds) & set(a_seeds))
    if common:
        pos = sum(1 for s in common
                  if acc_of(v_seeds[s]) > acc_of(a_seeds[s]))
        a["seed_sign_consistent"] = pos >= math.ceil(0.8 * len(common))
    else:
        a["seed_sign_consistent"] = len(common) == 0 and bool(v_seeds) is False
    return out


def _mk(arm, rung, correct_n, n=200, k=0, b=0.0, seed=0, flops=1e11, ext_correct=None):
    m = {"item_correct": [1] * correct_n + [0] * (n - correct_n),
         "metric_vector": {"inference_compute": {"flops_per_query": flops}}}
    if ext_correct is not None:
        m["item_correct_external"] = [1] * ext_correct + [0] * (100 - ext_correct)
    return {"config": {"arm": arm, "rung": rung, "retry_budget": k,
                       "escalation_budget": b, "seed": seed}, "metrics": m}


def selftest():
    recs = [
        _mk(ARM_ALONE, "R1", 100, ext_correct=50), _mk(ARM_ALONE, "R2", 180, flops=4e11),
        _mk(ARM_ALONE, "R3", 190),
        _mk(ARM_VERIFY, "R1", 160, k=1, flops=2e11, ext_correct=80),
        _mk(ARM_VERIFY, "R1", 150, k=2, flops=2.5e11),
        _mk(ARM_VERIFY, "R1", 150, k=4, flops=3e11),
        _mk(ARM_VERIFY, "R2", 186, k=1, flops=6e11),
        _mk(ARM_TEXT, "R1", 110, flops=1.2e11), _mk(ARM_SC, "R1", 110, flops=2e11),
        _mk(ARM_SELFV, "R1", 120, k=1, flops=2e11),
        _mk(ARM_PRM, "R1", 140, flops=2e11),
        _mk(ARM_CV, "R1", 170, b=0.25), _mk(ARM_CL, "R1", 160, b=0.25),
        _mk(ARM_CT, "R1", 160, b=0.25),
        {"config": {"arm": ARM_IFACE, "rung": "R1", "retry_budget": 0,
                    "escalation_budget": 0, "seed": 0},
         "metrics": {"n_labelled": 300, "n_extraction_failures": 15}},
        {"config": {"arm": ARM_IFACE, "rung": "R2", "retry_budget": 0,
                    "escalation_budget": 0, "seed": 0},
         "metrics": {"n_labelled": 300, "n_extraction_failures": 15}},
    ]
    out = analyze(recs, B=800)
    a = out["analysis"]
    assert abs(a["gap_closed_fraction_R1R2"] - 0.75) < 1e-12, a   # HAND-COMPUTED
    assert abs(a["gap_closed_fraction_R2R3"] - 0.60) < 1e-9, a    # HAND-COMPUTED
    assert a["best_retry_budget"] == 1 and a["gap_below_half"] is False
    assert abs(a["cost_ratio_vs_S"] - 0.5) < 1e-12                # 2e11/4e11
    assert out["gates"]["instrument_valid"] is True               # 15/300 lb=0.0326<=0.1
    assert a["competitor_closes_asmuch"] is False
    assert a["primary_reject"] is True and a["primary_p"] < 0.05
    assert a["beats_text_null"] is True and a["beats_gloss_self_verify"] is True
    assert a["holm"]["prm_beaten"] is True and a["holm"]["cascade_dominance"] is True
    assert a["tost_equivalence_pass"] is False
    # degenerate no-lift case: verifier == alone -> no rejection, gap 0
    flat = [r for r in recs if r["config"]["arm"] in (ARM_ALONE, ARM_IFACE)]
    flat += [_mk(ARM_VERIFY, "R1", 100, k=1, flops=2e11)]
    out2 = analyze(flat, B=400)
    assert out2["analysis"]["gap_closed_fraction_R1R2"] == 0.0
    assert out2["analysis"]["primary_reject"] is False
    assert out2["analysis"]["gap_below_half"] is True
    print("f2 selftest OK")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        records = [json.loads(l) for l in sys.stdin if l.strip()]
        print(json.dumps(analyze(records, B=B_PRODUCTION), sort_keys=True))
