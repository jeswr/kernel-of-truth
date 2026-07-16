# GPT-5.6 draft-pipeline — WordNet-10k pilot (build-ready) + million-scale FUTURE track

> **Status:** DESIGN / SPEC ONLY, revision 2. Authorizes nothing to run, spend, ingest, or
> freeze. Maintainer approval + a `kot-reg/*` prereg-freeze are required before any spend.
> Author: Kern (Fable design agent, designer-1), for @jeswr. Date: 2026-07-16.
> **Revision note (r2):** rewritten against the build-readiness review verdict
> (`scratchpad/largekern-spec-review-verdict.txt`, NEEDS-WORK, 2026-07-16). Per that
> review's ruling — *"the current document can at most authorize the WordNet pipeline"* —
> the **authorizable surface of this document is the WordNet-10k pilot only** (§§1–10).
> The 100k and 1M+ stages are a documented **FUTURE track** (§11): direction, named
> preconditions, and honesty caps — **not** an executable stage and **not** authorized here.
> **Mandate:** issue #44 (CLOSED, maintainer-decided) — *"Large-kernel drafting (biggest
> win, zero collision): GPT-5.6 drafts candidate concept explications at volume for the
> scale-up track → every draft passes the encoder-validator loop + lint gates (acceptance
> stays with the explicator pipeline). **Not** the kernel's final NSM records — drafts
> only, validator-gated."* This is the *volume authorship* half of #44 (use 1); orthogonal
> to the `plain-v5-natural` generic-control arm (use 2A/2B), which it does not touch.

Binding constraints: `docs/kernel-design-directives.md` §§1–6; the epistemic-discipline
directive (every load-bearing claim tagged; established only when MEASURED or LIT-BACKED;
an EXTRAPOLATION is never a decision premise); `docs/design-bulk-kernel.md` (the
`semanticStatus` honesty ladder); `data/haiku-tier/modelauthored-schema.md` (the existing
model-tier precedent this design now follows exactly); `docs/next/design/
sense-split-first-construction.md` + `docs/next/design/f1k-large-kernel-rebuild.md`
(the kernel-v1 sense-split-first construction this drafting feeds);
`docs/next/design/plain-v5-register-lint-spec.md` §7 (the runtime seat ledger reused here).

**Epistemic tags** (as in `registry/assumptions.jsonl`): **[MEASURED]** read from committed
bytes / a diagnostic this tick; **[LIT-BACKED]** published, provenance disclosed;
**[STIPULATED]** a design choice or this designer's ruling, rationale given, never
evidence; **[EXTRAPOLATION]** a forward projection with a resolution_path, never a
decision premise. Register state: rows **ASM-2420, -2424, -2428, -2429, -2431, -2434,
-2435, -2437, -2438** were registered by r1 and are now **committed**; the register is
append-only, so r2 does not edit them — it **appends amending/tightening rows
ASM-2466 … ASM-2472** (working tree, nothing committed by this pass; ids follow the
working-tree max after a concurrent s5-human-readj pass registered ASM-2459 … 2463
mid-flight — 2464/2465 are left free for that writer). §12 maps old → new. Where an r1 claim is *retracted* (the
"10–20% of cold" cache economics; the "floors not in the design doc" clause of ASM-2435),
the retraction is explicit in the superseding row, per the review's ruling.

---

## 0. The one-paragraph answer (r2)

GPT-5.6-Sol becomes the **draft author** inside the *already-designed* kernel-v1
sense-split-first construction — it does not become a new pipeline and it never decides
sense boundaries. **Pilot scope, frozen here:** 10,000 **singleton WordNet-3.1 synset**
candidates (one synset = one candidate; no clustering decision exists anywhere in the
pilot path — §1), drafted through an OpenAI prompt-cached, Batch-priced, **transactionally
idempotent** pipeline (§§3–6), accepted only by the unchanged deterministic stack
(`validateExplication` → catalog-closed encode-sanity → lint/leakage gates → quarantine on
repair exhaustion). Every accepted draft lands as an **immutable `ModelDrafted` record in
its own bucket** — exactly the committed `ModelAuthored`-tier discipline — and only an
**individual human 4-binary endorsement mints a new `Explicated` record**; there is no
mutable status transition and a sampled review never promotes unsampled records (§2).
The pilot's go/no-go is **fully numeric and frozen in this document** (§10): repair limit
R = 2; hard API cap **$500** ledger-enforced; accept-rate floor **α = 0.70** (Wilson 95%
lower bound), cache-read floor **κ = 0.70** (input-token fraction, online leg), cost
ceiling **$c = $0.05 per accepted record** (all-in API), human-pass floor **h = 0.60**
(Wilson 95% LB on a blind stratified n = 200 sample, ⟺ ≥ 134/200 observed), with pinned
denominators, API-failure and abstention rules, and a $15-sub-capped micro-pilot that
measures the P/S/O token distribution before the main spend. The 100k → 1M+ expansion is
a **FUTURE track** (§11): documented, gated on the pilot's PROCEED plus named unfinished
design work (the authored clustering process, per-source extractors, licence
adjudications), and **not authorized by this document**.

**Honesty tier.** GPT-5.6 drafts land in `semanticStatus: "ModelDrafted"` — a separate,
visibly-second-class bucket below `Explicated`, parallel to the committed `ModelAuthored`
tier (`data/haiku-tier/modelauthored-schema.md`: a model-tier record "is a *candidate*
that mechanical gates have accepted and no human or federation has endorsed"; endorsement
"upgrades … by minting a proper record"). The mechanical pass rate never becomes the
acceptance claim (g9 rule: mechanical legality is an UPPER BOUND —
`data/authored-explication-set/validation/mechanical-summary.json`).

---

## 1. Pilot worklist: singleton synsets, mechanical and blind (review item 3 resolved)

The r1 spec claimed a "precomputed worklist" of synset *clusters*. The review correctly
found that within-frame clustering (rule R3(b)/(c) of the sense-split-first construction)
is an **authored** decision — `sense-split-first-construction.md` §3.1 lists "Within-frame
synset clustering (R3), senseTag choice" as **Authored, disclosed** — so a "precomputed"
cluster worklist smuggled an unstaffed authoring step. r2 resolves it by **removing
clustering from the pilot path entirely**:

- **Pilot candidate = one WordNet-3.1 synset.** One worklist row per synset;
  `conceptId` = the synset URN (`urn:lexical-wn31:[nvar]-[0-9]{8}`); cluster = {that
  synset} by construction. A single synset URN is a sound identity for a singleton — the
  review's objection to using one synset URN as a *multi-synset* cluster key does not
  arise, because no multi-synset cluster exists in the pilot. `[STIPULATED ASM-2466]`
