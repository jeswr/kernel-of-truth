# XCACHE-SHARED — should the expert cache get a shared database across workers?

> **DESIGN + RESEARCH ONLY.** Answers the maintainer's issue-#30 note verbatim:
> *"it may be worth spinning up a single database (perhaps postgres?) that can
> be used as a shared cache across all workers, rather than this being
> something that is used only by a single worker and thus missing cache hits
> across workers. I don't know how useful this actually is nor the cost
> implications so it is something that needs researching."*
> No code applied, no instance launched, no registry write, no git action, no
> model run, $0 spent, and **no feasibility conclusion is stated**. ASM block
> ASM-2313..2326 at §8, mirrored in
> `docs/next/design/asm-shared-cache-2313-2330.json` for coordinator
> registration. Extends `docs/next/design/glm52-expert-cache.md` (XCACHE,
> ASM-2300..2312); companion to `glm52-f1k-cost-reduction.md` ($149 protocol +
> the #30 ~10-worker CPU-spot sharding conclusion) and `glm52-expert-drop.md`
> (#27). Repo state at emission: commit
> `3611025a3580b13cfb69af1d31e3723b9b9d165c`. All AWS prices pulled 2026-07-13
> from the public AWS Price List bulk API for **eu-west-2** (offer-file
> publication dates cited inline).
> **Revised 2026-07-13 (designer-16)** per the second GPT-5.6 xhigh review of
> the consolidated XCACHE design
> (`poc/gpt56-review/expert-cache-r2/out/last-message.json`): record
> integrity in the shared tier is **BLAKE3-128-authoritative** with CRC32
> demoted to a non-authoritative fast-reject/torn-tail hint (§5,
> ASM-2323(b) — r2 blocker 3, byte-consistent with XCACHE §2.4/ASM-2308),
> and §1's residual revision-1 "<1%" first-touch figure is replaced by the
> corrected ~2–7% corner band (r2 finding 6 residue; ASM-2313 parenthetical
> updated, its ≤ ~$1.5 band unchanged).

## 0. BLUF

**The design already has a shared cache across all workers — the S3
content-addressed mirror (XCACHE §5.1). One bucket, all ten workers, keyed by
content, writer-agnostic by construction.** The per-worker NVMe tier is a *hot
tier in front of* that shared store, not the store itself. Under the #30
sharding rule ("all arms of an item on the same worker"), essentially all
reuse is within-worker by construction; the reuse that is genuinely
cross-worker (frozen-template prefix first-touch, item reassignment after a
spot interruption, #27's cross-experiment baseline on a re-provisioned fleet)
is **already captured by the S3 tier**, and what a *synchronous* shared
database would add on top is estimated at **~0.1% (band 0–1%) of expert I/O,
≤ ~$1.5 per campaign** [EXTRAPOLATION, ASM-2313]. Against that benefit, a
shared Postgres costs **~$55/mo (index-only, db.t4g.medium) to ~$227/mo (blob
store, db.m6g.large + 700 GB gp3)** in eu-west-2 [LIT-BACKED, ASM-2318] — and
its ~ms round-trips are unusable on the per-probe critical path anyway (§3).
**Recommendation (§6): keep the tiered design — per-worker NVMe hot tier + the
existing shared S3 content-addressed cold tier — and make the shared role
explicit with a zero-cost existence index (a per-worker Bloom-filter snapshot
of the S3 segment manifests, synced on the existing checkpoint cadence).
DynamoDB is the trigger-gated optional upgrade for the index (~$17–21 per
campaign); Postgres adds nothing over shared-S3 + index and is not
recommended. The $149 F1-K ceiling is unchanged; incremental cost of the
recommended architecture ≈ $0–5/mo on the storage line.**

---

## 1. Q1 — What reuse is actually CROSS-worker?

Setting (from the #30 analysis transcribed in `glm52-f1k-cost-reduction.md`
and the issue thread): F1-K runs on ~10 CPU spot workers, sharded by
item/concept block, **all arms of an item kept on the same worker**. XCACHE as
designed: per-worker NVMe (hot) + one shared S3 bucket (persistent), Tier-C =
shared-prefix checkpoint.

Enumeration of every reuse class, with its locality [STIPULATED, ASM-2314 —
structural consequences of the causal DAG (ASM-2300) plus the sharding rule]:

| # | Reuse class | Volume | Cross-worker? | Captured today by |
|---|---|---|---|---|
| 1 | Cross-ARM within an item (b0 + 6 spliced passes; σ ≈ 55%/41%/1.3% per arm, XCACHE §1.2–1.3) — **the dominant class, ~95%+ of all reuse value** | ~4,700 prefill-equiv (L1) | **No** — sharding pins all 7 arms of an item to one worker | per-worker NVMe |
| 2 | Frozen template PREFIX (Tier-C): the R1.1 header bytes are identical across ALL items → the pre-item-token rows are byte-identical across items and workers | q·T ≈ 30–60 rows/prefill | **Yes**, but only *first-touch per worker*: each worker's own first item populates it locally; without sharing, exactly 9 redundant prefix computations occur fleet-wide | per-worker NVMe after item 1; S3 restore at bring-up |
| 3 | b0 baseline passes of an item, reused by that item's other arms | all items | **No** — same worker as its arms (class 1) | per-worker NVMe |
| 4 | Item reassignment (spot interruption, rebalancing): an item's populated entries needed on a *different* worker | rare; interruption-rate dependent | **Yes** | **S3 mirror** — restore the item's segments before resuming |
| 5 | #27 cross-experiment baseline (the b0-full TOPK=8 arm, byte-equal to F1-K's b0 → ~100% hit under the identical combined binary + retention preconditions of ASM-2309 as revised): #27's item→worker map may differ, and the fleet is likely re-provisioned | up to ~1,440 prefills | **Yes** | **S3 mirror** — that is exactly what the persistent tier is for |
| 6 | Genuine (W-hash, x-hash) collisions across *different* items | ≈ 0 | — | n/a |

On class 6, honestly closed: a pre-moe input row at layer ℓ is the
post-attention residual, a function of the **entire causal prefix** at that
position. Two different items share input rows only at positions where their
token prefixes are byte-identical — i.e. exactly the frozen template header
(class 2). There is no other collision mass; item-specific tokens diverge
every subsequent row at every layer.

On class 2, quantified with the union-saturation correction (ASM-2301, and
ASM-2302's corrected band — revision 1's "<1%" figure was wrong across its
own bands and is not reused here): caching the ~q·T prefix rows shrinks a
layer's demanded *disk* union by only ~2–7% at the short-template/high-q
corner (≈ 2% at T=200, q=0.4; the remaining rows' union stays ≈ saturated)
≈ 1.5–5 s of a ~100 s prefill's disk at d ≈ 0.75, plus those rows' expert
matmuls inside the ~25% non-disk share ≈ q × 25% ≈ **~7.5 s** — call it
~9–12 s per first-touch. A shared cache converts 9 redundant first-touches
into hits: **~9 × (9–12) s ≈ 1.5–2 worker-minutes fleet-wide, ≈
$0.005–0.01**. That is the entire additional *synchronous* cross-worker win
during steady-state operation (still ≪ the ≤ ~$1.5 ASM-2313 band, which is
unchanged).

**The honest bottom line the maintainer asked for** [EXTRAPOLATION,
ASM-2313, load_bearing:false]: content-addressed S3 already IS a shared
cache across workers — it captures classes 2 (at bring-up), 4, and 5, which
are the only cross-worker classes with any mass. The *additional* hit
fraction a genuinely-shared synchronous database buys over
per-worker-NVMe + shared-S3 is **~0.1% of expert I/O (band 0–1%)** — the
residue is concurrent duplicate computation of the same key inside one
S3-sync window, which item-disjoint sharding confines to the template prefix
during the fleet's first minutes. At the ~$124–147 expected campaign spend
(ASM-2302) and 75% disk share, that is **≤ ~$1.5 per campaign**. Resolution:
per-worker hit counters split by entry origin (locally-computed vs
S3-restored vs would-have-been-remote) in the run manifest.

---

## 2. Q2 — Storage-backend comparison (eu-west-2, cited)

Workload shape: values 24 KB (Tier-A/B expert rows) up to a few MB (Tier-C
row-sum/prefix checkpoints); keys 32-byte BLAKE3; naive full store ~518 GB
Tier-A, pruned mirror ~400–550 GB (ASM-2308); ~22 M entries; access pattern =
bulk populate + bulk restore + high-rate existence probes.

Prices pulled 2026-07-13 from the AWS Price List bulk API
(`pricing.us-east-1.amazonaws.com/offers/v1.0/aws/<service>/current/eu-west-2/index.json`)
[LIT-BACKED, ASM-2315..2318]:

- **S3** (offer pub 2026-07-08): Standard **$0.024/GB-mo** (first 50 TB);
  Standard-IA $0.0131/GB-mo + **$0.01/GB retrieval**; PUT/COPY/POST/LIST
  $0.0053 per 1,000; GET $0.0042 per 10,000. In-region transfer to EC2 free.
  S3 Express One Zone does **not** appear in the eu-west-2 offer file (no
  Express storage class listed) — the single-digit-ms S3 tier is not an
  option in this region as of the cited publication [LIT-BACKED, ASM-2315].
- **DynamoDB** (pub 2026-06-08): on-demand **$0.1487 per million RRU**,
  **$0.7423 per million WRU**; storage $0.29715/GB-mo beyond 25 free GB-mo.
- **ElastiCache** (pub 2026-07-06): Valkey cache.t4g.micro $0.0144/h,
  cache.t4g.medium (3.09 GiB) $0.0576/h, cache.r7g.large (13.07 GiB)
  $0.2048/h; Redis ~25% higher per node.
- **RDS PostgreSQL Single-AZ** (pub 2026-07-10): db.t4g.medium (4 GiB)
  **$0.072/h**, db.m6g.large (8 GiB) **$0.184/h**, db.r6g.large (16 GiB)
  $0.264/h; **gp3 storage $0.133/GB-mo** — note 5.5× S3 Standard per GB.

Comparison at the design's sizes (monthly figures at 730 h/mo; campaign ≈
one full F1-K = 22,920 prefills ≈ 439–531 instance-hours spread over the
fleet) [EXTRAPOLATION where composed, ASM-2322]:

| Option | Role | Infra $/mo | Per-campaign request $ | Probe-path latency | Correctness fit | Ops burden | Verdict |
|---|---|---|---|---|---|---|---|
| **S3 Standard (existing)** | shared cold blob tier | **$13.2** (550 GB) | <$1 (segment-level PUT/GET; ~9k PUTs ≈ $0.05, 10 full restores ≈ 88k GETs ≈ $0.04) | 100–200 ms first-byte — bulk only, never per-probe | Ideal: immutable objects, atomic visibility, strong read-after-write, content-addressed naming is native | ≈ zero (bucket exists) | **KEEP — this is the shared cache** |
| + Bloom manifest index (recommended) | existence oracle | $0 (a ~28 MB file per snapshot) | ~$0 | ~100 ns local RAM | FP rate 1% → a false positive = one wasted segment-index check or recompute; harmless | zero | **ADD** |
| + DynamoDB key index | existence oracle | ~$0 (1.4 GB index ≈ inside 25 GB free tier; else $0.42) | $16.3 write sweep (22 M WRU); reads $51 if probed per-key (344 M probes) → must be batched/coarse, then <$5 | 5–20 ms (single-digit ms typical) | Conditional puts idempotent; 400 KB item cap fine for index | low (serverless) | optional, trigger-gated (§6) |
| ElastiCache Valkey index | existence oracle | $42 (t4g.medium, 3.09 GiB — tight for 22 M keys) to $150 (r7g.large) | — | sub-ms | volatile RAM; eviction/restart = misses (harmless, cost-only) | medium (cluster, VPC) | not justified — 10–35× dearer than DynamoDB for the same answer |
| RDS Postgres, index-only | existence oracle | ~$55 (db.t4g.medium $52.6 + 20 GB gp3 $2.7) | — | ~1–5 ms same-AZ | fine if insert-only discipline enforced; connection limits across 10 workers × threads | high (patching, backups, VPC, vacuum) | **not justified — adds nothing over Bloom/DynamoDB at 3–50× the cost** |
| RDS Postgres, blob store | shared blob tier | ~**$227** (db.m6g.large $134.3 + 700 GB gp3 $93.1, incl. WAL/bloat headroom) | — | ~1–5 ms + 24 KB TOAST reads; thousands/s per conn | mutable store — must self-impose immutability; partial-write discipline is yours to build (S3 gives it free) | high | **REJECT** — 17× S3 storage cost for a slower-than-NVMe, faster-than-necessary tier |
| DynamoDB blob store | shared blob tier | ~$163 storage (550 GB × $0.29715) | ~$392 write sweep (24 KB = 24 WRU × 22 M) | 5–20 ms | **400 KB item cap fails the few-MB Tier-C values** | low | REJECT |
| ElastiCache blob tier | shared hot blob | ~$6,430 (≈ 43 × r7g.large to hold 550 GB in RAM) | — | sub-ms | RAM volatility fine for a cache, but | medium | REJECT — 480× S3 |
| Modal Volume | shared FS | n/a | n/a | n/a | **separate accounts cannot share a local Modal Volume** (asm-expert-cache file, §purpose note); F1-K fleet is EC2 spot, not Modal | n/a | EXCLUDED [STIPULATED, ASM-2326] |

Standard-vs-IA note with 10 workers [folded into ASM-2322]: IA saves
$0.0109/GB-mo but charges $0.01/GB on retrieval — break-even ≈ 1.1 full-store
retrievals per month. A 10-worker fleet doing per-worker bring-up restores
(and re-provisioning after interruptions) is retrieval-heavy: 10 × 550 GB
restores would cost $55 in IA retrieval fees vs $0 on Standard. **Standard
wins for the fleet case** (the single-worker $5/mo IA option from XCACHE
revision 1 inverted at 10 workers; XCACHE §5.1 as revised now specifies
Standard class accordingly).

---

## 3. Q3 — Latency/throughput on the critical path

Probe volume: Tier-A = 200 rows × 75 layers = **15,000 probes per ~100 s
prefill**; Tier-B up to 8× = 120,000. Probes are layer-synchronous (layer
ℓ+1's inputs depend on layer ℓ's output), so at best they batch to 75
round-trips of ≤200 keys each.

Synchronous per-probe round-trips vs the 100 s prefill [EXTRAPOLATION,
ASM-2320; network latencies STIPULATED vendor-doc design inputs,
ASM-2319 — AWS documents S3
small-object/first-byte latency at ~100–200 ms and positions
DynamoDB/ElastiCache at single-digit-ms/sub-ms respectively]:

| Store | RTT | 15k unbatched probes | 75 layer-batches | Verdict on probe path |
|---|---|---|---|---|
| local NVMe (i4i instance store) | ~0.05–0.2 ms per 24 KB read | ~1–3 s, overlappable with compute | — | **the only acceptable probe path** |
| local Bloom snapshot (RAM) | ~100 ns | ~0.002 s | — | free existence oracle |
| ElastiCache | ~0.3–0.5 ms | +4.5–7.5 s (+5–8%) | ~0.05 s | tolerable but pointless (index only, $42–150/mo) |
| Postgres same-AZ | ~1–5 ms | +15–75 s (+15–75%) | ~0.3 s | unusable unbatched; batched, it's an expensive Bloom |
| DynamoDB | ~5–20 ms | +75–300 s (≥ doubles the prefill) | ~0.75 s (BatchGetItem) — but per-key billing = $51/campaign of reads | async/coarse only |
| S3 | ~100–200 ms | +25–50 **min** (15–30×) | +7.5–15 s even fully batched | bulk restore only, never per-probe |

Mitigations (these ARE the recommended architecture, §6) [STIPULATED,
ASM-2321]:

1. **The synchronous probe path is local-only**: NVMe hot tier + in-RAM Bloom
   snapshot. No network I/O inside moe().
2. **The shared tier is bulk-granular**: segment restore at bring-up /
   item-assignment (64 MB objects, ~1 s each, in-region transfer free), and
   async write-behind of closed segments on the existing per-item checkpoint
   cadence (XCACHE §7.4). A worker assigned a reassigned/#27 item prefetches
   that item's segments *before* starting its prefills.
3. **Existence index = Bloom over the S3 segment manifests** (~22 M keys ×
   10 bits ≈ 28 MB, ~1% FP), rebuilt on each manifest sync. A false positive
   degenerates to a recompute — cost, never correctness. This removes the
   entire reason a low-latency shared index (Redis/DynamoDB/Postgres) was
   conceivable.
4. Note the sharding dividend: at 10 workers each holding ~1/10 of items,
   per-worker Tier-A is ~52 GB — the XCACHE §2.4 NVMe-pressure concern
   (ASM-2308) essentially vanishes per worker; the 550 GB union lives in S3.

---

## 4. Q4 — Cost vs benefit, break-even

Benefit of a *new* shared tier beyond per-worker-NVMe + shared-S3 (§1):
≤ ~$1.5 per campaign (band $0.1–1.5) of avoided recompute [ASM-2313].

Costs (§2): Bloom index **$0**; DynamoDB index **~$17–21 per campaign**
(write sweep + batched reads, ~$0 storage); Postgres index **~$55/mo**;
Postgres blob **~$227/mo**; plus, for any synchronous use, the
latency-induced *slowdown* is itself a cost multiplier on 439–531
instance-hours (a +15% probe drag ≈ +$19 at spot — a shared DB used naively
would cost more in wall-clock than it saves in hits).

Break-even [EXTRAPOLATION, ASM-2322, load_bearing:false]: a shared database
pays for itself only if cross-worker-only duplicate compute exceeds its
price. Against the ≤ $1.5/campaign benefit band, the DynamoDB index needs
~11×, Postgres index-only ~37×, Postgres blob ~150× more cross-worker reuse
than exists under item-disjoint sharding. **No backend with a nonzero price
breaks even; the $0 Bloom-over-S3-manifest index always does.** Even in the
counterfactual where the sharding rule failed entirely (arms scattered across
workers), the remedy is *restore the item's segments from S3* — bytes the
shared tier already holds — not a new database.

**The $149 ceiling is untouched**: the recommendation adds ≈ $0–5/mo to the
storage/retention line (Standard-vs-IA delta + manifest requests), which sits
outside the EC2-compute ceiling scope exactly like the existing $8.5/mo
retention and $9–13/mo mirror lines (ASM-2205, ASM-2308), and adds zero
synchronous latency to any prefill.

---

## 5. Q5 — Correctness of a shared store

**Content-addressing makes the shared store exactly as safe as a local one.**
A hit means the BLAKE3 key matched — engine-tag, layer/expert ids, W_e-hash,
x-hash (ASM-2303) — and the value is the bit-exact output of that pure
function *whichever worker computed it*. The key contains no worker identity,
no timestamp, nothing mutable; entries are immutable and never updated in
place; therefore **sharing introduces no staleness path**: the outcomes
remain exactly {valid hit | miss}, fleet-wide (ASM-2307's proofs are
writer-agnostic). [STIPULATED, ASM-2323]

Concurrency hazards and their closures [STIPULATED, ASM-2323; S3 semantics
STIPULATED vendor-doc design input, ASM-2324]:

- **Write race (two workers compute the same key concurrently)**: both
  produce byte-identical values (P1/P2, ASM-2304); concurrent content-
  addressed puts are idempotent — last-writer-wins with identical bytes.
  Wasted compute, never corruption.
- **Partial/torn writes**: S3 PUT/multipart-complete is atomic — an object is
  never visible partially written [STIPULATED, ASM-2324]; inside segments,
  the **authoritative BLAKE3-128 record digest (ASM-2308), validated before
  any value is served**, rejects any torn or corrupted record on restore —
  the per-record CRC32 is a non-authoritative fast-reject/torn-tail hint
  only (collision floor ~2⁻³²; it supports no integrity guarantee).
  Partial-write exclusion therefore rests on atomic content-addressed puts
  **plus BLAKE3 verification**, never on CRC. (Postgres
  would make this *your* discipline to build — one more point against.)
- **Read-after-write**: S3 provides strong read-after-write consistency for
  new-object PUTs and overwrites [STIPULATED, ASM-2324]; and on 32-byte
  immutable content-addressed keys even eventual consistency would only
  manifest as a miss → recompute.
- **Fleet-uniform engine discipline**: entries collide across workers only if
  every worker runs the identical engine-tag (same binary hash, same
  `XCACHE_CANON` setting per ASM-2304). A mixed fleet doesn't go stale — it
  simply doesn't share (over-invalidation, never staleness); the launch
  script asserts one engine-tag fleet-wide.
- **Carve-outs travel with the item, not the worker**: the guard-set
  no-serve/no-populate flag and the routing-arm cache-OFF rule (ASM-2306)
  must live in the frozen item manifest so every worker enforces them
  identically — sharing widens the blast radius of a per-worker mis-config,
  so the flag must not be per-worker config.
- **Verify-on-hit covers remote entries**: `XCACHE_VERIFY=N` (ASM-2305)
  recomputes hits regardless of which worker wrote them — cross-worker
  corruption (bad NIC, bad RAM on a peer) is caught below that by the
  **authoritative BLAKE3-128 record-digest check before any serve
  (ASM-2308)**, which covers transport corruption; the CRC32 is only a fast
  reject ahead of it and guarantees nothing (collisions).

---

## 6. Q6 — Recommendation

**Tiered, as anticipated — and the shared tier the design already has is the
right one** [STIPULATED, ASM-2325]:

- **T0 (hot, per-worker)**: NVMe `XCACHE_DIR`, unchanged (µs, the only
  synchronous probe path). ~52 GB/worker under 10-way item sharding.
- **T1 (shared, persistent)**: the **existing S3 content-addressed bucket** —
  one bucket for the whole fleet, **Standard class** (not IA: retrieval fees
  invert at 10 workers, §2), segment-granular bulk I/O only (bring-up
  restore, item-assignment prefetch, async write-behind on the checkpoint
  cadence). This *is* the shared cache across all workers; the answer to
  "missing cache hits across workers" is that with content-addressed keys and
  the S3 mirror, no hit with material value is missed (§1).
- **T2 (existence index)**: a **per-worker Bloom snapshot of the S3 segment
  manifests** (~28 MB, rebuilt each manifest sync, FP → recompute). Cost $0.
  **Trigger-gated upgrade**: if the run-manifest origin-split counters
  (ASM-2313 resolution) show cross-worker duplicate compute > ~$5/campaign —
  i.e. the sharding assumption eroded — add a **DynamoDB on-demand key index**
  (~$17–21/campaign, batched + async, never per-probe synchronous). That is
  the entire escalation ladder.
- **Postgres: not recommended, plainly.** As a blob store it is ~$227/mo of
  instance + gp3 (17× S3 per GB) for a tier that is too slow for the probe
  path and no better than S3 for bulk; as an index it is ~$55/mo + connection
  and vacuum ops for what a $0 Bloom file answers; and it captures **no reuse
  class** that content-addressed S3 does not already capture (§1 table).
  If a genuinely relational need appears later (cross-campaign cache
  analytics, say), run queries over the S3 manifests offline — no standing
  database required.

Incremental cost of the recommended architecture over the ASM-2308 design:
**≈ $0–5/mo** (Standard-vs-IA delta on the mirror + manifest request noise);
incremental compute cost: **$0**; incremental latency on any prefill: **0**
(everything shared is bulk/async). The $149 ceiling and every XCACHE validity
rule (guard carve-out, logical counters, verify-on-hit) are unchanged.

---

## 7. What would change this answer

Recorded so the estimate is falsifiable rather than convenient:

1. **Sharding erosion** — if arms of an item stop being co-located (scheduler
   drift, fine-grained work stealing), cross-worker reuse mass grows toward
   the within-item σ (~41–55%); the remedy ladder is: item-granular S3
   prefetch first, DynamoDB index second, and only then reconsider a
   low-latency shared value store. Detected by the origin-split hit counters.
2. **Decode-heavy future experiments** — decode does not saturate per-layer
   unions (XCACHE §4.4), so per-token cross-worker sharing could carry real
   disk value; Tier-C over S3 (+ index) is the first resort there too.
3. **S3 Express One Zone arriving in eu-west-2** would offer a single-digit-ms
   shared tier at S3 semantics — the natural middle tier if (1) ever fires;
   absent from the region's offer file today [ASM-2315].
4. **Fleet scale ≫ 10** — first-touch waste (class 2) scales with worker
   count but stays ~7.5 s × (N−1); it reaches $1 only at N ≈ 1,000. Not a
   real trigger.

---

## 8. Assumption register block (ASM-2313..2326)

Emitted for coordinator registration in `registry/assumptions.jsonl` with the
landing commit; this pass writes no registry entry. Range 2313..2330 verified
free at emission (registry tail = ASM-2293; repo-wide grep for
ASM-2313..2330 empty). Full JSON in
`docs/next/design/asm-shared-cache-2313-2330.json`; summary:

- **ASM-2313** [EXTRAPOLATION, not load-bearing] — additional cross-worker
  hit fraction of a synchronous shared cache over per-worker-NVMe+shared-S3
  ≈ 0.1% (band 0–1%) of expert I/O, ≤ ~$1.5/campaign.
- **ASM-2314** [STIPULATED] — enumeration of cross-worker reuse classes under
  item-disjoint sharding; only prefix first-touch, item reassignment, and
  cross-experiment fleet re-provisioning are cross-worker, all S3-capturable;
  no cross-item key collisions beyond the shared template prefix.
- **ASM-2315..2318** [LIT-BACKED] — eu-west-2 prices: S3 (incl. Express One
  Zone absence), DynamoDB, ElastiCache, RDS Postgres, from the AWS Price List
  bulk API offer files (pub dates 2026-06-08..2026-07-10).
- **ASM-2319** [STIPULATED] — network-store latency ladder (S3 ~100–200 ms
  first-byte; DynamoDB single-digit-to-~20 ms; ElastiCache sub-ms) — a
  stipulated vendor-doc design input per AWS documentation, 2026 (sources
  below).
- **ASM-2320** [EXTRAPOLATION, not load-bearing] — per-prefill probe-latency
  arithmetic (15k probes; +5–8% Redis, +15–75% Postgres, ≥2× DynamoDB
  unbatched, 15–30× S3) and the 75-layer batching floor.
- **ASM-2321** [STIPULATED] — architecture rule: synchronous probe path is
  local-only (NVMe + Bloom); shared tier is bulk/async segment-granular.
- **ASM-2322** [EXTRAPOLATION, not load-bearing] — cost table and break-even
  (Postgres $55–227/mo vs ≤$1.5/campaign benefit; DynamoDB index
  $17–21/campaign; Bloom $0; Standard-vs-IA inversion at 10 workers; ceiling
  unchanged).
- **ASM-2323** [STIPULATED] — sharing preserves exactness: writer-agnostic
  bit-identity, idempotent puts, no staleness path, fleet-uniform engine-tag
  discipline, carve-out flags in the frozen item manifest, verify-on-hit
  covers remote entries.
- **ASM-2324** [STIPULATED] — S3 atomic object visibility + strong
  read-after-write consistency — a stipulated design input per the AWS S3
  data-consistency documentation, 2026 (source below).
- **ASM-2325** [STIPULATED] — the recommendation itself (T0 NVMe / T1 shared
  S3 Standard / T2 Bloom index with DynamoDB trigger-gated upgrade; no
  Postgres).
- **ASM-2326** [STIPULATED] — Modal Volume excluded (cross-account sharing
  unsupported; F1-K fleet is EC2 spot, not Modal).

### Pricing sources (retrieved 2026-07-13)

- AWS Price List bulk API, eu-west-2 offer files:
  [S3](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonS3/current/eu-west-2/index.json) (pub 2026-07-08),
  [DynamoDB](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonDynamoDB/current/eu-west-2/index.json) (pub 2026-06-08),
  [ElastiCache](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonElastiCache/current/eu-west-2/index.json) (pub 2026-07-06),
  [RDS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonRDS/current/eu-west-2/index.json) (pub 2026-07-10).
- Latency: [AWS S3 performance design patterns](https://docs.aws.amazon.com/AmazonS3/latest/userguide/optimizing-performance-design-patterns.html)
  (~100–200 ms small-object/first-byte; "use ElastiCache/CloudFront for
  single-digit-ms over S3"); [DynamoDB](https://aws.amazon.com/dynamodb/) and
  [ElastiCache](https://aws.amazon.com/elasticache/) product documentation
  (single-digit-ms / sub-ms positioning).
- Consistency: [AWS S3 data-consistency model](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html#ConsistencyModel)
  (strong read-after-write; objects never partially visible).
