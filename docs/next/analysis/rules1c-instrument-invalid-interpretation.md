# RULES-1-C INSTRUMENT-INVALID — interpretation (Fable)

**Role: Fable INTERPRETATION agent, 2026-07-12. This document interprets the
already-computed mechanical readout of the landed rules-1-c campaign. It
states NO feasibility conclusion on either thesis; the mechanical verdict
belongs to the pinned `analysis/rules_1c.py` + `tools/registry/verdict-gen.py`
chain, and the slot decision it feeds is the maintainer's (open issue #24,
not pre-empted here).** Companion to
`docs/next/analysis/rules1-void-degenerate-instrument.md` (rules-1 void),
`docs/next/analysis/rules1b-form-misattribution.md` (rules-1-b supersession),
and `docs/next/design/post-rules1c-critical-path.md` (board state).

Epistemic tags: **[MECHANICAL]** = the supplied pinned-analysis output,
reported verbatim; **[MEASURED]** = read directly from committed bytes
(code, rows, manifests) this tick; **[DERIVED]** = follows from measured
bytes by stated arithmetic or code-reading, could be wrong if the reading
is; **[COUNTERFACTUAL]** = a what-if under stated assumptions, never
evidence; **[ASSESSMENT]** = this agent's judgment, to be weighed as one
model's opinion; **[UNRESOLVED]** = a question this document deliberately
leaves to the owning role.

**Sources read at source:** `registry/experiments/rules-1-c.json` (frozen
`09b246dc…`); `analysis/rules_1c.py` (pinned `bf4e6476…`);
`poc/rules-1/rules1_runner.py` (on-disk sha verified `91d780f3…`, the
rules-1-c bytes named by the critical-path doc);
`poc/rules-1/twin_engine.py`; `poc/rules-1/inputs/rules1-manifest.json`;
`poc/rules-1/results-incoming/20260712-142704-rules1b-parallel/merged/run-records-rules1b.jsonl`
(13,470 rows, re-aggregated read-only to confirm the supplied descriptives);
`poc/rules-1/results-incoming/pilot-20260712-rules1c-a3c1/`; the three
companion documents above.

---

## 0. The mechanical readout (given; not re-derived here)

Verdict: **INSTRUMENT-INVALID**. [MECHANICAL]

| gate | value |
|---|---|
| engagement_valid | **FALSE** |
| repeat_byte_identical | FALSE |
| host_validity_valid | TRUE |
| certificate_precondition_valid | TRUE |
| separation_valid | TRUE |
| twin_agreement_valid | TRUE |

Descriptives (entailed cells, 858 items × 3 seeds = 2,574 rows/arm):
A1 (135M alone) 0.703; A3 (135M + verify-retry) 0.531; c1 (shuffled-rules
control) 0.531; A5 (1.7B alone) 0.944; A7 (135M, render-only injected
derivation) 1.000. `primary_lift_lb95 = −0.196`; `kill_b_fired = TRUE`.
[MECHANICAL]

Verdict-rule ordering matters: rule 0 (INSTRUMENT-INVALID) tests the gate
conjunction *before* the KILL-b FAIL rule, and `engagement_valid = FALSE`
alone defeats the conjunction. `kill_b_fired = TRUE` is therefore a computed
field that never reaches the verdict — exactly the discipline rules-1-b
introduced so that "a degenerate instrument can never read as a substantive
FAIL (or PASS)". [MEASURED — frozen `verdict_rules`, rules-1-c record]

Two housekeeping notes on the gate vector. (i) `headroom_valid` is part of
rule 0 but absent from the supplied vector; A1 = 0.703 ≤ 0.85 implies it is
clear, and it is not load-bearing given the engagement failure. [DERIVED]
(ii) `repeat_byte_identical = FALSE` sits *outside* rule 0's conjunction; in
the pinned script it defaults to FALSE whenever no repeat-run shas are
supplied to the analysis (`rules_1c.py:199-200`), so its FALSE reading here
is consistent with "no determinism repeat was performed", not necessarily
with an observed byte divergence. Which of the two it is belongs to the
runner role's provenance record. [DERIVED; UNRESOLVED]

