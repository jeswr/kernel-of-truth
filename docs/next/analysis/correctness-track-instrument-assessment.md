# Correctness-track instrument assessment — after the fourth and fifth instrument stops (Fable)

**Role: Fable INTERPRETATION agent, 2026-07-12. This document assesses the
repeated failure of the CORRECTNESS track's host-integration instruments —
the RULES host-lift lineage (rules-1 → rules-1-b → rules-1-c) and the
g2-import-v2 typing-repair pilot — against what HAS instrumented cleanly.
It states NO feasibility conclusion on either thesis: that synthesis belongs
to the cross-experiment feasibility node (kernel-of-truth-d8p8/m90m), and
the host-integration slot decision belongs to the maintainer's open issue
#24, which this document informs and does not pre-empt.** Companion to
`docs/next/analysis/rules1c-instrument-invalid-interpretation.md` (the
rules-1-c instrument post-mortem) and
`docs/next/analysis/steering-read-fable-2026-07-12b.md` (the steering
opinion this partially overlaps; divergences are flagged where they occur).

Epistemic tags: **[MECHANICAL]** = a pinned-analysis or verdict-gen output
reported verbatim; **[MEASURED]** = read directly from committed bytes this
tick; **[DERIVED]** = follows from measured bytes by stated arithmetic or
code-reading; **[REPORTED]** = taken from a coordinator brief or companion
document, not independently resolvable here; **[COUNTERFACTUAL]** = a
what-if under stated assumptions, never evidence; **[ASSESSMENT]** = this
agent's judgment; **[SUBJECTIVE]** = opinion, explicitly weighed as one
model's opinion, binding on nothing.

**Sources read at source this tick:**
`docs/next/analysis/rules1c-instrument-invalid-interpretation.md`;
`docs/next/analysis/steering-read-fable-2026-07-12b.md`;
`docs/next/design/g2-import-v2-repair.md` (§§1–12, incl. the §11 κ-paradox
redesign); `poc/ontology-import-g2-v2/runs/real-20260712-auth/{result.json,
pilot-status.json}`; `poc/ontology-import-g2-v2/runs/pilot-20260712-ac1/
{README.txt,pilot-status.json}`; `poc/ontology-import-g2-v2/run-ontg2v2.py`
(header + pins); `analysis/ontg2v2.py` (the `agree_stats`/`kappa`
implementations); `registry/verdicts/f2b-transfer.json` (PASS, audit
CONFIRMED); `registry/verdicts/deconf-b.json` (PASS, audit CONFIRMED);
`registry/experiments/g2-import-v2.json` (status FROZEN);
`docs/next/design/post-rules1c-critical-path.md` (grep-verified §2/§5
anchors). Issue #24 could not be resolved via `bd show 24` (consistent with
the steering read's identical failure); its content is [REPORTED] from the
critical-path doc's maintainer-gated action 4.

---

## 0. The ledger, verified

### 0.1 What failed to instrument (both correctness sub-tracks)

**RULES host-lift — three instrument failures, one lane.** [MECHANICAL/MEASURED]

| iteration | verdict | failing interface |
|---|---|---|
| rules-1 | VOID | elicitation: direction-unstated cue + menu adjacency; all arms 0.000 incl. the oracle arm |
| rules-1-b | superseded pre-final-phase | task form: relation-word surface form-dead for unaided hosts (pilot A5 0/24) |
| rules-1-c | INSTRUMENT-INVALID (`engagement_valid = FALSE`) | verifier engagement: URN/word type mismatch at the verifier's address check ⇒ unconditional abstention (every A3 row `attempts = 1`; A3 ≡ c1 on all 2,574 item×seed cells), sitting atop a design-layer vacuity — at a 2-option surface a non-leaking verifier is necessarily vacuous and an informative one necessarily decisive |

The rules-1-c interpretation's deeper result is endorsed here without
re-derivation: at this operating point (135M host, depth-2 items, 3-name
lexicons forcing a 2-option surface) the inference-time verify-retry claim
**has no valid carrier in this design family** — the leak–vacuity dilemma,
the exhaustion degeneracy (k=4 retries against 2 options), and the
abstaining shuffled control close it independently. [DERIVED there;
ASSESSMENT here that the argument is sound]

**g2-import typing repair — two instrument-invalid records and two pilot
stops on the successor.** [MECHANICAL/MEASURED]

