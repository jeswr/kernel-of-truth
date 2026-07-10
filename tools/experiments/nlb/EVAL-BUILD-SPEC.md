# EVAL-BUILD-SPEC — blind EVAL/PROBE phrasing build for l3a-parse / a5-nl

Executor: **Opus runner** (mechanical build; run != design). The designer
(Fable) must NOT author or edit any phrasing. Budget: the records' usd_cap 12
covers this authoring (~1,831 eval + 120 probe items + 2 audit passes of
agent API spend); no GPU, Tier 0. Foreground gates; concurrency cap 5.

BLINDNESS ORDER (binding, design doc §5.3): the front-end shas are ALREADY
pinned in both DRAFT records. If ANY file under `tools/experiments/nlb/` or
`analysis/{l3a_parse,a5_nl}.py` changes after this build starts, STOP — that
mints a new record id; report to the coordinator instead of proceeding.

## Per vertical (l3a, then a5) — steps

1. **Packets** (deterministic, $0):
   `python3 tools/experiments/nlb/gen_author_packets.py --vertical <v>`
   → `data/nlb-phrasings-<v>/packets/` (eval batches of 100 + probe + packet
   manifest). Commit as-is; never edit a packet.

2. **EVAL authoring** (the only spend): for EACH `packets-eval-NNN.jsonl`,
   invoke ONE FRESH agent identity (a new conversation/agent with NO repo
   access, NO tools, NO memory of this programme) whose ENTIRE context is:
   the pinned `data/nlb-phrasings-<v>/prompt-eval.md` + that one batch file's
   lines. One identity per batch; identities must be pairwise distinct and
   distinct from every DEV/probe/audit identity. Save each raw transcript
   under `data/nlb-phrasings-<v>/transcripts/eval-NNN.txt` (prompt + batch +
   raw output, verbatim). Concatenate the returned `{qid, text}` lines in
   packet order into `data/nlb-phrasings-<v>/eval.jsonl`.
   - Malformed/short/refused outputs: re-invoke a NEW fresh identity for the
     affected batch (never show it the failed output); note the retry in the
     transcript directory. Never hand-edit a phrasing.

3. **PROBE authoring**: one further fresh identity per vertical authors
   `packets-probe.jsonl` under `prompt-probe.md` → `probe.jsonl` +
   `transcripts/probe.txt`. Same rules.

4. **Lints (G3)**:
   `python3 tools/experiments/nlb/nlb_lint.py --vertical <v> --receipt`
   must exit 0 with `"checked": {"dev": true, "eval": true, "probe": true}`.
   - On EVAL-DIVERSITY / EVAL-SCAFFOLD findings: re-author ONLY the affected
     family's items via a new fresh identity given the same packet lines plus
     the single extra sentence "Use a different sentence construction for
     each item." (append that invocation to the transcripts). On any other
     finding (leakage, count, form): re-author the affected batch fresh.
   - Never fix a finding by editing text yourself.

5. **Recoverability audit (§5.5, blocks freeze)**: take a deterministic
   60-item sample of `eval.jsonl` (first item of each family in qid order,
   then round-robin by family until 60). Give ONLY those `{qid, text}` lines
   + `prompt-audit.md` to a fresh judge identity. Score recovery against the
   packets: an item is RECOVERED iff shape matches the packet's shape and
   the entity label matches (case/hyphen-space-insensitive) and (where
   packeted) the rel/concept label matches up to inflection. Write
   `data/nlb-phrasings-<v>/audit-recoverability.json`
   `{n, recovered, rate, misses:[qid...], judge_transcript_sha256}` +
   transcript. **Rate < 0.95 blocks freeze** — report to the coordinator;
   do not re-roll the judge.

6. **Corpus pin**: `python3 tools/registry/corpus-pin.py nlb-phrasings-<v>`
   → write the digest into the record's `pins.corpus_hashes` entry
   (replacing the PINNED-AT-INPUTS placeholder), and set
   `EXPECTED_PHRASINGS_SHA256` in `analysis/l3a_parse.py` / `analysis/a5_nl.py`
   to the sha256 of the corresponding `eval.jsonl`, then re-pin that analysis
   script's sha256 in the record. (These two record edits are the ONLY edits
   this build makes to `registry/experiments/*.json`.)

7. **Smoke** ($0): `nlb_instrument.py --vertical <v> --mock` must stay green,
   and `analysis/<record>.py --selftest` must pass.

## Hand-back

Report: per-vertical lint receipt (green), recoverability rates, corpus
digests, identity ledger (batch -> opaque identity id; no account handles
anywhere in registry/**), changed-file list. The coordinator then routes the
independent skeptic re-attack (design doc §11 item 6) and only after that the
prereg-freeze (item 7). Mock bodies (phase=mock) must never reach verdict-gen.
