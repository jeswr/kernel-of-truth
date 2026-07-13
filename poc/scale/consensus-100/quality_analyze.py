#!/usr/bin/env python3
"""quality_analyze.py -- analyse the dual-judge quality scores and emit
quality-ranking.json + quality-ranking.md.

Reads quality-raw-judgeA.jsonl (gpt-5.6-sol) and quality-raw-judgeB.jsonl
(claude-opus-4-8). Computes:
  * per-model mean quality (per judge and averaged across judges);
  * inter-judge agreement: Pearson r + quadratic-weighted kappa on the 0-3
    scale, over gloss instances both judges scored;
  * side-by-side quality ranking vs the embedding-agreement ranking;
  * cheapest model-subset whose mean quality >= the {sol,fable} reference
    (and >= reference-0.1), + the cost-vs-quality Pareto frontier;
  * bottom line: does the cheap-ensemble recommendation survive the quality view.
No git.
"""
import itertools
import json
import math
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
MODELS = ["claude-opus-4-8", "claude-fable-5", "claude-haiku-4-5",
          "gpt-5.6-sol", "gpt-5.6-luna", "gpt-5.6-terra"]
SHORT = {"claude-opus-4-8": "opus", "claude-fable-5": "fable",
         "claude-haiku-4-5": "haiku", "gpt-5.6-sol": "sol",
         "gpt-5.6-luna": "luna", "gpt-5.6-terra": "terra"}
EMBED_AGREE = {"gpt-5.6-luna": 0.94, "claude-haiku-4-5": 0.90,
               "gpt-5.6-terra": 0.88, "claude-fable-5": 0.88,
               "gpt-5.6-sol": 0.86, "claude-opus-4-8": 0.84}


def load(path):
    recs = {}
    if not path.exists():
        return recs
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except Exception:
            continue
        if r.get("scores_by_model"):
            recs[r["concept"]] = r  # last write wins
    return recs


def mean(xs):
    return sum(xs) / len(xs) if xs else None


def pearson(xs, ys):
    n = len(xs)
    if n < 2:
        return None
    mx, my = mean(xs), mean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    dy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if dx == 0 or dy == 0:
        return None
    return num / (dx * dy)


def quad_weighted_kappa(a, b, K=4):
    """0..3 scale => K=4 categories. Quadratic weights."""
    n = len(a)
    if n == 0:
        return None
    O = [[0] * K for _ in range(K)]
    for x, y in zip(a, b):
        O[x][y] += 1
    row = [sum(O[i]) for i in range(K)]
    col = [sum(O[i][j] for i in range(K)) for j in range(K)]
    W = [[((i - j) ** 2) / ((K - 1) ** 2) for j in range(K)] for i in range(K)]
    num = sum(W[i][j] * O[i][j] for i in range(K) for j in range(K))
    den = sum(W[i][j] * row[i] * col[j] / n for i in range(K) for j in range(K))
    if den == 0:
        return None
    return 1 - num / den


