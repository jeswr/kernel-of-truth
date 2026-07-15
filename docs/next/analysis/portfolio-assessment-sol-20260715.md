## 1. State-of-outcomes assessment

1. **[MEASURED]** The programme remains **INCONCLUSIVE-PENDING on both theses**. Of 61 experiment records, 36 are FROZEN and 25 DRAFT; the frozen index contains exactly the same 36 frozen records. No result satisfies all four requirements simultaneously: valid instrument, adequate power at the registered margin, kernel versus matched-generic construction, and a nondegenerate structure-sensitive contrast.

2. **[MEASURED — CORRECTNESS]** `knull-v2` is the cleanest direct attribution result so far: all instrument gates passed, but kernel lift was 0.2397 versus 0.2440 for the matched plain-padded comparator, with equivalence inside ±0.05. This is a registered kernel-specific null at that content seam, not a failed instrument.

3. **[MEASURED — CORRECTNESS]** CASC-0′ independently found gloss and plain attribution equivalent within ±0.05, although the overall campaign was instrument-invalid. DECONF-B and RULES-2 show the stronger structural problem: the purported kernel and generic alternatives became identical in the realized artifacts—identity 1.0 in DECONF-B and 21,780/21,780 byte-identical training examples in RULES-2.

4. **[MEASURED — CORRECTNESS]** RULES-2 nevertheless establishes that engine-materialized entailment content can be internalized by a small host: B2 accuracy 1.0 versus B0 0.657, with a lower bound of +0.316. RULES-1 similarly certifies exact closure over its scoped inventory. Neither result attributes that value to kernel structure rather than authoritative derived content.

5. **[ASSESSMENT — CORRECTNESS]** The evidence is genuinely converging on **“closed, authoritative, engine-derived content can help”**, while kernel-specific structure has not yet added detectable value when a matched generic comparator is actually realized. This is not evidence that structure can never help; it is strong evidence that further surface-level kernel-versus-prose reruns are low-value.

6. **[MEASURED — CORRECTNESS BOTTLENECK]** The largest obstacle is the absence of a sufficiently large, human-validated semantic inventory that produces materially different kernel and generic artifacts. F1-K has only 49 realized clusters, 46 with at least eight observations, against a registered requirement of 65; the AST study found only 11/24 for the cascade and 16/24 for oracle-selected best-of-six, with only 63.2% assessor agreement.

7. **[MEASURED — EFFICIENCY]** R4 gives a small positive routing signal but not the registered efficiency result: kernel routing improved the miss metric by 2.6% over global-hot, versus a 19.8% oracle ceiling; embedding routing was −0.5%, and kernel versus embedding was unresolved at \(p=.094\). There are only eight effective trace clusters.

8. **[MEASURED — EFFICIENCY]** The earlier small-host verifier-offload result is also deflationary: the fixed-\(k=4\) 135M-plus-kernel system failed noninferiority to the 1.7B reference. Thus no existing experiment shows matched-quality compression or verifier offload.

9. **[ASSESSMENT — EFFICIENCY BOTTLENECK]** The main bottleneck is a combination of too few independent routing units and no demonstrated executable backend for the large GLM path under the currently allowed Modal/non-AWS resources. The existing implementation assumes approximately 370 GB of locally streamed weights and AWS CPU/NVMe infrastructure; spending against the current eight-cluster design would be statistically and operationally premature.

10. **[ASSESSMENT]** The pattern says to concentrate future work on three things only: preventing kernel/generic artifact collapse before spend, increasing independent concept/trace units rather than token count, and testing matched quality rather than isolated accuracy or cache-hit point estimates. Mechanism-positive work such as nsk1 B″ is useful for deciding whether those experiments are buildable, but it should not be promoted into thesis evidence.

## 2. Stale and duplicate audit

### Queue-read limitation

**[MEASURED]** `bd ready` and `bd list --status in_progress` could not complete because the installed `bd` attempted schema initialization on the read-only workspace. I reconstructed readiness from the passive `.beads/issues.jsonl` export by selecting open issues whose recorded dependencies are closed. Because that export is not the Dolt source of truth, the coordinator should confirm these closures in the live database; the underlying file/result evidence is nevertheless clear.

### Ready beads that are already complete

- **`kernel-of-truth-1np7` — close as DONE.** `knull-v2` has run, is FROZEN, and has a registered `NULL` verdict. The old verdict-registration blocker was repaired by the stdin adapter and correction record.

