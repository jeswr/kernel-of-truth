# g3-llmproxy-v2 — pinned judge-pair invocation specification (the harness bytes)

> STATUS: staged 2026-07-10 by FABLE (designer-1, experiment-designer role) as
> the per-item invocation spec whose sha256 fills the DRAFT record's
> `pins.artifact_hashes["poc/g3-llmproxy-v2/judge-invocation.md"]` BEFORE
> freeze (registry/experiments/g3-llmproxy-v2.json; design note
> poc/g3-llmproxy-v2/design.md). SUPERSEDES the frozen g3-llmproxy spec
> (poc/g3-llmproxy/judge-invocation.md, sha dd402cdd…) after its run ABORTED
> 2026-07-10 on the section-7 >10-no-label gate: judge-pB fenced its pass-B
> answers in ```json … ``` and the v1 section-5 contract rejected them
> (parse_fail; run-log captures under
> poc/g3-llmproxy/opus-runs/20260710T194903Z/). The ONLY deltas from v1:
> the hardened judge-pB pass-B system prompt, the section-5 FENCE
> NORMALIZATION, the section-8 extraction self-check, and the v2 output/
> provenance paths (sections 0, 4.2, 5, 8, 9) [STIPULATED: ASM-0650,
> ASM-0651]. The frozen g3 record, its GATE-H human annotation path and its
> open run-stage decisions are byte-untouched; this run writes NOTHING under
> `data/instance-descriptions/`. The Opus runner executes this spec
> MECHANICALLY; any situation this spec does not decide is a BOUNDARY STOP
> back to Fable, never a runner improvisation. Governing stipulations:
> ASM-0530/0531/0532/0533/0534 (design block), ASM-0550/0551/0552/0553/0554
> (shared llmproxy policy), ASM-0642 (rendering), ASM-0644 (init.tools==[]
> hard gate; staged 2026-07-10, so its after-2026-07-10 --strict-mcp-config
> clause is not triggered and the invocation bytes stay identical to v1),
> ASM-0650/0651 (this supersession).

## 0. Pinned inputs (runner fail-closes on every one before the first call; ERR_G3P_PIN)

Unchanged artifacts are carried at their existing v1 paths and pins
(byte-identical, shared with the superseded record); the three v2 artifacts
carry fresh pins.

