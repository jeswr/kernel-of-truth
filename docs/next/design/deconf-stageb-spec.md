# P3-E-DECONF-B — Stage-B freeze-ready spec (power-sizing · buildable GR-D-lite arm · freeze delta)

> **Status: [EXP-DESIGN → FREEZE-READY SPEC].** This document completes the three
> items that gated the DECONF/1 Stage-B prereg-freeze (docs/next/design/DECONF.md
> rev-B §5, §11 dependency edges; docs/next/optimal-resource-usage-plan.md lane
> B2): (1) the PROPOSED-ASM-1013 power sizing, computed explicitly from MEASURED
> stage-2 inputs; (2) the concrete, buildable resolution of the GPT-5.6 review's
> residual Stage-B concerns (poc/gpt56-review/rev-deconfb-20260711/
> last-message.json — non-oracular retrieval query, acceptance/abstention
> contract, RAGC signal-menu conformance); (3) the exact freeze delta the
> coordinator must register. **Nothing here is frozen, run, or registered by this
> document**; no frozen record, verdict, results-log line, or registry file is
> edited; no git/bd/kb operation is performed; no GPU is spent. New assumptions
> are confined to the disjoint block **PROPOSED-ASM-1100…ASM-1109** (doc-body
> only; the coordinator registers at commit). The experiment-designer role
> executes the freeze per §5; the runner role runs it. Author: Fable, design
> agent, 2026-07-11.
>
> **Binding frame, adopted verbatim and not restated in full:** DECONF.md rev-B
> §0/§5/§6/§7/§8 (the Stage-B design this spec instantiates, incl. the
> ASM-0960–0966 registered block and PROPOSED-ASM-1010–1017 pending
> registration); RAGC.md §5.2/§8.4 (the frozen GR-D signal menu + ratified
> de-confound statistics, ASM-0920–0927/0950–0957); FRONT.md §5 (ASM-0853 parity
> rules); the DECONF-A1 complete certificate as interpreted
> (docs/next/interpretations/deconf-a1.md — EXPLORATORY pre-registration, its
> §3 replay-substitution disclosure riding every citation); the f2b-transfer
> stage-2 mechanical result (docs/next/interpretations/f2b-transfer-stage2.md —
> PASS-PENDING-AUDIT; every consumption below is of RUN-RECORD facts as
> variance/throughput anchors, not of the pending verdict).
>
> **Tag convention (house):** `[MEASURED: ref]` restated artifact fact;
> `[STIPULATED: id]` design choice; `[DERIVED]` this document's own computation
> from MEASURED inputs, disclosed; `[EXTRAPOLATION]` forward projection, never a
> premise; `[PROPOSED-ASM-110x]` a stipulation of this spec awaiting coordinator
> registration.

---

## 0. What Stage B decides (contract restated in one paragraph, then the rider)

A1 is complete: on the measured closure the pinned checker's decisions are
extensionally computable from the urn-keyed answer-key projection alone —
kernel-runtime-STRUCTURE-inert; the GS-A arm is bit-identical to the kernel
arm under the pins [MEASURED: deconf-a1.md §0, C_dec = 1.0 over 40,576/40,576;
EXPLORATORY pre-registration]. Stage-2 measured the lift itself on blind
external gold: +0.2507 absolute, controls holding, PASS-PENDING-AUDIT
[MEASURED: f2b-transfer-stage2.md §0]. The one question neither settles — the
sharpest remaining attribution test — is whether the **ALIGNMENT** (the
item-aligned deterministic answer key) is load-bearing, or whether a generic
lexical-retrieval store with a generic menu acceptance signal, at matched
budget through the identical retry topology, reproduces the lift too. Stage B
measures exactly that: **Δ_align = acc_ext(GS-A-verify-retry) −
acc_ext(GR-D-lite)** on external gold, TOST/LCB branches per PROPOSED-ASM-1013
[STIPULATED: DECONF §5.2].

