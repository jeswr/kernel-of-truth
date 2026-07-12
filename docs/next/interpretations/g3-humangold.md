# FABLE INTERPRETATION — G3 human PASS-A gold (mechanical verdict-INPUT, no verdict issued: necessity violations 46/200 = 0.230, Wilson LB 0.1848 > 0.10 — the frozen FAIL/kill row is DECIDABLE and direction-invariant across five label-source configurations, but every violation quantity is PROVISIONAL-ON-LLM-PROXY pending human Pass B, the sole HS3 adjudicator; sufficiency 18/200 = 0.090, LB 0.0620 / UB 0.1290 — the frozen INCONCLUSIVE band; human-vs-GPT-5.6 q1 agreement κ = 0.756 — validates the q1 FACE of the proxy only; neither programme thesis moves)

> **QUARANTINE (ASM-0553), riding this document in full:** this document restates and
> interprets proxy-derived quantities from `poc/g3/`. Do NOT expose this document, the
> analysis doc, or any `poc/g3/` artifact to the g3 human annotator(s) before human A1
> Pass B and annotator A2's full round are complete. Exposure would contaminate the sole
> adjudicating instrument of HS3.

- **Author:** Fable (interpretation agent), 2026-07-11. The runner produced the measured
  artifacts and the analysis doc; the coordinator owns the mechanical verdict step, which
  has NOT been taken — `registry/verdicts/` contains `g3-llmproxy-v3.json` (the earlier
  pure-proxy run) and NO human-gold g3 verdict object [MEASURED: directory state,
  2026-07-11]. This document interprets a verdict-INPUT and issues nothing. It changes NO
  frozen record, NO verdict object, NO results-log line, NO registered assumption; it runs
  no experiment, no git, no bd, no kb-sync. The coordinator commits.
- **Sources (read at source, in full):** `poc/g3/result.json`, `poc/g3/metrics.json`,
  `poc/g3/analysis-output.json`, `docs/next/analysis/g3-result.md` (authoritative for
  every number below; nothing is recomputed here); `registry/experiments/g3.json` (FROZEN,
  frozen_sha256 `ef9608c6…` — the kill criterion, verdict rules, and extrapolation
  envelope, BINDING on every line below); `docs/research-plan/01-hypotheses-experiments.md`
  §HS3 (the hypothesis statement); `docs/next/interpretations/f2b-transfer-stage2.md` and
  `docs/next/interpretations/deconf-a1.md` (the composition partners for §5, each restated
  at pointer level with its own conditionality intact).
- **Epistemic discipline:** every load-bearing line carries its `[TAG]` on the same
  logical line. **MEASURED** restates a measured/computed fact strictly from a cited
  artifact (never recomputed); **PROVISIONAL-ON-LLM-PROXY** marks any quantity or reading
  that rests on the pinned LLM stand-in for the missing human seats (q2 and annotator A2)
  — it is the governing tag of this document's central result; **STIPULATED** marks
  frozen-design text, registered rulings, and framing adopted verbatim; **DERIVED** marks
  this document's own rule-application or counting over published artifact fields,
  disclosed as absent from the cited artifacts; **INTERPRETIVE INFERENCE** marks an
  inference of this document, never a fact of the record; **ASSUMED/EXTRAPOLATION** are
  direction-only and load-bearing for nothing.
- **The governing conditionality, stated first:** human annotator A1 has completed Pass A
  (q1) ONLY. Pass B (q2) is NOT DONE; annotator A2 has NOT STARTED [MEASURED:
  result.json `annotation_state`]. Every necessity/sufficiency violation count below is a
  conjunction of a human q1 judgment with a PROXY q2 judgment. Human Pass B is the sole
  HS3 adjudicator and alone converts PROVISIONAL to MEASURED [STIPULATED: the weak-proxy
  stand-in policy ASM-0550/ASM-0530, restated in result.json; the frozen two-human
  instrument has not yet been computed from human data]. On a Pass-B outcome that
  overturns the direction, this document's §2 is void and must be superseded, not edited.

---

## 0. The mechanical facts, restated (all from `poc/g3/` artifacts unless noted)

