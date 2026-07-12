# SCALE-1 S0 (10k rung) — interpretation and de-risked 100k-rung plan

**Date:** 2026-07-12
**Inputs:** `poc/scale/results/scale-s0-10k-readout.md`, `poc/scale/results/scale-s0-n{1000,10000}-report.{json,md}`, `docs/next/design/large-kernel-scale-track.md` (the design), `poc/scale/README.md`, ASM candidates `poc/scale/asm-1780-1789.json` (ASM-1780..1787).
**Epistemic tags:** [MEASURED] / [DERIVED] / [STIPULATED] / [EXTRAPOLATION] / [OPEN], per the design's convention.

**Standing discipline.** S0 is an exploratory engineering pilot over a STIPULATED
selection rule, a STIPULATED typing crosswalk and the EXPLORATORY §6.3 import
vectoriser `kot-enc-import/0-poc` (NOT construction B; kot-enc-B/1 pins and goldens
untouched). Every 100k/1M figure below is [EXTRAPOLATION] — to be measured, never a
premise. **This document makes NO feasibility conclusion; CORRECTNESS and EFFICIENCY
remain INCONCLUSIVE-PENDING (design §14).**

---

## 1. What the 10k readout licenses [MEASURED]

Four design predictions were tested against direct measurement at m = 10,000 and
survive. These are the only affirmative claims this rung licenses, and each is
scoped to the import vectoriser and the WordNet-only corpus actually built.

### 1.1 The §6.5 Gaussian-crosstalk model holds for the class it describes

For pairs in the *disjoint* class (no direct edge, no shared axiom target,
different lexFile — the class the independent-vector Gaussian model actually
addresses):

- **σ within 3% of 1/√D at every tested D** [MEASURED]: at D=8192, measured
  disjoint-pair σ 0.01106 vs predicted 0.01105; at D=512, 0.0456 vs 0.0442; at
  D=576, 0.0432 vs 0.0417.
- **The max-spurious-cosine curve √(2 ln m / D) is an upper envelope that the
  measured per-concept maxima respect** [MEASURED]: median per-concept
  max-disjoint cosine 0.169 vs the 0.1897 curve (proj512, m=10⁴), 0.1621 vs
  0.1788 (proj576), 0.0353 vs the 0.0411 sample curve (canon8192, 1k sample).
  The design's quoted ≈0.046 at m=10⁴/D=8192 (formula value 0.0474) is
  consistent with the measured statistics.

So the answer to the question the rung was built to ask — *does the design's
crosstalk arithmetic match reality?* — is **yes, it matches**, at three
dimensions and two rung sizes (ASM-1782). What does NOT follow is that this
curve is the binding constraint on margins; §2.4 below shows it is not.

### 1.2 Encode compute and storage arithmetic hold

- **Encoding is not the million-scale wall** [MEASURED → EXTRAPOLATION]:
  canonical D=8192 import vectorisation ran at 39.3 ms/concept on one niced
  shared core, *dominated by the two JL projections*; the native-512 encode
  alone is 258 µs/concept, with zero FFTs (the §1.2 two-FFTs-per-child cost is
  construction-B-specific and correctly absent on this path). Linear
  extrapolation gives ~1.1 CPU-h at 100k and ~10.9 CPU-h at 1M — small against
  the design's S1 band of 200–2,000 CPU-h for *all* stages (ASM-1785).
- **Storage arithmetic is exact** [MEASURED]: 327.68 MB fp32 dense at 10k/D=8192,
  matching §6.4 to the stated precision (0.655 GB fp64 / 0.164 GB fp16).
- **Determinism claims hold** [MEASURED]: all six stores byte-identical under
  independent recomputation (sha256, `out/n1000/vec/verify-report.json`);
  cycles handled without a reference DAG; zero silent axiom drops (ASM-1781).

### 1.3 The RDM-Spearman calibration: a negative result that is itself licensed

The X4 kernel-v0 calibration (RDM Spearman 0.9718/0.9706 at 54 concepts,
8192→512/576) **does not transfer** to bulk-import stores [MEASURED]: global RDM
Spearman is 0.2613/0.2820 at 10k. The mechanism is now understood, not merely
observed: on a bulk-import corpus, RDM mass sits in the near-zero disjoint noise
floor (σ ≈ 0.011 at D=8192), and *any* dimensionality reduction re-randomises
that floor. The operationally relevant fidelity numbers — structure-bearing
top-pair Spearman (0.81–0.82 at 10k, down from 0.98 at 1k) and strong-NN
recall@1 (0.41–0.42 at 10k, down from 0.64–0.67 at 1k) — degrade with m for
**native** 512/576 re-encoding just as for JL projection, identifying this as a
**D-capacity effect, not a projection artefact** (ASM-1784). What this licenses:
the kernel-v0 0.97 figure must never again be cited as evidence about
host-dimension fidelity at scale; host-dimension arms at 100k+ need re-gating
(§3.5).

