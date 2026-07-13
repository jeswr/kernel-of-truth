#!/usr/bin/env python3
"""scoring.py -- per-model agreement rates + the cheapest-subset / cost-vs-fidelity
analysis (the deliverable).

Definitions:
  * PER-MODEL AGREEMENT RATE (vs the 6-model strong consensus): fraction of
    concepts (that have a strong-consensus cluster and a gloss from the model)
    where the model's gloss is IN the strong-consensus cluster. From consensus.json.

  * REFERENCE = the sol+fable pair (the "more intelligent" models). The reference
    answer for a concept exists iff sol & fable BOTH produced a gloss AND their
    glosses cluster together (cosine >= tau). Reference direction = the unit-mean
    of the sol & fable gloss vectors (their shared definition).

  * SUBSET CONSENSUS: for a model subset S, its agreed definition on a concept is
    its MEDOID gloss (the S-member gloss with highest mean cosine to the other
    S members; for |S|=1 it is that gloss). S REPRODUCES the reference on a
    concept iff cosine(medoid_vec(S), reference_dir) >= tau. Fidelity(S) =
    reproduced / (concepts with a valid sol+fable reference AND all S models present).

  * COST proxy (published $/token style). Claude models: MEASURED API-equivalent
    $/concept (define_concept.py's total_cost_usd, mean over the run). GPT models
    via codex report tokens not USD (subscription marginal = $0): we price them
    from measured mean tokens x a STATED published-tier assumption (sol dear,
    luna/terra cheap), consistent with the maintainer's ordering. All cost figures
    are printed; the cheap-subset conclusion is robust so long as luna/terra <<
    sol/fable/opus (stipulated).

Outputs scoring.json + prints the headline tables. $0, no git.
"""
import argparse
import itertools
import json
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
CLAUDE = {"claude-opus-4-8", "claude-fable-5", "claude-haiku-4-5"}
REF = ("gpt-5.6-sol", "claude-fable-5")

# --- cost proxy (published-price style). GPT tiers STATED (see docstring). ------
# per-1M-token USD list-price assumption used ONLY for the 3 codex models, chosen
# to honour the maintainer's ordering (sol dear ~ opus/fable tier; luna/terra
# cheap ~ haiku tier). Claude models use MEASURED API-equivalent $/concept.
GPT_PRICE_PER_MTOK = {          # (input, output) USD / 1e6 tokens  -- STATED PROXY
    "gpt-5.6-sol":   (2.50, 10.00),   # dear frontier tier
    "gpt-5.6-luna":  (0.15, 0.60),    # cheap small tier
    "gpt-5.6-terra": (0.15, 0.60),    # cheap small tier
}


