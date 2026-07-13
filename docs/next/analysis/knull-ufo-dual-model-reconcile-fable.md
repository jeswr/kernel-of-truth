# knull-v2 + ufo-check-0 — independent Fable interpretation & dual-model reconcile

> **Provenance (Fable, 2026-07-13).** Independent second read for the standing dual-model
> discipline, reconciling against the GPT-5.6 (xhigh) proxy interpretations
> (`knull-v2-interpretation.md`, `ufo-check-0-interpretation.md`, both PROVISIONAL-ON-LLM-PROXY).
> Mechanical verdicts are frozen and are NOT re-derived here: **knull-v2 = NULL**
> (PASS-GENERIC; `registry/verdicts/knull-v2.json`) and **ufo-check-0 = INSTRUMENT-INVALID**
> (sole failed gate token-parity; `registry/verdicts/ufo-check-0.json`). Sections 1 of each part
> were formed from the verdict/analysis JSONs and frozen design docs before consulting the
> GPT-5.6 text; section 2 of each part is the explicit reconcile. Claims tagged
> MEASURED / PRE-SPECIFIED / INTERPRETATION; anything outside the pinned SAP is marked
> EXPLORATORY and is quarantined from verdict-bearing use. Uncommitted deliverable; no
> feasibility conclusion is authored here.

---

## Part A — knull-v2 (NULL / PASS-GENERIC)

### A1. Independent interpretation

**What the numbers say.**

- [MEASURED] TOST equivalence within the 0.05 SEOI: lift(kernel)=0.2397 vs
  best aligned arm (plain) 0.2477; D_full = −0.0080 with one-sided bounds
  [−0.0143, −0.0020]; matched contrast (plain-padded) D_matched = −0.0043,
  bounds [−0.0100, +0.0007]. Neither superiority nor inferiority beyond margin fired.
- [MEASURED] The point ordering is **plain > plain-padded > kernel > opaque**, and the
  kernel-vs-plain one-sided 95% UB is **below zero** — the kernel arm is nominally (not
  margin-relevantly) *worse* than the concise plain dictionary, which also runs at
  **0.565× the FLOPs** (`/gates/flops_ratio_plain`, descriptive by design under ASM-1085).
- [MEASURED] The sharpest single datum is the **opaque-nonce arm**: a store whose gloss
  content is nonce text at identical alignment and matched tokens delivers lift 0.2357 ≈
  kernel 0.2397. The length control is likewise flat (length_effect −0.0037, CI spans 0).
- [MEASURED] All instrument gates passed (bridge, difficulty bands, extraction, FLOP parity,
  length guard available); the shuffled control stayed dead (recovery 0.0028, UB 0.084) and
  the f2b form-effect secondary reproduced on the kernel arm (+0.0537, LB +0.0297) —
  attenuated roughly 3× from the original f2b +0.1507, on regenerated surfaces.

**Meaning for the CORRECTNESS thesis (within frozen scope).**

- [PRE-SPECIFIED] Kill (b) fired verbatim: *the kernel-content attribution dies at this
  scope*; the licensed forward phrase is "a generic aligned-deterministic-answer-key +
  retry effect at no greater — possibly smaller — token budget than the kernel store."
- [INTERPRETATION] I probed whether a less deflationary reading survives. The strongest
  candidate is a "couldn't-have-won-by-construction" objection: the M-V map proved the
  accept seam consumes only the canonical answer string (3456/3456 verifier decisions
  bitwise identical after stripping non-gloss fields), and the oracle-favourable
  construction was held fixed, so content could only act through reader-side surfaces and
  retry messages — a narrow channel. That objection is **correct as a diagnosticity point
  but does not rescue the attribution**: the frozen question was whether the *f2b lift as
  measured* carries NSM-content weight, and that lift was itself produced under the same
  construction. Within that question, NULL is a clean, informative answer. The legitimate
  less-deflationary residue is exactly what the envelope already carves out: knull-v2 says
  nothing about mechanisms that actually *consume* content (entailment-style checking,
  rules-line inference, transfer). It is not evidence *against* those; it is evidence that
  **this mechanism only ever needed alignment**.
- [INTERPRETATION] On the probe question "does NULL add weight to *content matters,
  kernel-specific structure unshown*?" — **half-no**. knull-v2 is an *anti-content-form*
  datum on definitional QA: even nonce glosses match the kernel. The "content can matter"
  side of the composed slogan is carried entirely by RULES-2 (PASS, audit CONFIRMED,
  2026-07-12), not strengthened by knull. The accurate composition is: **alignment does the
  work on D-QA; content mattered on the rules line; kernel-specific structure remains
  unshown everywhere** (no structural manipulation existed in this design).
