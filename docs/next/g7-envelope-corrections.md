# G7 extrapolation-envelope table — f1 / f4 / f5 / g9

- **Author:** Fable experiment-designer/interpreter role (`kern/fable-designer`), 2026-07-10.
  This is the envelope half of the claims-language + envelope corrections bundle
  (`docs/next/feasibility-synthesis.md` §5 row 1), adopting the GPT-5.6 lens-A envelope-audit
  rows as adjudicated in `poc/gpt56-review/SYNTHESIS.md` G7, under the binding invariants of
  the bundle spec `docs/design-claims-envelope-corrections.md` §0 (frozen objects untouched;
  narrowing only; append-only channels).
- **Companion artifacts (already landed):** `docs/research-plan/ERRATA.md` E-1..E-4
  (append-only narrowing of the pinned P1 §4b clauses); the corrected DRAFT envelopes inside
  `registry/experiments/f4.json` and `registry/experiments/f5.json` (lawful pre-freeze edits);
  the claims-language erratum `registry/corrections/f2b-replicate/3-claims-language-erratum.json`
  (L1 alignment relabel, L2 gold-label-independence rename, L3 named-checkpoint narrowing);
  register entries ASM-0160..ASM-0163.
- **Status: designer version.** An external adversarial re-review of this table by the GPT-5.6
  reviewer is a SEPARATE, OPTIONAL step — flagged, not performed here. Nothing below depends
  on it; each row rests on registry objects already in the repo.
- **What this table changes: language width only.** No verdict value, endpoint, fired rule,
  frozen byte, or results-log line changes. The G7 rows for records not yet designed to freeze
  readiness (f6, e9-c, e8-r, family-h0 provenance lint) are freeze-time adoptions tracked in
  `poc/gpt56-review/SYNTHESIS.md` G7 and are deliberately NOT restated here.

DECISION: the per-record envelope readings in the table below are the BINDING forward-language envelopes for f1, f4, f5 and g9; each row narrows a frozen or draft envelope clause to its measured scope and registers the wider reading as an open, never-premise EXTRAPOLATION entry (ASM-0161 for f1 store-size; ASM-0162 for g9 author-capability monotonicity; the f4/f5 anchor-width rule lives in the corrected DRAFT records themselves) [MEASURED: registry/verdicts/f1.json rungs_measured=["S1e5"] + scale_language_licensed="none"; registry/experiments/g9.json (FROZEN-but-UNRUN, verdict absent); registry/experiments/f4.json + registry/experiments/f5.json corrected DRAFT envelopes; docs/research-plan/ERRATA.md E-1/E-2/E-3 — the narrowings rest on the measured rung set and the measured haiku-tier counter-evidence, not on new assumptions].

