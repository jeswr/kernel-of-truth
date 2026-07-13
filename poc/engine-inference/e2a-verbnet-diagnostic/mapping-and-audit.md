# E2a VerbNet diagnostic — mapping, counts, and honesty audit

**Role: Fable diagnostic agent (analyst-7), 2026-07-13. A PURE DIAGNOSTIC
for maintainer decision #29 — it MEASURES whether the O2
(typed-disjointness) starvation that fired KILL-e1 on the E0 confirmatory
holdout (ASM-2140) is RULE-limited or INVENTORY-limited, using VerbNet 3.3
selectional restrictions as the alternative anomaly construct. It adopts
NOTHING (the admissibility of VerbNet-based O2 gold is the maintainer's
construct decision), freezes nothing, authors no lemma, touches no frozen
design doc, runs no engine, and states no feasibility conclusion.**
Assumption block: `asm-e2a-2170-2179.json` (ids ASM-2170..2178, owner
analyst-7). Epistemic tags as in the ENGINE-INF design.

**Custody [STIPULATED — ASM-2170].** Outcome-blind and $0: the diagnostic
script (`e2a_verbnet_diagnostic.py`) imports only `engineinf_wn` (never the
engine or scorer; asserted mechanically at exit, the extract_holdout.py
discipline), and consumes only item INVENTORIES — `holdout/items-h.json`
(pinned pre-freeze, carries no outcome), `results/items.json` (the closed
exploratory seen frame), and the holdout manifest's counts for cross-check.
It never opens `gold-h.json`, `rows.jsonl`, `orbit-rows.jsonl`,
`run-result.json`, or any decision artifact. Every number below is an
outcome-free census of pinned items and ASM-2106 cell keys — the exact
arithmetic KILL-e1 itself uses. Determinism: double-run byte-identical
(`e2a-result.json` sha `8ebb6156…`, `vn-mapping.json` sha `5aab2fe7…`).

---

## 1. The pinned source

VerbNet 3.3, pinned [MEASURED]: `verbnet/verbnet-vn3.3.zip`, sha256
`f11c901c21494a319e3bfaa56fab89f4e855d348629275293decce2ea2fd8ef7`
(cu-clear/verbnet tag `vn-3.3`, commit `90f85a63…`; manifest in
`verbnet/manifest.json`). The canonical subset is `verbnet3.3/*.xml` (329
class files); the zipball's `verbnet-test/` and `vn-gl/` variants are not
consumed [STIPULATED].

## 2. The predefined mapping (all rules fixed before any count)

The mapping was authored from the VerbNet DTD and class structure and from
the pinned WN 3.1 bytes, then computed mechanically; no rule consults any
item outcome, and the one place a rule choice could move the result is
audited in §5.

- **M1 — sense mapping [STIPULATED — ASM-2172].** A minted kernel-v1
  synset is VerbNet-covered iff some canonical class (or subclass) has a
  MEMBER whose `name` equals the Stage-A lemma and whose `wn` attribute
  contains a sense key that maps, via the pinned WN 3.1 `index.sense`
  (key + `::`), to that synset. `?`-prefixed keys (VerbNet's own
  uncertainty mark) are excluded and logged; empty `wn` attributes are
  logged. Sense keys are treated as stable across WN 3.0/3.1 — the same
  version-stability assumption the SemCor holdout already relies on
  (ASM-2139). VerbNet covers verbs only; `friend` (noun) is structurally
  out of scope, logged `vn-verbs-only`.
- **M2 — undergoer role [STIPULATED — ASM-2173].** The instrument's worlds
  are `rel(anchor, R, undergoer)`; the VerbNet role that corresponds to
  the undergoer is the role of the SECOND NP in the frame(s) whose
  DESCRIPTION `primary` is exactly `NP V NP` (the basic transitive),
  taken from the nearest node on the member's root-to-subclass chain that
  has such a frame. THEMROLES are resolved along the chain with the
  deepest definition winning (standard VerbNet subclass inheritance).
- **M3 — restriction → side [STIPULATED — ASM-2174].** Selectional
  restrictions are projected onto the experiment's G2 top-split vocabulary
  by the authored table `selrestr-side-table.json`, which covers the FULL
  28-type census of restrictions occurring in any canonical THEMROLE (the
  script asserts table = census, fail closed, so no type can be
  cherry-picked). Negative (`-`) restrictions never entail a side (the WN
  top split is not two-valued). `or`-joined restrictions entail a side iff
  every disjunct entails that same side; `and`-joined iff exactly one side
  appears among conjuncts.
