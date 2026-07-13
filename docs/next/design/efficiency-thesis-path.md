# Efficiency-thesis decisive critical path — design (GPT-5.6, coordinator-transcribed)

> GPT-5.6 (codex, xhigh) design of the decisive powered efficiency test, transcribed by the coordinator.

# EFFICIENCY-CP — decisive efficiency-thesis critical path

## Status and recommendation

EFFICIENCY remains INCONCLUSIVE-PENDING with zero live thesis-grade data. Issue #27 redirects the primary efficiency lane from underpowered DDC to GLM-5.2 expert-drop, while permitting DDC only as a disclosed secondary ([README](<README.md:58>); [GLM-DROP decision record](<docs/next/design/glm52-expert-drop.md:13>)).

**Recommendation:** run GLM-DROP first, after F1-K, but designate it thesis-bearing only after a no-spend power repair. The present eight-cluster design has simulated 80%-power MDE ≈16 accuracy points and power 0.119 at a true +3; that is adequate for detecting a large effect, not for a decisive efficiency non-demonstration ([GLM-DROP power record](<docs/next/design/glm52-expert-drop.md:862>)). If the repair cannot meet the registered power gate inside the cost ceiling, retain GLM-DROP as a screening systems experiment and do not call it the EFFICIENCY verdict.

This recommends an experiment order and licensed interpretations. It does not determine the programme’s fate.

## 1. Primary claim

### E-GLM: kernel-specific active-expert shrinkage

On the frozen concept-covered public-QA workload, a training-free kernel-concept mask enables GLM-5.2 to use at least 40% fewer routed-expert loads than full TOPK=8 while:

1. remaining non-inferior to full TOPK=8 on cluster-balanced accuracy, with margin −4.0 percentage points; and
2. preserving more accuracy than each of the following at the same realized expert-load budget:

   - uniform router TOPK truncation;
   - pooled frequency-based retention;
   - matched-cardinality embedding-cluster-conditioned retention; and
   - dose-exact, label-deranged kernel masks.

A PASS is the conjunction of every condition. There is no best-of comparator and no multiplicity relief in the kernel’s favour.

Formally, let \(Q(a)\) be cluster-balanced accuracy and \(L(a)\) mean realized experts-loaded/token. With `b0-full`, `u-topk`, `m-freq`, `m-emb`, `m-drng`, and `m-kern` defined as in the existing arm table ([GLM-DROP arms](<docs/next/design/glm52-expert-drop.md:468>)), E-GLM passes only if:

- \(L(m_{\text{kern}})/L(b0) \le 0.60\);
- every reduced arm is within ±5% of \(L(u_{\text{topk}})\);
- the one-sided 95% lower confidence bound for \(Q(m_{\text{kern}})-Q(b0)\) exceeds −4.0 points;
- the one-sided 95% lower confidence bound exceeds zero separately for:

  - \(Q(m_{\text{kern}})-Q(u_{\text{topk}})\);
  - \(Q(m_{\text{kern}})-Q(m_{\text{freq}})\);
  - \(Q(m_{\text{kern}})-Q(m_{\text{emb}})\); and
  - \(Q(m_{\text{kern}})-Q(\operatorname{mean}_R m_{\text{drng},R})\).

The engine counter, not nominal TOPK, determines resource matching; it already absorbs MTP union loading and is the physical I/O/compute quantity ([matched-load protocol](<docs/next/design/glm52-expert-drop.md:639>)).

The P0 1.9× and 2.5× observations are not a no-drop baseline to “beat” with a still larger speed ratio. They establish that uniform TOPK=4/2 is already a free efficiency lever. The kernel earns a sentence only by moving the quality–resource frontier beyond that exact arm, and beyond the embedding-conditioned arm, at the same reduced expert budget. The P0 wall-clock ratios remain preliminary because cache hit rate changed across the sequential sweep ([P0 qualification](<docs/next/design/glm52-expert-drop.md:233>)).

### Licensed PASS wording

> On the frozen concept-covered QA workload, training-free kernel-concept masks reduced GLM-5.2 routed-expert load by at least 40%, retained full-model cluster-balanced accuracy within the registered four-point margin, and preserved more accuracy than uniform router truncation, pooled-frequency retention, matched embedding-cluster conditioning, and dose-exact deranged labels at the same expert-load budget. EFFICIENCY is supported at this model, box, workload and active-expert-shrinkage seam.

This licenses no claim about general workloads, natural-input mapping, small-model/large-model parity, a physically smaller checkpoint, an exact wall-clock speedup, or favourable total deployment economics. Per-item masks also do not imply a 25%-sized deployable shard; their union footprint must be measured separately.

### Non-PASS wording

