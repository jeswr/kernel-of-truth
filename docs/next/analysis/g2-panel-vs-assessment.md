# g2-import-v2 A3 pilot — panel problem or assessment problem? Per-item diagnostic (Fable)

**Role: Fable ANALYSIS agent, 2026-07-12. This document is a per-item
diagnostic of the sanctioned Stage-P adoption-arm pilot
(`poc/ontology-import-g2-v2/runs/real-20260712-auth`, AC1_A3 = 0.6222 < 0.65,
mechanical verdict INSTRUMENT-INVALID with the pilot channel named). It
answers one maintainer question — is the AC1 near-miss a PANEL problem
(competent judges disagreeing on clear items) or an ASSESSMENT problem (the
typing claims genuinely ambiguous or borderline)? It states NO feasibility
conclusion on either thesis and does not revisit the mechanical verdict,
which stands.** Companion to the pilot-gate record
(`runs/real-20260712-auth/pilot-status.json`) and the v2.2 rubric-iteration
design (`docs/next/design/g2-import-v22-rubric-iteration.md`).

Epistemic tags: **[MECHANICAL]** = the pinned harness output, reported
verbatim; **[MEASURED]** = read directly from committed bytes this tick;
**[DERIVED]** = follows from measured bytes by stated arithmetic, wrong only
if the reading is; **[COUNTERFACTUAL]** = a what-if under stated assumptions,
never evidence; **[ASSESSMENT]** = this agent's judgment, one model's
opinion, never gold.

