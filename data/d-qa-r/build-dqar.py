#!/usr/bin/env python3
"""build-dqar — deterministic builder for the D-QA-R corpus (f2b-replicate
fresh eval items; architecture-advisor frozen design for f2b-REPLICATE).

D-QA-R is a FRESH, ID-DISJOINT draw of kernel-covered definitional-QA items
over the same 108 covered concepts as data/d-qa (the kernel's coverage is
fixed — freshness lives in the generator seed, i.e. in the distractor sets,
donor claims, claim-segment choices, option orders and item ranks, all of
which are salted with GEN_SEED and therefore disjoint from the d-qa draw).
It exists because the logged F2 d-qa items were used for best-k selection,
the frozen readout AND the quarantined f2b re-analysis; a same-items rerun
under deterministic decode would reproduce the logged numbers byte-for-byte
and carry zero evidential value (poc/f2/f2b-reanalysis.md section 5).

FRESHNESS CONTRACT (LC8, fail-closed): no d-qa-r item may share its exact
prompt surface (question + option texts) with ANY d-qa item (covered or
control). Template stems necessarily recur (same fixed templates, same 108
concepts); the enforced disjointness is at full-prompt granularity — under
the shared IF-C affordance the model's input bytes differ for every item.
Claim items whose only admissible claim segment would reproduce a d-qa
prompt are substituted with a claim-false item (count recorded).

NO control slice: f2b-replicate has no off-coverage arm reading; the P10
extraction gate re-verifies the pinned d-xif labelled set (original d-qa
items) instead.

DETERMINISM: no wall-clock, no os.urandom, no Python hash(); every choice is
a function of sha256 over GEN_SEED + fixed strings + the pinned source bytes.
Running this script twice produces byte-identical outputs. NO LLM authored
any item text: all questions are fixed templates instantiated from the
pinned records (authorship recorded in manifest.json).

FAIL-CLOSED: any leak-check violation or missing source aborts the build
with a named DQAR_ERR_* message; nothing is written on failure.

Usage:  python3 data/d-qa-r/build-dqar.py   (from the repo root or anywhere)
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

GENERATED = "2026-07-09"          # fixed build date (determinism: never wall-clock)
SCHEMA = "kot-dqar/1"
VERSION = "0.1.0"
GEN_SEED = "dqar/1|f2b-replicate|20260709"   # THE generator seed (advisor: new seed)
N_ITEMS = 1000                    # advisor: n>=500, 1000 since per-item cost allows
ITEMS_PER_CONCEPT = 9             # r1..r9 for all 108 concepts
N_TENTH = N_ITEMS - 9 * 108       # + r10 (def-match) for a seeded 28-concept subset
MIN_SEGMENT_CHARS = 15            # = build-dqa.py (canonical-record rendering contract)
FALSE_CLAIM_JACCARD_MAX = 0.5


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
    """UNSALTED prompt-surface hash — must be comparable across d-qa and
    d-qa-r (LC8 cross-set disjointness), so it uses the same construction as
    build-dqa.py's LC5 key but with a plain sha256 (no seed salt)."""
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
                die("DQAR_ERR_PICK", "cannot draw %d distinct indices (seed %s)" % (k, seed))
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
        die("DQAR_ERR_SOURCE", "expected 108 covered concepts, got %d" % len(concepts))
    labels = [c["label"] for c in concepts]
    if len(set(labels)) != len(labels):
        die("DQAR_ERR_SOURCE", "duplicate covered labels")
    return concepts


