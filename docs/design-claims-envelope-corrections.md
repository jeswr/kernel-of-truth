# Claims-language + envelope corrections bundle — correction SPEC

- **Line id:** `claims-envelope-corrections`
- **Author:** Fable experiment-designer role (`kern/fable-designer`), 2026-07-10. Design
  authority per `docs/next/feasibility-synthesis.md` §5 row 1 executor gate ("Fable-design:
  forward language + successor records only; frozen objects untouched. Opus-executable for
  the mechanical tracker/prose edits once Fable specifies them") and
  `poc/gpt56-review/SYNTHESIS.md` §5 item 1.
- **Kind:** corrections spec, NOT an experiment. No hypothesis is tested, no arm is run, no
  GPU is touched, no record is frozen. Cost: **$0** (CPU-only mechanical edits + one small
  tool fix). The "minimal decisive" unit here is the smallest edit set that removes every
  identified over-wide phrase from forward narration and makes the honest tracker render
  truthfully — with mechanical acceptance checks (§6) standing in for a verdict rule.
- **Consolidates / advances:** feasibility-synthesis §2b (relabel + rename DECISION), §3c
  (tracker rendering defect), §5 row 1 (this bundle); GPT-5.6 review G1/G2/G4/G7
  (`poc/gpt56-review/SYNTHESIS.md`); f-efficiency discrepancies D1 (f1 envelope staleness)
  and D3 (bead kernel-of-truth-97r stale description).
- **Dedup check (2026-07-10):** `registry/ideas.jsonl` (65 lines) has no
  claims-language/corrections idea; `registry/experiments/` (30 records) contains no
  corrections bundle; no `docs/design-*` doc covers this. The sibling line
  `docs/design-truthstyle-2x2-f2-taxonomy.md` is a DIFFERENT line (§5 row 2) and is not
  touched. **Not a duplicate.**

---

## 0. Binding invariants (read before executing anything)

1. **Frozen objects are never edited.** That set here is: every `registry/experiments/*.json`
   with `status: FROZEN`; every `registry/verdicts/*.json`; every
   `registry/assessments/*.json` (append-only kot-assess records); every
   `registry/audits/**`; every `results-log/*.jsonl`; every `reports/auto/**` (render-only
   outputs of `report-gen.py` — regenerate, never hand-edit; since no verdict changes,
   they do not change); and **`poc/f2b-transfer/design.md` + everything under
   `poc/f2b-transfer/`** — the frozen f2b-transfer record references that design doc and its
   harness manifest is a PINNED-AT-INPUTS staged-bytes manifest over `poc/f2b-transfer`, so
   adding or editing ANY byte in that directory while Stage-1 is in flight is forbidden.
2. **Every correction is forward language or a successor record.** Where an over-wide phrase
   lives inside an append-only record, the correction instrument is the successor erratum
   record in §5.1 (precedent: `registry/corrections/a5-llm/1-posthoc-pin-erratum.json`),
   never an edit.
3. **Execution split:** Opus executes the mechanical edits in §3 and the tool fix in §4
   exactly as specified (no discretion, no rewording). Only a Fable identity appends the
   §5 registry lines (`registry/corrections/...`, `registry/assumptions.jsonl`).
4. **Narrowing only.** Every change REDUCES claim width to measured scope. If any specified
   edit would widen a claim, that is a spec bug: stop and return to Fable.
5. `git add` targeted paths only; commit trailer per ops rules.

## 1. Defect register (what is wrong, with evidence)

- **(a) Over-wide attribution label.** Forward narration calls the f2b-replicate lift
  "kernel-content-specific". LOAD-BEARING: the seed-pinned derangement control destroys
  record↔item ALIGNMENT, not NSM content, and under both the real-content and the
  definitional-circularity readings it recovers ~0 of the lift, so it cannot discriminate
  kernel content from correct alignment [MEASURED: registry/verdicts/f2b-replicate.json
  (shuffled recovery −0.0206, ub95 0.1076 < 0.30) + registry/assessments/f2b-replicate.json
  does_not_license; external convergence poc/gpt56-review/SYNTHESIS.md G1].
- **(b) Misnamed confound.** The f2b-transfer confound is described as "ground-truth
  independence"; what Stage-2 actually removes is gold defined by the verifier's own
  string-equality — "gold-label independence" (poc/gpt56-review/SYNTHESIS.md G2; the wider
  name overstates what a PASS would license).
- **(c) Over-closed HC3.** "HC3 closed at the 1.5B (PRM) class" generalises one checkpoint
  — Skywork-o1-Open-PRM-Qwen-2.5-1.5B, a math-domain process verifier applied zero-shot —
  to a class [MEASURED scope: registry/verdicts/f2b-replicate.json PRM arm 0.5267, single
  pinned checkpoint; adjudication poc/gpt56-review/SYNTHESIS.md G4].
- **(d) Stale/over-wide envelopes.** (d1) The f1 envelope clause "store-size axis
  extrapolates freely (measured B/rec is size-independent)" is stale on both ends: only
  S1e5 was measured (c-f1-1 removed the 1e3/1e6 rungs) and size-independence is contradicted
  below ~1e4 records by the measured 2,348-record haiku-tier table+header overhead
  [MEASURED: registry/verdicts/f1.json rungs_measured=["S1e5"],
  scale_language_licensed="none"; registry/assessments/f-efficiency.json D1;
  docs/design-compact-kernel-serialization-v2.md §3.3]. Quoting 6.74× on any other tier or
  corpus is EXTRAPOLATION. (d2) f4/f5 DRAFT envelopes lean on ToolkenGPT/RETRO for
  direction; those papers license mechanism EXISTENCE at their scales, not this
  representation's direction or effect size (G7). (d3) g9's frozen envelope clause
  "extrapolates forward monotonically with author capability" is an unsupported projection
  (G7) — it must be registered and always cited as EXTRAPOLATION.
- **(e) Tracker rendering defect (flagged).** `tools/registry/audit-status.py` derives no
  run-state: FROZEN-but-UNRUN, DRAFT, and run-with-non-PASS-verdict rows all render with the
  same "n/a" columns, distinguishable only by free-text notes; the ledger is also missing a
  row for a VERDICTED experiment (f2b-transfer-llmproxy has
  registry/verdicts/f2b-transfer-llmproxy.json but no ledger line) and for FROZEN
  f2b-transfer. This is the mechanism behind the false "13/14 frozen experiments run +
  audited" framing corrected in feasibility-synthesis §3c.
- **(f) Stale bead text (D3).** Bead `kernel-of-truth-97r`'s description still asserts
  "gains do not transfer off in-house D-QA items"; its own comment thread corrects this as
  an instrument artifact (`poc/f2/runner/f2_runner.py` `ext_vector()` ran model-alone in
  every arm — alone-vs-alone, zero possible flips). Off-slice transfer is UNMEASURED, not
  negative [MEASURED: registry/assessments/f-efficiency.json D3; bead comment 2026-07-09].

## 2. Binding forward-language phrasebook (applies to ALL future docs)

| Superseded phrase | Binding replacement | Basis |
|---|---|---|
| "kernel-content-specific" (of the f2b lift); bare "content-specific" predicated of f2b | "**correct-alignment-specific**" (+ where space allows: "the derangement control cannot discriminate kernel content from correct record↔item alignment") | (a) above |
| "ground-truth independence" / "removes ground-truth dependence" (of f2b-transfer) | "**gold-label independence**" / "removes gold defined by the verifier's own string-equality" | (b) above |
| "HC3 closed at the 1.5B (PRM) class" | "HC3 closed **against the named checkpoint Skywork-o1-Open-PRM-Qwen-2.5-1.5B** (math-domain process PRM, zero-shot, pinned revision) on this task; class-width statements are EXTRAPOLATION" | (c) above |
| bare "6.74×" (f1) | "6.74× **on lexical-wn31 (117,791 records) at rung S1e5 only**; store-size-conditional — upward-only extrapolation on the same corpus process; contradicted at the 2,348-record haiku tier; elsewhere EXTRAPOLATION" | (d1) above |
| RETRO/ToolkenGPT cited as licensing direction/effect for f4/f5 | "…anchors **mechanism existence only**, not this representation's direction or effect size" | (d2) above |
| g9 envelope "extrapolates forward monotonically with author capability" quoted as licensed | always quoted WITH an EXTRAPOLATION tag citing the §5.2 register entry | (d3) above |
| "gains do not transfer off in-house D-QA items" (f2/f2b external slice) | "off-slice transfer is **UNMEASURED** (ext_vector instrument artifact: alone-vs-alone)" | (f) above |

The exception in every case: verbatim quotations of frozen records or of the external
review, clearly marked as quotations (e.g. `poc/gpt56-review/*`, frozen
`poc/f2b-transfer/design.md`), keep their original bytes.

## 3. Mechanical forward-doc edits (Opus-executable, exact strings)

### 3.1 `docs/next/kernel-precision-linter.md` (~line 495) — item (a)

OLD (exact):

```
primary −40.13, `registry/verdicts/f2.json`); the f2b pivot then replicated a real,
kernel-content-specific verifier lift (+0.151 primary) — but on self-authored covered
```

NEW:

```
primary −40.13, `registry/verdicts/f2.json`); the f2b pivot then replicated a real,
correct-alignment-specific verifier lift (+0.151 primary; the derangement control
destroys record↔item alignment, not NSM content, so "kernel-content-specific" is not
licensed — registry/corrections/f2b-replicate/3-claims-language-erratum.json) — but
on self-authored covered
```

Citation for the edit line: [MEASURED: registry/assessments/f2b-replicate.json
does_not_license + registry/verdicts/f2b-replicate.json].

### 3.2 `docs/next/arch-survey.md` (~line 68, M4 row) — item (d1)

OLD (exact substring inside the row):

```
**f1 PASS**: byte ratio **6.74×** vs best general-purpose-compressed gloss-text store (primary endpoint ≥2×), audit **CONFIRMED** cross-vendor (Codex/GPT-5.5, `registry/audits/f1/`).
```

NEW:

```
**f1 PASS**: byte ratio **6.74×** vs best general-purpose-compressed gloss-text store (primary endpoint ≥2×), audit **CONFIRMED** cross-vendor (Codex/GPT-5.5, `registry/audits/f1/`) — scope: lexical-wn31 (117,791 records) at rung S1e5 ONLY, `scale_language_licensed:"none"`; store-size-conditional (upward-only on the same corpus process; contradicted at the 2,348-record haiku tier by measured table+header overhead, `docs/design-compact-kernel-serialization-v2.md` §3.3, f-efficiency D1); quoting 6.74× at any other tier/corpus is EXTRAPOLATION.
```

### 3.3 `registry/experiments/f5.json` (status DRAFT — lawfully editable pre-freeze) — items (d1)+(d2)

In `extrapolation_envelope_verbatim`, replace the exact substring:

```
P1 §4b row HE5 (verbatim): Measured range: Store 10³–10⁶ records (model-free); accuracy leg 70M–160M. Envelope: Byte claim: store-size axis extrapolates freely; accuracy leg ≤410M without T3; direction to 7B via RETRO's published range. Anchor: RETRO measured 150M–7B with benefit retained (and InstructRetro absorption caveat).
```

with:

```
P1 §4b row HE5 as corrected by docs/research-plan/ERRATA.md E-1/E-2 (2026-07-10): Measured range: Store S1e5 (~1.18e5 records, lexical-wn31) ONLY — the 10³/10⁶ rungs were removed pre-freeze by c-f1-1 and never built; accuracy leg 70M–160M. Envelope: Byte claim extrapolates UPWARD-ONLY on store size within the same stationary corpus process (size-independence is contradicted below ~1e4 records by the measured 2,348-record haiku-tier table+header overhead — design-compact-kernel-serialization-v2.md §3.3; f-efficiency D1); accuracy leg ≤410M without T3. Anchor: RETRO measured 150M–7B with benefit retained (and InstructRetro absorption caveat) — this anchors mechanism EXISTENCE only, NOT this representation's direction or effect size above the measured range; any such statement is EXTRAPOLATION until measured (F7/T3).
```

### 3.4 `registry/experiments/f4.json` (status DRAFT) — item (d2)

In `extrapolation_envelope_verbatim`, replace the exact substring:

```
Anchor: ToolkenGPT (LLaMA-13/33B) anchors the mechanism; the text-null overtaking prediction (Law 2) is the declared bias direction.
```

with:

```
Anchor: ToolkenGPT (LLaMA-13/33B) anchors mechanism EXISTENCE only — NOT this representation's direction or effect size at those scales (any such statement is EXTRAPOLATION); the text-null overtaking prediction (Law 2) is the declared bias direction.
```

(Both 3.3 and 3.4 are pre-freeze design-record edits to DRAFT records — permitted; they
become impossible after freeze, which is why they are in this bundle. If either record has
been frozen by execution time, DO NOT edit; fall back to an ERRATA.md line per §3.5.)

### 3.5 NEW file `docs/research-plan/ERRATA.md` (append-only errata ledger) — items (d1)–(d3), (c)

Create with this content (verbatim; future errata append below E-4):

```
# Research-plan errata (append-only; the pinned P1/P8 bytes are NEVER edited)

Authority: registry verdict objects + corrections > frozen prereg > design docs.
Each entry narrows a P1/P8 clause to measured scope; the original rows stay
byte-identical in place so frozen-record pins and family-membership provenance
(P1 §4b) remain verifiable against git history.

- **E-1 (2026-07-10, P1 §4b row HE5).** "Measured range: Store 10³–10⁶ records" is
  STALE: correction c-f1-1 removed the 1e3/1e6 rungs pre-freeze (never built); the
  f1 verdict records rungs_measured=["S1e5"], scale_language_licensed="none"
  (registry/verdicts/f1.json; f-efficiency D1).
- **E-2 (2026-07-10, P1 §4b row HE5).** "store-size axis extrapolates freely
  (measured B/rec is size-independent)" is WITHDRAWN as stated: size-independence
  is contradicted below ~1e4 records by the measured 2,348-record haiku-tier
  table+header overhead (docs/design-compact-kernel-serialization-v2.md §3.3).
  Binding reading: upward-only within the same stationary corpus process;
  elsewhere EXTRAPOLATION (assumption register, f1-scope entry). RETRO anchors
  mechanism existence only, not this representation's direction/effect.
- **E-3 (2026-07-10, P1 §4b row HS-A / g9).** "Extrapolates forward monotonically
  with author capability" is reclassified EXTRAPOLATION (unsupported projection;
  registered in registry/assumptions.jsonl, g9-monotonicity entry). Note also:
  g9 is a cross-study comparison — the ≥10-point margin vs DeepNSM-8B's published
  point substitutes for, but does not equal, a controlled head-to-head.
- **E-4 (2026-07-10, P8 §1.6-adjacent worked example + all HC3 narration).**
  Verdict/claim wording must index PRM comparisons to the NAMED tested checkpoint
  (Skywork-o1-Open-PRM-Qwen-2.5-1.5B, math-domain process PRM, zero-shot, pinned
  revision), never to "the 1.5B class" / "the tested PRM class" as a class claim
  (registry/corrections/f2b-replicate/3-claims-language-erratum.json; GPT-5.6 G4).
```

Optionally (maintainer may veto for sha-churn reasons — flag in the PR): add the single
line `> Errata: see docs/research-plan/ERRATA.md` immediately under the H1 of
`docs/research-plan/01-hypotheses-experiments.md` and
`docs/research-plan/08-stats-and-extrapolation.md`. This changes those files' sha256 (they
are pinned at historical shas by frozen records; no lint verifies current-file shas —
checked `tools/registry/registry-check.py` 2026-07-10 — and git history preserves the
pinned bytes). §4b rows themselves stay byte-identical either way. If vetoed, ERRATA.md
stands alone.

