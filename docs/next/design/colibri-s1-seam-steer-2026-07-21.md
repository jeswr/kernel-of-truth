# colibri → S1-seam steer (coordinator synthesis of a dual-model design read)

**2026-07-21. Coordinator synthesis of TWO independent, blind labelled design opinions** (Fable via SDK #4; GPT-5.6 `gpt-5.6-sol` xhigh via the review runner) on what the colibri recon (`reports/colibri-recon-2026-07-21.md`) means for the S1 (MoE routing/pruning) shrink thesis. Per the dual-model-analysis discipline: these are labelled opinions, never overriding a mechanical verdict; the coordinator synthesises, and the material call is surfaced as a GitHub issue. Verbatim steers appended below.

## Where the two models AGREE (high-confidence steer)
1. **Naive expert-count reduction is dead as a *kernel* value proposition.** Both. The measured `EXPERT_BUDGET` collapse (cap=8 → HellaSwag 30% vs 90%; MTP acceptance 56%→0%) is decisive against raw top-k / static-skiplist *count reduction* as a kernel selling point.
2. **Seam ranking is IDENTICAL and unanimous: (b) S3 grounding-checker > (a) S1 skiplist > (c) S2 drafter.** The `gr_admissible`→hard-sampler-mask grounding-checker is the only seam where the kernel is **load-bearing by design**, and it is the best-conditioned bet on every measured axis: regime-independent (survives full RAM residency, unlike S1/S2), model-agnostic (survives colibri's Kimi-K3/DeepSeek-V4 pivot — grammar/sampler machinery is model-independent, expert atlases are not), and net-new/unowned. It also aligns with the programme's already-banked cross-read conclusion that the kernel's home is the output/logits seam (Logic-LM +39.2% analogue).
3. **A probe is worth running, and it is NOT a redundant re-run of colibri's cliff** — because uniform TOPK truncation is a *different lever* than the quarantined dynamic miss-aware cap.

## The load-bearing nuance (Fable, grounded in our frozen designs)
- colibri's cliff is the **dynamic, miss-aware distinct-expert cap** (forced redirection of out-of-budget picks to loaded experts) = a REAP-Thm-1 merge-to-constant that collapses ∝ Var[r(x)]·expert-gap; GLM's near-orthogonal experts maximise the gap. **Static saliency-scored removal behaves completely differently** (92.6% retention at 50% removal on GLM-4.5-Air with conditional-impact scoring, vs 0.011 under frequency scoring). *The entire spread between collapse and near-losslessness lives in the selection policy* — which is exactly where a kernel-informed ranking still has a defined job. So **S1 is narrowed + bar-raised, not closed**: the surviving hypothesis is the programme's existing **E-GLM/GLM-DROP** conjunction (a static, SPEC_PIN-consistent kernel-concept mask that must strictly beat uniform-TOPK / frequency / embedding-cluster / deranged-label controls at matched load), and colibri measured *none* of it.
- Honestly-tagged damage: the concept→expert mapping premise is weakened (only 7.9% strong specialists; routing tracks token-identity not topics) → modal outcome of kernel-mask-vs-controls stays a **tie** (as the design already banked); and "shrink" is mis-priced (at fixed k, retiring experts cuts union/cache footprint, not per-token bytes) → S1 value is **regime-gated to disk-streaming** = a residency/placement + footprint claim, not a per-token-compute claim. New hard constraint: any expert-firing change must be applied identically in draft+verify (the 56%→0% MTP datum) — dynamic per-token masking is now architecturally disfavoured.
- **Dimension-collapse (DDC) is orthogonal and untouched** (feature/width axis vs expert-count axis; no mechanistic transfer). Only cross-read is rhetorical: both axes now carry a measured warning that *naive* training-free shrinking of this model family collapses.

## Reconciling the probe question (they differ only in framing)
- **GPT-5.6** wants the kill-shot: a ranked-ablation curve measuring max removable expert-param fraction under fixed quality + MTP gates, kernel ranking vs frequency/Atlas/random. That is effectively the **powered E-GLM/GLM-DROP experiment** itself.
- **Fable** wants the cheap gate FIRST: the config-only `--topk {8,6,4}` sweep (MTP on AND off) prices E-GLM's binding null-hypothesis control arm (uniform TOPK at matched load) before any powered spend. If TOPK=6/4 retains near-full quality → count-reduction is a free kernel-free lever, kernel headroom ≈ 0 → **do not fund** the GLM-DROP power repair (~$56–95). If there is a cliff → selection policy demonstrably carries value → **green-light** the repair.
- **Synthesis: they are the same pipeline at two stages.** Cheap TOPK gate (Fable) → if a cliff exists → the powered kernel-vs-baselines ablation (GPT-5.6) behind the ≥65-cluster power repair. Fable's sequencing is the cost-disciplined ordering; adopt it.

## Steering implications (coordinator; decisions flagged)
- **Elevate the S3 grounding-checker to the top kernel-leverage seam.** [DESIGN DECISION → Fable design-scoping + maintainer buy-in.] This is the higher-value redirect than the S1 probe. Caveat carried from the prior cross-read: the checker claim needs its own priced falsifier vs a kernel-as-text control before its "home" status is banked.
- **S1 → second-priority selection-policy track**, gated by the cheap TOPK probe. [MECHANICAL, but needs a fresh GPU box + GLM-5.2 weight fetch — the eu-west-2 i4i.2xlarge probe box is terminated.]
- Nothing here changes DDC's own parked status.

---

## Verbatim — Fable steer (SDK #4)

# DESIGN STEER — colibri recon vs the S1 shrink thesis

**LABELLED DESIGN OPINION (Fable, architectural read, 2026-07-21). May be wrong; never overrides a mechanical verdict. No files edited, no ASM ids minted.**

## 1. S1 thesis call + sharpest falsifiable hypothesis

**Call: the naive expert-count-reduction framing is dead as a kernel value proposition — but colibri's cliff kills a *different lever* than the one our frozen-design pipeline actually bets on, so the S1 seam is narrowed, not closed. The surviving S1 value is selection/placement policy, and the programme already holds the sharpest form of that hypothesis (E-GLM). colibri's evidence raises its bar and constrains its implementation; it does not answer it.**

The load-bearing distinction: `EXPERT_BUDGET` is a **dynamic, miss-aware distinct-expert cap** — when a token's router pick isn't in budget, it is forcibly redirected to a loaded expert. That is a merge-to-constant-flavored substitution of r(x), exactly the mechanism REAP Thm-1 predicts collapses ([LIT-BACKED] REAP 2510.13999; functional-subspace collapse ∝ Var[r(x)]·expert-gap; GLM's near-orthogonal experts maximize the gap). colibri measuring it collapse (budget=8 → HellaSwag 30% vs 90%; MTP 56%→0%; budget=4 → noise [MEASURED, colibri, quarantine at glm.c:6297]) is a *confirmation of the literature's prediction on our exact model family*, not a novel negative about pruning per se. Static saliency-scored removal is measured to behave completely differently: 92.6% retention at 50% removal on GLM-4.5-Air with conditional-impact scoring, vs 0.011 collapse under frequency scoring ([LIT-BACKED], same source, full-text verified). **The entire spread between collapse and near-losslessness lives in the selection policy.** That is the one reading under which a kernel-informed ranking still has a defined job.

What the recon *does* damage, honestly tagged:

- **The concept→expert mapping premise is weakened.** Expert Atlas: only 7.9% strong specialists, leave-one-out 96.7% [MEASURED, colibri]. Combined with the programme's own prior — routing tracks token identity/syntax, not topics ([LIT-BACKED] Mixtral routing analysis); our probe's 93.92% universal-mass concentration [MEASURED, programme] — a concept-keyed importance ranking is betting on structure that ~92% of experts measurably don't have. The honest modal outcome of kernel-mask-vs-controls stays a **tie**, as the design menu already banked.
- **The "shrink" framing itself mis-prices the win.** At fixed k, retiring experts does not reduce per-token bytes streamed — only union size/cache hit-rate — on a box measured disk-bound at ~11.4 GB/token ([MEASURED] northstar §1.2 + menu critique arithmetic). And both S2 speculation and CACHE_ROUTE neutralize at full RAM residency ([MEASURED] colibri #472). So S1 value is regime-gated to disk-streaming and is really a **residency/placement** claim (which experts to pin — `hit_pin`/`hit_ecache` now instrument this directly), plus a footprint claim (union cut), not a per-token compute claim.
- **New hard constraint:** any lever changing which experts fire must be applied identically in draft+verify or it zeroes MTP acceptance ([MEASURED, colibri] — the 56%→0% datum). A kernel mask must be static and SPEC_PIN-consistent; dynamic per-token masking is architecturally disfavored now, not just risky.

**Sharpest falsifiable S1 hypothesis still worth an experiment** — it is the already-designed E-GLM conjunction (GLM-DROP), sharpened by this evidence:

> *A frozen, static, training-free kernel-concept expert mask, applied identically in draft and verify, achieves ≥40% fewer realized expert loads while (i) staying within −4.0 pts non-inferiority of full TOPK=8 on cluster-balanced accuracy and (ii) strictly beating uniform TOPK truncation, pooled-frequency retention, matched embedding-cluster retention, and dose-exact deranged-label masks at the same realized load.* [Registered design: efficiency-thesis-path §1, GLM-DROP arms]

Nothing colibri measured tests this: they measured a dynamic cap (collapses) and offer uniform TOPK (a control arm, not the hypothesis). The kernel-specific increment over the embedding-conditioned control remains unmeasured anywhere. It remains runnable only after the no-spend power repair (≥65 clusters; current C=8 power 0.119 at +3 [MEASURED, power record]) — that gate is untouched by this recon.

**Dimension-collapse relation: orthogonal, untouched.** DDC shrinks the *feature/width* axis (matched packed bytes at reduced hidden dimension); EXPERT_BUDGET/TOPK/skiplist shrink the *expert-count* axis. No mechanistic transfer in either direction — colibri's cliff says nothing about whether kernel-guided subspace selection preserves quality at matched packed parameters. DDC stays parked on its own failed I-5 power gate ([MEASURED] mechanical record), for its own reasons. The only legitimate cross-read is rhetorical discipline: both axes now carry a measured warning that *naive* training-free shrinking of this model family collapses, so neither track may borrow optimism from the other. [STIPULATED — orthogonality is an analysis claim, not a measurement.]

## 2. Ranked seam recommendation

**Rank 1 — (b) `gr_admissible` → hard sampler logit mask (S3 grounding-checker).** The only seam where the kernel is load-bearing *by design* rather than decorative. It aligns with the programme's strongest published analogue (Logic-LM +39.2% [LIT-BACKED]) and with the dual-model cross-read's banked conclusion that the kernel's honest home is the output/logits seam. Architecturally it is the best-conditioned bet on every measured axis: regime-independent (correctness value survives full RAM residency, unlike S1/S2 [MEASURED, colibri #472]); model-agnostic (survives colibri's Kimi-K3/DeepSeek-V4 pivot — grammar/sampler machinery is model-independent, expert atlases are not); net-new and unowned (colibri has neither built nor rejected it, and has live unowned quality defects it would target — reasoning loops #455, tool-output validation #401). One discipline carried over from the cross-read: the checker claim needs its own priced falsifier vs kernel-as-text before "home" is banked — migrate the test, not the optimism.

**Rank 2 — (a) per-expert-ID skiplist in `moe()`.** High value **as the enabling instrument for E-GLM**, low expected value as a standalone kernel proposition. It is the ~10-line mechanism the frozen GLM-DROP design needs to exist at all (static eid filter, applied pre-FASE-C so the disk load is skipped, SPEC_PIN-consistent — the recon confirms the plug-in point is clean and eid-keyed throughout). But the *kernel-specific* payoff prior is weak: 7.9% specialists [MEASURED], modal-tie prior from the programme's 0-for-5 runtime-judgment ledger [MEASURED, programme record], and value gated to the disk-streaming regime. Build it when GLM-DROP clears its power gate; do not sell it as a thesis before then.

**Rank 3 — (c) external kernel drafter (S2).** Weakest by a distance. A drafter must emit token sequences; the concept kernel is not a generative model, so a "kernel drafter" reduces either to grammar/engine-forced spans — which is Rank 1's correctness play delivered through the draft channel, already shipped as `grammar_draft()` — or to a net-new small LM, which is not our thesis. Compounding negatives: speculation measurably *loses* at full residency ([MEASURED] #472), MTP is off in serve (#358/#492), no logprobs/draft-submission surface exists, and GLM's native MTP head already occupies the interior-drafter niche at 2.2–2.8 tok/forward. Nothing here needs a concept kernel.

## 3. Single probe to run next

**Run [2] — the `--topk {8,6,4}` shrink sweep. colibri's measurement does NOT make it redundant.** Three reasons, in decision order:

1. **Different lever, non-transferable cliff.** The measured collapse is the miss-aware dynamic cap; uniform TOPK truncation keeps the router's own top-k ranking with no forced redirection. The cliff shape cannot be assumed to transfer across mechanisms — that assumption would be exactly the [EXTRAPOLATION]-as-premise this programme forbids. colibri has no published TOPK quality curve; and their numbers are not on our int4/hardware/bench config regardless.
2. **It prices the null-hypothesis frontier for the sharpest S1 hypothesis.** E-GLM's binding comparator is uniform TOPK *at matched load* — the kernel earns a sentence only by beating that exact arm. If TOPK=6/4 retains near-full quality (as the preliminary P0 1.9×/2.5× observations hint [MEASURED, qualified — cache-confounded]), count reduction is a free kernel-free lever and the kernel-mask headroom is capped near zero → deprioritize the GLM-DROP power repair *before* its $56–95 spend. If there is a cliff, selection policy demonstrably carries value → green-light the repair. Either outcome is decision-bearing; no other probe forecloses or funds the S1 experiment this directly.
3. **Cheapest per bit.** Config-only, sanctioned path (`--policy experimental-fast`), quality + `RSS_GUARD_GB` + tok/s in one pass. Probe [1] (STATS/LOOKA refresh) is genuinely needed later — the concept→expert fingerprints must be rebuilt on v1.0.0 for the power repair anyway — but it is an *input-construction* step, not a decision gate, and is worthless spend if [2] shows no headroom. [3] is secondary (regime-gated placement characterization; expected neutral at full residency [MEASURED]); [4] is S2, orthogonal to the S1 hypothesis.

**Sequencing note for the coordinator:** run [2] with MTP on and off — the draft-verify expert-union interaction is the measured constraint (56%→0%) that DRAFT=0 probes deliberately hide, and it is the deployment-relevant half of the tradeoff curve.

---

*Compact summary for synthesis: (1) [OPINION on MEASURED+LIT-BACKED evidence] naive count-reduction is dead as a kernel proposition; S1 survives only as static selection/placement policy, sharpest hypothesis = the existing E-GLM conjunction with a SPEC_PIN-consistent static mask; dimension-collapse is orthogonal and untouched. (2) Seam ranking: (b) hard sampler mask > (a) skiplist-as-instrument > (c) external drafter. (3) Next probe: [2] TOPK sweep — not redundant; different lever from the quarantined one, and it prices E-GLM's binding control arm before any powered spend.*

---

## Verbatim — GPT-5.6 steer (`gpt-5.6-sol`, xhigh)

Bottom line: the evidence materially downgrades S1 as a parameter-shrink seam. It does not kill S1, but redirects it toward disk-working-set optimization.

1. S1 assessment

Stop treating naive top-k reduction or a static skiplist as the plan. The collapse reported in [colibri-recon-2026-07-21.md](/home/ec2-user/css/kernel/kernel-of-truth/reports/colibri-recon-2026-07-21.md) is too severe to dismiss as tuning. Also, “only 7.9% strong specialists” does not imply the other 92.1% are redundant; they may implement distributed general computation.

The safer direction is router-preserving placement—kernel-informed pinning, prefetch, or eviction—which can reduce disk traffic without changing model semantics or speculative acceptance. But that is a streaming optimization, not genuine model shrink, and disappears at full RAM residency.

The one remaining shrink hypothesis worth a kill-shot test is:

> A kernel-derived, per-layer ranking can remove at least 10% of expert parameters, while refilling the native top-k from remaining experts and applying the same mask in draft and verification, with ≤1 percentage point mean benchmark loss and ≤5 points absolute MTP-acceptance loss—and outperforming frequency/Atlas-based rankings.

If that fails, stop positioning S1 as kernel-enabled model shrink.

2. Ranking of integration points

1. **Hard grammar/sampler constraint.** Strongest direct quality leverage, provided kernel facts can be compiled into closed-world admissibility constraints—for example valid entities, relations, IDs, or tool arguments. It guarantees structural or enumerated consistency, not general factual truth; unrestricted prose grounding would need a semantic checker beyond GBNF.

2. **Kernel-ranked expert skiplist.** High upside if the hypothesis succeeds, but a weak prior after the pruning cliff. Expert IDs are not clean concept slots, and a static global ranking is especially suspect.

3. **External speculative drafter.** Weakest knowledge leverage. The verifier tests whether the target model accepts the exact tokens, not whether they are grounded. Lossless speculation therefore changes speed, not correctness; acceptance also depends on surface-form prediction and its benefit is disk-streaming-specific.

3. Next measurement

Do not repeat the naive TOPK/`EXPERT_BUDGET` cliff.

Measure one scalar: **the maximum expert-parameter fraction removable under fixed quality and MTP-acceptance gates**. Produce a ranked-ablation curve for the kernel ranking versus matched frequency/Atlas and random rankings, with native top-k refilled and identical draft/verify masks.

That experiment distinguishes “kernel contains useful expert-importance signal” from “pruning is merely destructive.” A cache benchmark can follow, but it would validate I/O optimization—not the programme’s shrink thesis.