### 1.4 Wall-clock qualification

The full 10k pipeline (ingest → typing → six vector stores → metrics) completed
within its 30-minute shared-core budget with no partial-run fallback
[MEASURED]. The machinery-qualification purpose of S0 (design §8) is met at
this rung.

---

## 2. The honest blockers, and what each means for the scale thesis

The rung's more valuable product is its four blockers. None is a feasibility
verdict; each converts a design assumption into a measured constraint that the
next rung must engineer around.

### 2.1 WordNet-only typing yields 0% identity/dependence — the 0.95 gate is unreachable on this source

[MEASURED, ASM-1787] The imported-vs-inferred split at 10k: WordNet asserts
**no** native UFO structure beyond the instance flag (denotation_level
source-asserted for 1.27%). Everything else is STIPULATED rule inference:
ontic_category 52.0% hard / 41.9% soft / 6.0% underdetermined; sortality 85.5%
underdetermined; rigidity 86.8% underdetermined; **identity and dependence 100%
underdetermined**. No human audit sample exists yet at S0, so even the hard
inferences carry no measured precision.

**Meaning for the thesis:** the design's §4.3 promotion gate (lower 95% CI of
hard-typing precision ≥ 0.95) and the S1→S2 requirement of a passing stratified
audit are *unreachable in principle* by scaling the current WordNet-only rules —
the fields the full-UFO thesis most needs (identity providers, dependence,
relator patterns) have zero evidential source here. The "fully resolved CK-UFO
records" count of §3.5 will come essentially entirely from the OBO/BFO, SUMO
and gUFO-style legs of the §3.1 portfolio, plus endorsement. This is a
*sourcing* blocker, not a schema failure: the sidecar machinery correctly
preserved unknowns as `underdetermined` rather than fabricating values — which
is exactly the behavior §11 demands.

### 2.2 Exact O(m²) cleanup dies between the rungs

