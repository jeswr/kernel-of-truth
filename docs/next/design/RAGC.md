# P3-D-RAGC — RAGC/1: the matched generic-RAG/tool-use control (Phase-1 design, revision 2)

> **Status: Phase-1 [DESIGN] deliverable of Programme-3 (bead kernel-of-truth-s55r.15,
> P3-D-RAGC), revision 2 — the 2026-07-11 external review
> (`poc/gpt56-review/rev-dRAGC-20260711b`) applied in full; see the CHANGELOG below.
> Nothing here is frozen, pre-registered, scheduled, or run; no verdict, audit, or
> frozen object is touched. Revision-1 assumption entries remain REGISTERED at
> **ASM-0920…ASM-0927**; the revision-2 corrections are registered in the fresh
> append-only block **ASM-0950…ASM-0957** (block ASM-0950–0959 assigned to this
> revision; 0958–0959 remain free). Where a revision-2 entry supersedes a clause of
> a revision-1 entry, the supersession is named in the entry's notes — the register
> is append-only, nothing is edited in place.** Author: Fable, chief-architect role
> (`kern/fable-designer`), 2026-07-11.
>
> **Blocked-by inputs, read in full at source:**
> `docs/next/programme-3-neurosymbolic-architecture.md` (revision 2) — §2.2(2) the
> factorial control design incl. cell (f) "the matched generic-RAG/tool-use control
> (the strongest missing control)" (ASM-0812), §2.3 the six-way attribution
> factorisation + clause (iii), §1.4 W1 condition 4, §2.5 the statistical
> specification, §5 the P3-D-RAGC row ("same corpus, same retriever/index, same
> budgets" — read per §3.1's corrected sense: same retriever procedure, necessarily
> per-representation indexes); `docs/next/lit/RAG.md` (P3-LR-RAG) — §6 the five
> open design rules + supplied cells, §3 honest index accounting, §7.1 "the largest
> open item", §8 the P3-D-RAGC hand-off row; `docs/next/design/FRONT.md` (FRONT/1
> revision 2) — §5 the five matched-retrieval rules resolved as **binding defaults
> RAGC inherits verbatim** (ASM-0853), §1 the anchor-derived budget vector B_k,
> §2.3 the C3 arm types, §9 the interface row "RAGC instantiates factorial cells,
> amends only by registered change"; `docs/next/design/MF0.md` — §8.2(iii)
> (ASM-0890) + §8.5 the framework-owned cell inventory ("the
> retrieval-architecture cells are P3-D-RAGC's to implement"; executor-axis DRAFT
> cells "P3-D-RAGC/P3-D-ORACLE freeze them") (ASM-0891);
> `docs/next/arch/round1-critique-synthesis.md` — A.4/B.1 (W1 hypergraph's
> source-parity two-arm design inherited here as the worked-example shape; the
> generic-Datalog attribution cell of A.1 folded into the executor axis; B.2.2 the
> per-source-class precision census requirement); `docs/next/feasibility-synthesis.md`
> — the binding measured walls (§0–§2).
>
> **Tag convention (house discipline):** `[MEASURED: ref]` = a programme registry
> verdict/assessment restated strictly inside its envelope; `[LIT-BACKED: lit-review
> §]` = an external fact verified at primary source by a completed Phase-0 lit
> review, cited through that review; `[STIPULATED: id]` = a design choice made here
> or inherited from a registered stipulation (every design CHOICE is STIPULATED);
> `[EXTRAPOLATION: id]` = a registered forward projection, never a premise.

## CHANGELOG (revision 2 — each line names the review item it answers)

| Review item (rev-dRAGC-20260711b) | Repair | Where |
|---|---|---|
| **Ranked 1**: six-factor causal attribution invalid (contrasts change multiple factors; no interactions; integration unisolated) | attribution semantics rewritten: elimination + bounded-bundle licences only; no single-factor causal sentences; integration carried as an explicitly unattributed residual (ASM-0950) | §0, §7 |
| **Ranked 2**: KOT-FAIR/2 admissibility not closed (store caps not derived from total B_k; GR-C/GR-D lack SIZE/COST contracts) | total-system admissibility first; store cap derived as a residual of B_k.bytes; the anchor-generator arithmetic consequence stated; complete KOT-SIZE/2 + measured KOT-COST/2 vectors per arm in the manifest (ASM-0951) | §2.2, §8.1 |
| **Ranked 3**: cheap decisive test not prereg-ready (no frozen contrast, margin, kill rule, power, spend stop) | the f2b de-confound pre-specified in full: primary contrast, margins, kill rule, power target, spend stop, scope licence (ASM-0957) | §8.4 |
| "same retriever/index" over different object sets impossible | shared retriever = same algorithm/weights/config/build procedure; each representation necessarily builds its own hash-pinned index (ASM-0952) | §1.1, §3.1 |
| V2 ordering invariant invalid; LCB stated for one inequality only | single preregistered discrimination contrast LCB95(OR − R0) > 0; orderings reported with CIs as diagnostics, never gated (ASM-0953) | §9 |
| ε-parity uses observed difference without uncertainty | paired TOST/equivalence CI; failure to prove equivalence (incl. underpowered) downgrades (ASM-0952) | §2.3 |
| κ counts span survival, ignores extraction correctness | P5b per-source-class extraction/type-assignment precision audit on the same blind sample (ASM-0952) | §2.3 |
| P6 name conflates derivation/rendering/consumption | renamed the oracle-delivery consumption probe; composite nature disclosed; read jointly with P5b (ASM-0952) | §2.3 |
| "byte-identical dense indexes within a band" contradictory | BM25 byte-identical; dense side pinned at logical-record tolerance + retrieval-equivalence threshold (ASM-0953) | §9 V3 |
| tool-execution success is not answer validity | flagged weakest menu item; licensed only with a stated mapping to answer type; signal named in every readout sentence (ASM-0955) | §5.2, §8.4 |
| broken "§2.5" self-reference | the programme's §2.5 statistical specification named in full (ASM-0950) | §7 |
| GR-A mislabelled "best generic system" after parity failure | that licence reassigned to GR-B/native; GR-A retains shared-lens comparator status only (ASM-0952) | §2.3 |
| open scope: full arm matrix vs "3–5 configs" arithmetic | the closed 11-config matrix enumerated; envelope re-derived from it; no silent caps (ASM-0956) | §10 |
| GR-C "SQLite or Datalog" is a design fork, query surface unpinned | SQLite pinned; fork closed; closed tool-call protocol, expressivity envelope, recursive-query semantics, kernel-op mapping table (ASM-0954) | §5.3 |
| GR-D learned verifier lacks training/split/calibration/leakage rules | full discipline pinned; one signal per instantiation, sweeps barred (ASM-0955) | §5.2 |
| "FlashRAG-class" is not an implementation pin | named default (FlashRAG) + release/commit recording + compatibility checklist + registered in-repo fallback (ASM-0953) | §3.3 |
| §8.3 worked example's evidence class unstated | formal-input/G2-only licence stated directly in §8.3, not merely inherited | §8.3 |

---

## 0. Contract: what RAGC is, and is not

RAGC/1 is the **executable specification of the matched generic-RAG/tool-use
control**: the arm inventory, derivation pipelines, retriever policy, budget and
parity rules, perturbation cells, readout semantics, and validation gates that
(1) put a conventional retrieval/tool-use system over the *same evidence* at the
*same budgets* beside every store-touching Programme-3 arm, and (2) let any
observed win be TESTED against a pinned ladder of system-level contrasts read
under the corrected attribution semantics of §7 — elimination evidence along the
axes of the six-way factorisation, NOT factorial causal identification
[STIPULATED: ASM-0920 contract; ASM-0950 corrected semantics, executing ASM-0812
cell (f) + ASM-0890/0891].

Why this control is the single strongest missing baseline, in the programme's own
measured terms:

- PREMISE: across the registry there are ZERO audited end-task wins over the
  kernel-as-text null attributable to kernel content; both value theses stand
  INCONCLUSIVE-PENDING [MEASURED: docs/next/feasibility-synthesis.md §0].
