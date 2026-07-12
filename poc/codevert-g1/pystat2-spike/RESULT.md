# PY-STAT/2-SPIKE — bounded local dataflow on the '*' mass: MEASURED results

> **Status: NON-SCORED engineering spike (CODEVERT issue #16, option C).**
> No κ number here is verdict evidence. The pool is the G0 six-repo pool,
> NOT the G1 pinned-before-looking pool. Promoting PY-STAT/2 would be an
> extractor VERSION CHANGE per ASM-1031: new content-hashed inventory, new
> census discipline, full G1 rerun — none of that is done here. The G0
> census (poc/codevert-g0/results/census.json), corpus, engine and saved
> probe traces were consumed READ-ONLY; nothing under poc/codevert-g0/ was
> modified. Author: Fable experiment agent, 2026-07-11. No git/bd/kb
> operation performed.
>
> Tags: [MEASURED] = computed here on the pinned inputs (results/
> spike-metrics.json, results/*.probe-recheck.json); [SPIKE-STIPULATED] =
> scope/method choice pinned for this spike only.

## 0. What was built

`extractor2.py` (label PY-STAT/2-SPIKE) — a COPY of the G0 PY-STAT/1
extractor extended with bounded local dataflow whose SOLE aim is converting
unrestricted '*' unknown call edges into finite NAMED candidate sets.
Fail-closed: anything the bounded analysis cannot prove stays '*'. NO
unknown edge is upgraded to proved (candidates-only; status upgrades would
need a soundness re-validation, out of scope). Converted sites emit ONE
unknown edge PER candidate name, so the unknown edge COUNT changes (28,370
to 28,391 edges pooled [MEASURED]); engine.py counts per-candidate, which is
exactly the intended blocking semantics.

Pinned mechanisms [SPIKE-STIPULATED]:

- **D1 local-alias tracking** (function scope, intraprocedural): a call of a
  local name x() converts when EVERY binding of x in that exact function
  scope is provable — single-Name assignment from a Name/Attribute that the
  EXISTING machinery (resolve_global_name / resolve_member / mro_lookup)
  resolves to a repo function/class; a nested def with allowlisted-only
  decorators (name-preserving); a nested undecorated class; or a for-loop
  over a literal tuple/list of resolvable references. Parameters NEVER
  qualify; free variables, walrus, tuple targets, AugAssign, with-as,
  except-as, local imports, del, comprehension targets, and nonlocal
  rebinding from any nested scope all poison the name to '*'. Class-valued
  candidates expand to the analyzed ancestor-chain simple names (an
  inherited `__init__` runs in an ancestor frame); on chain hazard the
  simple name alone is kept — the same restricted-candidate discipline
  PY-STAT/1 already applies at its CALL_MRO_HAZARD sites.
- **D2 parametrized-decorator result application** (`d(args)`-applied
  decorator on def f): if d resolves to a repo function def, one-level
  return analysis of d's body — every `return` must be a Name that is (a) a
  nested def in d's body (allowlisted-only decorators, not rebound) or (b)
  one of d's own parameters (the `return func` wraps pattern) — candidates =
  {nested-def names} plus {f's name} if case (b) occurs. Sub-rule
  [SPIKE-STIPULATED]: if d resolves to an allowlisted EXTERNAL decorator
  factory (e.g. the `from functools import wraps` spelling the syntactic
  ALLOWLIST check misses), candidates = {f's name} — same identity-preserving
  stipulation the base ALLOWLIST already encodes. No recursion into calls.
- **D3 call-result calls** `g(...)(...)`: same return analysis on g; case
  (b) maps the returned parameter to the actual argument at THIS call site
  (positional/keyword, fail-closed on starred/double-star/defaults; plain
  Name callees only, to avoid bound-method argument shift).
- **D4**: every other '*' source (CALL_MODULE_BINDING_UNRESOLVED,
  CALL_GETATTR, TAINT_EXEC, unconverted D1–D3 sites, non-call '*') stays
  '*' unchanged.

Guard [MEASURED]: the runner HARD-ASSERTS the PY-STAT/2-SPIKE proved-edge
set is IDENTICAL to PY-STAT/1 on every repo (sorted full-row comparison).
The assertion PASSED on all 6 repos; κ differences, had there been any,
could only come from unknown-edge candidate narrowing.

## 1. Headline: '*' conversion vs κ recovery [MEASURED]

**'*' unknown call/instantiate mass: 1,685 → 1,305 pooled (22.55%
converted).** Per mechanism (sites / candidate edges): D1 137/158, D2
243/243 (of which 1 via the allowlisted-ext sub-rule), D3 0/0. Against
their own target masses: D1 converted 29.0% of the 473 CALL_LOCAL_VALUE
'*'; D2+D3 converted 26.9% of the 902 CALL_NONNAME_CALLEE '*'. D3 found
zero convertible `g(...)(...)` sites on this corpus.

**κ_q^indep over the frozen census: BIT-IDENTICAL to PY-STAT/1 on all 8
families × 6 repos.** Pooled query-pooled κ 0.4361 → 0.4361; family-macro
0.4286 → 0.4286; callers_of 0.0000 → 0.0000 (0/3,783), instance_of 0.0000 →
0.0000 (0/503), imported_by 0.1504 → 0.1504, where_defined 0.3994 → 0.3994.
(The v1 side independently reproduces the G0 published numbers exactly —
replication fidelity check passed.)

Per repo, the four inverse/exhaustive families (v1 = v2 everywhere, so one
column per family):

| repo | callers_of | instance_of | imported_by | where_defined | '*' v1→v2 (% conv) |
|---|---|---|---|---|---|
| bottle | 0.0 | 0.0 | 0.0 | 0.0 | 356→319 (10.4%) |
| click | 0.0 | 0.0 | 0.0 | 0.0 | 869→590 (32.1%) |
| more-itertools | 0.0 | 0.0 | 0.625 | 1.0 | 125→103 (17.6%) |
| python-tabulate | 0.0 | 0.0 | 0.900 | 1.0 | 226→217 (4.0%) |
| six | 0.0 | 0.0 | 0.0 | 0.0 | 87→56 (35.6%) |
| toml | 0.0 | 0.0 | 0.667 | 1.0 | 22→20 (9.1%) |

**Ablation-headroom recovery: 0.0000 of the callers_of 0.54–0.92 (and
instance_of 0.32–0.91) counterfactual ceiling, on every repo.**
imported_by and where_defined are structurally untouched (D1–D3 convert
only call-relation '*'; the import/binding '*' mass — 8 and 20 edges — is
out of the pinned scope by construction).

**Why zero**: the §2.2 completeness precondition is all-or-nothing — a
single surviving '*' call unknown zeroes callers_of and instance_of
repo-wide. Residual '*' after conversion: bottle 319, click 590,
more-itertools 103, python-tabulate 217, six 56, toml 20. Even a PERFECT
D1–D3 (100% of CALL_LOCAL_VALUE + CALL_NONNAME_CALLEE) would leave every
repo ≥ 11 '*' edges from sources D1–D3 cannot touch: module-binding
aliasing (CALL_MODULE_BINDING_UNRESOLVED '*': 8–180 per repo, worst
python-tabulate 180), CALL_GETATTR '*' (six 6, bottle 1), TAINT_EXEC
(six 2, bottle 4). Untargeted residual per repo: bottle 52, click 35,
more-itertools 11, python-tabulate 180, six 16, toml 16 [MEASURED].

**What the conversion DOES buy [MEASURED]**: blocking mass. Mean
blocking_unknown_count per callers_of query fell 438.9 → 329.4 pooled
(−24.9%); instance_of 335.7 → 254.7 (−24.1%); click callers_of 876.0 →
598.6. Under a per-candidate/partial-answer product semantics (G0 reading
§5.3b) that is a real answer-quality gain; under the registered §2.2 κ it
is worth exactly nothing.

## 2. Soundness guard: probe re-check on the saved traces [MEASURED]

Re-ran the G0 probe_check classification against the EXISTING saved traces
(poc/codevert-g0/results/probe/*.trace.json — no test suite was re-executed)
for BOTH extractors in one pass; outputs in results/*.probe-recheck.json.

- **(a) Contradictions of proved facts: 0.** Proved sets are asserted
  identical; query-level proved-answer validity violations 0 under v1 AND 0
  under v2 (callers_of/instance_of/imported_by remain non-proved throughout,
  so narrowing never produced a false-complete proved answer). Import-edge
  behavior byte-identical (import misses v1=v2 per repo: 0,0,1,0,0,0).
- **(b) NEW candidate-compatibility misses (observed truth EXCLUDED by
  narrowing): 4 total = 2 non-generator + 2 generator resumptions.**
  Strict per-callsite misses 104 → 106 non-generator. The two non-generator
  exclusions (both six, both previously masked by a '*' that D1 converted):
  1. test_six.py::test_print_ → test_six.py::test_print_.FlushableStringIO.flush
     — a flush() invoked through the C builtin print (no syntactic call
     site in the caller frame; C frames are invisible to the tracer).
  2. test_six.py::test_with_metaclass_pep_560 → six.py::with_metaclass.metaclass.\_\_new\_\_
     — metaclass \_\_new\_\_ invoked implicitly by a class statement; already
     one of the known G0 §3 miss families (metaclass \_\_new\_\_).
  Both are implicit-dispatch edges with NO syntactic call site — exactly
  the family the G0 §3 correction flagged; under PY-STAT/1 they were not
  "handled", they were VACUOUSLY absorbed by unrestricted '*' mass at those
  callsites. The 2 generator-resumption exclusions (more-itertools) are the
  same phenomenon on resumption frames. Additionally 6 observed dunder
  edges moved unknown_compatible → protocol_dispatch (domain-excluded per
  the existing spec reading, disclosed, not counted as misses).
- Honest reading: candidate narrowing surfaces real implicit-dispatch
  incompleteness that '*' was hiding. A full PY-STAT/2 build would have to
  PIN these domain exclusions (C-mediated callbacks, metaclass \_\_new\_\_,
  descriptor/protocol dispatch) BEFORE its G1 probe, or accept them as
  candidate-soundness misses. 4 exclusions on 7,232 observed edges is small
  but NOT zero — the candidate-name discipline (ASM-1056) is not fully
  sound under narrowing on this corpus.

## 3. Resource facts [MEASURED]

Pinned rig: 2 shared vCPU EC2, nice -n 10, CPython 3.9.25.
- Full spike run (both extractors on 6 repos, 2 × 16,722 census queries,
  probe re-check on 7,232 observed call edges + 3,041 import events):
  **wall 7.7 s, peak RSS 116.3 MB**.
- Extraction alone: PY-STAT/1 2.79 s total, PY-STAT/2-SPIKE 4.28 s total
  (~1.5×; the D1 per-function environment analysis dominates the delta).
- Edges 28,370 → 28,391 (+21 net: converted sites emit one edge per
  candidate; 380 '*' edges replaced by 401 named-candidate edges).

## 4. Reading and verdict-INPUT

1. [MEASURED] Bounded local dataflow in the pinned D1–D3 scope converts
   22.55% of the unrestricted mass at ~1.5× extraction cost and ~0 soundness
   regression on proved facts, but recovers **0.0000 of the ablation
   headroom** on every inverse family, every repo, because §2.2 is
   all-or-nothing and the residual '*' floor (module-binding aliasing,
   getattr, exec taint: 11–180 per repo even under PERFECT D1–D3) is
   untouchable without module-scope dataflow, getattr policy, and
   taint-scope redesign — each of which G0 §2 already flagged as beyond
   candidate-mechanics (the tier-b value-escape closure, ASM-1057, binds
   any relaxation attempt).
2. [MEASURED] The conversion is not worthless — blocking mass on the killed
   families fell ~25% pooled — but that value is only redeemable under a
   re-scoped product semantics (per-candidate blocking / partial-answer
   deliverable), i.e. CODEVERT G0 §5.3 option (b), not under the registered
   κ.
3. [MEASURED] Narrowing surfaced 4 observed-truth exclusions (implicit
   C-mediated and metaclass dispatch) that unrestricted '*' had been
   absorbing vacuously: any full build needs pre-pinned probe domain
   exclusions.
4. **Verdict-INPUT: PY-STAT/2 worth a full build: NO in this bounded-local-
   dataflow form** — measured basis: 0/4,286 additional proved inverse
   queries, 0.0000 headroom recovery on all 6 repos, with a hard structural
   floor (≥11 unconvertible '*' per repo) that D1–D3-class mechanisms
   cannot remove; a full build is only worth designing as a PACKAGE that
   (i) adds module-scope alias dataflow + a getattr/exec policy to drive
   '*' to literally zero per repo, or (ii) re-scopes §2.2 to per-candidate
   blocking — and that is a §2.2-semantics design decision (coordinator/
   Fable), not an extractor patch. NON-SCORED: this line is spike input to
   that decision, not a verdict.

## 5. Repro

```bash
cd poc/codevert-g1/pystat2-spike
nice -n 10 python3 run_spike.py
# consumes READ-ONLY: ../../codevert-g0/{corpus,results/census.json,
#   results/g0-ablation-unrestricted.json,results/probe/*.trace.json,
#   extractor.py,engine.py}
# writes: results/spike-metrics.json, results/<repo>.probe-recheck.json
```
