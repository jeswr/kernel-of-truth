#!/usr/bin/env python3
# E2a PURE DIAGNOSTIC (maintainer decision #29 input; NOT an adoption, NOT a
# re-freeze, NOT a confirmatory run): measure whether the O2
# (typed-disjointness) starvation that fired KILL-e1 on the E0 confirmatory
# holdout is RULE-LIMITED (the pinned H2 hard-unanimity anomaly construct is
# too strict) or INVENTORY-LIMITED (the 4-lemma Stage-A inventory cannot
# populate O2 under ANY reasonable third-party construct), using VerbNet 3.3
# selectional restrictions as the alternative construct.
#
# Design anchors:
#   docs/next/design/engine-inference-under-typing.md §2.1 G3 (the E1-named
#   VerbNet upgrade), §2.5 [R1] H2 + H* novel-cell restriction, §2.2 the
#   ASM-2106 cell key; poc/engine-inference/e0-kill-steering-synthesis.md
#   (E2a-first, outcome-blind construct-validity repair); ASM-2140 (the
#   measured KILL-e1 mechanism); ASM-2170.. (this diagnostic's block).
#
# CUSTODY (outcome-blind, $0):
#   - imports ONLY engineinf_wn (the engine-free core) — never the engine or
#     the scorer; asserted mechanically at exit (the extract_holdout.py
#     discipline, ASM-2135).
#   - consumes ONLY item INVENTORIES: holdout/items-h.json (pinned pre-freeze
#     items, no outcomes), results/items.json (the closed exploratory seen
#     frame), holdout/holdout-manifest.json (counts, for cross-check). It
#     never opens gold-h.json, rows.jsonl, orbit-rows.jsonl, run-result.json,
#     or any decision artifact, and computes NO engine verdict anywhere.
#   - every count below is outcome-free in exactly the KILL-e1 sense
#     (ASM-2105): a census of pinned items and cell keys.
#
# Determinism: no wall-clock, no RNG; sorted iteration; fail-closed asserts.

import json
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from engineinf_wn import (WN, LEMMAS, LEMMA_POS, cell_key, cell_key_str,  # noqa: E402
                          kernel_inventory, load_sense_keys, sha256_file,
                          wn_kind_cls)

VN_ZIP = HERE / "verbnet" / "verbnet-vn3.3.zip"
VN_PREFIX = "cu-clear-verbnet-90f85a6/verbnet3.3/"
SIDE_TABLE = HERE / "selrestr-side-table.json"
ITEMS_H = HERE.parent / "holdout" / "items-h.json"
SEEN_ITEMS = HERE.parent / "results" / "items.json"
H_MANIFEST = HERE.parent / "holdout" / "holdout-manifest.json"

FORBIDDEN_INPUTS = ("gold-h.json", "rows.jsonl", "orbit-rows.jsonl",
                    "run-result.json", "divergence-certificate")


def verify_vn_pin():
    man = json.load(open(HERE / "verbnet" / "manifest.json"))
    want = man["files"]["verbnet-vn3.3.zip"]["sha256"]
    got = sha256_file(VN_ZIP)
    if got != want:
        raise RuntimeError("verbnet zip sha256 %s != pinned %s (fail closed)"
                           % (got, want))
    return want


# ========================================================== VerbNet parsing
# Canonical subset only: verbnet3.3/*.xml (stipulated in verbnet/manifest).

def vn_class_files(zf):
    return sorted(n for n in zf.namelist()
                  if n.startswith(VN_PREFIX) and n.endswith(".xml"))


def selrestr_expr(srs):
    """SELRESTRS element -> nested expression:
    {'logic': 'and'|'or', 'kids': [('+'|'-', type) | expr, ...]}"""
    kids = []
    for c in srs:
        if c.tag == "SELRESTR":
            kids.append((c.get("Value"), c.get("type")))
        elif c.tag == "SELRESTRS":
            kids.append(selrestr_expr(c))
    return {"logic": srs.get("logic") or "and", "kids": kids}


def expr_render(e):
    parts = []
    for k in e["kids"]:
        parts.append("%s%s" % k if isinstance(k, tuple)
                     else "(%s)" % expr_render(k))
    return (" %s " % e["logic"]).join(parts) if parts else ""


