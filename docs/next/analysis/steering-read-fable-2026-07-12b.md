# Steering read — 2026-07-12b (Fable steering agent; post-rules-1-c-landing tick)

> **SUBJECTIVE OPINION, in its entirety.** This is a qualitative steering read for the
> coordinator to synthesise with the parallel GPT-5.6 read, per the dual-model
> subjective-analysis practice. It is **not** a mechanical verdict, **not** a
> feasibility conclusion, and it overrides no frozen envelope, rider, verdict rule, or
> registered assumption. **CORRECTNESS and EFFICIENCY remain INCONCLUSIVE-PENDING**
> exactly as the registry says, and nothing here changes that. Numbers cited are
> measured anchors read from the tree this tick; every judgment wrapped around them is
> opinion and should be weighed as one model's opinion.

**Sources read at source this tick:**
`docs/next/design/post-rules1c-critical-path.md` (board state + landed rules-1-c rows);
`poc/rules-1/results-incoming/20260712-142704-rules1b-parallel/` (4 slices, RUNNER_EXIT rc=0);
`analysis/rules_1c.py` (engagement gate at :186); `registry/experiments/rules-1-c.json` (frozen 09b246dc…);
`docs/next/analysis/scale-s0-interpretation.md`; `registry/verdicts/{f2b-transfer,deconf-b}.json`
(+0.2507 / Δ_align +0.2697, both audit CONFIRMED);
`docs/next/analysis/{rules1-void-degenerate-instrument,rules1b-form-misattribution}.md`;
`poc/ontology-import-g2-v2/runs/pilot-20260712-ac1/judge-pA-gpt56sol/` (authoritative pA judge active);
`poc/ddc/` (T0 harness present; build in flight per kernel-of-truth-7vv2/ifvn);
`docs/next/analysis/steering-read-2026-07-12.md` (the morning read, for continuity — and for a
self-correction, §1.3 below). The "issue #24 open on the slot decision" is [REPORTED] from the
coordinator brief; I could not resolve it via `bd show 24` and treat the slot decision's
maintainer-gated status as given by `post-rules1c-critical-path.md` §5.4.

---

## 1. What is going WELL vs POORLY — opinion

### 1.1 Well

1. **The fail-closed machinery keeps being the best thing in the repo.** rules-1-c's
   engagement gate (`analysis/rules_1c.py:186`) will, on the landed rows, fire
   INSTRUMENT-INVALID on a run people wanted to pass — every A3 row `attempts = 1`, A3
   correctness-identical to c1 on all 2,574 item×seed cells. The rows landed cleanly
   (13,470 rows, full 3-seed grid, rc=0 on all four slices), the arithmetic is
   unambiguous, and no one is arguing with it. Four instrument-invalids in a row being
   *clean diagnoses* rather than motivated readings is the programme's core asset.
   The RULES-2 pin/frame drift also failed closed (ERR_PIN / ERR_FRAME_DRIFT) instead of
   silently running stale bytes. This discipline is expensive; it is also why anything
   this programme eventually claims will be defensible.

2. **The content result is real and keeps replicating.** f2b-transfer primary +0.2507
   with endorsement 0.961, audit CONFIRMED; DECONF-B Δ_align +0.2697, bridge lift
   +0.285 (LB95 +0.255), audit CONFIRMED. That is a verdict-grade, twice-measured,
   located mechanism (item-aligned deterministic acceptance over authored content). It
   is the bedrock, and it has survived every deconfound thrown at it.

3. **scale-S0 is a model of how to buy information cheaply.** For ~30 minutes of
   shared-core compute the 10k rung confirmed the §6.5 crosstalk arithmetic (σ within
   3% of 1/√D at three dimensions), confirmed encode/storage arithmetic, *and*
   delivered four honest measured blockers (typing-source poverty, duplicate mass
   20.1% and growing down the tail, selection-rule exhaustion at 27,210, O(m²) cleanup
   death between 100k and 1M). `scale-s0-interpretation.md` correctly caps it at
   machinery-qualification. That is exactly what an engineering rung should look like.

4. **g2-import-v2 is being repaired the right way.** The v1 GO-shaped signal (0.679 vs
   0.393, p=7e-5) died on judge κ; the fix in flight is the *authoritative* frozen
   judge (pA=GPT-5.6, pilot artifacts on disk at `runs/pilot-20260712-ac1/`) rather
   than another proxy layered on a proxy. Slow, but correct.

### 1.2 Poorly

