# EXPR-1 — Expressivity Analysis: the Semantic-Web Stack, Its Boundaries, and a Layered Stance for the Kernel + World-Model + Rules-Engine

**Status: PROVISIONAL first draft** (designer-1, 2026-07-11). Written in response to the
maintainer's expressivity directive (issue #20): *the design must not be restricted in
expressivity — look outside the semantic-web stack where needed, but explicitly justify why
something is not expressible with that stack whenever stepping outside.* The maintainer also
notes that only the gUFO subset of UFO is modelled in RDF, not full UFO — a datum this
analysis uses directly (§2.6). **No feasibility conclusion is stated or implied anywhere in
this document; verdicts belong to the maintainer and the review gates. All epistemic tags are
provisional.** ASM ids in the disjoint block PROPOSED-ASM-1230..1239 are EMITTED here
(Appendix A) for central registration by the coordinator; this document has no write access
to `registry/assumptions.jsonl`.

Anchors: `docs/next/arch/world-model-rules-engine.md` (WMRE-1 + GPT-5.6 fold-in; the
"Expressivity boundary and the Lean seam" section, PROPOSED-ASM-1196), `poc/rules-1/RESULT.md`
(exploratory certificate: the engine as built), `docs/next/interpretations/g2.md` (the R1/R3/R4
claim families), maintainer threads #19 (Lean/mathematics) and #20 (this directive).

---

## 0. The one distinction everything below depends on

"Not expressible with the semantic-web stack" is three different claims, and the maintainer's
justification requirement is only dischargeable if every gap statement says WHICH one it is:

- **Axis 1 — not STATABLE.** No OWL 2 DL / RDF / N3 encoding of the proposition exists at all
  (e.g. an induction schema, a propositional-attitude operator). This is the strong claim.
- **Axis 2 — statable but not DERIVABLE in the tractable profile.** OWL 2 DL can state it and a
  tableau reasoner can conclude from it, but the rule-based profiles (OWL 2 RL, N3 Horn,
  Datalog) provably cannot, because their rule heads are assertion-only and they perform no
  case analysis. R-COVER-ELIM is the measured house example [MEASURED: sparq
  `inference-conformance-report.md` PR1 divergences; CV-8 in the WMRE-1 fold-in].
- **Axis 3 — statable but with the WRONG SEMANTICS.** The stack can write something
  syntactically adjacent, but its open-world, monotone, no-unique-names model theory makes the
  written thing mean something else (closed-world counting, defaults, negation-as-failure,
  integrity constraints).

The existing WMRE-1 regime discipline (`regime ∈ {owl-rl, horn-def, policy}` on every rule and
proof node, PROPOSED-ASM-1162) is the axis-2/axis-3 machinery already in place: the *policy*
regime is precisely "we pre-compiled an axis-2 case elimination into a Horn rule whose
extra-logical premises (covering, UNA) are named ASMs". This analysis extends that discipline
into a general gap taxonomy (§4.1) rather than inventing a new one.

---

## 1. What the semantic-web stack CAN and CANNOT express

### 1.1 The layers and what each buys

