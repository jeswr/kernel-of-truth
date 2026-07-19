# KOT-FAIR/2 review 1 — freeze-readiness roadmap (GPT-5.6 review + lit-review reconciliation)

> **STATUS: REVIEW OUTPUT — KOT-FAIR/2 is NOT freeze-ready.** GPT-5.6 review of docs/next/design/kot-fair-2-spec-p3mf0.md
> reconciled against the 10 completed Phase-0 lit-reviews, 2026-07-19. 12 ordered reconciliation edits (Part B) + 10
> freeze-readiness requirements + a correctness-instrument gap (Part C) that requires a MAINTAINER/FABLE strategic
> decision before freeze. Definite defects found: floor rule backward (UCB→LCB); parent's mandatory factorial
> attribution controls MISSING from the draft; 3× cost ceilings endogenous/indefensible; energy boundary unsound.
> Source: poc/gpt56-review/p3mf0-review-reconcile/. Actions this before P3-D-INDEX freeze.

---

# Review verdict

KOT-FAIR/2 is a strong framework skeleton, but it is not freeze-ready. After the fixes below it could support a defensible resource-frontier efficiency claim. In its present form it remains materially gameable through:

- scalar compensation across domains;
- energy shifted outside the measured boundary;
- the arbitrary, endogenous 3× secondary-resource ceilings;
- incomplete lifecycle/refresh accounting;
- incomplete matched-twin and matched-RAG specifications;
- omission of the parent’s mandatory factorial attribution controls;
- correctness metrics that are reported but do not participate in any claim.

The statistical principles in §2.5 are mostly correct, but the concrete implementation contains one definite floor-gating error and several under-specified resampling/inference choices.

## Part A — soundness and gameability

### KOT-AI-INDEX/2

Soundness: conditionally sound. Mean-of-normalised-scores, fixed domain macro-weights, frozen scorers, and mandatory vector reporting are the right basic design. This matches HELM’s current method, not its abandoned win-rate method ([EVAL §1](/home/ec2-user/css/kernel/kernel-of-truth/reports/lit-p3-eval.md:35), [draft §1.3](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kot-fair-2-spec-p3mf0.md:117)).

Gameability remains substantial:

- W1 is entirely scalar. A system can buy a large D4 gain with regressions elsewhere and still pass. Publishing the vector exposes this but does not alter the decision. W1 should become scalar superiority plus simultaneous per-domain non-inferiority against the domain frontier. “No regression” should mean a frozen one-sided non-inferiority margin, not an impossible demand that every point estimate increase.
- Domain assignment, benchmark duplication, and family grouping are weight-setting operations. An operator can split a favourable construct into several benchmarks or merge an unfavourable one. Freeze a construct map and benchmark-family clustering, then report sensitivity to plausible groupings.
- The floor rule is statistically backward. Excluding only when `UCB95(score−chance)<.02` admits an uncertain benchmark whose estimate is at chance but whose interval happens to be wide. Inclusion should require `LCB95(score−chance)>f`, or another preregistered discrimination criterion, on the rung anchor.
- “Any three domains” is too weak. Three convenient domains do not establish broad capability. Freeze a required core-domain set per rung.
- The R1 manifest still admits FOLIO and candidate GSM8K despite the review finding that they are weak/floored there. Conversely, low-hop CLUTRR and shallow/depth-stratified ProofWriter should be considered at R0/R1.

The `u=1.000` normalization is defensible for naturally bounded accuracy metrics and is more stable than a reference-model ceiling. The less defensible part is mixing it with BLiMP’s `.964` human-agreement figure: human agreement is not necessarily an attainable upper bound, it can be exceeded, and clipping then changes weights. Prefer a consistent `1.000` ceiling for bounded accuracies, including BLiMP, or justify each empirical ceiling and publish a ceiling-sensitivity analysis. This also needs an explicit amendment to the parent, which currently calls for human/reference ceilings ([parent §1.1](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/programme-3-neurosymbolic-architecture.md:230)).

### KOT-SIZE/2

Soundness: mostly sound. The canonical packer, pre-architecture base freeze, minimal-sufficiency boot test, remote-byte rule, and six co-reported figures close most ordinary packaging games ([draft §2](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kot-fair-2-spec-p3mf0.md:169)).

Residual games:

