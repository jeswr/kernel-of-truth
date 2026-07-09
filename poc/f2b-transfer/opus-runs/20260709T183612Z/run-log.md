# f2b-transfer — Opus-runner execution log (§4.7 pre-data RESET-REFREEZE)

- run-ts (UTC): 20260709T183612Z
- runner_agent_id: kern/opus-runner-7 (pseudonym `runner-7`)
- role: experiment-runner (Opus execution) — EXECUTE a Fable-frozen design; never design, never conclude
- experiment: f2b-transfer (registry/experiments/f2b-transfer.json)
- bounded task: MECHANICAL reset-refreeze under the SAME experiment id after the
  maintainer approved Fable's §4.7 adjudication-rule clarification (S1–S7 + the
  A-direction disclosure), then re-render the §4.7-dependent judge artifacts.
  Fable had ALREADY edited design.md (items 1–6 byte-unchanged); this run applied
  only the correction record + record reset/refreeze + the mechanical re-renders.
- outcome: refrozen under a new frozen_sha256; correction record written; judge-1
  package + judge-2 prompt re-rendered; all pre-declared verifications PASS. No GPU,
  no codex, no adjudication datum, no interpretation, no git push.

## Pre-conditions verified (fail-closed, before any write)

- design.md already edited by Fable: sha256 `4d0f7a70f3ecce6aa55665bd74f74e6ca24994b4e4e7ff795c70564a55ab9d0f` (== target).
- f2b-transfer ABSENT from `registry/gng0-signoff.json` frozen_records.
- `results-log/f2b-transfer.jsonl` ABSENT (zero adjudication data; P-9 cutoff not crossed).
- `judge-2-prompt-template.txt` at its recorded pin `65ea3c13…` before this run.
- `items-judge-1.jsonl` committed at HEAD and content sha256 `57070307…` (corpus byte-unchanged).
- Lawful reset-refreeze precedent: `registry/corrections/f2b-replicate/1-prefreeze-correction.json`.

## Sequence + sha transitions

1. Wrote `registry/corrections/f2b-transfer/1-prefreeze-correction.json`
   (kot-correction/1; seq 1; kind `pre-final-reset-refreeze`; author `runner-7`;
   authorized_by "maintainer approval 2026-07-09 (§4.7 …S1–S7…)"; kill_criterion_status
   "kill/gate verbatim text UNCHANGED"). refrozen_sha256 placeholder, filled at step 3.
   correction TS: `date -u` = 2026-07-09T18:36:12Z.
2. Reset `registry/experiments/f2b-transfer.json`: status FROZEN→DRAFT; prereg_doc.sha256
   `c4942eaf…` → `4d0f7a70…`; removed stale frozen_sha256/frozen_at/frozen_by (optional
   in DRAFT). d-qa-t corpus pin `7179ee67…` RETAINED (corpus byte-unchanged). Removed the
   `f2b-transfer` entry from `registry/frozen-index.json`.
3. `prereg-freeze --experiment f2b-transfer --agent-id runner-7` (dry-run PASS, then real):
   - supersedes_frozen_sha256 (old): `f00fd28fb84f96bfbef784091b28e808681aee6bdeab50c48cb035ebcc6baa27`
   - **refrozen_sha256 (new):        `b341a0901e12023d3c56bdc196be0b9c492c7d348f988416d7e9c43aade20879`**
   - frozen_by `runner-7`, frozen_at `2026-07-09T18:37:49Z`, pause_flags none.
   - wrote the new sha into the correction record's refrozen_sha256.
