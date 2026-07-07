# KOTK/1 — compact lossless serialization of the concept kernel (design, 2026-07-07)

**Status:** design record with a verified prototype. Every size number in §9 is **measured** on this
repo's data unless marked *(est)*; the prototype codecs that produced them live in
`tools/pack/proto-kotk1-lex.mjs` and `tools/pack/proto-kotk1-haiku.mjs` and re-verify on run.
**Author:** Kern (Claude Fable 5), for @jeswr.
**Depends on:** `docs/design-hash-input.md` (JCS identity decision), `tools/mint/src/{jcs,hash,mint-core,corpora}.ts`
(the minting pipeline this format must reproduce byte-exactly), `encoder/src/{ast,lexicon,encoder,contentHash}.ts`
(the vector pipeline it must feed), `docs/architecture.md` §1.

**Headline (measured):**

| corpus | today | KOTK/1 | KOTK/1 + zstd-19 |
|---|---|---|---|
| haiku-tier snapshot (2,348 records) | 4,757,811 B (2,026 B/rec) | **307,142 B** (130.8 B/rec) | **61,958 B** |
| lexical-wn31 (117,791 records) | 80,728,131 B source / 29.06 MB identity-JCS | **1,387,461 B** (11.8 B/rec) | **732,323 B** |
| full base kernel (~126k records, §9c) | ~93.9 MB sources | **~2.7 MB** (est, 2 corpora measured) | **~1.05 MB** (est) |

Round-trip is proven, not asserted: the prototype re-derives the `urn:kot:` digest of **all 117,791**
wn31 records and **all 84** published haiku URNs from the packed bytes alone (0 mismatches), and
byte-compares reconstructed JCS identity payloads for all 2,348 haiku records (0 mismatches). §6 walks
one record end-to-end.

---

## 1. What the format stores, and what it refuses to store

The whole design follows one rule, the maintainer's, and it is correct:
**anything deterministically derivable from the canonical explication is recomputed at load, never stored.**

Derivable and therefore banned from the canonical kernel document:

- **Content-address hashes.** Every `urn:kot:<multibase>` — both a record's own id and every substituted
  reference inside other records — is `sha256(profileHeader ‖ JCS(NFC(identityPayload)))` wrapped as
  multihash/multibase (`tools/mint/src/hash.ts`). Stored form: **nothing** for own ids; **varint indices
  into the concept table** for references (§5). Measured cost of storing them today: substituted URN
  strings are **59.1%** of math-mm identity bytes, **38.3%** of onto-obo, **28.9%** of physics-qudt.
- **Vectors.** `encodeExplication` (encoder/src/encoder.ts) is seedless and deterministic; vectors are a
  pure function of (AST, encoder pin). The pack stores the encoder pin *hash* (32 B, once) so a consumer
  knows which encoder reproduces the published vectors, and no vector data.
- **Derived per-record fields** already excluded from identity by `corpora.ts` (e.g. math-mm `definedBy`,
  sumo `axiomStats`) stay excluded.

Not derivable and therefore stored verbatim (they ARE the kernel):

- The explication/axiom content itself: ASTs, axiom lists, grounding-note prose, mm token strings,
  KIF strings — as compact structural encodings (§4) whose decode reproduces the exact JCS bytes.
- The identity-payload scalars the mint includes: `sourceId`, statuses, kinds, depths (§4 header
  dictionaries make the constant ones cost ~0).

Three layers, only the first of which is "the kernel" (§8 for the other two):

| layer | content | contract |
|---|---|---|
| **(i) canonical kernel** | everything needed to reproduce every id and every vector | **lossless**, byte-exact hash inputs |
| (ii) provenance/telemetry sidecar | model/prompt/pipeline hashes, source revisions, dates, token usage, cost | optional, lossy-permitted |
| (iii) human-aid sidecar | labels, glosses, lemmas, lexFiles, markers | optional, lossy-permitted |

Measured motivation (2,348-record haiku snapshot, 4,757,811 B): provenance is **43.2%** of
compact-serialized field bytes (~44.6% of file bytes once pretty-print whitespace is attributed), and is
almost entirely constant or telemetry — `promptVersionHash` has **1** unique value across all 2,348
records, `repairPromptVersionHash` **1**, `model` **1**, `framework` **1**, `pipelineVersionHash` **5**;
plus 4,379 `usage` entries and 2,883 `sources` entries. The actual kernel content — the identity
payloads — is 1,291,698 B (27%) of which the AST `record` fields are 702,429 B and grounding notes
169,331 B. Everything else is repetition.

