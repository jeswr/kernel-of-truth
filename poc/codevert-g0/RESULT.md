# CODEVERT G0 — NON-SCORED extractor spike + extractor-independent census: MEASURED results

> **Status: G0 spike readout — STRONG EXPLORATORY CHEAP-KILL SIGNAL, NOT
> formal verdict evidence.** This is the NON-SCORED engineering spike
> authorized by the 2026-07-11 GPT-5.6 review-gate ruling (CODEVERT.md rev 2
> header + §7-G0). Calibration, per the 2026-07-11 GPT-5.6 verification
> review (poc/gpt56-review/rev-g0-20260711/): the κ_q point estimate
> (0.4361, independently recomputed from the saved counts) and the
> structural '*'-driven inverse-family collapse (independently
> reconstructed; ablation reproduced exactly) are sound. But the census
> freeze ordering, the soundness-probe "pass", and any "instrument
> validated" claim are NOT independently auditable from the preserved
> artifacts (see §0.3 and §3) and are withdrawn or downgraded below.
> Additionally, §7-G0 declares this spike non-scored and ASM-1050 records it
> as such: no κ number here may be used as scored verdict evidence unless
> the protocol is explicitly amended. Per ASM-1039, no number here is a
> registered G1 verdict; the pool is NOT the G1 pinned-before-looking pool
> [ASM-1050]; the coordinator's mechanical step + Fable interpretation
> produce any verdict. Author: Fable experiment agent, 2026-07-11
> (auditability revision same date). No git/bd/kb operation performed;
> registry untouched.
>
> Tags: [MEASURED] = computed here on the pinned inputs; [STIPULATED] =
> method choice (registered ASM or PROPOSED-ASM ASM-1050..1059 listed in
> docs/next/analysis/codevert-g0.md); [ESTIMATED] = no measurement.

## 0. What was built (deliverables, content-hashed in results/hashes.json)

1. **PY-STAT/1 extractor** (`extractor.py`, sha `b508d844…`) per ASM-1031:
   ast+symtable only, pinned import resolver, enumerated proved inventory
   P1–P8 (`inventory.json`, sha `aebfe0a0…`), everything else fail-closed
   `unknown` with candidate-name sets ('*' = unrestricted), 4-state schema
   (disproved/conflict = 0 emission sites in v0, reported honestly), byte-span
   provenance, SQLite packed store.
2. **Query engine** (`engine.py`) — all 8 kot-query-code/1 families with the
   §2.2 completeness precondition and
   `UNKNOWN-INCOMPLETE(partial_lower_bound, blocking_count)`; proved-EMPTY
   negatives require the same precondition; census targets the extractor
   cannot locate count NOT-proved (anti-circularity).
3. **Extractor-INDEPENDENT census generator** (`census.py`, sha `2922ac79…`)
   per ASM-1030: raw repo bytes only, purely syntactic, seed 20260711,
   hash-frozen (results/freeze-manifest.json, census sha `a53f0554…`).
   16,722 census queries, 8 families × 6 repos.
   **Freeze-ordering caveat [DISCLOSED]**: the manifest asserts the census
   was frozen before any extractor code existed, and filesystem mtimes are
   consistent with that sequence (census + manifest ~17:50, inventory
   17:53, engine 17:58, extractor later) — but every artifact was untracked
   at freeze time. Hashes prove content identity, not temporal ordering;
   there is no pre-extractor git object, append-only event, or signed
   timestamp. The freeze-ordering claim is filesystem-time-CONSISTENT, not
   git-AUDITABLE. Anti-circularity is therefore structurally credible
   (census.py has no extractor dependency and constructs targets from
   repository syntax alone) but NOT proven.
   **Census-universe caveat [DISCLOSED]**: census.py's docstring describes
   enumerating attribute-access names and import-statement targets, but the
   ACTUAL query universes are built only from function/class definitions,
   module files, and definition/assignment names (attribute-access and
   import-target data are collected as collision DIAGNOSTICS only). This
   operationalization is consistent with the ASM-1053 narrowing but
   narrower than ASM-1030's literal description; it must be explicitly
   accepted before the 16,722-query denominator is treated as canonical.
