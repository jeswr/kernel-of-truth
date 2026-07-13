#!/usr/bin/env python3
# ENGINE-INF confirmatory-holdout EXTRACTOR (design §2.5 [R1], ASM-2104).
#
# A SEPARATE ENTRYPOINT THAT DOES NOT IMPORT THE ENGINE OR THE SCORER —
# custody clause 2, enforced mechanically: this file imports ONLY
# engineinf_wn (the engine-free core) and asserts at exit that neither
# twin_engine nor engineinf_lib (which carries score()) ever entered
# sys.modules. It constructs and sha-pins items-H + gold-H WITHOUT
# computing any outcome: gold is a function of third-party bytes + pinned
# rules, never of engine behaviour.
#
# Construction (all mechanical; no human item authoring; no new kernel
# authoring; $0 model spend):
#   H1  attested occurrences of the 4 Stage-A lemmas in SemCor
#       (brown1/brown2/brownv; pinned data/semcor30/semcor.zip, sha
#       verified before any byte is consumed). SemCor sense keys
#       (lemma%lexsn) map to WN3.1 synsets via the pinned index.sense;
#       unmappable keys -> logged exclusion. Argument extraction = the
#       ASM-1991 parse rules applied to the SemCor sentence, with a
#       mechanical ANCHOR CHECK: the parse's matched predicate token must
#       be the sense-tagged token, else logged exclusion.
#   H2  constructed-anomaly items: the pre-registered G3 cross-pair rule
#       applied to H1 objects (sense-side unanimity assessed over the
#       union of seen gloss-example objects and H1 objects; pairs
#       generated from H1 objects only).
#   H3  SemCor occurrences tagged to excludedSenses (kind refusal; feeds
#       the honesty secondary + full-divergence bookkeeping only — never
#       the co-primary frames).
# Decontamination: any H item whose (predicate synset, object noun lemma)
# pair occurs in ANY seen item is excluded, logged.
# Novel-cell restriction H*: an H item whose outcome-equivalence cell
# (ASM-2106 key) was realized in any seen frame has an inferable outcome
# under determinism; such items carry h_star=false and are EXCLUDED from
# the binding confirmatory frame (co-reported descriptively).
#
# Also emits the PC-6 DECOY bank (draw/hold/cut — members of neither
# Stage-A nor the kernel-v0 panel): the same pipeline run end-to-end on
# lemmas whose outcomes touch no endpoint. Decoy items are NOT holdout
# items (ids dc-*); the blocking pilot runs the engine on THEM, never on H.
#
# KILL-e1 (ASM-2105, evaluated here at $0, no outcomes needed): the binding
# frame (G1∪G3)_H* must have >= 30 items, >= 12 cells, span >= 2 closure
# ops (attested->O1, anomaly->O2) and >= 2 lemmas; a shortfall STOPS THE
# FREEZE (reported, not hidden).

import json
import re
import sys
import zipfile
from pathlib import Path

from engineinf_wn import (WN, LEMMAS, LEMMA_POS, DECOY_LEMMAS, DECOY_POS,
                          SEMCOR, ROOT, cell_key, cell_key_str,
                          kernel_inventory, load_sense_keys, parse_example,
                          sha256_file, canon_sha)

HERE = Path(__file__).resolve().parent
OUT = HERE / "holdout"
SEEN_ITEMS = HERE / "results" / "items.json"

KILL_E1_MIN_ITEMS = 30
KILL_E1_MIN_CELLS = 12
KILL_E1_MIN_OPS = 2
KILL_E1_MIN_LEMMAS = 2

WF_RE = re.compile(r"<wf ([^>]*)>([^<]*)</wf>")
ATTR_RE = re.compile(r'(\w+)="([^"]*)"')
TOKEN_RE = re.compile(r"[A-Za-z']+")


def verify_semcor_pin():
    man = json.load(open(SEMCOR / "manifest.json"))
    want = man["files"]["semcor.zip"]["sha256"]
    got = sha256_file(SEMCOR / "semcor.zip")
    if got != want:
        raise RuntimeError("semcor.zip sha256 %s != pinned %s (fail closed)"
                           % (got, want))
    return want