- A generous “generic” base can still launder runtime functionality. Freeze a minimal allowlisted base, publish its total bytes, and count any runtime used only by one family in that arm.
- Remote corpora are covered, but remote computation/API execution must also be explicitly forbidden or fully metered. Snapshotting data does not account for a remote service’s model, CPU, or energy.
- Compact code that reconstructs a large artifact at startup is legitimate compression, but its generated working set, construction bytes, CPU/energy, and startup latency must all bind—not merely be co-reported.
- Host RSS and VRAM are non-fungible. They need separate ceilings rather than a summed “memory” component.
- Packed incremental bytes support an “incremental artifact size” claim. They do not alone support “total deployment size” unless base+arm bytes are also reported.

No change is needed merely because zstd-19 or whole-file deduplication is stipulated; they are reproducible secondary figures, not scientifically important constants.

### KOT-COST/2

Soundness: blocked on energy; otherwise a good skeleton.

The true open-loop Poisson requirement is already present, including measurement from intended issue time ([draft §3.3](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kot-fair-2-spec-p3mf0.md:288)). It should be strengthened by pinning:

- the latency SLO that defines goodput;
- issued/completed/timed-out/dropped counts;
- queue and timeout policy;
- intended-versus-actual issue-time drift;
- fixed workload mix;
- treatment of unfinished requests.

“1,000 completed queries” alone permits survivorship gaming if timed-out queries disappear.

The energy design is not sound. RAPL package/DRAM plus NVML GPU-board energy is not system energy; disk, NIC, motherboard, PSU losses, remote compute, and sometimes host CPU remain outside the boundary ([SYS §Q7](/home/ec2-user/css/kernel/kernel-of-truth/reports/lit-p3-sys.md:324)). Each record needs first-class fields for boundary, method, counter availability, error band, sampling/wrap handling, and `system_energy_status`. Without wall/IPMI/RedFish measurement, system energy must say `UNMEASURED`, and an apparent win caused by movement into an uncovered domain is `UNPROVEN`. The framework must either obtain a common full-system boundary or amend W1 to bind named component-energy coordinates without calling them total energy.

The 3× anti-laundering ceilings are not defensible:

- “strongest fitting comparator” is endogenous to model selection;
- a slow or I/O-heavy strongest comparator grants S a large allowance;
- a zero-use comparator gives an impossible zero ceiling;
- 3× has no construct, power, or systems basis;
- one factor is inappropriate across CPU, I/O, TTFT, and throughput.

Replace these with preregistered, metric-specific absolute ceilings derived before S is measured, or extend \(B_k\) to include the relevant resource coordinates and construct explicit Pareto budgets. Retain co-reporting even for non-binding coordinates.

The A10G is a reasonable candidate, not a defensible frozen pin yet. Freeze it only after an actual host/SKU probe confirms counter access, reset semantics, RAPL or wall-power availability, storage behavior, and fit for all arms. Claims would remain A10G-specific; a second-platform sensitivity run would materially improve external validity.

The proposed repeatability bands are plausible calibration starting points, not established constants. In particular, the SYS review allows up to 10% within-day energy variation, while the draft applies 5% CoV to energy. Use at least ten repetitions but choose final \(N\) adaptively from a frozen rank-based CI-width rule. Repeatability must gate every W1 arm and comparator, not only P3-E-CAL. Measurement resolution should be assessed in each metric’s own units; a 5% latency drift cannot literally be compared with an index margin of 0.02.

The Offline rule is gameable: “batch 8 or the largest batch fitting all arms” lets one arm force every other arm to a small batch. Pin multiple batch cells, or require batch 8 and mark non-fitting arms inadmissible for that cell.

### KOT-LIFE/1

Soundness: conceptually right, operationally incomplete.

Keeping USD, human-hours, and joules separate is correct. The store schema nevertheless conflates or omits the economically important quantities. It needs explicit per-record-class subledgers for:

- build/mint, including rejected-candidate attrition;
- human review, redundancy and measured quality operating point;
- provenance verification;
- staleness detection and refresh;
- dependency/entailment fan-out, revalidation, reindex and rollback;
- human-time distributions and uncertainty, not only totals.

Refresh cost is not a function of query count alone. Replace `TCO(q)` with at least `TCO(q,t)` or add query rate/deployment duration; otherwise a continuously refreshed one-year deployment and a one-day burst of the same query count look identical.

Human and method-development accounting remains intrinsically gameable through unlogged prior work, failed experiments, and “generic” tooling. Require prospective metering from freeze, include failed candidates, and keep this as a standing limitation. W1 should not be described as overall lifecycle efficiency because KOT-LIFE remains non-binding.

