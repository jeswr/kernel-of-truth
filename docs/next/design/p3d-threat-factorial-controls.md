# P3-D-THREAT — Programme-3 threat model + factorial attribution controls — GPT-5.6 DRAFT

> **STATUS: UNREVIEWED GPT-5.6 DRAFT.** Produced 2026-07-19 (Programme-3 Phase-1, overflow-Fable; NON-gated on the
> #57 correctness re-weighting — these anti-gaming/causality controls apply to ANY W1 claim). Fills the gap the
> KOT-FAIR/2 review flagged (parent §2.2 factorial attribution controls entirely missing from P3-MF-0) and answers
> the FUSE/RULE crux (ablations don't establish causality). NEXT: review gate → Fable critique → integrate into the
> KOT-FAIR/2 revision (review edit #10) → P3-D-INDEX freeze. Not frozen. Source: poc/gpt56-review/p3d-threat-design/.

---

# P3-D-THREAT — Programme-3 threat model and factorial attribution controls

> **Status:** PROPOSAL for coordinator review and Fable critique. Not frozen, preregistered, or evidence.  
> **Scope:** text/specification only; no repository files changed.  
> **Authority:** The parent makes decontamination and factorial controls mandatory for every W1 claim and fixes the seven control families and six attribution dimensions ([parent §2.2](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/programme-3-neurosymbolic-architecture.md:469), [parent §2.3](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/programme-3-neurosymbolic-architecture.md:525)). The review correctly identifies their omission from P3-MF-0 as an authority mismatch ([review Part A](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kot-fair-2-review1-freeze-readiness.md:106), [edit #10](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kot-fair-2-review1-freeze-readiness.md:175)).

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
| Generic functionality called “kernel-specific” | B/C | Attribute gains from more tokens, typed storage, retrieval, generic tools, search, or prompting to kernel semantics | Six-way attribution ledger; aligned non-kernel store; strongest matched RAG/tool comparator; kernel-as-text null |
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

Let \(F\) denote the full real system with aligned kernel content, native retrieval/interface, deterministic execution, and the deployed retry/search policy. Let \(Y(A)\) be the frozen primary endpoint for arm \(A\).

Every W1 preregistration must freeze:

- the exact causal claim: kernel semantics, graph structure, deterministic execution, retry/search, neural-symbolic integration, or some conjunction;
- store, corpus, index, model, tokenizer, prompt, scorer, tool, executor, and transformation hashes;
- information-parity and record-alignment certificates;
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

### 3.1 Deranged store-to-item addressing — `D`

**Construction**

1. Run the frozen retriever/address resolver without generating model answers and record each item’s ranked record bundle.
2. Stratify items by domain, record schema/type signature, bundle cardinality, and context-length class.
3. Within each stratum construct a no-fixed-point item derangement.
4. Item \(i\) keeps its original retrieval ranks, slot count, query, prompt, and code path, but each resolved slot receives the matched bundle belonging to \(\pi(i)\).
5. Donor bundles must not share the target’s answer-bearing concept, source family, or gold answer. Screen this mechanically.
6. Match per-item record counts and LM-visible token counts exactly where the schema permits; otherwise use the frozen nearest-match rule and publish the residual.
7. No mapping may be changed after model outputs are observed.

**Isolates**

Whether the specific item-to-record mapping carries the effect, rather than any structured retrieval event or retry opportunity.

**PASS**

`LCB95(Y(F) − Y(D)) > δ_attr,k`.

A residual advantage in `D` is attributed only to generic storage, retrieval, formatting, or search—not aligned content.

**FAIL**

If the contrast does not clear the margin, the item-to-record mapping did not carry a claim-sized effect. Any store-content or kernel-semantic win claim is killed at this rung.

### 3.2 Concept-label permutation — `P`

**Construction**

1. Store records use stable fixed-width concept/relation identifiers plus a separate identifier-to-label/meaning table.
2. Within each declared ontology type, arity, and direction class, apply a bijective derangement to the table’s semantic labels/meanings.
3. Leave identifiers, adjacency, record positions, field masks, retrieval keys, rank scores, and record counts unchanged.
4. Preserve the multiset of label strings, relation labels, and serialized table bytes.
5. The natural-language query remains unchanged; only the mapping from the retrieved identifier to its meaning is wrong.

For architectures that consume labels directly rather than a mapping table, the preregistration must specify an equivalent slot-preserving permutation. If byte/token parity cannot be achieved without altering other factors, the arm is invalid.

**Isolates**

Whether the particular concept/relation-to-meaning mapping matters, rather than generic typed labels or a trained structured-input channel.

**PASS**

`LCB95(Y(F) − Y(P)) > δ_attr,k`.

**FAIL**

No claim that the learned or declared concept mapping is causally used. Attention changes, label decodability, or unit naming do not repair the failure. `[SV]` This intervention-first requirement is supported by the RULE causal-evidence audit ([RULE §3](/home/ec2-user/css/kernel/kernel-of-truth/reports/lit-p3-rule.md:315)).

### 3.3 Structurally matched irrelevant records — `I`

**Construction**

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

**Isolates**

Relevant content versus “more tokens,” structured formatting, extra memory accesses, or invoking a tool.

**PASS**

`LCB95(Y(F) − Y(I)) > δ_attr,k`.

**FAIL**

The claimed gain is consistent with token count, format, or generic tool invocation. No content-specific claim is licensed.

### 3.4 Edge/relation shuffle and topology attack — `G-edge`, `G-rel`, `G-adv`

Required for every graph, relational-structure, rule-composition, or topology claim.

**Edge-shuffle construction**

- Start from the same retrieved node set and node attributes.
- Apply directed degree-preserving double-edge swaps within relation/type-compatible strata.
- Preserve node count, edge count, per-relation edge counts, per-node in/out degree, retrieval results, and all textual node attributes.
- Reject duplicates, forbidden self-loops, or type-invalid edges.
- `[STIPULATED — coordinator/Fable to ratify]` At least 90% of original edge incidences must change.

**Relation-shuffle construction**

- Keep endpoints/topology fixed.
- Derange relation labels across type-, arity-, and direction-compatible edges.
- Preserve the complete relation-label histogram.
- `[STIPULATED — coordinator/Fable to ratify]` At least 90% of label assignments must change.

**Calibrated structural attack**

`[SV]` Deceive-KG shows that semantics can be destroyed while downstream performance survives; GTEval shows text-carrying fused models nearly unchanged under PRBCD while a graph-only model collapses. These are the reason a uniform shuffle and a targeted structure attack are both required—not evidence that either specific future arm will fail ([FUSE crux](/home/ec2-user/css/kernel/kernel-of-truth/reports/lit-p3-fuse.md:244), [FUSE controls](/home/ec2-user/css/kernel/kernel-of-truth/reports/lit-p3-fuse.md:409)).

- Use PRBCD where technically applicable; otherwise preregister a topology-only black-box attack with the same validation shape.
- `[STIPULATED — coordinator/Fable to ratify]` Select the lowest edit budget from `{1%, 2%, 5%, 10%, 20%}` that causes a simultaneous `LCB95` drop of at least `δ_attr,k` in a frozen graph-only positive control on calibration data.
- Freeze that budget and attack implementation before evaluating \(F\).
- If no budget validates the positive control, the structure instrument is invalid.

**PASS**

Each required arm independently satisfies:

- `LCB95(Y(F) − Y(G-edge)) > δ_attr,k`;
- `LCB95(Y(F) − Y(G-rel)) > δ_attr,k`;
- `LCB95(Y(F) − Y(G-adv)) > δ_attr,k`.

On generator-backed items where the transformed graph has a recomputable target, report whether the answer follows the transformed structure. Mere indiscriminate damage is necessity evidence, not proof of correct structural reasoning.

**FAIL / mandatory kill**

Failure of any required structure contrast kills the graph/structure attribution. A delivery probe showing that graph tokens contain topology does not override this kill: nsk1 and GTEval both exhibit delivery without behavioural integration ([programme premise](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/programme-3-neurosymbolic-architecture.md:175), [FUSE finding](/home/ec2-user/css/kernel/kernel-of-truth/reports/lit-p3-fuse.md:66)).

### 3.5 Aligned non-kernel typed store — `T`

No published instrument located in the reviewed literature supplies this control directly. `[SV]` This is therefore a first-party control proposal, not a literature-established measurement.

**Construction**

1. A query-blind compiler consumes the same frozen source-evidence snapshot as the kernel store.
2. It emits plain-English typed records with generic local identifiers, provenance, timestamps, aliases, and proposition/rule text.
3. It preserves all source-level information and query alignment but removes:
   - kernel URNs and canonical axiom identities;
   - kernel-specific normalization/equivalence classes;
   - dependency/proof DAGs;
   - executable kernel semantics;
   - kernel-specific traversal or inference rules.
4. Record count, schema/type shape, evidence entitlement, provenance, query alignment, retrieval positions, and LM-visible context ceiling match the kernel arm.
5. The compiler emits a bidirectional proposition inventory showing that every atomic source proposition available to one arm has a corresponding representation in the other.
6. Run both:
   - retrieval-only typed records;
   - the strongest admissible generic typed-tool version using schema-neutral lookup/filter/join or other predeclared generic tools.
7. Use the better admissible typed-store result as \(T^\*\). Do not select between variants after test outputs.
8. Both variants receive the same byte ceiling and complete build/query ledgers. A smaller typed store is not padded.

Query-specific answers or conclusions may not be materialized. Query-blind closure generated before the benchmark/store freeze is permitted only if the same closure policy is available to all applicable baselines and its bytes/build cost are counted.

**Isolates**

Kernel-specific semantics versus aligned typed storage, retrieval, provenance fields, and generic tools.

**PASS for a kernel-semantic claim**

`LCB95(Y(F) − Y(T*)) > δ_attr,k`.

**FAIL**

The gain is attributed to aligned typed storage/retrieval or generic tooling. The parent requires that result to be reported “whatever [it] show[s]” ([parent W1 condition 4](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/programme-3-neurosymbolic-architecture.md:400)). A resource-frontier system result may remain only under a preregistered typed-store label; “kernel semantics” is prohibited.

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
- the same total tuning CPU/accelerator budget and frozen dev-selection rule.

Use the strongest admissible preregistered RAG/tool configuration as \(R^\*\). Actual smaller artifacts remain eligible and are not padded.

`[SV]` Also freeze and report retrieval recall, record/source provenance, popularity strata, context order, position-shuffle sensitivity, and a random-document control. These are required by review edit #9 ([review](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kot-fair-2-review1-freeze-readiness.md:173)).

Two RAG comparisons are required:

1. a same-host, shared-retrieval attribution cell;
2. the strongest admissible G4 RAG/tool family from the frontier-builder.

**Isolates**

Whether the result requires kernel machinery, rather than access to the same corpus through conventional retrieval, prompting, in-context editing, or generic tools.

**PASS**

Because \(R^\*\in F(B_k)\), the inherited W1 rule applies verbatim:

`LCB95(INDEX(F) − INDEX(R*)) > δ_k`.

`[SV]` AxBench and RippleEdits are specific warnings that prompting or in-context access can beat apparently more sophisticated internal machinery ([RULE audit](/home/ec2-user/css/kernel/kernel-of-truth/reports/lit-p3-rule.md:345)).

**FAIL**

W1 fails against the neural/RAG frontier. It cannot be rescued as a kernel win.

### 3.7 Kernel-as-text null — `X`

**Construction**

1. Retrieve the same records/subgraph and, when executor-on, the same deterministic results and provenance.
2. Render them as text rather than passing them through graph tokens, KV injection, activation steering, adapters, or another privileged internal seam.
3. Share base weights, task data, trainable-parameter ceiling, tuning budget, retrieved information, and LM-visible token ceiling.
4. Select the strongest text serialization using the frozen dev split.
5. `[SV]` The serialization battery must cover the preregistered canonical encodings rather than a single weak rendering; serialization is a first-order graph baseline choice ([FUSE controls](/home/ec2-user/css/kernel/kernel-of-truth/reports/lit-p3-fuse.md:419)).
6. Charge serialization, prompt construction, prefill, and all text tokens.

If all information cannot fit under the shared token ceiling, reduce the common record set before freeze. Silently truncating only the text arm invalidates the control.

**Isolates**

Neural-symbolic integration/interface value over delivering the same kernel information as ordinary text.

**PASS for an integration claim**

`LCB95(Y(F) − Y(X*)) > δ_attr,k`, where \(X^\*\) is the strongest preregistered text serialization.

**FAIL**

No internal-integration claim. If text retains the result, attribution is “kernel information delivered as text.” If text is harmful but \(F\) merely returns to baseline, that does not establish a positive integration mechanism.

### 3.8 Executor and retry/search factor cells

These cells are necessary because the parent’s six-way decomposition explicitly separates deterministic execution and retry/search.

**Executor-bypass arm — `E0`**

- Keep kernel content, retrieval, tool invocation, and engine computation.
- Charge all engine work.
- Prevent engine results, masks, traces, or accept/reject decisions from affecting generation or candidate choice; log them post hoc only.
- Compare against executor-on with retry disabled in both cells.

Execution attribution requires:

`LCB95(Y(K,E1,Q0) − Y(K,E0,Q0)) > δ_attr,k`.

**One-shot arm — `Q0`**

- Keep retrieval and deterministic execution.
- Return the first candidate; no outcome-conditioned retry or search.

**Matched generic-search arm — `Qsham`**

- Generate the same frozen maximum number of candidates.
- Hide the kernel verdict during candidate selection.
- Select using the strongest preregistered non-kernel selector or neural verifier fitting the budget.
- Charge every candidate, engine call, selector, and backtrack.

Retry/search attribution is reported as:

- total retry/search: `Y(F) − Y(Q0)`;
- kernel-conditioned selection beyond generic search: `Y(F) − Y(Qsham)`.

A claim naming deterministic execution or kernel-guided retry must clear the corresponding simultaneous `δ_attr,k` margin. Otherwise that dimension is `NOT ESTABLISHED`, even if another kernel dimension passes.

## 4. Six-way attribution procedure

The attribution is a contrast ledger, not six percentages forced to sum to the total. Interactions are reported rather than allocated according to an arbitrary ordering.

| Attribution dimension | Primary controlled contrast | Interpretation |
|---|---|---|
| Kernel semantics | \(F-T^\*\), supported by \(F-D\), \(F-P\), \(F-I\) | Kernel-specific meaning beyond aligned typed records |
| Structured storage | same-host \(T^\*-R_{\text{shared}}\) | Benefit of typed/structured storage available without kernel semantics |
| Retrieval | \(R_{\text{relevant}}-R_{\text{random}}\), plus recall/provenance | Benefit from retrieving relevant evidence rather than supplying context tokens |
| Deterministic execution | \(Y(K,E1,Q0)-Y(K,E0,Q0)\) | Causal effect of engine output, independent of retry |
| Retry/search | \(F-Q0\) and \(F-Qsham\) | Generic extra search versus kernel-conditioned search |
| Neural-symbolic integration | \(Y(K,\text{native},E1,Q0)-Y(K,\text{text},E1,Q0)\) | Benefit of the internal seam over matched text delivery |

At minimum, report semantics×executor, semantics×retrieval, and integration×executor interactions wherever the cells exist. An interaction larger than either named main contrast is reported as such; it is not assigned post hoc to the preferred mechanism.

### 4.1 Claim gate

`[STIPULATED — coordinator/Fable to ratify]`

Set:

\[
\delta_{\text{attr},k}=\delta_k.
\]

Reason: a statistically detectable sliver should not inherit a claim whose competitive meaning is a rung-level \(\delta_k\) improvement.

For a full “kernel-mechanism neurosymbolic win,” define:

\[
J_{\text{core}}=\{D,P,I,T^\*,R^\*,X^\*\},
\]

plus `G-edge`, `G-rel`, and `G-adv` for every graph/structure claim. Add `E0`, `Q0`, or `Qsham` when the claim names execution or retry/search.

The mechanical attribution statistic is:

\[
A_k=\min_{j\in J_{\text{claim}}}
  \left\{LCB95\bigl(Y(F)-Y(j)\bigr)-\delta_{\text{attr},k}\right\}.
\]

A kernel-mechanism attribution passes only if \(A_k>0\) and W1 itself passes.

### 4.2 Verdict ladder

1. **W1 frontier gate fails:** `W1-FAIL`; controls remain diagnostic.
2. **Required arm missing, unmatched, inadmissible, or invalid:** `INSTRUMENT-INVALID`; no win claim.
3. **Derangement, permutation, or irrelevant-content gate fails:** store-content/kernel claim killed. No post hoc “more context helped” W1 fallback unless separately preregistered.
4. **Graph shuffle or calibrated attack fails:** structure/topology claim killed.
5. **Aligned typed store matches \(F\):** result attributed to typed storage/retrieval; no kernel-semantics wording.
6. **Matched RAG matches or beats \(F\):** W1 fails because RAG is in \(F(B_k)\).
7. **Kernel-as-text matches \(F\):** kernel information may matter, but internal integration is unestablished.
8. **Executor or retry contrast fails:** that component is not credited; other preregistered dimensions may still be evaluated.
9. **W1 and all claim-relevant contrasts clear their simultaneous margins:** `W1-PASS — KERNEL-MECHANISM ATTRIBUTED`, restricted to the tested rung, suite, budget, and declared dimensions.

Controls may reveal a legitimate generic typed-store or text-delivered result. They prevent that result from being laundered into a kernel-specific or structure-causal claim.

## 5. KOT-FAIR/2 and P3-D-INDEX integration

P3-D-THREAT gates P3-D-INDEX freeze, and every G4/W1 experiment is already blocked on both plus the matched-RAG design and calibration ([programme work graph](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/programme-3-neurosymbolic-architecture.md:928), [Phase-2 blocking rule](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/programme-3-neurosymbolic-architecture.md:950)).

The controls enter KOT-FAIR/2 as follows:

- **§0 Threat register:** replace the implicit malicious-adversary framing with the single motivated-operator model above.
- **§5 Anti-confound machinery:** add the complete arm manifest, parity certificates, transformation hashes, and PASS/FAIL meanings.
- **P3-D-RAGC:** owns the RAG renderings, shared/native retrieval cells, random-document/position controls, and identical ledgers.
- **P3-D-FRONTIER:** tunes RAG, prompting, generic tools, adaptive test-time compute, and neural verifiers under the same total tuning-compute rule.
- **Family designs:** P3-D-GNN freezes graph shuffle/attack details; P3-D-RULE freezes interchange/executor controls; every store-touching family instantiates the common spine.
- **P3-D-INDEX:** freezes the complete control manifest, grader logic, claim ladder, multiplicity family, and ratified constants before P3-E-CAL.
- **P3-E-CAL:** validates the perturbation generator and graph positive control, but does not treat either as architecture evidence.

All controls run on both the frozen public suite and the sealed suite. For sealed items, the custodian or pinned generator runs the already-frozen transformation code without exposing item-level content to the developer.

### 5.1 Statistics and multiplicity

The parent’s house rule remains verbatim: a margin claim requires `LCB95(Δ)>δ`, with simultaneous confidence bounds/FWER control across preregistered comparators and domains ([parent §2.5](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/programme-3-neurosymbolic-architecture.md:571)).

`[STIPULATED — coordinator/Fable to ratify]` Use a frozen two-stage gatekeeping procedure:

1. W1 frontier and domain non-inferiority family;
2. only if stage 1 passes, the attribution-control family.

Within each stage, use simultaneous one-sided max-t bounds at family-wise \(\alpha=0.05\). The attribution family includes every required `F − control` contrast and any domain-level mechanism claims. A RAG comparison already present in stage 1 is reused rather than tested twice.

For the fixed-suite estimand:

- keep benchmark and domain weights fixed;
- resample the appropriate item clusters within each benchmark—story, rule template, source document, paraphrase family, or equivalent;
- preserve all system/control outputs for an item as a pair;
- include perturbation seed as a crossed randomization factor;
- include training seed as a top-level random effect when the claim concerns a training procedure rather than one frozen artifact.

This incorporates the review’s correction to the draft bootstrap ([review statistics](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kot-fair-2-review1-freeze-readiness.md:137)).

The kill is conjunctive. No large win against one control compensates for failure against another. A low-powered valid result that does not clear its bound is a failed claim at that rung, not affirmative evidence of no causal effect; an invalid arm blocks the claim entirely.

### 5.2 Correctness claims

This proposal does not decide whether correctness becomes a second success claim, a conjunctive W1 gate, or a correctness–coverage–cost Pareto axis. That remains the coordinator/Fable decision identified in review Part C ([review](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kot-fair-2-review1-freeze-readiness.md:181)).

If a correctness claim is authorized, it needs the analogous control set over:

- dangerous-wrong probability;
- selective risk and coverage;
- accepted/provenance-backed soundness violations;
- end-to-end semantic correctness;
- graph counterfactual following where relevant.

The aligned typed-store, strongest neural/RAG selective-prediction baseline, text null, execution bypass, retry/search controls, and structure attacks remain mandatory. Endpoint-specific correctness margins and rare-event sample sizes belong to the separate correctness design; they are not fixed here.

## 6. `[STIPULATED]` values and rules needing ratification

1. `[STIPULATED — coordinator/Fable to ratify]` Use \(\delta_{\text{attr},k}=\delta_k\) for every claimed mechanism contrast.
2. `[STIPULATED — coordinator/Fable to ratify]` Use the SHA-256 seed-derivation scheme, five initial perturbation replicates, pre-output power-based increases, mean-over-seeds estimand, and no rerolling.
3. `[STIPULATED — coordinator/Fable to ratify]` Interpret “equal bytes” as equal canonical byte entitlement with no padding; smaller controls remain eligible and stronger.
4. `[STIPULATED — coordinator/Fable to ratify]` Require the aligned typed-store proposition-equivalence certificate and both retrieval-only and strongest generic-tool variants.
5. `[STIPULATED — coordinator/Fable to ratify]` Require shared BM25, shared dense, native conventional-RAG, position-shuffle, random-document, recall/provenance, popularity-stratified, and frozen-context-order cells.
6. `[STIPULATED — coordinator/Fable to ratify]` Require ≥90% changed edge incidences and ≥90% changed relation assignments in uniform structure shuffles.
7. `[STIPULATED — coordinator/Fable to ratify]` Calibrate the topology attack on `{1%, 2%, 5%, 10%, 20%}` edit budgets using the lowest budget that drops the graph-only positive control by at least \(\delta_{\text{attr},k}\).
8. `[STIPULATED — coordinator/Fable to ratify]` Require executor-bypass, one-shot, and matched generic-search cells to distinguish execution from retry/search.
9. `[STIPULATED — coordinator/Fable to ratify]` Use fixed-sequence W1→attribution gatekeeping with within-stage simultaneous one-sided max-t bounds at FWER 0.05.
10. `[STIPULATED — coordinator/Fable to ratify]` Run the factorial controls on both public and sealed suites.
11. `[STIPULATED — coordinator/Fable to ratify]` Prohibit post-result claim switching; any typed-store, text-delivery, or generic-retrieval fallback must be separately preregistered and multiplicity-controlled.