# judge-2 (GPT-5.5 via codex CLI) — pinned invocation specification

> Part of the d-adj-t instrument (design.md §4.1: judge-2 fallback = "the
> cross-vendor Codex/GPT-5.5 model via the `codex` CLI, temperature 0, pinned
> prompt stored in d-adj-t, shown ONLY the item text"). Authored by FABLE
> (design owner) to FILL the pinned-prompt/invocation placeholder referenced by
> the FROZEN protocol — bead `kernel-of-truth-67m`. Nothing in this file amends
> the frozen record `registry/experiments/f2b-transfer.json` (frozen_sha256
> f00fd28fb84f96bfbef784091b28e808681aee6bdeab50c48cb035ebcc6baa27) or
> `poc/f2b-transfer/design.md` §4 (prereg_doc sha256
> c4942eaf6c9914eb1392956a77c3ab24d1890678e869ea7cbe3f4e7b5db96c79); it
> operationalises them. The Opus runner executes this spec MECHANICALLY; any
> situation this spec does not decide is a BOUNDARY STOP back to Fable, never a
> runner improvisation.

## 0. Pinned inputs (runner fail-closes on every one; ERR_JUDGE2_PIN)

| artifact | path | sha256 |
|---|---|---|
| blind item set (360, keyed by id) | `poc/f2b-transfer/opus-runs/20260709T171156Z/blind-items-by-id.jsonl` | `ce820483336e6e25c607fa72e2591022f192d9e0eddc9a6689e02b4796af42cc` |
| pinned prompt template (AUTHORITATIVE bytes) | `data/d-adj-t/judge-2-prompt-template.txt` | `65ea3c137daa9d236b9de2bc13a94ce6b2c23f9eb845427828ee526c0452e70b` |
| output schema, MCQ items | `data/d-adj-t/judge-2-output-schema-mcq.json` | `1445fd021780dc54ec0c1cf94f5d70318f203ebe4ce8e2e4ad1a4d8a192deb38` |
| output schema, claim items | `data/d-adj-t/judge-2-output-schema-claim.json` | `3af3eaed608b712178aa4d2a627ddda7c42048f0ebef0c79600b4bee91494727` |
| calibration items (preflight only) | `data/d-adj-t/judge-2-calibration.jsonl` | `8bdb22dac8380ff834889f83b5f9bc0b9733e6446e895963cf0e084a8cffb9a1` |

Tooling pins: `codex-cli 0.142.5` (`codex --version` must print exactly this;
a different version is a BOUNDARY STOP), model `gpt-5.5` (the plain model, not
a `-codex` variant; §4.1 cross-vendor identity), reasoning effort `low`.

## 1. Per-item prompt assembly (byte-exact)

One codex invocation per item; each invocation sees the pinned prompt template
with the single placeholder line `{{ITEM}}` replaced by that ONE item's blind
rendering — §4.1's "shown ONLY the item text", §4.2's blinding (question +
option texts only; no id, no provenance, no type label ever enters the prompt).

`ITEM_RENDERING` (no trailing newline) from a `blind-items-by-id.jsonl` row:

- `format == "mcq"`:

  ```
  {question}\n
  \n
  - A) {options[A].text}\n
  - B) {options[B].text}\n
  - C) {options[C].text}\n
  - D) {options[D].text}\n
  - NONE) none of these / cannot say\n
  \n
  Allowed answers: "A", "B", "C", "D", "NONE".
  ```

- `format == "claim-yes-no"`:

  ```
  {question}\n
  \n
  Allowed answers: "yes", "no", "cannot say".
  ```

(In the blocks above `\n` marks the exact line breaks; `{question}` and option
texts are inserted verbatim, untouched — they are "the model's own rendering"
per §4.2. The `- NONE) none of these / cannot say` escape line mirrors
judge-1's `items-judge-1.md` rendering, so both judges see the same escape.)

`USER_PROMPT` = template bytes with the line `{{ITEM}}` replaced by
`ITEM_RENDERING`. Nothing else is added — no item id, no position number, no
progress note, no metadata.

## 2. Item order (§4.2 pinned shuffle)

Judge-2's pinned permutation seed is `dadjt/1|judge-2|20260710` (§4.2). The
permutation construction is the repo's canonical seeded-sort idiom — the same
one `build-judge1-package.py` and `build-dqat.py` use: sort the 360 items
ascending by `sha256_hex(utf8("dadjt/1|judge-2|20260710" + "|" + item_id))`;
positions 1..360 in that order. Items are run SEQUENTIALLY in that order (one
call at a time — box constraint friendly; per-item calls are stateless so the
order is science-neutral, but the §4.2 order is honoured and recorded).

The runner writes `judge-2-position-map.jsonl` (`{position, id}`) to the
opus-run provenance dir before the first call.

## 3. The pinned codex invocation (exact command)

For each item, with `$FMT` ∈ {mcq, claim} selected by the item's `format`:

```sh
codex exec \
  -m gpt-5.5 \
  -c model_reasoning_effort="low" \
  -s read-only \
  --ignore-user-config \
  --skip-git-repo-check \
  --ephemeral \
  --disable memories \
  --disable standalone_web_search \
  -C "$JUDGE2_WORKDIR" \
  --color never \
  --json \
  --output-schema "$REPO/data/d-adj-t/judge-2-output-schema-$FMT.json" \
  -o "$ATTEMPT_DIR/last-message.json" \
  - < "$ATTEMPT_DIR/user-prompt.txt" \
  > "$ATTEMPT_DIR/events.jsonl" 2> "$ATTEMPT_DIR/stderr.log"
```

Fixed elements, none optional:

- `$JUDGE2_WORKDIR`: a fresh EMPTY directory OUTSIDE any git repository
  (`mktemp -d /tmp/judge2-workdir.XXXXXX`), created once per run, verified
  empty before the run, path recorded in the run log. Rationale: codex
  discovers project docs (`AGENTS.md`) from its working root — the repo has an
  `AGENTS.md`, and injecting ANY project context would break §4.2 blinding /
  E5. The empty out-of-repo workdir plus `--ignore-user-config` gives the
  model no context beyond the pinned prompt.
- `--ignore-user-config`: config surface = exactly the flags above (auth still
  read from `CODEX_HOME`). No MCP servers, no user profile, no plugins config.
- `--disable memories` / `--disable standalone_web_search`: codex 0.142.5 has
  a cross-session memories feature and this box's codex has been used ON THIS
  PROJECT (it is the GPT-5.5 auditor) — injected memories would be a hard E5
  leak into a "kernel-naive" judge. Both features are default-off on this box
  (verified via `codex features list`) AND force-disabled here; the §5 event
  gate is the fail-closed backstop.
- `-s read-only` + the prompt's no-tools rule + the §5 zero-tool-use gate:
  belt, braces, and a tripwire. The judge must never read files, run
  commands, or search.
- `--ephemeral`: no session rollouts persisted into `~/.codex/sessions`.
- `--output-schema`: constrains the final message to the per-format enum —
  the machine-parseable output contract of the prompt, enforced server-side.
- `-o last-message.json`: the parsed artifact. stdout (`--json` event stream)
  and stderr are captured per attempt for the §5 gate and provenance.

## 4. "Temperature 0" — pinned operationalisation (DISCLOSED)

§4.1 commits judge-2 to temperature 0. MEASURED on the pinned tooling:
codex-cli 0.142.5 exposes NO temperature parameter (its full config-key
namespace contains no temperature key; `temperature` appears only inside MCP
protocol structs), and the `gpt-5.5` catalog entry (`codex debug models`)
exposes only reasoning-effort levels `{low, medium, high, xhigh}` — the
GPT-5.5 Responses API does not accept a sampling-temperature override for
reasoning models (vendor-fixed). No client of this model can set a literal
temperature.

The commitment is therefore discharged as the maximum-determinism
configuration the pinned interface exposes, plus a no-selection rule:

1. pinned model + pinned CLI version + pinned prompt bytes (sha-pinned §0);
2. stateless per-item calls (no shared context, no order effects);
3. `model_reasoning_effort="low"` — the LOWEST effort gpt-5.5 supports
   (catalog-verified; the fixed minimal-reasoning contract: no extended
   chain-of-thought that could rationalise toward a guessed "intended"
   answer);
4. structured-output enum (no free-text decoding surface);
5. FIRST VALID ANSWER IS FINAL — a syntactically valid, in-enum answer is
   never re-sampled, re-rolled, or "checked again" for any reason (§6), so
   residual server-side nondeterminism can never become a selection effect.

This operationalisation changes NOTHING about blinding, the escape, or
resolution. It is disclosed here, will be disclosed in every readout (§4.1's
judge-sourcing disclosure clause), and is flagged to the maintainer for
explicit ack on the coordination issue: if the maintainer reads the literal
"temperature 0" as requiring a correction record instead, that is the
maintainer's call — nothing in this file edits §4.

## 5. Attempt validity (mechanical, fail-closed)

An attempt is VALID iff ALL hold:

1. codex exit code 0;
2. `last-message.json` exists, parses as JSON, is an object with exactly one
   key `"answer"`;
3. the `"answer"` value is byte-exactly in the item's `allowed` set
   (MCQ: `A|B|C|D|NONE`; claim: `yes|no|cannot say`). No trimming, no case
   folding, no fuzzy repair — a near-miss is INVALID;
4. ZERO tool/command use in `events.jsonl`: no event whose type contains any
   of `exec_command`, `terminal_interaction`, `unified_exec`, `tool_call`
   (mcp/dynamic), `web_search`, `patch_apply`, `view_image`,
   `image_generation`, `collab_`. Any such event ⇒ the attempt is INVALID and
   flagged `tool_use_detected` (E5 tripwire: the judge acted instead of
   answering; its answer is not accepted even if in-enum).

Transport failures (nonzero exit with no model response, stream_error,
rate-limit) are NOT content attempts: retry the same item with backoff 30 s,
60 s, 120 s, 300 s, 300 s, ... up to 10 transport retries per item; then ABORT
the run (infra problem → report, don't grind).

## 6. Retry and no-label contract

- Per item: up to 3 CONTENT attempts (identical invocation bytes each time —
  the prompt is never edited per attempt). The first VALID attempt's answer is
  judge-2's label for the item, final, never revisited (§4.5 immutability +
  §4 no-resample rule).
- After 3 invalid content attempts: `answer = null`, flag
  `judge2_no_label` with the last failure reason (`parse_failure` |
  `tool_use_detected` | `refusal`). This is a JUDGE-QUALITY (instrument)
  event, never a content verdict — a refusal or malformed reply is NOT mapped
  to the escape token (the escape is a content judgement reserved for the
  model actually choosing it).
- Resolution routing for `judge2_no_label` items (mechanical completion,
  conservative under G-adj's judge-quality principle): the item counts as
  NON-agreement in the raw two-judge agreement statistic and is routed to
  judge-3 blind exactly as a discordant pair (§4.4). If judge-3 labels it,
  judge-3's label resolves; if judge-3 escapes: judge-1 also escaped ⇒
  CONTENT-UNDECIDED, judge-1 gave a label ⇒ UNRESOLVED (instrument event,
  G-adj cap). `n_judge2_nolabel` is disclosed in `summary.json` and every
  readout.
- Run-level abort: if `judge2_no_label` items exceed 18 (5% of 360), ABORT
  and report to Fable — the judge instrument is failing; do not finish a
  degenerate run. (Expected ≈ 0: the output schema enforces the enum.)

## 7. Preflight (step P — runs BEFORE any real item; small spend, within the
signed-off judge-2 envelope)

Run the two calibration items in `judge-2-calibration.jsonl` (ids `cal:*`;
trivially-easy everyday items authored for pipeline checking; NOT d-qa-t
items, NEVER enter labels.jsonl or any statistic) through the EXACT §1–§6
pipeline. Preflight PASSES iff both attempts are VALID on the first content
attempt AND each parsed answer equals the item's `expected` field. Any other
outcome (auth failure, schema flag rejected, effort rejected, wrong answer on
a trivial item, tool use) ⇒ ABORT before any real item and report to Fable.
Preflight artifacts are kept in the opus-run dir, clearly separated from
instrument outputs.

## 8. Recorded outputs

Into `data/d-adj-t/` (hashed corpus; RT-14: pseudonym "judge-2" only, no
names/emails/accounts anywhere in these bytes):

- `judge-2-responses.jsonl` — one line per real item, sorted by `id`, exactly:
  `{"answer": <token-or-null>, "flags": [...], "format": "mcq"|"claim-yes-no",
  "id": "...", "judge": "judge-2", "last_message_sha256": <hex-or-null>,
  "n_content_attempts": <int>, "n_transport_retries": <int>,
  "position": <int>}` (JSON sorted keys, ensure_ascii=false — repo jsonl
  idiom). This is judge-2's "per-judge raw response file" per design.md §3.2.
- (already present) `judge-2-prompt-template.txt`, the two schema files,
  `judge-2-calibration.jsonl`, `judge-2-prompt.md`, this file — the §4.1
  "pinned prompt stored in d-adj-t".

Into `poc/f2b-transfer/opus-runs/<TS>/` (provenance, NOT the hashed corpus):
`judge-2-position-map.jsonl`, per-attempt `user-prompt.txt` /
`last-message.json` / `events.jsonl` / `stderr.log`, preflight artifacts, run
log (workdir path, `codex --version`, wall times, token counts from
`token_count` events, transport-retry tally). Before commit, a mechanical
RT-14 scrub gate greps every provenance file for `@` and email-like patterns;
matching lines are replaced by `[RT-14-REDACTED]` with a count in the run log.

Judge sourcing disclosure (§4.1): d-adj-t's `summary.json` (assembled later
with labels) must record judge-2 = LLM fallback, model `gpt-5.5`,
codex-cli 0.142.5, effort `low`, this spec's sha256, and `n_judge2_nolabel`.

## 9. What stays OUT of judge-2's context (blinding audit list)

Never in any prompt byte: item ids, ranks, types, urns, record paths,
membership gold, the word "kernel", the project name, §4's own text, the
existence of judge-1/judge-3, endorsement/agreement statistics, counts of
MCQ-vs-claim items, or the fact that options are machine-rendered from
records. (Judge-1's human package mentions "kernel records" in its
eligibility self-certification; judge-2 needs no self-certification — its
kernel-naivety is enforced by vendor choice (E5) and by this context control,
and §4.1 itself pins judge-2 to "ONLY the item text" plus the pinned prompt.
The ADJUDICATION rules — own-competence answering, the genuine escape, the
plain-style note, no lookups — are mirrored verbatim-in-substance from
judge-1's README, so both judges answer under the SAME protocol.)
