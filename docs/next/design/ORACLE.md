# P3-D-ORACLE — the oracle-to-NL error-decomposition protocol (KOT-DECOMP/1)

> **Status: Phase-1 DESIGN, revision 1 — REVISED per the independent GPT-5.6 review
> (`poc/gpt56-review/rev-dORACLE-20260711/last-message.json`), all named corrections
> applied; §14 maps each change to the review point it answers. Nothing here is
> frozen, pre-registered, or run. This revision REGISTERS its stipulations as
> ASM-0820..ASM-0826 in `registry/assumptions.jsonl` (append-only block 0820–0849);
> the one governance item the design cannot grant itself — the `boundary-diagnostic`
> FULL-REAL exemption — is registered inside ASM-0824 **as a proposal requiring
> explicit coordinator/maintainer ratification**, with a fail-closed interim rule
> (§9.2).**
> Author: Fable, chief-architect role, 2026-07-11 (revision 1 same day).
> Bead: `kernel-of-truth-s55r.14` (P3-D-ORACLE). Parent epic: `kernel-of-truth-s55r`.
> Blocked-by (satisfied): P3-LR-PARSE (`docs/next/lit/PARSE.md`, 2026-07-11).
> Deliverable named by programme rev-2 §5: *"The oracle-to-NL error decomposition
> protocol: attributing G2→G3 loss across parse / retrieval-addressing / execution /
> generation, per experiment."*
> Inputs read at source: `docs/next/programme-3-neurosymbolic-architecture.md` (rev 2);
> `docs/next/feasibility-synthesis.md`; `docs/next/lit/PARSE.md`;
> `registry/verdicts/{l3a-parse,a5-nl,l3a,a5,f2b-replicate}.json` (as restated by the
> two docs above + direct structural inspection of l3a-parse); the external review
> named above, read in full.
> Epistemic discipline: every load-bearing line carries `[MEASURED|STIPULATED|
> EXTRAPOLATION: ref]` on the same logical line; a design CHOICE is STIPULATED and
> cites its registered ASM-id; forward expectations are EXTRAPOLATION and never
> premises.

---

## 0. One-paragraph summary

Every Programme-3 architecture family must pass through gate **G2** (does the
mechanism help at all, on oracle inputs?) and gate **G3** (how much of that survives
real natural-language input?) before any frontier attempt [STIPULATED:
ASM-0817, restated]. The measured history says the G2→G3 crossing is where this
programme dies or lives: both measured NL crossings FAILED (l3a-parse 47.6%
retention, a5-nl 41.6% + the S2 dangerous-wrong kill) while the engine beneath them
was exact (600/600, 855/855) [MEASURED: registry/verdicts/{l3a-parse,a5-nl,l3a,a5}.json,
restated within their envelopes per feasibility-synthesis §1]. This document
specifies **KOT-DECOMP/1**: a per-family, per-vertical protocol that runs each
architecture — **and its pre-registered no-mechanism control, in mandatory pairs** —
under a ladder of *oracle-splice configurations*, from all-real to all-oracle, one
stage boundary at a time, plus per-item stage tracing, so that any G2→G3 drop in the
**mechanism effect γ(c) = M(S,c) − M(C,c)** — the quantity the K-P3v2(5) kill
actually consumes — is **attributed to a named stage** (NL-parse and its four
sub-stages / retrieval-addressing / graph-construction / graph-encoding-delivery /
execution / rendering / an explicitly *unattributed* terminal residual) with paired
confidence intervals, per-stage risk-coverage reporting, and a mechanical S2
(dangerous-wrong) attribution rule — instead of remaining an ambiguous end-to-end
delta [STIPULATED: ASM-0821]. The protocol is a **diagnostic instrument**: every
configuration containing ANY oracled stage is `oracle-diagnostic` under ASM-0814 and
licenses NO W1 claim and no real-input usefulness claim of any kind [STIPULATED:
ASM-0814, applied]. The complete protocol is a design EXTRAPOLATION assembled from
field-attested ingredients (gold-parse arms, stage counters, perturbation-typed
attribution, ambiguity pre-tagging) — it is therefore validated on a **known-answer
shakedown** (P3-E-ORACLE-0, §8) whose decisive component is a **synthetic factorial
fault-injection pipeline with fully known ground truth** (the legacy-vertical bars
alone are near-true-by-construction and validate plumbing only) [EXTRAPOLATION →
tested: docs/next/lit/PARSE.md §8 P3-D-ORACLE scope, adopted; KA-6 §8 is the test].

---

## 1. Where this protocol sits (and what it must serve)

