#!/usr/bin/env python3
"""DDC T0 ops — calibration-corpus assembler (docs/next/design/DDC.md
sections 2.2/2.4/3, section 6 T0 stage row; ASM-1651/1659/1660; T0 build
stipulations emitted as PROPOSED-ASM-1790..1799, poc/ddc/asm-1790-1799.json).

Consumes the node-built kernel assets (poc/ddc/t0/build_kernel_assets.mjs
output) and writes the five calibration corpora + the det_u eval subset
under data/, each with a BUILD-MANIFEST.json disclosure (BUILD-MANIFEST is
.json, so ddc_selection.load_corpus_texts never reads it as a sequence):

  data/ddc-kernel-static-v1    K-static (ASM-1651): committed renders
      (65 prime lexicon names + 54 kernel-v0 renderExplication renders +
      54 molecules-v0 groundingNotes) first, then the seeded
      generateExplication pool ("ddc-kstatic|0|<i>", house depth x clause
      mixture) in order, <=256 donor-tokens each, exact-duplicate-
      deduplicated, cut at N=4096 sequences.
  data/ddc-shuffled-kernel-v1  C3: K-static with a WITHIN-SEQUENCE
      whitespace-token shuffle, seed 0 (per-sequence stream
      "ddc-c3|0|<seq>"): unigram statistics preserved, structure destroyed.
  data/ddc-knull-render-v1     C2 (ASM-1660): the knull plain-dictionary
      authored store (poc/knull/inputs/plain-authored.json, 108
      definitions) rendered "<term>: <gloss>", terms in sorted order,
      CYCLED until the total donor-token budget first reaches K-static's
      (the store is ~30x smaller than the budget — the repetition factor
      is disclosed here and adequacy is the standing MD-5 question).
  data/ddc-kernel-hybrid-v1    K-hybrid (ASM-1659): 2048 K-static
      sequences (det_u("ddc-khybrid|kstatic-half", seq) ranking, kept in
      corpus order) + 2048 closure sequences — the RULES-1 pinned kinship
      module (axioms-v0/{rel-mother,rel-father,class-man} +
      axioms-kinship-v1) rendered to NL, plus the stated facts AND the
      twin-engine (poc/rules-1/twin_engine.py, the rules-1-certified
      fixpoint) closure Cl(S) of data/world-v0, data/nsk1-eval and
      data/nsk1-clutrr, sentence-packed to a per-sequence token target
      that lands the corpus total on K-static's (gate I-3).
  data/ddc-c4-sample-v1        C1: the first 4096 rows of allenai/c4
      config "en" split "train" via the HF datasets-server rows API
      (offset order — the pinned deterministic selection rule), each
      truncated to a single binary-searched per-document token cap so the
      corpus total matches K-static's within the I-3 tolerance;
      ODC-BY LICENSE-NOTICE written alongside.
  data/ddc-eval-subset-v1      the pre-declared rho in {0.3, 0.15} tail
      subset (ASM-1703): pubeval's OWN subsample (det_u("sub", bench,
      seed, item_id) ranking, seed 20260712) cut at 500 items/task —
      computed by calling pubeval_runner.subsample, so the pre-declaration
      and the runtime subset coincide by construction. FOLIO has 204 eval
      items (< 500): the subset is the full set, disclosed.

Token counts use the DONOR tokenizer (HuggingFaceTB/SmolLM2-135M at the
pinned T0 revision; tokenizer.json fetched-if-missing and sha-verified —
both donors share this tokenizer). The I-3 parity table is written to
poc/ddc/t0/i3-token-parity.json.

Deterministic given (kernel assets, pinned tokenizer, C4 cache); the C4
fetch itself is pin-on-build (the corpus hash pins the bytes; a drifted
re-fetch fails the pin, never silently re-pins). $0, CPU-only, no torch.

This module states NO feasibility conclusion.
"""

import argparse
import hashlib
import json
import os
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "poc", "pubeval"))
sys.path.insert(0, os.path.join(ROOT, "poc", "rules-1"))

import benchmarks as B  # noqa: E402  (pubeval, stdlib-only)
import pubeval_runner as PE  # noqa: E402
from twin_engine import Closure, load_tbox  # noqa: E402

