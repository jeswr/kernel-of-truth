# GPT-5.6 draft-pipeline — WordNet-10k pilot (build-ready) + million-scale FUTURE track

> **Status:** DESIGN / SPEC ONLY, revision 5. Authorizes nothing to run, spend, ingest, or
> freeze. Maintainer approval + a `kot-reg/*` prereg-freeze are required before any spend.
> Author: Kern (Fable design agent, designer-1), for @jeswr. Date: 2026-07-16.
> **Revision note (r5):** closes the THREE round-4 CONCERNs (2026-07-16); everything the
> round-4 review CONFIRMED is untouched. (1) **Batch idempotency made crash-safe
> end-to-end (§6):** (a) the job discovery token now folds a **(wave, attempt)
> discriminator** into `jobKey` — hashing only the sorted member idempotencyKeys gave a
> repair wave (or a §10.4 retry job) with the same membership as its draft wave the SAME
> token, so reconciliation could adopt the WRONG batch; semantically distinct jobs now
> always carry distinct tokens. (b) The r3/r4 "proven absence" rule (which admitted a
> listing-lag miss and then *financially bounded* the residual duplicate — budget safety,
> not idempotency) is replaced by an **exhaustive-pagination completeness rule**: the
> restart sweeper must page `batches.list()` via `after`/`has_more` to verified coverage
> of the whole window back to the oldest unsettled outbox row before concluding a job
> absent; any failed call or unexhausted cursor ⇒ `ERR_RECONCILE_UNVERIFIED`, no
> resubmit. P5 gains the unexhausted-cursor and same-membership jobKey-distinctness test
> cases. (c) The §13 self-check wording is corrected to **jobKey/metadata
> reconciliation** (`custom_id` is correlation-only, as §6 already ruled). (2)
> **Economics wording (§5.2):** with the online route eliminated, $/accepted is a SINGLE
> figure — **Batch+cache ≈ $0.054** ($380 / 7,000 accepted at α = 0.70); the r4
> "$0.054–$0.106" range is retired (its $0.106 end was the ELIMINATED ~$745 warm-online
> route). $0.054 still exceeds the frozen $c = $0.05, so the P7 maintainer cap/$c gate
> stands unchanged. (3) **Provenance (§8):** the record block regains a `requestId`
> field, recorded from the Batch output line's `response.request_id` (per-call ids ride
> `usage[]`), so the §8 attestation claim ("traceable to a provider request id") is
> satisfiable again. **r5 creates, edits, and renumbers ZERO register rows** — the spec's
> rows stay locked at ASM-2473 … ASM-2478; the r5 idempotency tightenings ride the §12.2
> row A `ASM-2492`/`ASM-2493` request text.
> **Revision note (r4):** closes the TWO residual NEEDS-WORK items of the round-3
> build-readiness review (2026-07-16): (1) **the pilot is now Batch-ONLY** — the online
> (Responses-API) drafting leg is eliminated entirely (§6.0), because its crash-recovery
> discovery was unimplementable as written: the Responses API retrieves a stored response
> only by an **already-known response id**; there is **no response list/search endpoint**,
> so after provider acceptance but before the client records the id, no metadata-keyed
> online discovery can exist. Batch keeps a real, verified crash-safe primitive
> (`batches.list()` over the submit window, §6), and the §5.2 economics had already
> eliminated online anyway — Batch+cache (≈ $380) is the ONLY route under the $500 cap
> (warm-online ≈ $745, Batch-no-cache ≈ $705 both exceed it). §§0, 3, 5, 6, 8, 10, 13
> updated; κ is now computed over Batch usage; P5 is Batch-leg only; the P7 maintainer
> cap/$c re-confirmation STANDS (Batch+cache $/accepted ≈ $0.054 sits above the
> frozen $c = $0.05 — *r5 correction: r4 wrote "$0.054–$0.106" here; the $0.106 end was
> the eliminated warm-online route's $745/7,000 and never a Batch+cache figure — §5.2*). (2) the §12 map row for ASM-2474 now cites the register's single
> valid enum tag (**STIPULATED**); the measured frame-count/hash component is split out
> as a separate new-assumption request (§12.2) — no ASM ids created or renumbered by this
> pass; new rows are `ASM-2492`/`ASM-2493` requests only (§12.2).
> **Revision note (r3):** closes the build-readiness RE-review
> (`docs/next/analysis/largekern-10k-pilot-rereview-20260716.md`, NEEDS-WORK, 2026-07-16):
> (i) spend ≤ $500 via ATOMIC pre-submit worst-case reservation + full-10k terminal
> accounting as a PROCEED precondition (§10.2/§10.3); (ii) the WordNet sampling frame
> pinned by an explicit filter predicate + content hash (§1); (iii) economics re-derived
> at current GPT-5.6 Sol pricing $5/$0.50/$30 per Mtok with the 1.25× cache-write charge —
> the re-derived envelope EXCEEDS the $500 cap on non-cached routes and the maintainer
> must re-confirm the cap and $c ceiling before prereg-freeze (§5.2); (iv) job-level
> transactional outbox + verified provider-side discovery for idempotency (§6);
> (v) shard-throughput and record-size claims downgraded to MODELED with blocking
> benchmark preconditions P4a/P4b (§7); (vi) family-disjointness machinery build +
> fail-path tests as precondition P8, and `authorFamily` canonicalized to `"openai"`
> (§§8–9). Review item 3 (draft-vs-endorsed states) was CONFIRMED and §2 is unchanged.
> Register rows ASM-2473 … ASM-2478 appended (§12).
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
**r3 register state:** the r2 rows ASM-2466 … ASM-2472 are now **committed** (append-only:
r3 never edits them); r3 **appends amending rows ASM-2473 … ASM-2478** (working tree),
each superseding-by-reference the specific r2 claim it tightens — §12 carries the map.
In particular the ASM-2467 modelled arithmetic (old $2/$0.20/$12 prices, the $0.74
repopulation figure, the "$150–$290" spend band) is superseded by ASM-2475.

---

## 0. The one-paragraph answer (r2)

GPT-5.6-Sol becomes the **draft author** inside the *already-designed* kernel-v1
sense-split-first construction — it does not become a new pipeline and it never decides
sense boundaries. **Pilot scope, frozen here:** 10,000 **singleton WordNet-3.1 synset**
candidates (one synset = one candidate; no clustering decision exists anywhere in the
pilot path — §1), drafted through an OpenAI **Batch-ONLY** (no online/Responses drafting
leg — §6.0), prompt-cached, **transactionally idempotent** pipeline (§§3–6), accepted only
by the unchanged deterministic stack
(`validateExplication` → catalog-closed encode-sanity → lint/leakage gates → quarantine on
repair exhaustion). Every accepted draft lands as an **immutable `ModelDrafted` record in
its own bucket** — exactly the committed `ModelAuthored`-tier discipline — and only an
**individual human 4-binary endorsement mints a new `Explicated` record**; there is no
mutable status transition and a sampled review never promotes unsampled records (§2).
The pilot's go/no-go is **fully numeric and frozen in this document** (§10): repair limit
R = 2; hard API cap **$500** enforced by atomic pre-submit worst-case reservation (spend
≤ $500 by construction, §10.2) with a full-10k terminal-accounting PROCEED precondition
(§10.3); accept-rate floor **α = 0.70** (Wilson 95%
lower bound), cache-read floor **κ = 0.70** (input-token fraction, Batch usage sums), cost
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
- **Sampling frame: pinned filter predicate + content hash (reproducible population).**
  The pinned WN31 shards (`data/lexical-wn31/`, source `sha256:3f7d8be8…`) contain
  **117,791** synset records [MEASURED: `data/lexical-wn31/manifest.json`
  `totals.synsets`]. The pilot frame is NOT the whole manifest: **frame = every record
  whose `axioms` array contains no `instanceHypernym` relation** — i.e. named-individual
  / instance synsets are excluded, the identical predicate already frozen in
  `poc/scale/f1k-eligibility/screen_candidates.py` (`load_instance_urns`, SOP-1) and
  prescribed by `f1k-large-kernel-rebuild.md` §2.1 step 2. Applying it this tick:
  117,791 − 7,742 instance synsets = **110,049** type-level synsets [MEASURED,
  2026-07-16, this box]. The frame is hashed for reproducibility:
  `frameSha256 = sha256(UTF-8("\n"-join(lexicographically sorted frame synset URNs)))
  = 777c000ce60d1a83e11e6dd59c8e61f332e8c9ca16e003530b91dae0fac033f3` [MEASURED,
  2026-07-16]. The worklist builder recomputes the frame from the pinned shards, checks
  count == 110,049 AND hash == the pinned `frameSha256`, and **fails closed
  (`ERR_FRAME_HASH`) on any mismatch**; both values ride the pilot manifest. Malformed /
  no-lemma / no-usable-trigger exclusions (f1k §2.1's further steps) are **not** applied
  to the pilot frame — the pilot drafts from the full type-level frame so trigger
  screening never biases the sample. Tag discipline (r4): the **builder contract** —
  predicate choice, fail-closed recompute-and-match rule, no-trigger-screening ruling —
  is the STIPULATED claim of ASM-2474; the **frame count 110,049 and
  `frameSha256 = 777c000c…c033f3` themselves are a MEASURED claim** (2026-07-16, this
  box, from the pinned shards) carried as a separate register row:
  `ASM-2493`. `[STIPULATED ASM-2474
  (builder contract only); supersedes the r2 manifest-attribution error flagged by the
  2026-07-16 re-review item 2]`
- **The worklist builder is mechanical and item/kernel-blind by construction.** Inputs are
  exactly: the pinned WN31 shards filtered to the hashed frame above and the
  frozen-overlap denylist (§9.3). It reads **no
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
  not per-block markers. Cached input reads are priced at **0.1× normal input**;
  **first-token cache population (a cache WRITE) bills at 1.25× uncached input** — every
  partition's initial population and every post-TTL re-population pays this surcharge;
  output is **6× uncached input**. Current TTL guidance: **~30-minute minimum**; a
  partition idle longer than the TTL re-populates (and re-pays the 1.25× write) on next
  request. [LIT-BACKED: GPT-5.6 Sol pricing page
  (developers.openai.com/api/docs/models/gpt-5.6-sol) + prompt-caching guide
  (developers.openai.com/api/docs/guides/prompt-caching), per the 2026-07-16 re-review]
- **~15 requests/minute per cache key; each partition is its own cache population** —
  shards do NOT automatically share one warm prefix. [LIT-BACKED, provider guide as
  above.] **r4: provider background only — the pilot sends NO online drafting or repair
  calls (§6.0), so the online worker-partitioning design (r3's W = 4 workers ×
  `prompt_cache_key = sha256(cachePrefixHash ‖ w)`) is DELETED, not deferred.** A modelled
  prefix-(re)population allowance of ≈ **$2.24** per pilot (≈ 4 partitions × ~10 TTL
  windows × (8,000 prefix tokens × $6.25/Mtok write + 1,200 suffix tokens × $5.00/Mtok))
  is retained in the §5.2 envelope as a conservative bound on whatever population the
  Batch path incurs — how Batch requests map onto cache partitions is UNMEASURED and is
  exactly the m3 endpoint [STIPULATED arithmetic on the §5 price table; supersedes r2's
  $0.74, which used stale prices and omitted the write premium].
- **Batch API.** 50% price on input and output; limits **50k requests / 200 MB input file
  per job / 24 h completion window**; cached tokens still count against rate limits;
  per-tier token queues apply. Concrete pilot consequence: every Batch request embeds the
  full prefix **bytes** in the input file (no cross-request dedup in the file), so at
  P ≈ 8k tokens ≈ 32 kB the 200 MB file limit binds first: 10k drafts ship as **≥ 3 jobs
  of ≤ 4,000 requests (~160 MB each)**, serialized against the account's measured batch
  queue. `custom_id` carries the per-request ledger correlation key **within one job's
  input file only** — it is NOT a cross-submission deduplication key (Batch guide);
  job-level idempotency is the §6 outbox + `metadata` token. Expired-incomplete requests
  bill nothing and are retried per §10.4.
- **Whether Batch requests are served cache reads is UNMEASURED** and is a named
  micro-pilot endpoint (m3, §5.3). **r4: there is no routing decision left to make** —
  Batch is the ONLY drafting transport (§6.0); ASM-2467's "routing decided at the
  micro-pilot" clause is superseded (§12.2). A negative m3 (Batch serves no cache reads)
  does NOT fall back to online: it means the Batch-no-cache completion envelope (≈ $705,
  §5.2) exceeds the $500 cap, and the main run may not launch without a reviewed
  maintainer amendment (P7) — else the pilot is an economics NO-GO **before** main-run
  spend. `[STIPULATED; supersedes the routing clause of ASM-2467 — see §12.2
  ASM-2492 (row A)]`
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
> below, warm-online cost ≈ **53% of cold-online** (price-scale-invariant: the r3
> reprice multiplies every leg uniformly ×2.5) — caching is a **~2× lever**, Batch is
> another **~2× lever**, and they may or may not compose (micro-pilot m3). Caching is
> *material*, not *feasibility-defining*, at pilot scale. `[STIPULATED ASM-2467]`

**Cache-fraction definition (fixed, one definition everywhere):**
`κ = cache-read input tokens / total input tokens` — **input tokens only; output never
appears in the denominator.** Structural ceiling for a draft call: `P/(P+S)`; for the run
mix including repairs: `r·P / (r·P + S_draft + (r−1)·S_repair)`.

### 5.2 Modelled distribution → measured at the micro-pilot

All token counts **[STIPULATED placeholders]** until the micro-pilot measures them from
real `usage` fields; the price table is the **current official GPT-5.6 Sol price list**
[LIT-BACKED: developers.openai.com/api/docs/models/gpt-5.6-sol +
/api/docs/guides/prompt-caching, per the 2026-07-16 re-review; re-verified at P6
preflight], with the LIT-BACKED ratios (cached read = 0.1× input; cache WRITE = 1.25×
input; output = 6× input; Batch = 0.5×):

| symbol | meaning | modelled | measured by |
|---|---|---|---|
| P | cached prefix tokens | 8,000 | micro-pilot m1 |
| S_draft | draft suffix | 1,200 | m1 |
| S_repair | repair suffix (draft + ERR list) | 2,700 | m1 |
| O | output tokens / call (incl. any reasoning tokens billed as output) | 900 | m1 |
| r | calls/concept at R = 2 | 1.8 [MEASURED at A-F0 for the Haiku definer; EXTRAPOLATION here] | m4 |
| price | input $5.00 / cached read $0.50 / **cache write $6.25 (1.25×)** / output $30.00 per Mtok; Batch ×0.5 | current official list | preflight re-verification (ASM-0601 discipline) |

Arithmetic (shown so the conclusion is checkable; per concept; supersedes the r2 numbers,
which used the stale $2/$0.20/$12 list and no write charge). **r4: the online rows below
are REFERENCE ARITHMETIC ONLY** — Batch prices are defined as 0.5× the online legs, so
they must be shown for the derivation to be checkable — **they are NOT pilot routes**;
the pilot's only transport is Batch (§6.0):

- **Cold online (REFERENCE, not a pilot route):** 1.8 × ((8,000+~1,900avg)×$5 +
  900×$30)/10⁶ ≈ **$0.138**; if every call also pays the 1.25× prefix write (population
  never amortizes), 1.8 × ((8,000×$6.25 + ~1,900×$5) + 900×$30)/10⁶ ≈ **$0.156** — the
  true no-cache worst case.
- **Warm online (REFERENCE, not a pilot route):** draft (8,000×$0.50 + 1,200×$5 +
  900×$30)/10⁶ = $0.0370 + 0.8 repair × $0.0445 ≈ **$0.073** → 53% of cold.
- **Batch, no cache:** 0.5 × $0.138 ≈ **$0.069** — the pilot's modelled worst case if m3
  is negative.
- **Batch + cache (if they compose — m3):** 0.5 × $0.073 ≈ **$0.036** — **the single
  costed pilot route.**

→ modelled pilot API spend for 10k on **the single authorized transport, Batch** (incl.
the $15 micro-pilot + the §3 ~$2.24 population allowance): **Batch+cache ≈ $380** — the
only figure under the $500 cap, with ~1.3× headroom, contingent on a positive m3;
**Batch-no-cache ≈ $705** — over the cap; the run would abort safely at the kill ladder.
Reference (eliminated) routes: warm-online ≈ **$745**; cold ≈ $1,395–$1,575 — both over
the cap, which is reason (b) of the §6.0 Batch-only ruling. Modelled $/accepted at
α = 0.70 is a SINGLE figure (r5) — with the online route eliminated there is exactly
one costed transport, so a range is no longer honest: **Batch+cache ≈ $0.054**
($380 / 7,000 accepted). (The r4 "$0.054–$0.106" range is retired: its $0.106 end was
$745/7,000 on the ELIMINATED warm-online reference route and was never a Batch+cache
figure.) $0.054 is still **ABOVE the frozen $c = $0.05 ceiling** (r2's claimed
1.2–2.4× headroom stays retracted), so the P7 maintainer re-confirmation gate
**stands unchanged**. Structural cache ceiling at
the modelled mix: 14,400/17,760 ≈ **0.81**, so the κ = 0.70 floor detects gross cache
failure without gating on the model's own placeholder. `[STIPULATED ASM-2475 for the
price/route arithmetic; the r4 single-route framing supersedes ASM-2475's
"route-dependent" clause — §12.2 ASM-2492 (row A)]`

> **⚠ MAINTAINER RE-CONFIRMATION REQUIRED (blocking, part of P7 — unchanged by r4).**
> At current pricing only the **Batch+cache** route (~$380, m3-unverified) completes 10k
> under the **$500 hard cap**, with ~1.3× headroom; Batch-no-cache (~$705) and the
> eliminated online references (~$745 warm / ~$1,575 cold) all exceed it. The cap stays
> **$500** in this revision (spend ≤ $500 is still guaranteed by §10.2 reservation +
> kill ladder — the run aborts safely, it just may not finish the worklist), and the
> single route's modelled **$/accepted ≈ $0.054 ($380 / 7,000 accepted at α = 0.70)
> sits above $c = $0.05** (r5: single figure — the retired $0.106 range-end was the
> eliminated warm-online route, §5.2).
> Before prereg-freeze the maintainer must explicitly either (a) re-confirm $500 +
> $c = $0.05, accepting that a negative m3 (Batch serves no cache reads) means the main
> run may not launch — an economics NO-GO before main spend, or a kill-ladder abort if
> discovered mid-run — or (b) issue a reviewed design amendment raising the cap/ceiling.
> Neither is decided here; the micro-pilot's measured P/S/O and m3 land first and may
> lower the envelope.

**Context, not a premise:** the A-F0 baseline ($0.078/legal record; 1.8 calls/concept
[MEASURED: `a-f0-mint-economics-spec.md`]) is API-equivalent accounting on another model
and transport, and A-F0 itself declares Batch economics and volume-scale yield unmeasured
(§S8; ASM-0607). It is quoted as prior context only; **no gate below references it.**

### 5.3 Micro-pilot P0 (sub-capped $15, inside the $500 cap)

n = 100 worklist concepts (seeded draw; **excluded from the 10k main-gate denominators**;
their spend still counts in $c), **run through Batch — the same and only transport as the
main run (§6.0)**. Endpoints: **m1** measured P/S/O distribution from usage fields;
**m2** per-job/per-wave Batch cache-read fraction (from `usage` cached-token counts) +
prefix-population behaviour across successive jobs (r4: replaces r3's online TTL/partition
endpoint — there is no online leg to calibrate); **m3** Batch-cache calibration (do Batch
requests get cache reads at all, i.e. does the 0.5× compose with the 0.1× read price?) —
**now the launch-blocking economics input**: negative m3 ⇒ Batch-no-cache envelope ≈ $705
> the $500 cap ⇒ no main-run launch without the P7 maintainer amendment (§5.2); **m4**
measured r at R = 2 (repairs ride follow-up Batch waves, §6); **m5** accept-rate first
look (no gate authority at n = 100). Outputs: gen-settings selection from the pinned
candidate set (`max_output_tokens = 2,048` fixed; `reasoning_effort`/verbosity chosen from
the candidate set listed in the prompt manifest, then frozen) and the measured token
distribution — all frozen into the prereg record before the main run. **r4: the r3
"routing decision (Batch/online mix)" output is DELETED — the route is fixed by design
(Batch-only, §6.0), not chosen by the micro-pilot.** `[STIPULATED ASM-2468; the deleted
routing output supersedes the corresponding ASM-2467/ASM-2468 clause — §12.2 row A]`

---

## 6. Transactional idempotency — Batch-ONLY (review item 13 resolved; r4 closes the round-3 residual)

### 6.0 The Batch-only ruling (r4; supersedes every online-leg clause in this document)

**The pilot's ONLY drafting transport is the OpenAI Batch API. There is no online
(Responses-API) drafting or repair leg.** Rationale, in decision order:

- **(a) The online crash-recovery discovery was UNIMPLEMENTABLE as written.** r3's
  sweeper assumed it could "list/retrieve stored online responses" matching
  `metadata.idempotency_key`. The current OpenAI Responses API exposes retrieval **only
  by an already-known response id — there is no response list/search endpoint** (round-3
  review finding, adopted). So in exactly the crash window the sweeper exists for (after
  provider acceptance, before the client records the returned id), the client has no id
  and no way to discover the response: the proposed online discovery **cannot work**.
  No fix short of a provider-side listing primitive closes this; none exists for
  Responses. `[LIT-BACKED: round-3 build-readiness review, 2026-07-16, citing the OpenAI
  Responses API reference; re-verified at P6 preflight per the ASM-0601 discipline]`
- **(b) Online was not an economically viable route anyway.** The §5.2 r3 re-derivation
  already showed Batch+cache (≈ $380) is the ONLY route under the $500 cap — warm-online
  (≈ $745) and Batch-no-cache (≈ $705) both exceed it. Eliminating online forfeits
  nothing the cap had not already forfeited.
- **(c) Batch retains a real, verified crash-safe primitive.** The Batch API **does**
  expose a listing endpoint (`batches.list()`, paginated), so the job-level transactional
  outbox + a verified discovery sweep over the submit window — already specified below —
  is implementable exactly as written. The crash-safe design survives intact on the leg
  that can actually support it.

Consequences threaded through this revision: repairs ride **follow-up Batch waves**
(draft wave + ≤ R = 2 repair waves, each a normal §10.2-reserved Batch job over the
previous wave's repairable failures — latency ≤ 24 h/wave is acceptable at pilot scale);
κ is computed over **Batch usage sums** (§10.3); the online reservation rule, online
worker/cache-key table row, and online crash tests are deleted (§§10.1, 10.2, 10.6 P5);
`custom_id` stays demoted to per-input-file correlation; the job-level outbox +
idempotency token + `ERR_RECONCILE_UNVERIFIED` fail-closed rule stay binding.
`[STIPULATED — Batch-only transport; supersedes the online-leg clauses of ASM-2476,
ASM-2475, ASM-2473, ASM-2468 and ASM-2467 by reference; §12.2
ASM-2492 (row A)]`

### 6.1 The ledger mechanism

r1's JSONL-pre-check ("look up, then call") is not idempotent: two workers can both see a
missing tuple; a crash after provider submit but before ledger append orphans a paid job.
r2 replaced it with a transactional ledger + write-ahead intent, but leaned on Batch
`custom_id` as if it were a cross-submission dedup key — it is a per-input-file
correlation id only (re-review item 5). r3 closes the provider crash window with a
**transactional OUTBOX at both row and job level + a client-generated idempotency token
in provider `metadata` + a VERIFIED provider-side discovery sweep**; r4 restricts the
whole mechanism to the Batch leg (§6.0), where every discovery primitive it needs
actually exists: `[STIPULATED ASM-2476, tightening ASM-2469; online clauses superseded
per §6.0]`

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
  `CLAIMED → SUBMITTED(batchId) → COMPLETED(outcome)` with outcomes
  `ACCEPTED | QUARANTINED(code) [terminal content rejection] |
  PROVIDER_FAILED [retryable, §10.4]`; plus `FROZEN` (irreversible; §9.3).
  Terminal content rejection and retryable provider failure are **distinct states** —
  a quarantine is never retried, a provider failure never quarantines content.
- **Protocol per candidate (row-level outbox):**
  1. `BEGIN IMMEDIATE; INSERT (conceptId, conceptVersion, state=CLAIMED, owner, ts,
     idempotencyKey); COMMIT` — the UNIQUE primary key makes the claim **atomic**; a
     second worker's insert fails and it moves on. `idempotencyKey =
     "kv1d-" + versionHash[:24]`, generated and **durably committed BEFORE any network
     call** — this row is the transactional **outbox** entry for the candidate.
  2. Submit to the provider — **always inside a Batch job (§6.0; there is no per-call
     online submission path)** — carrying the idempotencyKey as the request's
     `custom_id = idempotencyKey` (correlation **within that job's input file only**;
     `custom_id` is NOT a cross-submission dedup key — Batch guide). Cross-submission
     dedup lives entirely at the job level: the job outbox row + the job's
     `metadata.idempotency_key = jobKey` (next bullet).
  3. Transition to `SUBMITTED` with the returned batch id; on the job's output, verify +
     record `responseSha256`, run acceptance locally, transition to `COMPLETED`. A
     repairable failure re-enters step 2 in the **next repair wave's** Batch job (≤ R = 2
     waves), under the same row identity.
- **Job-level transactional outbox (Batch creation is itself a paid, crash-exposed
  action):** before `batches.create`, a **job outbox row** is committed in the same
  ledger: `{jobKey = "kv1d-job-" + sha256(wave ‖ attempt ‖ sorted member
  idempotencyKeys)[:24], wave, attempt, state=JOB_PENDING, memberCount, worstCaseUSD
  (the §10.2 reservation), inputFileSha256, ts}`, where `wave` is the wave ordinal
  (0 = draft, 1..R = repair waves, §6.0) and `attempt` is the per-wave resubmission
  counter (§10.4 retries of a failed/expired job). **The (wave, attempt) discriminator
  is load-bearing (r5; closes the round-4 jobKey-collision CONCERN):** membership alone
  does not identify a job — a repair wave, or a §10.4 retry, can have *exactly the same
  member set* as an earlier job (the r3/r4 `jobKey` hashed only the sorted member
  idempotencyKeys, which are unchanged across waves), so two semantically different
  jobs would have carried the SAME discovery token and the reconciliation sweep could
  have adopted the WRONG batch's output. Folding `(wave, attempt)` into the hash
  guarantees every semantically distinct job carries a distinct `jobKey`; the sweeper
  matches a token to exactly one intended submission.
  `[STIPULATED — r5 tightening of the ASM-2476 mechanism; carried in the §12.2 row A
  request]` The Batch job is created with `metadata.idempotency_key = jobKey`; on acceptance
  the row moves `JOB_PENDING → JOB_SUBMITTED(batchId)` and, at settlement,
  `→ JOB_SETTLED` (reservation remainder released, §10.2). **Every paid provider
  submission in the pilot is inside such a job (§6.0)** — there is no submission path
  that bypasses the job outbox.
- **Crash windows closed by VERIFIED provider-side discovery, not hope:** on startup
  (and periodically) a sweeper re-examines every `CLAIMED`/`SUBMITTED`/`JOB_PENDING`/
  `JOB_SUBMITTED` row older than a timeout and reconciles against the provider by
  **listing recent Batch jobs** (`batches.list()`, paginated to cover the full window
  back to the oldest unsettled outbox row) and matching
  `metadata.idempotency_key = jobKey`. **This is the ONLY discovery primitive the design
  needs, and it verifiably EXISTS** — r4 deleted the r3 clause that also claimed to
  "list/retrieve stored online responses by metadata": the Responses API retrieves only
  by an already-known response id and has no list/search endpoint, which is precisely why
  the online leg was eliminated (§6.0(a)). Found → adopt the result (no double spend).
  **Completeness rule (r5; replaces r3/r4's "proven absence", which named no verifiable
  criterion and then financially bounded the residual — budget safety is NOT
  idempotency):** the sweeper may conclude a token ABSENT only after **exhaustive
  pagination** of `batches.list()` — following the `after` cursor while
  `has_more = true`, every page call succeeding, until EITHER the provider returns
  `has_more = false` OR the page sequence has verifiably passed the far edge of the
  window (the page's oldest `created_at` predates the oldest unsettled job-outbox
  row's commit `ts`). Both terminations constitute complete coverage of the window;
  **anything less — a failed or timed-out list call, an unexhausted `has_more` cursor,
  a pagination that never reached the window's far edge — is an INCOMPLETE listing and
  fails closed: no resubmission** (`ERR_RECONCILE_UNVERIFIED`), because an unverified
  absence is exactly the duplicate-submission window the 2026-07-16 re-review
  identified. Listing lag is handled *inside* the rule, not waved at money: the
  sweeper reconciles only outbox rows older than its timeout (above), and that timeout
  must exceed the provider's observed `batches.list()` visibility lag — the visibility
  behaviour is exercised at P5 (mock) and observed at P6 preflight/micro-pilot, and the
  timeout is pinned in the prereg record; a row younger than the timeout is simply not
  yet eligible for an absence verdict. The provider offers no server-side create-time
  idempotency guarantee, so dedup lives entirely in outbox-before-call + exhaustive
  verified discovery — that rule IS the idempotency guarantee. (The §10.2 pre-submit
  reservation still bounds the worst-case *cost* of any incident, but r5 removes the
  r3/r4 clause that leaned on financial bounding to excuse listing-lag duplicates. Any
  duplicate ever detected at reconciliation is a ledger INCIDENT: one result adopted,
  the duplicate's spend recorded, logged loudly, never silently absorbed.)
  `[STIPULATED — r5 tightening of the ASM-2476 mechanism; carried in the §12.2 row A
  request]`
  **Pilot precondition P5 (r4: Batch leg — the only leg):** crash-recovery tests against
  a mock provider that records every Batch submission it accepts, with kill −9 injected
  (a) after job-outbox commit but before `batches.create`, and (b) after provider
  acceptance of the job but before the returned `batchId` is recorded. Pass = zero
  duplicate paid submissions and zero orphaned rows after sweeper recovery, plus the
  negative cases (r5): `batches.list()` made to fail mid-pagination, AND made to return
  `has_more = true` with the next page unavailable (unexhausted cursor) ⇒ in both, the
  sweeper refuses to resubmit (`ERR_RECONCILE_UNVERIFIED`); plus one collision case
  (r5): a repair-wave (or retry) job with byte-identical membership to its draft wave
  ⇒ the two jobs carry DISTINCT `jobKey`s and reconciliation adopts each wave's own
  batch, never the other's.
- Runs remain checkpointed/`nohup`+`setsid` per harness discipline; the ledger frontier is
  the resume point (ASM-2429's intent, now with sound mechanics).

---

## 7. Validator throughput + storage (review items 8–9 resolved)

### 7.1 Bounded-shard validation (design sound; throughput MODELED until P4a measures it)

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
- **Anchor (this box, this tick) — NOT a shard benchmark:** full kernel-v0
  validate+encode (54 records, D = 8192, ref depth ≤ 3, including node startup) =
  **2.22 s wall, 108 MiB peak RSS** [MEASURED: `/usr/bin/time -v node data/validate.mjs`,
  2026-07-16]. The derived "≥ ~24 records/s ⇒ 10k ≤ 7 min, RSS flat" figures are
  **[MODELED]** — an extrapolation from a 54-record *whole-kernel* run of small curated
  records to a 1,000-record *shard* path that has never executed; they are planning
  numbers only and **no launch or PROCEED decision may cite them** (2026-07-16 re-review
  item 6). The measured replacement is P4a.
- **Pilot precondition P4a (instrument gate, blocks launch AND PROCEED):** parameterize
  `validate.mjs` (`--kernel/--shard`, already an f1k-rebuild deliverable) and **benchmark
  one representative B = 1,000-record validator shard** on this box — synthetic drafts
  shaped to the §7.2 drafted-record size model, catalog injected via `opts.concepts`,
  vectors dropped post-check — recording records/s and peak RSS into the pilot manifest.
  Launch requires the measured full-10k validation projection ≤ 1 h and peak RSS ≤ 1 GiB —
  generous bounds that exist so the numbers are *measured*, not assumed. §10.3's PROCEED
  additionally requires the P4a artifact to be on file (a verdict computed without it is
  INVALID). `[MEASURED anchor + STIPULATED plan: ASM-2477, tightening ASM-2471]`

### 7.2 Storage format (one format, measured sizes)

- **Drafts: JSONL shards, never per-concept files.** `data/kernel-v1-draft/records/
  shard-NNNN.jsonl.gz`, ≤ 5,000 records/shard, sha256-per-shard manifest; a shard is
  complete only when its validation checks are green (fail-closed). The r1 diagram's
  one-JSON-file-per-concept applies **only** to endorsed `Explicated` records in
  `data/kernel-v1/concepts/` — a human-paced, small population (matches the existing
  54-file kernel-v0 layout).
- **Record sizes: MODELED, not measured on draft records.** The only measured anchor is
  kernel-v0 concept records, n = 54: mean **3,407 B**, median 3,408, p90 5,078, max 7,316
  [MEASURED: `data/kernel-v0/concepts/*.json`, 2026-07-16] — small, curated, **not**
  `kernel-v1-draft/1` records. Everything derived from it is **[MODELED]**: the §8
  provenance increment (+~1.2 kB), the **~5 kB/record** plan (10k ≈ 50 MB records), and
  the transcript figure (prefix stored once by `cachePrefixHash` reference — never per
  record; per-call suffix+output ≈ 2.1k tokens ≈ ~8 kB text × r = 1.8 ⇒ ~15 kB/concept ⇒
  10k ≈ **150 MB** raw, gzipped shards ~⅓). Ledger: one row/candidate + events, ≪ 50 MB.
- **Pilot precondition P4b (instrument gate, blocks main-run launch AND PROCEED):**
  measure the record-size distribution on **real `kernel-v1-draft/1` records** — the
  micro-pilot's n ≈ 100 accepted drafts, each carrying its actual §8 draft-provenance
  block — plus their actual per-record transcript sizes, recording
  mean/median/p90/max into the pilot manifest before any main-run spend. These measured
  values replace the modeled ~5 kB / ~15 kB figures, size the P4a synthetic shard, and
  become the sizing input for §11's storage decision. §10.3's PROCEED requires the P4b
  artifact on file. `[STIPULATED ASM-2477]`
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
  "authorFamily":     "openai",   // CANONICAL = the pinned family-map resolver output:
                                  // plain-v5-register-lint-spec.md §7 maps ^(gpt-|o[0-9]|codex) → "openai".
                                  // r2 wrote "gpt" here, disagreeing with the resolver (re-review item 7);
                                  // the resolver's vocabulary wins — this field MUST equal
                                  // resolve_family(draftAuthor) and the P8 tests assert it.
  "pipelineOperator": "runner-1 (kb-pipeline-runner)",           // pseudonym, agent role
  "endorser":         null | "<review-id>",                      // set only on the MINTED record

  // request identity + attestation
  "conceptId": "...", "conceptVersion": 1, "versionHash": "sha256:…",
  "idempotencyKey": "kv1d-…", "batchId": "…", "customId": "…",
  "requestId": "…",   // r5 (closes the round-4 provenance regression): the provider
                      // request id of the ACCEPTING call, recorded from the Batch
                      // output line's `response.request_id` — Batch output DOES carry
                      // one per request, so the attestation claim below ("traceable
                      // to a provider request id") is satisfiable; r4's "no requestId
                      // field exists" comment conflated route elimination with field
                      // elimination. Per-call ids for EVERY call (draft + repairs)
                      // ride the usage[] entries. Batch-only (§6.0): the id comes
                      // from the job's OUTPUT file for a succeeded request (an
                      // accepted/minted record is always drawn from an output line);
                      // a failed/expired request carries no response.request_id and
                      // is reported on the job's SEPARATE error file (error_file_id,
                      // §10.4) — never an online response.
  "promptHash": "sha256:…", "cachePrefixHash": "sha256:…",
  "genSettings": {"max_output_tokens": 2048, "reasoning_effort": "<pinned>", "...": "..."},
  "sourceRowSha256": "…",                       // the WN worklist row
  "responseSha256": "…",                        // raw provider response bytes
  "transcriptRef": "shard-NNNN#offset",         // suffix+output transcript location
  "usage": [ /* per call: requestId (response.request_id), batchId, input/cached/output tokens, costUSD */ ],
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
provider request id (the recorded `requestId` / per-call `response.request_id` values
in the block above, taken from the Batch output lines — r5); and (b) **re-runnable
acceptance** — `validateExplication` and the
lints are pure, so the mechanical accept/reject of the *stored* draft is re-derivable
byte-identically. r1's "re-derivable: same prompt + same snapshot → attestable draft" is
narrowed to exactly that. `[STIPULATED: correction; carried in ASM-2472's enforcement row]`

