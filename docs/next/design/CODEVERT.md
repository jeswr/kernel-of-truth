# P3-D-CODEVERT — CODEVERT/1: critique + synthesis of the code-vertical selective coprocessor (CASK-CODE/1)

> **Status: [DESIGN-CRITIQUE + SYNTHESIS] deliverable of the bidirectional
> loop's CRITIC step on the round-1 top direction (docs/next/analysis/
> round1-steering.md convergence item 6: the narrow structured-domain selective
> coprocessor, named by BOTH independent subjective analyses as Programme-3's
> single most promising direction). The object under critique is GPT-5.6's
> proposal CASK-CODE/1 (`poc/gpt56-review/arch-codevert-20260711/
> last-message.json`, read in full). Nothing here is frozen, pre-registered,
> scheduled, or run; no verdict, audit, frozen object, or registered ruling is
> touched. The design's assumption entries are REGISTERED in the fresh
> append-only block **ASM-1000…ASM-1008** (block ASM-1000–1029 assigned to this
> bead, DISJOINT from every prior block — highest prior id ASM-0982; entries
> 1009–1029 remain free).** Author: Fable, chief-architect role
> (`kern/fable-designer`), 2026-07-11. This document goes through the standing
> GPT-5.6-class external review before any commit/prereg use.
>
> **Inputs read at source, in full:** the CASK-CODE/1 proposal;
> docs/next/analysis/round1-steering.md; docs/next/design/NLB.md (rev 2);
> docs/next/lit/PARSE.md + RAG.md (via full-text digests, section-cited);
> docs/next/design/DECONF.md; docs/next/feasibility-synthesis.md;
> docs/next/design/FRONT.md (rev 2);
> poc/f2b-transfer/judge-1-results/stage1-analysis.json (the just-landed
> stage-1 endorsement PASS); docs/design-a5-code-worldlayer-oracle.md (grammar
> family check); registry/assumptions.jsonl (block-collision check).
>
> **Tag convention (house discipline):** `[MEASURED: ref]` = a registry
> verdict/assessment/artifact restated strictly inside its envelope;
> `[LIT-BACKED: lit-review §]` = an external fact verified at primary source by
> a completed Phase-0 lit review, cited through that review;
> `[STIPULATED: ASM-id]` = a design choice registered here or inherited;
> `[EXTRAPOLATION: ASM-id]` = a registered forward projection, never a premise.

---

## 0. One-paragraph summary