- **M4 — required side per synset [STIPULATED — ASM-2173].** Defined iff
  at least one matched class entails a side on the undergoer and all
  side-entailing matched classes agree; multi-class conflicts yield none
  (logged).

**Mapping result on the current inventory [MEASURED — ASM-2175]**
(full detail: `vn-mapping.json`):

| minted sense (synset) | VN class | undergoer role | restriction | required side |
|---|---|---|---|---|
| break.shatter (v-00335806) | break-45.1 | Patient | `+solid` | **phys** |
| break.shatter-become (v-00334996) | break-45.1 | Patient | `+solid` | **phys** |
| find.discover (v-00723361) | discover-84 | Theme | (none) | — |
| find.locate (v-02290474) | discover-84 ∧ get-13.5.1 | Theme | (none) | — |
| make.create (v-01624592, v-01658171) | build-26.1(-1) | Product | (none) | — |
| break.violate, break.interrupt ×2, break.malfunction, make.cause ×2, make.create v-01657416 | — | — | no VN member sense key | — |
| friend.person (n-10132360) | — | — | VerbNet is verbs-only | — |

Coverage: 6 of 13 minted verb synsets carry a VerbNet member sense key; 0
sense keys were unmappable; only ONE undergoer restriction exists anywhere
on the covered set (break-45.1 `Patient [+solid]` → phys). In particular
break.violate — the design's own money contrast ("break a promise") — is
not a VerbNet member sense at all, and the make/find undergoers VerbNet
does cover are unrestricted.

## 3. The counts (all outcome-free censuses)

Anomaly construction mirrors the pinned H2 shape: cross-pairs from H1
objects, `(synset, noun)` seen-pair decontamination, novelty = the
ASM-2106 cell key absent from every seen item. Donor pools: PRIMARY = H1
objects of other minted senses of the same lemma (the pinned H2 cross-pair
shape); SECONDARY = H1 objects of any Stage-A minted synset. HARD
eligibility additionally requires that no attested object (seen ∪ H1 — the
H2 unanimity base) lies on the violating side; DEFEASIBLE drops that
requirement (attested violations are logged and are never themselves
anomalies). [STIPULATED — ASM-2176 mechanics; MEASURED results:]

| construct | eligible synsets | items | cells | **novel (H\*) cells** | lemma span of cells | KILL-e1 would fire |
|---|---|---|---|---|---|---|
| H2 hard unanimity (pinned) | 2 of 13 unanimous | 3 | 2 | **0** | make | **yes** (ops {O1}) |
| VerbNet HARD | **0** of 2 (both refuted by attested usage: fire; contract, first, stress) | 0 | 0 | **0** | — | **yes** (ops {O1}) |
| VerbNet DEFEASIBLE | 2 (break.shatter, break.shatter-become) | 18 primary / 114 secondary | 2 | **0** (both pools) | break only | **yes** (ops {O1}) |

The two VerbNet-licensable cells —
`(v-00334996, abst, wn-something, anomaly)` and
`(v-00335806, abst, wn-something, anomaly)` — are both ALREADY-SEEN cells:
the exploratory frame's own G3 rule constructed them on 2026-07-12, so
under determinism their outcomes are inferable and they can never enter
the binding confirmatory frame (design §2.5 H\*, §4 item 7). The
defeasible amendment therefore restores anomaly ITEMS (18–114) but zero
BINDING cells.

**A structural bound, not an accident [DERIVED — ASM-2177].** An
abst-side noun can never be `wn-somebody`: PERSON lies below
PHYSICAL_ENTITY in the pinned hypernym closure, so person-hood forces the
phys side. A phys-entailing restriction (the only kind VerbNet provides
here) therefore admits exactly ONE anomaly cell per synset —
`(synset, abst, wn-something, anomaly)` — and both such cells for the two
covered synsets are seen. No donor pool, however large, changes this: the
defeasible VerbNet construct is cell-space-exhausted on the current
inventory before it starts.

**Construct-agnostic headroom [DERIVED, NOT GOLD — ASM-2177].** If one
ignores VerbNet and asks what ANY single-side selectional-restriction
construct could reach from the H1 donor pool: 30 novel anomaly cells
spanning break/find/make (e.g. an abst-entailing restriction on
find.discover — which K's own `range C_info` axiom asserts — would license
2 novel phys-violating cells). But no third-party source in hand licenses
those restrictions; VerbNet, the named E1 upgrade source, licenses only
the 2 seen break cells. The headroom is real and the authority for it is
absent — that distinction is the actionable content for #29 and for E2b
lemma selection (choose extension lemmas where VerbNet DOES restrict the
undergoer).

