# judge-1p (GPT-5.6-Sol via codex CLI) — pinned invocation specification

> The judge-1 STAND-IN instrument of `f2b-transfer-llmproxy` (registry record
> `registry/experiments/f2b-transfer-llmproxy.json`; design note
> `poc/f2b-transfer/llmproxy-design.md`). Authored by FABLE (design owner;
> design-vs-judge separation: the judged model contributed NOTHING to this
> protocol). This spec fills the judge-1 ROLE of the f2b-transfer §4 protocol
> with a pinned LLM for the clearly-labelled stand-in experiment ONLY — it
> does not amend the FROZEN `registry/experiments/f2b-transfer.json`
> (frozen_sha256 b341a0901e12023d3c56bdc196be0b9c492c7d348f988416d7e9c43aade20879),
> whose human judge-1 path stays open and solely adjudicating. The Opus
> runner executes this spec MECHANICALLY; any situation this spec does not
> decide is a BOUNDARY STOP back to Fable, never a runner improvisation.

## 0. Pinned inputs (runner fail-closes on every one; ERR_JUDGE1P_PIN)

| artifact | path | sha256 |
|---|---|---|
| blind item set (360, keyed by id; BYTE-IDENTICAL to judge-2's) | `poc/f2b-transfer/opus-runs/20260709T171156Z/blind-items-by-id.jsonl` | `ce820483336e6e25c607fa72e2591022f192d9e0eddc9a6689e02b4796af42cc` |
| deranged-probe set (60, keyed by id; instrument control, NEVER in labels) | `data/d-adj-t-llmproxy/deranged-probe.jsonl` | `4479c6192c1830ef5eb3b75f564efef2114e369f5125786e95e9e79f27687e9c` |
| pinned prompt template (AUTHORITATIVE bytes) | `data/d-adj-t-llmproxy/judge-1p-prompt-template.txt` | `19b029991f1dc0cb031192db45f397c3a171ec701488817f181827c0101d2d1e` |
| output schema, MCQ items (reused, judge-agnostic) | `data/d-adj-t/judge-2-output-schema-mcq.json` | `1445fd021780dc54ec0c1cf94f5d70318f203ebe4ce8e2e4ad1a4d8a192deb38` |
| output schema, claim items (reused) | `data/d-adj-t/judge-2-output-schema-claim.json` | `3af3eaed608b712178aa4d2a627ddda7c42048f0ebef0c79600b4bee91494727` |
| calibration items (preflight only, reused) | `data/d-adj-t/judge-2-calibration.jsonl` | `8bdb22dac8380ff834889f83b5f9bc0b9733e6446e895963cf0e084a8cffb9a1` |

The prompt template is the judge-2 template with EXACTLY line 1 changed
("You are judge-2, an independent judge…" → "You are an independent judge…"):
the panel-position pseudonym is removed from the judge's own context (a §4.9
blinding improvement — the judge learns nothing about a panel existing); every
other byte, including the §4.7-derived judging standards, is identical, so
judge-1p, judge-2, and (later) the human judge-1 all answer under the SAME
protocol.

Tooling pins: `npx -y @openai/codex@0.144.1` (version-pinned npx invocation;
`npx -y @openai/codex@0.144.1 --version` must print exactly `codex-cli
0.144.1`), model **`gpt-5.6-sol`** (the catalog slug of GPT-5.6 "sol"),
reasoning effort `low`.

