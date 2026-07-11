# P3-D-CODEVERT — CODEVERT/1 rev 2: critique + synthesis of the code-vertical selective coprocessor (CASK-CODE/1)

> **Status: [DESIGN-CRITIQUE + SYNTHESIS, rev 2] — revision in response to the
> GPT-5.6 review-gate finding `poc/gpt56-review/rev-codevertb-20260711/
> last-message.json` (read in full; point-by-point response table at the end of
> this document). The review's operative ruling is adopted verbatim: this
> design does not become experiment-driving authority, and the G1 census, G2
> attribution kill, and G4 prereg are NOT run or frozen, until this revision's
> corrections are externally accepted. The only work authorized meanwhile is a
> NON-SCORED extractor engineering spike (§7-G0). Nothing here is frozen,
> pre-registered, scheduled, or run; no verdict, audit, frozen object, or
> registered ruling is touched. Rev-1's assumption entries ASM-1000…ASM-1008
> are REGISTERED (block ASM-1000–1029 assigned to this bead). Rev-2's new
> entries are **PROPOSED-ASM ASM-1030…ASM-1039** (a fresh DISJOINT block per
> the coordinator's instruction; NOT yet in registry/assumptions.jsonl — this
> document performs no registry edit; the coordinator registers them). Author:
> Fable, chief-architect role (`kern/fable-designer`), 2026-07-11.
>
> **Inputs read at source, in full:** everything in rev 1's input list; PLUS
> the GPT-5.6 review-gate finding above; docs/next/design/NLB.md §6–§7 (score
> class + the NLB-0 non-decisive discipline); docs/next/design/FRONT.md §5
> (Rules 1–5, shared/matched vs native cells); docs/next/design/RAGC.md
> (GR-A/B/C/D arm semantics, §2.3–§2.4 parity + anti-weak-control, §7–§8
> contrast table, manifest, and the §8.4 paired-statistics shape);
> docs/next/programme-3-neurosymbolic-architecture.md §1.2/§1.3/§1.3a/§2
> (KOT-SIZE/2, KOT-COST/2, KOT-LIFE/1, KOT-FAIR/2, §2.5 statistics).
>
> **Tag convention (house discipline):** `[MEASURED: ref]` = a registry
> verdict/assessment/artifact restated strictly inside its envelope;
> `[LIT-BACKED: lit-review §]` = an external fact verified at primary source by
> a completed Phase-0 lit review, cited through that review;
> `[STIPULATED: ASM-id]` = a design choice registered here or inherited —
> every design CHOICE in this document is STIPULATED, not MEASURED, unless a
> measurement is explicitly cited; `[PROPOSED-ASM: id]` = a rev-2 design
> choice pending coordinator registration; `[ESTIMATED]` = a planning number
> with no measurement behind it (all costs, all coverage/retention
> projections); `[EXTRAPOLATION: ASM-id]` = a registered forward projection,
> never a premise.

---

## 0. One-paragraph summary

GPT-5.6's CASK-CODE/1 is the strongest architecture proposal Programme-3 has
received: it is narrow, typed at exactly two neural↔symbolic seams, fail-closed,
and it names its own deflationary outcome (the aligned-generic-store arm) as a
first-class kill. Rev 1 confirmed the core recipe and repaired four defects
(mandatory-inverse, superfluous v1 verify-retry, unmeasured extraction
coverage, pilot duplication). The rev-2 external review found rev 1 itself not
yet commit-grade on five counts, all accepted here: (1) **G1's
extractor-relative query universe was circular** — it conditioned on
successful extraction and could report high κ while the extractor silently
missed edges; G1 is rebuilt on an extractor-INDEPENDENT universe with
query-level recall/completeness and negative-answer validity endpoints
[PROPOSED-ASM: ASM-1030]; (2) **the generic-store deconfound was not concrete
at the NL boundary** — two NL-valid controls are now pinned (GEN-EXEC: the
identical NLB front-end over the generic executor; TOOL-NL: a strong native NL
tool-use arm built under FRONT §5), and DECONF-A2 is re-scoped to
executor-validation only [PROPOSED-ASM: ASM-1032]; (3) **the "cheap decisive
test" claim is withdrawn** — G2 is a non-decisive screen (it inherits NLB §7's
own self-description), the decisive distinctive-architecture evidence lives
only at G4, which now carries paired cluster-level superiority/non-inferiority
statistics, a numeric clarification budget, and one internally consistent arm
table [PROPOSED-ASM: ASM-1033/1034/1035/1039]; (4) **the KOT-FAIR/2 manifest
is instantiated in full** (§6.1) [PROPOSED-ASM: ASM-1036]; (5) **the extractor
and edit path are honestly re-scoped** — `ast+symtable` is a
deliberately-restricted static subset (PY-STAT/1) with pinned `unknown`
propagation for inverse/exhaustive queries; rename is confined to a
syntactically closed subset with a finite pinned hazard inventory replacing
"plausibly"; and the annotation costs are repriced against the programme's
measured binding resource [PROPOSED-ASM: ASM-1031/1037/1038]. Everything here
still licenses at most an **architecture-family** claim; no outcome of any
CODEVERT rung is evidence about kernel CONTENT [STIPULATED: ASM-1000].

---

## 1. What GPT-5.6 proposed (restated for the record)

CASK-CODE/1: a selective coprocessor for Python repository comprehension and
two bounded edits. Deterministic conservative extractor (CPython ast +
symtable, pinned import resolver) → versioned relational substrate with
proved/disproved/unknown/conflict states and byte-span provenance → Tier-0
exact templates → a 110–360M contract front-end (intent + BIO spans +
role/direction + answer-shape + answerability heads) → a calibrated
ambiguity-set constructor emitting 1–8 complete DSL contracts → a
contract-and-contrast gate that executes every surviving interpretation and
answers only on denotation agreement, else deterministically CLARIFIES (one
scripted turn, inside the measured system, charged) or ABSTAINS. Edits go
through span-scoped neural drafting + a mechanical verifier with ≤2 retries.
Nine comparison arms including TOOL-native and GENERIC-store (identical
extracted facts in SQLite/Datalog); binding win = LB95 coverage ≥ +5 pts over
the strongest baseline at UB95 dangerous-error < 0.02, with GENERIC-store
within a 2-pt margin pre-registered as the death of the distinctive claim.
Cheapest falsifier: a CODE-only pilot on the existing 855-query grammar + ~300
new blind phrasings, three arms, ≤5 GPU-h + ~$25. Named worst failure:
agreement laundering; named strategic failure: attribution collapse.

The queried operations are real: all eight (callers-of, callees-of,
imports-of, imported-by, contains, contained-in, where-defined, instance-of)
are families of the measured kot-query-code/1 grammar
[MEASURED: registry/verdicts/a5.json + docs/design-a5-code-worldlayer-oracle.md
family inventory]. The two edit contracts are NEW surface with no measured
precedent anywhere in the registry.

---

## 2. Stress test 1 — does each component work at 100M–2B, or hand-wave at the seam?

Component-by-component verdicts:

**2.1 The seam discipline itself: SOUND, and the proposal's best feature.**
Exactly two serialized interfaces (`InterpretationSet/1`, `EditCandidate/1`),
no residual-stream injection, no opaque capsule addressing. This is the right
lesson from the measured record: the nsk1 internal-delivery line delivered at
echo grade but integration stayed unresolved, and text-appended grounding was
net-harmful — delivery topology, not content, was the binding failure
[MEASURED: docs/next/feasibility-synthesis.md §1 nsk1/g2d readings, restated
inside their DRAFT/exploratory envelope]. A typed, executable contract at the
boundary is the only seam class with a measured green anywhere in the registry
(the verify-retry accept seam of f2b-replicate,
+0.1507 / LB +0.1053 at cost 0.103
[MEASURED: registry/verdicts/f2b-replicate.json]).

**2.2 Deterministic extractor: buildable ONLY as a deliberately-restricted
static subset — rev 2 makes that scope explicit and binding.** The review is
accepted as written: `ast + symtable` is NOT a call/reference resolver for
general Python. Higher-order calls, decorators, descriptors, inheritance
dispatch, dynamic imports, aliasing across assignments, generated attributes,
and framework registration (entry points, plugin registries, metaclass
machinery) will force substantial `unknown` mass on real repositories — this
is expected behaviour of the design, not a surprise to be discovered
[PROPOSED-ASM: ASM-1031, superseding the softer reading in rev 1].

- DECISION: [STIPULATED: ASM-1031] the extractor is specified as **PY-STAT/1, an enumerated static
  subset**: a pinned, finite inventory of Python constructs for which each
  relation's edges are resolved (direct name-bound calls where the callee
  binding is a module-level or class-level def resolvable through symtable
  scoping and the pinned import resolver; static `import`/`from … import`
  statements; lexical containment; literal class instantiation and
  single-inheritance static attribute resolution over fully-analyzed bases).
  EVERYTHING outside the inventory emits `unknown` edges fail-closed: any call
  through a value of unresolved binding, any attribute access on a
  non-statically-typed receiver, `getattr`/`__import__`/importlib, decorators
  that are not the identity-preserving pinned allowlist, star imports,
  conditional imports, metaclasses, `exec`/`eval`. The inventory itself is a
  content-hashed artifact of the extractor spike (§7-G0) and is frozen before
  the G1 census runs [PROPOSED-ASM: ASM-1031].
- DECISION: [STIPULATED: ASM-1031] **`unknown` propagation for inverse/exhaustive queries** (the
  review's concrete gap — callers-of, imported-by, and every other query whose
  answer is a completeness claim over the whole repo). Each `unknown` edge
  carries, where syntactically derivable, a **candidate-name set** (e.g. the
  attribute name at an unresolved call site); an `unknown` edge with no
  derivable name is treated as potentially targeting EVERYTHING. An
  inverse/exhaustive query over target `t` returns status `proved` ONLY if
  (a) every listed edge is `proved` AND (b) the completeness precondition
  holds: no `unknown` edge of the queried relation kind exists anywhere in the
  analyzed scope whose candidate-name set contains `t`'s name (or is
  unrestricted). Otherwise the answer is
  `UNKNOWN-INCOMPLETE(partial_listing, blocking_unknown_count)` — the partial
  listing is labelled a lower bound, never an answer. Negative answers
  (`proved`-empty) require the SAME completeness precondition; a gold-empty
  answer without it is `UNKNOWN-INCOMPLETE`, and full-distribution scoring
  counts it as such [PROPOSED-ASM: ASM-1031, hardening ASM-1003].
