# Math sector — profile-M design record + v0 corpus

**Status:** design record, 2026-07-07. Deliverable of bead `kernel-of-truth-6ak`.
**Author:** math-sector agent (Claude Fable 5), for @jeswr.
**Scope:** a content-addressed concept profile for foundational mathematics ("profile-M"), per the mandate's explicit note that the maintainer is "not locked into NSM: other concept bases are admissible where needed (foundational mathematics, physical units)" (notes/mandate.md). Companions: concept-hash-design.md (the gist; profile-1 and the hashing machinery), docs/architecture.md §1 (construction B), reports/deterministic-concept-vectors.md §7.
**Honesty contract:** claims tagged **[established]** / **[claimed]** / **[open]**. This profile is minted permissionlessly per gist §8 — it is a *new content-addressed bundle*, not an amendment to profile-1; adoption is a separate endorsement act nobody has performed.

---

## 0. Summary of decisions

1. **Basis: many-sorted first-order logic over a Peano core with Set/Pair sort formers** (a two-sorted-PA-style fragment), in the Metamath/MM0 tiny-kernel spirit — *not* ZFC, *not* CIC. Reasons in §2.4; both rivals recorded as competing-profile possibilities per the gist's governance model (§8: profile minting is permissionless).
2. **Binding: canonical de Bruijn form is the only legal authored form.** Names never enter records; alpha-equivalence becomes syntactic identity by construction (§3.4). Vacuous binders are rejected at the gate.
3. **The concept-hash machinery (gist §6) applies unchanged** — it is grammar-agnostic given a closed, capped, tree-shaped record format, which profile-M provides (§3.5).
4. **Construction B generalises by codebook swap + valency-table swap** (§4); the encoder variant is specified here and deliberately **not built** (filed follow-up).
5. **v0 corpus: 39 records** in `data/math-v0/` (Peano core, order, divisibility, sets/pairs/functions over N, integers-as-equivalence-classes sketch), validated by a self-contained checker (`data/math-v0/validate.mjs`). Research-grade, agent-authored, not endorsed, no proof layer.
6. **NSM bridges recorded per concept**: a prime bridge where a prime honestly exists (ONE, TWO; THE-SAME flagged approximate), a research-grade profile-1 explication attempt for `addition` and `empty-set-nat` (both KNOWN-WEAK), `{"kind":"none"}` with a stated reason everywhere else.

---

## 1. Grounding survey

### 1.1 Metamath / set.mm — the closest thing to content-addressable math that exists

Metamath's kernel is a single inference rule — direct substitution into schemes — with all syntax and axioms supplied as data; set.mm carries ~40k+ theorems of ZFC over that kernel, and the format is stable enough that **over a dozen independently written verifiers** check the same database (metamath.org; github.com/metamath/set.mm) [established]. Statements are canonical, context-free token strings: a goal plus the list of prior statements completely determines verifier state (Polu & Sutskever, arXiv:2009.03393, use exactly this property) [established].

**How close to content-addressable?** Closest of anything surveyed, but not there:

- *For* — statements are already canonical symbol sequences with no elaboration layer, no inferred implicit structure, and linear-time checkable well-formedness. Hashing a statement's token string is almost meaningful as-is.
- *Against* — (a) identity is by **mutable label** (`$a`/`$p` names), and labels are load-bearing: proofs reference prior statements by label, and set.mm relabels in place across releases — exactly the OBO-style meaning-under-a-mutable-name pattern the gist's §1 exists to remove; (b) statement strings contain **metavariable names** (`x`, `ph`, …) plus distinct-variable side conditions, so statement identity is really identity *modulo metavariable renaming* — an alpha-equivalence problem at the schema level; (c) definitions are axioms guarded by convention (a definitional-soundness checker exists as tooling, not kernel).