**Rider (verbatim, on every Stage-B sentence including this spec's):**
*self-authored items, kernel-covered slice, oracle-addressed store; external
adjudication removes membership-gold circularity, not item-generation or
store-addressing circularity* [STIPULATED: PROPOSED-ASM-1017]. Stage B is a
formal/oracle-addressed covered-slice **G2-class diagnostic** — never W1,
never G4; BM25-only is a cheap lexical **precursor**, never RAGC's "strong
generic RAG baseline"; R-1/135M only, no extrapolation to the 100M–2B rung
range [STIPULATED: PROPOSED-ASM-1014].

---

## 1. POWER-SIZING (deliverable 1 — the PROPOSED-ASM-1013 calculation, explicit)

### 1.1 The measured inputs (the "MEASURED-where-they-exist" set)

All from the pinned stage-2 run records
`poc/f2b-transfer/results-incoming/20260711-184448-modal/run-records-f2bt.jsonl`
(the FULL-mode stage-2 execution: R1, 250-item d-qa-t eval prefix, seeds
{0,1,2}, k = 4, external-gold `item_correct_ext` vectors per arm×seed), read
directly and recomputed only as the variance decomposition below (a planning
computation, not a re-analysis of any endpoint) [MEASURED: the vectors;
DERIVED: every decomposition number]:

| Quantity | Value | Source contrast |
|---|---|---|
| acc_ext(R1-alone) | 0.3960 (identical all 3 seeds) | model-alone R1 |
| acc_ext(kernel-verify-retry) seed-mean | 0.6467 (0.660/0.560/0.720) | the arm GS-A is bit-identical to |
| paired sd of seed-averaged per-item diff, kernel−alone | 0.3208 (corr 0.756) | bridge-shaped contrast |
| paired sd, kernel−gloss-self-verify | 0.2851 (corr 0.793) | retry-vs-retry |
| paired sd, kernel−shuffled-verify | 0.2889 (corr 0.793) | retry-vs-retry |

Variance decomposition of the paired per-item difference d_i (3 seeds/item;
Var(d̄_i at s seeds) = σ_b² + σ_w²/s; σ_w² = mean within-item across-seed
variance, σ_b² = Var(d̄_i) − σ_w²/3) [DERIVED from the same records]:

| Contrast | σ_b² (between-item) | σ_w² (seed noise) |
|---|---|---|
| kernel − gloss-SV (retry-vs-retry) | 0.0288 | 0.1573 |
| kernel − shuffled (retry-vs-retry) | **0.0301** | **0.1600** |
| kernel − alone (retry-vs-deterministic) | 0.0576 | 0.1360 |

### 1.2 Planning values and their epistemic status

- **Primary planning values** [STIPULATED: PROPOSED-ASM-1101, informed by
  MEASURED]: σ_b² = 0.0301, σ_w² = 0.1600 — the **maxima over the two
  retry-vs-retry contrasts**, the shape-matched proxies for GS-A-verify-retry
  vs GR-D-lite (both arms are k = 4 retry arms over the same items with
  seed-driven resampling). Applying them to the unrun GR-D-lite arm is a
  STIPULATED planning step, disclosed: no GR-D-lite datum exists yet.
- **Pessimistic sensitivity** [STIPULATED, same ASM]: σ_b² = 0.0576 — the
  kernel−alone value, the worst measured between-item heterogeneity. Honesty
  note on this corner: that shape arises when one side of the pair is a fixed
  (deterministic) correctness pattern, i.e. when GR-D-lite degenerates toward
  the floor arm — but in that world the true Δ_align ≈ the bridge lift
  (~0.25 measured for the kernel arm), where power ≈ 1.0 at any of the sizes
  below [DERIVED]. The cell "pessimistic σ_b² AND true Δ = 0.10" combines a
  floor-like variance shape with a working-arm mean and is internally
  inconsistent; it is reported as sensitivity, not sized for.
- Effect target Δ = 0.10, δ_sup = δ_eq = 0.05, paired seed-averaged per-item
  analysis, BCa B = 10,000 — all inherited [STIPULATED: PROPOSED-ASM-1013;
  RAGC §8.4].

### 1.3 The calculation (normal approximation to the paired one-sided test; simulation confirmation required at freeze)

Test: reject iff LCB_{1−α}(Δ_align) > δ_sup. Power at true Δ:
`Φ( (Δ − δ_sup)·√n / sd_D(s) − z_{1−α} )` with
`sd_D(s) = √(σ_b² + σ_w²/s)`, n = items, s = seeds. The normal approximation
stands in for the pre-registered paired BCa bootstrap for planning purposes
(standard practice; the discrete d̄_i support at s = 5 is 11-point, CLT-safe
at n ≥ 250); a freeze-time SIMULATION confirmation is mandatory (§1.6)
[STIPULATED: PROPOSED-ASM-1100].

**FWER realisation** [STIPULATED: PROPOSED-ASM-1107]: Holm over the four
named one-sided contrasts {primary Δ_align; bridge lift; GR-D-lite −
GR-A-lite; GS-A-verify-retry − GR-A-lite} per PROPOSED-ASM-1013. The primary
is therefore **sized at the Holm worst-case floor α/4 = 0.0125 one-sided**
(the floor binds only if the primary has the smallest p; under the Δ = 0.10
alternative the bridge contrast at ~0.25 rejects at astronomically small p
and the realised threshold relaxes toward α — so the floor sizing is strictly
conservative) [DERIVED].

### 1.4 The size decision: why 250×3 fails, and what replaces it

- **The rev-B default (250 items × 3 seeds) is UNDERPOWERED and is
  withdrawn**: at the primary planning values, SE = 0.0183–0.0180 → power
  0.69–0.70 at the Holm floor, 0.86–0.87 even unadjusted [DERIVED]. The
  PROPOSED-ASM-1013 clause "enlarge the adjudicated eval set BEFORE freeze or
  do not freeze" fires.
- **The enlargement costs ZERO new adjudication**: the pinned d-adj-t labels
  file (sha256 `a0ffe09b04…`, the exact file stage-2 pinned) already contains
  **n_ext_labelled = 333** resolved external-gold labels of the 360
  adjudicated d-qa-t items (27 unresolved-disagreement items excluded by the
  issue-#9 rule) [MEASURED: data/d-adj-t/summary.json + labels.jsonl count].
  Stage-2 used only the 250-item prefix because ITS frozen design pinned 250;
  Stage B is a fresh prereg and may pin all 333. The A1 certificate covers the
  choice: its grid enumerated the FULL d-qa-t 360-item corpus (2,304 cells),
  so GS-A↔kernel decision concordance is measured on all 333 eval items, not
  only the 250 prefix [MEASURED: deconf-a1.md §0].
- **DECISION — the pre-registered size** [STIPULATED: PROPOSED-ASM-1100]:

  > **n = 333 items (every resolved gold_ext label in the pinned d-adj-t
  > file) × 5 seeds {0,1,2,3,4}, k = 4, m = 3 self-consistency probes,
  > all four arms at all five seeds.**

  Power at true Δ = 0.10, primary planning values
  (SE = √(0.0301 + 0.1600/5)/√333 = **0.01366**) [DERIVED]:

  | Level | Power (superiority branch) |
  |---|---|
  | Holm worst-case floor α/4 = 0.0125 | **0.922 ✔ (≥ 0.90 target met)** |
  | Holm realised α/2 = 0.025 | 0.955 |
  | unadjusted α = 0.05 | 0.978 |

  Sensitivity (pessimistic σ_b² = 0.0576; SE = 0.01640): 0.79 at the Holm
  floor, 0.92 unadjusted — disclosed with the §1.2 internal-inconsistency
  note; at that variance shape's own consistent alternative (Δ ≈ 0.25) power
  ≈ 1.0 at every level [DERIVED].
- Alternatives rejected [DERIVED]: 333×3 → 0.82–0.83 at the floor (fails);
  250×8 → 0.90 marginal at the floor but ~20% more retry-arm generations than
  333×5 and fewer items for the item-level bootstrap; ≥6 seeds at 333 →
  exceeds the ≤3 GPU-h worst-case budget (§4.1). 333×5 is the unique cell
  meeting both the ≥0.90-at-the-floor target and the budget.

### 1.5 TOST (collapse-branch) power, co-disclosed

The ASM-1013 target is defined at Δ = 0.10 (the superiority direction); TOST
power is a co-disclosure, not the sizing bar [STIPULATED: PROPOSED-ASM-1100].
At true Δ = 0, n = 333×5, primary planning values: P(90% CI inside ±0.05) =
2Φ(0.05/0.01366 − 1.645) − 1 = **0.956**; at the Holm floor analogue 0.844
[DERIVED]. The INCONCLUSIVE-UNDERPOWERED branch remains reachable and is
disclosed as such — no attribution sentence fires from it [STIPULATED:
DECONF §5.2].

### 1.6 Freeze-time confirmation (mandatory, CPU, ~$0 marginal compute)

The freeze package MUST include a deterministic simulation script (seeded
PRNG, pinned) that draws per-item true differences from the planning
decomposition, applies the actual paired BCa machinery (B = 10,000) and the
actual Holm family, and confirms empirical power ≥ 0.90 at Δ = 0.10 at the
worst-case floor for the pinned (n = 333, s = 5). If the simulation
contradicts the normal approximation, the simulation governs and the size is
revised before freeze — this is the P3-D-POWER §5 sizing-rig obligation
discharged locally for one G2 diagnostic (POWER.md's sizing rig
P3-D-POWER-SIZE does not exist yet; a G2 diagnostic may carry its own
explicit calc + simulation where a G4 prereg could not cite one)
[STIPULATED: PROPOSED-ASM-1100; POWER.md §5 status honesty adopted].

---

## 2. The buildable arm (deliverable 2 — the review's residual concerns closed in code-shape)

### 2.1 Arm inventory (unchanged from DECONF §5.1 except size and the registered arm-omission)

| Arm | Definition | Gens/item/seed (worst) |
|---|---|---|
| R1-alone | attempt-0, no store, no retrieval (`run_alone`, no context_fn) | 1 |
| GS-A-verify-retry | GS-A store behind the UNCHANGED pinned `run_verify_retry` (k = 4) | 5 |
| GR-A-lite | BM25 top-j context via `run_alone(context_fn=retrieve)` | 1 |
| GR-D-lite | §2.2 loop: same shape, acceptance = self-consistency | 5×(1+3) = 20 |

The conditional kernel-verify-retry arm is **omitted**: A1 measured zero
reachable discordance on the full d-qa-t grid (the §5.1 fail-closed condition
did not fire), so the GS-A arm carries both readings under measured identity
[MEASURED: deconf-a1.md §0/§4]. Because A1 is EXPLORATORY pre-registration,
the omission's REGISTERED form is sequenced in §3.3 (with a disclosed
fallback) [STIPULATED: PROPOSED-ASM-1105].

**Code-change contract** [STIPULATED: PROPOSED-ASM-1108]: `f2b_runner.py`
stays byte-identical at its pin (sha256 `b62c3a72…` — the A1-verified sha);
any edit voids the A1 invariance lemma (DECONF §7.1). All Stage-B additions
live in a NEW module `poc/deconf-b/stageb_runner.py` that IMPORTS the pinned
runner's `answer_once`, `run_alone`, `run_verify_retry`, `det_u`, frames, and
the A1 `GSAVerifier` class (poc/deconf-a1/audit_a1.py lineage), and adds only:
the BM25 index/retrieval, the query-construction function + leak check, and
the GR-D-lite loop. The new module is hash-pinned in the frozen record.

### 2.2 GR-D-lite: the exact loop (acceptance/abstention contract — review concern 2 closed)

[STIPULATED: PROPOSED-ASM-1102; plain adoption of RAGC menu item (i) per
PROPOSED-ASM-1012 — self-consistency, ONE signal, pinned threshold, no
sweeps, NO amendment to ASM-0924/0955 needed or claimed]

```
docs = retrieve(item)                          # fixed per item, seed-invariant (§2.3)
for attempt in 0..k (k = 4):
    cand = answer_once(lm, frames, item, seed, (attempt, 0), docs)   # probe_index 0 = candidate
    probes = [answer_once(lm, frames, item, seed, (attempt, j), docs) for j in 1..3]
    agree  = count(p == cand for p in probes)
    if agree >= 2: break                       # ACCEPT (threshold 2/3, pinned)
    # else REJECT -> next attempt (resample)
final = cand                                   # exhaustion: final answer = LAST attempt,
score final == gold_ext                        # mirroring run_verify_retry verbatim
```

- **Stochasticity keying:** every generation is keyed by the det_u tuple
  `(arm, item_id, seed, attempt, probe_index)` — the existing
  `lm.choose(item, keys, gold, seed, attempt, …)` scheme with the attempt key
  extended to the pair `(attempt, probe_index)`; probe_index 0 is the
  candidate, 1–3 the probes. Pinned at freeze; identical scheme documented in
  the frozen record so the run is bit-reproducible.
- **Acceptance prompt + parser (concrete for both item types):** each probe
  is the arm's OWN answer prompt — identical frames + item + the SAME
  retrieved docs — scored by the harness's existing closed-space
  option-scoring: MC items over the pinned option keys, yes/no claim items
  over {yes, no}; "agreement" = exact key equality. There is NO judging
  template and NO free-text parsing anywhere in the acceptance path.
- **Abstention semantics:** identical to `run_verify_retry` — exhaustion
  never yields a null; the last attempt is scored. Abstention-on-exhaustion
  counts and the attempt distribution are mandatory readout columns.
- **Calibration co-report (ASM-0955 rule adopted):** per-arm acceptance rate,
  attempt-count distribution, per-attempt agreement histogram (0/3…3/3), and
  exhaustion rate — an accept-everything or reject-everything signal must be
  visible on the table. Degeneracy is DISCLOSED, not gated (per DECONF
  §5.1.1). Every probe generation is charged to the arm's ledger row.

### 2.3 Retrieval: the non-oracular contract, pinned to code (review concern 1 closed)

[STIPULATED: PROPOSED-ASM-1103/1104, instantiating PROPOSED-ASM-1012]

- **Corpus:** the ASM-0922-pinned deterministic text serialisation of the
  SAME 108 covered kernel-v0/molecules-v0 records (one document per record:
  `"<label>: <canonical_text>"` from the GS-A projection's own columns — no
  new prose is authored; the rendered store IS the GS-A store's strings).
  Document ids = record urns, used ONLY as index keys and tie-breakers, never
  readable by the query function.
- **BM25, stdlib in-repo** (no new dependency ⇒ no image change): k1 = 1.2,
  b = 0.75, tokenizer = lowercase `\w+` — all pinned; index built once on CPU,
  build seconds + index bytes on the ledger (ASM-0925 shape).
- **Query construction (the oracle-leak fix):**
  `query(item) = question_string + " " + " ".join(option_texts in prompt order)`
  for MC; `question_string + " " + claim_text` for yes/no — EXACTLY the bytes
  that appear in the model-visible prompt, in prompt order. The function
  never reads `urn`, `record_path`, `record_sha256`, `answer`/gold, item
  `id`, `type`, or any metadata. Published + hash-pinned.
- **Run-time leak check (fail closed, `ERR_QUERY_LEAK`):** the runner
  re-derives the query from the RENDERED PROMPT bytes (post-`build_prompt`,
  stripping only the pinned frame constants) and asserts byte-equality with
  `query(item)`; any mismatch aborts the run. This makes non-oracularity a
  machine-checked property, not a review promise.
- **Zero/one/multiple hits:** score all documents; top-j by BM25 score with j
  floating to fill the pinned retrieved-token cap (**cap = 512 tokens**,
  STIPULATED-planning, maintainer-adjustable at freeze); ties by
  lexicographic document-id. Zero positive-score hits ⇒ EMPTY context, no
  fallback, zero-hit count a mandatory disclosure. Retrieval hit@j against
  the item's pinned record is co-reported (diagnostic only; the pinned record
  identity is consumed in SCORING the diagnostic, never in the query or the
  context).
- **Evidence-budget parity (worded per PROPOSED-ASM-1012):** the 512-token
  cap is the allowed evidence budget binding GR-A-lite and GR-D-lite;
  R1-alone and GS-A-verify-retry retrieve zero tokens BY DESIGN.
- **Retrieval is seed-invariant per item** (query and index are
  deterministic), so `docs` is computed once per item and shared across
  seeds/attempts/probes — pinned, and disclosed as a design fact (the
  retrieved evidence never resamples).

### 2.4 Menu conformance statement (review concern 3 closed)

GR-D-lite's acceptance signal is RAGC frozen-menu item (i) —
self-consistency at a pinned threshold — with menu items (ii) (learned
verifier) and (iii) (execution success) excluded for the reasons DECONF
§5.1.1 states (no executable surface at this vertical; learned-verifier
discipline out of scope at this right-size; both owned by the RAGC manifest).
This is **plain adoption of ASM-0924/0955 — no amendment is made or needed**,
and the rev-A gloss-self-check remains WITHDRAWN (the `it["urn"]` oracle leak
named at source) [STIPULATED: PROPOSED-ASM-1012, restated; ASM-0924/0955
untouched].

---

## 3. Endpoints, gates, statistics (instantiated, not redesigned)

### 3.1 Instrument gates (all inherited shapes, tested fresh on this run)

P10 extraction gate; RT-7a engagement on GS-A-verify-retry
(decidable_fraction ≥ 0.95; attempt-0 rejection ∈ [0.05, 0.95]; ≥1 final ≠
attempt-0); headroom acc_ext(R1-alone) ≤ 0.85 (stage-2 measured 0.3960 at the
250-prefix — an expectation anchor, not a substitute for the fresh gate);
bridge gate: one-sided 95% BCa LB of lift_ext(GS-A over R1-alone) > +0.05
(stage-2 measured the bit-identical kernel arm at +0.2507 — same status)
[STIPULATED: DECONF §5.2; MEASURED: the two anchors]. Gate failure ⇒
INSTRUMENT-INVALID-at-B; a bridge failure against the landed stage-2 result
is a flagged inconsistency to investigate [STIPULATED: ASM-0964].

### 3.2 Decision rule (PROPOSED-ASM-1013 machinery, Holm realisation pinned)

Primary Δ_align, paired item-level on the shared 333-item × 5-seed grid,
seed-averaged per-item means, paired BCa bootstrap B = 10,000 (PRNG seed
pinned at freeze). Holm over the four named one-sided contrasts; **the
primary's verdict branch fires on its Holm-ADJUSTED p** (equivalently the
Holm-adjusted LCB), with the unadjusted LCB95 / 90% TOST CI co-reported for
readability [STIPULATED: PROPOSED-ASM-1107]. Branches, riders, verdict rows,
equal-prominence rule, and the demoted descriptive recovery ratio: DECONF
§5.2/§6 verbatim, unchanged. Reporting: full contrast vector, hit@j +
zero-hit count, §2.2 calibration table, per-type breakdown descriptive-only,
every verdict sentence naming its licensing arm and carrying the §0 rider.

