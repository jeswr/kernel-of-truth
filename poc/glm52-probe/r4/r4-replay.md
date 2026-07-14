# R4 offline replay — M_oracle / M_kernel / M_emb on the committed GLM-5.2 probe fingerprints

> **Status: ANALYSIS-ONLY replay (Fable, 2026-07-14). Nothing frozen, nothing
> committed to the branch classifier — ASM-2013 fires only through the
> coordinator's mechanical pathway.** CPU-only on committed bytes plus one
> pinned-by-hash embedding artifact; no instance, no GPU, ~$0.
> Script: `r4_replay.py` (deterministic; seeds 20260712 / 20260724 recorded).
> Full numbers: `r4-replay.json`.

## 0. Executability determination

R4 is an **offline replay on committed bytes** — no GLM box needed:

- `docs/next/design/glm52-expert-drop.md` §7 item 1 (lines 1189–1191): "R4
  replay first, before any spend. The offline M_oracle/M_kernel replay
  (`interpretation-fable.md` §2 R4) is CPU-only on committed bytes, ~$0."
- `docs/next/design/glm-edrop-0-freeze-readiness.md` B4 (line 86): "CPU-only
  on committed bytes, ~$0 … completes the held ASM-2013 branch classifier."
- Governing spec: `poc/glm52-probe/interpretation-fable.md` §2 R4 (lines
  147–159); quantity definitions ASM-2013 /
  `docs/next/design/glm52-followup-experiment.md` §3.1 (lines 388–409).

## 1. DATA-INTEGRITY FINDING (new, load-bearing) — the committed .stats are session-cumulative

**[MEASURED this run]** The 24 committed `results/stats/f0NN.stats` files are
**cumulative usage dumps**, not per-prompt fingerprints: per-cell counts are
monotone non-decreasing across f000..f023 (0 violations in 328,193 cell
pairs), totals grow 111,904 → 371,336 (≈ +11.5k/prompt ≈ 21 tokens × 75
layers × topk-8 + MTP), and f000 already contains the 99,752 pre-P3
selections shown in its `[USAGE]` header line. Corollary: v2's "10,591 cells
present in all 24 fingerprints, ~94% mass" is exactly f000's cell set — the
"universal component" is in large part a **cumulation artifact**, not routing.

Consequences:

1. Per-prompt fingerprints are recovered **exactly** by first-differencing
   d_N = f_N − f_{N−1} (N = 1..23). f000's own fingerprint is unrecoverable
   from committed bytes (its pre-P3 per-cell baseline was not committed) →
   this replay uses **n = 23** prompts; concept `break.shatter` drops to n = 2.
2. Every committed analysis that read `.stats` as per-prompt fingerprints —
   `analyze_routing.py`, `analyze_routing_v2.py`, and therefore the pinned
   `routing-analysis-v2.json` numbers cited in the R4-frozen design (within
   0.912 / across −0.074, Δ 0.986) — ran on cumulative histograms, where
   within-concept prompts are **adjacent in run order** and adjacency alone
   inflates within-concept similarity. The v2 **numbers** are
   artifact-inflated; the v2 **qualitative conclusion survives** (§2 below).
3. The frozen expert-drop design §2.1 item 3 pins x_f as "exactly the
   `analyze_routing_v2.py` construction" over these same `.stats` files — if
   mask-building at freeze reads the cumulative bytes verbatim, the
   concept-conditional masks inherit the run-order contamination.
   **Surfaced as a pre-freeze design issue** (see §5).

## 2. Concept structure re-test on differenced fingerprints [MEASURED]

v2-style within/across cosine, 10,000 random label shuffles, seed 20260712,
n = 23:

| metric | within | across | Δ | perm p |
|---|---|---|---|---|
| raw cosine | 0.7276 | 0.6090 | **+0.1187** | **0.0001** |
| mean-centred cosine | 0.2566 | −0.0736 | **+0.3303** | **0.0001** |

Concept-shaped routing structure is **real on clean per-prompt data** —
attenuated (Δ 0.33 vs the artifact-inflated 0.986) but decisively nonzero.
The p_perm leg of ASM-2013 stands; its registered values need re-derivation
through the mechanical pathway on differenced fingerprints.

## 3. Replay method (interpretation-fable §2 R4, executed)

- **Pin simulation**: pin B (layer,expert) cells; per-prompt miss-fraction =
  unpinned usage mass / total mass on the held-out prompt's differenced
  fingerprint. Uniform per-expert bytes ⇒ relative miss-BYTE reduction ≡
  relative miss-MASS reduction **[STIPULATED-not-MEASURED: uniform ~18.9 MB
  int4 experts (19.8 GB / 1048 from the committed `[PIN]` lines); model
  shards not on this box]**. Static replay, no LRU dynamics [STIPULATED,
  per spec].
- **Matched RAM budget**: the probe's realized pin store grew 522 → 1048
  experts (9.9 → 19.8 GB, the RAM_GB≈20 GB auto cap) across runs; **primary
  B = 1048** (modal, 13/24 runs), sweep {262..2096} reported.
- **Policies** (all rankings: descending score, ties → ascending
  (layer,expert), per ASM-2344): **oracle** = prompt's own top-B;
  **global-hot** = top-B of the mean L1-normalized histogram of the other 22
  (held-out form); **kernel** = top-B of the prompt's concept's OTHER
  members (LOO, n = 1–2 training prompts); **emb** = top-B of the prompt's
  k-means cluster's other members (LOO).
