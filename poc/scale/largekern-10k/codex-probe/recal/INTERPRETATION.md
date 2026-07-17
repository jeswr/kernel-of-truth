# INTERPRETATION — largekern-10k recalibration probe (n=25 representative, codex R=2)

**Role:** interpretation owner (coordinator does not conclude). Single-shot, no experiments run.
**Date:** 2026-07-17
**Data:** `codex-probe/recal/out/results.json` (sampleSha256 `7a2d522c…45be9`, seed
`largekern10k-codexcal-repr-v1`, ASM-2498 stratified draw over the 10k worklist),
per-item raw outputs in `out/runs/`, fixed prompt `pipeline/prompt.py`
(cachePrefixHash `237a178d337d4f7e`, closed-lexicon BLOCK 2 fix in place).
**Frozen gate:** primary PROCEED α ≥ 0.70 Wilson-95 LB (prereg-freeze `frozen_sha256 9533262c`,
commit 5876da07).

Every load-bearing claim is tagged **[MEASURED]** / **[STIPULATED]** / **[ESTIMATE]**.

---

## Headline verdict

The pipeline instrument now works; the kernel does not cover the language.

- **[MEASURED]** n=25: accepted 6, abstain 19, quarantined 0, no_output 0.
  α_point = 0.24, **Wilson-95 LB = 0.1295** (the LB in results.json — note the
  coordinator brief's "LB ≈ 0.233 at n=10k" is an **[ESTIMATE]**, a projection of the
  point rate to n=10k, not a measurement; the measured n=25 LB is 0.13).
- **[MEASURED]** Wilson-95 **upper** bound on α at n=25 ≈ **0.43**. This is the decisive
  fact for the gate: even the most optimistic reading of the data sits far below the
  0.70 floor. P(observing ≤6/25 accepts | true α ≥ 0.70) is ~10⁻⁶ (exact binomial).
  The gate fails at n=25 with no possibility of rescue at n=10k.
- **[MEASURED]** The prompt fix eliminated the invalid-token failure class: 0
  ERR_PRIME/PRED/ROLE quarantines; first-pass valid among drafted 4/7 = 57%;
  post-repair 6/7 = 86% accepted-among-drafted; invalid-after-R2 = 0. The three
  first-wave failures were structural one-offs (ERR_OUTPUT_PARSE brace scan,
  ERR_REF_NOT_INTRODUCED, ERR_ENCODE_SANITY), all resolved inside the R=2 budget —
  two repaired to accepted, one honestly converted to abstention.
- **[MEASURED]** Every abstention names a specific missing concept, verified by
  inspection of the raw outputs (branch, white-coloration, hair, industrial facility,
  curved-shape/geometry, taxonomic species/genus, key/opening, specialized tool, …).
  These are coverage statements, not refusal boilerplate.
- **[MEASURED]** Strong POS gradient: nouns 1/16 accepted (6%), verbs 3/4, adjectives 1/4,
  adverb 1/1. The worklist is 68% nouns (6,766/10,000 per the sample manifest strata),
  41% mono nouns — so the noun crater dominates any representative α.

---

## Q1 — What does α ≈ 0.24 / 76% coverage-abstention mean for the SCALE thesis?

It **refutes "profile-1 suffices"** and **validates the direction** of the largekern
thesis — the kernel must be substantially bigger — but it does **not** validate the
**magnitude** ("millions of concepts"). Precision matters here because the two readings
imply different programmes:

- **[MEASURED]** Profile-1 (65 primes + 108-record ref catalog ≈ 173 nameable symbols)
  expresses roughly a quarter of representative WordNet-10k (CI [0.13, 0.43] at n=25),
  and the failure is concentrated where the frame is heaviest: specific/concrete/
  taxonomic nominal senses. That is a demonstrated coverage ceiling of the *current*
  kernel, and it is the sample frame's majority material, so it generalizes to the 10k
  (the coordinator's transport-independence claim — identical on Batch API — is taken
  as **[STIPULATED]** here; I did not re-verify it).
- **[MEASURED, structure]** The abstention reasons are not "this concept is
  inexpressible in NSM"; they are almost uniformly "profile-1 lacks a concept for X",
  where X is one or two *common concrete molecules* (branch, hair, key, white, curve,
  tool, facility) plus a residue class (taxonomic placeholders, ethnic/geographic
  proper names, physics senses) that NSM theory itself expects to be
  catalog-or-abstain material.
