# P1 — Unified pre-registered hypothesis & experiment suite

**Status:** pre-registration draft for maintainer sign-off, 2026-07-08. Component P1 of the
operational research plan (`docs/research-plan/`). Governed by
`docs/kernel-design-directives.md`, which this document treats as binding: the kernel and its
axiom layer are **native** (NSM-derived, formal semantics on the kernel's own terms); RDF/OWL/
SHACL/DL appear below only as optional lossy exports or as comparison lenses, never as design
targets or validation references. Both value theses (correctness AND efficiency) are
operationalised; every uncertain design choice is a registered fork with a deciding experiment
and a kill criterion; every hypothesis carries a model-scale axis; thresholds and analyses are
fixed here, before any run, so no outcome can be reframed.
**Author:** Fable planning agent (P1), for @jeswr. Coordination: sparq-org/sparq#1683.
**Inputs integrated:** `docs/architecture.md` (encoder B, seams A1–A6), `docs/poc-design.md`
(E-series rev 2 + kill chain), `reports/lit-ontology-vector-priorart.md` (L1),
`reports/lit-primitives-grounding-priorart.md` (L2), `reports/lit-llm-injection-priorart.md`
(L3: interface-locality law, Laws 1–3, the mandatory kernel-as-text null),
`docs/design-constraint-layer.md` (kot-axiom/1 — with its SHACL-as-destination framing demoted
per the directives), `docs/explainer-vectorisation.md` (X-series quality card, seam status),
`docs/design-dl-from-nsm-and-lean-reconstruction.md` (native-formalism forks, here NF1–NF7),
`docs/design-efficiency-track.md` (M1–M6, F0 accounting standard, F1–F7, efficiency forks
EF1–EF5, scale ladder).

**Naming discipline (collision fix, binding for all later components).** Three prior documents
each use "F1–F7" for different things. This suite renames at the point of use and all later
plan components must follow:

| Old name | Source doc | Name here |
|---|---|---|
| Experiments F1–F7 | design-efficiency-track.md §4 | **F1–F7** (unchanged — they are experiments) |
| Design forks F1–F7 | design-dl-from-nsm-and-lean-reconstruction.md §7 | **NF1–NF7** (native-formalism forks) |
| Design forks 1–5 | design-efficiency-track.md §7 | **EF1–EF5** (efficiency forks) |
| kot-axiom/1 sidecar ("F1" in the task brief) | design-constraint-layer.md | **the axiom sidecar** |

**Evidence status glossary.** PASS/FAIL/NULL = real pre-registered run against the pinned
encoder `40e8c8ba…`; MOCK-only = harness exists and mock pipelines ran, no real-run verdict;
INCONCLUSIVE = real run, neither criterion nor TOST bound met. Prior verdicts treated as
evidence throughout: **X0/X1/X4 SUCCESS** (determinism; adversarial margins 11× floor;
projection to 512/576 at RDM Spearman ≈0.97), **X2 51/54** (decode gap named, tracked; no
decode-dependent claim on the Bq toy-native path), **X3 FAIL→ban** (cosine on kernel vectors
banned downstream; similarity is structural overlap, not meaning), **X1-grounding FAIL**
(NSM primes not graph-distinguished in WordNet Core — instrument-limited, does not gate),
**E2 PASS** (kernel RDM adds explanatory power beyond relatedness baselines, 3/3 families,
correlational), **E5 PASS** (adapter transfers kernel content to unseen nonce concepts,
+28.5 pp over shuffled, p<1e-6, 5/5 seeds, 135M), **E9-defl PASS** (structure-preserving
semantic scramble recovers only ~8% of E5's effect — the effect is content, not format),
**E8 PASS on 1 family pair + NOT-REPLICATED on the 3rd** (named site confound:
MLP-output vs residual-stream SAE), **E1 INCONCLUSIVE** (kernel-frozen ≯ shuffled at the
pre-registered look; TOST could not exclude the effect either; trained arms did not beat the
step-0 instrument baseline), **E4 MOCK-only** (no real-run verdict on zero-exposure emission;
the literature prior is a null).

**Common statistical rules (inherited, binding).** ≥5 paired seeds per trained condition;
paired permutation tests; one named primary endpoint per experiment; Holm-corrected
secondaries; a "null" verdict requires a TOST equivalence bound at the pre-registered smallest
effect of interest (default Cohen's d = 0.5) — non-significance alone is INCONCLUSIVE, not
null; encoder + corpus hash pinned per run; every positive gets independent adversarial audit
before "PASS" is written (run-from-audit separation, directives §3); negative results are
committed with full statistics at the same prominence as positives. **Proportion/rate
endpoints** (catch rates, precision, violation rates, location rates) are tested one-sided
against their pre-declared threshold at α=0.05 with the verdict read from the **Wilson 95%
CI bound** — the CI bound, not the point estimate, must clear the threshold; **count-based
fork criteria** (G6/G7) are deterministic counts over pinned corpora and carry no test.
**Slope claims** (HC5, HE7, HS13) fit weighted least squares on log-params rungs and report
the 90% CI on the slope; "shrinking" means the CI excludes 0 from below. Where a kill
criterion below names only a threshold, these defaults supply the test and alpha. Every efficiency-relevant
report carries the full metric vector **V = {accuracy/correctness (task + kernel-covered
slice), params (N_total/N_active/N_trained), memory (total-system peak ledger per F0 §3.4),
inference compute (FLOPs/query, p50/p95 latency, $/query), training compute (FLOPs/steps/
tokens-to-target)}** under the F0 accounting standard (`design-efficiency-track.md` §3),
including all kernel machinery (encoder, adapter, verifier, store, retrieval) — nothing waived.
Every verdict restates the M0b kernel-expressibility coverage number and its rung.

**Scale rungs (the mandatory scale axis).** Inference rungs: **R1** = SmolLM2-135M,
**R2** = 360M, **R3** = 1.7B, **R4** = Qwen2.5-3B (replication family), **R5** = 7B-class
(gate-kept). Training rungs: **T0** = 5–15M toy (E1 scale), **T1** = Pythia-70M config,
**T2** = 160M (smallest decisive rung for training-side claims), **T3** = 410M–1B (gate-kept).
**R0** = this box, CPU, no model. Slope discipline: ≥3 rungs before any scale adjective;
2 rungs license a sign; 1 rung licenses nothing.

---

## 1. H0 — the top hypothesis and the go/no-go gate

**H0 (falsifiable statement).** *The kernel principle — deterministic, content-addressed,
training-free concept definitions plus their machinery (encoder, verifier, axiom sidecar,
store, adapter) — measurably improves an LLM system on at least one value thesis (correctness
or efficiency), on kernel-covered task slices, beyond BOTH (i) the kernel-as-text null (the
same definitional content, hash-pinned, rendered as Minimal-English text) and (ii) the
strongest industrial baseline for that thesis (RAG-over-text for knowledge; matched-compute
sampling, quantization, distillation, and smaller-model-alone for efficiency), at two or more
model-scale rungs.*

H0 is deliberately a **disjunction over mechanism-level hypotheses**, because the directives'
first question ("is the kernel principle useful to LLMs at all?") is answered by any one
mechanism surviving its strong baselines — and is answered negatively only when the
best-supported mechanisms are all TOST-killed against the text null. The literature (L3 Laws
1–3) predicts exactly where the disjunction is most likely to go through: verifier-side
(symbol-side) mechanisms, not injection (consumer-side) mechanisms. The suite is ordered so
the cheapest experiments discriminate along that line first.

**Decisive YES (pre-declared evidence pattern).** At least one of {HC1, HC2, HE1, HE2, HE3,
HE4, HE5, HE6} reaches PASS under its own kill criterion, **including** beating its
kernel-as-text arm, at ≥2 rungs of its ladder, with the positive surviving independent
adversarial audit (re-run from pinned artifacts by a non-running agent; audit checklist in
plan component P4). A YES licenses only the surviving mechanism at its measured rungs and
coverage — never the strong A1 claim, which has its own gated test (HS13).

**Decisive NO (pre-declared evidence pattern).** ALL of the following, each as a TOST-bounded
null or explicit kill: (a) F2 kills HE1 and HE2 at both (R1,R2) and (R2,R3) pairs; (b) E9-full
kills HC1 AND the constraint arm HC2; (c) F4 kills HE4 (in-context text matches the adapter
path); (d) F6 toy rung kills HE6 (or the text-scaffold arm matches it). Under this pattern the
kernel's measured value to LLMs is nil beyond its own text rendering, and the global tree (§6)
routes to *pivot* (if HC4/E8-R lives) or *kill* (if it does not). Cost to reach a decisive NO:
≈ **$180–650** (§5), plus the ~$0 R0 tier.

**What H0 cannot be resolved by:** any single-rung result; any result on a non-covered slice;
any arm that was tuned harder than its baselines; any positive not audited independently.

---

## 2. Correctness hypotheses (HC series — the endorsed primary track)

The surviving form of the maintainer's original claim (architecture.md §2): misunderstanding
made *detectable and correctable at the interface* — the kernel as external verifier and
instrument, the A5/A6 seams, the Law-3 topology (neural proposer + deterministic engine owns
correctness). Prior evidence in favour: E5/E9-defl (content transfers through the adapter
instrument), E2 (designed geometry detectably aligned with learned geometry), the
AlphaGeometry/Logic-LM template. Prior evidence against: nothing yet measures the verifier's
*end-task* benefit — that is exactly what this track buys.

### HC1 — Decode-verify beats RAG-with-citations and its own text deflation on error-catching

- **Statement.** On a factual/definitional-consistency task over kernel-covered content, the
  kernel decode-verify loop catches model errors that (i) vanilla RAG-with-citations and
  (ii) a hash-pinned definition-TEXT dictionary (the deflationary null — no encoder, no
  structured records) do not catch, at a measured marginal cost.
- **Decisive experiment: E9-full** (pre-registered in poc-design E9 rev 3; not yet run).
  Arms: (1) model alone; (2) model + RAG-with-citations over gloss corpus; (3) model +
  hash-pinned gloss-file dictionary lookup (deflation); (4) model + kernel decode-verify
  (decode concept-level output → check against canonical record; X2's 51/54 machinery, its
  gap on the ledger); (5) arm 4 + repair/retry. Scoring by non-LLM rubric or leak-checked
  judge (E5 discipline).
- **IVs:** verification architecture (arms); model rung; retry budget. **DVs:** error-catch
  recall/precision by error class; end-task accuracy after repair; full vector V (verifier
  FLOPs counted per F0 §3.3 — NN cleanup ≈ |lexicon|·D MACs, on the ledger).
- **Baselines:** arms 2 and 3 are both mandatory; arm 3 is the kernel-as-text null in its
  strongest form.
- **Kill criterion.** HC1 is dead at a rung if arm 4/5's error-catch set is ≥90% covered by
  arm 3's at ≤ arm 3's cost, or if end-task accuracy after repair does not exceed arm 3's by
  the pre-registered smallest effect of interest (Cohen's h = 0.2 on the per-item
  caught/corrected rate; paired bootstrap over items, α=0.05; a null verdict requires TOST
  with equivalence margin h = 0.2). Ships with the per-class breakdown: any HC1 PASS must
  name the error classes only structure catches.
- **Scale rungs:** R1, R2; R3 if a sign exists. **Cost:** ~$20–80 (inference-only, Modal
  harness reuse).

### HC2 — The axiom sidecar catches what no text arm can (the constraint-violation delta)

- **Statement.** Deterministic checking against the endorsed axiom sidecar (native closed
  axiom grammar; e.g. the litmus "a human has exactly two parents, one male, one female")
  detects planted consistency violations in model-asserted instance records that gloss-text
  and RAG arms structurally cannot ("a gloss file cannot count parents" —
  design-constraint-layer §5.2).
- **Decisive experiment: E9-C** (new arm inside E9-full). Build a seeded instance-record
  corpus (≥300 records) with planted cardinality/disjointness/domain violations at known
  rates over the litmus family (human/parent/sex, bookmark/maker, promise/parties) +
  molecule-tier axioms; the model asserts/summarises records; each verification arm flags.
- **IVs:** verification arm; violation class; model rung. **DVs:** end-to-end catch rate
  (through the decode step — the X2 gap is part of the system under test), false-positive
  rate on clean records, cost per check.
- **Baselines:** all E9-full arms; plus a text-diff checker over the gloss file (EF4's
  question folded in: can plain text verification match structural verification?).
- **Kill criterion.** Dead if end-to-end catch rate < 0.80 (one-sided exact binomial vs the
  0.80 threshold, α=0.05: the Wilson 95% lower bound over ≥300 planted violations must clear
  0.80), or < 3× the best text arm's catch rate (paired bootstrap on the per-record catch
  indicator, α=0.05), or false-positive rate on clean records > 2% (Wilson upper bound must
  sit below 2%). (The checker itself is deterministic;
  what is genuinely at risk is the decode step and the authoring of checkable axioms — a
  fail here indicts the pipeline, and the verdict must say which stage failed.)
- **Scale rungs:** R1, R2. **Cost:** inside E9-full's budget (+~$10). **Dependency:** NF2's
  axiom-syntax fork need not be resolved first — v0 kot-axiom sidecar suffices; if NF2 later
  selects the NSM-native syntax, HC2 is re-run cheaply as a regression, not re-registered.

### HC3 — Deterministic kernel verifier vs trained PRM (fork EF3, promoted to hypothesis)

- **Statement.** On kernel-covered content, the training-free kernel verifier provides
  routing/accept-reject signal at least as good as a small trained process-reward model at
  strictly lower total cost (no training, no per-token forward).
- **Decisive experiment: F2+PRM** — add an off-the-shelf small reward-model arm to F2 at
  matched inference FLOPs (design-efficiency-track EF3).
- **IVs:** verifier type (kernel-deterministic vs trained PRM vs logprob threshold). **DVs:**
  accuracy-vs-expected-FLOPs frontier; verifier precision/recall on kernel-covered errors;
  full V.
- **Kill criterion.** If the generic PRM matches the kernel verifier on kernel-covered
  content at matched FLOPs, the kernel's verification contribution collapses into commodity
  verification; determinism/provenance revert to governance claims and HC3 (and M1/M5's
  kernel-specificity) is dead. Numeric: the kernel-verifier arm must beat the PRM arm's
  frontier point on kernel-covered accuracy at matched FLOPs (paired bootstrap over items,
  α=0.05, minimum effect h = 0.2); "PRM parity" asserted as a positive finding requires TOST
  at the same margin, else the fork stays INCONCLUSIVE and buys one replication before verdict.
- **Scale rungs:** R1→R2 pair; R2→R3 replication. **Cost:** +~$10–20 on F2.

### HC4 — Kernel as canonical label/coordinate space for learned features (A6/E8)

- **Statement.** Kernel geometry predicts cross-model SAE feature correspondence beyond
  shuffled-kernel and permutation nulls on the seed-stable feature subset, in site-matched
  dictionaries, in ≥2 of 3 family pairs — and the instrument beats a simple baseline on a
  downstream task (the GDM acceptance test).
- **Prior evidence:** E8 PASS on GPT-2↔Pythia-160M (ρ≈0.39, p=1e-4, secondaries survive
  Holm); NOT-REPLICATED on SmolLM2-135M with a named conservative-direction confound
  (MLP-output-site vs residual-stream SAE). L3 §5: target must be the seed-stable subset
  (~30% per Paulo–Belrose); nulls must include cross-seed correspondence without the kernel;
  differentiate from Hyperdimensional Probe (arXiv:2509.25045) in any writeup.
- **Decisive experiments: E8-R** (site-matched residual-stream SAE on a third family;
  replication is the sole primary endpoint) then **E8-D** (downstream: cross-version semantic
  regression detection — did concept c's operational meaning move between model/kernel
  versions? — must beat a linear-probe baseline, AUC, pre-registered margin).
- **IVs:** family pair; SAE site (controlled); seed-stability stratum. **DVs:** correspondence
  ρ vs both nulls; E8-D AUC vs probe baseline.
- **Kill criterion.** E8-R dead if the site-matched third family fails both new pairs
  (permutation test vs shuffled-kernel null, p≥0.01 per pair, effect reported as Spearman ρ
  with bootstrap 95% CI); A6 then has one unreplicated pass and is shelved, not pitched.
  E8-D dead if the instrument fails to beat the linear probe by ΔAUC ≥ 0.05 (DeLong test,
  α=0.05) — then A6 is "alignment above chance, no downstream use" (decoration, per GDM's
  bar).
- **Scale rungs:** model families at 125M–160M class first; one ≥1B family pair if E8-R
  passes. **Cost:** ~$30–120 (SAE fitting dominates).

### HC5 — Verifier benefit does not vanish with scale (the correctness scale-slope)

- **Statement.** The end-task correctness lift from kernel verification (HC1/HC2 winners)
  is non-vanishing as host scale grows — Law 2 predicts the *text* arms improve with scale;
  the verifier's lift must not be a small-model artifact.
- **Decisive experiment:** the surviving HC1/HC2 arms re-measured at R3 and R4 (folded into
  F7's slope machinery; same budget gate).
- **Kill criterion.** If the verifier's marginal catch/lift shrinks across R1→R3/R4 (WLS
  slope on log-params, 90% CI excluding 0 from below) and the fitted trend extrapolates below
  practical significance (default <10% relative error-reduction) at R5, the correctness pitch
  is declared **toy-only** — honest for the prospectus, dead for a frontier pitch.
  **Scale rungs:** R1–R4. **Cost:** inside the F7 gate.

---

## 3. Efficiency hypotheses (HE series — mechanisms M1–M6)

All inherit F0 (accounting standard), the five mandatory baselines where applicable
(RAG-over-text, distillation, quantization/pruning, smaller-model-alone, kernel-as-text null),
Pareto-hull reporting ("wins" = a point strictly outside the convex hull of ALL baseline
points), and the dual iso-accuracy/iso-compute discipline (strong claim = wins under both).
Pre-registered prior (design-efficiency-track §1.4): M1/M5/M6 most likely to survive;
M2-output and M3-at-scale least likely — the ordering below spends money accordingly.

### HE1 — Verifier-offload buys parameters (M1)

- **Statement.** ∃ kernel-covered, correctness-sensitive task family and scales s<S such that
  model_s + kernel-verifier ≥ model_S alone on accuracy at strictly lower total inference
  FLOPs, $ and memory.
- **Decisive experiment: F2** (design-efficiency-track §4.2, adopted verbatim): 9 arms at
  (135M, 360M, 1.7B) incl. kernel-as-text (arm 5), RAG-over-text (arm 6), FLOP-matched
  self-consistency-N (arm 7), int4-quantized 360M (arm 9); retry sweep k∈{1,2,4}.
- **Primary endpoint:** kernel-covered-slice accuracy of 135M+verifier vs 360M alone,
  iso-accuracy discipline, paired bootstrap α=0.05, full V.
- **Kill criterion (verbatim from the track):** dead at a rung if (a) <50% of the s→S gap
  closed at best pre-registered retry budget, OR (b) the text null or matched-compute
  sampling closes as much gap at ≤ the same FLOPs/query, OR (c) closing the gap costs ≥
  running model_S directly. Nulls require TOST.
- **Scale rungs:** (R1,R2) then (R2,R3); pre-registered question: does the closable gap
  fraction grow or shrink with S? **Cost:** ~$10–40. **This is the single cheapest
  kill-or-support of the efficiency thesis proper.**

### HE2 — Verifier-gated cascade beats logprob-gated cascade (M5)

- **Statement.** A kernel-verifier-gated small→large cascade strictly dominates a
  logprob-threshold-gated cascade (matched escalation budget) on the accuracy-vs-expected-
  FLOPs frontier on kernel-covered tasks.
- **Decisive experiment: F2b** (arm 8 of F2); expected cost = c_small + p_escalate·c_large +
  c_verify with p measured, not assumed. EF5 (post-hoc retry vs in-decode gating) rides
  along: one in-decode gating arm, latency measured batch-1 and throughput modes.
- **Kill criterion.** Dead if not strictly dominant over the logprob gate — dominance means
  the verifier-gated frontier point is above the logprob-gated one at every pre-registered
  escalation budget (per-budget paired bootstrap, Holm-corrected across budgets, α=0.05);
  any budget where the logprob gate wins breaks dominance. EF5 has no kill —
  it only picks the surviving implementation. **Scale rungs:** (R1→R3) cascade; replication
  (R2→R3). **Cost:** inside F2.

### HE3 — Dense concept input cuts prompt FLOPs/KV at matched accuracy (M2-input)

- **Statement.** In the long-glossary regime (d∈{4,16,64} in-context definitions), kernel
  vectors through the E5 adapter (1 soft token/concept) reach the accuracy of full-text
  definitions at ≤1/2 the prompt FLOPs and KV bytes, and are not matched by (a) matched-token
  compressed/truncated text or (b) an xRAG-style trained compressor at the same training
  budget.
- **Decisive experiment: F3** (7 arms, adopted verbatim; JL-projected path, X4 distortion
  reported; shuffled-kernel arm inherited from E5 discipline).
- **Kill criterion.** Dead at a rung if the vector arm fails to beat BOTH matched-budget text
  arms at d≥16, or if the trained compressor matches it (then dense injection works but
  canonical training-free adds nothing to efficiency — residual claim moves to governance),
  or if amortized adapter cost exceeds per-query savings at Q=10⁶.
- **M2-output rider (pre-declared expected-fail):** loss-vs-compute slope for next-concept
  prediction into frozen kernel space vs next-token (E3 task and guards; the LCM-shaped
  cell). Budget ≤$20; kill expected per LCM/SONAR-LLM; a surprise survival re-opens at the
  next rung only.
- **Scale rungs:** R1→R2→R3 (Law-2 prediction: the win shrinks as hosts improve at text —
  measure the slope). **Cost:** ~$50–170.

### HE4 — Amortized concept-vocabulary onboarding beats LoRA and in-context text (M6)

- **Statement.** For a new terminology domain (≥50 held-out concepts), frozen kernel vectors
  + the already-trained adapter reach ≥90% of LoRA-finetune accuracy at ≤10% of its
  adaptation FLOPs, and beat in-context text definitions at matched inference cost.
- **Decisive experiment: F4** (5 arms incl. ToolkenGPT-protocol per-concept trained
  embeddings and the in-context-text null "most likely to win").
- **Kill criterion.** Dead if the adapter arm is <90% of LoRA accuracy at every rung
  (per-rung paired permutation over ≥5 seeds, α=0.05, Holm across rungs), or if in-context
  text ≥ adapter arm at matched inference FLOPs/query (text-parity as a kill requires the
  text arm's Wilson lower bound ≥ the adapter arm's point estimate, or TOST equivalence at
  d = 0.5), or if ToolkenGPT-style per-concept trained embeddings match the adapter arm at
  comparable all-in cost with their per-concept training FLOPs included on the ledger (then
  a trained identifier does the job and the kernel content is unnecessary).
- **Prior evidence:** E5 PASS + E9-defl PASS make this the programme's only injection cell
  with a measured kernel-content win — F4 adds the cost accounting and the missing text null.
- **Scale rungs:** R1/R2/R3; pre-registered: does the text null overtake vector injection as
  host scale grows? **Cost:** ~$20–60.

### HE5 — Content-addressed store offloads memory/params (M4)

- **Statement (two-stage).** (Byte premise) KOTK/2 beats the best general-purpose-compressed
  text store of the same records by ≥2× bytes at ≤2× retrieval latency. (Full claim)
  small-model + kernel-store retrieval sits strictly outside the accuracy-vs-total-system-
  bytes Pareto hull of {larger model, int4-quantized larger model, byte-matched text-RAG,
  distilled smaller model}.
- **Decisive experiments: F1** (byte/latency accounting, R0, ~$0 — measured priors: 2.90
  B/rec wn31 vs 9.58 B/rec zstd-JCS text ≈ 3.3×; glosses-only text still to be measured)
  then **F5** (the accuracy leg; Pythia-style controlled training; injection route fixed by
  F3's winner).
- **Kill criteria.** F1: byte claim dropped if <2× vs compressed gloss text (M4 then
  proceeds, if at all, on verifiability alone — which is HC2's territory, not an efficiency
  claim). F5: M4-kernel dead if the kernel-store arm fails to leave the hull of
  {byte-matched text-RAG, quantized, distilled}; beating only "no store" re-establishes
  Atlas/RETRO and is reported as not-ours.
- **Scale rungs:** store scale 10³→10⁵→10⁶ (F1); training rungs T1/T2, T3 only if T2
  positive (F5). **Cost:** F1 ~$0; F5 ~$200–800 (gated on F1 pass + F3 settled).

### HE6 — Kernel scaffolding cuts training tokens-to-target (M3)

- **Statement.** On a concept-heavy distribution, kernel-scaffolded training (frozen
  content-bearing rows) reaches the target-accuracy checkpoint at ≤0.8× the baseline
  token/FLOP budget, and is not matched by the explication-text-interleaved data arm (else
  the win is curriculum, not architecture).
- **Decisive experiment: F6** (E1's design + the text-scaffold arm the lit review demanded;
  5 paired seeds; E1 single-look rule carries over). Absorption is NOT a kill (InstructRetro
  logic: scaffolding absorbed still saved the steps); post-training apparatus-removal is run
  descriptively and feeds fork HS9.
- **Prior evidence:** E1 INCONCLUSIVE at T0 — neither a pass nor a TOST null; the instrument
  itself (cloze vs step-0 baseline) underperformed. F6's toy rung therefore first repairs the
  instrument (pre-registered instrument check: trained arms must beat step-0 before any
  between-arm comparison is read).
- **Kill criterion.** M3-vector dead if the ≤0.8× bound fails (TOST) vs trainable, or if the
  text-data arm matches the vector arm (text-arm survival alone is filed as M3-data — a data
  result, not an architecture result). **T2 (160M) is the smallest decisive rung** — frozen-
  embedding convergence penalties are documented ≥100M; toy wins gate spending, decide
  nothing.
- **Scale rungs:** T0→T1→T2 (merges into E7's ladder; one budget sign-off). **Cost:**
  ~$50–150 toy; T2 inside the E7/F7 gate.

### HE7 — Surviving efficiency deltas do not shrink to irrelevance with scale (F7)

- **Statement.** For every mechanism alive after F1–F6: Δ(cost saved at iso-accuracy) is
  flat or growing across ≥3 rungs.
- **Decisive experiment: F7** (merged with E7; ~$2–10k; maintainer budget gate).
- **Kill criterion.** A mechanism whose Δ shrinks across three rungs (WLS slope on
  log-params per common rules, 90% CI excluding 0 from below) and whose fitted trend
  extrapolates below 10% cost-saving at 7B is **toy-only**: kept for the prospectus,
  excluded from any frontier pitch. Flat-or-growing requires the slope CI to exclude
  material shrinkage (lower bound > −10%/decade of params). **Scale rungs:** R1–R4/R5
  inference; T0/T2/T3 training.

---

## 4. Structure / design-fork hypotheses (HS series)

The directives' second question: *if the kernel helps, which kernel structure is most
useful?* Forks are first-class hypotheses; no option is defended, each is decided by its
experiment. R0 forks are near-free and front-loaded.

### HS1 — NSM-semantic pinning beats any fixed random codebook (the L1 literature fork)

- **Statement.** The kernel's measured downstream effects require the NSM-derived semantic
  content of the codebook/explications — not merely a consistent fixed structured code — and
  are not matched by statistical concept vectors.
- **Prior evidence (partially decided at one rung/one model):** E9-defl — structure-preserved
  semantic scramble recovers only 8.2% of the E5 effect. That answers "content vs format" at
  R1 in one family.
- **Decisive experiment: G1** — extend F4 with three arms dictated by L1 §10: (a)
  random-atom-codebook encoder variant (same grammar and structure algebra, atoms assigned
  fresh random orthonormal rows — the Wieting-Kiela null confronted head-on); (b) Numberbatch
  vectors through the same adapter protocol (statistical concept vectors); (c) a KGE/OWL2Vec*-
  style embedding over the same concept graph (statistical relational; comparison lens only,
  not a design reference). Second model family mandatory.
- **Kill criterion.** If arm (b) matches true-kernel on the F4 primary endpoint, the
  "designed deterministic content" performance claim is dead — surviving value narrows to
  determinism/versioning/verifiability (governance), and every later doc must say so. If
  arm (a) matches, X-series structure is doing the work and NSM pinning is decoration.
- **Rungs:** R1 + R2, two families. **Cost:** +~$20–40 on F4.

### HS2 — Native axiom read-out (Π) vs authored-sidecar-only (NF1; "read-out-DL vs bolt-on")

- **Statement.** A deterministic projector Π over explication structure yields sound axiom
  read-outs (native form; any OWL rendering is an optional lossy export, never the reference)
  with subsumption precision ≥0.9 against a human gold set.
- **Decisive experiment: G2 = NF1's experiment** — implement Π over kernel-v0 (54 records) +
  gist walkthroughs; score derived subsumptions vs human gold; check Π recovers
  `promise ⊑ words` and cannot recover the partition-side axioms (confirming the
  read-out/residue split).
- **Kill criterion.** Precision <0.9 ⇒ Π demoted to lint; all axioms live in the authored
  sidecar (option b). Test: one-sided exact binomial vs the 0.9 threshold over ≥100 scored
  derived subsumptions, α=0.05 — the Wilson 95% lower bound must clear 0.9; inter-annotator
  agreement (Cohen's κ) reported, disagreements adjudicated blind before scoring. Additional
  kill for Π-as-normative if Π conflicts with any endorsed sidecar axiom on v0 (deterministic
  check, no test). **Rungs:** R0. **Cost:** ~$0 (agent + annotator time).

### HS3 — The semantics pin: necessary-conditions vs equivalence vs defeasible-script (NF7)

- **Statement.** The stipulated reading "explication = necessary conditions" (C ⊑ Π(C))
  survives contact with instances (≤10% necessity violations); the stronger equivalence
  reading survives only if sufficiency violations ≤10%.
- **Decisive experiment: G3 = NF7's annotation study** — ~20 concepts × ~10 instance
  descriptions, independent annotators judge necessity and sufficiency violations.
- **Kill criterion.** Necessity failures >10% ⇒ defeasible-script stands, Π is lint, and HS2
  auto-resolves to sidecar-only. Sufficiency failures >10% ⇒ equivalence dead, necessary-
  conditions only. Test: each rate against its 10% threshold by exact binomial with Wilson
  95% bounds over the full judgment set (~200 instance judgments: powered ≥0.9 to
  distinguish a true 10% from a true 20% rate at α=0.05); a "survives" verdict requires the
  Wilson upper bound ≤10%, a kill requires the lower bound >10%, anything between is
  INCONCLUSIVE and buys more annotations, not a verdict. Inter-annotator κ reported.
  **Rungs:** R0. **Cost:** ~$0 + annotator hours. **Upstream of HS2's interpretation; run
  first or concurrently.**

### HS4 — Axiom authoring surface: NSM-native AxiomSchema vs kot-axiom/1 vs both (NF2)

- **Statement.** The NSM-native axiom syntax (one grammar, profile-1L pins) is authorable at
  ≤2× the effort of the kot-axiom/1 sidecar without unresolved semantic disputes, and is not
  systematically mistranslated by the decode-legibility probe.
- **Decisive experiment: G4 = NF2's experiment** — same 20-axiom set (litmus + kinship +
  disjointness batch) authored in both syntaxes by two independent authors each; measure
  authoring error rate, record size, LLM decode-legibility.
- **Kill criterion.** As NF2: kill NSM-native if >2× effort or unresolved pin disputes; kill
  sidecar-only if its axioms are systematically mistranslated while NSM-native's are not.
  **Rungs:** R0. **Cost:** ~$0. **Depends on:** HS2's residue list.

### HS5 — Constraints stay out of the vector (NF4; near-decided)

- **Statement.** Folding projected-axiom content into v(c) worsens single-edit margins and
  adds no RDM signal — verifier-not-in-the-vector is correct.
- **Prior evidence:** X3's NOT-invisibility plus the stratum argument near-decide this.
- **Decisive experiment: G5 = NF4's encode-twice comparison** (X1-style margins on axiom
  edits + E2-style RDM delta). Run only if HS2 lands on Π-as-projection/normative.
- **Kill criterion.** Confirmation closes the fork; a surprise (axiom block improves margins
  AND adds RDM signal) re-opens with a new pre-registration. **Rungs:** R0. **Cost:** ~$0.

### HS6 / HS7 — Grammar capacity forks: AND-under-operator (NF5); apply-clauses (NF6)

- **Statements.** (HS6) <20% of the working axiom set needs AND-under-operator and all such
  are sidecar-expressible ⇒ the native fragment stays ∃-conjunctive-only. (HS7) inlining
  relational content forces cap violations or >1.5× clause growth on >10% of records at bulk
  scale ⇒ apply-clauses (kot-ast/2) win; else defer.
- **Decisive experiments: G6/G7** — static counts over kernel-v0 + molecules-v0 + the G4
  axiom set; bulk-scale projection. **Kill criteria:** the numeric bounds above (from NF5/
  NF6, verbatim). **Rungs:** R0. **Cost:** ~$0. **Depend on:** G4's axiom set.

### HS8 — Lean-derived facts minted vs Metamath-only identity (NF3)

- **Statement.** In-fragment Lean statements can be minted through the verified bridge F at
  useful rates (fragment-gate ≥1% of random Mathlib declarations; verified LLM location
  ≥80% top-5 on the easy set; round-trip fixed-point holds).
- **Decisive experiment: G8 = NF3's measurement** (1,000-declaration Mathlib sample;
  location rate on math-v0 overlaps; round-trip rate).
- **Kill criterion.** As NF3: below either bound ⇒ Metamath-only identity stands, Lean stays
  annotation-only; near-zero F-verification of LLM candidates kills the bridge programme.
  Tests: fragment rate vs the 1% gate by exact binomial over the 1,000-declaration sample
  (Wilson lower bound must clear 1%); top-5 location rate vs the 80% gate likewise (α=0.05,
  one-sided). **Rungs:** R0 (+ one crawl). **Cost:** ~$0–10. Independent; schedule
  opportunistically.

### HS9 — External-store (runtime dependency) vs in-weights (scaffold-then-absorb) (EF2)

- **Statement.** At realistic query volumes, keeping knowledge in the kernel store (M4)
  dominates scaffold-then-absorb (M3) on total lifecycle FLOPs (training + Q·inference,
  Q swept 10⁴–10⁸), or vice versa — the crossover is measured, not asserted.
- **Decisive experiment:** F5-arm-2 vs F6-arm-1 at T2, matched lifecycle FLOPs (F0
  amortization machinery). **Kill criterion.** Store dies if scaffold-then-discard dominates
  at all realistic Q; scaffold dies on F6's TOST. **Rungs:** T2. **Cost:** inside F5/F6.

### HS10 — Dense-concept-I/O vs verifier-keeps-token-I/O (EF1)

- **Statement.** The kernel's efficiency value concentrates at the interface (verify/route/
  cascade) rather than in dense input injection — or the reverse.
- **Decisive experiment:** F3 vs F2 on the same task family and budget; frontiers directly
  comparable under F0 §3.2. **Kill criterion.** If F3's vector arm is dominated by F2's
  cascade at matched accuracy, dense I/O is dropped from the efficiency track (latency-only
  survival must be measured, not presumed). **Rungs:** R1–R3. **Cost:** none extra.

### HS11 — Kernel-structured store vs hash-pinned text store (EF4)

- **Statement.** The structured store earns its place only through verifier consumption:
  byte-matched text-RAG plus a text-diff checker fails to match {retrieval accuracy,
  violation catching} of KOTK/2 + structural verifier.
- **Decisive experiments:** F5 arms 2 vs 3 (byte-matched) + the E9-C text-diff-checker arm.
  **Kill criterion.** Text-store parity on both ⇒ the kernel's storage contribution is a
  compression format, not an architecture; KOTK/2 kept as engineering, M4 architectural
  claim retired. **Rungs:** T2 + R1/R2. **Cost:** inside F5/E9.

### HS12 — Verification placement: post-hoc retry vs in-decode gating (EF5)

- As HE2's rider; no kill (implementation-selection fork); latency measured in both
  deployment modes decides. **Rungs:** R1–R3. **Cost:** inside F2.

### HS13 — A1 frozen-vocabulary at scale (the gated remnant of the strong claim)

- **Statement.** The kernel-frozen-vocabulary advantage (if any) is non-decreasing with
  scale (T0→T2→T3, matched tokens, ≥10³ concepts).
- **Prior evidence:** E1 INCONCLUSIVE; E4 MOCK-only (no real verdict; literature prior is a
  null); the frozen-glyph result and Law-1/-2 both predict the null; A1 labelled "not
  supported so far" in the seam status. **This hypothesis cannot gate anything** and is run
  (as E7) only if (a) F6's toy/T1 rungs show a real vector-arm signal AND (b) the maintainer
  signs off the E7 budget. A null here is expected and closes A1; a positive would be the
  single most surprising result in the programme and triggers immediate independent
  replication before any claim.
- **Decisive experiment: E7.** **Kill criterion:** advantage shrinking across all three
  rungs, or absent at T2 (TOST) ⇒ A1 closed at scale. **Cost:** $2–10k (shared with F7).

### HS-A — Authoring capability gate (the "why now" check, L1 implication 2)

- **Statement.** Fable-class authoring inside the validator loop decisively beats DeepNSM-8B
  on legality/substitutability/cross-translatability (Baartmans et al. metrics, reused
  as-is); the programme's authoring premise holds.
- **Decisive experiment: G9** — score N≥50 machine-authored explications with the validator
  + blinded human review against DeepNSM's published numbers (~24/100 self-metric).
- **Kill criterion.** Not decisively better than DeepNSM-8B ⇒ the "why-now" argument is
  weakened materially and the prospectus must say so; kernel authoring cost estimates revert
  to human-authoring rates in every plan document. "Decisively better" is pre-defined: the
  Wilson 95% lower bound of our composite validator-pass score (N≥50 explications) must
  exceed DeepNSM-8B's published point estimate by ≥10 points on the same metric definitions
  (published CIs unavailable, so the margin substitutes for CI overlap; α=0.05 one-sided).
  **Rungs:** authoring-model axis, not host axis. **Cost:** ~$0–20 (API + annotator).

---

## 4b. Extrapolation envelopes (directives §6 — binding on every verdict)

Every registry verdict must quote its row from this table verbatim; no report may state or
imply validity outside its envelope without the named caveat. Rules: **≥3 measured rungs**
before any scale adjective; a fitted WLS trend (90% CI) licenses extrapolation **at most one
order of magnitude** beyond the top measured rung, stated as direction-only unless the CI is
tight — the same discipline published scaling-law work applies (Kaplan et al. 2020;
Hoffmann et al. 2022 showed even 1–2-OOM extrapolations of a fitted law can mispredict,
which is the cautionary anchor here). Where the literature predicts the **direction of bias**
at larger scale, the envelope states it.

| ID | Measured range | Reasonable extrapolation envelope | Literature anchor + licensing assumption |
|---|---|---|---|
| H0 | 135M–1.7B (+3B repl.) | Verdict valid 135M–7B-class only; nothing at frontier without Tier 5 | No published scaling law covers kernel-type interventions; disjunction inherits the tightest surviving member's envelope |
| HC1 | 135M–360M (R3 if sign) | ≤3B, direction-only; bias stated: hosts' raw error rates fall with scale (loss scaling, Kaplan/Hoffmann), so absolute catch counts shrink; the *relative* catch on kernel-covered slices is the quantity extrapolated | Law 2 (L3): text arms improve with scale — verifier lift must be re-measured, never assumed, above 3B (that is HC5's job) |
| HC2 | 135M–360M | Checker soundness is model-free (deterministic) and extrapolates without limit; the END-TO-END rate is bottlenecked by decode fidelity, extrapolation ≤3B; larger hosts likely *improve* decode legibility (favourable direction, unmeasured) | AlphaGeometry/Logic-LM template (Law 3): deterministic-engine correctness is scale-invariant; only the neural translation step scales |
| HC3 | 135M–1.7B | Relative kernel-vs-PRM verdict extrapolates to ~7B ONLY under the stated assumption that the PRM is held at its measured size; a frontier-scale PRM re-opens the fork | PRM literature (process supervision) improves with PRM scale; verdict is indexed to the PRM size class tested |
| HC4 | 125M–160M families (+1 ≥1B pair if E8-R passes) | Open-weights families ≤7B; qualitative only above that | SAE feature-stability results (Templeton 2024, Paulo–Belrose seed-stability) span to mid-size production models; quantitative ρ does not transfer across SAE training regimes |
| HC5 | R1–R4 (135M–3B) | Fitted slope + 90% CI quoted to 7B (R5); beyond 7B direction-only with the no-published-verifier-lift-law caveat | This IS the extrapolation instrument for the correctness track |
| HE1 | (135M,360M),(360M,1.7B) | 3 rungs ⇒ gap-closure-fraction trend to 7B, direction-only; bias stated: the s→S gap itself narrows as S grows | Cascade/verification-routing literature measured to GPT-4-class (FrugalGPT-style) licenses mechanism existence, not effect size, above 7B |
| HE2 | 135M→1.7B cascade | Same as HE1; the cascade topology is standard at frontier scale, only the kernel gate's marginal value needs re-measurement | Same anchors as HE1 |
| HE3 | 135M–1.7B | ≤1.7B firm; to 7B direction-only with the pre-registered expectation of shrinkage; NO extrapolation of a win beyond 7B under any fit | Law 2 + xRAG fidelity ceiling + LCM/CALM scaling penalty: every anchor predicts the dense-input win decays with host scale |
| HE4 | 135M–1.7B | Mechanism existence to 13–33B (ToolkenGPT measured there); effect size and the text-null comparison ≤1.7B, direction to 7B only via the F7 slice | ToolkenGPT (LLaMA-13/33B) anchors the mechanism; the text-null overtaking prediction (Law 2) is the declared bias direction |
| HE5 | Store 10³–10⁶ records (model-free); accuracy leg 70M–160M | Byte claim: store-size axis extrapolates freely (measured B/rec is size-independent); accuracy leg ≤410M without T3; direction to 7B via RETRO's published range | RETRO measured 150M–7B with benefit retained (and InstructRetro absorption caveat); that published trend is the only license to speak above 410M |
| HE6 | 5M–160M (T0–T2) | ≤410M (T3) at most; explicitly UNLICENSED beyond: no published scaling study of frozen-embedding convergence penalties exists (L3 open question) | The one hypothesis where the literature provides no anchor at all — envelope hard-capped at the top measured rung until T3 runs |
| HE7 | ≥3 rungs per survivor | The programme's licensing instrument: one OOM past top rung, direction-only | Kaplan/Hoffmann extrapolation discipline, applied per mechanism |
| HS1 | 135M–360M, 2 families | Content-vs-format is an interface property; verdict quoted for ≤1.7B, expected weakly scale-dependent; re-check rides free on any F7 slice | E9-defl (R1) + Wieting–Kiela: random-structure nulls behave consistently across scales in the sentence-embedding literature |
| HS2–HS8 | R0 — no host model | Model-scale-free (properties of the kernel formalism); the relevant axis is KERNEL size: verdicts on 54–10³ records re-checked at 10⁴–10⁵ during bulk authoring (G6/G7 re-run as regression) | Formal-fragment properties don't vary with observer scale; only corpus composition shifts them |
| HS9–HS12 | Inherit constituent experiments | Envelope = intersection of the constituent rows (F2/F3/F5/F6) | — |
| HS13 | 5M–1B (T0–T3) | To 7B direction-only via fitted 3-rung trend; frontier statements prohibited — no published frozen-vocabulary scaling law exists in either direction | Frozen-glyph/arbitrary-identifier results + LCM penalty predict the null direction; a positive trend would contradict the literature and demands replication before extrapolation |
| HS-A | Authoring-model axis (Fable-5-class vs 8B) | Extrapolates forward monotonically with author capability (stated assumption: authoring quality non-decreasing in model capability — supported by Law 1); says nothing about host-side scale | DeepNSM (Baartmans et al.) is the published floor; Law 1 (symbol-side wins) is the licensing synthesis |

