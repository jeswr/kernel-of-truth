# plain-v5-natural — register-lint SPEC (codes PV5-1..PV5-14, S-1..S-7, F-*; companion validators FD-*, A-CLR-*, A-ANN-*, RD-*)

> **Status: [EXP-DESIGN] companion to
> `docs/next/design/plain-v5-natural-store-contract.md` (maintainer decision
> issue 44, epic kernel-of-truth-0f0y.1). Author: Fable (kern/fable-designer),
> 2026-07-16. This file is the IMPLEMENTABLE contract for
> `poc/plainv5/lint_plainv5_store.py` — to be implemented verbatim at
> authoring time and re-run inside every consuming builder. Fail-closed:
> any failing code blocks build, gate, and pin. Design only; no linter is
> implemented or run by this deliverable. [STIPULATED: ASM-2414]**
>
> **REVISION r2 (2026-07-16):** closes the cross-model review HOLD gaps at
> the spec level: S-5/S-6 (item-blind sense-source reproducibility +
> fallback budget, ASM-2450), PV5-10 family resolution via the pinned
> family map, new §7 family-map + FD-* disjointness validator (ASM-2452),
> new §8 exhaustive contextual leak review A-CLR-* (ASM-2451), new §9
> readout disclosure validator RD-* (ASM-2454), F-FACT feedback code for
> the G-C gate (ASM-2453).
>
> **REVISION r3 (2026-07-16):** closes the r2 re-review HOLD at the spec
> level: §4 inputs gain the pinned deterministic selector
> `select_senses.py`; S-6 REWRITTEN (freehand `fallback-designer` banned;
> `record-metadata-render` ≤22 + `maintainer-override` ≤8); S-7 NEW
> (full-chain byte-reproducibility of map + annotations from the pins)
> (ASM-2456). §7 gains the runtime seat ledger `kot-seat-ledger/1` +
> pinned invoker `invoke_seat.py` + FD-5/FD-6 (ASM-2458). §8 gains the
> annotation↔item mechanicals A-ANN-* and the P1a/P2a pairing probes with
> zero licensed channels for annotations (ASM-2457). §9 RD-3/RD-5 field
> updates (selector sha, override count, runtime-ledger head).

## 1. Inputs and shared definitions

- **Store file:** `poc/plainv5/store/plain-v5-natural.json`, schema
  `kot-plainv5-store/1`, top-level fields `schema`, `version` (semver,
  starts 5.0.0), `line`, `design_doc`, `lint_spec`, `authoring_disclosure`
  (contract §7.1), `sense_annotations_sha256`, `definitions`
  (object, label → definition text).
- **Canonical glosses:** for the 54 kernel-v0 concepts, the `gloss` field of
  `data/kernel-v0/concepts/<label>.json`; for the 54 molecules-v0 concepts,
  the `groundingNote` field of `data/molecules-v0/molecules/<label>.json`.
  The covered-label set (exactly 108) and the per-concept canonical text are
  resolved the same way as the pinned knull G-1 linter
  (`poc/knull/lint_plain_store.py`) — reuse its loader semantics verbatim.
- **word count** `wc(text)`: `len(text.split())` (whitespace split — the
  L-3/ASM-1082 convention, unchanged).
