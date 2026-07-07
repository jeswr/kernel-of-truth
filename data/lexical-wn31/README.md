# lexical-wn31 — the bulk lexical tier (AxiomsOnly, from WordNet 3.1)

117,791 synset records mechanically extracted from Princeton WordNet 3.1,
one JSONL line per synset, sharded by part of speech. This is the
`AxiomsOnly` stratum of the bulk-kernel design
(`docs/design-bulk-kernel.md`): structural axioms from a fixed source,
**no semantic-adequacy claim**, upgradeable per record later.

## The honesty architecture

The concept-hash design (concept-gist `concept-hash-design.md` §3.1) makes
AxiomsOnly a first-class, visibly-second-class status:

> Every record carries exactly one `cdef:semanticStatus` **inside the
> hash**: `cdef:Prime`, `cdef:Molecule`, `cdef:Explicated`, or
> `cdef:AxiomsOnly`. Consequences: (a) an axioms-only record is
> admissible — the design cannot force semantic quality on permissionless
> minting, only make its absence *visible and endorseable*; (b) a
> federation's endorsement checklist can require `Explicated` for its
> profile […]; (c) tooling renders the status everywhere the concept
> appears. The semantic layer is therefore **opt-in per concept and
> machine-legible**, never silently absent.

Concretely, in every record here:

- **Inside the identity surface:** `schema`, `semanticStatus:
  "AxiomsOnly"`, `pos`, `ssType`, and `axioms` (typed references to other
  synset records; antonym axioms additionally carry numeric `srcWord`/
  `tgtWord` lemma indices — structure, not lexical content).
- **Outside identity, under `annotations`:** `lemmas`, `gloss`,
  `lexFile` (and `markers` where the source has adjective syntactic
  markers). **Glosses and lemmas NEVER enter record identity.** A gloss
  here is a Princeton-authored prose annotation, exactly the mutable
  stratum the hash boundary exists to keep out.
- **`provenance`** (mandatory): source, pinned `sourceVersion` sha256,
  extractor name/version, pinned extraction date. A record is an
  assertion by an extractor about a source, re-derivable byte-identically.

These records do **not** enter the mapper (a pre-registration surface);
they may inform future ceiling measurements only as a separate
"AxiomsOnly-reachable" band.

## Source pin

- `wn3.1.dict.tar.gz` from `https://wordnetcode.princeton.edu/wn3.1.dict.tar.gz`
- sha256 `3f7d8be8ef6ecc7167d39b10d66954ec734280b5bdcd57f7d9eafe429d11c22a`
- Per-dict-file sha256s in `manifest.json`. The source itself is not
  committed (`source/` is gitignored); re-download and `tar xzf` in
  `source/` to regenerate.

WordNet 3.1 Copyright 2011 by Princeton University. All rights reserved.
Used under the WordNet license (redistribution with notice permitted;
THIS SOFTWARE AND DATABASE IS PROVIDED "AS IS" AND PRINCETON UNIVERSITY
MAKES NO REPRESENTATIONS OR WARRANTIES, EXPRESS OR IMPLIED). See the
license header in any WordNet database file.

## Files

| file | what |
|---|---|
| `synsets-{noun,verb,adj,adv}.jsonl` | the records (adj shard holds ss_type `a` and satellite `s`) |
| `manifest.json` | counts, per-relation axiom counts, shard sha256s, index-file cross-checks |
| `structure-report.json` | reference closure, reciprocity, hypernym cycles, depth stats |
| `alignment-kernel-v0.json` | hand-reviewed bridge: kernel-v0 + molecules-v0 → synsets (107 alignments + 1 unaligned, each with confidence) |
| `reachability-report.json` | semantic reachability of the explicated core through this tier |
| `extractor/` | parser, extractor, checks (Node ≥ 20, zero deps) |

Extracted axiom relations: hypernym/hyponym (+instance forms),
part/member/substance meronym–holonym, antonym, entailment, cause (verbs),
similarTo (adjectives). 269,960 axioms total. Deliberately NOT extracted
(follow-ups filed): derivational links, verb groups and sentence frames,
domain pointers, attribute, see-also, participle, pertainym,
sense-frequency weights.

## Verification results (2026-07-07 extraction)

- Deterministic re-extraction: two runs byte-identical (shard sha256s).
- Reference closure: 0 dangling axiom targets out of 269,960.
- Reciprocity (hypernym↔hyponym, meronym↔holonym, antonym, similarTo):
  0 missing inverses.
- Hypernym cycles: **none** in nouns or verbs in WordNet 3.1 (earlier
  WordNet versions shipped a few; had any been found they would have been
  recorded in `structure-report.json`, not broken).
- Noun taxonomy: single root (`entity`), all 82,192 nouns reachable,
  max depth 18, mean 7.95. Verbs: 566 roots, max depth 12, mean 2.52.
- Random-sample audit: 150 synsets (seeded PRNG 0x4d31) re-derived from
  the source via an independent byte-offset access path and independent
  string parsing: **0 errors (0.00%)**.
- Parser unit tests: `node --test data/lexical-wn31/extractor/parse.test.mjs`.

## The bridge (why this tier matters)

`alignment-kernel-v0.json` anchors the hand-authored semantic core (54
Explicated kernel-v0 concepts + 54 molecules-v0) into this taxonomy: 107
alignments (80 high / 25 medium / 2 low confidence; `has-part` unaligned —
WordNet expresses it as pointer structure, not a synset). Semantic
reachability of the core through the bulk tier (undirected
hypernym-graph hops from any anchor):

| k | synsets within k hops | % of 117,791 |
|---|---|---|
| 1 | 1,480 | 1.26% |
| 2 | 5,449 | 4.63% |
| 3 | 14,613 | 12.41% |
| 4 | 29,748 | 25.25% |
| 5 | 46,513 | 39.49% |

That is: ~100 hand-authored concepts put two-fifths of the English
lexicon's synsets within five taxonomy links of an explicated anchor
(48.4% of noun+verb synsets; adjectives/adverbs have no hypernyms and are
only reached if anchored directly). The curve is the honest version of
"coverage" for this tier: proximity to explicated meaning, not possession
of it.

## Regenerate

```bash
cd data/lexical-wn31/source
curl -sSLO https://wordnetcode.princeton.edu/wn3.1.dict.tar.gz && tar xzf wn3.1.dict.tar.gz
cd ../../..
nice -n 10 node data/lexical-wn31/extractor/extract.mjs          # fails closed on hash mismatch
nice -n 10 node data/lexical-wn31/extractor/structure-check.mjs
nice -n 10 node data/lexical-wn31/extractor/sample-check.mjs 150
nice -n 10 node data/lexical-wn31/extractor/align.mjs validate
node --test data/lexical-wn31/extractor/parse.test.mjs
```
