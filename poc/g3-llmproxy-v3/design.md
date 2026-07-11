# g3-llmproxy-v3 — design note + pre-registration text (prereg_doc for registry/experiments/g3-llmproxy-v3.json; SUPERSEDES g3-llmproxy-v2)

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

## S0-V3. Supersession delta (the ONLY changes from the superseded g3-llmproxy-v2)

The frozen g3-llmproxy-v2 (frozen_sha256 5c8002b3b52d0641b28ca4aee7ab243a78
cca40f111264a043253da1f33cb885) ABORTED at run time on a §6 blinding FALSE
POSITIVE: during pass-A, the pinned v2 §6 contract — a case-insensitive grep
of the WHOLE `user-prompt.txt`/`events.jsonl`/`stderr.log` for the five
blind tokens, any hit anywhere => ABORT — fired on the trigram `nsM` inside
the Anthropic-generated API identifier
`"request_id":"req_011Ccu3G1KQZ8ciX3SvEfnsM"` at offset 2242 of the
judge-pB events.jsonl for pass-A item g3-friend-07 (position ~40 of 200)
[MEASURED: poc/g3-llmproxy-v2/opus-runs/20260710T204828Z/judge-pB-haiku45/
run-log.txt + passA/g3-friend-07/c1_t0/events.jsonl]. The matched bytes are
machinery metadata, NOT semantic leakage: `user-prompt.txt` is byte-clean
(0 hits), `stderr.log` is empty, the judge's answer text is clean, and the
judge never saw the token — the id is stamped by the harness AFTER the model
answers. Every captured judge-pB attempt carries exactly TWO such base62
identifiers (24-character mixed-case tails; judge-pA/codex captures carry
none) [MEASURED: id census over all 131 captured attempts of
20260710T204828Z], so `nsm` occurs inside a tail by arithmetic coincidence
with expectation ≈ 22 windows × (2/62)³ × 2 ids ≈ 1.5e-3 per judge-pB call —
≈ 0.6 expected hits per perfectly blind 430-call judge-pB run, i.e. the
unamended scan aborts a CLEAN run with probability ≈ 0.5 under the null
(observed: died once, at call ~40). A blinding control that fires on vendor
machinery under the null detects nothing. This is byte-for-byte the
coincidence class the ratified truthstyle-2x2 Amendment A1 closed
(registry/corrections/truthstyle-2x2/4-blinding-audit-amendment-a1.json;
poc/truthstyle-2x2/blinding-audit-clarification.md §9; ASM-0660): there,
`nsm` inside `req_011Cctc1sK9P4SujinnsMiWU` at judge-p3 pos-102. The frozen
v2 record is immutable, therefore this fresh superseding id.

DECISION (blinding-scan-scope robustness fix ONLY, carried on TOP of v2's
fence fix; same design, estimand, brackets, gates, verdict rules, budget,
blinding channels) [STIPULATED: ASM-0740]:

1. The §6 blinding audit adopts the A1 rule IN ITS EXACT FORM: on the two
   HARNESS-CAPTURED surfaces `events.jsonl` and `stderr.log` — and NEVER on
   `user-prompt.txt` — a case-insensitive token match is excluded from being
   a HIT iff, in the original pre-lowercase bytes, it lies wholly inside the
   base62 TAIL of a maximal Anthropic-format vendor identifier literal
   `(req|msg)_[0-9A-Za-z]{20,48}` with lowercase-exact prefix and
   non-word-adjacent boundaries (a run longer than 48 fails maximality and
   is NOT excluded — fail-closed). Uniform over all five tokens; every byte
   outside qualifying tails is scanned byte-identically to v2.
2. ANSWER-SURFACE STRICTNESS (a strengthening, not a relaxation): the §5 RAW
   answer string — the judge-emitted bytes — is additionally re-scanned with
   ZERO exclusions, so a real leak in what the judge SAID aborts even when
   id-shaped. This closes, for the answer channel, the residual-risk shape
   A1 §9.6 could only disclose. It cannot false-positive: the valid answer
   grammar (`{"q1"|"q2": yes/no/cannot-say, "q2_failing_conditions":
   ["cN"…]}`) contains no base62 identifiers, and any answer carrying one is
   content-suspect by construction.
