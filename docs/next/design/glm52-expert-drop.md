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
2. **a kernel-free expert-importance baseline at the same retained fraction and
   the same k** — pooled usage-frequency retention AND an embedding-topic-cluster
   conditioned retention (the knull-analog for this seam; the *stronger* of the
   two is the comparator, ASM-1977 discipline carried).

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
(`poc/glm52-probe/results/stats/`, 24 prompts × 8 concept clusters × per-layer
expert-usage histograms):

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
   concept has trace coverage from its own prompts (n=3/concept), so no item is
   scored against a map built from itself.

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
- **Map coverage is ~24 concepts on one box.** Items whose active concepts lack
  trace coverage cannot get a kernel mask: they are excluded from masked-arm
  contrasts and counted; if exclusions exceed 20% of the subset, the coverage
  shortfall surfaces to the maintainer before the main phase (scale gate biting,
  not lever failure — ASM-2033 wording carried).
- **Sense-level shards are NOT assumed.** Sense-granular retained sets are
  admissible only if the held classifier lands A1; otherwise word-level concepts
  only (ASM-2013 A1/A2 carried).

---

## 3. Arms [STIPULATED: ASM-2232]

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
| **m-rand** | random f·256/layer (seeded, universal core NOT protected) | TOPK=k\* among survivors | floor: "any mask at f" — descriptive sanity |
| **m-freq** | top f·256/layer by pooled trace usage mass | TOPK=k\* among survivors | kernel-free importance, workload-blind — deflator 2a |
| **m-emb** | per-item: universal core ∪ top experts by embedding-cluster-conditional mass (off-the-shelf sentence embedding clusters the trace corpus; item assigned to nearest cluster; no kernel anywhere) | TOPK=k\* among survivors | kernel-free CONDITIONED importance — deflator 2b, the knull-analog |
| **m-kern** | R_kern(item, f) per §2.1 | TOPK=k\* among survivors | the kernel arm |

Notes: m-emb and m-kern are structurally identical pipelines differing only in
the conditioning signal (embedding cluster vs kernel concept labels) — this is
deliberate; it is the only comparison that can attribute anything to the kernel.
Retained-set Jaccard overlap between m-kern / m-freq / m-emb is reported
descriptively per layer; if m-kern∩m-emb overlap exceeds 95% the arms are
declared non-distinct and the D2 contrast is reported as uninformative rather
than as a tie [STIPULATED: ASM-2232].

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

### 5.2 Statistics and power [STIPULATED: ASM-2235]

Unit = item; concept-cluster-aware inference reusing F1-K's REVISION-1 machinery
(cluster-level permutation; ASM-2035/2038 analog): paired one-sided permutation
test, 10,000 resamples, α = 0.05, effect floor ≥ +3 accuracy points per named
contrast. Required n is power-derived (0.90 at the +3 floor) from pilot variance
using the same simulation rig F1-K's power gate used; n_max = the available
subset (F1-K pool, ≤1,440). **MD-6 lesson baked in:** if the power-required n
exceeds the available subset, the experiment does NOT run underpowered by
default — it surfaces to the maintainer with the measured shortfall and the
priced options. Fixed n, no optional stopping, no post-hoc subgroups beyond the
named sense-pair descriptive tag.

### 5.3 Decision rule — frozen wording, both directions [STIPULATED: ASM-2236]

Evaluated on the untouched test split at k\*, in this order:

- **D0 (deficit check).** If acc(u-topk) ≥ acc(b0-full) − 3 points on test (the
  dev deficit vanished), the run is **floor-bound**: no guided-vs-uniform
  contrast is licensed; report the retention-free uniform result and stop.
- **D1 (guided vs uniform).** acc(m-kern) − acc(u-topk) ≥ +3 points, paired
  one-sided permutation p < 0.05, matched loads verified (§4.1).
- **D2 (kernel-specificity).** acc(m-kern) − max(acc(m-freq), acc(m-emb)) ≥ +3
  points, same test against the STRONGER deflator.

| Outcome | The entire licensed sentence |
|---|---|
| D1 ∧ D2 | "Kernel-concept-guided expert-drop preserved more accuracy than uniform router truncation and than kernel-free importance baselines at matched experts-per-token, on concept-covered QA items at this model and box." Nothing about intelligence, parity, general capability, or deployment. |
| D1 ∧ ¬D2 | "Conditioned expert-drop preserves quality beyond router truncation; the kernel is one conditioner among several." Reported with equal prominence — the fifth guidance-not-kernel datum if it lands. |
| ¬D1 | "Router-weight truncation suffices at this budget; concept guidance added nothing" → kernel-guided B1b recorded **dead-at-this-scale-and-subset**; uniform TOPK stands as a colibri-native, concept-free lever with no kernel sentence attached (ASM-2018 wording carried). |
| m-rand ≈ m-kern (descriptive, Δ < 3 points) | flagged "any-mask regime" alongside whichever primary outcome obtains — an interpretive caution, not a gate. |

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
order if the ceiling binds: (1) drop m-rand; (2) drop m-freq (m-emb is the
stronger deflator and is never dropped); (3) drop the escalation k-cell;
(4) return to the maintainer. The order NEVER cuts n below the power
requirement (MD-6 lesson) and never drops a deflator required by D2.

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
prompts — thin, disclosed, and the 20% exclusion gate + Jaccard-degeneracy check
exist because of it; (iv) spot capacity for i4i.2xlarge can dry up — the ceiling
names the on-demand fallback as a decision, not a default.

---

## Self-check gate (governance)

Every load-bearing claim above carries MEASURED / DERIVED / STIPULATED /
EXTRAPOLATION / ASSESSMENT; every design choice is STIPULATED with an ASM id in
ASM-2230..2239; both directions of every gate (D0/D1/D2, the §4.2 STOP, the
coverage and power shortfalls) are worded in advance; the deflator arms
(uniform-TOPK at matched loads; frequency; embedding-cluster; random floor) are
mandatory before any kernel-specific sentence; kernel-specificity is recorded
OPEN pending R4, not assumed. No feasibility conclusion is stated. No frozen
record, verdict, encoder pin, or registered assumption is touched;
`registry/assumptions.jsonl` is not written; no git action, no model run, no
spend occurs in this pass. Companion assumptions emitted to
`poc/glm52-probe/asm-glm-drop-2230-2239.json` (owner designer-8; range verified
free at emission — central register tail ASM-2202, repo-wide grep for
`ASM-223[0-9]` empty); central registration is the coordinator's action, with
the landing commit, after the standing GPT-5.6 review gate.