4. **Dynamic trace probe** (`probe_runner.py` + `probe_check.py`) — the G1
   soundness-probe shape run as a mechanical mini: each repo's own test suite
   under sys.setprofile + an `__import__` wrapper; observed intra-repo
   call/import edges checked against proved ∪ unknown-compatible.
   **Corrected characterization [DISCLOSED]**: the implemented
   completeness check is WEAKER than the registered endpoint — it passes an
   observation whenever the corresponding inverse query
   (callers-of/instance-of) is already `unknown`, and does not test
   completeness of proved callees-of answers; see §3.
5. **Pinned corpus** (`repos.lock.json`): six, toml, python-tabulate, bottle,
   more-itertools, click — exact SHAs recorded; 133 analyzed modules
   (an earlier draft said 129 — the saved per-repo counts sum to 133),
   52,073 LOC
   total; MIT/BSD; tests INCLUDED in analyzed scope (fail-closed), with a
   package-source-only sensitivity slice co-reported [ASM-1051].

## 1. Headline: κ_q^indep vs the G1 floor (≥ 0.5, CODEVERT §7-G1)

[MEASURED, full frozen census, population values on this pool; the
repo-cluster bootstrap interval (n=6 clusters, 10k resamples, seed-pinned)
is a RESAMPLING SENSITIVITY BAND across these six clusters, NOT an
inferential generalization CI: the six repos were agent-selected, not
sampled from a defined population, and cluster bootstrapping cannot repair
selection bias at n=6]

| slice | κ_q^indep (query-pooled) | 95% band | family-macro | 95% band |
|---|---|---|---|---|
| full repo (tests incl.) | **0.4361** | [0.3610, 0.5364] | 0.4286 | [0.3712, 0.5168] |
| package-source only | 0.4537 | [0.3986, 0.4912] | 0.4104 | [0.3740, 0.4758] |

**The point estimate is BELOW the 0.5 planning floor on both slices.** The
package-source band lies entirely below the floor and the full-repo band
straddles it — but these are sensitivity bands, not generalization CIs
(above). **Package-source scope caveat [DISCLOSED]**: the source-only run
DROPS the entire where-defined family (run_g0.py cannot file-stratify
name-level queries), so 0.4537 and its band cover SEVEN families and 4,878
queries, not the registered full-8-family universe; any reading of that
band as a below-floor FULL-distribution sensitivity slice is withdrawn.
n=6 agent-selected repos is the honest cluster count; no narrower claim is
licensed.

Per family (full-repo, pooled over 16,722 queries) [MEASURED]:

| family | κ | n | note |
|---|---|---|---|
| contains | 1.0000 | 636 | lexical relation [ASM-1053] |
| contained-in | 1.0000 | 4,286 | lexical |
| imports-of | 0.6466 | 133 | conditional/lazy imports block the rest |
| where-defined | 0.3994 | 3,465 | bimodal 0/1 per repo: any setattr/exec/dynamic-ns hazard zeroes the repo |
| callees-of | 0.2326 | 3,783 | most functions contain ≥1 unresolved call |
| imported-by | 0.1504 | 133 | inverse; killed by conditional-import + dynamic-import unknowns |
| callers-of | **0.0000** | 3,783 | inverse; every repo has ≥1 unrestricted call unknown |
| instance-of | **0.0000** | 503 | inverse; quantifies over unknown call edges too |
| forward 4, family macro-average | 0.7198 | 8,838 | query-pooled κ = 5,888/8,838 = 0.6662 (an earlier draft mislabelled the macro as "pooled") |
| inverse/exhaustive 4, family macro-average | 0.1374 | 7,884 | query-pooled κ = 0.1781 (earlier-draft "0.1412 pooled" was a transcription + labelling error) |

384 callees-of, 17 imported-by, 5 imports-of and 84 contains queries were
answered **proved-EMPTY** (valid negatives under the precondition) — counted
as proved; zero silent empty answers [MEASURED].

## 2. Root-cause decomposition (what kills the inverse families)