1. **The rules track has now burned three instruments in a row and produced zero
   licensed host-integration bits.** rules-1 (degenerate host scorer, VOID), rules-1-b
   (relation-word frame form-dead for unaided hosts — gold top-1 in 1/72 R3 probes),
   and now rules-1-c (verify-retry acceptance ground vacuous at a 2-option surface:
   with functional-uniqueness dropped as gold-leaking, range/gender checks can never
   reject a well-formed 2-option answer, so the verifier never engaged — A3 0.5315 ≡
   c1, below A1's 0.7028). Three failures, three *different* channels, one lane. The
   engine itself is fine (the CPU certificate stands: 858/858 vs third-party gold,
   stated/entailed C_dec 1.0/0.0). What keeps failing is the *host-side measurement
   apparatus*, and each failure costs a freeze + GPU campaign + rework cycle.

2. **The vacuity was foreseeable at freeze time, again.** My own morning read
   (steering-read-2026-07-12 §2.2, ASM-1542-proposed) flagged exactly this pattern and
   proposed a mandatory instrument pilot at the operating point. "Can this acceptance
   ground ever reject at 2 options?" is a question answerable by hand-simulation of a
   dozen items before freezing — no GPU, no run. The proposed instrument-pilot gate is
   still not part of the prereg protocol, and the programme just paid for that a
   fourth time.

3. **Self-correction on the morning read.** The 2026-07-12 read named the RULES-1 GPU
   host-lift grade the single highest-value next experiment. It ran; it will grade
   INSTRUMENT-INVALID (predicted from landed rows + frozen rules). The *prioritisation*
   logic wasn't wrong — it was the fastest licensed movement available — but the read
   under-weighted its own §2.2 warning that instruments in this programme fail at the
   operating point. The GPT-5.6 counterpart read should weigh this: my confidence in
   "freeze-ready" records has been miscalibrated once already today.

4. **FAIL-by-attrition is now the modal outcome, not a risk.** Both theses have been
   INCONCLUSIVE-PENDING through f2b, DECONF-A1/B, CASC-0′, g2, g2-import, RULES-1-CPU,
   rules-1-b, rules-1-c, and S0. The deflationary/diagnostic legs keep landing;
   the affirmative decisive legs (a valid host-integration grade, human gold anywhere
   on the g2 line, the knull rules-source ablation, any efficiency datum at all)
   keep not existing. With Fable/codex quota tightening, attrition is no longer
   passive — it is now a budget phenomenon.

---

## 2. Directions: PROMISING vs DEAD-END — opinion, ranked

**Rules inference-time verify-retry (rules-1-d as a fourth attempt): stop.** My
opinion, plainly: after three instrument failures on three channels, the
verify-retry-at-inference-time *slot design* — a small host that must cooperate with
an external verifier over a surface where rejection has teeth — is not a bad
hypothesis, but it has proven to be an instrument-hostile experimental shape at this
model scale and item surface. The measured facts boxing it in: the entity form is the
only host-engageable form (A5 0.9441, A7 1.0000, A1 0.7028), but that form at
2 options leaves a non-leaking acceptance ground with nothing to reject, and the one
ground with teeth (functional uniqueness) leaks gold. Escaping that box (k-option
enlargement, structural grounds) is a *design research project*, not a repair. I
would not spend a fourth freeze+GPU cycle on it while rules-2 exists. **Verdict-shaped
opinion: dead-end as currently conceived; the slot's weight should move to rules-2
train-time internalisation** — where the host does not need to cooperate with a
verifier at inference, which is precisely the measured failure mode (per
post-rules1c-critical-path §3, whose reasoning I endorse). Keep rules-1-d alive only
as a paper design, and only if a pre-freeze pilot demonstrates a nonzero rejection
rate at the operating point.

**Kernel-content vs kernel-structure: the evidence has answered every time it was
asked, and it keeps saying CONTENT.** DECONF-B's GS-A–kernel identity 1.0, CASC-0′'s
K3′ gloss≡plain, DECONF-A1's inertness, g2-import's breadth control lifting to within
noise of A3. No experiment has yet measured kernel-*structure* runtime value
distinguishable from "aligned, closed, broadly-anchored content". Promising:
the aligned-content store economics/authoring legs, and the knull rules-source
ablation as the honest decider. Opinion: if the knull ablation also reads
content-not-structure, the defensible CORRECTNESS story should be *reframed* as
grounded-content + deterministic engine — which the evidence already supports — rather
than continuing to buy experiments hoping structure shows up. That reframe is a
maintainer call, but the coordinator should start pricing it now.

**DDC (efficiency leg): the most promising unblocked thing on the board.** It is the
only efficiency leg gated on nothing external, it is cheap ($5 ddc0 / $60 ddc1
ceilings), it uses public benchmarks and no LLM-proxy gold, and the T0 harness is
materially built (`poc/ddc/` runner/surgery/power-sim present; T0 ops in flight).
The EFFICIENCY thesis currently has *zero* measured legs; ddc0 converts that to one
for five dollars. Fund it ahead of everything discretionary.

**Large-kernel scale track: qualified machinery, but the thesis-relevant payoff has
moved a full rung further away — background it harder.** S0's own blockers show the
100k rung is now gated on multi-source crosswalk *engineering* (2–4 weeks, the
dominant cost) before it can even reach the typing gate WordNet can't touch
(identity/dependence 100% underdetermined; the 0.95 gate unreachable in principle
from this source). And even a clean S1 licenses no thesis movement (the design's own
§14 cap). Opinion: do the three cheap S1 pre-steps now (pre-register the
duplicate/differentia policy, the S1 selection rule, the audit design; run the OBO
1,142-term SCC fixture — <1 CPU-h total) because they are decision-preserving, and
hold the crosswalk build until a quota-rich week. This lane must not compete with
thesis-critical spend.

**g2 typing-repair line: promising, capped, correctly in flight.** The v2
authoritative-judge campaign is the right instrument repair and the pilot is on disk.
But its envelope can never touch a thesis (no host model, judge-measurement validity
only), so its claim on the *tightening codex quota* must be bounded: reviews and
audits first, bulk judge campaign second, and it yields to any audit needed by a
thesis-relevant run.

---

## 3. Single biggest risk to a DEFENSIBLE verdict, per thesis — opinion

**CORRECTNESS.** The engine-level half is measured and audited (certificate + f2b/
DECONF-B content lift). The biggest risk is that the *host-integration* half never
acquires a valid instrument: three attempts consumed, the fourth (rules-2 REWORK-3)
requires a substantive rebuild with two genuinely open design problems (2-option
derangement re-operationalisation; the "pick the non-bridge name" shortcut audit —
post-rules1c-critical-path §2.3/§2.5). If REWORK-3 also freezes with an unexercised
instrument, the thesis decays to "engine correct, host integration unmeasurable at
135M-scale" — which is an attrition verdict, not a defensible one, in either
direction. **What I'd change:** make the instrument pilot *mandatory and blocking* in
the prereg protocol today (gate channel exercised at the operating point before any
freeze — for rules-2 that means demonstrating, on ~20 pilot items, that the eval
surface separates a trained host from B0 and that the shortcut audit has teeth).
Hours of work; it would have saved all three rules campaigns. And resolve the slot
decision (#24) fast — every day it stays open, the only correctness-affirmative lane
is unstaffed.

**EFFICIENCY.** The biggest risk is simpler and worse: this thesis has *never had a
live measured leg*. The verifier-offload leg just went down with rules-1-c's
instrument (s3 unevaluable under INSTRUMENT-INVALID); train-time offload is
sequencing-gated behind the same rules-2 rework; compression (DDC) is built but
unlaunched. A verdict synthesised today would say "no evidence either way after N
experiments" — indefensible as anything but attrition. **What I'd change:** decouple
efficiency from the rules lane *now* — freeze and launch ddc0 this tick (it is
pre-authorized, $5, external gold), and treat the rules-2 efficiency ledger as a
free rider on the correctness run, never as the thesis's load-bearing leg.

**Cross-cutting risk for both:** the LLM-proxy-gold overhang. Zero human panels have
run; the annotation lane ratified twice in steering is still not operating. Every
proxy-provisional number in the eventual synthesis is a soft spot a hostile reviewer
can push on. This is annotation-hours, not compute, and quota-tightening makes it
*relatively cheaper* — do it now.

---

## 4. Where the NEXT unit of compute goes, under tightening quota — opinion

Ordered; the first three are near-$0 and should all happen this tick:

1. **rules-1-c mechanical readout** (merge → `analysis/rules_1c.py` → verdict-gen →
   `registry/verdicts/rules-1-c.json`). $0. The predicted INSTRUMENT-INVALID must
   become a registered fact, not a planning read — everything branches on it, and an
   ungraded landed campaign is exactly the kind of loose end that rots.
2. **ddc0 freeze + launch** ($5). First-ever efficiency datum; gated on nothing;
   pre-authorized. Highest information-per-dollar on the board.
3. **rules-2 REWORK-3 build** ($0 compute; design + regeneration work), with the two
   design-opens under the GPT-5.6 review gate and a *blocking* instrument pilot added
   to its freeze checklist. Hold GPU launch behind the #24 slot decision.
4. **Codex quota triage:** reserve remaining codex for (a) audits of any graded
   thesis-relevant run, (b) the g2-import-v2 review-gate jobs, then (c) the bulk
   authoritative-judge campaign — in that order. No new exploratory codex spend.
5. **Annotation lane** (human-hours, not model quota): stand up the g2-line human
   gold sample per the ratified ranking. Quota-tight weeks are what this lane is for.
6. **Scale track:** the <1 CPU-h S1 pre-steps only (SCC fixture + the three
   pre-registrations). The crosswalk engineering waits.
7. **Explicitly deferred:** rules-1-d (paper design only), knull-hostlift build
   (paused; activation gate unfulfillable on the predicted branch), any new
   architecture round, ddc1 (behind its own admission gate), 100k vectorise.

---

*This read is subjective opinion for coordinator synthesis with the GPT-5.6 read. It
changes no frozen object, registers no assumption, and issues no verdict. Supersede
it when the rules-1-c verdict file, the ddc0 readout, or the #24 slot decision lands.*
