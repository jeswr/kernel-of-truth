# P9 — Publication & reporting plan (directives §7)

**Status:** pre-registration draft for maintainer sign-off, 2026-07-08 (rev 3 — RT-9
relabelling upgraded: the auditor is now a second-vendor model, Codex/GPT-5.5 via the
`codex` CLI, so audit language moves from "role-separated re-derivation" to "independent
cross-vendor re-derivation" — see §2 item 4, §3.5, §5.3. rev 2 — P7
red-team pre-freeze fixes applied: RT-14 anonymize-by-OVERLAY replaces the
scrub-the-bytes plan; RT-15 external timestamping made load-bearing in §1.2; RT-9
"role-separated re-derivation" relabelling + external replication offer on TAKE; the
TAKE-route pitch stated honestly as a fund-the-next-rung pitch, direction-only to 7B;
STOP-AND-PUBLISH-UNDECIDED added to the paper-type table per RT-1.
**Timeline note 2026-07-08:** calendar dates herein (M8/M9 in Jan 2027, venue-window
arithmetic) are pre-recompression; under the agentic-pace re-base (P3 §5) the write-up lands
days after whichever GNG closes the evidence — ~late Aug–Sep 2026 on an early
PIVOT/KILL/UNDECIDED route, ~Nov–Dec 2026 on the full Tier-5 route — so O-9 re-runs the
"nearest window ≥2 weeks after M8" rule against the re-based M8). Component P9 of the
operational research plan (`docs/research-plan/`). Governed by
`docs/kernel-design-directives.md` §7 (binding): the write-up is a first-class programme
phase producing (a) a top-tier-venue-grade, completely honest scientific paper — including
negative results, without spin — and (b) an accessible explainer-back to the maintainer;
both are DAG nodes with an owning role and reporting skills, gated by the honesty system, and
every paper claim traces to a registry entry + auto-report with no claim exceeding what the
pre-registered analysis supports.
**Author:** Fable planning agent (P9), for @jeswr. Coordination: sparq-org/sparq#1683.
**Consumes:** P1 (`01-hypotheses-experiments.md` — hypotheses, kill criteria, §4b envelopes,
§6 decision tree), P2 (`02-data-and-reporting.md` §5.5 — claim manifest + `--paper` scanner
mechanics), P3 (`03-operational-dag.md` §1.9 — the write-up node chain, GATE classes, GR-15,
open decisions O-9/O-10), P4 (`04-skills.md` — S8 `paper-claims`, S9 `paper-draft`, S10
`explain-back`, S6 `audit-result`, S12s `registry-check`), P5 (`05-agent-roles.md` — R9
Scientific-Writer, R8/R10 review identities, C-6 write≠grade), P8
(`08-stats-and-extrapolation.md` — §2.5 frontier-persistence rule, anchor classes), and the
literature reports L1 (`reports/lit-ontology-vector-priorart.md`), L2
(`reports/lit-primitives-grounding-priorart.md`), L3 (`reports/lit-llm-injection-priorart.md`)
plus companions (`reports/fixed-vectors-in-llms.md`, `reports/nsm-and-knowledge-injection.md`).

