# F1-K input-corpora construction (DATA CONSTRUCTION pass, $0)

> **Built by the Fable model-code/data agent (designer-23), 2026-07-13.**
> This pass BUILDS the model-independent bytes of the three
> `PINNED-AT-INPUTS` corpora of `registry/experiments/f1k.json`
> `pins.corpus_hashes`, exactly to the frozen recipes, and REPORTS —
> instead of guessing — every recipe detail the frozen record leaves open.
> **NO git action, NO registry write, NO prereg-freeze, NO spend, NO
> instance launch, NO model or tokenizer download.** The engine is referred
> to only as **colibri**. The coordinator owns the freeze and the
> hashing-into-the-record; nothing here is frozen.

## Files

| File | What |
|---|---|
| `build_corpora.py` | The deterministic builder (byte-identical on re-run; the only PRNG uses are the REGISTERED derangement seeds). Every construction rule cites its frozen source in-line; every open choice is tagged `OP-1..OP-9`. |
| `fetch_sources.sh` | Stages the five revision-pinned, sha256-verified benchmark snapshots (the only network step; public data, $0). Run once before `build_corpora.py`. |
| `digests.json` | The three kot-corpus-hash/1 digests of this build (also below). |
| `driver-contract-check.json` | The run-driver input-contract verification (8 checks; 2 flagged, see below). |

Reproduce: `bash fetch_sources.sh && python3 build_corpora.py` (rebuilds all
three `data/` directories byte-identically; verified two consecutive runs
identical, and `tools/registry/corpus-pin.py` reproduces the digests).

## The kernel source (identified, with cites)

- **Concept set + explications:** `data/kernel-v0/` — the ONLY kernel corpus
  pinned by the frozen record (`pins.corpus_hashes["kernel-v0"] =
  8209cada…7c809`, byte-reproduced fail-closed at build time). 54 registered
  explications; the per-concept `gloss` field is the explication text
  rendering used for the K-carrier prepend and the d3-text arm
  (design §2.4 / §2.6).
- **Surface bridge:** `data/lexical-wn31/alignment-kernel-v0.json`
  (kot-lex-align/1, hand-reviewed kernel-v0→WN3.1 synset alignment; 53/54
  aligned, `has-part` recorded unaligned) + the in-repo WN3.1 source dict
  (`data/lexical-wn31/source/dict/`) for synset lemmas and derivational
  ("+") pointers — the "(WordNet lemma/derivational surface expansion)" of
  the `f1k-trigger-map-v1` pin text.
- **Encoder vectors are NOT an input:** design §2.4 explicitly DEFERRED
  "decoded kernel concept vectors projected in" (the B3 objection); carriers
  are forward-pass hidden-state offsets. The encoder pin is untouched.

## The three digests (kot-corpus-hash/1, this build)

Recipe: `f1k.json pins.corpus_hashes._recipe` (reference implementation
`tools/registry/corpus-pin.py`; digests reproduced by that tool).

| Corpus | Digest (this pass) | Pin status |
|---|---|---|
| `f1k-trigger-map-v1` | `14c2f1133ef190450de189257db678df608e9bca9f7f95e97e9a720b76a630de` | **(A)-complete as built** — pinnable at freeze-manifest (A) once the coordinator adopts OP-3/OP-4 (below). |
| `f1k-eval-v1` | `d242d6097ba2d44b29ea1c1b4a0bd0130645c12dfd99beae45a182579ca6038e` | Model-independent layer complete; the digest CHANGES when the tokenizer-derived sidecar lands (a pure function of this corpus + the bring-up-pinned tokenizer, pre-addendum-(6)). |
| `f1k-carriers-v1` | `3184921e6251768ca09a0eecf6b1c40be957807f4299a74c3824dcae929fb7e9` | **NOT the B0 pin.** Pre-spend generator components only; realized tables + raw/rescaled norms are the post-construction B0 pure-function addendum (SSR-REV3.3) and cannot exist in a $0 pass. |

## Build-to-recipe summary

1. **`data/f1k-trigger-map-v1/`** — 54 concepts (canonical index = URN byte
   order), 195 trigger phrases (synset lemmas + derivational forms, with
   per-phrase provenance), the frozen §R4 gate-precedence rules, and the
   disclosed base matching rule. `has-part` carries an empty trigger set
   (unaligned in the hand-reviewed alignment; disclosed, not padded).
2. **`data/f1k-eval-v1/`** — the frozen mechanical filter (§2.7: lexical
   trigger match over question+options; MMLU first, then the pre-registered
   pool ARC-Easy/Challenge, OpenBookQA, CommonsenseQA) over five pinned
   snapshots (19,311 items → 7,727 admitted, 11,584 zero-trigger);
   test-1440 (AT the registered cap, filled breadth-first to m=8 to
   maximise C) / dev-96 (stratified ≥1 per cluster, disjoint) / guard-60
   (zero-trigger, off-concept); frozen §R1.1 template BYTES per item
   (header/cue verified trigger-free char-level, fail-closed); §R4-resolved
   CHAR-level span sidecars in carrier-slot ids; d3-text renderings;
   `multi-concept` / `option-trigger` tags; verbatim subset composition +
   power-gate arithmetic in `coverage-report.json`.
3. **`data/f1k-carriers-v1/`** — registered-seed derangements (11;
   101/102/103) realized as fixed-point-free permutations over the 49
   carrier slots (the concepts present in the frozen test/dev spans, §R2);
   carrier-slot↔concept map; per-concept K-explication + d2-dictionary
   texts (hashed, freeze-(A)(ii)); DRAFT m=16 construction contexts
   (checked disjoint from every eval item); the §2.4/§R2 generator spec
   with every model-dependent input explicitly BLOCKED.

