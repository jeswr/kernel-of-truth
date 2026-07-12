# f2b-errors — error analysis of the f2b-transfer stage-2 PASS run (mechanism deepening; $0, no new GPU)

**Author:** Fable (analysis agent), 2026-07-11. **Status: PROVISIONAL — descriptive/diagnostic only.**
This document DEEPENS the mechanism understanding of the stage-2 result. It does **NOT re-verdict**:
the verdict object stands untouched (`registry/verdicts/f2b-transfer.json` — **PASS**, fired rule 4,
primary +0.25066666666666704; `audit.state` = **CONFIRMED**, `registry/audits/f2b-transfer/1-gate-a-codex.json`
[MEASURED: verdict object read at source; note the audit has CONFIRMED since
`docs/next/interpretations/f2b-transfer-stage2.md` was written with the PENDING rider — that doc's
conditionality clause is now discharged in the confirming direction]). Every number below is either
restated from a pinned artifact [MEASURED] or recomputed by this document from the raw run-records
[DERIVED] — no pinned analysis output is altered, and nothing here is an endpoint.

**Scope and riders (bounding everything below):**
- All findings are inside the frozen extrapolation envelope (≤1.7B hosts, kernel-rendered templated
  definitional QA, 108 covered concepts, k=4, THIS gold standard) [STIPULATED: envelope, quoted in
  full in the stage-2 interpretation §1 — not re-quoted here, adopted verbatim].
- Every per-item join below is a **reconstruction**: eval set = the first 250 externally-labelled
  `data/d-qa-t/items/covered.jsonl` items in pinned rank order (the runner's `build_eval_set`,
  `poc/f2b-transfer/runner/f2bt_runner.py:873–905`, replicated exactly), joined to the
  `item_correct_ext`/`item_correct_mem` vectors in
  `poc/f2b-transfer/results-incoming/20260711-184448-modal/run-records-f2bt.jsonl` and to
  `data/d-adj-t/labels.jsonl` gold. Per-item RETRY TRACES (attempt counts, per-attempt answers,
  per-item retrieval events) are **not** in the run-records — only aggregate `verifier_engagement`
  blocks exist — so every attempt-level quantity below is inferred from the correctness vectors +
  the runner code, and is tagged accordingly.
- **Calibration check (gates this whole document):** the reconstruction reproduces the verdict's
  primary exactly — net corrected item-seeds 188/750 = 0.25066… ≡ the pinned effect_size, and every
  arm accuracy (alone 0.3960, kernel 0.6467, shuffled 0.4027, gloss 0.4000, R3 0.6240, dual-scoring
  gap 0.0053) matches the verdict object [DERIVED, cross-checked against MEASURED].

---

## 0. The raw material

16 run-records: {model-alone × R1,R3} + {kernel-verify-retry, shuffled-kernel-verify-retry,
gloss-self-verify-retry × R1}, seeds {0,1,2}, 250 items each, + 1 extraction-instrument record
(0 extraction errors / 0 failures / 500 labelled) [MEASURED: run-records-f2bt.jsonl]. Eval prefix:
250 items over **103 concepts**; type mix def-match 74, term-match 75, claim-true 39, claim-false 62
[DERIVED from the reconstructed prefix]. Kernel membership key agrees with external gold on
**240/250** items (0.960 — consistent with the stage-1 endorsement A = 0.9610 on the full 333-item
resolved set [MEASURED: verdict `sec-endorsement`]).

Two structural facts of the harness, read at source, that organize everything:

- **F1 — the alone arms are deterministic.** Attempt 0 is argmax over option logprobs
  (`f2bt_runner.py:508–521`); the alone arms take attempt 0 only. Verified: the R1-alone AND
  R3-alone per-item vectors are **byte-identical across all 3 seeds** (ext and mem) [DERIVED].
  Every bit of seed variance in the experiment lives in the retry sampler.
- **F2 — retries are rejection-resampling from the host's own softmax.** On rejection the model
  resamples from the softmax over option logprobs (multinomial, `f2bt_runner.py:512–518`);
  acceptance = string-normalised consistency with the pinned kernel record
  (`KernelVerifier.check`, :297–318). The verifier never *proposes* an answer; it only decides
  when to *stop*. [MEASURED: code at source.]

## 1. Anatomy of the +0.2507: a one-way ratchet, entirely inside the two MCQ types