## 2. The hard constraint, restated as the format's invariant

Identity is `sha256( UTF8(profileHeader) ‖ JCS(nfcDeep(identityPayload)) )` per
`docs/design-hash-input.md` and `tools/mint/src/mint-core.ts`, with gist §6 component handling for
cyclic SCCs. So the format's single normative invariant is:

> **INV-1.** For every record, `decode(encode(record))` followed by JCS serialization MUST yield the
> exact bytes the minter hashed. Equivalently: re-minting the decoded pack reproduces every published
> `urn:kot:` URN bit-for-bit.

Everything below is engineered to satisfy INV-1 cheaply, and the encoder is required to *prove* it at
pack time (§7, self-check): if a record can't round-trip through the structural codec, it is stored via
the verbatim-JCS escape (§4.4) rather than ever shipping a lossy encoding. Grammar drift degrades size,
never correctness.

Two consequences worth pinning:

- **NFC is applied at pack time.** The mint pipeline hashes `JCS(nfcDeep(payload))`; the pack stores
  string content already NFC-normalized (NFC is idempotent), so the loader needs no Unicode tables and
  reconstructs hash-input strings by copying bytes.
- **JCS, not JSON.** Reconstruction targets RFC 8785 bytes: object keys sorted by UTF-16 code units,
  shortest-round-trip number serialization, minimal string escaping (`tools/mint/src/jcs.ts`). The
  decoder rebuilds JSON *values*; a shared `jcs()` emits the bytes. Integers ride as varints; any
  non-integer number rides as an IEEE-754 f64 whose JCS string form is recomputed via ECMAScript
  `Number::toString` (a pure function of the double, so lossless).

## 3. Container format (KOTK/1)

All integers are unsigned LEB128 varints unless a fixed width is stated. `str` = varint byte-length +
UTF-8 (NFC) bytes. Multi-byte fixed ints little-endian.

```
Pack        := Magic Header Section* Trailer
Magic       := "KOTK" 0x01                          ; format version 1
Header      := flags:varint                          ; bit0: trailer-has-encoder-pins
               packDate:str                          ; ISO date, informational
               sectionCount:varint
Section     := name:str                              ; corpus name, e.g. "lexical-wn31"
               profileHeader:str                     ; EXACT mint profile header incl. trailing \n,
                                                     ;   e.g. "kot-lex/1\n" — hashed verbatim at load
               refMode:u8                            ; 0 = stable, 1 = substitute   (corpora.ts)
               bodyCodec:varint                      ; 0 = JCS-verbatim rows (universal), else §4
               recordCount:varint
               dict:bytes                            ; varint length + codec-specific dictionaries (§4)
               bodyLen:varint  body:bytes            ; codec-specific record stream
Trailer     := identityRoot:32B                      ; Merkle root over all record digests (§7)
               [ pinCount:varint (encoderPinHash:32B D:varint)* ]   ; if flags bit0
               "KOTK" 0x01                           ; end sentinel (truncation check)
```

- **Section order is dependency order** (kernel-v0, math-v0, molecules-v0, then bulk tiers): every
  substitute-mode reference points to a record in an earlier section or earlier in the same section, so
  a single forward pass re-mints everything (§5). Stable-mode sections have no ordering constraint.
- **Streaming/append:** sections are self-delimiting (`bodyLen`), records are sequential within a body,
  and appending a corpus = append a section + rewrite the fixed-size trailer. A columnar layout was
  considered and rejected: the bodies are already so small (§9) that column splitting buys only a few
  percent of zstd ratio while killing single-pass streaming decode.
- **Whole-pack compression** is transport's business: `.kotk.zst` is the published artifact; the format
  stays defined on the uncompressed bytes.
- **`bodyCodec 0`** stores each record as one verbatim JCS string (`str`). Any corpus can always ship as
  codec 0 — that is the compatibility floor and the migration path for new profiles (§11).

## 4. Body codecs

A body codec owns: its dictionary block, the per-record layout, and the deterministic in-section record
order. Codecs registered for KOTK/1:

### 4.1 Codec 1 — `kot-lex/1` (WordNet-style axiom records; stable refs)

Dictionary block: `constJson:str` (the record-constant fields, here
`{"schema":"kot-lex/1","semanticStatus":"AxiomsOnly"}`), `placeholderPrefix:str`
(`"urn:lexical-wn31:"`), `relCount:varint rel:str…` (14 relations measured), `groupCount:varint
(posLetter:str count:varint)…` in fixed order n,v,a,r.

Record order: pos groups in header order; ascending synset offset within a group. `sourceId` is never
stored as a string — it is `<pos>-<offset zero-padded to 8>`, reconstructed from the group letter and a
**delta-varint offset** (sorted, so deltas are small).

```
Record := offsetDelta:varint
          [ssTypeFlag:u8]                ; 'a' group only: 0='a', 1='s'  (pos = ssType=='s' ? 'a' : ssType)
          axiomCount:varint
          Axiom*
Axiom  := tag:u8                         ; bits0-6 = relId, bit7 = has word indices (antonym srcWord/tgtWord)
          target:varint                  ; index into this section's record table (forward refs legal:
                                         ;   stable mode, two-pass decode); string form rebuilt as
                                         ;   placeholderPrefix + sourceId(target)
          [srcWord:varint tgtWord:varint]
```

Measured: 11.8 B/record, 269,960 axioms, 21× smaller than the identity-JCS bytes it reproduces.

### 4.2 Codec 2 — `kot-haiku/1` + `kot-ast/1` bytecode (explication records; stable refs)

Dictionary block: `constJson:str` (`{"schema":"haiku-tier/1","semanticStatus":"ModelAuthored",`
`"astSchema":"kot-ast/1"}`), `candidateStatus` enum list, `kind` enum list, and the **external-reference
table**: every distinct URN string that appears at a clean whole-string position (`groundingRefs`
entries, AST `concept`/`conceptHead` ids). Measured: 98 unique URNs, 1,962 B stored once, replacing
~31 KB of inline repeats. (Cross-corpus refs stay string-form in the table because haiku-tier is
stable-ref-mode — the mint hashes the placeholder string, not a `urn:kot:` — so no re-mint dependency.)
The closed kot-ast/1 inventories (65 primes, 17 roles in `ROLES` order, 19 predicate frames, 11
operators, 3 frames, 5 refKinds — `encoder/src/lexicon.ts`) are **also written to the dictionary block**
(one `str` list each): the pack must stay decodable if a future lexicon edition renumbers anything.

Record order: ascending `sourceId` (lemma), UTF-16-code-unit sort.

```
Record := sourceId:str                   ; the lemma — irreducible identity content (avg 7.1 B)
          flags:u8                       ; bit0 kindIdx, bit1 candidateStatusIdx,
                                         ; bit2 groundingNote, bit3 groundingRefs, bit4 moleculeDepth,
                                         ; bit5 record-present, bit6 record-is-escape (§4.4)
          [groundingNote:str]            ; NFC prose, verbatim — including embedded {urn:…|gloss} tokens
          [refCount:varint extIdx:varint*]
          [moleculeDepth:varint]
          [record: AstBody | EscapeBody]
AstBody := frame:u8                      ; 0 InstanceSchema, 1 WhenTrue, 2 RelationalSchema
           refCount:varint refKind:u8*   ; ReferentDecl indices are dense from 1 → only kinds stored
           clauseCount:varint Clause*
```

**AST bytecode tag space** (one tag byte per node; pre-order; validated against `encoder/src/ast.ts`):

| tag | node | payload after the tag |
|---|---|---|
| `0x00+p` (p<19) | PredClause, pred = `PREDICATE_FRAMES[p].pred` | roleMask:varint (bit i = `ROLES[i]` present), then one Filler per set bit in `ROLES` order |
| `0x20+o` (o<11) | OpClause, op = `OPERATORS[o]` | argCount:varint, then OpArg nodes |
| `0x30` | SP | spFlags:u8 (bit0 det, bit1 quant, bit2 mods, bit3 bind, bit4 restrictedBy); then in order: det:primeId, quant:primeId, (modCount:varint, per mod: primeId‖0x80-if-intensified, [intensifier:primeId]), bind:varint, Head, restrictedBy:Clause |
| `0x40+(i-1)` (i≤32) | RefMention index i | — |
| `0x60` | PrimeFiller | primeId:u8 |
| `0x61` | ConceptRef | extIdx:varint |
| `0x62` | ClauseFiller | Clause |
| `0x63` | QuoteFiller | clauseCount:varint, Clauses |
| `0x64`/`0x65` | TemporalAnchor AFTER/BEFORE | anchor node (SP / RefMention / PrimeFiller) |
| `0x70` | primeHead | primeId:u8 |
| `0x71` | refHead | index:u8 |
| `0x72` | conceptHead | extIdx:varint |
| `0x73`/`0x74` | kindFrame/partFrame head | `of` node |

