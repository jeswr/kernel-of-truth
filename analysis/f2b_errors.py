#!/usr/bin/env python3
"""f2b_errors.py — pinned analysis for the f2b-errors consumer record (DRAFT record
registry/experiments/f2b-errors.json; design docs/design-truthstyle-2x2-f2-taxonomy.md §5;
closed taxonomy poc/f2b-errors/taxonomy.json — this script implements that tree VERBATIM).

Pure function of (stage-2 per-attempt log, stage-2 pinned analysis output) -> output JSON.
Consumes f2b-transfer Stage-2 cells; runs NO model, spends NO GPU. It can never flip the
frozen f2b-transfer verdict.

Inputs:
  --cells      jsonl, one line per (arm, item, seed) cell with the taxonomy.json
               required_logged_fields (arms: kernel-verify-retry + model-alone R1).
  --stage2-out the pinned analysis/f2b_transfer.py output JSON (echoes
               /analysis/primary_reject and /analysis/effect_size; fail-closed if absent).
  --mock       synthesise a plausible Stage-2 world (pinned RNG) and run everything ($0).
"""
import argparse, hashlib, json, random, sys

B = 10000
BOOT_SEED = 20260710

CATS = ["X-EXTRACT", "X-NONENGAGE", "X-GOLDCONFLICT",
        "X-EXHAUST-STABLE", "X-EXHAUST-WANDER", "X-OTHER"]

def assign(cell):
    """poc/f2b-errors/taxonomy.json assignment_procedure, verbatim order."""
    att = cell["attempts"]
    fin = att[cell["final_attempt_index"]]
    if not fin.get("extraction_ok", False):
        return "X-EXTRACT"
    if all(a.get("verifier_decision") == "abstain" for a in att):
        return "X-NONENGAGE"
    if fin.get("verifier_decision") == "accept":
        return "X-GOLDCONFLICT"
    if not any(a.get("verifier_decision") == "accept" for a in att):
        ans = [a.get("extracted_answer") for a in att if a.get("extraction_ok")]
        if len(ans) >= 2 and len(set(ans)) == 1:
            return "X-EXHAUST-STABLE"
        if len(set(ans)) > 1:
            return "X-EXHAUST-WANDER"
    return "X-OTHER"

REQ = ["item_id", "concept_label", "template_type", "seed", "arm",
       "final_attempt_index", "item_correct_ext_final", "item_correct_ext_attempt0",
       "attempts"]

