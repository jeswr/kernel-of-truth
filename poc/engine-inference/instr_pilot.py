#!/usr/bin/env python3
# ENGINE-INF mandatory blocking instrument pilot — REVISION-1/2/3 RE-RUN
# (pre-freeze, per docs/next/protocol/blocking-pilot-before-freeze.md
# ASM-1830/1831; ENGINE-INF instantiation design §5 as amended by ASM-2111
# [R1], ASM-2114/2116 [R2], ASM-2120 [R3]; original build
# operationalisations ASM-2003..2005 retained where unamended).
#
# The 2026-07-12 pilot (PILOT-PASS-WITH-FLAGS, ASM-2002) predates the
# revisions and does NOT satisfy the gate: this re-run exercises all 6
# scored arms + oracle + the 960-member C-SHUF orbit, the new canaries,
# and the holdout machinery — on the exploratory frames and decoy lemmas
# ONLY, never on H (ASM-2111).
#
# Checks (mechanical predicates over emitted rows, thresholds pre-declared):
#   PC-1  no_degenerate_arm         every baseline strictly between 0 and 1
#                                   on the slice; refusal rate <= 0.5 on
#                                   non-G4 cells for every arm (ASM-2003)
#   PC-2' separation_nonvacuous     |Div(K,D-word-dom)| >= 6 and
#                                   |Div(K,B-wn)| >= 3 on the slice,
#                                   spanning >= 2 ops and >= 2 lemmas, PLUS
#                                   the EP-A existence check:
#                                   |Div_dec(K,K-lemma-x) ∩ (G1∪G3)| >= 3 on
#                                   the FULL exploratory frame for at least
#                                   one x (ASM-2111) — the anti-knull gate
#   PC-3' control_orbit             the FULL within-lemma permutation orbit
#                                   compiles; |Orbit| = 960 = the
#                                   build-derived factorial product;
#                                   identity reproduces K; >= 1 member
#                                   byte-differs; the orbit-invariant
#                                   A_union frame is computed and VERIFIED
#                                   invariant under a relabeled enumeration
#                                   (group-composition check); the
#                                   calibrated p over A_union is computable
#                                   end-to-end on the pilot slice; D-union
#                                   not row-identical to D-dom (ASM-2114/
#                                   2120)
#   PC-4' gate_teeth                planted mistyped axiom fires on exactly
#                                   the predicted cells; poisoned-gold
#                                   canary over the world compiler AND the
#                                   arm-module compilers (incl. K-lemma +
#                                   orbit); a planted gold-reading compiler
#                                   trips the canary; kernel-module
#                                   provenance (G2-independence); the
#                                   SENSE-TAG INSENSITIVITY canary: a
#                                   perturbed gold sense tag leaves K-lemma
#                                   and D-word compiled payloads
#                                   byte-identical AND changes the K / B-wn
#                                   relation on every remapped item
#   PC-5  elicitable_gold           extractor yield >= 0.95; oracle arm
#                                   scores 1.0 through the pinned scorer;
#                                   double-run determinism; B-wn frames
#   PC-6  holdout_machinery_decoys  the SemCor pipeline (pin -> sense-key
#                                   mapping -> extraction -> gold ->
#                                   compile -> engine -> score) end-to-end
#                                   on the three decoy lemmas (draw, hold,
#                                   cut — verified in neither Stage-A nor
#                                   the kernel-v0 panel); outcomes
#                                   quarantined to results/decoy/
#   PC-7  holdout_custody           no H item id in any results artifact;
#                                   items-H + gold-H pinned with no rows;
#                                   the runner's refuse-if-H-rows-exist and
#                                   refuse-without-freeze-marker assertions
#                                   DEMONSTRATED (planted fake H row ->
#                                   refusal; --holdout pre-freeze ->
#                                   refusal); the KILL-e1 adequacy count
#                                   reported from items-H + gold-H alone
#
# Kernel-as-text control: structurally N/A (no prompt surface exists in the
# instrument) -> recorded per protocol §2, downgrading the best verdict to
# PILOT-PASS-WITH-FLAGS. Never a silent pass.

