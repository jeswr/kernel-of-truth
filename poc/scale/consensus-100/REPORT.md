# Consensus-100: six-model concept-explication agreement & cheapest-set analysis

**Scope.** For the FIRST 100 F1-K concepts, generate a concept explication with
each of SIX models, find the strong-consensus definition per concept, score how
much each model agrees with the consensus, and determine the cheapest subset of
models that reproduces the two most-capable models (gpt-5.6-sol + claude-fable-5).
All work at **$0 marginal** (subscription auth throughout). No git commit.

Author: experiment-runner (Opus main loop). Everything under
`poc/scale/consensus-100/`. Judgement calls flagged (marked with a leading triangle)
for coordinator + Fable/GPT-5.6 review.

---

## 0. Headline

| | Result |
|---|---|
| Concepts generated | **100** (positions 1-100 of the frozen F1-K round-robin; 29 AGENTIVE / 56 ACT / 15 STATE) |
| Cells completed | **599 / 600** (99.8%). One gap: `predation` x `claude-fable-5` (Fable usage cap - see section 2) |
| Refusals | **ZERO** - no model refused any concept, including every sensitive one (rape, euthanasia, suicide, predation, coercion, shoring) |
| Per-model coverage | 5 models **100/100**; Fable **99/100** (1 cap gap) |
| Strong consensus (embedding, tau=0.90, >=4/6) | **83 / 100** concepts |
| sol+fable reference agreement | the two reference models agree on only **75 / 99** concepts (disagree on 24) |
| **Cheapest single model reproducing sol+fable >=95%** | **gpt-5.6-terra** - 97.3% fidelity at ~$0.0037/concept |
| **Cheapest single model at 100% fidelity** | **gpt-5.6-luna** - ~$0.0046/concept |
| **Recommended robust cheap set** | **haiku-4.5 + luna + terra** (cross-vendor, all cheap): 100% coverage, 100% paraphrase-fidelity, ~$0.014/concept - **~17x cheaper** than the sol+fable pair (~$0.25/concept) |
| Major caveat | Embedding consensus **diverges badly** from a strict LLM judge (mean Jaccard **0.42**). The fidelity numbers are **paraphrase-level**, not truth-conditional. See sections 4 + 6. |

Total wall time ~= **58 min** (batch generation ~38 min + timed re-run of stragglers
~10 min + 10-concept judge validation ~10 min). Measured Claude API-equivalent
cost ~= **$20.83** (Fable-dominated; opus $0.036, fable $0.176, haiku $0.006 per
concept); GPT models via the codex/subscription path report tokens not USD ->
**$0 marginal**. All work ran on subscription auth, so real marginal spend was $0.

---

## 1. Concept selection (Step 1)

`select_100.py` continues the pilot's frozen, benchmark-blind rule verbatim
(`concept-def-agent/select_test_concepts.py` / `gen_pilot.py`), only extending the
horizon 20 -> 100:

> P1 eligibility (`greedy_disjoint_m8` & not `header_cue_collision`) -> genus
> prefilter into strata AGENTIVE / ACT / STATE by gloss prefix -> sort by URN byte
> order -> round-robin A, ACT, S -> take positions 1-100.

Deterministic, no gloss/outcome consulted for ranking. Positions 1-15 are the
pilot and 16-20 the earlier smoke test, so this is a strict superset (continuity
guaranteed). Output: **`concepts-100.json`** (label + urn + pos + lemmas + WN
gloss + stratum per concept). Strata realised: 29 AGENTIVE, 56 ACT, 15 STATE
(the eligible genus-prefiltered pool holds only 108 such concepts total).

## 2. Generation (Steps 2-3) + the Fable gap

`define_concept.py` was extended **minimally** to accept the 3 new models
(`claude-haiku-4-5` on the existing Claude path; `gpt-5.6-luna`, `gpt-5.6-terra`
on the existing codex path - just a different `-m`). Prompt and record schema
unchanged. A single call per model was verified before the run (all 6 produce
valid, gate-passing records).

`run_batch.py` drove 600 calls with 10 concurrent workers, checkpointed
(resume = skip any cell whose record exists), records -> `gen/<slug>.<short>.json`.
Claude models were spread across the backup OAuth accounts (opus->acct3,
fable->acct2, haiku->acct4; each with a fallback chain + a per-account concurrency
cap) to dodge per-account usage caps.