def analyse(cells, stage2):
    verify = [c for c in cells if c["arm"] == "kernel-verify-retry"]
    alone = [c for c in cells if c["arm"] == "model-alone"]
    fields_ok = bool(verify) and bool(alone) and all(
        all(k in c for k in REQ) for c in verify)

    failures = [c for c in verify if not c["item_correct_ext_final"]]
    comp = {k: 0 for k in CATS}
    for c in failures:
        comp[assign(c)] += 1
    nf = len(failures)
    other_rate = (comp["X-OTHER"] / nf) if nf else 0.0

    harmful = sum(1 for c in verify
                  if c["item_correct_ext_attempt0"] and not c["item_correct_ext_final"])
    benign = sum(1 for c in verify
                 if not c["item_correct_ext_attempt0"] and c["item_correct_ext_final"])

    # ---- effect re-computation + concept-cluster bootstrap (taxonomy §declared_exploratory_reanalysis)
    def item_means(rows):
        by = {}
        for c in rows:
            by.setdefault(c["item_id"], []).append(c["item_correct_ext_final"])
        return {k: sum(v) / len(v) for k, v in by.items()}
    mv, ma = item_means(verify), item_means(alone)
    common = sorted(set(mv) & set(ma))
    diffs = {i: mv[i] - ma[i] for i in common}
    concept_of = {c["item_id"]: c["concept_label"] for c in verify}
    clusters = {}
    for i in common:
        clusters.setdefault(concept_of.get(i, "?"), []).append(diffs[i])
    names = sorted(clusters)
    point = sum(diffs.values()) / len(diffs) if diffs else 0.0

    rng = random.Random(BOOT_SEED)
    boots = []
    for _ in range(B):
        acc = []
        for _ in names:
            acc.extend(clusters[names[rng.randrange(len(names))]])
        boots.append(sum(acc) / len(acc) if acc else 0.0)
    boots.sort()
    lb = boots[int(0.05 * len(boots))] if boots else 0.0

    # item-level (unclustered) percentile CI width for the pricing ratio
    vals = list(diffs.values())
    iboots = []
    for _ in range(2000):
        acc = [vals[rng.randrange(len(vals))] for _ in vals] if vals else []
        iboots.append(sum(acc) / len(acc) if acc else 0.0)
    iboots.sort()
    def width(bs):
        return (bs[int(0.95 * len(bs))] - bs[int(0.05 * len(bs))]) if bs else 0.0
    ratio = (width(boots) / width(iboots)) if width(iboots) > 0 else 0.0

    # leave-one-seed-out jackknife
    seeds = sorted({c["seed"] for c in verify})
    jk = []
    for s in seeds:
        v2 = item_means([c for c in verify if c["seed"] != s])
        a2 = item_means([c for c in alone if c["seed"] != s])
        cm = sorted(set(v2) & set(a2))
        jk.append(sum(v2[i] - a2[i] for i in cm) / len(cm) if cm else 0.0)

    reject = bool(stage2.get("analysis", {}).get("primary_reject", False))
    return {
        "gates": {
            "fields_available": fields_ok and bool(stage2),
            "assignment_total": nf > 0 and other_rate <= 0.02,
        },
        "analysis": {
            "n_failure_cells": nf,
            "n_eval_items": len(common),
            "composition_counts": comp,
            "composition": {k: (v / nf if nf else 0.0) for k, v in comp.items()},
            "goldconflict_rate": (comp["X-GOLDCONFLICT"] / nf) if nf else 0.0,
            "harmful_flip_count": harmful,
            "harmful_flip_rate": harmful / len(verify) if verify else 0.0,
            "benign_flip_count": benign,
            "benign_flip_rate": benign / len(verify) if verify else 0.0,
            "stage2_primary_reject": reject,
            "primary_effect_point": point,
            "primary_effect_cluster_lb": lb,
            "cluster_robust": lb > 0.0,
            "cluster_ci_width_ratio": ratio,
            "seed_jackknife_min": min(jk) if jk else 0.0,
            "seed_jackknife_max": max(jk) if jk else 0.0,
        },
    }

