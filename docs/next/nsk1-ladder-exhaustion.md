# nsk1 ladder exhaustion — feasibility finding + the host-scale-vs-task-family fork

- **Author:** Fable analyst role (`kern/fable-analyst`), 2026-07-10. This is the analyst's
  authoritative interpretive readout of the nsk1 pre-freeze G2 ladder (Opus reports
  mechanical facts; the interpretation is decided here). Written under the honesty-guard
  (`.claude/agents/analyst.md`); every load-bearing claim tagged.
- **What this document is:** the pre-declared write-up that §5.2.1 of
  `docs/design-neurosym-kernel-internals.md` requires when the fallback ladder exhausts
  ("the no-headroom result is written up as the feasibility finding, and host scale vs
  task family becomes a registered fork for the maintainer"). It interprets; it changes
  no registry object, no verdict, no frozen record.
- **What this document is NOT:** a verdict. nsk1 never froze; no verdict object exists;
  every number below is `phase:"exploratory"` gate data — quarantined, uncitable in any
  verdict, licensed by §5.2 only to decide pre-freeze gates and to ground this
  feasibility finding. The evidentiary grade throughout is **MEASURED-exploratory**,
  strictly below verdict grade.
- **Inputs (all read at source by this role):**
  `poc/nsk1/out/g2/g2_summary.json` (sha256
  `3971708481bdc895ed01cf9e893d53d5afccf33b9334dc72f8ff3d7638095b24`) +
  `g2_rows.jsonl` (`e0d75e1c626eb861f60f592a72cbd30d80e09ae87e1affd118f030111e3b7c48`);
  `poc/nsk1/out/g2b/g2b_summary.json` (sha256
  `e1058bad49f634423de1e747b47d87acb4948c9f22acca3cb4f9c22b3ec50a66`) +
  `g2b_rows.jsonl` (`4972ef10a0948f64aaafd08a42fa7e30863486a1d7c08588519d5c919f70ed8a`);
  `poc/nsk1/out/g2c/g2c_summary.json` (sha256
  `8db8665ebc487b5716ab3075b4c8134cf9cf8e77594cb42799c4b95fdbdc8f72`) +
  `g2c_rows.jsonl` (`67abfbf66dc1d359c7bc49000f605fbcc76dda3ee5d010177c5d19f8c6393c20`);
  the ladder spec and rung-1 adjudication (`docs/design-neurosym-kernel-internals.md`
  §5.2, §5.2.1); `data/nsk1-clutrr/headroom.jsonl` (for row-level bridge/top/base
  decomposition); `docs/next/feasibility-synthesis.md` (the synthesis this finding
  updates). Naming note: "G2/G2b/G2c" below are the **nsk1 pre-freeze headroom gates**,
  not the registry experiment `g2` (Π read-out soundness) — unrelated objects.

---

## 0. The finding in one paragraph

LOAD-BEARING: At SmolLM2-135M-Instruct and SmolLM2-360M-Instruct, zero-shot, greedy, across THREE task forms on TWO independent eval surfaces (CLUTRR third-party; nsk1-eval custom), the pre-declared two-clause headroom gate failed at every rung of the fallback ladder, so the flagship's decisive internal-vs-external contrast is UNMEASURABLE as designed at these hosts and nsk1 does not freeze [MEASURED: poc/nsk1/out/{g2,g2b,g2c}/*_summary.json, sha256s above; scope: these two Instruct checkpoints, zero-shot greedy max_new_tokens=16, the as-built prompt per form, n=100/arm/rung/form, phase:exploratory].

The failure has a specific, row-level-measured shape: the models cannot COMPOSE two
in-context facts into the queried answer in ANY tested output space (relation word or
entity name, third-party or custom surface), and delivering the engine's correct hop-1
fact as appended text does not merely fail to help — on the only form with any
in-window text-only signal it made both models dramatically WORSE (−22pp at 135M,
−31pp at 360M). The grounding content was correct, licensed, and delivered; the hosts
lacked the capability the grounding was meant to assist, and the delivery mechanism
itself disrupted them. That is the programme's first direct measurement on its central
question — "does kernel-grounding help a model?" — and at this mechanism × scale the
answer is **no, and the text-delivery mechanism is net-harmful**.

---

## 1. The complete ladder outcome (all MEASURED-exploratory, n=100 per cell)

| Gate | Surface | Form | Rung | text-only | external-text | Δ | Gate result |
|---|---|---|---|---|---|---|---|
| G2 | CLUTRR | 1 (relation word, as-built stem) | R1 (135M) | 0.000 | 0.000 | 0.000 | FAIL both clauses |
| G2 | CLUTRR | 1 | R2 (360M) | 0.000 | 0.000 | 0.000 | FAIL both clauses |
| G2b | CLUTRR | 1b (direction-corrected relation) | R1 | 0.000 | 0.000 | 0.000 | FAIL both clauses |
| G2b | CLUTRR | 1b | R2 | 0.010 | 0.000 | −0.010 | FAIL both clauses |
| G2b | CLUTRR | 2 (entity: "Who is the grandmother of X?") | R1 | **0.230** | 0.010 | **−0.220** | clause (i) PASS, clause (ii) FAIL |
| G2b | CLUTRR | 2 | R2 | **0.370** | 0.060 | **−0.310** | clause (i) PASS, clause (ii) FAIL |
| G2c | nsk1-eval (custom, rung 3) | 2 (entity, native) | R1 | 0.000 | 0.010 | +0.010 | FAIL both clauses |
| G2c | nsk1-eval | 2 | R2 | 0.000 | 0.000 | 0.000 | FAIL both clauses |

Gate clauses (pre-declared, §5.2): (i) acc(text-only) ∈ [0.05, 0.85]; (ii)
acc(external-text) ≥ acc(text-only) + 0.02; a form freezes only if both clauses hold at
BOTH rungs. `g2c_summary.json` records `ladder_exhausted: true`,
`rung3_freeze_candidate: null`. Form 1b is N/A on the custom surface (no relation-word
gold), recorded as such in the summary.

PREMISE: the ladder is exhausted per the pre-declared §5.2.1 rule and the record does not freeze [MEASURED: poc/nsk1/out/g2c/g2c_summary.json sha256 8db8665ebc487b5716ab3075b4c8134cf9cf8e77594cb42799c4b95fdbdc8f72, `ladder_exhausted: true`; the rule itself was amended into §5.2.1 BEFORE the G2b/G2c runs, so this is the pre-registered outcome path, not a post-hoc call].

---

## 2. What the rows show (analyst recount, computed independently from the row files)

These decompositions were recomputed by this role directly from the row files (not
taken from the run logs); counts are per 100 items.

**2a. The external-text damage on G2b form 2 decomposes into two distinct, measured
pathologies.** Joining `g2b_rows.jsonl` to the per-item lexicons in
`data/nsk1-clutrr/headroom.jsonl` [MEASURED: both files, sha256s above]:

| Cell (form 2) | any in-lexicon name | top (gold) mentioned | bridge (fed) mentioned | base mentioned |
|---|---|---|---|---|
| R1 text-only | 72 | 23 | 25 | 24 |
| R1 external-text | **17** | **1** | 10 | 6 |
| R2 text-only | 91 | 39 | 30 | 28 |
| R2 external-text | **49** | **6** | 29 | 18 |

- *Pathology 1 — response-format collapse.* Appending one feedback sentence ("Note:
  the mother of Joe is Lisa.") collapses name production: in-lexicon-name rate drops
  72→17 (R1) and 91→49 (R2); at R2 the bare instruction-echo "the name of the person"
  with no name rises 9→51. The extra prompt text derails the small instruct models
  from answering at all.
- *Pathology 2 — bridge capture (parroting).* Among generations that still produce
  names, mass shifts from the gold chain-top toward the fed bridge: at R2 top mentions
  fall 39→6 while bridge mentions hold 30→29. The models read the fed fact and repeat
  it; they do not compose it with the second story edge. (Same pattern as the rung-1
  diagnosis fact 3 in §5.2.1: fed-relation parroting 20→46/100, bridge mentions
  44→76/100 on form 1.)
- Gold-not-in-feedback held by construction in every arm (the feedback names the
  bridge and the hop-1 relation, never the gold), so no arm could score by copying.

**2b. The text-only form-2 "success" is at or below the guess floor — there is no
measured 2-hop composition even without feedback.** The form-2 scorer accepts the
first in-lexicon name excluding the queried base; each item has a 3-name lexicon, so
indiscriminate non-base name emission scores ≈0.5. Measured text-only accuracies
(0.23 R1, 0.37 R2) sit BELOW that floor, and the R2 text-only name distribution
(top 39 / bridge 30 / base 28) is consistent with near-uniform name selection
[MEASURED: recount above]. Clause (i) "in-window" was therefore satisfied by
chance-level name emission, not by composition skill. This sharpens the §5.2.1
pending guess-floor disclosure into a measured statement: **at R1–R2 there is no
evidence of 2-hop composition in ANY arm of ANY form, including text-only.**

**2c. G2c exhaustion is robust to scorer strictness (with the truncation confound
checked).** The custom corpus uses double-barrelled surnames ("Petra Krail-Krail")
and max_new_tokens=16 truncates some generations mid-name; the strict scorer requires
the full surface. Recounting leniently (gold FIRST name appearing anywhere in the
generation): R1 text-only 1/100, R1 external 1/100, R2 text-only 6/100, R2 external
0/100 [MEASURED: g2c_rows.jsonl `gold_first_in_*` fields, recounted by this role].
Even at maximum leniency R2 text-only (0.06) scrapes clause (i) while clause (ii)
still fails in the same direction (external 0.00 — the delivery-hurts pattern
reproduces on the custom surface). The exhaustion verdict does not depend on scorer
strictness. Notably the G2c generations mimic the two-hop SURFACE form ("The mother
of the mother of X is …") while filling in wrong or hallucinated names — form without
composition.

---

## 3. Interpretation — the flagship and the central question

**3a. For the flagship (nsk1 and the neurosymbolic-internals line).** The flagship's
decisive experiment needs a comparator: internal steering-write-back vs the SAME
engine content as external text at matched budget. The ladder found that at R1–R2 the
external comparator is vacuous (clause ii) and — on every form but one — the task has
no floor (clause i). There is no measurable contrast to run. The pre-registered
machinery worked exactly as designed: ~$10 of quarantined gate spend killed a ~$60
Tier-2 campaign that could not have produced an interpretable result, BEFORE freeze
and before any final-run GPU.

DECISION: nsk1 does not freeze at R1–R2 on either eval surface; the flagship's direct test is deferred to the registered fork of §6, not silently redesigned [MEASURED: the three gate summaries, sha256s in the header; pre-declared outcome path per §5.2.1].

**3b. For the central question ("does kernel-grounding help a model?").** This is the
programme's first direct end-task-adjacent measurement of grounding DELIVERY, and it
is negative in a specific and instructive way. The failure is not in the kernel: the
engine resolved the correct, licensed hop-1 fact every time (l3a-grade machinery),
and the rows show the fact ARRIVED (bridge mentions rise under feedback). The failure
is in the host: at 135M/360M the models cannot execute the compose step the grounding
is meant to assist, and injecting correct grounding text actively disrupts what
little task behaviour they have. Grounding cannot help a model that lacks the
capability the grounding feeds into — at these scales the binding constraint is host
capability, not knowledge availability.

The behaviour is eval-independent (third-party CLUTRR and custom nsk1-eval agree),
form-independent (relation-word and entity forms agree), and scorer-independent
(§2c). It is NOT mechanism-independent or scale-independent — see §5.

---

## 4. Per-thesis implications

**4a. Correctness thesis (kernel as source of checked truth).** Unchanged at the
verdict level — nsk1 gate data is quarantined and flips nothing, and the correctness
thesis's semantics core (registry g2/g3/g8/g9) remains frozen-but-unrun. What changes
is the DELIVERY picture: the thesis's usefulness half requires some mechanism by
which checked content reaches a model, and the cheapest mechanism (append the fact as
text) is now measured net-harmful at the smallest hosts. The correctness thesis's
viable delivery region at tiny scale narrows to topologies where the ENGINE, not the
model, consumes the kernel content.

**4b. Efficiency thesis (small-model + kernel ≈ bigger model at lower cost).** This
finding cuts directly against the thesis's simplest form at its most favourable price
point. The efficiency pitch wants the smallest possible host; the measurement says
the smallest hosts are precisely the ones that cannot use delivered kernel content —
the kernel made them WORSE (−22pp/−31pp on the one in-window form). Two honest
readings, both carried:

- *Narrowing, not killing.* The one real (if attribution-confounded) efficiency
  positive in the registry — f2b-replicate, 135M + kernel-verify-retry beating
  1.7B-alone at cost_ratio 0.103 [MEASURED: registry/verdicts/f2b-replicate.json,
  audit CONFIRMED; correct-alignment-specific per docs/next/feasibility-synthesis.md
  §2b] — used the kernel as an EXTERNAL ACCEPTANCE RULE: the model never had to read,
  parse, or compose kernel content; the engine judged outputs and the topology
  retried. The new negative and the old positive are therefore CONSISTENT and jointly
  informative: at tiny scale, kernel value survives in select/verify/retry topologies
  (Law 3's engine-owns-correctness seat) and dies in content-delivery topologies
  (where the model must integrate the fed fact). That convergence is this finding's
  main constructive contribution to the efficiency thesis.
- *The scale question is now live and priced.* Whether content delivery starts
  helping at some larger host is exactly fork option A (§6), decidable for ~$2–5.

**4c. Cross-experiment picture.** The programme's measured evidence now splits
delivery mechanisms cleanly: engine-external verification (f2b: positive, confounded,
audited) vs text-content delivery (nsk1 G2: negative, exploratory-grade, two hosts ×
two surfaces × three forms). The flagship's novel third cell — internal state-space
delivery — remains empty (§5).

---

## 5. Honest bounds (the over-claim guard; read before citing this finding)

This is a **MECHANISM × SCALE** finding. Its licensed scope, exhaustively:

- **Hosts:** SmolLM2-135M-Instruct and SmolLM2-360M-Instruct, pinned checkpoints,
  zero-shot, greedy decode, max_new_tokens=16, one prompt format per form. Two rungs
  in the same family = at most "a sign" under P8 discipline — and here the sign is of
  ABSENCE of headroom, which licenses no slope and no threshold estimate.
- **It is NOT "grounding never helps."** G2 tested exactly two arms: text-only and
  external-TEXT delivery. The flagship's actual novel mechanism — the INTERNAL
  patchscope-read → engine → steering-write-back arm — was NEVER RUN. G2 is a
  text-delivery floor check for the external COMPARATOR; the internal arm's cell is
  still empty. A stronger reading is available but unproven: the measured external
  damage is largely a PROMPT-SURFACE pathology (format collapse, §2a), which a
  state-space write mechanically cannot cause since it adds no prompt tokens — but
  whether the internal channel composes any better is EXTRAPOLATION (proposed
  ASM-D, §8), and the §2b composition deficit is channel-independent in the worst
  case.
- **It is NOT "tiny models can't do CLUTRR."** Published CLUTRR baselines are all
  TRAINED models; zero-shot instruct capability is a different construct, and the
  covered slice is a filtered subset, never the published benchmark (§4.7 envelope,
  leaderboard language forbidden). Few-shot prompting, fine-tuned hosts, larger
  hosts, non-greedy decoding, and other prompt formats are ALL unmeasured forks —
  any of them could open headroom.
- **Evidentiary grade:** every number is `phase:"exploratory"` pre-freeze gate data —
  MEASURED-exploratory, licensed for gate decisions and this feasibility finding,
  citable in no verdict and no paper claim. There is no nsk1 verdict object and this
  document does not create one.
- **Contamination** (CLUTRR public since 2019) is priced per §7 item 9: the contrast
  is within-item and symmetric across arms; contamination compresses headroom but
  cannot manufacture the measured DIRECTION (external below text-only).
- **n=100 per cell.** Wilson intervals on 0.00–0.06 cells are wide upward (~0.04–0.12
  upper bounds); the gate clauses were designed for exactly this n and the
  qualitative pattern (external ≤ text-only on every in-window form, both rungs, both
  surfaces) is what carries the finding, not any single cell estimate.

---

## 6. The registered fork: HOST-SCALE vs TASK-FAMILY (maintainer decision)

Per §5.2.1, ladder exhaustion makes this a maintainer fork — no silent host upgrade
inside the record. Options ranked by information-per-dollar and decidability,
cheapest-decisive-first. Each option's decision rule is the EXISTING pre-declared
two-clause G2 gate (no new adjudication machinery needed).

| Rank | Option | What it is | Cost | Decidable by | What it buys |
|---|---|---|---|---|---|
| **1** | **A′ — host-scale G2 probe** | Re-run the identical two-arm, two-form headroom check (G2b harness unchanged) at SmolLM2-1.7B-Instruct (in-family; already the programme's R3 in f2/f2b), same discarded 100-item slices, same gate | **~$2–5**, one Modal A10G run, standing G2 spend envelope | The pre-declared two-clause gate, mechanically | Locates whether "compose a delivered fact" exists in-family at 1.7B. PASS ⇒ nsk1 re-freezes at the measured-headroom host (campaign re-estimate ~$30–70, still A10G-class; Modal-for-Academics/Oxford-ARC applications cover anything larger). FAIL ⇒ the negative extends a rung and the family prior drops sharply |
| **2** | **A″ — few-shot rider at R1/R2** (bundle into the same Modal run as A′) | Same items, same hosts, k-shot compose exemplars prepended (disclosed prompt amendment) | **+$2–5** (marginal; one combined "G2d" run for both ⇒ ~$5–10 total) | Same gate | Tests whether the format-collapse pathology (§2a) is a zero-shot prompt artifact — the cheapest way tiny hosts could still be rescued. PASS preserves the efficiency thesis's smallest-host price point; construct change (zero-shot → few-shot) must be disclosed in any freeze |
| **3** | **B′ — Stage-0 back-patch diagnostic as exploratory mechanism probe at R1/R2** | The already-designed V0 back-patch sweep (§4.2) run on the text-only failure set (which is now ~everything), against the pre-declared Wilson-LB(rescuable) ≥ 0.15 floor | **~$10–20** (5–8 GPU-h envelope) | The pre-declared Stage-0 floor | The direct test of whether the composition capability exists LATENTLY at these scales (layer-timing failure) even though the text channel shows none. Rescue ≥ floor ⇒ the internal arm has headroom the text channel lacks — itself a novel, publishable contrast and the only path that tests the flagship's actual mechanism at these hosts; rescue ≈ 0 ⇒ the tiny-host internal family is dead with a measured reason. Resolves ASM-0024 |
| **4** | **C — new compose-headroom task family for tiny hosts** | Author a covered task family where 135M/360M have measured headroom (e.g. single-hop apply-one-fact shapes) | Design time + ~$5 gate runs per candidate | New G2 per candidate | NOT RECOMMENDED as next spend: it re-imports the self-authored-primary weakness the CLUTRR pivot existed to remove (ASM-0027 rationale), and single-hop shapes where parroting IS the answer make the external arm win vacuously — it would measure delivery plumbing, not grounding value. Only if 1–3 all fail and the maintainer still wants a tiny-host result |
| **5** | **D — accept the negative as the flagship's R1–R2 finding** | This document, standing | **$0** | Already decided | The floor option, and it is NOT exclusive with 1–3: the finding stands regardless; D-alone is the terminal state only if the maintainer declines further spend. Note D-alone leaves the flagship's internal-vs-external question unmeasured at every scale — the negative is about measurability preconditions at R1–R2, not about the flagship mechanism |

DECISION (proposed to the maintainer, not committed by this document): execute ranks 1+2 as ONE combined ~$5–10 Modal run ("G2d": {R1, R2 few-shot; 1.7B zero-shot} × 2 forms × 2 arms × 100 items), then rank 3 only if G2d opens no headroom OR the maintainer wants the internal-mechanism question answered at tiny scale independently; rank 4 parked; rank 5 already in force as the standing finding [MEASURED basis: the complete ladder outcome §1; cost figures from the standing §5.2 G2 envelope and §8 of the design doc].

Sequencing note: if G2d passes at 1.7B, the freeze inherits the full §5.2.1 post-G2
mechanics (corpus rebuild for the winning form, S9/S10 re-run, §4.6 power redo at
achieved n, skeptic-memo re-run) with hosts renamed — that is a rung amendment inside
the pre-declared ladder discipline, not a new design.

---

## 7. Update to the cross-experiment feasibility synthesis

`docs/next/feasibility-synthesis.md` §0 states the central question is "fully
UNMEASURED" and §2a lists nothing between the fortress wall and the model. Both
statements need a dated qualifier (edit owned by the synthesis's next revision — this
document changes no other file):

- The question now has its FIRST direct measurement, at exploratory grade:
  **negative-and-disruptive for text-delivered grounding at 135M/360M-Instruct,
  zero-shot, on 2-hop kinship composition, two eval surfaces** (this document §1–§2).
  The verdict-grade statement "zero audited end-task wins over the kernel-as-text
  null" is UNCHANGED — gate data flips no verdict and this negative is likewise
  below verdict grade.
- §2a should carry the delivery-topology split from §4c: engine-external
  verification (f2b, positive, confounded) vs text-content delivery (nsk1 G2,
  negative, exploratory) vs internal state-space delivery (EMPTY CELL — the flagship
  mechanism, untested).
- §4's efficiency bottom line ("ALIVE-NARROW") narrows further: the smallest-host
  content-delivery route is measured net-harmful; the surviving tiny-host route is
  select/verify/retry topology, pending its own de-confounding (K-NULL /
  f2b-transfer, unchanged).
- §5's ranked next steps gain one row: the G2d probe (§6 ranks 1+2, ~$5–10) enters
  as a cheap decisive item — it is the cheapest measurement anywhere in the
  programme that can move the central question's host-scale boundary.

---

## 8. Epistemic register — assumptions this finding relies on (REPORTED for coordinator registration; NOT appended to `registry/assumptions.jsonl` by this role)

- **Proposed ASM-A (STIPULATED, load-bearing for §3a/§6):** the §5.2 two-clause G2
  gate is a valid measurability precondition for the flagship contrast — a host that
  gains nothing from external-text delivery of the identical engine fact provides no
  non-vacuous comparator for internal-vs-external. Pre-declared in §5.2/§5.2.1;
  registered here as the finding's interpretive premise. Owner: analyst. Resolution:
  stands with the design; falls only if a mechanism argument shows the internal arm
  is interpretable without the external comparator (which would be a new design, not
  this record).
- **Proposed ASM-B (STIPULATED, load-bearing for the whole document):**
  `phase:"exploratory"` gate rows may ground a FEASIBILITY FINDING at
  MEASURED-exploratory grade (as §5.2.1 itself does), while remaining uncitable in
  any verdict or paper claim. Owner: analyst. Resolution: standing programme rule;
  re-examine if the honesty-guard spec changes.
- **Proposed ASM-C (EXTRAPOLATION, load_bearing: false):** compose-a-delivered-fact
  capability emerges somewhere above 360M in the SmolLM2 family (motivating fork
  rank 1). Basis: the back-patch literature measured latent 2-hop machinery on
  substantially larger hosts [LIT-BACKED: arXiv:2406.12775 (2024), via
  reports/lit-structured-parsing-and-inner-symbolic.md §2.2]; no measurement at any
  scale in this programme. Resolution path: the G2d host-scale probe (§6 rank 1).
  Never a premise — precisely why rank 1 is a probe, not a re-freeze.
- **Proposed ASM-D (EXTRAPOLATION, load_bearing: false):** the internal
  steering-write-back channel evades the format-collapse component of the measured
  external-arm damage because it adds no prompt tokens (motivating fork rank 3's
  "headroom the text channel lacks" reading). Mechanistic argument only; the §2b
  composition deficit may bind regardless of channel. Resolution path: Stage-0
  back-patch probe (§6 rank 3), which also resolves ASM-0024.
- **Relation to the four §5.2.1 pending ASMs** (entity-form construct validity;
  form-2 guess floor; 1b counterfactual; Instruct reconciliation — reported by the
  designer, coordinator registration pending): this document SHARPENS the guess-floor
  item with a measured recount (§2b: text-only form-2 sits below the ≈0.5 floor with
  near-uniform name selection at R2) and relies on the Instruct reconciliation as
  recorded. The 1b counterfactual stays a flagged non-load-bearing extrapolation;
  nothing here rests on it.
- **MEASURED numbers, scope discipline:** every quoted accuracy carries gate id,
  surface, form, rung, and n; none extends past the two pinned checkpoints,
  zero-shot greedy decoding, and the two 100-item slices. Citing any of them wider
  re-classifies the citation as EXTRAPOLATION.
