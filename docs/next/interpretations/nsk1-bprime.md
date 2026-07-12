# FABLE INTERPRETATION — nsk1 B′ (mechanical: B′ HAS RUN and its gate label is INSTRUMENT-INVALID — the ASM-0041 shuffled-source control out-rescued the real arm 0.525 vs 0.400, LB95 0.467 ≥ the 0.15 floor, so `control_rescues_at_floor` fired; per the B′ spec's own pre-declared taxonomy this lands the §8 INCONCLUSIVE branch → MAINTAINER FORK, and neither the PASS branch (redesign@R3) nor the KILL branch (retire the internal-write family) is licensed by B′; the maintainer fork was already exercised 2026-07-10 as REDESIGN and is SPENT — its successors B″ (PASS-KEYED) and Stage-1 (INCONCLUSIVE) closed the internal-steering arc with delivery POSITIVE at echo grade and integration UNRESOLVED; B′ therefore does NOT confirm a kill of the deep-internal write line, and nothing in the arc licenses recording the round-2 deprioritisation as a measured retirement)

- **Author:** Fable (interpretation agent, bead kernel-of-truth-bh1n), 2026-07-11.
  This document interprets; it changes NO frozen record, NO verdict object, NO
  results-log line, NO registered assumption, and performs no git/bd/kb
  operation. The coordinator commits and surfaces. It supplies the evidenced
  verdict-INPUT and fork recommendation only; it declares no thesis conclusion.
- **Sources (read at source):** `poc/nsk1/out/bprime/bprime_summary.json`
  (sha256 verified this session: `539040e9…f1ef7c`, matching the pin in the
  prior assessment), `poc/nsk1/out/bprime2/bprime2_summary.json` (verified
  `0ee800f7…f76f1`), `poc/nsk1/out/stage1/stage1_summary.json`,
  `docs/next/nsk1-bprime-stage0-spec.md` (the BINDING pre-declared envelope:
  §5 decision rule, §8 fork branches), `docs/next/nsk1-bprime2-spec.md`,
  `registry/assessments/nsk1-bprime.json` + `nsk1-bprime2.json` +
  `nsk1-stage1.json` (prior designer interpretations, consistent with the raw
  summaries re-read here), `registry/experiments/nsk1.json` (status: DRAFT),
  `docs/next/analysis/round2-steering.md` §"Drop / dormant", and
  `docs/next/arch/cascade-naturalisation.md` (current downstream citation of
  the nsk1 readings).
- **Quarantine banner:** nsk1 has NO frozen SAP, NO results-log, NO verdict
  object — `registry/experiments/nsk1.json` is DRAFT and was never frozen.
  Every B′/B″/Stage-1 row is `phase:"exploratory"`: quarantined, uncitable at
  verdict grade, flips no verdict. The programme's verdict-grade bottom line
  (zero audited end-task wins over the kernel-as-text null) is UNCHANGED by
  everything below. "Frozen envelope" here means the pre-declared,
  hash-pinned B′ spec envelope (decision rule fixed before the run), not a
  registry freeze.

## 1. Answer to the tasking's precise question first

**B′ has actually been run.** It is not design-only. Executed 2026-07-10 by
the runner role on Modal (A10G, fp32, greedy, chat template), 32,958 rows,
0.457 GPU-h, ≈USD 0.50, no abort, no cap trip, `n_swept = 200` = the full
text-only failure set (no subsample) [MEASURED-exploratory:
`bprime_summary.json`, hash above]. Two successor runs also exist and have
run to completion: B″ (`out/bprime2/`, 2026-07-10) and Stage-1
(`out/stage1/`). Anyone holding a "B′ designed but not run" model of this
line is one full arc behind the evidence.

## 2. The MEASURED B′ outcome, inside its own envelope

Mechanical gate label: **INSTRUMENT-INVALID** (spec §5 rule 1, trigger
`ctrl_lb_ge_floor`). The numbers, all MEASURED-exploratory at the pinned
scope (SmolLM2-1.7B-Instruct commit `31b70e2e…`, zero-shot, CLUTRR entity
form 2, 958 covered items, final-prompt-position replacement patches,
prefill-only hooks):

| quantity | real arm | shuffled-source control |
|---|---|---|
| P1 any-cell rescue (n=200) | 0.400 (LB95 0.345, UB95 0.458) | **0.525 (LB95 0.467)** |
| P1 paired excess (real>ctrl) | b=4, c=29, p(one-sided)=0.9999993 → `excess_pass` FALSE | — |
| P2 oracle bridge-patch rescue | 0.040 | 0.050 (p=0.77) |
| P2 breakage on C100 | 98.5% mean correct→wrong cell breakage (per-cell 93–100/100) | — |

