# LAUNCH — coordinator handoff for the ast-pipeline experiment

Exploratory methodology R&D (no prereg, no registry write, no commit).
Design: `DESIGN.md`. Builder: fable (lead designer) — built + dry-ran only.
The coordinator (Opus) owns the full run AND all judging (builder/judge
separation; the builder never grades its own homework).

## Full ~24-concept run — exact commands (run from this directory)

```bash
cd poc/scale/ast-pipeline

# 1. GENERATION (29 new codex/Luna calls; 0 Claude calls; resumable, re-run on interruption)
nice -n 10 python3 run_pipeline.py gen

# 2. BLIND-JUDGE PREP (letter shuffle seed 34; builds judge-inputs/, judge-key.json, strategies.json)
python3 run_pipeline.py prep

# 3. JUDGING (coordinator-only; each resumable; A/B can run concurrently — separate quotas)
nice -n 10 python3 run_pipeline.py judge --judge A --i-am-the-coordinator   # gpt-5.6-sol (codex)
nice -n 10 python3 run_pipeline.py judge --judge B --i-am-the-coordinator   # claude-opus-4-8 (claude -p)
nice -n 10 python3 run_pipeline.py judge --judge T --i-am-the-coordinator   # gpt-5.6-terra, ONLY A/B-disagreed concepts

# 4. SCORE
python3 run_pipeline.py score        # -> results.json + results.md
```

Do NOT show any judge `judge-key.json`, `strategies.json`, `sample.json`,
the consensus-100 reports, or the split-concept adjudication — the judge
inputs in `judge-inputs/*.txt` are the ONLY thing a judge may see (they
contain bare anonymised explications; no self-flags, no model names).

## Judge plan (exact)

- **Judge A = gpt-5.6-sol** via `npx @openai/codex@0.144.1 exec` (xhigh,
  read-only, isolated ephemeral home) — the pinned pattern, invoked through
  `define_concept.run_codex` imported by `run_pipeline.py judge`.
- **Judge B = claude-opus-4-8** via headless `claude -p` (subscription auth,
  MAX_THINKING_TOKENS=0, no tools, identity tripwire) — the pinned pattern,
  via `define_concept.run_claude`.
- **Tie-break T = gpt-5.6-terra** (same codex pattern), automatically limited
  to concepts where A and B disagree on any candidate's verdict; final
  verdict = majority of {A,B,T}; quality = mean(A,B).
- One batched call per concept per judge: system prompt `judge_prompt.md`,
  user message `judge-inputs/<slug>.txt` (order-randomised anonymised
  candidates). 24 A-calls + 24 B-calls + expected ~5–10 T-calls.
- Structural-retry policy: up to 3 attempts per call on non-JSON or
  wrong-shape output only (recorded in `judgments/<J>/<slug>.json`).

## Expected cost (honest; DESIGN.md §7)

- New generation: 29 codex (Luna) calls — subscription quota only;
  ~$0.15–0.35 nominal at API rates (~19k in / ~2.4k out each, ~48 s median).
- Judging: 24 sol + ~5–10 terra codex calls (quota; ~$0.35–1.05 nominal) +
  24 opus48 calls at measured `total_cost_usd` scale (**~$1.50–4.00**, the
  only real Claude-quota draw).
- **Total ≈ $2–5.5 nominal, ~82–101 calls, ~2–3.5 h sequential wall-clock**
  (A and B may run concurrently; the box is API-bound, not CPU-bound).

## What already exists / what is reused

- 600 consensus-100 records reused for S0/S1/S2 — zero regeneration.
- `sample.json` (24 concepts: 4 unanimous-faithful / 12 split / 8
  unanimous-lossy; deterministic URN-stride, adjudication-blind).
- Dry run under `dryrun/` (2 NON-sample concepts) — see `dryrun/DRYRUN.md`
  for the invocation-path verdict (`claude -p` + `codex exec` nested in the
  script). Dry-run outputs stay in `dryrun/`; the real run never reads them.

## BLOCKER (as of 2026-07-14, from the dry run)

The OpenAI/codex subscription refresh token is **revoked**
(`refresh_token_invalidated`, confirmed in both the pipeline's isolated home
AND the default `~/.codex` home; last_refresh 2026-07-07). ALL codex-side
work (S3/S4 generation, judges A and T) is blocked until the maintainer runs
an interactive `codex login`. The `claude -p` side is fully working. After
re-login: `python3 run_pipeline.py dryrun` (auto-retries the transport-failed
calls) should print VERDICT: PASS, then launch as above. Fallback if codex
auth cannot be restored: swap S3/S4 generator and judges A/T to Claude models
— but this draws Claude quota AND forfeits cross-vendor judging, so it needs
a maintainer decision; do not do it silently.

## Known caveats for the readout

n=24 pilot (±~10pp noise); batched per-concept judging can anchor; every
available model authored some consensus-era candidate, so judges may grade
own-model output under blinding (no judge authored any NEW S3/S4 output —
those are all Luna); S2 shares its oracle with the metric (label it the
select-ceiling, not a deployable strategy); 20/144 existing sample records
are gate-invalid (opus48/haiku45) and are excluded from judge pools by
construction. If the run is interrupted anywhere, simply re-run the same
command — every step resumes from files on disk.
