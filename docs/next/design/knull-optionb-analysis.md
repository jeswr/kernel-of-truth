# KNULL-OPTB — the Option-B concise plain arm and the length-controlled analysis (design note)

> **Status: [EXP-DESIGN] deliverable of the maintainer's Option-B ruling
> (maintainer decision issue 6, kernel-of-truth repo, resolved 2026-07-11),
> unblocking the knull-v2 freeze after the ASM-0706 escalation. Nothing here
> is frozen, pre-registered, scheduled, or run; no verdict, audit, frozen
> object, or registered ruling is touched. This document's assumption entries
> are carried as **PROPOSED-ASM-1080…ASM-1088** (disjoint block ASM-1080–1089
> requested for this deliverable, the block's final id reserved unused; the coordinator
> registers them at commit — this document edits no registry file). Author:
> Fable, experiment-designer role (kern/fable-designer), 2026-07-11.**
>
> **Companion artifacts (this deliverable):**
> `poc/knull/inputs-v3/plain-authored.json` (the Option-B concise store,
> v3.0.0), `poc/knull/lint_plain_store_v3.py` + `poc/knull/inputs-v3/
> g1-lint-report.json` (the relaxed-contract lint, green),
> `poc/knull/project_tokens_optionb.py` + `poc/knull/inputs-v3/
> token-projection.json` (pinned-tokenizer length measurement, prompt-level
> projection, padded-arm feasibility).
>
> **Blocked-by inputs, read in full at source:** registry/experiments/
> knull-v2.json (DRAFT) and its quality-gate evidence poc/knull/
> quality-gate-v2/; poc/knull/inputs-v2/plain-authored.json (v2.0.2) +
> g1-lint-report.json + g3-token-band.json; poc/knull/lint_plain_store.py
> (the pinned G-1 contract) + build_inputs.py (the pinned v1 builder);
> poc/f2b/runner/f2b_runner.py (the pinned mechanism source);
> docs/design-knull-content-injection-ablation.md §1, §5, §6.2;
> docs/next/knull-plain-arm-quality.md (ASM-0700/0703 lineage).
>
> **Tag convention (house discipline):** `[MEASURED: ref]` = a programme
> registry verdict/assessment/artifact restated strictly inside its envelope;
> `[STIPULATED: id]` = a design choice made here or inherited from a
> registered stipulation (every design CHOICE in this document is STIPULATED,
> not MEASURED, unless a measurement is cited); `[PROJECTED: ref]` = a
> pre-freeze forward calculation, never a premise — its binding resolution is
> named where it appears; `[PROPOSED-ASM-108x]` = an entry awaiting
> coordinator registration.

---

## 1. The ruling, and what this note delivers

The v2 plain store cleared the defect-class half of the ratified quality gate
(both judge families: zero anaphoric-renaming, staged-observer, or
exemplification findings) but missed the blind-naturalness floor (GPT-5.6
4/10, Haiku 3/10 against the >=5 floor), and both judges traced the residual
unnaturalness to the same structural cause: the L-3 ±25% word band against
the NSM gloss (~2x natural entry length) and the L-4 mandatory second
segment [MEASURED: knull-v2.json prefreeze_gates_evidence; poc/knull/
quality-gate-v2/gate.new108.v2r*.{gpt56,haiku}.raw.md]. The maintainer
resolved the ASM-0706 escalation with **Option B**: author the control arm at
natural concise dictionary length — tighter than the reviewed 18-sample pass
(e.g. *music* drops "the sounds so made") — and keep attribution defensible
by measuring the resulting token deficit and controlling for it in the
analysis [STIPULATED: PROPOSED-ASM-1080; the ruling thread is maintainer
decision issue 6].

This note delivers (a) the store, (b) the exact length-control statistics,
and (c) the freeze delta for the knull-v2 DRAFT record (§6).

