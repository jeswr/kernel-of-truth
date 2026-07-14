# glm-edrop-0 — freeze-readiness checklist, blockers, and infra/$ estimate

> **Status: FREEZE-PREP ONLY (2026-07-14, Fable, experiment-designer role).
> Nothing here is frozen, run, or committed; the coordinator commits after
> review and the (currently deferred) GPT-5.6 review gate. This document
> states no feasibility conclusion.**
> Companion artifacts produced this pass (uncommitted):
> - `registry/experiments/glm-edrop-0.json` (DRAFT, kot-reg/1; bytes as
>   left this pass sha256
>   cd281c5047f8cfaa08051fce22be01a0f8e3325091ef92993cc55be452c9be26 —
>   informational only; the binding frozen_sha256 is computed at freeze)
> - `analysis/glm_edrop_0_stdin.py` (pinned analysis adapter, sha256
>   f6742504c4a63e25e3a876fe9edb6fdde3f4f4cd0e6b39157bfb453c66504326)
>
> Tag schema CLOSED to four tags (design header convention [R2]):
> MEASURED | LIT-BACKED | STIPULATED | EXTRAPOLATION.

## 1. What was verified this pass (all MEASURED = read/executed this tick)

| # | Check | Result | Evidence |
|---|---|---|---|
| 1 | Experiment id `glm-edrop-0` unused | PASS | no such file under `registry/experiments/`; zero matches for `glm-edrop`/`glm-drop` in `registry/frozen-index.json` [MEASURED: directory listing + grep this tick] |
| 2 | kot-reg/1 schema validity of the DRAFT record | PASS | `jsonschema.validate` green against `registry/schema/kot-reg-1.json` [MEASURED: validation run this tick] |
| 3 | Full prereg-freeze constraint battery (constraints 1–10: exactly-one-primary, metric-pointers ⊆ output_fields, exhaustive verdict rules, five-V metric vector for `efficiency_relevant`, kill + envelope non-empty, corpus-pin verifiability, no account material) | **DRY-RUN-OK** | `python3 tools/registry/prereg-freeze.py --experiment glm-edrop-0 --agent-id writer-9 --dry-run` → `"status": "DRY-RUN-OK"`; non-fatal PAUSE flags on open EXTRAPOLATIONs ASM-2238/2313/2341/2350 (expected; see blockers B2/B6) [MEASURED: dry-run output this tick; wrote nothing — `git status` clean of tool side-effects] |
| 4 | Adapter stdin conformance (the knull/ufo/ddc CLI-only-pin defect NOT repeated) | PASS | invoked as `python3 analysis/glm_edrop_0_stdin.py < stdin.jsonl` with NO argv; reads eligible records on `sys.stdin`; pins re-verified fail-closed; canonical JSON on stdout [MEASURED: end-to-end shell invocation this tick] |
| 5 | Adapter byte-determinism | PASS | two invocations on identical stdin → `cmp` byte-identical stdout [MEASURED: this tick] |
| 6 | Adapter drives ALL verdict branches on synthetic rows | PASS | `--selftest` green: PASS shape on BOTH inference branches (enumeration + implemented BCa fallback); not-demonstrated-D1; planted-harm KILL; floor-bound D0; D2 UNINFORMATIVE (Jaccard); clean-miss-decisive aggregation; load-VOID; gate-failure (INSTRUMENT-INVALID shape); m-drng exclusion bound; 11/11 hardened rejections fail-closed; pin round-trip byte-stable; 48/48 declared output_fields present on both branches [MEASURED: selftest output this tick] |
| 7 | Record `output_fields` == adapter `OUTPUT_FIELDS`, and script sha256 pin correct | PASS | exact list equality (48 fields); sha256 f6742504c4a63e25e3a876fe9edb6fdde3f4f4cd0e6b39157bfb453c66504326 [MEASURED: this tick] |
| 8 | Design doc pinned at its committed R4 bytes | PASS | `docs/next/design/glm52-expert-drop.md` sha256 f1c8d0f603f7b92ab7e36527912fbda2f4740f5f3c6a9d43dfcbe71307b45a1c, git-clean [MEASURED: sha256sum + `git status --porcelain` this tick]; recorded in `prereg_doc` and `analysis_plan_ref` |
| 9 | ASM central-registration state | PARTIAL — see B1 | ASM-2230..2239 at `registry/assumptions.jsonl` lines 1082–1091; ASM-2290..2293 at lines 1106–1109; ASM-2340..2352 at lines 1146–1158 WITH the R3/R4 amendment provenance notes, claims byte-identical to the R4 companion (`poc/glm52-probe/asm-glm-drop-r2-2340-2352.json`, sha256 286102b540ecd9d8025f4f1f7a82c931dc81bfa7cae5db9942f78757f3570209) [MEASURED: line-by-line comparison this tick] |
| 10 | R3 range-assignment hazard (2340..2345 overlap with the prompt-cache block) | RESOLVED-IN-EFFECT | central register carries prompt-cache ASM-2331..2339 and GLM-DROP ASM-2340..2352 with NO emitted-ID collision; the prompt-cache block's unused 2340..2345 assignment tail lapsed exactly as the design's option (a) anticipated [MEASURED: id scan of `registry/assumptions.jsonl` this tick] |
| 11 | Statistics in adapter exactly per design §5.2 | PASS (self-attested; review gate confirms) | exact 2^8=256 enumeration (identity included, p granularity 1/256, effective size 12/256 disclosed in record text); joint rule p ≤ 0.05 AND T ≥ +3.0 on the cluster-balanced T; dev-selected BCa fallback (B = 10,000, CI-inversion one-sided p) with fail-closed coherence; bootstrap randomness via the house SHA-256 DRBG over fixed labels — zero PRNG-library dependencies (encoder-pin discipline) [MEASURED: selftest branch coverage this tick] |