---

## 9. Mechanized guardrails (review items 15–16 resolved)

Prose rules become checked invariants: `[STIPULATED ASM-2472]`

1. **Family disjointness = the DESIGNED fail-closed seat machinery — which must be BUILT
   first (precondition P8).** The drafting store writes a `kot-seat-ledger/1` ledger with
   **entry 0 = the author seat** (exact dated `gpt-5.6-sol` id). Every LLM invocation in
   any downstream seat role over these records goes through the pinned invoker
   (`invoke_seat.py`), which resolves families via the pinned family map and refuses
   **before dispatch** on same-family or UNKNOWN (FD-1/FD-2), with orphan and
   hash-chain-integrity sweeps (FD-5/FD-6) — the ASM-2458 mechanism, pointed at this
   store (`plain-v5-register-lint-spec.md` §7). **Honesty correction (re-review item 7):
   r2 called this machinery "existing"; it is existing DESIGN, not existing code —
   `poc/plainv5/invoke_seat.py`, `poc/plainv5/check_family_disjoint.py`, and
   `poc/plainv5/family-map.json` are absent from the workspace this tick [MEASURED:
   2026-07-16].** **Pilot precondition P8 (blocks prereg-freeze):** build the invoker,
   validator, and family map exactly per the pinned plain-v5 §7 design (or pin whatever
   implementation of that design has landed by then), pointed at
   `data/kernel-v1-draft/`, with **fail-path tests green** for FD-1 (same family
   refused), FD-2 (UNKNOWN refused), FD-5 (orphan invocation detected), FD-6 (broken
   hash chain detected), `ERR_STATUS_INELIGIBLE` (§9.2), and an
   `authorFamily == resolve_family(draftAuthor) == "openai"` provenance-agreement
   assertion (§8). `authorFamily` remains record metadata; the **resolver + ledger are
   the enforcement**, never a string compare. Consumer prereg lint runs the disjointness
   validator against entry 0.
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
| Sampling frame | the 110,049 non-instance WN31 synsets (no-`instanceHypernym` filter), `frameSha256 = 777c000c…c033f3` (§1), checked fail-closed at worklist build |
| Worklist | 10,000 singleton WN31 synsets, seeded stratified draw (§1), single-draw |
| Repair limit **R** | **2** (≤ 3 model calls/concept); abstention = terminal, no repair |
| `max_output_tokens` | **2,048** per call |
| Gen settings | pinned candidate set in the prompt manifest; selected once at micro-pilot; frozen at prereg |
| Transport | **Batch API ONLY** (§6.0) — no online/Responses drafting or repair calls exist in the pilot |
| Batch jobs | ≤ 4,000 requests/job (200 MB bound), serialized; draft wave + ≤ 2 repair waves (§6.0) |
| Micro-pilot | n = 100, sub-cap **$15.00**, endpoints m1–m5 (§5.3), excluded from main denominators |
| Human sample | n = **200**, seeded stratified (POS × polysemy band), blind 4-binary |