import json
import shutil
import subprocess
import sys
from pathlib import Path

from engineinf_lib import (ARM_NAMES, WN, OrbitEvaluator, arm_relation,
                           arm_tbox_paths, bwn_frame_records,
                           build_klemma_arms, canon_sha, cell_key,
                           cell_key_str, derived_sides, kernel_inventory,
                           load_tbox, neutral_world, orbit_members,
                           orbit_semantic_sha, orbit_sense_records,
                           run_item, score, sha256_file,
                           _kernel_sense_records, lemma_sense_urns,
                           TBox, MODULE, ROOT, C, LEMMAS, DECOY_LEMMAS)

HERE = Path(__file__).resolve().parent
OUT = HERE / "results"
HOLDOUT = HERE / "holdout"
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
PC2_MIN_EPA_DIV_ITEMS = 3    # ASM-2111 EP-A existence, full exploratory frame
ORBIT_EXPECTED = 960         # ASM-2114
PC5_MIN_YIELD = 0.95
USD_CAP = 2.0
DATE = "2026-07-13T00:00:00Z"   # fixed (deterministic artifact bytes)


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


def arm_payload_sha(wn, slice_items, minted, arm):
    """The full per-arm compiled input payload (relation URN substituted
    into the shared neutral world) — the object the sense-tag insensitivity
    canary compares (PC-4' [R1])."""
    payload = []
    for it in slice_items:
        w = neutral_world(wn, it)
        rel = arm_relation(arm, it, minted)
        stated = [list(f[:2]) + [rel] + list(f[3:]) if f[2] == "@REL@"
                  else list(f) for f in w["stated"]]
        payload.append({"item": it["id"], "relation": rel, "stated": stated})
    return canon_sha(payload)


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


def module_dir_sha(d):
    return canon_sha({p.name: sha256_file(p) for p in sorted(d.rglob("*.json"))})