def main():
    A = load(HERE / "quality-raw-judgeA.jsonl")
    B = load(HERE / "quality-raw-judgeB.jsonl")
    scoring = json.load(open(HERE / "scoring.json"))
    cost = scoring["cost_table_usd_per_concept"]

    concepts = sorted(set(A) | set(B))
    both = sorted(set(A) & set(B))

    # per-model scores per judge
    perA = {m: [] for m in MODELS}
    perB = {m: [] for m in MODELS}
    for c, r in A.items():
        for m, s in r["scores_by_model"].items():
            perA[m].append(s)
    for c, r in B.items():
        for m, s in r["scores_by_model"].items():
            perB[m].append(s)

    per_model = {}
    for m in MODELS:
        mA, mB = mean(perA[m]), mean(perB[m])
        if mA is not None and mB is not None:
            overall = (mA + mB) / 2
        else:
            overall = mA if mA is not None else mB
        per_model[m] = {
            "mean_A_sol": round(mA, 4) if mA is not None else None,
            "mean_B_opus": round(mB, 4) if mB is not None else None,
            "mean_overall": round(overall, 4) if overall is not None else None,
            "n_A": len(perA[m]), "n_B": len(perB[m]),
            "cost_usd_per_concept": cost.get(m),
            "embed_agreement": EMBED_AGREE.get(m),
        }

    # inter-judge agreement over gloss instances both judges scored
    paired_a, paired_b = [], []
    for c in both:
        sa, sb = A[c]["scores_by_model"], B[c]["scores_by_model"]
        for m in MODELS:
            if m in sa and m in sb:
                paired_a.append(sa[m])
                paired_b.append(sb[m])
    r = pearson(paired_a, paired_b)
    qwk = quad_weighted_kappa(paired_a, paired_b)
    exact = sum(1 for x, y in zip(paired_a, paired_b) if x == y) / len(paired_a) if paired_a else None
    within1 = sum(1 for x, y in zip(paired_a, paired_b) if abs(x - y) <= 1) / len(paired_a) if paired_a else None
    inter_judge = {
        "n_paired_glosses": len(paired_a),
        "pearson_r": round(r, 4) if r is not None else None,
        "quadratic_weighted_kappa": round(qwk, 4) if qwk is not None else None,
        "exact_agreement": round(exact, 4) if exact is not None else None,
        "within_1_agreement": round(within1, 4) if within1 is not None else None,
        "mean_A_sol_overall": round(mean(paired_a), 4) if paired_a else None,
        "mean_B_opus_overall": round(mean(paired_b), 4) if paired_b else None,
    }

    # rankings
    q_rank = sorted([m for m in MODELS if per_model[m]["mean_overall"] is not None],
                    key=lambda m: per_model[m]["mean_overall"], reverse=True)
    a_rank = sorted(EMBED_AGREE, key=lambda m: EMBED_AGREE[m], reverse=True)

    # reference = mean quality of {sol, fable}
    ref_models = ["gpt-5.6-sol", "claude-fable-5"]
    ref_q = mean([per_model[m]["mean_overall"] for m in ref_models
                  if per_model[m]["mean_overall"] is not None])

    # subset frontier: set_quality = mean of member per-model qualities;
    # set_cost = sum of member costs.
    subsets = []
    qual = {m: per_model[m]["mean_overall"] for m in MODELS}
    for k in range(1, len(MODELS) + 1):
        for combo in itertools.combinations(MODELS, k):
            qs = [qual[m] for m in combo if qual[m] is not None]
            if not qs:
                continue
            sq = mean(qs)
            sc = sum(cost[m] for m in combo)
            subsets.append({
                "models": list(combo),
                "short": [SHORT[m] for m in combo],
                "size": k,
                "mean_quality": round(sq, 4),
                "cost_usd_per_concept": round(sc, 5),
                "meets_ref": sq >= ref_q if ref_q is not None else None,
                "meets_ref_tol": sq >= (ref_q - 0.1) if ref_q is not None else None,
                "contains_ref_model": any(m in ref_models for m in combo),
            })

    cheapest_ge = min((s for s in subsets if s["meets_ref"]),
                      key=lambda s: s["cost_usd_per_concept"], default=None)
    cheapest_ge_tol = min((s for s in subsets if s["meets_ref_tol"]),
                          key=lambda s: s["cost_usd_per_concept"], default=None)

    # cost-vs-quality Pareto frontier (max quality achievable at <= each cost)
    by_cost = sorted(subsets, key=lambda s: (s["cost_usd_per_concept"], -s["mean_quality"]))
    pareto = []
    best_q = -1
    for s in by_cost:
        if s["mean_quality"] > best_q + 1e-9:
            pareto.append(s)
            best_q = s["mean_quality"]

    # reference sensitivity: how the cheapest matched set shifts with a stricter
    # reference (sol alone) vs the {sol,fable} average.
    def cheapest_for(refval, tol):
        elig = [s for s in subsets if s["mean_quality"] >= refval - tol]
        return min(elig, key=lambda s: s["cost_usd_per_concept"], default=None)
    q_sol = qual["gpt-5.6-sol"]
    q_fable = qual["claude-fable-5"]
    ref_sensitivity = []
    for name, rv in [("mean{sol,fable}", ref_q), ("sol_alone", q_sol),
                     ("max{sol,fable}", max(q_sol, q_fable))]:
        for tol in (0.0, 0.1):
            c = cheapest_for(rv, tol)
            ref_sensitivity.append({
                "reference": name, "reference_quality": round(rv, 4), "tolerance": tol,
                "cheapest_set": c["short"] if c else None,
                "cheapest_quality": c["mean_quality"] if c else None,
                "cheapest_cost_usd_per_concept": c["cost_usd_per_concept"] if c else None,
            })

    # the embedding-agreement recommendation was {gpt-5.6-terra} alone
    embed_rec = scoring.get("recommended_cheapest_ge95", {})
    embed_rec_models = embed_rec.get("models", ["gpt-5.6-terra"])
    embed_rec_q = mean([qual[m] for m in embed_rec_models if qual.get(m) is not None])

    out = {
        "built": "dual-judge blind definitional-quality ranking over consensus-100",
        "judges": {"A": "gpt-5.6-sol (codex, reasoning=high)",
                   "B": "claude-opus-4-8 (claude -p, MAX_THINKING_TOKENS=0)"},
        "n_concepts_scored": {"A": len(A), "B": len(B), "both": len(both)},
        "scale": "0-3 (0 wrong/circular/broken, 1 poor, 2 good, 3 first-rate)",
        "per_model": per_model,
        "quality_ranking": [{"model": m, "short": SHORT[m],
                             "mean_overall": per_model[m]["mean_overall"]}
                            for m in q_rank],
        "embedding_agreement_ranking": [{"model": m, "short": SHORT[m],
                                         "agreement": EMBED_AGREE[m]} for m in a_rank],
        "inter_judge_agreement": inter_judge,
        "reference": {"models": ref_models, "mean_quality": round(ref_q, 4) if ref_q else None,
                      "tolerance": 0.1},
        "cheapest_quality_matched_set": {
            "ge_reference": cheapest_ge,
            "ge_reference_minus_tol": cheapest_ge_tol,
        },
        "embedding_recommendation_under_quality": {
            "models": embed_rec_models,
            "mean_quality": round(embed_rec_q, 4) if embed_rec_q is not None else None,
            "reference": round(ref_q, 4) if ref_q else None,
            "meets_reference": (embed_rec_q >= ref_q) if (embed_rec_q is not None and ref_q) else None,
            "meets_reference_tol": (embed_rec_q >= ref_q - 0.1) if (embed_rec_q is not None and ref_q) else None,
        },
        "reference_sensitivity": ref_sensitivity,
        "cost_quality_pareto": pareto,
        "all_subsets": subsets,
    }
    json.dump(out, open(HERE / "quality-ranking.json", "w"), indent=2, ensure_ascii=False)
    print("wrote quality-ranking.json")
    print(json.dumps({
        "per_model_overall": {SHORT[m]: per_model[m]["mean_overall"] for m in MODELS},
        "quality_ranking": [SHORT[m] for m in q_rank],
        "inter_judge": inter_judge,
        "reference_q": round(ref_q, 4) if ref_q else None,
        "cheapest_ge": cheapest_ge["short"] if cheapest_ge else None,
        "cheapest_ge_cost": cheapest_ge["cost_usd_per_concept"] if cheapest_ge else None,
        "embed_rec_meets": out["embedding_recommendation_under_quality"],
    }, indent=2))
    return out


if __name__ == "__main__":
    main()