GPT-5.6's CASK-CODE/1 is the strongest architecture proposal Programme-3 has
received: it is narrow, typed at exactly two neural↔symbolic seams, fail-closed,
and it names its own deflationary outcome (the aligned-SQLite arm) as a
first-class kill. The critique below CONFIRMS the core recipe and finds four
substantive defects: (1) the **mandatory-inverse rule re-imports the exact
ambiguity-set defect GPT-5.6's own NLB review forced us to reject** — it
manufactures a clarification turn on essentially every directional query and
must be replaced by the evidence-gated semantics already registered as
ASM-0940; (2) the **v1 edit contracts (rename / insert_import) are fully
mechanical once a contract is accepted**, so the proposal's neural
draft-plus-verify-retry loop guards machinery its own v1 workload never
exercises — v1 edits execute symbolically, and verify-retry defers to a later
genuinely generative contract; (3) **real-repo extraction coverage κ is
unmeasured** and the proposal has no rung that measures it before task
authoring — the coverage wall (the programme's measured existential risk)
relocates, uninspected, into the extractor; (4) the proposal's pilot
duplicates ~80% of the already-designed NLB-0-B code pilot and its win
statistics are unspecified — both repaired by unification (front-end :=
NLB-FE/1; statistics := ASM-0941's exact cluster-CP machinery). The synthesis
(§6) keeps CASK's product boundary, arm ladder, clarification protocol, and
kill criteria; the ladder (§7) runs cheapest-falsifier-first: G1 real-repo κ
census (~$0, CPU) → G2 merged mechanism pilot (≤5 GPU-h + ~$25, absorbing
NLB-0-B code) → G3 = the registered G-NLB code gate → G4 matched end-to-end
comparison (prereg deferred behind G2 per the steering freeze) → G5 edits.
Everything here licenses at most an **architecture-family** claim; no outcome
of any CODEVERT rung is evidence about kernel CONTENT
[STIPULATED: ASM-1000].

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

**2.2 Deterministic extractor: works, but it is where the coverage wall now
lives.** ast+symtable extraction with fail-closed `unknown` on dynamic
dispatch/reflection/monkey-patching is buildable and the conservative policy
is correct. Two under-priced costs: (a) blind repo-disjoint human annotation
of extractor precision is REAL human-annotation spend, and human annotation is
the programme's measured binding constraint, not compute
[MEASURED: docs/next/feasibility-synthesis.md §6]; (b) nothing in the proposal
measures what fraction of the product task distribution is `proved`-answerable
on REAL repositories before the eval corpus is authored. The programme's
measured coverage numbers are brutal everywhere they exist (g8 0/1000 random
Mathlib declarations; m0b 0.3542 on the friendliest corpus, corpus-indexed
[MEASURED: registry/verdicts/g8.json + registry/verdicts/m0b.json per ASM-0001]).
Python-repo relational facts are a far friendlier extraction target than
either, but "friendlier" is an expectation, not a number — it is registered
as EXTRAPOLATION [EXTRAPOLATION: ASM-1008] and the G1 census therefore
precedes all task authoring and all model work (§7) [STIPULATED: ASM-1004].

**2.3 The 110–360M contract front-end: plausible band, gate not cleared by
any cited number.** The closest published shapes sit AT or BELOW the
interesting bar: 110M BERT-class whole-frame exactness ≈88.2% ATIS / ≈92.8%
Snips; template-mined + grammar-constrained text-to-SQL (TeCoD) 83.6–89.2%
matched-template EX; learned parsers still drop 14.0% overall / 50.7%
worst-perturbation under Dr.Spider-style rephrasing; compositional-split
collapse (COGS 96–99% ID vs 16–35% OOD) is the standing warning for
role/direction binding [LIT-BACKED: docs/next/lit/PARSE.md §2, §5a, §5c].
The review's honest band on a closed grammar is ~0.85–0.95 with
paraphrase-diverse training + lexicon resources, and "no cited work reports
retention-at-S2-bound for a ≤360M parser on a grammar like ours"
[LIT-BACKED: docs/next/lit/PARSE.md §5a, §7.1]. Verdict: the encoder-heads
recipe is the right FIRST build (it is NLB's registered primary parser class,
ASM-0905, independently converged on), the pilot's 0.80-coverage kill bar is
inside the plausible band, and CASK's final +5-pt-over-baseline bar is an
open empirical question, never a premise. The BIO-span contract also means
descriptive references ("the function that parses configs") are out-of-contract
by construction — a disclosed coverage cost, not a defect
[STIPULATED: ASM-1002].

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
- DECISION: the synthesis replaces mandatory-inverse with the
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
- Kept from CASK: the ≤8-contract cap, empty-set → abstain, split-conformal
  calibration on complete-contract nonconformity with the honesty line that
  conformal guarantees are claimed only for the pinned phrasing distribution
  (exchangeability breaks across sources by construction; the CAL-vs-EVAL
  shift delta is a measured secondary) [LIT-BACKED: docs/next/lit/PARSE.md §4
  conformal caveats; STIPULATED: ASM-1001, adopting ASM-0903(3)].

**2.5 The edit path: the proposal guards machinery its own v1 never needs.**
For rename(symbol_id, new_identifier) and insert_import, once a contract is
ACCEPTED the entire edit is a deterministic function of the substrate: the
extractor's proved reference set names every span to rewrite; the new text at
each span is the contract's own argument. There is nothing for a neural model
to draft. GPT-5.6's §6 span-scoped neural drafting + verify-retry loop is
therefore architecturally superfluous for the only two edits v1 admits — it
adds a stochastic component (and its failure modes and its retry-parity
burden) to a workload that is 100% mechanically computable.
- DECISION: v1 edits execute SYMBOLICALLY — accepted contract → deterministic
  applicability check → deterministic transform → mechanical verifier (parse,
  span authorization, symbol resolution, postcondition, repo compile, pinned
  tests) → PATCH + certificate, no retries because nothing is sampled. The
  neural-draft + bounded verify-retry loop is DEFERRED to a later genuinely
  generative edit contract (G5b), where GPT-5.6's design of it (structured
  violation traces, ≤2 retries at matched token budget, certificate scope
  limited to mechanical properties) is adopted as written
  [STIPULATED: ASM-1007].
- DECISION: rename admissibility is fail-closed on analysis completeness —
  admissible ONLY when the symbol's full reference closure is `proved` with
  ZERO `unknown`-status references naming or plausibly naming it (dynamic
  attribute access, getattr strings, __all__ re-exports, shadowing ⇒
  ABSTAIN(analysis_incomplete)). Python rename is not statically certifiable
  in general; the contract is honest only if incompleteness refuses. The
  proposal's "deterministic applicability checks" line implies but never
  states this rule; it is now binding [STIPULATED: ASM-1007].

**2.6 Tier-0, substrate schema, cost envelope: adopt with NLB's pins.**
Tier-0 exact templates ≈ the measured 250–267 µs a1-hybrid class; executing
2–8 interpretations is ≈free at the measured 5.29–7.82 µs/query engine cost
[MEASURED: registry/verdicts/l3a-parse.json + a5-nl.json frontend timing;
registry/verdicts/a5.json engine timing]. The substrate reuses the measured
code-world schema and executor (CASK says this itself — correct). The size /
latency ceilings, packed-artifact manifest, and API-parser ineligibility rule
are NLB's registered pins and apply unchanged (artifact ≤1.0 GB, Tier-1 warm
p95 ≤500 ms CPU, measured in-gate) [STIPULATED: ASM-1001, adopting
ASM-0946(1)–(5)].

