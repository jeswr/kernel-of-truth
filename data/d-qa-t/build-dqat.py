#!/usr/bin/env python3
"""build-dqat — deterministic builder for the D-QA-T corpus (f2b-transfer
stage-1 adjudication + stage-2 eval items; FABLE-frozen design, resolution of
bead kernel-of-truth-voc).

D-QA-T is a FRESH, ID-DISJOINT draw of kernel-covered definitional-QA items
over the same 108 covered concepts as data/d-qa and data/d-qa-r, sized to
n=360 for blind external adjudication (poc/f2b-transfer/design.md §3.1, §4).
Same four item templates, same canonical-record rendering contract, and the
same fail-closed leak machinery as the committed data/d-qa-r/build-dqar.py.

PER-CONCEPT PLAN (re-authored for n=360 — NOT a seed-and-count change; the
d-qa-r plan structurally emits >=9 items/concept and cannot reach 360):
  t1  def-match                       x 108 (every covered concept)
  t2  term-match                      x 108 (LC1-substituted to def-match when
                                             the gloss contains the headword)
  t3  claim, TRUE-preferring          x 108 (claim-true from the concept's own
                                             gloss where a fresh admissible
                                             segment remains under LC8-t, else
                                             substituted to claim-false;
                                             substitutions counted)
  t4  claim, TRUE-preferring          x  36 (fourth-item subset: concepts that
                                             STILL have a fresh segment after
                                             t3 are prioritised, then a seeded
                                             fill from the rest)
  total = 3*108 + 36 = 360.
WHY availability-aware: claim-true surfaces are segments of the concept's own
gloss rendered through the fixed claim template, and d-qa + d-qa-r already
consumed most of them — measured at design time: only 57 fresh segments over
43 concepts remain (65 concepts have zero). A blind parity plan (d-qa-r's
r5/r9 style) would substitute ~80% of true draws to false and trip LC7's
yes/no bound (>0.75 "no"); the availability-aware plan yields ~56 true / ~88
false (no-share ~0.61) and passes with margin. LC7 stays the fail-closed
authority on the built counts.

FRESHNESS CONTRACT (LC8-t, fail-closed): no d-qa-t item may share its exact
prompt surface (question + option texts, unsalted sha256) with ANY of the 650
d-qa items OR any of the 1000 d-qa-r items. The reference corpora are pinned:
this builder recomputes their kot-corpus-hash/1 digests and aborts on
mismatch, so the disjointness reference set is byte-fixed.

DETERMINISM: no wall-clock, no os.urandom, no Python hash(); every choice is
a function of sha256 over GEN_SEED + fixed strings + the pinned source bytes.
Running this script twice produces byte-identical outputs (single-draw rule,
design §3.1: the one pre-committed seed below, one build). NO LLM authored,
selected, or edited any item text.

FAIL-CLOSED: any leak-check violation, missing source, or plan-shape
violation aborts the build with a named DQAT_ERR_* message; nothing is
written on failure.

Usage:  python3 data/d-qa-t/build-dqat.py   (from the repo root or anywhere)
"""

import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools", "registry"))
import kot_common as kc  # noqa: E402  (corpus_hash — the kot-corpus-hash/1 reference impl)

GENERATED = "2026-07-10"          # fixed build date (determinism: never wall-clock)
SCHEMA = "kot-dqat/1"
VERSION = "0.1.0"
GEN_SEED = "dqat/1|f2b-transfer|20260710"  # THE seed, pre-committed verbatim in design §3.1
N_ITEMS = 360                     # design §3.1 n_generated (registry n_planned.n_generated)
ITEMS_PER_CONCEPT_BASE = 3        # t1 def-match, t2 term-match, t3 claim — all 108 concepts
N_FOURTH = N_ITEMS - ITEMS_PER_CONCEPT_BASE * 108   # = 36 fourth-item (t4 claim) concepts
MIN_SEGMENT_CHARS = 15            # = build-dqa.py (canonical-record rendering contract)
FALSE_CLAIM_JACCARD_MAX = 0.5

