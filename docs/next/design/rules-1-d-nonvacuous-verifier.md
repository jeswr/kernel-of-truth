# RULES-1-D — the non-vacuous verifier (paper design; nothing frozen)

**Role: Fable DESIGN agent (designer-4), 2026-07-12. This document is the
maintainer-commissioned branch (C) of issue #24: the honest, non-vacuous
version of a fourth inference-time verify-retry instrument. It is a PAPER
DESIGN under the standing "do not fund rules-1-d beyond paper design" advice
(correctness-track assessment §4 item 4), which it does not overturn: nothing
here is frozen, built, minted, or launched; no feasibility conclusion is
stated; the slot decision remains the maintainer's (#24). Prereg
operationalisation (exact thresholds, power arithmetic, verdict rules) is the
experiment-designer role's if and only if the maintainer funds the tranche in
§6.** Companions:
`docs/next/analysis/rules1c-instrument-invalid-interpretation.md` (the
failure this design answers, esp. §1.2 and §6),
`docs/next/analysis/correctness-track-instrument-assessment.md` (§2.2),
`docs/next/protocol/blocking-pilot-before-freeze.md` (the pilot gate
instantiated in §5), `docs/next/design/post-rules1c-critical-path.md`.

Epistemic tags: **[MEASURED]** read from committed/on-disk bytes this tick
(commands stated); **[DERIVED]** follows from measured bytes by stated
arithmetic/code-reading; **[PREDICTED]** extrapolation, never evidence;
**[STIPULATED]** a design choice this document makes; **[ASSESSMENT]** this
agent's judgment; **[DESIGN-OPEN]** deliberately left to the owning role.

Assumption rows PROPOSED-ASM-1860..1867 are emitted alongside
(`docs/next/design/asm-rules1d-1860-1867.json`) for central registration by
the coordinator; `registry/assumptions.jsonl` is untouched by this build.
Range 1860–1869 verified free at emission time (no ASM-185x/186x reference
anywhere in the tree). [MEASURED]

---

## 0. The tension this design must break

rules-1-c's post-mortem closed the 2-option design point with three
independent boxes [DERIVED there; endorsed]:

1. **Leak–vacuity**: at n=2 any informative licensed rejection conveys the
   whole answer bit (the survivor is gold by elimination); a verifier
   constrained below one bit can never reject the unique distractor.
   Non-vacuous and non-leaking are jointly unsatisfiable at n=2.
2. **Exhaustion**: k=4 retries against 2 options makes a *working* verifier
   a rejection sampler converging to ≈1.0 regardless of host comprehension
   — oracle filtering read as host lift.
3. **Control asymmetry**: the shuffled-rules control abstains rather than
   rejects, so no arm separates "the feedback taught the host" from "the
   oracle filtered the host's guesses".

The tension: elicitability at the 135M host pushes the option count DOWN
(the 2-option ENTITY form is the only surface the host demonstrably
operates: A1 0.703, A5 0.944, A7 1.000 [MECHANICAL, rules-1-c]); verifier
informativeness pushes it UP (a rejection must eliminate strictly less than
everything). And the k=2 item bank binds from below: 3-name lexicons minus
the anti-echo base exclusion yield exactly 2 candidate surfaces.

**The design move: n=3 in-story options with a structurally guaranteed
gender-compatible wrong elder, retry budget k=1 (= n−2), an
uninformative-rejection control at matched budget, and third-party gold
preserved — reachable, it turns out, WITHOUT touching the engine's rule
language, via a sibling-bridged depth-3 item family that CLUTRR already
contains.** [STIPULATED; scoping facts §3]

---

## 1. The instrument

### 1.1 Item family and answer surface

**Items**: CLUTRR k=3 chains of shape (r1, r2, r3) with
r_i ∈ {father, mother, brother, sister}, exactly one sibling edge, and
target ∈ {grandfather, grandmother} — e.g. `('sister','father','father') →
grandfather`: A's sister B; B's father C (= A's father, shared parent);
C's father D (= A's grandfather). Four in-story names per item
{A base, B, C, D gold}; third-party CLUTRR `proof_state` gold predating
the kernel, same provenance discipline as the k=2 858-item bank
(PROPOSED-ASM-1125 analog). [MEASURED item shape; §3 counts]

