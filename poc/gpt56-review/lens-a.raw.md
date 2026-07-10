## Overall verdict

Both value theses are falsifiable in principle, but not yet validly tested at programme level.

- The efficiency thesis is operationalized mechanism by mechanism. `f1` and `f2b-replicate` produce interpretable measurements, but neither establishes general LLM utility beyond text. `f2b-replicate` establishes a benefit from an aligned deterministic acceptance rule on its authored task, not yet a benefit from NSM semantics.
- The correctness thesis is not tested by `l3a` or `a5`; those are implementation/oracle checks. Its real tests are the still-draft `e9-c` and `e9-full`. Those designs currently confound kernel semantics with ordinary structured data plus deterministic validation.
- Consequently, the packet’s honest summary—“**zero demonstrated end-task wins over the kernel-as-text null**”—remains the right programme-level conclusion. The measured `f2b-replicate` lift is not yet an independent end-task win in the required sense.

Pre-registration protects against outcome-driven threshold changes. It does not protect against a wrong construct, endogenous benchmark construction, pseudoreplication, or an inadequate negative control.

## The single weakest inferential link

The weakest link is the claimed circularity break from `f2b-replicate` through `f2b-transfer`, especially the inference that externally endorsed membership labels establish “ground-truth independence.”

The packet already acknowledges that `f2b-replicate` uses membership gold and that `f2b-transfer` retains kernel-rendered answer surfaces. My deeper objection is that `f2b-transfer`’s stage-1 statistic is not a test of independence at all:

> “kill (d) fires — with ZERO GPU — iff the one-sided 95% Wilson LB of A < 0.70.”

Here, \(A\) is agreement between external and membership gold. Low \(A\) can discredit transfer, but high \(A\) cannot distinguish these worlds:

1. The kernel records are semantically correct and independent judges recognize that.
2. The authored item and canonical option expose the same stylistic, lexical, or answer-construction cue that the verifier uses.
3. The task is effectively an answer-key lookup problem, and both humans and verifier recover the same authored key without NSM semantics contributing.
4. Judges recognize familiar NSM-like formulations or regard the most canonical-looking option as authoritative.

Thus the claim that a PASS “removes **exactly one** confound” overclaims. It replaces algebraic identity between verifier and gold with a human/LLM endorsement path, but does not make the criterion independent of the item-generation and answer-rendering process.

More seriously, the shuffled control does not isolate kernel content. It destroys record–item identity. A seed-pinned arbitrary lookup table, a conventional answer-key database, or opaque item IDs attached to the canonical answers would also fail under derangement. Therefore:

> “the verifier lift … is kernel-content-specific”

should be narrowed to “the lift requires the correct record–item alignment.” `g1` may later distinguish NSM content from arbitrary identities, but it rides on `f4`, not the `f2b` chain, and therefore does not rescue the current `f2b-replicate` interpretation.

Concrete false conclusion: suppose NSM explications add no semantic value, but every item has an authored canonical answer stored in a deterministic table. The true table gives a large retry lift; shuffling it gives none; passive prose loses; external judges endorse the canonical answers; and `f2b-transfer` passes. Every registered control can succeed while “kernel semantics caused the lift” is false.

I rank this above the alternatives because:

- The coverage ceiling is principally an external-validity problem; this is an internal construct-validity problem.
- `a5-llm` is narrower and not yet run.
- Small model scale limits extrapolation but does not by itself erase a local causal result.
- `f1` can still be a valid storage result even if its comparator needs repair.
- If this link fails, the programme’s only positive end-task model result reverts to “aligned machine-readable answer-key verification,” leaving no current evidence for either kernel semantics or ground-truth-independent verifier-offload.

## Highest-priority flaws and failure scenarios

### 1. `f2b-transfer-llmproxy`: the probe does not bound the important bias

The packet correctly labels this only a “**weak feasibility proxy**” and explicitly says it “does **not** adjudicate H-TRANSFER vs H-CIRC.” I agree. The remaining problem is that even the weak feasibility reading can be misleading.