**Fable cap.** This session's primary account had Fable capped from the start
(429 "reached your Fable 5 limit"); Fable was routed through backup account2 and
succeeded on 99/100 concepts. During finalisation the Fable tier then capped
**across all backup accounts** (account3 hard STOPCAP; account2/account4 returned
an identity-fallback - `modelUsage=[opus,haiku]`, no fable - which the identity
tripwire correctly rejects). The single remaining cell
`predation x claude-fable-5` is therefore a genuine **Fable-cap gap**, recorded
and not blocked on. **This is a cap, not a refusal.**

**Straggler handling.** The initial batch ran without a per-call timeout; the
codex `xhigh` path has heavy latency variance (luna median 57 s, **max 325 s**;
sol median 57 s, max 142 s; terra median 26 s) which left ~9 cells in flight /
non-recorded when the run was stopped. `rerun_missing.py` re-ran only those cells
with a **hard per-call timeout** (codex 300 s, claude 150 s) and first-class
outcome classification (`ok | timeout | cap | refused | nonjson | error`);
8/9 recovered, 1 = the Fable cap above.

## 3. Coverage (per-model, first-class signal) - `coverage.json`

| model | ok / 100 | refused | timeout | nonjson | cap | failed concepts |
|---|---|---|---|---|---|---|
| claude-opus-4-8 | **100** | 0 | 0 | 0 | 0 | - |
| claude-fable-5 | **99** | 0 | 0 | 0 | 1 | `predation` (Fable cap) |
| claude-haiku-4-5 | **100** | 0 | 0 | 0 | 0 | - |
| gpt-5.6-sol | **100** | 0 | 0 | 0 | 0 | - |
| gpt-5.6-luna | **100** | 0 | 0 | 0 | 0 | - |
| gpt-5.6-terra | **100** | 0 | 0 | 0 | 0 | - |

