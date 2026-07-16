# GPT-5.6 draft-pipeline for the large-kernel scale-up — design spec

> **Status:** DESIGN / SPEC ONLY. Authorizes nothing to run, spend, ingest, or freeze.
> No drafting run, no GPU, nothing committed by this pass. Maintainer approval + a
> `kot-reg/*` prereg-freeze are required before any spend. Author: Kern (Fable design
> agent, designer-1), for @jeswr. Date: 2026-07-16.
> **Mandate:** issue #44 (CLOSED, maintainer-decided) — *"Large-kernel drafting
> (biggest win, zero collision): GPT-5.6 drafts candidate concept explications at
> volume for the scale-up track → every draft passes the encoder-validator loop + lint
> gates (acceptance stays with the explicator pipeline). **Not** the kernel's final NSM
> records — drafts only, validator-gated."*
> **Scope note:** this is the *volume authorship* half of #44 (use 1). It is orthogonal
> to the `plain-v5-natural` generic-control arm (use 2A/2B) and does not touch it.

Binding constraints: `docs/kernel-design-directives.md` §§1–6; the epistemic-discipline
directive (every load-bearing claim tagged; established only when MEASURED or LIT-BACKED;
an EXTRAPOLATION is never a decision premise); `docs/design-bulk-kernel.md` (the
`semanticStatus` honesty ladder); `docs/next/design/sense-split-first-construction.md` +
`docs/next/design/f1k-large-kernel-rebuild.md` (the kernel-v1 sense-split-first
construction pipeline this drafting feeds).

