# CONTAMINATION NOTE — routing-analysis-v2 superseded by v3 (magnitude claims)

> **Status: DRAFT supersession record (Fable, 2026-07-14; bead
> `kernel-of-truth-xafk`). ANALYSIS-ONLY correction of existing committed
> bytes — no probe re-run, nothing frozen, no branch classifier fired.
> Uncommitted; the coordinator commits after review.** The contaminated
> pinned file `results/routing-analysis-v2.json`
> (sha256 `e9d6813f99a6efa03645a3c15260a84c3d47221a3d0061ad6bbc68749e1c57cc`)
> is deliberately NOT edited in place — it stays as the honest record of
> what was computed; this note marks it superseded.

## 1. What happened [MEASURED: r4/r4-replay.md §1]

The 24 committed `results/stats/f000..f023.stats` files are
**session-cumulative usage dumps**, not per-prompt fingerprints: per-cell
counts are monotone non-decreasing across f000..f023 (0 violations in
328,193 cell pairs), totals grow 111,904 → 371,336, and f000 already
contains the 99,752 pre-P3 selections shown in its `[USAGE]` header.
`analyze_routing.py` (v1, already VOID) and `analyze_routing_v2.py` read
these as per-prompt fingerprints. On cumulative histograms adjacent prompts
share almost all mass by construction, and within-concept prompts are
**adjacent blocks in run order** — so the pinned v2 magnitudes confound
concept structure with run-order adjacency and are **adjacency-inflated**.
The v2 "universal component" (10,591 cells, 93.92% mass) is in large part
f000's cell set — a cumulation artifact, not routing.

## 2. The correction (successor artifacts, this directory)

- **`analyze_routing_v3.py`** (sha256
  `e633e2a0f1f1a44e787bdbc93f976b1ab1b80cae2cd4aee84690ac464c4266f9`) —
  the v2 construction verbatim, run on **first-differenced per-prompt
  fingerprints**: d_N = f_N − f_{N−1} (N = 1..23, strictly-positive cells),
  which recovers per-prompt fingerprints exactly BECAUSE the dumps are
  cumulative; cumulativity is re-verified fail-closed at load
  (`ERR_NOT_CUMULATIVE`). f000's own fingerprint is **unrecoverable** (its
  pre-P3 per-cell baseline was not committed) → f000 dropped: n = 23,
  concept `break.shatter` n = 2. Deterministic: seed 20260712, 10k random
  label shuffles, pure stdlib; source-stats sha256s recorded in the output
  provenance block.
- **`routing-analysis-v3.json`** (sha256
  `d31be1c71003018d0f3ac39d5df490d4a28c29b6f7fc1ec5498b90e65220253d`) —
  the decontaminated numbers, with a provenance block naming the
  contamination, the recipe, the source hashes, and the superseded file.
- **Cross-check [MEASURED]:** v3's raw and mean-centred blocks reproduce
  `r4/r4-replay.json` `/structure_on_differenced_fingerprints` (independent
  numpy implementation, `r4/r4_replay.py`) to 4 decimal places.

## 3. Corrected vs superseded numbers

| quantity | v2 (CONTAMINATED, cumulative, n=24) | v3 (CLEAN, differenced, n=23) |
|---|---|---|
| raw cosine within / across / Δ | 0.9977 / 0.9545 / +0.0432 | 0.7276 / 0.6090 / **+0.1187** |
| raw perm p (10k) | 0.0001 | **0.0001** |
| mean-centred within / across / Δ | 0.9119 / −0.0740 / +0.9859 | 0.2566 / −0.0736 / **+0.3303** |
| mean-centred perm p (10k) | 0.0001 | **0.0001** |
| ever-active keyspace | 16,483 | 15,850 |
| universal cells / mass frac | 10,591 / 0.9392 | **2,027 / 0.4178** |
| sense pair `break` (centred Δ, p) | n=9: +0.1955, p 0.0029 | n=8: **+0.2564, p 0.0033** |
| sense pair `bank` (centred Δ, p) | n=6: +0.3259, p 0.1026 | n=6: **+0.3844, p 0.1026** (n=6 permutation floor) |

**What survives [MEASURED]:** the qualitative concept→routing structure —
within > across at p = 0.0001 under the registered 10k-shuffle test on
clean data; both sense minimal-pairs keep sign, `break` stays significant.
**What does not:** every v2 MAGNITUDE (the 0.912/−0.074 separation is
~3× inflated: clean centred Δ +0.3303 vs the inflated +0.9859) and the
"~94%-mass universal component" framing (clean: 2,027 cells, ~42% mass).

## 4. Downstream consumers that MUST switch to v3

Anything citing routing-analysis-v2 **magnitudes** (structure-exists
p-value claims survive but should re-cite v3):

1. **`docs/next/design/glm52-expert-drop.md` (glm-edrop-0) — PRE-FREEZE
   AMENDMENT REQUIRED; see §5 below.** §2.1 item 3 (x_f pinned to "exactly
   the `analyze_routing_v2.py` construction"), §2.1 item 1 (universal-core
   figures 10,591/0.9392 AND the pooled-mass core rule — see §5b), §2.1
   item 2 + §2.2 (0.9119/−0.0740 rationale; sense-pair numbers), header
   evidence pins of routing-analysis-v2.json sha `e9d6813f…`, §3.1 [R4]
   items referencing the v2 normalization (line ~1638).
