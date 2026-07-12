# sense-split Stage A — V-A + V-B harness (LAUNCH-READY, HELD)

Implements design §5 of `docs/next/design/sense-split-first-construction.md`
against the built `data/kernel-v1/` Stage-A corpus. **$0 spent: built,
mock-validated, held.** The run awaits (i) the maintainer's explicit go on
the §A redirect (`SSA_MAINTAINER_GO=1`) and (ii) the adjudication §D channel
resolution (proxy pair only if the v2.2 pilot passes AC1≥0.65; else the same
materials go to the two-human panel).

- **V-A** (30 items, `materials/va-items.jsonl`): the 5 g2 sense-channel
  items (011/036/037/070/071) + the friend 040/041 latent pair, re-rendered
  per sense with real sense glosses; resolution criterion pre-stated in
  `materials/resolution-map.json` (expectation ≥4/5, ASM-1907/1918 — a
  readout expectation, not a gate).
- **V-B** (31 items, `materials/vb-items.jsonl`): every binding
  SomeoneRef/SomethingRef/TimeRef/PlaceRef commitment in the 11 explications
  as a per-sense ordinary-meaning claim; the both-yes fraction (Wilson 95%)
  becomes the sense-scoped hard-typing soundness of record, replacing the
  word-scoped 0.3929 (which stands as a lower bound).
- **Judges**: pA = gpt-5.6-sol (pinned codex CLI), pB = claude-opus-4-8
  (maintainer Haiku→Opus directive, issue #25). Machinery ported verbatim
  from the audited `poc/ontology-import-g2-v2/run-ontg2v2.py` (validity,
  retries, blinding scans, checkpoints, live dollar abort). Rubric: the
  pinned v2.2 template, byte-reused.
- **Cost**: expected 142 calls ≈ $1.70 at the pinned $0.012/call bound;
  ceiling 200 calls / $2.40; hard $10 cap. `run-stageA.py dryplan` prints it.
- **Mock**: `python3 run-stageA.py mock runs/mock-<date>` — full pipeline,
  zero LLM calls (green: `runs/mock-20260712/result.json`).

Coordinator launch (verbatim, printed by `dryplan`): see
`materials/manifest.json` and the dryplan output; requires
`SSA_MAINTAINER_GO=1` + `--channel proxy` on each judge phase.