The 60-item deranged-gloss probe says the answer is “NONE by construction.” A Sattolo derangement proves only that an item did not receive its own gloss. It does not prove that no other gloss is semantically compatible, especially in a definitional corpus with related, overlapping, or near-synonymous concepts. The probe gold is therefore partly construction-defined again.

It also tests gross mismatch, not the relevant alternative: a semantically false answer written in more canonical or NSM-like form than the correct answer.

Concrete false conclusion: GPT-5.6 rejects obviously unrelated glosses but systematically prefers canonical-sounding wrong near-neighbours. The probe passes, \(A_{1p}\) passes, and programme sequencing treats human transfer as promising even though the exact surface-bias mechanism threatening `f2b-transfer` remains untouched.

Required control: crossed, independently adjudicated near-misses in which semantic correctness and kernel-like style vary independently; position and typography must also be randomized.

### 2. `m0b`, `f2b-*`, `a5-llm`, `l3a`, and `e9-*`: covered-slice selection is not merely narrow scope

The packet already admits that covered-slice-only results lack representativeness. The deeper issue is spectrum bias: the mechanism determining coverage may select cases where the kernel is unusually likely to win.

Coverage can correlate with:

- canonical answerability;
- low ambiguity;
- short definitional relations;
- direct record lookup;
- author familiarity;
- ease of constructing valid distractors;
- baseline-model difficulty.

This can inflate conditional accuracy even if unconditional deployment value is negligible. Narrow envelope language does not solve that causal selection problem.

`m0b` compounds it by measuring content-word token mass on TinyStories, not sense-correct expressibility or task checkability. A word can match a kernel lemma while being used in an uncovered sense. With no manual sense audit, 0.3542 may overstate semantic coverage.

Concrete false conclusion: frequent ambiguous lemmas inflate `m0b`, while the checkable items in `d-qa-*` are precisely the easiest canonical definitions. Conditional verifier accuracy is excellent, but randomly encountered propositions almost never map correctly.

The least-cost repair is a blind, task-specific audit: sample external items before kernel mapping; freeze external gold; run the mapper without seeing gold; then compare covered and uncovered strata on baseline difficulty, ambiguity, domain, answer form, and model-alone accuracy. Report both conditional and unconditional value:
\[
\Delta_{\mathrm{all}}=\Pr(C)\Delta_C+\Pr(\neg C)\Delta_{\neg C}.
\]