### 10.2 Frozen budget + kill ladder (spend ≤ the cap, by ATOMIC PRE-SUBMIT RESERVATION)

- **Hard pilot API cap: $500.00**, enforced by **atomic pre-submit worst-case
  reservation**, not by after-the-fact cost recording (the re-review item 1 correction:
  recording actual cost after a call cannot bound concurrent or Batch liability).
  Mechanism, in the §6 ledger (SQLite, `BEGIN IMMEDIATE` — one writer at a time):
  1. **Before ANY Batch submission** (the only paid provider action in the pilot —
     §6.0), a single transaction checks
     `spentUSD + reservedUSD + newReservation ≤ $500.00` and debits `newReservation`
     from the remaining budget; if the check fails, the submission **does not happen**
     (`ERR_BUDGET_RESERVE`). No provider submission is ever made without a committed
     reservation covering its worst case — unreserved liability cannot exist. (r4
     deletes r3's per-call online reservation rule ≈ $0.125/call: no online calls
     exist. The per-request worst-case figure it derived survives only as the ×0.5
     Batch per-request bound below.)
  2. **Batch job reservation** = the WHOLE job's worst case at submit, Σ over its
     requests at Batch 0.5× ≈ $0.0625 × requests — up to **≈ $250 for a full
     4,000-request job** — debited atomically BEFORE `batches.create` (written on the §6
     job-outbox row as `worstCaseUSD`) and held for the job's lifetime. Repair waves are
     jobs like any other and reserve identically. Consequence: a full-size job and much
     else cannot be in flight against a $500 cap simultaneously; jobs serialize against
     the remaining budget **by construction**, not by policy.
  3. **On completion/settlement**, actual cost from the provider `usage` fields is
     written to `spentUSD` and the **unused remainder of the reservation is released**
     in the same transaction. Expired/failed requests settle at their billed (possibly
     $0) cost; the reservation never leaks.
  Includes micro-pilot, calibration, repairs, and all failed attempts.