### 3.6 Bead `kernel-of-truth-97r` description (item (f), discrepancy D3)

Opus executes `bd update kernel-of-truth-97r --description '<text below>'` (preserving the
comment thread untouched):

```
F2 post-mortem: FAIL on degenerate R1->R2 gap (R2<=R1 on D-QA); follow-up decided and executed (f2b-replicate).
Frozen HE1 estimand gap_closed(R1,R2) fired FAIL because the scale premise failed on D-QA: R2 model-alone 0.388 <= R1 model-alone 0.394 (denominator -0.006 => gap_closed -40.13; CI [-135.6,-23.1]). Descriptive facts: verifier lift itself is large (R1 0.394->0.635, R2 0.388->0.792 at k=4; gap_closed(R2,R3)=2.73 Holm p~1e-4; beats gloss-self-verify/text-null/PRM all p~1e-4; cost_ratio_vs_S=0.43). HE2 cascade dominance FAILED Holm (worst-budget p=0.047).
EXTERNAL SLICE, corrected reading (supersedes the original description's 'gains do not transfer' claim — see comment 2026-07-09 and registry/assessments/f-efficiency.json D3): NO measurement exists. poc/f2/runner/f2_runner.py ext_vector() called run_alone() unconditionally, so the verify-arm external vector was byte-identical to model-alone at every k (0 flips possible); RT-7a compared alone-vs-alone and could never fire. Off-slice transfer is UNMEASURED, not negative.
STATUS 2026-07-10: successor f2b-replicate FROZEN -> RUN -> PASS -> Gate-A audit CONFIRMED (+0.1507 primary, cost_ratio_vs_R3 0.103; correct-alignment-specific per its derangement control — NOT kernel-content-specific; registry/assessments/f2b-replicate.json). Remaining open legs live elsewhere: f2b-transfer (human judge-1, in flight) and the K-NULL attribution ablation. Verdict: registry/verdicts/f2.json; report: reports/auto/f2/verdict-f2.md.
```

