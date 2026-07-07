# X1-grounding — dictionary grounding structure vs. NSM (pre-registration)

**Status:** 2026-07-07 — PRE-REGISTERED, not yet implemented. Everything below is fixed
before any graph is built or any statistic is computed. Deviations require a dated entry
in §9 (Amendments) written **before** results are unblinded.
**Author:** Kern (Claude Fable 5). **Tracker:** child of bead `kernel-of-truth-99a`
(construction methodology); builder files/claims its own bead before starting.
**Naming note:** this is **X1 of the methodology ladder**
(`notes/construction-methodology-research.md` §5), NOT Phase-X X1 (encoder margins,
`docs/poc-design.md`). It is referred to as **X1-grounding** (`x1g`) in all code, file
names, and results to avoid collision.

**Pre-registered question (ladder text, verbatim):**

> **X1 — Dictionary grounding structure vs. NSM (days, ~$0, CPU only).** *Question:* is
> the empirical floor of definitions where NSM says it is? *Method:* build the
> WordNet+Wiktionary definition graph; compute Kernel/Core/Satellites and sampled MinSets
> (the 2016 paper's method). Pre-registered predictions: NSM primes land in Kernel/Core
> far above frequency-matched chance, and over-represent in the MinSet intersection.
> *Pass:* NSM keeps its base-layer role. *Fail:* switch the basis to a dictionary-derived
> core (Jesse's route wins at the foundation). *Unblocks:* the basis decision, and
> produces the scaffold graph the hybrid needs regardless of outcome.

Method source: Vincent-Lamarre, Blondin Massé, Lopes, Marcotte, Johansson & Harnad,
"The Latent Structure of Dictionaries", *Topics in Cognitive Science* 2016
(arXiv:1411.0129), building on Blondin Massé et al. 2008 (arXiv:0806.3710). Where this
document says "the 2016 paper", that is the reference. One scoping deviation from the
ladder text, decided now: **the primary graph is WordNet 3.1 glosses only.** The local
Wiktionary cache (`data/haiku-tier/cache/defs/wiktionary`, 3,165 lemmas) covers only
already-processed lemmas and is not a dictionary; full-Wiktionary is deferred to an
optional extension X1b (§8, threat T1). The verdict below binds on the WordNet graph.

---

## 1. Data & provenance (pinned)

| input | path | pin |
|---|---|---|
| Synset records (glosses + lemmas) | `data/lexical-wn31/synsets-{noun,verb,adj,adv}.jsonl` | committed; shard sha256s in `data/lexical-wn31/manifest.json`; 117,791 synsets |
| Lemma vocabulary | `data/lexical-wn31/source/dict/index.{noun,verb,adj,adv}` | per-file sha256s in `manifest.json` |
| Morphology exceptions | `data/lexical-wn31/source/dict/{noun,verb,adj,adv}.exc` | inside `wn3.1.dict.tar.gz`, sha256 `3f7d8be8ef6ecc7167d39b10d66954ec734280b5bdcd57f7d9eafe429d11c22a` |
| NSM primes | `encoder/src/lexicon.ts` `PRIMES` (65, chart v20-2022) | the prime table in §5.1 is transcribed from it and is the frozen artifact |

`source/` is gitignored; if absent, re-download per `data/lexical-wn31/README.md` and
verify the tarball sha256 before anything runs (fail closed, `ERR_X1G_SOURCE_MISSING`).
The results JSON must embed every input sha256 it consumed.

**Definition unit.** The definitional unit is the synset gloss (`annotations.gloss`).
Every lemma of a synset is treated as defined by that synset's gloss; a word with several
senses is defined by the union of its synsets' glosses (sense-collapsed, word-level —
the 2016 paper likewise works at word level, not sense level; threat T4).

## 2. Preprocessing (exact pipeline, in order)

**2.1 Gloss cleaning.** Split the gloss on `;`. Drop every segment whose first
non-whitespace character is `"` (these are usage examples, e.g.
`| a tangible and visible entity; "it was full of rackets..."`). Within kept segments,
delete any remaining double-quoted span (`"[^"]*"`). Parenthetical text is **kept**
(WordNet parentheticals are usually definitional, e.g. "(living or nonliving)"); the
parens themselves fall to tokenization. Empty cleaned glosses are logged
(`emptyGlossCount`).

**2.2 Tokenization.** Lowercase; strip possessive `'s`/trailing `'`; split on every
character not in `[a-z'-]`; drop tokens containing a digit and tokens of length 1.
Hyphenated tokens: try the full form first (WordNet has hyphenated lemmas); if
out-of-vocabulary after morphology, split at hyphens and process the parts as separate
tokens. Apostrophes other than possessive are kept for vocabulary lookup (e.g. `o'clock`)
and the token is dropped if OOV.

**2.3 Lemmatization — Morphy-lite, no nltk.** A token resolves to a lemma node by, in
order (first hit wins):
1. **Exact match** in the index vocabulary (union of `index.{noun,verb,adj,adv}` lemmas).
2. **Exception lists**: look the token up in `noun.exc`, `verb.exc`, `adj.exc`, `adv.exc`
   (in that POS order); a candidate is accepted if it is in the index vocabulary (any POS).
3. **Detachment rules** (WordNet `morphy(7WN)` suffix rules, applied per POS in the order
   noun → verb → adj; within a POS, rule order as listed; a candidate is accepted iff it
   appears in **that POS's** index):
   - noun: `s→∅, ses→s, xes→x, zes→z, ches→ch, shes→sh, men→man, ies→y`
   - verb: `s→∅, ies→y, es→e, es→∅, ed→e, ed→∅, ing→e, ing→∅`
   - adj: `er→∅, est→∅, er→e, est→e`
4. Otherwise the token is **dropped** and counted (`oovTokenCount`, plus a top-100 OOV
   frequency list in the report).

**2.4 Function words / stopwords.** **No stopword list.** The node vocabulary IS the
WordNet lemma index; WordNet has no closed-class entries, so `the, of, a, to, that, who,
which, in, or, and, ...` drop out mechanically at step 2.3.4. This is the single lexical
filter, pinned because it is source-derived rather than analyst-chosen. Consequence,
stated up front: NSM's function-word-like primes (IF, BECAUSE, THIS, YOU, ...) are
structurally invisible to a WordNet graph — they are handled by exclusion in §5.1 and
discussed as threat T1. `not` and `maybe` survive (WordNet adverb entries) and are
treated like any other word.

## 3. Graph construction

- **Node set V:** all lemmas in `index.{noun,verb,adj,adv}`, lowercased, POS-collapsed
  (one node per orthographic lemma string, across POS). Multi-word lemmas (underscored,
  e.g. `physical_entity`) are included as nodes; they can be *defined* but can never
  *define* (gloss tokens are single words; no collocation matching — pinned), so they
  drop out of the Kernel mechanically. Census reports both `|V|` and `|V_sw|`
  (single-word nodes); all strata fractions and the null pool use `V_sw`.
- **Edges (orientation pinned):** for each synset `s` with lemma set `L(s)` and cleaned,
  tokenized, lemmatized gloss token set `D(s)`: first remove self-reference,
  `D'(s) = D(s) \ L(s)`; then add a directed edge **u → w for every u ∈ D'(s), w ∈ L(s)**.
  Reading: **u → w means "u is used in a definition of w" (definer → defined).**
  Deduplicate across synsets (simple digraph, no multi-edges, **no self-loops by
  construction**; removed self-reference tokens are counted, `selfRefCount`).
- **Degree covariates** (computed once, frozen with the graph):
  `outdeg(u) = |{w : u→w}|` (how many words u helps define — the "definition frequency"
  used for null matching, §5.2) and `usage(u) = |{s : u ∈ D'(s)}|` (synset-level usage
  count, the sensitivity covariate).
- **Undefined nodes:** a node whose every gloss cleaned to the empty set has no in-edges;
  counted (`undefinedNodeCount`) and reported; excluded from no computation (they simply
  sit outside the Kernel).

## 4. Kernel / Core / Satellites / MinSets (the 2016 method, operationalized)

**4.1 Kernel.** Repeatedly delete every vertex with out-degree 0 in the current induced
subgraph ("not used in any other remaining definition"), until fixpoint. The fixpoint is
the **Kernel** K. This reduction is confluent (order-irrelevant; unique fixpoint —
Blondin Massé et al. 2008); the implementation uses a worklist queue, O(V+E).
Equivalently: K is the maximal induced subgraph in which every vertex has out-degree ≥ 1.
Runtime assertion: every directed cycle of G lies inside K (any counterexample is a bug;
fail closed).

**4.2 Core and Satellites.** Compute the strongly connected components of the subgraph
induced on K (iterative Tarjan — 10^5 nodes exceeds Python's recursion limit; pinned
iterative). The **Core** is the largest SCC by node count (tie-break, deterministic:
the SCC containing the lexicographically smallest lemma; ties reported). **Satellites**
= K \ Core (the smaller SCCs and inter-SCC connective tissue inside the Kernel — the 2016
paper's usage; note the ladder's one-line paraphrase differs, the paper's definition is
binding). **Rest** = V \ K. Sanity check: every defined node in Rest is reachable from K
along definition edges (violations counted; expected 0 apart from undefined-node chains).

**4.3 Sanity corridor (construction-anomaly gates, NOT endpoints).** The 2016 paper
found Kernel ≈ 10% of the dictionary, Core ≈ a large fraction of the Kernel, MinSets ≈ 1%.
Before any NSM statistic is computed, the run halts with verdict
`CONSTRUCTION-ANOMALY` (investigate, amend §9, re-run) if any of:
`|K|/|V_sw| ∉ [0.01, 0.40]`; `|Core|/|K| < 0.20`; Core is not unique-largest by ≥ 2×
over the second SCC; or the cycle-containment assertion fails.

**4.4 Grounding sets / MinSets.** Per Blondin Massé et al., a set G ⊆ V grounds the
dictionary iff the subgraph induced on V \ G is acyclic (then every word outside G is
learnable in topological order); minimum grounding sets are exactly minimum **feedback
vertex sets** (FVS) of the graph, and since all cycles lie in K, of the Kernel subgraph.
MFVS is NP-hard and MinSets are **not unique** ("every dictionary has a huge number of
MinSets" — 2016); we therefore **sample many inclusion-minimal grounding sets** and say
"MinSet" for these, with the approximation caveat carried through all reporting
(threat T5). Pinned sampler, one run per seed σ ∈ {0, …, 999} (**N_MS = 1000**), PRNG =
`random.Random(σ)`:

1. H ← Kernel subgraph; F ← ∅. (Defensively: any self-loop vertex → F; none should exist.)
2. **Trim:** exhaustively delete vertices with in-degree 0 or out-degree 0 in H (they lie
   on no cycle).
3. If H is empty → step 5. Else compute SCCs of H; discard singleton SCCs; within each
   non-trivial SCC, greedily pick the vertex maximizing
   `(indeg(v) + u_v) · (outdeg(v) + u_v)` with `u_v ~ Uniform(0,1)` drawn from the seeded
   PRNG (the classic degree-product FVS heuristic, randomized so different seeds explore
   different MinSets); add it to F, delete it from H, go to 2. (Implementation note:
   recompute SCCs only within the SCC just modified.)
4. — (loop above until acyclic) —
5. **Minimality pass:** for each v ∈ F in seeded-shuffled order, if K \ (F \ {v}) is
   acyclic (Kahn check), remove v from F. Result: an inclusion-**minimal** FVS =
   grounding set. Emit sorted F with its seed.

Deliverables: `m(v)` = fraction of the 1000 samples containing v, for every v ∈ K; the
number of **distinct** sampled sets; size distribution (min/median/max); the exact
intersection `{v : m(v)=1}` and the **near-invariant grounding set** `I₀.₉ = {v : m(v) ≥ 0.9}`
(the operationalization of "MinSet intersection" — the exact intersection of 1000
approximate sets may be degenerate-small, so I₀.₉ is the pre-registered test set, exact
intersection reported descriptively). Checkpoint every 25 samples (box convention).
**Pre-authorized fallback:** after the first 25 samples, if projected total wall-clock
> 24 h, N_MS drops to 300 (recorded in §9 and in the results JSON; `m(v)` resolution
1/300 is ample for the effect sizes at stake). No other N is permitted.

## 5. The NSM test (the crux)

**5.1 Prime → node mapping (frozen now).** Rule: each prime maps to **one** node — the
first allolex exponent (in `lexicon.ts` `~`-order) that, after the §2 token pipeline
(lowercase + Morphy-lite), is a single orthographic word present in the index vocabulary.
Multi-word exponents do not map; two hand adjudications and two homograph exclusions are
pinned in the table below. If two primes map to the same node, the lower `chartIndex`
keeps it and the other is excluded (none expected). Mechanical verification against the
built vocabulary is stage 2 of the run; it may only *remove* rows (discrepancies
reported), never add or remap — the table is frozen.

**Excluded primes (14), with reasons:**

| prime | reason |
|---|---|
| YOU, THIS, BECAUSE, IF | no WordNet entry (closed-class; verified in index files 2026-07-07) |
| DON'T-WANT | negation compound; no single-word exponent |
| BE-SOMEWHERE, THERE-IS, BE-SPEC, IS-MINE | copular / multi-word constructions ("be", "mine" would be wrong-lexeme matches) |
| A-LONG-TIME, A-SHORT-TIME, FOR-SOME-TIME | multi-word duration exponents |
| I | WordNet `i` = the letter / iodine / the numeral — provably not the pronoun (homograph exclusion) |
| CAN | WordNet `can` = container / to preserve / etc. — the modal is absent (homograph exclusion) |

**Evaluable primes (51):** SOMEONE, SOMETHING~THING→`thing`, PEOPLE, BODY, KIND, PART,
THE-SAME→`same` (hand adjudication: the determiner is semantically empty),
OTHER~ELSE~ANOTHER→`other`, ONE, TWO, SOME, ALL, MUCH~MANY→`much`, LITTLE~FEW→`little`,
GOOD, BAD, BIG, SMALL, THINK, KNOW, WANT, FEEL, SEE, HEAR, SAY, WORDS→`word` (via
Morphy), TRUE, DO, HAPPEN, MOVE, LIVE, DIE, WHEN~TIME→`time`, NOW, BEFORE, AFTER, MOMENT,
WHERE~PLACE→`place`, HERE, ABOVE, BELOW, FAR, NEAR, SIDE, INSIDE, TOUCH, NOT, MAYBE,
VERY, MORE, LIKE~AS~WAY→`like`. All 51 verified present in the index files on
2026-07-07. Each row carries a `senseRiskNote` where the WordNet senses of the word form
may diverge from the prime's meaning (e.g. LIKE, TRUE, KIND) — logged, not acted on
(word-form-level analysis; threat T3). **Coverage gate:** if mechanical verification
yields < 45 evaluable primes, the verdict is `INCONCLUSIVE-BY-COVERAGE` (no PASS/FAIL
may be claimed; escalate to X1b).

**5.2 Frequency-matched null.** For each evaluable prime node p with out-degree d_p:
candidate pool = `V_sw` minus all mapped prime nodes, restricted to out-degree in
`[d_p/1.25, d_p·1.25]`; if < 50 candidates, widen the ratio to 1.5, then 2.0 (final width
per prime logged). One null draw = one uniformly sampled control per prime, without
replacement within the draw. **N_null = 10,000 draws**, PRNG `random.Random(42)`.
Out-degree ("how many words does this word help define") is the direct structural
confound between "primes are frequent defining words" and "primes are structurally
privileged"; matching on it is what makes enrichment non-trivial. **Sensitivity null**
(reported, non-binding): same construction matched on `usage(u)` instead; if its verdict
direction disagrees with the primary null's, that is flagged prominently as a caveat in
the report (pre-registered; no verdict change).

**5.3 Statistics.** For the prime set and for every null draw, compute:

| id | statistic | over |
|---|---|---|
| T_core | fraction of the 51 nodes in **Core** | primary |
| T_kern | fraction in **Kernel** | secondary |
| T_ms | mean MinSet-membership rate, `mean(m(v))` (m=0 for v ∉ K) | secondary |
| T_inv | fraction in the near-invariant grounding set **I₀.₉** | secondary |

One-sided empirical p-value per statistic: `p = (1 + #{T_null ≥ T_obs}) / (N_null + 1)`.
Enrichment ratio `ER = T_obs / mean(T_null)` (if `mean(T_null) = 0`, ER = ∞ and the
p-value alone decides). **Multiplicity (house rule, poc-design Common rule 1):** one
primary endpoint; the three secondaries are Holm-corrected at family α = 0.05.

**5.4 Endpoints (all criteria fixed now):**

- **E-core (PRIMARY):** `p(T_core) < 0.01` **and** `ER(T_core) ≥ 1.5`.
  Rationale: the Core is the maximally circular heart where the 2016 paper's
  psycholinguistic privileges concentrate; "base-layer role" minimally means the primes
  live there beyond what their definition-frequency buys.
- **E-kern (secondary):** Holm-corrected `p(T_kern) < 0.05` and `ER(T_kern) ≥ 1.25`
  (the Kernel is larger, matched nulls sit higher; a weaker ratio bar is honest).
- **E-ms (secondary):** Holm-corrected `p(T_ms) < 0.05` and `ER(T_ms) ≥ 1.5`.
- **E-inv (secondary):** Holm-corrected `p(T_inv) < 0.05` and `ER(T_inv) ≥ 1.5`
  (the ladder's "over-represent in the MinSet intersection", on I₀.₉).

An endpoint "holds" only if both its significance and magnitude criteria are met. No
peeking rule: prime↔strata joins happen only inside the `nsm_test` stage, which computes
observed and null statistics in a single pass; nothing upstream prints prime membership.

## 6. Pre-registered verdicts

| verdict | condition | decision binding |
|---|---|---|
| **PASS** | E-core holds AND ≥ 2 of {E-kern, E-ms, E-inv} hold | NSM keeps its base-layer role; hybrid proceeds with NSM base; X6 (basis-size sweep) optional calibration |
| **PARTIAL** | E-core holds with < 2 secondaries; OR E-core fails but E-kern holds at `p < 0.01` and `ER ≥ 1.5` | NSM retained *provisionally*; X6 becomes **mandatory** before the basis is frozen; report names which stratum claim failed |
| **FAIL** | E-core fails AND E-kern fails | basis switches to a dictionary-derived core (Jesse's route wins at the foundation); X6 runs with the dictionary core as default; NSM demoted to authoring vocabulary at most |
| **INCONCLUSIVE-BY-COVERAGE** | < 45 evaluable primes at stage 2 | no basis claim either way; X1b (full Wiktionary) required |
| **CONSTRUCTION-ANOMALY** | any §4.3 gate trips | no NSM statistic is computed; fix, amend, re-run |

**Scope limits (what a PASS cannot license, pre-registered):** word-form-level,
English-only, WordNet-glosses-only. A PASS does not show the 65 primes *suffice* to
explicate anything (that is X6's question), says nothing about NSM universality, nothing
about sense-level structure, and nothing about the 14 excluded primes — notably the
logical/deictic primes, which are exactly the ones a content-word dictionary cannot see.
A FAIL, symmetrically, is a claim about *this* graph's floor, not about NSM as
linguistics. Negative results are first-class deliverables (house rule).

**Deliverable regardless of verdict:** the scaffold graph the hybrid needs — committed
node/edge lists with strata labels and `m(v)` — this is X1-grounding's second output and
survives any verdict.

## 7. Implementation plan

**Environment:** Python 3.9 (verified on box), **stdlib only** (json, gzip, collections,
random, hashlib, argparse). No nltk (absent), no networkx (absent; not needed — Tarjan
and Kahn are ~60 lines iterative). Node ids interned to ints, adjacency as
lists-of-int-lists (~1.5M edges expected; keep RSS < 1 GB). Everything `nice -n 10`
(2 shared cores, live server — `CLAUDE.md` box rules). All JSON output: sorted keys,
newline-terminated (byte-determinism convention). All results committed to the repo
(box is ephemeral).

**Layout (`poc/x1-grounding/`):**

```
PREREG.md            this document (frozen)
build_graph.py       stage 1: parse JSONL + Morphy-lite → graph.json.gz, graph-stats.json
prime_map.py         stage 2: §5.1 table vs built vocab → primes-mapping.json (frozen output)
strata.py            stage 3: Kernel/Core/Satellites/Rest + §4.3 gates → strata.json.gz
minsets.py           stage 4: 1000 seeded MinSet samples → minsets/  (checkpointed shards) + minset-summary.json
nsm_test.py          stage 5: nulls + endpoints → results/x1g-results.json
report.py            stage 6: render results/x1g-report.md (verdict vs verbatim criteria)
smoke.py             self-test (below); must pass before stage 1 runs on real data
fixtures/            toy dictionary + hand-computed expected structures
run_all.sh           nice -n 10, stages in order, refuses to skip smoke, records stage input sha256s
results/             x1g-results.json, x1g-report.md (committed)
```

**Stage order is load-bearing:** `prime_map` (vocabulary lookup only, no structure) runs
before `strata`, so the evaluable-prime list is frozen before anyone can see where words
landed. `run_all.sh` enforces the order and each stage writes the sha256s of its inputs
into its output.

**Smoke/self-test (`smoke.py`), runs first, must pass:**
1. **Toy dictionary fixture** (~12–20 words, committed with hand-computed truth):
   must exhibit a Kernel strictly smaller than the vocabulary, a Core = largest SCC, at
   least one satellite cycle, and **≥ 2 distinct minimal grounding sets**; smoke asserts
   Kernel/Core/Satellites equality with the fixture's expected sets, asserts every
   sampled grounding set is verified grounding (complement acyclic) and minimal, and
   asserts ≥ 2 distinct sets appear across 20 seeds.
2. **Morphy-lite spot checks:** a committed list of ~30 (token → expected lemma) pairs
   including exception-file cases (`men→man`, `wolves→wolf`), detachment cases
   (`running→run`, `abilities→ability`), and expected-OOV function words (`the`, `of`).
3. **Real-slice run:** first 2,000 noun synsets end-to-end (minutes); asserts non-empty
   Kernel, prints a wall-clock projection for stage 4, and re-runs itself to assert
   byte-identical output (determinism).

**Expected wall-clock (2 shared cores, niced):** stages 1–3: ~10 min total (117,791
synsets, ~1.5M edges, linear-time reductions). Stage 4 dominates: est. 2–20 s per sample
(local SCC recomputation) → ~1–6 h with 2 workers over seed ranges; checkpoint every 25
samples; §4.4 fallback if projection > 24 h. Stage 5: minutes (membership lookups over
10,000 draws). Total: well inside the ladder's "days, ~$0, CPU only".

**Outputs:** `results/x1g-results.json` (input sha256s, census, corridor gates, strata
sizes, MinSet size distribution + distinct count, per-prime rows {prime, node, outdeg,
kernel, core, m(v), flags, matched-bin width}, all four T statistics with null means/95th
percentiles/p-values/ERs, Holm decisions, verdict string) and `results/x1g-report.md`
(the same against the verbatim §5.4/§6 criteria, plus the 2016-shape comparison table
and the caveat log). Encoder note: X1-grounding touches no encoder code; no
`ALGORITHM_VERSION` implications.

## 8. Threats to validity (named now, logged in the report)

- **T1 — WordNet glosses are not a full dictionary.** No closed-class entries (14 primes
  excluded, skewed toward NSM's logical/deictic primes), telegraphic gloss style,
  synonym-sharing glosses. *Mitigation:* verdict scoped to the content-word floor (§6);
  the excluded-prime list printed in the report; optional **X1b** = same pipeline over a
  full Wiktionary dump (dump URL + sha pinned at download time as a §9 amendment; the
  only new analysis licensed is re-testing the 14 excluded primes + replication of the
  four endpoints; X1b cannot overturn an X1 verdict, only annotate it).
- **T2 — Lemmatization noise.** Morphy-lite has no POS tagger; wrong resolutions create
  spurious edges. *Mitigation:* smoke spot-checks; OOV rate + top-100 OOV list reported;
  pre-registered audit — 100 random (gloss token → lemma) resolutions sampled with seed
  7, manually audited by the builder, error rate in the report; if > 10% the run halts
  for a §9 amendment before the NSM test.
- **T3 — Primes are word forms, not senses.** `like`/`true`/`kind` match on form while
  WordNet's senses may skew elsewhere; conversely `i`/`can` were excluded as provable
  homographs but softer cases remain. *Mitigation:* per-prime `senseRiskNote` frozen in
  §5.1; the two provable homographs excluded a priori; sense-level replication deferred
  (would require sense-tagged glosses — out of scope, noted for X6).
- **T4 — Sense-collapse inflates connectivity** (union of glosses per word). Affects
  primes and matched controls identically (matching is on the collapsed graph's
  out-degree); senses-per-node distribution reported.
- **T5 — Sampled minimal ≠ minimum grounding sets.** The greedy FVS is a heuristic;
  sizes are upper bounds. *Mitigation:* primes and nulls are scored against the *same*
  sample of sets, so membership-rate comparisons are unbiased w.r.t. the approximation;
  sizes labelled "approximate" everywhere; every emitted set is verified grounding +
  inclusion-minimal by construction (step 5).
- **T6 — Null-matching granularity.** Out-degree matching may under- or over-control.
  *Mitigation:* sensitivity null on `usage(u)` (§5.2); per-prime final bin widths
  published; disagreement between nulls flagged, verdict bound to the primary null only.
- **T7 — Analyst degrees of freedom.** *Mitigation:* this document; frozen prime table
  that verification can only shrink; single primary endpoint; Holm on secondaries;
  no-peeking stage order; amendments only via §9 before unblinding.

## 9. Amendments

*(any entry here must be dated, signed with its reason, and written before
`nsm_test.py` first runs on the full graph; pre-authorized: the N_MS→300 fallback of
§4.4, which must still be recorded here when triggered.)*

**Amendment 1 — 2026-07-07 — Kern (builder). Smoke spot-check expectations
hand-derived from the frozen §2.3 rules; two §7 illustrative examples superseded.
Zero effect on graph construction or the NSM analysis.**
§7's smoke item 2 lists illustrative (token→lemma) examples "men→man" and
"running→run". Under the *frozen* §2.3 rule order (exact-match in the index vocabulary
is step 1, before exception and detachment), `men`, `teeth`, `running`, `words`, `ate`,
and `better` are **themselves** WordNet 3.1 index lemmas (verified in `index.noun`/`.adj`/
`.verb`/`.adv` on 2026-07-07: e.g. `men`=workforce, `ate`=the goddess Atë, `better`=n/v/a/r),
so exact-match-first correctly resolves each to itself. The committed
`fixtures/morphy_spotchecks.json` therefore encodes the true frozen-pipeline behaviour
(`men→men`, `running→running`, `ate→ate`, `better→better`) rather than the §7 illustrative
strings, and includes clean exception cases (`wolves→wolf`, `mice→mouse`, `geese→goose`,
`feet→foot`, `children→child`, `went→go`) and clean detachment cases (`dogs→dog`,
`boxes→box`, `abilities→ability`, `walks→walk`, `helped→help`, `jumped→jump`). This is a
smoke-fixture clarification only; §2.3 is unchanged and the graph pipeline is unaffected.
Smoke passes 34/34 spot checks + toy fixture (7 distinct minimal grounding sets) + 2000-noun
determinism slice.

**Amendment 2 — 2026-07-07 — Kern (builder). T2 lemmatization audit HALT
(§8): audit error rate exceeds the pre-registered 10% ceiling; `nsm_test.py` NOT run;
remediation escalated to the coordinator.**
The pre-registered T2 audit (100 (gloss-token→lemma) resolutions, seed 7, population
854,458; `t2-audit-sample.json`, `t2-audit-result.json`) was manually audited. Error
rate = **17/100 (17%)** under the strict reading and **12/100 (12%)** counting only
closed-class function words; **both exceed the 10% gate**. Errors are dominated by a small,
enumerable set of function words that are rare WordNet content-homograph lemmas
(`in`, `or`, `as`, `by`, `so`, `an`) surviving §2.4's mechanical OOV drop-out (`or` alone
5× in-sample), plus a few inflections kept unreduced by exact-match-first
(`made`, `making`, `being`, `based`). Per §8 ("if > 10% the run halts for a §9 amendment
before the NSM test"), the run is **halted before `nsm_test.py`**. The natural remediation
— a minimal pinned closed-class stoplist, or POS-restriction — conflicts with §2.4's
*pinned* "No stopword list" decision, so it is a coordinator design call, not a unilateral
builder change. Stages 1–3 (graph, prime-map, strata) and the §4.3 corridor gates all
completed and PASSED (no CONSTRUCTION-ANOMALY); those artifacts and the scaffold graph
stand regardless. nsm_test and stage-4 MinSets are held pending the coordinator's decision
so compute is not spent on a graph that may be rebuilt.

**Amendment 3 — 2026-07-07 — coordinator decision (Option B) + Kern
(builder). Pinned closed-class definer stoplist resolves the T2 halt. Written
BEFORE `nsm_test.py` runs (no-peeking still binds; the builder saw no nsm_test output
before this fix was frozen).**

*Reasoning (coordinator, recorded per instruction):* the function-word homographs
(`in`, `or`, `as`, `by`, `so`, `an`, `of`, `the`, `to`, `a`, `and`, …) are **not merely
symmetric noise**. As very-high-out-degree hubs they inflate the Core and can distort
**where** the strata boundaries fall — and the strata are precisely what the primes are
tested against. Amendment-2's Option-A self-cancellation argument protects the null
comparison but **not** the strata definitions; Option B protects validity, not just
tidiness. This is also almost certainly why |K| came out 23.6% vs the 2016 paper's ~10%
and why the Core is a 17,393-node monster that makes MinSets infeasible — so B additionally
unblocks stage 4.

*Spec (amends §2.4):*
1. **Pinned closed-class stoplist**, applied to **definer (definition) tokens only**,
   at the tokenized surface-form level (post-lowercase, post-possessive-strip). Source:
   the **NLTK English `stopwords` list (179 entries)** — a standard published list
   (articles, prepositions, coordinating/subordinating conjunctions, pronouns,
   auxiliary/modal verbs, particles, high-frequency determiners) — transcribed **verbatim**
   into `x1g_lib.STOPLIST_STANDARD` and chosen **once, blind** to any downstream statistic
   (not tuned to the audit sample or the NSM result). Verbatim list:
   `i, me, my, myself, we, our, ours, ourselves, you, you're, you've, you'll, you'd, your,
   yours, yourself, yourselves, he, him, his, himself, she, she's, her, hers, herself, it,
   it's, its, itself, they, them, their, theirs, themselves, what, which, who, whom, this,
   that, that'll, these, those, am, is, are, was, were, be, been, being, have, has, had,
   having, do, does, did, doing, a, an, the, and, but, if, or, because, as, until, while,
   of, at, by, for, with, about, against, between, into, through, during, before, after,
   above, below, to, from, up, down, in, out, on, off, over, under, again, further, then,
   once, here, there, when, where, why, how, all, any, both, each, few, more, most, other,
   some, such, no, nor, not, only, own, same, so, than, too, very, s, t, can, will, just,
   don, don't, should, should've, now, d, ll, m, o, re, ve, y, ain, aren, aren't, couldn,
   couldn't, didn, didn't, doesn, doesn't, hadn, hadn't, hasn, hasn't, haven, haven't, isn,
   isn't, ma, mightn, mightn't, mustn, mustn't, needn, needn't, shan, shan't, shouldn,
   shouldn't, wasn, wasn't, weren, weren't, won, won't, wouldn, wouldn't`.
2. **Evaluable-prime guardrail (load-bearing, asserted in `definer_stoplist()`):** the 51
   frozen evaluable-prime node forms are **subtracted** from the stoplist before it is
   applied, so the filter can never remove a node under test. The 14 protected forms that
   the standard list would otherwise have removed: `same, other, some, all, do, now, before,
   after, here, above, below, not, very, more`. Applied stoplist size = 179 − 14 = 165.
3. **Node vocabulary unchanged** (still the WordNet index); only edges *out of* stoplisted
   definer tokens are suppressed. A stoplisted word can still be *defined* (retain in-edges).
   `graph-stats.json` reports `stoplistDroppedTokenCount` and edge/|K|/Core deltas.

*Procedure:* rebuild stages 1–3; **re-run the T2 audit** (seed 7, 100 samples). If it still
exceeds 10%, STOP and report (do NOT force). Otherwise proceed to stage 4 (with the
§4.4 incremental-SCC sampler and, if needed after the first 25 samples, the pre-authorized
N_MS→300 fallback) and `nsm_test`.

*Outcome (2026-07-07, Kern):* post-stoplist T2 re-audit = **5% < 10%** (gate passed;
`t2-audit-result.json` v2). Rebuilt census: 403,059 definer tokens suppressed, edges
1,405,063 → 1,175,680. **Notable:** the stoplist barely moved the strata — |K| 19,617 →
19,559, |Core| 17,393 → 17,324 (still 88.6% of K; all four §4.3 gates still pass). The
giant strongly-connected Core is therefore a genuine **content-word** phenomenon, robust to
closed-class removal — not an artifact of function-word hubs (the Amendment-3 core-inflation
hypothesis is not borne out, though the stoplist remains correct for T2 validity and removes
the spurious edges). nsm_test proceeds.

**Amendment 4 — 2026-07-07 — Kern (builder). Pre-authorized N_MS→300 fallback
(§4.4) invoked, and the two-worker plan reduced to one niced worker.**
Benchmarking the §4.4 sampler on the post-stoplist Kernel (19,559 nodes / 251,543
kernel-induced edges, Core 17,324) gives **≥ ~200 s CPU per grounding-set sample**: the
degree-product heuristic must re-decompose the persistent 17k-node Core after essentially
every removal (the "recompute only within the modified SCC" optimization does not help a
monolithic Core — an inherent property of *this* graph, not an implementation defect; the
neighbour-sort and per-SCC-sort hot paths were removed for a constant-factor win). At that
rate **N_MS=1000 ≈ 55 h ≫ 24 h**, so the pre-authorized fallback to **N_MS=300** is invoked
now (m(v) resolution 1/300 is ample for the effect sizes at stake, per §4.4) and recorded in
`x1g-results.json`. Additionally, the box is at **load average ~17 on 2 shared cores** with a
live server + a running agent fleet (CLAUDE.md), so the §4.4/§7 "2 workers" plan is reduced
to **one `nice`-d detached worker** over seeds 0–299, checkpointing every 25 (resumable), to
avoid starving the server. E-core/E-kern (the PRIMARY endpoint) need only stages 1–3 and are
computed immediately; the MinSet secondaries (E-ms, E-inv) follow when stage 4 completes.