---

## 3. Stress test 2 — does it REALLY get NL into the symbolic substrate, or smuggle an oracle?

**3.1 The clarification protocol: clean.** Pre-annotated intended readings,
scripted responses that reveal only a choice among the arm's DISPLAYED
readings, every arm (including RAG/tool baselines) gets the same one turn,
malformed clarification = failure, turn/tokens/latency charged, and an arm
that fails to display the intended reading cannot be rescued. This is a
measured-system component, not an oracle — the best clarification design in
the programme's record, and the synthesis adopts it verbatim
[STIPULATED: ASM-1002].

**3.2 The residual oracle is at corpus construction, and it is the same one
NLB already discloses.** Tasks are backward-authored phrasings of a closed
grammar over registered symbols; ambiguity and intended readings are
annotated by people who know the grammar. That supports a controlled
semantic-parsing + task-completion claim — it is NOT evidence about naturally
occurring developer traffic, and the 70/15/15 product distribution is a
STIPULATED workload model, not a measured demand distribution. Both
limitations ride verbatim on any G4 readout [STIPULATED: ASM-1002, adopting
the ASM-0945(1) disclosure discipline].

**3.3 The anti-smuggle rules CASK gets right — kept and hardened.**
Full-product-distribution scoring (never covered-slice-only) with blind
extraction coverage κ co-reported; the symbolic side never interprets prose;
execution success never certifies interpretation. Hardening: items whose
answer depends on `unknown`-status extraction MUST be answered
unknown/ABSTAIN and are creditable only under the pre-annotated
answerability labels — extraction incompleteness can never silently shrink
the denominator [STIPULATED: ASM-1003].

**3.4 What the covered slice is now worth.** The just-landed f2b-transfer
stage-1 endorsement PASS (blind external adjudication endorses the membership
gold at A = 0.9784, one-sided 95% LB 0.9606 ≥ 0.70; 360 adjudicated, 36
unresolved ≤ cap; adjudication_valid = true) establishes that kernel-line
covered-slice CONTENT survives blind external adjudication on the covered
slice [MEASURED: poc/f2b-transfer/judge-1-results/stage1-analysis.json +
registry/experiments/f2b-transfer.json stage-1 gate]. Scope discipline: that
is an endorsement of the d-qa membership gold, on the family/world line — it
licenses running stage 2 there; it says nothing about code-vertical NL entry,
which remains the measured FAIL this whole design exists to attack (a5-nl
41.6% retention + S2 kill fired [MEASURED: registry/verdicts/a5-nl.json]).
Its relevance here is morale-free and precise: the definitional-circularity
failure mode did NOT fire where it was tested, so "self-authored gold is
inherently circular" is not a standing objection to CODEVERT's G4 gold
protocol PROVIDED G4 buys the same insurance — blind, repo-disjoint,
externally-adjudicated task gold [STIPULATED: ASM-1006].

---

## 4. Stress test 3 — is the matched-win claim honestly falsifiable and cheap-first?

**4.1 Falsifiable: yes, unusually so.** The arm ladder (R0, RAG-BM25,
RAG-dense, TOOL-native, GENERIC-store, GENERIC-retry, CASK-top1, CASK-set,
CASK-set+retry) is the strongest baseline inventory any proposal has carried;
the GENERIC-store cell (identical extracted facts in SQLite/generic Datalog
behind ordinary JSON tools, consuming NL natively) is exactly the decisive
deconfound both round-1 analyses demanded, and CASK pre-registers its own
death: GENERIC-store within a 2-pt non-inferiority margin kills the
distinctive neurosymbolic claim even if CASK is a good product. The
CASK-set-vs-CASK-top1 frontier condition isolates the one mechanism this
architecture family adds. All kept [STIPULATED: ASM-1006].

