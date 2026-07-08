# task-family-tinystories — the pre-declared M0b target-task content-word mass

**What this is.** The frequency-weighted content-word lemma table of the
TinyStories validation split: 3,753,554 word tokens, of which 1,709,765
(45.55%) are content-word mass under the pinned function-word stoplist; the
top-500 content lemmas (80.35% of content mass) are listed with per-lemma
token counts and surface breakdowns. This is the denominator corpus for the
M0b kernel-expressibility coverage measurement (registry experiment `m0b`).

**Provenance (pre-declared, not produced for the refreeze).** The file
`m0b-vocab.json` is a byte-identical copy of `mapper/m0/results/m0b-vocab.json`
(sha256 `9e644b65db9cb804333350ffd75ffb37595ed1c02303691b1f23bacdce0345df`),
generated on 2026-07-07 by `mapper/m0/run-m0b-vocab.mjs` over the TinyStories
validation split, and committed with the original M0b estimate — i.e. it
predates the m0b registry freeze and the 2026-07-08 pre-sign-off correction
wave. Content-word definition, lemma-folding rules, and the function-word
stoplist are pinned in that generator's header comment.

**Coverage convention (conservative, stated).** The unclassified long tail
(7,481 − 500 distinct lemmas; 19.65% of content mass, skewed toward rare
concrete nouns and proper names) is counted as NOT covered at every rung.
Coverage numbers computed against this table are therefore lower bounds with
respect to the top-500 truncation only in the trivial sense — the tail is
assumed uncovered, which is the unfavourable direction for the kernel.

**Scope honesty.** TinyStories is the deliberately favourable ~1.5k-lemma
domain (see `mapper/m0/results/m0b-report.md` §"Limits"). Per the frozen m0b
extrapolation envelope, coverage measured here extrapolates to NO other corpus
or rung and is restated with its rung in every later verdict (P2 G-7).
