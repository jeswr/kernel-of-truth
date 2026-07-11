# P3-MF-0 — KOT-FAIR/2: the measurement + fair-comparison framework (DRAFT 2)

> **Status: DRAFT 2 — the review-blocked draft 1 REVISED per the independent
> GPT-5.6 review (`poc/gpt56-review/rev-dMF0-20260711/last-message.json`, read
> in full; every named correction applied at the section the review cites —
> §13 is the change record). NOTHING here is frozen, pre-registered,
> scheduled, or run; no frozen object, verdict, audit, results-log, or KB
> shard is touched. This revision DOES append its load-bearing design
> stipulations to `registry/assumptions.jsonl` (ASM-0880…ASM-0891,
> append-only fresh block) so every [STIPULATED] premise introduced here
> cites a registered id. This document does NOT propose freezing KOT-FAIR/2
> — the freeze belongs to the dedicated integration step P3-D-FAIR (§11;
> draft 1 wrongly routed the whole freeze through P3-D-INDEX, review ranked
> concern 1). Per the review's recommendation: NO G4/W1 experiment and NO
> P3-E-CAL execution launches from this document.**
> Author: Fable, chief-architect role (`kern/fable-designer`), 2026-07-11
> (draft 1 and this revision the same day; the review is the revision driver).
> Parent: `docs/next/programme-3-neurosymbolic-architecture.md` (revision 2)
> §2/§2.4/§5 P3-MF-0 row. Inputs read at source:
> `docs/next/feasibility-synthesis.md` (capstone verdict, 2026-07-11);
> `docs/next/lit/EVAL.md` + `docs/next/lit/SYS.md` (consumed in draft 1);
> `docs/next/lit/RAG.md` + `docs/next/lit/STORE.md` + `docs/next/lit/PARSE.md`
> (landed 2026-07-11 after draft 1; consumed in THIS revision at
> §8.2(iii)/§8.5, §5/§7.3(f), and §2.6 respectively, per the review's
> instruction); `docs/next/benchmark-evaluation-strategy.md` (the SmolLM2
> nine + anchoring protocol); `docs/next/assumption-register.md` (tag
> discipline).
>
> **Tag convention** (house discipline, `docs/next/assumption-register.md` §1):
> `[MEASURED: ref]` = a programme verdict/observation restated strictly inside
> its own envelope; `[LIT-BACKED: ref]` = external result verified at source by
> a named lit-review (this draft cites only through EVAL.md/SYS.md, never on
> memory); `[STIPULATED]` = a design CHOICE made here, owned and revisitable —
> every design decision below is STIPULATED, never smuggled as evidence;
> `[EXTRAPOLATION]` = forward projection, never a premise. Draft-2 change:
> the stipulations this revision INTRODUCES are registered (ASM-0880…ASM-0891
> appended to `registry/assumptions.jsonl`) and cited inline; inherited
> stipulations keep their original ids (§12.2).

---

## 0. What this framework is, and the walls it must respect

KOT-FAIR/2 is the instrument Programme-3 lives or dies by: the apparatus that
makes "a neurosymbolic system S beats the resource-constrained baseline
frontier F(B_k) on a pinned index" a measurable, auditable, gameable-by-neither-side
claim (programme doc §1.4 W1). It must exist, be calibrated on cases with known
answers, and be frozen — by P3-D-FAIR, the dedicated integration/freeze step
(§11) — before ANY Phase-2 G4/W1-relevant experiment freezes
[STIPULATED: ASM-0812, inherited; freeze ownership corrected per ASM-0880].

Three walls shape every choice below:

- The NL-boundary wall: both measured NL crossings FAILED (l3a-parse 47.6%
  retention; a5-nl 41.6% + the S2 dangerous-wrong kill fired at 5.0%)
  [MEASURED: registry/verdicts/l3a-parse.json + registry/verdicts/a5-nl.json,
  both FAIL at scope]. Consequence for the FRAMEWORK: index items are consumed
  as their natural benchmark text; no arm receives hand-formalised inputs; a
  store-touching arm includes its NL front-end inside the measured system or
  abstains — and abstention is scored (§2.6). The framework itself contains
  NO oracle channel: the only oracle-labelled machinery in this document is
  the G1 Δ_max coverage bound (§9.4), which is explicitly a paper KILL bound
  (an upper bound on what perfect oracle use could gain), never a capability
  claim, and it licenses nothing [STIPULATED, continuing ASM-0808/ASM-0814].
- The coverage wall: measured external coverage is ~zero (0/1,550 define-lane;
  g8 0/1,000; m0b 0.3542 on the friendliest corpus, corpus/rung/kernel-state
  indexed) [MEASURED: registry/assessments/b-cov-define-lane.json;
  registry/verdicts/g8.json; ASM-0001 (m0b)]. Consequence: the analysis plan
  makes the G1 bound a first-class, normalized-scale computation (§9.4) so the
  coverage kill fires on paper before GPU spend.
- The answer-key wall: the one end-task positive is provably consistent with
  "aligned answer key + retry" and its shuffled control cannot discriminate
  content from alignment [MEASURED: registry/assessments/f2b-replicate.json
  does_not_license]. Consequence: decontamination (§6) is a win-VOIDING gate,
  the sealed eval (§7) is mandatory, and the factorial controls + generic-RAG
  comparator are part of the framework, not of individual experiments — now
  SPECIFIED in §8.5 and §8.2(iii) (draft 1 named them without specifying
  them; review-flagged, ranked concern 1).

Fit to the gate ladder: G1 consumes §9.4; G2/G3 consume the oracle-diagnostic
labelling rules (§1, T-S5) and the §9 stage-attribution hooks; G4 consumes the
whole framework (index + size + cost + ledger + decon + sealed + frontier +
stats); G5 consumes the cross-rung comparability rules (§2.7)
[STIPULATED: framework-to-ladder mapping].

Executability constraint: everything in this draft runs at 100M–2B scale on the
programme's pool — the local 2-vCPU box (no GPU, no RAPL [MEASURED: SYS.md §0,
direct inspection 2026-07-11]), Modal GPU credits, ARC pending survey — and the
Phase-0/1 pieces (packing script, screener, G1 tables, calibration prereg
authoring) are CPU-only, ~$0 of COMPUTE — the human costs they carry
(coverage adjudication, decon flag adjudication, sealed authoring,
calibration oversight) are REAL, logged in hours into KOT-LIFE/1 lines, and
never rounded to zero; draft 1's bare "~$0" overclaimed (review-flagged)
[STIPULATED: ASM-0886].

---

## 1. The resource/baseline threat model — KOT-THREAT/1 (draft input to P3-D-THREAT)

An enumerated adversary analysis: how each metric can be gamed BY EITHER SIDE
(us or a baseline author), each channel with its mechanised counter in this
document, or an honest standing limitation where no counter exists at freeze
time [STIPULATED: ASM-0812 executed; the table below is the draft P3-D-THREAT
freezes, extends, and adversarially red-teams].

Threat classes and channels (counter → section):

**T-P — packaging/size games (target: KOT-SIZE/2)**
- T-P1 base-image migration: move arm-specific functionality into the "free"
  base image. Counter: frozen content-hashed base image, artifact-neutrality
  rule, anything beyond it counts as arm bytes (§3.3); the kernel ENGINE
  itself counts as arm bytes — no "the kernel is free" accounting (§3.3).
- T-P2 remote dependencies: serve from a remote store/cache/API and claim tiny
  deployment. Counter: KOT-SIZE/2 figure (6) — remote bytes count or the size
  claim is void (§3.1).
- T-P3 lazy paging / mmap games: keep bytes on disk, page them in, claim a
  small warm footprint. Counter: cold-start working set + bytes-to-first-answer
  (figure 4) and peak RSS (KOT-COST/2(e)) both measured (§3.1, §4).
- T-P4 serialization shopping: favourable formats, padding removal only on our
  side, duplicated-metadata asymmetry. Counter: ONE canonical packing script
  applied identically to every arm (§3.2).
- T-P5 minimal-sufficiency cheating: strip bytes the system actually needs and
  hope the measurement doesn't notice. Counter: the packed artifact must pass a
  boot-and-answer smoke test from packed bytes alone on the frozen base image
  (§3.2 step 5).

**T-F — frontier/budget games (target: W1 admissibility + F(B_k))**
- T-F1 budget shopping: pick B_k where the frontier is weak. Counter: budgets
  pre-registered before comparator search; full staircase/Pareto envelope
  published, W1 = above the envelope, not "won the neighbourhood" (§8.4).
- T-F2 comparator dodging: omit the strongest fitting baseline. Counter: the
  frontier-builder's source-family checklist is mandatory and its search log is
  published (§8.2); STANDING LIMITATION — baseline-search completeness is not
  provable; carried verbatim on every W1 claim (§1.9).
- T-F3 smaller-dominator blindness: beat same-size systems while a smaller,
  cheaper one dominates. Counter: F(B_k) explicitly includes systems smaller/
  cheaper than S (§8.1).
- T-F4 compute-optimal strawmen: compare against Chinchilla-optimal artifacts
  when deployed practice is overtrained/inference-optimal. Counter: anchor
  comparators are inference-optimal artifacts (SmolLM2-class, ~6,500–14,800
  tokens/param) [LIT-BACKED: SYS.md §9 (Sardana arXiv:2401.00448 verified at
  source; SmolLM2 cards)] (§8.1).

**T-C — cost games (target: KOT-COST/2)**
- T-C1 warm-cache-only reporting. Counter: COLD and WARM states both measured
  and both reported, never blended (§4.4).
- T-C2 output-length inflation/deflation. Counter: pinned max-token + stop
  discipline, or per-emitted-token normalisation, pinned per benchmark
  (KOT-COST/2(j)) (§4.1).
- T-C3 batch-size / concurrency shopping. Counter: pinned scenarios
  (SingleStream + Offline mandatory; Server optional under a pinned
  concurrency distribution) (§4.2).
- T-C4 symbolic-work hiding: CPU search/retrieval/decompression entering at
  zero under a neural-FLOP ledger. Counter: every measured KOT-COST/2
  component is either a PRIMARY budget component or a HARD SECONDARY CEILING
  of B_k (§8.1) — CPU, I/O, network and accelerator work cannot enter at
  zero; the neural-FLOP ledger is a demoted, non-binding diagnostic (§4.1)
  [LIT-BACKED: SYS.md §9 — FLOPs-vs-cost gap 1.3% vs 36% at 50× utilization
  difference, the literature warrant for the demotion].
- T-C5 closed-loop driver tails (coordinated omission): a closed-loop client
  silently deletes tail samples (documented ~200× p99 understatement)
  [LIT-BACKED: SYS.md §5 (wrk2)]. Counter: open-loop pinned seeded schedule,
  latency from intended issue time, closed-loop drivers PROHIBITED for
  latency-under-offered-load percentile claims; closed-loop SingleStream
  service-time percentiles stay legal and carry the "service-time
  (closed-loop, unloaded)" label — symmetric across arms (§4.3)
  [STIPULATED: ASM-0882].
- T-C6 test-trace memoisation: a comparator caches responses to the pinned
  trace. Counter: MLPerf caching prohibitions adopted as the legality rule for
  all arms [LIT-BACKED: SYS.md §1 (inference_rules.adoc)] (§4.3).
- T-C7 host/day shopping: measure S on a good host/day, B on a bad one.
  Counter: same-host same-session A/B/A/B interleave + host fingerprint +
  calibration-probe CoV gate, sessions discarded fail-closed (§4.5).