2. **ASM registry (`registry/assumptions.jsonl`)**: ASM-2042 (the v2
   result record — supersede/annotate), ASM-2034 (classifier
   reconciliation with v2), ASM-2013 (the frozen branch classifier's
   registered p_perm leg currently points at v2 values — re-register on
   v3 through the coordinator's mechanical pathway before the classifier
   reads it), ASM-2231/2233/2342/2343/2344 (evidence-base and pinned-mask
   entries whose backing_refs cite v2 numbers or the v2 construction).
3. **`docs/next/design/glm52-followup-experiment.md`** §R0 evidence
   preamble, §3.1 (ASM-2013 quantity definitions / p_perm inputs), §7
   backing_refs.
4. **Evidence packs `poc/glm52-probe/asm-glm-drop-2230-2239.json`,
   `asm-glm-drop-r1-2290-2293.json`, `asm-glm-drop-r2-2340-2352.json`** —
   all pin routing-analysis-v2.json sha `e9d6813f…` as primary evidence.
5. **`docs/next/analysis/steering-read-2026-07-13.md`** (line ~26 cites
   0.9119/−0.0740 as "strong" signal — magnitude claim, now ~3× inflated).
6. **`docs/next/feasibility-synthesis-v7.md`** item 9 — already flags the
   contamination; point it at v3 as the mechanical re-derivation.
7. `poc/glm52-probe/interpretation-fable.md` — no direct v2-number pins
   found by sweep; no action beyond awareness.

(v1, `results/routing-analysis.json` / `analyze_routing.py`, was already
VOID for the cyclic-shift defect; it is doubly void — also contaminated.)

## 5. glm-edrop-0 §2.1 amendment — exact wording needed [DRAFT, editable pre-freeze]

**(a) x_f construction (§2.1 item 3, MANDATORY — masks would otherwise
inherit the contamination byte-for-byte).** Replace the per-cluster score
input definition with:

> For fingerprint f_N (N = 1..23), let d_N = the first-differenced
> per-prompt fingerprint d_N(ℓ,e) = f_N(ℓ,e) − f_{N−1}(ℓ,e) over the
> committed `.stats` bytes (strictly-positive cells; cumulativity verified
> fail-closed at build time), and x_f(ℓ,e) = d_N's mass at cell (ℓ,e) over
> the **15,850-cell differenced ever-active keyspace**, L1-normalized over
> ALL cells jointly — exactly the `analyze_routing_v3.py` construction
> behind the pinned routing-analysis-v3.json (sha256 `d31be1c7…`); absent
> cells = 0; cells outside the keyspace = exactly 0.0. **f000 is excluded
> from every roster** (unrecoverable baseline): μ(ℓ,e) is the elementwise
> mean of x_f over the 23-fingerprint roster (reduced further under LOO),
> the frozen §2.1 concept table's member sets drop f000, and
> `break.shatter` has F_c of size 2 — under leave-one-out its conditional
> map is built from **n = 1** training prompt (disclose in the design's
> coverage statement; the ≥16 concept-tail slots guarantee is unaffected).
> All downstream rules (combination, fill-and-trim, tie-breaks, LOO
> recomputation) unchanged.

**(b) Universal core (§2.1 item 1, DECISION REQUIRED — flagged, not
resolved here).** The materialized core (sha `632bcd18…`) ranks experts by
pooled mass **summed over the 24 cumulative dumps**: since
f_N = f000 + Σ_{i≤N} d_i, that pooled sum equals 24·f000 + Σ_i (24−i)·d_i —
i.e. the core ranking is dominated by f000 (which embeds the 99,752
pre-P3 selections) and weights earlier prompts more than later ones. The
coordinator must either (i) re-pin the core by the same τ=0.50/cap-48 rule
on the SUM OF DIFFERENCED fingerprints (clean, order-invariant; new hash,
regenerated + re-verified at freeze) — recommended — or (ii) explicitly
re-stipulate the existing core as an arbitrary-but-fixed a-priori set,
disclosing the run-order/pre-P3 weighting. Either way the "10,591
universal cells / 93.92% mass" rationale text must be replaced with the
clean figures (2,027 / 0.4178) or dropped.

**(c) Rationale citations (§2.1 item 2, §2.2, header pins).** Re-point
magnitude citations to routing-analysis-v3.json keys (`/mean_centered/*`:
within 0.2566, across −0.0736, Δ +0.3303, p 0.0001;
`/sense_pairs_centered/break`: n=8, Δ +0.2564, p 0.0033;
`/sense_pairs_centered/bank`: n=6, Δ +0.3844, p 0.1026) and swap the
evidence-pin sha `e9d6813f…` → `d31be1c7…`. The qualitative rationale
("concept separation lives in the residual space") survives unchanged.

## 6. Labels

- **[MEASURED, recomputed this pass]**: everything in §3's v3 column;
  the v2↔v3 cross-check against r4-replay.json.
- **[STIPULATED]**: that first-differencing recovers per-prompt
  fingerprints exactly (follows from cumulativity, which IS measured:
  0/328,193 monotonicity violations, re-verified fail-closed at v3 load);
  f000 unrecoverability (its baseline was not committed — absence of
  bytes, not a computation).
- Nothing here fires ASM-2013; the classifier reads v3 only through the
  coordinator's mechanical pathway after re-registration.
