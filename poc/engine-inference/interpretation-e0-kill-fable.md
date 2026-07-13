# E0 KILL-e1 — Fable steering interpretation + E2 design recommendation

Author: Fable interpretation agent, 2026-07-13. Inputs: commit cdc2f305
(ASM-2135..2144), `holdout/holdout-manifest.json`, `holdout/exclusions-h.json`,
`results/rows.jsonl` + `run-result.json` (seen frame, exploratory-forever per
ASM-2104/2108), `data/axioms-engineinf-v0/kernel/*`, design
`docs/next/design/engine-inference-under-typing.md` [R1–R3].

**Epistemic status: STEERING INTERPRETATION, not a verdict.** No frozen E0 run
exists; nothing here is campaign evidence. Every seen-frame number below is
quarantined exploratory-forever [STIPULATED — ASM-2104]. This document decides
the pre-registered ASM-2105 consequence (E2, a designer decision) and will be
reconciled with a GPT-5.6 read.

---

## 1. What the kill means for the correctness thesis

**The kill is an adequacy stop, not an answer.** KILL-e1 fired because the
binding frame `(G1∪G3)_H*` spans only operator O1 (91 items, 17 cells, 4
lemmas — items/cells/lemmas all comfortably PASS) while O2 (typed
disjointness) is empty: the 3 H2 anomaly items all fall in seen cells
[MEASURED — ASM-2140]. The instrument itself is sound (PC-1..7 PASS,
custody clean, no H outcome ever computed) [MEASURED — ASM-2143]. So the
confirmatory question was never *asked*; it was not answered against the
kernel.

**Is E0 a sixth content-not-structure result? No — and that matters.** The
four prior deflations (f2b-transfer H-STRUCT, DECONF-B, CASC-0′, rules-2
knull) all had the same shape: the kernel-source and control-source arms
derived *identical* (in knull, byte-identical) artifacts, so structure could
not have shown even in principle [MEASURED verdicts — programme ledger,
asm-engineinf-1950-1969.json ASM-1950 rationale]. E0 was built precisely so
the arms *cannot* coincide, and on the seen frame they demonstrably do not:
K vs K-lemma-dom diverges on 176 decisions, K vs B-wn on 189 [MEASURED —
run-result.json]. On the covered divergent cells the structure side then
*wins*: EP-A dom +1.00 (6 win-cells / 0 loss), EP-A union +1.00 (5/0), EP-B
+0.714 (6/1) [MEASURED — ASM-2144, exploratory-forever]. E0 is therefore
**not** a content-not-structure datum; it is the programme's first
structure-*sensitive* instrument, showing a structure-*consistent* exploratory
signal, stopped before it could ask confirmatorily. The honest sentence is
"could not ask", which is categorically different from the previous five
"asked; answer was content".

**Two honesty caps on that exploratory signal.** (a) It is
confirmatory-untestable at this scale: the unseen holdout cannot populate O2
(mechanism in §2), so the two-operator question has no confirmable venue at
this inventory. (b) It is break-only: DIST-SPAN fails on all three endpoints
— every net win-cell is a break cell [MEASURED — ASM-2144]. And a third,
subtler cap: recomputing the seen frame per cell shows the EP-A-union and
EP-B win-cells are mostly *constructed-anomaly* cells (5/5 and 5/6
respectively; EP-A-dom is balanced, 3 attested + 3 anomaly) [MEASURED —
derived in this session from pinned `results/rows.jsonl`]. The anomaly gold
comes from the same G3 side-rule family whose unanimity base just collapsed
on real corpus objects — so part of K's exploratory win-surface rests on
gold whose ecological validity the kill itself calls into question
[DERIVED]. The 3 attested break win-cells (real gloss usage, no constructed
rule: K types `material` where the dom-collapse forces `happening` and wrongly
flags real sentences anomalous) are the strongest cells in the record
[MEASURED — rows.jsonl per-cell census]. C-SHUF sits exactly at the 0.05
boundary (rank 1, 48/960 with ties counted ≥) — partly a granularity
artifact: only 80 distinct TBoxes among 960 members because break has three
identical `material` senses and make's swap is idle, so the orbit is coarse
at this inventory [MEASURED counts — ASM-2137/2144; the granularity reading
is DERIVED].