## HEADLINE FINDING — the power gate is unsatisfiable at the pinned kernel

Realized test composition: **49 clusters, 46 with m ≥ 8**, against the
registered hard gate **C ≥ 65 clusters each m ≥ 8 at n = 1,440**
(ASM-2271). The pinned kernel universe bounds C ≤ 54 (and even the most
generous unpinned reading, kernel-v0+v1 = 65 concepts, cannot yield 65
clusters at m ≥ 8: `has-part` has no lexical surface, four concepts admit
zero items under the mechanical filter (`archived`, `bookmark`,
`condolence`, `lie`), and three more sit under m = 8 (`grieving` 2,
`reminder` 1, `sad` 1) — so even 65 concepts would realize at most ~57
gate-eligible clusters). **This is the design's own
registered PRE-RUN RETURN** ("below it F1-K does NOT run and returns to
the maintainer with the measured coverage-vs-power shortfall",
SSR-REV2.2/§8) — surfaced now, at corpus construction, before any spend.
F1-K as frozen cannot proceed past its power gate on any corpus derivable
from the pinned kernel; the maintainer decision (expand the kernel's
registered explications, amend the gate, or return the experiment) precedes
any freeze of these corpora.

## Underspecification report (frozen-recipe gaps — reported, not guessed)

Every open choice this build had to make is tagged `OP-n` in
`build_corpora.py` and in each corpus `manifest.json`; each REQUIRES
coordinator adoption (or amendment) at freeze-manifest (A):

- **OP-3 (LOAD-BEARING): the concept universe.** "All kernel concepts with
  registered explications" is ambiguous across kernel-v0 (54; the pinned
  corpus — THIS BUILD), v0+v1-with-supersession (61), v0+v1 (65). Pin
  discipline argues for kernel-v0; the power-gate consequence is stated
  above for all three readings.
- **OP-1: benchmark snapshot bytes.** The design names the datasets but pins
  no distribution; this build pins canonical HF revisions (sha256 in
  `data/f1k-eval-v1/source/sources.lock.json`). CommonsenseQA VALIDATION
  split (its test golds are unpublished; the §R1.1 scorer needs gold).
- **OP-2: template header/cue BYTES** (§R1.1 fixes the shape only) — drafted,
  mechanically verified trigger-free; freeze-(A) entry 1 adopts or redrafts.
- **OP-4: base trigger-matching rule** (case-insensitive whole-word) — §R4
  freezes only the overlap precedence.
- **OP-5: ARC numeric answer labels** rendered with the canonical A–E
  alphabet (published option ORDER preserved verbatim).
- **OP-6/OP-6a: residual deterministic split ordering** (stem-preference
  first per §R-REV2.1, then source rank in the design's listed order, then
  row; dev round-robin; test breadth-first to m=8 then round-robin;
  guard = first 60 zero-trigger items; item cluster = concept of the first
  §R4-resolved span).
- **OP-7: seed→derangement algorithm** — the design registers the SEEDS
  only; this build uses the run driver's exact algorithm.
- **OP-8: construction-context authoring procedure** (DRAFT; §2.4 allows
  "enumerated verbatim" — 16 verbatim WordNet-authored contexts/concept are
  enumerated, disjointness-checked against eval).
- **OP-9: prepend separator** (one blank line) for d3-text and the
  construction prepend variant.

**Named in the frozen record but given NO value anywhere (must be fixed at
(A); inventing them here would invalidate the experiment):** the
construction seed (freeze_manifest A(vii) names it; no value exists); the
d0 random-direction generation algorithm; the exact candidate splice-layer
ids (A(iv) = the pilot grid union; L1≈40/L2/L3 need the pinned model
config); the mean native expert weight anchoring the g grid; the GLM-5.2
tokenizer (bring-up pin, ASM-1971) for `template_tokens` /
`label_token_ids` / token-level spans / the single-token label
verification.

## Driver input-contract check (`driver-contract-check.json`)

Checked against `f1k_driver.py` `load_eval_manifest` / `validate_dose` /
`kaec_read` (the driver is being fixed in parallel; these are its
input-verification seams): split sizes 1440/96/60 ✓; guard zero-span
(recomputed) ✓; d3 present for test/dev ✓; labels/gold well-formed ✓;
derangement seeds+FPF match `validate_dose` ✓; KAEC parameters (D=6144,
nc=49, layers=bring-up) consistent ✓. **Two flagged items:**
(1) **token-field mismatch** — the driver requires TOKEN-level
`template_tokens`/`label_token_ids`/`spans`/`d3_template_tokens` in the
eval manifest; this corpus carries frozen template BYTES + CHAR-level spans
+ the deterministic derivation rule (`template-spec.json`), because the
tokenizer is a bring-up pin. Either the driver grows a corpus→manifest
tokenizer step, or the coordinator derives the token manifest pre-(6).
(2) **power gate** — see the headline finding.

## Governance self-check

- Engine named **colibri** only; no author handle anywhere in this pass.
- NO git, NO registry write, NO prereg-freeze, NO spend, NO instance, NO
  model/tokenizer download; network use = five public benchmark snapshots
  (pinned, sha256-verified, $0).
- Kernel source identified and byte-verified against the record's pin
  (kernel-v0 digest reproduced fail-closed at build).
- Every construction rule cites `f1k.json` or a design § in-line; every
  open choice is an enumerated OP requiring (A) adoption; the genuinely
  missing frozen details are REPORTED, not invented.
- Deterministic: two consecutive builds byte-identical; digests reproduced
  by `tools/registry/corpus-pin.py`; no wall-clock in any output byte.
- No feasibility conclusion is stated; the mock/coverage numbers are
  construction arithmetic, not evidence.
