#!/usr/bin/env python3
"""E4 emission-task data builder (docs/poc-design.md E4 rev 2; bead
kernel-of-truth-73u).

Produces the gloss->concept-token training/eval data in poc/e1's shard
format (uint16 little-endian token streams, <eos>-separated sequences), for
the E4 fine-tune of the E1 kernel-frozen model:

  <out>/e4-vocab.json     E1 vocab EXTENDED (never modified in place) with
                          one new special ``EMIT`` marker and 1000 synthetic
                          concept tokens appended after the E1 vocab; the
                          full 1054-token candidate list with ids.
  <out>/seed<s>/train.bin uint16 stream. Two sequence types:
                            emission:  <gloss tokens> EMIT <concept> <eos>
                            exposure:  <carrier tokens incl. <concept>> <eos>
                          Emission sequences exist ONLY for train concepts
                          (minus each concept's held-out eval gloss).
                          Exposure lines exist for train AND tier-1 concepts
                          at the SAME per-concept count (so exposure carries
                          no information about holdout status); NEVER tier-2.
  <out>/eval.jsonl        one eval item per (concept, eval gloss): token ids
                          ending in EMIT, target id, tier + composition
                          labels. Seed-independent.
  <out>/meta.json         provenance (hashes), stats, fail-closed assertion
                          results.

LEAKAGE GATES (fail closed):
  - the gloss file's sha-256 MUST equal poc/e4/GLOSS-HASH.txt (MAJOR 6: the
    hash was committed before any training) AND the holdout manifest's
    recorded hash;
  - tier-2 token ids must not occur anywhere in any train stream;
  - tier-1/tier-2 tokens must never follow EMIT in a train stream;
  - eval glosses of train concepts must not occur in train streams.

Seeding: sequence order = det_permutation('e4/order/<seed>'); carrier-frame
draws = DetStream('e4/exposure/<seed>/<slug>') — the encoder's SHA-256
DetStream via poc/e1's bit-exact python port (read-only import).

Usage:
  python3 build_emission.py --e1-vocab <e1 vocab.json> --out <dir> \
      [--glosses ../inputs/glosses.jsonl] [--holdout ../inputs/holdout-manifest.json] \
      [--seeds 0,1,2,3,4] [--exposure-per-concept 20] [--smoke N]
"""

import argparse
import hashlib
import json
import os
import re
import sys
from array import array

HERE = os.path.dirname(os.path.abspath(__file__))
E4_DIR = os.path.dirname(HERE)
E1_PIPELINE = os.path.join(E4_DIR, "..", "e1", "pipeline")
E1_INPUTS = os.path.join(E4_DIR, "..", "e1", "inputs")
sys.path.insert(0, E1_PIPELINE)  # read-only reuse of the parity-gated ports

from detstream import DetStream, det_permutation  # noqa: E402
from kernel_mapper import load_mapper  # noqa: E402

EMIT_TOKEN = "⟦emit⟧"  # ⟦emit⟧ — the emission-position marker

# Meaning-free carrier frames for exposure lines ({c} = the concept token).
# Committed (and hash-covered via this file) BEFORE any training run; frames
# deliberately say nothing about the concept beyond its being a word.
CARRIER_FRAMES = [
    "one word here is {c} .",
    "the next word is {c} .",
    "{c} is a word .",
    "this list has {c} in it .",
    "a child said the word {c} .",
    "someone wrote {c} on the page .",
]


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def slug_of(concept_id):
    return concept_id.replace("urn:kernel-v0:", "").replace("urn:kernel-e4:", "e4-")


def load_gloss_hash_pin():
    with open(os.path.join(E4_DIR, "GLOSS-HASH.txt")) as f:
        m = re.search(r"= ([0-9a-f]{64})", f.read())
    if m is None:
        raise SystemExit("ERR_PIN: GLOSS-HASH.txt has no sha-256")
    return m.group(1)


