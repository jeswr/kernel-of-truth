#!/usr/bin/env python3
"""Inter-annotator agreement (RAW, pre-adjudication) between fable-a and
gpt56-b, and the disagreement queue for adjudication [ASM-1113]."""
import json, os

BASE = os.path.dirname(os.path.abspath(__file__))
ANN = os.path.join(BASE, "annotation")
FAMILIES = ["contains", "contained_in", "imports_of", "where_defined",
            "callees_of"]


def load_a():
    out = {}
    d = os.path.join(ANN, "answers-a")
    for fn in sorted(os.listdir(d)):
        for row in json.load(open(os.path.join(d, fn))):
            out[row["query_id"]] = row
    return out


def load_b():
    out, nolabel = {}, []
    d = os.path.join(ANN, "answers-b")
    for fn in sorted(os.listdir(d)):
        rec = json.load(open(os.path.join(d, fn)))
        if rec.get("no_label") or not rec.get("answers"):
            nolabel.append(fn)
            continue
        for row in rec["answers"]:
            out[row["query_id"]] = row
    return out, nolabel


def norm(gold):
    return sorted(set(str(x).strip() for x in (gold or [])))


def jacc(x, y):
    sx, sy = set(x), set(y)
    if not sx and not sy:
        return 1.0
    return len(sx & sy) / len(sx | sy)


def cohen_kappa(pairs):
    n = len(pairs)
    if not n:
        return None
    po = sum(1 for a, b in pairs if a == b) / n
    pa = sum(1 for a, _ in pairs if a) / n
    pb = sum(1 for _, b in pairs if b) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    if pe == 1.0:
        return 1.0
    return (po - pe) / (1 - pe)


def main():
    sample = json.load(open(os.path.join(ANN, "sample.json")))
    A = load_a()
    B, nolabel = load_b()
    fam_stats = {f: {"n": 0, "set_agree": 0, "jaccard_sum": 0.0,
                     "ans_pairs": [], "missing": 0} for f in FAMILIES}
    disagreements = []
    for q in sample["queries"]:
        qid, fam = q["query_id"], q["family"]
        a, b = A.get(qid), B.get(qid)
        if a is None or b is None:
            fam_stats[fam]["missing"] += 1
            continue
        ga, gb = norm(a.get("gold")), norm(b.get("gold"))
        aa = bool(a.get("answerable_static"))
        ab = bool(b.get("answerable_static"))
        st = fam_stats[fam]
        st["n"] += 1
        st["ans_pairs"].append((aa, ab))
        agree = (ga == gb and aa == ab)
        if agree:
            st["set_agree"] += 1
        st["jaccard_sum"] += jacc(ga, gb)
        if not agree:
            disagreements.append({
                "query_id": qid, "family": fam, "repo": q["repo"],
                "target": q["target"],
                "a": {"answerable": aa, "gold": ga,
                      "notes": a.get("notes", "")},
                "b": {"answerable": ab, "gold": gb,
                      "notes": b.get("notes", "")}})
    report = {"annotators": ["fable-a (Claude-family subagents)",
                             "gpt56-b (gpt-5.6-sol, effort medium)"],
              "b_no_label_batches": nolabel, "families": {}}
    allpairs, tot, agr, js = [], 0, 0, 0.0
    for f in FAMILIES:
        st = fam_stats[f]
        allpairs.extend(st["ans_pairs"])
        tot += st["n"]
        agr += st["set_agree"]
        js += st["jaccard_sum"]
        report["families"][f] = {
            "n_compared": st["n"], "missing": st["missing"],
            "exact_agreement": round(st["set_agree"] / st["n"], 4) if st["n"] else None,
            "mean_jaccard": round(st["jaccard_sum"] / st["n"], 4) if st["n"] else None,
            "answerability_kappa": (round(cohen_kappa(st["ans_pairs"]), 4)
                                    if cohen_kappa(st["ans_pairs"]) is not None else None)}
    report["overall"] = {
        "n_compared": tot,
        "exact_agreement": round(agr / tot, 4) if tot else None,
        "mean_jaccard": round(js / tot, 4) if tot else None,
        "answerability_kappa": (round(cohen_kappa(allpairs), 4)
                                if cohen_kappa(allpairs) is not None else None),
        "n_disagreements": len(disagreements)}
    with open(os.path.join(ANN, "agreement-raw.json"), "w") as f:
        json.dump(report, f, indent=1, sort_keys=True)
    with open(os.path.join(ANN, "disagreements.jsonl"), "w") as f:
        for d in disagreements:
            f.write(json.dumps(d, sort_keys=True) + "\n")
    print(json.dumps(report["overall"], indent=1))
    for f in FAMILIES:
        print(f, report["families"][f])


if __name__ == "__main__":
    main()
