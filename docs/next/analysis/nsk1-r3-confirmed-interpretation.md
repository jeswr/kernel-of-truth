# nsk1-r3 CONFIRMED — interpretation of the programme's first confirmatory-grade kernel-specific-structure positive (delivery-only)

## Status, scope, and provenance

- **Status:** interpretation, **ANALYSIS ONLY** (Fable, lead scientist, 2026-07-15). This document
  interprets the nsk1-r3 verdict (`registry/verdicts/nsk1-r3.json`, **PASS**, audit
  `registry/audits/nsk1-r3/1-gate-a-codex.json` state **CONFIRMED**) against the standing v8
  synthesis (`docs/next/feasibility-synthesis-v8.md`). It changes no frozen record, verdict, audit,
  registry row, or synthesis; it runs nothing and commits nothing. The proposed v8 amendment in §6
  is **PROPOSED** text only — the coordinator registers it after review-gate.
- **Verdict chain [MEASURED, verdict-grade]:** frozen record
  `registry/experiments/nsk1-r3.json` (sha `cd3f2ddd…`), pinned analysis `analysis/nsk1_r3.py`
  (sha `162331d2…`), rows `poc/nsk1/out/r3/r3_rows.jsonl` (5,320 rows, sha `b1d03f12…`),
  results-log `results-log/nsk1-r3.jsonl`, non-runner Codex audit CONFIRMED. Endpoints on the
  verdict: `primary_confirmed=true`, `confirmed_replicated=true`, `c1_role_pass=true`,
  `refuted=false`, `coin_validity_ok=true`.
- **Number provenance disclosure:** the fine-grained keyacc/LB values quoted below are read from
  `poc/nsk1/out/r3/r3_analysis_diag_offspine.json` — a **quarantined diagnostic re-execution** of
  the pin-verified analysis over the sha-re-verified rows by the non-runner verdict agent
  (verdict-gen step-5 plumbing note, `results-log/nsk1-r3.jsonl` seq 2; issue
  `kernel-of-truth-fh4j`). The boolean endpoints those numbers instantiate are the on-spine,
  audited verdict values. Nothing in this interpretation depends on the diagnostic file beyond
  reporting the magnitudes of endpoints the verdict already fixes.
- **Substrate rider (carried on every sentence below):** the confirmatory substrate is the pinned
  generator's **SYNTHETIC-SURFACE** templating branch (ASM-2357-as-amended, ASM-2364; maintainer
  #39 = (a)), never the lost AMT-paraphrase surface B″ was measured on. Every "confirmed" in this
  document means **confirmed on a fresh, structurally-identical, synthetic-surface substrate** —
  the envelope's wording, not a paraphrase.

Epistemic tags as in v8: **[MEASURED]** (verdict-grade / exploratory / instrument-fact),
**[LIT-BACKED]**, **[STIPULATED]**, **[EXTRAPOLATION]**.

---

## 1. The result [MEASURED, verdict-grade]

At both pre-registered cells, on disjoint fresh partitions with distinct derangement seed
families, under the complete /6 Bonferroni plan (α_per_test = 0.008333) that fixed the Gate-A
FWER under-correction:

| Cell | n | keyacc_real | Wilson LB (z=2.3940) vs 0.70 floor | max coin | max role | worst coin p | worst role p |
|---|---|---|---|---|---|---|---|
| **C1 = (16,16)**, partition A, seeds 20260720–22 | 266 | **0.9436** | **0.8995** | 0.5113 | 0.6391 | 1.97×10⁻³² | 4.42×10⁻²⁴ |
| **C2 = (12,16)**, partition B, seeds 20260723–25 | 266 | **0.8910** | **0.8367** | 0.5038 | 0.6203 | 1.54×10⁻²³ | 5.63×10⁻¹⁸ |

All six elementary tests (2 cells × floor/coin/role) pass at every seed with p < 0.0083;
`confirmed_replicated = true` — the **two-cell claim is licensed**, reported here with the same
prominence as the primary. Instrument fully valid: text-only headroom 0.848 ∈ [0.05, 0.85],
532 scored, zero non-finite margins, zero ties, coin validity green.

**Calibration context [MEASURED-exploratory, b3 bridge, quarantined]:** the pre-freeze surface
bridge measured paired same-item syn−AMT keyacc at +0.04 (0.895 vs 0.855, Newcombe CI
[−0.005, +0.087], n = 200; branch verdict FREEZE-AS-IS). The r3 point estimates sitting *above*
B″'s 0.850 is therefore consistent with a mild synthetic-surface favourability already measured
before freeze, plus fresh-item sampling — it is **not** to be read as "the effect grew". The
substrate direction of any surface sensitivity is now bounded and disclosed, which is exactly
what the bridge was for.