## 2. FREEZE-READINESS: **NOT freeze-ready — by design.** DRAFT-complete.

The record and adapter are structurally freeze-ready (dry-run battery green),
but prereg-freeze MUST NOT be run until the blockers below clear. Every
remaining pin is a named sequenced pin with a fail-closed default (design §7
item 3 [R3]) — none is an open hole.

## 3. Blockers a coordinator must clear before freeze (in order)

- **B1 — un-persisted ASM supersessions (registry write + landing commit;
  GPT-5.6 review findings 11/12 residuals).** The §R2.14 supersession EDITS
  to the central copies of ASM-2232/2233/2234/2235/2236/2237/2238/2239/
  2290/2291/2292/2293 have NOT landed: all twelve rows are still
  `status: open` with no supersession markers [MEASURED: scan of lines
  1084–1091, 1106–1109 this tick]. Sharpest instance: central ASM-2238
  (line 1090) still carries its VOIDED degradation clause ("drop m-rand;
  drop m-freq…") verbatim, contradicting the registered D2 conjunction
  (ASM-2293) and ASM-2350. Until transcription lands, the §6.4 interim
  precedence rule governs (ASM-2350 wins every conflict) — but freezing
  against a central register that still contains operative contradicted
  clauses is exactly what the review cycle told us not to do. The
  transcription map is machine-readable at
  `poc/glm52-probe/asm-glm-drop-r2-2340-2352.json` key
  `central_supersessions` (line numbers stamped at repo HEAD 3611025a…;
  re-verify before editing). [STIPULATED-not-MEASURED that the coordinator
  wants this before freeze; the design text requires it at "the landing
  commit".]
- **B2 — the F1-K freeze dependency (the KaE #28 instance + artifacts).**
  The eligible-item ID list, n, m_c, exclusion count, derangement
  realizations, and all six mask-table hashes are pure functions of F1-K's
  FROZEN test-1440 id list + trigger-map + per-item span sidecars. STATE
  UPDATE vs the design's R3 wording ("not yet repo bytes"): the input BYTES
  now EXIST as committed files [MEASURED this tick:
  `data/f1k-eval-v1/items/test.jsonl` = 1,440 rows carrying `char_spans`;
  `dev.jsonl` = 96; `guard.jsonl` = 60; `data/f1k-trigger-map-v1/
  trigger-map.json`; manifest stamped "built 2026-07-13 designer-23
  data-construction pass"; git-clean] — but F1-K itself is UNFROZEN
  [MEASURED: `f1k` absent from `registry/frozen-index.json`; f1k.json
  status DRAFT with placeholder corpus pins]. glm-edrop-0's sequenced pins
  are therefore computable the MOMENT F1-K's freeze pins those bytes, and
  must NOT be computed from unfrozen bytes. Sequencing is
  F1-K-freeze → glm-edrop-0 sequenced pins → glm-edrop-0 prereg-freeze →
  any F1-K test outcome (else the §6.1 step-5 firewall applies). Coverage
  gates at pin time: exclusions ≤ 20% of 1,440; n ≥ 300; all 8 m_c ≥ 10;
  ≥ 48 eligible dev-96 items — any miss returns to the maintainer BEFORE
  spend. [STIPULATED: design §5.1/§6.1]
- **B3 — DROP-table C-patch: not yet authored, and approval is a named
  external gate.** The ~120–200-line item-ID→mask-table diff vs colibri
  a78a06fc5acc4b0dc0f9ef03987c66b0559d1250 is the only code artifact the
  design still owes; its approval rides the #28 maintainer patch review
  (bundled, one decision). Fail-closed default: while unapproved — NO
  bring-up, NO freeze completion, NO spend. [STIPULATED: §6.3 [R3]]
- **B4 — R4 replay (M_oracle/M_kernel) must land before main-phase spend.**
  CPU-only on committed bytes, ~$0, through the coordinator's mechanical
  pathway; completes the held ASM-2013 branch classifier and prices D2's
  prior. Not a freeze blocker strictly (it gates SPEND), but the
  coordinator should schedule it with the freeze. [STIPULATED: §7 item 1]
- **B5 — the deferred GPT-5.6 review gate (codex auth down).** This pass's
  two new artifacts (record + adapter) have NOT been externally reviewed;
  the design (R0–R4) has. Specific items flagged FOR that review: (i) the
  kill criterion — the design doc words NO kill; the record's
  harm-direction operationalisation (T(u-topk vs m-kern) ≥ +3, p ≤ 0.05,
  the F1-K kill analog) is new text needing explicit confirmation; (ii) the
  D2 aggregation choice "a CLEAN leg miss is decisive over another leg's
  void" (the design leaves the mixed case ambiguous; disclosed in the
  record and the adapter docstring); (iii) the adapter's BCa-fallback
  bootstrap riding the house DRBG (seedless fixed-label SHA-256) rather
  than a registered integer seed; (iv) the `PINNED-AT-INPUTS:` placeholder
  wording for the four design-materialized hashes (core / concept table /
  stats roster / power sim), whose expected plain-sha256s are already
  design-pinned but whose kot-corpus-hash/1 data/ directories are
  freeze-time artifacts. [STIPULATED: reviewer scope proposal]
- **B6 — GPU/instance sign-off + spot-capacity decision.** Maintainer
  ceiling sign-off on `budget` (usd_cap 95, wall_clock_cap_hours 320 —
  `budget.maintainer_signoff` is intentionally absent from the DRAFT), and
  the pre-decision that an on-demand fallback (≈ $193–220 worst case) is a
  coordinator sign-off event, never a silent fallback. The prereg-freeze
  PAUSE flags (open EXTRAPOLATIONs ASM-2238/2341/2350 + inherited
  ASM-2313) resolve per their registered paths: cost against
  `glm-drop/cost-ledger.json` only; power against the freeze re-run at
  realized (n, m_c). [STIPULATED: §6.4 / ASM-2350]
- **B7 — pilot artifacts at freeze.** k\* selection on F1-K's dev-96
  (deficit strictly > 3.0 rule, k = 1 escalation only, STOP wording
  pre-worded), the continuous-statistic sign check (disagreement surfaces
  to the maintainer BEFORE freeze), cold/warm byte-identity, MiniLM weight
  hashes, and the power re-run — all produced at or immediately before
  freeze per the §7 item-3 produce-vs-reverify split, already enumerated in
  the record's `n_planned.freeze_manifest`. [STIPULATED: §4.2/§4.3/§3.1]

## 4. Infra / GPU / $ estimate (instance-hours and dollars SEPARATE, per §6.4)

No GPU anywhere: the run is CPU-side prefill scoring on the pinned
**i4i.2xlarge** (the KaE #28 co-located instance); mask/map construction is
CPU-only on this box (~$0).

| Quantity | Value | Basis |
|---|---|---|
| Pass-equivalents | 8 (b0-full, u-topk, m-freq, m-emb, m-kern, 3×m-drng) | [STIPULATED: ASM-2350] |
| Pilot + bring-up volume | ≤ 530 prefills (dev-96 × {b0-full + u-topk@k∈{4,3,2}} + optional k=1 cell + ~50 verification) | [STIPULATED: §6.4] |
| Main volume | 8 × n prefills | [STIPULATED: §6.4] |
| n = 300 planning point | ≈ 2,930 prefills ≈ **68 instance-hours** ≈ **$14–19 spot** | [EXTRAPOLATION: ASM-2350 — standing F1-K model: 100 s/prefill pessimistic ÷ 1.20 pinning speedup; spot $0.20–0.28/h; throughput UNKNOWN until F1-K bring-up measures it (ASM-2023 carried)] |
| n = 1,440 pool cap | ≈ 12,050 prefills ≈ **279 instance-hours** ≈ **$56–78 spot** | [EXTRAPOLATION: ASM-2350, same model] |
| **HARD CEILING** | **320 instance-hours AND $95 spot dollars, whichever binds first** | [STIPULATED: ASM-2350; record `budget`] |
| On-demand fallback (spot dry) | ≈ $193–220 worst case — coordinator SIGN-OFF decision, never silent | [EXTRAPOLATION: ASM-2350 at $0.69/h] |
| Degradation order if ceiling binds | (1) drop the k=1 escalation pilot cell; (2) return to maintainer. NO masked arm dropped; R never < 3; n never cut | [STIPULATED: ASM-2350, superseding central ASM-2238 IN FULL] |
| Amortized via KaE co-location | one S3 restore (~370 GB, ~1 h), one bring-up, one gateway patch review, one subset construction, one throughput measurement | [STIPULATED: §6.1; if #28 GATE 0/1 do not land, glm-edrop-0 runs on its own restore — only amortization is lost] |
| Storage | existing S3 line, $8.5/mo (already running) | [STIPULATED: §6.2] |
| Cost resolution | ONLY against `glm-drop/cost-ledger.json` — never against quality metrics | [STIPULATED: ASM-2350] |

## 5. Hand-off pointer

bd issue: `kernel-of-truth-sotz` (this prep). Next actor: coordinator —
clear B1 (registry transcription), then hold for F1-K freeze (B2) and the
#28 patch/ceiling decisions (B3/B6); route B5 to GPT-5.6 when codex auth is
restored. Prereg-freeze itself is one command once B1–B7 clear
(`tools/registry/prereg-freeze.py --experiment glm-edrop-0`), and the
freeze pass must then replace the `PINNED-AT-INPUTS:` placeholders per the
record's `freeze_manifest` produce-list — each byte-identical-or-halt.