- [INTERPRETATION] Composition with f2b-transfer — see A2; this materially changes the
  "next move" section relative to the proxy read.

**Meaning for the EFFICIENCY thesis (within frozen scope).**

- [INTERPRETATION] The NULL narrows the efficiency story from architectural to economic,
  and the descriptives make it *actively unfavourable* for the kernel store on this line:
  the concise plain dictionary is nominally more accurate at ~0.57× verifier-side FLOPs,
  and padding it back to kernel length buys nothing. At this scope the kernel store is
  weakly dominated on both axes by a plain dictionary.
- [EXPLORATORY / INTERPRETATION — cross-cell, outside the Holm family; quarantined] The
  alone-R3 descriptives carry a caution for the verifier-offload narrative: 1.7B-alone
  scores 0.691 on kernel-rendered surfaces, 0.512 on opaque, but **0.948 on plain
  surfaces** — far above every verify-retry cell (~0.75). The pre-registered f2b form
  effect ("135M + verifier ≥ 1.7B alone") is kernel-arm-only by design and passed, but
  descriptively the effect exists *only where the surface depresses the big host's
  baseline*. On plain-English surfaces at this scope, you would simply use the 1.7B model.
  Forward EFFICIENCY narration citing the form-effect bridge should carry this
  surface-dependence caveat.

### A2. Reconcile vs the GPT-5.6 read

**Agree (bulk of the document).** Core meaning (informative equivalence, not a broken
experiment); the pre-specified deflationary phrase and its adoption; the scope limits;
"verify-retry works, kernel deserves no distinctive credit here"; the reroute to
authoring-cost economics; the closing do-not-overclaim list. No divergence on any
verdict-bearing statement.

**Divergence 1 — MATERIAL (stale recommendation).** GPT-5.6 §4 names **f2b-transfer** as
"the single highest-value follow-up," to be run. [MEASURED] The registry shows
`registry/verdicts/f2b-transfer.json` = **PASS, computed 2026-07-11, audit CONFIRMED** —
*two days before* the interpretation's provenance date. The recommendation is stale as
written. The correct forward statement is a **composition**, and it is a strong one:
f2b-transfer shows the kernel-arm verify-retry lift survives blind, gold-label-independent
external adjudication (+0.2507 primary); knull-v2 shows the store powering that mechanism
is content-generic on self-authored gold. [INTERPRETATION] Combined licensed reading at
this scope: *the mechanism is real and not definitionally circular, and the store content
is interchangeable — an aligned deterministic answer key, even a nonce one, suffices.* The
genuinely open follow-up this composition creates (which neither frozen record tests) is
**the generic arm under external gold**: does a plain/opaque store's lift also survive
blind adjudication? If yes, content attribution is fully dead on this line even under
independent gold; if no, a real content signal reappears exactly where knull could not see
it. That — plus the pre-specified authoring-cost economics — is the honest "next move"
slate. This divergence changes a recommendation (material) but not the verdict or the
deflationary reading.

**Divergence 2 — minor, not material.** GPT-5.6 §3: "the results corroborate … content can
matter, but kernel-specific structure remains unshown. knull-v2 makes that qualification
stronger." As argued in A1, knull-v2 does not add weight to the "content matters" half —
it is anti-content-form evidence on its family (opaque-nonce ≈ kernel). Same routing
either way; wording-level correction only.

**Divergence 3 — moderate; material to efficiency narration only.** GPT-5.6 §2 says the
NULL "preserves some evidence weight for small-model verifier offload." True for
lift-over-R1-alone, but it omits the alone-R3 surface-dependence caveat (plain surfaces:
1.7B-alone 0.948 > all verify cells). I would not let the offload framing travel without
that caveat. Exploratory, so it changes narration, not any registered claim.

---

## Part B — ufo-check-0 (INSTRUMENT-INVALID)

### B1. Independent interpretation

**What the numbers say.**

- [MEASURED] Rule 0 fired: sole failed gate = token-parity (`token_parity_valid=false`),
  because the AG/AU rejection-message ratio is **undefined — AG rejected zero scored items
  at runtime** (AD/AU = 1.008 and AN/AU = 0.810, both in the ±20% band). Everything else
  passed: fixtures, headroom, engagement (AU rejected/retried on 33.3% of scored rows),
  extraction (Wilson LB 0.9998), completeness, AN representation-match and non-degeneracy,
  AD coincidence, message discipline. Primary LB = 0.0; s1–s4 false, s5 true — none
  verdict-bearing after the gate failure. Total cost of the run: ~$0.19, 0.17 GPU-h.
