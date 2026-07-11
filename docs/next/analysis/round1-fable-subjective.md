# Round-1 subjective analysis — where Programme-3 actually stands, and where I would point it

> **Status: SUBJECTIVE OPINION.** This is FABLE's opinionated steering analysis,
> written because the maintainer asked for one. It is explicitly labelled as
> such: **nothing here overrides any mechanical verdict, audit outcome, frozen
> object, epistemic tag, or registered ASM**. Where I state a measured fact I
> cite it inside its envelope; everything evaluative is my judgement and is
> marked **[OPINION]**. This document touches no registry record, no verdict,
> no frozen object, no bead, and registers no assumption.
> Author: Fable, chief-architect role (`kern/fable-analyst`), 2026-07-11.
> Inputs read at source, in full or at their verdict sections:
> `docs/next/feasibility-synthesis.md` (capstone, both theses
> INCONCLUSIVE-PENDING); `docs/next/programme-3-neurosymbolic-architecture.md`
> rev 2; `docs/next/arch/round1-critique-synthesis.md`;
> `docs/next/lit/{PARSE,EVAL,RAG,RULE,NTP,FUSE,SURG,STORE,SYS,TINY}.md`;
> `docs/next/design/{MF0,POWER,ORACLE,FRONT}.md`;
> `docs/next/interpretations/g3-llmproxy-v3.md` (proxy FAIL);
> `docs/next/a5-llm-refute-adjudication.md` (Gate-A re-audit REFUTE);
> the l3a-parse / a5-nl / g8 / f2b-replicate / nsk1 readings as restated by
> the capstone.

---

## 0. The evidence picture in one paragraph (facts first, so the opinions have a floor)

The engine is exact, fail-closed, µs-cheap, and ports byte-identically across
two verticals — on its own self-authored closed-grammar substrate only
[MEASURED: l3a 600/600, a5 855/855, audits CONFIRMED]. Every measured crossing
of a boundary into real input is negative: NL retention 47.6% (safe) and 41.6%
(dangerous — S2 fired at 5.0% wrong-with-provenance) [MEASURED: l3a-parse,
a5-nl]; wild-formal capture 0/1,000 [MEASURED: g8]; external-benchmark coverage
0/1,550 [MEASURED: b-cov-define-lane]; text-delivered grounding net-harmful and
residual-stream delivery echo-without-integration [MEASURED: nsk1, exploratory].
The one end-task positive (+0.1507 at ~10% cost) is alignment-confounded and
formal-input-only, and its de-confound is STILL unrun [MEASURED:
f2b-replicate + does_not_license]. Since the capstone froze, two more shoes
dropped: the g3 proxy FAILED (concordant necessity-violation 18.5%, a weak-proxy
content-validity warning on the NSM semantics themselves — warns, cannot kill)
[MEASURED: g3-llmproxy-v3 verdict, envelope-bound], and the a5-llm Gate-A
re-audit came back REFUTE on record integrity (pins + scale-language; no
measured number disturbed, but the ledger and the capstone's "audit CONFIRMED"
line are now stale) [MEASURED: the adjudication doc]. Both theses stand
INCONCLUSIVE-PENDING; there are still ZERO audited end-task wins over the
kernel-as-text null attributable to kernel content.

---

## 1. Where Programme-3 is going well vs poorly

### 1.1 Going well [OPINION]

1. **The epistemic machinery is the best thing this programme owns.** The
   external adversarial-review loop is catching real, would-have-been-fatal
   errors *before* they cost anything: the gameable ±10% bands, the TOST
   mislabel, H-DD's incorrect rotation-invariance and 80%-width→5×-bytes
   arithmetic, and — the one I rate highest — POWER rev-2's withdrawal of its
   own advertised "live define-lane kill" as a false-kill (silent zeros for
   uncensused benchmarks, non-simultaneous bounds). A programme that retracts
   its own favourite kill on methodological grounds is a programme whose
   eventual positive result I would believe. That is rare and it is worth
   money.
2. **The re-aim was right, and events have vindicated it.** ASM-0800's move —
   headline claims are system-level competitive claims; kernel-content
   attribution is an honest secondary — looked like hedging in rev 1. After
   g3-llmproxy-v3, it looks prescient: the NSM content leg is now proxy-warned
   on top of being coverage-walled and reachability-walled. The programme's
   live asset is "typed store + exact fail-closed checker + small LM", and the
   design now says so out loud.
3. **The round-1 synthesis converged the portfolio onto the right slice.** The
   P7→P1→P3/P5 concentration on code/structured domains (round1 §B.2.2: the
   coverage, reachability, and mechanism levers on ONE slice) is, in my view,
   the single best strategic paragraph produced since the NL FAILs landed.