[MEASURED] 28,370 edges: 17,490 proved / 10,880 unknown (38.4%) / 0 disproved
/ 0 conflict. Unknown mass by construct family (pooled):
CALL_ATTR_RECEIVER_UNTYPED 3,902; CALL_MRO_UNRESOLVED 2,270;
CALL_ATTR_MODULE_MEMBER_UNRESOLVED 1,436; CALL_MODULE_BINDING_UNRESOLVED
1,076; CALL_NONNAME_CALLEE 902 (incl. every parametrized-decorator
result-application); CALL_LOCAL_VALUE 473; CALL_VALUE_ESCAPE 338;
IMPORT_CONDITIONAL 321; MRO_HAZARD 117; setattr/exec/star/dynamic ≤ 20 each.

**Unrestricted ('*') unknowns: call 1,682, binding 20, import 8,
instantiate 3.** Under the §2.2 repo-wide completeness precondition, a single
unrestricted call unknown zeroes callers-of AND instance-of for the whole
repo; all six repos have 22–869 of them.

**Ablation** (mechanical counterfactual: '*' excluded from preconditions,
restricted candidates kept — results/g0-ablation-unrestricted.json)
[MEASURED]: callers-of 0.54–0.92 per repo, imported-by 0.63–0.97,
where-defined 1.0, instance-of 0.32–0.91. **The entire inverse-family
collapse is attributable to the unrestricted-unknown mass, not to the
candidate-name mechanism.** Caveat: a SOUND version of this counterfactual
requires deriving candidates for local-value calls and decorator
result-applications, which is impossible without dataflow tracking outside
the PY-STAT/1 inventory — so this is G1-design headroom, not achievable κ.

**Candidate-set growth / identifier collisions** [MEASURED]: 1,191 distinct
restricted unknown-call candidates; 60.3% name ≥1 same-named repo def; 9.3%
name ≥2 (ambiguity pressure); max 56 same-named defs (`__init__`, click);
top colliders `__init__`, `run`, `test`, `convert` — the arch-critique §4.4
common-name concern now has numbers.

**Tier-b spec gap (counted, not edged)** [MEASURED]: 4,470 attribute-Load and
23,581 name-Load references whose values PY-STAT/1 does not track. A strict
value-escape closure over these (required for per-callsite soundness of any
RELAXED precondition) would push candidate mass toward unrestricted repo-wide
— it binds any attempt to soften §2.2 [ASM-1057].

## 3. Soundness / validity probe (mechanical; NO annotation spent)

All six repos' own test suites ran under the tracer (2,556 tests; 3
pre-existing repo test failures, disclosed; pytest 8.4.2, CPython 3.9.25).
7,232 observed intra-repo call edges, of which 5,718 non-generator edges
scored; 89 unmatched generator resumptions and 617 unmapped callees were
EXCLUDED from scoring [MEASURED]:

- **Headline correction — the registered dynamic soundness endpoint did NOT
  pass.** ASM-1030's endpoint requires every observed edge to appear in
  proved ∪ compatible-unknown; under that predicate the checker itself
  classifies **104 non-generator call records + 1 intra-repo import record
  as `miss`**. The previously advertised "query-level completeness
  violations 0/5,718" is a DIFFERENT, substantially weaker predicate:
  probe_check.py passes an observation whenever the corresponding inverse
  query (callers-of/instance-of) is already `unknown` — under this corpus's
  unrestricted '*' edges that check is close to vacuous, and it does not
  test completeness of proved callees-of answers. The prior statement that
  "the live checks are imported-by and the forward families" was incorrect
  and is withdrawn. Some of the 104 misses may warrant legitimate domain
  exclusions (implicit protocol/descriptor dispatch, subclass-`__init__`
  attribution, doctest dynamic import), but per §7-G1 discipline those
  exclusions must be PINNED BEFORE any rerun, not reclassified narratively
  afterward.
- What DID hold [MEASURED]: **0 observed contradictions of 1,415
  dynamically-exercised proved facts**, and the weaker
  inverse-query-compatibility predicate scored 0/5,718 (near-vacuity
  disclosed above).
