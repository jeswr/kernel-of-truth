#!/usr/bin/env python3
"""truthstyle_2x2.py — pinned analysis for the truthstyle-2x2 probe (DRAFT record
registry/experiments/truthstyle-2x2.json; design docs/design-truthstyle-2x2-f2-taxonomy.md).

Pure function of (items.jsonl, labels.jsonl) -> analysis-output JSON. The verdict is
a pure function of the frozen record's verdict_rules over these output fields
(verdict-gen); nothing here exercises discretion.

Estimand (primary): the STYLE main effect on acceptance at matched truth on the
tier-2 (kernel-bytes) pairs — mean over evaluable (judge, content-pair) of
[accept(nsm) - accept(plain)] — with a TOST equivalence margin of +/-0.10 absolute,
operationalised per P8 §1.5 as the two-one-sided-tests 90% interval (here: the
5th/95th percentiles of a B=10000 concept-cluster bootstrap, seed 20260710) lying
inside (-0.10, +0.10).

Labels file: one JSON line per judgment {"item_id","judge","label"} with label in
{"yes","no","cannot-say"} (anything else = unlabelled; the runner normalises raw
judge output to these three tokens with a pinned mapping, or leaves it raw).
accept := label == "yes"; "no" and "cannot-say" are both non-acceptance (escape
rates reported separately). Retest ":dup" items feed ONLY the retest gate.

--mock: synthesises a null-world label set (style effect 0, strong truth effect,
seeded) over the real committed d-ts items and runs the full pipeline ($0, no
network, no judge). Green mock = mechanics only, never evidence.
"""
import argparse, hashlib, json, os, random, sys

MARGIN = 0.10
B = 10000
BOOT_SEED = 20260710
ALPHA = 0.05
JUDGES = ["judge-p1-gpt56sol", "judge-p2-gpt55", "judge-p3-haiku45"]

def load_items(path):
    items = {}
    for ln in open(path):
        o = json.loads(ln)
        items[o["id"]] = o
    return items

def load_labels(path):
    lab = {}
    for ln in open(path):
        o = json.loads(ln)
        v = o.get("label")
        if v not in ("yes", "no", "cannot-say"):
            v = None
        lab[(o["judge"], o["item_id"])] = v
    return lab

def pairs_of(items, tier):
    """content pairs: (nsm_id, plain_id, concept_cluster, truth) for scored items."""
    out = []
    for it in items.values():
        if it["retest"] or it["tier"] != tier or it["style"] != "nsm":
            continue
        pid = it["id"].replace("-nsm", "-plain")
        if pid in items:
            out.append((it["id"], pid, it["label"], it["truth"]))
    return sorted(out)

def diffs(pairs, labels, items, judges, truth=None, judge=None):
    """per (judge, pair) accept-difference nsm-plain; clustered by concept label."""
    out = []  # (cluster, d)
    for j in judges if judge is None else [judge]:
        for nid, pid, cluster, tr in pairs:
            if truth is not None and tr != truth:
                continue
            a, b = labels.get((j, nid)), labels.get((j, pid))
            if a is None or b is None:
                continue
            out.append((cluster, (1 if a == "yes" else 0) - (1 if b == "yes" else 0)))
    return out

def cluster_boot_means(cd, b=B, seed=BOOT_SEED):
    by = {}
    for c, d in cd:
        by.setdefault(c, []).append(d)
    clusters = sorted(by)
    rng = random.Random(seed)
    means = []
    for _ in range(b):
        acc = []
        for _ in clusters:
            acc.extend(by[clusters[rng.randrange(len(clusters))]])
        means.append(sum(acc) / len(acc) if acc else 0.0)
    return sorted(means)

def pct(sorted_means, q):
    if not sorted_means:
        return 0.0
    i = min(len(sorted_means) - 1, max(0, int(q * len(sorted_means))))
    return sorted_means[i]

def tost(cd):
    if not cd:
        return {"point": 0.0, "ci_low": 0.0, "ci_high": 0.0, "tost_pass": False,
                "leak": False, "p": 1.0, "n": 0}
    point = sum(d for _, d in cd) / len(cd)
    bm = cluster_boot_means(cd)
    lo, hi = pct(bm, ALPHA), pct(bm, 1 - ALPHA)
    p_hi = sum(1 for m in bm if m >= MARGIN) / len(bm)   # H0: mu >= +margin
    p_lo = sum(1 for m in bm if m <= -MARGIN) / len(bm)  # H0: mu <= -margin
    return {"point": point, "ci_low": lo, "ci_high": hi,
            "tost_pass": (lo > -MARGIN and hi < MARGIN),
            "leak": (lo > MARGIN or hi < -MARGIN),
            "p": max(p_lo, p_hi), "n": len(cd)}

