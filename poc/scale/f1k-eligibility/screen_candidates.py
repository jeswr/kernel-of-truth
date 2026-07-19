#!/usr/bin/env python3
"""screen_candidates.py — F1-K candidate-pool eligibility screen (issue #33, $0).

DESIGN-INDEPENDENT (b)+(c) screen over the large-kernel concept pool
(poc/scale/results/scale-s1-census.json), producing the SCREENED POOL the
in-flight codex design (criterion (a): explication sourcing + final
selection) will select from:

  (b) clean WordNet-3.1 alignment  — concept maps to a WN31 synset;
  (c) >= 8 known-concept eval items available across the pinned F1-K eval
      sources (MMLU / ARC-Easy / ARC-Challenge / OpenBookQA / CSQA), counted
      with the SAME item->concept mapping machinery as
      poc/glm52-probe/f1k-harness/corpora/build_corpora.py (the build that
      yielded 49 clusters / 46 with m>=8 from kernel-v0).

BENCHMARK-BLIND: this pass counts trigger matches on item TEXT only. It
never reads gold-answer correctness against any model, never touches model
outputs, logits, or run results. (Gold indices pass through the same
well-formedness filter as build_corpora — an item-admission rule, not an
outcome.)

FROZEN / REUSED SOURCES (every rule cites one):
  [S1]   poc/scale/results/scale-s1-census.json — the pool definition
         (207,733 UNMERGED type-level clusters = WN 110,049 + OBO 95,201 +
         SUMO 2,483).
  [BC]   poc/glm52-probe/f1k-harness/corpora/build_corpora.py — the
         item->concept mapping machinery reused verbatim where possible:
         WN dict parse, trigger expansion (synset lemmas + derivational
         '+'-pointer lemmas), OP-4 whole-word case-insensitive matching,
         source pins, item admission (3<=k<=5 options, valid gold).
  [WN]   data/lexical-wn31/ — pinned WN3.1 source dict + kot-lex/1 jsonl
         (instanceHypernym marks the 7,742 named-individual synsets the
         census excludes from the type-level pool) +
         alignment-kernel-v0.json (kot-lex-align/1).
  [EV]   data/f1k-eval-v1/source/*.parquet — the five pinned benchmark
         snapshots, sha256-verified against build_corpora's SOURCES pins
         (fail closed).
  [REG]  registry/experiments/f1k.json power gate: C >= 65 clusters each
         m >= 8 (ASM-2271) — the downstream gate this screen buys headroom
         for. READ ONLY; nothing here writes the registry.

SCREENING OPERATIONALISATIONS (SOP-*; disclosed in coverage-report.json,
for the codex design to adopt or amend — none is a freeze):
  SOP-1  (b)-screenable pool = the WN31 TYPE-LEVEL portion (110,049
         synsets). OBO and SUMO clusters have NO computed WN crosswalk
         ([S1] four_counts_S35.exactly_crosswalked_clusters = NOT COMPUTED;
         data/onto-sumo carries zero WordNet mappings), so no OBO/SUMO
         record can be claimed "cleanly WN-aligned" without inventing an
         alignment. Excluded and REPORTED, not padded.
  SOP-2  trigger surface per synset = its own lemmas + derivationally-
         related ('+' pointer) word lemmas, lowercased, underscores to
         spaces, syntactic markers stripped — byte-identical rule to
         [BC build_triggers].
  SOP-3  matching = [BC OP-4] case-insensitive whole-word match, counted
         over QUESTION + OPTION text only. The fixed header/cue/label
         bytes are excluded from counting: over a 110k-concept pool many
         synsets' triggers collide with the draft header bytes (e.g.
         'letter', 'respond', 'item') and would spuriously score m = ALL
         items; in the realized design such concepts would instead FAIL
         the DES §R-REV2.1 header-trigger-freedom check, so they are
         FLAGGED (header_cue_collision) for the design to exclude or to
         redraft the header around.
  SOP-4  eligibility (c) = m_total >= 8, where m_total = number of admitted
         eval items with >= 1 trigger match in question or options
         (matches [BC]'s admission rule: any resolved span -> the item is
         available to the cluster).
  SOP-5  headroom honesty: per-concept counts OVERLAP (an item matching k
         concepts can serve only ONE cluster in a realized test set, [BC]
         OP-6a). A deterministic greedy DISJOINT assignment
         (scarcest-concept-first, ascending m_total then URN; each concept
         claims its 8 lowest-index unclaimed items) gives a LOWER BOUND on
         the number of clusters simultaneously reaching m >= 8. That bound,
         not the raw eligible count, is the honest number to hold against
         the C >= 65 gate.
  SOP-6  sense-ambiguity heuristic (screening aid only, NOT an eligibility
         criterion): a matched phrase is 'unambiguous evidence' for concept
         c iff it is a DIRECT lemma of c, that lemma names exactly one
         type-level synset in all of WN31, AND its WN SOURCE form carries
         no uppercase (cased/acronym lemmas like 'AN', 'IT', 'WHO', 'OR'
         are lowercased by the reused [BC] expansion and then collide
         case-insensitively with function words — objectively weak
         evidence, excluded from the heuristic but NOT from m_total).
         m_unambig = items with >= 1 such match. Criterion (a)
         (explication quality / sense fit) is the codex design's, deferred.

Determinism: byte-identical outputs on re-run. No wall-clock, no RNG, no
network, no model, no git/registry/freeze/spend. colibri naming; no handles.
"""

import hashlib
import json
import os
import re
import sys
from array import array
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]                       # repo root (kernel-of-truth/)

PASS_STAMP = "2026-07-13 designer-29 f1k-eligibility screen ($0)"  # fixed text, not wall-clock

# --- constants reused from [BC] (cited there) ------------------------------
POWER_GATE_MIN_C = 65      # [REG n_planned.power_gate, ASM-2271]
POWER_GATE_MIN_M = 8
HEADROOM_TARGET = 100      # issue #33: "target >=100+ if the pool supports it"
HEADER = ("Below is a multiple-choice item. Respond with the letter of the "
          "best option.\n\n")               # [BC OP-2 draft bytes]
CUE = "Answer:"
LABEL_ALPHABET = ["A", "B", "C", "D", "E"]
SOURCES = [                                  # [BC SOURCES] key + pinned sha256
    ("mmlu", "74a41822ce7d3def56e1682f958469c04642a5336a5ce912fa375fdb90fb25d7"),
    ("arc-easy", "4160597d618ae851c7eb04e281574f3f654776216ac6b6641588d64527b47177"),
    ("arc-challenge", "62f03257e737aed263f55c6abf87c7bb0028a44a6bdd2a26eb1279eb42c1d1e9"),
    ("openbookqa", "cd5483e366daa230c1c87bbdc512d8b7229f14f6dd04d19fc8b1a3855aaaa8a3"),
    ("csqa", "bdbd9bf9cc4d2349b24901038b2ab2f58e10e4e507ad2fd425dca55cd3cb6660"),
]
SRC_KEYS = [k for k, _ in SOURCES]
WORD_RE = re.compile(r"[a-z][a-z'-]*")       # [BC WORD_RE]
ERR = "ERR_F1K_ELIG"


def fail(msg):
    print("%s: %s" % (ERR, msg), file=sys.stderr)
    sys.exit(2)


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path, obj):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, indent=1, sort_keys=True, ensure_ascii=False)
        f.write("\n")


# ---------------------------------------------------------------------------
# Stage 1 — WN3.1 dict parse (identical logic to [BC parse_wn_dict])
# ---------------------------------------------------------------------------
def parse_wn_dict():
    dictdir = ROOT / "data" / "lexical-wn31" / "source" / "dict"
    out = {}
    cased = set()        # lowercased forms whose WN SOURCE form has uppercase
    for pos, fn in (("n", "data.noun"), ("v", "data.verb"),
                    ("a", "data.adj"), ("r", "data.adv")):
        with open(dictdir / fn, encoding="latin-1") as f:
            for line in f:
                if line.startswith("  "):
                    continue                 # license header
                body, _, gloss = line.partition("|")
                parts = body.split()
                off = parts[0]
                w_cnt = int(parts[3], 16)
                words, i = [], 4
                for _ in range(w_cnt):
                    w = parts[i]
                    w = re.sub(r"\((?:p|a|ip)\)$", "", w)   # syntactic markers
                    w = w.replace("_", " ")
                    if w != w.lower():       # SOP-6: cased/acronym source form
                        cased.add(w.lower())
                    words.append(w.lower())
                    i += 2                   # skip lex_id
                p_cnt = int(parts[i]); i += 1
                deriv = {}
                for _ in range(p_cnt):
                    sym, toff, tpos, st = parts[i:i + 4]
                    i += 4
                    if sym == "+":           # derivationally related form
                        src = int(st[:2], 16)
                        tgt = int(st[2:], 16)
                        tp = "a" if tpos == "s" else tpos
                        deriv.setdefault(src, []).append((tp, toff, tgt))
                out[(pos, off)] = {"words": words, "gloss": gloss.strip(),
                                   "deriv": deriv}
    return out, cased