- **The worklist builder is mechanical and item/kernel-blind by construction.** Inputs are
  exactly: the pinned WN31 shards (`data/lexical-wn31/`, source `sha256:3f7d8be8…`,
  110,049 type-level synsets [MEASURED: `data/lexical-wn31/manifest.json`;
  `f1k-large-kernel-rebuild.md` §2]) and the frozen-overlap denylist (§9.3). It reads **no
  benchmark bytes, no eval items, no kernel explication text, no model outputs**. The
  builder script is pinned and hashed in the pilot manifest; its output
  `data/kernel-v1-draft/worklist.jsonl` carries one row per candidate
  `{conceptId, lemma, pos, wnGloss, sourceRowSha256}`.
- **Sampling rule (pinned, seeded, single-draw):** 10,000 synsets drawn by a seeded
  stratified rule over POS × polysemy band (monosemous / 2–5 same-POS senses / ≥ 6),
  proportional to the WN31 composition, so the heavy tail (`break` 59 verb synsets,
  `make` 49, `give` 44 [MEASURED: ASM-1900]) is represented. Seed registered at
  prereg-freeze; a re-draw is a new experiment id.
- **Disclosed consequence:** drafting per-synset over-splits relative to kernel-v1's
  eventual within-frame clusters (WN is over-fine — 59 `break` verb synsets vs ~6 plausible
  kernel clusters). That is acceptable and *measured*, not hidden: byte-identical
  explications across sibling synsets are caught by the existing G1 duplicate-identity
  gate and reported as a profile-1 expressivity/granularity number
  (`sense-split-first-construction.md` §2.1 G1), never silently merged.
- **The authored clustering step is FUTURE-track work with a named owner.** For any
  multi-synset cluster (100k stage onward): clustering is authored by the **explicator
  role** (per §3.1 of the sense-split construction), independently reviewed, never
  GPT-5.6 and never this pipeline; its staffing and cost are a *precondition* of the 100k
  gate (§11.1), currently unpriced. Canonical multi-synset cluster key (frozen now so the
  ledger schema never changes): `clusterKey = sha256(canonicalJSON({members: sortedSynsetURNs,
  frame: frameURN|null, clusterVersion}))`. `[STIPULATED ASM-2466]`

---

## 2. Draft-vs-endorsed states: schema and minting rule (review items 6–7 resolved)