---

## 2. What a CONFIRMED delivery result licenses

**[MEASURED, verdict-grade; licence wording anchored to the frozen envelope]**

1. **The licence upgrade itself.** The programme's one live kernel-specific-STRUCTURE positive —
   internal keyed delivery of item-specific content via a norm-matched additive contrastive
   residual write at the final prompt token, read out as a teacher-forced paired margin — moves
   from **MEASURED-exploratory** (B″, Gate-A-verified, "licenses nothing alone") to **MEASURED,
   verdict-grade** (registered, frozen-before-run, powered, review-gated, cross-vendor-audited,
   replicated at both cells on disjoint partitions). This is the first entry in the
   kernel-specific-structure column of the ledger at confirmatory grade, in either direction.
2. **Specific alternative explanations are now dead.** The r3 design was built to kill the three
   Gate-A defects, and did: (a) *exploratory artifact / garden-of-forking-paths* — hypotheses,
   floors, cells, and seeds frozen before the run; (b) *FWER under-correction* — complete /6 plan,
   worst surviving p ~10⁻¹⁸; (c) *single-partition overfit / corroborating-not-independent* — two
   genuinely independent cells, disjoint fresh partitions, distinct derangement seeds, both pass.
   Additionally (d) *AMT-surface artifact* is strongly disfavoured: the effect reproduces on a
   different surface family at a bridge-consistent magnitude.
3. **The mechanism claim, exactly:** at R3 on SmolLM2-1.7B, an internal write channel exists
   through which the host reads out **item-specific** (not merely direction-generic) content at
   keyed accuracy far above an arithmetic-chance coin and a role-consistent control — i.e., the
   delivery seam is real, item-addressed, and reproducible. `primary_role_generic = false`: the
   role control specifically excludes the "generic direction, not item keying" deflation of this
   mechanism.