# ---------------------------------------------------------------------------
# Stage 2 — type-level pool (SOP-1): exclude the 7,742 instance synsets
# ---------------------------------------------------------------------------
def load_instance_urns():
    """urns of named-individual synsets ([S1] instances_named_individuals):
    kot-lex/1 records carrying an instanceHypernym axiom."""
    inst = set()
    total = 0
    for fn in ("synsets-noun.jsonl", "synsets-verb.jsonl",
               "synsets-adj.jsonl", "synsets-adv.jsonl"):
        with open(ROOT / "data" / "lexical-wn31" / fn, encoding="utf-8") as f:
            for line in f:
                d = json.loads(line)
                total += 1
                if any(a["rel"] == "instanceHypernym" for a in d["axioms"]):
                    inst.add(d["id"])
    return inst, total


def urn_of(pos, off):
    return "urn:lexical-wn31:%s-%s" % (pos, off)


# ---------------------------------------------------------------------------
# Stage 3 — trigger expansion (SOP-2, byte-identical rule to [BC])
# ---------------------------------------------------------------------------
def build_pool(wn, instance_urns):
    """Returns concepts list (index = concept id) + lemma ambiguity map.
    Concept order: (pos, offset) ascending — deterministic."""
    lemma_synsets = Counter()                # direct-lemma ambiguity (SOP-6)
    keys = sorted(wn.keys())
    for key in keys:
        if urn_of(*key) in instance_urns:
            continue
        for w in set(wn[key]["words"]):
            lemma_synsets[w] += 1
    concepts = []
    for key in keys:
        urn = urn_of(*key)
        if urn in instance_urns:
            continue
        ss = wn[key]
        triggers = {}
        for w in ss["words"]:
            triggers.setdefault(w, "synset-lemma")
        for src_idx, targets in ss["deriv"].items():
            src_lemma = (ss["words"][src_idx - 1]
                         if 0 < src_idx <= len(ss["words"]) else "?")
            for (tp, toff, tidx) in targets:
                tss = wn.get((tp, toff))
                if tss is None or not (0 < tidx <= len(tss["words"])):
                    continue
                triggers.setdefault(tss["words"][tidx - 1],
                                    "derivational(from %s)" % src_lemma)
        concepts.append({
            "urn": urn, "pos": key[0],
            "lemmas": ss["words"], "gloss": ss["gloss"],
            "triggers": sorted(triggers),
            "direct": set(ss["words"]),      # direct lemmas (SOP-6)
        })
    return concepts, lemma_synsets


def compile_index(concepts):
    """first-token -> {phrase: [concept ids]} prefilter index ([BC
    compile_matchers] shape; regexes compiled lazily on first hit)."""
    idx = {}
    for cid, c in enumerate(concepts):
        for ph in c["triggers"]:
            first = ph.split()[0] if ph.split() else ""
            if not WORD_RE.fullmatch(first):
                # a phrase whose first token is not a WORD_RE word can never
                # pass [BC]'s prefilter (WORD_RE extracts only [a-z]-initial
                # words) — skipped there, skipped identically here.
                continue
            idx.setdefault(first, {}).setdefault(ph, []).append(cid)
    return idx


class Matcher:
    """[BC OP-4] whole-word case-insensitive matching, presence-only."""

    def __init__(self, idx):
        self.idx = idx
        self.rx_cache = {}

    def match(self, text):
        """-> set of concept ids with >=1 trigger match, and the set of
        matched phrases (for the SOP-6 ambiguity heuristic)."""
        low = text.lower()
        words = set(WORD_RE.findall(low))
        cids, phrases = set(), set()
        for w in words:
            bucket = self.idx.get(w)
            if not bucket:
                continue
            for ph, owners in bucket.items():
                rx = self.rx_cache.get(ph)
                if rx is None:
                    rx = re.compile(r"\b" + re.escape(ph) + r"\b",
                                    re.IGNORECASE)
                    self.rx_cache[ph] = rx
                if rx.search(text):
                    cids.update(owners)
                    phrases.add(ph)
        return cids, phrases


# ---------------------------------------------------------------------------
# Stage 4 — benchmark items ([BC load_benchmarks] admission, pinned bytes)
# ---------------------------------------------------------------------------
def load_items():
    import pyarrow.parquet as pq
    src_dir = ROOT / "data" / "f1k-eval-v1" / "source"
    items = []
    for rank, (key, want) in enumerate(SOURCES):
        p = src_dir / ("%s.parquet" % key)
        if not p.exists():
            fail("pinned snapshot %s missing" % p)
        got = sha256_file(p)
        if got != want:
            fail("source %s sha256 %s != [BC] pin %s — STOP" % (key, got, want))
        rows = pq.read_table(p).to_pylist()
        for ri, r in enumerate(rows):
            if key == "mmlu":
                q = r["question"].strip()
                opts = [o.strip() for o in r["choices"]]
                gold = int(r["answer"])
            else:
                q = (r.get("question") or r.get("question_stem")).strip()
                ch = r["choices"]
                opts = [o.strip() for o in ch["text"]]
                labels_pub = list(ch["label"])
                if r["answerKey"] not in labels_pub:
                    continue
                gold = labels_pub.index(r["answerKey"])
            if not (3 <= len(opts) <= 5) or not (0 <= gold < len(opts)):
                continue                     # [BC] well-formedness admission
            items.append({"source": key, "source_rank": rank,
                          "question": q, "options": opts})
    return items