---

## 5. Dependency order and the kill-tree (cheapest-decisive-first)

Pre-experiment gates that must exist before any Tier-1 GPU spend: **M0b** kernel-
expressibility coverage number (bounds every claim; unrun — required), the P2 registry
(machine-readable pre-registration of every row below), and the F0 harness (`poc/f0/`).

| Tier | Experiments (hypotheses) | Cost | Gates / what a kill does |
|---|---|---|---|
| 0 (R0, this box, ~$0) | F1 (HE5 byte premise); G2+G3 (HS2, HS3); G6/G7 after G4; G8 (HS8); G9 (HS-A); M0b | ~$0 + annotator hours | F1-kill drops the byte story from every pitch. G3-kill (defeasible) auto-resolves HS2→sidecar-only and demotes Π to lint. G9-kill rewrites the why-now section. None of these blocks Tier 1. |
| 1 (~$10–60) | **F2** (HE1, HE2, HC3, HS12) | $10–40 (+$10–20 PRM arm) | **The pivot experiment.** F2 clean-kill at both rung pairs guts M1+M5 — the best-supported efficiency mechanisms — and the efficiency thesis shrinks to M6+M4-verifiability; maintainer informed for ~$40. F2 PASS makes H0-YES reachable and funds Tier 2 aggressively. |
| 2 (~$70–260) | E9-full + E9-C (HC1, HC2, HS11-part); F4+G1 (HE4, HS1); E8-R→E8-D (HC4) | E9 ~$20–90; F4+G1 ~$40–100; E8 ~$30–120 | E9-kill (incl. constraint arm) kills the correctness track's product story. F4-kill (text wins) kills M6 and, with F2-kill, most of H0's YES routes. G1-kill (Numberbatch parity) narrows every claim to governance. E8-R-kill shelves A6 — removes the pivot destination. |
| 3 (~$100–340) | F3 (HE3, HS10); F6 toy/T1 (HE6); G4 (HS4) then G6/G7 | F3 $50–170; F6 $50–150; G4 ~$0 | F3-kill retires dense I/O for efficiency (HS10 → interface-side). F6-kill (or text-arm parity) kills M3-vector and removes HS13's precondition. |
| 4 (~$200–800, double-gated) | F5 (HE5 full, HS9, HS11) | $200–800 | Runs only if F1 passed AND F3 settled the injection route. F5-kill retires M4-as-architecture. |
| 5 (maintainer gate, $2–10k) | F7 ≡ E7 (HE7, HC5, HS13) | $2–10k | The only tier that licenses scale adjectives and any frontier pitch. Never started without explicit budget sign-off. |

