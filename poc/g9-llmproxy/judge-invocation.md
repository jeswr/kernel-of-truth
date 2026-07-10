# g9-llmproxy — pinned judge-r1p invocation specification (the harness bytes)

> STATUS: staged 2026-07-10 by FABLE (designer-1, experiment-designer role) as
> the per-item invocation spec whose sha256 fills the DRAFT record's
> `pins.artifact_hashes["poc/g9-llmproxy/judge-invocation.md"]` BEFORE freeze
> (registry/experiments/g9-llmproxy.json; design note
> poc/g9-llmproxy/design.md). The frozen g9 record is byte-untouched. The Opus
> runner executes this spec MECHANICALLY; any situation this spec does not
> decide is a BOUNDARY STOP back to Fable, never a runner improvisation.
> Governing stipulations: ASM-0520/0521/0522/0523 (design block), ASM-0550/
> 0551/0552/0553/0554 (shared llmproxy policy), ASM-0643 (this rendering).

## 0. Pinned inputs (runner fail-closes on every one before the first call; ERR_G9P_PIN)

| artifact | path | sha256 |
|---|---|---|
| blinded review sheets (50; the ONLY item source) | `data/authored-explication-set/review/sheets.json` | `55082b1588c1c4f55b15fd07c6fbbc1b941d8fcb948de94e69b3f0e1d05b8c7c` |
| mechanical legality summary (MEASURED 50/50; composite leg) | `data/authored-explication-set/validation/mechanical-summary.json` | `a8c8ef69f8e4f4317910ab8221c6566ff931f18f2ec10a63d7b9ae177f7bf0fe` |
| prompt template (AUTHORITATIVE bytes) | `poc/g9-llmproxy/prompt-template.txt` | `c855cc3c27a1bba5b375aad6fbb060fb2ae9df6e9b1a3d759795aaad0e961916` |
| output schema (server-side, both fields) | `poc/g9-llmproxy/output-schema.json` | `f0d18c1b85cd05f6d404906ba9ce7bf0834b3a9836d44f4bd8601c03164a7543` |
| deranged-explication probe (50; NEVER in labels) | `poc/g9-llmproxy/deranged-probe.jsonl` | `c53ee4a84153456bdd421779b8cb57267f7bbe539cf4bac112640ca0775fa2a0` |
| probe + order manifest (real order, probe order, retest ids) | `poc/g9-llmproxy/deranged-probe-manifest.json` | `bd1d90d2293f6c1e58f981a09d82320e1a6a98b4450a5c19c32862bcb5577269` |
| probe builder (seed-pinned, single-draw) | `poc/g9-llmproxy/build-deranged-probe.py` | `b6db890b5a39d91aa2cbf2e4126560a4c9add51c957555fb309ccc2fbd5dfa3a` |
| calibration sheets (preflight only, expected labels inline) | `poc/g9-llmproxy/calibration-sheets.jsonl` | `0dd9ec51c0f16367652f42f6ac575b91f33b28757153f7c8d376bc8ea9d53e16` |
| pinned analysis | `analysis/g9_llmproxy.py` | `fc889af1786f1c110c6f8095457416e6a267963a514555cce04af00f369467bf` |
| this spec | `poc/g9-llmproxy/judge-invocation.md` | (pinned in the record's artifact_hashes) |

All shas re-verified against the working tree at staging time [MEASURED:
sha256sum 2026-07-10].

## 1. Judge binding

`judge-r1p-gpt56sol`: model `gpt-5.6-sol`, reasoning effort `low`, via
npx-pinned `@openai/codex@0.144.1` `exec` — the §4.1 form of
`poc/truthstyle-2x2/judges-invocation.md`, byte-derived as the frozen design
directs [STIPULATED: ASM-0551]. CROSS-VENDOR IS MANDATORY (the 50 explications
are Fable-authored; ASM-0520). The in-session Agent-tool sub-agent form is
FORBIDDEN (project-context injection; ASM-0240 finding, carried over).
`npx -y @openai/codex@0.144.1 --version` must print exactly `codex-cli
0.144.1` at preflight; the GLOBAL codex is never invoked.

## 2. Per-item prompt assembly (byte-exact; ASM-0643)

USER prompt = the bytes of `prompt-template.txt` with each `{{NAME}}` token
replaced as below, nothing else added or removed (the template's single
trailing newline stays). Two faithful runners MUST produce identical bytes.

- `{{WORD}}` — the sheet's `word` field bytes verbatim.
- `{{DEF}}` — the sheet's `def` field bytes verbatim.
- `{{EXAMPLES}}` — one line per entry of `examples`, in array order, each line
  `- ` + the entry bytes verbatim, lines joined with `\n` (no trailing `\n`).
- `{{AMBIG_EXAMPLES}}` — same rendering over `ambig_examples`.
- `{{PARAPHRASE}}` — the sheet's `candidate_explication` field bytes verbatim
  (the term of art never appears; the template says "proposed paraphrase";
  ASM-0521).

RENDERED FIELDS ARE EXACTLY THESE FIVE. `sheet_id` and `syn` are WITHHELD
(`syn` is a dictionary-source cue outside the design's enumerated sheet
fields; ASM-0643). Real items render from `sheets.json` (item id
`g9s:<sheet_id %02d>`); probe items render the SAME way from
`deranged-probe.jsonl` rows (ids `g9p:NN`); calibration sheets likewise from
`calibration-sheets.jsonl` (their `expected` object never enters any prompt).
Retest items are byte-identical re-renderings of their originals. No item id,
position, progress note, or metadata is ever added.

## 3. Item order and execution discipline

All orders are precomputed in `deranged-probe-manifest.json` (seeds verbatim:
real `g9lp/1|judge-r1p|20260710`, derangement `g9lp/1|probe|20260710`, probe
order `g9lp/1|probe-order|20260710`, retest `g9lp/1|retest|20260710`; ranking
= ascending `sha256_hex(utf8(seed + "|" + item_id))`). Execution: preflight
(§8) -> 50 real sheets in `real_order` -> 50 probes in `probe_order` -> 10
retest duplicates in `retest_ids` order. Sequential, one process per item,
concurrency 1 (the record's runner constraint). The runner writes
`judge-r1p-position-map.jsonl` (`{position, id}`, probe positions prefixed
`p`, retest prefixed `r`) to the run provenance dir before the first call.

## 4. The pinned invocation (exact command; §4.1 form)

```sh
npx -y @openai/codex@0.144.1 exec \
  -m gpt-5.6-sol \
  -c model_reasoning_effort="low" \
  -s read-only \
  --ignore-user-config \
  --skip-git-repo-check \
  --ephemeral \
  --disable memories \
  --disable standalone_web_search \
  -C "$JUDGE_WORKDIR" \
  --color never \
  --json \
  --output-schema "$REPO/poc/g9-llmproxy/output-schema.json" \
  -o "$ATTEMPT_DIR/last-message.json" \
  - < "$ATTEMPT_DIR/user-prompt.txt" \
  > "$ATTEMPT_DIR/events.jsonl" 2> "$ATTEMPT_DIR/stderr.log"
```

`$JUDGE_WORKDIR` = `mktemp -d /tmp/judger1p-workdir.XXXXXX` (verified empty,
path recorded). All fixed elements carry the judge-1p/truthstyle rationale
verbatim (empty out-of-repo workdir; user config ignored; memories + web
search disabled — this box's codex account is the GPT-5.5 auditor; read-only
sandbox + zero-tool tripwire; server-side schema; per-attempt capture).

## 5. Answer extraction and validity

The answer is `last-message.json` parsed as exactly
`{"substitutable": <token>, "cross_translatable": <token>}` (schema-
constrained). Each token must be byte-exactly one of `yes` / `no` /
`cannot-say` (the schema enum makes normalization a no-op; defense in depth:
strip ASCII whitespace, at most one trailing `.`, ASCII-lowercase, map
`cannot say` -> `cannot-say`, then require set membership — anything else
=> attempt INVALID, never repaired). A sheet is LABELLED iff both fields are
valid in one reply.

## 6. Tripwires (mechanical, fail-closed)

- Zero-tool: ZERO tool/command events in `events.jsonl` (`exec_command`,
  `terminal_interaction`, `unified_exec`, `tool_call`, `web_search`,
  `patch_apply`, `view_image`, `image_generation`, `collab_` prefixes) — any
  hit => attempt INVALID, flag `tool_use_detected`.
- Identity: version banner `codex-cli 0.144.1`; model as invoked. Mismatch
  => ABORT the pass.
- Blinding audit (per call): grep (case-insensitive) `user-prompt.txt` and
  captured `events.jsonl`/`stderr.log` for `kernel`, `nsm`, `deepnsm`,
  `baartman`, `explication` — any hit anywhere => ABORT to Fable (item
  contamination or a harness surface leaking project context; boundary
  stop). `user-prompt.txt` must equal the §2 assembly bytes exactly.

## 7. Attempt validity, retries, no-label contract

VALID iff: exit 0; §5 parse + token checks pass; §6 tripwires clean. FIRST
VALID ANSWER IS FINAL — never re-sampled, re-rolled, or "checked again"
(ASM-0241 operationalisation carried over; the §4.1 "temperature 0" discharge
applies verbatim). Transport/rate-limit failures are not content attempts:
backoff 30/60/120/300/300… s, max 10 per item, then ABORT the pass. Up to 3
CONTENT attempts per item, identical invocation bytes; after 3 invalid
attempts: NO LABEL — the sheet leaves the denominator (instrument accounting,
capped by the frozen gate: n_nolabel > 5 => INSTRUMENT-INVALID; ASM-0554);
never mapped to an answer. Run-level abort: > 5 no-label real sheets or > 5
no-label probes => ABORT and report to Fable.

## 8. Preflight (BEFORE any real item)

Both `calibration-sheets.jsonl` items (ids `cal:g9lp-1` expected yes/yes,
`cal:g9lp-2` expected no/no; trivially easy; never enter labels or any
statistic) through the EXACT §2–§7 pipeline. PASS iff both are VALID on the
first content attempt AND both fields match `expected`. Any other outcome =>
ABORT before any real item and report to Fable. Also at preflight: §0 sha
checks; workdir-empty check; `~/.claude/CLAUDE.md` must NOT exist; version
banner recorded; `preflight_pass` feeds `/gates/adjudication_valid`.

## 9. Recorded outputs

Into `data/g9-review-llmproxy/` (the corpus whose kot-corpus-hash/1 digest
fills the record's `corpus_hashes.g9-review-llmproxy` placeholder by ops
amendment AFTER the judge run and BEFORE the final-phase record; RT-14:
pseudonymous judge id `judge-r1p-gpt56sol` only):

- `judge-r1p-responses.jsonl` — one line per REAL sheet, sorted by `id`:
  `{id, substitutable, cross_translatable, flags, n_content_attempts,
  n_transport_retries, position, judge}`.
- `judge-r1p-probe-responses.jsonl` — same shape, probe items (`g9p:*`).
- `judge-r1p-retest-responses.jsonl` — same shape, retest duplicates
  (positions `r1..r10`).
- `labels-proxy.jsonl` — one line per real sheet: `{id, substitutable,
  cross_translatable, mechanical_legal (from the pinned mechanical summary),
  composite_pass (bool: legal AND both yes; cannot-say counts against),
  flags}`. These are the pinned per-sheet labels the eventual human review is
  measured against (ASM-0553); they must NEVER be shown to that reviewer.
- `summary.json` — the exact integer inputs of `analysis/g9_llmproxy.py`
  (`_rec` fields: n_sheets, n_labelled, n_nolabel, n_composite_pass_proxy,
  n_sub_yes, n_xt_yes, n_probe_labelled, n_probe_sub_yes, n_probe_xt_yes,
  n_retest_fields, n_retest_field_agree, preflight_pass,
  deepnsm_published_point_x100 = 24), version banners, workdir path, wall
  times, this spec's sha256, and the stand-in disclosure verbatim (LLM
  stand-in for the g9.review blinded-human role; WEAK FEASIBILITY PROXY).

Into `poc/g9-llmproxy/opus-runs/<TS>/` (provenance, NOT the hashed corpus):
position map, per-attempt `user-prompt.txt` / `last-message.json` /
`events.jsonl` / `stderr.log`, preflight artifacts, run log. Before commit:
the mechanical RT-14 scrub gate (grep `@` / email-like patterns ->
`[RT-14-REDACTED]` + count in the run log). The run writes NOTHING under
`data/authored-explication-set/` (ASM-0553).

## 10. What stays OUT of the judge's context

The judge sees ONE item's §2 bytes per process and nothing else, ever: never
the word "kernel" or the project name, never the reference explications or
authoring notes (withheld by the selection-manifest blinding rule, exactly as
for the human), never the probe/retest status of an item, never other items,
never this experiment's existence or stand-in status, never any margin or
threshold. Retest duplicates carry no marker of being duplicates.
