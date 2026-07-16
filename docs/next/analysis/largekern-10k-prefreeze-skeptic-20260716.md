# largekern-10k — pre-freeze skeptic attack memo (freeze-blocking deliverable)

> Author: designer-21 (freeze pass; freezes the record as `writer-4` — the registry
> pseudonym enum has no designer role). Date: 2026-07-16. Scope: the WordNet-10k
> drafting pilot registry record `largekern-10k` against the GO-TO-FREEZE design
> `docs/next/design/gpt56-draft-pipeline-large-kernel.md` (r5) and the maintainer
> P7 ruling (kernel-of-truth issue #48, option 2). This memo attacks the design
> BEFORE freeze, per the experiment-designer role contract (deliverable 4). It
> authorizes nothing.

Each attack states the strongest form I could construct, then what the frozen
record does about it. Residual risks are listed at the end, not hidden.

## A1. Oracle leakage — is the "gold label" the mechanism's own accept test?

Attack: endpoint 1 (accept-rate alpha) is computed by the SAME validator/lint
stack the pipeline uses to accept drafts. A pipeline that drafts toward its own
gates trivially inflates alpha — the F2/D-QA lesson (accept test == the record
that defined gold) in production-pipeline form.

Disposition: partially TRUE by construction and disclosed as such — alpha is a
*throughput/legality* endpoint, never a truth or quality claim (spec §10.5
honesty cap; the g9 rule that mechanical legality is an UPPER BOUND is restated
in the record). The anti-oracle control is endpoint 4: a blind human 4-binary
review (n = 200, seeded stratified, reviewer never the drafter, operator, or any
model seat; sheet shows no model identity, no coverage rank, no benchmark items)
whose floor h = 0.60 GATES PROCEED. alpha alone can never PROCEED: the frozen
`proceed_gate` conjunction requires the human leg, and its absence is
INSTRUMENT-INVALID, not a pass-by-default (analysis selftest covers this
channel). Residual: h is a *sampled* estimate of draft quality, not semantic
adequacy of the kernel — the envelope forbids quoting it as that.

## A2. Endpoint gameability

- alpha gameable by prompting toward trivially-legal drafts: bounded by the
  gloss lints (scholarly standard 1–9, 15–100 words, non-circularity), the
  8-token leakage reject, the G1 duplicate-identity profile, and the h gate —
  trivially-legal-but-vacuous drafts fail the human 4-binary.
- kappa gameable by inflating uncached input: kappa is computed from provider
  `usage` fields settled into the hash-chained ledger; fabrication requires
  falsifying the committed ledger export the auditor recomputes from (run !=
  audit; the verdict is a pure function of that export).
- $c gameable by denominator choice: $c's numerator is pinned as ALL pilot API
  spend (micro-pilot + calibration + every failed/quarantined/repair call), the
  denominator as `accepted` only; and per issue #48 the $c ceiling is ADVISORY —
  it cannot be gamed INTO a PROCEED because it does not gate one. Its breach
  flag (`/analysis/cost_advisory_breach`) is a declared output field, so it
  cannot be silently dropped either.
- Attempted-denominator gaming (mark hard items PROVIDER_FAILED to shrink the
  alpha denominator): capped by the 2% instrument bound — >2% PROVIDER_FAILED is
  INSTRUMENT-INVALID (INVALID-RERUN), and the ledger state machine separates
  content rejection (never retried past R=2, stays in the denominator) from
  provider failure (never quarantines content); P5 tests cover the routing.

## A3. Degenerate denominators (the F2 lesson)

Attack: a ratio endpoint with a collapsible denominator produces artifact
verdicts.

Disposition: all four endpoints are ABSOLUTE levels against frozen floors —
no gap-closure ratios, no between-arm denominators. Denominators are pinned:
attempted = 10,000 − provider_failed (≥ 9,800 whenever the instrument gate
holds), human n = 200 exactly, kappa's denominator is total input tokens (> 0
whenever any call was billed), $c's is accepted (accepted = 0 leaves $c null —
which cannot flip anything: $c is advisory and every gating comparison is
against always-boolean/numeric fields; division guards selftested).

## A4. Baseline asymmetry / the two standing nulls

Attack: no kernel-as-text null, no shuffled-kernel control — Law 2 violation?

Disposition: the pilot makes NO end-task, correctness, or efficiency-thesis
claim for the nulls to oppose — it prices drafting throughput + mechanical
acceptance + sampled human quality of a PRODUCTION instrument (spec §10.5;
envelope verbatim in the record). The record's `arms_mandatory_baselines`
declares the comparator honestly: the frozen numeric floors + the §5.2 modelled
envelope, and states that any CONSUMER experiment quoting drafted records must
carry its own Law-2 nulls (the ModelDrafted status gate + seat-ledger machinery
make silent consumption fail closed, `ERR_STATUS_INELIGIBLE`). A PASS here is
"the drafting pipeline is viable at these floors", nothing more.

