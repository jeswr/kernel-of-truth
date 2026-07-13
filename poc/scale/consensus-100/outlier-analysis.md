# Why Fable and GPT-5.6-Sol were the "outliers" — consensus-100 analysis

"Outlier" here = a model whose gloss fell **outside** the strong-consensus cluster (cosine < τ=0.90
to the ≥4-model medoid) on a concept. It measures **distinctiveness of phrasing in embedding space**,
NOT wrongness. Denominator = the ~83 concepts that reached a strong consensus.

## Outlier frequency (of ~83)
| model | outliers | mean gloss length |
|---|---|---|
| claude-opus-4-8 | **13** | 27.2 w |
| gpt-5.6-sol | **12** | 21.4 w |
| claude-fable-5 | 10 | **29.5 w** |
| gpt-5.6-terra | 10 | 22.9 w |
| claude-haiku-4-5 | 8 | 26.9 w |
| gpt-5.6-luna | **5** (most central) | 21.8 w |

Note opus is actually the single most frequent outlier; Fable and Sol are outliers for **two different reasons**.

## Fable's outlier signature: ELABORATION / narrative register
Fable writes the **longest** glosses (29.5 w) and adds process, consequence, and a literary/moralizing
tail — richer, more discursive, so the embedding sees the extra material as distant. It usually AGREES
on the meaning; it just says more.
- **candidate** — consensus: "A person considered as a possible choice for a position, prize, honour…".
  Fable adds a whole uncertainty clause: "…**it being not yet settled whether this person or someone
  else will receive it**."
- **spendthrift** — consensus: "…with little regard for future needs or the limits of their means".
  Fable: "…with no thought for future want or **for the ill that may follow**" (adds consequence + a
  moralizing note).
- **coiner** — Fable appends the diffusion process: "…**after which other speakers take it up and use
  it themselves**."
- **access** — Fable restates the spatial transition twice: "a movement by which someone who was not
  within it comes to be present inside it."

## Sol's outlier signature: FORMAL FRAMING + occasional NARROWING
Sol writes the **shortest** glosses (21.4 w) — so its outlier-ness is NOT verbosity, it's **register and
extension**: a more abstract/technical framing, and sometimes an over-specifying qualifier.
- **earner** — consensus: "A person who receives payment or wages in return for work…". Sol NARROWS:
  "…**from an employer** in return for work performed **under an employment arrangement**." (A real
  extension shift — a freelancer or business owner earns without an employer; Sol's is arguably *worse*.)
- **equality** — consensus: "…stand at the same level of value, measure, or standing…". Sol reframes
  abstractly: "a state of **correspondence between persons or things that do not materially differ**…".
- **initiation** — Sol adds a formal enumerated tail: "…bringing a new **activity, practice, condition,
  or organization** into being or operation."
- **grazing** — consensus: "…without stopping or striking it with force". Sol: "…without a **direct
  collision or interruption of motion**" (physics-register framing).

## The vendor split behind this
Claude models run **long and rich** (27–30 w), GPT models run **terse** (21–23 w). Luna (a terse GPT)
lands on the median phrasing most often (5 outliers); Fable (longest) and opus drift via elaboration;
Sol drifts via formal reframing despite being terse.

## The load-bearing caveat (ties to judge-Jaccard 0.42)
Because the consensus metric is **embedding paraphrase-similarity**, "outlier" tracks **distinctive
wording/register**, not meaning. Fable's richer definitions and Sol's formal ones **mostly agree on the
concept** — they're arguably *better* or *equal* lexicography, just non-median. So the "cheap models
agree more" result reads as **the cheap models reproduce the median phrasing**, NOT that they're more
correct. The one genuine-deviation class is Sol's occasional over-narrowing (earner→employer) — a real
extension difference a strict judge would also flag. Net: "agreement with consensus" rewards
median-blandness; it is a *reproducibility* signal, not a *quality* ranking — which is exactly why the
cheapest-set recommendation needs a judge/verify pass, not blind trust in embedding-agreement.
