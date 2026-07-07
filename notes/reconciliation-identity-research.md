# Reconciliation & concept identity — research dossier (bead kernel-of-truth-bo6)

> Produced 2026-07-07 by a 5-agent Fable research workflow (4 parallel research angles
> + synthesis), each grounded in this repo. Commissioned after @jeswr raised the
> order-invariance / "when can the content-hash alone be the identity" question and
> asked for deeper research + an experiment BEFORE committing to an identity model.
> Status: research complete; decision deferred pending experiment **E10-fix** (§4 of
> the synthesis). See [[kernel-of-truth-program]] history and bead bo6.

---

# Concept identity under reconciliation: synthesis for Jesse (bead kernel-of-truth-bo6)

## 1. The problem, in plain language

**Content-addressing.** Today a concept's identifier, `urn:kot:<hash>`, is computed by running its definition through a hash function — a mathematical fingerprint of the exact bytes. This is powerful: anyone can verify that an ID matches its definition, two identical definitions automatically get one ID, and nobody can tamper silently. But it has an unavoidable flip side: *improve* the definition, even by one character, and you have — by definition — a *different* ID. Every other concept that referenced the old ID is now pointing at something stale.

**Why we will keep improving definitions.** Concepts are authored in word-frequency order, but meaning doesn't stack up in frequency order. We authored "male" early, spelling it out in bare semantic primes; later we authored "person". The concise, faithful definition of "male" *uses* "person" — so we want to go back and rewrite "male". That rewrite changes male's hash, which changes the hash of everything that references male, and so on up the chain. One improvement can re-identify a large chunk of the 118k corpus. The kernel-integration angle confirmed this is not hypothetical: the encoder builds each concept's vector by recursively folding in the vectors of everything it references, so a re-derivation cascades through both identity *and* vectors.