**4.2 Gaps, each with a registered repair:**

1. **Statistics unspecified.** "UB95 / LB95" appear with no estimator, no
   clustering, no multiplicity family. Phrasings cluster by base task (K=3);
   rare-event legs need exact bounds. DECISION: adopt NLB rev-2's machinery
   verbatim — one-sided exact Clopper–Pearson on cluster-collapsed
   indicators for every dangerous-error and directional-stratum leg;
   pre-registered cluster bootstrap for non-rare coverage proportions with
   the CP co-report binding conservatively; enumerated Holm family per
   claim; every integer boundary derived by analytic inversion and pinned
   before any scored run [STIPULATED: ASM-1006, adopting ASM-0941].
2. **Parity accounting under-specified.** "Same tuning-compute allowance"
   without a meter is the review's own dimensional-closure lesson from
   FRONT. DECISION: G4 adopts the FRONT/RAGC registered mechanics — the T_k
   resource-vector meter over a closed arm table, the five matched-retrieval
   rules, retrieved-token caps, index bytes charged, shared/matched AND
   native retriever cells [STIPULATED: ASM-1006, adopting ASM-0852/ASM-0853].
   The no-published-precedent warning stands: no bytes-honest published
   small-model retrieval win exists to copy, so this ledger is constructed,
   not cited [ref: docs/next/lit/RAG.md §1 synthesis + §3 (internal lit-review)].
3. **Missing misaligned-store control.** House discipline (the f2b
   derangement lesson) requires the cheap control that shows the FACTS are
   load-bearing, not the store's shape: a seed-pinned shuffled/deranged fact
   table behind the identical CASK stack, expected to collapse to
   abstention/errors. Near-zero cost; added to G4 (and to G2 as a smoke
   variant) [STIPULATED: ASM-1006].
4. **Duplication against the already-designed NLB instrument.** CASK's §8
   pilot (855-grammar diagnostic + ~300 blind phrasings + 110M intent/slot
   model + frozen CAL threshold) is ~80% of NLB-0-B(code) plus two arms.
   Building two parsers, two synthetic-training pipelines, and two pilot
   corpora for the same vertical would be scaffolding-spend against the
   steering's own freeze. DECISION: **unify** — CODEVERT's front-end IS
   NLB-FE/1 on the code vertical (same kot-query-code/1 IR, same Tier-0
   repair, same acceptance layer with evidence-gated sets, same five-role
   data separation and freeze ordering); G2 below is the ONE merged pilot;
   the registered G-NLB code gate is CODEVERT's G3, not a rival bar. The
   only CODEVERT-specific front-end deltas are the two edit-contract intents
   (deferred to G5) and the clarification renderer
   [STIPULATED: ASM-1001; ASM-1005].
5. **Gate-bar reconciliation.** CASK's pilot bar (0.80 completed coverage at
   ≤1% point dangerous error) and G-NLB's gate (retention LB95 ≥ 0.90 +
   S2 UB95 < 0.02) measure different denominators (task completion incl.
   creditable clarification vs gold-parse-ceiling retention). Both are kept,
   explicitly ordered: G2 screens on CASK's cheaper bar; G3 = G-NLB decides
   parser clearance; G4's binding win is CASK's coverage-at-risk conditions.
   No number from a lower rung is ever quoted against a higher rung's bar
   [STIPULATED: ASM-1005].

**4.3 Cheap-first: yes, with one re-ordering.** CASK runs its pilot before
the edit path — right. But it authors evaluation material before measuring
real-repo extraction coverage. The census (G1) is cheaper than the pilot and
can kill the full-distribution product claim outright; it goes first. And the
aligned-SQLite substrate CASK needs already exists as designed work:
DECONF Stage A2 builds GS-C — the a5 typed world in pinned SQLite + published
recursive-CTE query library — and runs the pinned 977-query slice against it
[STIPULATED: ASM-0963, reused]. G2 reuses that artifact instead of building a
second generic executor [STIPULATED: ASM-1005].

---

## 5. Stress test 4 — the biggest failure mode

GPT-5.6 names **agreement laundering** (the emitted set omits the correct
interpretation and the wrong members agree; the executor certifies the wrong
question) and, strategically, **attribution collapse** (the generic store
matches everything). Both are right and both are already wired above:
laundering is bounded by evidence-gated sets + both-orientation strata with
near-zero allowances + blind semantic gold (and §2.4's empty-denotation
subclass is disclosed as the residual); collapse is priced FIRST, at ~$0, by
DECONF-A2/G2's aligned-SQLite arm rather than discovered at G4 price.

