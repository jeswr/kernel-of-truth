# truthstyle-2x2 — pinned 3-judge invocation specification (the harness_manifest bytes)

> STATUS: staged 2026-07-10 by FABLE (designer-1, experiment-designer role) as the
> per-judge invocation spec that fills the FROZEN record's `pins.harness_manifest`
> PINNED-AT-INPUTS placeholder via ops amendment
> (`registry/amendments/truthstyle-2x2/1-pin-harness-manifest.json`), BEFORE any
> adjudication call, per the frozen `design.n_planned.adjudication_protocol`.
> The frozen record `registry/experiments/truthstyle-2x2.json` (frozen_sha256
> `18893369a1206614ade399bfbdf33f7952f3a6b3460f1edc4193b8f13db71d74`) is
> byte-untouched. The Opus runner executes this spec MECHANICALLY; any situation
> this spec does not decide is a BOUNDARY STOP back to Fable, never a runner
> improvisation. Governing stipulations: ASM-0240 (judge-p3 operationalization),
> ASM-0241 (temperature-0 discharge), ASM-0242 (order seeds + normalization).

## 0. Pinned inputs (runner fail-closes on every one before the first call; ERR_DTS_PIN)

| artifact | path | sha256 |
|---|---|---|
| d-ts items (808, question bytes are the ONLY prompt content) | `data/d-ts/items.jsonl` | `9194f61713cc6cf01c34fa1ca97e01cd25b6b6d8c3bbae7db9a1772ac0c57a2d` |
| d-ts manifest | `data/d-ts/manifest.json` | `9fc7abbf25c871fb5ba66e18aa4e9c4c8dab1f339eb7be76749127341d88c600` |
| deterministic builder (frozen parenthetical pin) | `poc/truthstyle-2x2/build-dts.py` | `1edb96f46e726c5a961b042810a0ebcfdfc3be9a44547f50bb75861ee19d2849` |
| style rules (frozen parenthetical pin) | `poc/truthstyle-2x2/style-rules.json` | `b65837d4a1915a85b7632391e1b368398c9c79f7e3490e585d781e7d3478c902` |
| pinned analysis (frozen) | `analysis/truthstyle_2x2.py` | `bf171ed951c2100e0a768c9ecea571da604e912a08164e2dd563e103f1c071c8` |
| judge-p1/p2 output schema (server-side enum) | `poc/truthstyle-2x2/output-schema-dts.json` | `90d17f640c970d233d6b4addf90f0f331637802d9a27f974bb8e5c4d94206a5d` |
| judge-p3 system prompt (byte-exact) | `poc/truthstyle-2x2/judge-p3-system-prompt.txt` | `21f090ae004e3745640c0a88fc820265a610628bb538a72a6d2ad8a425914db8` |
| this spec | `poc/truthstyle-2x2/judges-invocation.md` | (pinned inside `poc/truthstyle-2x2/harness-manifest.json`) |

All shas above were re-verified against the working tree at staging time
[MEASURED: sha256sum 2026-07-10; identical to the frozen record / prereg §2 pins].

## 1. Judge pool (frozen §3.2; exact bindings pinned here)

| judge id (labels.jsonl `judge` field, byte-exact) | model | interface |
|---|---|---|
| `judge-p1-gpt56sol` | `gpt-5.6-sol`, reasoning effort `low` | `npx -y @openai/codex@0.144.1` (§4.1) |
| `judge-p2-gpt55` | `gpt-5.5`, reasoning effort `low` | `npx -y @openai/codex@0.144.1` (§4.2) |
| `judge-p3-haiku45` | `claude-haiku-4-5-20251001` | headless Claude Code sub-process, `claude -p` (§4.3) |

- `gpt-5.5` is the catalog slug under codex-cli 0.144.1 [MEASURED 2026-07-10:
  `npx -y @openai/codex@0.144.1 debug models` lists slug `gpt-5.5`, efforts
  {low, medium, high, xhigh}, default medium; the GLOBAL codex install printed
  `codex-cli 0.142.5` before AND after the npx runs — untouched, per the frozen
  runner constraint]. Effort `low` for both codex judges [STIPULATED: ASM-0241 —
  the fixed minimal-reasoning contract of the judge-1p form the frozen record
  cites for judge-p1; uniform across the family].
