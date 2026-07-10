# G3 annotation protocol (materials part — fixed with the corpus)

Procedure for the two human annotators of the G3 semantics-pin study
(`registry/experiments/g3.json`; GATE-H stage `g3.annotate`). This file is
part of the pinned materials so that the instrument is fixed before any
annotator is sourced. Blinding requirements implement the frozen record's
"blind to hypotheses" arm and P7 finding (ii). [STIPULATED: ASM-0182]

## Roles and blinding

- **Two annotators, independent.** No discussion of items until both have
  submitted complete sheets. The second annotator must be a genuinely
  independent human (P3 O-3); if the maintainer annotates, their pass happens
  before reading any kernel-side design material beyond these sheets.
- Annotators never see: `design-intent.jsonl`, `manifest.json`, `README.md`,
  the research plan, the 10% thresholds, or any statement of which outcome
  helps which hypothesis.
- Annotators see only the two generated sheets described below plus the
  instruction text in this file's "Instructions to annotators" section.

## Sheet generation (mechanical, from the pinned files)

- **Pass A sheet** — one row per instance, in `instances.jsonl` file order:
  `instance_id`, `text`, `target`. Response column: `q1` ∈ {yes, no,
  cannot-say}.
- **Pass B sheet** — one row per instance, same order: `instance_id`, `text`,
  `bindings`, the full enumerated condition list for the instance's
  `condition_set_id` (from `conditions.jsonl`), **without** the concept word,
  label, or `target`. Response columns: `q2` ∈ {yes, no, cannot-say};
  `q2_failing_conditions` (list of `cid`s, required when `q2 = no`).
- Each annotator completes **all of pass A before opening pass B** (Q1 must
  not be contaminated by the condition sets).

## Instructions to annotators (verbatim on the sheets)

Pass A: "For each numbered situation, read the description, then the claim
beneath it. Judge whether the claim is true of the situation as you would
ordinarily use the underlined word. There are no trick questions and no
expected answers; 'cannot-say' is allowed but use it sparingly. Judge each
situation on its own."

Pass B: "For each numbered situation you will see a short list of conditions
(K-sets) and a note fixing who or what plays each role. Mark 'yes' only if the
situation satisfies EVERY listed condition; otherwise mark 'no' and list the
numbers of the conditions that fail. Judge only what the conditions literally
say against what the description says; do not guess at what the conditions
might be 'getting at'."

## Derived quantities (fixed by the frozen design; not annotator-facing)

Per instance and annotator: **necessity violation** iff q1 = yes and q2 = no;
**sufficiency violation** iff q1 = no and q2 = yes (P1 HS3 / F7 verbatim:
"an instance of C failing Π(C)" / "a non-C satisfying Π(C)"). The metrics
consumed by `analysis/g3.py` are the summed counts plus the 2×2 agreement
table on the per-instance necessity-violation indicator
(`annot_both_yes / annot_both_no / annot_a_yes_b_no / annot_a_no_b_yes`);
κ < 0.4 trips INSTRUMENT-INVALID, never FAIL.

## Open run-stage decisions (NOT fixed by these materials — fix before
annotation starts, at `g3.annotate`)

1. Annotator sourcing (O-3, deferred by maintainer direction; MTurk is the
   leading paid option, maintainer + colleague at $0 remains open).
2. Combination rule from two annotators' judgments to the single violation
   counts (the g2 precedent is blind adjudication of disagreements before
   scoring; the frozen g3 record fixes only n_judgments = 200 and that κ is
   reported).
3. Treatment of `cannot-say` responses (proposal: they are neither violations
   nor satisfactions and are flagged in the run log; if they exceed ~5% of
   judgments the instrument is re-examined before readout).
