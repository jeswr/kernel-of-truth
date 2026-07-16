# plain-v5-natural — the strong generic-definition store CONTRACT (authoring, blindness, lint, gate, disclosure)

> **Status: [EXP-DESIGN] design-only deliverable of maintainer decision
> issue 44 ("1 + 2A", approved 2026-07-16): GPT-5.6-Sol AUTHORS a strong
> generic-definition store, with the LLM judge/gate seats swapped to the
> Claude family in any consuming experiment. Epic `kernel-of-truth-0f0y`,
> child `kernel-of-truth-0f0y.1`. Author: Fable, experiment-designer role
> (kern/fable-designer), 2026-07-16. NOTHING here is authored, frozen,
> scheduled, or run: no authoring session has been executed, no GPU touched,
> no frozen record (knull, knull-v2, gsx0, f1k) modified. The coordinator
> reviews and commits.**
>
> **Companion artifacts (this deliverable):**
> `docs/next/design/plain-v5-register-lint-spec.md` (the fail-closed lint
> contract, codes PV5-*/S-*), and
> `docs/next/design/plain-v5-authoring-prompt-template.txt` (the exact blind
> authoring prompt bytes, placeholders only).
>
> **Assumption entries:** ASM-2410–ASM-2419 (block verified disjoint —
> highest id in use before this deliverable: ASM-2406) appended to
> `registry/assumptions.jsonl` in the working tree with this deliverable;
> commit custody stays with the coordinator.
>
> **REVISION r2 (2026-07-16, Fable, design-only):** closes the five gaps of
> the cross-model review HOLD on r1: (1) item-blind sense-annotation source
> + checked pre-item ordering (§3.3, ASM-2450); (2) exhaustive CONTEXTUAL
> item-leak review replacing the sampled spot-check (§7.2, ASM-2451);
> (3) normalized family map + fail-closed disjointness validator at EVERY
> LLM seat including tie-breaks (§4.1, ASM-2452); (4) contextual
> no-extraneous-facts GATE read G-C (§6.4, ASM-2453); (5) readout-level
> disclosure validator, fail-closed (§7.3, ASM-2454). New assumption block
> ASM-2450–ASM-2454 (verified disjoint — highest id in use before r2:
> ASM-2449). Still design-only; nothing authored, run, or committed.
>
> **REVISION r3 (2026-07-16, Fable, design-only):** closes the three routes
> of the r2 RE-review HOLD: (1) NON-BLIND SENSE INPUTS — the sense
> channel's residual post-item human inputs (the designer synset picks and
> the freehand fallback lines) are ELIMINATED: sense selection is now a
> pinned DETERMINISTIC function of two item-independent, pre-item-fixed
> sources (the OEWN-2024 release archive and the frozen concept-record
> metadata), the fidelity seat is demoted to veto-only with a bounded
> published-synset-only override path, and the `fallback-designer` freehand
> channel is RETIRED as a lint failure (§3.3, lint S-6 rewritten + S-7 NEW,
> ASM-2456); (2) UNDER-AUDITED ANNOTATION↔ITEM PAIRS — the item-leak audit
> now covers the annotation↔item PAIRING itself: mechanical A-ANN-* checks
> (map byte-reproduction, n-gram, Jaccard vs item stems/answers) plus
> first-class CLR probes P1a/P2a with ZERO licensed channels for
> annotations, enumerated over every provenance-touching role — own, donor,
> distractor (§7.2, ASM-2457); (3) UNLEDGERED SAME-FAMILY EVALUATOR — the
> disjointness invariant is enforced AT RUN TIME by an append-only,
> hash-chained SEAT LEDGER (`kot-seat-ledger/1`, author = entry 0) written
> by the single pinned invoker `invoke_seat.py`, which refuses same-family
> or UNKNOWN-family dispatch BEFORE the API call; orphan seat outputs and
> chain/role breaks fail closed (FD-5/FD-6 NEW) (§4.1, ASM-2458). New
> assumption block ASM-2456–2458 (verified disjoint — highest id in use
> before r3: ASM-2455). Still design-only; nothing authored, run, or
> committed.
>
> **Tag convention (house discipline):** `[MEASURED: ref]` = a programme
> artifact restated strictly inside its envelope; `[STIPULATED: ASM-id]` = a
> design choice registered in the assumption register; every design CHOICE in
> this document is STIPULATED, never MEASURED.

---

## 1. Why this store exists (the advisory, and what it replaces)

The programme's aligned-non-NSM comparator lineage for the 108 covered
concepts now stands at:

- **knull-v2 verdict is NULL** — the kernel arm's verify-retry lift is
  TOST-equivalent (±0.05) to the best aligned non-NSM arm.
  PREMISE: [MEASURED: registry/verdicts/knull-v2.json] primary
  `/analysis/tost_equivalent` = true.
- The token-matched generic arm in that comparator set is **plain-padded**
  (ASM-1082): the concise plain definition cyclically repeated, whole own
  segments joined by "; ", until it lands in the kernel-gloss word band. That
  transform is deterministic and disclosed, but it is a **degenerate
  opponent**: its extra tokens are verbatim repetition, not content. The
  architecture-advisor's 2026-07-16 advisory (epic `kernel-of-truth-0f0y`
  description) finds the repetition plausibly biases human-gold endorsement
  in a KERNEL-FLATTERING (anti-conservative) direction on gsx0's kill-bearing
  endorsement leg — the forbidden bias direction under the programme's own
  conservatism principle. The GPT-5.6 readiness review of gsx0 independently
  flags the same structural ambiguity: "a padded-store FAIL is ambiguous
  between content and padding artefact" (finding 5,
  docs/next/analysis/gsx0-readiness-review.md).
- Three successive Fable-authored plain stores failed the blind two-family
  quality gate: v2 (naturalness 4/10 GPT-5.6, 3/10 Haiku), v3 (8/10 / 4/10 —
  set-level template monotony), v4 (4/10 / 3/10 — "theatrically formal"
  frame variation). The v3→v4 trajectory measured the same instrument moving
  8→4 on re-wordings of the same 108 concepts, with inter-family
  contradictions on named defect classes
  (docs/next/analysis/knull-v3-quality-gate.md, knull-v4-quality-gate.md).

**The maintainer's ruling (decision issue 44, "1 + 2A"):** stop iterating
Fable authorship and stop padding. A strong OpenAI-family model
(**GPT-5.6-Sol**) authors each generic definition **natively AT the
kernel-gloss word band** — natural elaboration, every added clause
definitional, no verbatim repetition — and, because the author family
changes, **every LLM evaluator seat that touches this store (quality gate,
downstream judges) moves to the Claude family**.

DECISION: [STIPULATED: ASM-2410] this contract adopts the issue-44 ruling as
binding for the plain-v5-natural store and all its consuming experiments.

**What this document is NOT.** It defines the STORE contract only. It does
not run the authoring session (coordinator-scheduled, $0-GPU, subscription
codex calls). It does not redesign the item builder — a natural at-band gloss
has MULTIPLE admissible segments, unlike the padded store's repetition of ONE
concise set, so claim-segment selection and polarity substitution must be
redesigned separately (epic child `kernel-of-truth-0f0y.2`, flagged in §6.3).
It does not register or modify any experiment record: the head-to-head that
consumes this store is `kernel-of-truth-0f0y.3`, a fresh record with a fresh
prereg.

## 2. Estimand — what the store's text is allowed to be

