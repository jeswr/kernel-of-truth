# XCACHE — cross-arm, cross-experiment expert-output cache for the GLM-5.2 programme

> **DESIGN ONLY — REVISION 3 (freeze-ready).** No code applied, no instance
> launched, no registry write, no git action, no model run, $0 spent in this
> pass. No feasibility conclusion is stated. This revision (designer-16,
> 2026-07-13) closes the second GPT-5.6 xhigh review — of revision 2 —
> (`poc/gpt56-review/expert-cache-r2/out/last-message.json`, verdict
> FIX-FIRST: 3 residual blockers + 1 non-blocking finding, all closed;
> resolution map at §11; the 8 findings that review marked RESOLVED are left
> untouched). Revision 2 (designer-13, 2026-07-13) folded in (a) the GPT-5.6
> xhigh review of revision 1
> (`poc/gpt56-review/expert-cache/out/last-message.json`, verdict FIX-FIRST —
> every blocking finding resolved; resolution map at §10) and (b) the
> XCACHE-SHARED research (`docs/next/design/glm52-shared-cache.md`,
> ASM-2313..2326 — its shared-tier recommendation adopted verbatim as §5.4).
> ASM block ASM-2300..2312: the CANONICAL source is the companion file
> `docs/next/design/asm-expert-cache-2300-2312.json`; §9 below reproduces that
> file VERBATIM (generated from it, byte-identical) for coordinator
> registration. Companion to:
> `poc/glm52-probe/kae-patch-draft/` (KaE ADD splice, colibri base commit
> `a78a06fc5acc4b0dc0f9ef03987c66b0559d1250`),
> `docs/next/design/glm52-followup-experiment.md` (F1-K, #28),
> `docs/next/design/glm52-expert-drop.md` (GLM-DROP, #27),
> `docs/next/design/glm52-f1k-cost-reduction.md` ($149 protocol).
> Revision 1 was written against repo commit
> `dcf55fb14f89f1a9c0e24788e911627a058e4468`; the shared-cache research it
> consolidates was written against `3611025a3580b13cfb69af1d31e3723b9b9d165c`.

## 0. One-paragraph summary

KaE never modifies native experts — the splice is `out[s] += g*K[c][l]` at the
moe() **output** (kae-add-path.patch hunk `@@ -1400`), after the routed top-8
sum + shared expert are accumulated. So the disk-bound native-expert work is a
pure function of (expert weights, per-row moe input) and is reusable wherever
those are byte-identical: across the b0/d0/d1-drng×3/d2/K arms for every token
whose layer-input has not diverged, across re-runs, and across **experiments**
(#28 KaE and #27 expert-drop score the same frozen item subset on the same
base checkpoint **under one byte-identical combined binary**, §5.2). XCACHE is
an **exact, persistent, per-expert content-addressed cache**: the Tier-B key
covers an enumerated byte domain (every weight/scale/metadata byte read, the
exact input row, the pinned engine, §2.2), and a hit is bit-identical to
recompute **conditional on BLAKE3 collision resistance and the pinned
execution environment** (§3.2) — auto-invalidated by any weight/engine/
upstream change, never served where an I/O counter is itself the measurement
(§3.4). Tier-A (per-row aggregate) caching is **permitted only under
campaign-wide mandatory canonical accumulation** with an order-complete key —
upstream's batch-union fp32 reduction order makes row-sums batch-dependent, so
without that discipline Tier-A is off and the cache is Tier-B-only (§3.1).
Honest saving model: the frozen claim is an accounting **identity** (§1.2,
ASM-2301); all numbers — union saturation, σ ≈ (ℓ*+1)/75 (~55% L1 / ~41% L2 /
~1.3% L3 per spliced arm), programme totals ~18–25% expert I/O, expected spend
~$124–147 — are non-load-bearing planning bands (ASM-2302). Serving is
enabled only through the **three-way no-negative-value gate** (paired
cache-ON/OFF bring-up measurement, §7): serve / disable-to-uncached /
halt-before-spend — the fallback is the uncached $149 model itself, so cache
overhead can never push spend past the ceiling; **the $149 ceiling is
unchanged and never depends on the lever**. Replay economics are scoped to
what the store actually retains (§5.3). The shared tier across the ~10-worker
fleet is the existing S3 content-addressed bucket + a $0 Bloom existence
index (§5.4, ASM-2313..2326); Postgres is rejected.

---

## 1. Sharing structure — the exact divergence geometry

### 1.1 Where arms diverge (structural contract, from the patch + causal attention)

Model facts [northstar §2; probe-main.log]: 75 MoE layers × 256 routed experts,
greedy top-8 + shared expert, hidden D = 6,144, int4 ≈ 370 GB, ≈ 19 MB/expert.
F1-K scoring is prefill-only (§R1.1: ONE prefill per item per arm, identical
template bytes across all spliced arms + b0; d3-text has different bytes).

The splice at layer ℓ modifies `out` (the moe-block output) for **gated rows
only**, after every native-expert contribution is accumulated. Divergence
propagates in exactly two ways, both strictly forward in the (position, layer)
DAG under causal attention:

1. **Residual/depth:** a gated row's residual stream differs from layer ℓ*+1
   onward (ℓ* = first splice layer). Its moe **inputs at layers ≤ ℓ* are
   identical across arms** — the splice acts after the layer-ℓ* expert sum is
   read out, so even the gated row's native expert work AT ℓ* is shared.
2. **Attention/width:** at layer ℓ*+1, every row at a position ≥ p* (p* = first
   gated position) attends to the gated row's diverged K/V and may diverge
   too. Rows at positions < p* **never** see a gated position (causal mask).

Shared region per item, per spliced arm vs b0 (T = template length):

```
            layer →  0 ........ ℓ*   ℓ*+1 ........ 74
 pos < p*           [ SHARED    ][ SHARED           ]   (causal: never sees carrier)
 pos ≥ p*           [ SHARED    ][ INVALIDATION CONE]
```

Two review-mandated precisions [ASM-2300]:

- The post-splice rectangle is a **potential invalidation cone**, not
  guaranteed byte divergence: rows there MAY diverge per arm, and the cache
  makes no assumption either way — every row in the cone is admitted or
  rejected purely by its x-hash (§2.2).
- The shared region's byte-identity is **conditional** on the pinned engine's
  per-row determinism and batch-composition independence (P1/P2, §3.1). For
  Tier-A row-sums specifically, colibri's batch-union fp32 accumulation order
  lets later rows perturb an earlier row's addition order, so the byte claim
  holds only under campaign-wide canonical accumulation (`XCACHE_CANON=1`)
  with the order-complete Tier-A key — the mandatory Tier-A precondition of
  §3.1. Per-expert Tier-B outputs involve no cross-expert reduction and are
  pinned by P1/P2 alone.

Shared **state** fraction f_state = q + (1−q)·(ℓ*+1)/75, q = p*/T.
Planning bands [EXTRAPOLATION, ASM-2302, non-load-bearing]: T ≈ 128–384
(use 200), header ≈ 30–60 tokens before the stem trigger → q ≈ 0.15–0.40
(use 0.3). Gated tokens themselves are few (≥1 trigger lemma per item,
typically 1–3 spans of 1–3 tokens) but that is NOT the operative number —
what matters is p* (everything after the first gated position enters the cone
past ℓ*).

Per pilot layer-set scenario (frozen carrier-blind per ASM-2040/2046), all
values planning bands under ASM-2302:

| Frozen L | first splice layer ℓ* | (ℓ*+1)/75 | f_state (q=0.3) |
|---|---|---|---|
| L1 (single mid-stack ≈ 40) | ≈ 40 | 0.547 | ≈ 0.68 |
| L2 (4 evenly spaced mid-to-late, first ≈ 30) | ≈ 30 | 0.413 | ≈ 0.59 |
| L3 (all MoE layers) | 0 | 0.013 | ≈ 0.31 |

### 1.2 The saving model: a frozen identity, plus banded numbers

The disk cost of a prefill is **per-layer expert unions**, loaded once per
moe() call for all rows ("expert letto 1 volta e moltiplicato per tutte le
posizioni", glm.c).

**The only frozen claim is the accounting identity** [STIPULATED, ASM-2301]:

```
saved physical bytes (per layer, per pass)
  = baseline physical bytes − miss-union physical bytes − cache overhead bytes
```

with its corollaries: a **partially-hit** layer saves `U_all − U_miss ≥ 0`
(the union difference) **before overhead** — a quantity that **may be zero**
(exactly when every expert demanded by a hit row is also demanded by at
least one miss row, i.e. the miss-union equals the full demanded union —
plausible under saturated unions) and whose net value after the overhead
term can be negative (one reason the G-XCACHE gate exists, §7); it is never
the hit-row fraction, and only the measured identity including overhead
determines net savings; a
**fully-hit** layer saves its entire demanded union plus its matmuls; and
physical NVMe savings after expert pinning/page cache need **not** be
proportional to requested union bytes — they are measured, not inferred.

The numeric instantiation [EXTRAPOLATION, ASM-2302, non-load-bearing]: under a
uniform-routing model, with S ≈ 200 rows × top-8 over 256 experts the union
per layer ≈ 256·(1−(1−8/256)^200) ≈ 99.8% of experts → ≈ 4.85 GB/layer,
≈ 364 GB per prefill — consistent with the ~100 s/prefill planning band at
~3.3 GB/s. Real routing is skewed and correlated, so measured unions may sit
below this. Under that model, removing the q·T prefix rows shrinks a layer's
union by **~2–7% at the short-template/high-q corner** (T=128, q=0.4 → ~7%;
T=200, q=0.4 → ~2%) — revision 1's "<1%" was wrong across its own bands and
is corrected here. The dominant saving still concentrates at layers where
**every** row hits, i.e. layers ≤ ℓ*: per spliced-arm prefill,

**σ ≈ (ℓ*+1)/75 — ~55% (L1), ~41% (L2), ~1.3% (L3)** — not f_state.

(The prefix q still buys full-depth *state* reuse — valuable for Tier-C
checkpointing (§4.4) and decode-time geometry, but F1-K is prefill-only.)

### 1.3 Programme-level shareable volume and speedup [EXTRAPOLATION, ASM-2302]

R=3 programme (per the $149 protocol): 22,920 prefill-equivalents ≈ main
8×1,440 = 11,520 (b0, d0, d1-drng×3, d2, K, d3-text) + construction 3,072 +
pilot ≈ 6,200 + guard 660 + misc.

Per item, the 7 same-byte passes (b0 + 6 spliced) cost 7×75 layer-loads
uncached vs 75 + 6×(75−(ℓ*+1)) cached — each distinct (row, layer,
upstream-state) is computed once, in whatever arm order the rotation dictates;
population is arm-agnostic because the key is content-addressed (§2).

| Component | prefills | saved (L1) | saved (L2) | saved (L3) |
|---|---|---|---|---|
| main, 6 spliced passes | 8,640 | 6×1,440×0.547 ≈ 4,725 | ≈ 3,570 | ≈ 115 |
| main, b0 + d3-text | 2,880 | 0 (populate / disjoint bytes) | 0 | 0 |
| pilot (grid × 4-member panel over dev; mixed L) | ≈ 6,200 | ≈ 550–900 | ≈ 550–900 | small |
| construction (with/without-prepend pairs differ from token 0) | 3,072 | 0 | 0 | 0 |
| guard set (EXEMPT — it IS the check, §3.4) | 660 | 0 | 0 | 0 |
| **total expert-I/O removed** | 22,920 | **≈ 23–25%** | **≈ 18–19%** | **≈ 1–2%** |

Wall-clock at an **assumed** disk share d = 0.75 — a pre-pinning
decode-profiling figure from probe-main.log, NOT a measured 128–384-row
prefill fraction under the frozen pinning policy [ASM-2302] —
×1/(1−0.75·saved) → **≈ 1.21× (L1), ≈ 1.16× (L2), ≈ 1.01× (L3)**. §7 turns
this into $, and the G-XCACHE gate (§7) replaces every one of these bands
with a paired measurement before serving is enabled.

---

## 2. Cache mechanism — exact, content-addressed, two tiers

### 2.1 What is cached

- **Tier-B (per-expert, the primitive):** value = y_e = expert e's raw output
  row (down(silu(gate·x)·(up·x))), D fp32 = **24 KB**, stored **pre-gating
  weight** (w_e is recomputed from the resident router — deterministic and
  cheap — so gating-weight changes never invalidate the expert entry).
  Tier-B involves no cross-expert reduction: its byte domain is pinnable by
  P1/P2 alone, which is why it is the primitive.
- **Tier-A (per-row aggregate, the compressor):** value = the row's full native
  moe output (routed top-8 weighted sum + shared expert), 24 KB/row/layer —
  8× smaller than Tier-B for the KaE case where no expert is ever modified.
  **Tier-A exists only under `XCACHE_CANON=1`** (mandatory canonical
  accumulation, §3.1) with the order-complete key of §2.2; without that, the
  cache is Tier-B-only.
- Value bytes are the **exact fp32 the engine computed** — no re-quantization,
  no fp16 truncation (exactness forbids it).

### 2.2 Keys — the enumerated byte domain [STIPULATED, ASM-2303]

All hashes BLAKE3-256. All key preimages use a **domain-separated,
length-delimited, fixed little-endian serialization**: every field is
`(u8 domain-tag, u32 length, bytes)`; a key/value `SCHEMA_VERSION` and a tier
byte lead every preimage; any schema change bumps `SCHEMA_VERSION` inside the
engine-tag (cold store — never an in-place reinterpretation).

```
engine-tag  = H( exact binary bytes (statically linked; else + hash of every
                 loaded numerical library) ‖ SCHEMA_VERSION ‖ IDOT_KERNEL ‖
                 ebits ‖ dbits ‖ CPU arch + feature fingerprint ‖
                 FP environment (rounding mode, FTZ/DAZ) ‖ every threading /
                 runtime knob that can affect any reduction schedule ‖
                 XCACHE_CANON state ‖ byte order )

W_e-hash    = H( expert e's gate ‖ up ‖ down quantized tensor bytes ‖
                 quantization scales / zero-points / block metadata ‖
                 shape/stride/dtype descriptors ‖ any bias or side tensor
                 actually read )                                   (per expert)
router-W-hash = H( every router tensor and config value actually read,
                 including score-correction biases and scaling factors ‖
                 shapes/dtypes )
x-hash      = H( the row's exact pre-moe input bytes: post-rmsnorm row, D×4B fp32 )
topk-config = exact bytes of TOPK / TOPP / norm-topk flag / routed scaling

Tier-B key  = H( engine-tag ‖ SCHEMA_VERSION ‖ tier=B ‖ layer-id ‖ expert-id ‖
                 W_e-hash ‖ x-hash )
Tier-A key  = H( engine-tag ‖ SCHEMA_VERSION ‖ tier=A ‖ layer-id ‖
                 router-W-hash ‖ shared-expert-W-hash + its accumulation
                 position ‖ topk-config ‖
                 ORDERED sequence [(expert-id, W_e-hash,
                                    exact routing-weight bits)]
                   in the canonical (XCACHE_CANON) accumulation order ‖
                 x-hash )                       (defined ONLY under CANON=1)
```

The Tier-A key is **order-complete**: it contains the exact routed ids, the
exact fp32 routing-weight bits, and (via CANON in the engine-tag plus the
ordered sequence) the exact addition order of the reduction it caches —
closing review finding 1's stale-aggregate path from the key side while §3.1
closes it from the engine side.

Probe order per row: run the router (resident weights, no disk) → know the
top-8 ids/weights → form Tier-A key → on miss, probe Tier-B per expert →
recompute only the missing experts. NOTE: layer-id/expert-id are in the key as
the maintainer specified (they also drive sharding, §2.4); validity needs only
(W_e-hash, x-hash, engine-tag) — the ids never *widen* validity, they only
forgo the (practically nil, int4) reuse between identical-weight experts.

**"Every byte read is hashed or engine-tag-pinned" is now a checklist, not a
slogan**: the enumeration above is the conformance list checked line-by-line
in code review of the eventual patch (ASM-2303); anything an implementation
reads outside it must be added to the key or engine-tag before serving is
enabled.

**No monolithic model-checkpoint hash anywhere in the key** (per the
maintainer refinement): a whole-model hash over-invalidates — modifying one
expert would cold the entire store. Per-component hashing gives maximal valid
reuse *within one pinned engine-tag* (§4).

The **per-expert weight-hash manifest** (21,504 routed experts + per-layer
router/shared/dense/attention component hashes, ≈ 0.7 MB) is computed once per
checkpoint at bring-up (~370 GB streamed ≈ 4–6 min on this box [ASM-2302]),
stored beside the cache and in S3, itself content-addressed by the checkpoint
file hash.

### 2.3 What a KaE run does with it

- **b0 (KAE=0)** populates Tier-A over all rows/layers (and Tier-B where
  enabled). **Population is arm-agnostic**: a spliced arm's rows in the shared
  region have byte-identical inputs, so its misses write the *same* keys —
  arm-order rotation (§7 discipline) is unaffected and costs nothing extra.
- **Spliced arms (K, d0, d1×3, d2)** hit for pos < p* at all layers and for
  all rows at layers ≤ ℓ*; they recompute wherever the x-hash misses in the
  cone. For gated rows at ℓ* the cache serves the **pre-carrier native sum**
  and `kae_apply_add` then adds `g·K[c][l]` on top — exactly the patch's
  splice point, zero interaction with cache contents.
- A layer where **every** row hits skips its entire expert load + matmul; a
  partially-hit layer loads only the union demanded by missed rows (saving
  `U_all − U_miss ≥ 0` per §1.2 — zero whenever the miss rows demand the
  full union — plus the hit rows' skipped matmuls).

### 2.4 Store, layout, integrity, eviction [STIPULATED, ASM-2308]

- **Layout:** content-addressed segments sharded by (layer, tier,
  W-hash-prefix): `XCACHE_DIR/<engine-tag>/<layer>/<tier>/<hh>/seg-*.xc`,
  append-only.
- **Record format and integrity** (review finding 3 — CRC32 cannot support an
  exactness bound; undetected-error floor ~2⁻³²):

  ```
  record = [ key 32B | len | value | BLAKE3-128( domain-tag ‖ key ‖ len ‖ value ) | crc32 ]
  ```

  - CRC32 is a **non-authoritative fast-reject / torn-tail detector only**.
  - The **BLAKE3-128 record digest is validated before any value is served**.
  - The **full 32-byte stored key** is compared against the probe key (no
    prefix or index-only serving).
  - A duplicate key with a **conflicting** value digest ⇒
    `ERR_XCACHE_CONFLICT`: never served, segment quarantined.
  - Write discipline: **single writer per segment**, fsync on segment close,
    closed segments immutable, per-segment index rebuilt by full scan on open
    (the index is advisory, never authoritative; a torn tail record fails its
    digest and is dropped).
- **Sizing (planning bands, ASM-2302):** unique unmodified rows ≈ 1,440 items
  × ~200 rows × 75 layers ≈ 21.6M × 24 KB ≈ **518 GB** Tier-A fp32 (+ ~72 GB
  d3-text rows, + ~100 GB construction contexts). Full Tier-B (×8 → ~4.1 TB)
  does NOT fit and is enabled selectively (e.g. layer-0 Tier-B for #27:
  ≈ 55 GB). i4i.2xlarge NVMe = 1.875 TB − 370 GB model − scratch →
  ≈ 1.3–1.4 TB free; under the 10-worker item sharding of §5.4 the per-worker
  Tier-A footprint is only ~52 GB. Bound with `XCACHE_GB` regardless.
- **Eviction:** by whole segment, priority-then-LRU; priority classes
  (highest kept longest): (1) layers ≤ max candidate ℓ* over the pilot grid,
  (2) construction-context rows, (3) b0 full-depth rows (re-run/audit +
  cross-experiment reuse), (4) arm-diverged rows — **written only under
  `XCACHE_DIVERGED=1`; the DEFAULT is `XCACHE_DIVERGED=0`, i.e. diverged rows
  are NOT stored** — evicted first when present. Eviction and store loss
  never affect **correctness** (a miss is a recompute), but they DO bound
  **replay coverage**: every replay-cost claim in §5.3 is scoped to what this
  retention policy actually keeps.
- **Overhead (planning band, ASM-2302):** probing hashes 24 KB/row/layer
  ≈ 360 MB/prefill ≈ 0.15–0.2 s at BLAKE3 speed — ≈ 0.2% of a 100 s prefill.
  Hit reads are 24 KB NVMe vs 4.85 GB/layer avoided. Measured, not assumed,
  by the G-XCACHE gate (§7).

---

## 3. Correctness — the exactness guarantee

### 3.1 Determinism premises and the mandatory Tier-A discipline [ASM-2304]

- **P1 (pure function):** the per-row expert output is a deterministic pure
  function f(W_e bytes, x bytes) — no RNG, fixed within-row accumulation order
  in the idot kernel.
- **P2 (batch-composition independence):** a row's per-expert output is
  identical whether computed in a batch of S rows or alone (per-row dot
  products; no cross-row reduction inside an expert). **Load-bearing** because
  cache misses shrink the recompute batch.
- **The known hazard, and the campaign-wide fix (review finding 1):**
  upstream moe() accumulates each row's routed experts in **batch-union
  order** ("routed nel loro ordine di union"), which depends on which OTHER
  rows share the batch; fp32 addition is non-associative, so **row-SUM bytes
  are not batch-invariant upstream** even where per-expert outputs are.
  Therefore **Tier-A is permitted only under mandatory canonical
  accumulation**: `XCACHE_CANON=1` (each row's routed experts accumulated in
  ascending-expert-id order, then the shared expert) is
  - frozen **before carrier construction and the pilot**,
  - folded into the **engine-tag**,
  - applied to **every pass of every arm, both experiments (#28/#27), the
    guard set (cache-OFF but same engine), and every cache-OFF comparison**,
  - and is **never** enabled as a mid-campaign remediation. A one-layer
    S=1-vs-batch spot check is not accepted as proof that the order
    dependency is absent elsewhere — the discipline is structural, not
    sampled.
- P1/P2 are **asserted, not assumed**: bring-up runs the §3.3 checks; if the
  CANON build fails them, **Tier-A is disabled** and the cache runs
  Tier-B-only; if P1/P2 fail for Tier-B per-expert outputs too, XCACHE is
  declared invalid for the build and the run proceeds cache-OFF (fail closed,
  `ERR_XCACHE_NONDET`) — savings forfeit, measurement untouched. The
  fail-closed policy is stipulated here; the bring-up P1/P2 **result** lands
  as a separate MEASURED register entry with patch/binary hashes and log SHA.

### 3.2 Hit == recompute — the conditional statement

A Tier-B hit means BLAKE3(W_e) and BLAKE3(x) both match ⇒ W_e and x are
byte-identical to the populating computation ⇒ by P1/P2, f(W_e, x) is
bit-identical ⇒ the cached value equals recompute exactly. Tier-A adds the
router/shared/topk hashes plus the **ordered (id, W-hash, routing-weight-bits)
sequence**, pinning the exact reduction it caches. This equality is stated as
**conditional, not an unconditional proof** [ASM-2303]:

- conditional on **BLAKE3 collision resistance** (bound ≤ 2⁻¹²⁸ — below any
  physical error floor, but an assumption, not a theorem about the system);
- conditional on **the pinned execution environment** actually satisfying
  P1/P2 (§3.1) — which is why §3.3 exists as a detection guard.

The key discipline is: *every byte the computation reads is either hashed
into the key (weights, scales, metadata, input row, routing config/bits) or
pinned by the engine-tag (binary, libraries, kernel, FP environment,
threading, CANON state, arch)* — with §2.2's enumeration as the reviewable
checklist. There is no cached quantity keyed on anything mutable that is not
hashed.

### 3.3 Verification protocol — a detection guard, not a proof [ASM-2305]

Validity is established by the complete key + deterministic computation
(§3.1–3.2). In-run verification exists to **detect implementation
violations**; sampling can never prove every hit exact, and no such claim is
made.

1. `XCACHE_VERIFY=N` (default 256; **N arbitrary**, not power-of-two-bound):
   interpret the first 8 bytes of the key as a little-endian u64; recompute
   the hit iff `u64 % N == 0`. Deterministic, RNG-free, replayable — and
   named accurately (second review, finding 4): a **deterministic per-key
   verification subset**, selecting ~1/N of **distinct keys** and verifying
   **every** served hit of a selected key. It is **not** per-hit-event
   sampling: the predicate is a pure function of the key, so repeated hits
   of one key are all-verified-or-all-skipped. Stated limitation: a
   violation confined to never-selected keys is invisible to this sampler;
   it is bounded by the coverage requirement (2) — a class with zero
   verifies has its hits voided and disabled — and by the bring-up checks
   (3)/(4). Any mismatch ⇒
   **abort the run** (`ERR_XCACHE_MISMATCH`), quarantine the store. Sketch:

   ```c
   if(hit){
       uint64_t s; memcpy(&s, key, 8);            /* little-endian u64 */
       if(s % xcache_verify_n == 0){
           expert_forward(tmp, We, x);            /* recompute, same kernel */
           if(memcmp(tmp, cached, (size_t)D*4)){ die("ERR_XCACHE_MISMATCH"); }
       }
   }
   ```

2. **Coverage requirement:** verify counters are reported per
   (tier × layer-band × hit origin: locally-computed vs S3-restored); every
   class that served hits must show verify > 0 by end of run, else that
   class's hits are voided in the cost accounting and disabled for the
   remainder.
3. Bring-up: one full dev item per arm scored cache-ON and cache-OFF; byte
   equality of the **complete final logit vector** (full vocab bytes at every
   scored position — not label logits only); both SHA-256 hashes are manifest
   entries.
4. Bring-up: S=1 vs S=full-batch per-row equality on at least **one early,
   one mid, and one late layer** (P2 assertion), plus a Tier-A
   aggregation-signature comparison whenever Tier-A is enabled.
5. Per-arm hit/miss/verify counters are manifest entries — the audit can see
   exactly how much was served from cache and that coverage held.

### 3.4 Non-perturbation of the measurements (the carve-outs) [ASM-2306]

The cache is exact in *values*, so quality endpoints (logits → accuracy) are
untouched by construction. The carve-outs are where the **instrument** is I/O
or where a check would become tautological:

- **Off-concept guard set (60 items): XCACHE fully OFF (no serve, no
  populate).** The guard's SHA-256 byte-identity of spliced arms vs b0 is the
  run-voiding validity check; serving spliced-arm guard prefills from b0's
  cache would make it vacuously true. **Enforcement asserts ZERO**: the guard
  items' per-item probe, hit, AND populate counters must all be exactly zero
  in the run manifest, and the audit checks those zeros directly — merely
  observing nonzero physical reads is NOT accepted as evidence the cache was
  off. (Cost: the 660 guard prefills are never discounted, §1.3.)
- **F1-A/F1-B routing arms: XCACHE OFF entirely**, enforced by the same
  zero-probe/zero-hit/zero-populate assertion. Their primary endpoint is
  expert miss-bytes — a cache IS a perturbation of that instrument.
- **REPLACE mode (if ever admitted post-K-1): gated rows at splice layers are
  NO-SERVE / NO-POPULATE for Tier-A.** REPLACE changes the **native** sum on
  those rows (an expert is skipped, its weight re-assigned) without changing
  any weight bytes or knob — the one KaE configuration whose modification is
  invisible to the Tier-A key, so an unmasked probe would serve a stale b0
  sum. The engine already knows the spans and `KAE_MODE` and masks exactly
  those (row, layer) pairs; Tier-B per-expert entries remain valid throughout
  (the substituted sum is always computed engine-side from them). ADD mode
  needs no mask — its native sum is untouched everywhere by construction.
- **Logical vs physical counters:** wherever an expert-loads counter is an
  endpoint or a gate (#27's ±5% matched-loads gate), the counter counts
  **logical demanded expert contributions / union loads** (router-demanded,
  incremented on hit and miss alike); physical disk reads, skipped matmuls,
  and cache hits are each reported as separate counters. A cache hit must
  never make an arm look "cheaper" to a dose-matching gate — and any
  dose/efficiency **measurement** arm runs XCACHE OFF.
- The carve-out flags live in the **frozen item manifest**, not per-worker
  config (ASM-2323 clause (e)): sharing widens the blast radius of a
  per-worker mis-config, so the flag carrier must be fleet-global.
- The d0-beats-b0 void trigger, flip matrices, and all §R3 statistics operate
  on per-item correctness — downstream of logits — hence inherit exactness.

---

## 4. Per-expert weight hashing — a reviewed implementation contract

Policy statement (maintainer's explicit priority): **serve every probe whose
key is valid** — across arms, passes, pilots, re-runs, experiments, and future
GLM-5.2 work; the only exemptions are §3.4's instrument carve-outs, which are
exempted because the measurement is I/O, not because validity fails. The
clauses below are a **reviewed implementation contract** (structural DAG
facts checked in code review against §2.2's byte-domain checklist), not
measured evidence; a separate MEASURED patch-review/log entry closes
conformance at bring-up [ASM-2307]. "Maximal reuse" is scoped: maximal
**within one pinned whole-binary engine-tag** and the layer/expert ids in the
key — cross-binary reuse does not exist (§5.2).

### 4.1 Contract (a): downstream changes never invalidate an unchanged expert

The transformer forward is a DAG; expert E at layer ℓ computes y = f(W_E, x)
where x is the row's post-rmsnorm layer-ℓ input. Everything downstream —
later layers, other experts' outputs at ℓ, the router's mixing weights, and
the KaE carrier (added to `out` AFTER y is accumulated, patch hunk `@@ -1400`)
— is **not an argument of f**. Information flows strictly forward; no
downstream edit can reach back into (W_E, x). Hence the key is unchanged and
the hit is valid at an unchanged input **regardless of what any later
component, other expert, or output-side carrier does**. Unmodified E hits
under KaE arms, under #27's masks (for still-routed experts at
not-yet-diverged rows), under any post-hoc output-side A/B.

### 4.2 Contract (b): direct invalidation is same-layer, self-only — downstream follows through the x-hash

Modifying expert Ê changes only BLAKE3(W_Ê). Tier-B keys of every other expert
contain their own W-hash and the x-hash — neither mentions W_Ê — so **at Ê's
own layer, for unchanged inputs, only Ê itself misses**, and Ê can never
serve stale bytes (its old keys are unreachable). Scope, per the review:
Ê's changed **output** alters downstream row inputs, so later-layer and
later-position misses correctly occur — delivered **through the x-hash by
contract (c)**, not claimed absent by this clause. Tier-A rows whose ordered
selection contains Ê miss (Ê's hash and position are in the ordered sequence)
and fall back to Tier-B, where the unmodified experts hit. Direct
invalidation is exactly as local as the modification; indirect invalidation
is exactly as wide as the modification's causal cone.

### 4.3 Contract (c): upstream changes are caught by the input hash

Any upstream change — earlier-layer weights, an earlier splice, a dropped
expert at a lower layer, different prompt bytes, different attention state —
that alters the row's layer-ℓ input at all alters its 24,576 input bytes ⇒
x-hash differs ⇒ **miss** ⇒ recompute. A change that leaves the input
byte-identical is, by definition, not a change f can observe — serving the
cached value is then not "stale", it is the recompute's exact output (§3.2,
conditional as stated there). There is no third case: staleness is
impossible, only (valid hit | miss).

Corner honestly closed: experts read *only* the §2.2-enumerated byte domain.
If a future engine change made an expert read anything else (a global scale, a
LoRA side-tensor, a runtime-mutable bias), that byte-source must be added to
the key or the engine-tag — enforced by re-running §3.3 on any engine bump
(the engine-tag already colds the store on any binary change, so the failure
mode is over-invalidation, never staleness).

### 4.4 Dense / attention / router analogues (sketch, optional Tier-C)

Same principle per component — but explicitly a **separate sketch, not
covered by the §4.1–4.3 contract** [ASM-2312]: value keyed on
(component-weight-hash ‖ exact input hash ‖ engine-tag). Router and dense-MLP
rows are per-row pure functions — directly cacheable, though RAM-resident and
cheap (inside the non-disk share), so priority is low. Attention output for a
row depends on the **whole prefix** at that layer, so its input-hash is a
running prefix hash — which is exactly a **per-item prefix state checkpoint**:
store (residual rows + KV) for the maximal unmodified prefix per (item, layer
set), key = H(engine-tag ‖ all component hashes up to ℓ ‖ token-id prefix ‖
per-layer prefix x-hash chain). Tier-C would let fully-shared prefixes skip
attention too and is the natural decode-time extension; **not required** for
the F1-K savings in §1.3 and deferred as an optimization note. (Its few-MB
values also exceed the DynamoDB item cap — one more reason the shared tier
for it is S3-only, §5.4.)

---

## 5. Persistence — cross-experiment, cross-instance, cross-worker

### 5.1 Persistent store

- **Primary: NVMe** (`XCACHE_DIR` on the i4i instance store), layout §2.4,
  bounded by `XCACHE_GB` (default: free-space − 15% headroom).
- **Durable: S3 artifacts bucket** (instance store dies with the spot
  instance). Segments are immutable ⇒ trivially mirrorable (`aws s3 sync` of
  closed segments, background, on the per-item checkpoint cadence). On a fresh
  spot instance: restore the weight-hash manifest + priority-class-1/2
  segments first (partial restore is fine — anything absent is a miss),
  lazily pull the rest. **Storage class: S3 Standard** — the fleet analysis
  (ASM-2322) shows Standard-vs-IA inverts at 10 workers because IA's $0.01/GB
  retrieval fee makes bring-up restores expensive; revision 1's IA option is
  superseded. ~400–550 GB pruned mirror ≈ **$13/mo** Standard [ASM-2302,
  banded], on top of the existing $8.5/mo retention line; same-region restore
  ≈ 0.5–1 h vs hundreds of instance-hours to recompute. Prune policy = the
  §2.4 priority classes; the S3 copy is subordinate (never a correctness
  input — every served byte still passes the full key + record-digest check
  locally, §2.4).

### 5.2 Cross-experiment validity — the identical-binary requirement [ASM-2309]

Validity follows from §4 **plus one hard precondition the review added
(finding 9): reuse exists only across byte-identical engine-tags.**
Kernel-family rounding differs across builds/backends; the same model +
template is insufficient, and because the engine-tag hashes the whole binary,
a KaE-enabled F1-K binary and a separately patched GLM-DROP binary would
share **no** keys. The plan is therefore **one hash-pinned combined binary**
containing KAE, DROP, and XCACHE as inert env-gated features, with the
identical `XCACHE_CANON` state and runtime fingerprint in both experiments;
both experiments' manifests pin **identical template bytes, token IDs,
tokenizer hash, and binary tag** (GLM-DROP §5.1 already freezes the same
frozen F1-K template). A #27 probe then hits a #28-populated entry iff
engine-tag, W-hash, and x-hash all match — the same guarantee as within-run.
A #27 modified/masked configuration misses exactly where §4.2/§4.3 say:
dropped experts are never probed (masked out); surviving experts hit until
the first (row, layer) whose input has diverged from any cached forward.
(The semantic per-component engine-tag alternative is noted and declined: it
is substantially harder to prove safe, and the combined binary achieves the
same reuse with a whole-binary hash.)

### 5.3 Cross-experiment value, honestly quantified [EXTRAPOLATION, ASM-2309]

- **Precondition worth engineering:** the combined binary + template/tokenizer
  pinning of §5.2. Without it, cross-experiment reuse is nil by construction.
- **#27 reuse, correctly named (review finding 10):** the eligible near-full
  hit is the **b0-full arm at TOPK=8** (byte-equal config to F1-K's b0),
  subject to retention of class-3 segments — ~1,440 prefills ≈ **$10–13** at
  spot avoided. The pilot's u-topk arm chooses k* from {4,3,2}+fallbacks, so
  k*=8 is **not** a possible u-topk outcome (revision 1 misnamed this).
  For k* < 8, unmasked u-topk reuses **layer-0 Tier-B outputs** (top-k ⊆
  top-8; layer-0 inputs are embeddings, identical) ≈ 1/75 of a $10–13 arm ≈
  **$0.13–0.17 per arm** before non-disk effects (revision 1's $1–2 was
  arithmetic error). Masked arms hit only where a selected expert was
  previously computed at a byte-identical input — lower, and reported from
  actual Tier-B intersection counters, not projected.
- **Re-runs / audits / replay — scoped to retention (review finding 7):** a
  full-programme replay at ≈ **$35–45** (≈ 0.25–0.30× of ~$149) is
  **conditional** on a separately provisioned, complete, immutable
  `XCACHE_DIVERGED=1` snapshot with **no eviction and verified S3 coverage** —
  which adds ~1–2.2 TB over the ~518–531 GB Tier-A baseline, exceeds the
  default NVMe free space, and therefore lives in S3 and is priced as its own
  line — **and** on the fact that guard items always recompute (they are
  never cached, §3.4). Under the **default** `XCACHE_DIVERGED=0` policy this
  projection is **withdrawn**: replay cost is then priced from the
  retained-key inventory and measured hit counters, not assumed. The
  revision-1 claim that spot-interruption repeats are "≈ free" is
  **withdrawn**: completed items are already skipped by per-item checkpoints,
  and an interrupted spot instance loses unsynced NVMe data. The snapshot
  decision (provision or not, sizing, S3 line) is made explicitly at the
  F1-K freeze and recorded in manifest (A).
- **Future carrier re-construction:** the 3,072 construction prefills are
  unmodified-model forwards (KAE=0) over frozen contexts; dump-mode re-dumps
  at NEW candidate layers replay at ≈ 0.25–0.30× → ≈ **$8–10 saved per future
  carrier variant** — conditional on retention of class-2 segments.
- **Any future GLM-5.2 experiment** over the same checkpoint + item set
  inherits the b0 forward iff it runs the identical combined binary (§5.2).

Zero-value cases stated plainly: different prompts, different tokenizer,
different checkpoint, **different binary/build/backend** → different keys →
cold cache. The cache is exact; it monetizes *repetition*, and this programme
is built on frozen, repeated inputs — that is why the value is real here.

### 5.4 The shared tier across workers (folded from XCACHE-SHARED) [ASM-2313..2326]

The maintainer's issue-#30 question — *should a single shared database (e.g.
Postgres) serve all ~10 F1-K workers so cross-worker hits are not missed?* —
was researched separately (`glm52-shared-cache.md` + ASM-2313..2330). Its
conclusion is **adopted here verbatim as the XCACHE shared-tier design**; the
findings are integrated, not re-derived:

- **The design already has its shared cache: the S3 content-addressed
  bucket.** One bucket, all workers, keyed by content, writer-agnostic.
  Under the #30 sharding rule (all arms of an item on one worker) the
  dominant reuse class (~95%+ of reuse value: cross-arm within an item) is
  within-worker **by construction**; the genuinely cross-worker classes
  (frozen-template prefix first-touch, item reassignment after spot
  interruption, #27's cross-experiment baseline on a re-provisioned fleet)
  are already captured by the S3 tier [ASM-2314].
- **Tiering [ASM-2321/2325]:** **T0** per-worker NVMe hot tier (~52 GB/worker
  under 10-way sharding) — the **only synchronous probe path**; no network
  I/O inside moe(). **T1** the shared S3 bucket, **Standard class** (IA
  inverts at 10 workers, §5.1), bulk/async and segment-granular only
  (bring-up restore, item-assignment prefetch, write-behind on the checkpoint
  cadence). **T2** a **zero-cost Bloom-filter existence index** — a
  per-worker in-RAM snapshot (~28 MB, ~1% FP) over the S3 segment manifests,
  rebuilt on the existing checkpoint-cadence sync; a false positive
  degenerates to one recompute (cost, never correctness).
- **What a synchronous shared DB would add: ~0.1% of expert I/O (band 0–1%),
  ≤ ~$1.5/campaign** [ASM-2313] — against **~$55/mo (Postgres index-only) to
  ~$227/mo (Postgres blob store)**, with ~1–5 ms round-trips that are
  unusable on the per-probe critical path anyway (15,000 probes per ~100 s
  prefill; +15–75% wall-clock if probed synchronously) [ASM-2318/2320].
  **Postgres is REJECTED** [ASM-2325]: it captures no reuse class that
  content-addressed S3 does not already capture, at 17× S3 storage cost.
  **DynamoDB is the optional, trigger-gated index upgrade** (~$17–21 per
  campaign, batched + async, never per-probe): taken only if the
  origin-split hit counters show cross-worker duplicate compute
  > ~$5/campaign (i.e. the sharding assumption eroded).
- **Sharing preserves exactness** [ASM-2323]: the key contains no worker
  identity and nothing mutable; concurrent duplicate computes of one key
  produce byte-identical values (P1/P2) and content-addressed puts are
  idempotent; S3 object visibility is atomic with strong read-after-write
  [ASM-2324]; entries collide across workers only under a **fleet-uniform
  engine-tag** (same combined binary, same `XCACHE_CANON` — asserted by the
  launch script; a mixed fleet over-invalidates, never goes stale). The
  §3.4 carve-out flags travel in the frozen item manifest, fleet-globally.
  `XCACHE_VERIFY` covers remote-origin entries unchanged — and §3.3's
  coverage requirement explicitly counts the S3-restored hit class.
- **Cost:** the recommended shared tier adds ≈ **$0–5/mo** on the
  storage/retention line (outside the EC2-only ceiling scope, §7) and **zero
  synchronous latency** to any prefill. The $149 ceiling is untouched.

Consistency note reconciling the two ASM blocks: ASM-2313/2314's #27
cross-experiment class is the **b0-full (TOPK=8)** arm of ASM-2309 (the
earlier "k*=8 u-topk" phrasing is superseded); the fleet-uniform engine-tag
of ASM-2323(d) is exactly §5.2's identical-combined-binary requirement plus
§3.1's CANON state; ASM-2322's Standard-class conclusion supersedes revision
1's IA note in §5.1; and the ~52 GB/worker figure resolves revision 1's NVMe
pressure concern (§2.4). No clause of ASM-2313..2326 conflicts with
ASM-2300..2312 as revised.

---

## 6. Upstream — colibri PR sketch, staged [ASM-2310]

A persistent, per-component-versioned expert-output cache remains a strong
upstream candidate, same etiquette as the ANN and KaE drafts (out-of-tree
patch vs pinned commit `a78a06fc5acc4b0dc0f9ef03987c66b0559d1250`,
inert-by-default, unit tests + ASan, zero deps — single-file vendored BLAKE3
**pinned by source hash and license file**). Per review finding 11 the slice
is **staged into four reviewable PRs** rather than one:

1. **PR-1: Tier-B record-only** + deterministic recompute verification.
2. **PR-2: read/serve** with immutable record integrity (BLAKE3-128
   authoritative + CRC fast-reject, §2.4) and crash/torn-tail tests.
3. **PR-3: Tier-A** — only after aggregation-order semantics (canonical
   accumulation) are settled with the maintainer; not before.
4. **PR-4 (non-PR): S3 synchronization stays harness-side**, never in-engine.

- **Surface:** `XCACHE=<dir>` (unset ⇒ inert), `XCACHE_GB`,
  `XCACHE_VERIFY=N`, `XCACHE_TIERB=0|1|layers`, `XCACHE_CANON`,
  `XCACHE_DIVERGED=0|1`, `XCACHE_RO=1` (serve, never write — audit mode).
  Hit/miss/verify counters in the existing STATS output. A self-contained
  `xcache.h` mirroring the kae.h pattern (static-inline, unit-testable
  without a Model). Code-size figures are **nonbinding planning notes**.
- **Inertness requirement when unset (strengthened):** zero allocation, zero
  hashing, zero I/O, zero threads, zero banner/config changes,
  pristine-vs-patched **full-output byte equality**, AND a **disassembly
  review of moe()** — a false runtime branch can change register
  allocation/code generation even when never taken.
- **Touch points:** moe() expert loop (probe before load/compute, insert
  after), model load (per-expert hash manifest, built once and sidecar-cached
  keyed by checkpoint hash), banner.
- **Why upstream wants it:** any post-hoc A/B on a frozen model (steering
  vectors, expert ablation, TOPK sweeps, quantization diffs of single
  components) re-pays the identical expert work today; crash-resume of long
  benchmark sweeps; deterministic-replay regression testing; and the
  per-expert hash manifest doubles as a weight-integrity checker.
- **PR caveats to state:** valid only for deterministic kernel builds
  (IDOT_KERNEL in the tag; the built-in VERIFY mode is the detection guard);
  batch-composition independence asserted at first use; Tier-A requires the
  canonical-accumulation semantics of PR-3; disk footprint can exceed model
  size on long corpora (hence XCACHE_GB + segment LRU).

No upstream action is taken in this pass.

---

## 7. Integration into the F1-K run harness — the fourth cost lever, gated

Stack order (each on top of the previous, per the $149 protocol):

1. **Spot i4i.2xlarge** ($0.20–0.28/h) — price lever, unchanged.
2. **Expert-pinning + warm page cache** (1.20× pessimistic) — unchanged.
   **Interaction with XCACHE is measured, not assumed** (review finding 8):
   removing layers ≤ ℓ* from the miss stream may remove exactly the hot bytes
   pinning was already serving and leave a colder residual stream — the
   revision-1 claim that pinning "can only improve" is withdrawn. The two
   levers attack the same disk bytes; their combined effect enters only
   through the G-XCACHE paired measurement below.
3. **R=3 derangements** — volume lever, unchanged.
4. **XCACHE** — projected to remove ≈ 23–25% (L1) / 18–19% (L2) / 1–2% (L3)
   of total expert I/O [ASM-2302, banded] → wall ≈ 1.21× / 1.16× / 1.01× at
   the assumed d = 0.75 — **enabled for serving only through the gate below**.

**GATE G-XCACHE — the no-negative-value gate, three-way and fail-safe
[STIPULATED, ASM-2311].**
Cache overhead (hashing, Tier-A writes, hit reads, verification recomputes,
smaller-miss-batch inefficiency, S3 sync, restore time, canonical
accumulation) must not push spend UP. Frozen in manifest (A); evaluated at
bring-up **before campaign spend**; paired cache-ON vs cache-OFF measurement
on the same dev items under the **frozen pinning policy**, covering:

- (i) populate-pass overhead, (ii) a full-hit pass, (iii) a partial-hit pass,
  (iv) verification recompute overhead, (v) S3 sync + fresh-instance restore
  time (charged to the ledger as compute).

Decision — **three-way and exhaustive** (second review, blocker 2: the
revision-2 fallback "otherwise run cache-OFF" could itself exceed the
ceiling, e.g. projected ON $151 / OFF $155). Let P_ON / P_OFF be the paired
measurement's total metered campaign projections (both under the frozen
pinning policy and CANON state) and C the standing $149 affordability
ceiling:

1. **SERVE** iff `P_ON ≤ P_OFF` **and** `P_ON ≤ C`.
2. **DISABLE (fail-safe)** — else, iff `P_OFF ≤ C`. Exact measured trigger:
   `P_ON > P_OFF` (measured cache overhead ≥ measured savings on the frozen
   paired bring-up measurement) or `P_ON > C`. Exact action: the **entire
   campaign runs with XCACHE serving OFF** — the uncached $149 model the
   ceiling was derived on — and the lever is reported landed-but-inert. A
   disabled cache contributes zero campaign cost, so cache overhead can
   **never** push spend past the ceiling.
3. **HALT** — else (`P_OFF > C`: even the uncached protocol fails the
   ceiling — a defect of the cost model, not of the cache). No campaign arm
   is started; bring-up spend already incurred is charged to the ledger; the
   ceiling is re-derived under the ASM-2205 protocol before any further
   spend (reverting to the pristine pre-CANON protocol if the halt precedes
   carrier construction and the pilot). XCACHE is never enabled to rescue
   affordability.

**In-run tripwire:** after SERVE, if the metered ledger at any per-item
checkpoint shows cumulative measured cache overhead ≥ cumulative measured
avoided recompute (separate counters per §3.4), serving is **disabled for
the remainder** — fail-safe to the uncached path; disable, never abort (hits
are exact, so the measurement is untouched). With
this three-way gate, **the $149 ceiling honestly remains unchanged**:
expected spend ≈ $124 (L1) / $129 (L2) / $147 (L3) [ASM-2302, advisory] — a
~$0–25 expected reduction decided by the carrier-blind pilot's frozen L, not
knowable (or influenceable) in advance; the L3 corner grants ≈ nothing, and
ceilings must cover corners. **Accounting:** restore/sync compute is charged
to the EC2 ledger; S3 storage/request costs sit **outside** the EC2-only
ceiling scope on the storage/retention line (like the existing $8.5/mo and
mirror lines) and are reported separately. Side values not in the ceiling:
conditional replay per §5.3, #27 b0-full at ≈ $10–13 if retained,
re-construction at ≈ $8–10/variant.

Harness/manifest additions (freeze-ordering compliant — all frozen in
manifest (A) before any spend, per ASM-2047/2278 discipline):

1. Manifest entries: engine-tag, checkpoint hash + weight-manifest hash,
   XCACHE config (GB, VERIFY N, tier policy, **CANON state, DIVERGED
   state**), per-arm hit/miss/verify counters **split by origin**, the
   cache-ON/OFF **full-logit-vector** hash pairs from §3.3, the G-XCACHE
   paired measurements and enable/disable decision.
2. Registered exemptions verbatim: guard set OFF **with zero
   probe/hit/populate counters asserted**, routing arms OFF likewise, logical
   counters for load-matched gates (§3.4), carve-out flags in the frozen item
   manifest.
3. Arm rotation unchanged (§7 of the F1-K design): the cache makes arm order a
   cost variable only — exactness means it cannot become a measurement
   variable; aggregate saving is order-invariant (§1.3).
4. Spot lifecycle: closed segments synced to S3 (Standard class, §5.4) with
   the existing per-item checkpoint cadence; fresh-instance bring-up restores
   manifest + priority-1/2 segments before first prefill; Bloom index rebuilt
   on each manifest sync.
5. #27 co-location / fleet: #27 inherits the store read-write **under the
   identical combined binary** (§5.2); its match-gate counters follow the
   logical-counter rule; the fleet launch script asserts one engine-tag
   fleet-wide (§5.4).

Failure containment: every cache fault (record-digest failure, CRC
fast-reject, mismatch, nondeterminism, ENOSPC) fails **closed to cache-OFF
recompute** — the experiment can always complete as if XCACHE never existed;
only §3.3(1) mismatches abort (a mismatch means the determinism premises are
broken, which taints more than the cache).

## 8. Risks and open points

- **P1/P2 under CANON** remain the load-bearing premises (§3.1) — resolved
  mechanically at bring-up; CANON-build failure ⇒ Tier-B-only; Tier-B failure
  ⇒ cache-OFF, all savings forfeit, nothing else harmed. [ASM-2304]
- **G-XCACHE may fail** — measured overhead can exceed measured savings
  (especially at L3); serving is then DISABLED (branch 2) and the campaign
  runs the uncached $149 model, whose ceiling never depended on the lever;
  if even the uncached projection exceeds the ceiling, the gate HALTS before
  any campaign spend and the ceiling is re-derived (branch 3) — cache-OFF is
  never run at a projected spend above the ceiling. [ASM-2311]
- **Frozen L = L3** makes within-run savings ≈ nil (§1.2) — the lever's value
  is pilot-contingent. [ASM-2302]
- **Replay coverage** is bounded by retention: without the explicit
  `XCACHE_DIVERGED=1` snapshot decision at freeze, the $35–45 replay figure
  stays withdrawn. [ASM-2309]
- **Guard-set temptation**: the single most dangerous misuse is serving guard
  prefills from cache — registered as a run-voiding protocol violation with
  zero-counter enforcement, not a tuning choice. [ASM-2306]
- **Fleet drift**: a mixed-binary or mixed-CANON fleet silently forfeits
  sharing (over-invalidation, never staleness) — launch-script assertion.
  [ASM-2323; §5.4]
- The §1.3 volume/saving numbers inherit the planning bands (T, q, pilot
  composition, d) — EXTRAPOLATION under ASM-2302; resolved by the run's
  metered ledger and the G-XCACHE measurements.

## 9. Assumption register block (ASM-2300..2312)

Canonical source: `docs/next/design/asm-expert-cache-2300-2312.json` — the
block below is that file reproduced **verbatim** (byte-identical; generated
from it). For coordinator registration in `registry/assumptions.jsonl` with
the landing commit; this pass writes no registry entry.

```json
{
 "range": "ASM-2300..2312",
 "purpose": "Companion assumption block for XCACHE, the persistent per-component-weight-hashed exact expert-output cache design for GLM-5.2 experiments (docs/next/design/glm52-expert-cache.md). REVISION 2 (2026-07-13, designer-13): folds the GPT-5.6 xhigh FIX-FIRST review (poc/gpt56-review/expert-cache/out/last-message.json) and the XCACHE-SHARED research (docs/next/design/glm52-shared-cache.md, ASM-2313..2326) into one consolidated freeze-candidate block. Key changes vs revision 1: Tier-A is permitted ONLY under campaign-wide mandatory canonical accumulation with an order-complete key (findings 1); the key byte domain is fully enumerated with a domain-separated fixed-endian serialization and the exactness claim is stated as conditional (finding 2); record integrity is BLAKE3-128-authoritative with CRC32 demoted to fast-reject (finding 3); the verification protocol is restated as a detection guard with arbitrary-N sampling and tier/layer/origin coverage (finding 4); proof (b) is scoped to direct same-layer invalidation (finding 5); saving numerics are separated from the frozen accounting rule (finding 6); the full-replay projection is scoped to the actual retention policy and the near-free-interruption claim is withdrawn (finding 7); a no-negative-value gate protects the unchanged $149 ceiling (finding 8); cross-experiment reuse requires a byte-identical combined binary (finding 9); GLM-DROP reuse accounting is rewritten around b0-full (finding 10); the upstream slice is staged (finding 11); the .md section-9 mirror is generated verbatim from THIS file as the canonical source with no invalid tags (finding 12); and policy is separated from projections throughout (finding 13). REVISION 3 (2026-07-13, designer-16, freeze-ready): closes the SECOND GPT-5.6 xhigh review, of revision 2 (poc/gpt56-review/expert-cache-r2/out/last-message.json, verdict FIX-FIRST; resolution map at the design's section 11), leaving the 8 findings that review marked RESOLVED untouched: (r2 blocker 1) ASM-2301's partial-hit corollary now reads U_all - U_miss >= 0 and MAY BE ZERO, with net savings decided only by the measured identity including overhead; (r2 blocker 2) ASM-2311's gate is a three-way decision - SERVE iff P_ON <= P_OFF and P_ON <= ceiling; else DISABLE serving iff P_OFF <= ceiling (fail-safe to the uncached $149 model, so cache overhead can never push spend past the ceiling); else HALT before any campaign spend and re-derive the ceiling - plus an in-run overhead-vs-savings tripwire; (r2 blocker 3) the shared block's ASM-2323 clause (b) is corrected so record integrity in the shared tier is BLAKE3-128-authoritative with CRC32 demoted to a fast-reject/torn-tail hint, byte-consistent with ASM-2308; (r2 finding 4) ASM-2305's sampler is named what it is - a deterministic per-key verification subset (~1/N of DISTINCT keys), not per-hit-event sampling - with its limitation stated, and the shared design's residual revision-1 '<1%' first-touch figure is replaced by the corrected band. This block is BYTE-CONSISTENT with, and cites, the shared-tier block ASM-2313..2326: the shared tier of record is per-worker NVMe (hot) + the shared S3 content-addressed bucket (cold, Standard class) + a zero-cost Bloom existence index on the checkpoint cadence; DynamoDB is trigger-gated optional; Postgres is rejected. Central registration in registry/assumptions.jsonl is the COORDINATOR's action with the landing commit, after the standing review gate. This pass writes NO registry/assumptions.jsonl entry, takes NO git action, runs NO model, spends $0, and states NO feasibility conclusion.",
 "owner": "designer-16",
 "backing_artifacts": [
  "docs/next/design/glm52-expert-cache.md (the governing design; its section 9 mirror is generated verbatim from this file)",
  "poc/gpt56-review/expert-cache/out/last-message.json (first GPT-5.6 xhigh review, of revision 1, verdict FIX-FIRST; resolved in revision 2, resolution map at the design's section 10)",
  "poc/gpt56-review/expert-cache-r2/out/last-message.json (second GPT-5.6 xhigh review, of revision 2, verdict FIX-FIRST; 3 residual blockers + 1 non-blocking finding, closed by revision 3, resolution map at the design's section 11)",
  "docs/next/design/glm52-shared-cache.md + docs/next/design/asm-shared-cache-2313-2330.json (XCACHE-SHARED research, folded in as the design's section 5.4 shared tier; recommendation adopted, not re-argued)",
  "poc/glm52-probe/kae-patch-draft/ (KaE ADD splice draft vs colibri base commit a78a06fc5acc4b0dc0f9ef03987c66b0559d1250; splice = out[s]+=g*K[c][l] at moe() output, kae-add-path.patch hunk @@-1400)",
  "docs/next/design/glm52-followup-experiment.md (F1-K; sections 2.3/2.7/R1.1/R6; ASM-2035/2040/2046/2047/2048)",
  "docs/next/design/glm52-f1k-cost-reduction.md (the ASM-2205 $149 spot+pinning+R=3 protocol this lever stacks on; the issue-#30 ~10-worker sharding rule)",
  "docs/next/design/glm52-expert-drop.md (GLM-DROP #27; shared item subset, b0-full TOPK=8 arm, matched-loads gate the logical-counter rule protects)"
 ],
 "assumptions": [
  {
   "id": "ASM-2300",
   "tag": "STIPULATED",
   "claim": "KaE CROSS-ARM DIVERGENCE GEOMETRY, STRUCTURAL CORE ONLY (a reviewed implementation contract, not measured evidence): the ADD splice modifies moe() OUTPUT only (out[s]+=g*K[c][l], kae-add-path.patch hunk @@-1400), so in the (position, layer) causal DAG, per item with first gated position p* and first splice layer l*: (i) rows at pos<p* never attend to a gated position (causal mask), and all rows at layers <= l* precede the splice read-out, so their per-row expert computations are REUSABLE across b0 and all spliced arms; (ii) the region pos>=p* AND layer>l* is a POTENTIAL INVALIDATION CONE - inputs there MAY diverge per arm, no byte divergence is guaranteed or assumed, and the cache treats every row in it through the x-hash (hit only on byte-equal inputs); (iii) clause (i)'s byte-identity is CONDITIONAL on the pinned engine's per-row determinism and batch-composition independence (P1/P2, ASM-2304): for Tier-A row-sums it requires campaign-wide canonical accumulation (XCACHE_CANON=1) plus the order-complete Tier-A key of ASM-2303, because upstream colibri accumulates routed experts in batch-union order and fp32 addition is non-associative, so later rows can otherwise perturb a prefix row's sum at ULP level. All numeric planning bands (q, T, f_state and their L1/L2/L3 instantiations) live in ASM-2302 (EXTRAPOLATION, non-load-bearing).",
   "rationale": "The sharing structure is a DAG fact of causal attention plus the splice point, but its byte-level force is conditional on reduction-order discipline (GPT-5.6 review finding 1 and adjudication); it is stated as an enforced invariant to be verified at bring-up, never as measured evidence, and carries no numbers.",
   "backing_ref": "poc/glm52-probe/kae-patch-draft/kae-add-path.patch (colibri base a78a06fc5acc4b0dc0f9ef03987c66b0559d1250); docs/next/design/glm52-followup-experiment.md sections 2.3/R1.1; docs/next/design/glm52-expert-cache.md section 1.1; poc/gpt56-review/expert-cache/out/last-message.json finding 1",
   "owner": "designer-13",
   "load_bearing": true,
   "status": "open",
   "resolution_path": "Verified mechanically at bring-up per ASM-2305: per-row/per-layer input-hash and aggregation-signature comparisons across arms on dev items (not final-logit equality alone); a subsequent MEASURED register entry with run-log SHA closes conformance; q/T bands resolve separately under ASM-2302.",
   "date": "2026-07-13"
  },
  {
   "id": "ASM-2301",
   "tag": "STIPULATED",
   "claim": "XCACHE SAVING ACCOUNTING RULE, THE IDENTITY ONLY (a reviewed implementation contract, not measured evidence): per layer and per pass, saved physical bytes = baseline physical bytes - miss-union physical bytes - cache read/write/hash overhead bytes. Corollaries frozen with it: a partially-hit layer saves U_all - U_miss >= 0 (the difference of demanded expert unions) BEFORE the overhead term - a quantity that MAY BE ZERO (it is zero exactly when every expert demanded by a hit row is also demanded by at least one miss row, i.e. the miss-union equals the full demanded union, plausible under saturated unions) and whose NET value after cache overhead can be negative, which is one reason serving is gated by ASM-2311; it is never the hit-row fraction of the layer, and only the measured identity including overhead determines net savings; a fully-hit layer saves its entire demanded union plus its matmuls; physical NVMe savings after expert pinning and page cache need NOT be proportional to requested union bytes and are measured, never inferred. Every numeric instantiation - union-saturation fractions, per-layer-set sigma, disk share d, wall-clock multipliers, spend - is model-dependent (uniform-routing and planning-band assumptions) and lives in ASM-2302 (EXTRAPOLATION, non-load-bearing). No claim is made that later re-derivation moves in any particular direction.",
   "rationale": "Only the accounting identity is strong enough to freeze; the numbers that previously rode on it (uniform-routing saturation, a '<1%' subset-saving figure that is false at the short-template/high-q corner, a decode-profiled 75% disk share) are projections and are moved out per GPT-5.6 review finding 6 and the adjudication. Revision 3: the revision-2 'never zero' corollary was itself false (the miss-union can equal the full demanded union) and is corrected to '>= 0, may be zero' per the second review's blocker 1.",
   "backing_ref": "docs/next/design/glm52-expert-cache.md section 1.2; poc/glm52-probe/results/probe-main.log (facts only: 75 layers, ~19 MB/expert); poc/gpt56-review/expert-cache/out/last-message.json finding 6; poc/gpt56-review/expert-cache-r2/out/last-message.json blocker 1",
   "owner": "designer-13",
   "load_bearing": true,
   "status": "open",
   "resolution_path": "Instantiated at bring-up from measured per-layer physical-byte counters over multiple representative dev items under the frozen pinning policy; recorded in a MEASURED follow-up entry with log SHA; projections then re-derive from measurement in ASM-2302.",
   "date": "2026-07-13"
  },
  {
   "id": "ASM-2302",
   "tag": "EXTRAPOLATION",
   "claim": "XCACHE NUMERIC ANNEX (all planning bands and projections; advisory only, gated by ASM-2311 and never load-bearing): (i) geometry bands: T ~ 128-384 (use 200), q ~ 0.15-0.40 (use 0.3), f_state = q + (1-q)(l*+1)/75 ~ 0.68 (L1) / 0.59 (L2) / 0.31 (L3); (ii) uniform-routing union model: 256*(1-(1-8/256)^S) ~ 99.8% at S~200 -> ~4.85 GB/layer, ~364 GB/prefill, consistent with the ~100 s/prefill planning band at ~3.3 GB/s; real routing is skewed and correlated so measured unions may sit below this; prefix-subset union reduction is ~2-7% at the short-T/high-q corner (T=128,q=0.4 -> ~7%; T=200,q=0.4 -> ~2%), not '<1%'; (iii) per-spliced-arm saving sigma ~ (l*+1)/75 ~ 0.55 (L1) / 0.41 (L2) / 0.013 (L3); within-F1-K totals at R=3 (22,920 prefill-equivalents): expert-I/O removed ~23-25% (L1) / ~18-19% (L2) / ~1-2% (L3); wall-clock x1.21/x1.16/x1.01 at an ASSUMED disk share d=0.75, which is a pre-pinning decode-profiling figure from probe-main.log, NOT a measured 128-384-row prefill fraction under the frozen pinning policy; expected spend ~$124 (L1) / ~$129 (L2) / ~$147 (L3) against the $149 model, ceiling unchanged; (iv) store sizes: Tier-A full ~518 GB fp32 (+~72 GB d3-text, +~100 GB construction), full Tier-B ~4.1 TB (does not fit; selective enablement, e.g. layer-0 ~55 GB), i4i.2xlarge free ~1.3-1.4 TB after the 370 GB model, ~52 GB/worker under 10-way item sharding; retaining diverged rows (XCACHE_DIVERGED=1) adds ~1-2.2 TB and exceeds default NVMe free space, hence S3-resident if provisioned; (v) overheads and ops: probe hashing ~0.2% of a 100 s prefill, weight-hash manifest ~0.7 MB built in ~4-6 min per checkpoint, S3 pruned mirror ~400-550 GB ~ $13/mo Standard class, fresh-instance restore ~0.5-1 h.",
   "rationale": "One non-load-bearing annex holding every number so the load-bearing entries (ASM-2300/2301/2308) stay purely structural, per the review adjudication; nothing downstream may treat these bands as evidence.",
   "backing_ref": "docs/next/design/glm52-expert-cache.md sections 1.1-1.3/2.4/5.1/7; docs/next/design/glm52-f1k-cost-reduction.md (ASM-2205 arithmetic); docs/next/design/glm52-shared-cache.md section 2 (S3 Standard pricing via ASM-2315); poc/gpt56-review/expert-cache/out/last-message.json findings 6/8",
   "owner": "designer-13",
   "load_bearing": false,
   "status": "open",
   "resolution_path": "Resolved by the F1-K bring-up measurements (per-layer physical bytes, measured unions, measured disk share under pinning, ASM-2311 gate timings) and the run's metered cost ledger with per-arm hit/miss counters; any band that fails re-derivation is replaced by the measurement before further use.",
   "date": "2026-07-13"
  },
  {
   "id": "ASM-2303",
   "tag": "STIPULATED",
   "claim": "XCACHE KEY SCHEMA, FULL BYTE DOMAIN, AND CONDITIONAL EXACTNESS: all key preimages use a domain-separated, length-delimited, fixed little-endian serialization (every field = u8 domain-tag, u32 length, bytes; SCHEMA_VERSION and a tier byte lead every preimage). Byte-domain enumeration - W_e-hash = BLAKE3 over expert e's gate, up, and down quantized tensor bytes PLUS quantization scales/zero-points/block metadata PLUS shape/stride/dtype descriptors PLUS any bias or side tensor actually read; router-W-hash = BLAKE3 over every router tensor and config value actually read, including score-correction biases and scaling factors; x-hash = BLAKE3 over the row's exact pre-moe input bytes (post-rmsnorm row, D x 4 B fp32); topk-config = exact bytes of TOPK/TOPP/norm-topk/routed-scaling. Tier-B key = BLAKE3(engine-tag || SCHEMA_VERSION || tier=B || layer-id || expert-id || W_e-hash || x-hash). Tier-A key (defined ONLY under XCACHE_CANON=1, ASM-2304) = BLAKE3(engine-tag || SCHEMA_VERSION || tier=A || layer-id || router-W-hash || shared-expert-W-hash and its accumulation position || topk-config || the ORDERED sequence of (expert-id, W_e-hash, exact routing-weight bits) in the canonical accumulation order || x-hash) - order-complete, so the key pins the exact fp32 reduction. engine-tag = BLAKE3 over the exact binary bytes (statically linked; otherwise plus the hashes of every loaded numerical library) || SCHEMA_VERSION || IDOT_KERNEL || ebits/dbits || CPU architecture + feature fingerprint || FP environment (rounding mode, FTZ/DAZ) || every threading/runtime knob that can affect any reduction schedule || XCACHE_CANON state || byte order. Values are the exact fp32 the engine computed (no precision truncation). EXACTNESS STATEMENT (conditional, not an unconditional proof): a hit is bit-identical to recompute CONDITIONAL on (a) BLAKE3 collision resistance (bound <= 2^-128) and (b) the pinned execution environment satisfying P1/P2 (ASM-2304); under those conditions every byte the computation reads is either hashed into the key or pinned by the engine-tag, and the enumeration above is the conformance CHECKLIST verified in code review of the eventual patch - anything an implementation reads outside it must be added to the key or engine-tag before serving is enabled. No monolithic model-checkpoint hash appears in any key (per-expert hashing supersedes it to avoid over-invalidation).",
   "rationale": "GPT-5.6 finding 2: 'every byte read is hashed' was previously asserted without a byte-domain specification; this entry pins the exact domain, the serialization, and states equality as conditional on collision resistance and the pinned environment.",
   "backing_ref": "docs/next/design/glm52-expert-cache.md sections 2.2/3.2/4; poc/glm52-probe/kae-patch-draft/kae.h (splice-after-accumulation precedent); poc/gpt56-review/expert-cache/out/last-message.json finding 2",
   "owner": "designer-13",
   "load_bearing": true,
   "status": "open",
   "resolution_path": "Frozen verbatim into the F1-K manifest (A) cache-config entry before any spend; the byte-domain checklist is checked line-by-line in code review of the xcache patch; enforced in-run by the ASM-2305 detection guard; any key-schema change bumps SCHEMA_VERSION inside the engine-tag (cold store), never an in-place reinterpretation.",
   "date": "2026-07-13"
  },
  {
   "id": "ASM-2304",
   "tag": "STIPULATED",
   "claim": "XCACHE DETERMINISM PREMISES + MANDATORY CANONICAL ACCUMULATION FOR TIER-A: P1 - per-row per-expert output is a pure deterministic function of the ASM-2303 byte domain (no RNG, fixed within-row accumulation order in the idot kernel); P2 - per-row per-expert output is independent of batch composition/size S (required because cache misses shrink the recompute batch). KNOWN HAZARD (GPT-5.6 finding 1): upstream moe() accumulates each row's routed experts in batch-union order, which depends on which OTHER rows share the batch; fp32 addition is non-associative, so row-SUM bytes are NOT batch-invariant upstream even where per-expert outputs are. THEREFORE TIER-A IS PERMITTED ONLY UNDER CAMPAIGN-WIDE CANONICAL ACCUMULATION: XCACHE_CANON=1 (each row's routed experts accumulated in ascending-expert-id order, then the shared expert) is frozen BEFORE carrier construction and the pilot, folded into the engine-tag, and applied to EVERY pass of EVERY arm, both experiments (#28 and #27), the guard set (which runs cache-OFF but on the same engine), and every cache-OFF comparison - it is never enabled as a mid-campaign remediation, and a one-layer S=1-vs-batch spot check is not accepted as proof that the order dependency is absent elsewhere. If the CANON build fails the ASM-2305 bring-up checks, Tier-A is disabled and the cache runs Tier-B-only (per-expert outputs, whose byte domain is pinned without any cross-expert reduction); if P1/P2 fail for Tier-B per-expert outputs too, XCACHE is declared invalid for the build and the campaign runs cache-OFF (fail closed, ERR_XCACHE_NONDET) - savings forfeit, measurement untouched. These premises are a reviewed implementation contract, asserted not assumed; the fail-closed serving policy is what this entry stipulates, and the eventual bring-up P1/P2 result lands as a SEPARATE MEASURED entry carrying patch/binary hashes and log SHA.",
   "rationale": "P2 is the premise that could silently split hits and misses into different numeric universes; the review's adjudicated fix is to make canonical accumulation the mandatory precondition of Tier-A rather than an optional response to one sampled failure, and to keep policy (this entry) separate from the future measurement (findings 1/13).",
   "backing_ref": "docs/next/design/glm52-expert-cache.md section 3.1; colibri glm.c moe() at base commit a78a06fc5acc4b0dc0f9ef03987c66b0559d1250 (batch-union accumulation order); poc/gpt56-review/expert-cache/out/last-message.json findings 1/13",
   "owner": "runner-4",
   "load_bearing": true,
   "status": "open",
   "resolution_path": "Resolved at F1-K bring-up by the ASM-2305 checks (S=1 vs batched per-row comparisons on early/mid/late layers, aggregation-signature comparison, full-logit-vector equality) recorded as a separate MEASURED register entry; PASS enables serving per tier; Tier-A FAIL under CANON disables Tier-A for the campaign; Tier-B FAIL disables XCACHE and this entry is closed 'premise false, cache unused'.",
   "date": "2026-07-13"
  },
  {
   "id": "ASM-2305",
   "tag": "STIPULATED",
   "claim": "XCACHE VERIFICATION PROTOCOL - A DETECTION GUARD, NOT A PROOF: validity of a hit rests on the complete key domain (ASM-2303) plus the determinism premises (ASM-2304); in-run sampling exists to DETECT implementation violations and can never prove every hit exact. Protocol: (1) XCACHE_VERIFY=N (default 256, N arbitrary - not restricted to powers of two): interpret the first 8 bytes of the key as a little-endian u64 and recompute the hit iff u64 mod N == 0; deterministic, RNG-free, replayable - NAMED ACCURATELY (second review, finding 4): a DETERMINISTIC PER-KEY VERIFICATION SUBSET selecting ~1/N of DISTINCT keys and verifying EVERY served hit of a selected key; it is NOT per-hit-event sampling (the predicate is a pure function of the key, so repeated hits of one key are all-verified-or-all-skipped), and its stated limitation - a violation confined to never-selected keys is invisible to this sampler - is bounded by the class-coverage requirement in (2) (a class with zero verifies has its hits voided and disabled) and the bring-up checks in (3)/(4); any mismatch ABORTS the run and quarantines the store (ERR_XCACHE_MISMATCH); (2) COVERAGE REQUIREMENT: verify counters are reported per (tier x layer-band x hit origin: locally-computed vs S3-restored), and every class that served hits must show verify > 0 by end of run, else that class's hits are voided in the cost accounting and disabled for the remainder; (3) bring-up scores one full dev item per arm cache-ON and cache-OFF and requires byte equality of the COMPLETE final logit vector (full vocab bytes at every scored position - not label logits only), recorded as SHA-256 manifest entries; (4) bring-up runs S=1 vs full-batch per-row output comparisons on at least one early, one mid, and one late layer, plus a Tier-A aggregation-signature comparison whenever Tier-A is enabled; (5) every other cache fault (record-digest failure, CRC fast-reject, ENOSPC, missing segment) fails closed to recompute. A cached result is never load-bearing without live in-run detection coverage over its class.",
   "rationale": "GPT-5.6 findings 4/13: one dev item per arm plus ~1/N recomputation is a detector, not a proof, and the previous low-byte-mask expression implemented 1/N only for power-of-two N <= 256; the second review (r2 finding 4) additionally corrected revision 2's 'hit-event sampling' label - u64(key) mod N is a per-key selector, so it is now named a deterministic per-key verification subset with its limitation stated; validity is established by the key discipline and determinism, and this entry claims only detection.",
   "backing_ref": "docs/next/design/glm52-expert-cache.md section 3.3; poc/gpt56-review/expert-cache/out/last-message.json finding 4; poc/gpt56-review/expert-cache-r2/out/last-message.json finding 4",
   "owner": "runner-4",
   "load_bearing": true,
   "status": "open",
   "resolution_path": "Executed at bring-up and continuously in-run; the audit checks per-class verify counters and the full-logit-vector hash pairs; zero verifies in a serving class or a missing pair voids the cache's use in that run's cost accounting (never the quality data, which is exact regardless by recompute fallback); the bring-up result lands as a separate MEASURED entry.",
   "date": "2026-07-13"
  },
  {
   "id": "ASM-2306",
   "tag": "STIPULATED",
   "claim": "XCACHE MEASUREMENT CARVE-OUTS (validity-critical): (1) the 60-item off-concept GUARD SET runs with XCACHE fully OFF in both directions (no serve, no populate) - serving spliced-arm guard prefills from b0's cache would make the run-voiding byte-identity check vacuously true; violating this is a run-voiding protocol breach, not a tuning choice; ENFORCEMENT ASSERTS ZERO: the guard items' per-item XCACHE probe, hit, AND populate counters must all be EXACTLY ZERO in the run manifest, and the audit checks those zeros directly (merely observing nonzero physical reads is NOT accepted as evidence the cache was off); (2) F1-A/F1-B ROUTING ARMS run XCACHE OFF entirely, enforced by the same zero-probe/zero-hit/zero-populate assertion (their endpoint IS miss-bytes; a cache is a perturbation of that instrument); (3) wherever an expert-loads counter is an endpoint or gate (GLM-DROP's +/-5% matched-loads gate), the counter counts LOGICAL DEMANDED EXPERT CONTRIBUTIONS / UNION LOADS (router-demanded, incremented on hit and miss alike), with physical disk reads, skipped matmuls, and cache hits each reported as separate counters; any dose/efficiency MEASUREMENT arm runs XCACHE OFF; (4) REPLACE mode (if ever admitted post-K-1): gated rows at splice layers are NO-SERVE/NO-POPULATE for Tier-A - REPLACE changes the NATIVE sum on those rows without changing any weight bytes or knob, the one KaE configuration invisible to the Tier-A key, so an unmasked probe would serve a stale b0 sum; the engine masks exactly those (row, layer) pairs from spans+KAE_MODE; Tier-B per-expert entries remain valid throughout; ADD mode needs no mask (its native sum is untouched everywhere by construction).",
   "rationale": "The cache is exact in values; these are the places where the instrument is I/O or the check would become tautological. Per the review adjudication, guard enforcement now asserts zero probes/hits/populates rather than inferring from nonzero physical reads, and the logical counter is named for what it counts.",
   "backing_ref": "docs/next/design/glm52-expert-cache.md section 3.4; docs/next/design/glm52-followup-experiment.md section 7.4 (guard byte-identity); docs/next/design/glm52-expert-drop.md section 4 (match gate); poc/gpt56-review/expert-cache/out/last-message.json findings 10/13",
   "owner": "skeptic-3",
   "load_bearing": true,
   "status": "open",
   "resolution_path": "Frozen verbatim in manifest (A); mechanically enforced by the harness (guard and routing-arm item ids carry a no-cache flag in the FROZEN ITEM MANIFEST per ASM-2323 clause (e), not per-worker config); audit asserts the zero probe/hit/populate counters for every carved-out item.",
   "date": "2026-07-13"
  },
  {
   "id": "ASM-2307",
   "tag": "STIPULATED",
   "claim": "PER-EXPERT WEIGHT HASHING - REVIEWED IMPLEMENTATION CONTRACT (not measured evidence) for reuse WITHIN one pinned engine-tag: (a) DOWNSTREAM changes (later layers, other experts at the same layer, the router's mixing weights, the KaE carrier added to moe output AFTER the expert sum is accumulated) are not arguments of f(W_E, x) in the forward DAG, so they never invalidate an unchanged expert at an unchanged input; (b) SCOPE - DIRECT SAME-LAYER SELF-ONLY INVALIDATION: modifying expert E-hat changes only BLAKE3(W_E-hat), which appears in no other expert's Tier-B key, so at ITS OWN layer and for UNCHANGED inputs only E-hat itself misses, and E-hat can never serve stale bytes (its old keys are unreachable); E-hat's changed OUTPUT then alters downstream row inputs, so later-layer and later-position misses correctly FOLLOW THROUGH THE x-HASH - downstream invalidation is delivered by clause (c), not claimed absent; Tier-A rows whose ordered selection contains E-hat miss and fall back to Tier-B, where the unmodified experts hit; (c) any UPSTREAM change that alters E's input alters the hashed input bytes -> miss; one that leaves the input byte-identical is unobservable by f, so the hit equals the recompute exactly (conditional per ASM-2303/2304). Reuse is maximal only WITHIN the pinned whole-binary engine-tag and the layer/expert ids in the key; cross-binary reuse does not exist (ASM-2309 precondition). Dense/attention/router analogues are a separate deferred sketch (ASM-2312) and are NOT covered by this contract. Corner: if a future engine makes experts read bytes outside the ASM-2303 enumerated domain, those bytes must join the key or the engine-tag - the engine-tag colds the store on any binary change, so that failure mode is over-invalidation, never staleness. A later MEASURED patch-review/log entry closes conformance at bring-up.",
   "rationale": "Supersedes the monolithic checkpoint-hash key (which would cold the whole store on any single-expert modification); per the review adjudication this is framed as a reviewed implementation contract with 'self-only miss' scoped to direct same-layer invalidation and downstream misses routed through the input hash (finding 5).",
   "backing_ref": "docs/next/design/glm52-expert-cache.md section 4; poc/glm52-probe/kae-patch-draft/kae-add-path.patch hunk @@-1400 (carrier after accumulation); poc/gpt56-review/expert-cache/out/last-message.json finding 5 and adjudication",
   "owner": "designer-13",
   "load_bearing": true,
   "status": "open",
   "resolution_path": "Clauses (a)-(c) are checked in code review of the eventual xcache patch against the ASM-2303 byte-domain checklist; a separate MEASURED patch/log entry at bring-up closes conformance; the corner clause is enforced by re-running the ASM-2305 checks on every engine-tag change.",
   "date": "2026-07-13"
  },
  {
   "id": "ASM-2308",
   "tag": "STIPULATED",
   "claim": "XCACHE PERSISTENT STORE - POLICY AND RECORD INTEGRITY ONLY (all capacities, S3 costs, restore times, hash overheads, and build times live in ASM-2302): content-addressed append-only segments sharded by (layer, tier, weight-hash prefix), path XCACHE_DIR/<engine-tag>/<layer>/<tier>/<hh>/seg-*.xc. RECORD FORMAT: [key 32 B | len | value | BLAKE3-128 over (domain-tag || key || len || value) | crc32]. CRC32 is a NON-AUTHORITATIVE fast-reject and torn-tail detector ONLY - it cannot support any exactness bound (undetected-error floor ~2^-32); the BLAKE3-128 record digest is validated BEFORE any value is served, and the FULL 32-byte stored key is compared against the probe key (no prefix or index-only serving). A duplicate key with a conflicting value digest raises ERR_XCACHE_CONFLICT: the record is never served and the segment is quarantined. WRITE DISCIPLINE: single writer per segment, fsync on segment close, closed segments immutable, per-segment index rebuilt by full scan on open (the index is advisory, never authoritative; a torn tail record fails its digest and is dropped). EVICTION: whole-segment, priority-then-LRU with classes (1) layers <= max candidate l* over the pilot grid, (2) construction-context rows, (3) b0 full-depth rows, (4) arm-diverged rows (written only under XCACHE_DIVERGED=1, evicted first; DEFAULT is XCACHE_DIVERGED=0, i.e. diverged rows are NOT stored). FALLBACK: eviction and store loss never affect CORRECTNESS (a miss is a recompute) - but they DO bound REPLAY COVERAGE, so every replay-cost claim is scoped to what this retention policy actually keeps (ASM-2309).",
   "rationale": "Store mechanics are bounded and fail-closed-to-recompute so the exactness invariant lives entirely in the key; per GPT-5.6 finding 3 the integrity story is now BLAKE3-authoritative with CRC demoted, and per the adjudication every numeric rider is moved to the non-load-bearing annex (ASM-2302).",
   "backing_ref": "docs/next/design/glm52-expert-cache.md sections 2.4/5.1; poc/gpt56-review/expert-cache/out/last-message.json findings 3/7",
   "owner": "designer-13",
   "load_bearing": false,
   "status": "open",
   "resolution_path": "Realized layout and integrity behaviour verified in code review + crash/torn-tail unit tests of the xcache patch (PR-2 of ASM-2310); realized sizes and costs resolve under ASM-2302; retention-vs-replay coverage is decided at the F1-K freeze under ASM-2309.",
   "date": "2026-07-13"
  },
  {
   "id": "ASM-2309",
   "tag": "EXTRAPOLATION",
   "claim": "CROSS-EXPERIMENT VALUE, honestly bounded and preconditioned: (i) PRECONDITION - IDENTICAL BINARY: cross-experiment reuse exists ONLY across byte-identical engine-tags; kernel-family rounding differs across builds/backends, so 'same engine family' is insufficient. The plan is ONE hash-pinned combined binary containing KAE, DROP, and XCACHE as inert env-gated features, with the identical XCACHE_CANON state and runtime fingerprint in both experiments; both experiments' manifests pin identical template bytes, token IDs, tokenizer hash, and binary tag (GLM-DROP's section 5.1 already freezes the same F1-K template). (ii) #27 REUSE, correctly named: the eligible near-full hit is the B0-FULL arm at TOPK=8 (byte-equal config to F1-K's b0), subject to retention of class-3 segments - ~1,440 prefills, ~$10-13 at spot avoided; the pilot's u-topk arm chooses k* from {4,3,2}+fallbacks, so k*=8 is NOT a possible u-topk outcome; for k*<8, unmasked u-topk reuses layer-0 Tier-B outputs (top-k is a subset of top-8; inputs at layer 0 are embeddings, identical) worth ~1/75 of a $10-13 arm ~ $0.13-0.17 before non-disk effects; masked arms hit only where a selected expert was previously computed at a byte-identical input - lower and empirical, reported from actual Tier-B intersection counters. (iii) REPLAY, scoped to retention: a full-programme replay at ~$35-45 (~0.25-0.30x of ~$149) is CONDITIONAL on a separately provisioned, complete, immutable XCACHE_DIVERGED=1 snapshot with no eviction and verified S3 coverage (adding ~1-2.2 TB over the ~518-531 GB Tier-A baseline, exceeding default NVMe free space, hence S3-resident and separately priced) AND on guard items always recomputing (they are never cached). Under the DEFAULT XCACHE_DIVERGED=0 store policy this projection is WITHDRAWN: replay cost is then priced from the retained-key inventory and measured hit counters, not assumed. The former 'spot-interruption repeats ~ free' claim is WITHDRAWN (completed items are already skipped by checkpoints; an interrupted spot instance loses unsynced NVMe data). Carrier re-construction re-dumps over frozen contexts (~$8-10/variant) remain conditional on retention of class-2 segments. (iv) ZERO value for different prompts/tokenizer/checkpoint/binary (cold by construction).",
   "rationale": "The cache monetizes repetition, but per GPT-5.6 findings 7/9/10 the replay projection must not contradict the default eviction policy, reuse must not be claimed across non-identical binaries, and the #27 accounting must name b0-full (not k*=8 u-topk) with corrected arithmetic.",
   "backing_ref": "docs/next/design/glm52-expert-cache.md sections 5.2/5.3; docs/next/design/glm52-expert-drop.md sections 3/5.1 (arms, pilot k* grid, frozen template); poc/gpt56-review/expert-cache/out/last-message.json findings 7/9/10",
   "owner": "designer-13",
   "load_bearing": false,
   "status": "open",
   "resolution_path": "Resolved by GLM-DROP's and any replay's metered ledgers plus Tier-B intersection and origin-split hit counters; the XCACHE_DIVERGED snapshot decision (provision + size + S3 line) is made explicitly at the F1-K freeze and recorded in manifest (A); the combined-binary precondition is checked by comparing both experiments' manifest engine-tags before any reuse is claimed.",
   "date": "2026-07-13"
  },
  {
   "id": "ASM-2310",
   "tag": "STIPULATED",
   "claim": "UPSTREAM COLIBRI CANDIDATE, STAGED (proposed PR shape only; no upstream action in this pass): the contribution is split into reviewable slices in the ANN/KaE etiquette (out-of-tree drafts vs pinned commit a78a06fc5acc4b0dc0f9ef03987c66b0559d1250, unit tests + ASan, zero deps): PR-1 Tier-B RECORD-ONLY plus deterministic recompute verification; PR-2 READ/SERVE with immutable record integrity (BLAKE3-128 authoritative + CRC fast-reject, ASM-2308) and crash/torn-tail tests; PR-3 TIER-A only after aggregation-order semantics (canonical accumulation) are settled with the maintainer; PR-4 S3 synchronization remains HARNESS-SIDE, never in-engine. INERTNESS REQUIREMENT when XCACHE is unset: zero allocation, zero hashing, zero I/O, zero threads, zero banner/config changes, pristine-vs-patched FULL-OUTPUT byte equality, AND a disassembly review of moe() (a false runtime branch can change register allocation/code generation even when never taken). The vendored single-file BLAKE3 is pinned by source hash and license file. Surface: XCACHE=<dir>, XCACHE_GB, XCACHE_VERIFY=N, XCACHE_TIERB, XCACHE_CANON, XCACHE_DIVERGED, XCACHE_RO; hit/miss/verify counters in STATS. Code-size figures are NONBINDING planning notes carrying no conformance weight. General value beyond this programme: post-hoc A/B on a frozen model, crash-resume of long sweeps, deterministic-replay regression testing, and the weight-hash manifest as an integrity checker.",
   "rationale": "PR-shape proposal only, per GPT-5.6 finding 11: the previous single-slice draft was too broad for one clean PR, the unset-path inertness needs codegen-level evidence, and the LOC estimate is demoted to nonbinding.",
   "backing_ref": "docs/next/design/glm52-expert-cache.md section 6; poc/glm52-probe/kae-patch-draft/README.md (etiquette precedent); poc/gpt56-review/expert-cache/out/last-message.json finding 11",
   "owner": "designer-13",
   "load_bearing": false,
   "status": "open",
   "resolution_path": "Resolved if/when the staged xcache patch drafts are built and independently code-reviewed like the KaE draft (PR-1 first); until then this is a sketch.",
   "date": "2026-07-13"
  },
  {
   "id": "ASM-2311",
   "tag": "STIPULATED",
   "claim": "F1-K INTEGRATION PROTOCOL + NO-NEGATIVE-VALUE GATE: XCACHE is the fourth cost lever on top of spot + pinning + R=3, and serving is enabled ONLY if it provably does not push spend UP. GATE G-XCACHE (frozen in manifest (A), evaluated at bring-up BEFORE campaign spend): a PAIRED cache-ON vs cache-OFF measurement on the same dev items under the FROZEN pinning policy, covering (i) populate-pass overhead (hashing, Tier-A writes), (ii) a full-hit pass, (iii) a partial-hit pass (smaller-miss-batch inefficiency included), (iv) verification recompute overhead, (v) S3 sync + fresh-instance restore time. DECISION (three-way, exhaustive, frozen in manifest (A); P_ON/P_OFF = the paired measurement's total metered campaign projections, both under the frozen pinning policy and CANON state; C = the standing $149 affordability ceiling): (1) SERVE iff P_ON <= P_OFF AND P_ON <= C; (2) else DISABLE iff P_OFF <= C - the exact measured trigger is P_ON > P_OFF (measured cache overhead >= measured savings on the frozen paired bring-up measurement) OR P_ON > C, and the exact disable action is running the ENTIRE campaign with XCACHE serving OFF, i.e. the uncached $149 model the ceiling was derived on, so cache overhead can never push spend past the ceiling (a disabled cache contributes zero campaign cost); the lever is reported landed-but-inert; (3) else HALT (P_OFF > C: even the uncached protocol fails the ceiling - a defect of the cost model, not of the cache): NO campaign arm is started, bring-up spend already incurred is charged to the ledger, and the ceiling is re-derived under the ASM-2205 protocol before any further spend (reverting to the pristine pre-CANON protocol if the halt precedes carrier construction and the pilot); XCACHE is never enabled to rescue affordability. IN-RUN TRIPWIRE: after SERVE, if the metered ledger at any per-item checkpoint shows cumulative measured cache overhead >= cumulative measured avoided recompute (separate counters per ASM-2306), serving is DISABLED for the remainder of the campaign (fail-safe to the uncached path; disable, never abort - hits are exact, so the measurement is untouched). NO pinning-interaction improvement is assumed (removing layers <= l* from the miss stream may remove exactly the hot bytes pinning was already serving and leave a colder residual stream); the interaction enters ONLY through the gate's paired measurement, and the assumed disk share d is a planning band (ASM-2302), not an input to the gate. ACCOUNTING: restore/sync COMPUTE is charged to the EC2 ledger; S3 storage/request costs sit OUTSIDE the EC2-only $149 ceiling scope on the storage/retention line (like the existing ASM-2205/2308-era lines) and are reported separately. THE $149 CEILING IS UNCHANGED and never depends on the lever landing. Manifest deltas frozen before spend: engine-tag, checkpoint + weight-manifest hashes, XCACHE config (GB, VERIFY N, tier policy, CANON state, DIVERGED state), per-arm hit/miss/verify counters split by origin, the cache-ON/OFF full-logit-vector hash pairs, the ASM-2306 exemptions verbatim (guard counters asserted zero), arm rotation unchanged (exactness makes arm order a cost variable, never a measurement variable), S3 segment sync on the per-item checkpoint cadence, GLM-DROP co-location under the logical-counter rule, and the shared-tier configuration per ASM-2325 (S3 Standard + Bloom index; DynamoDB only if its trigger fires). All cache faults fail closed to recompute; only a verify mismatch aborts (it impeaches the determinism premises, not just the cache).",
   "rationale": "GPT-5.6 finding 8: carrier-blind selection prevents outcome-driven choice of L but not cache overhead pushing spend up; the second review's blocker 2 showed the revision-2 fallback ('otherwise run cache-OFF') could itself exceed the ceiling (e.g. projected ON $151 / OFF $155), so the gate is now three-way with a provably non-negative fallback: DISABLE serving (the uncached model the ceiling was derived on) while OFF fits the ceiling, HALT before any campaign spend when it does not. Policy only - the spend projections live in ASM-2302.",
   "backing_ref": "docs/next/design/glm52-expert-cache.md section 7; docs/next/design/glm52-f1k-cost-reduction.md (ASM-2205); docs/next/design/glm52-shared-cache.md sections 4/6 (ceiling scope, shared-tier cost lines); poc/gpt56-review/expert-cache/out/last-message.json finding 8; poc/gpt56-review/expert-cache-r2/out/last-message.json blocker 2",
   "owner": "designer-13",
   "load_bearing": true,
   "status": "open",
   "resolution_path": "The gate's paired measurements and enable/disable decision are recorded in the F1-K run manifest at bring-up; the campaign ledger then resolves the realized cost either way; if the frozen L is L3 or the gate fails, the lever is reported landed-but-inert with the ceiling never having depended on it.",
   "date": "2026-07-13"
  },
  {
   "id": "ASM-2312",
   "tag": "STIPULATED",
   "claim": "TIER-C PREFIX-STATE CHECKPOINT (optional extension, NOT required for the ASM-2302 savings and NOT covered by the ASM-2307 contract): per (item, layer) store residual rows + KV for the maximal unmodified prefix, keyed by engine-tag, the component-hash chain up to that layer, and the token-id/x-hash prefix chain - the attention analogue of per-expert caching (attention's input is the whole prefix, so its input-hash is a prefix chain). It would additionally skip attention/dense work for fully-shared prefixes (inside the non-disk share) and is the natural decode-time geometry where per-token expert unions do NOT saturate; its few-MB values also exceed the DynamoDB item cap (ASM-2316), reinforcing the S3-only shared-tier rule for it. Deferred as an optimization note with no cost or validity claim.",
   "rationale": "Recorded so the dense/attention/router analogue has a concrete shape without inflating the present saving claims; kept separate from the Tier-B contract per the review's scope-tightening (finding 5).",
   "backing_ref": "docs/next/design/glm52-expert-cache.md section 4.4; docs/next/design/glm52-shared-cache.md section 2 (DynamoDB item cap via ASM-2316)",
   "owner": "designer-13",
   "load_bearing": false,
   "status": "open",
   "resolution_path": "Only picked up if a decode-time experiment (e.g. a future F1-A-class quality-invariant run wanting replay) needs it; otherwise remains a note.",
   "date": "2026-07-13"
  }
 ]
}
```

## 10. Review resolution map (GPT-5.6 xhigh, verdict FIX-FIRST → revision 2)

Every finding of `poc/gpt56-review/expert-cache/out/last-message.json`,
with disposition and location. No finding is declined.

| # | Finding (short) | Class | Disposition |
|---|---|---|---|
| 1 | Tier-A can return a stale aggregate (batch-union fp32 order) | Blocking | **RESOLVED** §2.2 + §3.1 + ASM-2303/2304: Tier-A permitted only under campaign-wide mandatory `XCACHE_CANON=1` (frozen pre-construction/pilot, engine-tagged, every arm/experiment/guard/cache-OFF comparison) AND an order-complete Tier-A key (ordered (id, W-hash, routing-weight-bits) sequence). ASM-2300 restated as conditional; cone language adopted. Spot checks not accepted as proof (§3.1). |
| 2 | "Every byte read is hashed" unspecified | Blocking | **RESOLVED** §2.2 + ASM-2303: domain-separated, length-delimited, fixed-endian serialization; full enumeration (gate/up/down + scales/zero-points/metadata/shapes/strides/biases; router tensors incl. correction biases/scaling; schema version; FP env; threading; libraries; arch fingerprint; CANON state); exactness stated conditional on BLAKE3 collision resistance + pinned environment (§3.2). |
| 3 | CRC32 cannot support the exactness bound | Blocking | **RESOLVED** §2.4 + ASM-2308: BLAKE3-128 record digest over (domain‖key‖len‖value) validated before serve; CRC demoted to fast-reject/torn-tail; full stored-key compare; conflicting duplicates rejected (ERR_XCACHE_CONFLICT); single-writer, fsync, immutable closed segments, index rebuild specified. (Revision 3: the SHARED block's residual CRC-as-integrity wording aligned — §11 blocker 3.) |
| 4 | Verification is a detector, not a proof; low-byte mod broken for arbitrary N | Should-fix | **RESOLVED** §3.3 + ASM-2305: restated as detection guard; u64 key-prefix mod arbitrary N recompute-on-hit; coverage per (tier × layer-band × origin); bring-up compares complete final logit vector bytes. (Revision 3: the selector is named accurately — a deterministic per-key verification subset, not hit-event sampling — §11 finding 4.) |
| 5 | Proof (b) overbroad; dense/attention claims mixed in | Should-fix | **RESOLVED** §4.2 + ASM-2307: scoped to direct same-layer self-only invalidation; downstream misses follow through the x-hash (contract (c)); "maximal" scoped to the pinned engine-tag; Tier-C kept as a separate uncovered sketch (§4.4, ASM-2312). |
| 6 | Saturation correction's categorical/numeric claims not established ("<1%" false; 75% disk share is decode-profiled) | Should-fix | **RESOLVED** §1.2–1.3 + ASM-2301/2302: frozen claim reduced to the accounting identity (saved = baseline − miss-union − overhead; partial hits save U_all−U_miss); "<1%" corrected to a 2–7% corner band; d=0.75 flagged as a pre-pinning decode figure; all numbers EXTRAPOLATION, resolved by measurement. (Revision 3: partial-hit saving restated as ≥ 0, may be zero — §11 blocker 1; the shared doc's own residual "<1%" scrubbed — §11 finding 4.) |
| 7 | Full-audit replay projection contradicts the default store policy; "interruption ≈ free" unsupported | Blocking | **RESOLVED** §5.3 + ASM-2308/2309: $35–45 replay made explicitly conditional on a separately provisioned complete `XCACHE_DIVERGED=1` immutable snapshot (+~1–2.2 TB, S3-resident, no eviction, verified coverage); withdrawn under the default policy — replay then priced from retained-key inventory + measured hit counters; the near-free-interruption claim withdrawn outright. |
| 8 | The unchanged $149 ceiling needs a no-negative-value gate; pinning "can only improve" false | Blocking | **RESOLVED** §7 + ASM-2311: GATE G-XCACHE — paired cache-ON/OFF bring-up measurement (populate, full-hit, partial-hit, verification, sync/restore) under the frozen pinning policy; serving enabled only if cache-ON ≤ cache-OFF within the affordability gate, else cache-OFF; restore/sync charged to the ledger; S3 outside the EC2-only cap; the pinning-improvement claim withdrawn. (Revision 3: the fallback made three-way and provably ceiling-safe — §11 blocker 2.) |
| 9 | Cross-experiment reuse requires the identical binary | Blocking | **RESOLVED** §5.2 + ASM-2309: one hash-pinned combined binary (KAE+DROP+XCACHE inert env-gated), identical CANON state and runtime fingerprint; both manifests pin identical template bytes, token IDs, tokenizer hash, binary tag; the semantic component-tag alternative explicitly declined as harder to prove safe. |
| 10 | GLM-DROP reuse names the wrong arm; arithmetic wrong | Should-fix | **RESOLVED** §5.3 + ASM-2309: rewritten around b0-full (TOPK=8); k*<8 u-topk layer-0 reuse re-priced at ~$0.13–0.17/arm; masked-arm reuse empirical from Tier-B intersections; counter renamed "logical demanded expert contributions / union loads" with physical reads / skipped matmuls / hits separate (§3.4); efficiency-measurement arms run XCACHE OFF. |
| 11 | Upstream slice too broad; unset-path codegen risk | Should-fix | **RESOLVED** §6 + ASM-2310: staged PR-1..PR-4 (record-only → serve+integrity → Tier-A after semantics → S3 harness-side); unset ⇒ zero alloc/hash/I/O/threads/banner + byte-equality + disassembly review; BLAKE3 pinned by source hash + license; LOC figures nonbinding. |
| 12 | ASM package internally inconsistent (invalid tags in the .md mirror; band-tag mismatch) | Blocking | **RESOLVED** §9 + companion JSON: the companion JSON is the single canonical source; §9 reproduces it verbatim (byte-identical, generated); no invalid tag remains anywhere; ASM-2300/2301/2307 are STIPULATED structural/contract cores with all numeric bands moved to ASM-2302 (EXTRAPOLATION, non-load-bearing), matching the adjudicated final tagging. |
| 13 | Other ASMs mix policy with projections | Should-fix | **RESOLVED** across the block: ASM-2304 stipulates the fail-closed policy with the bring-up result as a future separate MEASURED entry; ASM-2305 says detection guard, not proof; ASM-2308 is policy-only with numerics moved to ASM-2302; ASM-2310's LOC nonbinding; ASM-2306 asserts zero probes/hits/populates; ASM-2311 is now the stipulated gate/integration policy with spend numbers in ASM-2302. |

Shared-cache integration check: the XCACHE-SHARED recommendation
(ASM-2313..2326) is folded in as §5.4; the reconciliation clauses at the end
of §5.4 record that no contradiction remains between the two blocks
(b0-full supersedes the k*=8 phrasing; fleet-uniform engine-tag =
combined-binary + CANON; S3 Standard supersedes the IA note; per-worker
sizing resolves the NVMe pressure note).

## 11. Re-review resolution map (GPT-5.6 xhigh on revision 2 → revision 3)

Second review: `poc/gpt56-review/expert-cache-r2/out/last-message.json`
(verdict FIX-FIRST; 8 of 13 prior findings RESOLVED — none of those is
touched by this revision). Every residual item, with disposition and
location:

| # | Residual finding | Class | Disposition |
|---|---|---|---|
| 1 | ASM-2301 says a partial hit "never" saves zero — false when the miss-union equals the full demanded union | Blocking | **RESOLVED** §1.2 + §2.3 + ASM-2301: the corollary now reads `U_all − U_miss ≥ 0` **before overhead**, explicitly **may be zero** (exactly when every expert demanded by a hit row is also demanded by a miss row), and net savings after overhead can be negative — only the measured identity including overhead determines net savings. |
| 2 | $149 gate fallback unsound (canonical OFF could itself exceed the ceiling, e.g. ON $151 / OFF $155) | Blocking | **RESOLVED** §7 + ASM-2311: the gate is a three-way, exhaustive decision — (1) SERVE iff P_ON ≤ P_OFF ∧ P_ON ≤ C; (2) else DISABLE serving iff P_OFF ≤ C (exact measured trigger `P_ON > P_OFF ∨ P_ON > C`; exact action: whole campaign runs the uncached $149 model the ceiling was derived on, so cache overhead can never breach the ceiling); (3) else HALT before any campaign spend, charge bring-up spend to the ledger, re-derive the ceiling per ASM-2205 (pristine pre-CANON protocol if before construction/pilot). Plus an in-run overhead ≥ savings tripwire that disables serving mid-campaign (disable, never abort). |
| 3 | Shared block reintroduces CRC32 as an integrity closure (ASM-2323(b); shared §5 "CRC catches transport corruption") | Blocking | **RESOLVED** shared §5 + shared ASM-2323(b): BLAKE3-128-validated-before-serve (ASM-2308) is the shared-tier integrity closure everywhere; partial-write exclusion rests on atomic content-addressed S3 visibility (ASM-2324) **plus the BLAKE3-128 record digest**; CRC32 is demoted to a non-authoritative fast-reject/torn-tail hint (collision floor ~2⁻³² — no universal guarantee). Core §2.4/ASM-2308 unchanged; core and shared blocks are now consistent. |
| 4 | `u64(key) % N` is a per-key selector, not hit-event sampling; shared §1 retains revision-1's false "<1%" | Non-blocking | **RESOLVED** §3.3 + ASM-2305: renamed a **deterministic per-key verification subset** (~1/N of distinct keys; every served hit of a selected key verified; repeated hits of one key all-verified-or-all-skipped) with the limitation stated and bounded by the class-coverage requirement; shared §1 + shared ASM-2313 re-derived from the corrected ~2–7% corner band (first-touch ≈ 9–12 s each, ≈ $0.005–0.01 fleet-wide; the ≤ ~$1.5 ASM-2313 band unchanged). |

The r2 review's three additional non-blocking notes — the §5.3
"different prompt/tokenizer/checkpoint ⇒ cold" phrasing (component
addressing permits residual byte-identical reuse), S3 segment object naming
/ race-safe manifest merge, and the Standard-vs-IA ten-restore arithmetic —
are recorded here as open notes for the coordinator at freeze: each sits
inside a non-load-bearing EXTRAPOLATION entry (ASM-2309/2322) or a
harness-side mechanism spec (segment naming, decided in PR-2 code review per
ASM-2308/2310), and none carries a validity or ceiling claim.
