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


if __name__ == "__main__":
    main()