---

## 1. Root cause, two layers deep

### 1.1 The as-run mechanical cause: the verifier abstained unconditionally

The supplied root cause — the A3 verify-retry channel never engaged (every
A3 row `attempts = 1`; A3 correctness-identical to c1 on all 2,574 item×seed
cells) — is confirmed in the merged rows and, notably, was already present
in the pre-launch full-arm pilot (`pilot-20260712-rules1c-a3c1`: all 24 A3
rows `attempts = 1`, acc 6/24). [MEASURED]

Code-reading the pinned bytes locates a proximate mechanism one layer
*shallower* than the design-level vacuity named in the planning documents:

- `twin_engine.py:288-322` — `Closure.query_relation` returns
  `(word, why)`: `payload.answer` is a relation **surface word** (e.g.
  `"grandfather"`). [MEASURED]
- `rules1_runner.py:342-343` — the verifier's address check reads
  `if urn2word.get(payload.answer) != rel_word: return None  # abstain`.
  But `urn2word` is **URN-keyed** (cf. its every other use, e.g.
  `verbalise_fact`, line 272). Looking a *word* up in a URN-keyed map
  returns `None`, which never equals `rel_word` — so the check abstains on
  **every** item, before the accept branch, before ground (i)
  (range/gender), and before ground (ii) (the catch-all "no derivation
  licenses '<X> is the <rel> of <A>'"). [MEASURED code; DERIVED consequence]

As run, `licensed_rejection` was therefore dead code past line 343: the
verifier could not accept, reject, or distinguish anything. This single
defect is sufficient to produce the entire observed signature: (a)
`attempts = 1` on 100% of A3 rows including the ~47% incorrect ones; (b)
A3 ≡ c1 exactly (c1's deranged payloads refuse and abstain at line 341 by
design; both arms thus reduce to the identical feedback-free single-shot
code path with identical seeds → identical picks, 2,574/2,574); (c) no
rejection text ever emitted. [DERIVED]

Note what this defect is *not*: it is not the engine (twin agreement TRUE,
certificate 858/858 standing, both [MECHANICAL]), and it is not the grounds
design per se — ground (ii) in the pinned bytes would have rejected any
unlicensed proposal without naming the gold token, had control flow reached
it. The failure is a one-line type mismatch at the verifier's front door,
of exactly the class a "can this ground ever reject one hand-simulated wrong
answer?" pre-freeze check would have caught. The engagement signature was on
disk in the pilot rows *before* the GPU launch; the mandatory pre-launch
check enforced only the host-validity floors, so the launch proceeded.
[MEASURED pilot bytes; ASSESSMENT on the check gap]

### 1.2 The design-layer cause beneath it: 2 options make the verifier
vacuous-or-decisive

Suppose the address check had been correct. The design would then have hit
the deeper problem the critical-path document names ("the entity-form
acceptance ground is vacuous at the 2-option surface"), and it is worth
stating that problem precisely, because it does not go away with a bugfix:

1. **The leak–vacuity dilemma.** At a closed 2-option surface the answer
   carries exactly one bit. Any *informative* licensed rejection — in
   particular ground (ii) rejecting the sole distractor — conveys that
   entire bit: the remaining option is gold by elimination. The gold-leak
   guard is lexical (the gold *token* may not appear in feedback,
   `rules1_runner.py:317-322`), but the operative leak channel at n=2 is
   combinatorial, invisible to a lexical guard. Conversely, a verifier
   constrained to convey strictly less than one bit can never reject the
   unique distractor — it is vacuous. Non-vacuous and non-leaking are
   jointly unsatisfiable at n=2. [DERIVED]

2. **The exhaustion degeneracy.** The frozen design set k=4 retries against
   2 options. Acceptance requires proposing the engine's answer; a working
   verifier therefore implements rejection sampling with up to 5 seeded
   draws over a near-uniform 2-option distribution (A3's attempt-0 accuracy
   is 0.53). Under the stated assumption that the retry sampler's softmax
   draws are not pathologically peaked on the distractor, a *working* A3
   converges to ≈1.0 regardless of whether the host understands a single
   feedback line — pure oracle filtering. [DERIVED, with the sampling
   assumption flagged]

3. **The control asymmetry.** c1's deranged verifier cannot license
   rejections (it refuses and abstains — disclosed in the runner itself,
   line ~1132), so s1's shuffled control compares an accept/reject oracle
   against an abstainer. It can detect content destruction; it cannot
   separate "the derivations taught the host" from "the oracle filtered the
   host's guesses". No arm in the design (e.g. an uninformative-rejection
   "try again" control at matched retry budget) makes that separation.
   [MEASURED design; DERIVED consequence]

**A sobering counterfactual.** Had line 342 been typed correctly, the
plausible readout is A3 ≈ 1.0 by exhaustion (point 2), a PASS-shaped primary
(lift ≈ +0.30 over A1), s1 passing (c1 pinned at 0.53 by its abstaining
verifier), and every rule-0 gate TRUE — a mechanical **PASS** measuring
oracle filtering, not host reasoning, that the frozen gates were not built
to catch. The type defect, perverse as it sounds, prevented a false
affirmative that would have been far more expensive than this
INSTRUMENT-INVALID. [COUNTERFACTUAL — stated assumptions above; never
evidence for or against anything]

---

## 2. What INSTRUMENT-INVALID licenses (assessment 1)

**Thesis-wise: nothing.** Not a FAIL: `primary_lift_lb95 = −0.196` was
computed over an A3 arm that never received the treatment — its rows are a
padding-shape contrast (§4), not the hypothesis — so KILL-b's meaning ("the
derivations do not help the host; route to L3b") is unlicensed, and no L3b
routing follows from this run. Not a PASS in any direction, and not evidence
about verify-retry's value either way. The CLAIM CAP stack (kernel-specific
value needs the knull c5 ablation; sign-only scale language; gold-parse
scope; depth ≤ 4) never comes into play because nothing beneath it is
licensed. [ASSESSMENT, tracking the frozen verdict semantics]