- **Kill ladder:** checkpoint at **$50** (require: ≥ 500 concepts attempted, κ diagnostic
  ≥ 0.50, running accept-rate ≥ 0.40 — else abort INVALID-INSTRUMENT); checkpoint at
  **$250** (require ≥ 45% of worklist attempted — else abort INVALID-INSTRUMENT);
  hard-abort at $500. (At current §5.2 pricing, a no-cache Batch outcome — negative m3 —
  is modelled to trip these checkpoints before completing the worklist; but the m3
  micro-pilot endpoint is designed to surface that BEFORE main-run launch — see the §5.2
  maintainer flag and §5.3.)
- **Reproducible worst case:** worst-case API spend **≤ $500.00** — an upper bound
  guaranteed by the reservation invariant above (the r2 claim "≡ $500.00 exactly" was
  wrong twice over: a sound cap is an inequality, and post-hoc recording could not even
  enforce that); plus human review **40–75 h** (planning band, §4.3) and this box's CPU
  (validation bound measured at P4a, §7.1). The cap is NOT a completion claim: on the
  single authorized transport (§6.0), modelled completion is Batch+cache ≈ $380 (under
  the cap) vs Batch-no-cache ≈ $705 (§5.2); in the no-cache case the run aborts at the
  cap/kill ladder without finishing — safely, with all spend reserved-then-settled.
  `[STIPULATED ASM-2473; its online-call reservation clause and "route-dependent
  $380–$745" wording are superseded by the §6.0 Batch-only ruling — §12.2 row A]`

