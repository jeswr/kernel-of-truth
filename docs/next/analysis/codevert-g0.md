# CODEVERT G0 readout — measured finding, STRONG EXPLORATORY cheap-kill signal

> **Status: [MEASURED READOUT of the authorized NON-SCORED G0 spike —
> STRONG EXPLORATORY CHEAP-KILL SIGNAL, not formal verdict evidence].**
> Calibration per the 2026-07-11 GPT-5.6 verification review
> (poc/gpt56-review/rev-g0-20260711/): the κ_q point estimate
> (independently recomputed) and the structural '*'-driven collapse
> (independently reconstructed; ablation reproduced exactly) are sound; the
> census freeze ordering, the soundness-probe "pass", and any "instrument
> validated" claim are NOT independently auditable and are downgraded below
> (see "Auditability caveats"). §7-G0 declares the spike non-scored
> (ASM-1050 likewise), so no κ here may serve as scored verdict evidence
> without an explicit protocol amendment. Author: Fable experiment agent,
> 2026-07-11 (auditability revision same date). Full detail:
> `poc/codevert-g0/RESULT.md`; artifacts content-hashed in
> `poc/codevert-g0/results/hashes.json`. This document registers nothing,
> edits no registry, performs no git/bd/kb operation. The repo pool is the
> agent-selected G0 pool [STIPULATED: ASM-1050], NOT the G1
> pinned-before-looking pool; per ASM-1039 no G0 number binds G1.

## The measured finding

Built per spec: PY-STAT/1 (ASM-1031 — enumerated inventory P1–P8,
candidate-name `unknown` propagation, UNKNOWN-INCOMPLETE, byte-span
provenance, SQLite twin) + the extractor-INDEPENDENT census (ASM-1030 —
raw-bytes syntactic generator, seed 20260711, hash-frozen; the
before-the-extractor freeze ordering is filesystem-time-consistent but NOT
git-auditable — see "Auditability caveats") on 6 pinned real repos
(six/toml/tabulate/bottle/more-itertools/click, exact SHAs pinned;
52,073 LOC, 133 analyzed modules; 16,722 census queries).

- **[MEASURED] κ_q^indep = 0.4361, repo-cluster bootstrap band
  [0.3610, 0.5364]** (family-macro 0.4286 [0.3712, 0.5168]). The bands are
  RESAMPLING SENSITIVITY BANDS over these six agent-selected clusters, NOT
  inferential generalization CIs (selection bias is not repaired by
  bootstrapping at n=6). Package-source slice 0.4537 [0.3986, 0.4912] —
  band entirely below the floor, but it covers SEVEN families / 4,878
  queries only (where-defined cannot be file-stratified and is dropped),
  so it is not a full-8-family-distribution slice. **Below the G1 kill
  floor (≥ 0.5, ASM-1030) at point estimate on both slices.**
- **[MEASURED] the collapse is structural**: lexical families 1.00; forward
  0.23–0.65 (family-macro 0.7198; query-pooled 0.6662 = 5,888/8,838);
  inverse/exhaustive callers-of 0/3,783 and instance-of 0/503 on ALL six
  repos — every repo carries 22–869 unrestricted (`*`) unknown call edges
  (parametrized decorators, local-value calls, call-result calls), and one
  suffices to zero every repo-wide completeness precondition. Ablation with
  `*` mass excluded: callers-of 0.54–0.92 — the candidate-name mechanism
  works; the `*` mass is the whole kill. Scope: a structural property of
  PY-STAT/1 + §2.2 on these six repositories, not a proven fact about all
  real Python.
- **[MEASURED] soundness/validity probe** (all 6 test suites traced, no
  annotation): 0 observed contradictions of 1,415 dynamically-exercised
  proved facts. **The registered dynamic soundness endpoint did NOT pass**:
  the checker classifies 104 call records + 1 import record as strict
  misses (1.8% of 5,718 scored edges; 89 unmatched generator resumptions
  and 617 unmapped callees excluded from scoring), and the
  previously-quoted "0/5,718 completeness violations" is a weaker,
  near-vacuous predicate (it passes whenever the corresponding inverse
  query is already `unknown`). One real validity bug (parent-package import
  closure) was probe-caught and fixed, but no before-fix artifact was
  preserved: the fix-once sequence is asserted, not auditable. Detail:
  RESULT.md §3.
- **[MEASURED] resources (pinned 2-vCPU rig)**: 52k LOC / 133 modules
  extracted in 2.907 s (0.094–1.067 s/repo); peak RSS 82 MB; packed store
  6.05 MB = 213 B/edge; reference-engine query p95 3–11 µs/family. The
  ASM-0946 ceilings are not threatened by the symbolic side at this repo
  band.
- **NOT measured** (honestly): precision and R_q against adjudicated human
  gold — that is G1's annotation spend (ASM-1038); G0 spent zero annotation
  hours and ~$0 compute.

## Auditability caveats (per the GPT-5.6 verification review — what is NOT
## established)

1. **Anti-circularity: credible, NOT proven.** census.py has no extractor
   dependency and builds targets from repository syntax alone; the saved
   generator/census hashes match the freeze manifest; filesystem mtimes are
   consistent with the claimed sequence (census + manifest ~17:50,
   inventory 17:53, engine 17:58, extractor later). But everything was
   untracked at freeze time: hashes prove content identity, not temporal
   ordering, and there is no pre-extractor git object, append-only event,
   or signed timestamp. "Frozen before any extractor code existed" is
   filesystem-time-consistent, not git-auditable.