- Two under-priced costs stand from rev 1, now with honest numbers: (a) blind
  repo-disjoint human annotation is REAL human-annotation spend, and human
  annotation is the programme's measured binding constraint, not compute
  [MEASURED: docs/next/feasibility-synthesis.md §6] — repriced in §7; (b) what
  fraction of the product task distribution is `proved`-answerable on REAL
  repositories is unmeasured; the programme's measured coverage numbers are
  brutal everywhere they exist (g8 0/1000 random Mathlib declarations; m0b
  0.3542 on the friendliest corpus, corpus-indexed
  [MEASURED: registry/verdicts/g8.json + registry/verdicts/m0b.json per
  ASM-0001]). "Python repos are a friendlier extraction target" is an
  expectation, not a number — registered as EXTRAPOLATION
  [EXTRAPOLATION: ASM-1008]; the G1 census (rebuilt, §7-G1) precedes all task
  authoring and all model work [STIPULATED: ASM-1004 as amended by
  PROPOSED-ASM: ASM-1030].

**2.3 The 110–360M contract front-end: plausible band, gate not cleared by
any cited number — every retention figure below is ESTIMATED/ASSUMED, never
MEASURED.** The closest published shapes sit AT or BELOW the interesting bar:
110M BERT-class whole-frame exactness ≈88.2% ATIS / ≈92.8% Snips;
template-mined + grammar-constrained text-to-SQL (TeCoD) 83.6–89.2%
matched-template EX; learned parsers still drop 14.0% overall / 50.7%
worst-perturbation under Dr.Spider-style rephrasing; compositional-split
collapse (COGS 96–99% ID vs 16–35% OOD) is the standing warning for
role/direction binding [LIT-BACKED: docs/next/lit/PARSE.md §2, §5a, §5c].
The review's honest band on a closed grammar is ~0.85–0.95 with
paraphrase-diverse training + lexicon resources, and "no cited work reports
retention-at-S2-bound for a ≤360M parser on a grammar like ours"
[LIT-BACKED: docs/next/lit/PARSE.md §5a, §7.1] — i.e. **the literature does
NOT guarantee the joint 0.90-retention/S2 bar**; that projection is
[ESTIMATED], carried only inside EXTRAPOLATION ASM-1008 and resolved only by
G2/G3 themselves. Verdict: the encoder-heads recipe is the right FIRST build
(it is NLB's registered primary parser class, ASM-0905, independently
converged on); the pilot's 0.80-coverage screen bar is inside the plausible
band; CASK's final +5-pt-over-baseline bar is an open empirical question,
never a premise. The BIO-span contract also means descriptive references
("the function that parses configs") are out-of-contract by construction — a
disclosed coverage cost, not a defect [STIPULATED: ASM-1002].