- T-C8 energy laundering: TDP/utilisation-modelled energy where no counter
  exists. Counter: counter-based estimates with declared boundary or the cell
  is reported MISSING, fail-closed — never modelled [LIT-BACKED: SYS.md §2
  (MLPerf Power kills TDP proxies)] (§4.6).

**T-I — index games (target: KOT-AI-INDEX/2)**
- T-I1 suite shopping / post-hoc component drops. Counter: suite membership,
  domains, constants, harness, prompts pinned at P3-D-INDEX freeze; below-floor
  EXCLUSION criteria registered from calibration data BEFORE campaign results
  (§2.5, §10) [STIPULATED per EVAL.md §5.3].
- T-I2 domain reweighting after results. Counter: fixed registered weights;
  any change is an index version bump that re-baselines everything (§2.7).
- T-I3 abstention gaming: refuse everything hard, harvest easy accuracy.
  Counter: abstention scored as incorrect in every accuracy component;
  abstention/refusal rates co-reported in the vector; risk–coverage curves are
  diagnostics, never index credit (§2.6).
- T-I4 strategy shopping: CoT vs direct prompting moves BBH-class scores
  enormously [LIT-BACKED: EVAL.md §6 (BBH row)]. Counter: prompting strategy
  pinned per rung per benchmark inside the index version (§2.4).
- T-I5 harness shopping. Counter: ONE pinned harness commit per index version;
  KOT-SMOL-CONT/1 anchoring within ±2.0 pp validates harness fidelity (§2.8).
- T-I6 reference/ceiling shopping and clamping games: pick a flattering
  ceiling; exploit clamped-vs-unclamped asymmetry. Counter: per-component
  registered reference estimand + uncertainty + ONE clamping rule + version
  bump on reference update (§2.3) [STIPULATED per EVAL.md §2/§8.1].
- T-I7 scalar hiding a profile: quote the scalar where the vector disagrees.
  Counter: no claim quotes the scalar without the domain vector one link away
  (ASM-0811(3)); metabench's one-factor result is the quantitative reason
  [LIT-BACKED: EVAL.md §2 (arXiv:2407.12844)].

**T-S — store games (target: the answer-key confound)**
- T-S1 answer-key encoding: benchmark answers written into the store. Counter:
  the decontamination screener as a win-VOIDING hard gate (§6).
- T-S2 error-analysis-driven authoring: grow the store where the frozen suite
  fails. Counter: authoring-provenance rule + per-record provenance log (§6.3);
  artifact freeze (store hash pinned at eval time).
- T-S3 paraphrase-level leakage below screener threshold: a 13B trained on
  rephrased test sets reached GPT-4-level scores while PASSING standard
  decontamination [LIT-BACKED: EVAL.md §4 (arXiv:2311.04850)]. Counter: the
  screener is a gross-leakage gate ONLY; the SEALED evaluation is the actual
  defence (§7); STANDING LIMITATION otherwise.
- T-S4 researcher adaptation to the frozen suite across iterations. Counter:
  sealed releases are one-shot, burned after use, no-feedback across releases
  (§7.3).
- T-S5 oracle smuggling: hand-formalised inputs, gold parses, or gold record
  addresses inside a claimed real-input result. Counter: NL-input integrity
  rule (§0); any oracle-input stage is labelled `oracle-diagnostic` in its
  prereg and licenses NO W1 claim and no real-input claim of any kind
  [STIPULATED: ASM-0814, restated as a threat-model row].

**T-T — tuning games (target: symmetry)**
- T-T1 unequal search compute behind equal config counts. Counter: symmetry
  binds on TOTAL tuning compute (accelerator-h + CPU-h actually spent), logged
  per arm into KOT-LIFE/1, with a FIXED pre-registered selection rule on a dev
  split disjoint from the index suite (§5.2, §8.3).
- T-T2 dev-split contamination of the index suite. Counter: dev-split hash
  pinned; disjointness checked mechanically by the screener run suite-vs-dev
  (§6.4).

**T-A — analysis games**
- T-A1 multiplicity shopping (test many comparators/domains, quote the
  survivor). Counter: simultaneous/family-wise error control across the
  pre-registered comparator set (§9.2).
- T-A2 margin laundering (point estimate above δ, LCB merely >0, reported as a
  margin win). Counter: LCB95 itself must clear δ (§9.1).
- T-A3 estimand swapping (TOST-vs-non-inferiority mislabels). Counter: §9.3.

**§1.9 Standing limitations (games with NO mechanised counter at draft time —
carried verbatim on every W1 claim they touch)** [STIPULATED, continuing the
programme doc §7.3 correction]:
1. Training-data contamination of CLOSED baseline corpora cannot be audited;
   we report known contamination status symmetrically and run the Oren logprob
   diagnostic on open donor weights where logprob access exists [LIT-BACKED:
   EVAL.md §4 (arXiv:2310.17623) — a negative result proves nothing]. The
   asymmetry favours baseline scores, i.e. is conservative for us.
2. Baseline-search completeness is unprovable (T-F2); the search log +
   published envelope is disclosure, not proof.
3. Lifecycle costs are incommensurable across store-authoring hours and
   GPU-hours; KOT-LIFE/1 publishes per-unit lines and K-P3v2(6) gates by
   per-line Pareto domination without ever combining units (§5.1); no scalar
   TCO number is quoted anywhere.
4. Generator-based sealing is only as independent as its producer; fresh seeds
   from a known generator are NOT sealing [STIPULATED per EVAL.md §4]; the
   producer-independence decision is P3-D-SEAL's one governance question.
5. Residual packaging/frontier gaming beyond the enumerated channels: the
   threat model is enumerable-adversary, not complete-adversary.

---

## 2. KOT-AI-INDEX/2 — the AI-index pins (DRAFT pins; frozen by P3-D-INDEX)

### 2.1 Construction (inherited, made concrete)

Per-benchmark normalisation s̃ = (s − chance)/(ceiling − chance); per-SUBTASK
chance floors where cardinality is heterogeneous (the OLLv2 precedent: BBH's
24 subtasks 2–19 choices normalised each against its own floor, then averaged)
[LIT-BACKED: EVAL.md §2 (OLLv2 normalization docs)]. Normalised scores are
macro-averaged first WITHIN capability domains, then across domains; every
publication reports the DOMAIN VECTOR and the scalar; no claim quotes the
scalar without the vector one link away [STIPULATED: ASM-0811 restated].

Scope limits, adopted from the lit-review verbatim [STIPULATED per EVAL.md §2]:
the chance-to-ceiling transform is defined for ACCURACY-type metrics only.
Draft rules for everything else:
- Held-out LM loss (D1, R-0/R-1): VECTOR-ONLY — reported, excluded from the
  scalar, because no verified normalising transform exists. P3-D-INDEX may
  register a reference-model-anchored transform; until then vector-only
  [STIPULATED].
- Calibration/robustness metrics: not in the v2 index at all; candidate v3
  material [STIPULATED].
- Generative components (IFEval, GSM8K): lower_bound = 0, labelled a
  CONVENTION, not a measured floor [STIPULATED per EVAL.md §2].
- Mean-win-rate aggregation is RULED OUT with cause: it is ordinal and
  comparator-set-dependent, which conflicts with a pre-registered frontier —
  adding a comparator must not move S's own index [STIPULATED per EVAL.md §1].

### 2.2 The concrete benchmark set (draft membership, per rung)

Membership below is the DRAFT pin; dataset revisions (HF dataset ids +
revision hashes) and the harness commit are pinned at P3-D-INDEX freeze, not
here. Floors marked "CAL" are unmeasured in the literature at tiny scale and
MUST be measured by P3-E-CAL before margins are set [STIPULATED per EVAL.md
§6/§8.4].

| Domain | R-0 (1–30M) | R-1 (100–200M) | R-2 (300–500M) | R-3+ (1–2B+) | chance floor |
|---|---|---|---|---|---|
| D1 linguistic | held-out LM loss (pinned hashed corpus; vector-only) + BLiMP + EWoK | same | same | same | BLiMP 0.50; EWoK 0.50 [LIT-BACKED: EVAL.md §6] |
| D2 commonsense/world | — | HellaSwag, PIQA, WinoGrande | same | same | 0.25 / 0.50 / 0.50 |
| D3 knowledge/factual | — | ARC-Easy, ARC-Challenge, OpenBookQA | same | + MMLU-Pro | 0.25 / 0.25 / 0.25; MMLU-Pro 0.10 |
| D4 relational/rule (the neurosymbolic diagnostics) | procedural relational suite PR-KOT/1 (generator-pinned synthetic; held-out rules, compositions, depths, paraphrase splits) | + CLUTRR (generator-pinned) + ProofWriter/RuleTaker (PROMPTED protocol, §2.4) | same, deeper splits | same, deeper splits; FOLIO R-3+ only | PR-KOT/1 by construction; CLUTRR CAL; ProofWriter CAL; FOLIO ≈0.33 |
| D5 math/procedural | — | — (GSM8K floored ≤360M [LIT-BACKED: EVAL.md §3]) | GSM8K iff rung ≥1B, else — | GSM8K + BBH (strategy-pinned) | 0 (convention); BBH per-subtask |
| D6 instruction following | — | IFEval (instruct hosts; PROMPT-LEVEL STRICT accuracy, one variant pinned) | same | same | 0 (convention) |
| D7 code | — | — | — | one pinned code benchmark + a frozen LiveBench release (versioned) | per benchmark |
| S sealed secondary | §7, per release | §7 | §7 | §7 | per release |

Membership rationale, each a draft judgement resting on the lit-review's floor
evidence: IFEval is PROMOTED to R-1 (135M-Instruct 29.9 vs floor ≈0,
discriminative across the whole range) [LIT-BACKED: EVAL.md §6]; MMLU-cloze is
dropped as a cross-rung component (ASM-0811); MMLU-Pro/BBH/BBEH/MATH/GPQA/MuSR
stay out below R-3 (floor/weak-discrimination evidence and unverified
tiny-scale numbers) [LIT-BACKED: EVAL.md §3/§6]; EWoK carries an explicit
floor warning (near-chance in the BabyLM regime) and earns its seat via the
domain vector, not the scalar [LIT-BACKED: EVAL.md §6]; FOLIO is R-3+ or
oracle-diagnostic material only [STIPULATED per EVAL.md §6].

PR-KOT/1 (new, named here): a small procedural relational + rule-reasoning
generator suite, OURS, seed-pinned, with by-construction chance floors and
held-out rule/composition/depth/paraphrase splits — the R-0-usable D4 cell and
the cheap sealed-refresh substrate (§7.2). Its generator spec is a P3-D-INDEX
deliverable; the CLUTRR generator design is prior art, and CLUTRR's
CC-BY-NC-4.0 licence means OUR generator is a re-implementation, not a
derivative artifact redistribution — licence check at freeze [STIPULATED per
EVAL.md §8.8].

### 2.3 Ceiling pins (the piece with no published precedent)

No published leaderboard does ceiling-pinning; this piece is ours to freeze
and defend [STIPULATED per EVAL.md §2]. Draft rules:
- Per component, register: the reference ESTIMAND (e.g. BLiMP human-aggregate
  96.4 vs human-individual 88.6 are DIFFERENT estimands [LIT-BACKED: EVAL.md
  §2/§6]), its score + uncertainty, and the update policy (a reference change
  is an index VERSION change).
- Draft choice: where a human-aggregate estimate exists, pin
  ceiling = human-aggregate (BLiMP: 96.4); where only model references exist,
  ceiling = the named pinned reference model's own-harness score; where
  neither, ceiling = 1.0 (degenerating to the OLLv2 formula) [STIPULATED].