- PREMISE: the one audited end-task SIGN (f2b: 135M + kernel-verify-retry beats
  1.7B-alone by +0.1507 at ~10% cost) is provably consistent with "aligned answer
  key + retry": its verifier accepts iff the answer string-equals the canonical
  record while gold is DEFINED by that equality, and the shuffled control cannot
  discriminate content from alignment [MEASURED:
  registry/assessments/f2b-replicate.json does_not_license]. f2b had **no
  generic-RAG arm**: nothing measured distinguishes the kernel store from ANY
  typed store + retrieval + retry at matched budgets. RAGC exists to close
  exactly that gap [STIPULATED: ASM-0920].
- PREMISE: no published precedent exists for the cross-representation matched
  control — the five design rules (source-content derivation + information
  parity; identical-vs-architecture-specific retrievers; retrieved-token/context
  budgets + ordering; generator/tool-executor/retry-policy/tuning-compute parity;
  construction leakage + authoring effort) "must be designed and pre-registered
  by P3-D-RAGC itself; the literature supplies cells, not the control"
  [LIT-BACKED: RAG.md §6 rules 1–5 + §7.1, 28 sources fetched at primary venue
  2026-07-11].
- PREMISE: both measured NL crossings of the kernel front-end FAILED (l3a-parse
  47.6% retention; a5-nl 41.6% + the S2 dangerous-wrong kill) [MEASURED:
  registry/verdicts/l3a-parse.json + a5-nl.json]. Consequence here: the generic
  control consumes natural benchmark text NATIVELY and is never NLB-gated — the
  NL wall is the kernel side's cost; a control weakened to share it would fake
  the comparison (FRONT/1 §6's asymmetry rule applies to this control verbatim)
  [STIPULATED: ASM-0808 applied; ASM-0920].

What RAGC is NOT, with the owning design named:

| Not this | Owner |
|---|---|
| The frontier F(B_k), its builder pipeline S0–S6, T_k meter, envelope | P3-D-FRONTIER (FRONT/1) — RAGC's GR-A/GR-B arms are BUILT AND MEASURED by that pipeline; RAGC supplies their derivation + cell manifest (§8) |
| The five matched-retrieval RULES | FRONT/1 §5 (ASM-0853) — inherited verbatim below; RAGC refines only by registered amendment, never silently |
| The content-type control cells (a) derangement, (b) label permutation, (c) structurally-matched irrelevant records, (e) aligned-non-kernel store, (g) kernel-as-text null | MF0 §8.5 framework-owned; instantiated per consuming experiment. RAGC owns the retrieval-architecture axis + co-owns the executor axis (§5.3) |
| The index, dev split, analysis plan | P3-D-INDEX / MF0 §9 |
| The measurement rig | P3-D-HW |
| The G2→G3 oracle decomposition protocol | P3-D-ORACLE (the oracle-retrieval cell here is co-frozen with it, §5.4) |
| Any architecture family S | P3-D-VL/GNN/RULE/PS/DD/GU |

Gate placement under G1–G5 [STIPULATED: ASM-0920, consistent with ASM-0817]:
RAGC's parity diagnostics (§2.3) feed G1 (they are census-class, CPU/annotation
work, exempt from P3-E-CAL); the oracle-retrieval cell is a G2 `oracle-diagnostic`
instrument (ASM-0814 labelling, no W1 claim); the full GR arm set is MANDATORY at
every G4/W1-relevant experiment that uses a store (programme §1.4 condition 4);
nothing in RAGC waits on the NLB gate.

---

## 1. Objects: the control-arm inventory

### 1.1 Named arms

- DECISION: the matched control is not one arm but a **closed, named arm
  inventory**; every consuming prereg names which arms + perturbation cells it
  instantiates and what each discriminates (the named-cells rule, MF0 §8.5(1))
  [STIPULATED: ASM-0920]:

| Arm | Definition | Role | Claim licence (per §7 semantics) |
|---|---|---|---|
| **GR-A** shared/matched generic-RAG | Pinned standard-harness RAG over the SAME pinned source snapshot, the SAME retriever **algorithm + weights + configuration + build procedure** (Rule 2 SHARED cell: GR-A.bm25 + GR-A.dense sub-cells) — each representation necessarily builds its OWN hash-pinned index over its own objects (§3.1) — SAME budgets, SAME generator checkpoint + decoding as S | REQUIRED member of F(B_k) whenever S uses a store, AND the primary elimination control (FRONT/1 §5 Rule 2, ASM-0853) | bundle-level comparison at a fixed retrieval lens (§7); frontier membership; a W1 claim that has not beaten GR-A is void |
| **GR-B** native generic-RAG | Same snapshot + budgets; the builder's best in-budget retriever/index configuration for a conventional RAG system (FRONT/1 §2.3(b) NATIVE cell) | additional F(B_k) point | "the best a conventional RAG can do on this evidence at this budget" — never replaces GR-A; this licence lives HERE, not on GR-A (§2.3) |
| **GR-C** generic tool-use / generic-executor | Same snapshot derived into tool schemas + one pinned generic deterministic executor (SQLite, pinned; the fork is closed — §5.3) called via function-calling by the same generator | executor-axis cell (MF0 §8.5 "generic-executor substitution", frozen here; absorbs the round-1 A.1 generic-Datalog attribution control) | kernel bundle vs generic-deterministic-execution bundle over the same typed content (§7) |
| **GR-D** matched retry/search | GR-A.bm25 (default; §10) wrapped in the SAME retry loop shape as S — same max-k, same abstention accounting — with ONE named GENERIC acceptance signal (§5.2) | retry/search-axis cell | verify-retry SHAPE + generic signal vs the kernel-verifier bundle (the f2b de-confound, §8.4) |
| **R0** retrieval-off | The same generator, no store, no retrieval, matched decoding | floor for Δ-retrieval | what the parametric model alone does |

Perturbation sub-cells, attachable to GR-A (and to S symmetrically where
meaningful) [STIPULATED: ASM-0920; cells supplied by the lit review]:

| Cell | Definition | Kills / discriminates |
|---|---|---|
| **PS** position-shuffle | gold-context position randomised vs the pinned score-descending order | context-position confound [LIT-BACKED: RAG.md §6.4, Lost-in-the-Middle] |
| **RD** random-document | retrieved slots filled with seed-pinned random documents | prompt-perturbation reading of any "retrieval win"; a CONTROL, never a tuning opportunity [LIT-BACKED: RAG.md §6.5 + §7.7, Power-of-Noise] |
| **OR** oracle-retrieval | gold object injected (retrieval bypassed) | retrieval-vs-generation attribution ceiling; G2 `oracle-diagnostic` ONLY, never F(B_k), no W1 claim [STIPULATED: ASM-0814 applied] |

### 1.2 Scale and generators

- DECISION: RAGC generators are the rung anchors and their admissible F(B_k)
  companions (R-1 = SmolLM2-135M-class, R-2 = 360M-class, R-3 = 1.7B-class,
  pinned name+revision by P3-D-BASE); every arm above is specified to run
  unchanged across the 100M–2B span, with all per-rung constants (budgets,
  k, token caps) pinned per rung at the consuming experiment's prereg freeze.
  Note the §2.2 admissibility arithmetic: a STORE-BEARING arm at rung k
  necessarily runs a sub-anchor generator [STIPULATED: ASM-0920; ASM-0951].

---

## 2. Rule 1 executed — source-content derivation + the information-parity instrument

FRONT/1 §5 Rule 1 (one pinned snapshot; pinned seed-pinned derivation scripts;
four measured parity checks; effort disclosure; the residual honesty line) is
inherited verbatim [STIPULATED: ASM-0853 inherited]. RAGC's job is to make the
derivations and the parity measurement EXECUTABLE.

### 2.1 The derivation matrix

- DECISION: one pinned **derivation matrix D** per vertical/corpus: rows =
  representations, columns = {script + version hash, object grammar, packed-bytes
  cap, build-compute ledger key}. The four standing rows [STIPULATED: ASM-0921]:

| Representation | Derivation (pinned, seed-pinned, content-hashed) | Indexed object |
|---|---|---|
| **kernel records** | the standing mint/authoring pipeline at its pinned version (the encoder content-hash pin discipline applies) | kot-axiom/world records |
| **passages** | pinned chunker: proposed default 256 tokens/chunk, stride 128, sentence-boundary snapping; chunk params are TUNABLE on the dev split within the arm's T_k meter, then pinned — best-effort control, not arbitrary default | text chunks |
| **triples** | structure-grounded sources (code, schemas, tables): a DETERMINISTIC extractor (the measured a5 route — typed world from code structure, no LLM [MEASURED: registry/verdicts/a5.json]); prose sources: one pinned open IE extractor, name+revision hashed, extraction compute booked | (s, p, o, provenance-span) |
| **tool schemas** | deterministic generator mapping the derived typed schema → JSON function signatures per the closed §5.3 protocol over the GR-C generic store | callable tool definitions + docstrings |

