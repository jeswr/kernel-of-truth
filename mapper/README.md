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

## Build & test

```sh
cd mapper && npm install && npm test   # tsc build + node:test (27 tests)
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

The corpus file is NOT committed (19.4 MB): fetch with
`curl -L https://huggingface.co/datasets/roneneldan/TinyStories/resolve/main/TinyStories-valid.txt -o /tmp/TinyStories-valid.txt`.