### Anti-confound machinery

Soundness: incomplete and therefore not freezeable.

The largest omission is that the draft does not instantiate the parent’s mandatory factorial controls at all. The parent requires derangement, label permutation, structurally matched irrelevant records, edge/relation shuffle, aligned non-kernel typed store, matched RAG/tool use, and kernel-as-text null, followed by six-way attribution ([parent §2.2](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/programme-3-neurosymbolic-architecture.md:469)). None appears in the draft. This is a direct authority mismatch, not an optional refinement.

The decontamination thresholds—8-gram, MiniLM cosine `.85`, 99% near-verbatim recall, 90% paraphrase recall—are plausible hypotheses, not ratifiable values. A set of 100 paraphrases cannot substantiate 90% population recall with useful precision, especially if threshold selection and evaluation use the same examples. Require:

- separate threshold-development and held-out validation sets;
- multiple independent paraphrase sources;
- confidence bounds on recall/FPR;
- perturbation-based checks on flagged and near-threshold items;
- Min-K-style donor membership diagnostics where logits exist;
- screening of derivation inputs and source pages, not only final record text.

Define “confirmed leakage” as benchmark-derived or answer-bearing leakage. Literal overlap with an independently sourced fact should not automatically void a store merely because the benchmark asks about that fact.

The sealed-evaluation design is directionally strong, but 250 items/domain is not automatically powered for a 0.01 scalar margin. Determine size from the covariance, comparator count, rare dangerous-wrong targets, and intended CI width. The `.03` frozen-to-sealed gap should be tested as non-inferiority of a difference-in-differences, not as a point-estimate rule.

### Calibration

Soundness: good gate concept, insufficient coverage.

P3-E-CAL being conjunctive and blocking freeze is correct. However:

- It calibrates `INDEX_COMMON` selected from the R1 floor split, not every rung-specific manifest. Each W1 rung/version needs its own floor census, membership, ordering and variance calibration.
- Pure-neural SmolLM anchors do not exercise CPU-heavy, I/O-heavy, retry-heavy, or mixed CPU/GPU measurement boundaries. Add synthetic rig probes for those resource shapes without treating them as architecture evidence.
- One model family can validate harness continuity but not broad construct validity. Add at least one out-of-family neural model as a non-gating robustness subject.
- Mock-seal absolute-shift ≤.03 is arbitrary and risks tuning the seal producer toward the public suite. It needs a specified difficulty-matching method and empirical justification.
- Calibration success licenses repeatable separation of the chosen anchors, exactly as the draft says; it cannot validate fairness to hybrid systems.

### Statistics

The high-level §2.5 rules are correct:

- `LCB95(Δ)>δ` is the correct margin-superiority rule.
- FWER/max-t simultaneous bounds are safe and satisfy the parent. For the bare conjunction “beats every comparator,” an intersection-union test already controls the global claim, but simultaneous bounds remain appropriate because individual comparator and domain conclusions are reported.
- Retention is one-sided non-inferiority; TOST is only for equivalence.

The concrete implementation still needs correction:

- Fix the backward floor-UCB rule.
- Resampling “benchmark families within domain” can change the estimand and is unreliable when a domain has only one or two families. For an index defined on a fixed suite, keep benchmark/domain weights fixed and resample the appropriate item clusters within each benchmark—paradigm, rule template, story, source document, paraphrase family—while preserving paired system outputs.
- If the claim concerns a training procedure rather than one pinned artifact, training seed must be a top-level random effect; the current item-only bootstrap does not capture training variance.
- Resource UCBs need day/session/run hierarchy and simultaneous coverage across binding resource cells.
- Once per-domain non-inferiority is binding, those domain×comparator gates belong in the predeclared multiplicity family or a frozen gatekeeping procedure.
- The sealed `.03` consistency condition needs a CI on `Δsealed−Δpublic`.
- Twenty thousand replicates are adequate as a starting computational choice, but diagnostics, studentization, degenerate-cell handling, and Monte Carlo error—not the number alone—make max-t valid.

## Part B — ordered reconciliation edits

1. Amend W1 to require scalar superiority and per-domain non-inferiority against the preregistered domain frontier. Cite the construct-validity objection and make the vector the primary descriptive object ([EVAL §§2,7](/home/ec2-user/css/kernel/kernel-of-truth/reports/lit-p3-eval.md:104); current scalar-only rule: [draft §0](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kot-fair-2-spec-p3mf0.md:24)).