- **Power or coverage gate fails:** “The decisive question was not run because the available design could not resolve its registered effect at admissible cost.”
- **Load/dose/distinctness gate fails:** `INSTRUMENT-INVALID`; no direction is inferred.
- **Kernel retains quality but loses an embedding, frequency, or deranged-label contrast:** “Reduced-expert inference worked, but a kernel-specific efficiency increment beyond generic conditioning was not demonstrated.”
- **Kernel beats controls but misses full-model non-inferiority:** “Kernel guidance improved reduced-budget quality but did not demonstrate capability retention within the registered margin; EFFICIENCY is not supported by this run.”
- **Clean powered non-demonstration:** “No kernel-specific advantage of the registered five-point planning scale was demonstrated on this model, workload and seam.” This is not equivalence, “the kernel adds nothing,” or a programme-wide negative.

The registry must explicitly supersede the current clause saying GLM-DROP cannot move EFFICIENCY before preregistration; otherwise the narrower existing claim cap remains binding ([current outcome cap](<docs/next/design/glm52-expert-drop.md:299>)).

## 2. Power and affordability repair

The current map contains 24 prompts collapsed into eight concept clusters. With eight inference units, adding benchmark items barely improves power. The repair is to build concept-level routing fingerprints for the F1-K frozen concept roster, using its outcome-blind carrier-construction contexts but with `KAE` disabled. The target is:

- at least 65 non-empty concept clusters;
- at least eight test items per cluster;
- \(n=1{,}440\), unless the frozen eligible pool is smaller;
- construction contexts disjoint from dev and test items;
- no F1-K carrier vector or test outcome consumed by GLM-DROP.

F1-K already requires the ≥65-cluster/≥8-item geometry and freezes the relevant contexts, trigger map, item lists, templates and span sidecars ([F1-K freeze inputs](<docs/next/design/f1k-freeze-readiness.md:98>); [power gate](<docs/next/design/f1k-freeze-readiness.md:124>)). Routing counters should therefore be recorded during those construction forwards where possible, avoiding another model pass. These are shared construction runs, not shared carriers.

At GLM-DROP freeze, run a pinned simulation over the realized cluster sizes and a preregistered dependence/ICC grid. Require at least 0.80 joint power for the entire conjunction when:

- true \(Q(m_{\text{kern}})-Q(b0)=0\);
- the non-inferiority margin is −4 points; and
- each kernel-versus-control contrast is truly +5 points.

The five-point quantity is the experiment’s planning resolution, not an observed-effect hurdle. If least-favourable joint power is below 0.80, freeze fails before main-phase spend; neither the cluster count nor the margins may be adjusted after seeing test outcomes.

Use cluster-level sign-flip inference with a preregistered Monte Carlo seed and sufficient draws to make Monte Carlo error negligible, importing F1-K’s sign-symmetry basis and dev-chosen BCa fallback. The test split remains untouched until masks, operating point, inference method, power output and table hashes are frozen.

The decisive \(n=1{,}440\) run should be budgeted at the high end of the existing model: approximately 12,050 prefills, 279 instance-hours and $56–78 spot, with a $95 ceiling ([GLM-DROP cost table](<docs/next/design/glm52-expert-drop.md:1133>)). If concept-level traces cannot be collected from already-required F1-K construction forwards, their incremental prefills must be priced before freeze and the ceiling re-approved rather than silently absorbed.

## 3. Candidate instruments

| Instrument | Decisiveness | Power/readiness | Cost | Positive licenses | Mandatory deflator |
|---|---|---|---|---|---|
| **GLM expert-drop** | Direct test of training-free active-expert compute/I/O reduction on a real frontier MoE. Does not by itself prove a smaller stored checkpoint. | Current C=8 form is not decisive; the ≥65-cluster repair above makes it eligible for a powered verdict. | Approximately $56–78 at the decisive \(n=1{,}440\) point; $95 ceiling. | Kernel-specific improvement of the quality–expert-load frontier at one model/box and covered workload. | Uniform TOPK at identical load, frequency mask, embedding-conditioned mask, and dose-exact deranged labels. |
| **Dimension-collapse/DDC** | Cleanest literal test of “shrink a model without retraining”: matched packed parameters/bytes and public-benchmark retention across a sweep. | Not currently runnable as a decisive test. I-5 correctly failed when the informative pool reduced to ARC-Easy and neither superiority nor equivalence reached 0.90 power ([DDC gate](<docs/next/design/DDC.md:727>)). | Nominal campaign ~$40 with $60 cap, but that price buys no decisive run after the failed power gate ([DDC cost](<docs/next/design/DDC.md:862>)). A powered repair must be re-priced. | Training-free physical model shrinkage at matched size on the tested donors. | Matched parameter count, packed bytes and FLOPs; magnitude/random; generic-text, plain-dictionary and shuffled-kernel calibration. |
| **Verifier offload at scale** | Strongest end-to-end test of the thesis’s other disjunct: small host plus deterministic machinery versus a larger host at matched total cost. | Not first-ready. Existing f2b-transfer showed mechanism lift but not non-inferiority to 1.7B, while DECONF-B located the value in a generic aligned answer key rather than kernel-specific runtime structure ([programme record](<README.md:29>)). A real retrieved store and non-vacuous verifier are prerequisites. | Scale design is approximately $500–3,000 inference-only after the data/system pipeline exists, plus substantial construction work ([OFFLOAD-SCALE](<docs/next/design/large-kernel-scale-track.md:658>); [scale estimate](<docs/next/design/large-kernel-scale-track.md:802>)). | Small-plus-kernel verifier matches or beats the larger host at lower end-to-end cost, and typed structure beats a flat/generic verifier. | Large host, host-only, self-consistency at matched cost, flat retrieved store, generic aligned key, rules-off and shuffled mapping/rules. All retries, retrieval, verifier, store update and amortized build costs counted. |

