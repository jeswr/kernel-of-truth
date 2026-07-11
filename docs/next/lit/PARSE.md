# P3-LR-PARSE — Semantic Parsing, Program Synthesis, Grammar Induction, Uncertainty + Selective Prediction

**Kernel of Truth Programme-3, Phase-0 literature review.**
Author: Fable (Claude Fable 5, literature-researcher discipline), 2026-07-11.
Bead: `kernel-of-truth-s55r.5` (P3-LR-PARSE, programme rev-2 §5 Phase-0 table).
Feeds (Phase-1): **P3-D-NLB** (schedule-critical: gates every natural-input store leg,
ASM-0814), **P3-D-PS**, **P3-D-ORACLE** (co).

**Epistemic contract.** Every load-bearing line carries [MEASURED|STIPULATED|EXTRAPOLATION];
literature claims carry `[LIT: <id>]` keys into `docs/next/lit/PARSE.sources.jsonl`
(one JSON object per source; `verified:true` = primary page fetched by me 2026-07-11 at the
URL given — NOT a claim that every body figure was independently re-checked; where a
specific number is load-bearing, its metric definition is stated in-line;
`verified:false` = carried from a prior verified review or KB recall, NOT
re-fetched — flagged in-line as UNVERIFIED-THIS-PASS). KB/lit records are recall
infrastructure, not evidence; nothing here amends any registry object. Prior-failure
judgements (capability-limited vs fundamental) are §5's explicit deliverable.

**Dedup statement (what already exists; this review builds on, does not repeat):**
- `reports/lit-structured-parsing-and-inner-symbolic.md` (2026-07-09) — owns the
  **grammar/type-constrained decoding** record (PICARD, Synchromesh, SynCode, XGrammar,
  type-constrained PLDI-2025, GAD distortion caveat, format-tax line, GENRE trie idea A3).
  §3 below only re-anchors what PARSE needs and adds the 2025–26 correctness caveats.
- `reports/lit-llm-injection-priorart.md` — rule-injection laws; not re-covered.
- lit-KB (`kb/records/`, 552 records; pipelines in `tools/kb/`) — already holds directly
  relevant records: TranX (1810.02720), Program Synthesis with LLMs (2108.07732),
  SQL-PaLM (2306.00739), STaR-SQL (ACL 2025), TeCoD (2604.28028), P-GCD (2606.01926),
  PVD selective prediction (2605.25133), BAR-SQL (openalex w7124513826), text-to-SQL
  knowledge injection (2409.15907). New sources found here are staged in
  `PARSE.sources.jsonl` for the coordinator's central ingest — **no KB shard/index is
  mutated by this bead** (governance).
- No `docs/research-plan/` or `docs/` review covers selective prediction, conformal
  abstention, paraphrase-robust parsing, or small-scale NL→DSL — that is this document's
  net-new ground.

---

## 0. Executive verdict (one paragraph)