**Hard orderings:** F1 ≺ F5; F3 ≺ F5 (injection route); G2/G3 ≺ G4 ≺ G6/G7; F6(T0/T1 signal) ∧
maintainer-signoff ≺ E7/HS13; {F2, E9, F4, F6} readouts ≺ any F7 spend; M0b ≺ first external
quotation of any result. Everything else parallelises within the ~5-concurrent-agent cap.

---

## 6. Global go/no-go decision tree

Evaluated when Tiers 0–3 have read out (Tier 4 optional input); re-evaluated after any gated
tier. Verdicts are mutually exclusive; the FIRST matching pattern from the top applies.
"PASS"/"kill" below always means: against the pre-registered criterion, including the
kernel-as-text arm, audit-confirmed.

1. **TAKE-TO-FRONTIER-LAB** — pattern: (≥1 of HC1/HC2/HE1–HE6 PASS at ≥2 rungs) AND (its F7/
   HC5 slope measured at ≥3 rungs, flat-or-growing) AND (novelty search re-run per L1 §10.7)
   AND (every load-bearing positive independently audited). The pitch is scoped to the
   surviving track only (verifier/instrument OR a named efficiency mechanism), carries its
   rungs, coverage bound (M0b), and comparison discipline, and never restates A1 unless HS13
   itself passed. Two-audience separation (research vs assurance) per architecture §4.
