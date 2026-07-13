# Human faithfulness spot-check — is Claude's 'faithful' genuine or lenient?

For each concept the **Claude** model called its kot-ast/1 explication **FAITHFUL** (profile-1's 65 primes fully render the differentia); the **GPT** model called its own **LOSSY** (primes drop meaning). Same 65 primes for both. **Your call: is the concept genuinely renderable in the primes (Claude right) or inherently lossy (GPT right)?**

Mark each **FAITHFUL-genuine / LOSSY-GPT-right / PARTIAL**. Mostly FAITHFUL-genuine → a Claude generator's ~3× faithful yield is real (faithful-heavy arm ~200 gens not ~700). Mostly LOSSY → Claude was lenient (real faithful rate ≈ GPT's ~10%).

The 65 profile-1 primes = the fixed NSM-style primitive inventory the AST must be built from (SOMEONE, SOMETHING, DO, HAPPEN, BE, KIND, PART, GOOD, BAD, BIG, SMALL, BEFORE, AFTER, BECAUSE, CAN, WANT, THINK, KNOW, SAY, MOVE, TOUCH, PLACE, TIME, …).
---

## apparition  (urn:lexical-wn31:n-00051304)  [ACT]
**WordNet gloss:** an act of appearing or becoming visible unexpectedly; "natives were amazed at the apparition of this white stranger"

**Opus (Claude) — FAITHFUL:**  gloss: *The event of someone or something coming suddenly and unexpectedly into view, so that people who could not see it before now see it, in a way they had not thought would happen.*
  - AST: `{"schema": "kot-ast/1", "frame": "InstanceSchema", "referents": [{"index": 1, "refKind": "SomethingRef"}, {"index": 2, "refKind": "SomethingRef"}, {"index": 3, "refKind": "TimeRef"}, {"index": 4, "refKind": "SomeoneRef"}], "clauses": [{"type": "pred", "pred": "HAPPEN", "roles": {"undergoer": {"kind": "sp", "head": {"kind": "primeHead", "prime": "SOMETHING~THING"}, "bind": 1}, "time": {"kind": "sp", "det": "SOME", "he`
  - note: AST adequacy: faithful — the thing cannot be seen before the time and is seen after, and the beholders had not thought they would see it, rendering both the coming-into-view and the unexpectedness.

**Luna (GPT) — LOSSY:**  gloss: *The event in which someone or something unexpectedly comes into view, becoming perceptible to people who had not previously seen it.*
  - AST: `{"schema": "kot-ast/1", "frame": "InstanceSchema", "referents": [{"index": 1, "refKind": "SomethingRef"}, {"index": 2, "refKind": "SomethingRef"}, {"index": 3, "refKind": "TimeRef"}], "clauses": [{"type": "pred", "pred": "HAPPEN", "roles": {"undergoer": {"kind": "ref", "index": 1}, "time": {"kind": "sp", "det": "SOME", "head": {"kind": "primeHead", "prime": "WHEN~TIME"}, "bind": 3}}}, {"type": "op", "op": "BEFORE", "`
  - note: AST adequacy: lossy — the explication renders a thing coming into view across a time boundary but cannot express that this was unexpected or unanticipated.

**YOUR VERDICT:** ____ (FAITHFUL-genuine / LOSSY-GPT-right / PARTIAL)

---

## pull  (urn:lexical-wn31:n-00115251)  [ACT]
**WordNet gloss:** the act of pulling; applying force to move something toward or with you; "the pull up the hill had him breathing harder"; "his strenuous pulling strained his back"

**Opus (Claude) — FAITHFUL:**  gloss: *The act of applying force to something so as to draw it toward oneself, causing it to move nearer or to move along with one.*
  - AST: `{"schema": "kot-ast/1", "frame": "InstanceSchema", "referents": [{"index": 1, "refKind": "SomeoneRef"}, {"index": 2, "refKind": "SomethingRef"}], "clauses": [{"type": "pred", "pred": "DO", "roles": {"agent": {"kind": "ref", "index": 1}, "undergoer": {"kind": "sp", "head": {"kind": "primeHead", "prime": "SOMETHING~THING"}, "bind": 2}}}, {"type": "op", "op": "BECAUSE", "args": [{"type": "pred", "pred": "DO", "roles": {`
  - note: AST adequacy: faithful — acts on a thing so that it moves nearer and comes to be near the agent — a sound primitive reading of drawing toward oneself, though the applied 'force' is rendered only as ag