def one_sided_gt0(cd):
    if not cd:
        return {"point": 0.0, "p": 1.0, "pass": False, "n": 0}
    bm = cluster_boot_means(cd)
    p = (sum(1 for m in bm if m <= 0.0) + 1) / (len(bm) + 1)
    return {"point": sum(d for _, d in cd) / len(cd), "p": p, "n": len(cd)}

def holm(members):
    """members: dict name->p. returns name->bool (reject at family alpha 0.05)."""
    order = sorted(members, key=lambda k: members[k])
    m = len(order)
    reject, alive = {}, True
    for i, name in enumerate(order):
        thr = ALPHA / (m - i)
        alive = alive and (members[name] < thr)
        reject[name] = alive
    return reject

def truth_effect(pairs_by_word, labels, items, tier, judges):
    """paired within (word, style): accept(correct) - accept(wrong)."""
    ds = []
    for it in items.values():
        if it["retest"] or it["tier"] != tier or it["truth"] != "correct":
            continue
        wid = it["id"].replace(":correct-", ":wrong-")
        if wid not in items:
            continue
        for j in judges:
            a, b = labels.get((j, it["id"])), labels.get((j, wid))
            if a is None or b is None:
                continue
            ds.append((1 if a == "yes" else 0) - (1 if b == "yes" else 0))
    return (sum(ds) / len(ds) if ds else 0.0), len(ds)

def marker_stats(items, rules):
    marks = rules["nsm_register_markers"]
    def mc(t):
        return sum(t.count(m) for m in marks)
    tot = differ = reduced = 0
    for it in items.values():
        if it["retest"] or it["tier"] != "t2" or it["style"] != "nsm":
            continue
        twin = items[it["id"].replace("-nsm", "-plain")]
        tot += 1
        if it["text"] != twin["text"]:
            differ += 1
            if mc(it["text"]) > mc(twin["text"]):
                reduced += 1
    return (differ / tot if tot else 0.0), (reduced / differ if differ else 0.0)

def length_match(items):
    ok = tot = 0
    for it in items.values():
        if it["retest"] or it["truth"] != "wrong":
            continue
        twin = items[it["id"].replace(":wrong-", ":correct-")]
        tot += 1
        if abs(it["len_tokens"] - twin["len_tokens"]) / max(1, twin["len_tokens"]) <= 0.35:
            ok += 1
    return ok / tot if tot else 0.0

