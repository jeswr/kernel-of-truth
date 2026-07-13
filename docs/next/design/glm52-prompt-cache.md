# PCACHE — prompt / KV-prefix caching for the GLM-5.2 colibri engine

> **RESEARCH + DESIGN ONLY — REVISION 2.** No code applied, no instance
> launched, no registry write, no git action, no model run, $0 spent in this
> pass. **No feasibility conclusion is stated.** This is the EXPLICITLY
> NON-BLOCKING prompt-caching research thread the maintainer requested on
> 2026-07-13: experiments do not wait on it. Revision 2 (designer-18,
> 2026-07-13) closes the GPT-5.6 xhigh review of revision 1
> (`poc/gpt56-review/prompt-cache/out/last-message.json`, verdict DEFECTIVE —
> repairable; resolution map at §11). The four repairs: (1) the stale
> "colibri does nothing of the kind" framing is corrected — current
> `coli serve` ALREADY does single-prefix prompt caching, and PR-P1 is now
> "adapt that existing implementation to the benchmark paths"; (2) the
> hit==recompute chain is fixed (DSA `Ic` state stored/keyed, the arm hash
> replaced by a canonical null-effect marker, the P-RESID cut-over off-by-one
> corrected) and the exactness claim is DOWNGRADED to "bit-identical within a
> pinned kernel/shape regime", gated accordingly; (3) the speedup model is
> rebuilt as additive calibrated coefficients with attention separated and no
> constant disk fraction; (4) the mid-run hot-swap claim (§8) is re-derived
> from the exactness actually guaranteed and is now CONDITIONAL, not
> unconditional. Parts the review upheld (llama.cpp characterization,
> MIT→Apache note, XCACHE/PCACHE non-duplication, KaE composition modulo the
> arm-key/DSA fixes) are kept.
> Owner: designer-14 (revision 1); revision-2 owner: designer-18.
> Companion ASM block (canonical source):
> `docs/next/design/asm-prompt-cache-2331-2345.json` — **populated range
> ASM-2331..2339 only**; ASM-2340..2345 were found already occupied by the
> GLM-DROP R2 block (`poc/glm52-probe/asm-glm-drop-r2-2340-2352.json`,
> referenced throughout `docs/next/design/glm52-expert-drop.md`) and are left
> untouched.
> Companions: `docs/next/design/glm52-expert-cache.md` (XCACHE, ASM-2300..2312
> — per-expert OUTPUT caching; THIS design is the complementary prompt/KV-PREFIX
> layer and reuses its keying discipline), `glm52-shared-cache.md`
> (ASM-2313..2330 shared tier), `glm52-followup-experiment.md` (F1-K),
> `glm52-expert-drop.md` (#27), `poc/glm52-probe/kae-patch-draft/` (KaE splice
> vs colibri base commit `a78a06fc5acc4b0dc0f9ef03987c66b0559d1250`).
> **Naming/citation rule:** the engine is referred to only as "colibri". The
> upstream repository URL embeds an author account name, so it is never
> written in this design or its ASM block; upstream-source facts are cited via
> the pinned review artifact
> `poc/gpt56-review/prompt-cache/out/last-message.json`, which records the
> resolvable URLs (README KV-persistence/slot sections; current `c/glm.c`).

## 0. BLUF

**What this is.** KV-prefix (prompt) caching reuses the attention Key/Value
state computed for a shared prompt PREFIX so the prefix is never re-prefilled.
For a benchmark where every item = (long fixed instructional context P) +
(short per-item suffix S), the per-item prefill drops from (P+S) rows to ~S
rows after the first item. It composes with XCACHE (which caches per-expert
outputs for the rows that ARE computed) and with the KaE splice (which acts
only on computed, gated rows).

**What colibri does today (corrected framing, §1).** Colibri ALREADY has
single-prefix prompt caching — in serve mode. Current `coli serve` compares
token histories, preserves the common KV prefix, processes only the unseen
suffix, persists KV across restarts (MLA `Lc`/`Rc` plus the DSA indexer keys
`Ic`), and exposes 16 isolated KV slots; its README states "no re-prefill"
[LIT-BACKED via the review-artifact source recheck, §1.1]. **The gap is
path-scoped, not engine-scoped:** the benchmark paths of record —
`run_score` / drafted `run_kae_score` / one-shot `generate()` — do not use
that machinery and re-prefill every item from position 0. Two consequences,
stated plainly: (a) **a large share of the benchmark win may be obtainable by
routing benchmark items through `coli serve`** as it exists today — with the
caveat that the one-shot experiment harness does not use serve, and moving the
harness onto the serve surface is itself a change that must pass the same
equality bring-up before any campaign use (§1.3); (b) **the genuinely
novel/missing parts** are (i) the aggressive CROSS-VARIANT PER-LAYER reuse —
reusing a prefix's KV even when a later expert/weight changes, or under a
different wider prompt — and (ii) multi-prefix generalization beyond serve's
per-slot single-history model. PR-P1 therefore ADAPTS colibri's existing
serve implementation into `SCORE`/`KAE_SCORE`; the per-layer generalization
comes after (§9).

**What exists to lift (§2).** First, colibri's own serve-mode implementation
(the primary adaptation source — same engine, same KV layout, already
persists `Lc`/`Rc`/`Ic`). Then llama.cpp (MIT, C/C++, closest external engine
shape): `--prompt-cache` session files (token ids verbatim + KV bytes; prefix
memcmp on restore; only the differing suffix is re-evaluated), server
`cache_prompt` (default enabled), `--cache-reuse N` (arbitrary N, default 0 =
disabled), slot save/restore endpoints, and the `cache_n`/`prompt_n`
observability split. vLLM APC (block-hash chain, full-blocks-only) and SGLang
RadixAttention (token-level radix tree + LRU) are the at-scale references.
No dedicated MoE-specific prefix-KV literature surfaced — prefix caching is
attention-side and orthogonal to expert routing (§2.3).

**Exactness, honestly scoped (§4).** Per-layer prefix-KV keyed by
(engine-tag ‖ weight-hash-below-L ‖ token-prefix chunk chain ‖
arm-effect-on-prefix marker) supports (a) reuse ACROSS a later expert/weight
change — earlier layers' prefix KV survives; cut over at the changed block ℓ̂
via a residual checkpoint AT OR BELOW ℓ̂ (block ℓ̂ itself is always rerun) —
and (b) reuse ACROSS different downstream prompts sharing the same leading
tokens. The cached state is the MLA latent (`Lc`/`Rc`) AND the DSA indexer
keys (`Ic`) — colibri's own persistence format is the precedent. **The
exactness claim is scoped:** a hit is bit-identical to recompute CONDITIONAL
on BLAKE3 collision resistance, P1/P2, `XCACHE_CANON=1` (MoE accumulation
order), AND a pinned kernel/shape regime (`PCACHE_SHAPEPIN`, §4.3) — because
colibri's quantized kernels are shape-dependent (batched vs single-row
forwards can select different int/fp32 kernel families and round differently
[LIT-BACKED via the review-artifact recheck]), CANON alone does NOT make
chunked prefill equal monolithic prefill. Within the pinned regime, equality
is verified at bring-up; OUTSIDE it, no byte-identity is claimed and PCACHE
does not serve (fail-closed `ERR_PCACHE_SHAPE`).

**The honest speedup model (§6).** Additive calibrated cost model — no
constant "disk fraction": C(P,S) = row-local compute (scales with rows
computed) + attention (suffix queries STILL attend over the full prefix:
hit-side pair count ≈ P·S + S²/2, not a share of row count; DSA needs its own
measured length-dependent term) + expert-union I/O (saturates in row count)
+ restore/write overhead. Consequences: at F1-K's short header the win is
~1.02–1.05× (the expert-union I/O floor dominates); at long prefixes the win
GROWS with P (the superseded constant-d model's 1/(d·U(S)) ceiling was an
artifact of holding d fixed while P→∞ — expert-union I/O saturates while row
compute and attention keep growing, so the disk share falls with shape). All
bands [EXTRAPOLATION, ASM-2336, non-load-bearing]; no closed-form asymptote
is claimed; G-PCACHE calibrates the four coefficients. Break-even is stated
as the incremental identity n*·(C_off−C_hit) ≥ populate/write overhead — not
as an average-cost shortcut (§6.2).

**Recommendation shape (no feasibility conclusion).** PR-P1: adapt colibri's
EXISTING serve prefix-reuse into `SCORE`/`KAE_SCORE` (mostly in-tree
adaptation, llama.cpp-session-file persistence as the secondary reference).
Then the campaign layer: P-KV (per-layer prefix KV chunks incl. `Ic`) +
optional P-RESID (residual checkpoints at declared weight-mutation frontier
layers) — under the XCACHE store/etiquette (append-only segments, BLAKE3-128
record digests, fail-closed ERR_PCACHE_*, no-negative-value gate G-PCACHE,
guard-set and I/O-instrument carve-outs). Whether it is WORTH enabling for a
given campaign is exactly what G-PCACHE measures; this document states no
conclusion.