- DECISION: every derivation consumes the identical snapshot (content hash), no
  arm-specific extra sources; every derivation's outputs pass the same
  decontamination screen; human curation hours inside any derivation are logged
  to KOT-LIFE/1 and disclosed (FRONT/1 Rule 1 checks (a)/(c)/(d), inherited)
  [STIPULATED: ASM-0853 inherited; ASM-0921].

### 2.2 Byte accounting under TOTAL-SYSTEM admissibility (corrected)

Revision 1 imposed equal store caps without deriving them from the rung's total
deployment budget; the review is right that equal caps alone cannot establish
KOT-FAIR/2 admissibility. Corrected mechanics [STIPULATED: ASM-0951, superseding
the byte-cap clause of ASM-0921]:

- DECISION: **admissibility is total-system first.** Every arm's complete packed
  artifact set — generator checkpoint + tokenizer + store objects + index
  structures + embedder weights + verifier weights + executor binary beyond the
  frozen base image + serialisers/adapters — must fit `B_k.bytes_max` under the
  ONE KOT-SIZE/2 canonical packing script (figure-1), warm and cold per FRONT/1
  §1 [STIPULATED: ASM-0951].
- DECISION: **the equal store cap is DERIVED, never free-standing:**
  `store_bytes(B_k) := B_k.bytes_max − max over compared arms of (that arm's
  non-store packed bytes)`. Every compared arm receives the same derived cap —
  equal cap, not forced-equal usage; an arm under the cap may NOT bank the slack
  into any other resource [STIPULATED: ASM-0951, executing ASM-0853 check (b)].
