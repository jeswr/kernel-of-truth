# knull plain-dictionary arm — quality finding, confound ruling, re-authored sample, scope audit, full-rewrite plan

- **Author:** Fable experiment-designer role (`kern/fable-designer`), 2026-07-10.
- **Trigger:** the maintainer's hard language-quality standard (2026-07-10), verbatim:
  definitional output *"should follow a very precise style following proper language
  conventions — as if it were an article written by a very well-trained English scholar
  who knows all of the conventions of the language and will use the most appropriate word
  in a given place. Including unnecessary information in the definition also seems
  inappropriate for the task."* Mechanical/templated prose is unacceptable.
- **What this doc is:** the maintainer-review artifact for the knull plain-arm quality
  problem — a plain-language explanation of the experiment (§1), the measured defect (§2),
  the designer's confound ruling (§3), a re-authored 12-item sample with blind
  quality-gate evidence (§4–§5), a programme-wide audit of every other authored or
  generated definitional surface (§6), and the full-rewrite plan with costs and re-freeze
  steps (§7). **Nothing frozen is touched**: the frozen record
  `registry/experiments/knull.json` and every pinned input under `poc/knull/inputs/` are
  byte-identical to their frozen state; the sample lives in `poc/knull/reauthor-sample/`
  and is wired into nothing. No GPU was spent; no full rewrite has been executed — the
  maintainer reviews this first.
- **Owned files:** this doc; `poc/knull/reauthor-sample/**`; register entries
  ASM-0700..ASM-0703. Nothing else.

---

## 1. What knull tests, and what the plain-dictionary arm is FOR (plain language)

The programme's one positive end-task result so far is **f2b-replicate**: a 135M model
plus a "verify-retry" loop against the kernel's record store answers definitional
multiple-choice questions **+0.1507 absolute** better than a 12x-larger 1.7B model
answering alone, at about a tenth of the cost.
PREMISE: [MEASURED: registry/verdicts/f2b-replicate.json] f2b lift +0.1507 absolute
(one-sided 95% BCa LB +0.1053), audit CONFIRMED.

The open question knull decides: **is that lift earned by the NSM content of the store,
or would any correctly-aligned answer key have done the same?** The mechanism is blunt:
the verifier accepts an answer only when its text string-matches the stored record, and
on rejection the model silently resamples (up to k=4). Nothing in that machinery reads
NSM structure — it compares strings. So the lift might be a *generic*
"aligned-answer-key + retry" effect. knull runs the same frozen mechanism three times,
changing ONLY what the store says:

| arm | store content | role |
|---|---|---|
| **kernel** | the canonical NSM glosses (e.g. *alive*: "this someone lives now; the body can move; this someone can feel something.") | the arm under test |
| **plain** | the same 108 concepts defined in **ordinary dictionary English** | the **aligned-but-non-NSM control** — "would a normal dictionary do just as well?" |
| **opaque** | deterministic nonce text, meaningless by construction | the alignment-only pole — "would a meaningless but aligned key do just as well?" |

Everything else is held identical across arms: the same 1000 question skeletons (same
concepts, same template types, same distractor coordinates, same option layout), the same
retry budget, the same acceptance machinery, and **matched token budgets** (each arm's
prompts must cost the model the same compute, within ±10% pre-freeze / ±20% at run time).

**How the plain definitions are consumed** (the part that was missing from prior
narration): the definitions are not passive reference data — they are simultaneously the
prose the model reads, the answer key, and the claim pool:

1. **def-match items** (324): the question is "Which option gives the meaning of the word
   X?" — the correct option's text **is the plain definition verbatim**, and the three
   distractors are other concepts' plain definitions.