3. REFERENCE IMPLEMENTATION: `blinding_scan()` / `_vendor_id_tail_spans()` /
   `answer_blinding_hit()` in the pinned `analysis/g3_llmproxy_v3.py`
   (adapted from the A1 §9.5 normative code; g3's five tokens all contain
   non-hex letters, so the truthstyle hex-run branch has no g3 analogue).
   The runner scans through it, never a reimplementation (boundary stop).
4. Preflight (spec §8) extends the runner-local self-check `cal:g3lp-x1`:
   `python3 analysis/g3_llmproxy_v3.py --selftest` now also proves (a) the
   EXACT v2-abort bytes (the g3-friend-07 request_id byte neighbourhood,
   verbatim slice) are EXCLUDED on the captured surface, and (b) real-leak
   shapes — token in item bytes, in judge-emitted answer text, delimited
   stderr spellings, malformed/oversized/embedded id lookalikes — all still
   ABORT. The carried v1-defect fence fixtures (ASM-0650) remain.

Leak-safety (the A1 §9.4 argument, which this design adopts): item
contamination fires byte-identically to v2 (`user-prompt.txt` untouched by
the exclusion, and §2-assembly byte-equality is separately required); every
project spelling of the tokens contains delimiters or casing/format that
fail the anchored id shape; a judge ECHOING a token emits it in a
result/content block, which is never inside a qualifying id tail — and the
strict answer-surface scan backstops even the id-shaped echo. Rejected
alternatives (rejected for the A1 §9.4 reasons, verbatim class): dropping
id fields from the scan surface (strictly larger blind spot; requires
parsing non-JSON surfaces); scrubbing ids from provenance (destroys
re-derivability — the auditor must be able to re-run strict, v2-form, and
v3-form scans over the SAME retained bytes); changing the pinned §4
capture form (inverts the control hierarchy for a detector-side false
positive).

DECISION (custody) [STIPULATED: ASM-0741]: unchanged artifacts are carried
at their existing v1/v2 paths and sha256 pins (`poc/g3-llmproxy/` templates,
schemas, pass-A system prompt, probe set + manifest + builder, calibration
items; `poc/g3-llmproxy-v2/judge-pB-system-prompt-pass-b.txt` — the v2
fence-hardened pass-B prompt, byte-identical; `data/instance-descriptions/`);
only the changed artifacts get v3 paths (judge-invocation spec, analysis
script, this prereg doc). Outputs land in the DISJOINT corpus
`data/g3-annot-llmproxy-v3/` and provenance in
`poc/g3-llmproxy-v3/opus-runs/<TS>/`; the superseded records'
`g3-annot-llmproxy` and `g3-annot-llmproxy-v2` corpus placeholders stay
unfilled forever. The aborted v2 run's provenance is retained read-only as
defect evidence, its g3-friend-07 vendor-id bytes NOT scrubbed (under the
amended rule they are a listed, auditor-inspectable exclusion; the v3-form
sweep over all 131 retained v2 attempts is GREEN — strict scan: exactly the
one g3-friend-07 hit; amended scan: zero hits [MEASURED: sweep 2026-07-10]).
Nothing from the aborted run is reused — v3 re-runs both judges' both passes
in full from preflight. No selection effect, with one disclosure: no v2
label file was ever assembled or written (responses are written only at pass
END, and no pass ended); during the boundary-stop diagnosis the mechanical
runner's log displayed per-item q1 fields for the ~40 processed pass-A items
and the coordinator read the abort context (one request_id literal). Those
void partials are discarded, enter no statistic, and the re-run decision
criterion (detector false positive on machinery metadata) is structural, not
outcome-dependent; first-valid-answer-final bars outcome-conditioned
re-rolls. All governing stipulations carry over verbatim (ASM-0530–0534,
ASM-0550–0554, ASM-0642, ASM-0644 incl. the mandatory per-call
init.tools==[] hard gate, ASM-0650/0651 — the v2 fence fix and custody,
carried).

## S0-V2. Carried supersession delta (v1 -> v2, byte-carried into this design)