2. **Census-universe mismatch [DISCLOSED LIMITATION].** census.py's
   docstring says it enumerates attribute-access names and import-statement
   targets, but the ACTUAL query universes use only function/class
   definitions, module files, and definition/assignment names
   (attribute-access and import targets are collected as collision
   diagnostics only). Consistent with the ASM-1053 narrowing, narrower than
   ASM-1030's literal description; the operationalization must be
   explicitly accepted before the 16,722-query denominator is canonical.
3. **The soundness probe did not pass the registered endpoint.** 104 call +
   1 import checker-classified misses stand; the advertised 0/5,718 was a
   weaker predicate (RESULT.md §3). Any domain exclusions must be pinned
   BEFORE a rerun.
4. **The fix-once path is asserted, not evidenced.** No before-fix checker
   output, diff, or violation artifact was preserved; current artifacts
   prove only the final (clean) state.
5. **Governance.** §7-G0 defines the spike as non-scored with no κ quoted
   as a spike result; using these numbers as scored verdict evidence
   requires an explicit protocol amendment.

## Reading (exploratory signal, not verdict evidence)

Does Python extraction clear the G1 κ_q floor (≥ 0.5)? **On this pool, no —
0.4361 at point, with the seven-family package-source sensitivity band
entirely below the floor.** If the pinned G1 pool behaves like this one,
the G1 kill fires on κ_q^indep under the registered full-8-family
semantics (a logically-correct conditional, not a verdict). EXTRAPOLATION
ASM-1008 is now bounded by fact: Python IS friendlier than the measured
walls (0.44 ≫ g8 0/1000) and the instrument is buildable at ~$0 — though
NOT yet validated (see caveats above) — but the full-distribution 8-family
product claim does not clear its own floor on these repos. A defensible
re-scoped G1 universe exists and is a DESIGN choice, not a G0 output:
(a) the forward/lexical family subset (family-macro κ 0.7198, query-pooled
0.6662),
(b) UNKNOWN-INCOMPLETE partial answers as first-class product output, or
(c) PY-STAT/2 with bounded local dataflow (measured ablation headroom:
callers-of 0.54–0.92) — an extractor version change requiring a new spike.
Cheapest-first ordering held: this fact cost zero annotation dollars and
precedes all task authoring and model work, exactly as ASM-1004/1030
intended.

## PROPOSED-ASM (block ASM-1050–1059, disjoint; listed for the coordinator —
## NOT registered by this document)

| id | scope |
|---|---|
| ASM-1050 | G0 repo pool: 6 agent-selected small permissive repos, SHAs pinned in poc/codevert-g0/repos.lock.json; non-scored spike only; G1 pool remains pinned-before-looking |
| ASM-1051 | Analyzed scope = all *.py incl. tests (fail-closed); package-source-only co-reported as a pinned-path-rule sensitivity slice |
| ASM-1052 | Census generator may use ast.parse as a purely syntactic enumerator (no symtable/resolution); satisfies ASM-1030's raw-bytes/syntactic requirement |
| ASM-1053 | contains/contained-in are LEXICAL relations (AST-only, proved for parsed modules); binding SITES are syntactic (conditional nesting does not void a site); where-defined domain = def/class at any nesting + module/class-level assigns; import bindings and function-local assigns excluded |
| ASM-1054 | P8 devirtualization: single-inheritance MRO over fully-analyzed hazard-free chains, VOIDED on any repo-internal subclass override; out-of-repo subclassing is a disclosed residual |
| ASM-1055 | exec/eval/compile in a module ⇒ one unrestricted unknown edge per non-lexical relation, module-scoped (H4-analog) |
| ASM-1056 | Candidate discipline: an unknown edge's candidate set is restricted to a name ONLY when the runtime callee's def-name is provably preserved (attribute lookups, star-import bare names, non-aliased from-imports, literal getattr); local-value calls, aliased/assign-bound names, decorated targets, call-result calls ⇒ '*' |
| ASM-1057 | Value-escape edges: Load references to repo-resolvable defs outside call position emit unknown call edges (candidate = resolved def name); unresolvable Load references are counted (tier-b spec gap) not edged; implicit protocol/descriptor dispatch is outside the call relation's domain and classified separately in the probe |
| ASM-1058 | Pinned resolver models deployed sys.path: roots = repo root, src/, plus non-package .py directories; import edges close over parent packages (import a.b.c ⇒ imports a, a.b, incl. self-edges) — the probe-detected validity fix |
| ASM-1059 | G0 gold proxies are machine-only: dynamic-trace probe (soundness, query-level completeness, negative-answer validity) stands in for the adjudicated R_q/precision/negative-validity endpoints, which remain G1 annotation work |

## Epistemic register

[MEASURED] the counts, κ values, ablation, resource numbers, and probe
tallies in "The measured finding" (exact counts/denominators in
poc/codevert-g0/results/*.json). NOT [MEASURED]: the census freeze
ORDERING (filesystem-time-consistent only — see Auditability caveats 1)
and the fix-once SEQUENCE (final state only — caveat 4); neither carries a
[MEASURED] tag. [STIPULATED] ASM-1030/1031 as built; ASM-1050–1059
proposed operationalizations, including the narrower-than-docstring census
universe (caveat 2). [ESTIMATED] nothing here — no cost projections made.
[EXTRAPOLATION] none used as premise; the only forward-looking sentences
("if the pinned G1 pool behaves like this pool"; extending the structural
collapse beyond these six repos) are explicitly conditional/labelled.
Overall epistemic weight: STRONG EXPLORATORY cheap-kill signal, not formal
verdict evidence. Nothing here is evidence about kernel CONTENT (ASM-1000)
or NL entry.