- Consequence, stated openly because revision 1 hid it: `B_k` is anchor-derived
  (`bytes_max` = the anchor's own packed bytes, FRONT/1 §1.2), so an anchor-sized
  generator plus ANY nonzero store/index is arithmetically inadmissible at its
  own rung. A store-bearing arm at rung k therefore necessarily runs a
  sub-anchor generator — exactly the measured f2b shape (135M generator + store,
  admissible against the 1.7B anchor's budget, never against the 135M anchor's
  own) [STIPULATED: ASM-0951].

### 2.3 The information-parity instrument (the falsifiable piece, statistics corrected)

Parity beyond FRONT/1's four checks cannot be certified — converting one snapshot
into different object types changes the retrieval problem itself (the standing
limitation, carried verbatim on every consuming claim) [STIPULATED: ASM-0853
inherited]. But it CAN be measured further than the four checks do, and the
measurement is cheap. RAGC adds three pre-registered **parity diagnostics**:

- DECISION: **P5 — decisive-span coverage per arm.** On a blind, power-sized
  sample of the consuming experiment's dev items (n from P3-D-POWER arithmetic,
  never fixed a priori), annotators mark the snapshot span(s) decisive for each
  item; for each arm, κ_arm = fraction of sampled items whose decisive span
  survives into ≥1 of that arm's indexed objects (string/provenance containment,
  mechanically checked). Deliverable: the per-arm κ vector — which is
  simultaneously the G1 census input for the generic arms (the same κ that
  P3-D-POWER's Δ_max needs, so the annotation is bought once)
  [STIPULATED: ASM-0921].
- DECISION: **P5b — per-source-class precision audit (new in revision 2).** κ
  measures provenance-span SURVIVAL, not semantic correctness: an incorrectly
  derived object pointing at the right span would count as covered. On the same
  blind sample, annotators audit each arm's derived objects for extraction and
  type-assignment correctness, reported PER SOURCE CLASS (code / schema / prose)
  — the round-1 B.2.2 census requirement, executed here. An incorrect object
  over the right span is a precision failure, never coverage
  [STIPULATED: ASM-0952].
- DECISION: **P6 — oracle-delivery consumption probe** (revision-1 name
  "answerable-fraction" withdrawn as overclaiming). With retrieval bypassed (OR
  cell), deliver each arm's own derived object containing the gold span to the
  same generator; a_arm = generator task accuracy on the sampled items. a_arm is
  a COMPOSITE of derivation correctness × representation rendering × generator
  consumption — it is read jointly with P5b (which isolates the
  derivation-correctness leg), never as a single-factor number. It bounds how
  much of any end-task gap is representation-side rather than retrieval-side.
  `oracle-diagnostic` labelled, G2-class, no W1 claim
  [STIPULATED: ASM-0952; ASM-0814 applied].
- DECISION: **the parity band as a paired EQUIVALENCE test + fail-closed
  downgrade.** A consuming prereg pins ε_par (proposed default 0.05 absolute on
  κ; maintainer-adjustable at freeze). Parity HOLDS only if a paired
  TOST/non-inferiority procedure shows |κ_S − κ_GR| within ε_par with the 90%
  CI inside the band (programme §2.5 machinery; the revision-1 observed-difference
  rule without uncertainty is withdrawn). FAILURE TO PROVE equivalence —
  including an underpowered sample — triggers the downgrade: the attribution
  sentence licensed by that comparison is DOWNGRADED to "confounded by
  derivation coverage" in the verdict. What survives a parity failure: GR-A
  remains a measured comparator under the shared lens and an F(B_k) member;
  the "best generic system built on this evidence" licence belongs to
  **GR-B/native**, which is unaffected. No silent pass
  [STIPULATED: ASM-0952, superseding the parity clause of ASM-0921].

### 2.4 The anti-weak-control channel (threat model, this design's mirror of weak-builder gaming)

The party building S also derives S's control — an under-built generic arm
manufactures fake kernel-semantics attribution, exactly as an under-searched
frontier manufactures a fake W1 (FRONT/1 §7.3's channel, mirrored on the control
side). Counters [STIPULATED: ASM-0922, extending the ASM-0812 threat model]:

1. GR-A/GR-B are built and tuned by the FRONT/1 pipeline under the SAME T_k
   meter and fixed selection rule as every comparator — the control's strength
   is bought with the same metered budget as S's tuning, never less.
2. The pinned standard harness (§3.3) supplies the community's default recipes;
   deviating BELOW harness defaults requires a logged reason.
3. FRONT/1's nomination window + F-CAL A4 challenger gate apply to the GR arms
   as F(B_k) members — outsiders can strengthen the control we would be tempted
   to weaken.
4. Full derivation + build logs published (no-silent-caps applied to the
   control's construction).

---

## 3. Rule 2 executed — the retriever decision table

FRONT/1 §5 Rule 2 (SHARED/MATCHED cell required in F(B_k) + W1 control set;
NATIVE cell additional; disclosed handicap, never exclusion) is inherited
verbatim [STIPULATED: ASM-0853 inherited]. RAGC pins the mechanics:

### 3.1 The shared retriever, and what "same retriever over different objects" can and cannot mean

- Corrected statement of the shared cell (revision 2): a literally "same index"
  over different object sets is technically impossible — each representation
  necessarily produces its own index. What the shared cell SHARES is the
  retriever **algorithm, weights, configuration, and build procedure**; what
  differs, necessarily and disclosed, is the per-arm index built over that arm's
  own objects, each index hash-pinned in the manifest [STIPULATED: ASM-0952].
- DECISION: the shared cell's retriever pair is **BM25 + one pinned small dense
  embedder** (name+revision hashed at freeze; embedder weights + index bytes
  charged inside the arm's §2.2 total-system accounting), run over a **pinned
  common text serialisation** of every arm's objects: kernel records via the
  existing deterministic renderer/desugaring path; triples as canonical
  subject–predicate–object sentences; tool schemas as their docstrings; passages
  as themselves. The serialiser is deterministic, versioned, content-hashed —
  the shared cell compares CONTENT REPRESENTATIONS under one fixed retrieval
  lens, which is exactly its claim licence [STIPULATED: ASM-0922; ASM-0952].
  BM25 is mandatory in every instantiation — a structured-store win that never
  ran the lexical baseline is unattributed [LIT-BACKED: RAG.md §6.2 (BEIR,
  arXiv:2104.08663, NeurIPS 2021)].
- DECISION: the per-cell identical-vs-native decision (the MF0 §8.2(iii)
  delegation) is closed as a fixed table, not per-experiment judgement
  [STIPULATED: ASM-0922]:

| Comparison being made | Retriever policy |
|---|---|
| bundle comparison at a fixed lens (GR-A vs S-serialised) | SHARED (BM25 + pinned dense procedure), both arms; per-arm indexes hash-pinned |
| frontier: strongest conventional system (GR-B) | NATIVE — builder's best in-budget choice, tuned within T_k |
| executor axis (GR-C vs S) | SHARED addressing where S's addressing is retrieval-like; else the tool-call interface IS the addressing and is measured as such, disclosed |
| retry axis (GR-D vs S) | inherit whichever cell GR-D wraps |

- Disclosure rule: where the shared lens structurally handicaps an arm whose
  native retrieval operates over different objects (kernel addressing most of
  all), the handicap is stated beside the result and the NATIVE cell carries the
  strongest-system reading — never grounds to drop the shared cell (FRONT/1
  Rule 2 corrected form, inherited) [STIPULATED: ASM-0853 inherited].

### 3.2 Retrieval metrics, separated from end-task metrics

- DECISION: every arm reports retrieval recall@k against gold provenance (where
  the P5 annotation supplies gold spans) SEPARATELY from end-task accuracy —
  retrieval quality and generation quality move independently and attribution
  requires both readouts [LIT-BACKED: RAG.md §6.3 (FiD, arXiv:2007.01282,
  EACL 2021); STIPULATED: ASM-0922].

### 3.3 The harness pin (corrected: a class is not a pin)

- DECISION: the proposed default pinned harness is **FlashRAG** by name. At
  P3-T-RAGC-IMPL start, the implementer records the exact release tag + commit
  hash and runs the compatibility checklist: (i) BM25 supported; (ii) the pinned
  dense embedder supported; (iii) 135M-class checkpoint hosting works on the
  pinned stack; (iv) deterministic seeding verified. Any failing item routes to
  the REGISTERED FALLBACK: a minimal in-repo retrieval+assembly harness
  (retrieval, budget enforcement, prompt assembly only — no method zoo),
  disclosed in the manifest. Either way, the manifest pin is the recorded
  release/commit or the in-repo harness hash — "FlashRAG-class" is no longer a
  pin. The v1/v2 method-count discrepancy is the standing lesson that un-pinned
  harness versions corrupt comparability [LIT-BACKED: RAG.md §3, FlashRAG v2
  abstract re-fetched 2026-07-11; STIPULATED: ASM-0953, superseding the harness
  clause of ASM-0922].

---

## 4. Rule 3 executed — retrieved-token/context budgets + ordering

FRONT/1 §5 Rule 3 (pinned max retrieved tokens per query identical across arms;
max context length; score-descending assembly; no hand-placement at context
edges) is inherited verbatim [STIPULATED: ASM-0853 inherited]. RAGC pins:

- DECISION: per rung, ONE retrieved-token budget `ret_tok(B_k)` and ONE context
  cap for every arm including S; k (objects retrieved) floats per arm to fill
  the SAME token budget — matching tokens, not object counts, because objects
  differ in size across representations by construction [STIPULATED: ASM-0923].
- DECISION: assembly order = retrieval-score-descending for every arm; the PS
  cell (§1.1) is the pre-registered order perturbation; its seed is pinned
  [STIPULATED: ASM-0923; the position confound is measured art, LIT-BACKED:
  RAG.md §6.4].
- DECISION: the RD cell fills the same token budget with seed-pinned random
  snapshot documents; RD is read as a control ONLY (if GR-A − RD ≈ 0, the
  "retrieval win" is a prompt-perturbation effect and the retrieval attribution
  is void at that scope); tuning toward RD-style noise injection is prohibited
  [STIPULATED: ASM-0923; LIT-BACKED: RAG.md §7.7].
- DECISION: cross-reference for token-parity with the content-type axis: the
  kernel-as-text null (cell (g), owner MF0 §8.5) runs at the SAME `ret_tok(B_k)`
  budget, so the null, the generic control, and S are token-commensurable in
  one experiment [STIPULATED: ASM-0923].

---

## 5. Rule 4 executed — generator / executor / retry / tuning parity

FRONT/1 §5 Rule 4 (identical generator checkpoint, decoding, retry budget,
abstention accounting, executor semantics for store-vs-store comparisons;
free-corpus/whole-system arms exempt with the narrower licence) is inherited
verbatim [STIPULATED: ASM-0853 inherited]. RAGC makes the retry and executor
sides concrete — they are where the f2b confound lives.

### 5.1 Generator parity

- DECISION: for every bundle comparison (GR-A/GR-C/GR-D/R0/perturbation
  cells vs S): same generator checkpoint (hash), same decoding parameters, same
  max-token + stop discipline, same abstention token semantics, same prompt
  template SKELETON with only the evidence slot varying (template pinned,
  per-arm evidence rendering pinned by §3.1's serialisers)
  [STIPULATED: ASM-0924].

### 5.2 Retry-policy parity (GR-D — the f2b de-confound generalised, discipline closed)

The measured sign the programme owns is a verify-RETRY loop; its assessment says
the shuffled control cannot separate content from alignment [MEASURED:
registry/assessments/f2b-replicate.json]. The generic control must therefore
match the LOOP, not just the store:

- DECISION: GR-D wraps a generic arm in S's exact loop shape — same max-k
  retries, same per-retry prompt-mutation rule, same abstain-on-exhaustion —
  with **exactly ONE generic acceptance signal per instantiation**, named in the
  consuming prereg; signal SWEEPS are tuning and are barred. The pinned menu the
  prereg chooses from [STIPULATED: ASM-0924 menu; ASM-0955 discipline]:
  (i) self-consistency agreement at a pinned threshold (SA-class components
  only, per FRONT/1 §4.2 semantics); (ii) a small learned outcome verifier
  (Cobbe-direction, auto-labels only [LIT-BACKED: RAG.md §5 (Cobbe
  arXiv:2110.14168, 2021; Math-Shepherd ACL 2024 auto-label recipe)]) under the
  full discipline below; (iii) tool-execution success — flagged the WEAKEST
  menu item — where the vertical has an executable surface (GR-C's executor as
  the checker).
- DECISION: **learned-verifier discipline** (closes the review's training-data /
  split / calibration / leakage gap) [STIPULATED: ASM-0955]: trained ONLY on
  the construction split (disjoint from dev-eval and the frozen suite under the
  P3-D-INDEX split scheme); auto-labels only, never human answer keys;
  calibration reported on a held-out construction fold (reliability curve +
  ECE); verifier bytes inside the §2.2 total-system cap and training compute
  inside T_k; supervision-leakage rule: the verifier never sees frozen-suite
  items, their gold labels, or S's kernel records.
- DECISION: **execution-success caveat**: tool-execution success is NOT in
  general an answer-validity signal — it can accept a syntactically valid but
  semantically irrelevant call. It is licensed only where the executed check
  mechanically resolves the task's answer type; the prereg states that mapping
  explicitly, and every readout sentence names the signal in use. GR-D and S
  co-report acceptance and abstention rates (an accept-everything verifier
  trivially matches loop shape and must be visible) [STIPULATED: ASM-0955].
- DECISION: the readout is the pair (S − GR-D) and (GR-D − GR-A), read under §7
  semantics: the first is the kernel-verifier BUNDLE against a generic
  acceptance signal in the same loop (verifier information, error profile,
  calibration, and acceptance rate all co-vary — no single-factor sentence);
  the second prices the loop shape itself [STIPULATED: ASM-0924; ASM-0950].

### 5.3 Executor parity (GR-C — the generic-executor cell, closed to an executable spec)

- DECISION: the MF0 §8.5 executor-axis draft cells are frozen here as:
  **engine-off** (S's store retrieved, execution disabled — owned by the
  consuming experiment, listed for completeness) and **GR-C generic-executor
  substitution**, now fully pinned [STIPULATED: ASM-0954, superseding the GR-C
  clause of ASM-0924; absorbs round-1 A.1's mandatory generic-Datalog
  attribution cell as the SQLite instantiation]:
  - **Engine:** SQLite, version-pinned, single pinned build. The revision-1
    "SQLite or a pinned Datalog engine" fork is CLOSED; reopening it is a
    registered amendment + manifest version bump.
  - **Query surface:** the generator NEVER writes SQL. The only surface is the
    closed tool-call protocol over the D tool-schema row:
    `lookup(entity, relation)`, `neighbors(entity)`,
    `check(claim_triple) → {true, false, unknown}`,
    `path(a, b, max_depth)` bounded reachability — with pinned max tool calls
    per query, per-call timeout, total wall-clock, error surface (§5.4), and
    deterministic result ordering on canonical keys.
  - **Expressivity envelope:** conjunctive queries + bounded transitive closure
    (recursive CTE with pinned max depth and row cap; semantics = SQLite's
    recursive-CTE evaluation under those limits, documented in the manifest);
    no negation beyond `check()`'s closed-world `unknown`.
  - **Kernel-op mapping table:** the manifest pins a table mapping every
    kernel-engine operation S exercises at that scope to its GR-C tool + SQL
    template, or to an explicit NOT-EXPRESSIBLE row. An S run exercising an
    unmapped operation VOIDS the S − GR-C elimination reading at that scope —
    disclosed, fail-closed.
  Tool-call syntax errors, timeouts, and refusals are accounted identically to
  S's engine errors. If S ≈ GR-C on the covered slice, the kernel bundle's
  distinctive contribution beyond generic deterministic execution over the same
  typed content is dead at that scope — K-P3v2(4)'s attribution-collapse input
  at the executor axis, an ELIMINATION reading per §7 [STIPULATED: ASM-0954;
  ASM-0950].

### 5.4 Tool-executor semantics + the oracle cell

- DECISION: sandbox, timeout, retry-on-tool-error, and error-message surface are
  pinned identically for every executor-bearing arm (S's engine, GR-C, any
  tool-use comparator); the OR oracle-retrieval cell is co-frozen with
  P3-D-ORACLE so the G2→G3 decomposition and this control use one instrument,
  not two [STIPULATED: ASM-0924].

### 5.5 Tuning parity

- DECISION: tuning-compute parity is NOT re-specified here — it binds through
  FRONT/1 §3.3's T_k resource-vector meter and arm table (the GR arms are arm
  keys C3-RAG-matched / C3-RAG-free already); GR-C and GR-D each get ONE arm-key
  addition to the arm table at rung entry (a frontier version-bump event if
  added later, per FRONT/1's closed-arm-table rule) [STIPULATED: ASM-0852
  consumed; ASM-0924].

---

## 6. Rule 5 executed — construction leakage + authoring effort

FRONT/1 §5 Rule 5 (every construction pass booked to KOT-LIFE/1 + KOT-SIZE/2 on
every arm identically; derivation pipelines frozen before any frozen-suite item
is drawn; screen applies to construction inputs and outputs; post-exposure
construction VOID for W1) is inherited verbatim [STIPULATED: ASM-0853 inherited].
RAGC adds the per-arm ledger table as the executable artifact:

- DECISION: every instantiation publishes one **build-ledger row per arm**:
  {derivation script hash, derivation CPU/GPU compute, human hours, index build
  compute, embedder training/selection compute (TinyAgent-DeBERTa-class
  selectors included [LIT-BACKED: RAG.md §1 (TinyAgent, arXiv:2409.00608,
  EMNLP 2024)]), packed object bytes, index bytes,
  screen result hash, freeze timestamp vs suite-exposure timestamp} — the
  literature's silent asymmetry (dense index ≈ free embed pass; graph/store
  build ≈ full sweep) becomes an explicit line item on BOTH sides
  [LIT-BACKED: RAG.md §3 (accounting-practice table, sources 2020–2025);
  STIPULATED: ASM-0925]. Build-ledger rows are necessary but NOT sufficient for
  admissibility — the §2.2 total-system check and the §8.1 KOT-SIZE/2 +
  KOT-COST/2 vectors are what close it [STIPULATED: ASM-0951].
- DECISION: kernel-store authoring hours (explicator work) appear on S's row of
  the SAME table — the control's fairness cuts both ways; no arm's construction
  is free [STIPULATED: ASM-0925].

---

## 7. The readout: system-level contrasts under corrected attribution semantics

Revision 1 claimed this ladder "operationalised the six-way attribution
factorisation" as if the pairwise cells achieved factorial identification. The
review is right that they do not: every contrast below changes MULTIPLE factors
at once, no contrast isolates the INTEGRATION factor, and no interactions are
estimated. Corrected semantics [STIPULATED: ASM-0950, superseding the
attribution reading of ASM-0926; ASM-0926's cell inventory, reporting
requirements, and kill wiring remain]:

- DECISION: each contrast licenses exactly two sentence shapes
  [STIPULATED: ASM-0950]:
  1. **ELIMINATION** (the contrast ≈ 0 or S loses): "nothing distinctive about
     the kernel bundle survives against this generic bundle at matched budgets
     at this scope." This is the K-P3v2(4) direction and needs NO factor
     isolation — it is the control's kill power and it is intact.
  2. **BOUNDED DIFFERENCE** (S wins): "S beats this specific generic bundle by
     Δ; the gap is attributable only to the FULL SET of factors that differ
     between the two systems, enumerated in the table below." NO pairwise
     contrast licenses a single-factor causal sentence ("the kernel ENGINE
     caused Δ"); single-factor attribution would require a factorial design
     with interaction estimation — out of scope for RAGC/1, priced only as a
     registered follow-up if a bounded-difference result ever warrants it.
- DECISION: the integration factor of the six-way factorisation is isolated by
  NO RAGC cell; every readout carries it as an explicitly unattributed residual
  line [STIPULATED: ASM-0950].

The contrast ladder, with the co-varying bundle stated honestly per row
[STIPULATED: ASM-0926 inventory; ASM-0950 semantics]:

| Contrast | Bundle that differs (ALL co-vary; none isolated) | If ≈ 0 (elimination licence) |
|---|---|---|
| S − cell (g) kernel-as-text | store machinery + retrieval path vs plain conditioning | machinery adds nothing over text at matched tokens |
| S − cell (e) aligned-non-kernel | kernel semantics + record grammar vs typed store (our own instrument; no published precedent — carries the load alone [LIT-BACKED: RAG.md §6 closing]) | "NSM semantics" attribution dead; "typed store + checker" reading stands |
| S − GR-A | derived representation, index contents, evidence rendering, interface, execution path | the win is available to a conventional RAG bundle → K-P3v2(4) input |
| GR-A − R0 | presence of retrieval + evidence | the evidence isn't doing anything retrievable |
| GR-A − RD | retrieved-content RELEVANCE vs prompt perturbation | "retrieval win" was noise-shaped |
| S − GR-C | engine, query surface, tool schema, expressivity (bounded by the §5.3 mapping table) | kernel bundle adds nothing over generic deterministic execution on the same typed content (§5.3) |
| S − GR-D | verifier information, error profile, calibration, acceptance rate | the f2b-shape win is loop-generic (§8.4's kill) |
| GR-D − GR-A | the retry/search loop shape + acceptance signal | the loop shape isn't the lever |

- DECISION: reporting requirements on every instantiation: (1) the full contrast
  vector for the named cells, never the headline alone; (2) covered-vs-uncovered
  split wherever a store is in play (ASM-0811's standing vector rule);
  (3) long-tail/popularity-stratified readout where the vertical admits a
  popularity proxy — unstratified averages hide whether the store or parametric
  memory answered [LIT-BACKED: RAG.md §6.6 (Mallen, arXiv:2212.10511,
  ACL 2023)]; (4) retrieval recall@k
  reported beside every end-task figure (§3.2); (5) each sentence in the verdict
  names the cell that licenses it AND stays inside the §7 sentence shapes
  (FRONT/1 Rule 2's licence discipline, generalised) [STIPULATED: ASM-0926;
  ASM-0950].
- DECISION: K-P3v2(4) wiring, verbatim: "every measured family gain vanishes
  against the matched generic-store / generic-RAG controls" is evaluated on the
  S − GR-A and S − GR-C contrasts under the programme's **§2.5 statistical
  specification** (docs/next/programme-3-neurosymbolic-architecture.md §2.5:
  LCB-vs-margin, FWER across the instantiated contrast set, hierarchical
  bootstrap preserving paired predictions), consumed via P3-D-INDEX's analysis
  plan — RAGC supplies the cells; the analysis plan supplies the test. (The
  revision-1 self-reference "§2.5 house statistics" pointed at a section this
  document does not have; corrected.) [STIPULATED: ASM-0926, consuming
  ASM-0813; ASM-0950].

---

## 8. The executable interface: what a consuming experiment and FRONT/1 receive

### 8.1 The control-arm manifest (the plug-in object)

- DECISION: RAGC's implementation (P3-T-RAGC-IMPL, §11) emits per
  vertical × rung one content-hashed **control-arm manifest**:
  `{snapshot_hash, derivation_matrix: D rows with script hashes, object hashes
  and byte counts, serialiser hashes, retriever pins (BM25 config, dense
  embedder name+revision), per-arm index hashes, harness release/commit pin (or
  fallback-harness hash, §3.3), ret_tok(B_k), context cap, ordering rule with
  PS/RD seeds, generator pin and decoding params, GR-C executor pin +
  tool-schema hash + kernel-op mapping table (§5.3), GR-D loop params +
  the one named acceptance signal (+ verifier training/calibration artifacts
  where signal (ii) is chosen), build-ledger rows, parity diagnostics (κ vector
  with equivalence CIs, P5b precision table, a vector, ε_par), screen results}`
  [STIPULATED: ASM-0927; ASM-0954; ASM-0955].
- DECISION: **the measurement contract (new in revision 2):** the manifest
  additionally carries, for EVERY arm including GR-C and GR-D, (i) the complete
  **KOT-SIZE/2 six-figure report** and (ii) the **measured KOT-COST/2 vector**
  — p95 latency, energy under the FRONT/1 §1.1 boundary rule (reported or
  MISSING, never modeled), peak accelerator memory + host RSS, I/O, warm and
  cold — produced under the P3-D-HW rig protocol (by FRONT/1 S3 for F(B_k)
  members; by the same rig protocol, booked here, for non-frontier cells).
  Build-ledger rows alone do not satisfy this [STIPULATED: ASM-0951].
- DECISION: consumption contract [STIPULATED: ASM-0927]:
  - **FRONT/1** consumes the manifest at S0 (GR-A/GR-B enter the candidate
    lattice as the C3-matched cells with their derivations already pinned) and
    measures/pins them through S1–S6 like any comparator — RAGC never runs its
    own frontier measurement;
  - **every store-touching [EXP]** consumes the manifest at prereg freeze: the
    prereg names instantiated arms/cells, discrimination claims, ε_par, and the
    contrast set; a store-touching G4 prereg that lacks the manifest hash does
    not freeze (fail-closed);
  - amendments to any inherited FRONT/1 §5 rule go through a registered
    amendment + manifest version bump — never silently (ASM-0853's clause).

### 8.2 Per-experiment instantiation checklist (what the prereg must name)

1. Vertical + snapshot hash; 2. arms + cells instantiated, each with its
discrimination claim in the §7 sentence shapes; 3. budgets (the §2.2 derived
store cap, ret_tok, context cap, retry k); 4. retriever cells (GR-A.bm25
mandatory; GR-A.dense; GR-B config); 5. GR-D's ONE named acceptance signal +
its answer-type mapping; 6. ε_par + the parity-diagnostic sample size from
P3-D-POWER; 7. the contrast set + its FWER family; 8. which contrasts feed
K-P3v2(4) [STIPULATED: ASM-0927; ASM-0955].

### 8.3 Worked example (design-level; the first instantiation target)

The shape inherited from round-1 (the W1 hypergraph's source-parity two-arm
design, salvaged to this bead) applied to the programme's two existing verticals
[STIPULATED: ASM-0927]:

- Snapshot: the a5 vertical's pinned source repository (code + docs), the same
  material the measured world layer was deterministically extracted from
  [MEASURED: registry/verdicts/a5.json 855/855 on that substrate].
- D rows: kernel records = the existing a5 world layer (already extant, hash
  pinned); passages = chunked source/docs; triples = the deterministic code
  extractor's output re-serialised; tool schemas = the §5.3 closed protocol over
  the triple store in SQLite.
- Arms: GR-A/GR-C/GR-D/R0 + PS/RD/OR cells; generator = the f2b 135M host;
  GR-D acceptance = GR-C `check()` execution success (the vertical is
  executable; §5.2's weakest-item caveat disclosed).
- What it buys: the missing generic-RAG/generic-executor/generic-retry arms for
  the ONLY measured end-task sign — the f2b de-confound the assessment says is
  required before the +0.1507 licenses anything [MEASURED:
  registry/assessments/f2b-replicate.json]. This instantiation is the natural
  first consumer bead (P3-E-VL-1's comparator set names these cells already,
  programme §3.1).
- **Evidence-class licence, stated directly (not merely inherited):** this
  worked example is **formal-input, G2-class evidence only**. Its queries are
  canonical/formal-slice items; the kernel side has NOT passed the NL boundary
  (both measured crossings FAILED — l3a-parse 47.6% retention, a5-nl 41.6% +
  the S2 kill [MEASURED: registry/verdicts/l3a-parse.json + a5-nl.json]). A
  decisive result here de-confounds the existing formal-slice +0.1507; it
  licenses NOTHING about real-input/deployment usefulness until the kernel side
  passes the NLB gate. This sentence rides every readout of this instantiation
  verbatim [STIPULATED: ASM-0957; ASM-0814/0808 applied].

### 8.4 The first decisive experiment, pre-specified (the f2b de-confound — new in revision 2)

RAGC-CAL (§9) validates the INSTRUMENT; it is not the decisive test of the
baseline's central scientific question. The review is right that the f2b
de-confound needs its own frozen contrast, margin, kill rule, power target, and
spend stop — pre-specified here at design level, frozen at the consuming prereg
(P3-E-RAGC-F2B or P3-E-VL-1), adjustable before freeze only by registered
amendment [STIPULATED: ASM-0957]:

- **Primary contrast:** paired Δ = acc(S) − acc(GR-D) on the frozen f2b eval
  slice; S = the measured f2b configuration (135M + kernel-verify-retry)
  rebuilt under this manifest; GR-D = the same generator + identical loop shape
  with acceptance = GR-C `check(claim_triple)` execution success (the one named
  signal; residual alignment risk disclosed — it is exactly the channel the
  content-type shuffled cells read).
- **Decision rule** (programme §2.5 machinery; FWER over the named family):
  - **KILL:** TOST equivalence — |Δ| within δ_eq = 0.05 absolute (90% CI inside
    the band). Verbatim kill sentence: *"the audited f2b gain is reproduced by
    a matched generic store + generic acceptance signal in the same retry loop;
    no kernel-content attribution survives on this vertical."* Feeds K-P3v2(4)
    at the retry axis.
  - **SURVIVE:** LCB95(Δ) > δ_sup = 0.05 — the kernel-verifier bundle adds
    something beyond this generic signal on the formal slice (a §7
    bounded-difference sentence, G2/formal-only).
  - **Neither:** INCONCLUSIVE-UNDERPOWERED, disclosed; no attribution sentence
    in either direction.
- **Power target:** n sized by P3-D-POWER to ≥ 0.90 power for Δ = 0.10
  (two-thirds of the measured +0.1507) under the paired analysis and the
  realised FWER family; if the frozen slice cannot support it, the item set is
  enlarged BEFORE freeze or the experiment does not freeze.
- **Spend stop:** worst-case ≤ ~4 GPU-h at R-1 (inside the free pool, within
  the §10 envelope); exhaustion before the primary readout = scientific stop +
  salvage per house rules, no retry.
- **Secondary contrasts** (same FWER family, reported never headlined):
  GR-D − GR-A (loop pricing), S − GR-A, S − GR-C.
- **Scope licence:** the §8.3 formal-input/G2-only sentence, carried verbatim.

---

## 9. Validation gates (RAGC-CAL) — the control is an instrument and gets instrument gates

RAGC-CAL validates that the instrument WORKS; the decisive science lives in
§8.4. Pre-registered acceptance tests, co-scheduled with P3-E-FCAL/P3-E-CAL
(same free-pool calibration campaign) [STIPULATED: ASM-0927; ASM-0953]:

- **V1 — harness reproduction (plumbing):** the pinned harness (named
  release/commit per §3.3, or the in-repo fallback) reproduces one published
  method×dataset figure from its own documentation within a pre-registered
  tolerance (fallback harness: reproduces a pinned BM25 reference run instead).
  Catches tooling breakage, not weakness.
- **V2 — discrimination sanity (per vertical × rung; corrected):** the gate is
  the single preregistered contrast **LCB95(OR − R0) > 0** on a
  knowledge-intensive dev slice (paired, programme §2.5 machinery). The
  revision-1 ordering invariant "OR ≥ GR-A ≥ R0" is WITHDRAWN as an instrument
  invariant — relevant retrieval can hurt generation, and oracle delivery can
  underperform retrieved context through representation/context effects;
  orderings among {OR, GR-A, R0} are REPORTED with CIs as diagnostics, never
  gated. If the gate fails, the vertical's dev slice cannot discriminate
  evidence use at all and every RAGC contrast on it is uninformative — the
  instantiation is blocked there, disclosed, not fudged
  [STIPULATED: ASM-0953].
- **V3 — build repeatability (corrected):** two independent derivation+index
  builds (same seeds): (a) BM25 indexes byte-identical; (b) dense side at the
  LOGICAL-RECORD level — embedding vectors reproduce within a pinned numeric
  tolerance in the canonical dump — plus (c) a pinned retrieval-equivalence
  threshold (top-k overlap on a pinned probe query set). Byte-identical ANN
  artifacts are NOT required (multithreaded/ANN builds are not byte-stable;
  demanding it was contradictory). The manifest is re-derivable from pins alone
  [STIPULATED: ASM-0953].
- **V4 — parity diagnostics in band:** §2.3's κ (with equivalence CIs), P5b
  precision table, and a vectors computed; the §2.3 equivalence test + downgrade
  rule applied.
- **Fail-closed rule:** no W1-relevant [EXP] cites any RAGC cell until V1–V3
  PASS for its vertical×rung manifest; V4 governs the attribution licence per
  §2.3. Mirrors FRONT/1 §8's builder fail-closed discipline
  [STIPULATED: ASM-0927].

Falsifiability, stated in two registers [STIPULATED: ASM-0927; ASM-0957]:
- **As an instrument:** RAGC/1 fails on its own gates (V2 can fail on a real
  vertical; V3 on a real toolchain; V4 on a real derivation), and its
  constructibility stipulation — that a token/byte/compute-matched generic
  control is CONSTRUCTIBLE on the programme's verticals inside the free pool
  (§10) — is falsified if the §10 envelope is exhausted before V1–V3 pass.
  That is an ENGINEERING falsifier: it tests whether the control can be built.
- **As science:** the decisive falsifiable object is §8.4's frozen primary
  contrast with its margins, kill rule, power target, and spend stop — that is
  what tests whether generic RAG/tool use explains the one measured gain.

---

## 10. Compute plan (cheap-first; the CLOSED matrix + worked arithmetic)

Planning estimates, not commitments; final at KOT-FAIR/2 freeze; local-box work
`nice -n 10` + checkpointed per standing practice [STIPULATED: ASM-0927;
ASM-0956].

- DECISION: **the closed executable scope** (supersedes the revision-1 "3–5
  configs" arithmetic, which covered a fraction of the design's own matrix — no
  silent caps). Dev-scale generation runs per vertical × rung, beyond FRONT/1's
  ledger, are exactly the 11-config set [STIPULATED: ASM-0956]:

| # | Config | Notes |
|---|---|---|
| 1 | R0 | floor |
| 2 | GR-A.bm25 | shared lexical cell |
| 3 | GR-A.dense | shared dense cell |
| 4 | GR-C | closed §5.3 spec |
| 5 | GR-D | wraps GR-A.bm25; ONE named signal; the only retry-multiplied config (≤ ×4, pinned at prereg) |
| 6 | GR-A.bm25 + PS | order perturbation |
| 7 | GR-A.bm25 + RD | noise control |
| 8–11 | OR × 4 representation renderings | the P6 consumption probe (kernel / passages / triples / tool-schema) |

  GR-B is built AND measured inside FRONT/1's ledger (C3-RAG-free arm key) —
  not double-counted here. S itself and the content-type cells (e)/(g) belong
  to the consuming experiment. Any additional cell = registered amendment +
  manifest version bump.
- **Derivations + indexes (per vertical, R-1):** chunking/triple/tool-schema
  derivation = CPU-only on snapshots ≤ ~100 MB; BM25 index = CPU; dense embed
  pass with a small pinned embedder ≈ ≤ ~1 GPU-h. SQLite GR-C store build = CPU.
- **Parity diagnostics:** P5 + P5b ride ONE costed annotation batch
  (power-sized, blind-sampled — costed as annotation, not ~$0, per the round-1
  correction to census accounting); P6 is configs 8–11 above.
- **Worked arithmetic (per vertical × rung):** 11 configs × ~1,500 dev items ×
  ≤ ~1,024 tokens ≈ ≤ ~17M generated tokens, + the GR-D retry multiplier
  (≤ ×4 on config 5 only) ≈ +~4.6M ⇒ ≤ ~22M tokens ≈ **≤ ~8.5 GPU-h per
  vertical × rung** at 135M-class throughput (same tokens-per-GPU-h rate as the
  revision-1 arithmetic) [STIPULATED: ASM-0956].
- **RAGC total beyond FRONT's ledger, R-1, both verticals: ≤ ~20 GPU-h** + CPU +
  one costed annotation batch — inside the ARC/Modal free pool. The §8.4
  de-confound's ≤ ~4 GPU-h spend stop is inside this envelope. R-2 scales
  ≈ 3–4×; R-3 rides the same secured-allocation condition as FRONT/1 §10
  (fail-closed if no allocation) [STIPULATED: ASM-0956].
- Graceful degradation: BM25-only GR-A + GR-C + RD/PS cells are CPU-feasible end
  to end at 135M-class with a single free GPU for generation — a valid (weaker,
  disclosed) control version can still freeze if the dense embedder or GR-D
  verifier training is unavailable [STIPULATED: ASM-0927].

---

## 11. Beads this design spawns (recommendation — the coordinator creates them; no bd operation is performed by this document)

```
P3-T-RAGC-IMPL  [task, P1]  Implement the control-arm pipeline: derivation
    matrix D (chunker/triple/tool-schema scripts + serialisers), BM25+dense
    shared index builds (per-arm indexes, hash-pinned), GR-C SQLite executor +
    closed tool protocol + kernel-op mapping table (§5.3), GR-D loop wrapper +
    the acceptance-signal implementations incl. verifier-training discipline
    (§5.2), PS/RD/OR cells, manifest emitter (§8.1 incl. the KOT-SIZE/2 +
    KOT-COST/2 measurement hooks), build-ledger rows, parity-diagnostic tooling
    (P5 containment checker, P5b audit protocol, P6 probe harness). Harness pin
    per §3.3 (named release/commit or in-repo fallback); keep OUT of encoder/;
    CPU/single-GPU first. Blocked-by: P3-T-FRONT-IMPL (shares the packing
    script, T_k meter, and arm-table ledger).
P3-E-RAGC-CAL  [task, P1]  Pre-register + run V1–V4 per vertical×rung
    manifest; co-scheduled with P3-E-FCAL/P3-E-CAL. Fail-closed per §9.
P3-E-RAGC-F2B  [task, P1, optional if P3-E-VL-1 absorbs it]  Pre-register +
    run the §8.4 f2b de-confound exactly as pre-specified (primary contrast,
    margins, kill rule, power, spend stop). Blocked-by: P3-T-RAGC-IMPL +
    P3-E-RAGC-CAL PASS on the a5 vertical.
Dependency edges for the coordinator: every store-touching G4 [EXP] adds
    blocked-by {P3-T-RAGC-IMPL, P3-E-RAGC-CAL PASS for its vertical}; the
    P3-E-VL-1 prereg names the §8.3 worked-example manifest.
```

---

## 12. Honest limits of this design (carried on every consuming claim)

1. **Information parity is measured, not certified** — the four inherited checks
   + the P5/P5b/P6 diagnostics + the ε_par equivalence-test downgrade bound the
   confound; they do not eliminate it. The residual limitation line rides every
   attribution sentence (FRONT/1 Rule 1, inherited).
2. **Attribution is elimination-grade, never factorial** — the §7 contrasts kill
   or bound; no RAGC cell isolates a single factor, no interactions are
   estimated, and the integration factor is an explicitly unattributed residual.
   A single-factor causal sentence from these cells is a licence violation.
3. **The shared retrieval lens is itself a choice** — BM25 + one dense embedder
   over pinned serialisations is A fixed lens, not THE neutral lens; the NATIVE
   cell and the disclosure rule are the mitigation, not a solution.
4. **Generic acceptance signals are not exhaustive** — GR-D's menu (agreement /
   small learned verifier / execution success) covers the published recipe
   space at our budgets [LIT-BACKED: RAG.md §5, sources 2021–2024], but "no
   generic signal matches the kernel verifier" licenses only "the ONE named
   signal did not match", never a universal; and execution success is the
   weakest item (§5.2).
5. **Equivalence tests can be underpowered** — the §2.3 parity test and the
   §8.4 TOST kill both have an INCONCLUSIVE branch; an underpowered equivalence
   is disclosed as such, never read as parity or as a kill.
6. **The control cannot rescue an unpowered comparison** — every contrast's
   sample size comes from P3-D-POWER under the realised FWER family; RAGC
   supplies cells, never power.
7. **V2 can render a vertical uninformative** — that is a property of the
   vertical/dev slice, disclosed and blocking, not repairable inside RAGC.
8. **ε_par, chunker defaults, the §8.4 margins (δ_eq/δ_sup), the executor
   pin (SQLite), and the GPU-hour envelope are stipulated planning values**,
   maintainer-adjustable at KOT-FAIR/2 freeze / prereg freeze by registered
   amendment; the §10 arithmetic re-derives from measured P3-E-CAL throughput.

---

## 13. Registered assumption entries

Revision-1 block ASM-0920–0927 (registered 2026-07-11) + revision-2 block
ASM-0950–0957 (fresh append-only block ASM-0950–0959 assigned to this revision;
0958–0959 remain free). Supersessions are named in each entry's notes; the
register is append-only.

| Registered id | Scope |
|---|---|
| **ASM-0920** | RAGC contract: the closed named arm inventory GR-A/GR-B/GR-C/GR-D/R0 + PS/RD/OR cells with per-arm claim licences; gate placement (G1 diagnostics, G2 oracle cells, G4 mandatory); NL-integrity applied to the control (never NLB-gated); rung-anchor generators (§0–§1) |
| **ASM-0921** | Rule 1 executed: the derivation matrix D (pinned chunker/deterministic-triple/tool-schema rows) and the P5 coverage census (§2.1, §2.3) — byte-cap clause superseded by ASM-0951; parity-statistics clause superseded by ASM-0952 |
| **ASM-0922** | Rule 2 executed: shared-retriever mechanics (BM25 + pinned dense over pinned common serialisations), the closed identical-vs-native decision table, recall-vs-answer separation, and the anti-weak-control counters (§2.4, §3) — "same index" wording corrected by ASM-0952; harness clause superseded by ASM-0953 |
| **ASM-0923** | Rule 3 executed: one retrieved-token budget per rung with floating k, score-descending assembly, PS/RD cell semantics (RD control-only), token-commensurability with the kernel-as-text null (§4) |
| **ASM-0924** | Rule 4 executed: generator parity mechanics; GR-D loop-shape parity + two-contrast readout; executor-semantics parity; arm-table keys for GR-C/GR-D (§5) — GR-C clause superseded by ASM-0954; GR-D menu clause superseded by ASM-0955 |
| **ASM-0925** | Rule 5 executed: the per-arm build-ledger row schema; kernel authoring hours on S's row of the same table (§6) |
| **ASM-0926** | The readout: the contrast-cell inventory, the five reporting requirements, and the K-P3v2(4) kill wiring (§7) — attribution READING superseded by ASM-0950 |
| **ASM-0927** | The executable interface + instrument gates: manifest schema and consumption contract (FRONT S0; prereg fail-closed), instantiation checklist, worked example, RAGC-CAL fail-closed rule, graceful degradation (§8–§10) — V1/V2/V3 clauses superseded by ASM-0953; compute clause superseded by ASM-0956; manifest extended by ASM-0951 |
| **ASM-0950** | Corrected attribution semantics: contrasts are system-level bundles; elimination + bounded-difference licences only; no single-factor causal sentences; integration an unattributed residual; K-P3v2(4) via programme §2.5 (§0, §7) |
| **ASM-0951** | Total-system admissibility: full-artifact-set fit to B_k.bytes_max; store cap derived as a residual; the anchor-generator inadmissibility consequence; complete KOT-SIZE/2 + measured KOT-COST/2 vectors per arm in the manifest (§2.2, §8.1) |
| **ASM-0952** | Parity instrument corrected: shared retriever = same procedure with per-representation hash-pinned indexes; κ parity as paired TOST/equivalence with underpowered→downgrade; P5b per-source-class precision audit; P6 renamed the consumption probe (composite disclosed); post-failure best-generic licence on GR-B/native (§2.3, §3.1) |
| **ASM-0953** | Instrument gates corrected: V1 named harness pin (FlashRAG default + checklist + registered in-repo fallback); V2 = single contrast LCB95(OR − R0) > 0, orderings diagnostic-only; V3 = BM25 byte-identity + dense logical-record tolerance + retrieval-equivalence threshold (§3.3, §9) |
| **ASM-0954** | GR-C closed to an executable spec: SQLite pinned (fork closed); closed tool-call protocol; expressivity envelope + recursive-CTE semantics; kernel-op mapping table with fail-closed disclosure (§5.3) |
| **ASM-0955** | GR-D discipline: one named signal per instantiation (sweeps barred); learned-verifier training/split/calibration/leakage rules; execution-success weakest-item caveat + answer-type mapping; acceptance-rate co-reporting (§5.2) |
| **ASM-0956** | The closed 11-config executable scope + re-derived compute envelope (≤ ~8.5 GPU-h per vertical×rung; ≤ ~20 GPU-h R-1 total beyond FRONT's ledger), superseding the revision-1 arithmetic (§10) |
| **ASM-0957** | The pre-specified f2b de-confound: primary contrast S − GR-D; δ_eq/δ_sup = 0.05; TOST kill / LCB survive / inconclusive branches; ≥ 0.90 power for Δ = 0.10; ≤ ~4 GPU-h spend stop; formal-input/G2-only scope licence carried verbatim (§8.3–§8.4) |

---

## Epistemic register (what this design relied on)

- **STIPULATED (registered blocks ASM-0920…ASM-0927 + ASM-0950…ASM-0957):**
  every design choice above; each is a scoping/mechanism decision, none is
  evidence for any architecture family or for either value thesis. Revision-2
  supersessions are named per entry in §13 and in the register's notes fields.
  Inherited binding stipulations consumed: ASM-0853 (FRONT/1 §5 rules,
  verbatim), ASM-0852 (T_k meter/arm table), ASM-0890/0891 (MF0
  §8.2(iii)/§8.5 ownership), ASM-0812/0813/0814/0808/0817 (controls,
  statistics, oracle labelling, NL integrity, gates).
- **MEASURED (restated strictly inside their envelopes):** the zero-audited-wins
  null (feasibility-synthesis §0); the f2b +0.1507 with its does_not_license
  assessment (the confound §8.4 exists to cut); the NL-boundary FAILs
  l3a-parse 47.6% / a5-nl 41.6% + S2; the a5 855/855 deterministic world-layer
  substrate used in the worked example (registry/verdicts + assessments as cited
  inline).
- **LIT-BACKED (through the completed P3-LR-RAG review, sources verified at
  primary venue 2026-07-11):** the five open rules + "cells, not the control"
  verdict (RAG.md §6/§7.1); BM25-mandatory (BEIR); recall-vs-answer separation
  (FiD); position confound (Lost-in-the-Middle); random-document trap
  (Power-of-Noise, control-only); long-tail stratification (Mallen); harness
  variance + release pinning (FlashRAG); construction-cost asymmetry (RAG.md §3);
  selector-on-the-ledger (TinyAgent); the verifier recipe menu (RAG.md §5).
- **EXTRAPOLATION:** none used as a premise. The only forward-looking values
  (ε_par default, δ_eq/δ_sup margins, chunker defaults, GPU-hour envelope) are
  stipulated planning numbers listed in §12 as maintainer-adjustable, not
  projections about any system's behaviour.

This document changes no frozen object, no verdict, no audit; its sixteen
assumption entries are REGISTERED in registry/assumptions.jsonl (append-only
blocks ASM-0920–0927 and ASM-0950–0957) by this design and its revision 2. No
git, bd, or kb-sync operation is performed.
