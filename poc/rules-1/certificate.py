#!/usr/bin/env python3
# RULES-1 — THE INVERTED-DECONF-A1 CERTIFICATE (WMRE-1 C5). CPU, ~$0.
#
# Question (docs/next/arch/world-model-rules-engine.md §4.4, PROPOSED-ASM-1131
# + PROPOSED-ASM-1163; maintainer-approved MD-6/MD-9, issue #19):
#   DECONF-A1 measured C_dec = 1.0 — every runtime decision of the structured
#   engine was reproducible from a flat projection of the store's STATED
#   bytes (machinery inert). This certificate runs the same instrument in
#   REVERSE on the RULES-1 engine: does the engine make decisions on
#   ENTAILED-BUT-NEVER-STATED facts that NO projection of the stated bytes
#   reproduces (C_dec < 1.0 on entailed cells), while staying exact on stated
#   cells (C_dec = 1.0), with the engine correct against third-party gold at
#   Wilson-LB >= 0.98?  KILL-a: Cl(S)\S empty or trivial.
#
# Cells:
#   E3  858 covered nsk1-clutrr items (two-hop, third-party CLUTRR gold
#       predating the kernel — PROPOSED-ASM-1125): entailed answer cell +
#       stated sanity cells + E2 person-typing cells.
#   E5  100 control items (up-edge f_comb outside the axiom inventory):
#       engine must REFUSE (fail-closed scored).
#   E1  2x124 world-v0 cells: held-out gendered-parent edge abstracted to
#       `parent`; engine must recover it via R-COVER-ELIM (policy regime).
#       Gold here is the held-out world-v0 stated edge (kernel-authored, NOT
#       third-party — disclosed; the external-gold soundness bar rests on E3).
#   CF  per-target counterfactual gates (PROPOSED-ASM-1163):
#       CF-1 definition-removal  -> targets disappear (refusal);
#       CF-2 targeted meaning-CHANGING mutation (father/mother chain swap)
#            -> exactly the predicted E3 flips, nothing else;
#       CF-3 meaning-preserving no-op mutation (record order + constraint
#            order permuted) -> byte-identical decisions.
#   DET whole-certificate double run -> identical determinism sha.
#
# GS-B projection operationalisation (disclosed, PROPOSED-ASM emitted in
# RESULT.md): the stated-bytes comparator is the aligned flat lookup over the
# item's stated kot-world/1 records projected onto the query read-set — for a
# relation query (a,b): the lexicon word of any STATED relation record linking
# a->b, else no-answer; for a class query: membership of the STATED class
# record. This mirrors DECONF-A1's GS-A construction (projection of stated
# store bytes onto exactly the checker read-set), inverted: here the ENGINE'S
# decisions are the reference and the projection tries to reproduce them.
#
# Engine identity: the Python differential twin (twin_engine.py) GOVERNS this
# execution per PROPOSED-ASM-1124 fallback (sparq-reason Rust build
# unavailable on this box at execution time — see result JSON
# engine_identity block; conformance cross-check is a named follow-up).
#
# Status: EXPLORATORY (pre-freeze execution), same posture as
# poc/deconf-a1/RESULT.md — deterministic and pin-gated so a registered
# re-run reproduces these bytes for $0. NO feasibility conclusion is stated.

import hashlib
import json
import time
from pathlib import Path

from twin_engine import load_tbox, Closure, EngineError

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent

MOTHER = "urn:kot:bciqdkz3mwjzgrbptwmryvvp5nwg7fuu6crj5e63i5y5cdkq4v2r6mua"
FATHER = "urn:kot:bciqgs7ze663hfdaq7be4jnuuue5nywum6qhdciqgq7greuyyobz6jqi"

TBOX_PINNED = [
    ROOT / "data/axioms-v0/rel-mother.json",
    ROOT / "data/axioms-v0/rel-father.json",
    ROOT / "data/axioms-v0/class-man.json",
    ROOT / "data/axioms-kinship-v1",
]


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def wilson_lb(k, n, z=1.959963984540054):
    if n == 0:
        return 0.0
    ph = k / n
    d = 1 + z * z / n
    c = ph + z * z / (2 * n)
    e = z * ((ph * (1 - ph) / n + z * z / (4 * n * n)) ** 0.5)
    return (c - e) / d