**2.4 The ambiguity-set constructor: one real defect — the mandatory-inverse
rule.** CASK §4 step 4: "for every directional contract, forcibly add its
typed inverse alternative before acceptance." This is, almost verbatim, the
NLB revision-1 rule that GPT-5.6's OWN external review of NLB ranked as its
concern #1 and that NLB rev-2 rejected: on genuinely directional queries the
correct and inverse denotations normally differ, so a
both-orientations-always set either abstains (NLB's answer-on-agreement) or —
in CASK's variant — burns the single clarification turn on essentially every
directional item, including items whose surface orientation cues are present
and unambiguous. Consequences: clarification rate ≈ the directional share of
the workload (~most of the 70% relational stratum), matched-resource token
and latency accounting inflates against CASK by construction, and users are
asked to disambiguate questions that were never ambiguous. Worse, the rule
does not even buy the safety it advertises: when both orientations return
EQUAL denotations (typically both empty), agreement licenses an answer while
saying nothing about which reading was intended — a systematic
empty-denotation subclass of exactly the agreement laundering CASK §10 fears.
- DECISION: [STIPULATED: ASM-1031] the synthesis replaces mandatory-inverse with the
  **evidence-gated ambiguity-set semantics already registered for NLB**: a
  pinned per-frame orientation-cue inventory decides each directional frame;
  cues present-and-consistent select ONE orientation; cues
  absent-or-conflicting add BOTH; trie collisions add competing bindings;
  a singleton set → answer (subject to contracts + τ), a larger set →
  execute all and answer only on denotation agreement, else CLARIFY.
  Systematic inversion is
  caught where it belongs: the both-orientation EVAL strata with near-zero
  per-stratum wrong allowances and the deterministic ROLE_DIR repair — the
  layered-control design law [STIPULATED: ASM-1001, adopting ASM-0940(1)/(2)
  and ASM-0941(3); the measured motivation is a5-nl's deterministic
  direction-table kill, contained-in 24 / where-defined 18 —
  MEASURED: registry/verdicts/a5-nl.json].
- Kept from CASK: the ≤8-contract cap and empty-set → abstain. **Score-class
  pinning corrected (rev 2):** rev 1 alternated between pinning
  split-conformal scoring here and inheriting NLB's protocol; the alternation
  is resolved by full deference — the front-end inherits NLB §6's threshold
  protocol INCLUDING its at-freeze score-class selection (raw probability vs
  CAL-A-trained calibrator vs conformal nonconformity; ONE chosen at freeze
  under ASM-0943's fixed-sequence risk-controlled procedure). No score class
  is pinned by this document. The honesty line stands: whatever class is
  chosen, calibration guarantees are claimed only for the pinned phrasing
  distribution (exchangeability breaks across sources by construction; the
  CAL-vs-EVAL shift delta is a measured secondary)
  [LIT-BACKED: docs/next/lit/PARSE.md §4; STIPULATED: ASM-1001 as amended,
  adopting ASM-0903(3)/ASM-0943].

**2.5 The edit path: NOT build-ready — re-scoped in rev 2 to a syntactically
closed subset, and demoted to design-track until G4.** Rev 1 correctly found
that for rename/insert_import an accepted contract makes the edit
deterministic — but its admissibility rule ("full reference closure is
proved… zero unknown references plausibly naming it") was not operationally
definable for general Python, exactly as the review says. Corrections
[PROPOSED-ASM: ASM-1037, superseding the admissibility clause of ASM-1007]:

- DECISION: [STIPULATED: ASM-1037] v1 edits execute SYMBOLICALLY — accepted contract → deterministic
  applicability check → deterministic transform → mechanical verifier (parse,
  span authorization, symbol resolution, postcondition, repo compile, pinned
  tests) → PATCH + certificate, no retries because nothing is sampled. The
  neural-draft + bounded verify-retry loop is DEFERRED to a later genuinely
  generative edit contract (G5b), where GPT-5.6's design of it (structured
  violation traces, ≤2 retries at matched token budget, certificate scope
  limited to mechanical properties) is adopted as written
  [STIPULATED: ASM-1007].
- DECISION (rev 2): **rename is scoped to RENAME-SAFE/1, a syntactically
  CLOSED subset**: the target is a module-level or class-level def/class/
  assignment whose entire PY-STAT/1 reference closure lies within modules
  fully analyzed under the PY-STAT/1 inventory, with zero `unknown`-status
  edges in those modules of any relation kind that could bind the name (per
  the §2.2 candidate-name rule). "Plausibly naming it" is REPLACED by a
  **finite pinned hazard inventory H1–H8**, each an executable scan; ANY hit
  → ABSTAIN(analysis_incomplete): H1 `getattr`/`setattr`/`hasattr`/`delattr`
  with a string literal equal to the identifier; H2 the identifier in any
  `__all__`/`__slots__` literal; H3 `globals()`/`locals()`/`vars()` subscript
  or `.get` with the identifier; H4 `eval`/`exec`/`compile` present anywhere
  in a closure module; H5 an exact-identifier string literal anywhere in repo
  source or pinned config surfaces (entry_points, setup/pyproject, ini/toml/
  yaml keys) — docstrings and comments INCLUDED, fail-closed; H6
  `importlib`/`__import__` in a closure module; H7 the name participates in
  shadowing or in an MRO crossing any class with an unanalyzed base; H8
  dynamic attribute-name construction patterns (`getattr(x, f"…")`,
  `format`/`+` building an attribute or import name). The inventory is
  content-hashed with the extractor; extending it is an extractor version
  change [PROPOSED-ASM: ASM-1037].
- DECISION (rev 2): **insert_import semantics fully pinned**: placement =
  after the module docstring and any `__future__` block, appended to the
  existing top-level unconditional import block per a pinned ordering profile
  (stdlib/third-party/local, profile content-hashed); NO formatter is run —
  exact byte insertion with pinned newline discipline; alias/name collision
  with ANY existing module top-level binding → ABSTAIN; `__future__` imports
  are NOT an admissible target; conditional/`TYPE_CHECKING`/try-except import
  blocks are never created or modified; applicability requires the module to
  parse cleanly, to not already import the target (idempotence check → no-op
  refusal), and to contain no import hooks in the pinned hazard scan
  [PROPOSED-ASM: ASM-1037].
- DECISION (rev 2): **certificate honesty clause**: compile + pinned-test
  success certifies only OBSERVED MECHANICAL BEHAVIOUR (parse validity, span
  authorization, postconditions on the analyzed closure, the test suite that
  actually ran) — never semantic completeness of the rename over dynamic
  behaviour. The certificate schema carries this scope line verbatim
  [PROPOSED-ASM: ASM-1037].
- STATUS: the edit path is design-track only. No edit-path bead is buildable
  before G4 survives; the RENAME-SAFE/1 subset and hazard inventory are
  specified now so the G5a prereg has a closed object to freeze, not because
  the path is build-ready [PROPOSED-ASM: ASM-1037].

**2.6 Tier-0, substrate schema, cost envelope: adopt with NLB's pins.**
Tier-0 exact templates ≈ the measured 250–267 µs a1-hybrid class; executing
2–8 interpretations is ≈free at the measured 5.29–7.82 µs/query engine cost
[MEASURED: registry/verdicts/l3a-parse.json + a5-nl.json frontend timing;
registry/verdicts/a5.json engine timing]. The substrate reuses the measured
code-world schema and executor (CASK says this itself — correct). The size /
latency ceilings, packed-artifact manifest, and API-parser ineligibility rule
are NLB's registered pins and apply unchanged (artifact ≤1.0 GB, Tier-1 warm
p95 ≤500 ms CPU, measured in-gate) [STIPULATED: ASM-1001, adopting
ASM-0946(1)–(5)]. The full KOT-FAIR/2 measurement obligations these pins sit
inside are instantiated at §6.1 [PROPOSED-ASM: ASM-1036].

---

## 3. Stress test 2 — does it REALLY get NL into the symbolic substrate, or smuggle an oracle?

**3.1 The clarification protocol: clean at runtime — rev 2 adds the numeric
budget the evaluation was missing.** Pre-annotated intended readings,
scripted responses that reveal only a choice among the arm's DISPLAYED
readings, every arm (including RAG/tool baselines) gets the same one turn,
malformed clarification = failure, turn/tokens/latency charged, and an arm
that fails to display the intended reading cannot be rescued. This is a
measured-system component, not an oracle [STIPULATED: ASM-1002]. What rev 1
lacked (review, ranked concern 3): nothing NUMERIC stopped an
always-clarify/set-happy system from converting candidate recall into
"completed coverage". DECISION [PROPOSED-ASM: ASM-1033]:

- **Clarification-rate caps (instrument-validity gates, planning values,
  maintainer-adjustable at prereg — [ESTIMATED], not derived from any
  measurement):** on items pre-annotated UNAMBIGUOUS, clarification rate
  ≤ 0.05; over the full scored distribution, clarification rate ≤ 0.20. An
  arm exceeding either cap has its coverage numbers VOIDED for any binding
  win (reported, disclosed, never headline-eligible) — the cap is a gate on
  the instrument reading, not a tuning target.
- **Clarification-adjusted utility endpoint:** the G4 primary coverage
  quantity is U = mean over items of `correct_i × (1 − λ·clar_i)` where
  `clar_i` ∈ {0,1} marks a charged clarification turn and λ = 0.25 is a
  pinned planning discount ([ESTIMATED]; maintainer-adjustable at prereg,
  frozen before any scored run). Raw completed coverage and the
  no-clarification stratum are co-reported beside U on every readout; the
  binding superiority claim (§7-G4) is computed on U. Clarification-turn
  latency/tokens/energy are additionally charged in the KOT-COST/2 vector
  (§6.1), so a clarify-heavy arm pays twice: in U and in cost.

**3.2 The residual oracle is at corpus construction, and it is the same one
NLB already discloses — rev 2 adds the independence pin the review demanded.**
Tasks are backward-authored phrasings of a closed grammar over repo symbols;
ambiguity and intended readings are annotated by people who know the grammar.
That supports a controlled semantic-parsing + task-completion claim — it is
NOT evidence about naturally occurring developer traffic, and the workload
model is a STIPULATED distribution, not a measured demand distribution. Both
limitations ride verbatim on any G4 readout [STIPULATED: ASM-1002, adopting
the ASM-0945(1) disclosure discipline]. NEW, closing the
coverage-by-construction hole: **task targets at G1 AND G4 are sampled from
the extractor-independent syntactic census of §7-G1, never from the
extractor's symbol table or fact store** — the census generator consumes raw
repo bytes only, is content-hashed and seed-pinned before the extractor runs
on those repos, and task authors receive census entries, not extraction
output. Backward authoring over REGISTERED (= successfully extracted) symbols
is thereby excluded by construction [PROPOSED-ASM: ASM-1030].

**3.3 The anti-smuggle rules CASK gets right — kept and hardened.**
Full-product-distribution scoring (never covered-slice-only) with blind
extraction coverage κ co-reported; the symbolic side never interprets prose;
execution success never certifies interpretation. Hardening: items whose
answer depends on `unknown`-status extraction MUST be answered
unknown/ABSTAIN and are creditable only under the pre-annotated
answerability labels — extraction incompleteness can never silently shrink
the denominator [STIPULATED: ASM-1003; the §2.2 `UNKNOWN-INCOMPLETE`
propagation rule makes this executable for inverse/exhaustive queries,
PROPOSED-ASM: ASM-1031].

**3.4 What the covered slice is now worth.** The just-landed f2b-transfer
stage-1 endorsement PASS (blind external adjudication endorses the membership
gold at A = 0.9784, one-sided 95% LB 0.9606 ≥ 0.70; 360 adjudicated, 36
unresolved ≤ cap; adjudication_valid = true) establishes that kernel-line
covered-slice CONTENT survives blind external adjudication on the covered
slice [MEASURED: poc/f2b-transfer/judge-1-results/stage1-analysis.json +
registry/experiments/f2b-transfer.json stage-1 gate]. Scope discipline,
stated exactly as the review scopes it: that is an endorsement of the d-qa
membership gold, on the family/world line — **it supplies NO evidence for
code extraction or NL entry**, which remains the measured FAIL this whole
design exists to attack (a5-nl 41.6% retention + S2 kill fired
[MEASURED: registry/verdicts/a5-nl.json]). Its relevance here is morale-free
and precise: the definitional-circularity failure mode did NOT fire where it
was tested, so "self-authored gold is inherently circular" is not a standing
objection to CODEVERT's G4 gold protocol PROVIDED G4 buys the same insurance
— blind, repo-disjoint, externally-adjudicated task gold. It improves
confidence in that separate membership-gold PROCEDURE; nothing more
[STIPULATED: ASM-1006].

---

## 4. Stress test 3 — is the matched-win claim honestly falsifiable and cheap-first?

**4.1 Falsifiable: yes — but rev 1 overclaimed "cheap AND decisive", and the
generic-store deconfound was not concrete at the NL boundary. Both corrected.**
The arm ladder is the strongest baseline inventory any proposal has carried,
and CASK pre-registers its own death: GENERIC-store within a 2-pt
non-inferiority margin kills the distinctive neurosymbolic claim even if CASK
is a good product. The CASK-set-vs-CASK-top1 frontier condition isolates the
one mechanism this architecture family adds. All kept [STIPULATED: ASM-1006].
What changes [PROPOSED-ASM: ASM-1032]:

- DECISION: [STIPULATED: ASM-1032] **the two NL-valid generic-store controls, pinned concretely. No
  gold SQL, no gold formal contract, no oracle parse enters EITHER arm at any
  rung.**
  1. **GEN-EXEC** — the IDENTICAL NLB-FE/1 contract front-end (same parser
     weights, same acceptance layer, same frozen τ, same clarification
     protocol) whose accepted contracts are compiled to the generic executor
     by the pinned deterministic kernel-op→SQL mapping table (RAGC §5.3's
     GS-C protocol; an unmapped operation VOIDS the elimination reading at
     that scope, per ASM-0954). The NL→contract step is the SAME measured
     in-system component in both arms; the contrast isolates
     substrate/executor value ONLY. Claim licence: "the kernel substrate +
     engine add (nothing/something) over generic deterministic execution of
     the same contracts" — an executor-axis sentence, never an NL-entry
     sentence.
  2. **TOOL-NL** — a STRONG native NL tool-use arm: an in-budget tool-calling
     model consuming the task NL directly and calling the GS-C JSON tool
     schemas (RAGC §2.3 GR-C surface), built and tuned by the FRONT/1
     pipeline under the SAME T_k meter, pinned standard-harness defaults, and
     fixed selection rule as every comparator — RAGC §2.4's anti-weak-control
     counters apply in full (deviating below harness defaults requires a
     logged reason; nomination window + challenger gate open to outsiders;
     build logs published). This is the FRONT §5 NATIVE cell for the tool
     baseline. Claim licence: "CODEVERT's typed front-end beats the best
     in-budget native NL tool-use system at equal risk" — the actual
     distinctive-architecture contrast.
  3. **Who maps NL→tools is thereby answered per arm**: in GEN-EXEC, the
     shared measured parser via a deterministic mapping (no new NL
     component); in TOOL-NL, the arm's own in-budget model (its NL handling
     is part of its measured product, exactly as S's parser is part of S —
     FRONT §6/ASM-0808 applied to comparators).
- DECISION: [STIPULATED: ASM-1032] **DECONF-A2 re-scoped.** DECONF Stage A2 (GS-C: the a5 typed
  world in pinned SQLite + published recursive-CTE library, run on the pinned
  977-query FORMAL slice) is reused ONLY as executor validation — it proves
  the generic executor covers the query surface and supplies the GS-C
  artifact. It is FORMAL-query reproduction and is NOT an early NL
  attribution-collapse test; rev 1's reading of it as "priced FIRST at ~$0"
  attribution evidence is withdrawn. Early NL-boundary attribution SIGNAL
  (screen-grade only) comes from G2's GEN-EXEC/TOOL-NL arms; attribution
  EVIDENCE exists only at G4 [PROPOSED-ASM: ASM-1032; ASM-0963 consumed
  within its actual scope].
- HONESTY (review, ranked concern 3, accepted): **no cheap decisive
  distinctive-architecture test exists in this design.** G2 is a non-decisive
  screen (§7-G2); G3 decisively tests the NL parser, NOT whether CODEVERT
  beats a generic store/tool system; G4 is the only rung whose statistics can
  carry the distinctive claim, and it is deliberately deferred behind the
  screens. The ladder buys cheap KILLS (each rung can stop the programme
  spending), not cheap WINS [PROPOSED-ASM: ASM-1039].

**4.2 Gaps, each with a registered repair:**

