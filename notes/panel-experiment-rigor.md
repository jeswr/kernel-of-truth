# Panel review — experimental rigor of docs/poc-design.md (rev 1)

**Reviewer:** adversarial methodology panel (empirical-ML methodologist persona). Date: 2026-07-07.
**Scope:** docs/poc-design.md against docs/architecture.md, reports/architecture-and-poc-options.md, reports/fixed-vectors-in-llms.md, reports/deterministic-concept-vectors.md.
**Stance:** default to refutation. Each finding: severity, problem, minimal fix. Severity counts: 4 BLOCKER, 15 MAJOR, 6 MINOR.

---

## BLOCKERS

### 1. BLOCKER — The kernel-D → model-d projection is unspecified, and every Phase-X guarantee is priced at the wrong dimension

The encoder produces vectors at D ≈ 8k–32k (architecture.md §1.2; capacity math explicitly requires this). The E1 model has embedding dim d ≈ 256–512 (5–15M non-embedding params); SmolLM2-135M has d=576; Qwen2.5-0.5B d=896. **poc-design.md never says how a kernel vector becomes an embedding row.** The two candidate routes break different things:

- *Down-project (JL/random projection)*: pairwise geometry survives approximately (n≈115, d≈512 ⇒ ε≈0.1), but exact orthonormal unbinding, decode margins, and the X1/X2 numbers do not transfer. E4's "geometry places h near the unseen read-out direction" then happens in a space Phase X never characterised.
- *Run the encoder natively at D=d*: a 512-row Hadamard codebook still fits ~200 atoms orthonormally, but capacity (0.2–0.5 bits/dim ⇒ ~100–250 bits at d=512) is far below the ~2–4 kbit structure budget — the margin and decodability claims collapse.

Either way, the experiments as pre-registered are not runnable, and the choice silently changes which hypothesis is tested. **Fix:** pre-register the projection (e.g. one fixed, seeded, published projection matrix per (D, d) pair), report the similarity-matrix distortion between R^D and R^d for kernel v0 (Spearman of the two RDMs), and re-state X1-style margins *in R^d* — those, not the D=8192 numbers, are the ones E1/E4 inherit.

### 2. BLOCKER — E1's success criterion uses the wrong null: random-frozen cannot support the "content matters" conclusion

Random-frozen (i.i.d., norm-matched) differs from kernel-frozen in **two** ways at once: (a) the kernel Gram matrix has structure (concepts sharing primes are correlated; lower effective rank; clusters), (b) the specific concept↔vector assignment is meaningful. A kernel > random-frozen win is therefore uninterpretable as stated in the doc's own terms: it could reflect the generic benefit of *any* correlated frozen dictionary (similarity smoothing across tied output rows raises cloze/PPL on related concepts at initialization, before any learning) rather than correct content. The doc's Common rules list shuffled-kernel as "load-bearing, everywhere applicable" — but E1's success criterion omits it. **Fix:** add shuffled-kernel-frozen as a fourth E1 arm (12 runs, ~$3–8 extra) and make the primary pre-registered criterion **kernel-frozen > shuffled-kernel-frozen** (exactly spectrum-, norm-, and marginal-matched; only assignment differs), with kernel > random-frozen demoted to secondary. Without this, an E1 "success" does not license the kill-chain's "content-as-inductive-bias" advance.

### 3. BLOCKER — E4's "above chance" is undefined, and under the natural reading the criterion is incoherent

With ~115 concepts, 20% held out is ~23 unseen concepts. "Unseen top-10 above chance" is not concrete: (a) **over the full extended vocab**, chance ≈ 10/V ≈ 0.1–0.25%, and mere task-format learning ("emit some concept token after a gloss") puts *both* kernel and random-frozen far above it — the co-criterion "random-frozen control at chance" then fails by construction and the rule cannot fire; (b) **over the 115 concept tokens**, chance = 10/115 ≈ 8.7%, and with one gloss per held-out concept (n=23) you need ≥5/23 hits for exact-binomial p<0.05 — a knife-edge, single-look test with no stated statistics. **Fix:** pre-register (i) candidate set = concept tokens only; (ii) ≥5 paraphrase glosses per held-out concept (n≥115 trials); (iii) the test = kernel vs random-frozen unseen accuracy, Fisher exact / permutation, p<0.05 — using the control as the empirical chance floor rather than a theoretical one.