def entail_side(expr, table, flags):
    """The pinned combination logic (selrestr-side-table.json _readme):
    leaf +type -> table side; leaf -type -> None (3-way top split);
    or-node -> a side iff EVERY kid entails that same side;
    and-node -> the unique side among kids (both sides -> contradiction
    flag, None)."""
    def leaf(v, t):
        if t not in table:
            raise RuntimeError("selrestr type %r missing from the authored "
                               "side table (fail closed)" % t)
        return table[t]["side"] if v == "+" else None

    def rec(e):
        sides = []
        for k in e["kids"]:
            s = leaf(*k) if isinstance(k, tuple) else rec(k)
            sides.append(None if s == "none" else s)
        got = sorted({s for s in sides if s})
        if e["logic"] == "or":
            return got[0] if (len(got) == 1 and all(s for s in sides)
                              and sides) else None
        if len(got) == 2:
            flags.append("contradictory-conjunction:%s" % expr_render(e))
            return None
        return got[0] if got else None

    return rec(expr)


def walk_classes(zf):
    """Yield (class_id, chain) for every VNCLASS/VNSUBCLASS node, where
    chain is the root-to-node list of element nodes."""
    for name in vn_class_files(zf):
        root = ET.fromstring(zf.read(name))

        def rec(el, chain):
            chain = chain + [el]
            yield el.get("ID"), chain
            sub = el.find("SUBCLASSES")
            if sub is not None:
                for s in sub:
                    yield from rec(s, chain)
        yield from rec(root, [])


def chain_roles(chain):
    """THEMROLES resolved along the chain (deepest definition per role)."""
    roles = {}
    for el in chain:
        trs = el.find("THEMROLES")
        if trs is None:
            continue
        for tr in trs:
            roles[tr.get("type")] = selrestr_expr(tr.find("SELRESTRS"))
    return roles


def undergoer_roles(chain):
    """The pinned undergoer-role rule (mapping doc M4): the role(s) of the
    SECOND NP in the frame(s) whose DESCRIPTION primary is exactly
    'NP V NP' (the basic transitive — the shape of the instrument's
    rel(anchor, R, undergoer) worlds), taken from the NEAREST chain node
    that has at least one such frame."""
    for el in reversed(chain):
        frames = el.find("FRAMES")
        if frames is None:
            continue
        found = set()
        for fr in frames:
            if fr.find("DESCRIPTION").get("primary") != "NP V NP":
                continue
            nps = [c.get("value") for c in fr.find("SYNTAX") if c.tag == "NP"]
            if len(nps) >= 2 and nps[1]:
                found.add(nps[1])
        if found:
            return sorted(found)
    return []


