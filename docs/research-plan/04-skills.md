# P4 — Skills to develop (reusable automation, honesty-enforcing by construction)

**Status:** operational specification for maintainer sign-off, 2026-07-08 (rev 2 — verifier
pass: RT-5 `prereg amend` design-amendment cutoff aligned to the **first `phase:"final"` run
record** (P2 §1.4/G-3), not the later `unblind` line; identity strings aligned to P2 §1.2
constraint 10 pseudonyms (RT-14); M0 date Jul 22 per RT-18). Component P4 of the
research plan (`docs/research-plan/`). Governed by `docs/kernel-design-directives.md`
(binding; esp. §3 "The SKILLS to develop", §6, §7). Implements the verbs defined by P2
(`02-data-and-reporting.md` §5.3 — the tool/guardrail surface each skill drives), the stage
template and guardrails of P3 (`03-operational-dag.md` §0.2, §4 GR-1…GR-15, node `I-SKILLS`),
and the statistical methodology of P8 (`08-stats-and-extrapolation.md` §1 SAP template, §2
extrapolation). Where this document names a guardrail ID (G-\* = P2 §4, GR-\* = P3 §4) or a
DAG node id, those documents are normative; P4 adds nothing to their semantics — it packages
them so they cannot be skipped.
**Author:** Fable planning agent (P4), for @jeswr. Coordination: sparq-org/sparq#1683.

**Purpose in one sentence.** Every recurring action in the programme — pre-register, run,
meter, decode, analyse, audit, report, write up, explain back — becomes a versioned,
self-documenting skill whose *only* write paths are the pinned P2 tools, so that executing
the plan with minimal manual work and maximal consistency is the same thing as executing it
honestly: the convenient path and the compliant path are one path.

Nothing here is RDF/OWL/SHACL-shaped (directives §1): skills operate on canonical JSON,
JSONL, sha256 pins, and the kernel's native formalism only.

---

## 0. What a "skill" is here, and the binding conventions

### 0.1 Format and location

A skill is a Claude Code `SKILL.md`-style package: a directory containing a `SKILL.md`
(YAML frontmatter `name:` + `description:`, then step-by-step operating instructions an
agent must follow verbatim) plus its executable scripts. Canonical, committed home:

```
tools/skills/<name>/
  SKILL.md            the agent-facing procedure (frontmatter + instructions)
  bin/                thin executable entrypoints (argparse CLIs, stdlib-only)
  tests/              fixture tests (run by `npm run skills:test` / `make skills-test`)
```

`.claude/skills/<name>` is a symlink into `tools/skills/<name>` so the harness auto-discovers
them; the committed copy under `tools/` is the system of record (box is ephemeral — GR-12).
Skills are Python 3.9 / Node stdlib-only, byte-deterministic, `nice -n 10` for anything heavy
(box constraints, house rules).

### 0.2 The normativity rule (binding)

**Skills are wrappers; the pinned tools are the law.** All state-changing operations go
through `tools/registry/{prereg-freeze, log-append, verdict-gen, registry-check}` and the
`poc/f0/` meters. A skill may orchestrate, template, validate, and explain; it may never
re-implement a write path, compute a verdict, or hold a second copy of any threshold. A buggy
or stale skill can therefore waste effort but cannot corrupt the record: the fail-closed
checks live below the skill layer (P2 G-1…G-14). Consequence: skills may be improved mid-
programme without amendment ceremony, **except** any change to `run-stats`'s shared statistics
library after an experiment freezes that library's hash (see §2.5 — that IS pinned material).

### 0.3 Shared conventions (every SKILL.md includes this block by reference)

1. **Identity**: every invocation asserts `--agent-id <role>-<n>` — a stable **pseudonym**
   (P2 §1.2 constraint 10 / RT-14: account-identifying material never enters hashed record
   bytes; the account↔pseudonym binding lives only in the unhashed
   `registry/identity-map.json` sidecar); skills refuse to
   run without it and stamp it into every record they touch (P2 §4 identities; GR-6).
2. **Fail closed**: any unverifiable precondition (missing verdict object, unreadable ledger,
   hash mismatch, absent human record) aborts with a named `ERR_*` code; no silent fallbacks
   (house rule; GR-4).
3. **No result invention**: a skill never types a number into a record; numbers flow from
   harness outputs, meters, or the pinned analysis script.
4. **Session close**: every skill that writes ends by running `registry-check`; work is done
   only when it passes AND `git push` succeeds (CLAUDE.md protocol + P2 §5.3; GR-12).
5. **Concurrency**: skills are single-experiment-scoped; parallelism happens via Modal
   `starmap` inside `run-experiment`, never by spawning agents (GR-3).
6. **Budget awareness**: every skill that can incur spend calls the ledger check first and
   prints its own kill command (GR-1, GR-14).

### 0.4 Name mapping to P3 `I-SKILLS`