2. **term-match items** (324): the plain definition is embedded in the question ("Which
   word means: …?"), and the options are concept names.
3. **claim items** (56 true + 376 false): individual semicolon/period-separated
   **segments** of the definition are asserted as claims about the word and judged
   true/false.
4. **the verifier** accepts or rejects the model's pick by normalized string identity /
   segment membership against the same store; on rejection the model resamples.

So in the plain arm, the definition text is the entire content of the arm. Its prose
quality is not cosmetic: it is what the model reads, what the model must reproduce, and
what the claim items are made of.

**Verdict logic** (frozen): if the kernel arm's lift is statistically equivalent to the
best aligned non-NSM arm's lift (margin ±0.05), the f2b lift is relabeled *generic* and
the content attribution dies at this scope (verdict NULL, a decisive and fully-reportable
outcome). If the kernel arm wins by more than 0.05, NSM content measurably carries weight
(PASS). If it loses by more than 0.05, NSM surface is a measured net cost (FAIL).

## 2. The measured problem

A blind review was run on the committed plain store: GPT-5.6 (codex 0.144.1, read-only,
empty out-of-repo workdir, no project/NSM/experiment context, headwords withheld) was
shown the 108 definition texts and asked to judge them as a lexicographer.

PREMISE: [MEASURED: poc/knull/gpt56-plaindict-review/review.raw.md] the blind reviewer
rated the plain store **3/10** for naturalness, with named
defect classes: a universal semicolon-chain template ("core gloss; restatement;
consequence; further consequence"), mechanical anaphoric renaming ("the item", "the
object", "the creature"), staged generic observers ("anyone who looks in the right
direction perceives it"), before/after state-transition scripts, register violations
("Drowsiness demands it", "dreams may visit"), and extraneous non-definitional content
(symptoms, biological necessity, literary flourish); set-level discriminability from a
real dictionary was estimated at 95–99%.

PREMISE: [MEASURED: poc/knull/reauthor-sample/gate.old12.raw.md] re-scored at the matched
set size used by the sample gate (the 12 concepts of §4, definitions only, same rubric,
independent blind session), the OLD definitions read **2/10**.

This fails the maintainer's standard on all three named counts: register violations are
improper word choice; the consequence/observer/flourish clauses are unnecessary
information; the anaphoric template is mechanical prose.

## 3. Confound ruling (the designer's epistemic call)

DECISION: [STIPULATED: ASM-0700] a mechanically-defective plain-dictionary control
**CONFOUNDS the knull ablation, one-sidedly**, and re-authoring the plain store to the
maintainer's standard is **methodologically REQUIRED before the knull campaign runs** —
not optional polish.

The reasoning, explicitly:

- **What a bad control cannot fake: the deflationary outcomes.** If the kernel arm is
  merely *equivalent* to (or worse than) even a badly-written aligned store, then a
  fortiori it would not beat a well-written one — the NULL (generic) and FAIL (inferior)
  readings survive a degraded control.
- **What a bad control CAN fake: exactly the content win.** H-KN2 / PASS-CONTENT claims
  "NSM content carries weight beyond alignment" by beating the best aligned non-NSM arm.
  If that comparator is weakened by defective authoring — incoherent register, filler
  clauses diluting the definitional signal the 135M host must latch onto — the kernel arm
  can "win" by being less badly written rather than by carrying NSM content. The
  within-arm alone baseline absorbs *difficulty* differences, and the difficulty gate
  bounds *headroom* asymmetry, but **no frozen gate measures prose quality**, so this
  channel is unbounded by any pre-registered instrument.
- **The bias direction is the forbidden one.** The design's own conservatism principle
  (design doc §5 attack 5) is that every irreducible bias must run AGAINST the content
  claim. A degraded control biases TOWARD it. That is disqualifying on the design's own
  terms.
- **Independently binding:** the maintainer's language-quality standard is adopted as a
  hard requirement on all authored ordinary-English definitional content, so even absent
  the confound argument the store as committed is not shippable.

Consequence for custody: the plain store's bytes are pinned inside the FROZEN knull
record (manifest + authored-source sha). A content rewrite therefore cannot be a quiet
ops amendment — it requires a superseding record and a re-freeze (§7 steps 5–7). Until
then, the frozen knull record must not be run.

**What the re-authoring must preserve** (the matching that keeps the arms comparable —
all enforced fail-closed by the committed linter and build):

| constraint | meaning | why it exists |
|---|---|---|
| L-1 completeness | exactly the 108 covered concepts | arm coverage identical |
| L-2 LC1 own-label | headword never appears in its own definition | no trivial self-identification |
| L-3 word band | within −25%/+25% (min +8) words of the concept's NSM gloss | the matched token budget (FLOPs-parity proxy at build time) |
| L-4 segments | ≥2 admissible claim segments (split on `[.;]`, ≥15 chars) | claim items need segments |
| L-5 / R-1 | pairwise unique; no verbatim NSM segment either direction | arms must not leak into each other |
| R-2 register | every segment carries non-NSM vocabulary; ratio ≥0.25 | the arm must actually BE non-NSM |
| R-3 Jaccard | token overlap with own NSM gloss < 0.5 | content, not paraphrase, varies |
| R-4 / D-1 | ASCII, no double quotes, no account strings; authoring disclosure | hygiene |
| G-3 token band | mean prompt tokens within ±10% of kernel arm at the pinned tokenizer (run-time gate ±20%) | matched compute per query |

## 4. The re-authored sample (12 items, 3 blind-gated iterations)

Items: the 10 blind spot-check concepts (`poc/knull/inputs/plain-spotcheck.json`) plus
the two entries the baseline review rated least natural (*ball*, *sleep*). File:
`poc/knull/reauthor-sample/plain-reauthored-sample.json` (v0.3.0). Every iteration was
verified against the FULL G-1 linter contract by substitution into the committed store
(`check_sample.py` → PASS, `check-report.json`) — word band, segments, LC1, uniqueness,
register, Jaccard, hygiene all green, so the sample is drop-in compatible with the frozen
matching guarantees.

Authoring model: edited general-dictionary English — genus + differentiae, genuine sense
divisions, contrastive distinctions, parenthetical subject restrictions in the ODE
manner, exemplification where a dictionary would exemplify; **every clause definitional**;
no consequence narration, no staged observers, no anaphoric renaming, no life-lesson or
literary closings; the most apt word in each slot.

Old vs new, side by side (4 of 12; the rest are in the sample file):

| concept | OLD (committed store) | NEW (v3 sample) |
|---|---|---|
| **sleep** | "the nightly state of rest in which the body lies still and awareness fades; a slumbering person does not see, barely hears, and knows nothing of events nearby; everyone requires the restorative pause, and drowsiness demands it after long exertion; dreams may visit during the deepest stretches, vanishing by morning" | "the natural state of rest that recurs in every day or night, in which the eyes close, the muscles relax, and consciousness is suspended; it differs from mere rest in the loss of awareness, and from a swoon or coma in the ease with which it is broken" |
| **ball** | "a manufactured plaything with a uniformly round shape; struck or thrown by hand, it rolls or bounces across the ground for a while; children spend hours playing games with one because the activity is enjoyable; its evenness distinguishes it from most other objects" | "a rounded object employed in games and sports, typically struck, kicked, or thrown; it may be hollow or solid, and its size and weight are fixed by the game in which it is used, ranging from the small hard sphere of golf to the large inflated sphere of football" |
| **dog** | "a domesticated canine widely kept by households; it barks loudly when anything stirs nearby, alerting owners at a distance; renowned for loyalty, it forms warm bonds with its keepers, and most owners return the affection; breeds vary greatly in size" | "a domesticated carnivorous mammal of the wolf family, noted for its keen scent and its bark, and kept since ancient times as a companion or working animal; the breeds differ widely in size and form" |
| **dead** | "no longer living; having permanently ceased all vital functions; incapable of any further action or awareness" | "(of a person, animal, or plant) no longer alive; having permanently ceased the functions of life" |

## 5. Blind gate result — and what it measured

Gate instrument [STIPULATED: ASM-0701]: the SAME blind reviewer, rubric, and prompt frame
as the 3/10 baseline (GPT-5.6, codex 0.144.1, effort high, read-only, ephemeral, empty
out-of-repo workdir, headwords withheld, no project context, the judge never told a
comparison set exists), at matched set size N=12, with the OLD 12 re-scored in an
independent session as the paired control. Stipulated PASS threshold: ≥7/10.

PREMISE: [MEASURED: poc/knull/reauthor-sample/gate.*.raw.md] the measured trajectory on
the rubric's overall-naturalness scale is — OLD-12 **2/10**; re-authored v1 **4/10**;
v2 **4/10**; v3 **5/10** (gate.old12 / gate.new12.v1 / v2 / v3 respectively).

**Reported without softening: the sample did NOT reach the stipulated 7/10.** What the
iteration trajectory shows, from the blind judge's own findings per round:

- **The maintainer's named defect classes are eliminated.** The baseline/old reads found
  register violations, anaphoric renaming, staged observers, consequence narration,
  extraneous symptoms/necessity/flourish. From v1 onward, **none of those classes appears
  in any finding**. The v3 findings are of a different kind: density of three-item
  enumerations, recurrence of "define; elaborate" clause rhythm, uniformly extended
  entries across a themed set. Two residual LOCAL word-aptness lapses were flagged and are
  genuine (they fall under the "most appropriate word" half of the standard): *ball*'s
  "the small hard sphere of golf … the large inflated sphere of football" (should be
  "golf ball"/"football") and *make*'s elliptical "as a craftsman does a chair" — both are
  single-word fixes a final editing pass clears, not template defects. Everything else the
  judge names is structural (below).
- **The residual findings are the footprint of the frozen matching constraints, not of
  careless authoring.** Every entry MUST have ≥2 `[.;]`-separated segments (L-4: the
  claim items are built from segments) — so every entry necessarily has the "definition;
  second unit" shape the judge reads as a template. Every entry MUST sit within ±25% of
  its NSM gloss's word count (L-3: the token-budget match) — and the NSM glosses run
  16–56 words, roughly **2x the natural length** of an edited dictionary entry for the
  same word, so every entry is necessarily "over-elaborated for a simple word" (the
  judge's phrase). The devices a real dictionary would use instead — one-word synonym
  definitions, numbered senses, terse labels — are exactly the devices the frozen
  contract forbids or breaks.
- The rubric's 10-anchor is "indistinguishable from a professionally edited general
  dictionary". Under the frozen L-3/L-4 contract that anchor is unreachable for ANY
  authoring, however scholarly — a set of 12 same-length, always-two-part entries is
  identifiable as non-editorial regardless of prose quality. The instrument saturates
  below the stipulated threshold for structural reasons independent of the maintainer's
  actual standard (word-aptness, propriety, no unnecessary information), which the v3
  text satisfies on the blind judge's own per-finding evidence.

DECISION: [STIPULATED: ASM-0703] the sample gate at threshold 7/10 is recorded as
**FAIL**, the raw scores stand unedited, and the threshold question is escalated to the
maintainer rather than silently re-based by the designer: a post-measurement gate
amendment (defect-class instrument + naturalness floor 5/10 at matched size, both judges)
is REGISTERED AS A PROPOSAL that takes effect only on maintainer ratification.

The maintainer's decision fork, stated plainly:

- **(a) Ratify the re-based gate** (ASM-0703): accept that under matched budgets the
  plain arm reads like an unabridged/extended dictionary rather than a pocket one;
  require zero defect-class findings (the maintainer's verbatim standard,
  operationalized) plus a naturalness floor ≥5/10; proceed to the full rewrite (§7).
  This is the designer's recommendation: matched token budgets are a hard scientific
  requirement of the ablation (without them the FLOPs-parity guarantee dies and the arms
  stop being comparable), every arm's store is "unnatural" in its own disclosed way (the
  kernel arm is a controlled metalanguage), and what fairness requires is that the plain
  arm be the best ordinary-English rendering the matching constraints permit — which the
  defect-class gate measures.
- **(b) Relax the matching constraints** (natural-length entries, ~0.4–0.6x the NSM
  gloss): buys genuine pocket-dictionary naturalness at the cost of the FLOPs-parity
  instrument (def-match prompts are 4 definitions long, so prompt compute would drop
  ~40% in the plain arm) and a deeper redesign + new record regardless. Not recommended:
  it trades a disclosed stylistic footprint for an undisclosed compute asymmetry.
- **(c) Keep the 7/10 gate as-is**: knull's PASS-CONTENT reading stays unlicensable
  (ASM-0700), so the experiment would only be worth running for its deflationary
  readings. Strictly worse than (a) for decision value at equal cost.

## 6. Programme-wide scope audit: where authored/generated definitional content lives

The maintainer's deeper worry: *"is this what the system produces?"* Audit of every
surface where definitional prose is authored or generated:

| # | surface | register | audit verdict |
|---|---|---|---|
| 1 | `poc/knull/inputs/plain-authored.json` → `stores/plain/`, `items/plain.jsonl` | intended ordinary English | **MECHANICAL, measured 3/10 — the subject of this doc; rewrite REQUIRED** |
| 2 | `poc/knull/inputs/stores/opaque/` | deterministic nonce | mechanical **by design** — it is the semantic-empty control; prose standards do not apply [STIPULATED: ASM-0702] |
| 3 | `data/kernel-v0/concepts/*.json` glosses (108) + `data/molecules-v0/molecules/*.json` grounding notes (54) | NSM controlled language | **by design, not defective** — but see the first-order finding below |
| 4 | `data/authored-explication-set/concepts/` (50 g9-authored explications) | NSM controlled language | same category as #3; consistent with its purpose |
| 5 | `data/d-qa`, `data/d-qa-r`, `data/d-qa-t`, knull item stems | fixed question templates | instrument text, templated by construction (pairing/LC8 require it); not definitional output |
| 6 | `data/d-ts` (truthstyle) style variants | rule-generated restyles | the style axis IS the manipulated variable; exempt; note its readout measured a small real judge-side preference FOR NSM register (pooled +0.025) — context for interpretation, ASM-0680/ASM-0681 |

**The first-order finding (stated plainly).** The kernel arm's own definitional content —
the thing the system actually serves as a correct answer — is the NSM gloss **verbatim**.
On every current end-task surface (f2b, knull, d-qa, d-qa-r), the "correct definition"
presented and accepted is text like *"this someone lives now; the body can move; this
someone can feel something."* By the maintainer's scholarly-English standard, that output
would score at the bottom of any naturalness scale — **deliberately**: NSM is a formal
controlled semantic metalanguage, the programme's chosen interlingua, not an attempt at
ordinary English. This is a different category from the plain arm's defect (accidental
bad English in text that purports to be ordinary English). But the consequence must be
said out loud: **nothing in the current system produces scholarly-English definitional
output, and no existing verdict licenses any claim that it does.** If system-facing
output in proper English is part of the value thesis, a surface-realization layer (NSM
record → edited English definition) is a missing, unmeasured component programme-wide —
a named gap, not a control nuisance [STIPULATED: ASM-0702]. Its output, when designed,
falls under the maintainer's standard and needs a quality gate of the same blind form
used here.

## 7. Full-rewrite plan + cost (NOT executed — maintainer reviews first)

Scope: 108 definitions; 12 exist at the v3 standard → **96 to re-author**.

1. **Maintainer review** of this doc: ratify or amend (i) the v3 style model (§4), and
   (ii) the gate instrument (ASM-0703 proposal vs alternatives in §5). ($0)
2. **Re-author the remaining 96** to the ratified style model, under a per-entry
   checklist: zero defect-class content (no anaphoric renaming, no observers, no
   consequences, no flourish, no register violation); every clause definitional; shape
   variety quotas across the set (parenthetical restrictions, finite second clauses,
   sense divisions, exemplification) so no single frame dominates. Designer role,
   ~one focused session (est. 2–4 h agent time), CPU only. ($0)
3. **Mechanical gate**: `lint_plain_store.py` green over the full replacement store
   (G-1 contract, fail-closed). ($0)
4. **Blind quality gate on the full 108** (freeze precondition): the ratified instrument,
   headwords withheld, no project context; GPT-5.6 (the baseline instrument — old-108
   already measured 3/10) **plus** a second judge family (Claude Haiku via the pinned
   headless `claude -p` form of `poc/truthstyle-2x2/judges-invocation.md` §4.3, including
   the §4.3.1 strict-mcp-config addendum), both judges passing the ratified thresholds.
   Raw outputs committed under `poc/knull/` as gate evidence. (a few judge calls, ≈$0)
5. **Rebuild inputs**: `build_inputs.py` regenerates `stores/plain/` + all three arms'
   item files; pairing (KNULL_ERR_PAIRING) and LC8 prompt-surface disjointness re-assert
   fail-closed. Disclosed consequence: claim segments change with the new definitions,
   so the item **type mix may shift** from 324/324/56/376 and must be re-disclosed in the
   new record (the mix stays identical ACROSS arms either way — the builder derives all
   arms from the same skeleton schedule). ($0)
6. **G-3 re-check**: token-band measurement at the pinned SmolLM2 tokenizer; the plain
   arm's mean-prompt-token ratio must stay inside the ±10% pre-freeze band (v3 keeps
   word-count parity with the old store, so ≈0.95 is expected — but it is measured, not
   assumed). ($0)