Every name-valued field (pred is looked up via its frame index; det/quant/mods/intensifiers/prime
fillers/prime heads) is one byte into the single prime table. Caps (≤32 clauses, ≤32 referents, ≤12
depth — `lexicon.ts CAPS`) guarantee the 1-byte ref encodings.

Measured: conforming explications average **32.6 B** of bytecode vs **685 B** of JCS — **21×**, before
any general-purpose compression. (Positional binary AST vs canonicalized text form, adjudicated: the
bytecode wins 21× uncompressed and still wins post-zstd; a canonical text form is only competitive after
zstd and forfeits the uncompressed/mmap win, so the bytecode is adopted.)

### 4.3 Codec sketches for the remaining corpora *(est rows in §9)*

Same container, same discipline; listed so the estimates are auditable:

- **`kot-pm-mm/1` (math-mm, substitute refs):** dictionary of mm symbol tokens (the 216,034 string
  leaves are drawn from a few-thousand-token alphabet: `"ph"`, `"("`, `"->"` …) → definitions become
  varint token-id arrays; `references` become global concept indices (§5); variables as (nameId, sortId)
  pairs; `status`/`typecode` enums. Removes the 2.25 MB (59.1%) of substituted URN strings outright.
- **`kot-phys/1` (physics-qudt, substitute refs):** enums for type/status; dim vectors as small-int
  arrays; scale/offset/piExponent as varint-or-f64 (§2); `quantityKind`/`coherentSI`/`broader` as
  concept indices.
- **`kot-obo/1` (onto-obo, substitute refs):** rel enum + concept-index axiom pairs (same shape as
  codec 1 but substitute-mode targets), `logicalDefinition` genus/differentia as indices; `oboId` =
  `sourceId` stored once, not twice.
- **`kot-sumo/1`:** KIF strings are literal identity content (stable mode, bare-name refs *inside* the
  string) — stored verbatim; only enums/keys are dictionary-coded, so the win is honest-but-modest (§9).

### 4.4 The verbatim-JCS escape (normative, all codecs)

`EscapeBody := jcsString:str` — the record's field (or whole payload, codec 0) as its exact JCS text.
The pack encoder MUST self-check every structurally-encoded record (encode → decode → JCS
byte-compare, in memory) and MUST fall back to the escape on any failure. This is what makes INV-1
unconditional rather than "true for grammar-conforming inputs".

Measured necessity: **103 of 1,025** live haiku explications (4.4%) deviate from strict `kot-ast/1` —
model-authored records that passed gates with stray shapes (38 with a separate `adjuncts` object on
pred clauses, 38 with `time` directly on the clause, plus a long tail: `manner`, `because`,
`intensifier`-on-SP, `mod`, `op`, `negation`, …). They cost 78,076 B as escapes (758 B avg vs 33 B for
bytecode). Hardening the runner gate to canonicalize these into `roles` *before minting* would shrink
the haiku body by ~70 KB (§9 shows both rows) — but note those records are **already minted with the
deviant bytes in identity**, so for this snapshot the escape is not optional; a re-mint is a semantic
decision outside this format's scope.

## 5. References, topological order, SCCs

- **Stable-mode sections** (wn31, haiku, molecules-v0, sumo): the mint hashed *placeholder* URN strings
  (`urn:<corpus>:<sourceId>`), so references encode as varint indices into the section's own record
  table (rebuild = prefix + sourceId, §4.1) or into the external-URN dictionary (§4.2). Forward
  references are legal (the axiom graphs are non-DAGs — WordNet antonymy — which is *why* these corpora
  are stable-mode); decode is two-pass: read all rows, then materialize strings.