The measured Programme-2 NL-boundary failure (l3a-parse 47.6% retention / a5-nl 41.6% +
S2 dangerous-wrong) was produced by a **verbatim-lexicon, frozen-frame, no-learning
front-end** — the exact architecture class whose paraphrase ceiling the field measured and
abandoned in 2014–2018 [MEASURED: registry/verdicts/{l3a-parse,a5-nl}.json;
LIT: berant-liang-2014]. On that failure class, **capability-limited is the leading
hypothesis**: fine-tuned small parsers (110M–3B) with grammar-constrained decoding post
strong results on closed grammars far wider than kot-query/1's seven families — with the
metric accounting kept honest: whole-frame exactness ~88–93% (Joint BERT sentence-level
semantic-frame accuracy ≈88.2% ATIS / ≈92.8% Snips; the oft-quoted 96–97% figures are
intent accuracy / slot F1, §2), matched-template BIRD execution accuracy ~83.6–89.2%
(TeCoD, §2), Spider EX mid-80s [LIT: picard-2021, codes-2024, tecod-2025,
bert-intent-slot-2019] — plausibility evidence, NOT a demonstration that the joint
0.90-retention/S2 gate clears. The specific l3a mechanism (paraphrase stratum 0/261) is
the single best-understood fixable defect in the field. Two residues must be engineered
around, not parsed through: (i) **role/direction binding errors** (the a5-nl dangerous
class) were, in the MEASURED system, a **deterministic direction-table bug** ("what
contains X" vs "what X contains" bound to the wrong valid operation) with a targeted
deterministic repair already proposed [MEASURED: registry/assessments/a5-nl.json]; for
LEARNED parsers the analogous class stays brittle under compositional/distributional
shift with current techniques [LIT: cogs-2020, cfq-2020, qiu-scale-2022 — limitations of
the particular models/splits tested, not an impossibility result]. Checked execution
CANNOT catch this class (a flipped query is valid-and-wrong, §3); the mitigations are
the deterministic repair, symmetric both-orientation adversarial tests, typed/contrastive
validation, and risk control — noting that systematic high-confidence inversions are
exactly where confidence scores can fail to separate (§4, §5c); (ii)
**ambiguity/underspecification** is a property of natural language
[LIT: amp-2024, dte-2023] — the correct output is abstention (or clarification), and
detecting should-abstain inputs is itself a measured-hard task [LIT: triagesql-2020].
Selective prediction supplies the missing contract: trained calibrators beat raw
confidence under shift [LIT: kamath-2020], and conformal methods give distribution-free
bounds of exactly the S2 shape ("P(wrong-with-answer) ≤ ε at 1−δ")
[LIT: conformal-abstention-2024, conformal-lm-2024, geifman-2017]. Bottom line for
P3-D-NLB: a 0.90-retention, S2-fail-closed front-end at small scale is **plausible but
empirically unresolved at the programme gate** — no cited work reports
retention-at-S2-bound for a ≤360M parser on a grammar like ours (§7.1); it is testable
only as a parser+abstention SYSTEM whose risk-coverage curve is the measured product —
and any conformal guarantee is only as good as the phrasing distribution it was
calibrated on [EXTRAPOLATION, argued §4/§6].

---

## 1. The measured failure, restated precisely, and its literature class

What actually failed [MEASURED: registry/verdicts/l3a-parse.json + a5-nl.json]:

- The a1-hybrid front-end is **deterministic and training-free**: one entity/identifier
  gazetteer + one frozen frame rule set, single-label verbatim concept mapper, ~250–267 µs
  per query.
- l3a-parse (family/world): 47.6% retention; label-verbatim stratum 76.4% but
  **paraphrase stratum 0/261 = 0.0%** (no synonym table); stage breakdown frame-miss 228,
  mapper-abstain 48, gazetteer-miss 40, frame-ambiguous 41. Failure mode SAFE (mis-parse →
  refusal; S2 did not fire).
- a5-nl (code): 41.6% retention, frame-miss 468/gazetteer-miss 24 — AND the S2 kill fired:
  the frame ROLE_DIR direction table **flips containment orientation** into
  real-but-wrong answers with provenance (5.0% ≥ 2% bar). Mechanism, precisely: a
  **deterministic hand-coded lookup defect** — "what contains X" vs "what X contains"
  bound to the wrong (valid) engine operation. The a5 assessment already names the
  targeted deterministic repair route: a frame-layer fix that fails closed on ambiguous
  orientation [MEASURED: registry/assessments/a5-nl.json].

Literature mapping [STIPULATED — this taxonomy organizes §5]:

| our stage | literature name | canonical instruments |
|---|---|---|
| frame-miss (paraphrase) | lexical/paraphrase gap of rule- and template-parsers | [LIT: berant-liang-2014, spider-syn-2021, drspider-2023] |
| gazetteer-miss | schema linking / entity linking | [LIT: nl2sql-survey-2025, spider-syn-2021, genre-2021] |
| frame-ambiguous | NL ambiguity / underspecification | [LIT: amp-2024, dte-2023, triagesql-2020] |
| ROLE_DIR flip (dangerous) | measured: deterministic direction-table defect; learned-parser ANALOG only: role/argument-structure generalization error | [MEASURED: a5-nl assessment; LIT: cogs-2020, cfq-2020] |
| mapper-abstain | out-of-lexicon abstention (correct behaviour) | selective-prediction frame, §4 |

Direction-only reading [EXTRAPOLATION: from the MEASURED l3a-parse stage breakdown + LIT: berant-liang-2014 — never a premise; P3-E-NLB-1 is what tests it]: the 0.0% paraphrase stratum is a **floor artifact of the no-learning front-end**, not a measurement of what parsing can do — the same sentence class that kills a verbatim matcher is the *bread-and-butter positive case* of every learned parser since 2014. This is the single most decision-relevant sentence in this review.

---

## 2. SQ1 — semantic parsing into executable forms at SMALL model scale: state of the art

**The proven recipe at 110M–3B is: fine-tuned seq2seq (or intent+slot) parser + grammar-
constrained decoding + execution-aware selection.** Evidence, smallest-first:

- **110M (BERT-base), closed intent+slot grammars:** joint intent classification + slot
  filling significantly improves sentence-level semantic-frame accuracy on ATIS/Snips
  [LIT: bert-intent-slot-2019]. Metric discipline: the oft-quoted ~96–97% figures are
  **intent accuracy / slot F1**, NOT whole-frame exactness; sentence-level semantic-frame
  accuracy — the exactness-shaped metric — was ≈88.2% (ATIS) / ≈92.8% (Snips), i.e.
  BELOW the 0.90 bar on one of the two benchmarks. kot-query/1's 7 shape-recoverable families +
  gazetteer slots are structurally an intent+slot task, NOT open text-to-SQL
  [STIPULATED mapping; design-relevant because it sets the difficulty prior].
- **220M–3B, open cross-domain SQL:** fine-tuned T5 + PICARD incremental-parse-constrained
  decoding = then-SOTA Spider/CoSQL [LIT: picard-2021]. CodeS (1B–15B open models,
  SQL-centric incremental pretraining + schema-linking prompt construction + bidirectional
  augmentation) = SOTA accuracy AND robustness on Spider/BIRD/Spider-Syn/-Realistic/-DK/
  Dr.Spider at much smaller size than GPT-4 pipelines [LIT: codes-2024]. STaR-SQL adds
  self-taught reasoning traces: 86.6% EX Spider [LIT: star-sql-2025, KB record,
  UNVERIFIED-THIS-PASS].
- **The closed/recurring-grammar special case (ours):** TeCoD mines NL→SQL templates,
  fine-tunes a template selector, and enforces the chosen template by grammar-constrained
  decoding: up to +36 points execution accuracy over in-context learning and 2.2× lower
  latency on matched queries; matched-BIRD execution accuracy varies ~83.6–89.2% across
  the reported settings/models [LIT: tecod-2025]. This is the closest published shape
  to FK-NLB-3 (closed template family + constrained decode + classifier); it APPROACHES
  but does not demonstrably clear the 0.90 bar on its matched slice, and reports nothing
  about simultaneously meeting an S2-style confidence bound — plausibility evidence for
  the recipe, not gate feasibility.
- **Few-shot, data-scarce:** constrained canonical-utterance parsing (map NL into a
  controlled English sublanguage under grammar constraints, then deterministically to
  logical form) [LIT: shin-2021]; grammar prompting for DSLs (predict a minimal BNF, then
  constrain) [LIT: grammar-prompting-2023]. Both trade accuracy for near-zero training
  cost — the fallback if NLB must stay training-free.
- **Perspective on difficulty:** open cross-domain text-to-SQL is HARD (best 2018 model
  12.4% exact on Spider's DB split [LIT: spider-2018]; ChatGPT 40.08% vs human 92.96%
  execution accuracy on realistic BIRD databases [LIT: bird-2023]). Our envelope is the
  opposite corner: closed grammar, fixed tiny schema, recurring query shapes — the corner
  where the literature's numbers are highest [EXTRAPOLATION, direction-only].

LOAD-BEARING (for P3-D-NLB sizing): nothing in this record supports 0.90+ retention from
a **zero-learning** front-end under held-out phrasing; everything that clears 0.85+ under
paraphrase has a learned component (fine-tuned parser, learned selector, or synonym
resources) [EXTRAPOLATION over the §2 record + §1's measured floor].

## 2b. Accounting skepticism (what "beat" means above)

- Constrained decoding wins are **compute-matched by construction** (same model, masked
  softmax, near-zero overhead at serving [LIT: xgrammar-2024, UNVERIFIED-THIS-PASS]) —
  the cleanest wins in this review.
- Fine-tuned-small > few-shot-giant claims (CodeS, TeCoD, STaR-SQL) are
  **inference-matched but training-unmatched**; under the programme's deployment-
  efficiency accounting this is admissible ONLY with the tuning compute declared in the
  KOT-LIFE ledger [STIPULATED, per programme §2].
- Execution-feedback/verifier wins (§3) spend k× sampling; honest comparisons must hold
  k fixed vs self-consistency — LEVER does report against sampling baselines
  [LIT: lever-2023]; TinyGSM's 81.5% is teacher-data-unmatched (12.3M synthetic problems
  from GPT-3.5) [LIT: tinygsm-2023].
- BAR-SQL-class RL-trained abstention claims ("beats GPT-5") are single-group on a
  self-built benchmark [LIT: barsql-2026] — adopt the *shape* (abstention in the reward),
  not the numbers.

---

## 3. SQ2 — NL→DSL / program synthesis WITH execution feedback

(Decoder-side grammar machinery is owned by the prior review; here: what the executor
buys, and its precise limit.)

- **Execution-guided decoding** (condition decoding on execution of partial programs):
  universally improves 4 architectures on WikiSQL/ATIS/GeoQuery; 83.8% EX WikiSQL in 2018
  [LIT: egd-2018]. With a µs deterministic engine, partial-execution pruning is
  effectively free for us [EXTRAPOLATION].
- **Execution-based selection:** MBR-EXEC — vote among sampled programs by execution
  agreement on test inputs; significantly outperforms every non-execution selector
  [LIT: mbr-exec-2022]. Precise limit: agreement over a SMALL set of test inputs is an
  approximation of semantic equivalence, and the vote can select a majority cluster of
  spurious (consistently-wrong) programs — it is a selector, not a correctness check.
- **Learned verification over execution results:** LEVER — verifier reads (NL, program,
  execution result) and rescores; +4.6–10.9% over code-davinci-002 across 4 benchmarks,
  then-SOTA [LIT: lever-2023]. Note the host was frontier-scale; small-host transfer is
  an open cell — but f2b-replicate is OUR measured small-host analog of exactly this
  verifier-rescoring shape [MEASURED: registry/verdicts/f2b-replicate.json, +0.1507,
  alignment-specific, formal inputs only].
- **The small-scale existence proof:** TinyGSM — 1.3B generator + 1.3B verifier emitting
  Python that is EXECUTED: 81.5% GSM8K, above its GPT-3.5 teacher (77.4%) and the prior
  34B floor for 80% [LIT: tinygsm-2023]. This is an EXISTENCE ANALOGY for
  H-PS's pipeline shape (NL → program → execute → verify/select → answer from checked
  result) at 1.3B — NOT a matched H-PS demonstration [LOAD-BEARING for P3-D-PS]: its
  12.3M GPT-3.5-synthesized training corpus, single domain (grade-school math),
  executable-Python target, sampled verifier selection, and trivial numeral rendering
  all differ materially from KOT parsing + surface generation —
  our generation leg is nsk1-g2d-cautioned [MEASURED: g2d text-append net-harmful].
