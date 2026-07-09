# d-adj-t — blind adjudication corpus (f2b-transfer stage 1) — UNDER ASSEMBLY

Frozen contract: `registry/experiments/f2b-transfer.json` pins this corpus as
`PINNED-AT-INPUTS` — the kot-corpus-hash/1 digest is computed and written by
ops amendment ONLY after the §4 adjudication completes and BEFORE the stage-1
record is appended (design.md §3.2/§4.5). Do NOT pin early; the stage-2 runner
fail-closes on the pin.

Contents per design.md §3.2 (final state): `PROTOCOL.md` (verbatim §4 copy),
per-judge raw response files, `labels.jsonl`, `summary.json`.

Present now — the judge-2 instrument (the §4.1 "pinned prompt stored in
d-adj-t", authored by Fable, bead `kernel-of-truth-67m`):

- `judge-2-prompt-template.txt` — AUTHORITATIVE pinned prompt bytes
- `judge-2-prompt.md` — informative copy + rationale (judge-1 mirror map)
- `judge-2-invocation.md` — pinned codex invocation spec (mechanical for Opus)
- `judge-2-output-schema-mcq.json`, `judge-2-output-schema-claim.json`
- `judge-2-calibration.jsonl` — 2 preflight-only items (never adjudicated)

Still to arrive (Opus assembly, after judges run): `PROTOCOL.md`, judge-1
re-keyed labels, `judge-2-responses.jsonl`, judge-3 tie-break labels,
`labels.jsonl`, `summary.json`.

RT-14: nothing in this directory may contain names, emails, or account
identifiers — pseudonyms judge-1/judge-2/judge-3 only.
