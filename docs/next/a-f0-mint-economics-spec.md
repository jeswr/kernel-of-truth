# A-F0 — cached-prefix mint economics (frozen experiment spec)

**Kernel of Truth programme — experiment spec, node N-AF0.**
Author: Kern (Fable experiment-designer role, designer-1), for the maintainer.
Date: 2026-07-10. Registry record: `registry/experiments/a-f0-mint-economics.json`
(kot-reg/2; frozen via `tools/registry/prereg-freeze.py`; this file is its pinned
prereg doc). Ladder position: the ASM-0463 rung after the A-E2 readout
(`registry/assessments/a-e2-census.json` fork resolution "PROCEED TO A-F0",
ASM-0563). Assumptions registered this pass: **ASM-0600…ASM-0609** (reserved
block 0600–0619) in `registry/assumptions.jsonl`. Epistemic tags as in N-IOC:
[MEASURED], [LIT-BACKED], [STIPULATED], [EXTRAPOLATION]; no EXTRAPOLATION is
load-bearing anywhere in this design.

---

## S1 — What A-F0 is, and what it can never be quoted as

A-F0 prices the **mint side** of the coverage-growth track: what it costs, in
real API dollars, tokens, and wall time, to mint one concept into the
`modelAuthored` tier through the cached-prefix Haiku definer (N-IOC §2.2), and
how that cost amortizes as the shared definitional prefix is reused across a
mint batch. It simultaneously resolves the maintainer's symbolic-output vs
thinking-time fork (N-IOC §2.3) with the four pre-shaped arms.