- **Embedding leg**: `sentence-transformers/all-MiniLM-L6-v2` (the design
  §3.1 pinned model), ONNX realization, model sha256
  `6fd5d72f…6046452`, tokenizer sha256 `be50c362…572037`; text rule NFC +
  whitespace-collapse + strip, no case-folding; own-impl k-means k = 8, seed
  20260724, n_init = 10 (spec shape of design §3.1 item 2; stdlib-MT streams
  in place of the house DRBG — **replay-grade, not freeze-grade**
  [STIPULATED deviation]). Realized clustering: ARI 0.461 vs the concept
  partition, sizes [2,2,2,3,3,3,3,5], 0 singleton fallbacks.
- **Inference**: paired per-prompt differences, exact 2⁸ = 256 concept-cluster
  sign-flip enumeration (the design's inference shape; p floor 1/256 ≈ 0.004),
  one-sided; 10k prompt-level sign-flips as secondary (ignores clustering).

## 4. Results [MEASURED, differenced data, B = 1048 primary]

Median miss-fraction: oracle **0.512** | global-hot **0.640** | kernel
**0.638** | emb **0.643**.

| quantity | value | test |
|---|---|---|
| **M_oracle** (median rel. miss reduction, oracle vs global-hot) | **+19.8 %** (mean +20.0 %) | cluster-flip p = 0.0039 (floor) |
| **M_emb** (emb vs global-hot) | **−0.5 %** | — (direction: worse) |
| stronger deflator | global-hot | emb does not beat it |
| **M_kernel** (kernel vs stronger deflator) | **+2.6 %** | cluster-flip p = 0.035 |
| kernel vs emb head-to-head (matched label count) | kernel better 12/23; mean paired miss-frac diff +1.2 pp, median +0.3 pp | cluster-flip p = 0.094 (ns); prompt-level p = 0.016 (anti-conservative) |

Budget sweep (M_oracle / M_emb / M_kernel-vs-stronger): B=262: +5.0/−1.2/+0.0 %;
B=524: +9.8/−1.3/+0.7 %; B=786: +15.1/−1.1/+1.7 %; B=1048: +19.8/−0.5/+2.6 %;
B=1572: +27.5/+0.1/+3.6 %; B=2096: +36.4/+0.7/+3.2 %. Ordering is
budget-stable: oracle ≫ kernel > emb ≈≤ global-hot at every budget.

## 5. Reading (labelled)

- **[MEASURED]** Exploitable per-prompt routing structure exists at matched
  budget: M_oracle ≈ 19.8 % ≥ the 15 % Branch-C bar.
- **[MEASURED]** Kernel-concept conditioning captures almost none of it:
  M_kernel = 2.6 % vs the stronger deflator — far below the registered 10 %
  margin. **Kernel-specificity at the registered margin: ABSENT on this
  data.**
- **[MEASURED]** But the framing "a generic embedding-cluster conditioner
  suffices" is ALSO not what the data shows: the matched-label embedding
  conditioner is *weaker than unconditioned global-hot* (M_emb ≤ 0 at
  B ≤ 1048), and kernel beats global-hot with the honest clustered test
  (p = 0.035) while kernel-vs-emb is directionally kernel-favoring but ns
  (p = 0.094). **The kernel-vs-generic head-to-head is UNRESOLVED at n = 23.**
- **[ASSESSMENT]** The dominant fact is the conditioner-vs-oracle gap
  (2.6 % vs 19.8 %): with 1–2 training prompts per concept, ANY
  concept-level pin — kernel or embedding — recovers only a sliver of the
  per-prompt-exploitable structure, much of which is plausibly token-level
  idiosyncrasy no label-level conditioner can reach. This is exactly the
  thin-sample instability interpretation-fable §2 R4 pre-authorized us to
  declare: **the 24-prompt sample is too thin for a stable M_kernel**; a
  replay-grade re-probe (more prompts/concept, per-prompt stats dumps) is a
  separately priced maintainer decision — do not extrapolate from this.
- **[ASSESSMENT — binding nothing]** On ASM-2013's frame these values are
  Branch-B-shaped (not-A: M_kernel < 10 %; M_oracle ≥ 15 %). The classifier
  must NOT fire on this document: it fires through the coordinator's
  mechanical pathway, and its other leg (p_perm) is currently registered on
  cumulative-contaminated v2 numbers that need mechanical re-derivation
  (§2 gives the expected clean values). Note this replay is offline routing
  analysis — **not a capability benchmark**; no quality claim anywhere.

## 6. Blockers / follow-ups surfaced

1. **Pre-freeze design issue (new):** the frozen expert-drop design's §2.1
   x_f construction reads the cumulative `.stats` bytes as fingerprints; the
   trace-derived masks inherit run-order contamination unless the
   construction is amended to differenced fingerprints (and f000's
   unrecoverability is handled). Filed in beads.
2. Registered v2 numbers (p_perm inputs, `/mean_centered/*` pins) need
   mechanical re-derivation on differenced data before the classifier reads
   them.
3. `r4/minilm/model.onnx` (90 MB, hash above) is a fetched artifact — not
   for git; re-fetch by hash if needed.
