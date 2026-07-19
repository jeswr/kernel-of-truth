# P3-LR-RULE — Rule-injection into transformers (formalized, verified)

**Bead:** P3-LR-RULE (`kernel-of-truth-s55r.8`; Programme-3 rev-2 §5 Phase-0 table; scope §3.3
H-RULE placement analysis).
**Deliverable path:** `reports/lit-p3-rule.md`.
**Author/role:** literature-review agent (Opus execution), independent source-verification +
formalization pass.
**Date:** 2026-07-19. **Status:** DRAFT for coordinator review. Nothing here is frozen, registered,
or scheduled; no registry record / ASM / KB shard is touched; no bd/git operations; no child agents.
**Parent:** `docs/next/programme-3-neurosymbolic-architecture.md` (rev 2) §3.3
(H-RULE-{CD,KV,AD,ACT,HL} placement table + the CD → KV → {AD,ACT} → HL ordering ruling, ASM-0802,
ASM-0806, ASM-0815). **Extends** `reports/lit-llm-injection-priorart.md` (2026-07-08).
**Feeds:** P3-D-RULE (co-blocked by P3-LR-NTP).

> **Relationship to `docs/next/lit/RULE.md`.** A prior, careful RULE review exists (Fable,
> 2026-07-11, once-revised on an independent GPT-5.6 review, with source ledger
> `RULE.sources.jsonl`, 65 entries). **This report is not a redo.** It is (a) an independent
> re-verification of the draft's load-bearing citations at their primary sources this session,
> (b) an explicit divergence log, and (c) a formalization at the requested `reports/` path,
> epistemic-tagged and refreshed to 2026-07-19. Where I re-fetched a source I say so; where I
> accepted the 07-11 verification without re-fetch (uncontested abstract-level anchors) I mark
> `[prior-verified: 2026-07-11]`. **Headline of the verification pass: every load-bearing number I
> re-checked holds at source** — including the two I chased hardest (VSA-rule's contested figures
> and CRANE's Table-1 token counts). Divergences found are provenance-level and, in one case, a
> now-*stale caution* in the draft that this pass can retire (§ Divergences). This report's central
> analytic addition over the draft is the **matched-resource-win assessment for the RULE pathway,
> put in the same accounting frame the sibling FUSE review used** (github #57), so the two pathways
> can be read side by side.

## Epistemic tag convention

- `[established]` — external empirical/methodological fact confirmed at a primary source (this
  session or prior). `[claimed]` — asserted in a source but single-group, abstract-only, or not
  independently corroborated. `[speculative]` — my forward inference / design judgement.
- Provenance suffix: `[search: 2026-07-19]` = re-verified at source via WebSearch/WebFetch this
  session; `[prior-verified: 2026-07-11]` = verified at source in the 07-11 RULE.md, accepted here
  without re-fetch; `[memory]` = from the parent doc / in-repo verdicts, not a literature source.
- `[UNVERIFIED]` = could not be confirmed at primary source (paywall/fetcher failure or carried
  unre-fetched from a prior review).
- Measurement register (inherited from the draft, kept): a "MEASURED" number below is the *authors'*
  published measurement restated inside that paper's own envelope — never *our* measurement, and
  never a premise for a KoT verdict. Cross-paper readings are direction-only.

---

## Top findings (read this first)

1. **THE CRUX — does any rule-injection method beat a *matched-resource* neural baseline under fair
   accounting? Honest answer: no — and this concurs with the sibling FUSE finding (#57).**
   `[established][search: 2026-07-19]` Under the fair-accounting bar (same information + trainable
   params + training compute + causality-by-perturbation), **no rule-injection placement in this
   review shows a clean matched-resource win**:
   - **Constrained decoding + executor** (MGD, type-constrained, CRANE) wins as a **same-host
     ablation** (same frozen model ± engine-derived mask), *not* a resource-matched win: the
     constrained arm does extra, unpriced work — static-analysis/executor CPU time, per-token engine
     calls, backtracking, and (with reasoning-admitting grammars) **more generated tokens**
     (CRANE Table 1, verified: 128.97 → 131.3 tokens at Qwen2.5-1.5B, 212.24 → 235.78 at
     R1-Distill-Qwen-7B). These are **accuracy** claims on a fixed host.
   - **Steering and editing LOSE their matched comparison outright**: prompting beats every
     representation-level steering method at 2B (AxBench), and a simple in-context baseline beats
     every parametric editor on ripple propagation (RippleEdits). The matched neural baseline *is
     the winner* in both families.
   - **The one genuine matched-FLOPs win in the whole review is memory-layers** — and it does **not**
     count as a rule-injection win (see finding 2).
   - **KV-of-rules is an empty cell** (untested), and the strongest H-RULE-ACT result (VSA-rule) is
     single-group and unreplicated (finding 4).
   This is exactly the FUSE steering signal — *"the NeSy systems that DO beat neural baselines win by
   adding an exact-reasoning capability the baseline lacks, not at matched resources"* (#57) — now
   independently reproduced on the RULE pathway. The strongest and cleanest wins in this review
   (Logic-LM +39.2%/+18.4%, CD+executor) are **add-capability** wins where an external deterministic
   engine owns correctness, not matched-resource efficiency wins.

2. **The strongest matched-resource candidate — memory-layers — is verified, and is honestly the
   wrong prior for the H-RULE frozen-host bet.** `[established][search: 2026-07-19]` Memory Layers at
   Scale (Meta) verifies exactly at source: memory-augmented models "outperform dense models with
   more than twice the computation budget, as well as mixture-of-expert models when matched for both
   compute and parameters," with gains "especially pronounced for factual tasks" (up to 128B memory
   params, 1T tokens, base to 8B). That is a real matched-FLOPs *and* matched-params win — but (a)
   it is **factual RECALL, not rule inference**; (b) **params go up** — it is a
   trained-from-pretraining *architecture*, not a training-free rule store bolted onto a frozen host;
   (c) it is therefore prior art for **H-GU / H-RULE-HL economics**, not for any shallow H-RULE
   placement. It sharpens rather than rescues the crux: the only matched-resource win the literature
   offers is a lookup-capacity architecture for facts, not a rule-composition mechanism.

3. **The composition wall (the draft's §5) is the load-bearing architectural PRIOR, and all four of
   its legs verify at source.** `[established][search: 2026-07-19]` (i) Physics-3.2: transformers
   "excel in knowledge retrieval but struggle even in the simplest classification or comparison
   tasks unless CoTs are employed during both training and inference," and inverse search is
   "virtually 0%." (ii) CoT-depth theory (NeurIPS 2023 oral): bounded-depth transformers "are unable
   to directly produce correct answers for basic arithmetic/equation tasks unless the model size
   grows super-polynomially"; constant-size transformers suffice *with* CoT tokens. (iii)
   Two-hop/hopping/grokking: latent multi-hop composition is unreliable; back-patching rescues up to
   66% of failures. Read honestly as a **strong, falsifiable, burden-shifting prior** (asymptotic
   theory + controlled synthetic studies, *not* a closed law): placements that ask the host to
   execute rule composition in a forward pass carry the burden of proof; placements that let the
   engine compute and *deliver results* do not. This is the literature's independent argument for
   the CD → KV-of-derived-facts ordering — not just cheapest-first.

4. **The strongest H-RULE-ACT result (VSA-rule) verifies numerically — at BOTH sources — but stays a
   single-group, unreplicated, nsk1-shaped bet.** `[established (numbers)/claimed (load-bearing
   use)][search: 2026-07-19]` Dhanraj & Eliasmith (EMNLP 2025 main) report "88.6% lower cross-entropy
   loss and 15.4 times more problems correctly solved" vs CoT and LoRA. I verified this at the ACL
   Anthology **and** at arXiv 2502.01657 — they now agree (see the retired-caution divergence). But
   it is one group (Waterloo / Nengo VSA lineage), a narrow math suite, unreplicated, host size
   unstated in the abstract, and structurally the exact nsk1 channel the programme has already
   measured as **delivery-yes / integration-unresolved**. Its "efficiency via offloading" claim is
   *not* accounting-audited against matched trainable-param/compute — it adds a VSA encode/compute/
   decode apparatus. It is a replication-shaped bet, not a load-bearing positive.

5. **The per-placement causal-evidence bar is real and independently supported: attention maps are
   not provenance.** `[established][prior-verified: 2026-07-11]` KBLaM's own "attention weights give
   interpretable insight into knowledge use" is descriptive telemetry, not causal provenance — the
   attention-(not-)explanation literature, localization≠intervention (HASE), patching
   protocol-sensitivity, the Hydra self-repair effect, and the subspace-illusion result each become a
   pre-registered control. This corroborates ASM-0815 and gives P3-D-RULE a ready threat/control
   table (§ The per-placement causal-evidence bar).

**Bottom line for Programme-3.** The RULE pathway does **not** overturn the FUSE steering signal; it
reinforces it. If the kernel's defensible value on this pathway is efficiency-at-matched-resources,
the literature offers no precedent and the composition wall predicts failure for the composition-
requiring placements. If the value is **add-capability correctness** — an external deterministic
engine that owns a class of exact reasoning/coverage/fail-closed behaviour the neural baseline
lacks, delivered at the decode boundary — that is where every clean win in this review lives, and it
is the F1-K correctness thesis (#57 speculative point 2), now supported from a second pathway.

---

## 1. What the programme's own measured anchors fix (unchanged, [memory])

The draft's §1 anchors are repo-internal and I did not re-derive them; they frame every ruling below
and are carried verbatim as `[memory]`:

- The external verify-retry loop (H-VL) is the programme's **only** end-task positive (f2b-replicate
  +0.1507 at ~10% FLOPs, alignment-specific, formal inputs) `[memory: registry/verdicts/
  f2b-replicate.json]`. H-RULE asks whether moving the engine *inside* the model beats that loop on
  Pareto frontiers (ASM-0806).
- Text-appended engine facts were **net-harmful** to a small host (g2d 0.76 → 0.43; 0/24 rescues);
  the residual-stream channel delivers content at ECHO grade (keyacc 0.81/0.85) without resolving
  INTEGRATION (R− rescue 0/8) `[memory: registry/assessments/nsk1-*]`. Any H-RULE-ACT design
  inherits this caution directly.
- The NL front-end is a measured FAIL at scope (l3a-parse 47.6%, a5-nl 41.6% + S2 fired) `[memory]`
  — so every NL leg of P3-E-RULE-1 is NLB-gated (ASM-0814); formal/covered slices go first.
- Constrained decoding is TRANSPORT, not inference; attention maps are NOT causal provenance
  `[memory: ASM-0815]`. Both stipulations survive the literature test below (the second with strong
  independent support).

---

## 2. Per-placement findings (verified)

### 2.1 H-RULE-CD — constrained/grammar decoding WITH an executor

The organizing distinction (draft §2.1) survives at source: **grammar-only CD shapes the output
language** (a solved transport problem — SynCode eliminates JSON syntax errors and cuts Python/Go
syntax errors ~96%; XGrammar makes grammar-mask transport near-zero-overhead), while
**executor-coupled CD** has a semantic engine derive the *valid continuation set* and the mask
deliver it. The verified executor-coupled lineage:

- **Execution-guided decoding (2018)** `[established][prior-verified: 2026-07-11]` — execute partial
  SQL during beam decoding, prune faulty candidates, no retraining; then-SOTA 83.8% execution
  accuracy on WikiSQL. Earliest clean instance.
- **PICARD (EMNLP 2021)** `[claimed][UNVERIFIED — carried]` — incremental parsing with type-checking
  modes; T5-3B to then-SOTA Spider/CoSQL, execution errors 12%→2%. Flagged `verified:false` in the
  draft and NOT re-fetched this pass; carried as UNVERIFIED. (PICARD's is a fine-tuned-parser-+-mask
  *systems* claim, not a same-host ablation — noted for accounting.)
- **Synchromesh / Constrained Semantic Decoding (ICLR 2022)** `[established][prior-verified:
  2026-07-11]` — formalizes the **completion engine**: given a partial program, return the valid
  continuation set enforcing syntax, scope, typing, contextual logic, no retraining. This is the
  exact formal shape of H-RULE-CD and the interface spec P3-D-RULE should adopt.
- **Monitor-Guided Decoding (NeurIPS 2023)** `[established][search: 2026-07-19]` — **RE-VERIFIED.**
  "With MGD, SantaCoder-1.1B achieves better compilation rate and next-identifier match than the
  much larger text-davinci-003 model"; the monitor "uses static analysis"; improvements consistent
  "on models of varying parameter scale." **This is the flagship in-band (1.1B) executor-in-the-
  decode-loop result** — the only published result in the programme's exact shape (tiny host +
  deterministic engine at the decode boundary). Accounting caveat (draft-correct): same-model ±
  monitor is a same-host **ablation**; the monitor's static-analysis CPU work and decode-loop latency
  are real, unpriced resources; the cross-size headline (1.1B > 175B-class) is quoted only in its
  same-model form.
- **Type-constrained decoding (PLDI 2025)** `[established][search: 2026-07-19]` — **RE-VERIFIED at
  arXiv 2504.09246** (the ACM DOI is paywalled; see Divergences): prefix automata + inhabitable-type
  search "reduces compilation errors by more than half" and "significantly increases functional
  correctness in code synthesis, translation, and repair tasks across LLMs of various sizes and
  model families, including state-of-the-art open-weight models with more than 30B parameters."
  Executor = the type system; sound enforcement.
- **IterGen (ICLR 2025)** `[established][prior-verified: 2026-07-11]` — grammar-symbol-addressed
  backtracking with KV-cache reuse; +18.5% mean over SOTA grammar-guided generation on SQL. Adds the
  retract primitive pure masking lacks.
- **CRANE (ICML 2025)** `[established][search: 2026-07-19]` — **RE-VERIFIED, including Table 1.**
  Answer-only grammars provably diminish reasoning; augmenting the grammar to admit reasoning then
  constraining answer spans recovers it — "up to 10% points accuracy improvement over baselines on
  GSM-symbolic and FOLIO." Table 1 token counts (fetched from the HTML): Qwen2.5-1.5B CoT **128.97**
  tokens (26% acc) → CRANE **131.3** (31%); R1-Distill-Qwen-7B CoT **212.24** (24%) → CRANE
  **235.78** (29%). **CRANE emits MORE tokens than unconstrained CoT** while gaining accuracy — an
  accuracy win, explicitly not a resource-matched one. The draft's numbers are correct.

**Priced caveats (draft §2.2), each confirmed:** distribution distortion (GAD/ASAp corrects at
sampling cost) `[established][prior-verified]`; reasoning/format tax (format restriction degrades
reasoning; "structure snowballing" in reflection on Qwen3-8B) `[established][prior-verified]`, with
the mitigation demonstrated only for the reasoning-tax component (CRANE's span-scoping). The **empty
cell** the draft flags stands: **no surveyed system constrains a span to {engine-valid
continuations} ∪ {refusal} with fail-closed semantics under partial coverage** — selective-span,
coverage-aware, abstention-preserving CD is unbuilt, and the programme would be first.

**Accounting verdict (CD):** the cleanest in the review, but the correct claim is **same-host
ablation, not matched compute**. Every §2.1 headline is an accuracy claim on a fixed host (except the
MGD cross-size quote and PICARD's systems claim, both flagged). XGrammar's near-zero overhead is for
grammar-mask transport only and does **not** transfer to semantic-engine calls, per-token executor
work, or backtracking (draft-correct; an open engineering question, not a result). `[established +
speculative synthesis]`

### 2.2 H-RULE-KV — KV-memory injection

- **KBLaM (ICLR 2025)** `[established][search: 2026-07-19]` — **RE-VERIFIED.** KB triples →
  continuous key-value pairs "via pre-trained sentence encoders with linear adapters," read through
  rectangular attention; ">10K triples into an 8B pre-trained LLM ... on one single A100 80GB GPU";
  overhead "scales linearly with KB size"; "interpretable insights into its use of the augmented
  knowledge." Two things the draft gets right: (a) the specific *attention-weights-show-knowledge-use*
  wording is from the **MSR blog** (cited separately, `kblam-msr-blog-2025`), while the paper abstract
  says only "interpretable insights" — the draft attributes each correctly; (b) the base-weights-
  frozen / instruction-tuned-projection detail is a body-level claim (not in the abstract), carried
  from the 07-08 injection review. **Demonstrated only at 8B+.**
- **AtlasKV (ICLR 2026)** `[established][search: 2026-07-19]` — **RE-VERIFIED.** KG2KV + HiKVP push
  the same KV shape to "~1B triples ... less than 20GB VRAM," sub-linear time/memory, "no external
  retrievers ... or retraining when adapting to new knowledge." The line is alive and industrializing
  — but every member trains the bridge.
- **Memory Layers at Scale (Meta 2024)** `[established][search: 2026-07-19]` — **RE-VERIFIED** (see
  finding 2). The genuine matched-FLOPs+params win; factual recall; params up; a pretraining
  architecture, not a bolt-on. Prior art for H-GU/H-RULE-HL economics.
- **Cache steering (2025)** `[established][search: 2026-07-19]` — **RE-VERIFIED.** Training-free
  one-shot KV-cache intervention; vectors "constructed from reasoning traces ... from teacher models
  (e.g. GPT-4o)"; induces multi-step reasoning in small models; lower latency + better hyperparameter
  stability than continuous activation steering. **The only training-free KV write demonstrated at
  our band — but it injects BEHAVIOUR (reasoning style), not content, and the vectors come from a
  teacher model, not an engine.**
- **Larimar (ICML 2024)** `[established][prior-verified: 2026-07-11]` — external episodic memory
  module; one-shot updates 8–10× faster than locate-then-edit; a trained bridge again.

**Verdict for the placement (draft §3.2):** `[established pattern → speculative as a law]` every
working KV-side injection of **content** runs through a trained component (KBLaM/AtlasKV adapters +
instruction tuning; memory layers trained end-to-end; Larimar's trained module; cache steering's
teacher-distilled vectors) — the injection report's interface-locality law extends unbroken into
2026. **Two cells empty:** (i) content-level KV injection at ≤2B (only *behaviour*-level cache
steering is in-band); (ii) KV injection of **rules** with causal validation of the licensed inference
— the H-RULE-KV bet, whose predicted failure mode is §5's composition wall (the host must still
compose the injected rule with query facts in-weights). The literature-consistent variant is **KV of
engine-DERIVED facts** (engine fires the rule per query; the KV pair carries the conclusion, keyed by
kernel content-hash) — lookup-shaped consumption, the shape KBLaM proves at 8B. Both arms should be
carried: KV-of-rule-premises stays as the pre-registered falsifier of the prior, alongside the
derived-facts lead.

### 2.3 H-RULE-ACT / H-RULE-AD — steering, editing, adapters

**Steering — the positive line, then the hard correction:**

- Positive `[established][prior-verified: 2026-07-11]`: ITI lifts Alpaca TruthfulQA 32.5%→65.1%;
  CAA/ActAdd steer Llama-2-Chat behaviours; function vectors are transportable activation-space
  objects. (ActAdd, RepE flagged `verified:false` in the draft, carried UNVERIFIED.)
- The correction `[established][search: 2026-07-19 for the two load-bearing ones]`:
  - **AxBench (ICML 2025)** — **RE-VERIFIED**: on Gemma-2-2B/9B concept steering, "prompting
    outperforms all existing methods, followed by finetuning"; "SAEs are not competitive." On the
    only matched concept-steering harness at our scale, **the text interface wins** — the same Law-2
    shape as the injection report.
  - **Steering off Course (2025)** — **RE-VERIFIED**: DoLa / function vectors / task vectors across
    "up to 36 models belonging to 14 families ... 1.5B to 70B," with "a large number of models
    showing no improvement and at times degradation"; "fundamental flaws in the assumptions."
  - Mechanistic cause `[established][prior-verified]`: steering fails when the target behaviour lacks
    a coherent linear direction (cosine similarity of training activation diffs + pos/neg separation
    predict steerability).
- Direct rule-injection steering prior — **VSA-rule (EMNLP 2025 main)** `[established (numbers) /
  claimed (use)][search: 2026-07-19]`: **RE-VERIFIED at two sources** (finding 4). The strongest
  H-RULE-ACT-shaped result, but single-group, narrow, unreplicated, nsk1-shaped. **ATLAS (2026)**
  `[established][prior-verified]` adds a *trained* verifier over latent states gating adaptive
  steering — executor-adjacent, but the gate is learned (PRM-grade, not engine-grade provenance).

**Editing — fact-rewrite, not rule-injection:** ROME/MEMIT localize + edit associations; AlphaEdit's
null-space projection lifts the locate-then-edit family avg 36.7% and repairs sequential-editing
damage `[established][prior-verified]`. Against that: **localization does not inform editing** (HASE);
**a simple in-context baseline beats all parametric editors on RippleEdits** (**RE-VERIFIED this
pass**: "current methods fail to introduce consistent changes"; "a simple in-context editing baseline
obtains the best scores"); sequential editing causes gradual-then-catastrophic forgetting. **Nothing
in the editing literature injects an inference RULE** — every item is a (subject, relation, object)
rewrite, and even the *consequences* of one edit do not propagate in-weights. Editing is maintenance
tooling for parametric facts, weak at that; not a rule channel.

**Adapters — procedures softly yes, knowledge no:** knowledge-injection via adapters/FT loses to
in-context on the same host (RAG > unsupervised FT; new-knowledge FT is slow then hallucinogenic;
parametric-RAG underperforms token-RAG) `[established][prior-verified]` — noting these test
KNOWLEDGE, not rules, and do not establish matched lifecycle/tuning compute. Procedures are more
modular than facts (task-arithmetic composes; LoraHub reaches few-shot ICL parity) but few-shot
parity is the ceiling and nothing gives soundness or fail-closed behaviour. **Verdict:** adapters
LEAD as vehicles for *around-engine* behaviours (consult/format/defer — the A2/E5 bridge precedent),
and are the wrong vehicle for the rules themselves; a rule-as-adapter arm is retained as §5's AD-side
falsifier, measured LAST among the shallow placements.

### 2.4 The composition wall (H-RULE's load-bearing prior)

All four legs **RE-VERIFIED this pass** (findings 3): Physics-3.2 (storage ≠ manipulation; inverse
search ~0%), CoT-depth theory (bounded-depth can't do multi-step arithmetic without CoT tokens; NeurIPS
2023 oral), two-hop/grokking/hopping (latent composition unreliable; back-patching rescues ≤66%;
reversal curse). Read as a **strong, falsifiable, burden-shifting prior**, not a closed law — scope
stated honestly (asymptotic theory on specific constructions + controlled synthetic studies; does not
rule out finite-length tasks, latent recurrence, deeper hosts, or trained adapters). What it licenses:
internal placements should deliver engine RESULTS, not rule PREMISES; composition-requiring arms
(KV-of-rules, AD-of-rules, HL) carry the burden of proof and stay as pre-registered falsifiers.

**H-RULE-HL corollary (bottleneck architectures):** CBMs achieve competitive accuracy with test-time
concept intervention, and CB-LLMs claim classification parity + controlled generation — but concept
**leakage** is documented (bottleneck units "do not correspond to anything semantically meaningful in
input space") `[established][prior-verified]`. Naming units is not interpretability; an HL placement
would need §6-grade causal validation of every pinned unit *plus* a general-capability non-inferiority
gate. Nothing in the record makes HL urgent; everything makes it expensive.

---

## 3. The per-placement causal-evidence bar (what counts beyond attention maps)

`[established][prior-verified: 2026-07-11; ASM-0815 corroborated]` **Attention maps are not
provenance**: attention weights are frequently uncorrelated with gradient importance and adversarially
different attention yields identical predictions (Attention is not Explanation); the strongest defense
concedes attention claims need diagnostics and never stand alone (Attention is not not Explanation).
KBLaM's "attention shows knowledge use" is descriptive telemetry. The threat/control table P3-D-RULE
should freeze:

| Threat | Evidence | Control to pre-register |
|---|---|---|
| Localization ≠ intervention success | causal tracing does not predict best edit layer (HASE, NeurIPS 2023 spotlight) | never infer "inject/edit HERE" from tracing alone; test the intervention directly |
| Protocol sensitivity | patching conclusions flip with metric (prob vs logit-diff vs KL) and corruption method (ICLR 2024) | fix the metric suite in advance; report all three |
| Self-repair masks effects | ablating one attention layer recruits downstream compensation (Hydra effect) | resampling ablations over single-point ablations; compensation-aware baselines |
| Dormant-pathway illusions | subspace patching can change behaviour via causally-disconnected parallel pathways | full-rank + random-subspace controls; require agreement |
| Hypothesis under-specification | causal scrubbing's resampling-ablation discipline `[UNVERIFIED at source — anchored via the verified causal-abstraction survey]` | state the causal graph being claimed BEFORE intervening |
| Framework | interchange interventions / causal abstraction unify patching, scrubbing, tracing, steering | state per-placement provenance claims as causal-abstraction claims |

**The per-placement provenance ladder** (draft §6, carried): **CD** — the engine's derivation trace
(record id per constrained span) is exact *constraint/eligibility* provenance by construction, and
causal *answer* attribution only where the engine uniquely determines the span (multi-valid and
uncovered spans need the apparatus above). **KV** — knowledge-token ablation + interchange
interventions (swap record KVs between matched queries; the answer must follow the record; echo-vs-
integration à la nsk1 derangement controls) + executor trace; attention maps descriptive only.
**ACT** — activation patching under the fixed metric suite + cross-seed steering-vector stability +
dormant-pathway controls. **AD/HL** — behavioural counterfactuals with matched controls
(shuffled-rule adapters; leakage probes for HL); no unit-naming accepted as evidence.

---

## 4. The matched-resource-win honest assessment (the FUSE-parallel section)

The sibling FUSE review (github #57) established that no GNN–LLM *fusion* system beats a
matched-resource neural baseline under fair accounting. **The same audit, applied to the RULE
pathway, returns the same answer.** Ledger, in the FUSE accounting frame:

| Rule-injection candidate | Baseline it beat | What was matched | What was NOT matched | Matched-resource win? |
|---|---|---|---|---|
| MGD (SantaCoder-1.1B + monitor > text-davinci-003) | same model without monitor (+ a cross-size headline) | the host (same-model ablation) | static-analysis CPU work, decode-loop latency; the cross-size claim is cross-model | **No** — same-host accuracy ablation; engine work unpriced |
| Type-constrained (compile errors −½) | same model without type mask | the host | type-inference/automaton work per token | **No** — accuracy ablation |
| CRANE (+≤10pp, GSM-Symbolic/FOLIO) | same model, constrained & unconstrained | the host | **more generated tokens** (Table 1, verified) + constrained-decoder work | **No** — accuracy at higher token cost |
| Logic-LM (+39.2%/+18.4%) | standard prompting; CoT | the host | an external solver (add-capability) | **No** — the archetypal *add-capability* win, not matched-resource |
| Memory layers (> MoE at matched compute+params) | dense (>2×), MoE (matched) | **compute AND params** | it is factual recall, params-up, trained from pretraining | **Yes for facts — but not rule injection**; H-GU/HL economics prior |
| VSA-rule (15.4× more solved) | CoT; LoRA | (host, per abstract; size unstated) | VSA encode/compute/decode apparatus; not param/compute-audited; single-group | **Not established** — unreplicated, nsk1-shaped |
| KBLaM / AtlasKV (KV injection) | in-context text of the same KB | the knowledge content | trained instruction-tuned adapters; the win is **cost-shape**, not accuracy | **No** — cost-shape win, needs a trained bridge, 8B+ |
| AxBench (steering) | prompting | concept-steering harness | — | **No — the matched baseline (prompting) WINS** |
| RippleEdits (editing) | in-context editing | ripple benchmark | — | **No — the matched baseline (in-context) WINS** |

**Audit verdict** `[established facts; EXTRAPOLATION reading, direction-only]`:

1. **No rule-injection placement in this review beats a matched-resource neural baseline under full
   accounting** (same info + trainable params + train compute + causality-by-perturbation). CD wins
   are same-host ablations with unpriced engine work; steering/editing *lose* their matched
   comparison; KV wins are cost-shape and need a trained bridge at 8B+; VSA-rule is unreplicated.
2. **The one genuine matched-resource win (memory layers) is factual-recall architecture economics,
   not rule injection** — params-up, trained-from-pretraining. It is the wrong prior for the shallow
   H-RULE placements and the right prior for H-GU/H-RULE-HL.
3. **Where clean wins exist, they are add-capability**: an external deterministic engine owns a class
   of exact reasoning the neural baseline cannot do (Logic-LM; CD+executor). This is the FUSE
   conclusion reproduced: *NeSy beats neural by adding capability, not at matched resources.*
4. For P3-D-RULE this hardens ASM-0806's status as EXTRAPOLATION: an internal-placement
   matched-resource-efficiency win over H-VL would be **above anything in the literature**. Expect
   that null; design so the null is informative and so the *add-capability* value (coverage,
   fail-closed correctness, exact provenance on covered spans) is measured as first-class, not only
   the resource delta.

---

## 5. Implication for P3-D-RULE

`[speculative — design projection; ASM-0806 is its resolver]`

1. **Frame the value as add-capability correctness, not matched-resource efficiency.** The literature
   gives no precedent for an internal rule-injection placement winning on matched resources, and the
   composition wall predicts failure for composition-requiring placements. Build and price the
   *correctness/coverage/fail-closed* value-add explicitly (the F1-K thesis), and treat a
   resource-parity loss as expected rather than disqualifying — the Pareto endpoint (§3.3) already
   permits accuracy/coverage/latency-variance wins at equal cost.
2. **Lead with CD+executor and KV-of-derived-facts** (the two placements where the host does no rule
   composition), per the literature's own ordering, not merely cheapest-first. Retain KV-of-rule-
   premises and AD-of-rules as pre-registered **falsifiers** of the composition prior, with their
   predicted failure modes stated in advance.
3. **Adopt the CD design template:** completion-engine formalization (Synchromesh) as the interface
   spec (prefix-soundness, continuation-completeness); span-scoped constraining with free reasoning
   tokens (CRANE) + backtracking on engine rejection (IterGen); and three pre-registered controls — a
   GAD-style likelihood-distortion audit, a format-tax control arm (unconstrained + post-hoc engine
   check), and the **build** of the empty-cell coverage-aware abstention-preserving mask.
4. **Enforce KOT-COST/2 + lifecycle accounting on every arm** — full resource vector (generated
   tokens, accelerator + CPU time, p50/p95 latency, energy, backtracking count, executor/monitor
   work) AND any trained-bridge/projection/adapter training budget; same-host ablations are NOT
   "matched compute." Compare against H-VL **and** the neural/RAG frontier, not just the
   unconstrained twin.
5. **Freeze the §3 causal-evidence bar** as instrumentation: provenance claims graded per span type
   (uniquely-determined / multi-valid / uncovered); no attention map or unit-naming accepted as
   provenance; interchange/derangement controls on KV; cross-seed stability + dormant-pathway
   controls on ACT.
6. **Budget for being first** where cells are empty (content-level KV ≤2B; coverage-aware abstention
   CD; KV-of-rules with causal validation) — the good kind of risk, but it must be built, and a null
   pre-registered as informative.
7. **VSA-rule and steering enter only as replication-shaped bets** with nsk1-grade derangement/
   integration controls, never as primary lanes; the matched-condition steering evidence is
   predominantly negative at our band.

---

## 6. Citation-verification table

Load-bearing citations re-verified at their primary sources **this session (2026-07-19)** unless
marked otherwise. "Verify result" = whether the source supports the draft's load-bearing use.

| Source id | Claim (load-bearing use) | Status | Verify result |
|---|---|---|---|
| vsa-rule-2025 | 88.6% lower CE, 15.4× more math problems solved vs CoT/LoRA | `[search: 2026-07-19]` ACL Anthology **+ arXiv 2502.01657** | **VERIFIED at both.** Numbers agree at both sources now (draft's "arXiv differs" caution is stale — see Divergences). Host size unstated in abstract (draft-correct). |
| memory-layers-2024 | beats dense >2× compute; beats MoE at matched compute+params; 128B mem params/1T tok/≤8B base; factual gains | `[search: 2026-07-19]` arXiv 2412.09764 | **VERIFIED exactly.** The crux matched-resource candidate; confirmed factual-recall + params-up architecture. |
| mgd-2023 | SantaCoder-1.1B + MGD > text-davinci-003 (compile rate, next-id match); static analysis; consistent across scales | `[search: 2026-07-19]` arXiv 2306.10763 | **VERIFIED.** No exact figures in abstract; draft quotes same-model form only (correct). |
| crane-2025 | ≤10pp on GSM-Symbolic/FOLIO; emits MORE tokens than CoT (Table 1) | `[search: 2026-07-19]` arXiv 2502.09061 abstract + HTML Table 1 | **VERIFIED incl. token counts** (128.97→131.3; 212.24→235.78; acc 26→31%, 24→29%). |
| axbench-2025 | prompting > all steering methods > finetuning; SAEs not competitive; Gemma-2-2B/9B | `[search: 2026-07-19]` arXiv 2501.17148 | **VERIFIED exactly.** |
| kblam-2025 | KB triples→KV via encoders+linear adapters; >10K triples into 8B on 1×A100; linear scaling; interpretable insights | `[search: 2026-07-19]` arXiv 2410.10450 | **VERIFIED.** "Attention-weights" specific wording is from the MSR blog (cited separately) — draft attributes correctly. |
| atlaskv-2026 | ~1B triples <20GB VRAM; KG2KV+HiKVP; sub-linear; no retriever/retrain | `[search: 2026-07-19]` arXiv 2510.17934 | **VERIFIED exactly.** |
| cache-steering-2025 | training-free one-shot KV-cache write; multi-step reasoning in small models; teacher (GPT-4o) traces; lower latency | `[search: 2026-07-19]` arXiv 2507.08799 | **VERIFIED.** Behaviour-level, teacher-distilled (not engine) — draft-correct. |
| logic-lm-2023 | +39.2% over prompting, +18.4% over CoT across 5 datasets; translate→solver→self-refine | `[search: 2026-07-19]` arXiv 2305.12295 | **VERIFIED exactly.** The add-capability archetype. |
| type-constrained-2025 | compile errors −½; functional correctness up across sizes/families | `[search: 2026-07-19]` **arXiv 2504.09246** (ACM DOI paywalled/403) | **VERIFIED** at arXiv (incl. ">30B" models). Provenance divergence — see below. |
| physics-3.2-2024 | storage ≠ manipulation; classify/compare fail without CoT; inverse search ~0% | `[search: 2026-07-19]` arXiv 2309.14402 | **VERIFIED exactly.** |
| cot-depth-theory-2023 | bounded-depth can't do arithmetic without super-poly size; constant size suffices WITH CoT | `[search: 2026-07-19]` arXiv 2305.15408 | **VERIFIED exactly** (NeurIPS 2023 oral). |
| ripple-2024 | parametric editors fail ripple; in-context baseline best on RippleEdits | `[search: 2026-07-19]` arXiv 2307.12976 | **VERIFIED exactly** (TACL 2024). |
| steering-off-course-2025 | 36 models/14 families/1.5B–70B; no improvement or degradation; "fundamental flaws" | `[search: 2026-07-19]` arXiv 2504.04635 | **VERIFIED exactly.** |
| eg-decoding-2018, synchromesh-2022, itergen-2025, syncode-2024, xgrammar-2025, gad-2024, format-tax-2024, cd-alignment-tax-2026, iti-2023, caa-2024, memit-2023, alphaedit-2025, hase-localization-2023, editing-scale-2024, gekhman-2024, ovadia-ft-vs-rag-2024, prag-2026, larimar-2024, grokked-2024, hopping-2024, reversal-2024, twohop-2025, attention-not-expl-2019, attention-not-not-2019, patching-best-2024, hydra-2023, subspace-illusion-2023, causal-abstraction-2025, cbm-2020, cbm-leakage-2021, cbllm-2025, function-vectors-2024, steering-genrel-2024, steering-eval-2024, steering-unreliability-2025, atlas-steer-2026, k-adapter-2020, plugplay-injection-2023, task-arithmetic-2023, lorahub-2024, meki-2026 | supporting / lineage anchors | `[prior-verified: 2026-07-11]` (`verified:true` in ledger) | Accepted without re-fetch; abstract-level uncontested anchors. Not re-checked this pass. |
| picard-2021, knnlm-2020, memorizing-transformers-2022, actadd-2023, repe-2023, causal-scrubbing-2022, knn-lm-note-dedup | lineage / carried anchors | `[UNVERIFIED]` (`verified:false` in ledger, flagged UNVERIFIED-THIS-PASS in draft) | Not re-fetched; carried as UNVERIFIED. None is a standalone load-bearing positive. |

**Tally:** 14 load-bearing citations re-verified at source this session; **0 load-bearing failures**;
1 stale-caution retirement (VSA-rule) and 1 provenance divergence (type-constrained URL). The
remaining ~44 ledger anchors are accepted at the draft's 07-11 `verified:true` status (abstract-level,
uncontested) and 7 are carried UNVERIFIED (none load-bearing).

---

## 7. Divergences from the Fable draft (`docs/next/lit/RULE.md`)

All minor; none overturns a finding. Listed for the coordinator.

1. **VSA-rule arXiv/Anthology reconciliation — a stale caution the draft can retire.** The draft
   pins the 88.6%/15.4× figures to the ACL Anthology "because the arXiv 2502.01657 page is mutable
   and its current abstract reports different numbers." As of **2026-07-19 the arXiv 2502.01657
   abstract now matches the Anthology exactly** (88.6% lower cross-entropy, 15.4× more problems, vs
   CoT and LoRA). The Anthology pin remains good practice (immutable proceedings record), but the
   "arXiv differs" rationale is no longer true and should be updated to "arXiv and Anthology agree as
   of 2026-07-19." `[search: 2026-07-19]`
2. **type-constrained-2025 — verifiable via arXiv, not the paywalled ACM DOI.** The ledger's only URL
   is the ACM DOI (`10.1145/3729274`), which returns **HTTP 403** to WebFetch. The claim
   (compile errors −½; correctness up across sizes/families incl. >30B) **verifies cleanly at
   arXiv 2504.09246**, the open-access version (PLDI 2025; eth-sri reproduction package exists).
   Recommend adding the arXiv URL to the ledger so the load-bearing row is source-checkable without a
   subscription. `[search: 2026-07-19]`
3. **KBLaM "attention weights" attribution — already handled, noted for completeness.** The
   paper *abstract* says "interpretable insights into its use of the augmented knowledge"; the
   specific "attention weights ... mimicking a soft retrieval process" wording is the MSR **blog**.
   The draft cites these to separate ids (`kblam-2025` vs `kblam-msr-blog-2025`) and attributes each
   correctly — no error, but the distinction is load-bearing for the §6 "attention ≠ provenance"
   argument and is worth keeping explicit. `[search: 2026-07-19]`
4. **No Sardana/TinyAgent-class numeric error found.** The sibling passes caught a Sardana $-figure
   error (elsewhere) and a TinyAgent 40k-vs-80K error (elsewhere); the equivalent high-risk numeric
   claims here (VSA-rule 15.4×, CRANE token counts, memory-layers matched-params claim, MGD
   1.1B>175B-class) **all verify at source**. The draft's numeric discipline on the RULE ledger held.

---

## 8. What this review settles, and what it leaves open

**Settled (evidence class stated):**
- CD → KV-of-derived-facts is the literature's ordering, not merely cheapest-first (the composition
  wall is the independent argument) `[established prior + speculative synthesis]`.
- No rule-injection placement beats a matched-resource neural baseline in the verified record; the
  only matched-resource win (memory layers) is factual-recall architecture economics, params-up
  `[established]`. **This concurs with FUSE (#57).**
- Attention ≠ provenance; the §3 threat/control table is ready to freeze `[established]`.
- Steering and editing lose their matched comparisons (prompting; in-context) at our band
  `[established]`.

**Open for Phase-1 (P3-D-RULE must answer in design):**
- The abstention-preserving selective-span CD cell is empty — free-decode+fail-closed post-check vs
  refusal-token insertion; both designable, neither has prior art.
- Whether engine-derived masking distorts the within-valid-set distribution enough to matter (GAD
  audit).
- Whether the kot-axiom engine can discharge Synchromesh's completion-engine obligations
  (prefix-soundness, continuation-completeness) at µs/token cost, per-token, with backtracking (an
  engineering measurement, NOT extrapolable from XGrammar's grammar-transport number).
- Whether KV-of-derived-facts works at ≤2B and its trained-projection budget under KOT-COST/2.
- The Pareto-endpoint operationalization that lets CD/KV be compared to H-VL on formal legs before
  NLB clears (NL legs NLB-gated, ASM-0814).
- A replication spec for VSA-rule at our rung with nsk1-grade controls.

**Consistency link:** nothing here contradicts `docs/next/feasibility-synthesis.md` (external loop =
the only measured end-task positive) or `reports/lit-p3-fuse.md` (matched-resource null on fusion);
this review reproduces the FUSE steering signal on the RULE pathway and equips P3-E-RULE-1 to test
the add-capability value rather than assume a matched-resource win.