| Layer | Expressive content | Reasoning cost | In-estate status |
|---|---|---|---|
| RDF | Ground **binary** atoms (triples); blank nodes = existential variables in data | — | native (`urn:kot:` IRIs) |
| RDFS | subClassOf / subPropertyOf hierarchies, domain/range typing | PTIME, trivial rules | sparq-reason, conformance-tested |
| OWL 2 DL (SROIQ(D)) | Boolean class constructors incl. **classical negation and disjunction**, existential/universal restrictions, qualified cardinality, inverse/functional/(ir)reflexive/disjoint roles, **regular** property chains, nominals, datatypes with facets | N2EXPTIME-complete worst case [LIT-BACKED: Horrocks/Kutz/Sattler 2006; Kazakov 2008]; practical via tableau/hypertableau (HermiT, Openllet) | NOT in estate; no Rust-class engine |
| OWL 2 RL | The rule-implementable subset: assertion-only heads, no disjunction elimination, no existential-head individual invention | PTIME, forward rules | **primary** (sparq-reason OwlRl; twin) |
| OWL 2 EL | Existentials + chains, no inverse/universal/cardinality; classifies SNOMED-scale | PTIME (ELK) | not needed yet; RO shard appears RL-compatible by kind (profile-validation pending, §4.3) |
| OWL 2 QL | Query-rewriting fragment | AC⁰ data complexity | not needed |
| SPARQL 1.1 | **Queries**: arbitrary graph patterns (full FO-query power over the data), aggregation (COUNT/SUM/AVG), arithmetic in FILTER/BIND, property paths, **negation-as-failure** (NOT EXISTS / MINUS) | PSPACE-complete eval; but it is a query language — closed-world at query time, no entailment | sparq (query side) |
| SHACL (+AF) | **Closed-world integrity constraints** over shapes; SHACL-AF adds rules | validation, not entailment | adopted as separate artifact per ASM-1162 rider (i) |
| N3 | Horn rules over triples with **cyclic rule graphs** (beyond OWL's regularity restriction), builtins (math:, string:, list:), graph quoting, **scoped NAF** (`log:notIncludes`) | terminating only if the ruleset is safe; undecidable in general | sparq-reason `reason_n3`, the RULES-1 `rules.n3` carrier |
| SWRL (DL-safe) | Horn rules over OWL atoms, builtins; monotone, no NAF, no head disjunction | decidable only DL-safe [LIT-BACKED: Motik et al. 2005] | subsumed by N3 here |

### 1.2 What the stack, taken as a whole, CANNOT do

Each row states the gap, the axis, and the one-line justification the maintainer's directive
requires. These are properties of the formalisms, not of our engine [LIT-BACKED throughout:
W3C OWL 2 Profiles; OWL 2 Direct Semantics; N3 CG spec 2023; standard DL literature].

| # | Gap | Axis | Why the stack cannot do it (the justification) |
|---|---|---|---|
| G1 | **Full first-order quantification** (arbitrary ∀/∃ alternation over ≥3 variables; non-tree-shaped axioms) | 1 | OWL 2 DL is (approximately) the two-variable + counting + regular-role fragment of FOL, chosen to keep satisfiability decidable; an axiom whose variable graph is not tree-shaped (beyond what regular role chains linearise) has no SROIQ encoding. |
| G2 | **Case elimination / reasoning by disjunction** in the RULE profiles (our R-COVER-ELIM) | 2 | OWL 2 RL rule heads assert single atoms; the profile is documented incomplete for entailments that require splitting on `A ⊔ B` — the covering+functional+differentFrom→father inference is *statable* in OWL 2 DL and derivable by tableau, but no RL/N3/Datalog engine can perform the split [MEASURED: sparq conformance PR1; reproduced independently by GPT-5.6, CV-8]. |
| G3 | **Negation-as-failure / closed-world defaults** as entailment ("not known to be X", "birds fly unless...") | 3 | OWL model theory is open-world and monotone: absence of a triple is not evidence, and no OWL axiom can conclude from absence; SPARQL/N3 NAF exists but is non-monotonic and sits *outside* the OWL entailment relation (query/scoped semantics, not ontology semantics). |
| G4 | **Unique names** | 3 | OWL makes no unique-name assumption; distinctness must be asserted pairwise (`owl:differentFrom`, quadratic) or via `owl:AllDifferent` — which is why UNA is a named, item-scoped stipulation here (ASM-1120), not a free ambient fact. |
| G5 | **Arithmetic over values; comparisons between derived quantities** ("BMI = kg/m²", "more children than siblings") | 1 (OWL) / 3 (N3, SPARQL) | OWL datatypes admit only facet restrictions on single values — there is no term algebra, no function symbols, no cross-value computation; N3 `math:` builtins and SPARQL BIND compute, but procedurally, outside the model theory, with no completeness story. |
| G6 | **Counting/aggregation as a class definition** ("family with exactly 3 recorded children" as derived from data) | 3 | OWL qualified cardinality constrains *models*, it does not count *data*: open-world semantics means unstated children may exist, so no OWL axiom can conclude "exactly 3" from three assertions; aggregation needs CWA (SPARQL aggregates, ASP `#count`) — query semantics, not entailment. |
| G7 | **n-ary relations and events** ("x gave y to z at t") | 1 | The RDF data model is binary; n-ary facts require reification patterns, and OWL axioms cannot then quantify smoothly across a reified event's participant slots (role chains do not traverse reification shapes in general). |
| G8 | **Function symbols / terms** (f(x) inside axioms; term rewriting) | 1 | OWL/N3 have no term constructors; skolem functions appear only implicitly via existentials, which the RL profile refuses to instantiate (no individual invention — ASM-1162 rider ii). |
| G9 | **Higher-order statements** ("every relation with property P is transitive"; axiom schemas) | 1 | OWL 2 punning is syntactic only; the direct semantics never quantifies over classes or properties, so schema-level generalisations must be expanded per instance by a compiler, not stated once. |
| G10 | **Temporal and modal operators** (before/after as operators, "necessarily", "believes/wants/knows that φ") | 1 | OWL/RDF have no modalities and no propositional arguments; time must be reified (4D fluents [LIT-BACKED: Welty & Fikes 2006]) at combinatorial cost, and interval-algebra composition (Allen) has disjunctive entries — outside Horn (compounds with G2). |
| G11 | **Induction, recursion beyond transitive closure, mathematics** | 1 | Transitive/chain closure is the *only* fixed point OWL offers; an induction schema is second-order (or an infinite FO axiom family), and arithmetic with induction is not merely outside OWL but outside every complete decidable logic (Gödel) — this is the maintainer's #19 mathematics case, permanently un-encodable in this stack. |
| G12 | **Integrity constraints as constraints** ("every kot-world person record MUST carry a gender field") | 3 | An OWL axiom read open-world *infers* rather than *checks* (a missing field triggers inference or silence, never an error); constraint semantics needs SHACL — which the architecture already emits as a separate validation artifact, never as entailment (ASM-1162 rider i). |

### 1.3 What the stack CAN do that is easy to underestimate

For balance — the following are fully in-stack, and several were load-bearing in the RULES-1
certificate [MEASURED: `poc/rules-1/RESULT.md`, double-run sha match; the certificate rerun is
now pinned by the FROZEN `registry/experiments/rules-1.json` (frozen 2026-07-11), superseding
this document's earlier "exploratory pre-freeze" description]:

- Property hierarchies + typing: `mother ⊑ parent`, domain/range person-typing (E2) — 2,574
  entailed typing cells, none reproducible from stated bytes.
- Regular property chains: `parent ∘ parent ⊑ grandparent`, gendered via range — 858/858
  against third-party CLUTRR gold, Wilson-LB95 0.9955.
- Functionality, inverses, class disjointness with contradiction surfacing (`cax-dw` fired
  exactly as predicted under the CF-2a mutation — 858/858 flips to ERR_CONFLICT).
- **Cyclic-rule-graph kinship in N3 that OWL cannot state**: `sibling(x,y) ← parent⁻∘parent
  minus identity` and `cousin(x,y) ← parent(x,u) ∧ parent(y,v) ∧ sibling(u,v)` are diamonds,
  not chains — OWL's regularity restriction on role inclusions excludes them (axis 1 *for
  OWL*), but they are ordinary safe N3/Datalog rules, i.e. **in-stack** one layer over. Gaps
  of this shape justify moving OWL→N3, not leaving the stack.
- Defined classes at EL strength: `CatPhoto ≡ Photo ⊓ ∃depicts.Cat` (the maintainer's
  person/photo/cat leg; E4-lite).
- The OBO RO shard's `inverse_of` / `transitive_over` / `holds_over_chain` — RL-compatible
  *by axiom kind*; whether the shard as placed conforms to the OWL 2 RL profile requires an
  actual profile-validation run, since RL conformance is a matter of syntactic placement and
  global restrictions, not relation-name inspection [LIT-BACKED: W3C OWL 2 Profiles].

---

## 2. Audit of OUR concept set: where OWL/N3 suffices and where it genuinely falls short

### 2.1 Kinship vertical (RULES-1) — SUFFICIENT, with one named axis-2 patch

Everything in the frozen-inventory kinship vertical is in-stack: R-SUBP, R-DOM/R-RNG, R-INV,
R-CHAIN are OWL 2 RL; the single non-RL item, R-COVER-ELIM, is **axis 2, not axis 1** — the
covering inference is statable in OWL 2 DL (`parent ⊑ mother ⊔ father` + functional mother +
differentFrom entails father under tableau), and its non-derivability is a property of the RL
profile (assertion-only heads, no disjunction elimination) [MEASURED: sparq conformance PR1].
The standing remedy — pre-compile the case analysis into one monotone Horn *policy* rule whose
covering (ASM-1121) and UNA (ASM-1120) premises are named, registered stipulations visible in
every `why()` proof — is an **in-stack** answer at the N3 layer with the epistemics disclosed.
The alternative (adopt a full-DL tableau engine to get the inference "natively") buys nothing
we need at the cost of N2EXPTIME machinery, a Java stack, weaker proof-tree/fail-closed
discipline, and the loss of the µs-scale certificate loop. → PROPOSED-ASM-1232.

### 2.2 g2's claim families (R1 subClassOf, R3 domain/range, R4 existentials) — EXPRESSIVITY IS NOT THE BINDING CONSTRAINT

All three families are OWL-EL-grade statable: subsumptions, sortal typing, and
`⊑ ∃role.Class` existentials. What failed at proxy strength on g2 was not the ability to
*state* these claims but their ordinary-meaning **soundness** — the blind judge pair endorsed
only ~29–45 % (bracket), with the collapse concentrated in the R3 domain/range renderings
(domain 0/21 concordant-yes) [MEASURED at LLM-proxy strength: `docs/next/interpretations/g2.md`;
PROVISIONAL-ON-LLM-PROXY; human gold adjudicates]. No richer logic fixes a wrong sortal claim —
a false statement in FOL is exactly as false as in OWL. Expressivity work must therefore never
be cited as a remedy on the g2/Π line. One genuine expressivity note does attach to R4: OWL
states `person ⊑ ∃mother.person` but the RL engine rightly refuses to *use* it to mint an
anonymous mother (G8/ASM-1162 rider ii); deriving named facts from existentials is a real
axis-2 boundary we have chosen to keep closed (refusal over skolemisation). → PROPOSED-ASM-1238.

### 2.3 NSM-style explications — GENUINELY OUTSIDE (axis 1), and already handled correctly

The kernel's native formalism is NSM explication over the 65-prime lexicon. The primes include
propositional-attitude and modal/temporal/conditional operators as first-class citizens:
THINK, KNOW, WANT, FEEL, SAY (attitudes taking *propositional* arguments), IF, BECAUSE, MAYBE,
CAN, NOT, WHEN/BEFORE/AFTER, GOOD/BAD. A typical explication is a quantified, tensed,
counterfactual mini-text ("X did something; because of this, Y thinks: 'I don't want this'").
**Justification (axis 1, gaps G10 + G7 + G1):** OWL/RDF have no operators over propositions —
`wants(x, φ)` where φ is itself a quantified formula has no SROIQ encoding (DL is a fragment
of non-modal, non-intensional FOL); reifying φ as a node loses its logical structure for
inference. This is why C1 compiles *authored, endorsed constraint records* (functional,
domain/range, disjoint, subPropertyOf, coveredBy, chains) and never attempts wholesale
NL→OWL translation of explications — the architecture's existing stance (ASM-1126/CV-2) is
hereby recorded as an *expressivity* necessity, not merely a prudence choice: the full content
of an explication admits **no semantics-preserving encoding into the currently adopted
extensional entailment regimes** (its *syntax* can of course be carried as RDF data or quoted
N3 formulae, but the embedded formula's logical structure is then opaque to those regimes'
entailment); only its extensional shadow enters the entailment layer.
→ PROPOSED-ASM-1233.

### 2.4 Mathematics / the Lean cases (maintainer #19) — GENUINELY OUTSIDE (axis 1, permanent)

The estate's Lean corpora (`data/math-lean-sample/`, `data/mathlib-1000-sample/`,
`data/math-v0/`, `data/math-mm/`) contain induction proofs, dependent types, and higher-order
statements. **Justification (G11 + G9 + G5):** induction schemas are second-order; arithmetic
with induction admits no complete decidable axiomatisation (Gödel), so it is outside every OWL
profile *by mathematical necessity, not engineering choice*; and Mathlib-grade statements
quantify over types and functions (higher-order), which OWL's direct semantics never does.
The already-registered Lean seam (PROPOSED-ASM-1196: endorsed formal content compiling to a
proof-assistant backend at the same authored C1 boundary, returning regime-tagged
proof-carrying derivations) is the correct escape hatch; this analysis adds only the regime
name (`proof-assistant`) and one cheap near-term use: proving, once, inside Lean, that
R-COVER-ELIM is sound given its covering/functional/UNA premises — machine-checking the §3
soundness argument of WMRE-1. → PROPOSED-ASM-1234.