**What it does license — instrument findings only:**

1. *The engagement finding*: an inference-time verify-retry instrument at
   this operating point was frozen, piloted, and run without its verifier
   ever engaging, for the two-layer reason in §1. [MEASURED+DERIVED]
2. *The host-validity result*: `host_validity_valid = TRUE` (A7 1.000 ≥
   0.85, A5 0.944 ≥ 0.75) — the ENTITY form is the first rules-lane host
   surface on which the pinned hosts demonstrably operate. The
   elicitation problem that killed rules-1 and rules-1-b is solved at this
   form. That is an instrument datum, not a hypothesis datum. [MECHANICAL]
3. *Quarantined descriptives*: A1 0.703 vs A3/c1 0.531 (§4); A7 1.000
   (§5); all exploratory under the instrument-invalid verdict.
4. *Consequences for dependents* (per the critical-path doc, endorsed):
   knull-hostlift's activation gate (`primary_pass true`) is unfulfillable
   on this branch — the record must never be frozen or run; s3
   (verifier-offload efficiency) is unevaluable this run; rules-2's
   sequencing gate and B4/gap23 fate need re-registration against an
   instrument-valid successor or a struck s3′. [MEASURED gate texts;
   MECHANICAL-PENDING for the owning roles]

Engine-side correctness is untouched: the CPU certificate (engine 858/858
vs third-party gold, C_dec stated/entailed 1.0/0.0) and twin agreement
stand, pinned and pre-dating this campaign. [MEASURED]

---

## 3. The three-failure pattern (assessment 2)

### 3.1 The pattern

