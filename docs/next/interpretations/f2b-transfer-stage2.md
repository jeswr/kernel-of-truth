# FABLE INTERPRETATION — f2b-transfer STAGE-2 (mechanical: verdict **PASS-PENDING-AUDIT**; fired rule = primary_reject AND (shuffled_low_recovery AND beats_gloss_self_verify); primary external-gold effect +0.2507; noninferiority_vs_r3 FALSE; dual-scoring gap 0.0053 ≈ 0; all instrument gates VALID; audit state PENDING — every licensing sentence below is CONDITIONAL on Gate-A audit confirmation)

- **Author:** Fable (interpretation agent), 2026-07-11. The coordinator computed the
  mechanical result; I own the epistemic reading. This document changes NO frozen record,
  NO verdict object, NO results-log line, NO analysis output, and NO registered assumption;
  it runs no experiment, no git, no bd, no kb-sync. The coordinator commits.
- **Conditionality, stated first because it bounds everything:** the mechanical verdict is
  **PASS-PENDING-AUDIT**, not PASS [MEASURED: registry/verdicts/f2b-transfer.json,
  `verdict`; `audit.state` = PENDING, `audit.path` = null; computed_at 2026-07-11T18:47:00Z].
  A Codex Gate-A audit is in flight. Every "licensed" claim in this document is conditional
  on that audit confirming the verdict; on audit DISCONFIRMATION this document is VOID in
  its entirety and must be superseded, not edited. No programme prose should cite this
  result without the pending-audit rider until the audit lands.
- **Sources (read at source, in full):** `registry/verdicts/f2b-transfer.json` (authoritative
  for EVERY stage-2 number below; nothing is recomputed), `registry/experiments/f2b-transfer.json`
  (FROZEN, frozen_sha256 b341a090…, amendments [1, 2] applied, amended_record_sha256
  fcd19925… — esp. H-TRANSFER/H-CIRC/H-STRUCT/RT-2, `kill_criterion_verbatim`, and
  `extrapolation_envelope_verbatim`, BINDING on every line below),
  `docs/next/interpretations/f2b-transfer-stage1.md` (the FINAL post-judge-3 stage-1
  reading, whose figures are restated, never recomputed), and
  `docs/next/interpretations/deconf-a1.md` (the complete DECONF-A1 certificate — the
  reconciliation partner for §5).
- **Epistemic discipline:** every load-bearing line carries its `[TAG]` on the same logical
  line. **MEASURED** restates a measured/computed fact strictly from a cited artifact
  (never recomputed); **STIPULATED** marks frozen-design text, registered rulings, and
  framing adopted verbatim; **DERIVED** marks this document's own rule-application from
  MEASURED facts, disclosed as absent from every cited artifact; **INTERPRETIVE INFERENCE**
  marks an inference of this document from measured facts read against the frozen frame,
  never a fact of the record; **EXTRAPOLATION/ASSUMED** are direction-only and load-bearing
  for nothing.

---

## 0. The mechanical facts, restated inside the envelope (all from the verdict object unless noted)

- PREMISE: [MEASURED: verdict object] Verdict **PASS-PENDING-AUDIT**; the fired rule is
  rule index 4, the frozen PASS rule: `primary_reject AND (shuffled_low_recovery AND
  beats_gloss_self_verify)`. Eligible runs 17, excluded 0; rungs measured R1 and R3;
  seeds {0, 1, 2}; the fixed pre-registered retry budget k = 4; 250 externally-labelled
  d-qa-t items [STIPULATED: frozen design for n/seeds/k].
- PREMISE: [MEASURED] **Primary effect_size = 0.2507** (verbatim 0.25066666666666704) —
  acc_ext(135M + kernel-verify-retry, k = 4) − acc_ext(135M-alone), seed-averaged per-item
  means on the 250-item externally-labelled eval set, scored against BLIND-ADJUDICATED
  external gold; `primary_reject` TRUE under the frozen test (paired item BCa bootstrap,
  B = 10000, PRNG seed 20260710, one-sided 95% BCa lower bound > 0) [STIPULATED: the test
  wording; the LB value itself is not restated here — it is the analysis artifact's, and
  the fired rule certifies its sign].