**Surface**: the measured-working ENTITY form, unchanged in kind — question
`Who is the <target> of <A>?`, forced choice with the f2bt scorer, options =
the three non-base in-story names {B, C, D} (anti-echo base exclusion
retained). Chance = 1/3, DISCLOSED. Option order position-shuffled per
seed. [STIPULATED]

**Primary stratum (gender-competitive)**: only items where ≥1 distractor
matches the gold's gender are primary; items whose gold is the *only*
gender-consistent option are solvable by a surface gender heuristic and are
quarantined as a disclosed descriptive stratum. Gender of B is fixed by r1,
of C by r2, so the stratum is decidable at build time from `edge_types`
alone. [STIPULATED; DERIVED stratum rule]

### 1.2 The verifier and why its rejection is real derivational work

Verifier grounds, in checking order, all computed against Cl(S) by the
pinned twin engine (typed payload interface — §5 PC-4 kills the rules-1-c
URN/word class of defect by unit test on real item bytes):

- **accept** iff the proposed name is the engine's certified derivation for
  the query (proof-carrying, as in rules-1-c A7's channel);
- **ground (i) — range/gender**: reject a proposal whose derived class
  (man/woman via R-RNG on stated edges) contradicts the target relation's
  range axiom;
- **ground (ii) — no licensing derivation**: reject a proposal X with the
  licensed reason "the stated facts derive <what X provably is to A>; no
  derivation licenses X as the <target> of A".

**The planted plausible distractor**: in every primary-stratum item at
least one non-gold elder (typically C, the shared parent, or B when r1 is a
same-gender sibling/parent edge) is (a) in-story, (b) gender-compatible
with the target, (c) at the end of a plausible-but-wrong partial chain —
it passes ground (i) and every surface feature the host or a shortcut bot
can compute, and is rejected ONLY by ground (ii), i.e. only by actually
computing the closure and finding grandparent(A) = D ≠ X. "Planted" means
guaranteed by stratum construction, not injected into the story text.
A verifier that must reject THIS proposal is doing derivational work no
lexical/surface check reproduces — that is the non-vacuity claim, and §5
makes it an exercised gate (PC-4), not an argued one. [STIPULATED; DERIVED
existence from the stratum rule]

### 1.3 Anti-exhaustion, leak criterion, scoring

- **Retry budget k = 1 = n−2** [rules-1-c interpretation §6 item 3]: one
  rejection leaves 2 live options; acceptance cannot be reached by
  exhaustion. A feedback-blind resampler's final-accuracy ceiling is
  p0 + (1−p0)·½ < 1 (vs ≈1.0 at the rules-1-c operating point). [DERIVED]
- **Information-theoretic leak criterion** [ibid. item 6]: a rejection may
  remove at most log2(3/2) ≈ 0.585 bits of option-set entropy (name the
  rejected proposal, never the gold, never a second option); asserted
  fail-closed per feedback line by an entropy audit REPLACING the lexical
  gold-token guard (which stays as a redundant backstop). At n=3 an
  informative rejection is therefore compatible with genuine residual
  uncertainty (1 bit over 2 options) — the leak–vacuity dilemma dissolves
  exactly here. [DERIVED]
- **Attempt-indexed scoring** [ibid.]: rows carry per-attempt answers;
  attempt-0 accuracy and final accuracy are both first-class, so filtering
  vs teaching is visible in the rows, not reconstructed.
- **Surface-matched attempt-0 prompts** [ibid. item 5]: A1 and A3/c7/c1
  attempt-0 prompts are byte-identical (pad both or neither — kill the
  measured +0.171 padding confound before it reaches the primary).

### 1.4 Arms and contrasts

| arm | content |
|---|---|
| A1 | 135M alone, surface-matched prompt (floor + headroom gate) |
| A3 | 135M + engine verify-retry, k=1, licensed informative rejections |
| **c7** | **135M + the SAME accept/reject oracle, feedback text replaced by the uninformative constant "Rejected; answer again." at matched budget and token cost** — NEW; the control rules-1-c lacked |
| c1 | shuffled-rules control (Sattolo-deranged TBox), retained for content destruction; its abstention behaviour on the extended module re-measured and disclosed either way (§3 D4) |
| A5 | 1.7B alone (efficiency comparator, sign-only) |
| A7 | render-only injected derivation (attribution-clean systems arm + host-validity gate component) |

**Primary P1 (the claim carrier): final-accuracy(A3) − final-accuracy(c7)**
— does the CONTENT of a licensed engine rejection teach the host anything
beyond the bare reject bit? Both arms share the accept/reject oracle and
the eliminated-option information; they differ only in the stated reason.
**Secondary S1: c7 − A1** (value of engine accept/reject filtering as a
systems quantity); **S2: A3 − A1** (the lane's historic contrast, now
attribution-capped by P1/S1). Wording rule fixed in advance: an
"engine feedback teaches the host" sentence is licensed only by P1;
if P1 ≈ 0 < S1 the licensed sentence is filtering-only. [STIPULATED;
exact margins/power are the experiment-designer's — SESOI guidance §6]

---

## 2. Why this verifier is non-vacuous, precisely

Re-closing the three rules-1-c boxes plus the fourth (counterfactual
false-PASS) direction:

1. **Leak–vacuity broken**: n=3; a maximally informative licensed rejection
   removes 0.585 of 1.585 bits — informative AND non-leaking are jointly
   satisfiable; the entropy audit enforces the bound mechanically. [DERIVED]
2. **Exhaustion broken**: k=1 ≤ n−2; the composite cannot converge to the
   verifier's knowledge; the scripted resampler ceiling p0+(1−p0)/2 is
   measured in the pilot as the filtering floor. [DERIVED]
3. **Filtered-vs-taught separable**: c7 is the matched-budget
   uninformative-rejection arm the post-mortem demanded; c1's abstention
   asymmetry is thereby demoted from load-bearing to content-destruction
   duty. [STIPULATED]
4. **Both degeneracy directions gated**: never-engages (engagement gate:
   attempts>1 on a nonzero fraction, PC-2) AND always-decides (oracle
   capture: the decisive flag fires if the A3 composite is statistically
   indistinguishable from the scripted oracle-filter bot, and structurally
   k=1 caps what deciding can deliver). rules-1-c gated only the first.
   [STIPULATED, answering interpretation §7]
5. **The retry has real work**: on primary-stratum items the attempt-0
   error mass lands on in-story, gender-compatible elders that only ground
   (ii) rejects — a rejection event requires the engine to have computed a
   closure fact, and the pilot requires observing a rejection rate inside
   [0.10, 0.90] at the operating point before any freeze (PC-2, §5).
   [STIPULATED; the rate itself is UNMEASURED until the pilot runs]

---

## 3. The dependency chain this forces, scoped

**Scoping facts measured this tick** (read directly from
`data/clutrr-cache/clutrr-emnlp-release.zip`, the sha-pinned EMNLP release;
one-shot Python over the inner CSVs):

- **CLUTRR contains ZERO parent-only k=3 chains** (321 distinct k=3
  edge-type combos in the CLEAN bundle; none ⊆ {father, mother} —
  great-grandparent is not in CLUTRR's 23-relation vocabulary, so pure
  3-up chains are never generated). **The naive depth-3
  "great-grandparent" route has NO third-party gold and is dead on
  arrival.** [MEASURED]
- The **sibling-bridged route** (§1.1) IS covered with third-party gold:
  16 combos, target ∈ {grandfather, grandmother}, edges ⊆ {father, mother,
  brother, sister}. Counts: bundle `data_089907f8` (CLEAN k=2,3): 245
  coverable / 184 gender-competitive; bundle `data_db9b8f04` (CLEAN
  k=2,3,4): 248 / 186. **≈493 coverable, ≈370 primary-stratum items before
  cross-bundle dedup.** [MEASURED]

### D1 — lexicon extension (≥4 gendered names per family)

The k=3 stories already carry 4 in-story names with CLUTRR gender
annotations (`provenance.genders`); the extension is to the ITEM builder,
not to any name invention: per-item closed lexicons of 4 URN-named
entities, stated gendered class facts (man/woman) for each via the story's
gender data, anti-collision checks, and the S9-style build assertions
re-run (engine resolution, unique licensed lookup, control refusal, no
gold token in feedback, story-contamination count). Owner: builder role
(`poc/nsk1/build_clutrr_corpus.py` variant → `nsk1-clutrr-k3`).
Cost: $0 compute, ~1 agent-day + review. [STIPULATED]

### D2 — rule-inventory extension (NOT a rule-language extension)

New minted content (explicator role, mint pipeline + endorsement, exactly
the axioms-kinship-v1 discipline):

- concepts: brother, sister, sibling (molecule-style records, URN-minted);
- axioms: `brother subPropertyOf sibling`, `sister subPropertyOf sibling`,
  `range(brother→man)`, `range(sister→woman)`,
  `propertyChain(sibling, father → father)`,
  `propertyChain(sibling, mother → mother)` — the shared-parent rule.

**Key scoping fact [DERIVED from the pinned engine bytes]**: all of this is
expressible in the EXISTING closed rule language. R-CHAIN is length-2 only,
but the fixpoint rebuilds its index over ALL derived rels each pass
(`twin_engine.py` `_run`, R-CHAIN comment: "matching f as the FIRST hop
only is complete at fixpoint"), so a k=3 derivation is two/three
applications of len-2 rules: stated sibling edge → subprop → shared-parent
chain → existing parent∘parent grandparent chain → existing coveredBy +
gender elimination. **No engine code change, no new rule kinds, no
ALGORITHM_VERSION bump (encoder untouched).** The full-sibling
shared-parent premise ("siblings share both parents" — true in CLUTRR's
generator by construction, not in the world) is a **policy-regime
assumption to be disclosed exactly like UNA (ASM-1120) and covering
(ASM-1121)**, carried on every proof node that uses it. [DERIVED;
STIPULATED disclosure]

Residual engine risks to verify (not argue): interaction of the new chains
with `functional(father/mother)` conflict detection (derived father(B,D)
must agree with any stated father(B,·) — on covered items it does by
construction; conflicts must surface, not crash), and derivation-budget
growth at 4-entity worlds. Both are certificate/CF matters (D3), and the
`chain length != 2` refusal stays untouched. [DESIGN-OPEN → D3]

### D3 — ENGINE RE-CERTIFICATION (mandatory, $0, CPU)

The standing certificate (engine 858/858 vs third-party gold, C_dec
stated/entailed 1.0/0.0, KILL-a not fired) is scoped to the 6-property
module and the k=2 bank; it does NOT carry to the extended inventory.
Before any rules-1-d freeze, `certificate.py` must be re-run in full on
the extended module:

- **E3′**: the coverable k=3 slice (≈493 items pre-dedup) — engine answer
  vs third-party CLUTRR gold, Wilson-LB ≥ 0.98 soundness bar, plus the
  k=2 858 re-run under the extended TBox (no regression);
- **KILL-a re-execution**: Cl(S)\S non-empty and non-trivial on the new
  worlds; C_dec(entailed) < 1.0 vs the GS-B stated-bytes projection,
  C_dec(stated) = 1.0;
- **E5′ refusal controls**: ~100 uncovered k=3 combos (305 of 321 combos
  are outside the extended inventory — a large honest refusal pool) must
  refuse with named ERR_*;
- **CF-1/2/3 on the NEW axioms**: sibling-chain removal → targets
  disappear; meaning-changing mutation (swap the shared-parent chain's
  gendered head) → exactly the predicted flips; no-op permutation →
  byte-identical; **DET** double-run sha.
- New `certificate-result.json` pins; the rules-1-d record's
  ERR_CERT_PRECONDITION check points at the NEW result bytes.

Cost: $0 (CPU, hours, niced on this box's 2 shared cores). Effort: ~1–2
agent-days including the coverage re-derivation. [STIPULATED]

### D4 — item bank + controls rebuild

Cross-bundle dedup (story-text hash) with the count disclosed; per-item
4-name lexicons; primary-stratum flag; c1 derangement re-derivation on the
extended (9-property) module — the rules-1-c disclosed property ("every
derangement makes the engine refuse everywhere") must be RE-MEASURED, not
assumed, and disclosed either way; c8-analog surface-shortcut audit: a
scripted story-position/gender-heuristic bot's accuracy ceiling on the
primary stratum, gated in the pilot (PC-4). Cost: $0 compute, ~1 agent-day.
[STIPULATED]

---

## 4. What rules-1-d inherits unchanged

ENTITY form and its measured floors as pilot constants (A5/A7 host-validity
duty); f2bt forced-choice scorer/resampler bytes; fail-closed pin
discipline (kot-corpus-hash/1 on all inputs, sha pins on engine,
certificate result, runner, analysis); run-vs-audit separation; the
INSTRUMENT-INVALID-before-KILL verdict-rule ordering from rules-1-c; the
gold-leak lexical guard (now a backstop under the entropy criterion).
[STIPULATED]

---

## 5. The MANDATORY blocking instrument pilot (built IN FRONT)

Per `docs/next/protocol/blocking-pilot-before-freeze.md` (PROPOSED-ASM-1830
rule; kot-pilot/1 artifact; freeze refuses ERR_P2_PILOT_MISSING without
it). The pilot is the FIRST spend of the tranche and blocks everything
downstream. REAL instrument, pinned harness, operating-point pins
byte-equal to the draft record, ~24 primary-stratum items × all arms ×
1 seed, cost cap $2, verdict = instrument-validity ONLY (never evidence).

Instantiation — every predicate mechanical, thresholds pre-declared in the
pilot runner before any result is read:

| check | rules-1-d operating-point predicate |
|---|---|
| **PC-5 elicitable gold** | scripted oracle arm ≥ 22/24 under the pinned parser; A7-analog (render-only) ≥ 0.85; A5-analog (1.7B alone, n=3, k=3 stories) ≥ 0.60 vs chance 1/3; parse-failure ≤ 0.05 every arm. **This is the make-or-break check: host engageability at n=3 options over longer k=3 stories is UNMEASURED — the k=2/2-option floors do not carry.** |
| **PC-1 no degenerate arm** | A1 within [0.20, 0.85]: above a form-death floor by exact binomial vs 1/3 parse-alive behaviour, below the saturation/headroom ceiling; refusal/abstention bounded every arm |
| **PC-2 non-vacuous engagement** | **A3 attempt-0 rejection rate ∈ [0.10, 0.90]** (the retry has real work AND the verifier is not rejecting everything); **attempts > 1 on a nonzero fraction of A3 AND c7 rows**; A3 NOT row-identical to c7 or c1 on the pilot slice |
| **PC-3 controls non-degenerate** | c7 engages with an attempts distribution matched to A3 (same oracle ⇒ same rejection events — asserted row-wise); c1 behaviour on the extended module re-measured and consistent with its D4 disclosure; every gating statistic clears its degeneracy floor by more than its observed pilot replicate noise (the g2 margin-vs-noise clause) |
| **PC-4 gate teeth** | on real item bytes, planted violations FIRE: (a) unit test — the verifier REJECTS a hand-simulated planted-distractor proposal via ground (ii) AND ACCEPTS the gold proposal (kills the rules-1-c URN/word type-mismatch class at its exact location); (b) a planted gold-naming feedback line fires the entropy/leak audit; (c) a planted always-accept verifier stub fires the engagement gate; (d) a planted always-reject stub fires the decisive/oracle-capture flag; (e) the scripted surface-shortcut bot scores under its pre-declared ceiling on the primary stratum, and a planted gender-heuristic exploiter scores OVER it (the audit can fire) |

Freeze order: D2 mint + D3 re-certification (both $0) → pilot ($2) → ONLY
on PILOT-PASS: prereg draft, GPT-5.6 review, coordinator freeze. A
PILOT-FAIL on PC-5/PC-1 is a NO-GO trigger (§6), not a redesign invitation.
[STIPULATED]

---

## 6. Costed plan and the honest risk read

### 6.1 Cost table [STIPULATED estimates; caps fail-closed]

| stage | compute $ | effort | gate |
|---|---|---|---|
| D1 builder + D4 bank | $0 | ~2 agent-days | build assertions S9′ |
| D2 mint + explicator endorsement | $0 | ~1 agent-day + explicator pass | endorsement |
| D3 engine re-certification | **$0 (CPU)** | ~1–2 agent-days | KILL-a′, CF′, DET′, Wilson-LB ≥ 0.98 |
| §5 blocking pilot | ≤ $2 | ~½ agent-day | PC-1..PC-5, kot-pilot/1 |
| campaign (6 arms × ~370 items × 3 seeds, k≤2 attempts, longer prompts) | ~$12–18, **cap $20** | runner + analyst roles | frozen record |
| knull-analog ablation (kernel-specificity cap, if P1/S1 land) | ~$4 | — | its own activation gate |
| **worst-case total** | **≤ $26** | **~1 wk serial agent effort + a fourth freeze cycle** | |

Power honesty: ~370 primary items × 3 seeds supports a SESOI of ~0.10 on
the paired P1 contrast at conventional power; **0.05 is out of reach at
this bank size** — the prereg must set SESOI 0.10 or formally pool both
CLEAN bundles post-dedup and re-derive. [DERIVED rough arithmetic;
experiment-designer to finalise]

### 6.2 Is it worth it vs the RULES-2 train-time route? [ASSESSMENT]

What a maximally clean rules-1-d PASS would add over what is already
verdict-grade: DECONF-B (audited) already shows verify-retry against an
item-aligned deterministic key lifts a 135M host (+0.2697) with the kernel
as one way to AUTHOR the key. rules-1-d's genuine increments are (a) the
key becomes the CERTIFIED ENGINE over ENTAILED-never-stated facts, and
(b) P1 vs c7 finally attributes any lift to feedback CONTENT vs oracle
filtering — the question none of the three dead instruments could ask.
Those are real but incremental; and P1 is plausibly small (both arms share
the reject bit; the content delta is one licensed reason sentence read by
a 135M host), so the modal outcome is a well-instrumented small-or-null P1
with a positive S1 — informative about the interface, unlikely to move
either thesis. rules-2 measures a different and more valuable quantity
(internalisation, no deployment-time cooperation) on the most deterministic
channel the lane has proposed, is commissioned, and is ~$14 all-in. **If
only one can be funded, fund rules-2 — unchanged from the standing
advice.** The strongest honest argument FOR the rules-1-d tranche: it is
the only design on the board that can produce a VALID measurement of the
inference-time interface at all, its first ~$2 buys the answer to the
question that killed three instruments (does the retry engage at a real
operating point?), and its $0 stages (D2/D3) also de-risk any future
deeper-item work the scale track needs anyway.

### 6.3 NO-GO triggers (pre-committed) [STIPULATED]

1. **Pilot PC-5/PC-1 fail** (host form-dead or floor-dead at n=3 / k=3
   story length): declare the inference-time slot CLOSED at this host
   scale — no rules-1-e, no option-count search; the design family is
   exhausted.
2. **Bank too small**: post-dedup primary stratum < 300 items ⇒
   underpowered even at SESOI 0.10 ⇒ NO-GO (paper design stands, campaign
   does not).
3. **c1/derangement pathology**: if the extended module's derangements no
   longer uniformly refuse AND no non-leaking c1 semantics can be
   re-operationalised, the structure control is unbuildable ⇒ NO-GO.
4. **rules-2 lands a valid affirmative first**: the slot's question is
   better answered there; rules-1-d reverts to paper permanently unless
   the maintainer explicitly re-opens it for the filtered-vs-taught
   attribution question alone.
5. **Certificate regression**: D3 fails Wilson-LB or fires KILL-a′ ⇒ stop;
   that is an engine finding, not an instrument to iterate past.

### 6.4 Recommendation shape [ASSESSMENT, non-binding]

Fund at most the **$0 + $2 tranche** (D1–D4 + pilot) now if branch (C) is
to proceed at all; hold the $20 campaign decision until BOTH the pilot
artifact and the rules-2 readout exist. This keeps the maintainer's option
value at ≤ $2 spent while converting every load-bearing unknown
(engageability, rejection rate, coverage, certificate) from argued to
measured. My honest read of the campaign itself: coin-flip or worse that
it changes any decision the programme faces; the tranche, by contrast, is
cheap and its information survives either #24 branch.

---

## 7. Claim caps (fixed now, before any freeze)

- A PASS-shaped P1 licenses at most: "licensed engine rejection CONTENT
  lifts a 135M host beyond an uninformative reject signal, on
  sibling-bridged depth-3 kinship, ENTITY form, n=3, k=1, at the measured
  operating point" — never kernel-specific value (knull-analog required),
  never NL robustness, never a scale slope, never generality past this
  vertical.
- S1 alone licenses only a SYSTEMS sentence (filtering value), explicitly
  redundant with A7's channel and DECONF-B's family.
- The pilot artifact licenses exactly one sentence (instrument dynamic
  range); pilot rows are never campaign evidence (ASM-1819/1835 fence).
- Under INSTRUMENT-INVALID, nothing thesis-shaped is licensed — the
  rules-1-c verdict-ordering discipline carries verbatim.
- The full-sibling shared-parent premise is disclosed on every proof that
  uses it; items are CLUTRR-generator-true, not world-true.

## 8. Limitations of this design read

The CLUTRR counts (§3) were computed by one-shot scripts over the pinned
release zip this tick and are pre-dedup; the builder must re-derive them
under pinned code. The engageability of the 135M at n=3 over k=3 stories,
the A3 rejection rate, and the c1 derangement behaviour on the extended
module are UNMEASURED until the pilot runs — every load-bearing rate in
§1–§2 is a design target, not a datum. Power arithmetic is rough. Nothing
here alters any frozen object, registers any assumption, or pre-empts
issue #24.
