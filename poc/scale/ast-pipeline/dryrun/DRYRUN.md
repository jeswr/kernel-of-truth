# DRY RUN result (authoritative; supersedes DRYRUN.auto.md, the script-generated summary)

Date: 2026-07-14. Concepts (deliberately OUTSIDE the 24-concept sample, both
Luna-lossy, both S4-eligible): **pull** (S3 + S4 merge), **dig** (S3 + S4 +
the deliberate `claude -p` path check). 9 nested invocations attempted across
two dryrun passes (the second pass proving resume/retry semantics).

## Verdict per invocation path

| path | result | evidence |
|---|---|---|
| `claude -p` (haiku45, forcing prompt) nested in run_pipeline.py → define_concept.py | **PASS** | `gen-claude/dig.haiku45.json`: full kernel-v1 record, mechanical checks clean, encoder gate PASS, self-flag lossy, cost $0.0252, rc=0. On re-run: correctly skipped (resume). |
| `codex exec` (gpt-5.6-luna; S3 forcing ×2, S4 merge ×2) nested the same way | **BLOCKED — environment, not script** | codex launches, streams `thread.started`/`turn.failed` events, fails closed with full provenance after 3 attempts (~7 s each): `refresh_token_invalidated` / "Your session has ended. Please log in again." |
| codex auth in the DEFAULT home (control, trivial prompt, outside the pipeline) | same 401 `refresh_token_invalidated` | the revocation is global (`~/.codex/auth.json` last_refresh 2026-07-07), NOT an artefact of the isolated-home copy pattern. |
| prep (blind judge-input build) over the dryrun concepts | **PASS** | `judge-inputs/{dig,pull}.txt` (anonymised bare explications), `judge-key.json`, `strategies.json`, `candidates.json` built. |
| resume/retry rule | **PASS** | transport-only failure reports preserved as `*.report.failed-1.json` and retried; the successful claude record skipped, never re-billed. |

## Bottom line

**Nested invocation works.** The script correctly drives both CLIs end-to-end;
the only failure is a revoked OpenAI/codex subscription token — an
environment blocker requiring an interactive `codex login` by the maintainer
(the builder cannot re-auth headlessly and did not touch auth state).

After re-login, verify with:

```bash
cd poc/scale/ast-pipeline && python3 run_pipeline.py dryrun
```

— the transport-failed codex calls retry automatically (prior failures are
preserved as `.failed-N.json`); expect 4 fresh Luna records in
`dryrun/gen-s3/` + `dryrun/gen-s4/` and VERDICT: PASS. Then launch per
LAUNCH.md. Dry-run outputs live only under `dryrun/`; the real run never
reads them.

Offline plumbing (no API): `prep` over the real 24-concept sample produced
124 gate-clean records → 106 unique blind candidates; `score` + tie-break
detection exercised end-to-end with synthetic judgments in a scratch dir
(deleted; no synthetic data remains in this tree).