| artifact | path | sha256 |
|---|---|---|
| instances (200; the ONLY item source) | `data/instance-descriptions/instances.jsonl` | `04cdfbfd77117e6f6e9313d53df6534b01077e241cd7664ca6f709cd7be311f1` |
| condition sets (20) | `data/instance-descriptions/conditions.jsonl` | `fec2bc669b40077d057f59d6480eee3501ef396f62af64171479676a4ed3590a` |
| annotation protocol (instruction source) | `data/instance-descriptions/annotation-protocol.md` | `57610024480122a5db9596e2d27dd3cb717167a88673e2c9eeb4fa9a98414284` |
| prompt template, pass A | `poc/g3-llmproxy/prompt-template-pass-a.txt` | `3cd7b450948770916ae937186f15ebbdb15d052c2a7c60f866642dacde8ea54e` |
| prompt template, pass B | `poc/g3-llmproxy/prompt-template-pass-b.txt` | `dbb0693720cb0d1c9bf3f0861ef6a6cce5bbfaff83f87c4baa5343ea011f3380` |
| output schema, pass A (judge-pA server-side) | `poc/g3-llmproxy/output-schema-pass-a.json` | `fa1e46a3d5a4e0e1e49992c9f5f5f08b902ae66470dfb59aebb16aa0f26624d7` |
| output schema, pass B (judge-pA server-side; judge-pB validation contract) | `poc/g3-llmproxy/output-schema-pass-b.json` | `5576ee23c66bc797b7f443533279da3aaa963164c63bd7ffc0644ec47da55137` |
| judge-pB format-only system prompt, pass A (§4.3 analog) | `poc/g3-llmproxy/judge-pB-system-prompt-pass-a.txt` | `d82a0450f697562244cca2f172956424f6a902bd4bdb5ab80a752b9c5c4526d9` |
| judge-pB format-only system prompt, pass B (§4.3 analog; v2 HARDENED: bare raw object, no fence) | `poc/g3-llmproxy-v2/judge-pB-system-prompt-pass-b.txt` | `d0672138241f2722f24be59cba2256ed2f834048ad89de2b9c2f70d94e7b9122` |
| probe-B set (30; NEVER in counts) | `poc/g3-llmproxy/probe-b.jsonl` | `5691473c878df8623054664c02717274127b2a53eeb9068459064f08fa35b287` |
| probe + order manifest (4 real orders, 2 probe orders) | `poc/g3-llmproxy/probe-b-manifest.json` | `7269a629f9fdbaa4eb4f2214e89da10e4e051dd24d07a0eada27d059509df7bc` |
| probe builder (seed-pinned, single-draw) | `poc/g3-llmproxy/build-probe-b.py` | `b0a368947b0535d26297fdd867fa40281aa6ba0bccf7c1a955b1d5de51cce6d6` |
| calibration items (preflight only, 2 per pass, expected inline) | `poc/g3-llmproxy/calibration-items.jsonl` | `90ffc7dae4d60918d08ebc6c1a7fc355ee0f21aad4986219fcd9f6d944a045cc` |
| pinned analysis (v2: carries the §5 extraction reference implementation) | `analysis/g3_llmproxy_v2.py` | `8a749087ca73d77370b2e4494f5af63a720337f1d930fd167f515aaec9c642bf` |
| this spec | `poc/g3-llmproxy-v2/judge-invocation.md` | (pinned in the record's artifact_hashes) |

Also required: the `instance-descriptions` kot-corpus-hash/1 digest
`1a55a219…` (the record's design-time pin; if it drifts before freeze, the
record re-pins FIRST — boundary stop). All shas re-verified against the
working tree at staging time [MEASURED: sha256sum 2026-07-10].

## 1. Judge pair (frozen two-annotator design mirrored cross-family; ASM-0530)

| judge id (labels `judge` field, byte-exact) | model | interface |
|---|---|---|
| `judge-pA-gpt56sol` | `gpt-5.6-sol`, reasoning effort `low` | `npx -y @openai/codex@0.144.1` (§4.1 form, truthstyle judges-invocation) |
| `judge-pB-haiku45` | `claude-haiku-4-5-20251001` | headless `claude -p` sub-process (§4.3 form, truthstyle judges-invocation) |

judge-pB's vendor-family overlap with the materials' authoring agents is
DISCLOSED (FORK-2-style); it is half of a pair, never sole gold [STIPULATED:
ASM-0530]. The in-session Agent-tool sub-agent form is FORBIDDEN for both
(ASM-0240 finding, carried over).

## 2. Per-item prompt assembly (byte-exact; ASM-0642)

USER prompt = the pass's template bytes with each `{{NAME}}` token replaced
as below, nothing else added or removed (the template's single trailing
newline stays). IDENTICAL bytes for both judges. Two faithful runners MUST
produce identical bytes.

Pass A (`prompt-template-pass-a.txt`; instruction = the protocol's pass-A
instruction verbatim, carried inside the template):
- `{{TEXT}}` — the instance's `text` field bytes verbatim.
- `{{TARGET}}` — the instance's `target` field bytes verbatim.
- `{{WORD}}` — the concept word: the substring of the instance's `concept_id`
  after the last `:` (e.g. `end`), rendered with any `-` replaced by a space.
  The sheet's underlining is operationalised as this explicit
  "underlined word" line — nothing in `target` is marked [STIPULATED:
  ASM-0642]. Pass A may name the concept word (the human pass-A sheet shows
  it inside `target`); the `concept_id` itself (the `urn:` string) NEVER
  appears.

Pass B (`prompt-template-pass-b.txt`; instruction = the protocol's pass-B
instruction verbatim, carried inside the template; concept word, label and
target WITHHELD per the protocol):
- `{{TEXT}}` — the instance's `text` field bytes verbatim.
- `{{BINDINGS}}` — one line per key of the instance's `bindings` object, in
  the object's recorded order, each line `- ` + key bytes + ` = ` + value
  bytes verbatim; lines joined with `\n` (no trailing `\n`).
- `{{CONDITIONS}}` — one line per condition of the instance's
  `condition_set_id` set (from `conditions.jsonl`), in recorded order, each
  line `- ` + `cid` bytes + `: ` + `text` bytes verbatim; joined with `\n`
  (no trailing `\n`). The set's `concept_id`, `concept_label`, `frame` and
  `gloss_verbatim` fields NEVER render.

Probe-B items render through the EXACT pass-B path from their pre-resolved
`probe-b.jsonl` rows (`text`, `bindings`, deranged `conditions`). Calibration
items render through their pass's path from `calibration-items.jsonl`
(their `expected` object never enters any prompt). No item id, position,
progress note, or metadata is ever added.

## 3. Item order and execution discipline (frozen contamination rule honoured)

All orders are precomputed in `probe-b-manifest.json` (seeds verbatim:
`g3lp/1|judge-pA-passA|20260710`, `g3lp/1|judge-pA-passB|20260710`,
`g3lp/1|judge-pB-passA|20260710`, `g3lp/1|judge-pB-passB|20260710`; probe
select `g3lp/1|probe|20260710`, derangement + per-judge probe orders as
pinned in the builder; ranking = ascending
`sha256_hex(utf8(seed + "|" + item_id))`). Per judge: preflight (§8) -> ALL
200 pass-A items -> ALL 200 pass-B items -> 30 probe-B items (the frozen
all-A-before-B rule; structurally guaranteed anyway by stateless per-item
processes — one item, one pass, one fresh process, no session state;
ASM-0530). Items within a pass are SEQUENTIAL; the two judges' passes MAY run
concurrently with each other (2 processes, the record's concurrency cap). The
runner writes `judge-<p>-position-map.jsonl` (`{position, id}`, pass-B
positions prefixed `b`, probe positions prefixed `p`) to the run provenance
dir before each judge's first call.

## 4. The pinned invocations (exact commands)

### 4.1 judge-pA-gpt56sol (codex; truthstyle §4.1 form)

With `$PASS` in {a, b} selecting the schema:

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
  -C "$JUDGEPA_WORKDIR" \
  --color never \
  --json \
  --output-schema "$REPO/poc/g3-llmproxy/output-schema-pass-$PASS.json" \
  -o "$ATTEMPT_DIR/last-message.json" \
  - < "$ATTEMPT_DIR/user-prompt.txt" \
  > "$ATTEMPT_DIR/events.jsonl" 2> "$ATTEMPT_DIR/stderr.log"
```

`$JUDGEPA_WORKDIR` = `mktemp -d /tmp/judgepa-workdir.XXXXXX` (verified empty,
path recorded). `npx … --version` must print exactly `codex-cli 0.144.1` at
preflight; the GLOBAL codex is never invoked.

### 4.2 judge-pB-haiku45 (headless Claude Code sub-process; truthstyle §4.3 form)

With `$SYSPROMPT` = `poc/g3-llmproxy/judge-pB-system-prompt-pass-a.txt`
(pass A) / `poc/g3-llmproxy-v2/judge-pB-system-prompt-pass-b.txt` (pass B;
the v2 HARDENED prompt) — format-enforcement ONLY; the judging standards live
in the identical user-prompt bytes:

```sh
cd "$JUDGEPB_WORKDIR" && \
env -u ANTHROPIC_API_KEY -u ANTHROPIC_AUTH_TOKEN \
    MAX_THINKING_TOKENS=0 DISABLE_AUTOUPDATER=1 \
  claude -p \
  --model claude-haiku-4-5-20251001 \
  --system-prompt "$(cat "$REPO/$SYSPROMPT")" \
  --tools "" \
  --setting-sources "" \
  --no-session-persistence \
  --output-format stream-json --verbose \
  < "$ATTEMPT_DIR/user-prompt.txt" \
  > "$ATTEMPT_DIR/events.jsonl" 2> "$ATTEMPT_DIR/stderr.log"
```

Element semantics carry over verbatim from the truthstyle §4.3 staging
measurements (claude-code >= 2.1.201): exact dated model id asserted per call
against the init `model` field AND the sole `modelUsage` key; `--tools ""`
=> init `"tools":[]`; `--setting-sources ""` => no user/project/local
settings; `--no-session-persistence`; `MAX_THINKING_TOKENS=0` (the p-family
minimal-reasoning contract); `env -u …` pins subscription auth — init
`apiKeySource` must read `"none"`; one process per item => stateless
independence, `num_turns == 1`. `claude --version` recorded at preflight and
re-checked after each pass (same version, >= 2.1.201). Any flag rejection or
behavior drift => ABORT to Fable, never a workaround.

## 5. Answer extraction, normalization, validity

- judge-pA: the answer object is `last-message.json` (schema-constrained).
- judge-pB: the answer object is the `result` field of the single
  `"type":"result","subtype":"success"` event in `events.jsonl`.

FENCE NORMALIZATION (the ONLY §5 change from the superseded spec; uniform,
both judges, all passes and probes; content-blind FORMAT normalization in the
same class as the token normalization below — deterministic, applied before
any answer field is read, unable to change which label is extracted; never
answer repair; ASM-0650): the raw answer string is stripped of leading and
trailing ASCII whitespace; if it now both starts AND ends with ```, exactly
ONE fence layer is removed — the opening ``` plus an optional language tag
matching `[A-Za-z0-9_-]{0,16}` plus optional spaces/tabs plus, when present,
the first newline (LF or CRLF), and the closing ``` — then stripped again. A
string still starting with ``` after one removal is INVALID (single layer
only). The result must parse (`json.loads` over its ENTIRE length) as exactly
one JSON object. REFERENCE IMPLEMENTATION (the single source of truth): the
runner labels through `extract_answer_object()` and `normalize_token()`
imported from the pinned `analysis/g3_llmproxy_v2.py` — a reimplementation is
a spec violation (boundary stop).

Pass A: the object must be exactly `{"q1": <token>}`. Pass B: exactly
`{"q2": <token>, "q2_failing_conditions": <list>}`. Token normalization
(uniform, both judges, defense in depth): strip ASCII whitespace, at most one
trailing `.`, ASCII-lowercase, map `cannot say` -> `cannot-say`; VALID iff
the result is byte-exactly one of `yes` / `no` / `cannot-say`. Pass-B list
checks: every element matches `^c[0-9]+$` AND names a cid of the item's
rendered condition list; non-empty iff `q2 = no`, byte-empty `[]` otherwise.
Any violation => attempt INVALID (never repaired, never guessed).

## 6. Tripwires (mechanical, fail-closed)

- Zero-tool: judge-pA — zero tool/command events in `events.jsonl` (the §4.1
  event list). judge-pB — init `"tools"` must be `[]`; zero `tool_use`
  blocks; `permission_denials` `[]`; `num_turns == 1`. Any violation =>
  attempt INVALID, flag `tool_use_detected`.
- Identity: judge-pA — banner `codex-cli 0.144.1`, model as invoked.
  judge-pB — init `model == "claude-haiku-4-5-20251001"`, `modelUsage` keys
  == {that id}, `apiKeySource == "none"`. Mismatch => ABORT that judge's
  pass.
- Blinding audit (per call): grep (case-insensitive) `user-prompt.txt` and
  captured `events.jsonl`/`stderr.log` for `kernel`, `nsm`, `necessity`,
  `sufficiency`, `hypothesis` — any hit anywhere => ABORT to Fable (boundary
  stop). The judges must never see the 10% thresholds, the derived-violation
  rules, or which outcome helps which hypothesis. `user-prompt.txt` must
  equal the §2 assembly bytes exactly.

## 7. Attempt validity, retries, no-label contract

VALID iff: exit 0; §5 checks pass; §6 tripwires clean. FIRST VALID ANSWER IS
FINAL (the §4.1/§4.3 "temperature 0" discharge carries over verbatim).
Transport failures are not content attempts: backoff 30/60/120/300/300… s,
max 10 per item, then ABORT that judge's pass. Up to 3 CONTENT attempts per
(item, judge, pass), identical invocation bytes; after 3 invalid attempts: NO
LABEL for that (item, judge, pass) — instrument accounting, capped by the
frozen no-label gate (> 5% per judge per pass => INSTRUMENT-INVALID;
ASM-0554); never mapped to an answer. cannot-say is a VALID label (neither
violation nor satisfaction; its own <= 5% gate). Run-level abort: > 10
no-label items in one judge's pass, or > 3 no-label probes for one judge =>
ABORT and report to Fable.

## 8. Preflight (per judge, BEFORE any real item)

FIRST, once per run (runner-local, no judge call): the extraction self-check
`cal:g3lp-x1` — `python3 analysis/g3_llmproxy_v2.py --selftest` must exit 0
and print `g3-llmproxy-v2 selftest OK`; its pinned fixtures include the EXACT
fenced pass-B defect bytes from the aborted v1 run
(```json … ``` around the two-field object) and prove the §5 extraction
handles them [STIPULATED: ASM-0650]. Any failure => ABORT before any judge
call and report to Fable.

Then, per judge: all four `calibration-items.jsonl` items (ids `cal:g3lp-a1`
expected q1=yes, `cal:g3lp-a2` expected q1=no, `cal:g3lp-b1` expected q2=yes
+ `[]`, `cal:g3lp-b2` expected q2=no + `["c2"]`; trivially easy; never enter
labels or any statistic) through the EXACT §2–§7 pipeline (pass-A items under
the pass-A path, pass-B items under the pass-B path — pass-B under the v2
hardened system prompt and the v2 §5 extraction). PASS iff all four are VALID
on the first content attempt AND match `expected` exactly (including the
failing-conditions list). Any other outcome => ABORT that judge before any
real item and report to Fable. Also at preflight: §0 sha checks + the
instance-descriptions corpus digest; workdir-empty checks;
`~/.claude/CLAUDE.md` must NOT exist; version banners recorded; per-judge
`preflight_pass` (both required) feeds `/gates/adjudication_valid` (the
run-level extraction self-check is a precondition of BOTH judges'
`preflight_pass`).

## 9. Recorded outputs

Into `data/g3-annot-llmproxy-v2/` (the DISJOINT v2 corpus whose
kot-corpus-hash/1 digest fills the record's
`corpus_hashes.g3-annot-llmproxy-v2` placeholder by ops amendment AFTER the
judge runs and BEFORE the final-phase record; the superseded record's
`g3-annot-llmproxy` placeholder stays unfilled forever [STIPULATED:
ASM-0651]; RT-14: pseudonymous judge ids `judge-pA-gpt56sol` /
`judge-pB-haiku45` only):

- `judge-<p>-pass-a-responses.jsonl` / `judge-<p>-pass-b-responses.jsonl` —
  one line per REAL instance, sorted by `id`: `{id, q1 | q2 +
  q2_failing_conditions, flags, n_content_attempts, n_transport_retries,
  position, judge}`.
- `judge-<p>-probe-responses.jsonl` — same pass-B shape, probe items
  (`*-pb`). NEVER merged into counts.
- `labels-proxy.jsonl` — one line per instance: `{id, q1_pA, q2_pA,
  q2_failing_pA, q1_pB, q2_pB, q2_failing_pB, decisive_pA, decisive_pB,
  dual_decisive, necessity_violation_pA, necessity_violation_pB,
  sufficiency_violation_pA, sufficiency_violation_pB (the frozen derivation
  verbatim: necessity iff q1=yes and q2=no; sufficiency iff q1=no and
  q2=yes), flags}`. These are the pinned per-item labels the eventual human
  round is measured against (ASM-0553); they must NEVER be shown to those
  annotators.
- `summary.json` — the exact integer inputs of `analysis/g3_llmproxy_v2.py`
  (`_rec` fields: n_instances, n_dual_decisive, the necessity 2x2
  n_nec_both/n_nec_neither/n_nec_a_only/n_nec_b_only, bracket counts
  n_necessity_concordant/union + sufficiency pair, per-judge-per-pass
  n_cannot_say_*/n_nolabel_*, per-judge probe n_probe_labelled_*/
  n_probe_false_sat_*, per-judge n_necessity_*/n_sufficiency_*,
  failing_cid_histogram over both judges' real pass-B `no` answers,
  preflight_pass = AND of both judges), version banners, workdir paths, wall
  times, this spec's sha256, and the stand-in disclosure verbatim (cross-
  family LLM pair; WEAK FEASIBILITY PROXY; the human g3 remains the sole
  adjudicator of HS3 and the only trigger of its DAG consequences).

Into `poc/g3-llmproxy-v2/opus-runs/<TS>/` (provenance, NOT the hashed
corpus): position maps, per-attempt artifacts, preflight artifacts, run log.
Before commit: the mechanical RT-14 scrub gate. The run writes NOTHING under
`data/instance-descriptions/` (ASM-0553), NOTHING under
`data/g3-annot-llmproxy/` and NOTHING under `poc/g3-llmproxy/` (the
superseded record's trees, retained read-only; ASM-0651).

## 10. What stays OUT of every judge's context

Each judge sees ONE item's §2 bytes per process and nothing else, ever: never
the concept ids or condition-set provenance, never pass-B concept words,
never the thresholds or derivation rules, never the other judge's existence
or answers, never the probe status of an item, never this experiment's
existence or stand-in status. For judge-pB the isolation is structural (empty
out-of-repo cwd => no project context; `--setting-sources ""`;
`--system-prompt` replacement; subscription auth asserted) and audited
mechanically (§6). Q1 can NEVER see a condition set: one item, one pass, one
fresh process (structurally stronger than the human ordering requirement;
the A-before-B run order is honoured anyway; ASM-0530).