- **Substitute-mode sections** (kernel-v0, math-v0, math-mm, physics-*, obo, framenet): the mint hashed
  *minted `urn:kot:` URNs*, so the loader must re-mint dependencies first. Records are stored in
  **reverse topological order of the condensation DAG** (Unison-style, as the mint pass already
  computes); every reference is a varint **global concept index** — position in the pack-wide
  concatenated record numbering — and always points backward. Small numbers, delta-friendly, and the
  topological discipline is checkable in O(1) per ref at load (`refIdx < ownIdx`).
- **Cyclic SCCs** (gist §6, adopted unchanged by `design-hash-input.md`; implemented in
  `mint-core.ts mintComponent`): an SCC of size n ≥ 2 is stored as a contiguous block, introduced by a
  component marker in the record stream: `componentSize:varint` (1 for singletons — the common case
  encodes in 1 byte) followed by the member records; **intra-component references use reserved index
  values** (own = sentinel 0, sibling j = j+1, external = global index + componentSize offset — the
  exact `#self`/`#member-i` sentinel discipline, index-encoded). The loader re-runs the §6 algorithm
  verbatim: ordering keys (`#self`/`#intra` substitution → sha256), byte-lexicographic sort,
  `ERR_SYMMETRIC_SCC` fail-closed, component digest X, member URN = `H(header#member ‖ X ‖ uvarint(i))`.
  Nothing about the ordering keys is stored — they are recomputed. Measured SCC load: math-mm has
  exactly one 2-cycle ({df-cleq, df-clel}), physics-v0 has 25 two-cycles, onto-obo 49 SCCs (max 11);
  wn31/haiku have none (stable mode sidesteps the question entirely).

## 6. Loader algorithm, with a worked round-trip

```
load(pack):
  1. parse header; for each section, parse dict; decode rows (codec-specific)
  2. for each section in order, for each record/component in order:
       payload := rebuild JSON value          (dictionaries + tables + verbatim strings)
       if substitute-mode: replace ref indices with minted[globalIdx] URN strings
       if singleton:  digest := sha256(profileHeader ‖ jcs(payload)); urn := urnKot(digest)
       else:          run gist §6 componentwise (mint-core.ts semantics) → member digests/urns
       minted[globalIdx…] := urns; leaves.push(raw digests)
  3. verify: merkleRoot(leaves) == trailer.identityRoot   — else ERR_KERNEL_INTEGRITY, fail closed
  4. vectors (on demand): for explication-grammar records, the rebuilt `record` value IS the
     encoder input — encodeConceptSet over the topologically-ordered table (concept refs bind the
     referenced concept's already-computed vector), under the encoder pin(s) named in the trailer.
```

Note what step 4 gets for free: the decoded AST is the *same JSON object shape* `encodeExplication`
consumes (`encoder/src/ast.ts`), and the encoder is seedless (SHA-256 over fixed labels only), so
"reconstruct canonical bytes" and "reconstruct encoder input" are one operation. Determinism of the
float pipeline is X0's golden-vector business, not this format's.

**Worked example — `abate` (records/abate.json), explication-kind.** Identity payload per
`corpora.ts idPayload`: `{sourceId:"abate", schema, semanticStatus, candidateStatus, kind, record}`.
JCS bytes: 580. KOTK/1 stores: `sourceId` `"abate"` (6 B incl. length), flags `0x22`
(kind=explication, candidateStatus=Explicated, record-present, bytecode), and 20 bytes of AST:

```
00            frame = InstanceSchema
01 01         1 referent: SomethingRef            (index 1 implicit — dense)
01            1 top-level clause
24 02         OpClause BECAUSE, 2 args
00 03         PredClause DO, roleMask 0b11 = {agent, undergoer}
60 00           agent    = PrimeFiller I
40              undergoer= RefMention 1
0f 82 02      PredClause BE-SPEC, roleMask 0b100000010 = {undergoer, attribute}
40              undergoer= RefMention 1
30 02 10        attribute= SP, flags {quant}, quant = LITTLE~FEW
70 03           head     = primeHead SOMETHING~THING
```