## 4. `tools/registry/audit-status.py` fix — item (e), Opus-executable

Goal: the honest tracker derives run-state from registry ground truth instead of trusting
prose notes, so FROZEN-unrun, DRAFT, run-awaiting-verdict, and verdicted rows are visibly
distinct, and a verdicted experiment can never silently miss the ledger again.

**Derived state per experiment id** (pure reads, no writes — preserve the tool's contract):

- `record = registry/experiments/<id>.json` → `status` field (`DRAFT`/`FROZEN`), else state `UNKNOWN` (lint error).
- `ran` = `results-log/<id>.jsonl` exists AND contains ≥1 line whose JSON has `"phase": "final"`.
- `verdicted` = `registry/verdicts/<id>.json` exists.
- State = `VERDICTED` if verdicted; else `RUN-AWAITING-VERDICT` if ran; else `FROZEN-UNRUN`
  if status==FROZEN; else `DRAFT`.

**Rendering:** add a `state` column between `experiment` and `by`; suffix flags become:
`<- PENDING fable-assess` only when state==VERDICTED and fable=="pending";
`(frozen-unrun)` / `(draft)` derived, never from the note text. `--json` adds
`derived_state` per row. Summary line reports counts BY DERIVED STATE, e.g.:
`15 row(s): 9 verdicted (9 assessed, 0 pending), 0 run-awaiting-verdict, 4 frozen-unrun, 2 draft`
plus, always, a ledger-coverage line listing frozen/verdicted experiment records with no
ledger row.

**Fail-closed lints (exit 2, matching the tool's governance ethos):**

- `ERR_AUDIT_STATE_PENDING_NO_VERDICT`: `fable_interpretive_assessed=="pending"` but state != VERDICTED.
- `ERR_AUDIT_STATE_VERDICT_UNTRACKED`: state==VERDICTED but `fable_interpretive_assessed` not in ("pending","done").
- `ERR_AUDIT_VERDICT_PATH_DRIFT`: row `verdict_path` null while `registry/verdicts/<id>.json` exists (or non-null while absent).
- `ERR_AUDIT_LEDGER_MISSING_VERDICTED`: an id with a verdict file has no ledger row (this fires TODAY for `f2b-transfer-llmproxy` — expected until §4b lands).
- FROZEN-unrun / DRAFT records missing from the ledger are LISTED (warning), not exit-2.

**§4b ledger appends (after the tool fix; append-only, practice-3 schema):** one row for
`f2b-transfer-llmproxy` (verdict PASS-PENDING-AUDIT ⇒ `codex_audited:"pending"`,
`fable_interpretive_assessed:"pending"`, verdict_path
`registry/verdicts/f2b-transfer-llmproxy.json`; executed_by/executor_model/run paths from
its results-log and poc run dir) and one for `f2b-transfer`
(`fable_interpretive_assessed:"n/a"`, note: FROZEN, Stage-1 human-annotation in flight,
verdict_path null). Opus fills the mechanical fields from the run logs; note text must not
make claims beyond "frozen/running/pending" state words.

**Acceptance:** `python3 tools/registry/audit-status.py` exits 0 after §4b; `g2` renders
state `FROZEN-UNRUN` and `f2b-transfer-llmproxy` renders `VERDICTED ... <- PENDING
fable-assess`; deleting the llmproxy row (in a scratch copy) makes the tool exit 2 with
`ERR_AUDIT_LEDGER_MISSING_VERDICTED`. Unit check: `--json` output for g4 carries
`derived_state:"DRAFT"` and for g2 `derived_state:"FROZEN-UNRUN"`.

## 5. Successor registry lines — Fable-authored ONLY (not Opus)

These are drafted verbatim here and appended by a Fable identity at execution time (ids and
dates stamped then; ASM ids are the next four free ids — the register tail sits at 0025 as
of this spec; re-check the tail immediately before appending, parallel lines also mint ids).

### 5.1 `registry/corrections/f2b-replicate/3-claims-language-erratum.json` (next seq after the two prefreeze corrections)

```json
{"kind": "claims-language-erratum", "experiment": "f2b-replicate", "seq": 3,
 "author": "<fable designer pseudonym per RT-14>",
 "authorized_by": "feasibility-synthesis SS5 row 1 executor gate (Fable-design: forward language + successor records only; frozen objects untouched) + poc/gpt56-review/SYNTHESIS.md SS5 item 1; spec docs/design-claims-envelope-corrections.md",
 "date": "<execution date>",
 "frozen_objects_untouched": ["registry/experiments/f2b-replicate.json", "registry/verdicts/f2b-replicate.json", "registry/assessments/f2b-replicate.json", "registry/assessments/f-efficiency.json", "poc/f2b-transfer/design.md", "reports/auto/"],
 "corrections": [
  {"id": "L1", "phrase_superseded": "kernel-content-specific (and bare 'content-specific' predicated of the f2b lift)",
   "binding_reading": "correct-alignment-specific: the seed-pinned derangement control destroys record<->item ALIGNMENT, not NSM content; any aligned deterministic answer table would produce the same lift and die under the same derangement, so the control cannot discriminate kernel content from correct alignment",
   "applies_to": ["registry/assessments/f2b-replicate.json promotions[] ('the lift is kernel-content-specific')", "registry/assessments/f2b-replicate.json findings[] pass statement on shuffled recovery", "all forward narration of the f2b-replicate PASS"],
   "basis": "MEASURED: registry/verdicts/f2b-replicate.json shuffled recovery -0.0206 (ub95 0.1076 < 0.30) + registry/assessments/f2b-replicate.json does_not_license; convergent external adjudication poc/gpt56-review/SYNTHESIS.md G1"},
  {"id": "L2", "phrase_superseded": "ground-truth independence / removes ground-truth dependence (of f2b-transfer)",
   "binding_reading": "gold-label independence: a Stage-2 PASS removes gold-defined-by-the-verifier's-own-string-equality only, not ground-truth dependence in general; the frozen poc/f2b-transfer/design.md retains its original wording (pinned) and assessors map the terms explicitly at assessment time",
   "applies_to": ["all forward narration of f2b-transfer and f2b-transfer-llmproxy"],
   "basis": "registry/assessments/f2b-replicate.json does_not_license; poc/gpt56-review/SYNTHESIS.md G2"},
  {"id": "L3", "phrase_superseded": "HC3 closed at the 1.5B (PRM) class",
   "binding_reading": "HC3 closed against the NAMED checkpoint Skywork-o1-Open-PRM-Qwen-2.5-1.5B (math-domain process PRM, zero-shot, pinned revision) on d-qa-r at matched FLOPs - one checkpoint, not a class; class-width statements are EXTRAPOLATION; the successor stub f2b-frontier-prm must carry a task-matched verifier arm whose supervision uses external gold (never membership-string labels)",
   "applies_to": ["registry/assessments/f2b-replicate.json promotions/tree_impact/stubs f2b-frontier-prm", "registry/assessments/f-efficiency.json forks_resolved HC3 + tree_impact", "all forward narration"],
   "basis": "MEASURED scope: registry/verdicts/f2b-replicate.json PRM arm 0.5267 (single pinned checkpoint); poc/gpt56-review/SYNTHESIS.md G4"}],
 "non_retroactivity": "No verdict value, endpoint, fired rule, or assessment verdict field changes. This record narrows LANGUAGE to measured scope. Where an assessment sentence and this erratum conflict, this erratum is the current reading; the underlying verdict objects are untouched and already consistent with the narrowed reading.",
 "schema_version": "kot-correction/1"}
```

### 5.2 `registry/assumptions.jsonl` appends (4 lines; schema per register tail; all `load_bearing: false`, all `status: "open"`)

1. f2b-content id-next: claim "The f2b-replicate lift (+0.1507) is kernel-CONTENT-specific
   — i.e. NSM semantic content beyond correct record<->item alignment (the reading the
   derangement control cannot support)." tag EXTRAPOLATION; backing_ref
   "registry/verdicts/f2b-replicate.json; registry/assessments/f2b-replicate.json
   does_not_license; poc/gpt56-review/SYNTHESIS.md G1"; resolution_path "K-NULL
   aligned-non-NSM-store ablation (content-injection map first) OR human f2b-transfer
   Stage-1/2".
2. f1-scope id-next: claim "The f1 byte ratio 6.7369x holds at store tiers or corpora other
   than lexical-wn31 at S1e5 (~1.18e5 records)." tag EXTRAPOLATION; backing_ref
   "registry/verdicts/f1.json rungs_measured=[S1e5] scale_language_licensed=none;
   counter-evidence at the 2,348-record haiku tier
   docs/design-compact-kernel-serialization-v2.md SS3.3; f-efficiency D1 (upward-only)";
   resolution_path "measure the pack at the d-st store rungs (f5 inputs) or a committed
   small-tier corpus".
3. g9-monotonicity id-next: claim "Authoring quality (g9 composite validator-pass rate) is
   non-decreasing in author-model capability ('extrapolates forward monotonically with
   author capability', P1 SS4b row HS-A)." tag EXTRAPOLATION; backing_ref
   "registry/experiments/g9.json envelope (frozen; clause reclassified by
   docs/research-plan/ERRATA.md E-3); poc/gpt56-review/SYNTHESIS.md G7"; resolution_path
   "repeat the g9 protocol at a second author-model rung (shares infrastructure with the
   N19 explication-reliability trial)".
4. hc3-class id-next: claim "The f2b-replicate PRM-beating result extends beyond the named
   Skywork-o1-Open-PRM-Qwen-2.5-1.5B checkpoint to trained PRMs of the 1.5B class
   generally." tag EXTRAPOLATION; backing_ref "registry/verdicts/f2b-replicate.json (PRM arm
   0.5267, one pinned checkpoint); poc/gpt56-review/SYNTHESIS.md G4"; resolution_path
   "f2b-frontier-prm successor with a task-matched verifier arm supervised on external gold".

DECISION: the two renamings ((a),(b)) and the HC3 narrowing ((c)) are adopted as binding forward language because each RESTORES a claim to the scope its own control measured — the adoption rests on the measured control behaviour, not on new assumptions [MEASURED: registry/verdicts/f2b-replicate.json + registry/assessments/f2b-replicate.json does_not_license].
The four register entries above capture the WIDER readings as open EXTRAPOLATIONs so no
future doc can silently re-promote them.

## 6. Acceptance checks (the "verdict rule" of this bundle — all mechanical, $0)

1. Phrase sweep clean:
   `grep -rn "kernel-content-specific" docs/ --include="*.md" | grep -v "gpt56-review\|ERRATA\|design-claims-envelope-corrections\|feasibility-synthesis"` → empty;
   same for `"ground-truth independence"` (excluding `poc/f2b-transfer/`, `poc/gpt56-review/`, quotations) and `"1\.5B class"` in docs/.
2. `python3 tools/registry/audit-status.py` → exit 0, `state` column present, g2 ≠ any
   pending row visually; scratch-copy deletion test per §4 fires exit 2.
3. `bd show kernel-of-truth-97r` description contains "UNMEASURED" and no longer contains
   "do not transfer".
4. `python3 tools/registry/registry-check.py --claims` (and default checks) green — in
   particular the claims-check over docs/ still passes with this spec + ERRATA.md present.
5. `git diff --stat` touches ONLY: the two docs in §3.1/§3.2, the two DRAFT records in
   §3.3/§3.4, new `docs/research-plan/ERRATA.md` (+ optional two pointer lines),
   `tools/registry/audit-status.py`, `registry/audit-status.jsonl` (appends),
   `registry/corrections/f2b-replicate/3-claims-language-erratum.json` (new),
   `registry/assumptions.jsonl` (appends). ANY other path in the diff = stop.

## 7. What this bundle licenses vs does NOT

- Licenses: honest forward narration at measured scope; a truthful tracker; nothing else.
- Does NOT license the deflationary conclusion either: "the lift is ONLY alignment" is as
  unmeasured as "the lift is kernel content" — both readings stay open until K-NULL or
  human f2b-transfer reads out (feasibility-synthesis §3a/§3d). This bundle changes no
  verdict, kills nothing, promotes nothing.
- Does NOT edit any frozen object, any results-log, any auto-report, or anything under
  `poc/f2b-transfer/`.

## 8. Honest failure modes

1. **Scope creep into pinned bytes** — e.g. "fixing" `poc/f2b-transfer/design.md` or an
   assessment JSON directly. Guard: §0 invariant + §6 check 5 diff allowlist.
2. **P1/P8 sha churn** — the optional pointer lines change files pinned (historically) by
   every frozen record. Mechanically inert today (no current-file sha lint), but flag to
   the maintainer; ERRATA.md alone suffices if vetoed.
3. **ASM-id collision** — parallel design lines mint ids concurrently; re-read the register
   tail in the same session as the append, and re-run `registry-check --claims` after.
4. **Phrase regression** — future docs re-introduce the wide phrases. Cheapest guard
   (follow-up idea, NOT executed here): extend the claims-check ban-list mechanism with
   "kernel-content-specific" and "ground-truth independence" outside quotation contexts.
5. **Tool-fix false alarms** — legacy ledger rows (backfilled pre-practices) could trip the
   new lints; the states derived for the CURRENT 15 rows were hand-verified in this spec's
   session (9 verdicted / 4 frozen-unrun / 2 draft) and only the missing-llmproxy row
   should fire before §4b.
6. **Bead description length limits** — if `bd` truncates, keep paragraphs 1+3 (corrected
   reading + status) and move the descriptive cells to a comment; the correction sentence
   must survive verbatim.

## 9. Cost + compute

$0. CPU-only text edits, one ~60-line Python tool change, two ledger appends, one bead
update. No GPU, no Modal, no model calls. Executable in one Opus session + one Fable append
session; independent of every in-flight experiment (nothing here blocks or is blocked by
f2b-transfer Stage-1).
