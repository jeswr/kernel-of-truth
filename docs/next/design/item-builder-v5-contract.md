# item-builder v5 — multi-segment natural-gloss item construction CONTRACT (claim selection, polarity, distractors, pairing, leak lints)

> **Status: [EXP-DESIGN] design-only deliverable of epic
> `kernel-of-truth-0f0y`, child `kernel-of-truth-0f0y.2` ("THE LONG POLE").
> Author: Fable, experiment-designer role (kern/fable-designer), 2026-07-16.
> NOTHING here is built, run, frozen, or committed: no builder script exists,
> no item is rendered, no GPU or LLM call is made, no frozen record (knull,
> knull-v2, gsx0, f1k*) is modified. The coordinator reviews and commits.**
>
> **Companion artifact (this deliverable):**
> `docs/next/design/item-builder-v5-leak-lint-spec.md` — the fail-closed
> leak-lint contract (codes V5-L*), implementable verbatim inside the builder.
>
> **Upstream contract (binding input):**
> `docs/next/design/plain-v5-natural-store-contract.md` +
> `docs/next/design/plain-v5-register-lint-spec.md` (epic child 0f0y.1;
> ASM-2410–2419). This document is the deliverable those flagged at §5.1 /
> ASM-2418: no consuming experiment can freeze before it lands.
>
> **Assumption entries:** ASM-2440–ASM-2449 appended to
> `registry/assumptions.jsonl` in the working tree with this deliverable;
> commit custody stays with the coordinator. Block choice: highest id in the
> REGISTRY before this deliverable is ASM-2419, but the concurrent
> working-tree deliverable `docs/next/design/gpt56-draft-pipeline-large-kernel.md`
> already claims the id block 2420–2439 (not yet registered); this
> deliverable therefore takes the 2440–2449 block, verified unreferenced
> anywhere in docs/, registry/, poc/, data/ (grep, 2026-07-16).
>
> **Tag convention (house discipline):** `[MEASURED: ref]` = a programme
> artifact restated strictly inside its envelope; `[STIPULATED: ASM-id]` = a
> design choice registered in the assumption register. Every design CHOICE in
> this document is STIPULATED, never MEASURED.

---

## 1. What breaks, and why nothing from gsx0 G-2 is ported

The gsx0 injection builder (`data/d-qa-t-plain/build.py`, RULING G-2) rested
on a MEASURED property of the padded store: **exactly one unique admissible
(≥15-char) segment per concept** (cyclic self-padding dedupes away). Every
downstream rule was a child of that scarcity:

- the FIRST claim-true skeleton of a concept took "the" store segment;
- a SECOND claim-true skeleton of the same concept was **forcibly flipped**
  to claim-false (seeded donor) — 13 items at build time
  [MEASURED: `data/d-qa-t-plain/leak-check.json`
  RULING-G2-claim-polarity-substitutions, count 13];