**Net for the thesis:** formally unchanged — still no confirmatory
kernel-specific-value datum, four content-not-structure results stand. But
materially the picture improved: there is now a validated $0 deterministic
instrument, a real (exploratory, capped) structure-side signal on its covered
surface, and a kill whose mechanism is *diagnostic* — it names exactly what
the construction and the inventory lack.

## 2. Small-kernel artifact vs real limit

The kill and the DIST-SPAN failure have **four stacked causes**; three are
inventory-size artifacts, one is a structural rule defect that scale makes
*worse*, plus one genuine expressiveness residue.

**(i) Anomaly-cell exhaustion — pure artifact.** The cell key is
(synset, side, class∈{wn-somebody, wn-something}, kind) [MEASURED —
engineinf_wn.cell_key], so 13 minted synsets admit only a handful of anomaly
cells, and the seen frames already realize 9 of them [MEASURED — recomputed
from items.json]. Novel anomaly cells were nearly impossible at this
inventory *regardless* of the H2 rule. Vanishes mechanically with more
minted synsets [DERIVED].

**(ii) Typing-differentiation concentrated in ONE lemma — artifact, and it
makes the DIST-SPAN failure near-inevitable a priori.** The kernel module
bytes: break has 3 distinct range profiles across 5 senses
(happening/material/words); find has 2 (info/material); friend's senses
differ only by one domain constraint; make's two senses carry **zero**
typing constraints — their split is tautologically idle for EP-A and K
*cannot* detect a make anomaly (K loses all 4 make anomaly cells, its only
seen-frame losses) [MEASURED — data/axioms-engineinf-v0/kernel/*.json +
rows.jsonl per-cell census]. Friend contributes zero G1∪G3 cells and find
exactly one (concordant) [MEASURED — same census]. So the win-surface was
confined to break *by construction*: an instrument with one differentiated
lemma cannot pass a ≥2-lemma distribution gate. The break-only result is an
instrument-design fact, not a measured kernel-quality ceiling. Find has the
teeth (differentiated profiles) but lacked cells; with 28 novel-cell
attested find items already sitting in the holdout, a richer frame plausibly
puts find in play [MEASURED counts; the distribution expectation is
EXTRAPOLATION].

**(iii) H2 side-unanimity — a structural defect that does NOT scale.** The
rule demands every attested object (seen gloss ∪ H1) of a synset fall on one
side of the WN abst/phys top split; real SemCor objects break this for 11/13
minted synsets [MEASURED — ASM-2140, exclusions-h.json]. Unanimity is a
conjunction over attestations, so survival probability *decays* with
attestation count — precisely the high-frequency synsets that supply H1
items are the ones that go mixed [DERIVED]. A larger kernel under the same
rule would populate O2 only via rare synsets that stay unanimous by paucity
(thin, noisy gold) [EXTRAPOLATION]. Conclusion: the unanimity rule must be
amended; scaling alone will not populate O2 honestly. Note this is a defect
of the *gold construction*, not of the kernel: real verb senses take objects
on both sides of the WN top split (coercion, metaphor, light-verb uses, plus
SemCor tag noise), so the split is too coarse an anomaly axis [DERIVED].

**(iv) Sortal-expressiveness residue — the one real limit to keep named.**
Some high-frequency verbs (make, and plausibly get/do/have) have senses that
do not differ *sortally*; domain/range typing cannot split them, and no
inventory size fixes that. A kernel-value claim covering such lemmas needs
richer structure (event/causal rules) than this instrument measures
[DERIVED from the make constraint bytes; scope claim is EXTRAPOLATION].

**Verdict on the maintainer's barrier thesis:** substantially supported —
(i), (ii) and the frame starvation are exactly small-kernel artifacts, and a
larger inventory of *sortally differentiated* lemmas plausibly distributes
the advantage past break [EXTRAPOLATION, mechanistically grounded in find's
measured profiles]. But O2 population additionally requires the H2 amendment
in (iii) — scale alone is predicted to fail there. The scale track (207,733
typed clusters, 99.99% BFO-anchored [MEASURED — commit 4296e98e]) supplies
the class vocabulary and typing skeleton for EP-A at the 10k+ rung, but EP-B
is defined by kernel-*authored* (explication-cited) content — mechanically
minting senses from the scale track would quietly change EP-B's meaning.
Keep EP-A scalable, keep EP-B on the authored rung [STIPULATED — design
recommendation].

## 3. The E2 decision (pre-registered ASM-2105 consequence)

**Ranked recommendation: E2b+E2a as one staged package; E2c as bookkeeping
regardless; reject E2a-alone freeze and E2c-alone.**

**1. (recommended) E2b WITH E2a folded in — construction amendment +
inventory extension.**
- E2a component: replace the H2 attestation-side-unanimity base with the
  **VerbNet selectional-restriction pin the design already names as the E1
  gold upgrade** (§1 G3 row: third-party published per-class restrictions,
  e.g. break-45.1 Patient [+concrete], plus the ~30-item human spot-audit —
  GPT-5.6 annotator-proxy per the standing #11 arrangement, reconciled
  later) [STIPULATED]. Honesty: outcome-free (no H outcome was ever
  computed, so no gold is being tuned to results), third-party bytes that
  predate the programme, and *pre-named in the registered design* rather
  than invented post-kill; it also strengthens the gold under the cells K
  already wins, cutting both ways. Anomaly-gold construction is a
  maintainer-owned call (design §maintainer-gates) — surface as a decision
  issue [STIPULATED].
- E2b component: extend the kernel by **6–10 SemCor-frequent lemmas chosen
  for sortally differentiated senses** (selection by a $0 mechanical census:
  SemCor tag_cnt × sense count × distinct candidate range classes), authored
  to the scholarly-explication bar, review-gated; re-extract the holdout
  (new lemmas dominate novel cells), re-pilot, freeze. Build note: the PC-6
  decoys draw/hold/cut are pre-verified extraction-compatible and are
  natural candidates, but promoting any burns the decoy bank — mint a
  replacement bank first [STIPULATED].
- Cost: $0 GPU/model-compute throughout; roughly a week of agent time
  (authoring dominates), extraction/pilot/freeze runs are minutes
  [ASSESSMENT].

**Cheapest decisive next step (start immediately, inside the package):**
the **E2a recount on the CURRENT inventory** — pin VerbNet, amend
`extract_holdout.py`'s H2 base, re-extract, read KILL-e1 again. $0 compute,
~1–2 agent-days, custody-clean (extractor never touches engine/scorer). It
is decisive for §2's artifact-vs-limit split: if VerbNet-gold cross-pairs
still cannot mint novel O2 cells at 13 synsets, cell exhaustion (i) is
*measured*, not argued, and the inventory extension becomes the registered
necessity [STIPULATED].

**2. (rejected as a standalone) E2a-alone, then freeze.** Even if the
recount clears KILL-e1, freezing at one differentiated lemma sends the run
into a DIST-SPAN gate it structurally cannot pass (§2-ii) — a predictable
scope-limited FAIL-A that would also *burn the holdout's novel cells
forever* (once scored, seen). Running an experiment whose distribution gate
is unpassable by construction is not evidence-gathering [DERIVED].

**3. (do regardless, insufficient alone) E2c — exploratory-only fold-in.**
Log the capped break-only exploratory read into the synthesis as
non-binding now (hours, $0). Alone it abandons a validated instrument at
the moment its blocker became cheap to fix, and leaves the correctness
thesis carrying an unpaid confirmatory IOU [DERIVED].

## 4. Steer (coordinator + maintainer)

E0's kill leaves the correctness thesis formally where it was — no
confirmatory kernel-specific datum; four content-not-structure results stand
— but materially better off than before the build: the programme now owns a
validated, $0, deterministic, structure-*sensitive* instrument; its
exploratory surface shows the first structure-side signal in programme
history (sense-split beats the kernel's own lemma-collapse +1.00 cell-wise
on covered cells, with the strongest cells on *attested* gold), and the kill
mechanism is diagnostic rather than fatal — it localises the block to an
anomaly-gold rule that provably fails on real corpus objects and an
inventory holding exactly one typing-differentiated lemma. The single
highest-value next move is the staged E2 package: start the $0 VerbNet H2
recount on the current inventory now (1–2 agent-days, decisive on whether
O2 is rule-limited or inventory-limited), and in parallel author the 6–10
sortally-differentiated-lemma extension — which converts the maintainer's
small-kernel-barrier thesis from an argument into a cheap, falsifiable
prediction: *the advantage distributes past break exactly when the
inventory contains more than one lemma capable of expressing it.*

---
Changed files (no git actions taken by this agent):
`poc/engine-inference/interpretation-e0-kill-fable.md` (new, this document).