P3's `I-SKILLS` node names `prereg, run-experiment, flop-meter, decode-verify, audit-result,
report-gen, paper-claims, explain-back`. P4 keeps those names and adds: `run-stats` (the P8
SAP/extrapolation executor — P3 folds it into report-gen/verdict-gen; it is split out here
because SAP *authoring* happens at freeze time, long before any readout), `paper-draft` (the
§7 manuscript skill; P3's writer-role tooling), and three supporting skills (`log-append`,
`registry-check`, `gate-eval`, `budget-watch`) that P2/P3 define as tools and P4 packages
with operating instructions. This is a packaging refinement, not a scope change to I-SKILLS.

---

## 1. Skill inventory (one line each)

| # | Skill | One-line purpose | Primary DAG nodes | Guardrail it enforces |
|---|---|---|---|---|
| S1 | `prereg` | Author, lint, and FREEZE an experiment registry record (with its SAP and pinned analysis script) before anything runs | every `X.reg` (f1–f7, g1–g9, e9, e8r/e8d, m0b, a-\*, family-h0), I-HYP | G-1, G-8, G-10, G-11 freeze-time lints; P8 §1.9 no-TBD rule |
| S2 | `run-experiment` | Execute a hash-pinned run (mock-first) and land every result via the append-only log | every `X.inputs`, `X.mock`, `X.run`, `X.log`; D-\* artifact pinning | GR-1/2/13; G-1, G-11, G-14 at the write path |
| S3 | `flop-meter` | Measure the full metric vector V: params, FLOPs, peak memory, latency p50/p95, $/query, training FLOPs, lifecycle amortization | I-F0; every `efficiency_relevant` run (f1–f7, e9 cost sides); a-hs9 | G-9 (full vector or no verdict); directives §2 |
| S4 | `decode-verify` | Decode a kernel vector against the pinned encoder and report fidelity + confidence (the verifier instrument itself) | e9 arms 4/5, f2 verifier loop, g5, m0b materials, audit re-runs | encoder pin (GR-2/G-14); HC2 "name the failing stage" rule |
| S5 | `run-stats` | Instantiate the P8 SAP into a pinned analysis script at freeze; execute readouts and §2 extrapolation fits at unblind | `X.reg` (script authoring), every `X.readout`, a-hs9/10/11, a-extrap-2/5, a-h0 | G-4 (frozen analysis), G-10 (Holm/TOST), G-12/P8 §2 (scale licensing) |
| S6 | `audit-result` | Independent adversarial audit of a readout from pinned artifacts, by a non-runner identity | every `X.audit` (GATE-A), paper.review | G-6/GR-6 run-vs-audit separation; only path PASS-PENDING-AUDIT→PASS |
| S7 | `report-gen` | Produce the verdict object + rendered report purely from registry+log (wraps `verdict-gen`); regenerate the global status table and GNG dossiers | every `X.close`, r-final, GNG-1/2/3 dossiers | G-3/G-5/G-7 (negatives at full prominence; coverage in every verdict) |
| S8 | `paper-claims` | Generate and check the machine claims-trace table: no claim without a verdict-object row | paper.claims, paper.lint, xb.lint | GR-15 / P2 §5.5 (`registry-check --paper`) |
| S9 | `paper-draft` | Draft the top-tier-venue manuscript whose every quantitative statement carries a `{{claim:<id>}}` anchor into the claims table | paper.outline, paper.draft | GR-15; directives §7 (honest write-up incl. negatives) |
| S10 | `explain-back` | Render the plain-language maintainer explainer (what-found / what-it-means / what-scale / go-no-go) from the same verdict objects | xb.draft, xb.deliver prep | GR-15 (xb.lint); directives §7 explainer-back |
| S11s | `log-append` (supporting) | The only write path into `results-log/<id>.jsonl` (hash-chained) | inside S2/S5/S6; standalone for `note`/`status`/`supersede` events | G-1, G-2, G-11, G-14 |
| S12s | `registry-check` (supporting) | The honesty lint: chain, append-only, frozen drift, citations, paper scan, status regen | CI on every push; pre-push hook; paper.lint/xb.lint engines | G-2, G-3, G-12, G-13, GR-9, GR-15 |
| S13s | `gate-eval` (supporting) | Evaluate AUTO-GATE / GNG conditions with the P2 §3.1 expression grammar over verdict objects — the only gate semantics | GATE-T1/T4/T5 conditions, GNG-1/2/3 route computation, E7-PRE, a-h0 | GR-4 (fail-closed gates); P2 §5.2 |
| S14s | `budget-watch` | Hourly spend monitor + tested kill switches | I-BUDGET; runs continuously through P-1…P-6 | GR-1, GR-14 |

Coverage check against the directives-§3 list: `prereg` ✓ (S1), `run-experiment` ✓ (S2),
`flop-meter` ✓ (S3), `decode-verify` ✓ (S4), `audit-result` ✓ (S6), `report-gen` ✓ (S7);
directives-§6 statistics ✓ (S5); directives-§7 write-up + explainer ✓ (S8–S10).

---

## 2. Per-skill specifications

Format per skill: purpose · inputs · outputs · DAG usage · guardrail · spec sketch.

### 2.1 S1 `prereg`

- **Purpose.** Take an experiment from P1 prose to a FROZEN, hash-pinned registry record that
  verdict-gen can later execute — before a single eligible run exists.
- **Inputs.** EXP-ID; the P1 hypothesis/experiment section (path+anchor); the P8 SAP block for
  this experiment; arm definitions incl. mandatory baselines; pins (encoder hash, corpus
  manifests, model revisions, harness manifest); budget block; rungs + seeds; the pinned
  analysis script (produced by S5 mode A) + its fixture-test results; `--agent-id`.
- **Outputs.** `registry/experiments/<id>.json` (DRAFT → FROZEN), `frozen_sha256` appended to
  `registry/frozen-index.json`, a freeze commit, and a freeze announcement line for the
  coordination issue. For post-GNG-0 late freezes (e8d, f7, g5, d-st-dependent): the
  announcement is mandatory (P3 §1.1 GNG-0 row).
- **DAG usage.** Every `X.reg` stage (~30 nodes: f1–f7, g1–g9, e9, e8r, e8d, m0b, a-hs9/10/11,
  a-extrap-2/5, a-h0, family-h0); I-HYP (freezing `registry/hypotheses.json`); amendment
  authoring (`registry/amendments/<id>/…`) via `prereg --amend`.
- **Guardrail enforced.** G-1 (nothing runs unfrozen), and all freeze-time lints: G-8
  (mandatory baselines incl. kernel-as-text vs `registry/hypotheses.json`), G-10 (exactly one
  primary endpoint; secondaries form one Holm family), G-11 (budget block; Tier-5 requires
  `budget.maintainer_signoff`), P2 §1.2 schema constraints 1–10 (exhaustive verdict rules,
  TOST bound present for NULL, full-V DV list when `efficiency_relevant`, ≥5 seeds for
  trained arms, verbatim kill + envelope text non-empty), P8 §1.9 (no field TBD; SAP shows
  both rejection-branch and TOST-branch power ≥0.90), and the P2 §5.4 review rule (the
  "script implements the plan" reviewer ≠ script author, recorded in
  `analysis_plan_review: {by, date}`).
- **Spec sketch.**
  1. `prereg draft <id>` — scaffold the record from the P1/P8 anchors; interactive fill of
     IVs/DVs/endpoints/verdict_rules; verdict_rules generated from the SAP §1.8 canonical
     ordering with P1 kill clauses quoted verbatim.
  2. `prereg lint <id>` — run every schema + G-8/G-10/G-11 check; verify every
     `verdict_rules` metric pointer against the analysis script's declared output vocabulary
     (P8 §1.8) — unknown pointers fail HERE, not at readout; verify `analysis_plan_ref.sha256`
     against the committed P8 doc; run the analysis script's fixture tests (P2 R-4).
  3. `prereg freeze <id> --reviewed-by <identity>` — refuse if reviewer == script author or
     any lint fails; canonicalise; compute `frozen_sha256`; write frozen-index; commit;
     announce. `ERR_P4_PREREG_LINT`, `ERR_P4_SELF_REVIEW`, `ERR_P2_NOT_FROZEN` downstream.
  4. `prereg amend <id> --kind ops|design|pre-authorized-fallback` — build an RFC-6902 patch
     record; tooling stamps `unblinding_state_at_write` from the log. A `design` amendment
     is refused with the "new experiment ID" message as soon as the log contains **any
     `phase:"final"` run record** — the raw-data-exposure cutoff (P2 §1.4/G-3, RT-5),
     deliberately EARLIER than the `unblind` line (which is only a second, later witness of
     first analysis exposure). `ops` amendments (the whitelisted pointers) stay valid until
     CLOSED; `pre-authorized-fallback` must name its authorizing frozen-record field.
- **Tests.** Golden freeze of a mock experiment; a lint-failure battery (missing text-null
  arm, two primaries, TBD power field, drifted plan sha, self-review).

### 2.2 S2 `run-experiment`

- **Purpose.** Execute one experiment campaign exactly as frozen: build+pin inputs, mock
  smoke, full run, and land every cell in the chained log — with the budget checked before
  and during, and nothing writable by hand.
- **Inputs.** EXP-ID (must be FROZEN); stage (`inputs|mock|run|log`); transport
  (`modal|aws`); `--agent-id`; for `run`: nothing else — everything comes from the frozen
  record (the point).
- **Outputs.** A materialised RunSpec (P3 §3.2, all fields verified); staged-bytes manifest;
  Modal/AWS app launch with per-call sized timeouts; `results-incoming/<stamp>-…/` artifact
  dirs + provenance sidecars; one `log-append` line per arm×rung×seed cell; a mock stamp for
  GR-13; deliberate-commit checklist for the coordinator (results are never auto-pushed —
  GR-8).
- **DAG usage.** Every `X.inputs`, `X.mock`, `X.run`, `X.log` (all Tier 0–5 experiments); the
  D-\* authoring nodes reuse its hash-pinning subcommand (`run-experiment pin <path>…`) so
  every corpus/arm artifact enters the world with a manifest sha.
- **Guardrail enforced.** GR-2 (in-container staged-manifest + encoder + corpus + prereg-hash
  assertions, fail-closed `ERR_STAGING_MISMATCH`/`ERR_GLOSS_PIN`-style codes); GR-13
  (mock-first: refuses `run` without a same-day green mock stamp of the same staged bytes);
  GR-1 (refuses any RunSpec whose `worst_case_usd` exceeds tier headroom — `ERR_BUDGET`);
  G-1/G-14 via `log-append` (final-phase records require FROZEN status + matching prereg
  hash; drifted pins auto-demote to exploratory); GR-3 (parallelism only via `starmap`);
  P3 §3.5 retry discipline (infra failures: ≤2 retries, backoff; scientific failures: never
  retried, salvage to `-FAILED/`, bead filed).
- **Spec sketch.**
  1. `run-experiment inputs <id>` — build/collect inputs, hash each, verify against the
     frozen `pins` block, write the input manifest.
  2. `run-experiment mock <id>` — `--mock` transport smoke (~pennies), record stamp keyed on
     (app, staged-bytes digest, UTC day).
  3. `run-experiment run <id>` — materialise RunSpec from the frozen record; verify all
     fields; ledger check; print the kill command (`modal app stop <app-id>` /
     `terminate.sh`); launch; poll; salvage on failure.
  4. `run-experiment log <id> <results-dir>` — validate artifacts, compute per-cell raw
     metrics files' shas, call `log-append` once per cell (raw metrics only — any p-value or
     effect size in the payload fails schema, P2 §2.4); prompt coordinator for the deliberate
     commit.
- **Tests.** End-to-end against a dummy 2-arm/1-rung/2-seed experiment on CPU; a pin-drift
  fixture (must demote to exploratory); a budget-breach fixture (must refuse); a mock-absent
  fixture (must refuse `run`).

### 2.3 S3 `flop-meter`

- **Purpose.** One implementation of the F0 accounting (`design-efficiency-track.md` §3) that
  every efficiency-relevant run calls, so V is measured identically everywhere and the two
  value theses are always reported on the same ruler (directives §2).
- **Inputs.** A run context: model spec (params incl. n_total/n_active/n_trained), tokenizer,
  per-query traces (prompt/output token counts, verifier calls), hardware profile (pinned GPU
  + rate card), store byte inventories; for lifecycle numbers: training FLOPs/steps/tokens
  and the query-volume sweep Q ∈ 10⁴–10⁸ (HS9).
- **Outputs.** The `metric_vector` block of the P2 run-record schema, exactly: `accuracy`
  (filled by the harness, passed through), `params {n_total, n_active, n_trained}`, `memory
  {peak_bytes_total_system}` (total-system byte ledger — model + adapter + store + index +
  verifier lexicon), `inference_compute {flops_per_query, latency_ms_p50, latency_ms_p95,
  usd_per_query}`, `training_compute {flops, steps, tokens}`; plus the `cost {usd,
  gpu_hours}` block; plus a lifecycle-amortization table for a-hs9. Verifier accounting
  includes the NN-cleanup ≈ |lexicon|·D MACs term explicitly (P3 I-F0).
- **DAG usage.** Built at I-F0 (with unit tests, a GNG-0 prerequisite); invoked inside every
  `X.run` where `efficiency_relevant: true` (f1–f7, e9's cost sides, g4's LLM-cost lines);
  a-hs9's amortization sweep; instrument cross-check consumed by f2's SAP gate ("FLOP-meter
  within 2× of wall-clock-derived FLOPs" — P8 §3.2 item 10).
- **Guardrail enforced.** G-9 — a missing V component makes the verdict INCOMPLETE-DATA;
  flop-meter's job is that the component is never missing and never hand-estimated. Also the
  F0 fairness rules (matched items, matched budgets) by measuring, not trusting, per-arm
  compute.
- **Spec sketch.** Library (`poc/f0/`) + CLI: `flop-meter measure --model … --trace …`;
  analytic FLOPs from architecture dims cross-checked against wall-clock×device-peak-utilisation
  bounds (2× tolerance gate exported as `/gates/…` input); memory via peak-RSS + CUDA
  max_memory_allocated + store bytes on disk (zstd-JCS discipline for byte-matched
  baselines, from F1); $/query = sized-time × pinned rate card (rates frozen in the record's
  budget block); JSON out, schema-validated. Unit tests: hand-computed transformer-block FLOP
  fixture; a known-size store byte fixture; a fabricated trace with expected p50/p95.

### 2.4 S4 `decode-verify`

- **Purpose.** The kernel-decode-fidelity instrument: given concept vector(s) and the pinned
  encoder, reconstruct the explication, verify it against the kernel/axiom sidecar, and
  report per-stage confidence — the operational core of the correctness thesis (kernel as
  external verifier) and of HC1/HC2's arms.
- **Inputs.** Vector(s) or vector-store handle; `--encoder-hash` (must equal the frozen pin —
  currently `40e8c8ba…` mainline; the G1 random-atom fork quotes its own fork hash); decode
  depth/clause budget; optionally an axiom sidecar sha for constraint checking (E9-C); mode
  (`decode | verify | roundtrip`).
- **Outputs.** Decoded explication (canonical form) + per-clause confidence + margin
  diagnostics (X2 machinery); verify mode: {violations found, axiom ids, per-stage status
  decode/authoring/checker} — the "name the failing stage" structure HC2's kill requires;
  roundtrip mode: encode(decode(v)) fidelity for g5-style checks. All outputs are raw-metric
  JSON fit for `log-append`.
- **DAG usage.** e9 arms 4/5 (decode-verify + repair-retry) and the E9-C constraint arm; f2's
  verifier loop (arm 4, cascade arm, in-decode gating arm); g5 encode-twice margins; m0b
  materials (coverage spot-check packets); every S6 audit that re-derives a decode-dependent
  claim; heritage: wraps the existing X2 decoder + confidence reporting in `encoder/`.
- **Guardrail enforced.** GR-2/G-14 encoder-pin discipline (refuses on hash mismatch —
  `ERR_ENCODER_PIN`; no decode-dependent claim on the Bq path, P3 §3.2); fail-closed ERR_\*
  decode errors rather than best-effort guesses (house rule); instrument-validity feed
  (decode-collapse rate → `/gates/instrument_valid`, P8 §3.1 item 10 — a decode collapse is
  INSTRUMENT-INVALID, never a hypothesis FAIL).
- **Spec sketch.** CLI over the `encoder/` package: `decode-verify --encoder-hash … --mode
  verify --sidecar-sha … < vectors.jsonl > findings.jsonl`; deterministic (no sampling; any
  LLM-repair step lives in the *arm harness*, not in this instrument); per-item output
  schema versioned (`kot-dv/1`); latency of the verifier itself metered via S3 (the verifier
  is on the cost ledger — F0). Tests: X2 golden decode cells; a planted-violation fixture
  from D-IR with known catch set; a wrong-hash refusal test.

### 2.5 S5 `run-stats`

- **Purpose.** Make the P8 statistics executable and unalterable: (mode A, freeze time)
  instantiate an experiment's SAP into a pinned analysis script from one shared, tested
  statistics library; (mode B, readout time) execute the readout via `verdict-gen`; (mode C)
  run the §2 scale-extrapolation fits for the a-extrap nodes.
- **Inputs.** Mode A: EXP-ID + its P8 SAP block (§1.9 fields). Mode B: EXP-ID (everything
  else is frozen). Mode C: the per-rung effect estimates + SEs from member experiments'
  `analysis-output.json` files (pinned by sha), the target rung, and the §2.4 anchor row id.
- **Outputs.** Mode A: `poc/<exp>/analyze_<id>.py` + fixture tests (hand-computed expected
  outputs on mock data) + the declared output-field vocabulary (P8 §1.8) — all inputs to S1's
  freeze. Mode B: `reports/auto/<id>/analysis-output.json` + the `unblind` log line (both
  produced by `verdict-gen`, which run-stats invokes; the skill never computes a verdict
  itself). Mode C: `/analysis/slope, slope_ci_low|high, pi_at_target_low|high, anchor_class`
  + the licensed-claim sentence template of P8 §3.2, for a-extrap-2 (sign level) and
  a-extrap-5 (slope level).
- **DAG usage.** Mode A inside every `X.reg`; mode B = every `X.readout` (incl. the
  analysis-only chains a-hs9, a-hs10, a-hs11, a-h0, family-h0); mode C = a-extrap-2,
  a-extrap-5 — the only nodes that license scale adjectives (GR-9).
- **Guardrail enforced.** G-4 (all derived statistics exist only in the pinned script's
  output; the shared library's version hash is embedded in each generated script, and any
  post-freeze library change does NOT affect frozen scripts — they vendor their exact
  functions or pin the library sha, checked at execution); G-10 (Holm families, TOST margins
  from the P8 §1.5 table — the library refuses a NULL path with no declared SESOI); C-1…C-7
  clarifications hard-coded (one-sided Wilson z=1.645; IUT for conjunctions; item-level
  seed-stratified resampling; cluster bootstrap when concept-overlap >20%; float64, no
  pre-rounding); P8 §2 (WLS 1/SE² weights; M-lin/M-pow/M-sat candidate set with the ≥4-rung
  M-sat rule; AICc selection; form-disagreement downgrade; both PI procedures, wider governs;
  1-OOM range cap; anchor classification with the ANCHOR-CONTRADICTING ⇒ replication-first
  consequence); G-12 (`scale_language_licensed` computed from rung count, never asserted).
- **Spec sketch.**
  - Shared library `tools/stats/kotstats.py`: seed-stratified paired permutation (B=10⁵),
    BCa bootstrap (B=10⁴, item/cluster resampling, selection-inside-resample), exact
    binomial + one-sided Wilson bounds, TOST per §1.5 margin table, Holm, BH-FDR (F-explore
    only, output flagged `citable:false`), Cohen's h/d, DeLong, Spearman+permutation, WLS +
    AICc + parametric-PI + parametric-bootstrap-envelope, power formulas (§1.6) — every
    routine with a hand-computed fixture.
  - `run-stats author <id>` → generates `analyze_<id>.py` that: reads eligible run records
    from stdin (and nothing else — no network, no other experiments' files), computes exactly
    the SAP's named fields into the §1.8 vocabulary, declares its output schema, and embeds
    (a) the library pin, (b) the C-7 float64 declaration, (c) PRNG seeds from the frozen
    record.
  - `run-stats readout <id>` → thin wrapper: `verdict-gen <id>` (chain verify → amendments →
    eligibility → completeness → pinned script in no-network sandbox → unblind line →
    verdict_rules → PASS-PENDING-AUDIT gating). Refuses to run any script whose sha ≠ the
    frozen `pins.analysis_script.sha256` (`ERR_P2_FROZEN_DRIFT` path).
  - `run-stats extrapolate --family <a-extrap-2|a-extrap-5> …` → mode C as above; refuses a
    slope fit with <3 rungs and an M-sat fit with <4 (`ERR_P4_RUNGS`); emits the P8 §2.5
    persistence-rule checklist evaluation alongside the numbers.
- **Tests.** The P8 §3.2 worked HE1/HE7 example as an end-to-end fixture (illustrative
  numbers → expected slope −0.10/decade, CI, PI, anchor class); a TOST-margin battery; a
  3-rung PI vacuity check (t=6.31 shows up); a form-disagreement downgrade fixture.

### 2.6 S6 `audit-result`

- **Purpose.** The independent adversarial audit that separates running from grading: a
  distinct identity re-derives a readout from pinned artifacts and either CONFIRMs or REFUTEs
  it. The only path from PASS-PENDING-AUDIT to PASS.
- **Inputs.** EXP-ID with a computed verdict; `--agent-id` (MUST differ from every `runner`
  in the experiment's eligible log — schema-enforced, `ERR_P2_SELF_AUDIT`); audit depth
  (`full` for positives, `conformance` for kills/nulls — P3 §0.2); for Tier ≥2 positives and
  paper.review: an auditor pseudonym bound to the backup Fable account in the unhashed
  `registry/identity-map.json` sidecar (`auditor-<n>`, O-5; the account name itself never
  enters record bytes — P2 §1.2 constraint 10, RT-14).
- **Outputs.** `registry/audits/<id>/<n>.json` (kot-audit/1): artifacts re-hashed, chain
  segment re-verified, re-run outputs + deltas, checklist item results, outcome
  CONFIRMED/REFUTED/BLOCKED; an `audit-ref` log line; on CONFIRMED, a re-run of S7 upgrades
  the verdict.
- **DAG usage.** Every `X.audit` (GATE-A; ~30 nodes); paper.review (the manuscript audit —
  same skill, checklist section 9); m0b.audit's re-derivation leg.
- **Guardrail enforced.** G-6/GR-6 (identity separation + adversarial re-derivation);
  indirectly GR-10 (tuning-asymmetry check is an audit item).
- **Spec sketch — the audit checklist (normative; each item scored pass/fail/n-a with
  evidence):**
  1. **Pins**: recompute frozen_sha256; re-hash every artifact the log cites; re-verify the
     chain segment covering eligible runs.
  2. **Re-derivation**: re-execute the pinned analysis script in the sandbox from the
     eligible records; byte-compare `analysis-output.json`; re-evaluate verdict_rules with
     the shared evaluator; any delta ⇒ REFUTED.
  3. **Eligibility honesty**: re-run the step-3 filter independently; check the excluded-runs
     table is complete; check no superseded-successful-run pattern.
  4. **Leakage**: eval-set/train-set overlap probes; prompt-contamination scan on arm inputs;
     judge-leak check where an LLM judge was allowed (E5 discipline).
  5. **Tuning asymmetry** (GR-10): per-arm config diff over the full logged configs — LR
     sweeps/retry budgets/prompt iterations must be arm-symmetric per the frozen record.
  6. **Endpoint drift**: diff the executed estimand pipeline against the SAP text (P8 §1.9
     field 1); selection steps must be inside the bootstrap as declared.
  7. **Baseline strength**: verify the mandatory baselines actually ran at competitive
     settings (not straw-manned): spot re-run of ≥1 baseline cell.
  8. **Instrument gates**: verify `/gates/*` inputs were computed, not defaulted.
  9. **(paper.review mode)** every quantitative sentence re-derived from its claims-table
     verdict object; framing checked against P1 §6 anti-overselling guards; scale language
     against the license fields.
  Outcome rule: CONFIRMED requires items 1–8 all pass; any REFUTED item ⇒ REFUTED with the
  evidence attached; BLOCKED (cannot evaluate) is fail-closed and leaves the verdict pending.
- **Tests.** A planted-discrepancy fixture (tampered analysis output must REFUTE); a
  self-audit refusal test; a conformance-depth path test on a FAIL verdict.

### 2.7 S7 `report-gen`

- **Purpose.** Produce every human-readable result artifact purely from machine state —
  verdict reports, the global status table, and the GNG gate dossiers — so no result is ever
  narrated by hand (P2 P-3: verdict = f(frozen record, log)).
- **Inputs.** EXP-ID (report mode); or `--status` (table mode); or `--dossier <GNG-1|2|3>`
  (dossier mode). No free-text inputs except the optional, fenced
  `reports/auto/<id>/commentary.md`.
- **Outputs.** `registry/verdicts/<id>.json` + `reports/auto/<id>/verdict-<id>.md` (via
  `verdict-gen`, template P2 §3.3 — kill text rendered beside every outcome, coverage +
  rungs + envelope verbatim, excluded-runs table, PASS-PENDING-AUDIT banner);
  `registry/status.json` (one line per experiment, negatives identical in structure);
  GNG dossiers: every member verdict + audit + kill text + M0b + envelope rows + spend
  ledger + the machine-computed route (via S13s), zero hand-written numbers.
- **DAG usage.** Every `X.close`; r-final (the paper's evidence bundle IS report-gen output);
  GNG-1/2/3 dossier prep; the `registry/status.json` regen after every verdict (I-BEADS
  resync trigger).
- **Guardrail enforced.** G-5 (unconditional rendering — FAIL/NULL/INCONCLUSIVE get every
  section a PASS gets; the DAG's done-predicate requires the committed report); G-7 (refuses
  to render without the M0b coverage block); GR-5's mechanised anti-overselling (refuses a
  PASS render without the verbatim kill text — this is inside the template contract); GR-9
  (every quoted number carries rung + coverage; scale wording gated on the license field).
- **Spec sketch.** `report-gen verdict <id>` = verdict-gen + template render + commit
  checklist; `report-gen status` = regenerate status.json + a markdown mirror; `report-gen
  dossier GNG-2` = assemble from verdict objects + `gate-eval` route output + budget ledger;
  refuse on any empty mandatory slot (`ERR_P4_EMPTY_SLOT`). Byte-deterministic: same repo
  state ⇒ identical bytes (repo convention).
- **Tests.** Render fixtures for each verdict type incl. INCOMPLETE-DATA and
  PASS-PENDING-AUDIT; a missing-coverage refusal; a dossier fixture over three mock verdicts.

### 2.8 S8 `paper-claims`

- **Purpose.** The claims-trace generator and checker: every claim the manuscript or
  explainer will make becomes a machine row first, and text that exceeds its row cannot ship.
- **Inputs.** The set of CLOSED verdict objects (via `registry/status.json`); paper scope
  declaration `paper/scope.json` (hypothesis IDs — frozen before results drafting, P2 §5.5);
  in check mode: the manuscript/explainer source with `{{claim:<id>}}` anchors.
- **Outputs.** `paper/claims.json`: rows `{claim_id, text, experiment, verdict_path,
  verdict_sha256, fields_cited, envelope_row, kill_text, scale_language_license}`; check
  mode: the `registry-check --paper` report (pass/fail with per-anchor findings).
- **DAG usage.** paper.claims (generation); paper.lint and xb.lint (checking — S8 is the
  skill face of `registry-check --paper/--citations`); consumed by S9/S10.
- **Guardrail enforced.** GR-15 in full: no claim without a trace row; PASS-PENDING-AUDIT
  never cited as PASS; kill text travels with every PASS; scale adjectives require the
  license; every CLOSED experiment in scope appears in the results section (negatives cannot
  be omitted); every extrapolation sentence quotes its a-extrap envelope + uncertainty.
- **Spec sketch.** `paper-claims generate` — seed one row per closed verdict per hypothesis
  in scope, with suggested claim text templated from the verdict object (the writer edits
  wording, never numbers; regeneration flags text/number drift). `paper-claims check
  <doc.md>` — anchor↔row bijection; sha re-verification; direction/magnitude regex battery;
  scale-adjective scan against license fields; envelope-citation scan; scope-completeness
  cross-check vs status.json. Fail-closed exit codes wired into paper.lint / xb.lint gates.
- **Tests.** A fixture paper with one untraced claim, one over-claimed scale adjective, one
  omitted negative — all three must fail with named findings.

### 2.9 S9 `paper-draft`

- **Purpose.** Draft the directives-§7 manuscript: top-tier-venue standard, completely honest
  including negatives, with every quantitative statement anchored to the claims table — the
  Writer agent's operating procedure, not just a template.
- **Inputs.** r-final evidence bundle; `paper/claims.json`; `paper/scope.json`; the P1 §6
  route actually taken (TAKE/NARROW/PIVOT/KILL — the paper's framing follows the route, and
  a KILL route yields a rigorous negative-results paper as a pre-declared success mode);
  venue format (O-9); the L1–L3 prior-art positioning + Hyperdimensional-Probe
  differentiation notes; P8 §2.4 anchor table for the related-work scaling discussion.
- **Outputs.** paper.outline (results section enumerates every CLOSED experiment from
  status.json — omission is mechanical and forbidden); paper.draft manuscript with
  `{{claim:<id>}}` anchors on every quantitative sentence; limitations section = the
  envelope table verbatim; abstract states the headline honestly (a negative headline goes
  in the abstract when it is the finding).
- **DAG usage.** paper.outline, paper.draft (Writer role `writer-1`); iterates
  under paper.lint (S8/S12s) until clean; then paper.review (S6, auditor identity) →
  paper.sign (GATE-H).
- **Guardrail enforced.** GR-15/directives §7 by construction: the skill's drafting rules
  forbid any number not copied from a claims row; methods = pointers to frozen preregs
  (never re-described in ways that could drift); results ordered by the registry table, not
  by favourability.
- **Spec sketch.** SKILL.md procedure: (1) freeze scope.json; (2) generate outline from
  status.json + claims table; (3) write section-by-section with the anchor discipline —
  numbers via `{{claim:…}}` only; (4) self-run `paper-claims check` after every section;
  (5) mandatory sections: full results table (all CLOSED experiments), envelope/limitations
  verbatim, negative-results discussion at structural parity, reproducibility appendix =
  r-final bundle pointers, agent-contribution disclosure (O-10); (6) hand to paper.lint,
  then request S6 review under a distinct identity. Anti-spin phrasebook: banned verdict
  synonyms ("effectively passed", "nearly significant" …) — the same impostor list
  registry-check greps for.
- **Tests.** Outline-completeness fixture (a hidden CLOSED FAIL must appear); an anchor-drift
  fixture (edited number ≠ verdict object must fail S8 check).

### 2.10 S10 `explain-back`

- **Purpose.** The accessible explainer-back to the maintainer: plainest-possible language,
  same numbers, same honesty gates — what we found / what it means / what scale it holds at /
  go-no-go recommendation (directives §7).
- **Inputs.** The same verdict objects + claims table as S9; the GNG-3 (or GNG-2) computed
  route; the P1 §4b envelope rows; maintainer Q&A transcript (post-delivery).
- **Outputs.** xb.draft: one page + Q&A appendix; every number carries its experiment id;
  each finding rendered as a four-slot card {found, means, scale-it-holds-at (from
  `scale_language_licensed` + envelope), recommendation}; the delivered version with the
  live Q&A appended and committed (xb.deliver record).
- **DAG usage.** xb.draft → xb.lint (S8 check, same engine as paper.lint) → xb.deliver
  (GATE-H; skill prepares the session materials and commits the Q&A record).
- **Guardrail enforced.** GR-15's explainer clause: *simplify language, never claims* — the
  lint is identical to the paper's; plus paper.sign ≺ xb.deliver ordering (P3 §1.10).
- **Spec sketch.** Template with fixed slots filled from `verdict`, `coverage`,
  `scale_language_licensed`, `extrapolation_envelope_verbatim`, and the computed decision
  route (P2 §5.5); a plain-language glossary mapping every statistical term used to a
  one-line explanation; readability target enforced editorially (short sentences, no
  unexplained jargon), honesty enforced mechanically (S8). Q&A protocol: questions logged
  verbatim, answers must cite experiment ids, unanswerable questions become beads issues.
- **Tests.** A lint fixture where the explainer rounds a number beyond display precision or
  drops a CI — must fail.

### 2.11 Supporting skills (S11s–S14s, brief)

- **S11s `log-append`** — packages `tools/registry/log-append` with operating instructions
  for the non-run events (`note` for anomalies, `status` transitions, `supersede` with the
  exit≠ok-only rule). Guardrails G-1/G-2/G-11/G-14 live here; every other skill calls it
  rather than touching JSONL. Used by: S2, S5, S6; standalone in triage.
- **S12s `registry-check`** — packages the CI lint (`--chain --append-only --frozen-drift
  --citations --paper --status`) + the pre-push hook installation + the session-close
  protocol line. Used by: CI on every push; every skill's step "finish with registry-check";
  paper.lint/xb.lint engines. Guardrails G-2/G-3/G-12/G-13/GR-9/GR-15.
- **S13s `gate-eval`** — the single shared evaluator for AUTO-GATE conditions and the P1 §6
  decision tree over verdict objects (P2 §3.1 grammar; no second semantics). Evaluates
  GATE-T1/T4/T5 preconditions, GNG-1/2/3 routes, E7-PRE, a-h0's disjunction. Fail-closed:
  unevaluable ⇒ CLOSED (GR-4). Output: a committed gate record quoting every input sha.
- **S14s `budget-watch`** — deploys the hourly cost monitor against Modal spend + the
  ledger; smoke-tests kill switches against a dummy breach (I-BUDGET); documents the GR-14
  kill inventory; every launcher prints its kill command. Runs continuously P-1…P-6.

---

## 3. Build order

Ordering is forced by three facts: (a) nothing may run before GNG-0, and GNG-0 needs the
freeze machinery + F0 + skills packaged (P3 §1.1); (b) `prereg` cannot freeze anything
without a pinned analysis script, so `run-stats` mode A precedes the first real freeze;
(c) f2's freeze is the acceptance test of the whole backbone (P2 §5.5).

| Order | Skill | Why here | Needed by (first consumer) | Target |
|---|---|---|---|---|
| 1 | S12s `registry-check` | The lint everything else's tests assert against; tamper fixture proves the chain | I-REG unit tests | Jul 09–10 |
| 2 | S11s `log-append` | The only write path; S1/S2/S5 all depend on it | I-REG | Jul 09–10 |
| 3 | S5 `run-stats` (library + mode A) | Analysis scripts must exist and pass fixtures before any freeze; the shared stats library is the largest single build item | m0b.reg, f2.reg | Jul 10–13 |
| 4 | S1 `prereg` | Freezing starts (m0b first, then a-h0, then f2 as acceptance test) | m0b.reg (W0b) | Jul 11–13 |
| 5 | S3 `flop-meter` | I-F0 is a GNG-0 dependency; f2.inputs needs it | I-F0, GATE-T1 | Jul 11–14 |
| 6 | S7 `report-gen` | m0b.close (pre-GNG-0 milestone) needs verdict render; status table feeds beads | m0b.readout/close | Jul 12–14 |
| 7 | S6 `audit-result` | m0b.audit is on the M0 critical path; I-AUDIT is a GNG-0 dep | I-AUDIT, m0b.audit | Jul 12–15 |
| 8 | S14s `budget-watch` | I-BUDGET (GATE-H O-1) needs the tested monitor before GNG-0 | I-BUDGET | Jul 13–15 |
| 9 | S2 `run-experiment` | First GPU spend is f2 (GATE-T1, target Jul 22); Tier-0 CPU runs use its pin/log path earlier | f1.run (CPU), f2.mock | Jul 13–18 |
| 10 | S4 `decode-verify` | First consumers are f2's verifier arm and e9.inputs; wraps existing X2 machinery (small delta) | f2.inputs | Jul 15–20 |
| 11 | S13s `gate-eval` | First hard machine gate is GATE-T1 (~Jul 22); GNG-1 needs the route evaluator | GATE-T1, GNG-1 | Jul 16–20 |
| 12 | S5 mode C (extrapolation) | Needed at a-extrap-2 (Sep); built earlier only if slack | a-extrap-2 | by Aug 31 |
| 13 | S8 `paper-claims` | First needed at paper.claims, but building it by GNG-2 lets the dossier reuse the trace machinery | GNG-2 dossier, paper.claims | by Sep 18 |
| 14 | S9 `paper-draft` + S10 `explain-back` | Write-up phase (P-7); built before GNG-2 so a PIVOT/KILL route (write-up pulls forward to Oct 01) is not blocked on tooling | r-final/paper.outline; xb.draft | by Sep 25 |

Items 1–8 are the GNG-0 package (P3 milestone M0, Jul 22 — slipped from Jul 15 per P7
RT-18; the build targets above land ahead of it): they make `I-REG`, `I-F0`,
`I-AUDIT`, `I-BUDGET`, `I-SKILLS` green. Items 9–11 complete the Tier-1 launch surface
(GATE-T1). Items 12–14 are deliberately early relative to their DAG position so that the
directives-§7 phases are never tool-blocked on any route, including early KILL.

Estimated build cost: R0-tier, ~4–6 agent-days total, ~$0 compute (stdlib only; fixture
tests on this box, `nice`d). The largest single risk is S5's statistics library; its
fixtures (hand-computed permutation/bootstrap/WLS cases, incl. the P8 §3.2 worked example)
are the mitigation and are non-negotiable at freeze time (P2 R-4).

---

## 4. SKILL.md skeletons for the top three

Concrete skeletons for the three highest-leverage skills (S1, S2, S5). Frontmatter +
procedure; scripts referenced live in `bin/`.

### 4.1 `tools/skills/prereg/SKILL.md`

```markdown
---
name: prereg
description: Author, lint, and FREEZE a kernel-of-truth experiment registry record
  (with its SAP-derived pinned analysis script) BEFORE anything runs. Use whenever a
  DAG node X.reg is ready, or to author an amendment. Refuses to freeze anything that
  could not later produce an honest verdict.
---

# prereg — pre-register an experiment

## When to use
- An experiment's P1 section and P8 SAP block exist and its X.reg node is unblocked.
- NEVER to "fix" a frozen record after data exists — that is `prereg amend` (design
  amendments are valid only BEFORE the experiment's first phase:"final" run record —
  the raw-data-exposure cutoff, P2 §1.4/G-3; ops amendments until CLOSED) or a NEW
  experiment id. If in doubt, stop and file a bead.

## Inputs you must have before starting
1. EXP-ID and the P1 anchor (hypotheses, arms, kill text — quoted verbatim, never retyped).
2. The P8 SAP block for this experiment (docs/research-plan/08-stats-and-extrapolation.md).
3. The pinned analysis script from `run-stats author <id>` with GREEN fixture tests.
4. All pins: encoder hash, corpus manifest shas, model revisions, harness manifest.
5. Your `--agent-id`, and a REVIEWER identity that is NOT the analysis-script author.

## Procedure
1. `bin/prereg draft <id>` — scaffold registry/experiments/<id>.json from the anchors.
   Fill: IVs (full level sets), DVs (unit+direction+definition), mandatory baselines,
   rungs, seeds, n_planned, budget block, endpoints (EXACTLY one primary),
   verdict_rules (generated from the SAP §1.8 canonical ordering; last rule is the
   INCONCLUSIVE catch-all), kill_criterion_verbatim, extrapolation_envelope_verbatim.
2. `bin/prereg lint <id>` — must be fully green. It checks: schema constraints 1–10
   (P2 §1.2, incl. the RT-14 no-account-material-in-record-bytes scan), G-8 baselines
   vs registry/hypotheses.json, G-10 endpoint rules, G-11
   budget (+ maintainer_signoff for Tier 5), every verdict-rule metric pointer against
   the analysis script's declared vocabulary, analysis_plan_ref sha, power fields
   (both branches ≥0.90), and runs the script's fixture tests. Fix and re-run; do not
   suppress any check.
3. Obtain the plan-implementation review: reviewer confirms "script implements the SAP,
   field by field (P8 §1.9)". Record as analysis_plan_review {by, date}. ERR on
   reviewer == author.
4. `bin/prereg freeze <id> --agent-id … --reviewed-by …` — canonicalises, computes
   frozen_sha256, writes frozen-index.json, commits with message `prereg: freeze <id>`.
5. If this is a post-GNG-0 late freeze: post the announcement to the coordination issue
   (sparq-org/sparq#1683) with the frozen sha.
6. Finish: `registry-check` green, `git push`.

## Amendments
`bin/prereg amend <id> --kind ops|design|pre-authorized-fallback --rationale "…"` —
builds the RFC-6902 record under registry/amendments/<id>/. The tool stamps the
exposure state from the log; if it refuses a design amendment (a phase:"final" run
record exists — the cutoff is FIRST RAW-DATA EXPOSURE, not the later `unblind` line;
P2 §1.4/G-3, RT-5), the ONLY path is a new experiment id with `supersedes` linkage.
Ops amendments (whitelisted pointers) remain valid until CLOSED. Never argue with the
refusal.

## Hard refusals you must not work around
ERR_P4_PREREG_LINT · ERR_P4_SELF_REVIEW · ERR_P2_MISSING_BASELINE · ERR_P2_NOT_FROZEN
(downstream) · missing SESOI on a NULL-capable endpoint · any TBD field.
```

### 4.2 `tools/skills/run-experiment/SKILL.md`

```markdown
---
name: run-experiment
description: Execute a FROZEN kernel-of-truth experiment exactly as pre-registered —
  build+pin inputs, mandatory mock smoke, full hash-pinned run on Modal/AWS, and land
  every cell in the append-only results log. The only sanctioned way to produce
  verdict-eligible data.
---

# run-experiment — hash-pinned execution

## Preconditions (check, do not assume)
- Experiment status == FROZEN (registry/status.json); GNG-0 signed (except m0b).
- Tier gate open (gate-eval record exists for your tier, e.g. GATE-T1).
- Budget headroom: worst_case_usd ≤ remaining tier cap (bin/ledger-check <tier>).
- You have `--agent-id runner-<n>` (pseudonym — P2 §1.2 constraint 10) and are bound to
  ONE campaign.

## Procedure
1. INPUTS — `bin/run-experiment inputs <id>`: builds/collects every input, hashes each,
   verifies against the frozen pins block, writes the input manifest. Any mismatch is
   ERR_*; stop and triage — never "fix" a pin inline (that is a new pre-registration).
2. MOCK — `bin/run-experiment mock <id>` (skip only for R0/CPU experiments): --mock
   transport smoke of the SAME app + staged bytes (~pennies). Required same-day before
   any full GPU run (GR-13).
3. RUN — `bin/run-experiment run <id>`:
   - Materialises the RunSpec (P3 §3.2) from the frozen record; refuses on ANY
     unverifiable field (prereg hash, encoder hash, corpus shas, image id, seeds,
     timeout sizing, worst-case $).
   - Prints the kill command for this app — copy it into the session notes.
   - Launches (Modal starmap fan-out; A10G default, T4 inference-light). Cells are log
     rows, not DAG nodes; the harness asserts staged-manifest shas IN-CONTAINER.
   - Infra failures: ≤2 retries, backoff. ERR_*/scientific failures: NO retry; salvage
     to <stamp>-modal-FAILED/, file a bead, stop.