The frozen g3-llmproxy (frozen_sha256 a50710609fe41d2b2b185400f95ee31594ef49
f5575b331c1976f923b531c2b8) ABORTED at run time on its own section-7 gate:
judge-pB (claude-haiku-4-5 headless) systematically wrapped its two-field
pass-B answer object in a ```json markdown code fence (~92% of attempted real
pass-B items, 24/26 before the >10-no-label abort; run-log parse_fail
captures, `poc/g3-llmproxy/opus-runs/20260710T194903Z/judge-pB-haiku45/`)
[MEASURED: run-log.txt, 20260710T194903Z]. The v1 section-5 contract accepted
only a bare JSON object, so every fenced answer was a parse_fail; the model's
own preflight calibration answers were unfenced, so the defect could not
surface before real items. judge-pA (server-side output schema) was
unaffected; pass-A completed 200/200 for both judges.

DECISION (pass-B output-handling robustness fix, CARRIED VERBATIM into v3)
[STIPULATED: ASM-0650]:

1. The judge-pB pass-B format-only system prompt EXPLICITLY requires a
   bare raw `{...}` object — no markdown code fence, no ``` characters, no
   language tag, no prose
   (`poc/g3-llmproxy-v2/judge-pB-system-prompt-pass-b.txt`, carried
   byte-identical at its v2 path + pin).
2. The section-5 extraction contract carries a uniform, content-blind FENCE
   NORMALIZATION (strip ASCII whitespace; remove exactly one ```-fence layer
   with optional language tag when the string both starts and ends with ```;
   re-strip; single layer only) applied to the raw answer string BEFORE
   `json.loads`, for both judges and all passes. Reference implementation:
   `extract_answer_object()` / `normalize_token()` in the pinned
   `analysis/g3_llmproxy_v3.py`; the runner labels through it, never a
   reimplementation. Format normalization in the same class as the existing
   whitespace/trailing-period token normalization — never answer repair;
   first-valid-answer-final and the ≤3-content-attempt/no-label accounting
   are unchanged.
3. Preflight (S5/spec section 8) requires the runner-local extraction
   self-check `cal:g3lp-x1` — the pinned `--selftest` must pass; its
   fixtures include the EXACT fenced defect bytes from the aborted v1 run —
   BEFORE any judge call (a model-side calibration item cannot force a
   fence, as the v1 abort proved).

READ-THROUGH RULE for S1–S6 below (byte-identical to the superseded v2
prereg sections, sha256 2440832ee02238df59bd4450110daa446cba38ce7f8d1ddd4f0c
db7ad705858c for the whole superseded doc, except this rule): every occurrence
of `analysis/g3_llmproxy.py` or `analysis/g3_llmproxy_v2.py` reads as
`analysis/g3_llmproxy_v3.py`, of
`poc/g3-llmproxy/judge-pB-system-prompt-pass-b.txt` as
`poc/g3-llmproxy-v2/judge-pB-system-prompt-pass-b.txt` (the carried v2
hardened prompt), of `poc/g3-llmproxy/judge-invocation.md` or
`poc/g3-llmproxy-v2/judge-invocation.md` as
`poc/g3-llmproxy-v3/judge-invocation.md`, and of `data/g3-annot-llmproxy`
or `data/g3-annot-llmproxy-v2` as `data/g3-annot-llmproxy-v3`; every other
pinned path and byte is shared with the superseded records verbatim.

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
human-agreement evidence. Blinding audit (per call, prompt + captured
events + stderr + the raw answer string): tokens `kernel`, `nsm`,
`necessity`, `sufficiency`, `hypothesis` under the S0-V3 scan-scope rule
(ASM-0740) — the judges must never see the 10% thresholds, the
derived-violation rules, or which outcome helps which hypothesis (the frozen
blind-to-hypotheses arm).

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
  first-attempt pass required before any real item — preceded once per run
  by the runner-local `cal:g3lp-x1` extraction + blinding-scan self-check
  (S0-V3 item 4).

## S6. Statistics, verdict, non-contamination, licensing

Wilson bounds z = 1.645 (the analysis/g3.py closed form) on necessity and
sufficiency rates under both bracket rules, over n_dual_decisive.
Verdict rules: INSTRUMENT-INVALID (gates); FAIL-analog iff concordant
necessity LB > 0.10; PASS-analog iff union necessity UB ≤ 0.10; else
INCONCLUSIVE. Secondary: the same bracket rule on sufficiency
(union UB ≤ 0.10 ⇒ `sufficiency_equivalence_survives_proxy`), per-judge rates,
escape rates, κ, probe stats, and the pass-B failing-cid histogram
(diagnostic: WHICH conditions fail — the beginnings of the failure taxonomy
the human round will need). Analysis `analysis/g3_llmproxy_v3.py`
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
