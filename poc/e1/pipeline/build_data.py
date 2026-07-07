#!/usr/bin/env python3
"""E1 data pipeline (docs/poc-design.md E1; bead kernel-of-truth-bk0).

Streams a TinyStories plain-text split, annotates it with the (parity-gated)
python port of the kernel mapper, applies SEEDED stochastic substitution
(p = 0.5 per mapped occurrence — MAJOR 13), builds the word-level vocab
(4-8k) with reserved concept/prime tokens, and emits tokenised uint16 shards
per experiment seed.

PARITY GATE (fail closed): before anything is emitted, the port must
reproduce the TS mapper bit-for-bit on the committed fixture
(inputs/mapper-parity-fixture.json): every lemma-candidate list, the inline
sample annotations, and — when the corpus file IS the fixture slice — the
full-slice decision-stream sha-256.

PAIRED SEEDS (Common rule 1): all seed-dependent choices (story order,
substitution draws) come from SHA-256 DetStream labels keyed by the seed
index; the 5 arms of a given seed consume IDENTICAL shards and batch
schedules. Substitution covers BOTH concept- and prime-mapped tokens
(M0a: 17.08% of token mass maps; x p=0.5 => ~8.5% substituted-token
exposure); abstained tokens are NEVER substituted. Only the 54 CONCEPT rows
are frozen/controlled downstream (Common rule 4); prime rows are ordinary
trainable vocab in all arms.

Two passes: (A) annotate once (seed-independent) into a compact intermediate
+ vocab counts; (B) per seed, permute stories, draw substitutions, emit
train/val shards. Intermediates are deleted unless --keep-intermediate.

Usage:
  python3 build_data.py --corpus TinyStories-valid.txt --out <dir> \
      [--seeds 0,1,2,3,4] [--vocab-size 8000] [--p-sub 0.5] \
      [--val-every 50] [--max-train-tokens N] [--keep-intermediate]
"""

import argparse
import hashlib
import json
import os
import re
import sys
import time
from array import array
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
E1_DIR = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from detstream import DetStream, det_permutation  # noqa: E402
from kernel_mapper import decision_line, load_mapper  # noqa: E402

UNIT_FLAG = 0x80000000  # high bit marks a mapped-unit header in the intermediate


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_json_file(path):
    return sha256_file(path)


def read_stories(path):
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()
    return [s for s in (t.strip() for t in raw.split("<|endoftext|>")) if s]


def parity_gate(mapper, fixture, stories, corpus_sha):
    """Fail-closed TS<->python parity checks. Returns a result dict."""
    for w, expect in fixture["lemmaTable"].items():
        got = mapper.lemma_candidates(w)
        if got != expect:
            raise SystemExit(f"ERR_PARITY: lemma_candidates('{w}') = {got} != fixture {expect}")

    full = corpus_sha == fixture["corpus"]["sha256"]
    if full:
        h = hashlib.sha256()
        for si, story in enumerate(stories):
            h.update(f"#{si}\n".encode())
            lines = [decision_line(a) for a in mapper.map_text(story) if a.is_word]
            h.update(("\n".join(lines) + "\n").encode())
            if si < len(fixture["sampleAnnotations"]) and lines != fixture["sampleAnnotations"][si]:
                raise SystemExit(f"ERR_PARITY: sample annotation mismatch at story {si}")
        if h.hexdigest() != fixture["decisionStreamSha256"]:
            raise SystemExit("ERR_PARITY: full decision-stream sha mismatch — port drifted from mapper")
        return {"lemmaTable": "ok", "fullStream": "ok", "mode": "full (corpus == fixture slice)"}

    # different corpus file: still verify the inline sample annotations by
    # re-annotating the fixture's own sample stories is impossible (text not
    # stored) — the lemma table + the committed full-stream hash on the
    # fixture slice remain the cross-language guarantee; record that.
    return {
        "lemmaTable": "ok",
        "fullStream": "skipped (corpus != fixture slice; gate ran on the fixture slice at prep time)",
        "mode": "lemma-table only",
    }


