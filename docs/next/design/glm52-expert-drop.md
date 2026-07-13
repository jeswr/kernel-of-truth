# GLM-DROP (B1b) — kernel-guided GLM-5.2 expert-drop at matched experts-per-token

> **Status: DESIGN ONLY (Programme-3 family, efficiency redirect per issue #27
> option A). Nothing here is frozen, pre-registered, scheduled, or run; no frozen
> record, verdict, encoder pin, or registered assumption is touched; no model run,
> no spend, and no git action occurs in this pass. This document states NO
> feasibility conclusion — it designs the experiment that would produce one.**
> Author: Fable, architecture-design role (designer-8), 2026-07-13.
>
> **Maintainer decision consumed (verbatim, issue #27 comment):** "Proceed with A
> (redirect), with a token underpowered-DDC secondary if you want the SmolLM
> cross-check." — the GLM-5.2 kernel-guided expert-drop (B1b) becomes the primary
> efficiency instrument; DDC's disposition (park vs token secondary) remains the
> coordinator's call and is not decided here.
>
> **Standing cost directive consumed (issue #28 thread, maintainer, verbatim):**
> "Yes that works; please also use similar cost saving measures on other GLM 5.2
> experiments (and other experiments generally if applicable)..." — SPOT i4i
> instances, expert-pinning/warm-cache, and co-location on the KaE (#28) instance
> are baked into this design as requirements, not options (§6).
>
> **ASM block claimed: ASM-2230..2239** (companion file
> `poc/glm52-probe/asm-glm-drop-2230-2239.json`, owner designer-8). Range verified
> free at emission: central register tail in `registry/assumptions.jsonl` is
> ASM-2202; repo-wide grep for `ASM-223[0-9]` empty. Central registration is the
> coordinator's action, with the commit, after the standing GPT-5.6 review gate;
> this pass writes the companion file only and does NOT touch
> `registry/assumptions.jsonl`.
>
> **REVISION 1 (2026-07-13, designer-8, same pass discipline):** the standing
> codex review of this design returned ISSUES on four points: (1) the masked
> deflator arms were not dose-matched (m-emb conditioned on one nearest cluster
> while m-kern may union multiple concepts; m-rand lacked the universal core);
> (2) map coverage was overstated as "~24 concepts" — the probe source is 24
> prompts across **8 concept clusters** (3 prompts/cluster); (3) the quality
> power target (0.90 at a true +3) was unsound under the joint licensing rule
> (p < 0.05 AND observed ≥ +3 has a ~50% power ceiling at true +3); (4) D2
> compared against the accuracy-selected maximum of the deflators instead of
> testing BOTH. All four are fixed in place below, tagged **[R1]**, and
> recorded in §R1. The revision claims **ASM-2290..2293** (companion file
> `poc/glm52-probe/asm-glm-drop-r1-2290-2293.json`, owner designer-8; range
> verified free at emission: central register tail in
> `registry/assumptions.jsonl` is ASM-2259, repo-wide grep for `ASM-229[0-9]`
> empty). The review's OK items — the fixed-compute k\* ±5% matched-loads
> comparison (§4.1), the full-TOPK=8 retention reference (b0-full), and the
> spot/pinning/co-location cost design (§6.1–6.3) — are untouched byte-for-byte.
> The ASM-2230..2239 companion file is left intact as the pre-review record;
> ASM-2232 (m-rand arm), ASM-2235 (power clause), and ASM-2236 (D2 max clause)
> are superseded ON THOSE POINTS by ASM-2290/2292/2293, an amendment the
> coordinator registers centrally with the landing commit as usual.
>
> **Tag convention (house discipline):** `[MEASURED: ref]` = repository bytes or a
> pinned mechanical output read this tick; `[DERIVED]` = arithmetic over tagged
> premises; `[STIPULATED: ASM-id]` = a design choice made here; `[EXTRAPOLATION:
> ASM-id]` = a registered projection, never a premise; `[ASSESSMENT]` = this
> designer's judgment, binding on nothing.
>
> **Inputs read this tick:** `poc/glm52-probe/results/probe-main.log` (sha256
> 77023d2b…2592), `results/routing-analysis.json` (f5d81dbd…7ec6),
> `results/routing-analysis-v2.json` (e9d6813f…57cc, the coordinator-run R1–R3
> mechanical record), `poc/glm52-probe/interpretation-fable.md`,
> `concept_prompts.json`, `docs/next/design/glm52-kernel-integration-northstar.md`
> (§1.2, §2.2, §5.4), `docs/next/design/glm52-followup-experiment.md` (§1.2–1.4,
> §2.7–2.9, §3, ASM-2010/2013/2030/2035/2038/2048), issues #27/#28 with comments.

---

## 0. Plain-language summary (maintainer-facing)

The P0 probe showed that simply telling GLM-5.2's router to use fewer experts per
token (a one-line environment knob, no kernel anywhere) makes the model ~1.9×
faster at 4-of-8 experts and ~2.5× at 2-of-8, with the sampled answer staying
coherent [MEASURED: probe-main.log P4]. That free result is now the bar. This
experiment asks the only question that earns a kernel sentence on the expert-drop
seam: **if we must drop experts, does dropping the ones the kernel's concept map
judges irrelevant preserve more answer quality than dropping uniformly by router
weight — at exactly the same number of experts computed per token — and more than
a kernel-free "importance" ranking (usage frequency / embedding-topic clusters)
would?** If kernel-guided dropping merely ties those controls, the honest reading
is "any sensible drop works," the uniform knob keeps the win, and no kernel claim
is made. The experiment rides the same spot-priced instance as the approved-track
KaE experiment (#28) to amortize cost, and is scored by cheap prefill
loglikelihood on a public-benchmark subset, not by generation. Nothing here
concludes feasibility; both directions of every gate are worded in advance.

---

## 1. Question, hypothesis, and the deflator crux

**Question [STIPULATED: ASM-2232].** At matched experts-computed-per-token k, on
public multiple-choice QA items restricted to kernel-covered concepts, does
restricting GLM-5.2's per-token expert selection to a *kernel-concept-retained*
candidate set preserve more accuracy than (a) the router's own uniform top-k
truncation over all experts, and (b) an equally-sized kernel-free
expert-importance retained set?

**Hypothesis under test (stated, not asserted).** The router's low-weight tail is
droppable (P0 showed that), but *which* survivors matter is workload-dependent;
a concept-conditioned candidate set concentrates the survivors on experts that
carry the concepts the item is actually about, so quality degrades less at the
same compute. The pre-named null: router weight is already a sufficient per-token
relevance signal, and any reasonable mask ties — "any drop works."

**The deflator crux (knull discipline, carried from four prior deflations)
[STIPULATED: ASM-2236].** A kernel sentence is licensed ONLY if the kernel-guided
arm beats BOTH:

1. **uniform-TOPK-drop at matched experts/token** — the zero-analysis, kernel-free
   knob that already banked 1.9× [MEASURED: probe-main.log P4; the explicit
   design-amendment recorded in `interpretation-fable.md` §1.1]; and
2. **the kernel-free expert-importance baselines at the same retained fraction,
   the same per-item dose, and the same k** — pooled usage-frequency retention
   AND a matched-multilabel embedding-topic-cluster conditioned retention,
   EACH in its own named contrast: the kernel arm must beat **both**, never a
   best-of (or accuracy-selected) comparator [R1: ASM-2293]. The ASM-1977
   knull "kernel-guided helps, not any-structured-drop" discipline is carried
   by the dose-exact label-deranged mask m-drng (§3 [R1: ASM-2290]), which is
   a third mandatory D2 leg.

Anything less is reported as "conditioned/any dropping works; the kernel is one
conditioner among several" — the exact shape of the programme's four
content-not-structure deflations, pre-worded in §5.3.

**What this experiment can and cannot feed.** Quality endpoints feed nothing
until verdict-gen's registered pathway runs; efficiency numbers (tok/s,
loads/token, projected shard size) are descriptive systems observations. No
outcome moves the EFFICIENCY or CORRECTNESS synthesis verdicts, which remain
INCONCLUSIVE-PENDING under their own experiments. [STIPULATED: ASM-2236]

---

## 2. The concept→expert map — mechanism, and its honestly-stated scope

### 2.1 Construction [STIPULATED: ASM-2233]

Built offline, CPU-only, from the committed P0 fingerprints
(`poc/glm52-probe/results/stats/`, 24 prompts spanning **8 concept clusters**,
3 prompts/cluster, with per-layer expert-usage histograms [R1: ASM-2291]):

1. **Universal core (always retained).** The (layer, expert) cells active in all
   24 fingerprints carry ~94% of histogram mass [MEASURED:
   routing-analysis-v2.json `universal_mass_frac` 0.9392] — chat template,
   function words, always-on experts. Dropping them is model destruction, not
   concept selection; every masked arm retains a shared universal core sized at
   pilot (top cells by pooled mass until cumulative mass ≥ a pre-registered
   fraction, frozen in the prereg).
2. **Concept-conditional tail.** For each concept cluster c, rank the remaining
   experts per layer by their mean-centred conditional mass (the residual space
   where concept separation actually lives: within 0.912 vs across −0.074,
   perm p ≈ 1e-4 [MEASURED: routing-analysis-v2.json `mean_centered`]). An item's
   active concepts come from the same harness-side lexical trigger map (G-lex)
   that F1-K uses — no router signal is consumed for gating (G-route stays
   unsupported per `interpretation-fable.md` §4).
3. **Retained set R_kern(item, f).** Per layer: universal core ∪ top
   concept-conditional experts for the item's active concepts, filled to exactly
   f·256 experts. Leave-one-out within concept clusters wherever a test item's
   cluster has trace coverage from its own prompts (n=3/cluster [R1: ASM-2291]),
   so no item is scored against a map built from itself.

### 2.2 Scope, honestly [STIPULATED: ASM-2233; ASSESSMENT where marked]

- **Kernel-specificity is OPEN.** The R4 replay legs (M_oracle, M_kernel — the
  oracle/kernel-vs-deflator pin quantities specified in
  `interpretation-fable.md` §2) have **never been computed**; the branch
  classifier (ASM-2013) is legitimately HELD. What IS mechanically on the record
  (routing-analysis-v2.json) shows concept-shaped routing structure exists
  (p ≈ 1e-4 under the registered 10k-shuffle test) — it does NOT show that kernel
  labels exploit it beyond an embedding-topic conditioner. On the programme's
  four-deflation record, a kernel≈embedding tie is the modal expectation
  [ASSESSMENT]. This design treats that as an open empirical question, prices it
  with its own arm (m-emb), and requires R4 to land before main-phase spend (§7).
- **Concept-vs-lexical confound unresolved.** 3 prompts/concept share content
  words; sense minimal-pairs argue against a purely surface account (break
  centred Δ +0.196, p 0.0029; bank Δ +0.326 at its n=6 permutation floor p 0.103
  [MEASURED: routing-analysis-v2.json]) but surface-disjoint discrimination is
  F1-A's job, not this experiment's. Claims are scoped accordingly.
- **Map coverage is 8 concept clusters (24 prompts, 3/cluster) on one box
  [R1: ASM-2291].** The earlier "~24 concepts" wording overstated this: the
  unit the map can condition on is the CLUSTER, and there are eight. Every
  claim in this design that rests on the count is scoped to C = 8 — in
  particular the cluster-aware inference and its power floor, re-derived in
  §5.2 [R1: ASM-2292]. Items whose active concepts lack trace coverage cannot
  get a kernel mask: they are excluded from masked-arm contrasts and counted;
  if exclusions exceed 20% of the subset, the coverage shortfall surfaces to
  the maintainer before the main phase (scale gate biting, not lever failure —
  ASM-2033 wording carried).
- **Sense-level shards are NOT assumed.** Sense-granular retained sets are
  admissible only if the held classifier lands A1; otherwise word-level concepts
  only (ASM-2013 A1/A2 carried).

---

## 3. Arms [STIPULATED: ASM-2232; masked-arm dose protocol R1: ASM-2290]

All at the same operating point k\* (experts computed per token per MoE layer,
§4.2) and, for masked arms, the same retained fraction f = 0.25 per layer
(64/256; primary — f is a design constant, not a search dimension). Mechanism:
a per-layer candidate bitmask (`DROP=` sidecar, §6.3) restricts the router's
candidate set; the router then takes its own top-k\* among survivors. Uniform arm
is the unrestricted knob colibri already exposes.

| Arm | Candidate set | Selection | What it isolates |
|---|---|---|---|
| **b0-full** | all 256/layer | TOPK=8 (config default) | retention reference |
| **u-topk** | all 256/layer | TOPK=k\* | uniform router-weight drop — deflator 1 (the P0 lever) |
| **m-drng** [R1] | per-item: universal core ∪ concept-conditional fill under a seeded LABEL DERANGEMENT — item i is masked with item σ(i)'s active-concept set, σ a derangement within strata of equal label-set cardinality, so \|labels\| is preserved per item; exactly f·256/layer | TOPK=k\* among survivors | dose-exact structured mask with WRONG labels — the knull analog (replaces m-rand); D2 leg 3 |
| **m-freq** | universal core ∪ top experts by pooled trace usage mass, filled to exactly f·256/layer (the core is the head of the pooled ranking; stated explicitly for dose-exactness) | TOPK=k\* among survivors | kernel-free importance, workload-blind — deflator 2a; D2 leg 1 |
| **m-emb** [R1] | per-item: universal core ∪ top experts by embedding-cluster-conditional mass for the item's top-\|C(item)\| nearest clusters — MATCHED MULTILABEL: the same number of conditioning labels as m-kern's active-concept set for that item (off-the-shelf sentence embedding clusters the trace corpus; no kernel anywhere); exactly f·256/layer | TOPK=k\* among survivors | kernel-free CONDITIONED importance — deflator 2b; D2 leg 2 |
| **m-kern** | R_kern(item, f) per §2.1 — universal core ∪ concept-conditional fill for the item's \|C(item)\| active concepts; exactly f·256/layer | TOPK=k\* among survivors | the kernel arm |

**Dose-exact mask protocol [R1: ASM-2290].** The review found the masked arms
were not dose-matched (single-cluster m-emb vs multilabel m-kern; m-rand
without the universal core). Fixed as a construction invariant: every masked
arm retains EXACTLY f·256 = 64 experts per layer; every mask includes the SAME
universal core; and per-item multilabel structure is matched — m-kern
conditions on the item's \|C(item)\| active concepts, m-emb on the item's
top-\|C(item)\| nearest embedding clusters, m-drng on a same-cardinality
deranged label set drawn from the same concept inventory. Across
m-kern / m-emb / m-drng / m-freq, ONLY the selection criterion differs; the
number of experts removed, the core, and the label-set cardinality do not.
Dose is verified mechanically: the run manifest records per-item, per-layer
retained-set sizes for every masked arm, and any inequality VOIDs the affected
contrast (never reinterpreted — the §4.1 discipline extended to mask dose).
m-drng is what licenses "kernel-guided helps" over "any-structured-drop
helps": identical pipeline, identical dose, identical structure, wrong labels.

Notes: m-emb, m-drng, and m-kern are structurally identical pipelines differing
only in the conditioning signal (matched-cardinality embedding clusters vs
deranged concept labels vs kernel concept labels) — this is deliberate; it is
the only construction that can attribute anything to the kernel labels
themselves. Retained-set Jaccard overlap among m-kern / m-freq / m-emb / m-drng
is reported descriptively per layer; if m-kern∩m-emb (or m-kern∩m-drng) overlap
exceeds 95% the affected pair is declared non-distinct and that D2 leg is
reported as uninformative rather than as a tie [STIPULATED: ASM-2232;
R1: ASM-2290].

---

## 4. Matched-experts protocol [STIPULATED: ASM-2234]

### 4.1 The matched quantity

Primary matched quantity: **realized experts-loaded-per-token**, read from the
engine's own counter (the `experts loaded/token` line, e.g. 1786.5 at TOPK=8,
998.9 at TOPK=4 [MEASURED: probe-main.log P4]) — this is the physical cost
(expert I/O + matmul), and it correctly absorbs MTP union-loading across
speculative drafts. All non-full arms run at the same k\*, so nominal
experts-computed/token match by construction; the realized counter is the
verification. **Match gate:** every masked arm's realized loads/token must be
within ±5% of u-topk's on the same items, else the affected arm is VOID (not
reinterpreted). With f = 0.25, survivors/layer (64) ≫ k\* — no layer can run
short; a short layer (impossible unless f·256 < k\*) is a config error and halts.

### 4.2 Operating-point selection (pilot, dev-only)

The comparison is only informative where uniform dropping actually costs
quality — P0's coherence at TOPK=4 warns that k=4 may be quality-free on easy
items [MEASURED: probe-main.log P4; the n=2 factual check is too small to call
either way, `interpretation-fable.md` §1.1]. Pilot on the dev split only
(§5.1): run b0-full and u-topk at k ∈ {4, 3, 2}; pick k\* = the largest k whose
uniform deficit on dev is ≥ 3 accuracy points. Escalation order if none
qualifies: k=1, then TOPP-tightened k=2. If NO operating point shows a ≥3-point
dev deficit, **STOP and report**: "uniform truncation is retention-free down to
the tested floor on this subset" — itself a strong kernel-free efficiency datum;
the guided-drop question is then unanswerable here (no deficit exists for
guidance to recover) and returns to the maintainer with that datum. Both
directions pre-worded. [STIPULATED: ASM-2234]

### 4.3 Instrument settings

Carried from ASM-2028 discipline: DRAFT=0 (greedy, deterministic scoring);
PILOT off; AUTOPIN/.coli_usage off in all arms (fresh caches at arm boundaries);
DIRECT off (quality endpoints; page cache is a cost lever here, not a
confounder — accuracy does not depend on cache state); item order randomized and
seeded; arm order rotated per item block; every run emits a committed manifest
(binary hash, mask-file hashes, knob values, per-item realized-loads counters,
seeds). Knob semantics re-verified from the checkout at bring-up; any surprise
halts for a protocol amendment BEFORE data collection. [STIPULATED: ASM-2234]

---

## 5. Quality endpoint, statistics, decision rule

### 5.1 Endpoint and items [STIPULATED: ASM-2235]

- **Items:** the F1-K known-concept subset, reused verbatim (MMLU filtered by the
  G-lex trigger map, supplemented mechanically from the ARC-Easy/Challenge /
  OpenBookQA / CommonsenseQA pool; ASM-2030/2038 machinery) — the same items,
  the same splits, the same frozen scorer. Dev = F1-K's dev split (pilot only);
  test untouched until arms freeze. Reuse is deliberate: it amortizes subset
  construction AND scores the drop arms on exactly the concept-covered workload
  the map exists for.
- **Scoring:** one prefill per item per arm with the frozen candidate-independent
  label-token template (F1-K §R1.1); per-option loglikelihood, argmax = answer.
  Generative benchmarking is unaffordable at 0.09–0.25 tok/s (ASM-1988 carried).
- **Primary endpoint:** per-item correctness; retention contrast Δ(arm) =
  acc(arm) − acc(b0-full), fully paired across arms (identical items).
- **Efficiency observations (descriptive only):** realized loads/token per arm;
  a small seeded generative spot-check (≤3 prompts/arm) for tok/s; projected
  deployment shard size f × 370 GB ≈ 93 GB [DERIVED, northstar §2.2]. No
  efficiency claim attaches to these numbers in this experiment.

### 5.2 Statistics and power [STIPULATED: ASM-2235; power clause superseded — R1: ASM-2292]

Unit = item; concept-cluster-aware inference reusing F1-K's REVISION-1 machinery
(cluster-level permutation; ASM-2035/2038 analog): paired one-sided permutation
test, 10,000 resamples, α = 0.05, effect floor ≥ +3 accuracy points per named
contrast — i.e. every licensing gate below is the JOINT rule (p < 0.05 AND
observed Δ̂ ≥ +3).

**Power, re-derived [R1: ASM-2292].** The original target — "0.90 power at the
+3 floor" — was unsound and is WITHDRAWN: under the joint rule a true effect of
exactly +3 gives P(observed Δ̂ ≥ +3) ≈ 0.5, so the observed-margin leg alone
caps joint power at ~50% at true +3 (at ANY n), before the significance leg
removes more. Power is therefore restated as a true-effect MDE, the KaE
§R-REV4.1(b)/§R-REV5.1 discipline carried verbatim:

- **JOINT-rule MDE at 80% power** (Gaussian planning approximation; the exact
  figure comes from the pre-registered permutation simulation at prereg-freeze,
  per the R-REV5.1 caveat): **MDE_true = max(3, c_α·SE) + 0.842·SE**, where
  c_α is the one-sided 5% rejection boundary of the cluster permutation test
  (Gaussian planning: 1.645·SE). Only true effects at or above MDE_true are
  detected with 80% probability by the joint gate.
- **The binding constraint is C = 8 clusters, not n items [R1:
  ASM-2291/2292].** With SE² = (σ_d²/n)·(1 + (m−1)ρ) and m = n/8 items per
  covered cluster, SE floors at σ_d·√(ρ/8) as n grows — item count cannot buy
  power past the 8-cluster floor. Planning rows (σ_d ≈ 39 pts at a 15% paired
  per-item disagreement rate, ρ = 0.10 — the F1-K planning premise family):
  n = 300 → SE ≈ 4.8 pts, c_α·SE ≈ 7.9 pts, **MDE_true ≈ 12 pts**; n → ∞ →
  SE ≈ 4.3 pts, **MDE_true ≈ 10.8 pts** (the floor). **Honest joint power at a
  true +3 effect: ≈ 0.15 at the planning n = 300, and ≤ 0.5 at any n** (the
  ceiling above); the significance leg, not the margin leg, binds at C = 8.
- **Consequence, stated before spend (MD-6 lesson).** At C = 8 the design
  resolves only large true effects (~11–12 pts at planning ρ). The prereg
  publishes the simulated MDE_true at the frozen n and the honest
  power-at-true-+3 figure, and the maintainer decides with those numbers
  whether that resolution is worth the spend — the experiment does NOT run
  carrying the withdrawn 0.90-at-+3 claim anywhere. The real power lever is
  C — collecting trace fingerprints for MORE concept clusters — not n; that
  option is priced to the maintainer alongside the shortfall. A
  non-significant result is scoped "powered to resolve ≥ MDE_true pts at
  C = 8 cluster coverage", never "no effect".

n_max = the available subset (F1-K pool, ≤1,440). Fixed n, no optional
stopping, no post-hoc subgroups beyond the named sense-pair descriptive tag.

### 5.3 Decision rule — frozen wording, both directions [STIPULATED: ASM-2236]

Evaluated on the untouched test split at k\*, in this order:

- **D0 (deficit check).** If acc(u-topk) ≥ acc(b0-full) − 3 points on test (the
  dev deficit vanished), the run is **floor-bound**: no guided-vs-uniform
  contrast is licensed; report the retention-free uniform result and stop.
- **D1 (guided vs uniform).** acc(m-kern) − acc(u-topk) ≥ +3 points, paired
  one-sided permutation p < 0.05, matched loads verified (§4.1).
- **D2 (kernel-specificity) [R1: ASM-2293].** THREE separate named paired
  contrasts, EACH under the joint rule (Δ̂ ≥ +3 points AND its own paired
  one-sided permutation p < 0.05): (a) acc(m-kern) − acc(m-freq); (b)
  acc(m-kern) − acc(m-emb); (c) acc(m-kern) − acc(m-drng). **D2 passes only if
  ALL THREE pass** — a kernel-guided win must beat BOTH kernel-free deflators
  (uniform-TOPK is already D1's job; frequency AND embedding are each tested
  here) and the label-deranged knull mask, never an accuracy-selected
  best-of/max comparator. The conjunction is deliberately conservative; no
  multiplicity relief is taken in the kernel's favour. A leg voided as
  non-distinct (§3 Jaccard rule) or dose-voided (§3 [R1]) makes D2
  UNINFORMATIVE, not passed.

| Outcome | The entire licensed sentence |
|---|---|
| D1 ∧ D2 | "Kernel-concept-guided expert-drop preserved more accuracy than uniform router truncation and than kernel-free importance baselines at matched experts-per-token, on concept-covered QA items at this model and box." Nothing about intelligence, parity, general capability, or deployment. |
| D1 ∧ ¬D2 | "Conditioned expert-drop preserves quality beyond router truncation; the kernel is one conditioner among several." Reported with equal prominence — the fifth guidance-not-kernel datum if it lands. |
| ¬D1 | "Router-weight truncation suffices at this budget; concept guidance added nothing" → kernel-guided B1b recorded **dead-at-this-scale-and-subset**; uniform TOPK stands as a colibri-native, concept-free lever with no kernel sentence attached (ASM-2018 wording carried). |
| D2 leg (c) fails: m-kern − m-drng < +3 or p ≥ 0.05 [R1] | "any-structured-drop regime": DERANGED concept labels preserved as much accuracy as correct ones — mask structure (core + conditioned fill at dose f), not kernel content, did the work. Subsumed by ¬D2 above; named separately because it is the sharpest deflation and the direct knull analog. |

A deflationary outcome at any rung is a real result and is filed at equal
structural prominence. Verdict-gen's registered pathway grades the run; this
document never does.

---

## 6. Co-location, cost, and the standing cost directive [STIPULATED: ASM-2237; costs EXTRAPOLATION: ASM-2238]

### 6.1 Co-location on the KaE (#28) instance — requirement, not option

GLM-DROP runs on the SAME i4i.2xlarge that #28 authorizes for F1-K, sequenced
AFTER F1-K's arms complete (never interleaved inside an arm; cache-state
discipline §4.3), amortizing across both experiments exactly as promised in the
#28 cost thread: one S3 model restore (~370 GB artifact, ~1 h), one bring-up +
fact re-verification, one echo+logprobs gateway patch, one known-concept subset
construction, one prefill-throughput measurement (F1-K's bring-up number is
reused to price this experiment's main phase before it starts — no separate
bring-up line). If #28's GATE 0/1 do not both land, GLM-DROP still runs on the
same instance class with its own restore; only the amortization is lost (the
DROP patch does not depend on the KaE patch, §6.3).

