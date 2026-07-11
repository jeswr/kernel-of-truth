# DECONF/1 Stage A1 — result (aligned-generic-store extensional-equivalence audit)

**Design:** docs/next/design/DECONF.md §2.1/§3 (ASM-0961/ASM-0962, registered).
**Executed:** 2026-07-11, local CPU, ~$0, zero model calls, zero GPU, zero network.
**Status: EXPLORATORY (pre-freeze execution).** The DECONF design routes through
external review → prereg freeze before a *registered* run; this execution is the
built harness run end-to-end at the coordinator's direction. Every step is
deterministic and pin-gated, so the registered re-run (post-freeze, runner role)
reproduces these bytes for $0. Nothing here appends to results-log, touches any
frozen record, or issues a verdict.

## Question

Does a GENERIC aligned answer-key — GS-A, a mechanical four-column projection
`{concept_id, term_labels, canonical_text, claims}` of the kernel's own 108
covered-concept records onto exactly the read-set of the pinned verifier's
`check()`, ZERO authored prose — reproduce the entire measured F2-line verifier
behaviour, bit-for-bit, with no model call?

## Method (as designed, ASM-0962)

Exhaustive decision-grid enumeration: three pinned corpora (d-qa 650 incl. 150
control items, d-qa-r 1000, d-qa-t 360) × every admissible answer (MC option
keys; yes/no for claims — the closed IF-C surface) × both verifier variants
(true map; the seed-pinned Sattolo derangement, replayed by the pinned code and
byte-verified against all 3 recorded `shuffle-map.json` files, sha `05af8f50…`,
then applied identically to GS-A rows). Decision triple `(extract_ok,
decidable, consistent)` compared between (i) the **literal pinned**
`KernelVerifier`/`ShuffledKernelVerifier` (imported from
`poc/f2b/runner/f2b_runner.py` @ `b62c3a72…`, byte-verified = the audited
Modal run's staged bytes) over the kernel store, and (ii) the same checker
class over GS-A rows only (`gs-a.jsonl` @ `4a28f7fa…`; no record file, no
derivation function touched at check time). All five input corpus hashes
verified against the frozen registry pins before anything ran.

## Results

| Statistic | Value | Tag |
|---|---|---|
| **C_dec** (primary: concordant triples / full grid) | **1.0 exactly — 11,848/11,848** | **[MEASURED]** (exhaustive count; no sampling error, no CI) |
| **R_repro** = lift(GS-A)/lift(kernel) | **≡ 1.0 identically** | **[MEASURED-BY-INVARIANCE]** (licensed by C_dec = 1.0 via the §1 determinism lemma; not a fresh model run) |
| Discordances | 0 (none on any grid) | [MEASURED] |
| Run-realized sub-grid (f2b-replicate protocol, d-qa-r[:250], 102-urn label index) | 1,460/1,460 | [MEASURED] |
| Run-planned sub-grid (f2b-transfer stage-2, d-qa-t[:250], 105-urn index) | 1,592/1,592 | [MEASURED] |
| Supplementary d-ext off-coverage abstention grid (500 × 4 × 2) | 4,000/4,000 | [MEASURED] |

**Vacuity guard (the grid does real work):** kernel-side true-variant triples
split 1,860 accepts / 3,644 rejects / 420 abstentions (the 150 non-checkable
d-qa controls); true vs shuffled variants diverge on 1,673/5,924 item-answer
pairs. Internal consistency: accepts = 1,860 = exactly one accepted answer per
checkable item. **Bonus exhaustive count:** verifier-accept ⇔ membership gold
on all 5,504 decidable pairs (accept|gold 1,860, reject|nongold 3,644,
off-diagonals **zero**) — the f2b-replicate assessment's circularity note,
previously analytic, is now count-verified at this scope [MEASURED].

## What the numbers imply (flagged; NOT concluded here)

Per pre-registered reading ASM-0962, C_dec = 1.0 is the verdict-input
**KERNEL-RUNTIME-GENERIC**: every F2-line endpoint — the audited +0.1507 lift
(BCa LB +0.1053), the shuffled-control ~0 recovery, and every future output of
the answer→check→resample topology including f2b-transfer stage-2's
external-gold endpoints — is bit-for-bit invariant under replacement of the
kernel store by its four-column projection. The generic aligned answer-key
DOES reproduce the entire measured lift, at zero model spend. The "kernel adds
nothing at runtime *on this line*" reading, the §6 invariance-lemma rider, and
any headline re-scoping are the **coordinator's/maintainer's to draw** — this
report supplies the number, not the conclusion. Scope limits (DECONF §9.1):
this closes only the RUNTIME channel for THIS checker/store pair (pins above);
it says nothing about authored-content value (knull-v2), authoring economics
(A-F0), or non-check-coupled architectures. Expected-direction disclosure: the
outcome matches EXTRAPOLATION ASM-0966 (now resolved); the stage's value is
the conversion of an analytic claim into a measured, riding, re-checkable fact.

## Still needed (exactly)

1. External (GPT-5.6-class) review of DECONF/1 + prereg freeze (kot-reg entry),
   per the design's own status line — then the registered A1 re-run (minutes,
   $0) + verdict-gen + results-log append under runner-role separation.
2. Coordinator: create beads P3-E-DECONF-0 / P3-E-DECONF-B (design §11) — no
   bd operation was performed here (governance rule for this session).
3. Maintainer: decide the §6 row-1 invariance-lemma rider wording and Stage B's
   arm-sharing economy (A1 = 1.0 ⇒ the conditional kernel arm is NOT run).
4. Stage A2 (GS-C/SQLite executor) and Stage B (GPU) remain unbuilt — out of
   this bead's scope by design.
   No missing data was encountered; the Stage-A1 spec was fully determined.

## Artifacts & pins

`poc/deconf-a1/`: `build_gsa.py` (GS-A builder), `gs-a.jsonl`
(108 rows, sha `4a28f7fae59c85d27fa4bc7d0c7d15d9856f0527fdc0492b00162af7dd41e9d5`),
`gsa-manifest.json`, `audit_a1.py`, `a1-result.json` (full grids, discordance
list [empty], decision-mix disclosure, all pins). Inputs verified: runner
`b62c3a72…`, f2b-manifest `da1fe9dd…`, perm seed 20260709 / map `05af8f50…`,
corpus pins d-qa `ad756a7e…`, d-qa-r `0d548bf1…`, d-qa-t `7179ee67…`,
kernel-v0 `8209cada…`, molecules-v0 `69f0c8a3…` (all == frozen registry pins).
No frozen object, verdict, ruling, or results-log line was modified.