**Why npx-pinned, not the global codex** (MEASURED, designer capability check
2026-07-09, scratchpad `gpt56-check/`): the global `codex-cli 0.142.5` has no
`gpt-5.6*` catalog entry and a hardened exec call with `-m gpt-5.6` fails
(HTTP 400 "The 'gpt-5.6' model is not supported when using Codex with a
ChatGPT account", exit 1). Under `@openai/codex@0.144.1` the catalog lists
`gpt-5.6-sol` (efforts low/medium/high/xhigh/max/ultra, DEFAULT low) plus
`gpt-5.6-terra` / `gpt-5.6-luna`, and the exact §3 command below succeeded
end-to-end (exit 0, schema-constrained `{"answer":"A"}` on a trivial MCQ,
zero tool events). OPERATIONAL CONSTRAINT: the in-flight f2b-transfer judge-2
run is pinned to the GLOBAL `codex-cli 0.142.5` — the global install MUST NOT
be upgraded until that run completes; the npx pin was verified to leave the
global binary untouched (`codex --version` still prints 0.142.5).

## 1. Per-item prompt assembly (byte-exact)

Identical to `data/d-adj-t/judge-2-invocation.md` §1 with the judge-1p
template substituted: one codex invocation per item; `USER_PROMPT` = template
bytes with the single `{{ITEM}}` line replaced by the item's blind rendering
(same MCQ / claim-yes-no blocks, same `- NONE) none of these / cannot say`
escape line). Nothing else is ever added — no item id, no position number, no
progress note, no metadata, and (blinding audit list, judge-2 spec §9) never
the word "kernel", the project name, provenance, membership gold, or the
existence of other judges. Probe items render through the EXACT same MCQ
block (their rows are shaped identically to blind item rows).

## 2. Item order (the judge-1 ROLE's pinned shuffle, §4.2)

Real items: the frozen §4.2 seed for the judge-1 ROLE, verbatim
**`dadjt/1|judge-1|20260710`** — sort the 360 ids ascending by
`sha256_hex(utf8(seed + "|" + item_id))`; positions 1..360; run SEQUENTIALLY.
(Per-item calls are stateless — fresh process, `--ephemeral`, memories
disabled — so order is science-neutral; the role's pinned order is honoured
and recorded. The identity filling the role is recorded as pseudonym
**judge-1p**, never as judge-1, so no artifact of this run can be confused
with the human judge-1's.)

Probe items: run AFTER position 360, as their own block (a probe failure can
never disturb the real-item run), in the pinned order
**`dadjt/1|judge-1p-probe|20260711`** (same construction; positions p1..p60,
precomputed in `deranged-probe-manifest.json` `run_position`).

The runner writes `judge-1p-position-map.jsonl` (`{position, id}`, probe
positions prefixed `p`) to the opus-run provenance dir before the first call.

## 3. The pinned codex invocation (exact command; VERIFIED 2026-07-09)

For each item, with `$FMT` ∈ {mcq, claim} selected by the item's `format`
(probe items are always mcq):

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
  -C "$JUDGE1P_WORKDIR" \
  --color never \
  --json \
  --output-schema "$REPO/data/d-adj-t/judge-2-output-schema-$FMT.json" \
  -o "$ATTEMPT_DIR/last-message.json" \
  - < "$ATTEMPT_DIR/user-prompt.txt" \
  > "$ATTEMPT_DIR/events.jsonl" 2> "$ATTEMPT_DIR/stderr.log"
```

Fixed elements — all carried over from the judge-2 spec §3 with identical
rationale (empty out-of-repo `$JUDGE1P_WORKDIR` via
`mktemp -d /tmp/judge1p-workdir.XXXXXX`, verified empty, path recorded;
`--ignore-user-config`; both feature disables — this box's codex account has
been used ON THIS PROJECT as the GPT-5.5 auditor, so injected memories would
be a hard E5 leak; `-s read-only` + prompt no-tools rule + the §5
zero-tool-use tripwire; `--ephemeral`; server-side `--output-schema` enum;
stdout/stderr captured per attempt). E5 kernel-instance-naivety is enforced
by context control exactly as for judge-2; the envelope discloses that no
GPT-5.x model is kernel-TRADITION-naive (NSM literature in training data) —
that residual is bounded by the deranged-probe gate, not by this spec.

## 4. "Temperature 0" — pinned operationalisation (DISCLOSED)

Carried over from the judge-2 spec §4, re-verified on the pinned tooling:
codex-cli 0.144.1 exposes no temperature parameter for reasoning models; the
`gpt-5.6-sol` catalog entry exposes only reasoning-effort levels
`{low, medium, high, xhigh, max, ultra}` (MEASURED, `codex debug models`
under 0.144.1). The commitment is discharged as maximum determinism the
interface exposes: (1) pinned model + pinned CLI version + pinned prompt
bytes; (2) stateless per-item calls; (3) `model_reasoning_effort="low"` — the
lowest level, which is also gpt-5.6-sol's catalog DEFAULT (the fixed
minimal-reasoning contract: no extended chain-of-thought rationalising toward
a guessed "intended" answer); (4) structured-output enum; (5) FIRST VALID
ANSWER IS FINAL — never re-sampled, re-rolled, or "checked again", so
residual server-side nondeterminism can never become a selection effect.

## 5. Attempt validity (mechanical, fail-closed)

Identical to the judge-2 spec §5: VALID iff exit 0; `last-message.json`
parses to exactly `{"answer": <token>}`; token byte-exactly in the item's
allowed set (no trimming/case-folding/fuzzy repair); ZERO tool/command events
in `events.jsonl` (`exec_command`, `terminal_interaction`, `unified_exec`,
`tool_call`, `web_search`, `patch_apply`, `view_image`, `image_generation`,
`collab_` → INVALID, flag `tool_use_detected`). Transport failures are not
content attempts: backoff 30/60/120/300/300… s, max 10 per item, then ABORT.

## 6. Retry and no-label contract

Identical to the judge-2 spec §6 EXCEPT resolution routing (this design has
NO judge-3 — see the design note §4: the maintainer tie-break instrument is
deliberately left uncontaminated for the human f2b-transfer round):

- up to 3 CONTENT attempts per item, identical invocation bytes; first VALID
  answer is final.
- after 3 invalid attempts: `answer = null`, flag `judge1p_no_label` with the
  last failure reason. A no-label is a JUDGE-QUALITY instrument event: the
  item leaves the A_1p denominator, `n_nolabel_j1p` counts it, and the gate
  caps it (> 18 of 360 ⇒ INSTRUMENT-INVALID). It is NEVER mapped to the
  escape token. No-label PROBE items likewise leave the probe denominator
  (`n_probe_labelled`; < 54 ⇒ probe gate fails).
- run-level abort: > 18 no-label real items (5% of 360) or > 6 no-label probe
  items ⇒ ABORT and report to Fable; do not finish a degenerate run.

## 7. Preflight (step P — BEFORE any real item)

Both `data/d-adj-t/judge-2-calibration.jsonl` items (ids `cal:*`; trivially
easy; never enter labels or any statistic) through the EXACT §1–§6 pipeline.
PASS iff both are VALID on the first content attempt AND match their
`expected` fields. Any other outcome (auth failure, model/flag rejected,
schema rejected, wrong answer, tool use) ⇒ ABORT before any real item and
report to Fable. `preflight_pass` is carried into the stage-1 record and is
part of the pre-registered `/gates/adjudication_valid`.

## 8. Recorded outputs

Into `data/d-adj-t-llmproxy/` (hashed corpus; RT-14: pseudonym "judge-1p"
only — no names/emails/accounts anywhere in these bytes):

- `judge-1p-responses.jsonl` — one line per REAL item, sorted by `id`, same
  row shape as judge-2's (`answer`, `flags`, `format`, `id`,
  `judge: "judge-1p"`, `last_message_sha256`, `n_content_attempts`,
  `n_transport_retries`, `position`).
- `judge-1p-probe-responses.jsonl` — same shape, probe items only, positions
  `p1..p60`. NEVER merged into labels or endorsement statistics.
- `labels-proxy.jsonl` — one line per real item: `{id, label_j1p,
  agree_membership (bool), escape (bool), j2_answer (diagnostic),
  pair_token_equal (bool|null), flags}`. Gold source is judge-1p ALONE.
- `summary.json` — the exact integer inputs of the pinned analysis
  (`analysis/f2b_transfer_llmproxy.py` selftest `_rec` fields), plus judge
  sourcing disclosure: judge-1p = LLM STAND-IN for the judge-1 role, model
  `gpt-5.6-sol`, `codex-cli 0.144.1` via pinned npx, effort `low`, this
  spec's sha256, `n_judge1p_nolabel`, and the verbatim note that judge-2
  (GPT-5.5) is DIAGNOSTIC-ONLY here and that the two judges are one model
  family (no independent validation).

Into `poc/f2b-transfer/opus-runs/<TS>/` (provenance, NOT the hashed corpus):
position maps, per-attempt `user-prompt.txt` / `last-message.json` /
`events.jsonl` / `stderr.log`, preflight artifacts, run log (workdir path,
`npx … --version` output, wall times, `token_count` events, transport tally).
Before commit: the mechanical RT-14 scrub gate (grep `@` / email-like
patterns → `[RT-14-REDACTED]` + count in the run log).

`judge-2-responses.jsonl` is NOT produced here: it is the in-flight
f2b-transfer instrument's output, committed to `data/d-adj-t/` under its own
spec; this experiment READS it (post-completion, ops-amended pin) to compute
the diagnostic/gate fields `judge_pairs_*`, `n_labelled_j2`, `n_agree_j2`,
`panel_*`.

## 9. What stays OUT of judge-1p's context (blinding audit list)

Byte-identical policy to the judge-2 spec §9, plus: the existence of the
probe, of judge-2/judge-3, of f2b-transfer, and of this experiment's
stand-in status are never in any prompt byte. The judge sees 420
independently-rendered items and nothing else, ever.
