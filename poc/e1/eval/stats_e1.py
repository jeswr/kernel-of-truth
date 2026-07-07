#!/usr/bin/env python3
"""E1 pre-registered statistics + verdict (docs/poc-design.md E1;
bead kernel-of-truth-bk0). No third-party stats deps: exact paired sign-flip
permutation tests and a self-contained Student-t CDF (incomplete beta by
continued fraction) for TOST.

PRE-REGISTERED CRITERIA (quoted verbatim in the emitted verdict):

  PRIMARY  "kernel-frozen > shuffled-kernel-frozen, paired permutation across
           5 paired seeds, p<0.05, single look: kernel at the 50%-token
           checkpoint vs shuffled at the 100%-token endpoint" (E1, MAJOR 12).
           Direction is one-sided by construction (">"): with 5 paired seeds
           the exact sign-flip permutation test has minimum attainable
           one-sided p = 1/32 = 0.03125.
  KILL     (MAJOR 11) "'null' requires the pre-registered
           smallest-effect-size-of-interest (Cohen's d = 0.5 on the primary
           endpoint) excluded by an equivalence bound (TOST), not mere
           non-significance."
  GUARD    (MAJOR 5) "every metric also evaluated on the untrained step-0
           kernel-frozen model; trained success requires beating the step-0
           baseline".
  PPL RULE (MAJOR 13) "if concept-token PPL saturates within 2% across all
           arms it is declared uninformative, pre-registered".
  SECONDARY "Kernel > random-frozen is secondary (Holm-corrected), demoted
           per BLOCKER 2." All secondary endpoints Holm-corrected
           (Common rule 1).

Inputs: the eval-*.json files emitted by eval_e1.py (arms x seeds x
{step0,50pct,100pct}). Emits verdict JSON + markdown.
"""

import argparse
import glob
import itertools
import json
import math
import os

PRIMARY_QUOTE = ("kernel-frozen > shuffled-kernel-frozen, paired permutation across 5 paired "
                 "seeds, p<0.05, single look: kernel at the 50%-token checkpoint vs shuffled "
                 "at the 100%-token endpoint")
KILL_QUOTE = ("\"null\" requires the pre-registered smallest-effect-size-of-interest "
              "(Cohen's d = 0.5 on the primary endpoint) excluded by an equivalence bound "
              "(TOST), not mere non-significance")
GUARD_QUOTE = ("every metric also evaluated on the untrained step-0 kernel-frozen model; "
               "trained success requires beating the step-0 baseline")
PPL_QUOTE = ("if concept-token PPL saturates within 2% across all arms it is declared "
             "uninformative, pre-registered")
SECONDARY_QUOTE = "Kernel > random-frozen is secondary (Holm-corrected), demoted per BLOCKER 2"


# ---------------------------------------------------------------------------
# Self-contained Student-t distribution (upper tail) via incomplete beta
# ---------------------------------------------------------------------------

