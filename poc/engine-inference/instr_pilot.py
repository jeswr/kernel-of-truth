#!/usr/bin/env python3
# ENGINE-INF mandatory blocking instrument pilot (pre-freeze, per the
# programme-wide protocol docs/next/protocol/blocking-pilot-before-freeze.md
# ASM-1830/1831; ENGINE-INF instantiation design §5, ASM-1963; build
# operationalisations ASM-2003..2005).
#
# One CPU run over a tiny deterministic slice, $0 model spend, mode REAL
# (the instrument IS a CPU engine — the real instrument at the operating
# point costs $0). Verdict semantics: instrument-validity ONLY; pilot rows
# are never campaign evidence and may not be quoted for or against any
# registered hypothesis (ASM-1835 fence).
#
# Checks (mechanical predicates over emitted rows, thresholds pre-declared):
#   PC-1 no_degenerate_arm      every baseline strictly between 0 and 1 on
#                               the slice; refusal rate <= 0.5 on non-G4
#                               cells for every arm (divergent-cell scores
#                               additionally REPORTED as evidence; the
#                               whole-slice floor is the gate — ASM-2003)
#   PC-2 separation_nonvacuous  |Div(K,D-word-dom)| >= 6 and
#                               |Div(K,B-wn)| >= 3 on the slice, spanning
#                               >= 2 closure ops and >= 2 lemmas — the
#                               non-vacuous-divergence existence proof
#                               (the anti-knull gate, ASM-1939(a))
#   PC-3 controls_nondegenerate K-shuf differs from K on >= 0.5 of the
#                               slice Div(K,D-word-dom) cells with the
#                               predicted signature (false conflicts on
#                               attested / missed anomalies); D-word-union
#                               not row-identical to D-word-dom;
#                               deterministic channel => replicate noise is
#                               exactly 0, margins are exact
#   PC-4 gate_teeth             (a) planted mistyped axiom (break.violate
#                               range flip) changes EXACTLY the predicted
#                               K rows and nothing else; (b) poisoned-gold
#                               canary: gold perturbation leaves every
#                               arm's compiled TBox + worlds byte-identical
#                               (no compiler reads gold); (c) a PLANTED
#                               gold-reading world-compiler must trip the
#                               canary; (d) kernel-module provenance: every
#                               domain/range target is a minted engineinf
#                               class (G2-independence grep, design §2.1)
#   PC-5 elicitable_gold        extractor yield >= 0.95 on candidate
#                               occurrences (named exclusion reasons for
#                               the rest); oracle arm scores 1.0 through
#                               the pinned scorer; double-run determinism
#                               sha match; B-wn frame availability
#
# Kernel-as-text control: structurally N/A (no prompt surface exists in the
# instrument) -> recorded per protocol §2, downgrading the best verdict to
# PILOT-PASS-WITH-FLAGS. Never a silent pass.

import json
import shutil
import sys
from pathlib import Path

from engineinf_lib import (ARM_NAMES, WN, arm_relation, arm_tbox_paths,
                           canon_sha, kernel_inventory, load_tbox,
                           neutral_world, run_item, score, sha256_file,
                           derived_sides, MODULE, ROOT, C)

HERE = Path(__file__).resolve().parent
OUT = HERE / "results"
sys.path.insert(0, str(ROOT / "tools" / "registry"))
import kot_common as kc  # noqa: E402  (corpus-hash recipe, RT-14 pseudonyms)

# ---- pre-declared constants (changing any after a coordinator has read a
# pilot result requires a fresh pilot — ASM-1815 discipline) ----
SLICE_PER_GROUP = 2          # first N per (lemma, kind), canonical id order
PC1_REFUSAL_CAP = 0.5
PC2_MIN_DIV_DWORDDOM = 6
PC2_MIN_DIV_BWN = 3
PC2_MIN_OPS = 2
PC2_MIN_LEMMAS = 2
PC3_MIN_KSHUF_DIFF_FRAC = 0.5
PC5_MIN_YIELD = 0.95
USD_CAP = 2.0
DATE = "2026-07-12T00:00:00Z"   # fixed (deterministic artifact bytes)


def pilot_slice(items):
    by_group = {}
    for it in items:  # items are already id-sorted
        by_group.setdefault((it["lemma"], it["kind"]), []).append(it)
    out = []
    for g in sorted(by_group):
        out.extend(by_group[g][:SLICE_PER_GROUP])
    return sorted(out, key=lambda it: it["id"])


