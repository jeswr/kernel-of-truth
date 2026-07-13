#!/usr/bin/env python3
# E2b LEMMA SELECTION — the MECHANICAL, BENCHMARK-BLIND rule (E2b-SEL) that
# picks the 6-10 sense-split inventory-extension lemmas for maintainer issue
# #29 (E2b, authorized after the E2a diagnostic measured the E0 O2 starvation
# as INVENTORY-LIMITED at the binding margin — ASM-2178).
#
# WHAT THIS SCRIPT IS: a deterministic census + filter over PINNED
# third-party bytes only. It selects lemmas whose VerbNet 3.3 classes
# GENUINELY restrict the undergoer (a side-entailing selectional restriction
# on the 'NP V NP' second-NP role — the exact E2a M2/M3/M4 mapping rules,
# imported byte-identically from the pinned e2a_verbnet_diagnostic module),
# that are SemCor-frequent (WN 3.1 index.sense tag_cnt), polysemous, and
# sortally differentiated within lemma. Design anchor: engine-inference
# design §E2b; ASM-2251 (rule verbatim); e0-kill-steering-synthesis.md item 3.
#
# BENCHMARK-BLINDNESS / CUSTODY (ASM-2250):
#   - consumes ONLY: the pinned VerbNet 3.3 zip (sha-verified, fail closed),
#     the pinned WN 3.1 dict bytes + synsets-*.jsonl extraction, the pinned
#     E2a selrestr-side-table.json, and the kernel-v0/v1 manifests (for the
#     mechanical exclusion list).
#   - NEVER opens: any SemCor sentence file, holdout/items-h.json,
#     holdout/gold-h.json, results/*, rows/orbit-rows/run-result, or any
#     outcome artifact. No engine, no scorer (asserted at exit, the
#     extract_holdout.py / e2a discipline).
#   - tag_cnt DISCLOSURE: WN 3.1 index.sense tag_cnt is a SemCor-DERIVED
#     aggregate shipped inside the pinned WN bytes. Using it is a FREQUENCY
#     steer toward holdout yield, not outcome information (no item, sentence,
#     or verdict is readable from it); it is the identical field the frozen
#     design already consumes (D-word-dom dominance ASM-1993; ASM-2110).
#
# Determinism: no wall-clock, no RNG; sorted iteration; fail-closed asserts.
# Double-run byte-identity required (certificate discipline).

import json
import re
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PENG = HERE.parent
sys.path.insert(0, str(PENG))
sys.path.insert(0, str(PENG / "e2a-verbnet-diagnostic"))

from engineinf_wn import (WN, LEMMAS, ROOT, parse_example,  # noqa: E402
                          sha256_file)
from e2a_verbnet_diagnostic import (VN_PREFIX, VN_ZIP, SIDE_TABLE,  # noqa: E402
                                    chain_roles, entail_side, expr_render,
                                    undergoer_roles, verify_vn_pin,
                                    walk_classes)

# ---------------------------------------------------------------- constants
# E2b-SEL rule constants — ALL fixed in this file before any selection
# output existed (ASM-2251). Changing any of them is a rule change and
# invalidates the selection.

DECOY_LEMMAS = ("cut", "draw", "hold")   # PC-6 machinery-SEEN lemmas (ASM-2111)
T_RESTRICTED = 5    # min tag_cnt of a VN-restricted synset (F2)
T_CONTRAST = 2      # min tag_cnt of the within-lemma contrast synset (F3/F4)
BUCKET_CAP = 5      # max lemmas taken per required-side bucket
TOTAL_FLOOR = 6     # E2b mandate: 6-10 lemmas
TOTAL_CAP = 10
# pinned relaxation ladder, applied IN ORDER only while total < TOTAL_FLOOR;
# each applied step is logged in the output (no silent relaxation):
LADDER = (("T_RESTRICTED", 3), ("T_CONTRAST", 1), ("DROP_F4B", None))

LEMMA_RE = re.compile(r"^[a-z]+$")   # F0: single-token alphabetic lemma


def excluded_lemmas():
    """Mechanical exclusion list (F1): Stage-A lemmas (their cells exist in
    seen frames), PC-6 decoy lemmas (their SemCor pipeline outcomes were
    computed end-to-end in the pilot => machinery-SEEN), and every kernel-v0
    panel lemma (the decoy-eligibility precedent, ASM-2111: E2b lemmas must
    be fresh w.r.t. BOTH kernels so no prior authored content anchors them)."""
    v0 = json.load(open(ROOT / "data/kernel-v0/manifest.json"))
    v0_lemmas = sorted({c["id"].split(":")[-1] for c in v0["concepts"]})
    return sorted(set(LEMMAS) | set(DECOY_LEMMAS) | set(v0_lemmas))