The failure mode GPT-5.6 UNDER-weights — the chief architect's addition:

- LOAD-BEARING: **a full CASK win is kernel-free.** Nothing in CASK v1
  consumes NSM semantics, explications, the encoder, or any kernel-authored
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

Two further named risks, with counters in the synthesis: the
**clarification-rate pathology** (a set-happy system converts coverage into
clarifications and wins a metric while losing the product — countered by
charging the turn everywhere, co-reporting clarification rate as a gated
instrument-validity leg, and the evidence-gated semantics that stop
manufactured ambiguity) [STIPULATED: ASM-1002]; and **κ-collapse on real
repos** (dynamic-Python idioms drive `unknown` mass so high that the full
product distribution is mostly unanswerable, making every arm's coverage
number small and the +5-pt contrast unpowered — countered by G1-before-
everything and a registered κ floor) [STIPULATED: ASM-1004].

---

## 6. CODEVERT/1 — the synthesised buildable design

One paragraph of shape, then deltas from CASK-CODE/1:

Pinned repo commit → deterministic conservative extractor (ast + symtable +
pinned import resolver; proved/disproved/unknown/conflict; byte-span
provenance; reuses the measured code-world schema + engine, extended by the
extractor) → SQLite + generic-Datalog serializations of the SAME facts
produced alongside (attribution controls by construction) → **NLB-FE/1 as the
front-end** (repaired µs Tier-0; 110–360M intent+slot Tier-1 under exact
product-automaton grammar masks; trie-constrained entities; evidence-gated
ambiguity set ≤8; split-conformal calibration; frozen τ by fixed-sequence
risk-controlled selection on CAL-B) → contract-and-contrast execution
(agreement → templated ANSWER with provenance; disagreement → deterministic
CLARIFY, one turn; else ABSTAIN with reason code) → v1 edits as deterministic
transforms with mechanical certificates (rename fail-closed on reference-
closure completeness; insert_import); generative edits + verify-retry
deferred. Output contract: ANSWER(value, provenance) / PATCH(diff,
certificate) / CLARIFY(2–3 choices) / ABSTAIN(reason). Everything
inside the measured system; bytes/latency/energy under the KOT-SIZE/2 +
KOT-COST/2 ledgers; no API-hosted component eligible
[STIPULATED: ASM-1001; ASM-1002; ASM-1003; ASM-1007].

Deltas from CASK-CODE/1, complete list:

| # | CASK-CODE/1 | CODEVERT/1 | Why |
|---|---|---|---|
| 1 | mandatory typed-inverse in every directional set | evidence-gated orientation-cue semantics (ASM-0940) | §2.4 — CASK re-imports the rejected NLB rev-1 defect |
| 2 | neural span-draft + verify-retry for v1 edits | v1 edits are deterministic transforms; verify-retry deferred to a generative G5b contract | §2.5 — v1 edit workload is fully mechanical |
| 3 | (absent) | rename fail-closed on `unknown` references in the closure | §2.5 — Python rename is not statically certifiable in general |
| 4 | new pilot parser + corpus | front-end := NLB-FE/1; ONE merged pilot (G2 = NLB-0-B(code) + 2 arms) | §4.2(4) — no duplicate scaffolding |
| 5 | unspecified interval statistics | exact cluster-CP + enumerated Holm family (ASM-0941) | §4.2(1) |
| 6 | "same tuning allowance" (unmetered) | T_k arm-table meter + FRONT §5 matched-retrieval rules (ASM-0852/0853) | §4.2(2) |
| 7 | (absent) | shuffled/deranged-store control arm | §4.2(3) — house derangement discipline |
| 8 | pilot before any repo-coverage measurement | G1 κ census first, kill floor registered | §4.3 / §5 |
| 9 | (implicit) | licence space pinned to architecture-family; kernel-content explicitly out | §5 |
| 10 | (absent) | clarification-rate gated co-report | §5 |

Kept from CASK-CODE/1 unchanged: the product boundary (8 measured query
families + 2 bounded edits, no free-form generation), the two-interface seam
rule, the four-state substrate with certificates, the conservative extraction
policy with blind precision annotation, the deterministic answer/clarify
templates (no free-form renderer), the clarification evaluation protocol
(§3.1), the full-distribution + κ reporting rule, the nine-arm ladder and all
seven binding-win conditions (re-based on the statistics above), the 2-pt
GENERIC-store attribution-collapse kill, the size ladder (110M preferred
first build; 2B admissible but efficiency-rationale-eroding), and the honest
"stop if generic matches" strategic clause [STIPULATED: ASM-1002; ASM-1003;
ASM-1006].