- Strict per-callsite: 1,157 confirmed proved-call + 258 confirmed
  instantiation + 4,043 unknown-compatible + 352 implicit protocol dispatch
  (dunder operators/descriptors — no syntactic call site exists; outside the
  call relation's domain as spec'd, classified not hidden) + 109
  property/decorated-descriptor invocations + **104 residual strict misses
  (1.8%)** in named classes: subclass-`__init__` attribution, `property()`
  -by-assignment setters, star-module attribute dispatch, metaclass
  `__new__`, one doctest-driven dynamic import.
- Imports: 290 confirmed, 16 unknown-compatible, 1 miss (doctest dynamic
  import by external code — outside the enumerated inventory, disclosed).
- Proved facts contradicted by observation: **0**.
- **Parent-package import-closure fix — legitimate, but the fix-once
  SEQUENCE is not evidenced**: the probe caught a negative-answer validity
  violation (imported-by listing missing an observed importer) whose root
  cause was missing parent-package import closure (`import a.b.c` also
  imports `a` and `a.b` — correct Python import semantics, self-edges
  included). The fix is in the current code and the current artifacts are
  clean on that check. However, NO before-fix checker output, diff, or
  initial violation artifact was preserved: the previously claimed
  "found → fixed → re-run once → clean" §7-G1 fix-once path is asserted,
  not auditable — the artifacts prove only the final state. The same
  holds for the two other probe-caught fixes (except-handler bodies not
  walked in pass 1; pytest sys.path sibling-import resolver scope)
  [ASM-1058].

**Precision vs adjudicated gold: NOT MEASURED** — that is G1's annotation
spend (ASM-1038); G0 offers only the mechanical stand-ins above (dynamic
confirmation of 1,415 proved facts, zero contradictions) [ASM-1059].
**R_q vs adjudicated gold: NOT MEASURED** — same reason. Zeros and
denominators above are exact counts, not estimates.

## 4. Resource facts (pinned rig: 2 shared vCPU EC2, nice -n 10, CPython 3.9.25)

[MEASURED]
- Extraction: 52,073 LOC / 133 modules in **2.907 s total** (0.094–1.067
  s/repo; click alone 1.067 s). An earlier draft reported 2.83 s / 129
  modules / 0.09–0.89 s per repo; the saved per-repo metrics sum to the
  corrected values.
- Peak RSS (extract + index + full 16,722-query census): **82.2 MB**.
- Packed SQLite store: **6.05 MB total, 213.4 B/edge** (28,370 edges,
  proved + unknown + provenance spans + indexes; 0.12–1.9 MB/repo).
- Query latency, THIS Python dict-index reference engine (not the measured
  5.29–7.82 µs compiled a5 engine; comparable only to itself): p50 1.4–4.5 µs,
  p95 3.0–11.4 µs per family, max 0.17 ms. Even a pure-Python engine sits
  ~3 orders of magnitude under the 500 ms Tier-1 p95 ceiling; the ceilings
  ASM-0946 pins are not at risk from the symbolic side on repos in this band.
- Compute cost of the whole spike: ~$0 (shared box); zero GPU-h; zero
  annotation hours.

## 5. Reading: STRONG EXPLORATORY cheap-kill signal (NOT formal verdict evidence)

Governance note: CODEVERT §7-G0 declares this spike non-scored and no κ
number is quoted as a spike result; ASM-1050 records the same. Treating any
number below as scored verdict evidence would conflict with that governance
unless the protocol is explicitly amended. What follows is exploratory
signal for design and planning.

1. **κ_q^indep = 0.4361 (macro 0.4286), sensitivity band [0.3610, 0.5364] —
   below the G1 0.5 floor at point estimate on this pool; the
   package-source slice (SEVEN families, 4,878 queries — where-defined
   dropped, §1) sits at 0.4537 with its band [0.3986, 0.4912] entirely
   below the floor.** The bands are resampling sensitivity bands over six
   agent-selected clusters, not generalization CIs (§1). The conditional
   remains logically correct: IF the pinned G1 pool behaves like this pool,
   the G1 kill fires on κ_q^indep. ASM-1008's "Python is a friendlier
   extraction domain" is now bounded: friendlier than the measured walls
   (0.44 ≫ g8's 0/1000; comparable to m0b's 0.3542 in magnitude, different
   metric), but NOT floor-clearing under the registered full-8-family
   semantics on this pool.
