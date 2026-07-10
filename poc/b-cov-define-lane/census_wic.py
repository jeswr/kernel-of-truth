#!/usr/bin/env python3
"""b-cov define-lane census — WiC CELL (bead kernel-of-truth-hu10) — MEASURED-exploratory.

Runs the ONE cell hu10 could not run: WiC. Uses a VERIFIED-FAITHFUL DISCLOSED
MIRROR (aps/super_glue config wic, dev/validation split, 638 items) pinned by
fetch_wic.py — see data/wic-fetch-manifest.json for provenance + faithfulness
evidence. This is a census-local exploratory input; it does NOT change the
programme fail-closed sourcing policy (data/d-ext/manifest.json).

Pipeline = EXACTLY hu10's other cells (reuses census.py machinery verbatim):
  leg 1 record  : onto-obo logicalDefinition (endorsed shards {go,so,mondo})
  leg 2 licence : data/axioms-definitional-v0/ endorsements (build_engine loads)
  leg 3 mapper  : mapper/dist/src/defineTemplates.js parseDefineQuestion (run_mapper.mjs)
  §C5 filter    : inverse-index collision count over the §2.2 DEFINE-MATCH canonical
                  form; item define-checkable iff n==1 [ASM-0131, memo §6 C5].

Item construction (faithful, NON-reframing): each WiC item is fed as its VERBATIM
natural-language content — text = "<sentence1> <sentence2>" (the two contexts the
item presents); options = [target word] (the item's candidate concept, used ONLY
for the diagnostic optionUrns resolution, exactly as MC options are in the other
cells). WiC presents no define-question, so the mapper-parse κ_B is expected ~0 by
the design projection (§5.2 / ASM-0019: "WiC is general-vocabulary and mostly NOT
biomedical, so its define-checkable yield may be small or ~0"). The census MEASURES
that, it does not assume it.

SUPPLEMENTARY breadth diagnostic (clearly labelled, NOT the headline κ_B): the more
informative WiC number for the design's §5.2 question — of the 638 dev target
words, how many even resolve to a UNIQUE licensed onto-obo concept, and of those,
how many carry a logicalDefinition (engine DEFINE-retrieve answerable). This prices
"how biomedical/definitional is WiC's vocabulary".

NO verdict / NO interpretation / NO registry write. Opus (runner) reports mechanical
counts; Fable interprets. Every number tagged MEASURED-exploratory.
"""
import json, os, sys, collections

ROOT = "."
HERE = os.path.join(ROOT, "poc", "b-cov-define-lane")
sys.path.insert(0, os.path.join(ROOT, "tools", "axiom"))
sys.path.insert(0, HERE)
import kot_axiom as K  # noqa: E402
import census as C  # noqa: E402


def load_wic():
    path = os.path.join(HERE, "data", "wic-validation.jsonl")
    items = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            # faithful, non-reframing text: the two contexts the item presents.
            text = (r["sentence1"].strip() + " " + r["sentence2"].strip()).strip()
            items.append({
                "id": "wic-dev-%d" % r["idx"],
                "text": text,
                "options": [r["word"]],   # the target word = candidate concept
                "gold": r["label"],       # 1=same sense, 0=different sense
                "word": r["word"],
            })
    return path, items


def breadth_diagnostic(items, eng, detail_fh):
    """SUPPLEMENTARY (not headline κ_B): resolve each WiC target word to a licensed
    onto-obo concept (via the mapper's byte-faithful resolveLabel through run_mapper
    optionUrns) and DEFINE-retrieve it. Prices WiC vocabulary breadth."""
    parses = C.run_mapper(items)
    res = collections.Counter()
    engine = collections.Counter()
    for it in items:
        rec = parses[it["id"]]
        ou = rec.get("optionUrns", [])
        kind = ou[0]["kind"] if ou else "none"
        detail = {"id": it["id"], "word": it["word"], "resolve_kind": kind}
        if kind == "urn":
            res["resolved_unique"] += 1
            urn = ou[0]["urn"]
            r = eng.query({"op": "define", "subject": urn})
            code = "answer" if r.get("status") == "answer" else r.get("code")
            engine[code] += 1
            detail["urn"] = urn
            detail["engine"] = code
        elif kind == "abstain":
            res["resolved_abstain_gt1_urn"] += 1
            detail["urns"] = ou[0].get("urns")
        else:
            res["unresolved_no_label"] += 1
        detail_fh.write(json.dumps(detail, ensure_ascii=False) + "\n")
    return {
        "epistemic_tag": "MEASURED-exploratory (SUPPLEMENTARY breadth, not headline "
                         "κ_B): WiC target-word resolvability into the endorsed "
                         "onto-obo definitional substrate",
        "n_target_words": len(items),
        "resolution": dict(res),
        "define_retrieve_engine_outcomes_over_resolved_unique": dict(engine),
        "define_checkable_via_retrieve": engine.get("answer", 0),
    }