def vn_mapping(zf, wn, minted, table):
    """The predefined WN<->VerbNet mapping over the CURRENT inventory:
    minted synset -> matched VN classes -> undergoer role -> restriction ->
    entailed side. Mechanical given the pinned bytes + the authored table."""
    sense_keys = load_sense_keys([l for l in LEMMAS if LEMMA_POS[l] == "v"])
    # measured selrestr-type census over the whole canonical set, asserted
    # against the authored table (fail closed both directions):
    used_types = set()
    matches = {}          # synset -> [class match records]
    unmapped_keys = []    # (class, lemma, key, reason)
    for cid, chain in walk_classes(zf):
        node = chain[-1]
        for tr in (node.find("THEMROLES") or []):
            srs = tr.find("SELRESTRS")
            for sr in srs.iter("SELRESTR"):
                used_types.add(sr.get("type"))
        members = node.find("MEMBERS")
        if members is None:
            continue
        for m in members:
            name, wnattr = m.get("name"), (m.get("wn") or "").strip()
            if name not in LEMMAS or LEMMA_POS.get(name) != "v":
                continue
            if not wnattr:
                unmapped_keys.append([cid, name, "", "empty-wn-attribute"])
                continue
            for key in wnattr.split():
                uncertain = key.startswith("?")
                k = key.lstrip("?")
                mapped = sense_keys.get(k + "::")
                if mapped is None:
                    unmapped_keys.append([cid, name, key, "unmappable-sense-key"])
                    continue
                pos, off = mapped
                syn = "urn:lexical-wn31:%s-%s" % (pos, off)
                if syn not in minted:
                    continue          # excluded/outside senses: not in scope
                if uncertain:
                    unmapped_keys.append([cid, name, key,
                                          "uncertain-?-key-excluded"])
                    continue
                roles = chain_roles(chain)
                und = undergoer_roles(chain)
                flags = []
                sides = []
                for r in und:
                    expr = roles.get(r)
                    s = entail_side(expr, table, flags) if expr else None
                    sides.append({"role": r,
                                  "restriction": expr_render(expr)
                                  if expr else "(role undefined on chain)",
                                  "entailed_side": s})
                got = sorted({s["entailed_side"] for s in sides
                              if s["entailed_side"]})
                matches.setdefault(syn, []).append({
                    "class": cid, "member_key": key,
                    "undergoer_roles": sides, "flags": flags,
                    "class_entailed_side": got[0] if len(got) == 1 else None})
    if used_types != set(table):
        raise RuntimeError("selrestr type census %s != authored table %s "
                           "(fail closed)" %
                           (sorted(used_types), sorted(table)))
    # per-synset required side: defined iff >=1 matched class entails a side
    # and ALL side-entailing classes agree (mapping doc M5)
    required = {}
    for syn in sorted(minted):
        recs = matches.get(syn, [])
        sides = sorted({r["class_entailed_side"] for r in recs
                        if r["class_entailed_side"]})
        if not recs:
            reason = ("vn-verbs-only" if syn.split(":")[-1].startswith("n-")
                      else "no-vn-member-sense-key")
            required[syn] = {"required_side": None, "reason": reason}
        elif not sides:
            required[syn] = {"required_side": None,
                             "reason": "matched-classes-unrestricted-undergoer"}
        elif len(sides) > 1:
            required[syn] = {"required_side": None,
                             "reason": "matched-classes-conflict"}
        else:
            required[syn] = {"required_side": sides[0],
                             "reason": "vn-selectional-restriction"}
    return matches, required, unmapped_keys, sorted(used_types)


# ===================================================== anomaly-cell counting
# All counts below are outcome-free censuses of (synset, side, wn-kind,
# 'anomaly') cell keys — the exact ASM-2106 key the KILL-e1 adequacy count
# uses. No engine verdict is computed or read anywhere.

OPP = {"phys": "abst", "abst": "phys"}


def load_inventories(wn):
    seen = json.load(open(SEEN_ITEMS))["items"]
    hold = json.load(open(ITEMS_H))["items"]
    seen_pairs = {(it["gold_synset"], it["object_noun"]) for it in seen}
    seen_cells = {cell_key_str(cell_key(wn, it)) for it in seen}
    h1 = {}          # minted synset -> {noun: side} (H1 attested objects)
    for it in hold:
        if it["kind"] == "attested":
            h1.setdefault(it["gold_synset"], {}).setdefault(
                it["object_noun"], it["object_side"])
    union_attested = {}   # seen gloss objects UNION H1 objects (the H2 base)
    for it in seen:
        if it["kind"] == "attested":
            union_attested.setdefault(it["gold_synset"], {}).setdefault(
                it["object_noun"], it["object_side"])
    for s, objs in h1.items():
        for n, sd in objs.items():
            union_attested.setdefault(s, {}).setdefault(n, sd)
    return seen, hold, seen_pairs, seen_cells, h1, union_attested


def anomaly_cells(wn, syn, viol_side, donors, attested_of_s, seen_pairs,
                  seen_cells):
    """Construct-agnostic cross-pair census for one synset: donor nouns on
    the violating side, minus nouns attested with the synset itself, minus
    decontaminated seen pairs; returns (items, cells, novel_cells)."""
    items, cells = [], set()
    for noun, side in sorted(donors.items()):
        if side != viol_side or noun in attested_of_s:
            continue
        if (syn, noun) in seen_pairs:
            continue
        ck = cell_key_str((syn, side, wn_kind_cls(wn, noun), "anomaly"))
        items.append({"synset": syn, "noun": noun, "cell": ck,
                      "h_star": ck not in seen_cells})
        cells.add(ck)
    novel = sorted(c for c in cells if c not in seen_cells)
    return items, sorted(cells), novel