### 3.3 Sequencing with the A1 registration (the arm-omission's registered form)

The coordinator SHOULD land the A1 registration + registered runner-role
re-run (minutes, ~$0 marginal compute — taxonomy item #4 of the resource
plan) BEFORE or WITH the Stage-B freeze, so the kernel-arm omission rests on
registered evidence. **Fallback, pre-declared:** if Stage B must freeze
first, the kernel-verify-retry arm is reinstated at +5 gens/item/seed
(+~0.45 GPU-h worst case, still ≤ 3 total) and the GS-A≡kernel identity
becomes a measured diagnostic of the run instead of an omission licence
[STIPULATED: PROPOSED-ASM-1105].

---

## 4. Budget (deliverable 1's second half — the ≤3 GPU-h arithmetic) and reuse

### 4.1 Worst-case generation ledger [DERIVED from MEASURED anchors]

Throughput anchors [MEASURED: stage-2 run-records metric_vector]: R1
option-scoring p50 ≈ 107–109 ms/query at ~403 prefill tokens, A100, decode 0;
whole 15-cell stage-2 campaign ≈ 0.14 GPU-h [MEASURED:
scratchpad/f2b-stage2-build.result, restated]. Context-bearing queries at cap
512 → ~915 prefill tokens ≈ 0.25 s/query (linear-prefill planning factor,
STIPULATED).