**Sol (GPT) — LOSSY:**  gloss: *An act of applying force to something so that it moves toward the agent or accompanies the agent's movement.*
  - AST: `{"schema": "kot-ast/1", "frame": "InstanceSchema", "referents": [{"index": 1, "refKind": "SomeoneRef"}, {"index": 2, "refKind": "SomethingRef"}], "clauses": [{"type": "pred", "pred": "DO", "roles": {"agent": {"kind": "ref", "index": 1}, "undergoer": {"kind": "sp", "head": {"kind": "primeHead", "prime": "SOMETHING~THING"}, "bind": 2}}}, {"type": "op", "op": "BECAUSE", "args": [{"type": "pred", "pred": "DO", "roles": {`
  - note: AST adequacy: lossy — the primes encode an agent acting on a thing so that it moves near the agent, but cannot distinguish applied force or the alternative of accompanying movement.

**YOUR VERDICT:** ____ (FAITHFUL-genuine / LOSSY-GPT-right / PARTIAL)

---

## fastening  (urn:lexical-wn31:n-00148415)  [ACT]
**WordNet gloss:** the act of fastening things together

**Opus (Claude) — FAITHFUL:**  gloss: *The act of joining two things so that they come to be firmly held together and remain so, no longer able to move apart.*
  - AST: `{"schema": "kot-ast/1", "frame": "InstanceSchema", "referents": [{"index": 1, "refKind": "SomeoneRef"}, {"index": 2, "refKind": "SomethingRef"}, {"index": 3, "refKind": "SomethingRef"}], "clauses": [{"type": "op", "op": "BECAUSE", "args": [{"type": "pred", "pred": "DO", "roles": {"agent": {"kind": "ref", "index": 1}, "undergoer": {"kind": "sp", "head": {"kind": "primeHead", "prime": "SOMETHING~THING"}, "bind": 2}}}, `
  - note: AST adequacy: faithful — someone acts so that one thing touches another and afterward cannot move away — a sound primitive reading of fastening things together.

**Sol (GPT) — LOSSY:**  gloss: *An act of joining two or more things and securing them to one another so that they remain connected.*
  - AST: `{"schema": "kot-ast/1", "frame": "InstanceSchema", "referents": [{"index": 1, "refKind": "SomethingRef"}, {"index": 2, "refKind": "SomethingRef"}, {"index": 3, "refKind": "SomethingRef"}, {"index": 4, "refKind": "TimeRef"}], "clauses": [{"type": "pred", "pred": "THERE-IS", "roles": {"undergoer": {"kind": "sp", "head": {"kind": "primeHead", "prime": "SOMETHING~THING"}, "bind": 2}}}, {"type": "pred", "pred": "THERE-IS"`
  - note: AST adequacy: lossy — the primes express resulting contact and inability to be far apart but cannot encode the criterial mechanical or material securing that makes the connection persist.

**YOUR VERDICT:** ____ (FAITHFUL-genuine / LOSSY-GPT-right / PARTIAL)

---

## grazing  (urn:lexical-wn31:n-00151582)  [ACT]
**WordNet gloss:** the act of brushing against while passing

**Opus (Claude) — FAITHFUL:**  gloss: *The act of lightly touching something in passing, so that a moving body comes for a moment into slight contact with it and then continues on without stopping.*
  - AST: `{"schema": "kot-ast/1", "frame": "InstanceSchema", "referents": [{"index": 1, "refKind": "SomethingRef"}, {"index": 2, "refKind": "SomethingRef"}], "clauses": [{"type": "pred", "pred": "MOVE", "roles": {"undergoer": {"kind": "ref", "index": 1}, "place": {"kind": "sp", "det": "OTHER~ELSE~ANOTHER", "head": {"kind": "primeHead", "prime": "SOMETHING~THING"}, "bind": 2, "restrictedBy": {"type": "pred", "pred": "BE-SOMEWHE`
  - note: AST adequacy: faithful — a thing moves past another, touches it for a moment, and moves on away — a sound reading of brushing against in passing, though 'lightly' is rendered only as brief momentary c