def variant_census(wn, minted, required, h1, union_attested, seen_pairs,
                   seen_cells, hard):
    """One construct variant. hard=True: a synset is eligible only if NO
    union-attested object of it lies on the violating side (the exact
    analogue of the H2 unanimity discipline — a hard restriction refuted by
    attested third-party usage cannot be gold). hard=False (defeasible):
    the restriction is a violable default; attested violations are logged
    (they are gold-CONSISTENT attested usage, never anomalies) but do not
    disqualify the synset. Donor pools: primary = H1 objects of OTHER
    minted senses of the SAME lemma (the pinned H2 cross-pair shape);
    secondary = H1 objects of any Stage-A minted synset."""
    def lemma_of(syn):
        return minted[syn].split(":")[-1].split(".")[0]

    out = {"eligible_synsets": [], "ineligible": [],
           "primary": {"items": [], "cells": set(), "novel_cells": set()},
           "secondary": {"items": [], "cells": set(), "novel_cells": set()}}
    all_donors = {}
    for s, objs in h1.items():
        for n, sd in objs.items():
            all_donors.setdefault(n, sd)
    for syn in sorted(minted):
        req = required[syn]["required_side"]
        if req is None:
            out["ineligible"].append([syn, required[syn]["reason"]])
            continue
        viol = OPP[req]
        attested_of_s = set(union_attested.get(syn, {}))
        refuting = sorted(n for n, sd in union_attested.get(syn, {}).items()
                          if sd == viol)
        if hard and refuting:
            out["ineligible"].append(
                [syn, "hard-restriction-refuted-by-attested-usage:%s"
                 % ",".join(refuting)])
            continue
        out["eligible_synsets"].append(
            {"synset": syn, "lemma": lemma_of(syn), "required_side": req,
             "violating_side": viol,
             "attested_violations_logged": refuting})
        lemma = lemma_of(syn)
        prim_donors = {}
        for s2, objs in h1.items():
            if s2 != syn and lemma_of(s2) == lemma:
                for n, sd in objs.items():
                    prim_donors.setdefault(n, sd)
        for pool, donors in (("primary", prim_donors),
                             ("secondary", all_donors)):
            items, cells, novel = anomaly_cells(
                wn, syn, viol, donors, attested_of_s, seen_pairs, seen_cells)
            out[pool]["items"].extend(items)
            out[pool]["cells"].update(cells)
            out[pool]["novel_cells"].update(novel)
    for pool in ("primary", "secondary"):
        p = out[pool]
        lemmas = sorted({minted[i["synset"]].split(":")[-1].split(".")[0]
                         for i in p["items"]})
        novel_lemmas = sorted({minted[i["synset"]].split(":")[-1].split(".")[0]
                               for i in p["items"] if i["h_star"]})
        out[pool] = {"n_items": len(p["items"]),
                     "n_items_novel_cell": sum(1 for i in p["items"]
                                               if i["h_star"]),
                     "n_cells": len(p["cells"]),
                     "cells": sorted(p["cells"]),
                     "n_novel_cells": len(p["novel_cells"]),
                     "novel_cells": sorted(p["novel_cells"]),
                     "lemma_span_cells": lemmas,
                     "lemma_span_novel_cells": novel_lemmas,
                     "items": p["items"]}
    return out


def ceiling_census(wn, minted, h1, union_attested, seen_pairs, seen_cells):
    """Construct-AGNOSTIC headroom [DERIVED, NOT GOLD]: for every minted
    verb synset and EITHER hypothetical violating side, the novel anomaly
    cells reachable from the H1 donor pool — an upper bound on what ANY
    single-side selectional-restriction construct could license on the
    current inventory. A cell here is NOT gold: no third-party source
    licenses most of these restrictions (that is the point of measuring
    the VerbNet-licensed subset separately)."""
    all_donors = {}
    for s, objs in h1.items():
        for n, sd in objs.items():
            all_donors.setdefault(n, sd)
    rows = []
    for syn in sorted(minted):
        if syn.split(":")[-1].startswith("n-"):
            continue
        for viol in ("phys", "abst"):
            attested_of_s = set(union_attested.get(syn, {}))
            items, cells, novel = anomaly_cells(
                wn, syn, viol, all_donors, attested_of_s, seen_pairs,
                seen_cells)
            if novel:
                rows.append({"synset": syn,
                             "sense": minted[syn],
                             "would_require_restriction_side": OPP[viol],
                             "violating_side": viol,
                             "novel_cells": novel,
                             "n_items_in_novel_cells":
                                 sum(1 for i in items if i["h_star"])})
    all_novel = sorted({c for r in rows for c in r["novel_cells"]})
    lemmas = sorted({r["sense"].split(":")[-1].split(".")[0] for r in rows})
    return {"rows": rows, "n_novel_cells_total": len(all_novel),
            "novel_cells_total": all_novel, "lemma_span": lemmas}


