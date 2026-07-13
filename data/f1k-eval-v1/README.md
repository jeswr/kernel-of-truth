# f1k-eval-v1 — known-concept item lists + frozen scored templates + span sidecars

Completes `registry/experiments/f1k.json` corpus pin `f1k-eval-v1`
("known-concept item lists (test/dev/off-concept-guard ids + frozen scored
templates + per-item span sidecars), produced by the frozen mechanical
filter + trigger map"; pinned by ops amendment at freeze-manifest (A)/(6),
before any test prefill). Built by
`poc/glm52-probe/f1k-harness/corpora/build_corpora.py` — 2026-07-13 designer-23 data-construction pass ($0).

## Contents
- `items/test.jsonl` (1,440 = the registered cap, SSR-REV3.1 item 4),
  `items/dev.jsonl` (96), `items/guard.jsonl` (60 off-concept: zero trigger
  match anywhere, DES §2.5) — each row: item id, source provenance,
  question/options/gold in PUBLISHED order, frozen template BYTES + sha256,
  CHARACTER-level §R4-resolved spans (carrier-slot ids), d3-text prompt
  rendering (test/dev), tags (`multi-concept`, `option-trigger`).
- `template-spec.json` — the §R1.1 template: header/cue bytes (OP-2 draft
  for (A) entry 1), rendering rule, tie-break, char-level trigger-freedom
  verification, and the DETERMINISTIC TOKENIZER-DERIVATION RULE for the
  fields this pass cannot produce.
- `source/` — the five pinned benchmark snapshots (OP-1) + lock file.
- `coverage-report.json` — realized (C, m), power-gate arithmetic, verbatim
  subset composition (SS2.7).

## What is BLOCKED this pass (honest list)
`template_tokens`, `label_token_ids`, token-level `spans`,
`d3_template_tokens`, and the single-token label verification are pure
functions of this corpus + the GLM-5.2 tokenizer, which is pinned only at
bring-up (ASM-1971); a $0 no-model pass cannot fetch it. The run driver's
`load_eval_manifest` consumes the TOKEN-level manifest — deriving it from
this corpus via `template-spec.json .tokenizer_derivation_rule` is a
mechanical pre-(6) step (contract mismatch flagged in
`poc/glm52-probe/f1k-harness/corpora/driver-contract-check.json`).

## Power-gate headline (read this first)
Realized test composition: 49 clusters, **46 with m >= 8** — the registered
gate needs **>= 65 clusters each m >= 8** (ASM-2271). Under the pinned
54-concept kernel universe (OP-3) the gate is UNSATISFIABLE: this is the
design's own registered PRE-RUN RETURN ("the scale gate biting", DES §8 /
SSR-REV2.2), surfaced at corpus construction, not a build defect. F1-K must
not run on this corpus without a maintainer ruling on the coverage-vs-power
shortfall.

CommonsenseQA uses the VALIDATION split (test gold labels are not
published; the scorer needs gold). MMLU/ARC/OpenBookQA use their published
test splits.