- **`kernel-of-truth-zc6l` — close as DONE.** The truthstyle three-judge campaign completed; `truthstyle-2x2` is FROZEN and has a registered PASS verdict. The associated blocked run and interpretation beads should also be reconciled.

- **`kernel-of-truth-cpnz` — close as DUPLICATE/DONE.** The UFO harness, corpus, fixtures and Modal wrapper were already built under the completed build bead; the experiment subsequently ran.

- **`kernel-of-truth-dpog` — close as DONE.** `ufo-check-0` is FROZEN with a registered `INSTRUMENT-INVALID` verdict. Repeating coordinator freeze/run steps would duplicate landed work.

- **`kernel-of-truth-utq` — close the principal deliverable as DONE.** The resource-usage plan exists and the issue notes say all components except the deliberately deferred logged-result-reuse feature are complete. If that deferred feature is ever revived, it should be a separate conditional bead.

- **`kernel-of-truth-hgbh` — close as RESOLVED.** The missing-freeze/stale-pin defect was resolved: `g2-import-v2` is now FROZEN and indexed.

- **`kernel-of-truth-p3z0` — close as DONE-WITH-INVALID-PILOT.** The hardened Stage-P pilot was rerun; its realized AC1 was 0.6222, below 0.65. Any v2.2 successor is new work, not another execution of this bead.

- **`kernel-of-truth-dt3w` — close as DONE.** Both `l3a-parse` and `a5-nl` are FROZEN and have registered FAIL verdicts.

- **`kernel-of-truth-6ky`, `kernel-of-truth-7qc`, `kernel-of-truth-wve` — close as obsolete E2 launch paths.** A full Modal E2 result exists and its registered primary was met in all three model families. These are alternative launch mechanisms for work already performed.

- **`kernel-of-truth-b6z`, `kernel-of-truth-ygx`, `kernel-of-truth-0r1` — close as DONE/SUPERSEDED.** The E1/E4 full campaign ran. E1 was inconclusive and E4 had no registered kernel advantage; pre-launch optimization and launch beads should not remain ready.

- **`kernel-of-truth-dn7` — close as prospectively superseded.** It requested a design decision before the E4 run, but the run has already occurred without replay interleaving. Any renewed replay experiment would require a new record.

- **`kernel-of-truth-dyg` — close as condition not triggered.** It authorized second-family replication only if E4 passed with its control at floor; E4 did not pass.

### Ready beads superseded by stronger evidence or a newer design

- **`kernel-of-truth-7vv2` and `kernel-of-truth-ifvn` — close/park as superseded.** The DDC I-5 power assessment stopped the design, and the standing decision redirected efficiency work toward GLM routing. Spending the proposed $40–60 would not produce a decisive thesis result.

- **`kernel-of-truth-kwv2` — close as superseded by `kernel-of-truth-8z5o`.** The original S5 design and builder were replaced by DESIGN-v2 and `run_s5.py` v2.

- **`kernel-of-truth-d024` and `kernel-of-truth-zusu` — close as superseded for portfolio purposes.** RULES-2-knull already established the load-bearing attribution fact: the generic dictionary and kernel generate byte-identical training corpora on the closed inventory. A RULES-1-specific repeat may answer a narrow certificate question, but it cannot change the current correctness-thesis attribution and should not consume priority capacity.

### Stale `in_progress` records to reconcile

These were not in the reconstructed ready set, but the requested in-progress audit exposes the same bookkeeping problem:

- **`kernel-of-truth-ak2u`** — Opus Pass-B rejudgment artifacts exist and v8 incorporates the conclusion.
- **`kernel-of-truth-d1s5`** — build complete; offline self-test is 46/46. Close the build bead; execution remains `8z5o`.
- **`kernel-of-truth-jy96`** — AST pipeline and full results exist.
- **`kernel-of-truth-uomb`** — the fresh nsk1-r3 corpus, manifest and resolved count gate exist; retain only the bridge/run work.
- **`kernel-of-truth-sotz`** — its own notes say PREP COMPLETE; remaining blockers belong to separate correction, inventory and backend beads.
- **`kernel-of-truth-e47a`** — the truthstyle campaign subsequently completed and registered a verdict.
- **`kernel-of-truth-ewvh`** — the g2 harness hardening was incorporated before the frozen campaign.
- **`kernel-of-truth-wks1`** — the g9, m0a and g3 proxy records/artifacts were subsequently frozen and run.
- **`kernel-of-truth-3wjn`** — l3a-parse/a5-nl are frozen and have final verdicts.
- **`kernel-of-truth-yuv5`** — its diagnostic/fix path produced RULES-1-b and RULES-1-c; the latter ran and was instrument-invalid. Further work needs a new question, not continuation of the original fix bead.

