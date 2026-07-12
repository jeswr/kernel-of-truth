# g2 measurement validity and sense-splitting — adjudication (Fable)

**Role: Fable ADJUDICATION agent, 2026-07-12, prompted by the maintainer's
response on issue #25. This document owns its conclusions: the rulings in
sections A–D are this agent's judgment, stated with confidence levels, and
are not the coordinator's. It changes no mechanical verdict — the
INSTRUMENT-INVALID readouts, the pilot-stop semantics, and the frozen
records all stand untouched. It adjudicates two prior questions: whether
the g2-import line is measuring the right thing, and whether the kernel
under measurement is constructed right.** Companion to
`docs/next/analysis/g2-panel-vs-assessment.md` (the per-item diagnostic this
document builds on and partially corrects) and
`docs/next/analysis/correctness-track-instrument-assessment.md` (the
instrument-failure ledger). Assumption block:
`docs/next/analysis/asm-g2adj-1880-1889.json` (emitted for central
registration by the coordinator; `registry/assumptions.jsonl` is not touched
here — no git actions in this pass).

Epistemic tags: **[MEASURED]** = read directly from committed bytes, run
files, or the live issue thread this tick (arithmetic that follows from
such bytes by stated steps is folded in and the steps shown);
**[LIT-BACKED]** = grounded in the published literature, provenance stated
(where the citation is from training knowledge and not pinned locally, that
is said); **[STIPULATED]** = a design choice, maintainer decision, or this
adjudicator's ruling — never evidence; **[COUNTERFACTUAL]** = arithmetic on
observed tables under stated substitutions, never evidence about a future
run; **[EXTRAPOLATION]** = a forward claim with its resolution path named.
Confidence figures are this agent's subjective probabilities, offered so
that disagreement has a handle to grip.

**Sources verified at source this tick:**
`data/onto-softtype/soft-type-candidates.jsonl` (all 84 records) and
`data/onto-softtype/{manifest.json,MAPPING.md}`;
`data/kernel-v0/{manifest.json,concepts/break.json}`;
`poc/ontology-import-g2/build-softtype.py` (the per-concept curation table,
break entries at lines 222–251) and `materials/arm-a{0,1,2,3}-*.jsonl`
(the pi:011 renders, verbatim); `poc/g2/materials/prompt-template.txt` and
`poc/g2/result.json` (the 0.3929 readout);
`poc/ontology-import-g2-v2/{pilot-manifest.json,prompt-template-v2.2.txt,
asm-opusjudge-1870-1879.json}` and
`runs/{real-20260712-auth/pilot-status.json,pilot-v22-20260712-171919/
driver.log,real-20260712-FABLEPROXY-PROVISIONAL/README.txt}`;
`docs/next/design/g2-import-v22-rubric-iteration.md` (§2b pre-commitment
anchors, grep-verified); `docs/next/design/ontology-import-plan.md`
(licensing clauses); issue #25 (body and comment state via `gh`); the
maintainer's sense-split directive (working-memory record
`kern-sense-split-concepts`, quoting the maintainer verbatim, 2026-07-12 —
the #25 thread itself carries no comment, so the directive's provenance is
the session record, disclosed as such). A repo-wide grep for consumers of
`soft-type-candidates.jsonl` / `kot-soft-type` outside
`poc/ontology-import-g2*` returned nothing.

---

## 0. The verified trace

The three facts supplied in the brief were each confirmed at source, and
each acquires a sharper edge on inspection.

**0.1 The soft layer is non-binding — and, today, unconsumed.** [MEASURED]
Every one of the 84 records in `soft-type-candidates.jsonl` carries
`binding: false`, `strength: preference`, `effect: rank-only`, and
`forbidden_effects: [assert-type, reject-world, derive-disjointness,
mint-entity, close-domain]`; the build manifest's `forbidden_effects_check`
is PASS and `hard_operational_axioms_emitted` is 0. Beyond that: no code
anywhere in the repository outside the import poc reads these records. The
layer's operational stakes are at present exactly zero; even after an
adoption GO, the plan's licensing clause caps its authority at ranking
otherwise-licensed interpretations — it can never "make an answer licensed
or forbidden" (`ontology-import-plan.md`, licensing section).