4. **What it forces open:** with delivery confirmed, "the write never arrives" is no longer an
   available explanation for downstream integration failures. The unresolved question is now
   cleanly localised at the **integration** seam (Stage-1's question), which is scientifically
   valuable even though — see §3 — this record contributes nothing to answering it.

---

## 3. What it does NOT license — precisely

**[STIPULATED — every clause below is the frozen envelope's own scope, restated; the
four-condition analysis is this synthesis lineage's reading discipline]**

1. **No integration, correctness-improvement, or real-generation claim.** The read-out is a
   teacher-forced paired logprob margin, not free generation. The Stage-1 free-generation probe
   read out mechanically **INCONCLUSIVE** (`registry/assessments/nsk1-stage1.json`), with the net
   generation rescue bounded near zero at the probed cell (v8 §1.5), **and this record does not
   re-open it** — the envelope says so verbatim. Confirmed delivery + inconclusive integration =
   *the content demonstrably arrives; whether the host usefully consumes it in generation remains
   unmeasured*. Mechanism, not value.
2. **It does not move CORRECTNESS off INCONCLUSIVE-PENDING — and here is the precise reason.**
   The v8 crux requires all four of {validated instrument; powered at a pre-registered margin;
   kernel-vs-**matched-generic** by construction; non-degenerate structure-sensitive contrast}.
   r3 satisfies (i) and (ii) outright, and its contrast is structure-sensitive in the *mechanism*
   sense (keying vs coin/role). But it fails (iii) **by design**: its controls are chance and
   direction controls, not a matched-generic delivery arm. No arm asked whether a
   dictionary-derived, deranged, or otherwise non-kernel-authored vector would deliver equally
   well — the kernel-origin of the delivered content was never the tested variable. And its seam
   is **delivery**, not value: it is not a four-condition kernel-vs-generic *value* result and
   was never registered as one. The verdict-words ASM-1840/1841 are untouched by this PASS.
3. **No internal-vs-external superiority claim** (the original nsk1 primary was never run); **no
   breadth/scale claim** (one host, one form, α = 1.0, one operator position, two cells, k = 2
   chains, ≤300/cell — and the programme-wide ≤108-concepts / coverage-0.3542 rider applies);
   **no CLUTRR leaderboard claim; no efficiency-thesis claim; no "the kernel powers the network"
   headline.** Scale language licensed by the verdict: **none**.
4. **No byte-faithful B″ replication claim.** The AMT surface remains unavailable through any
   verified/pinned path (D-1). What is confirmed is the *finding* on a structurally identical
   synthetic surface; B″-on-AMT itself stays MEASURED-exploratory, now with a confirmed
   same-structure sibling and a measured bridge delta rather than a stipulated equivalence.

---

## 4. Position in the v8 typed ledger

**[STIPULATED, interpretive; constituents MEASURED as cited]**

The v8 §2 ledger's counter-datum row read: *"nsk1 B″ (exploratory, Gate-A-verified, keyed
delivery 0.850) — a mechanism-side observation, not a matched-generic correctness positive; its
AMT substrate unavailable (D-1), with the #39=(a)/ASM-2364 mitigation now adopted."* After r3:

- The counter-datum is now **confirmatory-grade on the relabelled substrate**: one registered,
  audited, replicated kernel-specific-structure positive — **on the DELIVERY seam**. The ledger's
  asymmetry inverts in *grade* but not in *kind*: the deflationary Tier-1 evidence remains
  valid-instrument results at **content/value seams**; the confirmed positive remains a
  **mechanism** result. They do not meet on any common estimand, which is why both can be true
  simultaneously and why neither retires the other.
- v8 §3's observation that "H-uninstrumented's affirmative support has weakened (its one positive
  lost byte-faithful confirmability)" is now **partially reversed**: the positive did not merely
  survive relabelling, it passed confirmation on the relabelled path at the first attempt, at
  effect sizes the bridge predicted. H-uninstrumented's clause (b) — "the channels that could
  detect it are respectively starved and exploratory-then-substrate-compromised" — must be
  rewritten: the nsk1 channel is no longer exploratory or compromised; it is confirmed, and what
  it lacks is not validity but **reach** (a value-seam extension: integration, and a
  matched-generic delivery control).
- The four-condition scoreboard is **unchanged at zero, in both directions** — the crux stands.
  v8 §6 anticipated exactly this branch: "a PASS makes the structure ledger
  one-positive-at-confirmatory-grade and forces the integration question open." That is the
  branch we are on; nothing about this outcome was outside the priced outcome set.

**Explanatory-mass allocation [EXTRAPOLATION, subjective, binding on nothing]:** the v8 ~25/40/35
(sample-artifact / design-space / genuinely-deflationary) moves **little, and not across the
deflationary boundary**. The 35% deflationary mass rests on knull-v2, CASC-0′, and R4 — value- and
content-seam evidence with which a confirmed delivery mechanism is fully compatible (H-deflate
never claimed the write doesn't arrive; it claims arrival adds no kernel-specific value). What the
PASS does compress is the *sample-artifact* cell as applied to the structure ledger's one
positive: "the B″ number was exploratory noise / a surface fluke" is now untenable, and that
mass flows to the design-space cell, where the live question (delivery confirmed → is it
integrable, and is it kernel-specific at a value seam?) actually sits. My updated allocation:
**~22 / 43 / 35** — a ~3-point artifact→design-space flow, deflationary mass unchanged. Anyone
reading this as "the thesis got 3 points stronger" is misreading it: the thesis got one *question*
sharper, not one *claim* stronger. For calibration, this is smaller than the v6→v8 move (45→25 on
artifact) because a PASS here was the modal expected outcome given the bridge readout.

---

## 5. Consequences for prioritisation (no reordering proposed)

**[STIPULATED plan input]** The v8 §6 ordering survives contact with this result intact — r3 was
item 3 with exactly this licence, and its PASS *strengthens* the case for the two direct
discriminators rather than competing with them:

- The **F1-K/K-3 milestone** (v8 §6.2) gains urgency: it is now the only prepped path to the
  four-condition result that would tell us whether the confirmed mechanism carries
  kernel-specific *value* — and §3.2 above says a matched-generic **delivery** arm
  (dictionary/deranged vector, same write channel) is the natural cheap sibling to K-3 whenever
  the internal-write line is next touched. Filed as design guidance, not a premise.
- The **integration question** (Stage-1's) is re-opened as a question but NOT elevated: v8's
  deprioritisation of "any broad nsk1 campaign beyond r3" stands. Delivery-without-integration
  has now been measured twice (B″+S1; r3 confirms the first half only). A third
  delivery-side result would add nothing; only an integration-seam or value-seam design should
  next spend on this line, and only through its own gates.

---

## 6. Proposed v8 amendment (coordinator registers at commit; register verified through ASM-2367 this session, so the proposal takes 2368)

**Do not edit v8 in place.** The following row is proposed for registration, plus the §-level
note it authorises.

> **PROPOSED-ASM-2368** — supersedes-by-citation the wording of ASM-2366 (itself the amended
> ASM-2361) in one respect: the typed ledger's **counter-datum** is upgraded from "one
> exploratory substrate-relabelled mechanism observation (nsk1 B″)" to "**one confirmatory-grade,
> substrate-qualified, mechanism-side kernel-specific-structure positive**: nsk1-r3 PASS, audit
> CONFIRMED, confirmed_replicated=true — keyed delivery C1 (16,16) keyacc 0.9436 (Wilson-LB
> 0.8995 ≥ 0.70), C2 (12,16) keyacc 0.8910 (LB 0.8367), all six coin/role tests p < 0.0083 at
> every seed under the complete /6 FWER plan, disjoint fresh partitions, synthetic-surface
> substrate per ASM-2357-as-amended/ASM-2364, b3 bridge delta +0.04 [−0.005, +0.087] on record
> (`registry/verdicts/nsk1-r3.json`; `registry/audits/nsk1-r3/1-gate-a-codex.json`)". The
> upgraded row remains **DELIVERY-ONLY**: it licenses no integration, correctness-improvement,
> internal-vs-external-superiority, breadth/scale, or efficiency claim (frozen envelope,
> verbatim-controlling); B″-on-AMT itself remains MEASURED-exploratory. The **four-condition
> criterion remains unmet in either direction** — nsk1-r3 satisfies {validated instrument;
> powered at margin} but its controls are coin/role, not kernel-vs-matched-generic by
> construction, and its seam is delivery, not value. Both thesis verdict-words remain
> **INCONCLUSIVE-PENDING** (ASM-1840/1841 unchanged). The §3 clause "H-uninstrumented's
> affirmative support has weakened" is amended to record the partial reversal: the structure
> ledger's one positive is no longer exploratory or replication-path-compromised; its remaining
> deficits are reach (integration; matched-generic control), not validity. Direction-only;
> licenses no verdict.

**Authorised §-level note for v8 §2** (to be appended under "The counter-datum" when the
coordinator commits the amendment): *"[Amended per ASM-2368, 2026-07-15: nsk1-r3 PASS, audit
CONFIRMED — the counter-datum is now confirmatory-grade on the synthetic-surface substrate,
delivery-only; see `docs/next/analysis/nsk1-r3-confirmed-interpretation.md`.]"*

No other v8 row changes. ASM-2360 (verdict-words), ASM-2364 (substrate), ASM-2367 (glm-edrop
conditions) are unaffected.

---

## 7. For the maintainer, in plain terms

One honest paragraph. The programme claimed early on that it could write a concept's content
directly into a model's internals and have the model read out *which item* was written — and
until today the only evidence was one exploratory run whose original test data we then lost the
ability to regenerate. Today that claim passed a real replication: pre-registered before the run,
on freshly built data with a different surface style, at two independently sampled test cells,
with every statistical correction we previously got wrong now done right, checked by an
independent cross-vendor auditor. The mechanism is real — that is no longer in reasonable doubt,
and it is the first piece of the "the kernel's *structure* matters" story to reach that standard.
What it is not: evidence that this delivery makes the model more *correct* (our one probe of that
read inconclusive, with any effect bounded near zero), evidence that kernel-authored content
delivers better than a plain dictionary would (never tested at this seam), or anything about
efficiency or scale. Both programme theses stay exactly where they were — unproven, with the
overall evidence still leaning mildly deflationary — but the open question has become sharper and
cheaper to attack: the pipe demonstrably works, so the next dollar goes to whether anything
valuable, and specifically *kernel*-specific, flows through it.

---

## Epistemic register

- **MEASURED, verdict-grade:** everything in §1's table and endpoint list
  (`registry/verdicts/nsk1-r3.json`, PASS; audit CONFIRMED; magnitudes via the disclosed
  pin-verified diagnostic re-execution, booleans on-spine).
- **MEASURED-exploratory (quarantined):** the b3 bridge delta (+0.04, CI [−0.005, +0.087]);
  B″-on-AMT (0.850); Stage-1's mechanically-INCONCLUSIVE integration read.
- **STIPULATED:** every licence sentence in §§2–3 (envelope-anchored); the four-condition
  reading; the ledger recast in §4; §5's design guidance; the proposed amendment text.
- **EXTRAPOLATION:** the ~22/43/35 allocation and every probability-flavoured sentence in §4;
  binding on nothing.

*This interpretation is superseded when any of the following lands: an integration-seam or
matched-generic-delivery design on the internal-write line, the F1-K/K-3 freeze, or a maintainer
surface-fork decision revisiting B″-on-AMT.*