- **The limit that matters for a5-nl:** execution feedback catches *invalid/failing*
  programs, NOT *valid-but-wrong* ones. A direction-flipped kot-query executes perfectly
  and returns a well-formed wrong answer — exactly the class DTE documents for text-to-SQL
  (plausible SQL for ambiguous/unanswerable questions) [LIT: dte-2023] and BIRD's
  human-gap quantifies [LIT: bird-2023]. Execution feedback is therefore necessary-cheap
  but nowhere near sufficient for the S2 gate — and in particular it is NOT a mitigation
  for the ROLE_DIR class at all (§5c) [STIPULATED design law for P3-D-PS].

---

## 4. SQ3+SQ4 — grammar machinery (delta only) and calibrated abstention / selective prediction

**Grammar-constrained decoding, 2025–26 delta over the prior review:**
- GCD without finetuning substantially outperforms unconstrained LMs and can beat
  task-specific fine-tuned models on structured tasks (IE, entity disambiguation)
  [LIT: gcd-geng-2023] — constraints are the cheapest accuracy lever where data is scarce.
- Scope caveat: locally-masked constrained decoding can be **biased sampling** relative
  to the true grammar-conditioned LM distribution — P-GCD studies this sampling bias over
  finite-automaton constraint classes and corrects it with SMC-style tractable proposals;
  GAD documents the same distortion for greedy masking [LIT: pgcd-2026, gad-2024
  (UNVERIFIED-THIS-PASS)]. Neither result shows that ordinary local constrained decoding
  is unsafe or task-incorrect in general, nor that global decoding is "modest cost" for
  an arbitrary grammar — these are distributional-fidelity results on the constraint
  classes studied. Design note (project-local, not a field rule): kot-query is closed and
  tiny, so it should be cheap to CHECK a local-mask decoder against an exact global mask
  on our grammar and quantify any divergence before freezing — feasibility and cost to be
  established in P3-D-NLB, not assumed [EXTRAPOLATION].