7. **Record custody (the re-freeze)**: knull is FROZEN and its manifest pins the plain
   source sha, so the rewrite requires a **superseding record** (`knull-v2`,
   `supersedes: knull`, the g3-llmproxy-v2 pattern per ASM-0651): identical design and
   endpoints, new pins (manifest, authored-source sha, type mix, G-3 artifact), the
   quality gate added to `prefreeze_gates_evidence`, the four deferred freeze ASMs from
   the design doc §6.4 plus the quality-gate ASM registered at freeze. Coordinator runs
   `prereg-freeze.py`; RT-15 external timestamp. The old record stays frozen history and
   is never run. (coordinator step, $0)
8. **Campaign** (unchanged, runner role, after freeze): 30 GPU cells, est. 4–6 GPU-h /
   $15–30 within the authorized caps (usd 60 / 8 GPU-h / 24 h wall).

Total incremental cost of the quality remediation: **≈$0 compute** (CPU + a handful of
subscription judge calls); one to two designer sessions; the GPU envelope is untouched.

Hard boundaries: no GPU before the superseding freeze; the designer identity that
authored the store never runs, grades, or audits the campaign; this doc's plan is
executed only after maintainer sign-off.

## 8. Changed-file list + self-check

Changed/added by this line (working tree; git custody stays with the maintainer):