- [MEASURED] The behavioural texture matters more than the gate arithmetic. Per-disposition
  accuracy is *identical* across A0, AU, AG, AD: ENTAILED 1.0, CONTRADICTED 0.0,
  UNDERDETERMINED 0.0, total exactly 1/3 — the pattern of a host answering (near-)all-E.
  AU sits **below** its own analytic trivial-bit floor (0.333 vs floor 0.667; s1 LB −0.367).
  AN — the *null* checker — rejected 87.5%, broke the degenerate pattern
  (E 0.583 / C 0.198 / U 0.525) and is the **best arm at 0.436**. The 360M sign
  (`acc_au_minus_a0_360m_sign`) is +1.
- [INTERPRETATION, cheaply confirmable] AU's rejection rate of exactly one third, under the
  licensed-rejection contract (U never converted to rejection; engine-shared gold), is
  consistent with AU rejecting precisely the gold-C items where the host's E answer is
  provably violated — and the final CONTRADICTED accuracy of 0.0 means **no rejected item
  ever ended correct after the k=1 retry**. At 135M the host did not convert the checker's
  reasoned rejection into a correct answer even once, while AN's contentless "not stated"
  rejections did move it (to U, and occasionally to C).

**On the AG-zero-rejection: parity accident or something deeper?**

- [INTERPRETATION] Deeper — and deterministically checkable at zero GPU cost. The accept
  tables are materialised, seed-pinned, committed pre-freeze artifacts (per item × arm ×
  answer). AG rejecting nothing at runtime therefore means AG's stated-taxonomy-only rule
  inventory **accepts the host's realized answers (all-E) on every scored item**. That is
  not runtime noise; it is (almost certainly) a frozen property of the item family
  interacting with the host's answer distribution. And it is *expected*: the four families
  (F-RIG/F-ANTI/F-DISJ/F-SPEC) are built around rigidity/modal/cross-situation semantics
  that AG is *defined* to lack. AG is a behaviourally **inert control on this item family**
  — the H-U4 contrast (full-UFO vs taxonomy-only) was unmeasurable by construction, not by
  a length mismatch. Padding cannot make an inert checker fire.
- [INTERPRETATION] This is still **not a UFO-construct defect** (the UFO checker itself
  engaged, fired on a third of items, and kept message discipline; s5 even shows a genuine
  safety-favourable signal, dangerous-wrong 0.667 → 0.444). But it *is* more than a
  comparison-validity confound: the gate as designed conflates two different things —
  (i) per-message length parity, which is paddable and was fine where defined, and
  (ii) **realized-exposure parity across arms whose rejection incidence differs**, which is
  impossible to enforce without yoking incidence — and incidence *is the treatment*. A
  successor that only "token-matches" repairs (i) and leaves (ii) undefined the next time
  any arm's incidence goes to zero or diverges (AN at 87.5% vs AU at 33.3% is already a
  large realized-exposure gap that the per-message gate never sees).

**What a repaired instrument would likely find (EXPLORATORY — decision-relevant for
spend, never verdict-bearing).** Even with perfect parity, the 135M primary looks
unpromising: the host's degenerate all-E prior, AU's 0-for-~30 retry conversion, and AU
sitting below the trivial-bit floor jointly predict H-U1 FAIL at 135M; and AN
outperforming AU predicts the s2 attribution kill would fire anyway (the lift channel that
exists at this scale is "rejection pressure breaks a degenerate prior" — the knull lesson
in miniature: the *bit and its frequency*, not the reason). The positive 360M sign is the
one hint the hypothesis-bearing question is answerable slightly higher up.

### B2. Reconcile vs the GPT-5.6 read

**Agree.** INSTRUMENT-INVALID licenses neither "yes" nor "no" and no feasibility movement
(both theses stay INCONCLUSIVE-PENDING); not a degenerate-frame failure; "engagement =
operational invocation, not beneficial use" is exactly right; the no-GPU realized-exposure
audit over the frozen rows + accept tables is the correct first move; a small blocking
real-host pilot exercising every gate before any successor freeze; the frozen verdict
stands, no re-verdict.