4. **Phase-0 lit reviews are load-bearing, not decorative.** PARSE §0/§5's
   "capability-limited is the leading hypothesis; the measured front-end was a
   2014-class verbatim-lexicon architecture the field already abandoned" is
   the most valuable sentence Phase-0 bought: it converts the NL FAILs from a
   possible fundamental wall into a testable engineering hypothesis with a
   priced test. RULE's finding that decode-side executor-coupled masking is
   the only placement with repeated same-host wins independently confirms the
   CD-first ordering. And the discipline cuts both ways: STORE rev-2
   *withdrew* its own "maintenance fundamentally killed expert systems" doom
   narrative (downgraded to a material, accountable risk) — the machinery
   corrects pessimism as readily as optimism, which is what makes it credible.

### 1.2 Going poorly [OPINION]

1. **The design-to-measurement ratio is inverted.** Since l3a-parse/a5-nl read
   out, the programme has produced thousands of lines of measurement framework
   (KOT-FAIR/2, SIZE/2, COST/2, LIFE/1, threat model, frontier-builder,
   decomposition protocol — each with its own external review cycle and ASM
   block) and **zero new measurements against either wall**. Even the ~$0,
   already-named deterministic ROLE_DIR repair — the a5-nl assessment's own
   proposed fix, round1 step 1, "~$0, existing engine + CPU" — has not been
   executed. The scaffolding is genuinely good; but scaffolding compounds
   (every doc spawns reviews, revisions, ASM blocks, beads) while the walls
   sit untouched. This is the failure mode I'd flag to the maintainer as most
   under-priced: **the programme dying of process mass before its cheap
   decisive experiments run.**
2. **The keystone kill is currently un-fireable.** G1 Δ_max is advertised
   everywhere as "the cheapest decisive test in Programme-3", and K-P3v2(1)
   hangs off it — but POWER rev-2 (correctly!) refuses to emit any G1 verdict:
   with no frozen index pin, no oracle census, and no covered-baseline
   registrations, the corrected bound is Δ_max ≈ 0.81, i.e. vacuous. The
   cheapest kill is gated behind the heaviest scaffolding (P3-D-INDEX freeze,
   including the still-open abstention-scoring rule). Rigorous, and a
   scheduling own-goal at once.
3. **Every verdict-moving item is human-blocked and nobody owns the humans.**
   knull ablation, human f2b-transfer Stage-1, g2 gold, human g3/g9/M0a, the
   P2 and P7 annotation censuses — the capstone itself says the binding
   constraint is human annotation, not compute. I see no funded, owned,
   scheduled workstream to actually source annotators. The programme's rate
   of *decisive* information is currently set by an unstaffed queue.
4. **Hygiene debt at the core of the brand.** a5-llm's audit state is
   internally contradictory (ledger says CONFIRM, the 2026-07-11 re-audit says
   REFUTE, the verdict object says PENDING, no kot-audit/1 record exists), and
   the capstone cites "audit CONFIRMED per ledger". For a programme whose
   entire moat is auditability, a stale audit ledger under the flagship
   substrate comparison is small in substance and large in symbolism. Fix it.

### 1.3 The single biggest risk [OPINION]

**Coverage.** Not the NL boundary — coverage. The NL boundary is now a named,
lit-supported, capability-limited-leading-hypothesis engineering problem with a
funded attack (P1) and a quantitative kill. Coverage has neither: measured
external coverage is ~zero everywhere it has been measured (0/1,550; g8
0/1,000; m0b 0.3542 on the *friendliest* corpus), no mechanism family can beat
δ over items the store does not contain, and the portfolio's ONLY coverage
lever is P7 — a feeder resting on an unmeasured extrapolation (PROP-C), added
by the synthesis precisely because none of the nine external candidates
addressed it. If the honest normalised-scale Δ_max lands where the censuses
point, K-P3v2(1) kills every store-dependent family on any general-capability
index, and the only legitimate survivors are (a) a code/tool-weighted vertical
index where P7 can actually raise κ, or (b) nothing. The programme should
pre-position for that fork NOW (see §3.3) rather than discover it after the
index freeze. The operational shadow of the same risk: because G1 is blocked
on scaffolding, the programme could spend a quarter's runway building the
measurement cathedral for a competitiveness claim the coverage arithmetic was
always going to kill.

---

## 2. Architectural directions: most vs least promising [OPINION throughout; evidence cited]

### 2.1 Most promising

