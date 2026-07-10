# d-adj-t-llmproxy — judge-1 STAND-IN adjudication corpus (f2b-transfer-llmproxy stage 1) — UNDER ASSEMBLY

STAND-IN, NOT d-adj-t: this corpus belongs to the SEPARATE experiment
`registry/experiments/f2b-transfer-llmproxy.json` (design note
`poc/f2b-transfer/llmproxy-design.md`), in which a pinned LLM (GPT-5.6-Sol)
fills the judge-1 ROLE because the kernel-naive HUMAN judge-1 required by the
FROZEN f2b-transfer §4 protocol is unavailable. Nothing here fills, feeds, or
amends `data/d-adj-t/` or the frozen f2b-transfer record; the human judge-1
path stays open and solely adjudicating. The record's extrapolation envelope
(clauses 1–6: single judge family, kernel-tradition familiarity, weak
feasibility proxy only) binds every citation of numbers derived from these
bytes.

Frozen contract: the record pins this corpus as `PINNED-AT-INPUTS` — the
kot-corpus-hash/1 digest is computed and written by ops amendment ONLY after
the judge-1p run completes and BEFORE the stage-1 record is appended.

Present now (authored by the Fable designer, sha-pinned in the DRAFT record):

- `judge-1p-prompt-template.txt` — AUTHORITATIVE pinned prompt bytes (the
  judge-2 template with exactly line 1 changed: panel-position pseudonym
  removed; all judging-standards bytes identical)
- `judge-1p-invocation.md` — pinned, capability-VERIFIED codex invocation
  spec (npx-pinned @openai/codex 0.144.1, model gpt-5.6-sol, effort low;
  mechanical for Opus)
- `deranged-probe.jsonl` — 60 deranged-gloss def-match probes (the
  judge-level content-scramble control; correct answer NONE by construction;
  NEVER enter labels or endorsement statistics)
- `deranged-probe-manifest.json` — seeds, derangement map, run order,
  collision log

Reused, judge-agnostic, pinned from `data/d-adj-t/`: the two output schemas
and `judge-2-calibration.jsonl` (preflight only).

Still to arrive (Opus assembly, after the judge-1p run):
`judge-1p-responses.jsonl`, `judge-1p-probe-responses.jsonl`,
`labels-proxy.jsonl` (gold source = judge-1p ALONE; judge-2 columns are
diagnostic), `summary.json` (analysis-input integers + judge sourcing
disclosure). Judge-2's raw responses stay in `data/d-adj-t/` (they are the
in-flight f2b-transfer instrument's output, read here read-only via an
ops-amended artifact pin).

RT-14: nothing in this directory may contain names, emails, or account
identifiers — pseudonym judge-1p only.