**Sol (GPT) — LOSSY:**  gloss: *An act of making light, momentary contact with someone or something while moving past it, without a direct collision or interruption of motion.*
  - AST: `{"schema": "kot-ast/1", "frame": "InstanceSchema", "referents": [{"index": 1, "refKind": "SomethingRef"}, {"index": 2, "refKind": "SomethingRef"}, {"index": 3, "refKind": "TimeRef"}], "clauses": [{"type": "pred", "pred": "MOVE", "roles": {"undergoer": {"kind": "ref", "index": 1}, "time": {"kind": "sp", "det": "SOME", "head": {"kind": "primeHead", "prime": "WHEN~TIME"}, "bind": 3}}}, {"type": "pred", "pred": "BE-SOMEW`
  - note: AST adequacy: lossy — the AST renders movement and momentary contact at the same time but cannot specify the lightness of contact or the passing trajectory.

**YOUR VERDICT:** ____ (FAITHFUL-genuine / LOSSY-GPT-right / PARTIAL)

---

## joker  (urn:lexical-wn31:n-10243965)  [AGENTIVE]
**WordNet gloss:** a person who does something thoughtless or annoying; "some joker is blocking the driveway"

**Opus (Claude) — FAITHFUL:**  gloss: *A person who does something without thinking about its effect on others, in a way that causes other people to feel annoyed or badly affected.*
  - AST: `{"schema": "kot-ast/1", "frame": "InstanceSchema", "referents": [{"index": 1, "refKind": "SomeoneRef"}, {"index": 2, "refKind": "SomethingRef"}, {"index": 3, "refKind": "SomeoneRef"}], "clauses": [{"type": "pred", "pred": "DO", "roles": {"agent": {"kind": "ref", "index": 1}, "undergoer": {"kind": "sp", "head": {"kind": "primeHead", "prime": "SOMETHING~THING"}, "bind": 2}}}, {"type": "op", "op": "NOT", "args": [{"type`
  - note: AST adequacy: faithful — does something without thinking about it, so that other people feel bad — a sound reading of a thoughtless, annoying person.

**Sol (GPT) — LOSSY:**  gloss: *A person who, without due consideration for others, does something foolish, troublesome, or irritating to them.*
  - AST: `{"schema": "kot-ast/1", "frame": "InstanceSchema", "referents": [{"index": 1, "refKind": "SomeoneRef"}, {"index": 2, "refKind": "SomeoneRef"}, {"index": 3, "refKind": "SomethingRef"}], "clauses": [{"type": "pred", "pred": "THERE-IS", "roles": {"undergoer": {"kind": "sp", "det": "OTHER~ELSE~ANOTHER", "head": {"kind": "primeHead", "prime": "SOMEONE"}, "bind": 2}}}, {"type": "op", "op": "NOT", "args": [{"type": "pred", `
  - note: AST adequacy: lossy — The AST renders disregard as not thinking about another person and annoyance as that person's bad feeling, but cannot encode foolishness or practical inconvenience.

**YOUR VERDICT:** ____ (FAITHFUL-genuine / LOSSY-GPT-right / PARTIAL)

---

## quitter  (urn:lexical-wn31:n-10521631)  [AGENTIVE]
**WordNet gloss:** a person who gives up too easily

**Fable (Claude) — FAITHFUL:**  gloss: *A person disposed to abandon an undertaking at the first sign of difficulty, ceasing to pursue what was begun rather than persevering through even minor hardship.*
  - AST: `{"schema": "kot-ast/1", "frame": "InstanceSchema", "referents": [{"index": 1, "refKind": "SomeoneRef"}, {"index": 2, "refKind": "SomethingRef"}, {"index": 3, "refKind": "TimeRef"}], "clauses": [{"type": "pred", "pred": "DO", "roles": {"agent": {"kind": "ref", "index": 1}, "undergoer": {"kind": "sp", "head": {"kind": "primeHead", "prime": "SOMETHING~THING"}, "bind": 2}, "time": {"kind": "sp", "det": "SOME", "head": {"`
  - note: AST adequacy: faithful — when only a small bad thing happens during the doing, the person no longer wants to do it and afterward does not do it; the SMALL+BAD trigger carries the 'too easily' differen

**Sol (GPT) — LOSSY:**  gloss: *A person habitually disposed to abandon an undertaking prematurely, especially upon encountering difficulty or discouragement, rather than persist until it is completed.*
  - AST: `{"schema": "kot-ast/1", "frame": "InstanceSchema", "referents": [{"index": 1, "refKind": "SomeoneRef"}, {"index": 2, "refKind": "SomethingRef"}], "clauses": [{"type": "pred", "pred": "DO", "roles": {"agent": {"kind": "ref", "index": 1}, "undergoer": {"kind": "sp", "head": {"kind": "primeHead", "prime": "SOMETHING~THING"}, "bind": 2}, "duration": {"kind": "prime", "prime": "A-SHORT-TIME"}}}, {"type": "op", "op": "CAN"`
  - note: AST adequacy: lossy — the AST renders someone who acts only briefly and ceases despite retained ability because of feeling bad, but cannot represent habitual disposition, premature abandonment, diffic

