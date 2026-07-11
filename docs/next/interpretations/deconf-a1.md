# FABLE INTERPRETATION — DECONF Stage A1 (mechanical: C_dec = 1.0 exactly ON THE PRIMARY GRID, 11,848/11,848 grid decision triples concordant, zero discordances on every EXECUTED grid; this is an EXPLORATORY GRID-SCOPE equivalence result — the complete rev-B certificate is PENDING because §3.1(b) dual-initialization and §3.1(c) trajectory replay were NOT run; neither programme thesis moves)

- **Author:** Fable (interpretation agent), 2026-07-11; rev-2 after the GPT-5.6
  interpretation review (`poc/gpt56-review/rev-deconfa1i-20260711/last-message.json`),
  whose material-overreach findings are adopted in full. This document interprets; it
  changes NO frozen record, NO verdict object, NO results-log line, NO registered
  assumption, and performs no git/bd/kb operation. The coordinator commits.
- **Sources (read at source, in full):** `poc/deconf-a1/RESULT.md` + `a1-result.json` (the
  measured result, authoritative for every number below), `poc/deconf-a1/audit_a1.py` +
  `build_gsa.py` + `gsa-manifest.json` (what was actually computed — read line-by-line
  against the design), `docs/next/design/DECONF.md` rev-B (the BINDING interpretive frame,
  esp. §3.0's certificate semantics, §3.1's certificate DENOMINATOR — grid ∪ trajectory
  replay ∪ dual-initialization — §3.2's C_dec reading + triage ladder, §1's scoped
  invariance lemma, §9.1's honest limits),
  `poc/gpt56-review/rev-deconfb-20260711/last-message.json` (the external review that set
  the certificate framing), and
  `poc/gpt56-review/rev-deconfa1i-20260711/last-message.json` (the review of THIS
  document's rev-1, binding on this revision). For §5,
  `docs/next/interpretations/f2b-transfer-stage1.md` (post-judge-3 FINAL figures).
- **Epistemic discipline:** every load-bearing line carries its `[TAG]`. **MEASURED**
  restates a counted/computed fact strictly from a cited artifact (never recomputed);
  **STIPULATED** marks design rulings and framing adopted verbatim (including the entire
  rev-B licence structure — PROPOSED-ASM-1010/1011, coordinator registration pending);
  **DERIVED** marks an analytic observation made in THIS document from MEASURED facts or
  from direct code reading, disclosed as absent from the cited artifacts; **ASSUMED**
  marks a direction-only forward note, never load-bearing; **EXTRAPOLATION** marks a
  registered forward projection under DECONF's binding taxonomy (here ASM-0966).
- **Governance status of the run itself, stated first because it bounds everything:**
  the executed A1 is **EXPLORATORY — a pre-freeze execution** [MEASURED: RESULT.md status
  line]. The DECONF design routes through external review → prereg freeze → a registered
  runner-role re-run before any registered ruling. Every step of this execution is
  deterministic and pin-gated (all five corpus hashes, the runner sha `b62c3a72…`, the
  GS-A sha `4a28f7fa…`, the replayed shuffle map `05af8f50…` byte-verified against all
  three recorded run maps) [MEASURED: RESULT.md]; that the registered re-run reproduces
  these bytes for ~$0 marginal compute is the registered forward projection
  [EXTRAPOLATION: ASM-0966 — forward-looking, not measured]. Until that re-run lands,
  this document interprets a measured exploratory artifact, not a registered
  verdict-input.

> **PENDING TO COMPLETE THE CERTIFICATE — read this before citing anything below.**
> DECONF rev-B §3.1 defines the certificate statistic C_dec over the union
> **grid ∪ trajectory-replay (§3.1c) ∪ dual-initialization (§3.1b)**. The executed run
> covered ONLY the §3.1(a) grid (denominator 11,848): §3.1(b) dual eager/lazy
> initialization-order passes and §3.1(c) decision-for-decision replay of the logged
> f2b-replicate verifier trajectories were **NOT run** [DERIVED: §3 below, from
> audit_a1.py vs the rev-B procedure]. Therefore **11,848/11,848 is the measured
> GRID-SCOPE equivalence statistic, NOT the complete rev-B certificate statistic**
> [STIPULATED: rev-B §3.1 denominator; MEASURED: the executed grids]. §3.1(b) and
> §3.1(c) must be RUN — in the registered re-run or before it — before ANY
> complete-certificate claim; until then **no endpoint-wide, complete-certificate, or
> "certificate HOLDS" reading is licensed**, and every consequence in §4 that consumes
> the complete certificate is marked PENDING accordingly.

---

## 0. The mechanical facts, restated at grid scope

- PREMISE: [MEASURED: a1-result.json `C_dec`, `C_dec_exact`] **C_dec-on-grid = 1.0
  exactly — 11,848/11,848** decision triples concordant on the primary grid: three pinned
  corpora (d-qa 650 incl. 150 controls: 3,704 cells; d-qa-r 1000: 5,840 cells; d-qa-t
  360: 2,304 cells) × every admissible answer in the closed IF-C surface × both verifier
  variants (true; seed-pinned Sattolo derangement). This is an exhaustive count over the
  enumerated GRID decision space — no sampling error, no CI at that scope. Discordance
  list: empty (`n_discordant` = 0). It is NOT the complete rev-B C_dec, whose denominator
  also includes the unexecuted replay and init-order cells (header note; §3).
- PREMISE: [MEASURED: a1-result.json `grids`, `dext_supplementary`] Every executed
  secondary and supplementary grid is likewise fully concordant: the run-realized
  f2b-replicate protocol sub-grid (d-qa-r rank-prefix 250, 102-urn restricted label
  index) 1,460/1,460; the run-planned f2b-transfer stage-2 sub-grid (d-qa-t[:250],
  105-urn index) 1,592/1,592; the d-ext off-coverage abstention grid 4,000/4,000 (the
  store-independence of the abstention path measured on that grid, not asserted).
- PREMISE (vacuity guard — the grid does real work): [MEASURED: a1-result.json
  `decision_space_disclosure`] the kernel-side true-variant triples split 1,860 accepts /
  3,644 rejects / 420 abstentions (exactly the 150 non-checkable d-qa controls × their
  answer spaces), and the true and shuffled variants diverge on 1,673/5,924 item–answer
  pairs. Grid concordance was therefore measured across accepts, rejects, abstentions,
  AND shuffled-composition divergence — it is not a trivially-constant comparison.
- PREMISE (the counted circularity signature): [MEASURED: a1-result.json
  `true_variant_decidable_accept_vs_gold`] on all 5,504 decidable (item,
  admissible-answer) pairs, verifier-accept ⇔ membership gold with ZERO off-diagonal
  cells (accept|gold 1,860; reject|nongold 3,644; accept|nongold 0; reject|gold 0). The
  f2b-replicate assessment's circularity note — "gold was DEFINED by the same equality
  check() tests" — previously an analytic argument, is now an exhaustive count at grid
  scope.
- PREMISE: [MEASURED-BY-INVARIANCE, i.e. DERIVED in the artifact itself and tagged so
  there: a1-result.json `R_repro` + `status_tags`] **R_repro = lift(GS-A)/lift(kernel)
  ≡ 1.0 identically** — as an artifact-internal derivation. This is NOT a fresh model run
  and must never be cited as one: it invokes the §1 determinism lemma (identical
  decisions on the full REACHABLE decision surface ⇒ bit-identical endpoints), whose
  antecedent the executed run verifies only at grid scope; that the run-reachable
  surface, traversed through evolving lazy-load trajectory state, is fully covered is
  exactly what the unexecuted §3.1(c) replay exists to confirm [DERIVED: scope note of
  this document; STIPULATED: the lemma]. The kernel-arm lift it applies to (+0.1507 vs
  R3, BCa LB +0.1053) is restated context from the audited f2b-replicate record, not
  remeasured here [MEASURED: `measured_lift_context`, restated].

---

## 1. What was measured — a grid-scope equivalence result, read strictly inside the rev-B frame

LOAD-BEARING: [STIPULATED: DECONF §3.0 (PROPOSED-ASM-1010), adopted as binding] A1 is
designed as an **executable EQUIVALENCE/REGRESSION CERTIFICATE over an exact projection
of kernel-authored answer strings**; what was EXECUTED is the grid component of that
certificate. GS-A copies the kernel's own answer-bearing bytes (gloss.strip /
render_plain(groundingNote), claims = segments(canonical_text) — the pinned
`KernelVerifier._load` derivation itself, imported from the verified runner bytes)
[MEASURED: build_gsa.py + gsa-manifest.json]. Grid concordance was therefore *nearly
true by construction*, and the design says so in advance (§9.1: "a certificate, not a
discovery instrument"; the expected outcome was registered as non-load-bearing
EXTRAPOLATION ASM-0966, now resolved in its expected direction AT GRID SCOPE). The
stage's value, at the scope actually executed, is a partial version of the conversion
the design pre-registered: an analytic claim ("a generic aligned answer-key WOULD
reproduce it") became a measured, re-checkable fact ON THE GRID ("the answer-key
projection DOES reproduce every enumerated grid decision, bit-for-bit") — with the
replay and init-order components of that conversion still to run [STIPULATED: §3.3;
MEASURED: §0; DERIVED: the gap, §3].

The single narrow proposition SUPPORTED AT GRID SCOPE — not decided, because the rev-B
denominator is incomplete [STIPULATED: §3.0 wording, rescoped per the rev-2 review;
MEASURED: C_dec-on-grid = 1.0]:

> **On the enumerated grid, at the pinned harness/checker/output-space/init/store
> hashes, the pinned F2 runtime checker's decisions are reproduced exactly by the
> projected urn-keyed label/gloss/claim answer key.** Whether this extends to the
> logged run trajectories (§3.1c) and to both initialization orders (§3.1b) — the
> remainder of the rev-B certificate — is UNMEASURED and PENDING.

Equivalently, in the §3.2 vocabulary and at the same scope: the kernel's structural
fields (explication trees, primes, vectors, types, provenance frames, engine hooks) are
**decision/runtime-inert ON THE MEASURED GRID under the pinned topology**. That
sentence — and NOT "kernel-authored content is generic", and NOT any endpoint-wide or
complete-certificate reading — is the whole positive content of the grid result. GS-A is
not independently-generic content; its strings ARE the kernel's strings; nothing about
the value of authoring those strings is tested here [STIPULATED: §2.1/§3.0; this
restatement was the rev-B review's ranked concern #2, adopted verbatim].

DERIVED (a bounded robustness observation of this document, from reading audit_a1.py;
weakened per the rev-2 review, which is right that the rev-1 version overreached): the
GS-A-side checker (`GSAVerifier`/`GSAShuffledVerifier`) is a mirror class that
*physically has access only to the four projected columns* — no record file, no
derivation function, no engine is reachable at check time. Concordance of every
enumerated triple therefore establishes **extensional decision equivalence on the
enumerated cells**: each grid decision is computable from the projection alone. It does
NOT establish that the kernel-side checker performed no extra store reads — an extra
field may be read yet remain decision-inert on every enumerated cell — and a faulty
mirror can agree for coincidental or correlated reasons, so mirror-agreement is not a
read-set proof. The binding reading remains only the one above: structural fields are
decision/runtime-inert on the measured grid under the pinned topology. The residual
falsification surface the design named — the term-for-definition path, claim-polarity
membership, the shuffled-map composition, the order-dependent label map, engine
consultation inside `check()` — is CONSTRAINED at grid scope (any such channel that is
decision-relevant on an enumerated cell would have produced discordance and did not),
not closed: decision-inert reads, and channels that only activate on trajectory or
init-order states, are untouched [STIPULATED: §3.2 falsifiability note; MEASURED: zero
grid discordances incl. 1,673 divergent shuffled-composition pairs].

## 2. The triage ladder: does not fire on the executed grids — and what remains by-construction excluded

[STIPULATED: DECONF §3.2 — the four-cause triage (projection/adapter bug, incomplete
read-set, initialization-order difference, schema mismatch) is defined FOR the C_dec < 1
branch.] With grid concordance complete and an empty discordance list on every EXECUTED
grid, no triage is triggered there [MEASURED: §0], and **no
KERNEL-RUNTIME-CHANNEL-CANDIDATE exists on the executed grids** [MEASURED: zero grid
discordances; STIPULATED/DERIVED: the candidate label is assigned by the stipulated
classification rule, so its absence is a rule-consequence of the measured zeros, not
itself a raw measurement]. This exclusion is limited to the executed grids: the
unexecuted replay and init-order cells could in principle still produce a discordance
and hence a candidate [DERIVED: §3]. For completeness, the run's design bears on the
four causes anyway [DERIVED, from the code]: cause 1 (projection bug) and cause 4
(schema mismatch) are constrained by construction — the projection uses the checker's
own pinned load-time derivation functions and fails closed on every record/label/count
pin (ERR_RECORD_PIN, ERR_LABEL_DRIFT, ERR_LABEL_COLLISION: the label-collision list was
asserted empty, not assumed); cause 2 (incomplete read-set) is what grid concordance
constrains at grid scope in the extensional sense of §1 — no stronger; cause 3
(init-order) is only PARTIALLY probed — see §3, the material execution gap.

## 3. Execution-completeness honesty: what "exhaustive" covered, and what it did not

DERIVED (this document's own audit of audit_a1.py against the rev-B procedure; stated
because the interpretation must not inherit the word "exhaustive" beyond its object):

- The executed run implements DECONF §3.1(a) — the full decision-grid enumeration — in
  full, plus the two restricted-label-index protocol sub-grids and the d-ext supplement
  [MEASURED: §0].
- It does **NOT** implement rev-B §3.1(b) as specified (the dual eager/lazy
  initialization-order pass: the primary grids run eager `index_labels`-first only, with
  lazy `_load` occurring inside check as a side effect) and does **NOT** implement
  §3.1(c) at all (decision-for-decision replay of the logged f2b-replicate verifier
  trajectories with pinned log hashes). The design defines C_dec over
  (grid ∪ replay ∪ init-order); the executed denominator, 11,848, is grid-only. **This
  is why the header of this document rescopes the result to exploratory grid-scope
  equivalence, pending the complete rerun.**
- Mitigation, honestly weighed — and no stronger than PARTIAL: the label-collision set
  is empty by fail-closed assertion [MEASURED: build_gsa.py ERR_LABEL_COLLISION gate],
  which removes the only identified mechanism by which load ORDER can change `_by_label`
  contents (later-load-wins matters only under collisions), and the two restricted-index
  sub-grids (102 and 105 of 108 urns) probe the realized/planned partial-index states
  directly [MEASURED: §0]. So the init-order and trajectory-state risk is **partially
  mitigated and argued low — but NOT closed**: rev-B added logged sequential replay
  precisely because per-pair enumeration plus two restricted index states does not
  exhaust evolving checker state, and at this scope the residual is ARGUED, not counted
  — which is precisely the distinction A1 exists to erase and has, for this component,
  not yet erased.
- Consequence: **§3.1(b) dual-initialization and §3.1(c) trajectory replay must be RUN —
  in the registered re-run as frozen, or before it — for any complete-certificate
  claim; a frozen deviation note is the only registered alternative, and it would
  permanently cap the certificate at grid scope.** Nothing in this gap threatens the
  measured grid numbers; it bounds the noun. "Exhaustive" here means: exhaustive over
  the stateless per-pair decision grid and the two protocol-restricted index states —
  not over the evolving lazy-load trajectory state, and not over init order.

## 4. What grid-scope C_dec = 1.0 supports now — and what remains PENDING the complete certificate

**Supported NOW, at grid scope, exploratory status** [MEASURED: §0; STIPULATED: the
rev-B reading vocabulary]:

- The reading of §1: the kernel's structural fields are decision/runtime-inert ON THE
  MEASURED GRID under the pinned answer→check→resample topology; on every enumerated
  cell the store functions as an aligned deterministic answer key.
- The counted circularity signature (§0): verifier-accept ⇔ membership gold with zero
  off-diagonals on all 5,504 decidable pairs — the "gold is defined by check()" note is
  now a count at this scope, not an argument.
- A real, if narrow and strictly extensional, tightening of the falsification surface:
  any store channel that is decision-RELEVANT on an enumerated grid cell — on any path,
  any of the three corpora, either variant — would have produced discordance and did not
  [MEASURED: §0]. Per §1 (rev-2 correction), this does NOT extend to decision-inert
  reads and is not a read-set proof.

**PENDING — NOT currently licensed; each item consumes the COMPLETE rev-B certificate
(grid ∪ replay ∪ init-order) and is available only after §3.1(b)+(c) execute
concordantly in the registered re-run** [STIPULATED: DECONF §3.1 denominator + §6 row 1
+ §7.1 (PROPOSED-ASM-1010); DERIVED: the §3 gap]:

- The verdict-input **KERNEL-RUNTIME-STRUCTURE-INERT** at the pinned scope. Grid
  concordance is the largest component of its evidence, but the label is defined over
  the complete certificate and is NOT assigned by this result.
- The standing invariance-lemma rider on F2-line endpoints — *bit-for-bit invariance of
  the +0.1507 lift, its CIs, the shuffled-control readings, and any same-pin
  f2b-transfer stage-2 endpoints under replacement of the kernel store by GS-A*. The §1
  lemma's antecedent quantifies over the full RUN-REACHABLE decision surface; the
  executed run verifies it only on the grid; the replay component exists precisely to
  cover the trajectory-reachable remainder. No endpoint-wide invariance claim is
  licensed until then. (Even once complete: "future" runs are covered only under
  identical re-pins; any checker/harness/schema/output-space/init/store change voids the
  lemma and requires an A1 re-run.)
- The mechanical headline re-scoping of the F2 line to "aligned deterministic answer-key
  + retry". The grid result makes this the expected outcome, but rewording a frozen
  line's rider on the strength of a grid-only exploratory artifact would consume the
  complete certificate; it waits [STIPULATED: §6; RESULT.md "still needed" item 3 —
  and the wording is in any case the maintainer's to fix, not this document's].
- Stage B's arm-sharing economy (omitting the conditional kernel-verify-retry arm
  because the GS-A arm carries both readings). The relevant d-qa-t[:250] sub-grid is
  fully concordant, 1,592/1,592 [MEASURED: §0], which is necessary but not sufficient:
  the omission rule rides on the invariance lemma, hence on the complete certificate.
  Until then, Stage B planning must either retain the conditional kernel arm or
  explicitly condition its omission on the completed certificate [STIPULATED: §5.1
  conditional-arm rule].

**NOT licensed at ANY scope — each clause within the binding frame, restated without
widening** [STIPULATED: §3.0/§6/§9.1, clause by clause]:

- It does NOT show kernel-authored content is generic, replaceable, or valueless. GS-A's
  strings are the kernel's strings; whether independently-authored plain/nonce content
  reproduces anything is knull-v2's authored-content channel, untouched and still
  blocked on the plain-arm quality-gate ruling.
- It does NOT bear on authoring economics (A-F0), consumption channels (A-E2), or any
  architecture whose store coupling is not answer→check→resample.
- It does NOT extend beyond the pinned model context: **R-1/SmolLM2-135M only; no
  extrapolation to the 100M–2B rung band is licensed by anything here** — the lemma
  quantifies over the checker, not over model scale.
- It does NOT move either programme thesis. **The correctness thesis and the efficiency
  thesis both remain INCONCLUSIVE-PENDING.** A1 is a pre-ladder CPU attribution
  diagnostic: it occupies no gate rung and unlocks none (it is NOT G1); it bears on the
  ATTRIBUTION of the already-measured F2 lift — the lift is real and stands
  byte-identical in its frozen record, and its runtime mechanism is, AT GRID SCOPE and
  pending the complete certificate, measured to be consistent with
  answer-key-structural rather than kernel-structural operation. What the lift is worth
  to either thesis turns on the still-unrun legs: the completed certificate itself,
  alignment-vs-generic-retrieval (Stage B's Δ_align TOST/LCB contrast), authored-content
  value (knull-v2), authoring cost (A-F0), and the stage-2 external-gold system lift
  (f2b-transfer). If anything, the grid result sharpens the deflationary risk A1 was
  built to price: the F2 line now survives, on the executed evidence, as "verify-retry
  against an item-aligned deterministic answer key lifts a 135M host on this
  self-authored, kernel-covered, oracle-addressed slice" — with the kernel measured (at
  grid scope) as ONE WAY TO AUTHOR such a key and no kernel-specific runtime
  contribution detected on the grid [STIPULATED: the §5.2 ALIGNMENT-SPECIFIC licence
  sentence, whose runtime half the completed A1 would supply; the alignment half awaits
  Stage B].
- It does NOT retire the item-generation or store-addressing circularities: the items
  are rendered from the kernel's own records and every item pins the record that answers
  it; the self-authored/kernel-covered/oracle-addressed rider rides on [STIPULATED:
  PROPOSED-ASM-1017].

## 5. Relation to the f2b-transfer stage-1 endorsement — different confounds, not conflated

The two results are orthogonal probes of the SAME assessment ceiling and must not be
summed into one sentence:

- **f2b-transfer stage 1** broke the **gold-definition circularity**: it asked whether
  the membership gold — defined by the kernel's own string-equality — is *externally
  endorsable*, and blind human-anchored adjudication endorsed it at A = 320/333 = 0.9610
  (one-sided 95% Wilson LB 0.9395, post-judge-3 FINAL; the pre-judge-3 snapshot 0.9784
  cited in RESULT.md's premises is superseded) [MEASURED:
  interpretations/f2b-transfer-stage1.md §0, restated]. That is a claim about the gold's
  CONTENT contacting external understanding.
- **DECONF A1** probed the **runtime-read-set question at grid scope** — it did not
  close it. What is measured is concordant decisions on every enumerated grid cell
  [MEASURED: §0]; the reading "the runtime checker consumes nothing beyond the projected
  answer key" is, per §1, the stipulated/derived extensional interpretation of that
  concordance, holds only on the measured grid, and does not exclude decision-inert
  reads [STIPULATED/DERIVED: §1]. The full rev-B question — over grid ∪ replay ∪
  init-order — remains open until §3.1(b)+(c) run. This line of inquiry concerns the
  MECHANISM's information diet and is deliberately silent on whether the key's content
  is true, endorsable, or worth authoring.
- The bonus contingency links them precisely and no further: A1 count-verified
  (off-diagonals zero on all 5,504 decidable pairs) that verifier-accept ≡ membership
  gold at grid scope — the verifier IS the membership-gold generator on the enumerated
  cells, counted rather than argued [MEASURED: §0]. f2b-t stage 1 measured that this
  same membership gold agrees with an external human-anchored gold at 0.961 on the
  resolved slice. Chaining the two ("the runtime accept signal coincides with an
  externally-endorsed gold") is a direction-only composition — the frozen f2b-transfer
  design itself forbids inferring the stage-2 primary from A, and retry dynamics on the
  judge–kernel disagreement set are not a pure function of either number [ASSUMED —
  direction-only, non-load-bearing; STIPULATED: f2b-transfer design.md §2 layer 2].
  Stage 2 measures it; nothing here does.
- One economy transfers only CONDITIONALLY: the d-qa-t[:250] planned sub-grid is fully
  concordant [MEASURED: the sub-grid], so IF the complete certificate lands AND stage 2
  runs at the identical pins, f2b-transfer stage-2's endpoints would be covered by the
  invariance lemma and Stage B's kernel arm and a GS-A arm would be bit-identical. That
  arm-omission economy is PENDING the complete certificate (§4), not available on the
  grid result alone [STIPULATED: lemma scope; DERIVED: §3 gap].

## 6. What follows (recommendations to the coordinator/maintainer; no action taken here)

1. **Complete the certificate**: external review of the executed-A1 artifact + prereg
   freeze, then the registered runner-role re-run — which MUST include §3.1(b)
   dual-init-order and §3.1(c) logged-trajectory replay (or record an explicit frozen
   deviation, accepting a permanently grid-capped certificate; §3 above) [STIPULATED:
   DECONF status line; DERIVED: the gap]. No complete-certificate, endpoint-wide, or
   verdict-input claim before this lands.
2. Coordinator: register PROPOSED-ASM-1010–1017 and create P3-E-DECONF-0 / P3-E-DECONF-B
   per design §11 (no bd operation was performed by the run or by this document).
3. Maintainer: the §6 row-1 invariance-lemma rider wording and Stage B's
   conditional-arm decision are BLOCKED on item 1, not merely pending wording — see §4.
4. ASM-0966 (the expected-outcome extrapolation) is resolved in its registered direction
   AT GRID SCOPE; its replay/init-order component remains open with the rerun. The
   expected-direction disclosure should ride any citation of this result — the value is
   the certificate (when complete), not surprise [STIPULATED: §3.3/§9.2].

---

## Epistemic register (what this interpretation relied on)

- **MEASURED:** every number in §0 (grid C_dec 11,848/11,848; sub-grids 1,460/1,460 and
  1,592/1,592; d-ext 4,000/4,000; the 1,860/3,644/420 decision mix; 1,673/5,924
  divergence; the zero off-diagonal accept⇔gold contingency; all pins), restated from
  a1-result.json/RESULT.md without recomputation; the f2b-replicate lift context and the
  f2b-transfer stage-1 FINAL endorsement figures, restated from their own artifacts.
  Note the scope discipline adopted in rev-2: "no runtime channel candidate" and
  "runtime-inert" are NOT purely MEASURED — the measurements are the concordant
  decisions; the inertness/no-candidate readings are their stipulated/derived
  interpretation, grid-scope only (§1, §2, §5).
- **STIPULATED:** the entire interpretive frame — certificate-not-content-test, the
  §3.1 certificate denominator (grid ∪ replay ∪ init-order), the grid-scope reading of
  C_dec = 1.0 as structural-field decision-inertness on the measured grid, the
  four-cause triage semantics, the scoped invariance lemma, the R-1-only scope bar, the
  riders — adopted verbatim from DECONF.md rev-B (ASM-0960–0966 +
  PROPOSED-ASM-1010–1017, registration pending) and the two GPT-5.6 reviews this
  document answers.
- **DERIVED (this document's own, disclosed):** the §1 extensional-equivalence
  observation (bounded per the rev-2 review: not a read-set proof); the §3
  execution-completeness audit (grid-only C_dec denominator; §3.1(b)/(c) not executed;
  collision-emptiness as PARTIAL mitigation only); the §2 by-construction triage
  mapping; the R_repro scope note in §0.
- **ASSUMED (direction-only, never load-bearing):** the §5 chained
  accept↔external-gold composition.
- **EXTRAPOLATION (ASM-0966, registered forward projection):** that the registered
  re-run reproduces these bytes; resolved in its expected direction at grid scope only,
  open for the replay/init-order components.
- **R_repro ≡ 1.0** is cited only as MEASURED-BY-INVARIANCE, i.e. a derivation inside
  the artifact whose lemma-antecedent is grid-verified only (§0) — never as a model run,
  and never as an endpoint-wide guarantee before the complete certificate.

Neither the correctness thesis nor the efficiency thesis moves off
INCONCLUSIVE-PENDING on this result. The result itself is EXPLORATORY, GRID-SCOPE, and
PENDING the registered complete rerun (§3.1(b) dual-initialization + §3.1(c) trajectory
replay) before any complete-certificate reading.