def analyse(items, labels, judges):
    scored = [i for i in items.values() if not i["retest"]]
    n_expected = len(scored) * len(judges)
    n_labelled = sum(1 for i in scored for j in judges if labels.get((j, i["id"])) is not None)
    per_judge_cov = {j: sum(1 for i in scored if labels.get((j, i["id"])) is not None) / len(scored)
                     for j in judges}

    t2_pairs = pairs_of(items, "t2")
    t1_pairs = pairs_of(items, "t1")

    cd_primary = diffs(t2_pairs, labels, items, judges)
    primary = tost(cd_primary)

    # Holm family (pre-declared, 3 members)
    m_wrong = one_sided_gt0(diffs(t2_pairs, labels, items, judges, truth="wrong"))
    m_correct = tost(diffs(t2_pairs, labels, items, judges, truth="correct"))
    m_j1 = tost(diffs(t2_pairs, labels, items, judges, judge=judges[0]))
    rej = holm({"wrong_inflation": m_wrong["p"],
                "correct_tost": m_correct["p"],
                "judge1p_tost": m_j1["p"]})

    te1, te1_n = truth_effect(None, labels, items, "t1", judges)
    te2, _ = truth_effect(None, labels, items, "t2", judges)
    per_judge_te1 = {}
    for j in judges:
        v, _ = truth_effect(None, labels, items, "t1", [j])
        per_judge_te1[j] = v
    per_judge_style = {}
    for j in judges:
        cd = diffs(t2_pairs, labels, items, judges, judge=j)
        per_judge_style[j] = (sum(d for _, d in cd) / len(cd)) if cd else 0.0

    esc = {}
    for i in scored:
        cell = f"{i['tier']}:{i['truth']}:{i['style']}"
        for j in judges:
            v = labels.get((j, i["id"]))
            if v is not None:
                a, b = esc.get(cell, (0, 0))
                esc[cell] = (a + (1 if v == "cannot-say" else 0), b + 1)
    escape_rate = {k: (a / b if b else 0.0) for k, (a, b) in sorted(esc.items())}

    # retest gate
    agree = tot = 0
    for i in items.values():
        if not i["retest"]:
            continue
        base = i["id"][:-4]
        for j in judges:
            a, b = labels.get((j, i["id"])), labels.get((j, base))
            if a is not None and b is not None:
                tot += 1
                agree += (a == b)
    retest = (agree / tot) if tot else 0.0

    rules = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        "..", "poc", "truthstyle-2x2", "style-rules.json")))
    differ_frac, marker_frac = marker_stats(items, rules)
    len_frac = length_match(items)

    t1_style = diffs(t1_pairs, labels, items, judges)
    t1_style_point = (sum(d for _, d in t1_style) / len(t1_style)) if t1_style else 0.0

    out = {
        "gates": {
            "label_coverage_valid": (n_labelled / n_expected) >= 0.95 if n_expected else False,
            "pool_valid": all(per_judge_cov[j] >= 0.90 for j in judges)
                          and all(per_judge_te1[j] > 0.0 for j in judges),
            "truth_manipulation_valid": te1 >= 0.30 and te1_n >= 200,
            "style_fidelity_valid": differ_frac >= 0.80 and marker_frac >= 0.80,
            "length_match_valid": len_frac >= 0.90,
            "retest_valid": retest >= 0.85 and tot >= 48,
        },
        "analysis": {
            "n_labelled": n_labelled,
            "label_coverage": (n_labelled / n_expected) if n_expected else 0.0,
            "n_pairs_evaluable": primary["n"],
            "style_effect": primary["point"],
            "style_effect_ci_low": primary["ci_low"],
            "style_effect_ci_high": primary["ci_high"],
            "style_tost_pass": primary["tost_pass"],
            "style_leak_established": primary["leak"],
            "holm": {
                "wrong_cell_style_inflation": rej["wrong_inflation"],
                "wrong_cell_style_inflation_p": m_wrong["p"],
                "wrong_cell_style_inflation_point": m_wrong["point"],
                "correct_cell_style_tost": rej["correct_tost"],
                "correct_cell_style_tost_p": m_correct["p"],
                "correct_cell_style_point": m_correct["point"],
                "judge1p_style_tost": rej["judge1p_tost"],
                "judge1p_style_tost_p": m_j1["p"],
                "judge1p_style_point": m_j1["point"],
            },
            "truth_effect_t1": te1,
            "truth_effect_t2": te2,
            "style_effect_t1_diagnostic": t1_style_point,
            "per_judge_style_effect": per_judge_style,
            "escape_rate_by_cell": escape_rate,
            "retest_agreement": retest,
            "style_fidelity_pair_differ_fraction": differ_frac,
            "style_fidelity_marker_reduction_fraction": marker_frac,
            "length_match_fraction": len_frac,
        },
    }
    return out

def mock_labels(items, path):
    """null world: style effect exactly 0; strong truth effect; seeded; deterministic
    per (judge, tier,label,truth) so retest duplicates agree."""
    with open(path, "w") as f:
        for j in JUDGES:
            for it in items.values():
                # text digest => nsm/plain twins draw independent noise at EQUAL
                # marginal p (true style effect 0, discordance > 0, retest dups agree)
                tdig = hashlib.sha256(it["text"].encode()).hexdigest()[:12]
                key = f"mock|{j}|{it['tier']}|{it['label']}|{it['truth']}|{it['donor']}|{tdig}"
                u = int(hashlib.sha256(key.encode()).hexdigest(), 16) % 10**6 / 10**6
                p_yes = 0.90 if it["truth"] == "correct" else 0.08
                if u < p_yes:
                    lab = "yes"
                elif u < p_yes + 0.05:
                    lab = "cannot-say"
                else:
                    lab = "no"
                u2 = int(hashlib.sha256(("skip|" + key).encode()).hexdigest(), 16) % 100
                if u2 < 2:
                    continue  # ~2% unlabelled
                f.write(json.dumps({"item_id": it["id"], "judge": j, "label": lab}) + "\n")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--items", default="data/d-ts/items.jsonl")
    ap.add_argument("--labels")
    ap.add_argument("--out")
    ap.add_argument("--mock", action="store_true")
    a = ap.parse_args()
    items = load_items(a.items)
    if a.mock:
        lp = a.labels or "/tmp/dts-mock-labels.jsonl"
        mock_labels(items, lp)
        a.labels = lp
    if not a.labels:
        print("ERR_TS_NO_LABELS: --labels required outside --mock", file=sys.stderr)
        sys.exit(1)
    out = analyse(items, load_labels(a.labels), JUDGES)
    blob = json.dumps(out, indent=1, sort_keys=True)
    if a.out:
        open(a.out, "w").write(blob + "\n")
    print(blob)
    if a.mock:
        need = ["style_effect", "style_tost_pass", "style_leak_established"]
        ok = all(k in out["analysis"] for k in need) and len(out["gates"]) == 6
        print("MOCK", "GREEN" if ok else "RED", file=sys.stderr)
        sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
