# knull-v4 — blind two-family quality gate (ASM-0703 re-run on the frame-variation retry)

> STATUS: **PROVISIONAL** — MEASURED gate result, 2026-07-11, Fable agent
> session (maintainer issue 17, deliverable 3). This doc records the ASM-0703
> re-run on the v4 store, the option-A frame-variation retry authored after
> the v3 gate failed on set-level template monotony
> (docs/next/analysis/knull-v4-quality-gate.md's predecessor,
> docs/next/analysis/knull-v3-quality-gate.md). It is a readout, not a freeze
> action: nothing is frozen by this session. Raw evidence:
> `poc/knull/quality-gate-v4/` (prompt, order map, both judges' raw outputs +
> event transcripts, `gate-tally.json` with sha256 pins, `tally.sha256`).
>
> Tag convention: `[MEASURED: ref]` = observed result inside its envelope;
> `[STIPULATED: id]` = inherited design choice.

## 1. The store under test

`poc/knull/inputs-v4/plain-authored.json` v4.0.0, sha256
`97609ab…c0d2` — all 108 definitions re-authored with deliberately varied
sentence framing (mixed genus-first / synonym-first / fronted-restriction /
appositive leads; the v3 semicolon-paraphrase pairs eliminated — 108/108
single-segment), targeting the v3 gate's named evidence: the "a [noun] that
[verb phrase]" and "to [verb]; to [verb]" skeletons, the eight judge-named
nit entries (archived, cold, conversation, kind, maker of, open, reminder,
useful) and Haiku's four cited monotony exemplars (bear, birth, day,
father). Same relaxed Option-B contract as v3 (L-3 dropped, L-4 ≥1 admissible
segment); every other G-1 clause enforced and green:
`poc/knull/lint_plain_store_v4.py` PASS 108/108, register-ratio min 0.25,
median 0.467, own-gloss Jaccard all < 0.5
[MEASURED: poc/knull/inputs-v4/g1-lint-report.json].

## 2. Instrument fidelity (pinned protocol, replicated exactly)

- Same two-part instrument as v2/v3, byte-identical header/rubric — only the
  store path changed (unified diff of the builders: path lines + docstring
  only); the deterministic ascending-label order map is byte-identical to the
  v2/v3 pinned map [MEASURED: diff + json equality, 2026-07-11].
- Prompt `prompt.new108.txt` sha256 `feb8867…537c9b`, 10,044 chars (v3:
  9,248). Blindness (ASM-0701 mechanics): headwords withheld, definition
  texts only, no project/NSM/experiment context, judges never told a gate or
  comparison set exists; blinding grep (`kernel|nsm|truthstyle|f2b|knull`)
  zero hits on the prompt and both raw outputs [MEASURED].
- Judge families, per the pinned invocations:
  - **GPT-5.6** (`gpt-5.6-sol`), codex-cli **0.144.1** exec, reasoning effort
    **high**, `-s read-only --ignore-user-config --skip-git-repo-check
    --ephemeral --disable memories --disable standalone_web_search`, empty
    out-of-repo workdir; zero tool/command events in the `--json` stream
    [MEASURED: `gate.new108.gpt56.stdout.log`].
  - **Claude Haiku 4.5** (`claude-haiku-4-5-20251001`), headless `claude -p`
    per `poc/truthstyle-2x2/judges-invocation.md` §4.3 **+ §4.3.1**
    (`MAX_THINKING_TOKENS=0`, `--tools ""`, `--setting-sources ""`,
    `--strict-mcp-config`, `--no-session-persistence`, subscription auth,
    claude-code 2.1.201). Tripwires all green: init `tools==[]`,
    `mcp_servers==[]`, `apiKeySource:"none"`, single text block,
    `num_turns==1`, `permission_denials==[]`, `modelUsage` keys ==
    {`claude-haiku-4-5-20251001`} [MEASURED: `gate.new108.haiku.events.jsonl`].
- One blind full-108 read per family; FIRST VALID ANSWER IS FINAL — no
  re-rolls [STIPULATED: ASM-0241 discipline, carried by the v2/v3 gates].

## 3. Measured result

