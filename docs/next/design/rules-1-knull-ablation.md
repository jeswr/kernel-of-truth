# RULES-1-KNULL-ABLATION — the MD-7 kernel-specificity control (c5 realised)

**Status: DRAFT pre-registration, designer role, 2026-07-12; REWORKED
2026-07-12 to close all findings of the cross-vendor pre-registration review
(REWORK verdict, scratchpad knull-review-verdict.txt). No feasibility
conclusion is stated or implied anywhere in this document; verdicts belong to
verdict-gen/the maintainer.** Parent design:
`docs/next/arch/world-model-rules-engine.md` MD-7 / §4.3 c5 / DECISION D15
[STIPULATED: PROPOSED-ASM-1138]. Parent record:
`registry/experiments/rules-1.json` (FROZEN, frozen_sha256
`0ef03ee16fdc278885b450500cb674f4319c1154ad067995e0b491feae4bec6c`; its
artifact pins are re-verified fail-closed at stage time). New assumptions:
PROPOSED-ASM-1400..1419
(Appendix A; **nothing here writes `registry/assumptions.jsonl`**).

## 1. Question

RULES-1's pinned certificate measured the twin engine **machinery
non-inert**: C_dec(stated) = 1.0, C_dec(entailed) = 0.0 (0/3,680 entailed
decisions reproducible from any stated-bytes projection), engine 858/858
against third-party CLUTRR gold. Per MD-7/ASM-1138 that claim is **capped**:
"machinery non-inert, kernel-specific value unshown". This record runs the
pre-registered c5 ablation that resolves the cap:

> Re-run the byte-identical RULES-1 certificate with the endorsed kinship
> TBox (axioms-v0 kinship trio + axioms-kinship-v1) **substituted** by a
> ruleset compiled from PLAIN-DICTIONARY definitions (the knull discipline —
> no NSM explication, no explicator/endorsement chain). Does the
> non-inertness certificate **survive** the substitution (⇒ kernel necessity
> is UNSHOWN against this one plain-dictionary compilation channel — the
> deflationary branch, equal prominence; NOT a claim about "any" ruleset)
> or **collapse** (⇒ KERNEL-ADVANTAGE-OVER-THIS-KNULL-COMPILATION at this
> vertical, failure mode named)?

A phase-2b conditional leg does the same substitution on the host-lift
primary (A3−A1) once the RULES-1 GPU campaign lands (§6).

## 2. Arms

| Arm | TBox staged | Role |
|---|---|---|
| **k0** | the real (kernel) `data/axioms-v0` 3-file set + `data/axioms-kinship-v1` | staging-identity INSTRUMENT gate (ASM-1405): must reproduce the pinned decision payload sha `fce753ba…b070aee5` byte-exactly. Pre-freeze-safe (outcome already pinned in rules-1). |
| **k1** | `poc/rules-1-knull/inputs/tbox-knull` — compiled from plain-dictionary definitions (ASM-1401/1402/1403) | **the primary substitution arm** |
| **k2** | `poc/rules-1-knull/inputs/tbox-scrambled` — k1 with every constraint-slot filler Sattolo-deranged, seed 20260712, subjects fixed, topology/kinds/counts identical (ASM-1404) | content-destruction **discrimination gate**: must LOAD and then fail the survival predicate (ASM-1412); k2 surviving OR k2 failing to load ⇒ INSTRUMENT-INVALID |
| k3 (follow-on, NOT in this campaign) | a generic-provenance ruleset transcribed from public ontology patterns | pre-registered as a NAMED follow-on only (`design.n_planned.follow_on_arms`); expected near-redundant with k1 (both compile common-knowledge kinship); running it requires a record amendment |

Everything else — `certificate.py`, `twin_engine.py`, nsk1-clutrr items and
worlds, world-v0, the E1 cell constructor, the GS-B projection, vocab
machinery, seeds — is **byte-identical** to the frozen RULES-1 pins,
verified fail-closed (ERR_PIN_MISMATCH) at stage time by
`poc/rules-1-knull/ablation_runner.py` (shadow-tree staging: the harness
resolves ROOT from its own path, so substitution is invisible to the
harness bytes). Precisely: the **source ABox, evaluation constructor, and
harness bytes are identical across arms; the E1 generated cells are
treatment-consistently alpha-renamed to each TBox's parent URN** — they are
not byte-identical across arms (ASM-1410; review fix 5).

