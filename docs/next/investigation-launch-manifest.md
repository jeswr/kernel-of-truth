# Investigation Launch Manifest

**Date:** 2026-07-10 · **Branch:** `opus/f2b-replicate-rightsize` (HEAD `2e2c24b` == `origin`; all commits below pushed) · **Author role:** opus-coordinator (consolidation only — no design, no freeze, no spend)

Consolidates the 5 investigation lines designed this round from the dedup frontier map (10 launchable lines; the other 5 remain backlog, listed in §E). Each line is DRAFT kot-reg/1, mock-green at $0, claims-check / registry-check clean. **Nothing is frozen; nothing frozen was touched.** Freeze is the coordinator/maintainer gate for every run below.

**Duplication verdict: NONE.** All 5 designers independently re-verified against `registry/ideas.jsonl`, `registry/experiments/*`, and `docs/design-*`; every line reported "none." Two look-alikes are explicitly *not* duplicates: (i) nl-boundary had a concurrent-session intermediate snapshot `b0898eb` of the **same** line id (refined, not duplicated); (ii) knull's requested vector-free arm was **map-resolved at $0** (strip-test 3456/3456 identical verifier decisions) rather than spun up as a separate experiment.

---

## (A) RUNNABLE NOW at ~$0 by Opus

| Line | Ready? | Exact next action / run command | Cost |
|---|---|---|---|
| **claims-envelope-corrections** (prio 3, `d00b617`+`a17a554`) | YES — spec is file-by-file old/new strings + phrasebook + mechanical acceptance checks | Apply §3 mechanical text edits + §4 `tools/registry/audit-status.py` derived-run-state fix + ledger appends + bead `kernel-of-truth-97r`; Fable authors the §5 registry-line appends at execution. Accept = grep sweeps + diff allowlist + `python3 tools/registry/claims-check.py` green. Independent of f2b-transfer. | **$0** |
| **f2b-errors** (prio 1, `4777579`) | YES, but FREEZE-gated + consumes Stage-2 output | 1) Coordinator freeze `python3 tools/registry/prereg-freeze.py registry/experiments/f2b-errors.json`; 2) land R-2 superset-logging fields (`poc/f2b-errors/taxonomy.json`) into Stage-2 harness staging; 3) real run `python3 analysis/f2b_errors.py --cells <stage2-cells.jsonl> --stage2-out <f2b_transfer out.json>`. Mock green now: `python3 analysis/f2b_errors.py --mock`. | **~$0 CPU** |

> Opus may also run every mock harness below at $0 today for regression assurance.

## (B) GPU-GATED / SPEND-GATED — maintainer sign-off before spend

*Compute posture: **Modal** is the working path; **Anyscale $100 cloud** credit is live; **Modal-for-academics** + **ARC** are the bigger unlocks currently being applied for.*

| Line | Type | Compute / cost ask | Blocking gate |
|---|---|---|---|
| **knull-content-injection-ablation** (prio 4, `0d2e07a`/`c150eff`) | GPU | 1× A100-40GB Modal (f2b image), ~4–6 GPU-h, **~$15–30**; caps $60 / 8 GPU-h / 24h wall | Pre-freeze gates G-1..G-5 — **binding: author the plain-dictionary store** (currently a flagged placeholder) — then freeze. Vector-free arm already map-resolved at $0. |
| **truthstyle-2x2** (prio 1, `4777579`) | Paid-API (NOT GPU) | ≤**$40** bounded LLM adjudication (2,424 stateless cross-vendor 3-LLM invocations), CPU otherwise | Freeze **before** Stage-2 unblinds + maintainer sign-off for the ≤$40 spend. Mock green. |
| **nl-boundary** (`l3a-parse` + `a5-nl`) (prio 5, `2e2c24b`) | Paid-API (NOT GPU) | ~**$8–12** agent-API for blind phrasing authoring; usd_cap 12/record; run is minutes of box CPU | Freeze + blind DEV/EVAL phrasing authoring by **fresh non-designer agent identities** (identity-separation protocol); path in bead `kernel-of-truth-dt3w`. Both mocks green. |

## (C) HUMAN-BLOCKED

| Line | Blocker |
|---|---|
| **f2b-transfer Stage-2 / judge-1** (existing line, not part of this round) | Human judge (judge-1) adjudication. Its **Stage-2 unblind is the freeze deadline** for `truthstyle-2x2` + `f2b-errors` — both MUST freeze before any Stage-2 cell launches or any Stage-2 output is inspected. |

> None of the 5 newly-designed lines is human-blocked — their only gates are maintainer freeze + spend sign-off (approvals, not human labor).