2. Cite HELM Capabilities 2025 and explicitly prohibit mean-win-rate aggregation. Keep mean-of-normalised-scores ([EVAL §1](/home/ec2-user/css/kernel/kernel-of-truth/reports/lit-p3-eval.md:46); [draft §1.3](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kot-fair-2-spec-p3mf0.md:117)).

3. Correct rung membership and floor logic. Use BLiMP, appropriate EWoK, low-hop CLUTRR, and depth-stratified ProofWriter/RuleTaker at R0/R1 when they pass a proper LCB floor gate; move FOLIO and GSM8K to R2+ unless calibration proves otherwise; retain MMLU-Pro/BBH at R3+ ([EVAL §6](/home/ec2-user/css/kernel/kernel-of-truth/reports/lit-p3-eval.md:270); [draft manifest/floor rules](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kot-fair-2-spec-p3mf0.md:77)).

4. Add the proxy-rung asymmetry verbatim: R0/R1 directional kills may terminate a family; positive margins are hypotheses requiring higher-rung confirmation; overlapping benchmark prompts/scorers/formats remain byte-identical across rungs ([EVAL §5](/home/ec2-user/css/kernel/kernel-of-truth/reports/lit-p3-eval.md:216), [TINY §6](/home/ec2-user/css/kernel/kernel-of-truth/reports/lit-p3-tiny.md:372); absent from [draft §1](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kot-fair-2-spec-p3mf0.md:62)).

5. Replace implicit whole-system energy with explicit boundary records and `UNMEASURED/UNPROVEN` states; either obtain wall/system measurement or amend the binding budget to named component-energy coordinates ([SYS §§Q7,R7](/home/ec2-user/css/kernel/kernel-of-truth/reports/lit-p3-sys.md:362); [draft §§3.1–3.2](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kot-fair-2-spec-p3mf0.md:248)).

6. Retain the existing true Poisson design, but add a frozen goodput SLO, timeout/drop accounting, intended-send drift, rank-based CIs, adaptive repetition count, and a repeatability gate on every campaign arm ([SYS §§Q2,Q4](/home/ec2-user/css/kernel/kernel-of-truth/reports/lit-p3-sys.md:120); [draft §§3.3–3.5](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kot-fair-2-spec-p3mf0.md:288)).

7. Split KOT-LIFE store accounting into build/mint, human-review/provenance, and staleness-refresh subledgers; add attrition, redundancy/quality, fan-out and uncertainty; measure refresh TCO against matched external-context baselines ([STORE §§4–6](/home/ec2-user/css/kernel/kernel-of-truth/reports/lit-p3-store.md:196); [draft §4](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kot-fair-2-spec-p3mf0.md:324)).

8. Replace the single “training-compute-matched twin” bullet with a FLOP-ledger specification: parameters, interface tokens, sequence length, objectives, last-layer FLOPs and auxiliary execution; same data/order; IsoFLOP placement with Porian corrections; paired seeds; µP width sweep with fixed depth; explicit Muon/interface audit and equal-tuning-budget fallback. Released SmolLM anchors must be labelled pinned comparators, never compute-matched twins ([TINY §§4,7](/home/ec2-user/css/kernel/kernel-of-truth/reports/lit-p3-tiny.md:205); [draft §5.3 item 7](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kot-fair-2-spec-p3mf0.md:442)).

9. Complete the matched-RAG control: information-parity rules across passages/triples/typed records, both BM25 and dense retrieval, retrieval recall/provenance, position shuffle, random-document control, popularity stratification, frozen context order, standard harness, and identical bytes/build/query ledgers ([RAG §§Q5 and implications](/home/ec2-user/css/kernel/kernel-of-truth/reports/lit-p3-rag.md:261); current partial control: [draft §5.3](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kot-fair-2-spec-p3mf0.md:422)).

10. Restore the complete factorial control and six-way attribution section required by the parent. This is also the direct answer to the FUSE/RULE finding that component ablations do not establish structure causality ([FUSE crux](/home/ec2-user/css/kernel/kernel-of-truth/reports/lit-p3-fuse.md:244), [RULE crux](/home/ec2-user/css/kernel/kernel-of-truth/reports/lit-p3-rule.md:345); omitted from [draft §5](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kot-fair-2-spec-p3mf0.md:388)).