- Clamping rule (one rule, symmetric): the VECTOR reports unclamped s̃ (values
  >1 possible and visible); the SCALAR uses min(s̃, 1). An above-ceiling score
  triggers a reference review at the next index version, never a mid-version
  change [STIPULATED; answers the T-I6 channel].
- Saturation guard (NEW in draft 2 — the review showed a low reference plus
  clamping can destroy W1 discrimination: two systems above the ceiling both
  contribute 1.0 and become indistinguishable): P3-E-CAL carries a SATURATION
  GATE (§10 gate 7) — if any calibration anchor at the rung clamps to 1.0 on
  any in-scalar component, that component's ceiling is re-estimated
  headroom-preserving (or the component enters the scalar unclamped for that
  index version) BEFORE freeze; and any W1 component cell where S and a
  comparator BOTH clamp is reported "saturated — non-discriminative on this
  component" rather than counted as a silent tie [STIPULATED: ASM-0889].

### 2.4 Prompting-strategy and protocol pins

- Per rung, per benchmark, ONE prompting strategy is part of the index version.
  Draft: R-0/R-1 = zero-shot for MC-logprob components, harness-default
  few-shot counts for ARC/OBQA-class (pinned exactly at freeze), NO CoT
  anywhere below R-3; R-3+ BBH strategy pinned explicitly (CoT vs direct is a
  version-level choice) [STIPULATED; closes T-I4].
- D4 fine-tune-vs-prompt protocol (the EVAL.md §6 open question), draft ruling:
  the INDEX component is PROMPTED (zero/few-shot, pinned); a light-adaptation
  variant (pinned small fine-tune budget, identical for every arm) is reported
  as a separate DIAGNOSTIC column, never in the scalar — the prompted-vs-
  adapted gap is itself informative [STIPULATED].
- NL-input integrity (anti-l3a/a5, restated as an index rule): items are
  consumed as natural benchmark text; the parser is part of the product; its
  failures are the system's failures [STIPULATED: ASM-0808].

### 2.5 Floor handling

Below-floor exclusion criteria are REGISTERED FROM P3-E-CAL CALIBRATION DATA
BEFORE any campaign result is seen; components may not be dropped post hoc
[STIPULATED per EVAL.md §5.3]. Draft criterion (to be validated in P3-E-CAL),
CORRECTED in draft 2 — the draft-1 rule "LCB95(s − chance) ≤ 0" tested the
wrong inferential direction: it means "not proven above chance", which
excludes underpowered components and retains statistically-significant-but-
practically-useless ones (review-flagged). Corrected rule: a component is
below-floor at a rung iff UCB95(s − chance) < Δ_disc for the LARGEST anchor
model at that rung, where Δ_disc is a registered MINIMUM DISCRIMINATIVE SPAN
set from P3-E-CAL calibration data before any campaign result (draft: the
span required to move the component's domain score by one registered
δ-quantum; pinned at P3-D-INDEX freeze) — i.e. exclusion requires the data to
DEMONSTRATE, at controlled confidence, that the component cannot
discriminate. Below-floor components report in the vector, are excluded from
the scalar at that rung, and their exclusion list is part of the index
version [STIPULATED: ASM-0883].

### 2.6 Abstention scoring

Abstention/refusal is scored INCORRECT in every accuracy component; abstention
rate is a mandatory vector column; risk–coverage curves (selective-prediction
diagnostics for H-PS-class systems) are reported as diagnostics with no index
credit [STIPULATED; closes T-I3 while keeping the fail-closed design property
visible rather than rewarded — a5-nl's lesson is that wrong-with-provenance is
worse than refusal, so the vector separately reports the dangerous-wrong rate
where a store is in play (MEASURED precedent: a5-nl S2 kill)].

P3-LR-PARSE (landed 2026-07-11) is consumed here for the reporting
conventions the draft-1 §11 left open: any S2-class dangerous-wrong rate is
defined UNCONDITIONALLY — P(answered ∧ wrong) — with the selective risk
P(wrong | answered) co-reported, because the two diverge exactly when
coverage drops; risk–coverage reporting is whole-curve plus one frozen
operating threshold, never a bare point [LIT-BACKED: PARSE.md §4/§8]. The
NLB gate instrument itself — the joint 0.90-retention/S2 one-sided confidence
rule at pre-specified n, per-stratum minimum support over systematic-error
strata (relation/operator × direction × paraphrase family), four-way data
separation (model selection / calibration / threshold / final eval), and
shift stress of the guarantee under calibration-vs-deployment phrasing
sources — is P3-D-NLB's deliverable consumed by this framework as a gate;
the index makes no claim that the NLB gate is operational until P3-D-NLB
freezes those rules [STIPULATED per PARSE.md §8; this framework only pins
the reporting conventions above].

### 2.7 Weights, missing domains, versioning, cross-rung rules

- Draft weights (NORMATIVE, registered): equal weight across domains present
  at the rung; equal weight across benchmarks within a domain; per-subtask
  equal weight within a benchmark. No coverage-proportional weighting (it
  would let store coverage move the index definition — a T-I2 channel)
  [STIPULATED].
- Missing domains: the scalar at rung R is defined over the domains present at
  R and is tagged with the rung (INDEX_R1, INDEX_R2, ...); scalars are NEVER
  compared across rungs; cross-rung statements use the domain vector on shared
  components, and cross-rung extrapolation is licensed only for
  continuous/logprob metric families, never MC accuracy [STIPULATED per
  EVAL.md §5 — metric-dependent proxy validity, arXiv:2304.15004/2406.04391/
  2405.10938 as read there].
- Versioning: KOT-AI-INDEX/2.0-draft1 (this document). Any change to
  membership, domain assignment, normalisation constants, references, harness
  commit, prompt strategy, or exclusion lists bumps the version and
  re-baselines everything [STIPULATED: ASM-0811 restated].
- IRT-selected item compression (metabench-style subsetting) is flagged as a
  COST OPTION for R-1, default OFF; if ever adopted it enters as a version
  change with reconstruction error added to the variance budget
  [EXTRAPOLATION per EVAL.md §2 — an option, not a premise].

### 2.8 KOT-SMOL-CONT/1 — the continuity index (unchanged, demoted)

The revision-1 nine-task suite verbatim — HellaSwag, ARC (E/C avg), PIQA,
MMLU-cloze, CommonsenseQA, TriviaQA, WinoGrande, OpenBookQA, GSM8K-5shot
[MEASURED-in-repo: docs/next/benchmark-evaluation-strategy.md §1] — retained
ONLY for anchor continuity with the SmolLM2 cards and harness calibration:
own-harness model-alone scores must land within ±2.0 pp of the published card
number on variant-matched cells (the stipulated instrument constant), else the
harness is broken, not the model [STIPULATED: benchmark-evaluation-strategy §(c)
anchoring protocol, adopted]. Never the headline, never in W1, no
cross-benchmark aggregation over the nine [STIPULATED: ASM-0811].

---

## 3. KOT-SIZE/2 — canonical packing (kot-pack/1) + the base-image freeze rule

### 3.1 The six figures (inherited pins, restated as the rig's outputs)

(1) canonically-packed minimally-sufficient SERVING artifact bytes (PRIMARY —
the artifact that actually serves, per §3.2 step 2's draft-2 correction);
(2) compressed distribution bytes (zstd, pinned level 19); (3) warm resident
RAM/VRAM while serving; (4) cold-start working set + total bytes read to first
answer; (5) construction inputs, intermediate bytes, build scripts and build
cost (feeds KOT-LIFE/1; co-reported with every W1 claim);
(6) remote dependencies — remote bytes count or the size claim is void
[STIPULATED: ASM-0810 restated; figures (3)/(4) are measured by the KOT-COST/2
rig (§4) so size and cost share one measurement, closing T-P3].

### 3.2 kot-pack/1 — the canonical packing script (spec draft; implementation
is a P3-D-INDEX deliverable, CPU-only, runs on the local box)

Deterministic algorithm, applied IDENTICALLY to every arm [STIPULATED]:
1. **Manifest enumeration**: the arm declares its artifact file set; files are
   enumerated in bytewise-sorted path order; all timestamps/uids/permissions
   normalised to constants (byte-determinism discipline per the encoder
   programme's own X0 practice).
2. **Canonical per-type serialization** (pinned per type at freeze): neural
   weights → safetensors with sorted tensor keys, no padding, pinned dtype
   stated (quantisation allowed, symmetric per §8.2(ii)); store records →
   canonical KOTK/2 columnar form; retrieval indexes → the packed AS-BUILT
   serving bytes. CORRECTED in draft 2: figure (1) counts the actual
   minimally-sufficient serving artifact and nothing else — draft 1's
   "whichever is LARGER of (as-built) and (construction inputs + build
   script)" mixed deployment size with construction provenance, arbitrarily
   charging development material as deployed bytes (review-flagged).
   Construction inputs, intermediates, the build script, and build compute
   land in figure (5), which every W1 claim CO-REPORTS — so "rebuildable for
   free" still cannot hide a build, it just cannot inflate deployed bytes
   either [STIPULATED: ASM-0885].
3. **Deduplication**: content-addressed blocks; duplicated metadata stripped;
   dedup is WITHIN the arm's artifact only (no cross-arm sharing).
4. **Figure (1)** = total payload bytes of the canonical manifest.
   **Figure (2)** = zstd-19 over the single concatenated canonical stream.
5. **Minimal-sufficiency boot test** (closes T-P5): the packed artifact,
   unpacked onto the FROZEN base image and nothing else, must serve a pinned
   smoke query set (per vertical) correctly; failure voids the size figure.
   The smoke set is pinned at freeze and is disjoint from every index item
   (screener-checked, §6.4).
6. Output: a JSON size record {figures 1–6, artifact content hash, base-image
   hash, script version} — the artifact-freeze object W1 admissibility cites;
   "grow the store after measuring" is impossible by construction
   [STIPULATED: ASM-0810].

### 3.3 The base-image freeze rule

- ONE common base image, content-hashed (pinned Dockerfile: OS release +
  runtime interpreters + pinned generic libraries), frozen BEFORE any Phase-2
  architecture development begins — the first deliverable of P3-D-INDEX
  [STIPULATED: ASM-0810].
- **Artifact-neutrality rule** (closes T-P1): the base image may contain only
  components that (a) every measured arm uses or could use identically and
  (b) encode no arm-specific functionality or data. The kot-axiom ENGINE
  BINARY, the kernel, every store, every retrieval index, and every adapter
  are ARM BYTES, never base-image bytes — there is no "the kernel is free"
  accounting, ever [STIPULATED].
- Anything an arm needs beyond the frozen image counts as its figure-(1)
  bytes. A base-image change is a KOT-SIZE version change and re-baselines
  every size figure [STIPULATED].
- Disputed-inclusion protocol: any request to add a component to the base
  image is decided BEFORE the requesting experiment freezes, logged with
  rationale; default is DENY (the component counts as arm bytes)
  [STIPULATED].

---

## 4. KOT-COST/2 — the cost rig (draft; operating manual frozen by P3-D-HW)

### 4.1 The resource vector (binding) and the demoted diagnostic