**0.2 The pi:011 defect is two-layered — and one layer thinner than its
headline.** [MEASURED] The record `urn:kot-soft-type:g2i:g2-pi-011` types
the **range** of `urn:kernel-v0:break` — the patient Y in "X breaks Y" — as
BFO `material entity`, on the evidence of SUMO `Damaging`/`Object` and
FrameNet `Cause_to_fragment` (frame-414), all hand-curated into the build
script's per-concept table. Break's domain is typed `entity` (the BFO top)
and its existential slot `temporal region`. **No record in any layer types
the breaking itself as a material entity**; the headline compression
"break → material entity", carried from the #25 table into subsequent
discussion, invites exactly that misreading. The genuine defect is real but
sits at the patient slot: "break a promise / the silence / a record" defeats
the unhedged "body or material to it" gloss, and both judges plus the prior
Fable read correctly rejected it. Beneath it, the concept
`urn:kernel-v0:break` is a single hand-authored NSM explication of the
physical-shatter sense ("after this time Y is not one something; there are
many small somethings"), listed in the kernel's own `knownWeak`, whose
authoring note already concedes the many-small-pieces clause "fits
shattering better than e.g. a broken machine".

**0.3 The maintainer's requirement.** [STIPULATED — maintainer decision,
2026-07-12] A kernel concept is a sense, not a word: polysemy must be split
at construction time (break-physical, break-sound, break-trust are distinct
concepts), and typing must answer to the concept's own meaning — a breakage,
in any sense, is an event, never a material entity. The hand-built kernel
does not sense-split; per 0.2, the existing records happen not to violate
the "never a material entity" clause for the event itself, but the
requirement's force is the sense-splitting, and there the kernel is plainly
short.