11. Layer and validate decontamination, power the sealed suite rather than fixing 250/domain, and convert its gap rule to an inferential non-inferiority condition ([EVAL §4](/home/ec2-user/css/kernel/kernel-of-truth/reports/lit-p3-eval.md:168); [draft §§5.1–5.2](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kot-fair-2-spec-p3mf0.md:390)).

12. Keep Sardana only as qualitative context until the direct PDF reconciles the conflicting dollar examples. Do not copy any specific saving or model/token figure into KOT-LIFE before that read ([SYS §Q6](/home/ec2-user/css/kernel/kernel-of-truth/reports/lit-p3-sys.md:263); current qualitative parent citation: [parent §1.3a](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/programme-3-neurosymbolic-architecture.md:351)).

## Part C — correctness-instrument gap

The architecture reviews support “no matched-resource win shown,” not a universal impossibility result. FUSE, RULE, NTP and PARSE independently find that the clean positive results are predominantly add-capability wins in which an engine supplies exactness, sound deduction, validity, or OOD guarantees ([FUSE](/home/ec2-user/css/kernel/kernel-of-truth/reports/lit-p3-fuse.md:292), [RULE](/home/ec2-user/css/kernel/kernel-of-truth/reports/lit-p3-rule.md:365), [NTP](/home/ec2-user/css/kernel/kernel-of-truth/reports/lit-p3-ntp.md:417), [PARSE](/home/ec2-user/css/kernel/kernel-of-truth/reports/lit-p3-parse.md:231)). SURG likewise finds fact relocation demonstrated but computation relocation unproven ([SURG §4](/home/ec2-user/css/kernel/kernel-of-truth/reports/lit-p3-surg.md:119)). The memory-layer factual-recall result is a narrow matched-resource exception, but not evidence for the targeted rule-injection or checker pathway.

KOT-FAIR/2 is not completely blind to correctness: it already demands refusal, unconditional dangerous-wrong, selective-risk and covered/uncovered columns ([draft §1.2](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kot-fair-2-spec-p3mf0.md:104)). But those columns have no frozen definitions, challenge-set construction, statistical gates, or claim status. W1 treats abstention as incorrect and harmless wrong and dangerous wrong alike. Consequently the framework can report a correctness signal, but it cannot adjudicate a correctness-value win.

The minimal addition is a separate, non-composite correctness endpoint family:

- coverage/answer rate;
- unconditional `P(answer ∧ dangerous-wrong)`;
- selective risk `P(wrong | answered)`;
- the complete risk–coverage curve and AUACC;
- coverage at a frozen dangerous-wrong upper-confidence bound, or dangerous-wrong at frozen coverage;
- accepted/provenance-backed soundness-violation rate;
- end-to-end semantic correctness separately from parse validity or successful execution.

The scorer taxonomy and challenge suite must be frozen before outputs: include ambiguity/unanswerability, both orientations of directional relations, valid-but-wrong programs, paraphrase/source shifts, and held-out rule compositions. Rare dangerous-wrong rates need one-sided binomial bounds and adequate sample size; the operating threshold must be selected on disjoint development data. The strongest neural/RAG selective-prediction baseline must receive the same evidence, abstention opportunity, tuning budget and resource ledger.

Whether this correctness family becomes:

1. a second success claim alongside W1,
2. a conjunctive W1 gate,
3. or a separate Pareto axis over correctness–coverage–cost

is a strategic design question for the maintainer/Fable. This review should not choose that re-weighting. It must, however, be resolved before freeze; otherwise KOT-FAIR/2 is explicitly an efficiency framework that only records the programme’s increasingly central correctness thesis as a diagnostic footnote.

## Overall freeze decision

Do not freeze KOT-FAIR/2 yet. Freeze-readiness requires, at minimum:

1. resolve scalar W1 versus scalar-plus-domain non-inferiority;
2. fix the floor rule, rung manifest and cross-rung proxy language;
3. resolve the energy boundary and replace the 3× ceilings;
4. make repeatability an every-arm gate with valid CIs;
5. split and measure store refresh TCO;
6. fully specify compute-matched twins and matched RAG;
7. restore the mandatory factorial controls and attribution;
8. add a claim-capable correctness instrument or explicitly scope it out;
9. repair the hierarchical analysis plan and rung-specific calibration;
10. empirically ratify—not merely list—the hardware, decontamination, margin and sealed-suite constants.

No reviewed files were changed.