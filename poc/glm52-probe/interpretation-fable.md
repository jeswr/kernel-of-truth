# GLM-5.2 P0 probe — Fable steering interpretation

> **Status: STEERING INTERPRETATION (labelled opinion). Not a feasibility verdict —
> verdicts belong to verdict-gen. To be reconciled against the GPT-5.6 read.**
> Author: Fable, interpretation role, 2026-07-12.
> Inputs: `results/probe-main.log`, `results/routing-analysis.json`, `results/stats/`
> (24 fingerprints + manifest), `concept_prompts.json`, `analyze_routing.py`,
> `docs/next/design/glm52-followup-experiment.md` (F1), `glm52-kernel-integration-northstar.md`.
>
> **Verification-preview note.** The re-analysis numbers marked *preview* below were
> computed by this interpretation agent from the COMMITTED fingerprints only (CPU,
> seed 20260712, no instance, no new measurement) to test whether a sharper re-analysis
> changes the read. They are NOT the mechanical record; §2 specifies the exact runs the
> coordinator must reproduce and commit before anything downstream consumes them.

---

## 0. Headline

The probe's most consequential output is not a number in the log — it is a defect in
the analysis script. The reported p = 0.33 for concept→routing structure is an
artifact of a degenerate permutation scheme, not a property of the data
[DERIVED, §1.2]. Under the pre-registered test form (≥10,000 random label shuffles,
ASM-2013), the same committed data yields p ≈ 0.0001 (*preview*), and a
mean-centred similarity metric shows near-total concept separation (within 0.91 vs
across −0.07) with all four registered sense minimal-pairs separating in the
predicted direction [MEASURED: preview, §1.2]. The routing signal is real and was
buried twice over — once by a floored test, once by a universal routing component
carrying ~94% of histogram mass. Meanwhile the TOPK sweep shows a genuine,
kernel-free speed lever (1.9× at topk=4) that raises the deflator bar for B1b
without touching its mechanism. The branch call should be HELD pending the §2
re-analysis being run through the coordinator's mechanical pathway plus the missing
M_oracle/M_kernel replay; F1-K is unaffected throughout.

---

## 1. Subjective read, per thesis

### 1.1 Efficiency thesis — the TOPK shrink sweep

[MEASURED: probe-main.log P4] Uniform topk 8→6→4→2 gives 0.10→0.12→0.19→0.25 tok/s
(1.9× at topk=4, 2.5× at topk=2), expert-loads/token 1786→1596→999→606, on a box
where expert-disk is ~75–80% of decode wall-time and the Amdahl ceiling is 5×
[MEASURED: P1/P1b; DERIVED: ASM-2012].

[ASSESSMENT] Yes, uniform expert-drop is already a real speed/quality lever at this
scale: nearly half the baseline expert I/O sits in the router's low-weight tail and
can be skipped for ~2× wall-clock. But the quality evidence is thinner than the
headline suggests: the sky-blue answer stayed correct and coherent down to topk=4
[MEASURED: P4], while the factual-retention check is n=2 and mixed — at topk=8 the
France prompt answered "Paris."; at topk=4 it emitted "The capital of France" (an
echo, not an answer) within its tiny token budget [MEASURED: P4]. That is too little
generation to call a regression, but it is NOT quality-neutrality either. The honest
summary: speed effect solid, quality effect unbounded, n=2.

What this does to kernel-guided B1b (drop concept-redundant experts): **both
directions at once**, and the design should absorb both.

- **More promising on mechanism** [ASSESSMENT]: the sweep proves the exact physics
  B1b exploits — most loaded experts per token are droppable at modest visible cost,
  and expert-loads are the bottleneck. B1b's additional offer over TOPK is real:
  a *static, concept-profiled* drop shrinks the disk estate itself (f × 370 GB) and
  is workload-persistent, which a per-token TOPK knob cannot do.
- **Harder to license** [ASSESSMENT]: a trivially simple, kernel-free, zero-analysis
  knob already banks 1.9×. B1b's deflator set must therefore include
  **uniform-TOPK-at-matched-expert-loads** as an explicit control arm; a
  concept-guided drop that merely matches topk=4's speed/quality point has earned no
  kernel sentence. This is a design-amendment note for B1b's future prereg (B1b is
  gated behind B1a's outcome anyway, ASM-2010; nothing fires now).

Also for the record [MEASURED: P2]: the LOOKA routing-predictability instrument
returned `0.0% (0/0)` — no counters recorded. Routing lookahead predictability is
UNMEASURED, not negative. Flag as an instrument fix for any probe re-run.

### 1.2 Correctness/routing thesis — the concept→routing signal

**Read: real-but-buried — and buried by the instrument, not by the model.**