| iteration | failing interface | signature | caught by |
|---|---|---|---|
| rules-1 | elicitation (direction-unstated cue + menu adjacency) | all arms 0.000 incl. the oracle arm | post-hoc; VOID |
| rules-1-b | task form (relation word, form-dead for unaided hosts) | pilot A5 0/24 | launch gate, $0 final-phase |
| rules-1-c | verifier engagement (address-check defect atop a 2-option vacuity) | A3 `attempts=1` ×2,574, A3≡c1 | engagement gate, at analysis |

Each fix moved the failure exactly one interface inward, and each new
failure occurred at the first interface *not yet exercised by a gate at the
operating point*: rules-1-b added the host-validity gate and the form
failed the pilot; rules-1-c added the all-arms pilot and the form passed —
but the pilot checked only the host-validity floors, and the one channel it
did not assert on (rejection rate > 0) is the one that was dead, even
though its signature was sitting in the pilot rows. The generalisation is
uncomfortable but well-supported: **in this programme, instruments fail at
the first untested interface, and "tested" must mean exercised at the
operating point, not argued from design.** The steering read's proposed
mandatory instrument pilot (every gate channel exercised before freeze) is
the process-level fix; this campaign is the fourth datum in its favour.
[MEASURED history; ASSESSMENT]

### 3.2 Structurally un-instrumentable, or a fixable design-space point?

The precise claim I can support: **at this operating point — a 135M host,
depth-2 kinship items with 3-name lexicons, and a closed forced-choice
surface — the model-level claim H-R1 ("verify-retry lifts the host") has no
valid carrier in this design family.** Three independent boxes close it
(§1.2): at n=2 a non-leaking verifier is necessarily vacuous and an
informative one necessarily decisive; at k ≥ n−1 a working verifier is a
rejection sampler whose ceiling is the verifier's knowledge, not the
host's; and the shuffled control abstains rather than rejects, so even a
"lift" could not be attributed to feedback comprehension. Note the third
box means a working A3 would have measured a *systems* quantity — host +
verifier composite accuracy — which A7 already delivers at 1.000 for a
fraction of the mechanism. [DERIVED + ASSESSMENT]

**The elicit-gold(2-option) vs non-vacuous-verifier(>2-option) tension.**
The 2-option surface was not a careless choice; it is where the elicitation
evidence pushed. The lineage measured: 23-way relation-word surface —
form-dead at both hosts (gold top-1 in 1/72 R3 probes, 0/30 at R1); 23-way
with fixed frame — A7 only 0.833; entity 2-option — A1 0.703, A5 0.944, A7
1.000. Elicitability at 135M scale pushes the option count *down*; verifier
informativeness (rejection must eliminate less than everything) pushes it
*up*, to n ≥ 3 with retry budget k ≤ n−2. And the item bank binds from
below: a 3-name lexicon (base, bridge, chain-top) minus the anti-echo base
exclusion yields exactly 2 candidate surfaces. The routes to n ≥ 3 are all
substantive: fresh out-of-story names are non-competitive (a
"pick-a-name-from-the-story" surface heuristic defeats them, and rejecting
them is uninformative in practice while still eliminating options);
cross-item names likewise; genuinely competitive in-story distractors
require deeper chains (4+ name lexicons), which requires extending the
closed rule inventory past R-CHAIN len-2, which touches the certified
engine layer — a new certificate, KILL-a re-execution, coverage
re-derivation. Whether the 135M host even remains engageable at n = 3–4 is
unmeasured; it is precisely the kind of axis on which the last three
instruments died. [MEASURED lineage data; DERIVED structure; ASSESSMENT]

So: **un-instrumentable as operationalised, at this scale and item bank —
[ASSESSMENT]** — while a *neighbouring* design point (n ≥ 3 competitive
in-story options, k ≤ n−2, a feedback-content control) is not excluded by
anything measured. Reaching it is a design-research project with an
engine-layer dependency, not a repair. The word "repair" for rules-1-d
would be a misnomer; §6 states what the point would minimally require.

---

## 4. The A1 − A3 gap: a measured non-neutrality of the "neutral" padding