**Epistemic tags** (as in the assumption register, `docs/next/assumption-register.md` §1):
**[MEASURED]** read from committed bytes / a diagnostic this tick; **[LIT-BACKED]**
published, provenance disclosed; **[STIPULATED]** a design choice or this designer's
ruling, rationale given, never evidence; **[EXTRAPOLATION]** a forward projection with a
resolution_path, never a decision premise. This pass registers its nine design
assumptions — **ASM-2420, ASM-2424, ASM-2428, ASM-2429, ASM-2431, ASM-2434, ASM-2435,
ASM-2437, ASM-2438** (eight load-bearing STIPULATED + one EXTRAPOLATION carrying its
resolution_path) — in `registry/assumptions.jsonl` (working tree, nothing committed by
this pass; ids drawn from the 2420–2439 block reserved when the max registered id was
ASM-2419, 2026-07-16 — the block's unused ids are returned free). Design points that
restate an already-committed rule keep their inline tag + committed source and carry no
new ASM (§7).

---

## 0. The one-paragraph answer

GPT-5.6-Sol becomes the **draft author** in the *already-designed* kernel-v1
sense-split-first construction pipeline — it does not become a new pipeline. Each
candidate is one WordNet-3.1 synset cluster (sense-split-first: polysemous words are
distinct concepts, `ASM-1902` R1–R5). GPT-5.6 emits a `gloss` + a `kot-ast/1`
explication **draft** in profile-1 (65 primes); the draft then runs the *unchanged*
acceptance stack — `validateExplication` (per-record, fail-closed ERR_* codes) →
`encodeConceptSet` encode-sanity → lint/leakage gates → the human 4-binary review of the
existing eligibility gate (`f1k-large-kernel-rebuild.md` §1.1). **GPT-5.6 authors DRAFTS
ONLY; acceptance never moves off the validator loop + human gate.** The single novel
engineering surface is a **stable-prefix prompt cache + idempotent dedup by
concept-id+version** so that at millions-scale the NSM grammar / profile-1 lexicon /
few-shot / lint contract are paid for *once per warm worker*, not once per concept. We
validate the whole thing on a **$-capped ~10k WordNet pilot with a pre-registered
accept-rate and cache-hit gate** before any 100k → 1M+ spend. Nothing here re-authors
frozen kernel-v0 (directives §8; kernel-v0 stays Fable/agent-authored and frozen), and
no downstream experiment that *consumes* these drafts may use a GPT-family judge
(author-family ≠ judge-family; #44 guardrail).

**The honesty tier this produces.** GPT-5.6 drafts land in a **new, visibly-second-class
tier** — proposed `semanticStatus: "ModelDrafted"` (below `Explicated`, distinct from the
mechanical `AxiomsOnly` of WordNet extraction, `docs/design-bulk-kernel.md` §honesty
ladder). A draft is *promoted* to `Explicated` only by passing the full composite gate
including human review; until then it carries no semantic-adequacy claim. This is the
same discipline the g9 authoring node used (`data/authored-explication-set/validation/
mechanical-summary.json`: mechanical legality is an UPPER BOUND, not a verdict) — the
mechanical pass rate never becomes the acceptance claim.

---

## 1. Inventory source (sense-split-first)

### 1.1 Stage 1 — WordNet 3.1 (~100k synsets)

Already extracted and pinned: `data/lexical-wn31/` at `semanticStatus: AxiomsOnly`,
source `sha256:3f7d8be8…`, **110,049 type-level synsets** across noun/verb/adj/adv
[MEASURED: `data/lexical-wn31/manifest.json`; `docs/next/design/f1k-large-kernel-rebuild.md`
§2 "110,049 WordNet type-level synsets"]. The scale-census 207,733 figure is an
**unmerged upper bound** (110,049 WN + 95,201 OBO + 2,483 SUMO, cross-source dups not
removed) and must never be treated as 207,733 independent clusters [MEASURED, same ref].

**Candidate = one WordNet-3.1 synset cluster**, keyed by the synset URN
(`urn:lexical-wn31:[nvar]-[0-9]{8}`). Sense-split-first is already the frozen construction
rule (`ASM-1902`): (R1) candidate senses = all same-POS synsets of the lemma, enumerated
mechanically; (R2) project onto the FrameNet frame carrying the lemma's LU, else
`frame:null`; (R3) a kernel-v1 concept is a cluster of ≥1 synsets sharing ONE frame + one
NSM explication + one argument structure — **the frame boundary is a HARD split
criterion** (causative/inchoative never clustered); (R4) mint only kernel-needed senses,
every non-minted candidate recorded in an explicit `excludedSenses` list (scope closed by
construction, not prose); (R5) single-source candidates enter with disclosed single-source
provenance, nothing silently dropped. Polysemy is real and heavy-tailed: `break` has 59
verb synsets / 75 across all POS, `make` 49, `give` 44 [MEASURED: `ASM-1900`].

**Consequence for drafting:** the drafting work-list is the enumerated, deduped
**synset-cluster candidate set**, materialized as `data/kernel-v1/draft-worklist.jsonl`
(one row per concept-id = cluster key). GPT-5.6 drafts *per cluster*, never *per word* —
this is what keeps polysemous words split. The worklist is produced by the pinned
sense-inventory reconciliation step (already designed), **not** by GPT-5.6; GPT-5.6 never
decides sense boundaries (that would move a construction-defining decision onto the
model). `[STIPULATED ASM-2420]`

### 1.2 Stage 2+ — Wiktionary / Wikidata / BabelNet-scale (millions+)

For the millions+ staged tiers the candidate source broadens beyond WordNet. Design
constraints, **not commitments** (each is its own ingest + its own extractor-design pass,
`docs/next/coverage-growth-ingestion-plan.md` §2 cost model — there is no generic RDF
extractor; every source is bespoke):

- **Wiktionary** — sense inventory is prose-rich; senses become candidate concepts after a
  mechanical sense-split extractor (Cost-2, bespoke). Licence CC BY-SA — must be recorded
  per record; SA obligations flow into provenance. `[EXTRAPOLATION, resolution_path:
  Wiktionary sense-split extractor design + licence verification pass]`
- **Wikidata** — lexeme/sense layer (`L…-S…`) is the sense inventory; the *item* layer is
  **world-layer facts, wrong tier** for explication (`docs/design-bulk-kernel.md` rejects
  Wikidata for the definitional tier). Only the lexeme/sense layer is a drafting candidate
  source. `[STIPULATED: the docs/design-bulk-kernel.md tier ruling, restated]`
- **BabelNet** — a synset *merge* across WN/Wiktionary/Wikidata; its value is
  **cross-source sense alignment** (dedup key), not a new sense inventory. Licence is
  research-restricted — a redistribution-licence blocker that must clear before ingest, or
  it is used only as an alignment oracle and never redistributed. `[EXTRAPOLATION,
  resolution_path: BabelNet licence adjudication]`

The **canonical dedup key** carries across tiers: a BabelNet/cross-source crosswalk maps a
Wiktionary/Wikidata sense onto its WN synset **where one exists**; single-source senses
(no WN anchor) enter with disclosed single-source provenance (R5). This is what prevents
the millions+ tiers from re-drafting the WordNet 100k under a different name.

**Scale figures are STIPULATED targets, not counts.** "Hundreds-of-thousands → millions+"
is the maintainer's ideal ceiling; the *realizable* candidate count at each tier is
measured by the extraction, not assumed. No scale number in this doc is load-bearing for a
go decision — the per-stage gate (§5) decides on measured accept-rate + cost, not on a
hoped concept count. `[STIPULATED ASM-2424]`

---

## 2. Draft pipeline

```
 sense-inventory (pinned, NOT GPT)         ← work-list = synset-cluster candidates
        │  draft-worklist.jsonl (concept-id = cluster key, + WN gloss/synset, extracts)
        ▼
 ┌──────────────────────────────────────────────────────────────────┐
 │  GPT-5.6-Sol DRAFT AUTHOR  (authoring-blind; sees only:           │
 │    headword + sense/synset + WN gloss + pinned extracts +         │
 │    the cached NSM/profile-1/few-shot/lint contract)              │
 │  → emits {gloss, explication:kot-ast/1}  DRAFT                    │
 └──────────────────────────────────────────────────────────────────┘
        ▼
 ┌──────────── ACCEPTANCE (unchanged; NOT GPT) ─────────────────────┐
 │ 1. validateExplication(e)   per-record, fail-closed ERR_*        │  ← encoder/src/validate.ts
 │ 2. encodeConceptSet          encode-sanity: no NaN, norm ok       │  ← data/validate.mjs --kernel
 │ 3. lint gates                gloss standard (§1.1 1–9),           │
 │                              non-circularity, 15–100 words,       │
 │                              ≤128 tok pinned tokenizer,           │
 │                              8-token leakage check vs eval items  │
 │ 4. repair loop (≤R tries)    same prefix + draft + real ERR_*     │
 │ 5. HUMAN 4-binary review     same-sense · intension · scholarly · │  ← promotion gate
 │                              AST/prose consistent  (ALL yes)      │
 └──────────────────────────────────────────────────────────────────┘
        │ accept → data/kernel-v1/concepts/<slug>.json  (ModelDrafted → Explicated on human-pass)
        │ reject → quarantine w/ failure code; never silently dropped
        ▼
 provenance recorded per record (§2.3)
```

### 2.1 GPT-5.6 authors DRAFTS ONLY

The model emits, per candidate, a `{gloss, explication}` pair in the kernel-v0/v1 record
shape (`{id, label, status, pattern?, gloss, notes?, references, explication}`,
`f1k-large-kernel-rebuild.md` §1.1). `gloss` is scholarly prose; `explication` is the
`kot-ast/1` structural record in profile-1 (frame ∈ EXPLICATION_FRAMES, ≤32 referents
dense-from-1, closed prime/role/op vocabulary — the exact surface `validateExplication`
enforces, `encoder/src/validate.ts`). **The model's output is a candidate, not a record.**
Acceptance is 100% on the deterministic validator + human gate; the model never
self-accepts, never sees eval items or perf data (authoring blindness, below).

### 2.2 Authoring blindness (binding, from the #44 guardrail + g9 precedent)

The draft prompt contains **only**: headword + sense/synset id + the aligned WordNet gloss
+ the pinned source extracts (A-F2(b) source-fed form) + the cached NSM grammar /
profile-1 lexicon / few-shot / lint contract. It **never** contains: benchmark items, the
kernel, coverage rank, matched eval questions, model-performance data, or any downstream
metric. Prompt + transcript are pinned per drafting batch (`kot-log/1` record). This is
the g9 authoring-blindness rule verbatim (`data/authored-explication-set/` selection
manifest: the dataset's own reference explication is kept "for provenance only — NEVER
shown on the blinded review sheet"). `[STIPULATED: the g9 selection-manifest rule,
restated verbatim]`

### 2.3 Provenance & disclosure (per record, mandatory)

Every drafted record carries, in addition to the existing bulk-provenance quadruple
(`{source, sourceVersion/hash, extractorVersion/hash, extractionDate}`,
`docs/design-bulk-kernel.md`):

```jsonc
"provenance": {
  "draftAuthor": "gpt-5.6-sol",            // model id + pinned snapshot/date
  "authorFamily": "gpt",                    // for the author≠judge gate (§6)
  "authorship": "model-drafted, agent-authored, validator-gated",
  "promptHash": "sha256:…",                 // pinned draft prompt (blindness attestable)
  "cachePrefixHash": "sha256:…",            // the stable prefix under cache (§3)
  "repairCalls": <int>,                     // draft→validator repair iterations used
  "acceptancePath": "validateExplication+encode+lint+human4",
  "humanReviewId": "<review-id>", "humanReviewPass": true,
  "semanticStatus": "Explicated|ModelDrafted",
  "conceptId": "<synset-cluster-key>", "conceptVersion": "<n>"  // dedup identity (§3.2)
}
```

Disclosure travels in the manifest (the #44 guardrail: "disclosure travels in the
manifest"). A drafted record is an **assertion by GPT-5.6 that the validator + human
accepted**, re-derivable: same prompt + same model snapshot → attestable draft; the
*acceptance* is deterministically re-runnable (`validateExplication` is pure).
`[STIPULATED: the docs/design-bulk-kernel.md provenance quadruple + the #44
disclosure-travels-in-the-manifest guardrail, extended per-field]`

### 2.4 What stays fail-closed

No silent fallback (`CLAUDE.md` conventions). A draft that fails `validateExplication`
returns the **real** `ERR_*` list (e.g. `ERR_PRIME_UNKNOWN`, `ERR_SLOT_KIND`,
`ERR_ROLE_REQUIRED_MISSING`, `ERR_CAP_CLAUSES`, `ERR_REF_NEVER_INTRODUCED`) into the repair
call; after R repair tries it is quarantined with its failure code, never coerced into a
record. Leakage (8-token overlap with any eval item after trigger/stopword removal) is a
hard reject, not a warning (`f1k-large-kernel-rebuild.md` §1.1). `[STIPULATED: the
CLAUDE.md no-silent-fallback convention + the f1k-large-kernel-rebuild.md §1.1 leakage
rule, restated]`

---

## 3. Caching (first-class — maintainer emphasis)

The A-F0 mint-economics experiment already priced *and froze the mechanism* of a
stable-prefix cached definer on the Messages API (`docs/next/a-f0-mint-economics-spec.md`
§S2): a shared system prefix under `cache_control:{type:"ephemeral"}`, variable suffix =
target word + extracts, repair call = same prefix + draft + validator errors. This design
carries that mechanism forward to GPT-5.6 at volume.

### 3.1 Stable prompt-prefix cache

**Cached prefix (invariant across every call in a batch)** — the four blocks that make up
the bulk of the tokens:

1. NSM grammar contract (profile-1: frames, the 65 primes, roles, ops, caps — the surface
   `validateExplication` enforces).
2. Profile-1 lexicon / closed grounding vocabulary + the ref catalog (kernel-v0 +
   molecules-v0 depth ≤ 3, at its pinned mint-manifest state).
3. Few-shot exemplars (a small fixed set of accepted `{gloss, explication}` pairs — e.g.
   drawn from the 50 g9-authored records).
4. The lint contract (gloss standard 1–9, leakage rule, caps).

**Variable suffix (only this changes per call):** headword + sense/synset id + WN gloss +
pinned extracts. **Repair suffix:** the draft + the real `ERR_*` list.

The prefix is deterministically serialized and content-hashed (`cachePrefixHash`); it
changes **only** on a deliberate contract bump (which is a re-freeze, like an
ALGORITHM_VERSION bump). The prefix is engineered to exceed the provider minimum cacheable
size so it is actually cacheable (A-F0 pinned Haiku's 4096-token floor; GPT-5.6's floor is
re-verified at preflight, ASM-0601-style). `[STIPULATED ASM-2428]`

### 3.2 Idempotent dedup by concept-id + version (never re-draft; resumable)

Identity = `conceptId` (synset-cluster key) + `conceptVersion`. Before any call, check a
persistent **draft ledger** (`data/kernel-v1/draft-ledger.jsonl`, append-only, same
discipline as `registry/`): if `(conceptId, conceptVersion, promptHash, cachePrefixHash)`
already has an accepted or quarantined outcome, **skip — no call**. Consequences:

- **Resumable / checkpointed** (the harness rule — long runs `nohup`+`setsid`, checkpointed;
  cf. the F1-K carrier pipeline's mode+sha-bound checkpoints). A kill mid-run re-enters at
  the ledger frontier; zero re-draft, zero double-spend.
- A `conceptVersion` bump (e.g. contract change) re-drafts *only that concept*, not the
  corpus.
- **Never re-draft an accepted concept** — the ledger is the single source of truth; the
  worklist minus the ledger frontier is the remaining work. `[STIPULATED ASM-2429]`

### 3.3 Batch + warm-cache worker pool

Workers are **long-lived and cache-warm**: a worker holds the prefix hot (cache read, not
re-write) and streams candidate suffixes. Batch mode (the provider's async batch tier, A-F0
projected a ~50% discount as a *derived multiplier only*) is used for the non-interactive
bulk; interactive/repair calls stay online. Concurrency + sharding per §4. `[STIPULATED:
operational detail under §3.1/§3.2 (ASM-2428/ASM-2429) — no separate assumption]`

### 3.4 Cache-hit economics at millions-scale (the estimate — STIPULATED arithmetic)

> **HONESTY CAP.** Every USD/token figure below is **[STIPULATED]** on a *placeholder*
> price table and *modelled* token counts. GPT-5.6-Sol's real price table and prompt-cache
> semantics are **not committed in this repo** and are **re-verified against the live
> provider reference at staging preflight** — any discrepancy is an ops amendment *before*
> first spend (the A-F0 ASM-0601 discipline verbatim). The **arithmetic** is MEASURED (shown
> below); the **inputs** are STIPULATED; therefore the **conclusion is STIPULATED** and is
> **never a decision premise** — the §5 gate decides on the *measured* pilot, not on this
> model. `[STIPULATED ASM-2431]`

Model (per-concept, warm cache), using a generic cached-input price table shaped like
A-F0's (`input`, `output`, `cache_read` ≈ 0.1×input, `cache_write` ≈ 1.25×input):

Let `P` = cached prefix tokens (large; the NSM/lexicon/few-shot/lint contract), `S` =
variable suffix tokens (small; headword+sense+extracts), `O` = output tokens (the drafted
gloss+AST), `r` = repair-call multiplier (≈ calls/concept; A-F0 measured **~1.8
calls/concept** for the Haiku baseline [MEASURED: `a-f0-mint-economics-spec.md` LOAD-BEARING
s1-G]).

- **Cold (no cache)** per concept ≈ `r · (P+S)·input + r·O·output`. Dominated by `P·input`
  because `P ≫ S`.
- **Warm (prefix cached)** per concept ≈ `cache_write` paid **once per warm worker**, then
  per concept `r · (P·cache_read + S·input + O·output)`.

The prefix cost collapses from `P·input` to `P·cache_read ≈ 0.1·P·input` per concept — a
**~10× reduction on the prefix component**, which is the dominant component when `P ≫ S+O`.
Across a batch of `N` concepts sharing one warm prefix, the one-time `cache_write` amortizes
to ≈ 0 as `N → millions`. **Illustrative** (placeholder numbers, NOT a quote): with `P` an
order of magnitude larger than `S+O`, warm per-concept cost is on the order of **10–20% of
cold** — i.e. caching is the difference between a feasible and an infeasible millions-scale
run. This is *why* the maintainer's caching emphasis is load-bearing: at 1M concepts the
prefix, uncached, would be paid 1M×; cached, effectively once. The **measured** pilot
cache-hit rate + cost/concept (§5) replaces every number here before any scale decision.
`[STIPULATED ASM-2431]`

Cache-hit rate target is a **gate metric**, not an assumption: the pilot must demonstrate a
measured cache-read fraction near the structural ceiling (≈ `P/(P+S+O)` of input tokens
served from cache), and cost/accepted-record within the A-F0-baseline envelope
(baseline-to-beat: **$0.078 per legal record** for the Haiku definer [MEASURED:
`a-f0-mint-economics-spec.md`], adjusted for GPT-5.6's real price table at preflight).

---

## 4. Throughput & storage (millions of AST records)

### 4.1 Throughput / parallelism

- **Decouple draft from acceptance.** GPT-5.6 drafting is network/latency-bound and runs on
  the provider's fleet (batch tier). `validateExplication` + `encodeConceptSet` are pure,
  local, deterministic CPU — they parallelize trivially and run on our side. The pipeline is
  a producer/consumer queue: drafters fill a candidate queue, a validator pool drains it. No
  GPU is involved (encoder is `node:crypto` + own FFT, zero deps).
- **Sharding by concept-id.** The worklist shards by a hash of `conceptId` into K shards;
  each shard is an independent resumable stream with its own ledger segment (append-only,
  mergeable). Shards share the same warm cached prefix (same `cachePrefixHash`) — sharding
  multiplies throughput without multiplying prefix cost.
- **Concurrency cap** honours the provider rate limits and our local core budget; the
  validator pool is sized to keep up with the drafter fill rate so the candidate queue does
  not grow unbounded (backpressure).
- **Checkpointed, niced, nohup+setsid** per the harness lessons (`modal-attached-runs…`
  memory; F1-K carrier checkpoint discipline). A killed client never orphans remote batch
  jobs — batch handles are recorded in the ledger and reconciled on resume. `[STIPULATED:
  operational detail under the existing harness discipline + the ASM-2429 ledger — no
  separate assumption]`

### 4.2 Storage plan

Two-plane storage, mirroring the existing bulk decision (`docs/design-bulk-kernel.md`
"vectors on demand"):

- **Identity + structure plane (stored):** the `{gloss, explication:kot-ast/1}` records +
  provenance + ledger. A `kot-ast/1` record is small JSON (≤32 referents, bounded clauses).
  At **1M records** ≈ low single-digit GB of JSONL — commodity, shardable, git-LFS/object-
  store friendly. Records are the durable artifact.
- **Vector plane (on demand, NOT stored wholesale):** canonical vectors are
  **re-derivable** because the encoder is deterministic and pinned (content-hash over
  {schema, algorithm, D, codebook, weighting}). Storing 1M × D=8192 fp16 ≈ **16 GB** and
  is unnecessary on this box; vectors are materialized per-consumer, per-experiment, from the
  pinned encoder, exactly as the bulk-kernel design already rules (10⁵ × D=8192 fp16 ≈ 1.6
  GB "not stored wholesale; the encoder is deterministic so vectors are always
  re-derivable"). `[MEASURED: `docs/design-bulk-kernel.md` §Interactions]`
- **Manifest / provenance plane:** per-shard manifests with source shas + `promptHash` +
  `cachePrefixHash` + model snapshot, so any drafted slice is re-derivable and disclosure is
  attestable. Append-only, same `registry/` discipline.
- **Sanity at scale:** whole-corpus checks (`encodeConceptSet`, reference/manifest
  cross-checks, no-NaN/norm) run per shard; a shard is not marked complete until its checks
  are green (fail-closed). `[STIPULATED: the docs/design-bulk-kernel.md vectors-on-demand
  ruling, restated at kernel-v1 scale]`

---

## 5. Staged rollout + per-stage go/no-go gate

**Sequence (each stage gates the next; no stage's spend is authorized until the prior
stage's gate returns PROCEED):**

| Stage | Source scope | Purpose | $ cap | Primary gate metrics |
|---|---|---|---|---|
| **Pilot (10k)** | WordNet 3.1, 10k synset-cluster candidates | validate the *pipeline + caching* end-to-end | **$-capped (registered before spend)** | (a) validator+lint **accept-rate**; (b) **cache-hit rate** (cache-read token fraction); (c) **$/accepted-record** vs A-F0 baseline; (d) human-review pass-rate on a sampled subset |
| **100k** | WordNet remainder + clean crosswalks | scale the validated pipeline over the full WN inventory | registered, larger cap | same four, must hold within the pilot's measured envelope |
| **1M+** | Wiktionary/Wikidata/BabelNet-scale | millions+ tiers | registered per-tier cap | same four, per source; licence-clearance gate per source (§1.2) |

### 5.1 The 10k WordNet pilot gate (the near-term deliverable)

**Design (frozen shape; numbers registered at prereg-freeze, not here):**

- **Sample:** 10,000 synset-cluster candidates drawn by a pinned, seeded rule from the WN
  worklist (stratified across POS + polysemy band so the heavy tail — `break`/`make`/`give`
  — is represented, `ASM-1900`). Seed pinned; single-draw rule (a re-draw is a new id).
- **$ cap:** a hard pre-registered ceiling, checked against a worst-case ledger *before*
  launch (the experiment-runner ledger discipline: mock/dry-plan first, worst-case-$ checked
  against the cap, fail-closed on overrun). Mock run ($0) green before any real spend.
- **Measured endpoints (all reported with scope, none extrapolated):**
  1. **accept-rate** = accepted records / attempted candidates (validator+lint+repair leg).
     Reported with a Wilson interval (the g9 mechanical-summary convention). The g9 precedent
     shows the mechanical leg *reachable at ceiling* on curated authoring (50/50) — but that
     was Fable-authored on a curated 50; GPT-5.6 at 10k WN volume is **UNMEASURED** and this
     pilot is exactly what measures it. `[EXTRAPOLATION ASM-2434, resolution_path: the 10k
     pilot itself]`
  2. **cache-hit rate** = cache-read input tokens / total input tokens, per §3.4. Must
     approach the structural ceiling `P/(P+S)`.
  3. **$/accepted-record** — real API usage × the preflight-verified GPT-5.6 price table.
     Baseline to beat: **$0.078/legal record** (A-F0 Haiku) adjusted to GPT-5.6 pricing.
  4. **human-pass-rate** — on a blind sampled subset (the 4-binary review), because
     mechanical accept-rate is an UPPER BOUND on composite acceptance, never the acceptance
     claim (`data/authored-explication-set/validation/mechanical-summary.json`).
- **Go/No-Go decision rule (registered, verbatim kill criteria + envelope):** PROCEED to
  100k **iff** all hold: accept-rate ≥ a registered floor `α`; cache-hit rate ≥ a registered
  floor `κ`; $/accepted-record ≤ the registered cost ceiling `$c`; human-pass-rate on the
  sample ≥ a registered floor `h`. Any miss → **NO-GO / reassess** (not silent proceed;
  directives §4 fork discipline). The floors `α, κ, $c, h` are set at prereg-freeze on the
  A-F0 + g9 priors, not in this design doc (that would be a hollow number here). `[STIPULATED
  ASM-2435]`
- **What the pilot can never be quoted as** (honesty cap): the pilot prices *drafting
  throughput + acceptance rate*, on *WordNet*, at *10k*. It is **not** a semantic-adequacy
  measurement of the drafted kernel (that is DeepNSM-territory, ≈24/100 established in wave
  1) and **not** a coverage or checkability claim (checkability ≠ vocabulary coverage,
  `coverage-growth-ingestion-plan.md` §0 — d-ext measured ~49% lemma-touch with 0%
  checkability). Accept-rate is a *legality/scholarly-review* rate, not a truth claim.
  `[STIPULATED: the coverage-growth-ingestion-plan.md §0 honesty cap + the g9
  mechanical-upper-bound rule, restated for the pilot]`

---

## 6. Guardrails (binding)

1. **Stay in the validated NSM formalism.** Drafts are profile-1 (65 primes) `kot-ast/1`
   only; anything the encoder rejects is rejected (fail-closed). No new frames, primes, ops,
   or caps are introduced by drafting — that would be an encoder version change (bump
   ALGORITHM_VERSION, regenerate X0 goldens, re-run Phase X). `[STIPULATED ASM-2437]`
2. **Author-family ≠ judge-family, downstream.** Any experiment that *consumes* these
   GPT-5.6-drafted records may not use a GPT-family judge/gate — swap to the Claude family
   (Haiku judge is ready), exactly the #44 (2A) ruling. The `authorFamily:"gpt"` provenance
   field (§2.3) makes this mechanically checkable at experiment prereg. Reciprocally, GPT-5.6
   keeps its judge seat *everywhere it did not author*. `[STIPULATED ASM-2438]`
3. **Never re-author frozen kernel-v0.** kernel-v0's NSM explications stay Fable/agent-
   authored and frozen (directives §8; #44: "kernel NSM explications never GPT-5.6-authored —
   that would dissolve the very contrast we measure"). GPT-5.6 drafts land in the **new**
   kernel-v1 `ModelDrafted` tier, a distinct id space; kernel-v0 is not touched, re-rendered,
   or grandfathered (`f1k-large-kernel-rebuild.md` §1: "Do not grandfather kernel-v0
   concepts").
4. **Disclosure per record.** Every drafted record carries the §2.3 provenance
   (`draftAuthor`, `authorFamily`, `authorship`, `promptHash`, review id/pass, semanticStatus);
   disclosure travels in the manifest; a `ModelDrafted` record makes no semantic-adequacy
   claim until human-promoted.
5. **Acceptance stays with the validator loop + human gate.** GPT-5.6 never self-accepts;
   the mechanical rate is an upper bound, not a verdict; the composite bar includes blind
   human review. `[STIPULATED: the #44 mandate verbatim ("acceptance stays with the
   explicator pipeline") + the g9 mechanical-upper-bound rule — enforced by the §2
   pipeline, no separate assumption]`

---

## 7. Assumptions registered this pass

Nine assumptions REGISTERED in `registry/assumptions.jsonl` (working tree only — nothing
committed by this pass): eight load-bearing STIPULATED + one EXTRAPOLATION
(`load_bearing: false` per the register rule — a load-bearing EXTRAPOLATION cannot exist —
with its resolution_path). Ids drawn from the block reserved at authoring time (2420–2439,
max registered id then ASM-2419); the block's unused ids are returned free. Every row
carries the rider: *DESIGN-ONLY, maintainer approval required before any build or spend;
no feasibility conclusion on CORRECTNESS or EFFICIENCY; scale figures are targets, never
premises.* Backing refs are real repo artifacts (ASM-2431 caching economics →
`docs/next/a-f0-mint-economics-spec.md`; ASM-2420/2424 sense-split worklist →
`ASM-1900/1902` + `f1k-large-kernel-rebuild.md`; ASM-2437 formalism →
`encoder/src/validate.ts`; ASM-2438 author≠judge → issue #44).

| id | tag | one-line |
|---|---|---|
| ASM-2420 | STIPULATED | drafting is per synset-cluster candidate; GPT never decides sense boundaries |
| ASM-2424 | STIPULATED | scale figures are targets, never load-bearing; gate decides on measured counts |
| ASM-2428 | STIPULATED | stable cached prefix = NSM/lexicon/few-shot/lint; hashed; bump = re-freeze |
| ASM-2429 | STIPULATED | idempotent dedup by concept-id+version; ledger frontier = resumable, no re-draft |
| ASM-2431 | STIPULATED | cache economics: ~10× prefix reduction warm; numbers placeholder → preflight |
| ASM-2434 | EXTRAPOLATION | GPT-5.6 volume accept-rate on WN is UNMEASURED; the 10k pilot resolves it |
| ASM-2435 | STIPULATED | per-stage go/no-go on accept-rate + cache-hit + $/record + human-pass; floors at freeze |
| ASM-2437 | STIPULATED | profile-1 (65 primes) only; encoder rejection = rejection; no vocab change |
| ASM-2438 | STIPULATED | author-family ≠ judge-family downstream; authorFamily provenance makes it checkable |

**Deliberately NOT registered** (over-annotation trimmed; each design point restates an
already-committed rule and stays inline-tagged to its committed source — a design spec
should not mint an ASM per paragraph): the Stage-2+ source notes (§1.2
Wiktionary/Wikidata/BabelNet — forward-looking, non-load-bearing, each its own future
ingest-design pass; the two EXTRAPOLATIONs there keep inline resolution_paths), authoring
blindness (§2.2, the g9 selection-manifest rule verbatim), per-record
provenance/disclosure (§2.3, `docs/design-bulk-kernel.md` quadruple + the #44 manifest
guardrail), fail-closed repair/quarantine (§2.4, `CLAUDE.md` conventions +
`f1k-large-kernel-rebuild.md` §1.1), the warm worker pool (§3.3) and queue/shard mechanics
(§4.1, operational detail under ASM-2428/ASM-2429 + existing harness discipline),
two-plane storage (§4.2, the `docs/design-bulk-kernel.md` ruling), the pilot honesty cap
(§5.1, `coverage-growth-ingestion-plan.md` §0 + the g9 mechanical-upper-bound rule), and
validator-owned acceptance (§6 item 5, the #44 mandate verbatim, enforced by the §2
pipeline itself).

---

## 8. Self-check

- **Design-only / nothing committed?** ✅ No run, no spend, no GPU, no ingest, no freeze; no
  git commit/push. This file and the nine §7 register rows are uncommitted working-tree
  artifacts. The maintainer's session-close push protocol is **explicitly overridden by the
  task** ("Design only … nothing committed").
- **STIPULATED/MEASURED tagged?** ✅ Every load-bearing claim tagged; the only MEASURED
  claims cite committed bytes (`data/lexical-wn31/manifest.json`, `f1k-large-kernel-rebuild.md`
  §2, `a-f0-mint-economics-spec.md`, `ASM-1900/1902`, `docs/design-bulk-kernel.md`). All $/token
  economics are STIPULATED on a placeholder table (ASM-2431) with a preflight re-verify path;
  **no economics figure is a decision premise** — the gate decides on the measured pilot.
- **ASMs have real backing_ref?** ✅ Each registered row cites an existing repo artifact or
  the closed issue #44; no hollow refs. The registered EXTRAPOLATION (ASM-2434) carries its
  resolution_path with `load_bearing: false` (the register rule: a load-bearing
  EXTRAPOLATION cannot exist); the two Stage-2+ EXTRAPOLATIONs in §1.2 stay inline-tagged
  with resolution_paths, unregistered, and are non-load-bearing for any go decision.
- **Pseudonyms only?** ✅ Author "Kern (Fable design agent, designer-1)"; no real names beyond
  the maintainer handle `@jeswr`/email already in-repo.
- **GPT authors DRAFTS only; acceptance unchanged?** ✅ §2 — validator loop + human gate own
  acceptance; GPT never self-accepts; mechanical rate is an upper bound.
- **Guardrails covered?** ✅ formalism (ASM-2437), author≠judge (ASM-2438), no re-author
  kernel-v0 (§6.3), disclosure per record (§2.3/§6.4).
- **Caching first-class?** ✅ §3 — stable prefix, idempotent dedup/resumable, warm pool,
  millions-scale economics estimate with honesty cap.
- **Honesty caps present?** ✅ pilot cannot be quoted as adequacy/coverage/checkability
  (§5.1 cap); mechanical ≠ composite; DeepNSM 24/100 and checkability≠coverage priors surfaced.
- **Open risk flagged for the maintainer:** accept-rate at GPT-5.6 volume on WN is the single
  UNMEASURED unknown the design turns on (ASM-2434, EXTRAPOLATION — never a decision premise) —
  which is precisely why the 10k pilot gate exists *before* any 100k/1M spend.
```
```
