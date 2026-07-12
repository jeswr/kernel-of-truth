# DECONF/1 Stage A1 — result (aligned-generic-store extensional-equivalence audit)

**Design:** docs/next/design/DECONF.md §2.1/§3 (ASM-0961/ASM-0962,
PROPOSED-ASM-1010/1011). No new ASM: this is execution of the frozen §3.1
procedure, all three parts.
**Executed:** 2026-07-11, local CPU, ~$0, zero model calls, zero GPU, zero
network. First execution ran the §3.1(a) grid only (GRID-SCOPE, per the GPT-5.6
review and the committed interpretation docs/next/interpretations/deconf-a1.md);
this execution adds §3.1(b) dual-INITIALIZATION and §3.1(c) TRAJECTORY REPLAY
— the certificate is now **COMPLETE** as DECONF defines it (C_dec over
grid ∪ replay ∪ init-order).
**Status: EXPLORATORY (pre-freeze execution).** The DECONF design routes through
external review → prereg freeze before a *registered* run; every step here is
deterministic and pin-gated, so the registered re-run reproduces these bytes for
$0. Nothing here appends to results-log, touches any frozen record, or issues a
verdict.

## Question

Does a GENERIC aligned answer-key — GS-A, a mechanical four-column projection
`{concept_id, term_labels, canonical_text, claims}` of the kernel's own 108
covered-concept records onto exactly the read-set of the pinned verifier's
`check()`, ZERO authored prose — reproduce the entire measured F2-line verifier
behaviour, bit-for-bit, with no model call — over the exhaustive decision grid
AND the logged trajectories AND both initialization orders?

## Results — the COMPLETE certificate

| Statistic | Value | Tag |
|---|---|---|
| **C_dec (COMPLETE: grid ∪ replay ∪ init-order)** | **1.0 exactly — 40,576/40,576** | **[MEASURED]** (exhaustive count; no sampling error, no CI) |
| — §3.1(a) grid component (eager init) | 11,848/11,848 | [MEASURED] |
| — §3.1(b) init-order component (lazy init, full grid re-run) | 11,848/11,848 | [MEASURED] |
| — §3.1(c) trajectory-replay component | 16,880/16,880 | [MEASURED] |
| **R_repro** = lift(GS-A)/lift(kernel) | **≡ 1.0 identically** | **[MEASURED-BY-INVARIANCE]** (licensed by C_dec = 1.0 via the §1 determinism lemma; not a fresh model run) |
| Discordances (all components) | **0** | [MEASURED] |
| §3.2 4-cause triage ladder | **NO-OBJECT** (zero discordant triples — nothing to triage; no KERNEL-RUNTIME-CHANNEL-CANDIDATE exists) | [MEASURED] |

**The certificate is COMPLETE:** per the pre-registered §3.2 reading
(ASM-0962 as amended by PROPOSED-ASM-1010), C_dec = 1.0 across all three
components is the verdict-input **KERNEL-RUNTIME-STRUCTURE-INERT** — the
kernel's structural fields (explication trees, primes, vectors, types,
provenance frames, engine hooks) are runtime-inert under the pinned topology;
the checker reads nothing beyond the urn-keyed answer-key projection. Scope:
the pinned harness+checker version, the three pinned corpora, the closed
option-scoring output space, the pinned initialization procedure, the
content-hashed store version; measured model context **R-1/135M only — no
extrapolation to the 100M–2B rung range is licensed** (DECONF §1/§3.0).

### §3.1(b) dual-initialization detail

- **Label collisions (published, counted):** 0 store-label collisions over 108
  lowercased store labels; 0 item-label collisions over 108 item labels — the
  later-load-wins overwrite path is **unreachable** in the covered set
  [MEASURED].
- **Eager vs lazy grids:** full grid run under BOTH orders; kernel↔GS-A
  concordant under both (11,848/11,848 each). Eager-vs-lazy divergence WITHIN
  each store: **0 cells on either side** — the lazy term-for-definition path
  can miss a not-yet-loaded concept, but a missing `_by_label` entry and a
  non-matching entry both decide `ok=False`, and no two covered concepts share
  a normalized canonical text (108/108 unique, counted) — so decisions are
  init-order-invariant even though internal lookup state is not [MEASURED].

### §3.1(c) trajectory-replay detail

- **Replayed logs (pinned):** the audited final run's
  `run-records-f2b.jsonl` (poc/f2b/results-incoming/20260709-114229-modal/,
  sha `dd98ccebaebd…` — full sha in a1-complete-result.json pins) — all 7
  verifier-consulting cells: kernel-verify-retry k=4 × seeds {0,1,2},
  shuffled-kernel-verify-retry k=4 × seeds {0,1,2}, extraction-instrument;
  plus `data/d-xif/outputs/r1.jsonl` (sha == the f2b-manifest pin
  `133abf1f…`), the 500 covered-slice REAL logged model answers.