def load_dqa_prompt_hashes():
    """LC8 reference set: prompt-surface hashes of EVERY d-qa item."""
    taken = set()
    n = 0
    for name in ("covered.jsonl", "control.jsonl"):
        path = os.path.join(ROOT, "data", "d-qa", "items", name)
        with open(path, encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                it = json.loads(line)
                taken.add(qhash(it["question"], it["options"]))
                n += 1
    if n != 650:
        die("DQAR_ERR_SOURCE", "expected 650 d-qa reference items, got %d" % n)
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
    variant loop retries until the prompt surface is unused (intra + LC8)."""
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
            die("DQAR_ERR_LEAK", "LC4 duplicate answer text in %s" % item_id)
        checks["lc4_option_sets"] += 1
        return {"type": "def-match", "question": q, "options": opts, "answer": ans}
    die("DQAR_ERR_LEAK", "LC8: no fresh def-match option set for %s" % item_id)


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
    die("DQAR_ERR_LEAK", "LC8: no fresh term-match option set for %s" % item_id)


def claim_question(concept, claim):
    return ('According to the definition of "%s", is the following true of %s? '
            '"%s" Answer yes or no.' % (concept["label"], concept["label"], claim))


def claim_true_item(item_id, concept, taken, checks):
    """T3T: a verbatim definitional segment, seeded start offset; skips any
    segment whose prompt surface is already used (own items OR d-qa — LC8).
    Returns None when no admissible segment remains (caller substitutes)."""
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
    non-entailed (LC3) and prompt-fresh (LC8)."""
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
    die("DQAR_ERR_LEAK", "LC3/LC8: no admissible fresh false claim for %s" % item_id)


def build_items(concepts, pool, tenth_labels, taken, checks):
    """Per-concept plan r1..r9 (+r10 for the seeded tenth subset):
    r1 def-match, r2 term-match (LC1-sub -> def-match), r3 claim-true
    (LC8-sub -> claim-false), r4 claim-false, r5 seeded-parity claim,
    r6 def-match, r7 term-match variant-2 (LC1-sub -> def-match),
    r8 claim-false, r9 opposite-parity claim of r5, r10 def-match."""
    items = []

    def add(concept, meta, iid, itm):
        taken.add(qhash(itm["question"], itm["options"]))
        items.append(dict(meta, id=iid, **itm))

    def claim_pref_true(iid, c, checks):
        it = claim_true_item(iid, c, taken, checks)
        if it is None:
            checks["lc8_substituted_true_to_false"] += 1
            it = claim_false_item(iid, c, pool, taken, checks)
        return it

    for c in concepts:
        base = "dqar:covered:%s" % c["label"]
        meta = {"slice": "covered", "label": c["label"], "urn": c["urn"],
                "source": c["source"], "record_path": c["record_path"],
                "record_sha256": c["record_sha256"], "kernel_checkable": True,
                "gloss_doc_id": "doc:%s:%s" % (c["source"], c["label"])}

        add(c, meta, base + ":r1", def_match_item(base + ":r1", c, pool, taken, checks))

        it = term_match_item(base + ":r2", c, pool, taken, checks)
        if it is None:
            it = def_match_item(base + ":r2", c, pool, taken, checks)
        add(c, meta, base + ":r2", it)

        add(c, meta, base + ":r3", claim_pref_true(base + ":r3", c, checks))
        add(c, meta, base + ":r4",
            claim_false_item(base + ":r4", c, pool, taken, checks))

        r5_true = h("r5kind|" + c["urn"]) % 2 == 0
        if r5_true:
            add(c, meta, base + ":r5", claim_pref_true(base + ":r5", c, checks))
        else:
            add(c, meta, base + ":r5",
                claim_false_item(base + ":r5", c, pool, taken, checks))

        add(c, meta, base + ":r6", def_match_item(base + ":r6", c, pool, taken, checks))

        it = term_match_item(base + ":r7", c, pool, taken, checks)
        if it is None:
            it = def_match_item(base + ":r7", c, pool, taken, checks)
        add(c, meta, base + ":r7", it)

        add(c, meta, base + ":r8",
            claim_false_item(base + ":r8", c, pool, taken, checks))

        if r5_true:  # r9 takes the opposite parity of r5
            add(c, meta, base + ":r9",
                claim_false_item(base + ":r9", c, pool, taken, checks))
        else:
            add(c, meta, base + ":r9", claim_pref_true(base + ":r9", c, checks))

        if c["label"] in tenth_labels:
            add(c, meta, base + ":r10",
                def_match_item(base + ":r10", c, pool, taken, checks))
    return items


# --------------------------------------------------------------- leak checks

def final_leak_checks(items, dqa_hashes, checks):
    seen_ids, seen_q = set(), set()
    ans_dist = {}
    for it in items:
        if it["id"] in seen_ids:
            die("DQAR_ERR_LEAK", "LC5 duplicate id %s" % it["id"])
        if it["id"].startswith("dqa:"):
            die("DQAR_ERR_LEAK", "id namespace collision with d-qa: %s" % it["id"])
        seen_ids.add(it["id"])
        qk = qhash(it["question"], it["options"])
        if qk in seen_q:
            die("DQAR_ERR_LEAK", "LC5 duplicate question+options (%s)" % it["id"])
        seen_q.add(qk)
        if qk in dqa_hashes:  # LC8: full-prompt disjointness from d-qa
            die("DQAR_ERR_LEAK", "LC8 prompt surface collides with a d-qa item (%s)"
                % it["id"])
        if it["options"]:
            texts = [o["text"] for o in it["options"]]
            if len(set(texts)) != len(texts):
                die("DQAR_ERR_LEAK", "LC4 duplicate option text in %s" % it["id"])
            ans_text = next(o["text"] for o in it["options"] if o["key"] == it["answer"])
            if it["type"] == "def-match" and ans_text.lower() in it["question"].lower():
                die("DQAR_ERR_LEAK", "LC2 answer text leaked in question %s" % it["id"])
            checks["lc2_checked"] += 1
        if it["type"] == "term-match" and word_in(it["label"], it["question"]):
            die("DQAR_ERR_LEAK", "LC1 headword in shown definition %s" % it["id"])
        ans_dist[it["answer"]] = ans_dist.get(it["answer"], 0) + 1
    checks["lc7_answer_distribution"] = {k: ans_dist[k] for k in sorted(ans_dist)}
    mc_total = sum(v for k, v in ans_dist.items() if k in "ABCD")
    for k in "ABCD":
        if ans_dist.get(k, 0) > mc_total / 2:
            die("DQAR_ERR_LEAK", "LC7 answer-position imbalance: %s=%d/%d"
                % (k, ans_dist[k], mc_total))
    yn_total = ans_dist.get("yes", 0) + ans_dist.get("no", 0)
    for k in ("yes", "no"):
        if ans_dist.get(k, 0) > 0.75 * yn_total:
            die("DQAR_ERR_LEAK", "LC7 yes/no imbalance: %s=%d/%d"
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
    covered = load_covered()
    dqa_hashes = load_dqa_prompt_hashes()
    taken = set(dqa_hashes)   # LC8 working set: d-qa prompts + own items so far
    checks = {"lc1_checked": 0, "lc1_substituted": 0, "lc2_checked": 0,
              "lc3_accepted": 0, "lc3_rejected": 0, "lc4_option_sets": 0,
              "lc6_true_claims": 0, "lc8_retries": 0,
              "lc8_substituted_true_to_false": 0}

    if not 0 <= N_TENTH <= len(covered):
        die("DQAR_ERR_SOURCE", "cannot hit %d items from %d concepts"
            % (N_ITEMS, len(covered)))
    tenth = {c["label"] for c in
             sorted(covered, key=lambda c: hhex("r10|" + c["urn"]))[:N_TENTH]}
    items = build_items(covered, covered, tenth, taken, checks)
    if len(items) != N_ITEMS:
        die("DQAR_ERR_SOURCE", "items %d != %d" % (len(items), N_ITEMS))

    final_leak_checks(items, dqa_hashes, checks)
    for it in items:
        blob = it["question"] + "".join(o["text"] for o in (it["options"] or []))
        if "{urn:" in blob or "[m]" in blob:
            die("DQAR_ERR_MARKUP", "unrendered markup in %s" % it["id"])

    # pinned item order (fresh seeded order — frozen DV: "pinned item order")
    items.sort(key=lambda it: hhex("order|" + it["id"]))
    for rank, it in enumerate(items):
        it["rank"] = rank

    os.makedirs(os.path.join(HERE, "items"), exist_ok=True)
    wjsonl(os.path.join(HERE, "items", "covered.jsonl"), items)

    type_counts = {}
    for it in items:
        key = "%s:%s" % (it["slice"], it["type"])
        type_counts[key] = type_counts.get(key, 0) + 1

    leak = {"artifact": "d-qa-r-leak-check", "generated": GENERATED, "result": "PASS",
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
                "LC8-prompt-surface-disjoint-from-d-qa": {
                    "rule": "no item may share its exact prompt surface (question + "
                            "option texts, unsalted sha256) with any of the 650 d-qa "
                            "items; candidate draws colliding intra- or cross-set are "
                            "retried with the next seeded variant; claim-true items "
                            "with no fresh admissible segment are substituted with a "
                            "claim-false item",
                    "dqa_reference_items": len(dqa_hashes),
                    "candidate_retries": checks["lc8_retries"],
                    "claim_true_substituted_to_false":
                        checks["lc8_substituted_true_to_false"]}},
            "note": "fail-closed: any violation aborts the build; this file exists "
                    "only on PASS. Freshness caveat (disclosed): the 108 covered "
                    "concepts and the fixed question templates are SHARED with d-qa "
                    "by construction (kernel coverage is fixed); disjointness is "
                    "enforced at full-prompt granularity, which is the granularity "
                    "at which deterministic decode would replay logged behaviour."}
    wjson(os.path.join(HERE, "leak-check.json"), leak)

    manifest = {
        "corpus": "d-qa-r",
        "schema": SCHEMA,
        "version": VERSION,
        "generated": GENERATED,
        "generator_seed": GEN_SEED,
        "role": "f2b-replicate eval inputs: FRESH, ID-disjoint, prompt-surface-"
                "disjoint kernel-covered definitional-QA items (advisor design; "
                "registry pin definitional-qa-eval-set-fresh resolves to this "
                "corpus's kot-corpus-hash/1 digest). No control slice: the P10 "
                "extraction gate re-verifies the pinned d-xif labelled set instead.",
        "authorship": "deterministically generated by data/d-qa-r/build-dqar.py from "
                      "the pinned source records; fixed question templates in-script "
                      "(same templates as data/d-qa/build-dqa.py); NO LLM authored, "
                      "selected, or edited any item text; built by runner-2",
        "normalisation": "identical to d-qa: molecule groundingNote markup "
                         "{urn:...|surface} rendered to its surface form, [m] flags "
                         "dropped, whitespace collapsed; kernel-v0 glosses verbatim; "
                         "build fails closed on residual markup",
        "builder": {"path": "data/d-qa-r/build-dqar.py",
                    "sha256": file_sha256(os.path.abspath(__file__))},
        "sources": {
            "kernel-v0": {"kot_corpus_hash": kc.corpus_hash(ROOT, "kernel-v0")},
            "molecules-v0": {"kot_corpus_hash": kc.corpus_hash(ROOT, "molecules-v0")},
            "d-qa-cross-set-reference": {
                "kot_corpus_hash": kc.corpus_hash(ROOT, "d-qa"),
                "use": "LC8 prompt-surface disjointness reference ONLY — no d-qa "
                       "item text enters any d-qa-r item"}},
        "counts": {
            "covered_items": len(items),
            "covered_concepts": len(covered),
            "items_per_concept_base": ITEMS_PER_CONCEPT,
            "tenth_item_concepts": N_TENTH,
            "by_type": type_counts},
        "files": {
            "items/covered.jsonl": "%d fresh covered items, pinned order (rank field)"
                                   % N_ITEMS,
            "leak-check.json": "leak-check evidence incl. LC8 cross-set disjointness "
                               "(build fails closed on violation)"},
    }
    wjson(os.path.join(HERE, "manifest.json"), manifest)
    print("d-qa-r build OK: %d fresh covered items over %d concepts "
          "(LC8 retries %d, true->false substitutions %d)"
          % (len(items), len(covered), checks["lc8_retries"],
             checks["lc8_substituted_true_to_false"]))


if __name__ == "__main__":
    main()
