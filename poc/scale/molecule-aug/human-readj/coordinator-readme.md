# s5-human-readj input packet — coordinator instructions

This directory is the FROZEN input packet for the 2-human fidelity
re-adjudication (registry/experiments/s5-human-readj.json). It was built
deterministically by `poc/scale/molecule-aug/human-readj/build_kit.py` from
the existing molecule-S5 re-pilot artefacts. Nothing here is to be
regenerated; any content change makes the run exploratory, full stop.

## Contents

- `items/<id>.txt` — the 95 arm-blind adjudication items (byte-copies of the
  re-pilot's expanded, provenance-free judge inputs). SAFE to show humans.
- `order.json` — the pinned shuffled presentation order (seed
  `s5-human-readj/1|order|20260716`). SAFE to show humans (ids only).
- `rubric.md` — the human rubric. SAFE to show humans (it IS for them).
- `reconciliation.md` — the pinned reconciliation rule. SAFE to show humans
  only AFTER both raw sheets are complete and hashed.
- `answers-template.csv` — the per-adjudicator answer sheet skeleton, already
  in pinned order. Give one copy to each adjudicator.
- `key.json` — **COORDINATOR ONLY. NEVER show any part to an adjudicator.**
  Arm/cell identity, proxy verdicts, pins. The analysis reads it.
- `manifest.json` — per-file sha256 pins (tamper check).

## Building the spreadsheet (blinding is procedural — follow exactly)

1. Recruit TWO kernel-naive human adjudicators (no prior work on this
   project's kernel, records, or judging; disclose sourcing in the run log by
   pseudonym only: judge-H1, judge-H2).
2. For each adjudicator, build a spreadsheet with one row per line of
   `answers-template.csv` (pinned order) and, per row, the FULL text of
   `items/<item_id>.txt` (or a link to a rendered copy of just that file).
   The sheet must contain NOTHING else: no arm, no concept-source, no cell,
   no proxy verdicts, no per-item metadata beyond the item text and id.
3. Hand each adjudicator: their sheet + `rubric.md`. Do NOT hand
   `reconciliation.md` yet (it describes the discussion step; independence
   first). Both work alone, in the same pinned order.
4. When BOTH sheets are complete: export both to CSV
   (`order_index,item_id,verdict,missing,audit`), sha256 both files, record
   the hashes in the run log. Only then compute the discordant list and run
   `reconciliation.md` verbatim. Export the consensus sheet
   (`item_id,consensus,audit`).
5. Run the pinned analysis:
   `python3 analysis/s5_human_readj.py --h1 <h1.csv> --h2 <h2.csv> --recon <recon.csv>`
   It re-verifies every pin (fail-closed) and emits the registered output
   fields. Grading is verdict-gen from that JSON — never by hand.

## Hard rules

- Humans never see: arm labels, the words "flat"/"molecule", generator or
  model names, proxy/LLM verdicts, this file, `key.json`, results, or any
  project doc. They see: item text, item id, rubric, their own sheet.
- No LLM touches any part of the adjudication, tie-break, or transcription
  (transcription must be mechanical copy, spot-checked against the pinned
  item shas).
- The exhausted cell `conception.mol-fable` is never shown to anyone; it is
  scored LOSSY (ITT) inside the analysis automatically.