`headroom_ok` true (text-only 0.7912 on all 958; 100/100 agreement with the
G2d headroom vector — the R3 host premise replicated at 9.6× sample).

The prior assessment's row-level recount (`registry/assessments/nsk1-bprime.json`,
verified against the summary re-read here) mechanistically closed the
confound: conditional on ANY patch changing the output, gold-hit rate is
~0.43–0.53 in every (arm × source-layer) stratum, real and shuffled alike —
the metric read perturbation FREQUENCY, not content; the control's advantage
is fully explained by a foreign layer-22 vector flipping outputs at 0.603 vs
the item's own vector at ~0.27. Two durable instrument facts fall out:
(i) any-cell exact-gold floors on two-candidate forms are passable by
content-free damage (the ASM-0041 control conjunct prevented a false
floor-PASS that the bare pre-declared criterion would have minted, LB 0.345 ≥
0.15); (ii) final-position replacement transplant is measured destructive
(98.5%) and content-indifferent. [Both MEASURED-exploratory; scope = this
operationalization at this host on this form.]

## 3. Which fork does the B′ evidence support?

The bead's fork map is exactly the B′ spec §8 map. Read against §5 in order:

- **PASS (→ redesign@R3): NOT licensed.** Rule 2 requires Wilson-LB ≥ 0.15
  AND `excess_pass`(P1). The LB conjunct held (0.345) but `excess_pass` is
  FALSE — the control dominated (b=4 vs c=29). A PASS reading here would be
  the false positive the control was installed to block.
- **KILL (→ retire the internal-write family): NOT licensed.** Rule 3
  requires Wilson-UB95 < 0.15; measured UB95 = 0.458. The KILL branch did
  not fire, and — the deeper point — an INSTRUMENT-INVALID probe returns
  information about the instrument, not the channel [STIPULATED: ASM-0110].
  Retiring the family on B′ would convert an instrument failure into a
  channel conclusion.
- **INCONCLUSIVE (→ maintainer fork): the supported branch.** Rule 1 fired
  (`control_rescues_at_floor`), which the spec routes to the §8 INCONCLUSIVE
  path: maintainer fork on any extension, no automatic spend.

**Verdict-input, B′ alone: INCONCLUSIVE → maintainer fork.** This is the
mechanical, pre-declared reading; no adjective is added to it.

## 4. Status of that fork: already exercised and SPENT

The recommendation is not hypothetical forward guidance — the fork was
decided on 2026-07-10 (maintainer chose REDESIGN, rank 1 of
`nsk1-bprime.json` `fork_recommendation`) and the pre-stated PASS/KILL paths
were subsequently reached THROUGH the redesign, not through B′:

- **B″ (`bprime2`), the control-unpassable redesign: PASS-KEYED on a VALID
  instrument** [MEASURED-exploratory: `bprime2_summary.json`,
  `0ee800f7…f76f1`]. Source-keyed counterfactual discrimination (coin
  control ≤ 0.5 in expectation BY ARITHMETIC) with additive norm-matched
  injection: keyacc_real 0.810 / 0.850 at cells (ℓh,ℓt) = (12,16) / (16,16),
  corrected Wilson-LB 0.730 / 0.775 ≥ the 0.70 floor, paired real>coin
  p ≤ 1.4e-10, real>role p ≤ 8.9e-07, FWER ≤ 0.05 over 9 cells; coin control
  ≤ chance at all 9 cells (instrument valid); 7 of 9 cells cleanly dead.
  First and only measured-positive delivery mode in the programme's
  topology: an internal residual-stream write delivers ITEM-specific content
  the host's computation reads out — at echo grade, teacher-forced margins,
  α=1.0, 2 of 9 cells.
- **Stage-1 (free-generation keyed rescue at those two cells): INCONCLUSIVE**
  [MEASURED-exploratory: `stage1_summary.json`]. Keying REPLICATED exactly
  (0.810/0.850 at α=1.0, now against 3 derangement seeds), but the
  echo-proof integration endpoint R− fired at 0 of 8 units and sits at-or-
  below the content-free coin null everywhere (pooled UB95 ≤ 0.0384 vs the
  0.10 kill bound), while the echo-confounded R+ residual at α=1.0 keeps the
  pre-declared all-units-both-endpoints KILL from firing (pooled UB95
  0.1423/0.1390). Keying and damage co-attenuate down the α ladder — no
  low-damage keying window exists on this operator. Integration is
  UNRESOLVED, and by ASM-0404's conservative sign semantics this design
  cannot separate "no integration" from "integration cancelled by the
  operator's own anti-gold surface push" at any n.

