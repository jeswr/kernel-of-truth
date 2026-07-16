# f1k-trigger-map-v1 — phrase→concept trigger map (F1-K lexical gate)

Completes `registry/experiments/f1k.json` corpus pin `f1k-trigger-map-v1`
("phrase->concept trigger map expanded to all kernel concepts with registered
explications (WordNet lemma/derivational surface expansion) + gate precedence
rules"; pinned at freeze-manifest (A), before ANY spend). Built by
`poc/glm52-probe/f1k-harness/corpora/build_corpora_96.py` — 2026-07-15 fable REVISION-6 data-construction pass ($0).
**supersedes the 2026-07-13 designer-23 kernel-v0-only pass (49 clusters, n=1440) — REVISION-6 frozen geometry C=96 / n_test=1573, maintainer-approved 2026-07-15.**

- **Concept universe (OP-3 SUPERSEDED, REVISION-6):** the kernel-v0 +
  kernel-v1 synset-deduped join of the frozen askability screen
  (`poc/f1k-askability/screen.py load_kernel_records`): the universe listed
  in `trigger-map.json` (counts in `manifest.json`), with the retention-filtered
  gate pool and the frozen selected 96 (ranks 1..96 of
  `poc/f1k-askability/reports/candidate-report.json`, 45 kernel-v0 + 51
  kernel-v1) marked per concept. The 2026-07-13 kernel-v0-only reading
  (C<=54, registered power gate unsatisfiable) is void; at this universe the
  gate C>=65 each m>=8 is SATISFIED (96/96 at the approved n_test=1573).
- **Surface expansion:** aligned WN3.1 synset lemmas + derivationally-related
  ("+" pointer) word lemmas, from the in-repo pinned `data/lexical-wn31/`
  source dict (kernel-v0 via `alignment-kernel-v0.json`; kernel-v1 synsets
  inline) — the [BC] `build_triggers` rule, unchanged.
- **Gate precedence (frozen, DES §R4):** exactly one carrier per gated
  position; overlap → longest trigger match, then earliest span start, then
  lowest concept index; label tokens never triggers; multi-concept items
  tagged. Matching/resolution runs over the retention-filtered gate pool
  (the screen's frozen counting universe; `in_gate_pool` per concept).
- **Matching rule (OP-4, unchanged):** case-insensitive whole-word match;
  see `trigger-map.json .matching_rule`.

Files: `trigger-map.json` (the map: joined universe, canonical index = URN
byte order, triggers + provenance + gate-pool/selection marks),
`manifest.json`.
