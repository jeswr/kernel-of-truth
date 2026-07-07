# KOTK/2 — near-entropy-floor kernel serialization (decision record, 2026-07-07)

**Status:** decision record over two verified competing prototypes. Every number is **measured** on
this repo's data; the codecs re-verify on run (encode → decode → rebuild JCS → re-mint every
`urn:kot:` → hard-fail on any mismatch).
**Author:** Kern (Claude Fable 5), for @jeswr.
**Supersedes for storage:** `docs/design-compact-kernel-serialization.md` (KOTK/1). The **hashing form
is untouched**: identity remains `sha256(profileHeader ‖ JCS(nfcDeep(identityPayload)))` per
`docs/design-hash-input.md`; KOTK/2 changes only the storage codec under the same INV-1
(decode must reproduce the exact JCS bytes the minter hashed).

**Prototypes compared:**

- **entropy-columnar** — `tools/pack/proto-kotk2-entropy.mjs` (wn31), `tools/pack/proto-kotk2-haiku.mjs`
  (haiku). Columnar symbol streams, per-context static rANS, mirror-queue structural derivation.
- **grammar-factored** — `tools/pack/kotk2-lib.mjs` + `proto-kotk2-grammar.mjs` (wn31) +
  `proto-kotk2-haiku-part.mjs` (haiku). Static rANS plus explicit grammar layers: a domain
  inverse-edge rule on wn31 and generic Re-Pair subtree factoring on haiku ASTs.

Both prove losslessness the same way KOTK/1 did: **wn31 117,791/117,791 URNs re-minted identically
from packed bytes alone; haiku 2,348/2,348 JCS byte-equality + 84/84 published URNs re-derived**, in
both prototypes. The 103 grammar-drift records (4.4%) ride the verbatim-JCS escape unchanged; gist-§6
SCC handling is inherited from KOTK/1 semantics but not exercised (both corpora are stable-ref-mode,
no SCCs).

---

## 1. The measured verdict