| stage | pair statistic | outcome |
|---|---|---|
| g2-import v1 (full run) | κ_A3 = 0.286 < 0.40 | INSTRUMENT-INVALID; disagreement localised to hedged-modality composites (24/27 disagreements on "Typically" clauses) |
| v2 exploratory pilot (quarantined) | κ = −0.021 at raw 0.70; AC1 0.578 < its independence ceiling 0.587 | instrument evidence only; triggered the §11 κ-paradox gate redesign (gate → Gwet AC1 ≥ 0.65) |
| v2 Stage-P pilot #1 (`pilot-20260712-ac1`, authoritative pA = GPT-5.6) | **AC1 0.6909 ≥ 0.65** (table 29/2/6/3; κ 0.182 co-reported) | mechanical FAIL on the **calibration channel only** (11/12): a claude.ai MCP connector leak into 1/62 pB headless sessions rejected a semantically correct answer; 5/5 diagnostic repeats clean |
| v2 Stage-P pilot #2 (`real-20260712-auth`, post-MCP-hardening re-run) | **AC1 0.6222 < 0.65** (table 28/1/7/4; κ = 0.0000 exactly) | pilot gate FAIL on the AC1 channel; **full run never launched** (pilot-stop semantics held); result assembled PROVISIONAL-ON-LLM-PROXY, pilot-only |

In both v2 pilots every **prevalence-free known-answer channel was green**:
hedge-calibration 12/12 semantically correct (the pilot-#1 miss was
infrastructure, not judgment), hedge-flip false-satisfaction 0/8 per judge,
decisive 40/40 per judge. Only the pair-stability statistic failed, and only
in pilot #2. [MEASURED]

### 0.2 What DID instrument cleanly

- **f2b-transfer**: primary +0.2507 on blind externally-adjudicated gold,
  endorsement 0.961, all gates TRUE, verdict PASS, audit CONFIRMED.
  [MECHANICAL]
- **DECONF-B**: Δ_align +0.2697 (Holm-passed), bridge/engagement/headroom/
  instrument gates TRUE, verdict PASS, audit CONFIRMED — with the licensed
  sentence capped at "verify-retry against an item-aligned deterministic
  answer key lifts a 135M host …; the kernel is one way to AUTHOR such a
  key; no kernel-specific runtime contribution is measured". [MECHANICAL]
- **RULES-1 CPU certificate**: engine 858/858 vs third-party gold, stated/
  entailed C_dec 1.0/0.0 — machinery non-inertness, standing and pre-dating
  the failed campaigns. [MEASURED]
- Inside the failed rules-1-c campaign, the **host-validity instrument
  itself worked**: the ENTITY form is the first rules-lane surface the
  pinned hosts demonstrably operate (A5 0.944, A7 1.000, A1 0.703 at chance
  0.5), and the padding non-neutrality (+0.171) is a reusable measured
  instrument fact. [MECHANICAL/MEASURED]

The asymmetry this ledger displays is the subject of §1: the instruments
that succeeded all have **deterministic or externally-adjudicated
measurement channels** (string-equality acceptance, blind human-protocol
adjudication, exact-match against third-party gold). The instruments that
failed all require a **judgment interface the programme's smallest
components must stably support at the operating point** — a 135M host
cooperating with an interactive verifier, or a two-proxy judge pair agreeing
on hedged compound semantics at prevalence ≈ 0.84. [ASSESSMENT]

---

## 1. What the repeated correctness-instrument failure means

Three candidate readings, weighed separately. They are not exclusive; the
verdict at the end is a weighting, not a selection.

### 1.1 Reading (a): SCALE ARTIFACT — tiny kernel, tiny model, tiny judge panel make the instruments fragile

**Evidence for.** The failure mechanisms on both sub-tracks bottom out in
smallness, traceably:

1. The rules lane's terminal box is *forced by the item bank and the host*:
   elicitability at 135M pushed the surface to 2 options (the only form the
   host operates), and the 3-name lexicons — themselves bound by the closed
   R-CHAIN len-2 rule inventory, i.e. by the tiny certified kernel slice —
   yield exactly 2 candidate surfaces. The leak–vacuity dilemma is a theorem
   *at n=2*; it dissolves at n ≥ 3, which requires deeper chains, which
   requires a larger rule inventory and richer items. A 1.7B host already
   clears the harder surfaces the 135M cannot (A5 0.833 on the 23-way fixed
   frame vs 135M form-dead). [MEASURED lineage; DERIVED structure]