- **normalization** `norm(text)`: casefold; collapse whitespace; strip
  leading/trailing space (the pinned linter's normalization, reused).
- **admissible segment:** split the definition on `[.;]`; keep segments
  whose stripped text is ≥ 15 characters and contains no double-quote
  character (the build-dqa/build-dqar claim-item contract, unchanged).
- **tokens** `toks(text)`: lowercase alphabetic tokens `[a-z]+` (the pinned
  linter's TOKEN_RE).
- **n-gram:** an n-tuple of consecutive `toks`.
- **NSM-legal surface vocabulary:** exactly the pinned linter's set (65
  profile-1 prime exponents + inflections, closed function words, plus the
  108 concept headwords added at runtime). Reuse, do not re-type.
- **RT-14:** the account-string pattern list of
  `tools/registry/kot_common.require_no_account_strings`.

Error-code convention: the linter exits nonzero and prints one line per
finding, `FAIL PV5_ERR_<CODE> <label>: <detail>`; `--report` writes a JSON
per-check summary (`g1-lint-report.json` shape) to
`poc/plainv5/store/pv5-lint-report.json`.

## 2. Store checks (per entry unless noted)

**PV5-1 completeness (set-level).** `definitions` keys == the 108 covered
labels exactly; no missing, no extras. `PV5_ERR_COVERAGE`.

**PV5-2 LC1 own-label.** Neither the full label nor its headword (first
whitespace token of the label) occurs as a `toks` word in the entry — the
STRICT form of the pinned linter (full label AND headword). The authoring
prompt additionally instructs "no form of the headword", but the LINT bound
is exact-token, matching the pinned contract so cross-arm LC1 semantics stay
identical. `PV5_ERR_LC1`.

**PV5-3 word band (the reinstated L-3).** With `wc` = word count of the
concept's canonical gloss and `wn` = word count of the entry:
`ceil(0.75*wc) <= wn <= max(floor(1.25*wc), wc+8)`. `PV5_ERR_BAND`.

**PV5-4 segments (the reinstated L-4).** ≥ 2 admissible segments.
`PV5_ERR_SEGMENTS`.

**PV5-5 uniqueness (set-level).** All 108 normalized entries pairwise
distinct AND distinct from every normalized canonical gloss.
`PV5_ERR_UNIQUE`.

**PV5-6 no-verbatim-NSM.** No normalized admissible segment of any entry
occurs as a substring of ANY normalized canonical gloss, and no normalized
canonical-gloss segment occurs as a substring of any entry (both directions;
the attack-9 check, unchanged). `PV5_ERR_NSM_VERBATIM`.

**PV5-7 register.** Every admissible segment contains ≥ 1 content token
outside the NSM-legal surface vocabulary, AND the whole-entry non-NSM
content ratio ≥ 0.25 (REGISTER_RATIO_MIN, unchanged — canonical NSM glosses
score ~0.0–0.1 by construction). `PV5_ERR_REGISTER`.

**PV5-8 own-gloss overlap.** Token-set Jaccard(entry, own canonical gloss)
< 0.5. `PV5_ERR_JACCARD`.

**PV5-9 hygiene.** ASCII only; no double-quote characters; RT-14 clean.
`PV5_ERR_HYGIENE`.

**PV5-10 disclosure.** `authoring_disclosure` present, schema
`kot-plainv5-disclosure/1`, ALL fields of contract §7.1 present and
non-empty (r2: including `sense_source` and `family_map_sha256`).
Family disjointness is resolved VIA the pinned family map (§7 below) —
`family(authoring_model.model)` and `family(m)` for every model id in
`evaluator_families.gate_seats` must all resolve non-UNKNOWN and the
author's family must differ from each seat's. Never a string compare,
never a default-pass: an UNKNOWN resolution is itself a failure.
`PV5_ERR_DISCLOSURE`.

**PV5-11 no internal repetition (NEW — the anti-ASM-1082 clause).**
Within one entry: (a) no two admissible segments are equal after `norm`;
(b) no 5-gram of `toks(entry)` occurs twice. Rationale: (a) kills verbatim
whole-segment padding, (b) kills sub-segment cyclic padding and verbatim
restatement; 5 was chosen over 6 to also catch clause-internal recycling
while leaving room for natural function-word recurrence (function words are
in `toks`, but a repeated 5-gram of them is already mechanical prose).
`PV5_ERR_REPEAT`.

**PV5-12 definitional-register mechanicals (NEW).** The entry contains no
uppercase letters (lowercase-only — mechanically bans named entities in
edited-dictionary defining style) and no digit characters (bans dates,
quantities, numbered senses). This is the MECHANICAL floor of the contract
§2 encyclopedic bound; the semantic remainder is gate class 4.
`PV5_ERR_ENCYC`.

**PV5-13 set-level frame diversity (NEW, set-level).** Over the 108
entries: (a) no single first token of `toks(entry)` accounts for > 45% of
entries; (b) no single first-two-token bigram accounts for > 15% of
entries. Calibration note: threshold (a) is deliberately loose because
noun-heavy sets legitimately open with an article; (b) is the operative
monotony backstop. These are BACKSTOPS — the primary set-level monotony
instrument is gate class 6 — so a near-miss here is a real authoring defect,
not instrument noise. `PV5_ERR_MONOTONY`.

**PV5-14 one-sense surface (NEW).** The entry contains none of the
multi-sense enumeration surface markers: the substrings `also :`/`also:`,
` or , as a separate sense`, sense-numbering (impossible anyway under
PV5-12's digit ban), or the pattern `; (as ` opening a re-sensing
parenthetical. Semantic one-sense enforcement is gate G-B; this code only
stops the mechanical forms. `PV5_ERR_MULTISENSE`.

## 3. Ordering and reporting

Run order: PV5-1 first (fail-closed on coverage before per-entry checks),
then per-entry checks in code order, then set-level PV5-5/PV5-13. ALL checks
run to completion (no short-circuit after the first failure) so one repair
round can carry the complete failing-code set. The report JSON carries, per
code: pass/fail, count, per-label details, and the thresholds used — the
thresholds are part of the pinned contract; changing ANY threshold is a
store-contract version change (bump the store schema, re-run the full gate).

## 4. Sense-annotation lint (codes S-*; runs BEFORE the authoring session)

Inputs (r3, all FIVE sha-pinned together — the contract §3.3(c) pre-item
ordering point): `poc/plainv5/inputs/oewn-pin.json` (inventory archive
pin), `poc/plainv5/inputs/select_senses.py` (deterministic selector —
extended-Lesk argmax over the headword's OEWN synsets vs the canonical
gloss, lexicographic-synset-id tie-break; contract §3.3(a)2),
`poc/plainv5/inputs/sense-map.json` (SELECTOR OUTPUT, never hand-written),
`poc/plainv5/inputs/render_sense_annotations.py` (deterministic renderer),
`poc/plainv5/inputs/sense-annotations.json` (rendered output).

**S-1 shape.** Exactly the 108 covered labels; each annotation ≤ 15 words,
lowercase ASCII, no digits, no double quotes; RT-14 clean. `PV5_ERR_S_SHAPE`.

**S-2 no gloss verbatim.** No 4-gram of `toks(annotation)` occurs in
`toks` of ANY canonical gloss. `PV5_ERR_S_VERBATIM`.

**S-3 own-gloss overlap.** Token-set Jaccard(annotation, own canonical
gloss) < 0.3 (tighter than PV5-8: the annotation is shown to the author, so
its leak budget is smaller). `PV5_ERR_S_JACCARD`.

**S-4 sense-pointing only.** The annotation may contain the headword and
ordinary disambiguating English (e.g. part-of-speech words, "the ... not
the ..." contrasts); it must not contain a candidate definition — proxy
bound: the annotation shares no admissible segment (≥15 chars) with the
authored entry once the store exists (re-checked post-authoring), and no
4-gram with the authored entry. `PV5_ERR_S_DEFINES`.

**S-5 render reproducibility (r2; ASM-2450).** For every concept with
`source ∈ {"oewn-selector", "maintainer-override"}`: the annotation
byte-equals a fresh deterministic re-render from (pinned inventory archive,
pinned map entry, pinned renderer), run by the linter itself; AND the
renderer consumed synset METADATA only — asserted two ways: (a) the
renderer's pinned source reads no gloss/definition field of the inventory
record (code-level assertion at pin time), (b) no 4-gram of
`toks(annotation)` occurs in `toks` of the mapped synset's OEWN definition
text (output-level assertion, every entry). For
`source == "record-metadata-render"` entries: byte-equal re-render from
the pinned template over the concept's frozen-record fields (kernel
`pattern` / molecule `corpusLemmas`), same assertions with the record in
place of the synset. `PV5_ERR_S_SOURCE`.

**S-6 source budget + freehand ban (REWRITTEN r3; ASM-2456).** Every
`source` value ∈ {`oewn-selector`, `maintainer-override`,
`record-metadata-render`} — ANY other value, including the retired r1/r2
`fallback-designer`, is an immediate FAIL (the freehand channel no longer
exists). Count of `record-metadata-render` entries ≤ 22 (of 108); count of
`maintainer-override` entries ≤ 8, each carrying a published `synset_id`
from the pinned inventory plus a non-empty `justification`; the report
lists both label sets verbatim — they are mandatory-coverage subsets of
the §8 review. Exceeding either cap HALTS before the authoring session and
escalates to the maintainer. `PV5_ERR_S_FALLBACK`.

**S-7 full-chain byte-reproducibility (NEW r3; ASM-2456).** The linter
re-RUNS the pinned selector from (pinned inventory archive, canonical
glosses) and asserts the committed `sense-map.json` byte-equals the re-run
output on every `source == "oewn-selector"` entry (override and
record-metadata entries are excluded from the equality but counted by
S-6); then asserts the committed `sense-annotations.json` byte-equals the
full re-render. No hand edit to the map or the annotations can survive
this code; the §8 audit re-asserts the same property audit-side
(A-ANN-MAP), so the store side cannot self-certify. `PV5_ERR_S_CHAIN`.

## 5. Feedback codes (the ONLY authoring-visible lint surface; contract §3.4)

Repair prompts to the blind author may carry, per failing entry, ONLY the
entry's own current text plus lines drawn from this enumerated table —
never quoted canonical-gloss text, never item text, never another store's
text. Every rendered repair prompt is part of the pinned transcript.

| feedback code | rendered line (exact template) | triggered by |
|---|---|---|
| F-BAND | `your entry has {n} words; it must have between {LO} and {HI} words` | PV5-3 |
| F-SEG | `your entry needs at least two clauses, separated by ";" or ".", each at least 15 characters long` | PV5-4 |
| F-SELF | `your entry uses the headword or a form of it; remove every occurrence` | PV5-2 |
| F-REP | `your entry repeats itself; remove the repetition and add new defining content instead` | PV5-11 |
| F-DUP | `your entry is too close to your entry for "{other headword}"; make them clearly distinct` | PV5-5 |
| F-RES | `clause {k} of your entry coincides with a reserved phrase set; rephrase that clause in different words with the same meaning` | PV5-6 |
| F-OVL | `your entry's overall wording is too close to a reserved text; rephrase using different vocabulary` | PV5-8 |
| F-REG | `clause {k} of your entry needs at least one more specific content word` | PV5-7 |
| F-HYG | `use lowercase ascii letters only; no digits; no double quotes` | PV5-9, PV5-12 |
| F-ONE | `your entry must define exactly the one sense given in the sense note` | PV5-14, gate G-B |
| F-DEF | `clause {k} of your entry does not state what the word means; replace it with a defining property of the sense` | gate G-A classes 3–5 |
| F-FACT | `clause {k} adds knowledge about the thing rather than stating what the word means; replace it with a defining property of the sense` | gate G-C (contract §6.4) |
| F-APT | `clause {k} contains a word that is not the most apt word for its place; choose a better one` | gate G-A classes 1–2 |
| F-VAR | `too many of your entries open the same way; vary the shapes of the entries named below` | PV5-13, gate G-A class 6 |

Leak accounting: F-RES/F-OVL each leak ≤ 1 bit per use about the canonical
gloss ("your natural phrasing collides with it"); the bounded round count
(≤ 3 lint + ≤ 2 gate) caps the channel, and the pinned transcript makes the
realized leakage inspectable byte-for-byte. [STIPULATED: ASM-2412]

## 6. Sense-map fidelity check (gate-side seat; contract §3.3(a)3)

Not a lint code (it is an LLM read, so it lives with the gate discipline
and runs through the §7 ledgered invoker): before S-5/S-7 rendering is
accepted, a Claude-family seat (family map §7; pinned headless form, one
read per concept, first-valid-final) is shown headword + canonical gloss +
the FULL candidate synset list rendered from the pinned inventory, and
answers whether the SELECTOR'S synset (r3: the seat verifies, never
chooses) is the sense of the canonical gloss. A veto ⇒ escalate to the
maintainer, whose only override is another PUBLISHED synset of the same
headword (`source: "maintainer-override"`, S-6 cap 8) — never free text;
Fable never adjudicates or overrides. The per-concept verdicts and prompt
shas land in a committed `poc/plainv5/inputs/sense-map-fidelity.json`,
whose sha rides `authoring_disclosure.sense_source.fidelity_check`.

## 7. Normalized family map + disjointness validator (codes FD-*; ASM-2452)

**Map file:** `poc/plainv5/family-map.json`, schema `kot-family-map/1`:

```json
{
  "schema": "kot-family-map/1",
  "normalize": ["lowercase",
                 "strip-prefix-regex: ^(us|eu|apac)\\.",
                 "strip-prefix-regex: ^(anthropic|openai|bedrock|vertex|azure)[./]"],
  "rules": [
    {"match": "^claude-",                 "family": "anthropic"},
    {"match": "^(gpt-|o[0-9]|codex)",     "family": "openai"},
    {"match": "^(glm|chatglm)",           "family": "zhipu"},
    {"match": "^gemini-",                 "family": "google"},
    {"match": "^(llama|meta-llama)",      "family": "meta"},
    {"match": "^deepseek",                "family": "deepseek"},
    {"match": "^qwen",                    "family": "alibaba"},
    {"match": "^(mistral|mixtral|magistral)", "family": "mistral"},
    {"match": "^grok",                    "family": "xai"}
  ],
  "unmatched": "UNKNOWN-FAILS-CLOSED"
}
```

Resolution: normalize the id, apply rules in order, first match wins;
no match ⇒ UNKNOWN ⇒ FAIL (never inferred, never default-pass).
Normalization is for family resolution only — manifests carry the exact
dated model id verbatim. Extending the map is a contract change: new sha
in the store disclosure and every consuming manifest.

**Runtime seat ledger + invoker (r3; ASM-2458).** Schema
`kot-seat-ledger/1`: append-only JSONL (`poc/plainv5/seat-ledger.jsonl`
store-side; `runs/<id>/seat-ledger.jsonl` per consumer run), **entry 0 =
the author seat** (exact dated authoring model id). Entry fields:
`{seq, prev_sha256, seat_role, model_id, resolved_family,
family_map_sha256, prompt_sha256, invocation_form, output_sha256}`;
`prev_sha256` hash-chains each entry to its predecessor, so deletion,
reordering, or rewrite breaks the chain. Every LLM invocation in ANY seat
role goes through the pinned invoker `poc/plainv5/invoke_seat.py`, which
resolves the family via the pinned map, evaluates
`family(seat) != family(entry 0)` AND both non-UNKNOWN BEFORE dispatch,
REFUSES (no API call) on FD-1/FD-2, appends the entry pre-dispatch, and
completes `output_sha256` on return. Direct model calls are banned;
FD-5 catches them as orphans.

**Validator:** `poc/plainv5/check_family_disjoint.py`. Inputs: the map,
the store's `authoring_disclosure`, the record's DECLARED
`llm_seat_ledger` (`[{seat_role, model_id}]` — for the store's own gate,
the two gate seats + the fidelity seat; for a consumer, every LLM seat:
judges, screens, CLR/annotation-audit seats, and every
tie-break/resolution seat, declared in advance even if conditionally
invoked), and the RUNTIME seat ledger. Codes, fail-closed:

- **FD-1** any model id resolves UNKNOWN.
- **FD-2** `family(seat) == family(author)` for any seat.
- **FD-3** a seat's model id missing or not in the exact dated form.
- **FD-4** the declared seat ledger is absent, or omits a seat role the
  record's own text names (mechanical cross-check: every string matching
  `seat|judge|screen|tie-break` role names declared in the record's
  protocol section must appear in the ledger).