## 3. Prioritized high-impact feasible work

Global ranking below is by expected information per dollar toward either thesis. “Direct” means the result can bear directly on a thesis, although I explicitly note when it still falls short of the full four-condition standard.

### A. Direct or near-direct thesis discriminators

#### Rank 3 — Run the nsk1-r3 bridge and, only if it passes, the frozen r3 campaign

- **What:** **[MEASURED PLAN]** Execute the 200-item same-item surface bridge at \(C1=(16,16)\); if synthetic key delivery clears the registered threshold, freeze and run r3 on the already-built fresh corpus.
- **Thesis/impact:** **[ASSESSMENT — CORRECTNESS, mechanism-side]** This tests whether the strong B″ delivery result—0.850 key accuracy, lower bound 0.775—survives the required surface change. It does not establish kernel-versus-generic value, but it decisively determines whether delivery remains a live premise for integration experiments.
- **Needs/cost:** **[ESTIMATE]** Bridge expected $0.10–0.35, hard cap $2 and 0.5 GPU-hour; r3 approximately $3. Fable sign-off plus mechanical GPT-5.6 analysis.
- **Dependencies:** Review/land the existing corpus and runner; bridge first. Below 0.75: stop. Between 0.75 and 0.81: re-power or add corpus under a new registration. At least 0.81: proceed.
- **Queue relation:** Extend **`kernel-of-truth-fgbl`** and the existing `nsk1-r3` DRAFT; close/reconcile **`uomb`**.

#### Rank 4 — GSX0: generic plain store × external gold, with a headroom pilot

- **What:** **[ASSESSMENT]** Freeze and run the missing generic-store/external-gold diagonal, but first adjudicate a small blinded headroom sample. Stop if the plain surface is already too easy for the small host.
- **Thesis/impact:** **[ASSESSMENT — CORRECTNESS]** This is the cheapest direct check of whether prior benefits belong to grounded kernel content or merely to authoritative answer-bearing content. It closes a genuine missing comparison, though it is not by itself a fully structure-sensitive four-condition test.
- **Needs/cost:** **[ESTIMATE]** Approximately $1–2 for the pilot; $6–10 expected all-in, $16 pessimistic ceiling; 0.25–0.6 GPU-hour; one to two data/design days and bounded adjudication.
- **Dependencies:** Select and freeze the generic store, define external-gold scoring, pin a non-vacuous headroom gate, and require identical item skeletons across store conditions.
- **Queue relation:** **NEW bead.** The design and analysis adapter already exist, but no registry record or execution bead does.

#### Rank 8 — Matched-quality small-host verifier-offload successor to F2B

- **What:** **[ASSESSMENT]** Pre-register one retry/offload budget selected on development data, then compare 135M+kernel checker, 135M+matched-plain checker, 135M without checker, and the 1.7B reference on held-out external gold. Match realized host, verifier and retry compute—not nominal \(k\).
- **Thesis/impact:** **[ASSESSMENT — EFFICIENCY]** This directly distinguishes kernel-specific verifier offload from generic authoritative-content offload and asks the correct endpoint: quality noninferiority at lower realized cost. It is a valid successor because fixed \(k=4\) already failed; it must not be an exploratory sweep followed by reporting the best \(k\).
- **Needs/cost:** **[ESTIMATE]** Two to three design/data days, approximately 2–6 Modal GPU-hours and $10–30, plus GPT-5.6 analysis.
- **Dependencies:** GSX0 must first produce a valid generic external-gold arm; use a development split to select a single budget; demonstrate that kernel and plain stores are not byte- or answer-equivalent; freeze the structure-sensitive endpoint before test evaluation.
- **Queue relation:** **NEW successor bead**, explicitly extending the registered negative evidence from `f2b-transfer`.

### B. Cheap, high-information enabling work

#### Rank 1 — Finish the R4 cumulative-statistics correction