### 2.5 World-model needs on the visible horizon — MIXED, each named

- **Temporal kinship/narrative** ("who was x's spouse *before* t"; CLUTRR stories have event
  order): axis 1 (G10, G7). Binary triples cannot index a relation by time without reification,
  and Allen-composition reasoning is disjunctive (re-enters G2). In-stack mitigation exists
  (fluent reification + Horn rules over explicit time points) and should be tried first; a
  genuine interval-algebra need would justify ASP.
- **Closed-world counting** ("only child", "has exactly 3 recorded children"): axis 3 (G6, G3).
  Open-world OWL cannot conclude from absence; SPARQL aggregation answers the *query* form
  in-stack; deriving *facts* from counts needs ASP/Datalog-with-aggregates.
- **Defaults/exceptions** ("legal parent = biological parent unless adoption stated"): axis 3
  (G3). Monotone logics cannot retract; this is default logic / stable-model territory.
- **Schema-level governance** ("every axiom record must cite an endorsing explication sha"):
  axis 1 (G9) — but correctly handled *procedurally* (validators, mint pipeline), and should
  stay procedural; no logic upgrade warranted.

### 2.6 The gUFO datum (maintainer's own observation, generalised)

The maintainer notes only gUFO — the lightweight subset — of UFO is modelled in RDF. That is
not an accident of effort: full UFO is formalised in quantified **modal** logic, and its
load-bearing metaproperties are modal through and through — rigidity ("a Kind applies to its
instances in every world in which they exist"), anti-rigidity (Phases/Roles), relational
dependence [LIT-BACKED: Guizzardi 2005; gUFO spec, Almeida et al.]. **Justification (axis 1,
G10 + G9):** rigidity quantifies over possible worlds and over predicates; OWL has neither
modality nor predicate quantification, so gUFO necessarily demotes rigidity to annotation-level
discipline (naming conventions, disjointness patterns) that a reasoner cannot enforce. The
general lesson for us: when a foundational ontology's *inference-bearing* content is modal,
the RDF rendering keeps the taxonomy and loses the theorems — exactly the failure mode our
authored-shadow C1 stance avoids by never pretending the shadow is the explication.
→ PROPOSED-ASM-1237.

---

## 3. Richer formalisms that cover the gaps — with trade-offs

| Formalism | Covers | Decidability | Tooling / reasoners | Cost & fit here |
|---|---|---|---|---|
| **Full FOL** — Common Logic (ISO 24707), SUO-KIF/SUMO, TPTP | G1, G5 (with theory axioms), G7, G8; n-ary native | Semi-decidable (proofs findable, non-theorems may never terminate) | Mature ATPs: E, Vampire; SUMO's Sigma pipeline | We already hold `data/onto-sumo/` (15,595 KIF axioms — excluded from RULES-1 pending a KIF→rule translation bead). No fail-closed guarantee (timeout ≠ refusal ≠ disproof); proof objects exist but provenance discipline is weaker than `why()` trees. Use only if the SUMO vertical demands it. |
| **ASP** — clingo/DLV (stable models); Datalog± (existential rules) | G2 (head disjunction native), G3 (NAF native), G4 (UNA native), G6 (#count/#sum), defaults; Datalog± adds controlled G8-existentials with decidable chase fragments | Decidable on ground programs (NP/Σ₂ᵖ; polynomial fragments) | clingo: single binary, C++, excellent; fits the 2-core box | **The natural first step outside.** Prior art on our exact task family is literally LLM→ASP on CLUTRR [LIT-BACKED: Yang/Ishay/Lee 2023, already ASM-1122 backing]. Non-monotone semantics must be firewalled from ontology entailment (regime tag). Answer sets are not proof trees — provenance needs extra work (e.g. xclingo). |
| **Type theory / Lean 4 + Mathlib** (dependent types) | G11, G9, G5, G8 — all of mathematics; also machine-checked soundness of our own rules | Proof *checking* decidable; proof *search* not | Lean 4, Mathlib, mature ecosystem; heavy build | The registered Lean seam (ASM-1196). Highest authoring cost per fact by orders of magnitude; reserved for content that is mathematics or for one-off soundness certificates of compiled rules. Long-term, out of RULES-1 scope. |
| **Full OWL 2 DL tableau** — HermiT, Openllet | G2 natively (real disjunction elimination); the DL-statable residue | Decidable, N2EXPTIME worst case | Java stacks; no incremental µs-loop; explanation support exists but weaker than `why()` | Buys only what the policy-rule precompilation already delivers for our finite case inventory, at large operational cost. Not recommended (§2.1). |
| **Temporal formalisms** — reified fluents in Datalog/ASP; LTL model checking | G10 (time) | Depends on carrier | in Datalog: same engines | Prefer in-stack fluent reification first; escalate to ASP only when interval disjunction actually bites. |
| **SHACL(-AF)** | G12 | Validation decidable | in-stack | Already adopted (ASM-1162 rider i); listed for completeness — constraints, never entailment. |

The pattern across the table: **each step outside trades away exactly one of the properties
the RULES-1 certificate leaned on** — decidability (FOL), monotone proof-carrying provenance
(ASP), or µs-scale cost (Lean, tableau). That is why the stance below makes the justification
mandatory *per rule*, not per system.

---

## 4. Recommendation: a layered stance with a machine-readable justification gate

### 4.1 The gap taxonomy (the justification vocabulary)

Register the gap codes so every future "we need more expressivity" claim must pick one and
name its axis: **GAP-CASE** (axis-2 disjunction elimination, G2), **GAP-NAF** (closed-world/
defaults, G3), **GAP-UNA** (G4), **GAP-ARITH** (G5), **GAP-AGG** (G6), **GAP-NARY** (G7),
**GAP-FUNC** (G8), **GAP-HO** (G9), **GAP-MODAL** (attitudes/rigidity/time-as-operator, G10),
**GAP-MATH** (induction/arithmetic-with-proof, G11), **GAP-CONSTRAINT** (G12). A proposal that
cannot name its gap code has not met the maintainer's justification bar. → PROPOSED-ASM-1230.

### 4.2 The ladder (innermost layer that suffices, always)

| Layer | Formalism | Regime tag | When | Status |
|---|---|---|---|---|
| L-A | OWL 2 RL (sparq-reason OwlRl + twin) | `owl-rl` | default for all TBox/ABox entailment | live (RULES-1) |
| L-B | Safe N3/Datalog Horn rules (sparq `reason_n3`) | `horn-def` | cyclic rule graphs OWL cannot state (sibling/cousin diamonds), guarded inequality bodies | live carrier; regime unused so far (disclosed in RESULT.md) |
| L-C | Pre-compiled case eliminations with named ASM premises | `policy` | finite, enumerable case splits (GAP-CASE) whose covering/UNA premises can be endorsed | live (R-COVER-ELIM) |
| L-D | **ASP (clingo)** — the designated first step OUTSIDE the stack | `stable-model` (new) | GAP-NAF, GAP-AGG, GAP-UNA-at-scale, and any GAP-CASE that is not finitely pre-compilable | NOT adopted; gated on a named experiment with a concrete blocked inference |
| L-E | **Lean 4** — the proof-assistant seam (ASM-1196) | `proof-assistant` (new) | GAP-MATH, GAP-HO; plus one-off soundness certificates for L-C rules | registered future work, out of RULES-1 scope |
| (L-F) | Full FOL (CL/SUO-KIF via E/Vampire) | `fol-atp` (reserved) | only if the onto-sumo vertical's translation bead shows content that is FOL-statable but neither Horn-compilable (L-B/C) nor worth Lean cost (L-E) | reserved; not scheduled |

Rules of the ladder: (i) every rule/derivation carries its layer's regime tag end-to-end
(extends ASM-1162); (ii) a rule may sit at layer N only with a recorded justification naming
the gap code and axis that excludes every layer < N; (iii) L-D/L-E outputs never silently mix
into `owl-rl` closures — cross-regime derivations are visibly composite in `why()` trees;
(iv) fail-closed refusal (`ERR_RULE_UNIMPLEMENTED`) remains the answer for content no
adopted layer covers — approximation is never the answer. → PROPOSED-ASM-1231, 1235.

### 4.3 What this changes for RULES-1's engine choice: NOTHING

The audit in §2 finds no concept in RULES-1's frozen inventory, in the g2 claim families, or
in the OBO RO second vertical that requires L-D or beyond: the kinship vertical is L-A + one
L-C rule (measured working: certificate C_dec 1.0 stated / 0.0-reproducible entailed, engine
0.9955 Wilson-LB on third-party gold [MEASURED: `poc/rules-1/RESULT.md`; the certificate rerun
is now pinned by the FROZEN `registry/experiments/rules-1.json`, frozen 2026-07-11 — no longer
"exploratory pre-freeze"]); g2's families are EL-statable and their problem is soundness, not
expressivity (§2.2); the RO shard *appears* RL-compatible on relation-kind inspection
(`inverse_of`, `transitive_over`, `holds_over_chain`), but RL conformance depends on syntactic
placement and global restrictions, not on the presence of familiar axiom kinds [LIT-BACKED:
W3C OWL 2 Profiles, https://www.w3.org/TR/owl2-profiles/] — an actual OWL 2 RL
profile-validation run over the shard is required before "RL-profile material" is asserted as
MEASURED. **Keep sparq-reason + the
differential twin exactly as frozen; RULES-1's arms, endpoints, kill rules, and envelope are
untouched by this analysis.** The layered stance changes only what we *say* (justifications,
regime tags, the two reserved regime names) and what we *plan* (ASP experiment gate, Lean
seam sequencing). → PROPOSED-ASM-1236.

### 4.4 Sequencing (recommendation only; maintainer decides)

1. Register the taxonomy + ladder (this document's ASMs) — $0, pure bookkeeping.
2. RULES-1 proceeds unchanged.
3. First L-D candidate, *when a concrete blocked inference exists* (e.g. closed-world
   counting or a temporal case in a later world): a small pre-registered ASP twin experiment
   at the same certificate discipline. Not before.
4. Lean seam per ASM-1196 timing (much later), with the R-COVER-ELIM soundness certificate as
   the cheap first Lean artifact if the seam opens.
5. onto-sumo translation bead decides L-F's fate; nothing else waits on it.

---

## Appendix A — Proposed ASM rows (PROPOSED-ASM-1230..1238; block 1230..1239 reserved)

Emitted for central registration by the coordinator; this document does not write to
`registry/assumptions.jsonl`.

```json
[
  {"id":"PROPOSED-ASM-1230","tag":"STIPULATED","claim":"Expressivity-gap taxonomy: any claim that content is 'not expressible with the semantic-web stack' must name (a) one gap code from {GAP-CASE, GAP-NAF, GAP-UNA, GAP-ARITH, GAP-AGG, GAP-NARY, GAP-FUNC, GAP-HO, GAP-MODAL, GAP-MATH, GAP-CONSTRAINT} and (b) the axis: axis-1 not statable in OWL 2 DL/RDF/N3 at all; axis-2 statable but not derivable in the rule profiles (OWL 2 RL/N3 Horn); axis-3 statable only with wrong (open-world, monotone, non-UNA) semantics. Claims without a gap code and axis do not meet the maintainer's issue-#20 justification bar.","backing_ref":"docs/next/arch/expressivity-analysis.md#0,#4.1; maintainer directive issue #20","rationale":"Operationalises the maintainer's requirement to explicitly justify every step outside the stack; makes the justification machine-checkable rather than prose.","load_bearing":true,"status":"open","owner":"designer-1","date":"2026-07-11","notes":"Extends the regime-tag discipline of PROPOSED-ASM-1162 with a vocabulary."},
  {"id":"PROPOSED-ASM-1231","tag":"STIPULATED","claim":"Layered expressivity stance: entailment machinery is chosen from the ladder L-A owl-rl -> L-B horn-def (N3/Datalog) -> L-C policy (pre-compiled case eliminations with named ASM premises) -> L-D stable-model (ASP, outside the stack) -> L-E proof-assistant (Lean seam) -> L-F fol-atp (reserved), always at the innermost layer that suffices; a rule sits at layer N only with a recorded gap-code justification excluding every layer below N; cross-regime derivations are visibly composite in proof trees; content no adopted layer covers refuses fail-closed (ERR_RULE_UNIMPLEMENTED), never approximates.","backing_ref":"docs/next/arch/expressivity-analysis.md#4.2","rationale":"Keeps the cheap, decidable, tooled, proof-carrying stack as the default while guaranteeing the design is not expressivity-capped, per issue #20.","load_bearing":true,"status":"open","owner":"designer-1","date":"2026-07-11","notes":"Regime tags stable-model and proof-assistant are reserved names extending {owl-rl, horn-def, policy} (PROPOSED-ASM-1162)."},
  {"id":"PROPOSED-ASM-1232","tag":"STIPULATED","claim":"R-COVER-ELIM is classified axis-2/GAP-CASE: the covering case elimination is statable in OWL 2 DL (coveredBy + functional + differentFrom entails the father role assignment under tableau semantics) and its non-derivability is a property of the OWL 2 RL profile (assertion-only rule heads, no disjunction elimination); the standing remedy is the in-stack policy-regime Horn precompilation with named covering/UNA premises (PROPOSED-ASM-1120/1121), and adopting a full-DL tableau engine for RULES-1 is rejected (N2EXPTIME machinery, weaker fail-closed/proof-tree discipline, loss of the microsecond certificate loop, no capability gained on the finite case inventory).","backing_ref":"sparq inference-conformance-report.md PR1; docs/next/arch/world-model-rules-engine.md CV-8; docs/next/arch/expressivity-analysis.md#2.1","rationale":"Records the precise axis of the one measured expressivity gap already hit, so it is never misreported as 'OWL cannot express covering'.","load_bearing":true,"status":"open","owner":"designer-1","date":"2026-07-11","notes":"The RL incompleteness leg is MEASURED (conformance PR1); the classification and the tableau rejection are the stipulated parts."},
  {"id":"PROPOSED-ASM-1233","tag":"STIPULATED","claim":"NSM explications are axis-1 outside the semantic-web stack (GAP-MODAL + GAP-NARY + GAP-HO): the prime inventory contains propositional-attitude, modal, conditional and temporal operators (THINK/KNOW/WANT/FEEL/SAY, IF, BECAUSE, MAYBE, CAN, WHEN/BEFORE/AFTER) taking propositional arguments, which SROIQ/RDF cannot encode without losing the embedded formula's logical structure; therefore C1 compiles only authored, endorsed extensional constraint records (the explication's shadow) and wholesale explication->OWL translation is out of scope permanently on expressivity grounds, not merely prudence.","backing_ref":"docs/next/arch/expressivity-analysis.md#2.3; encoder 65-prime profile-1 lexicon; PROPOSED-ASM-1126 (authored compilation stance)","rationale":"Upgrades the existing no-automatic-NL->OWL stance from a prudence choice to a recorded expressivity necessity with the justification attached.","load_bearing":true,"status":"open","owner":"designer-1","date":"2026-07-11","notes":"The shadow/full-content distinction parallels the gUFO/UFO datum (PROPOSED-ASM-1237)."},
  {"id":"PROPOSED-ASM-1234","tag":"STIPULATED","claim":"Mathematical content (the Lean corpora: data/math-lean-sample, data/mathlib-1000-sample, data/math-v0, data/math-mm) is axis-1/GAP-MATH+GAP-HO: induction schemas are second-order and arithmetic-with-induction admits no complete decidable axiomatisation (Goedel), so it is outside every OWL profile by mathematical necessity; such content routes only to the L-E proof-assistant regime (the ASM-1196 Lean seam, same authored/endorsed C1 boundary), never to Horn approximation or FOL ATPs; a cheap first Lean artifact, if the seam opens, is a machine-checked soundness certificate for R-COVER-ELIM given its covering/functional/UNA premises.","backing_ref":"docs/next/arch/world-model-rules-engine.md#expressivity-boundary (PROPOSED-ASM-1196); docs/next/arch/expressivity-analysis.md#2.4","rationale":"Discharges the maintainer's #19/#20 mathematics flag with the specific impossibility justification and names the cheapest useful first Lean deliverable.","load_bearing":false,"status":"open","owner":"designer-1","date":"2026-07-11","notes":"Out of RULES-1 scope; sequencing unchanged from ASM-1196."},
  {"id":"PROPOSED-ASM-1235","tag":"STIPULATED","claim":"The designated first formalism OUTSIDE the semantic-web stack is ASP (clingo, stable-model semantics), covering GAP-NAF (closed-world/defaults), GAP-AGG (counting as derivation), GAP-UNA at scale, and non-precompilable GAP-CASE; it is NOT adopted now — adoption is gated on a named experiment triggered by a concrete blocked inference, run at the RULES-1 certificate discipline, with stable-model outputs regime-tagged and never mixed silently into owl-rl closures; full-FOL ATPs (Common Logic/SUO-KIF via E/Vampire) are reserved (L-F) pending the onto-sumo translation bead and are disfavoured for fail-closed use because timeout, refusal and disproof are indistinguishable at the interface.","backing_ref":"Yang/Ishay/Lee 2023 arXiv:2307.07696 (LLM->ASP on CLUTRR, existence proof on the exact task family, per ASM-1122 backing); docs/next/arch/expressivity-analysis.md#3,#4.2","rationale":"Picks the step-outside formalism with decidable ground reasoning, single-binary tooling fit for the 2-core box, and direct prior art on our task family, while keeping it gated rather than adopted.","load_bearing":true,"status":"open","owner":"designer-1","date":"2026-07-11","notes":"Provenance gap disclosed: answer sets are not proof trees; any adoption experiment must include a why()-equivalent (e.g. xclingo-style) leg."},
  {"id":"PROPOSED-ASM-1236","tag":"PROVISIONAL","claim":"No concept currently in scope — the RULES-1 kinship inventory (subPropertyOf, domain/range, inverse, functional, disjoint, length-2 chains, the covering policy rule), the g2 claim families (R1 subClassOf, R3 domain/range, R4 existential read-outs), and the onto-obo RO second vertical (inverse_of, transitive_over, holds_over_chain) — requires any layer beyond L-A/L-B/L-C (i.e. beyond OWL RL + N3 Horn + policy precompilation); this is an audit conclusion about the enumerated current corpus, held PROVISIONAL because it is not yet backed by a reproducible exhaustive kind-census (promotion to MEASURED requires one) and because the RO-shard leg additionally requires an actual OWL 2 RL profile-validation run (RL conformance depends on syntactic placement and global restrictions, not relation-name inspection; W3C OWL 2 Profiles, https://www.w3.org/TR/owl2-profiles/); it does NOT extend to future kernel growth, new verticals (temporal narrative, closed-world counting, onto-sumo), or any content class not enumerated here.","backing_ref":"docs/next/arch/expressivity-analysis.md#2,#4.3; poc/rules-1/RESULT.md (kinds actually compiled); data/onto-obo/ RO shard; W3C OWL 2 Profiles","rationale":"States precisely why RULES-1's engine choice is unchanged by the expressivity directive, with the classification's evidential grade and its promotion path explicit.","load_bearing":false,"status":"open","owner":"designer-1","date":"2026-07-11","resolution_path":"Promote to MEASURED via (a) a reproducible kind-census script over the three enumerated corpora and (b) an OWL 2 RL profile-validation run over the RO shard; re-audit against the gap taxonomy whenever a new axiom kind, vertical, or world class is proposed; the first blocked inference fires the L-D gate experiment (PROPOSED-ASM-1235).","notes":"RULES-1 arms, endpoints, kill rules, envelope untouched. load_bearing demoted to false (2026-07-11 review-gate correction): RULES-1's engine choice stands on its FROZEN registration independently of this classification, so nothing may rest on this row until the census/profile-validation promotion lands."},
  {"id":"PROPOSED-ASM-1237","tag":"STIPULATED","claim":"gUFO/UFO stance: full UFO's inference-bearing metaproperties (rigidity, anti-rigidity, relational dependence) are quantified-modal (axis-1/GAP-MODAL+GAP-HO — quantification over worlds and over predicates), which is why only the gUFO subset exists in RDF (the maintainer's observation, adopted as a datum); accordingly, if UFO-grade metaproperties are ever wanted here they enter as annotation/validator discipline (non-inference-bearing) unless and until a modal layer is deliberately adopted under the PROPOSED-ASM-1230 justification protocol — an RDF rendering of a modal ontology keeps the taxonomy and loses the theorems, and must never be presented as carrying the full theory.","backing_ref":"Guizzardi 2005 (UFO in quantified modal logic); gUFO specification (Almeida et al.); maintainer note on issue #20","rationale":"Generalises the maintainer's own gUFO observation into a reusable rule about modal foundational ontologies and the stack.","load_bearing":false,"status":"open","owner":"designer-1","date":"2026-07-11","notes":"Directly parallels the explication-shadow stance (PROPOSED-ASM-1233)."},
  {"id":"PROPOSED-ASM-1238","tag":"STIPULATED","claim":"Expressivity is NOT the binding constraint on the g2/Pi line: the R1/R3/R4 claim families are OWL-EL-grade statable, and the proxy-strength failure there is ordinary-meaning soundness of the derived statements (precision bracket 0.29-0.45, PROVISIONAL-ON-LLM-PROXY, human gold adjudicates), which no richer logic repairs; no expressivity upgrade may be cited as a remedy for g2/HS2. The one genuine expressivity boundary on that line — deriving named individuals from existential heads — is kept closed by design (refusal over skolemisation, PROPOSED-ASM-1162 rider ii).","backing_ref":"docs/next/interpretations/g2.md; ASM-1180/ASM-1181; docs/next/arch/expressivity-analysis.md#2.2","rationale":"Prevents the expressivity workstream from being spent, or spun, as a fix for a soundness problem.","load_bearing":true,"status":"open","owner":"designer-1","date":"2026-07-11","notes":"Ids 1239 unused; block 1230..1239 reserved to this document."}
]
```

---

**Self-check gate:** no feasibility conclusion stated or implied anywhere above; every
gap claim carries a gap code, an axis, and a one-line justification (the maintainer's #20
requirement); the axis-1/axis-2/axis-3 distinction is applied throughout, in particular
R-COVER-ELIM is reported as profile-incompleteness (axis 2), never as "OWL cannot express
covering"; all epistemic tags provisional; MEASURED citations point at their artifacts and
the RULES-1 certificate is cited against the now-FROZEN `registry/experiments/rules-1.json`
(the earlier "exploratory pre-freeze" flag is superseded, 2026-07-11); g2 numbers carry
PROVISIONAL-ON-LLM-PROXY; RULES-1's frozen design (arms, endpoints, kill rules, envelope,
engine choice) is untouched; new assumptions confined to the disjoint block 1230..1239;
`registry/assumptions.jsonl` untouched; no @handle/account strings.