**Substitution scope (ASM-1400).** The ABox states facts using the kernel
URNs for mother/father/man/woman; those identifiers are shared data schema
in every arm. The ablation substitutes ALL definitional content: every
constraint on those relations/classes, and every term the TBox itself
introduces (parent, person, grandparent, grandfather, grandmother — minted
fresh under the `kot-knull-def/1` profile, ASM-1403; the knull TBox contains
zero kernel URNs beyond the shared stated vocabulary).

**Attestation discipline (ASM-1413; review fix 2).** Before any arm runs,
`ablation_runner.py:stage()` re-digests the k1/k2 SOURCE input directories
under the kot-corpus-hash/1 recipe and compares them against the REGISTERED
pins in the record's `pins.artifact_hashes` — post-freeze drift refuses
fail-closed (ERR_PIN_MISMATCH). Every payload carries an `attestation`
block (record id + frozen sha, arm identity, per-arm harness shas, source +
staged TBox dir-digests, shared-corpus file shas, the pinned decision
payload sha); `analysis/rules_1_knull.py` REJECTS unattested or drifted
payloads (`/gates/harness_pins_valid` false ⇒ INSTRUMENT-INVALID).

**Engine identity (ASM-1416; review fix 6).** k1/k2 decisions are computed
SOLELY by the pinned Python differential twin (`twin_engine.py`, sha
`399fcd8d…`). The certificate's inherited
`certificate_result.engine_identity` text ("BOTH engines … sparq-reason …
EXACTLY agreed") describes the RULES-1 conformance run over the KERNEL
TBox and is FALSE for the substituted arms: sparq-reason is NOT executed
over the knull or scrambled TBoxes. The runner stamps this disclosure into
every k1/k2 payload; substituted-TBox differential conformance is a NAMED
FOLLOW-ON, not part of this record.

## 3. Inputs (built, hash-pinned)

- `poc/rules-1-knull/knull_kinship_defs.json` — 10 plain-register
  definitions: child/father/man/mother/woman **byte-verbatim from the knull
  v4 plain-authored store** (sha `97609abe…`), parent/person/grandparent/
  grandfather/grandmother newly authored in the same register (the v4 store
  covers the F2 vertical and lacks them). Contamination direction analysed
  in ASM-1401: the drafting session had kernel exposure; the pressure is
  toward kernel-equivalence, i.e. toward the SURVIVES (deflationary)
  reading — it cannot manufacture a false kernel-advantage result.
- `poc/rules-1-knull/build_knull_tbox.py` — deterministic compiler.
  Protocol (ASM-1402): the closed RULES-1 constraint inventory is the
  compilation TARGET GRAMMAR; every emitted constraint carries a
  `licensed_by` block quoting the definition span and the reading that
  licenses it; filename mirroring against the pinned TBox set is a
  harness-compatibility contract (CF-1/2/3 target rows by filename), never
  content copying; `inputs/lint-report.json` is the span-traceability lint.
- **Compilation-fidelity gate is THREE-part (review fix 4):** the lint
  alone does not establish a competent comparator. Added pre-freeze:
  (i) `inputs/parse-smoke.json` (ASM-1414) — `ablation_runner.py --smoke`,
  a PARSE-ONLY load of every arm's staged TBox through the pinned
  `twin_engine.load_tbox` (no closure, no decisions, no unblinding); a
  trivially-unparseable comparator is caught pre-freeze as an authoring
  bug, never read post-freeze as an outcome; and
  (ii) `inputs/def-constraint-mapping.json` + `inputs/mapping-review.json`
  (ASM-1415) — a mechanical per-constraint definition→constraint mapping
  extract, INDEPENDENTLY reviewed (reviewer role, fresh context, authored
  neither the definitions nor the compiler) for semantic licensing and for
  compiler-induced-collapse hazards (missing needed content).
  `/gates/compilation_lint_valid` = lint pass AND smoke pass AND mapping
  review pass.
- The two disclosed stipulations the kernel also makes are re-derived, not
  imported: exhaustive-or covering ("a person's father OR mother", the
  ASM-1121 class) and male/female exclusivity (disjointWith). The
  male→man range mapping's adultness over-restriction risk is disclosed in
  the record bytes and in the mapping review.

## 4. Decision rules (pre-registered)

**Survival predicate (pinned — identical to the rules-1 certificate
precondition):** `success_asm_1131 AND gates_asm_1163_all_pass AND NOT
kill_a_fired`, computed by the byte-identical certificate over the
substituted TBox.

Instrument gates (ALL must hold or INSTRUMENT-INVALID, never an outcome):
1. `/gates/harness_pins_valid` — every staged byte matched the rules-1
   pins AND every payload carries a valid attestation naming this record,
   this arm, the pinned harness shas and the registered TBox dir-digests
   (ASM-1413).
2. `/gates/staging_identity_valid` — k0 reproduced decision sha
   `fce753ba…b070aee5` (ASM-1405).
3. `/gates/compilation_lint_valid` — lint AND parse-smoke AND independent
   mapping review all pass (ASM-1402/1414/1415).
4. `/gates/k1_tbox_loads` — the knull TBox loads and the certificate runs;
   a load/run failure is an authoring-channel failure, INSTRUMENT-INVALID
   with a named failure mode, never scored as collapse (ASM-1408).
5. `/gates/k2_tbox_loads` — the scrambled TBox loads and the certificate
   runs over it (ASM-1412; review fix 3). A k2 parse/load failure resolves
   INSTRUMENT-INVALID, NEVER "successful discrimination".
6. `/gates/discrimination_valid` = `k2_tbox_loads AND NOT
   k2_certificate_success` — k2 must load and then fail the survival
   predicate; if content destruction survives, the instrument cannot
   distinguish content and nothing is licensed (ASM-1404).

**Primary endpoint** `/analysis/k1_certificate_success` (binary,
deterministic, exhaustive — no sampling, no bootstrap):

- **k1 SURVIVES** ⇒ verdict **NULL = KERNEL-NECESSITY-UNSHOWN (this
  channel)**: kernel necessity is unshown against THIS ONE plain-dictionary
  compilation channel (this documented protocol, this drafting session).
  One comparator cannot license any universal "ANY competent ruleset"
  claim (review fix: NULL language). The MD-7 cap on RULES-1 STAYS IN
  FORCE at the kinship vertical and is re-worded to name the measured
  channel: "machinery non-inert; kernel necessity unshown against the
  measured plain-dictionary compilation channel"; kernel-specific value
  must be sought elsewhere (authoring/endorsement economics — the A-F0
  line; coverage at verticals where plain definitions fail to compile;
  NL-robustness walls). Equal prominence with any positive (the knull
  discipline verbatim).
- **k1 COLLAPSES** ⇒ verdict **PASS =
  KERNEL-ADVANTAGE-OVER-THIS-KNULL-COMPILATION** (review fix: PASS
  language): the substituted ruleset fails the certificate where the
  endorsed kernel passed it; the failure mode is named mechanically
  (`/analysis/k1_failure_mode`). Scope: THIS vertical, THIS compilation
  protocol, one knull author-channel — no claim that no better generic
  compilation exists (k3 and better compilers are named follow-ons).

**Expected-direction disclosure (ASM-1406):** kinship logic is common
knowledge; a-priori the SURVIVES branch is the likely outcome. This record
is run to MEASURE the cap's resolution, not to confirm a preferred branch;
the deflationary branch is the honesty upgrade MD-7 bought.

## 5. Statistics

The certificate leg is deterministic and exhaustive: booleans and exact
counts, no inference. Wilson-LB95 rates are carried descriptively from the
certificate bytes. The only inferential statistics live in the phase-2b
host-lift leg (§6): paired item BCa bootstrap B = 10⁴, PRNG seed 20260712;
h1 one-sided α = 0.05 for the knull lift; h2 TOST with margin ±0.05 on the
90% BCa CI of (kernel lift − knull lift); per-item seed-averaged means.
**Holm within {h1, h2} is implemented on one-sided bootstrap p-values**
(smallest p at α/2, the other at α only if the first rejects); each
hypothesis passes only if its registered CI criterion AND its Holm-adjusted
rejection both hold (review fix 9 — no unadjusted twin α=.05 tests).
**Row-completeness (review fix 9):** exactly 858 paired items × 3 seeds ×
all four (host_tbox × host_arm) cells (10,296 rows); duplicates, missing
rows or extras REJECT (`/analysis/hostlift_rows_valid` false, every stat
null) — complete-case dropping is a preregistration violation.

## 6. Phase-2b host-lift leg (conditional, pre-registered here)

Activated ONLY when the pinned parent readout carries rules-1
`/analysis/primary_pass == true` (machine-enforced: the analysis takes the
parent analysis JSON and refuses to evaluate hostlift rows otherwise —
review fix 8). Arms: A1 and A3 (verify-retry k = 4) with the k1 TBox
substituted, same 858 items, seeds {0,1,2}, same pinned runner bytes, same
third-party gold. **The (kernel, A1) and (kernel, A3) rows are REUSED
verbatim from the frozen rules-1 campaign run-records — never regenerated**
(review fix 8; reuse declared, rows keyed by the parent run-record shas at
activation). Only the two knull cells (knull×A1, knull×A3) are fresh GPU
work. **Pinned runnable harness (review fix 1):** the rules-1 GPU harness
bytes themselves — `poc/rules-1/rules1_runner.py` (sha `020394f2…`),
`poc/rules-1/modal/modal_rules1.py` (sha `209dd08f…`),
`poc/rules-1/inputs/rules1-manifest.json` (sha `a4c947bf…`, which pins the
f2b-transfer A3 loop bytes `810dcbc5…` and the Modal image requirements
`0fac7243…`), model R1 =
`HuggingFaceTB/SmolLM2-135M-Instruct@12fd25f77366fa6b3b4b768ec3050bf629380bac`
(the FROZEN f2b-replicate/f2b-transfer revision carrier; nsk1 is DRAFT and
carries placeholders — the inherited "nsk1 pinned revision" text was
wrong and is corrected in this record). The knull cells stage the k1 TBox
by the same attested shadow-substitution discipline as the certificate leg.
Endpoints (secondary family, Holm within {h1, h2} as in §5):
- **h1** knull lift: (A3_knull − A1_knull) paired BCa one-sided 95% LB > 0.
- **h2** equivalence: TOST — 90% BCa CI of (kernel lift − knull lift)
  inside ±0.05 ⇒ the host-lift ALSO survives substitution.
Host-level survival = h1 AND h2. Unevaluable (rules-1 not yet read out or
primary not PASS, KILL-b fired, arm unrun, rows invalid) ⇒ every hostlift
field null — never a fail, never blocking the certificate-leg verdict
(ASM-1407/1417). Budget: ≤ $5 GPU inside the standing Tier-0/F2
authorization; certificate leg is ~$0 CPU.

## 7. Roles and execution discipline (ASM-1409)

This build (designer role) produced: inputs, runner, analysis, mock, DRAFT
record; the mapping review is the independent reviewer role's (ASM-1415).
**Arms k1/k2 were NOT executed pre-freeze** — the runner refuses them
without `--registered` AND a FROZEN record (fail-closed
ERR_NOT_REGISTERED / ERR_NOT_FROZEN); only k0 (outcome already pinned),
the PARSE-ONLY smoke (no closure, no decisions — ASM-1414) and synthetic
mocks ran. Freeze is the coordinator's; the registered $0 CPU run is the
runner role's; grading is verdict-gen/analyst; audit is the cross-vendor
auditor.

## Appendix A — PROPOSED-ASM-1400..1419 (emitted for central registration)

The JSON rows are carried in `poc/rules-1-knull/RESULT.md`; block
1400..1419 fully assigned after the review rework (1412 k2-loads gate,
1413 attestation, 1414 parse-smoke, 1415 mapping review, 1416 engine
identity, 1417 hostlift exactness/Holm/activation/reuse, 1418
runtime/generation EXTRAPOLATION, 1419 harness manifests).