**Metamath Zero (MM0)** (Carneiro, arXiv:1910.10703; github.com/digama0/mm0) sharpens the same virtues: multi-sorted FOL, a binary proof format, essentially-linear verification, and a verified-verifier bootstrap down to x86 semantics [established]. MM0 is the closest *in spirit* to this suite's discipline (tiny trusted core, canonical byte formats, fail-closed gates), and profile-M's basis choice (§2.4) is Metamath/MM0-shaped, not Lean-shaped.

### 1.2 Lean 4 / Mathlib — the richest substrate, the wrong identity discipline

Mathlib is the largest maintained formal library: >1M lines spanning algebra through analysis (github.com/leanprover-community/mathlib4; lean-lang.org/use-cases/mathlib) [established]. Its kernel is a comparatively small trusted C++ core with independent re-checkers (lean4checker; Lean4Lean, arXiv:2403.14064) [established]. But as a *content-addressed definitional substrate* it fails on three counts [claimed, from the cited system properties]:

1. **Identity is modulo definitional equality.** Two byte-different CIC terms can be kernel-equal (beta/delta/iota/zeta reduction, proof irrelevance, universe lifting); byte-hashing mints different ids for what Lean treats as the same definition, and canonicalising modulo defeq means *running the kernel inside the mint gate* — the trusted base the gist's SHACL-shaped gates deliberately avoid.
2. **Elaboration hides structure.** Source definitions omit implicit arguments, instances and universe parameters that the elaborator infers; the "definition" a human audits and the term the kernel sees are far apart. Profile-1's virtue — the authored record *is* the hashed record — is lost.
3. **Names and refactors churn.** Mathlib deprecates and renames continuously; identity rides on a mutable global namespace.

Mathlib's right role in this programme is as a **bridge target**: `sameConceptAs`-style signed annotations from profile-M hashes to Mathlib names (e.g. via MathGloss's Lean links, §1.4), never as the identity layer.

### 1.3 OpenMath content dictionaries — the right record shape, the wrong governance

OpenMath CDs define symbols with informal (CMP) and formal (FMP) mathematical properties plus examples — e.g. `arith1` pins commutativity of `plus` as an FMP (openmath.org/cd/arith1; OpenMath 2.0 standard, 2004) [established]. That is structurally a concept record: symbol + typed formal characterisation + prose gloss. Two disqualifiers as substrate: the semantics is deliberately weak — a two-level scheme where expression trees get only "very weak algebraic semantics" extended by CD properties (Kohlhase & Rabe, *Math. in CS* 2012) [established]; and CDs are owned, versioned, editable documents of the OpenMath Society — the mutable-owner model, again. Profile-M borrows the record shape (our `AxiomDef` records are FMPs made hashable) and drops the governance.

### 1.4 MathGloss — annotation layer, not substrate

MathGloss (Horowitz & de Paiva, arXiv:2311.12649) links ~700 undergraduate concepts across Wikidata, the Chicago curriculum, the French curriculum's Lean 4 links, MuLiMa and nLab [established]. It is a *petname/crosswalk* artifact: exactly what the gist calls the annotation layer (labels, translations, legacy bridges), useful for the phrase→concept mapper and for bridge annotations. It contains no formal definitions and cannot ground identity.

**Survey verdict [claimed]:** the cleanest definitional substrate for content-addressed math concepts is *Metamath/MM0-style canonical statements over a tiny multi-sorted FOL kernel*, reduced to a closed, capped profile; Lean/Mathlib and OpenMath/MathGloss enter as bridge/annotation targets. This is what profile-M does.

### 1.5 Math-aware embeddings and number handling in LMs (survey depth)

What is known about how LMs actually represent mathematical content — the evidence any "math kernel helps LLMs" claim must survive:

- **xVal** (Golkar et al., arXiv:2310.02989): encode every number as a single `[NUM]` token whose embedding is *scaled by the numeric value*; better out-of-distribution behaviour on scientific data than digit tokenisation [established]. Note what this is: **magnitude-based**, definition-free — the exact opposite inductive bias to a definition-derived vector.
- **FoNE** (arXiv:2502.09741): precise single-token number embeddings via explicit Fourier features [established].
- **Pretrained LLMs compute addition with Fourier features** (Zhou et al., arXiv:2406.03445): MLP layers approximate magnitude with low-frequency features; attention layers do modular (parity-like) work with high-frequency features; models trained from scratch without pretrained token embeddings fail to develop the high-frequency mechanism [established]. Related: helical/trigonometric addition structure (arXiv:2502.00873); digit-wise base-10 internal representations explaining characteristic per-digit errors (arXiv:2410.11781); multi-operand addition failing for lookahead/carry reasons independent of tokenisation (arXiv:2502.19981); convergent number representations across model families (arXiv:2604.20817) [all established as reported].
- **Tokenisation matters mechanistically**: digit grouping determines whether the modular/Fourier structure can emerge at all (arXiv:2406.03445 §tokenisation; arXiv:2502.19981) [established].

**The implication, stated plainly [claimed]:** LMs do arithmetic through *learned magnitude and periodic features over digit tokens*, plus memorised procedure. Nothing in that mechanism touches Peano recursion. A frozen structure-derived vector for `addition` (a primitive-recursion tree) has no mechanistic route to making a model better at `37+58`; anyone claiming otherwise must first answer the same evidence that contradicted the maintainer's C1/C2 at architecture.md §2. What math records *can* buy is different and narrower — §5.

---

## 2. The foundation decision

### 2.1 Requirements from the machinery

Profile-M must supply what profile-1 supplies, because that is what the hash pipeline and construction B consume:

1. a **closed, typed grammar** — complete inventories, no open lexical class inside the hash;
2. **caps** making every record small and every gate linear-ish (gist §5 caps table, §6 complexity note);
3. **tree-shaped records** referencing prior concepts by id (bnode trees + `urn:concept:` refs);
4. **decidable, syntax-directed well-formedness** — a mint gate that is a checker, not a theorem prover.

### 2.2 The chosen basis [decision]

**Many-sorted FOL with equality over a Peano core, with two sort formers.**

- **Sorts:** `N` (natural number); formers `Set(σ)` and `Pair(σ,τ)`; sort-former depth ≤ 4. `Prop` is the sort of formulas only — never a binder/parameter sort (no quantification over propositions).
- **Term/formula formers (closed):** `zero`, `succ`; typed `eq`; `member`; `pair`/`fst`/`snd`; connectives `not, and, or, implies, iff`; binders `forall, exists, comprehension` ({x:σ | φ} : Set(σ)); de Bruijn `var`; `const` (application of a previously minted concept).
- **Axioms (in the profile bundle, mirrored as records):** successor non-zero + injectivity; **induction stated once via `Set(N)`** — second-order induction in its two-sorted first-order clothing; set extensionality; pair projection/eta laws.
- **Definitions:** five record frames (§3.2) — `Primitive`, `AxiomDef`, `TermDef`, `PredicateDef`, `RecursiveFunctionDef` (Gödel-style primitive recursion with guardedness by construction).

With full second-order semantics this basis is categorical for N (Dedekind) [established]; under Henkin/first-order semantics it is a conservative two-sorted PA fragment (ACA₀-flavoured) and non-standard models exist [established]. The records don't care: they are *definitions relative to a pinned basis*, and the basis is inside the profile bundle hash.

### 2.3 Why not ZFC (the set.mm choice)

Untyped `∈` over one sort forces encodings *into concept identity*: naturals become von Neumann ordinals, pairs become Kuratowski sets, and junk theorems (`2 = {∅,{∅}}`, `1 ∈ 2`) become part of what the hash fixes. The concept "two" should not have "is a set containing the empty set" inside its identity — that is encoding residue, not meaning. Typed formers keep records at concept altitude and make sort-checking a local, linear gate. Cost, stated honestly: a fixed sort algebra is *less expressive* — no transfinite material, no unbounded comprehension, schema instances must be minted per sort (§6, limitation L2). A ZFC-based profile-M′ is mintable by anyone under the gist's §8 governance; the disagreement would be adjudicated by endorsement, not by this document.

### 2.4 Why not CIC/type theory (the Lean choice)