N_KSTATIC = 4096          # ASM-1651
MAX_TOKENS = 256          # ASM-1651 / manifest surgery.max_seq_tokens
N_HYBRID_HALF = 2048      # ASM-1659 50/50 split
N_C4 = 4096               # DDC.md section 3 C1 row
SUBSET_N = 500            # ASM-1703
SUBSET_SEED = 20260712    # manifest eval.seed
I3_TOL = 0.10             # gate I-3

TOKENIZER_URL = ("https://huggingface.co/HuggingFaceTB/SmolLM2-135M/resolve/"
                 "93efa2f097d58c2a74874c7e644dbc9b0cee75a2/tokenizer.json")
TOKENIZER_SHA = ("9ca9acddb6525a194ec8ac7a87f24fbba7232a9a15ffa1af0c1224fc"
                 "d888e47c")

C4_API = ("https://datasets-server.huggingface.co/rows?dataset=allenai%%2Fc4"
          "&config=en&split=train&offset=%d&length=%d")
C4_PAGE = 100

KINSHIP_TBOX = [
    os.path.join(ROOT, "data", "axioms-v0", "rel-mother.json"),
    os.path.join(ROOT, "data", "axioms-v0", "rel-father.json"),
    os.path.join(ROOT, "data", "axioms-v0", "class-man.json"),
    os.path.join(ROOT, "data", "axioms-kinship-v1"),
]
WORLDS = ["world-v0", "nsk1-eval", "nsk1-clutrr"]


def die(code, msg):
    sys.stderr.write("%s: %s\n" % (code, msg))
    raise SystemExit(1)


def log(msg):
    print(msg, flush=True)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def det_u(*keys):
    """pubeval/f2bt det_u convention (sha256, no RNG state)."""
    h = hashlib.sha256(("|".join(str(k) for k in keys)).encode()).digest()
    return int.from_bytes(h[:8], "big") / 2.0 ** 64


# --------------------------------------------------------------------------
# tokenizer
# --------------------------------------------------------------------------

def load_tokenizer(cache_dir):
    from tokenizers import Tokenizer
    path = os.path.join(cache_dir, "tokenizer-smollm2-93efa2f0.json")
    if not os.path.exists(path):
        log("fetching pinned donor tokenizer ...")
        req = urllib.request.Request(TOKENIZER_URL, headers={
            "User-Agent": "kot-ddc-t0/1 (stdlib urllib)"})
        with urllib.request.urlopen(req, timeout=120) as r:
            body = r.read()
        os.makedirs(cache_dir, exist_ok=True)
        with open(path, "wb") as f:
            f.write(body)
    got = sha256_file(path)
    if got != TOKENIZER_SHA:
        die("ERR_T0_TOKENIZER", "tokenizer sha %s != pinned %s"
            % (got[:16], TOKENIZER_SHA[:16]))
    tok = Tokenizer.from_file(path)

    def count(text):
        return len(tok.encode(text, add_special_tokens=False).ids)

    def encode(text):
        return tok.encode(text, add_special_tokens=False).ids

    return count, encode, tok


# --------------------------------------------------------------------------
# corpus writing
# --------------------------------------------------------------------------