**Stable identity vs content-hash.** The alternative used by every long-lived dictionary-scale project (lexical-ontological angle): give each concept an *opaque* ID — a meaningless label like `i35545` — that never changes, and let the definition attached to it improve over time. **WordNet** (the lexical database our 118k base concepts came from) learned this the hard way: it groups words into *synsets* — sets of words sharing one meaning — and originally identified them by their byte position in a data file, so every release shifted every ID and required painful mapping files. Its successors (the Collaborative Interlingual Index, Wikidata's Q-numbers) all converged on opaque never-reused IDs with mutable definitions. The tradeoff: references never break, but the ID no longer *proves* anything about the definition — you lose self-verification, the very thing our content-hash buys.

**Fixpoint / order-invariance.** A fixpoint is a state that a process maps to itself: run the "revisit every concept and re-express it in the best available vocabulary" pass, and nothing changes anymore. The kernel's central claim — canonical, deterministic vectors — requires the settled corpus to be a fixpoint that is also *order-invariant*: whatever order we happened to author concepts in, reconciliation lands on the same final corpus. If the end-state depends on authoring order, "canonical" is false advertising.

**Strongly-connected components (SCCs) / bidirectional pairs.** Some concept pairs mutually define each other: buy/sell, parent/child, borrow/lend. There is no non-arbitrary way to say which comes "first"; if each references the other, they form a cycle — in graph terms, a strongly-connected component. Cycles are exactly what a hash-of-what-you-reference scheme can't naively handle (which hash goes into which?).

## 2. The design space

Four realistic identity models, with honest tradeoffs:

**(a) Content-hash-only, always.** Pure, self-verifying, no infrastructure. But while the corpus is evolving, every reconciliation pass re-mints most of the corpus, and any *external* holder of an old hash (world-layer facts, PSS snapshot packs) is stranded — the formal-fixpoint angle showed you can't even *state* a fixpoint over hashes while content is moving, because the thing you're iterating on keeps renaming itself. Nobody runs this; even Git, the archetype, layers mutable refs on top.

**(b) Two-layer permanent: stable opaque ID + versioned definition/vector.** The WordNet/CILI/Wikidata pattern. Battle-tested at 100M-concept scale, references never break. Cost: the kernel is no longer inherently definitional — the ID proves nothing, and you carry naming infrastructure forever. This is the model Jesse suspects is over-engineering for our end-state, and the prior art partially supports him: those systems keep the mutable layer forever because their definitions *never* stop changing. Ours is supposed to.

**(c) Version-and-migrate: hashes as IDs, plus published old→new mappings on every change.** Git's rebase model. Works inside one corpus; the content-addressed-systems angle flagged the failure mode: external references can't be rewritten by us, so mapping files accumulate indefinitely. Tolerable as history, miserable as a living identity model.

**(d) Settle-then-freeze: stable working names during construction; compute the fixpoint; mint content-hashes once, from the settled corpus; keep an append-only old→new record as history.** This is the **Unison** model (content-addressed-systems angle) — a programming language whose functions are literally named by hashes, which handles change via an atomic "upgrade" that rewrites the whole dependent cone in one transaction, and which handles mutual recursion by hashing each SCC *as a single unit* with placeholder internal references, so neither buy nor sell is privileged. Notably, our hash design (docs/design-hash-input.md, gist §6) *already adopted* SCC-as-unit hashing — the identity layer anticipated cycles; what's missing is the upgrade/reconciliation machinery. And the working corpus is already living this way de facto: kernel-v0's 54 concepts reference each other by mutable slugs (`urn:kernel-v0:give`), not hashes (kernel-integration angle).

**Honest assessment of the purist position.** Jesse's hypothesis — "once the kernel stabilizes, the content-hash alone should suffice" — is *achievable and has an existence proof*, but under three conditions, and it is stronger than he may realize in one respect and weaker in another.

It's *validated* by Unison: at runtime a settled Unison codebase is exactly the "inherently definitional" artifact he wants — only hashes, the naming layer discarded as build-time scaffolding. The formal-fixpoint angle adds that the math actively *forces* his sequencing: since no fixpoint over hashes is expressible while content moves, stable-ID scaffolding during settlement isn't a rival identity model, it's the only coherent construction method — and every successful predecessor did both, in that order.

The three conditions: **(1) The fixpoint must actually exist and be order-invariant.** Theory (Knaster–Tarski, and structurally the same argument as shortest-path algorithms) guarantees existence, termination, and order-independence — but only *given* a pinned cost function (what counts as a "better" explication), a pinned deterministic tie-break for equally-good paraphrases, snapshot-style update semantics, and — the real weak point — a *deterministic* "re-express this concept faithfully" procedure. If that last step is an LLM judgment call, all guarantees collapse to heuristics (formal-fixpoint angle). NSM theory won't rescue us: it fixes the skeleton (acyclic, stratified, primes at the bottom) but deliberately under-determines which of several faithful explications is canonical — NSM's own literature revises explications constantly (lexical-ontological angle). **(2) The freeze must be real.** CILI-style experience says definitions in a living lexicon never fully stop changing; our answer is architecture.md §1.0's stipulative posture — we *decree* the settled definitions — plus CILI's deprecate-and-mint (a new hash with a `replaces` edge) for genuine post-freeze corrections. **(3) External-reference hygiene.** Once hashes escape into external systems, no rewrite can fix them; the old→new mapping must be published as a permanent append-only artifact even after settlement (Git's lesson).

The one anti-pattern all four angles agree on: mutable pointers *inside* the kernel (IPNS-style) — they reimport trust, key management, and liveness into an artifact whose entire point is self-verification.

## 3. Recommendation

Jesse is right that it's premature to *commit* to a final identity model — but the question is now sharp, not vague. Everything except one item is settled by prior art and theory:

- Build-phase identity: **stable working names** (we already do this in kernel-v0) — mathematically forced, not a taste choice.
- Bidirectional pairs: **SCC-as-unit hashing**, already in our hash design; semantically, prefer the FrameNet-style move of factoring the shared scenario (the commerce event under buy/sell) into its own concept, which removes the asymmetry rather than tie-breaking it (lexical-ontological angle).
- End-state: **settle-then-freeze (d)**, i.e. the purist position with transitional scaffolding — *conditional on one empirical unknown*.

That unknown, the single thing that must be learned first: **does reconciliation actually converge to an order-invariant fixpoint when the "re-express faithfully" step is a real (LLM-driven, pinned) procedure rather than an idealized function?** If yes, hash-only identity at freeze is exactly what the mathematics licenses. If no, the frozen hashes would be accidents of authoring order, the canonical-vector claim fails, and we'd need the permanent two-layer model (b) — or a redesign of the reconciliation procedure — before minting anything. Do not pick between (b) and (d) until this is measured.

## 4. The next experiment: E10-fix (kernel-integration angle, endorsed)

**Setup.** 30 concepts: the 18 kernel-v0 concepts on the 22 known cross-reference edges plus their dependency closure, plus 6 fresh concepts forming 3 bidirectional pairs (buy/sell, borrow/lend, parent/child). Draw 10 seeded random authoring orders. For each order, author concepts one at a time with a pinned LLM (Haiku, temperature 0, one pinned prompt), allowed to reference only already-authored concepts, else bare primes; every output through `validateExplication`, fail closed. Then reconcile: visit concepts in alphabetical order, re-express each against the full pool ("shortest faithful; change only if strictly better"), deterministic hash-based tie-break for pair members, repeat until no change (max 5 rounds). Author calls cached by (concept, hash of pool state) so residual disagreement is order-driven, not sampler noise.

**Measure**, pairwise across the 10 orders, before vs after reconciliation: (1) fraction of concepts with byte-identical canonical payloads (= identical `urn:kot` hashes); (2) angle between the same concept's vectors under the pinned `kot-enc-B/1` encoder at D=8192, calibrated against X1's measured floors (fp16 noise 0.000213 rad; smallest meaningful single-edit 0.002342 rad). Controls: the unreconciled corpora (the drift we must close), and reconciliation under shuffled visit schedules (if the result depends on schedule, the "fixpoint" is an artifact).

**Pre-registered outcomes.** **PASS:** ≥90% of concepts hash-identical across all 10 orders within 5 rounds, residual vector disagreements below 0.0023 rad → hash-only identity at freeze is empirically defensible; proceed with (d). **PARTIAL:** vectors converge (≥90% drift reduction vs control) but bytes don't → meanings settle, spellings don't; the two-layer scaffold (b) is needed at least until the canonicalization/tie-break rules are strong enough to close the byte gap. **FAIL:** <50% hash agreement, oscillation, or schedule-dependent results → order-invariance falsified; the purist end-state needs a redesign, not a freeze.

**Cost.** ~3,300 Haiku calls at ~1–2k tokens: single-digit dollars, a few hours wall-clock; all encoding CPU-trivial and niced for this box's 2 shared cores.

One framing for Jesse to keep: the repo's most mature component already lives the two-stage pattern — the encoder has a stable human name (`kot-enc-B/1`) *and* a content hash, with a deliberate re-versioning ritual. The question E10-fix answers is whether the *concepts* can eventually graduate to hash-only, the way a settled Unison program does.

---

# Appendix — the four research briefs (verbatim)

## Angle: content-addressed-systems

I've grounded in the repo (docs/design-hash-input.md, docs/architecture.md §1.1, encoder/src/encoder.ts `ALGORITHM_VERSION = 'kot-enc-B/1'`, CLAUDE.md pin rules). Brief follows.

---

# Prior art: how content-addressed systems survive re-derivation

**Bead kernel-of-truth-bo6 — identity vs content-hash, for a non-ML reader**

**The shared problem.** A *content-addressed* system names a thing by a cryptographic hash of its bytes. This buys tamper-evidence and deduplication, but the name is brittle by construction: improve the definition and you have, by definition, a different name — and every reference to the old name is now stale. Every mature content-addressed system has hit exactly the kernel's bo6 problem, and each answered it differently.

**Unison (the closest analogue).** Unison is a programming language where a function's true name is a hash of its abstract syntax tree, with all dependencies referenced *by their hashes*, not by human names. Human names live in a completely separate, mutable naming layer (the "codebase manager"): a name is just a pointer to a hash, so renaming is free — no code changes, no rebuilds. When you *change* a definition, Unison does not mutate anything: the new definition gets a new hash, and the `update`/`upgrade` machinery mechanically rewrites every dependent to point at the new hash — which changes *their* hashes too, cascading through the whole dependent cone in one tool-assisted transaction. Nothing dangles, because all hash-references live inside the codebase being rewritten. Crucially for buy/sell: Unison handles mutually recursive definitions by hashing the *strongly connected component* (a group of definitions that reference each other) **as a single unit**, with internal cross-references replaced by positional placeholders. Neither member is "first"; the pair has one joint identity. Note the gist §6 ordering-key algorithm adopted in docs/design-hash-input.md already does essentially this — the kernel's hash design anticipated cycles; what's missing is the *upgrade* machinery.

**Nix.** Nix builds software from "derivations" (build recipes). Classic Nix is *input-addressed*: a package's store path hashes the recipe and all inputs, so touching one low-level input re-derives and re-addresses everything downstream — a mass rebuild, the exact cascade bo6 fears. Newer *content-addressed* derivations add "early cutoff": after a rebuild, if the output bytes are unchanged, the new path equals the old one and the cascade **stops**. The lesson: distinguish "the derivation changed" from "the result changed", and only propagate the latter.

**Git.** Git's object store (blobs, trees, commits) is immutable and content-addressed, forming a Merkle DAG — a structure where each node's hash covers its children, so one hash authenticates the whole history. Usability comes entirely from a thin mutable layer: refs (branches, tags) are named pointers freely repointed to new hashes. Git also shows the failure mode: history rewriting (rebase) mints all-new hashes, and every *external* holder of an old hash is stranded — tolerable inside one repo, painful across repo boundaries. External references are the thing a cascading rewrite cannot fix.

**IPFS/IPLD.** A CID is an immutable content hash (structurally the same multihash/multibase convention the kernel's URN scheme already uses). Mutability is bolted on as IPNS: a name that *is* a public key, whose owner signs "this key currently points at CID X". Cost: resolution is no longer self-verifying from content alone — you now need key infrastructure, trust in the key holder, and a live network. Mutable pointers import trust and liveness dependencies that pure content addressing was supposed to eliminate.

**Assessing Jesse's purist position.** *No* system achieves "content-hash alone" for a corpus that is still evolving — all four grew a second layer (Unison names, Nix channels/flake refs, Git refs, IPNS). But Unison validates the purist claim for the **end-state**: at runtime there are only hashes; the naming layer is build-time scaffolding, and a settled Unison program is exactly the "inherently definitional" artifact Jesse wants. The honest restatement: content-hash-only is a property of a *frozen* corpus, and the systems that get there cleanly (Unison) do so via heavy transitional machinery — not via versioned mutable pointers in the final artifact. Jesse's instinct (no permanent ID/version indirection) and the transitional two-stage scaffolding are not in conflict; every successful system did both, in that order. The one caveat is Git's: once `urn:kot:` hashes escape into *external* systems (PSS estate, snapshot packs per bead 6j5), a rewrite strands them — so publish an old-hash→new-hash mapping (Unison keeps these as "patches") as a permanent, append-only artifact even after settlement.

**Three patterns worth stealing:**

1. **SCC-as-unit hashing (Unison).** Hash mutually-referential pairs (buy/sell, parent/child) as one strongly-connected component with placeholder internal references. Dissolves bo6's "someone must be authored first" problem outright — neither member is privileged. The gist §6 algorithm already specifies this; make the reconciliation pass actually *form* the SCCs.
2. **`upgrade` as an atomic corpus rewrite, not a versioning scheme (Unison).** Treat re-derivation ("male" re-expressed over "person") as a mechanical pass: rewrite the definition, cascade new hashes through the dependent cone in one transaction, emit the old→new mapping as history. Hashes change; nothing breaks, because intra-corpus references are rewritten together and extra-corpus consumers get the mapping. This is the transitional scaffolding — a tool, not an identity model — which is precisely Jesse's preference.
3. **Early cutoff (Nix CA-derivations).** After rewriting a concept, check whether the *canonical identity payload* (and separately the encoder vector, pinned by `kot-enc-B/1`) actually changed. If a re-expression is canonically equivalent, the hash is identical and the cascade halts. This bounds fixpoint iteration cost and gives a concrete convergence test for the settled corpus: the fixpoint is reached when an `upgrade` pass produces zero new hashes.

Anti-pattern to avoid: IPNS-style mutable pointers *in the kernel itself* — they reintroduce trust, key management, and liveness into an artifact whose whole point is self-verification.

---

## Angle: lexical-ontological-identity

I have enough grounding from the repo (design-hash-input.md, architecture.md §1.0–1.1, design-molecule-tier.md's topological mint order and SCC ordering-key adoption). Here is the brief.

---

# Prior art brief: stable identity in large lexicons, and whether NSM fixes a definition order

*(for bead kernel-of-truth-bo6 — non-ML reader; repo anchors: docs/design-hash-input.md, docs/design-molecule-tier.md §1.3, docs/architecture.md §1.1)*

## 1. The vocabulary, in plain words

**WordNet.** A *lemma* is a dictionary headword ("bank"). A *synset* is a set of lemmas that share one meaning, plus a gloss and links to other synsets ({bank, cant, camber} = "a slope in the turn of a road"). A *sense* is one lemma's membership in one synset. Crucially, WordNet's primary identifier for a synset is its **byte offset in a data file** (e.g. `02038357-n`) — an accident of serialization. Add one synset anywhere and every offset after it shifts. So synset IDs are **not stable across versions**, and thirty years of downstream pain followed: every WordNet upgrade requires published *mapping files* between versions, built semi-automatically and imperfect (senses merge, split, and vanish — measurable sense drift between 1.6 → 2.0 → 3.0 → 3.1).

WordNet's own partial fix is the **sense key** (`bank%1:17:01::`): a composite of lemma + lexicographer-file + a lexical ID, deliberately independent of file offsets. Sense keys are much more stable than offsets — but they are stable *names*, not stable *meanings*: the gloss behind a sense key can be rewritten between versions and the key does not change. That is the important lesson: **WordNet decoupled identity from both storage layout and definition text.**

**ILI / CILI.** When dozens of language-specific wordnets appeared, none of their internal IDs could serve as the shared backbone, so EuroWordNet introduced the **Inter-Lingual Index**: a flat list of language-neutral concept records that each wordnet's synsets *map to*. Its modern successor, the **Collaborative Interlingual Index (CILI)** (Bond, Vossen & Fellbaum, 2016), makes the design explicit: each ILI concept is an **opaque numbered ID (`ili:i35545`) plus a short English definition**; new concepts get new IDs; IDs are **never reused and never deleted, only deprecated** (with a pointer to a successor). Definitions may be *clarified* but a change of meaning requires deprecate-and-mint. This is the field's mature answer to exactly the bo6 problem: **a monotonic, append-only identity layer, decoupled from any one resource's internal representation.**

**Wikidata QIDs.** Same pattern, harder-nosed: `Q42` is a meaningless integer. Labels, descriptions, and every statement about the item change freely, daily, in 300 languages; the QID never does. Deleted QIDs are never reassigned; merged items leave permanent redirects. Wikidata is the largest existence proof that *identity via opaque ID + mutable description* scales to ~110M concepts with heavy interlinking.

**BabelNet** mints its own opaque synset IDs (`bn:00005054n`) over merged WordNet+Wikipedia clusters — and its version-to-version instability (clusters re-merge) is a known complaint, showing that IDs derived from *aggregation output* inherit the aggregation's instability. **Cyc** uses constants (`#$Dog`) each backed by a permanent external GUID; the surrounding axioms — the "definition" — are revised continuously against the fixed handle.

**The pattern is unanimous.** Every long-lived concept inventory that survived definitional evolution did it the same way: **an opaque, immutable, never-reused identifier, with the definition attached as mutable (or deprecate-and-succeed) content**. No production system content-addresses concept identity by hashing the definition — because all of them needed to revise definitions without breaking references, which is precisely the operation a content hash forbids.

## 2. Does NSM give definitions a canonical order?

Partly — and the structure it gives is a *partial* order, not a total one.

NSM's method is **reductive paraphrase with a non-circularity requirement**: every explication must bottom out in the ~65 primes, and definitions must never be circular. That immediately induces a **dependency DAG requirement** — exactly the acyclicity your molecule tier already enforces mechanically ("already-minted only", design-molecule-tier.md §1.3).

Goddard's **semantic molecules** (marked `[m]` — "hands", "children", "water") add stratification: molecules are non-prime concepts licensed to appear *inside* other explications, and they come in **nesting levels** — level-1 molecules defined purely in primes, level-2 molecules using level-1 molecules, and so on. Goddard even posits ~25 near-universal molecules and notes some (e.g. body parts) sit low in every language's hierarchy. So NSM prescribes: (a) acyclicity, (b) a *layered* structure, (c) a rough bottom layer. That is a **canonical stratification**, and your v0 tier already tracks it.

But NSM **under-determines everything the bo6 bead actually needs**:

- **No canonical explication.** NSM's adequacy test is substitutability judged by analysts; Riemer (2006) showed it is not decidable. Two NSM experts routinely publish different explications of the same word, and explications are revised across Wierzbicka's/Goddard's own books. NSM has *no* doctrine that an explication, once written, is final — quite the opposite: revision is the normal scholarly process.
- **No canonical molecule choice.** Whether "father" routes through *man [m]* → *woman [m]* → *child [m]* or is spelled out in primes is a paraphrase-equivalence NSM does not adjudicate. Your frequency-order authoring artifact ("male" written before "person" exists) is a choice NSM permits both ways.
- **Converse pairs (buy/sell, parent/child) have no NSM-sanctioned winner.** NSM practice handles converses not by defining one from the other, but by giving each its own explication over a **shared scenario** (both buy and sell describe the same someone-gives-something-someone-gives-money event from different participants' viewpoints — the same insight FrameNet encodes as a shared Commerce frame). The prior-art answer to "which of the pair goes first" is: *neither* — factor out the shared frame as its own (possibly unnamed) concept, and define both members over it. Your SCC ordering-key algorithm (design-hash-input.md, gist §6) is the degenerate mechanical version of this; the frame-extraction version is semantically cleaner and removes the asymmetry rather than tie-breaking it.

## 3. The squarely-put answer

**Is there a natural stable anchor?** Yes, and it is not the hash of the explication. The WordNet-lineage anchor is *the sense/ILI record*: an opaque ID whose meaning is fixed by social commitment ("this ID means the concept currently described by this text") while the text improves. Every system that tried to anchor on representation internals (offsets, cluster output) paid for it in mapping files. Jesse's purist end-state — hash-only identity — matches prior art **only at fixpoint**: CILI-style IDs are effectively content-addressable *once definitions are frozen*, and CILI's deprecate-and-succeed is exactly "a new hash with a `replaces` edge". So the two-stage scaffold (stable opaque ID during settlement, hash as the post-fixpoint identity, with hash-succession edges during convergence) is not an anti-purist compromise — it is the transition mechanism every predecessor used, and NSM's own revision culture guarantees the settlement phase is real, not hypothetical.

**Does NSM fix the order?** It fixes the *skeleton* (acyclic, stratified, primes at the bottom, ~25 molecules low) and leaves the *flesh* (which explication, which molecule route, converse-pair priority) under-determined. The fixpoint therefore cannot be discovered from NSM theory; it must be *computed* (iterate re-expression until no explication improves — a reconciliation pass NSM is silent on) and then *endorsed* (per architecture.md §1.0's stipulative-definition posture). For converses, prefer shared-frame extraction over SCC tie-breaking.

---

**Key sources:** Fellbaum (ed.) *WordNet* 1998; WordNet sense-key docs (`senseidx(5WN)`); Daudé et al. version-mapping work; Vossen *EuroWordNet* 1998 (ILI); Bond, Vossen & Fellbaum, "CILI: the Collaborative Interlingual Index," GWC 2016; Wikidata identifier policy (Q-IDs never reused); Navigli & Ponzetto, BabelNet 2012; Lenat, Cyc constants/GUIDs; Goddard, "Semantic molecules and semantic complexity" 2010; Goddard & Wierzbicka *Words and Meanings* 2014; Riemer 2006 (substitutability circularity); Fillmore, FrameNet Commerce frame (converse pairs).

---

## Angle: formal-fixpoint

Below is the deliverable brief.

---

# Order-invariance as a fixpoint: formal grounds for reconciliation (bead bo6)

## 1. Setup

Let a **corpus** be a finite map `K : Name -> Explication`, where each explication is a canonical AST (`kot-ast/1`) whose leaves are primes or references to other names. The **dependency graph** G(K) has an edge X→Y when X's explication references Y. Note one deliberate abstraction: work over *stable symbolic names*, not `urn:kot:` hashes. Since the hash is computed over the explication bytes (docs/design-hash-input.md), any re-derivation cascades hash changes to every transitive referrer; no fixpoint over *hashes* can even be stated while content is moving. So: **settle the abstract corpus first, mint hashes once, at the end.** This is a mathematical forcing, not a style choice — and it is compatible with Jesse's purist end-state: hash-only identity is coherent *for the settled kernel*; any stable-ID scaffolding is strictly a construction-time device that the final minting pass discards.

Define the **reconciliation operator** R: for each concept X, `R(K)(X) = best(X, K)` — the best faithful explication of X given the vocabulary currently in K (all concepts, evaluated against the *same snapshot* K). "Best" means argmin of a **cost function** `c(E)`, e.g. the lexicographic tuple *(clause count, reference depth, canonical bytes)*. Order-invariance is then exactly: **K\* is a fixpoint, R(K\*) = K\*, reached from any authoring order.**

## 2. Existence and uniqueness — what the theory actually gives you

**Knaster–Tarski** guarantees a fixpoint when R is monotone on a complete lattice. The honest question is what order on corpora makes R monotone. The natural candidate is the pointwise **cost order**: K ⊑ K′ iff `c(K(X)) ≥ c(K′(X))` for all X. Because each concept has *finitely many* well-formed explications (byte cap + depth cap ≤ 4, per the molecule-tier rules), the candidate set per concept is finite and `c` well-orders it. This turns reconciliation into something structurally identical to **Bellman–Ford / value iteration**: the "cost of X's best definition" plays the role of shortest-path distance, and adding vocabulary can only *shorten or preserve* best definitions, never lengthen them — provided one discipline holds:

> **(D1) No regression:** R may replace an explication only with one of strictly lower cost, or equal cost and strictly smaller canonical bytes.

Under D1, each application of R strictly descends in a well-founded total order on a finite space, so **Kleene iteration from the bottom element** (the all-bare-primes corpus — which is exactly the frequency-ordered corpus you have today) **terminates at a fixpoint in finitely many rounds**. Existence and termination are genuine theorems here, not heuristics.

**Uniqueness** needs one more ingredient. Fixpoint theory gives a unique *least* fixpoint; for it to be authoring-order-independent you additionally need R itself to be **order-free within a round**: compute every `best(X, K_t)` against the frozen snapshot `K_t` (Jacobi-style), never against a half-updated corpus (Gauss–Seidel-style). Gauss–Seidel sweeps converge too, but the *path* — and, where ties exist, the *result* — can depend on sweep order. Snapshot semantics kills that dependence.

## 3. Termination vs oscillation: the flip-flop

The classic failure: A re-defines via B (cheaper), then B re-defines via A (cheaper), then A's definition via B is no longer well-founded, and the pair churns. Under D1 alone this cannot loop forever (cost strictly descends), but it *can* land the pair in a mutual cycle — which the current validator rejects (molecule rule 4: "already-minted only", explicit cycle check). Unilateral improvement is the wrong move inside a cycle. The correct discipline:

## 4. SCCs as joint co-definitions

Condense G(K) with Tarjan into a DAG of strongly-connected components. Singleton SCCs are ordinary concepts. A non-trivial SCC {buy, sell} is treated as **one definitional unit**: its members are solved *jointly* — choose the assignment of explications to all members minimizing *total* component cost, with cross-references inside the component permitted as internal links. For identity, hash the **whole component as a unit** and derive member ids as component-hash + canonical ordering key — which is precisely the gist §6 machinery the hash-input decision already adopts unchanged ("Tarjan SCC → … → digest"; design-hash-input.md, design-math-sector.md §6 note). Neither buy nor sell is the arbitrary first-mover; symmetry is preserved in the identity layer itself.

## 5. Algorithm sketch

```
RECONCILE(K):                          # K over symbolic names, not hashes
  repeat:
    G   := dependency graph of K
    SCCs, order := tarjan(G)           # order = reverse topological over condensation
    K'  := copy of K                   # frozen snapshot — Jacobi semantics
    for C in order:                    # leaves (prime-only) first
      if |C| == 1:
        K'[X] := argmin_c { E : E faithful to X, refs ⊆ dom(K) \ {X} }   # D1 + tie-break
      else:
        K'[C] := argmin_totalc { joint assignment to C;
                                 internal cross-refs allowed;
                                 external refs ⊆ dom(K) \ C }
    if K' == K: break                  # fixpoint
    K := K'
  MINT(K): for C in reverse topo order of condensation:
    hash each SCC component per gist §6 (JCS bytes, profile header, ordering key)
  return (K, urns)
```

Termination bound: total corpus cost is a natural number that strictly decreases each outer round, so rounds ≤ initial total cost; in practice a handful.

## 6. What concretely breaks uniqueness — and what to pin

1. **Ties.** Multiple equally-minimal faithful explications ("male person" via person vs via man). *Every* such tie must fall to a pinned canonicalization: lexicographic order on JCS bytes of the candidate is deterministic, auditable, and already in the repo's idiom. Without it, the kernel is only unique *up to paraphrase* — which falsifies the canonical-vector claim. So yes: **a tie-breaking rule is a mandatory part of the profile**, versioned exactly like `ALGORITHM_VERSION` (`kot-enc-B/1`) pins the encoder.
2. **The cost function is a semantic commitment.** Different `c` ⇒ different fixpoint ⇒ different kernel. Uniqueness holds *relative to a pinned c*; there is no cost-free notion of "the" minimal kernel. Pin it in the profile header.
3. **The faithfulness oracle — the real weak point.** Everything above assumes `best(X, K)` enumerates a decidable candidate set with a decidable equivalence check. If candidates come from an LLM (as for the Haiku tier), R is not even a function, and *all* guarantees collapse to heuristics; determinism then only holds for the *verification* pass, not generation. The panel's remedy is the right one: admit exactly a closed list of terminating, confluent, syntax-directed rewrites as the equivalence relation, nothing entailment-shaped.

**Honest summary.** Existence, termination, and order-independence of the fixpoint are theorem-grade *given* D1, snapshot updates, a pinned well-founded cost, a pinned tie-break, and a decidable candidate/equivalence procedure. The SCC co-definition needs no new identity machinery — gist §6 already provides it. The unguaranteed residue is concentrated in one place: whether "re-derive faithfully" can be made a deterministic procedure rather than a judgment call. That is the experiment worth running before committing to hash-only identity — and if it succeeds, Jesse's purist end-state (content-hash alone, minted once from the settled fixpoint) is not just aesthetically preferable but exactly what the mathematics licenses.

---

## Angle: kernel-integration-experiment

I have what I need. Key facts grounded: the encoder pin covers {schema, algorithm, D, codebook, weighting} (`encoder/src/contentHash.ts`, `ALGORITHM_VERSION = 'kot-enc-B/1'`); `encodeConceptSet` binds referenced concepts' vectors recursively and fails closed on cycles (`encoder/src/encoder.ts:360-364`); identity is JCS-canonical-JSON of the identity payload (`docs/design-hash-input.md`) with gist §6 SCC handling at the hash layer; kernel-v0's 54 concepts use slug URNs (`urn:kernel-v0:give`) with 22 DAG cross-reference edges; X1-kernel-v0 gives the noise floor (0.000213 rad fp16) and minimum single-edit margin (0.002342 rad); E9 measured vectors via pinned kot-enc-B/1 @ D=8192 (hash `40e8c8ba…`) through the pinned X4 JL 8192→576 projection, unit-normalised.

---

# Identity under reconciliation: what the machinery wants, and an experiment to settle it

## Part A — what the existing machinery actually needs

**The encoder pin is orthogonal — and is itself a precedent.** `ALGORITHM_VERSION` and `encoderContentHash()` pin the *map* from explication to vector, not any concept's identity. Changing D, codebook, or weighting is an encoder version bump with deliberate X0 golden regeneration. Note the pattern: a stable human name (`kot-enc-B/1`) *plus* a content hash, with an explicit re-versioning ritual. The repo's own most mature component already uses the two-stage "stable label + hash" scheme Jesse calls transitional.

**The vector construction makes content-hash identity a Merkle DAG — with Merkle consequences.** `encodeConceptSet` encodes a concept by recursively binding the *vectors* of every concept it references, and requires the reference graph to be a DAG (cycles fail closed; fixpoint encoding is explicitly deferred). Under `urn:kot:<hash>` references, re-deriving one concept therefore does two things at once: (a) the referrer's payload must swap in the new URN, changing the referrer's hash, and so on up the entire reverse-dependency tree — every reconciliation touch rehashes all ancestors; (b) if the referrer *doesn't* swap, it keeps a valid hash pointing at a deprecated definition — silent semantic staleness with no mechanical signal. This is exactly how git behaves, and it is fine for a *settled* corpus. For a corpus *under reconciliation* it means every pass churns most identities in the 118k+ set.

**There is a live conflict on bidirectional pairs.** The identity layer already solves cycles (design-hash-input adopts the gist §6 SCC ordering-key, SCC ≤ 32), but the encoder cannot encode them — v0 fails closed on any cycle. So buy/sell-type pairs must be broken acyclically for the *vector* layer regardless of which identity model wins. Any fixpoint procedure needs a deterministic, order-independent tie-break for who gets the bare-prime definition.

**Facts and interop need something stable.** World-layer facts must bind to identifiers that survive definitional refinement; a fact over `urn:kot:<hash>` dangles the moment its concept is re-expressed. And the PSS bridge already ships the linking device a two-ID world needs (`sameDefinitionAs`, dual-hash option (a) in design-hash-input). Meanwhile the actual working corpus, kernel-v0, references concepts as `urn:kernel-v0:give` — mutable slugs. The build phase is *already* living in stable-ID mode de facto.

**Conclusion.** The machinery pushes toward: stable working IDs during authoring/reconciliation, content-hash identity minted at *freeze* — Jesse's transitional scaffold, but forced by the code, not chosen by taste. His purist end-state (hash alone suffices) is coherent **iff** reconciliation reaches an order-invariant fixpoint, so that the frozen hashes are canonical rather than accidents of authoring order. That is an empirical claim. Part B measures it.

## Part B — E10-fix: measuring order-invariance of the reconciled fixpoint

**Concept set (30).** The 18 kernel-v0 concepts participating in the 22 known cross-reference edges plus their dependency closure (e.g. repair→broken→break, condolence→grieving→{death→event, sad}, trustworthy→{promise, lie}), plus 6 fresh concepts forming 3 bidirectional pairs with no acyclic order: buy/sell, borrow/lend, parent/child. Dependencies are read mechanically from conceptRefs via the encoder's `collectConceptRefs` — no hand annotation.

**Procedure.** Draw N = 10 uniformly random total orders over the 30 slugs (seeded, recorded). For each order, *author* concepts one at a time with a pinned LLM author (Haiku, temperature 0, one pinned prompt), under one rule: you may reference only concepts already authored *in this order*; otherwise use bare primes. Every output passes `validateExplication`, fail closed. Then run a **reconciliation pass**: visit concepts in canonical alphabetical slug order; the author sees the full current pool and re-expresses the concept ("shortest faithful explication; change only if strictly better"); for the bidirectional pairs, the member whose canonical-AST sha-256 is lexicographically smaller keeps the prime-only base (a deterministic, order-independent tie-break that keeps the encoder's DAG requirement). Repeat rounds until no explication changes, max R = 5. Crucially, author calls are **cached by (concept, sha-256 of the JCS-canonical pool state)**: identical pool states get byte-identical rewrites, so the process is deterministic given trajectory, and any residual disagreement is genuinely order-driven, not sampler noise.

**Metrics, per concept, pairwise across the 10 orders, BEFORE vs AFTER reconciliation.**
1. *Explication drift:* fraction of order-pairs whose JCS identity payloads are byte-identical (identical payloads = identical `urn:kot` hashes). Secondary descriptive: canonical-AST node-level diff count.
2. *Vector drift:* encode each order's full corpus with `encodeConceptSet` at the pinned kot-enc-B/1, D = 8192 (content-hash `40e8c8ba…`, fail closed), and measure the angle between the same concept's vectors across orders — in native D = 8192 and through the pinned X4 JL 8192→576 unit-normalised projection, i.e. the identical instrument E9's vector tables were built with. Calibration comes free from X1-kernel-v0: fp16 noise floor 0.000213 rad; minimum meaningful single-edit angle 0.002342 rad; median 0.1045 rad.

**Controls.** (i) *No-reconciliation:* the as-authored corpora — the drift reconciliation must close. (ii) *Shuffled-schedule reconciliation:* same passes but per-run random visit order instead of alphabetical; if convergence is a true fixpoint, final corpora should agree with the canonical schedule's; if agreement depends on the schedule, the "fixpoint" is an artifact of the visit order.

**Pre-registered outcomes.** **PASS:** after ≤5 rounds, ≥90% of concepts hash-identical across all 10 orders, and every remaining disagreement has max inter-order angle < 0.0023 rad (below the smallest meaningful single edit) — content-hash-alone identity is empirically defensible at freeze. **PARTIAL:** hash agreement < 90% but median vector drift reduced ≥90% vs the no-reconciliation control and below X1's p5 single-edit angle (0.0188 rad) — vectors converge, bytes don't; identity needs the two-stage scaffold. **FAIL:** hash agreement < 50%, oscillation without fixpoint, or shuffled-schedule corpora disagreeing with canonical-schedule corpora — order-invariance falsified; the purist end-state requires a redesign, not a freeze.

**Cost.** ~300 authoring + ≤1,500 reconciliation + ~1,500 control Haiku calls at ~1–2k tokens: single-digit dollars, a few hours wall-clock. All encoding/metrics are CPU-trivial (X1 already ran 2,475 encode-and-compare operations on this box), niced for the 2 shared cores.

**Files:** /home/ec2-user/css/kernel/kernel-of-truth/docs/design-hash-input.md, /home/ec2-user/css/kernel/kernel-of-truth/encoder/src/contentHash.ts, /home/ec2-user/css/kernel/kernel-of-truth/encoder/src/encoder.ts, /home/ec2-user/css/kernel/kernel-of-truth/data/kernel-v0/concepts/, /home/ec2-user/css/kernel/kernel-of-truth/poc/results/x1-kernel-v0-report.md, /home/ec2-user/css/kernel/kernel-of-truth/poc/e9/README.md
