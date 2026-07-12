# CASC-0' kernel-coverage mapping + gloss-template authoring record (ASM-1158 pre-freeze check)

> **Status: PROVISIONAL — pre-freeze explicator deliverable.** Executes the
> PROPOSED-ASM-1158 stipulated check for `registry/experiments/casc-0.json`
> (DRAFT). Author: Fable, explicator role, 2026-07-11. This document performs
> no freeze, no registry edit, no bd write, no run. Nothing here is a
> feasibility conclusion; a mapping verdict licenses only a RIDER WORDING.

## 1. What was checked, against what

The d-casc0 relation concepts (`data/d-casc0/composition-table.json`):
7 core relation types {parent, child, sibling, grandparent, grandchild,
pibling, nibling} and their 14 gendered surfaces {mother, father, son,
daughter, sister, brother, grandmother, grandfather, grandson,
granddaughter, aunt, uncle, niece, nephew}, plus the supporting concepts
the items lean on (agent sex; "born" never appears in items but anchors the
molecule senses).

Mapped against the kernel instance the manifest pins VERBATIM from
f2b-transfer: kernel-v0 (54 records, kot-hash `8209cada…`) and molecules-v0
(kot-hash `69f0c8a3…`), read from `dist/kernel-snapshot-2026-07-07/corpora/`
records. **Sense discipline:** a mapping counts only if the record bears the
RELATIONAL sense the composition engine uses (`rel(A,B)` = "A is the <rel>
of B"), not merely the same lemma in another sense.

## 2. The mapping

| d-casc0 concept | kernel/molecule record | status |
|---|---|---|
| parent (core) | — | **no kernel record** (no gender-neutral parent-of record) |
| child (core, offspring-of) | `urn:molecule-v0:child` | **sense mismatch** — the molecule explicates the AGE sense ("born a short time before now; the body … is small"), not the relational offspring-of sense the engine composes over |
| sibling (core) | — | no kernel record |
| grandparent (core) | — | no kernel record |
| grandchild (core) | — | no kernel record |
| pibling (core) | — | no kernel record |
| nibling (core) | — | no kernel record |
| mother (surface) | `urn:molecule-v0:mother` | **covered, relational** ("a child was born from inside this someone's body …") |
| father (surface) | `urn:molecule-v0:father` | **covered, relational** |
| son, daughter (surfaces) | — | no kernel record |
| sister, brother (surfaces) | — | no kernel record |
| grandmother, grandfather (surfaces) | — | no kernel record |
| granddaughter, grandson (surfaces) | — | no kernel record |
| aunt, uncle, niece, nephew (surfaces) | — | no kernel record |
| support: woman / man | `urn:molecule-v0:woman` / `urn:molecule-v0:man` | covered (sex atoms) |
| support: born / birth | `urn:kernel-v0:birth` | covered (event; anchors mother/father/child molecules) |

Counts: core relation types **0/7** kernel-record-backed in the relational
sense (1/7 only under a sense-lenient reading of molecule `child`);
gendered surfaces **2/14** (mother, father).

## 3. Threshold and verdict

**Threshold (stated pre-verdict):** the mapping SUCCEEDS — i.e. the record's
rider may keep "kernel-covered" — iff **≥ 6 of the 7 core relation types**
map to an existing kernel-v0/molecules-v0 record bearing the relational
sense. Rationale: every eval item's 7-option answer surface spans all 7 core
types, so "covered" with more than one uncovered type would misdescribe
essentially every item; one gap is tolerable as lexical accident, two are
not. Robustness: the verdict does not depend on this exact number — the
measured 0/7 (2/14 surfaces) fails ANY threshold above 2/7.

**VERDICT: FAIL.** Per ASM-1158, the rider clause weakens from
"kernel-covered" to **"kernel-STYLE"** in the frozen record — a wording
change, not a design change; the rider rides regardless. kernel-v0 /
molecules-v0 remain pinned as the gloss medium's authoring-STYLE anchor
only (they were never read by the runner; `casc0-manifest.json`
`inputs_status` already says so).

## 4. Gloss-template upgrade (the ASM-1142/1158 open item, discharged)

`poc/casc-0/inputs/casc0-manifest.json` `prompt_frames.gloss` rewritten from
one designer-authored skeleton (the knull-v3 set-level-monotony failure
mode: a single template with `{rel_core_upper}` swapped in) to
**explicator-authored per-relation Option-A records**: `fact_line` is now a
dict of 6 authored entries keyed by fact surface, `claim_line` a dict of 14
keyed by assertable surface. `casc0_runner.py Renderer` gained dict-frame
support that **fail-closes** (`ERR_FRAME`) on any surface without an
authored entry — no silent fallbacks.

Each record is a typed canonical claim, one claim per field/clause:
record kind (`[claim kinship/1]` / `[derived kinship/1]` /
`[query kinship/1]`), canonical `type:` (`casc0:rel/<core>` — SELF-AUTHORED
namespace, per §3), `surface:`, `agent:`/`patient:` (entity URNs on store
facts; bare labels on reasoner-derived claims, which assert no URNs),
`direction:`, then a `gloss:` clause reading the head in plain words.

**Variation is semantic, never cosmetic** (the scholarly-definition
standard): parent/grandparent glosses lead with the sex clause in adult
terms ("a woman/a man") then the core relation; child/grandchild glosses
lead with the relation and mark sex age-neutrally ("female/male" — a son
need not be a child); sibling records carry `direction: symmetric` (the one
relation where `agent-to-patient` would mislead) and a two-party gloss;
aunt/uncle/niece/nephew glosses stay at the natural gendered surface with
no redundant sex clause (English has no everyday neutral term; the head
carries the canonical core `pibling`/`nibling`). Minimal pairs
(mother/father) differ minimally — that is correct authoring, not monotony.

**Before/after (fact, `mother`):**
- BEFORE: `[claim kinship/1] relation: PARENT-OF | agent: Diane (urn:…) |
  patient: Zack (urn:…) | direction: agent-to-patient | gloss: Diane is
  someone of the female kind; Diane is the mother of Zack.`
- AFTER: `[claim kinship/1] type: casc0:rel/parent | surface: "mother" |
  agent: Diane (urn:…) | patient: Zack (urn:…) | direction:
  agent-to-patient | gloss: Diane is a woman; Diane is a parent of Zack.`

**Before/after (derived claim, `sister`):**
- BEFORE: `[derived kinship/1] relation-surface: sister | agent: Ana |
  patient: Bea | status: asserted-by-reasoner.`
- AFTER: `[derived kinship/1] status: asserted-by-reasoner | type:
  casc0:rel/sibling | surface: "sister" | agent: Ana | patient: Bea |
  direction: symmetric | gloss: Ana and Bea are siblings; Ana is female.`

**Content-matching (analytic-content boundary), stated for the record:**
every gloss head field and clause is a function of the single fact/claim
triple (subj, surface term, obj) — core type, agent sex, and
direction/symmetry are lexical content of the surface word the
content-matched nl sentence already carries ("Diane is the mother of
Zack"). Deliberately EXCLUDED as information the nl arm does not carry:
converse restatements, generation counts, decompositions (never "an aunt is
a parent's sister" — that is composition-table content, the very thing
under test), and the molecule explication bodies (birth semantics) — the
last also for consistency with the kernel-STYLE verdict. nl and plain
frames are untouched. Measured over 50 rendered eval prompts: gloss/nl
char ratio 3.36, plain/nl 0.87 (planning note said ≈3.0/≈0.9; estimates
only — dry-plan re-run 2026-07-11, worst case $16.13, inside every cap).

**Re-verification (2026-07-11):** `--mock` green end-to-end (24 run-record
bodies), pinned `analysis/casc_0.py` consumes them with all four instrument
gates valid and emits the weakened rider; `--dry-plan` inside all caps.
MOCK figures are never measurements.

## 5. What the coordinator must apply (exact wording)

Already edited pre-freeze by this pass (new bytes to be pinned at freeze):
1. `poc/casc-0/inputs/casc0-manifest.json` — `prompt_frames.gloss`
   (per-relation records + `gloss_authoring_note`), `frames_note`,
   `eval_set.scoring` rider restatement, `pins.kernelPinsNote` (mapping
   executed, FAIL).
2. `poc/casc-0/runner/casc0_runner.py` — `Renderer._frame` dict support +
   `ERR_FRAME`; rider restatements (module docstring, `outcome_note`).
3. `analysis/casc_0.py` — rider restatements (docstring, `/analysis/rider`).
   The `analysis_script.sha256` pinned in the frozen record must be of
   these NEW bytes.

Remaining, coordinator-owned:
4. `registry/experiments/casc-0.json` — replace the token `kernel-covered`
   with `kernel-STYLE` at its 3 occurrences ("… / kernel-STYLE /
   engine-derived-gold corpus — rider on every sentence)", "… /
   kernel-STYLE / engine-derived-gold rider on every verdict sentence.",
   "…kernel-STYLE/engine-derived-gold rider]"); replace both
   "designer-authored kernel-STYLE pending the explicator's pre-freeze pass
   [PROPOSED-ASM-1142, PROPOSED-ASM-1158]" and "designer-authored
   kernel-STYLE Option-A (self-authored rider; PROPOSED-ASM-1142)" with
   "explicator-authored kernel-STYLE Option-A per-relation records
   (ASM-1158 check executed 2026-07-11; poc/casc-0/kernel-coverage.md)".
5. `poc/casc-0/design.md` §1 rider line — "SELF-AUTHORED / kernel-covered /"
   → "SELF-AUTHORED / kernel-STYLE /". Optionally §3 planning parenthesis
   "gloss≈3.0" → "gloss≈3.4 (rendered upgraded templates)".
6. `poc/casc-0/proposed-asm-1140-1159.json` —
   ASM-1142 claim final sentence → "The gloss templates are
   explicator-authored kernel-STYLE Option-A per-relation records (dict
   frames keyed by rel_surface; runner fail-closes ERR_FRAME; ASM-1158
   check executed 2026-07-11 — poc/casc-0/kernel-coverage.md)."; ASM-1157
   claim "kernel-covered" → "kernel-STYLE"; ASM-1158 notes append:
   "EXECUTED 2026-07-11 (explicator): mapping FAILED — 0/7 core relation
   types kernel-record-backed in the relational sense (surfaces
   mother/father map to urn:molecule-v0:mother / urn:molecule-v0:father;
   molecule 'child' is the age sense); rider weakened to 'kernel-STYLE';
   gloss templates upgraded; mock + dry-plan re-verified green.". The
   ASM-1140–1159 array is OTHERWISE VALID: no other entry states or depends
   on the coverage outcome, and ASM-1158 pre-authorised exactly this
   weakening path.
7. **Do NOT edit `data/d-casc0/manifest.json`** — its internal
   "kernel-covered rider" string sits inside the bytes covered by
   `dcasc0CorpusKotHash` (the recipe walks the whole directory); editing it
   would break the corpus pin. The frozen record should note that string as
   superseded wording, governed by the record's own rider.
8. Pre-existing, out of this pass's scope (flag only): exemplar blocks
   render a doubled answer cue ("Answer:\nAnswer: B") in EVERY medium
   (`Renderer.exemplar_block` rstrip + `exemplar_answer`); medium-symmetric,
   so no contrast confound, but the coordinator may want a deliberate fix
   before freeze.

Self-check: no frozen object edited; no account handles; provisional
throughout; no feasibility conclusion is licensed by anything above.