- **What:** **[MEASURED PLAN]** Land the clean per-prompt fingerprint extraction, contamination note and v3 analysis; register the missing permutation construction; decide whether the frozen \(x_f\) input must be replaced or merely quarantined.
- **Thesis/impact:** **[ASSESSMENT — EFFICIENCY]** Every future routing estimate depends on knowing which observations are independent rather than repeated cumulative snapshots. This is the highest information-per-dollar cleanup because it can materially change effective sample size without new compute.
- **Needs/cost:** **[ESTIMATE]** $0 GPU; less than one analysis day plus a short independent review.
- **Dependencies:** None beyond reviewing the already-built correction artifacts.
- **Queue relation:** Extend **`kernel-of-truth-xafk`**; do not create a duplicate correction bead.

#### Rank 2 — Model-free F1-K askability and coverage screen

- **What:** **[ASSESSMENT]** Before authoring more definitions or launching a model, construct an outcome-blind candidate list targeting 96 concepts, require 80–100 reviewable concepts, materialize the kernel and matched-dictionary artifacts, verify that their bytes and prompts differ, and recompute cluster-aware power for K-1/K-2/K-3.
- **Thesis/impact:** **[ASSESSMENT — CORRECTNESS]** This determines whether a four-condition correctness experiment is even askable. It directly addresses the current failure—46 eligible clusters versus 65 required—and prevents another expensive content-collapse result.
- **Needs/cost:** **[ESTIMATE]** $0 GPU; roughly one to two data-build days and one Fable design review for the screen. Full explication authoring is deliberately excluded at this stage.
- **Dependencies:** Existing benchmark text, WordNet candidate pool and F1-K corpora. The screen must be blind to model outcomes and gold labels.
- **Queue relation:** Extend and supersede the current scope of **`kernel-of-truth-lyvi`**. Stop if fewer than 80 valid, genuinely contrasting concepts are available.

#### Rank 5 — Cluster-aware R4 inference and prospective re-probe design

- **What:** **[ASSESSMENT]** Recompute an honest interval/equivalence analysis over the eight independent clusters, then prospectively simulate the number of concepts and prompt traces needed to distinguish a 10-point routing gain from a small 2–3-point gain. Specify randomized run order and per-prompt statistics.
- **Thesis/impact:** **[ASSESSMENT — EFFICIENCY]** This tells the programme whether R4’s +2.6% estimate is compatible with a verdict-relevant effect and how much genuinely independent data—not more cumulative cells—is needed.
- **Needs/cost:** **[ESTIMATE]** $0–2 compute, one analysis day, independent GPT-5.6 review.
- **Dependencies:** Final clean inputs from `xafk`.
- **Queue relation:** **NEW bead.** It follows `xafk`; it is not part of the mechanical contamination repair.

#### Rank 6 — Non-AWS GLM backend feasibility gate

- **What:** **[ASSESSMENT]** Audit whether the pinned checkpoint, approximately 370 GB of weights, expert-streaming implementation, per-prompt statistics and storage semantics can run reproducibly on an allowed non-AWS backend. Only after a paper/configuration PASS should one prompt be executed end to end.
- **Thesis/impact:** **[ASSESSMENT — EFFICIENCY]** This prevents the portfolio from treating GLM-DROP as executable when its current design assumes AWS CPU/NVMe streaming. A negative result cheaply redirects effort to the small-host offload route.
- **Needs/cost:** **[ESTIMATE]** $0 for the configuration audit; $5–20 for a one-prompt smoke only if the audit passes; roughly one infrastructure-agent day.
- **Dependencies:** None for the audit. The smoke requires demonstrable access to the exact weights and sufficient storage/memory.
- **Queue relation:** **NEW bead.** Do not reopen `sotz`; that bead completed registry/analysis preparation, not backend portability.

#### Rank 7 — S5-v2 bridge repair and n=24 pilot only

- **What:** **[MEASURED PLAN]** Review and freeze the 31 bridge records, land the completed v2 runner, then execute only the 24-concept matched four-cell pilot. Apply the registered futility rule before considering the n=200 campaign.
- **Thesis/impact:** **[ASSESSMENT — CORRECTNESS enabler]** This tests whether molecule-ensemble construction improves AST/explication quality enough to justify inventory work. The previous oracle-selected 16/24 ceiling was not deployable, so another broad generation sweep without the pilot would have little value.
- **Needs/cost:** **[ESTIMATE]** Approximately $10–30 for the pilot and one to two Fable/analysis days. The full proxy campaign is estimated at $90–260 and is not authorized by this recommendation.
- **Dependencies:** Reconcile `d1s5`, adjudicate the bridge records without benchmark outcomes, freeze the judging package, and keep a human-rejudge kit.
- **Queue relation:** Narrow/extend **`kernel-of-truth-8z5o`** to pilot-first; close **`kwv2`**.