def decide_all(wn, slice_items, gold, minted, tbox_paths):
    tboxes = {a: load_tbox(p) for a, p in sorted(tbox_paths.items())}
    rows = {}
    for it in slice_items:
        world = neutral_world(wn, it)
        for arm in ARM_NAMES:
            v, r, d = run_item(tboxes[arm], world, arm_relation(arm, it, minted))
            correct, pen = score(gold[it["id"]], v, d)  # ASM-2116: G4 vacuity check
            rows[(arm, it["id"])] = {
                "arm": arm, "item": it["id"], "kind": it["kind"],
                "lemma": it["lemma"], "gold_rule": gold[it["id"]]["gold_rule"],
                "gold_verdict": gold[it["id"]]["verdict"], "verdict": v,
                "refusal": r, "derived_sides": derived_sides(d),
                "correct": bool(correct), "honesty_penalty": pen}
        ov = gold[it["id"]]["verdict"]
        oc, op = score(gold[it["id"]], ov)
        rows[("oracle", it["id"])] = {
            "arm": "oracle", "item": it["id"], "kind": it["kind"],
            "lemma": it["lemma"], "gold_rule": gold[it["id"]]["gold_rule"],
            "gold_verdict": ov, "verdict": ov, "refusal": None,
            "derived_sides": [], "correct": bool(oc), "honesty_penalty": op}
    return rows


def compile_worlds_sha(wn, slice_items, gold_doc):
    """The REAL shared world compiler ignores gold entirely; its output sha
    must be invariant under gold perturbation (poisoned-gold canary)."""
    worlds = [neutral_world(wn, it) for it in slice_items]
    return canon_sha(worlds)


def planted_gold_reading_compiler_sha(wn, slice_items, gold_doc):
    """PC-4(c): a deliberately gold-reading compiler variant — it copies the
    gold verdict into the world bytes. MUST trip the canary."""
    worlds = []
    for it in slice_items:
        w = neutral_world(wn, it)
        w["stated"] = w["stated"] + [["cls", w["undergoer"],
                                      "urn:leak:%s" % gold_doc[it["id"]]["verdict"]]]
        worlds.append(w)
    return canon_sha(worlds)