**The content-refusal hypothesis is not supported.** The genuinely
content-sensitive WordNet concepts in the set - `rape` (#93, "despoiling a country
in warfare"), `euthanasia` (#38), `suicide` (#64), `predation` (#84), `coercion`
(#100), `shoring` (#95) - were **defined by all six models, GPT included**. The
apparent "hang on sensitive concepts" observed mid-run was **codex `xhigh`
latency variance, not refusal**: the slowest codex cells were mundane concepts
(`changelessness` 325 s, `cook`, `chip`, `dilation`, `cheerfulness`), and a scan
of every record + codex `last-message` found **no refusal language** anywhere
(the only regex hits were definitional content - e.g. "wrongdoer = one who
*violates* a law"). Coverage is thus a non-discriminator here: all six models are
viable on general-dictionary concepts, so coverage does **not** rule any model
out for scale. (The one operational risk it surfaces is codex tail-latency, which
matters for throughput, not correctness.)

## 4. Consensus (Step 4) - mechanical + judge - `consensus.json`, `judge-spotcheck.json`

**Embedding.** Each gloss embedded with the repo's pinned `nomic-embed-text-v1.5`
(`kb_common.Embedder`, 256-d Matryoshka, `search_document:` prefix, L2-normed -
the repo's canonical call), pairwise cosine among a concept's glosses.

**Strong consensus** = the largest **clique of >=4** glosses that are **pairwise**
cosine >= tau (mutually similar, not merely connected); consensus definition = the
clique **medoid**.

**Threshold tau = 0.90 (chosen + justified).** Within-concept pairwise cosines are
high and tight (min 0.806, p10 0.888, median **0.933**, mean 0.931) - all six
models write near-paraphrases of the same WN sense. The count of concepts with a
>=4 clique is flat-then-cliff as tau rises: **0.86->100, 0.88->99, 0.90->83,
0.92->69, 0.94->35, 0.95->19**. The knee at 0.88->0.90 is where requiring a
4-clique first "bites" (separating near-identical glosses from merely-similar
ones), so tau=0.90 is the discriminating operating point. **Sensitivity
(tau +/- 0.05): 0.85->100, 0.90->83, 0.95->19 strong-consensus concepts.**

**Judge validation (10-concept random sample, gpt-5.6-sol, identity hidden).**
The judge grouped glosses by strict truth-conditional identity ("adding/dropping
a truth-conditional element => different group; consensus = the single >=4 group").

> **Mean Jaccard(embedding clique, judge consensus) = 0.42; only 2/10 exact
> matches.** The result is bimodal: strong agreement on `neglecter`/`weakening`
> (1.0) and `dilation`/`equality` (0.8), but on **5/10** (`combustion`,
> `medication`, `ransom`, `rape`, `builder`) the judge found **no >=4 supermajority
> at all** while embeddings clustered 4-6 together.

**The embedding clustering diverges badly from the judge, and per the design I
prefer the judge's grouping for the "same-definition" question.** Reconciliation
(embedding clique vs judge across tau) shows **no threshold rescues it**: mean
Jaccard peaks at only ~0.50 (tau >= 0.95, and only because both sides go empty
there) and is ~0.41-0.45 across 0.86-0.90. **Interpretation:** cosine >= 0.90
certifies *paraphrase* similarity; the judge enforces *truth-conditional*
identity - different constructs. The models genuinely differ in definitional
detail on ~half of concepts. **Cost of preferring the judge at scale:** the judge
is a dear-tier model at ~57 s + heavy tokens per concept (~$0.07/concept on the
sol price proxy) vs ~free embedding - a real per-concept tax for millions of
concepts.

**Consequence for the numbers below:** the embedding-based agreement/fidelity
figures should be read as **"same definition up to paraphrase."** They
**overstate** strict definitional agreement. See section 6 for scaling.

## 5. Scoring + cheapest set (Step 5) - `scoring.json`

### 5a. Per-model agreement vs the 6-model strong consensus (tau=0.90)

Fraction of strong-consensus concepts where the model's gloss is in the >=4 clique:

| model | agreement | (in / of) |
|---|---|---|
| gpt-5.6-luna | **0.940** | 78/83 |
| claude-haiku-4-5 | **0.904** | 75/83 |
| gpt-5.6-terra | 0.880 | 73/83 |
| claude-fable-5 | 0.878 | 72/82 |
| gpt-5.6-sol | 0.855 | 71/83 |
| claude-opus-4-8 | 0.843 | 70/83 |

**Notable:** the *cheap* models (luna, haiku, terra) sit **closer to the group
consensus** than the *expensive* ones (opus, sol, fable). The dear models are the
ones most often left out of the tight cluster - consistent with them adding more
distinctive/nuanced phrasing. At the paraphrase level, "more capable" does **not**
mean "more central."

### 5b. Cost proxy ($/concept)

| model | $/concept | basis |
|---|---|---|
| gpt-5.6-terra | **0.0037** | measured mean tokens x stated cheap-tier price |
| gpt-5.6-luna | **0.0046** | as above |
| claude-haiku-4-5 | **0.0059** | **measured** API-equivalent (cache-affected) |
| claude-opus-4-8 | 0.0357 | **measured** API-equivalent |
| gpt-5.6-sol | 0.0732 | measured tokens x stated dear-tier price |
| claude-fable-5 | **0.176** | **measured** API-equivalent (dearest) |

Claude figures are the API-equivalent `total_cost_usd` reported by the CLI
(reduced by prompt caching during the batch). **The 3 GPT figures are a
published-price PROXY** (codex reports tokens, not USD; subscription marginal =
$0): dear tier sol = $2.50/$10 per-Mtok in/out, cheap tier luna/terra =
$0.15/$0.60. Full input tokens are priced (cache ignored), so GPT is if anything
*over*-costed. The cheap-set conclusion depends only on the stipulated ordering
(luna/terra/haiku << sol/fable), which holds under any plausible pricing.

### 5c. Reference = sol + fable, and the cost-vs-fidelity frontier

Reference answer for a concept exists iff sol & fable both produced a gloss **and**
their glosses cluster (cosine >= tau). **The reference pair agree on only 75 of 99
concepts** (disagree on 24, ~24%) - the two "most intelligent" models are far from
interchangeable with each other at tau=0.90. A subset S "reproduces" the reference
on a concept iff its medoid gloss is within tau of the sol+fable shared direction.

**Pareto frontier (cost ascending, reference models excluded):**

| $/concept | fidelity to sol+fable | subset |
|---|---|---|
| 0.0037 | 0.973 (73/75) | **terra** |
| 0.0046 | **1.000 (75/75)** | **luna** |
| 0.0083 | 1.000 | luna + terra |
| 0.0142 | 1.000 | **haiku + luna + terra** |

- **Cheapest >=95%:** `gpt-5.6-terra` alone - 97.3% at $0.0037/concept.
- **Cheapest >=90%:** same (`terra`).
- **Cheapest at 100%:** `gpt-5.6-luna` alone - $0.0046/concept.

**tau-sensitivity of the headline (terra):** fidelity 0.85->**1.000**,
0.90->**0.973**, 0.95->**0.600**. i.e. at the strict 0.95 bar, a single cheap
model reproduces the reference only 60% of the time - "reproduction" here means
*same definition up to paraphrase*, and is threshold-dependent. This is the
quantitative face of the judge-divergence caveat.

## 6. Recommendation - cheapest viable set for scaling to millions

Folding agreement **and** coverage **and** the judge caveat:

1. **If paraphrase-level reproduction of sol+fable is the bar** (the metric this
   experiment can measure cheaply), a **single cheap model suffices**:
   - **gpt-5.6-luna** - 100% coverage, **100%** fidelity, ~$0.0046/concept, and the
     single most consensus-central model; or
   - **claude-haiku-4-5** - 100% coverage, 97.3% fidelity, $0.0059/concept
     (measured), and cross-vendor from the GPT reference partner.
2. **Recommended robust set: `claude-haiku-4-5 + gpt-5.6-luna + gpt-5.6-terra`** -
   cross-vendor, all cheap, **100% coverage, 100% paraphrase-fidelity,
   ~$0.014/concept**, **~17x cheaper** than running the sol+fable pair
   (~$0.25/concept). The mix hedges single-model / single-vendor blind spots that a
   size-100 sample cannot rule out, and gives a free per-concept agreement signal
   (route disagreements to a judge).
3. **Do not read this as "generation is solved cheaply."** The judge divergence
   (section 4) shows the six models disagree on truth-conditional detail on ~half
   of concepts, and the reference pair itself agrees only 75%. For the kernel's
   actual need - *canonical, truth-conditionally correct* explications - **no
   generator tier (cheap or dear) reliably produces a judge-certified consensus
   definition on its own.** The scalable pattern is **cheap-ensemble generation +
   a verification/judge pass on disagreements**, not "pick one model and trust it."
   Budget the judge tax (~$0.07/concept dear-tier, or a cheaper judge to be
   evaluated separately).

## 7. Gaps, threats to validity, honest caveats

- **1 missing cell:** `predation x claude-fable-5` (Fable cap across all accounts;
  not a refusal). Fable coverage 99/100; all fable-dependent stats use n=99/82.
- **Judge sample is n=10** (random, seeded). Mean Jaccard 0.42 is a strong signal
  of divergence but a small sample; a full-100 judge pass would firm it up (cost
  ~95 min + dear-tier tokens) and is the natural next step if the maintainer wants
  a judge-grounded reference.
- **GPT $/concept are a stated price proxy**, not billed cost (subscription = $0).
  Ordering, not magnitude, drives the conclusion.
- **tau=0.90 is a defensible but stipulated choice** (elbow of the count curve);
  all key results carry the 0.85/0.90/0.95 sensitivity. Everything downstream is
  paraphrase-level similarity, per section 4.
- **Easy regime:** the first-100 F1-K concepts are common, well-lexicalised words;
  agreement is high and coverage universal. Harder/rarer concepts (the
  millions-scale tail) may separate the models on coverage *and* agreement - this
  sample cannot extrapolate there. Treat the cheap-set recommendation as validated
  **only** for this common-concept regime.

## 8. Artifacts (all under `poc/scale/consensus-100/`)

| file | contents |
|---|---|
| `concepts-100.json` | the 100 selected concepts (Step 1) |
| `select_100.py` | selection script (frozen round-robin, positions 1-100) |
| `run_batch.py`, `rerun_missing.py` | parallel checkpointed generator + timed straggler re-run |
| `gen/<slug>.<short>.json` (+ `.report.json`, `provenance/`) | 599 raw records + per-call provenance/latency/cost |
| `run-log.jsonl`, `coverage-rerun.jsonl` | per-cell run log + re-run outcome classification |
| `consensus.py` -> `consensus.json` | mechanical strong-consensus, cosine matrices, medoids, tau-sensitivity |
| `judge_spotcheck.py` -> `judge-spotcheck.json` | 10-concept judge validation vs embeddings |
| `coverage.py` -> `coverage.json` | per-model ok/refused/timeout/cap grid |
| `scoring.py` -> `scoring.json` | per-model agreement, cost table, Pareto frontier, cheapest sets |
| `REPORT.md` | this report |

*(A change to `concept-def-agent/define_concept.py` - the added model choices -
is left uncommitted for coordinator review; it does not touch the prompt or record
schema.)*