**Arc state: CLOSED-INCONCLUSIVE with a two-stage ledger** — delivery
POSITIVE at echo grade and replicated; integration UNRESOLVED with tight net
bounds on the echo-proof endpoint. The live fork is now the post-Stage-1
maintainer fork, whose standing rank-1 recommendation
(`nsk1-stage1.json`) is ACCEPT-INCONCLUSIVE-AND-RECORD and redirect flagship
weight to engine-external designs; rank-2 (conditional, maintainer-gated) is
a NEW operator/read-out design that de-confounds fact delivery from
answer-surface push — never a re-run or a scale-up of the measured construct.

## 5. Bearing on the round-2 steer ("deep-internal rule/write placements")

The round-2 steering note lists "deep-internal placements" under
**Drop / dormant** (`round2-steering.md` item 6). The tasking asks: does
nsk1 B′ confirm that kill, or leave it open?

**B′ confirms no kill — and the full arc does not either.** Precisely:

- B′ alone is evidence about an instrument, not the channel; its own KILL
  branch did not fire (UB95 0.458). Citing B′ as a kill of the family is an
  over-claim in the exact direction the honesty rules block [DERIVED from
  the §5 bounds + ASM-0110].
- The arc's net measured content runs mildly AGAINST a hard kill: the only
  measured-positive delivery mode in the whole programme is this channel
  (B″, echo grade, replicated), while the thing a placement would need for
  end-task value — integration into free generation — is UNRESOLVED with a
  near-zero NET bound under one conservative operator, not measured-dead
  [MEASURED-exploratory: Stage-1 R− pooled UB95 ≤ 0.0384, confound
  disclosed].
- Therefore the round-2 "drop/dormant" call is legitimate as a PRIORITY
  decision (no integration evidence arrived; the cheap-win hypothesis died;
  the corpus failure population is exhausted at 200, so more power means a
  fourth disclosed contact) — but it must be recorded as
  **deprioritised-while-unresolved**, not as retired-on-measurement. The
  current downstream citation already has this right:
  `cascade-naturalisation.md` records V-LL as "NAMED, DEFERRED —
  steering-dormant … every measured deep-internal channel is
  unresolved-at-best". Keep that wording class; do not let it harden into
  "killed by nsk1".

## 6. Fork recommendation (verdict-input for the coordinator)

1. **On the bead's own fork map: INCONCLUSIVE → maintainer fork.** PASS and
   KILL are both unlicensed by B′'s measured bounds. [MECHANICAL, spec §5.]
2. **Do not re-open that fork — mark it consumed.** It was exercised as
   REDESIGN (2026-07-10) and discharged through B″ + Stage-1. Surfacing B′
   in isolation would misstate the line's state by two runs.
3. **Surface the arc-level input instead:** internal-steering arc
   CLOSED-INCONCLUSIVE; delivery positive-echo-grade-replicated; integration
   unresolved (bounded near zero net under this operator); standing rank-1 =
   record-and-redirect to engine-external; any revival requires a new
   de-confounded operator/read-out spec with per-endpoint kill labels and
   the fourth corpus contact disclosed, maintainer-gated, no automatic
   spend.
4. **Round-2 steer disposition:** uphold the deprioritisation as steering;
   annotate it "measured status: unresolved-at-best (delivery positive /
   integration inconclusive), not killed" wherever it is recorded.
5. **Nothing here moves a thesis.** Both theses stay wherever their
   verdict-grade evidence has them; every number above is
   MEASURED-exploratory and quarantined.

## 7. Carried unknowns (so the record cannot silently narrow)

[UNMEASURED] integration of delivered content into free generation under any
de-confounded operator; keying below α=1.0 without damage (measured
co-attenuating on THIS operator only); any host other than R3, any form
other than CLUTRR entity, any position other than final-prompt-token;
ASM-0042's latent-timing band (its resolution path was consumed without
resolution and re-points at a future de-confounded probe); the role
control's mild elevation (~0.55–0.60) as a possible generic direction
transfer — a covariate candidate, never gated.
