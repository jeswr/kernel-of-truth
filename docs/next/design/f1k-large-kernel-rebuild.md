# F1-K powered rebuild on the large-kernel — build-ready design (GPT-5.6, coordinator-transcribed)

> Implements the maintainer-authorized sequence (issue #33). GPT-5.6 (codex, xhigh) design, transcribed
> by the coordinator; a Fable builder executes it. Fold in the steering read's pre-spend deflator gate
> (docs/next/analysis/steering-read-2026-07-13.md §4.2) before the main campaign.

# F1-K large-kernel rebuild design

**Status:** design for a new, confirmatory F1-K successor authorized under issue #33. It does not amend the completed inventory finding for kernel-v0 and makes no programme-level feasibility decision.

The successor retains the registered F1-K endpoints, \(n=1{,}440\), \(\rho_U=0.10\), +3-point SEOI, cluster-balanced estimand, K-1/K-2 licensing rule, and 10,000-draw cluster sign-flip analysis. Its scientific population is the selected kernel-v1 concept set, not kernel-v0 and not the entire approximately 207k-record source pool.

## 1. F1-K concept eligibility

A concept is F1-K-eligible only if all three gates below pass. Materialize one row per candidate in `data/kernel-v1/f1k-eligibility.jsonl`, including every pass/fail field and exclusion reason. Do not grandfather kernel-v0 concepts: its README explicitly describes adequacy as unvalidated and marks known-weak records.

### 1.1 Scholarly explication gate

Each eligible concept must have a `data/kernel-v1/concepts/<slug>.json` record in the kernel-v0 shape:

```text
{id, label, status, pattern?, gloss, notes?, references, explication}
```

Here, `gloss` is the exact K-carrier and d3-text content. `explication` is its corresponding `kot-ast/1` structural record.

A `gloss` passes the scholarly-definition standard only when:

1. It defines exactly one sense and the same intension as the aligned WordNet synset.
2. It states a superordinate category and distinguishing condition(s), or the corresponding explicit argument/condition structure for a relation, event, quality, or process.
3. It is non-circular: the label or a morphological variant cannot be the sole defining content.
4. It separates defining conditions from examples, typical effects, symptoms, etymology, or usage notes.
5. It is self-contained scholarly prose: no unresolved ontology identifiers, unexplained abbreviations, benchmark-specific wording, or unsupported claims.
6. It is source-backed. Record source identifier, version, license, source-definition hash, and whether the text is reused, lightly edited, or newly authored.
7. It is concise enough for stable carrier construction: normally one to three sentences, 15–100 words, and no more than 128 tokens under the pinned GLM-5.2 tokenizer. A justified exception must be recorded before freeze.
8. Its `kot-ast/1` record expresses the same meaning, passes grammar/valency/referent/cap checks, has an acyclic and fully resolved reference graph, and encodes without NaNs or norm failure.
9. It is not marked `KNOWN-WEAK`.

Mechanical checks:

- Parameterize `data/validate.mjs` to accept `--kernel data/kernel-v1`; run per-record `validateExplication`, whole-corpus `encodeConceptSet`, reference/manifest cross-checks, and vector sanity.
- Reject an eight-token-or-longer contiguous overlap between `gloss` and any evaluation question/option after removing the concept’s own trigger phrase and stopwords. This is a leakage check, not a semantic score.
- Hash the final UTF-8 `gloss` and `explication` object separately.

Human check:

- A human reviewer sees the label, proposed definition, aligned WordNet gloss/synset, cited source, and structural rendering, but not coverage rank, matched benchmark items, or model outputs.
- The reviewer answers four binary questions: same sense; intension accurate; scholarly/self-contained; AST and prose semantically consistent.
- All four must be yes. A no causes revision and a new review; unresolved cases are excluded.

### 1.2 Clean WordNet-3.1 alignment gate

Create `data/lexical-wn31/alignment-kernel-v1.json` using `kot-lex-align/1`. Every active concept must have exactly one alignment row and no active concept may appear in `unaligned`.

A clean alignment requires:

1. `synset` matches `urn:lexical-wn31:[nvar]-[0-9]{8}` and exists in the pinned WordNet shards.
2. `lemma` occurs in that synset, after the existing underscore/space and case normalization.
3. POS agrees with the target synset.
4. The concept definition and synset identify the same referent and construal, not merely the nearest lexical neighbor.
5. Confidence is at least 0.85, using the existing alignment file’s definition of “high.”
6. The human alignment reviewer records an affirmative exact-sense judgment. Notes such as “nearest available,” “different referent class,” or “granularity differs” fail this gate.
7. Two active concepts may not map to the same synset. Merge them into one concept cluster or exclude one before coverage allocation.
8. The alignment validator confirms target existence and lemma membership. Refactor `extractor/align.mjs validate` to accept an alignment path rather than hard-coding kernel-v0.

WordNet-origin candidates use their source synset as the initial anchor, but the authored/reused `gloss` must still be reviewed against it. OBO, SUMO, and FrameNet candidates require a reviewed crosswalk to a WordNet synset before they can enter F1-K.

### 1.3 Evaluation-coverage gate

“Known-concept item” retains the existing mechanical meaning from `build_corpora.py`:

- Use the same pinned MMLU, ARC-Easy, ARC-Challenge, OpenBookQA, and CommonsenseQA snapshots and splits.
- Expand surfaces from the aligned WordNet synset’s lemmas and derivational `+` pointers.
- Match case-insensitive whole words over the frozen question-plus-options template.
- Resolve overlaps by longest trigger, then earliest start, then lowest final concept index.
- Assign each item to the concept owning its first resolved span.
- Preserve published option order; multi-concept and option-trigger remain tags, not alternative cluster assignments.
- Allocate dev-96 first by the existing round-robin rule.
- Allocate test to \(m=8\) breadth-first, then round-robin to exactly \(n=1{,}440\).
- Guard-60 contains zero-trigger items and contributes no coverage.

A concept passes only if its realized final **test** count is \(m_c\ge8\). Dev and guard items do not count. The check is made from the emitted test rows after joint overlap resolution and split allocation, not from raw lexical-hit counts.

`f1k-eligibility.jsonl` must record at least:

```text
concept_id
wn31_synset
definition_mode and source
gloss_sha256
ast_valid
definition_review_id/pass
alignment_confidence
alignment_review_id/pass
raw_unique_hits
resolved_hits
n_dev
m_test
eligible
exclusion_reason
```

## 2. Selecting concepts from the approximately 207k pool

The scale census’s 207,733 figure is an unmerged upper bound: 110,049 WordNet type-level synsets, 95,201 OBO classes, and 2,483 SUMO classes. Cross-source duplicates have not been removed. It must not be treated as 207,733 independent F1-K clusters.

### 2.1 Canonical candidate key and filtering

Use the WordNet-3.1 synset as the F1-K candidate key. OBO, SUMO, and FrameNet records enrich that candidate with definitions, formal structure, valency, or provenance; they do not create an additional cluster when crosswalked to the same synset.

Build `data/kernel-v1/selection/candidate-inventory.jsonl` as follows:

1. Start from WordNet’s 110,049 type-level synsets.
2. Exclude named-individual/instance synsets, malformed/no-lemma records, and records lacking a usable trigger after the existing expansion.
3. Join exact source crosswalks and xrefs from OBO, SUMO, and FrameNet.
4. Admit a non-WordNet record only after a clean reviewed WordNet crosswalk.
5. Merge all records sharing a WordNet synset into one candidate row.
6. Preserve every source ID and definition; do not silently choose among conflicting definitions.
7. Record source and domain composition descriptively. F1-K does not inherit SCALE-1’s million-concept or domain-balance claim.

FrameNet supplies frames and argument structure, not definitions. SUMO supplies a reusable definition only where a genuine definitional biconditional can be rendered and reviewed. Neither source alone satisfies the explication gate.

### 2.2 Coverage screening before authoring

Add a non-writing `--coverage-only` mode to `build_corpora.py`. It should accept the candidate inventory and alignment without requiring kernel explications.

The screening mode must:

1. Build provisional triggers exactly as the final builder does.
2. Read a redacted benchmark view containing item ID, source, question, and options—but no gold answer and no model output.
3. Scan the 19,311-source-item pool once using an inverted trigger index.
4. Emit per candidate:
   - unique matched items;
   - stem matches;
   - option-only matches;
   - exclusive matches;
   - collision/multi-concept counts;
   - per-source counts.
5. Simulate the exact dev/test allocator jointly over candidate sets so authoring decisions use projected `m_test`, not raw hits.

No baseline, K, derangement, pilot, or other model score may exist at this stage.

### 2.3 Deterministic selection order

Freeze this ordering before running the screen:

1. Higher projected final `m_test`.
2. Higher exclusive stem-match count.
3. Higher exclusive total-match count.
4. Lower trigger-collision fraction.
5. Existing source definition already eligible for reuse, then light-edit candidate, then fresh-authoring candidate.
6. WordNet synset URN byte order.

Process candidates in that order. Tentatively add each candidate, sort the tentative set by final concept URN, and rerun the exact overlap and split allocation. Retain it only if it has \(m_{\text{test}}\ge8\) and does not make an already retained candidate fall below eight.

Target **96 active concepts**, matching the frozen high-headroom planning geometry. Freeze only in the 80–100 range and only after both power confirmations in Section 4 pass. Keep the next 30 coverage-qualified candidates as an ordered reserve. If definition or alignment review rejects a candidate, backfill from this reserve without changing the ordering.

If fewer than 80 accepted concepts remain, continue down the already frozen reserve ordering. Do not lower the definition/alignment bar or inspect model results. The registered absolute floor remains \(C\ge65\), but 65–79 does not provide the headroom authorized for this rebuild and should return to selection rather than be frozen as the intended successor.

Coverage selection is benchmark-text-aware but outcome-blind. Its claim population must therefore be described as “the preselected, coverage-qualified kernel-v1 concept set,” not a random sample of WordNet, OBO, or the 207k pool.

## 3. Explication sourcing and quality control

Perform sourcing only after coverage screening. Authors and definition reviewers should receive concept/source packets, not matched evaluation items.

### 3.1 Reuse classes

**Direct reuse — permitted**

An OBO natural-language definition may be copied verbatim into `gloss` when:

- the concept has a clean WordNet alignment;
- the definition is source-asserted and versioned;
- its genus and differentiae are explicit;
- it matches the OBO logical definition where one exists;
- it passes the complete scholarly and human-review gate.

A source-authored SUMO definition may be treated the same way when it is genuinely definitional rather than a loose axiom or comment.

**Light edit — still reviewed as authored output**

An OBO logical genus–differentia expression may be deterministically rendered using pinned labels, but automatic verbalization does not itself meet the bar. It requires human editing or approval and is recorded as `light-edit`, with both source and final hashes.

A WordNet gloss with examples, semicolon fragments, circular wording, or missing category information normally falls here or in fresh authoring.

**Fresh kernel-standard explication required**

Use Fable to author new prose and `kot-ast/1` when:

- only a short WordNet dictionary gloss is available;
- source definitions conflict;
- the source is lexical/axiomatic rather than definitional;
- technical context is needed to state the correct intension;
- an automatic rendering fails the scholarly gate.

### 3.2 Protecting the d2 control

The current corpus builder uses the aligned WordNet gloss as d2. Therefore a WordNet gloss cannot also be reused verbatim as K content without collapsing K and d2.

Default rule for this rebuild:

- retain the aligned WordNet gloss as d2;
- permit direct K reuse primarily from independently sourced OBO/SUMO definitions;
- require `sha256(K_text) != sha256(d2_text)` for every active concept;
- treat WordNet-only candidates as requiring a fresh or materially completed K explication.

A WordNet gloss may be reused as K only if the successor first pins a different, independently sourced plain-dictionary d2 definition for that concept. That alternative must pass its own accuracy gate before any authoring. The builder must never resolve a K/d2 collision after observing outcomes.

### 3.3 Expected load

For a 96-concept active set, use this planning band until the coverage screen measures the actual mix:

- 15–30 direct OBO/SUMO reuses;
- 10–20 light edits of source definitions;
- 45–70 fresh scholarly explications;
- all 96 still require a validated `kot-ast/1` record or an explicitly reviewed carried-forward record.

Keep reserve candidates source-screened, but do not author all 30 reserves initially. Author them in frozen rank order only as replacements are needed.

Every active concept receives:

1. Fable authoring or source-adoption pass.
2. Mechanical AST/corpus validation.
3. Human definition review.
4. Human WordNet-alignment review.
5. Revision and re-review on any failure.

A practical human-review allowance is approximately 20–35 hours for 96 concepts including revisions. This is a planning estimate, not a fixed cost claim.

## 4. Corpus, power, carrier, and token pipeline

### 4.1 Build kernel-v1 and successor corpora

Do not overwrite the existing inventory-shortfall artifacts. Produce successor-namespaced corpora such as:

```text
data/kernel-v1/
data/f1k-trigger-map-v2/
data/f1k-eval-v2/
data/f1k-carriers-v2/
```

`kernel-v1` may preserve kernel-v0 records, but `build_corpora.py` must accept a hashed `f1k-eligible-concepts.json` allowlist so only concepts passing Section 1 enter triggers, evaluation allocation, and carrier slots.

Refactor hard-coded kernel-v0 assumptions in `build_corpora.py` into arguments:

```text
--kernel
--alignment
--eligible-concepts
--trigger-output
--eval-output
--carrier-output
--coverage-only
```

Retain unchanged:

- benchmark snapshot revisions and hashes;
- template rendering;
- WordNet lemma/derivational expansion;
- matching and overlap precedence;
- dev/test/guard allocation;
- \(n=1{,}440\), dev-96, guard-60;
- canonical concept ordering;
- registered derangement seeds 101, 102, 103 and pilot seed 11.

Fail closed unless:

- every active concept has one clean alignment and nonempty trigger set;
- every active concept has \(m_{\text{test}}\ge8\);
- \(80\le C\le100\), with the absolute registered gate \(C\ge65\);
- test \(n=1{,}440\) exactly;
- all emitted IDs are unique and splits are disjoint;
- template header, cue, and labels are trigger-free.

### 4.2 Recompute exact-test power for K-1 and K-2

Implement a dedicated, deterministic power tool, preferably by extracting the sign-flip implementation from `analysis/f1k.py` into shared code. Pin its code hash and canonical output.

Use the final realized cluster-size vector \((m_1,\ldots,m_C)\), not a balanced mean. Frozen inputs remain:

```text
delta = 0.10
rho_u = 0.10
mu_star = 0.0409
N_sim = 10000
B_signflips = 10000
alpha = 0.05 one-sided
effect floor = 0.03
global seed = 20260713
```

For each outer simulation and contrast, use the frozen Gaussian random-intercept planning model:

\[
X_{cir}=\mu^*+\sqrt{\delta\rho_U}\,Z_c+
\sqrt{R\delta(1-\rho_U)}\,\epsilon_{cir},
\]

with independent standard-normal \(Z_c,\epsilon_{cir}\). Set \(R=1\) for K-1. Set \(R=3\) for K-2 and form

\[
X_{ci}=R^{-1}\sum_{r=1}^R X_{cir},
\]

which explicitly exercises the registered K-versus-mean-of-three contrast while preserving final contrast variance \(\delta\) and ICC \(\rho_U\). Then calculate \(D_c=m_c^{-1}\sum_iX_{ci}\) and \(T=C^{-1}\sum_cD_c\).

For each simulated dataset:

1. Run the same 10,000-sign cluster-flip code path as licensing.
2. Use deterministic contrast-specific sub-seeds.
3. Apply the add-one correction.
4. Record a joint fire iff \(p<0.05\) and \(T\ge0.03\).

Emit separate K-1 and K-2 blocks with joint power at 4.09 points, Monte Carlo standard error, the realized \(C,m_c\), and the smallest 0.01-point grid value attaining 80% power using common random numbers.

The successor’s “properly powered” readiness gate is:

```text
inventory: C >= 65 and every m_c >= 8 and n == 1440
headroom target: 80 <= C <= 100
K-1 exact-test joint power at 4.09 points >= 0.80
K-2 exact-test joint power at 4.09 points >= 0.80
```

If either power value is below 0.80, add concepts or rebalance using only the frozen reserve ordering and rerun the model-free corpus/power build. Do not change \(\mu^*\), \(\delta\), \(\rho_U\), the SEOI, or \(n\).

This makes the two-contrast ≥0.80 requirement a successor strengthening. The current `f1k.json` describes its single Monte Carlo check as reporting-only; the successor registry must state the strengthened gate explicitly rather than attributing it retroactively to the old record.

The Monte Carlo remains planning evidence. Licensing still uses observed K-1/K-2 lifts and the registered test or preselected BCa fallback.

### 4.3 Carrier construction

After the concept/evaluation/power freeze, complete freeze-manifest (A):

- final eligible concept and carrier-slot map;
- exact \(m=16\) construction contexts per concept;
- evaluation-disjointness proof;
- K and d2 text plus hashes;
- prepend separator and gated-position rule;
- exact candidate splice-layer union;
- construction, pilot, d0, and derangement seeds;
- mean-difference and norm-rescaling algorithms.

Run the colibri forward-pass construction campaign. For each concept and construction context, obtain:

1. no-definition hidden states;
2. K-explication-prepended hidden states;
3. d2-definition-prepended hidden states.

The no-definition pass may be shared. Dump all candidate layers in the same pass where supported. Construct:

\[
v^K_{c,l}=\operatorname{mean}(h^{K}_{c,l}-h^{none}_{c,l}),
\qquad
v^{d2}_{c,l}=\operatorname{mean}(h^{d2}_{c,l}-h^{none}_{c,l}).
\]

Generate d1 from fixed-point-free permutations of K with seeds 101–103, and d0 from the frozen seeded random-direction algorithm. Rescale every non-K carrier at each \((c,l)\) to \(\lVert v^K_{c,l}\rVert\). Commit B0 with every table, raw/rescaled norm, construction log, code pin, and corpus hash before the pilot.

At \(C=80\)–100, the explicit K/d2/no-prepend construction is 3,840–4,800 context prefills. Recompute the successor cost ledger from actual calls; do not assume the old ≤3,072 construction estimate without demonstrating equivalent accounting.

### 4.4 Token manifest

After pinning the exact GLM-5.2 tokenizer revision and bytes, derive mechanically:

- `template_tokens`;
- context-dependent single-token `label_token_ids`;
- token-level carrier-slot spans from character spans;
- `d3_template_tokens`;
- tokenizer and derivation-code hashes.

Use the engine’s own prefill tokenization without extra normalization or BOS removal. Fail closed if:

- any answer label is not one token at the answer position;
- char-to-token span projection is ambiguous;
- token-level header/cue/labels acquire a trigger;
- round-trip rendering changes template bytes;
- item counts, IDs, gold indices, or option order differ from the model-independent corpus.

The final eval hash is computed only after these token fields land. Rerun the driver contract check before pilot or test use.

## 5. Pre-registration integrity and freeze ordering

Coverage screening necessarily reads benchmark text; “benchmark-blind” here means blind to model/KaE outcomes and gold-conditioned performance, not blind to the existence of benchmark questions.

Use this ordering:

1. **Rule freeze:** pin source snapshots, candidate filters, WordNet expansion, redacted coverage input, matching, allocation, selection ordering, reserve ordering, definition standard, review forms, and all scripts.
2. **Coverage screen:** run on question/options only. Produce the ordered candidate and reserve lists.
3. **Definition/alignment work:** authors and reviewers do not see matched benchmark items or coverage counts.
4. **Concept freeze F0:** commit the accepted kernel-v1 records, `f1k-eligible-concepts.json`, alignment, review ledger, source provenance, and `kot-corpus-hash/1`.
5. **Evaluation freeze F1:** build and commit trigger map, test/dev/guard IDs, templates, char spans, source locks, coverage report, cluster-size vector, and all model-independent hashes.
6. **Power freeze F2:** run and commit separate K-1/K-2 simulations, code hash, seeds, realized powers/MDEs, and the inventory/headroom gates.
7. **Successor pre-registration:** register a new experiment ID linked to and superseding only the run intent of frozen F1-K. Pin F0–F2, endpoints, inference rules, claims, return paths, and budget. Do not modify the old record into compliance.
8. **Manifest A:** freeze the complete carrier generator and tokenizer derivation rules before the first colibri forward pass.
9. **Construction and B0:** realize and pin carrier tables and norms.
10. **Token addendum:** pin tokenizer-derived eval manifest and final eval hash.
11. **Family-blind dev pilot:** select \((L,g)\), measure bring-up cost, and select sign-flip versus BCa through the registered dev procedure.
12. **Addenda 5/7/6:** commit pilot choice, affordability/semantics, inference method, and remaining run/defer gates.
13. **Test run and analysis:** only now access test-set model outcomes.

At minimum, pin:

- kernel-v1 directory hash and manifest;
- active concept-list and alignment hashes;
- source-definition and review-ledger hashes;
- selection code, redacted coverage input, candidate order, and reserve order;
- trigger map and span-sidecar hashes;
- model-independent and tokenizer-complete eval hashes;
- test/dev/guard ID-list hashes;
- realized cluster-size vector;
- K-1 and K-2 power code/output hashes;
- construction contexts and carrier-generator hash;
- realized carrier tables and raw/rescaled norm hashes;
- tokenizer revision, token-manifest derivation code, and output hash;
- all seeds, thresholds, layer candidates, and cost rules;
- successor registry and analysis-code hashes.

No concept, definition, alignment, trigger, item, or cluster assignment may change after any model or KaE outcome is observed. A necessary change after that boundary requires abandoning the run and minting/refreezing a new successor, not editing this one.

## 6. Effort, sequencing, and ownership

| Sequence | Work | Human touchpoint | Shared or F1-K-specific |
|---|---|---|---|
| 1 | Build WordNet-keyed candidate inventory; exact OBO/SUMO/FrameNet joins; deduplicate source records | Review ambiguous crosswalk rules | Shared with large-kernel scale track |
| 2 | Add coverage-only builder mode; run redacted screen; freeze main/reserve order | None | F1-K-specific |
| 3 | Source definitions; author or adapt scholarly explications and `kot-ast/1` | Mandatory definition and alignment review for every active concept | Kernel asset shared; prioritization is F1-K-specific |
| 4 | Assemble/validate/hash kernel-v1 and eligibility sidecars | Audit failures and revisions | Shared kernel-v1 asset |
| 5 | Rebuild trigger/eval corpora; verify \(m_c\), \(C\), and \(n\) | Optional blind spot-check of trigger-sense fidelity; it cannot inspect model outcomes | F1-K-specific |
| 6 | Run K-1/K-2 exact-test power simulations; backfill only from frozen reserve if needed | None | F1-K-specific |
| 7 | Commit F0/F1/F2 and successor registry; audit pins | Human/coordinator freeze review | F1-K-specific governance |
| 8 | Freeze generator A; construct colibri carriers; commit B0 | Review only anomalous construction failures, without changing concepts/items | F1-K-specific |
| 9 | Derive tokenizer manifest; pilot; freeze addenda | Coordinator checks single-token and span gates | F1-K-specific |
| 10 | Run frozen test campaign and analysis | None until normal result review | F1-K-specific |

Planning effort before model construction:

- candidate/crosswalk and builder refactor: approximately 2–4 agent-days;
- definition/AST work: approximately 5–10 Fable agent-days, dominated by 45–70 fresh records;
- human review: approximately 20–35 hours;
- final corpus, power, and freeze packaging: approximately 2–3 agent-days;
- colibri construction/token/pilot bring-up: approximately 2–4 agent-days plus measured compute time.

Shared SCALE-1 work consists of source inventory, type-level filtering, cross-source identity clusters, provenance/licensing, reviewed WordNet crosswalks, kernel-v1 records, and reusable definition-quality reviews. F1-K must not wait for the 100k/1M scale store, CK-UFO completion, ANN indexing, large-world closure, or domain-balance programme. Conversely, its benchmark-selected 80–100 concepts do not establish those scale-track properties.

Frozen source basis:

- `docs/next/design/f1k-power-shortfall-options.md`: kernel-v0’s 54-concept bound, realized 49/46 coverage, unequal-cluster MDE, and the authorized large-kernel successor path.
- `registry/experiments/f1k.json`: \(n=1{,}440\), \(\rho_U=0.10\), +3 points, \(C\ge65\) with every \(m\ge8\), K-1/K-2 definitions, seeds, sign-flip \(B=10{,}000\), and freeze ordering.
- `poc/glm52-probe/f1k-harness/corpora/build_corpora.py` and its README: trigger expansion, matching, split allocation, carrier generator, and tokenizer derivation contract.
- `data/f1k-eval-v1/coverage-report.json`: 49 realized clusters and 46 with \(m\ge8\).
- `data/kernel-v0/` and `data/lexical-wn31/alignment-kernel-v0.json`: target record/alignment formats and validation semantics.
- `poc/scale/results/scale-s1-census.json` and `docs/next/design/large-kernel-scale-track.md`: source-pool counts, unmerged-upper-bound caveat, semantic-status discipline, and source roles.
- `docs/next/design/glm52-followup-experiment.md`, SHA-256 `9f18e5e09f5c8a2a933f3446697daf5849676447004540398237da7f8e67f2b6`: carrier construction, deflator ladder, scholarly content role, cluster inference, power approximation, Monte Carlo confirmation, and freeze-manifest discipline.

This rebuild tests F1-K on the frozen kernel-v1 covered population. It does not adjudicate kernel-v0, the full large-kernel pool, or the programme’s overall fate.