def write_corpus(name, rows, manifest):
    d = os.path.join(ROOT, "data", name)
    os.makedirs(d, exist_ok=True)
    seq_path = os.path.join(d, "sequences.jsonl")
    with open(seq_path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")
    manifest = dict(manifest)
    manifest["n_sequences"] = len(rows)
    manifest["built_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(os.path.join(d, "BUILD-MANIFEST.json"), "w") as f:
        json.dump(manifest, f, indent=1, sort_keys=True)
        f.write("\n")
    log("%s: %d sequences -> %s" % (name, len(rows), d))
    return d


# --------------------------------------------------------------------------
# K-static (ASM-1651)
# --------------------------------------------------------------------------

def build_kstatic(assets_dir, count):
    rows = []
    seen = set()
    skipped_long = 0
    skipped_dup = 0

    def push(source, text):
        nonlocal skipped_long, skipped_dup
        if len(rows) >= N_KSTATIC:
            return
        if text in seen:
            skipped_dup += 1
            return
        if count(text) > MAX_TOKENS:
            skipped_long += 1
            return
        seen.add(text)
        rows.append({"seq": len(rows), "source": source, "text": text})

    for line in open(os.path.join(assets_dir, "committed-renders.jsonl")):
        r = json.loads(line)
        push("%s:%s" % (r["kind"], r["id"]), r["text"])
    n_committed = len(rows)
    for line in open(os.path.join(assets_dir, "synth-pool.jsonl")):
        if len(rows) >= N_KSTATIC:
            break
        r = json.loads(line)
        push("synth:ddc-kstatic|0|%d" % r["i"], r["text"])
    if len(rows) != N_KSTATIC:
        die("ERR_T0_KSTATIC", "only %d/%d sequences after the pool — "
            "enlarge N_SYNTH_POOL in build_kernel_assets.mjs"
            % (len(rows), N_KSTATIC))
    total = sum(count(r["text"]) for r in rows)
    man = {
        "corpus": "ddc-kernel-static-v1 (K-static, ASM-1651)",
        "recipe": "committed renders (65 primes + 54 kernel-v0 + 54 "
                  "molecules-v0 groundingNotes) then seeded "
                  "generateExplication pool ddc-kstatic|0|<i> (x1-q house "
                  "depth x clause mixture); <=256 donor tokens; exact-dup "
                  "dedup; N=4096",
        "n_committed": n_committed,
        "skipped_over_256_tokens": skipped_long,
        "skipped_exact_duplicates": skipped_dup,
        "total_donor_tokens": total,
        "tokenizer_sha256": TOKENIZER_SHA,
        "builder": "poc/ddc/t0/build_corpora.py + build_kernel_assets.mjs",
    }
    write_corpus("ddc-kernel-static-v1", rows, man)
    return rows, total


# --------------------------------------------------------------------------
# C3 shuffled kernel (section 3 C3 row)
# --------------------------------------------------------------------------

def build_shuffled(kstatic_rows, count):
    import numpy as np
    rows = []
    for r in kstatic_rows:
        toks = r["text"].split()
        sub = int(hashlib.sha256(
            ("ddc-c3|0|%d" % r["seq"]).encode()).hexdigest()[:12], 16)
        rng = np.random.default_rng(sub)
        perm = rng.permutation(len(toks))
        rows.append({"seq": r["seq"],
                     "text": " ".join(toks[i] for i in perm)})
    total = sum(count(r["text"]) for r in rows)
    man = {
        "corpus": "ddc-shuffled-kernel-v1 (C3)",
        "recipe": "K-static with within-sequence whitespace-token shuffle, "
                  "seed 0 (numpy default_rng(sha256('ddc-c3|0|<seq>')[:12] "
                  "per sequence)); unigram statistics preserved",
        "total_donor_tokens": total,
        "tokenizer_sha256": TOKENIZER_SHA,
        "builder": "poc/ddc/t0/build_corpora.py",
    }
    write_corpus("ddc-shuffled-kernel-v1", rows, man)
    return total


# --------------------------------------------------------------------------
# C2 knull render (ASM-1660)
# --------------------------------------------------------------------------

def build_knull(count, target_tokens):
    store_path = os.path.join(ROOT, "poc", "knull", "inputs",
                              "plain-authored.json")
    store = json.load(open(store_path))
    defs = store["definitions"]
    terms = sorted(defs)
    rows = []
    total = 0
    i = 0
    while total < target_tokens:
        term = terms[i % len(terms)]
        text = "%s: %s" % (term, defs[term])
        n = count(text)
        rows.append({"seq": len(rows), "term": term,
                     "cycle": i // len(terms), "text": text})
        total += n
        i += 1
    man = {
        "corpus": "ddc-knull-render-v1 (C2, ASM-1660)",
        "recipe": "poc/knull/inputs/plain-authored.json definitions "
                  "rendered '<term>: <gloss>', terms sorted, cycled until "
                  "the running donor-token total first reaches K-static's "
                  "(gate I-3); repetition disclosed (MD-5 adequacy "
                  "question)",
        "store_sha256": sha256_file(store_path),
        "n_definitions": len(terms),
        "cycles_completed": i / float(len(terms)),
        "total_donor_tokens": total,
        "tokenizer_sha256": TOKENIZER_SHA,
        "builder": "poc/ddc/t0/build_corpora.py",
    }
    write_corpus("ddc-knull-render-v1", rows, man)
    return total


# --------------------------------------------------------------------------
# K-hybrid (ASM-1659): kinship module + engine closures
# --------------------------------------------------------------------------

def _urn_labels():
    labels = {}
    for src in ("data/kernel-v0/minted-urns.jsonl",
                "data/molecules-v0/minted-urns.jsonl"):
        for line in open(os.path.join(ROOT, src)):
            r = json.loads(line)
            labels[r["urn"]] = r["sourceId"]
    man = json.load(open(os.path.join(
        ROOT, "data", "axioms-kinship-v1", "manifest.json")))
    for label, rec in man.get("concept_records", {}).items():
        labels[rec["urn"]] = label
    return labels


def _entity_surface(urn, lexicons):
    for lx in lexicons:
        if urn in lx:
            return lx[urn]
    tail = urn.rsplit(":", 1)[-1]
    words = tail.split("-")
    if all(w.isalpha() for w in words):
        return " ".join(w.capitalize() for w in words)
    return tail


REL_SENTENCES = {
    "maker-of": "%s is the maker of %s.",
    "part-of": "%s is a part of %s.",
}


def _rel_sentence(label, s, o):
    if label in REL_SENTENCES:
        return REL_SENTENCES[label] % (s, o)
    return "The %s of %s is %s." % (label, s, o)


def _axiom_sentences(labels):
    """NL renderings of the pinned kinship module (templates below are the
    T0 build's stipulated surfaces, PROPOSED-ASM-1793)."""
    out = []
    tbox = load_tbox(KINSHIP_TBOX)
    lab = lambda u: labels.get(u) or die(  # noqa: E731
        "ERR_T0_LABEL", "no label for %s" % u)
    for p, supers in sorted(tbox.subprop.items()):
        for (q, _ref) in sorted(supers):
            out.append("The %s of someone is also a %s of that someone."
                       % (lab(p), lab(q)))
    for p, (c, _ref) in sorted(tbox.domain.items()):
        out.append("Anyone who has a %s is a %s." % (lab(p), lab(c)))
    for p, (c, _ref) in sorted(tbox.range.items()):
        out.append("The %s of someone is always a %s." % (lab(p), lab(c)))
    for p in sorted(tbox.functional):
        out.append("Someone can have only one %s." % lab(p))
    for (c1, c2, _ref) in sorted(tbox.disjoint):
        out.append("No %s is a %s." % (lab(c1), lab(c2)))
    for (p1, p2, sup, _ref) in sorted(tbox.chains):
        out.append("The %s of someone's %s is that someone's %s."
                   % (lab(p2), lab(p1), lab(sup)))
    for (p, ms, _ref) in sorted(tbox.covers):
        out.append("Every %s of someone is their %s or their %s."
                   % (lab(p), lab(ms[0]), lab(ms[1])))
    return out, tbox


def _world_sentences(world, tbox, labels):
    d = os.path.join(ROOT, "data", world)
    lexicons = []
    lx_path = os.path.join(d, "lexicon.json")
    if os.path.exists(lx_path):
        lexicons.append(json.load(open(lx_path)).get("entities", {}))
    stated = []
    for line in open(os.path.join(d, "world.jsonl")):
        r = json.loads(line)
        if r["kind"] == "relation":
            stated.append(("rel", r["subject"], r["relation"], r["object"]))
        elif r["kind"] == "class":
            stated.append(("cls", r["entity"], r["concept"]))
        else:
            die("ERR_T0_WORLD", "%s: unknown fact kind %r" % (world, r))
    cl = Closure(tbox, stated, max_derived=200000)
    derived = sorted(cl.derived())

    def sent(f):
        if f[0] == "rel":
            _k, s, p, o = f
            label = labels.get(p)
            if label is None:
                die("ERR_T0_LABEL", "no label for relation %s" % p)
            return _rel_sentence(label, _entity_surface(s, lexicons),
                                 _entity_surface(o, lexicons))
        _k, e, c = f
        label = labels.get(c)
        if label is None:
            die("ERR_T0_LABEL", "no label for class %s" % c)
        return "%s is a %s." % (_entity_surface(e, lexicons), label)

    stated_s = [sent(f) for f in stated]
    derived_s = [sent(f) for f in derived]
    return stated_s, derived_s, len(cl.conflicts)


def build_hybrid(kstatic_rows, count, target_tokens):
    # half 1: det_u-ranked K-static half, kept in corpus order
    ranked = sorted(range(len(kstatic_rows)),
                    key=lambda i: det_u("ddc-khybrid|kstatic-half", i))
    keep = sorted(ranked[:N_HYBRID_HALF])
    half1 = [{"seq": n, "source": "kstatic:%d" % i,
              "text": kstatic_rows[i]["text"]}
             for n, i in enumerate(keep)]
    half1_tokens = sum(count(r["text"]) for r in half1)

    # half 2: kinship module + stated worlds + engine closures
    labels = _urn_labels()
    axiom_s, tbox = _axiom_sentences(labels)
    stream = list(axiom_s)
    world_stats = {}
    for w in WORLDS:
        st, dv, conflicts = _world_sentences(w, tbox, labels)
        stream.extend(st)
        stream.extend(dv)
        world_stats[w] = {"stated": len(st), "derived": len(dv),
                          "engine_conflicts_recorded": conflicts}
        log("  %s: %d stated, %d derived, %d conflicts recorded"
            % (w, len(st), len(dv), conflicts))
    for s in stream:
        if count(s) > MAX_TOKENS:
            die("ERR_T0_HYBRID", "sentence over %d tokens: %r"
                % (MAX_TOKENS, s[:80]))

    per_seq = max(8, (target_tokens - half1_tokens) // N_HYBRID_HALF)
    per_seq = min(per_seq, MAX_TOKENS)
    half2 = []
    idx = 0
    cycles = 0
    while len(half2) < N_HYBRID_HALF:
        parts = []
        tokens = 0
        while True:
            s = stream[idx % len(stream)]
            n = count(s)
            if parts and tokens + 1 + n > per_seq:
                break
            parts.append(s)
            tokens += n + (1 if len(parts) > 1 else 0)
            idx += 1
            if idx % len(stream) == 0:
                cycles += 1
        half2.append({"seq": N_HYBRID_HALF + len(half2),
                      "source": "closure", "text": " ".join(parts)})
    half2_tokens = sum(count(r["text"]) for r in half2)

    rows = half1 + half2
    total = half1_tokens + half2_tokens
    man = {
        "corpus": "ddc-kernel-hybrid-v1 (K-hybrid, ASM-1659)",
        "recipe": "50%% K-static (det_u('ddc-khybrid|kstatic-half', seq) "
                  "ranking, 2048 sequences, corpus order) + 50%% kinship-"
                  "module NL renders + stated facts + twin-engine closures "
                  "of world-v0/nsk1-eval/nsk1-clutrr, sentence-packed to "
                  "~%d tokens/sequence (I-3 landing rule)" % per_seq,
        "engine": "poc/rules-1/twin_engine.py (rules-1-certified fixpoint; "
                  "tbox = axioms-v0/{rel-mother,rel-father,class-man} + "
                  "axioms-kinship-v1 — the RULES-1 pinned kinship module)",
        "sentence_stream": {"axiom_sentences": len(axiom_s),
                            "worlds": world_stats,
                            "stream_cycles_completed": cycles},
        "half_tokens": {"kstatic_half": half1_tokens,
                        "closure_half": half2_tokens},
        "total_donor_tokens": total,
        "tokenizer_sha256": TOKENIZER_SHA,
        "builder": "poc/ddc/t0/build_corpora.py",
    }
    write_corpus("ddc-kernel-hybrid-v1", rows, man)
    return total


# --------------------------------------------------------------------------
# C1 — C4 sample (section 3 C1 row)
# --------------------------------------------------------------------------

def _fetch_c4(cache_dir):
    cache = os.path.join(cache_dir, "c4-en-train-first%d.jsonl" % N_C4)
    if os.path.exists(cache):
        rows = [json.loads(l) for l in open(cache)]
        if len(rows) == N_C4:
            return rows, cache
    rows = []
    offset = 0
    while len(rows) < N_C4:
        url = C4_API % (offset, C4_PAGE)
        last = None
        for attempt in range(5):
            try:
                req = urllib.request.Request(url, headers={
                    "User-Agent": "kot-ddc-t0/1 (stdlib urllib)"})
                with urllib.request.urlopen(req, timeout=120) as r:
                    j = json.loads(r.read())
                break
            except Exception as e:  # noqa: BLE001
                last = e
                time.sleep(2 ** attempt)
        else:
            die("ERR_T0_C4_FETCH", "%s: %s" % (url, last))
        batch = [r["row"] for r in j.get("rows", [])]
        if not batch:
            die("ERR_T0_C4_FETCH", "empty page at offset %d" % offset)
        rows.extend(batch)
        offset += len(batch)
        if offset % 1000 == 0:
            log("  c4 rows: %d/%d" % (offset, N_C4))
    rows = rows[:N_C4]
    os.makedirs(cache_dir, exist_ok=True)
    with open(cache, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")
    return rows, cache


def build_c4(cache_dir, count, encode, tok, target_tokens):
    raw, cache = _fetch_c4(cache_dir)
    lens = [len(encode(r["text"])) for r in raw]

    def total_at(cap):
        return sum(min(n, cap) for n in lens)

    lo, hi = 1, MAX_TOKENS
    if total_at(MAX_TOKENS) < target_tokens * (1 - I3_TOL):
        die("ERR_T0_C4", "even cap=%d yields %d tokens < %.0f — fetch more "
            "rows" % (MAX_TOKENS, total_at(MAX_TOKENS),
                      target_tokens * (1 - I3_TOL)))
    while lo < hi:
        mid = (lo + hi) // 2
        if total_at(mid) < target_tokens:
            lo = mid + 1
        else:
            hi = mid
    cap = lo
    if abs(total_at(cap - 1) - target_tokens) < abs(total_at(cap)
                                                    - target_tokens):
        cap = cap - 1
    rows = []
    for i, r in enumerate(raw):
        ids = encode(r["text"])
        text = r["text"] if len(ids) <= cap else tok.decode(ids[:cap])
        rows.append({"seq": i, "c4_offset": i, "text": text})
    total = sum(count(r["text"]) for r in rows)
    d = write_corpus("ddc-c4-sample-v1", rows, {
        "corpus": "ddc-c4-sample-v1 (C1)",
        "recipe": "first %d rows of allenai/c4 en/train via the HF "
                  "datasets-server rows API (offset order — the pinned "
                  "selection rule), each truncated to the binary-searched "
                  "per-document cap %d donor tokens so the corpus total "
                  "lands on K-static's (gate I-3); truncation by tokenizer "
                  "decode of the first-cap token ids" % (N_C4, cap),
        "source": "hf-datasets-server:allenai/c4/en/train offsets 0..%d"
                  % (N_C4 - 1),
        "raw_cache_sha256": sha256_file(cache),
        "per_doc_token_cap": cap,
        "n_docs_truncated": sum(1 for n in lens if n > cap),
        "total_donor_tokens": total,
        "tokenizer_sha256": TOKENIZER_SHA,
        "builder": "poc/ddc/t0/build_corpora.py",
    })
    with open(os.path.join(d, "LICENSE-NOTICE.md"), "w") as f:
        f.write(
            "# ddc-c4-sample-v1 — license notice\n\n"
            "Sampled from C4 (allenai/c4, config en, split train), the\n"
            "Colossal Clean Crawled Corpus (arXiv:1910.10683). Released\n"
            "under ODC-BY 1.0 (https://opendatacommons.org/licenses/by/);\n"
            "subject to the Common Crawl terms of use. NOT authored by\n"
            "this project; calibration-input use only. [search 2026-07-12]\n")
    return total


# --------------------------------------------------------------------------
# det_u eval subset (ASM-1703)
# --------------------------------------------------------------------------

def build_eval_subset():
    data_dir = os.path.join(ROOT, "poc", "pubeval", "data")
    subset = {}
    counts = {}
    for name in sorted(B.BENCHMARKS):
        items = B.BENCHMARKS[name].load(data_dir, "eval")
        picked = PE.subsample(items, SUBSET_N, SUBSET_SEED, name)
        subset[name] = [it["id"] for it in picked]
        counts[name] = {"pool": len(items), "subset": len(picked)}
    d = os.path.join(ROOT, "data", "ddc-eval-subset-v1")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "eval-subset.json"), "w") as f:
        json.dump({
            "schema": "kot-ddc-eval-subset/1",
            "rule": "pubeval_runner.subsample: rank eval items by "
                    "det_u('sub', bench, %d, item_id), take first %d "
                    "(pools <= %d take the full set); computed by calling "
                    "the runner's own subsample so the pre-declaration and "
                    "the runtime subset coincide by construction "
                    "(ASM-1703)" % (SUBSET_SEED, SUBSET_N, SUBSET_N),
            "seed": SUBSET_SEED,
            "n_per_task": SUBSET_N,
            "counts": counts,
            "item_ids": subset,
        }, f, indent=1, sort_keys=True)
        f.write("\n")
    with open(os.path.join(d, "BUILD-MANIFEST.json"), "w") as f:
        json.dump({"corpus": "ddc-eval-subset-v1 (ASM-1703 tail subset)",
                   "counts": counts,
                   "pubeval_data_manifest_sha256": sha256_file(
                       os.path.join(data_dir, "manifest.json")),
                   "builder": "poc/ddc/t0/build_corpora.py",
                   "built_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                              time.gmtime())},
                  f, indent=1, sort_keys=True)
        f.write("\n")
    log("ddc-eval-subset-v1: %s -> %s"
        % ({k: v["subset"] for k, v in counts.items()}, d))


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--kernel-assets", required=True,
                    help="build_kernel_assets.mjs output dir")
    ap.add_argument("--cache-dir", required=True,
                    help="tokenizer + raw C4 cache dir (NOT committed)")
    args = ap.parse_args()

    count, encode, tok = load_tokenizer(args.cache_dir)

    kstatic_rows, t_kstatic = build_kstatic(args.kernel_assets, count)
    log("K-static total donor tokens: %d" % t_kstatic)
    totals = {"ddc-kernel-static-v1": t_kstatic}
    totals["ddc-shuffled-kernel-v1"] = build_shuffled(kstatic_rows, count)
    totals["ddc-knull-render-v1"] = build_knull(count, t_kstatic)
    totals["ddc-kernel-hybrid-v1"] = build_hybrid(kstatic_rows, count,
                                                  t_kstatic)
    totals["ddc-c4-sample-v1"] = build_c4(args.cache_dir, count, encode,
                                          tok, t_kstatic)
    build_eval_subset()

    parity = {}
    ok = True
    for name, t in sorted(totals.items()):
        ratio = t / float(t_kstatic)
        good = abs(ratio - 1.0) <= I3_TOL
        ok = ok and good
        parity[name] = {"total_donor_tokens": t,
                        "ratio_vs_kstatic": round(ratio, 4),
                        "within_10pct": good}
    out = {
        "artifact": "gate I-3 token-parity table (five calibration "
                    "corpora vs K-static; DDC.md section 8)",
        "tokenizer": "HuggingFaceTB/SmolLM2-135M @ 93efa2f0 tokenizer.json "
                     "sha256=" + TOKENIZER_SHA,
        "tolerance": I3_TOL,
        "parity": parity,
        "i3_corpus_parity_valid": ok,
        "built_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    path = os.path.join(HERE, "i3-token-parity.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
        f.write("\n")
    log("I-3 parity: %s -> %s" % ("GREEN" if ok else "RED", path))
    if not ok:
        die("ERR_T0_I3", "token parity outside +/-10%% — see %s" % path)


if __name__ == "__main__":
    main()
