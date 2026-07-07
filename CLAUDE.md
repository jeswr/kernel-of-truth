# Project Instructions for AI Agents

This file provides instructions and context for AI coding agents working on this project.

<!-- BEGIN BEADS INTEGRATION v:1 profile:minimal hash:7510c1e2 -->
## Beads Issue Tracker

This project uses **bd (beads)** for issue tracking. Run `bd prime` to see full workflow context and commands.

### Quick Reference

```bash
bd ready              # Find available work
bd show <id>          # View issue details
bd update <id> --claim  # Claim work
bd close <id>         # Complete work
```

### Rules

- Use `bd` for ALL task tracking — do NOT use TodoWrite, TaskCreate, or markdown TODO lists
- Run `bd prime` for detailed command reference and session close protocol
- Use `bd remember` for persistent knowledge — do NOT use MEMORY.md files

**Architecture in one line:** issues live in a local Dolt DB; sync uses `refs/dolt/data` on your git remote; `.beads/issues.jsonl` is a passive export. See https://github.com/gastownhall/beads/blob/main/docs/SYNC_CONCEPTS.md for details and anti-patterns.

## Session Completion

**When ending a work session**, you MUST complete ALL steps below. Work is NOT complete until `git push` succeeds.

**MANDATORY WORKFLOW:**

1. **File issues for remaining work** - Create issues for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **PUSH TO REMOTE** - This is MANDATORY:
   ```bash
   git pull --rebase
   git push
   git status  # MUST show "up to date with origin"
   ```
5. **Clean up** - Clear stashes, prune remote branches
6. **Verify** - All changes committed AND pushed
7. **Hand off** - Provide context for next session

**CRITICAL RULES:**
- Work is NOT complete until `git push` succeeds
- NEVER stop before pushing - that leaves work stranded locally
- NEVER say "ready to push when you are" - YOU must push
- If push fails, resolve and retry until it succeeds
<!-- END BEADS INTEGRATION -->


## Build & Test

```bash
# encoder package (@jeswr/kernel-encoder)
cd encoder && npm install && npm test        # tsc build + node:test property suites

# Phase-X harnesses (pre-registered in docs/poc-design.md)
cd poc && npm install
npm run x0          # golden vectors / byte-determinism (verify against committed fixture)
npm run x0:write    # regenerate goldens — ONLY on a deliberate encoder version change
npm run x1          # adversarial single-edit margins, reduced n=500
npm run x1:full     # full pre-registered n=10^4 run (hours; niced, checkpointed)
npm run x2          # decode recovery by (depth x clause-count) cell
npm run x3          # polarity pathology + weighting sensitivity
npm run x4          # JL projection distortion (8192->512, 8192->576)
```

Reports land in `poc/results/` (JSON + markdown). All compute-heavy scripts are
`nice -n 10`'d and checkpointed for this box's 2 shared cores.

## Architecture Overview

- `encoder/` — deterministic explication->vector encoder v0 (construction B:
  exact Hadamard TPR within clauses; whitened unitary circular-convolution HRR
  across clauses/depth), decoder with confidence reporting, 65-prime profile-1
  lexicon data, seeded synthetic generator + single-edit mutator, and the
  encoder content-hash pin. Zero runtime deps; node:crypto + own FFT.
- `poc/` — Phase-X harnesses only (X0-X4). Keep harness code OUT of encoder/.
- `docs/`, `reports/`, `notes/` — design record, wave-1 evidence, panel notes.
  Spec anchors: docs/architecture.md §1 (encoder), docs/poc-design.md Phase X
  (pre-registered tests), reports/deterministic-concept-vectors.md §7.

## Conventions & Patterns

- Every mathematical choice in encoder code carries a comment citing its
  source (report section). No silent fallbacks; fail closed with ERR_* codes.
- The encoder content-hash pins {schema, algorithm, D, codebook, weighting};
  changing any of these is an encoder version change: bump ALGORITHM_VERSION,
  regenerate X0 goldens deliberately, re-run Phase X.
- Synthetic generation takes an explicit seed; the ENCODER itself is seeded by
  nothing (SHA-256 over fixed labels only).