1. **Statistics — rev 2 corrects rev 1's own repair.** Rev 1 adopted NLB's
   cluster-Clopper–Pearson machinery for everything; the review is right that
   CP is a SINGLE-ARM exact bound — it cannot give the CI for a PAIRED
   coverage difference (+5-pt superiority) or the 2-pt generic-store
   non-inferiority. DECISION [PROPOSED-ASM: ASM-1034]: the G4 statistical
   plan is split by leg type —
   - **Paired difference legs (superiority):** every arm-vs-arm coverage/
     utility contrast is estimated on PAIRED per-item outcomes, clustered at
     the base-task level (K=3 phrasings per cluster), via the programme §2.5
     machinery: hierarchical cluster bootstrap preserving paired predictions
     (resample base-task clusters; within each, keep both arms' outcomes on
     the same items), LCB95 of the paired Δ on U vs the pre-named strongest
     baseline arm ≥ +5 pts = the binding win condition.
   - **Non-inferiority legs (the death condition):** GENERIC-store
     (GEN-EXEC and TOOL-NL each, separately named) within 2 pts is tested as
     paired cluster-level TOST/NI (RAGC §2.3's shape): the 90% CI of the
     paired Δ inside (−2, +2) pts ⇒ attribution collapse fires, feeding
     K-P3v2(4) at this scope. Neither superiority nor NI established ⇒
     INCONCLUSIVE-UNDERPOWERED, disclosed, NO attribution sentence in either
     direction (RAGC's fail-closed downgrade discipline).
   - **Single-arm rare-event legs:** dangerous-error rates and per-stratum
     directional kills KEEP the exact cluster-collapsed Clopper–Pearson UB
     (that is what CP is for) [STIPULATED: ASM-1006 adopting ASM-0941, now
     scoped to these legs only].
   - **Multiplicity:** one enumerated Holm family per claim across the named
     contrast set; every integer boundary derived by analytic inversion and
     pinned before any scored run. Power for the paired legs is sized by
     P3-D-POWER at prereg; a slice that cannot support the +5/2-pt margins is
     enlarged BEFORE freeze or the experiment does not freeze (RAGC §8.4's
     rule, adopted).
2. **Parity accounting.** G4 adopts the FRONT/RAGC registered mechanics — the
   T_k resource-vector meter over a closed arm table, the five matched-
   retrieval rules, retrieved-token caps, index bytes charged
   [STIPULATED: ASM-1006, adopting ASM-0852/ASM-0853]. Rev 2 instantiates
   (not merely cites) the FRONT §5 Rule-2 cells and the rest of the
   KOT-FAIR/2 manifest at §6.1 [PROPOSED-ASM: ASM-1036]. The
   no-published-precedent warning stands: no bytes-honest published
   small-model retrieval win exists to copy, so this ledger is constructed,
   not cited [ref: docs/next/lit/RAG.md §1 synthesis + §3 (internal
   lit-review)].
3. **Missing misaligned-store control.** House discipline (the f2b
   derangement lesson) requires the cheap control that shows the FACTS are
   load-bearing, not the store's shape: a seed-pinned shuffled/deranged fact
   table behind the identical CODEVERT stack, expected to collapse to
   abstention/errors. Near-zero cost; in the G4 arm table (§7-G4) and in G2
   as a smoke variant [STIPULATED: ASM-1006].
4. **Duplication against the already-designed NLB instrument.** Unchanged
   from rev 1: **unify** — CODEVERT's front-end IS NLB-FE/1 on the code
   vertical (same kot-query-code/1 IR, same Tier-0 repair, same acceptance
   layer with evidence-gated sets, same five-role data separation and freeze
   ordering); G2 below is the ONE merged pilot; the registered G-NLB code
   gate is CODEVERT's G3, not a rival bar. The only CODEVERT-specific
   front-end deltas are the two edit-contract intents (deferred to G5) and
   the clarification renderer [STIPULATED: ASM-1001; ASM-1005].
5. **Gate-bar reconciliation.** G2 screens on the pilot bar; G3 = G-NLB
   decides parser clearance; G4's binding win is the §4.2(1) paired
   machinery on the §7-G4 arm table. No number from a lower rung is ever
   quoted against a higher rung's bar; no lower rung's point estimate is
   ever quoted as evidence at all (§7-G2 status line)
   [STIPULATED: ASM-1005; PROPOSED-ASM: ASM-1039].

**4.3 Cheap-first: yes, with the ordering corrected and honestly labelled.**
The census (G1, rebuilt) is cheaper than the pilot and can kill the
full-distribution product claim outright; it still goes first — but it is no
longer "~$0": query-level gold adjudication is real annotation spend (§7-G1,
repriced). The extractor engineering spike (G0) precedes it and is the only
work the review authorizes before this revision lands. The aligned-generic
substrate reuse stands within its corrected scope: DECONF-A2 builds GS-C and
validates the executor; G2 reuses that artifact rather than building a second
generic executor [STIPULATED: ASM-0963 reused; PROPOSED-ASM: ASM-1032].

---

## 5. Stress test 4 — the biggest failure mode

GPT-5.6 names **agreement laundering** (the emitted set omits the correct
interpretation and the wrong members agree; the executor certifies the wrong
question) and, strategically, **attribution collapse** (the generic store
matches everything). Both are right and both are wired above: laundering is
bounded by evidence-gated sets + both-orientation strata with near-zero
allowances + blind semantic gold (and §2.4's empty-denotation subclass is
disclosed as the residual); collapse is screened early (G2's GEN-EXEC/TOOL-NL
arms, signal-grade) and decided at G4 (paired NI machinery, evidence-grade)
[PROPOSED-ASM: ASM-1032/1034].

The failure mode GPT-5.6's ORIGINAL proposal under-weighted — the chief
architect's addition, unchanged in substance from rev 1:

- LOAD-BEARING: **a full CODEVERT win is kernel-free.** Nothing in CODEVERT
  v1 consumes NSM semantics, explications, the encoder, or any kernel-authored
  content: the substrate is deterministically extracted structural fact
  records (the a5 world is already structural-not-NSM by its own registered
  assumption), the front-end is a semantic parser, the executor is the
  engine's desugaring layer. Even the a5-llm PASS's own assessment says
  nothing there distinguishes the kot-axiom kernel from ANY typed store +
  checker [MEASURED: registry/assessments/a5-llm.json does_not_license,
  restated per docs/next/feasibility-synthesis.md §1; the a5 structural
  caveat is ASM-0007]. Therefore CODEVERT's entire licence space is an
  **architecture-family claim** (calibrated contract front-end +
  ambiguity-set execution + exact substrate beats matched RAG/tool at equal
  risk) — the H-PS shape of Programme-3 — and NEVER a kernel-content claim;
  kernel-content value lives with knull-v2 / A-F0 / the f2b-transfer line
  and is untouched by any CODEVERT outcome in either direction. The
  `instance-of(symbol, concept)` family is the single seam where kernel
  concept content could later enter (linking code symbols to kernel
  concepts); it is kept in the task mix with its own stratum so that seam
  stays measurable, but no G1–G5 rung claims it [STIPULATED: ASM-1000].

Two further named risks, with rev-2-hardened counters: the
**clarification-rate pathology** (a set-happy system converts coverage into
clarifications and wins a metric while losing the product) — rev 1 named it
but priced no gate; now countered NUMERICALLY by the §3.1 caps + the
clarification-adjusted utility endpoint + charging the turn in KOT-COST/2
[PROPOSED-ASM: ASM-1033]; and **κ-collapse on real repos** (dynamic-Python
idioms drive `unknown` mass so high that the full product distribution is
mostly unanswerable, making every arm's coverage number small and the +5-pt
contrast unpowered) — countered by G1-before-everything with the rebuilt
extractor-independent census and its registered floor, which can no longer be
satisfied by conditioning on successful extraction
[PROPOSED-ASM: ASM-1030].

---

## 6. CODEVERT/1 — the synthesised buildable design

One paragraph of shape, then deltas from CASK-CODE/1:

Pinned repo commit → deterministic conservative extractor (the PY-STAT/1
enumerated static subset; ast + symtable + pinned import resolver;
proved/disproved/unknown/conflict with candidate-name sets on unknown edges;
byte-span provenance; reuses the measured code-world schema + engine,
extended by the extractor) → SQLite + generic-Datalog serializations of the
SAME facts produced alongside (attribution controls by construction) →
**NLB-FE/1 as the front-end** (repaired µs Tier-0; 110–360M intent+slot
Tier-1 under exact product-automaton grammar masks; trie-constrained
entities; evidence-gated ambiguity set ≤8; NLB §6 threshold protocol with its
at-freeze score-class selection; frozen τ by fixed-sequence risk-controlled
selection on CAL-B) → contract-and-contrast execution (agreement → templated
ANSWER with provenance; disagreement → deterministic CLARIFY, one charged
turn under the §3.1 numeric budget; else ABSTAIN with reason code; inverse/
exhaustive queries subject to the §2.2 completeness precondition, else
UNKNOWN-INCOMPLETE) → v1 edits as deterministic transforms with mechanical
certificates (rename confined to RENAME-SAFE/1 with the H1–H8 hazard scan;
insert_import per the §2.5 pinned semantics); generative edits + verify-retry
deferred. Output contract: ANSWER(value, provenance) / PATCH(diff,
certificate) / CLARIFY(2–3 choices) / ABSTAIN(reason) /
UNKNOWN-INCOMPLETE(partial, blocking_count). Everything inside the measured
system; the full KOT-FAIR/2 manifest of §6.1 applies; no API-hosted component
eligible [STIPULATED: ASM-1001; ASM-1002; ASM-1003; PROPOSED-ASM:
ASM-1031/1033/1036/1037].

### 6.1 The KOT-FAIR/2 manifest, instantiated (rev 2 — the review's "partially slotted" finding closed)

Every item below is a binding obligation on the G4 prereg (and, where marked,
on G2); each is a design choice [PROPOSED-ASM: ASM-1036] consuming the named
programme instrument. Rev 1 cited these frameworks; rev 2 instantiates them:

1. **B_k and the closed comparator set F(B_k).** G4 runs at ONE pinned rung:
   B_k = {bytes_max = 1.0 GB canonically-packed artifact (NLB's registered
   ceiling, ASM-0946); latency: Tier-1 warm p95 ≤ 500 ms CPU; tuning
   allowance T_k per arm per the FRONT §3.3 resource-vector meter (GPU-h +
   CPU-core-h logged per arm-table key into KOT-LIFE/1)}. F(B_k) = EXACTLY
   the eight arms of the §7-G4 table, closed at prereg freeze; comparator
   additions only via FRONT's nomination window + challenger gate. Every arm
   — including GEN-EXEC, TOOL-NL, and the deranged control — carries the
   complete measurement contract below (RAGC §8.1's rule: build-ledger rows
   alone do not satisfy it, ASM-0951 adopted).
2. **KOT-SIZE/2, all six figures, per arm:** (1) canonically-packed minimal
   artifact bytes via the ONE canonical packing script; (2) compressed
   distribution bytes; (3) warm RAM/VRAM peak; (4) cold-start working set +
   bytes read; (5) construction size + cost (extractor output, indexes, tool
   schemas — feeds KOT-LIFE/1); (6) remote dependencies — NONE are eligible
   (the API-parser ineligibility rule generalized: any remote service, cache,
   or corpus dependency voids the smaller-deployment claim; CODEVERT and all
   controls run fully local). **Frozen base image:** all arms measured inside
   the SAME content-hashed base image, frozen before any G4 artifact is
   built; store hashes pinned at eval time (no post-measurement growth).
3. **KOT-COST/2, the full measured vector per arm, warm AND cold, on the
   P3-D-HW pinned rig:** accelerator time + estimated ops; CPU-seconds; bytes
   read (storage + network — network must be zero per item 2); energy (RAPL
   on CPU, reported-or-MISSING never modeled, per the FRONT §1.1 boundary
   rule); peak accelerator memory + host RSS; I/O; latency percentiles
   (p50/p95, TTFT where streaming applies) warm and cold; throughput under
   the pinned concurrency distribution; output-length control (pinned
   max-token + stop discipline); **and the clarification-turn cost**: each
   charged CLARIFY turn's tokens/latency/energy booked to the arm that
   emitted it. Symbolic computation (extractor, engine, SQL execution) enters
   the vector at its measured CPU/I-O/energy cost — never at zero.
4. **KOT-LIFE/1 lifecycle ledger, per arm:** repo-snapshot curation hours;
   extractor build + run compute; index/store construction compute and
   artifact bytes (booked to SIZE figures (1)/(5) identically on every arm —
   FRONT Rule 5); task authoring hours; phrasing-sourcing hours; annotation +
   external-adjudication hours (the dominant line — §7 repricing); per-arm
   tuning meter (T_k actuals); amortization of build+authoring against
   measured per-query KOT-COST/2 at 10^3 / 10^6 / 10^9 queries. No common
   unit is fabricated; hours and compute are co-reported (the ledger's
   no-fudged-exchange-rate rule).
5. **Sealed evaluation + construction-leakage/decontamination protocol:**
   (a) evaluation repos are frozen and hash-pinned BEFORE task authoring and
   are disjoint from anything any front-end or tool-arm trains, tunes, or
   calibrates on (five-role separation inherited from NLB); (b) every
   derivation/construction pipeline (extractor, census generator, index
   builders, tool-schema generator, synthetic-training generator) is
   content-hashed and frozen BEFORE any frozen-suite item is drawn; a store
   or index whose construction post-dates suite exposure is VOID for the
   binding claim (FRONT Rule 5 verbatim); (c) the programme decontamination
   screen runs over every arm's derived objects AND construction inputs
   identically; (d) blind phrasing authors and adjudicators never see
   extractor output or any arm's responses at authoring time; (e) the sealed
   production protocol governs EVAL-item handling from authoring to scoring
   (no EVAL item touches any tuning loop).
6. **FRONT §5 Rule-2 cells, instantiated (not merely cited):** the
   **SHARED/MATCHED cell** = one pinned retriever pair (BM25 + one pinned
   small dense embedder) over a common text serialization of every arm's
   objects at the same budgets — a REQUIRED member of the control set; claim
   licence: content-representation attribution at fixed retrieval. The
   **NATIVE cell** = each arm retrieving/addressing the way its architecture
   natively does (CODEVERT's contract execution; TOOL-NL's function calls;
   the RAG arms' own retrieval) — additional frontier points; claim licence:
   "the best each architecture can do at the budget". Both cells appear in
   the §7-G4 arm table; every sentence in any G4 verdict names its licensing
   cell. Retrieved-token caps, context ordering = retrieval-score-descending,
   and the position-shuffle control follow FRONT Rule 3.

Deltas from CASK-CODE/1, complete list (rev-1 deltas 1–10 retained, rev-2
deltas 11–17 added):

| # | CASK-CODE/1 | CODEVERT/1 | Why |
|---|---|---|---|
| 1 | mandatory typed-inverse in every directional set | evidence-gated orientation-cue semantics (ASM-0940) | §2.4 — CASK re-imports the rejected NLB rev-1 defect |
| 2 | neural span-draft + verify-retry for v1 edits | v1 edits are deterministic transforms; verify-retry deferred to a generative G5b contract | §2.5 — v1 edit workload is fully mechanical |
| 3 | (absent) | rename fail-closed on `unknown` references in the closure | §2.5 — Python rename is not statically certifiable in general |
| 4 | new pilot parser + corpus | front-end := NLB-FE/1; ONE merged pilot (G2 = NLB-0-B(code) + arms) | §4.2(4) — no duplicate scaffolding |
| 5 | unspecified interval statistics | split statistics: paired cluster bootstrap/TOST for contrasts, cluster-CP for rare-event legs (rev 2) | §4.2(1) |
| 6 | "same tuning allowance" (unmetered) | T_k arm-table meter + FRONT §5 matched-retrieval rules (ASM-0852/0853) | §4.2(2) |
| 7 | (absent) | shuffled/deranged-store control arm | §4.2(3) — house derangement discipline |
| 8 | pilot before any repo-coverage measurement | G1 census first, kill floor registered | §4.3 / §5 |
| 9 | (implicit) | licence space pinned to architecture-family; kernel-content explicitly out | §5 |
| 10 | (absent) | clarification-rate gated co-report | §5 |
| 11 | κ over queries "over extracted symbols" | extractor-INDEPENDENT query universe; query-level recall/completeness + negative-answer validity; independence pin on task sampling | rev-2 review ranked 1 (§7-G1) |
| 12 | generic-store arm ambiguous at the NL boundary | two pinned NL-valid controls: GEN-EXEC + TOOL-NL; DECONF-A2 = executor validation only; no gold SQL anywhere | rev-2 review ranked 2 (§4.1) |
| 13 | pilot billed as cheap decisive falsifier | "cheap decisive test" withdrawn; G2 = non-decisive screen; decisive evidence only at G4 | rev-2 review ranked 3 (§4.1, §7-G2) |
| 14 | (absent) | numeric clarification caps + clarification-adjusted utility U | rev-2 review ranked 3 (§3.1) |
| 15 | extractor described as a general resolver | PY-STAT/1 enumerated static subset; `unknown` candidate-name propagation; UNKNOWN-INCOMPLETE for inverse/exhaustive queries | rev-2 review technical gaps (§2.2) |
| 16 | "plausibly naming it" admissibility | RENAME-SAFE/1 closed subset + finite H1–H8 hazard inventory; insert_import semantics pinned; certificate scope = observed mechanical behaviour | rev-2 review technical gaps (§2.5) |
| 17 | $100–300 corpus estimate | repriced honestly against the annotation binding-resource finding; MEASURED-vs-ESTIMATED tags mandatory | rev-2 review (§7-G4 envelope) |

Kept from CASK-CODE/1 unchanged: the product boundary (8 measured query
families + 2 bounded edits, no free-form generation), the two-interface seam
rule, the four-state substrate with certificates, the conservative extraction
policy with blind precision annotation, the deterministic answer/clarify
templates (no free-form renderer), the clarification evaluation protocol
(§3.1 runtime rules), the full-distribution + κ reporting rule, the binding-
win conditions (re-based on the §4.2(1) statistics and the §7-G4 arm table),
the 2-pt GENERIC-store attribution-collapse kill, the size ladder (110M
preferred first build; 2B admissible but efficiency-rationale-eroding), and
the honest "stop if generic matches" strategic clause [STIPULATED: ASM-1002;
ASM-1003; ASM-1006].

---

## 7. The experiment ladder (cheapest falsifier first)

All costs are planning estimates, [ESTIMATED] throughout [STIPULATED:
ASM-1004/1005/1006 as amended; PROPOSED-ASM: ASM-1030/1038/1039]. Per the
review-gate ruling: **only G0 may start now**; G1/G2/G4 do not run or freeze
until this revision is externally accepted.

**G0 — NON-SCORED extractor engineering spike (authorized now).** Build
PY-STAT/1 (the enumerated construct inventory, candidate-name `unknown`
propagation, four-state facts, byte-span provenance, SQLite +
generic-Datalog twin serializations) + the census tooling of G1. No scored
output, no κ number is quoted from spike runs; the spike's deliverables are
content-hashed code + the frozen construct inventory. Keep OUT of encoder/;
poc/-side harness code [PROPOSED-ASM: ASM-1031].

**G1 — real-repo extraction census, REBUILT (CPU + real annotation).**
Rev 1's universe ("all 8 families over extracted symbols") is withdrawn as
circular — it conditioned on successful extraction (review, ranked concern
1). Rebuilt design [PROPOSED-ASM: ASM-1030, superseding ASM-1004's census
definition; the ASM-1004 repo-selection pin and floor discipline survive]:

- **Repo rule (unchanged):** pinned BEFORE looking; 20–30 permissively-
  licensed Python repos in a pinned size band, disjoint from anything any
  front-end or tool arm trains/tunes/calibrates on.
- **Extractor-independent query universe:** a content-hashed, seed-pinned
  **census generator whose only input is raw repo bytes** — it enumerates
  query targets from a purely SYNTACTIC identifier census (every def/class/
  assignment name, every attribute-access name, every import-statement
  target, every module file), with NO name resolution and NO access to
  extractor output. The generator is frozen (hash-pinned) before the
  extractor runs on the selected repos. Queries are instantiated per family
  over census entries, stratified per family × repo, seed-pinned sampling.
  Task sampling at G4 draws from the same census procedure (fresh seed,
  held-out repos) — the independence pin of §3.2.
- **Endpoints (all query-level, on a blind two-annotator adjudicated
  sample):**
  1. **completeness/recall R_q** — fraction of gold-answerable sampled
     queries whose FULL adjudicated gold answer set is returned with status
     `proved`;
  2. **precision** — fraction of `proved` answer elements that are correct
     (subsumes and extends the 150-fact check);
  3. **negative-answer validity** — fraction of gold-EMPTY sampled queries
     answered `proved`-empty under the §2.2 completeness precondition
     (a silent or wrong non-empty answer fails; UNKNOWN-INCOMPLETE is
     honest-but-uncovered);
  4. **κ_q^indep** — fraction of the FULL mechanically-enumerated
     independent census answerable fully-`proved` (the coverage headline,
     now over the unbiased denominator);
  5. **soundness probe (dynamic traces, where pinned test suites exist):**
     run each repo's own test suite under a pinned import/call tracer;
     every OBSERVED call/import edge must appear in `proved` ∪ `unknown` —
     an observed edge absent from both is an extractor SOUNDNESS bug (fix +
     re-run the census once; a recurrence after the fix = kill). Observed
     edges landing in `unknown` are honest incompleteness and simply count
     against R_q/κ_q^indep.
- **KILL (registered planning floors, [ESTIMATED], maintainer-adjustable at
  prereg):** κ_q^indep < 0.5 on the pinned pool, or query-level completeness
  R_q < 0.90 on the adjudicated sample, or precision < 0.95, or
  negative-answer validity < 0.90, or a post-fix soundness recurrence — any
  one kills the full-distribution product claim before any model exists; the
  direction survives only re-scoped (covered-slice tool, not product).
- **Cost honesty [ESTIMATED; PROPOSED-ASM: ASM-1038]:** compute ~$0 (CPU),
  but adjudicating query-LEVEL gold (a callers-of gold set is a whole-repo
  judgement, not a fact check) is real spend: ~200 sampled queries × 2
  annotators at ~10–20 min each ≈ **70–130 annotator-hours**. Rev 1's "~$0 +
  the smallest honest annotation" is withdrawn. This is the smallest honest
  price of a non-circular census; there is no cheaper valid version.

**G2 — the merged mechanism pilot (≤5 GPU-h free pool + ~$25 API compute;
[ESTIMATED]) — a NON-DECISIVE SCREEN, stated in its own header.** G2 inherits
NLB-0's instrument, which describes ITSELF as a screen, not a decisive
experiment (NLB §7 / ASM-0944: K=1 legacy corpora, public outcomes,
point-estimate reads, acceptance layer absent) — so no G2 outcome, including
its generic-store legs, is ever quoted as decisive evidence; its thresholds
are STOP-SIGNALS that route to redesign and spending decisions
[PROPOSED-ASM: ASM-1039, hardening ASM-1005]. Content: NLB-0-B on the code
vertical, absorbed and extended — ONE pilot, one parser, one training
pipeline: synthetic-only training (ASM-0947(6) recipe); frozen pilot
operating point; evaluated once on the legacy 855-query K=1 blind corpus
(labelled diagnostic — outcomes public) PLUS ~300 fresh blind phrasings from
two disjoint author sources; arms: (i) CODEVERT-top1, (ii) evidence-gated
ambiguity-set + scripted clarification under the §3.1 numeric caps, (iii)
**GEN-EXEC** (identical front-end → GS-C generic executor via the pinned
mapping; GS-C built by / shared with DECONF-A2, ASM-0963, consumed as
executor-validation), (iv) **TOOL-NL** at pilot strength (built under the
FRONT/1 pipeline + RAGC §2.4 anti-weak-control counters, T_k-metered;
disclosed as a pilot-strength build — its G4 incarnation is rebuilt at full
T_k), (v) shuffled-store smoke variant. STOP-SIGNALS (point thresholds,
exact where n permits): no operating point with ≥0.80 completed-task
coverage at point dangerous-error ≤1%; correct DSL absent from the emitted
set on >10% of answerable items; set-execution < +5 pts completed coverage
over top-1 at matched risk; systematic directional inversion in any supported
stratum; either generic arm within 2 pts at the same risk and resource cap
(= early attribution-collapse SIGNAL at pilot scope — a routing input to the
G4 go/no-go, never an attribution finding); clarification-cap violation on
the pre-annotated unambiguous stratum. Its numbers are neither floors nor
ceilings for G3/G4 and bind nothing [STIPULATED: ASM-1005, adopting
ASM-0944; PROPOSED-ASM: ASM-1032/1033/1039].

**G3 — the registered gate (not a new experiment) — decisive about the
PARSER only.** P3-E-NLB-1 on the code vertical, exactly as designed: G-NLB
retention LB95 ≥ 0.90 jointly with unconditional dangerous-wrong UB95 < 0.02,
K=3 blind phrasings, five-role separation, directional-stratum kills
[STIPULATED: ASM-0901/0940–0947, consumed as-is]. Honesty line (review,
accepted): G3 decisively tests whether the NL front-end clears the
entry-instrument bar; it says NOTHING about whether CODEVERT beats a generic
store/tool system — that question has exactly one decisive rung, G4. CODEVERT
adds nothing to the gate and quotes nothing over it; a code-vertical PASS
unblocks G4's NL legs under ASM-0814/0945.

**G4 — the matched end-to-end comparison (query-only; the expensive rung;
the ONLY decisive distinctive-architecture test; prereg DEFERRED until G2 GO
+ G1 floor + external acceptance of this revision, per the steering's
scaffolding freeze).** 20–30 held-out repos frozen before task authoring;
~1,200 base tasks × 3 independently-sourced phrasings (task targets sampled
via the §7-G1 census procedure, fresh seed — the independence pin); gold =
blind, repo-disjoint authoring + external adjudication (the §3.4 insurance).

- **Denominator, made consistent (review: rev 1 contradicted itself):** G4
  scores the **query-product distribution** — the 70/15 query share of the
  70/15/15 product model, renormalized: **82.4% relational / 17.6%
  ambiguous-or-unanswerable** ([ESTIMATED] workload model, STIPULATED not
  measured). The 15% edit share is NOT reallocated and NOT scored at G4; it
  is explicitly disclosed as unscored, and the FULL-product-distribution
  claim is available only after G5 completes the edit share. Every G4
  sentence is licensed over the query-product denominator only
  [PROPOSED-ASM: ASM-1035].
- **The single G4 arm table (exactly eight arms = the closed F(B_k); this
  table supersedes every earlier arm enumeration in this document's history)
  [PROPOSED-ASM: ASM-1035]:**

| Arm | Description | FRONT §5 cell | Licence |
|---|---|---|---|
| A1 R0 | no-store generator baseline | — | floor |
| A2 RAG-BM25 | pinned BM25 over the common text serialization | SHARED/MATCHED | content-representation attribution at fixed retrieval |
| A3 RAG-dense | pinned small dense embedder, same serialization/budgets | SHARED/MATCHED | ditto |
| A4 TOOL-NL | strong native NL tool-use over GS-C JSON tools, FRONT-built, T_k-tuned | NATIVE | best in-budget native NL tool system |
| A5 GEN-EXEC | identical NLB-FE/1 front-end → pinned contract→SQL mapping → GS-C | NATIVE (executor axis) | substrate/executor attribution at fixed NL entry |
| A6 CODEVERT-top1 | full stack, singleton contract only | NATIVE | mechanism-ablation reference |
| A7 CODEVERT-set | full stack, evidence-gated set + clarification | NATIVE | the system under test |
| A8 DERANGED | seed-pinned deranged fact store behind the identical A7 stack | control | facts-are-load-bearing check |

  Retry arms (CASK's GENERIC-retry / CASK-set+retry) are REMOVED from G4 —
  v1's query path samples nothing and has no verify-retry loop to price;
  they are deferred to G5b where a verify-retry loop actually exists. The
  product denominator × arm table gives 3,600 phrasings × 8 arms scored
  runs, compute-cheap (CPU executor + ≤360M parsers), annotation-expensive.
- **Binding win (paired machinery of §4.2(1)):** LCB95(paired Δ on the
  clarification-adjusted utility U) ≥ +5 pts for A7 vs the pre-named
  strongest baseline (max of A2–A5 on the dev-split, named at freeze), at
  UB95 dangerous-error < 0.02 (cluster-CP), clarification caps respected,
  both-orientation strata clean. **Death condition:** A5 or A4 within the
  2-pt paired TOST/NI band ⇒ attribution collapse = the measured input to
  K-P3v2(4) at this scope. Underpowered ⇒ INCONCLUSIVE, no sentence either
  way. Every sentence names its licensing cell (§6.1 item 6).
- **Cost honesty, repriced [ESTIMATED; PROPOSED-ASM: ASM-1038]:** rev 1's
  "$100–300" is WITHDRAWN as materially underpriced — it contradicted the
  programme's own measured finding that human annotation is the binding
  resource [MEASURED: docs/next/feasibility-synthesis.md §6]. Honest
  planning envelope: 3,600 independently-sourced phrasings (two external
  author sources + one designer source), per-item intended-reading +
  answerability annotation, and external blind adjudication of task gold ≈
  **400–900 annotator/adjudicator-hours** (order **$8k–25k** at market
  rates, or the equivalent internal annotation-queue allocation — the queue
  is the same one every other programme line competes for). Compute stays in
  the ≤50 GPU-h free-pool class [ESTIMATED]. The spend decision is a
  maintainer call AT G4 prereg, priced by this honest figure, never by
  rev 1's.

**G5 — edits (design-track; exists only if G4 survives).** G5a: the two
mechanical edit contracts on the RENAME-SAFE/1 subset with the H1–H8 hazard
inventory and pinned insert_import semantics (endpoints: edit success
non-inferiority vs the strongest generic edit baseline, zero
unauthorized-span edits, certificate validity, hazard-scan false-negative
audit on a blind sample). G5b: ONE genuinely generative edit contract with
the CASK verify-retry loop vs matched generic verify-retry — the deferred
retry arms re-enter HERE (CASK condition 7: non-inferior accuracy/safety + a
material win on tokens, p95, or energy) [STIPULATED: ASM-1007 as amended by
PROPOSED-ASM: ASM-1037].

Decision economics, honestly restated: G1 (~70–130 annotation-hours) can
kill the domain; G2 (~$25 + 5 GPU-h) is a screen that can stop all further
spend and previews — as signal, not evidence — attribution collapse; G3
gates the parser; only G4 (the expensive rung) can DECIDE the distinctive
claim, and only after its honest annotation price is accepted. No rung is
billed as both cheap and decisive [PROPOSED-ASM: ASM-1038/1039].

---

## 8. Beads this design spawns (recommendation — the coordinator creates them; no bd operation is performed by this document)

```
P3-T-CODEVERT-XT [task, P1]  G0 NON-SCORED extractor engineering spike
    (authorized by the 2026-07-11 review): PY-STAT/1 enumerated-subset
    extractor (construct inventory content-hashed; candidate-name unknown
    propagation; 4-state facts; byte-span provenance; SQLite +
    generic-Datalog twin serializations; reuse the a5 code-world schema and
    engine desugaring) + the seed-pinned extractor-INDEPENDENT census
    generator (raw-bytes-only input, frozen before extraction). No scored
    output. Keep OUT of encoder/; poc/-side harness code. From CODEVERT.md
    rev 2 §2.2/§7-G0/G1 (ASM-1003/1031/1030).
P3-E-CODEVERT-G1 [task, P1, BLOCKED on rev-2 external acceptance]  Rebuilt
    real-repo census: pinned repo rule; extractor-independent universe;
    query-level completeness/precision/negative-answer-validity + κ_q^indep
    + dynamic-trace soundness probe; registered kill floors; honest
    annotation budget (~70–130 h). Blocked-by: P3-T-CODEVERT-XT + review
    acceptance. (ASM-1030/1038.)
P3-E-CODEVERT-G2 [task, P0, BLOCKED on rev-2 external acceptance]  The
    MERGED code-vertical mechanism pilot — a NON-DECISIVE SCREEN: NLB-0-B
    (code) absorbed + ambiguity-set arm + GEN-EXEC (GS-C shared with
    DECONF-A2, executor-validation scope) + pilot-strength TOOL-NL +
    shuffled-store smoke + ~300 fresh blind phrasings; stop-signal set under
    ASM-1005/1032/1033/1039. Blocked-by: P3-E-DECONF-0 (GS-C artifact) and
    the NLB-0-A ROLE_DIR repair leg; coordinates with (and supersedes any
    separate) NLB-0-B code pilot.
P3-D-CODEVERT-G4 [task, P2, DEFERRED]  Prereg the matched end-to-end
    query-only comparison per §7-G4: eight-arm closed table, query-product
    denominator, paired cluster-level superiority/NI statistics, numeric
    clarification budget, full §6.1 KOT-FAIR/2 manifest, honest annotation
    pricing for the maintainer spend decision. Blocked-by: P3-E-CODEVERT-G2
    GO + P3-E-CODEVERT-G1 floor + G3 + external review of this doc; per the
    round-1 steering freeze it is NOT designed further until G2 reads out.
    (ASM-1033/1034/1035/1036/1038.)
P3-D-CODEVERT-EDIT [task, P3, DEFERRED]  Edit-contract design (mechanical
    G5a on RENAME-SAFE/1 + H1–H8; generative G5b verify-retry) per
    ASM-1007/1037. Blocked-by: P3-D-CODEVERT-G4 outcome.
Dependency edges: G1 ← XT; G2 ← {DECONF-0, NLB-0-A}; G4 ← {G1, G2, G3=
    P3-E-NLB-1(code)}; EDIT ← G4. ALL of G1/G2/G4 ← rev-2 external
    acceptance of this document.
```

---

## 9. Honest limits of this synthesis

1. **Every feasibility number for the front-end is a band, not a clearance**
   — all retention/coverage projections are [ESTIMATED]; the projection that
   G2's bars are reachable is EXTRAPOLATION ASM-1008, never a premise; the
   literature does not guarantee the joint 0.90-retention/S2 bar; the
   K-P3v2(2) negative branch (checker stays an internal instrument; the
   surviving programme is formal/code interfaces and compression diagnostics)
   remains a legitimate pre-agreed outcome.
2. **A CODEVERT win, if it ever lands, is an architecture-family result** on
   a stipulated workload model over backward-authored phrasings — not
   kernel-content evidence, not natural-traffic evidence, not a general-index
   W1 (the vertical fork is the steering's own re-scope). And at G4 it is a
   QUERY-PRODUCT claim only; the full-product claim waits on G5.
3. **κ and the product distribution are the soft underbelly**: the G1 floors
   are stipulated planning values; the 70/15/15 mix (and its 82.4/17.6
   query-product renormalization) is a workload model. Both are
   maintainer-visible knobs and both are disclosed on every readout. The
   census is now extractor-independent, but its syntactic identifier census
   is still a CONSTRUCTED universe — it enumerates what is syntactically
   visible, not what developers actually ask; that residual is disclosed,
   not solved.
4. **The generic controls must be strong to mean anything** — an under-built
   TOOL-NL or GEN-EXEC fakes the distinctive win; the counters are RAGC
   §2.4's anti-weak-control rules (same T_k meter, harness defaults,
   nomination/challenger gates, published build logs) inherited at every
   rung, plus FRONT's weak-builder counters at G4. The symmetric risk — an
   under-tuned CODEVERT faking a collapse — is priced by the same metered
   parity.
5. **G2 is a screen, and nothing more, anywhere in this document.** Legacy-
   corpus reuse is disclosed post-outcome analysis; K=1; pilot numbers bind
   nothing at G3/G4 and are never quoted as attribution evidence.
6. **Agreement laundering is reduced, not eliminated** — the residual (novel
   systematic inversion a cue inventory does not enumerate; the
   empty-denotation agreement subclass) is carried verbatim on any PASS,
   with the directional-stratum kills as the only in-gate catch.
7. **The edit path is design-track only** — RENAME-SAFE/1 and the hazard
   inventory are specifications, not validated instruments; the hazard scan's
   own false-negative rate is unmeasured until G5a's blind audit.
8. **No cheap decisive test exists.** The ladder's cheap rungs kill; only
   its expensive rung decides. Any summary of this design that claims
   otherwise misstates it [PROPOSED-ASM: ASM-1039].

---

## 10. Assumption entries

### 10.1 Registered (rev 1, in registry/assumptions.jsonl): ASM-1000–1008

| Registered id | Scope | Rev-2 status |
|---|---|---|
| **ASM-1000** | licence space = architecture-family claims only, kernel-content out; instance-of stratum as future seam; steering-freeze compliance | unchanged |
| **ASM-1001** | front-end := NLB-FE/1; evidence-gated sets (ASM-0940/0941/0946) | amended: score class fully deferred to NLB §6/ASM-0943 at-freeze selection (§2.4) |
| **ASM-1002** | product boundary + I/O contract; clarification protocol; workload model stipulated | amended: numeric clarification budget added (ASM-1033); UNKNOWN-INCOMPLETE added to the output contract |
| **ASM-1003** | conservative 4-state extractor; twin serializations; full-distribution scoring, κ disclosed | amended: executable unknown-propagation semantics (ASM-1031) |
| **ASM-1004** | G1 census: repo rule, floors | census DEFINITION superseded by ASM-1030 (extractor-independent universe, query-level endpoints); repo rule + floor discipline survive |
| **ASM-1005** | G2 merged pilot; gate-bar ordering | amended: arms re-pinned (ASM-1032), non-decisive status hardened (ASM-1039), caps added (ASM-1033) |
| **ASM-1006** | G4 commitments | amended: statistics split (ASM-1034), single arm table + denominator (ASM-1035), manifest (ASM-1036), cost repricing (ASM-1038) |
| **ASM-1007** | edit path: deterministic v1, deferred verify-retry | amended: admissibility clause superseded by ASM-1037 (RENAME-SAFE/1 + H1–H8; insert_import semantics; certificate scope) |
| **ASM-1008** | EXTRAPOLATION: κ and screen bars reachable | unchanged; explicitly covers the parser-retention projections as ESTIMATED, never premises |

### 10.2 PROPOSED-ASM (rev 2; block ASM-1030–1039, DISJOINT from all prior blocks per the coordinator's instruction; NOT registered by this document — the coordinator registers them; entries 1009–1029 of this bead's original block remain deliberately unused)

| Proposed id | Scope |
|---|---|
| **ASM-1030** | G1 rebuilt: extractor-INDEPENDENT query universe (seed-pinned census generator over raw repo bytes only, frozen before extraction); query-level completeness/recall, precision, negative-answer validity, κ_q^indep, dynamic-trace soundness probe; kill floors (κ_q^indep ≥ 0.5, R_q ≥ 0.90, precision ≥ 0.95, neg-validity ≥ 0.90, soundness); independence pin extends to G4 task sampling (§3.2, §7-G1) |
| **ASM-1031** | Extractor scope: PY-STAT/1 enumerated static subset, content-hashed construct inventory; candidate-name sets on `unknown` edges; completeness-precondition semantics + UNKNOWN-INCOMPLETE for inverse/exhaustive and negative answers (§2.2, §7-G0) |
| **ASM-1032** | The two NL-valid generic controls: GEN-EXEC (identical front-end → pinned contract→SQL mapping → GS-C) and TOOL-NL (FRONT-built native NL tool-use, anti-weak-control rules); no gold SQL/formal contract in any control arm at any rung; DECONF-A2 re-scoped to executor validation only (§4.1, §7-G2/G4) |
| **ASM-1033** | Numeric clarification budget: rate caps (≤0.05 on annotated-unambiguous, ≤0.20 overall; planning values) as instrument-validity gates voiding coverage wins; clarification-adjusted utility U with pinned λ=0.25 planning discount as the G4 primary; turn cost charged in KOT-COST/2 (§3.1, §7-G4) |
| **ASM-1034** | G4 statistics split: paired cluster-level hierarchical bootstrap (programme §2.5) for superiority LCB95(ΔU) ≥ +5; paired cluster TOST/NI for the 2-pt generic margins; cluster-CP retained for single-arm rare-event legs only; enumerated Holm family; underpowered → INCONCLUSIVE, no attribution sentence (§4.2(1)) |
| **ASM-1035** | The single G4 arm table (A1–A8, closed F(B_k)); retry arms removed from G4, deferred to G5b; query-product denominator 82.4/17.6 (renormalized 70/15), edit share unscored at G4 and disclosed; full-product claim deferred behind G5 (§7-G4) |
| **ASM-1036** | KOT-FAIR/2 manifest instantiated: B_k + closed F(B_k); KOT-SIZE/2 six figures + frozen base image + no-remote-dependency rule; full KOT-COST/2 vector incl. clarification-turn cost, warm/cold, P3-D-HW rig; KOT-LIFE/1 ledger incl. authoring/annotation hours + amortization; sealed-eval + construction-leakage/decontamination protocol; FRONT §5 shared/matched AND native cells instantiated with per-sentence licences (§6.1) |
| **ASM-1037** | Edit path re-scope: rename confined to RENAME-SAFE/1 (syntactically closed subset); "plausibly" replaced by the finite pinned hazard inventory H1–H8; insert_import placement/collision/__future__/conditional-import/no-formatter/applicability semantics pinned; certificates certify observed mechanical behaviour only; edit path design-track until G4 (§2.5, §7-G5) |
| **ASM-1038** | Honest cost model: annotation is the binding resource; G1 repriced 70–130 annotator-hours; G4 repriced 400–900 hours / order $8k–25k; the rev-1 $100–300 figure withdrawn; MEASURED-vs-ESTIMATED tags mandatory on every cost/coverage/retention number (§7) |
| **ASM-1039** | Epistemic demotion of the cheap rungs: G2 is a non-decisive screen whose thresholds are stop-signals, never evidence; G3 is decisive about the parser only; the distinctive-architecture claim has exactly one decisive rung (G4); the "cheap decisive test" claim is withdrawn (§4.1, §7) |

---

## Epistemic register (what this critique relied on)

- **STIPULATED (registered block ASM-1000…ASM-1008) + PROPOSED-ASM
  (ASM-1030…ASM-1039, pending coordinator registration):** every design
  choice above — no design choice in this document is MEASURED. Inherited
  binding stipulations consumed: ASM-0900/0901/0905, ASM-0940–0947 (NLB/1
  rev-2, front-end + gate + statistics + pilot discipline), ASM-0903/0943
  (threshold protocol + at-freeze score class), ASM-0814/0945 (gating +
  consumer obligations), ASM-0852/0853 (FRONT parity mechanics + Rule-2
  cells), ASM-0950–0957 (RAGC arm semantics, anti-weak-control, paired
  TOST/NI shape, manifest measurement contract), ASM-0960–0966 (DECONF
  stages, GS-C reuse — within the executor-validation scope only), ASM-0007
  (a5 structural-not-NSM), ASM-0001 (m0b coverage envelope).
- **MEASURED (each restated strictly inside its envelope):** a5 855/855 +
  7.82 µs and the code-world schema; a5-llm PASS +0.6602 with its
  does_not_license ceiling; a5-nl FAIL 41.6% + S2 kill (ROLE_DIR,
  contained-in 24 / where-defined 18); l3a-parse FAIL 47.6% (paraphrase
  0/261); f2b-replicate +0.1507 / LB +0.1053 at cost 0.103; f2b-transfer
  stage-1 endorsement A = 0.9784 (LB 0.9606, adjudication_valid — no
  evidence for code extraction or NL entry); m0b 0.3542 (corpus-indexed per
  ASM-0001); g8 0/1000; the frontend/engine timings; the human-annotation
  binding-constraint finding (feasibility-synthesis §6).
- **LIT-BACKED (through the completed Phase-0 reviews):** the 110M
  whole-frame band (ATIS 88.2 / Snips 92.8), TeCoD 83.6–89.2, Dr.Spider and
  COGS/CFQ robustness losses, the 0.85–0.95 closed-grammar band — all
  consumed as bands, with the explicit negative finding that no cited work
  guarantees the joint 0.90-retention/S2 bar; conformal exchangeability +
  consistent-confident-inversion caveats; execution-feedback limits
  (PARSE.md §§2–5, §7); the no-bytes-honest-published-win sweep,
  BM25-mandatory and text-serialization-control warnings, matched-control
  no-precedent finding (RAG.md §§1–3, §6).
- **ESTIMATED (planning numbers, no measurement behind them):** every cost
  figure (G1 annotation hours, G2 compute, G4 annotation/adjudication
  envelope), every kill-floor planning value (κ_q^indep 0.5, R_q 0.90,
  precision 0.95, clarification caps, λ), the workload model and its
  renormalization, and all extractor-coverage / parser-retention
  projections.
- **EXTRAPOLATION:** exactly one, ASM-1008, non-load-bearing, resolved by
  G1/G2; no premise or decision rests on it.

This document changes no frozen object, no verdict, no audit, no ruling, and
performs no git, bd, kb, or registry operation. ASM-1000–1008 were registered
by rev 1; ASM-1030–1039 are PROPOSED and listed for the coordinator to
register.

---

## GPT-5.6 review-gate response (rev-codevertb-20260711)

Point-by-point disposition of every concern in
`poc/gpt56-review/rev-codevertb-20260711/last-message.json`. Resolutions are
in this revision; there are no deferrals except where marked (each with
justification and a tracking pointer).

| # | Review concern | Disposition |
|---|---|---|
| R1 (ranked 1) | Extractor-relative coverage hides failure: G1's universe "over extracted symbols" conditions on successful extraction; 150-fact precision ≠ recall/completeness; backward-authored tasks recreate coverage-by-construction | **RESOLVED** §7-G1 + §3.2 [ASM-1030]: extractor-INDEPENDENT census generator (raw repo bytes only, hash/seed-pinned, frozen before extraction); query-level completeness R_q, precision, negative-answer validity, κ_q^indep over the unbiased denominator; dynamic-trace soundness probe; independence pin extended to G4 task sampling; kill floors on all endpoints |
| R2 (ranked 2) | Generic-store deconfound not concrete at the NL boundary; DECONF-A2 ambiguity (gold SQL smuggles the oracle / weak tool agent fakes attribution); "who maps NL→tools" unresolved | **RESOLVED** §4.1 [ASM-1032]: two pinned NL-valid controls — GEN-EXEC (identical measured front-end → pinned deterministic contract→SQL mapping → GS-C; executor-axis licence) and TOOL-NL (strong native NL tool-use, FRONT-built, T_k-metered, RAGC §2.4 anti-weak-control); no gold SQL/formal contract in any arm at any rung; DECONF-A2 re-scoped to executor validation only, its "early NL attribution test" reading withdrawn |
| R3 (ranked 3) | The claimed cheap decisive test is not decisive: G2 inherits a self-declared non-decisive instrument; G3 tests the parser only; no numeric clarification gate; no paired NI statistics; arm table self-contradictory | **RESOLVED** §4.1/§3.1/§4.2(1)/§7 [ASM-1033/1034/1035/1039]: "cheap decisive test" withdrawn — G2 demoted to stop-signal screen, G3 scoped to parser-only, G4 named the sole decisive rung; numeric clarification caps (0.05 unambiguous / 0.20 overall) + clarification-adjusted utility U (λ=0.25) as the primary; paired cluster bootstrap superiority + paired TOST/NI for the 2-pt margin, CP retained only for single-arm rare-event legs; one consistent eight-arm G4 table with retry arms explicitly deferred to G5b |
| R4 | KOT-FAIR/2 manifest incomplete (B_k/F(B_k), SIZE/2 six figures + base image + cold-start/remote, full COST/2 vector, LIFE/1 ledger, sealed-eval/decontamination, exact arm table) | **RESOLVED** §6.1 [ASM-1036]: full manifest instantiated — B_k pinned, F(B_k) = the closed A1–A8 table; six SIZE figures + frozen base image + no-remote rule; full COST/2 vector incl. clarification-turn cost, warm/cold, P3-D-HW rig; LIFE/1 incl. authoring/annotation/amortization; sealed-eval + construction-leakage protocol; FRONT §5 shared/matched AND native cells instantiated with per-sentence licences |
| R5 | Extractor honesty: ast+symtable is not a general resolver; `unknown` propagation undefined for inverse/exhaustive queries | **RESOLVED** §2.2 [ASM-1031]: PY-STAT/1 deliberately-restricted enumerated static subset, content-hashed inventory; candidate-name-set propagation; completeness precondition + UNKNOWN-INCOMPLETE for callers-of/imported-by and negative answers |
| R6 | Edit path not build-ready: "full reference closure is proved" not operationally definable; "plausibly" not executable; insert_import semantics missing; certificates overclaim | **RESOLVED** §2.5 [ASM-1037]: rename confined to RENAME-SAFE/1 (syntactically closed subset); finite pinned hazard inventory H1–H8 replaces "plausibly"; insert_import placement/alias-collision/__future__/conditional-import/no-formatter/applicability pinned; certificate scope = observed mechanical behaviour only; path demoted to design-track until G4 |
| R7 | $100–300 for 3,600 tasks + adjudication contradicts the measured annotation-binding-resource finding | **RESOLVED** §7-G1/G4 [ASM-1038]: figure withdrawn; G1 repriced 70–130 annotator-hours; G4 repriced 400–900 hours / order $8k–25k, all [ESTIMATED]; MEASURED-vs-ESTIMATED tags mandatory |
| R8 | Reallocating the reserved edit share makes G4 not full-product-distribution | **RESOLVED** §7-G4 [ASM-1035]: reallocation withdrawn; G4 claims the query-product denominator (82.4/17.6, renormalized) with the edit share disclosed unscored; full-product claim deferred behind G5 |
| R9 | Design alternates between pinning split-conformal and inheriting NLB's not-yet-selected score class | **RESOLVED** §2.4 [ASM-1001 amended]: full deference to NLB §6/ASM-0943 at-freeze score-class selection; no score class pinned here |
| R10 | Literature does not guarantee the joint 0.90-retention/S2 bar; coverage/retention numbers must be ESTIMATED/ASSUMED | **RESOLVED** §2.3/§9/Epistemic register: all such numbers tagged [ESTIMATED], carried only inside EXTRAPOLATION ASM-1008, never premises |
| R11 | f2b-transfer Stage-1 supplies no evidence for code extraction or NL entry | **RESOLVED** §3.4: scoped exactly as the review states — procedure-confidence for the membership-gold protocol only; the no-code-no-NL sentence carried verbatim |
| R12 | Do not commit as controlling design / run or freeze G1, G2, G4 until corrections land; extractor spike authorized | **ADOPTED** header + §7-G0 + §8: all scored rungs blocked on external acceptance of this revision; G0 spike is the only authorized work; bead recommendations carry the blocks explicitly |

**Self-check gate (confirmed before writing):** (a) G1 samples an
extractor-independent universe and measures query-level recall/completeness +
negative-answer validity — §7-G1; (b) both generic-store controls are
concretely pinned, NL-valid, with no gold SQL in any arm — §4.1; (c) numeric
clarification caps + paired cluster-level G4 statistics + one consistent
eight-arm table — §3.1/§4.2(1)/§7-G4; (d) full KOT-FAIR/2 manifest — §6.1;
(e) extractor and edit path honestly scoped — §2.2/§2.5; (f) epistemic tags
throughout; new assumptions confined to PROPOSED-ASM ASM-1030–1039, registry
untouched.