# ---------------------------------------------------------------------------
def main():
    print("[1/6] parsing WN3.1 dict + type-level pool ...")
    wn, cased = parse_wn_dict()
    instance_urns, jsonl_total = load_instance_urns()
    concepts, lemma_synsets = build_pool(wn, instance_urns)
    n_pool = len(concepts)
    if jsonl_total != 117791:
        fail("lexical-wn31 record count %d != census 117791" % jsonl_total)
    if n_pool != 110049:
        fail("type-level pool %d != census type_level 110049 — pool moved"
             % n_pool)
    mono = {w for w, n in lemma_synsets.items() if n == 1} - cased
    print("  pool: %d type-level synsets (census-exact), %d instances "
          "excluded, %d monosemous lowercase-source direct lemmas "
          "(%d cased/acronym forms excluded from the SOP-6 heuristic)"
          % (n_pool, len(instance_urns), len(mono), len(cased)))

    idx = compile_index(concepts)
    matcher = Matcher(idx)
    n_phrases = len({ph for b in idx.values() for ph in b})
    print("  trigger index: %d distinct phrases over %d first tokens"
          % (n_phrases, len(idx)))

    # ---- header/cue/label collision flags (SOP-3) -------------------------
    print("[2/6] header/cue/label collision flags ...")
    hdr_cids = set()
    for text in (HEADER, CUE, " ".join(LABEL_ALPHABET)):
        cids, _ = matcher.match(text)
        hdr_cids.update(cids)
    print("  %d pool concepts collide with the draft header/cue/label bytes "
          "(flagged; excluded from nothing — SOP-3)" % len(hdr_cids))

    # ---- eval items --------------------------------------------------------
    print("[3/6] loading pinned eval snapshots ...")
    items = load_items()
    n_items = len(items)
    src_totals = Counter(it["source"] for it in items)
    print("  %d admitted items: %s" % (n_items, dict(src_totals)))

    # ---- counting pass (SOP-3/SOP-4) ---------------------------------------
    print("[4/6] counting trigger matches (question+options, OP-4 rule) ...")
    stats = {}           # cid -> [m_total, m_stem, m_unambig, Counter(src)]
    per_cid_items = {}   # cid -> array('i') of item indices (for SOP-5)
    per_cid_unamb = {}   # cid -> array('i') of unambiguous-evidence items
    contention = Counter()   # per item: #matching concepts (raw pool)
    for ii, it in enumerate(items):
        stem_cids, stem_ph = matcher.match(it["question"])
        opt_cids, opt_ph = matcher.match("\n".join(it["options"]))
        all_cids = stem_cids | opt_cids
        if not all_cids:
            contention[0] += 1
            continue
        contention[len(all_cids)] += 1
        phrases = stem_ph | opt_ph
        for cid in all_cids:
            s = stats.get(cid)
            if s is None:
                s = stats[cid] = [0, 0, 0, Counter()]
                per_cid_items[cid] = array("i")
            s[0] += 1
            if cid in stem_cids:
                s[1] += 1
            c = concepts[cid]
            if any(ph in mono for ph in phrases if ph in c["direct"]):
                s[2] += 1
                per_cid_unamb.setdefault(cid, array("i")).append(ii)
            s[3][it["source"]] += 1
            per_cid_items[cid].append(ii)
        if (ii + 1) % 5000 == 0:
            print("  ... %d/%d items" % (ii + 1, n_items))
    n_matched_any = len(stats)
    print("  %d pool concepts match >=1 item" % n_matched_any)

    # ---- eligibility (SOP-4) ----------------------------------------------
    eligible = [cid for cid, s in stats.items() if s[0] >= POWER_GATE_MIN_M]
    # rank: m_total desc, m_stem desc, urn asc — deterministic
    eligible.sort(key=lambda cid: (-stats[cid][0], -stats[cid][1],
                                   concepts[cid]["urn"]))
    n_eligible = len(eligible)
    n_eligible_clean = sum(1 for cid in eligible if cid not in hdr_cids)
    print("[5/6] eligibility: %d concepts with m_total >= %d (%d of them "
          "free of header/cue collisions)"
          % (n_eligible, POWER_GATE_MIN_M, n_eligible_clean))

    # ---- SOP-5 greedy disjoint lower bound ---------------------------------
    print("[6/6] greedy disjoint assignment (scarcest-first) ...")
    order = sorted(eligible, key=lambda cid: (stats[cid][0],
                                              concepts[cid]["urn"]))
    claimed = bytearray(n_items)
    greedy_ok = set()
    for cid in order:
        take = []
        for ii in per_cid_items[cid]:
            if not claimed[ii]:
                take.append(ii)
                if len(take) == POWER_GATE_MIN_M:
                    break
        if len(take) == POWER_GATE_MIN_M:
            for ii in take:
                claimed[ii] = 1
            greedy_ok.add(cid)
    c_disjoint = len(greedy_ok)
    # and the same bound over header-clean concepts only
    claimed2 = bytearray(n_items)
    greedy_ok_clean = set()
    for cid in order:
        if cid in hdr_cids:
            continue
        take = []
        for ii in per_cid_items[cid]:
            if not claimed2[ii]:
                take.append(ii)
                if len(take) == POWER_GATE_MIN_M:
                    break
        if len(take) == POWER_GATE_MIN_M:
            for ii in take:
                claimed2[ii] = 1
            greedy_ok_clean.add(cid)
    c_disjoint_clean = len(greedy_ok_clean)
    # CONSERVATIVE bound (SOP-5+SOP-6): header-clean concepts reaching m>=8
    # on DISJOINT items each matched via a MONOSEMOUS DIRECT LEMMA — the
    # strongest design-independent adequacy statement this screen can make.
    unamb_eligible = sorted(
        (cid for cid, s in stats.items()
         if s[2] >= POWER_GATE_MIN_M and cid not in hdr_cids),
        key=lambda cid: (stats[cid][2], concepts[cid]["urn"]))
    claimed3 = bytearray(n_items)
    greedy_ok_unamb = set()
    for cid in unamb_eligible:
        take = []
        for ii in per_cid_unamb[cid]:
            if not claimed3[ii]:
                take.append(ii)
                if len(take) == POWER_GATE_MIN_M:
                    break
        if len(take) == POWER_GATE_MIN_M:
            for ii in take:
                claimed3[ii] = 1
            greedy_ok_unamb.add(cid)
    n_unamb8 = sum(1 for cid, s in stats.items() if s[2] >= POWER_GATE_MIN_M)
    c_disjoint_unamb = len(greedy_ok_unamb)
    print("  disjoint m>=8 lower bound: C >= %d (raw), C >= %d "
          "(header-clean), C >= %d (conservative: unambiguous-lemma "
          "evidence only)" % (c_disjoint, c_disjoint_clean, c_disjoint_unamb))

    # ---- kernel-v0 / molecules alignment flags -----------------------------
    align = json.load(open(ROOT / "data" / "lexical-wn31" /
                           "alignment-kernel-v0.json", encoding="utf-8"))
    aligned_to = {}
    for a in align["alignments"]:
        aligned_to.setdefault(a["synset"], []).append(a["concept"])

    # ---- alternative ranking by unambiguous evidence (screening aid) -------
    alt_order = sorted(eligible, key=lambda cid: (-stats[cid][2],
                                                  -stats[cid][0],
                                                  concepts[cid]["urn"]))
    alt_rank = {cid: i + 1 for i, cid in enumerate(alt_order)}

    # ---- candidate-pool.json ------------------------------------------------
    def entry(rank, cid):
        c, s = concepts[cid], stats[cid]
        return {
            "rank": rank,
            "urn": c["urn"],
            "pos": c["pos"],
            "lemmas": c["lemmas"],
            "gloss": (c["gloss"][:240] + " …[truncated]"
                      if len(c["gloss"]) > 240 else c["gloss"]),
            "n_trigger_phrases": len(c["triggers"]),
            "m_total": s[0],
            "m_stem": s[1],
            "m_unambiguous_lemma": s[2],
            "by_source": {k: s[3].get(k, 0) for k in SRC_KEYS if s[3].get(k)},
            "header_cue_collision": cid in hdr_cids,
            "greedy_disjoint_m8": cid in greedy_ok,
            "greedy_disjoint_m8_unambiguous": cid in greedy_ok_unamb,
            "rank_by_unambiguous": alt_rank[cid],
            "existing_alignment": sorted(aligned_to.get(c["urn"], [])) or None,
        }

    pool_out = {
        "name": "f1k-eligibility candidate pool (b)+(c) screen",
        "built": PASS_STAMP,
        "issue": "#33 (maintainer-authorized F1-K large-kernel rebuild)",
        "status": "SCREENED POOL for the codex (a)-design selection. NOT a "
                  "freeze, NOT a registry write. Criterion (a) explication "
                  "sourcing/quality is deferred to the design.",
        "criteria": {
            "b": "clean WordNet-3.1 alignment: pool = the census's "
                 "110,049 TYPE-LEVEL WN31 synsets (SOP-1; each IS its own "
                 "alignment). OBO/SUMO clusters excluded: no computed WN "
                 "crosswalk exists in-repo (disclosed, not padded).",
            "c": "m_total >= 8 admitted eval items with >= 1 trigger match "
                 "(SOP-2..4; the [BC] f1k-trigger-map machinery's mapping "
                 "rule, counted over question+options).",
        },
        "benchmark_blind": "item counting only; no model outcomes read",
        "ranking": "m_total desc, m_stem desc, urn asc. CAUTION for the "
                   "(a)-design: raw m_total is inflated for hyper-ambiguous "
                   "lemmas (single letters, function-word senses); use "
                   "rank_by_unambiguous / m_unambiguous_lemma and the "
                   "header_cue_collision flag when selecting (SOP-6).",
        "n_eligible": n_eligible,
        "candidates": [entry(i + 1, cid) for i, cid in enumerate(eligible)],
    }
    write_json(HERE / "candidate-pool.json", pool_out)

    # ---- coverage-report.json -----------------------------------------------
    m_vals = sorted((stats[cid][0] for cid in eligible), reverse=True)
    contention_hist = {str(k): v for k, v in sorted(contention.items())[:2]}
    contention_hist.update({
        "2-10": sum(v for k, v in contention.items() if 2 <= k <= 10),
        "11-100": sum(v for k, v in contention.items() if 11 <= k <= 100),
        ">100": sum(v for k, v in contention.items() if k > 100),
    })
    report = {
        "built": PASS_STAMP,
        "issue": "#33",
        "pool": {
            "census": "poc/scale/results/scale-s1-census.json",
            "unmerged_type_level_clusters": 207733,
            "wn31_type_level": n_pool,
            "wn31_instances_excluded": len(instance_urns),
            "obo_classes_excluded_no_wn_crosswalk": 95201,
            "sumo_classes_excluded_no_wn_crosswalk": 2483,
            "exclusion_basis": "census four_counts_S35."
                               "exactly_crosswalked_clusters = NOT COMPUTED; "
                               "data/onto-sumo carries no WordNet mappings "
                               "(grep-verified). A future crosswalk can only "
                               "ADD candidates that dedupe INTO WN synsets "
                               "already screened here, so the WN-only "
                               "screen is yield-complete for (b).",
        },
        "eval_sources": {
            "pins": "sha256-verified against [BC] SOURCES (fail closed)",
            "admitted_items": n_items,
            "by_source": dict(sorted(src_totals.items())),
        },
        "funnel": {
            "wn_aligned_pool_b": n_pool,
            "matching_ge_1_item": n_matched_any,
            "eligible_m_ge_8_c": n_eligible,
            "eligible_and_header_clean": n_eligible_clean,
            "eligible_m_unambiguous_ge_8": n_unamb8,
            "greedy_disjoint_C_lower_bound": c_disjoint,
            "greedy_disjoint_C_lower_bound_header_clean": c_disjoint_clean,
            "greedy_disjoint_C_lower_bound_unambiguous_header_clean":
                c_disjoint_unamb,
        },
        "gate_arithmetic": {
            "gate": "C >= %d clusters each m >= %d (ASM-2271, [REG])"
                    % (POWER_GATE_MIN_C, POWER_GATE_MIN_M),
            "raw_eligible_vs_gate": "%d >= %d: %s"
                % (n_eligible, POWER_GATE_MIN_C,
                   n_eligible >= POWER_GATE_MIN_C),
            "disjoint_bound_vs_gate": "%d >= %d: %s  (the honest number: "
                "counts clusters SIMULTANEOUSLY reaching m>=8 on disjoint "
                "items, SOP-5)"
                % (c_disjoint, POWER_GATE_MIN_C,
                   c_disjoint >= POWER_GATE_MIN_C),
            "headroom_target_100plus": "%d >= %d: %s (header-clean disjoint: "
                "%d)" % (c_disjoint, HEADROOM_TARGET,
                         c_disjoint >= HEADROOM_TARGET, c_disjoint_clean),
            "conservative_unambiguous_bound": "%d header-clean concepts "
                "reach m>=8 on DISJOINT items each matched via a monosemous "
                "direct lemma (SOP-5+SOP-6) — vs gate 65: %s, vs 100+ "
                "headroom: %s" % (c_disjoint_unamb,
                                  c_disjoint_unamb >= POWER_GATE_MIN_C,
                                  c_disjoint_unamb >= HEADROOM_TARGET),
            "adequacy_finding": (
                "POOL SUPPORTS THE GATE WITH HEADROOM (even on the "
                "conservative unambiguous-evidence bound)"
                if c_disjoint_unamb >= HEADROOM_TARGET else
                "POOL SUPPORTS THE GATE WITH HEADROOM"
                if c_disjoint_clean >= HEADROOM_TARGET else
                "POOL SUPPORTS THE GATE (headroom below the 100+ target)"
                if c_disjoint_clean >= POWER_GATE_MIN_C else
                "HARD ADEQUACY SHORTFALL: pool does NOT support C>=65 on "
                "disjoint items — report, do not invent coverage"),
        },
        "m_distribution_eligible": {
            "max": m_vals[0] if m_vals else 0,
            "p50": m_vals[len(m_vals) // 2] if m_vals else 0,
            "min": m_vals[-1] if m_vals else 0,
            "n_ge_16": sum(1 for m in m_vals if m >= 16),
            "n_ge_35": sum(1 for m in m_vals if m >= 35),
        },
        "item_contention_hist_concepts_per_item": contention_hist,
        "operationalisations": {
            "SOP-1": "pool = WN31 type-level only; OBO/SUMO excluded "
                     "(no computed crosswalk)",
            "SOP-2": "trigger surface = [BC build_triggers] rule verbatim "
                     "(synset lemmas + derivational '+' lemmas)",
            "SOP-3": "OP-4 matching over question+options only; header/cue/"
                     "label collisions FLAGGED per concept, not counted",
            "SOP-4": "(c) = m_total >= 8 (any-span availability, as [BC])",
            "SOP-5": "greedy scarcest-first disjoint assignment = lower "
                     "bound on simultaneous C at m >= 8",
            "SOP-6": "m_unambiguous_lemma = monosemous-direct-lemma "
                     "heuristic, cased/acronym WN source forms excluded "
                     "(AN/IT/WHO/OR-style function-word collisions); "
                     "screening aid, not a criterion",
        },
        "governance": {
            "benchmark_blind": True,
            "model_outcomes_read": False,
            "git_registry_freeze_spend": "none",
            "deterministic": "byte-identical on re-run; no RNG/wall-clock",
        },
        "outputs": {
            "candidate_pool": "poc/scale/f1k-eligibility/candidate-pool.json",
            "this_report": "poc/scale/f1k-eligibility/coverage-report.json",
        },
    }
    write_json(HERE / "coverage-report.json", report)

    # ---- self-check ----------------------------------------------------------
    print("\n=== GOVERNANCE SELF-CHECK ===")
    print("candidate concepts with WN alignment (b):        %d" % n_pool)
    print("candidates with >=8 eval items (c):              %d" % n_eligible)
    print("  of which header/cue-collision-free:            %d"
          % n_eligible_clean)
    print("  of which >=8 UNAMBIGUOUS-lemma items (SOP-6):  %d" % n_unamb8)
    print("disjoint-items C lower bound (honest headroom):  %d raw / %d "
          "header-clean / %d conservative-unambiguous"
          % (c_disjoint, c_disjoint_clean, c_disjoint_unamb))
    print(">=65 achievable: %s   >=100 headroom: %s   (conservative bound: "
          ">=65 %s, >=100 %s)"
          % (c_disjoint_clean >= POWER_GATE_MIN_C,
             c_disjoint_clean >= HEADROOM_TARGET,
             c_disjoint_unamb >= POWER_GATE_MIN_C,
             c_disjoint_unamb >= HEADROOM_TARGET))
    print("benchmark-blind: item counting only, no model outcomes read")
    print("colibri naming; no handles; no git/registry/freeze/spend; $0")
    print("candidate-pool.json: %s" % (HERE / "candidate-pool.json"))
    print("coverage-report.json: %s" % (HERE / "coverage-report.json"))


# ===========================================================================
# ASKABILITY MODE (issue #33 follow-on, bead 21er; $0, blind) — additive.
#
# `python3 screen_candidates.py askability` runs sol's 4-part F1-K askability
# screen (docs/next/design/f1k-askability-screen-sol-20260715.md): a model-
# outcome-BLIND, gold-label-BLIND feasibility GATE deciding whether the
# deciding kernel-vs-generic correctness experiment (F1-K rungs K-1/K-2/K-3)
# is BUILDABLE before any explication authoring or GPU spend.
#
# The default (no-arg) invocation above is UNCHANGED (the lyvi (b)+(c) screen,
# whose load_instance_urns predicate + pool are registry-pinned by ASM-2474/
# ASM-2493): this mode adds a SEPARATE entrypoint and writes ONLY under
# poc/scale/f1k-eligibility/askability/ (reports/ + contrast/) so nothing the
# lyvi screen owns (candidate-pool.json, coverage-report.json) is touched.
#
# This is a faithful transcription of the prior verified realization
#   [ASK31] poc/f1k-askability/screen.py — "2026-07-15 designer-31 f1k-
#           askability screen" — re-homed into the eligibility screener the
#           bead directs it to extend, with byte-identical operationalisations
#           so the numbers reproduce. Every rule still cites its frozen source:
#   [BC]  poc/glm52-probe/f1k-harness/corpora/build_corpora.py — WN3.1 parse,
#         trigger surface expansion, §R4 overlap resolution, render_template,
#         the production prepend rule (payload + '\n\n' + template).
#   [KV0] data/kernel-v0/ (54 concepts; gloss + kot-ast/1) +
#         data/lexical-wn31/alignment-kernel-v0.json (kernel-v0 -> WN synset).
#   [KV1] data/kernel-v1/ (100 concepts; gloss + kot-ast/1 + inline synset).
#   [WN]  data/lexical-wn31/source/dict/ — the matched dictionary gloss.
#   [EV]  data/f1k-eval-v1/source/*.parquet — 5 pinned benchmarks (sha256
#         fail-closed vs [BC] SOURCES); ONLY {item_id, source, question,
#         options} survive into the redacted view (gold used for [BC]
#         well-formedness admission then DROPPED — never stored/ranked).
#   [REG] registry/experiments/f1k.json — K-1/K-2/K-3 endpoints, joint rule
#         (lift >= +3 pts AND cluster sign-flip p<0.05), power gate C>=65 each
#         m>=8 at n=1440, seed 20260713, B=10000. READ ONLY.
#   [DES] docs/next/design/glm52-followup-experiment.md §R-REV5 — the frozen
#         pre-spend Monte-Carlo EXACT-test joint-power procedure (mu*=+4.09
#         pts, rho_U=0.10, exchangeable within-cluster correlation, >=0.80).
# Deterministic: byte-identical on re-run; only PRNG is the registered power
# seed 20260713. colibri naming; no handles; $0; no GPU/network/spend/freeze.
# ===========================================================================

ASK_PASS_STAMP = "2026-07-19 designer-21er f1k-askability screen ($0, blind)"

# ---- frozen constants (cited) ---------------------------------------------
ASK_DEV_N = 96             # [REG n_planned.dev_split_items]
ASK_N_TEST = 1440          # [REG n_planned.n_test_items — runs AT the cap]
ASK_MIN_M = POWER_GATE_MIN_M       # 8 [REG power_gate]; reuse the module const
ASK_SELECT_N = 96          # [SPEC 1] select 96
ASK_RESERVE_N = 30         # [SPEC 1] retain the next 30 as a fixed reserve
ASK_NLD_MIN = 0.20         # [SPEC 2] distinctness bar
ASK_C_LO, ASK_C_HI = 80, 100       # [SPEC 4] ASKABLE band on the operating C
ASK_PREFIX_LO = 65         # [SPEC 3] sweep from the registered power gate C>=65
# power-sim constants [DES §R-REV5 / REG statistics]
ASK_POWER_SEED = 20260713  # [REG statistics global PRNG seed]
ASK_N_SIM = 10000          # [DES §R-REV5 N_sim]
ASK_B_FLIP = 10000         # [REG B / DES §R-REV5: 10,000 sign-flips]
ASK_DELTA = 0.10           # [DES §R-REV4.1(b): per-item paired-diff variance]
ASK_RHO_U = 0.10           # [DES §R-REV5: conservative planning rho_U]
ASK_MU_STAR = 0.0409       # [DES §R-REV4.1(b): mu* = +4.09 pts]
ASK_T_FIRE = 0.03          # [REG joint rule: observed lift >= +3.0 pts]
ASK_POWER_MIN = 0.80       # [DES §R-REV5 pass threshold]
# R = number of deflator/comparator passes per rung [REG endpoints]:
#   K-1 (K vs b0) R=1 ; K-2 (K vs mean over R=3 drng) R=3 ; K-3 (K vs d2) R=1
ASK_CONTRASTS = [("K-1", 1), ("K-2", 3), ("K-3", 1)]
ASK_ERR = "ERR_F1K_ASK"


def _ask_fail(msg):
    print("%s: %s" % (ASK_ERR, msg), file=sys.stderr)
    sys.exit(2)


def _ask_sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def _ask_write_text(path, text):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        f.write(text if isinstance(text, bytes) else text.encode("utf-8"))


def _ask_slug(urn):
    return urn.split(":")[-1].replace("/", "_")


# --- Levenshtein + NLD (NFC-normalised) [SPEC 2] ---------------------------
def _ask_levenshtein(a, b):
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1,
                           prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def _ask_nld(k, d):
    """NLD_c = Lev(NFC(K), NFC(D)) / max(|K|, |D|)  [SPEC 2]."""
    import unicodedata
    kn = unicodedata.normalize("NFC", k)
    dn = unicodedata.normalize("NFC", d)
    denom = max(len(kn), len(dn))
    if denom == 0:
        return 0.0
    return _ask_levenshtein(kn, dn) / denom


# --- existing-kernel record join (kernel-v0 + kernel-v1) [SPEC 1/KV0,KV1] --
def _ask_ast_parseable(expl, kc):
    """kot-ast/1 explication 'parseable' iff a JSON object bearing schema
    'kot-ast/1', a non-empty clause list, and JCS-canonicalising without error
    (the exact bytes kernel.ast.json ships)."""
    if not isinstance(expl, dict) or expl.get("schema") != "kot-ast/1":
        return False, None
    if not isinstance(expl.get("clauses"), list) or not expl["clauses"]:
        return False, None
    try:
        ast_bytes = kc.canonical_bytes(expl)
    except Exception:
        return False, None
    return True, ast_bytes


def _ask_load_kernel_records():
    """kernel-v0 (via alignment) + kernel-v1 (inline synset), deduped by
    synset (v1 preferred on collision; disjoint in fact). [SPEC 1/KV0,KV1]."""
    recs = []
    align = json.load(open(ROOT / "data" / "lexical-wn31" /
                           "alignment-kernel-v0.json", encoding="utf-8"))
    v0syn = {a["concept"]: a["synset"] for a in align["alignments"]
             if a["concept"].startswith("urn:kernel-v0:")}
    cdir = ROOT / "data" / "kernel-v0" / "concepts"
    for fn in sorted(os.listdir(cdir)):
        d = json.load(open(cdir / fn, encoding="utf-8"))
        recs.append({"urn": d["id"], "label": d.get("label", ""),
                     "gloss": d.get("gloss", ""),
                     "explication": d.get("explication"),
                     "synset": v0syn.get(d["id"]), "source": "kernel-v0"})
    cdir = ROOT / "data" / "kernel-v1" / "concepts"
    for fn in sorted(os.listdir(cdir)):
        d = json.load(open(cdir / fn, encoding="utf-8"))
        recs.append({"urn": d["id"], "label": d.get("label", ""),
                     "gloss": d.get("gloss", ""),
                     "explication": d.get("explication"),
                     "synset": d.get("synset"), "source": "kernel-v1"})
    by_syn, dup = {}, 0
    for r in sorted(recs, key=lambda r: (0 if r["source"] == "kernel-v1"
                                         else 1, r["urn"])):
        s = r["synset"]
        if not s:
            continue
        if s in by_syn:
            dup += 1
            continue
        by_syn[s] = r
    return list(by_syn.values()), len(recs), dup


# --- redacted benchmark loader [SPEC 1 / EV / BC admission] -----------------
#   Returns the REDACTED view {item_id, source, question, options} only.
#   ALLOWLIST ENFORCED: gold is read ONLY for the [BC] well-formedness
#   admission and is never stored on the returned item (no gold/pred/logit/
#   K/pilot/derangement field ever materialises).
def _ask_load_items_redacted(bc):
    import pyarrow.parquet as pq
    src_dir = ROOT / "data" / "f1k-eval-v1" / "source"
    items = []
    for rank, (key, ds, rev, path, want, split) in enumerate(bc.SOURCES):
        p = src_dir / ("%s.parquet" % key)
        if not p.exists():
            _ask_fail("pinned snapshot %s missing" % p)
        h = hashlib.sha256()
        with open(p, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        if h.hexdigest() != want:
            _ask_fail("source %s sha256 mismatch vs [BC] pin — STOP" % key)
        rows = pq.read_table(p).to_pylist()
        for ri, r in enumerate(rows):
            if key == "mmlu":
                q = r["question"].strip()
                opts = [o.strip() for o in r["choices"]]
                gold = int(r["answer"])              # ADMISSION ONLY
                native = "%s/%d" % (r["subject"], ri)
            else:
                q = (r.get("question") or r.get("question_stem")).strip()
                ch = r["choices"]
                opts = [o.strip() for o in ch["text"]]
                labels_pub = list(ch["label"])
                if r["answerKey"] not in labels_pub:
                    continue
                gold = labels_pub.index(r["answerKey"])   # ADMISSION ONLY
                native = str(r["id"])
            if not (3 <= len(opts) <= 5) or not (0 <= gold < len(opts)):
                continue                             # [BC] well-formedness
            # gold DROPPED here — never stored on the redacted item
            items.append({"item_id": "%s#%s" % (key, native),
                          "source": key, "source_rank": rank, "row_index": ri,
                          "question": q, "options": opts})
    return items


ASK_ALLOWED_ITEM_FIELDS = frozenset(
    {"item_id", "source", "question", "options"})   # [SPEC 1] redacted allowlist
ASK_FORBIDDEN_ITEM_FIELDS = (
    "gold", "gold_index", "answer", "answerKey", "label", "prediction",
    "pred", "logit", "logits", "accuracy", "correct", "baseline", "K",
    "pilot", "derangement")


def _ask_assert_redacted(view):
    """Fail closed if any redacted item carries a field outside the [SPEC 1]
    allowlist or any forbidden outcome field (the code-level enforcement the
    bead requires: no gold/pred/logit/K/pilot field is readable downstream)."""
    for it in view:
        extra = set(it.keys()) - ASK_ALLOWED_ITEM_FIELDS
        if extra:
            _ask_fail("redacted view carries non-allowlisted field(s) %s — "
                      "STOP (allowlist = %s)" % (sorted(extra),
                                                 sorted(ASK_ALLOWED_ITEM_FIELDS)))
        for f in ASK_FORBIDDEN_ITEM_FIELDS:
            if f in it:
                _ask_fail("redacted view carries forbidden outcome field %r "
                          "— STOP" % f)


# --- §R4 span helpers over an arbitrary concept subset [BC] -----------------
def _ask_raw_candidates(text, matchers, bc):
    low = text.lower()
    words = set(bc.WORD_RE.findall(low))
    cand = []
    for w in words:
        for ph, rx, cidx in matchers.get(w, ()):
            if ph.split()[0] != w:
                continue
            for m in rx.finditer(text):
                cand.append((m.start(), m.end(), cidx))
    return cand


def _ask_resolve(cands, allowed):
    """§R4 precedence over cands whose concept is in `allowed`: longest, then
    earliest start, then lowest concept index; non-overlapping. [BC find_spans]."""
    cand = [c for c in cands if c[2] in allowed]
    cand.sort(key=lambda s: (-(s[1] - s[0]), s[0], s[2]))
    taken, out = [], []
    for s in cand:
        if any(not (s[1] <= t[0] or s[0] >= t[1]) for t in taken):
            continue
        taken.append(s)
        out.append(s)
    out.sort(key=lambda s: s[0])
    return out


# --- cluster allocation (dev-96 + test to m=8 / n=1440) [BC OP-6] -----------
def _ask_allocate(prefix_cidx, item_cands, items, q_end):
    allowed = set(prefix_cidx)
    by_cluster = {c: [] for c in prefix_cidx}
    for ii, it in enumerate(items):
        cands = item_cands.get(ii)
        if not cands:
            continue
        spans = _ask_resolve(cands, allowed)
        if not spans:
            continue
        cluster = spans[0][2]                        # [BC OP-6a] leftmost resolved
        stem = spans[0][0] < q_end[ii]
        by_cluster[cluster].append((0 if stem else 1, it["source_rank"],
                                    it["row_index"], ii))
    for c in by_cluster:
        by_cluster[c].sort()
    used = {c: 0 for c in prefix_cidx}

    def take(c):
        if used[c] < len(by_cluster[c]):
            used[c] += 1
            return True
        return False

    dev = {c: 0 for c in prefix_cidx}
    ndev = 0
    while ndev < ASK_DEV_N:
        progressed = False
        for c in prefix_cidx:
            if ndev >= ASK_DEV_N:
                break
            if take(c):
                dev[c] += 1
                ndev += 1
                progressed = True
        if not progressed:
            break
    test = {c: 0 for c in prefix_cidx}
    ntest = 0
    for _ in range(ASK_MIN_M):
        for c in prefix_cidx:
            if ntest >= ASK_N_TEST:
                break
            if take(c):
                test[c] += 1
                ntest += 1
    progressing = True
    while ntest < ASK_N_TEST and progressing:
        progressing = False
        for c in prefix_cidx:
            if ntest >= ASK_N_TEST:
                break
            if take(c):
                test[c] += 1
                ntest += 1
                progressing = True
    return test, dev, ntest, ndev


# --- EXACT cluster sign-flip Monte-Carlo joint-power sim [DES §R-REV5] ------
def _ask_power_seed(contrast, C):
    h = hashlib.sha256(("%d|%s|C%d" % (ASK_POWER_SEED, contrast, C)).encode())
    return int(h.hexdigest()[:16], 16)


def _ask_power_curve(m_list, contrast, mus, chunk=2500):
    """Joint power of the EXACT cluster sign-flip test (fire iff permutation
    p<0.05 AND observed mean lift T>=+3 pts) at every mu in `mus`, under the
    [DES §R-REV5] exchangeable alternative: per cluster c the cluster mean
    D_c ~ N(mu, delta*(rho + (1-rho)/m_c)). N_sim synthetic datasets scored
    against ONE frozen b-row +-1 sign-flip reference matrix per (contrast, C)
    with common random numbers (variance reduction; unbiased power estimate).
    add-one p = (1+ge)/(B+1); p<0.05 <=> ge <= 499 at B=10000."""
    import numpy as np
    C = len(m_list)
    v = ASK_DELTA * (ASK_RHO_U + (1.0 - ASK_RHO_U)
                     / np.asarray(m_list, dtype=np.float64))
    sd = np.sqrt(v)
    rng = np.random.default_rng(_ask_power_seed(contrast, C))
    noise = rng.standard_normal((ASK_N_SIM, C)) * sd[None, :]
    noise_mean = noise.mean(axis=1)
    Z = (rng.integers(0, 2, size=(ASK_B_FLIP, C), dtype=np.int8).astype(np.float64)
         * 2.0 - 1.0)
    rowsum = Z.sum(axis=1)
    ge_cut = 499
    fire = {mu: 0 for mu in mus}
    for start in range(0, ASK_N_SIM, chunk):
        end = min(start + chunk, ASK_N_SIM)
        nz = noise[start:end]
        zn = Z @ nz.T
        nm = noise_mean[start:end]
        for mu in mus:
            tb = (mu * rowsum[:, None] + zn) / C
            tobs = mu + nm
            ge = (tb >= tobs[None, :]).sum(axis=0)
            fired = (ge <= ge_cut) & (tobs >= ASK_T_FIRE)
            fire[mu] += int(fired.sum())
    return {mu: fire[mu] / ASK_N_SIM for mu in mus}


def _ask_mde_from_curve(mus, curve):
    """Smallest mu whose joint power >= 0.80, linearly interpolated between the
    bracketing grid points. None if the grid never reaches 0.80."""
    ordered = sorted(mus)
    prev_mu, prev_p = None, None
    for mu in ordered:
        p = curve[mu]
        if p >= ASK_POWER_MIN:
            if prev_mu is None or prev_p is None or prev_p >= ASK_POWER_MIN:
                return mu
            frac = (ASK_POWER_MIN - prev_p) / (p - prev_p)
            return prev_mu + frac * (mu - prev_mu)
        prev_mu, prev_p = mu, p
    return None


def main_askability():
    import numpy as np
    sys.path.insert(0, str(ROOT / "poc" / "glm52-probe" / "f1k-harness"
                           / "corpora"))
    sys.path.insert(0, str(ROOT / "tools" / "registry"))
    import build_corpora as bc                     # [BC] parse/triggers/spans/render
    import kot_common as kc                        # JCS canonical bytes

    OUT = HERE / "askability"
    REP = OUT / "reports"
    print("=" * 72)
    print("F1-K/K-3 askability + coverage screen ($0, blind) — %s"
          % ASK_PASS_STAMP)
    print("=" * 72)

    # ---- PART 1 — pool + selection --------------------------------------
    print("\n[PART 1] pool + selection")
    wn = bc.parse_wn_dict()
    recs, n_raw, n_dup = _ask_load_kernel_records()
    print("  joined kernel-v0+v1 records: %d raw -> %d synset-deduped "
          "(%d dropped)" % (n_raw, len(recs), n_dup))
    bc.build_triggers(recs, wn)

    pool = []
    rej = {"no_gloss": 0, "no_ast": 0, "no_wn_gloss": 0, "no_triggers": 0}
    for r in recs:
        ok, ast_bytes = _ask_ast_parseable(r["explication"], kc)
        if not (r["gloss"] and r["gloss"].strip()):
            rej["no_gloss"] += 1
            continue
        if not ok:
            rej["no_ast"] += 1
            continue
        if not (r.get("d2_gloss") and r["d2_gloss"].strip()):
            rej["no_wn_gloss"] += 1
            continue
        if not r["triggers"]:
            rej["no_triggers"] += 1
            continue
        r["ast_bytes"] = ast_bytes
        pool.append(r)
    for i, r in enumerate(pool):
        r["index"] = i
    print("  retention pre-filter: %d records pass gloss+ast+WNgloss+triggers "
          "(rej %s)" % (len(pool), rej))

    matchers = bc.compile_matchers(pool)

    hdr_cids = set()
    for text in (bc.HEADER, bc.CUE, " ".join(bc.LABEL_ALPHABET)):
        for (_s, _e, cidx) in _ask_raw_candidates(text, matchers, bc):
            hdr_cids.add(cidx)
    print("  header/cue/label collisions: %d concepts flagged (excluded)"
          % len(hdr_cids))

    # redacted benchmark items + freeze the redacted-input hash BEFORE screening
    items = _ask_load_items_redacted(bc)
    redacted_view = [{"item_id": it["item_id"], "source": it["source"],
                      "question": it["question"], "options": it["options"]}
                     for it in sorted(items, key=lambda x: x["item_id"])]
    _ask_assert_redacted(redacted_view)              # fail-closed allowlist gate
    redacted_hash = _ask_sha256_bytes(kc.canonical_bytes(redacted_view))
    rules = {
        "retention_filter": ["existing kernel gloss", "parseable kot-ast/1",
                             "aligned WordNet dictionary gloss",
                             "clean triggers (>=1, WORD_RE-valid)",
                             "no header/cue/label collision",
                             "projected m_test >= 8"],
        "ranking_keys": ["projected_m_test desc", "exclusive_stem_hits desc",
                         "exclusive_total_hits desc", "collision_fraction asc",
                         "synset_urn_bytes asc"],
        "select_n": ASK_SELECT_N, "reserve_n": ASK_RESERVE_N,
        "nld_min": ASK_NLD_MIN, "power_gate_min_m": ASK_MIN_M,
        "n_test": ASK_N_TEST, "dev_n": ASK_DEV_N,
        "redacted_input_allowlist": sorted(ASK_ALLOWED_ITEM_FIELDS),
        "prepend_renderer": "payload + '\\n\\n' + [BC §R1.1 template] "
                            "(the production d3-text rule, [BC] OP-9)",
        "power": {"seed": ASK_POWER_SEED, "n_sim": ASK_N_SIM,
                  "b_flip": ASK_B_FLIP, "delta": ASK_DELTA, "rho_u": ASK_RHO_U,
                  "mu_star": ASK_MU_STAR, "t_fire": ASK_T_FIRE,
                  "power_min": ASK_POWER_MIN,
                  "R_per_contrast": {c: r for c, r in ASK_CONTRASTS}},
        "verdict_band_C": [ASK_C_LO, ASK_C_HI], "prefix_lo": ASK_PREFIX_LO,
    }
    rules_hash = _ask_sha256_bytes(kc.canonical_bytes(rules))
    print("  redacted-input FROZEN: %d items, hash %s… ; rules hash %s…"
          % (len(items), redacted_hash[:12], rules_hash[:12]))

    item_cands = {}
    q_end = {}
    for ii, it in enumerate(items):
        tpl = bc.render_template(it["question"], it["options"])
        it["template_text"] = tpl
        q_end[ii] = len(bc.HEADER) + len(it["question"])
        cands = _ask_raw_candidates(tpl, matchers, bc)
        if cands:
            item_cands[ii] = cands

    allowed_all = set(range(len(pool)))
    raw_match = [0] * len(pool)
    excl = [0] * len(pool)
    excl_stem = [0] * len(pool)
    for ii, cands in item_cands.items():
        for (_s, _e, cidx) in cands:
            raw_match[cidx] += 1
        spans = _ask_resolve(cands, allowed_all)
        if spans:
            win = spans[0][2]
            excl[win] += 1
            if spans[0][0] < q_end[ii]:
                excl_stem[win] += 1
    for r in pool:
        i = r["index"]
        r["raw_match"] = raw_match[i]
        r["excl_total"] = excl[i]
        r["excl_stem"] = excl_stem[i]
        r["collision_fraction"] = (round((raw_match[i] - excl[i]) /
                                         raw_match[i], 6) if raw_match[i] else 0.0)
        r["projected_m_test"] = excl[i]
        r["header_cue_collision"] = i in hdr_cids

    survivors = [r for r in pool
                 if r["projected_m_test"] >= ASK_MIN_M
                 and not r["header_cue_collision"]]
    survivors.sort(key=lambda r: (-r["projected_m_test"], -r["excl_stem"],
                                  -r["excl_total"], r["collision_fraction"],
                                  r["synset"].encode("utf-8")))
    for i, r in enumerate(survivors):
        r["rank"] = i + 1
    n_surv = len(survivors)
    selected = survivors[:ASK_SELECT_N]
    reserve = survivors[ASK_SELECT_N:ASK_SELECT_N + ASK_RESERVE_N]
    print("  survivors (projected m>=8, header-clean): %d" % n_surv)
    print("  selected: %d ; reserve: %d" % (len(selected), len(reserve)))

    def cand_entry(r):
        return {"rank": r["rank"], "urn": r["urn"], "source": r["source"],
                "label": r["label"], "synset": r["synset"],
                "pos": bc.synset_key(r["synset"])[0],
                "projected_m_test": r["projected_m_test"],
                "raw_match": r["raw_match"], "excl_stem": r["excl_stem"],
                "collision_fraction": r["collision_fraction"],
                "n_triggers": len(r["triggers"])}

    write_json(REP / "candidate-report.json", {
        "part": "1 — pool + selection", "built": ASK_PASS_STAMP,
        "spec": "docs/next/design/f1k-askability-screen-sol-20260715.md",
        "reference_realization": "poc/f1k-askability/screen.py [ASK31]",
        "kernel_records_joined_raw": n_raw,
        "synset_deduped_records": len(recs),
        "dedup_dropped": n_dup,
        "retention_pre_filter_pass": len(pool),
        "retention_pre_filter_rej": rej,
        "header_cue_collisions_flagged": len(hdr_cids),
        "redacted_items": len(items),
        "redacted_input_allowlist": sorted(ASK_ALLOWED_ITEM_FIELDS),
        "survivors_projected_m8_header_clean": n_surv,
        "selected_count": len(selected), "reserve_count": len(reserve),
        "reserve_target": ASK_RESERVE_N,
        "selected": [cand_entry(r) for r in selected],
        "reserve": [cand_entry(r) for r in reserve],
        "source_mix_selected": {k: sum(1 for r in selected if r["source"] == k)
                                for k in ("kernel-v0", "kernel-v1")},
        "MEASURED": "counts are exact over the pinned corpora + benchmarks",
    })

    # ---- PART 2 — contrast (condition iv) -------------------------------
    print("\n[PART 2] contrast / distinctness certification")
    contrast_rows = []
    prompt_pairs_total = 0
    prompt_pairs_diff = 0
    outside_payload_diff_total = 0
    sel_idx = [r["index"] for r in selected + reserve]
    sel_allowed = set(sel_idx)
    assigned = {c: [] for c in sel_idx}
    for ii, cands in item_cands.items():
        spans = _ask_resolve(cands, sel_allowed)
        if spans:
            assigned[spans[0][2]].append(ii)

    all_pass = True
    for r in selected + reserve:
        i = r["index"]
        k_text = r["gloss"]
        d_text = r["d2_gloss"]
        ast_bytes = r["ast_bytes"]
        k_bytes = k_text.encode("utf-8")
        d_bytes = d_text.encode("utf-8")
        k_hash = _ask_sha256_bytes(k_bytes)
        d_hash = _ask_sha256_bytes(d_bytes)
        ast_hash = _ask_sha256_bytes(ast_bytes)
        nld_c = _ask_nld(k_text, d_text)
        hashes_differ = (k_hash != d_hash)
        n_items = 0
        n_diff = 0
        opd = 0
        for ii in assigned[i]:
            tpl = items[ii]["template_text"]
            k_prompt = (k_text + "\n\n" + tpl).encode("utf-8")
            d_prompt = (d_text + "\n\n" + tpl).encode("utf-8")
            n_items += 1
            if _ask_sha256_bytes(k_prompt) != _ask_sha256_bytes(d_prompt):
                n_diff += 1
            if k_prompt[len(k_bytes):] != d_prompt[len(d_bytes):]:
                opd += 1
        prompt_pairs_total += n_items
        prompt_pairs_diff += n_diff
        outside_payload_diff_total += opd
        phdr = (n_diff / n_items) if n_items else 1.0
        passed = (hashes_differ and nld_c >= ASK_NLD_MIN and phdr == 1.0
                  and opd == 0 and n_items > 0)
        r["contrast_pass"] = passed
        if r in selected and not passed:
            all_pass = False
        d = OUT / "contrast" / ("%03d-%s" % (r["rank"], _ask_slug(r["urn"])))
        _ask_write_text(d / "kernel.txt", k_bytes)
        _ask_write_text(d / "kernel.ast.json", ast_bytes)
        _ask_write_text(d / "dictionary.txt", d_bytes)
        contrast_rows.append({
            "rank": r["rank"], "urn": r["urn"], "source": r["source"],
            "synset": r["synset"], "in_selected": r in selected,
            "kernel_sha256": k_hash, "kernel_ast_sha256": ast_hash,
            "dictionary_sha256": d_hash, "hashes_differ": hashes_differ,
            "kernel_len": len(k_text), "dictionary_len": len(d_text),
            "NLD_c": round(nld_c, 6), "nld_pass": nld_c >= ASK_NLD_MIN,
            "assigned_items": n_items,
            "prompt_hash_diff_rate": round(phdr, 6),
            "outside_payload_diff": opd, "contrast_pass": passed})

    sel_rows = [x for x in contrast_rows if x["in_selected"]]
    nlds = sorted(x["NLD_c"] for x in sel_rows)
    n_contrast_pass = sum(1 for x in sel_rows if x["contrast_pass"])
    C_contrast = n_contrast_pass
    global_phdr = (prompt_pairs_diff / prompt_pairs_total
                   if prompt_pairs_total else 0.0)
    print("  selected concepts passing contrast (C_contrast): %d/%d"
          % (C_contrast, len(sel_rows)))
    print("  NLD over selected: min %.3f  median %.3f  max %.3f"
          % (nlds[0], nlds[len(nlds) // 2], nlds[-1]))
    print("  prompt-hash-diff-rate (all rendered pairs): %.6f ; "
          "outside-payload-diff total: %d"
          % (global_phdr, outside_payload_diff_total))

    write_json(REP / "distinctness-report.json", {
        "part": "2 — contrast (condition iv)", "built": ASK_PASS_STAMP,
        "nld_min": ASK_NLD_MIN,
        "selected_pass_contrast": C_contrast,
        "selected_total": len(sel_rows),
        "nld_selected": {"min": nlds[0], "median": nlds[len(nlds) // 2],
                         "max": nlds[-1]},
        "nld_pass_rate": round(sum(1 for x in sel_rows
                                   if x["nld_pass"]) / len(sel_rows), 6),
        "concepts": contrast_rows,
        "MEASURED": "exact Levenshtein NLD over NFC-normalised bytes",
    })
    write_json(REP / "hash-report.json", {
        "part": "2 — contrast certification + input freeze",
        "built": ASK_PASS_STAMP,
        "redacted_input_hash_frozen_before_screen": redacted_hash,
        "rules_hash": rules_hash,
        "rules": rules,
        "prepend_renderer": rules["prepend_renderer"],
        "rendered_prompt_pairs_total": prompt_pairs_total,
        "prompt_hash_difference_rate": round(global_phdr, 8),
        "prompt_hash_difference_rate_is_1": global_phdr == 1.0,
        "outside_payload_diff_total": outside_payload_diff_total,
        "outside_payload_diff_is_0": outside_payload_diff_total == 0,
        "all_selected_hashes_differ": all(x["hashes_differ"] for x in sel_rows),
        "certification": ("PASS: hashes differ, NLD>=0.20, prompt-hash-diff-"
                          "rate==1.00, outside-payload-diff==0"
                          if (all_pass and global_phdr == 1.0
                              and outside_payload_diff_total == 0)
                          else "PARTIAL — see distinctness-report.json"),
    })

    # ---- PART 3 — coverage / power sweep --------------------------------
    print("\n[PART 3] coverage + exact-power sweep")
    pass_selected = [r for r in selected if r["contrast_pass"]]
    ranked_cidx = [r["index"] for r in pass_selected]
    prefix_hi = min(ASK_C_HI, C_contrast)
    mu_grid = sorted(set([round(x, 5) for x in
                          np.arange(0.030, 0.05201, 0.002)] + [ASK_MU_STAR]))

    coverage_rows = []
    power_rows = []
    smallest_passing = None
    for C in range(ASK_PREFIX_LO, prefix_hi + 1):
        prefix = ranked_cidx[:C]
        test, dev, ntest, ndev = _ask_allocate(prefix, item_cands, items, q_end)
        m_list = [test[c] for c in prefix]
        m_min = min(m_list)
        m_mean = round(sum(m_list) / C, 4)
        cov_ok = (m_min >= ASK_MIN_M and ntest == ASK_N_TEST)
        coverage_rows.append({
            "C": C, "n_test": ntest, "n_dev": ndev, "m_min": m_min,
            "m_mean": m_mean, "m_max": max(m_list),
            "every_m_ge_8": m_min >= ASK_MIN_M,
            "coverage_ok": cov_ok})
        prow = {"C": C, "m_min": m_min, "m_mean": m_mean,
                "coverage_ok": cov_ok, "contrasts": {}}
        all3 = cov_ok
        for name, R in ASK_CONTRASTS:
            curve = _ask_power_curve(m_list, name, mu_grid)
            p_star = curve[ASK_MU_STAR]
            mc_se = round((p_star * (1 - p_star) / ASK_N_SIM) ** 0.5, 5)
            mde = _ask_mde_from_curve(mu_grid, curve)
            prow["contrasts"][name] = {
                "R": R, "power_at_mu_star": round(p_star, 4),
                "mc_se": mc_se,
                "mde_80pct_power": (round(mde, 5) if mde is not None else None),
                "power_ge_0.80": p_star >= ASK_POWER_MIN}
            if p_star < ASK_POWER_MIN:
                all3 = False
        prow["all_three_power_ge_0.80"] = all3
        prow["prefix_passes"] = all3 and cov_ok
        power_rows.append(prow)
        if prow["prefix_passes"] and smallest_passing is None:
            smallest_passing = C
        print("  C=%2d m_min=%2d m_mean=%5.2f  K-1=%.3f K-2=%.3f K-3=%.3f  %s"
              % (C, m_min, m_mean,
                 prow["contrasts"]["K-1"]["power_at_mu_star"],
                 prow["contrasts"]["K-2"]["power_at_mu_star"],
                 prow["contrasts"]["K-3"]["power_at_mu_star"],
                 "PASS" if prow["prefix_passes"] else "-"))

    write_json(REP / "coverage-report.json", {
        "part": "3 — coverage allocation", "built": ASK_PASS_STAMP,
        "prefixes": coverage_rows,
        "note": "per prefix C: dev-96 round-robin then test breadth-first to "
                "m=8 then round-robin to n=1440 ([BC] OP-6), realized over the "
                "rank-ordered contrast-passing selected concepts",
    })
    write_json(REP / "power-report.json", {
        "part": "3 — exact sign-flip Monte-Carlo joint power",
        "built": ASK_PASS_STAMP,
        "procedure": "DES §R-REV5 exact cluster sign-flip joint-power sim "
                     "(fire iff perm p<0.05 AND observed lift >=+3 pts)",
        "params": {"seed": ASK_POWER_SEED, "n_sim": ASK_N_SIM,
                   "b_flip": ASK_B_FLIP, "delta": ASK_DELTA, "rho_u": ASK_RHO_U,
                   "mu_star": ASK_MU_STAR, "t_fire_pts": 3.0,
                   "power_min": ASK_POWER_MIN,
                   "R_per_contrast": {c: r for c, r in ASK_CONTRASTS}},
        "prefix_range": [ASK_PREFIX_LO, prefix_hi],
        "C_contrast": C_contrast,
        "smallest_passing_prefix": smallest_passing,
        "prefixes": power_rows,
        "STIPULATED": "R=1,3,1 recorded as rung metadata; all three rungs "
                      "share the registered planning delta=0.10 (the record "
                      "assigns one per-item paired-diff variance to the F1-K "
                      "rungs) — for K-2 (R=3 deflator averaging) this is the "
                      "CONSERVATIVE choice (averaging only lowers variance). "
                      "One frozen b=10000 sign-flip matrix per (contrast,C), "
                      "common random numbers across the 10000 datasets "
                      "(unbiased power estimate).",
        "MEASURED": "Monte-Carlo joint power; MC-SE = sqrt(p(1-p)/N_sim)",
    })

    # ---- PART 4 — verdict ----------------------------------------------
    print("\n[PART 4] verdict")
    supply_ok = C_contrast >= ASK_C_LO
    operating_C = None
    if smallest_passing is not None:
        operating_C = max(ASK_C_LO, smallest_passing)
        if operating_C > prefix_hi:
            operating_C = None
    if operating_C is not None and ASK_C_LO <= operating_C <= ASK_C_HI:
        row = next(p for p in power_rows if p["C"] == operating_C)
        cov = next(c for c in coverage_rows if c["C"] == operating_C)
        askable = (row["prefix_passes"] and cov["every_m_ge_8"]
                   and all_pass and ASK_C_LO <= operating_C <= ASK_C_HI)
        verdict = "ASKABLE" if askable else "NOT-ASKABLE-AT-SCALE"
    elif not supply_ok:
        verdict = "NEEDS-MORE-INVENTORY"
    else:
        verdict = "NOT-ASKABLE-AT-SCALE"

    top = power_rows[-1] if power_rows else None
    headline_C = prefix_hi
    headline_power = (top["contrasts"]["K-3"]["power_at_mu_star"]
                      if top else None)

    verdict_obj = {
        "part": "4 — verdict", "built": ASK_PASS_STAMP,
        "verdict": verdict,
        "operating_C": operating_C,
        "C_contrast_selected_passing": C_contrast,
        "supply_contrasting_pairs_ge_80": supply_ok,
        "smallest_passing_prefix": smallest_passing,
        "prefix_hi_min100_Ccontrast": prefix_hi,
        "all_selected_pass_contrast": all_pass,
        "verdict_rule": ("ASKABLE iff 80<=C<=100 AND every m_c>=8 AND all "
                         "pass contrast AND all 3 power gates (K-1/K-2/K-3) "
                         ">=0.80; NEEDS-MORE-INVENTORY if <80 contrasting "
                         "pairs survive; NOT-ASKABLE-AT-SCALE if no C<=100 "
                         "geometry powers all contrasts"),
        "headline": {
            "note": "the single most important number",
            "C": headline_C,
            "K-3_joint_power_at_mu_star_+4.09pts": headline_power,
        },
        "reports": {
            "candidate": "poc/scale/f1k-eligibility/askability/reports/"
                         "candidate-report.json",
            "distinctness": "poc/scale/f1k-eligibility/askability/reports/"
                            "distinctness-report.json",
            "hash": "poc/scale/f1k-eligibility/askability/reports/"
                    "hash-report.json",
            "coverage": "poc/scale/f1k-eligibility/askability/reports/"
                        "coverage-report.json",
            "power": "poc/scale/f1k-eligibility/askability/reports/"
                     "power-report.json",
        },
        "governance": {"gold_label_blind": True, "model_outcome_blind": True,
                       "gpu": "none", "spend_usd": 0.0, "network": "none",
                       "git_registry_freeze": "none",
                       "deterministic": "byte-identical on re-run"},
    }
    write_json(REP / "verdict-report.json", verdict_obj)

    print("  VERDICT: %s   (operating C=%s, C_contrast=%d, smallest passing "
          "prefix=%s)" % (verdict, operating_C, C_contrast, smallest_passing))
    print("  headline: K-3 joint power at mu*=+4.09 pts, C=%s -> %s"
          % (headline_C, headline_power))
    print("  reports under %s" % REP)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "askability":
        main_askability()
    else:
        main()
