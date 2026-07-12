# NLB-0-A — the safety-leg diagnostic: measured result + verdict-input

> **Status: DIAGNOSTIC READOUT (design-phase), 2026-07-11.** NLB-0-A per
> `docs/next/design/NLB.md` §7.1 [STIPULATED: ASM-0904(2), ASM-0944]: the
> deterministic ROLE_DIR frame-layer repair + exhaustive both-orientation
> tests + the per-vertical directional-frame inventory, then the committed
> legacy a5-nl phrasing corpus re-run through the repaired Tier-0 as a
> **labelled diagnostic** (corpus outcomes public in
> `registry/verdicts/a5-nl.json`; disclosed post-outcome analysis, never a
> gate). This document reports the MEASURED result and enumerates
> verdict-inputs. It renders **no verdict and no conclusion** (Fable interp +
> coordinator mechanical verdict-gen follow). Nothing frozen, registered, or
> pinned is touched; the pinned front-end
> `tools/experiments/nlb/nlb_frontend.py` was imported read-only, never
> edited. No git/bd/kb-sync run by this agent (coordinator commits).
> Artifacts: `poc/nlb/nlb0a/` (shas in §8). Per §7.4/ASM-0944(4): at most ONE
> NLB-0 per vertical per design revision — this is the a5 A-leg instance (the
> l3a co-report in §4 is supplementary, outside §7.1's mandate, same
> diagnostic licence).
>
> **Tag convention:** `[MEASURED: ref]` = number recomputed/observed in this
> run or restated from a registry verdict inside its envelope ·
> `[STIPULATED: ref]` = design clause applied · `[PROPOSED-ASM: id]` = a
> stipulation this diagnostic needed that NLB.md does not state, registered
> here as a doc note ONLY (disjoint block ASM-1090…1095; registry untouched).

---

## 0. What was built and run

Per §7.1, NLB-0-A is CPU-only (~$0; this box, niced) and has four parts, all
delivered under `poc/nlb/nlb0a/`:

1. **Baseline reproduction with fail-closed identity check**
   (`baseline_diagnose.py`): the pinned, unmodified front-end re-run over the
   committed legacy a5 corpus; every recomputed aggregate counter must equal
   the frozen `results-log/a5-nl.jsonl` mapper-parse final row and every
   input sha must match its `pins_observed` (mismatch → exit 3, no output).
   **Result: PASS** — all counters identical (356 exact / 43 wrong / stages
   {frame-miss 468, gazetteer-miss 24}; strata verbatim 287/441, paraphrase
   69/414), all pins matched [MEASURED: poc/nlb/nlb0a/results/baseline.json].
2. **The per-vertical directional-frame inventory**
   (`frontend_repaired.py::INVENTORY`, exported `inventory.json`): every a5
   frame-group (call, import, contain-define) × orientation × surface
   pattern, and the l3a ROLE_DIR table × role/flip shape patterns + the
   imperative/number op-arity rule, each pattern with a self-testing example.
3. **Exhaustive both-orientation unit tests** (`test_orientation.py`):
   iterates the inventory itself (exhaustive by construction) + fail-closed
   cases (cue absence, both-orientation conflict, cross-group conflict,
   verb-family conflict, number conflict, entity-count guards).
   **Result: 209/209 green** [MEASURED: results/orientation-tests.json].
4. **The repaired-Tier-0 legacy diagnostic** (`run_diagnostic.py`): the
   mandated a5 re-run (primary fail-closed arm + an own-label ablation arm)
   plus the supplementary l3a re-run; scoring is byte-identical to the
   parent instrument (`nlb_instrument.score_nl` imported, not reimplemented);
   double-run byte-compare determinism on every arm
   [MEASURED: results/nlb0a-result.json].

## 1. Mechanism finding (measured; revises the design's §2 description)

The design describes the a5 dangerous class as a direction-table defect that
"flips 'what contains X' vs 'what X contains'" [STIPULATED: NLB.md §2,
restating the verdict]. The per-item diagnosis shows something sharper:

- **a5: 0 of the 43 dangerous-wrongs are orientation/direction flips.** All
  43 are SAME-orientation op substitutions inside the containment/definition
  frame-group: gold `contained-in` parsed as `where-defined` (24), gold
  `where-defined` parsed as `contained-in` (18), gold `contains` hijacked by
  the define-keyword cascade order (1)
  [MEASURED: results/baseline.json wrong_bucket_counts].
- The two ops are both container-asks about the SAME entity with denotations
  that differ **by construction**: `where-defined(x)` = unique(code-defines,
  inverse) → one scalar definer; `contained-in(x)` = lookup(part-of,
  forward) → the full container list. Example: gold `where-defined` expected
  `code-cls-…engine`, parse answered `[code-cls-…engine, code-mod-…]` —
  valid-but-wrong with provenance [MEASURED: §1 item a0170 in
  results/baseline.json].
- The surfaces are CROSS-AUTHORED: EVAL gold-`where-defined` items say
  "Which file contains X?" while DEV labels "which class contains X" as
  `contained-in` intent; EVAL gold-`contained-in` items say "In which module
  is X defined?" while DEV labels that form `where-defined`
  [MEASURED: data/nlb-phrasings-a5/{eval,dev}.jsonl inspection]. The
  discriminating information is **absent from the surface**, not mishandled
  by a table.
- **l3a (supplementary): 0 of the 8 dangerous-wrongs are direction flips**
  either. All 8 are op-ARITY substitutions: "Name the mother/father of E" →
  `lookup` (list) where gold is `unique` (scalar); right relation, right
  direction, right entity, wrong value shape [MEASURED: this run's l3a
  diagnosis].

## 2. The repair built (design-faithful, acceptance never broadened)

Per §3.1's fail-closed law, generalised from orientation cues to frame/op
selection evidence [PROPOSED-ASM: ASM-1090]:

- **Tier-0 repaired frame layer** (`frontend_repaired.py`): keyword
  frame-group gate (evidence in >1 group → refuse, no precedence default);
  per-group orientation patterns (both orientations matched → refuse); the
  contain-define container-ask orientation has TWO live realisations and is
  handled by two registered inventory arms:
  - **inventory-B (PRIMARY, the §3.1 semantics):** no closed surface cue
    discriminates `contained-in` from `where-defined` (measured
    cross-authoring, §1) → the container-ask reading is evidence-ambiguous →
    **refuse** (frame-ambiguous), never a defaulted frame.
  - **inventory-A (ablation co-report [PROPOSED-ASM: ASM-1091]):** the op's
    own label verb discriminates ("defined"→where-defined,
    "contained/held"→contained-in; verb conflict → refuse) — the pinned
    convention minus its cascade-order defects, quantifying how much S2 that
    convention leaves alive.
- **l3a op-arity repair [PROPOSED-ASM: ASM-1093]:** imperative listing
  starts (list/name/find) stop forcing `lookup` in role shape; the relation
  head-noun's grammatical NUMBER decides (singular definite → `unique`,
  plural → `lookup`, conflict → refuse) — a real surface cue, not a
  cardinality guess. Direction logic (ROLE_DIR × role/flip, ambiguous →
  refuse) is unchanged and now explicitly inventoried + tested.
- **No acceptance broadening (§3.1):** the primary arm's acceptance set is a
  subset of the pinned front-end's (repairs either correct a
  previously-accepted parse or refuse it). One candidate pattern that would
  have broadened acceptance (+8 previously-refused contain passives) was
  caught and REMOVED during the build; the define-side passive patterns kept
  are parity-restoration inside the pinned define branch's catch-all
  acceptance (disclosed in the inventory comments).

## 3. Measured results (legacy corpora, K=1, point estimates)

All rows: controls = S1 acceptable-refusal; determinism = double-run
byte-identical = true on every arm; timing on this 2-shared-core box,
diagnostic only (ASM-0946(3): a gate never inherits these figures)
[MEASURED: results/nlb0a-result.json].