# LC8-t reference corpora, byte-pinned (kot-corpus-hash/1; values equal the
# registry pins in registry/experiments/f2b-transfer.json at design time):
REF_PINS = {
    "d-qa": "ad756a7e31f9281de3baaff149e87832d8195452b41b19b6f16883ff196571e6",
    "d-qa-r": "0d548bf18ac78f9d7b2abb6686c567f0930acd494c5ca03cee49806c4996ec5e",
}
REF_ITEM_FILES = {"d-qa": ("covered.jsonl", "control.jsonl"), "d-qa-r": ("covered.jsonl",)}
REF_ITEM_COUNTS = {"d-qa": 650, "d-qa-r": 1000}


def die(code, msg):
    sys.stderr.write("%s: %s\n" % (code, msg))
    sys.exit(1)


def h(s):
    """Deterministic integer from a string (sha256 over GEN_SEED-salted key)."""
    return int.from_bytes(
        hashlib.sha256(("%s|%s" % (GEN_SEED, s)).encode("utf-8")).digest(), "big")


def hhex(s):
    return hashlib.sha256(("%s|%s" % (GEN_SEED, s)).encode("utf-8")).hexdigest()


def qhash(question, options):
    """UNSALTED prompt-surface hash — must be comparable across d-qa, d-qa-r
    and d-qa-t (LC8-t cross-set disjointness), so it uses the same construction
    as build-dqa.py's LC5 key but with a plain sha256 (no seed salt)."""
    blob = question + "||" + "|".join(o["text"] for o in (options or []))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def file_sha256(path):
    d = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            d.update(chunk)
    return d.hexdigest()


def pick_k(seed, n, k, exclude=frozenset()):
    """k distinct indices in [0,n) excluding `exclude`, deterministic in seed."""
    out = []
    i = 0
    while len(out) < k:
        idx = h("%s|%d" % (seed, i)) % n
        i += 1
        if idx in exclude or idx in out:
            if i > 10000:
                die("DQAT_ERR_PICK", "cannot draw %d distinct indices (seed %s)" % (k, seed))
            continue
        out.append(idx)
    return out


TOKEN_RE = re.compile(r"[a-z]+")


def tokens(text):
    return set(TOKEN_RE.findall(text.lower()))


def jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / float(len(a | b))


def word_in(word, text):
    return re.search(r"\b%s\b" % re.escape(word.lower()), text.lower()) is not None


URN_MARKUP_RE = re.compile(r"\{urn:[^|}]+\|([^}]*)\}")


def render_plain(text):
    """VERBATIM build-dqa.py normalisation (canonical-record rendering)."""
    text = URN_MARKUP_RE.sub(r"\1", text)
    text = text.replace(" [m]", "").replace("[m]", "")
    return re.sub(r"  +", " ", text).strip()


def segments(gloss):
    """VERBATIM build-dqa.py claim segmentation."""
    out = []
    for seg in re.split(r"[.;]", gloss):
        seg = seg.strip()
        if len(seg) >= MIN_SEGMENT_CHARS and '"' not in seg and seg not in out:
            out.append(seg)
    return out


# --------------------------------------------------------------- load sources

def load_covered():
    concepts = []
    kdir = os.path.join(ROOT, "data", "kernel-v0", "concepts")
    for name in sorted(os.listdir(kdir)):
        if not name.endswith(".json"):
            continue
        path = os.path.join(kdir, name)
        rec = json.load(open(path, encoding="utf-8"))
        concepts.append({
            "label": rec["label"], "urn": rec["id"], "gloss": rec["gloss"].strip(),
            "source": "kernel-v0", "record_path": "data/kernel-v0/concepts/" + name,
            "record_sha256": file_sha256(path),
        })
    mdir = os.path.join(ROOT, "data", "molecules-v0", "molecules")
    for name in sorted(os.listdir(mdir)):
        if not name.endswith(".json"):
            continue
        path = os.path.join(mdir, name)
        rec = json.load(open(path, encoding="utf-8"))
        concepts.append({
            "label": rec["label"], "urn": rec["id"],
            "gloss": render_plain(rec["groundingNote"]),
            "source": "molecules-v0", "record_path": "data/molecules-v0/molecules/" + name,
            "record_sha256": file_sha256(path),
        })
    if len(concepts) != 108:
        die("DQAT_ERR_SOURCE", "expected 108 covered concepts, got %d" % len(concepts))
    labels = [c["label"] for c in concepts]
    if len(set(labels)) != len(labels):
        die("DQAT_ERR_SOURCE", "duplicate covered labels")
    return concepts


