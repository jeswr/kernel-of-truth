#!/usr/bin/env python3
"""consensus.py -- MECHANICAL strong-consensus over the 6-model glosses.

For each concept:
  * load the available model glosses (gen/<slug>.<short>.json 'gloss');
  * embed each with the repo's pinned nomic-embed-text-v1.5 (kb_common.Embedder,
    dim_committed=256, doc prefix, L2-normed) -> pairwise cosine among the glosses;
  * STRONG CONSENSUS = the largest clique of >=4 glosses that are pairwise
    cosine >= tau (all-pairs, i.e. mutually similar, not merely connected);
    tie-break by highest mean intra-clique similarity;
  * consensus definition = the clique MEDOID (highest mean cosine to the other
    clique members).

Outputs consensus.json (per-concept clusters + medoid + membership + matrices)
and prints the global within-concept cosine distribution used to justify tau,
plus a sensitivity table at tau +/- 0.05.

$0, no git. Re-runnable on a partial gen/ set.
"""
import argparse
import itertools
import json
import os
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
GEN = HERE / "gen"
sys.path.insert(0, str(ROOT / "tools" / "kb"))

MODEL_SHORT = {"claude-opus-4-8": "opus48", "claude-fable-5": "fable5",
               "claude-haiku-4-5": "haiku45",
               "gpt-5.6-sol": "gpt56sol", "gpt-5.6-luna": "gpt56luna",
               "gpt-5.6-terra": "gpt56terra"}
MODELS = list(MODEL_SHORT.keys())


def slug_of(label):
    s = label.lower().replace("'", "").replace("’", "")
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def load_glosses(row):
    """-> dict model -> gloss (only models with a written record)."""
    slug = slug_of(row["concept"])
    out = {}
    for m in MODELS:
        p = GEN / f"{slug}.{MODEL_SHORT[m]}.json"
        if p.exists():
            try:
                rec = json.load(open(p))
                g = rec.get("gloss")
                if isinstance(g, str) and g.strip():
                    out[m] = g.strip()
            except Exception:
                pass
    return out


def max_clique(models, C, tau, min_size=4):
    """Largest subset (>=min_size) of `models` pairwise cosine >= tau in matrix C
    (C indexed by model name). Tie-break: highest mean intra-subset cosine."""
    best = None
    best_mean = -1
    n = len(models)
    for k in range(n, min_size - 1, -1):
        found_at_k = False
        for combo in itertools.combinations(models, k):
            ok = True
            tot = cnt = 0.0
            for a, b in itertools.combinations(combo, 2):
                c = C[a][b]
                if c < tau:
                    ok = False
                    break
                tot += c
                cnt += 1
            if ok:
                mean = tot / cnt if cnt else 1.0
                if mean > best_mean:
                    best, best_mean = combo, mean
                found_at_k = True
        if found_at_k:
            break  # take the largest k that has any clique
    return list(best) if best else None


def medoid(cluster, C):
    """member with highest mean cosine to the OTHER cluster members."""
    best, best_m = None, -1
    for a in cluster:
        others = [b for b in cluster if b != a]
        m = sum(C[a][b] for b in others) / len(others) if others else 1.0
        if m > best_m:
            best, best_m = a, m
    return best, best_m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tau", type=float, default=0.86)
    ap.add_argument("--dim", type=int, default=256)
    ap.add_argument("--out", default=str(HERE / "consensus.json"))
    args = ap.parse_args()

    import numpy as np
    import kb_common as K
    emb = K.Embedder()

    data = json.load(open(HERE / "concepts-100.json"))
    rows = data["concepts"]

    per_concept = []
    all_pairwise = []  # global within-concept cosines (for tau justification)
    for row in rows:
        gl = load_glosses(row)
        if len(gl) < 2:
            per_concept.append({"concept": row["concept"], "urn": row["urn"],
                                "n_glosses": len(gl), "models": list(gl.keys()),
                                "note": "insufficient glosses"})
            continue
        models = list(gl.keys())
        V = emb.embed([gl[m] for m in models], is_query=False, dim=args.dim)
        M = V @ V.T
        C = {a: {b: float(M[i][j]) for j, b in enumerate(models)}
             for i, a in enumerate(models)}
        for i, j in itertools.combinations(range(len(models)), 2):
            all_pairwise.append(float(M[i][j]))
        per_concept.append({
            "concept": row["concept"], "urn": row["urn"], "stratum": row["stratum"],
            "n_glosses": len(models), "models": models,
            "cosine": C, "glosses": gl,
        })

    def clusters_at(tau):
        res = {}
        n_consensus = 0
        for pc in per_concept:
            if "cosine" not in pc:
                res[pc["concept"]] = None
                continue
            cl = max_clique(pc["models"], pc["cosine"], tau, min_size=4)
            if cl:
                med, medm = medoid(cl, pc["cosine"])
                res[pc["concept"]] = {"cluster": cl, "medoid": med,
                                      "medoid_mean_sim": round(medm, 4)}
                n_consensus += 1
            else:
                res[pc["concept"]] = {"cluster": None}
        return res, n_consensus

    # sensitivity sweep
    sens = {}
    for tau in [round(args.tau - 0.05, 3), args.tau, round(args.tau + 0.05, 3)]:
        _, nc = clusters_at(tau)
        sens[tau] = nc

    primary, n_consensus = clusters_at(args.tau)

    # attach primary clusters to per_concept
    for pc in per_concept:
        c = primary.get(pc["concept"])
        if c and c.get("cluster"):
            pc["consensus_cluster"] = c["cluster"]
            pc["consensus_medoid_model"] = c["medoid"]
            pc["consensus_gloss"] = pc["glosses"][c["medoid"]]
            pc["in_consensus"] = {m: (m in c["cluster"]) for m in pc["models"]}
        else:
            pc["consensus_cluster"] = None

    arr = np.array(all_pairwise) if all_pairwise else np.array([0.0])
    dist = {
        "n_pairs": int(arr.size),
        "min": round(float(arr.min()), 4), "p10": round(float(np.percentile(arr, 10)), 4),
        "p25": round(float(np.percentile(arr, 25)), 4),
        "median": round(float(np.median(arr)), 4),
        "mean": round(float(arr.mean()), 4),
        "p75": round(float(np.percentile(arr, 75)), 4),
        "p90": round(float(np.percentile(arr, 90)), 4),
        "max": round(float(arr.max()), 4),
    }

    out = {
        "built": "consensus-100 mechanical strong-consensus (nomic v1.5, dim %d)" % args.dim,
        "tau": args.tau, "min_cluster": 4, "dim": args.dim,
        "n_concepts_with_glosses": sum(1 for pc in per_concept if "cosine" in pc),
        "n_with_strong_consensus": n_consensus,
        "within_concept_cosine_distribution": dist,
        "sensitivity_n_consensus_by_tau": sens,
        "per_concept": per_concept,
    }
    json.dump(out, open(args.out, "w"), indent=2, ensure_ascii=False)
    print("concepts with >=2 glosses:", out["n_concepts_with_glosses"])
    print("strong consensus (>=4 clique) at tau=%.2f:" % args.tau, n_consensus)
    print("within-concept cosine distribution:", json.dumps(dist))
    print("sensitivity (n_consensus by tau):", sens)
    print("wrote", args.out)


if __name__ == "__main__":
    main()
