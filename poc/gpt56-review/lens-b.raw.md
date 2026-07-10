## 1. Most important coverage gaps

### Generalization

- **External-task generalization is still untested.** `f2b-transfer` may remove kernel-defined gold, but it retains self-authored question style and a kernel-rendered answer surface. `d-ext` establishes zero engagement, while N1-LB is only a proposed coverage-gated evaluation. The programme never asks: *Does the verifier improve an unfiltered population of independently authored questions when neither record selection nor item selection was conditioned on kernel checkability?*

- **Covered-slice representativeness is unmeasured.** `m0b` measures token-mass coverage, not whether covered items are easier, more definitional, less ambiguous, or otherwise selected for likely success. Reporting a blended benchmark identity does not resolve this selection question.

- **The cross-linguistic claim has no cross-linguistic test.** All operative correctness and efficiency evidence is English. The proposed multilingual phrase-compression idea tests token economics, not whether NSM-grounded records map, verify, refuse, and repair correctly on native-authored non-English queries.

- **End-to-end model-family coverage is effectively one family.** SmolLM2 supplies the important F2 and A5 evidence. `g1` requires two families and `e8-r` seeks a third, but neither establishes cross-family verifier-offload or decode-verify performance. The programme does not know whether the observed lift is host-specific.

- **There is no measured result at or above 7B.** `f7` is draft, costly, and survivors-only. No experiment asks whether the strongest current seam survives at 7B or 14B before a frontier narrative is entertained. Survivors-only scaling also cannot reveal that a mechanism failed for qualitatively different reasons at larger scale.

### Failure-mode characterization

`e9-full` commendably requires an error-class breakdown, and `e9-c` separates decode from axiom-authoring failure. But there is no corresponding diagnostic for the programme’s only demonstrated end-task lift, `f2b-replicate`.

The missing questions are:

- When verification harms an initially correct answer, was the cause a mapper error, over-narrow canonical answer set, bad axiom, ambiguous question, retry instability, or extraction?
- Are failures concentrated by concept, template, author, query operation, or refusal type?
- Does increasing `k` repair errors or systematically amplify a wrong verifier decision?
- Are apparently random errors actually repeated failures on a small set of records?
- When the gloss baseline wins, what information or flexibility did it retain that the kernel arm removed?

Without this, a FAIL says little about what should be fixed, and a PASS can conceal a harmful-flip subgroup.

### Deployment realism

All important cells are offline benchmark cells. The programme does not ask:

- What are p50/p95/p99 latency, throughput, queueing, cache behaviour, timeout rate, and actual cost/query under concurrent serving?
- Does retry create tail-latency spikes even when mean FLOPs look favourable?
- Does a multi-turn system preserve the correct kernel version and assumptions across turns?
- Can an agent enter verification/retry loops or act on a wrongly “verified” intermediate claim?
- What happens when source records change, sidecars become stale, or model traffic drifts away from the authored coverage distribution?
- How much operational burden comes from version rollout, cache invalidation, monitoring refusals, and repairing bad authored records?

FLOPs and static USD estimates cannot answer these questions.

### Kernel-specific attribution

The shuffled-kernel null proves that **correct content alignment matters**. It does not prove that the distinctive kernel machinery matters.

The programme still does not ask, on an end task:

- Does the NSM prime basis outperform an arbitrary but fixed typed vocabulary carrying the same facts?
- Does Construction B—Hadamard binding plus HRR—outperform a lossless canonical AST, sparse vector, or ordinary content-addressed identifier?
- Does the axiom engine win because it is deterministic, because it has better coverage, or because it has effectively been given a canonical answer table?
- Would conventional typed JSON/Datalog records with the same parser, facts, retry controller, and authoring budget produce the same lift?
- How much variance comes from authoring quality rather than representation?
- Do vectors contribute at all to the external-verifier seam, or is that seam’s value entirely in canonical records and deterministic membership checking?

`g1` partly addresses basis choice through F4, but it does not attribute the F2/e9 correctness lift. No current end-task ablation isolates Construction B.

### Adversarial robustness

The derangement null and deranged-gloss probe are scientific controls, not security tests. H-FAB tests ordinary unsupported queries, not an attacker.

Missing questions include:

- Can retrieved text inject instructions that bypass or redirect verification?
- Can Unicode confusables, aliases, malformed records, contradictory axioms, or parser differentials cause unsafe acceptance?
- Does deliberate ambiguity produce principled refusal or arbitrary canonicalization?
- Can a schema-valid but adversarial sidecar make a desired false answer appear licensed?
- Can an author maximize benchmark acceptance by writing overly broad axioms?
- Does the engine fail closed under resource-exhaustion inputs, cyclic rules, oversized clauses, or version mismatches?

Determinism makes attacks reproducible; it does not make the system robust.

## 2. Cheapest experiments that close each gap

