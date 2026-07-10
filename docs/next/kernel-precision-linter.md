# N-PL — The kernel precision linter: grounding guardrail + controlled-language rewrite for LLM output

**Kernel of Truth programme — design proposal, node N-PL.**
Author: Kern (Fable design agent), for @jeswr. Date: 2026-07-09.
Bead: `kernel-of-truth-z82`. Idea record: `idea-kernel-precision-linter`
(`registry/ideas.jsonl`; the fleshed entry appended with this document supersedes the
2026-07-09 stub per last-line-wins).
Status: **DESIGN/PLANNING document. Nothing here is pre-registered; nothing spends
money; no experiment entry is created.** Everything proposed becomes real only through
the existing rails (research-engine candidate template → `prereg-freeze`; maintainer
sign-off). Binding constraints: `docs/kernel-design-directives.md`
(§1 no-semantic-web-legacy, §2 two value theses, §4 don't-guess-test, §6 honest stats).
Epistemic tags throughout: **[MEASURED]** (registry verdict / committed data),
**[LIT-BACKED]** (verified at source or in a repo lit-report), **[kb-recall]** (KB hit,
NOT yet verified at source — recall only, per N-C §0), **[memory]** (author knowledge,
unverified), **[search]** (live web verification 2026-07-09), **[STIPULATED]** (design
choice), **[EXTRAPOLATION]** (hope, not premise). No EXTRAPOLATION is load-bearing.

---

## 0. The maintainer's ask, and the one-paragraph answer

**Ask (2026-07-09):** use the kernel as, or as part of, a framework that guardrails /
"lints" LLM outputs into a very precise linguistic style — clear, concise,
precisely-articulated written language with **no meaningless or hallucinated text** —
and make it genuinely **usable**.

**Answer in one paragraph.** Treat "precision" the way software linters treat
correctness: not as detecting every bug in arbitrary code, but as **enforcing a
discipline under which whole classes of defect cannot be expressed**. The kernel is an
NSM-grounded reductive-paraphrase system — a closed, deterministic, versioned,
controlled vocabulary with a parse/render pair — which is exactly the artefact a
*controlled-language* linter needs and exactly what no LLM judge has. The linter
parses LLM output into propositions, classifies each into a five-way verdict lattice
(grounded-consistent / grounded-contradicted / ungrounded / vacuous / ambiguous), and
acts per a declared mode: **flag** (permissive report), **quarantine** (strict
contract: ungroundable content must sit in explicitly-marked unverified blocks), or
**rewrite** (deterministic re-rendering of groundable content into a
Minimal-English-style kernel-native surface with a mechanical round-trip check).
The honest boundary is stated up front and built into the lattice: **ungroundable ≠
false**, and at today's coverage (0.3542 content-token mass at rung molecules-v0 on
one pinned corpus [MEASURED `registry/verdicts/m0b.json`]) a naive "flag everything
ungrounded" linter would flag most text — so ungroundedness is *informational* by
default and an *error* only under an opt-in strict contract, while the
coverage-independent classes (vacuity, ambiguity, analytic contradiction on covered
content) carry the near-term value.

---

## 1. What "lint" means here — the operational definition

### 1.1 The linter analogy, taken seriously

A software linter does three distinct things, and the design keeps them distinct:

1. **Style enforcement** — the code must be *expressible in a restricted form*
   (no-implicit-any, no unused vars). Violation is defined by the contract, not by
   runtime failure.
2. **Defect-class detection** — patterns that are almost always wrong (use-after-free
   shapes), flagged with a precision/recall trade-off.
3. **Rewrite/autofix** — mechanical transformation into the sanctioned form, safe only
   where the transformation is semantics-preserving *by construction*.

The industrial lesson that binds this design: **false positives are the adoption
killer**. Static-analysis deployment experience (Coverity: Bessey et al. 2010,
*CACM* 53(2), "A Few Billion Lines of Code Later") found users abandon tools whose
alarms they cannot act on **[memory — verify at source before any prereg cites it]**.
Every mode below therefore carries an over-flagging endpoint as a co-primary, and the
default mode never renders a coverage gap as an error.

### 1.2 The unit of analysis: propositions, not sentences

