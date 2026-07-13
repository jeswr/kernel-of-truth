# Is the AST-lossiness a Luna issue? — per-model breakdown

Answer: **No — it's a GPT-family pattern, not Luna-specific; but there's a real vendor split.** AST-adequacy
self-flag (each model self-assesses whether its kot-ast/1 explication, in profile-1's 65 primes, fully
renders the differentia), over the 100 consensus-100 concepts:

| model | faithful | lossy | % lossy |
|---|---|---|---|
| claude-opus-4-8 | 31 | 69 | 69% |
| claude-fable-5 | 35 | 64 | **65%** |
| claude-haiku-4-5 | 34 | 66 | 66% |
| gpt-5.6-sol | 11 | 89 | 89% |
| gpt-5.6-luna | 9 | 91 | 91% |
| gpt-5.6-terra | 9 | 91 | 91% |

- **Luna's 91% is NOT a Luna artefact** — Sol (89%) and Terra (91%) show the same. Switching Luna→Sol would
  **not** help; the whole GPT family self-flags ~90% lossy.
- **But the Claude family self-flags only ~65–69% lossy** (~33% faithful) — a real, consistent ~3× higher
  faithful rate than GPT.

## Cross-model agreement (99 concepts flagged by all 6)
- **Unanimously LOSSY: 48** — genuinely hard; all six agree the 65 primes can't render them (concept-determined).
- **Unanimously FAITHFUL: 6** — genuinely simple.
- **SPLIT: 45** — the models disagree; this is exactly where the vendor gap lives (Claude tends to call
  these faithful, GPT tends to call them lossy).

## Interpretation (the open question this raises)
The vendor split could be either:
- **(a) genuine** — the Claude models decompose into the primes more completely (really more faithful), or
- **(b) leniency** — the Claude models apply a lower bar for self-flagging "faithful" (under-report lossiness).
The self-flags alone can't disambiguate; the **45 SPLIT concepts** are the test bed. An independent
AST-adequacy adjudication on those 45 (does the AST actually render the differentia?) would settle it.

## Why this matters for #33 (the faithful-heavy option)
If (a) holds, a **Claude generator (fable or haiku, ~33% faithful yield)** makes the faithful-heavy arm
**~3× cheaper** than Luna/GPT (~10% yield) — netting 65 faithful from ~200 generations instead of ~700.
That would materially change the cost of option 2/3. But it hinges on the (a)-vs-(b) question above — and
note the countervailing fact: the GPT models scored **higher on definitional quality** (sol 2.70/luna 2.54
vs opus 1.79/fable 1.72), so GPT may simply be the more rigorous self-critic (consistent with (b)), in which
case Claude's "faithful" flags are optimistic and the real faithful rate is closer to the GPT ~10%.

Recommended next step if the faithful arm is wanted: adjudicate the 45 SPLIT concepts with an independent
strict AST-adequacy check (blind, cross-vendor) to resolve genuine-vs-lenient before committing a
Claude-generated faithful-heavy batch.