2. **The failure is structural and family-specific, not noise**: lexical
   families 1.00, forward families 0.23–0.65, inverse/exhaustive families
   0.00–0.40. The §2.2 repo-wide completeness precondition + unrestricted
   unknowns (parametrized decorators, local-value calls, call-result
   calls — 22–869 per repo) make callers-of 0/3,783 and instance-of 0/503
   (jointly 0/4,286) on all six repos. No amount of annotation changes
   this; it is a structural property of PY-STAT/1 + §2.2 ON THESE SIX
   REPOSITORIES — extending "inevitable on real Python" beyond them is
   [EXTRAPOLATION], not licensed by G0 (though the generating constructs
   are commonplace Python).
3. **The defensible G1 universe, if the direction proceeds**: (a) the
   lexical/forward subset (contains, contained-in, imports-of, callees-of,
   where-defined-on-hazard-free-repos) — family-macro κ 0.7198
   (query-pooled 0.6662) on the 4 forward families; or (b) a re-scoped
   product answer where UNKNOWN-INCOMPLETE (partial lower bound + blocking
   count) is a first-class deliverable rather than a κ-failure — every
   blocked query here still returns its partial listing; or (c) a PY-STAT/2
   with bounded local dataflow to convert the '*' mass to candidates
   (ablation headroom: callers-of 0.54–0.92) — an extractor version change,
   new inventory, new spike. Choosing among these is a DESIGN decision
   (coordinator/Fable), not a G0 output.
4. **Instrument status — buildable, NOT validated**: the
   extractor-independent census + fail-closed semantics + mechanical
   dynamic probe were all built and exercised at ~$0 compute, and the
   census design cannot be satisfied by conditioning on extraction (κ
   counts every syntactic target). But three earlier validation claims are
   withdrawn as not audit-clean: (a) the census freeze ordering is
   filesystem-time-consistent, not git-auditable (§0.3); (b) the registered
   dynamic soundness endpoint did NOT pass — 104 call + 1 import
   checker-classified misses remain, and the advertised 0/5,718 was a
   weaker, near-vacuous predicate (§3); (c) the fix-once path's before-fix
   state was not preserved, so "found → fixed → re-run once → clean" is
   asserted, not evidenced (§3). "Instrument buildable and sound" is an
   overclaim. G1 instrument validation requires durable freeze evidence
   (pre-extractor git object / append-only event / signed timestamp),
   pre-pinned probe domain exclusions, and preserved before/after fix
   artifacts.
5. **What G0 does NOT license**: any statement about precision or R_q against
   human gold (unmeasured); any statement about the pinned G1 pool (different
   repos); any product-utility statement (UNKNOWN-INCOMPLETE utility is a
   G2/G4 question); any NL-entry statement (out of scope entirely); any
   "instrument validated" or "soundness probe passed" statement (§3, §5.4);
   any use of these κ values as scored verdict evidence absent an explicit
   §7-G0 protocol amendment.

## 6. Repro

```bash
cd poc/codevert-g0
# corpus is pinned by repos.lock.json (clone at the recorded SHAs)
python3 census.py                 # frozen census (seed 20260711)
nice -n 10 python3 run_g0.py      # extraction + kappa + resources
G0_EXCLUDE_TESTS=1 python3 run_g0.py   # package-source sensitivity slice
# dynamic probe (venv with pytest 8.4.2):
venv/bin/python probe_runner.py corpus/<repo> <testdir> results/probe/<repo>.trace.json
python3 probe_check.py <repo> results/probe/<repo>.trace.json results/probe/<repo>.check.json
```
All artifact hashes: results/hashes.json. Result JSONs: results/g0-metrics.json,
results/g0-metrics-srconly.json, results/g0-ablation-unrestricted.json,
results/probe/*.check.json.