def load_all_verb_sense_keys():
    """index.sense: every verb sense-key -> WN3.1 offset (no lemma filter —
    E2b scans the full VerbNet member inventory)."""
    keys = {}
    for line in open(ROOT / "data/lexical-wn31/source/dict/index.sense"):
        f = line.split()
        key, off = f[0], f[1]
        lemma, rest = key.split("%", 1)
        if rest[0] != "2":            # verbs only
            continue
        keys[key] = (lemma, off)
    return keys


def load_verb_gloss_examples(offsets):
    """synsets-verb.jsonl: offset-urn -> (lemmas, gloss) for wanted set."""
    out = {}
    for line in open(ROOT / "data/lexical-wn31/synsets-verb.jsonl"):
        r = json.loads(line)
        off = r["id"].split("-")[-1]
        if off in offsets:
            out[off] = r["annotations"]
    return out


EXAMPLE_RE = re.compile(r'"([^"]+)"')


def vn_restriction_scan(zf, table, sense_keys):
    """Full-VerbNet analogue of the E2a mapping (rules M1/M2/M3/M4,
    byte-identical helper functions): for EVERY canonical class member with
    a non-'?' resolvable verb sense key, compute the undergoer role of the
    nearest 'NP V NP' frame on the chain and the side its selectional
    restriction entails under the pinned side table.

    Returns {lemma: {offset: {"sides": {side: [class ids]},
                              "classes": [match records]}}}"""
    scan = {}
    for cid, chain in walk_classes(zf):
        node = chain[-1]
        members = node.find("MEMBERS")
        if members is None:
            continue
        roles = None
        und = None
        for m in members:
            name, wnattr = m.get("name"), (m.get("wn") or "").strip()
            if not LEMMA_RE.match(name or "") or not wnattr:
                continue
            for key in wnattr.split():
                if key.startswith("?"):        # VerbNet's own uncertainty mark
                    continue
                hit = sense_keys.get(key + "::")
                if hit is None:
                    continue
                lemma, off = hit
                if lemma != name:              # key must belong to the member
                    continue
                if roles is None:              # lazy, once per class node
                    roles = chain_roles(chain)
                    und = undergoer_roles(chain)
                flags = []
                sides = set()
                rendered = []
                for r in und:
                    expr = roles.get(r)
                    s = entail_side(expr, table, flags) if expr else None
                    rendered.append({"role": r,
                                     "restriction": expr_render(expr)
                                     if expr else "(role undefined on chain)",
                                     "entailed_side": s})
                    if s:
                        sides.add(s)
                side = sorted(sides)[0] if len(sides) == 1 else None
                rec = scan.setdefault(lemma, {}).setdefault(
                    off, {"per_class": [], "sides": {}})
                rec["per_class"].append(
                    {"class": cid, "member_key": key,
                     "undergoer_roles": rendered, "flags": flags,
                     "class_entailed_side": side})
                if side:
                    rec["sides"].setdefault(side, []).append(cid)
    return scan


def required_side(rec):
    """E2a rule M4, verbatim: defined iff >=1 matched class entails a side
    and ALL side-entailing matched classes agree; conflicts yield None."""
    sides = sorted(rec["sides"])
    return sides[0] if len(sides) == 1 else None