- **FD-5** (r3) orphan: a raw seat output file whose sha matches no
  runtime-ledger entry, or a runtime entry with no completed
  `output_sha256` — swept by verdict-gen/report-gen before any readout.
- **FD-6** (r3) integrity: the runtime ledger's hash chain does not
  verify head-to-entry-0, OR its role set mismatches the declared ledger
  (a declared role never ledgered, or an undeclared role appearing at
  run time).

Run points (all blocking): EVERY invocation via the invoker (FD-1/FD-2
pre-dispatch), plus store lint (via PV5-10), gate staging, consumer
prereg-freeze, readout validation (§9, RD-5 — verified against the
runtime ledger head).

## 8. Contextual leak review (audit codes A-CLR-*; consumer-side, EXHAUSTIVE; ASM-2451)

Implements contract §7.2 layer 2 plus the r3 annotation↔item mechanicals.
Unit enumeration is MECHANICAL, derived from the builder's pinned
provenance: for every item in the consumer's final built set, the
touching-definition set = {own concept} ∪ {claim_source donor} ∪
{distractor option concepts}; and (r3, ASM-2457) the touching-ANNOTATION
set = the sense annotations of the SAME provenance concepts, every role —
not merely the item's own concept. Prompts (P1 answerability, P2
implication for definitions; P1a/P2a for annotations — contract §7.2) are
pinned bytes under `poc/plainv5/audit/`, order map pinned, one read per
unit, first-valid-final, blinding grep on prompts and outputs, every seat
invoked through the §7 ledger.