**The store, as committed.** All 108 definitions re-authored at natural
lexicographic length: genus + differentiae, the most apt word, parenthetical
restrictions only where load-bearing, a second sense division only where
genuinely definitional. Against the pinned G-1 contract run MINUS the two
deliberately relaxed clauses (L-3 dropped; L-4 relaxed to >=1 admissible
claim segment, the floor the claim-item contract actually needs), the store
lints green: 108/108 enforced checks pass (D-1, L-1, L-2, L-4b, L-5,
R-1–R-4); register-ratio min 0.273, median 0.462; own-gloss Jaccard max
0.179; word-ratio vs the NSM gloss median 0.304 (min 0.139, max 0.818);
106/108 now outside the old band, 81/108 single-segment [MEASURED:
poc/knull/inputs-v3/g1-lint-report.json]. The blind two-family quality gate
(ASM-0703) must be RE-RUN on this store as a freeze precondition — the
Option-B ruling changes the length constraint, not the quality bar
[STIPULATED: PROPOSED-ASM-1080].

## 2. The confound, quantified before it is controlled

L-3/L-4 existed to hold the plain arm at FLOP parity with the kernel gloss.
Dropping them costs, at the pinned SmolLM2-135M tokenizer:

- **Gloss level (MEASURED, committed bytes):** kernel mean 40.2 tokens;
  plain-v3 mean 12.4 tokens — ratio **0.309** (v2 was 0.962)
  [MEASURED: poc/knull/inputs-v3/token-projection.json].
- **Prompt level (PROJECTED):** substituting the v3 glosses (and
  index-mapped v3 claim segments) into the byte-identical v2 item schedule
  and re-rendering with the pinned f2b `build_prompt` gives a plain-arm mean
  of 69.1 prompt tokens vs kernel 110.5 — ratio **0.626**
  [PROJECTED: token-projection.json; binding resolution = the G-3 artifact
  of the actual v3 build, PROPOSED-ASM-1088].