def iter_sentences(zf):
    """Deterministic scan: brown1, brown2, brownv; files sorted; sentences
    in file order. Yields (file_id, snum, [(text, attrs-or-None), ...])."""
    names = sorted(n for n in zf.namelist()
                   if re.match(r"semcor/brown[12v]/tagfiles/.*\.xml$", n))
    # brown1 < brown2 < brownv sorts naturally under str order
    for name in names:
        fid = name.split("/")[-1].rsplit(".", 1)[0]
        part = name.split("/")[1]
        text = zf.read(name).decode("utf8", errors="replace")
        for sm in re.finditer(r'<s snum="?(\d+)"?>(.*?)</s>', text, re.S):
            snum = int(sm.group(1))
            toks = []
            for wm in WF_RE.finditer(sm.group(2)):
                attrs = dict(ATTR_RE.findall(wm.group(1)))
                toks.append((wm.group(2), attrs))
            yield "%s/%s" % (part, fid), snum, toks


def parse_tokens(text):
    """EXACTLY the parse_example tokenization, applied per wf-token so the
    tagged token's index inside the joined sentence is computable."""
    raw = TOKEN_RE.findall(text.lower())
    return [t.strip("'") for t in raw if t.strip("'")]


def extract_corpus_occurrences(wn, lemma_pos, sense_keys, tag_of_interest):
    """Scan the pinned SemCor zip for tagged occurrences of the given
    lemmas; parse each carrier sentence with the ASM-1991 rules; anchor-
    check; type the argument noun. Returns (occurrences, exclusions).

    tag_of_interest(lemma, pos, synset_urn) -> kind-or-None decides whether
    an occurrence enters the bank (None -> logged exclusion with reason)."""
    occs, exclusions = [], []
    zf = zipfile.ZipFile(SEMCOR / "semcor.zip")
    for src, snum, toks in iter_sentences(zf):
        # token start-index ledger, mirroring parse_example tokenization
        starts, count = [], 0
        for text, attrs in toks:
            starts.append(count)
            count += len(parse_tokens(text.replace("_", " ")))
        for i, (text, attrs) in enumerate(toks):
            lemma = attrs.get("lemma")
            lexsn = attrs.get("lexsn")
            if lemma not in lemma_pos or not lexsn:
                continue
            pos_want = lemma_pos[lemma]
            if lexsn[0] != {"v": "2", "n": "1"}[pos_want]:
                continue                      # other-POS tagging of the form
            loc = {"source": src, "snum": snum, "token": text}
            key = "%s%%%s" % (lemma, lexsn)
            mapped = sense_keys.get(key)
            if mapped is None:
                exclusions.append(dict(loc, lemma=lemma, reason="unmappable-sense-key",
                                       sense_key=key))
                continue
            pos, off = mapped
            syn = "urn:lexical-wn31:%s-%s" % (pos, off)
            kind = tag_of_interest(lemma, pos, syn)
            if kind is None:
                exclusions.append(dict(loc, lemma=lemma, synset=syn,
                                       reason="synset-outside-inventory"))
                continue
            sentence = " ".join(t.replace("_", " ") for t, _ in toks)
            parsed, reason = parse_example(wn, sentence, [lemma])
            if parsed is None:
                exclusions.append(dict(loc, lemma=lemma, synset=syn,
                                       reason=reason))
                continue
            vi, vlen, noun, how = parsed
            if vi != starts[i]:
                exclusions.append(dict(loc, lemma=lemma, synset=syn,
                                       reason="anchor-mismatch"))
                continue
            side = wn.noun_side(noun)
            if side is None:
                exclusions.append(dict(loc, lemma=lemma, synset=syn,
                                       reason="side-undetermined:%s" % noun))
                continue
            occs.append({"lemma": lemma, "gold_synset": syn,
                         "object_noun": noun, "object_side": side,
                         "arg_slot": how, "kind": kind,
                         "source": loc, "sentence": sentence})
    return occs, exclusions