Two independent burial mechanisms, both demonstrable from committed bytes:

1. **The permutation test was degenerate** [DERIVED; MEASURED: preview]. The
   manifest orders the 24 prompts in contiguous blocks of 3 per concept, and
   `analyze_routing.py` permutes labels by cyclic shift only (23 shifts). Every
   shift that is a multiple of 3 maps blocks to blocks, preserving the
   within/across pair partition EXACTLY — verified: all 7 such shifts tie the
   observed statistic at 0.043174. The minimum achievable p is therefore
   8/24 = 0.333, which is precisely the value reported. Read correctly, the logged
   result is the *strongest outcome this scheme can express*: all 16 informative
   relabelings scored strictly below the true labelling. ASM-2013 registers
   p_perm as "≥10,000 label shuffles"; the script's 23 cyclic shifts are a
   deviation from the registered form. Restoring the registered test on the same
   similarity matrix gives ge = 0/10,000 → **p ≈ 0.0001** (*preview*).
2. **The metric was dominated by a universal component** [MEASURED: preview].
   10,591 of 16,483 (layer, expert) cells are nonzero in all 24 fingerprints and
   carry ~94% of mean histogram mass — shared chat-template tokens, function words,
   and always-on experts. This compresses raw cosines into [0.95, 1.0], so the raw
   delta +0.043 spans most of the available dynamic range while looking tiny.
   Subtracting the grand-mean fingerprint and re-running cosine gives
   within-concept **0.912** vs across-concept **−0.074** (delta 0.986,
   perm p ≈ 0.0001, *preview*) — near-total separation of concepts in the
   residual routing space.
3. **Sense minimal-pairs separate** [MEASURED: preview]. Under the centred metric
   with proper within-group permutation: break senses delta +0.196, p = 0.0037;
   bank senses delta +0.326 at p = 0.100 — which is the FLOOR for n=6 in two
   groups of 3 (every informative relabeling scored below the true one). All 4
   registered sense-pair comparisons show cross-sense distance > within-sense
   distance (SensePairSep preview = 4/4 = 1.00 ≥ the 0.75 A1 threshold).

[ASSESSMENT] So the concept→routing signal at this scale is not marginal — it is
strong, sense-granular, and was masked by two instrument artifacts. One honest
caveat survives: with 3 prompts per concept sharing content words, "concept
structure" and "topical-lexical structure" are not yet separated — the sense
minimal-pairs (same lexeme, different routing) are evidence against a purely
surface-lexical account, but the clean discriminator is F1-A's surface-disjoint
held-out prompts and, if needed, F1-B.1's paraphrase diagnostic. The routing
structure is at least *context-conditioned at sense granularity*; whether kernel
concept LABELS exploit it beyond kernel-free conditioners (M_kernel) is exactly
what remains unmeasured.

---

## 2. Sharper re-analysis: warranted, specified, before any GPU spend

**Warranted — unambiguously.** It changes the read (p 0.33 → ~1e-4) and it costs
CPU-minutes on committed data. Per delegate-and-reanalyse discipline, the following
should be run by the coordinator as the mechanical record BEFORE any new instance
hour. All inputs exist in `poc/glm52-probe/results/stats/`.

- **R1 (PRIMARY — restores the registered test).** Identical fingerprint loading
  and raw-cosine similarity to `analyze_routing.py`; replace the 23 cyclic shifts
  with 10,000 uniform random permutations of the concept labels (registered form,
  ASM-2013), fixed seed recorded in the output; report one-sided p for
  within−across delta. Also report the degeneracy diagnosis (7/23 shifts
  partition-preserving; floor 0.333) so the original p = 0.33 is superseded on the
  record, not silently replaced. *Expected on preview: p ≈ 1e-4.*
- **R2 (SECONDARY descriptive — the sharper metric).** Centred cosine: subtract
  the grand-mean fingerprint from each L1-normalised fingerprint, cosine on
  residuals; report within/across means, delta, and the same 10,000-shuffle p.
  Label post-hoc-metric/descriptive (it is not the registered similarity). Report
  the universal-component fact (cells common to all 24; ~94% mass) alongside.
  Optional robustness twin: per-layer top-16 expert Jaccard, same permutation —
  confirms the result is not a normalisation artifact.
- **R3 (sense pairs, proper test).** Within-sense-group label permutation (break:
  n=9; bank: n=6, noting its p-floor of 0.10) on raw and centred metrics; compute
  SensePairSep exactly as ASM-2013 defines it (fraction of registered sense-pair
  comparisons with cross-sense distance > within-sense). *Preview: 4/4.*