- **Verify-retry cells:** replayed IN SEQUENCE with the runner's exact
  realized initialization (eager `index_labels` over the rank-prefix-250
  scored items) and consultation order (250 covered + 500 d-ext items):
  6 × 2,730 = 16,380 decisions, all concordant; repeat-consultation
  (×5 = the realized max attempts) violations: 0 [MEASURED].
- **Coverage disclosure [MEASURED at source]:** the pinned runner persisted
  per-item `item_correct` vectors only — per-attempt answers were NOT logged.
  The replay therefore covers the realized trajectories by ANSWER-SUPERSET
  enumeration at the realized evolving state; this covers every realizable
  logged (item, attempt, answer) decision because the ONLY checker-state
  mutator is `_load(item)` (answer- and attempt-independent, a code-level
  fact of the pinned runner), and repeat-consultation invariance is itself
  measured (0 violations), not assumed.
- **Answer-for-answer replay where real answers exist:** the 500 logged d-xif
  R1 `ifc_answer` records, replayed in file order through both checkers:
  500/500 concordant; the stored per-output `ifc_*` flags match the kernel
  replay 500/500; and BOTH stores reproduce the audited cell's logged
  aggregates exactly (`n_labelled` 500 / `n_extraction_failures` 0 /
  `n_extraction_errors` 0) — the replay is tied to the audited run's own log,
  not only to re-derived state [MEASURED].

### Grid-scope detail (unchanged from the first execution)

Sub-grids all fully concordant: run-realized f2b-replicate protocol
(d-qa-r[:250], 102-urn index) 1,460/1,460; run-planned f2b-transfer stage-2
(d-qa-t[:250], 105-urn index) 1,592/1,592; supplementary d-ext off-coverage
abstention grid 4,000/4,000. Vacuity guard: kernel-side true-variant triples
split 1,860 accepts / 3,644 rejects / 420 abstentions; true vs shuffled
diverge on 1,673/5,924 item-answer pairs; verifier-accept ⇔ membership gold
exact on all 5,504 decidable pairs (off-diagonals zero) [MEASURED].
`a1-result.json` (grid-scope) is reproduced **byte-identically** by this
execution.

## What the numbers imply (flagged; NOT concluded here)

Per §3.2/§6, C_dec = 1.0 COMPLETE licenses the invariance-lemma rider at §1's
stated scope: every pinned-scope F2-line endpoint — the audited +0.1507 lift
(BCa LB +0.1053), the shuffled-control ~0 recovery, and f2b-transfer stage-2's
external-gold endpoints IF stage 2 runs at the same pins — is bit-for-bit
invariant under replacement of the kernel store by its urn-keyed answer-key
projection. What this does NOT prove: that kernel-authored content is generic
(GS-A's strings ARE kernel-authored — knull-v2's channel), anything about
other topologies/harness versions, or the 100M–2B rung range. The §6 rider
wording, headline re-scoping, and the interp update are the
**coordinator's/maintainer's to route** — this report supplies the numbers.
Expected-direction disclosure: the outcome matches EXTRAPOLATION ASM-0966
(resolved); the stage's value is the conversion of an analytic claim into a
measured, riding, re-checkable COMPLETE certificate.

## Still needed (exactly)

1. Coordinator: route the interp update (docs/next/interpretations/deconf-a1.md
   currently scopes to GRID-SCOPE; this execution completes §3.1(b)+(c)) — NOT
   done here by instruction.
2. External review → prereg freeze → registered A1 re-run (minutes, $0) +
   verdict-gen + results-log append under runner-role separation.
3. Stage A2 (GS-C/SQLite executor) and Stage B (GPU) remain unbuilt — out of
   this bead's scope by design.

## Artifacts & pins

`poc/deconf-a1/`: `build_gsa.py`, `gs-a.jsonl` (108 rows, sha
`4a28f7fae59c85d27fa4bc7d0c7d15d9856f0527fdc0492b00162af7dd41e9d5`),
`gsa-manifest.json`, `audit_a1.py` (now runs §3.1(a)+(b)+(c)),
`a1-result.json` (grid-scope, byte-identical to the first execution),
`a1-complete-result.json` (the COMPLETE certificate: all components,
collision lists, eager-vs-lazy counts, replay coverage disclosure, empty
discordance list, all pins). Inputs verified fail-closed: runner
`b62c3a72…`, f2b-manifest `da1fe9dd…`, perm seed 20260709 / map `05af8f50…`,
corpus pins d-qa `ad756a7e…`, d-qa-r `0d548bf1…`, d-qa-t `7179ee67…`,
kernel-v0 `8209cada…`, molecules-v0 `69f0c8a3…` (all == frozen registry pins);
replay pins: run-records-f2b.jsonl + d-xif outputs `133abf1f…` (== manifest
pin), d-ext items `ba2c1c43…` (== manifest pin), d-qa covered `e96ad766…`
(== manifest pin) — exact shas in a1-complete-result.json. No frozen object,
verdict, ruling, or results-log line was modified.
