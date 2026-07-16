# f1k-eval-v1 — known-concept item lists + frozen scored templates + span sidecars

Completes `registry/experiments/f1k.json` corpus pin `f1k-eval-v1`
("known-concept item lists (test/dev/off-concept-guard ids + frozen scored
templates + per-item span sidecars), produced by the frozen mechanical
filter + trigger map"; pinned by ops amendment at freeze-manifest (A)/(6),
before any test prefill). Built by
`poc/glm52-probe/f1k-harness/corpora/build_corpora_96.py` — 2026-07-15 fable REVISION-6 data-construction pass ($0).
**supersedes the 2026-07-13 designer-23 kernel-v0-only pass (49 clusters, n=1440) — REVISION-6 frozen geometry C=96 / n_test=1573, maintainer-approved 2026-07-15.**

## Geometry (REVISION-6, the headline)
Test items are the EXACT materialization of the frozen askability-screen
allocation at the maintainer-approved geometry: **C = 96 clusters,
n_test = 1573**, per-cluster counts equal to
`poc/f1k-askability/reports/power-report-n1573.json geometry.m_list_by_rank`
element-by-element in rank order (verified fail-closed at build; m_min 10,
m_mean 16.3854, m_max 18; **96/96 clusters at m >= 8** — the registered
C>=65 each-m>=8 gate is SATISFIED). The redacted-input hash was re-verified
against the frozen pre-screen pin and the re-derived selection cross-checked
against `candidate-report.json` before any item was written.

## Contents
- `items/test.jsonl` (1,573 = the approved REVISION-6 cap), `items/dev.jsonl`
  (96), `items/guard.jsonl` (60 off-concept: zero trigger match anywhere,
  DES §2.5) — each row: item id, source provenance, question/options/gold in
  PUBLISHED order, frozen template BYTES + sha256, CHARACTER-level
  §R4-resolved spans (carrier-slot ids = askability rank - 1), d3-text
  prompt rendering (test/dev), tags (`multi-concept`, `option-trigger`).
- `template-spec.json` — CARRIED OVER unchanged from the 2026-07-13 pass
  (universe-independent): the §R1.1 template bytes, rendering rule,
  tie-break, and the DETERMINISTIC TOKENIZER-DERIVATION RULE for the fields
  this pass cannot produce.
- `source/` — the five pinned benchmark snapshots (OP-1) + lock file,
  CARRIED OVER unchanged (sha256 re-verified against the pins this pass).
- `coverage-report.json` — realized (C, m) at the new geometry, power-gate
  arithmetic, composition.

## What is BLOCKED this pass (honest list, unchanged)
`template_tokens`, `label_token_ids`, token-level `spans`,
`d3_template_tokens`, and the single-token label verification are pure
functions of this corpus + the GLM-5.2 tokenizer, which is pinned only at
bring-up (ASM-1971); a $0 no-model pass cannot fetch it. Derivation rule:
`template-spec.json .tokenizer_derivation_rule`.

CommonsenseQA uses the VALIDATION split (test gold labels are not
published; the scorer needs gold). MMLU/ARC/OpenBookQA use their published
test splits.