The linter's atomic unit is the **proposition**: the smallest checkable meaning unit
extracted from a sentence. The decomposition-into-atomic-units move is the
established base of modern factuality evaluation — FActScore decomposes long-form
generations into atomic facts and scores the supported fraction (Min et al., EMNLP
2023, arXiv:2305.14251 **[search]**); FacTool generalises tool-assisted per-claim
checking (arXiv:2307.13528 **[kb-recall]**). The kernel changes *what the checker
is*: not retrieval over Wikipedia, but the deterministic kernel machinery —
`kernel_checkable` + decode-verify against canonical records + the `kot-axiom/1`
sidecar + the world layer (the same artefact that passed L3a: exact-answer Wilson-LB
0.9955, correct-refusal Wilson-LB 0.9911, 5.29 µs/query, formalism-properties-only
envelope [MEASURED `registry/verdicts/l3a.json`]).

### 1.3 Flag vs reject vs rewrite — all three, as declared modes

The fork "flag-only vs reject vs rewrite" is resolved by making the action a **mode
parameter**, because the three actions have different soundness requirements:

| Mode | Action | Soundness requirement | Coverage sensitivity |
|---|---|---|---|
| **P (permissive report)** | annotate + flag; never blocks | flags must be precise enough to act on | works at any coverage; U-class is informational |
| **S (strict contract)** | output must be kernel-parseable controlled surface; ungroundable content only inside explicit `unverified:` quarantine blocks; violation ⇒ reject/retry | the *contract* must be checkable (decidable parse), not the *world* | usable now on scoped covered domains; the CNL move (§4) |
| **R (rewrite)** | groundable propositions re-rendered by the deterministic renderer; rest handled per P or S | round-trip: re-parsing the rendered text must recover the identical proposition set (mechanical, both directions deterministic) | rewrite applies only to the covered fragment, by construction |

Mode S is where "no hallucinated text" becomes a **structural** claim rather than a
detection claim: within the quarantine contract, every non-quarantined assertion is
kernel-parsed and checked before emission, so unverifiable content cannot appear
*unmarked* — fail-closed, the same discipline as the encoder's ERR_* convention. This
is precisely the controlled-natural-language architecture: Attempto Controlled
English and its kin obtain decidable checkability by restricting the language, not by
solving open-domain NLU (ACE: Fuchs, Kaljurand & Kuhn 2008 **[memory]**; the CNL
design space is surveyed and classified in Kuhn 2014, *Computational Linguistics*
40(1):121–170 **[search]**).

---

## 2. The pipeline

```
LLM output (or LLM under generation, mode S)
  │
  S1 segment          deterministic sentence/clause segmentation (offset-preserving)
  │
  S2 map + extract    mapper (a1-hybrid preset, signed) → concept refs + abstentions;
  │                   proposition extractor → kot-ast/1 fragments + world-layer
  │                   reference candidates.  EXTRACTION IS THE INSTRUMENT (§2.1).
  │
  S3 classify         per proposition → verdict lattice (§3):
  │                   kernel_checkable → decode-verify vs canonical records
  │                   + kot-axiom sidecar checks + world-layer lookup
  │
  S4 act              mode P: flag report
  │                   mode S: quarantine enforcement / reject+retry
  │                   mode R: deterministic record→text re-render + round-trip gate
  │
  S5 report           per-span classes + severities, per-document coverage-engagement
                      vector, kernel version pin.  Same text + same kernel version
                      ⇒ byte-identical lint report.
```

S5's determinism is the artefact-level differentiator: a lint verdict is
**reproducible, versioned, and auditable** — a property no LLM-judge pipeline offers
(same-input/same-output plus a content-hash-pinned vocabulary; encoder determinism
contract, `encoder/README.md`). This is a *property* claim, true by construction; it
is priced in the evaluation (§5) but never substitutes for the empirical endpoints.

### 2.1 The extraction stage is the instrument, and it is the hard part