**Diverge — MATERIAL to the repair design (not to the verdict).** GPT-5.6 frames the
failure as "a mismatch between template-level parity and realized exposure, not an
intrinsic UFO-construct defect," repaired by "a token-matched `ufo-check-1` with a neutral
padding/length-control arm." Half right: not a UFO-construct defect, agreed — but the AG
zero is best read as **deterministic construct-level inertness of the taxonomy-only
control on this item family**, checkable today from the committed accept tables, and a
padding arm does not touch it. If ufo-check-1 ships as "same design + padding," I expect a
second gate death (AG engagement/parity again, or an uninformative 135M FAIL). The repair
slate should be:
1. [Both models agree] Run the zero-cost accept-table/realized-exposure audit first;
   specifically compute per-arm rejection incidence over the frozen tables at the realized
   answer distribution *and* at counterfactual distributions (what would AG reject if the
   host ever answered C/U?).
2. [Fable addition] Redefine the token-parity gate as **conditional-on-firing** per-message
   parity, plus a separate **minimum-firing/engagement gate per checker arm** — so an inert
   control fails honestly as "control cannot engage on this family," not as an undefined
   ratio inside a parity gate.
3. [Fable addition] Decide H-U4's fate explicitly: either add items with stated-taxonomy
   violations so AG has purchase, or rescope/drop the AU-vs-AG contrast (it is claim-cap
   only, so dropping it costs little).
4. [Fable addition] Reconsider the primary rung: gate on host answer-distribution
   non-degeneracy at pilot, and consider 360M as primary (the +1 sign) with 135M demoted
   to descriptive.

**On the "instrument keeps dying at gates" pattern (E0 / CASC-0′ / DDC / rules-1-c /
ufo-check-0).** Agree with GPT-5.6 that this is a **methodological** signal, not evidence
for either substantive answer. I add two sharpenings. First, the common cause is
identifiable, not diffuse: every death in that list is a **template-vs-realized gap in a
behaviour-dependent gate** — a validity condition that depends on runtime behaviour of a
host or arm (rejection incidence, realized compute, realized power) and therefore cannot
be certified from templates, mocks, or pre-freeze artifacts alone. That converts the
pattern into one standing rule: *every behaviour-dependent gate must be exercised by a
small real-host pilot at the operating point before freeze* (GPT-5.6's pilot
recommendation, generalized from ufo-check-1 to the programme). Second, guard against
over-reading in *both* directions: these are fail-closed designs with ~10 gates each, so
gate deaths are the designed failure mode under hard questions — the gates are working,
not failing. The real cost to watch is the **forking-instruments ledger**: successive
repaired successors (check-0 → check-1 → …) are each individually licensed, but the
per-line successor count should stay disclosed so the family-level try-count is visible.

---

## Bottom line — does anything need a re-do or change a recommendation?

- **knull-v2: no re-do, no re-verdict.** The NULL, the pre-specified deflationary phrase,
  and the scope limits stand; my read and GPT-5.6's agree on every verdict-bearing point.
  **One recommendation must change:** GPT-5.6 §4's "run f2b-transfer next" is stale —
  f2b-transfer is already PASS (2026-07-11, audit CONFIRMED). Amend the proxy doc's §4 to
  the composition reading (mechanism survives external gold; store content is generic) and
  route the open question to (a) the pre-specified authoring-cost economics and (b) a
  candidate *generic-store-under-external-gold* successor. Additionally, forward EFFICIENCY
  narration should carry the surface-dependence caveat on the f2b form effect (plain
  surfaces: 1.7B-alone 0.948 > all verify cells; exploratory). These are **amendments to
  the interpretation document, not a re-do** — no frozen claim or verdict is contested.
- **ufo-check-0: no re-verdict; the repair recommendation needs revision before any
  successor freeze.** Agree the instrument, not the construct, failed — but the
  "token-matched ufo-check-1" framing under-diagnoses the AG zero as a parity accident
  when it is most likely deterministic control inertness plus a gate-definition flaw
  (undefined-at-zero parity). Run the zero-cost accept-table audit **before** designing
  ufo-check-1; expect it to force the four-point repair slate above (conditional parity +
  per-arm engagement gate, H-U4 rescope-or-refit, host-rung/non-degeneracy rethink). This
  is a material divergence about the *shape of the next experiment*, resolvable for ~$0
  by the audit both models endorse — resolve it there rather than by re-doing the
  interpretation.
- **Theses:** unchanged by both records, as pre-specified. CORRECTNESS: knull-v2 shifts
  attribution weight from kernel content to alignment+retry on the D-QA line (with the
  f2b-transfer composition keeping the *mechanism* alive under external gold); ufo-check-0
  moves nothing. EFFICIENCY: narrowed to economics on the F2 line, with the kernel store
  weakly dominated by a plain dictionary at this scope; ufo-check-0 moves nothing.
