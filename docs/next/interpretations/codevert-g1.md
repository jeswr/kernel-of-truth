# FABLE INTERPRETATION — CODEVERT G1-FORWARD (re-scoped FL-4 vertical on the pinned 20-repo pool: κ_q^indep = 0.7435 [0.6072, 0.8773] [MEASURED, gold-free], ENTIRE band above the 0.5 floor — the coverage leg the raw G0 vertical failed is cleared at scope; precision 0.9325 and R_q 0.7688 [both MEASURED + PROVISIONAL-ON-LLM-PROXY] sit below their floors AT POINT, but the precision miss is ONE repairable AnnAssign extractor defect and the R_q miss is 100% explicit UNKNOWN-INCOMPLETE abstention [both MEASURED + PROVISIONAL-ON-LLM-PROXY]; every gold-dependent number PROVISIONAL-ON-LLM-PROXY; PY-STAT/2 bounded-dataflow spike recovers 0.0000 of the inverse-family ablation headroom [MEASURED] — the '*'-mass ceiling is structural UNDER the registered all-or-nothing §2.2 endpoint and the tested bounded D1–D3 approach on the 6-repo G0 spike, NOT a general impossibility over all engineering approaches; recommendation: option (ii) AnnAssign version-bump re-run, with option (iii) R_q re-pin flagged as a maintainer design decision; no verdict issued here)

- **Author:** Fable (interpretation agent), 2026-07-11. This document
  interprets the MEASURED G1-forward result; it registers nothing, edits no
  frozen object, issues no verdict, writes no registry line, and performs
  no git/bd/kb operation. The coordinator computes the mechanical verdict
  and commits; the maintainer + review gate own every feasibility call.
- **Sources (read at source, in full):**
  `docs/next/analysis/codevert-g1-forward.md` (the measured verdict-input —
  authoritative for every G1 number below),
  `poc/codevert-g1/DESIGN-PIN.md` (pinned pre-clone, sha `48283b6f…` in
  `freeze-manifest.json`; PROPOSED-ASM ASM-1110…ASM-1119),
  `poc/codevert-g1/results/g1-metrics.json` + `g1-endpoints-proxygold.json`
  + `results/census-g1.json` (hashes verified against the freeze manifest),
  `poc/codevert-g1/annotation/` (agreement-raw, adjudication.jsonl),
  `poc/codevert-g1/pystat2-spike/RESULT.md`,
  `docs/next/analysis/codevert-g0.md` + `docs/next/interpretations/codevert-g0.md`
  (the G0 below-floor baseline and its re-scope-or-drop implication),
  `docs/next/interpretations/f2b-transfer-stage2.md` +
  `docs/next/feasibility-synthesis-v3.md` (the standing capstone this
  result feeds), `registry/assumptions.jsonl` (ASM id-space check).
- **Epistemic discipline:** **[MEASURED]** restates a counted/computed fact
  strictly from a cited artifact, never recomputed; every gold-dependent
  MEASURED quantity additionally carries **[PROVISIONAL-ON-LLM-PROXY]** —
  both annotators are LLM stand-ins for the ASM-1030 human annotators, and
  per ASM-1113 (PROPOSED) every such number is VOID as evidence the moment
  a human re-annotation of the same sample lands (the g3-humangold /
  Google-Sheet reconciliation pattern); **[STIPULATED]** marks registered
  or PROPOSED design text consumed as-is; **[DERIVED]** marks this
  document's own rule-application from MEASURED facts; **[IMPLICATION]**
  marks a decision-relevant consequence surfaced for the
  coordinator/maintainer, never a conclusion; **[ESTIMATED]** marks the one
  forward projection, labelled where it appears; **[EXTRAPOLATION]** is
  direction-only and load-bearing for nothing. **NO sentence in this
  document is a feasibility conclusion** — that call belongs to the
  maintainer and the external review gate.
