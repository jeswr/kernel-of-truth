# knull-v3 — blind two-family quality gate (ASM-0703 re-run on the Option-B store)

> STATUS: MEASURED gate result, 2026-07-11, Fable coordinator session. This doc
> records the ASM-0703 re-run that the v3 store's authoring disclosure and the
> Option-B ruling (maintainer decision issue 6; PROPOSED-ASM-1080) require as a
> freeze precondition for the knull-v2 superseding record. It is a readout, not
> a freeze action: the record is NOT frozen by this session (coordinator
> boundary). Raw evidence: `poc/knull/quality-gate-v3/` (prompt, order map,
> both judges' raw outputs + transcripts, `gate-tally.json` with sha256 pins).
>
> Tag convention: `[MEASURED: ref]` = observed result inside its envelope;
> `[STIPULATED: id]` = inherited design choice.

## 1. Instrument fidelity (pinned protocol, replicated exactly)

- Same two-part instrument as v2, byte-identical header/rubric — only the
  store path changed: `poc/knull/quality-gate-v3/build_gate_prompt.py` diffs
  against the v2 script header ZERO; the deterministic ascending-label order
  map is byte-identical to the v2 pinned map (same 108 labels)
  [MEASURED: diff, 2026-07-11].
- Store under test: `poc/knull/inputs-v3/plain-authored.json` v3.0.0, sha256
  `8812f91e…774b1d`; prompt `prompt.new108.txt` sha256 `c27a223b…ac8870`,
  9,248 chars (v2: 22,414 — the Option-B concision is 2.4x).
- Blindness (ASM-0701 mechanics): headwords withheld, definition texts only,
  no project/NSM/experiment context, judges never told a gate or comparison
  set exists; blinding grep (`kernel|nsm|truthstyle|f2b|knull`) zero hits on
  the prompt and both raw outputs [MEASURED].
- Judge families, per the pinned invocations:
  - **GPT-5.6** (`gpt-5.6-sol`), codex-cli **0.144.1** exec, reasoning effort
    **high**, `-s read-only --ignore-user-config --ephemeral --disable
    memories --disable standalone_web_search`, empty out-of-repo workdir;
    banner + zero-tool tripwire clean [MEASURED: `gate.new108.gpt56.err`].
  - **Claude Haiku 4.5** (`claude-haiku-4-5-20251001`), headless `claude -p`
    per `poc/truthstyle-2x2/judges-invocation.md` §4.3 **+ §4.3.1**
    (`MAX_THINKING_TOKENS=0`, `--tools ""`, `--setting-sources ""`,
    `--strict-mcp-config`, `--no-session-persistence`, subscription auth,
    claude-code 2.1.201). Tripwires: init `tools==[]`, `mcp_servers==[]`,
    `apiKeySource:"none"`, single text block, `num_turns==1`,
    `permission_denials==[]`, `modelUsage` keys ==
    {`claude-haiku-4-5-20251001`} [MEASURED: `gate.new108.haiku.events.jsonl`].
- One blind full-108 read per family; FIRST VALID ANSWER IS FINAL — no
  re-rolls [STIPULATED: ASM-0241 discipline, carried by the v2 gate].

## 2. Measured result

| | GPT-5.6 (effort high) | Haiku 4.5 (headless) |
|---|---|---|
| **Naturalness (1–10, floor ≥5 both)** | **8/10** — PASS | **4/10** — **FAIL** |
| Anaphoric renaming | none found | **1 finding** (entry 87) |
| Staged observers | none found | none found |
| Non-definitional / exemplification / consequence | none found | none found |
| Register/word-choice nits (non-blocking residual, per the v2 tally treatment) | 4 (entries 29, 62, 71, 80) | 4 (entries 5, 26, 62, 103) |

Context row [MEASURED: knull-v2.json prefreeze_gates_evidence;
gpt56-plaindict-review]: old-108 store 3/10 (GPT-5.6); v2 final store
GPT-5.6 **4/10**, Haiku **3/10**. v3 moves GPT-5.6 **4 → 8** and Haiku
**3 → 4**; the v2r4 GPT-5.6 register-nit count 12 → 4.

Notes on the defect column, reported unedited:

- Haiku's single anaphoric-renaming finding is entry 87 (*reminder*): "'a
  matter' is vague". By the class's own terms ("the thing **being defined**
  re-referred to by a vague placeholder"), 'a matter' refers to the thing
  recalled, not to the definiendum — arguably a misapplication of the class
  — but the gate is blind and the score stands as MEASURED; any discount is
  a maintainer judgement, not this session's.
- GPT-5.6 explicitly cleared the same class with reasoning ("occurrences of
  *thing* … do not vaguely rename the headword") and cleared
  non-definitional material explicitly ("kept for ready return … are not
  appended advice, narrative, or commentary").
- No archaic/affected-diction findings of the v2r1 kind ("begotten by him");
  GPT-5.6's harshest register call is "affected circumlocution" on entry 71
  (*maker of*), and both judges independently name entry **62**
  (*kind (gufo:Kind)*) the least natural entry ("abstruse philosophical
  jargon" / "philosophical jargon … 'reidentified'").

## 3. Gate verdict

**The ratified ASM-0703 gate is NOT met as-stated: FAIL.**

- Part 2 (floor ≥5/10 BOTH families): GPT-5.6 8/10 clears; **Haiku 4/10
  misses the floor by one point**. One family short.
- Part 1 (zero hard-defect-class findings BOTH families): staged observers
  and non-definitional material are ZERO from both families; anaphoric
  renaming is zero from GPT-5.6 but carries **one Haiku finding (entry 87)**
  — clean under the v2 tally only if the maintainer discounts it as a
  class misapplication (see §2 note); reported here as a hit.

**Why it fails (named exactly):** the residual unnaturalness Haiku measures
is no longer length (v2's structural ceiling — the ±25% word band and the
mandatory second segment — is gone, and Haiku confirms the entries are
"technically correct"); it is **template uniformity across the set**:
"rigid parallelism and repetitive syntactic templates … 'a [noun] that
[verb phrase]' or 'to [verb]; to [verb]'", "the collection as a whole bears
the marks of algorithmic or template-driven composition" [MEASURED:
gate.new108.haiku.raw.md]. GPT-5.6 sees the same property ("somewhat
artificially uniform … the same polished template") but weighs it at 8/10.
The two families now disagree by 4 points on the same bytes — the failure
is one judge family's weighting of set-level template monotony, not any
per-entry defect class.

## 4. Disposition (coordinator; no freeze action taken)

The freeze precondition for the knull-v2 superseding record is **not met**.
Recommendation to the maintainer (ASM-0706 escalation pattern, second
round):

1. **Cheapest targeted retry:** one more authoring pass aimed at the named
   evidence — vary sentence-frame shape across the set (break the
   semicolon-paraphrase and "a X that Y" templates), fix the two-judge
   consensus nit entry 62 (*kind*) and the seven other named entries — then
   re-run this gate unchanged. The GPT-5.6 half (8/10, zero hard classes)
   suggests the store is close; Haiku's cited evidence is concrete and
   actionable.
2. Alternatively the maintainer may re-rule on the instrument (e.g. whether
   a set-level monotony penalty from one family should block a per-entry
   quality gate, and whether the entry-87 finding is inside the anaphoric
   class) — that is a ratification question, not a measurement one.

Until one of those happens: **do not freeze; the GPU kernel-necessity run
stays blocked on this gate.**

Raw evidence: `poc/knull/quality-gate-v3/gate.new108.gpt56.raw.md` (sha256
`408ad0b4…3e115`), `gate.new108.haiku.raw.md` (sha256 `310ffb74…0767d`),
`gate.new108.haiku.events.jsonl`, `gate.new108.gpt56.err`,
`gate-tally.json`, `tally.sha256`.