Thus GLM-DROP is the best first instrument on latency, reuse and current authorization; repaired DDC is the better independent confirmation of literal checkpoint shrinkage; OFFLOAD-SCALE is the eventual end-to-end test of the other thesis branch.

## 4. Critical path and sequencing

1. **Before spend:** land the mandatory CPU-only R4 routing replay. Freeze whether kernel labels add information over the embedding conditioner; report that prior alongside the live result regardless of direction. This is already a prerequisite of #27 ([GLM-DROP sequencing](<docs/next/design/glm52-expert-drop.md:1187>)).

2. **F1-K freezes first:** freeze the shared kernel version, concept roster, construction contexts, trigger map, dev/test item IDs, templates, scorer and span sidecars.

3. **GLM-DROP freezes before F1-K test outcomes are read:** construct the expanded concept→expert map, masks, power simulation and operating-point protocol from outcome-blind artifacts. No F1-K test score may influence a GLM-DROP choice.

4. **F1-K runs and seals:** terminate its process and record the seal.

5. **GLM-DROP runs on the same spot instance in a fresh process:** reuse model bytes, restored storage, approved combined binary and frozen evaluation carriers. Reset `KAE`, `TOPK`, `TOPP`, `DROP`, `PIN` and `AUTOPIN`; use distinct checkpoints, results, seeds and cost ledger. The existing isolation contract already requires this separation ([co-location contract](<docs/next/design/glm52-expert-drop.md:946>)).

6. **Shared carriers, precisely:** share benchmark carriers and carrier-construction text contexts; do **not** share or inject F1-K carrier vectors. `KAE` remains off throughout GLM-DROP. The only treatment is native-expert eligibility.

7. **Large-kernel work proceeds in parallel but does not rescue this run post hoc:** the current experiment is scoped to its frozen concept roster. A later nested replication may use 10k/100k/1M kernel tiers, but only with a newly frozen map, mapper and benchmark population. A small-kernel negative is not silently reinterpreted as a scale prediction.

8. **After GLM-DROP:** a positive warrants a separately registered hard-shard validation measuring union footprint, packed bytes and controlled wall-clock throughput. A powered DDC repair supplies cross-architecture confirmation. OFFLOAD-SCALE follows only when retrieval, natural-input mapping and a non-vacuous verifier pass their own gates.

## 5. Deflator and preregistration discipline

The following are non-negotiable:

- Freeze all item IDs, cluster assignments, encoder weights, mask bytes, seeds, tie-breaks, operating-point rules and power outputs before test access.
- Compare the kernel against uniform TOPK at the same \(k^\*\), not against full TOPK=8 alone.
- Match masked arms exactly at 64 retained experts/layer, identical universal core, identical label cardinality and ±5% realized loads.
- Make `m-kern`, `m-emb` and `m-drng` the same code path and scoring functional; only the conditioning labels or cluster membership may differ.
- Void a specificity contrast when retained-set Jaccard exceeds 0.95; non-distinct arms are uninformative, not tied.
- Beat every named control separately. Never select the weakest comparator or report a best-of contrast.
- Meter lexical mapping, table lookup and mask-construction overhead. Keep active-expert-load claims distinct from wall-clock, checkpoint-size and total-cost claims.
- For dimension collapse, match retained parameters, packed artifact bytes and measured inference FLOPs—not nominal width alone.
- For verifier offload, match total end-to-end cost including retries, retrieval, deterministic verification, false rejections, store construction/update and amortization.
- A failed superiority test is not equivalence. Any “adds nothing,” “generic structure suffices,” or “retention-free” claim requires its own powered equivalence/non-inferiority test.

This path gives the redirected GLM instrument the earliest credible opportunity to produce an efficiency verdict while preserving DDC and verifier offload as independent tests of the thesis’s literal shrinkage and end-to-end offload forms.