**Sources read at source:**
`poc/ontology-import-g2-v2/runs/real-20260712-auth/judge-pA-a3-pilot-responses.jsonl`
and `judge-pB-a3-pilot-responses.jsonl` (40 rows each);
`runs/real-20260712-auth/{pilot-status.json,result.json,analysis-output.json}`;
`poc/ontology-import-g2-v2/pilot-manifest.json` (the 40 pinned ids, gate
justification); `poc/ontology-import-g2/materials/arm-a3-bfo-sumo-framenet.jsonl`
(the pre-rendered A3 item texts); `poc/ontology-import-g2-v2/prompt-template-v2.txt`
(the wrapper the judges saw); `poc/ontology-import-g2-v2/run-ontg2v2.py`
(render path: `phase_pilot` loads the arm file rows and `assemble_prompt`
substitutes the row's `item` text verbatim into `{{ITEM}}`);
`data/onto-softtype/soft-type-candidates.jsonl` (concept, imported
`preferred_type`, regime/strength); for the stability read only, the
diagnostic response sets `runs/pilot-20260712-EXPLORATORY-kappa/` and
`runs/pilot-20260712-ac1/`.

---

## 1. What the judges actually saw (reconstruction) [MEASURED]

The pilot ran under the **v2 template** (`prompt-template-v2.txt`; the
`--rubric v22` flag postdates this run — no rubric flag appears in the run's
logs, and the v2.2 design names this pilot as the failure it responds to).
Each call was the fixed template with `{{ITEM}}` replaced by the arm-file
row's `item` field, verbatim (`assemble_prompt`, run-ontg2v2.py). The item
text is two lines — `Concept: “...”` then `Statement: ...` — reproduced in
the table below split across the *concept* and *rendered statement* columns,
otherwise byte-identical to what was judged. The template instructs: judge
ONLY by ordinary meaning; the parenthetical fixes the sense; unhedged
sentences claim ALL normal cases; "Normally"/"Typically" sentences claim the
usual case and are not falsified by exceptions; answer yes only if EVERY
sentence is true at its stated strength.

Two consequences of the render worth stating plainly, since the analysis
turns on them:

- **"as described above" points at nothing beyond the parenthetical.** The
  R3 statements open "In every case of “X finds Y” as described above ..." —
  but the only thing above is the Concept line itself. Where the
  parenthetical genuinely fixes a sense ("lie (the words)", "reminder (the
  made something)"), the claim is well-scoped; where it is bare ("find (X
  finds Y)", "make (X makes Y)", "break (X breaks Y)"), the verb's ordinary
  polysemy is left to the judge. [MEASURED]
- **No gold exists for these 40 items.** They are real A3 items — the
  measurement target. I verified the absence of any expected/gold field in
  the arm file, `soft-type-candidates.jsonl`, and the probe files; the
  `expected: no` labels in `probes-hedgeflip-a3.jsonl` attach to the
  hedge-FLIPPED variants of some of these items, not to the originals. The
  gold column below is therefore honestly empty. [MEASURED]

## 2. Headline pair structure [MECHANICAL / MEASURED]

| quantity | value |
|---|---|
| items | 40 (R3=20, R4=16, R1=4) |
| both yes | 28 |
| both no | 1 (g2:pi:011) |
| pA yes / pB no | 7 (g2:pi:016, 021, 025, 033, 064, 068, 089) |
| pA no / pB yes | 4 (g2:pi:036, 037, 070, 071) |
| raw agreement | 29/40 = 0.725 |
| marginals (yes) | pA 35/40 = 0.875; pB 32/40 = 0.800 |
| AC1 (gated, min 0.65) | **0.6222** — FAIL |
| Cohen κ (co-reported, never gated) | −4.0e−16 ≈ 0 |
| PABAK | 0.45; p_pos 0.836, p_neg 0.154 |
| known-answer channels | calibration 12/12; hedge-flip false-sat 0/8 (pA) and 0/8 (pB); decisive 40/40 both |

Eleven disagreements, all one item deep in opposite directions: seven where
GPT-5.6 accepts and Haiku rejects, four the reverse.

## 3. The per-item table [MEASURED verdicts; Fable column ASSESSMENT]

Disagreements first (pA-yes/pB-no block, then pA-no/pB-yes), then the lone
both-no item, then the 28 both-yes items, each block in id order. The Fable
column is my own sound/unsound judgment of the rendered claim under the same
v2 ordinary-meaning rubric — one model's opinion, tagged [ASSESSMENT]
throughout, offered as a tie-breaker signal and never as gold.

| item | rule/form | concept as judged (sense-fixing parenthetical included) | imported preferred type (anchor) | rendered statement (verbatim; the claim judged) | gold | pA GPT-5.6-Sol | pB Haiku-4.5 | agree? | Fable verdict + rationale |
|---|---|---|---|---|---|---|---|---|---|
| 016 | R3/range | “cause (happening X causes happening Y)” | occurrent (BFO_0000003) | In every case of “cause (happening X causes happening Y)” as described above, Y is something that happens or comes about — a happening or outcome, not a lasting object, a place, or a time. Normally Y is a happening that would not have come about, or not in that way, without X. Typically Y comes after X, or while X is going on — not before. | — | yes | no | **DISAGREE** | **sound** — Y's happening-hood is fixed by the parenthetical; counterfactual dependence and X-before-Y describe the usual run of causes, and '— not before' sits inside the 'Typically' hedge. pB reads the tacked-on contrast at unhedged strength. Sides with pA. |
| 021 | R4/existential | “change (the event)” | continuant (BFO_0000002) | In every case of a change, there is something that changes — something that was one way before, and another way after. Normally that something is there both before and after — it lasts through the change. Typically one can say what it was like at first and what it became. | — | yes | no | **DISAGREE** | **sound (lean)** — 'something that changes' is near-analytic of the event sense; persistence through the change is only hedged. Creation/destruction edges make the first sentence genuinely arguable. Sides with pA. |
| 025 | R4/existential | “condolence (the words)” | role (BFO_0000023) | In every case of a condolence, the words are offered to someone — there is one the condolence is for. Normally that one is a person other than the one speaking — the bereaved or the one suffering the loss. Typically the words are addressed to that person directly. | — | yes | no | **DISAGREE** | **sound (lean)** — A recipient is analytic to condolence; direct address (spoken, card, letter) is the usual case, though 'Typically ... directly' is honestly borderline against relayed condolences. Sides with pA. |
| 033 | R3/domain | “end (happening X ends at time T)” | occurrent (BFO_0000003) | In every case of “end (happening X ends at time T)” as described above, X is something that happens or goes on in time (a happening or process) — not a person, a place, or a time. Normally X is the kind of happening that was going on for some time before it ended. Typically after T, the happening X is no longer going on. | — | yes | no | **DISAGREE** | **sound** — All three sentences are near-analytic of 'X ends at T'; no principled 'no' found — the clearest of pB's seven. Sides with pA. |
| 064 | R4/existential | “lie (the words)” | role (BFO_0000023) | In every case of a lie, someone tells it — there is the one whose words they are. Normally a person speaking or writing. Typically the teller knows the words are not true. | — | yes | no | **DISAGREE** | **sound** — A lie (the words) entails a teller; knowing falsity is near-definitional, so 'Typically' carries easily. Likely trigger: the subject-less hedged fragment 'Normally a person speaking or writing.' Sides with pA. |
| 068 | R4/existential | “lost” | quality (BFO_0000019) | Whenever someone or something is lost, being lost is how things now stand with it — it cannot be found by, or does not know its way to, those it matters to. Normally this came about through an earlier losing — someone lost it, or it lost its way. Typically no one who matters to it knows where it is. | — | yes | no | **DISAGREE** | **sound (lean)** — The ordinary lost case satisfies the long unhedged disjunctive gloss, but 'cannot be found by ... those it matters to' is the strongest unhedged composite in the pilot and a strict parse is defensible. One of the two least-stable items (pA flipped it once, in the ac1 response set). Sides with pA. |
| 089 | R4/existential | “reminder (the made something)” | process (BFO_0000015) | In every case of a reminder, it was made or set up — something was done so that someone will call something back to mind. Normally by someone — a person — often through a tool or device that then does the reminding. Typically there is the one to be reminded, and the thing to be brought back to mind. | — | yes | no | **DISAGREE** | **sound** — '(the made something)' fixes the sense, making 'was made or set up' analytic; natural-sign reminders (a scar) fall outside the fixed sense. Likely trigger: the double-hedged fragment 'Normally by someone — ... often through a tool or device ...'. Sides with pA. |
| 036 | R3/domain | “find (X finds Y)” | independent continuant (BFO_0000004) | In every case of “find (X finds Y)” as described above, X is the one that does the finding — someone or something that can look for things or come upon them; not a time or a place. Normally X is a person, or an animal or other being that can perceive. Typically X was looking for Y, or at least comes to know where Y is. | — | no | yes | **DISAGREE** | **sound (lean)** — Under the central sense a finder perceives or comes upon; 'X is a time' occurs only in the marked literary construction ('morning found him at his desk'), fairly excluded. The bare parenthetical leaves the sense open, so a principled 'no' exists. Sides with pB. |
| 037 | R3/range | “find (X finds Y)” | entity (BFO_0000001) | In every case of “find (X finds Y)” as described above, Y is what is found — something that was not in view, or not known to be where it is, and then is. Normally Y is a thing, but it can be a person, an animal, a place, or even something like an answer. Typically Y is somewhere — the finding fixes where it is. | — | no | yes | **DISAGREE** | **sound (lean)** — Abstract finds (an answer, a flaw) satisfy the unhedged gloss only on a charitable reading, and 'found it where I left it' strains 'not known to be where it is'. Borderline; the whole picture of the usual case is right. Sides with pB. |
| 070 | R3/range | “make (X makes Y)” | entity (BFO_0000001) | In every case of “make (X makes Y)” as described above, Y is what is made — something that comes to be through the making. Normally Y is a thing one can point to afterwards — an object, a stuff, a work. But Y can also be words, a plan, or a happening — one can make a promise, or make trouble. | — | no | yes | **DISAGREE** | **sound (lean)** — The statement's own third sentence licenses words, plans and happenings, and the imported type (entity, the BFO top) excludes nothing; the claim fails only if non-creation idioms ('make the bed', 'make the train') are in scope — which the bare parenthetical does not settle. Sides with pB. |
| 071 | R4/existential | “make (X makes Y)” | temporal region (BFO_0000008) | In every case of “make (X makes Y)” as described above, the making happens at some time — there is a time at which it takes place. Normally one can say when it happened, at least roughly. | — | no | yes | **DISAGREE** | **sound** — Schema-matched to birth (g2:pi:006) and death (g2:pi:032), which pA passed in every response set; 'at some time ... at least roughly' covers extended makings. pA's 'no' is inconsistent with its own matched-schema verdicts — the cleanest panel-side datum (and, with 068, pA's only cross-run instability). Sides with pB. |
| 011 | R3/range | “break (X breaks Y)” | material entity (BFO_0000040) | In every case of “break (X breaks Y)” as described above, Y is a thing that can be in one piece and then not — something with a body or material to it, not a time and not a bare idea. Normally Y is a whole object — one thing that comes apart or stops holding together. Typically the breaking leaves pieces, or leaves Y no longer working as it should. | — | no | no | agree | **unsound** — Concur with both judges. 'Break a promise / the silence / a record' are frequent ordinary uses; the unhedged 'body or material to it' gloss fails them, and the bare parenthetical does not fix the physical sense. |
| 000 | R4/existential | “archived (bookmark boolean property)” | process (BFO_0000015) | Whenever someone or something is archived, an archiving happened — something took place in time by which it was put away for keeping. Normally this putting-away is done on purpose, so that the thing is kept but out of the way. Typically there is someone — or a tool or system acting for someone — that does the archiving, the thing archived, and a place or collection where it is kept. | — | yes | yes | agree | **sound** — Sense-fixed to the bookmark property; an archiving event is entailed, the rest properly hedged. |
| 004 | R3/range | “believe (X believes Y)” | generically dependent continuant (BFO_0000031) | In every case of “believe (X believes Y)” as described above, Y is something that can be thought — a content, the kind of thing that could also be put into words. Normally Y is something that can be so or not so — the kind of content that can be true or false. Typically Y, the content believed, can be about anything — a person, a place, a thing, or another happening. | — | yes | yes | agree | **sound** — Thinkable, truth-apt content is analytic of the described sense. |
| 005 | R1/subClassOf | “birth (the event)” | process (BFO_0000015) | Every birth is a happening — something that takes place in time (an event), not a lasting object. Normally a birth is a bodily happening in the life of a living thing. Typically a birth involves the one who is born (a child or young), and it happens at some time and place. | — | yes | yes | agree | **sound** — Event-hood analytic; bodily character and participants properly hedged. |
| 006 | R4/existential | “birth (the event)” | temporal region (BFO_0000008) | In every case of a birth, it happens at some time — there is a time at which the birth takes place. Normally one can say when it happened, at least roughly. | — | yes | yes | agree | **sound** — Events are datable 'at least roughly'. |
| 014 | R4/existential | “broken” | quality (BFO_0000019) | Whenever someone or something is broken, being broken is a way that thing now is — a condition of it, not something separate from it. Normally it is broken because at some earlier time a breaking happened to it. Typically a broken thing no longer holds together or no longer works as it should. | — | yes | yes | agree | **sound** — Condition-hood analytic; the earlier breaking is the usual case. |
| 018 | R1/subClassOf | “celebration” | process (BFO_0000015) | Every celebration is a happening — something people do that takes place in time (an event). Normally it is a social happening: people together doing something because something good happened or matters to them. Typically there are people taking part — those attending or celebrating. | — | yes | yes | agree | **sound** — Event-hood analytic; social character properly hedged. |
| 020 | R4/existential | “celebration” | process (BFO_0000015) | In every case of a celebration, something happens — there are things done as part of it. Normally these are things people do on purpose — the celebrating itself. Typically this includes doings shared by those taking part. | — | yes | yes | agree | **sound** — That things are done as part of it is analytic. |
| 023 | R1/subClassOf | “condolence (the words)” | generically dependent continuant (BFO_0000031) | Every condolence is something said — words, spoken or written, offered to someone. Normally the words say that the one offering them feels for someone over something bad — most often a death or a loss. Typically there is a message with a content, and a way it is given — said, written, or sent. | — | yes | yes | agree | **sound** — '(the words)' fixes the said-words sense; flowers-as-condolence excluded. |
| 032 | R4/existential | “death (the event)” | temporal region (BFO_0000008) | In every case of a death, it happens at some time — there is a time at which the death takes place. Normally one can say when it happened, at least roughly. | — | yes | yes | agree | **sound** — As g2:pi:006. |
| 034 | R3/range | “end (happening X ends at time T)” | temporal region (BFO_0000008) | In every case of “end (happening X ends at time T)” as described above, T is a time — a moment or stretch of time. Normally T is thought of as the moment the happening stops. Typically nothing of X goes on after T. | — | yes | yes | agree | **sound** — T's time-hood analytic; both hedged sentences near-analytic. |
| 040 | R3/domain | “friend (X is a friend of Y)” | material entity (BFO_0000040) | In every case of “friend (X is a friend of Y)” as described above, X is a being one can have a bond with — someone, not a mere thing, a time, or a place. Normally X is a person; people also speak of animals, or of groups, as friends. Typically X is one of two or more who like each other and are close. | — | yes | yes | agree | **sound** — A bond-capable being; personhood properly hedged. |
| 041 | R3/range | “friend (X is a friend of Y)” | material entity (BFO_0000040) | In every case of “friend (X is a friend of Y)” as described above, Y is a being one can have a bond with — someone, not a mere thing, a time, or a place. Normally Y is a person; people also speak of animals, or of groups, as friends. Typically Y is one of two or more who like each other and are close. | — | yes | yes | agree | **sound** — Symmetric twin of g2:pi:040. |
| 044 | R4/existential | “gift” | process (BFO_0000015) | In every case of a gift, a giving is in play — the gift is given, or meant to be given. Normally the giving is done freely, with nothing owed for it. Typically there is the giver, the gift itself, and the one it goes to. | — | yes | yes | agree | **sound (lean)** — 'or meant to be given' absorbs the unopened-gift edge; the talent sense ('a gift for music') is a distinct sense a strict reader could press against the bare concept label. |
| 046 | R3/range | “give (X gives Y to someone)” | entity (BFO_0000001) | In every case of “give (X gives Y to someone)” as described above, Y is what is given — something that can go from one to another. Normally Y is a thing that can be had or kept. But Y can also be something like help, time, words, or care. | — | yes | yes | agree | **sound** — 'But Y can also be ...' is a possibility claim and true. |
| 053 | R3/domain | “help (X helps Y)” | entity (BFO_0000001) | In every case of “help (X helps Y)” as described above, X is what does the helping — someone or something that makes things better or easier for Y. Normally X is a person or other being acting on purpose. But X can also be a thing or a happening that helps — a tool, a medicine, a change. | — | yes | yes | agree | **sound** — Helper gloss wide enough for tools, medicines, happenings. |
| 059 | R3/domain | “learn (X learns Y)” | independent continuant (BFO_0000004) | In every case of “learn (X learns Y)” as described above, X is the learner — someone or something that can come to know; not a time, a place, or a mere thing. Normally X is a person or other being with a mind — an animal can learn too. Typically after the learning, X knows Y or can do Y. | — | yes | yes | agree | **sound** — 'can come to know' properly covers animals and arguably machines. |
| 060 | R3/range | “learn (X learns Y)” | generically dependent continuant (BFO_0000031) | In every case of “learn (X learns Y)” as described above, Y is what is learned — something that can be known or done: a fact, a skill, a way. Normally Y is content one can carry in mind — knowledge or know-how. Typically Y can be about anything — persons, places, things, happenings. | — | yes | yes | agree | **sound** — Learnable content — fact, skill, way — analytic. |
| 062 | R1/subClassOf | “lie (the words)” | generically dependent continuant (BFO_0000031) | Every lie is something said — made of words, spoken or written. Normally the words say something the one saying them takes to be not true. Typically it is said to someone, about something. | — | yes | yes | agree | **sound** — '(the words)' fixes the sense; 'living a lie' excluded. |
| 065 | R3/domain | “lose (X loses Y)” | independent continuant (BFO_0000004) | In every case of “lose (X loses Y)” as described above, X is the one who loses — someone or something that had Y and then does not. Normally X is a person, or a group, to whom Y belonged or mattered. Typically X can no longer find Y, or no longer has it. | — | yes | yes | agree | **sound** — Had-then-does-not analytic of the described sense. |
| 073 | R3/domain | “maker of (X is the maker of Y)” | entity (BFO_0000001) | In every case of “maker of (X is the maker of Y)” as described above, X is the maker of Y — the one that brought Y into being. Normally X is a person or people. But a maker can also be a firm, a machine, or nature at work. | — | yes | yes | agree | **sound** — 'But a maker can also be ...' is a possibility claim and true. |
| 074 | R3/range | “maker of (X is the maker of Y)” | entity (BFO_0000001) | In every case of “maker of (X is the maker of Y)” as described above, Y is what was made — something that came to be through X’s making. Normally Y is a thing one can point to — an object, a stuff, a work. But Y can also be words, a plan, or a happening that X brought about. | — | yes | yes | agree | **sound** — The same breadth pA disputed at g2:pi:070, here uncontested by both judges. |
| 075 | R4/existential | “maker of (X is the maker of Y)” | process (BFO_0000015) | In every case of “maker of (X is the maker of Y)” as described above, a making happened — Y came to be through it, at some time. Normally the making was done by X on purpose. Typically the making came before Y’s being there. | — | yes | yes | agree | **sound** — A making event analytic; purpose and temporal priority hedged. |
| 077 | R4/existential | “memory (a stored something)” | generically dependent continuant (BFO_0000031) | In every case of a memory, the memory is of something — there is something it keeps or is about. Normally something from before — a happening, a person, a place, a fact — as it was taken in. Typically the one whose memory it is can bring that content back to mind. | — | yes | yes | agree | **sound** — Aboutness analytic of the stored-memory sense. |
| 080 | R3/domain | “part of (X is part of Y)” | entity (BFO_0000001) | In every case of “part of (X is part of Y)” as described above, X is a part — something that belongs to Y and helps make it up; it can be a thing, a person, a place, or even a happening. Normally X is a smaller piece or portion of the whole. Typically X is where Y is — the part is not somewhere else than its whole. | — | yes | yes | agree | **sound** — Part-hood analytic; colocation only 'Typically'. |
| 081 | R3/range | “part of (X is part of Y)” | entity (BFO_0000001) | In every case of “part of (X is part of Y)” as described above, Y is a whole — something the part belongs to; it can be a thing, a person, a place, or even a happening. Normally Y is one thing whose parts belong to it and make it up. Typically Y is not less than X: the whole is at least its part. | — | yes | yes | agree | **sound** — Whole-hood analytic; 'not less than' hedged and true. |
| 084 | R4/existential | “promise (the words)” | role (BFO_0000023) | In every case of a promise, someone makes it — there is the one who gives their word. Normally a person, or a group speaking as one. Typically the maker of the promise is then bound by it. | — | yes | yes | agree | **sound** — A promiser is analytic; bindingness the typical case. |
| 086 | R3/range | “remember (X remembers Y)” | generically dependent continuant (BFO_0000031) | In every case of “remember (X remembers Y)” as described above, Y is what is remembered — something that can be held in mind: a fact, a happening, a person, a place, a thing to do. Normally Y is content from before — something X knew, saw, or went through. Typically Y comes back to X’s mind as it was taken in. | — | yes | yes | agree | **sound** — Memorable-content gloss analytic; provenance and fidelity hedged. |
| 090 | R4/existential | “reminder (the made something)” | generically dependent continuant (BFO_0000031) | In every case of a reminder, there is something it is meant to bring back to mind — the reminder is about, or for, something else. Normally something to be done, or something not to be forgotten. Typically that something is distinct from the reminder itself. | — | yes | yes | agree | **sound** — Aboutness analytic under the sense-fix; distinctness typical. |