| Arm | Gens (worst) = n×s×g | s/gen | GPU-s (worst) |
|---|---|---|---|
| R1-alone | 333×5×1 = 1,665 | 0.11 | 183 |
| GR-A-lite | 1,665 | 0.25 | 416 |
| GS-A-verify-retry | 333×5×5 = 8,325 | 0.11 | 916 |
| GR-D-lite | 333×5×20 = 33,300 | 0.25 | 8,325 |
| **Total** | **44,955** | | **≈ 9,840 s ≈ 2.73 h** |

Plus container spin-up + model load (~5–10 min, amortised by co-scheduling):
**worst case ≈ 2.9 GPU-h ≤ 3 GPU-h ✔; ≤ ~$12 at A100 planning rates ≤ $25 ✔**
[DERIVED; EXTRAPOLATION: the realised cost will sit well below worst case
because acceptance stops attempts — stage-2's kernel arm realised far fewer
than max attempts]. Expected-case ≈ 1.3–1.7 GPU-h. BM25 build + all analysis:
CPU, on the lifecycle ledger per PROPOSED-ASM-1015 (mandatory columns:
model/probe tokens + FLOPs per arm, artifact bytes incl. index, peak RSS,
latency distribution, BM25 build CPU-s, store/query-fn derivation effort).
Spend stop: exhaustion before the primary readout = scientific stop +
salvage, no retry [STIPULATED: PROPOSED-ASM-1109; DECONF §8].