Flip accounting at item-seed grain (750 = 250 items × 3 seeds), kernel arm vs alone, external gold
[DERIVED]:

| type | n items | alone acc | kernel acc | lift | help (0→1) | harm (1→0) | net |
|---|---|---|---|---|---|---|---|
| def-match | 74 | 0.270 | 0.712 | **+0.441** | 98 | 0 | +98 |
| term-match | 75 | 0.147 | 0.547 | **+0.400** | 90 | 0 | +90 |
| claim-true | 39 | 0.205 | 0.205 | ±0.000 | 2 | 2 | 0 |
| claim-false | 62 | 0.968 | 0.968 | +0.000 | 0 | 0 | 0 |
| **total** | 250 | 0.396 | 0.647 | **+0.2507** | 190 | 2 | **+188** |

- **The lift is 100.0% MCQ.** 188/188 net corrected item-seeds are def-match + term-match; the two
  claim types contribute exactly zero net [DERIVED]. The claim-false zero is a ceiling effect
  (alone already 0.968). The claim-true zero is NOT — headroom was 0.795 and the verifier engaged
  (§3). So: **the +0.2507 lift is broad across concepts but narrow across item types** — within
  MCQ, 84 of 96 concepts carrying MCQ items show positive lift, 12 zero, **0 negative**
  [DERIVED]; across types, two of four channels carry everything.
- **Zero MCQ harm.** Not one MCQ item-seed went right→wrong under verification. With a
  240/250-endorsed key and a stop-on-accept loop, verify-retry behaved as a pure ratchet on the
  4-option surface [DERIVED; mechanism reading INTERPRETIVE].
- Because the baseline is deterministic (F1), the lift decomposes cleanly over the 118 MCQ items
  the R1 argmax gets wrong (0/3 seeds) vs the 31 it gets right: kernel arm = 1.000 on all
  alone-right items (no harm), 0.531 on the alone-wrong mass [DERIVED]. "Difficulty" for the
  baseline is binary at this grain.

## 2. Residual-error taxonomy: 265 wrong item-seeds, ~97% host-side, ~3% kernel-content

Kernel-arm external-gold errors, 265 item-seeds total; per-item wrong-seed histogram
{0 seeds: 111 items, 1: 50, 2: 52, 3: 37} [DERIVED]:

| class | item-seeds | share | mechanism |
|---|---|---|---|
| **E1 claim-true "no"-lock** (host proposal failure, verifier engaged) | 91 | 34% | §3 |
| **E2 MCQ sampling shortfall within k=4** | 166 (term 102, def 64) | 63% | §3/§8 |
| **E3 refuted-key enforcement, accept-path** (kernel content wrong, verifier locks it) | 6 | 2.3% | §4 |
| **E4 refuted-key enforcement, reject-path succeeded** (kernel content wrong, model flipped to it) | 2 | 0.8% | §4 |

- The 37 always-wrong (3/3 seeds) items: **29 claim-true, 4 term-match, 2 def-match, 2 claim-false**
  [DERIVED]. Their kernel-arm MEM accuracy is 0.054 — i.e. on the items the system reliably gets
  wrong vs external gold, it is also NOT complying with the kernel's own key: these are almost
  entirely **failures of the host to produce the key answer**, not the kernel steering wrong
  (the two claim-false exceptions ARE kernel-steering-wrong — §4).