[MEASURED → EXTRAPOLATION, ASM-1786] The exact NN cleanup pass measured 117 s
at m=10⁴, D=512, one core → ~3.2 h at 100k, **~324 CPU-h at 1M**. The design's
§6.5 warning (the decoder's `conceptNN` linear scan is the retrieval analogue)
is confirmed by measurement: the exact path is workable *once* at 100k
(usefully, as ANN ground truth) and infeasible as an operational path at 1M on
box-class hardware. The ANN index plus the ≥0.99 exact-vs-ANN recall gate
(S1→S2) is therefore **mandatory between 100k and 1M**, and prudently built and
gated *at* 100k while exact ground truth is still cheap.

### 2.3 The selection rule exhausts at 27,210

[MEASURED, ASM-1780] The SemCor tag_cnt pool contains exactly 27,210 nonzero
synsets; the 10k boundary already sits at tag_cnt = 4. **This rule cannot
produce the 100k rung.** Consequence: the §3.1 multi-source portfolio — with
crosswalk, type-level dedup and per-shard license machinery that does not yet
exist in `poc/scale/` — becomes load-bearing one rung earlier than the compute
does. The S1 selection rule is an open design obligation, not a parameter tweak.

### 2.4 Duplicate structural mass, not crosstalk, is the binding margin constraint — and it worsens down the tail

[MEASURED, ASM-1783] 2,008/10,000 records (20.1%) fall into 475
identical-token-multiset groups (largest: 466 zero-axiom adverbs; 662 records
have no axioms at all), producing **124,343 vector-identical pairs
(cos > 0.9999)** in every lexical-free store — §6.5 collision class 2 realised
at 20% incidence. These are *legitimate* under the record-identity rule
(glosses/lemmas are annotations outside identity): a representational-poverty
ceiling of AxiomsOnly WordNet import, not an encoder defect. Two aggravating
observations:

- **The incidence grows toward the tail** [MEASURED at two rungs]: 1.2% of
  records were duplicates at the 1k rung (13.6 axioms/concept) vs 20.1% at 10k
  (5.8 axioms/concept). Descending into sparser synsets thins the axiom
  structure that individuates records; extrapolating the trend (direction only,
  [EXTRAPOLATION]) the 100k tail should be worse, not better.
- **The obvious patch is not free** [MEASURED]: the optional §6.2 lexical block
  cuts >0.999 pairs from 124,343 to 55 but degrades top-pair RDM fidelity from
  0.81 to 0.56 — lexical tokens buy identity at the price of semantic-geometry
  distortion.

**Meaning for the thesis:** the §12 margin-distribution gate, as currently
framed, would at 100k be measuring the duplicate census, not the encoder's
margin behavior. Without a pre-registered structural-duplicate/differentia
policy fixed *before* the 100k vectorise, any margin pass/fail at S1 is
uninterpretable — post-hoc policy choice could manufacture either verdict.

---

## 3. A de-risked 100k-rung (S1) plan

[STIPULATED throughout; costs are planning estimates, not commitments.] Each
element addresses one measured blocker; the sequencing puts decisions that
change downstream numbers *before* the compute they change.

### 3.1 Multi-source typing and selection portfolio (addresses §2.1, §2.3)

**Sources** (per design §3.1/§3.2, permissive core only at this rung):

- **WordNet 3.1** (117,791 synsets) remains the lexical backbone but is no
  longer the selector.
- **OBO/BFO** — 96,192 records with 24,578 genus–differentia logical definitions
  already local [MEASURED, design §1.1]. This is the primary source of
  *source-asserted* UFO commitments: BFO anchoring gives ontic_category
  (continuant/occurrent → object/event), and genus–differentia definitions give
  both differentia structure (§3.4 below) and identity-provider candidates via
  the genus chain.
- **SUMO** — 3,705 terms, 15,595 KIF axioms local; the SUMO↔WordNet mapping
  (not yet loaded) is the crosswalk lever: it types WordNet synsets *by
  imported commitment* (cascade step 1–2) rather than by lexFile guess (step 3).
- **Wikidata** — class-subset shard from the official CC0 dumps for P31/P279
  class structure and cross-source exact identifiers (crosswalk fuel and
  count-headroom); individuals excluded from the concept count per §0.

**Selection rule** [must be disclosed and pre-registered]: a benchmark-blind
union rule, e.g. rank by (source multiplicity of the crosswalked cluster,
then degree, then URN) over the deduplicated cluster set — a pure function of
the pinned snapshots, replacing the exhausted tag_cnt rule. Report the §3.5
four counts (raw records / exactly crosswalked clusters / type-level clusters /
fully resolved CK-UFO records) with per-shard license manifests.

**Typing target:** identity/dependence coverage moves off 0% only via
imported commitments (cascade steps 1–2). Expectation to be *measured*, not
assumed: OBO-anchored records should reach nonzero source-asserted
ontic_category and identity-provider candidates; the WordNet-only residue
stays mostly underdetermined and is reported as such. **Add the missing §4.3
stratified human audit sample at this rung** (stratified by source × field ×
cascade step; oversample role/phase/relator/identity assignments), because
without it the 0.95 hard-precision gate has no estimator at all — this is the
single cheapest item that unblocks the S1→S2 gate.

### 3.2 ANN cleanup index with a ≥0.99 recall gate (addresses §2.2)

Build a deterministic-parameter ANN index (HNSW-class or IVF-class; pinned
build parameters, pinned insertion order so the index is reproducible) over
each persisted store. Gate [pre-registered, from design §8.1]: exact-vs-ANN
recall@1 and recall@10 ≥ 0.99 on ≥10k held-out queries, stratified by source
and type, with the one-off exact O(m²) pass (~3.2 CPU-h at 100k
[EXTRAPOLATION]) as ground truth. Failing the gate means repair the index, not
relax the gate. Deliverable: the 1M rung inherits a *qualified* retrieval path
instead of meeting the cleanup wall mid-campaign.

### 3.3 Pre-registered structural-duplicate/differentia policy (addresses §2.4)

Freeze, *before* the S1 vectorise, a written policy of the form:

1. **Enrich first**: records gaining differentia from OBO logical definitions
   or SUMO axioms via crosswalk leave the duplicate class by content, not by
   annotation (the preferred exit).
2. **Pinned lexical profile** as a *disclosed, separately versioned* store
   variant for records that remain structurally identical — carrying the
   measured fidelity cost (0.81 → 0.56 top-pair ρ at w=0.5) as a reported
   trade-off, possibly at a re-tuned weight; never silently merged into the
   lexical-free canonical store.
3. **Report-not-drop** for irreducible duplicates (e.g. the 466-adverb class):
   they remain counted records but are excluded from the margin-gate
   denominator *by the pre-registered rule*, and the duplicate census is
   published alongside every margin number.

The point is not which branch wins — it is that the branch is chosen before
the numbers exist, so the §12 margin gate at S1 measures the encoder, not the
policy.

### 3.4 SCC validation on the real OBO 1,142-term SCC (addresses the cycle risk)

S0 ran one synchronous round on a near-acyclic graph — the §6.3 multi-round
SCC path is untested at real cycle scale [MEASURED gap]. Before the full S1
vectorise: run the pinned multi-round synchronous construction on the known
OBO 1,142-term SCC (design §1.1) as a fixture; require byte-determinism across
independent recomputations, round-count sensitivity reporting, and the
§12 shuffled-edge control on the SCC subgraph. Cheap (minutes of compute) and
it retires the one algorithmic unknown between the import vectoriser and the
OBO-heavy S1 corpus.

### 3.5 Host-dimension re-gating (carries forward §1.3)

The E-series-style projected arms cannot inherit the kernel-v0 X4 calibration
[MEASURED]. At S1, re-measure top-pair ρ and strong-NN recall at D ∈ {512,
576} and at least one larger projection D as a capacity probe; gate any
host-integration arm on the S1-measured numbers, not the 54-concept ones.

### 3.6 Sequence and rough cost

| step | item | blocker | rough cost [EXTRAPOLATION] |
|---|---|---|---|
| 1 | Pre-register S1 selection rule + duplicate/differentia policy + audit design | §2.3, §2.4 | ~1 wk design/review, no compute |
| 2 | SCC fixture on OBO 1,142-term SCC | cycles | <1 CPU-h |
| 3 | Multi-source ingest, crosswalk, type-level dedup, license manifests | §2.3 | 2–4 wks engineering (the dominant cost); CPU-days |
| 4 | Typing portfolio + stratified human audit sample | §2.1 | ~1 wk rules + audit-hours (human time dominates) |
| 5 | Vectorise 100k (six stores) | — | ~1.1 CPU-h canonical [EXTRAPOLATION from 39.3 ms/concept] |
| 6 | One-off exact O(m²) ground truth + ANN build + ≥0.99 recall gate | §2.2 | ~3.2 CPU-h exact + hours ANN |
| 7 | Metrics under the frozen policy: margins, duplicate census, RDM/NN re-gate, cost tables | all | CPU-hours |

Total inside the design's S1 band (200–2,000 CPU-h, 4–8 weeks) with wide
headroom on compute; the schedule risk is concentrated in step 3's crosswalk
engineering and step 4's human audit-hours, exactly as the design's §10
[EXTRAPOLATION] anticipated ("dominated by crosswalks, typing audits… rather
than GPU time").

---

## 4. Claim caps

**What a clean 100k rung would license** (all conditional on the gates above
passing, all [MEASURED]-scoped to the import vectoriser):

- crosstalk-model validity and margin behavior *under a pre-registered
  duplicate policy* at m = 10⁵, one decade further along the √(2 ln m/D) curve;
- a qualified ANN retrieval path (≥0.99 recall vs exact) — the S1→S2
  infrastructure gate;
- a first *estimated* hard-typing precision with confidence bounds against the
  0.95 bar, and a measured multi-source resolution profile for
  identity/dependence;
- multi-source dedup/crosswalk machinery demonstrated at the four-count
  reporting standard;
- SCC-scale determinism of the §6.3 construction.

**What it would NOT license** — and these caps are hard:

- **No feasibility conclusion**: CORRECTNESS and EFFICIENCY remain
  INCONCLUSIVE-PENDING regardless of S1's outcome (design §14). S0 and S1
  qualify machinery; neither tests the thesis.
- **No scale-thesis evidence in either direction**: the governing question
  (design §0, §7.2) is answered only by the SCALE-GROUND nested interaction
  `(A4−A2 at 1M) − (A4−A2 at 10k)` with ≥30% tail-exposed items and a causally
  active store — none of which exists at 100k. A store that is merely built
  and vectorised is, per §0.8, not enough.
- **No "emergence" or coverage claims**: coverage is reach-and-successful-use
  (§7.7), measurable only against benchmark legs S1 does not run.
- **No transfer to construction B**: every S1 number is a property of
  `kot-enc-import/*`; nothing touches kot-enc-B/1's record.
- **No million-scale margin/recall extrapolation as premise**: the duplicate
  incidence trend, the NN-recall-vs-m curve and the ANN behavior at 1M remain
  [EXTRAPOLATION] until measured — the design's own discipline.

**What only emerges at 1M+** [per design §7.2, §10]: the thesis-grade
quantities — long-tail coverage with realistic distractors, tail-exposed
retrieval and proof behavior, the architecture-by-scale interaction, closure
tractability at ≥10M facts, ANN recall at genuine million-candidate cleanup,
and the domain-balance question (whether the count survives exclusion of
single-taxonomy domination). The 100k rung's entire role is to make that
experiment *runnable without instrumentation failure* — it cannot substitute
for it.

---

*This interpretation issues no feasibility conclusion. Registration of
ASM-1780..1787 is a coordinator action; this document only cites the
candidates.*
