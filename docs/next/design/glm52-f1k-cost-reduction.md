# F1-K reduced-cost execution protocol (GPT-5.6 overflow design, coordinator-transcribed)

Fable was capped; this reduced-cost protocol was designed by GPT-5.6 (codex, xhigh) as overflow and
transcribed here by the coordinator. It cuts the F1-K ceiling **$550 → $149** without weakening
validity. Registered as ASM-2205 (EXTRAPOLATION — a cost projection resolved by the metered run).

## Reduced ceiling: **$149**
Arithmetic: `22,920 prefills × 100 s ÷ 1.20 (pinning speedup, pessimistic) ÷ 3,600 × $0.28/h (spot) = $148.56` → **$149**.
Modeled hours 439–531 h; full price/speed corner band $88–149; at the deliberately pessimistic 1.20×
speed the spot-rate band is $106–149. EC2 instance compute only (same scope as the original $550);
storage/tax/transfer separately accounted.

## Configuration (the standing cost directive applied)
1. **Spot i4i.2xlarge** — $0.20–0.28/h vs $0.69 on-demand (1.20–1.45× cost lever), with per-item
   checkpoint/resume so a spot interruption just resumes. (This is the DEFAULT for all GLM-5.2 runs now.)
2. **Expert-pinning + warm page-cache** — priced conservatively at **1.20×** throughput (up to ~1.45×);
   grounded in the P0 probe's measured hit-rate (h₀=0.34) and 75% disk fraction, not optimism.
3. **R = 3 deflator derangements** (design's own degradation order, ASM-2037/§1066): the 5→3 cut
   removes mapping-average-precision repetitions, NOT dose matching — R=3 still preserves carrier
   length, construction provenance, and marginal covariance, so the d1-drng deflator stays dose-exact.
4. **Instance sizing:** i4i.4xlarge needs >2× (>~78% hits) to break even, i4i.8xlarge >4× (Amdahl-impossible);
   neither is ceiling-grade cheaper. **Stay on 2xlarge.**

## Validity preserved (verbatim from the overflow design)
- The powered sample is **never reduced**: ρ_U=0.10 → **n=1,440** (not the superseded ~1,180).
- Licensing unchanged: exact cluster sign-flip permutation p<0.05 under the registered
  cluster-sign-symmetry null **AND** observed lift ≥3 points; cluster-bootstrap fallback available.
- One candidate-independent label-logit prefill remains the scoring unit.

## Co-location with #27 (GLM expert-drop)
After F1-K finishes and its durable checkpoint is sealed, run the #27 expert-drop on the **same spot
instance** to amortize model staging/conversion/bring-up/cache-warming — as a **fresh process with its
own manifest + accounting**; never interleave its function-changing TOPK/drop arms with F1-K.

```json
[
 {"id":"ASM-2205","tag":"EXTRAPOLATION","claim":"F1-K reduced-cost ceiling is $149 (from $550) via spot i4i.2xlarge ($0.20-0.28/h) + expert-pinning (1.20x pessimistic) + R=3 derangements; modeled 439-531 instance-hours, band $88-149. n=1,440 and the exact cluster-sign-flip licensing (p<0.05 AND lift>=3) are unchanged; R=3 preserves the d1-drng deflator's dose-exactness; larger instances do not break even. EC2 compute only.","backing_ref":"docs/next/design/glm52-f1k-cost-reduction.md; GPT-5.6 overflow design over glm52-followup-experiment.md sections R1.1/R3/R-REV4 + poc/glm52-probe/results/probe-main.log","owner":"designer-8","load_bearing":false,"status":"open","resolution_path":"Resolved by the actual metered spot-instance spend recorded in the F1-K run's cost ledger at completion; if pinning yields <1.20x or spot rates exceed $0.28/h, the degradation order (R stays 3, n never cut) governs and the ceiling is re-derived from measured throughput."}
]
```

## GPU option evaluated (maintainer suggestion) — REJECTED, stay CPU-spot
GPT-5.6 overflow analysis of running on an approved AWS GPU instance (colibri CUDA tier = VRAM-resident
pinned experts): **RECOMMENDATION = stay-CPU-spot.** The only economical GPU (24 GB A10G/L4) covers too
little of the KaE routing mass to collapse the disk bottleneck → only ~1.05x vs pinned CPU; the big-VRAM
GPUs that *would* hold the hot working-set (multi-A10G / A100) cost several times the $149 CPU ceiling.
GPU reserved only for an optional ~$5 benchmark-only cross-check. Reproducibility caveat moot (not used).
The $149 spot-i4i + pinning + R=3 plan stands.