DECISION: [STIPULATED: ASM-2411] the store's estimand is **matched dictionary
content**: for each of the 108 covered concepts, an ordinary-English
definition in the **genus + differentiae register** of an edited general
dictionary, occupying the SAME word budget as the concept's canonical gloss.
It is NOT encyclopedic knowledge injection: no named entities, no dates, no
quantities, no historical/technical/statistical facts beyond what a
dictionary's defining line would carry. The lint enforces the mechanical
surface of this bound (PV5-12: lowercase-only, no digits); the semantic
remainder is enforced fail-closed by TWO gate reads — the blind
`encyclopedic-injection` hard defect class (§6.2 class 4) and the
CONTEXTUAL no-extraneous-facts read G-C (§6.4), which classifies every
clause defining/extraneous with the headword and sense in view. The bound
is a gate, not a guideline: one surviving extraneous clause blocks
acceptance. The claim this store supports in a consuming experiment is therefore
"a first-rate generic DICTIONARY store at token parity", tagged
STIPULATED-not-MEASURED: nothing measures that the store is the best possible
generic opponent, only that it passes this contract's gates.

**Word band (the old L-3, reinstated as an AUTHORING constraint).** For
concept c with canonical gloss word count `wc` (whitespace-split; the kernel
gloss for the 54 kernel-v0 concepts, the molecule groundingNote for the 54
molecules-v0 concepts):

```
LO(c) = ceil(0.75 * wc)          HI(c) = max(floor(1.25 * wc), wc + 8)
```

— the identical arithmetic of knull G-1 clause L-3 and of the ASM-1082 padded
band, so the store is token-band-comparable with every prior arm. The
canonical glosses run 10–57 words (mean 34.9, median 34.5 across the 108), so
targets range roughly [8, 18] to [43, 71] words. The band is met by NATIVE
authoring — the author writes to the budget — never by any padding transform;
PV5-11 (no internal repetition) makes the ASM-1082 channel a lint failure.

## 3. Authoring protocol (GPT-5.6-Sol, blind, one pinned session)

DECISION: [STIPULATED: ASM-2412] authoring runs as ONE batched blind
GPT-5.6-Sol session over all 108 concepts, plus at most 3 leakage-bounded
repair rounds, under the following pins.

### 3.1 Instrument

- **Model/client:** `gpt-5.6-sol` via codex-cli exec (version recorded at
  run time; ≥ 0.144.1), reasoning effort high, `-s read-only
  --ignore-user-config --skip-git-repo-check --ephemeral --disable memories
  --disable standalone_web_search`, **empty out-of-repo workdir** — the same
  isolation envelope as the pinned blind-judge form
  (docs/next/analysis/knull-v4-quality-gate.md §2), used here for authoring.
- **Prompt:** the rendered bytes of
  `docs/next/design/plain-v5-authoring-prompt-template.txt` §A with exactly
  three placeholder classes filled per concept row: `{{HEADWORD}}`,
  `{{SENSE}}` (§3.3), `{{LO}}`/`{{HI}}` (§2). Nothing else varies. The
  rendered prompt sha256 and the FULL session transcript sha256 are pinned in
  the store's `authoring_disclosure` (§8.1).
- **Batched, not per-entry:** one session sees all 108 rows and is instructed
  to vary entry shapes as a real dictionary does. Rationale: the v3 gate
  failure was set-level template monotony produced by uniform per-entry
  authoring; only a set-aware author can control set-level shape diversity.
  The cost — entries are not independent draws — is irrelevant here because
  the store is a single arm's content, not sampled stimuli.
- **Output:** a single JSON object `{headword: definition}` with exactly the
  108 keys; parsed fail-closed.

### 3.2 Blindness (binding guardrail)

The author sees ONLY:

1. the headword,
2. the one-line sense annotation (§3.3),
3. the per-concept word band `[LO, HI]`,
4. the authoring-facing constraint list (template §A — the lint contract's
   author-visible subset, with no mention of the programme, of any
   experiment, of any other store, or of the band's provenance).

The author NEVER sees: kernel/molecule records or glosses, QA items or
skeletons, any d-qa/d-qa-r/d-qa-t performance data, any prior plain store
(v1–v4, padded), any gate rubric, or any project documentation. Enforcement
is structural (empty ephemeral workdir; prompt = pinned template bytes only)
plus a **blinding grep** over the rendered prompt and all repair prompts:
the case-insensitive pattern list
`kernel|nsm|knull|f2b|truthstyle|gsx|molecule|explication|wierzbicka|padded`
must have zero hits (asserted before send, fail-closed).

**Disclosed leak channels (bounded, pinned):**

- **Band arithmetic leaks gloss LENGTH.** `[LO, HI]` is invertible to `wc`:
  the author learns each canonical gloss's word count and nothing else about
  it. Disclosed in `authoring_disclosure.band_leak_note`; content-free beyond
  length.
- **Sense annotations are a deterministic function of item-blind sources**
  (§3.3, r3): selection AND rendering are pinned pure functions of the
  OEWN-2024 archive and frozen pre-item record fields — no designer pick,
  no freehand line, no post-item human byte reaches the author except the
  capped, disclosed, published-synset-only maintainer overrides of
  §3.3(a)3, every one of which is mandatorily audited (§7.2). The whole
  chain is S-linted (S-1..S-7) and byte-reproduced by the audit
  (A-ANN-MAP).
- **Repair feedback** is restricted to the enumerated feedback codes of the
  lint spec §5 (e.g. "clause 2 overlaps a reserved phrase set; rephrase in
  different words") — never quoted kernel text, never item text. Every
  repair prompt is part of the pinned transcript, so the total leaked
  information is inspectable byte-for-byte.

### 3.3 Sense annotations (ITEM-BLIND source, pinned BEFORE authoring and BEFORE any consuming item)

One line per concept identifies the intended sense (the store must define
ONE admissible sense — e.g. *kind* the category-noun, not the adjective;
*ball* the play-object, not the dance). r1 had Fable — who is NOT
item-blind — author these lines freehand under a mechanical S-lint only;
the cross-model review correctly held that free text from a non-blind
author is a semantic side channel no string lint can close.
DECISION: [STIPULATED: ASM-2450] the channel is rebuilt on two independent
defences: an item-blind SOURCE and a CHECKED pre-item ordering.

r2 still left two post-item HUMAN inputs inside the channel: Fable's
synset picks in the sense-map (a non-blind designer choosing, after items
exist, which of several published senses the author reads about) and up to
22 freehand fallback lines. The r2 re-review correctly held that a
capacity BOUND on a non-blind chooser is not blindness — a chooser who has
seen the items can still steer item-correlated bits through any nonzero
channel. DECISION: [STIPULATED: ASM-2456] r3 removes the chooser: every
author-visible annotation byte is a PINNED DETERMINISTIC FUNCTION of
item-independent sources whose content was fixed before any programme item
existed. The exact sources, the selection function, and the ordering:

**(a) Item-blind source (primary; the load-bearing defence).** Sense
annotations are RENDERED, not written:

1. **Inventory:** Open English WordNet 2024 (OEWN, CC BY 4.0 — the
   programme's scouted lexical sense inventory,
   docs/next/structured-db-scouting.md), release archive sha256-pinned at
   commit time in `poc/plainv5/inputs/oewn-pin.json`. The inventory's
   content was fixed YEARS before any programme item (d-qa*, gsx0, f1k,
   plain-v5) existed, so no byte of it can encode an item answer: the
   blindness is temporal and absolute, not attested.
2. **Mapping (r3: DETERMINISTIC SELECTION, no designer pick):**
   `poc/plainv5/inputs/sense-map.json` is a BUILD ARTIFACT, never
   hand-written: the pinned selector
   `poc/plainv5/inputs/select_senses.py` (sha-pinned; its scoring rule is
   fixed HERE, before implementation) scores every OEWN synset of the
   headword lemma by normalized token overlap between the concept's
   canonical gloss and the synset's definition + lemma names + direct
   hypernym/hyponym lemma names (extended-Lesk), takes the argmax, and
   breaks ties by lexicographic synset id. Per-concept output:
   `{label, source: "oewn-selector", synset_id, pos, lexname, lemmas_used,
   score}` — no `justification` free text (the justification IS the pinned
   rule). Inputs to the function are exclusively pre-item bytes: the
   OEWN-2024 archive (1) and the canonical glosses byte-frozen in the
   kernel-v0/molecules-v0 records — records that every programme item was
   later DERIVED FROM, so the gloss adds no item information the record
   did not already carry, and the gloss itself never reaches the author
   (the render is metadata-only, S-5). What the author can observe is only
   WHICH synset was selected — the same log2(#synsets)-bit payload as r2,
   but now computed by a pure function containing zero post-item human
   bits. Tuning surface: none — the scoring rule and tie-break are pinned
   in this contract before the selector exists; any change to the selector
   is a contract version change (new shas everywhere); the map's
   byte-reproducibility from the pins is lint code S-7 and is re-asserted
   audit-side (A-CLR/A-ANN-MAP, §7.2), so a post-hoc hand edit cannot
   survive.
3. **Fidelity check (independent seat, r3: VETO-ONLY):** a Claude-family
   seat (family map, §4.1; pinned headless form, one read,
   first-valid-final, ledgered per §4.1) sees, per concept, the headword,
   the canonical gloss, and the full candidate synset list rendered from
   the pinned inventory, and answers whether the SELECTOR'S synset is the
   sense of the canonical gloss. The seat cannot substitute a pick; a veto
   escalates to the maintainer. A maintainer override may ONLY substitute
   another PUBLISHED synset of the same headword from the pinned
   inventory — never free text — recorded in the map as
   `source: "maintainer-override"` with a justification field, counted and
   capped at 8 of 108; exceeding the cap HALTS before the authoring
   session. Overrides are the sole post-item human input remaining in the
   whole channel: each is disclosed (§7.1 `override_count`) and is a
   MANDATORY unit of the §7.2 annotation audit. Fable never adjudicates
   and never overrides.
4. **Deterministic render:** `poc/plainv5/inputs/render_sense_annotations.py`
   (sha-pinned) renders each annotation from synset METADATA ONLY — part of
   speech, supersense (lexname), at most two non-headword lemma names, and,
   where the headword has other synsets, one contrast clause built from the
   nearest excluded sense's supersense or a contrast lemma. The OEWN
   definition text is NEVER consumed (it is a definition, and the sense
   channel must not carry one — S-4). Byte-reproducibility is lint code
   S-5; the renderer's no-definition-input property is asserted there too.

**(b) Fallback channel (r3: DETERMINISTIC RECORD-METADATA RENDER; freehand
RETIRED).** Concepts whose headword has no OEWN synset at all (or whose
selection is vetoed with no admissible published-synset override) do NOT
take a designer-authored line — the r1/r2 `fallback-designer` source value
is RETIRED, and its appearance anywhere in the map is a lint FAILURE
(S-6). Instead the SAME pinned renderer produces a degraded annotation
from the concept's own frozen-record metadata only — the kernel-v0
record's `pattern` field or the molecules-v0 record's `corpusLemmas` list,
both byte-frozen in the committed records that predate every item derived
from them — through a pinned closed template (headword + part-of-speech
frame + at most two corpus lemma names; no gloss text, no free text),
flagged `"source": "record-metadata-render"`. Deterministic and
byte-reproducible under S-7 like the primary path. Render-fallbacks are
capped at 22 of 108 (lint code S-6); a higher count HALTS before the
authoring session and escalates to the maintainer, whose resolution space
is another published synset or a programme-level redesign — never designer
prose. Every fallback annotation remains a MANDATORY unit of the
exhaustive §7.2 audit — reviewed against every provenance-touching item,
never sampled, no exemption.

**(c) Pre-item ordering (checked invariant, not prose; r3 exact chain).**
The provability argument has two legs. **Leg 1 — content (load-bearing):**
every author-visible annotation byte is a pinned deterministic function of
artifacts whose content was fixed BEFORE the first programme item existed:
the OEWN-2024 release archive (published 2024, years before the first
d-qa* item; sha-pinned) and the frozen kernel-v0/molecules-v0 record
fields (committed before any item was built from them). A pure function of
pre-item bytes cannot carry item content NO MATTER WHEN IT RUNS — the
blindness is structural, not attested, and it now covers the selection
step too, which r2 left to a post-item human. **Leg 2 — ordering (for
every FUTURE item):** the pins commit in the exact chain
`oewn-pin.json` → `select_senses.py` run (map emitted) → fidelity veto
pass (§3.3(a)3, ledgered) → `render_sense_annotations.py` run →
S-lint S-1..S-7 green → coordinator commits ALL of
{inventory sha, selector sha, map sha, renderer sha, annotations sha} —
and ONLY THEN (i) the authoring session renders its prompt and (ii) any
run of the item builder (0f0y.2) is legal. Mechanised, not promised: the
builder REQUIRES `sense_annotations_sha256` among its input pins and fails
closed without it; the store's `authoring_disclosure.sense_source` (§7.1)
carries all five shas including `selector_sha256`; the readout validator
(§7.3, RD-6) fails any readout that omits them. Stated honestly: item
families over the same 108 concepts (d-qa*, gsx0) ALREADY existed before
this contract, so ordering alone cannot make the channel blind to THOSE
items — which is exactly why leg 1 is load-bearing, and why the ONLY
post-item human input left anywhere in the channel (the capped,
published-synset-only maintainer overrides of (a)3) is disclosed, counted,
and exhaustively audited (§7.2).

The annotations remain inputs, not store content: no quality gate, but the
full S-lint (S-1..S-7, lint spec §4) and full §7.2 audit scope — including
the r3 annotation↔item pairing layer.

### 3.4 Repair loop (fail-closed, bounded)

Render → send → parse → run the FULL lint (spec §2–§3). For each failing
entry, send one repair sub-prompt (template §B) carrying only feedback codes
+ the entry's own current text. At most **3 repair rounds**; entries still
failing after round 3 **escalate to the maintainer** — Fable never edits a
definition byte (author-purity: the store must be 100% GPT-5.6-Sol text, both
for the family-attribution claim and because Fable is not blind). The
`repair_rounds` count and per-round failing-code sets are disclosed.

## 4. Vendor-disjoint seats (binding rule)

DECISION: [STIPULATED: ASM-2413] **author-family ≠ evaluator-family** is
binding for every LLM seat that evaluates this store or its consuming
experiments' outputs. Since the OpenAI family (GPT-5.6-Sol) authors:

- the blind quality gate's seats are **Claude family** (§7): Seat 1 =
  Claude Haiku 4.5 in the operationalised headless form
  (`poc/truthstyle-2x2/judges-invocation.md` §4.3 + §4.3.1); Seat 2 =
  Claude Sonnet 4.5 (`claude-sonnet-4-5-20250929`) in the same headless form
  (staging must assert the exact dated id in the init event, same tripwires;
  any rejection ⇒ escalate, never a workaround);
- any downstream LLM-judge seat in a consuming experiment (e.g. the
  endorsement leg of the 0f0y.3 head-to-head) is Claude family, with the
  Haiku form already operationalised;
- GPT-5.6/OpenAI models are DISQUALIFIED from judging plain-v5 content in
  any capacity, including the item-leak audit's contextual leak review.

**Disclosed degradation:** the prior gate's two seats were two VENDOR
families (GPT-5.6 + Haiku). With OpenAI excluded, both gate seats are Claude
family — two independent models, one vendor. Cross-family triangulation is
therefore reduced, and this is disclosed in every gate readout rather than
papered over. Restoration path: operationalise a third-family judge (e.g. a
pinned GLM-family form) and add it as a seat; until then the two-model
one-family gate is the honest maximum under the binding disjointness rule.
Note the direction of this trade is conservative for the kernel-vs-generic
question: the Claude family judging a GPT-5.6-authored generic store has no
author-flattering incentive channel, which is the channel the swap exists to
cut.

### 4.1 Normalized family map — the disjointness rule as a CHECKED INVARIANT

r1 stated author-family ≠ evaluator-family in prose and checked it only as
a string compare inside PV5-10; the review correctly held that prose plus a
string compare enforces nothing at the seats that appear LATER (downstream
judges, tie-breaks) and nothing against alias drift (`gpt-5.6-sol` vs
`GPT-5.6-Sol` vs a provider-prefixed id). DECISION: [STIPULATED: ASM-2452]
the rule is mechanised over a normalized family map:

- **Map:** `poc/plainv5/family-map.json`, schema `kot-family-map/1`,
  sha-pinned in the store disclosure (`family_map_sha256`) and in every
  consuming manifest. Normalization before matching: lowercase; strip
  region/provider envelope prefixes (`us.`/`eu.`/`apac.`, `anthropic.`/
  `openai.`/`bedrock/`/`vertex/`/`azure/`). Normalization is for family
  RESOLUTION only — every seat manifest still records the exact dated
  model id verbatim. Ordered first-match rules (normative; restated
  implementably in lint spec §7): `^claude-` → anthropic;
  `^(gpt-|o[0-9]|codex)` → openai; `^(glm|chatglm)` → zhipu;
  `^gemini-` → google; `^(llama|meta-llama)` → meta;
  `^deepseek` → deepseek; `^qwen` → alibaba;
  `^(mistral|mixtral|magistral)` → mistral; `^grok` → xai. Any unmatched
  id resolves to UNKNOWN, and **UNKNOWN FAILS CLOSED** — an unrecognized
  model can never pass as "some other family". Extending the map is a
  contract change (new sha everywhere).
- **Seat domain (exhaustive by construction):** the invariant binds EVERY
  LLM seat that touches this store or its consumers' outputs: the author;
  gate seats G-A/G-B/G-C (§6); the sense-mapping fidelity seat (§3.3);
  the contextual-leak-review seats (§7.2); the item builder's semantic
  screens (ASM-2446); every downstream judge seat in a consuming
  experiment; and every TIE-BREAK/resolution seat (judge-3-style,
  f2b-transfer precedent) — a tie-break is a seat, not an exception; and
  any seat added later. Rule, per seat s:
  `family(model(s)) ≠ family(authoring_model)` AND both resolve non-UNKNOWN.
- **Runtime SEAT LEDGER (r3 — the invariant enforced at run time, not at
  declared checkpoints) [STIPULATED: ASM-2458]:** r2 checked the ledger
  only where it was DECLARED (lint, staging, freeze, readout); a seat spun
  up between checkpoints — a mid-run tie-break, an ad-hoc re-read, an
  extra repair judge — could execute unrecorded and unchecked. r3 makes
  the ledger an APPEND-AT-INVOCATION artifact and puts the check in front
  of every dispatch:
  - **Artifact:** schema `kot-seat-ledger/1`, append-only JSONL —
    `poc/plainv5/seat-ledger.jsonl` for the store's own seats;
    `runs/<id>/seat-ledger.jsonl` per consumer run. **Entry 0 is the
    AUTHOR seat** (`seat_role: "author"`, the exact dated authoring model
    id), so every disjointness compare is against a ledger fact, never
    prose. Each entry:
    `{seq, prev_sha256, seat_role, model_id (exact dated form),
    resolved_family, family_map_sha256, prompt_sha256, invocation_form,
    output_sha256 (completed on return)}`. Entries are HASH-CHAINED
    (`prev_sha256` = sha256 of the previous entry's bytes) so an entry
    cannot be dropped, reordered, or rewritten silently; the ledger-head
    sha is the `fd_status` witness carried by RD-5.
  - **Single pinned invoker:** every LLM call in ANY seat role — gate
    G-A/G-B/G-C, sense-fidelity, CLR/annotation-audit seats, builder
    screens, downstream judges, tie-breaks — goes through
    `poc/plainv5/invoke_seat.py` (sha-pinned), which (1) resolves the
    seat's family via the pinned map, (2) evaluates
    `family(seat) ≠ family(ledger entry 0)` AND both non-UNKNOWN, BEFORE
    dispatch, (3) on FD-1/FD-2 REFUSES — the API call is never made —
    and (4) appends the ledger entry pre-dispatch, completing
    `output_sha256` post-return. Direct (non-invoker) model calls are
    banned by contract; they are caught as orphans below.
  - **Orphan detection:** verdict-gen/report-gen cross-check every raw
    seat output file against the ledger by sha. An output with no ledger
    entry, or an entry with no output, is **FD-5** — the readout is
    blocked. A broken hash chain, or a runtime ledger whose role set
    mismatches the frozen declaration (a declared role never ledgered, or
    an UNDECLARED role appearing at run time — tie-break roles must be
    declared in advance even when only conditionally invoked), is
    **FD-6**. Both fail closed and escalate.
- **Validator:** `poc/plainv5/check_family_disjoint.py`, fail-closed codes
  FD-1 (a family resolves UNKNOWN), FD-2 (family collision with the
  author), FD-3 (seat model id missing or not in the exact dated form),
  FD-4 (a consumer's declared `llm_seat_ledger` absent, or missing a seat
  role the record's own text names), FD-5 (orphan seat output / outputless
  ledger entry), FD-6 (ledger chain integrity broken, or declared-vs-
  runtime role-set mismatch). Enforcement is at EVERY INVOCATION via the
  invoker (FD-1/FD-2 pre-dispatch), plus the four checkpoints: store lint
  (PV5-10 resolves families VIA the map, never by string compare); gate
  staging (before the first judge call); consumer prereg-freeze (the
  record REQUIRES a declared `llm_seat_ledger` listing
  `{seat_role, model_id}` for every LLM seat — now the EXPECTED-role list
  the runtime ledger must match — and freeze is blocked on any FD
  nonzero); and the readout validator (§7.3, RD-5, verified against the
  hash-chained runtime ledger head).

## 5. Register lint (fail-closed; codes PV5-*)

The full mechanical contract is the companion
`docs/next/design/plain-v5-register-lint-spec.md`; summary:

| code | check | inherits |
|---|---|---|
| PV5-1 | completeness: exactly the 108 covered labels | L-1 |
| PV5-2 | LC1 own-label: neither full label nor headword token in own definition | L-2 |
| PV5-3 | word band: `LO(c) ≤ wn ≤ HI(c)` per §2 | L-3 REINSTATED |
| PV5-4 | ≥ 2 admissible claim segments (split `[.;]`, ≥15 chars, no double quotes) | L-4 REINSTATED |
| PV5-5 | pairwise distinct AND distinct from every canonical gloss | L-5 |
| PV5-6 | no-verbatim-NSM: no admissible segment substring-shared with any canonical gloss, either direction | R-1 |
| PV5-7 | register: every segment ≥1 non-NSM content token; whole-definition non-NSM ratio ≥ 0.25 | R-2 |
| PV5-8 | own-gloss token-set Jaccard < 0.5 | R-3 |
| PV5-9 | hygiene: ASCII, no double quotes, RT-14 account-string clean | R-4 |
| PV5-10 | disclosure block present, schema-valid (§7.1), families resolved via the pinned family map — UNKNOWN fails (§4.1) | D-1 extended |
| PV5-11 | **no internal repetition**: no duplicate admissible segment (normalized) and no repeated 5-gram within an entry | NEW — kills the ASM-1082 padding channel |
| PV5-12 | **definitional-register mechanicals**: lowercase-only, no digits | NEW — mechanical floor of the §2 encyclopedic bound |
| PV5-13 | **set-level frame diversity**: no leading token > 45% of entries; no leading bigram > 15% | NEW — mechanical backstop against v3-style monotony |
| PV5-14 | one-sense surface: no multi-sense enumeration markers | NEW — mechanical floor; semantic enforcement is gate G-B |
| S-1..S-7 | sense-annotation leak-lint + full deterministic-chain byte-reproducibility (selector + renderer) + render-fallback/override budgets, freehand-source ban (§3.3) | S-1..4 r1; S-5 r2; S-6 REWRITTEN + S-7 NEW r3 |

DECISION: [STIPULATED: ASM-2414] the PV5/S lint is the store's fail-closed
mechanical gate: a store that fails ANY code cannot be built into items,
gated, or pinned; the linter (`poc/plainv5/lint_plainv5_store.py`, to be
implemented verbatim from the spec at authoring time) re-runs inside any
consuming builder.

Companion fail-closed validators OUTSIDE the store lint (r2, extended r3):
FD-* family disjointness — now runtime-enforced via the seat ledger, FD-1..6
(§4.1, lint spec §7); A-CLR-* exhaustive contextual leak review + A-ANN-*
annotation↔item mechanicals (§7.2, lint spec §8); RD-* readout disclosure
(§7.3, lint spec §9). Same discipline: any nonzero blocks the step it
guards.

### 5.1 The item-builder implication (flagged, NOT solved here)

The padded store had exactly ONE concise admissible-segment set per concept
(repetition dedupes away); a natural at-band gloss has **multiple distinct
admissible segments** (PV5-4 requires ≥2; at median band ~34 words, 3–5 are
typical). Claim-segment selection, polarity substitution, LC7/LC8p
prompt-surface disjointness, and cross-arm pairing must all be redesigned
for multi-segment stores. That is `kernel-of-truth-0f0y.2` (a separate
design deliverable, named THE LONG POLE in the epic) — this contract defines
the STORE only, and no consuming experiment can freeze before 0f0y.2 lands.
[STIPULATED: ASM-2418]

## 6. Blind quality gate (two Claude seats, register + adequacy)

DECISION: [STIPULATED: ASM-2415] acceptance requires the two-seat blind gate
below — the ASM-0703 pattern that caught the v3 monotony, with the seats
swapped per §4 and the pass criteria rebuilt around **register + adequacy,
not a set-level fluency scalar**. r2 adds a THIRD read, G-C
([STIPULATED: ASM-2453], §6.4): the contextual no-extraneous-facts gate
that holds the §2 estimand.

### 6.1 Instrument fidelity (both seats, every read)

Pinned prompts + deterministic order map committed under
`poc/plainv5/gate/` before any judge call; one read per seat per round;
**first valid answer is final** (no re-rolls; ASM-0241 discipline). Blinding
grep (`kernel|nsm|knull|f2b|truthstyle|gsx|molecule|explication`) zero-hit on
every gate prompt and raw output. Seat invocations exactly as pinned: Haiku
per judges-invocation.md §4.3 + §4.3.1 with all tripwires
(`tools==[]`, `mcp_servers==[]`, `apiKeySource:"none"`, `num_turns==1`,
single text block, dated model id in init + sole modelUsage key); Sonnet
identical form with `claude-sonnet-4-5-20250929`, tripwires re-asserted at a
3-probe staging pass before first use.

### 6.2 Read G-A — blind register read (headwords withheld)

Definition texts only, pinned randomized-order map, judged as a
lexicographer. Findings are classified into HARD DEFECT CLASSES (the
maintainer's verbatim 2026-07-10 standard, operationalized, plus the two
classes this store adds):

1. register violation / improper word choice,
2. inapt word (the "most appropriate word" clause),
3. non-definitional material: consequence narration, staged observers,
   anaphoric renaming, life-lesson/literary closings,
4. **encyclopedic injection** (§2: named entities, dates, quantities,
   facts beyond a defining line),
5. **padding/repetition** (any within-entry restatement that adds no
   defining content),
6. **set-level template monotony** (a named recurring frame dominating the
   set — the v3 killer, kept as a hard class).

Word-choice NITS below the hard-class bar are reported and NON-blocking (the
v2 tally treatment). An overall-naturalness scalar (1–10) is still collected
but is **DESCRIPTIVE ONLY, never gate-bearing**: the v3→v4 record measured
the same scalar instrument moving 8→4 across re-wordings with inter-family
contradictions on the same bytes, so a scalar floor is not a stable
acceptance instrument for a control store; the ASM-0703 floor stays history
for the knull stores and does not carry here. Maintainer may re-instate a
floor at ratification — flagged, not assumed.

**Pass G-A: zero hard-defect-class findings, BOTH seats.**

### 6.3 Read G-B — adequacy read (headword + sense shown)

Separate call, separate envelope: the judge sees, per entry, the headword,
the sense annotation, and the definition, and gives a per-entry binary
verdict **adequate / inadequate** with one line of reasoning. "Adequate"
means: identifies the annotated sense and only that sense; genus +
differentiae sufficient to distinguish the headword from near neighbours; a
competent reader could pick the headword from the definition. This is the
"not just fluency" half: a beautifully written wrong or empty definition
fails here.

**Pass G-B: zero inadequate entries, BOTH seats.**

### 6.4 Read G-C — contextual no-extraneous-facts read (the estimand GATE)

r1 relied on the blind G-A class 4 plus the PV5-12 mechanicals for the §2
encyclopedic bound; the review correctly held that a BLIND read cannot
catch meaning-adjacent world knowledge — a clause can be lowercase,
digit-free, and register-clean, yet still be true-of-the-referent rather
than part of the sense (knowledge injection by paraphrase).
DECISION: [STIPULATED: ASM-2453] a third gate read, fail-closed:

Separate call, separate envelope, BOTH seats: the judge sees headword,
sense annotation, and definition, and classifies EVERY clause as
**defining** (states part of what the word means in the annotated sense:
genus, differentia, load-bearing restriction, sense contrast) or
**extraneous** (adds knowledge about the referent: facts about the world,
typical instances or examples, causes and effects, history, statistics,
evaluation, usage commentary — anything an edited dictionary's defining
line would not carry). The pinned prompt carries the operative test
verbatim: *"would removing this clause change WHAT THE WORD MEANS, or
only how much the reader knows about the thing?"*

**Pass G-C: zero extraneous clauses, BOTH seats.** Findings map to the
F-FACT feedback code (lint spec §5) and re-enter the repair loop.
Division of labour: PV5-12 is the mechanical floor (named entities, dates,
quantities); G-A class 4 catches injection visible without the headword;
G-C is the CONTEXTUAL gate that holds the estimand at "matched dictionary
content, not encyclopedic". It is a GATE, not a guideline: a store with
one surviving extraneous clause cannot be accepted, built, or pinned.

### 6.5 Gate-repair loop and acceptance

G-A/G-B/G-C findings map to feedback codes (lint spec §5) and re-enter the
§3.4 repair loop (same author, same blindness, same bounded feedback); each
repair round re-runs the FULL lint and ALL THREE gate reads on the changed
entries' round (set-level classes re-judged on the full set). At most 2
gate-repair rounds on top of the lint repairs; still-failing ⇒ maintainer
escalation. **Acceptance = lint green (all PV5/S codes) ∧ G-A pass ∧ G-B
pass ∧ G-C pass, both seats, with every round's raw outputs committed**
under `poc/plainv5/gate/` and tallied in a sha-pinned `gate-tally.json`
(itself a readout: it carries the §7.3 disclosure block).

## 7. Disclosure schema and item-leak audit

### 7.1 `authoring_disclosure` (schema `kot-plainv5-disclosure/1`)

Embedded in the store file, pinned into every consuming manifest, and
restated in every readout that reports a number derived from this store.
[STIPULATED: ASM-2416] Fields (all required, fail-closed at PV5-10):

```json
{
  "schema": "kot-plainv5-disclosure/1",
  "authoring_model": {
    "family": "OpenAI", "model": "gpt-5.6-sol",
    "client": "codex-cli <version>", "reasoning_effort": "high",
    "sandbox": "read-only, ephemeral, --ignore-user-config, empty out-of-repo workdir"
  },
  "authored_date": "<YYYY-MM-DD>",
  "authoring_prompt_sha256": "<rendered prompt bytes>",
  "transcript_sha256": "<full session incl. all repair rounds>",
  "repair_rounds": {"lint": "<n<=3>", "gate": "<n<=2>", "codes_by_round": ["..."]},
  "blindness_attestation": {
    "shown": ["headword", "sense annotation", "word band [LO,HI]",
              "authoring-facing constraint list (template section A)"],
    "withheld": ["kernel/molecule records and glosses", "QA items/skeletons",
                 "d-qa* performance data", "prior plain stores v1-v4 and padded",
                 "gate rubrics", "all project documentation"],
    "mechanism": "empty ephemeral workdir; prompt = pinned template bytes; blinding grep zero-hit (pattern list pinned)",
    "band_leak_note": "the [LO,HI] band is invertible to the canonical gloss word count; the author learns gloss LENGTH and nothing else about it",
    "feedback_leak_note": "repair feedback = enumerated codes only, full transcript pinned"
  },
  "sense_annotations": {"path": "poc/plainv5/inputs/sense-annotations.json",
                         "sha256": "<...>",
                         "provenance": "deterministic selector + metadata-only renderer per contract section 3.3 (r3); render-fallbacks and maintainer overrides flagged in sense-map; NO designer-authored line exists (fallback-designer retired)",
                         "leak_lint": "S-1..S-7 green, report sha <...>"},
  "sense_source": {"inventory": "oewn-2024",
                    "inventory_sha256": "<release archive>",
                    "selector_sha256": "<select_senses.py>",
                    "map_sha256": "<poc/plainv5/inputs/sense-map.json>",
                    "renderer_sha256": "<render_sense_annotations.py>",
                    "fallback_count": "<n<=22, source record-metadata-render>",
                    "override_count": "<n<=8, source maintainer-override, published synsets only>",
                    "fidelity_check": "claude veto-seat report sha <...>, vetoes escalated: <n>"},
  "family_map_sha256": "<poc/plainv5/family-map.json>",
  "seat_ledger": {"schema": "kot-seat-ledger/1",
                   "path": "poc/plainv5/seat-ledger.jsonl",
                   "invoker_sha256": "<invoke_seat.py>",
                   "head_sha256": "<hash-chain head at disclosure time>",
                   "entry0": "author seat, exact dated model id"},
  "evaluator_families": {"gate_seats": ["claude-haiku-4-5-20251001",
                                          "claude-sonnet-4-5-20250929"],
                          "excluded_family": "openai (author, resolved via family map)",
                          "fd_validator": "FD-1..6 green at staging AND at every ledgered invocation, report sha <...>",
                          "family_diversity_note": "two models, one vendor family - disclosed degradation per contract section 4"},
  "estimand": "matched dictionary content (genus + differentiae register) at the canonical word band - STIPULATED, not MEASURED"
}
```

### 7.2 Item-leak audit — mechanical layer + EXHAUSTIVE contextual leak review (independent, non-authoring, pre-freeze in every consumer)

Before any consuming experiment freezes, an independent audit (never the
author family; mechanical part role-run by the coordinator/runner, semantic
part Claude-family seats per the §4.1 map) executes BOTH layers:

**Layer 1 — mechanical (string-level) [STIPULATED: ASM-2417; annotation
mechanicals r3, ASM-2457]:** re-run PV5-2 (LC1), PV5-5 (uniqueness), PV5-8
(Jaccard) against the FINAL built item files; plus cross-concept leakage:
no definition shares a ≥6-gram with any OTHER concept's item answer text or
stem, and token-set Jaccard(definition of X, answer text of any item about
Y≠X) < 0.5. Licensed channels are exactly the ASM-2447 set (A
own-definition, B donor-claim, C distractor-definition), exempt by
construction and NAMED per hit in the audit report.

r3 adds the ANNOTATION↔ITEM mechanicals — r2 string-checked definitions
against items but never the annotations the author actually read (codes
A-ANN-*, lint spec §8, all fail-closed):

- **A-ANN-MAP** — the committed `sense-map.json` AND
  `sense-annotations.json` byte-equal a fresh audit-side re-run of the
  pinned selector + renderer from the pinned inventory and records
  (S-7 re-asserted by the AUDITOR, not the store side): a post-hoc hand
  edit to steer an annotation toward an item cannot survive.
- **A-ANN-NGRAM** — no ≥4-gram of any annotation's tokens occurs in any
  item's stem or answer text, ANY concept, both directions (4, not 6:
  annotations are ≤15 words, so their leak quantum is smaller).
- **A-ANN-JACCARD** — token-set Jaccard(annotation, answer text of any
  item) < 0.3 for every (annotation, item) pair in the built set.

Annotations have NO licensed channels: the ASM-2447 exemptions license
definition content only, so every A-ANN hit is a finding — there is no
"licensed-only" disposition for an annotation.

**Layer 2 — contextual leak review (CLR; exhaustive, supersedes the r1
k=12 sampled spot-check) [STIPULATED: ASM-2451]:** string checks cannot
see a paraphrase or an implication, and a sampled spot-check certifies
only the sample. The review's requirement is adopted verbatim: a gloss
must not encode an item answer via paraphrase or implication, checked
CONTEXTUALLY and EXHAUSTIVELY:

- **Unit of review:** every (item, touching-definition) pair in the
  consumer's final built set — the item's own concept's definition plus
  every donor/distractor concept's definition its surface touches per the
  builder's pinned provenance (claim_source, option coordinates) — AND
  (r3, ASM-2457) every (item, touching-ANNOTATION) pair: the sense
  annotation of every concept the item's provenance touches in ANY role
  (own, donor, distractor), not merely items over the annotation's own
  concept as in r2 — an annotation can leak into an item it serves as
  donor or distractor for just as a definition can. Render-fallback and
  maintainer-override annotations (§3.3) are mandatory units. Nothing is
  sampled; a coverage check (A-CLR-COVERAGE, lint spec §8) fails the audit
  if any provenance-derivable pair — definition OR annotation — lacks a
  verdict.
- **Seat + form:** Claude-family seats per the §4.1 map (FD-checked),
  pinned prompt bytes, pinned order map, one read per unit, first valid
  answer final (ASM-0241: findings are never waived by re-rolling);
  blinding grep on every prompt and raw output as in §6.1.
- **Probe P1 — answerability:** the seat receives the definition text(s)
  and the item stem/options WITHOUT the key, and must attempt the item
  using ONLY the definition content. Keyed-answer recovery outside a
  licensed channel is a leak.
- **Probe P2 — implication:** the seat receives item + key + definitions
  and answers the pinned question: does any definition text — by
  paraphrase, implication, or entailment — determine or materially raise
  the probability of the keyed answer BEYOND what a correct dictionary
  definition of that concept licenses? Verdict ∈ {no-leak, licensed-only,
  leak}, one line of reasoning.
- **Probes P1a/P2a — annotation pairing (r3, ASM-2457):** the same two
  probes run with the ANNOTATION as the conditioning document. P1a: the
  seat receives ONLY the sense annotation text(s) the item's provenance
  touches, plus the item stem/options WITHOUT the key, and attempts the
  item — ANY keyed-answer recovery is a leak, full stop: annotations have
  no licensed channels, so P1a has no exemption clause. P2a: the seat
  receives item + key + annotation(s) and answers the pinned question:
  does any annotation — by encoding, paraphrase, implication, or
  correlation of its surface choices — determine or materially raise the
  probability of the keyed answer BEYOND bare identification of the
  intended sense? Verdict ∈ {no-leak, leak} only (no licensed-only
  disposition exists for annotations); one line of reasoning.
- **Adjudication (fail-closed):** any P2 `leak`, any P2a `leak`, any P1a
  recovery, or P1 recovery outside a licensed channel, is a finding
  `A-CLR-LEAK` ⇒ audit FAIL ⇒ freeze blocked ⇒ maintainer escalation. A
  `licensed-only` verdict (definitions only) must name its ASM-2447
  channel; one that matches no pinned channel is `A-CLR-CHANNEL` and
  escalates — the audit exempts exactly the pinned channels and nothing
  else, and never exempts an annotation.
- **Cost bound (why exhaustive is affordable):** units = O(items ×
  touching definitions) + O(items × touching annotations) — annotations
  are ≤15 words, so the P1a/P2a units are the cheap half — low thousands
  of subscription judge calls, no GPU. The audit report disclosed counts:
  definition units and annotation units enumerated/reviewed, findings by
  code, licensed hits by channel, A-ANN-* results, and the verbatim
  P1/P2/P1a/P2a prompt shas. All audit seats are invoked through the §4.1
  ledger (FD-5 catches any that are not).

### 7.3 Readout-level disclosure validator (fail-closed; codes RD-*)

r1's "restated in every readout" (§7.1) was prose with no enforcement — a
readout could silently drop the provenance and nothing would catch it.
DECISION: [STIPULATED: ASM-2454] every readout artifact (markdown or JSON)
that reports ANY number derived from this store — gate tallies, audit
reports, consumer analyses, interpretations — MUST embed a
machine-checkable disclosure block, and
`poc/plainv5/validate_readout_disclosure.py` FAILS CLOSED (nonzero exit)
on absence or mismatch:

- **Required block:** a fenced JSON block with
  `"schema": "kot-plainv5-readout-disclosure/1"` carrying:
  `authoring_model {family, model}`, `authored_date`,
  `authoring_prompt_sha256`, `transcript_sha256`,
  `item_blindness {sense_source (inventory + selector + map + renderer
  shas), fallback_count, override_count,
  clr_status ∈ {"green:<report sha>", "not-yet-run"}}`,
  `family_disjointness {family_map_sha256, fd_status:
  "green:<runtime seat-ledger HEAD sha>"}`. All shas full 64-hex,
  byte-checked against the pinned store disclosure.
- **Codes:** RD-1 block missing; RD-2 schema tag wrong; RD-3 required
  field missing or empty; RD-4 any sha mismatching the pinned store
  disclosure; RD-5 `fd_status` not green against the consumer's
  hash-chained RUNTIME seat ledger (chain verified head-to-entry-0;
  FD-5/FD-6 clean — a declared-only ledger no longer satisfies RD-5);
  RD-6 item-blindness fields missing — or `clr_status`
  "not-yet-run" on a readout reporting consumer results (store-only
  readouts produced before any consumer exists may carry "not-yet-run";
  anything reporting an experiment number may not).
- **Enforcement points:** the consumer's report-gen/verdict-gen pipeline
  runs the validator before any readout is committed; the consumer prereg
  carries the verbatim clause "no readout is publishable with RD nonzero";
  the gate tally (§6.5) is itself a readout and carries the block; the
  analyst role's checklist cites this section.

## 8. Scope, reuse, and the deflation-honesty note

DECISION: [STIPULATED: ASM-2419] scope of THIS store: the **108 covered
concepts** (54 kernel-v0 glosses + 54 molecules-v0 grounding notes), current
store coverage. The contract — not the store — is what the f1k-successor d2
and large-kernel variants reuse later: same authoring/blindness/lint/gate/
disclosure machinery re-instantiated over their concept sets with fresh
bands, fresh sense annotations, and fresh gate runs. Nothing in this
document licenses reuse of the 108 authored texts outside their band-matched
setting.

**Deflation honesty (said out loud, by design):** knull-v2 is already NULL —
the kernel arm did not beat even the DEGENERATE padded generic beyond
±0.05. A first-rate natural generic at the same token budget is a strictly
stronger opponent, so every future kernel-vs-generic reading that uses this
store is pushed MORE deflationary: kernel equivalence to plain-v5-natural
relabels the lift "generic dictionary content + retry", and a kernel WIN
over plain-v5-natural is a materially stronger content claim than a win over
the padded arm would have been. **That raises the kernel's bar by design** —
the advisory's point is precisely that the previous bar was too low in the
kernel's favour (anti-conservative). A PASS-CONTENT against this store is
worth having; a NULL against it is more informative than the padded NULL.
Both directions are honest outcomes; neither is softened.

## 9. Execution plan (for the coordinator; nothing executed here)

1. Coordinator review of this contract + companions; maintainer ratifies the
   §6.2 scalar-demotion choice (ASM-2415 resolution path) or amends.
2. Coordinator pins the OEWN release archive (`oewn-pin.json`), the
   family map (`family-map.json`), and implements-then-pins the two r3
   scripts from their contract-fixed specs: `select_senses.py` (§3.3(a)2)
   and `invoke_seat.py` (§4.1). The selector RUNS and emits
   `sense-map.json` — no hand authoring. ($0)
3. Fidelity VETO pass: Claude seat (through the ledgered invoker) checks
   every selector output against the canonical gloss (§3.3(a)3); vetoes
   to maintainer; overrides published-synset-only, ≤8, counted.
   (subscription claude calls, ≈$0)
4. Deterministic render of `sense-annotations.json` (record-metadata
   fallbacks included); S-1..S-7 lint (S-7 = full-chain byte
   reproduction); coordinator commits ALL FIVE sense-source pins
   (inventory, selector, map, renderer, annotations) — the §3.3(c)
   pre-item ordering point. ($0)
5. Coordinator (or runner role) renders the prompt, runs the blinding grep,
   opens the seat ledger with ENTRY 0 = the author seat, then executes the
   GPT-5.6-Sol authoring session + lint/repair loop per §3.
   (subscription codex calls, ≈$0, no GPU)
6. FD staging run (`check_family_disjoint.py` over the declared seats,
   §4.1), Sonnet-seat staging probes (3), then the §6 gate — reads G-A,
   G-B, G-C, every call through `invoke_seat.py` (FD-1/FD-2 pre-dispatch;
   FD-5 orphan sweep after each round); gate tally carries the §7.3
   disclosure block and passes the RD validator. (subscription claude
   calls, ≈$0)
7. Item-leak audit prerequisites wait on `kernel-of-truth-0f0y.2`
   (item-builder v5); the §7.2 audit — mechanical layer incl. A-ANN-* +
   EXHAUSTIVE CLR incl. P1a/P2a annotation-pairing probes — runs inside
   the 0f0y.3 consumer's pre-freeze gates, over the consumer's full built
   set, every touching definition, and every touching annotation.
8. Store + evidence committed; consuming experiment (0f0y.3) pins
   `store sha256`, disclosure, family-map sha, invoker sha, gate tally,
   declared + runtime seat ledgers (hash-chain head), and audit report in
   its record; every consumer readout passes the §7.3 RD validator
   (RD-5 against the runtime ledger) before commit.

## 10. Self-check gate (mandatory)

- Every design choice above is tagged STIPULATED with a registered ASM-id
  (ASM-2410..2419 r1; ASM-2450..2454 r2; ASM-2456..2458 r3); every number
  is MEASURED with its artifact or is band arithmetic. Checked.
- Re-review-HOLD closure map (r3): route 1 → §3.3/ASM-2456 (deterministic
  selector over pre-item OEWN-2024 + frozen-record metadata; veto-only
  fidelity seat; freehand fallback RETIRED as lint failure S-6; full-chain
  byte-reproducibility S-7; overrides published-synset-only, ≤8, audited);
  route 2 → §7.2/ASM-2457 (annotation↔item pairing audited: A-ANN-MAP/
  NGRAM/JACCARD mechanicals + P1a/P2a CLR probes, zero licensed channels
  for annotations, coverage over own/donor/distractor roles, counted by
  A-CLR-COVERAGE); route 3 → §4.1/ASM-2458 (runtime append-only
  hash-chained seat ledger kot-seat-ledger/1, author = entry 0, single
  pinned invoker refusing FD-1/FD-2 pre-dispatch, FD-5 orphan + FD-6
  chain/role-set codes, RD-5 rebound to the runtime ledger head).
  Residual-route check: with selection and rendering pure functions of
  pre-item bytes, the only human input left in the author's view is the
  capped audited override set; with annotations first-class audit units
  in every provenance role and no licensed channel, no annotation↔item
  correlation goes unexamined; with the invariant evaluated before every
  dispatch and every output required to trace to a chained ledger entry,
  no evaluator seat can run same-family or unrecorded. No further
  leakage / knowledge-conditioning / circularity route identified at r3;
  anything later discovered is a contract version change, not a waiver.
  Checked.
- Review-HOLD closure map (r2): gap 1 → §3.3/ASM-2450 (item-blind OEWN
  source + checked pre-item ordering); gap 2 → §7.2/ASM-2451 (exhaustive
  CLR, P1 answerability + P2 implication, coverage-checked); gap 3 →
  §4.1/ASM-2452 (normalized family map, FD-* validator, tie-break seats in
  scope, UNKNOWN fails closed); gap 4 → §6.4/ASM-2453 (G-C contextual
  extraneous-facts GATE in the acceptance formula); gap 5 → §7.3/ASM-2454
  (RD-* readout disclosure validator, fail-closed). Checked.
- Pseudonyms only (Fable, kern/fable-designer, GPT-5.6-Sol, coordinator,
  maintainer, designer-1); RT-14 pattern list clean over this doc and both
  companions. Checked.
- ASM block disjointness: ASM-2410–2419 disjoint at r1 (highest then in use
  ASM-2406); ASM-2450–2454 disjoint at r2 (grep over registry/ and docs/,
  2026-07-16 — highest registered id ASM-2449; the sole higher-numbered
  string in the tree is a stylistic citation in an unrelated uncommitted
  draft, not a registered entry); ASM-2456–2458 disjoint at r3 (grep over
  registry/, docs/, tools/, poc/, kb/, 2026-07-16 — highest registered id
  ASM-2455, the F1-K round-10 entry; no id ≥ 2456 anywhere in the tree).
  Checked.
- No frozen object touched: registry/experiments/{knull,knull-v2,gsx0,f1k*}
  byte-untouched; no store authored; no GPU; no experiment record created or
  modified. Checked.
- The authoring-prompt template contains zero hits on the blinding grep
  pattern list (unchanged at r2 — the G-C bound was already in the
  template's STYLE clause; r2 adds enforcement, not prompt bytes). Checked.
- `python3 tools/registry/registry-check.py` PASS after the register append
  (run in-session; result in the session report). Checked.

## Registered ASM block (verbatim summaries; full entries in registry/assumptions.jsonl)

- **ASM-2410 [STIPULATED]** issue-44 "1 + 2A" adoption: GPT-5.6-Sol authors
  plain-v5-natural; all LLM evaluator seats move to the Claude family.
- **ASM-2411 [STIPULATED]** estimand + band: matched dictionary content at
  the reinstated L-3 authoring band; STIPULATED-not-MEASURED strength claim.
- **ASM-2412 [STIPULATED]** authoring protocol: one blind batched session,
  pinned prompt/transcript, ≤3 leakage-bounded repair rounds, no designer
  edits.
- **ASM-2413 [STIPULATED]** vendor-disjoint seat rule (binding) + disclosed
  two-model/one-family gate degradation + restoration path.
- **ASM-2414 [STIPULATED]** PV5/S register-lint contract, fail-closed.
- **ASM-2415 [STIPULATED]** gate protocol: G-A zero hard-defect classes +
  G-B zero inadequate, both Claude seats; naturalness scalar demoted to
  descriptive (maintainer ratification path recorded).
- **ASM-2416 [STIPULATED]** disclosure schema kot-plainv5-disclosure/1 rides
  the store, every consuming manifest, and every readout.
- **ASM-2417 [STIPULATED]** independent item-leak audit contract, mechanical
  layer, freeze-blocking in every consumer (its r1 sampled semantic
  spot-check clause superseded by ASM-2451's exhaustive CLR).
- **ASM-2418 [STIPULATED]** item-builder v5 is a SEPARATE deliverable
  (0f0y.2); no consumer freezes before it lands.
- **ASM-2419 [STIPULATED]** scope 108 concepts; contract (not text) reuse
  for d2/large-kernel; deflation-honesty direction disclosed.
- **ASM-2450 [STIPULATED]** (r2, gap 1) item-blind sense source: OEWN-2024
  pinned inventory + capacity-bounded synset map + independent fidelity
  check + deterministic metadata-only render (S-5), capped disclosed
  fallback channel (S-6), checked pre-item ordering invariant.
- **ASM-2451 [STIPULATED]** (r2, gap 2) exhaustive contextual leak review
  (CLR): every (item, touching-definition) pair + all 108 annotations,
  P1 answerability + P2 implication probes, A-CLR-* fail-closed codes,
  coverage-checked; supersedes the r1 k=12 sampled spot-check clause of
  ASM-2417 (mechanical layer unchanged).
- **ASM-2452 [STIPULATED]** (r2, gap 3) normalized family map
  (kot-family-map/1) + FD-* disjointness validator at every LLM seat —
  author, gate, screens, judges, TIE-BREAKS — UNKNOWN fails closed;
  tightens ASM-2413 from prose to checked invariant.
- **ASM-2453 [STIPULATED]** (r2, gap 4) gate read G-C: contextual
  per-clause defining/extraneous classification, zero-extraneous pass both
  seats, in the acceptance formula; extends ASM-2415.
- **ASM-2454 [STIPULATED]** (r2, gap 5) readout-level disclosure validator
  RD-1..RD-6, fail-closed on any readout deriving a number from this
  store; extends ASM-2416 from prose to enforcement.
- **ASM-2456 [STIPULATED]** (r3, route 1) provably item-blind sense
  inputs: sense selection is a pinned deterministic function
  (`select_senses.py`: extended-Lesk argmax, lexicographic tie-break) of
  the OEWN-2024 archive + frozen concept-record fields, both fixed before
  any programme item; fidelity seat veto-only; maintainer overrides
  published-synset-only, ≤8, disclosed, audited; `fallback-designer`
  RETIRED (lint failure), replaced by the deterministic
  record-metadata render (≤22); full-chain byte-reproducibility S-7;
  exact five-pin pre-item ordering chain. Tightens ASM-2450.
- **ASM-2457 [STIPULATED]** (r3, route 2) annotation↔item pairing audit:
  mechanical A-ANN-MAP (audit-side selector/renderer byte re-run),
  A-ANN-NGRAM (≥4-gram vs any item stem/answer), A-ANN-JACCARD (<0.3 vs
  any answer text); CLR probes P1a (answerability from annotation alone —
  any recovery is a leak) and P2a (encoding/implication/correlation
  beyond bare sense identification); annotations have ZERO licensed
  channels; units enumerated over every provenance-touching role
  (own/donor/distractor), coverage-checked. Extends ASM-2451/ASM-2417.
- **ASM-2458 [STIPULATED]** (r3, route 3) runtime seat ledger
  `kot-seat-ledger/1`: append-only, hash-chained, author = entry 0;
  single pinned invoker `invoke_seat.py` resolves family and evaluates
  the disjointness invariant BEFORE dispatch (refuses on FD-1/FD-2);
  FD-5 orphan-output and FD-6 chain/role-set integrity codes; declared
  `llm_seat_ledger` becomes the expected-role list the runtime ledger
  must match; RD-5 rebound to the runtime ledger head. Tightens
  ASM-2452 from checkpoint enforcement to per-invocation enforcement.