def tokenize_text(mapper, text):
    """E1 token convention: word tokens -> norm, non-word tokens -> surface."""
    out = []
    for t in mapper.tokenize(text):
        out.append(t.norm if t.is_word else t.surface)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--e1-vocab", required=True, help="vocab.json from poc/e1 build_data.py")
    ap.add_argument("--out", required=True)
    ap.add_argument("--glosses", default=os.path.join(E4_DIR, "inputs", "glosses.jsonl"))
    ap.add_argument("--holdout", default=os.path.join(E4_DIR, "inputs", "holdout-manifest.json"))
    ap.add_argument("--mapper-lexicon", default=os.path.join(E1_INPUTS, "mapper-lexicon.json"))
    ap.add_argument("--seeds", default="0,1,2,3,4")
    ap.add_argument("--exposure-per-concept", type=int, default=20)
    ap.add_argument("--smoke", type=int, default=0,
                    help="mechanics-only subset: N train + N//3 tier-1 concepts "
                         "(tier-2 always fully included); stamps meta mock:true")
    args = ap.parse_args()
    seeds = [int(s) for s in args.seeds.split(",")]

    # ---- leakage gate: gloss-set hash pin (MAJOR 6) -------------------------
    gloss_sha = sha256_file(args.glosses)
    pin = load_gloss_hash_pin()
    if gloss_sha != pin:
        raise SystemExit(
            f"ERR_GLOSS_PIN: sha256({args.glosses}) = {gloss_sha} != published {pin} "
            "(GLOSS-HASH.txt; a different gloss set is a NEW pre-registration)")
    with open(args.holdout) as f:
        holdout = json.load(f)
    if holdout.get("artifact") != "e4-holdout-manifest":
        raise SystemExit("ERR_ARTIFACT: not an e4-holdout-manifest")
    if holdout["inputs"]["glossesSha256"] != gloss_sha:
        raise SystemExit("ERR_GLOSS_PIN: holdout manifest was built against a different gloss set")

    mapper = load_mapper(args.mapper_lexicon)
    with open(args.e1_vocab) as f:
        e1_vocab = json.load(f)
    if e1_vocab.get("artifact") != "e1-vocab":
        raise SystemExit("ERR_ARTIFACT: --e1-vocab is not an e1-vocab artifact")

    glosses = [json.loads(l) for l in open(args.glosses, encoding="utf-8")]

    tier1_full = list(holdout["tiers"]["tier1"]["ids"])
    tier2_full = list(holdout["tiers"]["tier2"]["ids"])
    eval_variant = holdout["evalGlossVariant"]
    composition = holdout["composition"]["labels"]
    all_ids = sorted({g["conceptId"] for g in glosses})
    heldout_full = set(tier1_full) | set(tier2_full)
    train_full = [i for i in all_ids if i not in heldout_full]
    if sorted(eval_variant.keys()) != train_full:
        raise SystemExit("ERR_HOLDOUT: evalGlossVariant keys != train concepts")

    # ---- extended vocab ------------------------------------------------------
    tokens = list(e1_vocab["tokens"])
    base_size = len(tokens)
    tok_id = {t: i for i, t in enumerate(tokens)}
    unk_id, eos_id = e1_vocab["specials"]["unk"], e1_vocab["specials"]["eos"]
    c_base = e1_vocab["specials"]["conceptBase"]
    e1_slugs = e1_vocab["conceptSlugs"]

    emit_id = len(tokens)
    tokens.append(EMIT_TOKEN)
    concept_token_id = {}
    for cid in all_ids:
        slug = slug_of(cid)
        tok = f"⟦c:{slug}⟧"
        if cid.startswith("urn:kernel-v0:"):
            if slug not in e1_slugs:
                raise SystemExit(f"ERR_VOCAB: authored slug {slug} missing from e1 vocab")
            concept_token_id[cid] = c_base + e1_slugs.index(slug)
        else:
            concept_token_id[cid] = len(tokens)
            tok_id[tok] = len(tokens)
            tokens.append(tok)
    if len(tokens) > 65535:
        raise SystemExit("ERR_VOCAB: extended vocab exceeds uint16")

    # ---- smoke subset (mechanics only): restricts which concepts EMIT data,
    # never relabels — labels always come from the FULL holdout manifest.
    mock = args.smoke > 0
    train_active = set(train_full[: args.smoke] if mock else train_full)
    tier1_active = set(tier1_full[: max(1, args.smoke // 3)] if mock else tier1_full)

    # ---- tokenize glosses ----------------------------------------------------
    by_concept = {}
    for g in glosses:
        by_concept.setdefault(g["conceptId"], []).append(g)
    for cid, gl in by_concept.items():
        gl.sort(key=lambda x: x["variant"])

    oov = 0
    total_gloss_tokens = 0

    def encode_words(words):
        nonlocal oov, total_gloss_tokens
        ids = []
        for w in words:
            i = tok_id.get(w, unk_id)
            if i == unk_id:
                oov += 1
            total_gloss_tokens += 1
            ids.append(i)
        return ids

    def eval_item(cid, g, ids, tier_name):
        comp = composition.get(cid, {})
        return {
            "conceptId": cid,
            "slug": slug_of(cid),
            "variant": g["variant"],
            "tier": tier_name,
            "sharesStructureWithSeen": comp.get("sharesStructureWithSeen"),
            "featureCoverage": comp.get("featureCoverage"),
            "ids": ids,
            "target": concept_token_id[cid],
        }

    emission_train = []  # (concept_id, variant, token ids WITHOUT eos)
    eval_items = []
    for cid in all_ids:
        gl = by_concept[cid]
        if len(gl) < 5:
            raise SystemExit(f"ERR_GLOSS: {cid} has {len(gl)} glosses (< 5)")
        tid = concept_token_id[cid]
        in_tier2 = cid in set(tier2_full)
        in_tier1 = cid in set(tier1_full)
        for g in gl:
            ids = encode_words(tokenize_text(mapper, g["gloss"])) + [emit_id]
            if in_tier2:
                eval_items.append(eval_item(cid, g, ids, "tier2"))
            elif in_tier1:
                if cid in tier1_active:
                    eval_items.append(eval_item(cid, g, ids, "tier1"))
            elif cid in train_active:
                if g["variant"] == eval_variant[cid]:
                    eval_items.append(eval_item(cid, g, ids, "seen-heldgloss"))
                else:
                    emission_train.append((cid, g["variant"], ids + [tid]))

    # ---- exposure lines (train + tier-1, identical count; never tier-2) -----
    def exposure_lines(seed, cid):
        slug = slug_of(cid)
        stream = DetStream(f"e4/exposure/{seed}/{slug}")
        tid = concept_token_id[cid]
        lines = []
        for _ in range(args.exposure_per_concept):
            frame = CARRIER_FRAMES[stream.next_below(len(CARRIER_FRAMES))]
            pre, post = frame.split("{c}")
            ids = encode_words(tokenize_text(mapper, pre)) + [tid] \
                + encode_words(tokenize_text(mapper, post))
            lines.append(ids)
        return lines

    os.makedirs(args.out, exist_ok=True)
    tier1_set = {concept_token_id[c] for c in tier1_full}
    tier2_set = {concept_token_id[c] for c in tier2_full}
    seed_stats = {}
    for seed in seeds:
        seqs = [ids for (_, _, ids) in emission_train]
        for cid in sorted(train_active) + sorted(tier1_active):
            seqs.extend(exposure_lines(seed, cid))
        order = det_permutation(f"e4/order/{seed}", len(seqs))
        outdir = os.path.join(args.out, f"seed{seed}")
        os.makedirs(outdir, exist_ok=True)
        stream = array("H")
        n_tokens = 0
        for si in order:
            stream.extend(seqs[si])
            stream.append(eos_id)
            n_tokens += len(seqs[si]) + 1
        # ---- fail-closed leakage assertions on the ACTUAL stream ------------
        after_emit = set()
        prev = None
        for t in stream:
            if t in tier2_set:
                raise SystemExit(f"ERR_LEAK: tier-2 token {t} in seed {seed} train stream")
            if prev == emit_id:
                after_emit.add(t)
            prev = t
        if after_emit & (tier1_set | tier2_set):
            raise SystemExit(f"ERR_LEAK: held-out token supervised after EMIT in seed {seed}")
        with open(os.path.join(outdir, "train.bin"), "wb") as f:
            stream.tofile(f)
        seed_stats[str(seed)] = {
            "sequences": len(seqs),
            "emission": len(emission_train),
            "exposure": len(seqs) - len(emission_train),
            "tokens": n_tokens,
        }
        print(f"seed {seed}: {len(seqs)} sequences, {n_tokens} tokens -> {outdir}/train.bin")

    # eval items: assert coverage
    n_t2 = sum(1 for e in eval_items if e["tier"] == "tier2")
    if n_t2 != len(tier2_full) * 5:
        raise SystemExit(f"ERR_EVAL: tier-2 eval items {n_t2} != {len(tier2_full) * 5}")
    with open(os.path.join(args.out, "eval.jsonl"), "w") as f:
        for e in eval_items:
            f.write(json.dumps(e) + "\n")

    candidate_ids = [concept_token_id[c] for c in all_ids]
    with open(os.path.join(args.out, "e4-vocab.json"), "w") as f:
        json.dump({
            "artifact": "e4-vocab",
            "mock": mock,
            "baseVocab": {"path": os.path.abspath(args.e1_vocab),
                          "sha256": sha256_file(args.e1_vocab), "size": base_size},
            "vocabSize": len(tokens),
            "emitId": emit_id,
            "conceptTokenIds": {slug_of(c): concept_token_id[c] for c in all_ids},
            "candidateIds": candidate_ids,
            "tokens": tokens,
        }, f)

    meta = {
        "artifact": "e4-emission-data",
        "mock": mock,
        "provenance": {
            "glossesSha256": gloss_sha,
            "glossHashPin": pin,
            "holdoutSha256": sha256_file(args.holdout),
            "e1VocabSha256": sha256_file(args.e1_vocab),
            "mapperLexiconSha256": sha256_file(args.mapper_lexicon),
        },
        "args": {"seeds": seeds, "exposurePerConcept": args.exposure_per_concept,
                 "smoke": args.smoke},
        "format": {
            "train": "uint16 LE stream; sequences <gloss> EMIT <concept> <eos> (emission) and "
                     "<carrier with concept token> <eos> (exposure); order = "
                     "det_permutation('e4/order/<seed>')",
            "eval": "eval.jsonl items end at EMIT; score next-token logits restricted to "
                    "candidateIds (e4-vocab.json)",
        },
        "counts": {
            "concepts": len(all_ids),
            "train": len(train_active), "tier1": len(tier1_active),
            "tier2": len(tier2_full),
            "evalItems": len(eval_items),
            "evalTier2": n_t2,
            "glossOovTokens": oov,
            "glossTokens": total_gloss_tokens,
            "glossOovRate": (oov / total_gloss_tokens) if total_gloss_tokens else None,
        },
        "assertions": "tier-2 absent from all train streams; no held-out token after EMIT; "
                      "verified on the emitted uint16 streams (fail closed)",
        "seedStats": seed_stats,
    }
    with open(os.path.join(args.out, "meta.json"), "w") as f:
        json.dump(meta, f, indent=2)
    print(f"eval items: {len(eval_items)} (tier2 {n_t2}); OOV rate "
          f"{meta['counts']['glossOovRate']:.4f}; wrote {args.out}/meta.json")


if __name__ == "__main__":
    main()