DECISION: A-F0's scope, honesty caps, and pipeline identity are frozen as
  registered — mint cost ONLY; never quotable as end-to-end viability;
  net-positive mint economics is NECESSARY-NOT-SUFFICIENT for idea A (the
  consumption channel — K-A3 tokenizer-extension null, trained-compressor
  null, 1-token delivery, accuracy non-inferiority — stays UNMEASURED, and
  K-A4 mappability stays UNPRICED per ASM-0560); the result serves the whole
  coverage-growth track (idea B's re-entry lever, the linter staircase) and
  survives a K-A2 fire; nothing here displaces the feasibility-synthesis §5
  critical path [STIPULATED: ASM-0600].

LOAD-BEARING: the mint baseline to beat is the s1-G pipeline — 31.7% gate-pass
  of attempted records, 13 legal records / 50 concepts (26% yield),
  ~1.8 calls/concept in volume-runner form, $0.0202/concept, ≈ **$0.078 per
  legal record** (API-equivalent accounting via the claude-CLI transport)
  [MEASURED: data/haiku-tier/s1-experiments/s1-report.md sha256
  238db0ddfaca614f30886afebfee219430062ed067c9f7d2ded83a489118e5b5].

LOAD-BEARING: A-E2 established the selection-side value pool this cost pairs
  against as a MEMBERSHIP UPPER BOUND only — blended wordlike @10k concepts
  33.4–41.7% (SmolLM2, uniform) / 18.5–24.0% (Qwen2.5), fertility-driven and
  concentrated in fi/ja/es; K-A2 interpretively does not fire
  [MEASURED: registry/assessments/a-e2-census.json;
  poc/a-e2/results/summary.json sha256
  90eb62834b06c3b929dc84073430eed88d974ff7de9280bd3421f7203b1e3a18].

## S2 — Mechanism under test and price basis

The definer is `claude-haiku-4-5-20251001` called **directly over the Messages
API** with prompt caching — a new pipeline identity per the s1 convention (the
pinned call configuration is part of pipeline identity); the s1-G claude-CLI
pipeline is left byte-untouched as the baseline [STIPULATED: ASM-0600].

Prefix (system blocks, `cache_control: {type: "ephemeral"}` on the last
block, deterministically serialized): the framework-G how-to-define
instruction, the closed grounding lexicon, the trap list, the ref catalog
(kernel-v0 + molecules-v0 depth ≤ 3 + the accumulated haiku-tier catalog at
its pinned mint-manifest state), and the few-shot exemplars. Variable suffix
(user turn): the target word + its pinned fetched extracts (A-F2(b)
source-fed form). Repair call: same prefix + the draft + the real `gates.mjs`
validator error list.

DECISION: every USD figure in A-F0 is API usage fields × the frozen price
  table — input $1.00/MTok, output $5.00/MTok (thinking bills as output),
  cache read $0.10/MTok, cache write $1.25/MTok (5-minute TTL), Batch 50%
  discount as a derived projection multiplier only, minimum cacheable prefix
  4096 tokens on Haiku 4.5, budgeted-thinking-only on Haiku 4.5 — checked
  2026-07-10 against the current Claude API reference and byte-consistent
  with N-IOC §2.2's 2026-07-09 live-docs verification; the runner re-verifies
  at staging preflight and any discrepancy is an ops amendment before first
  spend [STIPULATED: ASM-0601].

## S3 — Design: arms, sample, protocol, budget

**Arms** (identical concepts, framework-G gate-in-the-loop, source-fed):

| Arm | Output form | Thinking |
|---|---|---|
| a | current G output (JSON record + minimal frame) | off |
| b | direct-symbolic: record only, compact serialization, zero prose | off |
| c | = b | enabled, `budget_tokens: 1024` |
| d | = a | enabled, `budget_tokens: 1024` |

DECISION: the four N-IOC §2.3 arms are frozen as above, all in the A-F2(b)
  source-fed configuration (the conservative case for caching economics and
  the baseline-matching input shape); the A-F2(a) word-only arm and the
  Batch-vs-interactive delta are deferred to A-E1; TTFT is dropped (batch
  minting is throughput-bound) in favour of wall latency per call; repair
  policy is the volume-runner form (at most one gate-error-fed repair, only
  for gate-failing attempted drafts); sampling parameters are omitted (API
  defaults, one stochastic sample per concept per arm, no determinism claim)
  [STIPULATED: ASM-0603].

DECISION: sample n = 60 English concepts identical across arms — 45
  seed-pinned stratified draws from the haiku-tier inventory (15 per band
  A/B/C; seed string `a-f0/1|sample|20260710`; already-minted lemmas
  excluded; staging fetch failures replaced in-band and logged) plus the 15
  s1 hand-authored-overlap anchors verbatim; English-only because the English
  framework-G pipeline is the only executable fail-closed mint path today
  [STIPULATED: ASM-0604].

The cross-lingual cost question raised by A-E2's fi/ja/es concentration is
carried as a registered sizing expectation, load-bearing for nothing: mint
cost is expected to transfer to first order because it is dominated by shared
prefix + output length, not target-word language; A-E1 owns the measurement
[EXTRAPOLATION: ASM-0606].

DECISION: run protocol — concurrency 1; fixed arm order a → d → b → c; two
  byte-identity prefix groups {a,d} and {b,c} (the thinking toggle preserves
  the tools/system cache tier, so d and c run warm); first call per group is
  the cache-writing call; cold-start amortization curves defined on arms a
  and b only; steady-state marginal cost (last-20-concepts mean) on all four
  arms; TTL re-write events logged and left inside measured totals
  [STIPULATED: ASM-0605].

**Budget.** Expected spend ≈ $3.5–6.5 all-in (sizing only: ~450 calls at
~30k cache-read + ~1.5k uncached suffix + 0.4–1.4k output each; synthetic
dry-run of the pinned analysis at these shapes prices the full design at
≈ $4.1) — inside the maintainer's standing ~$5–10 clearance for A-F0
(ASM-0463). Hard cap: the runner tracks cumulative usage × price table per
call and **aborts at $10.00**; an abort fails `budget_within_cap` and the
verdict is INSTRUMENT-INVALID, never a economics reading. `max_tokens`: 2000
(arms a/b), 3200 (arms c/d; > budget_tokens as required).

## S4 — Metrics (exact definitions; computed only by the pinned script)

Per arm: `n_concepts`, `n_attempted`, `n_legal`; `gate_pass_attempted` =
legal/attempted; `cf_rate`, `parse_fail_rate`; `calls_per_concept`;
`usd_per_concept` = arm spend / concepts; **`usd_per_legal_record`** = arm
spend / legal records (the decision variable); wall `mean_latency_s` /
`p90_latency_s`; mean tokens per call by class (uncached input, cache read,
cache write, output). Amortization: cumulative mean usd/concept at
k ∈ {1,5,10,20,40,60} (arms a, b) and steady-state marginal usd/concept
(all arms); `derived_batch_projected_usd_per_concept` = usd_per_concept × 0.5
(projection only, tagged as derived). Fork diagnostics (reported-only):
`output_form_paradox` (b cuts output tokens vs a but costs ≥ or is slower),
thinking deltas d−a and c−b on $/legal record, `thinking_helps_cost`.
All definitions are frozen in `analysis/a_f0_mint_economics.py` (pinned in
the registry record); the runner computes nothing.

## S5 — Decision rule and gates

DECISION: the frozen mint-economics gate — an arm is LAWFUL iff ≥ 55/60
  concepts processed and ≥ 5 legal records; **PASS** iff the best lawful
  arm's `usd_per_legal_record` ≤ 0.75 × $0.078 = **$0.0585**; **FAIL**
  (K-A1-mint fires: the cached-prefix definer is dead as an economics play)
  iff a lawful arm exists and the minimum lawful `usd_per_legal_record` ≥
  $0.078 (no improvement at all); otherwise INCONCLUSIVE
  [STIPULATED: ASM-0602].

Instrument gates (any failure ⇒ INSTRUMENT-INVALID, never FAIL/PASS):
`prefix_min_cacheable_valid` (both prefixes ≥ 4096 tokens by `count_tokens`
at staging), `cache_integrity_valid` (cache_read_input_tokens > 0 on ≥ 90% of
post-first-call requests per prefix group — the silent-invalidator check),
`run_completeness_valid` (≥ 55/60 concepts per arm), `budget_within_cap`
(≤ $10.00, no abort) [STIPULATED: ASM-0605].

DECISION: the mechanical verdict decides economics only; the N-IOC §2.3
  ADOPTION rule (argmin $/legal record subject to gate-pass within 10pp of
  arm (a) and no fidelity regression on the 15 overlap anchors, s1 0/1/2
  scale, regression = mean > 0.25 below the s1 draft mean 1.47 or any
  0-scored record) is applied in the designer-side interpretive assessment
  after the verdict, and a fidelity regression vetoes adoption of a cheaper
  arm regardless of PASS; the runner never judges fidelity
  [STIPULATED: ASM-0608].

Expected-direction notes, sizing only, never premises: the N-IOC worked
estimate puts the interactive cached path at ≈ $0.011/concept ⇒
≈ $0.042/legal record at s1 yield (PASS branch reachable), while a repair-rate
or yield collapse on the new transport lands ≥ $0.078 (FAIL branch reachable);
both branches stay live at n = 60. The estimate is not a premise; A-F0
measures it.

## S6 — Pairing against A-E2 (the only lawful frame)

DECISION: pairing A-F0's measured mint cost against A-E2's selection-side
  savings is interpretive and quotable only in the sizing form "at the
  measured mint price, a 10k-concept kernel-A costs $X all-in (amortization
  curve attached); A-E2's MEMBERSHIP UPPER BOUND on blended prefill savings
  at that budget is Y–Z% (span across weight arms, K-A4 unpriced, consumption
  unmeasured)" — never a net-positive claim, never achievable savings, never
  end-to-end viability [STIPULATED: ASM-0609].

Worked shape (illustration of the frame, numbers to be filled by the run):
at $c per legal record, 10k legal records cost $10,000·c + the amortized
prefix writes; the A-E2 curve at the 10k anchor supplies the paired
upper-bound savings band; the K-A4 pricing instrument (ASM-0560 prerequisite
for A-E1) and the consumption channel (A-E3/F3) are the two named gaps that
must close before any net statement.

## S7 — Registry mechanics, staging, and runner boundaries

Record: `registry/experiments/a-f0-mint-economics.json` (kot-reg/2, frozen).
Analysis: `analysis/a_f0_mint_economics.py` (pinned sha; input format
documented in the script header). Run artifacts land under `poc/a-f0/`
(quarantined — A-F0 outputs are experiment artifacts, NOT tier records; any
promotion into `data/haiku-tier/records` is a separate post-verdict
coordinator decision). Staging plan (ops amendments pin the placeholders
before any spend):

1. Stage `poc/a-f0/run-a-f0.py` (runner), `poc/a-f0/prompt-manifest.json`
   (the two serialized prefix block sets + their `count_tokens` results +
   sha256s), `poc/a-f0/sample-manifest.json` (the 60 concepts + seed
   derivation + fetch pins) → ops amendment pins all three.
2. Preflight: re-verify the ASM-0601 price table against live docs; verify
   API key present; `count_tokens` both prefixes ≥ 4096; 2 calibration calls
   (not in analysis denominators, logged, counted against budget).
3. Run arms a → d → b → c serialized; per-call raw usage + latency + gate
   outcomes appended to `poc/a-f0/results/run-log.jsonl`; checkpointed;
   hard-abort at $10.00.
4. Pin `data/a-f0-mint` (run outputs) by corpus-pin ops amendment; log-append
   the final-phase record; verdict-gen; designer-side interpretive assessment
   (fidelity + adoption + A-E2 pairing).

Runner preconditions and boundaries: an Anthropic API key provisioned by the
maintainer at run time is a hard precondition (none exists on the box at
design time — checked 2026-07-10); absent key ⇒ BOUNDARY STOP to the
maintainer, no claude-CLI fallback (that would silently revert the pipeline
identity under test). The runner executes the staged harness mechanically;
any undecided situation is a boundary stop back to the designer, never
improvisation. The baseline-comparability weaknesses of the $0.078 comparison
(API-equivalent vs API-billed accounting, catalog growth since s1, binomial
yield noise) are registered and binding on any PASS/FAIL citation
[STIPULATED: ASM-0607].

## S8 — Envelope summary and ASM index

Any A-F0 verdict is scoped to: this definer model and pinned call
configuration, this prefix composition at the pinned catalog state, English
source-fed minting on this 60-concept sample, and the frozen price table.
It licenses pipeline-choice and A-E1-configuration decisions on the mint
side only. It does not measure consumption, mappability, cross-lingual cost,
Batch economics, or volume-scale yield; it is never quotable as compression
viability (ASM-0600/0609); and kernel-expressibility coverage remains 0.3542
at rung molecules-v0, measured by m0b on one incomplete kernel-v0 instance —
no coverage-general claim exists here.

| ASM | Role |
|---|---|
| ASM-0600 | scope, identity, honesty caps |
| ASM-0601 | price-table pin + preflight re-verification |
| ASM-0602 | decision rule, margins, lawfulness floors |
| ASM-0603 | arms, A-F2 split, TTFT drop, repair policy |
| ASM-0604 | sample + English-only scoping |
| ASM-0605 | amortization protocol + cache-integrity gate |
| ASM-0606 | language-transfer expectation (EXTRAPOLATION, load-bearing for nothing) |
| ASM-0607 | baseline-comparability envelope |
| ASM-0608 | verdict/adoption split + fidelity veto placement |
| ASM-0609 | A-E2 pairing frame (upper-bound discipline) |

*Cross-references:* `docs/next/io-compression-ideas.md` §§2.2–2.3 (N-IOC);
`docs/next/io-compression-signoff.md` §3 (N-IOC-S, ASM-0460–0464);
`registry/assessments/a-e2-census.json` (A-E2 readout, ASM-0560–0564);
`data/haiku-tier/s1-experiments/s1-report.md` (baseline);
`docs/kernel-design-directives.md` §§2, 6, 7.