def kill_e1_rescore(hold, novel_o2_cells, novel_o2_items, novel_o2_lemmas,
                    thresholds):
    """The KILL-e1 count re-evaluated with a variant's NOVEL O2 cells added
    to the pinned (G1∪G3)_H* frame — same outcome-free op rule as
    extract_holdout.kill_e1 (attested->O1, anomaly->O2)."""
    frame = [it for it in hold if it.get("h_star")
             and it["kind"] in ("attested", "anomaly")]
    cells = {it["cell"] for it in frame}
    lemmas = {it["lemma"] for it in frame}
    ops = {"O1" if it["kind"] == "attested" else "O2" for it in frame}
    n_items = len(frame) + novel_o2_items
    n_cells = len(cells) + novel_o2_cells
    if novel_o2_cells:
        ops.add("O2")
        lemmas.update(novel_o2_lemmas)
    fired = (n_items < thresholds["min_items"]
             or n_cells < thresholds["min_cells"]
             or len(ops) < thresholds["min_ops"]
             or len(lemmas) < thresholds["min_lemmas"])
    return {"n_items": n_items, "n_cells": n_cells,
            "ops_spanned": sorted(ops), "lemmas_spanned": sorted(lemmas),
            "kill_e1_would_fire": fired}


def main():
    # FORBIDDEN_INPUTS documents the custody boundary; enforcement is
    # structural (no read of any such artifact exists in this module).
    vn_sha = verify_vn_pin()
    table = json.load(open(SIDE_TABLE))["types"]
    wn = WN()
    minted, excluded, _ = kernel_inventory()
    zf = zipfile.ZipFile(VN_ZIP)

    matches, required, unmapped, used_types = vn_mapping(zf, wn, minted, table)
    seen, hold, seen_pairs, seen_cells, h1, union_attested = load_inventories(wn)
    hman = json.load(open(H_MANIFEST))
    thresholds = hman["kill_e1"]["thresholds"]

    # cross-check the pinned frame numbers (fail closed on drift)
    frame = [it for it in hold if it.get("h_star")
             and it["kind"] in ("attested", "anomaly")]
    assert len(frame) == hman["kill_e1"]["n_items_g1g3_hstar"], "frame drift"
    assert len({it["cell"] for it in frame}) == \
        hman["kill_e1"]["n_cells_g1g3_hstar"], "cell drift"

    # ---- H2 baseline (the pinned construct's own result, recounted) ----
    h2_items = [it for it in hold if it["kind"] == "anomaly"]
    h2_cells = sorted({it["cell"] for it in h2_items})
    h2 = {"construct": "H2 hard side-unanimity (pinned, ASM-2104)",
          "n_items": len(h2_items),
          "n_cells": len(h2_cells), "cells": h2_cells,
          "n_novel_cells": sum(1 for c in h2_cells if c not in seen_cells),
          "lemma_span_cells": sorted({it["lemma"] for it in h2_items}),
          "unanimity_base_synsets": len(union_attested),
          "unanimous_synsets": sorted(
              s for s, objs in union_attested.items()
              if len(set(objs.values())) == 1),
          "kill_e1_rescore": kill_e1_rescore(hold, 0, 0, [], thresholds)}

    hard = variant_census(wn, minted, required, h1, union_attested,
                          seen_pairs, seen_cells, hard=True)
    defe = variant_census(wn, minted, required, h1, union_attested,
                          seen_pairs, seen_cells, hard=False)
    ceiling = ceiling_census(wn, minted, h1, union_attested, seen_pairs,
                             seen_cells)

    hard["kill_e1_rescore"] = kill_e1_rescore(
        hold, len(hard["primary"]["novel_cells"]),
        hard["primary"]["n_items_novel_cell"],
        hard["primary"]["lemma_span_novel_cells"], thresholds)
    defe["kill_e1_rescore"] = kill_e1_rescore(
        hold, len(defe["primary"]["novel_cells"]),
        defe["primary"]["n_items_novel_cell"],
        defe["primary"]["lemma_span_novel_cells"], thresholds)

    coverage = {
        "minted_synsets_total": len(minted),
        "minted_verb_synsets": sum(1 for s in minted
                                   if not s.split(":")[-1].startswith("n-")),
        "vn_covered_verb_synsets": sorted(matches),
        "n_vn_covered": len(matches),
        "vn_required_side_by_synset": {
            s: dict(required[s], sense=minted[s]) for s in sorted(minted)},
        "unmapped_member_keys": unmapped,
        "selrestr_types_used_in_themroles": used_types,
    }

    mapping_out = {"schema": "kot-e2a-vn-mapping/1",
                   "verbnet_sha256": vn_sha,
                   "canonical_subset": VN_PREFIX,
                   "coverage": coverage,
                   "class_matches": {s: matches[s] for s in sorted(matches)},
                   "emitted_by": "analyst-7", "date": "2026-07-13"}
    (HERE / "vn-mapping.json").write_text(
        json.dumps(mapping_out, indent=1, sort_keys=True) + "\n")

    result = {
        "schema": "kot-e2a-diagnostic/1",
        "role": ("PURE DIAGNOSTIC for maintainer decision #29 — measures "
                 "the O2 rule-vs-inventory question; adopts NOTHING, "
                 "freezes NOTHING, licenses NO feasibility conclusion."),
        "custody": ("Outcome-blind: consumes item inventories only "
                    "(items-h.json, results/items.json, manifest counts); "
                    "no engine/scorer import (asserted at exit); no gold-h/"
                    "rows/run-result read; every number is an outcome-free "
                    "census of pinned items and ASM-2106 cell keys."),
        "pins": {"verbnet_zip_sha256": vn_sha,
                 "side_table_sha256": sha256_file(SIDE_TABLE),
                 "items_h_sha256": sha256_file(ITEMS_H),
                 "seen_items_sha256": sha256_file(SEEN_ITEMS),
                 "script_sha256": sha256_file(HERE / "e2a_verbnet_diagnostic.py"),
                 "engineinf_wn_sha256": sha256_file(HERE.parent / "engineinf_wn.py")},
        "h2_baseline": h2,
        "verbnet_hard": hard,
        "verbnet_defeasible": defe,
        "construct_agnostic_ceiling_NOT_GOLD": ceiling,
        "emitted_by": "analyst-7", "date": "2026-07-13",
    }
    (HERE / "e2a-result.json").write_text(
        json.dumps(result, indent=1, sort_keys=True) + "\n")

    # ---- custody self-check: no engine, no scorer, ever ----
    if "twin_engine" in sys.modules or "engineinf_lib" in sys.modules:
        raise RuntimeError("CUSTODY VIOLATION: engine/scorer module loaded "
                           "inside the E2a diagnostic")

    brief = {
        "h2": {"items": h2["n_items"], "cells": h2["n_cells"],
               "novel_cells": h2["n_novel_cells"],
               "kill_e1_would_fire": h2["kill_e1_rescore"]["kill_e1_would_fire"]},
        "vn_hard": {"eligible_synsets": len(hard["eligible_synsets"]),
                    "items": hard["primary"]["n_items"],
                    "cells": hard["primary"]["n_cells"],
                    "novel_cells": hard["primary"]["n_novel_cells"],
                    "kill_e1_would_fire":
                        hard["kill_e1_rescore"]["kill_e1_would_fire"]},
        "vn_defeasible": {"eligible_synsets": len(defe["eligible_synsets"]),
                          "items_primary": defe["primary"]["n_items"],
                          "cells_primary": defe["primary"]["n_cells"],
                          "novel_cells_primary": defe["primary"]["n_novel_cells"],
                          "items_secondary": defe["secondary"]["n_items"],
                          "novel_cells_secondary":
                              defe["secondary"]["n_novel_cells"],
                          "kill_e1_would_fire":
                              defe["kill_e1_rescore"]["kill_e1_would_fire"]},
        "ceiling_not_gold": {"novel_cells": ceiling["n_novel_cells_total"],
                             "lemma_span": ceiling["lemma_span"]},
        "custody": "no engine/scorer modules loaded",
    }
    print(json.dumps(brief, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