def build_holdout(wn):
    minted, excluded, _ = kernel_inventory()
    sense_keys = load_sense_keys(LEMMAS)
    seen = json.load(open(SEEN_ITEMS))["items"]
    seen_pairs = {(it["gold_synset"], it["object_noun"]) for it in seen}
    seen_cells = {cell_key_str(cell_key(wn, it)) for it in seen}

    def tag_of(lemma, pos, syn):
        if syn in minted:
            return "attested"
        if syn in excluded:
            return "refusal"
        return None

    occs, exclusions = extract_corpus_occurrences(
        wn, LEMMA_POS, sense_keys, tag_of)

    # ---- H1/H3 items with decontamination ----
    items, gold = [], {}
    seq = {}
    h1_attested = {}   # synset -> {noun: side} (for the H2 unanimity input)
    for o in occs:
        pair = (o["gold_synset"], o["object_noun"])
        if pair in seen_pairs:
            exclusions.append({"reason": "decontaminated-seen-pair",
                               "synset": o["gold_synset"],
                               "noun": o["object_noun"],
                               "source": o["source"]})
            continue
        if o["kind"] == "attested":
            h1_attested.setdefault(o["gold_synset"], {}).setdefault(
                o["object_noun"], o["object_side"])
        off = o["gold_synset"].split("-")[-1]
        k = (o["lemma"], o["kind"], off)
        seq[k] = seq.get(k, 0) + 1
        iid = "hi-%s-%s-%s-%02d" % (o["lemma"], o["kind"], off, seq[k])
        it = {"id": iid, "kind": o["kind"], "lemma": o["lemma"],
              "gold_synset": o["gold_synset"], "object_noun": o["object_noun"],
              "object_side": o["object_side"], "arg_slot": o["arg_slot"],
              "source_example": o["sentence"], "source": o["source"],
              "sense": minted.get(o["gold_synset"])}
        it["cell"] = cell_key_str(cell_key(wn, it))
        it["h_star"] = it["cell"] not in seen_cells
        items.append(it)
        gold[iid] = {"verdict": "CONSISTENT" if o["kind"] == "attested"
                     else "REFUSE",
                     "sense": minted.get(o["gold_synset"]),
                     "object_side": o["object_side"],
                     "gold_rule": "G1+G2" if o["kind"] == "attested" else "G4"}

    # ---- H2: the pre-registered G3 cross-pair rule over H1 objects ----
    # (unanimity over the UNION of seen gloss-example objects and H1
    # objects; pairs generated from H1 objects only — ASM-2104)
    union_attested = {}
    for it in seen:
        if it["kind"] == "attested":
            union_attested.setdefault(it["gold_synset"], {}).setdefault(
                it["object_noun"], it["object_side"])
    for s, objs in h1_attested.items():
        for n, sd in objs.items():
            union_attested.setdefault(s, {}).setdefault(n, sd)

    def synset_lemma(s):
        sense = minted[s]
        return sense.split(":")[-1].split(".")[0]

    unanimous = {}
    for s, objs in sorted(union_attested.items()):
        sides = sorted(set(objs.values()))
        if len(sides) == 1:
            unanimous[s] = sides[0]
        else:
            exclusions.append({"synset": s, "reason": "g3-mixed-attested-sides",
                               "sides": sides})
    for s, s_side in sorted(unanimous.items()):
        lemma = synset_lemma(s)
        for s2, s2_side in sorted(unanimous.items()):
            if s2 == s or synset_lemma(s2) != lemma or s2_side == s_side:
                continue
            for noun, n_side in sorted(h1_attested.get(s2, {}).items()):
                if n_side == s_side:
                    continue
                if (s, noun) in seen_pairs:
                    exclusions.append({"reason": "decontaminated-seen-pair",
                                       "synset": s, "noun": noun,
                                       "source": "h2-cross-pair"})
                    continue
                iid = "hi-%s-anomaly-%s-x-%s" % (lemma, s.split("-")[-1], noun)
                if iid in gold:
                    continue
                it = {"id": iid, "kind": "anomaly", "lemma": lemma,
                      "gold_synset": s, "object_noun": noun,
                      "object_side": n_side, "arg_slot": "object",
                      "source_example": "cross-pair: %s object of %s (H1)"
                                        % (noun, s2),
                      "source": {"source": "h2-cross-pair", "donor": s2},
                      "sense": minted.get(s)}
                it["cell"] = cell_key_str(cell_key(wn, it))
                it["h_star"] = it["cell"] not in seen_cells
                items.append(it)
                gold[iid] = {"verdict": "ANOMALOUS", "sense": None,
                             "object_side": n_side, "gold_rule": "G3"}

    items.sort(key=lambda it: it["id"])
    return items, gold, exclusions


