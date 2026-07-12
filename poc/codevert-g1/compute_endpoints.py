#!/usr/bin/env python3
"""G1-FORWARD endpoints vs the adjudicated PROXY GOLD [ASM-1116].
PROVISIONAL-ON-LLM-PROXY throughout. Verdict is the coordinator's step.

Gold = agreed annotations where fable-a == gpt56-b; else the adjudicated
resolution from annotation/adjudication.jsonl. Endpoints per family + FL-4:
  R_q          = P(status==proved AND gold subset-of listing | gold-answerable)
  R_q_exact    = P(status==proved AND listing == gold | gold-answerable)  (co-report)
  precision    = pooled |listing ∩ gold| / |listing| over proved queries with
                 answerable gold (unanswerable-gold proved queries excluded, counted)
  neg_validity = P(status==proved AND listing==[] | gold-answerable AND gold==[])
"""
import json, os

BASE = os.path.dirname(os.path.abspath(__file__))
ANN = os.path.join(BASE, "annotation")
FAMILIES = ["contains", "contained_in", "imports_of", "where_defined",
            "callees_of"]
FL4 = ["contains", "contained_in", "imports_of", "where_defined"]


def norm(g):
    return sorted(set(str(x).strip() for x in (g or [])))


def main():
    sample = json.load(open(os.path.join(ANN, "sample.json")))
    engine = json.load(open(os.path.join(BASE, "results",
                                         "sample-engine-answers.json")))
    A, B = {}, {}
    for fn in os.listdir(os.path.join(ANN, "answers-a")):
        for r in json.load(open(os.path.join(ANN, "answers-a", fn))):
            A[r["query_id"]] = r
    for fn in os.listdir(os.path.join(ANN, "answers-b")):
        rec = json.load(open(os.path.join(ANN, "answers-b", fn)))
        for r in (rec.get("answers") or []):
            B[r["query_id"]] = r
    adj = {}
    adjpath = os.path.join(ANN, "adjudication.jsonl")
    if os.path.exists(adjpath):
        for line in open(adjpath):
            if line.strip():
                d = json.loads(line)
                adj[d["query_id"]] = d

    gold = {}
    dropped = []
    for q in sample["queries"]:
        qid = q["query_id"]
        a, b = A.get(qid), B.get(qid)
        if a is None or b is None:
            dropped.append({"query_id": qid, "reason": "annotator-missing"})
            continue
        ga, gb = norm(a.get("gold")), norm(b.get("gold"))
        aa, ab = bool(a.get("answerable_static")), bool(b.get("answerable_static"))
        if ga == gb and aa == ab:
            gold[qid] = {"answerable": aa, "gold": ga, "src": "agreed"}
        elif qid in adj:
            gold[qid] = {"answerable": bool(adj[qid]["resolved_answerable"]),
                         "gold": norm(adj[qid]["resolved_gold"]),
                         "src": "adjudicated"}
        else:
            dropped.append({"query_id": qid, "reason": "unadjudicated-disagreement"})

    fam = {f: {"n_gold": 0, "n_answerable": 0, "rq_num": 0, "rq_exact": 0,
               "prec_inter": 0, "prec_listed": 0, "n_proved": 0,
               "n_proved_unanswerable_gold": 0,
               "neg_n": 0, "neg_ok": 0} for f in FAMILIES}
    per_query = []
    for q in sample["queries"]:
        qid, f = q["query_id"], q["family"]
        if qid not in gold:
            continue
        g = gold[qid]
        e = engine[qid]
        st = fam[f]
        st["n_gold"] += 1
        proved = e["status"] == "proved"
        listing = norm(e["listing"])
        row = {"query_id": qid, "family": f, "gold_src": g["src"],
               "answerable": g["answerable"], "gold_n": len(g["gold"]),
               "engine_status": e["status"], "listing_n": len(listing)}
        if proved:
            if g["answerable"]:
                st["n_proved"] += 1
                inter = len(set(listing) & set(g["gold"]))
                st["prec_inter"] += inter
                st["prec_listed"] += len(listing)
                row["prec_frac"] = (inter, len(listing))
            else:
                st["n_proved_unanswerable_gold"] += 1
        if g["answerable"]:
            st["n_answerable"] += 1
            full = proved and set(g["gold"]) <= set(listing)
            exact = proved and listing == g["gold"]
            st["rq_num"] += 1 if full else 0
            st["rq_exact"] += 1 if exact else 0
            row["rq_full"] = full
            if not g["gold"]:
                st["neg_n"] += 1
                st["neg_ok"] += 1 if (proved and not listing) else 0
        per_query.append(row)

    def agg(fams):
        t = {k: 0 for k in ["n_gold", "n_answerable", "rq_num", "rq_exact",
                            "prec_inter", "prec_listed", "n_proved",
                            "n_proved_unanswerable_gold", "neg_n", "neg_ok"]}
        for f in fams:
            for k in t:
                t[k] += fam[f][k]
        return t

    def render(t):
        return {
            "n_gold_queries": t["n_gold"],
            "n_gold_answerable": t["n_answerable"],
            "R_q": round(t["rq_num"] / t["n_answerable"], 4) if t["n_answerable"] else None,
            "R_q_exact": round(t["rq_exact"] / t["n_answerable"], 4) if t["n_answerable"] else None,
            "precision_elements": round(t["prec_inter"] / t["prec_listed"], 4)
                if t["prec_listed"] else None,
            "precision_denominator_elements": t["prec_listed"],
            "n_proved_with_unanswerable_gold_excluded": t["n_proved_unanswerable_gold"],
            "neg_validity": round(t["neg_ok"] / t["neg_n"], 4) if t["neg_n"] else None,
            "n_gold_empty": t["neg_n"]}

    out = {"tag": "MEASURED + PROVISIONAL-ON-LLM-PROXY",
           "gold_sources": {"agreed": sum(1 for g in gold.values() if g["src"] == "agreed"),
                            "adjudicated": sum(1 for g in gold.values() if g["src"] == "adjudicated"),
                            "dropped": dropped},
           "families": {f: render(agg([f])) for f in FAMILIES},
           "FL4_primary": render(agg(FL4)),
           "callees_of_sensitivity": render(agg(["callees_of"])),
           "floors_quoted_ASM_1030": {"kappa_q_indep": 0.5, "R_q": 0.90,
                                      "precision": 0.95, "neg_validity": 0.90},
           "note": "verdict-INPUT only; coordinator performs the mechanical verdict"}
    with open(os.path.join(BASE, "results", "g1-endpoints-proxygold.json"), "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
    with open(os.path.join(BASE, "results", "g1-endpoints-perquery.jsonl"), "w") as f:
        for r in per_query:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    print(json.dumps({"FL4": out["FL4_primary"],
                      "callees": out["callees_of_sensitivity"],
                      "gold_sources": {k: v for k, v in out["gold_sources"].items()
                                       if k != "dropped"},
                      "n_dropped": len(dropped)}, indent=1))


if __name__ == "__main__":
    main()