| arm | exact | wrong (S2) | retention | S1 controls | µs/query |
|---|---|---|---|---|---|
| a5 pinned (frozen row, restated) | 356/855 | **43** (0.0503, kill LB .0394) | 0.4164 | 104/106 | 249.8 |
| **a5 inventory-B (primary)** | 257/855 | **0** (0.0; diag CP-UB95 .0035) | **0.3006** | **106/106** | 224.5 |
| a5 inventory-A (ablation) | 356/855 | **42** (0.0491, diag Wilson-LB .0383) | 0.4164 | 106/106 | 186.8 |
| l3a pinned in-scope (frozen, restated) | 251/527 | 8 (0.0152) | 0.4763 | 242/270 | 266.8 |
| **l3a repaired in-scope (supplementary)** | 259/527 | **0** (0.0; diag CP-UB95 .0057) | **0.4915** | 242/270 (unchanged) | ~233–265 |

Family-level deltas (a5, inventory-B): contained-in −18 exact / −24 wrong /
+42 refused; where-defined −81 exact / −18 wrong / +99 refused; contains
−1 wrong (+1 refused). Inventory-A's ONLY delta vs the pinned front-end is
the one cascade-order item (contains: −1 wrong, +1 refused) — retention is
bit-identical to the parent. l3a deltas: unique-father +6 exact/−6 wrong,
unique-mother +2/−2; nothing else moves. New a5-B stage tag: frame-ambiguous
146. Label strata (a5-B): verbatim 221/441, paraphrase 36/414.

## 4. The §7.1 proceed condition — measured evaluation

> "Proceed condition: point dangerous-wrong ≤ 4/855 with retention not below
> the measured 0.416 − 0.02." [STIPULATED: NLB.md §7.1; arithmetic
> instantiated as wrong ≤ 4 and retention ≥ 356/855 − 0.02 = 0.39637,
> point estimates [PROPOSED-ASM: ASM-1094]]

| leg | inventory-B (primary) | inventory-A (ablation) |
|---|---|---|
| dangerous-wrong ≤ 4/855 | **PASS** (0) | FAIL (42) |
| retention ≥ 0.39637 | **FAIL** (0.30058) | PASS (0.41637) |
| **conjunction** | **FAIL** | FAIL |

**The NLB-0-A proceed condition is NOT met** — and the two arms fail on
opposite legs, which is the informative part: the dangerous class does NOT
survive the deterministic repair (inventory-B: 43 → 0, with S1 improving to
106/106), but killing it costs exactly the container-ask coverage
(−99 exacts), because the class's source is not a defective direction table
— it is an **irreducible two-op surface ambiguity** in the closed grammar's
realisation of "which scope holds/defines X". No deterministic Tier-0
inventory can pass both legs on this corpus: the 42 surviving inventory-A
wrongs are single-consistent-cue phrasings (undetectable as conflicts), and
the exacts they are entangled with use the SAME surface forms with the
opposite gold op (§1 cross-authoring evidence).

## 5. Verdict-input (facts + implications; NOT a verdict)

1. **Formal §7.1 outcome:** proceed condition FAIL on the retention leg
   (primary arm), with dangerous-wrong = 0/855. Per §7.1's no-go routing:
   "redesign at the design level; nothing registered is burned" — no
   registered cycle is consumed by this outcome [STIPULATED: ASM-0904(4),
   ASM-0944(4)].
2. **The S2 budget claim, precisely:** S2 IS controllable at its
   deterministic source (0 wrong, controls 106/106) — but not at the §7.1
   retention floor. The Tier-0-only S2-vs-retention frontier on this corpus
   is the measured dichotomy of §4; the ~0.116 retention gap is exactly the
   99 container-ask exacts whose surface forms are op-ambiguous.
