# kot-lint — Stage-0 kernel precision linter (mode P)

The coverage-INDEPENDENT usable core of the kernel precision linter
(design: `docs/next/kernel-precision-linter.md`, node N-PL, §6 Stage 0).
Zero runtime dependencies beyond `mapper/dist` and the committed kernel data.

## What it does (Stage 0, mode P — permissive report; never blocks)

| class | mechanism | severity |
|---|---|---|
| **V-rhetorical** | deterministic filler/weasel/hedge pattern lexicon (`lib/patterns.mjs`, 75 patterns, content-hashed; LNT-F3 arm (a)) | warn |
| **A ambiguous** | mapper abstentions on CONTENT tokens (candidates listed; a1-hybrid preset default, N-PL §2 S2) | warn |
| **U coverage** | per-token vocabulary-band annotation on the m0b rung ladder kernel-v0 → molecules-v0 → wn31-aligned (membership only) | info |

Plus, per document: the coverage-engagement vector (Stage-0 lattice
projection `{M, A, U-mol, U-wn31, U-out}` over clause-level propositions),
conjunctive proposition-coverage fractions by rung, flag rates, and the full
pin block (kernel manifest sha, mapper version + policy sha, pattern-lexicon
sha).

## What it deliberately does NOT do (Stage 1+, N-PL §6)

- **G+/G− groundedness** — needs decode-verify against canonical records +
  the `kot-axiom/1` sidecar (the L3a engine seat). Class `M` means "fully
  kernel-v0-mappable", NEVER "grounded-consistent".
- **V-tautology** — needs the explication normaliser (coverage-dependent).
- **Mode S (quarantine contract) / mode R (rewrite)** — need the renderer +
  round-trip gate. `--mode=S|R` fails closed (`ERR_LINT_MODE_UNIMPLEMENTED`).

**Vocabulary honesty (binding, N-PL §9.6):** class U is
"out of kernel coverage / unverifiable-here" — never "hallucination".
Ungroundable ≠ false.

## Usage

```sh
node tools/lint/kot-lint.mjs README.md                       # human-readable
node tools/lint/kot-lint.mjs --json --strip=markdown x.md    # stable JSON
node tools/lint/kot-lint.mjs --policy=none --no-wn31 x.txt   # flagless mapper, skip wn31 band
node tools/lint/test/selftest.mjs                            # mechanics self-test ($0)
```

`--strip=markdown` is offset-preserving (stripped characters become spaces),
so flag offsets always index the original file.

## Determinism contract (N-PL §2 S5)

Same text + same pinned inputs ⇒ byte-identical `--json` report: no RNG, no
timestamps, stable key order (`stableStringify`). Verified by two-run `cmp`
in the LNT-E0 harness run of 2026-07-09.

## Declared Stage-0 operationalisations (read before citing numbers)

1. **Proposition proxy = clause** via deterministic segmentation
   (`lib/segment.mjs`): sentence split + clause split on hard punctuation,
   comma+coordinator, and a closed subordinator list. No syntactic parse; no
   frame/grammar conjunct. All conjunctive-coverage fractions are therefore
   **upper bounds** on true proposition-level conjunctive coverage
   (LNT-F1 arm (a)).
2. **Content token** = the pinned M0b `FUNCTION_STOPLIST` definition, copied
   verbatim from `mapper/m0/run-m0b-vocab.mjs` (provenance
   `data/task-family-tinystories/README.md`).
3. **A-flags fire on content tokens only.** Function-word abstentions (the
   copula is/was lexicon collision) are counted in `tokens.decisions.abstain`
   but not flagged — flagging every copula would be pure alarm noise (the
   Bessey false-positive lesson, N-PL §1.1).
4. **Band membership for unmapped tokens** checks
   `{norm, lemma} ∪ lemmaCandidates(norm)` against molecule `corpusLemmas`
   and wn31 single-word synset lemmas (same band definitions as
   `tools/experiments/m0b_instrument.py`). wn31 is membership only — never
   quoted as explicated coverage.
5. **Default mapper policy** is the signed `a1-hybrid` preset (which aliases
   `shadowed-hybrid-recommended`, policy sha `e13dc838…`); `--policy=none`
   gives byte-identical v0.1.0 abstain-and-record.

## Files

- `kot-lint.mjs` — CLI (mode P only)
- `lib/lint.mjs` — core classification + report assembly + context pins
- `lib/segment.mjs` — sentence/clause segmentation, markdown de-formatting
- `lib/patterns.mjs` — V-rhetorical pattern lexicon (versioned + hashed)
- `lib/vocab.mjs` — band vocabularies + pinned content-word stoplist
- `test/selftest.mjs` — planted-defect fixtures, determinism, monotonicity

First measured numbers: `poc/linter-census/` (LNT-E0 — exploratory Tier-0
census + false-alarm floor).