1. **The concentrated code/structured-data stack: P7 feeder → P1 front-end →
   P3/P5 loop.** This is my top pick, as a *stack*, not as three bets. Why:
   it is the unique slice where all three walls are simultaneously tractable.
   Coverage: deterministic extraction from code structure is the only
   authoring route that has EVER scaled in this programme without humans or
   LLMs (the a5 world: 855 covered queries, no-LLM extraction) [MEASURED: a5].
   Reachability: on code, much of the NL boundary dissolves into syntax (M2's
   "honest domain"; MGD lifts a 1.1B model above text-davinci-003 in RULE's
   ledger — same-host ablations, not frontier wins, but real). Mechanism: the
   programme's only audited end-task sign (f2b +0.1507 at ~10% cost) lives on
   exactly this shape [MEASURED: f2b-replicate, alignment-confounded]. A
   coherent story — "small model + deterministic world extracted from your
   codebase + exact checker beats a bigger model at matched budget on
   code/tool tasks" — is also the only W1-shaped claim I can currently
   imagine surviving the frontier-builder.
2. **P1 (CONTRACT-FRONT-END, M1+K2+W3+ambiguity-set executor).** The only
   direct wall attack, and correctly portfolio #1. The measured failure was a
   verbatim-lexicon 2014-class front-end (paraphrase stratum 0/261); the
   dangerous class was a deterministic table bug with a named ~free repair;
   the ambiguity-set executor (enumerate competing parses, execute all at µs
   cost, answer only on denotation agreement) is the single cheapest idea in
   round 1 that attacks the S2 class without trusting self-consistency.
   PARSE's honest caveat stands: no cited work jointly clears 0.90 retention
   + an S2 bound at ≤360M — this is a real bet, not a formality. I put the
   NL-boundary attack at genuinely uncertain odds of clearing the joint gate
   within N=2 redesign cycles on the family/world vertical — and materially
   better on the code vertical. Attack code first.
3. **P4 (capsule consumption test, transfer-repaired).** Cheapest new
   information per dollar in the portfolio: it prices the one unmeasured
   channel (symbolic content → model consumption) that THREE other lines
   (M3's expert input, K1's certificate-interface claim, the entire a-e2
   ~18–42% compression upper bound) silently depend on. Both outcomes steer:
   a transfer-arm pass unlocks P6 with a measured format; a fail kills the
   one-token channel and quarantines the compression story before anyone
   spends on it.

### 2.2 Middle of the field

- **P2 (claim firewall).** Keep as the diagnostic census it was demoted to.
  Its honest ceiling is small: a contradiction-only firewall cannot add
  correct answers, and its index gain is bounded by covered-contradiction
  share of baseline errors on the normalised scale. Run the annotation only
  after the abstention-scoring rule registers; do not let it drift back into
  "architecture" status.
- **P6 (routed symbolic expert / M3).** The right high-upside long shot,
  correctly sequenced last, correctly gated on P4's transfer arms. nsk1's
  delivery-without-integration result is the named ghost at this feast; the
  ≥3-width direction protocol is the right cheap way to see the ghost or rule
  it out. Keep, late, and hold the line on the equal-compute learned-expert
  control.

### 2.3 Least promising — I'll say it plainly

