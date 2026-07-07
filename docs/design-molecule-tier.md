# Design record — the molecule tier, v0

**Status:** implemented (data/molecules-v0, 54 records, all gates green) ·
**Date:** 2026-07-07 · **Spec anchor:** concept-hash-design.md §3.5 (normative
molecule rules), §3.4 (WebResource example) · **Motivation:** M0b measured
that **33.0% of TinyStories top-500 content mass is molecule-gated** — the
single biggest coverage limiter in the programme (m0b-report.md: "the
molecule tier is load-bearing for any corpus-level coverage claim, and it is
currently unbuilt and unsized"). This note records how v0 sizes it.

**Result up front** (details: `mapper/m0/results-molecules-v0/`): 54
molecules move the profile-1+molecule expressibility ceiling from **58.2% →
87.6% of top-500 content mass** (direct 74.7%; +1.5 borderline band to
89.1%), i.e. from **~26% → ~40% of all word tokens** under the m0b scaling
convention. Adding the 54 labels to the mapper lexicon creates **0 new
ambiguous surfaces** (measured, mapper default untouched).

## 1. Authoring workflow

1. **Selection by frequency-weighted coverage.** Shopping list = the 246
   `molecule`-class rows of the committed m0b report, ranked by token count.
   A candidate is minted only if (a) high direct mass (day, smile, run…),
   (b) high *transitive* leverage as a grounding target (hand, water, house,
   child, animal…), or (c) structurally required by another mint (woman for
   mother; open for close/box). NSM's ~25 claimed-universal molecules
   (Goddard 2010) were preferred wherever frequency allowed — 20 of the 54
   are on or adjacent to that list (water, fire, sun, sky, ground, day,
   night, hands, head, eyes, mouth, children, women, men, mother, father,
   bird, fish, tree, wood-adjacent rock).
2. **Mint-only-what-explication-cannot-reach.** Natural kinds, materials,
   percept qualities, basic bodily actions and expression gestures, and
   artifact kinds whose identity is perceptual/material get minted.
   Functional/relational kinds (toy, room, door, bed, chair, park, family,
   school…) are NOT minted: once the base molecules exist they are
   profile-1-explicable, and the measurement counts them in a separate
   *explicable-with-molecules* class. This discipline keeps the molecule
   tier small and pushes everything reachable back into the explicated
   (first-class) tier — the direction the gist wants pressure to flow.
3. **Topological mint order.** Grounding refs may point only to kernel-v0
   records (depth 0) or earlier molecules — rule 4's "already-minted only"
   becomes a mechanical acyclicity guarantee. Depth budget is spent
   deliberately: father is depth 4 (the cap) via man → woman → child.
4. **Grounding-note discipline.** Notes are recognition anchors in the
   §3.5-rule-3 controlled lexicon, mechanically gated by
   `data/molecules-v0/validate.mjs` (tokenizer + pinned exponent table +
   ref syntax + byte cap + depth + cycle check; the validator also rejects
   the gist's own rev-1 illegal example tokens "pages"/"computers").
   Notes do NOT claim to be explications — see §3 honesty.
5. **[m] second-class flagging** (rule 1): `semanticStatus: "Molecule"` and
   `flag: "[m]"` on every record; inside notes, every molecule ref must be
   followed by the `[m]` token and kernel refs must not be — both enforced.

## 2. Composition with profile-1 — the transitive tier

Molecules exist to be *referenced*: an explication (or another molecule's
grounding note) that references `{urn:molecule-v0:hand|hand} [m]` brings
manual-action vocabulary (pick/hold/grab/throw/catch/pull/push/wave/clap/
point/carry/drop/shake/hit…) into profile-1 reach in a few clauses each.
The measurement makes this concrete: 16.6 points of content mass are covered
by the 54 records directly; a further **12.9 points** become explicable only
because the molecules now exist. That transitive class uses exactly the
closure the original m0b `explicable` class already used (explicables may
reference other explicables), so the two numbers are commensurable.

The borderline sub-band (1.5 points — bite without teeth [m], stand without
legs [m], paper/sand/air materials, story-kinds monster/dragon…) is reported
separately and never merged into the clear class.

## 3. What the gist leaves to judgement — and how v0 exercised it

- **The function-word allolex table.** Rule 3 admits prime exponents
  "including its closed function-word allolexes", pinned by a profile bundle
  that does not exist yet. v0 pins its own closed table in `validate.mjs`
  (articles, case/infinitive particles, pronominal allolexes it/they/them,
  NOT-fusions nothing/no, NSM-canonical toward/about, enumerated
  inflections). This is the single largest judgement in the corpus; any
  change is a corpus version change.
- **Molecule necessity.** Rule 6 is quoted here because it is the honesty
  clause of the whole tier: *"There is deliberately **no mechanical
  decomposability test** for whether a molecule is necessary — none exists
  even inside NSM scholarship … admission is a governance judgement, and the
  rules above bound its blast radius rather than pretend to adjudicate it."*
  Accordingly: **molecule admission is endorsement, not proof.** These 54
  records pass every mechanical gate; no federation, no NSM practitioner,
  no second annotator has endorsed them. Every record says so
  (`researchGrade: true` + per-record `notes` stating known weaknesses).
- **Note adequacy.** Grounding notes are display-anchored recognition text,
  not proven definitions (Lemanek's charge that molecules conceal complexity
  stands; the gist cites it). Where a note is coarse the record's notes
  field says how (e.g. run/walk without legs [m]; dog's bark as
  "does something, people can hear this from far").
- **Rule 2 (partial explications)** is deferred in v0 — records carry
  `axioms: []`, `partialExplication: null`. Honest reading: v0 satisfies
  "as much partial explication as the concept bears" with "none yet",
  because the AST cannot represent molecule records at all (next section).

## 4. Schema gap and the minimal extension (specced, NOT implemented)

Checked: `encoder/src/ast.ts` (kot-ast/1) covers exactly the explication
tree and **has no semanticStatus/molecule field** — its header scopes the
wider definition record (axioms, semantic status) out of the encoder by
design. The kernel-v0 record shape (`{id, label, status, gloss, …,
explication}`) likewise has no molecule fields; molecules-v0 therefore uses
its own record shape (`kot-molecule/0`, see data/molecules-v0/README.md)
and touches neither `kot-ast/1` nor kernel-v0.

Minimal extension for molecule-aware corpora (follow-up bead, encoder
version change — do NOT do this casually):

1. **Corpus record**: add optional `semanticStatus:
   "Explicated" | "Molecule" | "AxiomsOnly"` (default "Explicated" for
   kernel-v0 back-compat), and for molecules `groundingNote`,
   `groundingRefs`, `moleculeDepth` as in kot-molecule/0; `explication`
   becomes optional-when-Molecule (partial explications, rule 2).
2. **AST/encoder**: `ConceptRef.id` today binds "that concept's canonical
   vector" — molecules have no explication, hence no derived vector. Before
   any explication may reference `urn:molecule-v0:*`, the encoder needs a
   pinned molecule-vector derivation (natural candidate: codebook-style
   seeded row over SHA-256 of the NFC grounding-note bytes, making the
   vector move iff the note moves). That changes the content-hash inputs ⇒
   ALGORITHM_VERSION bump, X0 golden regeneration, Phase-X re-run.
3. **Mapper**: adding the 54 labels + 10 synonym surfaces is
   collision-free (measured: 12 → 12 ambiguous surfaces). Integration is a
   coordinator decision (bead), because it changes M-series baselines and
   needs an M0a-style precision pass for the new sense-caveat surfaces
   (close/light/cold/run noted per-record).

## 5. Limits of the measurement

Same basis as M0b and stated the same way: TinyStories is the deliberately
favourable ~1.5k-lemma domain; top-500 lemmas only (80.35% of content mass;
the unclassified tail is concrete/named and would dilute); single-annotator
agent classification with criteria in `classify-molecules-v0.py`; ceilings
are *expressibility* bounds for authoring, not mapper coverage — nothing
here claims the mapper now maps 40% of tokens. On open-domain text the
molecule tier will need to be 10–100× larger (Goddard's ~180 productive
molecules for English is the floor, not the ceiling) — the still-gated
remainder here (2.1 points spread over ~33 kinds) already shows the
frequency curve going flat.