def load_worlds():
    """Group nsk1-clutrr stated records by item id (URN-embedded)."""
    worlds = {}
    for line in (ROOT / "data/nsk1-clutrr/world.jsonl").open():
        r = json.loads(line)
        ent = r["entity"] if r["kind"] == "class" else r["subject"]
        item = ent.split(":")[3].rsplit("-", 1)[0]  # clutrr-cNNNN
        w = worlds.setdefault(item, [])
        if r["kind"] == "class":
            w.append(("cls", r["entity"], r["concept"]))
        else:
            w.append(("rel", r["subject"], r["relation"], r["object"]))
    return worlds


def una(entities):
    ents = sorted(entities)
    return [("diff", a, b) for i, a in enumerate(ents)
            for b in ents[i + 1:]]  # PROPOSED-ASM-1120, item-scoped


def projection_answer(stated, a, b, urn2word):
    """GS-B: flat stated-bytes lookup on the query read-set."""
    words = sorted({urn2word[f[2]] for f in stated
                    if f[0] == "rel" and f[1] == a and f[3] == b
                    and f[2] in urn2word})
    return words[0] if len(words) == 1 else (None if not words else "AMBIG")


def engine_answer(tbox, stated, a, b, vocab):
    cl = Closure(tbox, stated)
    try:
        w, why = cl.query_relation(a, b, vocab)
        return cl, w, why, None
    except EngineError as e:
        return cl, None, None, e.code


def run_pass(tbox_paths, vocab, urn2word, items, worlds, e1_cells,
             collect_proofs=False):
    """One full decision pass. Returns the canonical decision payload."""
    tbox = load_tbox(tbox_paths)
    person = json.load((ROOT / "data/axioms-kinship-v1/manifest.json")
                       .open())["minted_urns"]["person"]
    out = {"e3": [], "e5": [], "e1": [], "stated": [], "e2": []}
    proofs = []
    for it in items:
        iid = it["item_id"]
        stated = worlds.get(iid, []) + una(it["lexicon"].keys())
        if it["hop1"]:
            a = it["hop1"]["subject"]
            b = [u for u in it["lexicon"]
                 if u not in (a, it["hop1_bridge"])][0]
        else:
            # uncovered/control: query pair from the pinned fallback template
            # "How is [A] related to [B]?" (manifest question_path) via the
            # item's closed name lexicon.
            q = it["question"]
            name_a, name_b = q[len("How is "):-1].split(" related to ")
            n2u = {v: k for k, v in it["lexicon"].items()}
            a, b = n2u[name_a], n2u[name_b]
        cl, w, why, err = engine_answer(tbox, stated, a, b, vocab)
        proj = projection_answer(stated, a, b, urn2word)
        if it["stratum"] == "covered":
            out["e3"].append({
                "item": iid, "engine": w, "refusal": err, "proj": proj,
                "gold": it["gold_relation"],
                "target_stated": ("rel", a, vocab.get(w, ""), b)
                                 in set(map(tuple, stated)) if w else None,
                "n_derived": len(cl.derived()),
                "concordant": w == proj})
            if collect_proofs and why and len(proofs) < 3:
                proofs.append({"item": iid, "answer": w, "why": why})
            # stated sanity cells: each stated relation edge, queried back
            for f in stated:
                if f[0] != "rel":
                    continue
                cw = urn2word.get(f[2])
                ew = None
                try:
                    ew, _ = cl.query_relation(f[1], f[3], vocab)
                except EngineError:
                    pass
                out["stated"].append({
                    "item": iid, "engine": ew,
                    "proj": projection_answer(stated, f[1], f[3], urn2word),
                    "gold": cw, "concordant": ew is not None and
                    ew == projection_answer(stated, f[1], f[3], urn2word)})
            # E2 person-typing cells (entailed via domain/range of parent)
            for u in sorted(it["lexicon"]):
                in_cl = ("cls", u, person) in cl.facts()
                in_stated = ("cls", u, person) in set(map(tuple, stated))
                out["e2"].append({"item": iid, "entity": u,
                                  "engine": bool(in_cl),
                                  "proj": bool(in_stated),
                                  "concordant": in_cl == in_stated})
        else:  # control -> E5 refusal stratum
            out["e5"].append({"item": iid, "engine": w, "refusal": err,
                              "proj": proj,
                              "refused": err is not None and w is None})
    # E1 world-v0 cells
    for cell in e1_cells:
        cl, w, why, err = engine_answer(tbox, cell["stated"],
                                        cell["a"], cell["b"], vocab)
        proj = projection_answer(cell["stated"], cell["a"], cell["b"],
                                 urn2word)
        out["e1"].append({"cell": cell["id"], "engine": w, "refusal": err,
                          "proj": proj, "gold": cell["gold"],
                          "concordant": w == proj})
        if collect_proofs and why and len(proofs) < 5:
            proofs.append({"cell": cell["id"], "answer": w, "why": why})
    return out, proofs