Mechanical annotation codes (r3; run before the LLM probes, fail-closed):

- **A-ANN-MAP** — the committed `sense-map.json` + `sense-annotations.json`
  do not byte-equal an audit-side re-run of the pinned selector + renderer
  from the pinned inventory/records (the §4 S-7 property re-asserted by
  the AUDITOR — the store side cannot self-certify).
- **A-ANN-NGRAM** — a ≥4-gram of `toks(annotation)` occurs in any item's
  stem or answer text (any concept, both directions).
- **A-ANN-JACCARD** — token-set Jaccard(annotation, any item's answer
  text) ≥ 0.3.

LLM-probe codes:

- **A-CLR-LEAK** — P2 `leak`; P2a `leak`; ANY P1a keyed-answer recovery
  (annotations have NO licensed channels); or P1 keyed-answer recovery
  outside a licensed ASM-2447 channel. Audit FAIL, freeze blocked,
  escalate.
- **A-CLR-CHANNEL** — a `licensed-only` verdict whose named channel
  matches no pinned ASM-2447 channel (A own-definition, B donor-claim,
  C distractor-definition). `licensed-only` is only ever a DEFINITION
  disposition — on an annotation unit it is itself a finding. Escalates;
  never silently exempted.
- **A-CLR-COVERAGE** — any provenance-derivable (item, definition) pair,
  any provenance-derivable (item, annotation) pair, or any of the 108
  annotations lacks a verdict. Exhaustiveness is itself a checked
  property, not an intention.