2. The g2 pilot's gating statistic is intrinsically weak at its operating
   point *because the panel is a pair and the sample is 40*: at π ≈ 0.84 the
   pairwise signal lives in rare no-items (both_no = 1 in pilot #2), any
   pair coefficient discriminates weakly (the design's own §11.3 honesty
   pin), and the two authoritative pilots — identical marginals 35/40 and
   32/40 — differ by exactly **two agreeing items** yet straddle the gate
   (0.6909 vs 0.6222). A pair statistic whose run-to-run noise at n=40 spans
   the gate width is a small-sample instrument, definitionally. [MEASURED +
   DERIVED]
3. The pattern named in the rules-1-c interpretation — "instruments fail at
   the first untested interface, and 'tested' must mean exercised at the
   operating point" — is itself a small-regime phenomenon: at these scales
   the operating point sits near multiple degeneracy boundaries (form-death,
   verifier vacuity, prevalence compression) simultaneously, so design-time
   argument keeps missing what a $1 pilot would catch. [ASSESSMENT]

**Evidence against / limits.** The reading must not be stretched into "at
larger scale these instruments would have worked", which is unmeasured in
every direction: host engageability at n = 3–4 options is explicitly
unmeasured (rules-1-c interpretation §3.2); nothing shows a larger judge
panel stabilises hedged-modality adjudication (the residual g2 disagreement
is one-sided pB hedge-strictness in both pilots — 7v4 and 6v3 — a
*systematic* offset, and systematic offsets do not average out with panel
size the way noise does). And the rules-1-c proximate cause (a one-line
type mismatch) is scale-independent process failure, caught only because
the gates were well built. [MEASURED; ASSESSMENT]

To the extent reading (a) holds, it reinforces the large-kernel/deeper-item
direction ([REPORTED] as a standing directive; the design record is
`docs/next/design/large-kernel-scale-track.md`) — but with the caveat that
scale-S0's own measured blockers put the thesis-relevant large-kernel
payoff a rung further away, so "scale fixes the instruments" is a
medium-term bet, not an available move this quarter. [MEASURED S0 blockers
via the steering read; ASSESSMENT]

### 1.2 Reading (b): DESIGN-SPACE signal — these specific instruments are hard, but the thesis is testable another way

**Evidence for.** Both sub-tracks have *identified, cheaper, already-named
alternative carriers* — the failures localise to the instrument family, not
to the measurable quantity:

1. Rules: the train-time pivot (rules-2 REWORK-3) removes the exact failed
   interface — the host need not cooperate with a verifier at inference —
   and is commissioned as a $0 build inheriting the one instrument success
   of the lane (the ENTITY form and its host-validity floors, plus the
   padding lesson). [MEASURED board state]
2. g2: the pre-registered envelope has *always* named the two-human
   adjudicated panel as the sole adoption authority; the proxy pair was
   only ever a provisional stand-in. A proxy-pair stability failure does
   not block the authoritative path — it arguably *strengthens the case for
   taking it directly*, since human-hours are the quota-cheap resource this
   week (steering read §3, endorsed). [MEASURED envelope text; ASSESSMENT]
3. The five instrument failures failed at five *different* channels
   (elicitation, task form, verifier engagement, judge-κ-on-hedges,
   judge-AC1-at-boundary). No two failures share a mechanism. That is the
   signature of a hard instrument *neighbourhood*, not of an untestable
   quantity — an untestable quantity tends to fail the same way repeatedly.
   [ASSESSMENT]

**Evidence against / limits.** The alternative carriers are not free of the
same disease: rules-2 carries two open design problems (the 2-option
derangement re-operationalisation and the non-bridge-name shortcut audit,
critical-path §2.3/§2.5), both of which are exactly the kind of
first-untested-interface where the last three instruments died; and the
human panel resolves judge *stability* by fiat but not the underlying
question of whether hedged soft-typing statements are crisply decidable at
all (§1.3). [MEASURED design-opens; ASSESSMENT]

### 1.3 Reading (c): the correctness thesis is genuinely hard to demonstrate at this scale

**Evidence for.** Two observations give this reading real weight:

1. **The deflationary channel keeps instrumenting; the affirmative channel
   keeps not.** Every experiment asking "does aligned content help?" landed
   cleanly and answered yes (+0.2507, +0.2697, audit-confirmed twice).
   Every experiment asking the sharper affirmative questions — does the
   *kernel-specific structure* help at runtime, does *engine-verify-retry*
   lift a host, is the *imported typing* sound — either failed its
   instrument or answered "content, not structure" (DECONF-B's GS-A–kernel
   identity 1.0; g2-import's breadth control within noise of A3; CASC-0′
   gloss≡plain; DECONF-A1 inertness — [MEASURED] via the steering read's
   verified anchors). Five-for-five on one side and zero-for-five on the
   other is unlikely to be pure instrument bad luck; it is consistent with
   the affirmative effects being *small where the deflationary effects are
   large*, which makes their instruments intrinsically fragile — small
   effects at small scale sit inside the degeneracy margins. [ASSESSMENT]
2. **The g2 pilot's judges are individually competent and jointly at
   chance.** All known-answer channels green, yet κ = 0.0000 on real
   items in pilot #2: conditional on marginals, the pair shares zero
   signal (measured AC1 exactly equals its own independence-ceiling AC1 —
   `pilot_ac1_a3 = pilot_ac1_indep = 0.6222` to machine precision, which
   the pinned `agree_stats` arithmetic shows is the κ=0 point). The most
   natural reading is that the residual A3 items are *genuinely borderline
   under ordinary-meaning adjudication at their stated hedge force* — the
   content, not (only) the judges, resists crisp adjudication. If so, a
   third judge or a bigger pilot cannot manufacture decidability that the
   statements do not possess. [MEASURED + DERIVED; ASSESSMENT]

**Evidence against / limits.** The hard-thesis reading systematically
over-reads instrument failures as evidence about the world. An instrument
that never engaged (rules-1-c) is evidence about *nothing* thesis-shaped —
its own verdict semantics say so, and the counterfactual false-PASS analysis
shows the same design could as easily have manufactured a spurious
affirmative. Likewise pilot #1's AC1 0.6909 *passed* the substantive gate;
the "judges share zero signal" datum is one pilot out of two, at n=40, on a
statistic with ±2-item noise. And the one-sided pB asymmetry points at a
*fixable* judge-specific strictness bias at least as much as at item
undecidability. The correct epistemic state for every affirmative quantity
is **UNMEASURED**, not "resistant". [ASSESSMENT]

### 1.4 Verdict on the three readings

**[SUBJECTIVE]** My weighting: **(a) 45% / (b) 40% / (c) 15%**, read as
"where does the explanatory mass sit", not as exclusive probabilities.

The dominant compound is (a)+(b): the failures are *scale-artifact-shaped
at the instrument layer* — the 2-option box is forced by tiny lexicons and
a tiny host; the AC1 boundary-sitting is forced by a two-judge panel at
n=40 and prevalence 0.84 — and both sub-tracks have named, cheaper carriers
that route around the failed interface rather than through it. I give (c)
a real but minority weight because the deflationary/affirmative asymmetry
(five clean deflationary instruments, zero clean affirmative ones) is the
kind of pattern that, if it persists through rules-2 and a human-gold g2,
should be *promoted* to the primary reading — and because the κ=0 datum on
individually-competent judges is the single most (c)-flavoured measurement
in the ledger. What keeps (c) at 15% today is that neither sub-track has
yet run a *valid* affirmative instrument even once: "hard to demonstrate"
cannot be distinguished from "never yet validly attempted" on the current
record. That distinction is precisely what the two minimal paths in §2
would purchase. [SUBJECTIVE]

---

## 2. The minimal path to a valid correctness instrument, per sub-track

### 2.1 g2: is the 0.03 AC1 gap closeable?

The gap must first be stated correctly, because "0.6222 vs 0.65" understates
how strange the measurement is:

- **Arithmetically, the gap is one item.** At pilot #2's marginals
  (pe_γ = 0.2722), AC1 ≥ 0.65 ⇔ p_o ≥ 0.7453 ⇔ ≥ 30/40 agreements; pilot #2
  had 29. One converted disagreement passes the gate. [DERIVED]
- **Statistically, the instrument sits ON the boundary.** The two
  authoritative pilots — same 40 pinned items, same judges, identical
  marginals (35/40, 32/40), fresh stateless calls — measured 31/40 then
  29/40 agreements: AC1 0.6909 (pass) then 0.6222 (fail). The pair
  statistic's run-to-run movement (2 items) equals the gate margin.
  Pooling naively, the operating point is ≈ 30/40 ⇔ AC1 ≈ 0.657 — within a
  hair of the threshold from either side. [MEASURED + DERIVED]
- **In signal terms, however, pilot #2 measured zero.** κ = 0.0000 exactly:
  the pair agreed at precisely its independence rate, and the measured AC1
  *equals* its independence ceiling. Pilot #1's κ was 0.182 — small but
  nonzero. So the honest description is: the pair's conditional signal
  oscillates between ~zero and ~small, and the AC1 gate — deliberately set
  just above the independence ceiling — is doing exactly its designed job
  of refusing to certify a pair that cannot be distinguished from
  independent judges. [MEASURED; DERIVED; ASSESSMENT]

Against that, the three named closure options:

1. **A larger pilot (n=80–84)** buys precision, not signal. If the true
   operating point is ≈30/40-equivalent, a larger n concentrates the
   estimate *at* the boundary and the pass probability approaches a coin
   flip; if the true point is the κ=0 independence rate, larger n makes a
   pass *less* likely (the estimate converges to the ceiling, below 0.65).
   Larger pilots only help if the truth is comfortably above the gate,
   which two pilots' evidence does not support. **Not the move.**
   [DERIVED; SUBJECTIVE]
2. **A third judge** is a protocol change, not a repair: directive #11 pins
   the pA/pB pair, so a panel design needs a new record, a new gated
   statistic (majority-vote stability has its own prevalence pathologies at
   π ≈ 0.84), and a third vendor family to avoid deepening the disclosed
   overlap. It also does not address the *located* failure channel — the
   one-sided pB hedge-strictness — unless the third judge happens to
   adjudicate the rare no-items with signal the current pair lacks.
   **Possible, expensive in design-cycles, weakly targeted.** [ASSESSMENT]
3. **A targeted v2.2 rubric clarification for multi-hedge composites** —
   the next move the design record itself names (PROPOSED-ASM-1690) — is
   the only option aimed at the measured channel: both pilots' residual
   disagreement is one-sided (pA-yes/pB-no 7v4 and 6v3), consistent with
   residual pB strictness on real composites, the same behaviour pB showed
   on the original (unsound) cal:hedge-1 anchor. A rubric line that
   operationalises "usual case" for stacked hedges could plausibly convert
   the 1–2 items the gate needs. The risk is the measured v1→v2 pattern:
   the last rubric iteration converted 6 old discordances and *minted 8 new
   ones* while shifting prevalence — rubric edits move the operating point
   as much as they stabilise the pair. [MEASURED; ASSESSMENT]

**Closeability call [SUBJECTIVE]:** the gap is *technically closeable* —
one item, on a boundary-sitting statistic, with a located one-sided
channel and one of two pilots already past the gate — so "fundamental
judge disagreement" is not established. But it is closeable mostly *by
noise* unless v2.2 genuinely converts the pB-strict items, and the κ
evidence caps how much a pass would mean: a pair that passes 0.65 from a
κ≈0–0.18 regime certifies stability barely above independence. My call:
fund **exactly one** v2.2 rubric iteration + fresh Stage-P pilot (~$1.4),
with a pre-commitment that a second AC1 failure retires the proxy-pair
instrument for this record family, and route the decisive spend to the
**two-human adjudicated panel on the 84 slots** — which the frozen envelope
already names as the sole adoption authority, which the quarantined
bracket-robustness analysis shows would settle the primary under every
label construction (A3 ≥ 34/84 holds even on the maximally conservative
pair-concordant bracket, 42/84), and which converts the judge-stability
problem from "solve it" to "moot". The adoption-arm disagreement is, on my
reading, *partially* substantive — hedged soft-typing statements at
π ≈ 0.84 are genuinely borderline for ordinary-meaning adjudication — and
that is itself a finding the human panel would either confirm (humans also
split ⇒ the soft-typing rendering needs redesign, not the judges) or
dissolve. Either outcome is more valuable than a third proxy iteration.
[SUBJECTIVE]

### 2.2 rules: rules-1-d vs the rules-2 pivot

**rules-1-d (a non-vacuous inference-time verifier) is not a repair; it is
a design-research project with an engine-layer dependency.** The minimal
necessary conditions are already catalogued (rules-1-c interpretation §6,
endorsed): an exercised-not-argued verifier (unit-tested rejection on real
item bytes + a blocking nonzero-rejection pilot); n ≥ 3 with *competitive
in-story* distractors — which requires 4+-name lexicons, hence extending
the closed rule inventory past R-CHAIN len-2, hence a **new engine
certificate** (KILL-a re-execution, coverage re-derivation); retry budget
k ≤ n−2 or attempt-indexed scoring; an uninformative-rejection
feedback-content control; surface-matched attempt-0 prompts (the +0.171
padding effect designed out); and an information-theoretic leak criterion
replacing the lexical guard. Two of these sit on axes that are entirely
unmeasured (host engageability at n = 3–4; competitive-distractor
construction), i.e. exactly the axes on which the last three instruments
died. Cost shape: re-certification + two unmeasured-risk pilots + a fourth
freeze/campaign cycle, to measure an interface that has now failed three
different ways. [MEASURED requirements; ASSESSMENT on cost shape]

**rules-2 REWORK-3 (train-time internalisation) sidesteps the failed
interface by construction**: the host internalises engine-materialised
derivations at training time and needs no inference-time cooperation with
a verifier — verify-retry, the leak–vacuity dilemma, and the exhaustion
degeneracy simply do not appear in its measurement path. It is a $0 build,
commissioned, re-based onto the one instrument success of the lane (the
ENTITY form, A5/A7 host-validity floors), currently fail-closed behind
ERR_PIN/ERR_FRAME_DRIFT (correctly) and GPU-held on the #24 slot decision.
Its two open design problems — the 2-option derangement
re-operationalisation for the shuffled control, and the non-bridge-name
shortcut audit — are real and are precisely where a *fifth* instrument
failure would occur if the lane's process lesson is not applied. [MEASURED
board state; ASSESSMENT]