§1.2's three failures are decision-grade: identity-modulo-defeq puts a full typechecker (conversion, reduction, universes) inside the mint gate; elaboration divorces the audited record from the hashed record; and the expressive power (dependent types, universes, typeclasses) is precisely what breaks "closed grammar + caps + linear gates". The kernel's mandate is a *small definitional core*, not a proof assistant. A CIC-based competing profile remains admissible [governance]; if the programme ever needs theorem-mass at Mathlib scale, that pressure arrives at the bridge layer first (§1.2), not the identity layer.

---

## 3. Profile-M specification (v0 sketch, normative for `data/math-v0/`)

### 3.1 Record envelope

A math concept record is a JSON document (`pm-ast/1` — the authoring mirror of an eventual RDF record form, exactly as `kot-ast/1` mirrors profile-1's RDF form):

```json
{
  "id": "urn:math-v0:<slug>",
  "label": "...", "status": "primitive|axiom|core|sketch",
  "gloss": "...", "notes": "...",
  "references": ["urn:math-v0:..."],
  "nsmBridge": { "kind": "prime" | "explication" | "none", ... },
  "definition": { "schema": "pm-ast/1", "frame": "...", ... }
}
```

`id`s are **placeholder URNs** exactly as in kernel-v0 — real minting is the concept-hash pipeline's job. `label`, `gloss`, `notes` and `nsmBridge` are **annotation-layer** content (outside a future hash boundary); `definition` (+ `frame`) is the hash-boundary content.

### 3.2 Frames

| Frame | Fields | Typing obligation (gate-checked) |
|---|---|---|
| `Primitive` | `primitive` (name from the closed basis table) | must byte-match the bundle's basis table — the exact analogue of profile-1 prime records pinned to the lexicon (`ERR_PRIME_LEXICON_MISMATCH` ↔ `ERR_PRIMITIVE_UNKNOWN`) |
| `AxiomDef` | `statement`; record-level `characterizes` list | `statement` is a *closed* term of sort `Prop` |
| `TermDef` | `params: [sort…]`, `resultSort`, `definiens` | `definiens : resultSort` in the parameter context |
| `PredicateDef` | `params` (≥1), `definiens` | `definiens : Prop` in the parameter context |
| `RecursiveFunctionDef` | `params` (last must be `N`), `resultSort`, `baseCase`, `stepCase` | primitive recursion on the last argument: `baseCase : resultSort` in context `params[0..k-2]`; `stepCase : resultSort` in that context extended by `n : N` (the predecessor) and `rec : resultSort` (the recursive value). Termination/guardedness holds **by construction** — there is no self-application node at all |
| (profile-1's `InstanceSchema`/`WhenTrue`/`RelationalSchema`) | — | replaced wholesale; math definitions are equations/formulas, not discourse schemas |

### 3.3 Caps (profile-M v0; conformance-defining, mirroring gist §5)

| Constant | Value |
|---|---|
| Term nodes per definition | ≤ 256 |
| Binder depth (params + quantifiers + comprehensions) | ≤ 12 |
| Parameters per definition | ≤ 6 |
| Sort-former depth | ≤ 4 |
| Concept references per record | ≤ 16 |
| Reference graph | DAG only in v0 (no SCCs; mutual recursion deferred — the gist's §6 cycle machinery would apply if admitted) |
| Vacuous binders | rejected (`ERR_VACUOUS_BINDER`) |

### 3.4 Binding and alpha-equivalence — what breaks, and the canonicalisation

**This is the one place profile-M is genuinely harder than profile-1.** Profile-1 has no bound variables: its referents are flat, DRT-style indexed declarations with a single introducing occurrence (gist §4.2), deliberately reconciled with the bnode-tree rule by using literal indices. Mathematics has real binders (`∀`, `∃`, comprehension), and alpha-equivalent authored forms (`∀x.x=x` vs `∀y.y=y`) must not mint different hashes — otherwise fixity of reference is broken at the first quantifier.

**Decision: the canonical form is nameless.** `pm-ast/1` has no variable names anywhere — a variable occurrence is `{"kind":"var","index":k}` with **0-based de Bruijn indices, 0 = innermost binder**; parameters are outermost binders (pushed left-to-right, so the last parameter is index 0 in a binder-free body). Alpha-equivalence is thereby *syntactic identity by construction* [established — standard de Bruijn property]. Human-facing named forms are renderer/authoring-tool business, i.e. annotations; a named→de-Bruijn canonicaliser is a filed follow-up, and until it exists authors write indices by hand (the v0 corpus does).

Two subtleties, recorded honestly:

1. **Vacuous binders** (`∀x. φ` with `x` not free in `φ`) are logically redundant but syntactically distinct de Bruijn terms; left legal they'd be a free hash-splitting surface. Rejected at the gate — cheap, deterministic, semantically costless (mirrors the gist's duplicate-FDH move in spirit: reject the degenerate case rather than canonicalise it).
2. **De Bruijn indices are context-dependent**, so *sub*term sharing across records is not stable under this canonical form (the same mathematical subexpression carries different indices in different binding contexts). For record-level identity — our only requirement — this is irrelevant. For future term-level deduplication/e-graph work it is exactly the problem "Hashing modulo alpha-equivalence" solves (Maziarz, Ellis, Lawrence, Fitzgibbon, Peyton Jones, PLDI 2021, arXiv:2105.02856 — O(n log²n), holes-and-binder-maps instead of de Bruijn; see also context-sensitive variant, arXiv:2401.02948) [established prior art]. Deliberately not adopted for v0: whole-record hashing doesn't need it.

**What is deliberately NOT canonicalised:** logical equivalence. `and(a,b)` vs `and(b,a)`, `¬¬φ` vs `φ`, `≤` defined via `∃k. x+k=y` vs via `<` — all mint distinct ids. Identity is the stated form, exactly as gist §13 Q1 decides for profile-1 (entailment-normalisation is undecidable; even commutativity-normalisation starts an unwinnable "how much semantics" negotiation). Rival formulations coexist; endorsed `sameConceptAs` annotations mediate [decision recorded].

### 3.5 How the concept-hash machinery applies (unchanged)

Gist §6 consumes: extracted records that are bnode *trees* under a closed shape with a literal whitelist, references as `urn:concept:` URNs, caps, then NFC → Tarjan SCC → RDFC-1.0 → profile-header-prefixed digest → multihash/multibase. Nothing in that pipeline knows it is hashing NSM explications [established — by inspection of §6, every step is shape-generic]. Profile-M plugs in by supplying:

- an RDF record form for `pm-ast/1` (formers as profile IRIs, argument order via RDF lists, literals whitelist = de Bruijn indices + primitive names + sort atoms — the direct analogue of profile-1's refIndex/exponent whitelist);
- a **profile-M bundle**: grammar tables (§3.2–§3.3), the basis table (primitives + axiom statements), caps, SHACL shape + sort-checker spec — content-addressed, immutable, with its own header string (e.g. `urn:concept-def:M1` defined as an alias for the bundle hash, per gist §8's frozen-bundle rule). The in-band header guarantees a profile-M payload can never verify as profile-1 or vice versa (gist §6 step 5).

Per gist §8, minting this profile requires nobody's permission; *adoption* is federation endorsement; profile-1 and profile-M records reference each other freely by URN (a math concept may appear inside a profile-1 axiom position and vice versa — cross-profile reference is just a URN reference; [open] whether endorsement checklists want to gate on cross-profile closure).

---

## 4. Encoder variant: construction B-M (specified, not built)

Architecture.md §1 note holds: construction B is grammar-agnostic in principle — orthonormal atoms + typed binding works over any closed typed grammar. The swap:

- **Atom codebook:** replace {65 primes + roles + operators + frame/referent atoms} with: node-kind atoms (~17: the formers of §2.2), primitive atoms (zero, succ, eq, member, pair, fst, snd), sort atoms (N, Set, Pair, composed structurally like any other subtree), frame atoms (5), de Bruijn index atoms `var-0 … var-11` (12, = binder-depth cap). Total **≈ 50–80 exactly-orthonormal atoms** — comfortably under profile-1's ~200, so the D ≈ 8k–32k capacity arithmetic of reports/deterministic-concept-vectors.md §7.2 carries over with slack [established math, claimed transfer].
- **Valency tables:** each former's typed argument list plays the role of §4.4's predicate frames; argument position uses the same position-permutation mechanism as clause position in construction B. Hadamard/DFT codebook, exact within-node TPR, unitary circular-convolution across depth — all unchanged.
- **References:** `const` nodes bind the referenced concept's own canonical vector (compositionality by construction, unchanged); the corpus DAG is the cleanup lexicon, unchanged.
- **Versioning:** a new codebook is an encoder version change by definition — new ALGORITHM_VERSION, new content-hash, fresh X0 goldens, full Phase-X re-run on the math corpus (CLAUDE.md conventions apply verbatim).

**Encoding precondition:** records reach the encoder only *after* de Bruijn canonicalisation + vacuous-binder rejection (§3.4) — encoding a named form would make alpha-variants encode differently, silently breaking "same concept ⇒ same vector".

**New pathologies (the honest list) [claimed, pending measurement]:**

1. **Quantifier/connective flips are single-atom edits.** `∀↔∃`, `and↔or`, `≤↔<` (one `succ` node), `n↔n+1` — mathematical meaning is *maximally* brittle under exactly the small-structural-edit regime where construction B's similarity is *maximally* smooth. This is profile-1's NOT-pathology (architecture §1.2 weakness 1) in a strictly worse form, because in math nearly every meaningful error is a polarity-class edit. An X1-style adversarial single-edit margin suite on the math corpus is a precondition for any downstream use of math-kernel similarity; raw cosine similarity stays banned (panel O9 discipline carries over).
2. **Unary numerals burn depth.** `v(three)` already sits atop a 3-deep reference/succ chain; `v(seventeen)` would be architecture-hostile and the structure budget (s ≈ 100–200 bound terms) makes large literals impossible *by design*. Positional-numeral definitions (digits as records, a base-10 construction) are definitional work not attempted in v0. Interplay with §1.5 is the interesting research surface: the LM side already owns magnitude geometry (Fourier/helix); the kernel side owns definitional structure; they will not align by accident [open].
3. **Binder-depth atoms enter the code.** Two occurrences of "the same" variable at different depths are different atoms (`var-0` vs `var-2`); structural similarity across records with different binder nesting is correspondingly noisier than profile-1's flat referent indices. Quantified impact unknown; measured in the (future) X-suite variant [open].

---

## 5. What math concepts buy the LLM-kernel story — and what they don't

**Buys:**

1. **Adequacy becomes checkable — the single biggest epistemic win.** Profile-1's honest caveat is that explication adequacy is "social, not proven" (gist §1 claim 3); NSM's own acceptance test is analyst-dependent (Riemer 2006). A profile-M record has a *correctness fact*: `less-or-equal := ∃k. x+k=y` is provably right relative to the pinned basis. The kernel's weakest epistemic layer simply does not exist in this sector [established, with the caveat that *which* formulation to prefer among provably-equivalent ones remains a social choice — §3.4].
2. **Natural E-series extensions.** Math records give the probe suite what it lacks: tasks with machine-checkable ground truth. Concrete candidates (probe design filed as a bead, not designed here): E1/E4-style frozen-row runs where the concept set is {zero…three, addition, less-than, even, odd, prime-number} over arithmetic word-problem corpora; definitional-distinction probes (does a kernel-carrying model separate "at least" from "more than" — `le` vs `lt`, a one-atom kernel distinction — better than the shuffled-kernel control?); E4 emission with math glosses. The shuffled-kernel control discipline (architecture §4 A1) carries over unchanged.
3. **Language-independence, for real.** Profile-1's ground layer is English-anchored with NSM's universality claim doing load-bearing work (gist §3.1); Peano arithmetic has no Bohnemeyer problem. The cross-linguistic story is strongest exactly here [established].
4. **World-layer synergy.** Facts about numbers are theorems; the mandate's "assume world-layer facts are true" deferral is *dischargeable in principle* for this sector via a future proof layer (§6 L1) [open].

**Doesn't buy:**

1. **The formal-definition ≠ usage gap, in its sharpest form.** §1.5's evidence: LMs compute arithmetic via magnitude/periodic features over digit tokens and pattern-matched procedure — a mechanism with no route to a primrec tree. Frozen `v(addition)` will not improve calculation; the E-series math probes must target *definitional/relational* behaviour, not arithmetic throughput, or they test a strawman [established evidence, claimed consequence].
2. **Token-mass coverage.** Formal-math vocabulary is rare in natural text; the numerals that *are* frequent are what profile-M v0 handles worst (unary towers, §4.2). An M0-style coverage measurement would be honest to run before any claim; expectation: negligible mass [open, expectation stated].
3. **The mapper gets harder.** "prime", "even", "odd", "function", "integer" are aggressively polysemous; mapping them to math-sector concepts *without* wrecking ordinary-language precision is strictly harder than the bookmarks/kinship vocabulary of kernel-v0 [claimed].
4. **No proof layer in v0** — records are definitions and axioms; `2+2=4` is *not in the kernel* (it is a theorem of the basis, and v0 has no theorem records). Saying otherwise would be the exact overclaim this programme exists to avoid.

**Tokeniser interplay, one honest paragraph.** xVal/FoNE demonstrate that the *right* number representation for LM numeracy is magnitude/Fourier-structured, learned or engineered at the token layer [established]. The kernel's numeral vectors are depth/structure-derived. These are different objects serving different masters: one makes 37+58 work, the other makes "what `two` *is*" fixed, auditable and drift-free. A hybrid — kernel identity for number-*concepts*, xVal-style value channels for number-*tokens*, bridged at the mapper — is the plausible architecture, and it is exactly the kind of precise mechanism the mandate asks the programme to translate loose ideas into [open, filed with the probe-design bead].

---

## 6. The v0 corpus (`data/math-v0/`)

**39 records, research-grade, agent-authored, NOT endorsed, adequacy-of-formulation unreviewed** (the *correctness* obligations are machine-checked by the validator; *choice-of-formulation* is not — §3.4). Composition:

- **9 `Primitive`**: natural-number, zero, successor, equality, set-membership, ordered-pair, pair-first, pair-second, set-of.
- **6 `AxiomDef`**: succ-nonzero, succ-injective, induction (via `Set(N)`), set-extensionality-at-N, pair-projections-at-N, pair-eta-at-N.
- **3 numerals** (`TermDef`): one, two, three (reference chain three→two→one exercises reference binding).
- **3 `RecursiveFunctionDef`**: predecessor, addition, multiplication.
- **6 order/divisibility `PredicateDef`**: less-or-equal, less-than, divides, even, odd, prime-number (deepest reference chain: odd → even → divides → multiplication → addition, depth 4).
- **5 sets-over-N**: empty-set-nat, singleton-nat, subset-nat, union-nat, intersection-nat.
- **2 functions-as-graphs**: function-on-nat, injective-on-nat.
- **5 integers sketch**: int-pair-equiv ((a,b)~(c,d) ⇔ a+d=c+b), integer (S is an equivalence class of ~), integer-zero, integer-one, integer-negation — the classic quotient construction *without* quotient sorts: classes as `Set(Pair(N,N))` values, class-hood as a predicate. What it demonstrates: the construction is expressible; what it exposes: no new sort is minted (an "integer" is forever a `Set(Pair(N,N))` here), and integer addition needs image-sets v0 cannot form cleanly — recorded as limitation L3, not papered over.

**NSM bridges:** `one`→prime ONE, `two`→prime TWO [the mandate's existence proof]; `equality`→THE-SAME flagged *approximate* (a determiner prime is not a typed identity relation); `addition` and `empty-set-nat` carry research-grade profile-1 explication attempts, both KNOWN-WEAK and both **validated against the actual profile-1 encoder gates** by the corpus validator (so "profile-1-legal" is machine-checked, while their adequacy emphatically is not — the addition gloss captures aggregation-of-collections, not additive structure; the empty-set gloss conflates spatial containment with membership; both say so in their notes). All 34 remaining records carry `nsmBridge: {"kind":"none"}` with a per-record stated reason. Bridge policy honesty: the near-total `none` rate *is* the finding — foundational mathematics is exactly where the mandate predicted NSM would not reach.

**Validation** (`data/math-v0/validate.mjs`, self-contained, no dependencies): closed-inventory grammar check; full sort checker (bidirectional, per §3.2 typing obligations); de Bruijn scope + vacuous-binder gates; caps; reference recomputation-vs-declaration, resolution and DAG check; NSM-bridge checks (prime names against the 65-prime lexicon; explication bridges pushed through `encoder/dist`'s `validateExplication` when built, warn-and-skip otherwise); manifest cross-checks. Exit 0 iff all 39 records pass everything. **Vector encoding is explicitly NOT done here** — construction B-M is a filed follow-up; running the profile-1 encoder over pm-ast records would be a category error.

**Known limitations (recorded, not hidden):**

- **L1 — no proofs.** Definitional records only; theoremhood (even `integer(integer-zero)`) is unexpressed. A proof-carrying record frame (Metamath-style, referencing axiom records) is future work, unpromised.
- **L2 — no schemas.** Extensionality/pair axioms are stated at fixed sorts (`N`, `Pair(N,N)`); sort-schematic axioms need a schema mechanism v0 lacks (each instance minted separately — tolerable at v0 scale, ugly at scale).
- **L3 — no quotients, no images.** §6 integers paragraph above; integer arithmetic blocked on set-image formers.
- **L4 — empty-set's `⊥` is encoded as `¬(x=x)`** — the grammar has no falsum constant; noted in-record.
- **L5 — indices are hand-authored.** Until the de Bruijn canonicaliser follow-up lands, authoring is error-prone; the sort/scope gates catch most but not all slips (they cannot catch a *well-typed wrong* index choice).

---

## 7. Follow-ups filed (beads)

1. **Profile-M encoder variant (construction B-M)** — build per §4: codebook + valency tables + canonicalisation precondition + ALGORITHM_VERSION discipline + math-corpus X0/X1 (single-edit margins over quantifier/connective flips).
2. **De Bruijn canonicaliser + named authoring surface** — named-form → canonical nameless form, vacuous-binder rejection, round-trip renderer; Maziarz-style subterm hashing only if term-level dedup becomes a requirement.
3. **Math probe design for the E-series** — definitional-distinction probes (le/lt), arithmetic word-problem frozen-row arms with shuffled-kernel controls, kernel-numeral vs xVal-style value-channel interplay; pre-registered before any GPU spend.

---

*Primary sources: metamath.org + github.com/metamath/set.mm; Carneiro arXiv:1910.10703 (MM0); github.com/leanprover-community/mathlib4 + lean-lang.org (Mathlib, lean4checker) + arXiv:2403.14064 (Lean4Lean); openmath.org/cd/arith1 + OpenMath 2.0 (2004) + Kohlhase & Rabe, Math. in CS 2012; arXiv:2311.12649 (MathGloss); arXiv:2310.02989 (xVal); arXiv:2502.09741 (FoNE); arXiv:2406.03445 (Fourier features for addition); arXiv:2502.00873; arXiv:2410.11781; arXiv:2502.19981; arXiv:2604.20817; arXiv:2105.02856 (hashing modulo alpha, PLDI 2021) + arXiv:2401.02948; arXiv:2009.03393. Local: concept-hash-design.md §3–§8, docs/architecture.md §1–§2, reports/deterministic-concept-vectors.md §7, data/kernel-v0/.*