- **Governance status, stated first because it bounds everything:** G1-forward
  ran under the maintainer's issue-#16 decision (2026-07-11): re-scope leg
  (A) to the forward/lexical subset with two LLM annotators, plus leg (C)
  the PY-STAT/2 spike [STIPULATED: DESIGN-PIN header]. The design was
  pinned and hashed pre-clone (filesystem-time-consistent ordering only,
  the G0 auditability caveat verbatim, mitigated by the staged manifest and
  discharged only by the coordinator's commit) [STIPULATED + MEASURED:
  freeze-manifest.json]. The floors quoted throughout are the ASM-1030
  planning floors; the mechanical comparison against them is the
  COORDINATOR's step, not this document's.

---

## 1. What G1-forward ESTABLISHES for the code vertical

### 1.1 The coverage leg the raw vertical failed is now cleared, at scope

**The fact** [MEASURED: analysis §3; g1-metrics.json]: on the
pinned-before-looking 20-repo pool (268,869 LOC, zero substitutions,
94,545 census queries, frozen + hashed before extraction), FL-4
κ_q^indep = **0.7435, sensitivity band [0.6072, 0.8773], query-pooled**
(family-macro 0.7597 [0.6696, 0.8478]). The point estimate AND the entire
band sit above the 0.5 floor. This is the mechanical, gold-free leg — no
LLM proxy touches it; it is MEASURED without qualification.

**The reading** [DERIVED]: G0's headline was 0.4361 [0.3610, 0.5364] on
6 agent-selected repos — below floor at point, CI straddling
[MEASURED: G0 interp §1]. The G0 interpretation's conditional
extrapolation was that a full-8-family G1 kill would fire; G1-forward now
confirms BOTH halves of that prediction on a pinned, disjoint,
3.3×-larger pool: the all-8 disclosure aggregate reproduces the collapse
(**0.4301 [0.3794, 0.4756]** — the G0 structural finding TRANSFERS,
[MEASURED]), and the re-scoped FL-4 subset clears decisively. The
forward/lexical fragment was not a small-pool artifact; neither was the
inverse-family zero (callers_of 0.0000, instance_of 0.0000, imported_by
0.3118 on the new pool [MEASURED]). What G0 could only extrapolate,
G1-forward has measured.

### 1.2 The two point-failures, decomposed — and why the decomposition is the load-bearing finding

Sources: analysis §5; g1-endpoints-proxygold.json. Tags are PER ROW —
the κ row is gold-free and carries no proxy rider; the
[MEASURED + PROVISIONAL-ON-LLM-PROXY] tag applies to the gold-dependent
rows (precision, R_q, negative validity) and to the agreement/
adjudication figures, NOT as an umbrella over κ. Gold-dependent rows are
scored against the adjudicated 200-query proxy gold (raw inter-annotator
agreement 0.915 exact-set / 0.957 Jaccard / answerability κ 0.807;
17 disagreements adjudicated with logged rationale; 0 dropped — all
[MEASURED + PROVISIONAL-ON-LLM-PROXY]):

| endpoint | measured | ASM-1030 floor | at point | tag |
|---|---|---|---|---|
| κ_q^indep (full census, gold-free) | 0.7435 [0.6072, 0.8773] | ≥ 0.5 | above, entire band | [MEASURED, gold-free] |
| precision (474 elements) | 0.9325 | ≥ 0.95 | below | [MEASURED + PROVISIONAL-ON-LLM-PROXY] |
| R_q (160 gold-answerable) | 0.7688 | ≥ 0.90 | below | [MEASURED + PROVISIONAL-ON-LLM-PROXY] |
| negative-answer validity (6 gold-empty) | 1.0000 | ≥ 0.90 | above | [MEASURED + PROVISIONAL-ON-LLM-PROXY] |

The decomposition [MEASURED + PROVISIONAL-ON-LLM-PROXY, both roots —
both are scored against the proxy gold]:

1. **Precision: one mechanical defect, fully enumerated.** All 32/32 wrong
   proved elements are annotation-only `AnnAssign` declarations
   (`name: type` with no value) that PY-STAT/1 emits as binding/contains
   facts. Under the pinned gold semantics (ASM-1053 "assigns" — an
   annotation without a value binds nothing at runtime; a Python language
   fact) these are false facts. Evidential basis, stated precisely
   [MEASURED: annotation/adjudication.jsonl]: the three AnnAssign-bearing
   queries were blind DISAGREEMENTS, not replications — annotator B
   included the annotated names; adjudication (rationales logged, each
   case verified at source) selected annotator A's exclusion — so the
   defect is supported by ADJUDICATED proxy gold plus source
   verification, not by independent blind two-annotator agreement. Every other scored element — 442/442 — is
   correct. Post-fix precision on this sample is 1.0 **[ESTIMATED — a
   projection, not a measurement; it must be re-measured on a pinned
   re-run, never assumed]**.
2. **R_q: 100% honest abstention — zero wrong PROVED answers beyond the
   AnnAssign defect.** (Precision is computed over proved queries only;
   unknown partial listings are not precision-scored, so "no wrong
   answers" claims are scoped to proved/scored answers.) All 37 FL-4
   misses are explicit `UNKNOWN-INCOMPLETE` abstentions on
   gold-answerable queries (imports_of 17/40:
   conditional/lazy imports blocking the §2.2 precondition; where_defined
   20/40: the hazard-repo bimodality — 1.0 on the 10 hazard-free repos,
   0.0 on the 10 carrying any setattr/exec/dynamic-namespace hazard). No
   silent empty answer exists (neg-validity 1.0). The instrument is
   charging its own fail-closed abstentions against a floor written as if
   abstention were error.

**What is therefore established** [DERIVED]: on this pool and this proxy
gold, the re-scoped vertical exhibits exactly the profile the fail-closed
design promises — *never wrong on a proved answer except via one
identified mechanical defect, honest about every gap* — and fails its floors only where (a) the
extractor disagrees with its own pinned gold semantics on one AST node
type, and (b) the floor's charging semantics counts disclosed abstention
as failure. Whether that profile "clears the correctness bar" is NOT this
document's call: at point, two floors are missed, and a mechanical verdict
on the floors as written kills [IMPLICATION: coordinator's step]. What IS
established, as verdict-input: the failure modes are enumerated,
non-diffuse, and of exactly the two kinds (repairable defect; charging
semantics) that the ASM-1030 floor structure was designed to distinguish
from diffuse incapacity.

### 1.3 Scope caveats that ride every citation of §1.1–1.2

[DERIVED, from the analysis §9 honest-limits, all endorsed]:

- **Proxy gold, not human gold.** Two LLM annotators, cross-family but
  possibly sharing training-data blind spots; two context-discipline
  violations (one per annotator) were caught only by mutual disagreement —
  colluding errors would pass silently; the adjudicator is the same
  identity class as annotator-a (disclosed, rationales logged for external
  re-adjudication). Agreement 0.915 characterizes the observable
  disagreement between the two proxies; it does NOT bound shared /
  common-mode error — with no human truth in the loop, correlated
  blind spots are undetectable by agreement alone.
  Every §1.2 gold-dependent number is PROVISIONAL-ON-LLM-PROXY and void on
  human re-annotation. This run CANNOT discharge ASM-1038's
  human-annotation obligation; it stands in for it.
- **Agent-selected pool.** Pinned-before-looking, but from agent memory,
  not sampled: every band is a resampling sensitivity band, never a
  generalization CI.
- **The annotated sample is cap-biased** toward smaller modules (481
  replacements under the 120 KB rule, disclosed); the κ headline is
  cap-free and unaffected.
- **where_defined is bimodal, not uniformly covered**: FL-4's clearance
  carries a family whose per-repo κ is 0/1 hazard-driven; any product
  claim over FL-4 must disclose that the fourth family is
  hazard-conditional [MEASURED: per-family 0.4110 pooled].
- **The srconly 0.9820 slice is FL-3 only** (where_defined not
  file-stratifiable, inherited G0 limitation).
- Nothing here is evidence about kernel CONTENT (ASM-1000), NL entry, or
  the excluded inverse families' product value [STIPULATED].

## 2. The §5 three options — recommendation and rationale

The analysis §5 leaves the coordinator three choices: **(i)** mechanical
verdict on the ASM-1030 floors as written (R_q/precision kill at point,
PROVISIONAL-ON-LLM-PROXY); **(ii)** authorize the AnnAssign fix as a
pinned extractor version bump + G1 re-run; **(iii)** re-pin the R_q floor
against answered-queries for a fail-closed abstaining instrument
[STIPULATED: analysis §5 "Reading"].

**Recommendation [IMPLICATION — a routing recommendation, not a verdict
and not a feasibility conclusion]: execute (i) AND (ii); route (iii) to
the maintainer as a design decision that re-enters the review gate.**

- **(i) is not optional and should not be skipped to spare the result.**
  The coordinator should record the mechanical verdict on the floors as
  written — kill at point on precision and R_q, tagged
  PROVISIONAL-ON-LLM-PROXY — because the floors were pinned before the
  numbers existed (ASM-1116) and the register's integrity depends on
  never suppressing a mechanical outcome. The verdict record should carry
  the §1.2 root-cause decomposition beside it verbatim.
- **(ii) is the correct next spend and is cheap, mechanical, and already
  semantically licensed.** The defect is a disagreement between the
  extractor and its OWN pinned gold semantics (ASM-1053), supported by
  adjudicated proxy gold plus source verification (the three AnnAssign
  cases were annotator disagreements — annotator B included the names —
  adjudicated to annotator A, not blind replications); the fix is one
  condition; the re-run
  is 19 s of compute plus re-scoring, with NO new annotation needed for
  the precision leg (the same 200-query proxy gold rescored against the
  new engine output) [MEASURED: analysis §5.1 + §2 resource facts].
  Crucially, (ii) is NOT floor-shopping: it changes the instrument to
  match the registered semantics, not the floor to match the number. Per
  ASM-1031 it is an extractor VERSION change — new inventory hash, new
  census freeze, deliberate — and §3 below specifies it precisely.
- **(iii) is defensible on the evidence but is exactly the move the G0
  interpretation flagged as epistemically dangerous** (its option (b)
  analysis, endorsed verbatim): re-defining what "answered" or what the
  R_q denominator charges converts a floor-failure into a floor-pass by
  definitional change. The measured facts make the case FOR it stronger
  than at G0 (0 wrong proved answers beyond the AnnAssign defect, all
  R_q misses explicit UNKNOWN-INCOMPLETE abstentions, neg-validity
  1.0 — the floor as written cannot distinguish this instrument from one
  that guessed and was wrong 23% of the time, which is a real
  mis-specification argument); but legitimacy requires (a) the
  re-definition registered BEFORE any re-scored readout, (b) the G1
  as-written numbers carried beside the change in perpetuity, and (c) the
  utility of abstention-heavy answers independently measured (a G2/G4
  question no current run licenses). That is a maintainer design decision
  under the rev-2 review-gate ruling, not a coordinator mechanical step
  and not a Fable call [DERIVED from the G0 interp §3(b) discipline].
- Sequencing note [IMPLICATION]: (ii) resolves ONLY the precision leg
  (projected 1.0 [ESTIMATED]); R_q is untouched by the fix (its misses
  are abstentions, not AnnAssign artifacts). So (ii) alone leaves one
  floor failed at point, and the vertical's disposition still turns on
  (iii)-or-not. The maintainer should decide (iii) with the post-(ii)
  re-measured numbers in hand, not before.

## 3. OPS-AMENDMENT vs maintainer-judgment — the precise split

**3a. The AnnAssign extractor fix: a precisely-specifiable OPS-AMENDMENT
candidate** [DERIVED]. Fable can specify it completely; nothing in it
requires judgment beyond sign-off:

> AMENDMENT SPEC (proposed text, coordinator to register on maintainer
> sign-off): In PY-STAT/1's `AnnAssign` handling, when `node.value is
> None`, emit NO binding/contains fact for the annotated name (an
> annotation without a value creates no runtime binding; conformance to
> ASM-1053 "assigns" gold semantics). This is an extractor VERSION change
> per ASM-1031: bump the extractor version label; regenerate + re-hash
> `inventory.json`; re-freeze the G1 census discipline (the census
> generator is extractor-independent, so `census-g1.json` sha `b64a6930…`
> is expected byte-stable — verify, do not assume); re-run extraction +
> κ on the pinned 20-repo pool at the recorded SHAs
> (`repos.lock.json` sha `64b5e2b8…`); re-score the EXISTING 200-query
> adjudicated proxy gold (annotation sha-pinned in freeze-manifest.json)
> against the new engine answers — no new annotation for the precision
> leg; report κ/precision/R_q/neg-validity deltas side-by-side with the
> v1 numbers; the post-fix precision claim remains [ESTIMATED] until this
> re-run lands and remains PROVISIONAL-ON-LLM-PROXY after it; and,
> being re-scored on the SAME 200-query sample, the post-fix precision
> is adaptive/in-sample repair verification — suitable for verifying the
> repair, NOT independent replication or fresh generalization evidence
> [review-gate determination, endorsed].

The one caveat that keeps this honest [IMPLICATION]: although the fix is
mechanically specified, ASM-1031 version changes touch a registered
design object, so whether it may proceed as an ops amendment or must
re-enter the external review gate is the review-gate's call under the
rev-2 ruling — this document asserts the SPEC is complete, not that the
gate is waived.

**3b. The R_q abstention-charging semantics: a MAINTAINER-judgment flag,
not specifiable as an ops amendment** [DERIVED]. Any re-pin requires
choosing among materially different semantics — charge abstentions fully
(status quo); score R_q over answered-queries only with abstention rate
co-reported; count `UNKNOWN-INCOMPLETE(partial_listing, blocking_count)`
as a first-class answer with its own quality endpoint (G0 option (b));
or keep the floor and re-scope the product's answerability claim — and
each choice changes the ENDPOINT (ASM-1116/ASM-1030), redistributes what
the 0.90 floor means, and presupposes an unmeasured utility judgment
about abstention-heavy products. There is no unique mechanical
completion; Fable cannot write it as a spec without making the design
decision. FLAGGED for the maintainer, with the §1.2 decomposition (0
wrong proved answers, 100% disclosed abstention) as the evidence that makes the
question live [IMPLICATION]. (Scope rider on "0 wrong answers"
throughout: zero wrong PROVED/scored answers beyond the AnnAssign
defect — precision is measured over proved queries only; all R_q misses
were explicit UNKNOWN-INCOMPLETE abstentions, which are not
precision-scored.)

## 4. What this does to the CORRECTNESS thesis

**The thesis does not move** [DERIVED, stated deliberately]: by
registered stipulation ASM-1000, no CODEVERT outcome in either direction
is evidence about kernel CONTENT; CODEVERT is the kernel-free vertical.
CORRECTNESS remains INCONCLUSIVE-PENDING exactly as feasibility-synthesis
v3 §2 holds; nothing here touches g2, g3 Pass B, NL entry, or coverage.

**What moves is the evidence base under the synthesis's §4 pointer**
[DERIVED + EXTRAPOLATION, direction-only]: v3 §4 reads the accumulated
results as pointing toward "small model + aligned, authored,
externally-true store + deterministic checker", citing G0's
forward/lexical fragment as "the routable substrate" — *typed aligned
stores with honest incompleteness*. G1-forward strengthens that
constituent from an off-pool spike observation to an on-pool measured
one: the fragment's coverage clears its floor with the whole band on a
pinned 20-repo pool [MEASURED, gold-free], and its answer-quality
profile on proxy gold is "exact where it answers (one enumerated defect
aside), honest where it doesn't" [MEASURED + PROVISIONAL-ON-LLM-PROXY].
The all-8 transfer (0.4301) simultaneously HARDENS the boundary of that
pointer: the deep/inverse half of the query surface stays measured-out
at PY-STAT/1+§2.2 semantics, now on two disjoint pools, with the §6
spike closing the cheap repair route AT ITS TESTED SCOPE — bounded
D1–D3 candidate mechanics under the registered all-or-nothing §2.2
endpoint, on the 6-repo G0 spike pool — not over all engineering
approaches.

**The one-sentence thesis update** (for the coordinator, tags included):
*The code vertical's re-scoped forward/lexical fragment now has
on-pinned-pool MEASURED coverage above floor and a
PROVISIONAL-ON-LLM-PROXY proxy-gold profile of zero wrong PROVED answers
beyond one enumerated repairable defect (precision is scored over proved
queries only) with all R_q misses explicit UNKNOWN-INCOMPLETE
abstentions —
strengthening, direction-only, the "aligned typed store with honest
incompleteness" success mode of feasibility-synthesis v3 §4, while
moving neither thesis and remaining void on human re-annotation.*

**The reconciliation obligation** [STIPULATED: ASM-1113 (PROPOSED), the
g3-humangold pattern]: every §1.2/§2 gold-dependent quantity carries
PROVISIONAL-ON-LLM-PROXY until human annotators re-annotate the same
200-query sample (the Google-Sheet proxy-reconciliation pattern used for
g3: the human pass is the sole adjudicator; on landing, the proxy
numbers are void as evidence and survive only as a priced
proxy-agreement measurement). The 0.915 raw LLM–LLM agreement and the
logged per-item adjudication rationales are the assets that make that
reconciliation cheap and auditable [MEASURED: annotation/ artifacts].
Until then, no programme prose should cite a G1 precision/R_q number
without the proxy rider.

## 5. The PY-STAT/2 NO and the '*'-mass ceiling (structural at the tested scope: §2.2 all-or-nothing endpoint + bounded D1–D3 mechanics, 6-repo G0 spike)

**The fact** [MEASURED: pystat2-spike/RESULT.md]: bounded local dataflow
(D1 local-alias, D2 parametrized-decorator return, D3 call-result
return; candidates-only, fail-closed, proved-sets hard-asserted
identical to PY-STAT/1 on all 6 G0 repos) converts 22.55% of the
unrestricted '*' call mass (1,685 → 1,305) at ~1.5× extraction cost —
and recovers **0.0000 of the callers_of 0.54–0.92 ablation headroom, on
every inverse family, on every repo; κ bit-identical to PY-STAT/1 on all
8 families × 6 repos**. Cause is structural: §2.2 is all-or-nothing per
repo, and even a PERFECT D1–D3 leaves 11–180 untargetable '*' edges per
repo (module-binding aliasing, getattr, exec taint). Mean blocking mass
on the killed families fell ~25% — worth something only under a
per-candidate/partial-answer semantics, which is a §2.2 re-scope, not an
extractor patch. Narrowing also surfaced 4 observed-truth exclusions
(implicit C-mediated / metaclass dispatch that '*' had absorbed
vacuously): any full build must pre-pin probe domain exclusions or
accept candidate-soundness misses [MEASURED].

**What it means** [DERIVED]:

1. **The '*'-mass ceiling is a design boundary, not an engineering gap —
   AT THE MEASURED SCOPE: structural UNDER the registered all-or-nothing
   §2.2 endpoint and the tested bounded D1–D3 approach, on the 6-repo G0
   spike pool. This is NOT a general impossibility claim over all
   engineering approaches** (heavier mechanics and endpoint re-scopes
   remain open, untested routes — see (a)/(b) below).
   G0 left open that the inverse-family zeros might yield to a cheap
   extractor generation; the spike closes that route measured-ly at that
   scope. The
   registered κ on the inverse families is unreachable by
   candidate-mechanics of the D1–D3 class; it moves only via (a) a much
   heavier package driving '*' to literally zero per repo
   (module-scope alias dataflow + getattr/exec policy — the ASM-1057
   tier-b closure named as the binding risk), or (b) re-scoping §2.2 to
   per-candidate blocking — both design decisions above spike grade, and
   any promotion is an ASM-1031 version change [STIPULATED: spike §4].
2. **This retroactively ratifies the FL-4 pin.** Excluding
   callers_of/imported_by/instance_of from the re-scoped product
   (ASM-1110) is now backed by a measured no-cheap-repair result, not
   only by G0's observation of the collapse — the exclusion is
   principled, not cosmetic [DERIVED].
3. **The ~25% blocking-mass reduction is an asset ONLY for option-(b)
   futures.** If the maintainer ever re-opens
   UNKNOWN-INCOMPLETE-as-product (G0 §5.3(b) / §3b above), the spike
   shows bounded dataflow buys real partial-answer quality; under the
   registered semantics it buys exactly nothing. The build/no-build
   verdict-input stands: **NOT worth a full build in this form**
   [MEASURED: spike §4, restated as input — the build decision is the
   maintainer's].

## 6. ASM-1110…ASM-1119 — coordinator-registerability confirmed

[DERIVED, checked at source]: (a) **Id-space disjoint** — the registry's
assumptions ledger currently ends at ASM-1079; no ASM-11xx ≥ 1100 exists
in `registry/assumptions.jsonl` [MEASURED: grep over the ledger,
2026-07-11]. (b) **Schema-mappable** — each DESIGN-PIN §6 row carries
`id` + a self-contained scope/claim sentence, mapping mechanically onto
the ledger's row shape (`id`, `claim` = the §6 scope text, `tag` =
STIPULATED for ASM-1110–1119 as pinned design choices, `backing_ref` =
`poc/codevert-g1/DESIGN-PIN.md` sha `48283b6f…` + `freeze-manifest.json`,
`load_bearing`, `status`, `owner`, `date`); no field the ledger requires
is missing from the pin. (c) **No handle/account strings** appear in the
block (the annotator identities are model/CLI labels, not accounts;
ASM-1119 itself pins that rule). The rows are registerable as-is by the
coordinator; registration is the coordinator's act, not this document's
[IMPLICATION].

## 7. Honest gaps, carried verbatim

1. **Human gold: [UNMEASURED].** Everything gold-dependent is LLM-proxy;
   ASM-1038's annotation obligation is undischarged (analysis §7 says so
   explicitly, endorsed).
2. **Post-fix precision: [ESTIMATED]** — the only forward-looking number
   anywhere in the chain; it must be re-measured under the §3a spec.
3. **Freeze ordering** [MEASURED: freeze-manifest.json staging state,
   2026-07-11] is filesystem-time-consistent only until the
   coordinator's commit creates git objects (G0 caveat class, mitigated
   by the staged manifest, not discharged).
4. **Product utility of abstention-heavy answers: [UNMEASURED]** — the
   entire case for §3b's option-(iii)/option-(b) semantics rests on a
   G2/G4-class question no current run touches.
5. **The census universe is constructed** (syntactic visibility, not
   developer demand); the FL-4 headline inherits its stratification, and
   contained_in alone contributes 23,872 of 94,545 queries [MEASURED:
   analysis §2 counts; DERIVED: the weighting observation].
6. **where_defined bimodality** [MEASURED: per-repo κ 1.0 on the 10
   hazard-free repos, 0.0 on the 10 hazard-carrying repos; pooled
   per-family 0.4110 — gold-free census leg] means FL-4 coverage on
   hazard-carrying repos is materially worse than the pooled headline;
   any product surface must disclose per-repo hazard status [DERIVED].

## 8. Self-check gate (run before hand-off, per the session governance)

- Every RECOMMENDATION/DECISION line cites its governing ASM: §2 routing
  → ASM-1116/ASM-1030 (floors + coordinator verdict), ASM-1031 (version
  change), ASM-1113 (proxy voidability); §3a spec → ASM-1031/ASM-1053;
  §3b flag → ASM-1116/ASM-1030 + the G0-interp option-(b) discipline;
  §5 → ASM-1057/ASM-1117/ASM-1118/ASM-1031; §6 → ASM-1119. ✅
- Every empirical claim carries a local or umbrella tag —
  [MEASURED]/[ESTIMATED]/[UNMEASURED]/[DERIVED] — including the title,
  §7.3 (freeze ordering) and §7.6 (where_defined bimodality); the §1.2
  table is tagged PER ROW: the κ row [MEASURED, gold-free] and
  [MEASURED + PROVISIONAL-ON-LLM-PROXY] on the gold-dependent rows
  (precision, R_q, neg-validity) and on the agreement/adjudication
  figures only — never as an umbrella over κ. ✅
- Rev-1 (2026-07-11, post GPT-5.6 review gate): six wording/tagging
  corrections applied — AnnAssign support restated as adjudicated proxy
  gold + source verification (three blind DISAGREEMENTS adjudicated to
  annotator A; NOT blind two-annotator replication); "zero wrong
  answers" narrowed to zero wrong PROVED/scored answers beyond the
  AnnAssign defect (all R_q misses explicit UNKNOWN-INCOMPLETE
  abstentions; precision is scored over proved queries only); κ row
  tagged separately from the proxy umbrella; agreement 0.915 restated
  as characterizing observable proxy disagreement, NOT bounding
  common-mode error; the structural-ceiling claims scoped to the
  registered all-or-nothing §2.2 endpoint + tested D1–D3 approach on
  the 6-repo G0 spike; untagged empirical statements (title, §7.3
  freeze ordering, §7.6 bimodality) given local tags. Additionally,
  from the review's determinations: the §3a spec now states that
  same-sample post-fix precision is adaptive/in-sample repair
  verification, not independent replication. The recommendation
  ((i)+(ii), (iii) flagged to the maintainer) and all numbers are
  UNCHANGED. ✅
- No feasibility conclusion is stated anywhere; the mechanical verdict is
  reserved to the coordinator, the (iii) decision and any build/re-scope
  to the maintainer + review gate. ✅
- No @handle/account strings appear in this document. ✅
- No git/bd/kb operation was performed; nothing frozen was edited; this
  file is the only artifact written. ✅

## 9. One-paragraph summary

G1-forward did what the issue-#16 re-scope asked: on a
pinned-before-looking 20-repo pool it measured the forward/lexical FL-4
vertical clearing the 0.5 coverage floor with its entire sensitivity band
(κ_q^indep 0.7435 [0.6072, 0.8773], gold-free) while the all-8 aggregate
(0.4301) reproduced G0's structural collapse — converting G0's
extrapolations, in both directions, into on-pool measurements [MEASURED].
Against two-LLM proxy gold (agreement 0.915, PROVISIONAL-ON-LLM-PROXY,
void on human re-annotation) the vertical fails precision (0.9325 < 0.95)
and R_q (0.7688 < 0.90) at point — but the precision miss is one
enumerated, mechanically-specifiable AnnAssign defect (post-fix 1.0
[ESTIMATED]) and the R_q miss is 100% honest UNKNOWN-INCOMPLETE
abstention — zero wrong PROVED answers beyond the AnnAssign defect
(precision is scored over proved queries only) — with neg-validity 1.0
[MEASURED +
PROVISIONAL-ON-LLM-PROXY]. Recommended routing [IMPLICATION]: record the
mechanical verdict on the floors as written (i), authorize the AnnAssign
version-bump re-run per the §3a spec (ii — an ops-amendment-grade fix,
review-gate permitting), and put the R_q abstention-charging re-pin (iii)
to the maintainer as the design decision it is. The PY-STAT/2 spike's
0.0000 headroom recovery makes the '*'-mass ceiling structural UNDER
the registered all-or-nothing §2.2 endpoint and the tested bounded
D1–D3 approach on the 6-repo G0 spike pool — not a general
impossibility over all engineering approaches — and the inverse-family
exclusion principled; the cheap D1–D3-class repair route is closed at
that scope [MEASURED]. Neither thesis moves; the "aligned typed store with honest
incompleteness" pointer of feasibility-synthesis v3 §4 is strengthened
direction-only, pending human reconciliation of the proxy gold via the
g3-humangold pattern.