Decode rebuilds `{schema:"kot-ast/1", frame:"InstanceSchema", referents:[{index:1, refKind:"SomethingRef"}],
clauses:[…]}` plus the four dictionary constants; `jcs()` of the rebuilt payload is byte-identical to the
original 580 (verified in the prototype for all 2,348 records), and
`sha256("kot-haiku/1\n" ‖ those bytes)` → `urn:kot:bciqmsmosjz4gevvm6jh36exmpo3ghyhimr7kzyycazzkhifpu2tr2uy`.
27 stored bytes reproduce a 580-byte hash input and its URN. For the published subset the URNs were
additionally checked against `data/haiku-tier/minted-urns.jsonl`: 84/84; wn31: 117,791/117,791 against
`data/lexical-wn31/minted-urns.jsonl`.

## 7. Integrity: one root instead of 186k hashes

Per-record hashes are recomputed, so the document needs exactly one stored integrity value:

- `identityRoot` = binary Merkle root over the **raw 32-byte record digests in pack order**
  (RFC-6962-style domain separation: leaf = `sha256(0x00 ‖ digest)`, node = `sha256(0x01 ‖ L ‖ R)`, odd
  node promoted). SCC members contribute their member digests (mint-core step 9), so every concept —
  cyclic or not — is a leaf.
- Loader verification (§6 step 3) makes the pack **self-verifying against tampering, truncation and
  bit-rot in one comparison**, and any individual recomputed id is checkable against the root with an
  O(log n) membership proof — which is also exactly the commitment shape the A5/ZK story wants
  (architecture.md §3: verifiable grounding without revealing the store).
- Corpus manifests may additionally record per-section roots (subtree roots at section boundaries) for
  cheap per-corpus diffing; optional, zero effect on INV-1.
- The prototype's simplified chain digest stands in for the Merkle tree; the tree is normative for the
  implementation (membership proofs are load-bearing for A5).

Pack-time self-check (normative, restated): the encoder MUST verify INV-1 per record (structural
round-trip or escape) *and* re-derive `identityRoot` from its own decode pass before publishing.

## 8. The two optional sidecars (explicitly lossy-permitted)

Separate files, content-addressed by the pack's `identityRoot` (`<pack>.prov.kotk`, `<pack>.aid.kotk`),
same container conventions, records keyed by global concept index. **Dropping either loses no identity
and no vectors** — that is the definition of layer (i).

- **Provenance/telemetry sidecar:** header tables for the constants (1 model string, 1 framework, 1+1
  prompt hashes, 5 pipeline hashes — 1-byte ids per record instead of ~874 B of repeated hash strings);
  per-record: pipeline-hash id, date (delta epoch-seconds varint), sources as (templateId, revision:str,
  fetched-delta) — the wiktionary URL is a template over the lemma and is not stored; usage entries as
  token-count varints + costUSD f64. Estimated ~70–90 B/record vs today's ~874 B (**~0.19 MB** vs
  2.05 MB for the haiku tier) *(est)*. Lossy-permitted means: consumers MUST NOT need it to verify the
  kernel; the honest-ledger use case (re-run the pipeline at pins and diff) keeps full fidelity for
  whatever fields it retains — recommended retention is everything except `usage`, which is operational
  telemetry (4,379 entries whose loss changes no scientific claim; keep the per-corpus cost total in the
  manifest if the number matters).
- **Human-aid sidecar:** `label`, `gloss` (216 KB haiku; 8.9 MB wn31), wn31 `lemmas` (2.1 MB)/`lexFile`/
  `markers`, `gatesPassed`/`researchGrade` flags. All annotation-layer by the D1 boundary
  (design-hash-input.md: identity = record minus annotation block) — glosses are paraphrase aids, never
  hash inputs. zstd-dictionary compression applies well here (short similar prose).

## 9. Measured sizes

Method: prototypes in `tools/pack/` (§12); zstd 1.5.x `-19`; "identity-JCS JSONL" = one JCS payload per
line, the honest like-for-like baseline (it is what `dist/canonical/*.canonical.jsonl` stores minus the
redundant `urn` field).

**(a) haiku-tier, 2,348 records (frozen snapshot `haiku-records-2348-20260707T201855Z`):**

| representation | bytes | B/record | zstd-19 |
|---|---|---|---|
| current `records/*.json` (identity + provenance + gloss) | 4,757,811 | 2,026 | 285,796 |
| identity payloads as JCS JSONL | 1,294,046 | 551 | 67,231 |
| **KOTK/1 canonical kernel** | **307,142** | **130.8** | **61,958** |
| KOTK/1 if the 103 grammar-deviant records were re-minted clean *(est)* | ~237,000 | ~101 | ~55,000 |