### 4. BLOCKER — Pre-registration is void unless the encoder version is pinned before any E-run

The encoder has admitted free parameters (superposition weighting "silently determines whether root or leaf differences dominate similarity" — deterministic-concept-vectors §7.3; polarity-weighted variants from X3; D; normalization). E2 costs ~$1 and hours. Nothing in poc-design.md forbids iterating the encoder against E2's ρ until it passes — the cheapest garden of forking paths in the whole programme, and the doc's own provenance machinery (content-addressed encoder, §3.1 of architecture.md) makes the fix trivial. **Fix:** add to Common rules: "One encoder version, selected on Phase-X results alone; its content hash is written into this document before the first E-run; any E-series run against a different encoder hash constitutes a new pre-registration and is reported as such."

---

## MAJOR

### 5. MAJOR — E1 probe/cloze circularity: the kernel rows *are* linear encodings of the evaluation targets

Kernel vectors are, by construction, linear sketches of explication feature multisets. A **linear probe for explication relations** applied to any representation that still linearly contains the frozen input row (embedding layer, early residual stream) will beat random-frozen *with zero learning by the LM* — the probe reads the answer out of the encoder's own output. Same for cloze at step 0 via tied-row logit correlations. A "win" would be reported as the model exploiting content when the evaluation pipeline exploited it instead. **Fix:** (i) evaluate every E1 metric on the **untrained (step-0) kernel-frozen model** and pre-register that trained-model success requires beating the step-0 baseline, not just random-frozen; (ii) run probes only on mid-layer contextual states at positions *other than* the concept token itself.

### 6. MAJOR — Mapper→evaluation leakage is unaddressed

The phrase→concept mapper, the corpus augmentation, the E1 cloze "explication-entailment templates", and the E4 glosses are all generated from the same explications by the same team/tooling. If E4 glosses are rendered explications, E4 reduces to "learn the deterministic text→vector encoder map and regress onto it" — a seq2seq function-fitting result compatible with rows-as-arbitrary-but-predictable-ids, not evidence the model uses geometry as semantics. If cloze templates share surface n-grams with augmented training text, "held-out" is nominal. **Fix:** pre-register the held-out **unit** (template *type* and concept, not instance); E4 glosses must be naturalistic paraphrases authored independently of the explication rendering and disjoint from the mapper lexicon; publish the gloss set hash before training.

### 7. MAJOR — E4 "unseen" concepts were seen throughout E1 pretraining

Held out "of emission training" only: their tokens (with frozen rows) appear in the augmented TinyStories corpus, so the model has contextual knowledge of them before the gloss task. The random-frozen control shares this exposure, so the comparison survives, but the headline gloss — "a never-trained read-out direction" — is false as stated, and the result cannot cleanly support the strong zero-shot-geometry claim. **Fix:** add a second tier of ~10 concepts excluded from *all* training text (rows present in vocab, never emitted or seen). Cost ≈ zero; this tier is the actual decisive test, and the doc's "single cheapest result making the strong claim credible" line should attach to it.

### 8. MAJOR — E2's RDM over "prime … exponent words" is degenerate for primes

The 65 primes are encoded as **exactly orthonormal** codebook rows (architecture.md §1.2): every prime–prime kernel cosine is exactly 0. That block of the RDM is constant — it contributes only massive ties that drag Spearman toward zero and distort the permutation null; all real signal must come from the ~50 explicated molecules. **Fix:** restrict the RSA item set to explicated concepts (graded overlap), or pre-register exclusion of the prime–prime block; state item counts and the tie-handling policy.

### 9. MAJOR — E2 cannot be the "empirical hook" for A1, and a bare permutation null tests almost nothing