Per query and per suite, on pinned hardware under the P3-D-HW protocol:
(a) accelerator time + estimated accelerator ops; (b) CPU-seconds; (c) bytes
read from storage and network; (d) energy (counter-based, §4.6); (e) peak
accelerator memory AND host RSS; (f) end-to-end latency p50 and p95;
(g) throughput under a pinned concurrency distribution; (h) warm AND cold
conditions, incl. startup/index-load; (i) TTFT + inter-token latency for
generative arms; (j) output length controlled (pinned max-token + stop
discipline) or cost normalised per emitted token, pinned per benchmark
[STIPULATED: ASM-0810 restated]. Recorded-vs-binding, CORRECTED in draft 2
(the draft-1 phrase "the FULL resource vector binds" overclaimed — B_k's four
components did not cover this vector, so CPU, I/O, network and accelerator
work were recorded but unbounded, review ranked concern 2): every component
above is either a PRIMARY budget component of B_k or a HARD SECONDARY
CEILING under §8.1; no measured component is free [STIPULATED: ASM-0881].
The analytic neural-FLOP ledger
(2·params·tokens + attention terms, pinned formula sheet) is REPORTED always,
BINDING never [STIPULATED: ASM-0810; literature warrant LIT-BACKED: SYS.md §9].

The measurable-cell matrix (declared up front so P3-E-CAL reports MISSING
cells fail-closed instead of discovering them) [STIPULATED per SYS.md §11]:

| Platform | (a) accel | (b) CPU-s | (c) bytes | (d) energy | (e) mem | (f,i) latency | (g) throughput |
|---|---|---|---|---|---|---|---|
| local box (2-vCPU EC2, no GPU) | n/a | ✓ | ✓ | **MISSING** (no RAPL [MEASURED: SYS.md §0]) | RSS ✓ | ✓ | ✓ |
| Modal GPU | ✓ | ✓ | ✓ | GPU-only via NVML total-energy counter (units/floor to confirm at P3-D-HW [LIT-BACKED: SYS.md §4 — UNVERIFIED cells named]); CPU energy MISSING | ✓ | ✓ | ✓ |
| ARC | survey pending (P3-D-HW opening question: any RAPL/wall-power path?) | | | | | | |

### 4.2 Load shapes

Adopt MLPerf's scenario machinery, not its workloads (no MLPerf artifact
exists at 100M–2B) [LIT-BACKED: SYS.md §1]: SingleStream — CLOSED-LOOP by
MLPerf definition, yielding isolated per-query SERVICE-TIME percentiles,
every such figure labelled "service-time (closed-loop, unloaded)" — and
Offline (batch throughput) MANDATORY per arm; Server/Poisson (OPEN-LOOP
scheduled arrivals) MANDATORY for any latency-under-offered-load claim and
otherwise optional per rung under the pinned concurrency distribution
(draft 1 prohibited closed-loop drivers for every percentile claim while
mandating SingleStream, a contradiction the review caught; SYS.md §1/§5
distinguish the two claim types and both scenarios survive under their
correct labels). Minimum run:
600 s or the statistical-sufficiency bound at our n, whichever binds; the
query-count-per-percentile table is computed from the MLPerf confidence
machinery at freeze; p50/p95 are the pinned percentiles and p99 is BANNED
below its supporting n (the 90th-percentile/99%-confidence bound alone needs
~24k queries) [LIT-BACKED: SYS.md §1; STIPULATED adoption].

### 4.3 Driver legality

For any latency-under-offered-load or throughput-conditioned percentile
claim: open-loop, seeded, pinned-schedule query issue; latency measured from
INTENDED issue time; closed-loop next-query-on-completion drivers PROHIBITED
for those claims (coordinated omission is a failure of closed-loop
measurement PRESENTED AS latency-under-load, not of closed-loop service-time
measurement as such). Closed-loop SingleStream-style drivers remain valid for
isolated service-time percentiles, and every such figure carries the
"service-time (closed-loop, unloaded)" label so the two claim types can never
be conflated [LIT-BACKED: SYS.md §1/§5; STIPULATED: ASM-0882 — corrects the
draft-1 blanket prohibition]. MLPerf caching prohibitions bind all arms: no caching of queries,
responses, or activation-derived values; KV-cache reuse only within a batch
[LIT-BACKED: SYS.md §1; closes T-C6]. Any serving-rate claim is goodput-style
(rate under a stated percentile SLO), never bare tokens/s [STIPULATED per
SYS.md §5].

### 4.4 Warm/cold three-state protocol

Per arm: **COLD** — fresh container/process, page cache dropped where
privileged (else fresh-VM/container semantics; mechanics per platform are a
P3-D-HW deliverable), model+index load INSIDE the measured window → startup
time + bytes-to-first-answer (= KOT-SIZE/2 figure (4)); **WARM** — steady
state after a pinned warmup trace → p50/p95/throughput; BOTH reported, never
blended; cold runs repeated ≥10× (cold-path variance is I/O-dominated)
[STIPULATED per SYS.md §6, Traeger-grounded]. W1 admissibility binds on BOTH
states; headline cost figures are warm with cold published alongside
[STIPULATED per SYS.md §11 recommendation].

### 4.5 Repeatability protocol (draft skeleton; P3-D-HW hardens)

(a) same-host same-session A/B/A/B interleave for every S-vs-comparator cost
comparison — never across days or hosts; (b) host fingerprint per run (CPU
model, GPU UUID, driver, clocks, container image hash); (c) per-session
calibration probe (fixed synthetic workload at session start + end); sessions
whose probe CoV exceeds the pinned gate (draft 5%, calibrated in P3-E-CAL) are
discarded fail-closed; (d) ≥10 repetitions per cell, rank-based nonparametric
CIs, no normality assumption, cost summaries = arithmetic mean for costs /
harmonic for rates, ratios never summarised directly; (e) environment pinned
PLUS a randomized-dummy-env-var replicate to bound UNIX-layout bias (>10%
shifts documented from env size + link order alone) [STIPULATED adoption;
LIT-BACKED: SYS.md §7 (Hoefler–Belli SC15 rules 3–9; Mytkowicz ASPLOS 2009)].

### 4.6 Energy rules (fail-closed)

Energy figures are counter-based COMPONENT ESTIMATES with a declared
measurement boundary, whole-run integration (never query-level spot reads —
NVML power polling samples only ~25% of runtime on A100/H100), preferring the
cumulative energy counter over power polling; where no counter exists the
energy cell is reported MISSING — never modelled from TDP or utilisation. NO
Programme-3 energy figure may be labelled MLPerf-Power-compliant (no wall
meter, no PTDaemon, no bare metal anywhere in the pool)
[LIT-BACKED: SYS.md §2–§4; STIPULATED: the §1.3 no-silent-fallback convention
applied to the rig]. Energy is reported in Joules and NOT monetised in
KOT-LIFE/1 (monetising component-estimate Joules launders precision)
[STIPULATED per SYS.md §11].

---

## 5. KOT-LIFE/1 — the lifecycle-ledger template

Every W1-relevant system (S and every comparator) publishes one ledger record;
the ledger CO-REPORTS with every W1 claim and feeds kill condition K-P3v2(6);
it does not gate W1 numerically (no non-arbitrary common unit exists across
authoring-hours and GPU-hours — the honesty mechanism is publication + the
kill condition, which gates by PER-LINE Pareto domination, §5.1)
[STIPULATED: ASM-0810 restated].

Draft-2 rewrite (review-flagged: "the lifecycle schema cannot currently
execute K-P3v2(6)" — amortisation/crossover were empty objects, "dominated"
was undefined, and the schema predated the landed STORE.md requirements):

### 5.1 The template (draft JSON schema `kot-life/1-draft2`)

```jsonc
{
  "schema": "kot-life/1-draft2",
  "system_id": "...",                       // arm or comparator, artifact hash
  "donor_provenance": {                     // per neural component
    "model": "name+revision",
    "pretraining_tokens": "...",            // stated where known
    "pretraining_compute_est": "...",       // STATED, NEVER NETTED OUT
    "contamination_status": "known|unknown" // §1.9(1) symmetric disclosure
  },
  "tuning": {                               // the tuning-symmetry audit trail
    "accelerator_hours": 0.0, "cpu_hours": 0.0,
    "selection_rule_ref": "prereg §",       // FIXED, pre-registered
    "dev_split_hash": "sha256:..."          // disjoint from index suite (§6.4)
  },
  "store_costs": {                          // per store artifact — the STORE.md
    "record_classes": ["..."],              // §6 three-sub-line discipline;
    "build_mint": {                         // (a) build/mint, denominated per
      "accepted_records": 0,                //     ACCEPTED CHECKABLE record:
      "candidate_records": 0,               //     rejected-candidate attrition
      "source_items": 0,                    //     visible; article→fact yield
      "authoring_hours": 0.0,               //     n measurable, never assumed
      "authoring_usd": 0.0,
      "parse_embed_index_compute": {"cpu_hours": 0.0, "accel_hours": 0.0}
    },
    "review_provenance": {                  // (b) recurring human review +
      "review_hours": 0.0,                  //     provenance verification,
      "redundancy_multiplier": 1.0,         //     with the crowd-redundancy
      "provenance_verification_hours": 0.0  //     multiplier explicit
    },
    "staleness_refresh": {                  // (c) recurring, DECLARED cadence
      "cadence": "...",
      "per_fact_refresh_hours": 0.0,
      "reindex_rollback_compute": {"cpu_hours": 0.0, "accel_hours": 0.0},
      "dependency_fanout_per_update": 0.0   // entailment/reindex fan-out
    },
    "fixed_vs_variable": {                  // one-time infra vs per-record
      "fixed_usd": 0.0, "variable_usd_per_record": 0.0
    },
    "construction_bytes": 0                 // = KOT-SIZE/2 figure (5)
  },
  "hardware_occupancy": {                   // EXPLICIT formulas, computed:
    "ram_rent_usd":     "GB_resident * hours_served * pinned_gb_hour_price",
    "accel_rent_usd":   "accel_hours * pinned_sku_hour_price",
    "storage_rent_usd": "GB_stored * months * pinned_gb_month_price"
  },
  "per_query_vector_ref": "kot-cost record",// measured KOT-COST/2 output
  "amortisation": {
    // DEFINED (draft 1 left these {}): per volume q and per separately-
    // denominated unit u ∈ {usd, human_hours, joules_where_measured}:
    //   TCO_u(q) = fixed_u + build_u + q * per_query_u + refresh_u(q)
    // published PER UNIT, never combined across units.
    "q1e3": {"usd": 0.0, "human_hours": 0.0, "joules": null},
    "q1e6": {"usd": 0.0, "human_hours": 0.0, "joules": null},
    "q1e9": {"usd": 0.0, "human_hours": 0.0, "joules": null}
  },
  "sardana_crossover": {
    // DEFINED: per comparator C and unit u, the volume q* solving
    // TCO_u(S, q*) = TCO_u(C, q*) — where the per-query gap repays the
    // lifecycle delta; null where the curves do not cross.
    "per_comparator": {}
  },
  "energy_note": "J reported per §4.6 boundary, not monetised",
  "price_pins": [{"item":"...","usd":0,"date":"YYYY-MM-DD","url":"..."}]
}
```

**"Dominated", defined** (draft 1 refused to combine units but never said what
K-P3v2(6) tests — review-flagged): S is dominated by comparator C iff
TCO_u(C, q) ≤ TCO_u(S, q) on EVERY unit u measurable for BOTH arms
(usd; human-hours; joules where the §4.6 boundary covers both) at ALL THREE
pinned volumes, with strict inequality in at least one (u, q) cell —
per-line Pareto domination, no cross-unit exchange rate, ever; a unit
measurable for only one arm is excluded from the domination test and
disclosed [STIPULATED: ASM-0886].