def main():
    wn = WN()
    minted, _, _ = kernel_inventory()
    items_doc = json.load(open(OUT / "items.json"))
    items = items_doc["items"]
    gold = json.load(open(OUT / "gold.json"))["gold"]
    sl = pilot_slice(items)
    ids = [it["id"] for it in sl]

    rows = decide_all(wn, sl, gold, minted, arm_tbox_paths(HERE / "arms"))
    rows2 = decide_all(wn, sl, gold, minted, arm_tbox_paths(HERE / "arms"))
    det_sha = canon_sha({"%s|%s" % k: v for k, v in sorted(rows.items())})
    det_ok = det_sha == canon_sha({"%s|%s" % k: v for k, v in sorted(rows2.items())})

    def sig(arm, iid):
        r = rows[(arm, iid)]
        return (r["verdict"], r["refusal"] or "", tuple(r["derived_sides"]))

    # ---- PC-2: divergence on the slice ----
    div_dd = [i for i in ids if sig("K", i) != sig("D-word-dom", i)]
    div_bwn = [i for i in ids if sig("K", i) != sig("B-wn", i)]

    def ops_of(b, iid):
        k, r = rows[("K", iid)], rows[(b, iid)]
        o = []
        if tuple(k["derived_sides"]) != tuple(r["derived_sides"]):
            o.append("O1")
        if (k["verdict"] == "ANOMALOUS") != (r["verdict"] == "ANOMALOUS"):
            o.append("O2")
        if (k["verdict"] == "REFUSE") != (r["verdict"] == "REFUSE"):
            o.append("O3")
        return o

    dd_ops = sorted({o for i in div_dd for o in ops_of("D-word-dom", i)})
    dd_lemmas = sorted({rows[("K", i)]["lemma"] for i in div_dd})
    pc2 = (len(div_dd) >= PC2_MIN_DIV_DWORDDOM
           and len(div_bwn) >= PC2_MIN_DIV_BWN
           and len(dd_ops) >= PC2_MIN_OPS and len(dd_lemmas) >= PC2_MIN_LEMMAS)

    # ---- PC-1: arm degeneracy ----
    arm_scores, refusal_rates, div_scores = {}, {}, {}
    for arm in ARM_NAMES:
        arm_scores[arm] = sum(1 for i in ids if rows[(arm, i)]["correct"]) / len(ids)
        non_g4 = [i for i in ids if rows[(arm, i)]["gold_rule"] != "G4"]
        refusal_rates[arm] = (sum(1 for i in non_g4
                                  if rows[(arm, i)]["verdict"] == "REFUSE")
                              / len(non_g4) if non_g4 else 0.0)
        dcells = div_dd if arm != "B-wn" else div_bwn
        div_scores[arm] = (sum(1 for i in dcells if rows[(arm, i)]["correct"])
                           / len(dcells) if dcells else None)
    pc1 = all(0.0 < arm_scores[a] < 1.0 for a in ARM_NAMES if a != "K") and \
        all(refusal_rates[a] <= PC1_REFUSAL_CAP for a in ARM_NAMES)

    # ---- PC-3: controls ----
    # Denominator = TYPING-ACTIVE divergent cells (K did not refuse):
    # on cells where K maps the sense to NONE, K-shuf refuses identically
    # BY CONSTRUCTION (the shuffle deranges typing content, not coverage),
    # so refusal cells are structurally shuffle-invariant and cannot
    # discriminate any control (ASM-2004 operationalisation).
    div_dd_active = [i for i in div_dd
                     if rows[("K", i)]["verdict"] != "REFUSE"]
    kshuf_diff_cells = [i for i in div_dd_active
                        if sig("K", i) != sig("K-shuf", i)]
    kshuf_frac = (len(kshuf_diff_cells) / len(div_dd_active)
                  if div_dd_active else 0.0)
    # predicted error signature: on cells where K-shuf differs from K,
    # K-shuf shows a false conflict on an attested/G4 cell or a missed
    # anomaly (relative to K's verdict)
    sig_ok = all(
        (rows[("K-shuf", i)]["verdict"] == "ANOMALOUS"
         and rows[("K", i)]["verdict"] != "ANOMALOUS")
        or (rows[("K-shuf", i)]["verdict"] != "ANOMALOUS"
            and rows[("K", i)]["verdict"] == "ANOMALOUS")
        or tuple(rows[("K-shuf", i)]["derived_sides"]) !=
        tuple(rows[("K", i)]["derived_sides"])
        for i in kshuf_diff_cells)
    du_identical_dd = all(sig("D-word-union", i) == sig("D-word-dom", i)
                          for i in ids)
    pc3 = (kshuf_frac >= PC3_MIN_KSHUF_DIFF_FRAC and sig_ok
           and not du_identical_dd)

    # ---- PC-4: gate teeth ----
    # (a) planted mistyped axiom (CF-2-style): flip the range of the FIRST
    # slice-present K-typed sense (deterministic by item-id order) to the
    # opposite-side class; the scorer + divergence must change EXACTLY the
    # predicted cells (all slice items mapping to that sense) and nothing
    # else (ASM-2005 — slice-aware plant selection).
    sense_of = {it["id"]: arm_relation("K", it, minted) for it in sl}
    plant_sense = plant_old = None
    for it in sl:  # id-sorted
        s = sense_of[it["id"]]
        if s is None:
            continue
        rec = json.loads((MODULE / "kernel" /
                          ("sense-%s.json" % s.split(":")[-1])).read_text())
        rng = [c for c in rec["constraints"] if c["kind"] == "range"]
        if rng:
            plant_sense, plant_old = s, rng[0]["target"]
            break
    if plant_sense is None:
        raise RuntimeError("no K-typed sense in the pilot slice (fail closed)")
    flip_to = C["words"] if plant_old in (C["material"], C["person"]) \
        else C["material"]
    mut = OUT / "_pc4_mutated_kernel"
    if mut.exists():
        shutil.rmtree(mut)
    shutil.copytree(MODULE / "kernel", mut)
    mut_file = mut / ("sense-%s.json" % plant_sense.split(":")[-1])
    rec = json.loads(mut_file.read_text())
    for con in rec["constraints"]:
        if con["kind"] == "range":
            con["target"] = flip_to
    mut_file.write_text(json.dumps(rec, indent=1, sort_keys=True) + "\n")
    tb_mut = dict(arm_tbox_paths(HERE / "arms"))
    tb_mut["K"] = [MODULE / "classes", mut]
    rows_mut = decide_all(wn, sl, gold, minted, tb_mut)
    changed = sorted(i for i in ids
                     if rows_mut[("K", i)] != rows[("K", i)])
    predicted = sorted(i for i in ids if sense_of[i] == plant_sense)
    planted_fires = changed == predicted and len(predicted) > 0
    # (b) poisoned-gold canary on the REAL compiler
    poisoned = {k: dict(v, verdict={"CONSISTENT": "ANOMALOUS",
                                    "ANOMALOUS": "CONSISTENT",
                                    "REFUSE": "CONSISTENT"}[v["verdict"]])
                for k, v in gold.items()}
    real_sha_clean = compile_worlds_sha(wn, sl, gold)
    real_sha_poisoned = compile_worlds_sha(wn, sl, poisoned)
    arms_sha = sha256_file(HERE / "arms" / "arm-manifest.json")
    canary_silent_on_real = real_sha_clean == real_sha_poisoned
    # (c) planted gold-reading compiler must TRIP the canary
    leak_clean = planted_gold_reading_compiler_sha(wn, sl, gold)
    leak_poisoned = planted_gold_reading_compiler_sha(wn, sl, poisoned)
    canary_fires_on_leak = leak_clean != leak_poisoned
    # (d) kernel-module provenance (G2-independence): every domain/range
    # target minted under urn:kot-engineinf:
    prov_ok = True
    for p in sorted((MODULE / "kernel").glob("sense-*.json")):
        r = json.loads(p.read_text())
        for con in r["constraints"]:
            if con["kind"] in ("domain", "range") and \
                    not con["target"].startswith("urn:kot-engineinf:cls:"):
                prov_ok = False
    pc4 = planted_fires and canary_silent_on_real and canary_fires_on_leak \
        and prov_ok

    # ---- PC-5: elicitable gold ----
    yield_rate = items_doc["extractor_stats"]["yield_rate"]
    oracle_score = sum(1 for i in ids if rows[("oracle", i)]["correct"]) / len(ids)
    bwn_manifest = json.load(open(HERE / "arms" / "arm-manifest.json"))
    frames_ok = bwn_manifest["bwn_typed_relations"] > 0
    pc5 = yield_rate >= PC5_MIN_YIELD and oracle_score == 1.0 and det_ok \
        and frames_ok

    # ---- artifact (kot-pilot/1) ----
    records_path = OUT / "run-records-instrpilot.jsonl"
    with open(records_path, "w") as f:
        for k in sorted(rows):
            f.write(json.dumps(rows[k], sort_keys=True) + "\n")

    flags = [{"name": "kernel_as_text_na",
              "detail": ("mandatory kernel-as-text control is structurally "
                         "N/A: no LLM/host consumer exists anywhere in the "
                         "instrument — no prompt surface for the text to "
                         "enter (design §1.3/§4.2, ASM-1963); the shuffle + "
                         "source-projection arms carry the "
                         "content-vs-structure burden")}]
    checks = {
        "no_degenerate_arm": {"pass": bool(pc1), "evidence": {
            "arm_scores_slice": arm_scores,
            "arm_scores_divergent_cells_reported": div_scores,
            "refusal_rates_non_g4": refusal_rates,
            "note": ("gate = whole-slice floor 0<score<1 per baseline + "
                     "refusal cap (ASM-2003); K at/near 1.0 is "
                     "certificate-normal and disclosed, not a failure")}},
        "separation_nonvacuous": {"pass": bool(pc2), "evidence": {
            "div_k_dworddom_n": len(div_dd), "div_k_bwn_n": len(div_bwn),
            "ops_spanned": dd_ops, "lemmas_spanned": dd_lemmas,
            "div_k_dworddom_items": div_dd, "div_k_bwn_items": div_bwn,
            "note": ("the non-vacuous-divergence existence proof — the "
                     "anti-knull gate (ASM-1851/1939(a) lineage)")}},
        "controls_nondegenerate": {"pass": bool(pc3), "evidence": {
            "denominator": ("typing-active Div(K,D-word-dom) slice cells "
                            "(K non-refusing) — refusal cells are "
                            "shuffle-invariant by construction (ASM-2004)"),
            "div_cells_active_n": len(div_dd_active),
            "kshuf_differs_frac_of_div_cells": kshuf_frac,
            "kshuf_error_signature_ok": bool(sig_ok),
            "dunion_row_identical_to_ddom": bool(du_identical_dd),
            "replicate_noise": 0.0,
            "note": "deterministic channel => margins are exact (noise 0)"}},
        "gate_teeth": {"pass": bool(pc4), "evidence": {
            "planted_sense": plant_sense,
            "planted_range_flip": [plant_old, flip_to],
            "planted_axiom_flip_changed_items": changed,
            "planted_axiom_flip_predicted_items": predicted,
            "planted_fires_exactly": bool(planted_fires),
            "poisoned_gold_canary_silent_on_real_compiler":
                bool(canary_silent_on_real),
            "arm_modules_sha_unchanged": arms_sha,
            "planted_gold_reading_compiler_trips_canary":
                bool(canary_fires_on_leak),
            "kernel_module_provenance_g2_independent": bool(prov_ok)}},
        "elicitable_gold": {"pass": bool(pc5), "evidence": {
            "extractor_yield_rate": yield_rate,
            "oracle_arm_score": oracle_score,
            "double_run_sha_match": bool(det_ok),
            "bwn_frame_typed_relations":
                bwn_manifest["bwn_typed_relations"]}},
    }
    all_pass = all(c["pass"] for c in checks.values())
    verdict = "PILOT-PASS-WITH-FLAGS" if all_pass else "PILOT-FAIL"

    artifact = {
        "schema_version": "kot-pilot/1",
        "experiment": "engine-inference",
        "mode": "REAL",
        "verdict": verdict,
        "verdict_semantics": "instrument-validity ONLY; never campaign evidence",
        "checks": checks,
        "flags": flags,
        "operating_point": {
            "description": ("certified rules-1 twin engine (Python), 5 arms "
                            "+ oracle, kot-axiom/1 modules, WN31-derived "
                            "deterministic gold, grade-S items; CPU-only, "
                            "$0 model spend"),
            "n_pilot": {"items": len(ids), "decisions": len(rows)},
            "seed": None,
            "pins": {
                "corpus_hashes": {
                    "_recipe": kc.CORPUS_RECIPE,
                    "kernel-v1": kc.corpus_hash(str(ROOT), "kernel-v1"),
                    "lexical-wn31": kc.corpus_hash(str(ROOT), "lexical-wn31"),
                    "axioms-engineinf-v0":
                        kc.corpus_hash(str(ROOT), "axioms-engineinf-v0"),
                },
                "harness_manifest": canon_sha({
                    p.name: sha256_file(p) for p in sorted(HERE.glob("*.py"))
                    if p.name != "instr_pilot.py"}),
            },
        },
        "thresholds_predeclared": {
            "slice_per_group": SLICE_PER_GROUP,
            "pc1_refusal_cap_non_g4": PC1_REFUSAL_CAP,
            "pc2_min_div_dworddom": PC2_MIN_DIV_DWORDDOM,
            "pc2_min_div_bwn": PC2_MIN_DIV_BWN,
            "pc2_min_ops": PC2_MIN_OPS, "pc2_min_lemmas": PC2_MIN_LEMMAS,
            "pc3_min_kshuf_diff_frac": PC3_MIN_KSHUF_DIFF_FRAC,
            "pc5_min_yield": PC5_MIN_YIELD,
            "usd_cap_note": "default $2 cap; planned worst case $0 (CPU)"},
        "runner": {"path": "poc/engine-inference/instr_pilot.py",
                   "sha256": sha256_file(HERE / "instr_pilot.py")},
        "records_file": "run-records-instrpilot.jsonl",
        "records_sha256": sha256_file(records_path),
        "determinism_sha256": det_sha,
        "cost": {"usd_cap": USD_CAP, "worst_case_usd_planned": 0.0},
        "asm_block": "ASM-1950..1967 (design) + ASM-1990..2009 (build)",
        "date": DATE,
        "emitted_by": "writer-4",
    }
    (OUT / "instrpilot-result.json").write_text(
        json.dumps(artifact, indent=1, sort_keys=True) + "\n")
    print(json.dumps({"verdict": verdict,
                      "checks": {k: v["pass"] for k, v in checks.items()},
                      "n_pilot": len(ids),
                      "div_dd": len(div_dd), "div_bwn": len(div_bwn),
                      "kshuf_frac": kshuf_frac,
                      "flags": [f["name"] for f in flags]},
                     indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