15.5× structural vs current, **77×** end-to-end (4.76 MB → 62 KB); composition: grounding-note prose
171,223 B (56%), AST bodies 108,283 B (33 B/explication bytecode; 78 KB of that is the 103 escapes),
lemmas+flags+dicts ~28 KB.

**(b) lexical-wn31, 117,791 records:**

| representation | bytes | B/record | zstd-19 |
|---|---|---|---|
| current `synsets-*.jsonl` (identity + annotations + provenance) | 80,728,131 | 685 | 5,398,597 |
| identity payloads as JCS JSONL | 29,174,399 | 248 | 1,128,696 |
| **KOTK/1 canonical kernel** | **1,387,461** | **11.8** | **732,323** |

21× structural vs identity-JCS, 58× vs source files, and still **1.54×** smaller than zstd can make the
JCS baseline.

**(c) full base kernel — wn31 + set.mm + QUDT tiers + haiku + hand-authored v0 (126,437 records):**

| corpus | records | identity-JCS | KOTK/1 | KOTK/1+zstd |
|---|---|---|---|---|
| lexical-wn31 | 117,791 | 29.06 MB | 1.39 MB *(measured)* | 0.73 MB *(measured)* |
| math-mm | 2,998 | 3.80 MB | ~0.76 MB *(est §4.3; URNs 59.1% removed, token dict)* | ~0.22 MB *(est)* |
| physics-qudt | 3,070 | 0.77 MB | ~0.23 MB *(est)* | ~0.05 MB *(est)* |
| haiku-tier | 2,348 | 1.29 MB | 0.31 MB *(measured)* | 0.06 MB *(measured)* |
| kernel/math/molecules/physics-v0 | 230 | 0.10 MB | ~0.04 MB *(est)* | ~0.01 MB *(est)* |
| **total** | **126,437** | **35.1 MB** | **~2.7 MB (21 B/rec)** | **~1.05 MB** |

Against the ~93.9 MB of current source records (with annotations/provenance): **~34×** uncompressed,
**~90×** end-to-end. With the onto-* tiers included (185,776 records, 58.5 MB identity-JCS) the same
discipline lands at ~11 MB / ~4 MB *(est — onto-sumo is KIF-string-bound and only compacts ~1.5×
structurally; its win comes from zstd on the literal strings)*.

Assumptions for *(est)* rows: leaf-content decomposition measured per corpus (string-leaf bytes kept
verbatim, URN refs → 3 B, ~1.5 B/node structural overhead); mm/qudt zstd ratios taken from their
measured identity-JCS zstd ratios, which is conservative (post-dedup bodies compress no worse).

**Where domain encoding beats zstd, and where it doesn't (measured, honest):** zstd-19 on uniform JSONL
already removes most key/URN repetition, so the *post-compression* structural win is 1.54× on wn31
(0.73 vs 1.13 MB) and only 1.08× on the prose-dominated haiku tier (62.0 vs 67.2 KB). The decisive wins
of the structural encoding are (i) the **uncompressed working footprint** — 21× — which is what an
mmap'd loader, a phone, or a WASM verifier actually holds; (ii) decode cost — varint scans, no JSON
parse of 35 MB; (iii) the escape/self-check discipline that makes losslessness provable per record. If
only transport size mattered, zstd-over-JCS-JSONL would be within 1.1–1.6× and this format would be
over-engineering; it is the load path, the derive-don't-store rule, and the single-root verification
that justify it. Grounding-note prose is where generic compression wins and structure has nothing to
offer — by design (identity bytes).

## 10. Reference codec (pseudocode)

```
encode(corpora):
  emit magic/header
  order sections by dependency; for each corpus:
    build dicts (constants, enums, ext-URN table, closed inventories)
    order records (codec rule); assign global indices; group SCCs contiguously (substitute mode)
    for each record:
      body := try structural-encode(record)
      if fail OR jcs(decode(body)) != jcs(nfcDeep(idPayload(record))): body := escape(jcs bytes)  # INV-1
      append body
    emit section
  leaves := decode-pass digests (self-check re-mint)
  emit trailer(merkleRoot(leaves), encoderPins)

decode(pack) -> {payloads, urns, root-verified}:   # §6, two-pass for stable-mode refs
verify(pack) := decode(pack); assert merkleRoot == trailer.identityRoot
vectors(pack, pin) := encodeConceptSet(topologically-ordered decoded ASTs, pin)
```