- **Kernel-CONTENT-attributable error is ≈3% of the residual (8/265 item-seeds).** Everything else
  is the 135M proposal distribution failing to reach the (externally-correct) key within 4 draws.
  [DERIVED; the attribution split is this document's classification, disclosed as such.]
- **Retrieval hit-miss axis: degenerate by design.** `n_decidable = 250/250` on every
  kernel-arm seed [MEASURED: verifier_engagement]; every eval item is record-backed with the
  record pin re-hashed at use (ERR_RECORD_PIN fail-closed); the extraction instrument recorded
  0 errors / 0 failures. There are NO retrieval misses to taxonomize on the true arm; the
  shuffled arm is the forced-miss control (§6).

## 3. The claim-true wall: an engaged verifier cannot move a host with no proposal mass

The sharpest single mechanism fact in the run [DERIVED throughout, from vectors + F1/F2]:

- **Both rungs answer "no" to every claim item.** R1-alone AND R3-alone give "no" on 101/101
  claim items (verified: claim-true alone-mem = 0/39 and claim-false alone-mem = 62/62, both
  rungs, identical across seeds). At these scales the claim items measure a yes/no response
  prior, not content discrimination — R3's apparently fine 0.968/0.205 claim profile is the SAME
  constant "no" as R1's.
- **The verifier engaged and was ignored.** The aggregate `n_attempt0_rejected = 157` decomposes
  exactly as 118 MCQ-wrong + **39 claim-true** + 0 claim-false [DERIVED: arithmetic
  reconstruction, exact]. So on every seed the verifier rejected ALL 39 claim-true attempt-0
  answers ("no" while the claim is a record member) and granted 4 retries each — yet the final
  answer flipped to "yes" on only **4/117 item-seeds** (kernel-arm claim-true mem acc 0.034).
  Under F2 this bounds the host's per-draw yes-mass at roughly 1% on these prompts
  [DERIVED, order-of-magnitude; attempt-level traces absent, see §8 for the sampler caveat].
- **Mechanism law this licenses (INTERPRETIVE, the document's own):** verify-retry converts the
  host from argmax to rejection-sampling against the kernel's acceptance set; per-item lift is
  bounded by the host's tail mass on the key answer within k draws. The verifier supplies
  *direction*; the host must supply *proposal mass*. Where that mass is ~0 (binary claim items
  under a hard "no" prior), a perfectly-informed deterministic verifier with 4 retries moves
  nothing. The offload is real but it is **selection, not injection** — no knowledge flows from
  the store into the host's distribution; the store only gates which sample survives.
- Falsifiable corollaries (EXTRAPOLATION, direction-only, for future designs — NOT claims):
  claim-true lift should appear under (a) larger k, (b) answer-order/option-format debiasing, or
  (c) feedback-bearing retry prompts (the current retry prompt is byte-identical to attempt 0's);
  MCQ lift should saturate in k much faster than claim lift.

## 4. The 10 externally-refuted keys: enforcement is asymmetric, and the "no"-bias is an accidental shield

All 10 items where the kernel's key disagrees with blind external gold are **claim-type**
(8 claim-true where judges rejected a record clause as not true of the concept; 2 claim-false
where judges accepted a foil the record excludes: `celebration:t3` "it is not living",
`change (the event):t3` "X does something to Y at some time") [DERIVED: item join; the full list
with claims is reproducible from the reconstruction]. Zero def-match/term-match keys were refuted —
**every kernel-content error the blind judges caught lives at claim/clause grain; whole-definition
identity survived external adjudication 149/149** [DERIVED]. This is texture consistent with the
g3 clause-grain WARNING being about a real grain distinction (pointer only; g3 is a different
instrument and is neither confirmed nor rebutted here).

On these 10 items the verifier is actively enforcing externally-wrong content, and the outcome
splits by enforcement path [DERIVED]:

- **Accept-path (2 claim-false, key="no"):** the host's "no" is instantly accepted — wrong key
  locked 6/6 item-seeds. Enforcement of a refuted key SUCCEEDS when the wrong key coincides with
  the host prior. These 2 items are the only always-wrong claim-false items in the run.
- **Reject-path (8 claim-true, key="yes", ext gold "no"):** the verifier rejects the host's
  (externally-CORRECT) "no" every attempt and tries to force "yes" — and mostly FAILS, for the
  same reason it fails in §3: kernel-arm mem compliance 4/24 item-seeds. Net measured harm on
  the whole disagreement set: alone 24/30 → kernel 22/30 correct item-seeds (−2; overall
  −0.0027 absolute).
- **INTERPRETIVE:** the host's "no"-bias acted as an accidental shield — had the verifier been
  able to fully enforce its key, the 10 refuted keys would have cost ≈−0.029 absolute instead of
  −0.003. **The same proposal rigidity that caps the lift (§3) also caps the damage a wrong key
  can do.** In a future host/budget where §3's wall falls, the key-error rate (here 4%) converts
  from latent to realized harm at roughly 1:1 on reject-path items — key quality and host
  steerability are coupled risks, not independent ones.

## 5. Where `noninferiority_vs_r3` FALSE lives: one item type, and it is retrieval-vs-knowledge

The R3 gap decomposes entirely by type [DERIVED]:

| type | kernel(R1) | R3-alone | Δ |
|---|---|---|---|
| def-match | 0.712 | 0.324 | **+0.387** |
| term-match | 0.547 | 0.853 | **−0.307** |
| claim-true | 0.205 | 0.205 | 0 |
| claim-false | 0.968 | 0.968 | 0 |

- On def-match, 135M+verifier doesn't just match the 1.7B — it fixes **59% of the item-seeds R3
  itself gets wrong** (50 of 54 alone-wrong def-match items are also R3-wrong; kernel fix-rate on
  those 0.593) [DERIVED]. The verifier reaches beyond the bigger model's knowledge here.
- On term-match the situation inverts: 57/64 alone-wrong term-match items are items **R3 already
  knows** (fix-rate by scale ≈ 0.89), while the kernel channel converts only 46% of them. Naming
  the right term is cheap for parametric scale and comparatively expensive for
  rejection-sampling on a 4-option surface with an anti-key prior.
- **INTERPRETIVE:** the efficiency headline did not fail uniformly — it failed on exactly the
  sub-surface where parametric knowledge is strong and the sampling channel is weak, and it
  *over-delivered* where both models are ignorant. "Verifier-offload replaces scale" is
  item-class-dependent even inside this templated slice; any future non-inferiority design
  should pre-register type-stratified endpoints or it will keep averaging a +0.39 and a −0.31
  into an uninformative net.

## 6. The shuffled arm as forced-retrieval-miss: the budget-exhaustion signature

The shuffled control (Sattolo-deranged record map — every lookup is a guaranteed content miss at
identical machinery/cost) recovers **+0.0067 of the +0.2507 lift = 2.7%** (5 net item-seeds, all
def-match; term-match shuffled ≡ alone EXACTLY at every seed) [DERIVED; consistent with the
verdict's `shuffled_low_recovery` TRUE, which this document does not re-adjudicate].
`verifier_engagement` under shuffle: attempt-0 rejects 149/250 (deterministic across seeds), but
`n_final_differs_attempt0` collapses to {2, 30, 2} vs the true arm's {67, 51, 85} [MEASURED].
Reading [INTERPRETIVE]: with no reachable acceptance state, the loop almost always exhausts its
budget and the final (last-draw) answer collapses back toward the host's own distribution —
retrieval-miss ≈ model-alone, not chaos. This is the cleanest available demonstration that the
lift's binding resource is the **stop rule's content**, not the retry churn: the shuffled arm
performs the same churn (same rejects, same draws, same FLOPs) and keeps none of the lift.

## 7. Harness observation for the auditor (rider — no verdict risk asserted, none dismissed)

The retry sampler's generator is seeded by `(SEED_BASE, seed, attempt)` ONLY — not by item
(`f2bt_runner.py:514–517`). Consequence: within one (seed, attempt) cell, every item's multinomial
draw consumes an identical random stream, so retry outcomes are **correlated across items within a
seed** [MEASURED: code at source; the {2,30,2} vs {67,51,85} final-differs spreads in §6 are the
visible fingerprint]. Two implications, flagged and bounded:

- The per-item paired bootstrap treats items as independent; within-seed draw-sharing partially
  violates that. With 3 independent seeds, sign-consistency 3/3, and a primary ~0.25 with LB > 0
  by a wide margin, nothing here plausibly threatens the fired rule — but the correlation is a
  fact of the instrument and belongs in the audit record. **This document does not re-verdict; it
  reports the observation.** [DERIVED + INTERPRETIVE; severity assessment is the auditor's call.]
- Effective retry diversity is LESS than 4 independent draws — so the measured lift plausibly
  *understates* what k=4 independent-per-item resampling would deliver, and §3's per-draw mass
  estimates are approximations under correlated draws. Direction-only [EXTRAPOLATION].

## 8. Mechanism synthesis (what this deepens, stated once)

The stage-2 interpretation located the value in the *authored, item-aligned answer key* (its §5).
This error analysis adds the operational half [INTERPRETIVE, resting on §§1–6 DERIVED facts]:

> **The offload mechanism is rejection-sampling with a content-true stop rule.** The kernel
> contributes exactly one thing at runtime: *when to stop sampling*. Its lift is therefore
> multiplicative in the host's proposal mass on the key (large on 4-option MCQ where the wrong
> argmax still leaves ~15–21%/draw reachable mass; zero on binary claims under a hard prior),
> immune to harm wherever the host cannot be steered (§4's shield), bounded by k, and worthless
> under retrieval miss (§6). Residual error is ~97% proposal failure, ~3% key error. The
> mechanism neither injects knowledge nor requires any — which is why it beats a 12.6×-larger
> model where both are ignorant (def-match) and loses where knowing beats sampling (term-match).

## 9. Proposed assumption records (coordinator to register; numbering per brief)

- **PROPOSED-ASM-1320 (lift anatomy):** the f2b-transfer stage-2 primary +0.25066… decomposes
  exactly as 190 help − 2 harm = 188 net corrected item-seeds/750; net lift is 100% def-match
  (+98) + term-match (+90); both claim types net zero; zero MCQ harm. [DERIVED from run-records;
  reproduces the pinned effect_size exactly.]
- **PROPOSED-ASM-1321 (baseline determinism):** both alone arms are argmax-deterministic;
  per-item vectors byte-identical across seeds {0,1,2}; all seed variance is retry-sampling
  variance.
- **PROPOSED-ASM-1322 (claim no-bias):** R1 AND R3 answer "no" on 101/101 claim items at
  attempt 0; at these rungs claim-type items measure a response prior, not content
  discrimination; claim-false's 0.968 and claim-true's 0.205 are the same constant behavior.
- **PROPOSED-ASM-1323 (engaged-but-immovable):** the verifier rejected all 39 claim-true
  attempt-0 answers on every seed (39 of the 157 aggregate rejects) yet finals flipped on 4/117
  item-seeds; the k=4 retry channel cannot move a ~99% binary prior.
- **PROPOSED-ASM-1324 (refuted-key asymmetry):** all 10 kernel-key≠ext-gold eval items are
  claim-type (0 of 149 MCQ keys refuted); accept-path enforcement locked 2 items wrong 6/6
  item-seeds; reject-path enforcement failed 20/24; net measured harm −2 item-seeds (−0.0027);
  counterfactual full-enforcement harm ≈ −0.029.
- **PROPOSED-ASM-1325 (residual attribution):** of 265 kernel-arm wrong item-seeds, ≈97% are
  host proposal failure under budget k=4 and ≈3% kernel-content-attributable.
- **PROPOSED-ASM-1326 (noninferiority localization):** the `noninferiority_vs_r3` FALSE is
  entirely term-match (−0.307); on def-match the R1+verifier arm exceeds R3-alone by +0.387 and
  repairs 59% of R3's own def-match errors.
- **PROPOSED-ASM-1327 (forced-miss signature):** shuffled-verify recovers 2.7% of the lift;
  term-match shuffled ≡ alone exactly at every seed; retrieval-miss degrades to model-alone,
  not below it, via budget exhaustion.
- **PROPOSED-ASM-1328 (shared-quantile sampler):** the retry multinomial generator is seeded
  (SEED_BASE, seed, attempt) without item — within-seed cross-item draw correlation exists;
  flagged to the audit record; per-item-independence assumptions of the bootstrap are partially
  violated; no verdict-risk determination is made here.
- **PROPOSED-ASM-1329 (mechanism law — INTERPRETIVE class):** at this scope, verify-retry lift
  is selection-not-injection: bounded by host tail mass on the key within k; harm from wrong
  keys bounded by the same steerability; value of the store concentrated in the stop rule's
  content.

## 10. What this document does NOT change

The verdict, the fired rule, every gate, the Holm family, the stage-1 endorsement, the frozen
envelope, and the stage-2 interpretation's licensing all stand exactly as written; this analysis
consumed only committed artifacts and spent $0 of GPU. The claim-item findings (§3, §4) do NOT
retro-invalidate the claim types as eval items — they were pre-registered, their gold is sound,
and their zero net effect is *informative* (it is the measurement that exposes the proposal-mass
wall). Nothing here licenses any claim outside the quoted envelope; every INTERPRETIVE/
EXTRAPOLATION line above is load-bearing for future DESIGN choices only, never for the record.

**Reproducibility:** every DERIVED number regenerates from
`run-records-f2bt.jsonl` + `data/d-qa-t/items/covered.jsonl` (rank order) +
`data/d-adj-t/labels.jsonl` via the eval-prefix rule at `f2bt_runner.py:873`; calibration =
exact reproduction of effect_size 188/750 and all five arm accuracies.