def kill_e1(items, gold):
    """Holdout adequacy over the BINDING frame (G1∪G3)_H* — a COUNT of
    pinned items+cells, never a scoring (ASM-2105)."""
    frame = [it for it in items if it["h_star"]
             and gold[it["id"]]["gold_rule"] in ("G1+G2", "G3")]
    cells = sorted({it["cell"] for it in frame})
    ops = sorted({"O1" if it["kind"] == "attested" else "O2" for it in frame})
    lemmas = sorted({it["lemma"] for it in frame})
    fired = (len(frame) < KILL_E1_MIN_ITEMS or len(cells) < KILL_E1_MIN_CELLS
             or len(ops) < KILL_E1_MIN_OPS or len(lemmas) < KILL_E1_MIN_LEMMAS)
    return {"n_items_g1g3_hstar": len(frame), "n_cells_g1g3_hstar": len(cells),
            "ops_spanned": ops, "lemmas_spanned": lemmas,
            "thresholds": {"min_items": KILL_E1_MIN_ITEMS,
                           "min_cells": KILL_E1_MIN_CELLS,
                           "min_ops": KILL_E1_MIN_OPS,
                           "min_lemmas": KILL_E1_MIN_LEMMAS},
            "kill_e1_fired": fired,
            "op_rule": ("mechanical, outcome-free: kind attested exercises "
                        "O1 (typed entailment vs stated G2 side), kind "
                        "anomaly exercises O2 (typed disjointness) — "
                        "counted from pinned items alone")}


def build_decoys(wn):
    """PC-6 decoy bank (ASM-2111): the same pipeline on draw/hold/cut.
    No kernel inventory exists for decoys; every mapped synset is accepted
    (kind attested) and the synset-level G3 cross-pair rule runs over the
    decoy occurrences themselves. Ids dc-*, quarantined from every endpoint."""
    sense_keys = load_sense_keys(DECOY_LEMMAS)
    occs, exclusions = extract_corpus_occurrences(
        wn, DECOY_POS, sense_keys, lambda l, p, s: "attested")
    items, gold, seq = [], {}, {}
    attested = {}
    for o in occs:
        off = o["gold_synset"].split("-")[-1]
        k = (o["lemma"], off)
        seq[k] = seq.get(k, 0) + 1
        iid = "dc-%s-attested-%s-%02d" % (o["lemma"], off, seq[k])
        items.append({"id": iid, "kind": "attested", "lemma": o["lemma"],
                      "gold_synset": o["gold_synset"],
                      "object_noun": o["object_noun"],
                      "object_side": o["object_side"],
                      "arg_slot": o["arg_slot"],
                      "source_example": o["sentence"], "source": o["source"],
                      "sense": None})
        gold[iid] = {"verdict": "CONSISTENT", "sense": None,
                     "object_side": o["object_side"], "gold_rule": "G1+G2"}
        attested.setdefault(o["gold_synset"], {"lemma": o["lemma"],
                                               "objects": {}})
        attested[o["gold_synset"]]["objects"].setdefault(o["object_noun"],
                                                         o["object_side"])
    unanimous = {s: sorted(set(r["objects"].values()))[0]
                 for s, r in sorted(attested.items())
                 if len(set(r["objects"].values())) == 1}
    for s, s_side in sorted(unanimous.items()):
        lemma = attested[s]["lemma"]
        for s2, s2_side in sorted(unanimous.items()):
            if s2 == s or attested[s2]["lemma"] != lemma or s2_side == s_side:
                continue
            for noun, n_side in sorted(attested[s2]["objects"].items()):
                if n_side == s_side:
                    continue
                iid = "dc-%s-anomaly-%s-x-%s" % (lemma, s.split("-")[-1], noun)
                if iid in gold:
                    continue
                items.append({"id": iid, "kind": "anomaly", "lemma": lemma,
                              "gold_synset": s, "object_noun": noun,
                              "object_side": n_side, "arg_slot": "object",
                              "source_example": "cross-pair: %s object of %s"
                                                % (noun, s2),
                              "source": {"source": "decoy-cross-pair"},
                              "sense": None})
                gold[iid] = {"verdict": "ANOMALOUS", "sense": None,
                             "object_side": n_side, "gold_rule": "G3"}
    items.sort(key=lambda it: it["id"])
    return items, gold, exclusions