**Minimal path, rules sub-track [SUBJECTIVE]:** rules-2 REWORK-3, with a
**mandatory blocking instrument pilot at the operating point** added to its
freeze checklist before any freeze: on ~20 pilot items, demonstrate (i)
that the eval surface separates a trained host from the B0 baseline, (ii)
that the shortcut audit actually fires on a planted shortcut exploiter, and
(iii) that the shuffled-derivation control is non-degenerate (its arm
neither collapses to abstention nor to the treatment). rules-1-d should
survive only as a paper design gated on a demonstrated nonzero rejection
rate — no freeze, no build, no GPU. This matches the steering read's
on-record opinion; I reach it independently from the instrument ledger:
the programme's instruments succeed when the measurement channel is
deterministic or externally adjudicated, and rules-2's channel (train-time
weight change → forced-choice accuracy against the certified engine's
gold) is the most deterministic channel the lane has ever proposed.
Whether the *slot* moves is the maintainer's #24 decision; this paragraph
is input to it, not a substitute for it. [SUBJECTIVE]

---

## 3. What the programme can currently claim about CORRECTNESS

Stated with the licence stack intact; every sentence below inherits the
relevant record's rider and envelope verbatim, and the coverage disclosure
(kernel-expressibility 0.3542 at rung molecules-v0, one incomplete
kernel-v0 instance) applies wherever content claims are made.