4. LOG — `bin/run-experiment log <id> <results-dir>`: one log-append line per
   arm×rung×seed cell — RAW metrics only (accuracies, counts, FLOPs via flop-meter,
   latencies, bytes; NEVER p-values/effect sizes/verdict-adjacent stats). metric_vector
   complete for efficiency_relevant experiments (G-9). Artifacts stay in
   results-incoming/ for the coordinator's DELIBERATE commit — never auto-push.
5. Finish: registry-check green; hand the campaign to X.readout (run-stats). You do NOT
   read out your own primary endpoint beyond the tool's mechanical output, and you will
   never audit this experiment (GR-6).

## Notes
- Drifted-pin runs are auto-demoted to phase:"exploratory" by log-append — they are kept
  and can never count. Do not delete them.
- If the ledger blocks you (ERR_BUDGET): stop; a cap raise is a dated ops amendment by
  the maintainer, not a retry.
```

### 4.3 `tools/skills/run-stats/SKILL.md`

```markdown
---
name: run-stats
description: The P8 statistics executor. Mode A (freeze time) — instantiate an
  experiment's SAP into a pinned, fixture-tested analysis script from the shared
  kotstats library. Mode B (readout) — execute the pre-registered readout via
  verdict-gen. Mode C — scale-extrapolation fits (a-extrap-2/5), the ONLY licensed
  source of scale statements.
