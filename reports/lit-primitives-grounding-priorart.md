# Semantic primitives and symbol grounding — prior art and verdicts

**Kernel of Truth programme — literature review, Line 2 (semantic PRIMITIVES and symbol GROUNDING).**
Author: Kern (Claude Fable 5). Date: 2026-07-08. Coordination: sparq-org/sparq#1683.
Companion to `reports/nsm-and-knowledge-injection.md` (Line 1: computational NSM + KG-injection into LMs) — that report owns DeepNSM, definition-grounded vectors, and KEPLM injection mechanics; this report does **not** re-litigate them except where they bear on the primitive-basis question.

Every substantive claim is tagged **[established]** (replicated / uncontroversial), **[claimed]** (asserted by authors, not independently verified), or **[speculative]** (inference, ours or others').

Per the mission's CRITICAL LENS, each sub-line closes with a verdict on whether the observed failure/limitation is **CAPABILITY-LIMITED** (a Fable-class model or more compute plausibly changes the result) or **FUNDAMENTAL** (a principled barrier that better models do not move).

---

## 0. Executive summary — the two questions this dive owns

**Q1: Has anyone successfully built canonical vectors from a SMALL primitive basis (tens of primitives), and to what quality?**

Short answer: **Yes, but only in the human-annotated, non-deterministic sense, and only to "decodes/predicts" quality, never to "is a competitive representation" quality.** The three strongest existence proofs are all *brain/behaviour-grounded feature spaces*, not training-free constructions:
- **Mitchell et al. 2008** predicted fMRI activation for nouns from a **25-verb** sensory-motor basis — a genuine small-basis success, but the basis is hand-picked and the readout is a *trained* linear model over corpus co-occurrence [established].
- **Binder et al. 2016** built a **65-dimension** brain-based componential space (curiously the same order as NSM's 65 and Mel'čuk's ~60 lexical functions) from **human ratings** of 535 words; it decodes word embeddings and predicts brain activation with interpretable dimensions [established].
- **McRae feature norms (2005)** — hundreds of production-elicited features — support categorisation and priming models but are large (thousands of features), sparse, and not a *small* basis [established].

None of these is *training-free* or *deterministic*. Every one either (a) is elicited from humans, (b) is fitted with a learned readout, or (c) both. **No published system builds a competitive semantic space from a small primitive basis with zero training and zero human annotation** — which is exactly what the kernel's Hadamard/HRR encoder attempts. The kernel is therefore not reproducing a solved problem; it is attempting an *unattempted* point in the design space, and the prior art tells us the honest bar is "decodes/predicts," not "beats distributional vectors."

**Q2: Did the primitive-decomposition programme fail for capability reasons (no good automatic decomposer) or for principled reasons (Fodor, polysemy, open-endedness)?**

Short answer: **Both, in a specific split.** The *engineering* failure (no scalable automatic decomposer; hand-built lexica of hundreds of explications over decades) is **CAPABILITY-LIMITED** and is precisely what LLMs now erode (DeepNSM, §1.1 of the companion report). The *scientific* failure (that lexical meaning *is* a finite composition of primitives) is **FUNDAMENTAL** and is not moved by better models — Fodor's atomism, the polysemy/vagueness of the primes themselves, and the open-endedness of the definiens vocabulary are principled barriers. The correct reading for the kernel: **treat primitives as an engineering interlingua (capability-limited, now tractable), not as a discovered mental ontology (fundamental, unproven).** This is the same conclusion Line 1 reached from the NSM-critique side (Riemer 2006, von Fintel & Matthewson 2008), arrived at here independently from the decomposition-theory side.

**On our own X1-grounding negative result:** the prior literature *predicts it precisely* and it does **not** undermine the choice of NSM-65 as a basis. See §6.

---

## 1. NSM: Wierzbicka & Goddard, and the primitive inventory as an object

### 1.1 What NSM claims

Natural Semantic Metalanguage (Wierzbicka 1972, 1996; Goddard & Wierzbicka eds. 2002, *Meaning and Universal Grammar*; Goddard 2011, *Semantic Analysis*) posits a closed set of ~65 **semantic primes** — indefinable, universally lexicalised word-meanings (I, YOU, SOMEONE, SOMETHING, THIS, KNOW, THINK, WANT, FEEL, SAY, DO, HAPPEN, GOOD, BAD, BIG, SMALL, WHEN/TIME, WHERE/PLACE, NOT, CAN, BECAUSE, IF, ...) plus a universal **combinatorial grammar** (valency frames, substantive phrases). Meanings of all other words are stated as **reductive paraphrases** ("explications") built only from primes and a staged vocabulary of "semantic molecules" [established as a description of the programme].

Two empirical pillars are claimed [claimed by the NSM school]: (i) **universality** — every prime has a lexical exponent in every language; (ii) **reductive definability** — every word is explicable in primes without circularity. The kernel adopts NSM's *closed set + grammar* as its symbol layer (`encoder/src/lexicon.ts`, 65 primes chart v20-2022).

### 1.2 The state of the empirical pillars (the kernel inherits these)

Line 1's companion report already catalogues the leading critiques; the ones that bear on *this* dive's "primitive basis" question:
- **Universality is contested at the lexical level.** Bohnemeyer's Yucatec Maya fieldwork shows no lexical exponents of BEFORE/AFTER [established]; von Fintel & Matthewson 2008 find "remarkably few convincing semantic universals" and reject the claim that primes are self-evidently simple [established]. The NSM reply weakens the Strong Lexicalization Hypothesis, conceding the strong universality claim while keeping the metalanguage [established].
- **The primes are themselves polysemous / vague across allolexes** — a recurring critique (Riemer 2006) that matters directly for a *vector* encoder: if a prime's identity is fuzzy, its assigned basis row is a convenient fiction, not a natural kind.

**Verdict (NSM as inventory):** The choice of NSM-65 as the kernel's symbol alphabet is defensible **as engineering** (small, closed, cross-translatable, grammar-constrained, decades of hand-worked explications to seed from) and **indefensible as a claim to have found the atoms of thought**. This split is FUNDAMENTAL on the science side and CAPABILITY-LIMITED on the engineering side. It does not, by itself, doom the kernel — it constrains what the kernel may *claim*.

---

## 2. Classical semantic decomposition: the programme that (mostly) failed

The kernel is a late entry in a 60-year line of "meaning = structured composition of primitives." The history is a graveyard, and the causes of death are diagnostic.

### 2.1 Katz & Fodor (1963) and the Katz-Postal semantic markers

The founding decompositional theory: word senses as bundles of **semantic markers** (`(Human)`, `(Male)`, `(Adult)`) plus a **distinguisher** for idiosyncratic residue; projection rules compose sentence readings and resolve ambiguity via selection restrictions [established]. It collapsed under two blows: (i) the marker/distinguisher line was principled nowhere — the distinguisher was an admission that decomposition *runs out*; (ii) **Fodor himself** (having co-authored it) turned against it. This is the historically decisive fact: the strongest anti-decompositionalist is the co-inventor of decomposition.

### 2.2 Fodor's anti-decompositional arguments — the FUNDAMENTAL barrier

Fodor (1970 "Three Reasons for Not Deriving 'Kill' from 'Cause to Die'"; 1998 *Concepts*; Fodor, Garrett, Walker & Parkes 1980 psycholinguistic studies) mounts the barrier the whole primitive programme must clear [established]:
- **No definitions survive.** For almost any lexical concept (the famous cases: *bachelor*, *kill*, *paint*, *climb*), proposed definitions have counterexamples; the definitional project has essentially **zero successful non-trivial definitions** to show after decades. ("Bachelor = unmarried adult male" fails on the Pope, on divorced men, etc.) [established].
- **No psychological reality of decomposition.** Fodor et al. 1980 found that sentences with putatively "more complex" (more-decomposed) verbs are **not** reliably harder to process — if *kill* were mentally stored as CAUSE-BECOME-NOT-ALIVE, it should cost more than a primitive; it doesn't [established, and this is the empirical crux].
- **Informational atomism.** Fodor's positive view: lexical concepts are **unstructured atoms** whose content is fixed by nomic/informational relations to the world, not by internal structure. BACHELOR means bachelor; possessing it does not require possessing [UNMARRIED & MALE] [established].

Fodor's *radical concept nativism* (that atoms are largely innate) "has had few supporters," but — the telling admission from his critics — "it has proven difficult to say exactly what's wrong with Fodor's argument" (Laurence & Margolis; Stanford Encyclopedia, *Word Meaning*, 2025) [established]. The anti-decomposition core is far more robust than the nativist conclusion attached to it.

**Verdict (Fodor):** This is the **FUNDAMENTAL** ceiling on the *scientific* reading of any primitive basis, NSM's included. A Fable-class model does **not** dissolve it, because it is an argument about the *nature of concepts*, not about our tooling. **But it is precisely bounded:** Fodor attacks decomposition *as a theory of what concepts are*. He does **not** show that a stipulated, canonical *description* in primitives is useless — indeed dictionaries, interlinguas, and the kernel all live in the space Fodor leaves open (useful conventional paraphrase, not discovered structure). The kernel must site itself on the descriptive side of the Fodor line.

### 2.3 Jackendoff — Conceptual Semantics (the survivor, by lowering the bar)

Jackendoff (1983 *Semantics and Cognition*; 1990 *Semantic Structures*; 2002 *Foundations of Language*; 2025 "Toward a Deeper Lexical Semantics," *Topics in Cognitive Science*) posits a finite set of **ontological categories** (Event, State, Thing, Path, Place, Property, Amount, Time) and combination principles, with primitives like GO, BE, STAY, CAUSE, INCH, and spatial/force-dynamic features [established]. It survives where Katz-Fodor died because Jackendoff **abandons the strong reductive claim**: decomposition need not bottom out in a finite universal alphabet, primitives may be partial, and the theory targets the *form* of conceptual structure, not exhaustive definitions. His 2025 paper explicitly pushes toward richer, more graph-like lexical entries — i.e., **away** from a small tidy basis. Notably, Jackendoff's function-argument structures (CAUSE(x, GO(y, PATH))) are **structurally isomorphic** to the kernel's predicate + role→filler clause AST — the kernel's `pred = prime + role-map` is Conceptual-Semantics-shaped, not NSM-shaped, in its combinatorics.

**Verdict (Jackendoff):** Survival-by-bar-lowering is itself the lesson: the decomposition that lives is *structural and partial*, not *reductive and complete*. CAPABILITY-LIMITED where it concerns building the structures (LLMs can now propose them); FUNDAMENTAL where it concerns completeness (there is no finite floor). **Directly relevant: the kernel should model its combinatorics on Jackendoff (typed roles, partial structure) and NOT stake itself on NSM's stronger reductive-completeness claim.**

### 2.4 Schank — Conceptual Dependency (the cautionary AI tale)

Schank (1972, 1975 "The Primitive ACTs of Conceptual Dependency," TINLAP; Schank & Abelson 1977 *Scripts, Plans, Goals and Understanding*) reduced verbs to **~11 primitive ACTs** (ATRANS, PTRANS, MTRANS, MBUILD, INGEST, EXPEL, PROPEL, MOVE, GRASP, SPEAK, ATTEND) plus states and a dependency grammar [established]. This is the closest historical analogue to the kernel's ambition: a *tiny* action basis, canonical case-role structure, language-neutral representation, composition by binding roles to fillers. It powered MARGIE, SAM, PAM in the 1970s-80s.

Why it failed [established as the standard post-mortem]:
- **The primitives under-determined meaning** — "kiss," "hit," and "point at" all reduce toward MOVE-bodypart, losing distinctions; the residue was smuggled into un-primitive-ised modifiers.
- **Scripts exploded** — canonical event structure required hand-built scripts per situation; no coverage, no learning, brittle.
- **No principled inventory** — 11 ACTs was a working guess; nobody could derive or bound it.

A 2026 arXiv preprint ("Do Neurons Dream of Primitive Operators? Wake-Sleep Compression Rediscovers Schank's Event Semantics," arXiv:2603.25975) [claimed] reports that a neural program-compression system *rediscovers Schank-like primitive operators* — a CAPABILITY-LIMITED reframing: the primitives may have been roughly right, but hand-authoring the decompositions and scripts was the fatal bottleneck.

**Verdict (Schank):** The most important precedent for the kernel, and the most sobering. The **architecture** (small ACT basis + role binding + canonical structure) is almost exactly the kernel's, and it **failed on coverage and hand-authoring, not on the core idea** — that part is CAPABILITY-LIMITED and is exactly what a Fable-class explication-writer attacks. But the **under-determination** failure (primitives too coarse to preserve meaning distinctions) is FUNDAMENTAL to any *small* basis and is the kernel's single biggest inherited risk. The kernel's answer — recursive reference to *other concepts'* canonical vectors (molecules), not just primes — is precisely the escape hatch Schank lacked, and its viability is the crux experiment.

### 2.5 Wilks — Preference Semantics (the honest concession)

Wilks (1975 "A Preferential, Pattern-Seeking Semantics"; Fass & Wilks 1983) built MT/understanding on ~80-100 semantic primitives with **preferences** (soft selection restrictions: "hit" *prefers* a HUMAN agent) rather than hard rules, which gracefully handles metaphor and ill-formedness [established]. Crucially, Wilks himself later ("Semantic Primitives: The Tip of the Iceberg," in the Sparck-Jones festschrift) concluded that **fewer than 100 primitives are nowhere near enough** — the working vocabulary for definitions needs ~1000 central terms out of a ~2000+ defining vocabulary [established]. This is a *quantitative* verdict from inside the primitive-semantics camp: **the useful basis is ~1000, not ~65-100.**

**Verdict (Wilks):** The soft-preference idea is CAPABILITY-LIMITED and, honestly, *vindicated* — modern embeddings are soft preferences. But Wilks's headcount is a **FUNDAMENTAL** warning to the kernel: a 65-prime floor is likely a factor of ~10-15 too small to carry lexical meaning without a large molecule tier. The kernel's molecule/reference machinery is not optional decoration; Wilks says it is where most of the actual meaning must live.

### 2.6 Mel'čuk — Meaning-Text Theory / Lexical Functions (the relational alternative)

Mel'čuk's MTT (1974-onward; *Semantics: From Meaning to Text*, 3 vols 2012-2015) offers a different decomposition: not into a substance-basis of primitives but into **~60 standard Lexical Functions** — abstract, language-universal relations (MAGN = intensifier, OPER/FUNC/LABOR = light-verb support, ANTI, SYN, CONV, INCEP, CAUS, LIQU, ...) that map a keyword to its idiomatic collocates/paradigmatic relatives, organised in the Explanatory Combinatorial Dictionary [established]. It is the most computationally successful of the classical decompositions in narrow tasks (collocation, paraphrase, generation, MT) and remains in use.

**Verdict (Mel'čuk):** MTT's lesson for the kernel is **decompose the RELATIONS, not (only) the substance.** The kernel's role→filler bindings and inter-concept references are closer to Lexical Functions than to NSM primes. That ~60 relations recur here — alongside NSM's 65 primes and Binder's 65 features — is suggestive that *the tractable basis for the relational/structural layer is small*, even if the substance layer is not. CAPABILITY-LIMITED and largely positive; the kernel underuses this tradition and should mine it for its role/operator inventory.

### 2.7 Cross-cutting verdict on classical decomposition

The programme failed **twice over**, and the two failures have opposite prognoses:
- **Engineering failure** (no automatic decomposer; hand-built; no coverage; brittle scripts): **CAPABILITY-LIMITED.** This is the failure LLMs erase. It is why NSM has ~hundreds of explications after 50 years and DeepNSM can generate ~44k in a week (companion report §1.1).
- **Theoretical failure** (meaning is not finite composition of primitives; Fodor; under-determination of any small basis; open-ended definiens; polysemy of the primitives themselves): **FUNDAMENTAL.** No model dissolves it.

The kernel is viable **iff** it lives entirely on the capability-limited side: it must claim *canonical description in a conventional interlingua*, never *discovery of conceptual atoms*, and it must not bet on a 65-prime floor carrying meaning alone (Wilks, Schank under-determination).

---

## 3. Harnad's symbol grounding problem and the dictionary "grounding kernel"

### 3.1 The problem (Harnad 1990)

Harnad, "The Symbol Grounding Problem," *Physica D* 42:335-346 [established]. A pure symbol system (symbols defined only by other symbols) is a **merry-go-round**: like learning Chinese from a Chinese-only dictionary, you can traverse forever without ever connecting a symbol to its referent. Meaning cannot be grounded in more symbols; some symbols must be grounded **directly** (Harnad's proposal: in sensorimotor categorisation / perceptual invariants). This is *the* framing objection to any purely internal-relational semantics — including a VSA that binds primes to primes.

**Bearing on the kernel (blunt):** The kernel is, by construction, a symbol-to-symbol system. Primes are defined by fixed Hadamard rows; concepts are compositions of primes and *other concepts*. **Nothing in the kernel touches a referent.** By Harnad's lights the kernel is ungrounded *in principle* — it is a beautifully structured merry-go-round. This is **FUNDAMENTAL** and cannot be waved away: the kernel does not *solve* symbol grounding; at best it provides a *canonical internal scaffold* that an already-grounded system (an LLM whose embeddings are grounded distributionally, or a multimodal model grounded perceptually) can be aligned to. The E-BERT precedent (companion report §5) is the honest model: an externally-built vector is useful iff *linearly aligned into an already-grounded space*. The kernel's grounding, if any, is **borrowed**, not intrinsic.

### 3.2 The "vector grounding problem" (the modern update)

Mollo & Millière 2023, "The Vector Grounding Problem" (arXiv:2304.01481) [established as a position] reframe grounding for LLMs: they distinguish *referential* grounding (which they argue RLHF-tuned LLMs partially achieve via feedback loops to the world) from sensorimotor/embodied grounding. The live debate matters for the kernel's *pitch*: if one holds LLMs are already referentially grounded, then a training-free symbolic kernel injected into them inherits that grounding; if one holds they are not, the kernel adds structure but not grounding. **Either way, the kernel is not an independent grounding solution** [speculative — our synthesis].

### 3.3 The dictionary grounding-kernel line — Harnad, Blondin-Massé, Vincent-Lamarre

This is the line the kernel's **X1-grounding** experiment directly tests, so it gets the most careful treatment.

**Method & headline results** (Blondin Massé et al. 2008, arXiv:0806.3710; Vincent-Lamarre, Blondin Massé, Lopes, Lord, Marcotte & Harnad 2016, "The Latent Structure of Dictionaries," *Topics in Cognitive Science* 8:625-659; "Hidden Structure and Function in the Lexicon," arXiv:1308.2428; "Psycholinguistic Correlates of Symbol Grounding in Dictionaries," 2016) [established]:
- Model a dictionary as a directed graph: edge from each **defining** word to each **defined** word. Recursively delete words that are *reachable* by definition but never themselves *define* anything.
- What remains is the **Grounding Kernel (~10%** of the dictionary) — the words out of which all others can be defined.
- The Kernel splits into one large **strongly connected component, the Core (~half the Kernel)**, plus small SCCs (**Satellites**) around it.
- Inside the Kernel, the smallest sets from which everything can be reached — **Minimal Grounding Sets (MinSets)**, computed as minimum feedback vertex sets — are **~1% of the whole dictionary** (~15% of the Kernel), and there are *many* alternative MinSets.

**The psycholinguistic finding — the decisive one for us** [established, from "Psycholinguistic Correlates" 2016]:
- **Frequency tracks grounding depth: Core > Satellites > Rest.** Core words are the *most frequent*, then Satellites, then the Rest.
- **Core words are learned earlier (lower age of acquisition), more frequent, and LESS concrete than Satellites.** Satellites are learned earlier and more frequent than the Rest, but *more concrete* than the Core.
- Every MinSet has a younger/more-frequent **C-part** and a more-concrete **S-part**.

So the grounding Core is characterised by **high frequency + early acquisition + (relative) abstractness** — i.e. exactly the profile of function-word-like, high-out-degree defining vocabulary. This is the single most important external fact for interpreting X1 (§6).

**Verdict (dictionary grounding-kernel):** A real, replicated structural result — dictionaries *do* have a compressible grounding skeleton, and it *is* ~1-10% of the vocabulary. **But two hard limits.** (i) It is a result about the *dictionary graph's* internal compressibility, **not** about grounding in Harnad's referential sense — the authors are explicit that the Kernel still has to be grounded *outside* language (sensorimotor); the graph just tells you the *minimum set you'd have to ground directly*. (ii) The Core's defining property is **frequency**, which makes Core membership nearly uninformative as a *selectivity* signal — a fact that predicts our X1 null result. This line is CAPABILITY-LIMITED as to *computing* MinSets (NP-hard FVS, but tractable heuristically) and FUNDAMENTAL as to what it can prove about grounding (it proves compressibility, not grounding).

---

## 4. WordNet as a semantic basis, and gloss-graph structure

- **WordNet is a relational, not a primitive, semantics** [established]: ~117k synsets linked by hypernymy/hyponymy, meronymy, antonymy, etc. It has no privileged primitive layer; meaning is position in the graph. This is the anti-thesis of NSM — grounding by *relations among all words*, not reduction to a floor.
- **Unique Beginners / base concepts.** WordNet's noun hierarchy roots in ~25 "unique beginners" (Miller 1990) and later EuroWordNet/Global-WordNet "Base Concepts" (~4,700-8,000 concepts selected by high position + high connectivity) [established]. These are the WordNet-native analogue of a "primitive basis," and note the size: **thousands, not tens** — converging with Wilks's ~1000 headcount and *against* NSM-65 as a sufficient basis.
- **Gloss graphs & dictionary circularity.** Every WordNet gloss is written in ordinary words that are themselves in WordNet, so the gloss graph is a self-defining dictionary — precisely the substrate for the Vincent-Lamarre analysis, and precisely what X1-grounding built (117,791 synsets → definer→defined graph). Extended WordNet (Harabagiu et al.) and the eXtended WordNet Knowledge Base parse glosses into relations; these show glosses carry exploitable definitional structure (genus/differentia) [established].
- **WordNet as a vector basis.** Poincaré embeddings (Nickel & Kiela 2017) show the noun hypernymy graph embeds in *very* low dimension hyperbolically; path2vec, retrofitting, and Numberbatch (companion report §3) show WordNet structure *refines* distributional vectors but does **not** produce a competitive space alone [established].

**Verdict (WordNet):** WordNet is the best-available *substrate* for the kernel's grounding experiments (it is what X1 used) and a useful source of relational structure, but it argues **against** a tiny primitive basis: its own "base concept" layer is thousands strong. CAPABILITY-LIMITED as data; FUNDAMENTAL as a counter-datum to NSM-65 sufficiency.

---

## 5. Feature norms and brain-based semantic features — the small-basis existence proofs

This is where "canonical vectors from tens of primitives" has actually been *built and evaluated*, so it directly answers Q1.

### 5.1 McRae feature production norms (McRae, Cree, Seidenberg & McNorgan 2005; Buchanan et al. 2019 extension to 4,436 concepts)

Human participants list features for concepts (*dog*: `is an animal`, `has four legs`, `barks`); features are pooled and weighted by production frequency [established]. Powers models of categorisation, priming, and the living/nonliving deficit. **But:** the feature *space* is large (thousands of features), sparse, and correlated; it is a *distributed* representation, not a *small primitive basis*. It is evidence that concepts *have* decomposable featural structure, and simultaneously evidence that the number of features is **large and open-ended** — a point *for* decomposability and *against* smallness.

**Verdict:** CAPABILITY-LIMITED (elicitation is laborious; LLMs can now approximate norms — cf. "Probing BERT for nouns' semantic properties"). Supports *featural* decomposition; does **not** support a *small* basis.

### 5.2 Binder et al. 2016 — brain-based componential semantics (the closest existence proof)

Binder, Conant, Humphries, Fernandino, Simons, Aguilar & Desai 2016, "Toward a Brain-Based Componential Semantic Representation," *Cognitive Neuropsychology* 33:130-174 [established]. **65 experiential attributes** (Vision, Bright, Dark, Color, Motion, Shape, ... Audition, Touch, Taste, Smell, ... Body-action, ... Space, Time, ... Emotion, Reward, ... Cognition, Social, ...) grouped into 14 domains, each with a **defined neural substrate** from meta-analysis; 535 words rated 0-6 per attribute by humans. The result: a **65-dimensional, interpretable, componential vector per concept**, grounded in brain systems rather than corpus statistics.

Downstream: **Utsumi 2020** ("Exploring What Is Encoded in Distributional Word Vectors," and the *Computational Linguistics* 47(3) "Decoding Word Embeddings with Brain-Based Semantic Features") shows Binder features can be **decoded from** and used to interpret distributional embeddings, and that the 65 dims explain semantic behaviour and brain activation [established]. Anderson et al. and Fernandino et al. used Binder features to predict fMRI. A 2023 *Scientific Data* release extended the ratings computationally.

**This is the strongest published "small canonical basis" result** — and its properties are exactly the honest bar for the kernel:
- The basis is **~65, interpretable, motivated by an external ground (brain systems)** — structurally the best analogue to NSM-65-with-a-story.
- **But the vectors are human-rated, not training-free**, and the readout to embeddings/brain is a **trained/fitted linear map**. Quality is "decodes and predicts significantly," never "replaces distributional vectors."

**Verdict (Binder):** The kernel's best friend and its sharpest mirror. It proves a ~65-dim interpretable concept space *can* be built and *is* useful — **CAPABILITY-LIMITED and positive on existence.** But it achieves this via human grounding + a trained readout, neither of which the kernel has; the residual gap (training-free + deterministic + no human ratings) is unproven and is the kernel's actual novelty and risk.

### 5.3 Mitchell et al. 2008 — predicting brain activity from a 25-verb basis

Mitchell, Shinkareva, Carlson, Chang, Malave, Mason & Just 2008, "Predicting Human Brain Activity Associated with the Meanings of Nouns," *Science* 320:1191-1195 [established]. A concrete noun's fMRI activation is predicted as a **linear combination of 25 hand-chosen sensory-motor verbs** (see, hear, listen, taste, smell, eat, touch, rub, lift, manipulate, run, push, fill, move, ride, say, fear, open, ...), with the noun's loading on each verb given by **corpus co-occurrence**. It predicts held-out nouns' brain images above chance.

**Why it matters here:** it is a *literal* success of "canonical vectors from tens of primitives" — 25 primitives, interpretable, predictive of an external ground (the brain). **But** the basis is hand-picked, the loadings are distributional (corpus co-occurrence), and the map to fMRI is *trained*. Remove all three and you have the kernel; nobody has shown the kernel's all-deterministic version works.

**Verdict (Mitchell):** CAPABILITY-LIMITED and positive on existence of a small predictive basis; but the small basis succeeds *because* it is coupled to distributional loadings and a trained readout. It is evidence *for* small bases and *against* fully training-free ones.

### 5.4 Cross-cutting verdict on feature/brain bases (answers Q1 directly)

The small-basis programme **succeeds** in the brain/behaviour-grounded, human-rated, trained-readout regime (Mitchell 25, Binder 65) and **fails to have been attempted** in the training-free deterministic regime the kernel occupies. The recurrence of **~25-65** as the workable *interpretable* dimensionality (Mitchell 25, Binder 65, NSM 65, Mel'čuk ~60) is a genuine and encouraging regularity [speculative — the convergence is real, the causal story is not established]. The discouraging half: every success buys its quality with *grounding the kernel does not have* (human ratings, distributional loadings, trained maps). **The kernel's bet is that fixed orthonormal codebook rows + algebraic binding can substitute for learned loadings. No prior art confirms this substitution works, and Schank/Wilks warn the substance layer needs far more than 65 atoms.**

---

## 6. Confronting X1-grounding honestly — does the literature predict our null?

**Recap of the result** (`poc/x1-grounding/results/x1g-report.md`): On the WordNet-3.1 gloss graph, of 51 evaluable NSM primes, **50/51 land in the dictionary Core** (T_core = 0.9804). But a **frequency-matched null** lands in the Core **97.0%** of the time (null mean 0.9705), giving enrichment ratio **~1.01, p ≈ 0.58**. Verdict: FAIL — "no detectable selectivity." The Core spans **88.6% of the Kernel** and ~97% of frequency-matched high-out-degree content words; Core membership is near-universal and near-uninformative. The report reads this as a **ceiling/saturation** effect, not evidence primes are absent.

**Does the prior literature predict this? — Yes, precisely, and from two independent directions.**

1. **The Vincent-Lamarre psycholinguistic result predicts it mechanically.** The Core's defining property is **high frequency** (Core > Satellites > Rest, §3.3). NSM primes are, by design, among the highest-frequency, earliest-acquired, most-abstract words — the *exact* profile of the Core. A null that *matches on frequency* therefore matches on the very property that *causes* Core membership. Under this construction, "primes are in the Core" and "frequency-matched words are in the Core" are the **same statement**, so ER ≈ 1 is the *expected* outcome, not a surprising one. **The X1 null is a textbook confound-controlled-away result: once you control for frequency, the apparent selectivity vanishes because frequency was the whole signal.** [established chain of reasoning from Vincent-Lamarre 2016.]

2. **The size/saturation of the Core predicts it.** Our own census: Core = 88.6% of Kernel (vs the 2016 paper's Core ≈ 50% of Kernel). Our Core is *far larger* relative to the Kernel than the published dictionaries', so Core membership carries even *less* information here than in the original studies. When ~97% of eligible content words are in the Core, no subset can be "enriched" in it. This is a **ceiling artifact of the WordNet gloss graph**, plausibly because WordNet glosses are written in a broad, self-referential content vocabulary with high mutual reachability. [established from the X1 census + 2016 comparison.]

**Does the null undermine NSM-65 as the basis? — No. It undermines one selectivity CLAIM, not the basis choice.** Three reasons:
- The pre-registered X1 question was *"is the empirical floor of definitions where NSM says it is, above chance?"* The answer is "primes ARE on the floor (50/51 in Core) but so is everything frequent." That refutes a **strong distinctiveness claim** (primes are *specially* selected by the dictionary's grounding structure) — a claim NSM does not actually need and the kernel never depended on. NSM's basis claim is about *reductive adequacy* (you can define things in primes) and *universality* (lexicalised everywhere), **not** about primes being graph-theoretically distinguished in a specific dictionary's gloss graph.
- The test had **known low power for NSM-shaped items by construction**: 14 of 65 primes (the function-word/deictic/logical ones: IF, BECAUSE, THIS, YOU, ...) were *excluded* because WordNet has no closed-class nodes (PREREG §2.4, §5.1) — i.e., the most "grounding-floor-like" primes were structurally invisible to the very graph meant to test them. The saturation confound plus the exclusion of the strongest candidates make this a weak instrument for the distinctiveness claim, not a strong refutation of NSM.
- **The convergent literature actively expects "primes ≈ high-frequency defining vocabulary, not a magic subset."** Wilks (§2.5): the real defining vocabulary is ~1000 central terms, of which primes are a *fraction*, not a graph-distinguished elite. The dictionary-kernel work never claimed the ~1% MinSet coincides with any theorist's primitive list — indeed MinSets are **non-unique** and heuristically chosen, explicitly *not* a canonical primitive inventory. So "NSM primes are not a distinguished FVS/Core subset" is the *predicted* relationship, not an anomaly.

**What X1 legitimately costs the programme:** it kills the cheap, attractive claim that *"the dictionary's own structure ratifies NSM's choice of primes."* It does not license switching the basis to a "dictionary-derived core," because the dictionary-derived Core here is 88.6% of the Kernel — it is not a small, clean, alternative basis; it is nearly the whole content vocabulary. The pre-registered "Fail → switch to dictionary core" branch is therefore **under-warranted by its own result**: there is no crisp dictionary core to switch *to*. The honest conclusion is **null on selectivity, basis choice untouched, and the MinSet route offers no smaller principled basis than NSM already provides.**

**Capability vs fundamental (X1):**
- The **saturation/ceiling** is a property of the WordNet gloss graph + word-level sense collapse + frequency confound. It is **not** capability-limited in the model sense (a Fable-class model does not change a graph statistic), but it **is instrument-limited**: a different substrate (full Wiktionary — the deferred X1b; sense-level rather than word-level nodes; or a *learner-directed* dictionary like the Longman Defining Vocabulary, which is an actual ~2000-word controlled defining set) could give a non-saturated Core and a real selectivity test. So the *specific null* is **CAPABILITY/INSTRUMENT-LIMITED** (better substrate could move it), while the *underlying fact* — that frequency, not primitivity, drives Core membership — is **FUNDAMENTAL** (Vincent-Lamarre).
- The deeper point the null gestures at (that a dictionary's internal graph cannot *ground* or *ratify* a primitive basis, because it is a symbol-to-symbol structure) is **FUNDAMENTAL** — it is Harnad's merry-go-round restated as a null result. **No dictionary-graph experiment can validate the kernel's grounding, because dictionary graphs are exactly the ungrounded symbol systems Harnad diagnosed.**

**One concrete recommendation from this section:** retire the "dictionary structure ratifies NSM" line of argument entirely; it is both unsupported (X1) and category-mistaken (Harnad). Replace it with the Binder/Mitchell-style bar: validate the kernel by whether its vectors *decode into* an already-grounded space (LLM embeddings, fMRI, behaviour), not by whether primes are distinguished inside a dictionary graph.

---

## 7. Implications for the decisive experiments (what this dive changes about methodology)

1. **Move the validation target from "dictionary-internal selectivity" to "cross-space decodability."** X1 shows dictionary-graph tests are saturated and, per Harnad, category-mistaken for grounding. The decisive experiments should mirror Binder/Mitchell/E-BERT: can a *fixed* linear map carry kernel vectors into (a) LLM input-embedding space (E-BERT protocol), (b) Binder-65 brain-feature space, or (c) fMRI/behaviour? If a *frozen* kernel vector linearly decodes a concept's Binder features or its distributional neighbours, that is real, grounded evidence; dictionary Core-membership is not.

2. **Do not stake the programme on the 65-prime floor carrying meaning.** Wilks (~1000), WordNet base concepts (thousands), Schank (under-determination), and McRae (thousands of features) converge: the substance layer needs far more than 65 atoms. The decisive experiment must stress-test the **molecule/reference tier** (concepts binding other concepts' canonical vectors) — that is where the kernel's meaning capacity must actually reside, and it is the exact mechanism Schank lacked. Design an experiment that isolates *how much* meaning distinction survives with primes-only vs primes+molecules.

3. **Adopt the Fodor/Jackendoff siting explicitly.** Frame every claim as *canonical description in a conventional interlingua* (Fodor-safe), never *discovery of conceptual atoms*. Prefer Jackendoff-style *partial, structural, typed* decomposition over NSM-style *complete reductive* decomposition — the kernel's clause AST already is Jackendoffian; lean into it and drop reductive-completeness claims.

4. **Instrument the grounding-kernel test properly before re-running it (X1b), or drop it.** If the dictionary-graph line is kept at all, run it on (a) a controlled Defining-Vocabulary dictionary (Longman LDOCE ~2000-word defining vocabulary) where a real, small, non-saturated core exists, and (b) sense-level not word-level nodes. Otherwise the Core is 88.6% of the Kernel and no selectivity test has power. But per §6, the higher-value move is to *abandon* dictionary-internal validation for cross-space decodability.

5. **Steal from Mel'čuk for the relational inventory.** The kernel's roles/operators are under-specified relative to MTT's ~60 Lexical Functions. If ~60 relations recur across MTT, and ~65 across NSM and Binder, the *structural* layer is plausibly small even if the substance layer is not — a testable asymmetry: hold the role inventory at ~60 and let the concept (filler) inventory grow large.

6. **Report the null as designed-for, not embarrassing.** X1's FAIL is a correctly controlled result predicted by Vincent-Lamarre; it is a *strength* of the pre-registration, not a wound. Its lesson (frequency ≠ primitivity; dictionary graphs can't ground) sharpens the programme. Communicate it that way.

---

## 8. Sub-line verdict table (capability-limited vs fundamental)

| Sub-line | Core finding | Verdict lens |
|---|---|---|
| NSM inventory (Wierzbicka/Goddard) | Small closed cross-translatable set; universality & reductive-completeness contested | Engineering CAPABILITY-LIMITED (usable); science FUNDAMENTAL (unproven) |
| Katz-Fodor markers | Died on distinguisher residue + Fodor's defection | FUNDAMENTAL (no definitions survive) |
| Fodor atomism | No successful definitions; no processing cost for "complex" verbs; atoms | FUNDAMENTAL barrier to decomposition-as-theory; leaves *description* open |
| Jackendoff Conceptual Semantics | Survives by dropping reductive-completeness; partial structural primitives; isomorphic to kernel AST | CAPABILITY-LIMITED (build structures) + FUNDAMENTAL (no finite floor) |
| Schank Conceptual Dependency | ~11 ACTs; failed on coverage/hand-authoring AND under-determination | Authoring = CAPABILITY-LIMITED (LLMs fix); under-determination = FUNDAMENTAL |
| Wilks preference semantics | Soft preferences vindicated; but needs ~1000 not ~65 primitives | Soft = CAPABILITY-LIMITED; headcount = FUNDAMENTAL warning |
| Mel'čuk MTT / Lexical Functions | ~60 universal relations; decompose relations not substance; kernel underuses it | CAPABILITY-LIMITED, positive; mine it |
| Harnad symbol grounding | Symbol-to-symbol system is a merry-go-round; kernel is one | FUNDAMENTAL; kernel's grounding is borrowed, not intrinsic |
| Dictionary grounding-kernel (Vincent-Lamarre) | ~1% MinSet / ~10% Kernel; Core = high-freq/early/abstract; proves compressibility not grounding | Compute = CAPABILITY-LIMITED; grounding claim = FUNDAMENTAL |
| WordNet as basis | Relational not primitive; base concepts number in thousands | Data CAPABILITY-LIMITED; counter-datum to NSM-65 sufficiency = FUNDAMENTAL |
| McRae feature norms | Featural decomposition real but thousands of features | Elicitation CAPABILITY-LIMITED; smallness disconfirmed |
| Binder 2016 (65 brain features) | Best small-basis existence proof; human-rated + trained readout | CAPABILITY-LIMITED & positive on existence; training-free gap unproven |
| Mitchell 2008 (25 verbs) | Literal small-basis brain prediction; distributional loadings + trained map | CAPABILITY-LIMITED & positive; disconfirms *fully* training-free |
| X1-grounding null (ours) | Primes in Core but so is everything frequent; ER≈1.01, p≈0.58 | Specific null = INSTRUMENT-LIMITED; freq-drives-Core = FUNDAMENTAL |

---

## 9. Key references

- Harnad, S. (1990). The Symbol Grounding Problem. *Physica D* 42:335-346.
- Blondin Massé, A. et al. (2008). How Is Meaning Grounded in Dictionary Definitions? arXiv:0806.3710. TextGraphs-3.
- Vincent-Lamarre, P., Blondin Massé, A., Lopes, M., Lord, M., Marcotte, O. & Harnad, S. (2016). The Latent Structure of Dictionaries. *Topics in Cognitive Science* 8:625-659. (+ arXiv:1308.2428 "Hidden Structure and Function in the Lexicon"; "Psycholinguistic Correlates of Symbol Grounding in Dictionaries," ePrints Soton 366805.)
- Mollo, D. C. & Millière, R. (2023). The Vector Grounding Problem. arXiv:2304.01481.
- Katz, J. & Fodor, J. (1963). The Structure of a Semantic Theory. *Language* 39:170-210.
- Fodor, J. (1970). Three Reasons for Not Deriving "Kill" from "Cause to Die." *Linguistic Inquiry* 1:429-438. Fodor, J. (1998). *Concepts: Where Cognitive Science Went Wrong.* OUP. Fodor, Garrett, Walker & Parkes (1980), *Cognition* 8:263-367.
- Laurence, S. & Margolis, E. Radical Concept Nativism. Stanford Encyclopedia of Philosophy, *Word Meaning* (2025 ed.).
- Jackendoff, R. (1983) *Semantics and Cognition*; (1990) *Semantic Structures*; (2002) *Foundations of Language*; (2025) Toward a Deeper Lexical Semantics, *Topics in Cognitive Science*.
- Schank, R. (1975). The Primitive ACTs of Conceptual Dependency. TINLAP, ACL Anthology T75-2008. Schank & Abelson (1977) *Scripts, Plans, Goals and Understanding*.
- Wilks, Y. (1975). A Preferential, Pattern-Seeking Semantics. *Artificial Intelligence* 6. Wilks, Y. Semantic Primitives: The Tip of the Iceberg (Sparck-Jones festschrift). Fass & Wilks (1983), ACL Anthology J83-3004.
- Mel'čuk, I. (2012-2015). *Semantics: From Meaning to Text*, 3 vols. Benjamins. Lexical Functions / Explanatory Combinatorial Dictionary.
- Miller, G. et al. (1990). WordNet. *Int. J. Lexicography* 3. Nickel & Kiela (2017), Poincaré Embeddings, NeurIPS.
- McRae, K., Cree, G., Seidenberg, M. & McNorgan, C. (2005). Semantic feature production norms. *Behavior Research Methods* 37:547-559. Buchanan et al. (2019) extension, *Behavior Research Methods*.
- Binder, J. et al. (2016). Toward a Brain-Based Componential Semantic Representation. *Cognitive Neuropsychology* 33:130-174. Utsumi (2020/2021), Decoding Word Embeddings with Brain-Based Semantic Features, *Computational Linguistics* 47(3).
- Mitchell, T. et al. (2008). Predicting Human Brain Activity Associated with the Meanings of Nouns. *Science* 320:1191-1195.
- Riemer, N. (2006). Reductive Paraphrase and Meaning. *Linguistics & Philosophy* 29. von Fintel & Matthewson (2008). Universals in Semantics. *The Linguistic Review* 25. (Both detailed in companion report `nsm-and-knowledge-injection.md`.)
- Repo: `poc/x1-grounding/results/x1g-report.md`, `poc/x1-grounding/PREREG.md`, `encoder/src/lexicon.ts`.
