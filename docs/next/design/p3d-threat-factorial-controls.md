# P3-D-THREAT — Programme-3 threat model + factorial attribution controls — REVISED PROPOSAL (Revision 1)

> **STATUS: REVISED PROPOSAL — NOT A PREREG FREEZE; revise before it governs any architecture; waits on #57 + framework blockers.** 2026-07-20, Programme-3 Phase-1 (overflow-Fable).
> Revision 1 applies the load-bearing fixes from the independent GPT-5.6 soundness review
> ([p3-arch-family-review1.md §P3-D-THREAT](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3-arch-family-review1.md): "NEEDS-FIX — strong attribution skeleton …
> the architecture mapping is not yet sound") to the prior unreviewed GPT-5.6 draft, and makes the
> controls consistent with the family's committed Revision-1 states: **H-PS** (primary arm,
> [p3d-ps-architecture.md](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3d-ps-architecture.md)), **H-VL** (re-scoped as the `A-VL` ablation/variant family
> inside H-PS, [p3d-vl-architecture.md](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3d-vl-architecture.md)), and **H-GU** (API-gate-only prereg; full recipe
> conditional, [p3d-gu-architecture.md](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3d-gu-architecture.md)).
> **Any prereg-freeze WAITS on the #57 framework-adjudication decision AND the framework blockers;
> nothing here is frozen, registered, scheduled, or committed.** THREAT gates P3-D-INDEX freeze and
> must itself be ratified before it governs any W1 or attribution claim.
> See "## Revision 1 — review fixes applied" for the itemised changes.
> Source: poc/gpt56-review/p3d-threat-design/ + review-1 fixes.