**Native-formalism note (directives §1).** The paper presents the kernel and axiom layer as
NATIVE (NSM-derived constructors, formal semantics on the kernel's own terms). RDF/OWL/SHACL/
DL appear in the manuscript in exactly two capacities and no other: (i) related-work
comparison lenses (the L1 prior art), (ii) one sentence noting that a lossy export projection
exists and is non-authoritative. No section frames semantic-web tech as a design target,
validation reference, or destination. `registry-check --paper` gains a lint term for this
(§3.4).

**What P9 owns vs what it reuses.** P2 §5.5 owns the *mechanics* (claims manifest, scanners);
P3 §1.9 owns the *node chain*; P4 owns the *skills*; P5 owns the *role*. P9 owns the
*content*: venue strategy and paper-type mapping per go/no-go route (§1), the manuscript
specification (§2), the paper-level honesty rules the lints enforce (§3), the explainer-back
specification (§4), and the trigger/wiring table that binds all of it to the DAG (§5).
Where P9 names a node, role, gate, or skill, it is the P3/P4/P5 name — no new machinery is
invented here except two small additions flagged explicitly (§3.4 lint terms, §5.3 companion
outputs).

---

## 1. Target venues and paper type

### 1.1 Paper type follows the computed route (P1 §6), not preference

The GNG-2/GNG-3 route is machine-computed from verdict objects (P2 §5.2). The paper's type,
headline, and claim scope are a pure function of that route. Pre-declared mapping:

| P1 §6 route | Paper type | Headline shape (template, exact claims filled from verdict objects) |
|---|---|---|
| **TAKE-TO-FRONTIER-LAB** | Main-track empirical paper on the surviving mechanism(s) | "A training-free, deterministic concept kernel [verifies / cuts cost of] LLM outputs on kernel-covered content: it beats [text-null + named strong baselines] at [measured rungs], with a measured scale trend" |
| **NARROW-AND-CONTINUE** | Same as TAKE but claim scope explicitly bounded to measured rungs; the missing rung/test named in limitations; possibly staged as workshop→main-track after the missing evidence lands | "…at [rungs]; whether the effect persists at [next rung] is unresolved (pre-registered test pending)" |
| **PIVOT (A6: E8-R + E8-D pass, mechanisms dead)** | Interpretability-instrument paper: kernel as external canonical label/coordinate space for SAE features + cross-version semantic-regression detection; the mechanism kills reported in the same paper (P1 §6 anti-overselling guard: "a pivot must publish the kills that forced it in the same document"). **E8-D evidence-labelling rule (P1 HC4, quoted here as required):** any PIVOT-A6 route citing E8-D must label its evidence **"planted-drift"** unless the natural version-pair secondary agrees | "Designed concept geometry predicts cross-model feature correspondence and detects semantic regressions [on planted drift, unless the natural secondary agrees]; the same kernel does NOT improve task correctness or efficiency beyond its own text rendering (pre-registered nulls reported in full)" |
| **PIVOT (A5-narrow: HC2 alone passes)** | Verification/assurance paper: deterministic axiom checking catches violation classes no text arm catches; no performance claims | "Structural verification catches what gloss text cannot: a measured constraint-violation delta, with everything else that failed" |
| **KILL** | Rigorous negative-results paper — a pre-declared success mode of the programme (P3 §1.9), not a consolation | "Deterministic, training-free concept kernels do not measurably help LLMs beyond their own text rendering at 135M–1.7B: a pre-registered, TOST-bounded negative across 8 mechanisms" |
| **STOP-AND-PUBLISH-UNDECIDED** (P1 §6 route 5; P7 RT-1) | "We could not power the answer at this spend" paper — a first-class outcome, not a failure to report: the pre-registered programme published with the blocking INCONCLUSIVE / INSTRUMENT-INVALID member(s) named, the pre-computed decidability bands quoted verbatim (P8 §3.2 pattern), the replication-buy cap shown as exhausted, and an explicit what-budget/n-would-decide statement; everything that did read out reported in full. Honest and publishable — TMLR-class | "At the pre-registered spend, [member(s)] remained undecidable (pre-computed decidable bands quoted); deciding them requires [stated n/budget]; all decided members are reported in full, and re-opening requires a fresh pre-registration and budget envelope" |

**The TAKE-route ceiling, stated honestly (P7 §6/§10).** Even a full TAKE route licenses
only **direction-only extrapolation to ~7B** (P8 §2.5; P1 §4b) — so any frontier-lab pitch
built on it is **structurally a fund-the-next-rung pitch**, never a "this works at frontier"
pitch. The GNG-3 dossier, the pitch deck (§5.3), and the paper's discussion each state this
ceiling in one explicit sentence, so the audience prices the pitch correctly. The plan's
honesty here is the pitch's credibility; pretending otherwise would be the actual risk.

Binding rule: **claim scope ⊆ verdict-object scope.** The paper may claim exactly what the
surviving verdict objects support — mechanism identity, measured rungs, M0b coverage slice,
and the P1 §4b envelope — and nothing else. The paper's scope declaration
(`paper/scope.json`, hypothesis IDs) is frozen before results-section drafting begins (P2
§5.5), so the route→scope mapping above is checkable, not aspirational. Both value theses
are reported in every route: every results table carries the full metric vector V
(accuracy/correctness, params, memory, inference compute, training compute — directives §2);
a correctness-route paper still reports the efficiency nulls and vice versa.

### 1.2 Candidate venues (with norms and negative-results fit)

Deadline dates drift year to year; the table records each venue's *cycle* and *norms*; exact
windows are verified by the Writer at GNG-2 (provisional pick) and fixed at paper.sign
(open decision O-9). P3's timeline puts the normal-route write-up at Dec 2026 – Jan 2027
(M8 = review-clean manuscript ≥2 weeks before any target window; M9 = Jan 30 submission);
a PIVOT/KILL/UNDECIDED route at GNG-2 pulls the write-up forward to ~Oct 2026.

| Venue | Track/type | Cycle (typical; verify at GNG-2) | Norms that matter here | Negative-results fit | Route fit |
|---|---|---|---|---|---|
| **TMLR** (Transactions on Machine Learning Research) | Rolling journal | Submit any time; ~2-month review | Acceptance = (i) claims supported by accurate, convincing evidence, (ii) audience interest — **explicitly no novelty/impact/significance bar**; open review; Reproducibility + Survey certifications exist | **Best in class** — the acceptance criteria are exactly directives §6/§7: supported claims, honest evidence | **Default home on every route; primary on KILL and both PIVOTs; strong fallback on TAKE/NARROW** |
| **NeurIPS** (main track) | Conference | Abstract ~mid-May, full ~late May; notify Sep | Paper checklist (claims-match-evidence, limitations, compute disclosure) maps 1:1 onto our registry artifacts; OpenReview; appendix + code encouraged | Moderate: rigorous negatives publishable when framing is a strong empirical study; reviewer variance real | TAKE/NARROW (mechanism paper); PIVOT-A6 (interpretability is in scope) |
| **ICML** (main track) | Conference | Full paper ~late Jan; notify May | Similar checklist culture; double-blind | Moderate, as NeurIPS | TAKE/NARROW — **the natural window for the normal-route timeline (M9 Jan 30)**, if the 2027 deadline falls after M8; else NeurIPS May |
| **ICLR** (main track) | Conference | Full paper ~late Sep; notify Jan | OpenReview public reviews; strong representation-learning + interpretability audience | Moderate | PIVOT/KILL/UNDECIDED pulled-forward route (~Oct 1 write-up) can hit ICLR if the window aligns; otherwise TMLR |
| **ACL / EMNLP main + Findings** (via ARR) | Conference / Findings | ARR rolling cycles (~every 2 months); commit to nearest conference | Responsible-NLP checklist; Findings absorbs sound-but-lower-excitement papers — a respectable landing for bounded-scope results | Findings: good for honest bounded/negative NLP results | TAKE/NARROW when the surviving mechanism is verification-of-language-output (HC1/HC2 framing); A5-narrow pivot |
| **COLM** (Conference on Language Modeling) | Conference | ~late Mar deadline | LM-centric; efficiency + verification + evaluation all in scope; younger venue, methodologically serious | Good — empirical-rigor culture | TAKE/NARROW efficiency-mechanism paper (HE series); fits the Mar window if ICML is missed |
| **ICBINB** ("I Can't Believe It's Not Better" — workshop series + negative-results initiative) | Workshop / non-archival or PMLR proceedings depending on year | Aligned to NeurIPS/ICLR host cycles | Dedicated venue for well-executed negative and surprising-null results in ML | **Purpose-built** | Companion venue on KILL (visibility + community), never the archival substitute — the archival negative paper goes to TMLR |
| **BlackboxNLP** (EMNLP workshop) | Workshop | ~Aug deadline | The interpretability-of-NLP community; SAE audience | Good | Companion on PIVOT-A6 |
| **MLRC / ReScience-class replication tracks** | Journal/track | Rolling | Replication + rigor culture | Good | Optional companion: the programme's registry design itself (a methods/tooling paper) — only if the maintainer wants a second output (§6, O-P9-4) |

Pre-declared venue policy (needs O-9 ratification, §6):

1. **Primary target by route:** TAKE/NARROW → nearest of {ICML, NeurIPS, COLM, ACL/EMNLP}
   whose window is ≥2 weeks after M8, chosen by mechanism audience fit (efficiency → ICML/
   NeurIPS/COLM; verification-of-text → ACL/EMNLP); PIVOT-A6 → ICLR or NeurIPS; A5-narrow →
   ACL/EMNLP or TMLR; KILL → **TMLR** (+ ICBINB companion); STOP-AND-PUBLISH-UNDECIDED →
   **TMLR**.
2. **TMLR is the standing fallback on every route**: one conference rejection cycle maximum
   before the manuscript goes to TMLR — the programme's obligation is the honest public
   record, not venue prestige-chasing (directives §7 "could score well and be accepted at a
   top-tier venue" is a *quality bar on the manuscript*, met at paper.review; it is not a
   license to sit on results through multiple cycles).
3. **The pre-registration is load-bearing at review time — and externally witnessed
   (P7 RT-15)**: the frozen registry (freeze dates in git history, `frozen-index.json`) is
   cited in the paper as the pre-registration record, and it does **not** rest on our git
   history alone: every freeze's `frozen_sha256` is externally timestamped at freeze time —
   published on the public coordination issue (sparq-org/sparq#1683) and, preferably, an
   OSF registration mirroring `frozen-index.json` (the `prereg freeze` post-step, P2 §1.1)
   — so reviewers can verify from a third-party surface that hypotheses/thresholds/analyses
   predate data. This is a genuine differentiator at any of these venues and the cover
   letter / checklist answers say so explicitly, citing the external timestamps.
4. **Double-blind compliance — anonymize by OVERLAY, never by scrubbing chained bytes
   (P7 RT-14).** A scripted scrub of identity strings inside the registry/log records would
   rewrite byte-hashed content, invalidating every `frozen_sha256` and `prev_sha256` — and
   with them the very pre-registration/reproducibility claim under review. Instead:
   (a) the registry, hash-chained logs, and verdict objects ship **byte-intact**; the
   in-record agent-identity strings (`runner-3` and kin) are already pseudonyms,
   and the reproducibility statement says so; (b) only **repo-external identifiers**
   (account names, profile ids, issue/repo URLs such as the coordination-issue link) are
   renamed via an **overlay mapping file** applied at snapshot-render time — the mapping is
   held privately and never enters the snapshot; (c) the anonymized snapshot is deposited
   via an anonymous-repository service for review and de-anonymized on acceptance.
   **Schema implication (cross-reference; the change lands in P2, decided before I-REG
   freezes):** the P2 record schemas keep account-identifying material **out of hashed
   record bytes** from the start — pseudonymous role identities inside hashed records,
   account bindings in an unhashed sidecar — so the overlay never has to touch a hashed
   byte. arXiv preprint timing follows the venue's policy and is a
   GATE-H (GR-8: external communication of results requires maintainer action) — decided at
   paper.sign.

### 1.3 What the paper is NOT allowed to be

- Not a systems/demo paper for the encoder (engineering value is an appendix + repo, not the
  claim).
- Not a manifesto for the kernel principle: the introduction states the hypothesis and the
  two value theses; the results state what survived; nothing argues past the verdicts.
- Not scoped beyond the H0 gate: if H0-YES was reached via one mechanism, the paper is about
  that mechanism (with the disjunction structure and the other members' outcomes reported);
  the strong A1 claim appears only if HS13 itself passed (P1 §1).
- Never a frontier-scale claim: P8 §2.5's prohibition (≥70B claims outright prohibited below
  Tier 5 + new measurement) binds the abstract, intro, and conclusion verbatim.

---

## 2. Paper outline (normative section spec)

The outline below is the paper.outline node's deliverable template. Slots marked `[R]` are
generated (never hand-written); slots marked `[W]` are Writer prose that must pass paper.lint.
Section order is fixed; per-route variation is confined to §§1, 5, 7 framing. Length target:
9 pages main + appendices (conference) or unbounded (TMLR), same content either way.

**Title** `[W]` — names the mechanism and the scope honestly. On KILL, the title contains
"pre-registered" and the negative (e.g. "…: a pre-registered negative result").

**Abstract** `[W, lint-checked]` — mandatory content, in order:
1. The hypothesis (kernel principle, two value theses) and that the programme was
   pre-registered with kill criteria before any run.
2. The design in one sentence: deterministic, training-free, NSM-derived concept kernel +
   native axiom sidecar + encoder/verifier machinery; evaluated against the kernel-as-text
   null and strong industrial baselines.
3. The headline results with effect sizes + CIs — negatives stated as flatly as positives;
   if the headline is negative, the negative IS the abstract's main sentence.
4. **The mandatory scale sentence** (lint-enforced, §3.3): measured rung range, the fitted
   trend if ≥3 rungs (with CI), and the extrapolation cap — e.g. "Effects are measured at
   135M–1.7B parameters; the fitted trend licenses direction-only statements to ~7B; we make
   no claims beyond that range." No abstract ships without this sentence.
5. Pointer to the open registry + code + logs.

**1. Introduction** `[W]`
- The question exactly as P1 frames it: is the kernel principle useful to LLMs at all; if
  so, which structure. Both value theses stated as first-class (correctness AND efficiency),
  with the full-metric-vector reporting discipline announced.
- The pre-registration story as a contribution in itself: registry frozen before runs,
  verdicts computed not narrated, negatives reported at equal prominence.
- Contributions list `[W over R]` — each contribution cites its verdict object(s); a
  contribution with no verdict trace cannot be listed (lint). Typical shape (TAKE route):
  (i) the kernel object (deterministic encoder, content-addressed identity, native axiom
  sidecar) with its measured quality card (X-series); (ii) the pre-registered 8-mechanism
  evaluation against text-null + strong baselines across a model-scale ladder; (iii) the
  surviving mechanism(s) with effect sizes, costs, and scale trends; (iv) the honest map of
  what died, with TOST bounds; (v) the open registry/reproducibility bundle.

**2. Related work** `[W]` — drawn from L1/L2/L3 + companions; the load-bearing positioning
items are pre-declared here so reviewers' likely objections are pre-empted:
- *L1 (ontology/KB vectors):* Numberbatch, KGE/OWL2Vec*-class embeddings (comparison lenses
  only — G1 arms), the Wieting–Kiela random-structure null (confronted head-on by HS1's
  random-atom-codebook arm), and the **mandatory Hyperdimensional Probe differentiation**
  (P1 HC4: any A6/E8 writeup must differentiate from arXiv:2509.25045).
- *L2 (semantic primitives/grounding):* NSM and its empirical status; DeepNSM as the
  published machine-authoring floor (HS-A/G9); why NSM is a *pinning* choice for
  deterministic identity, not a claim that primes are neurally real.
- *L3 (injection/fixed representations):* the interface-locality synthesis (Laws 1–3) as the
  paper's predictive frame — the results section explicitly scores the predictions;
  KEPLM lineage (dead at BERT scale), soft prompts/ToolkenGPT/GraphToken/xRAG/KBLaM (the
  trained-mediator topology the adapter follows), LCM/SONAR→CALM (the fixed-semantic-space
  scaling penalty the M2-output rider tests), RETRO/InstructRetro (external memory +
  absorption caveat), test-time-compute/PRM verification (HC3's frame), speculative decoding
  (verify-don't-generate), and the 2025 SAE corrections (feature absorption, seed
  non-identifiability) that both motivate and bound the A6 instrument.
- *Verification/neuro-symbolic:* AlphaGeometry/Logic-LM as the Law-3 template the correctness
  track instantiates.
- One paragraph on semantic-web-adjacent work, framed per directives §1: prior art compared
  against, never a target.

**3. The kernel: construction, native axiom layer, vectorisation** `[W over R]`
- 3.1 Concept records: NSM-derived explications (profile-1 lexicon, 65 primes), purely
  definitional stratum, content-addressed identity (canonical bytes → sha256; encoder pin
  `40e8c8ba…` convention); world facts and provenance excluded from the hash (directives §5).
- 3.2 The native axiom sidecar: the closed axiom grammar (kot-axiom/1 or NSM-native per the
  HS4/G4 fork outcome — the paper reports which fork won and why, citing G-verdicts); the
  litmus axiom ("a human has exactly two parents, one male, one female") as the
  expressiveness demonstration; endorsement/versioning semantics; **one sentence**: an
  optional lossy OWL/SHACL export exists for interoperability and is non-authoritative.
- 3.3 Vectorisation: construction B (Hadamard TPR within clauses; whitened unitary circular
  convolution across clauses/depth), determinism guarantees (X0), adversarial single-edit
  margins (X1), JL projection to host dimensions (X4), and the pre-registered *bans* —
  cosine-as-similarity banned by X3 (stated plainly: designed geometry is structural overlap,
  not meaning), decode gap (X2 51/54) on the ledger.
- 3.4 The machinery under test: decode-verify loop, axiom checker, adapter (E5 protocol),
  store (KOTK/2), cascade gate — each drawn as the arm it becomes in §4.

**4. Pre-registered experimental design** `[R + W]`
- The registry as method: freeze-before-run, hash-chained logs, verdict = pure function,
  run-vs-audit separation — described in the manuscript by its honest name, which since
  2026-07-08 is **"independent cross-vendor re-derivation"** (P2 G-6, P7 RT-9 as upgraded):
  the audit, adversarial-verification (red-team), and paper.review roles run on a genuinely
  independent second-vendor model — Codex/GPT-5.5, invoked via the `codex` CLI — not on the
  operator's Anthropic accounts, and the manuscript names the vendor split explicitly so
  the reader can price the claim. The word "independent" remains reserved for exactly this
  cross-vendor audit, the maintainer-level audit, and the external replication offer
  (§5.3); it is never applied to a same-vendor agent audit (one figure: the P2 lifecycle).
- The hypothesis table `[R]` — generated from `registry/hypotheses.json`: every hypothesis,
  its decisive experiment, verbatim kill criterion, rungs, and status.
- Baselines discipline: kernel-as-text null mandatory everywhere; RAG-over-text,
  matched-compute sampling, quantization, distillation, smaller-model-alone where
  applicable (G-8); arms never tuned harder than baselines (audit checklist).
- Scale ladder (R1–R5, T0–T3) and the slope discipline (≥3 rungs for adjectives).
- Statistics: one primary endpoint per experiment, Holm families, TOST for nulls, power —
  a half-page summary citing P8, with the SAPs in the appendix.
- M0b coverage: the kernel-expressibility number that bounds every claim, stated here and
  restated in every results subsection (G-7).

**5. Results** `[R + W]`
- 5.0 **The master results table `[R]`** — generated from `registry/status.json`: EVERY
  closed experiment, its hypothesis, verdict (closed vocabulary: PASS/FAIL/NULL/
  INCONCLUSIVE/INSTRUMENT-INVALID/INCOMPLETE-DATA), primary effect size + CI, rungs, cost.
  Omission is mechanical and forbidden (paper.lint cross-checks status.json). Ordering is
  by P1 tier structure, NOT by outcome — negatives are not sorted to the back.
- 5.1–5.n Per-mechanism subsections, one per hypothesis family actually read out, in tier
  order. Each subsection renders, in fixed order: the pre-registered statement (verbatim),
  the kill criterion (verbatim — PASSes never travel without the bar they cleared), the
  primary endpoint result (effect size + CI + test), Holm-corrected secondaries, the full
  metric vector V table for efficiency-relevant results (Pareto plots for HE series), and
  the verdict sentence copied from the verdict object. Negative/inconclusive subsections
  are structurally identical to positive ones — same table set, same length discipline, in
  place (front-and-centre where they occur in the tier order), not aggregated into a
  "limitations" afterthought.
- Where a result is INCONCLUSIVE, the paper says INCONCLUSIVE and gives the TOST bound that
  was not met; the pre-computed decidability statement (e.g. F2's "decidable when true
  closure ≤0.35 or ≥0.65" — P8 §3.2) is quoted so "nearly passed" spin is impossible.
- 5.final The H0 gate readout `[R]`: the disjunction/`family-h0` Holm result and the
  computed P1 §6 route, stated as the programme's answer to its own top question.

**6. Scale analysis and extrapolation** `[R + W]`
- Per surviving mechanism: the WLS fit (form, slope, 90% CI), the prediction interval at the
  target rung, the anchor class (CONSISTENT / DIRECTIONALLY-CONSISTENT /
  ANCHOR-CONTRADICTING / NO-ANCHOR) against the published scaling anchors (P8 §2.4 table:
  Kaplan/Hoffmann discipline, test-time-compute, LCM/CALM penalty, RETRO range,
  frozen-embedding no-anchor, Law 2).
- **The envelope table `[R]`** — the P1 §4b rows for every reported finding, verbatim. Every
  extrapolation sentence in the paper quotes or cites its row (lint-enforced).
- The honest statement of what is NOT licensed: one-OOM cap, direction-only defaults,
  ≥70B prohibition, and (where relevant) "no published scaling law covers this mechanism"
  in so many words.

**7. Limitations** `[W, content floor lint-checked]` — mandatory minimum content:
M0b coverage bound (all claims live on the covered slice); rung caps per finding; the X2
decode gap wherever decode is load-bearing; the X3 cosine ban and what it precludes;
single-family/site confounds where they exist (e.g. E8's history); instrument-limited
results (X1-grounding pattern); annotator-dependence of R0 fork verdicts; the
kernel-as-text null's strength and what parity with it would have meant / did mean;
authoring-cost assumptions (HS-A outcome); compute budget honesty (what was not run and
why, incl. any tier the maintainer declined).

**8. Discussion** `[W]` — scores the L3 Laws' predictions against outcomes (did
verifier-side beat consumer-side as predicted?); what the outcome means for the
external-structure-into-LLMs literature; on TAKE routes, the §1.1 ceiling sentence (the
frontier pitch is structurally a fund-the-next-rung pitch, direction-only to ~7B) stated
explicitly; on PIVOT/KILL routes, what the negative teaches
(e.g. "the text rendering carries the value — structured canonical form adds nothing
measurable at these scales" is itself a finding the field can use).

**9. Reproducibility statement + appendices** `[R]`
- A: the evidence bundle (r-final): registry snapshot, frozen-index shas, results-log tail
  hashes, verdict objects, spend ledger.
- B: full SAPs per experiment (P8 §1.9 instantiations, verbatim).
- C: encoder/corpus/model pins; harness manifests; how to re-run every analysis
  (`verdict-gen` is deterministic — byte-identical reproduction is the claim, and the
  auditors' **independent cross-vendor re-derivation** records are cited, named exactly
  that, with the vendor split stated: audits performed by Codex/GPT-5.5 via the `codex`
  CLI, a different vendor/model from every run identity (P7 RT-9 as upgraded 2026-07-08)).
- D: the amendment log, in full (every amendment: date, kind, rationale — nothing edited
  silently is the point).
- E: agent-contribution disclosure (O-10): which roles (runner/analyst/auditor/writer)
  were agents, which human acts occurred (GATE-H inventory), maintainer as accountable
  author.
- F: negative-space table: exploratory (quarantined) analyses that exist but are uncitable
  (G-13), listed by title only — so reviewers can see the garden of forking paths was
  fenced, not hidden.

---

## 3. Honesty binding (paper-level rules; each names its enforcement)

The mechanics are P2 §5.5 / GR-15; this section fixes the *rules the mechanics enforce* so
the Writer, the lint, and the reviewer all read from one list. R-1…R-12 below are the
paper.lint rule set.

### 3.1 Claim tracing (hard rules)

- **R-1 Every quantitative or verdict-bearing sentence carries a `{{claim:<id>}}` anchor**
  resolving to a `paper/claims.json` row `{claim_id, text, experiment, verdict_path,
  verdict_sha256, fields_cited}`. No row → the sentence cannot ship. *(registry-check
  --paper, fail-closed.)*
- **R-2 No claim exceeds the pre-registered analysis.** Operationalised: the claim's
  direction and magnitude must be entailed by the cited verdict-object fields alone —
  a claim asserting anything computed outside the pinned analysis script is exploratory
  and uncitable (G-13). Wording may compress; it may not extend. *(claims-table
  cross-check: claim-regex vs cited fields; paper.review re-derives every sentence.)*
- **R-3 PASS-PENDING-AUDIT is not PASS.** Never citable; the lint hard-fails. *(P2 §5.5.)*
- **R-4 Every PASS travels with its verbatim kill criterion** — in the results subsection,
  adjacent, not footnoted. *(GR-5/GR-15 lint term.)*
- **R-5 Completeness:** every CLOSED experiment whose hypotheses are in `paper/scope.json`
  appears in the §5.0 master table AND has a subsection or an explicit pointer; scope.json
  is frozen before results drafting. *(status.json cross-check.)*
- **R-6 Numbers are quoted, never retyped:** any numeral in results/abstract must equal its
  verdict-object field to display precision; display rounding only (P8 C-7). *(scanner
  compares numerals in anchored sentences to cited fields.)*

### 3.2 Negative and inconclusive results — framing without spin

- **R-7 The verdict vocabulary is closed in prose too.** FAIL is written "failed its
  pre-registered criterion"; NULL is written "equivalent to [baseline] within the
  pre-registered margin (TOST)"; INCONCLUSIVE is written "inconclusive — neither the
  criterion nor the equivalence bound was met". **Banned-phrase list** (extends P2 §3.1's
  impostor grep, applied to the manuscript): "promising trend", "nearly significant",
  "approaching significance", "directionally encouraging", "suggestive of", "on the right
  track", "partial pass", "qualified success", "effectively passed" — for any experiment
  whose verdict is not PASS. *(lint regex set, hard fail.)*
- **R-8 Placement equality.** Negative results appear in tier order in §5, with the same
  structural template (tables, CIs, V vector) as positives; if the headline result is
  negative, it leads the abstract and the contributions list. *(paper.review checklist
  item; §5.0 ordering is generated, unre-orderable.)*
- **R-9 A pivot publishes its kills.** On PIVOT routes the abstract and intro state the
  mechanism kills in the same document that announces the pivot (P1 §6 guard, applied to
  the manuscript). *(scope.json on a pivot route must include the killed hypotheses;
  R-5 then forces them into the paper.)*
- **R-10 No silent absence.** Anything pre-registered but not run appears in the master
  table as its non-terminal status with the reason (budget-declined, gated-off, superseded).
  *(status.json enumerates all registry entries in scope, not just CLOSED.)*

### 3.3 Extrapolation limits in the abstract and claims

- **R-11 The abstract's mandatory scale sentence** (§2 Abstract item 4): measured range +
  license level + cap. The lint requires, in the abstract: (a) at least one numeral-range
  matching the measured rungs of every headline claim; (b) no scale adjective ("scales",
  "at scale", "will scale", "persists at larger models", "frontier") anywhere in the paper
  for an experiment whose `scale_language_licensed` is below "slope" (G-12); (c) any
  "expected to persist at X" phrasing only where all five P8 §2.5 conditions hold, with the
  envelope row cited. *(G-12 + --paper extrapolation regex set + envelope-citation check.)*
- **R-12 Every extrapolation statement quotes its envelope.** The P1 §4b row (verbatim, via
  `extrapolation_envelope_verbatim`), the fitted form + PI, and the anchor class; NO-ANCHOR
  findings must include the literal words "no published scaling law covers this mechanism".
  ≥70B claims are prohibited outright (P8 §2.5). *(--paper scanner.)*

### 3.4 New lint terms P9 adds (to be implemented in S8/S12s; small, mechanical)

1. **Native-formalism term:** flag any sentence in §§1–4 of the manuscript matching
   RDF/OWL/SHACL/description-logic regexes that is not inside the related-work section or
   the single export-note sentence; fail if it frames them as target/reference/destination
   (fixed phrase list). (Directives §1 applied to the paper.)
2. **Banned-phrase list of R-7** (spin vocabulary) as a hard-fail regex set over anchored
   sentences whose cited verdict ≠ PASS.
3. **Abstract content check of R-11(a)**: abstract must cite ≥1 claim row per headline
   contribution and contain the scale sentence pattern.
4. **Limitations content floor (R-13):** §7 must cite M0b, the X2 gap (if decode is
   load-bearing in scope), and every envelope row of a headline claim — checked as
   presence-of-citation, wording free.

### 3.5 Process binding (who does what, already fixed elsewhere, restated as binding here)

Writer (R9, `kern/fable-writer-1`) drafts; the Writer never grades, audits, or touches
verdict tooling (P5 C-6, toolset exclusion). paper.lint (S8/S12s engines) must pass; then
paper.review — adversarial re-derivation by an auditor identity that is not the Writer
(R8, `codex-gpt5.5/auditor-2`: the cross-vendor Codex/GPT-5.5 auditor invoked via the
`codex` CLI, per the 2026-07-08 maintainer decision superseding the backup-account plan)
with a committed review record; R10 red-team (`codex-gpt5.5/redteam-1`, same cross-vendor
identity class) produces a venue-style mock review (scores + weaknesses) as advisory
input to paper.sign. paper.sign and paper.submit are GATE-H (maintainer). The identical
chain (xb.lint, then delivery gate) binds the explainer.

---

## 4. The accessible explainer-back (deliverable spec)

**Audience & register.** The maintainer as a person, not a reviewer: plain language,
non-expert-friendly (directives §7 "clearest possible terms"). Test applied at xb.lint
review: every sentence understandable by a technically curious non-ML-researcher; every
term of art either avoided or glossed inline on first use; no statistics vocabulary —
statistical outcomes are rendered as "we agreed in advance that X would count as success;
we measured Y; by that pre-agreed rule this is a [pass/fail/genuine tie/can't-tell]".

**Format.** `reports/explainer-back.md`, committed. One page (≤~900 words) main body +
appendices. Every number carries its experiment id in parentheses (the honesty hook — ids
resolve to verdict objects; xb.lint checks them exactly as paper.lint checks claims).
Delivered at xb.deliver with a live Q&A; the questions and answers are appended to the
file and committed (P3 §1.9 — a first-class node, not a courtesy).

**Required contents, in order (each a mandatory slot; the S10 `explain-back` skill fills
slots from verdict objects + the computed GNG route):**

1. **What we set out to test** (≤3 sentences): the kernel idea in plain words ("a small,
   fixed dictionary of machine-readable concept definitions, built once, never trained")
   and the two ways it could pay off (catching model mistakes; making small models do big
   models' work at lower cost).
2. **What we found** — one plain sentence per hypothesis family read out, each tagged
   [worked / didn't work / genuine tie / couldn't tell] (the four tags map 1:1 to
   PASS/FAIL/NULL/INCONCLUSIVE; the mapping is stated once in a footnote). Failures are
   listed in the same list, same grammar, same prominence. Example shape: "Checking the
   model's output against the dictionary caught N% of planted definition errors that a
   plain-text glossary missed (e9-c) — this worked."
3. **What it means** (≤5 sentences): the practical reading — what one could build or should
   not build on this evidence; which value thesis (if either) survived; explicitly, what
   the text-null comparison means in plain words ("whenever we say the kernel helped, we
   mean it helped MORE than just pasting the same definitions in as text — otherwise the
   fancy machinery isn't earning anything").
4. **What scale it holds at** — the envelope translated to plain words, one line per
   surviving finding: "tested on models of size A–B; the trend lets us reasonably guess up
   to ~C; beyond that, honestly, nobody knows — we did not test it and the literature
   doesn't settle it". The one-OOM cap and any NO-ANCHOR finding stated in exactly this
   register. No plain-language sentence may be more confident than its envelope row
   (xb.lint: simplify wording, never claims — GR-15's explainer clause).
5. **What it cost** — total spend vs the pre-approved envelope, by tier; what was declined
   or gated off and what that means for the conclusions.
6. **Go / no-go recommendation** — the machine-computed P1 §6 route (TAKE / NARROW / PIVOT
   / KILL) stated plainly, with the two or three verdicts that drove it, and what the
   recommendation asks of the maintainer next (fund rung X; pitch narrowly scoped Y;
   pivot to Z; stop and publish the negative). If the maintainer overrode the computed
   route at GNG-2/3, both the computed and ratified routes appear.
7. **If you only remember three things** — three sentences, chosen by the Writer, each
   carrying its experiment id.
8. **Appendix Q1: the honest one-pager of everything that died** — the full negative list
   with one plain sentence each (the same content as the paper's master table, rendered
   readable).
9. **Appendix Q2: live Q&A record** — appended after xb.deliver.

**What the explainer must never do:** introduce a number absent from a verdict object;
average, re-round, or "ballpark" across experiments; use analogy in place of a claim (analogy
is allowed as decoration only, flagged "loosely speaking"); soften a FAIL ("mixed results",
"room for improvement") — R-7's banned list applies verbatim at xb.lint.

---

## 5. DAG wiring and trigger conditions

### 5.1 The node chain (P3 §1.9, restated with P9 ownership annotations)

Owning role for all content nodes: **R9 Scientific-Writer** (`kern/fable-writer-1`, Fable
tier — P5 §R9). Reporting skills: S7 `report-gen` (evidence bundle), S8 `paper-claims`
(claims table + lint engine), S9 `paper-draft`, S10 `explain-back`, S6 `audit-result`
(paper.review mode), S12s `registry-check --paper` (the executable honesty gate).

| Node | Kind | Skill | Gate | P9 content spec |
|---|---|---|---|---|
| r-final | AUTO | S7 | — | §2 Appendix A contents (evidence bundle = reproducibility appendix, zero hand-written numbers) |
| paper.claims | AUTO | S8 | — | claims.json rows per §3.1; scope.json frozen first (R-5) |
| paper.outline | AUTO (Writer) | S9 | — | §2 outline instantiated for the computed route (§1.1 mapping); provisional venue pick per §1.2 policy recorded on the coordination issue |
| paper.draft | AUTO (Writer) | S9 | — | §2 section spec; R-1…R-13 authoring rules |
| paper.lint | AUTO-GATE | S8 + S12s | fail-closed | §3.1–§3.4 rule set incl. the four new lint terms |
| paper.review | GATE-A | S6 (paper.review mode) | CONFIRMED required | adversarial re-derivation; auditor ≠ Writer (cross-vendor `codex-gpt5.5/auditor-2` via the `codex` CLI); + R10 venue-style mock review (advisory) |
| paper.sign | **GATE-H** | — | maintainer | manuscript + authorship (O-10) + venue/timing (O-9) + preprint decision (§1.2 item 4) |
| paper.submit | **GATE-H** | — | maintainer (GR-8) | submission per §1.2 policy; one-cycle-then-TMLR fallback rule |
| xb.draft | AUTO (Writer) | S10 | — | §4 slots 1–8 |
| xb.lint | AUTO-GATE | S8 + S12s | fail-closed | same engine as paper.lint + §4's plain-language constraints (simplify wording, never claims) |
| xb.deliver | **GATE-H** | — | maintainer | delivery + live Q&A appended and committed (§4 slot 9) |

Hard orderings (P3 §1.10, binding): `paper.lint ∧ paper.review ≺ paper.sign ≺
paper.submit`; `paper.sign ≺ xb.deliver`; the whole chain runs on **every** GNG route,
including PIVOT and KILL.

### 5.2 Trigger table — which go/no-go outcome produces which paper, when

| Trigger (computed at) | Route | Paper produced | Primary venue (per §1.2 policy) | Explainer-back | Timing |
|---|---|---|---|---|---|
| GNG-3 = TAKE-TO-FRONTIER-LAB | TAKE | Mechanism paper, full scale analysis (a-extrap-5 slope level) | Nearest of ICML/NeurIPS/COLM/ACL by mechanism audience, window ≥2 weeks after M8 | Yes — includes the frontier-pitch recommendation and its scoping, stated plainly as a **fund-the-next-rung** pitch (direction-only to ~7B; §1.1 ceiling note) | Normal path: write-up P-7 (Dec 07–Jan 12), sign/submit/deliver P-8 (Jan 12–30) |
| GNG-3 = NARROW-AND-CONTINUE | NARROW | Same paper, claims bounded to measured rungs; missing rung named in limitations; venue may be Findings/COLM/TMLR if the bounded claim underfills a main track | As TAKE, or TMLR | Yes — recommendation = fund exactly the missing decisive test | Normal path |
| GNG-2 = PIVOT (A6 alive) and Tiers 4–5 declined | PIVOT-A6 | Interpretability-instrument paper + mechanism kills in the same document (R-9) | ICLR or NeurIPS (whichever window fits the pulled-forward date); BlackboxNLP companion optional | Yes — recommendation = pivot scope | **Pulled forward** (~Oct 01 start per P3 §5); r-final triggers off GNG-2 instead of GNG-3 |
| GNG-2 = PIVOT (A5-narrow: HC2 alone) | PIVOT-A5 | Assurance/verification paper, no performance claims | ACL/EMNLP (ARR) or TMLR | Yes | Pulled forward |
| GNG-2 or GNG-3 = KILL | KILL | Rigorous negative-results paper (full statistics, registry, raw logs; the pre-registration is the methods contribution) | **TMLR** primary; ICBINB companion (maintainer's call, §6) | Yes — recommendation = stop; what the negative teaches; archive statement | Pulled forward on a GNG-2 KILL; else normal path |
| GNG-2 or GNG-3 = STOP-AND-PUBLISH-UNDECIDED | UNDECIDED | "Could-not-power-the-answer" paper per §1.1: blocking members named, decidability bands quoted verbatim, replication-buy cap shown exhausted, what-budget/n-would-decide stated; spending stops (the §5 caps are terminal on this route) | **TMLR** | Yes — recommendation = stop and publish; re-opening requires a fresh pre-registration + fresh maintainer-approved envelope (P1 §6 route 5) | Pulled forward on a GNG-2 route; else normal path |
| Any route, conference rejection | — | Same manuscript, revised per reviews (revisions re-enter at paper.draft; paper.lint/review re-run — a review-driven change to claims is impossible without re-tracing) | TMLR after at most one conference cycle (§1.2 policy 2) | (already delivered) | Rolling |

Notes binding the table: (i) r-final's dependency is "GNG-3, or GNG-2 on a
PIVOT/KILL/UNDECIDED route that declines Tiers 4–5" (P3 §1.9) — the trigger rows above
instantiate exactly that; (ii)
a positive HS13 anywhere triggers immediate independent replication BEFORE any claim enters
paper.claims (P1 HS13; the claims table refuses a row citing an unreplicated
anchor-contradicting result per P8 §2.4's ANCHOR-CONTRADICTING consequence); (iii) the
explainer is delivered after paper.sign on every route — the maintainer never learns the
programme's outcome from a submitted PDF.

### 5.3 Companion outputs (pre-declared so they cannot become uncontrolled claim surfaces)

Any secondary external artifact — ICBINB/BlackboxNLP companion, arXiv preprint, blog-style
summary, frontier-lab pitch deck (TAKE route), talk slides — is generated from the same
claims table and passes the same `--paper` lint before any GATE-H exposure (GR-8 covers all
external communication; GR-15's lint is the uniform pre-gate). No companion may contain a
claim absent from `paper/claims.json`.

**Frontier-lab pitch deck, additional binding rules (P7 RT-9 + §6/§10):**

1. **Honest audit labelling** — every "audited" claim in the deck is described as
   independent cross-vendor re-derivation, naming the vendor split (audits by Codex/
   GPT-5.5 via the `codex` CLI; runs by Anthropic-model agents — P7 RT-9 as upgraded
   2026-07-08); the deck's methods slide says so in one sentence, and "independent" is
   never used for any same-vendor agent audit.
2. **Pre-committed external replication offer** — before any pitch exposure, the programme
   commits (recorded on the coordination issue) to one genuinely external replication of
   any headline positive: artifacts + harness public, one named outside person or lab
   invited to re-run the pinned analysis. The offer is cited in the deck.
3. **The ceiling sentence** — the deck states, in one explicit sentence, that even the full
   TAKE route licenses direction-only claims to ~7B, so what is being pitched is funding
   the next rung of measurement, not a claim that the mechanism works at frontier scale
   (§1.1 ceiling note; P8 §2.5). If m0b.gate fired below the GNG-0 threshold, the deck also
   carries the NICHE-SCOPE banner and the coverage-growth cost line (P3 m0b.gate), priced
   from the P6 §2.2 authoring-cost figure.

---

## 6. Open decisions for the maintainer (@jeswr)

1. **O-9 ratification (venue policy).** §1.2's pre-declared policy: route→venue mapping,
   the "one conference cycle maximum, then TMLR" fallback, and TMLR-primary on KILL.
   Provisional pick due at GNG-2; final at paper.sign. Default if unratified: policy as
   written.
2. **O-10 ratification (authorship & disclosure).** Default (P3): maintainer sole human
   author, agent roles disclosed in the contributions/appendix E; confirm whether any
   venue's authorship policy requires more (the Writer checks the chosen venue's
   AI-contribution policy at paper.outline and surfaces it at paper.sign).
3. **Preprint policy.** arXiv timing relative to submission (GR-8 GATE-H): default =
   preprint at paper.submit time where the venue allows; you may prefer to hold until
   acceptance.
4. **Companion outputs.** Yes/no on: ICBINB companion on KILL; BlackboxNLP companion on
   PIVOT-A6; a separate methods/tooling paper on the registry-honesty system (MLRC/TMLR) —
   each is extra Writer time, zero new claims (§5.3).
5. **Double-blind anonymization approach.** §1.2 item 4 (anonymize-by-OVERLAY: hashed
   records ship byte-intact with their pseudonymous in-record identities; only repo-external
   identifiers are renamed via a privately-held overlay mapping) — sign off the approach.
   The repo IS the reproducibility claim: scrubbing identity strings out of hashed bytes
   would break every `frozen_sha256`/`prev_sha256` chain reviewers are asked to verify
   (P7 RT-14), so the overlay is the only approach compatible with the pre-registration
   claim; the corresponding P2 schema rule (account-identifying material kept out of hashed
   bytes) must land before I-REG freezes.
6. **Explainer delivery format.** Written + live Q&A appended (default), or written-only.
   The directives make the explainer a first-class deliverable; the live Q&A is the
   recommended default because the Q&A record has repeatedly been where scope
   misunderstandings surface.

---

## 7. Component summary (one paragraph, for the plan index)

P9 turns directives §7 into an operational publication programme: the paper's type, venue,
and claim scope are pure functions of the machine-computed go/no-go route (TAKE/NARROW →
main-track mechanism paper at ICML/NeurIPS/COLM/ACL, with any frontier pitch honestly framed
as a fund-the-next-rung pitch, direction-only to ~7B; PIVOT → interpretability or assurance
paper that publishes its own kills; KILL → a TMLR negative-results paper as a pre-declared
success mode; STOP-AND-PUBLISH-UNDECIDED → a TMLR "could-not-power-the-answer" paper with
the decidability bands quoted; TMLR the standing fallback on every route); the manuscript follows a
fixed outline whose results and envelope tables are generated from the registry, whose every
claim anchors to a verdict object, and whose abstract must carry the measured-range +
extrapolation-cap sentence; honesty is enforced by the executable lint chain (R-1…R-13,
banned-spin vocabulary, scale-language license, native-formalism term) plus adversarial
review by a non-Writer identity; the maintainer receives a one-page plain-language
explainer-back (what-we-found / what-it-means / what-scale-it-holds-at / cost / go-no-go,
negatives at equal prominence, live Q&A committed); and both deliverables are the existing
P3 DAG nodes (r-final → paper.* → xb.*), owned by R9 Scientific-Writer with skills S8/S9/S10,
gated by GR-15 and GATE-H, running on every route out of GNG-2/GNG-3 — including the one
where everything died.