- `docs/next/knull-plain-arm-quality.md` (this doc, new)
- `poc/knull/reauthor-sample/plain-reauthored-sample.json` (new; v0.3.0)
- `poc/knull/reauthor-sample/check_sample.py`, `check-report.json` (new)
- `poc/knull/reauthor-sample/build_gate_prompts.py`, `prompt.old12.txt`,
  `prompt.new12.txt` (new)
- `poc/knull/reauthor-sample/gate.old12.raw.md`, `gate.new12.v1.raw.md`,
  `gate.new12.v2.raw.md`, `gate.new12.v3.raw.md` (+ `.err` transcripts) (new)
- `registry/assumptions.jsonl` (append-only: ASM-0700, ASM-0701, ASM-0702, ASM-0703)
- `kb/records/internal/internal_doc-next-knull-plain-arm-quality.json` (generated by the
  local, deterministic `tools/kb/kb-sync-internal` stub generator so registry-check's
  kb-check passes for the new doc; the other 84 internal records were rewritten byte-
  identically — mtime only, no content change; no git/bd/remote kb-sync was run)

Custody note: `registry/experiments/knull.json` was already FROZEN (by coordinator-1,
2026-07-10) when this line began and is left **byte-untouched** (frozen_sha256
`9b2065c6…` unchanged). The full-rewrite plan (§7) deliberately routes through a
SUPERSEDING record (`knull-v2`), never an edit or re-freeze of this one. No git/bd/kb
remote-sync run; changed-file list reported for maintainer custody.

Self-check: `python3 tools/registry/registry-check.py` → PASS (pasted in the session
report accompanying this doc).