## 4. Analysis: panel problem or assessment problem?

### 4.1 The disagreements are deterministic, not noise [MEASURED]

The same 40 items were answered by the same judge pair in three response
sets on 2026-07-12 (the quarantined EXPLORATORY set, the `pilot-20260712-ac1`
diagnostic set, and the sanctioned `real-20260712-auth` set — only the last
is gate-bearing; the others are read here purely as stability evidence).
Across 120 re-answers per judge: pA flipped 2 (g2:pi:068 and g2:pi:071, in
the ac1 set only), pB flipped 1 (g2:pi:081, exploratory only). All 11
sanctioned-pilot disagreements recur in the exploratory set; 9 of the 11
recur in all three sets with zero flips by either judge. A "panel problem"
in the noise sense — competent judges answering unstably — is ruled out by
the data: each judge is applying a fixed, repeatable criterion. What differs
is the criterion.

### 4.2 At the pair level the shared signal is exactly zero [DERIVED]

Raw agreement is 29/40 = 0.725. Chance agreement at the observed marginals
is 0.875·0.800 + 0.125·0.200 = 0.725 — **identical**, which is why κ is zero
to machine precision, and why the both-no cell (1) exactly equals its
independence expectation (5·8/40 = 1.0). The two judges' "no"-sets overlap
in a single item; statistically they are unrelated draws. Note also that
AC1 at marginal-matched independence equals the observed 0.6222 at these
marginals: the near-miss is not "almost enough shared signal" — above what
the yes-rates force, there is none. This is the κ≈0/high-prevalence caveat
in one line: at prevalence ≈ 0.84 raw agreement of 72.5% *looks* healthy
and AC1 0.62 *looks* like a near-miss, but the between-judge information
lives entirely in the rare no-calls, and there the panel is orthogonal.
(This is precisely why the gate was moved from κ to AC1 with the 0.65 floor
above the independence ceiling — pilot-manifest.json,
`ac1_threshold_justification`.)