4. Re-rendered the judge-1 package (builder + this log in this dir; outputs to
   `poc/f2b-transfer/judge-1-package/`), deterministic (re-run byte-identical):
   - `PROTOCOL.md` = verbatim copy of the NEW design.md §4 (now incl. §4.7 S1–S7 +
     A-direction disclosure); wrapper header note advanced to prereg_doc `4d0f7a70…`.
     §4 body asserted byte-identical to the design.md §4 slice. sha256 `6e6fe8e1…`.
   - `README.md` per Fable §B: added the "how to judge them" paragraph after the two
     format bullets (§B.2, verbatim); replaced the mandatory-escape final sentence
     (§B.3, verbatim); re-pointed the recording instructions at the self-contained
     `judge-1-adjudication.csv` (§B.1 — the over-reaching "close-but-not-quite → NONE
     is §4's stance" sentence never existed in this README, so nothing was removed);
     "Authoritative rules" left unchanged (§B.4). sha256 `d71408f2…`.
   - `items-judge-1.md` per Fable §D: third preamble bullet reworded; git diff confirms
     ONLY that line changed and the `## 1`-onward item region is byte-identical to HEAD.
     sha256 `80da9ce6…`.
   - `judge-1-adjudication.csv` (NEW, single self-contained answer file): Fable's exact
     13-line INSTRUCTIONS block sourced byte-for-byte from judge-instructions-wording.md
     §A (superseded "close but not quite right → NONE" line absent), header
     `position,question,allowed_answers,your_answer,comment`, 360 rows (216 MCQ / 144
     claim) with questions+options inline and blank your_answer/comment, keyed by
     position. sha256 `d7db2319…`.
   - `items-judge-1.jsonl` UNTOUCHED — sha256 `57070307…` (byte-identical to HEAD/committed).
5. `data/d-adj-t/judge-2-prompt-template.txt` per Fable §C: replaced the "Answer the item…"
   + "The item offers an escape answer…" paragraphs (and the "Do not force a choice…"
   line) with the §C block (task/how-texts-read/MCQ/yes-no/independence paragraphs),
   sourced byte-for-byte from the §C fenced block. sha256 `65ea3c13…` → `f21bfce38eda617fe6733efca75e8a2b3e754711931703119ef7c6602749931d`.
   Propagated the recomputed sha to BOTH references of the authoritative bytes:
   `judge-2-prompt.md` (line 4) and `judge-2-invocation.md` (line 21); refreshed the
   informative fenced copy in judge-2-prompt.md to the new bytes (verified equal to the
   .txt) and extended its rationale table with the "judging standards block" row.
   Lawful: d-adj-t corpus pin is still an unfilled PINNED-AT-INPUTS placeholder.

## Verification results (all PASS)

- `registry-check --frozen-drift` → `ok frozen-drift: f2b-transfer (b341a090)`, PASS
  (reproduces the new frozen_sha256).
- `registry-check --chain --claims` → PASS (chain ok; register + 46 doc(s) pass
  claims-check; no kb/* errors present in this tree).
- `registry-check --corpus-pins --reuse --append-only` → PASS.
- `judge-1-adjudication.csv` re-reads to 360 item rows, positions 1..360 contiguous,
  all your_answer + comment blank, header row exact.
- `items-judge-1.jsonl` sha256 `57070307…` — byte-identical to the committed corpus.
- record.frozen_sha256 == frozen-index[f2b-transfer] == captured `b341a090…`.

## Scope / boundary notes (no science, no interpretation)

- NO design change: arms, corpus, seeds, k=4, endpoints, gates, separation gate, Holm
  family, verdict rules, kill_criterion_verbatim and extrapolation_envelope_verbatim are
  byte-identical to the superseded freeze (only prereg_doc.sha256 + freeze stamps moved).
- `response-template.csv` (the older two-file answer surface) is left in place but is no
  longer referenced by README (superseded by the self-contained judge-1-adjudication.csv);
  left for the coordinator to decide whether to remove — not deleted here (out of task scope).
- Unrelated working-tree changes from other concurrent sessions (`.beads/*`,
  `data/haiku-tier/*`, `docs/*`, `tools/mint/*`, `poc/f2b-transfer/opus-runs/20260709T174657Z/`)
  were NOT touched. Fable's design.md edit and judge-instructions-wording.md are inputs, not
  authored here.
- Artifacts left UNCOMMITTED for the coordinator (RT-15 external post + commit + push +
  maintainer re-ack are the coordinator's). No git push. No GPU. No codex. No adjudication datum.

## Artifacts written / changed by this run

Created:
- `registry/corrections/f2b-transfer/1-prefreeze-correction.json`
- `poc/f2b-transfer/judge-1-package/judge-1-adjudication.csv`
- `poc/f2b-transfer/opus-runs/20260709T183612Z/build-judge1-package.py`
- `poc/f2b-transfer/opus-runs/20260709T183612Z/run-log.md` (this file)

Modified:
- `registry/experiments/f2b-transfer.json` (reset → refreeze; new frozen_sha256)
- `registry/frozen-index.json` (f2b-transfer → new frozen_sha256)
- `poc/f2b-transfer/judge-1-package/PROTOCOL.md`
- `poc/f2b-transfer/judge-1-package/README.md`
- `poc/f2b-transfer/judge-1-package/items-judge-1.md`
- `data/d-adj-t/judge-2-prompt-template.txt`
- `data/d-adj-t/judge-2-prompt.md`
- `data/d-adj-t/judge-2-invocation.md`