- The data is therefore consistent with **two very different worlds**, and cannot
  distinguish them at n=25:
  1. **Compositional world:** a few hundred–few thousand well-chosen molecules
     (body parts, colors, artifacts, biological kind anchors, geometry) unlock most of
     the noun mass compositionally → kernel of ~10³–10⁴, and the compression thesis
     lives.
  2. **Linear world:** coverage grows only ~1:1 with catalog size → the "kernel"
     converges on the whole vocabulary (~10⁶), and the compression thesis dies even as
     the scale thesis "wins" vacuously.
  **[ESTIMATE, subjective]** The shape of the abstentions — each naming 1–2 mineable,
  high-frequency concrete concepts rather than idiosyncratic sense-specific machinery —
  leans toward world 1, but that is a read, not a measurement.

So: α ≈ 0.24 is a **signpost, not a validation certificate** for "millions". The
binding variable the pilot exposed is **coverage as a function of catalog size**, and
that curve has not been measured at any second point.

## Q2 — Is n=25 decisive, or does the full 10k add real value?

Split the question, because the answer differs:

- **Decisive for the frozen gate: YES.** **[MEASURED]** Wilson-95 upper ≈ 0.43 < 0.70.
  No n=10k outcome consistent with this sample passes; running to "check" the gate
  buys nothing.
- **Decisive for the coverage NUMBER: NO.** **[MEASURED]** the n=25 CI is [0.13, 0.43] —
  a 3× range — and per-stratum cells are n ≤ 10. "Profile-1 expresses ~24%" is a point
  estimate with ±15pp of slop, and the per-POS/per-band structure (the actual design
  input for kernel expansion) is essentially unresolved.
- **What the full run buys** (**[ESTIMATE]**: ~2,400 accepted, ~7,600 abstentions,
  ~$0 Max20, ~19h at 4-way):
  1. The coverage number at ±1% **with per-stratum resolution** — which strata are
     expressible is the requirements spec for profile-2.
  2. ~2,400 real ModelDrafted records — a genuine partial kernel-v1 and the exemplar/
     molecule-mining substrate (P2 exemplar review currently blocks on having real
     passers).
  3. **The most valuable artifact:** ~7,600 abstentions each naming missing concepts —
     frequency-rank the named concepts and you have the empirical **molecule shopping
     list** for kernel expansion. n=25 gives ~19 data points of this; that is not a
     shopping list.
- **What it costs beyond $0/19h:** running it under the *frozen* prereg formalizes a
  known FAIL against an endpoint everyone now agrees measures the wrong thing (see Q3),
  polluting the registry with a campaign whose conclusion was decided before launch.
- **Middle path worth naming:** an n=500–1,000 re-scoped run resolves the coverage
  number to ±3–4pp and yields a usable abstention taxonomy in ~1–2h; the full 10k is
  justified mainly if you also want the ~2,400 records minted now.

**Bottom line:** the calibration is decisive for the *decision* (gate fails, pilot as
frozen cannot PROCEED) and indecisive for the *measurement* (coverage). The full run
has real value, but **only under a re-scoped registration**.

## Q3 — Was the α ≥ 0.70 gate mis-calibrated?

**Yes, in a precise and instructive way.** **[MEASURED, provenance]** The gate was set
against the mock drafter's pinned failure mix (mock e2e: α_LB 0.951, 9,521/10,000
accepted — README, `out/e2e-report.json`). The mock modeled **drafting-reliability**
failures (invalid AST, gloss lint, malformed output, provider transients) with
abstention as a rare stipulated class. Nobody measured real profile-1
**expressibility** before freezing — the first real-model probe used adversarial
samples with no repairs, which masked coverage behind token-validity noise.
**[STIPULATED]** the 0.70 floor therefore encodes "the pipeline mostly works", not
"the kernel mostly covers".

The recalibration cleanly separates the two quantities the single α conflated:

| quantity | value | verdict |
|---|---|---|
| **Instrument reliability** (accepted / drafted, post-R2) | **0.86** [MEASURED], 0 quarantines, 0 invalid-after-R2 | pipeline PASSES any reasonable bar |
| **Expressibility / coverage** (drafted / attempted) | **~0.24–0.28** [MEASURED, wide CI] | the actual discovery |

**The right endpoint design is two endpoints, not one:**
- **E1 (gate):** reliability among drafted — accept/drafted ≥ ~0.85, quarantine ≈ 0.
  This is what a PROCEED gate should protect (don't spend the budget on a broken
  drafter).
- **E2 (measurement):** expressibility over representative WordNet-10k, reported per
  stratum with a CI and an abstention-reason taxonomy — a **measured quantity, not a
  pass/fail gate** (or gated only against a stated downstream need).

This is a **re-scope, not a codex-transport re-freeze**. Changing the transport and
re-freezing the same α ≥ 0.70 accept-gate would re-register a question the data has
already answered in the negative. The pilot's primary question should become: *what is
profile-1's expressibility, where does it fail, and what do the failures name?* That
changes endpoint, analysis plan, and PROCEED semantics — a new registration.