| | GPT-5.6 (effort high) | Haiku 4.5 (headless) |
|---|---|---|
| **Naturalness (1–10, floor ≥5 both)** | **4/10** — **FAIL** | **3/10** — **FAIL** |
| Anaphoric renaming | none found (explicitly cleared) | **2 findings** (entries 31, 37) |
| Staged observers | none found (explicitly cleared, incl. 27/67) | **4 findings** (entries 27, 38, 67, 104) |
| Non-definitional material | **1 finding** (entry 62, permanence clause) | **8 findings** (11, 15, 21, 28, 47, 83, 88, 103) |
| Register/word-choice nits (non-blocking residual, per the v2 tally treatment) | 15 | 7 |

Context row [MEASURED: quality-gate-v2/v3 tallies]: old-108 store 3/10
(GPT-5.6); v2 final 4/10 / 3/10; **v3 8/10 / 4/10**; v4 **4/10 / 3/10**.
The frame variation moved GPT-5.6 **8 → 4** and Haiku **4 → 3**.

Notes on the defect columns, reported unedited:

- The two families **directly contradict each other** on staged observers:
  Haiku flags "the eye" / "organ of sight" / "the naked eye" in entries 27,
  38, 67, 104; GPT-5.6, on the same bytes, writes "references to *the eye*
  in 27 and 67 describe visual perception as part of the meaning; they do
  not invent generic onlookers."
- Haiku's eight non-definitional findings treat standard lexicographic
  function/context clauses as defects (e.g. *box* "used for holding or
  carrying goods", *condolence* "addressed to the bereaved or to one in
  misfortune") — arguably misapplications of the class by its own terms
  ("a clause that does not serve to state what the word means"); the counts
  stand as MEASURED, any discount is a maintainer judgement.
- Haiku lists entry 31 (*day*) among the MOST natural entries and among the
  LEAST natural entries **in the same answer**.
- Entry 62 (*kind*, gufo:Kind) — the v3 two-judge consensus-worst — draws
  ZERO register findings from either family in v4; GPT-5.6's sole hard-class
  finding is that its permanence clause ("so that it remains of that class
  for as long as it exists") is an appended metaphysical claim.

## 4. Gate verdict

**The ratified ASM-0703 gate is NOT met: FAIL — and now by BOTH families.**

- Part 2 (floor ≥5/10 BOTH): GPT-5.6 4/10, Haiku 3/10 — both short.
- Part 1 (zero hard-defect-class findings BOTH): GPT-5.6 carries one
  non-definitional finding (entry 62); Haiku carries findings in all three
  hard classes.

**Why it fails (named exactly):** the retry succeeded at its stated target —
neither judge reports rigid parallelism, repetitive templates, or
semicolon-paraphrase monotony anywhere in either answer — but the varied
framing itself reads to both families as mannered: "systematically
manufactured in an old-fashioned pseudo-lexicographic voice … recurrent
balanced clauses and literary circumlocutions" [MEASURED:
gate.new108.gpt56.raw.md], "syntactic over-formality masquerading as
precision … theatrically formal" [MEASURED: gate.new108.haiku.raw.md]. The
set-level failure mode INVERTED from too-uniform (v3) to too-mannered (v4).

**Instrument observation (for the maintainer, not adjudicated here):** across
v3 → v4 the same instrument on re-wordings of the same 108 concepts measured
GPT-5.6 8 → 4 and produced mutually contradictory set-level diagnoses and
inter-family contradictions on named defect classes. Combined with the v3
readout's §3 note (the v3 failure was one family's weighting of a set-level
property), this is direct evidence on the ASM-0706 question of whether the
two-family set-level naturalness floor is a stable instrument for a control
store, i.e. evidence relevant to option (B) (accept as-is for a control) or
an instrument re-ruling. That is a ratification question for the maintainer.

## 5. Disposition (no freeze action taken)

The freeze precondition is met by NEITHER store. Both stores, both gate
readouts, and the actual small-model sample responses
(`poc/knull/sample-responses.md` — what an LLM actually generates when
handed each store as context) go to the maintainer under issue 17. Until a
maintainer ruling: **do not freeze; the GPU kernel-necessity run stays
blocked on this gate.**

Raw evidence: `poc/knull/quality-gate-v4/gate.new108.gpt56.raw.md` (sha256
`fcf299c…f7cc`), `gate.new108.haiku.raw.md` (sha256 `0cf9c76…b498`),
`gate.new108.haiku.events.jsonl`, `gate.new108.gpt56.stdout.log`,
`gate-tally.json`, `tally.sha256`.
