#!/usr/bin/env python3
"""stage3_analyze.py — turn the Stage-3 paired ablation deltas into, per shortlisted
expert: causal harm summaries (on/off domain x contribution/route-around/module-swap),
an evidence-agreement causal confidence, a SAFE-TO-DROP / LOAD-BEARING /
DETERMINISTIC-REPLACEABLE classification, and a candidate skip-list.

Pure function of stage3_deltas.json + stage3_shortlist.json (re-runnable locally on
the downloaded raw).  All decision THRESHOLDS are STIPULATED (exploratory infra,
not a frozen experiment) and reported verbatim so the classification is auditable.
Primary causal endpoint = target-NLL increase (nats/token); correctness + margin +
top-K KL are secondary.  Route-around is the primary DROP proxy (it is what dropping
the expert actually does); contribution-ablation is the upper-bound (no renormalise).
"""
import argparse, json, math
from collections import defaultdict
from statistics import mean

try:
    import numpy as np
except Exception:
    np = None

# ---- STIPULATED thresholds (nats/token unless noted); exploratory, documented ----
TH = {
    "LOW":  0.05,     # negligible target-NLL increase
    "MID":  0.15,     # a real but modest effect
    "HIGH": 0.40,     # a large effect -> load-bearing
    "CORR_SIG": -0.05,  # mean exact-correctness drop that counts as real (5%)
    "SWAP_RECOVER_FRAC": 0.40,  # module-swap "holds" if it leaves <=40% of the route harm
    "CONF_HI": 0.66, "CONF_MED": 0.40,  # causal-confidence buckets
    "SKIP_MIN_CONF": 0.50,   # a cell joins the skip-list only at >= this causal confidence
}


def parse_cond(cond):
    # "contrib:main|56|45:on" -> ("contrib","main|56|45","on")
    kind, cell, arm = cond.split(":")
    return kind, cell, arm


def per_item_means(rows, field):
    """average `field` within each corpus_item, return the list of per-item means."""
    byit = defaultdict(list)
    for r in rows: byit[r["corpus_item"]].append(r[field])
    return [mean(v) for v in byit.values()]


def boot_ci(vals, n=2000, lo=5, hi=95, seed=0):
    if not vals: return (float("nan"), float("nan"))
    if np is None or len(vals) < 3:
        m = mean(vals); return (m, m)
    rng = np.random.default_rng(seed); a = np.asarray(vals, float)
    bs = a[rng.integers(0, len(a), size=(n, len(a)))].mean(axis=1)
    return (float(np.percentile(bs, lo)), float(np.percentile(bs, hi)))


def summarize(rows):
    """rows for one (cell, kind, arm) -> harm summary."""
    if not rows:
        return None
    it_nll = per_item_means(rows, "dNLL")
    it_mgn = per_item_means(rows, "dMargin")
    it_kl  = per_item_means(rows, "KL")
    it_corr= per_item_means(rows, "dCorr")
    lo, hi = boot_ci(it_nll)
    same = sum(1 for v in it_nll if (v > 0) == (mean(it_nll) > 0)) / max(1, len(it_nll))
    return {
        "n_items": len(it_nll), "n_pos": len(rows),
        "dNLL_mean": round(mean(it_nll), 4), "dNLL_ci": [round(lo, 4), round(hi, 4)],
        "dMargin_mean": round(mean(it_mgn), 4),
        "KL_mean": round(mean(it_kl), 4),
        "dCorr_mean": round(mean(it_corr), 4),
        "sign_stability": round(same, 3),
    }


def clip01(x): return max(0.0, min(1.0, x))