---

## 1. What colibri does today — evidence (corrected)

### 1.1 Serve mode: prompt caching already exists

[STIPULATED, ASM-2332 item (0) — a design input per the engine's own
documentation, 2026; source: current upstream colibri `c/glm.c`
and README (KV persistence / isolated-slots sections), verified by the
2026-07-13 cross-vendor source recheck recorded in
`poc/gpt56-review/prompt-cache/out/last-message.json`; the resolvable URLs
live in that artifact — they are not written here because the repository path
embeds an author account name (header naming rule).]

Current `coli serve`:

- **compares token histories** between the incoming request and each slot's
  stored history;
- **preserves the common KV prefix** and **processes only the unseen
  suffix** — the README's phrase is "no re-prefill";
- **persists KV across restarts**; the persisted per-token state includes the
  MLA latent components `Lc`, `Rc` AND the DSA indexer keys `Ic`;
- exposes **16 isolated KV slots** (per-slot histories; no cross-slot reuse).

So the revision-1 claim "colibri does nothing of the kind" was WRONG (stale
framing), and the correct statement is: **colibri has single-prefix,
per-slot prompt caching on the serve surface; it does not have it on the
one-shot benchmark paths, and it has no cross-variant/per-layer or
multi-prefix generalization anywhere.**

### 1.2 The benchmark paths of record: no prefix reuse (upheld)

Evidence: (i) the verbatim glm.c CONTEXT LINES carried by the KaE patch
(`poc/glm52-probe/kae-patch-draft/kae-add-path.patch`, diff base
`index 1d74f78..90a4e15` at colibri commit
`a78a06fc5acc4b0dc0f9ef03987c66b0559d1250`) and (ii) the northstar engine
survey (`glm52-kernel-integration-northstar.md` §1.1). The review confirmed
these citations against the pinned patch context. A direct read of glm.c at
the pinned commit — including the serve slot machinery — closes the remaining
evidence limit at bring-up [STIPULATED: ASM-2331].

- **The forward plumbing already supports positional resume.**
  `attention(Model *m, Layer *l, int layer, float *x, int S, int pos_base)`
  (glm.c ≈ line 1267) and `layers_forward(Model *m, float *x, int S, int
  pos_base)` (≈ line 1510) take an absolute `pos_base`; decode uses it to
  extend a sequence one token at a time against the existing KV. `moe(...)`
  (≈ line 1274) is per-batch expert-union loading.
- **The benchmark scoring paths re-prefill everything, every item.**
  `run_score` (≈ line 1907) and the drafted `run_kae_score` call
  `kv_alloc(m, maxT)` once, then per item embed all T tokens and call
  `layers_forward(m, x, T, 0)` — one full prefill from position 0 per item.
  (Precision per the review: `kv_alloc` itself frees and reallocates the
  arrays; the scoring loop merely reuses the allocation because it calls
  `kv_alloc` once.) The KV content is overwritten each item; nothing is
  compared, saved, or restored on this path — no token-prefix check of any
  kind. The serve-mode caching of §1.1 is not reachable from here.
- **One-shot `generate()` (≈ line 2039 context) re-prefills the whole prompt
  per call** (`kv_alloc(m, np+n_new+g_draft+2)` then prompt prefill); within
  one generate call decode is incremental (normal, not the gap). Cross-call
  reuse exists only behind the serve surface.
- **KV is cheap and well-shaped for persistence.** MLA latent ≈ 576
  floats/token/layer (57× smaller than a naive 32,768/token/layer cache),
  ~182 KB/token persisted across ~78 layers (northstar §1.1, a design-record
  derivation; current upstream documentation reports the same ~182 KB/token
  order per the review recheck). Whether the 182 KB figure covers `Lc`/`Rc`
  only or includes `Ic` is confirmed at bring-up; the `Ic` bytes are
  engine-defined and measured then (ASM-2336 sizing note).

### 1.3 The near-term option the reframe exposes

Because serve-mode caching exists TODAY, there is a zero-new-mechanism option:
**route benchmark items through `coli serve`** (shared instructional prefix
held in a slot; per-item suffixes as follow-on requests). Stated clearly, with
the honest caveats: the one-shot experiment harness does not use serve; the
serve surface adds an HTTP/slot-policy layer to the path of record; scoring
(logit extraction) parity between `SCORE` and the serve surface would need to
be established; and ANY such harness change must pass the same §7 bring-up
equality (full-logit SHA, ON vs OFF) plus the §4.3 kernel/shape-regime check
before campaign use. This is recorded as an OPTION with no conclusion; PR-P1
(§9) — porting the same mechanism into `SCORE`/`KAE_SCORE` in-process — keeps
the harness surface unchanged and is the recommended first step instead.

**Conclusion of this section (structural, not a feasibility verdict):**
prefix-KV reuse exists in colibri on the serve surface; it is absent on the
benchmark paths the campaigns use; the mechanism to port is small because
`pos_base` resume exists AND a working in-engine implementation (serve's) can
be adapted: restore KV[0..P) (`Lc`/`Rc`/`Ic`) + run
`layers_forward(m, x_suffix, S, P)`.

---

## 2. Existing code to lift or adapt (the maintainer's "research first" ask)

All rows are STIPULATED design inputs grounded in vendor/project
documentation (ASM-2332) — web-verified 2026-07-13; account-free URLs
inline where the naming rule permits (see header); the colibri row is backed
by the review-artifact source recheck, and the llama.cpp rows by the
project's official documentation, 2026 (no account-bearing repository URLs
written here per the naming rule).