### 10.3 Frozen endpoints, denominators, decision rule

**Denominators (fixed):**
- `attempted` = worklist items with ≥ 1 completed (billed) model response. Items whose
  every call ended in provider/transport failure are **PROVIDER_FAILED items**, excluded
  from `attempted` and reported separately.
- `accepted` = mechanically accepted within ≤ 3 calls (§4.1).
- Abstentions, malformed outputs (JSON parse failure counts as an attempt and enters
  repair once with the parse error), and repair-exhausted quarantines are **failures
  inside the denominator**.

**Terminal-accounting invariant (PROCEED precondition #0, re-review item 1):** every one
of the 10,000 worklist rows must be in a **terminal** ledger state, and the counts must
close exactly:

> `accepted + quarantined + provider_failed = 10,000`

recomputed from the committed ledger export (micro-pilot rows excluded per §5.3; the
worklist builder guarantees no `FROZEN` row enters the 10k). Any row left `CLAIMED` /
`SUBMITTED` / `JOB_*`, or any count mismatch, means the run is **unfinished or the ledger
is corrupt**: no PROCEED may be issued — the run either resumes to terminality under the
remaining budget or is closed INVALID-RERUN. The four endpoints below are necessary but
NOT sufficient; this invariant (plus the P4a/P4b measured artifacts, §7) must hold first.
`[STIPULATED ASM-2473]`

**Endpoints and floors — PROCEED iff the invariant above AND all four hold:**

| # | endpoint | rule | frozen threshold |
|---|---|---|---|
| 1 | **accept-rate** = accepted / attempted | Wilson 95% **lower bound** | **α = 0.70** |
| 2 | **cache-read fraction** κ = cache-read input tokens / total input tokens, computed over **all Batch usage sums** (input-only denominator; r4: there is no online leg — §6.0 — so r3's routing-conditional clause is deleted; if m3 measures Batch serving no cache reads, the main run does not launch without the P7 amendment, so a κ = 0 main run cannot occur by surprise) | point estimate from ledger usage sums (deterministic, no sampling) | **κ = 0.70** |
| 3 | **$/accepted-record** = ALL pilot API spend (micro-pilot + calibration + every failed/quarantined/repair call) ÷ accepted | point value from ledger | **$c = $0.05** |
| 4 | **human-pass-rate** on the n = 200 blind sample | Wilson 95% **lower bound** (⟺ observed ≥ **134/200**) | **h = 0.60** |

**Verdicts:** terminal-accounting invariant + all four endpoints hold → **PROCEED**
(authorizes designing the 100k stage's prereg,
not its spend). Any miss → **NO-GO / reassess** (directives §4 fork discipline; never
silent proceed). Instrument failure — PROVIDER_FAILED items > **2%** of the worklist, or
a kill-ladder abort — → **INVALID-RERUN**: no scientific verdict; a re-run requires a
fresh registration and fresh cap. The verdict is a **pure function of the ledger + the
review sheet**; anyone re-computing the four numbers from the committed ledger export and
the endorsement ledger must reach the same verdict.

### 10.4 API-failure and retry policy (frozen)

Provider/transport failures (HTTP 5xx on Batch endpoints, timeouts, Batch expiry,
expired-incomplete requests) are **retryable**: ≤ 3 retries per request — via
exponential-backoff resubmission of the job call, or re-inclusion of the expired/failed
request in a follow-up Batch job (§6.0 waves) — then the item is marked PROVIDER_FAILED
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

P1 worklist builder green on the pinned WN31 shards: frame recomputed and matched
   (count = 110,049 AND `frameSha256` match, else `ERR_FRAME_HASH`) + `ERR_FROZEN_OVERLAP`
   check (§1, §9.3);
P2 exemplar review done, k ≤ 8 passers sha-pinned (§9.4);
P3 micro-pilot complete (run through Batch — the only transport, §6.0), m1–m5 measured,
   gen settings frozen (§5.3; no routing decision exists in r4) — the only precondition
   with spend, inside the $15 sub-cap and only after maintainer approval of this design;
   a negative m3 additionally blocks main-run launch pending the P7 amendment (§5.2);
P4a representative B = 1,000-record validator-shard benchmark measured +
   `--kernel/--shard` refactor landed (§7.1) — also a PROCEED requirement;
P4b record-size + transcript-size distribution measured on real `kernel-v1-draft/1`
   micro-pilot records (§7.2) — also a PROCEED requirement;
P5 crash-recovery tests passed against a recording mock provider on the **Batch leg —
   the only leg (§6.0)**: both crash windows (post-job-outbox/pre-`batches.create`,
   post-acceptance/pre-`batchId`-record), plus the fail-closed incomplete-pagination
   cases (mid-pagination failure; unexhausted `has_more` cursor ⇒
   `ERR_RECONCILE_UNVERIFIED`) and the same-membership `jobKey`-distinctness collision
   case (§6, r5);
P6 preflight: live price table (incl. the 1.25× cache-write rate) + cache/Batch
   semantics re-verified vs §§3, 5.2 (ASM-0601 discipline); API key provisioned by the
   maintainer (none on this box — checked at A-F0, 2026-07-10); account tier + batch
   queue recorded;
P7 maintainer has explicitly re-confirmed (or amended by reviewed revision) the $500 cap
   and $c = $0.05 ceiling against the §5.2 re-derived envelope; then the `kot-reg/*`
   record is frozen carrying §10 verbatim; mock run ($0, including budget-reservation
   accounting) green;
P8 family-disjointness machinery built + fail-path tests green (FD-1/2/5/6,
   `ERR_STATUS_INELIGIBLE`, `authorFamily`/resolver agreement) per §9.1.

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

## 12. Assumptions registered (r2, committed; r3 appended in §12.1; r4 requests in §12.2)

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

### 12.1 Assumptions appended by r3 (ASM-2473 … ASM-2478)

The r2 rows above are now committed; r3 appends six amending rows (working tree —
nothing committed by this pass), closing the 2026-07-16 re-review
(`docs/next/analysis/largekern-10k-pilot-rereview-20260716.md`). **r4 note:** the rows
below are quoted as registered; where a row's one-liner mentions the online leg
(ASM-2473's per-call reservation, ASM-2475's route-dependent framing, ASM-2476's online
`store:true` + stored-response listing), that clause is superseded by the §6.0
Batch-only ruling — see §12.2 row A. **r5 note:** likewise superseded-by-reference via
row A are ASM-2475's "$/accepted $0.054–$0.106" range (single-route figure ≈ $0.054,
§5.2), ASM-2476's membership-only `jobKey` (now sha256(wave ‖ attempt ‖ sorted member
keys), §6) and its "proven absence" discovery wording (now the exhaustive-pagination
completeness rule, §6). The rows themselves are locked and untouched:

| id | tag | one-line | relation |
|---|---|---|---|
| ASM-2473 | STIPULATED | spend ≤ $500 via atomic pre-submit worst-case reservation (online ≈ $0.125/call; whole Batch job ≈ $0.0625/request, ≈ $250/4k-job, reserved at submit, remainder released at settlement; `ERR_BUDGET_RESERVE` fails closed) + terminal-accounting PROCEED precondition `accepted + quarantined + provider_failed = 10,000` | tightens ASM-2468 (retracts "≡ $500 exactly") |
| ASM-2474 | STIPULATED | pilot sampling frame is pinned by predicate + content hash: frame = the pinned WN31 shards filtered by "no `instanceHypernym` axiom" (the frozen screen_candidates.py / f1k §2.1-step-2 predicate); worklist builder recomputes the frame and fails closed (`ERR_FRAME_HASH`) unless count and hash match the pinned manifest values; f1k trigger-screening exclusions deliberately not applied. (r4: this map row now cites the register's single enum tag — the registered row IS `STIPULATED`; the r3 map's "STIPULATED+MEASURED" was a map error, not a register error. The measured count/hash component is split out as §12.2 row B.) | tightens ASM-2466 (fixes the r2 manifest-count attribution) |
| ASM-2475 | STIPULATED | economics re-derived at current GPT-5.6 Sol prices $5/$0.50/$30 per Mtok + 1.25× cache-write ($6.25): warm-online ≈ $0.073/concept, Batch+cache ≈ $0.036, cold ≈ $0.138–$0.156; 10k route-dependent $380–$745; $/accepted $0.054–$0.106 ≥ the $c = $0.05 ceiling; repopulation ≈ $2.24; completion envelope exceeds the $500 cap on non-cached routes → maintainer re-confirmation is precondition P7 | supersedes ASM-2467's arithmetic ($150–$290 band, $0.74 repop, headroom claim) |
| ASM-2476 | STIPULATED | provider idempotency = row- AND job-level transactional outbox committed before any call, client token in `metadata.idempotency_key` (online `store:true`; Batch job metadata; `custom_id` = per-file correlation only), verified discovery on restart (Batch-list / stored-responses listing must provably cover the window, else `ERR_RECONCILE_UNVERIFIED`, no resubmit); P5 widened to both legs × both crash windows + the fail-closed listing case | tightens ASM-2469 |
| ASM-2477 | STIPULATED | shard-throughput ("≥24 rec/s, ≤7 min") and record-size ("~5 kB", "~15 kB transcript") figures are MODELED, not measured; representative measurements are blocking preconditions P4a (B=1,000 validator-shard benchmark) and P4b (size distribution on real kernel-v1-draft/1 micro-pilot records), each also required for PROCEED | tightens ASM-2471 |
| ASM-2478 | STIPULATED | family-disjointness machinery (invoke_seat.py, check_family_disjoint.py, family-map.json) is designed but NOT in the workspace (MEASURED 2026-07-16); building it + fail-path tests (FD-1/2/5/6, ERR_STATUS_INELIGIBLE, provenance/resolver agreement) is precondition P8; canonical `authorFamily` = the resolver's output `"openai"`, never `"gpt"` | tightens ASM-2472 |