**Licensed today [MECHANICAL, audit-confirmed]:**

1. *Engine-level correctness at certificate scope*: the deterministic
   engine reproduces third-party gold 858/858 with stated/entailed
   C_dec 1.0/0.0 (RULES-1 CPU certificate) — the machinery is non-inert
   and exactly right where certified.
2. *Aligned-content lift, twice, on external gold*: verify-retry against
   item-aligned deterministic acceptance over authored content lifts a
   135M host by +0.2507 (f2b-transfer, blind-adjudicated gold, PASS) and
   the lift is alignment-specific over a generic lexical loop by +0.2697
   (DECONF-B, PASS) — with DECONF-B's own cap that the kernel is *one way
   to author* such an acceptance key and **no kernel-specific runtime
   contribution is measured**.

**Not licensed — and, more precisely, never yet validly measured:**

3. *Kernel-specific structural value at runtime.* Every deconfound that
   asked has answered "content, not structure" (GS-A–kernel identity 1.0;
   gloss≡plain; breadth control within noise); the designated honest
   decider (the knull rules-source ablation) is run-pending. Unmeasured,
   with the measured neighbours leaning deflationary. [MEASURED verdicts;
   ASSESSMENT on the lean]
4. *Engine-verify-retry host lift.* Three instruments consumed, zero valid
   readings, and a derivation that the claim has no valid carrier in the
   current design family at this operating point. The claim is not killed
   — KILL-b's firing was unlicensed under INSTRUMENT-INVALID — it is
   **uninstrumented**. [MECHANICAL verdict semantics]