| Gap | Cheapest useful experiment | Decision it enables |
|---|---|---|
| External domain and covered-slice selection | **`x-domain-1`**: 300 unfiltered questions from one independently maintained, non-code operational domain. Freeze source documents and questions before kernel authoring; representation authors cannot see evaluation items. Score all items, not only checkable ones, and compare difficulty/error rates between covered and uncovered strata. Primary: all-item accuracy delta over gloss-self-verify at matched cost. | Distinguishes an external population-level benefit from a covered-slice-only niche. |
| Natural languages | **`x-lang-1`**: 100 native-authored items each in English plus two typologically distinct languages, with native adjudicators and both native-original and translated-item strata. Run model-alone, kernel-verify, and native-gloss self-verify. Primary: minimum within-language kernel lift. | Tests three languages only; a PASS would justify broader multilingual work, not “NSM universality.” |
| Model families | **`f2b-family-replicate`**: rerun only the five load-bearing arms—alone, kernel, shuffled, gloss active, text passive—on one unrelated open-weight family at a matched parameter rung. | Determines whether the existing lift is at least two-family rather than SmolLM2-specific. |
| Parameter scale | **`f2b-14b-sentinel`**: 250 items, three seeds, at one approximately 14B host; retain kernel, shuffled, gloss-active, and model-alone arms. Primary: kernel-versus-gloss accuracy delta at matched retry budget. | Measures the sign beyond the current envelope. One rung licenses no slope. |
| Failure modes | **`f2b-errors`**: structured per-attempt logging plus blind adjudication of every harmful flip and a random sample of persistent failures. Freeze mutually exclusive causes before viewing outputs. Primary: proportion of failures assigned to a reproducible cause; also report record/template clustering and harmful-flip rate. | Routes work toward mapper, grammar, authoring, retry policy, or extraction rather than treating all FAILs alike. |
| Deployment realism | **`serve-1`**: replay a frozen request trace through an actual serving stack at concurrency {1, 8, 32}, including cache-cold, cache-warm, timeout, and version-update cells. Primary: cost/query at a predeclared p95-latency SLO; report p99 and retry amplification. | Establishes deployability of the seam, but not real-user utility. |
| Multi-turn/agentic use | **`agent-1`**: 100 three-to-five-turn tasks containing changing assumptions and tool results. Compare kernel verification of intermediate claims against gloss verification. Primary: final-task correctness; safety gate on “verified but false” intermediate actions. | Determines whether single-turn gains survive stateful use without licensing general agent safety. |
| Mechanism attribution | **`abl-kernel-1`**: on external gold, compare full kernel with (a) canonical AST identifiers replacing Construction B, (b) ordinary typed predicates/Datalog replacing NSM, and (c) the same deterministic retry topology over gloss text. Hold source facts and query parser fixed. | Separates NSM, binding, deterministic checking, and content coverage. |
| Adversarial robustness | **`adv-1`**: CPU grammar/property fuzzing plus 200 independently written attacks covering prompt injection, ambiguity, contradictions, confusables, malformed records, version mismatch, and adversarial sidecars. Primary: unsafe-acceptance rate; gate on parser crashes/nontermination. | Determines whether deployment work may proceed or robustness must precede it. |

The failure taxonomy and serving replay can often reuse a successor run’s structured logs, but they must be frozen before those outputs are inspected. They cannot be retrofitted post hoc and retain confirmatory status.

## 3. Single strongest missing experiment

### `x1 — blind external representation-ablation trial`

**Question.** On unfiltered, independently authored questions from domains not used to design the programme, does the *specific NSM/Construction-B kernel* produce a population-level correctness gain and an all-in efficiency advantage over both active text verification and a conventional deterministic symbolic store containing the same source information?

This is the strongest missing experiment because the current evidence leaves two central explanations entangled:

1. The kernel has a distinctive, generalizable representational advantage.
2. Any aligned canonical answer store connected to a deterministic retry loop would have produced the lift.

The shuffled-kernel result rejects “retry against arbitrary content.” It does not distinguish those two explanations.

### Design shape

Use two predeclared external domains with different surfaces—for example, a rule-heavy public-service eligibility domain and a procedural consumer troubleshooting domain.

For each domain:

1. Pin the source documents before any representation work.
2. Have an independent item team produce 300 natural questions and external gold from those documents. They see neither representation.
3. Have separate representation teams, blinded to the questions, encode the documents under a matched person-hour cap.
4. Score the complete 600-item population. Kernel checkability is a measured mediator, never an inclusion criterion.
5. Use two unrelated model families at a matched ≤1.7B rung. A 7B cell can be a gated confirmatory extension, not part of the initial claim.

Arms:

- small-model-alone;
- full NSM + Construction-B kernel verify/retry;
- **AST ablation:** same explications and axioms, but ordinary canonical AST/content IDs replace the Hadamard/HRR vectors;
- **generic-symbolic ablation:** the same source facts and rule inventory represented as conventional typed predicates/Datalog;
- gloss-text self-verify+retry;
- shuffled-kernel verify/retry;
- larger-model-alone as the offload reference.

The query parser, retry controller, `k`, extraction instrument, hardware, and allowable source information must be identical across structured arms. Authoring effort, storage, serving cost, and achieved checkability belong on the ledger.

Include a separately scored challenge stratum of ambiguous, unsupported, contradictory, and injection-bearing inputs. Do not mix its artificial prevalence into the natural-population primary.

### Primary metric

`external_all_item_kernel_specific_delta`:

\[
\min_{\text{domain, family}}
\left[
Acc(\text{full kernel}) -
\max\{Acc(\text{AST}),Acc(\text{generic symbolic}),Acc(\text{gloss active})\}
\right]
\]

Use paired, simultaneous confidence bounds because every arm sees the same items. A reasonable materiality threshold is +0.05 absolute, frozen before data.

### Verdict rules

**PASS** iff all of the following hold:

- the simultaneous 95% lower bound for the primary metric exceeds +0.05;
- the gain holds in both domains and both model families;
- kernel-verify is non-inferior to the larger-model reference on all-item accuracy;
- its measured all-in cost/query, including amortized authoring at a frozen query volume, is lower than that reference;
- shuffled-kernel recovery remains below the existing 30% ceiling;
- the unsafe-acceptance Wilson upper bound on the challenge stratum is below a predeclared safety threshold.

**FAIL-KSPEC** iff TOST establishes equivalence between the full kernel and either simpler structured ablation at a narrow frozen margin. Failure merely to reject is `INCONCLUSIVE`, not equivalence.

**FAIL-ECOLOGY** iff the kernel has a positive covered-slice effect but the valid upper bound on all-item population lift is ≤0.

**FAIL-EFFICIENCY** iff correctness survives but the actual all-in cost or serving SLO does not beat the larger-model reference.

**FAIL-ROBUSTNESS** iff the unsafe-acceptance or nontermination gate fires.

### What the result changes

A **PASS** would license a very specific claim: on two external domains, two tested model families, and the tested parameter range, the distinctive kernel representation beats simpler deterministic symbolic and active-text alternatives while providing measured offload economics. That would justify spending on 14B scaling, multilingual replication, and a shadow-serving pilot. It would not license universal NSM grounding, broad benchmark superiority, or frontier scaling.

A **FAIL-KSPEC** would be more valuable than another aggregate accuracy result. It would say that deterministic structured verification is useful but NSM and/or Construction B do not earn their complexity on this seam. The programme should pivot toward the simpler typed symbolic architecture, retaining the kernel only where provenance, interoperability, or compression independently justify it.

A **FAIL-ECOLOGY** would establish coverage and mapper engagement—not host scale—as the binding constraint. Frontier GPU work should stop while coverage growth and external-item parsing are addressed.

A **FAIL-EFFICIENCY** would narrow the programme to a correctness/governance system rather than verifier-offload.

A **FAIL-ROBUSTNESS** would block agentic or production deployment until the parser, sidecar trust model, and fail-closed behaviour are redesigned.

Those branches alter architecture and spending priorities; they do not merely add another benchmark cell.

## 4. Honesty-rail self-check

- **No universal generalization claim.** Two domains, three languages, two families, or one 14B rung remain exactly that. None licenses “cross-domain,” “cross-linguistically universal,” or a scaling slope without further replication.

- **No checkable-slice primary.** Conditioning the main analysis on items the kernel can answer would recreate the selection problem. All-item population accuracy must be primary; covered-slice results are mechanistic secondaries.

- **No post hoc failure taxonomy.** Categories, adjudication rules, and clustering analyses must freeze before outputs are viewed. Otherwise the taxonomy becomes storytelling.

- **Matched symbolic baselines are an instrument risk.** If the generic representation receives less authoring skill, worse tooling, or less source information, a kernel win would be uninterpretable. Use matched information and crossover authoring where practical; material imbalance should yield `INSTRUMENT-INVALID`.

- **Adversarial prevalence must not be presented as real-world incidence.** A challenge suite estimates conditional vulnerability under specified attacks, not production attack frequency.

- **Replay is not deployment.** `serve-1` can validate engineering SLOs under a trace; it cannot establish user behaviour, long-term drift, or real operational reliability.

- **External gold can still be contaminated.** Item and gold authors must be representation-blind, source versions pinned, and “cannot determine” permitted. Kernel-style answer options should not be the only response surface.

- **The proposed omnibus experiment is deliberately demanding.** Failure of its conjunction does not automatically kill every component. Its typed FAIL routes are necessary to prevent a cost failure from masquerading as a semantic failure, or a coverage failure from masquerading as evidence against deterministic verification.