### 4.2 Image + asset reuse — CONFIRMED, no new image build

[STIPULATED: PROPOSED-ASM-1106; MEASURED: the pins]

- **Modal image: the pinned f2b image `im-6uXR6RyVQV15h2B3gtpOG2`
  (requirements sha256 `0fac7243…`) — the exact image the stage-2 FULL run
  executed on** [MEASURED: stage-2 provenance-modal.json]. Stage B's only new
  code is repo-mounted stdlib Python (§2.1) ⇒ **no image build, no new
  dependency**. Co-schedule in the same session family as other f2b-image
  runs (resource plan §2.1); `modal app stop ap-<id>` after every attached
  run; nohup+setsid per the standing memory.
- Model checkpoint: R1 SmolLM2-135M-Instruct revision `12fd25f7…` (already
  cached; no R3 arm in Stage B). GS-A store: `poc/deconf-a1/gs-a.jsonl` sha256
  `4a28f7fa…` — consumed as-built, no rebuild. d-adj-t labels: the pinned
  sha `a0ffe09b04…` file as-is — **zero new adjudication**. Corpora/frames:
  the stage-2 pins verbatim.

---

## 5. The FREEZE delta (deliverable 3 — exactly what the coordinator must register; nothing else)

**(a) Assumption registrations (registry/assumptions.jsonl, append-only):**
PROPOSED-ASM-1010…1017 (the rev-B block, still pending — a PRECONDITION of
this freeze) and PROPOSED-ASM-1100…1109 (this spec, §6).