Mechanism fact that scopes the confound: in every knull cell the verifier is
the CPU string-matcher (norm_text equality against the arm's record), not an
LM call; LM compute is prompt-tokens × attempts, and store text reaches the
LM prompt only through item surfaces (def-match option texts, term-match
question texts, claim texts) — the gloss-as-context injection exists only in
the kernel-as-text arm, which knull-v2 does not run [MEASURED: poc/f2b/
runner/f2b_runner.py build_prompt/run_verify_retry; knull-v2.json
arms_mandatory_baselines NOTE]. So 0.626 is the right order for the per-call
compute deficit: **the concise plain arm runs at roughly five-eighths of the
kernel arm's token budget — far outside the ±20% flops-parity instrument
gate.** The confound is material and one-sided: it threatens only the
superiority (PASS-CONTENT) reading, because a kernel win over a shorter arm
could be purchased by tokens alone, whereas plain matching kernel on a
smaller budget only strengthens the deflationary reading (§4.3).

## 3. Two candidate controls; one is identified, one is not

**(a) Token-count covariate (NOT verdict-bearing — demoted to a descriptive
sensitivity).** The natural formulation is ANCOVA on the paired per-skeleton
contrast: D_i = lift_i(kernel) − lift_i(plain) regressed on
Δt_i = prompt_tokens_i(kernel) − prompt_tokens_i(plain), reading the content
effect as the regression estimate at Δt = 0, bootstrapped on the shared
resampling plan. This fails as a verdict-bearer on identification, not on
mechanics: Δt_i has **no within-concept experimental variation** — it is a
deterministic function of which concept (and item type) skeleton i touches,
so the length coefficient is identified only off between-concept variation,
which is confounded with concept complexity (NSM explications are long
exactly where concepts are hard). Reading the intercept at Δt = 0 also
imports a linearity assumption over an extrapolated region — a
forward-projection premise, which house statistics discipline forbids in a
verdict [STIPULATED: PROPOSED-ASM-1081; the no-extrapolation-as-premise
rule]. It survives as a DESCRIPTIVE sensitivity read (§4.5).

**(b) Length-matched plain-padded secondary arm (RECOMMENDED —
verdict-bearing guard).** Add a fourth store arm, `plain-padded`: the SAME
concise definition, deterministically padded back into the kernel-gloss word
band by **cyclic whole-segment repetition of its own admissible segments**,
joined by "; ", never cutting inside a segment; if the base definition
already sits in the band, it is carried unpadded (degenerate case,
disclosed) [STIPULATED: PROPOSED-ASM-1082]. This creates the exact variation
the covariate lacks: two arms with **identical content at two token budgets**,
assigned by construction rather than observed. Properties, verified on the
committed store:

- Feasible 108/108 under the fail-closed rule (2 degenerate, 106 padded);
  projected padded-arm prompt-token ratio vs kernel **0.931** — inside the
  ±10% pre-freeze G-3 band [MEASURED feasibility + PROJECTED ratio:
  token-projection.json].
- **Decision-isomorphism with the plain arm:** repetition of whole own
  segments adds no new admissible segment (duplicates are deduped by the
  pinned `segments()`) and no new token to the token set, so every builder
  decision that reads the plain gloss (LC1 own-label, LC3 false-claim
  Jaccard, claim segment inventory) is bitwise-identical between plain and
  plain-padded — same skeletons, same type mix, perfect item pairing; the
  two arms differ ONLY in injected store bytes. Enforced fail-closed at
  build (segment-set equality check, KNULL_ERR_PAD_SEGMENTS)
  [STIPULATED: PROPOSED-ASM-1082].
- **Conservative bias direction:** if repeating the answer-key text in the
  item surface has any effect at the accept seam, it favors the padded arm,
  making the kernel-superiority guard HARDER to pass — conservative against
  the content claim, the direction the design doc already accepts for
  comparator selection [STIPULATED: PROPOSED-ASM-1082; disclosed, not
  assumed absent].
- No authoring gate: the padded arm is a deterministic transform of the
  quality-gated concise store, REAL arm content in the same category as the
  opaque generator; the ASM-0703 blind gate applies to the concise store
  only [STIPULATED: PROPOSED-ASM-1087].

## 4. The statistical specification (exact analysis delta)

All machinery not named here is UNCHANGED from the knull-v2 DRAFT: paired
skeleton-level BCa bootstrap B=10000, sap_prng_seed 20260710, one shared
resampling plan, TOST margin ±0.05 absolute, lift defined within arm as
seedmean(verify) − seedmean(alone-R1), Holm family F-sec(knull) membership
{shuffled_low_recovery, f2b_form_positive}.

**4.1 Arms and cells.** Store levels: kernel, plain (concise v3),
plain-padded, opaque. The plain-padded arm runs **alone-R1 and
verify-retry-R1 only** (3 seeds, same 1000 rank-prefix skeletons): its sole
role is the length control for the lift contrast; it joins neither the
alone-R3 bridge restatement nor the shuffled control [STIPULATED:
PROPOSED-ASM-1086]. Cost: +6 cells of 135M compute (~+1/5 of the R1 cell
count; planning estimate, never a measurement — caps unchanged).

**4.2 Comparator set and primary.** best = the aligned non-NSM arm among
{plain, plain-padded, opaque} that passes its difficulty gate and has the
larger point lift (the pre-declared selection rule, unchanged; its known
~+0.01–0.03 selection bias remains conservative against the content claim).
D_full = mean_i[lift_i(kernel) − lift_i(best)]. The TOST equivalence test,
its margin, and /analysis/tost_equivalent are unchanged, now over the
three-arm comparator set.

**4.3 Verdict readings under the token deficit.**

- **NULL (TOST passes):** unchanged test; the licensed relabel gains a
  budget clause and gets stronger, not weaker: *the f2b lift is reproduced
  by a generic aligned answer-key + retry at no greater — possibly smaller —
  token budget than the kernel store.* The deflationary claim is an
  existence claim over the control arms; a cheaper matching arm satisfies it
  a fortiori [STIPULATED: PROPOSED-ASM-1084].
- **PASS-CONTENT (superiority):** now a conjunction (intersection-union
  test): `/analysis/kernel_superior_beyond_margin` = [LB95_1s(D_full) >
  +0.05] AND [LB95_1s(D_matched) > +0.05], where D_matched =
  mean_i[lift_i(kernel) − lift_i(best_matched)] and best_matched = the
  eligible token-matched arm (plain-padded if it passes its difficulty
  gate, else opaque) with the larger point lift. The second clause is the
  length guard: a kernel win must survive comparison at token parity, so it
  cannot be purchased by budget alone. An IUT conjunction at a fixed margin
  only shrinks type-I error, so the Holm family is NOT resized. If no
  token-matched arm is eligible, superiority is unavailable:
  `/gates/length_guard_available` = false forces the field false (the
  outcome space then contains NULL/FAIL/INCONCLUSIVE only)
  [STIPULATED: PROPOSED-ASM-1083].
- **FAIL (inferiority):** unchanged, UB95_1s(D_full) < −0.05 — kernel
  losing to any aligned arm at less-or-equal budget is the anti-content
  outcome a fortiori [STIPULATED: PROPOSED-ASM-1084].

**4.4 Instrument gates.**

- Difficulty band: add `/gates/difficulty_band_plain_padded` (same ±0.15
  rule); `/gates/any_aligned_arm_eligible` ranges over the three aligned
  arms; extraction Wilson gate extends per-arm to plain-padded.
- **Flops parity re-scoped:** the ±20% per-query gate binds the
  TOKEN-MATCHED arms only — `/gates/flops_ratio_plain_padded` and
  `/gates/flops_ratio_opaque` vs kernel. The concise plain arm is EXEMPT BY
  DESIGN (that is the ruling's point); its ratio is still metered and
  reported as `/gates/flops_ratio_plain`, DESCRIPTIVE (projected ~0.63).
  The pre-freeze G-3 ±10% band likewise applies to plain-padded and opaque
  only, with the plain arm's number measured and disclosed out-of-band
  [STIPULATED: PROPOSED-ASM-1085].

**4.5 New non-verdict-bearing reads (both DESCRIPTIVE, outside the Holm
family, never verdict-bearing).**

- `/analysis/length_effect`: lift(plain-padded) − lift(plain), skeleton-
  paired with BCa CI — the pure token-budget effect at fixed content; the
  direct empirical answer to "what do tokens alone buy at this seam", and
  the input the cascade line (naturalisation-front architectures) wants.
- `/analysis/length_sensitivity`: Spearman correlation, across skeletons,
  of [lift_i(kernel) − lift_i(plain)] with Δt_i — the demoted covariate
  read (§3a), reported for triangulation only.

**4.6 Output-field delta (pins.analysis_script.output_fields).** Add:
`/gates/difficulty_band_plain_padded`, `/gates/extraction_wilson_lb_plain_padded`,
`/gates/flops_ratio_plain_padded`, `/gates/length_guard_available`,
`/analysis/acc_alone_r1_plain_padded`, `/analysis/acc_verify_plain_padded`,
`/analysis/lift_plain_padded`, `/analysis/lift_plain_padded_lb95_1s`,
`/analysis/lift_plain_padded_ub95_1s`, `/analysis/best_matched_arm`,
`/analysis/diff_matched`, `/analysis/diff_matched_lb95_1s`,
`/analysis/diff_matched_ub95_1s`, `/analysis/length_effect`,
`/analysis/length_effect_lb95`, `/analysis/length_effect_ub95`,
`/analysis/length_sensitivity`. Semantics change (documented, same name):
`/analysis/kernel_superior_beyond_margin` (now the §4.3 conjunction),
`/gates/flops_parity` (token-matched scope). `verdict_rules` in the record
are structurally untouched — the guard lives inside the computation of the
superiority field.

## 5. Builder and harness delta (implementation spec, runner/coordinator work)

`build_inputs_v3.py` (v2-custody pattern — the pinned v1/v2 builders stay
byte-untouched): reads `inputs-v3/plain-authored.json`; adds the
plain-padded store via the §3(b) generator (fail-closed: band landing,
segment-set equality, LC1, uniqueness — KNULL_ERR_PAD_*); relaxes the
per-gloss segment floor to >=1 for plain and plain-padded (kernel/opaque
keep >=2); drops the word-band check for plain while ENFORCING it for
plain-padded against the kernel gloss; renders four item files with
joint substitution across all four arms (LC8 fail-closed, type mix
re-derived — expected to shift from v2 because 81/108 plain definitions are
single-segment, and REQUIRED identical across arms as before); manifest
re-pinned. `lint_plain_store_v3.py` is the store gate (this deliverable,
already green). `check_token_band_v3.py`: the v2 checker re-pointed at
inputs-v3 with the four-arm band scope of §4.4. Analysis: new
`analysis/knull_v3.py` implementing §4 (the v1 `analysis/knull.py` is
frozen-pinned by the knull v1 record and stays byte-untouched).

## 6. Freeze delta for registry/experiments/knull-v2.json (coordinator applies; this document changes no registry file)

1. `design.independent_vars.store.levels` += `plain-padded`; cell-restriction
   note per §4.1; `arms_mandatory_baselines` gains the padded-arm entry
   (alone-R1 + verify-retry-R1 only) and its rationale pointer.
2. `design.n_planned.item_source` → the inputs-v3 item files + re-derived
   type-mix sentence (four arms, identical across arms, claim-true scarcity
   re-disclosed).
3. `design.n_planned.prefreeze_gates_evidence` rewritten for v3: G-1 = the
   RELAXED contract lint (L-3 dropped, L-4 → >=1) with report + store shas;
   G-2 manifest re-pin; G-3 = four-arm re-check, band scoped to
   plain-padded/opaque, plain measured + disclosed; G-4 = analysis/knull_v3.py
   pin; G-5 checklists; QUALITY GATE = ASM-0703 blind two-family gate re-run
   on the v3 store (freeze remains blocked until it passes).
4. `design.n_planned.assumptions`: update the plain-store claim to v3.0.0
   (new sha, Option-B ruling cite); replace the v2 G-3 parity claim with the
   v3 artifacts + the token-projection disclosure; add the ASM-1080..1088
   entries once registered.
5. `endpoints`: primary test text gains the §4.3 conjunction; gate-difficulty
   and gate-extraction extended to plain-padded; gate-flops-parity re-scoped
   per §4.4; add the two §4.5 descriptive secondaries; `hypotheses` H-KN2
   restated with the token-matched guard.
6. `kill_criterion_verbatim` (b)/(c): licence text gains the "at no greater
   token budget" clause; `extrapolation_envelope_verbatim` gains one
   sentence scoping the plain arm to natural length with parity enforced via
   the token-matched arms.
7. `pins.harness_manifest`: v3 builder/linter/G-3-checker paths + shas;
   `pins.analysis_script` → analysis/knull_v3.py + §4.6 field list.
8. `title`: the "ONLY the plain arm authored bytes change" clause is no
   longer accurate — restate as "the plain arm re-authored at natural length
   (Option-B ruling) plus a deterministic length-matched plain-padded
   secondary arm and the length-guarded superiority read".
9. `budget`/`runner_constraints`: caps unchanged; estimate note +6 cells of
   135M compute (planning estimate).

## 7. Self-check gate (mandatory)

- Every design choice above is tagged STIPULATED (or carried in a
  PROPOSED-ASM); every number is tagged MEASURED or PROJECTED with its
  artifact and, for projections, its binding resolution. Checked.
- No handle, account, or repo-account string appears in this document or
  in the committed store/scripts (RT-14 pattern list re-run by the linter
  over all 108 definitions). Checked.
- ASM block disjointness: ASM-1080–1089 unused by any registry or design
  file before this note (grep over registry/ and docs/, 2026-07-11 — highest
  in use ASM-1079). Checked.
- The frozen knull v1 record, the pinned v1/v2 linter/builder/checker bytes,
  and analysis/knull.py are not modified by this deliverable. Checked.
- This document registers nothing itself: the coordinator registers
  ASM-1080..1088 with the commit and applies §6 to the DRAFT record.

## PROPOSED-ASM block (verbatim entries for registration)

- **PROPOSED-ASM-1080 [STIPULATED]** Option-B ruling adopted (maintainer
  decision issue 6, 2026-07-11): the knull plain arm is authored at natural
  concise dictionary length; G-1 clause L-3 (±25% word band) is DROPPED and
  L-4 is RELAXED to >=1 admissible claim segment for the plain store; all
  other G-1 clauses unchanged; the ASM-0703 blind quality gate is re-run on
  the v3 store as a freeze precondition. Store: poc/knull/inputs-v3/
  plain-authored.json v3.0.0.
- **PROPOSED-ASM-1081 [STIPULATED]** Length-confound control: the
  verdict-bearing control is the experimental length-matched plain-padded
  arm; token-count covariate/regression adjustment is DESCRIPTIVE only
  (no within-concept identification; intercept-at-parity is an
  extrapolation premise), never verdict-bearing.
- **PROPOSED-ASM-1082 [STIPULATED]** plain-padded generator: cyclic
  whole-own-segment repetition joined by "; " into the kernel-gloss word
  band [0.75·wc, max(1.25·wc, wc+8)]; degenerate no-pad allowed in-band;
  fail-closed (band landing, segment-set equality, LC1, uniqueness);
  deterministic transform, no authoring gate; feasibility MEASURED 108/108
  on v3.0.0; disclosed bias direction: any answer-key-repetition effect
  favors the padded arm — conservative against the content claim.
- **PROPOSED-ASM-1083 [STIPULATED]** Superiority guard (IUT):
  kernel_superior_beyond_margin = [LB95_1s(D_full) > +0.05] AND
  [LB95_1s(D_matched) > +0.05], D_matched vs the eligible token-matched arm
  (plain-padded, else opaque) with larger point lift; conjunction at fixed
  margin — no Holm resize; no eligible token-matched arm =>
  length_guard_available=false and superiority forced false.
- **PROPOSED-ASM-1084 [STIPULATED]** NULL and FAIL readings are unchanged
  in form and licensed a fortiori under the plain arm's smaller budget; the
  NULL relabel adopts the clause "at no greater token budget"; the
  extrapolation envelope gains the natural-length scope sentence.
- **PROPOSED-ASM-1085 [STIPULATED]** Gate scope: flops-parity (run-time
  ±20%; pre-freeze G-3 ±10%) binds plain-padded and opaque vs kernel; the
  concise plain arm is exempt by design, its ratio metered and reported
  DESCRIPTIVE (/gates/flops_ratio_plain); difficulty-band and extraction
  gates extend to plain-padded.
- **PROPOSED-ASM-1086 [STIPULATED]** plain-padded cell budget: alone-R1 +
  verify-retry-R1, seeds {0,1,2}, same 1000 paired skeletons; excluded from
  the alone-R3 bridge and the shuffled control (role-limited length
  control).
- **PROPOSED-ASM-1087 [STIPULATED]** Quality-gate scope: ASM-0703 applies
  to the authored concise store only; the padded arm is disclosed REAL
  non-authored arm content (deterministic transform; opaque-generator
  precedent).
- **PROPOSED-ASM-1088 [STIPULATED]** Pre-freeze token evidence status: the
  substitution projection (poc/knull/inputs-v3/token-projection.json —
  plain 0.626, plain-padded 0.931 of kernel mean prompt tokens; gloss-level
  plain 0.309 MEASURED) is pre-freeze evidence only; binding resolution =
  the v3-build G-3 artifact and the run-time F0 FLOPs ledger.