A1's prompt and A3's attempt-0 prompt are byte-identical *except* that A1 is
padded with the ASM-1127 neutral sentence block ("This line is neutral
padding text with no information about the family.", repeated to the
A2-shaped token target, inserted between question and answer cue), and A3
is unpadded (`run_alone_cell` vs `run_verify_retry_cell` +
`build_prompt`). Same items, same seeds, same options, same scorer. The
accuracy difference is 0.703 − 0.531 = **+0.171 attributable to the padding
block alone**. [MEASURED code + rows; DERIVED attribution]

Two consequences. (i) The registered "token-matching padding is neutral"
premise (PROPOSED-ASM-1127) is measurably false at this host and surface —
a ±0.17 prompt-shape sensitivity dwarfs the 0.05 smallest effect of
interest. (ii) Any successor design must surface-match the treatment arm's
attempt-0 prompt to the baseline (pad both or neither), otherwise the
primary contrast confounds the treatment with prompt shape from the first
byte. The supplied `primary_lift_lb95 = −0.196` is, in substance, a
*padding-shape effect with the wrong sign convention for a hypothesis test*
— further reason it must not be read as evidence about derivations.
[DERIVED; ASSESSMENT]

The direction (padding *helps*, or its absence *hurts*) is itself a small
instrument curiosity — plausibly cue-adjacency shaping at the 135M, the
same mechanism family as the rules-1 menu-adjacency defect — but resolving
it is not on the critical path. [ASSESSMENT; UNRESOLVED]

---

## 5. The A7 = 1.000 signal, precisely (assessment 3)

What A7 is: the engine answers from Cl(S) with proof; the prompt carries
*only* the bare derived fact plus question and cue (no stated-facts block,
no proof prose); the LM transcribes into a 2-option forced choice. The
injected line *is* the answer, verbatim ("<gold> is <base>'s <rel>"). A7 is
an **injected near-oracle derivation arm**, prereg-scoped as the
attribution-clean *systems* arm and, in this run, as a host-validity gate
component. [MEASURED design + prompt builder]

What A7 = 1.000 (and the +0.297 over A1) licenses:

1. *Instrument duty, served*: the 2-option entity channel is fully
   transparent to a verbatim in-context answer (floor 0.85 cleared at
   ceiling). This is the gate doing its job. [MECHANICAL]
2. *A sign-redundant echo of the measured content finding*: "aligned
   content in context helps the host" is already verdict-grade via
   f2b-transfer (+0.2507, audit CONFIRMED) and DECONF-B (Δ_align +0.2697,
   audit CONFIRMED). A7−A1 replicates that sign but adds nothing beyond
   it: the injected content here is the *full answer*, so the arm sits at
   ceiling by construction where f2b/DECONF-B measured graded value; and
   the contrast is prompt-surface confounded (render-only vs
   facts-plus-padding — not an all-else-equal injection; that matched
   contrast was A2's role, demoted to descriptive at freeze). [MEASURED
   verdicts; DERIVED]

What it does **not** license — and this is the point to be precise about,
because a +0.30 headline invites the wrong reading: it is *not* the
autonomous engine claim. H-R1's subject is a host improving *its own*
answers under engine verification; A7's host performs transcription of an
engine-computed result. The critical-path claim cap — "the A7 = 1.00
render-only read is a rendering-competence datum, never an inference
claim" — is exactly right and is endorsed here. Even the licensed *systems*
contrast for A7 (s4, A7 vs c6 axioms-as-text) is unlicensed this run under
the instrument-invalid verdict. [ASSESSMENT, tracking the frozen caps]

---

## 6. What a valid rules-1-d would minimally require; fourth iteration vs
pivot (assessment 4)

Minimal necessary conditions, each traceable to a measured failure above —
necessary, not claimed sufficient:

1. **A verifier that is exercised, not argued** [from §1.1]: typed payload
   interfaces or a unit test asserting the verifier *rejects a known-wrong
   proposal and accepts the licensed one* on real item bytes; plus a
   blocking pre-freeze engagement pilot showing a nonzero rejection rate at
   the operating point (the rules-1-c pilot contained the failure and no
   check read it).