### 4.3 Where the eleven disagreements actually come from [ASSESSMENT]

My own reads (table above) find **all eleven disputed rendered claims sound**
— I side with whichever judge said yes: with pA on all seven of its
yes-items, with pB on all four of its yes-items. On my read the pilot
contains eleven one-sided false rejections, produced by two different and
internally consistent strictness policies:

- **pB channel (7 items: 016, 021, 025, 033, 064, 068, 089) —
  composite-hedge strictness.** All seven are R4 existentials (021, 025,
  064, 068, 089) or three-sentence R3 composites (016, 033), carrying
  exactly the forms the v2 template
  under-specifies: a tacked-on contrast inside a hedge ("Typically Y comes
  after X ... — not before", 016), subject-less hedged fragments ("Normally
  a person speaking or writing.", 064; "Normally by someone — a person —
  often through a tool or device ...", 089), and long unhedged dashed glosses
  (021, 068). Haiku reads parts of these at unhedged strength, or demands
  each linked detail hold separately. This is the channel the v2.2
  composite-hedge clarification and the two new calibration anchors were
  built against; the diagnosis here independently supports that targeting.
- **pA channel (4 items: 036, 037, 070, 071) — verb-sense scoping.** All
  four are bare-parenthetical polysemous verbs (find ×2, make ×2) where "as
  described above" resolves to nothing beyond "X finds Y" / "X makes Y".
  GPT-5.6 lets non-central senses ("make the bed", "morning found him") into
  the unhedged ALL-cases quantifier and rejects; Haiku defaults to the
  central sense and accepts. Both readings are principled; the render leaves
  the choice open. The exception is **g2:pi:071**, where pA's "no" clashes
  with its own "yes" on the schema-matched birth (006) and death (032)
  items in every response set — the one clean case of within-judge
  inconsistency on a clear item, and (with 068) one of only two items where
  any cross-run flip occurred at all.

Against this, the panel's competence on determinate items is intact:
calibration 12/12, hedge-flip probes rejected 8/8 by both judges with zero
false satisfaction, and the one genuinely unsound real item in the pilot
(g2:pi:011, break→material-entity, where "break a promise" defeats the
unhedged material gloss) drew a correct **no from both judges** — the only
both-no cell in the table, and the one disputed-adjacent item where my own
verdict is also unsound.

### 4.4 Answer to the maintainer's question [ASSESSMENT]

**Predominantly an assessment problem, in a specific and fixable sense — and
the maintainer's dichotomy needs one refinement to be answered honestly.**
Three readings must be separated: (i) the *typings* are genuinely borderline;
(ii) the *rendered claims* admit two principled construals; (iii) the judges
are unreliable on clear items. The evidence sorts almost everything into
(ii): the underlying imported typings at the eleven disagreement items are,
on my read, all sound (and mostly anodyne — several disputed items import
`entity`, the BFO top, which excludes nothing); what is ambiguous is the
natural-language rendering — hedge-scope in multi-clause composites (pB's
seven) and verb-sense scope under bare parentheticals (pA's four). Reading
(iii) — the panel problem proper — is contradicted by near-perfect
determinism, perfect known-answer channels, and convergence on the one
clearly unsound item; it survives only as a residue at g2:pi:071 (pA's
matched-schema inconsistency) and arguably 068, call it 1–2 items of 11.
Reading (i) — genuinely borderline typing claims — describes at most the
find/make cluster, and even there the type content is trivially satisfiable;
the ambiguity is in the gloss, not the type.

Two consequences, tagged: **[COUNTERFACTUAL]** if either channel alone were
closed and nothing else changed, the pilot table passes the gate — repairing
pB's seven gives AC1 ≈ 0.88; repairing pA's four gives AC1 ≈ 0.78; both
clear 0.65 (arithmetic on the observed table under stated substitutions,
never evidence about a future run). **[ASSESSMENT]** the v2.2 instrument as
designed addresses the pB channel only; the pA verb-sense channel (4 of 11)
is untouched by a composite-hedge clarification, and — being deterministic —
will recur. If a second sanctioned pilot is spent (the recorded
pre-commitment retires this judge pair on a second AC1 fail), the render or
rubric should first pin verb sense where the parenthetical is bare, e.g. by
making "as described above" point at an actual sense description.

### 4.5 Caveats on this document's own verdict column [ASSESSMENT]

My verdicts are one Fable-model read under the same rubric, produced from
the same rendered text the judges saw. Three disclosed weaknesses: (a)
vendor-family overlap — the A3 renders were authored inside this programme
and pB is a same-vendor model, so my agreement with any party is a signal,
not adjudication; the two-human adjudicated gold remains the sole authority
(run disclosure, result.json). (b) My column is yes on 39/40 — more lenient
than either judge (35, 32); a yes-biased tie-breaker would look exactly like
this, so the per-item rationales, not the tally, are the evidence. (c) Where
I mark "(lean)" the opposite verdict is defensible under the same rubric —
that defensibility is itself the finding. No feasibility conclusion is
stated or implied; the INSTRUMENT-INVALID mechanical verdict and the
discard of pilot labels from scoring stand untouched.