def mock_world(path):
    """250 items over ~100 concepts x 4 templates, 3 seeds, verify + alone arms;
    a real lift; every taxonomy branch exercised; pinned hash-noise."""
    def u(*k):
        return int(hashlib.sha256("|".join(map(str, k)).encode()).hexdigest(), 16) % 10**6 / 10**6
    with open(path, "w") as f:
        for it in range(250):
            concept = f"c{it % 100:03d}"
            tpl = ["def-match", "term-match", "claim-true", "claim-false"][it % 4]
            gold_conflict = u("gc", it) < 0.10  # ext gold disagrees with membership
            for seed in (0, 1, 2):
                base = u("alone", it, seed) < 0.40
                f.write(json.dumps({
                    "item_id": f"dqat:{it}", "concept_label": concept,
                    "template_type": tpl, "seed": seed, "arm": "model-alone",
                    "final_attempt_index": 0, "item_correct_ext_attempt0": int(base),
                    "item_correct_ext_final": int(base), "item_correct_mem_final": int(base),
                    "attempts": [{"attempt_index": 0, "extraction_ok": True,
                                  "extracted_answer": "a" if base else "b",
                                  "verifier_decision": "abstain"}]}) + "\n")
                r = u("v", it, seed)
                a0 = u("a0", it, seed) < 0.40
                if r < 0.02:      # extraction failure at final
                    att = [{"attempt_index": k, "extraction_ok": k < 4,
                            "extracted_answer": None if k == 4 else f"x{k}",
                            "verifier_decision": "reject"} for k in range(5)]
                    fin, ext0, extf, memf = 4, int(a0), 0, 0
                elif r < 0.06:    # undecidable
                    att = [{"attempt_index": 0, "extraction_ok": True,
                            "extracted_answer": "y", "verifier_decision": "abstain"}]
                    fin, ext0, extf, memf = 0, int(a0), int(a0), int(a0)
                elif r < 0.72:    # accepted (canonical) — ext-correct unless gold conflict
                    if u("late", it, seed) < 0.5:
                        # accept after a rejected wrong attempt-0 (benign-flip mechanism)
                        att = [{"attempt_index": 0, "extraction_ok": True,
                                "extracted_answer": "off", "verifier_decision": "reject"},
                               {"attempt_index": 1, "extraction_ok": True,
                                "extracted_answer": "canon", "verifier_decision": "accept"}]
                        fin, ext0 = 1, 0
                    else:
                        att = [{"attempt_index": 0, "extraction_ok": True,
                                "extracted_answer": "canon", "verifier_decision": "accept"}]
                        fin, ext0 = 0, int(not gold_conflict)
                    extf, memf = int(not gold_conflict), 1
                elif r < 0.86:    # exhaust, stable answers
                    att = [{"attempt_index": k, "extraction_ok": True,
                            "extracted_answer": "same", "verifier_decision": "reject"}
                           for k in range(5)]
                    fin, ext0, extf, memf = 4, 0, 0, 0
                else:             # exhaust, wandering (may destroy a right attempt-0)
                    att = [{"attempt_index": k, "extraction_ok": True,
                            "extracted_answer": f"w{k}", "verifier_decision": "reject"}
                           for k in range(5)]
                    fin, ext0, extf, memf = 4, int(u("hf", it, seed) < 0.5), 0, 0
                f.write(json.dumps({
                    "item_id": f"dqat:{it}", "concept_label": concept,
                    "template_type": tpl, "seed": seed, "arm": "kernel-verify-retry",
                    "final_attempt_index": fin, "item_correct_ext_attempt0": ext0,
                    "item_correct_ext_final": extf, "item_correct_mem_final": memf,
                    "attempts": att}) + "\n")
    return {"analysis": {"primary_reject": True, "effect_size": 0.25}}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cells")
    ap.add_argument("--stage2-out")
    ap.add_argument("--out")
    ap.add_argument("--mock", action="store_true")
    a = ap.parse_args()
    if a.mock:
        a.cells = a.cells or "/tmp/f2b-errors-mock-cells.jsonl"
        stage2 = mock_world(a.cells)
    else:
        if not (a.cells and a.stage2_out):
            print("ERR_F2BE_INPUTS: --cells and --stage2-out required", file=sys.stderr)
            sys.exit(1)
        stage2 = json.load(open(a.stage2_out))
    cells = [json.loads(l) for l in open(a.cells)]
    out = analyse(cells, stage2)
    blob = json.dumps(out, indent=1, sort_keys=True)
    if a.out:
        open(a.out, "w").write(blob + "\n")
    print(blob)
    if a.mock:
        ok = (out["gates"]["assignment_total"]
              and out["analysis"]["composition_counts"]["X-OTHER"] == 0
              and all(out["analysis"]["composition_counts"][c] > 0 for c in
                      ["X-EXTRACT", "X-NONENGAGE", "X-GOLDCONFLICT",
                       "X-EXHAUST-STABLE", "X-EXHAUST-WANDER"])
              and out["analysis"]["harmful_flip_count"] > 0
              and out["analysis"]["benign_flip_count"] > 0)
        print("MOCK", "GREEN" if ok else "RED", file=sys.stderr)
        sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
