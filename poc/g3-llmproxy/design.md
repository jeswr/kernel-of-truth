# g3-llmproxy — design note + pre-registration text (prereg_doc for registry/experiments/g3-llmproxy.json)

> STATUS: DESIGN (record DRAFT). STAND-IN, NOT THE ADJUDICATING STUDY. Blind
> LLM annotators fill the two-annotator g3.annotate GATE-H role so the
> semantics-pin study can produce a feasibility read now and be human-verified
> later, per the f2b-transfer-llmproxy precedent [STIPULATED: ASM-0550].
> `registry/experiments/g3.json` (frozen_sha256 ef9608c6…) is byte-untouched:
> its two independent HUMAN annotators remain the sole adjudicators of HS3
> (necessity/sufficiency of the Π pin), and every DAG consequence of a g3
> verdict (HS2 auto-resolution to sidecar-only, g5 pruning, Π demotion to
> lint) can be triggered ONLY by the human g3. Designed by FABLE (designer-1);
> execution is Opus-runner work, mechanical, post-freeze; undecided situations
> are BOUNDARY STOPS back to Fable.

## S1. Fresh id, human record untouched

DECISION: mint `g3-llmproxy`; g3 stays FROZEN-UNRUN, its annotation round and
its open run-stage decisions (annotator sourcing O-3, combination rule,
cannot-say treatment) unconsumed [STIPULATED: ASM-0550, ASM-0530]. Annotator
identity is design scope: "blind human ordinary-usage judgment" is the g3
estimand; an LLM's judgment is a different estimand and therefore a different
experiment id.

## S2. Materials and the two-pass protocol (frozen form, honoured exactly)

Items: the 200 instances of `data/instance-descriptions/`
(kot-corpus-hash/1 digest 1a55a2194f667a0f647e8cd3ce21b2c6327446b020dd24576c5263ea930d4f7d
at design time; re-pinned at freeze; instances.jsonl sha256 04cdfbfd…,
conditions.jsonl fec2bc66…, annotation-protocol.md 57610024…). Sheets are
generated mechanically per `data/instance-descriptions/annotation-protocol.md`:

- Pass A item: `text` + `target` claim, the protocol's pass-A instruction
  VERBATIM; answer `q1` ∈ {yes, no, cannot-say}.
- Pass B item: `text` + `bindings` + the enumerated condition list for the
  instance's `condition_set_id`, WITHOUT concept word/label/target, the
  protocol's pass-B instruction VERBATIM; answer
  `{q2 ∈ {yes,no,cannot-say}, q2_failing_conditions: [cid…] required when no}`.
- Derived quantities, frozen rule verbatim: necessity violation iff q1 = yes
  ∧ q2 = no; sufficiency violation iff q1 = no ∧ q2 = yes.

Contamination rule: the protocol requires all of pass A before pass B. Each
proxy judge call is a stateless single-item process (one item, one pass, no
session state), so Q1 can NEVER see a condition set — structurally stronger
than the human ordering requirement; the A-before-B run order is honoured
anyway per judge [STIPULATED: ASM-0530]. Item orders seed-pinned:
`g3lp/1|judge-<p>-<pass>|20260710` sha256 ranking.

## S3. Judge pair and why

Mirroring the frozen two-annotator design with a CROSS-FAMILY pair:

- judge-pA-gpt56sol — `gpt-5.6-sol`, effort `low`, npx-pinned
  `@openai/codex@0.144.1`, invocation form byte-derived from
  `poc/truthstyle-2x2/judges-invocation.md` §4.1 (empty out-of-repo workdir,
  ignore-user-config, memories/web-search disabled, read-only, server-side
  output schema, zero-tool tripwire, first-valid-answer-final, ≤ 3 content
  attempts then no-label).
- judge-pB-haiku45 — `claude-haiku-4-5-20251001` via headless `claude -p`
  sub-process, byte-derived from judges-invocation.md §4.3 (format-only pinned
  system prompt, `--tools ""`, `--setting-sources ""`,
  `--no-session-persistence`, MAX_THINKING_TOKENS=0, subscription auth
  asserted, per-call identity + zero-tool tripwires). The in-session
  Agent-tool sub-agent form is FORBIDDEN (project-context injection; ASM-0240
  finding, carried over). judge-pB's vendor family overlaps the materials'
  authoring agents (Fable) — DISCLOSED, FORK-2-style; it is why judge-pB is
  half of a pair and never a sole gold source [STIPULATED: ASM-0530].