r1 proposed a mutable `ModelDrafted → Explicated` transition. That conflicted with the
committed governance (`docs/design-bulk-kernel.md`: `Explicated` is hand-authored;
`data/haiku-tier/modelauthored-schema.md`: the model tier is a separate bucket and human
endorsement "upgrades `candidateStatus` into the real status **by minting a proper
record**"). r2 adopts that committed discipline verbatim.

### 2.1 State machine (per candidate; all states terminal-or-forward, no mutation)

```
GENERATED ──validator+encode+lint pass (≤ R repairs)──▶ MECHANICALLY_VALID
   │                                                        │
   │ repair exhausted / abstention / malformed              │ written as an immutable
   ▼                                                        ▼ ModelDrafted record
QUARANTINED(code)  [terminal, never a record]        ModelDrafted record (immutable)
                                                            │
                                          individual human 4-binary endorsement
                                          (ALL four yes; blind sheet §4.3)
                                                            │
                                                            ▼
                                          MINT: a NEW Explicated record is created
                                          (concept-hash pipeline; draft untouched)
```

- **`ModelDrafted` record (schema `kernel-v1-draft/1`,** mirroring `haiku-tier/1`):

```jsonc
{
  "schema": "kernel-v1-draft/1",
  "id": "urn:kernel-v1-draft:<synsetURN>@v<conceptVersion>",   // immutable identity
  "label": "<lemma>", "semanticStatus": "ModelDrafted",
  "candidateStatus": "Explicated",
  "gloss": "<drafted scholarly prose>",
  "record": { /* kot-ast/1, profile-1 */ },
  "gatesPassed": true,
  "provenance": { /* full block, §8 */ }
}
```

  Records live in JSONL shards (§7.2), each record's `recordSha256` in the shard
  manifest. **A `ModelDrafted` record is never edited.** Any change (contract bump, source
  fix) is a new `conceptVersion` → a new id → a new ledger row (§6). `[STIPULATED ASM-2470]`
- **Minting rule.** Individual human endorsement = one 4-binary review (same-sense ·
  intension · scholarly · AST/prose consistent, ALL yes; blind sheet per §4.3) of **that
  record**, logged in an append-only endorsement ledger
  `data/kernel-v1/endorsements.jsonl` `{draftId, reviewId, reviewer, date, pass}`. A pass
  **mints a new record** into `data/kernel-v1/concepts/` via the concept-hash pipeline
  with `semanticStatus: "Explicated"`, `derivedFromDraft: <draftId>`, and the full draft
  provenance carried forward (the model authorship is disclosed forever). The draft
  record remains, immutable, in its bucket. There is **no in-place status transition
  anywhere**. `[STIPULATED ASM-2470]`
- **Sampling never promotes.** The pilot's n = 200 review sample (§10) endorses exactly
  the records it individually reviewed (those passers may mint); the other ~thousands of
  accepted drafts **stay `ModelDrafted`** regardless of the gate verdict. The gate verdict
  is a *pipeline-quality* estimate authorizing the next stage's spend — never a promotion
  event. Bulk endorsement at scale is therefore a *human-throughput* problem, priced in
  the FUTURE track (§11.1), not hand-waved here.
- **Governance reconciliation.** `design-bulk-kernel.md`'s "Explicated — hand-authored …
  never auto-generated" is satisfied: nothing is auto-promoted; every `Explicated` record
  minted from a draft exists only through a per-record human act, exactly the
  `modelauthored-schema.md` §8-semantics path, with model authorship disclosed in the
  record and manifest. Coverage measurements bucket `ModelDrafted` separately
  ("ModelDrafted-reachable" band), as the AxiomsOnly precedent prescribes; consumers that
  require `Explicated` mechanically reject `ModelDrafted` (§9.2).

### 2.2 Authoring blindness (unchanged from r1; binding)

The draft prompt contains **only**: headword + synset id + the aligned WN gloss + pinned
source extracts + the cached NSM grammar / profile-1 lexicon / few-shot / lint contract.
It never contains benchmark items, the kernel's other explications beyond the pinned ref
catalog, coverage rank, matched eval questions, or any model-performance data. Prompt +
transcript pinned per batch. This is the g9 selection-manifest rule verbatim.
`[STIPULATED: the g9 rule, restated; committed]`

### 2.3 What stays fail-closed (unchanged)

A draft failing `validateExplication` gets the **real** `ERR_*` list into the repair call;
after **R = 2** repairs (≤ 3 model calls total) it is quarantined with its failure code,
never coerced. Leakage (8-token overlap with any eval item after trigger/stopword removal)
is a hard reject. Structured model abstention (`{"cannot_draft": …}`, the haiku-tier
`cannot-formalise` precedent) is terminal quarantine, no repair. All quarantines are data,
logged with full provenance. `[STIPULATED: CLAUDE.md no-silent-fallback +
`f1k-large-kernel-rebuild.md` §1.1, restated; R frozen by ASM-2468]`

---

## 3. OpenAI cache semantics (review items 10–11 resolved)

r1 imported Anthropic Messages-API syntax (`cache_control:{type:"ephemeral"}`) and modeled
cache warmth as a client-worker property. r2 specifies the **actual OpenAI mechanism**,
per the review-cited provider references — all figures below **[LIT-BACKED: OpenAI
prompt-caching guide, OpenAI Batch guide, GPT-5.6 Sol model page, as cited by the
2026-07-16 review; re-verified against the live provider reference at staging preflight,
any discrepancy an ops amendment BEFORE first spend — the ASM-0601 discipline verbatim]`:

- **Exact-prefix caching with cache keys.** OpenAI caches on exact prompt prefixes; cache
  routing/partitioning uses explicit **`prompt_cache_key`** values and breakpoint options,
  not per-block markers. Cached input is priced at **0.1× normal input**; output is
  **6× uncached input**. Current TTL guidance: **~30-minute minimum**; a partition idle
  longer than the TTL re-populates on next request.
- **~15 requests/minute per cache key.** Higher-volume traffic must be partitioned across
  keys, and **each partition is its own cache population** — shards do NOT automatically
  share one warm prefix. Design: online worker *w* uses
  `prompt_cache_key = sha256(cachePrefixHash ‖ w)`; W = 4 online workers ⇒ ≤ 60 req/min
  online. Re-population overhead is modeled and negligible at pilot scale: 4 partitions ×
  ~10 TTL windows × 9,200 prefix+suffix tokens × $2.00/Mtok ≈ **$0.74** per pilot
  [STIPULATED arithmetic on the §5 placeholder table].
- **Batch API.** 50% price on input and output; limits **50k requests / 200 MB input file
  per job / 24 h completion window**; cached tokens still count against rate limits;
  per-tier token queues apply. Concrete pilot consequence: every Batch request embeds the
  full prefix **bytes** in the input file (no cross-request dedup in the file), so at
  P ≈ 8k tokens ≈ 32 kB the 200 MB file limit binds first: 10k drafts ship as **≥ 3 jobs
  of ≤ 4,000 requests (~160 MB each)**, serialized against the account's measured batch
  queue. `custom_id` = the ledger idempotency key (§6). Expired-incomplete requests bill
  nothing and are retried per §10.4.
- **Whether Batch requests are served cache reads is UNMEASURED** and is a named
  micro-pilot endpoint (m3, §5.2). Routing (Batch vs online) is decided on the micro-pilot's
  measured $/concept, then frozen at prereg. `[STIPULATED ASM-2467]`
- **Stable prefix (unchanged in substance from ASM-2428):** the four invariant blocks
  (NSM grammar contract; profile-1 lexicon + pinned ref catalog; few-shot exemplars —
  now §9.4-governed, g9 records banned; lint contract), deterministically serialized,
  content-hashed (`cachePrefixHash`), changed only by a deliberate contract bump =
  re-freeze. Prefix must exceed the provider minimum cacheable size (per the OpenAI guide;
  verified at preflight via the tokenizer count). Variable suffix = headword + synset id +
  WN gloss + extracts; repair suffix = draft + real `ERR_*` list.

---

## 4. Acceptance stack, human review instrument (unchanged mechanics, pinned)

### 4.1 Mechanical leg (per draft, deterministic, local)

1. `validateExplication` — per-record, fail-closed `ERR_*` (`encoder/src/validate.ts`).
2. **Catalog-closure lint (NEW, load-bearing for §7):** every `conceptHead`/concept ref id
   must be in the **pinned ref catalog** (kernel-v0 + molecules-v0 at their pinned
   manifest state). The syntax validator deliberately accepts any nonempty id
   [MEASURED: `encoder/src/validate.ts` lines 124–138], so closure is enforced at the lint
   layer: `ERR_REF_OUTSIDE_CATALOG`. Consequence: drafts are leaf nodes of the reference
   DAG — no draft ever references another draft — which is what makes sharded validation
   sound (§7.1). `[STIPULATED ASM-2471]`
3. `encodeConceptSet` encode-sanity per bounded shard (no NaN, norm ok) with the catalog
   pre-resolved (§7.1).
4. Lint gates: gloss standard 1–9 (`f1k-large-kernel-rebuild.md` §1.1), non-circularity,
   15–100 words, ≤ 128 tokens under the pinned tokenizer, 8-token leakage check.
5. Repair loop ≤ R = 2; then quarantine with code.

### 4.2 Human leg (endorsement instrument)

The 4-binary review (same-sense · intension accurate · scholarly/self-contained ·
AST/prose consistent; ALL yes) on the blind sheet: reviewer sees label, drafted gloss,
aligned WN gloss/synset, structural rendering — **never** coverage rank, benchmark items,
model identity, or model outputs beyond the draft under review. Reviewer: a
maintainer-recruited human (never the pipeline operator, never any model seat). Review
cost planning anchor: ~12–22 min/record including revisions [MEASURED range implied by
`f1k-large-kernel-rebuild.md` §3.3's 20–35 h / 96 concepts planning band].

### 4.3 Pilot review sample (gate instrument, not promotion)

n = **200** records drawn seeded + stratified (POS × polysemy band, proportional) from the
main run's mechanically-accepted drafts; single draw; the draw script and seed pinned at
prereg. Planning load: 200 × 12–22 min ≈ **40–75 h** human review — budgeted as hours in
the pilot plan, **excluded from the $c metric** (which is API-only; rationale: bulk
endorsement economics is FUTURE-track minting work, priced there — §11.1), and **reported**
alongside the gate verdict. Sampled passers may mint per §2.1; nothing else promotes.

---

## 5. Economics: measured-token plan + honest cost model (review item 12 resolved)

### 5.1 The corrected claim

> **RETRACTION (supersedes the r1/ASM-2431 "warm ≈ 10–20% of cold" claim).** With output
> priced at 6× uncached input [LIT-BACKED, §3], output + repair tokens dominate the warm
> residual even when prefix tokens dominate *counts*. Under the modelled distribution
> below, warm-online cost ≈ **51% of cold-online** — caching is a **~2× lever**, Batch is
> another **~2× lever**, and they may or may not compose (micro-pilot m3). Caching is
> *material*, not *feasibility-defining*, at pilot scale. `[STIPULATED ASM-2467]`

**Cache-fraction definition (fixed, one definition everywhere):**
`κ = cache-read input tokens / total input tokens` — **input tokens only; output never
appears in the denominator.** Structural ceiling for a draft call: `P/(P+S)`; for the run
mix including repairs: `r·P / (r·P + S_draft + (r−1)·S_repair)`.

### 5.2 Modelled distribution → measured at the micro-pilot

All token counts **[STIPULATED placeholders]** until the micro-pilot measures them from
real `usage` fields; the placeholder price table is **[STIPULATED]**, shaped by the
LIT-BACKED ratios (cached = 0.1× input; output = 6× input; Batch = 0.5×):

| symbol | meaning | modelled | measured by |
|---|---|---|---|
| P | cached prefix tokens | 8,000 | micro-pilot m1 |
| S_draft | draft suffix | 1,200 | m1 |
| S_repair | repair suffix (draft + ERR list) | 2,700 | m1 |
| O | output tokens / call (incl. any reasoning tokens billed as output) | 900 | m1 |
| r | calls/concept at R = 2 | 1.8 [MEASURED at A-F0 for the Haiku definer; EXTRAPOLATION here] | m4 |
| price | input $2.00 / cached $0.20 / output $12.00 per Mtok; Batch ×0.5 | placeholder | preflight (ASM-0601 discipline) |

Arithmetic (shown so the conclusion is checkable; per concept):

- **Cold online:** 1.8 × ((8,000+~1,900avg)×$2 + 900×$12)/10⁶ ≈ **$0.055**
- **Warm online:** draft $0.0148 + 0.8 repair × $0.0178 ≈ **$0.029** → 51% of cold
- **Batch, no cache:** ≈ **$0.026** — nearly identical to warm-online
- **Batch + cache (if they compose):** ≈ **$0.0145**

→ modelled pilot API spend ≈ **$150–$290** for 10k; modelled $/accepted at α = 0.70 ≈
**$0.021–$0.041** — under the $c = $0.05 ceiling with 1.2–2.4× headroom. Structural cache
ceiling at the modelled mix: 14,400/17,760 ≈ **0.81**, so the κ = 0.70 floor detects gross
cache failure without gating on the model's own placeholder. `[STIPULATED ASM-2467/2461]`

**Context, not a premise:** the A-F0 baseline ($0.078/legal record; 1.8 calls/concept
[MEASURED: `a-f0-mint-economics-spec.md`]) is API-equivalent accounting on another model
and transport, and A-F0 itself declares Batch economics and volume-scale yield unmeasured
(§S8; ASM-0607). It is quoted as prior context only; **no gate below references it.**

### 5.3 Micro-pilot P0 (sub-capped $15, inside the $500 cap)

n = 100 worklist concepts (seeded draw; **excluded from the 10k main-gate denominators**;
their spend still counts in $c). Endpoints: **m1** measured P/S/O distribution from usage
fields; **m2** online cache-read fraction + TTL/partition behaviour; **m3** Batch-cache
calibration (do Batch requests get cache reads?); **m4** measured r at R = 2; **m5**
accept-rate first look (no gate authority at n = 100). Outputs: routing decision
(Batch/online mix), gen-settings selection from the pinned candidate set
(`max_output_tokens = 2,048` fixed; `reasoning_effort`/verbosity chosen from the candidate
set listed in the prompt manifest, then frozen), and the measured token distribution —
all frozen into the prereg record before the main run. `[STIPULATED ASM-2468]`

---

## 6. Transactional idempotency (review item 13 resolved)

r1's JSONL-pre-check ("look up, then call") is not idempotent: two workers can both see a
missing tuple; a crash after provider submit but before ledger append orphans a paid job.
r2 replaces it with a **transactional ledger + write-ahead intent + provider-side
reconciliation key**: `[STIPULATED ASM-2469]`

- **Store:** `data/kernel-v1-draft/ledger.sqlite` (SQLite, WAL mode — transactional,
  single-file, no server; correct for this box's 2 shared cores and N ≤ a few workers).
  `data/kernel-v1-draft/draft-ledger.jsonl` is a derived, append-only **passive export**
  for audit (exactly the beads architecture: DB authoritative, JSONL passive).
- **Identity (fixed):** ledger primary key = `(conceptId, conceptVersion)`. Each row
  stores an immutable `versionHash = sha256(sourceRowSha256 ‖ promptHash ‖
  cachePrefixHash ‖ modelSnapshotId ‖ genSettingsHash ‖ validatorHash ‖ lintHash)`.
  Role of the prompt hash resolved: lookups key on `(conceptId, conceptVersion)` **only**;
  if the runner's *computed* current `versionHash` differs from the stored row's, it
  **fails closed** (`ERR_VERSION_DRIFT`) — no silent redraft under a drifted contract.
  Redrafting requires an explicit, registered **bump directive** (a reviewed file listing
  `conceptId`s, the new `conceptVersion`, reason), which creates *new* rows with a
  `supersedes` pointer. "Never re-draft accepted" now means precisely: never re-draft the
  same `(conceptId, conceptVersion)`; a bump is a new identity, and the superseded
  accepted draft record stays immutable in its shard.
- **State machine (durable, enforced by single-transaction transitions):**
  `CLAIMED → SUBMITTED(requestId|batchId) → COMPLETED(outcome)` with outcomes
  `ACCEPTED | QUARANTINED(code) [terminal content rejection] |
  PROVIDER_FAILED [retryable, §10.4]`; plus `FROZEN` (irreversible; §9.3).
  Terminal content rejection and retryable provider failure are **distinct states** —
  a quarantine is never retried, a provider failure never quarantines content.
- **Protocol per candidate:**
  1. `BEGIN IMMEDIATE; INSERT (conceptId, conceptVersion, state=CLAIMED, owner, ts,
     idempotencyKey); COMMIT` — the UNIQUE primary key makes the claim **atomic**; a
     second worker's insert fails and it moves on. `idempotencyKey =
     "kv1d-" + versionHash[:24]`, generated **before** any network call.
  2. Submit to the provider **carrying the idempotencyKey** as the request's
     `custom_id` (Batch) / metadata (online).
  3. Transition to `SUBMITTED` with the returned request/batch id; on response, verify +
     record `responseSha256`, run acceptance locally, transition to `COMPLETED`.
- **Crash windows closed by reconciliation, not hope:** on startup (and periodically) a
  sweeper re-examines every `CLAIMED`/`SUBMITTED` row older than a timeout and **queries
  the provider by `custom_id`/batch listing**: job found → adopt its result (no double
  spend); provably absent → re-claim and resubmit. Because the `custom_id` is
  deterministic from the row, every paid job is discoverable — a crash after submit can
  no longer orphan spend, and a duplicate submit is detectable server-side.
  **Pilot precondition P5:** a crash-recovery test (kill −9 between submit and record,
  against a mock provider) must pass before launch.
- Runs remain checkpointed/`nohup`+`setsid` per harness discipline; the ledger frontier is
  the resume point (ASM-2429's intent, now with sound mechanics).

---

## 7. Validator throughput + storage (review items 8–9 resolved)

### 7.1 Bounded-shard validation (benchmarked, not asserted)

The review is right: whole-corpus `encodeConceptSet` retains every vector
(`Map<string, Float64Array>`) — at 1M × D = 8192 × 8 B ≈ **61 GiB**, impossible here; and
`data/validate.mjs` is hard-coded to kernel-v0 [MEASURED: `data/validate.mjs` line 28].
The r2 plan:

- **Catalog-closed drafts ⇒ trivially shardable.** With `ERR_REF_OUTSIDE_CATALOG` (§4.1)
  every draft references only the pinned, pre-resolved catalog, so any partition of drafts
  is dependency-complete. `encodeConceptSet` already accepts pre-resolved external vectors
  (`opts.concepts` [MEASURED: `encoder/src/encoder.ts` lines 366–385]): the catalog
  (~108 kernel-v0+molecules-v0 vectors ≈ 7 MB) is encoded **once**, then each shard of
  **B = 1,000 drafts** encodes with the catalog injected and **drops its vectors after the
  no-NaN/norm check** (vectors are re-derivable; never stored wholesale —
  `design-bulk-kernel.md` ruling). Peak per shard: 1,000 × 65 kB ≈ 65.5 MB + catalog +
  runtime.
- **Measured anchor (this box, this tick):** full kernel-v0 validate+encode (54 records,
  D = 8192, ref depth ≤ 3, including node startup) = **2.22 s wall, 108 MiB peak RSS**
  [MEASURED: `/usr/bin/time -v node data/validate.mjs`, 2026-07-16] ⇒ ≥ ~24 records/s
  lower bound ⇒ 10k ≈ **≤ 7 min per full validation pass**, RSS flat by construction.
  Scope caveat: kernel-v0 records are small and curated; drafted records may be larger.
- **Pilot precondition P4 (instrument gate):** parameterize `validate.mjs`
  (`--kernel/--shard`, already an f1k-rebuild deliverable) and **benchmark 1,000 synthetic
  drafts** on this box, recording records/s and peak RSS into the pilot manifest.
  Launch requires the measured full-10k validation projection ≤ 1 h and peak RSS ≤ 1 GiB —
  generous bounds that exist so the numbers are *measured*, not assumed.
  `[MEASURED anchor + STIPULATED plan: ASM-2471]`

### 7.2 Storage format (one format, measured sizes)

- **Drafts: JSONL shards, never per-concept files.** `data/kernel-v1-draft/records/
  shard-NNNN.jsonl.gz`, ≤ 5,000 records/shard, sha256-per-shard manifest; a shard is
  complete only when its validation checks are green (fail-closed). The r1 diagram's
  one-JSON-file-per-concept applies **only** to endorsed `Explicated` records in
  `data/kernel-v1/concepts/` — a human-paced, small population (matches the existing
  54-file kernel-v0 layout).
- **Measured record-size anchor:** kernel-v0 concept records, n = 54: mean **3,407 B**,
  median 3,408, p90 5,078, max 7,316 [MEASURED: `data/kernel-v0/concepts/*.json`,
  2026-07-16]. With the §8 provenance block (modelled +~1.2 kB) → plan **~5 kB/record**:
  10k pilot ≈ **50 MB** records. Transcripts: **the prefix is stored once, by
  `cachePrefixHash` reference — never per record**; per-call suffix+output ≈ 2.1k tokens
  ≈ ~8 kB text × r = 1.8 ⇒ ~15 kB/concept ⇒ 10k ≈ **150 MB** raw (gzipped shards ~⅓).
  Ledger: one row/candidate + events, ≪ 50 MB.
- **Git discipline:** manifests + endorsed records + ledger JSONL export in git; draft
  shards + transcripts stay out of git (box storage + the existing backup path). The
  million-scale object-store decision is FUTURE-track (§11.1) with these measured numbers
  as its sizing input (1M ⇒ ~5 GB records + ~15 GB transcripts pre-compression — *modelled
  from the measured per-record anchor*, [EXTRAPOLATION, resolution_path: the pilot's
  measured record-size distribution over drafted records]). `[STIPULATED ASM-2471]`

---

## 8. Provenance (review item 14 resolved)

Per-record provenance block (extends the mandatory bulk quadruple
`{source, sourceVersion/hash, extractorVersion/hash, extractionDate}`):

```jsonc
"provenance": {
  // authorship — roles split, no compound strings
  "draftAuthor":      "gpt-5.6-sol-<exact dated snapshot id>",  // as *sent*
  "returnedModelId":  "<model field of the actual response>",    // as *returned*
  "authorFamily":     "gpt",
  "pipelineOperator": "runner-1 (kb-pipeline-runner)",           // pseudonym, agent role
  "endorser":         null | "<review-id>",                      // set only on the MINTED record

  // request identity + attestation
  "conceptId": "...", "conceptVersion": 1, "versionHash": "sha256:…",
  "idempotencyKey": "kv1d-…", "requestId"/"batchId": "…", "customId": "…",
  "promptHash": "sha256:…", "cachePrefixHash": "sha256:…",
  "genSettings": {"max_output_tokens": 2048, "reasoning_effort": "<pinned>", "...": "..."},
  "sourceRowSha256": "…",                       // the WN worklist row
  "responseSha256": "…",                        // raw provider response bytes
  "transcriptRef": "shard-NNNN#offset",         // suffix+output transcript location
  "usage": [ /* per call: input/cached/output tokens, costUSD */ ],
  "repairCalls": 0..2,

  // acceptance attestation
  "validatorHash": "40e8c8ba4c3d…",             // encoder content-hash at acceptance
  "lintHash": "sha256:…",
  "acceptancePath": "validateExplication+catalogLint+encodeShard+lint",
  "seatLedgerRef": "…"                          // §9.1 entry
}
```

**Corrected reproducibility claim:** drafting is **not byte-reproducible** — the provider
documents that identical requests need not return identical output [LIT-BACKED: OpenAI
FAQ, per the review], and human endorsement is not deterministic. What the record
supports is (a) **attestation** — every input and output is hashed and traceable to a
provider request id; and (b) **re-runnable acceptance** — `validateExplication` and the
lints are pure, so the mechanical accept/reject of the *stored* draft is re-derivable
byte-identically. r1's "re-derivable: same prompt + same snapshot → attestable draft" is
narrowed to exactly that. `[STIPULATED: correction; carried in ASM-2472's enforcement row]`

---

## 9. Mechanized guardrails (review items 15–16 resolved)

Prose rules become checked invariants: `[STIPULATED ASM-2472]`

1. **Family disjointness = the existing fail-closed seat machinery, reused.** The
   drafting store writes a `kot-seat-ledger/1` ledger with **entry 0 = the author seat**
   (exact dated `gpt-5.6-sol` id). Every LLM invocation in any downstream seat role over
   these records goes through the pinned invoker (`invoke_seat.py` pattern), which
   resolves families via the pinned family map and refuses **before dispatch** on
   same-family or UNKNOWN (FD-1/FD-2), with orphan and hash-chain-integrity sweeps
   (FD-5/FD-6) — the ASM-2458 mechanism verbatim, pointed at this store
   (`plain-v5-register-lint-spec.md` §7). `authorFamily` remains as record metadata; the
   **resolver + ledger are the enforcement**, never a string compare. Consumer prereg lint
   runs the disjointness validator against entry 0.
2. **Consumer status eligibility is a builder gate.** Corpus/experiment builders take an
   explicit eligible-status allowlist (the f1k `--eligible-concepts` pattern) and
   **fail closed** (`ERR_STATUS_INELIGIBLE`) if a `ModelDrafted` record reaches a slot
   requiring `Explicated`. Coverage tooling buckets `ModelDrafted`-reachable separately.
   Leakage/exclusion lints apply **symmetrically** to drafted-kernel and generic-control
   arms (plain-v5 contract cross-reference).
3. **Frozen-record exclusion is a worklist check, not prose.** The worklist builder
   excludes every synset in `data/lexical-wn31/alignment-kernel-v0.json` (107 alignment
   rows [MEASURED this tick]) — kernel-v0 is frozen forever and is never re-drafted,
   shadowed, or grandfathered; violation = `ERR_FROZEN_OVERLAP` at build time. Ledger
   state `FROZEN` is irreversible.
4. **Few-shot exemplars must be *actually* endorsed — the g9 50 are banned.** g9's own
   committed summary says the blinded human review was never done
   (`blinded_review_done=0`; "NO verdict is claimable" [MEASURED:
   `data/authored-explication-set/validation/mechanical-summary.json`]). Using them as
   "accepted" demonstrations would propagate an unreviewed style/quality prior at scale.
   **Exemplar protocol (pilot precondition P2):** 12 candidate kernel-v0 records receive
   the full 4-binary human review; **k = 8 passers** become the pinned few-shot set
   (sha-pinned in the prompt manifest, inside `cachePrefixHash`). ~3–4 h human effort,
   scheduled before prefix freeze. If fewer than 8 pass, the shortfall is a finding and
   the prefix ships with the passers only.

---

## 10. THE FROZEN 10k GATE (review item 2 resolved — all numbers concrete)

> These numbers are **frozen in this design revision** and are copied **verbatim** into
> the `kot-reg/*` prereg record; prereg-freeze may not alter them (an alteration is a new
> design revision + review). This deliberately supersedes r1/ASM-2435's "floors set at
> prereg-freeze, not in this design doc" clause, per the build-readiness review's ruling.
> `[STIPULATED ASM-2468]`

### 10.1 Frozen operational parameters

| parameter | frozen value |
|---|---|
| Worklist | 10,000 singleton WN31 synsets, seeded stratified draw (§1), single-draw |
| Repair limit **R** | **2** (≤ 3 model calls/concept); abstention = terminal, no repair |
| `max_output_tokens` | **2,048** per call |
| Gen settings | pinned candidate set in the prompt manifest; selected once at micro-pilot; frozen at prereg |
| Online workers / cache keys | W = **4**, one `prompt_cache_key` each, ≤ 15 req/min each |
| Batch jobs | ≤ 4,000 requests/job (200 MB bound), serialized |
| Micro-pilot | n = 100, sub-cap **$15.00**, endpoints m1–m5 (§5.3), excluded from main denominators |
| Human sample | n = **200**, seeded stratified (POS × polysemy band), blind 4-binary |

### 10.2 Frozen budget + kill ladder (worst-case spend is the cap, by construction)

- **Hard pilot API cap: $500.00**, enforced by ledger hard-abort (every call's cost is
  written to the ledger before the next call is authorized; the A-F0 hard-abort
  discipline). Includes micro-pilot, calibration, repairs, and all failed attempts.
- **Kill ladder:** checkpoint at **$50** (require: ≥ 500 concepts attempted, κ diagnostic
  ≥ 0.50, running accept-rate ≥ 0.40 — else abort INVALID-INSTRUMENT); checkpoint at
  **$250** (require ≥ 45% of worklist attempted — else abort INVALID-INSTRUMENT);
  hard-abort at $500.
- **Reproducible worst case:** because the abort is fail-closed and ledger-enforced,
  worst-case API spend ≡ **$500.00** exactly; plus human review **40–75 h** (planning
  band, §4.3) and this box's CPU (validation ≤ 1 h measured bound, §7.1). Modelled
  expected spend: $150–$290 (§5.2).

### 10.3 Frozen endpoints, denominators, decision rule

**Denominators (fixed):**
- `attempted` = worklist items with ≥ 1 completed (billed) model response. Items whose
  every call ended in provider/transport failure are **PROVIDER_FAILED items**, excluded
  from `attempted` and reported separately.
- `accepted` = mechanically accepted within ≤ 3 calls (§4.1).
- Abstentions, malformed outputs (JSON parse failure counts as an attempt and enters
  repair once with the parse error), and repair-exhausted quarantines are **failures
  inside the denominator**.

**Endpoints and floors — PROCEED iff ALL four hold:**

| # | endpoint | rule | frozen threshold |
|---|---|---|---|
| 1 | **accept-rate** = accepted / attempted | Wilson 95% **lower bound** | **α = 0.70** |
| 2 | **cache-read fraction** κ = cache-read input tokens / total input tokens, **online leg** (input-only denominator; if micro-pilot routes ≥ 95% of draft calls to Batch and m3 shows Batch serves no cache reads, κ is computed over the online/repair leg and reported for Batch separately) | point estimate from ledger usage sums (deterministic, no sampling) | **κ = 0.70** |
| 3 | **$/accepted-record** = ALL pilot API spend (micro-pilot + calibration + every failed/quarantined/repair call) ÷ accepted | point value from ledger | **$c = $0.05** |
| 4 | **human-pass-rate** on the n = 200 blind sample | Wilson 95% **lower bound** (⟺ observed ≥ **134/200**) | **h = 0.60** |

**Verdicts:** all four hold → **PROCEED** (authorizes designing the 100k stage's prereg,
not its spend). Any miss → **NO-GO / reassess** (directives §4 fork discipline; never
silent proceed). Instrument failure — PROVIDER_FAILED items > **2%** of the worklist, or
a kill-ladder abort — → **INVALID-RERUN**: no scientific verdict; a re-run requires a
fresh registration and fresh cap. The verdict is a **pure function of the ledger + the
review sheet**; anyone re-computing the four numbers from the committed ledger export and
the endorsement ledger must reach the same verdict.

### 10.4 API-failure and retry policy (frozen)

Provider/transport failures (HTTP 5xx, timeouts, Batch expiry) are **retryable**: ≤ 3
retries with exponential backoff per call, then the item is marked PROVIDER_FAILED
(excluded from `attempted`, counted toward the 2% instrument bound). Content failures
(validator rejection, lint failure, malformed output, abstention) are **never retried
beyond the R = 2 repair budget** and always stay in the denominator. Billed-but-failed
spend always counts in $c. Distinction enforced by the §6 ledger states.

### 10.5 What the pilot can never be quoted as (honesty cap, unchanged)

The pilot prices *drafting throughput + mechanical acceptance + sampled human quality* on
*WordNet singletons* at *10k*. It is **not** a semantic-adequacy measurement of a drafted
kernel (DeepNSM ≈ 24/100, wave-1), **not** a coverage or checkability claim
(`coverage-growth-ingestion-plan.md` §0), and its accept-rate is a legality/review rate,
never a truth claim. Mechanical rate remains an UPPER BOUND on composite acceptance (g9
rule). GPT-5.6 volume accept-rate remains the single UNMEASURED unknown the design turns
on — the pilot exists to measure it `[EXTRAPOLATION ASM-2434, unchanged, resolution_path:
this pilot]`.

### 10.6 Pilot preconditions (all must be green before prereg-freeze)

P1 worklist builder + `ERR_FROZEN_OVERLAP` check green on the pinned WN31 shards;
P2 exemplar review done, k ≤ 8 passers sha-pinned (§9.4);
P3 micro-pilot complete, m1–m5 measured, routing + gen settings frozen (§5.3) —
   the only precondition with spend, inside the $15 sub-cap and only after maintainer
   approval of this design;
P4 validator benchmark measured + `--kernel/--shard` refactor landed (§7.1);
P5 ledger crash-recovery test passed against a mock provider (§6);
P6 preflight: live price table + cache/Batch semantics re-verified vs §3 (ASM-0601
   discipline); API key provisioned by the maintainer (none on this box — checked at A-F0,
   2026-07-10); account tier + batch queue recorded;
P7 `kot-reg/*` record frozen carrying §10 verbatim; mock run ($0) green.

---

## 11. FUTURE track: 100k and 1M+ (documented, NOT authorized)

> **Authorization boundary (the review's ruling, adopted):** nothing in this section is
> executable under this document. Each stage requires its own design pass + review +
> prereg. This section exists so the pilot is built pointing in the right direction and
> so every known gap has a name and an owner. Scale figures remain STIPULATED targets,
> never counts, never premises `[STIPULATED ASM-2424, unchanged]`.

### 11.1 100k stage (WordNet remainder) — named preconditions

1. Pilot PROCEED (§10.3).
2. **The authored clustering design pass**: within-frame clustering (R3) as an explicator-
   owned, independently reviewed process with the §1 `clusterKey` identity; staffed and
   costed (currently unpriced — the review's finding stands).
3. **Endorsement throughput plan**: at the pilot's measured h and 12–22 min/record,
   individually endorsing even 10% of 100k drafts is ~2,000–3,700 h of human review —
   the FUTURE track must either budget it, or scope which slices get endorsed (e.g.
   panel-priority concepts), or keep the bulk permanently `ModelDrafted`. This is a
   maintainer decision the pilot's data will inform; it is not decided here.
4. Batch/account-tier schedule measured (P6 data), storage moved per §7.2 sizing
   (object store / LFS decision), validator sharding re-benchmarked at 100k.
5. Fresh $ cap registered; same four endpoints, floors re-derived from the pilot's
   measured envelope.

### 11.2 1M+ stage (beyond WordNet) — direction only

Wiktionary (bespoke sense-split extractor; CC BY-SA obligations into provenance)
`[EXTRAPOLATION, resolution_path: extractor design + licence verification pass]`;
Wikidata lexeme/sense layer only (the item layer is world-layer, wrong tier — committed
`design-bulk-kernel.md` ruling); BabelNet as alignment oracle only unless its
research-restricted licence clears `[EXTRAPOLATION, resolution_path: licence
adjudication]`. Cross-source dedup anchors on WN synsets where they exist (R5 single-source
disclosure otherwise). Per-source gates + licence-clearance gates; there is no generic RDF
extractor (`coverage-growth-ingestion-plan.md` §2). The scale-census 207,733 figure
remains an unmerged upper bound, never 207,733 independent candidates [MEASURED:
`f1k-large-kernel-rebuild.md` §2].

---

## 12. Assumptions registered this pass (r2)

Seven rows **appended** to `registry/assumptions.jsonl` (working tree only — nothing
committed by this pass), ids **ASM-2466 … ASM-2472** (committed max was ASM-2458; a
concurrent s5-human-readj pass registered 2459–2463 mid-flight, so this block starts at
2466, leaving 2464/2465 free for that writer; the r1
block's unused 242x/243x ids are not reused, to keep amendment ordering monotone). The
committed r1 rows stay (append-only register); the map:

| id | tag | one-line | relation to r1 rows |
|---|---|---|---|
| ASM-2466 | STIPULATED | pilot worklist = singleton synsets, mechanical + item/kernel-blind; within-frame clustering is explicator-owned AUTHORED future work; multi-synset `clusterKey` = sha256(sorted members ‖ frame ‖ clusterVersion) | tightens ASM-2420 |
| ASM-2467 | STIPULATED | OpenAI cache/Batch semantics (cache keys, 30-min TTL, ~15 req/min/key, cached 0.1×, output 6×, Batch 0.5×/50k/200 MB/24 h); κ input-only; **retracts** "warm ≈ 10–20% of cold" → modelled ~51%, ~2× lever; P/S/O measured at micro-pilot | supersedes the economics claim of ASM-2431; amends ASM-2428's provider mechanism |
| ASM-2468 | STIPULATED | the frozen numeric gate: R = 2, $500 cap + kill ladder, $15 micro-pilot, α = 0.70 WLB, κ = 0.70, $c = $0.05, h = 0.60 WLB on n = 200 (≥ 134/200), denominators + provider-failure/abstention rules, verdict a pure function of ledger + review sheet | supersedes ASM-2435's floors-at-prereg clause |
| ASM-2469 | STIPULATED | transactional idempotency: SQLite WAL ledger, atomic unique claim on (conceptId, conceptVersion), write-ahead idempotencyKey = f(versionHash) carried as provider custom_id, CLAIMED→SUBMITTED→COMPLETED/{ACCEPTED,QUARANTINED,PROVIDER_FAILED}+FROZEN, reconciliation sweep by custom_id; ERR_VERSION_DRIFT fails closed; JSONL = passive export | supersedes ASM-2429's mechanics |
| ASM-2470 | STIPULATED | ModelDrafted is a separate immutable bucket (ModelAuthored-tier discipline); only individual human 4-binary endorsement MINTS a new Explicated record; no mutable transition; samples never promote unsampled records | new (closes review items 6–7) |
| ASM-2471 | STIPULATED | catalog-closed drafts (ERR_REF_OUTSIDE_CATALOG) + bounded B = 1,000 shards via encodeConceptSet opts.concepts, vectors dropped post-check; measured anchors (54 rec / 2.22 s / 108 MiB; 3,407 B mean record) + P4 pre-launch benchmark gate; JSONL-shard storage, prefix stored once by hash | new (closes review items 8–9) |
| ASM-2472 | STIPULATED | guardrails mechanized: kot-seat-ledger/1 + pinned invoker with entry 0 = the GPT author seat (ASM-2458 machinery); ERR_STATUS_INELIGIBLE consumer gate; ERR_FROZEN_OVERLAP worklist check; g9 records banned as exemplars (blinded_review_done=0), exemplars require full 4-binary review; reproducibility claim narrowed to attestation + re-runnable acceptance | new (closes review items 14–16); extends ASM-2438 |

Unchanged and still binding from r1: ASM-2424 (scale figures never premises), ASM-2428
(stable hashed prefix; provider mechanism now per ASM-2467), ASM-2434 (EXTRAPOLATION,
volume accept-rate unmeasured; resolution_path = this pilot), ASM-2437 (profile-1 only;
encoder rejection = rejection; formalism changes are encoder version changes), ASM-2438
(author-family ≠ judge-family; now enforced per ASM-2472, not by provenance string alone).

---

## 13. Self-check

- **Design-only / nothing committed?** ✅ No run, no spend, no ingest, no freeze, no git
  commit/push. This file (working tree) + the seven appended register rows are the entire
  output. The session-close push protocol is explicitly overridden by the task ("Design
  only … nothing committed").
- **Review's authorization ruling honored?** ✅ The authorizable surface is the WN-10k
  pilot (§§1–10); 100k/1M+ is a documented FUTURE track (§11) behind named preconditions,
  explicitly not executable under this document.
- **All seven blocking fixes addressed?** ✅ (1) numeric gate + $500 cap + denominators +
  failure rules, §10; (2) singleton worklist + authored-clustering ownership + clusterKey,
  §1; (3) ModelDrafted schema + minting rule + governance reconciliation, §2; (4) OpenAI
  cache-key/TTL/req-rate/Batch semantics + κ definition fixed input-only + P/S/O
  micro-pilot + the 10–20% claim retracted, §§3, 5; (5) transactional ledger + custom_id
  reconciliation + versionHash identity, §6; (6) bounded shards with measured anchors +
  benchmark gate + JSONL-shard storage with measured record sizes, §7; (7) seat-ledger
  enforcement, consumer status gate, frozen-overlap check, g9 exemplar ban, §9.
- **STIPULATED/MEASURED tagged?** ✅ Every load-bearing claim tagged. New MEASURED claims
  are this-tick diagnostics with commands stated (validator timing/RSS; record sizes;
  alignment row count) or committed bytes; provider figures are LIT-BACKED per the
  review's citations **and** preflight-re-verified before any spend; every $/token model
  is STIPULATED with its measurement path; no EXTRAPOLATION is a decision premise.
- **ASMs have real backing_ref, registered?** ✅ Seven rows appended with committed-artifact
  backing_refs (`sense-split-first-construction.md`, `modelauthored-schema.md`,
  `design-bulk-kernel.md`, `plain-v5-register-lint-spec.md` §7/ASM-2458,
  `mechanical-summary.json`, `encoder/src/encoder.ts`, `a-f0-mint-economics-spec.md`,
  issue #44) + the review-cited provider guides for LIT-BACKED figures. Append-only
  discipline respected: committed r1 rows are superseded by reference, never edited.
- **Pseudonyms only?** ✅ "Kern (Fable design agent, designer-1)", "runner-1"; no real
  names beyond the in-repo maintainer handle.
- **Acceptance stays off the drafter?** ✅ Validator loop + human gate own acceptance
  (§4); the model never self-accepts; mechanical rate is an upper bound (§10.5); the
  drafter never decides sense boundaries (§1).
- **Open risks flagged for the maintainer:** (a) volume accept-rate remains the single
  unmeasured unknown (ASM-2434) — the pilot measures it; (b) endorsement throughput at
  100k+ is a real human-hours wall (§11.1 item 3) — a maintainer scoping decision, not a
  design trick; (c) if the micro-pilot measures P/S/O far from the model, the $c ceiling
  keeps the gate honest, but a κ floor re-derivation would be a design amendment, not a
  silent retune.