### 6.2 Cost-saving measures baked in (maintainer directive, #28 thread)

1. **SPOT instances:** i4i.2xlarge spot ≈ $0.20–0.28/h vs $0.69 on-demand
   (planning figures, verified at spin-up) — ~3× cut. The eval is one prefill
   per item per arm, checkpointed per item; a spot interruption resumes from the
   last completed item. Long runs launched nohup+setsid (house box discipline).
2. **Expert-pinning + warm cache:** masked arms draw from a 64-expert/layer pool
   (~93 GB) instead of 370 GB — the page cache runs far hotter by construction;
   additionally the universal core + workload-hot experts (measured at pilot) are
   PIN-ned within measured free RAM. This is the directive's pinning lever
   applied to eval throughput; it changes cost only, never scoring.
3. **Item-block batching:** items sharing active concepts are scheduled
   adjacently within an arm so their retained sets overlap in cache (order
   randomization operates at block level, seeded, recorded).
4. **No idle instance:** the box is stopped between phases; artifact persists in
   S3 ($8.5/mo line already running).

### 6.3 The one C change: the DROP mask [STIPULATED: ASM-2239]

`DROP=<mask-file>` — a per-layer expert bitmask sidecar read at startup; router
candidates are restricted to surviving experts before top-k. Estimated 40–60
lines against the same pinned colibri commit the KaE draft targets
(a78a06fc5acc4b0dc0f9ef03987c66b0559d1250), kept as an in-repo diff, inert
unless DROP is set, fail-closed on malformed masks (engine refuses to start —
never a silent partial arm). This is NOT a Law-1 matter (it selects among native
experts; nothing writes activations) but it EXCEEDS the P0 trace-dump-only C
envelope (ASM-1986/1989), so the diff rides maintainer patch approval — bundled
into the #28 review for one decision, not a new gate. Fork etiquette carried
from ASM-1989; nothing is pushed upstream.

