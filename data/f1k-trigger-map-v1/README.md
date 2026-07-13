# f1k-trigger-map-v1 — phrase→concept trigger map (F1-K lexical gate)

Completes `registry/experiments/f1k.json` corpus pin `f1k-trigger-map-v1`
("phrase->concept trigger map expanded to all kernel concepts with registered
explications (WordNet lemma/derivational surface expansion) + gate precedence
rules"; pinned at freeze-manifest (A), before ANY spend). Built by
`poc/glm52-probe/f1k-harness/corpora/build_corpora.py` — 2026-07-13 designer-23 data-construction pass ($0). NOT frozen: the
coordinator freezes this at (A) after adopting/amending the OP decisions in
`manifest.json`.

- **Kernel source (OP-3, LOAD-BEARING):** `data/kernel-v0/` — the ONLY kernel
  corpus the frozen record pins (kot-corpus-hash/1
  `8209cada…7c809`, reproduced at build). 54 registered explications; the
  `gloss` field is the explication text rendering. ALTERNATIVE READINGS of
  "all kernel concepts with registered explications" the coordinator must
  rule on at (A): (a) kernel-v0 only = 54 concepts (THIS BUILD; C <= 54);
  (b) kernel-v0 + kernel-v1 Stage-A with v1's registered supersession of the
  4 word concepts = 61 (C <= 61); (c) v0 + v1 ignoring supersession = 65
  (C <= 65, and word/sense triggers double-book the same surfaces). Under
  (a) and (b) the registered power gate C >= 65 (ASM-2271) is UNSATISFIABLE
  and F1-K pre-run-RETURNS with the measured coverage-vs-power shortfall;
  under (c) it is satisfiable only if every concept reaches m >= 8, which
  the realized filter output contradicts (see
  `data/f1k-eval-v1/coverage-report.json`). Molecules-v0 is excluded: the
  design bounds the universe by "the kernel's <100 concepts" (§R3.2) and
  molecules are not kernel concepts.
- **Surface expansion:** aligned WN3.1 synset lemmas + derivationally-related
  ("+" pointer) word lemmas, from the in-repo pinned `data/lexical-wn31/`
  source dict via `alignment-kernel-v0.json` (kot-lex-align/1,
  hand-reviewed). `has-part` is UNALIGNED in the hand-reviewed alignment
  (WordNet holds the relation as pointer structure) → empty trigger set,
  disclosed, not padded.
- **Gate precedence (frozen, DES §R4):** exactly one carrier per gated
  position; overlap → longest trigger match, then earliest span start, then
  lowest concept index; label tokens never triggers; multi-concept items
  tagged.
- **Matching rule (OP-4):** case-insensitive whole-word match; see
  `trigger-map.json .matching_rule`.

Files: `trigger-map.json` (the map: 54 concepts, canonical index = URN byte
order, triggers + provenance), `manifest.json`.