> **Tags:** the prior draft's `[SV]` markers are mapped to the programme's four-tag scheme:
> `[LIT-BACKED]` = literature-dependent choice supported by the supplied reviews; `[MEASURED: ref]`
> = observed fact with source; `[STIPULATED]` = design choice awaiting ratification;
> `[EXTRAPOLATION]` = forward claim beyond measurement (deliberately unused in this revision —
> forward performance statements are absent pending #57).

---

# P3-D-THREAT — Programme-3 threat model and factorial attribution controls

> **Status:** REVISED PROPOSAL (post-review-1) for the coordinator. Text/specification only; nothing is frozen, preregistered, scheduled, or evidence.
> **Authority:** The parent makes decontamination and factorial controls mandatory for every W1 claim and fixes the seven control families and six attribution dimensions ([parent §2.2](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/programme-3-neurosymbolic-architecture.md:469), [parent §2.3](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/programme-3-neurosymbolic-architecture.md:525)). The KOT-FAIR/2 review correctly identifies their omission from P3-MF-0 as an authority mismatch ([review Part A](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kot-fair-2-review1-freeze-readiness.md:106), [edit #10](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kot-fair-2-review1-freeze-readiness.md:175)).
> **Framing discipline:** the governed architectures are crux-validated ADD-CAPABILITY designs; none claims a literature-backed matched-resource efficiency win. THREAT therefore does not force an efficiency framing: until #57 resolves, \(Y\) is a **reported endpoint vector** (coverage, semantic correctness, dangerous-wrong risk, accepted soundness violations, resource coordinates), contrasted coordinate-wise — not a scalarized verdict `[STIPULATED — review-1 discipline]`.

## 1. Threat model (§2.0)

### 1.1 Actor, assets, and boundary

There is one trusted operator running one experiment under:

- a soft development/search budget;
- the hard W1 deployment budget \(B_k\);
- frozen public and sealed evaluation surfaces.

The operator is not assumed to steal, replace, decrypt, or maliciously tamper with an evaluation bundle. Cryptographic bundle-theft, collusion, and hostile multi-party attacks are out of scope. Hashes and custody records exist for reproducibility and commitment, not as a security claim.

The actor is nevertheless motivated: they want the programme to work, have seen prior failures, choose representations and comparators, and can unintentionally turn flexibility into evidence. The protected asset is therefore the validity and wording of the win claim.

### 1.2 In-scope games

| Operator failure mode | Confound | Concrete game | Mandatory counter |
|---|---|---|---|
| Self-deception through boundary choice | A | Move code, indices, generated state, CPU work, remote calls, or startup work outside the measured artifact/resource boundary | Canonical packing; frozen minimal base; all arm-specific runtime counted; cold and warm runs; remote compute forbidden or fully metered |
| Packaging or workload shopping | A | Choose serialization, compression, batch, output length, cache state, or concurrency that flatters S | One frozen packer and workload manifest for every arm; all six KOT-SIZE figures; output and load rules frozen before S is measured |
| Budget shopping | A/C | Pick \(B_k\) after seeing which comparator S can beat, or let an expensive comparator enlarge S’s allowance | \(B_k\), resource coordinates, and comparator-eligibility rules freeze before evaluation; smaller/cheaper dominators remain eligible |
| Answer-key laundering | B | Author or select records from benchmark items, paraphrases, sources, or error analysis; encode conclusions more directly than weights can | Decontamination hard gate; query-blind store construction; sealed evaluation; derivation-input and source-page screening |
| Alignment mistaken for semantics | B | A retry loop succeeds because a record happens to contain the canonical answer, then the result is called “kernel reasoning” | Derangement, label permutation, irrelevant-record, aligned typed-store, RAG, and text-null arms |
| Seed/control shopping | B | Try multiple permutations, shuffles, retrieval orders, or attacks and report the favourable one | Frozen seed derivation, fixed number of perturbation replicates, no rerolling, all outcomes published |
| Delivery mistaken for integration | B | Report attention, probe decodability, echo accuracy, or component ablation as evidence that the model used structure to solve the task | Primary endpoint must be paired end-task behaviour; direct interventions and counterfactual perturbations required |
| Generic functionality called “kernel-specific” | B/C | Attribute gains from more tokens, typed storage, retrieval, generic tools, search, or prompting to kernel semantics | Six-way attribution ledger; aligned non-kernel store (split, §3.5); strongest matched RAG/tool comparator; kernel-as-text null (conditional, §3.7) |
| Abstention mistaken for structural reasoning | B | A destructive world/store transformation creates conflicts or missing coverage; the system abstains fail-closed, the contrast clears, and the pass is read as “uses structure correctly” | Transformed-world validity gate (§3.0b): licensed, conflict-valid, coverage-matched worlds with recomputed targets; counterfactual-following gate for any structural-reasoning claim `[STIPULATED — review-1 fix 3]` |
| Feedback leakage mistaken for repair | B | Typed diagnostics or accept/reject sequences leak answer information; retry lift is oracle filtering or elimination, then called “the model uses engine feedback” | Common feedback-information factor (§3.9): same-oracle constant + information-matched sham feedback, attempt-indexed outcomes, entropy/exhaustion limits, pre-freeze engagement pilot `[STIPULATED — review-1 fix 6]` |
| Boundary-locus mismatch | B | Transform a host-visible copy of the evidence while the engine executes against the untransformed authoritative binding, so the “control” never touches the causal path | Executable treatment-boundary matrix (§3.0): every control declares its mutation locus per family; a control that leaves the claimed causal path unchanged is inadmissible for that claim `[STIPULATED — review-1 fix 1]` |
| Favourable comparator selection | C | Compare with an untuned neural baseline, a hostile RAG encoding, weak prompting, or no in-context alternative | Frozen frontier-builder; public candidate roster; same evidence and tuning compute; BM25, dense, native-RAG, prompting and in-context cells where applicable |
| Unequal tuning hidden behind equal configuration counts | C | Spend more accelerator/CPU time on S or tune its controls less carefully | Total tuning CPU-hours and accelerator-hours bind per family; same dev split and frozen selection rule |
| Post-result claim switching | B/C | Fail a structure control, then retrospectively call the same result a retrieval or correctness win | Predeclare the claim ladder and all fallback labels; no unregistered fallback claim |

This is the concrete version of the parent’s packaging, frontier, cost, index, store, and tuning games ([parent §2.0](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/programme-3-neurosymbolic-architecture.md:445)).

### 1.3 Standing limitations

The following cannot be eliminated by this single-operator design and must appear beside every affected claim:

- prior unlogged method-development or failed-candidate effort;
- unknown contamination in donor-model training corpora;
- incompleteness of any finite frontier search;
- imperfect semantic-equivalence certification between kernel, typed-record, passage, and triple representations;
- residual dependence on a finite collection of perturbation seeds;
- operator knowledge of the public suite;
- inability of a procedural seal to prove full human independence.

A counter that cannot be made executable before freeze becomes a standing limitation or blocks the corresponding claim. It is not replaced by prose reassurance.

## 2. Common control-arm rules

Let \(F\) denote the full real system with aligned kernel content, native retrieval/interface, deterministic execution, and the deployed retry/search policy. Let \(Y(A)\) be the frozen primary endpoint for arm \(A\) — pending #57, an endpoint **vector** contrasted coordinate-wise (header framing discipline), with the licensing coordinate(s) fixed at prereg-freeze.

**Governed family (Revision 1).** THREAT governs ONE primary architecture family in Phase 1 `[STIPULATED — review-1 consistency]`:

- **H-PS is the primary arm** \(F\): NL → constrained program proposal → compile → execute against the pinned authoritative store snapshot → calibrated risk gate → deterministic checked-result renderer ([p3d-ps-architecture.md §1–2](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3d-ps-architecture.md)).
- **`A-VL` is an ablation arm inside the H-PS control family**, not a second architecture: identical admission, engine, snapshot, and renderer; the sole delta is host value proposal + compare + leak-gated bounded retry ([p3d-vl-architecture.md §0](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3d-vl-architecture.md)). `A-VL` does not receive its own full attribution conjunction; it is a within-family contrast against the direct-render primary arm, and it inherits every common factor below.
- **H-GU is API-gated**: only its step-transition API gate and statement-supply/diversity curve are prereg-ready ([p3d-gu-architecture.md §0/§6.0](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3d-gu-architecture.md)). THREAT’s GU-specific instantiations (trajectory units §3.8, train-time spine §3.10, proof-graph `G-*`) are **conditional on that gate passing and MUST NOT be preregistered as executable arms before it does**; preregistering them earlier would repeat the exact assumed-interface error the review corrected in H-GU itself.

Every W1 preregistration must freeze:

- the exact causal claim: kernel semantics, graph structure, deterministic execution, retry/search, feedback content, neural-symbolic integration, or some conjunction;
- store, corpus, index, model, tokenizer, prompt, scorer, tool, executor, and transformation hashes;
- information-parity and record-alignment certificates;
- the treatment-boundary row (§3.0) of every control arm — which loci it mutates for this family;
- every control arm and its seed schedule;
- actual packed bytes and full KOT-COST/KOT-LIFE ledgers for every arm;
- the paired item/cluster structure used for inference;
- any fallback claim labels.

All controls use the same evaluation items, base model where the contrast is same-host, prompt/scoring rules, output limits, and evidence snapshot. All control arms must pass the same repeatability and resource-boundary checks as \(F\).

“Equal bytes” means the same canonical KOT-SIZE/2 byte ceiling and the same \(B_k\), not artificial padding to identical point values. A smaller control remains eligible and is the stronger comparator. LM-visible context ceilings and retrieved-record entitlements are identical; actual byte, token, CPU, I/O, latency, and energy differences are reported.

A missing, inadmissible, or information-inequivalent required control yields `INSTRUMENT-INVALID`; it never licenses “control unavailable” as a caveat.

### Seed discipline

`[STIPULATED — coordinator/Fable to ratify]`

- Commit a public `seed_root` before any public or sealed outputs exist.
- Derive each seed as
  `uint64(SHA256(input_manifest_hash || seed_root || arm_id || replicate_id)[0:8])`.
- Pin the PRNG implementation and transformation code.
- Use the same derived transformation and decoding seeds across paired systems.
- Use five perturbation replicates initially; increase this number before evaluation if calibration/power analysis requires it. Freeze the final count before S outputs are inspected.
- The estimand is the mean over all frozen perturbation replicates, with perturbation seed represented in resampling. Best-seed selection is prohibited; worst-seed sensitivity is reported.
- A construction failure follows a frozen fallback rule or makes the arm invalid. The operator may not reroll.

## 3. Mandatory factorial control arms (§2.2)

### 3.0 Executable treatment-boundary matrix `[STIPULATED — review-1 fix 1; PROPOSED-PREREG-ROW-THR-R1a]`

The review’s central architecture-mapping finding: the prior `D` construction operated on *retrieved bundles*, but the governed architectures send a formal query/program (plus a store snapshot hash) to an engine that executes against an **authoritative global snapshot**. Unless the authoritative query→store binding is itself transformed, the engine path can remain unchanged and the “control” never intersects the claimed causal mechanism. In `A-VL` the point is sharpest: retrieval output goes to the **ledger only, never the host channel**, so a host-visible-retrieval mutation is literally a mutation of an empty locus.

Five mutation loci are therefore distinguished:

| Locus | Content |
|---|---|
| **L1 — host-visible retrieval/context** | records, passages, or serialized evidence placed where the host LM can read them |
| **L2 — entity/schema linking** | the NL-surface→formal-symbol binding: parser lexicon, entity-linker URN tables, operator/relation vocabulary, GU action vocabulary |
| **L3 — formal request** | the compiled query/program/action object actually submitted to the engine |
| **L4 — authoritative store** | the pinned endorsed snapshot (definitions, axioms, world records) the engine executes against |
| **L5 — engine results/diagnostics** | typed results, provenance, licences, error codes, and the host-visible diagnostic channel |

**Matrix (per control, per family; freeze one row per control at prereg):**

| Control | H-PS / `A-VL` locus | H-GU locus (▷ conditional on the GU API gate) | Explicitly NOT mutated |
|---|---|---|---|
| `D` derangement | **L2 or L4** (declared; §3.1) — the authoritative binding from item entities to store records | ▷ same, over task→store addressing | L3 code path, L5 |
| `P` permutation | **L2** (binding seam; §3.2) + joint L2+L4 equivariant positive control | ▷ L2 action-vocabulary binding | L4 alone (engine is identifier-blind; a store-side label-table permutation under a fixed formal query does not test engine semantics) |
| `I` irrelevant records | **L4** (coverage-matched substitution; §3.3) and L1 where a host-visible evidence channel exists | ▷ L4 | L3, L5 |
| `G-edge/rel/adv` | **L4** world/dependency structure, validity-gated (§3.4) | ▷ L4 proof-relevant structure | L1–L3 |
| `T1/T2/T3` typed-store split | **L4+engine substitution** (§3.5) | ▷ same | L1–L3 of \(F\) |
| `R*` matched RAG/tool | separate comparator system (no mutation of \(F\)) | same | — |
| `X*` text-null | **L5→host delivery seam** (§3.7) | ▷ same | L1–L4 |
| `E0` executor bypass | **L5 influence blocked** (§3.8) | ▷ same | L1–L4 |
| `Q0`/`Qsham` | search/selection policy over family units (§3.8) | ▷ trajectory-level | L1–L5 content |
| `Qdiag-*` | **L5 host-visible diagnostic content** (§3.9) | ▷ same | acceptance decisions (identical oracle) |

**Admissibility rule (executable):** a control offered in support of a claim about the engine path (kernel semantics, structure, execution, addressing) must mutate at least one locus on the authoritative L2→L3→L4→L5 path *as consumed by the engine*, and the arm manifest must state which. A control whose declared mutations leave that path unchanged — e.g. transforming a host-visible copy at L1 while the engine resolves the untransformed binding — is `INSTRUMENT-INVALID` for that claim. The declared row is part of the frozen arm manifest; changing it after outputs are observed is prohibited.

### 3.0b Transformed-world validity gate `[STIPULATED — review-1 fix 3; PROPOSED-PREREG-ROW-THR-R1c]`

Every store-mutating control (`D`/`I` at L4, `P`’s joint positive control, all `G-*`) must produce transformed worlds that are:

1. **Licensed:** the transformed snapshot passes the engine’s load-time validation; every answer-eligible item’s transformed query resolves under the same licence machinery as the original (no new `ERR_TERM_UNLICENSED`-class failures introduced by the transformation itself);
2. **Conflict-valid:** the transformation introduces no functional/cardinality/disjointness/domain/range conflicts beyond a preregistered tolerance matched to the original world’s conflict rate — otherwise the engine’s fail-closed refusal, not the model, produces the contrast;
3. **Coverage-matched:** the fraction of items that remain answerable (engine returns an answer rather than a refusal) on the transformed world matches the original within a preregistered tolerance;
4. **Recomputed-target:** for every transformed world, the frozen engine/generator recomputes the transformed gold target before any model output is observed; transformed worlds without recomputable targets are excluded at construction time, and the exclusion rate is published.

A transformation that cannot satisfy 1–4 within its stratum follows the frozen fallback rule or renders the arm `INSTRUMENT-INVALID`. **Rationale (the review’s abstention game):** destructive shuffle alone proves necessity, not correct counterfactual following — a model can “pass” a destruction contrast merely because the shuffle creates conflicts or missing coverage and triggers fail-closed abstention. The gate removes the trivial abstention trigger so the contrast measures content/structure use, and §3.4 adds the counterfactual-following gate on top.

### 3.1 Deranged store-to-item addressing — `D` (revised per §3.0)

**Construction — retrieval-channel families (L1), where a host-visible retrieval channel exists**

1. Run the frozen retriever/address resolver without generating model answers and record each item’s ranked record bundle.
2. Stratify items by domain, record schema/type signature, bundle cardinality, and context-length class.
3. Within each stratum construct a no-fixed-point item derangement \(\pi\).
4. Item \(i\) keeps its original retrieval ranks, slot count, query, prompt, and code path, but each resolved slot receives the matched bundle belonging to \(\pi(i)\).
5. Donor bundles must not share the target’s answer-bearing concept, source family, or gold answer. Screen this mechanically.
6. Match per-item record counts and LM-visible token counts exactly where the schema permits; otherwise use the frozen nearest-match rule and publish the residual.
7. No mapping may be changed after model outputs are observed.

**Construction — executor families (H-PS/`A-VL`; ▷ H-GU): the authoritative binding is deranged `[STIPULATED — review-1 fix 1]`**

The engine consumes no per-item bundle, so the derangement must transform the authoritative query→store binding itself, at ONE declared locus:

- **L2 variant (binding derangement):** within strata (entity type, arity, frequency class), apply a no-fixed-point derangement to the entity-linker/lexicon URN resolution table, so item \(i\)’s surface entities resolve to the matched entities of \(\pi(i)\). Store, engine, and formal grammar are unchanged; the formal request is well-typed but addresses the wrong content.
- **L4 variant (address derangement):** apply the matched derangement to the store’s record-addressing (entity→record binding) under the engine’s own schema, then re-pin the snapshot hash for the arm.

Both variants must pass the §3.0b validity gate (the deranged world remains load-valid, licensed, conflict-valid, coverage-matched, with recomputed targets — here the recomputed target is what the deranged binding licenses, used as an instrument check that the arm remains mechanically executable rather than a refusal trigger). The chosen variant is frozen per family before evaluation; running both is admissible and reported separately, but the claim-bearing variant is declared in advance.

**Isolates**

Whether the specific item-to-content mapping — through the binding the engine actually consumes — carries the effect, rather than any structured retrieval/execution event or retry opportunity.

**PASS**

`LCB95(Y(F) − Y(D)) > δ_attr,k` on the claim-relevant coordinate(s).

A residual advantage in `D` is attributed only to generic storage, retrieval, formatting, execution mechanics, or search—not aligned content.

**FAIL**

If the contrast does not clear the margin, the item-to-content mapping did not carry a claim-sized effect. Any store-content or kernel-semantic win claim is killed at this rung.

### 3.2 Concept-label permutation — `P` (revised per review) `[STIPULATED — review-1 fix 5; PROPOSED-PREREG-ROW-THR-R1e]`

The prior construction permuted a store-side identifier-to-label table under an unchanged natural-language query. For the governed executor families this is **not a test of whole-query engine semantics at G2**: the engine computes over identifiers and is label-blind, so a store-side label permutation under a fixed formal request can leave the executed computation unchanged. `P` is a test of the **NL/schema binding seam**, and must be instantiated there.

**Architecture-specific instantiation (L2), frozen per family:**

- **H-PS/`A-VL`:** within each declared ontology type, arity, and direction class, apply a bijective derangement to the parser lexicon/entity-linker binding — the mapping from NL surface forms (entity aliases, operator trigger phrases, relation phrasings) to formal symbols (URNs, operators, relations). The store, engine, grammar, and identifier space are unchanged; the natural-language query is unchanged; only the meaning binding the compiler consumes is wrong.
- ▷ **H-GU (conditional):** the same derangement over the action-vocabulary binding — NL/task surface to formal action symbols.
- Preserve the multiset of surface forms, binding-table serialization bytes, retrieval keys, and record counts. If byte/token parity cannot be achieved without altering other factors, the arm is invalid.

**Equivariant-renaming positive control (mandatory companion):** apply one consistent bijective renaming **jointly** to the store identifiers/labels AND the binding tables/queries — a semantics-preserving isomorphism of the whole system (joint L2+L4). A sound system must be **invariant**: `|Y(F) − Y(F_rename)|` within a preregistered equivalence tolerance on the claim-relevant coordinates. This control validates the permutation instrument (the harness and system tolerate renaming per se, so the `P` contrast measures broken *binding*, not incidental brittleness) and catches memorized-surface-form shortcuts. An equivariance failure is `INSTRUMENT-INVALID` for the `P` contrast and is separately reported as a robustness finding.

**Isolates**

Whether the particular concept/relation/operator-to-meaning binding matters, rather than generic typed labels or a trained structured-input channel.

**PASS**

`LCB95(Y(F) − Y(P)) > δ_attr,k`, with the equivariant-renaming control simultaneously within tolerance.

**FAIL**

No claim that the learned or declared concept mapping is causally used. Attention changes, label decodability, or unit naming do not repair the failure. `[LIT-BACKED]` This intervention-first requirement is supported by the RULE causal-evidence audit ([RULE §3](/home/ec2-user/css/kernel/kernel-of-truth/reports/lit-p3-rule.md:315)).

### 3.3 Structurally matched irrelevant records — `I` (revised per §3.0)

**Construction — retrieval-channel families (L1)**

1. Build a query-blind irrelevant-record bank from disjoint source and concept families.
2. For every real retrieved record, select a record matching:
   - schema and field mask;
   - entity/relation types and arity;
   - node/edge counts where present;
   - serialized record size;
   - tokenizer token count;
   - provenance-field presence and length class;
   - retrieval rank and position.
3. Preserve record count, ordering, tool calls, context position, and all interface behaviour.
4. Irrelevant content must be semantically unrelated and screened against the target question, answer, and source.
5. Procedurally generated fixed-width nonce content may be used where needed, but it must be syntactically valid record content—not invisible padding.

**Construction — executor families (L4) `[STIPULATED — review-1 fix 1]`**

For H-PS/`A-VL` (▷ H-GU), replace the authoritative records backing each item with structurally matched irrelevant records **at the store level**, under the §3.0b validity gate: the substituted records must be load-valid, licensed, and coverage-matched, so the item’s formal query still resolves and returns a licensed (irrelevant) result rather than tripping `ERR_NO_RECORD`-class refusals. Without the gate, `I` at L4 degenerates into an abstention trigger and measures the fail-closed machinery, not content relevance. Recomputed transformed targets (the licensed irrelevant results) are recorded as the instrument check.

**Isolates**

Relevant content versus “more tokens,” structured formatting, extra memory accesses, executing *something*, or invoking a tool.

**PASS**

`LCB95(Y(F) − Y(I)) > δ_attr,k`.

**FAIL**

The claimed gain is consistent with token count, format, generic execution mechanics, or generic tool invocation. No content-specific claim is licensed.

### 3.4 Edge/relation shuffle and topology attack — `G-edge`, `G-rel`, `G-adv` (counterfactual-following GATE added) `[STIPULATED — review-1 fix 3; PROPOSED-PREREG-ROW-THR-R1c]`

Required for every graph, relational-structure, rule-composition, or topology claim. For the current family this primarily concerns ▷ H-GU proof/dependency structure (conditional on its API gate) and any H-PS claim naming relation composition; terminal single-op H-PS claims do not name structure and do not trigger this family.

**Edge-shuffle construction**

- Start from the same retrieved/authoritative node set and node attributes (locus per §3.0: L4 for executor families).
- Apply directed degree-preserving double-edge swaps within relation/type-compatible strata.
- Preserve node count, edge count, per-relation edge counts, per-node in/out degree, retrieval results, and all textual node attributes.
- Reject duplicates, forbidden self-loops, or type-invalid edges.
- `[STIPULATED — coordinator/Fable to ratify]` At least 90% of original edge incidences must change.

**Relation-shuffle construction**

- Keep endpoints/topology fixed.
- Derange relation labels across type-, arity-, and direction-compatible edges.
- Preserve the complete relation-label histogram.
- `[STIPULATED — coordinator/Fable to ratify]` At least 90% of label assignments must change.

**Validity gate (mandatory):** every transformed world in every `G-*` arm must satisfy §3.0b — licensed, conflict-valid, coverage-matched, recomputed-target. Shuffles that create conflicts or destroy coverage are rejected and re-drawn under the frozen seed schedule; if a stratum cannot be validly transformed, that stratum follows the frozen fallback rule or the arm is `INSTRUMENT-INVALID`.

**Calibrated structural attack**

`[LIT-BACKED]` Deceive-KG shows that semantics can be destroyed while downstream performance survives; GTEval shows text-carrying fused models nearly unchanged under PRBCD while a graph-only model collapses. These are the reason a uniform shuffle and a targeted structure attack are both required—not evidence that either specific future arm will fail ([FUSE crux](/home/ec2-user/css/kernel/kernel-of-truth/reports/lit-p3-fuse.md:244), [FUSE controls](/home/ec2-user/css/kernel/kernel-of-truth/reports/lit-p3-fuse.md:409)).

- Use PRBCD where technically applicable; otherwise preregister a topology-only black-box attack with the same validation shape.
- `[STIPULATED — coordinator/Fable to ratify]` Select the lowest edit budget from `{1%, 2%, 5%, 10%, 20%}` that causes a simultaneous `LCB95` drop of at least `δ_attr,k` in a frozen graph-only positive control on calibration data.
- Freeze that budget and attack implementation before evaluating \(F\).
- If no budget validates the positive control, the structure instrument is invalid.

**PASS — two conditions, BOTH gates for a structural-reasoning claim**

1. **Necessity (destruction contrasts).** Each required arm independently satisfies:
   - `LCB95(Y(F) − Y(G-edge)) > δ_attr,k`;
   - `LCB95(Y(F) − Y(G-rel)) > δ_attr,k`;
   - `LCB95(Y(F) − Y(G-adv)) > δ_attr,k`.
2. **Counterfactual following (GATE, not a report).** On the validity-gated transformed worlds (which, by §3.0b, remain answerable at the matched rate with recomputed targets), the system’s answers must **track the recomputed transformed targets** at or above a preregistered follow-rate on answered items, with abstention-rate inflation on transformed worlds bounded by a preregistered tolerance. The prior draft requested this “as a report”; that is withdrawn. Mere indiscriminate damage is necessity evidence only; a structural-reasoning claim (“the system follows the structure”) requires the following gate. A system that clears the destruction contrasts but fails the following gate may retain only a preregistered necessity-wording fallback (“structure-dependent”, not “structure-following”).

**FAIL / mandatory kill**

Failure of any required destruction contrast kills the graph/structure attribution; failure of the counterfactual-following gate kills any structural-reasoning wording. A delivery probe showing that graph tokens contain topology does not override either kill: nsk1 and GTEval both exhibit delivery without behavioural integration ([programme premise](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/programme-3-neurosymbolic-architecture.md:175), [FUSE finding](/home/ec2-user/css/kernel/kernel-of-truth/reports/lit-p3-fuse.md:66)).

### 3.5 Aligned non-kernel typed store — split into clean sub-factors `[STIPULATED — review-1 fix 2; PROPOSED-PREREG-ROW-THR-R1b]`

No published instrument located in the reviewed literature supplies this control directly. `[LIT-BACKED]` This is therefore a first-party control proposal, not a literature-established measurement.

The prior single `T` arm removed kernel normalization, dependency/proof DAGs, executable semantics, AND inference rules at once — not a clean single factor: an \(F−T\) contrast could not say *which* removed ingredient carried the effect. Revision 1 splits it into three store-side sub-factors plus the separate executor factor (which already exists as `E0/E1`, §3.8, and is NOT folded back in):

**Common construction base (all sub-factors)**

1. A query-blind compiler consumes the same frozen source-evidence snapshot as the kernel store.
2. Record count, schema/type shape, evidence entitlement, provenance, query alignment, retrieval positions, and LM-visible context ceiling match the kernel arm.
3. The compiler emits a bidirectional proposition inventory showing that every atomic source proposition available to one arm has a corresponding representation in the other.
4. Query-specific answers or conclusions may not be materialized (exception: `T3`, whose closure policy is itself query-blind, frozen pre-benchmark, and offered to all applicable baselines with bytes/build cost counted).
5. Each sub-factor receives the same byte ceiling and complete build/query ledgers. A smaller store is not padded.

**Sub-factor `T1` — aligned typed storage WITHOUT execution.** Plain-English typed records with generic local identifiers, provenance, timestamps, aliases, and proposition/rule text; retrieval-only delivery; no interpreter, no closure. Removes: everything executable. Retains: aligned typed content.
**Isolates:** typed storage + retrieval + provenance value.

**Sub-factor `T2` — schema-neutral generic interpreter over the SAME explicit rules.** The `T1` store plus the kernel’s rules/axioms rendered as explicit generic records, executed by a schema-neutral generic interpreter (predeclared generic lookup/filter/join/forward-chaining over the explicit rules) with no kernel-specific normalization, equivalence classes, URN identity semantics, or kernel traversal/inference procedures. The generic interpreter’s implementation is pinned and its runtime charged.
**Isolates:** kernel-specific semantics/normalization beyond *generic* interpretation of the same explicitly stated rules. This is the claim-bearing sub-factor for “kernel semantics”: \(F−T2\) is the cleanest available kernel-semantics contrast.

**Sub-factor `T3` — matched precomputed-closure/result store, where appropriate.** Where the covered grammar admits finite query-blind closure, materialize the closure/result store before the benchmark/store freeze; answers are delivered by lookup with no runtime inference. Bytes and build cost counted; the same closure policy is available to all applicable baselines.
**Isolates:** runtime deterministic inference versus precomputed results — whether *computing at query time* (as opposed to having the consequences stored) carries the effect. “Where appropriate” is decided at prereg per vertical; an infeasible `T3` (unbounded closure) is recorded as inapplicable, not silently skipped.

**The executor factor stays separate.** Executable-semantics removal is measured by `E0/E1` (§3.8) on \(F\) itself, never by comparing against a store variant that also changes content representation.

**Reporting and the composite \(T^\*\)**

- Report \(F−T1\), \(F−T2\), \(F−T3\) (where applicable) separately in the attribution ledger; the sub-factor differences (`T2−T1`, `T3−T1`) localize the generic-interpreter and closure contributions.
- For the conjunctive claim gate (§4.1), \(T^\*\) = the strongest admissible sub-factor result (the best-performing of `T1/T2/T3` under the frozen dev-selection rule, selected before test outputs). Do not select between variants after test outputs.

**PASS for a kernel-semantic claim**

`LCB95(Y(F) − Y(T*)) > δ_attr,k` — which, since \(T^\*\) is the strongest sub-factor, entails clearing \(F−T2\) in particular.

**FAIL**

The gain is attributed to the strongest surviving sub-factor’s ingredient: aligned typed storage/retrieval (`T1`), generic interpretation of explicit rules (`T2`), or precomputed closure (`T3`). The parent requires that result to be reported “whatever [it] show[s]” ([parent W1 condition 4](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/programme-3-neurosymbolic-architecture.md:400)). A resource-frontier system result may remain only under a preregistered typed-store/interpreter/closure label; “kernel semantics” is prohibited.

### 3.6 Matched RAG/tool-use — `R`

The matched RAG control is both an attribution arm and a member of the G4 frontier.

**Construction**

The RAG family receives:

- the same source-evidence snapshot and information entitlement;
- proposition-parity renderings as passages, triples, and typed records;
- a shared BM25 cell;
- a shared dense-retrieval cell with pinned model/index;
- a native conventional-RAG cell so RAG is not forced through a representation hostile to it;
- every generally available task-appropriate tool that fits the same budget;
- the same maximum retrieved-token/context budget;
- the same canonical packed-byte ceiling and \(B_k\);
- the same total tuning CPU/accelerator budget and frozen dev-selection rule;
- **equally strong parsing, calibration, and selective prediction** `[STIPULATED — review-1 table note]`: the RAG/tool family gets the same NL-admission machinery, calibration protocol, and abstention/selective-prediction tuning effort as \(F\), under the shared tuning budget — a kernel arm with calibrated abstention must not be compared against a RAG arm denied one.

Use the strongest admissible preregistered RAG/tool configuration as \(R^\*\). Actual smaller artifacts remain eligible and are not padded.

`[LIT-BACKED]` Also freeze and report retrieval recall, record/source provenance, popularity strata, context order, position-shuffle sensitivity, and a random-document control. These are required by review edit #9 ([review](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kot-fair-2-review1-freeze-readiness.md:173)).

Two RAG comparisons are required:

1. a same-host, shared-retrieval attribution cell;
2. the strongest admissible G4 RAG/tool family from the frontier-builder.

**Isolates**

Whether the result requires kernel machinery, rather than access to the same corpus through conventional retrieval, prompting, in-context editing, or generic tools.

**PASS**

Because \(R^\*\in F(B_k)\), the inherited W1 rule applies verbatim under the efficiency framing:

`LCB95(INDEX(F) − INDEX(R*)) > δ_k`.

Under a correctness-endpoint framing (post-#57), the corresponding coordinate-wise contrast rule is set by the correctness design; `R*` remains mandatory in both framings.

`[LIT-BACKED]` AxBench and RippleEdits are specific warnings that prompting or in-context access can beat apparently more sophisticated internal machinery ([RULE audit](/home/ec2-user/css/kernel/kernel-of-truth/reports/lit-p3-rule.md:345)).

**FAIL**

W1 fails against the neural/RAG frontier. It cannot be rescued as a kernel win.

### 3.7 Kernel-as-text null — `X` (CONDITIONAL, not core) `[STIPULATED — review-1 fix 4; PROPOSED-PREREG-ROW-THR-R1d]`

**Applicability rule.** `X*` is mandatory **only when the registered claim names native/internal neural-symbolic integration** — a privileged internal seam (graph tokens, KV injection, activation steering, adapters, residual-stream carriers). It is REMOVED from the default core conjunction (§4.1). Rationale: the governed family makes no privileged-seam claim by default — H-PS connects engine output to a deterministic renderer, and `A-VL` delivers feedback as prompt text. A legitimate text-delivered deterministic-executor capability must not be killed merely because text and structured delivery tie: an `X*` tie refutes an *integration* claim, not an *execution* claim. When no integration claim is registered, `X*` may still be run as a diagnostic; its result constrains wording (“kernel information delivered as text”) but is not a kill gate.

**Construction**

1. Retrieve the same records/subgraph and, when executor-on, the same deterministic results and provenance.
2. Render them as text rather than passing them through graph tokens, KV injection, activation steering, adapters, or another privileged internal seam.
3. Share base weights, task data, trainable-parameter ceiling, tuning budget, retrieved information, and LM-visible token ceiling.
4. Select the strongest text serialization using the frozen dev split.
5. `[LIT-BACKED]` The serialization battery must cover the preregistered canonical encodings rather than a single weak rendering; serialization is a first-order graph baseline choice ([FUSE controls](/home/ec2-user/css/kernel/kernel-of-truth/reports/lit-p3-fuse.md:419)).
6. Charge serialization, prompt construction, prefill, and all text tokens.

If all information cannot fit under the shared token ceiling, reduce the common record set before freeze. Silently truncating only the text arm invalidates the control.

**Isolates**

Neural-symbolic integration/interface value over delivering the same kernel information as ordinary text.

**PASS for an integration claim**

`LCB95(Y(F) − Y(X*)) > δ_attr,k`, where \(X^\*\) is the strongest preregistered text serialization.

**FAIL**

No internal-integration claim. If text retains the result, attribution is “kernel information delivered as text” — which, absent a registered integration claim, is not a failure of the architecture’s registered capability claim. If text is harmful but \(F\) merely returns to baseline, that does not establish a positive integration mechanism.

### 3.8 Executor and retry/search factor cells — family-specific units `[STIPULATED — review-1 fix 7; PROPOSED-PREREG-ROW-THR-R1g]`

These cells are necessary because the parent’s six-way decomposition explicitly separates deterministic execution and retry/search. Revision 1 fixes the sampling/selection **unit** per family — the prior generic “candidate” was undefined or wrong for each governed architecture:

| Family | Unit for `E0`/`Q0`/`Qsham` | Family-specific operationalization |
|---|---|---|
| H-PS | **compiled program** | `E0` abstains by construction (no answer without `EngineResult(status=answer)`), so it is a **capability ablation, not a symmetric end-to-end comparator**: surviving compiled programs are scored offline by the harness (canonical-bytes/`program_hash` equality to \(p^\*\) + harness-side typed-result equality, never shown to the arm); the symmetric comparator role belongs to `R*` (adopts H-PS PROPOSED-PREREG-ROW-R1d). `Q0` = first compiled candidate, no repair rounds. |
| `A-VL` (H-PS ablation) | **complete claim** (`kot-vclaim/1`: formal query + typed value) | `E0` withholds the compare result from candidate selection (engine still runs, charged, logged); `Q0` = attempt 0 only; `Qsham` = same attempt budget, kernel verdict hidden, strongest non-kernel selector. All per the `A-VL` spec ([p3d-vl-architecture.md §2](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3d-vl-architecture.md)). |
| ▷ H-GU (conditional on its API gate) | **complete trajectory** (full action sequence, initial state → termination under the frozen controller and budget) | “First candidate” is undefined for multi-step proof search. `Q0` = exactly one trajectory per item (one action proposal per visited state, no restarts, no trajectory reranking); `Qsham` = full registered trajectory budget with **engine-outcome-blind** selection, information-matched sham selection signal; full system = same budget with genuine engine-outcome selection (adopts H-GU PROPOSED-PREREG-ROW-GU-R1e). |

**Executor-bypass arm — `E0`**

- Keep kernel content, retrieval, tool invocation, and engine computation.
- Charge all engine work.
- Prevent engine results, masks, traces, or accept/reject decisions from affecting generation or candidate choice; log them post hoc only.
- Compare against executor-on with retry disabled in both cells.
- Where the architecture’s fail-closed invariants make `E0` abstain by construction (H-PS), the arm is scored per the family row above; \(\Delta_{\text{exec}}\) is then read as separate vector coordinates (proposal-seam exactness contrast + end-to-end coverage collapse), never as a single end-to-end scalar.

Execution attribution requires:

`LCB95(Y(K,E1,Q0) − Y(K,E0,Q0)) > δ_attr,k` on the preregistered claim-relevant coordinate(s), with the family unit above.

**One-shot arm — `Q0`**

- Keep retrieval and deterministic execution.
- Return the first unit (program / claim / trajectory per the family row); no outcome-conditioned retry or search.

**Matched generic-search arm — `Qsham`**

- Generate the same frozen maximum number of units.
- Hide the kernel verdict during unit selection.
- Select using the strongest preregistered non-kernel selector or neural verifier fitting the budget.
- Charge every unit, engine call, selector, and backtrack.

Retry/search attribution is reported as:

- total retry/search: `Y(F) − Y(Q0)`;
- kernel-conditioned selection beyond generic search: `Y(F) − Y(Qsham)`.

A claim naming deterministic execution or kernel-guided retry must clear the corresponding simultaneous `δ_attr,k` margin. Otherwise that dimension is `NOT ESTABLISHED`, even if another kernel dimension passes. `Q0`/`Qsham` control search **quantity and selection**; they do not control feedback **content** — that is §3.9.

### 3.9 Common feedback-information factor — `Qdiag` + leak gate + pilot `[STIPULATED — review-1 fix 6; PROPOSED-PREREG-ROW-THR-R1f]`

`Qsham` controls generic selection, not whether typed diagnostics leak answer information. THREAT therefore adopts, as a **common factor for every retry/feedback-bearing arm in the family**, the machinery already fixed in the sibling revisions (H-PS PROPOSED-PREREG-ROW-R1c; `A-VL` PROPOSED-PREREG-ROW-VL-R1b/c):

1. **Three diagnostic arms under ONE identical accept oracle** (same engine, same acceptance decisions in all three):
   - `Qdiag-typed` — real typed diagnostics (error class + offending field/type), the deployment configuration;
   - `Qdiag-const` — **same-oracle constant feedback**: every rejection returns one constant, uninformative token;
   - `Qdiag-sham` — **information-matched sham feedback**: messages drawn from the true diagnostic vocabulary with matched marginal frequency, length, and entropy, permuted across items so they are decoupled from the actual failure.
   A “feedback helped” claim requires BOTH `Qdiag-typed > Qdiag-const` (content beyond bare rejection) AND `Qdiag-typed > Qdiag-sham` (item-specific content, not generic message statistics), at the claim-relevant margins.
2. **Attempt-indexed outcomes:** attempt-0 and final outcomes are reported separately, with per-attempt acceptance/transition matrices; a gain confined to final outcomes is filtering/search until the `Qdiag` factor plus the leak audit establish feedback consumption.
3. **Entropy/exhaustion limits (executable, not prose):** host-visible diagnostics restricted to a closed non-answer-bearing vocabulary (no gold values, no record/licence identifiers sufficient to reconstruct the answer; answer-bearing witnesses are ledger-only); per-item elimination audit with cumulative leaked bits bounded by a registered budget \(B_{\text{leak}}\); retry-eligibility entropy floor \(H_{\min}\); finite-option exhaustion prohibition (the rules1c degeneracy shape: if the feasible option set satisfies \(|S_0| \le K_{\text{retry}}+1\), the loop is not entered) — per the rules1c precedent that at a closed small-option surface, non-vacuous and non-leaking feedback are jointly unsatisfiable `[MEASURED:` [rules1c instrument-invalid interpretation](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/analysis/rules1c-instrument-invalid-interpretation.md:125)`]`. Violations are fail-closed/`INSTRUMENT-INVALID`.
4. **Pre-freeze engagement pilot (BLOCKING):** before any registered retry campaign, a real-item pilot must go green on: nonzero rejection; non-exhaustion; genuine formal-object repair (a registered minimum fraction of reject→accept transitions change the formal object, moving toward the generator target on seeded probes); and behavioural `Qdiag-typed` vs `Qdiag-const` engagement difference at the attempt-trace level. No green pilot, no campaign.

Numeric \(B_{\text{leak}}\), \(H_{\min}\), and pilot thresholds are prereg-freeze parameters, not fixed here. This factor refines the retry/search attribution dimension of §4; it does not add a seventh dimension.

### 3.10 Train-time factorial spine `[STIPULATED — review-1 fix 8; PROPOSED-PREREG-ROW-THR-R1h]`

The §3.1–§3.9 spine is inference-centric. For ▷ H-GU (conditional on its API gate) and for every **trained** VL/PS variant (`A-VL-R` retry-trained hosts; H-PS execution-feedback-refined or verifier-ranked stages), any train-time mechanism claim additionally requires:

1. **The `Tr×E` grid:** `Tr0/Tr1 × E0/E1`, separating internalized training benefit from runtime engine benefit; plus `TrE0` (train-time engine-outcome-blind: same engine calls made and charged during training, outcomes prevented from controlling admission, targets, feedback, or reward).
2. **Mechanism cells at matched task/token/compute exposure** (adopting H-GU §4a as the family template): `C-label` (final-label-only), `C-trace` (genuine aligned traces — ▷ where step artifacts exist), `C-shuf` (both sub-variants: step-order-shuffled and trace–task mismatched), `C-filter` (executor-filtered admission only, target-bound), `C-feedback` (rejection + typed diagnostic contexts only), `C-reward` (terminal engine reward only). A gain claimed for any mechanism must beat its matched control cell — in particular `C-trace` must beat BOTH `C-shuf` sub-variants — not merely `C-label`. Each cell separately trained and separately seeded.
3. **Target binding everywhere:** admission to any positive buffer, feedback-success terminus, or reward requires engine certification AND target equality with the generator-recorded intended target (H-GU PROPOSED-PREREG-ROW-GU-R1d; the H-PS/`A-VL` analogue is the target-matching accepted-trace filter, `A-VL` PROPOSED-PREREG-ROW-VL-R1d). “Formally valid success” alone never admits a positive.
4. **Training seed as a top-level random effect** in the §5.1 inference procedure whenever the claim concerns a training procedure rather than one frozen artifact.
5. **Statement-supply precondition:** for any RL-bearing arm, the seeded generator’s statement-supply/diversity curve is measured first and bounds the registered exposure (H-GU PROPOSED-PREREG-ROW-GU-R1b).

For H-GU, none of the step-level cells may be preregistered as executable arms before the H-GU §6.0 API gate passes (§2, governed-family rule).

## 4. Six-way attribution procedure

The attribution is a contrast ledger, not six percentages forced to sum to the total. Interactions are reported rather than allocated according to an arbitrary ordering.

| Attribution dimension | Primary controlled contrast | Interpretation |
|---|---|---|
| Kernel semantics | \(F-T^\*\) with \(F-T2\) as the claim-bearing sub-contrast, supported by \(F-T1\), \(F-T3\), \(F-D\), \(F-P\), \(F-I\) | Kernel-specific meaning beyond aligned typed records AND beyond generic interpretation of the same explicit rules |
| Structured storage | same-host \(T1-R_{\text{shared}}\) | Benefit of typed/structured storage available without kernel semantics or execution |
| Retrieval | \(R_{\text{relevant}}-R_{\text{random}}\), plus recall/provenance | Benefit from retrieving relevant evidence rather than supplying context tokens |
| Deterministic execution | \(Y(K,E1,Q0)-Y(K,E0,Q0)\) (family unit, §3.8; H-PS: vector-coordinate reading per the capability-ablation rule), supported by \(F-T3\) (runtime inference vs precomputed closure) | Causal effect of engine output, independent of retry |
| Retry/search | \(F-Q0\), \(F-Qsham\), refined by the `Qdiag-typed/const/sham` content factor (§3.9) | Generic extra search vs kernel-conditioned search vs item-specific diagnostic content |
| Neural-symbolic integration (CONDITIONAL) | \(Y(K,\text{native},E1,Q0)-Y(K,\text{text},E1,Q0)\) — evaluated as a gate only when an integration claim is registered (§3.7) | Benefit of the internal seam over matched text delivery |

At minimum, report semantics×executor, semantics×retrieval, and (where the integration dimension is registered) integration×executor interactions wherever the cells exist; for trained variants, report the `Tr×E` interaction (§3.10). An interaction larger than either named main contrast is reported as such; it is not assigned post hoc to the preferred mechanism.

### 4.1 Claim gate

`[STIPULATED — coordinator/Fable to ratify]`

Margin: under the efficiency-W1 framing,

\[
\delta_{\text{attr},k}=\delta_k .
\]

Reason: a statistically detectable sliver should not inherit a claim whose competitive meaning is a rung-level \(\delta_k\) improvement. Under a correctness-endpoint framing (post-#57), the attribution margins are set by the correctness design; THREAT fixes the **conjunction structure**, not the correctness margins, and does not force the efficiency framing `[STIPULATED — review-1 discipline]`.

For a full “kernel-mechanism neurosymbolic win,” define `[STIPULATED — review-1 fix 4]`:

\[
J_{\text{core}}=\{D,P,I,T^\*,R^\*\},
\]

with the conditional additions:

- `G-edge`, `G-rel`, `G-adv` — for every graph/structure claim, **including the §3.4 counterfactual-following gate** for structural-reasoning wording;
- `E0`, `Q0`, `Qsham` (family units, §3.8) — when the claim names execution or retry/search;
- `Qdiag-typed/const/sham` (§3.9) — when the claim names feedback/diagnostic use (“feedback helped”, “learns from engine errors”);
- \(X^\*\) — **only when the claim names native/internal integration**; it is NOT in the default core conjunction;
- the §3.10 train-time cells — when the claim names a training mechanism.

The mechanical attribution statistic is:

\[
A_k=\min_{j\in J_{\text{claim}}}
  \left\{LCB95\bigl(Y(F)-Y(j)\bigr)-\delta_{\text{attr},k}\right\}
\]

over the registered claim-relevant coordinate(s). A kernel-mechanism attribution passes only if \(A_k>0\), every gate-type condition in \(J_{\text{claim}}\) (equivariance tolerance §3.2, counterfactual following §3.4, leak/pilot gates §3.9) holds, and W1 itself passes under the registered framing.

### 4.2 Verdict ladder

1. **W1 frontier gate fails (efficiency framing) / registered primary endpoint fails (correctness framing):** claim fails; controls remain diagnostic.
2. **Required arm missing, unmatched, inadmissible (incl. §3.0 boundary-locus mismatch or §3.0b validity-gate failure), or invalid:** `INSTRUMENT-INVALID`; no win claim.
3. **Derangement, permutation (with valid equivariance control), or irrelevant-content gate fails:** store-content/kernel claim killed. No post hoc “more context helped” fallback unless separately preregistered.
4. **Graph destruction contrast fails, or the counterfactual-following gate fails:** structure/topology claim killed; only a preregistered necessity-wording fallback may survive a following-gate-only failure.
5. **`T2` (or the composite \(T^\*\)) matches \(F\):** result attributed to typed storage/generic interpretation/closure per the strongest surviving sub-factor; no kernel-semantics wording.
6. **Matched RAG matches or beats \(F\):** W1 fails under the efficiency framing because RAG is in \(F(B_k)\); under a correctness framing the result is generic-tool-labelled.
7. **Kernel-as-text matches \(F\) where an integration claim is registered:** the integration claim fails; kernel information may still matter. Where no integration claim is registered, the same outcome constrains wording only (“kernel information delivered as text”).
8. **Executor, retry, or feedback-content contrast fails:** that component is not credited; other preregistered dimensions may still be evaluated.
9. **`Qdiag`/leak gate or engagement pilot fails:** any feedback-use claim is killed or the campaign blocked, respectively.
10. **W1 (or the registered primary endpoint) and all claim-relevant contrasts and gates clear their simultaneous margins:** `W1-PASS — KERNEL-MECHANISM ATTRIBUTED`, restricted to the tested rung, suite, budget, and declared dimensions.

Controls may reveal a legitimate generic typed-store, generic-interpreter, or text-delivered result. They prevent that result from being laundered into a kernel-specific or structure-causal claim — and, symmetrically (§3.7), they do not kill a legitimate text-delivered deterministic-executor capability that never claimed a privileged seam.

## 5. KOT-FAIR/2 and P3-D-INDEX integration

P3-D-THREAT gates P3-D-INDEX freeze, and every G4/W1 experiment is already blocked on both plus the matched-RAG design and calibration ([programme work graph](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/programme-3-neurosymbolic-architecture.md:928), [Phase-2 blocking rule](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/programme-3-neurosymbolic-architecture.md:950)). THREAT itself is a REVISED PROPOSAL: it must be ratified before it governs any architecture (header).

The controls enter KOT-FAIR/2 as follows:

- **§0 Threat register:** replace the implicit malicious-adversary framing with the single motivated-operator model above.
- **§5 Anti-confound machinery:** add the complete arm manifest (including the §3.0 treatment-boundary rows and §3.0b validity-gate certificates), parity certificates, transformation hashes, and PASS/FAIL meanings.
- **P3-D-RAGC:** owns the RAG renderings, shared/native retrieval cells, random-document/position controls, and identical ledgers.
- **P3-D-FRONTIER:** tunes RAG, prompting, generic tools, adaptive test-time compute, and neural verifiers under the same total tuning-compute rule — with parsing/calibration/selective-prediction parity (§3.6).
- **Family designs:** P3-D-PS (and its `A-VL` ablation) instantiates the common spine with the §3.8 family units and §3.9 feedback factor already fixed in its Revision 1; P3-D-GU freezes graph shuffle/attack and trajectory/train-time details only after its API gate; every store-touching family instantiates the common spine.
- **P3-D-INDEX:** freezes the complete control manifest, grader logic, claim ladder, multiplicity family, and ratified constants before P3-E-CAL.
- **P3-E-CAL:** validates the perturbation generator, the §3.0b validity-gate tolerances, the equivariant-renaming tolerance, and the graph positive control, but does not treat any of them as architecture evidence.

All controls run on both the frozen public suite and the sealed suite. For sealed items, the custodian or pinned generator runs the already-frozen transformation code without exposing item-level content to the developer.

### 5.1 Statistics and multiplicity

The parent’s house rule remains verbatim: a margin claim requires `LCB95(Δ)>δ`, with simultaneous confidence bounds/FWER control across preregistered comparators and domains ([parent §2.5](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/programme-3-neurosymbolic-architecture.md:571)).

`[STIPULATED — coordinator/Fable to ratify]` Use a frozen two-stage gatekeeping procedure:

1. W1 frontier and domain non-inferiority family (or the registered correctness-endpoint primary family, post-#57);
2. only if stage 1 passes, the attribution-control family.

Within each stage, use simultaneous one-sided max-t bounds at family-wise \(\alpha=0.05\). The attribution family includes every required `F − control` contrast, the gate-type conditions’ registered tolerances, and any domain-level mechanism claims. A RAG comparison already present in stage 1 is reused rather than tested twice.

For the fixed-suite estimand:

- keep benchmark and domain weights fixed;
- resample the appropriate item clusters within each benchmark—story, rule template, source document, paraphrase family, or equivalent;
- preserve all system/control outputs for an item as a pair;
- include perturbation seed as a crossed randomization factor;
- include training seed as a top-level random effect when the claim concerns a training procedure rather than one frozen artifact (§3.10).

This incorporates the review’s correction to the draft bootstrap ([review statistics](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kot-fair-2-review1-freeze-readiness.md:137)).

The kill is conjunctive. No large win against one control compensates for failure against another. A low-powered valid result that does not clear its bound is a failed claim at that rung, not affirmative evidence of no causal effect; an invalid arm blocks the claim entirely.

### 5.2 Correctness claims

This proposal does not decide whether correctness becomes a second success claim, a conjunctive W1 gate, or a correctness–coverage–cost Pareto axis. That remains the coordinator/Fable decision identified in review Part C ([review](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kot-fair-2-review1-freeze-readiness.md:181)).

If a correctness claim is authorized, it needs the analogous control set over:

- dangerous-wrong probability;
- selective risk and coverage;
- accepted/provenance-backed soundness violations;
- end-to-end semantic correctness;
- graph counterfactual following where relevant (now a gate, §3.4).

The typed-store split, strongest neural/RAG selective-prediction baseline, conditional text null, execution bypass, retry/search/feedback controls, and structure attacks remain mandatory. Endpoint-specific correctness margins and rare-event sample sizes belong to the separate correctness design; they are not fixed here.

## 6. `[STIPULATED]` values and rules needing ratification

1. `[STIPULATED — coordinator/Fable to ratify]` Under the efficiency-W1 framing, \(\delta_{\text{attr},k}=\delta_k\) for every claimed mechanism contrast; correctness-framing margins are deferred to the correctness design; THREAT fixes the conjunction structure only.
2. `[STIPULATED — coordinator/Fable to ratify]` The SHA-256 seed-derivation scheme, five initial perturbation replicates, pre-output power-based increases, mean-over-seeds estimand, and no rerolling.
3. `[STIPULATED — coordinator/Fable to ratify]` Interpret “equal bytes” as equal canonical byte entitlement with no padding; smaller controls remain eligible and stronger.
4. `[STIPULATED — coordinator/Fable to ratify]` The §3.0 treatment-boundary matrix: one frozen locus row per control per family; engine-path claims require an authoritative-path mutation; locus mismatch is `INSTRUMENT-INVALID`. (THR-R1a)
5. `[STIPULATED — coordinator/Fable to ratify]` The §3.0b transformed-world validity gate (licensed, conflict-valid, coverage-matched, recomputed-target) for every store-mutating control, with tolerances calibrated at P3-E-CAL. (THR-R1c)
6. `[STIPULATED — coordinator/Fable to ratify]` The `T1/T2/T3` split with the separate executor factor; \(T^\*\) = strongest admissible sub-factor selected before test outputs; sub-factor contrasts separately reported; proposition-equivalence certificates for each. (THR-R1b)
7. `[STIPULATED — coordinator/Fable to ratify]` Shared BM25, shared dense, native conventional-RAG, position-shuffle, random-document, recall/provenance, popularity-stratified, and frozen-context-order cells, with parsing/calibration/selective-prediction parity for the RAG/tool family.
8. `[STIPULATED — coordinator/Fable to ratify]` ≥90% changed edge incidences and ≥90% changed relation assignments in uniform structure shuffles, under the §3.0b gate.
9. `[STIPULATED — coordinator/Fable to ratify]` Calibrate the topology attack on `{1%, 2%, 5%, 10%, 20%}` edit budgets using the lowest budget that drops the graph-only positive control by at least \(\delta_{\text{attr},k}\).
10. `[STIPULATED — coordinator/Fable to ratify]` The counterfactual-following GATE for structural-reasoning claims: preregistered follow-rate on validity-gated transformed worlds + bounded abstention inflation; necessity-only wording as the sole fallback. (THR-R1c)
11. `[STIPULATED — coordinator/Fable to ratify]` `P` instantiated at the L2 binding seam per family, with the mandatory joint equivariant-renaming positive control and its equivalence tolerance. (THR-R1e)
12. `[STIPULATED — coordinator/Fable to ratify]` \(X^\*\) conditional on a registered native/internal-integration claim; removed from \(J_{\text{core}}\); diagnostic-only otherwise. (THR-R1d)
13. `[STIPULATED — coordinator/Fable to ratify]` Executor-bypass, one-shot, and matched generic-search cells with family-specific units (program / claim / trajectory), including the H-PS capability-ablation scoring rule and the H-GU trajectory definitions. (THR-R1g)
14. `[STIPULATED — coordinator/Fable to ratify]` The common feedback-information factor: `Qdiag-typed/const/sham` under one accept oracle, attempt-indexed outcomes, closed diagnostic vocabulary with \(B_{\text{leak}}\)/\(H_{\min}\)/exhaustion limits, and the blocking pre-freeze engagement pilot. (THR-R1f)
15. `[STIPULATED — coordinator/Fable to ratify]` The train-time factorial spine (`Tr×E` + `TrE0` + mechanism cells at matched exposure + target binding + training-seed random effect + statement-supply precondition) for H-GU and trained VL/PS variants; no GU step-level control arm preregistered before the GU API gate. (THR-R1h)
16. `[STIPULATED — coordinator/Fable to ratify]` Fixed-sequence primary→attribution gatekeeping with within-stage simultaneous one-sided max-t bounds at FWER 0.05.
17. `[STIPULATED — coordinator/Fable to ratify]` Run the factorial controls on both public and sealed suites.
18. `[STIPULATED — coordinator/Fable to ratify]` Prohibit post-result claim switching; any typed-store, generic-interpreter, closure, text-delivery, or generic-retrieval fallback must be separately preregistered and multiplicity-controlled.

## PROPOSED prereg rows (labels only — nothing registered)

All rows are PROPOSED only — nothing is registered, frozen, or scheduled; no `ASM-<number>` ids are minted here (those are assigned at prereg-freeze). Labels are `THR-`prefixed to stay disjoint from the sibling H-PS (`PROPOSED-PREREG-ROW-R1a…e`), H-VL (`…-VL-R1a…e`), and H-GU (`…-GU-R1a…e`) revisions.

- **PROPOSED-PREREG-ROW-THR-R1a:** treatment-boundary law — every control arm freezes a per-family mutation-locus row over {host-visible retrieval, entity/schema linking, formal request, authoritative store, engine results}; a control supporting an engine-path claim must mutate the authoritative path as consumed by the engine; a declared-locus mismatch (e.g. host-visible-only transformation under an untransformed authoritative binding) is `INSTRUMENT-INVALID` for that claim. `[STIPULATED]`
- **PROPOSED-PREREG-ROW-THR-R1b:** T-split law — the aligned non-kernel control is three clean sub-factors (`T1` typed storage without execution; `T2` schema-neutral generic interpreter over the same explicit rules; `T3` matched query-blind precomputed-closure/result store where applicable) plus the SEPARATE executor factor `E0/E1`; \(F−T2\) is the claim-bearing kernel-semantics contrast; \(T^\*\) = strongest admissible sub-factor, selected before test outputs; sub-factor contrasts reported separately. `[STIPULATED]`
- **PROPOSED-PREREG-ROW-THR-R1c:** transformed-world validity + counterfactual-following law — every store-mutating control produces licensed, conflict-valid, coverage-matched transformed worlds with recomputed targets (fail-closed otherwise); destructive contrasts prove necessity only; any structural-reasoning claim additionally requires the counterfactual-following GATE (preregistered follow-rate on transformed targets, bounded abstention inflation); abstention triggered by transformation-induced conflicts/coverage loss never counts as a pass. `[STIPULATED]`
- **PROPOSED-PREREG-ROW-THR-R1d:** X-conditionality law — the kernel-as-text null \(X^\*\) is mandatory only for claims naming native/internal neural-symbolic integration; it is excluded from the default core conjunction \(J_{\text{core}}=\{D,P,I,T^\*,R^\*\}\); a text-tie kills integration wording only, never a text-delivered deterministic-executor capability claim that named no privileged seam. `[STIPULATED]`
- **PROPOSED-PREREG-ROW-THR-R1e:** P-instantiation law — concept-label permutation is instantiated at the NL/schema binding seam with architecture-specific parser-lexicon/entity-linker/action-vocabulary derangements (not a store-side label-table permutation under a fixed formal query), accompanied by a mandatory joint equivariant-renaming positive control whose equivalence tolerance gates the instrument. `[STIPULATED]`
- **PROPOSED-PREREG-ROW-THR-R1f:** feedback-information law — every retry/feedback-bearing arm carries the common factor: `Qdiag-typed/const/sham` under one identical accept oracle (constant AND information-matched sham), attempt-indexed outcome reporting, closed non-answer-bearing diagnostic vocabulary with elimination-audit budget \(B_{\text{leak}}\), retry-eligibility entropy floor \(H_{\min}\), executable exhaustion prohibition, and a blocking pre-freeze real-item engagement pilot; violations fail-closed/`INSTRUMENT-INVALID` (aligns with H-PS R1c and VL-R1b/c). `[STIPULATED]`
- **PROPOSED-PREREG-ROW-THR-R1g:** family-unit law — `E0/Q0/Qsham` are defined over family-specific units: compiled programs for H-PS (with `E0` as a capability ablation scored offline, never a symmetric end-to-end comparator), complete claims for the `A-VL` ablation, and complete trajectories for H-GU (engine-outcome-blind sham selection); “first candidate” without a declared unit is inadmissible. `[STIPULATED]`
- **PROPOSED-PREREG-ROW-THR-R1h:** train-time spine law — any train-time mechanism claim (H-GU; trained VL/PS variants) requires the `Tr0/Tr1×E0/E1` grid with `TrE0`, the matched-exposure mechanism cells (`C-label`/`C-trace`/`C-shuf` both sub-variants/`C-filter`/`C-feedback`/`C-reward`, separately trained and seeded), mandatory target binding for every positive/reward signal, training seed as a top-level random effect, and the statement-supply precondition before RL spend; no H-GU step-level control arm is preregistrable before the H-GU step-transition API gate passes. `[STIPULATED]`

## Revision 1 — review fixes applied

Per [p3-arch-family-review1.md §P3-D-THREAT](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3-arch-family-review1.md) (verdict: NEEDS-FIX — “strong attribution skeleton … the architecture mapping is not yet sound”). This revision produces a REVISED PROPOSAL only; ratification and any prereg-freeze wait on #57 + the framework blockers.

1. **Executable treatment-boundary matrix (`D`/`I` under-specification) — ADOPTED.** New §3.0 defines the five mutation loci (host-visible retrieval / entity-schema linking / formal request / authoritative store / engine results), a per-control per-family matrix frozen at prereg, and the executable admissibility rule: engine-path claims require an authoritative-path mutation; host-visible-only transformations under an untransformed authoritative binding are `INSTRUMENT-INVALID`. `D` (§3.1) gains executor-family constructions (L2 binding derangement or L4 address derangement of the authoritative query→store binding, declared and frozen); `I` (§3.3) gains the L4 coverage-matched substitution so it does not degenerate into a refusal trigger. The `A-VL` ledger-only-retrieval fact is made explicit as the sharpest instance. (THR-R1a)
2. **`T*` split — ADOPTED.** §3.5 replaces the overloaded single factor with `T1` (aligned typed storage without execution), `T2` (schema-neutral generic interpreter over the same explicit rules), `T3` (matched query-blind precomputed-closure/result store where applicable), and keeps the executor factor separate in `E0/E1` — four clean sub-factors in place of one confounded arm. \(F−T2\) is named the claim-bearing kernel-semantics contrast; \(T^\*\) is the strongest admissible sub-factor selected before test outputs; the ledger (§4) reports each sub-contrast. (THR-R1b)
3. **`G-*` gate — ADOPTED.** §3.0b adds the transformed-world validity gate (licensed, conflict-valid, coverage-matched, recomputed-target) for ALL store-mutating controls, and §3.4 upgrades counterfactual following from “requested as a report” to a GATE for any structural-reasoning claim, with a preregistered follow-rate, bounded abstention inflation, and a necessity-only wording fallback. The §1.2 games table gains the abstention-mistaken-for-structural-reasoning row. (THR-R1c)
4. **`X*` out of the core conjunction — ADOPTED.** §3.7 and §4.1: \(J_{\text{core}}=\{D,P,I,T^\*,R^\*\}\); \(X^\*\) is mandatory only when the claim names native/internal integration, diagnostic-only otherwise; the verdict ladder (§4.2 item 7) states that a text-tie kills integration wording only and cannot kill a text-delivered deterministic-executor capability that named no privileged seam. (THR-R1d)
5. **`P` instantiation — ADOPTED.** §3.2 withdraws the store-side label-table permutation as the executor-family instantiation (the engine is identifier-blind; it does not test whole-query engine semantics at G2) and requires architecture-specific binding-seam derangements (parser lexicon/entity linker for H-PS/`A-VL`; action vocabulary for H-GU) PLUS the mandatory joint equivariant-renaming positive control with an equivalence tolerance gating the instrument. (THR-R1e)
6. **Common feedback-information factor — ADOPTED.** New §3.9 adds, family-wide: `Qdiag-typed`/same-oracle-constant/`Qdiag-sham` (information-matched) under one identical accept oracle, attempt-indexed outcomes, executable entropy/exhaustion limits (closed vocabulary, \(B_{\text{leak}}\) elimination audit, \(H_{\min}\) floor, exhaustion prohibition, per the rules1c precedent), and the blocking pre-freeze real-item engagement pilot — aligned with and adopting the sibling H-PS `Qdiag` (R1c) and `A-VL` leak-gate/pilot (VL-R1b/c) fixes. The §1.2 games table gains the feedback-leakage row. (THR-R1f)
7. **Family-specific `E0/Q0/Qsham` units — ADOPTED.** §3.8 defines the unit per family: compiled programs for H-PS (with the H-PS R1d capability-ablation/offline-scoring rule inherited verbatim), complete claims for the `A-VL` ablation, complete trajectories for H-GU (adopting GU-R1e’s trajectory-level `Q0`/`Qsham` with engine-outcome-blind sham selection). (THR-R1g)
8. **Train-time factorial spine — ADOPTED.** New §3.10: `Tr×E` grid + `TrE0`, the six matched-exposure mechanism cells (GU §4a as family template, `C-shuf` both sub-variants), mandatory target binding, training-seed random effect (wired into §5.1), and the statement-supply precondition — required for H-GU and trained VL/PS variants, with the explicit rule that no H-GU step-level control arm is preregistrable before the H-GU API gate. (THR-R1h)

**Consistency with the revised family — applied throughout:** §2 “Governed family” states the Revision-1 structure (H-PS primary; `A-VL` an ablation inside the H-PS control family with no separate full conjunction; H-GU API-gate-only, with all GU-specific THREAT instantiations marked ▷ conditional). **Adopted-with-modification (one point):** the review lists `X*` as “conditional — neither [VL nor PS] makes a privileged neural-integration claim by default”; Revision 1 adopts the conditionality rule generally rather than hard-coding the current family’s claim inventory, so a future arm that *does* register an integration claim automatically re-acquires \(X^\*\) as a gate — same effect for the current family, more robust to family evolution. No fix is rebutted.

**Framing discipline retained:** the add-capability discipline the review praised is kept and strengthened — the header and §2 fix \(Y\) as an endpoint vector pending #57; §4.1 scopes \(\delta_{\text{attr},k}=\delta_k\) to the efficiency framing only; §3.6 and §4.2 carry both framings; THREAT nowhere requires an efficiency claim and no matched-resource win is asserted anywhere.

Additionally (discipline, not a numbered review fix): the draft’s `[SV]` markers were mapped to the programme’s four-tag scheme as `[LIT-BACKED]`; the rules1c fact carries `[MEASURED]` with source; every new design choice carries `[STIPULATED]`; `[EXTRAPOLATION]` is deliberately unused. The review-praised skeleton is unchanged: the motivated-operator threat model (§1), the six-way contrast ledger that refuses to force interacting effects into percentages (§4), and the T/R/X/E0/Q0/Qsham dimension set (now split, conditioned, and unit-fixed rather than replaced).

No repository files other than this design document were changed; nothing was committed, registered, frozen, scheduled, or executed.

## MANDATORY self-check (Revision 1)

1. **All 8 fixes addressed?** YES — itemised above with section anchors: (1) §3.0/§3.1/§3.3, (2) §3.5, (3) §3.0b/§3.4, (4) §3.7/§4.1, (5) §3.2, (6) §3.9, (7) §3.8, (8) §3.10; each carries a `PROPOSED-PREREG-ROW-THR-R1a…h` row.
2. **`T*` split into ≥4 clean sub-factors?** YES — `T1` (typed storage, no execution), `T2` (schema-neutral generic interpreter over the same explicit rules), `T3` (matched precomputed-closure/result store where applicable), and the SEPARATE executor factor `E0/E1` (§3.5, explicitly not folded back in); \(F−T2\) named claim-bearing.
3. **`G-*` a gate with licensed/conflict-valid/coverage-matched/recomputed-target conditions?** YES — §3.0b states all four conditions as constructional requirements (fail-closed/`INSTRUMENT-INVALID` otherwise) and §3.4 PASS condition 2 makes counterfactual following a GATE (preregistered follow-rate + bounded abstention inflation), with “requested as a report” explicitly withdrawn.
4. **`X*` not in the default core conjunction?** YES — §4.1: \(J_{\text{core}}=\{D,P,I,T^\*,R^\*\}\); \(X^\*\) added only for registered native/internal-integration claims; §4.2 item 7 protects text-delivered executor capabilities.
5. **Controls consistent with revised H-PS / H-VL(ablation) / H-GU(API-gated)?** YES — §2 “Governed family” encodes the Revision-1 states; §3.8 inherits H-PS R1d (`E0` capability ablation) and GU-R1e (trajectory units) verbatim; §3.9 adopts H-PS R1c + VL-R1b/c; §3.10 adopts GU §4a/GU-R1b/d; all GU step-level instantiations are ▷ conditional on the GU §6.0 gate and barred from earlier preregistration.
6. **Every load-bearing claim tagged?** YES — literature-derived choices carry `[LIT-BACKED]` (mapped from `[SV]`); the rules1c leak–vacuity fact carries `[MEASURED]` with source; every design choice carries `[STIPULATED]` (§3.0–§3.10 rules, stipulated values 1–18, THR rows); `[EXTRAPOLATION]` deliberately unused; no `[MEASURED]` tag sits on a choice.
7. **No @handle/account strings?** YES — checked; none present.
8. **No `ASM-<number>` ids minted?** YES — only `PROPOSED-PREREG-ROW-THR-R1a…h` labels; the PROPOSED-rows section states ids are assigned at prereg-freeze; sibling rows are referenced by their PROPOSED labels only.
9. **Nothing committed/registered/frozen?** YES — this file edited in place only; registry untouched; no git operations, no runs, no goldens, no schedules; the header states any prereg-freeze waits on #57 + the framework blockers and that THREAT must be ratified before it governs any architecture.