- PREMISE: [MEASURED] Holm family F-secondary(f2b-t): `shuffled_low_recovery` TRUE (the
  seed-pinned Sattolo-deranged shuffled-kernel arm, at identical retry topology and cost,
  recovers less than 30% of the true-verify external-gold lift at the one-sided 95% BCa
  upper bound); `beats_gloss_self_verify` TRUE (the kernel arm beats gloss-text self-verify
  + retry at matched budget and FLOPs, one-sided paired bootstrap under Holm);
  **`noninferiority_vs_r3` FALSE** — absolute non-inferiority of the 135M + verify arm to
  1.7B-alone on external gold at margin 0 was NOT established. The separation gate is
  VALID, so this secondary was lawfully IN the Holm family and its FALSE is a licensed
  reading, not a gate artifact.
- PREMISE: [MEASURED] Descriptive diagnostics (never verdict-bearing, restated as such):
  **dual_scoring_gap = 0.0053** (verbatim 0.005333333333333301) — lift_mem − lift_ext on
  the SAME runs, i.e. the external-gold lift is within half a point of the membership-gold
  lift; `seed_sign_consistent` TRUE (3/3 seeds same-direction lift on external gold).
  Stage-1 external endorsement A = 0.9610 (verbatim 0.960960960960961; = 320/333, one-sided
  95% Wilson LB 0.9395, human-anchored per the issue-#9 tie-break rule) [MEASURED: verdict
  `sec-endorsement` + f2b-transfer-stage1.md §0, restated].
- PREMISE: [MEASURED] Every instrument gate VALID: adjudication (G-adj), engagement
  (RT-7a made structural — the verifier decidably engaged, attempt-0 rejection inside
  [0.05, 0.95], at least one final answer differing from attempt 0; the F2/d-ext vacuity
  signature is excluded), headroom (R1-alone ≤ 0.85 on external gold — room to lift),
  separation (R3-alone exceeds R1-alone by ≥ 0.05 with LB > 0 on external gold), and P10
  extraction. The result is an evidence event, not an instrument event.
- PREMISE: [MEASURED: m0b, restated mandatorily per the envelope] Kernel-expressibility
  coverage **0.3542 at rung molecules-v0**, measured on one incomplete kernel-v0 instance —
  NOT general coverage. Every claim below is bounded to the kernel-covered slice.
- PREMISE: [MEASURED: deconf-a1.md §0, restated for §5] DECONF-A1 complete certificate:
  C_dec = 1.0 exactly (40,576/40,576 concordant decisions, grid ∪ replay ∪ init-order;
  triage NO-OBJECT) — kernel-runtime-STRUCTURE-INERT at the pinned R-1/135M scope;
  EXPLORATORY pre-freeze, registration pending.

## 1. The extrapolation envelope, quoted verbatim — BINDING on every sentence below

> "Binding on any PASS: 2 host rungs (135M, 1.7B) license a SIGN, not a slope; every claim
> is scoped to <=1.7B hosts, kernel-covered kernel-RENDERED templated definitional QA over
> the 108 covered concepts, the fixed k=4 retry budget, and THIS gold standard — blind
> dual-judge external adjudication under the pinned d-adj-t protocol, judge panel and
> sourcing disclosed. A PASS removes exactly ONE confound from the f2b-replicate envelope:
> gold defined by the kernel's own string-equality ('oracle-favourable eval design' loses
> its gold-definition leg; the constrained IF-C answer surface remains and stays
> disclosed). It does NOT license: external question-STYLE ecological validity
> (public-benchmark surfaces remain unmeasured for system lift — the deterministic
> verifier cannot engage them: MEASURED byte-identical verify/alone d-ext vectors in
> f2b-replicate); any coverage-general claim (kernel-expressibility coverage 0.3542 at
> rung molecules-v0 — MEASURED by m0b on one incomplete kernel-v0 instance, NOT general
> coverage — restated mandatorily); any PRM-class comparison (HC3 stays indexed to the
> 1.5B class tested in f2b-replicate; no PRM arm here); any scale language beyond
> sign-only (the s->S gap narrows as S grows, so absolute verifier catch-room shrinks with
> scale; cascade/verification-routing literature licenses mechanism existence above 7B,
> never effect size). A FAIL by kill (d) is symmetrically scoped: it kills the
> kernel-content claim for THIS kernel instance at this rung, not the verify-retry
> mechanism as such."