## (D) FLAGSHIP — neurosymbolic-architecture line

**`idea-neurosym-kernel-internals`** (prio 2, committed+pushed `24d3a31`). **Status:** design COMPLETE — B-family consolidated under one umbrella idea (constituents parked as staged variants V0–V7, nothing deleted); lints pass, mock green at $0, ASM-0023..0025 registered, nothing frozen.

**Single decisive first experiment — `nsk1`** (DRAFT kot-reg/1, two stages in one record):
- **Stage-0** back-patch rescuable-fraction diagnostic (B5) on kernel-covered 2-hop failure slices — Wilson-LB **≥ 0.15** floor, else cheap family kill.
- **Stage-1** training-free forward-hook loop on **SmolLM2-135M/360M**: patchscope-decode → EXACT lexicon match (no kernel-space cosine/kNN) → l3a kot-axiom engine resolving hop-1 only (gold = generator graph-traversal, structurally independent of engine accept test — the f2b oracle-leakage lesson) → kernel-keyed cached steering write-back (channel **B2**, lit-backed training-free causal-write precedent; gated activation modulation = fallback V2).
- **PRIMARY:** absolute paired accuracy delta vs the strongest matched baseline (identical engine feedback delivered as text via an external F2-topology loop at matched token budget), **TOST ±0.02** for the null; mandatory text-only / kernel-as-text / shuffled-derangement / random-direction / no-op-hook controls + instrument gates. Law-1 clean (steering vectors are the model's own activations).

**Cost:** Tier-2 — 1× A10G (or L4) on Modal, ~8–12 GPU-h, est **$12–20**; requested caps **$60 / 14 GPU-h / 30h wall**. Run is maintainer-gated (Tier-2 sign-off + prereg-freeze), executed by the runner role (run ≠ audit; Codex audits any computed PASS). Mock: `python3 poc/nsk1/nsk1_runner.py --mock`.

---

## Immediate actions for coordinator / maintainer

1. **FREEZE `truthstyle-2x2` + `f2b-errors` before any Stage-2 GPU cell launches or any Stage-2 output is inspected** — both `prereg-freeze.py --dry-run` green now. This is timing-critical (R-2): after Stage-2 unblind they permanently lose confirmatory standing.
2. **Land the R-2 logging handoff** — per-attempt superset fields in `poc/f2b-errors/taxonomy.json` must go into Stage-2 harness staging.
3. **~~Push `4777579`~~ RESOLVED** — origin already contains `4777579`; no push needed (input flag was session-local and is now stale).
4. **At freeze, mint the 4 assumptions** in design doc §7.3 (`truthstyle-2x2`) and note ASM-0023..0025 (`nsk1`); non-fatal PAUSE on ASM-0021 is **expected** (truthstyle-2x2 is part of its resolution path). ID-collision watch on next-free ASM ids (claims-envelope §5 also queues 4 EXTRAPOLATION lines).
5. **Opus can start now, $0:** run **claims-envelope-corrections** §3/§4 edits, and re-run all mock harnesses.

## (E) NOT designed this round — backlog

`g8-mathlib-crawl-materials` [opus-run] · `g3-g9-materials-generation` [fable-design] · `bcov-benchmark-checkability-census` [fable-design] · `a5-llm-prefreeze-repairs` [fable-design] · `research-engine-deltas-d1-d3` [fable-design].

## Spec index

| Line | Design doc | Records | Harness |
|---|---|---|---|
| truthstyle-2x2 / f2b-errors | `docs/design-truthstyle-2x2-f2-taxonomy.md` | `registry/experiments/{truthstyle-2x2,f2b-errors}.json` | `analysis/{truthstyle_2x2,f2b_errors}.py`; `poc/truthstyle-2x2/`; `poc/f2b-errors/`; `data/d-ts/` |
| neurosym-kernel-internals (nsk1) | `docs/design-neurosym-kernel-internals.md` | `registry/experiments/nsk1.json` | `poc/nsk1/`; `analysis/nsk1.py`; `data/nsk1-eval/` |
| claims-envelope-corrections | `docs/design-claims-envelope-corrections.md` | §5 successor lines (author at execution) | `tools/registry/audit-status.py` (fix) |
| knull-content-injection-ablation | `docs/design-knull-content-injection-ablation.md` | (draft in §3) | `poc/knull/` |
| nl-boundary | `docs/design-nl-boundary-l3a-parse-a5-nl.md` | `registry/experiments/{l3a-parse,a5-nl}.json` | `tools/experiments/nlb/` |
