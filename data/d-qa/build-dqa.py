#!/usr/bin/env python3
"""build-dqa — deterministic builder for the D-QA corpus (F2 eval inputs).

D-QA is the F2 definitional-QA eval set (P1 HE1/HE2/HC3; DAG node d-qa;
06-resources.md D-QA row): a kernel-covered definitional QA slice over the
concepts the kernel actually covers (data/kernel-v0 + data/molecules-v0), a
NOT-kernel-covered control slice (WordNet-3.1-glossed lemmas from the M0b
top-500 content-mass vocabulary that no kernel/molecule record covers), and
the hash-pinned gloss corpus + deterministic BM25 index consumed by the F2
text arms (kernel-as-text arm 5, RAG-over-text arm 6, gloss-text
self-verify+retry arm 10).

DETERMINISM: no wall-clock, no os.urandom, no Python hash(); every choice is
a function of sha256 over fixed strings and the pinned source bytes. Running
this script twice produces byte-identical outputs. NO LLM authored any item
text: all questions are fixed templates instantiated from the pinned records
(authorship is recorded in manifest.json).

FAIL-CLOSED: any leak-check violation or missing source aborts the build with
a named DQA_ERR_* message; nothing is written on failure.

Usage:  python3 data/d-qa/build-dqa.py   (from the repo root or anywhere)
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

GENERATED = "2026-07-08"          # fixed build date (determinism: never wall-clock)
SCHEMA = "kot-dqa/1"
VERSION = "0.1.0"
N_COVERED_ITEMS = 500             # = f2.json design.n_planned.per_arm_items (frozen)
N_CONTROL_CONCEPTS = 30
ITEMS_PER_CONTROL_CONCEPT = 5     # -> 150 control items
MIN_SEGMENT_CHARS = 15
MIN_CONTROL_GLOSS_CHARS = 30
FALSE_CLAIM_JACCARD_MAX = 0.5
BM25_K1 = 1.2
BM25_B = 0.75


def die(code, msg):
    sys.stderr.write("%s: %s\n" % (code, msg))
    sys.exit(1)


def h(s):
    """Deterministic integer from a string (sha256, big-endian)."""
    return int.from_bytes(hashlib.sha256(s.encode("utf-8")).digest(), "big")


def hhex(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


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
                die("DQA_ERR_PICK", "cannot draw %d distinct indices (seed %s)" % (k, seed))
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
    """Render molecule groundingNote markup to plain Minimal English:
    {urn:...|surface} -> surface; drop [m] molecule flags; collapse spaces."""
    text = URN_MARKUP_RE.sub(r"\1", text)
    text = text.replace(" [m]", "").replace("[m]", "")
    return re.sub(r"  +", " ", text).strip()


def segments(gloss):
    """Definitional claim segments: split on '.'/';', strip, drop short/quoted."""
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
        die("DQA_ERR_SOURCE", "expected 108 covered concepts, got %d" % len(concepts))
    labels = [c["label"] for c in concepts]
    if len(set(labels)) != len(labels):
        die("DQA_ERR_SOURCE", "duplicate covered labels")
    return concepts


def wn31_gloss_index(wanted):
    """First WordNet-3.1 gloss per wanted lemma; scan order noun,verb,adj,adv."""
    idx = {}
    for part in ("noun", "verb", "adj", "adv"):
        path = os.path.join(ROOT, "data", "lexical-wn31", "synsets-%s.jsonl" % part)
        with open(path, encoding="utf-8") as f:
            for line in f:
                rec = json.loads(line)
                ann = rec.get("annotations", {})
                gloss = (ann.get("gloss") or "").strip()
                if not gloss:
                    continue
                for lemma in ann.get("lemmas", []):
                    lem = lemma.lower()
                    if lem in wanted and lem not in idx:
                        # strip WordNet example clauses (quoted) from the gloss
                        core = gloss.split('"')[0].strip().rstrip(";:, ")
                        if core:
                            idx[lem] = {"gloss": core, "wn31_id": rec["id"], "pos": part}
    return idx


def load_control_and_filler(covered):
    report = json.load(open(os.path.join(ROOT, "mapper", "m0", "results", "m0b-report.json"),
                            encoding="utf-8"))
    covered_words = {c["label"].lower() for c in covered}
    # molecules-v0 corpusLemmas are also covered
    mman = json.load(open(os.path.join(ROOT, "data", "molecules-v0", "manifest.json"),
                          encoding="utf-8"))
    for m in mman["molecules"]:
        covered_words.update(w.lower() for w in m.get("corpusLemmas", []))

    candidates = []  # NOT-kernel-covered content lemmas, M0b file order (count desc)
    for row in report["rows"]:
        lemma = row["lemma"].lower()
        if row.get("class") in ("explicable", "molecule", "oos") \
                and lemma not in covered_words and re.fullmatch(r"[a-z]+", lemma):
            candidates.append(lemma)

    glosses = wn31_gloss_index(set(candidates))
    control, filler = [], []
    for lemma in candidates:
        entry = glosses.get(lemma)
        if entry is None or len(entry["gloss"]) < MIN_CONTROL_GLOSS_CHARS:
            continue
        if word_in(lemma, entry["gloss"]):
            continue  # leak rule LC1: definition must not contain the headword
        rec = {"label": lemma, "urn": entry["wn31_id"], "gloss": entry["gloss"],
               "source": "lexical-wn31", "record_path": None, "record_sha256": None}
        if len(control) < N_CONTROL_CONCEPTS:
            control.append(rec)
        else:
            filler.append(rec)
    if len(control) != N_CONTROL_CONCEPTS:
        die("DQA_ERR_SOURCE", "only %d control concepts found" % len(control))
    return control, filler


# --------------------------------------------------------------- item builders

def letter(i):
    return "ABCD"[i]


def shuffle_options(item_id, options):
    """Deterministic option order; returns (ordered_options, answer_key)."""
    keyed = sorted(options, key=lambda o: hhex("%s|opt|%s" % (item_id, hhex(o["text"]))))
    ans = None
    out = []
    for i, o in enumerate(keyed):
        out.append({"key": letter(i), "text": o["text"]})
        if o["is_answer"]:
            ans = letter(i)
    return out, ans


def def_match_item(item_id, concept, pool, variant, checks):
    """T1: which option gives the meaning of <label>? Distractors from pool."""
    n = len(pool)
    self_idx = {i for i, p in enumerate(pool) if p["label"] == concept["label"]}
    # LC4: distractor gloss must differ from the true gloss
    same_gloss = {i for i, p in enumerate(pool) if p["gloss"] == concept["gloss"]}
    dis = pick_k("%s|dis|%s" % (item_id, variant), n, 3, exclude=self_idx | same_gloss)
    options = [{"text": concept["gloss"], "is_answer": True}] + \
              [{"text": pool[i]["gloss"], "is_answer": False} for i in dis]
    opts, ans = shuffle_options(item_id, options)
    checks["lc4_option_sets"] += 1
    q = 'Which option gives the meaning of the word "%s"?' % concept["label"]
    if any(o["text"] == concept["gloss"] and o["key"] != ans for o in opts):
        die("DQA_ERR_LEAK", "LC4 duplicate answer text in %s" % item_id)
    return {"type": "def-match", "question": q, "options": opts, "answer": ans}


def term_match_item(item_id, concept, pool, checks):
    """T2: a word that means <gloss> — which word? LC1: gloss must not leak label."""
    if word_in(concept["label"], concept["gloss"]):
        checks["lc1_substituted"] += 1
        return None  # caller substitutes a def-match variant
    checks["lc1_checked"] += 1
    n = len(pool)
    self_idx = {i for i, p in enumerate(pool) if p["label"] == concept["label"]}
    dis = pick_k("%s|labels" % item_id, n, 3, exclude=self_idx)
    options = [{"text": concept["label"], "is_answer": True}] + \
              [{"text": pool[i]["label"], "is_answer": False} for i in dis]
    opts, ans = shuffle_options(item_id, options)
    q = 'A word whose definition is: "%s". Which word is it?' % concept["gloss"]
    return {"type": "term-match", "question": q, "options": opts, "answer": ans}


def claim_true_item(item_id, concept, seg_index, checks):
    segs = segments(concept["gloss"])
    if len(segs) <= seg_index:
        return None
    claim = segs[seg_index]
    checks["lc6_true_claims"] += 1
    q = ('According to the definition of "%s", is the following true of %s? '
         '"%s" Answer yes or no.' % (concept["label"], concept["label"], claim))
    return {"type": "claim-true", "question": q, "options": None, "answer": "yes",
            "claim": claim}


def claim_false_item(item_id, concept, pool, checks):
    """T3F: a definitional segment of a DIFFERENT concept, checked non-entailed."""
    own_toks = tokens(concept["gloss"])
    n = len(pool)
    for t in range(64):
        idx = h("%s|donor|%d" % (item_id, t)) % n
        donor = pool[idx]
        if donor["label"] == concept["label"] or donor["gloss"] == concept["gloss"]:
            continue
        dsegs = segments(donor["gloss"])
        if not dsegs:
            continue
        claim = dsegs[h("%s|dseg|%d" % (item_id, t)) % len(dsegs)]
        # LC3: must not be entailed-by-construction by the target's own gloss
        if claim.lower() in concept["gloss"].lower():
            checks["lc3_rejected"] += 1
            continue
        if jaccard(tokens(claim), own_toks) >= FALSE_CLAIM_JACCARD_MAX:
            checks["lc3_rejected"] += 1
            continue
        checks["lc3_accepted"] += 1
        q = ('According to the definition of "%s", is the following true of %s? '
             '"%s" Answer yes or no.' % (concept["label"], concept["label"], claim))
        return {"type": "claim-false", "question": q, "options": None, "answer": "no",
                "claim": claim, "claim_source": donor["label"]}
    die("DQA_ERR_LEAK", "LC3: no admissible false claim for %s" % item_id)


def build_items(concepts, pool, slice_name, per_concept_five, checks):
    items = []
    for c in concepts:
        base = "dqa:%s:%s" % (slice_name, c["label"])
        meta = {"slice": slice_name, "label": c["label"], "urn": c["urn"],
                "source": c["source"], "record_path": c["record_path"],
                "record_sha256": c["record_sha256"],
                "kernel_checkable": slice_name == "covered",
                "gloss_doc_id": "doc:%s:%s" % (c["source"], c["label"])}

        it = def_match_item(base + ":t1", c, pool, "v1", checks)
        items.append(dict(meta, id=base + ":t1", **it))

        it = term_match_item(base + ":t2", c, pool, checks)
        if it is None:  # LC1 leak — substitute a second def-match variant
            it = def_match_item(base + ":t2", c, pool, "v2sub", checks)
        items.append(dict(meta, id=base + ":t2", **it))

        it = claim_true_item(base + ":t3t", c, 0, checks)
        if it is None:
            die("DQA_ERR_SOURCE", "no claim segment for %s" % c["label"])
        items.append(dict(meta, id=base + ":t3t", **it))

        it = claim_false_item(base + ":t3f", c, pool, checks)
        items.append(dict(meta, id=base + ":t3f", **it))

        if c["label"] in per_concept_five:
            # alternate true/false by seeded parity so the yes/no key stays balanced
            it = None
            if h("t5kind|" + c["urn"]) % 2 == 0:
                it = claim_true_item(base + ":t5", c, 1, checks)
            if it is None:  # parity says false, or gloss has one segment only
                it = claim_false_item(base + ":t5", c, pool, checks)
            items.append(dict(meta, id=base + ":t5", **it))
    return items


# --------------------------------------------------------------- leak checks

def final_leak_checks(items, checks):
    seen_ids, seen_q = set(), set()
    ans_dist = {}
    for it in items:
        if it["id"] in seen_ids:
            die("DQA_ERR_LEAK", "LC5 duplicate id %s" % it["id"])
        seen_ids.add(it["id"])
        qk = hhex(it["question"] + "||" +
                  "|".join(o["text"] for o in (it["options"] or [])))
        if qk in seen_q:
            die("DQA_ERR_LEAK", "LC5 duplicate question+options (%s)" % it["id"])
        seen_q.add(qk)
        if it["options"]:
            texts = [o["text"] for o in it["options"]]
            if len(set(texts)) != len(texts):
                die("DQA_ERR_LEAK", "LC4 duplicate option text in %s" % it["id"])
            ansdup = [o for o in it["options"]
                      if o["key"] == it["answer"] and o["text"] not in texts]
            if ansdup:
                die("DQA_ERR_LEAK", "LC4 answer not among options in %s" % it["id"])
            # LC2: a def-match question must not contain the answer gloss
            ans_text = next(o["text"] for o in it["options"] if o["key"] == it["answer"])
            if it["type"] == "def-match" and ans_text.lower() in it["question"].lower():
                die("DQA_ERR_LEAK", "LC2 answer text leaked in question %s" % it["id"])
            checks["lc2_checked"] += 1
        ans_dist[it["answer"]] = ans_dist.get(it["answer"], 0) + 1
    checks["lc7_answer_distribution"] = {k: ans_dist[k] for k in sorted(ans_dist)}
    # LC7: no forced-choice letter may carry an outright majority of MC answers
    mc_total = sum(v for k, v in ans_dist.items() if k in "ABCD")
    for k in "ABCD":
        if ans_dist.get(k, 0) > mc_total / 2:
            die("DQA_ERR_LEAK", "LC7 answer-position imbalance: %s=%d/%d"
                % (k, ans_dist[k], mc_total))


# --------------------------------------------------------------- gloss corpus

def build_gloss_corpus(covered, control, filler):
    docs = []
    for c in covered + control + filler:
        docs.append({"doc_id": "doc:%s:%s" % (c["source"], c["label"]),
                     "term": c["label"], "text": c["gloss"], "source": c["source"],
                     "urn": c["urn"]})
    docs.sort(key=lambda d: d["doc_id"])
    ids = [d["doc_id"] for d in docs]
    if len(set(ids)) != len(ids):
        die("DQA_ERR_SOURCE", "duplicate gloss doc ids")
    return docs


def build_bm25_index(docs):
    df, doclen = {}, {}
    for d in docs:
        toks = TOKEN_RE.findall(d["text"].lower())
        doclen[d["doc_id"]] = len(toks)
        for t in set(toks):
            df[t] = df.get(t, 0) + 1
    n = len(docs)
    avgdl = sum(doclen.values()) / float(n)
    return {"scheme": "bm25", "k1": BM25_K1, "b": BM25_B, "n_docs": n,
            "avgdl": round(avgdl, 6), "tokenizer": "lowercase [a-z]+ runs",
            "df": {k: df[k] for k in sorted(df)},
            "doc_len": {k: doclen[k] for k in sorted(doclen)}}


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
    control, filler = load_control_and_filler(covered)
    checks = {"lc1_checked": 0, "lc1_substituted": 0, "lc2_checked": 0,
              "lc3_accepted": 0, "lc3_rejected": 0, "lc4_option_sets": 0,
              "lc6_true_claims": 0}

    # exactly N_COVERED_ITEMS covered items: 4/concept + a 5th for a seeded subset
    n_fifth = N_COVERED_ITEMS - 4 * len(covered)
    if not 0 <= n_fifth <= len(covered):
        die("DQA_ERR_SOURCE", "cannot hit %d items from %d concepts"
            % (N_COVERED_ITEMS, len(covered)))
    fifth = {c["label"] for c in sorted(covered, key=lambda c: hhex("t5|" + c["urn"]))[:n_fifth]}
    covered_items = build_items(covered, covered, "covered", fifth, checks)
    if len(covered_items) != N_COVERED_ITEMS:
        die("DQA_ERR_SOURCE", "covered items %d != %d" % (len(covered_items), N_COVERED_ITEMS))

    control_pool = control + filler  # distractors/donors stay off-kernel
    fifth_c = {c["label"] for c in control} if ITEMS_PER_CONTROL_CONCEPT == 5 else set()
    control_items = build_items(control, control_pool, "control", fifth_c, checks)
    if len(control_items) != N_CONTROL_CONCEPTS * ITEMS_PER_CONTROL_CONCEPT:
        die("DQA_ERR_SOURCE", "control items %d" % len(control_items))

    final_leak_checks(covered_items + control_items, checks)
    for it in covered_items + control_items:
        blob = it["question"] + "".join(o["text"] for o in (it["options"] or []))
        if "{urn:" in blob or "[m]" in blob:
            die("DQA_ERR_MARKUP", "unrendered markup in %s" % it["id"])

    # pinned item order (frozen f2 DV: "pinned item order")
    covered_items.sort(key=lambda it: hhex("order|" + it["id"]))
    control_items.sort(key=lambda it: hhex("order|" + it["id"]))
    for rank, it in enumerate(covered_items):
        it["rank"] = rank
    for rank, it in enumerate(control_items):
        it["rank"] = rank

    docs = build_gloss_corpus(covered, control, filler)
    index = build_bm25_index(docs)

    os.makedirs(os.path.join(HERE, "items"), exist_ok=True)
    wjsonl(os.path.join(HERE, "items", "covered.jsonl"), covered_items)
    wjsonl(os.path.join(HERE, "items", "control.jsonl"), control_items)
    wjsonl(os.path.join(HERE, "gloss-corpus.jsonl"), docs)
    wjson(os.path.join(HERE, "rag-index.json"), index)

    type_counts = {}
    for it in covered_items + control_items:
        key = "%s:%s" % (it["slice"], it["type"])
        type_counts[key] = type_counts.get(key, 0) + 1

    leak = {"artifact": "d-qa-leak-check", "generated": GENERATED, "result": "PASS",
            "checks": {
                "LC1-headword-not-in-shown-definition": {
                    "rule": "term-match items are dropped and substituted when the shown "
                            "definition contains the headword (word-boundary, case-insensitive); "
                            "control concepts violating it are excluded at selection",
                    "checked": checks["lc1_checked"], "substituted": checks["lc1_substituted"]},
                "LC2-answer-text-not-in-question": {"checked": checks["lc2_checked"]},
                "LC3-false-claim-not-entailed": {
                    "rule": "false claims must not be a substring of the target gloss and must "
                            "have token-Jaccard < %s vs the target gloss" % FALSE_CLAIM_JACCARD_MAX,
                    "accepted": checks["lc3_accepted"], "rejected_candidates": checks["lc3_rejected"]},
                "LC4-options-distinct-answer-present": {"option_sets": checks["lc4_option_sets"]},
                "LC5-no-duplicate-ids-or-questions": {"items": len(covered_items) + len(control_items)},
                "LC6-true-claims-verbatim-from-record": {"claims": checks["lc6_true_claims"]},
                "LC7-answer-position-balance": checks["lc7_answer_distribution"]},
            "note": "fail-closed: any violation aborts the build; this file exists only on PASS"}
    wjson(os.path.join(HERE, "leak-check.json"), leak)

    manifest = {
        "corpus": "d-qa",
        "schema": SCHEMA,
        "version": VERSION,
        "generated": GENERATED,
        "role": "F2 eval inputs (registry pins definitional-qa-eval-set and "
                "gloss-corpus-and-rag-index both resolve to this corpus's "
                "kot-corpus-hash/1 digest)",
        "authorship": "deterministically generated by data/d-qa/build-dqa.py from the pinned "
                      "source records; fixed question templates in-script; NO LLM authored, "
                      "selected, or edited any item text; built by runner-2",
        "normalisation": "molecule groundingNote markup {urn:...|surface} rendered to its "
                         "surface form, [m] molecule flags dropped, whitespace collapsed "
                         "(render_plain in the builder); kernel-v0 glosses carry no markup "
                         "and are used verbatim; build fails closed on residual markup",
        "builder": {"path": "data/d-qa/build-dqa.py",
                    "sha256": file_sha256(os.path.abspath(__file__))},
        "sources": {
            "kernel-v0": {"kot_corpus_hash": kc.corpus_hash(ROOT, "kernel-v0")},
            "molecules-v0": {"kot_corpus_hash": kc.corpus_hash(ROOT, "molecules-v0")},
            "m0b-report": {"path": "mapper/m0/results/m0b-report.json",
                           "sha256": file_sha256(os.path.join(
                               ROOT, "mapper", "m0", "results", "m0b-report.json"))},
            "lexical-wn31-synsets": {
                "synsets-%s.jsonl" % p: file_sha256(os.path.join(
                    ROOT, "data", "lexical-wn31", "synsets-%s.jsonl" % p))
                for p in ("noun", "verb", "adj", "adv")}},
        "counts": {
            "covered_items": len(covered_items),
            "control_items": len(control_items),
            "covered_concepts": len(covered),
            "control_concepts": len(control),
            "gloss_docs": len(docs),
            "filler_docs": len(filler),
            "by_type": type_counts},
        "split": {
            "covered": "items/covered.jsonl — kernel-covered slice; every item names its "
                       "record (urn + record_sha256) so the kernel verifier can score it",
            "control": "items/control.jsonl — NOT-kernel-covered lemmas (M0b top-500 content "
                       "mass, classes explicable/molecule/oos, minus kernel-v0 labels and "
                       "molecules-v0 corpusLemmas), WordNet-3.1 glosses; kernel_checkable=false"},
        "files": {
            "items/covered.jsonl": "500 covered items, pinned order (rank field)",
            "items/control.jsonl": "150 control items, pinned order (rank field)",
            "gloss-corpus.jsonl": "hash-pinned gloss dictionary + RAG corpus (text arms)",
            "rag-index.json": "deterministic BM25 stats over gloss-corpus.jsonl",
            "leak-check.json": "leak-check evidence (build fails closed on violation)"},
    }
    wjson(os.path.join(HERE, "manifest.json"), manifest)
    print("d-qa build OK: %d covered + %d control items, %d gloss docs (%d filler)"
          % (len(covered_items), len(control_items), len(docs), len(filler)))


if __name__ == "__main__":
    main()