2. **NARROW-AND-CONTINUE** — pattern: (≥1 mechanism PASS at ≥2 rungs but slope unmeasured or
   mixed) OR (E8-R PASS but E8-D unrun/failed) OR (single-discipline efficiency wins only).
   Action: fund exactly the missing decisive rung/test (usually the F7 gate or E8-D); no
   external claims beyond the measured rungs; prospectus updated with qualified verdicts.
3. **PIVOT** — pattern: correctness and efficiency mechanisms all killed against the text
   null (H0-NO per §1) BUT (E8-R PASS + E8-D PASS) ⇒ pivot the programme to the
   kernel-as-interpretability-instrument (A6) and cross-version semantic-regression tooling;
   OR all vector-mediated cells dead but HC2 (constraint-violation delta) alone PASSes ⇒
   pivot to the assurance/verification product (A5-narrow) with no performance claims. In
   either pivot, the encoder/identity layer persists as standalone engineering value.
4. **KILL** — pattern: H0-NO (F2, E9-full incl. E9-C, F4, F6 all TOST-killed or criterion-
   killed at their decisive rungs) AND E8-R fails site-matched AND HC2 fails. Action: the
   programme terminates as a negative-results publication — full statistics, all raw logs,
   the registry, and the honest statement that the kernel's measured value to LLMs, at the
   tested scales and coverage, did not exceed its own text rendering. The kernel object
   (encoder, identity, KOTK/2, axiom sidecar) is archived as reusable engineering with its
   X-series quality card.