Rationale lines: the Sardana crossover-volume line is adopted per the
lit-review — optimal size depends on inference volume, FLOPs ≠ dollars (1.3%
FLOP gap vs 36% cost gap at 50× utilisation difference), and dimension-drop
arms inherit donor pretraining stated-not-netted because the donor was sized
for someone else's inference demand [LIT-BACKED: SYS.md §9
(arXiv:2401.00448 verified at source)]. Storage RENT is negligible at our
MB-scale stores (~$0.01/month-class, five orders below a GPU-hour); the
binding I/O economics are cold-start bytes (≥8 s/GB at gp3 baseline), egress
under figure (6), and request costs only at the 10⁹ volume — the ledger
charges resident-RAM (RSS) rent per five-minute-rule logic rather than storage
rent, with the occupancy formulas now EXPLICIT in the schema
[LIT-BACKED: SYS.md §8; STIPULATED adoption]. The store line's three
sub-lines, the accepted-checkable-record denominator (the mint anchor
$0.078/record and the expert anchor $219/article are DIFFERENT denominators,
not a bracket), the redundancy multiplier, and the refresh/reindex/rollback +
dependency-fan-out fields consume the landed STORE review; the MEASUREMENT of
those fields (yield n, attrition, time distributions, fan-out) is P3-D-LIFE's
§7-protocol work — this schema makes the categories un-hideable, it does not
claim the numbers [LIT-BACKED: STORE.md §6–§8; STIPULATED: ASM-0886]. Price
pins carry date + URL and are refreshed at P3-D-LIFE freeze (prices drift)
[STIPULATED].

### 5.2 Tuning symmetry (the operative rule)

Symmetry binds on TOTAL tuning compute actually spent (accelerator-h + CPU-h,
logged into `tuning`), with a FIXED pre-registered selection rule on the
hashed dev split; equal config counts are NOT sufficient. An architecture that
only wins with more search compute has not won [STIPULATED: ASM-0812
restated; data-matched ≠ compute-matched is the BabyLM lesson as read in
EVAL.md §7].

---

## 6. The decontamination screener — kot-decon/1 (draft spec)

### 6.1 What it is and is not

A GROSS-LEAKAGE gate ONLY: paraphrase/translation-level leakage defeats
n-gram/string decontamination (a 13B trained on rephrased test sets passed
standard decontamination at GPT-4-level scores) [LIT-BACKED: EVAL.md §4
(arXiv:2311.04850)]. The screener is therefore necessary-not-sufficient by
design; the sealed evaluation (§7) is the fairness instrument. A win whose
store fails the screener is VOID, not caveated [STIPULATED: ASM-0812].

### 6.2 Mechanism (CPU-only, local box, ~$0 compute; adjudication hours are
a real, logged cost — see flag handling below)

Inputs: every kernel/world/store record (all text fields canonically
serialized) × every item of the frozen index suite (question + choices +
answer + source-page text where the benchmark publishes it). Two channels
[STIPULATED, thresholds draft — CALIBRATED in P3-E-CAL on planted positives
(verbatim/near-verbatim insertions) and known negatives before the gate is
frozen]:
1. **n-gram overlap**: word-level 8-gram exact match after case/punctuation
   normalisation; ANY hit flags the pair. (Draft n=8 balances the OLLv2-era
   10-gram convention against our short typed records; the planted-positive
   calibration decides.)
2. **Embedding similarity**: pinned small sentence-embedding model
   (name+revision pinned at freeze), cosine ≥ 0.85 (draft) flags the pair.
Flag handling, CORRECTED in draft 2 (the draft-1 sampling path — "stratified
sample + top decile if >500 flags" — let a win-VOIDING gate clear unreviewed
flags; unreviewed flags cannot be treated as benign, review-flagged):
EVERY flagged pair is human-adjudicated {benign-collision, leakage}; an
unadjudicated flag COUNTS AS LEAKAGE. There is no sampling path: if the flag
count exceeds adjudication capacity, then either the thresholds were
mis-calibrated — recalibrate on the planted positives/negatives, bump the
screener version, re-run — or the store is not decontaminatable at that size
and the dependent wins are void. Adjudication hours are logged into
KOT-LIFE/1's review line (a real cost, not ~$0). ANY leakage adjudication on
a store record voids wins that store touches [STIPULATED: ASM-0888].

### 6.3 Authoring-provenance rule (the forward-looking half)

Stores may not be authored, selected, or grown USING any index item, its
paraphrase, or its source page. Enforcement: every store record carries a
provenance line (source, authoring session, date); authoring sessions log
their input corpora; the screener cross-checks declared sources against the
suite's source list [STIPULATED: ASM-0812; this is what closes T-S2 to the
extent it is closable — residual researcher adaptation is T-S4, answered by
the sealed eval].

### 6.4 Ancillary disjointness duties

The same machinery mechanically checks: dev-split vs index-suite disjointness
(T-T2); the kot-pack smoke set vs index items (§3.2(5)); PR-KOT/1 generator
outputs vs frozen-suite items per release [STIPULATED].

### 6.5 The donor-weights side

For OPEN comparator/donor weights with logprob access, the Oren
exchangeability test is a cheap runnable diagnostic (canonical-order vs
shuffled likelihood); a positive PROVES contamination, a negative proves
NOTHING — reported as disclosure, never as clearance [LIT-BACKED: EVAL.md §4
(arXiv:2310.17623); STIPULATED adoption into the toolbox]. Closed corpora
remain the §1.9(1) standing limitation, disclosed symmetrically.

---

## 7. The sealed-evaluation protocol (draft; frozen by P3-D-SEAL)

### 7.1 The gate shape (corrected form, adopted verbatim from the lit-review)

A W1-relevant claim passes the sealed evaluation only if S BEATS the
resource-matched baselines ON THE SEALED RELEASE by a registered margin,
uncertainty-controlled — CORRECTED in draft 2 (the draft-1 gate used the
point estimate (S − B) ≥ δ_sealed and never said which comparators run
sealed, review ranked concern 3): primary sealed endpoint = the simultaneous
one-sided LCB95 of (INDEX_sealed(S) − INDEX_sealed(C)) > δ_sealed for EVERY
comparator C in the pre-registered F(B_k), ALL run on the same sealed items
under the same pinned harness (the full pre-registered comparator set, not a
single convenience baseline), with multiplicity controlled by the same §9.2
machinery as the frozen-suite analysis; δ_sealed frozen in the prereg BEFORE
unsealing; a point estimate above δ_sealed with LCB below it is NOT a pass
(§9.1 discipline applies on the sealed side too) [STIPULATED: ASM-0887].
Directional consistency with the frozen suite is
necessary but NOT sufficient. The frozen-vs-sealed gap is a SECONDARY
overfitting diagnostic whose band derives from ≥2 MOCK SEALED RELEASES
produced by the §7.2 recipes and graded on the calibration anchors during
P3-E-CAL (§10 gate 8) — CORRECTED in draft 2: frozen-suite seed/prompt
replicate variance cannot calibrate the PRODUCER/DIFFICULTY shift between a
frozen suite and a fresh release (review-flagged); GSM1k's observed up-to-8%
drops describe one tested population and license no universal tolerance
constant [STIPULATED: ASM-0887, per EVAL.md §4 (corrected reading of
arXiv:2405.00332); supersedes any "directional consistency" gate phrasing in
earlier drafts].

### 7.2 Production recipes (three, per domain class)

1. **D4/D5 procedural domains**: pinned generator FAMILIES (PR-KOT/1; a
   CLUTRR-class re-implementation) with — because fresh seeds from a known
   generator are NOT sealing — genuinely held-out generator families /
   rule-combinations reserved per release, and/or maintainer-held generator
   secrecy [STIPULATED per EVAL.md §4]. Cheapest producer; runs on the local
   box.
2. **Knowledge/instruction domains**: GSM1k-style matched authoring, with the
   difficulty-matching triple (human solve rate, solution step count, answer
   magnitude) as the per-domain difficulty-calibration instrument
   [LIT-BACKED: EVAL.md §4 (arXiv:2405.00332)].
3. **R-3+ live domains**: LiveBench-style versioned refresh — every release a
   new version, never silently folded in; release ID pinned from the GitHub
   tags at freeze (the live site rendered empty at review time)
   [LIT-BACKED: EVAL.md §4 (arXiv:2406.19314); STIPULATED adoption].

### 7.3 Operational rules (registered at P3-D-SEAL freeze)

(a) custody + access rules for sealed sets (who holds them, storage,
disclosure controls); (b) ONE-SHOT use — each sealed release grades at most
one claimed evaluation and is then BURNED; (c) post-evaluation disclosure of
items and per-item outputs; (d) independent difficulty calibration per domain
(the matching triple); (e) no-feedback — anything learned from release N's
disclosure informs only claims graded against a fresh release N+1; (f) the
fresh-facts store leg, chronology and symmetry RESOLVED in draft 2
(P3-LR-STORE landed; the review flagged the unresolved chronology/oracle
problem — draft 1 froze architecture and store BEFORE the sealed set existed
yet required temporally-fresh facts, without saying who receives new
evidence, whether stores may update, or whose refresh cost is charged):
architecture + store freeze FIRST, per the sealing chronology; the sealed
release then publishes, alongside its items, a pinned COMMON fresh-evidence
snapshot; EVERY arm — store-based and neural/RAG baseline alike — receives
the same snapshot and the same metered refresh budget (ingest/update/reindex
inside the measured window; costs logged symmetrically into KOT-LIFE/1's
staleness-refresh line and co-registered with δ_sealed); live search is
enabled for every arm under the same budget or for none; supplying the needed
fresh evidence to any single arm is an ORACLE channel and voids the release;
where no refresh mechanism is affordable, the fresh-facts leg is DROPPED for
that release and the sealed claim says so explicitly. Whether the store-side
remedy is a maintained store or live retrieval is P3-D-SEAL's registered
decision; producer-side truth-refresh cost is disclosed and never charged
asymmetrically to the store arm [STIPULATED: ASM-0887; per STORE.md
§6/§7.3/§7.7]. Independently held-out domains remain the leg's alternative
where freshness is not required [STIPULATED per EVAL.md §4/§8.5/§8.7].
Producer independence (maintainer-held
secrecy vs held-out families vs cross-vendor generation) is the one governance
question the literature cannot answer and is flagged to P3-D-SEAL + maintainer
[STIPULATED].

---

## 8. The neural frontier-builder spec (draft; frozen by P3-D-FRONTIER)

### 8.1 Inputs and outputs

Input: a pre-registered budget vector B_k, REDEFINED in draft 2 with two
tiers (review ranked concern 2: the draft-1 four-component B_k left CPU
seconds, accelerator work, storage/network I/O and throughput recorded but
unbounded while §4.1 claimed "the full vector binds" — a system could consume
far more of any of them and still win W1; and energy silently dropped out
whenever unmeasurable, contradicting the parent's "energy explicitly binds"
W1) [STIPULATED: ASM-0881]:

- **PRIMARY components** (the headline budget): max canonically-packed
  serving bytes (figure 1); max p95 service-time latency — plus max p95
  latency under the pinned open-loop load wherever an offered-load claim is
  made (§4.2/§4.3 labels); max energy/query at the declared boundary; max
  peak accelerator memory + host RSS.