def main():
    wn = WN()
    minted, excluded, _ = kernel_inventory()
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

    # ---- PC-2': divergence on the slice + EP-A existence on the full frame
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
    # EP-A existence (ASM-2111): decision-level Div(K, K-lemma-x) on the
    # FULL exploratory frame, G1∪G3 items, >= 3 for at least one x — if K's
    # own collapses cannot diverge from K even exploratorily, EP-A is
    # stillborn and the redesign stops pre-freeze at $0.
    g1g3_items = [it for it in items
                  if gold[it["id"]]["gold_rule"] in ("G1+G2", "G3")]
    full_rows = decide_all(wn, g1g3_items, gold, minted,
                           arm_tbox_paths(HERE / "arms"))
    epa_div = {}
    for x in ("K-lemma-dom", "K-lemma-union"):
        epa_div[x] = [it["id"] for it in g1g3_items
                      if (full_rows[("K", it["id"])]["verdict"],
                          full_rows[("K", it["id"])]["refusal"]) !=
                         (full_rows[(x, it["id"])]["verdict"],
                          full_rows[(x, it["id"])]["refusal"])]
    pc2 = (len(div_dd) >= PC2_MIN_DIV_DWORDDOM
           and len(div_bwn) >= PC2_MIN_DIV_BWN
           and len(dd_ops) >= PC2_MIN_OPS and len(dd_lemmas) >= PC2_MIN_LEMMAS
           and max(len(v) for v in epa_div.values()) >= PC2_MIN_EPA_DIV_ITEMS)

    # ---- PC-1: arm degeneracy (ASM-2003: whole-slice floor; K exempt) ----
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

    # ---- PC-3': the C-SHUF orbit (ASM-2114 mechanics, ASM-2120 frame) ----
    import math
    inv = lemma_sense_urns()
    members = orbit_members()
    expect = 1
    for l in sorted(inv):
        expect *= math.factorial(len(inv[l]))
    senses = _kernel_sense_records()
    member_shas = [orbit_semantic_sha(orbit_sense_records(m, senses, inv))
                   for m in members]
    pinned_sha = orbit_semantic_sha(
        [{"subject": u, "constraints": senses[u]["constraints"]}
         for u in sorted(senses)])
    identity_ok = member_shas[0] == pinned_sha
    some_differ = any(s != pinned_sha for s in member_shas)

    # orbit evaluation on the pilot-slice G1∪G3 cells
    slice_cells = {}
    for it in sl:
        if gold[it["id"]]["gold_rule"] not in ("G1+G2", "G3"):
            continue
        ck = cell_key_str(cell_key(wn, it))
        slice_cells.setdefault(ck, {"cell": ck, "rep": it,
                                    "gold_verdict": gold[it["id"]]["verdict"]})
    cell_list = [slice_cells[k] for k in sorted(slice_cells)]
    ev = OrbitEvaluator(wn, minted)
    per_member = ev.eval_cells(cell_list)

    def active(m):
        return {c for c, r in per_member[m].items()
                if r["derived_sides"] or r["verdict"] == "ANOMALOUS"}

    a_union = sorted(set().union(*[active(m) for m in per_member]))
    # invariance under a relabeled enumeration (group composition with a
    # fixed non-identity element): {pi ∘ sigma} must BE the orbit, and the
    # union over that relabeled enumeration must be the identical cell set
    perm_index = {canon_sha({l: list(m[l]) for l in sorted(m)}): i
                  for i, m in enumerate(members)}
    sigma = members[1]
    composed_ok = True
    a_union_relabeled = set()
    for m in members:
        comp = {l: tuple(m[l][sigma[l][i]] for i in range(len(m[l])))
                for l in m}
        j = perm_index.get(canon_sha({l: list(comp[l]) for l in sorted(comp)}))
        if j is None:
            composed_ok = False
            break
        a_union_relabeled |= active(j)
    invariance_ok = composed_ok and sorted(a_union_relabeled) == a_union
    # calibrated p end-to-end on the slice frame (mechanics check only —
    # pilot rows are never campaign evidence, ASM-1835)
    gold_of = {c["cell"]: c["gold_verdict"] for c in cell_list}
    if a_union:
        t = {m: sum(1 for c in a_union
                    if per_member[m][c]["verdict"] == gold_of[c]) / len(a_union)
             for m in per_member}
        pilot_p = sum(1 for m in t if t[m] >= t[0]) / len(t)
        p_computable = True
    else:
        pilot_p, p_computable = None, False
    du_identical_dd = all(sig("D-word-union", i) == sig("D-word-dom", i)
                          for i in ids)
    pc3 = (len(members) == ORBIT_EXPECTED == expect and identity_ok
           and some_differ and invariance_ok and p_computable
           and not du_identical_dd)

    # ---- PC-4': gate teeth ----
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
    # (b) poisoned-gold canary on the REAL compilers: the world compiler AND
    # every arm-module compiler (incl. the new K-lemma collapse compiler and
    # the orbit record generator) must be byte-invariant under a poisoned
    # gold.json ON DISK (none of them may read it — ASM-1957/2111)
    poisoned = {k: dict(v, verdict={"CONSISTENT": "ANOMALOUS",
                                    "ANOMALOUS": "CONSISTENT",
                                    "REFUSE": "CONSISTENT"}[v["verdict"]])
                for k, v in gold.items()}
    real_sha_clean = compile_worlds_sha(wn, sl, gold)
    real_sha_poisoned = compile_worlds_sha(wn, sl, poisoned)
    arms_sha = sha256_file(HERE / "arms" / "arm-manifest.json")
    gold_path = OUT / "gold.json"
    gold_bytes = gold_path.read_bytes()
    tmp_a, tmp_b = OUT / "_pc4_arms_clean", OUT / "_pc4_arms_poisoned"
    for d in (tmp_a, tmp_b):
        if d.exists():
            shutil.rmtree(d)
    try:
        build_klemma_arms(wn, tmp_a)
        orbit_sha_clean = canon_sha(member_shas)
        gold_path.write_bytes(json.dumps(
            {"schema": "kot-engineinf-gold/1", "gold": poisoned},
            indent=1, sort_keys=True).encode())
        build_klemma_arms(wn, tmp_b)
        orbit_sha_poisoned = canon_sha(
            [orbit_semantic_sha(orbit_sense_records(m, senses, inv))
             for m in members])
    finally:
        gold_path.write_bytes(gold_bytes)
    module_canary_silent = (module_dir_sha(tmp_a) == module_dir_sha(tmp_b)
                            and orbit_sha_clean == orbit_sha_poisoned)
    shutil.rmtree(tmp_a)
    shutil.rmtree(tmp_b)
    canary_silent_on_real = real_sha_clean == real_sha_poisoned
    # (c) planted gold-reading compiler must TRIP the canary
    leak_clean = planted_gold_reading_compiler_sha(wn, sl, gold)
    leak_poisoned = planted_gold_reading_compiler_sha(wn, sl, poisoned)
    canary_fires_on_leak = leak_clean != leak_poisoned
    # (d) kernel-module provenance (G2-independence): every domain/range
    # target minted under urn:kot-engineinf: — checked on the pinned kernel
    # module AND the compiled K-lemma modules
    prov_ok = True
    for d in (MODULE / "kernel", HERE / "arms" / "klemma-dom",
              HERE / "arms" / "klemma-union"):
        for p in sorted(d.glob("*.json")):
            r = json.loads(p.read_text())
            for con in r["constraints"]:
                if con["kind"] in ("domain", "range") and \
                        not con["target"].startswith("urn:kot-engineinf:cls:"):
                    prov_ok = False
    # (e) sense-tag insensitivity canary (ASM-2101/2111 [R1]): remap every
    # slice item's gold sense tag to the nearest cyclically-next synset in
    # the lemma's sorted minted∪excluded synset list WHOSE K-ROUTING TARGET
    # (minted sense URN or NONE) differs — a remap onto a sibling synset of
    # the same concept, or excluded->excluded, would leave K's projection
    # legitimately unchanged and test nothing. Per-lemma arms must be
    # payload-byte-identical; K and B-wn must change on every remapped item.
    lemma_synsets = {}
    for s, sense in minted.items():
        lemma_synsets.setdefault(sense.split(":")[-1].split(".")[0],
                                 set()).add(s)
    for s, lem in excluded.items():
        lemma_synsets.setdefault(lem, set()).add(s)
    remapped = []
    for it in sl:
        pool = sorted(lemma_synsets[it["lemma"]])
        i0 = pool.index(it["gold_synset"])
        target0 = minted.get(it["gold_synset"])
        j = next((i0 + k) % len(pool) for k in range(1, len(pool) + 1)
                 if minted.get(pool[(i0 + k) % len(pool)]) != target0)
        it2 = dict(it, gold_synset=pool[j])
        remapped.append(it2)
    tag_insensitive_ok = all(
        arm_payload_sha(wn, sl, minted, a) == arm_payload_sha(wn, remapped,
                                                              minted, a)
        for a in ("K-lemma-dom", "K-lemma-union", "D-word-dom",
                  "D-word-union"))
    tag_routed_ok = all(
        arm_relation(a, it, minted) != arm_relation(a, it2, minted)
        for it, it2 in zip(sl, remapped) for a in ("K", "B-wn"))
    pc4 = (planted_fires and canary_silent_on_real and module_canary_silent
           and canary_fires_on_leak and prov_ok and tag_insensitive_ok
           and tag_routed_ok)

    # ---- PC-5: elicitable gold ----
    yield_rate = items_doc["extractor_stats"]["yield_rate"]
    oracle_score = sum(1 for i in ids if rows[("oracle", i)]["correct"]) / len(ids)
    bwn_manifest = json.load(open(HERE / "arms" / "arm-manifest.json"))
    frames_ok = bwn_manifest["bwn_typed_relations"] > 0
    pc5 = yield_rate >= PC5_MIN_YIELD and oracle_score == 1.0 and det_ok \
        and frames_ok

    # ---- PC-6: holdout machinery on decoys (ASM-2111) ----
    decoy_doc = json.load(open(HOLDOUT / "decoy-items.json"))
    d_items, d_gold = decoy_doc["items"], decoy_doc["gold"]
    kv0 = json.load(open(ROOT / "data/kernel-v0/manifest.json"))
    panel_labels = {c["label"] for c in kv0["concepts"]}
    decoys_clean = all(l not in LEMMAS and l not in panel_labels
                       for l in DECOY_LEMMAS)
    decoy_synsets = sorted({it["gold_synset"] for it in d_items})
    dtbox = TBox()
    for r in [json.loads(p.read_text())
              for p in sorted((MODULE / "classes").glob("*.json"))]:
        dtbox.load_record(r, "decoy-classes")
    for r in bwn_frame_records(wn, decoy_synsets):
        dtbox.load_record(r, "decoy-bwn")
    decoy_dir = OUT / "decoy"
    decoy_dir.mkdir(exist_ok=True)
    d_rows = []
    for it in d_items:
        world = neutral_world(wn, it)
        # B-wn-style relation (mechanical, kernel-free) — the decoy pipeline
        # exercises compile+engine+score on real SemCor-derived items
        rel = "urn:kot-engineinf:bwn:%s" % it["gold_synset"].split(":")[-1]
        v, r, d = run_item(dtbox, world, rel)
        corr, pen = score(d_gold[it["id"]], v, d)
        # the K arm on a decoy is the fail-closed path (no minted sense)
        kv, kr, kd = run_item(dtbox, world, None)
        d_rows.append({"item": it["id"], "kind": it["kind"],
                       "lemma": it["lemma"], "verdict": v, "refusal": r,
                       "derived_sides": derived_sides(d),
                       "correct": bool(corr), "honesty_penalty": pen,
                       "k_fail_closed_verdict": kv})
    with open(decoy_dir / "decoy-rows.jsonl", "w") as f:
        for r in d_rows:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    decoy_lemma_cov = sorted({r["lemma"] for r in d_rows})
    k_fail_closed_ok = all(r["k_fail_closed_verdict"] == "REFUSE"
                           for r in d_rows)
    pc6 = (decoys_clean and len(d_rows) > 0
           and len(decoy_lemma_cov) == len(DECOY_LEMMAS)
           and k_fail_closed_ok
           and len(decoy_doc["exclusions"]) > 0)   # reasons logged

    # ---- PC-7: holdout custody (ASM-2104/2111) ----
    items_h_p = HOLDOUT / "items-h.json"
    gold_h_p = HOLDOUT / "gold-h.json"
    man_h = json.load(open(HOLDOUT / "holdout-manifest.json"))
    pins_ok = (items_h_p.is_file() and gold_h_p.is_file()
               and man_h["pins"]["items-h.json"] == sha256_file(items_h_p)
               and man_h["pins"]["gold-h.json"] == sha256_file(gold_h_p))
    hids = sorted({it["id"] for it in json.load(open(items_h_p))["items"]})
    # (i) repo scan: no H id in any results artifact
    contamination = []
    for p in sorted(OUT.rglob("*")):
        if not p.is_file() or p.suffix not in (".json", ".jsonl") \
                or p.name == "instrpilot-result.json":
            continue
        text = p.read_text(errors="replace")
        for iid in hids:
            if '"%s"' % iid in text:
                contamination.append({"file": p.name, "item": iid})
                break
    scan_clean = not contamination
    # (ii) planted fake H row -> the runner must refuse (exit 3), in BOTH
    # the default and the --holdout mode; (iii) --holdout without the
    # freeze marker must refuse (exit 4)
    plant = OUT / "rows-h.jsonl"
    runner = str(HERE / "engineinf_runner.py")
    try:
        plant.write_text(json.dumps({"item": hids[0], "arm": "K",
                                     "verdict": "PLANTED"}) + "\n")
        r_default = subprocess.run([sys.executable, runner, "--dry-plan"],
                                   capture_output=True, text=True)
        r_holdout = subprocess.run([sys.executable, runner, "--holdout"],
                                   capture_output=True, text=True)
    finally:
        if plant.exists():
            plant.unlink()
    r_nofreeze = subprocess.run([sys.executable, runner, "--holdout"],
                                capture_output=True, text=True)
    refuse_on_planted_row = (r_default.returncode == 3
                             and r_holdout.returncode == 3)
    refuse_without_freeze_marker = (r_nofreeze.returncode == 4
                                    and "freeze marker" in r_nofreeze.stderr)
    # (iv) KILL-e1 adequacy count from pinned items-H + gold-H alone (a
    # COUNT, never a scoring — ASM-2105); recomputed here independently of
    # the extractor's own record and cross-checked against it
    hitems = json.load(open(items_h_p))["items"]
    hgold = json.load(open(gold_h_p))["gold"]
    hframe = [it for it in hitems if it["h_star"]
              and hgold[it["id"]]["gold_rule"] in ("G1+G2", "G3")]
    hcells = sorted({it["cell"] for it in hframe})
    hops = sorted({"O1" if it["kind"] == "attested" else "O2"
                   for it in hframe})
    hlemmas = sorted({it["lemma"] for it in hframe})
    kill_e1 = {"n_items": len(hframe), "n_cells": len(hcells),
               "ops_spanned": hops, "lemmas_spanned": hlemmas,
               "fired": (len(hframe) < 30 or len(hcells) < 12
                         or len(hops) < 2 or len(hlemmas) < 2),
               "matches_extractor_record":
                   (len(hframe) == man_h["kill_e1"]["n_items_g1g3_hstar"]
                    and len(hcells) == man_h["kill_e1"]["n_cells_g1g3_hstar"])}
    pc7 = (pins_ok and scan_clean and refuse_on_planted_row
           and refuse_without_freeze_marker
           and kill_e1["matches_extractor_record"])
    # NOTE: PC-7 verifies CUSTODY; the KILL-e1 COUNT itself is a freeze
    # gate, not a pilot gate — it is REPORTED here and blocks the freeze
    # independently if fired (ASM-2105).

    # ---- artifact (kot-pilot/1) ----
    records_path = OUT / "run-records-instrpilot.jsonl"
    with open(records_path, "w") as f:
        for k in sorted(rows):
            f.write(json.dumps(rows[k], sort_keys=True) + "\n")

    flags = [{"name": "kernel_as_text_na",
              "detail": ("mandatory kernel-as-text control is structurally "
                         "N/A: no LLM/host consumer exists anywhere in the "
                         "instrument — no prompt surface for the text to "
                         "enter (design §1.3/§4.2, ASM-1963); the matched "
                         "K-lemma pair + the permutation orbit carry the "
                         "content-vs-structure burden")}]
    if kill_e1["fired"]:
        flags.append({"name": "kill_e1_fired_pre_freeze",
                      "detail": ("the pinned holdout's binding frame "
                                 "(G1∪G3)_H* spans ops %s (< 2): the H2 "
                                 "cross-pair leg yields no NOVEL anomaly "
                                 "cell under the pre-registered unanimity "
                                 "rule on real SemCor objects. Per ASM-2105 "
                                 "the freeze DOES NOT PROCEED; inventory/"
                                 "construction extension first. This is a "
                                 "freeze-gate fact reported via the pilot, "
                                 "not a pilot-validity failure."
                                 % (kill_e1["ops_spanned"],))})
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
            "epa_existence_div_dec_g1g3_full_frame":
                {x: len(v) for x, v in epa_div.items()},
            "note": ("the non-vacuous-divergence existence proof — the "
                     "anti-knull gate (ASM-1851/1939(a) lineage); PC-2' "
                     "adds the ASM-2111 EP-A existence check")}},
        "control_orbit_nondegenerate": {"pass": bool(pc3), "evidence": {
            "orbit_members": len(members),
            "expected_factorial_product": expect,
            "identity_reproduces_k": bool(identity_ok),
            "some_member_differs": bool(some_differ),
            "a_union_slice_cells": a_union,
            "a_union_invariant_under_relabeled_enumeration":
                bool(invariance_ok),
            "calibrated_p_computable": bool(p_computable),
            "pilot_slice_orbit_p_mechanics_only": pilot_p,
            "dunion_row_identical_to_ddom": bool(du_identical_dd),
            "note": ("ASM-2114 orbit + ASM-2120 A_union; the pilot p is "
                     "mechanics validation on the slice, never campaign "
                     "evidence (ASM-1835); the retired single-rotation "
                     "check is superseded")}},
        "gate_teeth": {"pass": bool(pc4), "evidence": {
            "planted_sense": plant_sense,
            "planted_range_flip": [plant_old, flip_to],
            "planted_axiom_flip_changed_items": changed,
            "planted_axiom_flip_predicted_items": predicted,
            "planted_fires_exactly": bool(planted_fires),
            "poisoned_gold_canary_silent_on_real_compiler":
                bool(canary_silent_on_real),
            "poisoned_gold_canary_silent_on_arm_module_compilers":
                bool(module_canary_silent),
            "arm_modules_sha_unchanged": arms_sha,
            "planted_gold_reading_compiler_trips_canary":
                bool(canary_fires_on_leak),
            "kernel_and_klemma_provenance_g2_independent": bool(prov_ok),
            "sense_tag_canary_lemma_arms_payload_invariant":
                bool(tag_insensitive_ok),
            "sense_tag_canary_k_bwn_relations_change":
                bool(tag_routed_ok)}},
        "elicitable_gold": {"pass": bool(pc5), "evidence": {
            "extractor_yield_rate": yield_rate,
            "oracle_arm_score": oracle_score,
            "double_run_sha_match": bool(det_ok),
            "bwn_frame_typed_relations":
                bwn_manifest["bwn_typed_relations"]}},
        "holdout_machinery_decoys": {"pass": bool(pc6), "evidence": {
            "decoy_lemmas": list(DECOY_LEMMAS),
            "decoys_outside_stage_a_and_kernel_v0_panel": bool(decoys_clean),
            "decoy_items_run": len(d_rows),
            "decoy_lemma_coverage": decoy_lemma_cov,
            "decoy_exclusions_logged": len(decoy_doc["exclusions"]),
            "k_fail_closed_on_all_decoys": bool(k_fail_closed_ok),
            "quarantine": "results/decoy/decoy-rows.jsonl (endpoint-inert)"}},
        "holdout_custody": {"pass": bool(pc7), "evidence": {
            "items_h_gold_h_pinned": bool(pins_ok),
            "items_h_sha256": man_h["pins"]["items-h.json"],
            "gold_h_sha256": man_h["pins"]["gold-h.json"],
            "results_scan_clean_of_h_ids": bool(scan_clean),
            "contamination": contamination,
            "runner_refuses_on_planted_h_row": bool(refuse_on_planted_row),
            "runner_refuses_without_freeze_marker":
                bool(refuse_without_freeze_marker),
            "kill_e1_count": kill_e1,
            "note": ("KILL-e1 is a freeze gate reported through the pilot: "
                     "custody PASSES here even when the count fires — the "
                     "firing blocks the FREEZE, per ASM-2105")}},
    }
    all_pass = all(c["pass"] for c in checks.values())
    verdict = "PILOT-PASS-WITH-FLAGS" if all_pass else "PILOT-FAIL"

    artifact = {
        "schema_version": "kot-pilot/1",
        "experiment": "engine-inference",
        "mode": "REAL",
        "verdict": verdict,
        "verdict_semantics": "instrument-validity ONLY; never campaign evidence",
        "revision": "R1/R2/R3 re-run (ASM-2111; supersedes the 2026-07-12 "
                    "pilot ASM-2002 for freeze purposes)",
        "checks": checks,
        "flags": flags,
        "operating_point": {
            "description": ("certified rules-1 twin engine (Python), 6 "
                            "scored arms + oracle + 960-member C-SHUF "
                            "orbit, kot-axiom/1 modules, WN31+SemCor-"
                            "derived deterministic gold, grade-S items; "
                            "CPU-only, $0 model spend"),
            "n_pilot": {"items": len(ids), "decisions": len(rows)},
            "seed": None,
            "pins": {
                "corpus_hashes": {
                    "_recipe": kc.CORPUS_RECIPE,
                    "kernel-v1": kc.corpus_hash(str(ROOT), "kernel-v1"),
                    "lexical-wn31": kc.corpus_hash(str(ROOT), "lexical-wn31"),
                    "axioms-engineinf-v0":
                        kc.corpus_hash(str(ROOT), "axioms-engineinf-v0"),
                    "semcor30": kc.corpus_hash(str(ROOT), "semcor30"),
                },
                "harness_manifest": canon_sha({
                    p.name: sha256_file(p) for p in sorted(HERE.glob("*.py"))
                    if p.name != "instr_pilot.py"}),
                "holdout_manifest": sha256_file(HOLDOUT /
                                                "holdout-manifest.json"),
                "orbit_manifest": sha256_file(HERE / "arms" /
                                              "orbit-manifest.json"),
            },
        },
        "thresholds_predeclared": {
            "slice_per_group": SLICE_PER_GROUP,
            "pc1_refusal_cap_non_g4": PC1_REFUSAL_CAP,
            "pc2_min_div_dworddom": PC2_MIN_DIV_DWORDDOM,
            "pc2_min_div_bwn": PC2_MIN_DIV_BWN,
            "pc2_min_ops": PC2_MIN_OPS, "pc2_min_lemmas": PC2_MIN_LEMMAS,
            "pc2_min_epa_div_items_full_frame": PC2_MIN_EPA_DIV_ITEMS,
            "pc3_orbit_expected": ORBIT_EXPECTED,
            "pc5_min_yield": PC5_MIN_YIELD,
            "usd_cap_note": "default $2 cap; planned worst case $0 (CPU)"},
        "runner": {"path": "poc/engine-inference/instr_pilot.py",
                   "sha256": sha256_file(HERE / "instr_pilot.py")},
        "records_file": "run-records-instrpilot.jsonl",
        "records_sha256": sha256_file(records_path),
        "determinism_sha256": det_sha,
        "cost": {"usd_cap": USD_CAP, "worst_case_usd_planned": 0.0},
        "asm_block": ("ASM-1950..1967 (design) + ASM-1990..2009 (build) + "
                      "ASM-2100..2112 (R1) + ASM-2113..2117 (R2) + "
                      "ASM-2120..2121 (R3)"),
        "date": DATE,
        "emitted_by": "writer-5",
    }
    (OUT / "instrpilot-result.json").write_text(
        json.dumps(artifact, indent=1, sort_keys=True) + "\n")
    print(json.dumps({"verdict": verdict,
                      "checks": {k: v["pass"] for k, v in checks.items()},
                      "n_pilot": len(ids),
                      "div_dd": len(div_dd), "div_bwn": len(div_bwn),
                      "epa_existence": {x: len(v) for x, v in epa_div.items()},
                      "orbit_slice_p": pilot_p,
                      "kill_e1": kill_e1,
                      "flags": [f["name"] for f in flags]},
                     indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