def main():
    OUT.mkdir(exist_ok=True)
    pin = verify_semcor_pin()
    wn = WN()

    items, gold, exclusions = build_holdout(wn)
    adequacy = kill_e1(items, gold)
    d_items, d_gold, d_exclusions = build_decoys(wn)

    counts = {}
    for it in items:
        counts[it["kind"]] = counts.get(it["kind"], 0) + 1
    (OUT / "items-h.json").write_text(json.dumps(
        {"schema": "kot-engineinf-items-h/1",
         "custody": ("Constructed and pinned PRE-FREEZE with NO engine or "
                     "scorer execution on any H item (ASM-2104). The "
                     "binding confirmatory frame is the h_star=true G1∪G3 "
                     "cells; h_star=false items are seen-cell duplicates "
                     "with inferable outcomes, co-reported descriptively "
                     "only."),
         "semcor_sha256": pin,
         "items": items, "counts": {"total": len(items), **counts},
         "n_hstar": sum(1 for it in items if it["h_star"])},
        indent=1, sort_keys=True) + "\n")
    (OUT / "gold-h.json").write_text(json.dumps(
        {"schema": "kot-engineinf-gold-h/1",
         "gold_disclosure": ("G1 sense-by-attachment (SemCor sentence tags) "
                             "+ G2 WN top-split typing are third-party "
                             "bytes; G3 anomaly labels are CONSTRUCTED-RULE "
                             "gold (design §2.1, disclosed in every claim); "
                             "G4 refusal gold is excludedSenses membership "
                             "with the ASM-1997/2116 scoring rule."),
         "gold": gold}, indent=1, sort_keys=True) + "\n")
    (OUT / "exclusions-h.json").write_text(json.dumps(
        {"schema": "kot-engineinf-exclusions-h/1", "exclusions": exclusions},
        indent=1, sort_keys=True) + "\n")
    (OUT / "decoy-items.json").write_text(json.dumps(
        {"schema": "kot-engineinf-decoy/1",
         "role": ("PC-6 machinery-validation bank (ASM-2111): outcomes "
                  "quarantined, touch no endpoint"),
         "items": d_items, "gold": d_gold,
         "exclusions": d_exclusions}, indent=1, sort_keys=True) + "\n")

    manifest = {
        "schema": "kot-engineinf-holdout-manifest/1",
        "semcor_zip_sha256": pin,
        "pins": {p.name: sha256_file(OUT / p.name)
                 for p in sorted(OUT.glob("*.json"))
                 if p.name != "holdout-manifest.json"},
        "counts": {"total": len(items), **counts,
                   "n_hstar": sum(1 for it in items if it["h_star"]),
                   "n_g1g3_hstar_items": adequacy["n_items_g1g3_hstar"],
                   "n_g1g3_hstar_cells": adequacy["n_cells_g1g3_hstar"],
                   "n_exclusions": len(exclusions),
                   "decoy_items": len(d_items)},
        "kill_e1": adequacy,
        "extractor": {"path": "poc/engine-inference/extract_holdout.py",
                      "sha256": sha256_file(HERE / "extract_holdout.py"),
                      "engineinf_wn_sha256": sha256_file(HERE / "engineinf_wn.py")},
        "date": "2026-07-13",
        "emitted_by": "writer-5",
    }
    (OUT / "holdout-manifest.json").write_text(
        json.dumps(manifest, indent=1, sort_keys=True) + "\n")

    # ---- custody self-check: no engine, no scorer, ever (ASM-2104) ----
    if "twin_engine" in sys.modules or "engineinf_lib" in sys.modules:
        raise RuntimeError("CUSTODY VIOLATION: engine/scorer module loaded "
                           "inside the holdout extractor")

    print(json.dumps({"items": len(items), "counts": counts,
                      "n_hstar": manifest["counts"]["n_hstar"],
                      "kill_e1": adequacy,
                      "decoys": len(d_items),
                      "exclusions": len(exclusions),
                      "custody": "no engine/scorer modules loaded"},
                     indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