- PREMISE: [MEASURED: g3-result.md §1; poc/g3/human-passA-a1-q1.json] Human annotator
  **A1 Pass A COMPLETE**: 200/200 q1 concept-applicability judgments — **163 yes / 29 no /
  8 cannot-say** (4.0% cannot-say, under the protocol's 5% re-examination trigger). One
  extraction anomaly is on record (10 answered rows relocated above the sheet header;
  flagged for coordinator confirmation with the annotator) and rides the q1 extraction as
  a data-integrity flag, not a finding.
- PREMISE: [MEASURED as computed; PROVISIONAL-ON-LLM-PROXY as evidence] **Necessity
  (primary endpoint), hybrid annotator = human q1 × GPT-5.6 q2, protocol-proposal mapping,
  n = 200: 46 violations, rate 0.230, Wilson LB 0.1848, UB 0.2824** (z = 1.645 per the
  pinned script `analysis/g3.py`, sha `eac8fd81…` verified, selftest OK). Against the
  frozen `verdict_rules`: `necessity_wilson_lb 0.1848 > 0.10` — **the FAIL row matches;
  the kill side is decidable** on these inputs, with `instrument_valid` TRUE on both
  n = 200 mappings [MEASURED: analysis-output.json A1/A2].
- PREMISE: [MEASURED as computed; PROVISIONAL-ON-LLM-PROXY] **Direction invariance** of
  the necessity result across every available label-source configuration: decisive-only
  mapping 46/192, LB 0.1928; Haiku-4.5 substituted at q2 65/200, LB 0.2732; pure GPT-5.6
  proxy 49/199, LB 0.1996; the earlier frozen llmproxy-v3 verdict (concordant-pair rule)
  36/195, LB 0.1433, FAIL-analog [MEASURED: metrics.json; g3-result.md §2]. Five
  configurations, five lower bounds, all above 0.10.
- PREMISE: [MEASURED as computed; PROVISIONAL-ON-LLM-PROXY] **Sufficiency (secondary,
  the equivalence reading), hybrid n = 200: 18 violations, rate 0.090, Wilson LB 0.0620,
  UB 0.1290.** UB > 0.10 so the survives rule does not fire
  (`sufficiency_equivalence_survives` = false); LB ≤ 0.10 so the kill does not fire —
  **the frozen INCONCLUSIVE band** ("buys more annotations, not a verdict")
  [MEASURED: analysis-output.json; STIPULATED: the frozen rule text].
- PREMISE: [MEASURED — this is the document's one fully human-anchored number]
  **Human-vs-proxy agreement on q1**: human vs GPT-5.6-Sol exact 3-way 0.895 (179/200),
  decisive agreement 0.9372 (n = 191), **Cohen's κ = 0.7561**, 12 disagreement items,
  disagreement table symmetric (h_yes_p_no 6 / h_no_p_yes 6); human vs Haiku-4.5 exact
  0.870, decisive 0.9202 (n = 188), κ = 0.7069, 15 items, mildly asymmetric (Haiku says
  "no" more: 10 vs 5) [MEASURED: metrics.json `q1_agreement_*`].
- PREMISE: [MEASURED: analysis-output.json; g3-result.md §2] **Instrument gates:** hybrid-vs-Haiku (independent label sources)
  κ = 0.5248; hybrid-vs-GPT-5.6 κ = 0.8758, structurally inflated (the pair shares q2)
  and not citable as agreement evidence. Both ≥ 0.4, so no INSTRUMENT-INVALID trip on the
  n = 200 mappings; the decisive-only mapping's `instrument_valid` = false is the
  n ≥ 200 gate reacting to n = 192 — a mapping artifact, not an instrument finding. The
  true two-HUMAN κ of the frozen instrument remains unmeasured [MEASURED:
  analysis-output.json; g3-result.md §2].
- PREMISE: [MEASURED: metrics.json `hybrid_violation_ids`; DERIVED: the counts;
  PROVISIONAL-ON-LLM-PROXY: the violation set itself rests on proxy q2] the 46
  hybrid necessity violations touch **18 of the 20 concepts** (only *begin* and *give*
  are violation-free), with concentration in *reminder* (6/10 instances) and *useful*
  (4/10); the remaining 36 violations spread over 16 further concepts. On these
  provisional inputs the signal is broad-based with two hot spots, not a two-bad-pins
  artifact.
- PREMISE: [STIPULATED: ASM-0181 — registry n_planned] n = 200 was powered ≥ 0.90 to distinguish a
  true 10% from a true 20% violation rate at α = 0.05; the observed 0.230 sits beyond
  the powered alternative. The design had the power to see what it saw.

## 1. The frozen frame, quoted verbatim — BINDING on every sentence below

The kill criterion [STIPULATED: `kill_criterion_verbatim`, registry/experiments/g3.json]:

> "Necessity failures >10% ⇒ defeasible-script stands, Π is lint, and HS2 auto-resolves
> to sidecar-only. Sufficiency failures >10% ⇒ equivalence dead, necessary-conditions
> only. Test: each rate against its 10% threshold by exact binomial with Wilson 95%
> bounds over the full judgment set (~200 instance judgments: powered ≥0.9 to distinguish
> a true 10% from a true 20% rate at α=0.05); a 'survives' verdict requires the Wilson
> upper bound ≤10%, a kill requires the lower bound >10%, anything between is
> INCONCLUSIVE and buys more annotations, not a verdict. Inter-annotator κ reported."

The extrapolation envelope [STIPULATED: `extrapolation_envelope_verbatim`]:

> "P1 §4b row HS2–HS8 (verbatim): Measured range: R0 — no host model. Reasonable
> extrapolation envelope: Model-scale-free (properties of the kernel formalism); the
> relevant axis is KERNEL size: verdicts on 54–10³ records re-checked at 10⁴–10⁵ during
> bulk authoring (G6/G7 re-run as regression). Literature anchor + licensing assumption:
> Formal-fragment properties don't vary with observer scale; only corpus composition
> shifts them."

Scope consequences, applied before anything is read into the numbers [DERIVED:
rule-application of the envelope]: g3 is an R0 instrument with no host model — nothing
here is about any model, any lift, or any runtime. Its object is the kernel FORMALISM's
semantic claim on THIS pinned kernel instance (kernel-v0, hash `8209cada…`), THIS pinned
materials set (20 concepts × 10 instance descriptions), THIS annotation protocol, and —
for the human component — ONE annotator's Pass A. The envelope's own licensing assumption
("only corpus composition shifts them") cuts both ways: it licenses model-scale-free
reading of a verdict, and it warns that a different concept sample could shift the rates;
the 20 pinned concepts ARE the measured range, and the observed concept-level clustering
(§0) is a live reminder that the instance-level Wilson bound does not license
concept-population generality beyond them [INTERPRETIVE INFERENCE, bounded to a caution].

## 2. The necessity result: what a 23% violation rate means for the correctness thesis

**What HS3's necessity reading claims** [STIPULATED: HS3 statement + registry DV
definition]: "explication = necessary conditions" (C ⊑ Π(C)) — every instance falling
under concept C satisfies the pinned explication conditions Π(C). A necessity violation
is an instance the annotator judges to fall under C (q1 = yes) whose pinned conditions
are judged unsatisfied (q2 = no). The measured hybrid rate of such violations is 0.230
with Wilson LB 0.1848 [MEASURED as computed; PROVISIONAL-ON-LLM-PROXY].

**The precise reading** [INTERPRETIVE INFERENCE from §0 within the §1 frame]: on these
inputs, the kernel's semantic pins, read as strict necessary conditions of ordinary
usage, are violated on roughly a quarter of judged instances — nearly two and a half
times the frozen tolerance, with the entire 95% interval above the kill line. If human
Pass B confirms, the necessary-conditions reading of Π is dead at this kernel instance,
and the frozen consequence chain fires exactly as pre-registered: **the defeasible-script
reading stands, Π is demoted to lint, and HS2 auto-resolves to sidecar-only**
[STIPULATED: kill criterion verbatim]. Conditional on that Pass-B confirmation, this
would be a genuine negative on the semantics-necessity axis of the correctness thesis:
the kernel's formal claim that its explications state what MUST hold whenever a concept
applies would not survive contact with instances as pinned
[PROVISIONAL-ON-LLM-PROXY: the violation set rests on proxy q2; void if Pass B
overturns the direction].

**One conflation must be blocked here** [DERIVED: a scope distinction this document
insists on]: "the pins are not necessary as pinned" is a claim about the LOGIC of the
kernel's semantic annotations — instances of C fail Π(C). It is NOT the claim that the
kernel's semantic content is unnecessary for downstream value; that question (does
kernel-grade authoring matter for the F2-line lift?) belongs to knull-v2 and DECONF
Stage B's Δ_align, and nothing in g3 measures it. G3 impugns the pins' modal status, not
the content's usefulness.