2. **n ≥ 3 with competitive in-story distractors** [from §1.2 box 1]:
   requires deeper-chain items (4+ name lexicons), hence rule-inventory
   extension past R-CHAIN len-2, hence re-certification (new KILL-a run,
   coverage re-derivation). A cheap host-engageability pilot at n = 3–4
   must precede any build — this axis is unmeasured.
3. **Retry budget k ≤ n − 2, or attempt-indexed scoring** [box 2]: so
   acceptance cannot be reached by exhaustion and the composite cannot be
   mistaken for the host.
4. **A feedback-content control** [box 3]: an uninformative-rejection arm
   ("rejected; try again") at matched retry budget, separating "feedback
   taught" from "resampling filtered". The deranged-rules c1 cannot do
   this work.
5. **Surface-matched attempt-0 prompts** [§4]: the +0.171 padding effect
   must be designed out of the primary contrast.
6. **An information-theoretic leak criterion** [box 1]: feedback bounded in
   the option-set entropy it removes, replacing (not merely supplementing)
   the lexical gold-token guard.

**Fourth iteration vs pivot — considerations, not a recommendation.** The
cost shape of rules-1-d is a redesign with an engine-layer dependency (item
2 alone forces re-certification) plus two unmeasured-risk pilots, in a lane
that has consumed three freeze-plus-campaign cycles; and even a flawless
rules-1-d measures inference-time cooperation, the precise interface that
has now failed three different ways. The alternative already on the board
(rules-2 REWORK-3, train-time internalisation) removes the inference-time
cooperation requirement entirely — the host need not heed a verifier at
deployment — and its rebuild is commissioned, though it carries its own two
open design problems (2-option derangement re-operationalisation; the
non-bridge-name shortcut audit). A third option named in the critical path
is to declare the inference-time slot unresolved rather than force either.
The steering read's on-record opinion ("dead-end as currently conceived;
move the slot's weight to rules-2; keep rules-1-d as a paper design gated
on a demonstrated nonzero rejection rate") is consistent with everything
measured here. **The decision is the maintainer's open issue #24; this
document supplies the instrument analysis it needs and takes no position it
would pre-empt.** [ASSESSMENT throughout; DECISION-OPEN]

---

## 7. Residue worth keeping regardless of the #24 branch

- The ENTITY form's host-validity numbers (A5 0.944, A7 1.000, A1 0.703 at
  chance 0.5) are the rules lane's first working host channel; any
  successor (rules-1-d, rules-2 rework) should inherit the form and its
  floors. [MECHANICAL/MEASURED]
- The padding non-neutrality (+0.171) is a reusable instrument fact for
  every small-host forced-choice design in the programme. [MEASURED]
- The two-layer failure (§1) is a clean case for the mandatory
  exercised-at-operating-point instrument pilot as prereg protocol — the
  cheapest change with the largest expected save, four campaigns of
  evidence deep. [ASSESSMENT]
- The counterfactual false-PASS (§1.2) argues that gate design should model
  *both* degeneracy directions of an interactive arm: never-engages
  (vacuity) and always-decides (oracle capture). rules-1-c gated the first
  only. [ASSESSMENT]

## 8. Limitations of this reading

The §1.1 code diagnosis is a reading of the pinned on-disk bytes
(`91d780f3…`) whose sha matches the critical-path doc's statement of the
as-run rules-1-c runner; if the staged Modal bytes differed in
`licensed_rejection`, the proximate mechanism would need re-derivation
(the design-layer analysis in §1.2 is unaffected). The exhaustion
counterfactual assumes non-degenerate softmax draws by the seeded retry
sampler. The mechanical numbers in §0 are consumed as supplied; this
document performed only read-only row re-aggregation as a cross-check and
ran no analysis script. Nothing here alters any frozen object, registers
any assumption, or issues any verdict.