### 6.4 Cost bands [EXTRAPOLATION: ASM-2238 — planning figures, never premises]

Prefill throughput on this box is UNKNOWN until F1-K bring-up measures it
(ASM-2023 carried); bands below use its $40–140/7-arm band as the scaling
anchor. Pilot: 24 dev items × (2 arms × 3 k-values + spot-checks) ≈ 170
prefills. Main: 6 arms × n (power-derived, ≤1,440-pool, planning n ≈ 300) ≈
1,800 prefills + mask/map construction (CPU, ~$0). Band ≈ **$15–45 spot**;
**CEILING $60 spot-hours** (≈ $150 if spot capacity forces on-demand, which
requires coordinator sign-off, not silent fallback). Pre-registered degradation
order if the ceiling binds [R1: ASM-2293]: (1) drop the escalation k-cell;
(2) cut the generative tok/s spot-checks (descriptive only); (3) return to the
maintainer. **NO masked arm can be dropped:** m-freq, m-emb, AND m-drng are
all required by the both-deflators D2 rule (§5.3 [R1]), and the order NEVER
cuts n below the frozen power/MDE basis (MD-6 lesson).

---

## 7. Sequencing, gating, and prerequisites [STIPULATED: ASM-2230/2231]

1. **R4 replay first, before any spend.** The offline M_oracle/M_kernel replay
   (`interpretation-fable.md` §2 R4) is CPU-only on committed bytes, ~$0, and
   MUST land through the coordinator's mechanical pathway before GLM-DROP's main
   phase: it completes the held ASM-2013 branch classifier and prices D2's prior
   (an M_kernel failure against the embedding deflator on the pin replay is
   registered prior evidence against D2 and is reported alongside GLM-DROP's
   result either way).