The P10 lesson transfers verbatim: the step where model output becomes a checkable
record is part of the instrument, its fidelity must be measured before any readout,
and its failures must never score as kernel successes or failures
(`docs/research-plan/10-model-record-interface.md`; the one existing decode number,
X2's 51/54, is encoder-side only [MEASURED, P10 §1]). Concretely:

- **Mode S** is the IF-C analog: generation is constrained (or retried) into the
  controlled surface, so the parse is near-trivial and parse failure is an observable
  event. This is why mode S is the *sound* mode.
- **Mode P** on arbitrary prose is the IF-A analog: extraction quality upper-bounds
  everything. Fork **LNT-F1** (§7) decides deterministic-parser-only vs LLM-assisted
  extraction; either way the P10 extraction-failure instrument gate applies (held-out
  labelled set; Wilson-LB failure rate > 10% ⇒ instrument-invalid, not a kernel
  result).
- The deterministic mapper's ambiguity policy (abstain-and-record; never resolves
  word sense; `mapper/README.md`) is inherited: abstentions surface as lattice class
  A, not as silent guesses.

---

## 3. Hallucination vs merely-out-of-coverage — the verdict lattice

### 3.1 The problem, stated with the measured existence proof

`ungroundable ≠ false`. The kernel is explicitly partial: 0.3542 content-word token
mass at the primary rung molecules-v0 (kernel-v0 0.2210; the wn31-aligned
AxiomsOnly-reachable band 0.7841, which is vocabulary membership, never explicated
coverage), measured on one pinned corpus (TinyStories-validation) and one incomplete
kernel instance, extrapolating to no other corpus [MEASURED
`registry/verdicts/m0b.json`, envelope verbatim]. And the degenerate behaviour of a
naive groundedness gate is already on the ledger: in f2b-replicate, all 500 external
(OpenBookQA) items were `kernel_checkable = false` by construction, the verifier
abstained on 100% of them, and the verify-arm outputs were byte-identical to
model-alone at every seed [MEASURED `registry/verdicts/f2b-replicate.json`;
`poc/f2b-transfer/design.md` §2]. A linter that renders "cannot ground" as
"hallucination" would today mislabel most of any real document. The design answer has
two parts: a **class lattice** that separates the reasons a proposition fails to
ground, and a **severity policy** that is a function of (class, mode) — never of
groundability alone.

### 3.2 The five classes

| Class | Definition (deterministic) | What it honestly indicates | Default severity (mode P) |
|---|---|---|---|
| **G+ grounded-consistent** | parses to kernel-expressible proposition(s); decode-verify + sidecar + world-layer checks pass | precise and consistent with the kernel's content | none (positive annotation) |
| **G− grounded-contradicted** | parses to kernel-expressible proposition(s) that violate a definition, a `kot-axiom/1` constraint, or contradict a world-layer record | analytic error or record conflict — the one class the kernel can call *wrong* | **error** |
| **U ungrounded (coverage gap)** | contains content lemmas/senses outside the kernel vocabulary, or structure outside the grammar | out of coverage — says nothing about truth | **info** (annotation + per-document coverage disclosure) |
| **V vacuous** | parses to zero propositional content: rhetorical filler ("it is important to note that…"), tautology after explication normalisation ("innovative solutions deliver value" → no non-trivial clause), unresolvable deixis, weasel quantification ("many experts believe") with no groundable complement | the "meaningless text" target — *distinct from U* | **warning/error** per sub-class |
| **A ambiguous** | mapper abstention: multiple candidate senses, none policy-resolved | imprecise wording — precise text should not require sense-guessing | **warning** (candidates listed) |

Three consequences of the lattice:

1. **"Hallucination" is never a lint class.** The linter's honest claims are:
   G− catches *analytic/record contradictions* on covered content; V catches
   *meaninglessness*; mode S makes *unmarked unverifiable assertion* structurally
   inexpressible. Open-domain factual-hallucination detection is explicitly NOT
   claimed — that fight belongs to retrieval-based checkers (FActScore-class
   **[search]**) and consistency methods (SelfCheckGPT, arXiv:2303.08896
   **[memory]**; NLI-based inconsistency detection, SummaC,
   doi:10.1162/tacl_a_00453 **[kb-recall]**), which are the comparison arms, not the
   competitors we must dethrone.
2. **Over-flagging at low coverage is prevented by policy, not hope**: U is
   informational in mode P; only an opt-in mode-S contract (a *style* contract, like
   a lint rule set) promotes it — and mode S is recommended only for scoped covered
   domains until coverage grows (§6).
3. **The vacuity class carries coverage-independent value, partially.** Sub-class
   V-rhetorical (discourse filler, hedging templates) is detectable from function
   words and shallow deterministic patterns at any coverage; V-tautology (content
   that survives parsing but reduces to nothing after explication) requires coverage.
   The split is measured, not assumed (LNT-E0, §5).