| Record (status) | Envelope clause as frozen/carried | Why it is over-wide (evidence) | Binding corrected envelope (forward language) | Channel + register |
|---|---|---|---|---|
| **f1** (FROZEN; PASS, audit CONFIRMED) | P1 §4b row HE5 verbatim: "Measured range: Store 10³–10⁶ records"; "Byte claim: store-size axis extrapolates freely (measured B/rec is size-independent)"; RETRO range as directional license | Stale on the measured range: correction c-f1-1 removed the 1e3/1e6 rungs pre-freeze (never built) — the verdict records `rungs_measured=["S1e5"]`, `scale_language_licensed="none"`. Size-independence is CONTRADICTED below ~1e4 records by the measured 2,348-record haiku-tier table+header overhead (~25%; `docs/design-compact-kernel-serialization-v2.md` §3.3; f-efficiency discrepancy D1). Bytes-only by design: the ≤2× retrieval-latency sub-premise was deferred to F5 | The audited 6.7369× is a byte ratio ONLY, on lexical-wn31 (117,791 records) at rung S1e5 ONLY, vs the zstd-19 glosses-only text of the SAME records; it extrapolates UPWARD-ONLY on store size within the same stationary corpus process; no latency claim of any kind; quoting it at any other record tier, corpus shape, or downward store scale re-classifies the statement as EXTRAPOLATION | ERRATA E-1/E-2 (landed); ASM-0161 (wider reading, open); `docs/next/arch-survey.md` M4 row already narrowed |
| **f4** (DRAFT) | HE4 anchor: ToolkenGPT (LLaMA-13/33B) cited toward mechanism at those scales | A published external result licenses mechanism EXISTENCE at its measured scales, never this representation's direction or effect size there (G7; cross-study anchors cannot carry representation-specific effect claims) | "ToolkenGPT (LLaMA-13/33B) anchors mechanism EXISTENCE only — NOT this representation's direction or effect size at those scales (any such statement is EXTRAPOLATION)"; effect size and the text-null comparison stay ≤1.7B; direction to 7B only via the F7 slice | Corrected text already inside the DRAFT record (spec §3.4); binding at freeze — the freeze gate must carry it verbatim |
| **f5** (DRAFT; double-gated) | HE5 anchor + inherited store-range clause: RETRO 150M–7B "with benefit retained" as the license to speak above the measured range; the stale 10³–10⁶ measured-range wording | Same existence-vs-effect width as f4, plus f5 inherits f1's corrected store-size scope (E-1/E-2): the small-store direction is measured-contradicted, and RETRO/InstructRetro say nothing about THIS representation's direction/effect above the programme's own measured range | Envelope as corrected by ERRATA E-1/E-2: measured store range = S1e5 only; byte claim UPWARD-ONLY within the same stationary corpus process; "RETRO ... anchors mechanism EXISTENCE only, NOT this representation's direction or effect size above the measured range; any such statement is EXTRAPOLATION until measured (F7/T3)" | Corrected text already inside the DRAFT record (spec §3.3); binding at freeze; ASM-0161 covers the store-size axis |
| **g9** (FROZEN-but-UNRUN) | HS-A row verbatim: "Extrapolates forward monotonically with author capability (stated assumption: authoring quality non-decreasing in model capability — supported by Law 1); says nothing about host-side scale" | Unsupported projection: no experiment anywhere in the registry measures two author-capability rungs; Law 1 is a licensing synthesis, not a measurement. Additionally g9 is a CROSS-STUDY comparison — the ≥10-point margin vs DeepNSM-8B's published point estimate substitutes for, but does not equal, a controlled head-to-head (published CIs unavailable) | The monotonicity clause is reclassified EXTRAPOLATION and is never a premise; it is always quoted WITH an EXTRAPOLATION tag citing ASM-0162. A g9 PASS licenses the measured author rung only (Fable-class vs the published 8B floor, same metric definitions), carries the cross-study caveat in all narration, and says nothing about host-side scale | Frozen record untouched (byte-frozen); ERRATA E-3 (landed) + ASM-0162 (open) |

## What this table does NOT do

- It does not change any verdict, kill anything, or promote anything; every row is a
  width reduction of language around unchanged measurements.
- It does not license the deflationary readings either: "the f1 ratio would NOT hold
  elsewhere", "g9 authoring would NOT improve with capability" are exactly as unmeasured
  as their optimistic mirrors — ASM-0161/ASM-0162 hold both directions open with named
  resolution paths (a second store rung / a second author rung).
- It does not touch the claims-language half of the bundle (alignment relabel,
  gold-label-independence rename, named-checkpoint narrowing): that half is executed by
  `registry/corrections/f2b-replicate/3-claims-language-erratum.json` with the wider
  readings registered as ASM-0160/ASM-0163, and the binding phrasebook lives in
  `docs/design-claims-envelope-corrections.md` §2.

## Open follow-ups (flagged, not executed)

1. **OPTIONAL external re-review:** hand this table + the erratum to the GPT-5.6 reviewer
   for an adversarial width-check (same channel as `poc/gpt56-review/`). Separate step;
   zero blocking.
2. **Freeze-time inheritance:** f4/f5 freeze gates must verify the corrected envelope text
   survives into the frozen bytes verbatim; the remaining G7 rows (f6, e9-c, e8-r,
   family-h0 member-list lint against P1 §4b) fire at their records' freezes.
3. **Phrase-regression guard (idea only):** extend the claims-check ban-list mechanism to
   the superseded phrases outside quotation contexts (spec §8 item 4).
