# Kernel construction methodology — research dossier (bead kernel-of-truth-99a)

> Produced 2026-07-07 by a 6-agent Fable research workflow (5 parallel angles +
> synthesis), each grounded in this repo. Commissioned after @jeswr questioned the
> whole construction methodology: is LLM-generation the right substrate, or should
> meaning be sourced from a dictionary (his idea), or extracted from a model's
> internals (his future-state idea)? Ask: theory-grounded best approach + honest
> uncertainties + a proper sequenced experiment programme.
>
> HEADLINE: recommended path is a HYBRID with sharply assigned roles — dictionary =
> content authority, dictionary-graph = scaffold, NSM = provisional stipulated base,
> LLM = demoted to SOURCE-CHECKED TRANSLATOR (not author), reconciliation = settlement,
> model-internals = external referee (never substrate). Hard caveat: on the strongest
> theory (Fodor), concepts likely have no discovered definitional structure — so
> "canonical" = canonical-BY-CONVENTION (like SI units), which is fatal to a literal
> "can't-misunderstand" pitch and non-fatal to everything else. Decision spine: run
> X1 (free/CPU/days) + X2 (the key one, ~weeks/$hundreds) to settle it empirically.
> See [[kernel-of-truth-program]], [[kern-working-mode-2026-07]], and notes/reconciliation-identity-research.md.

---

# How should we build the kernel? A synthesis of the theory, honestly

## 1. What we are actually deciding

Every construction method for the kernel has to answer three separate questions, and much of the confusion comes from treating them as one:

1. **Where does the *content* of a definition come from?** (An author's judgment? A dictionary? A model's training data? A model's internal circuitry?)
2. **What makes a definition *the* definition** — canonical — rather than one of many defensible paraphrases?
3. **What connects the whole structure to the world**, so it isn't just symbols defined by other symbols?

Five terms, defined once:

- **Semantic primes (NSM).** Wierzbicka and Goddard's claim that ~65 words (SOMEONE, WANT, GOOD, BECAUSE...) are indefinable, exist in every language, and suffice to paraphrase everything else. Our current explications are written in this vocabulary.
- **Grounding kernel.** A result from Harnad's group (Vincent-Lamarre, Blondin Massé et al., "The Latent Structure of Dictionaries," 2016): treat a dictionary as a graph (definition words point to the word defined), repeatedly delete words that define nothing else, and you always land on the same unique core — about 10% of the dictionary suffices to define the rest. This is your dictionary-plus-convergence idea, already formalized, with theorems.
- **Symbol grounding problem.** Harnad's 1990 argument that a system whose symbols are defined only by other symbols is like learning Chinese from a Chinese–Chinese dictionary: perfectly structured, meaning-free. Something must connect the base symbols to the world non-definitionally.
- **SAE features.** A sparse autoencoder is a small trained network that decomposes an LLM's internal activations into thousands of "features" — directions that each fire on a coherent theme. This is the tooling behind your "deconstruct a local model" idea.
- **LLM-as-proposer vs. LLM-as-source-of-truth.** The decisive distinction for your Haiku worry. If the model's output *is* the definition, the "canonical" meaning is one vendor's compression of internet text — your circularity worry, and it's correct. If the model merely *proposes* candidates and an independent authority accepts or rejects them, the model's provenance stops mattering — the same way a proof found by a stochastic search is still a proof (this is how AlphaGeometry and FunSearch earn their legitimacy). The soundness then lives entirely in the verifier.

The real choice, then, isn't "Wikipedia vs. dictionary vs. Haiku." It is: **which component holds semantic authority, and can that component be external, auditable, and order-invariant?**

## 2. The candidates, scored against our own criteria

| | Canonical? | Deterministic? | Training-free? | Grounded / non-circular? | Convergent? | Scalable? |
|---|---|---|---|---|---|---|
| (a) LLM-generated NSM (current) | **No** — one model's opinion | Reproducible, not canonical: temp-0 makes the same opinion repeat | Construction yes; content is distilled training | **No** — this is your worry, and it stands | Unknown — the key untested number | Yes (proven, ~2.3k records) |
| (b) Dictionary graph + convergence | Structure **yes** (unique kernel, confluent reduction); minimal basis **no** (many MinSets) | Yes | Yes, if extraction survives | Provenance yes; base-layer meaning still unglued | Yes — mathematically guaranteed for the reduction | Extraction is the historical graveyard |
| (c) Model-internal extraction (SAEs) | **No** — features vary by seed/width/model | **No** (~65–70% feature overlap across mere reseeds) | **No** — SAEs are trained | Partly — measured computation over usage, with causal checks | Only via cross-model agreement, which is fragile (see E8-ext) | Expensive |
| (d) Hybrid: dictionary authority + LLM translator + internals as referee | By construction where fixpoints agree; by fiat elsewhere | Yes for the artifact | Yes for the artifact | Content anchored to auditable source; validation rents grounding from trained systems | The thing the reconciliation design exists to deliver | Plausible; unproven |

Three honest annotations to that table.

**On (a).** The current pipeline is better than you may think: Haiku drafts from pinned, hash-checked Wiktionary/Wikipedia revisions, outputs pass grammar gates, and every record is marked sub-canonical (`ModelAuthored`) with full provenance. But the gates check **form, not truth**: a perfectly grammatical explication of "umbrella" that actually describes a parasol passes everything. On the axis you care about, Haiku is still the de facto source of truth. Verdict from the pipeline review: *a verified proposer for form, an unverified oracle for content.*

**On (b).** Your proposal has a distinguished pedigree and a documented failure mode. The pedigree: the grounding-kernel results above, plus Formal Concept Analysis (Ganter & Wille), which gives a provably unique concept lattice from a relations table — genuinely the right mathematics for "settle the relations." The failure mode: the step "turn each definition into relations" is where forty years of machine-readable-dictionary research died (Ide & Véronis's 1993 post-mortem "Have we wasted our time?"; Microsoft's MindNet, abandoned). Today that step would be done by an LLM — so your alternative does not remove the LLM, **it demotes it from author to translator**. That demotion is still the whole ballgame: a translation can be checked against its source; a free generation cannot.

**On (c).** SAE features are more grounded than prompting — they're statistical regularities in how a model *processes* millions of real usages, not its freestyle opinion, and you can verify them causally (steer the feature, watch behavior change). But they fail canonical, deterministic, *and* training-free, structurally, not fixably. Our own E8 extension is the live demonstration: the kernel↔SAE alignment that held for gpt2↔pythia (ρ≈0.36–0.39, p=0.0001) went null when SmolLM2 was added (possibly a measurement-site confound — worth the cheap re-run — but the fragility is real). **Internals should be the referee, never the substrate.**

**A deeper caveat from theory that applies to all of (a), (b), (d):** fifty years of decompositional semantics supports the idea that concepts *can* be paraphrased in a small vocabulary; almost nothing supports the claim that there is *one right* paraphrase. NSM's own inventory grew from 14 primes to ~65; published explications of the same word differ across authors; Riemer showed NSM's acceptance test (substitutability) is circular and doesn't select a unique winner. Fodor's attack on definitions ("kill" ≠ "cause to die"; *Concepts*, 1998) is generally judged to have won descriptively: mainstream cognitive science does not believe concepts have discovered definitional structure. What survives Fodor is **stipulation** — law, SI units, and ISO vocabularies fix meanings by convention and work fine. Our architecture.md §1.0 already takes this posture. The implication has teeth: unless the convergence experiments below come back positive, "canonical" means *canonical-by-fiat*, and the hash identifies an endorsed convention, not the concept itself.

## 3. Recommendation

Theory converges on a hybrid with sharply assigned roles — and all four briefs, arriving from different directions, landed on the same shape:

1. **The dictionary is the content authority.** Pinned, versioned dictionary text (Wiktionary + WordNet glosses) is what explications must be faithful *to*. This is your proposal, adopted — for exactly your reason. It buys provenance and checkability that free generation can never have.
2. **The dictionary graph is the scaffold.** Compute its grounding kernel/core; build outward in dependency order, satellites last. The confluence theorems mean this ordering is canonical for free.
3. **NSM stays, provisionally, as the stipulated base vocabulary** — a compression target, not a scientific truth — pending the basis experiments below. One warning flag already exists: real dictionaries' minimum grounding sets are ~1,000 words and skew *concrete and sensorimotor* (see, hand, water), while NSM's 65 primes are abstract. The empirical floor of definitions may not be where NSM says it is.
4. **The LLM is demoted to source-checked translator.** It converts dictionary senses into NSM under a *semantic* gate — entailment both ways between explication and pinned source, checked by a different model family — added to the existing structural gates. This is the single most important pipeline change, and it is incremental, not a rewrite.
5. **The reconciliation fixpoint is the settlement mechanism** — it survives this pivot intact; it's the same confluent-reduction discipline the dictionary literature uses.
6. **Model internals are the external referee.** E8-style cross-model measurement scores rival explications and validates geometry. "LLM proposes, cross-model measurement disposes" neutralizes the circularity: no single model's opinion is load-bearing.

**Where theory genuinely under-determines the choice** — and this must be said plainly: theory cannot tell us whether independently produced explications of the same concept converge to the same fixpoint (the entire meaning of "canonical" rides on this); whether the right basis is 65 primes or ~1,000 dictionary-grounded words; or whether kernel geometry tracks anything real. These are measurable, not debatable. Hence §5.

## 4. What we don't know, ranked by decision impact

**Settled by literature (stop re-litigating):** dictionary reduction is confluent and its kernel unique; the minimal basis (MinSet) is *not* unique — many exist; naive definition→relations extraction fails without a strong parser/validator; discovered canonical decompositions have no theoretical support; SAE dictionaries are non-canonical by construction.

**Open empirical questions, in decision order:**
1. **Proposer invariance** (biggest): do different LLM families, translating the same pinned definition, reconcile to the same fixpoint? If yes on concretes, the method is sound for a core tier. If no everywhere, generation-as-construction is dead and the pipeline inverts fully to your design.
2. **Is E8 measuring meaning or graph shape?** If a meaning-destroying, structure-preserving permutation of the kernel aligns with SAEs just as well, our best grounding evidence evaporates.
3. **Basis size**: do 65 primes cost accuracy that ~1,000 dictionary-grounded words don't?
4. **Was the E8/SmolLM2 null a measurement-site artifact or real fragility?** Determines how much weight the referee can bear.
5. **Does kernel geometry predict anything non-definitional** (human similarity judgments, perceptual norms)?

**Philosophical / contested (won't be settled; manage by posture):** whether NSM primes are true universals (von Fintel & Matthewson: unproven); whether any symbol-only system "really" means anything (Harnad, Searle); whether concepts have definitional structure at all (Fodor). Our stance: the kernel is a *stipulative coordination artifact* — like SI units — whose usefulness is empirical. That is fatal to a literal "can't-misunderstand" pitch and non-fatal to everything else.

## 5. The experimental programme (cheapest, most decision-relevant first)

**X1 — Dictionary grounding structure vs. NSM (days, ~$0, CPU only).**
*Question:* is the empirical floor of definitions where NSM says it is? *Method:* build the WordNet+Wiktionary definition graph; compute Kernel/Core/Satellites and sampled MinSets (the 2016 paper's method). Pre-registered predictions: NSM primes land in Kernel/Core far above frequency-matched chance, and over-represent in the MinSet intersection. *Pass:* NSM keeps its base-layer role. *Fail:* switch the basis to a dictionary-derived core (Jesse's route wins at the foundation). *Unblocks:* the basis decision, and produces the scaffold graph the hybrid needs regardless of outcome.

**X2 — Proposer invariance + author-vs-translator (1–2 weeks, low hundreds of $ in API calls).** Merges the E-CONV and E-D2 designs. *Question:* how much canonicality does the dictionary buy, and is LLM output model-idiosyncratic? *Method:* ~300 concepts stratified by concreteness and by X1 stratum; 3–4 unrelated model families (Haiku, GPT-4o-mini, Gemini Flash, Llama) × {free generation, source-constrained translation}; everything through gates + reconciliation; measure identical-hash rates and whether inter-proposer vector distance ≪ inter-concept distance. *Pass:* translation mode converges strongly, at least on concretes — your circularity worry is defused *with numbers*, and "canonical" is partly earned. *Fail (divergence even in translation mode):* canonicality is pure governance; docs and pitch must say so; human endorsement becomes the bottleneck by design. *Unblocks:* the central construction-method decision. **This is the single most important experiment.**

**X3 — E8 permutation test (days, existing machinery).** *Question:* is E8 evidence of meaning, or of topology? *Method:* corrupt the kernel by permuting prime assignments / swapping explication subtrees (structure preserved, meaning destroyed); re-run E8. Also re-run SmolLM2 at a residual-stream site to resolve the ext-1 confound. *Pass:* real kernel beats permuted — content is doing work; internals are certified as referee. *Fail:* E8 was graph statistics; the referee role needs rebuilding before anything in §3 step 6 proceeds. *Unblocks:* whether internals can arbitrate anything.

**X4 — Internals as explication referee (1–2 weeks, modest GPU).** Contingent on X3 passing. *Question:* can cross-model SAE alignment *rank* rival explications? *Method:* ~200 concepts, 2–3 rival explications each, score by predicted cross-model feature correspondence vs. a shuffled-rival null. *Pass:* wire the oracle into the admission pipeline. *Fail:* referee stays validation-only. *Unblocks:* automated semantic gating beyond source-entailment.

**X5 — External-criterion battery (1 week, public data, ~$0).** *Question:* does kernel geometry predict anything non-definitional? *Method:* test against SimLex-999/WordSim-353, McRae/CSLB feature norms, concreteness/AoA norms, and vision-only (DINOv2) similarity; baselines fastText + LLM embeddings + shuffled-explication null. *Unblocks:* honest external claims about what the kernel captures; expected partial pass (taxonomic yes, perceptual no) sharpens the pitch.

**X6 — Basis-size sweep (2–3 weeks).** Re-explicate a fixed sample over bases of ~65 / ~300 / ~1,000 (from X1's core); measure explication blowup, authoring failure, and degradation on X3/X5 metrics. *Unblocks:* final basis choice, informed by cost curves rather than doctrine.

**X7 — Inter-analyst convergence, human-inclusive (slow, most expensive; the "canonical" license).** ~100 concepts, k≥4 maximally decorrelated routes (different humans, model families, source dictionaries), reconcile each route separately, compare fixpoints against a preregistered threshold. Only a pass here licenses the word "canonical" outside the repo without a "by convention" footnote.

(Held in reserve: the SAE determinism-ceiling audit, M2 — only needed if anyone ever again proposes internals as substrate; X3+published seed-stability numbers likely settle it for free.)

**Decision spine:** X1+X2 (~two weeks, trivially cheap) settle your two challenges directly — whether the dictionary should replace Wikipedia/free-generation as the authority (almost certainly yes; the question is by how much), and whether the Haiku worry is fatal or fixable-by-demotion. X3 tells us whether our best grounding evidence is real. Everything downstream is calibration. Nothing in the programme requires abandoning the reconciliation design, the encoder, or the honesty/tier architecture — the pivot is about *where authority lives*, and every piece built so far survives the move.

---

# Appendix — the five research briefs (verbatim)

## Angle: decompositional-semantics-theory

I have enough grounding from the repo (architecture.md §1.0 already gestures at this territory; the nsm-and-knowledge-injection report covers Riemer/von Fintel/Bohnemeyer). Here is the deliverable.

---

# Is there a canonical primitive basis for meaning? Theory survey for the Kernel of Truth

**The question.** The kernel presumes that every concept has (a) a decomposition into a finite closed set of primitives, and (b) a *canonical* such decomposition — one right answer, so a hash of it can be an identity. Fifty years of decompositional semantics speaks to (a); almost nothing in the literature supports (b) as a *discovered* fact. That asymmetry is the headline.

**NSM.** Natural Semantic Metalanguage (Wierzbicka, *Semantic Primitives*, 1972; Goddard & Wierzbicka, *Meaning and Universal Grammar*, 2002) claims ~65 semantic primes — indefinable words like SOMEONE, WANT, GOOD, BECAUSE — found as lexicalized items in every language, plus a small universal grammar for combining them. A word's meaning is given by *reductive paraphrase*: a text in primes (plus vetted intermediate "molecules") substitutable for the word. It is the only decompositional program with an explicit closed basis, a grammar, and decades of worked explications — which is why the kernel uses it. But note three problems, each documented by serious critics. *First, the basis is not stable*: the inventory grew from 14 primes (1972) to ~55–65 today, with items added and removed; a basis under revision is not canonical. *Second, universality is contested*: Bohnemeyer's Yucatec Maya fieldwork found no lexical exponents of BEFORE/AFTER; von Fintel & Matthewson ("Universals in Semantics," *The Linguistic Review* 2008) find "remarkably few convincing semantic universals" and rate the prime inventory unproven. *Third — the one that matters most for hashing — explications are analyst-dependent*: NSM's acceptance test is substitutability, and Riemer ("Reductive Paraphrase and Meaning," *Linguistics and Philosophy* 2006) showed that test is circular (judging a paraphrase adequate presupposes knowing the meaning) and does not select a unique winner. NSM practice confirms it: published explications of the same word differ across authors and editions, and the school itself calls explications revisable hypotheses. NSM gives you a *language* for definitions; it does not give you a *normal form*.

**The rivals fare no better on canonicality.** Katz & Fodor's semantic markers (1963) — the first formal decomposition — died of two wounds: Lewis's "markerese" objection (1970: translating English into markers isn't semantics, just another uninterpreted language) and the discovery that markers had no principled inventory. Schank's Conceptual Dependency (~1972) reduced verbs to ~11 primitive ACTs (PTRANS, MTRANS, INGEST…); it powered 1970s story-understanding systems but the inventory was avowedly an engineering convenience, and coverage collapsed outside physical-transfer verbs. Wilks's preference semantics used ~80–100 primitives and, in his exchanges with Wierzbicka, took exactly the position the kernel has now been forced into: primitives are *chosen for utility, not discovered*. Jackendoff's Conceptual Semantics (*Semantic Structures*, 1990) decomposes into functions (EVENT, PATH, CAUSE, GO) but Jackendoff himself denies full definitional decomposition — meanings bottom out partly in perceptual/spatial representations that no symbolic paraphrase captures. Pustejovsky's Generative Lexicon (1995) is actively anti-canonical: word meaning is a generative device (qualia structure: what a thing is, is for, is made of, comes from) whose specific senses are *composed at use time* — "begin a book" gets its reading in context. If Pustejovsky is right, a static explication per concept is the wrong data structure at the root.

**The strongest objection: Fodor.** Fodor's case against definitions must be taken at full strength because, if sound, it removes the kernel's substrate. Three prongs. (1) *Definitions don't exist*: after two millennia of trying, almost no lexical concept has an accepted necessary-and-sufficient definition; his classic "Three Reasons for Not Deriving 'Kill' from 'Cause to Die'" (1970) shows even the textbook decomposition leaks (you can cause someone to die on Tuesday by acting on Monday, but you can't kill them on Tuesday on Monday). (2) *No psychological reality*: Fodor, Garrett, Walker & Parkes ("Against Definitions," *Cognition* 1980) found definitionally "complex" words are not processed slower — decomposition leaves no experimental fingerprint. (3) *Prototypes don't save it*: Rosch's typicality effects show categories are graded, but prototypes fail to compose (Fodor & Lepore's "pet fish" — the prototype of *pet fish* is not derivable from the prototypes of *pet* and *fish*). Fodor's conclusion (*Concepts*, 1998): lexical concepts are *atoms*; their content is a causal mind–world relation, not internal structure. Verdict for the kernel: Fodor is generally judged to have won the *descriptive* battle — mainstream cognitive science does not believe most concepts have discovered definitional structure — but his target was decomposition as a theory of *mental representation*. He has nothing against *stipulated* definitions; law, mathematics, and ISO vocabularies stipulate meanings usefully every day.

**Where the kernel premise stands.** Theory does **not** support a canonical, finite, deterministic decomposition of meaning as a discoverable fact about concepts. It *does* permit a stipulative one: a governed community can fix a closed basis and a normal form by convention, exactly as architecture.md §1.0 already concedes. But that concession has teeth the project must accept: "canonical" then means *canonical-by-fiat*, and the hash identifies an endorsed convention, not the concept. For the discovered-canonicality version to hold, three things would have to be true, none currently evidenced: (i) a finite basis whose closure covers the target vocabulary with bounded explication depth — note that the empirical dictionary-grounding result (Vincent-Lamarre, Massé, Harnad et al., "The Latent Structure of Dictionaries," *TopiCS* 2016) finds minimal grounding sets of ~1,000 words, an order of magnitude above 65, which is quiet evidence against prime-level sufficiency; (ii) a normal form under which independently produced explications of the same concept converge; (iii) explication-space distances that track distinctions external systems actually make (E8 is the existing evidence here, and it is the kernel's best asset).

**Two decisive experiments.**

1. **Inter-analyst convergence test (tests canonicality directly).** Take ~100 concepts stratified by concreteness. Produce k≥4 independent explications per concept in the profile-1 grammar via maximally decorrelated routes: different humans, different LLM families, different source dictionaries. Run the reconciliation fixpoint on each route separately, then compare fixpoints (hash identity; structural edit distance). Preregister a threshold. High convergence ⇒ the fixpoint is discovering something and "canonical" is honest; low convergence ⇒ canonicality is governance, and the docs/pitch must say so.

2. **Basis-size sweep (tests Jesse's dictionary proposal against NSM).** Compute the minimum grounding set of WordNet/Wiktionary definition graphs (Vincent-Lamarre et al.'s method), then re-explicate a fixed concept sample over bases of ~1,000, ~300, and 65 primitives. Measure explication depth/length blowup, authoring failure rate, and — critically — whether E8-style kernel↔SAE alignment and X3 similarity pathology degrade as the basis shrinks. If 65 primes cost accuracy that ~1,000 dictionary-grounded words don't, the right basis is the dictionary's, not NSM's.

**Bottom line:** decomposition is a defensible *engineering convention* and an indefensible *scientific claim*. Build the kernel as the former; run experiment 1 before ever using the word "canonical" outside the repo.

---

## Angle: dictionary-graphs-grounding-kernels

All research done. Here is the deliverable.

# Dictionary graphs, grounding kernels, and convergence: does Jesse's alternative work?

## What the grounding-kernel literature already established

Jesse's proposal — take a dictionary, turn definitions into relations, run a convergence algorithm — has been studied in almost exactly this form, under a name that should sound familiar: the **grounding kernel**. Treat a dictionary as a directed graph (an arrow from each word used in a definition to the word it defines). Then repeatedly delete every word that is defined but never used to define anything else. This reduction is **confluent** — deletion order doesn't matter; you always land on the same unique subgraph. Vincent-Lamarre, Blondin Massé, Lopes, Marcotte & Harnad, ["The Latent Structure of Dictionaries"](https://arxiv.org/abs/1411.0129) (Topics in Cognitive Science, 2016), building on [Blondin Massé et al. 2008](https://arxiv.org/abs/0806.3710), found across real dictionaries:

- **Kernel:** ~10% of the dictionary suffices to define all the rest.
- **Core:** ~75% of the Kernel is one strongly connected component — every word definitionally reachable from every other, i.e. the maximally circular heart.
- **Satellites:** the remaining ~25%, small mutually-defining clusters.
- **MinSet** (minimum feedback vertex set — the smallest set of words which, if their meanings were given from outside, would break every circular loop): ~1% of the dictionary, roughly half Core, half Satellite.

Crucially, this structure is *psycholinguistically real*: Kernel and Core words are acquired earlier in childhood and are more frequent; Satellites are more concrete. The graph topology of dictionaries genuinely tracks how humans bootstrap vocabulary. A 2025 follow-up from the same group ([Goulet, Blondin Massé & Abdenbi](https://arxiv.org/abs/2508.11068)) extends this with confluent (order-invariant) reductions over AMR graphs of definitions — the same fixpoint discipline our just-designed reconciliation step uses.

**Two findings bear directly on us.** First, the *Kernel is canonical* (unique fixpoint of a confluent reduction) — good news for a project literally called Kernel of Truth. Second, the *MinSet is not*: "every dictionary has a huge number of MinSets." There is no "the" minimal defining vocabulary; the truly minimal basis is underdetermined by the dictionary. If we want one canonical minimal set, we must either canonicalize over all MinSets (e.g. their union/intersection) or stipulate one — the same stipulation move our architecture doc already makes about NSM.

Third, and most important: the grounding-kernel result is a *topology* result, not a *semantics* result. It tells you **where** circularity bottoms out, not **what** the bottom words mean. Harnad's point is precisely that MinSet words must be grounded *outside* the dictionary (sensorimotorically, in his story). Jesse's convergence algorithm inherits this: the dictionary can order and structure the kernel, but cannot supply the content of its base layer. Something else must — NSM primes by stipulation, human sensorimotor grounding, or model internals (the E8 angle).

## The step where this historically died

"Turn each definition into a set of relations" is a 40-year-old programme with a documented failure mode. Quillian's semantic-memory networks (1968) and 1980s work (Amsler's taxonomy from Webster's; Chodorow, Byrd & Heidorn's hypernym extraction) led to Ide & Véronis's famous 1993 verdict, *"Extracting knowledge bases from machine-readable dictionaries: have we wasted our time?"* — fifteen years produced "little more than a handful of limited and imperfect taxonomies." Causes: definitions are written for humans who already speak the language; genus terms are sense-ambiguous; lexicographic conventions are inconsistent. Microsoft's [MindNet](https://www.researchgate.net/publication/230876760_MindNet_Acquiring_and_Structuring_Semantic_Information_from_Text) (Richardson, Dolan & Vanderwende, 1998) was the most serious attempt — full parsing of LDOCE into ~24 relation types — and it required a broad-coverage NLP parser whose interpretive choices were themselves neither canonical nor complete; it was ultimately abandoned for corpus statistics.

The honest modern statement: the definition→relations step today would be done *by an LLM* (the 2025 paper above does exactly this). So Jesse's alternative does not remove the LLM — **it demotes it from author to translator**. That demotion is still valuable: a model *parsing an external authoritative text* produces output checkable against its source (faithfulness is verifiable), whereas a model *generating* an explication from its weights is emitting trained opinion with nothing to check against — Jesse's circularity worry, and it is well-founded.

## FCA as the convergence algorithm

**Formal Concept Analysis** (Ganter & Wille, [*Formal Concept Analysis: Mathematical Foundations*](https://dl.acm.org/doi/10.5555/550737), 1999) is the mathematically mature version of "convergence-style algorithm." Given a *formal context* (a table of objects × attributes), the **concept lattice** is provably unique — a canonical hierarchy, no ordering choices, no seeds — and the **Duquenne–Guigues basis** gives the canonical minimal set of implications. This is genuinely the right formal tool for the "settle the relations" step. Caveats: canonicality is *conditional on the context* — the extracted relations fully determine the lattice, so FCA launders whatever the extraction step produced ("canonical garbage out"); and lattices can blow up exponentially, so dictionary-scale use needs pruning thresholds, which reintroduce arbitrary choices.

## Verdict

The dictionary route yields canonicality of *structure* (unique Kernel, unique lattice, confluent fixpoints) and *provenance* (an external, auditable, versioned source text), which pure LLM-generation lacks. It does not yield groundedness of the base layer, does not yield a unique minimal set, and its extraction step is the historical graveyard — survivable only by using the LLM as a validated translator. The theoretically strongest position is a **hybrid**: dictionary graph as scaffold and dependency ordering; NSM (or whatever base survives testing) as stipulated kernel content; LLM as source-checked parser; confluent fixpoint (our reconciliation design carries over intact) as settlement.

## Experiments

**E-D1 — Compute the grounding structure of a real dictionary and test NSM against it.** Build the definition graph from WordNet glosses + Wiktionary; compute Kernel, Core, Satellites, and a sample of MinSets (MFVS is NP-hard but ILP/heuristics handle 100k-node dictionary graphs — the 2016 paper did it). Pre-registered predictions: (a) the 65 NSM primes fall in the Kernel/Core massively above frequency-matched chance; (b) primes over-represented in the MinSet *intersection*. Outcome (a) failing would be evidence against NSM as the base layer; (b) holding would be independent, non-NSM-internal validation of the prime set. Cheap: CPU graph algorithms, days not weeks.

**E-D2 — Author vs. translator.** For ~500 concepts sampled across Kernel/Satellite/rest strata, produce explications four ways: {Haiku, one other model} × {free generation (current method), constrained translation of the dictionary definition with source-faithfulness validation}. Run all four through the reconciliation fixpoint; measure cross-model agreement (identical canonical hashes, structural edit distance) and fixpoint convergence rates. Hypothesis: translation mode is substantially more model-invariant than generation mode. This directly quantifies how much canonicality the dictionary buys and either vindicates or defuses Jesse's circularity objection with numbers.

Sources: [Vincent-Lamarre et al. 2016, arXiv:1411.0129](https://arxiv.org/abs/1411.0129) ([journal](https://onlinelibrary.wiley.com/doi/full/10.1111/tops.12211)); [Blondin Massé et al. 2008, arXiv:0806.3710](https://arxiv.org/abs/0806.3710) ([TextGraphs](https://aclanthology.org/W08-2003.pdf)); [Goulet, Blondin Massé & Abdenbi 2025, arXiv:2508.11068](https://arxiv.org/abs/2508.11068); [Richardson, Dolan & Vanderwende 1998 (MindNet)](https://www.researchgate.net/publication/230876760_MindNet_Acquiring_and_Structuring_Semantic_Information_from_Text); [Ganter & Wille, FCA foundations](https://dl.acm.org/doi/10.5555/550737); Ide & Véronis 1993 (KB&KS proceedings). Repo grounding: /home/ec2-user/css/kernel/kernel-of-truth/docs/architecture.md (§1.0 stipulative posture, §2 convergence caveat), /home/ec2-user/css/kernel/kernel-of-truth/poc/e8/README.md.

---

## Angle: symbol-grounding-and-circularity

I have enough context from the repo (architecture.md §1.0 already concedes the NSM-foundations caveat; §2 C1 concedes "fixing a vector fixes a symbol, not its meaning"; E8 is the kernel↔SAE alignment result). Here is the deliverable.

---

# Is a definition-only kernel grounded, or just circular?

## 1. The problem, stated plainly

The kernel defines every concept in terms of other concepts, bottoming out in ~65 NSM primes. Stevan Harnad named the worry in "The Symbol Grounding Problem" (Physica D, 1990): a system whose symbols are defined only by other symbols is like trying to learn Chinese from a Chinese–Chinese dictionary — a "merry-go-round" of meaningless shapes pointing at other meaningless shapes. Meaning, he argued, requires that at least some symbols connect *non-symbolically* to the world — through perception and action — and the rest can then be composed from those. Searle's Chinese Room (1980) makes the companion point: rule-governed symbol manipulation, however consistent, is not understanding. The kernel, as built, is exactly the kind of system these arguments target: a closed formal structure. The honest starting position is that **the kernel is not grounded; it is a very well-engineered dictionary**.

## 2. Are the 65 primes a legitimate floor?

NSM's own answer to circularity is that the primes don't need definitions because, in *humans*, they are innate and universal (Wierzbicka, *Semantics: Primes and Universals*, 1996; Goddard & Wierzbicka's cross-linguistic programme). Note what kind of claim that is: it says the primes are grounded **in human cognition** — in creatures who already perceive, act, and feel. That grounding does not transfer to a machine. Inside the kernel, `GOOD` and `SOMEONE` are just two more uninterpreted node labels; NSM's floor is real for people and empty for the artifact. (The repo's architecture.md §1.0 already adopts NSM for engineering value, not scientific truth — this is the same concession, one level deeper.)

Jesse's dictionary intuition has, encouragingly, been formalized — by Harnad's own group. Massé et al. ("How Is Meaning Grounded in Dictionary Definitions?", 2008) and Vincent-Lamarre, Massé, Lopes, Lord, Marcotte & Harnad ("The Latent Structure of Dictionaries", *Topics in Cognitive Science*, 2016) treat a dictionary as a directed graph and extract its **minimum grounding set**: the smallest set of words from which all others are reachable by definition alone. Two findings matter here. First, such a core exists and is small (~10% of the dictionary, with a tighter "kernel" and "core" structure inside it) — so a convergence-style reduction of definitions is mathematically sound, which supports Jesse's proposed algorithm. Second, and this is the sting: the grounding-core words are systematically **more concrete, more frequent, and learned earlier in childhood** — words like *see*, *hand*, *water* — i.e. exactly the words humans acquire through the senses *before* they can use definitions. The dictionary's own structure testifies that definitions bottom out in perception, not in abstract primes. NSM's inventory (SOMEONE, BECAUSE, MAYBE…) is largely abstract; the empirically observed grounding floor of real dictionaries skews sensorimotor. The primes are a *good compression basis*; they are not the place where meaning enters.

## 3. Does distributional semantics change the verdict?

The rival theory of meaning is distributional: "you shall know a word by the company it keeps" (Firth 1957; Harris 1954), operationalized as word embeddings (Mikolov et al., word2vec, 2013) and, at scale, LLMs. The standard critique is that this is *also* ungrounded — Bender & Koller ("Climbing towards NLU", ACL 2020) argue meaning cannot be learned from form alone. But there is a real asymmetry the kernel should respect. Trained models have **causal contact with the world at one remove**: their statistics are distilled from text produced by grounded humans about a real world, and Mollo & Millière ("The Vector Grounding Problem", 2023) argue this gives them a defensible, if thin, kind of referential grounding; Piantadosi & Hill (2022) argue conceptual-role meaning can live in such systems. Empirically, distributional vectors predict human perceptual and behavioral data they were never trained on (Grand et al., *Nature Human Behaviour* 2022; Bruni et al.'s multimodal distributional semantics). The kernel has none of this: its only "experience" is WordNet plus Haiku's outputs.

This reframes Jesse's Haiku worry precisely. Haiku's explications are *not* ungrounded — they inherit the distributional grounding of Haiku's training. The actual problems are different: they are **not canonical** (another model, or the same model tomorrow, yields different explications), **not independent** (using an LLM's opinion of meaning to build a kernel meant to correct LLMs is circular in the audit sense), and **not deterministic** in provenance. So the LLM-generation issue is a *canonicity* failure, while the definitional structure is a *grounding* failure. They need different fixes.

## 4. Is ungroundedness fatal? It depends which goal you mean

For the **interface tier** — drift-free, content-addressed, verifiable reference — grounding in Harnad's sense is not required. Coordination artifacts (SI units, ISO standards, legal definitions) are stipulative and work precisely because everyone binds to the same token. Architecture.md's "stipulative-definition posture" is the right philosophy here, and it is honest.

For the **strong goal** — canonical meaning *inside* an LLM, "can't-misunderstand" — ungroundedness bites, and the repo has already partially conceded it (C1: fixing a vector fixes a symbol, not its meaning). A model interprets a frozen vector by how it *uses* it, and use is learned from data. Meaning will be fixed only where kernel structure and learned structure agree.

Does grounding require abandoning training-free? **For construction, no; for validation, yes.** The tractable middle path is: keep the kernel deterministic and training-free, but treat trained systems (SAE dictionaries, vision encoders, human norms) as *measuring instruments* that check whether the kernel's geometry tracks the world. E8 — kernel coordinates predicting gpt2↔pythia SAE feature correspondence — is already this move, and it is the single strongest grounding evidence the project owns: agreement with two independently trained systems is agreement with the data-generating world, at one remove.

## 5. Two experiments

**E-G1 — External-criterion test (does the kernel predict anything non-definitional?).** Take matched concept sets and test whether kernel geometry predicts: (a) human similarity/relatedness judgments (SimLex-999, WordSim-353), (b) feature-production norms (McRae, CSLB/Buchanan), (c) concreteness and age-of-acquisition norms (Brysbaert; Kuperman), and (d) visual similarity from a vision-only encoder (e.g. DINOv2 over per-concept image sets — vision-only avoids text contamination). Baselines: fastText/LLM embeddings, plus a **shuffled-explication null**. Prediction if ungrounded-but-formal: kernel beats null on (a) taxonomic pairs but fails (b)–(d) where distributional baselines succeed. Cheap, all public data.

**E-G2 — Structure-permutation ("swap") test, extending E8.** Build a corrupted kernel: permute prime assignments (and/or systematically swap explication subtrees) so graph *structure* is preserved but intended *meaning* is destroyed; re-run E8's cross-model SAE alignment. If the real kernel beats the permuted kernel, its content — not just its topology — is doing work: that is a direct, quantitative operationalization of "grounded vs merely formal," because a purely formal system is invariant under meaning-destroying, structure-preserving permutations. If they tie, the E8 result was measuring graph statistics, and the grounding claim dies honestly.

**Bottom line:** the kernel is a formal coordination artifact, not a grounded semantics; its weakest point is the prime floor, which is grounded in human cognition but not in the artifact. That is fatal to "can't-misunderstand" as originally stated, non-fatal to the interface-tier product, and empirically improvable: grounding can be *rented* from trained systems for validation (E8, E-G1/G2) without abandoning training-free construction — and the dictionary-graph literature says the grounding core, if the project ever builds one, should be concrete and acquisition-ordered, not abstract.

---

## Angle: model-internal-extraction

Grounding done (docs/architecture.md, poc/e8/README.md, both E8 verdicts). Deliverable follows.

---

# Model-internal extraction: can we get the kernel out of a model's guts instead of its mouth?

## The idea, and why it addresses Jesse's circularity worry only halfway

When you prompt Haiku for an explication, you get the model's *utterance* — text sampled from its output distribution, shaped by RLHF, prompt wording, and whatever the model thinks an NSM explication should look like. Mechanistic interpretability offers a different tap point: read the concept out of what the model *computes* internally when it processes the concept, rather than what it *says* about it.

The main tool is the **sparse autoencoder (SAE)**: a small trained network that decomposes a model's internal activations into a large dictionary of sparse "features" — directions that each fire on a recognizably coherent theme (Bricken et al., "Towards Monosemanticity", Anthropic 2023; scaled to Claude 3 Sonnet in Templeton et al., "Scaling Monosemanticity", 2024; DeepMind's Gemma Scope, Lieberum et al. 2024, published SAEs for every layer of Gemma 2; Cunningham et al. 2023 for the original dictionary-learning result). This sits on the **linear representation hypothesis** — evidence that models encode many concepts as directions in activation space (Park, Choe & Veitch 2023; the word2vec analogy lineage, Mikolov et al. 2013), supported by linear probing (Alain & Bengio 2016) and by steering: adding a concept direction changes behavior in the concept's direction (Turner et al., activation addition; Zou et al., "Representation Engineering", 2023).

Is this less circular than prompting? **Partly, and the distinction matters.** An SAE feature for "deception" is not the model's opinion about deception; it is a statistical regularity in how the model processes millions of real usage contexts. That is closer to distributional grounding — meaning-from-use across a corpus — than to asking the model to freestyle a definition. It also gives you something prompting never can: causal verifiability (ablate or steer the feature and watch behavior change). But it does not escape the circle entirely: the features are still *of a trained model*, so they inherit the training corpus's biases and the model's idiosyncrasies. What rescues the approach from pure circularity is **cross-model convergence**: if independent models trained on different data yield corresponding features (the "Platonic Representation Hypothesis", Huh et al. 2024; model-stitching results), the shared structure plausibly reflects the world/language, not any one model's whim.

## The honest cost: it fails all three of your adjectives

Measured against **canonical / deterministic / training-free**, SAE features fail all three, and no known technique fixes this:

- **Not training-free.** SAEs are themselves trained (Gemma Scope burned substantial TPU compute). Any extraction pipeline is "training-free" only in the sense that someone else did the training.
- **Not deterministic.** SAE feature dictionaries vary with random seed, width, sparsity penalty, layer, and training data. Paulo & Belrose (2025) found only ~65–70% of features are shared across seeds of otherwise identical SAEs. "Feature splitting" (Bricken et al.) means there is no canonical inventory: train a wider SAE and one feature fractures into several finer ones. There is no fact of the matter about *the* feature list.
- **Not canonical.** Features are model-relative coordinates. Your own E8 extension is the cleanest demonstration this project owns: the kernel↔SAE alignment that passed on gpt2↔pythia (P1 ρ=0.386, P2 ρ=0.360, both p=0.0001; retrieval above chance) **did not replicate** when SmolLM2 was added as a third family (both new pairs null, p>0.05) — with the named confound that the SmolLM2 SAE sits on an MLP-output site rather than the residual stream. The generous reading: kernel-relevant structure lives at specific sites in specific models, and finding it is itself an empirical hunt, not a lookup.

## What "deconstruct the output layer" could concretely mean

Three versions, in ascending cost:

1. **Learned readout into the kernel basis (cheap, days).** Train a linear map from a model's residual stream to kernel coordinates — a probe. The kernel stays canonical and deterministic; only the per-model adapter is learned. This is exactly architecture A2 in docs/architecture.md, and E8 already validates its precondition for one model pair. This is the defensible version.
2. **Tie the unembedding to a concept dictionary (moderate).** Add a second output head whose rows *are* frozen kernel vectors, so the model emits a distribution over concepts alongside tokens. Feasible via fine-tuning; but per the architecture doc's "update paradox", the model learns its interpretation around the frozen rows — you fix symbols, not meanings.
3. **Distill a model whose latent basis is the kernel (expensive, speculative).** Related art: Backpack language models (Hewitt et al. 2023), which force predictions through interpretable per-word sense vectors — it works, at a real performance cost, and it is full-scale training. This is a research program, not a construction step.

## Verdict: internals are the referee, not the substrate

Model-internal extraction cannot *replace* the definitional construction, because it cannot produce a canonical, deterministic, auditable object — that is structural, not an engineering gap. But it beats definitional approaches at exactly the thing they lack: an **empirical oracle**. A dictionary-graph or NSM explication is stipulative; you cannot ask WordNet whether your explication of "regret" carves reality correctly. You *can* ask whether it predicts the shared structure of independently trained models. So: build the kernel from definitional sources (dictionary grounding-kernel work is the right substrate for Jesse's alternative), and use model internals for **validation and arbitration** — a role E8 has already piloted. Haiku-prompting then becomes a proposal generator whose outputs are scored against internals, which neutralizes the circularity worry: the LLM proposes, cross-model measurement disposes.

## Two concrete experiments

**Exp M1 — internals as explication referee.** For ~200 concepts with Haiku-tier explications, generate 2–3 *rival* explications each (different LLMs, or perturbed prompts). For each concept, compute its SAE feature signature in ≥2 model families (E8 machinery, residual-stream sites only). Test: does the rival explication whose kernel vector best predicts cross-model feature correspondence also win on the existing validation gates? If kernel↔internals alignment can *rank* rival explications above a shuffled-rival null, internals can serve as the selection oracle in the generation pipeline. Also run the cheap E8 follow-up: SmolLM2 at a residual-stream site, to resolve whether ext-1's null was the site confound or a real fragility.

**Exp M2 — determinism ceiling audit.** Train 3–5 SAEs differing only in seed (one model, one site; small model, ~$100s), plus one width variation. Measure feature-match rates (Hungarian/max-cosine matching) restricted to the E8 concept set, and how much E8's ρ varies across seeds. This puts a *number* on the best-case canonicality of any internals-derived construction. Pre-register a kill criterion: if seed-to-seed feature agreement on kernel concepts is below ~70%, internals are permanently confined to the referee role and the substrate question is settled in favor of definitional sources.

**Bottom line:** more grounded than prompting, yes — grounded in measured computation over usage, with causal checks, and cross-model agreement as the anti-circularity mechanism. But it is the least canonical, least deterministic, least training-free option on the table, and E8's own non-replication shows the fragility live. Use it to *judge* the kernel, never to *be* the kernel.

---

## Angle: llm-generator-critique

I have enough grounding from the repo (haiku-tier README, modelauthored-schema.md, s1-report structure, design-bulk-kernel honesty architecture). Here is the deliverable.

---

# Is generating explications with an LLM sound, or circular? (the Haiku worry)

## The distinction that decides everything: proposer vs. source of truth

Jesse's worry is exactly right as stated, and the way out of it is a distinction with good precedent in both mathematics and recent ML.

- **LLM-as-source-of-truth**: the model's output *is* the definition. Whatever Haiku emits for "umbrella" becomes the canonical vector for umbrella. This is circular in the precise sense Jesse fears: the "canonical" meaning is one particular model's compression of its training data — a popularity-weighted average of internet text, frozen at a training cutoff, with that model's biases baked in. Calling it canonical doesn't make it so; it makes it *Anthropic-2025-English-web canonical*. Worse, if the kernel is later used to train or steer models, you have a closed loop of model output feeding model input — the failure mode Shumailov et al. documented as **model collapse** ("AI models collapse when trained on recursively generated data", Nature 2024).

- **LLM-as-search-heuristic (verified proposer)**: the model proposes candidates, and an *independent* checker decides acceptance. This is the guess-and-verify pattern that makes systems like AlphaGeometry (Trinh et al., Nature 2024) and FunSearch (Romera-Paredes et al., Nature 2023) legitimate: the neural net's provenance is irrelevant to the correctness of the result, because a symbolic verifier — not the model — is the authority. A proof found by a stochastic search is still a proof. **The soundness of the artifact then rests entirely on the strength and independence of the verifier**, and the LLM demotes from oracle to a very good random-candidate generator.

So the question is not "is it okay to use Haiku?" but "**does the gate actually carry the semantic authority, or does Haiku?**"

## Honest read of the current pipeline

The current haiku-tier pipeline is better than Jesse may realize — and weaker than it needs to be.

What it already does right (this is real verified-proposer machinery): definitional text is fetched from **pinned Wiktionary/Wikipedia revisions** (sha256-checked), so Haiku is drafting *from a cited source*, not from free recall; drafts go through a **gate-loop repair** cycle against the real encoder gates; only gate-passing outputs become records; every record carries provenance (model id, prompt hashes, source revisions) and sits in an explicitly **sub-canonical tier** (`semanticStatus: ModelAuthored`, below Explicated/Molecule, excluded from coverage stats until human endorsement). The honesty architecture is genuinely good.

The gap: **the gates are structural, not semantic.** They check that an explication is grammatical NSM — prime inventory, syntax, molecule-depth caps, DAG acyclicity. They cannot check that the explication is *true of the concept*. A perfectly well-formed explication of "umbrella" that describes a parasol passes every gate. On the axis Jesse cares about — *what the concept means* — the current verifier is silent, and Haiku is still the de facto source of truth. Verdict: **the pipeline is a verified proposer for form and an unverified oracle for content.**

Two subsidiary points, briefly:

- **Temperature 0 buys reproducibility, not canonicity.** Greedy decoding makes the same model+prompt give the same bytes (mostly — batching and hardware can still introduce nondeterminism), but a *deterministically produced opinion is still an opinion*. Determinism of the wrong kind is the *appearance* of canonicity. What buys real canonicity is order-invariance across proposers: if the fixpoint you converge to doesn't depend on which model proposed the candidates, the model has genuinely been demoted to a heuristic. That is the right success criterion for the reconciliation work.
- **There is a real hypothesis that LLM idiosyncrasy is small.** Huh et al.'s "Platonic Representation Hypothesis" (ICML 2024) argues models trained on enough data converge toward a shared representation; the project's own E8 result (kernel coordinates predicting GPT-2↔Pythia SAE feature correspondence) is weak in-house evidence in the same direction. If true, "Haiku's opinion" is closer to "the consensus statistical structure of English" than to one vendor's quirk. But this is an empirical question — hence the experiment below — not a license to skip verification.

## What would move it fully to "verified proposer"

1. **Add a semantic gate independent of the proposer.** The cheapest principled one is Jesse's own dictionary idea: require every explication to be *entailed-by-and-covering* the pinned Wiktionary sense it cites, checked by a different mechanism than the drafting model (bidirectional NLI with a different model family is the pragmatic version; a relation-extraction match against the dictionary's own defining vocabulary, à la Vincent-Lamarre/Massé/Harnad's dictionary grounding-kernel work, is the strict version). The dictionary, not Haiku, becomes the content authority; Haiku merely translates it into NSM.
2. **Multi-model consensus as an admission requirement.** Generate explications with ≥3 unrelated model families; admit only where they reconcile to the same fixpoint. Divergent concepts get flagged for human authoring instead of silently taking one model's vote.
3. **Cross-check against model internals**, extending E8: an explication whose predicted vector aligns with SAE features that *multiple* models share has independent evidence; one that doesn't is proposer-idiosyncratic by measurement.
4. Keep the existing tier/endorsement ladder — it is the right governance shape.

## Proposed experiment: E-CONV (proposer-invariance)

**Question:** are LLM-generated explications convergent across models, or model-idiosyncratic? **Method:** take a stratified sample of ~200 concepts (concrete nouns / abstract nouns / verbs / socially contested terms). Generate explications with 4 proposers from different training lineages (e.g. Haiku, GPT-4o-mini, Gemini Flash, Llama-3.1-70B), temp 0, identical prompts and pinned sources, same gate-loop. **Measure:** (a) post-gate, post-reconciliation fixpoint identity rate (do they hash to the same record?); (b) where not identical, encoder-vector cosine distance between variants vs. between *different* concepts (is inter-proposer noise ≪ inter-concept signal?); (c) breakdown by concept class. **Reading the result:** high convergence on concretes but divergence on abstracts would say the method is sound for a core tier and needs dictionary/human anchoring for the rest; low convergence everywhere would say Jesse's worry is fatal for generation-as-construction and the pipeline should invert — dictionary relations first (his proposal), LLM only as an NSM translator; near-total convergence would be publishable evidence for the platonic-consensus reading. Cost is a few hundred dollars of API calls, and it directly measures the thing the whole methodology currently assumes.

**Bottom line:** LLM generation is legitimate exactly insofar as an independent authority — pinned dictionary content, cross-model consensus, model-internal features, or a human endorser — can reject its outputs on *semantic* grounds. Today's gates reject on form only, so Jesse's circularity worry currently stands for content; the fixes above are incremental, not a rewrite, and E-CONV tells you how much it actually matters.