Report `poc/plainv5/audit/clr-report.json`: definition and annotation
units enumerated/reviewed, findings by code (incl. A-ANN-*), licensed hits
by channel, P1/P2/P1a/P2a prompt shas, seat model ids (FD-checked,
runtime-ledger entries referenced). Its sha is the `clr_status` green
witness of §9.

## 9. Readout disclosure validator (codes RD-*; ASM-2454)

Implements contract §7.3. `poc/plainv5/validate_readout_disclosure.py`
takes a readout artifact (md or json) + the pinned store file; scans for a
fenced JSON block (or a top-level JSON member) with
`"schema": "kot-plainv5-readout-disclosure/1"`; exits nonzero with named
codes:

- **RD-1** no disclosure block found.
- **RD-2** schema tag wrong or malformed JSON.
- **RD-3** a required field missing/empty: `authoring_model{family,model}`,
  `authored_date`, `authoring_prompt_sha256`, `transcript_sha256`,
  `item_blindness{sense_source{inventory_sha256,selector_sha256,
  map_sha256,renderer_sha256}, fallback_count, override_count,
  clr_status}`,
  `family_disjointness{family_map_sha256, fd_status}`.
- **RD-4** any sha (full 64-hex required) mismatching the pinned store
  disclosure byte-for-byte.
- **RD-5** `fd_status` not `green:<runtime seat-ledger HEAD sha>`
  verifiable against the consumer's committed hash-chained RUNTIME ledger
  (chain verified head-to-entry-0; FD-5/FD-6 clean — a declared-only
  ledger does not satisfy RD-5 at r3).
- **RD-6** item-blindness fields missing, or `clr_status == "not-yet-run"`
  on a readout that reports consumer-experiment numbers (store-only
  readouts predating any consumer may carry it; experiment readouts may
  not — the validator distinguishes by the presence of a consumer
  experiment id in the readout's own header fields).

Wired into the consumer's report-gen/verdict-gen path and into the store's
own gate tally emission; the consumer prereg carries "no readout is
publishable with RD nonzero" verbatim.

## 10. What changing this spec means

The PV5/S/FD/A-CLR/A-ANN/RD codes, thresholds, band arithmetic, family-map
rules, the selector's scoring/tie-break rule, the invoker's refusal logic,
CLR probe prompts (P1/P2/P1a/P2a), and feedback-table bytes are part of the
store contract.
Any change after the authoring session starts is a NEW store version:
re-render, re-author or re-repair under the new contract, re-run the full
gate, new shas everywhere. No silent threshold edits, ever.