## A5. Leakage into the worklist or prompts

Attack: the sample or prompt could encode eval/benchmark information.

Disposition: the worklist builder is mechanical and item/kernel-blind (inputs:
pinned WN31 shards + frame hash + 107-synset frozen-overlap denylist; no
benchmark bytes, no kernel explication text, no model outputs); the prompt
contains only headword + synset id + WN gloss + pinned extracts + the cached
contract blocks; the 8-token leakage lint is a hard reject. The ADOPTED sample
(ASM-2499) was drawn during the $0 mock build by a pinned seeded rule
(ASM-2498) — at draw time no real-model output existed anywhere in the process,
and the mock drafter is deterministic seeded junk, so the draw cannot encode
real-model performance. Adoption is disclosed; a re-draw is a new experiment id.

## A6. Undecidable / underpowered gates

Attack: a Wilson-bound gate undecidable at the planned n (RT-4).

Disposition: both Wilson gates carry freeze-checked decidability declarations
(constraint 9): alpha (threshold 0.70, n = 9,800, planning expected rate 0.80
[STIPULATED ASM-2500 — a decidability input, never a premise; the true volume
accept-rate is the ASM-2434 open unknown this pilot measures]) and h (threshold
0.60, n = 200, planning expected rate 0.70). The z = 1.96 operationalization is
pinned in the analysis script and PROVEN equivalent to the spec's ">= 134/200"
wording by selftest (134 passes, 133 fails). kappa and $c are deterministic
point values — no power question exists for them.

## A7. Freeze-then-fill abuse (PINNED-AT-INPUTS placeholders)

Attack: deferring gen-settings / P–S–O / cachePrefixHash / tokenizer / snapshot
id to ops amendments lets the runner tune the instrument post-freeze.

Disposition: the placeholders are declared IN the frozen record with the P2 P-9
rule restated: each must be completed by a logged ops amendment BEFORE any
main-run spend, none may touch `/pins/analysis_script`, the endpoints, the
floors, the kill ladder, or the budget — verdict-gen enforces the analysis-pin
immutability mechanically. The floors and denominators are frozen NOW; what the
placeholders pin is instrument plumbing (which prefix bytes, which snapshot id),
all of it disclosed in provenance and none of it able to move a floor.

## A8. Mock-green overclaim

Attack: quoting the mock e2e (alpha_LB 0.951, kappa 0.864, $0.0192/accepted) as
evidence the real run will pass.

Disposition: the record tags the mock as MECHANICS-ONLY evidence (the $0 green
mock the role contract requires) and bans quoting its rates as expected real
rates (ASM-2496: the failure mix is pinned mock convention). The real
accept-rate remains the registered open unknown (ASM-2434, EXTRAPOLATION,
resolution_path = this pilot) — the freeze tool will emit its non-fatal PAUSE
flag for exactly this, which is correct and by design: the experiment IS the
resolution path.

## A9. Run/grade/audit separation

Attack: the designer who froze the gate also grades it.

Disposition: no. This pass designs and freezes only (identity writer-4 ==
designer-21, disclosed here); the campaign is run by runner-1 under the frozen
record; the verdict is verdict-gen's pure function; a computed PASS is
PASS-PENDING-AUDIT until the cross-vendor auditor confirms. The analysis input
is the committed ledger export + review sheet, both recomputable by the auditor.

## A10. Known interface wrinkle (disclosed, not resolved here)

The pinned `check_family_disjoint.check_status_eligibility` reads per-file
`.json` records keyed on `status`; kernel-v1-draft shards are JSONL keyed on
`semanticStatus`. The pipeline's `accept.check_status_eligibility_jsonl` applies
the identical fail-closed semantics to the shard format (tested); reconciling
the two tools is a follow-up decision outside this pilot's endpoints. Risk to
this record: none of its four endpoints read that seam; the P8 gate tests both.

## Residual risks accepted at freeze (disclosed)

1. Negative m3 (Batch serves no cache reads): modelled completion ≈ $705 > cap;
   the frozen consequence is NO main-run launch pending a maintainer amendment,
   or a safe kill-ladder abort — never silent overspend. (Spec §5.2/§5.3.)
2. Human review throughput (40–75 h planning band) may slip; the record's h
   endpoint cannot be waived — a permanently missing review sheet leaves the run
   INSTRUMENT-INVALID, which is the honest outcome.
3. The provider price table may move between freeze and run; P6 preflight
   re-verifies and any discrepancy is an ops amendment BEFORE first spend
   (ASM-0601 discipline), with the $500 HARD cap invariant regardless.