A cross-family pair gives the frozen record's κ statistic real diagnostic
content (unlike the f2b single-family pair) while remaining two LLMs with
shared web-scale training exposure — κ here is judge-pair stability, never
human-agreement evidence. Blinding audit greps (per call, prompt + captured
events): `kernel`, `nsm`, `necessity`, `sufficiency`, `hypothesis` — the
judges must never see the 10% thresholds, the derived-violation rules, or
which outcome helps which hypothesis (the frozen blind-to-hypotheses arm).

## S4. Escapes, coverage, combination brackets

- cannot-say: neither violation nor satisfaction (protocol's stated
  treatment); per judge per pass, cannot-say rate ≤ 0.05 required (the
  protocol's ~5% re-examination line made mechanical, fail-closed), else
  INSTRUMENT-INVALID [STIPULATED: ASM-0533]. No-label (3 invalid content
  attempts) ≤ 5% per pass per judge.
- An instance is decisive for a judge iff its q1 AND q2 are both in {yes, no};
  dual-decisive iff decisive for both judges. n_dual_decisive ≥ 170 of 200
  required, else INSTRUMENT-INVALID (both Wilson branches stay reachable at
  170) [STIPULATED: ASM-0533].
- Combination rule (the human record left this open; the proxy PRE-DECLARES a
  two-sided bracket instead of consuming that decision): over dual-decisive
  instances, concordant count = both judges derive the violation; union count
  = either judge derives it. The PASS-analog must clear under the rule LEAST
  favourable to it (union rate Wilson UB ≤ 0.10) and the FAIL-analog likewise
  (concordant rate Wilson LB > 0.10); each verdict direction is therefore
  conservative under pre-declared bracketing [STIPULATED: ASM-0531].
- κ: computed on the per-instance necessity-violation indicator 2×2 exactly as
  `analysis/g3.py` (sha eac8fd81…); κ < 0.4 ⇒ INSTRUMENT-INVALID (frozen rule
  carried over; here it reads as judge-pair instability, never FAIL).

## S5. Instrument controls

- Probe-B (mismatched-conditions control): 30 seed-pinned instances
  (`g3lp/1|probe|20260710`, first 30) presented in pass-B form with the
  condition set of a DIFFERENT concept (seed-pinned Sattolo cycle over the 20
  condition_set_ids at concept level), original `text` + `bindings` verbatim.
  Correct answer `no` by construction (another concept's conditions, roles
  largely unbound; a content-competent judge must not mark every-condition
  satisfaction). Per judge: probe coverage ≥ 27/30 AND false-satisfaction
  (yes) rate < 0.30, else INSTRUMENT-INVALID [STIPULATED: ASM-0534]. Probes
  run after the real pass-B; never enter counts.
- Preflight per judge: 2 pinned calibration items per pass (trivially easy;
  pass-A plainly-true claim; pass-B plainly-all-satisfied condition list),
  first-attempt pass required before any real item.

## S6. Statistics, verdict, non-contamination, licensing

Wilson bounds z = 1.645 (the analysis/g3.py closed form) on necessity and
sufficiency rates under both bracket rules, over n_dual_decisive.
Verdict rules: INSTRUMENT-INVALID (gates); FAIL-analog iff concordant
necessity LB > 0.10; PASS-analog iff union necessity UB ≤ 0.10; else
INCONCLUSIVE. Secondary: the same bracket rule on sufficiency
(union UB ≤ 0.10 ⇒ `sufficiency_equivalence_survives_proxy`), per-judge rates,
escape rates, κ, probe stats, and the pass-B failing-cid histogram
(diagnostic: WHICH conditions fail — the beginnings of the failure taxonomy
the human round will need). Analysis `analysis/g3_llmproxy.py`
(PINNED-AT-FREEZE).

Non-contamination of the human round: proxy prompts render from the pinned
materials but write NOTHING under `data/instance-descriptions/`; proxy labels,
run logs and derived rates are quarantined and must never be shown to the
eventual human annotators before their sheets are submitted (ASM-0553). The
proxy consumes no g3 pin and appends nothing to g3's log.

Licensing summary (envelope is binding): PASS-analog = weak feasibility signal
that the necessity pin is not obviously dead — licenses continued investment
in the Π-pin line and human annotator sourcing; upgrades no HS2/HS3 claim.
FAIL-analog = early-warning analog of the g3 kill: pause Π-hardening
investment and escalate to the maintainer — formally scoped to this proxy id;
HS2 auto-resolution and g5 pruning can be triggered only by the human g3.
Budget: ≈ 920 calls across both judges (2 × 400 + 60 probes + preflight +
retries), Tier 0, usd_cap 15, zero GPU.