[STIPULATED: `extrapolation_envelope_verbatim`, identical in the frozen registration and
the verdict object.] Symmetry discipline: just as a FAIL would have been scoped to this
kernel instance at this rung, the PASS is scoped identically — supported here means
supported at THIS instance, THIS rung pair, THIS slice, THIS gold standard, and nowhere
wider.

## 2. What the PASS adjudicates: H-TRANSFER against H-CIRC, with both controls holding

LOAD-BEARING (the central reading; conditional on audit): **H-TRANSFER is supported at
scope — the f2b-replicate verifier lift survives ground-truth-independent gold.** The
frozen registration gave the circularity alternative H-CIRC two registered predictions,
disjunctively: blind endorsement A near chance (kill d, stage 1), and/or no external-gold
lift (kill a, stage 2) [STIPULATED: hypotheses[1] verbatim]. Stage 1 disconfirmed the
first leg (A = 0.961, LB 0.939 against a 0.70 bar) [MEASURED: stage-1 interp §0]; stage 2
has now disconfirmed the second: the lift on gold fixed by blind judges — an authority the
kernel did not define — is +0.2507 absolute with a positive one-sided 95% BCa lower bound
[MEASURED: §0]. Both of H-CIRC's registered falsification routes have now failed to fire
[DERIVED: rule-application of the frozen disjunction to the two measured outcomes]. At
this kernel instance, this rung, this slice, and this gold standard, the
definitional-circularity reading of the F2-line lift is disconfirmed; the lift is real
semantic contact, not an artifact of "gold := whatever the kernel says"
[INTERPRETIVE INFERENCE from the §0 MEASURED facts read against the frozen hypothesis
text; scoped by §1].

The two carried-over controls both held, and they matter as much as the primary:

- **H-STRUCT (content, not structure):** the shuffled-kernel arm — the SAME records,
  identical retry topology and identical cost, content decoupled from items by a
  seed-pinned derangement — recovers less than 30% of the external-gold lift at the
  one-sided 95% upper bound [MEASURED: `shuffled_low_recovery` TRUE]. The lift is
  kernel-CONTENT-specific: retry-against-any-oracle structure does not produce it; the
  correct item–content alignment does.
- **RT-2 (better than commodity):** gloss-text self-verification at matched budget and
  FLOPs does not close the lift [MEASURED: `beats_gloss_self_verify` TRUE]. The
  deterministic-verifier channel is doing something matched-cost commodity
  self-verification does not — the Law-2 deflation ("any verification would do this")
  does not hold at this scope.

INTERPRETIVE NOTE on the circularity signature: H-CIRC predicted lift_mem ≫ lift_ext ≈ 0;
H-TRANSFER predicted a small gap. The measured dual-scoring gap on the same runs is
0.0053 — the external-gold lift and the membership-gold lift are, to within half an
accuracy point, the SAME lift [MEASURED: §0; descriptive endpoint, never verdict-bearing,
cited as texture not proof]. The circularity signature is not merely below threshold; it
is absent.

## 3. What the PASS licenses for the CORRECTNESS thesis

LICENSED (conditional on audit; each clause inside §1):