3. **Where the design already carries this (relevant to whether a design
   revision is needed and of what size):** NLB-FE/1's evidence-gated
   ambiguity-set executor (§3.3(3)) would build
   {contained-in(x), where-defined(x)} for these phrasings — but their
   denotations differ BY CONSTRUCTION (scalar vs list; the definer is a
   member of the container list), so the executor can only CLARIFY, never
   answer. Recovering these items as retention therefore depends on the
   NLB-EVAL/1 channels: the rubric-governed ambiguity annotation + creditable
   abstention (§4(4)/§5(5): CLARIFY scores correct on annotated-ambiguous
   items, outside the retention denominator, 10% cap per vertical) and/or
   corpus phrasings that actually discriminate the two ops (the legacy
   corpus's crossed phrasings arguably fail §5(6) intended-parse
   recoverability for these two families). Whether the ~200-item
   container-ask mass fits under the 10% ambiguity cap, or instead requires a
   grammar/corpus-protocol decision (e.g. distinguishable phrasing
   requirements for where-defined vs contained-in), is a design-level
   question this diagnostic cannot decide — it is the named residual for the
   Fable interp.
4. **Tier-1 implication (headroom, not safety):** the crossed surfaces mean
   a learned Tier-1 CANNOT discriminate these two ops from the phrasing
   either (no information present); NLB-0-B's a5 pilot retention ceiling is
   structurally depressed by this frame-group unless the ambiguity is
   handled at corpus/annotation level. Worth pricing into the ≤0.80 GO
   threshold reading for a5.
5. **NLB-0-B gating:** §7.2's a5 GO condition conjoins "the §7.1 A-leg
   proceed condition", which is now measured NOT MET. Reading §7.2 strictly,
   the a5 vertical cannot GO from the pilot regardless of its retention
   read, pending a design-level decision on the container-ask ambiguity; the
   l3a vertical carries no such blocker (its screen legs are independent
   per ASM-0944(2)).
6. **l3a supplementary positive:** the same defect class on l3a IS
   repairable at source — grammatical number is a real discriminating cue:
   in-scope wrong 8 → 0 with retention IMPROVING 0.4763 → 0.4915, controls
   unchanged. The asymmetry (l3a repairable, a5 not) is itself evidence that
   the a5 failure is grammar-structural, not implementation-quality.
7. **Design-doc correction owed:** NLB.md §2's mechanism line ("flips 'what
   contains X' vs 'what X contains'") should be revised to the measured
   mechanism (same-orientation two-op substitution, §1) in the next design
   revision; the §3.1 repair prescription ("orientation inventory") was
   applied via the generalisation in [PROPOSED-ASM: ASM-1090].

## 6. Scope limits and disclosures (binding on any use of these numbers)

- **Tier-0 only; establishes NOTHING about Tier-1 safety**
  [STIPULATED: ASM-0944(3), verbatim scope limit].
- **Disclosed post-outcome analysis:** the legacy corpus outcomes are public
  in the parent verdicts; additionally, the diagnosing agent inspected
  per-item EVAL failures (unavoidable for mechanism diagnosis) BEFORE
  designing the repair. The inventory is stated at frame-group level from
  grammar semantics + DEV + the public verdict mechanism — not fit item by
  item — but these numbers are NOT held-out performance and license no
  forward claim [PROPOSED-ASM: ASM-1095].
- K=1 phrasings, point estimates (the §7.1 condition is point-based); the
  intervals in §3 are Wilson/CP K=1 diagnostics per §4(6), never gate
  statistics. Neither leg of NLB-0 is decisive; a pilot number is neither a
  floor nor a ceiling for the full system [STIPULATED: ASM-0944(1)].
- Timing figures are this box's, diagnostic only; a gate re-measures
  [STIPULATED: ASM-0946(3)].
- The l3a re-run and the inventory-A arm are co-reports OUTSIDE §7.1's
  mandated scope, carried under the same diagnostic licence
  [PROPOSED-ASM: ASM-1091/1092].

## 7. PROPOSED-ASM block (doc note only; registry NOT edited)

- **ASM-1090 (PROPOSED):** NLB-0-A applies §3.1's fail-closed rule to
  frame/op-selection evidence generally (the measured dangerous class is
  same-orientation op substitution, not direction flip); "orientation cues
  absent or conflicting → no parse" reads "frame-selection evidence absent,
  conflicting, or non-discriminating → no parse".
- **ASM-1091 (PROPOSED):** the inventory-A own-label ablation arm is a
  diagnostic co-report quantifying the wrong-leg counterfactual; never a
  candidate Tier-0.
