# SCALE-1 S0 first rung — honest readout at m = 10,000

date: 2026-07-12 · pipeline: `poc/scale/` · full tables: `scale-s0-n10000-report.{json,md}` · smoke: `scale-s0-n1000-report.json`

**Epistemic status.** Exploratory S0 engineering pilot (design §8): MEASURED numbers over a
STIPULATED selection rule, STIPULATED typing crosswalk and an EXPLORATORY §6.3 import
vectoriser (`kot-enc-import/0-poc` — NOT construction B, NOT an encoder version; kot-enc-B/1
pins untouched). All 100k/1M rows are [EXTRAPOLATION] — to be measured, never premises.
**This readout makes NO feasibility conclusion; CORRECTNESS and EFFICIENCY remain
INCONCLUSIVE-PENDING (design §14).**

## What was built and measured

- **Ingest:** 10,000 WordNet 3.1 synsets by summed SemCor tag_cnt from the pinned
  `index.sense` (deterministic; nonzero pool 27,210; boundary tag_cnt = 4; POS mix
  n 4,713 / v 2,902 / a 1,810 (840 heads + 970 satellites) / r 575; 58,270 axioms,
  5.83/concept; 77.8% of axiom targets fall outside the subset — disclosed identity-atom
  fallback in the vectoriser).
- **Typing:** full ck-ufo-scale/1 sidecars for all 10k via the §4.1 cascade; split below.
- **Vectors:** six deterministic stores (canon fp64 D=8192 → fp32 persisted; X4-label JL
  proj512/proj576; native512/576; native512+lexical-block probe). Byte-determinism verified
  (independent recomputation, sha256-identical, `out/n1000/vec/verify-report.json`).
- **Wall:** 1k smoke ~90 s end-to-end; 10k ≈ 6.5 min vectorise + ~8 min metrics on one
  niced shared core — within the 30-min budget, no partial-run fallback needed.

## Imported-vs-inferred UFO-type split (m = 10,000)

| field | source-asserted | rule-inferred (hard) | soft-candidate | underdetermined |
|---|---|---|---|---|
| denotation_level | **1.27%** (instance flag — the ONLY imported UFO structure in WordNet) | 98.73% | 0 | 0 |
| ontic_category | 0 | 52.04% (STIPULATED lexFile crosswalk) | 41.92% | 6.04% |
| sortality | 0 | 11.96% (kind 10.7%, non-sortal 1.3%) | 2.54% (role 2.0%, phase 0.5%) | **85.50%** |
| rigidity | 0 | 10.69% | 2.54% | **86.77%** |
| identity | 0 | 0 | 0 | **100%** |
| dependence | 0 | 0 | 0 | **100%** |

## Predicted vs measured collision/margin (§6.5)

Disjoint class = no direct edge, no shared axiom target, different lexFile (the class the
independent-vector Gaussian model actually describes).

| store | D | σ pred 1/√D | σ meas | max-spurious pred √(2ln m/D) | median per-concept max-DISJOINT | median per-concept max-ANY |
|---|---|---|---|---|---|---|
| canon8192 (1k sample) | 8192 | 0.01105 | **0.01106** | 0.0411 @m=1k (0.0474 @m=10⁴; design quotes ≈0.046) | 0.0353 | 0.0594 |
| proj512 | 512 | 0.0442 | **0.0456** | 0.1897 | 0.169 | **0.3857** |
| proj576 | 576 | 0.0417 | **0.0432** | 0.1788 | 0.1621 | **0.3867** |

**The Gaussian-crosstalk curve HOLDS** — σ within 3% at every D, per-concept max-disjoint
under the predicted curve. **But it is not the binding constraint:** 2,008/10,000 records
(20.1%) sit in 475 identical-token-multiset groups (largest: 466 zero-axiom adverbs; 662
records have no axioms at all) → **124,343 vector-identical pairs (cos > 0.9999)** in every
lexical-free store, i.e. §6.5 collision class 2 realised at 20% incidence. These are
*legitimate* identical semantic blocks under the record-identity rule (glosses/lemmas are
annotations outside identity) — a representational-poverty ceiling of AxiomsOnly WordNet
import, not an encoder defect. The optional §6.2 lexical block cuts >0.999 pairs
124,343 → 55 (but degrades top-pair RDM fidelity: 0.81 → 0.56).

## X4 RDM-Spearman re-measure (design cites 0.9718 / 0.9706 at 54 kernel-v0 concepts)

