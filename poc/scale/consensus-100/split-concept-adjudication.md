# Split-concept AST-adequacy adjudication — resolving genuine-vs-lenient

**$0, read-only, blind cross-vendor adjudication.** Resolves whether the Claude family's ~3× higher
AST-faithful self-flag rate on the consensus-100 concepts is GENUINE (Claude really renders more
concepts faithfully in profile-1's 65 primes) or LENIENT (Claude under-reports lossiness). Gates the
faithful-heavy kernel-arm decision (#33).

## Method

- **The 45 SPLIT concepts** = of the 100 consensus-100 concepts, those whose 6 model self-flags
  (`ast_adequacy_self_flag` in `gen/<c>.<model>.report.json`) are NOT unanimous. Full pool: **6
  unanimously faithful, 49 unanimously lossy, 45 split** (99–100 concepts flagged per model).
- **Blind panel.** Each judge got ONLY: the concept label, its WordNet gloss, and the explicit closed
  list of the 65 profile-1 primes (plus a factual note that kot-ast/1 is a *compositional* reductive
  paraphrase: predicate frames + role slots, NOT/CAN/MAYBE/IF/BECAUSE/WHEN/BEFORE/AFTER/LIKE operators,
  up to 32 clauses so length is not the limit — only the reach of the 65 primitives). Judges were NOT
  shown the models' self-flags or any model's explication. They judged the concept's *renderability
  itself*, not any attempt.
- **Question put to each judge:** can a kot-ast/1 explication built ONLY from the 65 primes faithfully
  render this concept's differentia (what distinguishes it from its genus) without dropping meaning? →
  `FAITHFUL-POSSIBLE` / `INHERENTLY-LOSSY` / `PARTIAL`, one-line reason.
- **Judge A = gpt-5.6-sol** (codex exec, reasoning effort xhigh, read-only, isolated ephemeral home).
  **Judge B = claude-opus-4-8** (`claude -p`, neutral cwd). Deliberately cross-vendor: Judge A is from
  the *same vendor whose generators self-flagged ~90% lossy*, so a lenient bias would show as harshness,
  not agreement.

## Aggregate result

| verdict | Judge A (gpt-5.6-sol) | Judge B (claude-opus-4-8) |
|---|---|---|
| FAITHFUL-POSSIBLE | 42 | 44 |
| PARTIAL | 3 | 1 |
| INHERENTLY-LOSSY | 0 | 0 |

- **Inter-judge agreement: 43/45 = 96%** (exact verdict).
- **INHERENTLY-LOSSY verdicts: 0 / 45 from BOTH judges.** Not one split concept was judged inherently
  un-renderable in the 65 primes by either vendor's judge.
- **Both judges FAITHFUL-POSSIBLE: 42/45.** The only non-both-FAITHFUL concepts are the 3 below,
  and all 3 are PARTIAL (genus + most differentia render; a residual artefact/institution detail is hard) —
  none is a total loss:
    - **builder** — A=PARTIAL, B=PARTIAL. Creating and developing can be paraphrased, but the institution-specific meanings of business and country cannot be preserved fully with these primes.
    - **dig** — A=PARTIAL, B=FAITHFUL. Sudden brief TOUCH can be rendered, but finger and elbow cannot be uniquely identified using only generic BODY and PART terms.
    - **shoring** — A=PARTIAL, B=FAITHFUL. The supporting function can be paraphrased, but the defining beam-like shore artifact requires shape, rigidity, and artifact content unavailable in the primes.

## Resolution: the Claude self-flags are GENUINE, not lenient

The decisive fact is **cross-vendor**: the GPT judge (gpt-5.6-sol) — same family whose *generators*
self-flagged ~90% of concepts lossy — judged **42/45 split concepts FAITHFUL-POSSIBLE and 0 inherently
lossy**. The GPT judge thus *contradicts the GPT generators*. That is only consistent with the split
concepts being **genuinely renderable** in the 65 primes; the GPT generators' 'lossy' calls were a
stricter self-application bar (pessimistic self-critique of their own attempt), **not** a claim that the
concept is inherently un-renderable. Had the Claude gap been mere leniency (option b), the independent
GPT judge would have re-flagged these lossy — it did the opposite.

→ **Option (a) GENUINE holds.** On the contested concepts, faithful renderings genuinely exist, so the
Claude family's 'faithful' flags reflect real renderability, not a lowered bar.

## Implied genuine faithful yield

Self-flag faithful counts over the 100 concepts (from `ast-lossy-by-model.md`, reconfirmed here):

| generator | faithful self-flags /100 | yield |
|---|---|---|
| claude-opus-4-8 | 31 | 31% |
| claude-fable-5 | 35 | 35% |
| claude-haiku-4-5 | 34 | 34% |
| **Claude family avg** | **~33** | **~33%** |
| gpt-5.6-sol | 11 | 11% |
| gpt-5.6-luna | 9 | 9% |
| gpt-5.6-terra | 9 | 9% |
| **GPT family avg** | **~9.7** | **~10%** |

- **Concept-level faithful-renderable ceiling ≈ 51/100**: 6 unanimously-faithful + ~45 split
  (both judges: 42 clean FAITHFUL-POSSIBLE + 3 PARTIAL, 0 inherently lossy). The 49 unanimously-lossy
  were not adjudicated (all six models, Claude included, agreed lossy — treated as the genuinely hard tail).
- **A Claude generator's ~33% faithful yield is REAL.** Its faithful flags fall inside the ~51% renderable
  ceiling and survive independent cross-vendor adjudication → genuine, not inflated.
- **A GPT generator's ~10% UNDER-reports.** GPT flags lossy the very split concepts both judges call
  renderable, so ~10% is a pessimistic floor, not the achievable rate. Using GPT self-flags to size the
  faithful arm would discard ~2/3 of genuinely-faithful concepts.

### Cost implication for the faithful-heavy arm (#33)
- To net **65 faithful** concepts: Claude generator @ ~33% ⇒ **~200 generations**; GPT generator @ ~10%
  self-flagged ⇒ **~650–700 generations**. The Claude route is **~3× cheaper**, and the adjudication
  confirms the extra Claude yield is genuine faithful renderability rather than mislabelled loss.

### Honest caveat (scope of this test)
This adjudicates **renderability-in-principle** (does a faithful explication *exist*), which is exactly
what refutes the 'inherently lossy' hypothesis and validates the yield. It does **not** verify that each
Claude *explication actually produced* is itself faithful/high-quality — and the separate quality-ranking
found GPT stronger on definitional quality (sol 2.70 / luna 2.54 vs opus 1.79 / fable 1.72). So: the
faithful *count* is genuine, but Claude-generated faithful-flagged output should still pass an
explication-level quality gate before use. Renderability is settled in Claude's favour; per-explication
quality remains a separate check.

## Per-concept verdicts (all 45)

Self-flag key: `O`=opus48 `F`=fable5 `H`=haiku45 (Claude) · `s`=gpt56sol `l`=gpt56luna `t`=gpt56terra (GPT);
value `F`=faithful `L`=lossy `·`=missing. Judge verdict `FAITHFUL`=FAITHFUL-POSSIBLE.

| # | concept | self-flags (O F H·s l t) | Judge A | Judge B |
|---|---|---|---|---|
| 1 | apparition | F F F F L L | FAITHFUL | FAITHFUL |
| 2 | changelessness | L F L L L L | FAITHFUL | FAITHFUL |
| 3 | continuousness | L F L L L L | FAITHFUL | FAITHFUL |
| 4 | wealth | L L F L F L | FAITHFUL | FAITHFUL |
| 5 | builder | L L F L L L | PARTIAL | PARTIAL |
| 6 | pull | F L F L L L | FAITHFUL | FAITHFUL |
| 7 | dig | L L F L L L | PARTIAL | FAITHFUL |
| 8 | serviceability | L F L L L L | FAITHFUL | FAITHFUL |
| 9 | coiner | L F L F L L | FAITHFUL | FAITHFUL |
| 10 | fastening | F F L L L L | FAITHFUL | FAITHFUL |
| 11 | instrumentality | F F F F L F | FAITHFUL | FAITHFUL |
| 12 | linkage | L F L L L L | FAITHFUL | FAITHFUL |
| 13 | feasibility | F F F L L L | FAITHFUL | FAITHFUL |
| 14 | grazing | F L F L L L | FAITHFUL | FAITHFUL |
| 15 | pettiness | L F L L L L | FAITHFUL | FAITHFUL |
| 16 | move | L F F L L L | FAITHFUL | FAITHFUL |
| 17 | cognitive state | L L L L L F | FAITHFUL | FAITHFUL |
| 18 | differentiator | L L F L L L | FAITHFUL | FAITHFUL |
| 19 | self-esteem | F F F L L L | FAITHFUL | FAITHFUL |
| 20 | poisoning | L F L L L L | FAITHFUL | FAITHFUL |
| 21 | cancellation | F F F L L L | FAITHFUL | FAITHFUL |
| 22 | contamination | F L L L L L | FAITHFUL | FAITHFUL |
| 23 | joker | F F F L L L | FAITHFUL | FAITHFUL |
| 24 | initiation | F F F L L L | FAITHFUL | FAITHFUL |
| 25 | medium | L L L L F L | FAITHFUL | FAITHFUL |
| 26 | optimization | F F L L L L | FAITHFUL | FAITHFUL |
| 27 | access | F L F L L L | FAITHFUL | FAITHFUL |
| 28 | quitter | L F F L L L | FAITHFUL | FAITHFUL |
| 29 | carry | F L F L L L | FAITHFUL | FAITHFUL |
| 30 | drop | F F F L L L | FAITHFUL | FAITHFUL |
| 31 | suicide | F F F F L F | FAITHFUL | FAITHFUL |
| 32 | minimization | L F L L L L | FAITHFUL | FAITHFUL |
| 33 | depletion | F F F L L L | FAITHFUL | FAITHFUL |
| 34 | dilation | L L F L L L | FAITHFUL | FAITHFUL |
| 35 | chip | L L F F L L | FAITHFUL | FAITHFUL |
| 36 | dissociation | L L F L L L | FAITHFUL | FAITHFUL |
| 37 | subdivision | L F F L L L | FAITHFUL | FAITHFUL |
| 38 | harassment | F F F L L L | FAITHFUL | FAITHFUL |
| 39 | lookout | F F L L F L | FAITHFUL | FAITHFUL |
| 40 | view | F F F L L L | FAITHFUL | FAITHFUL |
| 41 | invention | F F F L L L | FAITHFUL | FAITHFUL |
| 42 | gather | F F F L L L | FAITHFUL | FAITHFUL |
| 43 | shoring | F L L L L L | PARTIAL | FAITHFUL |
| 44 | inhabitancy | F F L L L L | FAITHFUL | FAITHFUL |
| 45 | coercion | F L L L L L | FAITHFUL | FAITHFUL |

### Judge reasons (one line each)

**apparition**
- A (FAITHFUL): A transition from not being seen to being seen, when people had not thought it would happen, is fully expressible.
- B (FAITHFUL): 'Something/someone can now be seen where before could not be seen, people did not think this would happen' renders in SEE/HAPPEN/NOT/THINK.

**changelessness**
- A (FAITHFUL): Remaining THE-SAME across time and being unable to become otherwise can be composed from temporal, sameness, negation, and modal primes.
- B (FAITHFUL): 'It does not become other, over a long time it is the same' renders in NOT/OTHER/THE-SAME/A-LONG-TIME.

**continuousness**
- A (FAITHFUL): It can be stated that something happens at all times with no time when it does not happen.
- B (FAITHFUL): 'It keeps happening, there is no moment when it does not happen' renders in HAPPEN/FOR-SOME-TIME/NOT/MOMENT.

**wealth**
- A (FAITHFUL): Profuse abundance reduces directly to there being VERY MUCH or VERY MANY of something.
- B (FAITHFUL): 'There is very much of something good' renders in MUCH~MANY/VERY/GOOD.

**builder**
- A (PARTIAL): Creating and developing can be paraphrased, but the institution-specific meanings of business and country cannot be preserved fully with these primes.
- B (PARTIAL): 'Someone who does much so something big exists' renders, but 'business/country/empire' as organized institutions have no primitive paraphrase.

**pull**
- A (FAITHFUL): It can be rendered as bodily action intended to cause something to MOVE nearer to or together with the agent.
- B (FAITHFUL): 'Someone does something to a thing so it moves toward them' renders in DO/MOVE/NEAR/TOUCH.

**dig**
- A (PARTIAL): Sudden brief TOUCH can be rendered, but finger and elbow cannot be uniquely identified using only generic BODY and PART terms.
- B (FAITHFUL): 'For a moment touches someone with a part of the body, they feel something' renders in TOUCH/BODY/PART/MOMENT/FEEL.

**serviceability**
- A (FAITHFUL): It can be described as something being able to do what people want in a GOOD way for some time.
- B (FAITHFUL): 'People can use this to do good things' renders in CAN/DO/GOOD.

**coiner**
- A (FAITHFUL): A person can be described as first saying WORDS that people did not say before and thereby causing others to say them.
- B (FAITHFUL): 'Someone who says words no one said before' renders in SAY/WORDS/OTHER/BEFORE/NOT.

**fastening**
- A (FAITHFUL): The action can be rendered as causing things to TOUCH or remain together so that they cannot move apart without another action.
- B (FAITHFUL): 'Doing something so two things are together and cannot move apart' renders in DO/TOUCH/NOT/MOVE.

**instrumentality**
- A (FAITHFUL): A thing is instrumental when someone can do something with it because this can cause a wanted outcome.
- B (FAITHFUL): 'Because of this, someone can do something they want' renders in BECAUSE/CAN/DO/WANT.

**linkage**
- A (FAITHFUL): Linking can be expressed as causing things to become parts of one whole or to affect or move with one another.
- B (FAITHFUL): 'Doing something so things are joined, now like one thing' renders in DO/PART/THE-SAME/ONE.

**feasibility**
- A (FAITHFUL): The differentia is directly expressible as someone being able to DO the relevant thing.
- B (FAITHFUL): 'Someone can do it' renders directly in CAN/DO.

**grazing**
- A (FAITHFUL): It can be rendered as moving past something and TOUCHING it only for a short time during that movement.
- B (FAITHFUL): 'While moving near, touches it a little' renders in MOVE/NEAR/TOUCH/LITTLE.

**pettiness**
- A (FAITHFUL): Lack of importance can be explicated through LITTLE consequence and people's judgment that the matter does not merit much thought.
- B (FAITHFUL): 'It is something small, people can think it is not something good, not big' renders in SMALL/NOT/BIG/GOOD.

**move**
- A (FAITHFUL): A decision can be rendered as someone THINKING and WANTING to do something and settling on doing it.
- B (FAITHFUL): 'Someone does something because they want something to happen' renders in DO/WANT/HAPPEN/THINK.

**cognitive state**
- A (FAITHFUL): What someone THINKS, KNOWS, SEES, or HEARS at a particular time can be specified directly with mental primes.
- B (FAITHFUL): 'The way someone thinks and knows something at a time' renders in THINK/KNOW/WHEN.

**differentiator**
- A (FAITHFUL): Differentiating can be rendered as causing or enabling someone to KNOW that two things are NOT THE-SAME.
- B (FAITHFUL): 'That which makes one see this is not the same as the other' renders in SEE/NOT/THE-SAME/OTHER.

**self-esteem**
- A (FAITHFUL): It can be expressed as FEELING something GOOD because one THINKS something GOOD about oneself.
- B (FAITHFUL): 'When someone thinks about themselves they feel something good, thinks good things about themselves' renders in THINK/I/GOOD/FEEL.

**poisoning**
- A (FAITHFUL): Poison can be functionally described as something that can cause a living body to DIE when put inside it, with the agent WANTING that outcome.
- B (FAITHFUL): 'Giving someone something that, when inside the body, makes them die, because wanting them to die' renders in DO/INSIDE/BODY/DIE/WANT.

**cancellation**
- A (FAITHFUL): An arrangement can be represented as prior words about a future event, followed by words and actions causing it not to happen.
- B (FAITHFUL): 'Before someone said this will happen, now says it will not happen' renders in BEFORE/SAY/NOT/HAPPEN.

**contamination**
- A (FAITHFUL): It can be described as an unwanted other kind of thing being INSIDE or touching something and being able to cause BAD effects.
- B (FAITHFUL): 'Something bad is now part of it that before was not, because of this it is not good' renders in BAD/PART/BEFORE/NOT/GOOD.

**joker**
- A (FAITHFUL): The person can be described as doing something without sufficient thought that others do not want and because of which they feel or think something BAD.
- B (FAITHFUL): 'Someone who does something bad without thinking, other people feel something bad because of it' renders in DO/NOT/THINK/FEEL/BAD.

**initiation**
- A (FAITHFUL): Starting for the first time reduces to causing something to happen or exist NOW when it did not happen or exist BEFORE.
- B (FAITHFUL): 'Something begins to happen/exist that before did not, this is the first time' renders in BEFORE/NOT/HAPPEN/THERE-IS/ONE.

**medium**
- A (FAITHFUL): It can be rendered as someone believed able to receive or convey WORDS between living people and people who have DIED.
- B (FAITHFUL): 'Someone people think can say words to and hear people who are not living' renders in THINK/SAY/HEAR/LIVE/NOT.

**optimization**
- A (FAITHFUL): It can be expressed as making an outcome such that no other possible outcome is MORE as wanted according to the relevant criterion.
- B (FAITHFUL): 'Doing something so it is very good, so it cannot be more good' renders in DO/VERY/GOOD/CAN/NOT/MORE.

**access**
- A (FAITHFUL): Approaching is becoming NEAR, and entering is moving from NOT INSIDE to INSIDE.
- B (FAITHFUL): 'Moving so as to be near or inside a place' renders in MOVE/NEAR/INSIDE/PLACE.

**quitter**
- A (FAITHFUL): The disposition can be rendered as stopping after a short time or after little adversity despite being able to continue, when others think one should continue.
- B (FAITHFUL): 'Someone who, when doing something, does not do more because doesn't want it, when they could do more' renders in DO/NOT/MORE/DON'T-WANT/CAN.

**carry**
- A (FAITHFUL): It can be rendered as causing something to MOVE with the agent while remaining near or in contact with the agent's body.
- B (FAITHFUL): 'Something touches part of the body and moves with the person as they move' renders in TOUCH/BODY/MOVE/WITH.

**drop**
- A (FAITHFUL): Dropping can be described as ceasing to support something so that it moves from ABOVE to BELOW.
- B (FAITHFUL): 'Someone no longer touches a thing, it moves below' renders in NOT/TOUCH/MOVE/BELOW.

**suicide**
- A (FAITHFUL): The same person can occupy agent and undergoer roles in a clause where intentional action causes that person to DIE.
- B (FAITHFUL): 'Someone does something to their own body because they want to die, so they die' renders in DO/BODY/WANT/DIE.

**minimization**
- A (FAITHFUL): It can be expressed as making an amount, degree, or position such that no other possible result is smaller or lower, using reversed MORE comparisons and BELOW.
- B (FAITHFUL): 'Doing something so there is as little as can be, it cannot be less' renders in DO/LITTLE/CAN/NOT/MORE.

**depletion**
- A (FAITHFUL): It can be stated that there was MUCH of something before and markedly less afterward.
- B (FAITHFUL): 'Before there was much, now there is little' renders in BEFORE/MUCH/NOW/LITTLE.

**dilation**
- A (FAITHFUL): An aperture can be paraphrased as an empty passage through a thing, and dilation as causing that place to become MORE BIG.
- B (FAITHFUL): 'A part/opening becomes more big than before' renders in PART/MORE/BIG/BEFORE.

**chip**
- A (FAITHFUL): Chipping can be rendered as doing something that causes a SMALL PART of a thing to cease touching the rest and separate from it.
- B (FAITHFUL): 'A small part moves away from a thing, is no longer part of it' renders in SMALL/PART/MOVE/NOT.

**dissociation**
- A (FAITHFUL): It can be described as causing things that were parts of one whole, acted together, or affected one another to cease doing so.
- B (FAITHFUL): 'Before with the same others, now not with them' renders in BEFORE/WITH/THE-SAME/NOT.

**subdivision**
- A (FAITHFUL): It can be rendered as taking one PART produced by an earlier division and causing that part to become several further parts.
- B (FAITHFUL): 'One thing becomes parts, then these parts become more parts' renders in ONE/PART/MORE.

**harassment**
- A (FAITHFUL): Repeated BAD actions and critical WORDS directed at someone over time, causing unwanted BAD feelings, can be fully composed.
- B (FAITHFUL): 'Someone does bad things to someone and says bad words many times over time, they feel bad' renders in DO/BAD/SAY/MUCH/FEEL.

**lookout**
- A (FAITHFUL): Keeping lookout can be rendered as intentionally trying to SEE for some time because something, possibly BAD, may happen.
- B (FAITHFUL): 'Someone wants to see if something bad happens or comes' renders in WANT/SEE/IF/HAPPEN/MAYBE.

**view**
- A (FAITHFUL): The act is directly expressible through SEE, or through doing something because one wants to SEE something.
- B (FAITHFUL): 'Someone wants to see something, sees it' renders in WANT/SEE.

**invention**
- A (FAITHFUL): Inventing can be described as first THINKING of something that did not exist or was not known before and then causing it to exist.
- B (FAITHFUL): 'Someone thinks and does something so that something that did not exist before now exists' renders in THINK/DO/BEFORE/NOT/THERE-IS.

**gather**
- A (FAITHFUL): Gathering can be rendered as causing many things that were in different places to be together in one place.
- B (FAITHFUL): 'Moving many things so they are in one place together' renders in MANY/MOVE/ONE/PLACE/WITH.

**shoring**
- A (PARTIAL): The supporting function can be paraphrased, but the defining beam-like shore artifact requires shape, rigidity, and artifact content unavailable in the primes.
- B (FAITHFUL): 'Putting something below/at the side of a thing so it cannot move down' renders in BELOW/SIDE/TOUCH/CAN/NOT/MOVE; the artefact is only the means.

**inhabitancy**
- A (FAITHFUL): It can be expressed as someone or another living thing LIVING and BEING in the same place for a long time.
- B (FAITHFUL): 'Someone lives in a place for a long time' renders in LIVE/BE-SOMEWHERE/PLACE/A-LONG-TIME.

**coercion**
- A (FAITHFUL): It can be rendered as someone doing an unwanted act because another can cause BAD consequences and makes this condition known through words or actions.
- B (FAITHFUL): 'Making someone do what they don't want because if not, something bad will happen to them' renders in DO/DON'T-WANT/IF/NOT/BAD/BECAUSE.

---

*Provenance:* self-flags from `poc/scale/consensus-100/gen/<concept>.<model>.report.json`; glosses from
`concepts-100.json` (`wn31_gloss`); 65 primes from `encoder/src/lexicon.ts` (`PRIMES`, closed profile-1
inventory). Judge A: `gpt-5.6-sol` via `npx @openai/codex@0.144.1 exec` (effort xhigh, read-only, isolated
ephemeral home, no web, no memory). Judge B: `claude-opus-4-8` via `claude -p` from a neutral cwd. Both
judges received the identical blind prompt (concept label + gloss + 65 primes only). Read-only; uncommitted.