| System | Mechanism | License | Adaptability to colibri (single-sequence C) |
|---|---|---|---|
| **colibri `coli serve` (the engine itself)** | Token-history comparison per slot; common KV prefix preserved; only the unseen suffix processed ("no re-prefill"); KV persisted across restarts incl. MLA `Lc`/`Rc` + DSA `Ic`; 16 isolated slots. Source: current `c/glm.c` + README via the review artifact (header naming rule). | Apache-2.0 (same project) | **Primary.** Same engine, same KV layout, already handles the DSA state. PR-P1 = adapt this implementation to `SCORE`/`KAE_SCORE`/one-shot `generate()` (§9). What it lacks: cross-variant/per-layer keying, multi-prefix store, content-addressed persistence discipline. |
| **llama.cpp CLI** `--prompt-cache FNAME`, `--prompt-cache-all`, `--prompt-cache-ro` | Persist the session (token ids verbatim + KV state) to a file; on the next run, memcmp the stored token prefix against the new prompt and re-evaluate ONLY the differing suffix. `-ro` reads without updating. Not supported with some interactive modes. Source: llama.cpp official documentation (docs moved; behavior summarized in llama.cpp project discussion threads and a llama-cpp-python issue thread, read 2026-07-13 — no account-bearing repository URLs written here per the naming rule) | MIT | **High (secondary reference).** Same shape as the one-shot paths: single sequence, file-backed, prefix-memcmp, suffix-only re-prefill. Persistence-format template for PR-P1's session file (§9). MIT→Apache-2.0 (colibri) is compatible with attribution; the ~hundreds-of-LOC mechanism is re-implementable cleanly anyway. |
| **llama.cpp server** `cache_prompt` (default **enabled**), `--slot-prompt-similarity` (default 0.10), `--cache-reuse N` (min chunk size for KV reuse "via KV shifting" — "the common prefix does not have to be re-processed, only the suffix that differs"; **N is arbitrary, default 0 = disabled; no official threshold guidance**), `POST /slots/{id}?action=save\|restore` + `--slot-save-path`, timing readout `cache_n` (reused) vs `prompt_n` (newly processed) vs `predicted_n`. Official caveat: prompt-cache results are not guaranteed bit-for-bit identical across batch sizes. Source: the official llama.cpp server documentation (tools/server README, read 2026-07-13 — no account-bearing repository URL written here per the naming rule) | MIT | **High as a design reference** (multi-prefix store, similarity slot matching, the cache_n/prompt_n observability split we adopt in §7, and the batch-shape caveat we inherit in §4.3); the multi-slot server machinery itself is not needed for a single-sequence engine. Third-party field datapoint: ~4K-token slot ⇒ 219 MB file, save 211 ms / restore 87 ms; 5K-token chat re-prefill 9.9 s vs restore 1.4 s (<https://ai-muninn.com/en/blog/kv-cache-disk-restore-7x>, blog-grade). |
| **vLLM Automatic Prefix Caching** | PagedAttention KV blocks (16-token default), each block keyed by hash(parent-block hash ‖ block token ids ‖ extra keys: LoRA id, multimodal hash, cache salt); **full blocks only** are cacheable; sha256 default hasher (v0.11+, collision-risk note in docs); LRU eviction, last blocks freed first. <https://docs.vllm.ai/en/latest/design/prefix_caching.html> | Apache-2.0 | **Design reference only** (Python/GPU scheduler). Two ideas adopted: the parent-chained block hash (= our chunk chain, §4.1) and the full-blocks-only cachability rule. |
| **SGLang RadixAttention** | Radix tree over token sequences → KV tensor pages (one token/page); LRU leaf eviction; cache-aware scheduling; automatic reuse across calls/forks (few-shot prefixes, chat history, tree search); up to 5× throughput vs baselines; "no noticeable overhead even in the absence of cache hits" (always-on). <https://lmsys.org/blog/2024-01-17-sglang/> | Apache-2.0 | **Design reference only.** The radix structure is what PR-P2's multi-prefix store degenerates to at our scale (a handful of prefixes); the always-on/no-overhead finding motivates the no-negative-value gate rather than replacing it. |
| **MoE-specific prefix-KV caching** | Searched 2026-07-13: **no dedicated MoE prefix-KV-caching work surfaced.** Adjacent MoE literature is expert-side (offloading/caching/prefetch): fMoE fine-grained expert offloading <https://arxiv.org/html/2502.05370v1>, OD-MoE on-demand expert loading <https://arxiv.org/html/2512.03927v1>, speculative-decoding offload-hiding <https://arxiv.org/html/2508.21706v1>. | — | Prefix-KV caching is ATTENTION-side and orthogonal to expert routing — vLLM/SGLang apply it to MoE models unchanged. The MoE-specific content in THIS design is not the KV mechanism but the ECONOMICS (§6) and the expert-side complement (XCACHE). |

**Is there code to "lift" directly?** Yes — colibri's own serve
implementation is the primary source (adapt in-tree, same license, same
author-project conventions). The llama.cpp session-file mechanism is the
persistence-format template (token-ids-verbatim header + prefix memcmp +
suffix-only re-eval + `-ro` mode + cache_n/prompt_n counters); what we lift
from llama.cpp is the DESIGN, not the code.

---

## 3. How OpenAI and Anthropic do it at scale (the maintainer's explicit ask)

LIT-BACKED (ASM-2333); both pages fetched 2026-07-13; the OpenAI entry was
re-verified the same day by the cross-vendor review's official-doc recheck
(recorded in the review artifact), which corrected one stale point (below).

### 3.1 OpenAI — automatic for all, plus explicit controls on GPT-5.6+

Source: <https://developers.openai.com/api/docs/guides/prompt-caching>

- **Automatic**: enabled for all prompts ≥ **1024 tokens**. Below the
  minimum, `cached_tokens: 0`.
- **Correction vs revision 1 (review recheck 2026-07-13):** "automatic only;
  no opt-in API" is stale. Current GPT-5.6-generation models support
  **explicit cache breakpoints** and a **`prompt_cache_options`** surface, in
  addition to the automatic behavior; the automatic-only description applies
  to earlier models.
- **Exact-prefix keying**: "Cache hits are only possible for exact prefix
  matches within a prompt"; routing to cache-holding machines is by a hash of
  the prompt's first ~256 tokens, with an optional `prompt_cache_key`
  parameter to improve routing locality for callers sharing prefixes.
- **TTL/eviction**: older models ~5–10 min of inactivity (up to ~1 h);
  GPT-5.6+ retains ≥30 min. Org-scoped ("prompt caches are not shared between
  organizations").
- **Economics**: pre-GPT-5.6 cache writes are free, reads discounted;
  GPT-5.6+ writes cost 1.25× uncached input, reads bill at the cached rate.
- **Exactness posture**: "Prompt Caching does not change how the model
  generates output tokens" (it does NOT promise bitwise-identical sampling —
  weaker than what our campaign needs; we hold ourselves to byte-equality
  within a pinned regime, §4.3/§7).
- **Observability**: `usage.input_tokens_details.cached_tokens` and
  `cache_write_tokens`.

### 3.2 Anthropic — explicit breakpoints, ephemeral TTL, write/read pricing

Source: <https://platform.claude.com/docs/en/docs/build-with-claude/prompt-caching>

- **Explicit `cache_control` breakpoints** (up to 4 per request, plus an
  automatic top-level mode): the system hashes the entire prefix up to the
  breakpoint; on later requests it checks that prefix hash (with a ~20-block
  lookback for prior writes). Writes happen only at breakpoints.
- **Minimum cacheable prefix**: model-dependent, **512–4096 tokens**
  (e.g. 1024 for the Opus-4/Sonnet-4 tier; 2048–4096 for others); shorter
  prompts are silently processed uncached.
- **TTL/eviction**: ephemeral **5-minute TTL**, refreshed on read at no extra
  write cost; optional **1-hour TTL** at a higher write rate.
- **Economics (write-once/read-many)**: 5-min writes **1.25×** base input,
  1-h writes **2×**, reads **0.1×** — the pricing IS the design statement:
  a cache entry pays for itself after ~2 reads and is ~10× cheaper thereafter.
- **Exact-prefix invalidation, hierarchical**: tools → system → messages;
  a change at any level invalidates that level and everything after it;
  "100% identical prompt segments" required — a whitespace change breaks it.
- **Concurrency**: an entry becomes readable only when the first response
  begins; parallel identical requests can all miss and duplicate-write.
- **Observability**: `usage.cache_creation_input_tokens`,
  `usage.cache_read_input_tokens` (+ per-TTL breakdown), letting the caller
  audit every request's hit/miss economics.

### 3.3 Transferable design principles (adopted in §§4–7)

1. **Exact-prefix keying, never similarity** (both providers; llama.cpp's
   similarity is slot ROUTING, not validity) → our keys are content hashes of
   the exact token prefix + everything that feeds the bytes (§4.1).
2. **Prefix granularity via chained blocks** (OpenAI prefix hash; vLLM parent
   chain) → chunk-chained keys, longest-prefix reuse, full-chunks-only (§4.1).
3. **Provider min-length thresholds (OpenAI 1024; Anthropic 512–4096) are
   ELIGIBILITY/ECONOMICS rules at fleet scale** — cited as examples of store
   management, explicitly NOT as evidence for colibri's local break-even,
   which is derived from the incremental-cost identity in §6.2.
4. **TTL/eviction + write-vs-read asymmetry** → append-only segments with
   priority-then-LRU eviction inherited from XCACHE §2.4; populate passes are
   the "write price" G-PCACHE must charge honestly (§7).
5. **Cache-hit observability as a first-class output** (`cached_tokens`;
   `cache_n`/`prompt_n`) → per-item `pcache_hit_tokens`/`pcache_new_tokens`
   counters in the manifest (§7).
6. **Scoping/isolation keys** (org scoping; vLLM cache salts) → the
   engine-tag + arm-effect marker play this role (§4.1); nothing is shared
   across engine-tags.
7. **Explicit invalidation hierarchy** (Anthropic tools→system→messages) →
   our hierarchy is structural: engine-tag → weights-below-L → token prefix →
   arm-effect-on-prefix (§4.2).

---

## 4. The "aggressive" validity rule — per-layer keying and exactness

The maintainer's requirement, restated: *even if the model around a
particular expert changes, or a different prompt is given to the wider model —
if a given expert (layer) is given the same start of a prompt, it should
reuse the cache.* This section gives the rule that delivers both reuses
without ever serving a stale byte — with the exactness scope stated honestly
(§4.3).

### 4.1 Keys [STIPULATED: ASM-2334]

All hashes BLAKE3-256 with XCACHE's domain-separated, length-delimited,
little-endian preimage serialization (ASM-2303) and a leading
`PCACHE_SCHEMA_VERSION`. `engine-tag` is XCACHE's engine-tag verbatim
(binary bytes, IDOT_KERNEL, ebits/dbits, CPU/FP environment, threading knobs,
**XCACHE_CANON state**, byte order) **extended by the kernel/shape-regime pin
`PCACHE_SHAPEPIN` (§4.3): the pinned prefill row-block policy (fixed
row-chunk size for ALL prefills, cache-ON and cache-OFF, incl. the tail rule)
and the pinned kernel-family selection per (op, dtype, path)**. Chunk size B
(default 64 tokens; full-chunks-only, vLLM rule).

```
token-chunk chain:   h_0 = H("pfx" ‖ tok[0..B))
                     h_i = H(h_{i-1} ‖ tok[i·B..(i+1)·B))
                     (position is implicit: chunk i covers absolute positions
                      i·B..(i+1)·B, so RoPE/absolute-position effects are keyed)

W-below(L)   = H( embedding-hash ‖ block-hash[0] ‖ … ‖ block-hash[L-1] ‖ kvpath-hash[L] )
  block-hash[ℓ]  = H(every component hash of transformer block ℓ actually read:
                     attention q/kv projections, MLA down/up, rope + DSA-indexer
                     params, rmsnorm weights, router (incl. bias/scaling),
                     shared expert, EVERY routed expert W_e-hash — all from the
                     existing XCACHE per-checkpoint weight-hash manifest —
                     or the dense-FFN hashes for the 3 dense blocks)
  kvpath-hash[L] = H(the layer-L components on the token→cached-state path:
                     pre-attention rmsnorm, KV/MLA latent projection, rope
                     params, AND the layer-L DSA-INDEXER-PATH weights — the
                     indexer projections that produce Ic — because Ic is part
                     of the cached value below)

arm-effect-marker(L,i) =
    H("ARM0")                                 when the arm's injection provably
                                              has NO effect on any position
                                              < (i+1)·B at any layer < L or on
                                              the layer-L cached-state path —
                                              decision procedure: spans ∩
                                              [0,(i+1)·B) = ∅, OR every
                                              configured splice layer ≥ L
    H( KAE state ‖ carrier-file hash ‖ mode   otherwise (the injection DOES
       ‖ g ‖ splice-layer set ‖               touch this prefix below L: hash
       spans[0..(i+1)·B) verbatim )           the full config + spans verbatim)
    — FIX vs revision 1 (review finding 2, arm hash): revision 1 hashed the
    full config unconditionally and then claimed the digest was identical
    across baseline and spliced arms for empty prefix spans — but those
    preimages are NOT identical (different KAE/carrier/mode/gain/splice
    bytes). The canonical "no effect on this prefix below L" marker H("ARM0")
    makes the preimages identical EXACTLY when the semantic effect is
    identical (null). The null/full decision procedure is deterministic,
    part of the patch, and on the ASM-2334 code-review checklist. Fail-closed
    property preserved: every key contains either the marker or the full
    config; nothing is conditionally omitted without a canonical replacement.

P-KV key(L,i)   = H( engine-tag ‖ SCHEMA ‖ tier=PKV  ‖ layer L ‖ W-below(L)
                     ‖ h_i ‖ arm-effect-marker(L,i) )
    value       = the exact cached-state bytes the engine computed for
                  positions i·B..(i+1)·B at layer L: MLA latent Lc/Rc AND the
                  DSA indexer keys Ic (fp32 / engine-native, no truncation)
    — FIX vs revision 1 (review finding 2, DSA state): revision 1 stored only
    the MLA Lc/Rc bytes, but colibri's suffix DSA also READS the cached
    indexer keys Ic (its own disk format persists Ic, §1.1). P-KV therefore
    stores Ic alongside Lc/Rc and keys the indexer-path weights via
    kvpath-hash[L]. (The rejected alternative — recompute Ic from the restored
    residuals before serving — is noted for completeness: it would require
    P-RESID rows at EVERY layer, defeating P-KV; storing Ic matches colibri's
    own persistence precedent.)

P-RESID key(L,i)= H( engine-tag ‖ SCHEMA ‖ tier=PRES ‖ layer L ‖ W-full(<L)
                     ‖ h_i ‖ arm-effect-marker(L,i) )
    where W-full(<L) = H(embedding-hash ‖ block-hash[0..L-1]) — the residual
    stream at ENTRY to layer L depends on the complete blocks below, including
    their expert weights, but NOT on layer L itself
    value       = the residual-stream rows x(L, i·B..(i+1)·B), D×4 B each
```

Store discipline: XCACHE §2.4 verbatim — append-only segments under
`PCACHE_DIR/<engine-tag>/…`, BLAKE3-128 record digest authoritative before
serving, CRC32 fast-reject only, full 32-byte key compare, single writer per
segment, fsync on close, `ERR_PCACHE_CONFLICT` quarantine on duplicate keys
with conflicting digests. Shared tier: the same S3 content-addressed bucket +
Bloom existence index as XCACHE-SHARED (ASM-2313..2326) — P-KV values are
chunk-layer-sized (~11–182 KB + the Ic bytes) and fit the same segment
machinery.

### 4.2 Why this key is right (the dependency argument)

**Claim.** The cached state (Lc/Rc/Ic) at (layer L, position p) is a
deterministic function of exactly: (i) the token ids at positions 0..p;
(ii) the weights feeding layers 0..L−1 in full, plus the layer-L
cached-state-path weights (KV/MLA projection path AND DSA-indexer path);
(iii) the pinned execution environment INCLUDING the kernel/shape regime;
(iv) any activation-injection configuration (KaE) touching positions ≤ p at
layers < L (or layer L pre-KV). Nothing else. (The review upheld this
dependency form; the realization fixes are in §4.1/§4.3.)

**Proof sketch (induction over the causal (position, layer) DAG).**
x(0, p) = embed(tok[p]) — depends on tok[p] + embedding only. Assume x(ℓ, q)
for all q ≤ p depends only on tok[0..q], blocks 0..ℓ−1, and injections below
ℓ. Then block ℓ maps {x(ℓ, q)}_{q≤p} → x(ℓ+1, p) via attention (reads KV of
positions ≤ p at layer ℓ — causal mask; the DSA indexer's selection is itself
a function of the layer-ℓ indexer weights and the same inputs, given a
deterministic tie-break), moe/dense, rmsnorms, plus the KaE add if configured
at ℓ over gated positions ≤ p — all functions of block-ℓ weights and the
inductive inputs. So x(L, p) depends on tok[0..p] ‖ blocks 0..L−1 ‖
injections < L. (Lc,Rc,Ic)(L, p) = statepath_L(x(L, p)) adds exactly the
layer-L cached-state-path weights. ∎

The key of §4.1 hashes precisely this dependency set (plus the engine-tag
pinning (iii)), so — conditional on BLAKE3 collision resistance (≤ 2⁻¹²⁸) and
the determinism premises of §4.3, WITHIN the pinned kernel/shape regime —
a key match implies the cached bytes are bit-identical to what recompute
would produce in that regime. The same argument with the cached-state-path
weights deleted gives P-RESID's W-full(<L) key. This is XCACHE's contract (c)
("upstream changes are caught by the input hash", §4.3 there) applied to the
prefix state; staleness is structurally impossible — only (valid hit | miss).

**The two aggressive reuses, as corollaries (cut-over corrected):**

- **(a) A later weight change — with the change-CLASS distinction the review
  required.** Modify something in block ℓ̂ (TOPK/TOPP/mask config counts as
  "config actually read" inside block-hash[ℓ̂], same checklist rule as
  ASM-2303). Two classes:
  - **Class (i): the change is OFF the layer-ℓ̂ cached-state path** (an
    expert swap, router/bias change, shared-expert or other MLP-side change,
    post-attention components). Then kvpath-hash[ℓ̂] is unchanged, so
    W-below(L) is unchanged for every **L ≤ ℓ̂ INCLUSIVE** ⇒ prefix P-KV at
    layers 0..ℓ̂ all hit — the layer-ℓ̂ cached state itself is still valid.
  - **Class (ii): the change touches the layer-ℓ̂ cached-state path**
    (KV/MLA projection, pre-attention rmsnorm, rope params, DSA-indexer-path
    weights). Then kvpath-hash[ℓ̂] changes ⇒ P-KV at layer ℓ̂ misses too;
    hits are layers 0..ℓ̂−1 only.
  In BOTH classes, later layers' KV must be recomputed for the prefix rows,
  and — **off-by-one fix vs revision 1 (review finding 2)** — **block ℓ̂
  itself must always be rerun**: the valid resume point is the residual
  x(ℓ̂) at ENTRY to block ℓ̂, never x(ℓ̂+1), which already depends on the
  changed block. Cut-over: resume from the P-RESID checkpoint at the highest
  checkpointed layer **≤ ℓ̂** and forward the prefix rows through blocks
  ℓc..77 (cost ceiling: blocks ℓ̂..77 when a checkpoint sits exactly at ℓ̂).
  Without a P-RESID checkpoint at or below ℓ̂, fall back to a full prefix
  recompute (which repopulates). Checkpoint placement policy: AT each layer
  of the DECLARED mutation frontier — the KaE splice-layer candidates and the
  #27 mask layers are known from the frozen manifests before any run — plus
  layer 0 (free: it is the embedding output). P-RESID costs
  24 KB/token/checkpoint-layer; a handful of checkpoint layers ≈ 2–4× the
  total P-KV footprint [band, ASM-2336].
- **(b) A different downstream prompt with the same leading tokens.** The
  chunk chain h_i matches for every full chunk before the first differing
  token ⇒ reuse ⌊P_shared/B⌋ chunks at every layer; recompute the partial
  chunk + suffix. This is llama.cpp's prefix-memcmp and vLLM's parent-chain,
  content-addressed.
- **(c) Across KaE arms (the campaign case).** Benchmark templates put the
  instructional header BEFORE any gated stem token; when spans∩prefix = ∅ the
  arm-effect-marker is the canonical H("ARM0") for every arm — identical
  preimage, identical key — so b0's populate pass serves every spliced arm's
  prefix at ALL 78 layers; strictly more than XCACHE's layers ≤ ℓ* sharing
  for those rows, because the prefix rows are never recomputed at all. When a
  gated position IS in the prefix, arms get distinct entries (full-config
  hash), and additionally arms still share entries at layers L ≤ min splice
  layer (the marker is L-aware). (XCACHE §1.1's pos < p* column of the
  sharing diagram becomes a full skip.)

### 4.3 Exactness — the honest scope: two hazards, one pin, one downgrade [STIPULATED: ASM-2334/2335]

The target equality:

```
forward(prefix rows) ⧺ forward(suffix rows at pos_base=P over restored state)
    ==  forward(all P+S rows monolithically)          (byte-for-byte)
```

conditional on BLAKE3 collision resistance and on the pinned environment
satisfying:

- **P1/P2 (ASM-2304)**: per-row computations are pure and batch-composition
  independent AT THE ALGORITHM LEVEL. rmsnorm, q/kv/o projections, dense MLP,
  per-expert forwards involve no cross-row reduction. Attention output for a
  row reduces over POSITIONS in fixed position order — the same set and order
  whether the prefix KV was restored or computed in-batch, so it is
  composition-safe once the state BYTES are equal. The DSA sparse-attention
  indexer must have a deterministic tie-break (bring-up check item; same
  class as P1), and the suffix DSA reads the RESTORED `Ic` — byte-equal by
  the §4.1 value definition, closing the state-coverage gap.
- **Hazard 1 — MoE batch-union accumulation order (the XCACHE hazard):**
  upstream moe() accumulates each row's routed experts in batch-union order,
  which depends on which OTHER rows share the batch. **PCACHE serving
  requires `XCACHE_CANON=1`** (per-row ascending-expert-id accumulation, then
  shared expert — already mandated campaign-wide, frozen before the pilot,
  and inside the engine-tag). Without CANON, PCACHE must not serve
  (fail-closed `ERR_PCACHE_NONCANON`); there is no Tier-B-only fallback here
  because the cached object IS downstream of row-sums.
- **Hazard 2 — quantized-kernel SHAPE dependence (NEW in revision 2; the
  review's finding 3).** Revision 1 claimed batch-union order was "the ONLY
  composition hazard"; that claim is RETRACTED. Colibri's quantized kernels
  are shape-dependent: batched and single-row forwards can select different
  integer/fp32 kernel families and round differently (colibri documents this
  explicitly; llama.cpp likewise warns that prompt-cache results may not be
  bit-for-bit identical across batch sizes — both facts recorded in ASM-2332
  as stipulated vendor/project-doc design inputs). `XCACHE_CANON` covers ONLY the MoE accumulation order; it does
  NOT make a P-row populate forward bit-equal to the first P rows of a
  (P+S)-row monolithic forward if the two shapes select different kernels.
  **Resolution — pin, and downgrade what the pin cannot cover:**
  - **The pin (`PCACHE_SHAPEPIN=1`, in the engine-tag):** a campaign-wide
    fixed row-block prefill policy — EVERY prefill, cache-ON and cache-OFF,
    populate and verify, processes rows in fixed-size row-blocks (block size
    frozen, e.g. 64 rows, with a frozen tail rule), so the kernel-selection
    shape seen by every op is identical regardless of total prompt length —
    plus the pinned kernel-family selection per (op, dtype, path) and
    IDOT_KERNEL (already tag-pinned). Like CANON, SHAPEPIN is an engine
    discipline frozen before any campaign use and hashed into the engine-tag.
  - **The downgraded claim:** hit == recompute is asserted **bit-identical
    ONLY within the pinned kernel/shape regime** (CANON + SHAPEPIN + the
    engine-tag's kernel pins), and is VERIFIED there at bring-up (§7). No
    byte-identity is claimed across regimes (e.g. against an unpinned
    monolithic prefill, a different row-block size, or a different kernel
    family). If the engine cannot be run under SHAPEPIN, PCACHE serving is
    scoped to shapes where populate, hit-resume, and verify demonstrably used
    identical row-block shapes — and the §8 hot-swap is NOT licensed (see
    there).
  - **The gate:** `ERR_PCACHE_SHAPE` — fail-closed refusal to serve when a
    serving-path forward would use a shape/kernel outside the pinned regime.
- Equality is verified, not assumed, at bring-up (§7) — PER REGIME: full
  logit-vector SHA equality ON vs OFF per dev item, restored-vs-recomputed
  state byte equality (Lc/Rc AND Ic) on sampled (layer, chunk) pairs, and the
  chunked-vs-monolithic-under-SHAPEPIN prefill assertion. The in-run sampled
  re-prefill guard (`PCACHE_VERIFY=N`) is a DETECTION guard — it bounds
  undetected-corruption exposure and triggers quarantine; it is NOT the proof
  of equality (the proof is the bring-up verification + the structural key
  argument), and §8 draws the hot-swap consequence.

---

## 5. Minimal architecture for colibri

**Can colibri support it?** Structurally yes-shaped (no feasibility
conclusion) — and partially DEMONSTRATED by the engine itself: serve mode
already restores persisted Lc/Rc/Ic and continues from a common prefix
(§1.1). The port is (probe → load longest valid prefix state → prefill suffix
at `pos_base=P` → append new full chunks on completion).

Components (in dependency order):

1. **In-memory hot path (per process) — adapted from serve.** The trivial
   80% win for a benchmark run: keep the CURRENT prefix state resident
   between items; per item, compare token ids against the resident prefix
   (memcmp — no hashing needed in-process since the engine-tag/weights are
   constant within a process), truncate to the longest match, prefill only
   the remainder. This is exactly serve's token-history comparison relocated
   into the `SCORE`/`KAE_SCORE` loop (single slot, no HTTP). It converts an
   ordered benchmark stream with a shared header into first-item-pays
   semantics.
2. **On-disk persistent store (cross-process, cross-arm, cross-experiment).**
   The §4.1 content-addressed P-KV/P-RESID store under XCACHE's segment
   etiquette, `PCACHE_DIR`/`PCACHE_GB`-bounded, S3-mirrored via the
   XCACHE-SHARED tier. Value = Lc/Rc + Ic per (layer, chunk). This is what
   survives re-runs, arm changes, worker sharding, and weight mutations.
   (llama.cpp `--prompt-cache` semantics + colibri's own Lc/Rc/Ic disk
   format, generalized to per-layer content-addressed keys.)
3. **P-RESID checkpoints** at declared mutation-frontier layers (§4.2a;
   checkpoints AT frontier layers, resume from ≤ ℓ̂, block ℓ̂ always rerun).
4. **Composition with XCACHE** — strictly complementary, one shared
   discipline:
   - PCACHE removes PREFIX rows from the prefill entirely (attention + expert
     work at all layers). XCACHE then serves per-expert/per-row outputs for
     the SUFFIX rows across arms (its cone geometry unchanged — the suffix
     rows' x-hashes are identical across arms up to the divergence cone).
   - Both reuse the same per-checkpoint weight-hash manifest (ASM-2303's
     0.7 MB artifact), the same engine-tag (now incl. SHAPEPIN), the same
     CANON requirement, the same segment/record format, the same S3+Bloom
     shared tier.
   - **XCACHE §4.4's Tier-C sketch IS this design**, developed: P-KV/P-RESID
     supersedes that "deferred optimization note" (its key sketch —
     H(engine-tag ‖ component hashes up to ℓ ‖ token-id prefix ‖ per-layer
     prefix x-hash chain) — is refined into §4.1's W-below/W-full split and
     chunk chain; its observation that these values exceed the DynamoDB item
     cap carries over: the shared tier is S3-only).
   - Probe order per item: PCACHE first (sets the computed row set), then
     XCACHE per remaining row. Counters are reported separately.
5. **Composition with the KaE splice.** The splice acts on computed rows via
   `kae_apply_add(…, pos_base, …)`; a restored prefix simply means the splice
   sees only suffix rows — correct by construction when spans∩prefix = ∅, and
   handled by the arm-effect-marker keying when not (§4.1). `kae_bind_spans`
   per-item binding is unaffected. (The review upheld this composition
   conditional on the arm-key and DSA-state fixes, which §4.1 makes.)

Sizing bands [EXTRAPOLATION, ASM-2336, non-load-bearing]: ~182 KB/token of
MLA-latent P-KV per (prefix × weight-config × arm-effect-config), PLUS the
`Ic` indexer-key bytes (engine-defined; whether the northstar's 182 KB/token
figure already includes them is confirmed at bring-up); a 2k-token shared
instructional prefix ≈ 373 MB + Ic; a 60-subject few-shot benchmark at 2k
tokens/subject ≈ 22 GB — comfortably inside the i4i NVMe budget beside
XCACHE's ~52 GB/worker Tier-A share. F1-K's own ~30–60-token shared header
≈ 5–11 MB — negligible either way.

---

## 6. The benchmark speedup model, honestly (rebuilt in revision 2)

### 6.1 The additive model [EXTRAPOLATION: ASM-2336, non-load-bearing]

Revision 1's model — a constant disk fraction d≈0.75 with attention folded
into the row-linear term and an asymptote 1/(d·U(S)) as P→∞ — is
**superseded** (review finding 4): holding d constant while P→∞ is invalid
(expert-union I/O saturates while row compute and attention keep growing, so
the disk share falls with shape), and attention must carry its own term
because suffix queries still attend over the whole prefix.

The replacement is additive with FOUR CALIBRATED COEFFICIENTS (α row-local
compute per token, β attention per attended position-pair, γ expert-union
I/O per layer-union unit, ρ restore + ω write per prefix token), all measured
by G-PCACHE under the frozen pinning policy — none assumed:

```
C_off(P,S)  =  α·(P+S)  +  β·A_off(P+S)      +  γ'·U(P+S)
C_hit(P,S)  =  α·S      +  β·A_hit(P,S)      +  γ'·U(S)      +  ρ·P
C_pop(P,S)  =  C_off(P,S)                    +  ω·P            (first pass)

A_off(T)   ≈ T²/2                 (dense causal)   or the DSA-limited form
A_hit(P,S) ≈ P·S + S²/2           (dense causal)   or the DSA-limited form
             — the ATTENTION term is separated: suffix queries attend over
             the full P+S context; the hit/off attention ratio is
             (P·S + S²/2)/((P+S)²/2), NOT S/(P+S)
U(n)       = 1 − (1−k/E)^n, k=8 of E=256 (uniform-routing union model;
             real routing is skewed/correlated — same caveat as ASM-2302)
γ'         = γ·78 layers; U enters per forward pass; under SHAPEPIN row-block
             chunking, cross-chunk expert re-reads are a page-cache question —
             physical reads are MEASURED, never inferred (ASM-2301 rule)
```

**DSA caveat (its own term, per the review):** colibri's DSA sparse attention
bounds the attended set for long context, so the dense-quadratic A(·) forms
are an UPPER BOUND on attention growth; the illustrative table below uses a
capped stand-in A(T) ≈ Σ_q min(q, w_eff) with w_eff = 512 — a placeholder,
NOT a measured DSA profile. The DSA term must be measured as its own
length-dependent coefficient at calibration; the dense variant would make the
large-P speedups LARGER (more OFF-side work avoided), so the cap is the
conservative choice for the table.

**No closed-form asymptote is claimed.** As P grows at fixed S: γ'·U(P+S)
saturates at γ', while α·P and β·A grow without bound — so the OFF cost is
eventually compute/attention-dominated, the effective "disk share" d(P,S)
falls, and the cached win GROWS with P (the direction revision 1's constant-d
ceiling got wrong). How fast it grows is exactly the α:β:γ calibration
question.

**Illustrative bands** under two anchor scenarios for the cost shares at the
reference shape T=256 (chosen to bracket ASM-2302's decode-profiled
disk-share caveat: scenario A = 20% row / 5% attention / 75% I/O; scenario
B = 7.5% / 2.5% / 90%), w_eff = 512, ρ from the §6.2 restore band — every
number [EXTRAPOLATION, ASM-2336, non-load-bearing, resolution = G-PCACHE]:

| Shape | speedup C_off/C_hit (scenario B – scenario A) | provider/GPU intuition ≈(P+S)/S |
|---|---|---|
| F1-K header: P≈45, S≈155 | **≈1.02–1.05×** | 1.3× |
| P=1024, S=256 | **≈1.6–2.2×** | 5× |
| P=1024, S=64 | **≈1.9–3.0×** | 17× |
| P=4096, S=128 | **≈3.8–7.6×** | 33× |
| P=2048, S=32 | **≈3.7–7.2×** | 65× |

**The honest headlines:**

1. **Short shared prefixes are floored by expert-union I/O.** Even a modest
   suffix batch demands most experts per layer (U(64) ≈ 87%, U(155) ≈ 99%),
   so for F1-K's own short header the win is a ~2–5% band — PCACHE's value
   concentrates on benchmarks with LONG shared instructional/few-shot
   contexts (the maintainer's stated case).
2. **Long prefixes benefit MORE than revision 1 said, not less** — because
   the I/O term saturates while the avoided row/attention work keeps growing
   with P. But the large-P cells are the most scenario-sensitive (they lean
   on the uncalibrated α and the placeholder DSA term), and they remain below
   the provider-style (P+S)/S intuition at these shapes.
3. **The second-order effects still apply**: a smaller working set per item
   leaves more RAM/page-cache/pin budget for the hot suffix union, and
   repeated same-prefix items stop evicting it. Physical reads are measured,
   never inferred (ASM-2301's rule inherited).

### 6.2 Break-even — the incremental identity (corrected)

Revision 1's break-even used average whole-prefill time per token; the review
rejected that shortcut. The correct statement, per prefix, over its lifetime:

```
net(P,S,n) = n · ΔC(P,S) − ω·P − c_store        where ΔC = C_off − C_hit
break-even reuse count  n* = (ω·P + c_store) / ΔC(P,S)
break-even prefix size: smallest P with ΔC(P,S) > 0, i.e. the saved
row/attention/I/O work must exceed the restore overhead ρ·P
```

Bands for the components [EXTRAPOLATION, ASM-2336]: restore ρ ≈ read
182 KB/token at NVMe ~3.3 GB/s (~55 µs/token) + BLAKE3 digest (~50 µs/token)
≈ ~0.1 ms/token; first-write ω is the same order (NVMe write + fsync
amortized); recomputing a prefix token costs ~0.3–0.7 s at the planning
band — a ~10³–10⁴× ratio. So the BANDS say n* ≪ 1 for any P ≥ one chunk
(the first reuse more than repays the populate write) and the ΔC>0 prefix
threshold is O(1) tokens — but this is now stated as a band over the
calibrated identity, not as an established fact; G-PCACHE measures ΔC, ω, ρ
directly, including the populate pass (§7).

Provider minimums — OpenAI 1024 (§3.1), Anthropic 512–4096 per model (§3.2) —
are cited ONLY as examples of fleet-scale eligibility/economics; they are NOT
evidence about colibri's local break-even. (Revision 1's "llama.cpp ~256-token
reuse-chunk guidance" is REMOVED: official llama.cpp exposes arbitrary
`--cache-reuse N`, default 0 = disabled, and specifies no 256-token
threshold — review finding 4.) Recommended default `PCACHE_MIN=64` tokens
(= one chunk) [STIPULATED: ASM-2336's threshold clause] purely to bound store
churn; `PCACHE_GB` bounds the footprint; eviction priority-then-LRU with the
shared instructional prefixes of the ACTIVE campaign in the top class.

### 6.3 What would make the model wrong (resolution path)

Measured unions below the uniform model (routing skew) ⇒ bigger I/O-term
wins; measured α/β shares lower ⇒ smaller large-P wins; the measured DSA
attention profile ⇒ moves the large-P cells either way; page-cache effects
across SHAPEPIN row-blocks ⇒ either direction. All are exactly what the
G-PCACHE paired measurement (§7) replaces the bands with; none is assumed.

---

## 7. Correctness gate, carve-outs, and the no-negative-value guard

Inherits XCACHE §§3.3–3.4 and §7 wholesale; deltas only [STIPULATED: ASM-2337]:

- **Fail-closed errors**: `ERR_PCACHE_NONCANON` (serving attempted without
  CANON in the engine-tag), `ERR_PCACHE_SHAPE` (a serving-path forward would
  use a shape/kernel outside the pinned SHAPEPIN regime — NEW in revision 2),
  `ERR_PCACHE_MISMATCH` (sampled verify recompute differs ⇒ abort + quarantine
  store + §8 item-void rule), `ERR_PCACHE_CONFLICT` (duplicate key,
  conflicting digest). Token mismatch / digest failure / weight-hash or
  engine-tag miss are NOT errors — they are misses ⇒ full recompute.
- **Bring-up equality (before any served hit; PER kernel/shape regime — a
  regime change is an engine-tag change and colds the store):** (i) one full
  dev item per arm scored PCACHE-ON vs OFF — SHA-256 of the complete final
  logit vector must match; (ii) restored-vs-recomputed state byte equality —
  Lc/Rc AND Ic — on ≥ one early, one mid, one late layer × ≥ 2 chunks;
  (iii) the chunked-vs-monolithic prefill equality of §4.3 asserted directly
  on a dev prefix UNDER SHAPEPIN (both sides run in the pinned row-block
  policy); (iv) the DSA deterministic-tie-break assertion (§4.3 P1/P2 item).
- **In-run detection guard**: `PCACHE_VERIFY=N` (default 256) — on a served
  chunk whose key's leading u64 ≡ 0 (mod N), recompute the chunk's state and
  memcmp (Lc/Rc/Ic). Coverage counters per (tier × layer-band × origin
  local/S3); any served class with zero verifies by run end is voided in cost
  accounting (ASM-2305's rule). **Honest scope (review finding 6): this is a
  DETECTION guard, not proof** — it bounds exposure and cannot certify
  earlier unsampled hits; the equality license comes from the bring-up
  verification plus the structural key argument, and a mismatch triggers the
  §8 retroactive item-void rule, not just an abort.
- **Instrument carve-outs (verbatim XCACHE §3.4 policy):** the off-concept
  guard set runs PCACHE fully OFF (probe/hit/populate counters asserted
  ZERO per guard item in the manifest — serving guard prefills from cache
  would weaken the SHA-identity check's bite); F1-A/F1-B routing arms and any
  arm whose ENDPOINT or gate is expert-I/O run PCACHE OFF (a prefix cache
  changes demanded unions, i.e. perturbs that instrument — e.g. #27's ±5%
  matched-loads gate); logical expert-load counters remain defined over
  COMPUTED rows and are reported beside separate pcache counters. Carve-out
  flags live in the frozen item manifest, fleet-global (ASM-2323 clause (e)).
- **GATE G-PCACHE — no-negative-value [mirrors G-XCACHE / ASM-2311]:**
  paired PCACHE-ON/OFF measurement on dev items under the frozen pinning
  policy, covering populate-pass overhead (the ω·P write price, charged
  honestly), full-hit, partial-hit, verify overhead, S3 sync/restore — and
  yielding the α/β/γ/ρ/ω calibration that replaces every §6 band. Serving
  enabled only if metered campaign projection ON ≤ OFF within the standing
  affordability gate; else the lever lands inert.
  **The $149 ceiling is unchanged and never depends on PCACHE.**
- **Observability (the §3.3 principle):** per item, the manifest records
  `pcache_hit_tokens` / `pcache_new_tokens` / `pcache_populate_tokens` /
  verify counts (the cache_n/prompt_n split), per arm — the audit sees
  exactly what was served.

---

## 8. Mid-experiment introduction — re-derived from the guaranteed exactness

Revision 1 asserted the hot-swap unconditionally from hit==recompute; the
review found the exactness premises failing, so the claim is RE-DERIVED here
from what §4.3 actually guarantees. [STIPULATED: ASM-2338]

**What is licensed, and by what.** WITHIN one frozen binary whose engine-tag
pins CANON + SHAPEPIN + the kernel families, and AFTER the §7 bring-up
equality (i)–(iv) has passed for that regime, a served hit is byte-equal to
recompute in that regime — so flipping `PCACHE=1` at an item boundary changes
when bytes are recomputed vs read, never what any logit is. UNDER EXACTLY
THOSE CONDITIONS, PCACHE is a pure cost lever (the same "arm order is a cost
variable, never a measurement variable" clause as XCACHE ASM-2311), and
mid-run introduction is safe. If ANY condition fails — no SHAPEPIN, bring-up
not run for the active regime, CANON off — the byte-identity claim is not
available, PCACHE must not serve (§7 fail-closed errors), and mid-run
adoption is NOT licensed: the flip would be a measurement-surface change and
may only happen at a campaign/stratum boundary with the change registered.

Procedure:

1. **The binary must not change mid-run.** The PCACHE code must be IN the
   campaign's combined binary from freeze, env-gated OFF (`PCACHE` unset) —
   the same way KAE/XCACHE ship inert. **Changing to a new binary mid-run is
   a NEW BINARY/CONFIGURATION STRATUM, not merely a costed cache flip**
   (review finding 6): new engine-tag, both stores cold, inertness + bring-up
   reproven, old-vs-new-binary full-logit SHA equality on dev items recorded,
   AND the run's items are stratified by binary in analysis — the coordinator
   registers it as a configuration-stratum change, never silently.
2. **Inertness proof at freeze (KaE/XCACHE etiquette):** PCACHE unset ⇒ zero
   allocation, zero hashing, zero I/O, zero threads; pristine-vs-patched
   FULL-OUTPUT byte equality on dev items; disassembly review of the touched
   functions (`run_score`/`run_kae_score`/`generate` call sites) — a false
   branch can perturb codegen even when never taken (ASM-2310's rule).
3. **At flip time (any item boundary):** run the §7 bring-up equality
   (i)–(iv) and G-PCACHE on dev items FOR THE ACTIVE REGIME; only then enable
   serving. Populate-first is automatic (first pass over each prefix writes,
   later passes read).
4. **Detection-guard honesty + the retroactive rule.** The in-run
   `PCACHE_VERIFY` sampling is detection, not proof (§7). If a sampled verify
   EVER mismatches: abort, quarantine the store, AND void every item that
   consumed a served hit since the last clean full-equality check — those
   items are re-run PCACHE-OFF before any use. This makes the failure mode
   costly but never silent, and it is what keeps the hot-swap honest under a
   detection (rather than proof) guard.
5. **Provenance:** every item's manifest row records the PCACHE state and
   counters, so the run-log shows exactly where the flip happened; the audit
   verifies the guard/instrument carve-out zeros straddling the flip.
6. **Rollback is free:** unset `PCACHE` — misses everywhere, recompute, no
   state to unwind (eviction/loss never affects correctness, only coverage).

---

## 9. The upstream colibri contribution slice (reframed)

Colibri is Apache-2.0, single-author, single-C-file, no plugin architecture
(northstar §1.1) — contributions must be small, inert-by-default,
self-contained (the KaE `kae.h` + `test_kae.c` and XCACHE ASM-2310 etiquette).
Staged shape [STIPULATED: ASM-2339; no upstream action in this pass]:

- **PR-P1 — bring serve's existing prompt cache to the one-shot paths.**
  REFRAMED per the review: this is an ADAPTATION of colibri's own serve-mode
  mechanism (token-history compare; common-prefix preservation; suffix-only
  prefill; Lc/Rc/Ic persistence), not a novel port of llama.cpp. `SCORE`/
  `KAE_SCORE`/one-shot `generate()` gain: `PCACHE=<file>` env — load the
  session state, compare stored token ids against the current prompt
  (verbatim memcmp, serve's rule), restore the matching prefix state
  (Lc/Rc/Ic), prefill only the suffix at `pos_base=n_match`, save on exit;
  `PCACHE_RO=1` reads without updating. Session file: the llama.cpp-shaped
  envelope (magic + format version + model fingerprint (config hash +
  ebits/dbits + IDOT_KERNEL) + token ids verbatim + per-layer state bytes +
  whole-file checksum) OR a thin reuse of serve's own persistence format —
  bring-up decides which is smaller. No new deps (no BLAKE3 at this stage).
  Self-contained `pcache.h` (static inline, fail-safe: any mismatch/
  short-read ⇒ warn + full prefill, never crash) + `test_pcache.c` + the
  `cache_n/prompt_n` fields added to the score progress line. Inert unless
  `PCACHE` is set; pristine-vs-patched byte-equality is the review artifact.
  Nonbinding size note: ~200–300 LOC, lower if serve's functions are directly
  callable.
- **PR-P2 — multi-prefix store + longest-prefix match.** Directory store,
  chunked entries, longest-chain reuse across DIFFERENT prompts (the §4.1
  chunk chain minus the per-layer weight keys — upstream runs one fixed
  checkpoint, so W-below collapses into the model fingerprint). This
  generalizes serve's per-slot single-history model (16 isolated slots, no
  cross-slot reuse) and is where the "different prompt, same start" reuse
  lands for ordinary users (`coli chat` system prompts, benchmark harnesses,
  the serve slots themselves).
- **PR-P3 — per-layer W-below keying + P-RESID cut-over (campaign layer;
  offered upstream as optional).** The genuinely novel part (§0). Valuable
  only where weights mutate mid-model (expert swaps/masks/steering research)
  — precisely our campaign; reuses the XCACHE weight-hash manifest and
  vendored BLAKE3 if XCACHE's PR series lands, else stays out-of-tree
  harness-side.
- **Why upstream plausibly wants PR-P1/P2** (stated as motivation, not a
  conclusion): upstream already judged prompt caching worth building — serve
  mode has it; PR-P1 extends its own mechanism to its own one-shot surfaces.
  llama.cpp ships the equivalent default-on server-side with visible user
  demand (§2 links); colibri's ~0.05–1.8 tok/s disk-bound regime makes
  re-prefill of a long system prompt one of its most user-visible costs, and
  MLA's small KV makes session files unusually cheap (~182 KB/token + Ic vs
  llama.cpp-class models' ~MB/token).

---

## 10. Self-check (governance)

- **Colibri reframe done (review finding 1):** §1.1 states plainly that
  current `coli serve` already implements single-prefix prompt caching
  (token-history compare, suffix-only processing, Lc/Rc/Ic persistence, 16
  slots, "no re-prefill"); §1.3 states the serve-routing option with its
  harness caveat; PR-P1 (§9) adapts the existing serve implementation; the
  novelty claim is narrowed to cross-variant per-layer reuse + multi-prefix
  generalization. "Colibri does nothing of the kind" is retracted.
- **Exactness sub-fixes (review findings 2–3):** (a) DSA state — P-KV values
  now store `Ic` beside `Lc`/`Rc` and kvpath-hash[L] keys the layer-L
  indexer-path weights (§4.1); (b) arm hash — replaced by the canonical
  H("ARM0") null-effect marker with a deterministic decision procedure, so
  preimages are identical exactly when effects are identical (§4.1); (c)
  kernel/shape dependence — `PCACHE_SHAPEPIN` pin in the engine-tag + the
  exactness claim DOWNGRADED to bit-identical-within-the-pinned-regime, gated
  by `ERR_PCACHE_SHAPE` and per-regime bring-up (§4.3). Also fixed from the
  review's finding 2: the P-RESID cut-over off-by-one (checkpoint ≤ ℓ̂, block
  ℓ̂ always rerun) and the block-ℓ̂ change-class distinction (§4.2a).
- **Speedup model additive (review finding 4):** four calibrated
  coefficients (row α, attention β with A_hit ≈ P·S+S²/2 separated and a DSA
  term flagged for measurement, expert-I/O γ, restore/write ρ/ω); no constant
  d; no closed-form asymptote claimed; break-even via the incremental
  identity n*·ΔC ≥ ω·P + store cost incl. populate cost and reuse count; the
  fabricated llama.cpp 256-token guidance removed; provider minimums scoped
  to eligibility/economics examples (§6).
- **Hot-swap re-derived (review finding 6):** §8 licenses mid-run
  introduction ONLY under frozen-binary + CANON + SHAPEPIN + passed
  per-regime bring-up; otherwise adoption only at a stratum boundary; a
  mid-run binary change is a configuration STRATUM, never a costed flip;
  `PCACHE_VERIFY` acknowledged as detection-not-proof with a retroactive
  item-void rule.
- **Upheld parts kept (review finding 5):** llama.cpp characterization
  (plus its across-batch-size non-determinism caveat now cited), MIT→Apache
  license note, XCACHE/PCACHE non-duplication, KaE composition under the
  fixed arm key + DSA state. ASM-2333's OpenAI staleness corrected (explicit
  GPT-5.6 breakpoints + `prompt_cache_options`).
- **Tags:** only MEASURED/LIT-BACKED/STIPULATED/EXTRAPOLATION (no MEASURED
  claims are made in this pass — nothing was run). Provider-doc facts
  LIT-BACKED (ASM-2333) with URLs inline; the existing-code survey
  (ASM-2332) is a STIPULATED design input grounded in vendor/project
  documentation, 2026, with account-free URLs inline where the naming rule
  permits; the colibri upstream facts cite the pinned review artifact, which
  records the resolvable URLs (the repository path embeds an author account
  name — see header). Structural claims STIPULATED with rationale + resolution paths;
  projections EXTRAPOLATION, load_bearing:false. Owners: designer-14 (r1
  entries), designer-18 (this revision) — both in the closed roster. No
  GitHub handles or account names anywhere; the engine is referred to only
  as "colibri". No registry write, no git action, no model run, $0. ASM
  range: 2331..2339 populated; 2340..2345 found occupied (GLM-DROP R2) and
  left untouched.

---

## 11. Resolution map — GPT-5.6 xhigh review of revision 1 (verdict DEFECTIVE, repairable)

Review artifact: `poc/gpt56-review/prompt-cache/out/last-message.json`.

| # | Finding | Class | Resolution in this revision |
|---|---|---|---|
| 1 | Stale colibri framing: current `coli serve` already does prompt caching (token-history compare, common-prefix KV preservation, suffix-only processing, Lc/Rc/Ic persistence across restarts, 16 isolated slots, "no re-prefill"); "colibri does nothing of the kind" and the PR-P1 novelty framing wrong; `kv_alloc` wording imprecise | Major | **RESOLVED** §0/§1.1/§1.3/§2 row 1/§9: serve-mode caching stated as existing fact [ASM-2332(0), STIPULATED design input per the engine's own documentation, 2026, via review-artifact URLs per naming rule]; benchmark win may be largely obtainable via serve routing (option recorded with harness caveat); PR-P1 reframed as adapting serve's implementation; novelty narrowed to per-layer cross-variant reuse + multi-prefix; `kv_alloc` frees-and-reallocates precision adopted (§1.2). |
| 2a | DSA state omitted: P-KV stored only MLA Lc/Rc; suffix DSA reads cached `Ic`; colibri's own disk format persists `Ic` | Blocking (exactness) | **RESOLVED** §4.1: P-KV value = Lc/Rc **+ Ic**; kvpath-hash[L] extended with the layer-L DSA-indexer-path weights; recompute-Ic alternative noted and rejected; bring-up equality checks Ic bytes explicitly (§7 ii). |
| 2b | P-RESID cut-over off by one: checkpoint ≤ℓ̂+1 / cost ℓ̂+1..77 can restore an x(ℓ̂+1) that depends on the changed block | Blocking (exactness) | **RESOLVED** §4.2a: valid resume point is x(ℓ̂) at ENTRY to block ℓ̂; resume from highest checkpoint ≤ ℓ̂; block ℓ̂ always rerun; cost = blocks ℓc..77. ASM-2334 updated. |
| 2c | Arm hash contradiction: unconditional hash of KAE/carrier/mode/gain/splice cannot be identical across arms for empty prefix spans | Blocking (exactness) | **RESOLVED** §4.1: canonical H("ARM0") "no effect on this prefix below L" marker with a deterministic, reviewed decision procedure (spans∩prefix=∅ OR all splice layers ≥ L); full-config hash otherwise; fail-closed property preserved. |
| 2d | "Anything in block ℓ̂" too broad: expert/router/post-attention change leaves KV(ℓ̂) valid; a layer-ℓ̂ KV/indexer-path change does not | Correctness of corollary | **RESOLVED** §4.2a: change-class (i)/(ii) distinction; the key already expresses it via kvpath-hash[ℓ̂]; corollary restated per class. |
| 3 | Single-sequence operation does not eliminate the fp32/batch-shape hazard: quantized kernels are shape-dependent; XCACHE_CANON covers only MoE accumulation; "the ONLY composition hazard" and ASM-2335 false | Blocking (exactness) | **RESOLVED** §4.3: "only hazard" claim retracted; Hazard 2 added [facts recorded in ASM-2332, stipulated vendor/project-doc design inputs]; `PCACHE_SHAPEPIN` (fixed row-block prefill policy + kernel-family pins) added to the engine-tag; exactness claim DOWNGRADED to within-the-pinned-regime; `ERR_PCACHE_SHAPE` gate; per-regime bring-up (§7). |
| 4 | Speedup model: attention folded into row term; d=0.75 held constant as P→∞; break-even via average not incremental cost; fabricated llama.cpp 256-token guidance | Model honesty | **RESOLVED** §6 rebuilt: additive α/β/γ/ρ/ω model; A_hit ≈ P·S+S²/2 separated; DSA term flagged for measurement; no asymptote claimed; bracketed scenario table; break-even n* = (ω·P+c_store)/ΔC; 256-token claim removed; provider minimums scoped as eligibility examples. |
| 5 | Upheld: llama.cpp characterization, MIT→Apache, XCACHE/PCACHE non-duplication, KaE composition once arm key + DSA state fixed; ASM-2333 OpenAI staleness (explicit GPT-5.6 breakpoints + prompt_cache_options now exist) | Keep + one fix | **KEPT** §§2/3/5 unchanged in substance; §3.1 corrected for the OpenAI recheck; ASM-2333 updated. |
| 6 | Hot-swap conditionally true but unsupported; sampled recomputation is detection not proof; mid-run new binary = new stratum | Blocking (ASM-2338) | **RESOLVED** §8 re-derived: license = frozen binary + CANON + SHAPEPIN + per-regime bring-up; else stratum-boundary only; binary change = configuration stratum; detection-guard honesty + retroactive item-void rule. |
| 7 | ASM semantics: revise ASM-2331, 2333–2336, 2338, 2339; 2334/2335/2338 most serious | Registration blocker | **RESOLVED** — all listed entries rewritten in the companion JSON (see per-entry revision notes there); structural checks (range, tags, URLs, owner, collision disclosure) preserved. |