- **Grammar induction** (the bead's named sub-question): our grammar is known and closed,
  so induction is NOT needed for the target side. Its two proven parser-relevant uses:
  (i) induce a grammar over training pairs → recombine → data augmentation that transfers
  compositional robustness into a fine-tuned T5 (SOTA on comp-gen + natural-variation
  benchmarks) [LIT: csl-2022]; (ii) few-shot explicit rule-system synthesis beats neural
  meta-learning when the mapping is genuinely rule-like [LIT: nye-2020]. Use (i) to
  manufacture paraphrase training data for NLB [STIPULATED recommendation].

**Selective prediction — the frame the NLB gate instrument should adopt:**
- Foundations: the risk-coverage trade-off and near-optimal reject strategies
  [LIT: elyaniv-wiener-2010]; risk-CONTROLLED selection — set desired risk, reject to
  guarantee it w.h.p. (2% top-5 ImageNet error at ~60% coverage) [LIT: geifman-2017].
  The NLB gate ("retention ≥0.90 with S2 ≤2% dangerous-wrong") is a point on a
  risk-coverage curve; the literature-standard instrument reports the whole curve + AUACC
  and then FREEZES an operating threshold [STIPULATED adoption].
- Raw model confidence is not enough under shift: a trained calibrator answers 56% of
  questions at 80% accuracy vs 48% for softmax under domain shift [LIT: kamath-2020].
  Parser-specific: calibration of semantic parsers varies by model and dataset; metrics
  library + confidence-based challenge splits exist [LIT: calibrated-interpretation-2023].
- Selective prediction is trainable into small hosts (PEFT + self-evaluation lifts
  AUACC/AUROC) [LIT: aspire-2023]; 2026 variants train abstention directly into the
  parser's RL reward (BAR-SQL) [LIT: barsql-2026] or extract it from two-model
  deliberation — which **collapses when the verifier is weak/out-of-domain**
  [LIT: pvd-2026, caution for small pairs].
- **Conformal methods give the S2-shaped guarantee:** conformal abstention bounds the
  error (hallucination) rate with rigorous guarantees (including high-probability
  risk-control variants) while abstaining less than log-prob baselines
  [LIT: conformal-abstention-2024]; conformal language modeling returns
  calibrated generation sets with coverage guarantees [LIT: conformal-lm-2024]; survey of
  scope + caveats [LIT: conformal-nlp-survey-2024]. CENTRAL caveat for the ROLE_DIR class
  (not a footnote): the guarantee holds only under exchangeability and only for the
  chosen loss/match function, and the conformal-abstention paper itself notes that a
  self-consistency-style match score **cannot detect a model that is consistently
  confident in the same wrong answer** [LIT: conformal-abstention-2024]. Systematic
  high-confidence direction inversions are exactly that case — abstention reduces them
  only if the chosen score actually separates them, which P3-D-NLB must measure, not
  assume (§5c).
- LOAD-BEARING caveat: every conformal guarantee assumes exchangeability with the
  calibration set — a paraphrase-distribution shift (exactly what K=1 agent-authored
  phrasings vs real users is) silently voids the bound [LIT: conformal-nlp-survey-2024 +
  kamath-2020's measured shift degradation; EXTRAPOLATION to our setting]. The NLB gate
  must therefore calibrate and evaluate on *disjoint phrasing sources* and stress the
  threshold under Dr.Spider-style perturbation [STIPULATED requirement for P3-D-NLB].
- Detecting should-abstain inputs is itself hard: cross-domain answerable-vs-unanswerable
  classification sits at 60% F1 for RoBERTa [LIT: triagesql-2020]; ambiguity taxonomies +
  counterfactual training data help [LIT: dte-2023]; models only represent meaning
  distributions of ambiguous inputs when ambiguity is attested in training/prompt
  [LIT: amp-2024].

---

## 5. SQ5 — WHY NL→formal fails: capability-limited vs fundamental, per failure class

The bead's central question, judged per class (method: what moved the number, at what
scale, under what accounting):

**(a) Lexical/paraphrase gap — CAPABILITY-LIMITED (method-limited), high confidence.**
Verbatim/rule front-ends have a hard paraphrase ceiling; the field's fix was learned
paraphrase absorption: canonical utterances + paraphrase models [LIT: berant-liang-2014],
then fine-tuned seq2seq, then constrained few-shot canonical parsing [LIT: shin-2021].
Residual truth: even LEARNED parsers drop dramatically when explicit NL↔schema lexical
correspondence is removed (Spider-Syn), and schema synonym annotations recover more than
adversarial training [LIT: spider-syn-2021]; the most robust model still loses 14.0%
overall / 50.7% worst-perturbation on Dr.Spider [LIT: drspider-2023]. So: fixable to
~0.85–0.95 on a closed grammar, NOT to 1.0, and only with paraphrase-diverse training +
lexicon resources. l3a-parse's 0/261 says nothing beyond "no-learning fails"
[EXTRAPOLATION, §1].

**(b) Entity/schema linking (gazetteer-miss) — CAPABILITY-LIMITED.** Persistent named
core difficulty of NL2SQL [LIT: nl2sql-survey-2025], but on a FIXED tiny schema with a
registered lexicon, trie-constrained name emission + exact post-mapping (GENRE shape,
prior review idea A3) plus synonym annotation [LIT: spider-syn-2021] is the measured
strong recipe [LIT: genre-2021, UNVERIFIED-THIS-PASS].

**(c) Role/direction binding (the a5-nl dangerous class) — MEASURED as a DETERMINISTIC
direction-table bug, directly repairable; for LEARNED parsers, currently brittle under
compositional/distributional shift (a limitation of current techniques, NOT shown
fundamental).** What actually failed [MEASURED: registry/assessments/a5-nl.json]: the
frozen frame layer's hand-coded ROLE_DIR lookup bound "what contains X" vs "what X
contains" to the wrong (valid) engine operation — a deterministic table defect, and the
a5 assessment already proposes the targeted deterministic repair (a frame-layer fix that
fails closed on ambiguous orientation). Nothing in that measurement licenses
"fundamental". The LEARNED-parser ANALOG of this class is where the compositional-
generalization literature applies: 96–99% in-distribution vs 16–35% compositional split
[LIT: cogs-2020]; accuracy collapses as compound divergence grows [LIT: cfq-2020];
fine-tuning scale curves on OOD comp-gen FLAT OR NEGATIVE up to 11B (ICL scales but
stays below small fine-tuned models) [LIT: qiu-scale-2022]. Those results establish poor
OOD compositional generalization for the PARTICULAR learned models and splits tested —
Qiu et al. explicitly frame their findings as limitations of current techniques, not an
impossibility result — so they do NOT establish that direction/argument binding is
unfixable by a better parser. What has measurably moved it: grammar-based data
augmentation (CSL) [LIT: csl-2022] and explicit rule synthesis at tiny scale
[LIT: nye-2020]. What CANNOT catch it: checked execution — a direction-flipped query is
valid-and-wrong and executes perfectly (§3), and no output grammar catches it; and
self-consistency-style confidence scores can fail on exactly this class (consistent
confident inversion — §4 conformal caveat), so abstention helps only if its score
separates the inversions. DESIGN LAW for NLB: (1) apply the targeted deterministic
ROLE_DIR repair regardless of parser class; (2) role/direction correctness must be
adversarially and symmetrically tested (both orientations of every directional frame,
held-out compositions, per-frame error strata); (3) typed/operator-specific validation
and contrastive inverse tests as independent checks; (4) low-margin directional parses
abstain, with the score's ability to separate systematic inversions itself a measured
quantity [STIPULATED, from the MEASURED defect + §3/§4].

**(d) Ambiguity/underspecification — FUNDAMENTAL (property of NL, not of models).**
Ambiguous inputs have meaning DISTRIBUTIONS; models capture them only when deliberately
instructed/attested [LIT: amp-2024]; real question streams contain unanswerable and
ambiguous classes that parsers happily "answer" [LIT: dte-2023, triagesql-2020]. No
scale fixes this; the correct product behaviour is calibrated abstention (or
clarification), which is why the abstention policy is PART of the measured NLB system
[STIPULATED, consistent with programme §3.4 H-PS definition].

**(e) Confident-wrong-with-provenance (S2) — a SYSTEM failure, prevented by LAYERED
controls, never by parser accuracy alone.** The literature's parsers exhibit it endemically
(plausible SQL for bad questions [LIT: dte-2023]; 40% vs 93% human on BIRD with fluent
outputs [LIT: bird-2023]). The safety budget is carried by several layers, not by
abstention alone: fixing deterministic relation semantics at the source (§5c repair),
typed/operator-specific validation, contrastive inverse tests, independent verification
where available — and then risk-controlled selection for the residual, via trained
calibrators under shift [LIT: kamath-2020], conformal abstention with error-rate bounds
[LIT: conformal-abstention-2024], and abstention-aware training rewards [LIT: barsql-2026].
The a5-nl lesson ("wrong-with-provenance is worse than refusal") is the field's selective-
prediction motivation, verbatim [EXTRAPOLATION, direction-only].

**Net judgement for FK-NLB-3:** **capability-limited is the LEADING HYPOTHESIS at our
scope, empirically unresolved at the programme gate.** The retention loss is driven
~entirely by classes (a)+(b) — the two the literature repairs most reliably — and the
dangerous class (c) is, as measured, a repairable deterministic defect; but no cited
work reports 0.90-retention jointly with an S2-style confidence bound for a small parser
on a grammar like ours (§7.1), so this judgement is a testable hypothesis P3-D-NLB must
resolve, not a settled or literature-established conclusion. Classes (d)+(e), plus the
learned-parser residue of (c), are why the redesign must keep the deterministic engine
as the sole answer authority and treat the parser as an untrusted proposer under a
risk-controlled gate with layered checks [EXTRAPOLATION over §5; the single sentence
P3-D-NLB should be built around].

---

## 6. SQ6 — paraphrase robustness: methods that measured

1. **Paraphrase-diverse supervision** — the dominant fix: augmentation via induced-grammar
   recombination (CSL, SOTA incl. natural-variation splits) [LIT: csl-2022]; bidirectional
   augmentation inside CodeS's robustness wins [LIT: codes-2024].
2. **Canonical-utterance factoring** — parse NL→canonical utterance→(deterministic) form;
   absorbs variation in the NL-NL half where LMs are strongest [LIT: berant-liang-2014,
   shin-2021].
3. **Lexicon/synonym resources at the interface** — schema synonym annotations beat
   adversarial training [LIT: spider-syn-2021]; registered-lexicon trie constraints
   [LIT: genre-2021, UNVERIFIED-THIS-PASS].
4. **Constrained decoding** — removes syntax/validity violations that a CORRECT grammar
   expresses, at low serving overhead; it does not remove semantic invalidity,
   grammar-specification or tokenizer-integration bugs, or all serving cost, and carries
   the local-vs-global mask fidelity caveat [§4; LIT: picard-2021, pgcd-2026].
5. **Evaluation practice (adopt):** robustness is measured with multi-perturbation
   diagnostic suites (17 perturbation sets; report per-perturbation worst-case, not just
   aggregate) [LIT: drspider-2023]. Our l3a-parse/a5-nl used K=1 held-out phrasing per
   query [MEASURED: envelope verbatim] — BELOW field practice; the NLB gate instrument
   needs K>1 phrasings per query from an author source disjoint from calibration, plus a
   perturbation taxonomy (synonym, structure, typo/ASR-style noise) [STIPULATED
   requirement for P3-D-NLB].

---

## 7. Open questions Phase-1 must resolve (the design beads' opening questions)

1. **Learned parser vs fail-closed contract:** a learned proposer introduces a NEW
   confident-wrong channel exactly where the deterministic mapper abstained. What
   operating threshold on the risk-coverage curve clears BOTH 0.90 retention and S2 ≤2%,
   and does any exist for a ≤360M parser on our verticals? (Empirical; nothing in the
   literature reports retention-at-S2-bound for closed grammars at this scale.)
2. **Guarantee validity under phrasing shift:** conformal/calibration guarantees assume
   exchangeability; the deployment phrasing distribution is unknown. Split-source
   calibration, shift stress tests, and (possibly) online recalibration need a design —
   the literature flags the problem more than it solves it [LIT: conformal-nlp-survey-2024,
   kamath-2020].
3. **Cost envelope:** the a1-hybrid ran at ~250 µs; a 135–360M parser is ~ms–10s-of-ms on
   our 2 shared CPU cores. Does NLB admit a two-tier front-end (µs template/trie fast path
   [LIT: tecod-2025] + ms learned fallback + abstain), and what does that do to the
   KOT-COST vector? (Design choice, no literature blocker.)
4. **Direction/role adversarial coverage:** the measured ROLE_DIR defect gets the
   targeted deterministic repair FIRST (a5 assessment's fail-closed frame-layer fix);
   the remaining design question is how to enumerate and symmetrically test every
   directional frame — per-vertical inventory, both-orientations eval, and per-frame
   systematic-error strata [§5(c)].
5. **Composition with the verifier loop:** f2b's verify-retry and NLB's parse-abstention
   are both selective mechanisms; are their failures correlated (same host, same phrasing
   sensitivity)? Unmeasured anywhere [EXTRAPOLATION cell].
6. **Generation-from-checked-result:** H-PS's last leg (surface answer FROM the engine
   result) is cautioned by nsk1-g2d's net-harmful text append [MEASURED]; TinyGSM's
   numeric answers dodge this. Whether small hosts can verbalize checked results without
   corrupting them is an open experimental question for P3-E-PS-1.

---

## 8. Phase-1 hand-off — beads this review recommends the coordinator bd-create

*(Recommendation only — this bead runs no bd; blockers per programme rev-2 §5.)*

- **P3-D-NLB** [DESIGN, P0, blocked-by: this review — discharged as Phase-0 evidence for
  PROCEEDING, not as evidence the 0.90/S2 gate is likely to clear]. Scope: the real-
  parser re-entry (FK-NLB-3) gate instrument + front-end redesign targeting ≥0.90
  retention with S2 fail-closed per vertical, as a risk-coverage-measured
  parser+abstention system. **What this review supports:** capability-limited is the
  leading hypothesis for the dominant classes (§5a/b, net judgement §5) — do NOT rebuild
  deterministic-only; the recipe with the strongest matched-accounting record is
  fine-tuned-small-parser (intent+slot or seq2seq, 110M–1B) + grammar-constrained decode
  (local-vs-global mask divergence checked on our grammar, §4) + trie/synonym lexicon +
  trained-calibrator or conformal abstention threshold frozen pre-eval (§2, §4); the
  targeted deterministic ROLE_DIR repair applies regardless of parser class (§5c);
  two-tier µs/ms front-end is the cost shape to design first (§7.3).
  **Gate-instrument requirements the design MUST specify (the joint 0.90/2% protocol):**
  (1) define S2 precisely — unconditional P(answer ∧ wrong) vs selective risk
  P(wrong | answered): the cited literature uses both notions and they diverge exactly
  when coverage drops; (2) pre-specify calibration/evaluation sample sizes and the
  one-sided confidence rule required to establish a 2% bound at those n; (3) systematic-
  error strata, not just average risk — every relation/operator × direction × paraphrase
  family gets a minimum support and a zero/near-zero wrong allowance; (4) four-way data
  separation: model selection / confidence calibration / threshold selection / final
  evaluation on disjoint sets; (5) independent ambiguity/answerability annotation and an
  explicit clarification behaviour; (6) K>1 disjoint-source phrasings + perturbation
  suite + both-orientation directional tests + whole risk-coverage-curve reporting
  (§6.5, §5c); (7) shift stress on the guarantee itself: calibration-source vs
  deployment-source phrasing shifts, not merely random held-out paraphrases (§4).
- **P3-D-PS** [DESIGN, P1, blocked-by: this review + P3-LR-NTP]. Scope: H-PS concrete
  design — NL→DSL→execute-on-the-µs-engine→generate-from-checked-result, with calibrated
  abstention as part of the measured product. **What this review supports:** TinyGSM is
  a 1.3B existence ANALOGY for the pipeline shape (materially unmatched to H-PS, §3) and
  execution-based selection/verification is the strongest matched-inference lever
  (EGD/MBR-EXEC/LEVER, §3, with MBR-EXEC's spurious-majority caveat); execution catches
  invalid-not-wrong, so the S2 budget is carried by LAYERED controls — deterministic
  relation-semantics repair, typed/operator-specific validation, contrastive inverse
  tests, independent verification where available, and a calibrated abstention layer for
  the residual (§3, §5c/e); the design must name its protections against semantically
  valid-but-wrong programs and against renderer corruption of checked results
  explicitly; the DSL should stay inside the closed kot-query grammars where exact
  constrained decoding is checkable (§4); the open legs are generation-from-checked-
  result (§7.6) and verifier-abstention composition (§7.5).
- **P3-D-ORACLE** [DESIGN, P1, blocked-by: this review (co)]. Scope: the oracle-input
  error-decomposition protocol attributing G2→G3 loss across
  parse / retrieval-addressing / execution / generation per experiment. **What this
  review supports:** field practice attests the INGREDIENTS — gold-parse arms as the
  G2 anchor (our l3a/a5 verdicts already are that arm [MEASURED]), per-stage breakdown
  counters (our frame-miss/gazetteer-miss/mapper-abstain instrumentation is already
  field-shaped, §1), perturbation-typed robustness attribution (Dr.Spider's 17-set
  design), and ambiguity/unanswerable tagging of inputs BEFORE scoring so abstentions
  are creditable (§4, §5d) — but the complete KOT stage protocol is a DESIGN
  EXTRAPOLATION from those ingredients, not itself field-attested. The decomposition
  must oracle-ablate each stage SEPARATELY — intent/frame selection, role/direction
  binding, entity linking, DSL serialization, execution, rendering — a single gold-parse
  arm cannot localize correlated errors adequately. The protocol should mandate
  reporting the risk-coverage curve per stage, not a scalar.

**Non-recommendations (cells this review closes for Phase-1):** do not attempt grammar
induction of the target grammar (known/closed — induction's proven use is augmentation,
§4); do not rely on two-small-model deliberation for confidence (collapses with weak
verifiers [LIT: pvd-2026]); do not treat execution success as correctness (§3); and as
a project-local check (not a field-general prohibition — the bias results cover specific
constraint classes, §4), verify any locally-masked constrained decoder against the exact
global mask on our tiny closed grammar and quantify the divergence before freezing.

---

*Sources: `docs/next/lit/PARSE.sources.jsonl` — 43 entries; 36 fetched-verified at
primary venue 2026-07-11, 7 carried (6 from the 2026-07-09 prior review's [search]
verification or [memory], 1 KB-recall) and marked `verified:false` here.*