1. **H-DD (dimension-drop) is probably a dead end.** [OPINION, held with
   moderate-high confidence.] The prior is bad on every axis: revision 1
   contained four technical errors, all in its own favour; nothing measured
   links kernel concept vectors to any model's internal subspaces; the
   premise ("~80% of a model's dimensions correspond to droppable encoded
   concepts backfillable from a 0.35-coverage store") sits orders of
   magnitude beyond the measured coverage; and SURG found essentially no
   prior art for dropping semantically-identified parameters and backfilling
   from an external store — while judging the SAE-orthogonal-block idea "dead
   several times over" and flagging localization≠editability as the reason
   identification can look successful and still not be droppable. The
   P3-E-DD-0 gate is cheap, but "cheap" still
   displaces R-1 GPU-hours and — more scarce — design attention. My
   recommendation: DORMANT. Cancel P3-D-DD design spend now; revisit only if
   P4's transfer arms and P6's direction read both surprise positive. If the
   maintainer wants the 5× smaller model, W2 via generic retrained
   pruning+distillation of a W1 winner is the honest route.
2. **H-GNN in its general-NL form, and the W1 hypergraph.** The lit is
   unusually unanimous: GraphRAG-class construction cost and extraction error
   dominate ("frequently underperforms vanilla RAG"), our own extraction
   precision proxy is ~0.71, and the injection prior-art's interface-locality
   law plus nsk1 make "the GNN delivers but the LM doesn't use it" the modal
   outcome. FUSE's own sweep is the clincher: no fusion result in it beats a
   matched baseline under full accounting; the recurring +13–48% deltas
   shrink to +2–12% once the text host merely gets LoRA; and two independent
   causality probes found fused models reading the text, not the structure —
   the field-scale replica of nsk1. The synthesis deferred W1; I would go one
   notch further and hold P3-E-GNN-1 out of round 1 entirely — FUSE found no
   small-scale fusion-beats-text-at-matched-budget result across any depth
   sweep, and "structure wins with depth" remains a confounded hypothesis in
   both FUSE's and RAG's ledgers. Every GPU-hour it would take is
   worth more inside P1/P4.
3. **H-RULE-ACT and H-RULE-HL (deep-internal placements).** Dead-end-shaped
   until a shallow placement shows a positive: the only measured deep channel
   delivered at echo grade and integrated nothing, and text delivery was
   net-harmful. The CD→KV ordering already encodes this; my addition is just:
   do not let ACT/HL design work start at all in round 1, even speculatively.
4. **The quiet one: the broad general-capability W1 ambition itself at
   R-1/R-2.** On any honest chance/ceiling-normalised general index, κ≈0
   makes Δ_max≈0 for every whole-query mechanism — the coverage arithmetic
   will kill the general-index competitiveness claim long before any
   architecture question is reached. I regard "beat the frontier on a general
   AI index at R-1/R-2 with today's store" as effectively dead already; the
   live version of W1 is the vertical (code/tool/structured) budgeted index.
   Better to choose that deliberately now than to have K-P3v2(1) choose it
   for us. (Correctly-dead negatives worth keeping dead: W2 compiled views;
   the cascade/router — HE2 measured dead.)

---

## 3. What I would change or reprioritise right now [OPINION]

### 3.1 Run the ~$0 kills this week — stop letting scaffolding queue-jump them

In order, with owners nameable today:

1. **ROLE_DIR deterministic repair + exhaustive both-orientation table tests**
   (round1 step 1). Named fix, existing engine, CPU-only. Its absence is pure
   process debt, and it gates P1's S2 leg AND P3's mask-address safety.
2. **The knull plain-arm rewrite → the knull K-NULL ablation** (~$0–250,
   Programme-2 item). This de-confounds the ONE positive number the entire
   H-VL/P5 incumbency — and half the efficiency thesis — rests on. It is, to
   my eye, anomalous that we are designing frontier-builders around a lift
   whose attribution question is answerable for the price of a nice dinner.
   If the ablation says "generic aligned store reproduces it", the sooner the
   portfolio absorbs that the better (it strengthens the re-aim, kills
   nothing operational).
3. **Sensitivity-banded Δ_max now, verdict later.** Do not wait for the full
   P3-D-INDEX freeze to learn what the coverage arithmetic says. Publish the
   POWER rig's bound under 2–3 candidate index/δ₁ configurations (general
   suite; code-weighted suite; the SmolLM2 continuity set) as explicitly
   non-verdict sensitivity bands. The rig already refuses verdicts — good;
   bands still steer the portfolio and the §3.3 fork months earlier.
4. **P1 G2 system-seam test** (round1 step 3, ~$0–50) and **P4 consumption
   test** (cheap adapters) as the first GPU items, ahead of any parser
   fine-tune.

### 3.2 Make human-annotation sourcing a P0 workstream with an owner

Everything verdict-moving queues behind humans: g2 gold, f2b-transfer Stage-1,
human g3/g9/M0a, the P2 firewall census, P7's κ/precision census. One
workstream, one owner, one budget line (KOT-LIFE/1 already has the columns);
recruit once, amortise across all six consumers. Until this exists, the
programme's decisive-information rate is set by an accident of maintainer
availability, and every "PENDING — human-blocked" row in the capstone is a
euphemism for "no plan".

### 3.3 Pre-register the vertical-index fork before the coverage numbers force it

Decide — as a registered, pre-results decision — that if the banded Δ_max
shows the general-index W1 dead at R-1 (my expectation), the programme's W1
target becomes a **code/tool/structured vertical index** under the same
KOT-FAIR/2 machinery (frontier comparators, decontamination, sealed eval all
apply unchanged). Doing this BEFORE the numbers land is what makes it a scope
choice rather than goalpost-moving; doing it after makes it look like what
the threat model calls suite-shopping. This is the single cheapest
strategic insurance available this month.

### 3.4 Cap the scaffolding