**How strong is the evidence, given PROVISIONAL-ON-LLM-PROXY?** Two forces, stated
honestly and in tension:

- *For robustness* [MEASURED: §0 direction invariance]: the kill-side direction survives
  every available perturbation of the label sourcing — two cross-family q2 proxies
  (GPT-5.6, Haiku), the decisive-only mapping, both pure-proxy legs, and the earlier
  frozen llmproxy-v3 concordant-pair rule; the LOWEST of the five lower bounds (0.1433)
  still clears 0.10 by a wide margin. The human's own Pass-A contribution moves the
  estimate DOWN relative to the pure proxies (hybrid 0.230 vs pure GPT-5.6 0.246, pure
  Haiku 0.303) — the human q1 is not the source of the signal's size, and for the human
  Pass B to undo decidability it would have to overturn the proxy's clause-satisfaction
  judgments on a substantial fraction of the 46 flagged items while flagging few new
  ones, systematically and in one direction, against two model families that agree in
  direction [DERIVED: reading of the §0 configuration table; no flip threshold is
  computed here].
- *Against overconfidence* [DERIVED; the honest counterweight, and the reason the
  PROVISIONAL tag governs]: q2 is a DIFFERENT and plausibly harder judgment than q1 —
  clause-level satisfaction of NSM explication text against an instance description,
  rather than ordinary-usage concept applicability — and NO human q2 exists to validate
  the proxy's q2 face. The measured q1 κ (§3) does not transfer to q2. And cross-family
  proxy agreement does not exclude the main threat model: a SHARED error mode — e.g., an
  over-literal reading of NSM clauses that both LLM families apply alike — would leave
  the direction invariant across every configuration above while still being wrong
  against a human reader. The robustness checks available are real but do not span the
  threat that matters most; only Pass B spans it.