**(b) New registry record — `registry/experiments/deconf-b.json` (kot-reg/1),
frozen by the experiment-designer role after green mock + skeptic pass:**

- hypotheses/branches/verdict rows: DECONF §5.2/§6 verbatim (TOST collapse /
  LCB superiority / inconclusive / instrument-invalid), rider verbatim, the
  §1 envelope-class restrictions (G2 diagnostic, R-1 only, lexical-precursor
  licence space, no competitiveness sentence);
- design cells: n = 333 (item-id list = all gold_ext-resolved d-adj-t ids,
  list sha256 computed at freeze), seeds {0,1,2,3,4}, k = 4, m = 3, threshold
  2/3, cap 512, arms per §2.1 (kernel arm omitted per §3.3 or reinstated per
  its fallback);
- statistics: paired BCa B = 10,000 with pinned PRNG seed; Holm family +
  realisation per §3.2; the §1 power section verbatim (planning inputs,
  formulae, 0.922-at-floor result, sensitivity) + the §1.6 simulation script
  and its output;
- **pin block:** d-qa-t corpus kot-hash `7179ee67…`; d-adj-t labels sha256
  `a0ffe09b04…` + summary sha256 `54820db3…`; kernel-v0 `8209cada…` /
  molecules-v0 `69f0c8a3…` kot-hashes; GS-A `gs-a.jsonl` sha256 `4a28f7fa…` +
  gsa-manifest; `f2b_runner.py` sha256 `b62c3a72…` (byte-identical import,
  §2.1); `poc/deconf-b/stageb_runner.py` sha256 (at freeze); query-fn +
  leak-check source sha256; BM25 params + rendered-corpus + index sha256;
  frames file sha; R1 revision `12fd25f7…`; Modal image
  `im-6uXR6RyVQV15h2B3gtpOG2` + requirements sha `0fac7243…`; det_u
  probe-key schema string; bootstrap PRNG seed;