2. **Sequencing amendment to ASM-2010 (stipulated here, registered by the
   coordinator).** ASM-2010 gated B1b behind B1a's outcome. The maintainer's
   #27-A redirect promotes B1b to the primary efficiency instrument; ASM-2230
   amends the sequencing: GLM-DROP's admissibility no longer waits on a B1a live
   win — its physics lever (fewer experts computed) is TOPK-like and does not
   presuppose pin-miss structure — but it inherits every deflator obligation,
   and a Branch-B/C classifier outcome scopes (not blocks) its claims per §2.2.
   F1-K's primacy and gates (#28) are untouched.
3. **Own prereg before freeze.** This document is the design; the experiment
   still requires its own kot-reg/1 prereg (experiment-designer role: frozen
   thresholds, seeds, mask hashes, power simulation, pre-freeze skeptic attack)
   and runs only inside maintainer-approved ceilings. Nothing fires from this
   pass.
4. **Prerequisites:** F1-K bring-up artifacts (subset, scorer, throughput
   number) or, degraded, their independent construction; the DROP patch
   approval (§6.3); R4 landed (item 1); the 24-fingerprint trace set (exists,
   committed).

**Honest risks [ASSESSMENT]:** (i) the modal outcome on the programme's record is
D1-tie or D1-pass/D2-tie — either is a publishable systems datum and neither is
a kernel result; (ii) the deficit regime may not exist above k=1 on this subset
(GLM-5.2 is strong; §4.2's STOP handles it honestly); (iii) the map rests on 24
prompts across only 8 concept clusters [R1: ASM-2291] — thin, disclosed, and
doubly binding: C = 8 is also the inference floor that fixes the ~11–12-pt
MDE_true (§5.2 [R1: ASM-2292]); the 20% exclusion gate, the Jaccard-degeneracy
check, and the dose gate exist because of it, and the honest power lever is
more trace clusters, not more items; (iv) spot capacity for i4i.2xlarge can dry
up — the ceiling names the on-demand fallback as a decision, not a default.

---

## R1. REVISION 1 — codex design-review response [STIPULATED: ASM-2290..2293]

The standing codex review of this design (pre-revision bytes sha256
e52b3c3a…d966) returned ISSUES on four points. Each is fixed in place above
(tagged [R1]); this section is the audit trail. No review-OK item was touched:
the fixed-compute k\* ±5% matched-loads comparison (§4.1), the full-TOPK=8
retention reference (b0-full), and the spot/pinning/co-location cost design
(§6.1–6.3) stand byte-for-byte.

1. **Deflator masking — dose-exact, matched multilabel [ASM-2290].** Found:
   m-emb conditioned on ONE nearest cluster while m-kern may union multiple
   concepts, and m-rand lacked the universal core — the drop-selection arms
   were not dose-matched, so a m-kern win could have reflected dose or
   structure, not labels. Fixed (§3): every masked arm retains exactly
   f·256 = 64 experts/layer including the same universal core; m-emb is
   matched-multilabel (top-\|C(item)\| clusters, the same per-item label
   cardinality as m-kern); m-rand is replaced by **m-drng**, a dose-exact
   LABEL-DERANGED mask (the m-kern pipeline under a seeded
   cardinality-stratified derangement of item→concept-set assignment). All
   three drop-selection arms now remove the SAME number of experts with
   matched multilabel structure; only the selection CRITERION differs. The
   manifest verifies dose per item per layer; inequality VOIDs the contrast.
   This preserves the knull "kernel-guided helps, not any-structured-drop"
   discipline as a construction invariant.
2. **Coverage corrected [ASM-2291].** Found: "~24 concepts" overstated the
   probe source, which is 24 prompts across only **8 concept CLUSTERS**
   (3 prompts/cluster). Fixed: §2.1, §2.2, and §7 risk (iii) now state the
   8-cluster coverage; every claim resting on the count is re-scoped to C = 8,
   and the power analysis is re-derived on that basis (item 3).
3. **Quality power re-derived [ASM-2292].** Found: "0.90 power at a true +3"
   is impossible under the joint licensing rule (p < 0.05 AND observed ≥ +3):
   at true +3 the observed-margin leg alone has a ~50% ceiling. Fixed (§5.2):
   the target is withdrawn; power is restated as a true-effect MDE per the KaE
   §R-REV4.1(b)/§R-REV5.1 precedent — **MDE_true = max(3, c_α·SE) +
   0.842·SE** for 80% joint power (Gaussian planning; exact by simulation at
   prereg-freeze). At the actual C = 8 coverage, SE floors at σ_d·√(ρ/8), so
   planning MDE_true ≈ 12 pts at n = 300 and ≈ 10.8 pts at n → ∞, with honest
   joint power at true +3 of ≈ 0.15 at planning n (≤ 0.5 at any n). The frozen
   prereg must publish the simulated MDE_true and the honest power-at-+3
   figure; the maintainer decides on those numbers (MD-6), and the named power
   lever is more trace clusters (C), not more items (n).
4. **D2 both-deflators rule [ASM-2293].** Found: D2 compared m-kern against
   max(acc(m-freq), acc(m-emb)) with a single test "against the STRONGER
   deflator" — an accuracy-selected comparator whose permutation null ignores
   the selection. Fixed (§5.3): D2 is a CONJUNCTION of three separate named
   paired contrasts — m-kern vs m-freq, m-kern vs m-emb, m-kern vs m-drng —
   each requiring Δ̂ ≥ +3 AND its own p < 0.05; all must pass. §1's crux and
   §6.4's degradation order are updated to match (no D2 comparator can ever
   be dropped). ASM-2232's m-rand arm, ASM-2235's power clause, and
   ASM-2236's D2 max clause are superseded on exactly these points; the
   ASM-2230..2239 companion file is left intact as the pre-review record and
   the coordinator registers the amendment centrally as usual.