---

# run-stats — pre-registered statistics, executed as written

## Mode A: author the analysis script (before freeze; feeds `prereg`)
1. `bin/run-stats author <id> --sap docs/research-plan/08-stats-and-extrapolation.md#<id>`
   Generates poc/<exp>/analyze_<id>.py which:
   - reads ONLY eligible run records on stdin (no network, no other experiments' files);
   - computes exactly the SAP's named fields into the §1.8 vocabulary
     (/gates/*, /analysis/primary_reject, effect_size + BCa CI, wilson_lb, holm/*,
     tost_equivalence_pass, seed_sign_consistent, <named-kill-terms>, slope block);
   - embeds: kotstats library sha, PRNG seeds from the frozen record, the C-7
     float64/no-prerounding declaration.
2. Write fixture tests: mock input with HAND-COMPUTED expected outputs (P2 R-4). The
   P8 §1.1 table row used for the primary test must be named in the script header with
   its justification; going outside the table requires the non-author-reviewed
   justification block.
3. Checks the tool enforces: exactly one primary; TOST margin from the §1.5 table
   present for any NULL path; conjunctions as IUT / Holm exactly where P1 says Holm;
   resampling per §1.7 (stratified within seed blocks; cluster bootstrap when
   concept-overlap >20%; selection steps INSIDE the bootstrap); power printout (§1.6,
   both branches).
4. Hand {script path, sha, output vocabulary, fixture results} to `prereg`.

## Mode B: readout (X.readout; also a-hs9/10/11, a-h0, family-h0)
1. `bin/run-stats readout <id>` — wraps tools/registry/verdict-gen: chain verify →
   amendment overlay → eligibility filter → completeness gate (missing cells ⇒
   INCOMPLETE-DATA) → pinned script in no-network sandbox → writes the `unblind` log
   line → evaluates frozen verdict_rules → emits the verdict object (PASS becomes
   PASS-PENDING-AUDIT until a CONFIRMED audit exists).
2. You may not: edit the script (sha-pinned), re-run with different seeds, add an
   endpoint, or compute ANY statistic outside the sandboxed script. Post-hoc curiosity
   goes to phase:"exploratory" via log-append — quarantined and uncitable (G-13).

## Mode C: extrapolation (a-extrap-2 sign-level; a-extrap-5 slope-level)
1. `bin/run-stats extrapolate --node a-extrap-5 --target-rung <x*>` — inputs are the
   member experiments' analysis-output.json files by pinned sha. Fits M-lin/M-pow
   (M-sat only with ≥4 rungs), WLS 1/SE², AICc selection, form-disagreement downgrade;
   reports BOTH the parametric PI and the bootstrap envelope — the wider governs.
2. Hard rules the tool enforces: ≥3 rungs for any slope (2 ⇒ sign-only; 1 ⇒ nothing);
   extrapolation ≤1 OOM past the top measured rung; anchor_class computed against the
   §2.4 table — ANCHOR-CONTRADICTING ⇒ mandatory replication before any claim;
   NO-ANCHOR ⇒ hard cap at top measured rung; the §2.5 persistence checklist is
   evaluated and attached. Output feeds verdict objects and the claims table — never
   quote a scale statement from anywhere else.
```

---

## 5. Consistency & maintenance rules

1. **One implementation per concept.** Statistics live in `kotstats` only; gate semantics in
   the shared evaluator only (S13s); write paths in the P2 tools only. A second
   implementation of any of these is a bug by definition.
2. **Skill changes are cheap; pinned material is not.** SKILL.md wording and orchestration
   may be improved any time (commit + note). The kotstats library, analysis scripts, meters
   (`poc/f0/`), and `encoder/` are pinned material: frozen experiments keep their pinned
   shas; improvements apply only to not-yet-frozen experiments; a pinned-material bug found
   post-unblinding is handled per P2 R-4 (superseding experiment id, documented).
3. **Every skill ships tests**, and `registry-check` runs in each skill's final step —
   the session-close protocol (CLAUDE.md) plus P2 §5.3 is thereby self-enforcing.
4. **Beads mirror.** Each skill build is a bead under the I-SKILLS epic (I-BEADS); a skill
   is "done" when its tests are green in CI, its SKILL.md is discoverable via
   `.claude/skills/`, and its first real consumer node has exercised it.
5. **Identity hygiene.** Skills never share `--agent-id` defaults; the auditor skill refuses
   to run under an identity present in the audited log (mechanical, not procedural).

## 6. Open decisions for the maintainer

1. **O-P4-1 (folds into O-1/GNG-0 sign-off):** approve this skill set + build order as the
   content of DAG node I-SKILLS (items 1–8 land before GNG-0 on Jul 22 — M0 per RT-18).
2. **O-P4-2:** confirm skills' canonical home `tools/skills/` with `.claude/skills/`
   symlinks (vs `.claude/skills/` as primary) — affects only discovery, not normativity.
3. **O-P4-3 (= O-5):** confirm the backup-account policy for `audit-result` on Tier ≥2
   positives and paper.review, so S6 can hard-code the identity check.
4. **O-P4-4:** approve adding the `registry-check` pre-push hook to the repo (one-line
   session-close change already mandated by P2 §5.3 — this makes it mechanical).