---

## 7. The experiment ladder (cheapest falsifier first)

All costs are planning estimates [STIPULATED: ASM-1004; ASM-1005; ASM-1006].

**G1 — real-repo extraction census (CPU, ~$0 + the smallest honest
annotation).** Pin a repo-selection rule BEFORE looking (candidate pool:
20–30 permissively-licensed Python repos in a pinned size band, disjoint from
anything any front-end trains or calibrates on); run the extractor; report
per-relation fact counts by status, and **κ_q = the fraction of a
mechanically-enumerated query census (all 8 families over extracted symbols)
whose answers are fully `proved`**; blind two-annotator precision check on a
~150-fact sample (the only human spend). KILL (registered planning floor,
maintainer-adjustable at prereg): κ_q < 0.5 on the pinned pool, or blind
extractor precision < 0.95, kills the full-distribution product claim before
any model exists — the direction survives only re-scoped (covered-slice
tool, not product) [STIPULATED: ASM-1004].

**G2 — the merged mechanism pilot (≤5 GPU-h free pool + ~$25 API).**
NLB-0-B on the code vertical, absorbed and extended — ONE pilot, one parser,
one training pipeline: synthetic-only training (ASM-0947(6) recipe); frozen
pilot operating point; evaluated once on the legacy 855-query K=1 blind
corpus (labelled diagnostic — outcomes public) PLUS ~300 fresh blind
phrasings from two disjoint author sources; arms: (i) top-1, (ii)
evidence-gated ambiguity-set + scripted clarification, (iii) the
aligned-SQLite tool arm over GS-C (built by / shared with DECONF-A2,
ASM-0963), (iv) shuffled-store smoke variant. KILLS (adopting CASK §8, exact
where n permits): no operating point with ≥0.80 completed-task coverage at
point dangerous-error ≤1%; correct DSL absent from the emitted set on >10%
of answerable items; set-execution < +5 pts completed coverage over top-1 at
matched risk; systematic directional inversion in any supported stratum;
aligned-SQLite arm within 2 pts at the same risk and resource cap
(= early attribution-collapse signal at pilot scope). Status: a NON-DECISIVE
screen under the NLB-0 discipline — it consumes no registered redesign
cycle and its numbers are neither floors nor ceilings for G3/G4
[STIPULATED: ASM-1005, adopting ASM-0944].

**G3 — the registered gate (not a new experiment).** P3-E-NLB-1 on the code
vertical, exactly as designed: G-NLB retention LB95 ≥ 0.90 jointly with
unconditional dangerous-wrong UB95 < 0.02, K=3 blind phrasings, five-role
separation, directional-stratum kills [STIPULATED: ASM-0901/0940–0947,
consumed as-is]. CODEVERT adds nothing to the gate and quotes nothing over
it; a code-vertical PASS unblocks G4's NL legs under ASM-0814/0945.

