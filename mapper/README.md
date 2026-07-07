# @jeswr/kernel-mapper — phrase→concept mapper v0

Deterministic transducer from English text to kernel-v0 references
(architecture.md §3.2: deterministic lexicon primary; learned assist would be
annotation-only and does not exist in v0). Zero runtime dependencies.

## Design

- **Lexicon** (`src/lexicon.ts`): compiled from kernel-v0 concept labels
  (`data/kernel-v0/manifest.json`; parentheticals stripped) + the 65-prime
  surface-exponent lists (`src/primes.ts`, incl. allolexes: SOMETHING~THING →
  something/thing, OTHER~ELSE~ANOTHER → other/else/another, …). Prime names
  are test-locked against `encoder/src/lexicon.ts`.
- **Tokenizer** (`src/tokenize.ts`): lowercasing, deterministic contraction
  expansion (don't → do not), offset-preserving.
- **Lemmatizer** (`src/lemmatize.ts`): rule-based, dictionary-free — returns
  an ordered CANDIDATE list (plural/-ed/-ing/-er/-est with doubling and
  e-restoration rules, irregular tables); it never pretends suffix stripping
  is unambiguous.
- **Matcher** (`src/mapper.ts`): multiword phrases longest-match-first, then
  single-token lookup over the lemma-candidate union.
- **Ambiguity policy — abstain and record.** Any surface form whose candidate
  set contains >1 distinct target (prime/concept collisions like kind, near,
  inside; copula polysemy is/was; inflection collisions broken/break,
  lost/lose) yields `{kind:'abstain', candidates:[...]}`. The mapper NEVER
  resolves word sense; abstention rate is a first-class pre-registered number
  (M0a).
- **Output**: annotated token stream `{surface, norm, lemma, decision,
  phraseLen, phrasePos, start, end}` suitable for E1 corpus augmentation —
  stochastic substitution happens downstream; the mapper only annotates.
- **Flag-gated ambiguity policies** (`src/policy.ts`, bead
  kernel-of-truth-30d; DEFAULT OFF — no policy argument = v0.1.0 behaviour,
  byte-identical): declared sense-priority tiers (exact-decision-set keyed,
  fail-closed, content-addressed via `policyHash`; resolved tokens carry
  `resolvedFrom` for audit) and evaluated-set exclusion lists (reporting
  only; decisions untouched). Candidate declarations for the five
  ambiguity-shadowed concepts (broken, lost, inside, near, kind) are
  measured in `m0/results/m0a-shadowed-policy.md`.
- **Amendment A1 preset** (signed 2026-07-07, docs/poc-design.md Phase M):
  the hybrid declaration is ADOPTED for E1 as the named preset `a1-hybrid`
  (`policyPreset('a1-hybrid')`, also `--policy=a1-hybrid` on run-m0a.mjs) —
  tiers for {inside, near, broken}, evaluated-set exclusion for {kind, lost},
  policy sha `e13dc838…` (pinned as `A1_POLICY_SHA256`; resolution fails
  closed on drift). The preset ALIASES `SHADOWED_HYBRID_RECOMMENDED`; the
  package default (no policy argument) remains byte-identical v0.1.0
  abstain-and-record.

## Build & test

```sh
cd mapper && npm install && npm test   # tsc build + node:test (37 tests)
```

## M0 measurements (pre-registered; poc-design.md Phase M)

`m0/` holds the M0a/M0b harnesses and `m0/results/` the reports:

- `m0/run-m0a.mjs` — token-mass coverage, abstention, hit distributions over
  TinyStories-valid; emits `m0/annotation-sample.jsonl` (300-token stratified
  sample **for human annotation**).
- `m0/make-agent-judgments.py` + `m0/compute-pr.py` — PROVISIONAL agent-judged
  precision/recall (caveat stamped; superseded by the human pass).
- `m0/run-m0b-vocab.mjs` + `m0/classify-m0b.py` — frequency-weighted
  kernel-expressibility classes over the top-500 content lemmas.
- `m0/run-shadowed-sample.mjs` + `m0/make-shadowed-judgments.py` — 50-item
  per-concept samples of the five shadowed concepts' abstained occurrences
  + AGENT-JUDGED sense judgments (pending human annotation);
  `m0/run-m0a.mjs --policy=<name>` re-measures M0a under a candidate policy
  into `m0/results/m0a-policy-<name>.json` (never overwrites the baseline).

The corpus file is NOT committed (19.4 MB): fetch with
`curl -L https://huggingface.co/datasets/roneneldan/TinyStories/resolve/main/TinyStories-valid.txt -o /tmp/TinyStories-valid.txt`.
