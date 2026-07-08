# P7 — Adversarial red-team / completeness critique of the research plan

**Status:** red-team report, 2026-07-08. Component P7 of the operational research plan
(`docs/research-plan/`). Governed by `docs/kernel-design-directives.md` (binding).
**Scope reviewed:** P1 (hypotheses/experiments), P2 (data & reporting backbone), P3
(operational DAG), P4 (skills), P5 (agent roles), P6 (resources), P8 (stats &
extrapolation), P9 (publication & reporting), plus `reports/lit-llm-injection-priorart.md`
(L3) and the directives themselves.
**Author:** Fable red-team agent (P7), for @jeswr. Coordination: sparq-org/sparq#1683.
**Stance:** hard skeptic, playing the hostile frontier-lab reviewer AND the hostile
methodologist. Findings are numbered RT-1…RT-24 with severity
(**CRITICAL** = can invalidate the programme's answer or its honesty claim if unfixed;
**MAJOR** = materially weakens a verdict, a pitch, or an execution path;
**MINOR** = fixable friction/inconsistency), each with a concrete fix and where it lands.

---

## 0. Verdict up front

**Overall readiness: FIX-THEN-EXECUTE.**

The honesty backbone (P2), the statistics (P8), and the kill-tree economics (P1 §5:
~$40 to the pivot readout, ~$180–650 to a decisive NO) are genuinely excellent — top-decile
relative to published pre-registered ML work, and the plan confronts most of its own hard
priors (kernel-as-text null everywhere, M2-output pre-declared expected-fail, HS13
double-gated, E8 recalibrated to the seed-stable subset, the LCM/CALM penalty and
Kaplan→Chinchilla misprediction wired into the extrapolation rules). Phase-0
infrastructure build can start immediately.

But three CRITICAL findings must be fixed **before the affected registry entries freeze**,
or the programme can (1) end without a routable answer, (2) win its headline correctness
experiment against a strawman of the one baseline Law 2 says will actually compete, and
(3) rest its entire correctness track on an instrument whose model-facing interface is
never specified in the plan. A further cluster of MAJOR findings (sample-size
inconsistencies, unblinding leak-path, supersession semantics, coverage/ecological
validity, authoring-cost accounting) are pre-freeze edits, not redesigns. Nothing found
requires redesign of the architecture, the backbone, or the DAG topology.

---

## 1. Axis 1 — DECISIVE: can the programme end without an answer?

### RT-1 (CRITICAL) — The global decision tree is non-exhaustive; the *most probable* messy outcome has no route.

P1 §6's four routes are: TAKE (needs ≥1 PASS + slope), NARROW (needs ≥1 mechanism PASS at
≥2 rungs, or E8-R PASS), PIVOT (needs H0-NO **plus** a surviving A6/HC2), KILL (needs
H0-NO **plus** E8-R fail **plus** HC2 fail). H0-NO (P1 §1) requires all four of
{F2, E9-full+E9-C, F4, F6} to be **TOST-bounded nulls or explicit criterion-kills**.

Now walk the plausible outcome the programme's own priors predict: no mechanism PASSes,
but one or more of the four decisive experiments lands **INCONCLUSIVE** (E1 already did
exactly this; P8 §3.2 pre-computes that F2's gap-closure is undecidable in the true-value
band 0.35–0.65) or **INSTRUMENT-INVALID** (F6's instrument failed once already — see
RT-19). Then: no route's first-match pattern fires. The tree — which P2 §5.2 encodes as
verdict-object expressions and which GNG-2 evaluates mechanically — evaluates to
*nothing*. The maintainer gets a dossier with no computed route, and the "decisive
go/no-go" promise fails at exactly the moment it matters. The anti-overselling guard
("narrow-and-continue not invocable twice for the same missing evidence") caps repeat
spending but does not supply a route either.

Related soft spot: HC3's "INCONCLUSIVE buys one replication before verdict" is the only
replication-cap in the suite; no global rule caps how many INCONCLUSIVEs across the
programme may buy re-runs before the answer is declared "not decidable at this budget".

**Fix (pre-GNG-0, edits P1 §6 + a-h0.reg):** add a fifth terminal route, e.g.
**STOP-AND-PUBLISH-UNDECIDED** — pattern: no PASS, and the H0-NO pattern not met because
≥1 member is INCONCLUSIVE / INSTRUMENT-INVALID after its (single, pre-declared)
replication buy. Action: publish with the pre-computed decidability bands quoted (P9
R-7 already bans spin), state what budget/n would decide it, and treat the route as a
first-class outcome in P9 §1.1's paper-type table (it is a "we could not power the
answer at this spend" paper — honest and publishable at TMLR). Add a global cap: at most
one replication buy per experiment, at most two programme-wide, pre-declared.

### RT-19 (MAJOR, interacts with RT-1) — F6's INSTRUMENT-INVALID blocks the decisive-NO clause (d).

H0-NO clause (d) requires "F6 toy rung kills HE6 (or text-scaffold matches it)". But F6's
first verdict rule is INSTRUMENT-INVALID (trained arms must beat step-0 cloze), and the
instrument *already failed once* at E1. If it fails again, F6 produces neither a kill nor
a null — and H0-NO becomes permanently unreachable regardless of what F2/E9/F4 say. A
decisive NO should not be hostage to a cloze instrument the programme knows is fragile.