def build_e1_cells(parent_urn):
    mo, fa = {}, {}
    for line in (ROOT / "data/world-v0/world.jsonl").open():
        r = json.loads(line)
        if r["kind"] != "relation":
            continue
        if r["relation"] == MOTHER:
            mo[r["subject"]] = r["object"]
        elif r["relation"] == FATHER:
            fa[r["subject"]] = r["object"]
    cells = []
    for c in sorted(set(mo) & set(fa)):
        m, f = mo[c], fa[c]
        if m == f:
            continue
        # held-out FATHER: abstract father edge to parent; recover father.
        cells.append({"id": f"e1-f-{c.split(':')[-1]}", "a": c, "b": f,
                      "gold": "father",
                      "stated": [("rel", c, MOTHER, m),
                                 ("rel", c, parent_urn, f)] + una([c, m, f])})
        # held-out MOTHER: symmetric direction.
        cells.append({"id": f"e1-m-{c.split(':')[-1]}", "a": c, "b": m,
                      "gold": "mother",
                      "stated": [("rel", c, FATHER, f),
                                 ("rel", c, parent_urn, m)] + una([c, m, f])})
    return cells


def canon_sha(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True,
                                     separators=(",", ":"))
                          .encode()).hexdigest()


def main():
    t0 = time.time()
    kin = json.load((ROOT / "data/axioms-kinship-v1/manifest.json").open())
    u = kin["minted_urns"]
    vocab = {"mother": MOTHER, "father": FATHER,
             "grandfather": u["grandfather"], "grandmother": u["grandmother"]}
    urn2word = {v: k for k, v in vocab.items()}
    urn2word[u["parent"]] = "parent"        # projection may see 'parent'
    urn2word[u["grandparent"]] = "grandparent"

    items = [json.loads(x) for x in
             (ROOT / "data/nsk1-clutrr/items.jsonl").open()]
    worlds = load_worlds()
    e1_cells = build_e1_cells(u["parent"])

    # ---- main pass ----
    dec, proofs = run_pass(TBOX_PINNED, vocab, urn2word, items, worlds,
                           e1_cells, collect_proofs=True)
    t_main = time.time() - t0

    # ---- CF-1: definition removal (PROPOSED-ASM-1163 gate i) ----
    no_chains = [p for p in TBOX_PINNED if p.is_file()] + \
        [p for p in sorted((ROOT / "data/axioms-kinship-v1").glob("*.json"))
         if p.name not in ("manifest.json", "chain-grandfather.json",
                           "chain-grandmother.json")]
    cf1_e3, _ = run_pass(no_chains, vocab, urn2word,
                         [i for i in items if i["stratum"] == "covered"],
                         worlds, [])
    no_cover = [p for p in TBOX_PINNED if p.is_file()] + \
        [p for p in sorted((ROOT / "data/axioms-kinship-v1").glob("*.json"))
         if p.name not in ("manifest.json", "cover-parent.json")]
    cf1_e1, _ = run_pass(no_cover, vocab, urn2word, [], worlds, e1_cells)

    # ---- CF-2: targeted meaning-CHANGING mutation (gate ii, changing arm):
    # swap the gendered chains' second hop -> every E3 answer must flip
    # grandfather<->grandmother; stated cells must not move. ----
    mut_dir = HERE / "results" / "_cf2_mutated_tbox"
    mut_dir.mkdir(parents=True, exist_ok=True)
    for p in sorted((ROOT / "data/axioms-kinship-v1").glob("*.json")):
        if p.name == "manifest.json":
            continue
        rec = json.loads(p.read_text())
        if p.name in ("chain-grandfather.json", "chain-grandmother.json"):
            for c in rec["constraints"]:
                if c["kind"] == "propertyChain":
                    c["chain"] = [c["chain"][0],
                                  MOTHER if c["chain"][1] == FATHER
                                  else FATHER]
        (mut_dir / p.name).write_text(json.dumps(rec, sort_keys=True))
    # CF-2a: mutation vs the FULL gender-typed worlds. Prediction: the
    # mutated gendered chains now derive a grandparent gender CONTRADICTING
    # the stated CLUTRR gender record, so every covered decision must flip to
    # the named fail-closed refusal ERR_CONFLICT (CAX-DW) — the definitions
    # measurably bind against the data.
    mut_tbox = [p for p in TBOX_PINNED if p.is_file()] + [mut_dir]
    covered = [i for i in items if i["stratum"] == "covered"]
    cf2a, _ = run_pass(mut_tbox, vocab, urn2word, covered, worlds, [])
    # CF-2b: FULL label-swap mutation — swap BOTH the chain second hop AND
    # the range (Man<->Woman) of the two gendered-chain records, i.e. the
    # 'grandfather' record now denotes the grandmother concept and vice
    # versa. Prediction: every E3 surface answer flips
    # grandfather<->grandmother EXACTLY, with zero conflicts (the swap is
    # internally coherent; only the word->concept binding moved).
    MAN = "urn:kot:bciqkttqo6lnzwz7u72dbbpteqryr76cdyj7glivilcqribbggeqofsy"
    WOMAN = "urn:kot:bciqbz6th7ul3gmk5bhtovyi2yifyv7twotuvwjcebgetthcs532sgoq"
    mutb_dir = HERE / "results" / "_cf2b_labelswap_tbox"
    mutb_dir.mkdir(parents=True, exist_ok=True)
    for p in sorted((ROOT / "data/axioms-kinship-v1").glob("*.json")):
        if p.name == "manifest.json":
            continue
        rec = json.loads(p.read_text())
        if p.name in ("chain-grandfather.json", "chain-grandmother.json"):
            for c in rec["constraints"]:
                if c["kind"] == "propertyChain":
                    c["chain"] = [c["chain"][0],
                                  MOTHER if c["chain"][1] == FATHER
                                  else FATHER]
                elif c["kind"] == "range":
                    c["target"] = WOMAN if c["target"] == MAN else MAN
        (mutb_dir / p.name).write_text(json.dumps(rec, sort_keys=True))
    cf2b, _ = run_pass([p for p in TBOX_PINNED if p.is_file()] + [mutb_dir],
                       vocab, urn2word, covered, worlds, [])

    # ---- CF-3: meaning-PRESERVING no-op mutation (gate ii, preserving arm):
    # reverse record load order + reverse constraint order. ----
    nop_dir = HERE / "results" / "_cf3_nop_tbox"
    nop_dir.mkdir(parents=True, exist_ok=True)
    srcs = [p for p in TBOX_PINNED if p.is_file()] + \
        [p for p in sorted((ROOT / "data/axioms-kinship-v1").glob("*.json"))
         if p.name != "manifest.json"]
    for i, p in enumerate(reversed(srcs)):
        rec = json.loads(p.read_text())
        rec["constraints"] = list(reversed(rec["constraints"]))
        (nop_dir / f"{i:02d}-{p.name}").write_text(
            json.dumps(rec, sort_keys=True))
    cf3, _ = run_pass([nop_dir], vocab, urn2word, items, worlds, e1_cells)

    # ---- determinism: second full main pass ----
    dec2, _ = run_pass(TBOX_PINNED, vocab, urn2word, items, worlds, e1_cells)

    # ================= scoring =================
    e3, e5, e1, st, e2 = (dec["e3"], dec["e5"], dec["e1"], dec["stated"],
                          dec["e2"])
    ent_cells = ([c for c in e3] + [c for c in e1] +
                 [c for c in e2 if not c["proj"]])
    n_ent = len(ent_cells)
    n_ent_repro = sum(1 for c in e3 if c["concordant"]) + \
        sum(1 for c in e1 if c["concordant"]) + \
        sum(1 for c in e2 if not c["proj"] and c["concordant"])
    n_st = len(st)
    n_st_repro = sum(1 for c in st if c["concordant"])
    k_e3 = sum(1 for c in e3 if c["engine"] == c["gold"])
    k_e1 = sum(1 for c in e1 if c["engine"] == c["gold"])
    k_e5 = sum(1 for c in e5 if c["refused"])
    target_stated_violations = sum(1 for c in e3 if c["target_stated"])
    cl_s_nonempty = sum(1 for c in e3 if c["n_derived"] > 0)

    cf1_e3_refuse = sum(1 for c in cf1_e3["e3"]
                        if c["engine"] is None and c["refusal"])
    cf1_e1_refuse = sum(1 for c in cf1_e1["e1"]
                        if c["engine"] is None and c["refusal"])
    flip = {"grandfather": "grandmother", "grandmother": "grandfather"}
    cf2a_conflict = sum(1 for c in cf2a["e3"]
                        if c["engine"] is None and
                        c["refusal"] == "ERR_CONFLICT")
    cf2b_pred = sum(1 for a, b_ in zip(e3, cf2b["e3"])
                    if a["engine"] is not None and
                    b_["engine"] == flip.get(a["engine"]))
    cf3_identical = canon_sha(cf3) == canon_sha(
        {k: dec[k] for k in ("e3", "e5", "e1", "stated", "e2")})
    det_sha1 = canon_sha(dec)
    det_sha2 = canon_sha(dec2)

    wl_e3 = wilson_lb(k_e3, len(e3))
    wl_e5 = wilson_lb(k_e5, len(e5))
    wl_all = wilson_lb(k_e3 + k_e1, len(e3) + len(e1))

    c_dec_entailed = n_ent_repro / n_ent if n_ent else 1.0
    c_dec_stated = n_st_repro / n_st if n_st else 1.0

    success = (c_dec_stated == 1.0 and c_dec_entailed < 1.0 and
               wl_e3 >= 0.98)
    kill_a = (n_ent == 0 or c_dec_entailed == 1.0 or
              target_stated_violations > 0)

    result = {
        "certificate": "rules-1-inverted-deconf-a1",
        "status": ("EXPLORATORY (pre-freeze execution; deterministic + "
                   "pin-gated; a registered re-run reproduces these bytes "
                   "for $0). NO feasibility conclusion is stated here; "
                   "verdicts belong to the maintainer/verdict-gen."),
        "design_refs": ["docs/next/arch/world-model-rules-engine.md §4.4",
                        "PROPOSED-ASM-1131", "PROPOSED-ASM-1163",
                        "PROPOSED-ASM-1120", "PROPOSED-ASM-1121",
                        "PROPOSED-ASM-1124", "PROPOSED-ASM-1160",
                        "PROPOSED-ASM-1162"],
        "engine_identity": {
            "ran": ("BOTH engines (MD-4a as approved): decisions in this "
                    "result computed by the Python differential twin "
                    "(poc/rules-1/twin_engine.py); sparq-reason (Rust, "
                    "primary) built on this box after toolchain install "
                    "and its N3 fixpoint (reason_n3, the rules.n3 "
                    "compilation target) EXACTLY agreed with the twin on "
                    "Cl(S) for all 1207 conformance cases (958 nsk1-clutrr "
                    "items + 248 world-v0 E1 cells + the §3 worked example) "
                    "— see poc/rules-1/results/conformance-result.json"),
            "twin_governs_fallback_used": False,
            "sparq_commit": "0ab87b2a5910fe0c783a73dcc043e93ed39c9f58",
            "disclosure": ("Conformance exercised sparq-reason's N3 fixpoint "
                           "entry point, not its OwlRl materializer; both "
                           "engines consumed the same compiled rule "
                           "artifact (results/rules.n3). The build required "
                           "installing gcc + a minimal rust toolchain on "
                           "this 2-core box (~3 min compile)."),
        },
        "grid": {
            "C_dec_stated": c_dec_stated,
            "C_dec_stated_counts": [n_st_repro, n_st],
            "C_dec_entailed": c_dec_entailed,
            "C_dec_entailed_counts": [n_ent_repro, n_ent],
            "entailed_cell_composition": {
                "e3_two_hop_clutrr": len(e3),
                "e1_cover_elim_world_v0": len(e1),
                "e2_person_typing": sum(1 for c in e2 if not c["proj"])},
        },
        "engine_soundness": {
            "e3_vs_third_party_clutrr_gold": {
                "correct": k_e3, "n": len(e3), "wilson_lb95": wl_e3,
                "bar": 0.98, "meets_bar": wl_e3 >= 0.98},
            "e1_vs_held_out_world_v0_edge": {
                "correct": k_e1, "n": len(e1),
                "wilson_lb95": wilson_lb(k_e1, len(e1)),
                "gold_disclosure": ("kernel-authored world-v0 stated edge, "
                                    "held out by abstraction — NOT third-"
                                    "party gold; disclosed")},
            "combined_answered": {"correct": k_e3 + k_e1,
                                  "n": len(e3) + len(e1),
                                  "wilson_lb95": wl_all},
            "e5_control_refusal": {
                "refused": k_e5, "n": len(e5), "wilson_lb95": wl_e5,
                "refusal_codes": sorted({c["refusal"] for c in e5
                                         if c["refusal"]})},
        },
        "kill_a": {
            "fired": kill_a,
            "rule": ("Cl(S)\\S empty or trivial (PROPOSED-ASM-1131): "
                     "entailed set empty OR projection reproduces all "
                     "entailed decisions OR any E3 target found stated"),
            "cl_minus_s_nonempty_items": [cl_s_nonempty, len(e3)],
            "e3_target_stated_violations": target_stated_violations},
        "counterfactual_gates": {
            "cf1_definition_removal": {
                "e3_refuse_without_gendered_chains":
                    [cf1_e3_refuse, len(cf1_e3["e3"])],
                "e1_refuse_without_covering_axiom":
                    [cf1_e1_refuse, len(cf1_e1["e1"])],
                "pass": (cf1_e3_refuse == len(cf1_e3["e3"]) and
                         cf1_e1_refuse == len(cf1_e1["e1"]))},
            "cf2_targeted_meaning_changing_mutation": {
                "a_full_worlds_conflict_refusals": [cf2a_conflict, len(e3)],
                "a_prediction": ("mutated gendered chains contradict the "
                                 "stated gender records -> every covered "
                                 "decision fail-closes ERR_CONFLICT "
                                 "(CAX-DW); definitions bind against data"),
                "b_full_label_swap_exact_flips": [cf2b_pred, len(e3)],
                "b_prediction": ("chain+range swapped together (coherent "
                                 "relabelling): every E3 surface answer "
                                 "flips grandfather<->grandmother exactly, "
                                 "zero conflicts"),
                "b_conflicts": sum(1 for c in cf2b["e3"]
                                   if c["refusal"] == "ERR_CONFLICT"),
                "pass": (cf2a_conflict == len(e3) and
                         cf2b_pred == len(e3))},
            "cf3_meaning_preserving_noop": {
                "decisions_byte_identical": cf3_identical,
                "pass": cf3_identical}},
        "determinism": {"double_run_sha_match": det_sha1 == det_sha2,
                        "decision_payload_sha256": det_sha1},
        "certificate_result": {
            "SUCCESS_rule": ("C_dec=1.0 stated AND C_dec<1.0 entailed AND "
                             "engine Wilson-LB>=0.98 vs third-party gold "
                             "(PROPOSED-ASM-1131) AND counterfactual gates "
                             "(PROPOSED-ASM-1163)"),
            "success_asm_1131": bool(success),
            "gates_asm_1163_all_pass": bool(
                cf1_e3_refuse == len(cf1_e3["e3"]) and
                cf1_e1_refuse == len(cf1_e1["e1"]) and
                cf2a_conflict == len(e3) and cf2b_pred == len(e3) and
                cf3_identical),
            "kill_a_fired": bool(kill_a)},
        "regime_ledger": {
            "e3_proof_regimes": "owl-rl only (R-SUBP, R-CHAIN, R-DOM/RNG)",
            "e1_proof_regimes": ("policy (R-COVER-ELIM; premises "
                                 "PROPOSED-ASM-1120 UNA + 1121 covering, "
                                 "named in every proof tree)"),
            "horn_def_regime_used": False},
        "sample_proof_trees": proofs,
        "pins": {
            "items_jsonl": sha(ROOT / "data/nsk1-clutrr/items.jsonl"),
            "world_jsonl": sha(ROOT / "data/nsk1-clutrr/world.jsonl"),
            "world_v0_jsonl": sha(ROOT / "data/world-v0/world.jsonl"),
            "twin_engine_py": sha(HERE / "twin_engine.py"),
            "certificate_py": sha(HERE / "certificate.py"),
            "mint_kinship_py": sha(HERE / "mint_kinship.py"),
            "axioms_kinship_manifest":
                sha(ROOT / "data/axioms-kinship-v1/manifest.json"),
            "tbox_records": {str(p.relative_to(ROOT)): sha(p)
                             for p in TBOX_PINNED if p.is_file()},
            "minted_urns": u},
        "timing": {"main_pass_seconds": round(t_main, 3),
                   "total_seconds": round(time.time() - t0, 3),
                   "items": len(items), "e1_cells": len(e1_cells)},
    }
    out = HERE / "results" / "certificate-result.json"
    out.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: result[k] for k in
                      ("grid", "engine_soundness", "kill_a",
                       "counterfactual_gates", "determinism",
                       "certificate_result", "timing")}, indent=1))
    print("->", out)


if __name__ == "__main__":
    main()