---

## Self-check gate (governance)

Every load-bearing claim above carries MEASURED / DERIVED / STIPULATED /
EXTRAPOLATION / ASSESSMENT; every design choice is STIPULATED with an ASM id in
ASM-2230..2239 or (REVISION 1) ASM-2290..2293; both directions of every gate
(D0/D1/D2, the §4.2 STOP, the coverage and power shortfalls) are worded in
advance; the deflator arms (uniform-TOPK at matched loads; frequency;
matched-multilabel embedding-cluster; dose-exact label-deranged knull mask) are
mandatory before any kernel-specific sentence, D2 requires beating EACH of them
in its own named contrast (never a best-of), and all masked arms are
dose-exact (same expert count, same universal core, matched multilabel
structure — only the selection criterion differs); the probe coverage is
stated as 24 prompts across 8 concept clusters and the power analysis is a
true-effect MDE under the joint rule at C = 8, with the withdrawn 0.90-at-+3
target recorded as withdrawn; kernel-specificity is recorded OPEN pending R4,
not assumed. No feasibility conclusion is stated. No frozen record, verdict,
encoder pin, or registered assumption is touched; `registry/assumptions.jsonl`
is not written; no git action, no model run, no spend occurs in this pass.
Companion assumptions emitted to `poc/glm52-probe/asm-glm-drop-2230-2239.json`
(pre-review record, left intact) and
`poc/glm52-probe/asm-glm-drop-r1-2290-2293.json` (REVISION 1; owner designer-8;
range verified free at emission — central register tail ASM-2259, repo-wide
grep for `ASM-229[0-9]` empty); central registration of both blocks, with the
supersession notes in §R1 item 4, is the coordinator's action, with the landing
commit, after the standing GPT-5.6 review gate.