- **HARD SECONDARY CEILINGS** (admissibility-binding, registered in the same
  prereg): max CPU-seconds/query; max accelerator-time/query; max bytes read
  (storage + network)/query; max TTFT/TPOT for generative arms; min
  throughput under the pinned load. Set generously (draft: 3× the strongest
  fitting comparator's measured value, pinned at prereg freeze) so they
  exclude resource laundering without deciding close competition; exceeding
  ANY ceiling makes the arm inadmissible.
- **ENERGY RULE**: a W1 run executes on ONE common platform for all arms with
  a common MEASURABLE energy boundary, at which energy binds for every arm
  (current candidate: the pinned Modal SKU's NVML total-energy counter,
  units/floor confirmed by P3-D-HW). If the chosen platform has no measurable
  boundary, the claim is never silently energy-free: it must carry the
  explicit label ENERGY-EXCLUDED on its claim surface, and the prereg must
  justify the platform choice.
- **ADMISSIBILITY UNDER UNCERTAINTY** (review-flagged: point-estimate
  membership makes frontier composition unstable near ceilings): membership
  of F(B_k) — and S's own admissibility — is decided on the UCB95 of each
  measured resource component over the §4.5 repetitions, never the point
  estimate; an arm whose UCB95 straddles a ceiling is inadmissible
  (fail-closed), and near-ceiling exclusions are disclosed in the search log.

Output: the
comparator set F(B_k) — every pre-registered, reproducible OPEN comparator and
baseline family fitting EVERY component of B_k under KOT-SIZE/2 + KOT-COST/2,
warm and cold, EXPLICITLY INCLUDING systems smaller or cheaper than S (closes
T-F3); anchor models are inference-optimal artifacts (SmolLM2-class), not
compute-optimal strawmen (closes T-F4) [STIPULATED: ASM-0812 restated;
LIT-BACKED anchor status: SYS.md §9].

### 8.2 Source families (the mandatory checklist)

(i) strongest open pure-neural models at or below budget (pinned
name+revision at the consuming experiment's prereg freeze); (ii)
budget-optimising transforms — quantisation, structured pruning, distillation
— applied best-effort; quantisation symmetry: if the neurosymbolic arm
quantises, every comparator gets the same best-effort quantisation; (iii)
**neural + retrieval**, CORRECTED in draft 2 (P3-LR-RAG landed; the review
flagged that "same corpus, same retriever/index" can HANDICAP a conventional
RAG baseline whose native retrieval operates over different objects — "same
source snapshot" is not "same retriever": converting one snapshot into
passages vs records vs triples indexes different objects): conventional
RAG / tool-use built from the SAME pinned source-evidence snapshot under the
SAME byte/build/query budgets as the kernel arm, implemented from a pinned
STANDARD harness (FlashRAG-style, release pinned), with BOTH BM25 and dense
retriever cells mandatory, retrieval recall@k reported separately from
end-task accuracy, and identical index-bytes + build-compute + query-compute
ledgers on both arms; the identical-vs-architecture-specific retriever
decision is made per factorial cell by P3-D-RAGC under FRONT/1 §5's binding
default rules [LIT-BACKED: RAG.md §3/§6; STIPULATED: ASM-0890] (the strongest
missing control; the aligned-non-kernel store does NOT replace it); (iv) optimised/ADAPTIVE test-time compute —
mandatory to CONSIDER, included where task-appropriate and budget-feasible:
the verified result (compute-optimal test-time strategies >4× over best-of-N;
a smaller model beating a 14× larger one FLOPs-matched) is CONDITIONAL on
non-trivial base success and verifier quality, so naive best-of-k is too weak
as the only entry but adaptive strategies are not unconditionally mandatory
either [LIT-BACKED: EVAL.md §7 (Snell et al., ICLR 2025, verified at the
review's exact link); STIPULATED adoption of the conditional reading]; any
learned verifier's training cost logs into KOT-LIFE/1 symmetrically; (v)
training-compute-matched from-scratch twins, required only where the
neurosymbolic arm itself trains from scratch (H-GU) [STIPULATED: ASM-0812].

### 8.3 Discipline

Comparator pinning: names/revisions/recipes pinned at prereg freeze of the
consuming experiment; the builder's SEARCH LOG (what was considered, what fit,
what was excluded and why) is published with every F(B_k) (T-F2 disclosure);
per-comparator tuning compute logs into KOT-LIFE/1 under the same
total-compute symmetry rule (§5.2); every comparator runs under the same
packing script, cost rig, driver legality, and caching rules as S
[STIPULATED].

### 8.4 Reporting

The full staircase/Pareto envelope of neural and neural-retrieval points
(index vs bytes; index vs cost) is published with S plotted against it; W1
means S lies significantly above the envelope at its budget (§9.1–9.2), not
that it won a favourable neighbourhood; a W1 PASS licenses ONLY the narrowed
claim: "S exceeds every pre-registered, reproducible open comparator and
baseline family searched under budget B_k by ≥ δ_k on KOT-AI-INDEX/2-vN" —
the literal universal ("all models of the same size") is retired from every
claim surface [STIPULATED: ASM-0810 restated].

### 8.5 The factorial attribution controls (framework-owned; NEW in draft 2)

The parent's mandatory control design (programme doc §2.2(2), ASM-0812) is
part of THIS framework, not of individual experiments — draft 1 said so and
then never specified it (review ranked concern 1). The cell inventory,
restated verbatim from the parent and organised on its three axes, each cell
annotated with what it discriminates [STIPULATED: ASM-0891; cell list
inherited from ASM-0812]:

| Axis | Cell | Discriminates |
|---|---|---|
| content-type | (a) seed-pinned deranged store→item addressing | alignment vs content (the f2b control, inherited) |
| content-type | (b) label permutation within records | label semantics vs record structure |
| content-type | (c) irrelevant-but-structurally-matched records (same schema/types/sizes) | structural priming vs content |
| content-type | (e) aligned-non-kernel store (matched size + alignment, plain-English typed records) | kernel semantics vs typed store |
| content-type | (g) kernel-as-text null at matched token budget | store machinery vs plain conditioning |
| retrieval-architecture | (f) matched generic-RAG/tool-use comparator (§8.2(iii)) + BM25 / dense / position-shuffle / random-document cells | typed store + kernel retrieval vs conventional retrieval; prompt-perturbation effects |
| retrieval-architecture | (d) edge/relation shuffling (graph arms) | graph structure vs node content |
| executor | engine-on vs engine-off (same store, execution disabled); generic-executor substitution where meaningful | deterministic execution vs storage/retrieval |

Rules: (1) every Phase-2 W1-relevant prereg NAMES which cells it instantiates
and what each discriminates — the full cross product is never mandatory, the
named-cells-with-discrimination-claims rule is; (2) the six-way attribution
factorisation (kernel semantics / structured storage / retrieval /
deterministic execution / retry-search / integration) is decomposed as far as
the instantiated cells allow; (3) the retrieval-architecture cells are
P3-D-RAGC's to implement under FRONT/1 §5's binding defaults; (4) the
kernel-semantics-vs-typed-store cell — (e) vs the kernel store, same
retriever — has NO published precedent and is our own instrument, so it
carries that load alone [LIT-BACKED: RAG.md §6 closing]; (5) the EXECUTOR
axis, which the parent names without enumerating, gets the two DRAFT cells in
the table (owned here; P3-D-RAGC/P3-D-ORACLE freeze them)
[STIPULATED: ASM-0891].

---

## 9. The statistical analysis plan (draft; §2.5 house rules operationalised)

### 9.1 Margin wins

A margin-δ superiority claim requires the one-sided 95% lower confidence
bound ITSELF to clear the margin: LCB95(INDEX(S) − INDEX(C)) > δ_k for every
C ∈ F(B_k). A point estimate above δ with LCB merely > 0 is NOT a margin win
and is never reported as one [STIPULATED: ASM-0813].

### 9.2 Multiplicity and resampling (the corrected estimand)

- Family-wise error control across the pre-registered comparator set (and
  across domains where per-domain claims are made). Draft procedure: max-t
  style simultaneous one-sided bounds computed from the joint bootstrap
  distribution over comparators (the same resamples score every comparator, so
  correlation is preserved and the simultaneous bound is not needlessly
  conservative); fallback if the joint bootstrap is unstable at our n:
  Holm–Bonferroni on the per-comparator one-sided p-values. The choice is
  pinned at P3-D-INDEX freeze after P3-E-CAL variance data [STIPULATED].
- Bootstrap estimand, corrected per the lit-review: FIXED registered domain
  and benchmark weights; the hierarchical bootstrap resamples ITEMS (and
  prompts/seeds where applicable) WITHIN benchmarks, preserving PAIRED
  per-item predictions between S and each comparator; benchmark families are
  NOT resampled (a registered suite is not a sample from a benchmark universe)
  [STIPULATED per EVAL.md §2 — the earlier "bootstrap over benchmark families"
  phrasing is superseded].
- Variance/size asymmetry (250-item vs 14k-item benchmarks entering with equal
  weight) is a registered normative choice, priced by reporting per-benchmark
  CIs in the vector [STIPULATED per EVAL.md §2].

### 9.3 Non-inferiority vs equivalence

"Retains capability" claims are NON-INFERIORITY: single one-sided test/CI
against the pre-registered margin. TOST is reserved for genuine EQUIVALENCE
claims. All retention claims in Programme-3 preregs (H-DD's central claim
included) use the non-inferiority form [STIPULATED: ASM-0813].

### 9.4 The G1 Δ_max bound on the NORMALIZED scale (the coverage kill,
restated so it composes with the index)

The raw-scale identity Δ_B = κ_B × Δ_covered and its max-gain bound
κ_b(1 − a_b^cov) are stated on raw accuracy and are NOT valid under
chance/ceiling normalization without the denominator carried through
[STIPULATED per EVAL.md §5.3]. Normalized form, per benchmark b in domain d,
CORRECTED in draft 2 with the explicit headroom clamp (review-flagged:
"scalar clamping requires an explicit per-benchmark min/available-headroom
term"):

  Δ̃_max,b = min( κ_b · (1 − a_b^cov) / (ceiling_b − chance_b),
                  1 − min(s̃_b^B, 1) )

where s̃_b^B is the baseline family's normalized score on b — the second term
is the headroom left under the §2.3 scalar clamp, which a covered-item gain
cannot exceed; and κ_b = 0 ⇒ Δ̃_max,b = 0 with a_b^cov UNDEFINED-AND-UNUSED
(the review-flagged zero-coverage cell, now closed by definition rather than
left 0/0). Index-level bound with the registered weights w_d / w_{b|d}:

  Δ_max(INDEX) ≤ Σ_d w_d Σ_{b∈d} w_{b|d} · Δ̃_max,b

Validity conditions, ALL frozen (by P3-D-POWER) before any G1 kill may fire —
until then G1 outputs are provisional and kill nothing
[STIPULATED: ASM-0884]:
1. **Uncertainty by census mode** (corrected — draft 1 charged "counting
   uncertainty" to every census): a COMPLETE finite census of a frozen suite
   has NO counting uncertainty (the count is exact); a SAMPLED census carries
   sampling error; an AUTOMATED census carries measured classifier error.
   Each mode propagates its actual error, together with the a_b^cov
   estimation error, to UCB95(Δ_max); the kill compares UCB95(Δ_max) < δ_k,
   so the bound errs in the killed family's favour.
2. **Coverage-label direction, the load-bearing condition** (review-flagged:
   "an automatic NL classifier with false negatives would invalidate the
   upper bound"): "covered" means ANSWERABLE FROM THE STORE — a semantic
   judgement, not a string match. Since false NEGATIVES shrink κ_b and hence
   shrink an UPPER bound, protection is mandatory: uncertain items count as
   COVERED; an automated labeller must have its false-negative rate measured
   against a human-adjudicated audit sample and folded into an upper bound on
   κ_b; the κ adjudication protocol (audit-sample size, double-labelling,
   inter-annotator agreement threshold) and its HUMAN-HOURS accounting (a
   real cost logged to KOT-LIFE/1 — the "~$0" is compute-only) are frozen by
   P3-D-POWER before any kill.
3. **Oracle quarantine**: manual formalisation used to PROVE answerability
   validates the labeller only; it is an oracle diagnostic under the ASM-0814
   label, never a capability input, and its hours are logged.
4. Below-floor components excluded per the corrected §2.5 criterion;
   per-benchmark clamping consistent with §2.3.

Computable from censuses + baseline accuracies, CPU-only compute (the
adjudication hours above are the real cost); consumed by P3-D-POWER and by
K-P3v2(1). Given measured external coverage (0/1,550; 0/1,000; 0.3542
friendliest-corpus) [MEASURED: §0 refs], this bound is EXPECTED to bind hard
and early — that is its job, and an early paper kill is a success of the
framework, not a failure of it [STIPULATED: ASM-0884].

### 9.5 Standing discipline

One primary endpoint per experiment; kill criteria verbatim in the prereg;
verdicts generated by the mechanical grader (verdict-gen) and cross-vendor
audited; anything off the pinned script is quarantined exploratory
[STIPULATED: standing practice, inherited unchanged].

### 9.6 δ_k margin machinery (how margins get set, not what they are)

δ_k values are NOT set in this draft. Machinery: after P3-E-CAL, δ_k is set
per rung subject to BOTH (a) a noise floor — δ_k ≥ 2 × SD_cal(INDEX), the
replicate standard deviation of the index on calibration seed/prompt-order
replicates (a margin inside instrument noise is unfalsifiable), and (b) a
normative materiality floor set by maintainer fork (what gap is worth
claiming). δ_sealed (§7.1) is set by the same machinery on the sealed suite's
variance estimate. Both freeze in P3-D-INDEX / the consuming prereg BEFORE any
campaign result exists [STIPULATED].

---

## 10. The calibration prereg — P3-E-CAL (draft skeleton; freezes via
experiment-designer after P3-D-INDEX + P3-D-HW)

Purpose: validate the instrument on cases with KNOWN answers before it ever
judges a neurosymbolic system. PURE-NEURAL models only — no store, no kernel,
no oracle anywhere in this experiment, so the NL wall is untouched by
construction [STIPULATED: ASM-0812 §2.4 executed].

- **Subjects**: SmolLM2-135M-Instruct / 360M-Instruct / 1.7B-Instruct (pinned
  revisions at freeze; Instruct because D6/IFEval requires it; base variants
  optional diagnostic column) [STIPULATED].
- **Instrument gates (all must pass; no architecture claim is made)**:
  1. **Separation on a COMMON index** — CORRECTED in draft 2 (draft 1
     compared "rung-appropriate" indices across models at different rungs,
     which §2.7 itself forbids; and treated model size as a known-answer
     ordering, which it is not once data/tuning/recipes differ — review
     ranked concern 3): pairwise simultaneous
     LCB95(INDEX_COMMON(larger) − INDEX_COMMON(smaller)) > 0 for
     1.7B > 360M > 135M, where INDEX_COMMON is ONE fixed component set (the
     R-1 membership) scored under ONE protocol identically for all three
     models. Anchor status, honestly: the three are same-family SmolLM2
     checkpoints sharing a data recipe and tuning lineage — the closest
     available approximation to a known-answer ordering — but the ordering is
     a strong instrument DIAGNOSTIC, not ground truth; a FAIL blocks the
     freeze (conservative) and triggers instrument-vs-anchor localisation
     rather than an automatic index falsification [STIPULATED: ASM-0889].
  2. **Floor table**: per-component (s − chance) with CIs per model → the
     registered below-floor exclusion lists per rung (§2.5), INCLUDING the
     literature-absent tiny-scale D4 floors (CLUTRR/ProofWriter prompted at
     135M–1.7B: no published numbers found — must be measured here)
     [STIPULATED per EVAL.md §8.4].
  3. **Variance decomposition** — CORRECTED in draft 2 (draft 1's "k ≥ 3
     seeds + prompt-order permutations" pooled distinct variance sources and
     cannot estimate SD_cal reliably; prompt-order permutations are
     deterministic reconfigurations, not independent replicates —
     review-flagged): estimate SEPARATELY (a) item-sampling variance
     (hierarchical bootstrap within benchmarks, §9.2), (b) decoding
     randomness (seed replicates; zero for deterministic MC-logprob
     components), and (c) run-to-run harness variance (repeated identical
     runs). Prompt-order permutations are reported as a systematic
     SENSITIVITY SPAN, never pooled as noise. Replicate counts per source are
     POWERED from a pilot against a registered precision target on SD_cal —
     k ≥ 3 is a floor, never a sufficiency claim. SD_cal feeds the §9.6 δ
     machinery [STIPULATED: ASM-0889].
  4. **Anchoring**: KOT-SMOL-CONT/1 own-harness within ±2.0 pp of published
     card numbers on variant-matched cells (harness-fidelity gate) [STIPULATED:
     benchmark-evaluation-strategy §(c)].
  5. **Cost-rig repeatability**: calibration-probe CoV within the pinned gate
     (draft 5%) across ≥3 sessions on ≥2 days, per platform (local box; one
     pinned Modal SKU); the measurable-cell matrix (§4.1) confirmed by
     attempting every cell and logging MISSING fail-closed; ≥10 reps/cell,
     rank-based CIs [STIPULATED per SYS.md §7/§11].
  6. **Screener calibration**: kot-decon/1 thresholds validated on planted
     positives/negatives (§6.2) [STIPULATED].
  7. **Saturation gate** (NEW in draft 2, feeds §2.3): no calibration anchor
     at the rung clamps to 1.0 on any in-scalar component; a saturating
     component's ceiling is re-estimated headroom-preserving (or the
     component enters the scalar unclamped) before freeze
     [STIPULATED: ASM-0889].
  8. **Mock sealed releases** (NEW in draft 2, feeds §7.1): ≥ 2 mock releases
     per §7.2 production-recipe class, graded on the calibration anchors →
     the frozen-vs-sealed shift distribution for the §7.1 secondary band
     (frozen-suite prompt variance cannot calibrate producer/difficulty
     shift) [STIPULATED: ASM-0887].
- **Primary endpoint** (one): the common-index separation gate (gate 1, 2
  pairwise simultaneous bounds) — the single property without which the index
  cannot adjudicate W1 at all. All other gates are named instrument gates
  reported alongside [STIPULATED: one-primary discipline].
- **Kill criterion (verbatim, draft)**: "If INDEX fails the common-index
  separation gate (any pairwise simultaneous LCB95 ≤ 0 on INDEX_COMMON, §10
  gate 1) across the same-family anchor triple, or the cost-rig probe CoV
  exceeds its gate in ≥50% of sessions on the primary platform, KOT-FAIR/2
  does not freeze; P3-D-INDEX re-enters design with the failure localised
  (component variance table / rig variance log / anchor-vs-instrument
  diagnosis per gate 1)."
- **Envelope**: instrument-only; licenses no capability, efficiency, or
  architecture claim; results index to {suite version, harness commit, model
  revisions, platforms} [STIPULATED].
- **Cost class**: local box + Modal free credits; the 1.7B eval is the only
  GPU-preferring cell; subsampled n per benchmark chosen at freeze against
  the §9.2 variance targets. COMPUTE lands in the free pool; the REAL costs —
  multi-day calibration oversight, mock sealed-release authoring (gate 8),
  planted-positive adjudication — are human-hours, logged into KOT-LIFE/1
  lines, not zero (draft 1's "~$0" overclaimed; review-flagged)
  [STIPULATED: ASM-0886; consistent with programme doc §6 allocation policy].
- **Sequencing exemption honoured**: NLB work and coverage censuses/G1
  computations do NOT wait for this calibration (they make no index claim);
  every G4/W1-relevant experiment DOES require P3-E-CAL PASS
  [STIPULATED: ASM-0817].

---

## 11. Freeze conditions and the freeze graph (why this is a DRAFT)

RESTRUCTURED in draft 2 (review ranked concern 1: draft 1 said P3-D-INDEX
freezes the whole framework while its dependency list omitted the component
designs and its freeze conditions required mostly lit inputs rather than
completed designs). KOT-FAIR/2 freezes only via the dedicated
INTEGRATION/FREEZE step **P3-D-FAIR** (§12.1 bead 3), and NOT before ALL of
[STIPULATED: ASM-0880]:
1. **Every component design COMPLETE**, each owning exactly the section named
   here — P3-D-INDEX (§2 index pins, §3 packing + base image, §6 kot-decon/1,
   §9 analysis constants; and it authors the P3-E-CAL prereg), P3-D-HW (§4
   rig operating manual), P3-D-LIFE (§5 ledger), P3-D-SEAL (§7), P3-D-FRONTIER
   (§8.1–8.4), P3-D-RAGC (§8.2(iii) + §8.5 retrieval cells), P3-D-THREAT (§1).
   P3-D-INDEX does not absorb the others.
2. Lit-review inputs: P3-LR-RAG, P3-LR-STORE, P3-LR-PARSE LANDED 2026-07-11
   and are CONSUMED in this revision (§8.2(iii)/§8.5; §5 + §7.3(f); §2.6
   respectively). Still pending where named: P3-LR-TINY (R-0 twin recipes,
   feeds P3-D-BASE and through it the G4 block).
3. P3-D-HW resolves the named UNVERIFIED cells: NVML total-energy units +
   architecture floor on the actual Modal SKUs (the §8.1 energy-boundary
   candidate); the MLPerf LLM-constraint percentile; ARC RAPL/wall-power
   survey; cache-drop mechanics per platform.
4. P3-E-CAL passes its instrument gates (§10, now eight) and supplies:
   floor/exclusion lists (corrected §2.5 criterion), SD_cal from the variance
   decomposition, screener thresholds, rig CoV gates, saturation check, and
   the mock-sealed shift band.
5. Maintainer sign-off (the freeze is a maintainer-gated event; this document
   deliberately contains no freeze proposal).

Known drift risks carried openly: price pins (§5.1) drift and re-verify at
freeze; the LiveBench release ID was unverifiable at review time; CLUTRR
licence check (NC) at freeze; base-image contents will be contested (the §3.3
default-DENY protocol is the answer) [STIPULATED].

---

## 12. Hand-off

### 12.1 Beads this draft recommends the coordinator create (per the parent
bead's ON-COMPLETION instruction; recommendations only — no bd command is run
by this document)

1. **P3-D-THREAT** [DESIGN, P0; blocked by P3-MF-0 (+P3-LR-EVAL co)] — freeze
   the §1 resource/baseline threat model: red-team the enumerated channels,
   add EVAL.md §8.3 strategy-shopping as a named row (already folded in at
   T-I4), attempt counters for the §1.9 standing limitations or confirm them
   as standing, and gate the P3-D-INDEX freeze. Opening artifact: §1 of this
   document.
2. **P3-D-INDEX** [DESIGN, P0; blocked by P3-MF-0 + P3-LR-EVAL + P3-LR-SYS +
   P3-D-THREAT] — the INDEX-PIECE design bead (scope narrowed in draft 2; it
   is no longer "the KOT-FAIR/2 freeze vehicle"): pin KOT-AI-INDEX/2 dataset
   revisions + harness commit + prompt strategies + references/estimands +
   weights + the corrected exclusion criteria (§2); implement kot-pack/1 +
   freeze the base image (§3); implement kot-decon/1 (§6); the §9 analysis
   plan constants; author the P3-E-CAL prereg from §10 and spawn it. Opening
   artifact: this document.
3. **P3-D-FAIR** [INTEGRATION/FREEZE, P0; blocked by P3-D-INDEX + P3-D-HW +
   P3-D-LIFE + P3-D-SEAL + P3-D-FRONTIER + P3-D-RAGC + P3-D-THREAT +
   P3-E-CAL PASS; NEW in draft 2 per review ranked concern 1] — the
   KOT-FAIR/2 integration/freeze vehicle: verify every §11 condition,
   reconcile each component design against this framework document (drift
   between a component design and MF0 is resolved BEFORE freeze, by
   registered amendment), obtain maintainer sign-off, freeze KOT-FAIR/2 as
   one versioned object. No component design bead may declare the framework
   frozen [STIPULATED: ASM-0880].

### 12.2 Registered assumption entries (draft-2 change)

The corrections this revision introduces are load-bearing design premises, so
they are REGISTERED — appended to `registry/assumptions.jsonl` as the fresh
block **ASM-0880…ASM-0891** (append-only; the 0820 and 0850 blocks were taken
by the concurrent ORACLE and FRONT revision writers) — rather than left as
in-doc proposals. Draft 1's five in-doc proposals MF0-1…MF0-5 are SUPERSEDED:
their surviving content is folded into the entries below or stands unchanged
in the text under its inherited ids (ASM-0808/0810/0811/0812/0813/0814/0817).

- **ASM-0880** — the KOT-FAIR/2 freeze graph: P3-D-FAIR integration/freeze
  bead blocked by ALL component designs + P3-E-CAL + maintainer (§0, §11,
  §12.1).
- **ASM-0881** — two-tier W1 resource admissibility: primary B_k components +
  hard secondary ceilings; energy binds at a declared common boundary or the
  claim is labelled ENERGY-EXCLUDED; UCB95-based admissibility (§4.1, §8.1).
- **ASM-0882** — driver legality: closed-loop SingleStream valid for labelled
  service-time percentiles; open-loop mandatory for offered-load percentiles
  (§4.2–4.3, T-C5).
- **ASM-0883** — below-floor exclusion by minimum discriminative span,
  UCB95(s − chance) < Δ_disc (§2.5).
- **ASM-0884** — G1 validity preconditions: headroom clamp, zero-coverage
  rule, census-mode uncertainty, coverage-label false-negative protection, κ
  adjudication + human-cost accounting frozen before any kill (§9.4).
- **ASM-0885** — packing figure separation: figure (1) = as-built serving
  artifact; construction provenance = figure (5), co-reported (§3.1–3.2).
- **ASM-0886** — kot-life/1-draft2 schema: three store sub-lines, attrition,
  fixed/variable, record classes, refresh/reindex/rollback + fan-out,
  explicit occupancy formulas, defined amortisation/crossover, "dominated" =
  per-line Pareto at all three volumes; human hours never rounded to ~$0
  (§0, §5, §10).
- **ASM-0887** — sealed statistics + fresh-facts chronology: simultaneous
  sealed-side LCB95 > δ_sealed over the full F(B_k); common fresh-evidence
  snapshot + symmetric metered refresh; ≥2 mock sealed releases calibrate the
  shift band (§7.1, §7.3(f), §10 gate 8).
- **ASM-0888** — decon adjudication fail-closed: every flag adjudicated;
  unadjudicated = leakage; no sampling path (§6.2).
- **ASM-0889** — calibration corrections: common-index separation gate
  (diagnostic-not-ground-truth anchors), variance decomposition + powered
  replicates, saturation gate (§2.3, §10).
- **ASM-0890** — generic-RAG comparator equity: same evidence + budgets +
  pinned standard harness, BM25+dense cells, per-cell retriever decision —
  never a forced identical retriever (§8.2(iii)).
- **ASM-0891** — factorial attribution controls specified framework-side
  (§8.5), with the draft executor-axis cells.

Draft-1 rules that STAND unchanged under inherited ids (no new entry needed):
abstention scored incorrect with rates co-reported (§2.6); equal registered
weights + rung-tagged non-comparable scalars (§2.7); vector-unclamped/
scalar-clamped ceiling rule (§2.3, now with the ASM-0889 saturation guard);
LM-loss vector-only (§2.1); prompted-D4-with-adaptation-diagnostic (§2.4);
base-image default-DENY + engine-is-arm-bytes (§3.3); measurable-cell matrix
+ fail-closed MISSING energy cells + caching legality + warm/cold both-bind +
p99 ban (§4); the §9.6 δ machinery (2×SD_cal noise floor + maintainer
materiality floor).

### 12.3 What this draft deliberately does NOT do

It does not freeze anything; does not set δ_k/δ_sealed values; does not pin
dataset revisions, harness commits, or the base-image hash (freeze-time
objects); does not implement the generic-RAG control (the equity rules are
now pinned in §8.2(iii)/§8.5 from the landed P3-LR-RAG, but the executable
cells are P3-D-RAGC's); does not decide sealed-producer independence
(P3-D-SEAL + maintainer); does not run, grade, or audit anything; does not
launch any G4/W1 experiment or P3-E-CAL execution (review recommendation,
honoured); and does not claim any architecture is likely to win under it —
the framework is deliberately indifferent to who wins, including us
[STIPULATED].

---

## Epistemic register (what this draft relied on)

- **MEASURED (restated strictly within envelopes)**: l3a-parse 47.6% FAIL /
  a5-nl 41.6% FAIL + S2 fired; f2b-replicate +0.1507 alignment-confounded
  (does_not_license); coverage 0/1,550, 0/1,000, 0.3542 corpus-indexed; the
  local box has no GPU and no RAPL (SYS.md §0 direct inspection).
- **LIT-BACKED (via the five landed lit-reviews consumed here, each verified
  at source there)**: OLLv2 normalization; HELM structure + mean-win-rate
  rejection; metabench one-factor; contamination rephrase-evasion (Yang) +
  Oren logprob test; GSM1k corrected reading; LiveBench versioning;
  per-benchmark floors/ceilings table (EVAL.md §6); Snell adaptive test-time
  compute (conditional); MLPerf scenarios/statistics/caching incl. the
  SingleStream closed-loop/Server open-loop distinction (SYS.md §1/§5);
  MLPerf-Power boundary + TDP kill; NVML sampling hole; coordinated omission;
  Traeger warm/cold; Hoefler–Belli + Mytkowicz repeatability; Sardana
  inference-volume sizing + FLOPs≠$; storage price pins + five-minute rule;
  RAG source-snapshot-vs-retriever distinction + FlashRAG standardisation +
  BM25/recall-separation cells (RAG.md §3/§6); STORE three-sub-line store
  accounting + denominators-not-a-bracket + FreshQA refresh motivation
  (STORE.md §6–§8); PARSE S2-definition divergence + risk-coverage-curve
  conventions + shift-stress requirement (PARSE.md §4/§8).
- **STIPULATED**: every design choice in §§1–10, each tagged inline; the
  draft-2 corrections registered as ASM-0880…ASM-0891 (§12.2); the freeze
  conditions (§11).
- **EXTRAPOLATION (never premises)**: IRT suite compression as a future cost
  option (§2.7); the expectation that G1 binds early (§9.4 — a motivated
  expectation feeding schedule priority, deciding nothing).

This document changes no frozen object, no verdict, no audit, and no
results-log; this revision APPENDED the fresh assumption block
ASM-0880…ASM-0891 to `registry/assumptions.jsonl` (append-only) so its
corrections are citable premises, and touched nothing else in the registry.

---

## 13. Draft-2 change record (each change → the review point it answers)

| # | Review point (rev-dMF0-20260711) | Change | Where |
|---|---|---|---|
| 1 | Ranked 1: no coherent freeze/dependency owner | P3-D-FAIR integration/freeze bead blocked by ALL component designs; P3-D-INDEX scope narrowed | §0, §11, §12.1; ASM-0880 |
| 2 | Ranked 1: factorial controls mentioned, never specified | Full content×retrieval×executor cell inventory with discrimination claims, framework-owned | §8.5 (new); ASM-0891 |
| 3 | Ranked 2: "binding resource vector" does not bind W1 | Two-tier B_k: primary components + hard secondary ceilings over every measured component | §4.1, §8.1, T-C4; ASM-0881 |
| 4 | Ranked 2: energy dropped when unmeasurable contradicts parent W1 | Common-platform common-boundary energy rule; explicit ENERGY-EXCLUDED label otherwise | §8.1; ASM-0881 |
| 5 | Ranked 3: calibration compares scalars across rungs; size not known-answer | Common-index separation gate; same-family anchors as diagnostic, not ground truth | §10 gate 1; ASM-0889 |
| 6 | Ranked 3: sealed gate is a point estimate; comparator set unstated | Simultaneous sealed-side LCB95 > δ_sealed over the FULL pre-registered F(B_k) | §7.1; ASM-0887 |
| 7 | Open-loop/SingleStream contradiction | Closed-loop SingleStream kept with "service-time (closed-loop, unloaded)" label; open-loop for offered-load claims | §4.2–4.3, T-C5; ASM-0882 |
| 8 | Below-floor rule: wrong inferential direction | UCB95(s − chance) < Δ_disc minimum-discriminative-span criterion | §2.5; ASM-0883 |
| 9 | G1: clamping term, a_cov at zero coverage, census uncertainty, coverage false negatives, κ protocol + human cost | Headroom min-term; κ=0 rule; census-mode uncertainty; uncertain-counts-covered + measured labeller FN rate; adjudication protocol + hours frozen pre-kill | §9.4; ASM-0884 |
| 10 | Packing mixes deployment size with construction provenance | Figure (1) = as-built serving artifact; max() rule retired; construction → figure (5), co-reported | §3.1–3.2; ASM-0885 |
| 11 | Lifecycle schema cannot execute K-P3v2(6); predates STORE | kot-life/1-draft2: three store sub-lines, attrition, fixed/variable, record classes, refresh/reindex/rollback, fan-out, occupancy formulas, DEFINED amortisation/crossover, "dominated" = per-line Pareto | §5; ASM-0886 |
| 12 | Fresh-fact sealing chronology/oracle problem | Freeze-first + common fresh-evidence snapshot + symmetric metered refresh budget + cost co-registration; drop-the-leg fallback | §7.3(f); ASM-0887 |
| 13 | Decon gate can clear unreviewed flags | Every flag adjudicated; unadjudicated = leakage; sampling path deleted | §6.2; ASM-0888 |
| 14 | Resource admissibility ignores measurement uncertainty | UCB95-based F(B_k) membership, fail-closed near ceilings | §8.1; ASM-0881 |
| 15 | k ≥ 3 too weak; prompt-order not independent; sealed shift uncalibrated | Variance decomposition + powered replicate counts; prompt-order = sensitivity span; ≥2 mock sealed releases | §10 gates 3/8; ASM-0889/0887 |
| 16 | Reference-ceiling clamping can destroy W1 discrimination | Saturation guard + P3-E-CAL saturation gate; saturated cells reported non-discriminative | §2.3, §10 gate 7; ASM-0889 |
| 17 | Generic-RAG control under-specified / can handicap baseline | Equal evidence + budgets + pinned standard harness + BM25/dense cells; per-cell retriever decision | §8.2(iii); ASM-0890 |
| 18 | Consume landed RAG/STORE/PARSE | Consumed at §8.2(iii)/§8.5, §5/§7.3(f), §2.6; §11 updated | header, §11 |
| 19 | "~$0" unsupported once human costs counted | All "~$0" claims narrowed to compute; human hours logged to KOT-LIFE/1 | §0, §9.4, §10; ASM-0886 |
| 20 | Do not drive experiment beads; review-blocked draft | Status header: no G4/W1 or P3-E-CAL execution launches from this document | header, §12.3 |
