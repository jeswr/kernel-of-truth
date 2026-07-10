The largest weakness is not lack of citations; it is that several comparators operate at the wrong abstraction level. The programme often compares a deterministic executor with free generation, an NSM representation with geometrically unmatched embeddings, or a domain-specific verifier with an off-domain PRM. Those comparisons can produce real measurements while leaving the claimed differentiation unresolved.

1. **Add the missing neural-parser + deterministic-executor baseline; otherwise `a5-llm` measures the cost of using the wrong substrate.**

   - **Bears on:** `a5-llm/HA5-LLM`, `l3a-parse`, L3b/L3c, `e9-full/HC1`.
   - **Missing/collision:** The closest prior art is not raw LLM-RAG. It is the established neural-symbolic pattern “LM emits a constrained formal object; deterministic machinery executes it”: [PICARD](https://aclanthology.org/2021.emnlp-main.779/), [Synchromesh](https://openreview.net/forum?id=KmtVD97J43e), [Logic-LM](https://openreview.net/forum?id=nWXMv949ZH), [Binder](https://openreview.net/forum?id=lH1PV42cbF), and [StructGPT](https://aclanthology.org/2023.emnlp-main.574/).
   - **Borrow:** Add an arm that emits `kot-query/1` using input-dependent grammar/type constraints, executes it with the byte-identical engine, and may abstain before execution. Report parse validity, denotation accuracy, semantic-parse error, engine error, refusal calibration, latency, and cost separately. If the 977 inputs are already formal `kot-query/1`, this arm collapses to the engine itself—which demonstrates that `a5-llm` is an intentionally artificial substrate comparison and should not be sold as a deployment differentiator. The scientifically meaningful comparison then moves to `l3a-parse`.
   - **Differentiate as:** “Our closed semantics and content-addressed records improve translation reliability/provenance/cost” rather than “a deterministic program is more exact than free generation.”
   - **Honesty rail:** A win on gold-parsed, covered-by-construction queries cannot establish natural-language system superiority. Do not let `a5-llm` substitute for `l3a-parse`.
   - **Confidence:** **High confidence** on all cited systems and their architectural pattern; verified from primary papers. **High confidence** on the design inference.

2. **The HC3 “PRM fork closed at 1.5B” claim is too strong: the tested Skywork checkpoint is an off-domain process verifier, not a matched verifier for definitional QA.**

   - **Bears on:** `f2`, `f2b-replicate/HC3`, any interpretation of `f2b-transfer`.
   - **Missing/collision:** Process supervision in [Let’s Verify Step by Step](https://openai.com/index/improving-mathematical-reasoning-with-process-supervision/) was studied on mathematical reasoning traces. The [Skywork-o1-Open-PRM-Qwen-2.5-1.5B model card](https://huggingface.co/Skywork/Skywork-o1-Open-PRM-Qwen-2.5-1.5B) likewise demonstrates step-scoring through mathematical examples. Meanwhile, [ProcessBench](https://arxiv.org/abs/2412.06559) reports that existing PRMs often fail to generalize to harder math distributions and can underperform prompted critic models. Thus the current comparison mostly measures domain/interface mismatch.
   - **Borrow:** Use a factorial verifier comparison: task-matched outcome verifier, task-matched process verifier, prompted critic, Skywork zero-shot, kernel verifier, and shuffled verifier. Give every arm the same candidate set and compare best-of-\(N\) selection or retry under matched generation FLOPs. Train matched verifiers only on a concept-disjoint development partition and evaluate on externally adjudicated `d-qa-t`.
   - **Differentiate as:** The defensible current result is “kernel verification beat this named zero-shot 1.5B PRM checkpoint on this task,” not “kernel verification beats trained PRMs at the 1.5B class.”
   - **Honesty rail:** Training a task-matched PRM on membership-string labels would simply import the same circularity into the baseline. Its supervision must come from external gold, and author/concept families must be split.
   - **Confidence:** **High confidence** on the cited works, model specialization, and ProcessBench’s reported generalization finding; verified from primary sources/model card. **High confidence** that HC3 is presently overinterpreted.

3. **The deranged-gloss probe does not identify NSM-style or option-format preference in `f2b-transfer-llmproxy`; add a truth × style factorial successor.**

   - **Bears on:** `f2b-transfer`, `f2b-transfer-llmproxy`, H-TRANSFER/H-CIRC.
   - **Missing prior art:** LLM judges exhibit position and familiarity/self-preference effects. [Large Language Models are not Fair Evaluators](https://aclanthology.org/2024.acl-long.511/) demonstrates position bias; [Self-Preference Bias in LLM-as-a-Judge](https://arxiv.org/abs/2410.21819) associates judge preference with more familiar/lower-perplexity outputs; multiple-choice models are also sensitive to answer order in [Pezeshkpour and Hruschka](https://aclanthology.org/2024.findings-naacl.130/).
   - **Borrow:** Construct a frozen \(2\times2\) probe crossing semantic correctness with surface style: correct/incorrect content × NSM-shaped/ordinary-dictionary paraphrase. Match length, fluency, vocabulary, and syntactic templates; rotate option order; include style-matched wrong answers and meaning-preserving cross-style pairs. The estimand is the truth effect after conditioning on style, plus a truth×style interaction.
   - **Why the present probe is insufficient:** Deranging glosses tests whether grossly unrelated content is accepted. It does not test whether a judge favors NSM-looking wording when two semantically plausible alternatives differ mainly in presentation.
   - **Honesty rail:** Run this as a successor diagnostic; do not alter the frozen proxy record. Even a clean style-invariance result would strengthen only the LLM proxy, not replace the required kernel-naive human judge or establish external question-style validity.
   - **Confidence:** **High confidence** on the cited judge and option-order biases; verified from primary papers. **Medium-high confidence** that the proposed factorial is the cheapest decisive probe for this particular confound.

4. **NSM does not itself confer a unique canonical explication; the programme needs an explication-reliability experiment, not only downstream `g1`.**

   - **Bears on:** `g1/HS1`, `g4/HS4`, `g9/HS-A`, `f2b-transfer`, and every use of “canonical semantic vector.”
   - **Missing/collision:** NSM supplies a reductive-paraphrase methodology, a proposed inventory of primes and grammar, and a role for semantic molecules; see Goddard and Wierzbicka’s [Meaning and Universal Grammar](https://benjamins.com/catalog/slcs.61) and the overview of [semantic primes, molecules, and templates](https://www.degruyterbrill.com/document/doi/10.1515/ling-2012-0022/html). That literature does not automatically make one programme author’s explication the uniquely correct analysis.
   - **Borrow:** For 50–100 concepts, obtain independent explications from at least two NSM-competent analysts plus an ordinary controlled-definition baseline. Measure structural agreement, blind meaning-reconstruction accuracy, entailment between independently authored explications, and cross-language invariance: author or translate the explication in another NSM exponent language, remap primes to language-independent IDs, and compare decoded structure and downstream decisions.
   - **Differentiate as:** “Canonical conditional on a versioned authored analysis” and “content-addressed” are defensible. “Canonical meaning of the concept” is not established until analyst and cross-language stability are measured.
   - **Honesty rail:** High inter-author agreement would support reliability of this authoring protocol, not prove that the 65-prime inventory is metaphysically universal or that every concept has a unique reduction.
   - **Confidence:** **High confidence** on the cited NSM works and their methodological scope; verified from publisher sources. **Medium-high confidence** on the non-uniqueness inference because it is a framing judgment, not a claimed theorem from those works.

5. **`e9-full`’s “strongest text baseline” is not yet strongest enough; borrow atomic-claim verification and attribution protocols.**

   - **Bears on:** `e9-full/HC1`, `e9-c/HC2`, the kernel precision linter.
   - **Missing/collision:** Adjacent systems already decompose, retrieve evidence for, verify, and revise claims. [RARR](https://aclanthology.org/2023.acl-long.910/) performs research-and-revision; [FActScore](https://aclanthology.org/2023.emnlp-main.741/) decomposes long text into atomic facts; [VeriScore](https://aclanthology.org/2024.findings-emnlp.552/) explicitly distinguishes verifiable from unverifiable claims; [ALCE](https://aclanthology.org/2023.emnlp-main.398/) separates answer quality from citation support; and [RAGTruth](https://aclanthology.org/2024.acl-long.585/) provides span-level RAG hallucination annotations.
   - **Borrow:** Build a matched-information text arm that receives textual renderings of exactly the same records and axioms, decomposes output into atomic claims, retrieves the relevant clauses, applies NLI/QA verification, and revises or abstains. Score four separate quantities: kernel-source faithfulness, external-world factuality, verifiable-claim coverage, and post-repair task accuracy. Human-audit a stratified sample of each error class.
   - **Differentiate as:** The kernel wins only if its formal schema catches relational or quantified violations that this claim-level text pipeline misses at matched cost. Beating a model rereading an undifferentiated gloss does not show that text systems “structurally cannot” catch the class.
   - **Honesty rail:** Consistency with an authored kernel is source faithfulness, not external factual truth. Preserve the linter’s correct rule that “ungrounded” is not “false.”
   - **Confidence:** **High confidence** on all cited methods and distinctions; verified from primary papers. **High confidence** that the present baseline leaves a material attribution loophole.

6. **Construction B needs a classical VSA capacity-and-aliasing benchmark before its vectors can be treated as exact structural objects.**

   - **Bears on:** Construction B itself, `g2/HS2`, `g3/HS3`, `g5/HS5`, `f3/HE3`.
   - **Missing/collision:** Full tensor-product representations and compressed holographic representations are old territory: Smolensky’s [Tensor Product Variable Binding](https://www.sciencedirect.com/science/article/pii/000437029090007M) and Plate’s [Holographic Reduced Representations](https://redwood.berkeley.edu/wp-content/uploads/2020/08/Plate-HRR-IEEE-TransNN.pdf). Plate explicitly treats unbinding as noisy and uses cleanup memory. Modern [Capacity Analysis of Vector Symbolic Architectures](https://arxiv.org/abs/2301.10352) formalizes dimension/load trade-offs.
   - **Borrow:** Sweep dimension, number of clauses, depth, repeated fillers, role reuse, negation/operator nesting, and codebook size. Include adversarial pairs differing in exactly one role, order, quantifier, or repeated atom. Compare full TPR, HRR/circular convolution, MAP/FHRR-style binding, Construction B, and canonical AST bytes. Report exact-decode rate, false accept, nearest-neighbour margin, collision count, and memory/compute. Use cleanup-memory and no-cleanup variants.
   - **Important mathematical check:** Elementwise/Hadamard multiplication is commutative unless role and order information is encoded elsewhere. The registry should contain explicit invariance tests showing that clause argument permutations do not collapse.
   - **Differentiate as:** Deterministic seeding and content addressing may be novel engineering constraints; binding, superposition, cleanup, and capacity are not.
   - **Honesty rail:** Perfect decode on the committed corpus cannot license structural injectivity outside the measured load/depth envelope.
   - **Confidence:** **High confidence** on the foundational works and capacity issue; verified from primary sources. **High confidence** on the commutativity concern, conditional on the packet’s abbreviated description of the encoder.

7. **`g1` needs a geometry-matched factorial; its current random-atom and Numberbatch controls do not cleanly identify “NSM content.”**

   - **Bears on:** `g1/HS1`, `f4/HE4`, indirectly the interpretation of A2/E5.
   - **Missing prior art:** [Wieting and Kiela](https://arxiv.org/abs/1901.10444) showed that random encoders can be unexpectedly strong and emphasized careful downstream protocols. [ConceptNet Numberbatch](https://ojs.aaai.org/index.php/AAAI/article/view/11164) combines distributional vectors with relational knowledge, while [Mitchell and Lapata](https://aclanthology.org/P08-1028/) provide simple additive and multiplicative compositional baselines.
   - **Borrow:** Use a factorial crossing atom semantics with composition:

     - NSM labels vs random labels vs Numberbatch/distributional atoms;
     - Construction-B composition vs bag/addition vs pointwise multiplication vs random projection;
     - all dimension-, norm-, whitening-, token-count-, adapter-capacity-, and training-budget-matched.

     Also include a “true explication structure, deranged concept assignment” cell and a “random structure, correct concept identity” cell. This distinguishes semantics, identity lookup, and compositional geometry.
   - **Differentiate as:** A downstream margin can establish predictive utility of the authored NSM content under this interface. It cannot validate the linguistic prime inventory itself.
   - **Honesty rail:** Avoid choosing whitening, dimensionality, or adapter hyperparameters separately per representation using the test endpoint; that would make the null asymmetric.
   - **Confidence:** **High confidence** on all cited systems and their relevant methods; verified from primary sources. **High confidence** that the proposed factorial identifies more than the present three-way comparison.

8. **`f3` is missing two distinct compression families; xRAG alone does not exhaust the dense-I/O prior art.**

   - **Bears on:** `f3/HE3`, `f4`, `f5`, L1b, the M2-output rider.
   - **Missing/collision:** Dense learned compressors include [xRAG](https://arxiv.org/abs/2405.13792), [ICAE](https://arxiv.org/abs/2307.06945), [AutoCompressors](https://aclanthology.org/2023.emnlp-main.232/), and [Gist Tokens](https://arxiv.org/abs/2304.08467). Hard/extractive prompt compression includes [LLMLingua](https://aclanthology.org/2023.emnlp-main.825/) and LLMLingua-2. [Large Concept Models](https://arxiv.org/abs/2412.08821) instead operate autoregressively over sentence-level SONAR representations and are not a direct frozen-input-adapter baseline.
   - **Borrow:** Include at least one learned soft-slot compressor and one extractive text compressor, alongside xRAG. Match effective information budget, prompt FLOPs, KV bytes, compressor/adapter training, precomputation, retrieval storage, and break-even query count. Report reconstruction of exact identifiers and negation/quantifiers, not just end-task accuracy.
   - **Differentiate as:** The kernel’s residual claim is canonical, training-free, exactly decodable concept compression. If a learned compressor matches accuracy/cost, the performance claim collapses to governance—as the packet already says—but that comparison must span the relevant compressor classes.
   - **Honesty rail:** LCM/SONAR results can motivate an output-corner hypothesis; they do not license an expected failure for a frozen dense-input adapter. Keep those envelopes separate.
   - **Confidence:** **High confidence** on the cited architectures and their roles; verified from primary papers. **High confidence** on the comparator gap.

9. **ROME/MEMIT are not the closest editing baselines; external-memory editors collide more directly with `f4`, `f5`, and L2b.**

   - **Bears on:** `f4/HE4`, `f5/HE5`, L2b kernel-addressed memory, lifecycle claim `HS9`.
   - **Missing/collision:** [SERAC](https://arxiv.org/abs/2206.06520) stores edits in explicit memory and retrieves them to modulate model predictions. [IKE](https://aclanthology.org/2023.emnlp-main.296/) performs gradient-free in-context editing and evaluates side effects. These are closer to a versioned external concept store than ROME/MEMIT’s weight surgery.
   - **Borrow:** Add SERAC-style retrieved edit memory and IKE/selective-context arms. Use the editing literature’s dimensions: edit reliability, paraphrase generalization, locality/specificity on unrelated inputs, portability to logically related queries, sequential-edit degradation, rollback/version switching, and latency/storage. Run both single-edit and accumulated-edit regimes.
   - **Differentiate as:** “Deterministic provenance, exact rollback, no learned scope classifier, and byte efficiency” is plausible differentiation. “External memory makes knowledge editable” is already claimed territory.
   - **Honesty rail:** CounterFact/ZsRE-style success would test edit propagation, not NSM adequacy. Conversely, kernel exactness on direct lookups would not establish portability to paraphrases or implications.
   - **Confidence:** **High confidence** on SERAC and IKE’s methods and evaluation concerns; verified from primary papers. **High confidence** on their relevance as closer baselines.

10. **The leak checks need an explicit contamination threat model; “fresh item” does not exclude template, source, or semantic contamination.**

   - **Bears on:** `f2b-replicate`, `f2b-transfer`, `g9`, N1-LB/b-cov/LB-1, `f7`.
   - **Missing prior art:** Black-box membership diagnostics include [Min-K% Prob](https://openreview.net/forum?id=ZLJ6XRbdaC), [Min-K%++](https://openreview.net/forum?id=ZGkfoufDaU), [PaCoST](https://aclanthology.org/2024.findings-emnlp.97/), and test-set slot guessing in [Deng et al.](https://aclanthology.org/2024.naacl-long.482/). More robust evaluation designs use temporally fresh or sealed tests, as in [LiveBench](https://arxiv.org/abs/2406.19314) and [MMLU-CF](https://aclanthology.org/2025.acl-long.656/).
   - **Borrow:** Predeclare contamination levels: exact item, paraphrase, source-definition, answer-option/template, and task-family familiarity. For open models, search disclosed corpora; for all models, run paired membership diagnostics. More importantly, maintain a sealed post-model-cutoff test tranche or generate hidden counterfactual worlds with nonce concept names and newly authored axioms after model pinning.
   - **Differentiate:** N1-LB should report public-benchmark performance as contamination-susceptible and place more inferential weight on refreshed/hidden variants. For the F2 line, nonce concepts help separate following the supplied record from recalling familiar lexical/NSM associations.
   - **Honesty rail:** Membership tests are diagnostics with imperfect assumptions, not proof of absence. Only temporal or access-controlled separation materially changes the threat model, and even that does not eliminate general task familiarity.
   - **Confidence:** **High confidence** on the cited methods and dynamic-benchmark designs; verified from primary papers. **High confidence** that the present “fresh” label is under-specified scientifically.

11. **Evaluate refusal on a risk–coverage frontier; raw fabrication rate gives the engine an inherent policy advantage.**

   - **Bears on:** `a5-llm/H-FAB`, L3b routing, `e9-full`, the linter’s quarantine mode.
   - **Missing prior art:** [Semantic entropy](https://www.nature.com/articles/s41586-024-07421-0) evaluates uncertainty-driven refusal using rejection/accuracy curves and explicitly limits its claim to confabulations rather than systematic errors. This is the relevant evaluation shape even if semantic entropy itself is too expensive.
   - **Borrow:** For every LLM arm, expose a confidence/answerability score—token likelihood, sampled semantic entropy, critic score, or calibrated binary head—and sweep the abstention threshold. Compare selective risk, coverage, AURC/AURAC, cost, and utility at the engine’s achieved coverage. Add a router arm that sends only high-confidence licensed queries to the engine and the rest to the LLM.
   - **Differentiate as:** Engine refusal is genuinely valuable if it dominates calibrated LLM abstention at matched coverage and cost. “Engine refuses unlicensed queries while an unconstrained LLM answers them” is partly a comparison of fixed policies.
   - **Honesty rail:** Semantic entropy detects stochastic confabulation, not confidently repeated falsehoods; it must remain a baseline, not a factuality oracle. Coverage matching must not hide that the engine’s covered slice was authored by construction.
   - **Confidence:** **High confidence** on semantic entropy’s method, metrics, and stated limitation; verified from the primary article. **High confidence** that risk–coverage is the correct comparison for H-FAB.

The three changes I would make before spending substantial additional GPU budget are: add the parser+engine comparator, narrow HC3 to the named checkpoint unless a task-matched verifier is run, and install the truth×style probe around the transfer proxy. Those three address the most consequential cases where a clean PASS could currently support a narrower conclusion than the programme’s framing suggests.