`zstd 1.5.x -19`; *residual ratio* = `zstd(pack)/pack` — **1.00 means zstd finds nothing left**.
(KOTK/1's §9 quoted the inverse convention; normalized here.)

### lexical-wn31 (117,791 records) — the primary structured corpus

| representation | bytes | +zstd-19 | residual | B/record |
|---|---|---|---|---|
| source jsonl | 80,728,131 | — | — | 685.4 |
| identity-JCS JSONL | 29,174,399 | 1,128,696 | 0.039 | 247.7 |
| KOTK/1 | 1,387,461 | 732,323 | 0.528 | 11.8 |
| KOTK/2 grammar-factored | 500,858 | 484,538 | 0.967 | 4.25 |
| **KOTK/2 entropy-columnar** | **341,435** | **337,283** | **0.988** | **2.90** |

xz-9e cross-check on the winner: 337,560 B — generic compressors agree there is ~1% left.

### haiku-tier (frozen 2,348-record snapshot) — prose-heavy

| representation | bytes | +zstd-19 | residual |
|---|---|---|---|
| KOTK/1 (whole) | 307,142 | 61,958 | 0.202 |
| KOTK/2 grammar-factored (whole) | 293,726 | 59,494 | 0.203 |
| KOTK/2 entropy-columnar: symbolic kernel | 20,726 (8.8 B/rec) | 18,570 | 0.896 |
| KOTK/2 grammar-factored: symbolic kernel | **16,772** | **13,088** | 0.780 |
| entropy-columnar: text sidecar (notes 171,223 + escapes 78,076) | 249,305 | 32,119 | 0.129 |
| entropy-columnar: combined transport | 270,031 | 50,580 | 0.187 |

**Verdict: entropy-columnar wins**, decisively on the corpus that matters. On wn31 it is **1.47×
smaller raw and 1.44× smaller post-zstd** than grammar-factored, **4.06× / 2.17× smaller** than
KOTK/1, **236× smaller** than today's source jsonl, at **2.90 B per concept** with residual **0.988** —
zstd-19 recovers 1.2%, i.e. we are at the entropy floor to within a percent. On the haiku *symbolic
kernel* grammar-factored is smaller (16,772 vs 20,726 B) because Re-Pair captures repeated AST
sub-templates that order-1 context modeling misses — that earns Re-Pair a place as an **optional
per-stream transform** in the spec (§3.5), not as the base codec. Whole-file haiku numbers are
dominated by prose either way (§2).

## 2. The stakeholder's hypothesis, answered in bytes

*"KOTK/1's residual zstd-compressibility = repeated structure + symbol skew + embedded prose."*
Correct, with sharply different mixes per corpus.

### wn31: 0% prose, ~56% skew, ~44% structure

wn31 identity payloads contain **zero natural-language text** (gloss/lemmas were annotation-layer
already in KOTK/1), so prose explains none of its 0.528 residual. The ablation chain
(grammar-factored prototype, plus the columnar winner) decomposes the full
1,387,461 → 341,435 B gap (1,046,026 B):

| step | bytes | removed | share of gap | cause |
|---|---|---|---|---|
| KOTK/1 | 1,387,461 | — | — | — |
| + rANS entropy coding only (all 269,960 directed axioms) | 799,020 | 588,441 | 56.3% | **(b) symbol-frequency skew** |
| + inverse-edge grammar (mirror derivation) | 550,864 | 248,156 | 23.7% | **(a) cross-concept structure** |
| + generic Re-Pair on tag stream | 500,858 | 50,006 | 4.8% | (a) structure |
| entropy-columnar: contextual rANS + 91% mirror elision | **341,435** | 159,423 | 15.2% | (a)+(b) combined (order-1 context + better mirror capture) |

The structural half is the interesting finding: **WordNet's axiom graph is symmetric by construction**
— 269,326/269,331 edges have an exact mirror (`(B,hyponym,A)` ↔ `(A,hypernym,B)`, antonym
word-indices swap included). This redundancy is **invisible to zstd** (the mirror edge serializes with
a different target index, hence different bytes); only a semantic rule sees it. It also means a
topological "all refs point down" ID order **cannot exist** for wn31 — the endorsed design point 1 had
to bend there, and bending it paid: the columnar codec's deterministic *mirror queue*
(derive-don't-store, exact per-axiom fallback) elides 122,251/134,666 second-direction edges (91%) to
~1-bit symbols, strictly more than topological locality could recover. The grammar prototype's version
of the same rule derived 80,370 mirrors (capped by 8,849 records with non-canonical axiom order); that
gap plus per-context modeling (`rel` stream 2.32 → 1.07 b/sym with prev-symbol context; distance
chaining) is exactly the 159,423 B between the two prototypes.

### haiku: ~81% prose, remainder skew + AST structure

Of KOTK/1's 307,142 B, **249,305 B (81%) is natural-language text** — `groundingNote` prose
(171,223 B) plus the 103 verbatim-JCS escapes (78,076 B). That text zstd's 7.8× (→32,119 B); it is
where generic compression legitimately wins and structure offers nothing. The actual symbolic kernel
is 16.8–20.7 KB depending on codec. Within it, Re-Pair over the AST pre-order token stream removed a
further **23.6% beyond entropy coding** (21,945 → 16,772 B via 943 rules, 32,694 → 6,739 symbols) —
direct confirmation that NSM explications share repeated sub-templates
(`pred BE-SPEC{undergoer:ref, attribute:sp{…}}`-shaped).

**One honest caveat the stakeholder must see:** for *this frozen snapshot*, haiku's groundingNote
prose is **inside** the identity payloads (stable-mode mint decision), so the "text sidecar" stream is
identity-bearing — re-minting needs kernel+text. Making prose truly non-canonical (endorsed design
point 3, fully) is an **authoring/re-mint decision, not a codec one**; the codec already isolates the
prose into its own stream so that decision costs a re-mint, not a format change.

## 3. KOTK/2 specification (the winning codec, concretely)

### 3.1 Container

```
Magic        := "KOTK" 0x02
Section      := profileHeader:str            ; EXACT mint profile header, verbatim incl. trailing \n
                codecId:u8                   ; 0 = verbatim-JCS escape (compat floor), 2 = columnar-rANS
                streamCount:varint
                Stream*                      ; each: streamId:u8, ctxCount:varint, freqTables, blobLen, blob
                identityRoot:32B             ; §3.6
                "KOTK" 0x02                  ; end sentinel
```

One section per (corpus, profile). Whole-pack compression stays transport's business (`.kotk2.zst`)
— at residual 0.988 it is nearly a no-op on wn31, but it still earns its keep on freq tables and
raw-bit blobs.

### 3.2 Unified ID space — primes first, no dictionary (endorsed point 1, confirmed)

- **0–64**: the 65 NSM primes in the pinned `encoder/src/lexicon.ts` PRIMES chart order. A
  convention, zero stored bytes. Primes are precisely the concepts with no definition body.
- **65–127**: reserved structural codes — kot-ast/1 operators, frames, roles, ref-kinds, heads —
  pinned per grammar revision (assignment recorded in `proto-kotk2-haiku.mjs`).
- **128+** (`GLOBAL_BASE`): concepts in deterministic pack order. Where the reference graph is a DAG,
  topological order so every reference points down; where it is symmetric-by-construction (wn31: pos
  groups n,v,a,r, ascending offset), the mirror queue supersedes topological order (§3.4).
- **No string↔id dictionary anywhere.** References are concept ids; the only strings in a pack are
  the profile header and (haiku, stable-ref-mode only) 98 front-coded external URN strings the mint
  hashed as strings — a substitute-mode re-mint collapses those to ids too.

### 3.3 Entropy coding: static contextual rANS (endorsed point 2, confirmed)

Static rANS, 12-bit-normalized frequency tables, one table per (stream, context); tables
varint-serialized in the header; decode is table-driven O(1)/symbol. **rANS over canonical Huffman**
because several streams carry p≳0.5 symbols (MIRROR hits, ssType, chained-distance bucket 0) where
Huffman's 1-bit floor forfeits 0.3–0.6 b/sym; measured coder efficiency is within 0.02% of the
order-0 floor. Wide values (offset deltas, reference distances) split DEFLATE-style:
entropy-coded bit-length bucket + raw low bits (low bits measured ~uniform; coding them buys nothing).

wn31 streams and measured bits/symbol (vs naive fixed-width): `off` 1.401 vs 4 (ctx = pos group),
`ss` 0.978 vs 1, `nax` 2.285 vs 10, `rel` 1.069 vs 5 (ctx = previous symbol in record), `dist`
2.996 vs 5 (ctx = rel; value chained within record, zigzag), `word` 0.424 vs 4. Table overhead:
1,675 B (0.49% of pack) + 278 B header/dicts. Haiku: `tag` 2.672 vs 6, `prime` 2.255 vs 6, `roleMask`
1.259 vs 7 (ctx = pred), lemma chars 3.571 vs 5 (order-1); tables 4,212 B + header 983 B.

### 3.4 References: delta + chain + mirror queue

References code as **relative distances**, chained within a record (init = own index), zigzag'd,
bucket+raw-bits, entropy-coded with ctx = relation. On symmetric relations the **mirror queue**
applies: when an explicit forward axiom `(i, rel, t>i)` is coded, encoder and decoder both push the
implied inverse onto record `t`'s FIFO; at record `t` an axiom equal to the queue front codes as the
1-symbol MIRROR (~1 bit). Front mismatch falls back to explicit coding — **losslessness never depends
on the mirror property**; the rule is derive-don't-store with an exact per-axiom escape.

### 3.5 Optional per-stream Re-Pair transform (from the grammar prototype)

A stream may declare `transform = repair(rules)` in its header: Re-Pair grammar rules (nonterminals
allocated above the concept range) applied to the token stream before rANS. Encode-time A/B decides
per stream: on wn31 it loses to contextual modeling (columnar without it is already 32% smaller than
grammar-factored with it); on haiku's AST tag stream it wins 23.6%. This keeps the base decoder simple
and admits the AST-template win where it is real.

### 3.6 Sidecars and integrity (endorsed point 3, confirmed with one bend)

Canonical kernel = symbolic explications only (primes + refs + operators + identity scalars).
**Provenance** (model, prompt/pipeline version hashes, sources, dates, usage/cost) and **all NL text**
(labels, glosses, lemmas, grounding prose) live in separate files content-addressed by the pack's
`identityRoot` (`<pack>.prov.kotk2`, `<pack>.text.kotk2`), lossy-permitted, invisible to identity.
The bend: the current haiku snapshot's grounding prose is hash-covered (§2), so its text file is
marked `identity-bearing: true` until an authoring re-mint clears it.

`identityRoot` = sha256 over the re-minted URNs in pack order (wn31: `c11756…a6e7`). Encode is
self-verifying: the packer re-mints every record from its own output and refuses to emit on any
mismatch — INV-1 is proven at pack time, per record, every time.

### 3.7 Versioning

Profile headers are stored verbatim per section: a new hash profile is a new string, no format change.
The 0–64 prime assignment and 65–127 structural codes are pinned to the encoder/grammar version
(an `ALGORITHM_VERSION` bump per `contentHash.ts` implies a new pinned assignment, recorded in the
section header as a chart-revision id); old packs decode under their recorded revision. Codec 0
(verbatim JCS) remains the compatibility floor and migration path.

## 4. Honest limits

- **Small-corpus table overhead.** On haiku, freq tables + header are ~5.2 KB against a ~21 KB kernel
  (25%); Re-Pair's rule table is 6.3 KB against 16.8 KB. Both amortize at full-kernel scale (wn31:
  0.49%), but below ~10k records the entropy machinery is a real tax and codec-0 or KOTK/1 may be the
  pragmatic choice for tiny tiers.
- **Where the floor actually is.** The remaining 1.2% on wn31 is the freq tables themselves plus mild
  structure in the raw-bit extras (offset deltas cluster by lexicographer-file allocation; distance
  low bits not perfectly uniform). Static per-context tables deliberately concede a little vs
  adaptive/higher-order modeling to keep decode table-driven; an adaptive CM coder might buy a few
  more percent at real decode-speed cost. Not worth it.
- **Is grammar-factoring worth its complexity?** As a *base layer*, no — on wn31 contextual rANS +
  mirror queue beats explicit grammar + Re-Pair by 32% with a simpler decoder. As an *optional AST
  transform*, yes — 23.6% on haiku kernels, and the rule table amortizes with scale. The prototype
  Re-Pair is full-recount (~40 s niced on this box); production would want incremental linked-list
  Re-Pair.
- **Mint-side improvements the codec exposes.** Canonicalizing axiom order at mint time would push
  mirror elision toward the full ~134k (worth ~100 KB in the grammar prototype's accounting; the
  columnar fallback already recovers most of it). Re-minting the 103 grammar-drift records clean
  removes the 78 KB escape blob. Substitute-mode re-mint collapses haiku's external URN strings to
  ids and makes prose genuinely sidecar. All three are authoring decisions, deliberately outside
  this format.
- **Not exercised:** gist-§6 SCC/substitute-mode paths (no SCCs in stable-mode corpora); behavior is
  inherited from KOTK/1 §5 semantics and must be re-verified when a substitute-mode corpus lands.

## 5. Prototype inventory

- `tools/pack/proto-kotk2-entropy.mjs` — **the recommended base codec**, wn31: 341,435 B, 117,791/117,791 re-mint.
- `tools/pack/proto-kotk2-haiku.mjs` — columnar haiku: kernel 20,726 B + text sidecar, 2,348 JCS-exact + 84/84 URNs.
- `tools/pack/kotk2-lib.mjs`, `proto-kotk2-grammar.mjs`, `proto-kotk2-haiku-part.mjs` — grammar-factored
  competitor; source of the ablation numbers in §2 and of the §3.5 Re-Pair transform.