5. *Typing/import soundness (the g2 line).* A GO-shaped, bracket-robust
   signal (A3 ≥ 34/84 under every label construction including
   pair-concordant) exists **only under invalid instruments**; it licenses
   nothing. The v2 full run has never launched; the human panel has never
   run. Uninstrumented. [MEASURED]

The one-sentence honest position: **the programme can currently claim that
engine-verified, item-aligned authored content measurably helps small
hosts (twice, audited, externally adjudicated), and that its engine is
exactly correct at certificate scope; it cannot yet claim — in either
direction — anything about kernel-specific structure, inference-time
engine-host cooperation, or imported-typing soundness, because no valid
instrument has ever measured them.** The gap between those two halves is
the entire remaining correctness question, and it is an instrumentation
gap before it is an evidence gap. [ASSESSMENT]

---

## 4. Where the next correctness-directed effort should go (SUBJECTIVE, quota-aware)

**[SUBJECTIVE throughout this section; ordering is conditional advice into
the maintainer's open #24 decision and the coordinator's budget, and
pre-empts neither.]**

Given tight Fable/codex quota, ranked by information-per-unit-quota:

1. **rules-2 REWORK-3 instrument pilot** (near-$0, CPU/cheap-GPU pilot
   scale). The only affirmative host-integration lane on the board; the
   blocking exercised-at-operating-point pilot (§2.2) is the cheapest
   insurance the programme has repeatedly declined to buy and then paid
   for — four campaigns of evidence say buy it first. GPU launch stays
   held on #24, but the *pilot and design-open resolution* need not wait.