- `claude-haiku-4-5-20251001` is the exact model id actually served
  [MEASURED 2026-07-10: three staging probes; `modelUsage` key and stream-json
  init `model` field both read `claude-haiku-4-5-20251001`; claude-code 2.1.201;
  `apiKeySource:"none"` — subscription auth, NO Anthropic API key, per the
  maintainer ruling of 2026-07-10]. Designer-family caveat disclosed (FORK-2,
  frozen record): the judge labels are raw DATA graded by the pinned pure
  function `analysis/truthstyle_2x2.py`; the cross-vendor AUDITOR remains Codex.

## 2. Per-item prompt assembly (byte-exact)

USER prompt = the item's `question` field bytes VERBATIM, nothing else — the
frozen stem already carries the S1 fit+identification question, the S6
register-immunity instruction, and the mandatory `yes / no / cannot-say`
answer line. Nothing is ever added: no item id, no position, no progress note,
no metadata, and never (blinding audit list, §7.3) the word "kernel", the
project name, tier/truth/style/donor/provenance, or the existence of other
judges. The runner writes the bytes to `"$ATTEMPT_DIR/user-prompt.txt"` (no
added trailing newline beyond the field bytes) and delivers them on stdin.

Judge-p3 additionally receives the pinned system prompt
`judge-p3-system-prompt.txt` (format-enforcement ONLY — it adds no judging
standard; the judging standards live in the question bytes, identical across
judges). This is the p3 analog of the codex judges' server-side
`--output-schema` enum and of codex's own fixed base instructions
[STIPULATED: ASM-0240 — every judge runs inside some vendor harness wrapper;
p3's wrapper is the one we can pin byte-exactly].

## 3. Item order and execution discipline (frozen seeds, ASM-0242)

For judge `<p>` in {p1, p2, p3}: seed = `dts/1|judge-<p>|20260710`, i.e. the
literal strings `dts/1|judge-p1|20260710`, `dts/1|judge-p2|20260710`,
`dts/1|judge-p3|20260710`. Order all 808 item ids ascending by
`sha256_hex(utf8(seed + "|" + item_id))`; positions 1..808. Each judge's pass
runs SEQUENTIALLY in that order (stateless per-item calls make order
science-neutral; the frozen pinned order is honoured and recorded). The three
per-judge passes MAY run concurrently with each other (3 processes ≤ the
frozen concurrency cap 5); items within a pass are never parallelised. The
runner writes `judge-<p>-position-map.jsonl` (`{position, id}`) to the
opus-run provenance dir before the first call of each pass.

## 4. The pinned invocations (exact commands)

Common: `$REPO` = the repo root; per-judge empty out-of-repo workdir
`mktemp -d /tmp/judge<p>-workdir.XXXXXX` (verified empty, path recorded);
one process per item; `$ATTEMPT_DIR` = per-attempt provenance dir.

### 4.1 judge-p1-gpt56sol / 4.2 judge-p2-gpt55 (codex; form byte-derived from `data/d-adj-t-llmproxy/judge-1p-invocation.md` §3, as the frozen record directs)

```sh
npx -y @openai/codex@0.144.1 exec \
  -m "$MODEL" \
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
  --output-schema "$REPO/poc/truthstyle-2x2/output-schema-dts.json" \
  -o "$ATTEMPT_DIR/last-message.json" \
  - < "$ATTEMPT_DIR/user-prompt.txt" \
  > "$ATTEMPT_DIR/events.jsonl" 2> "$ATTEMPT_DIR/stderr.log"
```

with `$MODEL` = `gpt-5.6-sol` (p1) / `gpt-5.5` (p2). All fixed elements carry
the judge-1p §3 rationale verbatim (empty workdir; `--ignore-user-config` and
both `--disable`s — this box's codex account is the GPT-5.5 auditor, injected
memories would be a hard E5 leak; `-s read-only` + zero-tool tripwire §7.1;
server-side enum; per-attempt capture). `npx … --version` must print exactly
`codex-cli 0.144.1` at preflight; the GLOBAL codex is never invoked and never
upgraded while any f2b judge run is in flight (frozen runner constraint).

### 4.3 judge-p3-haiku45 (headless Claude Code sub-process; ASM-0240)

```sh
cd "$JUDGEP3_WORKDIR" && \
env -u ANTHROPIC_API_KEY -u ANTHROPIC_AUTH_TOKEN \
    MAX_THINKING_TOKENS=0 DISABLE_AUTOUPDATER=1 \
  claude -p \
  --model claude-haiku-4-5-20251001 \
  --system-prompt "$(cat "$REPO/poc/truthstyle-2x2/judge-p3-system-prompt.txt")" \
  --tools "" \
  --setting-sources "" \
  --no-session-persistence \
  --output-format stream-json --verbose \
  < "$ATTEMPT_DIR/user-prompt.txt" \
  > "$ATTEMPT_DIR/events.jsonl" 2> "$ATTEMPT_DIR/stderr.log"
```

Element-by-element (every flag semantics MEASURED 2026-07-10 on claude-code
2.1.201, three staging probes; recorded in §9):

- `--model claude-haiku-4-5-20251001` — exact dated model id, never the alias;
  asserted per call against the init event `model` field AND the sole
  `modelUsage` key (fail-closed, §7.2).
- `--tools ""` — documented and verified to disable ALL tools: init event
  emits `"tools":[]`; tool use is impossible at the harness level, satisfying
  the frozen no-tools clause structurally (plus tripwire §7.1).
- `--system-prompt …` — REPLACES the default agent system prompt with the
  pinned format-only bytes ($(cat …) strips the file's single trailing
  newline; that stripped string is the pinned prompt).
- `--setting-sources ""` — loads NO user/project/local settings (no hooks, no
  model overrides). Verified accepted.
- `--no-session-persistence` — nothing written to session storage; the ONLY
  record is the captured `events.jsonl`.
- `MAX_THINKING_TOKENS=0` — disables thinking [MEASURED: with it, the
  assistant message contains a single `text` block, output_tokens 4; without
  it, a `thinking` block precedes the answer]. The p3 analog of codex effort
  `low` (minimal-reasoning contract, ASM-0241).
- `DISABLE_AUTOUPDATER=1` — best-effort version stability; the BINDING check
  is `claude --version` recorded at preflight and re-checked after the pass:
  both must print the same version, and that version must be ≥ 2.1.201. Any
  flag rejection or behavior drift ⇒ ABORT to Fable (fail-closed), never a
  workaround.
- `env -u ANTHROPIC_API_KEY -u ANTHROPIC_AUTH_TOKEN` — pins the auth path to
  the box's Claude Code subscription login; init event must read
  `"apiKeySource":"none"` (assert per call). NO Anthropic API key exists or is
  used (maintainer ruling 2026-07-10).
- One `claude -p` process per item = stateless single-stimulus INDEPENDENCE by
  construction: fresh OS process, fresh session id, empty workdir, no session
  resume, no cross-item context of any kind. `num_turns` must equal 1.

### 4.3.1 MCP tool-definition isolation — POST-RUN HARDENING ADDENDUM (2026-07-10)

> ADDENDUM, added 2026-07-10 by FABLE (designer-1) AFTER the final-phase
> record and verdict, which consumed the STAGED bytes of this spec — sha256
> `5b543f41635f4676382952bd1f6cd75daafa6f4e2186d64ed7f34de06467543d`,
> committed in `harness-manifest.json` and pinned via ops amendment seq 1.
> This addendum changes the working-tree file only; auditors recomputing the
> harness-manifest pin must use the staged bytes (git history / the
> manifest's recorded sha). Ruling: `mcp-tool-isolation-ruling.md`;
> stipulations ASM-0644 (ruling), ASM-0645 (evidence), ASM-0646 (mechanism).

- CORRECTION to the `--tools ""` bullet above: "disable ALL tools" is
  intermittently FALSE for claude.ai account-level MCP connectors. In the
  completed p3 pass, 8 of 818 init events (~1%) carried non-empty `tools`
  arrays of MCP tool definitions (`mcp__claude_ai_*`) despite `--tools ""`
  and `--setting-sources ""`, and 269/818 inits showed the connectors
  attached in `init.mcp_servers` [MEASURED: run 20260710T182459Z]. The §7.1
  gate marked every such attempt content-invalid; only `init.tools == []`
  calls produced retained labels, so the frozen structurally-tool-less clause
  held over all retained data and the verdict stands (ruling §2).
- BINDING invariant (was already §7.1; now explicitly load-bearing): the
  per-call `init.tools == []` gate — with zero `tool_use` blocks,
  `permission_denials == []`, `num_turns == 1` — is MANDATORY for every blind
  headless `claude -p` judge. `--tools ""` alone is never a sufficient
  structural-isolation guarantee.
- Headless-judge protocols staged AFTER 2026-07-10 MUST additionally pass
  `--strict-mcp-config` (with no `--mcp-config`) in this command form
  [MEASURED 2026-07-10, 3 probes, claude-code 2.1.201: flag accepted in `-p`
  mode; `init.mcp_servers == []` and `init.tools == []`]. Defense-in-depth
  only — the `init.tools == []` gate remains the binding check, and
  `--setting-sources ""` must never be cited as an MCP-exclusion mechanism.

## 5. Answer extraction (per judge)

- codex judges: the answer is the `answer` field of `last-message.json`
  (schema-constrained to the enum). Anything else ⇒ attempt INVALID.
- judge-p3: the answer is the `result` field of the single
  `"type":"result","subtype":"success"` event in `events.jsonl`.

## 6. Output token set + normalization (uniform, pinned; ASM-0242; the frozen "labels normalised by the runner" clause + the 'cannot say'→'cannot-say' mapping)

Applied identically to every judge's raw answer string, in this exact order:

1. strip leading/trailing ASCII whitespace;
2. strip AT MOST ONE trailing `.`;
3. ASCII-lowercase (A-Z → a-z only);
4. map the exact string `cannot say` → `cannot-say`;
5. VALID iff the result is byte-exactly one of `yes` / `no` / `cannot-say`;
   anything else ⇒ the attempt is INVALID (never repaired, never guessed).

For the codex judges the server-side enum makes steps 1–4 no-ops in the normal
path; the pipeline still runs (defense in depth). The normalized token is what
enters `labels.jsonl`.

## 7. Attempt validity, tripwires, retries (mechanical, fail-closed)

### 7.1 Zero-tool tripwires
- codex: ZERO tool/command events in `events.jsonl` (`exec_command`,
  `terminal_interaction`, `unified_exec`, `tool_call`, `web_search`,
  `patch_apply`, `view_image`, `image_generation`, `collab_` prefixes) —
  any hit ⇒ attempt INVALID, flag `tool_use_detected`.
- judge-p3: init event `"tools"` must be `[]`; zero `tool_use` blocks in any
  assistant message; `permission_denials` must be `[]`; `num_turns == 1` —
  any violation ⇒ attempt INVALID, flag `tool_use_detected`.

### 7.2 Identity tripwires (per call)
- codex: tooling version banner = `codex-cli 0.144.1`; model as invoked.
- judge-p3: init `model == "claude-haiku-4-5-20251001"`;
  `modelUsage` keys == {`claude-haiku-4-5-20251001`};
  `apiKeySource == "none"`. Mismatch ⇒ ABORT the pass (not just the item).

### 7.3 Blinding audit (mechanical)
Grep (case-insensitive) each `user-prompt.txt` and each captured
`events.jsonl`/`stderr.log` for the strings `kernel`, `nsm`, `truthstyle`,
`f2b`. `user-prompt.txt` must equal the item's `question` bytes exactly. Any
hit anywhere ⇒ ABORT to Fable (a hit means either item contamination or a
harness surface leaking project context — both are boundary stops).

### 7.4 Attempt validity
VALID iff: exit 0; the judge's answer artifact parses (§5); tripwires §7.1/7.2
clean; normalization §6 yields a token in the set. FIRST VALID ANSWER IS FINAL
— never re-sampled, re-rolled, or "checked again" (ASM-0241).

### 7.5 Retries and no-label contract (mirrors judge-1p §6)
- Transport/rate-limit failures are not content attempts: backoff
  30/60/120/300/300… s, max 10 per item, then ABORT the pass.
- Up to 3 CONTENT attempts per item, identical invocation bytes; after 3
  invalid attempts: no label — the (item, judge) pair is UNLABELLED
  (instrument accounting; feeds the frozen label-coverage and pool gates;
  NEVER mapped to the escape token), flag with the last failure reason.
- Run-level abort: > 40 unlabelled items in one judge's pass (~5% of 808) ⇒
  ABORT and report to Fable; do not finish a degenerate pass.

## 8. Preflight (step P — per judge, BEFORE any real item)

Two pinned calibration probes through the EXACT §2–§7 pipeline (trivially
easy; NOT d-ts items; never enter labels or any statistic). PASS iff both are
VALID on the first content attempt AND match `expected`. Any other outcome ⇒
ABORT before any real item and report to Fable. Also at preflight: §0 sha
checks; workdir-empty checks; `~/.claude/CLAUDE.md` must NOT exist (verified
absent at staging; if present ⇒ ABORT — it would be injected context);
version banners recorded.

- cal-1 (expected `yes`), user-prompt bytes:
```
Here is a proposed definition of the word "chair".

definition: a seat for one person, with a support for the back

Does this definition correctly give the meaning of the word "chair" as ordinarily understood? Answer with exactly one word: yes / no / cannot-say.
```
- cal-2 (expected `no`), user-prompt bytes:
```
Here is a proposed definition of the word "dog".

definition: a large gray animal with a very long nose called a trunk

Does this definition correctly give the meaning of the word "dog" as ordinarily understood? Answer with exactly one word: yes / no / cannot-say.
```

## 9. "Temperature 0" — pinned operationalisation (DISCLOSED; ASM-0241)

Neither interface exposes a temperature parameter [MEASURED 2026-07-10:
codex-cli 0.144.1 exposes only reasoning-effort levels (judge-1p §4, re-cited);
`claude --help` (2.1.201) exposes NO temperature/sampling flag]. The frozen
"temperature 0" commitment is discharged EXACTLY as the frozen record already
discharges it for judge-p1 via the judge-1p invocation form it cites: (1)
pinned model ids + pinned tool versions + pinned prompt bytes; (2) stateless
single-shot per-item calls; (3) minimal reasoning (codex effort `low`; p3
`MAX_THINKING_TOKENS=0`, thinking-block-free MEASURED); (4) output constrained
to the exact token set (server enum / pinned format prompt + §6); (5) FIRST
VALID ANSWER IS FINAL. Residual server-side nondeterminism is bounded by the
frozen retest gate (agreement ≥ 0.85 over ≥ 48 duplicate judgments — disclosed
in the frozen record as a floor, not judge-quality evidence) and can never
become a selection effect.

Staging probe facts, recorded for the runner's expectations [MEASURED
2026-07-10, 3 probes]: p3 wall 0.9–4.4 s/call; nominal cost 0.0002–0.003
USD/call (≈ 0.2–2 USD for 808 calls, inside the frozen §3.7 estimate and the
40 USD cap; billed to the box's subscription — `total_cost_usd` is reported
nominally); the subscription's seven-day utilization read 0.59 at staging —
the runner records every `rate_limit_event` and backs off per §7.5.

## 10. Recorded outputs

Into `data/d-ts-labels/` (the corpus whose kot-corpus-hash/1 digest fills the
`corpus_hashes.d-ts-labels` placeholder by a LATER ops amendment, AFTER
adjudication completes and BEFORE the final-phase record — NOT part of this
staging; RT-14: pseudonymous judge ids only):

- `labels.jsonl` — one line per (item, judge) with a VALID label:
  `{"item_id", "judge", "label"}`, `judge` byte-exactly one of
  `judge-p1-gpt56sol` / `judge-p2-gpt55` / `judge-p3-haiku45` (the pinned
  analysis `JUDGES` list), sorted by (judge, item_id).
- `judge-<p>-responses.jsonl` — per judge: `{id, answer_raw, label, flags,
  n_content_attempts, n_transport_retries, position, judge}`.
- `summary.json` — counts (n_labelled per judge, n_unlabelled + reasons,
  retest ids), version banners, workdir paths, wall times, this spec's sha256,
  and the judge sourcing disclosure (p3 = Claude Haiku 4.5 via headless
  Claude Code sub-process, subscription auth, no API key; FORK-2 caveat).

Into `poc/truthstyle-2x2/opus-runs/<TS>/` (provenance, NOT the hashed corpus):
position maps, per-attempt `user-prompt.txt` / `last-message.json` /
`events.jsonl` / `stderr.log`, preflight artifacts, run log. Before commit:
the mechanical RT-14 scrub gate (grep `@` / email-like patterns →
`[RT-14-REDACTED]` + count in the run log).

## 11. What stays OUT of every judge's context (blinding audit list)

The judge sees ONE item's question bytes per process and nothing else, ever:
never tier/truth/style/donor/provenance labels, never the word "kernel" or the
project name, never other items, never other judges, never this experiment's
existence. For p3 the isolation is structural (empty out-of-repo cwd ⇒ no
project CLAUDE.md; fresh cwd-keyed memory path verified empty at staging;
`--setting-sources ""`; `--system-prompt` replacement; `~/.claude/CLAUDE.md`
verified absent) and audited mechanically (§7.3). The in-session Agent-tool
sub-agent form is FORBIDDEN for this record (ASM-0240): it injects the project
CLAUDE.md and auto-memory (which name the project and NSM) into the judge's
context — a hard violation of the frozen blinding clause.