Declare the measurement framework feature-frozen at MF0 draft-2 scope except
for: P3-D-INDEX (including the abstention-scoring rule — now the binding
scaffolding item, since three of five live entries are selective systems),
P3-E-CAL, and the minimum FRONT/1 needed for the first G4. No further
framework elaboration rounds, no new ledger dimensions, until at least one
architecture family has a G2 result. The framework is currently better than
any result it will be asked to measure; that is the wrong side to be ahead on.

### 3.5 Housekeeping that protects the brand

Reconcile the a5-llm audit state (formalise the three audits as kot-audit/1
records, correct the stale ledger line, add the capstone reconciliation note
the adjudication recommends), and land the g3-v3 capstone delta (PENDING→DONE
row + separately-labelled proxy-warning entry). Neither changes any verdict;
both close the gap between what the registry says and what is true — which is
the product.

### 3.6 What is missing entirely

- **A surface-realization layer** (NSM record → edited English) remains a
  named, unowned, unmeasured component (ASM-0702). It silently caps every
  human-facing quality claim and confounded the knull control once already.
  Small design bead, real leverage.
- **NTP's blocking "oracle/API gate", executed.** The whole executor-coupled
  line (P3 masks, P6 proof-trace curricula, NTP-style checker-in-loop
  training) presumes the µs engine can actually EMIT continuation sets, proof
  states, and traces at the needed interfaces — NTP flags this as currently
  ASSERTED, not demonstrated. Demonstrating it is a CPU-only engineering
  task; it belongs with the other ~$0 items in §3.1, ahead of any arm budget.
- **A second, genuinely different NLB redesign shape.** K-P3v2(2) grants N=2
  redesign cycles, but both currently route through one design family
  (fine-tuned parser + contracts). Pre-position a structurally different
  cycle-2 candidate now (e.g. a large-model-assisted parse as a ceiling probe
  run oracle-labelled, or clarification-dialogue selective parsing) so a
  cycle-1 failure buys information about the WALL, not about one design.

---

## 4. Are we attacking the NL wall hard enough, or building around it?

Both — and the mix is defensible in structure, not in tempo. [OPINION]

**Structurally, the wall is respected, not dodged**: NLB gates every
natural-input store leg by dependency rule (ASM-0814); oracle work is
quarantined as `oracle-diagnostic` licensing nothing; the parser is inside the
measured product (anti-l3a/a5 rule); P1 — the direct attack — is portfolio #1;
and two of six programme-kill conditions (K-P3v2(2)/(5)) fire on the wall
itself. That is the honest version of "building around": diagnostics continue
above the wall while the wall is attacked, and nothing above the wall can
convert into a claim. I endorse it.

**Temporally, the attack has not actually started.** Since the FAILs landed,
the wall has received: lit review (excellent), design documents (good), and
zero experiments — while the measurement framework received four full design
cycles with external review. The ~$0 named repair for the DANGEROUS failure
mode is still unexecuted. The honest characterisation: we are building the
courtroom before running the cheap forensic tests. The fix is calendar, not
architecture — steps 1/3/4 of the round-1 order are fundable today inside the
free pool, and step 4 (the parser fine-tune, ≤~50 GPU-h) needs nothing from
the G4 scaffolding stack by the programme's own sequencing exemption.

One more tempo point: the wall is not uniform, and the attack order should
exploit that. On the code vertical the boundary is partly syntax (and the
dangerous defect was a table bug); on family/world it is genuine open-domain
paraphrase (0/261). Spend redesign cycle #1 where the wall is thinnest and the
payoff stack (P7 coverage + f2b mechanism) is co-located: **code first,
family/world second**.

---

## 5. Bottom line [OPINION]

The programme's instruments, honesty machinery, and portfolio logic are in the
top percentile of anything I could design; its tempo against its own two walls
is not. The most promising direction is the concentrated code/structured-data
stack (P7 deterministic-extraction feeder + P1 contract front-end + P3/P5
verifier loop) — the only place where coverage, reachability, and a measured
mechanism positive coincide. The clearest probable dead ends are H-DD, general-
NL graph fusion, deep-internal rule placements, and — quietly — the general-
index W1 ambition itself at current coverage. The top changes: run the ~$0
kills now (ROLE_DIR repair, knull ablation, banded Δ_max, seam + consumption
tests), stand up an owned human-annotation pipeline, pre-register the
vertical-index fork, and freeze the scaffolding until some architecture has a
G2 result. The biggest risk is coverage — with an unmeasured feeder as the
only lever against it — compounded operationally by process mass consuming
runway before the decisive experiments run. None of this moves a verdict;
all of it is where I would put the next dollar.