## Q4 — Should α count honest abstentions?

**Report both; gate on neither alone; do not change the code's accounting.**

- α over **attempted** (current code → 0.24) is the honest **kernel-yield** metric. It
  answers the question the scale thesis actually asks — "what fraction of WordNet-10k
  becomes records under this kernel" — and it must stay the headline number. Moving
  abstentions out of the denominator *in order to pass the frozen 0.70 gate* would be
  post-hoc denominator surgery to convert a FAIL into a PASS — exactly what prereg
  discipline forbids. The gate fails; the remedy is re-scoping (Q3), not redefining α.
- α over **drafted** (0.86) is the honest **instrument-reliability** metric and should
  be promoted to a first-class, separately-named endpoint (E1 above), not smuggled in
  as "the real α".
- The abstention rate (0.76) **with its reason taxonomy** should be a first-class
  output, not residue: the reasons are the requirements data for profile-2.

Concrete recommendation to the maintainer: keep `alpha_denominator_attempted` as is;
add a named `alpha_amongDrafted` and an abstention-reasons artifact to the report
schema in the re-scoped registration.

## Q5 — Recommended path (ranked)

1. **(b)+(a) hybrid — treat the calibration as decisive for the gate; RE-SCOPE the
   pilot to a coverage-measurement + record-minting run; then run it (staged n≈1k
   sanity → full 10k).**
   *Basis:* the gate outcome is already decided at any bound the data allows
   [MEASURED]; the coverage number, the per-stratum map, the ~7,600-item molecule
   shopping list, and the ~2,400 real records all need n [ESTIMATE]; marginal cost
   ~$0 + ~19h is small against that. Re-scope first so the run formalizes a
   measurement rather than a pre-decided FAIL. This also unblocks P2 (real exemplar
   candidates) as a side effect.
2. **(c) expand profile-1 — but SEQUENCED AFTER (1), driven by the abstention corpus.**
   Expanding first means guessing which molecules matter and re-running blind. The
   right form of (c) is the *next* pilot: profile-2 = profile-1 + top-K
   frequency-ranked molecules mined from (1)'s abstentions, then re-measure. That
   run is the actual scale-thesis experiment: **coverage vs catalog size, two points
   on the curve.** If coverage jumps to 60–80% with a few hundred molecules, the
   "millions" framing is wrong and the compression thesis is alive; if it inches to
   ~30%, the kernel-must-be-huge direction is confirmed the hard way. Either outcome
   is worth far more than either single point.
3. **(a) pure run-to-formalize under the FROZEN prereg — dominated.** It spends 19h to
   confirm 0.24 ± 0.01 against a 0.70 gate that measures the wrong quantity, and books
   a formal FAIL whose only content is already in this calibration.
4. **Kill the direction — not justified.** The instrument works (0 quarantines, repair
   loop converges, abstention is honest and specific); the failure is informative and
   names its own fix.

## Subjective read (what's going well / poorly; dead-end or signpost)

**Going well:** the instrument. The closed-lexicon prompt fix removed an entire failure
class in one move; the drafter produces genuinely scholarly explications when the
kernel reaches; and — the underrated result — it **abstains honestly with specific,
mineable reasons** instead of hallucinating out-of-catalog references. A drafting
pipeline that says "profile-1 lacks a concept for a branch" is a measuring device for
kernel coverage. That is a better instrument than the one the pilot thought it was
building.

**Going poorly:** calibration order. The programme froze a semantic gate (α ≥ 0.70)
against a *mock's* reliability figure (0.951) before any real-model measurement of
expressibility existed, and the first real probe's adversarial sample + no-repair
design masked the coverage variable behind token-validity noise. Process lesson worth
persisting: **mocks calibrate plumbing, never semantics — run a tiny real-model
representative probe against any semantic gate before prereg-freeze.**

**Dead-end or signpost:** a signpost, and a cheap one. For ~$0 and n=25 the pilot
discovered the programme's actual binding variable — coverage as a function of kernel
size — and produced the method for measuring it. The largekern direction is neither
validated at "millions" nor refuted; it has been converted from a slogan into a
measurable curve, and the next two runs (re-scoped 10k, then profile-2 re-run) put two
points on it.

---
*Corrections to the coordinator brief, for the record:* (i) the measured Wilson-95 LB
at n=25 is **0.1295**, not 0.233 — the 0.233 figure is a projection to n=10k assuming
the point rate holds and should not be quoted as measured; (ii) decisiveness against
the 0.70 gate rests on the Wilson-95 **upper** bound (~0.43), which is the correct
load-bearing statistic; (iii) "first-pass valid among drafted 57%" is 4/7 — a
seven-item denominator; quote it with that caveat.