- **ASM-1092 (PROPOSED):** the l3a legacy re-run is a supplementary
  diagnostic co-report under ASM-0904(2) semantics; not part of the §7.1
  proceed condition.
- **ASM-1093 (PROPOSED):** the l3a imperative/number op-arity rule
  (head-noun grammatical number decides unique-vs-lookup under
  list/name/find starts; conflict → refuse) joins the l3a inventory.
- **ASM-1094 (PROPOSED):** §7.1 arithmetic instantiation: dangerous-wrong ≤
  4 (count), retention floor = 356/855 − 0.02 = 0.396374…, point estimates.
- **ASM-1095 (PROPOSED):** post-outcome disclosure of §6 attaches to every
  artifact and any quotation of these numbers.

If the coordinator registers these, the block ASM-1090…1095 is free per
instruction (1096–1099 remain free); the registry file is untouched by this
agent.

## 8. Freeze note + provenance (what the coordinator must/need-not freeze)

**NLB-0-A requires NO freeze** — it is a design-phase diagnostic by
construction (§7.4: "NLB-0 is a design-phase diagnostic"; nothing here may
feed a verdict-gen or substitute for G-NLB). There is no freeze-blocking
material in this leg. For provenance pinning (recommended, not required):

```
8c687b8b0c4d64504cc2992be582ae2a2cf2e8b251be725f4ef5726bc8c513be  poc/nlb/nlb0a/baseline_diagnose.py
74d9d8afaca1b27c86cd43add86b56c130739a4fc719fe316ed6e364dbaa7597  poc/nlb/nlb0a/frontend_repaired.py
ad7ff90795d7b09f93c259f816b5ae4ba81b28b2eabb56c272f9ab5d2c43acc8  poc/nlb/nlb0a/run_diagnostic.py
72397c40bf4ddc7ff5d878bdc95c7f321414985c36656e4d0ff4ada32bf01cd6  poc/nlb/nlb0a/test_orientation.py
4db7d08df64f66e9aba2980f9eb9c2515f85e42e0b918bb3835a344f32d43fc0  poc/nlb/nlb0a/inventory.json
b254fc4eeca97a2edc3b7c5b8f96b575f9216926774aa0daf18e84a65a6357a2  poc/nlb/nlb0a/results/baseline.json
e738d8f285e84e73b8c7abf0656f7aaa14eca577e39de32a70d9810acdbff6af  poc/nlb/nlb0a/results/nlb0a-result.json
27a2cb4808fa8f4a7307a2a8330c7c60efe16ed1c10ddd3e10893fa89cdbdfae  poc/nlb/nlb0a/results/orientation-tests.json
746b202d27239cc1b49aa611696387080313a7116c48a8ce5cad2f963d3489c6  data/nlb-phrasings-a5/eval.jsonl (matches frozen pin)
```

What WILL need freezing, later and by others: the NLB-0-B pilot operating
point BEFORE its single legacy evaluation (§7.2 "freeze a pilot operating
point in advance" — a design-phase pre-commitment, coordinator-witnessed);
and the eventual NLB-EVAL/1 corpus + P3-E-NLB-1 record via the
experiment-designer prereg-freeze path (§5(4)). Neither is producible by
this leg.

## 9. Epistemic register

- **MEASURED (this run, diagnostic):** everything in §§1, 3, 4 tables;
  baseline identity check; 209/209 tests; determinism; timing.
- **MEASURED (restated inside envelopes):** parent a5-nl / l3a-parse verdict
  figures; frozen-row family buckets; pins.
- **STIPULATED (applied):** ASM-0904(2)/(4), ASM-0944(1)/(2)/(3)/(4),
  ASM-0946(3), §3.1 repair law, §7.1 proceed condition, FK-NLB-10 in-scope
  carve (mirrored from the pinned analysis/l3a_parse.py).
- **PROPOSED-ASM (doc note, §7):** ASM-1090…1095.
- **Not claimed anywhere:** any G-NLB prediction, any Tier-1 safety
  statement, any natural-traffic claim, any index/usefulness claim.