**Anti-overselling guards bound to the tree:** no verdict may cite a mechanism's PASS without
its kill-criterion text alongside; "narrow-and-continue" cannot be invoked twice for the same
missing evidence; a pivot must publish the kills that forced it in the same document that
announces the pivot.

---

## 7. Already-decided vs open (the prior-evidence ledger)

| Question | Status | Decided by / open pending |
|---|---|---|
| Encoder determinism, adversarial margins, projection survival | **DECIDED — holds** | X0, X1 (11× floor), X4 (ρ≈0.97, ~10× floor at 512/576) |
| Full decode given the kernel | **DECIDED with named gap** | X2 51/54; gap tracked; no decode-dependent claim on Bq path |
| Kernel cosine as semantic similarity | **DECIDED — banned** | X3; kernel-kNN banned pending a dominating mitigation |
| NSM primes graph-distinguished in WordNet Core | **DECIDED — no** (instrument-limited) | X1-grounding FAIL; does not gate anything |
| Designed geometry detectably aligned with learned geometry | **DECIDED — yes (correlational)** | E2 PASS, 3/3 families |
| Adapter transfers kernel *content* to unseen concepts (R1, one family) | **DECIDED — yes** | E5 PASS + E9-defl PASS (content, not format) |
| Content-vs-format at other rungs/families; vs Numberbatch/random-codebook | **OPEN** | G1 (HS1) |
| A1 frozen vocabulary at toy scale | **OPEN, negative-leaning** | E1 INCONCLUSIVE (instrument underperformed); E4 MOCK-only; literature predicts null |
| A1 at scale | **OPEN, double-gated** | HS13/E7 |
| Kernel↔SAE label space (A6) | **OPEN** | E8: 1 PASS + 1 site-confounded non-replication → E8-R, then E8-D |
| Verifier end-task benefit (A5) | **OPEN — mechanics ready, benefit unmeasured** | E9-full (HC1), E9-C (HC2) |
| Verifier vs trained PRM | **OPEN** | F2+PRM (HC3) |
| All efficiency mechanisms M1–M6 | **OPEN** (M2-output expected-fail; M4 byte edge measured at ~3.3× pending gloss-text check) | F1–F6 |
| KOTK/2 byte floor vs structured text | **DECIDED (partial)** | 2.90 vs 9.58 B/rec measured; vs compressed gloss text OPEN (F1) |
| Verifier-not-in-the-vector | **NEAR-DECIDED** | X3 + stratum argument; G5 confirmation only if HS2 needs it |
| Π read-out soundness; semantics pin; axiom syntax; grammar capacity; Lean minting | **OPEN** | G2/G3/G4/G6/G7/G8 (HS2–HS8) |
| Kernel-expressibility coverage (bounds every claim) | **OPEN — required gate** | M0b |
| Authoring why-now vs DeepNSM | **OPEN** | G9 (HS-A) |