def _betacf(a, b, x):
    MAXIT, EPS, FPMIN = 200, 3e-12, 1e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    if abs(d) < FPMIN:
        d = FPMIN
    d = 1.0 / d
    h = d
    for m in range(1, MAXIT + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < FPMIN:
            d = FPMIN
        c = 1.0 + aa / c
        if abs(c) < FPMIN:
            c = FPMIN
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < FPMIN:
            d = FPMIN
        c = 1.0 + aa / c
        if abs(c) < FPMIN:
            c = FPMIN
        d = 1.0 / d
        de = d * c
        h *= de
        if abs(de - 1.0) < EPS:
            break
    return h


def _betai(a, b, x):
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    ln = (math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
          + a * math.log(x) + b * math.log(1.0 - x))
    bt = math.exp(ln)
    if x < (a + 1.0) / (a + b + 2.0):
        return bt * _betacf(a, b, x) / a
    return 1.0 - bt * _betacf(b, a, 1.0 - x) / b


def t_sf(t, df):
    """P(T_df >= t) (upper tail)."""
    p = _betai(df / 2.0, 0.5, df / (df + t * t)) / 2.0
    return p if t >= 0 else 1.0 - p


# ---------------------------------------------------------------------------
# Paired tests
# ---------------------------------------------------------------------------

def paired_permutation_one_sided(diffs):
    """Exact sign-flip test of H0: mean diff <= 0 vs H1: > 0."""
    n = len(diffs)
    obs = sum(diffs) / n
    count = 0
    total = 2 ** n
    for signs in itertools.product((1, -1), repeat=n):
        m = sum(s * d for s, d in zip(signs, diffs)) / n
        if m >= obs - 1e-15:
            count += 1
    return {"meanDiff": obs, "p": count / total, "n": n,
            "minAttainableP": 1 / total, "test": "exact one-sided sign-flip permutation"}


def tost_equivalence(diffs, sesoi_d):
    """Paired TOST with bounds +/- sesoi_d * sd(diff) (Cohen's d units)."""
    n = len(diffs)
    mean = sum(diffs) / n
    if n < 2:
        return {"error": "n<2"}
    var = sum((d - mean) ** 2 for d in diffs) / (n - 1)
    sd = math.sqrt(var)
    if sd == 0:
        return {"meanDiff": mean, "sd": 0.0,
                "note": "zero variance; TOST degenerate",
                "equivalent": abs(mean) == 0.0}
    bound = sesoi_d * sd
    se = sd / math.sqrt(n)
    t_lower = (mean + bound) / se   # H0: mean <= -bound
    t_upper = (mean - bound) / se   # H0: mean >= +bound
    p_lower = t_sf(t_lower, n - 1)          # P(T >= t_lower)
    p_upper = 1.0 - t_sf(t_upper, n - 1)    # P(T <= t_upper)
    return {"meanDiff": mean, "sd": sd, "cohensD": mean / sd, "sesoiD": sesoi_d,
            "rawBound": bound, "pLower": p_lower, "pUpper": p_upper,
            "equivalent": p_lower < 0.05 and p_upper < 0.05,
            "test": "paired TOST, bounds +/- sesoi_d*sd, alpha=0.05 per side"}


def holm(named_ps):
    """Holm-Bonferroni: list of (name, p) -> dict name -> (pAdj, reject@0.05)."""
    m = len(named_ps)
    out = {}
    prev = 0.0
    for rank, (name, p) in enumerate(sorted(named_ps, key=lambda x: x[1])):
        adj = min(1.0, max(prev, (m - rank) * p))
        prev = adj
        out[name] = {"p": p, "pAdj": adj, "reject": adj < 0.05}
    return out


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def load_evals(evals_dir):
    db = {}
    for path in sorted(glob.glob(os.path.join(evals_dir, "eval-*.json"))):
        with open(path) as f:
            e = json.load(f)
        db[(e["arm"], e["seed"], e["tag"])] = e
    return db


def series(db, arm, tag, metric_path, seeds):
    out = []
    for s in seeds:
        e = db.get((arm, s, tag))
        if e is None:
            raise SystemExit(f"ERR_MISSING_EVAL: ({arm}, seed {s}, {tag})")
        v = e
        for k in metric_path:
            v = v[k]
        if v is None:
            raise SystemExit(f"ERR_NULL_METRIC: {metric_path} for ({arm}, {s}, {tag})")
        out.append(v)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--evals", required=True, help="dir containing eval-*.json")
    ap.add_argument("--out-prefix", required=True)
    ap.add_argument("--seeds", default="0,1,2,3,4")
    ap.add_argument("--sesoi-d", type=float, default=0.5)
    ap.add_argument("--mock", action="store_true",
                    help="label the verdict as a MOCK pipeline check, not a result")
    args = ap.parse_args()
    seeds = [int(s) for s in args.seeds.split(",")]
    db = load_evals(args.evals)
    arms = sorted({k[0] for k in db})
    P = ["cloze", "heldOutAccAttested"]

    # ---- Amendment A1 evaluated-set declaration (must be uniform) ----------
    decls = {json.dumps(e.get("evaluatedConceptSet"), sort_keys=True) for e in db.values()}
    if len(decls) != 1 or decls == {"null"}:
        raise SystemExit("ERR_POLICY: evals carry missing/inconsistent evaluatedConceptSet "
                         "declarations — rebuild data + evals with the Amendment-A1 pipeline")
    evaluated_set = next(iter(db.values()))["evaluatedConceptSet"]
    policy = next(iter(db.values())).get("policy")

    # ---- primary: kernel@50% vs shuffled@100% (single look, MAJOR 12) ------
    kernel50 = series(db, "kernel-frozen", "50pct", P, seeds)
    shuffled100 = series(db, "shuffled-frozen", "100pct", P, seeds)
    diffs = [a - b for a, b in zip(kernel50, shuffled100)]
    primary = paired_permutation_one_sided(diffs)
    primary_pass = primary["p"] < 0.05

    # ---- kill direction: TOST on the same contrast (MAJOR 11) --------------
    tost = tost_equivalence(diffs, args.sesoi_d)

    # ---- circularity guard (MAJOR 5) ---------------------------------------
    step0 = series(db, "kernel-frozen", "step0", P, seeds)
    kernel100 = series(db, "kernel-frozen", "100pct", P, seeds)
    guard = {
        "step0Mean": sum(step0) / len(step0),
        "kernel50Mean": sum(kernel50) / len(kernel50),
        "kernel100Mean": sum(kernel100) / len(kernel100),
        "beatsStep0At50pct": all(a > b for a, b in zip(kernel50, step0)),
        "beatsStep0At100pct": all(a > b for a, b in zip(kernel100, step0)),
        "probeStep0": series(db, "kernel-frozen", "step0", ["probe", "testAcc"], seeds),
        "probe100": series(db, "kernel-frozen", "100pct", ["probe", "testAcc"], seeds),
    }

    # ---- PPL saturation rule (MAJOR 13) -------------------------------------
    slice_ppl = {}
    for arm in arms:
        vals = series(db, arm, "100pct", ["ppl", "conceptSlicePpl"], seeds)
        slice_ppl[arm] = sum(vals) / len(vals)
    lo, hi = min(slice_ppl.values()), max(slice_ppl.values())
    spread = (hi - lo) / lo
    saturated = spread < 0.02

    # ---- secondaries (Holm; Common rule 1) ----------------------------------
    def contrast(arm_a, tag_a, arm_b, tag_b, metric=P):
        a = series(db, arm_a, tag_a, metric, seeds)
        b = series(db, arm_b, tag_b, metric, seeds)
        return paired_permutation_one_sided([x - y for x, y in zip(a, b)])

    sec_raw = {
        "kernel100_vs_shuffled100_cloze": contrast("kernel-frozen", "100pct", "shuffled-frozen", "100pct"),
        "kernel100_vs_random100_cloze": contrast("kernel-frozen", "100pct", "random-frozen", "100pct"),
        "kernel100_vs_trainable100_cloze": contrast("kernel-frozen", "100pct", "trainable", "100pct"),
        "kernel100_vs_kernelInit100_cloze": contrast("kernel-frozen", "100pct", "kernel-init", "100pct"),
        "kernel100_vs_shuffled100_probe": contrast("kernel-frozen", "100pct", "shuffled-frozen",
                                                   "100pct", ["probe", "testAcc"]),
    }
    sec = holm([(k, v["p"]) for k, v in sec_raw.items()])
    for k in sec_raw:
        sec[k]["meanDiff"] = sec_raw[k]["meanDiff"]

    # ---- verdict -------------------------------------------------------------
    if saturated:
        verdict = "UNINFORMATIVE"
        reason = f"concept-token PPL spread across arms = {spread*100:.2f}% < 2% ({PPL_QUOTE})"
    elif primary_pass and guard["beatsStep0At50pct"]:
        verdict = "PRIMARY PASS"
        reason = (f"primary p = {primary['p']:.4f} < 0.05 and kernel@50% beats the step-0 "
                  f"baseline on every seed")
    elif primary_pass:
        verdict = "PRIMARY SIGNIFICANT BUT FAILS CIRCULARITY GUARD"
        reason = f"primary p = {primary['p']:.4f} < 0.05 but step-0 guard failed ({GUARD_QUOTE})"
    elif tost.get("equivalent"):
        verdict = "NULL (EQUIVALENCE-BOUNDED)"
        reason = (f"primary p = {primary['p']:.4f} >= 0.05 AND TOST excludes |d| >= "
                  f"{args.sesoi_d} ({KILL_QUOTE})")
    else:
        verdict = "INCONCLUSIVE"
        reason = (f"primary p = {primary['p']:.4f} >= 0.05 but TOST does NOT exclude d = "
                  f"{args.sesoi_d} — neither a pass nor a pre-registered null ({KILL_QUOTE})")
    if args.mock:
        verdict = f"MOCK RUN — machinery check only, not a result. ({verdict})"

    out = {
        "experiment": "E1", "mock": args.mock, "seeds": seeds,
        "policy": policy,
        "evaluatedConceptSet": evaluated_set,
        "preRegisteredCriteria": {"primary": PRIMARY_QUOTE, "kill": KILL_QUOTE,
                                  "circularityGuard": GUARD_QUOTE, "pplRule": PPL_QUOTE,
                                  "secondary": SECONDARY_QUOTE},
        "primary": {"kernel50": kernel50, "shuffled100": shuffled100, "diffs": diffs,
                    **primary, "pass": primary_pass},
        "tost": tost,
        "circularityGuard": guard,
        "pplSaturation": {"conceptSlicePplByArm": slice_ppl, "spread": spread,
                          "saturated": saturated},
        "secondariesHolm": sec,
        "verdict": verdict, "verdictReason": reason,
    }
    with open(args.out_prefix + ".json", "w") as f:
        json.dump(out, f, indent=2)

    excl = ", ".join(evaluated_set["excludedByPolicy"])
    pol_sha = (policy or {}).get("sha256", evaluated_set.get("policySha256", "?"))
    md = [
        f"# E1 verdict{' (MOCK — pipeline check only)' if args.mock else ''}",
        "",
        f"**Evaluated concept set (Amendment A1): {evaluated_set['size']} of "
        f"{evaluated_set['vocabConceptTokens']} vocab concept tokens — excluded by policy "
        f"`{(policy or {}).get('preset', 'a1-hybrid')}` (sha `{pol_sha[:8]}…`): {excl}.**",
        "",
        "Pre-registered criteria (docs/poc-design.md, quoted verbatim):",
        f"- **Primary:** \"{PRIMARY_QUOTE}\"",
        f"- **Kill:** {KILL_QUOTE}",
        f"- **Circularity guard:** \"{GUARD_QUOTE}\"",
        f"- **PPL rule:** \"{PPL_QUOTE}\"",
        f"- **Secondary:** \"{SECONDARY_QUOTE}\"",
        "",
        f"## Verdict: {verdict}",
        "",
        reason,
        "",
        "| quantity | value |",
        "|---|---|",
        f"| kernel@50% held-out cloze (per seed) | {', '.join(f'{v:.4f}' for v in kernel50)} |",
        f"| shuffled@100% held-out cloze (per seed) | {', '.join(f'{v:.4f}' for v in shuffled100)} |",
        f"| paired mean diff | {primary['meanDiff']:.4f} |",
        f"| one-sided exact permutation p | {primary['p']:.4f} (min attainable {primary['minAttainableP']:.4f}) |",
        f"| TOST equivalent (d = {args.sesoi_d}) | {tost.get('equivalent')} (pLower {tost.get('pLower', float('nan')):.4f}, pUpper {tost.get('pUpper', float('nan')):.4f}) |" if "pLower" in tost else f"| TOST | {tost} |",
        f"| step-0 kernel cloze mean | {guard['step0Mean']:.4f} |",
        f"| beats step-0 (50% / 100%) | {guard['beatsStep0At50pct']} / {guard['beatsStep0At100pct']} |",
        f"| concept-slice PPL spread across arms | {spread*100:.2f}% (saturated: {saturated}) |",
        "",
        "## Secondaries (Holm-corrected, one-sided)",
        "",
        "| contrast | mean diff | p | p (Holm) | reject |",
        "|---|---|---|---|---|",
    ]
    for k, v in sec.items():
        md.append(f"| {k} | {v['meanDiff']:.4f} | {v['p']:.4f} | {v['pAdj']:.4f} | {v['reject']} |")
    md.append("")
    md.append(f"Concept-slice PPL by arm: {json.dumps({k: round(v, 4) for k, v in slice_ppl.items()})}")
    md.append("")
    with open(args.out_prefix + ".md", "w") as f:
        f.write("\n".join(md))
    print(f"verdict: {verdict}")
    print(f"wrote {args.out_prefix}.json / .md")


if __name__ == "__main__":
    main()