**Fix:** pre-register the instrument repair itself (what changes vs E1, and the
instrument's own pass bar) inside f6.reg; and amend H0-NO clause (d) to
"F6 kills HE6, OR F6 is INSTRUMENT-INVALID after the pre-registered repair — in which
case HE6 is scored *undetermined-not-supporting* and H0-NO may still be declared with
the caveat rendered verbatim". The literature prior (frozen-embedding penalty, Law 1/2)
justifies treating an unmeasurable HE6 as non-supporting rather than blocking.

### RT-6 (MAJOR) — Supersession chains: which experiment ID feeds the tree?

G-3's escape valve for post-unblinding changes is a new experiment ID
(`f2-rev2`, `supersedes: f2`). Correct and honest — but *no document specifies how the
decision tree, a-h0, F-H0 Holm family, or GNG dossiers treat a superseded lineage*. If
f2 = FAIL and f2-rev2 = PASS, does the tree read the latest? Both? A motivated operator
could iterate `-revN` until a PASS lands, each step individually disclosed, the chain
collectively a garden of forking paths. Nothing in P2/P3 caps revisions or defines
lineage semantics.

**Fix (P2 §1.4 + P3 gate-eval):** (a) lineage rule: gates read the **latest** ID but the
verdict object must embed the full lineage with every predecessor verdict, and the report
renders them adjacently; (b) a revision that flips FAIL→PASS requires the full
adversarial audit *plus* red-team (R10) memo; (c) cap: ≥2 revisions of the same
experiment force the STOP-AND-PUBLISH-UNDECIDED treatment for that mechanism.

### RT-21 (MINOR) — Two kill criteria have exploitable conjunctions.

HC1: dead if the gloss arm covers ≥90% of the catch set **at ≤ arm 3's cost**. If gloss
covers 95% at 1.05× cost, HC1 survives on a cost technicality. HC2's "<3× best text arm"
multiplier: if the text arm catches ~0, 3× of ~0 is trivially cleared — the 0.80 absolute
floor saves this, but the 3× clause adds nothing when text arms floor out and should not
be quotable as "3× better than text" without the absolute rates adjacent.

**Fix:** HC1 kill: drop the cost conjunct or loosen to ≤1.5×; HC2: report both clauses'
raw rates verbatim in the verdict (template slot), ban the "N× better" phrasing when the
text-arm denominator's Wilson upper bound < 0.05.

### RT-12 (MAJOR) — "R3 iff sign" rung extension is a data-dependent design decision with no pre-specified rule.

E9 and HC1 extend to R3 "iff a sign exists" — undefined (primary_reject at both rungs?
point estimate > 0 at one?). Worse, "PASS at ≥2 rungs" does not fix conjunction
membership: if R1 passes, R2 fails, R3 (run because of R1's sign) passes, is HC1 "PASS at
2 rungs"? Under IUT the claim's rung set must be declared before the rungs are read, or
the conjunction is selected post hoc.

**Fix (P8 §1.9 field 12, freeze-time lint):** every multi-rung claim declares its rung
set at freeze; conditional rungs declare the extension trigger as a machine predicate
over the frozen fields (e.g. `primary_reject@R1 AND primary_reject@R2`), and extension
rungs may only *strengthen* an already-satisfied conjunction (report as "PASS at R1–R2,
replicated at R3"), never substitute into it.

---

## 2. Axis 2 — HONEST: where can motivated reasoning still leak?

The backbone kills the classic frauds (goalpost-moving, re-rolling, burying negatives,
self-grading, p-hacking) convincingly. The remaining leaks are subtler:

### RT-5 (MAJOR) — The unblinding cutoff is later than actual exposure to outcomes.

The `unblind` log line — the design-amendment cutoff — is written when the pinned
analysis first runs. But raw per-cell metrics (accuracies, catch counts) land in
`results-incoming/` and the chained log *continuously during the run*, and the
**coordinator deliberately reviews results-incoming/ before committing (X.log), by
design**. So for days between first final-phase cells and readout, agents with amendment
authority have lawful sight of raw outcomes while design amendments are still "valid".
GR-7's "no peeking" is a MUST-NOT for runners, not a mechanism, and does not bind the
coordinator at all. A motivated (or merely optimistic) amendment in that window is
compliant with G-3 as written.

**Fix (P2 §1.4, one line):** design amendments touching `endpoints`, `verdict_rules`, or
`pins.analysis_script` become invalid after the **first `phase:"final"` run record**, not
after `unblind`. Ops amendments keep the current cutoff. This costs almost nothing (those
fields should be settled by first run anyway) and closes the window completely.

### RT-7 (MAJOR) — The evaluation universe is self-authored; ecological validity is zero by construction.

Every primary endpoint lives on corpora the programme generates from its own kernel
(D-QA from kernel-v0 + wn31; D-IR's violations are *planted to be checkable by the
axiom checker*; D-GL/D-DOM likewise). The FP bound on clean records and the non-covered
control slice mitigate but do not answer the reviewer's first question: *does any of this
happen on tasks you didn't design?* E9-C in particular verges on circular — "our checker
catches the violations we seeded at known rates for our checker to catch" is a
calibration exercise unless the violation distribution is defended as natural.

Additionally M0b — the coverage number restated in every verdict — has **no threshold and
no consequence**. If coverage lands at 4% of content-word mass, every experiment proceeds
unchanged and every claim carries a disclosure that quietly means "this applies to almost
nothing". Disclosure without a gate is how the coverage ceiling gets routed around while
appearing faced (see Axis 3).

**Fix:** (a) add one small **externally-authored eval slice** as a pre-registered
secondary in E9 and F2 (e.g. the definitional/consistency subset of an established public
benchmark, filtered to kernel-covered concepts by M0b machinery — the filter is ours, the
items are not); (b) give M0b a pre-declared *interpretive* gate: coverage < X% (maintainer
sets X at GNG-0; suggest 20% of the target task family's content-word mass) ⇒ every
verdict template renders a "NICHE-SCOPE" banner and the frontier-pitch route requires an
explicit coverage-growth cost line (see RT-11); (c) for E9-C, add a *naturally-occurring*
violation sub-corpus (mined from model outputs, not planted) as a secondary, with the
planted corpus retained as the powered primary.

### RT-9 (MAJOR) — Audit independence is real inside the repo and weak outside it.

P2 R-1 admits identity strings are asserted, not proven. All runners, statisticians, and
auditors are Claude-family agents operated by one coordinator on one/two accounts. The
run-vs-audit separation genuinely defeats *procedural* self-grading (different context,
re-derivation from pins), but a frontier lab will not credit "independently audited" as
meaning anything beyond "the same lab re-ran its own pipeline". The plan's decision-tree
language ("every load-bearing positive independently audited") overstates what G-6 buys
externally.

**Fix (cheap, high pitch-value):** (a) rename the property honestly everywhere:
"role-separated re-derivation", reserving "independent" for the maintainer-level audit
that P2 §7.2 already contemplates; (b) for any TAKE-route headline positive, pre-commit
to one genuinely external replication offer (artifacts + harness public; invite one named
outside person or lab to re-run the pinned analysis) *before* the pitch; (c) implement
RT-15 (external timestamping) so at least the pre-registration is externally verifiable.

### RT-15 (MINOR, cheap, do it) — Self-hosted pre-registration has no external witness.

Freezes live in the programme's own git repo; git history can be rewritten (P2 R-2's
branch-protection ask is still open). Reviewers of the eventual paper have to take the
repo's word that thresholds predate data.

**Fix:** at each freeze, publish the `frozen_sha256` (just the hash, no content) to an
external, timestamped, third-party surface — the existing public coordination issue
(sparq-org/sparq#1683) already works; an OSF registration mirroring `frozen-index.json`
is better and costs ~minutes. Add to the `prereg freeze` skill as a post-step.

### RT-11 (MAJOR) — Kernel authoring cost is missing from the efficiency ledger.

F0's V is admirably total on the *serving* side (encoder, adapter, verifier, store,
retrieval — "nothing waived") but the **cost of authoring the kernel content itself** —
validated explications at ~$X/concept of Fable time, the axiom sidecar, molecule tier —
appears nowhere in V and is the single largest real cost of the approach at deployment
scale. HE4 (onboarding) counts ToolkenGPT's per-concept training FLOPs on the ledger and
the adapter's amortization, but not the cost of authoring the ≥50 D-DOM explications the
kernel arm needs — while its in-context-text competitor could ship raw glosses at
near-zero authoring cost. That asymmetry currently favours the kernel arm.

**Fix (F0 §3 + P1 HE4/HE5):** add an `authoring_cost` line to V for any arm consuming
authored kernel content (measured $/concept from G9/haiku-tier priors; amortized over the
same Q sweep as the adapter), and require HE4/HE5 verdicts to quote the break-even Q
including it. This also gives the M0b coverage-growth story a cost curve (RT-7b).

### RT-20 / RT-24 (MINOR) — Two lint soft spots.

(i) P2 §3.3: commentary.md is "excluded from --citations claim-scanning only when
consistent with the verdict" — circular as written (consistency is what the scan
determines). Fix: commentary is always scanned, full stop. (ii) The claim-regex battery
("direction/magnitude the cited fields do not support") is presented as mechanical; it is
genuinely hard NLP and will have false-passes ("consistent with a substantial effect"
evades regexes). The real backstop is paper.review's re-derivation — say so, and budget
R8's paper.review time as the load-bearing check, with the regex set as tripwire only.

### RT-17 (MINOR) — Judge-provider correlation.

The proposer-invariance second-provider check (P6 §2.2) covers G4/G9 authoring only. If
E9's fallback leak-checked judge is Anthropic-family and the arms' content is
Anthropic-authored, judge bias is correlated with the kernel arm. Fix: extend the
second-provider replication arm to any experiment where an LLM judge touches the primary
endpoint (E9 fallback), or hard-require the non-LLM rubric there.

---

## 3. Axis 3 — CONFRONTS HARD PRIORS: faced or routed around?

Mostly genuinely faced — this is the plan's strongest axis. Text-beats-vector: the
kernel-as-text null is schema-mandatory (G-8) in every relevant arm-set, and F4/G1 carry
the E5 lineage's only measured vector win into the cost-accounted test it needs. LCM
scaling penalty: M2-output is pre-declared expected-fail with ≤$20 exposure and an
anchor-contradiction tripwire. SAE deprioritisation: E8-D adopts GDM's own acceptance
test (beat a linear probe on a downstream task or be decoration), and the
Hyperdimensional-Probe differentiation is mandated. HS13/A1 is correctly demoted to a
double-gated remnant whose null is the expected outcome. Two failures to face remain:

### RT-2 (CRITICAL) — The strongest Law-2 baseline is missing: **text-based self-verification with retry**.

E9's arms are: model-alone / RAG-with-citations / **passive** gloss-dictionary lookup /
kernel decode-verify / +repair-retry. F2's are model-alone at sizes / +verifier /
kernel-as-text / RAG / self-consistency-N / cascade / int4. Nowhere in either arm-set is
the arm Law 2 (L3 §7.1) actually predicts will win: **the model checking its own output
against the gloss TEXT and retrying — the same verify-and-retry loop, with the text
rendering as the verification instrument, at matched retry budget and FLOPs.**
Self-consistency-N matches compute but not topology; the gloss dictionary matches content
but not the loop. If kernel decode-verify beats only arms that lack the retry loop, a
reviewer will correctly attribute the win to *verification-with-retry as such* — a known,
kernel-free technique (self-refine / CoVe lineage) — not to the kernel. HC1's PASS as
currently armed cannot distinguish "structured verification beats text verification" from
"any verification beats none". This is the single most likely way the programme's
headline correctness result dies on contact with a frontier reviewer, and it is exactly
the deflationary control the L3 report's own §8.1 logic demands.

**Fix (pre-freeze, e9.reg + f2.reg):** add arm "gloss-text self-verify + retry" (model
generates → model checks against the pinned gloss text → retry k∈{1,2,4}, identical retry
budgets to arm 5) to E9, and the analogous text-gated cascade to F2/HE2 (logprob gate is
already there; add text-self-check gate). Amend HC1/HE1/HE2 kill criteria: the kernel arm
must beat **this** arm, not just the passive dictionary, at matched FLOPs. Cost: ~+20–30%
of E9/F2 inference budget. This is the most important single edit in this report.

### RT-7 (again, as an Axis-3 finding) — The coverage ceiling is disclosed, not confronted.

See §2. Restating every verdict's M0b number is honesty-as-annotation; nothing tests
whether the covered slice is *worth anything* to a real workload, and no kill or scope
consequence attaches to a low number. That is routing-around wearing a disclosure badge.
Fix per RT-7.

### RT-16 (MINOR) — HS-A/G9's "decisively beats DeepNSM-8B" is instrument-incommensurable.

Our composite validator-pass score vs DeepNSM's *published self-metric* are different
instruments run by different pipelines (ours co-designed with our authoring loop); a
+10-point margin across instruments is not a like-for-like comparison, and the why-now
claim built on it is softer than the Wilson machinery makes it look. Fix: score a sample
of DeepNSM's published outputs (HF artifacts if available) through **our** validator +
blinded review as the primary comparison; the published-number comparison drops to
descriptive secondary. Also define G4's "effort" metric now (agent wall-time? tokens?
edit rounds?) — it is currently unmeasurable as registered.

---

## 4. Axis 4 — OPERATIONALISABLE: can agents actually execute this?

Largely yes — the stage template, RunSpec contract, fail-closed gates, and wave plan are
concrete and mostly build on validated machinery (Modal harness, staged-manifest
assertions, E5/E9 precedents). Gaps:

### RT-3 (CRITICAL) — The model↔verifier interface of the correctness track is never specified.

Everything in HC1/HC2 hinges on the step where **a SmolLM's output becomes something the
kernel can check**. X2's 51/54 decode was measured on *encoder-produced* vectors. In E9,
what exactly is decoded? Options with wildly different risk: (a) the model emits text
that is parsed/extracted into candidate concept-records (then "decode-verify" is mostly
an extraction problem, and the verifier's catch rate is bounded by extraction quality on
free text — the hard, unmeasured part); (b) the model emits soft vectors through an
inverted E5 adapter (never built or validated in reverse); (c) the model is constrained
to a structured output format (then the text arms must be granted the same format or the
comparison is confounded). P1, P3 (`decode-verify` S4), and P8's HC1 SAP all gesture at
"X2 machinery, gap on the ledger" without choosing. An agent cannot build e9.inputs from
these documents, and the choice materially changes what HC1 measures.

**Fix (blocking for e9.reg/f2.reg):** a one-page interface spec (extend S4's contract):
the extraction/decode path, its own instrument-validity gate (extraction failure rate on
a held-out labelled set; failures scored as instrument events, not hypothesis events —
extending P8's `/gates/instrument_valid`), and the rule that all arms share the same
output-format affordances. Pre-register extraction-failure accounting so the verifier arm
can neither harvest free wins (unparseable ⇒ "caught") nor free losses.

### RT-4 (MAJOR) — G2 is unpowered as scheduled; the plan contradicts itself on n.

P1's HS2 kill test requires the Wilson lower bound over "**≥100 scored derived
subsumptions**" to clear 0.9. P3 schedules `g2.gold` as "**~50 gold subsumption pairs
(~3h)**". P8 §1.6 then shows that even n=100 needs true precision ≳0.96 to clear a 0.9
threshold, recommending ~500 judgments if precision is marginal. At n=50 the gate is
undecidable for any realistic precision (50/50 correct gives LB ≈ 0.93; one error drops
it near the line). As scheduled, G2 will most likely read out INCONCLUSIVE after
consuming annotator hours. Same audit should run over every threshold gate: E9-C's FP≤2%
bound at n=300 clean records needs true FP ≲1.1% (P8 notes this — fine); G8's 1% fragment
gate at n=1000 needs ≥~18 hits to clear 1% (fine); G9's +10-point margin at N=50 is
similarly tight.

**Fix:** raise g2.gold to ≥150 pairs (≥300 if pilot precision <0.95), re-budget annotator
hours in P3/P6 (H-4 grows by ~3–6 h), and add a `prereg lint` rule: any Wilson-bound gate
must ship P8's detectable-alternative number and n must make the gate decidable at the
*expected* rate, not just the optimistic one.

### RT-10 (MAJOR) — E8-D, the PIVOT-A6 acceptance test, has no ground-truth story.

E8-D must detect "concept c's operational meaning moved between model/kernel versions"
better than a linear probe (ΔAUC ≥ 0.05, DeLong). No labelled semantic-regression dataset
exists; e8d.inputs says only "pin version pairs + probe baseline". Constructing ground
truth almost certainly means *planting* drift (fine-tuning a variant on shifted usage) —
which re-imports RT-7's circularity into the one experiment that can rescue the programme
on a PIVOT route. E8-D is simultaneously the vaguest experiment in the suite and a
route-deciding one.

**Fix:** design E8-D's ground-truth construction now (pre-freeze, even though e8d.reg is
conditional): a planted-drift primary (seeded fine-tunes, drift magnitudes pre-declared)
plus a natural secondary (existing public model version pairs, e.g. instruct vs base or
v1 vs v2 checkpoints, scored by behavioural probes authored blind to the instrument), and
state in the PIVOT-A6 paper-type row that the instrument's evidence is planted-drift
unless the natural secondary agrees.

### RT-8 (MINOR→MAJOR at execution) — Budget arithmetic is internally inconsistent.

(a) Tier-2 worst case (E9 $100 + F4/G1 $140 + E8 $120 = $360) exceeds the Tier-2 cap
($320): a fully-utilised tier BUDGET-HALTs mid-campaign by arithmetic, not misbehaviour.
(b) Worst-case Tiers 0–3 ($15+$60+$360+$320 ≈ $755) exceeds the $700 cumulative cap.
(c) P6 §4 says "caps $720 cumulative Tiers 0–3" vs GR-1's $700. None of this is
dishonest, but the first mid-experiment BUDGET-HALT will burn schedule and force an ops
amendment that looks like cap-raising under pressure.
**Fix at I-BUDGET:** reconcile the numbers (either raise T2 to $400/cumulative to $800,
or size campaign worst-cases down), and add a freeze-time lint: Σ(frozen worst-cases in a
tier) ≤ tier cap.

### RT-18 (MINOR) — Phase-0 schedule is optimistic and the backbone is the foundation.

I-REG + kotstats (the largest single build, with hand-computed fixtures) + skills 1–8 +
f2 frozen as acceptance test, all by Jul 15 — one week — on a 2-core shared box, under a
5-agent cap that Phase-0 also needs for other builds. A slip here cascades into every
date. The fixtures are exactly the wrong thing to rush (P2 R-4: a frozen buggy analysis
produces wrong verdicts deterministically).
**Fix:** declare Jul 22 the honest M0 target now (P3 already carries ~30% slack —
consume it here, visibly, rather than at fixture quality); GNG-0 date moves, GATE-T1
target moves to ~Jul 29; nothing downstream is calendar-critical until the venue windows.

### RT-23 / RT-22 (MINOR) — Two overconfident resource statements.

(a) The AWS fallback "2–3 day reroute" is fictional today: GPU quota is 0 and the
escalation is un-poked (H-9 optional). Either poke it in P-0 or state that Modal is a
single point of failure until it lands. (b) The RAG baseline defaults to BM25-primary;
by 2026 a "strong industrial baseline" claim wants at least one dense-retriever
configuration pre-registered (a small ungated embedder is already contemplated — make it
mandatory for the F2/E9 RAG arms rather than optional), or the "beats RAG" claim invites
the strawman charge.

### DAG audit (checked, mostly clean).

Coverage check at P3 §8 verified: every P1 §8 row has a deciding node; hard orderings
match P1 §5; analysis-only chains are wired; e8d/g5/f7 conditionals are guarded. Findings:
(i) the `family-h0` record (P8 C-3's Holm family) appears in P4's skill surfaces but is
**not a node in P3 §8** — a-h0.reg predates P8's C-3 tightening in the build order, so
there is a real risk a-h0 freezes with P1 §1 patterns only and the Holm requirement never
executes. Fix: add `family-h0.reg/readout` nodes (or fold C-3 into a-h0.reg explicitly)
and lint a-h0's frozen rules against P8 C-3 at freeze. (ii) The maintainer-as-default
annotator (O-3 default) sits inside experiments the maintainer later ratifies at GNG-2 —
acceptable with blinding, but g3's "2 independent annotators" must then mean the second
human is genuinely independent AND the maintainer's annotation happens before seeing any
kernel-side materials; state it. (iii) `xb.deliver` depends on `paper.sign` — on a KILL
route where the maintainer might reasonably want the explainer *before* approving a
manuscript, the ordering forces manuscript-first; intentional per directives §7
("after the write-up") but worth one line in the xb.deliver dossier acknowledging the
maintainer can read r-final anytime.

---

## 5. Axis 5 — HONORS DIRECTIVES

**Semantic-web legacy: clean.** Grepped the plan set: RDF/OWL/SHACL appear only as (i)
G1's declared comparison-lens arm, (ii) P9's single export-note sentence + related-work
lens, (iii) source-data provenance (QUDT/onto-* as data, allowed engineering periphery).
The Π/subsumption notation (⊑) is native-formalism mathematics, not a semantic-web
dependency. The paper lint (P9 §3.4 term 1) closes the write-up surface. No residual
creep found.

**Two value theses: both operationalised**, with the full V vector schema-enforced
(G-9) and Pareto-hull discipline. One gap is RT-11 (authoring cost missing from V) —
that is an efficiency-thesis completeness defect, fixed above.

**Forks genuinely testable: yes, with two soft spots.** HS4's "≤2× effort" has no
defined effort metric (RT-16). HS5/G5 is fine (conditional confirmation). All other
forks have real deciding experiments and numeric bounds.

**Directives §3 checklist:** registry ✓, append-only log ✓, DAG ✓, guardrails ✓
(hash-pinning, budget caps, concurrency, negatives, run-vs-audit), resources ✓, skills ✓,
roles ✓. §5 (definitional purity) respected — axioms in the sidecar, world facts out of
the hash. §6/§7 owned by P8/P9 and wired as DAG nodes. The plan honours the directives;
the failures found in this report are almost all *within* the directives' frame, not
departures from it.

---

## 6. Axis 6 — STATS & EXTRAPOLATION

P8 is the strongest component reviewed: one primary endpoint schema-enforced; IUT for
conjunctions with a stated basis; the F-H0 Holm family closes a real ~34% family-wise
hole P1 left open; TOST margins fixed per endpoint type; power shown for both the
rejection and TOST branches; the 3-rung PI vacuity honestly surfaced (t=6.31); the 1-OOM
cap and ≥70B prohibition are exactly the Kaplan→Chinchilla lesson, and
ANCHOR-CONTRADICTING ⇒ replication-first is a genuinely unusual and correct safeguard.
Residual findings:

- **RT-12** (rung-set membership / conditional rung extension) — see §1; the one real
  pre-specification hole in the SAP template.
- **RT-13 (MINOR):** F-H0 Holm runs "across members actually read out" — the family is
  data-dependently selected when tiers are pruned by upstream kills (F2 kill narrows
  Tier-2 efficiency scope, changing which members exist). Holm over a
  selection-dependent family is not strictly level-α. Fix: define the family as the 8
  pre-declared members with non-read-out members scored as non-rejections
  (conservative, one sentence in family-h0.reg).
- **RT-14-adjacent power gap:** E8-R has no power analysis anywhere (how many
  seed-stable features/concepts enter the correspondence test? what ρ is detectable at
  p<0.01 per pair?). The SAP template obliges field 8, but P8's worked examples skip the
  hardest case. Fix: require the E8-R SAP to derive the detectable ρ from the
  Paulo–Belrose ~30%-stable subset size before D-SAE spend.
- **Extrapolation honesty:** no overreach found. If anything the plan under-sells: even a
  full TAKE route licenses only "direction-only to 7B" — which means the frontier pitch
  is structurally a *fund-the-next-rung* pitch, never a "this works at frontier" pitch.
  The GNG-3 dossier and P9 §1.3 should say that ceiling in one explicit sentence so the
  maintainer prices the pitch correctly (currently implied, not stated).

---

## 7. Axis 7 — WRITE-UP

P9 is strong: route→paper-type as a pure function, generated results tables that make
omission mechanical, the banned-spin vocabulary, the mandatory abstract scale sentence,
negatives structurally equal, KILL pre-declared as a success mode with a purpose-built
venue policy (TMLR primary + ICBINB companion) — this will produce an honest paper on
every route. Findings:

- **RT-14 (MAJOR for the paper):** the double-blind anonymization plan ("scripted scrub
  of identity strings") **breaks the hash chain and the frozen hashes** — identity
  strings are *inside* the byte-hashed records; scrubbing them invalidates
  `frozen_sha256`, every `prev_sha256`, and therefore the very reproducibility/
  pre-registration claim being reviewed. Fix: do not scrub record contents; the identity
  strings (`kern/fable-runner-3`) are already pseudonymous — anonymize by (a) renaming
  only repo-external identifiers (account names, profile ids, issue links) via an
  overlay mapping file, (b) shipping the registry/logs byte-intact, and (c) noting in
  the reproducibility statement that agent-identity strings are pseudonyms. Decide this
  before the registry schema is frozen, since the fix constrains what goes *into* hashed
  records (keep account-identifying material out of hashed bytes now).
- **Top-tier bar vs TMLR-primary-on-KILL:** defensible and honest (the directive's bar is
  manuscript quality, met at paper.review), but say explicitly in the GNG dossier that on
  a KILL route the "top-tier venue" directive is satisfied by manuscript standard, not
  venue brand — the maintainer should ratify that reading (add to O-9).
- **The explainer spec (§4) is excellent** — the four-tag plain-language mapping and
  "simplify wording, never claims" lint are exactly right. One addition: slot 5 (cost)
  should also state annotator-hours consumed, not just $ — human time was a real input.
- **Pre-registration credibility:** RT-15's external timestamping materially strengthens
  P9 §1.2's "pre-registration is load-bearing at review time" — without it, reviewers
  must trust our git history.

---

## 8. Weakest experiments, ranked

1. **E8-D** — route-deciding (PIVOT-A6 acceptance) yet has no ground-truth design (RT-10).
2. **E9-full/E9-C (HC1/HC2)** — the correctness flagship, currently missing its strongest
   deflationary baseline (RT-2) and its model-interface spec (RT-3); E9-C's planted
   violations are near-calibration without a natural-violation secondary (RT-7c).
3. **G2** — undecidable at the scheduled n (RT-4).
4. **F6** — instrument already failed once; INSTRUMENT-INVALID blocks the decisive NO
   (RT-19).
5. **G9/HS-A** — instrument-incommensurable comparison propping up the why-now claim
   (RT-16).
6. **HE2/F2b** — kill bar ("strictly dominant at every budget") is so strict that PASS is
   nearly unreachable; cheap since it rides F2, but expect a kill and do not let its
   near-certain death be narrated as informative about M5's ceiling.

## 9. Missing baselines / controls / unstated assumptions (consolidated)

Missing: text-self-verify+retry arm (RT-2, the big one); dense-retriever RAG
configuration (RT-22); externally-authored eval slice (RT-7a); natural-violation
corpus for E9-C (RT-7c); authoring-cost line in V (RT-11); E8-R power analysis (§6);
second-provider check on any verdict-touching LLM judge (RT-17).

Unstated assumptions: that model outputs can be turned into checkable records at high
fidelity (RT-3 — the load-bearing one); that self-authored task distributions transfer
to any real workload (RT-7); that agent-run audits will be credited as independent
(RT-9); that Modal stays available/priced as planned with no live AWS fallback (RT-23);
that the maintainer's ~20 annotator-hours and gate decisions land on the calendar weeks
the timeline needs (P3 §7 partially owns this).

## 10. Top risks to a frontier-lab pitch

1. **"Your verifier win is just verification-with-retry"** — dead on arrival unless RT-2's
   arm exists and loses to the kernel arm.
2. **"Bespoke benchmark, planted errors, self-graded"** — ecological validity + audit
   independence (RT-7, RT-9); mitigated by the external slice, natural violations,
   external timestamping, and honest relabeling of audits.
3. **"135M–3B with direction-only to 7B is not evidence about our models"** — inherent;
   the pitch must be explicitly a fund-the-next-rung pitch (§6 last bullet). The plan's
   honesty here is a feature; pretending otherwise would be the risk.
4. **"What does coverage cost at 10⁵ concepts?"** — no answer today; RT-11's authoring
   cost line + M0b coverage-growth curve is the answer's skeleton.
5. **"The one novel cell (designed-geometry↔learned-geometry) rests on E8, whose field
   just got corrected hard"** — the plan knows this (seed-stable subset, GDM test); the
   residual risk is E8-D's ground truth (RT-10).

---

## 11. Prioritised fix list

Blocking = must land before the named freeze. All are edits to P1/P2/P3/P8 sections +
arm lists; none changes architecture or DAG topology.

| # | Fix | Finding | Where | Blocks |
|---|---|---|---|---|
| 1 | Add **gloss-text self-verify + retry** arm to E9 and F2; amend HC1/HE1/HE2 kill texts to require beating it | RT-2 | P1 §§2–3, e9.reg, f2.reg | e9/f2 freeze |
| 2 | Specify the **model↔verifier interface** (extraction/decode path, shared output affordances, extraction-failure accounting as instrument gate) | RT-3 | S4 spec + e9/f2 SAPs | e9/f2 freeze |
| 3 | Add **STOP-AND-PUBLISH-UNDECIDED** route + global replication-buy cap; score F6 INSTRUMENT-INVALID as undetermined-not-supporting in H0-NO | RT-1, RT-19 | P1 §§1, 6; a-h0.reg; P9 §1.1 | GNG-0 |
| 4 | Move design-amendment cutoff to **first final-phase run record** (endpoints/verdict_rules/analysis only) | RT-5 | P2 §1.4 | I-REG |
| 5 | Define **supersession-lineage semantics** + revision cap for the decision tree | RT-6 | P2 §1.4, gate-eval | I-REG |
| 6 | Fix **G2 n** (≥150 gold pairs) + freeze-time decidability lint for every Wilson-bound gate | RT-4 | P3 g2.gold, P8 §1.6, prereg lint | g2 freeze |
| 7 | Pre-declare **rung-set membership + conditional-rung extension predicates** for all ≥2-rung claims | RT-12 | P8 §1.9 field 12 | first multi-rung freeze |
| 8 | **M0b interpretive gate** (NICHE-SCOPE banner below threshold) + externally-authored eval slice (E9/F2 secondary) + natural-violation secondary for E9-C | RT-7 | m0b.reg, D-QA/D-IR, e9/f2 SAPs | Tier-2 freezes |
| 9 | Add **authoring-cost line to V** and to HE4/HE5 break-even reporting | RT-11 | F0 spec, P1 HE4/HE5 | f4/f5 freeze |
| 10 | **E8-D ground-truth design** (planted-drift primary + natural secondary) | RT-10 | e8d design note now | e8d.reg |
| 11 | Reconcile **budget arithmetic** ($320/$360, $700/$720/$755) + tier-sum lint | RT-8 | P3 GR-1, P6 §4, I-BUDGET | I-BUDGET |
| 12 | **External timestamping** of freezes (sparq issue and/or OSF); keep account-identifying bytes out of hashed records; anonymize by overlay, never by scrubbing chained bytes | RT-15, RT-14 | prereg skill, P2 schema, P9 §1.2 | I-REG (schema) |
| 13 | Add **family-h0 node** to P3 §8 and lint a-h0's frozen rules against P8 C-3; define non-read-out members as non-rejections | DAG audit, RT-13 | P3 §8, family-h0.reg | a-h0 freeze |
| 14 | Rename audit property to **role-separated re-derivation**; pre-commit an external replication offer for any TAKE-route headline | RT-9 | P2 §4, P9, GNG dossiers | pitch only |
| 15 | Dense-retriever RAG config mandatory; second-provider check on verdict-touching judges; G4 effort metric defined; G9 primary re-based on scoring DeepNSM outputs through our validator | RT-22, RT-17, RT-16 | P6 §2, e9/g4/g9 SAPs | respective freezes |
| 16 | Slip **M0 to Jul 22** explicitly; poke the AWS quota escalation in P-0 or declare Modal a single point of failure | RT-18, RT-23 | P3 §5, H-9 | schedule honesty |
| 17 | Minor lint fixes: commentary always scanned; HC1 cost-conjunct loosened; HC2 "N×" phrasing ban at floor denominators; E8-R power analysis required pre-D-SAE | RT-20, RT-21, §6 | P2 §3.3, P1 HC1/HC2, e8r SAP | respective freezes |

## 12. Readiness verdict

**FIX-THEN-EXECUTE.** The plan's honesty machinery, statistics, and kill-economics are
strong enough that most of what a hostile reviewer could do to a *finished* result is
already pre-empted. What remains exploitable is upstream of the machinery: an arm-set
that lets the flagship correctness result win against the wrong baseline (RT-2), an
unspecified instrument interface (RT-3), and a decision tree that can fail to return a
route (RT-1). Those three, plus fixes 4–7, are pre-freeze edits measured in days, not a
redesign. Phase-0 (I-REG, I-F0, kotstats, skills) should start now unchanged — fixes 4,
5, and 12 land inside that build; fixes 1–3 and 6–10 land as edits to P1/P8 and the
affected registry entries before each freezes; GNG-0 should not be signed until fixes
1–5, 8 (gate part), 11, and 13 are in the frozen text. With that done, this programme is
executable as designed and would withstand a frontier-lab review of its *methods*; its
*results* will be whatever they are — which is the point.

---

## Fixes applied (2026-07-08) — verification

**Verifier:** independent skeptic pass (backup-account auditor stance), 2026-07-08. Method:
every fix checked against the actual text of P0–P10 (`00`–`10`), not against changelog
claims. Statuses: **CLOSED** = applied and consistent in every doc the fix touches;
**PARTIAL** = substance applied somewhere but missing or contradicted at ≥1 designated
location; **OPEN** = not applied.

### Per-item closure table (17 items)

| Item | Status | Evidence / residual gap |
|---|---|---|
| **RT-1** (tree non-exhaustive) | **CLOSED** | P1 §6 route 5 is the explicit residual `else` branch (cannot evaluate to nothing) + replication-buy cap (1/experiment, 2 programme-wide) in P1 §6, P3 GR-9/GNG-2/GNG-3, a-h0.reg; P9 §1.1 + §5 carry the UNDECIDED paper type; P2 §5.2/§1.4 wire it. P1↔P3 route texts and caps agree. |
| **RT-2** (self-verify+retry arm) | **CLOSED** | E9 arm 6 + F2 arm 10 + HE2 text-self-check gate in P1 (H0 statement, HC1/HE1/HE2 kill texts all require beating it); P3 e9.reg/f2.reg/readouts; P6 budget lines updated. Consistent everywhere checked. |
| **RT-3** (model↔record interface) | **CLOSED** | New `10-model-record-interface.md`: IF-A/B/C enumerated, IF-C default, IF-1 fork with machine predicate, ≥300-output labelled set, 10%-Wilson INSTRUMENT-INVALID gate, no-free-wins/losses exclusion accounting, shared-affordance rule; P1 HC1/HC2/HE1 + §8 pin it; P3 has `e9.iface`/`f2.iface` AUTO-GATE nodes with `d-xif ≺ iface ≺ run` ordering. |
| **RT-4** (G2 n) | **CLOSED** | n = 500 consistent in P1 HS2, P2 §1.x, P3 g2.gold (~12 h, blind adjudication), P6 H-4 (re-budgeted 30–40 h), P8 §1.6/C-8; decidability lint operationalised in P8 §1.6 and named in P2's prereg-freeze row. (Soft spot: P4's S1 lint list doesn't name the decidability/tier-sum lints.) |
| **RT-5** (amendment cutoff) | **PARTIAL** | P2 P-9/§1.4/G-3/G-10 and P3 GR-7/GNG-0 all move the design cutoff to the **first `phase:"final"` run record**. **Gap: P4 §2.1 `prereg amend` step 4 still refuses design amendments only "after the `unblind` line"** — the enforcement-tool spec contradicts P2 §1.4/G-3 (the old, later cutoff). One-line fix in P4 before I-SKILLS builds it. |
| **RT-6** (supersession lineage) | **CLOSED** | P2 §1.4 lineage semantics (latest-ID-with-full-lineage, FAIL→PASS needs audit + R10 memo, 2-revision cap → route 5) + G-3 + threat table; P3 lineage rule for every gate/tree/dossier; R10 exists in P5. |
| **RT-7** (ecological validity + coverage gate) | **PARTIAL** | (a) D-EXT external slice: CLOSED (P1 HC1/HE1 secondaries; P3 D-EXT node, e9/f2 inputs, P-1 wave). (b) M0b NICHE-SCOPE gate: CLOSED (P3 m0b.gate + GR-9 + GNG-0 threshold-setting; P6, P9). (c) Natural-violation secondary: pre-registered in P1 HC2 and budgeted in P6 H-4 ("D-IR-N adjudication"), **but P3 has no D-IR-N node** — the D-IR row is planted-only and e9.inputs doesn't consume it. Wiring gap in P3. |
| **RT-8** (budget arithmetic) | **PARTIAL** | Canonical table (T0 $20 · T1 $80 · T2 $400 · T3 $400 · cum 0–3 $900 · T4 $900) identical in P1 §5, P2 G-11, P3 GR-1, P6 §4; worst-case $760 < $900 recomputed consistently; tier-sum lint added. **Gap: `00-overview.md` was never refreshed** — §9 still says "T0 $15 · cumulative ~$700", §2 still says decisive NO "$180–650" and stale tier ranges, §5/§9 still say 15–25 annotator-hours / $300–600 (vs 30–40 h / $500–900 in P3/P6). |
| **RT-9** (audit-independence relabel) | **PARTIAL** (pair with RT-15) | P2 G-6 naming discipline ("role-separated re-derivation"; "independent" reserved for maintainer-level/external; citation lint flags misuse) + P9 relabelled throughout + external replication offer pre-committed on TAKE (P9). **Gap: P1 itself still says "independent adversarial audit" (§1) and "every load-bearing positive independently audited" (§6 route 1) — the exact decision-tree phrase this finding quoted — and 00-overview §3/§4/§9 likewise.** P2's own lint would flag the frozen P1 text. |
| **RT-10** (E8-D ground truth) | **CLOSED** | P1 HC4: planted-drift primary (pre-declared magnitudes) + natural version-pair secondary scored blind to the instrument, pre-registered now; P9 PIVOT-A6 row quotes the "planted-drift unless the natural secondary agrees" labelling rule verbatim. |
| **RT-11** (authoring cost in V) | **CLOSED** (minor residue) | Authoring cost is a V component in P1 common rules; HE4 carries the binding amortized-authoring accounting + break-even-Q quoting; P6 §2.2 prices it ($0.10–0.50/concept planning figure) and charges F4/HE4 **and F5/HE5** ledgers. Residue: P1's HE5 section doesn't restate the break-even-Q requirement, and the F0 spec itself (`design-efficiency-track.md` §3) was not amended — the change lives in P1/P6 only. |
| **RT-12** (rung-set membership) | **PARTIAL** | P1 §0 defines the discipline (frozen rung set; extension trigger as machine predicate `primary_reject@R1 AND primary_reject@R2`; extension may only strengthen, never substitute) and P1 §8 pins it per registry entry. **Gap: the designated fix point — P8 §1.9 SAP field 12 — was not updated** (no rung-set/extension-predicate declaration, no freeze-time lint; RT-12 appears nowhere in P8; P8's rev-2 header lists only the RT-4/E8-R fixes). |
| **RT-13** (F-H0 family selection) | **PARTIAL** | P3 family-h0.reg/readout ("8 pre-declared members fixed at freeze; non-read-out members scored as non-rejections — never data-dependently selected") + ordering ≺ a-h0; P2 §5.4 concurs. **Gap: P8 C-3 and the §1.4 F-H0 family row still say "Holm … over/across the family members actually read out"** — the precise data-dependent-selection language this finding flagged. P8 contradicts P3/P2 on the family definition. |
| **RT-14** (anonymize by overlay) | **PARTIAL** | P9 §1.2 item 4: overlay approach fully specified (hashed records ship byte-intact; repo-external identifiers renamed via a privately-held mapping) + maintainer sign-off item. **Gap: the "corresponding P2 schema rule" P9 cites (account-identifying material kept out of hashed record bytes; account bindings in an unhashed sidecar) does not exist in P2** — worse, P2 §4's identity format `<account>/<role>-<n>` puts account-bearing strings (e.g. `jeswr-backup/fable-auditor-2`) *inside* hashed record bytes. Must land in the P2 schema before I-REG freezes it. |
| **RT-15** (external timestamping) | **CLOSED** | Mandatory `prereg-freeze` post-step in P2 §1.1 (sparq issue + OSF) and referenced at P2 R-2; P4 S1 step 5 posts the frozen sha to sparq-org/sparq#1683; P3 GNG-0 announces every late freeze's `frozen_sha256`; P9 §1.2 makes it load-bearing at review time. |
| **E8-R power gap** (P7 §6) | **CLOSED** | P8 C-8 + §1.6: detectable-ρ formula from the realized seed-stable subset, n ≳ 85 matched pairs to power ρ ≈ 0.39 at α = 0.01, required in the e8r SAP **before any D-SAE spend**; also in P8's sign-off list. |
| **family-h0 DAG node** (P7 §4 DAG audit) | **CLOSED** | P3 has family-h0.reg/readout/audit/close as first-class nodes, hard orderings `family-h0.reg ≺ a-h0.reg` and `family-h0.close ≺ a-h0.readout`, and a-h0.reg is linted against the family record at freeze; P4 skill surfaces and P2 §5.4 updated to match. |

### New inconsistencies introduced by the fix pass (all small, all pre-freeze)

1. **P4 §2.1 vs P2 §1.4/G-3 (RT-5):** the `prereg amend` tool spec still enforces the old
   `unblind`-line cutoff for design amendments; P2/P3 moved it to the first final-phase run
   record. The tool as specced would *accept* amendments P2 declares invalid.
2. **P8 C-3/§1.4 vs P3 family-h0.reg / P2 §5.4 (RT-13):** "members actually read out" vs
   "8 pre-declared members, non-read-out = non-rejections". The frozen family record must
   follow P3/P2; P8's two rows need the one-sentence update.
3. **P9 §1.2/§5 vs P2 §4 (RT-14):** P9 cites a P2 schema rule that P2 does not contain, and
   P2's example identities embed account names in hashed bytes. Blocking for I-REG.
4. **P3 vs P1 HC2 / P6 H-4 (RT-7c):** the natural-violation sub-corpus (D-IR-N) is
   pre-registered and budgeted but has no build node in P3's data table, and e9.inputs does
   not consume it.
5. **00-overview.md stale throughout (RT-8 and others):** old caps ($15/$700), old
   decisive-NO cost ($180–650 vs $200–700), old annotator-hours (15–25 vs 30–40), old
   platform cost ($300–600 vs $500–900), and M0 = Jul 15. The summary doc now contradicts
   the canonical numbers in P1/P2/P3/P6 it purports to summarise.
6. **P1 §1/§6 + 00-overview retain "independent(ly) audited" for agent audits (RT-9):**
   P2's own `--citations` lint, as now written, would flag the frozen P1 decision-tree text.

### Residual items from the §11 fix list NOT in this 17-item audit and still open

- **RT-16 (row 15): OPEN** — G9's primary is still the Wilson-bound-vs-*published-point*
  comparison (P1 HS-A; P6 §2 even re-affirms "compare against published point estimates
  only"); the re-base onto scoring DeepNSM outputs through our validator was not applied.
  G4's "effort" metric is still undefined (P1 HS4 kill criterion remains unmeasurable as
  registered; P3 D-AXN logs "effort" with no metric).
- **RT-17 (row 15): OPEN as specified** — the second-provider check covers G4/G9 only
  (P6 §2.2); E9's judge fallback remains "non-LLM rubric **or** leak-checked judge" with
  neither the hard non-LLM requirement nor a second-provider arm on verdict-touching judges.
- **RT-22 (row 15): OPEN** — dense-retriever RAG is still "if … pre-registered" optional
  (P6), not mandatory for the F2/E9 RAG arms.
- **RT-18 (row 16): OPEN** — M0 is still Jul 15 in P3 §5 and 00-overview; the recommended
  explicit slip to Jul 22 was not taken (GATE-T1 target Jul 22 remains).
- **RT-23 (row 16): PARTIAL** — P6 now marks the AWS quota BLOCKED and non-critical, but
  the contingency row still promises the "2–3 day reroute" with quota at 0 and H-9 optional.
- **RT-20/RT-21 (row 17): OPEN** — P2 §3.3 still contains the circular commentary
  exclusion verbatim ("excluded from --citations claim-scanning only when consistent with
  the verdict"); P1 HC1's kill still has the un-loosened "at ≤ arm 3's cost" conjunct; no
  HC2 "N× better" phrasing ban at floored text-arm denominators was added.

### Readiness verdict

**STILL-FIX (narrowly).** All three CRITICALs (RT-1, RT-2, RT-3) are genuinely closed, and
closed consistently — the decision tree is exhaustive in both P1 and P3, the deflationary
arm is in both arm-sets with the kill texts amended, and P10 is a real, buildable interface
spec with its instrument gate wired into the DAG. The programme is executable. But the plan
set is not yet freeze-consistent: three fixes are contradicted at their designated
enforcement point (P4's stale amendment cutoff; P8's stale F-H0 family language + missing
rung-set field; the RT-14 schema rule P9 relies on but P2 lacks), one is unwired in the DAG
(D-IR-N), and the overview doc contradicts the canonical budget/schedule numbers. Every
remaining edit is a sentence-to-paragraph patch in 00/02/03/04/08 — none is a redesign —
but the RT-14 schema rule blocks **I-REG**, the RT-5 tool spec blocks **I-SKILLS**, and the
RT-12/RT-13 P8 rows block **family-h0.reg / a-h0.reg / the first multi-rung freeze**, so
GNG-0 should not be signed until they land. Fix-list rows 15–17 (RT-16/17/18/20/21/22/23)
remain open as noted and should be either applied or explicitly waived by the maintainer at
GNG-0.

---

## Second-pass verification (2026-07-08)

**Verifier:** independent skeptic pass (backup-account auditor stance), second pass, after
the second fix wave. Method identical to the first pass: every previously-PARTIAL item and
the 04-vs-02 amendment-cutoff inconsistency re-checked against the actual text of
00/01/02/03/04/06/08/09/10, plus re-confirmation of the three CRITICALs. Statuses:
**CLOSED** = applied and consistent in every doc the fix touches; **OPEN** = residual gap
at a designated location.

### Previously-PARTIAL items

| Item | Status | Evidence (verified in text) |
|---|---|---|
| **RT-5** (amendment cutoff) | **CLOSED** | P2 P-9/§1.4/G-3 and **P4 §2.1 step 4 now agree**: design amendments invalid after the **first `phase:"final"` run record** (P4 lines: "deliberately EARLIER than the `unblind` line", tooling refuses on a `phase:"final"` record existing, `unblinding_state_at_write` stamped from the log). The 04-vs-02 contradiction is gone; P4 header names the RT-5 alignment. |
| **RT-7** (ecological validity) | **CLOSED** | (a) D-EXT slice in P1 HC1 + HE1 as Holm-corrected secondaries, P3 D-EXT node + e9.inputs/f2.inputs, P6 sourcing row with preference order + selection rule; (b) m0b.gate AUTO-GATE with NICHE-SCOPE default 20% and pitch-consequence (P3, GR-9); (c) **D-IR-N now a first-class P3 node** (data table + machine DAG `d-ir-n ; AUTO ; d-ax`), consumed by `e9.inputs ← D-IR, D-IR-N, …`, named in e9.reg, blind adjudication ~2 h inside the O-3 hours, circularity guard ("never surfaced by the axiom checker under test"); P1 HC2 natural-violation secondary concurs. |
| **RT-8** (budget arithmetic) | **CLOSED** | Canonical table (T0 $20 · T1 $80 · T2 $400 · T3 $400 · cum 0–3 $900 · T4 $900; worst-case ≈ $760) now identical in **00 §2/§9**, 01 §5/§8, 02 G-11, 03 GR-1, 06 §4; tier-sum lint present in 01/03/06. 00-overview refreshed throughout: decisive NO $200–700, annotator-hours 30–40, platform $500–900, **M0 = Jul 22** (slip stated explicitly — RT-18 was also applied in this pass, P3 §5 W0 "slipped from Jul 15 per P7 RT-18"). |
| **RT-9** (audit relabel) | **CLOSED** | No "independent(ly) audit(ed)" applied to agent audits anywhere in 00 or 01: 00 §3/§4/§9 and P1 §1/§6 route 1 all say **role-separated re-derivation**; remaining "independent" uses in 01 are benign (human annotators/authors, scheduling, HS13's genuinely external replication). P2 G-6 naming discipline + lint, P3 GR-6, P9 deck rules all concur. Cosmetic residue (non-blocking, one word): **P8 §1.8 order-rationale paragraph still says "requires independent audit"** in an internal cross-ref to P2 G-6 — the lint it cites would flag it; fix opportunistically. |
| **RT-12** (rung-set discipline) | **CLOSED** | P8 §1.9 **field 12 exists**: member rung set declared at freeze, extension trigger as a machine predicate over frozen fields, extension may only strengthen (report "PASS at R1–R2, replicated at R3"), **freeze-time lint refuses** undeclared rung sets / non-machine-evaluable triggers; worked example fills it (`primary_reject@R1 AND primary_reject@R2`). Consistent with P1 §0 discipline and P1 §8 packet fields. |
| **RT-13** (F-H0 family) | **CLOSED** | P8 C-3 and §1.4 F-H0 row now read "**8 fixed members… fixed at freeze… non-rejection, never dropped… never data-dependently selected**" — identical semantics to P3 family-h0.reg/readout (and machine DAG rows) and P2 §5.4. The "members actually read out" language is gone. `family-h0.reg ≺ a-h0.reg` and `family-h0.close ≺ a-h0.readout` orderings present; a-h0.reg linted against the family record. |
| **RT-14** (overlay + pseudonyms) | **CLOSED** | **P2 now contains the schema rule P9 cites**: §1.2 constraint 10 — account-identifying material (account names, `<account>/…` prefixes, emails, profile ids) MUST NOT appear in hashed record bytes; identities are pseudonyms `<role>-<n>`; account↔pseudonym binding lives only in the **unhashed, git-ignored `registry/identity-map.json` sidecar** (repo layout §5.1); write-path fails closed (`ERR_P2_ACCOUNT_IN_RECORD`); §4 rewritten to match; maintainer sign-off item 2 covers backup-account audit binding. P9 §1.2 item 4 (overlay, hashed records ship byte-intact) + GNG sign-off item 5 concur. Nit (cosmetic): P9's prose example `kern/fable-runner-3` predates P2's `<role>-<n>` exemplars (`runner-3`); "kern" is not an account string, but align the example. |
| **04-vs-02 cutoff inconsistency** | **CLOSED** | Same evidence as RT-5 — P4 was the offending doc and is now aligned. |

### CRITICALs re-confirmed

- **RT-1 — CLOSED (stands).** P1 §6: five routes with an explicit exhaustiveness clause
  (route 5 = the `else` branch; "the tree can never evaluate to nothing"); replication-buy
  cap (1 per experiment/gap, 2 programme-wide) in P1 §6, P3 GR-9/GNG-2/GNG-3, a-h0.reg
  (incl. the RT-19 F6 undetermined-not-supporting carve-out); route 5 in the machine DAG.
- **RT-2 — CLOSED (stands).** E9 arm 6 + F2 arm 10 (gloss-text self-verify + retry at
  matched budget) in P1, with HC1/HE1/HE2 kill texts requiring the kernel arm to beat it;
  P3 e9.reg/e9.\* and f2 rows carry it; P1 §8 rows HC1/HE1 name it; P6 budgets it.
- **RT-3 — CLOSED (stands).** `10-model-record-interface.md` in place (IF-A/B/C, IF-C
  default, IF-1 fork with the h ≥ 0.2 format-tax predicate, ≥300-output labelled set per
  rung, Wilson-LB > 10% ⇒ INSTRUMENT-INVALID, no-free-wins/losses accounting,
  shared-affordance rule); P3 has `f2.iface`/`e9.iface` AUTO-GATEs with
  `d-xif ≺ iface ≺ run` hard ordering.

### Deferred MINOR items (verified still open; ratify-or-defer at GNG-0, not blockers)

- **RT-16** — G9 primary remains Wilson-bound vs DeepNSM's published point estimate
  (P1 HS-A; P6 keeps the published-numbers route when HF artifacts are absent); G4's
  "effort" metric still undefined (effort logs collected, no metric pinned).
- **RT-17** — second-provider check still G4/G9 only; E9 judge remains "non-LLM rubric OR
  leak-checked judge".
- **RT-20** — P2 §3.3 commentary claim-scanning exclusion still circular as written.
- **RT-21** — HC1 kill retains the "at ≤ arm 3's cost" conjunct; no HC2 "N×" phrasing ban
  at floored denominators.
- **RT-22** — dense-retriever RAG config still optional ("if … pre-registered"), BM25
  primary.
- **RT-23** — AWS quota correctly marked BLOCKED/non-critical, but the "2–3 days' notice"
  reroute promise still stated (quota permitting).

(RT-18 — previously listed open — was applied this pass: M0 = Jul 22 in P3 §5 and
00-overview, GATE-T1 adjusted; it leaves the deferred list.)

### Second-pass verdict

**READY-TO-FREEZE.** All seven previously-PARTIAL items (RT-5, RT-7, RT-8, RT-9, RT-12,
RT-13, RT-14) and the 04-vs-02 amendment-cutoff inconsistency are CLOSED and consistent at
every designated enforcement point; the three CRITICALs remain closed. No blocker to
signing GNG-0 remains in the plan text. Two cosmetic one-word/one-example nits (P8 §1.8
"independent audit" cross-ref; P9's `kern/fable-runner-3` example vs P2 constraint 10) can
be patched any time before their docs are next linted — neither touches a frozen surface.
The deferred minors above go to the maintainer at GNG-0 as ratify-or-defer line items. The
threshold choices the fix agents set on the maintainer's behalf (IF-C default + IF-1 fork
trigger; the 10%-Wilson/≥300-output extraction gate; the 1-and-2 replication-buy cap; the
D-EXT WiC→OpenBookQA→MMLU preference order; the E8-R ≥85-stable-pair floor; the M0b
NICHE-SCOPE 20% default; the F-H0 8-member family; the ≥4/5 seed-sign gate; the canonical
cap table; g2.gold n = 500; the first-final-phase-run amendment cutoff) are all
pre-registration content and should be explicitly ratified in the GNG-0 signing record.