## 4. The rule-vs-inventory verdict (measurement, not feasibility)

- **The rule-limitation is confirmed.** Every HARD construct dies on real
  corpus objects: H2 unanimity survives on 2/13 synsets (ASM-2140's
  11/13 mechanism, reproduced here from inventory bytes alone), and
  VerbNet-HARD survives on 0/2 — attested SemCor usage ("the fire broke
  out", "the contract was broken") refutes hard `[+solid]` exactly as it
  refuted unanimity. Hard-form anomaly gold anti-scales with attestation,
  as the steering synthesis predicted.
- **But the repair-in-place fails at the binding margin.** The defeasible
  VerbNet amendment — the strongest repair the named third-party source
  supports — yields **0 novel O2 cells** (2 cells, both seen, single
  lemma). The KILL-e1 re-count under every variant leaves
  `ops_spanned = {O1}` and the kill would fire again unchanged.
- **Verdict: INVENTORY-LIMITED at the binding margin, with a real but
  insufficient rule-limited component.** Amending the construct alone
  cannot repair E0 in place on the current 4-lemma inventory; populating
  O2 in the confirmatory frame requires inventory extension (the E2b
  6–10 sortally-differentiated-lemma path), ideally selected where VerbNet
  carries genuine undergoer restrictions so the amended construct and the
  extension land together. Whether the defeasible VerbNet construct is
  ADMISSIBLE as O2 gold for that extension remains the maintainer's
  decision (#29); nothing here adopts it. **No feasibility conclusion on
  CORRECTNESS or EFFICIENCY is stated or implied.**

## 5. Honesty audit — how this mapping could game the gold, and why it does not decide #29

1. **The side projection is lossy, in the conservative direction.**
   `[+solid]` is strictly narrower than phys ("water" is phys but not
   solid); projecting onto the G2 side vocabulary can only UNDER-count
   VerbNet-licensable anomalies, never mint ones VerbNet would not
   license. The under-count is also forced: the instrument's worlds state
   side classes, so finer-than-side anomaly gold could not be exercised
   without new bridge classes — itself part of the inventory limit.
2. **The one tunable joint is the undergoer-role rule (M2), and abusing
   it changes nothing.** The most tempting abuse — reading build-26.1's
   `Material [+concrete]` (the object NP of the `NP V NP.material
   PP.product` frame) as make's undergoer — would manufacture a phys
   entailment for make.create; its violating cells
   (v-01624592/v-01658171, abst, wn-something) are ALSO already-seen
   anomaly cells. The 0-novel-cells conclusion is invariant under the
   abuse [DERIVED from the seen-cell list].
3. **Gold-set disjointness at the holdout margin.** VerbNet-defeasible
   does NOT license the pinned H2 holdout anomalies (all three are make
   items; Product is unrestricted): adopting VerbNet would REPLACE the O2
   gold, not refine it. GPT-5.6's caution that a VerbNet recount is "not
   automatically decisive gold" is therefore correct in both directions —
   the two constructs disagree on what an anomaly IS, and only a
   maintainer construct decision (plus, if adopted, the E1-named ~30-item
   human spot-audit) can arbitrate.
4. **Defeasible gold is intrinsically weaker.** A violated default is
   only presumptively anomalous; some unattested violating pairs are
   acceptable usage the corpus has not yet shown (exactly the pattern the
   attested violations demonstrate). A defeasible O2 PASS would need that
   weakness disclosed in every claim sentence, as G3's constructed-rule
   status already is.
5. **Shared-descent residual.** The side table's anchors and G2's gold
   both descend from the WN top split (the design's own §4.3 disclosure);
   VerbNet's restrictions are independently authored, but their
   projection here is not independent of G2's vocabulary.
6. **Sense-bridge assumption.** VerbNet's WN 3.0-era sense keys are
   mapped by the pinned WN 3.1 `index.sense`; measured fallout on this
   inventory: zero unmappable keys, so the assumption is unexercised
   here, but it is an assumption.
7. **What was NOT measured.** No engine verdicts, no arm behaviour, no
   holdout outcome — so nothing here says K would score well or badly on
   VerbNet-constructed cells; that is precisely what a post-decision,
   post-extension registered run would measure.

## Self-check gate (governance)

Choices are STIPULATED, results MEASURED, implications DERIVED; the one
ASSESSMENT-grade sentence (E2b lemma-selection steer) is labelled inside
ASM-2178. No frozen/locked doc is edited; no git action is taken in this
pass (coordinator custody); the ASM block awaits central registration with
the commit. This document states no feasibility conclusion and licenses no
sentence about kernel value.