- the answer key therefore diverged from the kernel skeleton on exactly
  those 13 items (yes/no 43/101 vs the kernel's 56/88), and **item-level
  pairing to the kernel corpus was disclaimed** (gsx0 design §3, RULING G-2).

The plain-v5-natural store makes the premise structurally false:

- **PV5-4** requires ≥ 2 admissible segments per entry and **PV5-11(a)**
  requires them pairwise distinct after normalization
  [STIPULATED: ASM-2414]; at the reinstated band, 3–5 admissible segments
  are typical (store contract §5.1). The canonical glosses the band mirrors
  carry 2–6 admissible segments (median 3) under the identical `segments()`
  rule [MEASURED this session: `re.split(r"[.;]")`, ≥15 chars, no
  double-quote, dedup, over the pinned kernel-v0/molecules-v0 records].
- The frozen skeleton corpus carries at most **2 claim-true skeletons per
  concept** (13 concepts carry 2; 30 carry 1; the remaining 65 carry 0)
  [MEASURED this session: `data/d-qa-t/items/covered.jsonl`, counts
  def-match 108 / term-match 108 / claim-true 56 / claim-false 88].

So multi-segment supply ≥ 2 covers the worst-case per-concept claim-true
demand of 2, and the G-2 flip is not merely unnecessary — keeping it would
FORFEIT the property this epic's head-to-head most wants: exact item-level
pairing between the kernel arm and the generic arm. Conversely, three NEW
hazards appear that the padded store never had (each gets its own ruling
below): **sub-definition claims** (a bare genus clause quoted as a claim can
be semantically true of many concepts — the genuine-falsity problem, §5),
**natural-vocabulary collisions** (a distractor definition can contain the
target headword; an option label can appear inside a shown definition — the
new LC1 surfaces, §6), and **polarity-correlated surface statistics**
(true and false claims now come from segment populations that admissibility
filtering could skew apart — the new LC7 surfaces, §4.4 and lint V5-L7).

Per the epic instruction, NO gsx0 ruling is ported. G-1's mapping is
re-derived and survives (§3); G-2 is retired and replaced (§4–§5); the
distractor, LC1, LC7 and LC8p machinery is re-derived for the new surfaces
(§6, companion lint spec).

## 2. Builder scope, inputs, outputs, discipline

DECISION: [STIPULATED: ASM-2440] item-builder v5 is an **injection builder**,
not a fresh-draw generator: it holds the 360 committed d-qa-t item skeletons
fixed (concept, template type, answer slot, donor/distractor coordinates,
option-slot layout, pinned rank) and re-renders every kernel gloss through
the plain-v5-natural store — the gsx0 construction shape, with every rule
re-derived for multi-segment glosses. Rationale: cross-arm skeleton identity
is what licenses a paired kernel-vs-generic difference-in-lifts in the
consuming head-to-head (0f0y.3); a fresh draw would re-open item-plan design
AND lose pairing. The kernel arm is the frozen `data/d-qa-t` corpus itself
(pin `7179ee…ee27`) and is never rebuilt.

**Inputs (all fail-closed pin checks, `IV5_ERR_REFPIN`):**

1. `data/d-qa-t` skeletons — kot-corpus-hash/1
   `7179ee6791bd0af643c410872925ff594945c29b563192f6d7c4a872397cee27`
   (the frozen f2b-transfer pin, byte-verified before any use);
2. `kernel-v0` / `molecules-v0` — pins as in the gsx0 builder (slot→concept
   mapping only, §3);
3. the plain-v5-natural store `poc/plainv5/store/plain-v5-natural.json` —
   sha256-pinned at build; the builder RE-RUNS the full PV5/S lint in-process
   (ASM-2414's re-run clause) and additionally requires the store's
   `gate-tally.json` to show G-A/G-B acceptance and the
   `authoring_disclosure` to be schema-valid before rendering one byte;
4. the LC8p-v5 reference inventory (companion spec, V5-L8p).

**Outputs:** `data/d-qa-t-plainv5/` containing `items/covered.jsonl`
(360 items, id prefix `dqatp5:`, schema `kot-dqat-plainv5/1`, rank carried
from d-qa-t), `leak-check.json` (fail-closed evidence incl. every disclosure
list of this contract), `pairing-map.json` (§9), `screen-report.json` (§7),
`manifest.json` (source pins, builder sha, counts, seed).

**Determinism and authorship (the gsx0 discipline, unchanged):** no
wall-clock, no os.urandom, no Python `hash()`; every choice is a function of
sha256 over the pre-committed seed + fixed strings + the byte-pinned sources;
built ONCE (single-draw). Seed template pinned here as
`iv5-plainv5/1|<consumer-record-id>|<YYYYMMDD>`; the concrete seed string is
pre-committed VERBATIM in the consuming experiment's prereg before the build
runs. **NO LLM authors, selects, or edits any item text** — the semantic
screens of §7 are deliberately non-steering so this sentence stays true.
FAIL-CLOSED: any pin mismatch, coverage gap, mapping ambiguity, lint
violation, admissibility exhaustion, or screen-threshold breach aborts with a
named `IV5_ERR_*` code; nothing is written on failure. Error codes:
`IV5_ERR_REFPIN`, `IV5_ERR_SOURCE`, `IV5_ERR_MAP`, `IV5_ERR_INJ`,
`IV5_ERR_LEAK`, `IV5_ERR_PAIR`, `IV5_ERR_SCREEN`, `IV5_ERR_MARKUP` (the
`PV5_ERR_*` namespace stays the store lint's).

**Shared definitions** are inherited byte-for-byte from the store lint spec
§1 (`segments()`, `toks()`, `norm()`, word-boundary matching, the NSM-legal
surface vocabulary, Jaccard) — reuse, do not re-type.

## 3. RULING V5-1 — slot→concept mapping (G-1 re-derived; survives)

DECISION: [STIPULATED: ASM-2440] option-slot → concept is recovered by
EXACT, UNIQUE, full-byte kernel-gloss match against the 108-concept pool,
after (a) the d-qa-t corpus reproduces its frozen pin byte-for-byte and
(b) pool-gloss uniqueness is asserted (108/108, fail-closed `IV5_ERR_MAP`).

Re-derivation, not a port: the skeletons are KERNEL-rendered, so the mapping
runs entirely on kernel bytes; nothing about multi-segment stores touches
it. The multi-segment store enters only AFTER mapping, at rendering. The
same fail-closed equivalence-to-regeneration argument as G-1 applies (the
committed corpus IS the pinned generator output). Additionally the builder
asserts plain-v5 store-gloss uniqueness (PV5-5 re-run) before injection, so
the reverse direction (rendered option → store concept) is also unambiguous
for the audit.

## 4. RULING V5-2 — claim-segment selection and polarity preservation (retires G-2)

### 4.1 The rule

DECISION: [STIPULATED: ASM-2441]

1. **Polarity is preserved for all 144 claim skeletons.** A claim-true
   skeleton renders claim-true; a claim-false skeleton renders claim-false.
   **Zero polarity substitutions** — the G-2 flip is retired. The built
   answer key equals the kernel skeleton answer key item-for-item (asserted
   fail-closed, lint V5-L7c), and the yes/no census is inherited unchanged
   (56/88, no-share 0.611 ≤ 0.75, re-asserted by V5-L7a on built counts).
2. **How many claim items per concept:** exactly what the skeleton multiset
   pins — ≤ 2 claim-true + ≤ 2 claim-false per concept [MEASURED, §1]. The
   builder mints NO new claim items and re-plans nothing: "how many" is
   answered by the frozen skeleton plan, because re-planning would break the
   cross-arm identity that motivates injection building (§2).
3. **Which segment (claim-true):** a seeded start-offset scan over the
   target's admissible segments in gloss order — offset
   `sha256(seed|skeleton_id|segstart) mod n_segs`, scanning forward
   cyclically — taking the first segment that passes the claim-eligibility
   predicate **E-CT**:
   - admissible (store lint §1: ≥15 chars, no double quote, from
     `segments()` of the target's plain-v5 definition — hence VERBATIM from
     the pinned store record, lint V5-L6);
   - **specificity tier-1:** ≥ 2 tokens outside the NSM-legal surface
     vocabulary (PV5-7 guarantees ≥ 1 for every admissible segment; the
     floor of 2 removes the most generic clauses from the claimable set);
   - prompt-fresh: the rendered claim question's unsalted surface hash is
     absent from the LC8p-v5 working set (which also enforces per-concept
     segment disjointness: two claim-true items of one concept can never
     quote the same segment, since their full prompt surfaces would
     collide).
4. **Tier fallback:** if the tier-1 scan exhausts, one further seeded scan
   runs at **tier-2** (the plain PV5-7 floor of ≥ 1 non-NSM content token).
   Tier use is recorded per item and disclosed (`claim_tier` field +
   leak-check counts); expected tier-2 count ≈ 0.
5. **Abort, never flip:** if both tiers exhaust for any claim-true skeleton,
   the build ABORTS (`IV5_ERR_INJ`). A silent flip would destroy the pairing
   invariant this ruling exists to establish; the lawful repairs are a store
   repair round (upstream contract §3.4/§6.4) or an explicit contract
   version bump — both coordinator/maintainer decisions, both leaving a
   disclosed trail. Feasibility note: PV5-4 + PV5-11(a) guarantee ≥ 2
   distinct admissible segments against a worst-case demand of 2, and the
   store text postdates every reference corpus, so exhaustion requires a
   specificity-tier + freshness conspiracy expected to occur zero times;
   fail-closed keeps that expectation honest instead of assumed.

### 4.2 Why the answer does not leak through selection

The selection rule is a **pure function of (pinned seed, skeleton_id, store
bytes)**. It never reads the gold answer of any other item, never reads
adjudication or performance data, and polarity itself is skeleton-fixed
(frozen in 2026-07-10 bytes, before the store existed). Four no-leak
invariants, each carried by a named mechanism:

- **(i) Symmetric draw mechanics.** True and false claims are drawn by the
  SAME seeded start-offset scan, over the same population type (admissible
  natural segments of a gate-passed store entry), under the same specificity
  tiers — so segment position, fluency and register do not separate
  polarities by construction of the sampler.
- **(ii) Symmetric eligibility where symmetry is possible.** The specificity
  floor (tier system) applies identically to E-CT and E-CF. The residual
  asymmetry — E-CF's target-relative checks (§5) have no E-CT analogue
  (a segment cannot be "foreign" to its own definition) — is surface-light:
  it conditions on token overlap with the TARGET's texts, which varies per
  item and is not a global surface cue. It is disclosed rather than denied,
  and bounded by (iii).
- **(iii) Fail-closed distributional lints.** V5-L7d bounds the yes-vs-no
  claim length ratio; V5-L7e disclosures publish per-polarity segment-tier
  and first-token distributions so any residual cue is inspectable
  numerically before freeze.
- **(iv) No answer-bearing metadata on the surface.** The rendered prompt
  carries only the fixed claim template + label + claim text (identical
  template bytes to d-qa-t); `claim_tier`, `claim_source`, pairing fields
  live in the item record, which no judge or host model ever sees.

### 4.3 What claim-true "genuinely true" means here

The claim is a verbatim admissible segment of the target's OWN plain-v5
definition (V5-L6 asserts verbatim-substring fail-closed), so it is true
**under the gloss** by construction — the item's definition-scoped gold
("According to the definition of X…") is airtight. Its ORDINARY-MEANING
truth (what a blind external judge answers) is exactly the store's adequacy:
that is what gate G-B and the G-A hard defect classes bought
(upstream contract §6), and no item-level machinery can improve on it.
Delegation disclosed: a claim-true item is only as endorsable as its store
entry, and the consumer's endorsement leg (§11) measures precisely that.

### 4.4 The genus-clause hazard (named, and why it needs §5 + V5-L7)

New with multi-segment glosses: a natural definition's opening genus clause
("a feeling that comes when…", "a small object that…") is FAR less
distinctive than the padded store's whole-definition claims. For claim-TRUE
that is harmless (a generic-but-true clause is still true). For claim-FALSE
it is the central hazard — a donor's genus clause can be semantically true
of the target. §5's admissibility predicate attacks it mechanically; the
tier-1 specificity floor thins generic clauses from BOTH polarities
symmetrically; the §7 falsity screen measures the residual.

## 5. RULING V5-3 — claim-false donor and substitution mechanics

DECISION: [STIPULATED: ASM-2442]

1. **Donor held fixed** from the committed skeleton's `claim_source`
   (pairing-preserving default), exactly as in gsx0.
2. **Segment choice:** the same seeded tiered scan as §4.1(3–4), over the
   DONOR's admissible segments, under eligibility predicate **E-CF** =
   E-CT's admissibility + specificity tiers PLUS all of:
   - **not entailed verbatim:** the segment (normalized) is not a substring
     of the target's normalized plain-v5 definition;
   - **dual overlap bound:** token-set Jaccard(claim, target's plain-v5
     definition) < 0.5 AND Jaccard(claim, target's canonical gloss) < 0.5 —
     the second bound is NEW: it screens world-truth-of-target through the
     kernel-side description too, cheap insurance the padded builder never
     needed because its donors were whole distinctive definitions;
   - **LC1-f (NEW):** no token of the claim equals the target's full label
     or headword (word-boundary, case-insensitive). Natural vocabulary makes
     this a live channel (a donor clause about "juice" may contain "fruit");
     a false claim that NAMES the target reads as self-referential and
     polarity-ambiguous (lint V5-L1d);
   - **foreign-witness (NEW, the genuine-falsity workhorse):** the claim
     contains ≥ 1 token that is (a) outside the NSM-legal surface
     vocabulary, (b) absent from `toks` of the target's plain-v5 definition,
     AND (c) absent from `toks` of the target's canonical gloss. Reading:
     the claim asserts at least one SPECIFIC property that the target's
     definitional content nowhere states — so the definition-scoped gold is
     "no" with a concrete witness, and an ordinary-meaning judge has a
     concrete falsity candidate instead of a generic genus clause;
   - prompt-fresh (LC8p-v5 working set).
3. **Seeded donor redraw:** if NO segment of the fixed donor passes E-CF,
   the donor is redrawn by the seeded loop (≤ 256 candidates over the sorted
   label list, excluding self and same-definition concepts), first redraw
   candidate with an E-CF-passing segment wins. Every redraw is recorded
   (`donor_redrawn` list) and marks the item DEVIATED in the pairing map
   (§9). Exhaustion of the redraw loop aborts (`IV5_ERR_INJ`).
4. **Truth semantics, stated honestly:** "genuinely false under the gloss"
   is carried by construction (the claim is not stated by, entailed
   verbatim by, or token-near the target's definition, and carries a
   foreign witness). "Genuinely false under ordinary meaning" — what the
   blind external judge answers — is carried only PROBABILISTICALLY by
   these proxies: no mechanical rule decides semantic truth
   [STIPULATED: ASM-2442, explicitly not a guarantee]. The residual is
   measured twice: the §7 falsity screen before freeze (fail-closed
   threshold), and the consumer's per-family endorsement leg at stage 1
   (§11), which is where a broken falsity construction lawfully kills the
   experiment cheaply.

## 6. RULING V5-4 — distractor selection (def-match, term-match)

DECISION: [STIPULATED: ASM-2443] fixed coordinates when admissible; seeded
redraw, disclosed and pairing-marked, when not. "Exactly one option is
correct" is enforced at three depths: bytes (uniqueness), tokens (overlap
bounds), semantics (screen §7 + store gate G-B).

### 6.1 def-match ("Which option gives the meaning of the word …?")

Options are the skeleton's four concept coordinates rendered through the
store: the target's plain-v5 definition (answer) + 3 distractor concepts'
plain-v5 definitions. Per-distractor admissibility **D-DM**:

- no token of the distractor definition equals the TARGET's label or
  headword (word-boundary) — the new LC1 surface: with natural vocabulary a
  distractor definition can literally contain the target word, a
  polarity-visible artifact absent from NSM-rendered kernel glosses (lint
  V5-L1c);
- token-set Jaccard(distractor definition, target's plain-v5 definition)
  < 0.5 — near-synonym discriminability floor; PV5-5 already guarantees
  byte-distinctness, this bounds token-level adequacy overlap so no
  distractor is a trivial re-wording of the answer.

An inadmissible slot is redrawn: seeded scan over the sorted label list
excluding the target, concepts already in the option set, and same-definition
concepts, first admissible candidate wins; recorded in
`distractor_redrawn` (item + slot) and pairing-marked DEVIATED. The answer
slot is NEVER redrawn — the answer is the target's definition by identity
(a failure of the answer's own constraints is impossible: PV5-2 bans the
headword from its own definition; if any assertion on the answer text fails
the build aborts, it does not substitute). Inherited assertions: option
texts pairwise distinct (V5-L4), answer present exactly once, answer text
not contained in the question (V5-L2), option-key layout and answer key
byte-carried from the skeleton.

### 6.2 term-match ("A word whose definition is: … Which word is it?")

The question renders the TARGET's plain-v5 definition; options are the four
skeleton label coordinates (words). Checks:

- **V5-L1a (inherited LC1-s, strict):** neither the target's full label nor
  its headword occurs as a token of the shown definition — guaranteed by
  PV5-2, re-asserted fail-closed at the item surface;
- **V5-L1b (NEW):** no DISTRACTOR label's headword occurs as a token of the
  shown definition. With natural glosses this is common (the definition of
  "juice" plausibly contains "fruit"); an option word visible inside the
  definition is a surface artifact cutting both ways (elimination cue /
  topical decoy), so it is removed symmetrically. Inadmissible distractor
  labels are redrawn (same seeded discipline as §6.1, excluding labels
  whose headword appears in the shown definition), recorded and
  pairing-marked.

The kernel-arm reproduction check (question reproduces from the pinned
template applied to the kernel gloss) is inherited from the gsx0 builder
verbatim, as is the template byte-identity requirement.

### 6.3 Why redraws are lawful here but flips were not in §4

A distractor/donor redraw changes a WRONG-option coordinate while preserving
item type, target concept, answer key, and template — the paired estimand
"same question about the same concept with the same correct answer" survives
with a disclosed perturbation, quantified per item in the pairing map. A
polarity flip changes the ANSWER — the estimand itself. Hence: redraws
allowed + disclosed + pairing-marked; flips forbidden + fail-closed.

## 7. Semantic screens (non-steering, fail-closed at threshold)

DECISION: [STIPULATED: ASM-2446] two blind screens run AFTER the build and
BEFORE any consumer freeze, on the pinned built corpus:

- **SCREEN-F (genuine falsity):** all 88 claim-false items. Prompt (pinned
  bytes, blinding-grep clean): the item's question only, plus "answer
  strictly from the ordinary meaning of the word: is the quoted statement
  true of <label>? yes/no/unsure". A flag = `yes` or `unsure`.
- **SCREEN-1C (single correct option):** all 216 option items (108
  def-match + 108 term-match). Prompt: the item's question + options only,
  plus "is more than one option a defensible answer? yes/no + the option
  keys". A flag = `yes`.

**Instrument:** Claude Haiku 4.5 in the operationalised pinned headless form
(`poc/truthstyle-2x2/judges-invocation.md` §4.3 + §4.3.1, all tripwires),
one read per item, first valid answer final (ASM-0241 discipline).
Vendor-disjointness holds per ASM-2413 (author family OpenAI; evaluator
Claude). Disclosed caveat: the screen shares a vendor family with the
consumer's judge seats — acceptable because the screen is **non-steering**:

- flags NEVER cause a redraw, re-render, or edit (the "NO LLM selected any
  item text" sentence of §2 stays exactly true);
- acceptance rule: flag rate ≤ **5% per family** (claim-false; def-match;
  term-match), else `IV5_ERR_SCREEN` abort → maintainer escalation (lawful
  repairs: store repair round or contract version bump — never item-level
  cherry-picking);
- on acceptance, ALL flagged item ids ride in `screen-report.json` and the
  consuming prereg MUST register a flagged-subset sensitivity (primary
  unchanged; a secondary re-read excluding flagged items) — so a marginal
  screen outcome is analyzed, not buried.

The screen is a defect DETECTOR bounding instrument-failure risk before
money is spent; it is not gold, and no verdict-bearing quantity may cite it
[STIPULATED: ASM-2446].

## 8. Leak lints (fail-closed; full contract in the companion spec)

DECISION: [STIPULATED: ASM-2444] the builder enforces, in-process and
fail-closed, the V5-L* contract of
`docs/next/design/item-builder-v5-leak-lint-spec.md`:

| code | check | lineage |
|---|---|---|
| V5-L1a | term-match: target label/headword not in shown definition | LC1/LC1-s re-derived |
| V5-L1b | term-match: no OPTION label headword in shown definition | NEW |
| V5-L1c | def-match: target headword in no option text | NEW |
| V5-L1d | claim-false: target label/headword not in claim (LC1-f) | NEW |
| V5-L2 | def-match: answer text not contained in question | LC2 |
| V5-L3 | claim-false admissibility E-CF (substring, dual Jaccard, foreign witness) | LC3-s re-derived |
| V5-L4 | options pairwise distinct; answer present exactly once | LC4 |
| V5-L5 | unique ids; unique prompt surfaces; store-text distinctness incl. vs knull store texts | LC5 extended |
| V5-L6 | claim-true verbatim substring of the pinned store record | LC6 |
| V5-L7a–e | yes/no ≤ 0.75; ABCD ≤ ½; ZERO polarity flips; claim-length polarity-cue band; per-polarity distribution disclosures | LC7 re-derived |
| V5-L8p | full-prompt disjointness vs the enumerated reference inventory + intra-corpus + sibling arms | LC8p re-derived |
| V5-L9 | no unrendered markup; RT-14 clean; ASCII | hygiene |

The reference-set definition for V5-L8p (which corpora count, and why) is
its own registered choice: [STIPULATED: ASM-2449] — five hard-pinned QA
corpora (d-qa 650, d-qa-r 1000, d-qa-t 360, d-qa-t-plain 360, d-qa-t-opaque
360), an auto-enumerated inventory sweep over every `data/*/items/*.jsonl`
present at build time (this mechanically covers current and future item
corpora, including the stage-3 input corpora under `data/`), and a
documented exclusion of non-item artifact trees (probe caches, atlases,
carrier manifests) which carry no QA prompt surfaces — with the consumer
obligation that any experiment reusing plain-v5 SURFACES elsewhere must
extend the reference set first. Details in the companion spec.

## 9. Pairing map and cross-arm binding

DECISION: [STIPULATED: ASM-2445]

**`pairing-map.json` (schema `kot-iv5-pairing/1`)** — one row per
skeleton_id:

```json
{
 "skeleton_id": "dqat:covered:<label>:t3",
 "plainv5_id": "dqatp5:covered:<label>:t3",
 "type": "claim-true",
 "status": "EXACT | DEVIATED",
 "deviations": ["donor-redraw" | "distractor-redraw:slot-B" | ...],
 "answer_equal_kernel": true,
 "claim_source_equal_kernel": true,
 "option_concepts_equal_kernel": true
}
```

`answer_equal_kernel` must be true for ALL 360 rows (V5-L7c; zero flips —
the headline improvement over gsx0). `status: EXACT` requires every
`*_equal_kernel` field true. The EXACT/DEVIATED census is a build output,
MEASURED then, forecast now only as "DEVIATED expected small" [STIPULATED —
explicitly not a number to be relied on].

**What pairing licenses (for the 0f0y.3 prereg):** the consumer MAY
pre-register an item-level PAIRED kernel-vs-generic difference-in-lifts on
the EXACT subset, with the DEVIATED subset handled by a pre-declared rule
(join unpaired, or sensitivity) — gsx0's "kernel pairing not claimed"
disclaimer is retired for the EXACT subset only, and only because zero
flips + coordinate-equality are asserted fail-closed per item. Whether the
kernel arm reuses the frozen f2b-transfer d-adj-t gold or re-adjudicates
concurrently is 0f0y.3's design decision, out of scope here; this contract
guarantees only surface-level pairing.

**Cross-arm binding (gsx0 rule inherited and generalized):** the plain-v5
pass is the BINDING pass. Any sibling rendering built from the same
skeletons (e.g., a fresh opaque analogue, or any future store arm) consumes
the plain-v5 decisions verbatim — polarity (identity, here), donor,
redrawn coordinates, option layout — and may NEVER redraw independently; a
sibling-side admissibility failure aborts the build (`IV5_ERR_INJ`,
skeleton forks are not allowed). Shuffled-store controls are runner-side
store derangements at verify time, not new corpora, and are untouched by
this contract.

## 10. Item-leak audit interplay (ASM-2417 licensed channels)

DECISION: [STIPULATED: ASM-2447] the store contract's independent item-leak
audit (§7.2 there) exempts "items about X quoting X's own definition". This
builder adds one more construction-licensed channel and machine-readable
provenance for both, so the audit exempts EXACTLY the pinned channels and
nothing else:

- **Channel A (own-definition):** def-match answer option, term-match stem,
  claim-true claim — item about X carrying bytes of X's plain-v5
  definition. Licensed iff the bytes match the pinned store record of the
  item's own `label`.
- **Channel B (donor-claim, NEW):** claim-false item about T carrying a
  segment of donor X's definition. Licensed iff X equals the item's pinned
  `claim_source` AND the quoted bytes equal the item's pinned `claim` field
  AND that claim passed E-CF.
- **Channel C (distractor-definition):** def-match option slots carrying
  OTHER concepts' definitions at the pinned (possibly redrawn-and-disclosed)
  coordinates.

Every ≥6-gram/Jaccard hit outside these channels is an audit FINDING
(freeze-blocking, per ASM-2417). The audit's mechanical pass re-runs
V5-L1*/V5-L5/E-CF-Jaccard independently of the builder — same rules,
different hands, which is the point.

## 11. Difficulty and headroom, re-read on the new surfaces

DECISION: [STIPULATED: ASM-2448]

**Void list — numbers that may NOT be carried into any plain-v5 consumer:**
knull-v2 R1-alone-plain ≈ 0.504–0.505 and R3-alone-plain ≈ 0.948 (padded
surfaces, membership gold); gsx0's pilot "PROCEED expected" posture and its
stage-1 endorsement expectation (A ≈ 0.85 at padded whole-definition
claims); every gsx0/knull power input derived from them. Reasons the
surfaces are out-of-distribution for those numbers: (i) register — fluent
edited-dictionary prose replaces cyclic padded repetition, changing both LM
guessability and judge fluency-endorsement; (ii) claim shape —
sub-definition segments replace whole-definition claims, shortening and
de-specifying the claim family in both polarities; (iii) distractor
discriminability — natural near-synonym definitions replace NSM explications
in option sets; (iv) the falsity construction is new (E-CF vs gsx0 LC3-s).
Direction-of-risk sketch (STIPULATED, no numbers, decision-useless by
design): R1-alone could move UP (more guessable text ⇒ headroom-cap risk)
or DOWN (more confusable options); human endorsement of true claims
plausibly up, of false-claim rejection genuinely unknown. Nothing here is a
forecast; everything must be measured.

**Consumer obligations (binding handoff conditions on any experiment that
freezes against a corpus built under this contract):**

- **O-1 (blinded pilot, re-derived arithmetic):** a stage-0 blinded pilot on
  the first-K items in pinned rank order, with a binding binary STOP rule
  whose bar is re-derived from the CONSUMER's own registered headroom cap
  and powered Δ (bar = cap − Δ, the gsx0 ARITHMETIC, never the gsx0
  CONSTANTS), Wilson-LB form, adjudicate-once/reuse discipline. No PROCEED
  expectation may be stated from prior stores.
- **O-2 (staged headroom):** the baseline-alone cells run and are gated
  BEFORE the majority of GPU spend (the 2b-i staging shape), with the
  headroom read emitted from baseline data alone.
- **O-3 (per-family endorsement):** the stage-1 endorsement gate must
  publish Wilson bounds PER ITEM FAMILY (def-match / term-match /
  claim-true / claim-false), not only pooled — the genus-clause hazard
  (§4.4) is family-local, and pooled A can mask a claim-false endorsement
  hole. Power for the family-level reads must be computed at the family
  n's (108/108/56/88), not at 360.
- **O-4 (no inherited premises):** the consumer's power/forecast section may
  cite void-listed numbers only as history tagged VOID-for-these-surfaces;
  any load-bearing premise about difficulty on plain-v5 surfaces must be
  MEASURED on plain-v5 surfaces (pilot or stage-1).

**Builder-level instruments (descriptive only, never verdict-bearing):** the
leak-check reports, per family: claim word-count distributions by polarity,
option-set Jaccard spreads (answer-vs-distractor), foreign-witness token
counts, segment-tier usage, EXACT/DEVIATED census. These are MEASURED at
build as corpus descriptions; a difficulty CLAIM from them would be an
unlicensed extrapolation [STIPULATED].

## 12. Execution plan (for the coordinator; nothing executed here)

1. Coordinator review of this contract + companion; ratify with 0f0y.1's
   open points (they gate the same consumer).
2. Store pipeline completes first (0f0y.1 §9: sense annotations → authoring
   → lint/repair → gate). The builder is implementable only against an
   existing, lint-green, gate-green, sha-pinned store.
3. Consumer (0f0y.3) prereg drafts; the concrete builder seed string is
   pre-committed verbatim there; THEN `data/d-qa-t-plainv5/build.py` is
   implemented verbatim from this contract + companion and run ONCE
   (single draw, CPU-only, $0).
4. Screens (§7) run on the pinned corpus (subscription claude calls, ≈$0);
   `screen-report.json` committed with the corpus.
5. Item-leak audit (ASM-2417 + §10 channels) runs inside the consumer's
   pre-freeze gates; corpus pins + pairing map + screen report enter the
   consumer's record.
6. Any store repair after the corpus exists invalidates the corpus: rebuild
   from scratch under a fresh pre-committed seed, full lint + screens re-run
   (no incremental patching, ever).

## 13. Self-check gate (mandatory)

- Every design choice is tagged STIPULATED with a registered ASM id
  (ASM-2440..2449 appended with this deliverable); every number is MEASURED
  with its artifact named (d-qa-t counts, gsx0 leak-check counts, canonical
  segment census) or is explicit arithmetic. Checked.
- Pseudonyms only (Fable, kern/fable-designer, coordinator, maintainer,
  designer-1); RT-14 pattern-list clean over this doc and the companion.
  Checked.
- ASM block disjointness: ASM-2440–2449 unused anywhere in registry/,
  docs/, poc/, or data/ before this deliverable (grep, 2026-07-16; the
  block starts at 2440 because the concurrent working-tree deliverable
  gpt56-draft-pipeline-large-kernel.md already references 2420–2439 —
  collision detected and avoided in-session). Checked.
- No frozen object touched: registry/experiments/{knull,knull-v2,gsx0,f1k*}
  byte-untouched; data/d-qa-t{,-plain,-opaque} byte-untouched; no builder
  implemented; no item rendered; no LLM call made; no experiment record
  created or modified. Checked.
- The gsx0 rulings are re-derived, not ported: G-1 re-argued on kernel
  bytes (§3); G-2 retired with the scarcity premise shown false (§1, §4);
  LC1/LC3/LC7/LC8p each re-derived with named NEW surfaces (§5–§6,
  companion). Checked.
- `python3 tools/registry/registry-check.py` run in-session after the
  register append + kb-sync-internal: ZERO violations attributable to this
  deliverable; the residual violations in the working tree all belong to
  the concurrent gpt56-draft-pipeline-large-kernel deliverable (its cited
  ASM block is not yet registered) and are that deliverable's to clear.
  Checked.

## 14. Registered ASM block (verbatim summaries; full entries in registry/assumptions.jsonl)

- **ASM-2440 [STIPULATED]** item-builder v5 is a deterministic, single-draw,
  fail-closed INJECTION builder over the 360 frozen d-qa-t skeletons; no
  LLM authors/selects/edits item text; RULING V5-1 mapping re-derived.
- **ASM-2441 [STIPULATED]** RULING V5-2: polarity preserved for all 144
  claim skeletons (zero flips; abort-not-flip), seeded tiered claim-true
  segment scan, no-leak invariants (i)–(iv).
- **ASM-2442 [STIPULATED]** RULING V5-3: claim-false E-CF admissibility
  (verbatim non-entailment, dual Jaccard < 0.5, LC1-f, foreign witness,
  tiers) with fixed donor + seeded disclosed redraw; genuine ordinary-
  meaning falsity is proxied + screened + stage-1-measured, never
  guaranteed.
- **ASM-2443 [STIPULATED]** RULING V5-4: distractor admissibility D-DM /
  V5-L1b with seeded disclosed redraws; answer slots never redrawn; flips
  forbidden while redraws are lawful (estimand argument §6.3).
- **ASM-2444 [STIPULATED]** the V5-L* leak-lint contract (companion spec)
  is fail-closed and runs in-process in the builder.
- **ASM-2445 [STIPULATED]** pairing-map schema + cross-arm binding; the
  EXACT subset licenses item-level paired analysis in the consumer; sibling
  arms never fork.
- **ASM-2446 [STIPULATED]** SCREEN-F/SCREEN-1C: blind Claude-seat,
  non-steering, ≤5% per-family flag threshold fail-closed, flagged-subset
  sensitivity mandatory in the consumer.
- **ASM-2447 [STIPULATED]** item-leak-audit licensed channels A/B/C with
  machine-readable provenance; all other overlap hits are findings.
- **ASM-2448 [STIPULATED]** difficulty/headroom re-read: gsx0/knull numeric
  forecasts VOID on plain-v5 surfaces; consumer obligations O-1..O-4;
  builder statistics descriptive-only.
- **ASM-2449 [STIPULATED]** LC8p-v5 reference-set definition: five pinned QA
  corpora + `data/*/items/*.jsonl` inventory sweep + store-text
  cross-store distinctness; exclusions documented; reuse extends the set
  first.