Net assessment [INTERPRETIVE, this document's own]: the necessity result is the
strongest PROVISIONAL negative the programme has on the kernel's formal-semantics axis —
decidable under the frozen rule, direction-robust across everything measurable today,
and correctly withheld from verdict because the one unmeasured face (human q2) is
exactly where a principled reversal would live. It should steer expectation (and the §8
priorities), and it must not be cited as a g3 FAIL until Pass B lands.

The concept-level texture sharpens, without deciding, the repair question [MEASURED ids;
DERIVED counts; INTERPRETIVE reading; PROVISIONAL-ON-LLM-PROXY throughout — the
violation set rests on proxy q2]: violations in 18/20 concepts would say, if Pass B
confirms them, that the problem is not confined to a few defective records — the
necessity reading itself would over-claim at the formalism level. The
*reminder*/*useful* concentration (10 of 46 in 2 concepts) would likewise say pin
quality varies — some records over-claiming worse than others. If Pass B confirms
the kill, the pre-registered demotion (Π as lint — a quality-assurance annotation, not a
sound modal claim) fits both observations at once; per-record repair alone would not.

## 3. The sufficiency band: inconclusive by rule, asymmetric as texture

The equivalence reading (C ≡ Π(C)) required sufficiency violations ≤ 10% as well; the
measured band (rate 0.090, LB 0.0620, UB 0.1290) decides neither rule: the point
estimate sits below the threshold, but the upper bound does not clear it and the lower
bound does not breach it — the frozen INCONCLUSIVE outcome, which "buys more
annotations, not a verdict" [MEASURED as computed, PROVISIONAL-ON-LLM-PROXY; STIPULATED:
the rule text]. The owed annotations (Pass B, A2) are already owed for the necessity leg;
no new spend decision arises from this band [DERIVED].

Two readings ride the band as texture, neither as verdict:

- **The asymmetry is diagnostic** [INTERPRETIVE INFERENCE from the two rates;
  PROVISIONAL-ON-LLM-PROXY: both rates rest on proxy q2]: necessity violations (0.230)
  outnumber sufficiency violations (0.090) two-and-a-half to one, in every configuration
  [MEASURED as computed; PROVISIONAL-ON-LLM-PROXY: metrics.json — Haiku q2 0.075, pure
  GPT-5.6 0.106, pure Haiku 0.082]. On these provisional inputs the pins would err on
  the side of OVER-strength: when the pinned conditions hold, the concept (mostly)
  applies; when the concept applies, the pinned conditions frequently fail — the
  explications would demand too much, not too little, if Pass B confirms the pattern.
  This is
  precisely the failure signature the defeasible-script reading predicts for
  prototype-style concepts formalised as strict conjunctions [ASSUMED: the
  literature-shaped gloss, direction-only, load-bearing for nothing].
- **The band is largely moot conditional on the necessity kill** [DERIVED: logic of the
  frozen readings]: equivalence entails necessity, so a confirmed necessity FAIL kills
  equivalence a fortiori regardless of where the sufficiency rate settles. What the
  sufficiency endpoint would still inform, post-kill, is the residual one-directional
  reading — whether Π(C) at least soundly IMPLIES C (pins as sufficient conditions) —
  which is a live question for what "Π as lint" can still be used for. On today's band,
  that reading is neither established nor excluded.

## 4. The proxy-validation result: what κ = 0.756 does and does not license

The one fully human-anchored measurement of this run is the q1 agreement table
[MEASURED: §0]: GPT-5.6 matches the human annotator on the ordinary-usage
concept-applicability judgment at κ = 0.7561 (89.5% exact over three categories, 93.7%
on mutually decisive items), with a direction-symmetric disagreement table (6/6);
Haiku-4.5 at κ = 0.7069 with a mild conservative skew (says "no" 10 vs 5). By the
conventional banding this is "substantial" agreement, short of "almost perfect"
[DERIVED: banding label only].

**What this licenses** [INTERPRETIVE, bounded clause by clause]:

- It upgrades the weak-proxy stand-in policy (ASM-0550/ASM-0530) from ASSUMED to
  measured-at-one-face: for judgments of the q1 TYPE — ordinary-usage concept
  applicability over short instance descriptions — GPT-5.6 tracks this human at ~90%
  with no directional bias detected. That is real support for leaning on GPT-5.6 for
  triage and provisional direction on the OTHER annotation legs (g2's HS2 instruments,
  and interim g3 sensitivity work), which may proceed under the same
  PROVISIONAL-ON-LLM-PROXY tag they already carry.
- **It validates the q1 FACE only.** No human q2 exists; the proxy's clause-satisfaction
  judgments — the face on which THIS document's central result rests — are unvalidated
  against any human, and q2 is the harder, more literalism-sensitive task (§2). Citing
  κ = 0.756 in support of proxy q2 would be a face-transfer error; this document does
  not, and no programme prose should.
- It does not transfer across item distributions or protocols without re-validation:
  the κ is measured on THESE 200 templated instance descriptions, THESE 20 concepts,
  THIS protocol, ONE human. Some share of the 10.5% disagreement may be A1 idiosyncrasy
  — the human-human κ is unmeasured, so the proxy's ceiling against "the human
  consensus" is unknown in both directions.
- **Near-threshold verdicts remain out of the proxy's reach** [DERIVED: reading of the
  measured q1 disagreement rate against the frozen thresholds]: on the one validated
  face, a judge that disagrees with the human ~10% of the time cannot, alone, settle a
  rule whose kill line sits at 10%. Where a frozen verdict is at stake and the measured
  quantity is within a proxy-disagreement's width of its threshold — exactly the g3
  sufficiency band, and plausibly parts of g2 — human gold is not optional. For q2 the
  point is stronger, not weaker: no human q2 error rate has been measured, so
  κ = 0.756 supplies NO quantitative calibration for the proxy's q2 judgments — near
  the band or far from it — and nothing here licenses treating the necessity result's
  distance from the kill line as a buffer against q2 error (per §2, shared-mode q2
  error is not excluded by any agreement number).

## 5. Composition with f2b-transfer and DECONF — a labelled implication, not a conclusion

The three results now on the table, each with its own conditionality that MUST ride any
citation:

- **f2b-transfer stage 2** (PASS-PENDING-AUDIT, conditional on Gate-A audit): the
  kernel-AUTHORED aligned answer key's content lifts a 135M host +0.2507 on blind
  external gold; content-specific (shuffled control), better-than-commodity (RT-2)
  [MEASURED: f2b-transfer-stage2.md §0, restated at pointer level].
- **DECONF A1** (EXPLORATORY, registration pending): C_dec = 1.0 over 40,576/40,576
  decision cells [MEASURED: deconf-a1.md §0, restated]; the reading that the kernel's
  runtime STRUCTURE is therefore inert — every runtime decision extensionally computable
  from the projected answer key alone, the lift surviving as an aligned-answer-key
  property — is DECONF's stipulated/derived extensional interpretation, itself
  EXPLORATORY pending registration [STIPULATED/DERIVED per deconf-a1.md, restated with
  its conditionality intact].
- **g3 human-gold** (PROVISIONAL-ON-LLM-PROXY, pending Pass B): the kernel's semantic
  pins, read as strict necessary conditions, are violated at ~23% against human-anchored
  ordinary usage — kill-side decidable, direction-robust [§0, §2].

**The composite picture, labelled as implication** [INTERPRETIVE INFERENCE from the
three results read against their frozen frames and their own tags; void wherever any
leg's conditionality resolves against it]: the three results cohere into a single, sharpening
story — **the kernel's demonstrated value lives in its authored surface content; its
formal-semantic apparatus is, so far, doing no measured work and now looks unsound in
its strongest reading.** DECONF showed the runtime never consumes Π's structure (the
checker's decisions reduce to the projected answer key); g3 now indicates that even if
something DID consume Π as a strict necessity logic, that logic over-claims against
human usage on this instance set. The two negatives brace each other from opposite
sides: nothing uses the pins' modal content at runtime, and the pins' modal content, as
pinned, appears not to hold. Meanwhile the programme's one strong positive is precisely
NOT impugned: f2b's lift is carried by gloss/claim strings consumed as an answer key,
and stage 1's blind endorsement (A = 0.961) certified that content at the answer grain.
There is no contradiction between "the content is true enough as answers" (f2b, answer
grain) and "the content over-claims as necessary conditions" (g3, clause-logic grain) —
they are different grains of the same records, and the grain distinction is exactly
where the composite lands: **value in authored content; the specific semantic pins, as
strict necessity claims, not sound — and per the frozen consequence, demotable to lint
without touching the answer-key channel** [components carry their own distinct
statuses as cited — f2b PASS-PENDING-AUDIT, DECONF EXPLORATORY (C_dec measured, the
inertness reading exploratory pending registration), g3 PROVISIONAL-ON-LLM-PROXY; the
composition INTERPRETIVE and conditional on all three].

Programme-shape corollary [DERIVED from the composite + the frozen tier table, which
pre-priced this outcome: "G3-kill (defeasible) auto-resolves HS2→sidecar-only and
demotes Π to lint… None of these blocks Tier 1" — STIPULATED:
docs/research-plan/01-hypotheses-experiments.md, phase-0 row]: a confirmed g3 kill is a
bounded demotion inside the plan, not a programme kill. It would formalise what DECONF's
deflationary implication already suggested — that the F2 line's honest name is
"aligned-answer-key verify-retry" — by removing the last standing reason to treat Π as a
binding runtime logic rather than an authoring-QA discipline. What would re-inflate the
formal-semantics axis is unchanged and enumerable: a Pass-B reversal here, or an
alignment-specific Δ_align residue in DECONF Stage B attributable to kernel-side
structure [ASSUMED: direction-only].

## 6. NOT licensed — the envelope applied clause by clause

- NO verdict: the kill row MATCHES on provisional inputs; no g3 verdict object exists
  and none is licensed until human Pass B lands and the coordinator runs mechanical
  verdict-gen [MEASURED: registry/verdicts/ state; STIPULATED: the runner/verdict role
  split].
- NO claim about model behaviour at any scale: R0, no host model; g3 is about the
  formalism, not about any lift [STIPULATED: envelope].
- NO concept-population generality beyond the 20 pinned concepts: the envelope's own
  licensing assumption makes rates corpus-composition-sensitive; the measured clustering
  (§0) underlines it. Verdicts on 54–10³ records are re-checked at 10⁴–10⁵ during bulk
  authoring (G6/G7 as regression) — extrapolation to bulk kernels is the plan's owed
  re-check, not this document's claim [STIPULATED: envelope].
- NO validated proxy q2: κ = 0.756 is a q1-face number only (§4). Any use of the
  GPT-5.6 stand-in on q2-type judgments retains full PROVISIONAL-ON-LLM-PROXY status.
- NO two-human instrument: the frozen design's two-annotator table and its κ remain
  unmeasured; the κ-gate passes today only on hybrid pairings, one of which (0.876) is
  structurally inflated and citable for nothing [MEASURED: §0].
- NO bearing on knull-v2 / Δ_align / authoring economics: g3 says nothing about whether
  kernel-grade authoring is necessary for the answer key's value (§2's conflation
  block).
- NO exposure of this analysis to the annotator(s) before Pass B/A2 complete
  [STIPULATED: ASM-0553 — the quarantine banner governs].

## 7. Does either thesis move? Explicit judgement, conservative

JUDGEMENT [INTERPRETIVE, this document's own]: **neither thesis moves.
Both the correctness thesis and the efficiency thesis remain INCONCLUSIVE-PENDING.**

- **Correctness:** g3's necessity result is a PROVISIONAL kill-side signal on ONE axis
  of the thesis — the formal-semantics (necessity) axis — awaiting its sole adjudicator
  (human Pass B). Even confirmed, it demotes a reading of the pins per a pre-registered,
  pre-priced consequence chain; it does not void the authored-content positives (f2b
  stages 1–2, themselves audit-conditional) and does not touch the untouched decisive
  legs (g2, the NL axis). A thesis does not move on a provisional input to an unissued
  verdict [DERIVED: rule-application of the programme's verdict discipline].
- **Efficiency:** g3 is efficiency-irrelevant by design (`efficiency_relevant`: false;
  R0, ~$0) [MEASURED: registry]. No leg moves.

What HAS changed is the expected shape of the correctness thesis's resolution
[INTERPRETIVE]: before this run, "the kernel's semantics pins survive contact with
instances" was an open empirical question with a proxy-only negative; it is now a
direction-robust, human-q1-anchored, kill-side-decidable PROVISIONAL negative with one
face left to measure. The correctness thesis's live hopes concentrate accordingly in the
authored-content channel (f2b line, knull-v2 attribution) rather than the
formal-necessity channel — a redistribution of expectation, not a verdict.

## 8. Recommendations (no action taken here; coordinator/maintainer to route)

1. **Complete the instrument: human A1 Pass B is the single highest-leverage annotation
   hour in the programme right now** — it converts the primary endpoint to MEASURED,
   licenses the mechanical verdict either way, and (per §2) is the only measurement that
   can span the shared-proxy-error threat model. A2's round then supplies the frozen
   two-human κ. [ASSUMED: prioritisation, the maintainer's call.]
2. **Maintain the quarantine** (ASM-0553) on every g3-derived artifact — including this
   document — until Pass B and A2 are complete; route the relocated-rows sheet anomaly
   to the annotator for confirmation through a channel that does not expose analysis
   content.
3. **No verdict, no ledger move, no sparq framing of g3 as FAIL** until Pass B +
   mechanical verdict-gen; interim citations must carry PROVISIONAL-ON-LLM-PROXY
   verbatim.
4. **Pre-position the consequence chain:** if Pass B confirms, HS2's auto-resolution to
   sidecar-only and the Π-as-lint demotion fire by frozen rule; the coordinator should
   have the HS2 record's routing ready so the resolution is applied mechanically, not
   re-argued.
5. **Cite κ = 0.756 carefully programme-wide:** as measured support for GPT-5.6 q1-type
   stand-ins (g2 triage), never as validation of q2-type judgments, and never as
   sufficient for near-threshold verdicts (§4). Consider registering this as the
   stand-in policy's measured anchor.
6. The sufficiency band resolves with the same owed annotations; no separate spend.

---

## Epistemic register (what this interpretation relied on)

- **MEASURED (restated, never recomputed):** human A1 Pass A 200/200 (163/29/8, 4.0%
  cannot-say); necessity 46/200 = 0.230, Wilson LB 0.1848 / UB 0.2824; sensitivity legs
  (46/192 LB 0.1928; 65/200 LB 0.2732; 49/199 LB 0.1996; llmproxy-v3 36/195 LB 0.1433);
  sufficiency 18/200 = 0.090, LB 0.0620 / UB 0.1290, `sufficiency_equivalence_survives`
  false; κ gates 0.5248 (independent) / 0.8758 (inflated, shared q2); q1 agreement
  human-vs-GPT-5.6 0.895 / 0.9372 / κ 0.7561 (6/6 symmetric), human-vs-Haiku 0.870 /
  0.9202 / κ 0.7069 (10/5); `instrument_valid` TRUE on both n = 200 mappings, false on
  n = 192 as an n-gate artifact; the violation-id lists; annotation state (Pass B not
  done, A2 not started); registry/verdicts/ contains no human-gold g3 verdict object;
  the f2b and DECONF figures restated from their own interpretation documents at pointer
  level.
- **PROVISIONAL-ON-LLM-PROXY (the governing tag):** every necessity and sufficiency
  violation quantity and the kill-side decidability reading — all rest on GPT-5.6 (or
  Haiku) q2 with human Pass B absent; likewise the §5 composite wherever it leans on the
  g3 leg.
- **STIPULATED:** the kill criterion and extrapolation envelope (quoted verbatim, §1);
  the verdict rules; the HS3 statement; the cannot-say mapping (the protocol's own
  proposed rule) and decisive-only sensitivity precedent; the weak-proxy stand-in policy
  (ASM-0550/ASM-0530); the ASM-0553 quarantine; the tier-table pre-pricing of a G3 kill;
  n-planned power.
- **DERIVED (this document's own, disclosed):** the 18/20-concepts violation spread and
  the 10-of-46 concentration counts (counted from the published id lists); the
  necessity-vs-usefulness conflation block (§2); the equivalence-entails-necessity
  mootness note (§3); the near-threshold proxy-inadequacy reading (§4); the §5
  programme-shape corollary; the §7 thesis-movement determinations.
- **INTERPRETIVE INFERENCE:** the §2 central reading and net assessment; the §3
  over-strength asymmetry reading; the §4 licensing clauses; the §5 composite picture
  ("value in authored content; specific semantic pins not sound as strict necessity");
  the §7 redistribution-of-expectation note.
- **ASSUMED/EXTRAPOLATION (direction-only, load-bearing for nothing):** the
  prototype-concepts gloss (§3); the re-inflation enumeration (§5); the §8
  prioritisation.

*This interpretation changes no frozen object, no verdict, no log, and no registered
assumption. Its central reading is PROVISIONAL-ON-LLM-PROXY in its entirety: on the
measured-plus-proxy inputs, the kernel's semantics pins fail the necessary-conditions
reading decisively and robustly in direction — and the one judgment that can make that
finding real, human Pass B, has not yet been made. Until it is, g3 says: expect the
kill, withhold the verdict, and keep the annotator blind.*