This is the direct analogue of avoiding spectrum bias in diagnostic evaluation ([Ransohoff & Feinstein, 1978](https://www.nejm.org/doi/10.1056/NEJM197810262991705), confidence: high; applicability here is analogical but strong).

### 3. `a5-llm`: it compares an LLM with deterministic lookup, not specifically with the kernel

The packet appropriately says `a5` itself licenses “**NO engine-vs-LLM claim**.” `a5-llm` can license such a claim on the pinned slice, but not a kernel-specific differentiator without a conventional deterministic baseline.

Missing controls include:

- SQL/Datalog over the same extracted records;
- a simple AST-index lookup implementation;
- a conventional static-analysis query engine;
- JSON Schema or ordinary integrity constraints for the store violations.

The abstain-all and answer-all brackets do not address this. Nor does the “oracle-strong” RAG arm: that is a strong LLM baseline, but it does not show that an NSM/kernel representation is responsible for the engine advantage.

Concrete false conclusion: any 100-line relational query evaluator answers the closed grammar exactly and cheaply. The engine beats every SmolLM2 cell by >0.10 and >\(10^3\) cost, but the result is “databases beat small LLMs at database queries,” not a kernel result.

The “lenient, pro-LLM” extractor is conservative only for a PASS favoring the engine. It is not conservative for the differentiator kill:

> “any extraction-gate-valid LLM cell within 0.05 (point) of the engine → exactness differentiator dead **regardless of cost**.”

A lenient extractor that accepts vague or underspecified answers can falsely fire that kill. Conversely, an extractor with up to roughly 10% asymmetric errors can affect an accuracy difference of the same size as the >0.10 primary threshold. The gate needs both extraction sensitivity and specificity against blinded human labels, with unparsed outputs counted as wrong rather than removed.

The cost ratio also needs extraction, indexing, oracle retrieval construction, batching, caching, and engine/store authoring on the ledger. Otherwise a >\(10^3\) per-query ratio can be true while the all-in comparison is false.

### 4. `l3a`, `a5`, and `e9-c`: query counts hide very small numbers of independent rule cases

`l3a` has 900 queries but six axiom records. `a5` has 977 queries but five code axioms. Those queries are repeated measurements of very few semantic/rule structures.

Wilson intervals over queries answer “how often did this pinned implementation answer these generated queries?” They do not support generalization across axiom types, query templates, extraction patterns, or codebases. Treating all queries as independent would be pseudoreplication ([Hurlbert, 1984](https://esajournals.onlinelibrary.wiley.com/doi/10.2307/1942661), confidence: high).

Concrete false conclusion: the engine correctly implements five simple rules thousands of times but fails on negation, joins, aliasing, inheritance, or interacting constraints not represented among those five. The nominal Wilson LB exceeds 0.98 while the effective rule-level sample is five.

For `e9-c`, planted violations create an additional alignment problem. If violations are generated by negating the checker’s own authored constraints, high catch rates are nearly guaranteed. The text-diff checker is not the correct negative control; the fair controls are the same decoded facts checked by a conventional validator and a non-NSM structured store using the same constraints.

The statement:

> “checker soundness is model-free and extrapolates without limit”

is unsupported by finite testing. It would require a formal soundness proof over the grammar and rule implementation, plus assumptions about conflict handling and resource bounds. Empirical success on planted cases cannot extrapolate without limit.

### 5. `e9-full`: the design does not isolate kernel structure from structured verification

The gloss-self-verify arm correctly closes the “retry loop alone” loophole. It does not close the “ordinary structure plus deterministic validation” loophole.

Missing arms:

- a conventional typed JSON/relational representation plus the same checker;
- text decoded into a conventional schema, then deterministically checked;
- grammar-constrained record emission without kernel vectors;
- independently authored natural errors, not merely planted violations aligned with the axiom taxonomy.

Concrete false conclusion: any typed schema catches the designated error classes, while prose self-checking does not. `e9-full` passes, but the causal ingredient is machine-readable structure, not NSM grounding or content-addressed vectors.

The required per-error-class breakdown is useful only if the taxonomy and natural-error corpus are frozen by parties who did not author the checker rules. Otherwise the checker can win on the classes chosen to match it.

### 6. `f2b-replicate` and `f2b-transfer`: three seeds are not 750 independent observations

The nominal design is 250 items × three seeds. If the BCa bootstrap resampled 750 item-seed cells independently, its quoted LB is too optimistic because predictions for the same item and model family are correlated. The valid analysis must resample both items and training/inference seeds, or state that inference is conditional on the three pinned seeds.

Three seeds are too few to estimate a population distribution over model initializations reliably. The +15.1-point result is large enough that item-level significance may survive, but the exact LB and “seed-general” interpretation may not.

The same problem recurs in `g2`/`g3` with judgments nested in concepts, and in `l3a`/`a5` with queries nested in axioms/templates.

### 7. `f7`: survivors-only slope estimation is selection-biased and weakly powered

The packet already flags limited rungs. The deeper flaw is “survivors-only” selection. Mechanisms enter `f7` because their earlier estimates were favorable; fitting slopes to those same selected mechanisms induces winner’s-curse and post-selection bias. Ordinary WLS confidence intervals do not account for qualification.

The rule:

> “90% CI lower bound > −0.1”

is permissive for a licensing instrument, and three to five highly correlated rungs in one family are not enough to distinguish linear decay, a threshold, and a plateau. Law 2 makes nonlinearity especially plausible.

Concrete false conclusion: a mechanism passes at small scale because of positive noise, enters `f7`, and regresses toward zero slowly enough over three rungs that its 90% interval excludes −0.1. It is pitched as non-toy despite having no advantage in an independent family or larger host.

Repair: qualification and slope estimation must use independent items/seeds, with the qualification event modeled or a fresh confirmation split. Selective inference exists precisely because ordinary intervals after selection are distorted ([Fithian, Sun & Taylor, 2014](https://arxiv.org/abs/1410.2597), confidence: high).

### 8. `family-h0` and `a-h0`: prospective family control cannot be added after member results are known

`family-h0` remains DRAFT while `f1`, `f2`, and `f2b-replicate` already have known outcomes. Holm correction performed later can mechanically adjust p-values, but it cannot convert a data-informed family definition into prospective confirmatory inference.

Concrete false conclusion: known favorable, unfavorable, or redundant hypotheses influence which hypothesis codes and estimands are counted as the eight members. Holm then reports valid-looking family-wise control even though the family boundary was chosen with outcome knowledge.

The record must either produce a timestamped pre-result artifact fixing the family or be labeled retrospective/descriptive. `a-h0` is defensible as a policy route selector, but it is not itself a scientific test. Its heterogeneous booleans combine storage, model accuracy, verification, and training efficiency under different populations and envelopes.

### 9. `f1` and `f5`: payload equivalence and the comparator class are not established

`f1` compares a KOTK/2 pack with “zstd-19 glosses-only text.” The byte result is interpretable only if both representations are self-contained and preserve an equivalent semantic payload.

Re-minting URNs does not by itself establish recovery of all gloss/explication content. The ledger must include external codebooks, dictionaries, schemas, indexes, sidecars, and decoder tables needed to reconstruct or use the pack.

Missing controls:

- front-coded or dictionary-coded gloss storage;
- succinct trie/minimal-perfect-hash storage;
- a conventional columnar record pack;
- compressed structured records with shared vocabulary factored out;
- the exact byte cost of every external dependency.

Concrete false conclusion: KOTK/2 wins by storing compact identifiers whose meanings reside in an uncounted shared codebook, while the text comparator stores its meanings explicitly.

The envelope:

> “the store-size axis extrapolates freely (B/rec is size-independent)”

overclaims. Compression ratio depends on corpus distribution, duplication, dictionary overhead, and record heterogeneity. It can extrapolate across more records sampled from the same stationary corpus process, not freely across store sizes or domains.

For `f5`, RETRO’s model-size range cannot license the direction of a *kernel-store advantage*. It licenses retrieval as a mechanism, not this representation’s relative effect.

### 10. `f3`, `f4`, `f6`, and `g1`: the identity/geometry controls are incomplete

`g1` has useful random-atom and Numberbatch controls, but it rides on `f4`; it does not validate `f3` or `f6`.

Each needs a topology-matched arbitrary-identity control:

- `f3`: fixed random concept IDs with the same adapter, dimension, norms, and token budget; ordinary learned vocabulary extension; and a compact non-NSM dictionary code.
- `f4`: frozen random IDs plus adapter, not only trained ToolkenGPT embeddings; held-out senses and paraphrases to separate memorized identity from semantics.
- `f6`: frozen random/orthogonal rows and pretrained semantic rows, in addition to shuffled scaffold.
- `g1`: alternative compositional representations with the same grammar and binding topology, not merely a different off-the-shelf embedding space.

Concrete false conclusion: the adapter learns concept identities or benefits from any stable low-dimensional code. True-kernel beats prose and shuffling but does not beat a matched arbitrary codebook. The programme attributes the result to semantic primes.

`f6` also measures only through 160M. Its “≤410M at most” envelope is still an extrapolation on an axis for which the packet says there is “**no anchor at all**.” That should be unlicensed until 410M is measured.

### 11. `g2`, `g3`, and `g9`: human-validation claims use the wrong population or comparator

For `g2`, high precision among emitted Π subsumptions does not establish useful “soundness” broadly. A system can attain >0.9 precision by emitting only obvious relations. Recall/coverage and adversarial hard negatives are required. Human agreement is also not a formal soundness proof.

For `g3`, ~20 concepts—not ~200 judgments—is the relevant unit for generalizing across concepts. Ten near-duplicate instances per concept cannot compensate for sparse concept diversity.

Concrete false conclusion: all sampled concepts belong to simple taxonomic classes and pass necessity, while relational, polysemous, evaluative, or culturally contingent concepts fail. The aggregate Wilson UB remains ≤0.1.

`g9` is not a valid comparative experiment. Comparing a Fable-class author/validator loop with DeepNSM-8B’s published point from another dataset and “self-metric” is cross-study confounding; a ten-point margin does not substitute for common items, prompts, validators, time limits, and adjudication.

Concrete false conclusion: the new validator is simply more permissive or tailored to Fable’s output. The Wilson LB clears DeepNSM by ten points although authoring capability has not improved.

The envelope that authoring capability “extrapolates forward monotonically” is also unsupported. Later models can improve fluency while regressing on schema compliance or reductive adequacy.

### 12. `e8-r`, `e8-d`, `g4`, `g5`, `g6`, `g7`, and `g8`: secondary validity failures

- `e8-r`: replication “on the seed-stable subset” risks selecting features because they already behaved well. Use a frozen holdout concept/feature set. Include alternative structured ontologies and random geometries, not only permutation/shuffle nulls.
- `e8-d`: a linear probe is too weak as the sole downstream baseline. Include regularized nonlinear probes, ordinary embedding-drift detectors, and representation-similarity methods. Planted drift must be authored independently of the kernel labels.
- `g4`: effort and mistranslation require randomized crossover authors, order control, and an external gold interpretation. Otherwise author familiarity decides the winner.
- `g5`: “PASS = no surprise reversal” has no numerical equivalence criterion. Failure to observe an RDM change is not evidence it is unchanged; this conflicts with the programme’s TOST rail.
- `g6`: the packet already notes that the G4-authored set is absent. Until `d-ax` exists, the census cannot license suitability for the programme’s actual authoring distribution.
- `g7`: the packet admits the one-level projection is “**biased against the kill**.” Going one level deeper, this makes FAIL informative but PASS unsafe: recursive or interacting inline expansions can exceed the cap even when the projection passes.
- `g8`: round-trip fixed points establish syntactic self-consistency, not faithful theorem semantics. Add BM25/embedding location baselines, Lean-native paraphrases, and independent semantic adjudication. With a ~1% fragment rate, the location and verification conclusions may rest on only a few tens of declarations.

## Envelope audit

The clearest overclaims are:

- `f2b-replicate`: “kernel-content-specific” should be “correct-alignment-specific.”
- `f2b-transfer`: a PASS does not remove ground-truth dependence completely; it removes literal string-equality gold while leaving generation/surface dependence.
- `f1`: B/record does not extrapolate freely across corpus composition and scale.
- `f4`/`f5`: ToolkenGPT and RETRO license related mechanisms, not the direction or effect size of this kernel intervention.
- `f6`: no evidence licenses 160M→410M when the packet concedes no scaling anchor.
- `f7`: survivor-conditioned WLS does not license an unbiased slope.
- `g2` and `l3a`: empirical agreement on finite authored cases is not a model-scale-free formalism proof.
- `g9`: future author capability is not guaranteed monotonic.
- `e8-r`: a third family does not automatically license all open-weight models ≤7B.
- `e9-c`: finite checker tests do not extrapolate “without limit.”
- `family-h0`: “135M–7B-class” is too broad if the surviving rejecting member was measured only below 1.7B.

There are also a few underclaims or misdirected claims:

- `l3a`, `a5`, `m0b`, `g6`, and `g7` are deterministic censuses on pinned bytes. Their exact behavior on those fixed inputs is known; Wilson intervals are not needed for that finite-set claim. The uncertainty concerns generalization to new queries, rules, or corpora.
- `f2b-replicate` does support a narrower and useful result: on `d-qa-r`, an aligned deterministic acceptance rule plus retry causally outperformed the listed text and PRM arms for the pinned seeds. The problem is attribution to NSM/kernel semantics, not the existence of that local effect.
- `f1`’s exhaustive round-trip can license losslessness for the pinned pack and dependencies, if the semantic payload audit succeeds; that is stronger than byte ratio alone but much narrower than general compression superiority.

## Cheapest decisive additions

1. **`f2b-external-factorial`**: external items selected before mapping, independently frozen gold, and a 2×2 factorial crossing semantic correctness with kernel-like surface. Include true kernel, aligned non-NSM answer store, deranged store, and no verifier. This is the most important addition.

2. **`f2b-style-probe`**: CPU/adjudication-only. Position swaps, canonical-vs-plain paraphrases, semantically false NSM-style near-misses, and semantically correct noncanonical answers. Require judges to explain evidence without seeing provenance.

3. **`b-cov-representativeness`**: stratified external-item audit reporting mapper precision, sense-level coverage, baseline difficulty, and unconditional augmentation value. Do not select the benchmark after seeing which one has favorable coverage.

4. **`a5-conventional` / `l3a-conventional`**: SQL/Datalog/AST-index baseline using exactly the same extracted facts and queries. This is near-zero cost and determines whether the result is kernel-specific.

5. **`e9-structure-control`**: conventional typed records plus the same deterministic constraints. If this matches the kernel, the result is structured validation, not kernel semantics.

6. **Existing-log reanalysis**: two-way cluster bootstrap for `f2b-*`; concept-level intervals for `g2`/`g3`; axiom/template-level reporting for `l3a`/`a5`. Do not count seeds or repeated templates as independent items.

7. **Independent `f7` confirmation split**: qualification on old data, slope estimation on fresh items and seeds. Without that split, report slopes as exploratory.

## Literature checks

These are methodological references, not claims that the programme must adopt their exact methods.

- Spectrum/selection effects can make performance look high on a narrow selected population: [Ransohoff & Feinstein (1978)](https://www.nejm.org/doi/10.1056/NEJM197810262991705). Confidence: high; application from diagnostic tests to kernel coverage is analogical.
- Non-independent repeated observations do not create independent treatment replications: [Hurlbert (1984)](https://esajournals.onlinelibrary.wiley.com/doi/10.2307/1942661). Confidence: high.
- Inference after selecting winners requires accounting for the selection event: [Fithian, Sun & Taylor (2014)](https://arxiv.org/abs/1410.2597). Confidence: high.
- NLP evaluation results can change materially with the evaluated data distribution: [Kovatchev & Lease (NAACL 2024)](https://aclanthology.org/2024.naacl-long.86/). Confidence: high.
- LLM judges exhibit systematic susceptibility to superficial and induced cues: [Chen et al. (EMNLP 2024)](https://aclanthology.org/2024.emnlp-main.474/). Confidence in the paper’s result: high; confidence that it explains this particular GPT-5.x proxy: moderate.
- Model evaluators can recognize and favor same-family/self-like generations: [Panickssery, Bowman & Feng (2024)](https://arxiv.org/abs/2404.13076). Confidence in the paper: high; applicability to NSM-tradition familiarity rather than literal self-generation: low-to-moderate, so it should motivate a control rather than be cited as proof of bias here.

## Honesty-rail check

The programme is unusually explicit about its caveats, but several caveats are currently doing work that only controls can do. Disclosing “covered by construction,” “pro-LLM extractor,” “single family,” or “biased against the kill” does not make the resulting PASS valid for the intended construct.

My proposed controls also carry honesty risks:

- The external benchmark must be selected and sampled before checking where the kernel engages.
- External gold must be frozen before kernel mapping or option rendering.
- The aligned non-NSM control must match information, acceptance rate, topology, and authoring cost; a deliberately impoverished random control would merely recreate the shuffled-kernel straw man.
- Natural-error taxonomies must not be authored solely from errors the checker was designed to catch.
- A failed human-recruitment stage must remain a missing experiment; repeated LLM proxies cannot accumulate into a human-independent gold claim.

The correct near-term licensing language is therefore: the programme has demonstrated a large local benefit from an aligned deterministic verifier on a fresh but self-authored definitional task. It has not yet demonstrated that NSM semantics, rather than canonical answer-key alignment and structured verification, caused that benefit; nor has it demonstrated utility on a source-external task distribution.