RSA on second-order similarity is invariant to rotations of either space — it tests geometry-up-to-transform, i.e. exactly A2's premise, never A1's raw-coordinates claim; the kill chain mislabels it. Worse, *any* measure loosely tracking semantic relatedness (WordNet, word2vec, definition word-overlap) beats a permuted null on ~100 English words; ρ > null at p<0.01 shows the kernel RDM contains generic relatedness, not that models converge toward *kernel* geometry. **Fix:** (i) re-label E2 as testing A2's precondition; (ii) add pre-registered comparison RDMs (word2vec cosine, WordNet path, gloss word-overlap) and require the kernel RDM to add explanatory power via **partial RSA** (partial Spearman controlling the baselines); otherwise report as "generic relatedness detected".

### 10. MAJOR — E2 layer/protocol freedom is an uncorrected multiple-comparisons machine

"Embedding-/mid-layer representations" across 3 models with unspecified extraction (isolated word? template context? multi-token pooling?) invites scanning layers × models × pooling and claiming success when any 2 families pass. **Fix:** pre-register: one mid layer (L/2) per model, or a max-over-layers statistic with the permutation null computed on the same max; the extraction protocol (each word in ≥k contexts, mean-pooled over the word's tokens); a Mantel-style permutation over concept labels, ≥10⁴ permutations; and the per-model in-vocabulary word list (attrition will differ across the three tokenizers — publish the intersection).

### 11. MAJOR — "3 seeds + non-overlapping 95% CIs" is statistically incoherent and severely underpowered

With n=3, the CI uses t₂=4.30 and the SE estimate has 2 df — CI width is itself noise. Non-overlap of two independent 95% CIs corresponds to roughly p≈0.006 under ideal conditions, but with 2 df the criterion's operating characteristics are unknown; in practice it demands enormous effects. A two-sample permutation test at 3v3 has a minimum attainable one-sided p of exactly 0.05 (20 assignments) — no room for any correction. Compounding: success requires passing on probes **and** cloze (a conjunction), further collapsing power. Consequence for the kill chain: an E1 "null" under this criterion is mostly a power artifact, yet the kill chain treats it as strong evidence of absence. **Fix:** ≥5 seeds per arm (252 assignments; min p≈0.004); pair seeds across conditions (identical data order/batch schedule per seed index) and use a paired permutation test; one **primary** endpoint (concept cloze), Holm correction for the rest; and for the *kill* direction, pre-register a smallest-effect-size-of-interest and use an equivalence bound — "not significant" and "shown ≈ null" are different claims and the kill chain needs the second.

### 12. MAJOR — "at ≤50% of training tokens" is ambiguous and implies uncorrected sequential looks

Does E1 success mean (a) kernel at the 50%-token checkpoint beats random at its 100% endpoint, (b) both compared at the 50% checkpoint, or (c) the advantage emerges anywhere before 50%? Reading (c) is multiple looks over the training curve with no alpha spending; readings (a) and (b) are different claims (sample efficiency vs. speed). **Fix:** pre-register one comparison: "kernel-frozen at the 50%-token checkpoint vs random-frozen at the 100%-token endpoint, single look" (that is the sample-efficiency claim C2 actually needs), all other checkpoints descriptive.

### 13. MAJOR — E1's augmentation policy is unspecified, and the deterministic mapper can make concept-token PPL insensitive in all arms

"Interleaved/substituted" is a design fork with opposite failure modes: deterministic interleaving makes every concept token perfectly predictable from the adjacent word (ceiling in all conditions — metric dead); deterministic substitution makes the token inherit the word's distribution (learnable as an arbitrary id — the null wins by construction, regardless of truth). Between-condition comparability survives (same corpus), but metric sensitivity does not. **Fix:** pre-register stochastic substitution (e.g. p=0.5 per occurrence, seeded), and pre-register that if concept-token PPL saturates within x% across all arms it is declared uninformative rather than narrated.

### 14. MAJOR — E3 is circular as specified and its per-token metric wins by arithmetic

The entailment labels are synthesized from explication structure; the concept-only coding hands the model tokens whose frozen vectors *encode that same structure*. The input may linearly contain the label — a "win" would show the synthesis pipeline leaks into the input coding, not that dense concept I/O is efficient. Separately, "accuracy per input token" mechanically favors the shorter concept coding, and "≤50% tokens" is trivially satisfied at matched examples. **Fix (three cheap additions):** (i) a **no-LM baseline** — logistic regression on the summed/mean kernel vectors of the input; if it solves the task, the task is degenerate and must be re-synthesized; (ii) a shuffled-kernel concept-only arm — content claim requires true > shuffled; (iii) primary criterion at matched *examples*, per-token reported as descriptive only.

### 15. MAJOR — Matched LR schedule across E1 arms is a confound wearing a control's clothes

Frozen-embedding and trainable-embedding models have different optimal LRs (the 5–10× convergence-slowdown result for badly-matched frozen vectors is partly an LR-mismatch story). Forcing one schedule can manufacture or erase the kernel-vs-random gap. **Fix:** pre-register a per-condition LR selection rule (small sweep on seed 0 only, best-of-3 by val loss, then fixed for all seeds), rather than one global schedule.

### 16. MAJOR — Kill-chain inferences are not valid as written

(i) The kill conjunction treats E1/E4 as independent, but E4 runs *on the E1 model* — if E1's model is broken or underpowered (see #11), E4-at-chance is inherited, not confirmatory. (ii) "Strong hypothesis dead" from nulls at 5–15M params, one corpus, one (unspecified — #1) projection is an overreach; the licensed conclusion is "dead in this instantiation at this scale". (iii) The advance rule is asymmetric: three nulls to kill, but a single E4 positive — n≈23, leakage-prone (#6, #7) — triggers "begin frontier-lab prospectus on the strong form". (iv) "E2 fail ⇒ A2 becomes primary" is in tension with E2 being precisely A2's premise (#9); state explicitly that E5 remains runnable after E2 failure only because a non-orthogonal linear adapter can reshape the Gram structure RSA sees. **Fix:** rewrite the kill chain: scale-qualified kill verdict; advance requires E4 positive **plus** the fully-unseen tier (#7) **plus** replication in a second model family; and per-branch statements of which architecture each outcome actually bears on.

### 17. MAJOR — X1's "fp16 noise floor" is not a defined quantity, and the success band is vacuous while the failure band leaves a dead zone

The encoder runs in TypeScript (float64); fp16 enters only as a downstream storage/GPU format, so "the fp16 noise floor at D=8192" names no property of the encoder. If it means componentwise fp16 rounding of unit vectors, the induced angular error is ~5×10⁻⁴ rad; "5×" that is ~0.14° — random high-D pairs sit near 90°, so the success criterion is passed by construction for anything but adversarially close pairs. Meanwhile "failure = margin < 2×" leaves 2×–5× unadjudicated. **Fix:** define the floor operationally — max angular self-distance of any kernel-v0 vector under an fp16 round-trip (and cross-platform re-encode), measured; success = min inter-explication angle > 5× that measured floor; declare 2×–5× "inconclusive ⇒ raise D or revise encoder, new pre-registration".

### 18. MAJOR — X1/X2 sample the wrong region: collisions live at single-edit neighbours, not random explications

10⁴ *random* synthetic explications will be far apart with overwhelming probability — that minimum is nearly vacuous. The doc's own weakness statement says one deep NOT moves the vector ~1/s of its norm: the dangerous pairs are single-edit neighbours (operator flip, clause swap, referent-index change). X2's "100% at depth ≤4 on kernel v0" is similarly weak if kernel v0 (~115 mostly shallow records) contains a handful of depth-4 trees. **Fix:** add an adversarial suite — all single-edit neighbours of every kernel-v0 explication (and of a sample of synthetics) — and report the margin distribution *over that suite* as X1's headline number; for X2, state n per (depth, clause-count) cell and synthesize cells with n < 30.

### 19. MAJOR — No pre-registered statement of what a tiny-scale positive cannot license

Even a clean sweep (E1+E4+E2 positive) cannot license: canonical/cross-model claims (every E-experiment is single-basis, single-model — the doc's own source report concedes arch (a) "cannot test cross-model canonicalness"); scale claims (in a 5–15M model with 4–8k vocab, concept rows are a meaningful parameter fraction and TinyStories is a synthetic, semantically clean domain with a near-perfect mapper — all four properties invert at scale); universality claims (English exponent words only, while NSM's core claim is cross-linguistic). Absent a written scope limit, the "frontier-lab prospectus" step will inherit unlicensed generality. **Fix:** add a pre-registered "claims a positive does NOT support" paragraph mirroring architecture.md §4's "what we do not claim"; cheap on-thesis extension: run E2 additionally on one non-English model/exponent list.

---

## MINOR

### 20. MINOR — E1 lacks the kernel-init-trainable arm
Kernel-initialised *trainable* embeddings (3 runs) would separate "content as head start that washes out" (arXiv:2407.05841's prediction) from "content + fixedness". Cheap and directly interprets a kernel-frozen > trainable outcome. **Fix:** add the arm.

### 21. MINOR — Frozen-scope ambiguity
"Three embedding conditions" doesn't say whether the *whole* table or only concept rows are frozen in the frozen arms (2507.04886 froze everything). These test different claims. **Fix:** one sentence: "concept rows only; all other rows trainable in all arms."

### 22. MINOR — Norm-matching target and post-embedding normalization unspecified
Norm-matched to the *init* distribution of trained rows (it drifts later)? And if the architecture applies embedding LayerNorm/scaling, kernel geometry is partially destroyed before layer 1 in all arms. **Fix:** pin the norm-match target to the init distribution; state whether embeddings are normalized before use and, if so, report kernel RDM distortion post-norm.

### 23. MINOR — E5 criteria undefined
"Beats shuffled kernel significantly": no test, no α, no nonce-concept count, no statement of how "usage/definition-match" is scored (if LLM-judged, judge prompts must not contain explications — leakage). **Fix:** pre-register n nonces, exact test, α, and a non-LLM scoring rubric or leak-checked judge.

### 24. MINOR — E2's frequency-matched random word set has no role in the success criterion
It appears as a baseline but the criterion only references the permuted null; as written it is free narrative material. **Fix:** either require kernel-set ρ > random-set ρ distribution (e.g. > 95th percentile over k random sets) or drop it.

### 25. MINOR — X1 compute feasibility on this box
Min pairwise angle over 10⁴ vectors at D=8192 is ~5×10⁷ dot products ≈ 10¹² flops — hours niced on 2 shared cores, and ~160 MB fp32 for the matrix against 3 GB free disk/8 GB RAM. Feasible but plan it (block-wise, fp32, checkpointed). **Fix:** note the budget in the doc.

---

## Verified clean (one line each)

- **AdamW weight-decay/momentum silent-unfreeze gotcha:** correctly identified and pre-empted in E1.
- **X0 byte-determinism + golden vectors:** sound discipline, mirrors existing concept-hash practice.
- **X3 as documentation-not-pass/fail:** honest handling of a known unsolved weakness.
- **Negative-results-as-deliverables and cost realism ($10–80, spot T4):** credible and commendable.
- **E6 deferral until E1/E4 read out:** correct sequencing.

## Summary of minimal-fix cost

Nearly all fixes are specification changes to poc-design.md (zero compute). Added compute: E1 shuffled-kernel arm + kernel-init arm (+6 runs ≈ $5–15), 5 seeds instead of 3 (+~60% of E1 budget), E4 fully-unseen tier and paraphrase glosses (~$0), E3 no-LM baseline (CPU). Total programme stays within the stated $10–80 envelope's upper half. The design is salvageable; as written, however, a headline "success" on E1/E2/E4 would be uninterpretable (#1, #2, #3, #5, #6) and a headline "kill" would be an underpowered non-result dressed as a falsification (#11, #16).