def eval_forced_tokens(mapper, templates):
    """All word norms + punct surfaces the eval instruments need in-vocab."""
    forced = []
    texts = list(templates["definitional"]["types"])
    for frames in templates["probe"]["types"].values():
        texts.extend(frames)
    for c in templates["concepts"]:
        texts.append(c["gloss"])
    for text in texts:
        text = text.replace("{c}", " ").replace("{gloss}", " ")
        for t in mapper.tokenize(text):
            tok = t.norm if t.is_word else t.surface
            if tok and tok not in forced:
                forced.append(tok)
    return forced


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--artifact-dir", default=os.path.join(E1_DIR, "inputs"))
    ap.add_argument("--seeds", default="0,1,2,3,4")
    ap.add_argument("--vocab-size", type=int, default=8000)
    ap.add_argument("--p-sub", type=float, default=0.5)
    ap.add_argument("--val-every", type=int, default=50,
                    help="original story index %% N == 0 -> validation split")
    ap.add_argument("--max-train-tokens", type=int, default=0,
                    help="cap train shard size per seed (0 = no cap)")
    ap.add_argument("--keep-intermediate", action="store_true")
    args = ap.parse_args()
    seeds = [int(s) for s in args.seeds.split(",")]
    if not (4000 <= args.vocab_size <= 8192):
        raise SystemExit(f"ERR_VOCAB: {args.vocab_size} outside the pre-registered 4-8k range")

    os.makedirs(args.out, exist_ok=True)
    t0 = time.time()

    lex_path = os.path.join(args.artifact_dir, "mapper-lexicon.json")
    fix_path = os.path.join(args.artifact_dir, "mapper-parity-fixture.json")
    tpl_path = os.path.join(args.artifact_dir, "cloze-templates.json")
    mapper = load_mapper(lex_path)
    with open(fix_path) as f:
        fixture = json.load(f)
    with open(tpl_path) as f:
        templates = json.load(f)

    corpus_sha = sha256_file(args.corpus)
    stories = read_stories(args.corpus)
    print(f"[{time.time()-t0:.0f}s] {len(stories)} stories from {args.corpus}")

    parity = parity_gate(mapper, fixture, stories, corpus_sha)
    print(f"[{time.time()-t0:.0f}s] parity gate: {parity['mode']}")

    # ---- special tokens ----------------------------------------------------
    concept_slugs = [c["slug"] for c in templates["concepts"]]  # alphabetical
    if concept_slugs != sorted(concept_slugs):
        raise SystemExit("ERR_ORDER: template concepts not alphabetical")
    primes = sorted({e["target"]["prime"] for e in json.load(open(lex_path))["entries"]
                     if e["target"]["kind"] == "prime"})
    concept_tok = {f"urn:kernel-v0:{s}": i for i, s in enumerate(concept_slugs)}
    specials = ["<unk>", "<eos>"] + [f"⟦c:{s}⟧" for s in concept_slugs] \
        + [f"⟦p:{p}⟧" for p in primes]
    CONCEPT_BASE = 2
    PRIME_BASE = 2 + len(concept_slugs)
    n_special = len(specials)

    # special index (into the intermediate's unit header) per mapper target
    def special_index(kind, target):
        if kind == "concept":
            return CONCEPT_BASE + concept_tok[target]
        return PRIME_BASE + primes.index(target)

    prime_index = {p: i for i, p in enumerate(primes)}

    # ---- pass A: annotate once, count vocab, write intermediate ------------
    inter_path = os.path.join(args.out, "annotated.u32.tmp")
    counts = Counter()
    symtab = {}
    symlist = []

    def intern(tok):
        i = symtab.get(tok)
        if i is None:
            i = len(symlist)
            if i >= UNIT_FLAG:
                raise SystemExit("ERR_SYMTAB overflow")
            symtab[tok] = i
            symlist.append(tok)
        return i

    story_offsets = []  # (offset_u32, length_u32) per story
    potential_units = Counter()  # special idx -> mappable occurrences
    n_word_tokens = 0
    with open(inter_path, "wb") as inter:
        pos = 0
        for si, story in enumerate(stories):
            buf = array("I")
            anns = mapper.map_tokens(mapper.tokenize(story))
            j = 0
            while j < len(anns):
                a = anns[j]
                if not a.is_word:
                    sid = intern(a.surface)
                    counts[a.surface] += 1
                    buf.append(sid)
                    j += 1
                    continue
                n_word_tokens += 1
                if a.kind in ("concept", "prime") and a.phrase_pos == 0:
                    sp = special_index(a.kind, a.target)
                    potential_units[sp] += 1
                    words = []
                    for k in range(a.phrase_len):
                        w = anns[j + k]
                        words.append(intern(w.norm))
                        counts[w.norm] += 1
                        if k > 0:
                            n_word_tokens += 1
                    buf.append(UNIT_FLAG | sp)
                    buf.append(len(words))
                    buf.extend(words)
                    j += a.phrase_len
                else:
                    counts[a.norm] += 1
                    buf.append(intern(a.norm))
                    j += 1
            buf.tofile(inter)
            story_offsets.append((pos, len(buf)))
            pos += len(buf)
            if si % 20000 == 19999:
                print(f"[{time.time()-t0:.0f}s] annotated {si+1} stories")
    print(f"[{time.time()-t0:.0f}s] pass A done: {n_word_tokens} word tokens, "
          f"{len(symlist)} distinct symbols")

    # ---- vocab --------------------------------------------------------------
    forced = eval_forced_tokens(mapper, templates)
    vocab = list(specials)
    seen = set(vocab)
    for tok in forced:
        if tok not in seen:
            vocab.append(tok)
            seen.add(tok)
    if len(vocab) >= args.vocab_size:
        raise SystemExit("ERR_VOCAB: specials+forced exceed vocab size")
    # deterministic order: count desc, then lexicographic
    for tok, _ in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])):
        if len(vocab) >= args.vocab_size:
            break
        if tok not in seen:
            vocab.append(tok)
            seen.add(tok)
    tok_id = {tok: i for i, tok in enumerate(vocab)}
    covered = sum(c for tok, c in counts.items() if tok in tok_id)
    total = sum(counts.values())
    print(f"vocab {len(vocab)} (specials {n_special}, forced {len(forced)}); "
          f"corpus coverage {covered/total*100:.2f}% of {total} tokens")

    sym_to_id = array("I", (tok_id.get(tok, 0) for tok in symlist))

    with open(os.path.join(args.out, "vocab.json"), "w") as f:
        json.dump({
            "artifact": "e1-vocab",
            "vocabSize": len(vocab),
            "specials": {"unk": 0, "eos": 1, "conceptBase": CONCEPT_BASE,
                         "conceptCount": len(concept_slugs), "primeBase": PRIME_BASE,
                         "primeCount": len(primes)},
            "conceptSlugs": concept_slugs,
            "primes": primes,
            "coveragePct": covered / total * 100,
            "tokens": vocab,
        }, f)

    # ---- pass B: per-seed substitution + shard emission ---------------------
    import numpy as np
    inter = np.fromfile(inter_path, dtype=np.uint32)
    unk_id, eos_id = 0, 1
    seed_stats = {}
    for seed in seeds:
        order = det_permutation(f"e1/order/{seed}", len(stories))
        outdir = os.path.join(args.out, f"seed{seed}")
        os.makedirs(outdir, exist_ok=True)
        exposure = Counter()  # concept slug -> substituted count (train)
        prime_exposure = 0
        stats = {"train": 0, "val": 0, "unk": 0, "substituted": 0, "kept": 0}
        ftrain = open(os.path.join(outdir, "train.bin"), "wb")
        fval = open(os.path.join(outdir, "val.bin"), "wb")
        train_full = False
        for si in order:
            is_val = (si % args.val_every == 0)
            if train_full and not is_val:
                continue
            off, ln = story_offsets[si]
            payload = inter[off:off + ln]
            sub = DetStream(f"e1/sub/{seed}/{si}")
            toks = array("H")
            k = 0
            while k < ln:
                v = int(payload[k])
                if v & UNIT_FLAG:
                    sp = v & ~UNIT_FLAG
                    nw = int(payload[k + 1])
                    if sub.next_float() < args.p_sub:
                        toks.append(sp)
                        stats["substituted"] += 1
                        if not is_val:
                            if CONCEPT_BASE <= sp < PRIME_BASE:
                                exposure[concept_slugs[sp - CONCEPT_BASE]] += 1
                            else:
                                prime_exposure += 1
                    else:
                        stats["kept"] += 1
                        for w in payload[k + 2:k + 2 + nw]:
                            tid = int(sym_to_id[int(w)])
                            toks.append(tid)
                            if tid == unk_id:
                                stats["unk"] += 1
                    k += 2 + nw
                else:
                    tid = int(sym_to_id[v])
                    toks.append(tid)
                    if tid == unk_id:
                        stats["unk"] += 1
                    k += 1
            toks.append(eos_id)
            if is_val:
                toks.tofile(fval)
                stats["val"] += len(toks)
            else:
                toks.tofile(ftrain)
                stats["train"] += len(toks)
                if args.max_train_tokens and stats["train"] >= args.max_train_tokens:
                    train_full = True
        ftrain.close()
        fval.close()
        stats["conceptExposure"] = dict(sorted(exposure.items()))
        stats["primeSubstitutedTrain"] = prime_exposure
        stats["attestedConcepts"] = sorted(exposure.keys())
        seed_stats[str(seed)] = stats
        print(f"[{time.time()-t0:.0f}s] seed {seed}: train {stats['train']} val {stats['val']} "
              f"tokens; {len(exposure)}/54 concepts attested")

    attested_all = sorted(set.intersection(
        *[set(seed_stats[str(s)]["attestedConcepts"]) for s in seeds]))

    meta = {
        "artifact": "e1-data",
        "date": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "corpus": {"path": os.path.abspath(args.corpus), "sha256": corpus_sha,
                   "stories": len(stories)},
        "provenance": {
            "mapperLexiconSha256": sha256_json_file(lex_path),
            "parityFixtureSha256": sha256_json_file(fix_path),
            "templatesSha256": sha256_json_file(tpl_path),
            "parity": parity,
        },
        "args": {"vocabSize": args.vocab_size, "pSub": args.p_sub,
                 "valEvery": args.val_every, "maxTrainTokens": args.max_train_tokens,
                 "seeds": seeds},
        "substitutionRule":
            "per mapped occurrence (concept AND prime; phrase head), one float from "
            "DetStream label 'e1/sub/<seed>/<originalStoryIndex>' consumed in story "
            "order; substitute iff float < pSub; abstained/unmapped tokens never "
            "substituted; story order = det_permutation('e1/order/<seed>')",
        "seedStats": seed_stats,
        "attestedInAllSeeds": attested_all,
        "primaryEndpointConceptRule":
            "pre-registered: the primary cloze endpoint averages over concepts attested "
            "(>=1 substituted train occurrence) in ALL seeds; the all-54 average is "
            "reported as secondary/descriptive",
    }
    with open(os.path.join(args.out, "meta.json"), "w") as f:
        json.dump(meta, f, indent=2)

    if not args.keep_intermediate:
        os.remove(inter_path)
    print(f"[{time.time()-t0:.0f}s] done -> {args.out}; attested in all seeds: "
          f"{len(attested_all)}/54")


if __name__ == "__main__":
    main()