def main():
    eng = K.build_engine(ROOT)

    # §C5 inverse index over the resolved definitional index (memo §6 C5 step 1) —
    # identical construction to census.py main().
    inv = collections.defaultdict(list)
    for x, entry in eng.defn.items():
        inv[C.canon_key(entry["genus"], entry["differentiae"])].append(x)
    for k in inv:
        inv[k] = sorted(set(inv[k]))
    internal_collision_keys = sum(1 for v in inv.values() if len(v) > 1)

    src_path, items = load_wic()

    detail_path = os.path.join(HERE, "detail", "wic-census-detail.jsonl")
    with open(detail_path, "w", encoding="utf-8") as detail_fh:
        # headline cell — EXACT hu10 machinery
        summary = C.census_benchmark("WiC-dev", src_path, items, eng, inv, detail_fh)

    breadth_path = os.path.join(HERE, "detail", "wic-breadth-detail.jsonl")
    with open(breadth_path, "w", encoding="utf-8") as bfh:
        breadth = breadth_diagnostic(items, eng, bfh)

    # disclosed-mirror provenance (mirror of fetch_wic manifest, echoed here)
    with open(os.path.join(HERE, "data", "wic-fetch-manifest.json"),
              encoding="utf-8") as f:
        fetch_manifest = json.load(f)

    endorsement_shas = {s: "sha256:" + C.sha256_file(
        os.path.join(ROOT, "data", "onto-obo", s))[7:] for s in C.ENDORSED_SHARDS}

    out = {
        "census": "b-cov define-lane WiC cell (kernel-of-truth-hu10)",
        "epistemic_tag": "MEASURED-exploratory",
        "runner_role": "Opus experiment-runner — mechanical counts only; NO verdict, "
                       "NO interpretation (Fable interprets); NO registry write.",
        "method_ref": C.METHOD_REF,
        "item_construction": "text = '<sentence1> <sentence2>' (verbatim WiC contexts, "
                             "non-reframing); options = [target word]. Headline κ_B is "
                             "the mapper-parse §C5 lane, identical to hu10's cells.",
        "disclosed_mirror_provenance": {
            "canonical_predeclared_source": fetch_manifest["canonical_predeclared_source"],
            "mirror_used": fetch_manifest["mirror_used"],
            "faithfulness_verification": fetch_manifest["faithfulness_verification"],
            "census_local_disclosed_input": True,
            "does_not_change_fail_closed_policy": "data/d-ext/manifest.json unchanged",
        },
        "engine_definitional_index": {
            "defn_licensed": len(eng.defn_licensed),
            "defn_resolved": len(eng.defn),
            "defn_unresolved": len(eng.defn_unresolved),
            "distinct_definition_keys": len(inv),
            "internal_collision_keys_ge2": internal_collision_keys,
        },
        "pins": {
            "endorsed_shards": C.ENDORSED_SHARDS,
            "endorsed_shard_sha256": endorsement_shas,
            "define_index_sha256": C.sha256_file(C.INDEX_JSON),
            "wic_input_sha256": summary["input_sha256"],
            "grammar": "kot-query/1 define-op (two-shape DEFINE / DEFINE-MATCH)",
        },
        "headline_cell": summary,
        "supplementary_breadth_diagnostic": breadth,
    }
    summary_path = os.path.join(HERE, "wic-census-summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, sort_keys=False, ensure_ascii=False)

    # console table (same shape as census.py)
    print("\n=== b-cov define-lane WiC cell (MEASURED-exploratory) ===")
    print("mirror: %s cfg=%s split=%s commit=%s (DISCLOSED, faithfulness PASS)" % (
        fetch_manifest["mirror_used"]["hf_repo"],
        fetch_manifest["mirror_used"]["config"],
        fetch_manifest["mirror_used"]["split"],
        fetch_manifest["mirror_used"]["hf_commit_sha"][:12]))
    mo = summary["mapper_parse_outcomes"]
    hdr = "%-12s %6s %7s %10s | %5s %5s %6s %5s %5s" % (
        "benchmark", "N", "check", "kappaB", "noT", "slot", "abst", "retr", "cand")
    print(hdr)
    print("%-12s %6d %7d %10.4f | %5d %5d %6d %5d %5d" % (
        summary["benchmark"], summary["n_total"], summary["n_checkable_C5_n1"],
        summary["kappa_B_engine_mapper"], mo["unmapped_no_template"],
        mo["unmapped_slot_unresolved"], mo["abstain_slot_collision"],
        mo["define_retrieve"], mo["candidate_bearing_C5_population"]))
    c5 = summary["c5_breakdown"]
    print("§C5 breakdown (n0 / n1 / n2+): %d / %d / %d" % (
        c5["n0_no_match"], c5["n1_checkable"],
        c5["n2plus_collision_dropped_INELIGIBLE_DEFN_COLLISION"]))
    print("supplementary breadth: target-word resolution=%s | define-retrieve=%s" % (
        breadth["resolution"],
        breadth["define_retrieve_engine_outcomes_over_resolved_unique"]))
    print("\nsummary -> %s\ndetail  -> %s\nbreadth -> %s" % (
        summary_path, detail_path, breadth_path))


if __name__ == "__main__":
    main()
