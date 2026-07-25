# KOT-FAIR/2 Part-C application — the co-equal correctness claim family (W3) and the five #57 guardrails — freeze-grade specification (Rev4)

> **STATUS: DESIGN — PROPOSED, NOTHING FROZEN; Revision 4 (2026-07-25) is the R0
> consistency cleanup the Rev3 delta-check requested (4/5 fixes CLOSED — S1
> direction, licensed micro statement, totalized cov-at-R + BLOCKED, tie cascade —
> all untouched here; fix 3's two stale-R0 residuals in §8.3 and §9 repaired).
> Revision 3 (2026-07-25) applied the
> Rev2 delta-check (NEW-DEFECT, converging).** This document operationalizes the
> maintainer-RATIFIED #57 decision — **option (a): a co-equal, non-composite
> correctness-endpoint claim family standing beside an intact W1, frozen together with
> five anti-gaming guardrails** — recorded in
> [p3-phase0-synthesis.md §5 + Revision-2 item 9](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3-phase0-synthesis.md).
> It RESOLVES the KOT-FAIR/2 "Part C — correctness instrument — DEFERRED pending #57"
> placeholder
> ([kot-fair-2-spec-p3mf0.md](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kot-fair-2-spec-p3mf0.md))
> and answers freeze-readiness requirement 8 ("add a claim-capable correctness
> instrument or explicitly scope it out",
> [kot-fair-2-review1-freeze-readiness.md](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kot-fair-2-review1-freeze-readiness.md)).
> **Revision 3** repairs the five narrow defects the Rev2 delta-check found — the S1
> threshold-direction reversal, the mathematically false macro selective-risk
> disclosure, the V0/R0 budget-anchor gap, the two collision-closure definedness
> seams, and the missing wrapper-argmax tie rule — while keeping every Rev2 fix that
> delta-check CONFIRMED (NO-OUTPUT + per-component identity, strict majority,
> component-equal weighting + conjunctive caps, dev-only secondary selection +
> roster-wide max-t, S-BENCH/S-HON + separate generative passes, UNANS hardening,
> enum literals, the completed §13). **Revision 2** applied the seven load-bearing
> defects + four additional items of the
> cross-vendor review (verdict NEW-DEFECT); that review's CONFIRMED-SOUND elements —
> the coverage-at-frozen-risk primary, alpha-free conjunctive validity gates,
> VOID-cannot-manufacture-a-PASS, the delivered-wrong collapse (as repaired for
> missing output), and the beside-not-conjoined structure (separate α families,
> no-disjunction, cross-status line, unchanged W1 abstention scoring) — are kept
> unchanged in substance. Itemised dispositions: "## Revision 2 — cross-vendor
> defects applied", "## Revision 3 — Rev2-delta-check repairs applied", and
> "## Revision 4 — R0 consistency cleanup". Nothing
> here is committed, frozen, preregistered, scheduled, or
> run; no registry row, verdict, or frozen object is touched; no `ASM-` id is minted
> anywhere in this file (prereg-row ids are assigned at prereg-freeze); every
> designer parameter is `[STIPULATED]`, never presented as measured. This revision
> rides a further delta-check before landing; content enters KOT-FAIR/2 only through
> the spec's next revision (intended Rev6), which needs its own re-review.
> Author: Fable, architecture-advisor role, 2026-07-25. Participants named by role
> only.
>
> **Tags** (four-tag house scheme): `[MEASURED: ref]` observed fact cited to its
> registry/analysis object, restated strictly inside its scope; `[LIT-BACKED: ref]`
> literature-dependent choice with a resolvable backing; `[STIPULATED]` design choice
> awaiting ratification; `[EXTRAPOLATION]` forward claim beyond measurement —
> deliberately unused as a premise anywhere in this document.
> Row labels continue the spec's series as `PROPOSED-PREREG-ROW-MF0-C1…C12`
> (labels only — nothing registered).

---

## 0. The decision being operationalized, and this document's premises

PREMISE: [MEASURED: maintainer #57 ruling as recorded in docs/next/design/p3-phase0-synthesis.md §5 and its Revision-2 item 9] the
maintainer ratified #57 option (a) — a co-equal correctness-endpoint claim family
beside an intact W1, with five anti-gaming guardrails frozen alongside it; this
document takes the ruling as given and does not re-argue it.

PREMISE: [MEASURED: kot-fair-2-review1-freeze-readiness.md Part C, read at source; restated verbatim in the spec's Part-C placeholder] KOT-FAIR/2
today reports correctness columns (refusal, unconditional dangerous-wrong, selective
risk, covered/uncovered — spec §1.2) but gives them no frozen definitions,
challenge-set construction, statistical gates, or claim status, so it can report a
correctness signal but cannot adjudicate a correctness-value win.

PREMISE: [MEASURED: p3d-threat-factorial-controls.md §4.1 and §5.2, the deferral read at source] P3-D-THREAT Rev1 fixes the
attribution CONJUNCTION STRUCTURE for a correctness framing but defers the
correctness margins and endpoint definitions to "the separate correctness design";
this document is that design for the margin and endpoint content.

PREMISE: [MEASURED: registry state as restated with scope in docs/next/programme-3-neurosymbolic-architecture.md §0 premise block, which cites the owning registry objects] the
programme's measured record licenses no correctness win anywhere — both theses are
INCONCLUSIVE-PENDING, the four-condition scoreboard is 0–0, and measured external
kernel coverage on benchmark-style material is approximately zero today (0/1,550
define-lane; g8 0/1,000; m0b coverage_fraction 0.3542 is corpus-indexed to the
TinyStories family at molecules-v0 on one incomplete kernel instance and
extrapolates to no other corpus); used here ONLY to reason about floor reachability,
never as evidence for or against any claim.

**Design decision `[STIPULATED — coordinator/Fable to ratify]`:** this document
specifies the correctness claim family's frozen structure — name, definitions,
resource envelope, endpoint hierarchy, guardrails, statistics, comparators,
arm-variant identity, reporting language, and ratification items — to freeze-grade
completeness, so that the #57 ruling becomes an executable part of the KOT-FAIR/2
freeze rather than a sentence in a synthesis; §12 states honestly what this document
does not do. (Prereg-row ids for every stipulation are assigned at prereg-freeze;
none is registered here.)

**Naming `[STIPULATED]`.** The obvious name "W2" is TAKEN: the parent defines W2 as
the shrink objective (W1-conditional Pareto sweep, parent §1.4). The correctness
claim family is therefore named **W3** — the programme's third win condition,
co-equal with W1 and NOT conditional on it. Disclosure: a round-1 architecture
candidate was once labelled "W3" in docs/next/arch/round1-critique-synthesis.md
(Counterfactual Evidence Mesh); that label lives in the retired candidate namespace
(merged into K2) and does not collide with the win-condition namespace {W1, W2}.
Routine stipulation; the ratifier may rename without touching other content.

---

## 1. Frozen definitions (the D-block)

All definitions are `[STIPULATED]` and become binding only at prereg-freeze. They are
written to be MECHANICAL: every term is computable by the grader from frozen per-item
rows with no judgement call.

- **D1 — Output classification (three terminal classes, Revision 2 per defect 3).**
  Every issued item receives exactly one of {ANSWER, ABSTENTION, NO-OUTPUT}:
  - *ABSTENTION*: the output matches the frozen abstention pattern set (exact
    byte-pinned format per benchmark, `abstention_format_sha256` in the manifest
    row; the set includes the pinned refusal patterns — a safety refusal is an
    abstention), or, on option-scored tasks, the arm's confidence functional (below)
    is under its dev-selected threshold (D7).
  - *NO-OUTPUT*: a complete non-return — empty output, harness-confirmed failure to
    return, or a timeout returning no content. NO-OUTPUT is NOT an answer and NOT an
    abstention; its treatment is fixed in D3/D4 (no coverage credit, adverse risk
    charge — Revision 2: the Rev1 rule that classified a non-return as an ANSWER
    perversely paid coverage, the primary statistic, for producing nothing).
  - *ANSWER*: everything else. Fail-closed: malformed outputs, parse failures,
    protocol violations, and timeouts that return content are ANSWERS — content was
    delivered.
  - Per task class: *generative tasks* classify from the logged output text;
    *option-scored tasks* carry a pinned per-arm **confidence functional** over the
    logged option scores (comparators: a register-item-26 closed-set wrapper
    functional; kernel-bearing arms may declare their native fail-closed signal,
    e.g. engine derivation-found/none, as their functional). *Generative-task
    confidence functionals exist too* (Revision 2 per defect 5): the item-26 closed
    set pins, per generative benchmark, at least (i) length-normalized answer-span
    log-probability (normalization pinned), (ii) self-consistency agreement over k
    pinned samples (k, temperature, seeds pinned), and (iii) a P(true)-style
    self-evaluation probe (prompt bytes pinned) — so D7 threshold selection and
    risk–coverage curves are defined on generative components; the explicit
    abstention pattern remains an unconditional abstention route on top.
  - Arm-vs-instrument missingness: NO-OUTPUT is an ARM property and scores
    adversely (D4); missing BENCHMARK items are an instrument property, never
    imputed, and scorer loss above the spec §1.4 threshold invalidates the
    component — inherited unchanged.
  - W1 scoring is UNTOUCHED by D1: for the index, abstentions, parse failures,
    malformed outputs and missing outputs score incorrect exactly per spec
    §1.2/§1.4. D1 adds parallel per-item flags; it re-scores nothing.
- **D2 — Delivered-wrong.** An item is DELIVERED-WRONG for an arm iff it is an
  ANSWER (D1) scored incorrect by the frozen scorer. There is NO hedged-wrong
  exemption: free-text hedging is not machine-checkable and is a gaming channel, so
  **every wrong answer delivered as an answer is dangerous** — the review's
  dangerous/harmless distinction is collapsed fail-closed to its strict side
  (stricter than the freeze-readiness Part C taxonomy; maintainer call, §13-2). The
  spec's column name "unconditional dangerous-wrong rate" is retained as an alias
  for D4.
- **D3 — Coverage (answer rate) and the frozen weighting estimand (Revision 2 per
  defect 4).** `cov` = the component-equal MACRO answer rate: per W3 component, the
  fraction of its issued items classified ANSWER; then the unweighted mean over the
  rung's frozen W3 component set — every manifest component holding vector
  membership at that rung (scalar-eligible or not) PLUS the D8 challenge component,
  which carries exactly ONE component weight regardless of its item count.
  NO-OUTPUT items stay in every denominator and never enter the coverage numerator.
  **The weighting estimand is FROZEN here**: all W3 family statistics (cov, D4, D5,
  S1–S3) are component-equal macro — aligned with the house fixed-weight discipline
  (spec §6.2: weights fixed, items resampled within components) and closing the
  channel where raw item counts (the UNANS count above all) dominate the primary
  and the floor. Raw-item (micro) versions of every statistic are mandatory
  DIAGNOSTIC columns; the V2 risk cap additionally binds on micro (§5). W3 is not
  an index-scalar claim and does not depend on scalar eligibility.
- **D4 — Unconditional adverse-outcome rate (udw⁺).** Per component,
  `P(DELIVERED-WRONG or NO-OUTPUT)` over issued items; macro-aggregated per D3.
  This is the V2-bounded quantity (Revision 2 per defect 3): a non-return earns no
  coverage AND charges the risk cap — crashing on hard items cannot imitate
  abstention. The Rev1 identity `udw = cov × sr` is REPLACED by
  `udw⁺ = cov·sr + P(NO-OUTPUT)` (per component; disclosed on every report
  surface). The pure delivered-wrong rate `udw = P(ANSWER ∧ incorrect)` remains a
  mandatory column.
- **D5 — Selective risk.** `sr = P(incorrect | ANSWER)` per component,
  macro-aggregated over components where defined; a component with zero answers
  contributes no sr term (disclosed count), never an imputation.
- **D6 — Accepted soundness-violation rate.** For arms that emit a machine-readable
  provenance/verification endorsement: `asv = P(ANSWER ∧ incorrect ∧ endorsed)`,
  macro-aggregated. Mandatory column for every engine/provenance-bearing arm;
  identically zero by construction for arms that never endorse (disclosed, not
  celebrated — no endorsement means no D6 exposure and also no provenance value).
- **D7 — Operating points.** Each arm's thresholds are selected on the hash-pinned
  dev split ONLY (the frontier record's dev-split discipline; where a component
  lacks one, register item 24 supplies it, item-ID-hash-partitioned and pinned
  BEFORE any anchor output is inspected, mirroring the spec's Rev5 partition
  discipline). Frozen pre-test, per arm: (i) the PRIMARY operating point —
  maximize dev macro cov subject to the arm's dev udw⁺ UCB ≤ β_dw, decided by the
  deterministic selection/tie cascade below; and (ii) one pre-registered threshold
  per S1 grid point g: the **LARGEST** candidate threshold t — over the finite
  ordered set of observed dev confidence values ∪ {+∞} — whose dev macro coverage
  ≥ g (Revision 3 per delta-check defect 1: D1 answers at confidence ≥ t, so
  coverage is NON-INCREASING in t; the Rev2 "smallest threshold" rule therefore
  selected MAXIMUM coverage and collapsed every grid point onto one threshold,
  invalidating the matched-coverage comparison; the largest qualifying threshold
  is the closest attainable operating point at or above g, and distinct grid
  points map to distinct thresholds wherever the dev curve separates them;
  Revision 2 per defect 6: NO test-data-dependent threshold or grid-point
  selection exists anywhere). An arm with no dev-feasible primary point: for S, W3
  is NOT-CLAIMABLE at that rung (disclosed); a comparator enters at its most
  abstaining pinned threshold with the infeasibility disclosed.
  **Deterministic selection/tie cascade (Revision 3 per delta-check defect 5),
  applied to EVERY dev argmax in this design — the D7 primary point, the per-grid
  thresholds, and the item-26 wrapper-and-threshold selection:** candidates are
  ordered by (1) the selection objective (higher dev macro cov; for grid
  thresholds, the largest-qualifying-threshold rule above); ties → (2) lower dev
  macro udw⁺; ties → (3) lower dev micro udw⁺; ties → (4) earlier position in the
  pinned, ratification-ordered closed wrapper-candidate list; ties → (5) the
  larger threshold (the more conservative operating point); final ties → (6)
  ascending byte order of the wrapper script hash. A total order — no operator
  discretion survives (discrete dev coverage makes argmax ties likely, so a bare
  argmax was operator discretion in disguise).
- **D8 — Challenge component UNANS-KOT/1.** A programme-owned generated component
  whose items' GOLD behaviour is abstention or whose surface invites a confident
  wrong answer: unanswerable/underdetermined premises, ambiguous references, BOTH
  orientations of directional relations, mutated-premise near-duplicates of
  answerable items, valid-but-wrong-program acceptance probes; held-out generator
  families per the sealed discipline. An ANSWER on a gold-abstain item scores
  incorrect (hence delivered-wrong). **Positive controls (Revision 2):** the
  component includes seeded ANSWERABLE near-duplicate twins at a pinned fraction,
  so blanket abstention on the component forfeits their coverage — the component
  cannot be gamed by answering nothing. UNANS-KOT/1 is **W3-only and vector-only**
  (never in any W1 scalar or domain mean) and carries ONE macro component weight.
  Certification and audit requirements: register item 25 (§10). [LIT-BACKED:
  content list per the freeze-readiness Part C requirement — ambiguity/
  unanswerability, directional orientations, valid-but-wrong programs,
  paraphrase/source shifts, held-out compositions.]
- **D9 — Arm-variant identity: S-BENCH and S-HON (Revision 2 per defect 7).** Every
  registered arm (S and each comparator) names two POLICY VARIANTS of the SAME
  packed artifact (identical KOT-SIZE/2 figure-1 bytes; divergent artifacts are two
  different systems requiring separate registrations):
  - **S-BENCH** — the forced-answer benchmark policy; W1 evaluates S-BENCH rows
    exclusively (consistent with spec §1.2, where abstention scores incorrect, and
    with KOT-HON/1 §4.2's non-penalised variant).
  - **S-HON** — the registered abstention policy (D1/D7); W3 evaluates S-HON rows
    exclusively. For comparators, the item-26 wrapper IS the hon variant.
  - *Option-scored components*: the two variants share the same forward passes and
    logged rows by construction (the policy differs only in post-hoc thresholding)
    — one run serves both families.
  - *Generative components*: the variants are separate preregistered decoding/output
    policies and run as SEPARATE PASSES (an honesty-first refusal policy cannot be
    reconstructed from forced-answer outputs, nor vice versa); W1 consumes S-BENCH
    generative rows, W3 consumes S-HON generative rows; both passes' resource
    ledgers are recorded separately, and the extra generative pass is disclosed
    campaign cost.
  - "One campaign" therefore means: ONE frozen registration containing both named
    variants — shared rows where the policies coincide, separate passes where they
    diverge. (Material call, §13-11.)

---

## 2. The W3 claim

**The claim licensed by a W3 PASS at rung \(R_k\), verbatim `[STIPULATED]`:**

> "At rung \(R_k\), S — itself fitting every component of the frozen budget
> \(B_k\) at the adverse bound — answers at least \(\delta_{cov}\) more of the
> frozen KOT-AI-INDEX/2-vN suite (component-equal weighting) than every
> pre-registered selective-prediction comparator and baseline family searched under
> the same budget \(B_k\), while keeping its unconditional adverse-outcome rate
> within the frozen bound \(\beta_{dw}\) (UCB95) and its coverage above the frozen
> floor \(c_{min}\), at operating points selected before test scoring."

It never licenses "S is safe", "S is correct", "S knows when it doesn't know" in
general, any statement off the frozen suite, or any efficiency statement. Kernel
attribution additionally requires the stage-2 attribution family (§6); without it a
W3 stage-1 pass is a GENERIC-TOOL-LABELLED result, exactly per THREAT Rev1 §4.2.

Plain-language reading: W1 asks "is the system better per resource?"; W3 asks "at
the same resource budget and a fixed, pre-declared tolerance for delivered wrong
answers, does the system usefully answer more?" — the add-capability, fail-closed
value thesis the Phase-0 synthesis re-weighted toward, made adjudicable without
conjoining it to an efficiency bar.

---

## 2a. V0 — the common W3 resource envelope (Revision 2 per defect 1)

`[STIPULATED]` `[PROPOSED-PREREG-ROW-MF0-C10]`

**The rule:** EVERY W3 arm — S-HON above all — must be \(B_k\)-admissible under the
SAME spec §0 budget vector and the spec's direction-aware admissibility law: S-HON
proves fit at the ADVERSE bound per coordinate (UCB95 vs ceilings, LCB95 vs floors,
per the MF0-R4a/R5d laws); comparator membership at the point estimate; every arm's
abstention/wrapper machinery is arm cost inside the envelope. This gate is
**independent of W1's claimability**: \(B_k\) derives from the §5.3 measured budget
anchor, which exists at every rung IN W3 CLAIM SCOPE (R1–R3; rung-scope rule below)
regardless of the §0 scalar-collision invariant — so at a W1-UNAVAILABLE
(scalar-collision) rung the envelope still binds and S cannot buy coverage with
uncounted compute while its opposition is budget-constrained. V0 failure for S ⇒
`w3_status = NOT-CLAIMABLE` (resource-inadmissible, disclosed); it is a validity
gate and consumes no alpha.

**The rejected alternative, surfaced (material call, §13-8):** an explicitly
UNMATCHED-resource correctness claim ("S answers more at bounded risk, whatever it
costs") is coherent but is a different, weaker claim family — it would need its own
roster definition (opposition unconstrained by \(B_k\)) and its own licensed
sentence, and it abandons the fair-accounting discipline the framework exists to
enforce. Matched-\(B_k\) is the proposed default; ratifying the unmatched variant
instead (or additionally, as a separately-labelled family) is the maintainer's call.

**Rung scope (Revision 3 per delta-check defect 3):** V0 is executable exactly
where a RATIFIED measured budget anchor exists — today R1–R3 (the spec §5.3 anchor
list); the R0 anchor is census-only (spec register item 21) and derives no
\(B_0\), so the Rev2 "every rung" wording was not executable at R0. Default
disposition: **W3 is CLAIM-INCAPABLE at R0** — `w3_status = NOT-CLAIMABLE` (no
budget anchor at the rung) — matching W1's own R0 posture (spec §1.5: R0 is
vector-first and cannot carry W1). R0 W3 KILL criteria remain registrable in
ABSOLUTE form only (a pre-registered bound violation, e.g. on udw⁺, needing no
comparator and no envelope) under the §1.6 census interlocks; comparative R0 W3
registrations are prohibited absent an anchor. The §8.3 availability statement is
correspondingly scoped: "W3 available where W1 is UNAVAILABLE" means the
SCALAR-COLLISION rungs (R1+), never R0. **Alternative, surfaced as a NEW material
call (§13-15):** ratify an R0 budget anchor (extending spec register item 21 with
a measured budget-anchor leg) if R0 W3 claims are wanted; the default here is the
scoping, not the new anchor.

---

## 3. Guardrail 1 — the frozen endpoint hierarchy

`[STIPULATED]` `[PROPOSED-PREREG-ROW-MF0-C2]`

**Design decision `[STIPULATED — coordinator/Fable to ratify; material call
§13-1]`:** the PRIMARY correctness endpoint is **coverage at frozen risk** — not the
unconditional bound itself, and not selective risk. Reasons, in order: (i) a bound is
an absolute property, not a comparative win — a claim family needs a comparative
primary, and the unconditional bound does binding work as a validity GATE inside it
(a stronger role than "secondary": it can void or fail the claim alone); (ii)
selective risk is the most abstention-launderable statistic in the family and may
not headline; (iii) coverage-at-frozen-risk is monotone in the useful direction —
it rewards answering more only while the risk cap holds — and with all thresholds
dev-selected (D7) it has no post-hoc operating-point freedom [STIPULATED: design
reasoning; the risk–coverage framing is standard selective-prediction practice per
reports/lit-p3-parse.md at that review's inherited status]. (Confirmed sound by the
cross-vendor review; kept in substance.)

**The frozen hierarchy (order binding; no post-hoc promotion):**

| Tier | Endpoint | Test | Status |
|---|---|---|---|
| **W3-P (primary)** | Coverage at frozen risk: \(\min_C LCB95(cov(S) - cov(C)) > \delta_{cov}\) over EVERY W3 roster comparator \(C\), max-t simultaneous one-sided bounds, conditional on validity gates V0 (§2a), V1 (§4), V2/V3 (§5) | one-sided, FWER α = 0.05 across the roster | claim-capable (the W3 claim) |
| **W3-S1** | Adverse-outcome superiority at the frozen matched-coverage point: \(\min_C LCB95(udw^{+}(C) - udw^{+}(S)) > \delta_{dw}\), both arms evaluated at their PRE-REGISTERED dev-calibrated thresholds for the ONE grid point \(g^{*}\) frozen at prereg (rule below) | one-sided, max-t across the roster, gatekept | claim-capable only as a REGISTERED secondary, never a headline |
| **W3-S2** | Selective-risk superiority at the primary operating point: \(\min_C LCB95(sr(C) - sr(S)) > 0\); UNTESTABLE (sequence stops) if any arm's realized macro cov < 0.05 | one-sided, max-t across the roster, gatekept | same |
| **W3-S3** | KOT-HON/1 asymmetric-utility superiority: \(\min_C LCB95(S_{\lambda}(S) - S_{\lambda}(C)) > 0\) at λ = 3, macro-weighted, NO-OUTPUT scored −λ (fail-closed) | one-sided, max-t across the roster, gatekept | same — and its adoption is a MATERIAL call (§13-13): KOT-HON/1's own design conditions any claim-surface use on maintainer + review-gate approval |
| **Diagnostics** | full risk–coverage curves + AUACC; covered/uncovered store-slice split with the corpus-indexed covered-fraction number; per-domain and per-component coverage/risk vectors; micro (raw-item) versions of all statistics; udw vs NO-OUTPUT decomposition; D6 asv distribution; semantic-correctness vs parse-validity split; refusal rate; dev-vs-test coverage drift at every pre-registered threshold | descriptive, CI-reported | NEVER claim-capable |

**Secondary-test completeness (Revision 2 per defect 6):**

1. **Scope and per-comparator control:** each secondary step is a family of
   per-comparator contrasts controlled by max-t simultaneous one-sided bounds
   across the FULL W3 roster within that step; the step passes only on the min over
   comparators. Individual per-comparator conclusions are reported from the same
   simultaneous bounds (licensed exactly as the parent's §2.5 multiplicity note
   licenses them) — never from unadjusted per-pair tests.
2. **S1 selection-awareness (quantifier + threshold rule corrected Revision 3 per
   delta-check defect 1):** the grid point \(g^{*}\) is frozen AT PREREG from
   dev/CAL data only — \(g^{*} = \max\{g \in \{0.25, 0.50, 0.75\}\) : EVERY W3
   arm, **S included**, attains dev macro coverage ≥ g at some candidate
   threshold\}; if the set is empty, S1 is declared untestable at freeze; with S
   inside the quantifier, S1 can never be scheduled at a coverage S itself cannot
   reach. Every arm's threshold for \(g^{*}\) is the D7 pre-registered
   LARGEST-qualifying threshold (the Rev2 smallest-threshold rule was
   direction-reversed against D1's answer-at-or-above convention and collapsed
   the grid). NO
   quantity in S1 is selected on test data, so no selection-aware correction is
   owed; the estimand is "udw⁺ at the dev-calibrated \(g^{*}\) operating point"
   (realized test coverage at that threshold is a disclosed diagnostic, not a
   selection variable). Exact-attainment/tie handling is the pinned D7 rule.
3. **S2 definedness:** the untestability rule above is frozen; an untestable step
   stops the fixed sequence fail-closed (later steps descriptive).
4. All steps run on the §6.2 resampling scheme with its `G_min`/diagnostic
   machinery; fixed sequence ACROSS steps, max-t WITHIN each step.

**Operationalized as a frozen, auditable requirement:**

1. The hierarchy is pinned in the prereg BEFORE any run; the verdict object carries
   `endpoint_id`; the mechanical grader REFUSES to emit a W3 `claim_class` for any
   endpoint id other than W3-P; secondary results appear only in secondary fields.
2. Secondaries run in FIXED SEQUENCE (S1 → S2 → S3), each only after the previous
   passes, only after a full W3-P pass (§6); a failed or untestable step stops the
   sequence.
3. Promotion, reordering, or addition of endpoints after freeze is a framework
   VERSION change with full re-review — never an amendment.
4. Any report surface quoting a secondary or diagnostic without its tier label, or
   as a headline, fails the claims lint (§7).

---

## 4. Guardrail 2 — the coverage floor

`[STIPULATED]` `[PROPOSED-PREREG-ROW-MF0-C5]`

**V1 (binding validity gate on S's claim; dual-aggregation, Revision 3 per
delta-check defect 2):** the W3 claim is **VOID** unless
\(LCB95(cov_{macro}(S)) \ge c_{min}\) AND \(LCB95(cov_{micro}(S)) \ge c_{min}\) —
BOTH aggregations (D3), the same constant, on the full W3 item set at the primary
operating point; the micro conjunct is what makes the §5 selective-risk statement
mathematically licensed (the macro floor alone licenses no such bound) and mirrors
V2's dual-aggregation form — AND asserted coverage \(\ge c_{dom}\) in at least
\(\lfloor |core|/2 \rfloor + 1\) of the rung's frozen core domains (STRICT majority
— Revision 2 per defect 4: the Rev1 ceiling formula permitted exactly half when
\(|core|\) is even; point estimates; an anti-concentration rider, not an inference).

**Proposed values `[STIPULATED — coordinator/maintainer to ratify]`:**

- \(c_{min} = 0.20\) (macro). Reasoning: (i) anti-thin-slice — under component-equal
  weighting, fully answering ONE component of an N-component rung yields macro
  coverage ≈ 1/N (< 0.07 for the R1+ manifests), so neither a sliver nor
  single-component concentration reaches 0.20; (ii) honest-abstention headroom —
  the floor must be reachable by a fail-closed system abstaining widely on
  genuinely hard/uncovered material; measured external kernel coverage is
  approximately zero today (§0 premise, corpus-indexed), so suite coverage comes
  overwhelmingly from the host plus its selective policy, and 0.20 macro sits far
  below typical calibrated answer rates while far above sliver scale; (iii)
  symmetry — the floor binds S's CLAIM only, so it cannot bias the contrast
  (comparators below floor are retained at realized coverage). NOT derived from any
  measurement of these suites — a stipulated constant subject to the item-23
  feasibility check.
- \(c_{dom} = 0.05\) per core domain, strict majority of core domains.
- **Feasibility check (freeze precondition, register item 23):** on the P3-E-CAL
  extension records (§9), the pinned anchors with the item-26 wrapper must clear
  \(c_{min}\) at some dev-feasible operating point; failure RETURNS the floor
  constants to design before ratification — never silently proceeds.

**VOID semantics (confirmed sound; kept):** VOID is not FAIL and cannot manufacture
a PASS anywhere. Below the floor, no W3 claim may be stated in EITHER direction from
that run at that operating point; the rows remain diagnostics;
`w3_status = VOID-COVERAGE-FLOOR`. (#57 prescribed VOID for this guardrail
specifically; the risk-bound gates take FAIL semantics — §5, material call §13-14.)

**The covered-slice rule (both readings of the #57 guardrail, closed fail-closed):**
(a) the binding floor above is on ANSWER RATE — the abstention-gaming channel;
(b) **store-covered-slice claims are prohibited outright under the W3 label** — W3
claims are full-suite only; the covered/uncovered split and the covered-fraction
estimate (always corpus-indexed, never "natural coverage") are mandatory
diagnostics; any future covered-slice claim family must be separately registered
with its OWN pre-registered covered-fraction floor and may never use the W3 label.
This encodes the programme's standing m0b scope-stripping caution structurally.

---

## 5. Guardrail 3 — the unconditional adverse-outcome bound

`[STIPULATED]` `[PROPOSED-PREREG-ROW-MF0-C4]`

**V2 (binding validity gate):** at the primary operating point, on the full W3 item
set (never a covered slice), the cap binds CONJUNCTIVELY on both aggregations
(Revision 2 per defect 4): \(UCB95(udw^{+}_{macro}(S)) \le \beta_{dw}\) AND
\(UCB95(udw^{+}_{micro}(S)) \le \beta_{dw}\) — macro closes component-domination,
micro is the true per-issued-query deployment risk. The bound is ABSOLUTE (not
comparator-relative) and UNCONDITIONAL (all issued items in the denominator;
abstentions AND no-outputs charged per D4), so abstention cannot launder
confident-wrong outputs and crashing cannot imitate abstention. Both conjuncts are
void/fail-only gates and consume no alpha.

**V3 (soundness sub-gate, provenance-bearing arms):**
\(UCB95(asv(S)) \le \beta_{sv}\) (macro and micro, conjunctive). An engine that
stamps wrong answers with provenance is worse than no engine (the parent's
wrong-with-provenance-is-worse-than-refusal discipline).

**Failure semantics (Revision 2 — material call, §13-14):** a V2 or V3 violation is
a substantive negative finding about S at its chosen operating point, not a scope
defect; hiding it as VOID would suppress a negative result. Proposed default:
`w3_status = FAIL-RISK-BOUND` / `FAIL-SOUNDNESS-BOUND` — reportable FAILs with the
same prominence machinery as any FAIL. (#57's VOID prescription was specific to the
coverage floor; extending VOID to the risk bounds is the alternative the maintainer
may choose instead; the difference is whether the outcome reads as "S failed to
control risk" — proposed — or "no claim adjudicable".)

**Proposed values `[STIPULATED — coordinator/maintainer to ratify]`:**

- \(\beta_{dw} = 0.05\) — deliberately REUSED from the programme's standing S2
  dangerous-wrong kill line (5.0% wrong-with-provenance, the nsk1 lineage as
  restated in the parent's premise block) rather than newly invented; deployment
  reading: at 95% confidence, no more than one adverse outcome per twenty issued
  queries. A ratifiable constant, not a claim of optimality.
- \(\beta_{sv} = 0.01\) — the endorsed channel must be materially safer than a bare
  answer.
- **Joint-implication disclosure (CORRECTED Revision 3 per delta-check defect 2 —
  the Rev2 statement was mathematically FALSE under the macro definitions: macro
  sr is a mean of per-component ratios, and mean(d_j) ≤ 0.05 with mean(c_j) ≥ 0.20
  does NOT bound mean(d_j/c_j); counterexample: twenty equal-weight components,
  four at c = 0.75/sr = 0 and sixteen at c = 0.0625/sr = 1 pass both macro gates
  with macro sr = 0.80):** what the gates LICENSE is the MICRO statement only —
  with the V1 micro coverage floor and the V2 micro cap both passed, on point
  rates, \(sr_{micro} = udw_{micro}/cov_{micro} \le udw^{+}_{micro}/cov_{micro}
  \le \beta_{dw}/c_{min} = 25\%\): up to one in four of delivered answers wrong,
  per issued-item accounting, at the exact boundary. **NO macro selective-risk
  bound is implied by any gate** — stated, not hidden; the macro-side guards are
  the S2 selective-risk endpoint, the mandatory per-component coverage/risk
  diagnostic vectors (which expose exactly the counterexample profile), and the
  anti-concentration rider (which limits but does not bound it). Whether a 25%
  micro boundary case may ever wear "CORRECTNESS-ONLY SUCCESS" remains the joint
  constants question (§13-3); mitigations if unacceptable: raise \(c_{min}\),
  lower \(\beta_{dw}\), or add a frozen micro selective-risk cap as a further
  validity gate. Two honesty notes retained: the boundary case must STILL beat
  every roster comparator by \(\delta_{cov}\) under the same caps to pass W3-P;
  and secondaries do not gate the primary label.
- **Direction-aware comparator handling (fail-closed for S, conservative
  otherwise):** S must satisfy V2/V3 or its claim FAILs as above. A COMPARATOR
  whose test bound exceeds the cap is NOT zeroed or excluded: it retains its
  realized coverage in the primary contrast (raising S's bar — the conservative
  direction) and the violation is disclosed. No violation ever weakens S's
  opposition.

**Rare-event statistics:** adverse-outcome and endorsed-wrong counts on challenge
subsets can be small. Intervals follow the framework's single-scheme law: the §6.2
cluster bootstrap wherever the pinned taxonomy has any non-singleton cluster; the
exact one-sided Clopper–Pearson bound ONLY where the taxonomy is provably
singleton-cluster (the spec's named carve-out, inherited verbatim). The sealed-suite
power analysis already sizes for rare dangerous-wrong targets (spec §5.2); the W3
bounds are declared inputs to that sizing at freeze.

---

## 6. Guardrail 4 — family-wise multiplicity control

`[STIPULATED]` `[PROPOSED-PREREG-ROW-MF0-C6]`

**Family definition (pinned at freeze):** the W3 family at rung \(R_k\) =
{ the W3-P contrast against EVERY W3 roster comparator } ∪ { the gatekept
secondary steps S1–S3, each itself a roster-wide max-t sub-family }. The validity
gates V0–V3 are conjunctive PRECONDITIONS, not tested hypotheses: they consume no
alpha because they can only void or fail a claim, never support one (confirmed
sound; kept).

**Method (which correction, over which family):**

1. **Stage 1 — primary:** simultaneous one-sided **max-t bounds across the W3
   comparator roster at family-wise α = 0.05**, on the ONE fixed-weight
   item-cluster resampling scheme of spec §6.2, inheriting VERBATIM its cluster
   taxonomies, `G_min` floor + automatic sub-`G_min` method switch, studentization
   and degenerate-cell diagnostics, the ±0.002 seed-recompute Monte-Carlo bound,
   and the instrument-invalid rule on diagnostic failure. No second resampling
   scheme exists anywhere in W3.
2. **Stage 1 — secondaries:** fixed-sequence gatekeeping S1 → S2 → S3 (order frozen
   in §3), each step a roster-wide max-t sub-family at α = 0.05 with full alpha
   inheritance, entered only on a complete primary pass; a failed or untestable
   step stops the sequence. Fixed sequence across steps + simultaneous bounds
   within steps preserves the family-wise rate without splitting alpha; individual
   per-comparator conclusions come only from the simultaneous bounds (Revision 2
   per defect 6).
3. **Stage 2 — attribution:** on a stage-1 W3 pass, THREAT Rev1 §5.1's two-stage
   gatekeeping runs its attribution family, on the same resampling scheme, with the
   correctness-framing margin THIS design supplies (the object THREAT §4.1/§5.2
   defers): \(\delta_{attr,W3} = \delta_{cov}\) on coverage-contrast attribution
   cells, and the V2/V3 bound form on risk-contrast attribution cells. A stage-1
   pass without a stage-2 pass is GENERIC-TOOL-LABELLED — no kernel attribution.
4. **Cross-family rule (confirmed sound; kept):** W1 and W3 are SEPARATE registered
   claims, each its own family at α = 0.05. **No disjunctive claim surface
   exists**: "a win on either W1 or W3" is not a registrable claim and may not be
   stated as a programme outcome. Registering any disjunctive or composite W1/W3
   claim requires explicit alpha assignment and a framework VERSION change. A
   CONJUNCTION ("both passed, independently") is permitted wording — conservative —
   under §7's labels.
5. **No post-hoc anything:** the FWER procedure, family membership, roster, gates,
   margins, grid point, thresholds, and secondary order are all in the frozen
   prereg; fallback method selection after results is instrument-invalid (inherits
   spec §6.2's rule verbatim).

**Proposed margins `[STIPULATED — coordinator/maintainer to ratify]`:**
\(\delta_{cov} = 0.05\) absolute macro coverage (five points of answer rate at
frozen risk — deliberately larger than the index margin \(\delta_k = 0.02\) because
coverage points are cheaper than index points); \(\delta_{dw} = 0.01\) for W3-S1.
Both subject to the register-item-23 power analysis on the realized comparator
count and CAL covariance before campaign freeze, exactly as the W1 margins are.

---

## 7. Guardrail 5 — the reporting-language rule

`[STIPULATED]` `[PROPOSED-PREREG-ROW-MF0-C7]`

**The rule:** every claim surface — report, verdict object, auto-report, README or
badge, issue post, paper abstract, talk slide — that states a W1 or W3 result MUST
(i) carry the frozen claim-class label, (ii) carry the cross-status line naming the
OTHER family's status at that rung verbatim from the frozen enums, and (iii) never
use the unqualified word "success". Frozen templates:

> **CORRECTNESS-ONLY SUCCESS (W3, rung R_k):** [the §2 licensed sentence, constants
> inlined]. This is NOT an efficiency-frontier (W1) result and licenses no resource
> or size statement. W1 status at this rung: {one of the w1_status enums}.

> **EFFICIENCY-FRONTIER SUCCESS (W1, rung R_k):** [the spec §0 licensed sentence].
> This is NOT a correctness (W3) result and licenses no delivered-wrong or coverage
> statement. W3 status at this rung: {one of the w3_status enums}.

> **DUAL SUCCESS (W1 + W3, rung R_k):** permitted ONLY when both families
> independently passed in the same registered campaign; both licensed sentences
> appear in full; no blended adjective ("better and safer") may replace them.

**Frozen status enums (Revision 2 — completed so the cross-status rule is
fail-closed; every inherited terminal state is renderable):**

- `w1_status ∈ {PASS, FAIL, UNAVAILABLE (§0 collision invariant), BLOCKED
  (§3.5 tier-mapped W1 block), INSTRUMENT-INVALID, NOT-RUN}`
- `w3_status ∈ {PASS, FAIL, FAIL-RISK-BOUND, FAIL-SOUNDNESS-BOUND,
  VOID-COVERAGE-FLOOR, NOT-CLAIMABLE (V0 resource-inadmissible, no dev-feasible
  operating point, or no ratified budget anchor at the rung — R0 today, §2a),
  BLOCKED (blocking-tier W3 comparator repeatability failure, §8.3 — Revision 3),
  UNAVAILABLE-CAL (the §9 W3 calibration extension not GREEN),
  INSTRUMENT-INVALID, NOT-RUN}`

**Enforcement (auditable, not aspirational):** the mechanical grader's verdict
object gains frozen fields `claim_family ∈ {W1, W2, W3}`, `w1_status`, `w3_status`
(enums above), and the W3 numbers verbatim (`cov_macro`, `cov_lcb`, `udw_plus_ucb`
macro and micro, `asv_ucb`, `no_output_rate`, floor/bound constants,
`operating_point_id`, `arm_variant`); report-gen emits the templates from those
fields only; the claims lint (`tools/registry/claims-check.py` extension, register
item 27) FAILS any claim surface that names one family's success without the other
family's status line, or that quotes a secondary/diagnostic as a headline (§3).
Kernel attribution wording additionally requires the stage-2 pass recorded in the
same verdict object.

---

## 8. Co-equality mechanics — how W3 sits BESIDE an intact W1

`[STIPULATED]` `[PROPOSED-PREREG-ROW-MF0-C1]`

1. **W1 is untouched.** Its governing claim, budgets, roster, NI family, scalar
   eligibility, census machinery, statistics, and licensed sentence are exactly the
   spec's; this design amends NO W1 clause. Spec §1.2's "abstentions score
   incorrect" stands for the index, evaluated on S-BENCH rows: a maximally
   abstaining policy tanks W1 while its S-HON sibling may excel on W3 — the two
   families measure the two value theses by construction and cannot be traded
   against each other inside either claim. (Confirmed sound; kept.)
2. **One campaign, two claim surfaces, variant-explicit (Revision 2 per defect 7).**
   Both families are fed from ONE frozen registration containing the two named
   policy variants of each arm (D9): option-scored components share rows (W1 reads
   forced-answer scoring, W3 reads the thresholded flags from the same logged
   option scores); generative components run separate S-BENCH and S-HON passes, W1
   consuming only the former and W3 only the latter. The row schema gains
   `answered_flag` / `no_output_flag` / `correct_flag` / `endorsed_flag` /
   `operating_point_id` / `arm_variant` (register item 24). No re-scoring of W1
   anywhere.
3. **Independent availability — now constructively defined (Revision 2 per
   defect 2).** W3 is defined on the vector-membership item set (D3), so it remains
   AVAILABLE at a rung where the §0 collision invariant makes W1 UNAVAILABLE — a
   SCALAR-collision rung (R1+; R0 is outside W3 claim scope per §2a's rung-scope
   rule: no budget anchor, no W3 claim) — and
   the machinery that needs a selection statistic there is frozen as follows,
   because the inherited frontier tooling selects by dev INDEX, which does not
   exist at a collision rung:
   - **W3 closure statistic** = dev **cov-at-R** (TOTALIZED, Revision 3 per
     delta-check defect 4a): the arm's dev macro coverage at its REGISTERED
     primary operating point — the D7 cap-feasible point where one exists, else
     the arm's pinned most-abstaining fallback threshold with the infeasibility
     flag carried (the statistic is thereby defined for EVERY roster arm; a
     cap-infeasible arm's low fallback coverage prices its infeasibility honestly)
     — on the hash-pinned dev split, D3 weighting. It is computable at every rung
     in W3 claim scope (§2a: R1+) and never references S.
   - **Strongest-by-dev (W3)** = argmax dev cov-at-R over admissible roster members;
     recomputed before prereg-freeze on any rebuild/challenger admission, exactly
     parallel to the \(C^{d}\) recompute rule.
   - **Challenger admission (all W3 CLAIM-SCOPE rungs — Revision 4, reconciling
     the stale "all rungs" wording with §2a):** a blinded, \(B_k\)-admissible
     challenger is admitted if its dev cov-at-R exceeds any roster member's — at
     every rung where a ratified budget anchor exists (R1+, per §2a; at R0 no
     \(B_0\) exists, W3 is claim-incapable, and no \(B_k\)-gated challenger
     admission applies), in ADDITION to the index-based W1 admission where that
     exists (so a selective-prediction-strong challenger cannot be dodged for
     having a mediocre index). Admission produces the full frozen comparator
     record.
   - **Rebuild regret gate:** 0.02 dev cov-at-R regret `[STIPULATED]`, the W3 analogue
     of the frontier's index-regret gate.
   - **Repeatability tier map (collision rungs):** blocking tier = W3
     strongest-by-dev + every member within 0.02 dev cov-at-R of the best
     `[STIPULATED]`; carry tier = remainder — the MF0-R3e rule with the W3 closure
     statistic substituted. At non-collision rungs the W1 tier map governs and the
     W3 statistic only ADDS blocking members, never removes any.
   - **Blocking-tier repeatability disposition (Revision 3 per delta-check
     defect 4b):** the spec's §3.5 comparator-repeatability law is mirrored with
     W3 as the object — a BLOCKING-tier W3 comparator failing its repeatability
     gate (admissibility leg included) **BLOCKS W3 at the rung**, `w3_status =
     BLOCKED` (frozen enum literal, §7), unconditionally; a carry-tier failure
     takes the inherited `NON-REPEATABLE-COMPARATOR` carry (K ≥ 3 scoring-run
     replicates, scoring-run bootstrap stratum, adverse status) — never a silent
     exit, and no failure ever weakens S's opposition. The Rev2 text left this
     disposition W1-only; it is now W3-native.
   - Dev-selection caveat recorded as for \(C^{d}\): winner's curse on the
     selection statistic; unbiased evaluation at test.
   Every W1/W3 availability asymmetry is forced onto the claim surface by the §7
   cross-status line. `[PROPOSED-PREREG-ROW-MF0-C11]`
4. **Independent reporting.** Each run's report carries both families' status
   blocks, always, including FAIL/VOID/NOT-RUN — negative and null W3 results get
   the same prominence machinery as W1's (the templates have no success-only
   branch).
5. **Shared opposition, extended and envelope-bound.** The W3 comparator roster =
   the closed W1 roster \(F(B_k)\) (frontier-built, nomination window, challenger
   gate — inherited) with each member equipped with the register-item-26 pinned
   wrapper as its hon variant, PLUS the matched-RAG completion \(R^{*}\) similarly
   equipped, PLUS any W3-statistic challengers admitted under item 3. Every arm —
   S included (§2a) — sits inside the same \(B_k\) with wrapper/abstention
   machinery counted as arm cost under the same ledgers; the freeze-readiness
   requirement that the strongest neural/RAG selective-prediction baseline receive
   the same evidence, abstention opportunity, tuning budget and resource ledger is
   thereby concrete and two-sided. `[PROPOSED-PREREG-ROW-MF0-C8]`

---

## 9. Inherited machinery (verbatim, no forks)

`[STIPULATED]` `[PROPOSED-PREREG-ROW-MF0-C9]`

- **Proxy-rung asymmetry (spec §1.6), imported with the §2a R0 restriction
  (Revision 4 — the Rev3 "verbatim" import carried R0 directional kills and
  positive R0 W3 margins, comparative constructs §2a prohibits):** at R1+ the
  import is verbatim — R1 W3 kills may terminate at registered scope (subject to
  the same census interlocks), and positive R1 W3 margins are hypotheses
  requiring higher-rung confirmation. At R0, only §2a's ABSOLUTE-form W3 kills
  exist (a pre-registered bound violation, e.g. on udw⁺ — no comparator, no
  envelope, no margin; same census interlocks); R0 directional kills, positive
  R0 W3 margins, and every other comparative R0 W3 construct are prohibited.
  Byte-identical prompts/scorers across rungs applies globally (a harness
  discipline, not a comparative construct).
- **Decontamination (§5.1) and sealed evaluation (§5.2):** W3 endpoints are computed
  on the sealed release; the sealed consistency condition for W3 is the SAME
  studentized one-sided bootstrap-t difference-in-differences construction, applied
  to the W3 primary estimand (the macro coverage contrast), same matched-domain
  common-estimand rule; the sealed power analysis's existing rare dangerous-wrong
  sizing input becomes the V2/V3 bound widths.
- **Statistics plumbing (§6.2):** one resampling scheme, `G_min`, diagnostics,
  MC-error bound, day/session/run hierarchy where a W3 arm has run-unstable cells —
  all inherited unchanged; the prereg fill-list gains the W3 block (operating
  points incl. per-grid thresholds, wrapper ids + hashes, D-block constants,
  UNANS-KOT/1 pins, arm-variant declarations, W3 kill text).
- **P3-E-CAL extension (new records, register items 23/26):** the anchor triple
  (and the non-gating subjects) run WITH the pinned wrapper candidates at a
  threshold sweep to produce the W3-column calibration records — coverage/udw⁺
  dispersion and covariance, per candidate wrapper — that (a) feed the item-23
  feasibility check on \(c_{min}\) and the margin power analysis, (b) feed the
  item-26 wrapper fidelity/selection record, and (c) verify the W3 columns are
  repeatable instrument outputs before any architecture exists. This extension
  gates W3 availability ONLY (`w3_status = UNAVAILABLE-CAL` until GREEN), never
  the existing W1 GREEN criteria — no retroactive tightening of an
  already-specified instrument.
- **THREAT (§5.4 + P3-D-THREAT Rev1):** conjunction structure unchanged; this design
  supplies only the deferred correctness margins (§6 item 3) and endpoint
  definitions; the content-hash pin + conformance attestation regime applies to the
  W3 wiring identically.

---

## 10. New ratification-register items

Continuing the spec's register numbering `[STIPULATED — all values PROPOSED]`:

23. **W3 constants package:** \(\delta_{cov}\), \(\delta_{dw}\), \(\beta_{dw}\),
    \(\beta_{sv}\), \(c_{min}\) (binding on BOTH coverage aggregations, V1 —
    Revision 3), \(c_{dom}\), the S1 grid and the frozen-\(g^{*}\)
    rule (S inside the quantifier; largest-qualifying-threshold selection —
    Revision 3) — each with the derive/cap/adversarial-check object the spec's
    stipulated-constant law demands (a bare constant is not ratifiable), the
    **joint-envelope disclosure ratified as one package** (the §5 boundary
    selective-risk implication stated verbatim in the ratification record), plus
    the CAL-based feasibility/power check with the RETURN-TO-DESIGN rule on
    failure.
24. **Output-classification protocol pins:** per-benchmark abstention format bytes
    (`abstention_format_sha256`), the NO-OUTPUT harness detection rule,
    per-task-class confidence functionals (option-scored AND generative), the dev
    split supply rule for components lacking one (hash-partition pinned before any
    anchor output inspection), per-grid-point threshold rule + tie rule,
    operating-point record schema, arm-variant declarations (D9), and the six new
    per-item row fields.
25. **UNANS-KOT/1 (hardened, Revision 2):** generator semantics, item count, seed
    range, held-out family discipline, W3-only/vector-only status, ONE-component
    macro weight, PLUS: (a) **non-answerability certification** — every gold-abstain
    item passes a mechanical validity check that no admissible answer exists under
    its premise set (generator constraint-check where applicable), with a seeded
    independent cross-vendor audit sample double-adjudicated for answerability
    before freeze; (b) **scorer conformance** on golden items (gold-abstain and
    answerable-twin), hash-pinned; (c) **cluster taxonomy** (generator family ×
    mutation type) and its `G_min` disposition; (d) **positive controls** — the D8
    answerable near-duplicate twins at a pinned fraction, so blanket abstention
    forfeits coverage; (e) audit-failure rule: certification or conformance failure
    RETURNS the generator to design, never trims items post-hoc.
26. **W3 wrapper instrument (rewritten freeze-grade, Revision 2 per defect 5):**
    - a **CLOSED candidate set**, pinned with implementation scripts + hashes at
      ratification — proposed: {max-softmax/max-logprob thresholding (baseline,
      always included); temperature-scaled max-prob with dev-fit temperature;
      self-consistency agreement (k, temperature, seeds pinned); P(true)-style
      self-evaluation probe (prompt bytes pinned)} — with the generative-task
      functionals of D1 pinned per generative benchmark; NO open "strongest
      published method" clause survives;
    - a **frozen selection objective**: per comparator arm, the wrapper and
      threshold are chosen on dev as argmax dev macro cov subject to dev udw⁺ UCB
      ≤ \(\beta_{dw}\), inside the arm's equal-tuning budget; the selected wrapper
      id freezes in the prereg pre-test;
    - an **implementation-fidelity test**: each candidate reproduces pinned golden
      outputs on a hash-pinned fidelity suite before ratification; failure excludes
      that candidate for ALL arms (instrument-level, disclosed);
    - a **wrapper challenger route**: wrapper-method nominations ride the §5.3
      nomination window; admission iff the nominated method improves an incumbent
      arm's dev cov-at-R; admitted methods join the closed set with full pins;
    - the **D7 deterministic selection/tie cascade governs the
      wrapper-and-threshold argmax verbatim** (Revision 3 per delta-check
      defect 5): discrete dev coverage makes argmax ties likely, so no selection
      without the pinned total order is ratifiable;
    - same-evidence / same-abstention-opportunity / equal-tuning-budget /
      same-ledger certificates per arm.
27. **Reporting enforcement:** the §7 templates as frozen strings, the COMPLETE
    status enums (incl. INSTRUMENT-INVALID, BLOCKED, UNAVAILABLE-CAL,
    NOT-CLAIMABLE), the verdict-object schema fields, and the claims-lint rule
    extension.
28. **W3 opposition constants (Revision 2 per defect 2; extended Revision 3):** the
    dev cov-at-R closure statistic definition (TOTAL — D7 point or pinned fallback
    threshold with infeasibility flag), the 0.02 rebuild-regret gate, the 0.02
    blocking-tier distance at collision rungs, the claim-scope-rung W3
    challenger-admission rule (R1+, per §2a — Revision 4), the W3 blocking-tier
    repeatability disposition
    (`BLOCKED`), and the winner's-curse caveat record.

---

## 11. PROPOSED prereg rows (labels only — nothing registered)

- **PROPOSED-PREREG-ROW-MF0-C1:** co-equal family law — W3 stands beside an intact
  W1 as a separate registered claim family; one registration with two named policy
  variants per arm feeds both families (shared rows where policies coincide,
  separate generative passes where they diverge); availability is independent in
  both directions; no W1 clause is amended. `[STIPULATED]`
- **PROPOSED-PREREG-ROW-MF0-C2:** frozen endpoint-hierarchy law — primary =
  coverage-at-frozen-risk (W3-P); fixed-sequence gatekept secondaries S1–S3, each a
  roster-wide max-t sub-family with all selection quantities dev/freeze-determined
  (largest-qualifying-threshold grid rule; \(g^{*}\) quantifies over every W3 arm,
  S included; the D7 total-order tie cascade — Rev3); diagnostics never
  claim-capable; grader-enforced endpoint ids; any change is a framework version
  change. `[STIPULATED]`
- **PROPOSED-PREREG-ROW-MF0-C3:** output-classification law — three terminal
  classes {ANSWER, ABSTENTION, NO-OUTPUT}; only pinned abstention/refusal patterns
  or sub-threshold confidence abstain; malformed/parse-fail/content-bearing-timeout
  = ANSWER; complete non-return = NO-OUTPUT (no coverage credit, adverse risk
  charge); dev-only threshold selection incl. per-grid thresholds; confidence
  functionals pinned for option-scored AND generative tasks. `[STIPULATED]`
- **PROPOSED-PREREG-ROW-MF0-C4:** adverse-outcome law — dangerous-wrong ≡ ANSWER ∧
  incorrect (no hedged-wrong exemption); V2 bounds udw⁺ = delivered-wrong ∪
  NO-OUTPUT at UCB95 ≤ β_dw, conjunctively on macro AND micro aggregations, on the
  full W3 set; V3 = UCB95(asv) ≤ β_sv likewise; V2/V3 violations are reportable
  FAILs (FAIL-RISK-BOUND / FAIL-SOUNDNESS-BOUND); rare-event intervals per the
  single-scheme law + CP carve-out; comparator violations disclosed, never
  weakening S's opposition. `[STIPULATED]`
- **PROPOSED-PREREG-ROW-MF0-C5:** coverage-floor law — V1 = LCB95(cov) ≥ c_min on
  BOTH macro and micro aggregations (Rev3: the micro conjunct licenses the §5
  selective-risk statement) plus the strict-majority per-domain rider
  (⌊|core|/2⌋+1 domains at ≥ c_dom); VOID (not FAIL) semantics reserved to this
  gate; W3 claims full-suite
  only; covered-slice claims prohibited under the W3 label; covered fraction always
  a corpus-indexed diagnostic. `[STIPULATED]`
- **PROPOSED-PREREG-ROW-MF0-C6:** W3 multiplicity law — max-t across the W3 roster
  at FWER α = 0.05 on the §6.2 scheme for the primary AND within each secondary
  step; gates consume no alpha; fixed sequence across steps; per-comparator
  conclusions only from simultaneous bounds; stage-2 attribution with δ_attr,W3 =
  δ_cov; separate families for W1/W3 with NO disjunctive claim surface; post-hoc
  method selection = instrument-invalid. `[STIPULATED]`
- **PROPOSED-PREREG-ROW-MF0-C7:** reporting-language law — frozen claim-class
  labels, mandatory cross-status line rendering the COMPLETE frozen enums (incl.
  INSTRUMENT-INVALID, BLOCKED, UNAVAILABLE-CAL, NOT-CLAIMABLE), no unqualified
  "success", grader fields + claims-lint enforcement. `[STIPULATED]`
- **PROPOSED-PREREG-ROW-MF0-C8:** W3 comparator law — closed W1 roster + matched-RAG
  R* + W3-statistic challengers, each with a pinned closed-set wrapper as its hon
  variant under same-evidence/same-abstention-opportunity/equal-tuning-budget/
  same-ledger certificates; wrapper cost is arm cost for every arm, S included.
  `[STIPULATED]`
- **PROPOSED-PREREG-ROW-MF0-C9:** W3 inheritance law — proxy-rung asymmetry, decon,
  sealed DiD (macro coverage-contrast estimand), single resampling scheme, and
  THREAT conjunction structure inherited verbatim; P3-E-CAL extended with the
  W3-column + wrapper-fidelity calibration records gating W3 availability only
  (UNAVAILABLE-CAL until GREEN). `[STIPULATED]`
- **PROPOSED-PREREG-ROW-MF0-C10:** common-envelope law — every W3 arm, S-HON
  included, is B_k-admissible under the spec's direction-aware admissibility law at
  every rung IN W3 CLAIM SCOPE (the budget anchor exists independently of scalar
  eligibility at R1+; R0 derives no B_0, so W3 is claim-incapable there, with
  absolute-form kills only — Rev3); abstention/wrapper machinery is in-envelope
  arm cost; V0 failure for S = NOT-CLAIMABLE; the unmatched-resource correctness
  variant is not registrable without its own separately-ratified family.
  `[STIPULATED]`
- **PROPOSED-PREREG-ROW-MF0-C11:** W3 opposition-closure law — the dev cov-at-R
  closure statistic (TOTAL: D3 weighting at the D7 point, or the pinned fallback
  threshold with infeasibility flag for cap-infeasible arms — Rev3) defines
  strongest-by-dev, challenger admission (all claim-scope rungs, additive to index
  admission), the 0.02 rebuild-regret gate, the collision-rung blocking-tier map,
  and the BLOCKED repeatability disposition (blocking-tier failure blocks W3 at
  the rung; carry-tier takes NON-REPEATABLE-COMPARATOR — Rev3); never references
  S; winner's-curse caveat recorded. `[STIPULATED]`
- **PROPOSED-PREREG-ROW-MF0-C12:** arm-variant identity law — S-BENCH (forced
  answer; the only variant W1 consumes) and S-HON (registered abstention policy;
  the only variant W3 consumes) are named variants of one packed artifact with
  identical figure-1 bytes; option-scored rows shared, generative passes separate
  with separate ledgers; divergent artifacts = separate registrations.
  `[STIPULATED]`

---

## 12. What this document does NOT do (honest scope)

- It runs nothing, spends nothing, freezes nothing, and registers nothing; it is a
  design input to the spec's next revision and then to the freeze process, both of
  which carry their own review gates.
- It does not make the kernel — or any system — correct, safe, or calibrated, and it
  contains no evidence that any system will pass W3: both programme theses remain
  INCONCLUSIVE-PENDING and the four-condition scoreboard remains 0–0 [MEASURED:
  registry state as carried by feasibility-synthesis-v9 §0/§5 and the parent].
- A future W3 PASS would not by itself attribute anything to kernel semantics: the
  literature's add-capability wins belong to engines and executors generally, and
  only the stage-2 attribution family (matched generic stores above all) can move a
  W3 win from generic-tool-labelled to kernel-attributed [LIT-BACKED:
  p3-phase0-synthesis.md §4(3) and the ten pathway reviews at their inherited
  statuses].
- It does not resolve the framework's OTHER freeze blockers (THREAT ratification +
  hash pin + attestation, P3-E-CAL GREEN, empirical ratifications, the final
  delta-check); resolving Part C removes exactly one named blocker.
- Every constant in §2a–§6 and §10 is a stipulation awaiting ratification; none is
  measured, and none may be quoted as a programme finding.

---

## 13. Maintainer-flagged calls vs routine stipulations

**Material framework calls the maintainer should explicitly ratify** (each changes
what a W3 claim can mean, beyond the #57 ruling's letter). Revision 2 completed the
list per the cross-vendor review; Revision 3 adds call 15 and amends calls 3 and 9:

1. **Primary = coverage-at-frozen-risk** (§3), with the unconditional bound as a
   validity gate rather than the primary. The #57 ruling ratified the family + the
   guardrails; it did not pick the primary among the Part-C candidates.
2. **The delivered-wrong collapse + NO-OUTPUT adverse treatment** (§1 D2/D4): every
   delivered wrong is dangerous, no hedged-wrong class, and a complete non-return
   charges the risk cap while earning no coverage. Stricter than the
   freeze-readiness taxonomy.
3. **The constants AND their joint implication** (β_dw = 0.05, β_sv = 0.01,
   c_min = 0.20 on both coverage aggregations, c_dom = 0.05, δ_cov = 0.05,
   δ_dw = 0.01) — ratified as ONE package including the CORRECTED §5 disclosure
   (Rev3): the gates license only the MICRO statement — micro selective risk ≤
   β_dw/c_min = 25% at the exact boundary, via the added V1 micro coverage floor —
   and NO macro selective-risk bound exists or is claimed (the Rev2 macro reading
   was mathematically false; the S2 endpoint + per-component diagnostics are the
   macro-side guards). Per-constant ratification without the joint envelope is
   insufficient.
4. **No-disjunctive-claim rule + per-family α = 0.05** (§6 item 4) — the
   statistical governance of co-equality.
5. **W3 availability at W1-UNAVAILABLE rungs** (§8.3) — co-equality includes census
   independence, now with concrete collision-rung machinery.
6. **UNANS-KOT/1 as a new mandatory instrument** (§1 D8, item 25) —
   authoring/compute cost, a new generator to govern, and its certification/audit
   regime.
7. **The P3-E-CAL extension** (§9) — new calibration records gating W3 availability
   (not W1 GREEN): incremental instrument work before any W3 claim.
8. **S's resource envelope** (§2a) — matched-\(B_k\) for every arm (proposed
   default) vs an explicitly-ratified unmatched-resource correctness family with a
   redefined roster.
9. **The collision-rung opposition machinery** (§8.3, item 28) — the dev cov-at-R
   closure statistic (totalized for cap-infeasible arms — Rev3) with its
   regret/tier constants and the BLOCKED repeatability disposition; without it,
   "W3 available where W1 is not" is not executable.
10. **The W3 weighting/aggregation estimand** (§1 D3) — component-equal macro as
    the primary estimand (with the dual macro+micro risk cap); the raw-item
    alternative changes what every W3 number means.
11. **Operating-policy identity** (§1 D9, §8.2) — the S-BENCH/S-HON dual-variant
    rule, which policy each family evaluates, and what "one campaign" means;
    includes the extra generative-pass cost.
12. **The comparator-wrapper instrument** (item 26) — the closed candidate set, the
    frozen selection objective, the fidelity test, and the generative-task
    confidence functionals; comparator strength on W3 is set here.
13. **KOT-HON/1 adoption as a claim-capable secondary (W3-S3)** — moved OUT of the
    routine list (Revision 2): KOT-HON/1's own design conditions any adoption into
    a frozen claim surface on maintainer + review-gate approval, so λ = 3 and the
    S3 slot are a material call, not a default.
14. **V2/V3 failure semantics** (§5) — FAIL-RISK-BOUND/FAIL-SOUNDNESS-BOUND
    (proposed: a substantive, reportable negative) vs VOID; #57 prescribed VOID
    only for the coverage floor, so extending or not extending VOID here is a
    separate ratifiable choice.
15. **The R0 disposition** (§2a — Rev3, NEW): default = W3 claim-incapable at R0
    (no ratified budget anchor derives \(B_0\); absolute-form kill criteria only,
    under the §1.6 census interlocks) vs ratifying an R0 budget anchor (a spec
    register-item-21 extension) to enable R0 W3 claims. The scoping is the
    proposed default; the anchor is the alternative.

**Routine stipulations** (flag only if the ratifier disagrees): the W3 name (§0;
W2 is taken by the shrink objective), the S1 grid values {0.25, 0.50, 0.75},
template wording in §7, register-item numbering.

---

## 14. Integration path

1. This Revision 3 rides one more delta-check (coordinator-run) and is revised on
   findings; the confirmed elements of BOTH prior reviews are not to be disturbed
   by that check's application.
2. The spec's next revision (Rev6) replaces the "Part C — DEFERRED pending #57"
   placeholder with this content by reference or inlining, updates the banner
   (the #57 blocker: RESOLVED by maintainer ruling; Part C: RESOLVED by this
   design), appends rows MF0-C1…C12 to the PROPOSED-row series, and appends
   register items 23–28; Rev6 then takes its own delta-check.
3. THREAT's correctness-framing hooks (§4.1, §5.2) bind to δ_attr,W3 = δ_cov at
   THREAT ratification; the joint-ratification and content-hash-pin regime is
   unchanged.
4. Freeze remains blocked by the remaining external gates regardless of this
   document (spec banner list); nothing accelerates past them.

---

## Revision 2 — cross-vendor defects applied

**[STIPULATED — revision record. The cross-vendor review returned NEW-DEFECT on
Rev1; its confirmed-sound elements (primary choice, alpha-free gates, VOID-no-PASS,
delivered-wrong collapse modulo defect 3, beside-not-conjoined structure) are kept
in substance. All seven load-bearing defects + four additional items applied;
disposition below.]**

1. **S not bound to a resource envelope — ADOPTED (matched option).** New §2a V0:
   every W3 arm, S-HON included, is \(B_k\)-admissible under the spec's
   direction-aware law at every rung (the budget anchor exists independently of the
   scalar-collision invariant); wrapper/abstention machinery is in-envelope arm
   cost for every arm; V0 failure = NOT-CLAIMABLE. The unmatched-resource
   alternative is surfaced as material call §13-8 with the matched default
   recommended. Rows MF0-C8/C10; the §2 licensed sentence now names S's own fit.
2. **Collision-rung roster not constructible — ADOPTED.** §8.3 freezes a
   W3-specific closure statistic — dev cov-at-R (D3 weighting, D7 operating point,
   hash-pinned dev split) — defining strongest-by-dev, challenger admission (all
   rungs, additive to index admission), a 0.02 rebuild-regret gate, and the
   collision-rung blocking-tier map; register item 28; row MF0-C11; material call
   §13-9.
3. **Missing output earned coverage — ADOPTED.** D1 gains the third terminal class
   NO-OUTPUT (complete non-return): excluded from the coverage numerator, retained
   in every denominator, charged to the V2 cap via the redefined bounded quantity
   udw⁺ = delivered-wrong ∪ NO-OUTPUT (D4); the udw = cov·sr identity is replaced
   by udw⁺ = cov·sr + P(NO-OUTPUT), disclosed; arm-missingness vs
   instrument-missingness separation restated. S3 scores NO-OUTPUT as −λ.
4. **Majority off-by-one + unfrozen weighting — ADOPTED.** V1 rider now
   \(\lfloor |core|/2 \rfloor + 1\) (strict majority). D3 FREEZES the estimand:
   component-equal macro for every W3 family statistic (UNANS carries one component
   weight regardless of item count), micro versions mandatory diagnostics, and the
   V2 cap binding conjunctively on macro AND micro; the c_min reasoning is restated
   in macro terms (single-component concentration yields ≈ 1/N < 0.07). Material
   call §13-10.
5. **Wrapper not freeze-grade — ADOPTED.** Register item 26 rewritten: CLOSED
   candidate set with pinned scripts/hashes (no "strongest published" open clause),
   frozen per-arm selection objective (dev argmax cov s.t. udw⁺ cap, inside equal
   tuning budget), implementation-fidelity test against golden outputs,
   wrapper-challenger route through the nomination window; D1 pins generative-task
   confidence functionals (span logprob, self-consistency-k, P(true) probe) so D7
   thresholds and risk–coverage curves exist for generative components.
6. **Secondaries statistically incomplete — ADOPTED.** §3: each secondary step is a
   roster-wide max-t sub-family passing only on the min over comparators;
   per-comparator conclusions only from simultaneous bounds; S1's grid point
   \(g^{*}\) and every arm's per-grid threshold are dev/freeze-determined (D7
   pinned tie rule) — no test-data-dependent selection exists, so no
   selection-aware correction is owed and the estimand is stated; S2 carries a
   frozen untestability rule (any arm's realized macro cov < 0.05 stops the
   sequence). Fixed-sequence-across / max-t-within stated in §6.
7. **Same-rows vs KOT-HON dual-variant — ADOPTED.** D9 + §8.2: named policy
   variants S-BENCH (W1's only input; forced answer, per KOT-HON/1 §4.2's
   non-penalised variant) and S-HON (W3's only input) of one packed artifact;
   option-scored rows shared by construction, generative components run as separate
   preregistered passes with separate ledgers; "one campaign" redefined as one
   registration containing both variants; row MF0-C12; material call §13-11.
8. **§13 completed — ADOPTED.** Added material calls 8–14: envelope, collision-rung
   machinery, weighting estimand, policy identity, wrapper instrument, KOT-HON
   adoption (moved from routine — its own design requires maintainer + review-gate
   approval), and V2/V3 FAIL-vs-VOID semantics (#57 prescribed VOID only for the
   coverage floor; proposed default here: FAIL, so a risk-bound violation reads as
   a substantive negative, per the negative-prominence discipline).
9. **Joint constants implication — ADOPTED.** §5 states in-doc that the boundary
   case c_min = 0.20, β_dw = 0.05 admits selective risk up to 25% among delivered
   answers, with mitigations; item 23 requires the joint-envelope disclosure to be
   ratified as one package (material call §13-3 updated).
10. **UNANS-KOT/1 hardening — ADOPTED.** Item 25 gains non-answerability
    certification with an independent cross-vendor audit sample, scorer conformance
    on golden items, cluster taxonomy + `G_min` disposition, a pinned
    positive-control (answerable-twin) fraction, and a return-to-design rule on
    certification failure (never post-hoc item trimming).
11. **Reporting enums completed — ADOPTED.** §7 freezes full enums: w1_status gains
    BLOCKED and INSTRUMENT-INVALID; w3_status gains FAIL-RISK-BOUND,
    FAIL-SOUNDNESS-BOUND, NOT-CLAIMABLE, UNAVAILABLE-CAL, and INSTRUMENT-INVALID —
    the cross-status rule is now renderable for every inherited terminal state,
    fail-closed.

---

## Revision 3 — Rev2-delta-check repairs applied

**[STIPULATED — revision record. The Rev2 delta-check returned NEW-DEFECT
(converging): it CONFIRMED the Rev2 fixes (NO-OUTPUT + per-component identity,
strict majority, component-equal weighting + conjunctive macro/micro caps — save
the false implication below, dev-only secondary selection + roster-wide max-t,
S-BENCH/S-HON + separate generative passes, UNANS hardening, enum literals, the
completed §13) and found five narrow defects. All five applied; nothing the
delta-check confirmed is disturbed.]**

1. **S1 threshold direction reversed — ADOPTED.** D7(ii): the per-grid threshold
   is now the LARGEST candidate threshold whose dev macro coverage ≥ g (under
   D1's answer-at-confidence-≥-t convention coverage is non-increasing in t; the
   Rev2 "smallest" rule selected maximum coverage and collapsed every grid point
   onto one threshold, invalidating the matched-coverage comparison). \(g^{*}\)'s
   quantifier now runs over EVERY W3 arm, **S included**, so S1 is never
   scheduled at a coverage S cannot reach. §3's completeness block and rows
   MF0-C2, register item 23 restate both.
2. **False 25% macro disclosure — ADOPTED (corrected + licensed).** The Rev2
   statement was mathematically false: macro sr is a mean of per-component ratios
   and is NOT bounded by the macro caps (counterexample: twenty equal-weight
   components, four at c = 0.75/sr = 0, sixteen at c = 0.0625/sr = 1 → macro cov
   0.20, macro adverse 0.05, macro sr 0.80). Fix in two parts: V1 gains a MICRO
   coverage-floor conjunct (same \(c_{min}\), dual-aggregation, mirroring V2),
   and §5 now states only the LICENSED implication — micro sr ≤ β_dw/c_min = 25%
   at the boundary — while explicitly stating that NO macro selective-risk bound
   follows from any gate, with the S2 endpoint and per-component diagnostics
   named as the macro-side guards. §13-3 amended: the licensed-statement choice
   and the added micro floor ride the constants-package material call.
3. **V0 at R0 had no budget anchor — ADOPTED (scoping default + NEW material
   call).** §2a rung scope: V0 (hence any W3 claim) is executable exactly where a
   ratified measured budget anchor exists (R1–R3 today); at R0, W3 is
   CLAIM-INCAPABLE (`NOT-CLAIMABLE`, matching W1's R0 vector-first posture), with
   ABSOLUTE-form W3 kill criteria still registrable under the §1.6 interlocks and
   comparative registrations prohibited. "W3 available where W1 is UNAVAILABLE"
   is scoped to scalar-collision rungs (R1+). The alternative — ratify an R0
   budget anchor via a spec register-item-21 extension — is NEW material call
   §13-15.
4. **Collision-closure definedness seams — ADOPTED (both).** (a) dev cov-at-R is
   TOTALIZED: the arm's dev macro coverage at its REGISTERED primary point — the
   D7 cap-feasible point, else the pinned most-abstaining fallback threshold with
   the infeasibility flag (defined for every roster arm; low fallback coverage
   prices infeasibility honestly). (b) The W3 blocking-tier repeatability
   disposition now exists natively: blocking-tier comparator repeatability
   failure BLOCKS W3 at the rung (`w3_status = BLOCKED`, new frozen enum
   literal); carry-tier takes the inherited NON-REPEATABLE-COMPARATOR carry. §7
   enums, register item 28, row MF0-C11 updated.
5. **Wrapper argmax tie rule — ADOPTED.** D7 now pins ONE deterministic
   selection/tie cascade — objective; then lower dev macro udw⁺; then lower dev
   micro udw⁺; then the ratification-ordered candidate-list position; then the
   larger (more conservative) threshold; then ascending wrapper-script-hash byte
   order — a total order governing every dev argmax (primary point, grid
   thresholds, wrapper selection); register item 26 binds to it verbatim.
   Discrete dev coverage made ties likely, so a bare argmax was operator
   discretion in disguise.

---

## Revision 4 — R0 consistency cleanup

**[STIPULATED — revision record. The Rev3 delta-check CLOSED four of five fixes
(S1 direction; licensed micro-25% statement; totalized cov-at-R + BLOCKED
disposition; deterministic tie cascade — none touched here) and found fix 3
incomplete: two sections still carried stale R0 language contradicting §2a's
rung-scope rule. Both repaired; nothing else changed.]**

1. **§8.3 challenger admission** — was "at ALL rungs" via \(B_k\)-admissibility,
   which is undefined at R0 (no \(B_0\)). Now scoped to the W3 claim-scope rungs
   (R1+, per §2a), with the R0 disposition stated inline (W3 claim-incapable; no
   \(B_k\)-gated challenger admission applies there). The same stale "all-rung"
   literal in register item 28's rule name is corrected to "claim-scope-rung" —
   the same defect's residue, no new content.
2. **§9 proxy-rung import** — was "verbatim" including R0 directional kills and
   positive R0 W3 margins, comparative constructs §2a prohibits. Now: verbatim at
   R1+ only; at R0, only §2a's absolute-form bound-violation kills exist (no
   comparator, envelope, or margin; same census interlocks); the byte-identical
   prompts/scorers rule stays global as a harness discipline, not a comparative
   construct.

---

## Self-check (mandatory, performed last)

1. **Governance tags:** every load-bearing choice carries exactly one of
   [MEASURED]/[LIT-BACKED]/[STIPULATED]; every designer parameter (δ_cov, δ_dw,
   β_dw, β_sv, c_min, c_dom, λ, grid, g* rule, regret/tier constants, name) is
   [STIPULATED], none presented as measured; [EXTRAPOLATION] is used as a premise
   nowhere. Checked. ✅
2. **No minted ids:** no `ASM-` followed by digits appears anywhere in this file;
   prereg rows use the `PROPOSED-PREREG-ROW-MF0-C*` label convention only, marked
   "labels only — nothing registered". Checked over the final text. ✅
3. **No account/handle strings:** participants appear as maintainer / coordinator /
   Fable / architecture-advisor role / cross-vendor reviewer only; no emails, no
   handles. Checked. ✅
4. **Run-vs-design separation:** this document designs and documents only — no
   experiment, spend, registry write, freeze, amendment, git/bd/kb operation, or
   grading is performed; §12 states the honest scope, kept in substance from Rev1
   per the review's instruction. ✅
5. **The five #57 guardrails each operationalized as a frozen auditable
   requirement:** (1) hierarchy → §3 (grader-enforced endpoint ids, dev-frozen
   secondary machinery incl. the corrected largest-qualifying-threshold rule and
   tie cascade, version-change rule); (2) coverage floor → §4 (dual macro+micro
   LCB floor + strict-majority rider + VOID semantics + covered-slice
   prohibition); (3) unconditional bound → §5 (udw⁺ UCB cap, macro+micro
   conjunctive, full-set, absolute, direction-aware, FAIL semantics proposed,
   licensed-only selective-risk statement); (4) multiplicity → §6 (max-t roster
   family + per-step max-t sub-families, fixed sequence, stage-2,
   no-disjunction); (5) reporting language → §7 (frozen templates, complete enums
   incl. w3 BLOCKED, cross-status line, lint). ✅
6. **All review findings dispositioned:** the seven Rev1-review defects in the
   Revision-2 log and the five Rev2-delta-check defects in the Revision-3 log,
   each with its fix's location; the additional items likewise. Nothing either
   review confirmed was redesigned: the primary choice, alpha-free gates,
   VOID-no-PASS, the (repaired) delivered-wrong collapse, the
   beside-not-conjoined structure, and every delta-check-confirmed Rev2 fix
   stand. ✅
7. **Co-equal, not conjoined:** §8 keeps W1 verbatim-intact on S-BENCH rows, gives
   each family its own claim surface, licensed sentence, availability, and
   opposition machinery, and prohibits blended claims; W3 is nowhere a condition on
   W1 or vice versa. ✅
8. **Measured claims restated inside scope:** the coverage numbers cited in §0/§4
   carry their corpus/rung indices and are used only for floor-reachability
   reasoning; no measurement is quoted outside its envelope; no conclusion exceeds
   its backing; both theses stated INCONCLUSIVE-PENDING, scoreboard 0–0. ✅
9. **Maintainer calls surfaced and complete:** §13 lists fifteen material calls
   (seven added by Revision 2; the R0-anchor call added and calls 3/9 amended by
   Revision 3) and a shrunken routine list; KOT-HON adoption is no longer
   routine. ✅
