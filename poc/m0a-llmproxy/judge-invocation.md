# m0a-llmproxy — pinned judge-m1p invocation specification (the harness bytes)

> STATUS: staged 2026-07-10 by FABLE (designer-1, experiment-designer role) as
> the per-item invocation spec whose sha256 fills the DRAFT record's
> `pins.artifact_hashes["poc/m0a-llmproxy/judge-invocation.md"]` BEFORE freeze
> (registry/experiments/m0a-llmproxy.json; design note
> poc/m0a-llmproxy/design.md). The M0a pre-registration and the pending human
> pass are byte-untouched. The Opus runner executes this spec MECHANICALLY;
> any situation this spec does not decide is a BOUNDARY STOP back to Fable,
> never a runner improvisation. Governing stipulations: ASM-0540/0541/0542/
> 0543/0544 (design block), ASM-0550/0551/0552/0553/0554 (shared llmproxy
> policy), ASM-0640/0641 (this rendering).

## 0. Pinned inputs (runner fail-closes on every one before the first call; ERR_M0AP_PIN)

| artifact | path | sha256 |
|---|---|---|
| annotation sample (300; the ONLY item source) | `mapper/m0/annotation-sample.jsonl` | `038604a8d7d0fa160209805374b5c89dd5a044c552d1e0dafe0d2bd028575a2c` |
| agent judgments (comparator, read-only, REPORTED-ONLY diagnostic) | `mapper/m0/agent-judgments.jsonl` | `6f291b692aaafd0b5bcba814a6ef6d3f64251ab239dfd513786371df7d4a3ba6` |
| prompt template, concept stratum | `poc/m0a-llmproxy/prompt-template-concept.txt` | `831b93006b6d02ba0e452f85f84dd7da88bf319a2ed7498431b49f63824381d2` |
| prompt template, prime stratum (byte-identical to concept by design) | `poc/m0a-llmproxy/prompt-template-prime.txt` | `831b93006b6d02ba0e452f85f84dd7da88bf319a2ed7498431b49f63824381d2` |
| prompt template, abstain stratum | `poc/m0a-llmproxy/prompt-template-abstain.txt` | `ca18cdb61929e56dfa4dbfb7d2ef5f60ddc963f4fbddb873b1bc7bfd9ed5efa3` |
| prompt template, none stratum | `poc/m0a-llmproxy/prompt-template-none.txt` | `82a4db341975a03a9b0833de99734a7a4179b77d57df5aa8e94e2ddfb428d320` |
| output schema, concept | `poc/m0a-llmproxy/output-schema-concept.json` | `c37b7c69ce4a41d93e3d5824988ff5c1079979b9d3fad11eb3f3786d69eb4e68` |
| output schema, prime (byte-identical to concept) | `poc/m0a-llmproxy/output-schema-prime.json` | `c37b7c69ce4a41d93e3d5824988ff5c1079979b9d3fad11eb3f3786d69eb4e68` |
| output schema, abstain | `poc/m0a-llmproxy/output-schema-abstain.json` | `a28c14501374a801c23934fa978703e7675e93c1bd8c5177438e39d7541339da` |
| output schema, none | `poc/m0a-llmproxy/output-schema-none.json` | `a0bbecfe8aaf9026dd263f12db062bed4b1c3478e864e06a89637aef03f00f5f` |
| prime one-line glosses (authored sense surface; ASM-0640) | `poc/m0a-llmproxy/prime-glosses.json` | `fdb004ccb495fd913c89bfe7262d3389d0d86276ff52f6657509735540cb2013` |
| none-stratum inventory builder | `poc/m0a-llmproxy/build-none-inventory.py` | `272d71d1a066746cf73ddc8df388476f2dc684a67bdf5fe5ffacce30d2eca359` |
| none-stratum inventory (byte-identical across all 50 none items) | `poc/m0a-llmproxy/none-inventory.txt` | `4d3374b5d73daebd033cbe87711b679ed9951846cd6ff242816aec3324786c31` |
| deranged-gloss probe (40; NEVER in labels) | `poc/m0a-llmproxy/deranged-probe.jsonl` | `b44b850dd32277be0f252fb363e8ab805185d912c4a14e79b99d49827b1b532c` |
| probe + order manifest (real order, probe order, retest ids) | `poc/m0a-llmproxy/deranged-probe-manifest.json` | `2fa6b73922508a265064b82940bfc2c7630251869b58a860b46342a60b722abc` |
| probe builder (seed-pinned, single-draw) | `poc/m0a-llmproxy/build-deranged-probe.py` | `81f783340721be8372e6a5ff02083ea34861bcee2efe79deb72da9208e0aa36e` |
| calibration items (preflight only, expected labels inline) | `poc/m0a-llmproxy/calibration-items.jsonl` | `a7b4fa015796d6bafd3b06f3815c5abdb5f93c93759039f7bbcaa344764c6c0b` |
| pinned analysis | `analysis/m0a_llmproxy.py` | `7cffe1a520d1c9a1e99a67cb550680e86325816b7a3574cdbf3b61cc52df72b4` |
| this spec | `poc/m0a-llmproxy/judge-invocation.md` | (pinned in the record's artifact_hashes) |

Also required (record pins, verified by kot-corpus-hash/1): the `kernel-v0`
corpus digest `8209cada…` (gloss source for concept senses). All shas
re-verified against the working tree at staging time [MEASURED: sha256sum
2026-07-10].

## 1. Judge binding

`judge-m1p-gpt56sol`: model `gpt-5.6-sol`, reasoning effort `low`, via
npx-pinned `@openai/codex@0.144.1` `exec` — the §4.1 form of
`poc/truthstyle-2x2/judges-invocation.md` [STIPULATED: ASM-0551].
CROSS-VENDOR is load-bearing twice over (the replaced comparator labels AND
the mapper/glosses are Claude-family work-products; ASM-0540). The in-session
Agent-tool sub-agent form is FORBIDDEN (ASM-0240 finding, carried over).
`npx -y @openai/codex@0.144.1 --version` must print exactly `codex-cli
0.144.1` at preflight; the GLOBAL codex is never invoked.

## 2. Per-item prompt assembly (byte-exact; ASM-0541, ASM-0640, ASM-0641)

USER prompt = the stratum's template bytes with each `{{NAME}}` token
replaced as below, nothing else added or removed (the template's single
trailing newline stays). Template + schema are selected by the item's
`stratum` field. Two faithful runners MUST produce identical bytes.

- `{{PASSAGE}}` — `contextBefore` bytes + `[[` + `surface` bytes + `]]` +
  `contextAfter` bytes, all verbatim, no stripping (the fragment may begin or
  end mid-word; the template says so; ASM-0641).
- `{{SURFACE}}` — the `surface` field bytes verbatim.
- `{{SENSE}}` (concept/prime strata) — the mapped target's gloss WITHOUT any
  id: for `urn:kernel-v0:<slug>` targets, the `gloss` field bytes of
  `data/kernel-v0/concepts/<slug>.json`; for `prime:<NAME>` targets, the
  `gloss` field of the `<NAME>` entry in `prime-glosses.json` (ASM-0640).
  Probe items carry their pre-resolved `sense` bytes from
  `deranged-probe.jsonl`; calibration items theirs from
  `calibration-items.jsonl`.
- `{{CANDIDATES}}` (abstain stratum) — one line per recorded candidate, in
  recorded array order, line `n` = `<n>. ` + the candidate's gloss resolved
  exactly as `{{SENSE}}` above; lines joined with `\n` (no trailing `\n`).
  [MEASURED at staging: all 50 abstain items carry exactly 2 candidates; the
  abstain schema enum is therefore {"1","2","none"}; any item violating this
  is a boundary stop.]
- `{{INVENTORY}}` (none stratum) — the exact bytes of `none-inventory.txt`
  with its single trailing newline stripped; byte-identical across all 50
  none items.

The judge NEVER sees: urns or target ids, stratum labels, the words the
blinding audit greps for, or that a mapping system produced the proposed
sense ("a proposed sense", never "the mapped target"; the judging criteria on
the sheets are the stated M0a criteria with exactly that blind renaming;
ASM-0641). No item id, position, progress note, or metadata is ever added.

## 3. Item order and execution discipline

All orders are precomputed in `deranged-probe-manifest.json` (seeds verbatim:
real `m0alp/1|judge-m1p|20260710`; probe select/derange/order
`m0alp/1|probe|20260710` + fixed sub-purpose suffixes as pinned in the
builder; retest `m0alp/1|retest|20260710`; ranking = ascending
`sha256_hex(utf8(seed + "|" + item_id))`). Execution: preflight (§8) -> 300
real items in `real_order` -> 40 probes in `probe_order` -> 30 retest
duplicates in `retest_ids` order. Sequential, one process per item,
concurrency 1. The runner writes `judge-m1p-position-map.jsonl`
(`{position, id}`, probe positions prefixed `p`, retest prefixed `r`) to the
run provenance dir before the first call.

## 4. The pinned invocation (exact command; §4.1 form)

With `$FMT` in {concept, prime, abstain, none} selected by the item's stratum
(probe items use their `stratum` field; calibration items their
`stratum_template` field):

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
  --output-schema "$REPO/poc/m0a-llmproxy/output-schema-$FMT.json" \
  -o "$ATTEMPT_DIR/last-message.json" \
  - < "$ATTEMPT_DIR/user-prompt.txt" \
  > "$ATTEMPT_DIR/events.jsonl" 2> "$ATTEMPT_DIR/stderr.log"
```

`$JUDGE_WORKDIR` = `mktemp -d /tmp/judgem1p-workdir.XXXXXX` (verified empty,
path recorded). All fixed elements carry the judge-1p/truthstyle rationale
verbatim.

## 5. Answer extraction and validity

The answer is `last-message.json` parsed as exactly `{"answer": <token>}`
(schema-constrained). Per-stratum token sets: concept/prime
`correct`/`incorrect`/`unclear`; abstain `1`/`2`/`none`; none `1`…`119`/
`none`. Defense-in-depth normalization (schema makes it a no-op): strip ASCII
whitespace, at most one trailing `.`, ASCII-lowercase, then require set
membership. ADDITIONAL PER-ITEM CHECK (abstain): the token must be `none` or
a number `<= ` the item's candidate count, else the attempt is INVALID.
Anything else => attempt INVALID, never repaired. Label mapping (analysis
inputs): abstain `1`/`2` -> candidate-correct, `none` ->
no-candidate-correct; none stratum number -> should-map, `none` ->
correctly-unmapped.

## 6. Tripwires (mechanical, fail-closed)

- Zero-tool: ZERO tool/command events in `events.jsonl` (the §4.1 event
  list) — any hit => attempt INVALID, flag `tool_use_detected`.
- Identity: version banner `codex-cli 0.144.1`; model as invoked. Mismatch
  => ABORT the pass.
- Blinding audit (per call): grep (case-insensitive) `user-prompt.txt` and
  captured `events.jsonl`/`stderr.log` for `kernel`, `nsm`, `urn:`, `mapper`
  — any hit anywhere => ABORT to Fable (boundary stop). `user-prompt.txt`
  must equal the §2 assembly bytes exactly.

## 7. Attempt validity, retries, no-label contract

VALID iff: exit 0; §5 checks pass; §6 tripwires clean. FIRST VALID ANSWER IS
FINAL. Transport failures are not content attempts: backoff 30/60/120/300/
300… s, max 10 per item, then ABORT the pass. Up to 3 CONTENT attempts per
item, identical invocation bytes; after 3 invalid attempts: NO LABEL — the
item leaves its stratum's denominator (instrument accounting, capped by the
frozen coverage gates; ASM-0554); never mapped to an answer. Run-level abort:
> 15 no-label real items (5% of 300), or any 100-item stratum's no-labels
> 10, or any 50-item stratum's > 5, or > 4 no-label probes => ABORT and
report to Fable.

## 8. Preflight (BEFORE any real item)

Both `calibration-items.jsonl` items (ids `cal:m0alp-1` expected `correct`,
`cal:m0alp-2` expected `incorrect`; trivially easy; never enter labels or any
statistic) through the EXACT §2–§7 pipeline under the concept template. PASS
iff both are VALID on the first content attempt AND match `expected`. Any
other outcome => ABORT before any real item and report to Fable. Also at
preflight: §0 sha checks + the kernel-v0 corpus digest; workdir-empty check;
`~/.claude/CLAUDE.md` must NOT exist; version banner recorded;
`preflight_pass` feeds `/gates/adjudication_valid`.

## 9. Recorded outputs

Into `data/m0a-judgments-llmproxy/` (the corpus whose kot-corpus-hash/1
digest fills the record's `corpus_hashes.m0a-judgments-llmproxy` placeholder
by ops amendment AFTER the judge run and BEFORE the final-phase record;
RT-14: pseudonymous judge id `judge-m1p-gpt56sol` only):

- `judge-m1p-responses.jsonl` — one line per REAL item, sorted by `id`:
  `{id, stratum, answer_raw, label, flags, n_content_attempts,
  n_transport_retries, position, judge}`.
- `judge-m1p-probe-responses.jsonl` — same shape, probe items (`m0ap-*`).
- `judge-m1p-retest-responses.jsonl` — same shape, retest duplicates
  (positions `r1..r30`).
- `labels-proxy.jsonl` — one line per real item: `{id, stratum, label,
  agent_label (diagnostic, from the pinned comparator), agree_agent
  (bool|null), flags}`. These are the pinned per-item labels the eventual
  human pass is measured against (ASM-0553); they must NEVER be shown to that
  annotator.
- `rendered-prompt-manifest.jsonl` — `{id, user_prompt_sha256}` per real +
  probe + retest item (the byte-exactness witness).
- `summary.json` — the exact integer inputs of `analysis/m0a_llmproxy.py`
  (`_rec` fields: n_items, per-stratum n_labelled/n_correct/n_unclear,
  n_candidate_correct_abstain, n_should_map_none, n_probe_labelled,
  n_probe_false_endorse, n_retest_compared, n_retest_agree, per-stratum
  n_agent_compared/n_agent_agree, preflight_pass), version banners, workdir
  path, wall times, this spec's sha256, and the stand-in disclosure verbatim
  (blind LLM proxy; WEAK-PROXY label on every P/R citation; the human pass
  over the same 300 items remains the sole gold standard).

Into `poc/m0a-llmproxy/opus-runs/<TS>/` (provenance, NOT the hashed corpus):
position map, per-attempt artifacts, preflight artifacts, run log. Before
commit: the mechanical RT-14 scrub gate. The run writes NOTHING under
`mapper/m0/` (ASM-0553).

## 10. What stays OUT of the judge's context

The judge sees ONE item's §2 bytes per process and nothing else, ever: never
urns/ids, never stratum labels, never the mapper's existence, never the
agent-judgment comparator, never the probe/retest status of an item, never
other items, never this experiment's existence or stand-in status. Retest
duplicates carry no marker of being duplicates.
