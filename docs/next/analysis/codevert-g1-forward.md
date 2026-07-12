# CODEVERT G1-FORWARD readout — the re-scoped forward/lexical vertical, measured; + the PY-STAT/2 spike

> **Status: [MEASURED verdict-INPUT, PROVISIONAL-ON-LLM-PROXY on every
> gold-dependent number].** Per the maintainer decision on issue 16
> (2026-07-11): (A) CODEVERT re-scoped to the forward/lexical subset, G1 run
> with Fable + GPT-5.6 as the two annotators (LLM stand-ins for the ASM-1030
> human annotators — the g3-humangold pattern: every gold-dependent quantity
> is void as evidence the moment a human re-annotation of the same sample
> lands); (C) a PY-STAT/2 bounded-dataflow spike. **No verdict is issued
> here** — the coordinator performs the mechanical verdict against the
> pinned floors. This document registers nothing, edits no registry,
> performs no git/bd/kb operation; the coordinator commits. New assumptions
> are PROPOSED-ASM block **ASM-1110…ASM-1119** (disjoint), pinned in
> `poc/codevert-g1/DESIGN-PIN.md` §6 BEFORE any G1 repo was cloned
> (pre-clone manifest sha in `poc/codevert-g1/freeze-manifest.json`;
> ordering is filesystem-time-consistent only — the G0 auditability caveat
> applies verbatim until the coordinator's commit creates git objects).
> Author: Fable experiment agent, 2026-07-11. Artifacts:
> `poc/codevert-g1/` (design pin, lock file, frozen census, metrics,
> annotation corpus, endpoints) and `poc/codevert-g1/pystat2-spike/`.

## 1. The re-scoped vertical: CODEVERT-FL/1 [PROPOSED-ASM: ASM-1110]

Primary family set **FL-4 = {contains, contained_in, imports_of,
where_defined}** (the maintainer's named list "defines-where / imports /
contains / lexical" mapped onto the measured family inventory);
**callees_of is a disclosed sensitivity slice** (G0 κ 0.2326 does not clear
the floor and it is absent from the maintainer's list); the inverse/
exhaustive trio (callers_of, imported_by, instance_of) is excluded — that
is the G0 structural collapse and the PY-STAT/2 spike's territory (§6).
DISCLOSED AMBIGUITY, resolved at pin time, not post-hoc: the brief's
"κ≈0.72" is G0's *forward-4* macro (which includes callees_of and omits
where_defined); the FL-4 set as pinned scored 0.7502 query-pooled / 0.7615
macro on the G0 pool — both readings clear 0.5, and the pinned primary is
FL-4.

## 2. G1 setup (all pins in DESIGN-PIN.md, hashed pre-clone)

- **Pool [ASM-1111]:** 20 repos pinned by name+order before looking, size
  band [300, 120000] `*.py` LOC, MIT/BSD/Apache/PSF, disjoint from the G0
  six; all 20 primaries cloned clean, **zero substitutions**; exact SHAs in
  `repos.lock.json`. 268,869 LOC total. Agent-selected list: every
  cross-repo band below is a resampling SENSITIVITY band, not a
  generalization CI.
- **Census [ASM-1112]:** the G0 extractor-independent generator logic
  (census.py sha `2922ac79…`, mechanically re-pathed; diff in repo), seed
  **20260716**, frozen + hashed before extraction
  (census-g1.json sha `b64a6930…`): **94,545 queries** (contains 3,566;
  contained_in 23,872; imports_of/imported_by 667 each; where_defined
  20,928; callees_of/callers_of 20,973 each; instance_of 2,899).
- **Extractor:** PY-STAT/1 **byte-identical** to G0 (extractor.py sha
  `b508d844…`, engine.py `4b62413d…`, inventory `aebfe0a0…`) — no version
  change, per ASM-1031.
- **Resources [MEASURED]:** extraction + full 94,545-query census in 19.0 s
  wall, peak RSS 256 MB, stores 42.6 MB total, on the pinned 2-vCPU box at
  nice 10. 174,137 edges: 92,414 proved / 81,723 unknown / 0 disproved /
  0 conflict.

## 3. [MEASURED] κ_q^indep on the pinned pool (mechanical, no gold needed)

| aggregate | κ_q^indep | 95% sensitivity band |
|---|---|---|
| **FL-4 primary, query-pooled** | **0.7435** | [0.6072, 0.8773] |
| **FL-4 primary, family-macro** | **0.7597** | [0.6696, 0.8478] |
| package-source-only slice (FL-3: where_defined not file-stratifiable, dropped — as in G0) | 0.9820 | [0.9778, 0.9861] |
| all-8 disclosure, query-pooled | 0.4301 | [0.3794, 0.4756] |

Per family (pooled): contains 0.9997, contained_in 1.0000, imports_of
0.6282, where_defined 0.4110 — where_defined is exactly the G0 bimodal
pattern: **1.0 on 10 hazard-free repos, 0.0 on the 10 repos carrying any
setattr/exec/dynamic-namespace hazard**. Sensitivity slice callees_of
0.1906. Excluded families reproduce the G0 collapse on this pinned pool:
callers_of 0.0000, instance_of 0.0000, imported_by 0.3118 — the G0
structural finding transfers from the agent-selected 6-repo pool to a
pinned 20-repo pool [MEASURED, this pool].

**The FL-4 point estimate AND its entire sensitivity band sit above the
0.5 floor.** (Floor quoted from ASM-1030; the mechanical comparison is the
coordinator's step.)

## 4. Proxy-gold annotation [PROPOSED-ASM: ASM-1113/1114/1115/1116; PROVISIONAL-ON-LLM-PROXY]

**Protocol:** 200 queries (2 per family × repo cell; FL-4 + callees_of
slice), seed-pinned from the frozen census; 120 KB context cap with pinned
next-index replacement (481 replacements logged — the sample is thereby
biased toward smaller modules, DISCLOSED). Two independent, blind
annotators with byte-identical instruction docs + context bundles built
from raw source only (prompts preserved verbatim; no extractor output in
any prompt byte): **fable-a** (Claude-family subagents, one per repo) and
**gpt56-b** (`gpt-5.6-sol`, pinned `npx @openai/codex@0.144.1` invocation,
isolated CODEX_HOME, ephemeral, read-only, memories/web disabled, effort
medium — a disclosed deviation from judge-1p's `low`; free-form code
reading, not MCQ). gpt56-b: **100/100 batches valid on first attempt, 0
no-labels, 395 s wall** for all 100 calls (3 workers).

**Inter-annotator agreement (RAW, pre-adjudication) [MEASURED]:**

| family | exact-set agreement | mean Jaccard | answerability κ |
|---|---|---|---|
| contains | 0.925 | 0.965 | 1.0 |
| contained_in | 1.000 | 1.000 | 1.0 |
| imports_of | 0.975 | 0.996 | 1.0 |
| where_defined | 1.000 | 1.000 | 1.0 |
| callees_of (slice) | 0.675 | 0.826 | 0.696 |
| **overall (200)** | **0.915** | **0.957** | **0.807** |

**Adjudication:** 17 disagreements, all adjudicated by the Fable main
agent with per-item logged rationale (`annotation/adjudication.jsonl`);
split fable-a 11 / gpt56-b 6. Three systematic sources: (i)
annotation-only class-body declarations (`name: type` with no value) —
verified at source in all three disputed cases to be non-assignments
(fable-a correct); (ii) ext-element naming drift (`ext:str.join` vs
`ext:builtins.str.join`) — canonicalized, affects nothing scored; (iii)
**one context-discipline violation by EACH annotator** (fable-a resolved
`attr.has` to a file whose source was not in context; gpt56-b did the
mirror-image on `dateutil.tz.datetime_ambiguous`) — both adjudicated
against the violator and DISCLOSED as a live LLM-proxy-annotator hazard.
Adjudicated proxy gold = 183 agreed + 17 adjudicated = 200; 0 dropped.

## 5. [MEASURED, PROVISIONAL-ON-LLM-PROXY] G1 endpoints vs the proxy gold — the verdict-input

| endpoint (FL-4 primary) | measured | ASM-1030 floor | at point |
|---|---|---|---|
| κ_q^indep (full census, §3) | 0.7435 [0.6072, 0.8773] | ≥ 0.5 | **above, entire band** |
| precision (element-level, 474 elements) | **0.9325** | ≥ 0.95 | **below** |
| R_q (completeness, 160 gold-answerable) | **0.7688** (exact-set 0.75) | ≥ 0.90 | **below** |
| negative-answer validity (6 gold-empty) | **1.0000** | ≥ 0.90 | above |

Per family: contains R_q 1.0 / precision 0.8951; contained_in 1.0 / 1.0;
imports_of R_q 0.575 / precision 1.0; where_defined R_q 0.50 / precision
1.0. Sensitivity slice callees_of: R_q 0.5455, precision 1.0 (4 elements
only), 18/40 unanswerable-static.

**Root-cause decomposition [MEASURED]:**

1. **The precision failure is ONE mechanical defect.** All 32/32 wrong
   proved elements are annotation-only `AnnAssign` declarations (no value)
   that PY-STAT/1 emits as binding/contains facts (`Template.name`,
   `CharInfo.alpha`, …). Under the pinned gold semantics (ASM-1053
   "assigns"; an annotation binds nothing at runtime) these are false
   facts. Every other element — 442/442 — is correct. Fixing it is a
   one-condition change (`node.value is None` ⇒ no binding) but is an
   ASM-1031 **extractor version change** (new inventory hash, new census
   freeze, re-run). Projected post-fix precision on this sample: 1.0
   [ESTIMATED, not measured].
2. **The R_q failure is 100% honest abstention, 0% wrong answers.** Every
   one of the 37 FL-4 R_q misses is `UNKNOWN-INCOMPLETE` on a
   gold-answerable query — imports_of misses (17/40) are conditional/lazy
   imports blocking the §2.2 precondition; where_defined misses (20/40)
   are the hazard-repo bimodality. No proved answer omitted a gold element
   except via the AnnAssign defect above; no silent empty answer exists
   (neg-validity 1.0). The gap between κ (0.74) and R_q (0.77 on the
   annotated sample) vs the 0.90 floor is the fail-closed design charging
   its own abstentions, exactly as ASM-1030 intended.

**Reading (not a verdict):** on LLM-proxy gold, the re-scoped FL-4
vertical **clears the coverage floor decisively** and fails R_q/precision
at point — but the precision failure is a single identified repairable
defect, and the R_q failure is abstention-shaped, which is exactly the
question option (b) (UNKNOWN-INCOMPLETE as first-class product output)
exists to answer. The coordinator's choices: (i) mechanical verdict on
the ASM-1030 floors as written (R_q/precision kill at point,
PROVISIONAL-ON-LLM-PROXY); (ii) authorize the AnnAssign fix as a pinned
extractor version bump + G1 re-run (cheap: 19 s compute + re-scoring, no
new annotation needed for the precision leg); (iii) treat the R_q floor as
mis-specified for a fail-closed abstaining instrument and re-pin it
against answered-queries (a DESIGN decision, not licensed by this run).

## 6. PY-STAT/2 spike (option C) — [MEASURED, NON-SCORED]

Built in `poc/codevert-g1/pystat2-spike/` [PROPOSED-ASM: ASM-1117/1118]:
`extractor2.py` = PY-STAT/1 + bounded local dataflow, candidates-only
(D1 function-scope alias tracking, D2 parametrized-decorator return
analysis, D3 call-result return analysis), fail-closed; proved-edge sets
hard-asserted identical to PY-STAT/1 on all 6 pinned G0 repos (passed; v1
side reproduces G0's published 0.4361 exactly — replication fidelity).

- **'*'-mass conversion:** 1,685 → 1,305 unrestricted call/instantiate
  edges (**22.55%** converted; D1: 137 sites, D2: 243, D3: 0 — no
  convertible `g(...)(...)` site exists on this corpus).
- **κ recovery vs the G0 ablation headroom (callers_of 0.54–0.92):**
  **0.0000, on every inverse family, on every repo** — κ is bit-identical
  to PY-STAT/1 on all 8 families × 6 repos. Cause is structural: the §2.2
  precondition is all-or-nothing per repo, and every repo retains an
  untargetable '*' floor (module-binding unknowns, getattr, exec taint:
  residual 11–180 per repo even under a PERFECT D1–D3). Partial '*'
  conversion buys ZERO registered κ; mean blocking mass drops ~25% —
  worth something only under a per-candidate/partial-answer semantics,
  which is a §2.2 re-scope (design decision), not an extractor patch.
- **Soundness cost of narrowing:** probe re-check on the saved G0 traces —
  0 proved-fact contradictions, but **4 observed-truth-excluded** edges
  (implicit-dispatch cases whose truth v1's '*' absorbed vacuously);
  strict misses 104 → 106.
- **Resources:** 7.7 s wall, 116 MB RSS; extraction cost ×1.5 vs v1.
- **Verdict-INPUT:** **PY-STAT/2 in this bounded-local-dataflow form: NOT
  worth a full build** — 0/4,286 additional proved inverse queries. The
  ablation headroom is reachable only by (a) a much heavier package
  (module-scope alias dataflow + getattr/exec policy) driving '*' to
  literally zero per repo, or (b) re-scoping §2.2 to per-candidate
  blocking — both are design decisions above spike grade; any promotion is
  an ASM-1031 extractor version change.

## 7. Costs [MEASURED]

Compute ~$0 (shared 2-vCPU box; G1 19 s + spike 7.7 s + tooling).
Annotation: gpt56-b 100 codex calls / 395 s wall / 0 retries; fable-a 20
subagent runs (~50–200k tokens each); adjudication 17 items. Zero human
annotation hours — which is exactly why every gold-dependent number
carries PROVISIONAL-ON-LLM-PROXY and why this cannot discharge ASM-1038's
human-annotation obligation, only stand in for it.

## 8. PROPOSED-ASM block ASM-1110…ASM-1119

Full text in `poc/codevert-g1/DESIGN-PIN.md` §6 (pinned pre-clone; listed
for the coordinator — NOT registered by this document): ASM-1110 FL-4
vertical definition + ambiguity resolution; ASM-1111 pool pin rule;
ASM-1112 census/extractor pins; ASM-1113 two-LLM-annotator proxy-gold
protocol + adjudication; ASM-1114 sample + cap + no-label gates; ASM-1115
element normalization; ASM-1116 endpoint definitions + quoted floors;
ASM-1117 spike scope; ASM-1118 spike metrics + probe guard; ASM-1119
session governance (no git/bd/kb; no handle strings; MEASURED +
PROVISIONAL-ON-LLM-PROXY tagging; verdict is the coordinator's).

## 9. Honest limits & auditability

1. **Proxy gold is not human gold.** Both annotators are LLMs; they share
   no model family (Claude vs GPT-5.6) but may share training-data blind
   spots; two context-discipline violations (one per annotator) were
   caught only because the OTHER annotator disagreed — colluding errors
   would pass silently. Agreement 0.915 bounds, not eliminates, that risk.
   The adjudicator is the same identity class as annotator-a (disclosed;
   rationales are logged per item for external re-adjudication).
2. **Freeze ordering** is filesystem-time-consistent only until the
   coordinator commits (no git op performed here — same caveat class as
   G0, now mitigated by the staged manifest but not discharged).
3. **Pool selection** is agent-memory, not sampled; bands are sensitivity
   bands. The 120 KB cap replacement rule (481 replacements) biases the
   ANNOTATED sample toward smaller modules; the κ headline is cap-free
   (full census) and unaffected.
4. **The srconly 0.982 slice covers FL-3 only** (where_defined not
   file-stratifiable — inherited G0 limitation, disclosed).
5. Nothing here is evidence about kernel CONTENT (ASM-1000), NL entry, or
   the excluded inverse families' product value.

## Epistemic register

[MEASURED]: every number in §2–§7 (exact counts in
poc/codevert-g1/results/*.json, poc/codevert-g1/annotation/*, and
poc/codevert-g1/pystat2-spike/results/*). [MEASURED +
PROVISIONAL-ON-LLM-PROXY]: all §4–§5 gold-dependent endpoints (precision,
R_q, neg-validity, agreement, adjudication). [STIPULATED]: ASM-1110…1119
(PROPOSED), the quoted ASM-1030 floors, ASM-1053/1056/1058 semantics as
inherited. [ESTIMATED]: the post-AnnAssign-fix precision projection (§5.1)
— the only forward-looking number, explicitly labelled. [EXTRAPOLATION]:
none used as premise. No verdict is issued; the coordinator's mechanical
step consumes §5's table and §6's verdict-input line.