2. **One g2 v2.2 rubric iteration + fresh pilot** (~$1.4, bounded), under
   the pre-commitment of §2.1: pass ⇒ the $5–6 full run; second AC1 fail ⇒
   retire the proxy pair for this family and let the human panel be the
   instrument. Cheap either way, and either branch terminates the
   iteration loop.
3. **The human annotation lane** (human-hours, not model quota — the
   resource that quota-tightening makes relatively cheaper). The g2-line
   two-human panel is the standing adoption authority and the only
   instrument in the correctness track that cannot fail on proxy-pair
   pathology. If only one item on this list can be funded to completion,
   my opinion is that it should be this one, because it is the only one
   whose result is authoritative rather than provisional.
4. **Do not fund rules-1-d** beyond paper design (no freeze, no build), and
   do not let the scale track's crosswalk engineering compete with any of
   the above this cycle — its instrument-fragility payoff (reading (a)'s
   remedy) is real but a rung away.

The meta-recommendation, which I weight more heavily than any single
ranking entry: **adopt the mandatory blocking instrument pilot as prereg
protocol now** — every gate channel exercised at the operating point
before freeze. It is the process fix that four (now five, counting the g2
pilot-stop as the machinery *working*) instrument events all point at, it
costs hours, and it converts reading (a)'s fragility from a recurring tax
into a designed-for property. The g2-import-v2 pilot-stop discipline is
the existence proof: it caught a boundary-sitting instrument for $1.4
instead of $6, exactly as designed. [SUBJECTIVE]

---

## 5. Limitations of this reading

The two-pilot g2 analysis treats the pilots as exchangeable measurements of
one operating point; if the MCP hardening between them changed pB's
effective behaviour, the pooling in §2.1 is optimistic. The AC1/κ/ceiling
arithmetic was re-derived from the pinned `agree_stats`/`kappa`
implementations and the committed contingency tables, not re-executed
through the analysis script. Issue #24's text was not resolvable via bd
this tick; its scope is taken from the critical-path doc. The reading (c)
weighting in §1.4 is a subjective prior update, not a computation. Nothing
here alters any frozen object, registers any assumption, issues any
verdict, or draws any feasibility conclusion — the cross-experiment
synthesis (kernel-of-truth-d8p8/m90m) owns that, and the host-integration
slot decision remains the maintainer's (#24).