### 3.3 Severity policy (mode × class)

```
            G+      G−      U            V-rhet   V-taut   A
mode P      ok      error   info         warn     warn     warn
mode S      ok      error   error*       error    error    error
mode R      keep    flag    quarantine   drop†    flag     flag
* unless inside an explicit `unverified:` quarantine block — then annotate-only.
† dropped filler is listed in the lint report (nothing is silently deleted).
```

---

## 4. The controlled-language rewrite target

### 4.1 The decision: a kernel-native, Minimal-English-style surface (fork LNT-F2, recommendation (c))

Candidates considered:

- **(a) Pure NSM reductive paraphrase (primes only).** Rejected as the *surface*:
  reductive paraphrase **expands** — explications are many clauses long — which
  contradicts the maintainer's "concise" requirement; and the NSM school itself
  concedes pure primes are unusable at scale, which is why **Minimal English**
  (Goddard ed. 2018, *Minimal English for a Global World*) exists: primes + vetted
  cross-translatable molecules + relaxed grammar, aimed at practical precise
  communication [LIT-BACKED `reports/nsm-and-knowledge-injection.md` §1.2, verified
  in-repo]. Primes remain the *expansion-on-demand* bottom layer: any rendered
  sentence can be expanded to its full explication on request (the "why is this
  precise" affordance).
- **(b) An existing CNL (Attempto ACE or kin).** Rejected as the target, kept as the
  literature comparator. ACE maps English-like text to discourse representation
  structures/FOL (Fuchs, Kaljurand & Kuhn 2008 **[memory]**; design space in Kuhn
  2014 **[search]**) — adopting it means importing a *second* semantics and a large
  grammar not aligned with `kot-ast/1`, buying a translation problem between ACE's
  logic and the kernel's records, and brushing against the spirit of directives §1
  (no legacy formalism imports; ACE is not semantic-web legacy, but the
  two-semantics tax is the same disease). The CNL literature's *empirical* lessons
  transfer regardless of grammar choice: CNLs are substantially easier for humans to
  **read/verify** than formal notations, while **writing** CNL unaided is hard and
  needs tool support (Kuhn 2014 and the ACE tooling line **[memory — soft claim;
  verify before any prereg leans on it]**). That asymmetry is exactly why the
  *machine-writes, human-reads* direction of a rewrite mode is the right way round.
- **(c) Kernel-native surface (RECOMMENDED).** A deterministic **record→text
  renderer** over the covered fragment: molecule-tier vocabulary (write at the
  highest covered tier, never raw primes), the closed explication grammar's frames
  rendered through pinned templates, one canonical surface form per record shape.
  The parser (mapper + extractor) and renderer are inverse *by construction* on the
  covered fragment, which is what makes the round-trip gate mechanical. Templated
  record→text rendering already exists in embryo (d-qa's templated definitional QA
  authoring [MEASURED as machinery, `data/d-qa/`]); DeepNSM's measured gap — LLM
  explication generation is low-quality and **enforces no grammar** (composite
  24.6/100; grammar enforcement flagged by its authors as future work) — is
  precisely the gap a deterministic grammar-owning renderer fills [LIT-BACKED
  arXiv:2505.11764 via `reports/nsm-and-knowledge-injection.md` §1.1].

### 4.2 Round-trip fidelity vs intent fidelity — two different guarantees

- **Round-trip (mechanical, gate-able):** re-parsing the rendered sentence recovers
  the identical proposition set. Both directions deterministic ⇒ testable at zero
  marginal cost per document; pre-declared bar ≥ 0.95 on the covered fragment or the
  rewrite mode is blocked (§5 kill K-R1).
- **Intent (human, not mechanically guaranteed):** the rendered text is faithful to
  what the *author meant*, not merely to what the extractor parsed. Riemer's critique
  of Wierzbickian substitutability — judging paraphrase adequacy presupposes the
  meaning being explicated — is inherited here in full [LIT-BACKED Riemer 2006,
  *Linguistics & Philosophy* 29, via `reports/nsm-and-knowledge-injection.md` §1.3]:
  parse-step meaning loss is invisible to the round-trip check *by construction*.
  Therefore human-rated intent fidelity is a mandatory co-primary in LNT-E2, and the
  rewrite is always emitted **alongside** the original (lint-style diff), never as a
  silent replacement.

### 4.3 Readability–concision accounting

Rendered text must be scored on both clarity AND length: reductive precision tends to
expand, molecule-tier writing pulls back. Token-count delta and human-rated concision
are separate endpoints (a rewrite that is clearer but 2× longer fails the
maintainer's brief). Comparison arm: the same LLM prompted to "rewrite clearly and
concisely in plain language" — LLMs are strong plain-language rewriters, and this
null is cheap **[STIPULATED as the null; strength of the null is the honest
expectation]**.

---

## 5. Evaluation plan (candidate-shaped; nothing here is frozen)

All experiments carry the coverage-disclosure discipline (m0b number restated
verbatim with rung, per P2 G-7) and report the per-document **coverage-engagement
vector** (fraction of propositions per lattice class) in every cell.

- **LNT-E0 — instruments + false-alarm floor (Tier 0, ~$0, r0-local-cpu).**
  (i) Proposition-coverage census over a sample of real LLM outputs: what fraction of
  propositions are *fully* covered (conjunctive over all content lemmas + frame)?
  Expected far below the 0.3542 token-mass number — measured, not assumed; this
  number *is* the linter's engagement ceiling and the headline coverage-dependence
  fact. (ii) False-alarm rate of V/A/G− flags on clean, human-authored precise text
  (good technical documentation on covered domains) — the linter-noise endpoint.
  (iii) The V-rhetorical/V-tautology coverage-independence split, measured.
- **LNT-E1 — flag quality (Tier 1, ~$20–40).** Seeded-corruption corpus: inject
  filler, weasel templates, and **analytic contradictions of covered
  definitions/axioms** into covered text via a validity-aware mutator (the X1
  single-edit pattern reused at text level), plus natural LLM outputs annotated
  blind. Endpoints: per-class precision/recall of flags; co-primary over-flag rate on
  clean text. Arms: {kernel linter; prompted-LLM linter; **prompted-LLM linter given
  the same kernel records as text — the Law-2 null, the arm that decides whether the
  deterministic machinery adds anything beyond its content** [LIT-BACKED Law 2,
  `reports/lit-llm-injection-priorart.md`]; NLI-detector (SummaC-class)
  **[kb-recall]**; consistency-sampling (SelfCheckGPT-class) **[memory]**} at
  matched per-document cost.
- **LNT-E2 — rewrite quality (Tier 1–2, ~$40–80 + judge time).** Blind pairwise
  preference on clarity, concision, and intent fidelity: kernel rewrite vs
  prompted-LLM rewrite at matched budget, on covered-domain documents; judges never
  see arm identity (the f2b-transfer blind-adjudication pattern; agent judges with
  human spot-audit to control cost). Mechanical endpoints: round-trip rate,
  token-count delta.
- **LNT-E3 — end-to-end reduction (Tier 2, ~$60–120).** Does mode-S generation on
  covered definitional/instructional tasks reduce vacuous/unfaithful content per 100
  sentences (independent blind judges + NLI detector as convergent instruments) at
  acceptable cost in task success and quarantine/refusal rate? Null: same model +
  a system-prompt style contract (the "just ask for precision" null). Caution
  imported from the constrained-decoding literature: hard output constraints can tax
  generation quality ("alignment tax" of constrained decoding, arXiv:2604.06066
  **[kb-recall]**; format-tax fork IF-1 in P10) — the mode-S tax is measured, not
  assumed away.

**Pre-shaped kills (margins fixed at freeze, shapes fixed here):**

- **K-P1 (permissive mode dies):** LNT-E1 flags lose to the kernel-as-text prompted
  null on per-class F1 at matched cost, AND the determinism/audit property premium
  is judged by the maintainer to not carry deployment value alone ⇒ mode P is dead;
  record the negative.
- **K-R1 (rewrite blocked):** round-trip < 0.95 on the covered fragment ⇒
  parser/renderer are not inverse in practice; fix or kill before any human eval.
- **K-R2 (rewrite harmful):** human intent-fidelity below the pre-declared margin ⇒
  rewrite mode dies regardless of clarity wins (a clearer lie about what you said is
  worse than your sentence).
- **K-N1 (noise kill):** false-alarm rate on clean precise text above the
  pre-declared bar ⇒ unusable regardless of catch rate (the Bessey lesson,
  mechanised).
- **K-S1 (strict-mode tax):** mode-S task-success degradation beyond margin vs the
  prompt-contract null ⇒ the contract is too expensive at current coverage; retreat
  to P/R and re-gate on coverage growth.

---

## 6. Coverage-dependence — what is usable sooner vs later

The dependence is a **staircase, not a wall**, because the lattice classes engage at
different coverage bands:

| Stage | Engages at | What it delivers | Gate |
|---|---|---|---|
| **0 — style/noise linter + instruments (now)** | V-rhetorical (coverage-independent) + A (mapper exists) + vocabulary-membership U-annotation at the wn31 band (0.7841 membership — never quoted as explicated coverage [MEASURED m0b sec-by-rung]) | a usable `kot-lint` CLI: filler/hedging/ambiguity flags + coverage annotation; dogfood on the programme's own generated docs; the LNT-E0 instruments | none (Tier 0) |
| **1 — strict-mode scoped domains (near-term)** | molecules-v0 band on *chosen* covered domains (definitional/instructional text over the covered vocabulary) | mode S with quarantine: structurally hallucination-surface-free emission on the covered fragment; mode R rewrite with round-trip gate | LNT-E0 pass + renderer build |
| **2 — permissive linting of arbitrary output** | grows with proposition-level coverage | G−/V-tautology flags at useful engagement rates on general text | LNT-E1/E2 verdicts + coverage growth |
| **3 — guardrail middleware (agent pipelines)** | high coverage + measured extraction | the maintainer's full vision | Stage-2 verdicts; not designable further without them (directives §4) |

Coverage growth is a **shared dependency, not this idea's burden alone**: the
haiku-tier cheap-mint pipeline and the cross-lingual phrase-coverage idea
(`idea-crosslingual-phrase-coverage-io-compression`) raise the same engagement
ceiling for their compression endpoint; every point of coverage bought there is
bought here too. Conversely the linter gives coverage growth a second, more
demanding consumer: proposition-level conjunctive coverage (all lemmas + frame),
which LNT-E0 instruments for the first time.

---

## 7. Forks (directives §4 form)

- **LNT-F1 — extractor identity (mode P).** *(a)* deterministic parser only (mapper +
  closed grammar; abstention-bounded, lowest engagement, fully deterministic);
  *(b)* LLM-assisted proposition extraction with leak-check + P10-style fidelity
  gate (higher engagement; re-imports stochasticity into the front of a determinism
  pitch — the S5 byte-identical-report property then holds only downstream of the
  extraction transcript). *Decided by:* extraction-fidelity F1 and engagement rate on
  the LNT-E0 census, cost on ledger. *Kill per arm:* (a) engagement too low to power
  any E1 cell; (b) fidelity gate fails.
- **LNT-F2 — rewrite surface.** Decided in §4.1 as a design recommendation:
  *(c)* kernel-native Minimal-English-style renderer; *(a)* primes-only and
  *(b)* ACE are recorded as rejected-with-reasons; (b) additionally survives as the
  comparator literature. Re-openable only by an LNT-E2 fidelity kill.
- **LNT-F3 — vacuity operationalisation.** *(a)* pattern-tier only (deterministic
  rhetorical-filler lexicon); *(b)* + explication-normalisation tautology detection
  (needs coverage); *(c)* + LLM vacuity judge (null arm, not part of the linter).
  *Decided by:* LNT-E0(iii) split + LNT-E1 per-class F1.
- **LNT-F4 — mode-S enforcement point.** *(a)* post-hoc reject+retry loop (F2
  harness reuse, cheapest); *(b)* grammar-constrained decoding of the controlled
  surface (strongest, imports the constrained-decoding tax; cf. arXiv:2604.06066
  **[kb-recall]**, P10 IF-1). *Decided by:* the measured format tax at LNT-E3.

---

## 8. Placement — ladder, idea registry, and the neighbouring programmes

### 8.1 Ladder placement

The linter is an **L0-family external-seam artefact**: the verifier seam (A5/F2)
generalised from answer-checking to full-text style+groundedness checking, plus the
L1a canonicaliser mirrored to the **output** side ("L1a-out"). It requires **no
in-network rung**: no adapter, no bottleneck, no training. The checking core is the
L3a engine in its third seat — the same deterministic artefact serving as *answerer*
(L3a), *checker* (F2), and now *linter* (the composition already anticipated in
N1-A §5.2's "same artefact in two seats"). `ladder_ref`: L0-verifier-seam /
L1a-out; it composes with, and is orthogonal to, every L1b/L2x rung.

### 8.2 Idea-registry links

- `idea-crosslingual-phrase-coverage-io-compression` and
  `idea-compositional-rollup-invented-concepts`: **orthogonal value theses**
  (they = efficiency/I-O compression; linter = correctness/precision of surface
  language) with **shared components** — the mapper/parse front-end, the
  kernel-native renderer (their decoder-side expansion and the linter's rewrite are
  the same renderer), and the coverage-growth dependency (§6).
- `idea-leaderboard-benchmark-eval`: orthogonal; the linter's evaluation is
  flag/rewrite quality on covered slices, deliberately not leaderboard accuracy.
- Programme-2 architecture ladder: sits beside L1a within Pillar A; its experiments
  flow through the Pillar-B candidate template like any rung.

### 8.3 The Shuttle / SHACL-CS synergy (maintainer's separate programme)

The maintainer's Shuttle programme (triple-generating EBNF formalism + streaming
generators, repo `jeswr/rdf-shuttle`) and SHACL-CS-1.2 (compact constraint-syntax
spec, `jeswr/shaclc-1.2`) are the same *genre* of artefact as this design's
controlled surface: **closed grammars engineered as product surfaces for precise,
machine-checkable language** [maintainer-programme]. Concrete synergy, honestly
bounded:

- **Formalism craft + tooling reuse [EXTRAPOLATION — resolution: assess at renderer
  build time]:** Shuttle's EBNF-driven streaming-generation machinery is a candidate
  implementation substrate for the record→text renderer (grammar-driven generation
  is exactly what a renderer is); SHACL-CS's shape-constraint compact syntax is the
  same design problem as rendering `kot-axiom/1` constraints readably.
- **The hard boundary (binding):** directives §1 — RDF/OWL/SHACL *semantics* do not
  enter the kernel. The synergy is engineering craft and a shared maintainer story
  ("precise formal-linguistic surfaces"), never a semantic dependency in either
  direction. Any shared code crosses the boundary as a grammar-engine library, not
  as a data model.

---

## 9. Honest risks, and the null this must beat

1. **The null is cheap and strong.** One prompt to a frontier model — "rewrite this
   precisely and concisely; flag unsupported or vague claims" — costs one API call
   and no kernel. Law 2's discipline applies with full force: the decisive null is
   that same prompt **plus the kernel's own records rendered as text**. The linter's
   defensible wins over it are (i) determinism/reproducibility/versioning of
   verdicts (structural — true by construction, valuable in exactly the
   spec/contract/regulated-writing contexts where a "precise style" is wanted),
   (ii) the mode-S structural guarantee (a prompt cannot make unverifiable assertion
   *inexpressible*; a fail-closed contract can), and (iii) per-class flag quality at
   matched cost — which is an open empirical fight the kernel can honestly lose.
2. **Extraction quietly becomes the experiment** (P10's own warning). Mode P on
   arbitrary prose stands or falls on parse engagement and fidelity; the mapper
   abstains heavily by design. Mitigation is architectural (mode S moves the hard
   direction to generation time) and instrumental (the extraction gate); it is not
   assumed away.
3. **Proposition-level coverage will be brutal at first.** Conjunctive coverage is
   necessarily ≤ token-mass coverage (0.3542 molecules-v0); the LNT-E0 census may
   put Stage-2 engagement in single-digit percent. That is a finding, not a
   surprise; the staging (§6) is designed so Stage 0/1 value does not depend on it.
4. **Rewrite can be fluently wrong about intent** (Riemer circularity, §4.2). The
   round-trip gate cannot see parse-step meaning loss; only the human fidelity
   endpoint can, and K-R2 makes it lethal.
5. **Concision may lose to the LLM.** Reductive precision expands; molecule-tier
   writing mitigates but the prompted-LLM rewrite is a genuinely strong stylist.
   Expected close fight; the differentiators are fidelity guarantees, not elegance.
6. **Vocabulary honesty in the UI.** The lint vocabulary must say
   "unverifiable-here" / "out of coverage", never "hallucination", for class U —
   otherwise the tool itself commits the ungroundable=false fallacy it was designed
   to avoid. This is a binding naming decision, not cosmetics.
7. **Guardrails-market adjacency.** Existing LLM guardrail frameworks (NeMo
   Guardrails-class **[memory]**; latent-reasoning guardrails, arXiv:2605.29068
   **[kb-recall]**) target safety/topic control, not semantic precision against a
   closed definitional vocabulary; the `kb novelty` sheet surfaced constrained-
   decoding and verifier lines but no grounded-precision-linter cell [kb-recall,
   DRAFT prior-art — verify at candidate time]. The novelty claim is plausible but
   must be re-verified at source before any write-up asserts an empty cell.

---

## 10. Is this a stronger value proposition than verifier-offload? (asked directly, answered honestly)

**Where verifier-offload stands [MEASURED]:** HE1's primary FAILED at F2 (gap-closure
primary −40.13, `registry/verdicts/f2.json`); the f2b pivot then replicated a real,
correct-alignment-specific verifier lift (+0.151 primary; the derangement control
destroys record↔item alignment, not NSM content, so "kernel-content-specific" is not
licensed — registry/corrections/f2b-replicate/3-claims-language-erratum.json) — but
on self-authored covered
definitional QA at ≤1.7B hosts, with the circularity question (content vs
self-defined gold) explicitly unresolved and under paid test right now
(f2b-transfer). The offload framing stakes the kernel's value on winning an accuracy
transfer fight against ever-stronger models — fighting Law 2 uphill.

**Where the linter framing differs.** It does not need to beat a bigger model at
accuracy. Its value claims sit on properties the kernel *demonstrably has* —
determinism, versioned closed vocabulary, exact checking with correct refusal
(L3a's formalism-property PASS), fail-closed discipline, a parse/render pair — and
that LLM-judge pipelines structurally lack. NSM reductive paraphrase is the kernel's
native register, so the linter is the first application whose *target output* is the
kernel's own surface rather than a foreign benchmark. And its user is a
writer/agent-pipeline wanting a precision contract, not a leaderboard: "usable" is
reachable at Stage 0/1 without winning any open-domain fight.

**The symmetrical honesty:** the linter inherits the same two exposures that hurt
offload — coverage (harsher here: conjunctive proposition-level) and a cheap prompted
null that may match its detection quality. If K-P1 fires and the maintainer does not
value the determinism premium, the broad form dies the same death.

**Net read:** as a *value framing* — what the kernel is *for* — the precision linter
is stronger than verifier-offload: it aligns the product claim with the artefact's
actual measured strengths and with NSM's actual identity as a
reductive-paraphrase discipline, and it has a coverage-independent usable core
(Stage 0/1, mode S on scoped domains) that offload never had. As an *empirical
claim* it is exactly as exposed as offload was until LNT-E0/E1 run — and this
document deliberately reaches no further than that [EXTRAPOLATION beyond the design
itself is confined to the tagged items above; none is a premise].

---

*Cross-references:* `registry/ideas.jsonl` (`idea-kernel-precision-linter`, fleshed
entry appended 2026-07-09); `docs/next/architecture-ladder.md` (L0/L1a/L3 seats);
`docs/next/00-programme-2-overview.md` (candidate rails);
`docs/research-plan/10-model-record-interface.md` (extraction instrument gate);
`registry/verdicts/{m0b,l3a,f2,f2b-replicate}.json` (the measured record);
`reports/nsm-and-knowledge-injection.md` §§1.1–1.3 (DeepNSM, Minimal English,
Riemer); `reports/lit-primitives-grounding-priorart.md` §1 (NSM status);
`reports/lit-llm-injection-priorart.md` (Laws 2–3); `mapper/README.md` (a1-hybrid,
abstention); `poc/f2b-transfer/design.md` (blind-adjudication pattern; d-ext
degeneracy). External anchors verified this pass: Kuhn 2014, *Computational
Linguistics* 40(1):121–170 (https://aclanthology.org/J14-1005/) **[search]**;
FActScore, Min et al. 2023 (https://arxiv.org/abs/2305.14251) **[search]**.