---

## 8. Master hypothesis table (registry seed)

Each row becomes one entry in the machine-readable registry (component P2); the registry
entry additionally pins: encoder hash, corpus hash, arm definitions, endpoint formula,
analysis script hash, the verbatim kill text from §§1–4, and the extrapolation envelope
from §4b (quoted verbatim in every generated verdict).

| ID | One-line statement | Decisive exp. | Kill criterion (abbrev.) | Rungs | Cost | Depends on |
|---|---|---|---|---|---|---|
| H0 | Kernel principle helps LLMs beyond text-null + industrial baselines | disjunction gate | all of {F2,E9,F4,F6} TOST-killed ⇒ NO | ≥2 rungs | Σ tiers 0–3 | all below |
| HC1 | Decode-verify catches errors RAG/gloss-text cannot | E9-full | ≥90% catch-overlap by gloss arm at ≤cost ⇒ dead | R1–R3 | $20–80 | Tier 0 |
| HC2 | Axiom sidecar catches planted violations text cannot | E9-C | e2e catch <0.80 or <3× best text arm or FP>2% ⇒ dead | R1–R2 | +$10 | E9-full |
| HC3 | Deterministic verifier ≥ trained PRM on covered slice | F2+PRM | PRM parity at matched FLOPs ⇒ dead | R1–R3 | +$10–20 | F2 |
| HC4 | Kernel = canonical SAE label space; beats probe downstream | E8-R, E8-D | site-matched non-replication; probe parity ⇒ dead | 125M–1B fams | $30–120 | — |
| HC5 | Verifier lift non-vanishing with scale | F7 slice | <10% rel. error-reduction extrapolated at R5 ⇒ toy-only | R1–R4 | in F7 | HC1/HC2 pass |
| HE1 | s+verifier ≥ S at lower total cost (M1) | F2 | <50% gap closed; or text/matched-compute parity; or cost ≥ S ⇒ dead | (R1,R2),(R2,R3) | $10–40 | Tier 0 |
| HE2 | Verifier-gated cascade dominates logprob cascade (M5) | F2b | not strictly dominant ⇒ dead | R1→R3 | in F2 | F2 |
| HE3 | Dense concept input halves prompt FLOPs/KV at parity (M2-in) | F3 | loses to matched-token text at d≥16; or trained-compressor parity ⇒ dead | R1–R3 | $50–170 | F2 read |
| HE4 | Adapter onboarding ≥90% LoRA at ≤10% FLOPs, beats text (M6) | F4 | text-null ≥ adapter at matched cost ⇒ dead | R1–R3 | $20–60 | Tier 0 |
| HE5 | Kernel store outside accuracy-vs-bytes hull (M4) | F1→F5 | F1 <2× bytes; F5 inside {text-RAG,int4,distill} hull ⇒ dead | store 10³–10⁶; T1–T2 | $0 + $200–800 | F1, F3 |
| HE6 | Kernel scaffolding ⇒ ≤0.8× tokens-to-target (M3) | F6 | TOST fail vs trainable; or text-data-arm parity ⇒ dead | T0–T2 | $50–150 | Tier 0 |
| HE7 | Surviving Δ flat/growing over ≥3 rungs | F7 | Δ<10% extrapolated at 7B ⇒ toy-only | 3+ rungs | $2–10k gate | survivors |
| HS1 | NSM pinning beats random codebook / Numberbatch | G1 (F4 ext.) | Numberbatch or random-codebook parity ⇒ claim narrows to governance | R1–R2, 2 fams | +$20–40 | F4 |
| HS2 | Π read-out sound (native axiom form) | G2 | precision <0.9 ⇒ Π = lint, sidecar-only | R0 | ~$0 | G3 |
| HS3 | Necessary-conditions pin survives instances | G3 | necessity fails >10% ⇒ defeasible; sufficiency >10% ⇒ no equivalence | R0 | ~$0 | — |
| HS4 | NSM-native axiom syntax authorable at ≤2× effort | G4 | >2× effort or pin disputes ⇒ sidecar; mistranslation ⇒ NSM-native | R0 | ~$0 | G2 residue |
| HS5 | Constraints out of the vector (confirm) | G5 | surprise reversal ⇒ new pre-registration | R0 | ~$0 | HS2 outcome |
| HS6 | ∃-conjunctive fragment suffices (AND-under-op <20%) | G6 | ≥20% need + not sidecar-expressible ⇒ extend grammar | R0 | ~$0 | G4 |
| HS7 | Apply-clauses needed iff caps break >10% at bulk | G7 | cap violations/1.5× growth >10% ⇒ kot-ast/2 | R0 | ~$0 | G4 |
| HS8 | Lean minting viable (≥1% gate, ≥80% top-5 location) | G8 | below bounds ⇒ Metamath-only stands | R0 | $0–10 | — |
| HS9 | Store vs scaffold-then-absorb lifecycle crossover | F5 vs F6 @T2 | dominated at all realistic Q ⇒ that option dies | T2 | in F5/F6 | F5, F6 |
| HS10 | Efficiency lives at interface, not dense I/O | F3 vs F2 | F3 arm dominated by F2 cascade ⇒ drop dense I/O | R1–R3 | — | F2, F3 |
| HS11 | Structured store earns place via verifier only | F5 a2v3 + E9-C | text-store parity on both ⇒ format, not architecture | T2, R1–R2 | in F5/E9 | F5, E9 |
| HS12 | Retry vs in-decode gating (implementation pick) | F2 sweep | no kill; latency decides | R1–R3 | in F2 | F2 |
| HS13 | A1 frozen vocabulary at scale (gated remnant) | E7 | shrinking or absent at T2 (TOST) ⇒ A1 closed | T0–T3 | $2–10k gate | F6 signal + sign-off |
| HS-A | Fable authoring decisively beats DeepNSM-8B | G9 | not decisively better ⇒ why-now weakened, stated everywhere | authoring axis | $0–20 | — |

*Total pre-gate budget (Tiers 0–3): ≈ $180–650. Tier 4 adds $200–800. Tier 5 (the only
frontier-relevant tier) is a separate $2–10k maintainer decision.*
