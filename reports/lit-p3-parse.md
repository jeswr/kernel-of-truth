# P3-LR-PARSE — Semantic parsing, program synthesis, grammar induction, uncertainty + selective prediction (formalized)

**Bead:** P3-LR-PARSE (Programme-3, Phase-0 [LIT]).
**Deliverable path:** `reports/lit-p3-parse.md`.
**Author/role:** literature-review agent (Opus execution), independent source-verification pass.
**Date:** 2026-07-19. **Status:** DRAFT for coordinator review. Nothing here is frozen,
registered, or scheduled; no registry record / ASM / KB shard is touched; no bd/git operations.
**Parent:** `docs/next/programme-3-neurosymbolic-architecture.md` (rev 2) §3.3a (H-PS NL→program
synthesis), §3.1 (H-VL verifier loop), §5 table row P3-LR-PARSE, ASM-0814/0815.
**Feeds:** **P3-D-NLB** (schedule-critical: gates every natural-input store leg, ASM-0814),
**P3-D-PS** (co, with P3-LR-NTP), **P3-D-ORACLE** (co).

> **Relationship to `docs/next/lit/PARSE.md`.** A prior, careful PARSE review exists (Fable,
> 2026-07-11, bead …s55r.5, with source ledger `PARSE.sources.jsonl`, 43 entries). **This report
> is not a redo.** It is (a) an independent re-verification of the draft's load-bearing citations
> at their primary sources this session, (b) an explicit divergence log, and (c) a formalization at
> the requested `reports/` path, epistemic-tagged and refreshed to 2026-07-19. **Headline of the
> verification pass: every load-bearing number in the draft holds at source.** I re-verified 32 of
> the 43 sources at primary venue this session, including all numerically load-bearing claims; I
> found **one genuine numeric divergence** (TeCoD "+36 points" vs the abstract's "up to 36%
> higher" — a points-vs-percent over-precision; § Divergences) and two minor provenance nuances.
> I **upgraded STaR-SQL** from the draft's `verified:false` (KB-recall) to source-verified
> (86.6% EX Spider confirmed). The draft's central verdicts — capability-limited-is-leading for the
> dominant failure classes, and the selective-prediction contract for the S2 gate — survive
> verification unchanged.

## Epistemic tag convention

- `[established]` — external empirical/methodological fact confirmed at a primary source this
  session or prior. `[claimed]` — asserted in a source but single-source, abstract-only, or new
  benchmark not independently corroborated. `[speculative]` — my forward inference / design judgement.
- Provenance suffix: `[search: 2026-07-19]` = re-verified at source via WebFetch this session;
  `[prior-verified: 2026-07-11]` = verified at source in the 07-11 PARSE.md, accepted here without
  re-fetch (uncontested abstract-level anchor); `[memory]` = from the parent doc / in-repo verdicts,
  not a literature source. `[UNVERIFIED]` = could not confirm at primary source this session.
- Measurement register (inherited): a "MEASURED" number below is the *authors'* published
  measurement inside that paper's own envelope — never *our* measurement, never a premise for a KoT
  verdict. In-repo verdicts (l3a-parse, a5-nl, f2b, g2d, nsk1) are tagged `[memory]` and cited as the
  measured failure this review interprets, not as literature.

---

## Top findings (read this first)

1. **THE CRUX — does execution-feedback program synthesis (H-PS) beat a matched-resource neural
   baseline, or is its win an add-capability win? Honest answer: it is an ADD-CAPABILITY win, and a
   cleaner one than the GNN-fusion case P3-LR-FUSE audited.** `[established][search: 2026-07-19]`
   Every execution-feedback result re-verified this session — EGD (83.8% WikiSQL, 4 architectures),
   MBR-EXEC (execution-agreement selection beats all execution-unaware selectors), LEVER
   (+4.6–10.9% over code-davinci-002, then-SOTA on 4 benchmarks), TinyGSM (1.3B+1.3B → 81.5%
   GSM8K, above the GPT-3.5 teacher's 77.4% and the prior 34B floor) — wins by giving the system an
   **executor the neural baseline structurally lacks** (exact, sound execution + a checkable result).
   None is a *matched-resource* win under full accounting: TinyGSM is teacher-data-unmatched (12.3M
   GPT-3.5-synthesized problems) AND executor-added AND verifier-sampling-unmatched; LEVER adds a
   *trained verifier* over execution results plus k× sampling; MBR-EXEC/EGD add the executor itself.
   This is **exactly the FUSE conclusion** (`reports/lit-p3-fuse.md` §3 pt 5): no neurosymbolic
   system in this sweep beats a matched-resource neural baseline at the same task+information; the
   demonstrated wins come from **adding an exact-reasoning/execution capability** — which is the
   programme's **correctness thesis** (a deterministic fail-closed checker priced against its own
   falsifier), *not* the efficiency thesis. **The difference from FUSE, in H-PS's favour:** the GNN
   "structure win" was *confounded and twice undercut* by perturbation probes (couldn't even
   establish the structure was used); H-PS's added capability — the deterministic µs engine — is
   **architecturally explicit and its contribution cleanly attributable**, with no "is it really
   using the executor?" confound. H-PS should therefore be argued and priced on the **correctness
   axis**; a matched-resource efficiency win for it is **not demonstrated by the parsing/synthesis
   literature and must not be assumed** (§3, §7).

2. **The one genuinely matched-resource sub-win is grammar/constrained decoding — and it buys
   validity, not correctness.** `[established][search: 2026-07-19]` Constrained decoding (GCD-geng:
   grammar-constrained LMs "substantially outperform unconstrained LMs or even beat task-specific
   finetuned models" on IE/ED/parsing where data is scarce; PICARD; XGrammar near-zero serving
   overhead) is **compute-matched by construction** — same model, masked softmax. It is the cleanest
   matched win in the review. But it only removes *invalid-language* outputs; it cannot catch a
   **semantically valid-but-wrong** program. The a5-nl dangerous class (a direction-flipped query)
   executes perfectly and satisfies every output grammar — so **neither constrained decoding nor
   the executor closes the S2 gate**. That budget is carried by the parser + deterministic ROLE_DIR
   repair + calibrated abstention, layered (§3, §5c/e).

3. **The measured l3a-parse / a5-nl failures are, on the leading hypothesis, CAPABILITY-LIMITED —
   the literature repairs their dominant classes most reliably, and the one dangerous class was a
   deterministic table bug.** `[established (lit) / memory (verdicts)][search: 2026-07-19]` The
   0.0% paraphrase stratum (l3a-parse 0/261) is a **floor artifact of a verbatim, no-learning
   front-end** — the exact class the field measured and moved past in 2014–2018 (Berant & Liang
   canonical-utterance paraphrasing; Shin constrained few-shot). The a5-nl S2 kill was a
   **deterministic hand-coded ROLE_DIR lookup defect** ("what contains X" vs "what X contains" bound
   to the wrong valid operation) with a targeted deterministic repair already named in the assessment
   `[memory]`. **Nothing in the measurement licenses "fundamental."** Two residues are genuine:
   (c) the *learned-parser analog* of role/direction binding stays brittle under compositional shift
   with current techniques (COGS 96–99% ID → 16–35% comp-split; CFQ strong negative
   compound-divergence/accuracy correlation; Qiu et al. flat-or-negative fine-tuning scaling to 11B —
   **explicitly framed by the authors as "limitations of current techniques," not an impossibility**),
   and (d) ambiguity/underspecification is **FUNDAMENTAL** (a property of NL: AmP, DTE, TriageSQL) —
   where the correct output is calibrated abstention, not a parse.

4. **Selective prediction supplies the missing S2 contract — with a verified, load-bearing caveat
   that bites exactly the ROLE_DIR class.** `[established][search: 2026-07-19]` Risk-controlled
   selective classification (Geifman: set a desired risk, reject to guarantee it w.h.p. — "2% top-5
   ImageNet error … with probability 99.9%, and almost 60% test coverage") + trained calibrators that
   beat softmax under shift (Kamath: 56% answered at 80% acc vs 48%) + conformal abstention with a
   distribution-free error-rate bound (conformal-abstention-2024) are the instrument shape the NLB
   gate needs. **BUT** I verified at the paper body that conformal abstention's self-consistency match
   score "**clearly cannot detect situations where the LLM is completely sure about an incorrect
   answer**" — the systematic confident-inversion case — and that the guarantee **assumes
   exchangeability** with the calibration set (verified in §2 of the paper). A K=1 agent-authored
   phrasing distribution silently voids that bound. **Do not** lean on two-model deliberation for
   this either (PVD's ~30pp confidence-precision signal **collapses or inverts** when the verifier is
   weak/OOD — verified verbatim). Recommendations for P3-D-NLB in §4.

5. **The programme gate is PLAUSIBLE-BUT-UNRESOLVED at small scale.** `[speculative — the review's
   exit claim]` No cited work reports **0.90 retention jointly with an S2-style confidence bound for
   a ≤360M parser on a closed grammar like kot-query/1**. TeCoD is the closest published shape
   (closed template family + constrained decode + fine-tuned selector) and it **APPROACHES but does
   not demonstrably clear** the bar on its matched slice and reports **no** confidence bound. So the
   net judgement — capability-limited-is-leading — is a **testable hypothesis P3-D-NLB must resolve
   as a parser+abstention SYSTEM whose risk-coverage curve is the measured product**, not a
   literature-settled conclusion.

---

## 1. The measured failure, restated, and its literature class

What actually failed `[memory: registry/verdicts/{l3a-parse,a5-nl}.json + assessments/a5-nl.json]`:

- The a1-hybrid front-end is **deterministic and training-free**: one entity/identifier gazetteer +
  one frozen frame rule set, single-label verbatim concept mapper, ~250–267 µs/query.
- **l3a-parse** (family/world): 47.6% retention; label-verbatim stratum 76.4% but **paraphrase
  stratum 0/261 = 0.0%** (no synonym table); stage breakdown frame-miss 228, mapper-abstain 48,
  gazetteer-miss 40, frame-ambiguous 41. Failure mode SAFE (mis-parse → refusal; S2 did not fire).
- **a5-nl** (code): 41.6% retention (frame-miss 468 / gazetteer-miss 24) AND the S2 kill fired: the
  frame ROLE_DIR direction table **flips containment orientation** into real-but-wrong answers with
  provenance (5.0% ≥ the 2% bar). Mechanism precisely: a **deterministic hand-coded lookup defect**,
  with a targeted deterministic repair (fail-closed on ambiguous orientation) already proposed in the
  assessment.

Literature mapping `[STIPULATED — organizes §5]`:

| our stage | literature name | canonical instruments (all V@src this session unless noted) |
|---|---|---|
| frame-miss (paraphrase) | lexical/paraphrase gap of rule/template parsers | berant-liang-2014, spider-syn-2021, drspider-2023 |
| gazetteer-miss | schema/entity linking | nl2sql-survey-2025, spider-syn-2021, genre-2021 [carried] |
| frame-ambiguous | NL ambiguity/underspecification | amp-2024, dte-2023, triagesql-2020 |
| ROLE_DIR flip (dangerous) | MEASURED deterministic direction-table defect; learned-parser ANALOG only: role/argument generalization | `[memory: a5-nl]`; cogs-2020, cfq-2020, qiu-scale-2022 |
| mapper-abstain | out-of-lexicon abstention (correct behaviour) | selective-prediction frame, §4 |

**Direction-only reading** `[speculative — from the MEASURED l3a stage breakdown + berant-liang-2014;
never a premise]`: the 0.0% paraphrase stratum is a **floor artifact of the no-learning front-end**,
not a measurement of what parsing can do. The same sentence class that kills a verbatim matcher is the
*bread-and-butter positive case* of every learned parser since 2014. This is the single most
decision-relevant sentence for P3-D-NLB — and P3-E-NLB-1 is what tests it.

---

## 2. SQ1 — semantic parsing into executable forms at SMALL model scale

**The proven recipe at 110M–3B: fine-tuned seq2seq (or intent+slot) parser + grammar-constrained
decoding + execution-aware selection.** Smallest-first, with metric discipline:

- **110M (BERT-base), closed intent+slot grammars.** `[established][search: 2026-07-19]` Joint
  intent+slot fine-tuning improves sentence-level semantic-frame accuracy. **Verified at the results
  table (Table 2):** the oft-quoted ~96–97% figures are **intent accuracy (97.5% ATIS / 98.6% Snips)
  and slot F1 (96.1% / 97.0%)** — NOT whole-frame exactness. The **exactness-shaped metric,
  sentence-level semantic-frame accuracy, is 88.2% (ATIS) / 92.8% (Snips)** — i.e. **below the 0.90
  bar on one of the two benchmarks.** kot-query/1's 7 shape-recoverable families + gazetteer slots
  are structurally an intent+slot task `[STIPULATED mapping; sets the difficulty prior]`.
- **220M–3B, open cross-domain SQL.** `[established][search: 2026-07-19]` PICARD (incremental
  parse-constrained decoding on fine-tuned T5, then-SOTA Spider/CoSQL) `[prior-verified: 2026-07-11]`;
  **CodeS** (open **1B–15B** models, SQL-centric incremental pretraining + schema-linking + bidirectional
  augmentation reach "**new SOTA accuracy and robustness on nearly all challenging** … benchmarks"
  — Spider/BIRD/Spider-Syn/-Realistic/-DK/Dr.Spider — "**at much smaller parameter sizes**" than
  GPT-4 pipelines; SIGMOD 2024, **V@src**); STaR-SQL (self-taught reasoning traces, **86.6% EX
  Spider**, +31.6 over few-shot / +18.0 over direct fine-tune — **V@src this session; upgraded from
  the draft's `verified:false`**).
- **The closed/recurring-grammar special case (ours).** `[established (headline) / body-level (BIRD)]
  [search: 2026-07-19]` **TeCoD** mines NL→SQL templates, fine-tunes an NLI-based template
  selector, and enforces the template by grammar-constrained decoding: headline "**up to 36% higher
  execution accuracy than in-context learning**" and "**2.2× lower latency on matched queries**"
  (abstract, V@src; PACMMOD vol 3(6) 2025). The **83.6–89.2% matched-BIRD** range is body-level and
  **not confirmable at abstract level** — kept as body-level, do NOT round to "at the 0.90 bar."
  **This is the closest published shape to the NLB gate** (closed template family + constrained decode
  + classifier) — it APPROACHES but does not demonstrably clear 0.90 on its matched slice and reports
  **no S2-style confidence bound.** Plausibility evidence for the recipe, not gate feasibility.
- **Few-shot, data-scarce fallback.** Constrained canonical-utterance parsing (Shin
  `[prior-verified]`); grammar prompting for DSLs (predict a minimal BNF, then constrain
  `[prior-verified]`). Near-zero training cost if NLB must stay training-free.
- **Difficulty perspective.** Open cross-domain text-to-SQL is HARD: best 2018 model **12.4% exact**
  on Spider's DB split (V@src: 10,181 Q / 5,693 SQL / 200 DBs / 138 domains); **ChatGPT 40.08% vs
  human 92.96%** execution accuracy on realistic BIRD databases (V@src). Our envelope is the opposite
  corner: closed grammar, fixed tiny schema, recurring shapes — the corner where the numbers are
  highest `[speculative, direction-only]`.

**LOAD-BEARING for P3-D-NLB sizing:** nothing in this record supports 0.90+ retention from a
**zero-learning** front-end under held-out phrasing; everything clearing 0.85+ under paraphrase has a
learned component (fine-tuned parser, learned selector, or synonym resources)
`[speculative over the §2 record + §1's measured floor]`.

**2b. Accounting skepticism (what "beat" means).** `[speculative — direction-only]`
- Constrained-decoding wins are **compute-matched by construction** (XGrammar near-zero serving
  overhead `[carried]`) — the cleanest wins here.
- Fine-tuned-small > few-shot-giant (CodeS, TeCoD, STaR-SQL) is **inference-matched but
  training-unmatched** — admissible only with tuning compute in the KOT-LIFE ledger `[per programme §2]`.
- Execution/verifier wins spend k× sampling; honest comparisons hold k fixed vs self-consistency —
  LEVER reports against sampling baselines; TinyGSM's 81.5% is **teacher-data-unmatched** (12.3M
  GPT-3.5-synthesized problems).
- BAR-SQL-class "beats GPT-5/Claude 4.5 Sonnet" is **single-group on a self-built benchmark**
  (Ent-SQL-Bench, 91.48% avg — V@src) — adopt the *shape* (abstention in the reward), not the numbers.

---

## 3. SQ2 — NL→DSL / program synthesis WITH execution feedback (the CRUX section)

(Decoder-side grammar machinery is owned by `reports/lit-structured-parsing-and-inner-symbolic.md`;
here: what the executor buys, its precise limit, and the matched-resource audit.)

**What the executor buys, re-verified:**
- **Execution-guided decoding** (condition decoding on execution of partial programs): "universally
  improves" 4 architectures on WikiSQL/ATIS/GeoQuery; **83.8% EX WikiSQL** (EGD, V@src). With a µs
  deterministic engine, partial-execution pruning is effectively free for us `[speculative]`.
- **Execution-based selection:** MBR-EXEC — MBR decoding over execution-result agreement on test
  inputs "significantly outperforms the methods that do not involve program semantics" (V@src).
  Precise limit: agreement over a SMALL test-input set approximates semantic equivalence; the vote can
  select a majority cluster of **spurious (consistently-wrong)** programs — a **selector, not a
  correctness check**.
- **Learned verification over execution results:** LEVER — a trained verifier reads (NL, program,
  execution result) and rescores: **+4.6–10.9% over code-davinci-002 across 4 benchmarks**, then-SOTA
  (V@src). The host was frontier-scale; small-host transfer is an open cell — but **f2b-replicate is
  OUR measured small-host analog** of this verifier-rescoring shape `[memory: +0.1507,
  alignment-specific, formal inputs only]`.
- **The small-scale existence analogy:** TinyGSM — 1.3B generator + 1.3B verifier emitting **executed**
  Python: **81.5% GSM8K**, above the GPT-3.5 teacher (77.4%) and the prior 34B floor (V@src).

**The matched-resource audit (the bead's central skeptical question).** `[speculative — direction-only
audit over the V@src numbers; the "matched?" reading is mine]`

| Headline | Baseline it beat | Matched? | NOT matched | Add-capability? |
|---|---|---|---|---|
| EGD 83.8% WikiSQL | same architectures w/o exec guidance | model, task data | +an executor | **yes — the executor** |
| MBR-EXEC > all non-exec selectors | non-execution selection at same k samples | **sampling k, model** | +the executor to run candidates | executor added; but **selection is matched at fixed k** |
| LEVER +4.6–10.9% | code-davinci-002 sampling | task data | +trained verifier params, +k sampling, +executor | **yes — executor + trained verifier** |
| TinyGSM 81.5% > GPT-3.5 77.4% | GPT-3.5 (34B-floor prior) | — | **teacher-data-unmatched (12.3M synth), +verifier, +executor, single domain** | **yes — and heavily data-unmatched** |
| GCD-geng > fine-tuned models | unconstrained / fine-tuned LM | **model, compute (masked softmax)** | none | **no — validity only, not a capability** |

**Audit verdict** `[speculative — this purposive sweep, not a systematic search]`:

1. **No execution-feedback result in this sweep beats a matched-resource neural baseline under full
   accounting** (same information, same trainable params, same sampling budget, no added executor).
   Where the executor is the differentiator (EGD/MBR-EXEC/LEVER/TinyGSM), the win is an
   **add-capability win**; where the comparison is genuinely matched (constrained decoding), the win
   is **validity, not semantic correctness**. **This is the crux answer, and it is "add-capability,
   not matched-resource."**
2. **This is the same structure P3-LR-FUSE found** — and locates H-PS's defensible value on the
   programme's **correctness thesis** (a deterministic fail-closed executor/checker priced against its
   own falsifier), not the efficiency thesis. The one clean *matched* lever (constrained decoding) is
   real but narrow (output-language conformance).
3. **H-PS is a cleaner add-capability bet than H-GNN-fusion.** FUSE's "structure win" was *confounded*
   (Deceive-KG, GTEval PRBCD showed models reading text, not structure). H-PS's added capability —
   the µs engine — is **architecturally explicit** and its contribution is cleanly attributable: a
   valid-but-wrong program executes perfectly (so the executor's *reach* is unambiguous), and its
   provenance is the engine's derivation, not an attention map.
4. **The limit that bounds even the add-capability win (decisive for a5-nl):** execution feedback
   catches *invalid/failing* programs, NOT *valid-but-wrong* ones. A direction-flipped kot-query
   executes perfectly and returns a well-formed wrong answer with provenance — exactly the DTE class
   ("plausible SQL for ambiguous/unanswerable questions" — V@src) that BIRD's 40% vs 93% human gap
   quantifies. **Execution feedback is necessary-cheap but nowhere near sufficient for the S2 gate,
   and is NOT a mitigation for the ROLE_DIR class at all** `[STIPULATED design law for P3-D-PS]`.
5. **Matched-inference honesty for TinyGSM as an H-PS analogy** `[LOAD-BEARING for P3-D-PS]`: it is
   an EXISTENCE ANALOGY for the pipeline shape (NL → program → execute → verify/select → answer from
   checked result) at 1.3B — **NOT a matched H-PS demonstration.** Its 12.3M GPT-3.5-synthesized
   corpus, single domain (grade-school math), executable-Python target, sampled verifier selection,
   and **trivial numeral rendering** all differ materially from KOT parsing + surface generation — and
   **our generation leg is nsk1-g2d-cautioned** `[memory: g2d text-append net-harmful]`.

---

## 4. SQ3+SQ4 — grammar machinery (delta only) and calibrated abstention / selective prediction

**Grammar-constrained decoding, 2025–26 delta over the prior review:** `[established][search: 2026-07-19]`
- GCD without finetuning "substantially outperform[s] unconstrained LMs or even beat[s] task-specific
  finetuned models" on IE/entity-disambiguation/constituency-parsing — the cheapest accuracy lever
  where data is scarce (gcd-geng-2023, V@src).
- **Scope caveat (verified):** locally-masked constrained decoding is **biased sampling** relative to
  the true grammar-conditioned distribution — P-GCD (V@src: Dang, Song, H. Zhang, J. Zhao, Van den
  Broeck, Ermon) studies this over finite-automaton constraint classes and corrects it with SMC-style
  tractable proposals (function-calling / SQL); GAD documents the same greedy-masking distortion
  `[carried]`. **Neither shows ordinary local constrained decoding is unsafe or task-incorrect in
  general, nor that global decoding is cheap for an arbitrary grammar** — these are
  distributional-fidelity results on the constraint classes studied. Design note (project-local):
  kot-query is closed and tiny, so it should be cheap to CHECK a local-mask decoder against an exact
  global mask on our grammar and quantify divergence before freezing — feasibility/cost established in
  P3-D-NLB, not assumed `[speculative]`.
- **Grammar induction** (the bead's named sub-question): our grammar is known and closed, so
  induction is NOT needed for the target side. Its two proven parser-relevant uses (V@src): (i) induce
  a quasi-synchronous grammar over training pairs → recombine → augmentation that transfers
  compositional robustness into a fine-tuned T5 (CSL — "even stronger than a T5-CSL ensemble on two
  real-world compositional-generalization tasks"); (ii) few-shot explicit rule-system synthesis beats
  neural meta-learning when the mapping is genuinely rule-like (Nye — SCAN + number-word translation).
  **Use (i) to manufacture paraphrase training data for NLB** `[STIPULATED recommendation]`.

**Selective prediction — the frame the NLB gate instrument should adopt.** `[established][search: 2026-07-19]`
This is the section that feeds P3-D-NLB directly. Recommendations, each source-anchored:

- **R1 — report the whole risk-coverage curve + AUACC, then FREEZE an operating threshold.**
  Foundations: risk-coverage trade-off and near-optimal reject strategies (El-Yaniv & Wiener 2010,
  JMLR `[prior-verified]`); **risk-CONTROLLED** selection — set a desired risk, reject to guarantee it
  w.h.p. (Geifman: "2% top-5 ImageNet error … probability 99.9%, almost 60% coverage" — V@src). The
  NLB gate ("retention ≥0.90 with S2 ≤2% dangerous-wrong") **is a point on a risk-coverage curve** —
  the instrument reports the whole curve, not a scalar.
- **R2 — train the calibrator under the shift you will face; raw confidence is not enough.** Kamath:
  a trained calibrator answers **56% at 80% accuracy vs 48% for softmax under domain shift** (V@src).
  Parser-specific: calibration of semantic parsers **varies by model and dataset**, with a
  calibration-metric library + confidence-based challenge splits available (calibrated-interpretation-2023, V@src).
- **R3 — selective prediction is trainable into a host** (PEFT + self-evaluation lifts AUACC/AUROC:
  ASPIRE CoQA AUACC 91.23→92.63, AUROC 74.61→80.25 — V@src). 2026 variants train abstention directly
  into the parser's RL reward (BAR-SQL — adopt the shape, not the single-group numbers).
- **R4 — conformal methods give the S2-shaped guarantee, WITH two verified caveats that are
  load-bearing, not footnotes.** Conformal abstention bounds the error/hallucination rate with rigorous
  guarantees while abstaining less than log-prob baselines (V@src); Conformal LM returns calibrated
  generation sets with coverage guarantees (V@src). **Caveat 4a (verified at the paper body):** the
  self-consistency match score "**clearly cannot detect situations where the LLM is completely sure
  about an incorrect answer**" — **exactly the systematic ROLE_DIR-inversion case.** Abstention reduces
  those only if the chosen score actually separates them, which P3-D-NLB must **measure, not assume**.
  **Caveat 4b (verified at §2):** the guarantee holds only under **exchangeability** with the
  calibration set — a paraphrase-distribution shift (exactly what K=1 agent-authored phrasings vs real
  users is) silently voids the bound. **Requirement:** calibrate and evaluate on *disjoint phrasing
  sources* and stress the threshold under Dr.Spider-style perturbation `[STIPULATED for P3-D-NLB]`.
- **R5 — do NOT extract confidence from two-small-model deliberation.** PVD's ~30pp
  high-confidence-precision signal **collapses or inverts when the verifier is weak or OOD** (V@src —
  "weaker prover-verifier pairings can collapse or invert the ANC signal") — the small-model pairing
  is precisely that regime.
- **R6 — detecting should-abstain inputs is itself hard.** Cross-domain answerable-vs-unanswerable
  classification sits at **60% F1 for RoBERTa** (TriageSQL, V@src, 4 unanswerable categories);
  ambiguity taxonomies + counterfactual training data help (DTE — 6 categories, "Detecting-Then-
  Explaining" beats baselines, V@src); models represent meaning distributions of ambiguous inputs only
  when ambiguity is **attested** in training/prompt (AmP — 5 ambiguity types, V@src).

---

## 5. SQ5 — WHY NL→formal fails: capability-limited vs fundamental, per class

Judged per class (method: what moved the number, at what scale, under what accounting):

**(a) Lexical/paraphrase gap — CAPABILITY-LIMITED, high confidence.** `[established][search: 2026-07-19]`
Verbatim/rule front-ends have a hard paraphrase ceiling; the field's fix was learned paraphrase
absorption — canonical utterances + paraphrase model (Berant & Liang: "a paraphrase model can absorb a
large portion of the linguistic variation in natural language", V@src), then fine-tuned seq2seq, then
constrained few-shot canonical parsing (Shin). Residual truth: even LEARNED parsers drop dramatically
when explicit NL↔schema lexical correspondence is removed (**Spider-Syn: "accuracy dramatically drops";
synonym annotation recovers more than adversarial training** — V@src), and the most robust model still
loses **14.0% overall / 50.7% worst-perturbation** on Dr.Spider (V@src). **Fixable to ~0.85–0.95 on a
closed grammar, NOT to 1.0**, and only with paraphrase-diverse training + lexicon resources. l3a's
0/261 says nothing beyond "no-learning fails."

**(b) Entity/schema linking (gazetteer-miss) — CAPABILITY-LIMITED.** `[established][search: 2026-07-19]`
A persistent named core difficulty of NL2SQL (survey names NL ambiguity, under-specification, schema
linking — V@src), but on a FIXED tiny schema with a registered lexicon, trie-constrained name emission
+ exact post-mapping (GENRE shape, prior-review idea A3 `[carried]`) plus synonym annotation is the
measured strong recipe.

**(c) Role/direction binding (the a5-nl dangerous class) — MEASURED as a DETERMINISTIC table bug,
directly repairable; the LEARNED-parser analog is currently brittle (a limitation of current
techniques, NOT shown fundamental).** `[memory (defect) + established (lit)][search: 2026-07-19]` What
actually failed: the frozen frame layer's hand-coded ROLE_DIR lookup bound "what contains X" vs "what X
contains" to the wrong (valid) operation — a deterministic table defect, with a targeted deterministic
repair already proposed (fail-closed on ambiguous orientation). **Nothing in that measurement licenses
"fundamental."** The learned-parser ANALOG is where compositional-generalization literature applies:
COGS 96–99% ID vs 16–35% comp-split (±6–8% seed, V@src); CFQ strong negative compound-divergence/accuracy
correlation (V@src); Qiu et al. **flat-or-negative fine-tuning scaling to 11B** on OOD comp-gen (ICL
scales but underperforms much smaller fine-tuned models — V@src), **which the authors explicitly frame
as "limitations of current techniques … [with] promising directions for future work," NOT an
impossibility result** (verified — this framing is load-bearing for the capability-limited judgement).
What has **measurably moved** it: grammar-based data augmentation (CSL, V@src) and explicit rule
synthesis at tiny scale (Nye, V@src). What **CANNOT** catch it: checked execution (§3.4 — valid-and-wrong,
executes perfectly) and self-consistency-style confidence (§4 caveat 4a). **DESIGN LAW for NLB:** (1)
apply the targeted deterministic ROLE_DIR repair **regardless of parser class**; (2) role/direction
correctness must be **adversarially and symmetrically** tested (both orientations of every directional
frame, held-out compositions, per-frame error strata); (3) typed/operator-specific validation +
contrastive inverse tests as independent checks; (4) low-margin directional parses abstain — with the
score's ability to separate systematic inversions itself a **measured quantity**.

**(d) Ambiguity/underspecification — FUNDAMENTAL (property of NL, not of models).** `[established][search: 2026-07-19]`
Ambiguous inputs have meaning DISTRIBUTIONS; models capture them only when attested (AmP); real question
streams contain unanswerable/ambiguous classes parsers happily "answer" (DTE, TriageSQL). No scale fixes
this; the correct product behaviour is calibrated abstention (or clarification), which is why the
abstention policy is PART of the measured NLB system.

**(e) Confident-wrong-with-provenance (S2) — a SYSTEM failure, prevented by LAYERED controls, never by
parser accuracy alone.** `[established (endemic) + speculative (layering)]` The field's parsers exhibit
it endemically (plausible SQL for bad questions — DTE; 40% vs 93% human on BIRD with fluent outputs).
The safety budget is carried by several layers, not abstention alone: fixing deterministic relation
semantics at the source (§5c repair), typed/operator-specific validation, contrastive inverse tests,
independent verification where available — and **then** risk-controlled selection for the residual
(Kamath calibrator; conformal abstention with error-rate bound; abstention-aware reward). The a5-nl
lesson ("wrong-with-provenance is worse than refusal") **is** the field's selective-prediction
motivation, verbatim.

**Net judgement for FK-NLB-3:** **capability-limited is the LEADING HYPOTHESIS at our scope,
empirically unresolved at the programme gate.** `[speculative — the single sentence P3-D-NLB is built
around]` The retention loss is driven ~entirely by classes (a)+(b) — the two the literature repairs
most reliably — and the dangerous class (c) is, as measured, a repairable deterministic defect. But no
cited work reports 0.90-retention jointly with an S2-style confidence bound for a small parser on a
grammar like ours (§7.1), so this is a testable hypothesis P3-D-NLB must resolve, not a settled
conclusion. Classes (d)+(e), plus the learned-parser residue of (c), are why the redesign must keep the
deterministic engine as the **sole answer authority** and treat the parser as an **untrusted proposer
under a risk-controlled gate with layered checks**.

---

## 6. SQ6 — paraphrase robustness: methods that measured `[established][search: 2026-07-19]`

1. **Paraphrase-diverse supervision** — the dominant fix: induced-grammar recombination augmentation
   (CSL, incl. natural-variation splits); bidirectional augmentation inside CodeS's robustness wins.
2. **Canonical-utterance factoring** — parse NL→canonical utterance→(deterministic) form; absorbs
   variation in the NL-NL half where LMs are strongest (Berant & Liang, Shin).
3. **Lexicon/synonym resources at the interface** — schema synonym annotations beat adversarial
   training (Spider-Syn); registered-lexicon trie constraints (GENRE `[carried]`).
4. **Constrained decoding** — removes syntax/validity violations that a CORRECT grammar expresses, at
   low serving overhead; it does NOT remove semantic invalidity, grammar-spec or tokenizer bugs, or
   all serving cost, and carries the local-vs-global mask fidelity caveat (§4).
5. **Evaluation practice (adopt):** multi-perturbation diagnostic suites (Dr.Spider's 17 sets; report
   per-perturbation worst-case, not just aggregate). Our l3a/a5 used **K=1** held-out phrasing per
   query `[memory]` — BELOW field practice; the NLB gate needs **K>1 phrasings from an author source
   disjoint from calibration**, plus a perturbation taxonomy (synonym, structure, typo/ASR-style noise)
   `[STIPULATED for P3-D-NLB]`.

---

## 7. Implication for the design beads (the hand-off)

*(Recommendation only — this bead runs no bd; blockers per programme rev-2 §5.)*

**P3-D-NLB** `[DESIGN, P0, blocked-by: this review — discharged as Phase-0 evidence for PROCEEDING,
not evidence the 0.90/S2 gate is likely to clear]`. **What this review supports:** capability-limited
is the leading hypothesis for the dominant classes (§5a/b, net judgement §5) — do NOT rebuild
deterministic-only; the recipe with the strongest matched-accounting record is fine-tuned-small-parser
(intent+slot or seq2seq, 110M–1B) + grammar-constrained decode (local-vs-global mask divergence checked
on our grammar, §4) + trie/synonym lexicon + trained-calibrator or conformal-abstention threshold frozen
pre-eval (§2, §4); the targeted deterministic ROLE_DIR repair applies regardless of parser class (§5c);
a two-tier µs/ms front-end is the cost shape to design first (§7.3 below). **Gate-instrument
requirements the design MUST specify (the joint 0.90/2% protocol):** (1) define S2 precisely —
unconditional P(answer ∧ wrong) vs selective risk P(wrong | answered): the cited literature uses both
and they diverge exactly when coverage drops; (2) pre-specify calibration/evaluation sample sizes and
the one-sided confidence rule required to establish a 2% bound at those n; (3) **systematic-error
strata**, not just average risk — every relation/operator × direction × paraphrase family gets a
minimum support and a zero/near-zero wrong allowance; (4) **four-way data separation** (model selection
/ confidence calibration / threshold selection / final eval on disjoint sets); (5) independent
ambiguity/answerability annotation + an explicit clarification behaviour; (6) **K>1 disjoint-source
phrasings + perturbation suite + both-orientation directional tests + whole risk-coverage-curve
reporting**; (7) **shift stress on the guarantee itself** — calibration-source vs deployment-source
phrasing shifts, not merely random held-out paraphrases (§4 caveat 4b). **Do NOT** rely on two-model
deliberation for confidence (PVD collapses with weak verifiers, §4 R5).

**P3-D-PS** `[DESIGN, P1, blocked-by: this review + P3-LR-NTP]`. Scope: H-PS concrete design —
NL→DSL→execute-on-the-µs-engine→generate-from-checked-result, with calibrated abstention as part of the
measured product. **What this review supports, sharpened by the crux (§3):** H-PS's value is an
**add-capability** value (the executor), which is **cleaner to attribute than H-GNN-fusion's** and
lands on the programme's **correctness thesis** — so **price it against its own falsifier, and do NOT
premise the design on a matched-resource efficiency win** the literature does not demonstrate. TinyGSM
is a 1.3B existence ANALOGY for the pipeline shape (materially unmatched, §3.5); execution-based
selection/verification is the strongest **matched-inference-at-fixed-k** lever (EGD/MBR-EXEC/LEVER, with
MBR-EXEC's spurious-majority caveat). **Execution catches invalid-not-wrong, so the S2 budget is
carried by LAYERED controls** — deterministic relation-semantics repair, typed/operator-specific
validation, contrastive inverse tests, independent verification where available, and a calibrated
abstention layer for the residual (§3.4, §5c/e). The design must name its protections against
**semantically valid-but-wrong programs** and against **renderer corruption of checked results**
(nsk1-g2d-cautioned generation leg) explicitly; keep the DSL inside the closed kot-query grammars where
exact constrained decoding is checkable (§4). Open legs: generation-from-checked-result (§8.6) and
verifier-abstention composition (§8.5).

**P3-D-ORACLE** `[DESIGN, P1, blocked-by: this review (co)]`. Scope: the oracle-input error-decomposition
protocol attributing G2→G3 loss across parse / retrieval-addressing / execution / generation per
experiment. **What this review supports:** field practice attests the INGREDIENTS — gold-parse arms as
the G2 anchor (our l3a/a5 verdicts already are that arm `[memory]`); per-stage breakdown counters (our
frame-miss / gazetteer-miss / mapper-abstain instrumentation is already field-shaped, §1);
perturbation-typed robustness attribution (Dr.Spider's 17-set design); ambiguity/unanswerable tagging of
inputs BEFORE scoring so abstentions are creditable (§4 R6, §5d) — **but the complete KOT stage protocol
is a DESIGN EXTRAPOLATION from those ingredients, not itself field-attested.** The decomposition must
oracle-ablate each stage SEPARATELY — intent/frame selection, role/direction binding, entity linking,
DSL serialization, execution, rendering — a single gold-parse arm cannot localize correlated errors
adequately. Mandate reporting the **risk-coverage curve per stage**, not a scalar.

**Non-recommendations (cells this review closes for Phase-1):** do not attempt grammar induction of the
target grammar (known/closed — induction's proven use is augmentation, §4); do not rely on
two-small-model deliberation for confidence (PVD, §4 R5); do not treat execution success as correctness
(§3.4); and as a project-local check (not a field-general prohibition — the bias results cover specific
constraint classes, §4), verify any locally-masked constrained decoder against the exact global mask on
our tiny closed grammar and quantify the divergence before freezing.

---

## 8. Open questions Phase-1 must resolve

1. **Learned parser vs fail-closed contract:** a learned proposer introduces a NEW confident-wrong
   channel exactly where the deterministic mapper abstained. What operating threshold clears BOTH 0.90
   retention and S2 ≤2%, and does any exist for a ≤360M parser on our verticals? (Empirical; nothing in
   the literature reports retention-at-S2-bound for closed grammars at this scale — §2.)
2. **Guarantee validity under phrasing shift:** conformal/calibration guarantees assume exchangeability;
   the deployment phrasing distribution is unknown. Split-source calibration, shift stress tests, and
   (possibly) online recalibration need a design — the literature flags the problem more than it solves
   it (§4 caveat 4b; Kamath, conformal-nlp-survey).
3. **Cost envelope:** the a1-hybrid ran at ~250 µs; a 135–360M parser is ~ms–10s-of-ms on 2 shared CPU
   cores. Does NLB admit a two-tier front-end (µs template/trie fast path + ms learned fallback +
   abstain), and what does that do to KOT-COST? (Design choice, no literature blocker.)
4. **Direction/role adversarial coverage:** the measured ROLE_DIR defect gets the targeted deterministic
   repair FIRST; the remaining question is how to enumerate and symmetrically test every directional
   frame — per-vertical inventory, both-orientations eval, per-frame systematic-error strata (§5c).
5. **Composition with the verifier loop:** f2b's verify-retry and NLB's parse-abstention are both
   selective mechanisms; are their failures correlated (same host, same phrasing sensitivity)?
   Unmeasured anywhere `[speculative cell]`.
6. **Generation-from-checked-result:** H-PS's last leg is cautioned by nsk1-g2d's net-harmful text
   append `[memory]`; TinyGSM's numeric answers dodge this (§3.5). Whether small hosts can verbalize
   checked results without corrupting them is an open experimental question for P3-E-PS-1.

---

## Citation-verification table (2026-07-19)

Legend: **V@src** = re-verified at primary source (abstract/PDF) this session; **V-body** = verified at
paper body/results table (ar5iv/PDF) this session; **prior** = accepted from the 07-11 PARSE.md
verification, not re-fetched (uncontested abstract-level); **carried** = owned by
`reports/lit-structured-parsing-and-inner-symbolic.md`, `verified:false` in draft, not re-verified here.

| # | Source (short) | URL | What it anchors | Status (2026-07-19) |
|---|---|---|---|---|
| 1 | TinyGSM | arxiv.org/abs/2312.09241 | H-PS existence analogy; add-capability crux | **V@src** — 1.3B+1.3B → 81.5%, teacher 77.4%, 34B floor: exact |
| 2 | LEVER | arxiv.org/abs/2302.08468 | learned verifier over execution | **V@src** — +4.6–10.9% code-davinci-002, 4 benchmarks, SOTA: exact |
| 3 | MBR-EXEC | arxiv.org/abs/2204.11454 | execution-agreement selection | **V@src** — beats all execution-unaware selectors; MBR over exec |
| 4 | EGD | arxiv.org/abs/1807.03100 | execution-guided decoding | **V@src** — 4 architectures, 83.8% WikiSQL: exact |
| 5 | TeCoD | arxiv.org/abs/2604.28028 | closest gate shape | **V@src** — "up to 36% higher" (NOT "+36 pts", § Divergences), 2.2×; BIRD 83.6–89.2% body-level (not re-confirmed); no confidence bound: confirmed |
| 6 | BERT intent+slot | arxiv.org/abs/1902.10909 | metric discipline (frame exactness) | **V-body (Table 2)** — 97.5/98.6 intent, 96.1/97.0 slot, **88.2/92.8 frame**: exact |
| 7 | CodeS | arxiv.org/abs/2402.16347 | small-scale SOTA + robustness | **V@src** — 1B–15B, SOTA+robustness on the six benchmarks, smaller than GPT-4 |
| 8 | STaR-SQL | aclanthology.org/2025.acl-long.1187 | reasoning-trace small-scale | **V@src — UPGRADED from draft's verified:false** — 86.6% EX, +31.6/+18.0 |
| 9 | PICARD | arxiv.org/abs/2109.05093 | incremental-parse constrained decode | **prior** (abstract-level; 12→2% Spider body-level in prior review) |
| 10 | Spider (2018) | arxiv.org/abs/1809.08887 | difficulty floor | **V@src** — 10,181/5,693/200/138; 12.4% exact DB-split: exact |
| 11 | BIRD | arxiv.org/abs/2305.03111 | realistic gap | **V@src** — ChatGPT 40.08% vs human 92.96%: exact |
| 12 | Shin (constrained few-shot) | arxiv.org/abs/2104.08768 | canonical few-shot parsing | **prior** (abstract-level) |
| 13 | Grammar prompting | arxiv.org/abs/2305.19234 | predict-BNF-then-constrain | **prior** (abstract-level) |
| 14 | Berant & Liang | aclanthology.org/P14-1133 | paraphrase absorption (fix for class a) | **V@src** — canonical utterances + paraphrase model, WebQuestions/Free917 |
| 15 | GCD-geng | arxiv.org/abs/2305.13971 | matched-resource validity win | **V@src** — "beat task-specific finetuned models", scarce-data |
| 16 | P-GCD | arxiv.org/abs/2606.01926 | local-mask bias caveat | **V@src** — Dang/Song/Zhang/Zhao/Van den Broeck/Ermon; SMC over FA; scope-bounded |
| 17 | COGS | arxiv.org/abs/2010.05465 | comp-gen (class c analog) | **V@src** — 96–99% ID / 16–35% gen, ±6–8% seed: exact |
| 18 | CFQ | arxiv.org/abs/1912.09713 | compound divergence | **V@src** — max-compound-divergence, strong negative correlation: exact |
| 19 | Qiu et al. (scale) | arxiv.org/abs/2205.12253 | scale doesn't fix comp-gen | **V@src** — flat/negative FT to 11B; **"limitations of current techniques"** framing: exact |
| 20 | CSL | arxiv.org/abs/2112.07610 | grammar-induction augmentation | **V@src** — quasi-synchronous CFG, T5, "stronger than T5-CSL ensemble" (§ Divergences: "SOTA" is mild) |
| 21 | Nye | arxiv.org/abs/2003.05562 | rule synthesis at tiny scale | **V@src** — beats neural meta-learning, SCAN + number-words |
| 22 | Spider-Syn | arxiv.org/abs/2106.01065 | paraphrase drop; annotation > adversarial | **V@src** — "dramatically drops"; annotation superior |
| 23 | Dr.Spider | arxiv.org/abs/2301.08881 | perturbation instrument | **V@src** — 17 sets, 14.0% overall / 50.7% worst: exact |
| 24 | NL2SQL survey | arxiv.org/abs/2408.05109 | core-difficulty naming | **V@src** — NL ambiguity, under-specification, schema linking |
| 25 | El-Yaniv & Wiener | jmlr.org/papers/v11/el-yaniv10a | risk-coverage foundations | **prior** (foundational, uncontested) |
| 26 | Geifman (selective DNN) | arxiv.org/abs/1705.08500 | risk-controlled selection | **V@src** — "2% top-5 ImageNet … 99.9% … ~60% coverage": exact |
| 27 | Kamath | arxiv.org/abs/2006.09462 | calibrator under shift | **V@src** — "56% at 80% … vs 48%": exact |
| 28 | Calibrated Interpretation | arxiv.org/abs/2211.07443 | parser calibration varies | **V@src** — varies by model/dataset; library + challenge splits |
| 29 | ASPIRE | arxiv.org/abs/2310.11689 | trainable selective prediction | **V@src** — AUACC 91.23→92.63, AUROC 74.61→80.25: exact ("small hosts" mild, § Div.) |
| 30 | BAR-SQL | arxiv.org/abs/2601.10318 | abstention-in-reward shape | **V@src** — 91.48% Ent-SQL-Bench, "outperforming … Claude 4.5 Sonnet and GPT-5"; single-group |
| 31 | PVD | arxiv.org/abs/2605.25133 | two-model confidence collapses | **V@src** — ~30pp HC-Prec gap; "collapse or invert … when the verifier operates outside its effective region": exact |
| 32 | Conformal abstention | arxiv.org/abs/2405.01563 | S2-shaped bound + central caveats | **V@src + V-body** — rigorous error-rate bound; **"clearly cannot detect situations where the LLM is completely sure about an incorrect answer"**; exchangeability in §2: exact |
| 33 | Conformal LM | arxiv.org/abs/2306.10193 | calibrated generation sets | **V@src** — set contains ≥1 acceptable answer w.h.p. |
| 34 | Conformal-NLP survey | arxiv.org/abs/2405.01976 | exchangeability caveats catalogue | **prior** (survey, uncontested framing) |
| 35 | AmP | arxiv.org/abs/2306.00824 | ambiguity is a property of NL | **V@src** — 5 ambiguity types; captured only when attested |
| 36 | TriageSQL | arxiv.org/abs/2010.12634 | should-abstain detection is hard | **V@src** — 4 unanswerable categories; RoBERTa 60% F1: exact |
| 37 | DTE | arxiv.org/abs/2212.08902 | confident-wrong class | **V@src** — plausible SQL for problematic Q; 6 categories; DTE beats baselines |
| 38 | Synchromesh | arxiv.org/abs/2201.11227 | constrained semantic decoding | **carried** (prior review) |
| 39 | SynCode | arxiv.org/abs/2403.01632 | CFG masking removes syntax errors | **carried** (prior review) |
| 40 | XGrammar | arxiv.org/abs/2411.15100 | near-zero-overhead serving | **carried** (prior review) |
| 41 | Type-constrained (PLDI-25) | arxiv.org/abs/2504.09246 | well-typedness enforcement | **carried** (prior review) |
| 42 | GAD (ASAp) | arxiv.org/abs/2405.21047 | greedy-masking distortion | **carried** (prior review) |
| 43 | GENRE | arxiv.org/abs/2010.00904 | trie-constrained entity linking | **carried** (prior review) |

**Coverage:** **32 / 43 re-verified at primary source this session** (30 abstract/PDF + BERT and
conformal-abstention at body level), including **every numerically load-bearing claim** and **all four
future-dated 2026 arXiv IDs** (TeCoD 2604.28028, P-GCD 2606.01926, BAR-SQL 2601.10318, PVD 2605.25133 —
all real, correct authors, numbers as cited); **6 accepted as `prior-verified`** (uncontested
abstract-level: PICARD, Shin, grammar-prompting, El-Yaniv/Wiener, conformal-NLP survey — and note
El-Yaniv/Wiener + survey are foundational, non-numeric); **6 carried** from the prior structured-parsing
review (Synchromesh, SynCode, XGrammar, type-constrained, GAD, GENRE — `verified:false` in draft, not
re-verified here). **No load-bearing citation failed source-verification.**

---

## Divergences from the Fable draft (`docs/next/lit/PARSE.md`)

All divergences are **minor / provenance-level**; none changes a conclusion. Listed for the record.

1. **TeCoD "+36 points" vs "up to 36% higher" — genuine numeric over-precision (the sibling-style
   catch).** `PARSE.sources.jsonl` and §2 render the headline as "**up to +36 points** execution
   accuracy over ICL." The abstract states "**up to 36% higher execution accuracy than in-context
   learning**." "36% higher" most naturally reads as a **relative** improvement, not absolute
   percentage points; the "+36 points" rendering is the stronger/more favorable reading and is **not
   confirmable at abstract level**. **Recommendation:** downgrade to "up to 36% higher (relative)
   execution accuracy" unless the paper body is checked to license absolute points. Non-decision-changing
   (TeCoD is already flagged as approaching-not-clearing the gate), but exactly the metric-type slip the
   discipline flags. *(Same points-vs-percent ambiguity exists benignly for STaR-SQL "+31.6/+18.0" and
   is non-load-bearing there.)*

2. **TeCoD BIRD 83.6–89.2% is body-level, not confirmable at abstract.** The draft already labels it
   "matched-BIRD … across reported settings/models (corrected 2026-07-11)"; I could not re-confirm the
   range at abstract level this session and did not fetch the body. Draft's honest body-level framing is
   **preserved, not overturned** — treat the range as body-level pending a body fetch.

3. **STaR-SQL status.** The draft carried it `verified:false` (KB-recall, not re-fetched). I fetched the
   ACL Anthology page and **confirmed 86.6% EX, +31.6/+18.0** — **upgrade to source-verified.**

4. **ASPIRE "small hosts."** The draft says selective prediction is "trainable into small hosts (PEFT +
   self-evaluation)." The abstract states PEFT + self-evaluation improves selective prediction but does
   **not** specifically say "small hosts"; ASPIRE's tested hosts are modest-scale and the mechanism
   (PEFT-into-a-host) is accurate, so this is a **fair characterization, mildly stronger** than the
   abstract's literal wording. Non-load-bearing.

5. **CSL "SOTA."** The draft calls CSL "SOTA on comp-gen benchmarks incl. natural-variation splits." The
   abstract emphasizes "**even stronger than a T5-CSL ensemble on two real-world compositional-
   generalization tasks**" rather than a blanket SOTA claim. Supported directionally as strong/SOTA-class;
   **mild over-characterization**, non-load-bearing.

**Points of full concordance worth stating:** the draft's executive verdict (capability-limited-is-leading
for the dominant classes; the deterministic ROLE_DIR defect as repairable-not-fundamental; the S2 gate as
an empirically-unresolved parser+abstention system), its metric-discipline correction on BERT
(intent/slot ≠ frame exactness; 88.2/92.8 confirmed), its elevation of the conformal-abstention
self-consistency caveat (confirmed verbatim at the paper body), its execution-catches-invalid-not-wrong
design law, and its selective-prediction recommendations **all hold at source.** This formalization adopts
them, adds the epistemic tagging + the citation-verification table + the **sharpened matched-resource-vs-
add-capability crux answer for H-PS** (§3, aligned with the P3-LR-FUSE sibling), and leaves the draft's
conclusions intact.