- lifecycle ledger schema per PROPOSED-ASM-1015; worst-case budget 2.9 GPU-h
  / ~$12 with the spend stop.

**(c) Bead + role wiring:** create `P3-E-DECONF-B` per DECONF §11
(blocked-by: P3-E-DECONF-0 registration per §3.3; the d-adj-t pin — already
satisfied; this power sizing — satisfied by this spec at freeze);
`reuse-check.py check --record … --gate` before launch; runner-role
separation (designer never runs/grades); verdict-gen mechanical; Codex
cross-vendor audit on readout.

**(d) What is NOT frozen or touched:** no frozen f2b/f2b-transfer/knull
object changes; no RAGC/FRONT amendment (menu adoption is plain); no encoder
version change; no new image; no new adjudication; knull-v2's
authored-content channel untouched.

---

## 6. PROPOSED-ASM block (doc note; coordinator registers at commit; 1100–1109, disjoint; none is evidence)

| Proposed id | Scope |
|---|---|
| **PROPOSED-ASM-1100** | Stage-B size: n = 333 (all resolved d-adj-t gold_ext labels) × 5 seeds, all arms, k = 4; power ≥ 0.90 at Δ = 0.10 sized at the Holm worst-case floor α/4 (0.922 computed; normal-approx planning + mandatory freeze-time simulation confirmation, which governs on conflict); TOST power co-disclosed, not the sizing bar; the rev-B 250×3 default withdrawn as underpowered (§1). Instantiates PROPOSED-ASM-1013's sizing clause |
| **PROPOSED-ASM-1101** | Planning-variance provenance: σ_b²/σ_w² decomposed from the pinned stage-2 run-records (MEASURED at 250×3); retry-vs-retry maxima (0.0301/0.1600) = primary planning values; kernel−alone (0.0576) = disclosed pessimistic sensitivity with its internal-inconsistency note; application to the unrun GR-D-lite arm is STIPULATED-planning (§1.1–1.2) |
| **PROPOSED-ASM-1102** | GR-D-lite loop contract: candidate + m = 3 probes via the pinned `answer_once` keyed by det_u tuple (arm, item_id, seed, attempt, probe_index); accept iff ≥ 2/3 exact-key agreement; reject → resample; exhaustion → final = LAST attempt scored (run_verify_retry semantics mirrored); probes use the arm's own prompt + same docs, closed-space option-scoring parser, no judging template; calibration table mandatory (§2.2) |
| **PROPOSED-ASM-1103** | Retrieval pins: stdlib in-repo BM25 (k1 = 1.2, b = 0.75, lowercase `\w+`), corpus = ASM-0922 rendered covered records (GS-A strings, zero new prose), top-j to a 512-token cap (maintainer-adjustable at freeze), lexicographic-id ties, zero-hit → empty context + disclosure, hit@j diagnostic-only, retrieval deterministic + seed-invariant per item (§2.3) |
| **PROPOSED-ASM-1104** | ERR_QUERY_LEAK machine check: query = pinned concatenation of prompt-visible bytes only (never urn/record_path/sha/gold/id/type/metadata); runner re-derives the query from the rendered prompt and fails closed on mismatch; query function published + hash-pinned (§2.3) |
| **PROPOSED-ASM-1105** | Sequencing: A1 registration + registered re-run lands before/with the Stage-B freeze so the kernel-arm omission is registered-evidence-backed; pre-declared fallback reinstates the kernel arm (+~0.45 GPU-h, ≤3 total) if Stage B freezes first (§3.3) |
| **PROPOSED-ASM-1106** | Image + asset reuse: Stage B runs on the pinned f2b Modal image im-6uXR6RyVQV15h2B3gtpOG2 (requirements sha 0fac7243…) with repo-mounted stdlib additions only — NO new image build, no new dependency; GS-A store, d-adj-t labels, corpora, frames, R1 checkpoint consumed at their existing pins (§4.2) |
| **PROPOSED-ASM-1107** | FWER realisation: Holm over the four named one-sided contrasts; the primary's verdict branch fires on its Holm-adjusted p (adjusted LCB), unadjusted LCB95/90% TOST CI co-reported; power sizing at the worst-case floor is the conservative planning convention (§1.3, §3.2) |
| **PROPOSED-ASM-1108** | Code-change contract: f2b_runner.py byte-identical at sha b62c3a72… (any edit voids the A1 lemma and forces an A1 re-run); all Stage-B code in a new hash-pinned module importing the pinned functions; deterministic-arm seed-invariance asserted at run time and disclosed (§2.1) |
| **PROPOSED-ASM-1109** | Budget + stop: worst-case ledger 44,955 generations ≈ 2.9 GPU-h ≤ 3 / ≤ ~$12 ≤ $25 (MEASURED throughput anchors + STIPULATED 0.25 s context-query planning factor); exhaustion before primary readout = scientific stop + salvage, no retry; PROPOSED-ASM-1015 lifecycle ledger mandatory (§4.1) |