def classify(cell_meta, S):
    """S = {(kind,arm): summary}. Returns (label, causal_confidence, evidence)."""
    def g(k, a, f, d=0.0):
        s = S.get((k, a)); return s[f] if s else d
    route_on  = g("route", "on", "dNLL_mean")
    route_off = g("route", "off", "dNLL_mean")
    contrib_on= g("contrib", "on", "dNLL_mean")
    corr_on   = g("contrib", "on", "dCorr_mean")   # correctness measured on contribution arm (routing kept)
    swap_on   = g("swap", "on", "dNLL_mean", None) if ("swap", "on") in S else None
    n_on = g("route", "on", "n_items")

    # ---- classification (STIPULATED gates) ----
    big_corr_loss = corr_on <= TH["CORR_SIG"]
    if (route_on < TH["LOW"] and route_off < TH["LOW"] and not big_corr_loss):
        label = "SAFE-TO-DROP"
    elif (route_on >= TH["HIGH"] or big_corr_loss or route_off >= TH["MID"]):
        label = "LOAD-BEARING"
    elif (swap_on is not None and route_on >= TH["MID"] and route_off < TH["LOW"]
          and (swap_on <= TH["LOW"] or swap_on <= TH["SWAP_RECOVER_FRAC"] * max(route_on, 1e-6))):
        label = "DETERMINISTIC-REPLACEABLE"
    else:
        label = "CHARACTERISE-MORE"

    # ---- causal confidence = evidence agreement across the causal channels ----
    coverage = clip01(n_on / 10.0)
    stability = clip01((g("route", "on", "sign_stability") - 0.5) / 0.5)
    cr_agree = 1.0 if (contrib_on > 0) == (route_on > 0) else 0.0     # contrib & route agree in sign
    denom = abs(route_on) + TH["LOW"]
    contrast = clip01(abs(route_on - route_off) / denom)             # on-vs-off separation clarity
    causal_conf = round(0.25 * coverage + 0.25 * stability + 0.25 * cr_agree + 0.25 * contrast, 3)

    evidence = {
        "route_on_dNLL": round(route_on, 4), "route_off_dNLL": round(route_off, 4),
        "contrib_on_dNLL": round(contrib_on, 4), "contrib_on_dCorr": round(corr_on, 4),
        "swap_on_dNLL": (round(swap_on, 4) if swap_on is not None else None),
        "coverage": round(coverage, 3), "sign_stability": round(g("route","on","sign_stability"), 3),
        "contrib_route_sign_agree": cr_agree, "on_off_contrast": round(contrast, 3),
    }
    return label, causal_conf, evidence


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--deltas", required=True)
    ap.add_argument("--shortlist", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    rows = json.loads(open(a.deltas).read())
    shortlist = json.loads(open(a.shortlist).read())
    meta_by_cell = {c["cell"]: c for c in shortlist["experts"]}

    # bucket rows by (cell, kind, arm)
    buckets = defaultdict(list)
    for r in rows:
        if not r.get("cond") or ":" not in r["cond"]: continue
        kind, cell, arm = parse_cond(r["cond"])
        buckets[(cell, kind, arm)].append(r)

    experts, skiplist, counts = [], [], defaultdict(int)
    for cell, cm in meta_by_cell.items():
        S = {}
        for kind in ("contrib", "route", "swap"):
            for arm in ("on", "off"):
                s = summarize(buckets.get((cell, kind, arm), []))
                if s: S[(kind, arm)] = s
        has_data = ("route", "on") in S
        if not has_data:
            label, conf, ev = "NO-DATA", 0.0, {}
        else:
            label, conf, ev = classify(cm, S)
        bucket = ("high" if conf >= TH["CONF_HI"] else "med" if conf >= TH["CONF_MED"] else "low")
        rec = {
            "cell": cell, "stratum": cm["stratum"], "candidate_kind": cm["candidate_kind"],
            "primary_domain": cm["primary_domain"], "events_total": cm["events_total"],
            "routing_confidence": cm.get("routing_confidence"),
            "label": label, "causal_confidence": conf, "confidence_bucket": bucket,
            "evidence": ev,
            "summaries": {f"{k}_{a}": v for (k, a), v in S.items()},
        }
        experts.append(rec); counts[label] += 1
        if label in ("SAFE-TO-DROP", "DETERMINISTIC-REPLACEABLE") and conf >= TH["SKIP_MIN_CONF"]:
            skiplist.append({"cell": cell, "action": ("DROP" if label == "SAFE-TO-DROP" else "SUBSTITUTE"),
                             "swap_to": cm.get("swap_to"), "causal_confidence": conf,
                             "route_on_dNLL": ev.get("route_on_dNLL"),
                             "route_off_dNLL": ev.get("route_off_dNLL"),
                             "stratum": cm["stratum"]})

    out = {
        "_about": "GLM-5.2 Stage-3 causal characterisation — per-expert classification + skip-list",
        "thresholds_stipulated": TH,
        "n_experts": len(experts),
        "label_counts": dict(counts),
        "confidence_buckets": {b: sum(1 for e in experts if e["confidence_bucket"] == b)
                               for b in ("high", "med", "low")},
        "skiplist": sorted(skiplist, key=lambda x: -x["causal_confidence"]),
        "skiplist_size": len(skiplist),
        "experts": sorted(experts, key=lambda e: (e["label"], -e["causal_confidence"])),
    }
    Path_out = a.out
    open(Path_out, "w").write(json.dumps(out, indent=1))
    # compact stdout for the driver
    print(json.dumps({"label_counts": out["label_counts"],
                      "confidence_buckets": out["confidence_buckets"],
                      "skiplist_size": out["skiplist_size"],
                      "n_experts": out["n_experts"]}, indent=1))


if __name__ == "__main__":
    main()