| store | global RDM ρ | top-pairs (cos>0.05) ρ | strong-NN recall@1 | strong-NN recall@10 |
|---|---|---|---|---|
| proj512 | **0.2613** | 0.8093 | 0.410 | 0.517 |
| proj576 | **0.2820** | 0.8201 | 0.423 | 0.518 |
| native512 | 0.0530 | 0.8117 | 0.407 | 0.474 |
| native576 | 0.0458 | 0.8002 | 0.417 | 0.487 |

The 0.97 calibration **does not transfer** to bulk-import stores: the global RDM mass sits in
the near-zero disjoint noise floor, which any D-reduction re-randomises. Fidelity that
matters operationally (structure-bearing pairs, NN identity) degrades with m: top-pair ρ
0.98 → 0.81 and strong-NN recall@1 0.64 → 0.41 from the 1k smoke to 10k — for **native**
re-encoding as much as for JL projection (a D-capacity effect, not a projection artefact).

## Encode cost & storage

| metric | measured @10k | design prediction | verdict |
|---|---|---|---|
| canonical 8192 vectorise (incl. both JLs, 1 core) | 39.3 ms/concept (JL-dominated); native-512 alone 258 µs | §1.2: encoding not the dominant scale cost | **HOLDS** (~10.9 CPU-h at 1M, linear) |
| FFT count | 0 (sign-diagonal binding) | §1.2 2-FFTs/child is construction-B-specific | as designed (§6.3 path) |
| dense store @8192 | 327.68 MB fp32 = 0.655 GB fp64 / 0.164 GB fp16 | §6.4: 0.66 / 0.16 GB | **HOLDS (exact)** |
| exact O(m²) NN cleanup | 117 s @10k, D=512 | §6.5 linear-scan warning | **3.2 h @100k, ~324 CPU-h @1M → exact scan dies between rungs** |

## Which design extrapolations HOLD at 10k / which look SHAKY

**Hold:**
1. §6.5 Gaussian crosstalk √(2ln m/D) — confirmed at D ∈ {512, 576, 8192} for the disjoint class.
2. §6.4 storage arithmetic — exact.
3. §1.2 "ordinary encoding is not the million-scale cost" — 1M vectorisation ≈ 11 CPU-h.
4. §6.3 determinism claims — byte-identical regeneration, cycles need no DAG, zero silent axiom drops (word-level pointers disclosed).

**Shaky for 100k/1M:**
1. **Margin story:** the margin distribution gate (§12) will be dominated by structural-duplicate
   mass, not crosstalk — 20.1% duplicate records at 10k, and the incidence should RISE as
   selection descends into sparser tail synsets. A record-identity/differentia policy
   (drop-or-enrich zero-axiom records; OBO logical definitions; pinned lexical profile) is
   needed BEFORE the 100k vectorise, or the duplicate census will read as a spurious pass/fail.
2. **Host-dimension stores (512/576):** NN identity already mostly lost at 10k and degrading
   with m; the X4 kernel-v0 calibration cannot be inherited by scale claims. E-series-style
   projected arms at 100k+ need re-gating (larger projection D, or adapter arms per §6.6).
3. **Typing coverage:** identity/dependence = 0% from WordNet; hard sortality 12%. The 1M
   "fully resolved CK-UFO" count depends entirely on the OBO/SUMO/gUFO legs — WordNet-only
   scaling of the current rules will NOT approach the §4.3 0.95 hard-precision promotion gate
   (and no human audit sample exists yet at S0).
4. **Selection rule exhaustion:** SemCor tag_cnt pool = 27,210 < 100k. The S1 rung cannot
   reuse this rule; the multi-source §3.1 portfolio (with dedup/crosswalk machinery that does
   not yet exist here) becomes load-bearing one rung earlier than the compute does.

## Concrete blockers for the 100k rung

1. New disclosed selection rule + multi-source ingestion (WordNet ∪ OBO ∪ SUMO) with
   type-level dedup and per-shard license manifests (§3.5 four-count reporting).
2. Structural-duplicate policy decision (record-identity differentia) — pre-registered, since
   it changes every downstream margin number.
3. ANN index + exact-vs-ANN ≥0.99 recall gate implementation (exact scan borderline at 100k,
   infeasible at 1M on box-class hardware).
4. Multi-round §6.3 SCC handling validated on the real OBO 1,142-term SCC (S0 used 1
   synchronous round on a near-acyclic graph — untested at that cycle scale).
5. UFO typing needs source-asserted commitments (OBO/BFO anchors, SUMO types) + the §4.3
   stratified human audit to have any path to the 0.95 hard-typing gate.

ASM candidates: `poc/scale/asm-1780-1789.json` (ASM-1780..1787) for coordinator registration.