def load_ref_prompt_hashes():
    """LC8-t reference set: prompt-surface hashes of EVERY d-qa item (650,
    covered + control) AND every d-qa-r item (1000). The reference corpora are
    byte-pinned: recompute kot-corpus-hash/1 and abort on mismatch."""
    for corpus, pin in sorted(REF_PINS.items()):
        got = kc.corpus_hash(ROOT, corpus)
        if got != pin:
            die("DQAT_ERR_REFPIN", "%s corpus hash %s != pinned %s — the LC8-t "
                "reference set is not the pinned one" % (corpus, got, pin))
    taken = set()
    for corpus, files in sorted(REF_ITEM_FILES.items()):
        n = 0
        for name in files:
            path = os.path.join(ROOT, "data", corpus, "items", name)
            with open(path, encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    it = json.loads(line)
                    taken.add(qhash(it["question"], it["options"]))
                    n += 1
        if n != REF_ITEM_COUNTS[corpus]:
            die("DQAT_ERR_SOURCE", "expected %d %s reference items, got %d"
                % (REF_ITEM_COUNTS[corpus], corpus, n))
    return taken


# --------------------------------------------------------------- item builders

def letter(i):
    return "ABCD"[i]


def shuffle_options(item_id, options):
    """Deterministic (GEN_SEED-salted) option order; returns (options, answer)."""
    keyed = sorted(options, key=lambda o: hhex("%s|opt|%s" % (item_id, hhex(o["text"]))))
    ans = None
    out = []
    for i, o in enumerate(keyed):
        out.append({"key": letter(i), "text": o["text"]})
        if o["is_answer"]:
            ans = letter(i)
    return out, ans


def def_match_item(item_id, concept, pool, taken, checks):
    """T1: which option gives the meaning of <label>? Fresh distractors; the
    variant loop retries until the prompt surface is unused (intra + LC8-t)."""
    n = len(pool)
    self_idx = {i for i, p in enumerate(pool) if p["label"] == concept["label"]}
    same_gloss = {i for i, p in enumerate(pool) if p["gloss"] == concept["gloss"]}
    q = 'Which option gives the meaning of the word "%s"?' % concept["label"]
    for v in range(16):
        dis = pick_k("%s|dis|v%d" % (item_id, v), n, 3, exclude=self_idx | same_gloss)
        options = [{"text": concept["gloss"], "is_answer": True}] + \
                  [{"text": pool[i]["gloss"], "is_answer": False} for i in dis]
        opts, ans = shuffle_options("%s|v%d" % (item_id, v), options)
        if qhash(q, opts) in taken:
            checks["lc8_retries"] += 1
            continue
        if any(o["text"] == concept["gloss"] and o["key"] != ans for o in opts):
            die("DQAT_ERR_LEAK", "LC4 duplicate answer text in %s" % item_id)
        checks["lc4_option_sets"] += 1
        return {"type": "def-match", "question": q, "options": opts, "answer": ans}
    die("DQAT_ERR_LEAK", "LC8-t: no fresh def-match option set for %s" % item_id)


def term_match_item(item_id, concept, pool, taken, checks):
    """T2: a word that means <gloss> — which word? LC1: gloss must not leak
    the label. Returns None on LC1 (caller substitutes a def-match)."""
    if word_in(concept["label"], concept["gloss"]):
        checks["lc1_substituted"] += 1
        return None
    checks["lc1_checked"] += 1
    n = len(pool)
    self_idx = {i for i, p in enumerate(pool) if p["label"] == concept["label"]}
    q = 'A word whose definition is: "%s". Which word is it?' % concept["gloss"]
    for v in range(16):
        dis = pick_k("%s|labels|v%d" % (item_id, v), n, 3, exclude=self_idx)
        options = [{"text": concept["label"], "is_answer": True}] + \
                  [{"text": pool[i]["label"], "is_answer": False} for i in dis]
        opts, ans = shuffle_options("%s|v%d" % (item_id, v), options)
        if qhash(q, opts) in taken:
            checks["lc8_retries"] += 1
            continue
        return {"type": "term-match", "question": q, "options": opts, "answer": ans}
    die("DQAT_ERR_LEAK", "LC8-t: no fresh term-match option set for %s" % item_id)


def claim_question(concept, claim):
    return ('According to the definition of "%s", is the following true of %s? '
            '"%s" Answer yes or no.' % (concept["label"], concept["label"], claim))


def claim_true_item(item_id, concept, taken, checks):
    """T3T: a verbatim definitional segment, seeded start offset; skips any
    segment whose prompt surface is already used (own items OR d-qa OR d-qa-r
    — LC8-t). Returns None when no admissible segment remains (caller
    substitutes a claim-false: the availability-aware plan)."""
    segs = segments(concept["gloss"])
    if not segs:
        return None
    start = h("%s|segstart" % item_id) % len(segs)
    for j in range(len(segs)):
        claim = segs[(start + j) % len(segs)]
        q = claim_question(concept, claim)
        if qhash(q, None) in taken:
            checks["lc8_retries"] += 1
            continue
        checks["lc6_true_claims"] += 1
        return {"type": "claim-true", "question": q, "options": None,
                "answer": "yes", "claim": claim}
    return None


def claim_false_item(item_id, concept, pool, taken, checks):
    """T3F: a definitional segment of a DIFFERENT concept, checked
    non-entailed (LC3) and prompt-fresh (LC8-t)."""
    own_toks = tokens(concept["gloss"])
    n = len(pool)
    for t in range(256):
        idx = h("%s|donor|%d" % (item_id, t)) % n
        donor = pool[idx]
        if donor["label"] == concept["label"] or donor["gloss"] == concept["gloss"]:
            continue
        dsegs = segments(donor["gloss"])
        if not dsegs:
            continue
        claim = dsegs[h("%s|dseg|%d" % (item_id, t)) % len(dsegs)]
        if claim.lower() in concept["gloss"].lower():
            checks["lc3_rejected"] += 1
            continue
        if jaccard(tokens(claim), own_toks) >= FALSE_CLAIM_JACCARD_MAX:
            checks["lc3_rejected"] += 1
            continue
        q = claim_question(concept, claim)
        if qhash(q, None) in taken:
            checks["lc8_retries"] += 1
            continue
        checks["lc3_accepted"] += 1
        return {"type": "claim-false", "question": q, "options": None,
                "answer": "no", "claim": claim, "claim_source": donor["label"]}
    die("DQAT_ERR_LEAK", "LC3/LC8-t: no admissible fresh false claim for %s" % item_id)


def has_fresh_segment(concept, taken):
    """True iff a claim-true draw for this concept could still succeed
    (deterministic pure function of the pinned sources + taken set)."""
    for seg in segments(concept["gloss"]):
        if qhash(claim_question(concept, seg), None) not in taken:
            return True
    return False


def build_items(concepts, pool, taken, checks):
    """The n=360 availability-aware plan (module docstring): t1 def-match,
    t2 term-match (LC1-sub -> def-match), t3 TRUE-preferring claim for every
    concept; then t4 TRUE-preferring claim for a 36-concept subset that
    prioritises concepts still holding a fresh admissible segment."""
    items = []

    def add(meta, iid, itm):
        taken.add(qhash(itm["question"], itm["options"]))
        items.append(dict(meta, id=iid, **itm))

    def claim_pref_true(iid, c):
        it = claim_true_item(iid, c, taken, checks)
        if it is None:
            checks["lc8_substituted_true_to_false"] += 1
            it = claim_false_item(iid, c, pool, taken, checks)
        return it

    def meta_for(c):
        return {"slice": "covered", "label": c["label"], "urn": c["urn"],
                "source": c["source"], "record_path": c["record_path"],
                "record_sha256": c["record_sha256"], "kernel_checkable": True,
                "gloss_doc_id": "doc:%s:%s" % (c["source"], c["label"])}

    # phase 1 — the 3-item base for every covered concept (fixed load order)
    for c in concepts:
        base = "dqat:covered:%s" % c["label"]
        meta = meta_for(c)

        add(meta, base + ":t1", def_match_item(base + ":t1", c, pool, taken, checks))

        it = term_match_item(base + ":t2", c, pool, taken, checks)
        if it is None:
            it = def_match_item(base + ":t2", c, pool, taken, checks)
        add(meta, base + ":t2", it)

        add(meta, base + ":t3", claim_pref_true(base + ":t3", c))

    # phase 2 — the 36-concept fourth item, fresh-segment-first:
    # concepts that STILL have a fresh admissible segment after phase 1 are
    # prioritised (they yield claim-TRUE at t4, protecting the LC7 yes/no
    # balance against reference-set exhaustion); the remainder of the 36 is a
    # seeded fill and substitutes to claim-false via the same recorded path.
    still_fresh = [c for c in concepts if has_fresh_segment(c, taken)]
    rest = [c for c in concepts if not has_fresh_segment(c, taken)]
    order = (sorted(still_fresh, key=lambda c: hhex("t4|" + c["urn"])) +
             sorted(rest, key=lambda c: hhex("t4|" + c["urn"])))
    fourth = order[:N_FOURTH]
    checks["t4_fresh_prioritised"] = sum(1 for c in fourth if c in still_fresh)
    checks["t4_seeded_fill"] = N_FOURTH - checks["t4_fresh_prioritised"]
    for c in fourth:
        base = "dqat:covered:%s" % c["label"]
        add(meta_for(c), base + ":t4", claim_pref_true(base + ":t4", c))
    return items


# --------------------------------------------------------------- leak checks

def final_leak_checks(items, ref_hashes, checks):
    seen_ids, seen_q = set(), set()
    ans_dist = {}
    type_seen = set()
    for it in items:
        if it["id"] in seen_ids:
            die("DQAT_ERR_LEAK", "LC5 duplicate id %s" % it["id"])
        if it["id"].startswith("dqa:") or it["id"].startswith("dqar:"):
            die("DQAT_ERR_LEAK", "id namespace collision with d-qa/d-qa-r: %s" % it["id"])
        if not it["id"].startswith("dqat:"):
            die("DQAT_ERR_LEAK", "id outside the dqat: namespace: %s" % it["id"])
        seen_ids.add(it["id"])
        qk = qhash(it["question"], it["options"])
        if qk in seen_q:
            die("DQAT_ERR_LEAK", "LC5 duplicate question+options (%s)" % it["id"])
        seen_q.add(qk)
        if qk in ref_hashes:  # LC8-t: full-prompt disjointness from d-qa AND d-qa-r
            die("DQAT_ERR_LEAK", "LC8-t prompt surface collides with a d-qa/d-qa-r "
                "item (%s)" % it["id"])
        if it["options"]:
            texts = [o["text"] for o in it["options"]]
            if len(set(texts)) != len(texts):
                die("DQAT_ERR_LEAK", "LC4 duplicate option text in %s" % it["id"])
            ans_text = next(o["text"] for o in it["options"] if o["key"] == it["answer"])
            if it["type"] == "def-match" and ans_text.lower() in it["question"].lower():
                die("DQAT_ERR_LEAK", "LC2 answer text leaked in question %s" % it["id"])
            checks["lc2_checked"] += 1
        if it["type"] == "term-match" and word_in(it["label"], it["question"]):
            die("DQAT_ERR_LEAK", "LC1 headword in shown definition %s" % it["id"])
        ans_dist[it["answer"]] = ans_dist.get(it["answer"], 0) + 1
        type_seen.add(it["type"])
    for t in ("def-match", "term-match", "claim-true", "claim-false"):
        if t not in type_seen:  # design §3.1: all four item types must be drawn
            die("DQAT_ERR_PLAN", "item type %s absent from the build" % t)
    checks["lc7_answer_distribution"] = {k: ans_dist[k] for k in sorted(ans_dist)}
    mc_total = sum(v for k, v in ans_dist.items() if k in "ABCD")
    for k in "ABCD":
        if ans_dist.get(k, 0) > mc_total / 2:
            die("DQAT_ERR_LEAK", "LC7 answer-position imbalance: %s=%d/%d"
                % (k, ans_dist[k], mc_total))
    yn_total = ans_dist.get("yes", 0) + ans_dist.get("no", 0)
    for k in ("yes", "no"):
        if ans_dist.get(k, 0) > 0.75 * yn_total:
            die("DQAT_ERR_LEAK", "LC7 yes/no imbalance: %s=%d/%d"
                % (k, ans_dist.get(k, 0), yn_total))


# --------------------------------------------------------------- write outputs

def wjson(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1, sort_keys=True, ensure_ascii=False)
        f.write("\n")


def wjsonl(path, rows):
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n")


def main():
    if not 0 <= N_FOURTH <= 108:
        die("DQAT_ERR_SOURCE", "cannot hit %d items from 108 concepts at base %d"
            % (N_ITEMS, ITEMS_PER_CONCEPT_BASE))
    covered = load_covered()
    ref_hashes = load_ref_prompt_hashes()
    taken = set(ref_hashes)   # LC8-t working set: d-qa + d-qa-r prompts + own items
    checks = {"lc1_checked": 0, "lc1_substituted": 0, "lc2_checked": 0,
              "lc3_accepted": 0, "lc3_rejected": 0, "lc4_option_sets": 0,
              "lc6_true_claims": 0, "lc8_retries": 0,
              "lc8_substituted_true_to_false": 0}

    items = build_items(covered, covered, taken, checks)
    if len(items) != N_ITEMS:
        die("DQAT_ERR_SOURCE", "items %d != %d" % (len(items), N_ITEMS))

    final_leak_checks(items, ref_hashes, checks)
    for it in items:
        blob = it["question"] + "".join(o["text"] for o in (it["options"] or []))
        if "{urn:" in blob or "[m]" in blob:
            die("DQAT_ERR_MARKUP", "unrendered markup in %s" % it["id"])

    # pinned item order (fresh seeded order — frozen DV: "pinned rank order";
    # the stage-2 eval set is the first 250 EXTERNALLY-LABELLED items in this order)
    items.sort(key=lambda it: hhex("order|" + it["id"]))
    for rank, it in enumerate(items):
        it["rank"] = rank

    os.makedirs(os.path.join(HERE, "items"), exist_ok=True)
    wjsonl(os.path.join(HERE, "items", "covered.jsonl"), items)

    type_counts = {}
    for it in items:
        key = "%s:%s" % (it["slice"], it["type"])
        type_counts[key] = type_counts.get(key, 0) + 1

    leak = {"artifact": "d-qa-t-leak-check", "generated": GENERATED, "result": "PASS",
            "generator_seed": GEN_SEED,
            "checks": {
                "LC1-headword-not-in-shown-definition": {
                    "rule": "term-match items are dropped and substituted with a "
                            "def-match variant when the shown definition contains the "
                            "headword (word-boundary, case-insensitive)",
                    "checked": checks["lc1_checked"],
                    "substituted": checks["lc1_substituted"]},
                "LC2-answer-text-not-in-question": {"checked": checks["lc2_checked"]},
                "LC3-false-claim-not-entailed": {
                    "rule": "false claims must not be a substring of the target gloss "
                            "and must have token-Jaccard < %s vs the target gloss"
                            % FALSE_CLAIM_JACCARD_MAX,
                    "accepted": checks["lc3_accepted"],
                    "rejected_candidates": checks["lc3_rejected"]},
                "LC4-options-distinct-answer-present": {
                    "option_sets": checks["lc4_option_sets"]},
                "LC5-no-duplicate-ids-or-questions": {"items": len(items)},
                "LC6-true-claims-verbatim-from-record": {
                    "claims": checks["lc6_true_claims"]},
                "LC7-answer-position-balance": checks["lc7_answer_distribution"],
                "LC8t-prompt-surface-disjoint-from-d-qa-and-d-qa-r": {
                    "rule": "no item may share its exact prompt surface (question + "
                            "option texts, unsalted sha256) with any of the 650 d-qa "
                            "items or any of the 1000 d-qa-r items; candidate draws "
                            "colliding intra- or cross-set are retried with the next "
                            "seeded variant; TRUE-preferring claim slots with no fresh "
                            "admissible segment are substituted with a claim-false "
                            "item (the availability-aware plan; counts below)",
                    "reference_items": {"d-qa": REF_ITEM_COUNTS["d-qa"],
                                        "d-qa-r": REF_ITEM_COUNTS["d-qa-r"]},
                    "reference_corpus_pins_verified": REF_PINS,
                    "candidate_retries": checks["lc8_retries"],
                    "claim_true_substituted_to_false":
                        checks["lc8_substituted_true_to_false"],
                    "t4_fresh_segment_prioritised": checks["t4_fresh_prioritised"],
                    "t4_seeded_fill": checks["t4_seeded_fill"]}},
            "note": "fail-closed: any violation aborts the build; this file exists "
                    "only on PASS. Freshness caveat (disclosed): the 108 covered "
                    "concepts and the fixed question templates are SHARED with d-qa "
                    "and d-qa-r by construction (kernel coverage is fixed); "
                    "disjointness is enforced at full-prompt granularity. Claim-true "
                    "supply is bounded by fresh gloss segments remaining after d-qa + "
                    "d-qa-r consumption; the availability-aware plan (build-dqat.py "
                    "docstring) maximises claim-true within that bound and LC7 "
                    "enforces the yes/no balance fail-closed."}
    wjson(os.path.join(HERE, "leak-check.json"), leak)

    manifest = {
        "corpus": "d-qa-t",
        "schema": SCHEMA,
        "version": VERSION,
        "generated": GENERATED,
        "generator_seed": GEN_SEED,
        "role": "f2b-transfer inputs: FRESH, ID-disjoint, prompt-surface-disjoint "
                "kernel-covered definitional-QA items for blind external "
                "adjudication (stage 1) and the externally-labelled eval prefix "
                "(stage 2); design poc/f2b-transfer/design.md §3.1; registry pin "
                "pins.corpus_hashes['d-qa-t'] resolves to this corpus's "
                "kot-corpus-hash/1 digest",
        "authorship": "deterministically generated by data/d-qa-t/build-dqat.py from "
                      "the pinned source records; fixed question templates in-script "
                      "(same four templates as data/d-qa/build-dqa.py and "
                      "data/d-qa-r/build-dqar.py); per-concept plan re-authored for "
                      "n=360 (availability-aware; NOT a seed-and-count change — see "
                      "builder docstring); NO LLM authored, selected, or edited any "
                      "item text; built by the committed generator",
        "normalisation": "identical to d-qa: molecule groundingNote markup "
                         "{urn:...|surface} rendered to its surface form, [m] flags "
                         "dropped, whitespace collapsed; kernel-v0 glosses verbatim; "
                         "build fails closed on residual markup",
        "builder": {"path": "data/d-qa-t/build-dqat.py",
                    "sha256": file_sha256(os.path.abspath(__file__))},
        "sources": {
            "kernel-v0": {"kot_corpus_hash": kc.corpus_hash(ROOT, "kernel-v0")},
            "molecules-v0": {"kot_corpus_hash": kc.corpus_hash(ROOT, "molecules-v0")},
            "d-qa-cross-set-reference": {
                "kot_corpus_hash": kc.corpus_hash(ROOT, "d-qa"),
                "use": "LC8-t prompt-surface disjointness reference ONLY — no d-qa "
                       "item text enters any d-qa-t item"},
            "d-qa-r-cross-set-reference": {
                "kot_corpus_hash": kc.corpus_hash(ROOT, "d-qa-r"),
                "use": "LC8-t prompt-surface disjointness reference ONLY — no d-qa-r "
                       "item text enters any d-qa-t item"}},
        "counts": {
            "covered_items": len(items),
            "covered_concepts": len(covered),
            "items_per_concept_base": ITEMS_PER_CONCEPT_BASE,
            "fourth_item_concepts": N_FOURTH,
            "by_type": type_counts},
        "files": {
            "items/covered.jsonl": "%d fresh covered items, pinned order (rank field)"
                                   % N_ITEMS,
            "leak-check.json": "leak-check evidence incl. LC8-t cross-set "
                               "disjointness vs d-qa AND d-qa-r (build fails closed "
                               "on violation)"},
    }
    wjson(os.path.join(HERE, "manifest.json"), manifest)
    print("d-qa-t build OK: %d fresh covered items over %d concepts "
          "(claims %d yes / %d no; LC8-t retries %d, true->false substitutions %d, "
          "t4 fresh-prioritised %d)"
          % (len(items), len(covered),
             checks["lc7_answer_distribution"].get("yes", 0),
             checks["lc7_answer_distribution"].get("no", 0),
             checks["lc8_retries"], checks["lc8_substituted_true_to_false"],
             checks["t4_fresh_prioritised"]))


if __name__ == "__main__":
    main()