#### Rank 9 — Adopt v8 as an enforceable pre-spend readiness ledger

- **What:** **[ASSESSMENT]** For every proposed thesis experiment, record four explicit states—instrument validity, power, matched-generic distinctness, and structure sensitivity—plus an executable-backend state and effective independent-unit count.
- **Thesis/impact:** **[ASSESSMENT — BOTH]** This does not create scientific evidence, but it prevents invalid or underpowered launches from competing with the few paths capable of changing a verdict.
- **Needs/cost:** **[ESTIMATE]** $0; less than half a coordinator/analysis day.
- **Dependencies:** None.
- **Queue relation:** Extend **`kernel-of-truth-5q2e`**, including the stale-bead reconciliation above.

### Work that cannot currently be made valid

- **[MEASURED] Current F1-K launch:** invalid at the registered power gate—46 eligible clusters versus 65 required. Do not waive the gate or count prompts as independent concepts.

- **[ASSESSMENT] Full F1-K successor:** potentially decisive, but not currently executable as a valid result. It requires 80–100 reviewed concepts, approximately 20–35 hours of actual human semantic review, five to ten Fable authoring days, and a working GLM backend. Fable/GPT proxy review cannot substitute for the human validity gate.

- **[MEASURED] Current GLM-DROP launch:** only eight routing clusters, low power, unresolved R4 contamination amendments, and an AWS-specific backend. The old $56–78/$95 estimates do not transfer to the allowed infrastructure.

- **[ASSESSMENT] Full S5 n=200 proxy campaign:** do not run merely because the runner exists. Proxy judgments cannot enter the validated inventory without prospective human adjudication; the n=24 futility pilot should come first.

- **[MEASURED] DDC launch:** stopped by its own power gate and superseded by the GLM decision path.

- **[MEASURED] CASC rerun solely to repair TTC:** not useful. Even if TTC were fixed, the separation gate remains invalid and the observed attribution contrast is already near zero.

- **[MEASURED] Further UFO or RULES-1 knull repetitions:** cannot repair the decisive attribution problem already exposed by DECONF-B and RULES-2’s identity results.

- **[MEASURED] A-F0 through a CLI substitute:** invalid under the frozen pipeline identity because the required direct API/cache accounting is unavailable. Park `l5yq` unless the exact transport is provisioned.

- **[MEASURED] Human-review beads under agent-only resources:** `6f9f`, `r7i`, and related human-gold work require real human allocation. In particular, the E4 review bead requiring sampling before unblinding can no longer be satisfied prospectively; a replacement would need a newly sampled, prospectively blinded record.

## 4. Parallelism map

### Can start independently now

- **Analysis lane:** `xafk` contamination correction.
- **Data-build lane:** F1-K model-free askability/coverage screen.
- **GPU lane 1:** nsk1-r3 surface bridge.
- **Design/data lane:** GSX0 headroom package and registry design.
- **Design lane:** S5 bridge-record review and pilot freeze preparation.
- **Infrastructure lane:** non-AWS GLM feasibility audit.
- **Coordinator lane:** v8 readiness-ledger adoption and stale-bead reconciliation.

**[ASSESSMENT]** These activities do not share outcome data and can run concurrently. After their respective freeze checks, the nsk bridge and GSX0 pilot can also use separate GPU accounts concurrently.

### Partially parallel, then serialized

```text
xafk correction
    └── clean R4 cluster analysis and power design
            └── expanded trace re-probe
                    └── re-powered GLM-DROP

F1-K askability screen
    └── candidate explications and AST construction
            └── real human semantic validation
                    └── F1-K freeze
                            └── correctness main run

S5 bridge review
    └── S5 n=24 pilot
            └── only if pilot passes: human validation capacity
                    └── optional larger inventory campaign

nsk corpus already built
    └── surface bridge
            └── bridge threshold decision
                    └── nsk1-r3 freeze and run

GSX0 design and headroom pilot
    └── GSX0 full run
            └── matched-quality verifier-offload successor

non-AWS backend audit
    └── one-prompt smoke
            └── expanded R4/GLM work only if executable
```

**[ASSESSMENT]** The critical correctness path is currently serialized behind inventory distinctness and human validity, not GPU availability. The critical efficiency path is serialized behind clean cluster inference and backend feasibility, not the nominal cost of the main run. Those are the two portfolio constraints that should determine scheduling.