Implementation-cost reality check from the prototypes: codec 1 is ~150 lines including verification;
codec 2 with the full tag table ~300. sha256 over 118k short inputs is sub-second on this box; the
expensive derived artifact is vectors, which were never going to be stored anyway (1.6–6.4 GB at
kernel scale — architecture.md §1.2 — is the whole reason derive-don't-store wins).

## 11. Honest limits, edge cases, versioning

- **What the sidecars lose** (§8): dropping provenance loses the pipeline-pinned re-derivation trail
  and cost accounting from the *distributed artifact* (it stays in the repo of record); dropping the
  human-aid sidecar loses every gloss/label — machine-sufficient, human-hostile. Both are stated
  lossy-optional; neither touches identity or vectors.
- **Prose-embedded refs are not indexed.** `{urn:…|gloss}` tokens inside `groundingNote`/molecule prose
  are identity *bytes* (stable-mode decision in `corpora.ts`) and stay verbatim — the format must not
  rewrite what the hash covers. Cost is bounded (zstd eats the repetition); a future *authoring*-side
  change (structured grounding refs) would fix it at the semantics layer, not here.
- **Grammar drift is a size bug, not a correctness bug** — but it is real: 4.4% of live model-authored
  ASTs deviate today (§4.4 list), and 5 published URNs among the 84 were minted over deviant bytes. The
  escape hatch carries them; re-minting them clean is a separate, semantic decision.
- **SCC edge cases:** `ERR_SYMMETRIC_SCC` (identical ordering keys) fails at *mint* time; a pack can
  therefore never contain one. Component blocks make the member count explicit, so a loader cannot
  silently mis-scope sentinels. Self-references (`#self`) are index-sentinel 0 and cost 1 byte.
- **Unicode:** NFC applied at pack time; JCS lone-surrogate hard errors surface at pack time (encoder
  runs the real JCS serializer in its self-check). A payload that JCS rejects cannot be minted either,
  so the format introduces no new failure class. Non-NFC *source* strings cannot occur in minted
  identity (the minter normalizes first); if a raw record ships non-NFC bytes, pack-time NFC matches
  what the mint hashed — verified by the URN checks.
- **Numbers:** all observed identity numbers are small non-negative ints; the varint/f64 split (§2)
  covers qudt's floats via ECMAScript shortest-form recomputation. A number that is not IEEE-754
  representable never existed in identity (JCS forbids it).
- **Alignment with encoder/hash-profile bumps:** profile headers are stored verbatim per section — a
  new hash profile is a new string, hashed as-is, no format change. The closed inventories ride in the
  dictionary block, so a lexicon/chart change (an *encoder* version bump per contentHash.ts) changes
  data, not code. A new AST schema (`kot-ast/2`) registers a new bodyCodec id; until a codec exists,
  codec 0 (JCS-verbatim rows) ships any corpus losslessly at ~zstd-baseline size. The trailer's encoder
  pins say which vector pipeline the pack reproduces; X0 goldens guard the float path.
- **What this format does NOT do:** it does not re-mint, merge, or canonicalize records (identity is
  the mint pipeline's); it does not store vectors, similarity structures, or indexes; it does not make
  the estate-interop (RDF projection) decision — the JCS bytes it reproduces are the programme-side
  identity per design-hash-input.md, and the RDF projection remains derivable downstream.

## 12. Prototype receipts (what was actually run, 2026-07-07)

`tools/pack/proto-kotk1-lex.mjs` — packs `data/lexical-wn31/synsets-*.jsonl` → 1,387,461 B; decodes;
re-mints all records; **117,791/117,791 URNs match `minted-urns.jsonl`**; identity-chain digest printed.
`tools/pack/proto-kotk1-haiku.mjs` — packs a records dir (run against the frozen 2,348 snapshot) →
307,142 B; decodes; **2,348/2,348 JCS byte-equality** against `nfcDeep` of the original identity
payloads; **84/84 published URNs** re-derived. Both scripts are self-verifying: a nonzero mismatch
count is a hard failure. zstd numbers via `zstd -19`.
