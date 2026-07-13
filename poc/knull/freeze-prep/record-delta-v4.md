# knull-v2 freeze delta, v4-adapted — STAGED for the coordinator (no registry file is edited by this document)

> **Status: freeze-prep staging artifact (Fable designer role, designer-26, 2026-07-13).**
> This is docs/next/design/knull-optionb-analysis.md §6 (the coordinator-applied freeze delta
> for `registry/experiments/knull-v2.json`) re-stated against the **v4** accepted store and the
> **now-registered** ASM-1080..1088 block, with every sha that already exists prefilled and every
> not-yet-existing pin marked `PINNED-AT-BUILD`. The coordinator applies this to the DRAFT record
> AFTER blockers B-1..B-3 (see README.md in this directory) land. Nothing here is frozen,
> registered, or run by this session.

## Why the committed DRAFT cannot freeze as-is

The DRAFT still pins the superseded v2 Option-A store
(`2536a294…`), a three-arm design, the ±10%-binds-plain flops gate, and quality-gate evidence text
whose final clause is "the freeze precondition is ESCALATED to the maintainer (ASM-0706)". All of
that is superseded by: maintainer issue 6 (Option B, → ASM-1080), maintainer issue 17
("proceeding with (B): the v4 control store is accepted with its residual naturalness-gate defects
documented"), and the maintainer blind style sign-off 10/10
(`poc/knull/inputs-v3/plain-spotcheck-current-RESULT.md`). Mechanical freeze checks pass on the
stale record (dry-run OK), so **nothing in the tooling will stop a wrong freeze** — this delta is
the substantive gate.

## The delta (per optionb-analysis §6, v3→v4 adaptations marked ★)

1. `design.independent_vars` store levels += `plain-padded`; cell-restriction note per §4.1
   (alone-R1 + verify-retry-R1 only, seeds {0,1,2}, ASM-1086); `arms_mandatory_baselines` gains the
   padded-arm entry + rationale pointer (ASM-1082).
2. `design.n_planned.item_source` → `poc/knull/inputs-v4/items/{kernel,plain,plain-padded,opaque}.jsonl`
   ★ (inputs-v4, not v3), + the re-derived type-mix sentence (four arms, REQUIRED identical across
   arms; claim-true scarcity re-disclosed). Expect a type-mix shift: **all 108 v4 definitions are
   single-segment** (flops-recheck-v4.json), vs 81/108 for v3.
3. `design.n_planned.prefreeze_gates_evidence` rewritten:
   - G-1 = relaxed-contract lint on the **v4** store ★: store sha
     `97609abe17f87e10a384950a5d69d4e579e40935109573eaf782095bcb43c0d2`, report
     `poc/knull/inputs-v4/g1-lint-report.json` sha
     `92e2e159995e0eb06a6bce97f6a0718a5db23082d10113989f1b8cb5302887f7`, linter
     `poc/knull/lint_plain_store_v4.py` sha
     `8049459cbebe9d964a54413c929e517c21a284ed7b34ff0ae28753cd3ee30e2e`.
   - G-2 manifest re-pin = `PINNED-AT-BUILD` (blocker B-1).
   - G-3 = four-arm re-check, band scoped to plain-padded/opaque (ASM-1085), plain measured +
     disclosed; artifact = `PINNED-AT-BUILD` (blocker B-2). Pre-freeze projection (non-binding):
     plain-padded 0.9907, opaque 1.0043, plain 0.6628
     (`poc/knull/freeze-prep/flops-recheck-v4.json` sha
     `c150270e9f7d59220d86052874fba787a4544943259a8934bb16e2bbf7c91011`).
   - G-4 = `analysis/knull_v3.py` pin = `PINNED-AT-BUILD` (blocker B-3).
   - G-5 checklists = prereg_doc + `poc/knull/freeze-prep/prefreeze-checklist.json`.
   - QUALITY GATE ★ = replace the ESCALATED clause with: ASM-0703 two-family gate MEASURED on v4
     (GPT-5.6 4/10, Haiku 3/10, gate_met false —
     `poc/knull/quality-gate-v4/gate-tally.json` sha
     `d10373c6537b2903da6acdc92a29f7df0c2149d284c49567b2a07fb8bad57e62`) RESOLVED by the maintainer
     issue-17 acceptance ruling (v4 accepted with residual defects documented) + the maintainer
     blind style sign-off 10/10 (`poc/knull/inputs-v3/plain-spotcheck-current-RESULT.md` sha
     `295bf42769e0f6a6f4ae77016c5b4d7d06a1aee7022d196f964fe8736769f2cc`; bookmark item-5 caveat
     carried, non-blocking).
4. `design.n_planned.assumptions`: plain-store claim → v4.0.0 + acceptance lineage ★; replace the
   v2 G-3 parity claim with the ASM-1085/1088 scoped statement + the v4 recheck numbers; cite
   ASM-1080..1088 as REGISTERED (they are — claims-check PASS) ★, tags exactly as registered
   (STIPULATED); tag any new pre-freeze token claim STIPULATED with its MEASURED components cited
   (the ASM-1088 pattern).
5. `endpoints`: primary test text gains the §4.3 IUT conjunction (ASM-1083); gate-difficulty +
   gate-extraction extended to plain-padded; gate-flops-parity re-scoped per §4.4/ASM-1085; add the
   two §4.5 descriptive secondaries; `hypotheses` H-KN2 restated with the token-matched guard.
6. `kill_criterion_verbatim` (b)/(c) gain the "at no greater token budget" clause;
   `extrapolation_envelope_verbatim` gains the natural-length scope sentence (ASM-1084). Keep the
   sign-not-slope sentence verbatim (the scale-language freeze lint reads it).
7. `pins.harness_manifest` → v4 builder/linter/G-3-checker paths + shas (`PINNED-AT-BUILD`);
   `pins.analysis_script` → `analysis/knull_v3.py` + the §4.6 output-field list
   (`PINNED-AT-BUILD`). Every metric pointer in `verdict_rules`/`endpoints` must stay inside the
   new field list (freeze constraint 2).
8. `title` restated: plain arm re-authored at natural length (Option-B ruling, issue-17-accepted
   v4) + deterministic length-matched plain-padded secondary arm + length-guarded superiority read ★.
9. `budget`/`runner_constraints`: caps unchanged ($60 / 8 GPU-h / 24 h wall); estimate note +6
   cells of 135M compute → 36 GPU cells (planning estimate, never a measurement).

## Invariants the delta must NOT break (freeze-tool trip-wires)

- Exactly one `role:"primary"` endpoint; last verdict rule stays the INCONCLUSIVE catch-all.
- Every endpoint/rule metric pointer ∈ the new `output_fields` (ERR_P2_UNKNOWN_POINTER).
- NULL rule ⇒ keep `smallest_effect_of_interest` on the primary.
- corpus pins untouched (they reproduce today — C-1).
- No account strings anywhere in hashed bytes (RT-14); identity fields pseudonymous.
- The frozen v1 record `knull`, its `poc/knull/inputs/` tree, and every pinned v1/v2 byte stay
  untouched (custody pattern: new work under fresh v4 paths only).