- The kernel's authored content, for the 108 covered concepts as rendered into templated
  definitional QA, is BOTH externally endorsed at the content level (stage 1, A = 0.961,
  human-anchored) AND functionally load-bearing at the system level on external gold
  (stage 2, +0.2507 with controls) [MEASURED: §0]. This is the programme's first end-task
  positive on ground-truth-independent gold — the specific residual the f2b-replicate
  assessment foregrounded ("content-specificity ≠ ground-truth independence") is now
  discharged for this kernel instance [STIPULATED: the envelope's "removes exactly ONE
  confound" clause].
- The confound removed is exactly one: gold-definition circularity. "Oracle-favourable
  eval design" loses its gold-definition leg and no other. The constrained IF-C answer
  surface remains and stays disclosed; the item-generation and store-addressing
  circularities remain in full force — the items are rendered from the kernel's own
  records and every item pins the record that answers it [STIPULATED: envelope +
  deconf-a1.md's PROPOSED-ASM-1017 rider, restated].
- The correctness evidence is therefore: on the slice the kernel covers and renders, its
  content is true enough by a blind external standard to lift a weak host by 25 absolute
  points against that same external standard, in a way neither content-shuffling nor
  commodity verification reproduces. That sentence, with every one of its qualifiers, is
  the flagship correctness result of the programme to date [INTERPRETIVE INFERENCE;
  "flagship" is a programme-history observation, not a widening of scope].

NOT thereby established for correctness: any claim about the ~65% of concept-space the
kernel does not cover (coverage 0.3542, one incomplete instance); any claim about
naturally-phrased inputs (the NL/reachability boundary is untouched — no natural-language
input appears anywhere in this design; the l3a-parse/a5-nl FAILs stand) [MEASURED: the
stage-1 interp's C2 pointer, restated at pointer level; STIPULATED: envelope]; any claim
at the clause-grain of explication quality (the g3 clause-literal proxy WARNING is a
different instrument at a different grain and is neither confirmed nor rebutted here)
[STIPULATED: stage-1 interp §3.5 framing, adopted].

## 4. What the PASS licenses for the EFFICIENCY thesis — mechanism yes, headline no

LICENSED (conditional on audit): **the verifier-offload MECHANISM works at scope.** A
135M host plus a deterministic verifier over an authored store, at a fixed k = 4 retry
budget, gains +0.2507 absolute on external gold over the same host alone — with the
engagement gate proving the verifier actually engaged and the headroom gate proving the
baseline had room [MEASURED: §0]. Small-model + cheap-verifier is, on this slice, a real
lever and not a scoring illusion.

NOT LICENSED — and this is the load-bearing negative of the result:
**`noninferiority_vs_r3` is FALSE** [MEASURED: §0]. The efficiency HEADLINE — "a 135M
host plus the kernel matches a 1.7B host" — had its pre-registered opportunity on honest
gold, under a valid separation gate (so the comparison was live and lawful), and did not
clear it. Non-inferiority at margin 0 was not established; note the precise reading:
this is a failure to establish equivalence-or-better, not a measured effect size of the
shortfall, and no shortfall figure is restated here. For context only: f2b-replicate had
measured the verify arm ABOVE R3 on membership gold (+0.1507, BCa LB +0.1053)
[MEASURED: deconf-a1.md `measured_lift_context`, restated]; that reading does not carry
to external gold on this corpus. The cross-experiment contrast spans different corpora
(d-qa-r vs d-qa-t) and different gold standards and is therefore direction-only texture,
not a measured regression [EXTRAPOLATION: direction-only, load-bearing for nothing].

The efficiency thesis accordingly gains its mechanism leg and loses (at this rung pair,
this margin, this slice) its strongest headline form. What the thesis still awaits, each
frozen elsewhere: the alignment-vs-generic attribution (knull-v2 / DECONF Stage B
Δ_align), mint-cost (A-F0), and the consumption channel (A-E2) [STIPULATED: stage-1
interp §3.4 + deconf-a1.md §4, restated]. RT-2's pass bears on the consumption question
only negatively (commodity self-verification is not the mechanism); it does not price the
kernel's authoring.

## 5. Reconciliation with DECONF-A1: a real content-specific lift from an inert runtime structure

The apparent tension: DECONF-A1 certified, exhaustively at its pinned scope, that the
kernel's runtime STRUCTURE is INERT — the pinned checker consumes nothing beyond the
projected four-column answer key (label/gloss/claims), and the kernel's structural
apparatus (explication trees, primes, vectors, engine hooks) contributes nothing at
runtime [MEASURED: C_dec = 1.0 over 40,576/40,576; STIPULATED: the §3.2 reading, both
restated from deconf-a1.md]. Stage 2 now certifies a real, content-specific,
better-than-commodity lift on external gold. How do both hold?

LOAD-BEARING (the composition, which is clean): **the two results bracket the mechanism
from opposite sides, and together they locate the value in the AUTHORED CONTENT of the
answer key.** [INTERPRETIVE INFERENCE from the two measured results read against their
frozen frames; each input MEASURED as cited.]

- A1 bounds the mechanism from ABOVE: nothing MORE than the projected answer key is
  consumed at runtime. The lift cannot be attributed to distinctive kernel runtime
  semantics, because on the measured closure there are none.
- The shuffled control bounds it from BELOW: nothing LESS than the item-ALIGNED key
  suffices. The same bytes, same topology, same cost, wrong alignment — the lift
  collapses (recovery ub95 < 0.30) [MEASURED: §0].
- Stage 1 + stage 2 then certify the remaining channel: the aligned key's CONTENT is
  externally true (A = 0.961) and externally load-bearing (+0.2507 on blind gold).

The F2-line story that survives all three results simultaneously is exactly the
aligned-answer-key / cascade reading (issue #12; the cascade-naturalisation architecture
line): *the kernel's runtime value is the item-aligned, externally-true deterministic
answer key it AUTHORS; the runtime channel that consumes it is thin and structurally
generic; the lift is a property of verify-retry against that authored key* [STIPULATED:
the deconf-a1.md §4 "aligned-answer-key verify-retry" implication, which this result now
strengthens rather than contradicts]. Stage 2 upgrades that reading in one decisive
respect: A1 left open whether the key's content was worth anything beyond the kernel's
own self-defined gold; stage 2 answers that the content is worth +0.2507 against an
authority the kernel never touched.

Two honesty riders that must travel with the composition:

- **Attribution stops at "kernel-AUTHORED".** Nothing here shows kernel-GRADE authoring is
  necessary. Whether an independently-authored plain or generic aligned key reproduces
  the lift is knull-v2's authored-content channel and Stage B's Δ_align contrast —
  untouched and unrun [STIPULATED: deconf-a1.md §4, restated]. The flagship sentence is
  "the kernel-authored aligned answer key transfers", never "only the kernel could have
  authored it".
- **The invariance-lemma coverage of stage 2 is conditional and unverified here.** A1's
  planned d-qa-t[:250] sub-grid was certified concordant (1,592/1,592), and the lemma
  would make every stage-2 endpoint bit-invariant under kernel→GS-A replacement — but
  ONLY at identical checker/harness/schema/output-space/init/store pins, and A1 remains
  EXPLORATORY pre-registration [MEASURED + STIPULATED: deconf-a1.md §0/§4/§5]. Whether
  the executed stage-2 runner's pins match the A1-certified pins is a mechanical
  pin-comparison for the coordinator/auditor; this document asserts nothing about it.
  The direction-only reading stands regardless: no channel in the stage-2 design feeds
  the runtime anything beyond the answer key [ASSUMED: direction-only].

## 6. NOT licensed — the envelope applied clause by clause [STIPULATED throughout: §1 verbatim]

- NO external question-STYLE ecological validity: the item surface is kernel-rendered
  templated QA; public-benchmark surfaces remain unmeasured for system lift, and
  measurably unengageable by this verifier (f2b-replicate d-ext: verify/alone
  byte-identical at every seed) [MEASURED: the frozen record's own d-ext assumption,
  restated].
- NO coverage-general claim: 0.3542 at molecules-v0, one incomplete kernel-v0 instance,
  restated mandatorily. The result is a covered-slice result.
- NO PRM-class comparison: HC3 stays indexed to the 1.5B class of f2b-replicate; no PRM
  arm ran here.
- NO scale slope: two rungs license a SIGN only (`scale_language_licensed`: "sign-only"
  [MEASURED: verdict object]); the envelope itself notes absolute verifier catch-room
  shrinks as host scale grows — nothing here predicts the effect at 7B, and the
  literature licenses mechanism existence above 7B, never effect size.
- NO retry-budget generality: k = 4 fixed, no sweep; nothing is claimed at any other
  budget.
- NO gold-standard generality: THIS gold — blind dual-judge adjudication under the pinned
  d-adj-t protocol, judge panel disclosed (human judge-1, GPT-5.5 judge-2 fallback,
  GPT-5.6 judge-3 under the issue-#9 human-anchored rule) — with its stage-1 caveats
  (abstention-heavy unresolved set; same-family model judges 2/3) riding every citation
  [STIPULATED: stage-1 interp §2 caveats 1–2, adopted verbatim].
- NO efficiency headline: §4. The non-inferiority-to-1.7B claim is not established on
  external gold.
- NO movement of the NL/reachability boundary, the item-generation circularity, or the
  authoring-economics question — none was measured here.

## 7. Does either thesis move? Explicit judgement, conservative

JUDGEMENT [INTERPRETIVE, this document's own, tagged as such and conditional on audit]:
**neither programme thesis moves off INCONCLUSIVE-PENDING. This is a strong-but-scoped
positive strictly within its envelope — the strongest measured positive the programme has
produced, and still not a thesis verdict.**

- **Correctness:** the thesis acquires its first ground-truth-independent end-task
  positive, with the gold-circularity confound discharged. It does not reach a thesis
  verdict because the thesis is not scoped to this slice: coverage is 0.3542 on one
  instance, the NL-input axis is measured-negative at scope, the clause-grain content
  instruments are in WARNING, and the decisive correctness legs identified in the
  capstone (g2; the NL parser line) are untouched [STIPULATED: stage-1 interp §3.5 +
  capstone discipline, restated at pointer level]. Upon audit confirmation, the
  capstone's governing sentence ("ZERO audited end-task wins on external gold
  attributable to kernel content") becomes stale and must be revised — with the
  attribution worded per §5: attributable to the kernel-AUTHORED aligned answer key,
  kernel-necessity of authoring unresolved [DERIVED: application of the capstone's own
  maintenance discipline; recommendation only].
- **Efficiency:** the mechanism leg is now measured-positive at scope; the headline leg
  (match-the-big-model) is measured-not-established at this rung pair on honest gold; the
  attribution (knull/Δ_align), mint-cost (A-F0), and consumption (A-E2) legs are unrun.
  A thesis that gains one leg, fails to establish a second, and has three unmeasured
  cannot lawfully move [DERIVED: rule-application of the capstone's verdict discipline].

What HAS changed is the shape of the remaining question. Before this result, the
programme's central risk was that the F2 line was self-licking (kernel-defined gold
scoring kernel-defined answers). That risk is now retired at this instance, pending
audit. The central open question is no longer "is the lift real?" but "is the kernel the
necessary AUTHOR of what carries it, and at what cost, and does anything survive contact
with natural input?" — knull-v2/Stage B, A-F0, and the NL axis respectively
[INTERPRETIVE: the reframing is this document's; each component claim is cited above].

## 8. Recommendations (no action taken here; coordinator/maintainer to route)

1. **Gate the world on the audit.** No capstone edit, no ledger move, no sparq post
   framing this as a PASS until the Codex Gate-A audit confirms; then apply the §7
   capstone delta with the pending-audit rider removed and the §5 attribution wording
   kept verbatim.
2. **Run the §5 pin comparison** (stage-2 runner pins vs the A1-certified pins) and record
   the outcome; if identical, the GS-A bit-invariance of the stage-2 endpoints should be
   stated in the registered A1 record's terms; if not, it must not be claimed.
3. **The sharpest next spend is attribution, not replication:** knull-v2's
   authored-content arm and DECONF Stage B's Δ_align contrast now carry more
   verdict-leverage per dollar than any repeat of this design [ASSUMED: direction-only
   prioritisation, the maintainer's call].
4. **Efficiency-headline honesty:** any programme prose citing this result must carry
   `noninferiority_vs_r3` FALSE alongside the primary — the pair "+0.2507 over itself;
   not shown to match 1.7B" is the honest unit of citation. Splitting them would
   overstate.
5. The stage-1 caveats (judge-family concentration; the abstention-heavy unresolved set)
   ride every citation of the external gold, per the frozen sourcing-disclosure
   discipline.

---

## Epistemic register (what this interpretation relied on)

- **MEASURED, never widened, never recomputed:** every stage-2 number in §0, restated from
  `registry/verdicts/f2b-transfer.json` (verdict PASS-PENDING-AUDIT; audit PENDING;
  fired_rule_index 4; effect_size 0.2507; shuffled_low_recovery TRUE;
  beats_gloss_self_verify TRUE; noninferiority_vs_r3 FALSE; dual_scoring_gap 0.0053;
  seed_sign_consistent TRUE; sec-endorsement 0.9610; all gates TRUE; eligible_runs 17,
  excluded 0; rungs R1/R3; sign-only scale language; coverage 0.3542 molecules-v0;
  amendments [1, 2]); the stage-1 FINAL figures (A = 320/333 = 0.9610, Wilson LB 0.9395)
  restated from f2b-transfer-stage1.md; the DECONF-A1 certificate figures (C_dec = 1.0,
  40,576/40,576; d-qa-t[:250] sub-grid 1,592/1,592) and the f2b-replicate lift context
  (+0.1507 vs R3, BCa LB +0.1053, membership gold) restated from deconf-a1.md.
- **STIPULATED, adopted verbatim:** the extrapolation envelope (§1, quoted in full); the
  H-TRANSFER/H-CIRC/H-STRUCT/RT-2 wordings and the kill criterion; the frozen endpoint
  tests (BCa/Holm/TOST machinery) cited as wordings, their outputs cited as booleans; the
  DECONF §3.2 inertness reading and its invariance-lemma scope; the stage-1 caveats and
  judge-sourcing disclosure; the capstone maintenance discipline.
- **DERIVED (this document's own rule-application, disclosed):** that both H-CIRC
  disjuncts have now failed to fire (§2 — the frozen disjunction applied to the two
  measured outcomes); the §7 thesis-movement determinations (application of the capstone's
  verdict discipline to the measured legs); the staleness finding on the capstone's
  zero-wins sentence (conditional on audit).
- **INTERPRETIVE INFERENCE (this document's, never a fact of any record):** the §2 central
  reading; the §3 flagship-correctness sentence; the §5 bracketing composition and its
  location of value in authored content; the §7 reframing of the central open question.
- **EXTRAPOLATION/ASSUMED (direction-only, load-bearing for nothing):** the §4
  cross-experiment membership-vs-external R3 contrast; the §5 pins-independent
  direction note; the §8 prioritisation.

*This interpretation changes no frozen object, no verdict, no log, and no registered
assumption. Its every licensing sentence is conditional on Gate-A audit confirmation of
the PASS-PENDING-AUDIT verdict; on disconfirmation it is void and must be superseded.
Within the quoted envelope and pending that audit, the result reads: the kernel-authored
aligned answer key's content — not its runtime structure, not retry topology, not
commodity verification — lifts a 135M host by +0.2507 absolute on blind external gold it
never defined; and the same run shows that lift does not yet make the small host the
equal of a 1.7B host.*