---

## Epistemic register

- **MEASURED (restated/consumed strictly inside envelopes):** stage-2
  run-record vectors + accs + latencies + prefill tokens + image/runner/label
  pins (poc/f2b-transfer/results-incoming/20260711-184448-modal/*); d-adj-t
  summary counts (n_ext_labelled 333, n_unresolved 27, labels sha a0ffe09b…);
  A1 complete certificate figures (C_dec = 1.0, full-360 d-qa-t grid; GS-A
  sha 4a28f7fa…; runner sha b62c3a72…) via deconf-a1.md with its §3
  substitution disclosure riding; stage-2 mechanical verdict facts via
  f2b-transfer-stage2.md with the PASS-PENDING-AUDIT rider riding (no
  licensing sentence of this spec depends on the audit — the variance and
  throughput anchors are run-record facts independent of the verdict);
  0.14 GPU-h campaign anchor via the resource plan.
- **DERIVED (this document's own computations, disclosed):** every variance
  decomposition, SE, power, TOST-power, and budget number in §1/§4; the
  250×3-underpowered finding; the pessimistic-corner inconsistency note.
- **STIPULATED:** the entire DECONF rev-B + RAGC + FRONT frame (adopted
  verbatim); every design choice in this spec, carried as
  PROPOSED-ASM-1100–1109; planning factors (0.25 s/context-query, cap 512).
- **EXTRAPOLATION (never a premise):** realised cost below worst case;
  expected gate passes (anchored, tested fresh).

This spec changes no frozen object, verdict, log, or registry file; runs no
GPU; performs no git/bd/kb operation. The coordinator registers the ASM
blocks, the experiment-designer freezes deconf-b.json per §5, the runner runs
it, verdict-gen + the cross-vendor audit read it out.