- **R4 (the missing classifier legs — histogram-level offline replay).** M_oracle
  and M_kernel were never computed (no P0.3 section in the log). Both are
  computable offline from the committed fingerprints: simulate pin sets at the
  matched RAM budget recorded in `stats.tgz` (expert-bytes from the model shard
  sizes): oracle per-prompt pin (top experts by the prompt's own histogram) vs
  global-hot pin (top experts by pooled histogram) → M_oracle; kernel-concept pin
  (train-split concept histograms, held-out prompts) vs the STRONGER of global-hot
  and an embedding-cluster pin (off-the-shelf sentence embedding, CPU) → M_kernel.
  Leave-one-out within concept groups given n=3 per concept; miss-bytes
  approximated as unpinned-expert usage mass × expert bytes; approximation
  (static, no LRU dynamics) stated on the record. If the 24-prompt sample is too
  thin for a stable M_kernel, say so and price a replay-grade re-probe as a
  separate maintainer decision — do not silently extrapolate.

[ASSESSMENT] R1 alone flips the headline; R4 is what actually unblocks the branch
classifier. Both precede any new spend.

---

## 3. Branch determination: HOLD — with a stated lean

[MEASURED] The ASM-2013 classifier needs (M_kernel, p_perm, M_oracle,
SensePairSep). The log supplies a defective p_perm and NO replay quantities; the
classifier cannot legitimately fire on today's record. Mechanically: **hold**.

[ASSESSMENT — the lean, binding on nothing] On the preview evidence the p_perm leg
of Branch A passes decisively (p ≈ 1e-4 under the registered test form), and
SensePairSep previews at 1.00 → sub-case **A1** (sense granularity live). What is
genuinely open is M_kernel ≥ 10% vs the stronger deflator: strong concept-shaped
routing does NOT imply kernel labels beat an embedding-cluster conditioner — this
is precisely the content-not-structure trap that has capped the programme four
times, and topic-clustered embeddings may capture the same structure. So: the
naive reading of the logged numbers ("p = 0.33, no structure → Branch C") is
WRONG and must not be allowed to kill the routing levers; the defensible
provisional read is "Branch A likely on the structure leg, A-vs-B undetermined on
the M_kernel leg." The branch call waits for R1 + R4 through the mechanical
pathway — that is hours of CPU, not a new experiment, so holding costs nothing.

---

## 4. KaE gating implication

[MEASURED: F1 design §1.1, §2.3, ASM-2024/2026] F1-K's gate is G-lex — an
external, harness-side lexical phrase→concept matcher. It does not touch or read
the native router. **Nothing in the routing result — weak, strong, or artifactual —
blocks F1-K.** Its gates remain exactly: MAINTAINER GATE 0 (scoped Law-1 amendment
+ KaE glm.c patch approval) and the n_min = 240 benchmark-coverage gate, both
checkable/preparable without an instance.

**The "piggyback the native router for gating" shortcut (G-route) is NOT
supported.** Plainly: do not do it. [MEASURED: ASM-2026] G-route is admissible
only after a Branch-A classification, which is held (§3). [ASSESSMENT] Even if A
lands after re-analysis, two probe facts count against the shortcut today: the
LOOKA predictability instrument returned no data (0/0), so router-signal
lead-time is unmeasured; and the concept separation lives in the residual space
after removing a ~94%-mass universal component — a gate reading raw router weight
mass would be dominated by exactly that universal component. G-lex stays primary;
G-route stays noted-not-scheduled.

---

## 5. Steer (one paragraph, ranked)

[ASSESSMENT] (1) Run the §2 re-analysis through the coordinator's mechanical
pathway now — R1 (registered 10k-shuffle test), R2/R3 (centred metric + sense
pairs, descriptive), R4 (offline M_oracle/M_kernel replay) — zero instance cost,
and it supersedes the artifactually null p = 0.33 on the record before anyone
quotes it; hold the branch call until it lands. (2) In parallel, proceed with
F1-K preparation that needs no instance and no branch: surface MAINTAINER GATE 0
(Law-1 amendment + patch approval) as a threaded issue, build the trigger map,
and run the MMLU/pool lexical filter to test the n_min = 240 coverage gate —
F1-K is unconditional on routing and remains the primary experiment. (3) When
R1/R4 land, let the ASM-2013 classifier fire mechanically; on the preview
evidence expect Branch A/A1 if M_kernel clears its deflators, Branch B if it does
not — either way the pre-written tree handles it. (4) Record two instrument fixes
for any re-probe (LOOKA 0/0; the token-starved TOPK factual check) and one design
amendment for B1b's future prereg (uniform-TOPK-at-matched-loads deflator arm).
Nothing here moves a thesis verdict; the EFFICIENCY and CORRECTNESS syntheses
remain INCONCLUSIVE-PENDING under their own experiments.