One further verified fact frames section D: the v2.2 successor (composite-
hedge rubric fix + judge-pB upgraded from Haiku-4.5 to Opus-4.8, shipped
together per the maintainer's directive) is built, mock-verified, and
**unspent** — its single launch attempt (2026-07-12T17:19:19Z) aborted at
preflight because the pA codex path was usage-capped, consuming a bounded
~$0.12 and zero pilot judgments. [MEASURED]

---

## A. Measurement validity: is "sound by ordinary meaning" the right test for a rank-only layer?

**Ruling: the test is a legitimate quality gate but a secondary
measurement, and the lineage has been spending its scarcest resource —
working judgment instruments — on the wrong end of the stakes gradient.
Confidence 0.85 on the stakes analysis; 0.7 on the redirect ordering.**
[STIPULATED — adjudicator's conclusion; grounds below are MEASURED]

The stakes of a typing error are set by what the typing is permitted to do.
The soft layer can only re-rank interpretations that the engine has already
licensed by other means (0.1); an unsound preference therefore has a
bounded worst case — a systematic bias in which reading is preferred — and
no path to asserting a false type, rejecting a true world, or deriving a
false disjointness. Today it has no worst case at all, because nothing
consumes it. By contrast, the typing that g2 v1 measured at 33/84 = 0.3929
soundness (primary stand-in; pair-concordant precision 0.286) is the
**hard** sort scheme — the `SomeoneRef`/`SomethingRef`/`TimeRef` referent
sorts inside the kot-ast/1 explications, which are identity-bearing by the
kernel manifest's own definition ("Identity = the explication object") and
which every consumer of explications inherits. Those sorts are where "X
breaks Y ⇒ X is a person" fails on storms. They remain in `data/kernel-v0/`
today, unmodified. [MEASURED]

The import line is not thereby pointless: its declared purpose
(`MAPPING.md`) is to *replace* each hard universal with a broad anchor plus
soft preferences, and the adoption gate (beat 0.3929 on the same 84 slots)
is a falsifiable check that the replacement's content is at least better
than what it displaces. Measuring "don't import falsehoods" before adopting
an import is sound practice. The invalidity creeps in at two points:

1. **The measured property is mis-centred relative to the value theses.**
   What the programme needs to know is whether typing *drives correct
   engine inference* — the rules-lane question, asked of the type layer.
   Ordinary-meaning soundness of rendered English is neither necessary nor
   sufficient for that: a preference can be a slightly false generic and
   still rank correctly in every case the engine meets, and can be
   impeccably true and rank nothing (several disputed items import
   `entity`, the BFO top, which excludes nothing — true and inert).
   Two Stage-P pilots and one full run have now been spent litigating the
   English of hedged composites; none of that expenditure moves either
   thesis. [MEASURED expenditure; STIPULATED reading]

2. **The instrument's currency aggravates the mismatch.** Rank-only
   preferences are generics; the instrument renders them as multi-sentence
   hedged composites and asks a universal question ("ALL normal cases") of
   the unhedged parts. Both AC1 failures decompose into construal channels
   of exactly this seam (hedge scope; sense scope — section B). An
   instrument whose failures are internal to its own rendering conventions
   is measuring its renderings. [MEASURED decomposition]

**What each redirect would license.** (i) *Re-measuring the binding sorts,
sense-split* (section C), licenses the thing the maintainer's requirement
actually governs: repair or replacement of identity-bearing typing. The
0.3929 stands as a word-scoped lower bound; the sense-scoped soundness of
the hard layer is currently **unmeasured**, and it, not the soft layer, is
what an engine consumer is bound by. (ii) *Engine-inference correctness
under the typing* — a ranking-sensitive task where the soft layer can
causally change an outcome, scored against an answer key (the DECONF-B /
f2b pattern: the instruments that have worked in this programme all had
deterministic or externally-adjudicated channels) — licenses the correctness
thesis's typing clause directly: "with the imported preferences the engine
resolves ambiguous items at rate p vs baseline q". Neither is licensed by
any outcome of the current soundness test; the current test licenses only
adoption of a module whose authority is rank-only and whose consumers do
not yet exist. That is a low-stakes license, and it should be priced
accordingly. [STIPULATED ruling]

---

## B. Rendering vs reality: re-adjudicating the #25 decomposition

**Ruling: the #25 framing — "English rendering ambiguity, not in the
kernel" — is right about the seven hedge-channel items, wrong about the
five sense-channel items, and the wrongness matters because it directed
repair effort at prose that cannot carry the fix. Decomposition: 7 of 12
rendering/rubric artifact; 5 of 12 real un-sense-split kernel polysemy
surfacing through the render; ontology-mapping over-commitment is real but
is the same defect seen from the pipeline side, not an independent third
cause. Confidence 0.9 on the channel split, 0.8 on the reclassification.**
[STIPULATED ruling; grounds MEASURED]

The twelve items at issue are the eleven splits plus the one both-no
(g2:pi:011) from the sanctioned pilot (`real-20260712-auth`, table
28/1/7/4, AC1 0.6222). [MEASURED]

**(i) Pure rendering/rubric artifact — the seven pB items (016, 021, 025,
033, 064, 068, 089).** Confirmed as framed. Each turns on hedge scope in a
multi-clause composite ("— not before" inside a "Typically"; subject-less
hedged fragments), the judge behaviour is deterministic across three
response sets, and the v2.2 rubric bullet plus calibration anchors target
precisely this seam. Nothing in the kernel or the mapping is implicated:
the same typings under a hedge-disciplined reading are unproblematic.
The prior panel diagnostic's attribution stands. [MEASURED]

**(ii) Real un-sense-split polysemy — the four pA items (036, 037, 070,
071) plus 011.** Here the #25 framing must be corrected. The template
instructs judges that "the parenthetical, if any, tells you which sense of
the word is meant", and the render's "as described above" resolves to
nothing beyond the concept line. For "lie (the words)", "birth (the
event)", "reminder (the made something)", that machinery works — the
parenthetical is a sense description, and not one of the pilot's
disagreements arises on a sense-fixed item through the sense channel. For
"break (X breaks Y)", "make (X makes Y)", "find (X finds Y)", the
parenthetical is bare valence: it names no sense **because the kernel has
no sense to name**. The instrument thereby delegates sense scope to the
judge; pA construed word-wide, pB centrally, and on 011 both construed
word-wide and correctly rejected. To call this "rendering ambiguity" is to
imply a prose fix exists; it does not. The proof is g2:pi:070 itself: its
render already carries an explicit breadth escape ("But Y can also be
words, a plan, or a happening — one can make a promise, or make trouble")
and pA still rejected, on non-creation idioms ("make the bed", "make the
train") that no gloss short of an actual sense specification excludes.
Deciding the sense is a kernel-construction act. The residue of genuine
panel noise remains as the prior diagnostic found it — pA's matched-schema
inconsistency at 071, arguably 068 — one to two items. [MEASURED renders
and responses; STIPULATED reclassification]

**(iii) Ontology-mapping over-commitment.** Real, but subordinate and
co-located with (ii). The pipeline's choice of `Cause_to_fragment` +
SUMO `Object` for break's range is faithful to the explication's
physical-shatter content — *within that sense* a material patient is a
defensible preference. The over-commitment consists in attaching a
sense-specific preference to a concept whose label and instrument scope are
word-wide. That is the same fault line as (ii), approached from the mapping
side: frame selection **is** sense selection (FrameNet separates the
physical `Cause_to_fragment` from the norm-violating `Compliance` that
covers "break a promise / the law" [LIT-BACKED — training knowledge, to be
pinned with the FrameNet source files at any sense-split build]), and the
pipeline made a sense choice the concept layer nowhere records. One latent
sibling deserves a flag: friend→`material entity` at both R3 slots (040,
041) passed the panel but over-commits by the same mechanism (imaginary or
artificial friends); it should be revisited under any sense-split
re-measure. [MEASURED build table; STIPULATED weighting]

**Corrections to #25, in order of importance.** First and principal: the
sentence "the ambiguity is in the *English rendering*, not the type" and
the summary "it is not that the kernel's typings are wrong" are unsound for
five of the twelve items — what the trace shows there is
sense-underdetermination *in the kernel*, a construction defect that
rendering iteration cannot repair and that the maintainer's requirement
squarely addresses. The #25 body in fact contained the observation that
undoes its own headline ("the bare parenthetical does not fix the physical
sense") without drawing the consequence. Second: the compression
"pi:011 (break → material entity)" should everywhere read "break's
*range* → material entity"; no layer types breakage as a material entity,
and precision here matters because the maintainer's stated concern ("in
none of these cases would I consider breakage a material entity")
responds to the compressed form. The sense-split requirement stands on its
own force regardless. Third, minor: #25's claim that the v2.2 fix leaves
the pA channel untouched is confirmed and quantified here — but note that
the untouched channel alone does not arithmetically fail the AC1 gate
(section D). [STIPULATED rulings on MEASURED text]

---

## C. Sense-splitting and construction methodology

**Ruling: the maintainer's requirement is the settled norm of every mature
lexical-semantic resource, and adopting it changes the construction
methodology's order of operations: sense inventory first, explication and
typing per sense after. It is a partial blocker on typing-soundness
measurement — binding for polysemous word-labelled concepts, already
satisfied by the sense-fixed ones. Confidence 0.9 on the precondition
claim; 0.7 on the pipeline specifics.** [STIPULATED ruling]

**The requirement is not an idiosyncratic preference.** WordNet's unit is
the synset, not the word; FrameNet's is the lexical unit — a lemma *in a
frame*; NSM practice explicates senses, one explication per sense, and
treats polysemy as the first analytic decision, not an afterthought.
"Break" is among the most polysemous verbs in English — WordNet's verb
entry runs to several dozen senses (the commonly cited count is 59)
[LIT-BACKED — training knowledge, not pinned locally; pin WordNet with the
sense-split build]. A concept store that assigns one vector, one
explication, and one typing to "break" has made a representational
commitment the entire field abandoned decades ago.

**What each construction route does with it.** The hand-NSM route, as
actually practised (agent-authored, 54 concepts, one pass), did not
spontaneously sense-split even under NSM discipline — the kernel's own
`knownWeak` list and break's authoring note are the honest record of that.
The ontology-derived route *implicitly* sense-splits at the mapping step —
choosing frame-414 is choosing break-physical — and the g2 failure mode was
precisely that this choice was made in the typing layer while the concept
layer stayed word-scoped: the two layers disagree about what the concept
is. The methodological consequence is not "hand vs ontology" but an
ordering: **sense-split-first**, with the sense inventory imported from the
resources the pipeline already pins (FrameNet lexical units, SUMO's
WordNet mappings, WordNet synsets), each kernel concept minted per sense
with a sense-fixing gloss in its label, and the NSM explication authored
against that fixed sense. The g2 corpus itself furnishes the internal
evidence for this ordering: every sense-channel disagreement and the sole
both-no item sit on bare-parenthetical heavy-polysemy verbs, while the
sense-fixed labels sailed through — though the condition is necessary
rather than sufficient, since give/help/lose, bare but centrally dominant,
also passed. [MEASURED pattern; STIPULATED methodology]

**Interaction with the large-kernel track.** Sense-splitting multiplies
concept count by the sense inventory — heavy-tailed, a factor of tens for
frequent verbs, near one for most nouns. At the staged 10k→1M+ scale this
is not a cost but the natural unit of account: importing by synset or
lexical unit *delivers* sense-split concepts for free, whereas hand-NSM
does not scale regardless (that being the large-kernel premise already).
[EXTRAPOLATION — resolved by the scale-track builds] The UFO-typed
construction is not an alternative to sense-splitting but a dependent of
it: gUFO's categories (Kind, Role, Phase, Event, Mode…) presuppose a
determinate sense — one cannot UFO-type the word "break", but one can type
break-physical (Event), broken (a Mode of the patient), break-trust (an
Event with a normative object). Sense-splitting is the entry ticket to the
UFO track. [LIT-BACKED category discipline; STIPULATED application]

**Is it a blocker on typing-soundness measurement?** For polysemous
word-labelled concepts, yes, and strictly: a soundness verdict against "the
ordinary meaning" of an unsplit word is ill-posed for any sense-specific
claim — the measured "unsound" conflates typing error with scope error, and
pi:011 is that conflation realised (the range preference is defensible for
the sense the explication describes and false for the word the label
denotes). For sense-fixed concepts the existing instrument already
measures cleanly, and those numbers stand. The practical rule: **do not
iterate further renders or spend further judgments on the polysemous subset
until it is split; the sense-fixed subset needs no such hold.**
[STIPULATED ruling]

---

## D. Net implication and the v2.2 pilot decision

**Feasibility read.** Nothing here moves either thesis, in either
direction. What it does move is the interpretation of the correctness
track's ledger: the g2 lineage's failures become progressively more legible
as instrument-and-construction confounds rather than as evidence about
typing quality, and the one alarming measured number — the 0.3929 hard-sort
soundness — is re-read as a word-scoped lower bound with the sense-scoped
truth unmeasured. That is a *less* pessimistic correctness picture than the
raw ledger suggests, purchased at the price of admitting we have not yet
measured the load-bearing quantity at all. The honest statement: typing
soundness and typing usefulness both remain open, now with a construction
prerequisite (sense-splitting) identified on the critical path to
measuring either. [STIPULATED assessment]

**The pilot decision. Recommendation: RUN the v2.2 Opus pilot as built,
when the pA quota returns — and re-scope, now and in writing, what any
outcome licenses. Confidence 0.7.** [STIPULATED ruling]

The case for running:

1. **The marginal cost is trivial and the design is bounded.** The pilot is
   funded, frozen, mock-verified; its only launch attempt died at preflight
   on pA quota, spending ~$0.12. The §4 pre-commitment caps the family: a
   second AC1 failure retires the proxy pair for A3 and leaves the human
   panel as the sole path — an endpoint the redirect would reach anyway.
   [MEASURED]
2. **The known-live pA channel does not by itself fail the gate.**
   [COUNTERFACTUAL] On the observed table, landing the seven hedge items
   while all four verb-sense items still split gives 36/40 raw agreement,
   AC1 ≈ 0.88 ≥ 0.65. The residual gate risk is Opus-4.8 introducing a new
   construal channel — real, unmeasured, and exactly what a pilot is for;
   the known-answer channels (calibration 12, hedge-flip 8, decisiveness)
   fence it.
3. **A pass buys the programme's scarcest commodity.** The instrument
   ledger is unambiguous: everything that has instrumented cleanly had a
   deterministic or externally-adjudicated channel; every judgment
   interface has failed at first contact. A validated proxy-judge pair with
   a prevalence-robust gate is reusable infrastructure — most immediately
   for re-measuring the *sense-split* materials this adjudication says must
   come, and for any ordinary-meaning channel the sparq/DDC work needs.
   Holding the pilot pending the redirect gains nothing: the rebuild needs
   the same instrument, and an unspent frozen pilot is a third zombie
   lineage on a track that already has two.
4. **A second failure is cheap information here**, retiring a pair we would
   otherwise retire by fiat and activating the human-panel path with its
   quota-cheap labour — which should then be pointed at sense-split
   materials rather than the current renders.

The re-scoping that must accompany it (this is the tradeoff, stated
plainly): a pilot PASS validates the **instrument**, not the typing; a
full-arm PASS against the 0.3929 baseline licenses only the engineering
adoption of a currently-unconsumed, rank-only module, and its soundness
number must carry a sense-scope caveat — its "unsound" cells include
word/sense confounds, so it under-states sense-scoped soundness by an
unmeasured margin. On PASS, the full arm should run within the approved
ceiling (no re-surfacing; this adjudication is the sanctioned decision
point). After this lineage closes, either way, the correctness track's
marginal measurement effort should move where section A points: an
engine-inference-under-typing instrument with a deterministic channel, and
a sense-split re-measure of the binding sorts. The next materials build —
proxy or human — must be sense-split-first; no further prose iteration on
unsplit concepts. [STIPULATED ruling; EXTRAPOLATION on the successor
instruments, resolved by their designs]

---

## Self-check gate (governance)

Tag mechanics verified: every load-bearing claim above carries MEASURED /
LIT-BACKED / STIPULATED / COUNTERFACTUAL / EXTRAPOLATION, with rulings and
design choices tagged STIPULATED, never MEASURED. Training-knowledge
citations (WordNet sense counts, FrameNet frame inventory) are disclosed as
unpinned with their pinning path named. No account handles appear. The
assumption block `asm-g2adj-1880-1889.json` uses the four registry tags
(MEASURED | LIT-BACKED | STIPULATED | EXTRAPOLATION), owner writer-4, range
1880–1889 verified free at emission (max registered id 1867; repo-wide grep
for ASM-188x empty); registration is the coordinator's, with commit. No
git actions were taken in this pass. No feasibility conclusion is stated on
either thesis. The mechanical verdicts of every cited run stand unmodified.