### 12.2 New-assumption REQUESTS from r4 (no ids allocated by this pass)

r4 creates **no** register rows and renumbers **nothing** — ASM allocation is
coordinator-owned and this spec's rows are locked at ASM-2473 … ASM-2478. The two r4
changes each need one NEW row; both are described here for the coordinator to register.
**r5 likewise allocates nothing:** its three fixes either tighten the row A claim
(the `jobKey` discriminator and the exhaustive-pagination completeness rule are folded
into row A's claim text below — same marker, still exactly two coordinator requests) or
change no registered claim (the single-figure $/accepted wording and the `requestId`
provenance field correct r4 drafting errors against already-registered claims):

| marker | proposed tag | claim to register | relation |
|---|---|---|---|
| **row A** `ASM-2492` | STIPULATED | **The pilot's ONLY drafting transport is the OpenAI Batch API — the online (Responses) leg is ELIMINATED** (§6.0). Grounds: (a) the r3 online crash-recovery discovery was unimplementable — the Responses API retrieves a stored response only by an already-known id; no response list/search endpoint exists, so the post-acceptance/pre-record crash window cannot be reconciled online; (b) §5.2 economics: Batch+cache (≈ $380) is the only route under the $500 cap (warm-online ≈ $745, Batch-no-cache ≈ $705); (c) Batch keeps a verified discovery primitive (`batches.list()` over the submit window). Consequences: repairs ride ≤ 2 follow-up Batch waves; κ computed over Batch usage sums; P5 is Batch-leg-only; no routing decision at the micro-pilot; a negative m3 blocks main-run launch pending P7. **r5 tightenings (same claim, same marker):** (i) `jobKey = "kv1d-job-" + sha256(wave ‖ attempt ‖ sorted member idempotencyKeys)[:24]` — the (wave, attempt) discriminator guarantees a repair wave or §10.4 retry with identical membership never shares a discovery token with its draft wave (§6); (ii) absence at reconciliation requires EXHAUSTIVE `batches.list()` pagination (`after`/`has_more` to `has_more = false` OR verifiably past the oldest unsettled outbox row, every page call succeeding), else `ERR_RECONCILE_UNVERIFIED` and no resubmit — financial bounding is budget safety, never the idempotency argument (§6); (iii) the single-route $/accepted is ≈ $0.054 ($380/7,000 at α = 0.70), replacing the route-dependent $0.054–$0.106 range (§5.2). | supersedes-by-reference the online-leg clauses of ASM-2476 (online `store:true` + stored-response listing; r5: also its membership-only jobKey + "proven absence" wording), ASM-2475 ("route-dependent" completion framing; r5: also the $0.054–$0.106 range), ASM-2473 (per-call online reservation), ASM-2468 (online-leg κ wording), ASM-2467 (micro-pilot routing decision) |
| **row B** `ASM-2493` | MEASURED | The pinned pilot-frame **values**: applying the ASM-2474 predicate to the pinned WN31 shards yields 117,791 − 7,742 = **110,049** type-level synsets and `frameSha256 = 777c000ce60d1a83e11e6dd59c8e61f332e8c9ca16e003530b91dae0fac033f3` (sha256 over the UTF-8 newline-joined lexicographically sorted frame URN list), measured 2026-07-16 on this box; these are the values the ASM-2474 builder contract checks against fail-closed (`ERR_FRAME_HASH`). | splits the measured component out of ASM-2474, which remains the STIPULATED builder-contract claim (register enum: exactly one tag per row) |

Unchanged and still binding from r1: ASM-2424 (scale figures never premises), ASM-2428
(stable hashed prefix; provider mechanism now per ASM-2467), ASM-2434 (EXTRAPOLATION,
volume accept-rate unmeasured; resolution_path = this pilot), ASM-2437 (profile-1 only;
encoder rejection = rejection; formalism changes are encoder version changes), ASM-2438
(author-family ≠ judge-family; now enforced per ASM-2472, not by provenance string alone).

---

## 13. Self-check

- **Design-only / nothing committed?** ✅ No run, no spend, no ingest, no freeze, no git
  commit/push by this pass. r5's entire output is this file (working tree); **r4 and r5
  create, edit, and renumber ZERO register rows** — the two new assumptions needed are
  the `ASM-2492`/`ASM-2493` requests (§12.2 rows A/B; r5's tightenings ride
  row A's claim text, same marker), and the spec's own rows stay locked at
  ASM-2473 … ASM-2478 exactly as registered. The session-close push protocol is
  explicitly overridden by the task (coordinator owns the commit).
- **r5: all three round-4 CONCERNs closed?** ✅ (1) **idempotency crash-safe end-to-end
  (BUILD-BLOCKING item)** — (a) `jobKey` now folds the (wave, attempt) discriminator
  over the sorted member idempotencyKeys, so a repair wave or §10.4 retry with
  membership identical to its draft wave can never share a discovery token and
  reconciliation can never adopt the wrong batch (§6); (b) "proven absence" replaced by
  the EXHAUSTIVE-pagination completeness rule — `after`/`has_more` paged to
  `has_more = false` or verifiably past the oldest unsettled outbox row, every page
  call green; any incompleteness ⇒ `ERR_RECONCILE_UNVERIFIED`, no resubmit; financial
  bounding demoted to budget-safety context, no longer any part of the idempotency
  argument (§6); P5 gains the mid-pagination-failure, unexhausted-cursor, and
  same-membership jobKey-distinctness cases (§6, §10.6); (c) the item-(5) wording below
  corrected to jobKey/metadata reconciliation. (2) **economics wording** — the stale
  "$0.054–$0.106" range is retired everywhere it was load-bearing; the single
  Batch+cache figure is ≈ $0.054 ($380 / 7,000 accepted at α = 0.70), still above
  $c = $0.05, so the P7 maintainer cap/$c gate stands (§5.2). (3) **provenance** —
  `requestId` (the Batch output line's `response.request_id`) restored to the §8 block,
  with per-call ids in `usage[]`, so the attestation claim ("traceable to a provider
  request id") is satisfiable (§8). Scope unchanged: WordNet-10k singletons; no frozen
  record touched; no ASM ids created or renumbered.
- **r4: both round-3 residuals closed?** ✅ (1) **idempotency implementable** — the pilot
  is Batch-ONLY (§6.0): the unimplementable online metadata-discovery (Responses API has
  no list/search endpoint; retrieval needs an already-known id) is deleted, not patched;
  the surviving crash-safe primitive is the job-level outbox + `metadata.idempotency_key`
  + a VERIFIED `batches.list()` sweep over the submit window, fail-closed on
  `ERR_RECONCILE_UNVERIFIED`; `custom_id` stays per-input-file correlation only; repairs
  ride ≤ 2 follow-up Batch waves; P5 tests the Batch leg at both crash windows plus the
  negative listing case (§6, §10.6). Economics updated to the single costed route:
  Batch+cache ≈ $380 under the $500 cap (warm-online ≈ $745 / Batch-no-cache ≈ $705 both
  exceed it — §6.0(b)); $/accepted ≈ $0.054 ($380/7,000 at α = 0.70 — r5's single-route
  figure; r4's "$0.054–$0.106" range is retired, §5.2) still above $c = $0.05, so **the
  P7 maintainer cap/$c re-confirmation gate stands unchanged** (§5.2). (2) **ASM-2474 tag**
  — the §12.1 map row now cites the register's single four-value-enum tag, `STIPULATED`
  (matching the registered row); the measured 110,049-count/`frameSha256` component is
  split into the §12.2 row-B `ASM-2492`/`ASM-2493` request; ASM-2474 remains
  the builder-contract stipulation (§1, §12.1, §12.2).
- **r3: all six re-review CONCERNs closed?** ✅ (1) budget/terminal accounting — atomic
  pre-submit reservation incl. whole-Batch-job worst case, spend ≤ $500 (not "≡ $500"),
  and `accepted + quarantined + provider_failed = 10,000` as PROCEED precondition #0
  (§10.2, §10.3); (2) population — the no-`instanceHypernym` filter predicate stated,
  117,791 → 110,049 reconciled, frame content-hashed (`777c000c…c033f3`) and checked
  fail-closed (§1, P1); (4) economics — repriced to $5/$0.50/$30 + 1.25× cache-write,
  re-derived per-route ($380–$745 for 10k; r3's route-dependent "$/accepted
  $0.054–$0.106 ≥ $c" has since collapsed to the single Batch+cache ≈ $0.054 via the
  r4/r5 route elimination — §5.2), envelope
  exceeds the cap on non-cached routes and maintainer re-confirmation is P7 (§5.2, §3);
  (5) idempotency — row+job transactional outbox, metadata idempotency token,
  `custom_id` demoted to per-file correlation, verified-listing discovery that fails
  closed, P5 crash-window coverage (§6) — *r3's "both legs" and online-discovery clause
  did not survive the round-3 review; r4 resolves it Batch-only, see the r4 bullet*; (6) validator/storage —
  throughput and size figures downgraded to MODELED; representative B = 1,000 shard
  benchmark (P4a) and real-draft size distribution (P4b) block launch AND PROCEED (§7);
  (7) guardrails — machinery absence disclosed [MEASURED], build + FD-1/2/5/6 +
  `ERR_STATUS_INELIGIBLE` fail-path tests are P8, `authorFamily` canonicalized to the
  resolver's `"openai"` (§8, §9.1). Item 3 was CONFIRMED; §2 untouched. Pilot scope
  unchanged: WordNet-10k singletons; million-scale stays FUTURE (§11); frozen records
  untouched.
- **Review's authorization ruling honored?** ✅ The authorizable surface is the WN-10k
  pilot (§§1–10); 100k/1M+ is a documented FUTURE track (§11) behind named preconditions,
  explicitly not executable under this document.
- **All seven blocking fixes addressed?** ✅ (1) numeric gate + $500 cap + denominators +
  failure rules, §10; (2) singleton worklist + authored-clustering ownership + clusterKey,
  §1; (3) ModelDrafted schema + minting rule + governance reconciliation, §2; (4) OpenAI
  cache-key/TTL/req-rate/Batch semantics + κ definition fixed input-only + P/S/O
  micro-pilot + the 10–20% claim retracted, §§3, 5; (5) transactional ledger +
  **jobKey/`metadata.idempotency_key` reconciliation** (`custom_id` is per-input-file
  correlation ONLY, never a reconciliation key — wording corrected r5 to match §6) +
  versionHash identity, §6; (6) bounded shards with measured anchors +
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
