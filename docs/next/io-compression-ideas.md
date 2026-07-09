# N-IOC — The two I/O-compression ideas: cross-lingual phrase coverage + cheap-mint, and compositional roll-up into invented concepts

**Kernel of Truth programme — design proposal, node N-IOC.**
Author: Kern (Fable design agent), for @jeswr. Date: 2026-07-09.
Bead: `kernel-of-truth-5iu`. Idea records: `idea-crosslingual-phrase-coverage-io-compression`
(= **idea A**) and `idea-compositional-rollup-invented-concepts` (= **idea B**) in
`registry/ideas.jsonl`; the fleshed entries appended with this document supersede the
2026-07-09 stubs per last-line-wins.
Status: **DESIGN/PLANNING document. Nothing here is pre-registered; nothing spends
money; no experiment entry is created.** Everything proposed becomes real only through
the existing rails (research-engine candidate template → `prereg-freeze`; maintainer
sign-off; margins fixed at freeze, shapes fixed here). Binding constraints:
`docs/kernel-design-directives.md` (§1 no-semantic-web-legacy, §2 two value theses +
full metric vector V, §4 don't-guess-test, §6 honest stats);
`reports/lit-llm-injection-priorart.md` (Laws 1–3); `idea-ast-input-injection-boundary`
(X1). Epistemic tags: **[MEASURED]** (registry verdict / committed data),
**[LIT-BACKED]** (verified at source or in a repo lit-report), **[verified 2026-07-09]**
(checked against live documentation this pass), **[memory]** (author knowledge,
unverified — never load-bearing), **[STIPULATED]** (design choice or planning constant),
**[EXTRAPOLATION]** (hope, not premise). No EXTRAPOLATION is load-bearing.

---

## 0. The maintainer's ask, and the one-paragraph answers

**Ask (2026-07-09), two ideas, both on the EFFICIENCY thesis (directives §2B):**
(A) mint concepts for the highest-frequency words/phrases *across languages* so the
encoder compresses LLM input into few dense concept tokens and the decoder expresses
high-bandwidth content in few tokens, with definitions generated cheaply by a Haiku
concept-definer whose entire context is cached and only the single word varies;
(B) have the encoder statically roll up recognisable compositional structure
("a is b", "a AND b", "a OR c") into single *invented* composite concepts whose vectors
are deterministically derived from their parts, with a per-utterance dictionary letting
the decoder expand them losslessly. Explicit: do NOT build yet; design first.

**Answer for A in one paragraph.** The cheap mint is real and mostly an engineering
change to the pipeline the repo already has: move the volume runner from `claude -p` to
direct `claude-haiku-4-5` API calls with the entire how-to-define context (instructions
+ closed grounding lexicon + trap list + ref catalog + exemplars) as a byte-stable
cached prefix, keep the measured-best gate-in-the-loop repair (framework G, 31.7%
gate-pass of attempted, 26% concept yield, ~$0.0202/concept [MEASURED
`data/haiku-tier/s1-experiments/s1-report.md`]), and the input side of every call drops
~10× on cache hits (~2× more with the Batch API) — a worked estimate of roughly
**$0.006–0.012/concept**, i.e. ~2–3× cheaper per legal record, *before* any yield
improvement — and yield, not caching, remains the bigger lever. The selection question
is sharper than "highest frequency": the objective must be **expected token savings**
(frequency × (host-BPE tokens − 1) × mappable-sense probability, weighted across
languages), because high-frequency English words are often already one BPE token
(savings ≈ 0) while the cross-lingual win concentrates exactly where BPE fertility is
high. The maintainer-flagged FORK (does directly-symbolic output cut tokens or
paradoxically increase thinking-time?) gets a decisive ~$5–10 sub-test, A-F0, defined
in §2.3 with its decision rule pre-shaped. Everything the minted kernel is *for* — the
actual compression — is measured on the existing L1b/F3 seam against the Law-2 null
family plus one new null this idea makes mandatory: **tokenizer-vocabulary extension**
(same phrases as literal new tokens), which is the cheapest competitor for the same
token savings.

**Answer for B in one paragraph.** The binding algebra already supports exactly two of
the three maintainer-named patterns, and the design says so plainly: **clause
conjunction ("a AND b") is native** (an explication is an ordered clause list,
deterministically superposed with position permutations — a two-clause roll-up is just
`encodeExplication` of the two-clause AST), **"a is b" is native** for the closed
grammar's kind/part frames and equative clauses, and **"a OR c" is not expressible at
v0** — the closed operator inventory (`encoder/src/lexicon.ts`: NOT, CAN, MAYBE, IF,
BECAUSE, WHEN, LIKE, AFTER, BEFORE, VERY, MORE) contains no OR, and paraphrasing
disjunction via MAYBE changes the semantics; adding OR is an encoder version change
gated on a *measured* need (B-E0 counts what the missing operator forfeits). Invented
composites are minted deterministically: canonical AST → content-hash URN
(`docs/design-hash-input.md`, so identical composites dedupe globally) → construction-B
vector (zero training) → X4 projection → one soft token through the E5/A2 adapter (the
only Law-1-supported topology). The decoder's invented-concept dictionary is
**system-side and exact-by-id** — it never enters the LLM context (or the savings
invert) and involves no cosine step (X3-compliant); symbol-level round-trip is exact by
construction and guarded by a Tier-0 property suite, so the real risks are parse
engagement on real text (measured in the B-E0 census) and whether the composite vector
carries content through the trained bridge (the B-E1 arms). Per **X1 the idea is framed
exclusively on compression/efficiency**: primary endpoints are tokens/FLOPs/latency at
accuracy *non-inferiority*; accuracy-superiority claims from structure are banned at
pre-registration; and the decisive incremental null is **L1b-flat** — per-concept
tokens without roll-up — because a roll-up that only matches flat concept tokens has
added nothing.

---

## 1. The shared constraint frame (binding on both ideas)

### 1.1 Value thesis and the X1 asymmetry

Both ideas live on the **efficiency thesis only** (directives §2B): fewer LLM tokens in
and out ⇒ cheaper inference at acceptable accuracy. Neither may claim accuracy value:

- Idea B is *hard-bound* by `idea-ast-input-injection-boundary` (X1) [LIT-BACKED
  arXiv:2602.06671 parity; arXiv:2505.12118 no-transfer]: handing an LLM structure over
  content it can already read is accuracy-parity, and structure-analysis pretraining
  does not transfer in. Every B pre-registration therefore declares accuracy as a
  **non-inferiority co-primary (TOST)**, never a superiority endpoint; a
  structure-as-text arm is included as an expected-parity *control*, never a candidate.
- Idea A is not X1-bound (it injects *content*, not structure), but its accuracy
  endpoint is still non-inferiority: the compression claim dies if the compressed arm
  loses accuracy beyond margin, and any accuracy *gain* is reported descriptively only.

### 1.2 Law 1 — interface locality, and what the trained bridge costs

The only supported injection topology is kernel vectors through a small trained adapter
into a trained host (E-BERT/A2 protocol) or kernel values addressed by model-native
keys [LIT-BACKED `reports/lit-llm-injection-priorart.md` §3]. Both ideas use the first:
X4 projection (8192→512/576, distortion measured [MEASURED X4]) through the E5 adapter
(nonce-concept content transfer +28.5 pp over shuffled at R1 [MEASURED E5]). The tolls,
priced in every cost account below:

1. **One-time**: adapter training (E5-class configs were 3–6 GPU-h; idea B may need a
   composite-trained bridge — fork B-F1). Amortized over query volume on V.
2. **Per-query**: mapper parse (CPU, µs–ms), X4 projection + one adapter matmul per
   concept token (negligible vs saved prefill FLOPs).
3. **The real toll — fidelity**: content through a trained bridge has a measured
   ceiling in the adjacent literature (xRAG retains ~62–73% of giving the model the
   text [LIT-BACKED, carried]). This is why accuracy non-inferiority is a co-primary
   and why the honest expectation is an accuracy *tax* that must stay within margin at
   a compression level that matters.

### 1.3 Law 2 — the null family, specialised for compression

The generic Law-2 null (same kernel content as text at matched budget) is necessary but
not sufficient here, because for a *compression* claim the kernel-as-text arm typically
*adds* tokens. The pre-registered null family for any consumption experiment:

| Null | What it kills |
|---|---|
| text-only baseline | everything (the do-nothing arm) |
| kernel-as-text at matched budget (Law 2) | "the vector interface adds value beyond its content" |
| matched-token trained compressor (LLMLingua/gist-class; HE3's existing kill) | "deterministic concept tokens beat learned compression" |
| **tokenizer-vocabulary extension** (idea-A-specific, §2.5) | "concept tokens beat plain new tokens for the same phrases" |
| **L1b-flat concept tokens** (idea-B-specific, §3.5) | "roll-up beats per-concept tokens" |
| shuffled-kernel / shuffled-composite (E9-defl discipline) | "the effect is content-carried at all" |

### 1.4 The LCM/CALM fixed-semantic-IO penalty

The standing caution [P8 anchor row; L3 §4 row 11]: fixed semantic spaces as prediction
targets paid a scaling-exponent penalty (SONAR-LLM α≈0.49–0.57 vs 0.79 token), and CALM
recovered step-compression by dropping fixedness. Both ideas are **edge instantiations
only**: frozen hosts, adapter-only trained parts, the model's internal computation and
next-token objective untouched. Consequences, binding:

- No scaling-exponent claim is in scope for either idea at v0. Any escalation that
  trains beyond the adapter triggers L1b's tripwire (≥3-rung exponent comparison) and
  inherits the L2c φ-knob discipline (`docs/next/architecture-ladder.md` §4.3).
- Idea A *raises coverage κ*, which pushes the effective input-edge fixedness up; the
  φ-semantic-fixedness sweep (L2c) is the instrument that licenses or retires that
  concern — A does not need to re-run it, only to report κ per cell.

### 1.5 The accounting identity (the shape every cost claim must take)

For a workload of N queries on host rung R with per-token prefill price p:

```
net_savings/query = Σ_covered-spans (t_span − c_span) · p        [t = text tokens, c = concept tokens]
                  − CPU(mapper + encode + project + render)       [µs–ms class; measured, expected negligible]
                  − (adapter_training$ + mint$ + authoring$) / N  [amortized; on V's authoring component]
corpus-level      = engagement × avg per-span savings             [engagement measured by census, never assumed]
```

Both ideas' first decisive number is therefore a **Tier-0 census** (m0b/b-cov pattern:
deterministic, CPU-only, pinned corpora + pinned tokenizers, envelope verbatim). The
coverage-disclosure discipline applies to every reported cell: the m0b anchor is
0.3542 content-token mass at molecules-v0 (kernel-v0 0.2210; wn31 membership band
0.7841 — membership, never explicated coverage) on one pinned corpus [MEASURED
`registry/verdicts/m0b.json`], and the d-ext lesson (≈49% lemma-touch coexisting with
0% checkability [MEASURED `data/d-ext/manifest.json`]) generalises here as:
**vocabulary membership ≠ mappable/parseable engagement** — the censuses measure the
latter.

### 1.6 Where the ideas sit architecturally

Neither idea is a new ladder rung. Both are **feeders of the L1b seam** (concept-dense
I/O, F3/HE3 DRAFT): idea A raises κ (how much text *can* enter as concept tokens, and
in how many languages); idea B raises compression-per-span (how many tokens one concept
token replaces). Their consumption experiments are arms *within* the L1b/F3 harness and
must not double-claim its result. `ladder_ref: in-tokenisation-normalisation` stands.
Shared components with the precision linter (N-PL): the mapper parse front-end and the
deterministic record→text renderer — B's dictionary expansion and the linter's rewrite
mode are the **same renderer artefact** (`docs/next/kernel-precision-linter.md` §8.2).

---

## 2. Idea A — cross-lingual phrase coverage + cached-context Haiku concept-definer

### 2.1 The selection design: maximise expected token savings, not frequency

**The objective.** For candidate concept c with surface forms s in language ℓ:

```
value(c) = Σ_ℓ w_ℓ · Σ_{s ∈ surfaces(c,ℓ)} f_ℓ(s) · (bpe_ℓ(s) − 1) · m̂(s,ℓ)
```

- `f_ℓ(s)`: relative frequency from **pinned** per-language corpora/frequency lists
  (candidate sources: aggregated frequency lists of the wordfreq lineage, Leipzig
  corpora, OSCAR/CC-100 slices [memory — exact sources pinned with hashes at candidate
  time, per the d-ext provenance discipline; fail-closed on provenance]).
- `bpe(s)`: token count of the surface under the **host tokenizer(s)** — pinned per
  rung (R1 SmolLM2 tokenizer mandatory; one R4-family tokenizer for the extension
  predicate). This term is what makes the objective honest: a high-frequency English
  word that is already one BPE token contributes zero, while multi-token words and
  phrases — and above all non-English surfaces, where English-centric BPE fertility is
  known to run severalfold higher [memory — the fertility-asymmetry literature must be
  verified at source before any prereg premise; the census measures it directly on our
  pinned tokenizers regardless, which is the load-bearing number] — contribute most.
- `m̂(s,ℓ)`: estimated **mappable** occurrence fraction — the probability the
  deterministic mapper can resolve the surface to this concept without abstaining.
  High-frequency words are the most polysemous; a concept whose surfaces the mapper
  must always abstain on has membership but no engagement (the d-ext lesson, §1.5).
  Estimated by sampling occurrences and running the mapper's ambiguity policy; refined
  by the census.
- `w_ℓ`: language weights — a maintainer/product decision (usage-share or uniform),
  declared at freeze, sensitivity-analysed (workload-mix discipline, ladder §8 item 13).

**Cross-lingual identity.** One concept = one URN = one vector, with per-language
surface lexemes attached as mapper data. This is the kernel's structural edge over the
tokenizer-extension null (§2.5): a new BPE token buys savings in one surface form; a
concept row covers every language's surfaces at zero marginal trained parameters.
Alignment across languages (which Wiktionary translation/sense links, how sense splits
differ per language) is fork **A-F1**; the abstain-on-ambiguity mapper policy is
inherited unchanged — misalignment surfaces as abstention, never as a silent wrong map.

**Scope honesty (v0).** The mapper is English-only today (`a1-hybrid`, Phase M).
v0 scoping: selection is cross-lingual (the *choice* of what to mint uses all-language
value), but consumption/census runs in English + 1–2 pilot languages chosen for
tokenizer-fertility contrast [STIPULATED — pilot languages named at freeze].
Per-language mapping infrastructure (lemmatisation, surface tables) is authoring labour
and goes on V.

**Output tier.** Minted records land in the existing `modelAuthored` provenance tier
(below Explicated and hand-authored Molecule; `data/haiku-tier/` honesty architecture),
gated by the real validators. This is an **alternative kernel** (coverage-maximising)
alongside molecules-v0 — kernel arms are compared, not merged, in any consumption
experiment.

### 2.2 The cheap-mint mechanism: fixed cached prefix + single-word variable

**Baseline to beat [MEASURED, s1-report]:** framework G (gate-error-fed repair) —
31.7% gate-pass of attempted records, 13 legal records/50 concepts (26% yield),
~1.8 calls/concept in the volume runner, $0.0202/concept ⇒ ≈ **$0.078/legal record**,
via `claude -p` with a pinned call configuration.

**The redesign.** Replace the CLI path with direct Messages-API calls to
`claude-haiku-4-5` (a **pipeline version change** — the pinned call configuration is
part of pipeline identity, per s1 conventions), structured for prompt caching:

- **Cached prefix (system blocks, `cache_control: {type:"ephemeral"}` on the last):**
  the full how-to-define instruction (framework-G prompt), the closed grounding
  lexicon, the trap list, the ref catalog (kernel-v0 + molecules-v0 depth ≤ 3 +
  accumulated haiku-tier), and the few-shot exemplars — serialised
  **deterministically** (sorted; catalog version pinned per wave). Everything volatile
  goes after the cache breakpoint.
- **Variable suffix (user turn):** the single target word — plus, under fork A-F2(b),
  its pinned fetched sources.
- **Repair call:** same cached prefix + the draft + the real validator error list
  (framework G unchanged) — also a cache hit on the prefix.

**Caching mechanics that bind the design [verified 2026-07-09 against live API docs]:**
Haiku 4.5 is $1.00/MTok input, $5.00/MTok output; cache reads ≈0.1× input
($0.10/MTok); cache writes 1.25× for the 5-minute TTL ($1.25/MTok; 2× for 1-hour);
the **minimum cacheable prefix on Haiku 4.5 is 4096 tokens** (shorter prefixes silently
don't cache — ours is far above); caching is a strict prefix match, so **any byte
change in the catalog invalidates the cache** — catalog updates happen only at wave
boundaries; concurrent identical-prefix requests all miss until the first response
begins streaming — the runner fires one call, awaits first token, then fans out at its
(already low) fixed concurrency; the Batch API gives a further 50% discount on all
token usage and supports caching. The volume runner's sustained call rate keeps the
5-minute cache warm between calls; idle gaps > TTL either re-warm via a `max_tokens: 0`
pre-warm request or eat one re-write.

**Fork A-F2 — what varies per call:**
*(a)* word-only (maximal caching; relies on Haiku's parametric knowledge of the word —
cheapest, but weakens the source-pinning provenance story and risks sense
hallucination); *(b)* word + pinned Wiktionary/Wikipedia extracts (current pipeline;
~1–2k uncached tokens/call; keeps provenance). *Decided by:* A-F0/A-E1 measure both;
the decision weighs $/legal record against a fidelity spot-audit on the hand-authored
overlap set. *Kill per arm:* (a) if its records show sense errors the gate cannot catch
(human audit), (a) is dead regardless of price — provenance is part of the honesty
architecture, not a preference.

**Worked cost estimate [STIPULATED sizing; prices verified 2026-07-09; re-measured in
A-E1 before any volume authorization].** Prefix ~30k tokens; word-only variable ~50–300
tokens; output ~250–600 tokens/call. Per concept at ~1.8 calls: cache-read input
≈ 54k tokens ≈ $0.0054 + variable ≈ $0.0005 + output ≈ 1k tokens ≈ $0.005 ⇒
≈ **$0.011/concept** interactive, ≈ **$0.006/concept** via Batch — vs $0.0202 measured.
At the current 26% yield: ≈ $0.023–0.042/legal record (vs $0.078). At a 10k-legal-record
target: roughly **$230–420** all-in mint cost (source-fed A-F2(b) adds ~$1–2/1k
concepts). Two honesty notes: (i) the *yield* term dominates — a gate-pass improvement
from 26%→40% saves more than all caching combined; caching is the multiplier, not the
headline; (ii) none of these numbers is a premise — A-E1 measures them.

### 2.3 A-F0 — the decisive sub-test for the maintainer's FORK (symbolic output vs thinking-time)

**The fork, stated precisely.** A "directly symbolic" output (the `kot-ast/1` record —
or a KOTK-compact serialisation of it — with no surrounding prose) minimises output
tokens *if the model can emit it directly*. The maintainer's worry: models often buy
correct formal output with reasoning; with thinking disabled that reasoning either
leaks into the output (verbose JSON, comments, prose-first drafts), degrades gate-pass
(⇒ more repair calls ⇒ the savings invert), or — with thinking enabled — shows up as
billed thinking tokens and latency. All three failure shapes are measurable cheaply.

**Design (Tier 0–1, ~$5–10, one wave, no model training).**
n = 60 concepts, stratified across inventory bands + the 15 hand-authored-overlap
concepts (fidelity anchors), identical across arms. Arms (all framework-G
gate-in-the-loop, pinned config):

| Arm | Output form | Thinking |
|---|---|---|
| a | current G output (JSON record + minimal frame) | off (no `thinking` param) |
| b | **direct-symbolic**: record only, compact serialisation, zero prose | off |
| c | = b | on, small budget (`thinking: {type:"enabled", budget_tokens: 1024}` — Haiku 4.5 uses the budgeted config; the `effort` parameter is unsupported on Haiku [verified 2026-07-09]) |
| d | = a | on, same budget (controls "does thinking help at all", isolating output-form from thinking effects) |

**DVs (all mechanical):** output tokens/call and thinking tokens (billed as output);
wall latency and time-to-first-token per call; gate-pass rate of attempted records
(real validators, `gates.mjs`); parse-fail rate; calls/legal record; **end-to-end
$/legal record** (the decision variable); fidelity spot-check on the 15 overlap
concepts.

**Pre-shaped decision rule (margins at freeze):** adopt
`argmin $/legal-record` subject to (i) gate-pass not below arm (a) beyond margin and
(ii) no fidelity regression on the overlap set. **The paradox is detected as:** arm (b)
cuts output tokens vs (a) but its $/legal record or latency is ≥ (a) — i.e. the token
saving is eaten by repair calls (hidden reasoning shortfall) — or arms (c)/(d) beat
(b)/(a) only by spending more thinking tokens than the symbolic form saves. Either
finding resolves the maintainer's fork with numbers, in one afternoon, before any
volume spend.

### 2.4 What idea A is *for* — the consumption seam (no new experiment surface)

The minted kernel's compression value is measured on **L1b/F3** (concept-dense input;
Tier 3 cap already drafted): covered spans → X4-projected, adapter-bridged concept
tokens; DVs = full V with FLOPs split prefill/decode. Idea A adds to that harness only:
(i) an **alternative-kernel arm** (kernel-A vs molecules-v0 at matched arm structure) —
does coverage-maximising selection beat definition-first selection *per dollar of
prefill saved*; (ii) the per-language cells from the pilot languages; (iii) the κ
covariate reported per cell. No claim of idea A's may bypass F3's existing kills
(matched-token trained-compressor parity kills; the E5/HE3 discipline).

### 2.5 The nulls idea A must beat

1. **Mint-side null:** the current s1-G pipeline ($0.078/legal record [MEASURED]).
   The cached-prefix definer must beat it on $/legal record at non-inferior gate-pass
   and fidelity. A secondary priced arm: a Sonnet-class definer (higher $/call, maybe
   higher yield) at small n — cheap to price, honest to include [STIPULATED arm].
2. **Consumption-side nulls:** the §1.3 family, with the **tokenizer-vocabulary
   extension null** mandatory: add the same selected phrases as literal new tokens with
   trained embedding rows (embedding-only training, host otherwise frozen). It buys the
   *same token savings* by the same mechanism; if it matches accuracy at equal savings
   and lower total cost, the kernel's definitional content adds nothing on this
   endpoint and only the cross-lingual-sharing and zero-per-item-training properties
   remain — which are then priced explicitly (one embedding row per surface form per
   language vs one concept row total), not asserted.

### 2.6 Cost accounting end-to-end (survival of the trained bridge)

Per §1.5: savings/query = κ_A × avg(t_span − 1) × p, with κ_A the *mappable* coverage
of the A-kernel on the workload (A-E2's number, not m0b's). Overheads: mapper +
projection + adapter matmul (negligible, measured); amortized adapter training
(E5-class, one-time; possibly zero if the E5 bridge transfers — A rides the same seam);
amortized mint cost (§2.2 — at $0.03/legal record and 10k concepts, $300 amortizes to
noise over any realistic query volume; authoring cost still reported on V per
directives §2). The Law-1 fidelity toll is the accuracy non-inferiority co-primary in
every consumption cell. **Break-even is a curve, not a number**: A-E2 delivers
savings-vs-mint-budget curves per language, and the maintainer picks the operating
point at sign-off.

### 2.7 Evaluation plan (candidate-shaped; nothing frozen)

- **A-F0 — the fork sub-test (Tier 0–1, ~$5–10).** §2.3. First; gates A-E1.
- **A-E2 — cross-lingual savings census (Tier 0, ~$0, r0-local-cpu; now-eligible).**
  Deterministic, no model calls. Pinned multilingual corpora × pinned tokenizers:
  compute the value(c) ranking, then the **achievable prefill-token-savings curve vs
  number of concepts minted**, per language and blended, under (i) membership and (ii)
  sampled mappability m̂. Deliverable = the go/no-go instrument for volume minting and
  the empirical fertility-asymmetry measurement (replaces the [memory] literature
  claim with our own number).
- **A-E1 — mint-economics pilot (Tier 1, ~$20–40).** One 500-concept wave with the
  A-F0-winning configuration; measure $/legal record, gate-pass, cache-hit rates (from
  API `usage` fields — `cache_read_input_tokens` verified nonzero, the silent-invalidator
  check), Batch-vs-interactive delta, fidelity spot-audit. Gated on A-F0 + maintainer
  sign-off (spend rule).
- **A-E3 — consumption (Tier 2–3, rides the F3 cap).** §2.4. Gated on F3's own gates.

**Pre-shaped kills (margins at freeze):**

- **K-A1 (mint economics):** A-E1 $/legal record not better than the s1-G baseline
  beyond margin, or fidelity audit fails ⇒ the cached-prefix definer is dead; volume
  minting continues on the existing pipeline or not at all.
- **K-A2 (selection worthless):** A-E2 shows corpus prefill savings below the floor at
  any affordable mint budget (sanity default: <5% blended prefill savings at 10k
  concepts [STIPULATED; reset at freeze]) ⇒ the coverage-maximising kernel does not pay
  for itself; record the curve as the negative.
- **K-A3 (vocabulary-extension parity):** in A-E3 the tokenizer-extension arm matches
  accuracy at equal token savings and lower total cost, and the cross-lingual-sharing
  premium (priced per §2.5) does not close the gap ⇒ the kernel adds nothing on this
  endpoint; publishable negative per directives §7.
- **K-A4 (mappability collapse):** m̂-weighted engagement so far below membership that
  effective κ_A is under the floor (the d-ext failure mode recurring at selection
  level) ⇒ selection must be redone against mappable occurrences or the idea narrows to
  low-polysemy strata.

### 2.8 Epistemic status and readiness

**EXTRAPOLATION** end to end; `premise_eligible: false` stands. Measured anchors:
s1-G economics and failure modes; m0b coverage (with envelope); E5 nonce PASS; X4
distortion. Verified-this-pass: Haiku pricing/caching mechanics (§2.2). [memory] items
that must be verified at source before any prereg leans on them: BPE fertility
asymmetry literature; wordfreq-lineage source suitability. Readiness: A-E2 and A-F0 are
**now-eligible** (Tier 0–1, no infra gates); A-E1 gated on A-F0 + sign-off; A-E3 gated
on F3. Nothing in idea A blocks on, or is blocked by, idea B.

---

## 3. Idea B — compositional roll-up into invented composite concepts

### 3.1 Which patterns are safely + deterministically roll-uppable (the concrete answer)

Ground truth is the closed grammar (`kot-ast/1`; operators in
`encoder/src/lexicon.ts`; frames per gist §4.6):

| Maintainer pattern | v0 status | Mechanism |
|---|---|---|
| **a AND b** | ✅ native | Conjunction is clause **sequencing**: an explication is an ordered clause list; the encoder superposes clauses under deterministic position permutations. Rolling up "a AND b" = building the 2-clause AST and calling `encodeExplication`. No new machinery. |
| **a is b** | ✅ native (scoped) | The kind/part frames (`X is a kind of Y` via `KindPartHead`) and equative/specificational clauses within the closed predicate frames. Exactly the parseable subset; anything outside the frames **abstains** (never approximates). |
| **a OR c** | ❌ not at v0 | The closed operator inventory is {NOT, CAN, MAYBE, IF, BECAUSE, WHEN, LIKE, AFTER, BEFORE, VERY, MORE} — **no OR**. The NSM-style paraphrase (two MAYBE clauses) expresses epistemic possibility, not disjunction (inclusive/exclusive undetermined) — semantically lossy, therefore banned for a "lossless" roll-up. Adding OR is an encoder version change (ALGORITHM_VERSION bump, X0 golden regeneration, Phase-X re-run) *and* a grammar-design question; deferred behind a measured need — **B-E0 counts the corpus mass the missing operator forfeits**, so the decision is a number, not a taste. |
| (free riders) NOT / CAN / MAYBE / IF / BECAUSE / WHEN complexes | ✅ native | Already unary/binary operators over clauses. |

**Scope rule (design decision):** the roll-up unit is any **maximal parseable
explication fragment** — not a pattern whitelist — with the three maintainer-named
patterns kept as pre-registered reporting *strata* (plus an operator-complex stratum
and the OR-forfeit count). "Safely" is enforced structurally: the deterministic parser
either produces a valid capped AST (validated fail-closed, ERR_* codes) or abstains and
the text passes through untouched. There is no approximate roll-up path.

### 3.2 Minting invented composites (deterministic, training-free)

- **Identity:** composite AST → canonical JCS serialisation → content-hash URN per
  `docs/design-hash-input.md` (`urn:kot:` scheme). Content addressing gives global
  deduplication for free: the same composite recurring across utterances or corpora
  mints the same URN, so a *global* invented-concept dictionary accumulates and the
  per-utterance dictionary is just its novel slice. Frequent composites become
  candidates for promotion to named haiku-tier/molecule concepts (a coverage-growth
  feedback into idea A — recorded as a link, not a mechanism).
- **Vector:** `encodeExplication` — construction B, exact Hadamard TPR within clauses,
  whitened unitary circular-convolution HRR across clauses/depth [MEASURED machinery;
  X0 byte-determinism; X1-adversarial margins; X2 decode 51/54 encoder-side]. Zero
  training, zero seeds, same-input⇒byte-identical.
- **Injection:** X4 projection → E5/A2 adapter → one soft token (Law-1 compliant).
- **Fork B-F1 — bridge identity.** The E5 bridge was trained on single-concept
  vectors; multi-clause composites occupy a different region of kernel space. Arms:
  *(a)* zero-shot existing bridge; *(b)* bridge trained on a composite split disjoint
  from all eval composites (E5's nonce discipline — no eval-composite leakage). *(a)*
  failing while *(b)* passes is itself a finding (composites need their own bridge) and
  puts the retraining cost on V. *Kill per arm:* both failing = K-B1.

### 3.3 The decoder: invented-concept dictionary, exact expansion, round-trip

- **The dictionary is system-side.** It maps URN → canonical AST (+ pinned rendered
  text) and lives in the encoder/decoder harness, **never in the LLM context**. This is
  a binding accounting rule: if dictionary text had to ride in the prompt, the
  compression would invert (each entry costs more tokens than a roll-up saves). The
  model receives only the soft token; the *system* re-expands whenever the content must
  surface as text.
- **Expansion is exact-by-id** (URN lookup), and rendering uses the deterministic
  record→text renderer (shared with N-PL §4 — one artefact, two seats). **No cosine
  step exists anywhere in the path** (X3 ban respected structurally); vector-space
  decoding via unbinding (X2 machinery) is available as a *diagnostic only* and is
  never load-bearing.
- **Round-trip fidelity** is therefore exact at the symbol level **by construction**
  (parse → roll-up → URN → expand → re-parse is an identity on the covered fragment).
  What guards it is an implementation property suite, not an experiment: extend the
  encoder `node:test` suites with roll-up/expansion round-trip over the seeded
  generator + the validity-preserving mutator (X1-suite pattern), depth×clause-count
  stratified. Pre-declared bar: **100%** — any failure is a bug, not a result (contrast
  the linter's ≥0.95 renderer bar, which tolerates parse-render asymmetries; here both
  ends are the same closed AST, so nothing less than identity is acceptable).
- The *scientific* risks live elsewhere: upstream, parse engagement on real text
  (mapper abstention bounds everything — measured in B-E0); downstream, whether the
  LLM can *use* the composite token (B-E1, the Law-1 question).

### 3.4 X1-compliant framing (binding on every B artefact)

Justified **only** on compression/efficiency: k text tokens of parseable structure →
1 concept token. Pre-registration declares: primary = token/FLOP/latency reduction;
co-primary = accuracy non-inferiority (TOST, margin at freeze); accuracy-superiority
claims from structure are **banned** (any observed gain is reported descriptively with
the X1 parity expectation restated); a structure-as-text arm (the rolled fragment's
canonical rendering as plain text) runs as an expected-parity control. This mirrors how
`idea-code-input-canonicaliser` survives X1 on the variance endpoint: survival is by
endpoint discipline, not by hoping X1 is wrong.

### 3.5 The nulls idea B must beat

The §1.3 family, with the decisive incremental null called out:

- **L1b-flat**: the same covered content as *per-concept* tokens without roll-up.
  B's whole marginal claim is fewer tokens than flat at non-inferior accuracy; if B
  only matches flat on the compression–accuracy Pareto, roll-up adds nothing (K-B2)
  and the finding folds back into L1b.
- **Shuffled-composite** (E9-defl): same roll-up, same token count, content-scrambled
  vector. If accuracy non-inferiority holds under shuffling too, the composite's
  content is not being used — the parity is context-redundancy, the kernel earns no
  credit, and the honest conclusion is "you can delete parseable fragments cheaply,"
  which belongs to the trained-compressor literature, not to us (K-B3).
- Kernel-as-text, matched-token trained compressor, full text: as in §1.3.

### 3.6 Cost accounting end-to-end

Per rolled span: savings = (t_span − 1) tokens × p. Marginal per-query cost ≈ 0
(deterministic CPU: parse, encode, hash, render — measured, expected µs–ms). No mint
cost at all (invented concepts are derived, not authored — this is idea B's structural
cost advantage over idea A). One-time: possible composite-bridge training (B-F1(b),
E5-class GPU-h, Tier 2). Corpus-level savings = engagement × avg span savings, where
engagement is the fraction of workload tokens inside maximal parseable fragments —
necessarily ≤ conjunctive proposition-level coverage, which the linter design already
warns may be far below the 0.3542 token-mass number [MEASURED m0b, envelope §1.5].
**B-E0's engagement number is therefore the idea's live-or-die number**, and it is free
to obtain.

### 3.7 Evaluation plan (candidate-shaped; nothing frozen)

- **B-RT — round-trip property suite (Tier 0, ~$0; now-eligible).** §3.3. Bar: 100%.
- **B-E0 — roll-up engagement census (Tier 0, ~$0, r0-local-cpu; now-eligible).**
  Deterministic, no model calls, pinned corpora (TinyStories-validation for continuity
  with m0b + one instruction/QA corpus [STIPULATED at freeze]) × pinned tokenizers.
  Per corpus: fraction of sentences/tokens inside maximal parseable fragments, by
  stratum {is-a, clause-AND, operator-complex}; per-span text-token counts (the
  savings distribution); composite dedupe statistics (unique URNs vs occurrences —
  sizes the global dictionary and the promotion-to-named-concept opportunity); the
  **OR-forfeit count** (fragments that would parse but for a disjunctive connective —
  the measured case for/against the grammar extension). Deliverable: achievable
  corpus-level compression ratio + the OR decision number.
- **B-E1 — consumption (Tier 2–3; rides the F3 cap, ≈ +$20–60).** Covered QA/cloze
  tasks at R1–R2 (≥2 rungs per P8): arms {full text; kernel-as-text; L1b-flat; B-rolled
  × B-F1(a,b); structure-as-text control; shuffled-composite; matched-token trained
  compressor}. DVs: full V (prefill/decode split), accuracy non-inferiority, per-span
  engagement realised at runtime. Statistics per P8 (paired bootstrap; TOST; Holm
  across the arm family where a region claim is made; IUT for conjunctions).

**Pre-shaped kills (margins at freeze):**

- **K-B0 (engagement):** B-E0 achievable corpus savings below the floor (sanity
  default: <2% of workload prefill tokens [STIPULATED; reset at freeze]) ⇒ roll-up is
  not worth its complexity at current coverage/grammar; idea parks behind coverage
  growth (idea A) and/or the OR extension, with the census as the re-entry gate.
- **K-B1 (bridge fidelity):** accuracy non-inferiority fails vs full text under both
  B-F1 arms at every rolled configuration ⇒ composite vectors don't survive the
  trained bridge; Law-1's toll wins; record the negative.
- **K-B2 (incremental):** B ≤ L1b-flat on the compression–accuracy Pareto ⇒ roll-up
  adds nothing beyond flat concept tokens; fold into L1b, close the idea.
- **K-B3 (content):** shuffled-composite recovers non-inferiority ⇒ no kernel credit
  (§3.5); the architectural observation is recorded without kernel claims.
- **K-B4 (commodity):** trained compressor achieves matched tokens at parity ⇒ HE3's
  kill inherited; deterministic roll-up loses to learned compression.

### 3.8 Epistemic status and readiness

**EXTRAPOLATION**; `premise_eligible: false` stands. Measured anchors: the binding
algebra's Phase-X record (X0/X1/X2/X4), E5's single-concept nonce PASS (+28.5 pp — the
existence proof that *one* pinned adapter-bridged token can carry usable content at R1;
composites are strictly beyond it, hence B-F1), m0b, and the d-ext
membership≠engagement lesson. Lit anchors: X1 (parity boundary — LIT-BACKED), Law 1/2.
Readiness: B-RT and B-E0 **now-eligible** (Tier 0, no gates); B-E1 gated on F3 +
maintainer sign-off; the OR grammar extension is *not proposed* — it waits on B-E0's
forfeit count.

---

## 4. Interactions, ordering, and placement

### 4.1 How A and B compose

Orthogonal but mutually reinforcing: A raises κ (which lemmas are covered at all); B's
engagement requires *every* lemma in a fragment to be covered (conjunctive), so each
point of A-coverage raises B's parseable mass superlinearly on mixed text. B's
frequent-composite statistics (B-E0 dedupe) feed A's mint queue (promote recurring
composites to named concepts). Both consume through L1b; both share the mapper
front-end and the N-PL renderer. A's alternative kernel becomes an arm in B-E0 re-runs
(roll-up engagement under kernel-A vs molecules-v0).

### 4.2 Recommended order (cheapest-decisive-first; design opinion)

| Order | Item | Tier / est. $ | Gate | What it decides |
|---|---|---|---|---|
| 1 | **B-E0 + A-E2 censuses** (+ B-RT suite) | 0 / ~$0 | none (r0-local-cpu) | both ideas' live-or-die engagement/savings numbers, the OR-forfeit count, the fertility asymmetry — before any spend |
| 2 | **A-F0** fork sub-test | 0–1 / ~$5–10 | maintainer spend-ack | the maintainer's symbolic-output fork, with the §2.3 decision rule |
| 3 | **A-E1** mint pilot | 1 / ~$20–40 | A-F0 verdict + sign-off | cached-prefix mint economics vs the s1-G baseline |
| 4 | **A-E3 / B-E1** consumption arms | 2–3 / F3 cap + ~$40–100 | F3 gates + sign-off | the actual compression claims, against the full null family |

A pre-registered **cost/accuracy Pareto metric vector** — {accuracy (non-inferiority
margin), prefill tokens, prefill/decode FLOPs, KV bytes, wall latency, $/query
end-to-end, amortized authoring/mint/training $ (V), engagement κ, per-language
splits} — is declared per the bead's instruction before any Tier-1+ spend, via the
research-engine candidate template.

### 4.3 Registry and ladder placement

`ladder_ref: in-tokenisation-normalisation` for both (L1b feeders; no new rung). Idea
records updated per §5 of the bead: fleshed entries appended centrally by the
coordinator (this document does not write `registry/ideas.jsonl`). Cross-links:
`idea-kernel-precision-linter` (shared renderer + coverage growth),
`idea-code-input-canonicaliser` (the X1-survival-by-endpoint precedent),
`idea-leaderboard-benchmark-eval` (b-cov census pattern reused),
`idea-a2-adapter` (the seam both ride).

---

## 5. Honest risks, stated before anyone falls in love

1. **Engagement may be brutal.** Both censuses may return single-digit-percent
   savings; that is a finding, and it is why the censuses run first and cost nothing.
2. **The nulls are strong and cheap.** A bigger BPE vocabulary (A) and a trained
   compressor (both) attack the same savings with mature tooling. The kernel's
   defensible residuals — zero per-item training, deterministic re-derivation on
   definition change, cross-lingual sharing, auditability — are real but must be
   *priced*, not asserted; K-A3/K-B4 can honestly fire.
3. **The bridge fidelity ceiling** (Law 1) may tax accuracy beyond any margin worth
   the savings, especially for composites (E5 proved single concepts only).
4. **Mint quality vs cost tension** (A): word-only variable input maximises caching
   but weakens provenance; the fidelity audit in A-F0/A-E1 is the guard, and
   provenance loss is a kill, not a trade.
5. **Thinking-time paradox** (A-F0) may be real: symbolic-direct output could cost
   more end-to-end than prose-tolerant output. The sub-test exists precisely so this
   is settled for ~$10 before it shapes anything.
6. **OR-shaped text is invisible to B at v0.** If B-E0 shows disjunction-heavy
   workloads dominate the forfeit, B's ceiling is structurally capped until a grammar
   version change that must clear its own design bar.
7. **LCM-shadow**: growing κ pushes the input edge toward higher effective fixedness;
   the L2c sweep, not this document, owns that question — these ideas only report κ.

---

*Cross-references:* `registry/ideas.jsonl` (both idea records; fleshed entries
appended 2026-07-09); `docs/next/architecture-ladder.md` §§3, 4.3, 10 (L1b, L2c, b-cov
pattern); `docs/next/kernel-precision-linter.md` §§4, 6, 8 (renderer, coverage
staircase, shared components); `data/haiku-tier/s1-experiments/s1-report.md` (framework
G economics [MEASURED]); `data/haiku-tier/README.md` + `mint-manifest.json`
(modelAuthored tier, URN scheme); `docs/design-hash-input.md` (content-hash identity);
`docs/design-compact-kernel-serialization-v2.md` (compact record forms for A-F0 arm b);
`encoder/README.md` + `encoder/src/lexicon.ts` (construction B; the closed operator
inventory §3.1 rests on); `reports/lit-llm-injection-priorart.md` (Laws 1–3; xRAG
ceiling); `registry/verdicts/m0b.json` (coverage envelope);
`data/d-ext/manifest.json` (membership ≠ engagement); `docs/research-plan/08-*`
(P8 statistics discipline). API pricing/caching facts in §2.2–2.3 verified 2026-07-09
against live Anthropic documentation (Haiku 4.5 $1/$5 per MTok; cache read ≈0.1×,
write 1.25× at 5-min TTL; 4096-token minimum cacheable prefix on Haiku 4.5; Batch API
−50%; thinking on Haiku 4.5 via `budget_tokens`, `effort` unsupported).