**YOUR VERDICT:** ____ (FAITHFUL-genuine / LOSSY-GPT-right / PARTIAL)

---

## feasibility  (urn:lexical-wn31:n-05159611)  [STATE]
**WordNet gloss:** the quality of being doable

**Opus (Claude) — FAITHFUL:**  gloss: *The quality of being capable of being done or accomplished; the state of a course of action such that someone is able to carry it through to completion.*
  - AST: `{"schema": "kot-ast/1", "frame": "WhenTrue", "referents": [{"index": 1, "refKind": "SomethingRef"}, {"index": 2, "refKind": "SomeoneRef"}], "clauses": [{"type": "op", "op": "CAN", "args": [{"type": "pred", "pred": "DO", "roles": {"agent": {"kind": "sp", "head": {"kind": "primeHead", "prime": "SOMEONE"}, "bind": 2}, "undergoer": {"kind": "ref", "index": 1}}}]}]}`
  - note: AST adequacy: faithful — the quality holds of something when someone can do it, which is a clean primitive reading of being doable.

**Sol (GPT) — LOSSY:**  gloss: *The quality of a proposed course or result whereby it can be carried out or brought about under the relevant circumstances.*
  - AST: `{"schema": "kot-ast/1", "frame": "WhenTrue", "referents": [{"index": 1, "refKind": "SomethingRef"}], "clauses": [{"type": "op", "op": "CAN", "args": [{"type": "pred", "pred": "DO", "roles": {"agent": {"kind": "sp", "head": {"kind": "primeHead", "prime": "SOMEONE"}}, "undergoer": {"kind": "ref", "index": 1}}}]}]}`
  - note: AST adequacy: lossy — it renders only that someone can do the relevant thing, without representing the proposed-course or result distinction or the constraint of relevant circumstances.

**YOUR VERDICT:** ____ (FAITHFUL-genuine / LOSSY-GPT-right / PARTIAL)

---

## self-esteem  (urn:lexical-wn31:n-07523944)  [STATE]
**WordNet gloss:** a feeling of pride in yourself

**Opus (Claude) — FAITHFUL:**  gloss: *A settled sense of one's own worth: the state in which a person thinks well of themselves and, on that account, feels good about the kind of person they are.*
  - AST: `{"schema": "kot-ast/1", "frame": "WhenTrue", "referents": [{"index": 1, "refKind": "SomeoneRef"}], "clauses": [{"type": "pred", "pred": "THINK", "roles": {"experiencer": {"kind": "ref", "index": 1}, "topic": {"kind": "ref", "index": 1}}}, {"type": "op", "op": "BECAUSE", "args": [{"type": "pred", "pred": "THINK", "roles": {"experiencer": {"kind": "ref", "index": 1}, "quote": {"kind": "quote", "clauses": [{"type": "pre`
  - note: AST adequacy: faithful — the bearer thinks of themselves as a good kind of person and, because of this, feels good — a clean reading of pride in oneself.

**Sol (GPT) — LOSSY:**  gloss: *A favourable sense of one's own worth, arising from the judgment that one's character or abilities merit respect.*
  - AST: `{"schema": "kot-ast/1", "frame": "WhenTrue", "referents": [{"index": 1, "refKind": "SomeoneRef"}], "clauses": [{"type": "op", "op": "BECAUSE", "args": [{"type": "pred", "pred": "THINK", "roles": {"experiencer": {"kind": "ref", "index": 1}, "quote": {"kind": "quote", "clauses": [{"type": "pred", "pred": "BE-SPEC", "roles": {"undergoer": {"kind": "prime", "prime": "I"}, "attribute": {"kind": "sp", "mods": [{"mod": "GOO`
  - note: AST adequacy: lossy — the primes preserve a good feeling caused by a positive judgment about one's own value, but cannot distinguish worth and deserved respect from undifferentiated goodness.

**YOUR VERDICT:** ____ (FAITHFUL-genuine / LOSSY-GPT-right / PARTIAL)

---
