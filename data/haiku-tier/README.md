# haiku-tier — the modelAuthored concept tier (Wikipedia/Wiktionary-sourced, claude-haiku-authored)

Programme: a prioritised inventory of English concept lemmas, definitional
text fetched from Wiktionary/Wikipedia (revisions pinned), formal definition
candidates authored by claude-haiku under fail-closed mechanical gates, and
emitted as `modelAuthored` records — a provenance tier explicitly BELOW
Explicated and hand-authored Molecule (see `modelauthored-schema.md` and
docs/design-bulk-kernel.md's honesty architecture).

- `inventory/` — stage 0: `build-inventory.py` (deterministic; pinned sources
  in `pins.json`, sha256-checked), `inventory.jsonl` (ranked, 4 bands),
  `inventory-excluded.jsonl` (audit trail), `sizing.md`.
- `fetch/` — stage 0: polite cached Wiktionary/Wikipedia fetcher
  (`fetch-definitions.py`), 99-lemma success-rate report (`fetch-report.md`).
- `s1-experiments/` — stage 1: prompting-framework experiments on 50 concepts
  (5 frameworks), mechanical gate evaluation (`gates.mjs` — runs the real
  encoder gates and a verbatim §3.5 port), fidelity comparison, and the
  quality readout `s1-report.md` (the stage-2 go/no-go evidence).
- `runner/` — the volume runner (`run-volume.py`): session-budget governor
  (max calls per 5h window, low fixed concurrency, usage-limit back-off,
  full checkpointing, per-window usage log). **Not yet run** — stage 2 is
  coordinator-gated (kernel-of-truth-63c).
- `records/`, `volume/` — created by the runner: gate-passing modelAuthored
  records; failures/cannot-formalise/usage logs.
- `cache/` — gitignored working set (pinned source files, fetched
  definitions). Re-derivable from `pins.json` + the fetcher.

Boundaries: this stream owns `data/haiku-tier/` only. `data/lexical-wn31` is
a different agent's stream; this directory keeps its own pinned WordNet copy
in cache and never touches that one.
