# N-IOC-S — Sign-off record: the two I/O-compression ideas, post-census

**Kernel of Truth programme — design SIGN-OFF, node N-IOC-S.**
Author: Kern (Fable experiment-designer role, designer-1), for the maintainer.
Date: 2026-07-10. Bead: `kernel-of-truth-5iu` (this record completes its "design AND
sign off" requirement; the design half is `docs/next/io-compression-ideas.md`, node
N-IOC, 2026-07-09). Status: **SIGN-OFF document. Nothing here is pre-registered;
nothing spends money; no experiment entry is created; no frozen object is touched.**
Assumptions registered this pass: **ASM-0460…ASM-0464** (reserved block 0460–0479)
in `registry/assumptions.jsonl`. Epistemic tags as in N-IOC: [MEASURED],
[LIT-BACKED], [STIPULATED], [EXTRAPOLATION]; no EXTRAPOLATION is load-bearing.

---

## 0. What changed between design and sign-off

N-IOC was written 2026-07-09 with both ideas' cheapest evidence still unbought. Between
then and this record, the Tier-0 census family ran at ~$0 and was interpreted
(`registry/assessments/compression-census.json`, re-verified byte-identical on the
2026-07-10 interpreter pass) and the programme-level synthesis placed the results
(`docs/next/feasibility-synthesis.md` §2d). The censuses did exactly what the
K-B0/b-cov precedent promised: they settled one idea's feasibility-at-current-scope
for free, before any spend. This record therefore signs the two ideas off **on the
measured evidence**, not on the design's hopes.

## 1. The measured base this sign-off stands on

LOAD-BEARING: On TinyStories-valid (the deliberately favourable m0b continuity corpus) at the kernel-v0+molecules-v0 instance under the fail-closed v0 parser, idea-B roll-up achieves 0.399–0.444% net savings of expanded word mass (engagement 0.592–0.643%) — ~4.5–5× below the 2% K-B0 sanity floor on every cell; the dominant abstain cause is unmapped-word at 2,068,450 (an order of magnitude above the next cause); clause-AND engages 1 fragment in 405,523 sentences; the strict→permissive-det lever moves savings only ~+10% relative and is a flagged LOSSY convention; the OR-forfeit is clause 0.0000% / NP ≤0.005% [MEASURED: registry/assessments/compression-census.json; poc/compression-census/results/b-e0-tinystories.json sha256 6a1b53f98eb163c64d599d8b8b78fcc2c308139d61997c70d449a2b20b0f5286].

LOAD-BEARING: The roll-up/expansion machinery is an exact round-trip identity — 1,786/1,786 items, 0 failures, across the depth×clause-count grid, D=8192 vectors byte-identical [MEASURED: poc/compression-census/results/b-rt-roundtrip.json sha256 248cf0fd6a40d3f27cc16d608fa89ca6a968de1c71332e040a8f30730f01cd24; encoder content-hash 40e8c8ba4c3d081c5051ea62d946d2ee9ee9f3205853b5c377a4c1e647e2d10c].

LOAD-BEARING: A-E2 (idea A's own census) has NO result — it is blocked on inputs that are absent from the box: pinned per-language frequency lists, pinned host tokenizers (the only tokenizer.json present is the kb embedding model's, re-confirmed 2026-07-10), and non-English surface data [MEASURED: poc/compression-census/results/a-e2-blocker.json sha256 a558ef25ed40b25ca8442eab263f411f198a58e2ff3ab83d8ca8ea39d3e5ae19].

Envelope, carried verbatim from the assessment: every B-E0 number above is scoped to
this one corpus, this one kernel instance, and word-mass (not host-BPE) currency;
quoted outside that scope it re-classifies as EXTRAPOLATION. The ~5× floor margin is
direction-robust to the currency; the exact multiple is tokenizer-dependent
(ASM-0103, open).

---

## 2. Idea B — `idea-compositional-rollup-invented-concepts` — sign-off: **DEFER (park ratified)**

### 2.a Mechanism + the metric it would move

As designed in N-IOC §3 (unchanged): deterministic parse of maximal parseable
explication fragments → content-hash URN → construction-B composite vector → X4 → one
soft token through the E5/A2 adapter; system-side exact-by-id dictionary for lossless
expansion. **Metric:** corpus prefill-token savings = engagement × avg per-span
savings, at accuracy non-inferiority (X1 framing: efficiency endpoint only). That
metric is now measured at current scope: **~0.4% of word mass**, against a 2% floor.

### 2.b The differentiation question, inverted: does the design escape its own wall?

For idea B the bead's differentiation question is reflexive — it *is* the parked
idea — so the honest form is: does any lever inside the design escape the measured
vocabulary-coverage bound? The census answers lever by lever:

| Lever inside idea B | Measured reach | Escapes the wall? |
|---|---|---|
| Parse permissiveness (strict→permissive-det) | +~10% relative, and LOSSY (ineligible for the lossless claim) | No — off-target: the gap lives in unmapped-word, not parse conventions |
| Grammar extension (add OR) | forfeit ≤0.005% of mass | No — an ALGORITHM_VERSION bump buys nothing measurable |
| Pattern scope (the maintainer's flagship clause-AND) | 1 fragment / 405,523 sentences | No — conjunctive engagement is the wall's steepest face |
| Roll-up machinery quality | 100% exact (B-RT) | Not the constraint — nothing is broken |
| Vocabulary coverage (unmapped-word 2.07M abstains) | the binding constraint | **Only escape route — and it is exogenous to idea B** (it is idea A's and the haiku-tier mint track's lever) |

Conclusion: idea B cannot self-rescue. A ~5× gap with a ~10%-reach internal lever set
is not a design-iteration problem; it is a coverage problem owned by other tracks.

### 2.c Cheapest-first evidence

Already bought: B-E0 + B-RT ran at ~$0 and were decisive — this is the census
precedent working as intended, and no further evidence purchase is needed to sign
off. Remaining $0 instruments (none blocking, none a rescue): the second-corpus
negative-completion (expected direction down; strengthens, cannot flip); host-BPE
re-denomination of the existing spans once the R1 tokenizer is pinned (dual-use with
A-E2, resolves ASM-0103); the standing re-entry census below.

### 2.d Verdict

DECISION: idea-compositional-rollup-invented-concepts is signed off as **DEFER** — the census assessment's interpretive PARK is ratified as the design-side ruling: no B-E1 consumption experiment is designed or run, no OR grammar extension, no B-F1 composite-bridge training, while the park holds; B-E1 now would spend Tier-2–3 money measuring a mechanism whose engagement is coverage-capped at ~0.6% by construction [STIPULATED: ASM-0460] [MEASURED: registry/assessments/compression-census.json].

Why DEFER and not REJECT: a reject would overclaim beyond the measured envelope — the
machinery is exact (B-RT 100%), the negative is scoped to one corpus and one kernel
instance in word-mass currency, and the binding constraint is the one quantity the
programme is actively growing. Why DEFER and not PURSUE: the park's own kill text
(K-B0) fired interpretively at ~5× margin on the *most favourable* corpus, and §2.b
shows no internal lever with the reach to close it.

**Re-entry gate (the one design artefact this sign-off adds for B):** trigger = any
coverage-growth wave that materially changes the mapper lexicon (haiku-tier mint
wave, a minted kernel-A, a molecules rung change); action = re-run B-E0 with the same
instrument, host-BPE denominated once pinned; un-park iff achievable corpus savings
clears the freeze-time K-B0 floor (2% sanity default until a freeze resets it); an
un-park re-opens B-E1 *design* only — execution still needs its own prereg, F3 gates,
and maintainer spend-ack [STIPULATED: ASM-0460].

---

## 3. Idea A — `idea-crosslingual-phrase-coverage-io-compression` — sign-off: **PURSUE at Tier-0, census-first**

### 3.a Mechanism + the metric it would move

As designed in N-IOC §2 (unchanged): coverage-maximising cross-lingual selection under
the expected-token-savings objective value(c) = Σ_ℓ w_ℓ · Σ_s f_ℓ(s)·(bpe_ℓ(s)−1)·m̂(s,ℓ),
minted cheaply via the cached-prefix Haiku definer into the modelAuthored tier, consumed
through the L1b/F3 seam. **Metric:** the achievable prefill-token-savings curve vs
number of concepts minted (host-BPE denominated, per language and blended) — A-E2's
deliverable and the K-A2 gate; downstream, the full cost/accuracy Pareto vector at F3
with accuracy as a non-inferiority co-primary.

### 3.b Differentiation from the parked idea B

DECISION: idea A is ruled DIFFERENTIATED from the parked idea B — the census does not dominate it — on the grounds that (i) it moves the exact quantity B-E0 measured as the binding constraint (vocabulary coverage: A mints NEW mappable vocabulary, the very lever the park names as B's re-entry route), (ii) its engagement is structurally per-span/disjunctive — one covered surface saves (bpe−1) tokens regardless of its neighbours — where B's was conjunctive over whole fragments (the structure that collapsed 0.354 membership to ~0.006 proposition engagement), (iii) its value axis (cross-lingual BPE fertility) has zero measurement in B-E0, which was English word-mass only, and (iv) the one thing that DOES carry over from B-E0 is a caution, not a domination: mappability m̂ is the measured binding term on covered English, so K-A4 (mappability collapse under polysemy) is priced up front by making m̂-weighted cells mandatory in A-E2 [STIPULATED: ASM-0460] [MEASURED: registry/assessments/compression-census.json idea_a_a_e2_read + licenses].

The domination check against the null family is also unchanged by the census: the
tokenizer-vocabulary-extension null (K-A3) and the trained-compressor null (K-A4/HE3
lineage) are *consumption-stage* kills — they can defeat idea A later, but no existing
measurement stands in for A-E2's $0 selection-value curve, and a strong null one rung
downstream is not a reason to skip a free census one rung upstream.

### 3.c Cheapest-first evidence: unblock and run A-E2 (Tier 0, ~$0)

A-E2 is idea A's live-or-die number (the K-A2 gate) and is CPU-only once its inputs
exist. The census assessment boundary-stopped on the input design choices; this
sign-off, as the design role the boundary-stop names, discharges them:

DECISION: A-E2 inputs are pinned as follows — frequency source = the wordfreq-lineage aggregated per-language frequency lists, sha256-pinned at fetch with URL+version in a committed manifest, fail-closed on provenance; census languages = en (anchor; the only m̂-sampled cell) + es + fi + ja (spanning the BPE-fertility axis: moderate-fertility Latin, extreme morphological fertility, non-Latin script); w_ℓ = uniform primary + usage-share sensitivity; tokenizers = SmolLM2-135M tokenizer.json (mandatory R1) + one R4-family tokenizer.json; non-English cells run membership-only (m̂=1 upper bound, disclosed per cell, K-A4 unpriced there); and the fetch itself is ruled in-scope of the bead's existing maintainer Tier-0 clearance once pinned this way, executed by the coordinator with the maintainer veto standing [STIPULATED: ASM-0461].

DECISION: the A-F1 cross-lingual-alignment fork is DEFERRED out of A-E2 under an exact bracketing convention — per-language unaligned curves are a LOWER bracket of aligned value at fixed budget, the cross-language sum is an UPPER bracket, K-A2 may fire only off the upper bracket, a go may rest only on the lower bracket, and a between-brackets landing forces A-F1 design before any mint decision [STIPULATED: ASM-0462].

### 3.d Ordering and spend gates (tightened from N-IOC §4.2)

DECISION: the compression track runs strictly cheapest-decisive-first — A-E2 first ($0, after the ASM-0461 fetch); A-F0 (the maintainer-flagged symbolic-output fork sub-test, ~$5–10, already cleared) only AFTER the A-E2 readout, but A-F0 survives a K-A2 fire because cached-prefix mint economics serve the whole coverage-growth track (idea B's re-entry lever and the linter's staircase), not idea A alone; A-E1 (~$20–40) requires A-F0's verdict AND a live selection target that did not fire K-A2 AND maintainer spend-ack; A-E3/B-E1 stay behind F3's gates (B-E1 also behind the §2.d un-park); and nothing on this track may displace the feasibility-synthesis §5 critical path [STIPULATED: ASM-0463].

### 3.e Verdict

DECISION: idea-crosslingual-phrase-coverage-io-compression is signed off as **PURSUE at Tier-0 now** — differentiated per §3.b, not dominated by any existing measurement, with its decisive number ($0) unbought and its first two evidence rungs (A-E2, then A-F0) already inside the maintainer's standing clearance; all Tier-1+ spend remains gated per §3.d [STIPULATED: ASM-0460].

Expectations, sizing only, never a premise [EXTRAPOLATION: ASM-0464]: the value curve
is expected to concentrate in non-English cells (English high-frequency words are
often already one BPE token; the fertility-asymmetry literature note in N-IOC remains
memory-tagged and unverified), and m̂-weighting is expected to discount the most
polysemous strata materially (direction from B-E0's abstention profile). A-E2
measures both directly on our pinned tokenizers; K-A2 and K-A4 can honestly fire, and
either firing is a publishable negative per the directives.

---

## 4. Hand-off (coordinator actions; none performed by this record)

1. **Register/idea records:** append superseding `registry/ideas.jsonl` lines for both
   ideas reflecting this sign-off (A: signed-off, pursue-Tier-0, blocked_on the
   ASM-0461 fetch; B: signed-off, parked/defer, blocked_on the §2.d re-entry gate) —
   idea-line appends are coordinator-central per the N-IOC convention.
2. **KB healing:** this file is a new `docs/**/*.md`; `kb-sync-internal` was NOT run
   here per lane rules — the expected `ERR_KB_INTERNAL` regeneration finding is
   DEFERRED to the coordinator heal.
3. **Bead:** `kernel-of-truth-5iu`'s design+sign-off requirement is now complete
   (design = N-IOC, sign-off = this record); close or update per coordinator
   workflow. The a-e2-tokenizer-unblock and a-e2-frequency-corpus-signoff stubs in
   the census assessment are discharged by ASM-0461.
4. **Commit:** changed files are `registry/assumptions.jsonl` (ASM-0460…0464,
   append-only) and `docs/next/io-compression-signoff.md` (new). No git was run in
   this lane.

*Cross-references:* `docs/next/io-compression-ideas.md` (N-IOC, the design half);
`registry/assessments/compression-census.json` (the measured base + its envelope);
`docs/next/feasibility-synthesis.md` §2d + §5; `registry/verdicts/m0b.json` (coverage
envelope); `data/d-ext/manifest.json` (membership ≠ engagement);
`docs/kernel-design-directives.md` §§2, 4, 6, 7.