1. **The G3 gate instrument.** Programme rev-2 §4 defines G3 as "how much of the G2
   effect survives realistic NL mapping", with this design named as the instrument
   that "attributes the G2→G3 loss (parse vs retrieval vs execution vs generation)"
   [STIPULATED: ASM-0817, adopted as this document's requirement].
2. **The K-P3v2(5) kill feed.** Programme §7.1 kills the competitiveness programme if
   "every family's G2 gain fails to survive G3 at the pre-registered retention
   margin" — this protocol defines the survival quantity σ (§7.2) mechanically **on
   the mechanism effect γ, not on raw system performance**, so that kill condition
   is computable, not narrative [STIPULATED: ASM-0818 served; estimand per
   ASM-0821/ASM-0824].
3. **The four-stage H-GNN decomposition.** Programme §3.2 mandates "retrieval → graph
   construction → graph encoding → LM use, separately instrumented"; KOT-DECOMP/1 is
   that instrumentation, generalised to all families [STIPULATED: ASM-0815/0805 scope,
   served].
4. **The NL-boundary wall, respected structurally.** Every natural-input
   store-addressed leg is NLB-gated or oracle-labelled [STIPULATED: ASM-0814].
   KOT-DECOMP/1 does not weaken that wall: §9 states exactly which runs are
   permitted now, which cells are populated only by replaying frozen measured
   artifacts, and which require the coordinator-ratified amendment proposed in
   ASM-0824 — the design grants itself nothing [STIPULATED: ASM-0824].
5. **KOT-FAIR/2 slot — supplement, never substitute.** Decomposition reports are a
   mandatory co-publication of every G4 attempt (the attribution annex), but
   KOT-DECOMP/1 **supplements** KOT-FAIR/2 and does NOT satisfy or replace its
   factorial content-type × retrieval-architecture × executor controls or the
   matched generic-RAG comparator (programme §2.2–§2.3) — those remain separately
   mandatory for any W1 claim [STIPULATED: ASM-0824; ASM-0812 restated].

What it must NOT do: manufacture a W1-relevant number from an oracle leg (the
anti-l3a/a5 rule — the parser is part of the product) [STIPULATED: ASM-0808(NL-input
integrity), restated]; and never let a single "gold-parse arm" stand in for stage
attribution — correlated upstream errors make one splice point uninterpretable
[STIPULATED: ASM-0821; adopted verbatim from docs/next/lit/PARSE.md §8 P3-D-ORACLE:
"a single gold-parse arm cannot localize correlated errors adequately"].

---

## 2. The measured anchor: what already exists and why it is not enough

What exists (the protocol's inheritance, all already field-shaped):

- **A G2 anchor per vertical.** The l3a/a5 verdicts ARE the gold-parse arm: engine
  covered-exactness 600/600 and 855/855 under gold formal inputs, µs cost
  [MEASURED: registry/verdicts/{l3a,a5}.json, audit CONFIRMED, instrument-only scope].
- **Per-stage failure counters.** l3a-parse already logs a stage breakdown
  (frame-miss 228 / mapper-abstain 48 / gazetteer-miss 40 / frame-ambiguous 41) as a
  secondary endpoint (`/analysis/parse_stage_breakdown`) [MEASURED:
  registry/verdicts/l3a-parse.json endpoint sec-stage-breakdown].
- **A measured dangerous-class mechanism.** a5-nl's S2 kill traced to a deterministic
  ROLE_DIR direction-table defect — a *sub-stage* of parsing (role/direction
  binding), not "parsing" generically [MEASURED: registry/assessments/a5-nl.json, as
  restated in PARSE.md §1].
- **A measured delivery-vs-use separation.** nsk1 showed content can be DELIVERED at
  echo grade while INTEGRATION into behaviour fails (R− rescue 0/8) — so
  encode-delivery and LM-use must be separately measurable [MEASURED:
  registry/assessments/nsk1-{bprime2,g2d}.json, exploratory/DRAFT status, restated
  per feasibility-synthesis §1].

Why that is not enough, per the lit-review this design is blocked by [STIPULATED:
ASM-0821, adopting PARSE.md §8]:

1. Observational counters label the *first visible* failure, not the *causally
   responsible* stage: a parse that is "close enough" by the artifact metric can
   still poison retrieval addressing downstream; counters alone cannot see that.
2. One gold-parse splice point cannot separate parse loss from retrieval loss from
   rendering loss when several stages cross the NL boundary at once (dense retrieval
   over NL queries, NL-conditioned rendering).
3. Abstentions must be creditable: without pre-scoring ambiguity/answerability tags,
   a correct abstention on an ambiguous item is indistinguishable from a stage
   failure (should-abstain detection is itself measured-hard: TriageSQL ~60% F1)
   [STIPULATED: ASM-0822, adopting PARSE.md §4/§5d].
4. Scalars hide the operating point: each stage must report its risk-coverage curve,
   not one number [STIPULATED: ASM-0826, adopting PARSE.md §8 verbatim].

And one defect the external review added, now load-bearing for this design
[STIPULATED: ASM-0821]: an end-to-end delta on the SYSTEM alone cannot feed the
K-P3v2(5) kill — the gate consumes the survival of the *mechanism effect*
γ(c) = M(S,c) − M(C,c), and a σ decline is ambiguous between "S degraded" and
"C improved" unless the control C crosses every splice with S. §4/§7.2 make the
control ladder mandatory.

---

## 3. The canonical stage taxonomy and per-family instantiation

### 3.1 Canonical stages (the superset; every family instantiates a subset, in order)

[STIPULATED: ASM-0820 — the taxonomy is a design choice; stage names are
deliberately NOT "S1/S2" to avoid collision with the S1/S2 kill-criteria namespace.]

| Stage id | Name | Input → output artifact | Oracle artifact (§5) | Stage-artifact metric (§7.4) |
|---|---|---|---|---|
| **PARSE** | NL → formal query/claim | NL string → typed formal object (kot-query/1 or family DSL) | gold logical form | whole-frame exactness (never slot-F1 alone) |
| — PARSE.a | intent/frame selection | NL → frame/family id | gold frame id | frame accuracy |
| — PARSE.b | entity/schema linking | NL + frame → bound entities/URNs | gold entity bindings | binding exactness |
| — PARSE.c | role/direction binding | frame + entities → directed roles | gold direction bits | both-orientation accuracy, per directional frame |
| — PARSE.d | serialization | bound frame → DSL string/AST | gold serialization | AST equality |
| **RETRIEVE** | store addressing | formal query (or NL, if the arm retrieves from NL) → record/rule/node id set | gold item→record map | set P/R@k vs gold; address exactness |
| **CONSTRUCT** | graph construction | record/node set → typed subgraph | gold subgraph | graph F1 (nodes, edges, labels) |
| **ENCODE** | encoding + delivery | subgraph/records → model-consumable signal (GNN embedding, soft tokens, KV pairs, continuation-set mask) | gold-input-encoding (upstream-oracle) + delivery probe | delivery probe keyacc (nsk1 instrument shape) |
| **EXECUTE** | deterministic engine | formal query + store → checked result + provenance | gold engine result | exactness (engine is exact where covered — expected ≈ oracle) |
| **RENDER** | surface generation from checked result | checked result → NL answer | canonical surface form (verbatim record answer / pinned template) | result-preservation match (the g2d corruption check) |
| **USE** | terminal LM integration (not spliceable) | all delivered signal → behaviour | none — bounded above by the *unattributed* terminal residual L_term (§4.4) | L_term, an upper bound only — never an attribution |

Notes binding the taxonomy:

- PARSE sub-stages a–d are mandatory wherever a parser exists — this granularity is
  what makes the measured a5-nl mechanism (a PARSE.c defect) expressible
  [STIPULATED: ASM-0820, adopting PARSE.md §8 "intent/frame selection,
  role/direction binding, entity linking, DSL serialization, execution, rendering"
  verbatim].
- ENCODE is **probe-instrumented, splice-limited**: a "gold encoding" of a learned
  encoder is not well-defined, so ENCODE's upstream splice is "encoder applied to the
  gold-constructed input", and the encode-vs-use separation comes from the delivery
  probe (can the signal be read back?) vs the endpoint (does behaviour improve?) —
  the nsk1 lesson turned into instrumentation [STIPULATED: ASM-0820; motivated by
  MEASURED nsk1 delivery/integration split].
- EXECUTE is expected to contribute ≈0 loss on the covered slice (the engine is
  exact and fail-closed there [MEASURED: l3a/a5]); it stays in the ladder anyway
  because integration bugs at the engine seam are exactly what a splice catches
  cheaply [STIPULATED: ASM-0820, ~zero marginal cost — the engine is µs-class].

### 3.2 Per-family instantiation (the boundary set B(F))

For each family F, define **B(F) = the ordered set of stages whose input regime
differs between the G2 (oracle-input) and G3 (natural-input) runs**. The
decomposition runs over B(F); stages outside B(F) are identical in both regimes and
are attributed zero by construction. The family prereg must order B(F) so that the
stages oracled in the registered G2 configuration form a PREFIX of the pipeline
order, ending at index j_anchor (§4.2) [STIPULATED: ASM-0820/ASM-0821].

| Family | Instantiated pipeline | B(F) (typical) | j_anchor set | Family-specific notes |
|---|---|---|---|---|
| **H-VL** (verifier loop) | PARSE → RETRIEVE → EXECUTE → USE(retry/accept policy) → RENDER | PARSE(a–d), RETRIEVE | PARSE(a–d) | the retry policy is part of USE; f2b's record→item alignment is the RETRIEVE gold map |
| **H-PS** (NL→program synthesis) | PARSE(a–d) → EXECUTE → RENDER | PARSE(a–d), RENDER | PARSE(a–d) — RENDER is BEYOND-ANCHOR (§4.2): oracling it exceeds the registered G2 configuration | RENDER is first-class here: generation-from-checked-result is nsk1-g2d-cautioned [MEASURED: g2d net-harmful text append, exploratory] |
| **H-GNN-ST/KV/LF** | PARSE(query understanding) → RETRIEVE → CONSTRUCT → ENCODE → USE | PARSE, RETRIEVE, CONSTRUCT (+ENCODE probe) | per family prereg (oracle-subgraph cell) | this IS the programme §3.2 four-stage decomposition; oracle-subgraph vs NL-extracted-subgraph are the two named control cells |
| **H-RULE-CD** | PARSE(span/coverage detection) → RETRIEVE(rule selection) → EXECUTE(continuation-set derivation) → ENCODE(mask delivery) → USE | PARSE, RETRIEVE | PARSE | CD is transport: the engine derives, masking delivers [STIPULATED: ASM-0815, restated] |
| **H-RULE-KV** | RETRIEVE(rule/record selection from input) → ENCODE(KV construction) → USE | RETRIEVE (+PARSE if NL-keyed) | RETRIEVE | provenance claims need the splice/ablation evidence, never attention maps [STIPULATED: ASM-0815] |
| **H-DD** (store reinjection legs) | RETRIEVE(store addressing) → ENCODE(reinjection) → USE | RETRIEVE | RETRIEVE | the oracle-addressed reinjection leg of P3-E-DD-0 step (4) is exactly a RETRIEVE-oracle splice [STIPULATED: ASM-0816 alignment] |

Each family's Phase-2 prereg MUST contain a completed instantiation row: its stage
map, its B(F) with j_anchor, its control arm C's stage map (§4.1), its oracle
corpora (hash-pinned), and its endpoint — §10 provides the prereg checklist block
[STIPULATED: ASM-0824].

---

## 4. The splice-ladder protocol (the interventional core)

### 4.1 Configurations — mandatory on BOTH arms

A configuration c is an assignment `regime(stage) ∈ {real, oracle}` for every stage
in B(F). **Every mandatory configuration runs on BOTH arms: the mechanism system S
and the family's pre-registered no-mechanism control C** (the family's factorial
control cell, programme §2.2) — the control ladder is NOT optional, because the
gate-fed quantity is the mechanism effect γ(c) = M(S,c) − M(C,c) (§7.2)
[STIPULATED: ASM-0821 — the review's ranked concern 1, adopted]. Where C does not
instantiate a stage in B(F), oracling that stage is the identity on C: M(C,·) is
constant across that splice, computed once per equivalence class and disclosed as
degenerate — the γ decomposition then reduces to the S decomposition at exactly
those rungs, visibly rather than silently [STIPULATED: ASM-0821].

The MANDATORY set per family × vertical [STIPULATED: ASM-0821]:

1. **FULL-REAL** — every stage real. The G3 reading's configuration; execution
   governance per §9.2 (NLB clearance, frozen-artifact replay, or the ratified
   exemption — never self-granted).
2. **PREFIX ladder** — for j = 1…K (K = |B(F)|, pipeline order): stages 1…j oracle,
   the rest real. PREFIX(K) = FULL-ORACLE. This yields the telescoped loss chain,
   segmented at the G2 anchor (§4.2).
3. **REPAIR splices** — for each j: stage j alone oracle, all others real. This
   answers "how much does fixing stage j alone buy?" — the deployment-relevant
   question (which stage should P3-D-NLB-class investment target first).
4. **G2-ANCHOR** — the family's registered G2 configuration = PREFIX(j_anchor)
   (oracle through the anchor prefix, everything downstream real). For H-VL this is
   PREFIX(PARSE.d) = FULL-ORACLE; for H-PS it is PREFIX(PARSE.d) with RENDER real —
   **not** FULL-ORACLE, which additionally oracles RENDER and therefore sits ABOVE
   the registered G2 anchor (§4.2). It is named separately because it must
   reproduce the family's registered G2 result (instrument gate IG-1, §8).

Config count: (K+1 prefix + K repair + full-real) ≤ 2K+2 configurations × 2 arms ≤
4K+4 ≤ 28 arm-runs at K ≤ 6, before degenerate-C de-duplication — still small
enough that the full ladder fits tiny-scale budgets (§10) [STIPULATED: ASM-0821
sizing]. OPTIONAL at R-1 where the per-config cost is trivial (deterministic
verticals, CPU-only): the full 2^K factorial, which upgrades the interaction report
(§4.3) from a bound to an exact Shapley decomposition — never required, except as
the §4.2 escalation when IG-3 fires on a CPU-deterministic vertical [STIPULATED:
ASM-0821; Shapley over 2^K configs is standard cooperative-game attribution, cited
as method shape only, no empirical claim].

### 4.2 Attribution semantics — on γ, segmented at the G2 anchor

Let M(a,c) be the family's pre-registered endpoint for arm a ∈ {S,C} under
configuration c, always reported as the selective triple (coverage, selective risk,
dangerous-wrong rate) plus the scalar the family prereg names (§7.1). Define the
mechanism effect **γ(c) = M(S,c) − M(C,c)** [STIPULATED: ASM-0821].

- **Prefix (telescoped) attribution:** Δγ_prefix(j) = γ(PREFIX(j)) − γ(PREFIX(j−1)),
  with PREFIX(0) = FULL-REAL. By construction the chain telescopes exactly, and it
  is read in TWO SEGMENTS [STIPULATED: ASM-0821 — arithmetic identity + the
  review's anchor correction]:
  - **Anchor segment (j = 1…j_anchor):** Σ Δγ_prefix(j) = γ(G2-ANCHOR) −
    γ(FULL-REAL) = γ_G2 − γ_G3 — **the G2→G3 mechanism-effect loss, the exact
    numerator gap the σ gate consumes (§7.2), decomposed with no residual.**
  - **Beyond-anchor segment (j = j_anchor+1…K):** Σ Δγ_prefix(j) = γ(FULL-ORACLE) −
    γ(G2-ANCHOR) — a labelled *beyond-anchor diagnostic* (e.g. H-PS RENDER
    oracling), NEVER counted as G2→G3 loss, because those rungs raise the system
    beyond its registered G2 configuration.
- **Repair attribution:** Δγ_repair(j) = γ(REPAIR(j)) − γ(FULL-REAL) — the
  single-stage recovery of mechanism effect.
- **System-degradation diagnostics (secondary):** the same ladder over M(S,c) alone
  is co-published under the explicit heading "system endpoint degradation" — useful
  for engineering triage, but it is NOT the σ attribution and is never quoted as
  decomposing the G2→G3 gain [STIPULATED: ASM-0821(5) — the review's
  narrower-claim branch, kept alongside the mandatory-γ branch].
- **Prefix-conditioning gap (mandatory report, honestly named):** I(j) =
  Δγ_prefix(j) − Δγ_repair(j), reported per stage with its paired CI. I(j) measures
  how stage j's marginal effect changes when the ENTIRE upstream prefix is gold vs
  real — it is NOT a general interaction decomposition: it cannot name WHICH
  upstream stage interacts, I(1) = 0 by construction, and a small max_j |I(j)| is
  necessary evidence against pipeline-order non-additivity but never sufficient for
  additivity [STIPULATED: ASM-0821(4) — the review's correction, adopted].
  Interactions are EXPECTED (an upstream fix can unmask a downstream failure); the
  protocol measures the non-additivity and gates the claim language on it (IG-3,
  §8); a flagged interaction is LOCALISED only by targeted pair splices {i,j} or
  the 2^K factorial — mandatory escalation on CPU-deterministic verticals, optional
  elsewhere [STIPULATED: ASM-0821(4)].

**Claim-language rule:** "stage j is responsible for X of the loss" may be published
only when |I(j)| is below the pre-registered interaction bound θ_int AND j is in the
anchor segment; otherwise the report publishes the prefix chain and repair vector
side-by-side and the attribution is stated as JOINT over the interacting stage set —
never silently resolved. Passing the θ_int bound licenses "no evidence of
non-additivity at the measured splices", never "additivity established"
[STIPULATED: ASM-0821].

### 4.3 Ordering

The prefix ladder runs in pipeline order (upstream first) — the natural
"conditioned on gold upstream" reading, with the anchor prefix constraint of §3.2.
Pipeline order is itself a choice that can hide order-dependence; the repair vector
is the built-in cross-check (a repair splice is order-free), and the 2^K factorial
removes the dependence entirely where cheap (mandatory on IG-3 escalation for
CPU-deterministic verticals) [STIPULATED: ASM-0821].

### 4.4 The terminal residual — an upper bound, not an attribution

After all spliceable stages are oracled (FULL-ORACLE), define **L_term = M_ceiling −
M(S, FULL-ORACLE)**, where M_ceiling is the family's pre-registered G2 ceiling (for
engine families: the measured covered-exact bound [MEASURED: l3a/a5]; for fusion
families: the family prereg's stated ceiling). **L_term is NOT identified as
LM-use loss** [STIPULATED: ASM-0820(4) — the review's correction, adopted]: it
bundles (i) genuine USE/integration failure, (ii) irreducible task error and label
ambiguity in the eval, (iii) model capacity limits, (iv) error in non-spliceable
executor/renderer internals, and (v) misspecification of the pre-registered ceiling
itself. The report publishes L_term as an **unattributed residual — an upper bound
on USE loss** — with those confounds listed on the same table. A large L_term with
a PASSING delivery probe is *consistent with* the measured nsk1
delivery-without-integration signature and licenses only the language
"integration-limited (unattributed residual)" — never "USE is responsible for X"
[STIPULATED: ASM-0820(4); motivated by MEASURED nsk1].

### 4.5 The observational layer (per-item stage trace)

Every run (all configs, both arms) logs a per-item trace: each stage's input/output
artifact content-hash, typed outcome code (OK / ERR_* fail-closed / ABSTAIN /
DIVERGED-FROM-GOLD-AT-<stage> where gold exists), per-stage confidence score where
the stage emits one, and µs/token cost. The trace supplies (a) the
first-divergence-point label per failed item — the generalisation of l3a-parse's
frame-miss/gazetteer-miss counters — and (b) the per-stage risk-coverage curves
(§7.3). **Authority rule:** where trace and splice disagree, the splice
(interventional) attribution is authoritative; the trace is diagnosis granularity —
a downstream stage whose apparent (trace-visible) error is caused upstream is
exactly the case the splice must win, and KA-6(d) tests it [STIPULATED:
ASM-0821(6) — counters label visible failure, splices establish causal
responsibility].

---

## 5. Oracle artifacts: provenance, authoring, and the no-smuggling rules

[STIPULATED throughout: ASM-0822.]

1. **Pinned before run.** Every oracle corpus (gold parses, gold record maps, gold
   subgraphs, gold engine results, canonical surface forms) is content-hashed and
   pinned in the family's prereg BEFORE any splice run; growing or editing an oracle
   corpus after first use is a new corpus version and restarts that family's ladder.
2. **Blind authoring.** Gold artifacts are authored blind to any system output —
   from the item + store only. Where the two measured verticals already have gold
   (l3a/a5 gold parses; f2b's d-qa-r record↔item map), those pins are REUSED, not
   re-authored [MEASURED: those corpora exist as frozen pins; reuse is a cost fact].
3. **Gold quality is measured, not assumed.** New gold corpora require dual
   independent authoring on a pre-registered sample (≥10% or 100 items, whichever is
   larger) with agreement ≥ the pre-registered bar (default 0.95 artifact-exactness;
   family preregs may tighten); disagreements adjudicated and logged. A corpus
   failing the bar is not an oracle [STIPULATED: ASM-0822, fail-closed gold gate,
   IG-4 §8]. Authoring, dual-annotation, and adjudication hours are logged into
   KOT-LIFE/1 (§10) [STIPULATED: ASM-0824(5)].
4. **Answerability pre-tagging.** Every eval item carries an independent tag —
   `answerable-covered | answerable-uncovered | ambiguous | unanswerable` — assigned
   BEFORE any scoring, by the gold-authoring pass. For `ambiguous`/`unanswerable`
   items the gold PARSE artifact is ABSTAIN (abstention is the correct output), and
   for `answerable-uncovered` the gold EXECUTE artifact is the fail-closed refusal —
   so abstentions are creditable and a stage is never penalised for correctly
   refusing [STIPULATED: ASM-0822, adopted from PARSE.md §4/§5d (amp-2024, dte-2023,
   triagesql-2020 lineage); this is the abstain-credit rule].
5. **Coverage disclosure.** Items lacking a defined gold artifact at stage j are
   EXCLUDED from stage-j splice cells; the exclusion count and reason are published
   per cell (no silent truncation — the programme's no-silent-caps norm). An
   exclusion rate > 20% in any cell voids that cell's attribution claim
   [STIPULATED: ASM-0822].
6. **No oracle leakage into real arms.** The real-regime stages must be bit-isolated
   from oracle corpora at run time (separate process inputs; the harness passes a
   config-scoped artifact bundle) — a real arm that could read gold is a broken run,
   ERR_ORACLE_LEAK, fail-closed [STIPULATED: ASM-0822].
7. **Labelling at the artifact level.** Every result row, plot, and report table
   carries `input_regime` (`full-real`, `prefix:<stage>`, `repair:<stage>`,
   `full-oracle`) AND `arm` (`S`, `C`); any figure quoted anywhere outside the
   report must carry both labels. Full-real is always the FIRST column
   [STIPULATED: ASM-0822; the anti-smuggling surface].

---

## 6. Instrumentation specification

[STIPULATED throughout: ASM-0823 — implementation choices.]

- **Home:** `poc/oracle/` (harness code stays out of `encoder/`, repo convention).
  Zero new runtime deps; node/python per existing harness practice; `nice -n 10`,
  checkpointed per box discipline.
- **Stage interface contract:** every participating architecture implements
  `run_stage(stage_id, item_id, upstream_artifact, config) → artifact | ERR_*`, and
  the harness owns the splice: at an oracled stage it substitutes the pinned gold
  artifact and never calls the real stage.
- **Versioned artifact schemas (review-added):** every stage's input/output
  artifact conforms to a versioned per-stage schema, `kot-stage-artifact/1:<stage>`,
  pinned in the family prereg; a schema change is an instrument version change
  [STIPULATED: ASM-0823(3)].
- **Family adapters (review-added):** each family ships an adapter module mapping
  its implementation onto the stage interface. Where an existing implementation
  cannot expose a boundary — a legacy parser without separable PARSE.a–d seams, or
  a tightly fused learned stage — the adapter either reconstructs the boundary with
  a published method, or the family prereg declares those sub-stages non-spliceable
  and attribution stays at the coarser granularity. Non-spliceable boundaries are
  published limitations, never synthetically split; this protocol is therefore NOT
  automatically a complete decomposition for every family, and each prereg says
  exactly where it is not [STIPULATED: ASM-0823(4) — the review's buildability
  caveat, adopted as a disclosure rule].
- **Config schema** (JSON, hash-pinned per run):
  `{family, vertical, arm: S|C, stage_map: [...], regimes: {stage: real|oracle},
  oracle_corpus_hashes: {...}, endpoint_id, seeds: [...], n_items,
  item_corpus_hash}`.
- **Trace record** (JSONL, one per item × config × arm):
  `{item_id, config_hash, arm, tags: {answerability}, perturbation_class,
  stages: [{stage, regime, in_hash, out_hash, outcome: OK|ABSTAIN|ERR_*,
  diverged_from_gold: bool|null, confidence: float|null, cost_us|tokens}],
  endpoint: {answered: bool, correct: bool|null, dangerous_wrong: bool},
  }` — dangerous_wrong = answered ∧ wrong ∧ provenance-attached, the a5-nl S2 event
  definition [MEASURED: a5-nl S2 class, adopted as the event type].
- **Determinism, realistically scoped (review-corrected):** deterministic stages
  byte-reproducible; LM stages are endpoint-exact ONLY under pinned
  deterministic-kernel enforcement (greedy or pinned-seed decoding + deterministic
  backend flags + pinned hardware/driver revision) — absent that enforcement the
  family prereg registers a reproduction tolerance band instead, and IG-2 judges
  the 1% twice-run sample against whichever regime the prereg pinned; "seed-pinned
  endpoint-exact" is never assumed on nondeterministic GPU kernels [STIPULATED:
  ASM-0823(6)].
- **Error codes:** ERR_ORACLE_LEAK, ERR_GOLD_MISSING, ERR_STAGE_CONTRACT,
  ERR_CONFIG_HASH — all fail-closed, run aborts, no partial report (house style: no
  silent fallbacks).
- **Perturbation typing:** the NL item corpus carries a perturbation-class tag per
  phrasing (minimum taxonomy: `label-verbatim | synonym | structural-paraphrase |
  noise(typo/ASR)`; extendable per vertical), enabling the perturbation × stage
  matrix (§7.5) — the Dr.Spider-shaped practice, K>1 phrasings per query from a
  source disjoint from any calibration set [STIPULATED: ASM-0823(9), adopted from
  PARSE.md §6.5; the measured l3a-parse/a5-nl used K=1, below field practice — this
  protocol requires K≥3 phrasings per item for new corpora, K=1 legacy corpora
  usable only for the shakedown; **every LM-pass cost estimate multiplies by K**
  (§10)].
- **Caching, measured not assumed:** the harness caches by (stage, in_hash) so
  identical sub-computations across configs are computed once; cache hit rates are
  MEASURED and published per run, and no budget line assumes a hit rate in advance
  [STIPULATED: ASM-0823(8)/ASM-0824(5) — the review's resource correction].

---

## 7. Metrics and statistical specification

### 7.1 Endpoint discipline

Each family × vertical decomposition names ONE pre-registered endpoint scalar M
(inherited from the family's G2/G3 prereg — e.g. covered-exactness for engine
families, item accuracy for fusion families) and ALWAYS co-reports the selective
triple: coverage (fraction answered), selective risk P(wrong | answered), and the
dangerous-wrong rate P(answered ∧ wrong ∧ provenance) — because abstention is part
of every product and the two risk notions diverge exactly when coverage drops
[STIPULATED: ASM-0826(1), adopted from PARSE.md §8 gate-instrument requirement (1)].

### 7.2 The survival fraction σ (the K-P3v2(5) quantity) — and its mandatory γ ladder

For family F with mechanism system S and its pre-registered no-mechanism control C
(the family's factorial control cell, programme §2.2):

- γ_G2 = γ(G2-ANCHOR) = M(S, G2-ANCHOR) − M(C, G2-ANCHOR)
- γ_G3 = γ(FULL-REAL) = M(S, FULL-REAL) − M(C, FULL-REAL)
- **σ = γ_G3 / γ_G2**, defined only when the one-sided 95% LCB of γ_G2 > 0
  (otherwise σ is N/A and the family has no G2 effect to lose — G2 already failed).

σ with its one-sided 95% CI (hierarchical bootstrap per §7.5) is THE number
K-P3v2(5) consumes: "G2 gain fails to survive G3 at the pre-registered retention
margin" ≡ UCB95(σ) < σ_min for the family, with σ_min set in the family's prereg,
not here [STIPULATED: ASM-0824(1); the margin is the family's choice, the estimator
is this protocol's]. **Both arms cross the NL boundary under every mandatory
configuration (§4.1): the splice ladder decomposes γ itself** — the anchor-segment
telescope Σ_{j≤j_anchor} Δγ_prefix(j) = γ_G2 − γ_G3 attributes the σ numerator gap
stage by stage, so a σ decline is never ambiguous between "S degraded" and "C
improved": the C column of every cell is published alongside S, and any rung where
the γ drop is driven by C improving rather than S degrading is visible and named in
the report [STIPULATED: ASM-0821 — the review's ranked concern 1, adopted; the
formerly-optional control ladder is now mandatory]. The S-only ladder remains a
co-published secondary ("system endpoint degradation", §4.2), explicitly separate
from σ attribution.

### 7.3 Per-stage risk-coverage

For every stage that emits a confidence score, the report includes the stage's
risk-coverage curve (risk vs coverage as the stage's abstention threshold sweeps)
and AUACC, computed at FULL-REAL and at the stage's repair splice — a scalar
operating point is never the only view [STIPULATED: ASM-0826(2), adopting PARSE.md
§8 verbatim].

### 7.4 Stage-artifact metrics

As tabled in §3.1 — each stage has an artifact-level match function against gold
(whole-frame exactness for PARSE, never intent-accuracy/slot-F1 alone [STIPULATED:
ASM-0820, adopting PARSE.md §2 metric discipline]; set P/R@k for RETRIEVE; graph F1
for CONSTRUCT; probe keyacc for ENCODE; exactness for EXECUTE; result-preservation
for RENDER). Artifact metrics are DIAGNOSTIC covariates; endpoint splices are the
attribution [STIPULATED: ASM-0821(6) authority rule].

### 7.5 The two attribution matrices — and the uncertainty hierarchy

1. **Stage-loss vector:** {Δγ_prefix(j)} (anchor and beyond-anchor segments
   labelled), {Δγ_repair(j)}, {I(j)} with paired 95% BCa bootstrap CIs, plus the
   unattributed terminal residual L_term (§4.4) and the secondary S-only vector.
2. **Perturbation × stage matrix:** Δγ_prefix(j) recomputed per perturbation class —
   which phrasing class breaks which stage (worst-class reported, not aggregate
   only) [STIPULATED: ASM-0823(9), Dr.Spider-shaped practice per PARSE.md §6.5].

**Uncertainty hierarchy (review-corrected):** the bootstrap is hierarchical with the
ITEM as the top-level resampling cluster; the K phrasings of an item stay nested
inside their item and are never resampled as independent units; where an LM stage
samples (non-greedy), ≥2 registered seeds are run and seed enters as a registered
variance component at its own level; items are paired across configs AND arms
(identical item sets by construction), and CIs on γ quantities are computed on
item-level paired differences [STIPULATED: ASM-0826(3)].

### 7.6 S2 (dangerous-wrong) attribution rule — mechanical

For every dangerous-wrong event at FULL-REAL: the event is attributed to stage j iff
REPAIR(j) flips that item to correct-or-abstain; if multiple stages flip it, it is
multi-attributed (reported in a separate joint bucket, never split fractionally); if
NO single repair flips it, it is attributed JOINT-UPSTREAM (the smallest prefix that
flips it) [STIPULATED: ASM-0821(7)]. Per-stage S2 counts carry Wilson bounds — and
any claim that a repair establishes the dangerous-wrong rate at-or-below a bar uses
the one-sided 95% UPPER confidence bound below the bar (the safety-establishment
direction; an LB below the bar proves nothing — LB≥bar is the different, KILL-firing
direction) [STIPULATED: ASM-0825 KA-4 correction, adopted from the review]. The
known-answer test is a5-nl's 43 measured events, whose mechanism is a PARSE.c
table defect — the shakedown must recover that attribution (§8) [MEASURED: a5-nl
S2 = 43/855, mechanism per its assessment; the recovery requirement is the test].
Standing caution carried on every S2 line: confidence scores can FAIL to separate
systematic high-confidence inversions (the conformal-abstention caveat), so S2
attribution never relies on stage confidence — only on splice flips [STIPULATED:
ASM-0821(7), adopting PARSE.md §4/§5c].

### 7.7 Sample sizes and power — endpoint-typed, no blanket claim

Legacy verticals: the full pinned item corpora are reused (527 NL items on l3a's
family/world slice; 855 on a5-nl) — sizes at which the measured Wilson intervals
were decision-grade FOR THOSE endpoints and verticals [MEASURED: l3a-parse/a5-nl
envelopes], carried as measured anchors only, never as a general sufficiency claim
[STIPULATED: ASM-0826(4)]. For new corpora, the family prereg MUST derive n from
its endpoint type and target (protocol default target: detect a stage loss of
Δ = 0.05 on the endpoint scale at 80% power, one-sided 5%; family-overridable
upward only) [STIPULATED: ASM-0826(4) — the review's power correction, adopted]:

- **Paired binary endpoints:** McNemar power computed from a PRE-REGISTERED
  discordant-pair-rate estimate, sourced from the shakedown or a pilot; required n
  scales inversely with the discordant rate and CAN exceed 1000 — the previous
  blanket "n ≈ 500–1000 covers this" claim is WITHDRAWN.
- **Continuous endpoints (graph F1, AUACC, etc.):** paired-difference power from a
  pre-registered SD estimate, or simulation-based power via the §7.5 hierarchical
  bootstrap — McNemar is never applied to non-binary endpoints.
- **The unit is the ITEM:** K phrasings are nested, not independent — they do not
  multiply effective n, and every power computation uses the item count.

Multiplicity: the stage-loss vector is DIAGNOSTIC (no verdict fires from it); σ is
the only gate-feeding estimand and gets the one-sided CI; no FWER correction is
applied to diagnostic vectors, and this is stated on every report [STIPULATED:
ASM-0826(5); house §2.5 rule 5 — one primary per experiment — applied per
ASM-0813].

---

## 8. Instrument gates and the protocol's own falsifiers

The protocol is itself an instrument and must be validated on known answers before
it judges any new architecture [STIPULATED: ASM-0825; programme §2.4 calibration
norm, applied to this instrument].

**Instrument gates (every family run, fail-closed):**

- **IG-1 (ceiling reproduction):** the G2-ANCHOR config must reproduce the family's
  registered G2 result within its pre-registered tolerance (deterministic verticals:
  exactly; LM endpoints: within the §6 reproduction band). Failure = harness bug; no
  attribution is published.
- **IG-2 (determinism):** the 1% twice-run sample must match — byte-exact for
  deterministic stages; for LM stages, endpoint-exact under pinned
  deterministic-kernel enforcement, otherwise within the pre-registered
  reproduction band (§6) [STIPULATED: ASM-0823(6)].
- **IG-3 (interaction bound):** if max_j |I(j)| > θ_int (default 0.10 endpoint
  scale, family-overridable downward only), single-stage claim language is BARRED
  for the interacting stages (§4.2) — the report still publishes, with joint
  attribution only, and on CPU-deterministic verticals the 2^K factorial escalation
  is mandatory to localise the interaction [STIPULATED: ASM-0821(4)].
- **IG-4 (gold quality):** dual-authoring agreement ≥ bar (§5.3) on every new oracle
  corpus.
- **IG-5 (exclusion ceiling):** per-cell exclusions ≤ 20% (§5.5).

**P3-E-ORACLE-0 — the known-answer shakedown (the design's falsifier; new bead §12):**
two components, both pre-registered [STIPULATED: ASM-0825]:

**(A) Legacy-vertical replay** — rebuild the ladder on the two ALREADY-MEASURED
verticals (a1-hybrid front-end + engine, frozen pins reused; CPU-only, ~$0;
real-boundary cells populated by replaying the frozen measured per-item artifacts,
per §9.2 — no new natural-input execution pre-ratification):

1. **KA-1 (paired ceiling, corrected):** FULL-ORACLE reproduces gold-parse covered
   exactness on the PAIRED NL item slices — **527/527** on the l3a family/world NL
   slice and **855/855** on a5-nl [MEASURED anchors: l3a-parse/a5-nl gold-parse
   replication]. The 600/600 figure is the larger PARENT FORMAL slice [MEASURED:
   l3a]; it is checked separately as an engine regression, never as the paired
   shakedown cell — the previous "600/600" bar was arithmetically unmeetable on the
   527-item slice [STIPULATED: ASM-0825, review correction adopted].
2. **KA-2 (regression only — disclosed as near-true-by-construction):** the
   decomposition attributes ≥ 95% of the measured G2→G3 loss to the PARSE stage
   family on both verticals — the known truth, because in the measured system the
   parser is the ONLY boundary-crossing fallible stage (everything downstream is
   the exact deterministic engine) [MEASURED: l3a-parse/a5-nl mechanism]. Because
   the harness directly replaces the sole fallible stage with gold, KA-2 validates
   plumbing and regression only; it CANNOT validate multi-stage causal attribution —
   that decisive test is KA-6 [STIPULATED: ASM-0825, review's ranked concern 2
   acknowledged].
3. **KA-3 (with a numeric tolerance, previously deferred):** sub-stage attribution
   reproduces the measured l3a-parse first-divergence breakdown
   (frame-miss 228 / mapper-abstain 48 / gazetteer-miss 40 / frame-ambiguous 41)
   with each sub-stage's attributed share within ±0.10 ABSOLUTE of its measured
   share and frame-miss remaining the modal category; the paraphrase stratum must
   fail at PARSE.a/PARSE.b [MEASURED: parse_stage_breakdown 228/48/40/41;
   STIPULATED tolerance: ASM-0825].
4. **KA-4 (bound direction corrected):** the S2 rule (§7.6) attributes ≥ 90% of
   a5-nl's 43 dangerous-wrong events to PARSE.c (the ROLE_DIR direction table), AND
   the PARSE.c repair splice drives the post-repair dangerous-wrong **one-sided 95%
   UCB below the 0.02 bar** on that vertical — establishing ≤2% requires the UCB
   below the bar; the previous LB formulation proved nothing [MEASURED: a5-nl
   assessment mechanism; STIPULATED: ASM-0825 — this simultaneously prices the
   deterministic ROLE_DIR repair the a5 assessment proposed].
5. **KA-5:** IG-1..IG-5 all pass with the legacy K=1 phrasing corpora (disclosed as
   below-field-practice, shakedown-only).

**(B) Synthetic factorial fault-injection pipeline (the DECISIVE falsifier —
review-added):**

6. **KA-6:** a synthetic known-answer pipeline — deterministic, CPU-only, ~$0, with
   a paired control arm and fully known ground truth — exercising the γ path
   end-to-end, containing by construction [STIPULATED: ASM-0825, the review's
   six-property list adopted verbatim]:
   (a) independently injected faults in ≥ 2 distinct stages at known marginal
   rates; (b) one pure two-stage interaction — items that flip only when BOTH
   stages are repaired; (c) one harmless artifact divergence (artifact differs
   from gold, endpoint unaffected); (d) one downstream stage whose apparent
   (trace-visible) error is caused upstream; (e) planted dangerous-wrong events
   with known causal stages; (f) one no-effect oracle splice.
   **PASS bars (exact — the pipeline is deterministic):** the ladder recovers the
   planted marginal attributions exactly; the planted interaction receives JOINT
   (not single-stage) claim language via IG-3; the harmless divergence and the
   no-effect splice are attributed zero endpoint loss; the upstream-caused error is
   attributed to the upstream stage, against the misleading trace label (the §4.5
   authority rule under test); planted-S2 recovery is 100%.

A shakedown FAIL on KA-2/KA-3/KA-4/KA-6 falsifies the protocol design (not the
architectures) and returns it here for redesign before any family G3 run consumes it
[STIPULATED: ASM-0825 — the design's own kill, verbatim].

---

## 9. Governance: what runs when, and what nothing here licenses

[STIPULATED: ASM-0824.]

1. **Every configuration with ≥1 oracled stage is `oracle-diagnostic`** under
   ASM-0814: NO W1 claim, no real-input claim of any kind, label carried on every
   artifact (§5.7).
2. **FULL-REAL legs: proposal, not self-grant (review's ranked concern 3,
   adopted).** The reviewed draft created a `boundary-diagnostic` class for
   FULL-REAL protocol runs; the programme's explicit exemption list names only
   P3-E-NLB-1, the G1 censuses, and oracle-labelled G2 (programme §4 / lines
   194–201, 881–889) — this design cannot extend that list itself. The class is
   therefore registered inside ASM-0824 **as a proposed programme/ASM-0814
   amendment**, bundled with the P3-E-CAL sequencing exemption for decomposition
   runs, and has **no effect until an explicit coordinator/maintainer ratification
   decision is recorded as an amendment**. Fail-closed interim rule [STIPULATED:
   ASM-0824(2)]:
   - configurations in which every boundary-crossing store-addressing stage is
     oracled run NOW, as ordinary `oracle-diagnostic` legs under ASM-0814;
   - FULL-REAL and partially-real-boundary cells are populated ONLY by replaying
     the frozen, already-measured per-item artifacts of registered runs
     (l3a-parse/a5-nl for the shakedown) — no new natural-input execution; a
     needed artifact that was not retained excludes that cell with disclosure
     (ERR_GOLD_MISSING-class, published per §5.5) and never triggers re-execution;
   - any new-family FULL-REAL leg waits for per-vertical NLB clearance
     (P3-E-NLB-1) or the ratified amendment, whichever comes first.
   If ratified, the class licenses ONLY the measured retention/σ/attribution
   vector — never an index, usefulness, or competitive claim — which is how the
   instrument can inform the NLB redesign cycles (K-P3v2(2)/(5)) rather than
   deadlock behind them; if rejected, the protocol still runs everywhere the
   interim rule allows.
3. **P3-E-CAL exemption — same ratification bundle:** decomposition runs make no
   index claim and should not wait for index calibration; this rider travels inside
   the ASM-0824(2) amendment request rather than being assumed here.
4. **G4 co-publication — supplement, not substitute:** any G4 (W1-relevant) attempt
   by a store-touching family must co-publish its most recent decomposition report
   (the attribution annex); a G4 report without one is incomplete under KOT-FAIR/2.
   The annex does NOT satisfy KOT-FAIR/2's six-way factorial controls or the
   matched generic-RAG comparator — those remain separately mandatory
   [STIPULATED: ASM-0824(3), review correction adopted].
5. **No oracle number travels:** the report template places FULL-REAL first; oracle
   columns are visually and machine-readably labelled (`input_regime` + `arm`);
   quoting an oracle-column number without its regime label anywhere in the repo is
   a claims-lint violation (extend `tools/registry/claims-check.py` pattern set —
   implementation rider on P3-E-ORACLE-0).

---

## 10. Cost and execution at the 100M–2B tiny scale

[STIPULATED: ASM-0823/ASM-0824 sizing rules; EXTRAPOLATION where marked. Scored
inputs = n items × K phrasings; arm-configs = configurations × {S, C} before
degenerate-C de-duplication (§4.1); the K≥3 multiplier and the control arm are IN
the estimates below — the reviewed draft omitted both.]

| Run | Stages K | Arm-configs | Scored inputs | Compute | Cost class |
|---|---|---|---|---|---|
| P3-E-ORACLE-0 (A) legacy replay | 6–8 (PARSE.a–d + RETRIEVE + EXECUTE + RENDER) | ≤ 18 (S-arm; legacy verticals have no registered mechanism-control C — disclosed; the γ path is validated in (B)) | (527 + 855) × K=1 | CPU only; frozen-artifact replay + engine (front-end ~267 µs, engine ~µs [MEASURED: l3a-parse sec-cost, l3a/a5 timing]) | ~$0, hours on the shared box, niced |
| P3-E-ORACLE-0 (B) synthetic fault-injection (KA-6) | 5 | 2 × (2K+2) = 24 mandatory + full 2×2^K = 64 factorial | 500 synthetic × K=1 | pure CPU, deterministic | ~$0 |
| H-VL / H-PS family decomposition, R-1 | 5–7 | ≤ 2×16 = 32 | 500–1000 items × K≥3 = 1,500–3,000 each ⇒ ≤ ~10^5 LM generations before caching | LM stages dominate at 135–360M | ≤ ~15 GPU-h/family [EXTRAPOLATION: throughput at 135M–360M on one A100-class card; inside the R-1 ≤50 GPU-h family envelope; realised cache savings measured, not assumed] |
| H-GNN / H-RULE decomposition, R-0/R-1 | 4–6 | ≤ 2×14 = 28 | 1,500–3,000 each | + encoder forward + probe passes | ≤ ~30 GPU-h/family [EXTRAPOLATION, same basis] |
| **R-3 rerun (1–2B), G4/G5 survivors only** | as family | same grid | same grid | ~10–15× the per-token cost of the 135M rung at 1.7B-class models | ~100–200 GPU-h/family [EXTRAPOLATION]; **explicitly budgeted in the family's R-3 prereg from the gated R-3 allocation (maintainer + secured allocation, programme §4) — never absorbed silently and NOT covered by the R-1 envelope** |
| Optional 2^K factorial | 6 | 2×64 | 500 × K | deterministic verticals only | CPU, ~$0 |

The ladder's cost multiplier over a plain G3 run is ≤ 2×(2K+1) arm-configs, but
most configs differ only in which cheap deterministic stage is spliced — the LM
forward passes (the true cost) are shared or re-run only where an upstream splice
changes the LM's input. The harness caches by (stage, in_hash); **realised cache
hit rates are measured and published per run, and no budget assumes them in
advance** [STIPULATED: ASM-0823(8)].

**Resource accounting (review-added, mandatory)** [STIPULATED: ASM-0824(5)]:

1. Actual CPU/GPU hours of EVERY splice run enter the family's tuning/development
   audit trail (the KOT-FAIR/2 tuning-symmetry ledger) — diagnostic spend is spend.
2. Oracle authoring, dual annotation, adjudication, and K≥3 phrasing-production
   hours enter KOT-LIFE/1 (store-side lifecycle cost).
3. Any FULL-REAL figure feeding a G4 reading carries the complete KOT-COST/2
   warm/cold resource vector — never `cost_us|tokens` alone.
4. The 1–2B reruns and the K≥3 expansion are explicit budget lines in each family
   prereg (the table above), not assumed slack.

**Prereg checklist block (copy into every family Phase-2 prereg that claims a G3
reading):**

```
KOT-DECOMP/1 instantiation:
  stage_map: [...]                     # §3.2 row, completed
  B(F) + j_anchor: [...]               # boundary set; anchor prefix = registered G2 config
  control_arm_C: {stage_map, degenerate_splices}   # §4.1 — mandatory paired arm
  oracle_corpora: {stage: sha256}      # pinned pre-run (§5.1)
  gold_quality: {corpus: agreement}    # IG-4 evidence (§5.3)
  artifact_schemas: {stage: kot-stage-artifact/1 pin}  # §6
  adapter + non-spliceable disclosure  # §6 — where boundaries cannot be exposed
  endpoint_id + selective-triple defs  # §7.1
  σ_min: <margin>                      # the K-P3v2(5) retention margin
  θ_int: <bound>                       # IG-3 (≤ 0.10)
  n + endpoint-typed power computation # §7.7 (discordant-rate / SD source named)
  seeds + determinism regime           # §6 (deterministic-kernel enforcement or band)
  perturbation taxonomy + K phrasings  # §6 (K≥3; cost estimates × K)
  exclusions forecast                  # §5.5
  resource lines                       # §10: splice-hours → tuning ledger;
                                       #      authoring-hours → KOT-LIFE/1; R-3 budget
  full_real_governance: NLB-cleared | frozen-replay | ratified-amendment   # §9.2
```

---

## 11. Registered stipulations (this revision's ASM block)

Registered by this revision in `registry/assumptions.jsonl`, append-only block
0820–0849 (next free block after ASM-0819 at registration time); the reviewed
draft's placeholder ids ASM-ORC-1..6 are retired and map as follows:

- **ASM-0820 (taxonomy; was ORC-1):** canonical stage taxonomy §3.1 (PARSE.a–d,
  RETRIEVE, CONSTRUCT, ENCODE, EXECUTE, RENDER), B(F) §3.2, the ENCODE
  probe-instrumented/splice-limited rule, and the terminal residual L_term as an
  explicitly UNATTRIBUTED upper bound with named confounds (review correction).
- **ASM-0821 (attribution semantics; was ORC-2, estimand corrected):** the γ(c)
  estimand with the MANDATORY paired control ladder; the mandatory config set; the
  anchor-segmented telescope (G2→G3 loss = γ(G2-ANCHOR) − γ(FULL-REAL), beyond-
  anchor rungs labelled diagnostic); the prefix-conditioning gap I(j) with its
  stated limits and the pair-splice/2^K localisation escalation; the claim-language
  rule; interventional authority; the mechanical S2 attribution rule.
- **ASM-0822 (oracle provenance; was ORC-3):** pin-before-run, blind dual authoring
  + IG-4 agreement bar, answerability pre-tagging with abstain-credit, per-cell
  exclusion disclosure with the 20% void bar, ERR_ORACLE_LEAK isolation,
  `input_regime` + `arm` labelling on every artifact.
- **ASM-0823 (instrumentation; was ORC-4, schema/determinism corrected):**
  `poc/oracle/` harness, stage-interface contract, VERSIONED per-stage artifact
  schemas + family adapters with non-spliceable disclosure, config/trace schemas
  incl. arm, realistic determinism regimes (deterministic-kernel enforcement or a
  registered reproduction band), fail-closed ERR_* set, measured-not-assumed
  (stage, in_hash) caching, K≥3 phrasings with the K-multiplier in every cost line.
- **ASM-0824 (governance + gate feed; was ORC-5, overreach removed):** σ as the
  K-P3v2(5) estimand on γ with family-set σ_min; the `boundary-diagnostic`
  FULL-REAL class registered AS A PROPOSAL requiring coordinator ratification
  (bundling the P3-E-CAL rider), with the fail-closed interim rule of §9.2;
  KOT-DECOMP/1 supplements-never-satisfies KOT-FAIR/2; G4 co-publication; the §10
  resource-accounting obligations (tuning ledger, KOT-LIFE/1, KOT-COST/2 vector,
  explicit R-3 budgets).
- **ASM-0825 (the design's own falsifier; was ORC-6, bars corrected + KA-6 added):**
  KA-1 paired ceilings 527/527 + 855/855 (600/600 demoted to a separate engine
  regression); KA-2 disclosed as regression-only; KA-3 with the ±0.10-share
  tolerance; KA-4 in the UCB direction; KA-5; KA-6 the synthetic factorial
  fault-injection pipeline with the review's six required properties and exact PASS
  bars; a KA-2/3/4/6 FAIL falsifies KOT-DECOMP/1.
- **ASM-0826 (statistics):** endpoint discipline + selective triple; per-stage
  risk-coverage; the hierarchical bootstrap (item clusters, nested phrasings, seed
  variance component); endpoint-typed power with the blanket-n claim withdrawn;
  σ-only multiplicity rule.

---

## 12. Beads this design recommends the coordinator bd-create

*(Recommendation only — this bead runs no bd-create per its governance.)*

1. **P3-E-ORACLE-0 — KOT-DECOMP/1 harness + known-answer shakedown** [EXP-shaped
   build+run, P1, blocked-by: this design (review-passed)]. Build `poc/oracle/`
   (stage-interface harness + versioned artifact schemas, splice runner, paired-arm
   γ path, trace/report generators, claims-lint pattern rider), reuse the frozen
   l3a-parse/a5-nl pins + gold corpora (real-boundary cells by frozen-artifact
   replay per §9.2), BUILD the KA-6 synthetic fault-injection pipeline, and run
   KA-1..KA-6. CPU-only, ~$0, local box. Its PASS is the precondition for any
   family G3 decomposition; its FAIL returns this design for revision.
2. **Coordinator decision item (not a bead this design can execute):**
   ratify-or-reject the ASM-0824(2) `boundary-diagnostic` amendment (with its
   P3-E-CAL rider) as a programme/ASM-0814 amendment record, BEFORE any new-family
   FULL-REAL decomposition leg is scheduled; until then the §9.2 interim rule
   stands.
3. **(rider, not a new bead)** P3-D-NLB and P3-D-PS should consume §8 KA-4's
   PARSE.c repair-splice pricing when it lands — the deterministic ROLE_DIR repair
   the a5-nl assessment proposed gets its effect size measured for free inside the
   shakedown. Suggested as a note on `kernel-of-truth-s55r.13` rather than a bead.

No other new beads: per-family decomposition runs are legs of the already-planned
P3-E-* experiments (their preregs adopt the §10 checklist), not separate beads
[STIPULATED: ASM-0824 scoping — keeps the WBS as programme rev-2 §5 drew it].

---

## 13. Epistemic register (what this design relied on)

- **MEASURED (restated strictly within envelopes):** l3a/a5 covered-exactness +
  timing (instrument-only; 600/600 + 855/855 on the FORMAL slices); l3a-parse 47.6%
  retention on the 527-item NL slice + gold-parse replication 527/527 + stage
  breakdown 228/48/40/41 + SAFE failure; a5-nl 41.6% + S2 fired 43/855 + ROLE_DIR
  mechanism; f2b-replicate +0.1507 (alignment-confounded, formal-only); nsk1
  delivery-at-echo / integration-unresolved + g2d net-harmful (exploratory/DRAFT);
  front-end ~267 µs.
- **STIPULATED (design choices, registered this revision):** ASM-0820 taxonomy +
  B(F) + unattributed terminal residual; ASM-0821 γ estimand + mandatory control
  ladder + anchor segmentation + prefix-conditioning gap + S2 rule; ASM-0822 oracle
  provenance + abstain-credit + exclusion bars; ASM-0823 harness contract + schemas
  + adapters + determinism regimes + K-multiplier; ASM-0824 σ governance +
  ratification-gated exemption proposal + KOT-FAIR/2 supplement rule + resource
  accounting; ASM-0825 the corrected known-answer bars + KA-6; ASM-0826 statistics.
- **STIPULATED (adopted from parents, not new):** ASM-0814 oracle-diagnostic rule;
  ASM-0817 G1–G5 ladder + sequencing exemptions (whose list this design does NOT
  extend by itself); ASM-0818 K-P3v2(5); ASM-0815 CD-transport + causal-provenance
  rules; ASM-0812 KOT-FAIR/2 factorial + generic-RAG controls; house statistics
  ASM-0813; PARSE.md §8's P3-D-ORACLE requirements (per-stage oracle ablation,
  risk-coverage per stage, ambiguity pre-tagging, single-arm insufficiency) and
  §2/§4/§6 metric/robustness practice.
- **EXTRAPOLATION (never premises):** the complete KOT stage protocol as a working
  instrument (field-attested ingredients, unattested assembly — PARSE.md §8 says so
  explicitly; P3-E-ORACLE-0, decisively its KA-6 component, is the test); the
  R-1/R-3 GPU-hour sizing estimates (§10); the expectation that loss concentrates
  in PARSE/RETRIEVE for engine families (direction-only, from the measured
  verticals — each family's ladder measures its own).

This document changes no frozen object, no verdict, no audit; its stipulations are
registered append-only as ASM-0820..0826; the single governance extension it needs
(the FULL-REAL `boundary-diagnostic` class) takes effect only on coordinator
ratification (§9.2), and the protocol takes effect only on a P3-E-ORACLE-0 PASS.

---

## 14. Revision-1 change map (review point → change)

| Review point (rev-dORACLE-20260711) | Change in this revision |
|---|---|
| Ranked 1: wrong quantity decomposed — control ladder must be mandatory | §4.1/§4.2/§7.2: γ(c)=M(S,c)−M(C,c) is the decomposed estimand; every mandatory config runs on both arms; degenerate-C convention; S-only ladder demoted to labelled secondary (ASM-0821) |
| Ranked 2: falsifier largely tautological | §8: KA-2 relabelled regression-only/near-true-by-construction; KA-6 synthetic factorial fault-injection pipeline added with the review's six properties + exact PASS bars (ASM-0825) |
| Ranked 3: governance overreach (FULL-REAL exemption self-granted) | §9.2/ASM-0824(2): exemption converted to a ratification REQUEST with a fail-closed interim rule (oracle-boundary configs run now; real-boundary cells by frozen-artifact replay only; new-family FULL-REAL waits for NLB or ratification); §12 coordinator decision item |
| FULL-ORACLE not consistently G2 (H-PS RENDER) | §3.2/§4.2: j_anchor prefix constraint; anchor-segmented telescope; G2→G3 loss = γ(G2-ANCHOR)−γ(FULL-REAL); beyond-anchor rungs labelled diagnostic (ASM-0821(3)) |
| USE residual not identified | §3.1/§4.4: renamed L_term, an UNATTRIBUTED upper bound with five named confounds; nsk1 signature is consistent-with, never proof; claim language barred (ASM-0820(4)) |
| Interaction statistic incomplete (I(1)=0; no localisation; small I ≠ additivity) | §4.2/IG-3: renamed prefix-conditioning gap; limits stated; pair-splice/2^K localisation escalation; "no evidence of non-additivity" language cap (ASM-0821(4)) |
| Wrong confidence-bound direction (KA-4 LB) | §7.6/§8 KA-4: one-sided 95% UCB < 0.02 (safety-establishment direction) (ASM-0825) |
| Incompatible shakedown sample (600/600 vs 527) | §8 KA-1: paired ceilings 527/527 + 855/855; 600/600 demoted to separate engine regression (ASM-0825) |
| KA-3 has no actual tolerance | §8 KA-3: ±0.10 absolute per sub-stage share + frame-miss modal, set now (ASM-0825) |
| Power claim unsupported; McNemar ≠ continuous endpoints | §7.7: blanket n claim withdrawn; endpoint-typed power (McNemar from pre-registered discordant rate; paired/simulation power for continuous); item is the unit (ASM-0826(4)) |
| Stochastic hierarchy underspecified; endpoint-exact repro unrealistic | §6/§7.5/IG-2: item-cluster hierarchical bootstrap, nested phrasings, seed variance component; determinism regimes (deterministic-kernel enforcement or registered band) (ASM-0823(6)/ASM-0826(3)) |
| KOT-DECOMP/1 must supplement, not satisfy, KOT-FAIR/2 | §1(5)/§9(4): supplement-never-substitute stated; factorial + generic-RAG controls remain separately mandatory (ASM-0824(3)) |
| K≥3 not multiplied into LM-pass estimates | §6/§10: scored inputs = n×K in every cost line; table recomputed (ASM-0823(9)) |
| Cost model missing 1–2B end | §10: explicit R-3 rerun row, ~100–200 GPU-h/family [EXTRAPOLATION], gated-allocation budgeting mandatory (ASM-0824(5)) |
| Resource accounting incomplete | §5.3/§10: splice-hours → tuning ledger; authoring/annotation/adjudication/phrasing hours → KOT-LIFE/1; cache savings measured not assumed; full KOT-COST/2 warm/cold vector on any G4-feeding FULL-REAL figure (ASM-0824(5)) |
| No versioned artifact schemas / family adapters; fused stages | §6: kot-stage-artifact/1:<stage> schemas pinned per prereg; adapter modules; non-spliceable-boundary disclosure rule (ASM-0823(3)/(4)) |