def slug_of(label):
    s = label.lower().replace("'", "").replace("’", "")
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def cost_table():
    """-> {model: mean $/concept}, plus raw provenance."""
    import numpy as np
    claude_costs = {m: [] for m in CLAUDE}
    gpt_tokens = {m: {"in": [], "out": []} for m in GPT_PRICE_PER_MTOK}
    for m in MODELS:
        short = MODEL_SHORT[m]
        for rp in GEN.glob(f"*.{short}.report.json"):
            try:
                rep = json.load(open(rp))
            except Exception:
                continue
            atts = rep.get("attempts") or []
            if not atts:
                continue
            meta = atts[-1].get("meta") or {}
            if m in CLAUDE and meta.get("cost_usd") is not None:
                claude_costs[m].append(meta["cost_usd"])
            elif m in GPT_PRICE_PER_MTOK:
                u = meta.get("usage") or {}
                itok = u.get("input_tokens") or u.get("prompt_tokens")
                otok = u.get("output_tokens") or u.get("completion_tokens")
                if itok is not None and otok is not None:
                    gpt_tokens[m]["in"].append(itok)
                    gpt_tokens[m]["out"].append(otok)
    table, prov = {}, {}
    for m in CLAUDE:
        c = claude_costs[m]
        table[m] = round(float(np.mean(c)), 5) if c else None
        prov[m] = {"kind": "measured_api_equiv_usd", "n": len(c),
                   "mean_usd_per_concept": table[m]}
    for m in GPT_PRICE_PER_MTOK:
        pin, pout = GPT_PRICE_PER_MTOK[m]
        it = gpt_tokens[m]["in"]; ot = gpt_tokens[m]["out"]
        if it and ot:
            mi = float(np.mean(it)); mo = float(np.mean(ot))
            cost = mi / 1e6 * pin + mo / 1e6 * pout
            table[m] = round(cost, 5)
            prov[m] = {"kind": "measured_tokens_x_stated_price", "n": len(it),
                       "mean_in_tok": round(mi), "mean_out_tok": round(mo),
                       "price_per_mtok_in_out": [pin, pout],
                       "mean_usd_per_concept": table[m],
                       "note": "subscription marginal = $0; this is a published-price proxy"}
        else:
            table[m] = None
            prov[m] = {"kind": "no_token_usage_found"}
    return table, prov


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tau", type=float, default=0.86)
    ap.add_argument("--dim", type=int, default=256)
    ap.add_argument("--consensus", default=str(HERE / "consensus.json"))
    ap.add_argument("--out", default=str(HERE / "scoring.json"))
    args = ap.parse_args()

    import numpy as np
    import kb_common as K
    emb = K.Embedder()
    con = json.load(open(args.consensus))
    pcs = con["per_concept"]

    # ---- per-model agreement vs the 6-model strong consensus --------------
    have = {m: 0 for m in MODELS}
    inc = {m: 0 for m in MODELS}
    n_consensus = 0
    for pc in pcs:
        if not pc.get("consensus_cluster"):
            continue
        n_consensus += 1
        cluster = set(pc["consensus_cluster"])
        for m in pc["models"]:
            have[m] += 1
            if m in cluster:
                inc[m] += 1
    per_model = {m: {"in_consensus": inc[m], "of_concepts_with_consensus_and_gloss": have[m],
                     "agreement_rate": round(inc[m] / have[m], 4) if have[m] else None}
                 for m in MODELS}

    # ---- embed all glosses per concept; build reference + subset math -----
    vecs = {}  # concept -> {model: unit vec}
    for pc in pcs:
        if "glosses" not in pc:
            continue
        models = pc["models"]
        V = emb.embed([pc["glosses"][m] for m in models], is_query=False, dim=args.dim)
        vecs[pc["concept"]] = {m: V[i] for i, m in enumerate(models)}

    def cos(a, b):
        return float(a @ b)

    def medoid_vec(concept, S):
        vs = vecs[concept]
        present = [m for m in S if m in vs]
        if not present:
            return None
        if len(present) == 1:
            return vs[present[0]]
        best, bestm = None, -2
        for a in present:
            others = [b for b in present if b != a]
            mm = sum(cos(vs[a], vs[b]) for b in others) / len(others)
            if mm > bestm:
                best, bestm = a, mm
        return vs[best]

    # reference per concept
    references = {}   # concept -> reference unit dir
    ref_agree = ref_disagree = 0
    for pc in pcs:
        c = pc["concept"]
        vs = vecs.get(c, {})
        if REF[0] in vs and REF[1] in vs:
            if cos(vs[REF[0]], vs[REF[1]]) >= args.tau:
                d = vs[REF[0]] + vs[REF[1]]
                references[c] = d / (np.linalg.norm(d) or 1.0)
                ref_agree += 1
            else:
                ref_disagree += 1
    ref_concepts = set(references.keys())

    def fidelity(S, tau):
        S = tuple(S)
        num = den = 0
        for c in ref_concepts:
            vs = vecs.get(c, {})
            if not all(m in vs for m in S):
                continue
            den += 1
            mv = medoid_vec(c, S)
            if mv is not None and cos(mv, references[c]) >= tau:
                num += 1
        return num, den

    # ---- enumerate all non-empty subsets -> (cost, fidelity) --------------
    costs, cost_prov = cost_table()

    def subset_cost(S):
        cs = [costs[m] for m in S]
        if any(c is None for c in cs):
            return None
        return round(sum(cs), 5)

    subsets = []
    for r in range(1, len(MODELS) + 1):
        for S in itertools.combinations(MODELS, r):
            num, den = fidelity(S, args.tau)
            fid = num / den if den else None
            subsets.append({
                "models": list(S), "size": len(S),
                "cost_usd_per_concept": subset_cost(S),
                "fidelity": round(fid, 4) if fid is not None else None,
                "reproduced": num, "denominator": den,
                "contains_ref_model": any(m in REF for m in S),
            })

    # Pareto frontier over (cost asc, fidelity desc) among subsets with a cost & fidelity
    valid = [s for s in subsets if s["cost_usd_per_concept"] is not None and s["fidelity"] is not None]
    valid.sort(key=lambda s: (s["cost_usd_per_concept"], -s["fidelity"]))
    pareto = []
    best_fid = -1
    for s in valid:
        if s["fidelity"] > best_fid:
            pareto.append(s)
            best_fid = s["fidelity"]

    # cheapest subset that EXCLUDES both reference models reaching thresholds
    def cheapest_at(thresh, exclude_ref=True):
        cands = [s for s in valid if s["fidelity"] >= thresh and
                 (not exclude_ref or not s["contains_ref_model"])]
        cands.sort(key=lambda s: (s["cost_usd_per_concept"], -s["fidelity"], s["size"]))
        return cands[0] if cands else None

    # sensitivity of fidelity to tau for the headline recommendation
    rec95 = cheapest_at(0.95) or cheapest_at(0.95, exclude_ref=False)
    rec90 = cheapest_at(0.90) or cheapest_at(0.90, exclude_ref=False)
    sens = {}
    if rec95:
        for t in [round(args.tau - 0.05, 3), args.tau, round(args.tau + 0.05, 3)]:
            num, den = fidelity(rec95["models"], t)
            sens[t] = {"fidelity": round(num / den, 4) if den else None, "den": den}

    out = {
        "built": "consensus-100 scoring + cheapest-subset (tau=%.2f dim=%d)" % (args.tau, args.dim),
        "tau": args.tau, "dim": args.dim,
        "n_concepts_total": len(pcs),
        "n_with_strong_consensus": n_consensus,
        "per_model_agreement_vs_strong_consensus": per_model,
        "reference": {"models": list(REF),
                      "n_concepts_ref_defined": len(ref_concepts),
                      "sol_fable_agree": ref_agree, "sol_fable_disagree": ref_disagree},
        "cost_table_usd_per_concept": costs,
        "cost_provenance": cost_prov,
        "subsets": subsets,
        "pareto_frontier": pareto,
        "recommended_cheapest_ge95": rec95,
        "recommended_cheapest_ge90": rec90,
        "rec95_tau_sensitivity": sens,
    }
    json.dump(out, open(args.out, "w"), indent=2, ensure_ascii=False)

    # ---- prints -----------------------------------------------------------
    print("\n=== PER-MODEL AGREEMENT vs 6-model strong consensus (n_consensus=%d) ===" % n_consensus)
    for m in MODELS:
        pm = per_model[m]
        print("  %-18s %5s  (%d/%d)" % (m, pm["agreement_rate"], pm["in_consensus"],
                                        pm["of_concepts_with_consensus_and_gloss"]))
    print("\n=== COST proxy ($/concept) ===")
    for m in MODELS:
        print("  %-18s %s" % (m, costs[m]))
    print("\nreference sol+fable: defined on %d concepts (agree=%d disagree=%d)"
          % (len(ref_concepts), ref_agree, ref_disagree))
    print("\n=== PARETO FRONTIER (cost asc / fidelity) ===")
    for s in pareto:
        print("  $%s  fid=%.3f  %s" % (s["cost_usd_per_concept"], s["fidelity"], "+".join(s["models"])))
    print("\nCHEAPEST >=95%% (ref-excluded):", rec95 and ("+".join(rec95["models"]),
          "$%s" % rec95["cost_usd_per_concept"], "fid=%.3f" % rec95["fidelity"]))
    print("CHEAPEST >=90%% (ref-excluded):", rec90 and ("+".join(rec90["models"]),
          "$%s" % rec90["cost_usd_per_concept"], "fid=%.3f" % rec90["fidelity"]))
    print("rec95 tau-sensitivity:", sens)
    print("wrote", args.out)


if __name__ == "__main__":
    main()