def main():
    vn_sha = verify_vn_pin()
    table = json.load(open(SIDE_TABLE))["types"]
    wn = WN()
    sense_keys = load_all_verb_sense_keys()
    zf = zipfile.ZipFile(VN_ZIP)
    excl = excluded_lemmas()

    scan = vn_restriction_scan(zf, table, sense_keys)

    t_restricted, t_contrast, drop_f4b = T_RESTRICTED, T_CONTRAST, False
    ladder_applied = []

    def build_candidates():
        cands = []
        for lemma in sorted(scan):
            if lemma in excl:                              # F1
                continue
            if lemma not in wn.vidx:                       # in pinned WN 3.1
                continue
            tagmap = wn.tags.get((lemma, "v"), {})
            offs = wn.vidx[lemma]
            # restricted synsets passing F2
            restricted = []
            for off, rec in sorted(scan[lemma].items()):
                side = required_side(rec)
                if side and tagmap.get(off, 0) >= t_restricted:
                    restricted.append((off, side, tagmap.get(off, 0),
                                       sorted(set(rec["sides"][side]))))
            if not restricted:
                continue
            restricted.sort(key=lambda r: (-r[2], r[0]))
            top_off, top_side, top_tag, top_classes = restricted[0]
            # F3: polysemy — >=2 synsets with tag_cnt >= T_CONTRAST
            frequent = [o for o in offs if tagmap.get(o, 0) >= t_contrast]
            if len(frequent) < 2:
                continue
            # F4: within-lemma sortal differentiation — another frequent
            # synset with (a) VN required side OPPOSITE the restricted
            # synset's, or (b) a parsed WN gloss-example object on the
            # opposite side (pinned ASM-1991 parse + noun_side; gloss bytes
            # are third-party and were never extracted for non-Stage-A
            # lemmas, so nothing here is benchmark-derived).
            opp = {"phys": "abst", "abst": "phys"}[top_side]
            contrast = None
            for off in frequent:
                if off == top_off:
                    continue
                rec2 = scan[lemma].get(off)
                if rec2 and required_side(rec2) == opp:
                    contrast = (off, "vn-opposite-side")
                    break
            if contrast is None and not drop_f4b:
                want = {o for o in frequent if o != top_off}
                ann = load_verb_gloss_examples(want)
                for off in sorted(want, key=lambda o: (-tagmap.get(o, 0), o)):
                    a = ann.get(off)
                    if not a:
                        continue
                    for ex in EXAMPLE_RE.findall(a["gloss"]):
                        parsed, _ = parse_example(wn, ex, a["lemmas"])
                        if parsed is None:
                            continue
                        if wn.noun_side(parsed[2]) == opp:
                            contrast = (off, "gloss-object-%s:%s"
                                        % (opp, parsed[2]))
                            break
                    if contrast:
                        break
            if contrast is None and drop_f4b:
                others = sorted((o for o in frequent if o != top_off),
                                key=lambda o: (-tagmap.get(o, 0), o))
                if others:
                    contrast = (others[0], "ladder-DROP_F4B-any-second-sense")
            if contrast is None:
                continue
            cands.append({
                "lemma": lemma, "bucket": top_side,
                "restricted": [
                    {"offset": o, "synset": "urn:lexical-wn31:v-" + o,
                     "required_side": sd, "tag_cnt": tg, "classes": cl}
                    for o, sd, tg, cl in restricted],
                "top_restricted": {"offset": top_off,
                                   "synset": "urn:lexical-wn31:v-" + top_off,
                                   "required_side": top_side,
                                   "tag_cnt": top_tag,
                                   "classes": top_classes},
                "contrast": {"offset": contrast[0],
                             "synset": "urn:lexical-wn31:v-" + contrast[0],
                             "tag_cnt": tagmap.get(contrast[0], 0),
                             "evidence": contrast[1]},
                "n_verb_synsets": len(offs),
                "n_frequent_synsets": len(frequent),
                "lemma_tag_total": sum(tagmap.values()),
            })
        return cands

    cands = build_candidates()

    def select(cands):
        buckets = {"phys": [], "abst": []}
        for c in cands:
            buckets[c["bucket"]].append(c)
        for b in buckets.values():
            b.sort(key=lambda c: (-c["top_restricted"]["tag_cnt"],
                                  c["lemma"]))
        sel = buckets["phys"][:BUCKET_CAP] + buckets["abst"][:BUCKET_CAP]
        if len(sel) < TOTAL_FLOOR:
            rest = sorted((c for c in cands if c not in sel),
                          key=lambda c: (-c["top_restricted"]["tag_cnt"],
                                         c["lemma"]))
            sel += rest[:TOTAL_FLOOR - len(sel)]
        return sorted(sel, key=lambda c: c["lemma"])[:TOTAL_CAP]

    selected = select(cands)
    for name, val in LADDER:                     # pinned ladder, in order
        if len(selected) >= TOTAL_FLOOR:
            break
        ladder_applied.append(name)
        if name == "T_RESTRICTED":
            t_restricted = val
        elif name == "T_CONTRAST":
            t_contrast = val
        elif name == "DROP_F4B":
            drop_f4b = True
        cands = build_candidates()
        selected = select(cands)

    # structural O2 cell-space bound of the selection (ASM-2177 arithmetic):
    # a phys-restricted synset admits exactly 1 fresh anomaly cell
    # (synset|abst|wn-something|anomaly); an abst-restricted synset admits 2
    # (phys x {wn-somebody, wn-something}). Fresh-by-construction: no
    # selected lemma's synset occurs in any seen frame (F1 guarantees it).
    bound = 0
    for c in selected:
        for r in c["restricted"]:
            bound += 1 if r["required_side"] == "phys" else 2

    out = {
        "schema": "kot-e2b-selection/1",
        "role": ("E2b MECHANICAL LEMMA SELECTION (design artifact, "
                 "maintainer-approved issue #29). Selects inventory-extension "
                 "lemmas by the pinned E2b-SEL rule; adopts NO anomaly-gold "
                 "construct, runs NO engine, reads NO outcome, licenses NO "
                 "feasibility conclusion."),
        "rule": {
            "F0": "single-token alphabetic VerbNet member lemma, present in "
                  "pinned WN 3.1 index.verb",
            "F1": "lemma not in Stage-A {break,find,friend,make}, not a PC-6 "
                  "decoy {cut,draw,hold}, not a kernel-v0 panel lemma "
                  "(mechanical from the two manifests)",
            "F2": "has >=1 VN-restricted synset: some canonical class member "
                  "sense key (non-'?', resolved via pinned index.sense) whose "
                  "chain undergoer role (M2: second NP of the nearest "
                  "'NP V NP' frame) carries a side-entailing restriction "
                  "(M3 pinned side table; M4 all-classes-agree), with "
                  "tag_cnt >= T_RESTRICTED",
            "F3": "polysemy: >=2 verb synsets with tag_cnt >= T_CONTRAST",
            "F4": "within-lemma sortal differentiation: another frequent "
                  "synset with VN required side OPPOSITE the top restricted "
                  "synset's (a), else a parsed WN gloss-example object on "
                  "the opposite side (b, ASM-1991 parse rules)",
            "ranking": "per required-side bucket: top restricted synset "
                       "tag_cnt desc, lemma asc; take <=BUCKET_CAP per "
                       "bucket; floor/backfill per pinned ladder",
            "constants": {"T_RESTRICTED": T_RESTRICTED,
                          "T_CONTRAST": T_CONTRAST,
                          "BUCKET_CAP": BUCKET_CAP,
                          "TOTAL_FLOOR": TOTAL_FLOOR,
                          "TOTAL_CAP": TOTAL_CAP},
            "ladder_applied": ladder_applied,
        },
        "custody": ("Benchmark-blind: consumed VerbNet zip + WN 3.1 dict "
                    "bytes + synsets-*.jsonl + selrestr-side-table + kernel "
                    "manifests ONLY; no SemCor sentence, holdout, results, "
                    "gold, rows, or outcome artifact opened; no engine/"
                    "scorer import (asserted at exit). tag_cnt is the "
                    "SemCor-derived frequency aggregate inside the pinned "
                    "WN bytes (disclosure: ASM-2251)."),
        "pins": {
            "verbnet_zip_sha256": vn_sha,
            "side_table_sha256": sha256_file(SIDE_TABLE),
            "script_sha256": sha256_file(HERE / "e2b_select_lemmas.py"),
            "engineinf_wn_sha256": sha256_file(PENG / "engineinf_wn.py"),
            "e2a_diagnostic_sha256": sha256_file(
                PENG / "e2a-verbnet-diagnostic/e2a_verbnet_diagnostic.py"),
        },
        "excluded_lemmas": excl,
        "n_candidates": len(cands),
        "candidates_not_selected": sorted(
            c["lemma"] for c in cands if c not in selected),
        "selected": selected,
        "n_selected": len(selected),
        "bucket_counts": {
            "phys": sum(1 for c in selected if c["bucket"] == "phys"),
            "abst": sum(1 for c in selected if c["bucket"] == "abst")},
        "structural_novel_o2_cell_bound_NOT_GOLD": bound,
        "emitted_by": "designer-8", "date": "2026-07-13",
    }
    (HERE / "e2b-selection.json").write_text(
        json.dumps(out, indent=1, sort_keys=True) + "\n")

    # ---- custody self-check: no engine, no scorer, ever ----
    if "twin_engine" in sys.modules or "engineinf_lib" in sys.modules:
        raise RuntimeError("CUSTODY VIOLATION: engine/scorer module loaded "
                           "inside the E2b selection")

    brief = {"n_candidates": len(cands), "n_selected": len(selected),
             "buckets": out["bucket_counts"],
             "ladder_applied": ladder_applied,
             "selected": [(c["lemma"], c["bucket"],
                           c["top_restricted"]["classes"][0],
                           c["top_restricted"]["tag_cnt"]) for c in selected],
             "o2_bound": bound}
    print(json.dumps(brief, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