**G4 — the matched end-to-end comparison (query-only; the expensive rung;
prereg DEFERRED until G2 GO per the steering's scaffolding freeze).** 20–30
held-out repos frozen before task authoring; ~1,200 base tasks × 3
independently-sourced phrasings; 70% relational / 15%
ambiguous-or-unanswerable / 15% RESERVED (edits enter only at G5 — at G4 the
edit share is re-allocated to relational + ambiguity strata); arm ladder =
CASK §7 minus the retry arms, plus the deranged-store control; binding win =
CASK conditions 1–3, 5, 6 under §4.2(1) statistics; GENERIC-store 2-pt
non-inferiority ⇒ the measured attribution-collapse input to K-P3v2(4) at
this scope. Gold protocol buys the stage-1 insurance: blind, repo-disjoint
authoring + external adjudication of task gold [STIPULATED: ASM-1006].
Rough envelope: the corpus + annotation spend (order $100–300 of authoring
+ the adjudication queue) dominates; compute stays in the ≤50 GPU-h
free-pool class.

**G5 — edits.** G5a: the two mechanical edit contracts (deterministic
transforms; endpoints: edit success non-inferiority vs GENERIC-retry, zero
unauthorized-span edits, certificate validity). G5b: ONE genuinely
generative edit contract with the CASK verify-retry loop vs matched generic
verify-retry (CASK condition 7: non-inferior accuracy/safety + a material
win on tokens, p95, or energy). G5 exists only if G4 survives
[STIPULATED: ASM-1007].

Decision economics: ~$0 (G1) kills the domain; ~$25 + 5 GPU-h (G2) kills the
mechanism AND previews attribution collapse; only then does authored-corpus
money move. Any cheaper ordering tests nothing that can actually die.

---

## 8. Beads this design spawns (recommendation — the coordinator creates them; no bd operation is performed by this document)

```
P3-T-CODEVERT-XT [task, P1]  Build the deterministic Python repo extractor +
    κ-census tool (ast/symtable, conservative fail-closed policy, 4-state
    facts, byte-span provenance, SQLite + generic-Datalog serializations of
    the same facts; reuse the a5 code-world schema and engine desugaring).
    Keep OUT of encoder/; poc/-side harness code. From CODEVERT.md §6/§7-G1
    (ASM-1003/1004).
P3-E-CODEVERT-G1 [task, P1]  Real-repo extraction census: pinned repo rule,
    κ_q + status counts + blind 2-annotator precision sample; registered
    kill floor. Blocked-by: P3-T-CODEVERT-XT. (~$0 CPU + minimal annotation.)
P3-E-CODEVERT-G2 [task, P0]  The MERGED code-vertical mechanism pilot:
    NLB-0-B(code) absorbed + ambiguity-set arm + aligned-SQLite (GS-C) arm +
    shuffled-store smoke + ~300 fresh blind phrasings; CASK §8 kill set under
    ASM-1005. Blocked-by: P3-E-DECONF-0 (GS-C artifact share) and the
    NLB-0-A ROLE_DIR repair leg; coordinates with (and supersedes any
    separate) NLB-0-B code pilot to prevent duplicate scaffolding.
P3-D-CODEVERT-G4 [task, P2, DEFERRED]  Prereg the matched end-to-end
    query-only comparison per §7-G4 (ASM-1006). Blocked-by: P3-E-CODEVERT-G2
    GO + P3-E-CODEVERT-G1 floor + external review of this doc; per the
    round-1 steering freeze it is NOT designed further until G2 reads out.
P3-D-CODEVERT-EDIT [task, P3, DEFERRED]  Edit-contract design (mechanical
    G5a + generative G5b verify-retry) per ASM-1007. Blocked-by:
    P3-D-CODEVERT-G4 outcome.
Dependency edges: G1 ← XT; G2 ← {DECONF-0, NLB-0-A}; G4 ← {G1, G2, G3=
    P3-E-NLB-1(code)}; EDIT ← G4.
```

---

## 9. Honest limits of this synthesis

1. **Every feasibility number for the front-end is a band, not a clearance**
   — the projection that G2's bars are reachable is EXTRAPOLATION ASM-1008,
   never a premise; the K-P3v2(2) negative branch (checker stays an internal
   instrument; the surviving programme is formal/code interfaces and
   compression diagnostics) remains a legitimate pre-agreed outcome.
2. **A CODEVERT win, if it ever lands, is an architecture-family result** on
   a stipulated workload model over backward-authored phrasings — not
   kernel-content evidence, not natural-traffic evidence, not a general-index
   W1 (the vertical fork is the steering's own re-scope).
3. **κ and the product distribution are the soft underbelly**: κ_q's floor is
   a stipulated planning value; the 70/15/15 mix is a workload model. Both
   are maintainer-visible knobs and both are disclosed on every readout.
4. **The GENERIC-store arm must be strong to mean anything** — an under-built
   SQLite/tool baseline fakes the distinctive win; the counter is DECONF's
   anti-weak-control rule (published query library, grammar-conformance
   check) inherited at every rung, plus FRONT's weak-builder counters at G4.
5. **G2 is a screen.** Legacy-corpus reuse is disclosed post-outcome
   analysis; K=1; pilot numbers bind nothing at G3/G4.
6. **Agreement laundering is reduced, not eliminated** — the residual
   (novel systematic inversion a cue inventory does not enumerate; the
   empty-denotation agreement subclass) is carried verbatim on any PASS,
   with the directional-stratum kills as the only in-gate catch.

---

## 10. Registered assumption entries

Fresh append-only block ASM-1000–1029 assigned to this bead (disjoint from
all prior blocks; highest previously-used id ASM-0982); entries 1009–1029
remain free.

| Registered id | Scope |
|---|---|
| **ASM-1000** | CODEVERT contract: critique+synthesis of CASK-CODE/1; licence space = architecture-family claims only, kernel-content explicitly out (either direction); instance-of stratum kept as the future kernel-content seam; steering-freeze compliance (G4/G5 design deferred behind G2) (§0, §5) |
| **ASM-1001** | Front-end unification: CODEVERT front-end := NLB-FE/1 on kot-query-code/1; mandatory-inverse REJECTED, evidence-gated ambiguity-set semantics adopted (ASM-0940/0941/0946 consumed); conformal claims pinned to the phrasing distribution (§2.4, §2.6, §4.2(4)) |
| **ASM-1002** | Product boundary + I/O contract: 8 measured query families; ANSWER/PATCH/CLARIFY/ABSTAIN with deterministic templates; one charged scripted clarification turn inside the measured system; clarification-rate gated co-report; BIO-span contract disclosure; workload model stipulated (§2.3, §3, §5, §6) |
| **ASM-1003** | Substrate rule: conservative 4-state extractor with provenance + blind repo-disjoint precision annotation; SQLite/Datalog twin serializations mandatory; full-distribution scoring with κ disclosed; unknown-dependent items answer ABSTAIN/unknown (§2.2, §3.3, §6) |
| **ASM-1004** | G1 census: pinned repo-selection rule, κ_q definition, blind precision sample, kill floor (planning values κ_q ≥ 0.5, precision ≥ 0.95; maintainer-adjustable at prereg) (§7-G1) |
| **ASM-1005** | G2 merged pilot: one pilot absorbing NLB-0-B(code) + ambiguity-set + aligned-SQLite (GS-C shared with DECONF-A2) + shuffled-store arms; CASK §8 kill set; non-decisive screen per the ASM-0944 discipline; gate-bar ordering G2 screen → G3 G-NLB → G4 binding win (§4.2(4)/(5), §7-G2) |
| **ASM-1006** | G4 commitments (prereg deferred): nine-arm ladder + deranged-store control; parity via ASM-0852/0853 mechanics; exact cluster-CP statistics + enumerated Holm family via ASM-0941; CASK binding-win conditions 1–3/5/6; GENERIC-store 2-pt margin = K-P3v2(4) input at scope; blind externally-adjudicated task gold (stage-1 insurance) (§3.4, §4, §7-G4) |
| **ASM-1007** | Edit path: v1 rename/insert_import execute as deterministic transforms with mechanical certificates; rename fail-closed on any `unknown` reference in the closure; neural draft + bounded verify-retry deferred to a generative G5b contract adopting CASK §6 mechanics (§2.5, §7-G5) |
| **ASM-1008** | EXTRAPOLATION (non-load-bearing): real-repo κ_q will clear the G1 floor and the G2 recipe will clear its screen bars; resolved by G1/G2 themselves |

---

## Epistemic register (what this critique relied on)

- **STIPULATED (registered block ASM-1000…ASM-1008):** every design choice
  above. Inherited binding stipulations consumed: ASM-0900/0901/0905,
  ASM-0940–0947 (NLB/1 rev-2, front-end + gate + statistics + pilot
  discipline), ASM-0814/0945 (gating + consumer obligations), ASM-0852/0853
  (FRONT parity mechanics), ASM-0960–0966 (DECONF stages, GS-C reuse),
  ASM-0007 (a5 structural-not-NSM), ASM-0001 (m0b coverage envelope).
- **MEASURED (each restated strictly inside its envelope):** a5 855/855 +
  7.82 µs and the code-world schema; a5-llm PASS +0.6602 with its
  does_not_license ceiling; a5-nl FAIL 41.6% + S2 kill (ROLE_DIR,
  contained-in 24 / where-defined 18); l3a-parse FAIL 47.6% (paraphrase
  0/261); f2b-replicate +0.1507 / LB +0.1053 at cost 0.103; f2b-transfer
  stage-1 endorsement A = 0.9784 (LB 0.9606, adjudication_valid);
  m0b 0.3542 (corpus-indexed per ASM-0001); g8 0/1000; the frontend/engine
  timings.
- **LIT-BACKED (through the completed Phase-0 reviews):** the 110M
  whole-frame band (ATIS 88.2 / Snips 92.8), TeCoD 83.6–89.2, Dr.Spider and
  COGS/CFQ robustness losses, the 0.85–0.95 closed-grammar band, conformal
  exchangeability + consistent-confident-inversion caveats, execution-
  feedback limits (PARSE.md §§2–5, §7); the no-bytes-honest-published-win
  sweep, BM25-mandatory and text-serialization-control warnings, matched-
  control no-precedent finding (RAG.md §§1–3, §6).
- **EXTRAPOLATION:** exactly one, ASM-1008, non-load-bearing, resolved by
  G1/G2; no premise or decision rests on it.

This document changes no frozen object, no verdict, no audit, no ruling; its
nine assumption entries are REGISTERED in registry/assumptions.jsonl
(append-only block ASM-1000–1008) by this design. No git, bd, or kb-sync
operation is performed.
