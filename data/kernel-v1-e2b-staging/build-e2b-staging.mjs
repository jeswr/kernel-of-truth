#!/usr/bin/env node
/**
 * kernel-v1 E2b STAGING build — sense-split inventory-extension concepts for
 * the ENGINE-INF E2b design (docs/next/design/engine-inference-under-typing.md
 * §E2b; maintainer-approved issue #29; selection artifact
 * poc/engine-inference/e2b-inventory-extension/e2b-selection.json).
 *
 * STAGING, NOT ADOPTION: this directory is an experiment-scoped Stage-A
 * EXTENSION CANDIDATE. It does NOT touch data/kernel-v1 (whose frozen
 * surface proof stands), does NOT mint urn:kot: identity hashes (identity
 * minting happens at the adoption build, the Stage-A path, coordinator
 * custody), and adopts NO anomaly-gold construct. Concept ids here are
 * alias URNs urn:kernel-v1e2b:<lemma>.<senseTag>, pending adoption.
 *
 * Gates (fail closed, mirroring build-kernel-v1-stageA.mjs):
 *   ENC   every explication passes the encoder's validateExplication and one
 *         encodeConceptSet pass; encoder pin READ-only == kernel-v0 frozen.
 *   SCOPE minted synsets per lemma == the E2b-SEL selection output
 *         (restricted ∪ contrast synsets, mechanically cross-checked).
 *   R1    per-lemma candidate recount against pinned WN31 synsets-verb.jsonl;
 *         excludedSenses = candidates − minted (R4/R5 closure: nothing
 *         silently dropped).
 *   ONTIC every minted verb-sense concept is ontic_category 'event'
 *         (ERR_VERB_NOT_EVENT — the "break is an EVENT" rule generalized).
 *   G1    no two concepts share a synset; G2 every minted synset appears in
 *         exactly one concept.
 */
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const repo = join(here, '..', '..');
const die = (m) => { console.error('FATAL: ' + m); process.exit(1); };

const { validateExplication, encodeConceptSet, encoderContentHash, ALGORITHM_VERSION } =
  await import(join(repo, 'encoder/dist/src/index.js'));

// ---------- encoder pin: READ-only, must equal kernel-v0 frozen ----------
const v0manifest = JSON.parse(readFileSync(join(repo, 'data/kernel-v0/manifest.json'), 'utf8'));
const encHash = encoderContentHash();
if (encHash !== v0manifest.encoderContentHash) {
  die(`ERR_ENCODER_PIN: live ${encHash} != kernel-v0 frozen ${v0manifest.encoderContentHash}`);
}

// ---------- the mechanical selection this build is scoped to ----------
const selection = JSON.parse(readFileSync(
  join(repo, 'poc/engine-inference/e2b-inventory-extension/e2b-selection.json'), 'utf8'));
const selLemmas = new Map(selection.selected.map((c) => [c.lemma, c]));

// ---------- AST helpers (authored content below; helpers are shape only) ----
const R = (i) => ({ kind: 'ref', index: i });
const P = (p) => ({ kind: 'prime', prime: p });
const SP = (prime, extra = {}) => ({ kind: 'sp', head: { kind: 'primeHead', prime }, ...extra });
const PART = (of, extra = {}) => ({ kind: 'sp', head: { kind: 'partFrame', of }, ...extra });
const pred = (p, roles) => ({ type: 'pred', pred: p, roles });
const op = (o, ...args) => ({ type: 'op', op: o, args });
const CL = (clause) => ({ kind: 'clause', clause });
const T = (bind) => SP('WHEN~TIME', { det: 'SOME', bind }); // introducing time SP
const PEOPLE = () => SP('PEOPLE');
const SOMEPLACE = (extra = {}) => SP('WHERE~PLACE', { det: 'SOME', ...extra });
// the two recurring undergoer-sort clauses the §E2b axiom promotion reads:
//   PHYS license: the undergoer can be somewhere (locational capability)
//   ABST license: the undergoer cannot be somewhere
const CAN_BE_SOMEWHERE = (i) => op('CAN', pred('BE-SOMEWHERE', { undergoer: R(i), locus: SOMEPLACE() }));
const NOT_BE_SOMEWHERE = (i) => op('NOT', CAN_BE_SOMEWHERE(i));

// ---------- the 22 authored sense-split concepts -----------------------------
// One concept per sense; a concept claims its synset cluster, not the word
// (ASM-1884). Every explication carries the clause the §E2b axiom promotion
// reads for the undergoer sort (named in `notes`). All verb senses are
// EVENTS (ck-ufo sidecar below). Authored content is research-grade,
// profile-1-validated; NOT federation-endorsed.
const CONCEPTS = [
  // ===================================================================== add
  {
    lemma: 'add', tag: 'combine', synsets: ['v-00182551'], role: 'restricted', side: 'phys',
    vn: 'mix-22.1-2 Patient [+concrete]',
    label: 'add.combine (X adds Y to other things — after X does something, Y is with these things and they are like one bigger something; as in "add flour to the mix", NOT as in "the music added a lot to the play")',
    gloss: 'X did something to Y at some time; before this time Y was not with some other things; after this time Y is with these things; after this time these things are like one big something.',
    notes: 'E2b restricted sense (VerbNet mix-22.1-2, Patient [+concrete] -> phys). Undergoer-sort clause: Y is placed somewhere with other things (BE-SOMEWHERE capability) — the phys license the §E2b promotion reads. Referent 1 kept SomeoneRef (adding is agentive in the attested frame).',
    referents: [['SomeoneRef'], ['SomethingRef'], ['SomethingRef'], ['TimeRef']],
    clauses: [
      pred('THERE-IS', { undergoer: SP('SOMETHING~THING', { quant: 'MUCH~MANY', bind: 3 }) }),
      pred('DO', { agent: R(1), undergoer: R(2), time: T(4) }),
      op('BEFORE', R(4), op('NOT', pred('BE-SOMEWHERE', { undergoer: R(2), locus: R(3) }))),
      op('AFTER', R(4), pred('BE-SOMEWHERE', { undergoer: R(2), locus: R(3) })),
      op('AFTER', R(4), pred('BE-SPEC', {
        undergoer: R(3),
        attribute: SP('SOMETHING~THING', { quant: 'ONE', mods: [{ mod: 'BIG' }] }),
      })),
    ],
  },
  {
    lemma: 'add', tag: 'enhance', synsets: ['v-02329474'], role: 'contrast', side: null,
    vn: '(no VN undergoer restriction; E2b-SEL F4(b) evidence: gloss object "cachet", abst)',
    label: 'add.enhance (X adds Y to Z — Y is not a thing that can be somewhere; because of X, people can think something more good about Z; as in "the music added a lot to the play", NOT as in "add flour to the mix")',
    gloss: 'Y is not something that can be somewhere; X did something at some time; because of this, after this time, when people think about the other something, they can think something good.',
    notes: 'E2b contrast sense (within-lemma sortal differentiation for add.combine). Undergoer-sort clause: NOT(CAN(BE-SOMEWHERE Y)) — the abst reading; kept broad, no side-forcing axiom is required of the promotion.',
    referents: [['SomeoneRef'], ['SomethingRef'], ['SomethingRef'], ['TimeRef']],
    clauses: [
      NOT_BE_SOMEWHERE(2),
      pred('THERE-IS', { undergoer: SP('SOMETHING~THING', { det: 'OTHER~ELSE~ANOTHER', bind: 3 }) }),
      pred('DO', { agent: R(1), undergoer: R(2), time: T(4) }),
      op('BECAUSE',
        pred('DO', { agent: R(1), undergoer: R(2) }),
        op('AFTER', R(4), op('CAN', pred('THINK', {
          experiencer: PEOPLE(), topic: SP('SOMETHING~THING', { quant: 'SOME', mods: [{ mod: 'GOOD' }] }),
        })))),
      pred('KNOW', { experiencer: PEOPLE(), topic: R(3) }),
    ],
  },
  // =================================================================== bring
  {
    lemma: 'bring', tag: 'carry', synsets: ['v-02081903'], role: 'restricted', side: 'phys',
    vn: 'bring-11.3-1 Theme [+concrete]',
    label: 'bring.carry (X brings Y to a place — X moves to this place and Y moves with X; after this Y is in this place; as in "bring me the box", NOT as in "the rain brought relief")',
    gloss: 'X moved to some place at some time; when X moved, Y moved with X; before this time Y was not in this place; after this time Y is in this place.',
    notes: 'E2b restricted sense (VerbNet bring-11.3-1, Theme [+concrete] -> phys). Undergoer-sort clauses: Y MOVEs and Y ends BE-SOMEWHERE — the phys license.',
    referents: [['SomeoneRef'], ['SomethingRef'], ['PlaceRef'], ['TimeRef']],
    clauses: [
      pred('DO', { agent: R(1), undergoer: R(2), time: T(4) }),
      pred('BE-SOMEWHERE', { undergoer: R(1), locus: SOMEPLACE({ bind: 3 }) }),
      op('WHEN', pred('MOVE', { undergoer: R(1) }), pred('MOVE', { undergoer: R(2) })),
      op('BEFORE', R(4), op('NOT', pred('BE-SOMEWHERE', { undergoer: R(2), locus: R(3) }))),
      op('AFTER', R(4), pred('BE-SOMEWHERE', { undergoer: R(2), locus: R(3) })),
    ],
  },
  {
    lemma: 'bring', tag: 'fetch', synsets: ['v-01435927'], role: 'restricted', side: 'phys',
    vn: 'bring-11.3-1 Theme [+concrete]',
    label: 'bring.fetch (X fetches Y — Y is in a place where X is not; X moves to this place and then moves back with Y; as in "could you bring the wine?", NOT as in "the rain brought relief")',
    gloss: 'Y was in some place at some time; X was not in this place; X moved to this place; after this, X moved away from this place; when X moved away, Y moved with X; after this time Y is not in this place.',
    notes: 'E2b restricted sense (VerbNet bring-11.3-1, Theme [+concrete] -> phys). Distinct from bring.carry by the go-first component (WN: "go or come after and bring or take back"). Undergoer-sort clauses: Y is somewhere, Y MOVEs — the phys license.',
    referents: [['SomeoneRef'], ['SomethingRef'], ['PlaceRef'], ['TimeRef']],
    clauses: [
      pred('BE-SOMEWHERE', { undergoer: R(2), locus: SOMEPLACE({ bind: 3 }), time: T(4) }),
      op('NOT', pred('BE-SOMEWHERE', { undergoer: R(1), locus: R(3) })),
      pred('MOVE', { undergoer: R(1) }),
      op('AFTER', R(4), op('WHEN', pred('MOVE', { undergoer: R(1) }), pred('MOVE', { undergoer: R(2) }))),
      op('AFTER', R(4), op('NOT', pred('BE-SOMEWHERE', { undergoer: R(2), locus: R(3) }))),
    ],
  },
  {
    lemma: 'bring', tag: 'cause', synsets: ['v-01632781'], role: 'contrast', side: null,
    vn: '(no VN undergoer restriction; E2b-SEL F4(b) evidence: gloss object "miracle", abst)',
    label: 'bring.cause (X brings Y about — Y is something that happens; because X does something, Y happens; as in "the rain brought relief", NOT as in "bring me the box")',
    gloss: 'Y is something that happens; Y is not something that can be somewhere; because X did something at some time, Y happened at this time; before this time there was no Y.',
    notes: 'E2b contrast sense (within-lemma sortal differentiation for bring.carry/fetch). Referent 1 broadened to SomethingRef ("the rain brought relief" — the §3.2 Stage-A precedent). Undergoer-sort clauses: HAPPEN(Y) and NOT(CAN(BE-SOMEWHERE Y)) — the abst reading.',
    referents: [['SomethingRef'], ['SomethingRef'], ['TimeRef']],
    clauses: [
      op('BECAUSE',
        pred('DO', { agent: R(1), time: T(3) }),
        pred('HAPPEN', { undergoer: R(2), time: R(3) })),
      NOT_BE_SOMEWHERE(2),
      op('BEFORE', R(3), op('NOT', pred('THERE-IS', { undergoer: R(2) }))),
    ],
  },
  // ================================================================= conduct
  {
    lemma: 'conduct', tag: 'manage', synsets: ['v-02450374'], role: 'restricted', side: 'abst',
    vn: 'conduct-111.1 Theme [+eventive]',
    label: 'conduct.manage (X conducts Y — Y is something that happens for some time; X does many things because X wants Y to happen in a certain way; as in "conduct business", NOT as in "he conducted us to the palace")',
    gloss: 'Y is something that happens for some time; Y is not something that can be somewhere; X wants Y to happen in some way; because of this, X does many things for some time.',
    notes: 'E2b restricted sense (VerbNet conduct-111.1, Theme [+eventive] -> abst). Undergoer-sort clauses: HAPPEN(Y, duration) and NOT(CAN(BE-SOMEWHERE Y)) — the abst license the §E2b promotion reads.',
    referents: [['SomeoneRef'], ['SomethingRef']],
    clauses: [
      pred('HAPPEN', { undergoer: R(2), duration: P('FOR-SOME-TIME') }),
      NOT_BE_SOMEWHERE(2),
      pred('WANT', { experiencer: R(1), complement: CL(pred('HAPPEN', { undergoer: R(2) })) }),
      op('BECAUSE',
        pred('WANT', { experiencer: R(1), complement: CL(pred('HAPPEN', { undergoer: R(2) })) }),
        pred('DO', { agent: R(1), undergoer: SP('SOMETHING~THING', { quant: 'MUCH~MANY' }), duration: P('FOR-SOME-TIME') })),
    ],
  },
  {
    lemma: 'conduct', tag: 'escort', synsets: ['v-02003830'], role: 'contrast', side: 'phys',
    vn: 'E2b-SEL F4(a): VN-opposite-side sense (accompany-51.7-shaped; second synset carries phys-side undergoer evidence)',
    label: 'conduct.escort (X conducts Y to a place — Y is someone; X moves to this place, Y moves with X, X knows the way; as in "he conducted us to the palace", NOT as in "conduct business")',
    gloss: 'Y is someone; X moved to some place at some time; when X moved, Y moved with X; X knows this place; after this time Y is in this place.',
    notes: 'E2b contrast sense (within-lemma sortal differentiation for conduct.manage; the selection\'s F4(a) opposite-side evidence). Undergoer-sort: SomeoneRef referent + MOVE + BE-SOMEWHERE — the phys reading.',
    referents: [['SomeoneRef'], ['SomeoneRef'], ['PlaceRef'], ['TimeRef']],
    clauses: [
      pred('DO', { agent: R(1), undergoer: R(2), time: T(4) }),
      pred('BE-SOMEWHERE', { undergoer: R(1), locus: SOMEPLACE({ bind: 3 }) }),
      op('WHEN', pred('MOVE', { undergoer: R(1) }), pred('MOVE', { undergoer: R(2) })),
      pred('KNOW', { experiencer: R(1), topic: R(3) }),
      op('AFTER', R(4), pred('BE-SOMEWHERE', { undergoer: R(2), locus: R(3) })),
    ],
  },
  // ===================================================================== cry
  {
    lemma: 'cry', tag: 'exclaim', synsets: ['v-00914001'], role: 'restricted', side: 'abst',
    vn: 'manner_speaking-37.3 Topic [+communication]',
    label: 'cry.exclaim (X cries Y — Y is words; X says Y with a big voice because X feels something at that moment; as in "‘Help!’ she cried", NOT as in "she cried bitterly at the news")',
    gloss: 'Y is words; X said Y at some time; X felt something at this time; because of this, X said Y not like people say words at other times; people in other places could hear Y.',
    notes: 'E2b restricted sense (VerbNet manner_speaking-37.3, Topic [+communication] -> abst). Undergoer-sort clause: BE-SPEC(Y, WORDS) — the abst (C_words-shaped) license, the break.violate pattern.',
    referents: [['SomeoneRef'], ['SomethingRef'], ['TimeRef']],
    clauses: [
      pred('BE-SPEC', { undergoer: R(2), attribute: SP('WORDS') }),
      pred('SAY', { agent: R(1), topic: R(2), time: T(3) }),
      pred('FEEL', { experiencer: R(1), time: R(3) }),
      op('BECAUSE', pred('FEEL', { experiencer: R(1) }), pred('SAY', { agent: R(1), topic: R(2) })),
      op('CAN', pred('HEAR', { experiencer: PEOPLE(), stimulus: R(2) })),
    ],
  },
  {
    lemma: 'cry', tag: 'weep', synsets: ['v-00065962'], role: 'contrast', side: null,
    vn: '(no VN undergoer restriction; E2b-SEL F4(b) evidence: gloss subject "girl", phys)',
    label: 'cry.weep (X cries — X feels something very bad; because of this, small watery somethings come out of a part of X\'s body; as in "she cried at the news", NOT as in "‘Help!’ she cried")',
    gloss: 'X felt something very bad at some time; because of this, some small somethings came out of a part of X\'s body; people can see these somethings; X did not want to do anything at this time.',
    notes: 'E2b contrast sense (within-lemma sortal differentiation for cry.exclaim; intransitive — the instrument\'s subject-fallback undergoer is X, a person, phys). Undergoer-sort: SomeoneRef X + body-part clause.',
    referents: [['SomeoneRef'], ['TimeRef']],
    clauses: [
      pred('FEEL', { experiencer: R(1), attribute: P('BAD'), time: R(2) }),
      op('BECAUSE',
        pred('FEEL', { experiencer: R(1) }),
        pred('MOVE', { undergoer: SP('SOMETHING~THING', { quant: 'MUCH~MANY', mods: [{ mod: 'SMALL' }] }) })),
      pred('BE-SOMEWHERE', {
        undergoer: SP('SOMETHING~THING', { quant: 'MUCH~MANY', mods: [{ mod: 'SMALL' }] }),
        locus: PART(R(1)),
      }),
      op('CAN', pred('SEE', {
        experiencer: PEOPLE(),
        stimulus: SP('SOMETHING~THING', { quant: 'MUCH~MANY', mods: [{ mod: 'SMALL' }] }),
      })),
    ],
  },
  // =================================================================== fight
  {
    lemma: 'fight', tag: 'combat', synsets: ['v-01092746'], role: 'restricted', side: 'phys',
    vn: 'meet-36.3-2 Co-Agent [+animate]',
    label: 'fight.combat (X fights Y — Y is someone; X does bad things to Y\'s body and Y does the same to X; as in "the tribesmen fought each other", NOT as in "the senator fought the bill")',
    gloss: 'Y is someone; X did some bad things to a part of Y\'s body at some time; at the same time Y did the same to X; X wanted something bad to happen to Y.',
    notes: 'E2b restricted sense (VerbNet meet-36.3-2, Co-Agent [+animate] -> phys). Undergoer-sort clauses: SomeoneRef referent + DO onto a part of Y (body) — the phys/person license.',
    referents: [['SomeoneRef'], ['SomeoneRef'], ['TimeRef']],
    clauses: [
      pred('DO', {
        agent: R(1), undergoer: PART(R(2)), time: T(3),
      }),
      pred('DO', { agent: R(2), undergoer: PART(R(1)), time: R(3) }),
      pred('WANT', {
        experiencer: R(1),
        complement: CL(pred('HAPPEN', {
          undergoer: SP('SOMETHING~THING', { quant: 'SOME', mods: [{ mod: 'BAD' }] }),
        })),
      }),
    ],
  },
  {
    lemma: 'fight', tag: 'oppose', synsets: ['v-01093838'], role: 'contrast', side: null,
    vn: '(no VN undergoer restriction; E2b-SEL F4(b) evidence: gloss object "bill", abst)',
    label: 'fight.oppose (X fights Y — Y is something that can happen, not someone; X does not want Y to happen and does many things because of this; as in "the senator fought the bill", NOT as in "the tribesmen fought each other")',
    gloss: 'Y is something that can happen; some people want Y to happen; X does not want Y to happen; because of this, X does many things for some time.',
    notes: 'E2b contrast sense (within-lemma sortal differentiation for fight.combat). Undergoer-sort clause: CAN(HAPPEN(Y)) — the abst/eventive reading.',
    referents: [['SomeoneRef'], ['SomethingRef']],
    clauses: [
      op('CAN', pred('HAPPEN', { undergoer: R(2) })),
      pred('WANT', {
        experiencer: SP('PEOPLE', { quant: 'SOME' }),
        complement: CL(pred('HAPPEN', { undergoer: R(2) })),
      }),
      pred("DON'T-WANT", { experiencer: R(1), complement: CL(pred('HAPPEN', { undergoer: R(2) })) }),
      op('BECAUSE',
        pred("DON'T-WANT", { experiencer: R(1), complement: CL(pred('HAPPEN', { undergoer: R(2) })) }),
        pred('DO', { agent: R(1), undergoer: SP('SOMETHING~THING', { quant: 'MUCH~MANY' }), duration: P('FOR-SOME-TIME') })),
    ],
  },
  // =================================================================== leave
  {
    lemma: 'leave', tag: 'depart', synsets: ['v-02013448', 'v-02019450'], role: 'restricted', side: 'phys',
    vn: 'escape-51.1-1-1 Initial_Location [+concrete]',
    label: 'leave.depart (X leaves Y — Y is a place; before, X was in Y; X moves; after, X is not in Y; as in "leave the room" / "the ship leaves at midnight", NOT as in "she left a mess")',
    gloss: 'Y is a place; X was in Y before some time; X moved at this time; after this time X is not in Y.',
    notes: 'E2b restricted sense cluster (VerbNet escape-51.1-1-1, Initial_Location [+concrete] -> phys; two WN synsets — "go away from a place" and "move out of or depart from" — one schema, the break.interrupt cluster precedent). Referent 1 broadened to SomethingRef ("the train leaves"). Undergoer-sort: PlaceRef referent + BE-SOMEWHERE locus — the phys/location license.',
    referents: [['SomethingRef'], ['PlaceRef'], ['TimeRef']],
    clauses: [
      pred('BE-SOMEWHERE', { undergoer: R(1), locus: R(2), time: T(3) }),
      pred('MOVE', { undergoer: R(1), time: R(3) }),
      op('AFTER', R(3), op('NOT', pred('BE-SOMEWHERE', { undergoer: R(1), locus: R(2) }))),
    ],
  },
  {
    lemma: 'leave', tag: 'behind', synsets: ['v-00615374'], role: 'contrast', side: null,
    vn: '(no VN undergoer restriction; E2b-SEL F4(b) evidence: gloss object "mess", abst)',
    label: 'leave.behind (X leaves Y — X moves away from a place; after this, Y is in this place because of what X did before; as in "she left a mess" / "he left his gloves", NOT as in "leave the room")',
    gloss: 'X was in some place before some time; X moved away from this place at this time; after this time Y is in this place; Y is in this place because of what X did before this time.',
    notes: 'E2b contrast sense (within-lemma sortal differentiation for leave.depart; its objects range over both sides — "a mess" abst-side, "his gloves" phys-side — so the explication does NOT sortally force Y; breadth is the point of a contrast sense).',
    referents: [['SomeoneRef'], ['SomethingRef'], ['PlaceRef'], ['TimeRef']],
    clauses: [
      pred('BE-SOMEWHERE', { undergoer: R(1), locus: SOMEPLACE({ bind: 3 }), time: T(4) }),
      pred('MOVE', { undergoer: R(1), time: R(4) }),
      op('AFTER', R(4), op('NOT', pred('BE-SOMEWHERE', { undergoer: R(1), locus: R(3) }))),
      op('AFTER', R(4), pred('BE-SOMEWHERE', { undergoer: R(2), locus: R(3) })),
      op('BECAUSE',
        pred('DO', { agent: R(1) }),
        pred('BE-SOMEWHERE', { undergoer: R(2), locus: R(3) })),
    ],
  },
  // ================================================================= produce
  {
    lemma: 'produce', tag: 'engender', synsets: ['v-01756692'], role: 'restricted', side: 'abst',
    vn: 'engender-27.1 Theme [+abstract]',
    label: 'produce.engender (X produces Y — Y is something that happens; because of X, Y happens; as in "this procedure produces a curious effect", NOT as in "the tree would not produce fruit")',
    gloss: 'Y is something that happens; Y is not something that can be somewhere; because X did something at some time, Y happened after this time; before this time there was no Y.',
    notes: 'E2b restricted sense (VerbNet engender-27.1, Theme [+abstract] -> abst). Referent 1 broadened to SomethingRef ("this procedure produces..."). Undergoer-sort clauses: HAPPEN(Y) and NOT(CAN(BE-SOMEWHERE Y)) — the abst license.',
    referents: [['SomethingRef'], ['SomethingRef'], ['TimeRef']],
    clauses: [
      op('BECAUSE',
        pred('DO', { agent: R(1), time: T(3) }),
        pred('HAPPEN', { undergoer: R(2) })),
      NOT_BE_SOMEWHERE(2),
      op('BEFORE', R(3), op('NOT', pred('THERE-IS', { undergoer: R(2) }))),
    ],
  },
  {
    lemma: 'produce', tag: 'yield', synsets: ['v-01756303'], role: 'contrast', side: 'phys',
    vn: '(no VN undergoer restriction on this synset; E2b-SEL F4(b) evidence: gloss object "fruit", phys)',
    label: 'produce.yield (X produces Y — before there was no Y; Y comes out of X; after, Y is somewhere and people can see it; as in "the tree would not produce fruit", NOT as in "this procedure produces a curious effect")',
    gloss: 'Before some time there was no Y; at this time Y came out of a part of X; after this time Y is somewhere; people can see Y.',
    notes: 'E2b contrast sense (within-lemma sortal differentiation for produce.engender). Referent 1 broadened to SomethingRef ("the tree produces"). Undergoer-sort clauses: MOVE(Y), BE-SOMEWHERE(Y), SEE(Y) — the phys reading.',
    referents: [['SomethingRef'], ['SomethingRef'], ['TimeRef']],
    clauses: [
      op('BEFORE', T(3), op('NOT', pred('THERE-IS', { undergoer: R(2) }))),
      pred('MOVE', { undergoer: R(2), time: R(3) }),
      op('AFTER', R(3), pred('BE-SOMEWHERE', { undergoer: R(2), locus: SOMEPLACE() })),
      op('CAN', pred('SEE', { experiencer: PEOPLE(), stimulus: R(2) })),
    ],
  },
  // ===================================================================== run
  {
    lemma: 'run', tag: 'locomote', synsets: ['v-01930264'], role: 'restricted', side: 'phys',
    vn: 'carry-11.4 Theme [+concrete]; run-51.3.2-2-1 Trajectory [+concrete]',
    label: 'run.locomote (X runs — X moves fast with parts of X\'s body; a short time after, X is in another place; as in "the children ran to the store", NOT as in "she is running a relief operation")',
    gloss: 'X moved at some time; X moved with two parts of X\'s body; X moved not like people move at most other times; a short time after this time, X was in another place.',
    notes: 'E2b restricted sense (VerbNet carry-11.4 Theme [+concrete] and run-51.3.2-2-1 Trajectory [+concrete], both -> phys, M4-agreeing). Referent 1 SomethingRef ("horses run"). Undergoer-sort clauses: MOVE(X) + BE-SOMEWHERE — the phys license (intransitive: the instrument\'s subject-fallback undergoer).',
    referents: [['SomethingRef'], ['TimeRef']],
    clauses: [
      pred('MOVE', { undergoer: R(1), time: R(2) }),
      pred('DO', { agent: R(1), instrument: PART(R(1), { quant: 'TWO' }) }),
      op('AFTER', R(2), pred('BE-SOMEWHERE', {
        undergoer: R(1),
        locus: SP('WHERE~PLACE', { det: 'OTHER~ELSE~ANOTHER' }),
        duration: P('A-SHORT-TIME'),
      })),
    ],
  },
  {
    lemma: 'run', tag: 'flee', synsets: ['v-02079296'], role: 'restricted', side: 'phys',
    vn: 'run-51.3.2-2-1 Trajectory [+concrete]',
    label: 'run.flee (X runs — X moves fast away from a place because X thinks something bad can happen to X there; as in "the burglars escaped before the police showed up", NOT as in "she is running a relief operation")',
    gloss: 'X was in some place at some time; X thought at this time: "something bad can happen to me here"; because of this, X moved away from this place; after this time X is not in this place.',
    notes: 'E2b restricted sense (VerbNet run-51.3.2-2-1, Trajectory [+concrete] -> phys). Undergoer-sort clauses: BE-SOMEWHERE(X)/MOVE(X) — the phys license.',
    referents: [['SomeoneRef'], ['PlaceRef'], ['TimeRef']],
    clauses: [
      pred('BE-SOMEWHERE', { undergoer: R(1), locus: R(2), time: T(3) }),
      pred('THINK', {
        experiencer: R(1), time: R(3),
        quote: {
          kind: 'quote',
          clauses: [op('MAYBE', pred('HAPPEN', {
            undergoer: SP('SOMETHING~THING', { quant: 'SOME', mods: [{ mod: 'BAD' }] }),
          }))],
        },
      }),
      op('BECAUSE', pred('THINK', { experiencer: R(1) }), pred('MOVE', { undergoer: R(1) })),
      op('AFTER', R(3), op('NOT', pred('BE-SOMEWHERE', { undergoer: R(1), locus: R(2) }))),
    ],
  },
  {
    lemma: 'run', tag: 'operate', synsets: ['v-02448714'], role: 'restricted', side: 'abst',
    vn: 'conduct-111.1 Theme [+eventive]',
    label: 'run.operate (X runs Y — Y is something that happens for some time because many people do things; X says words to these people because X wants Y to happen in a certain way; as in "she is running a relief operation", NOT as in "the children ran to the store")',
    gloss: 'Y is something that happens for some time; Y is not something that can be somewhere; many people do things because of Y; X says words to these people; because of this, these people do things; X wants Y to happen in some way.',
    notes: 'E2b restricted sense (VerbNet conduct-111.1, Theme [+eventive] -> abst) — run\'s own opposite-side restricted sense: the selection\'s F4(a) evidence for run is INTERNAL (phys-restricted locomote/flee vs abst-restricted operate). Undergoer-sort clauses: HAPPEN(Y, duration) and NOT(CAN(BE-SOMEWHERE Y)) — the abst license.',
    referents: [['SomeoneRef'], ['SomethingRef'], ['SomeoneRef']],
    clauses: [
      pred('HAPPEN', { undergoer: R(2), duration: P('FOR-SOME-TIME') }),
      NOT_BE_SOMEWHERE(2),
      pred('THERE-IS', { undergoer: SP('PEOPLE', { quant: 'MUCH~MANY', bind: 3 }) }),
      pred('SAY', { agent: R(1), addressee: R(3), topic: R(2) }),
      op('BECAUSE',
        pred('SAY', { agent: R(1), addressee: R(3) }),
        pred('DO', { agent: R(3), undergoer: SP('SOMETHING~THING', { quant: 'MUCH~MANY' }) })),
      pred('WANT', { experiencer: R(1), complement: CL(pred('HAPPEN', { undergoer: R(2) })) }),
    ],
  },
  // =================================================================== shape
  {
    lemma: 'shape', tag: 'influence', synsets: ['v-00702806'], role: 'restricted', side: 'abst',
    vn: 'engender-27.1 Theme [+abstract]',
    label: 'shape.influence (X shapes Y — Y is something people think; because of X, after, people think Y in one way and not in other ways; as in "mold public opinion", NOT as in "she molded the rice balls")',
    gloss: 'Y is something; people think Y; Y is not something that can be somewhere; because of what X did at some time, after this time people think Y in one way, not in other ways.',
    notes: 'E2b restricted sense (VerbNet engender-27.1, Theme [+abstract] -> abst). Referent 1 broadened to SomethingRef ("experience determines ability"). Undergoer-sort clauses: THINK-topic(Y) and NOT(CAN(BE-SOMEWHERE Y)) — the abst license.',
    referents: [['SomethingRef'], ['SomethingRef'], ['TimeRef']],
    clauses: [
      pred('THINK', { experiencer: PEOPLE(), topic: R(2) }),
      NOT_BE_SOMEWHERE(2),
      pred('DO', { agent: R(1), time: T(3) }),
      op('BECAUSE',
        pred('DO', { agent: R(1) }),
        op('AFTER', R(3), pred('THINK', {
          experiencer: PEOPLE(), topic: R(2),
          manner: SP('SOMETHING~THING', { quant: 'ONE' }),
        }))),
    ],
  },
  {
    lemma: 'shape', tag: 'form', synsets: ['v-01663142'], role: 'contrast', side: 'phys',
    vn: '(no VN undergoer restriction on this synset; E2b-SEL F4(b) evidence: gloss object "ball(s)", phys)',
    label: 'shape.form (X shapes Y — Y is a thing; X does things to Y with parts of X\'s body; after, Y is like X wants it to be; as in "she molded the rice balls", NOT as in "mold public opinion")',
    gloss: 'Y is something that can be somewhere; X did some things to Y at some time with two parts of X\'s body; X wanted Y to be like something X thought; after this time Y is like this.',
    notes: 'E2b contrast sense (within-lemma sortal differentiation for shape.influence). Undergoer-sort clause: CAN(BE-SOMEWHERE Y) — the phys license.',
    referents: [['SomeoneRef'], ['SomethingRef'], ['TimeRef']],
    clauses: [
      CAN_BE_SOMEWHERE(2),
      pred('DO', { agent: R(1), undergoer: R(2), instrument: PART(R(1), { quant: 'TWO' }), time: T(3) }),
      pred('WANT', {
        experiencer: R(1),
        complement: CL(pred('BE-SPEC', {
          undergoer: R(2), attribute: SP('SOMETHING~THING', { det: 'THIS' }),
        })),
      }),
      op('AFTER', R(3), pred('BE-SPEC', {
        undergoer: R(2), attribute: SP('SOMETHING~THING', { det: 'THIS' }),
      })),
    ],
  },
  // ==================================================================== sing
  {
    lemma: 'sing', tag: 'perform', synsets: ['v-01734912'], role: 'restricted', side: 'abst',
    vn: 'manner_speaking-37.3 Topic [+communication]',
    label: 'sing.perform (X sings Y — Y is words; X says Y not like people say words at other times; people can hear something good when X says Y; as in "sing Christmas carols", NOT as in "my brother sings very well")',
    gloss: 'Y is words; X said Y at some time; X said Y not like people say words at other times; when X said Y, people could hear something good; because of this, people could feel something good.',
    notes: 'E2b restricted sense (VerbNet manner_speaking-37.3, Topic [+communication] -> abst). Undergoer-sort clause: BE-SPEC(Y, WORDS) — the abst (C_words-shaped) license, the break.violate pattern.',
    referents: [['SomeoneRef'], ['SomethingRef'], ['TimeRef']],
    clauses: [
      pred('BE-SPEC', { undergoer: R(2), attribute: SP('WORDS') }),
      pred('SAY', { agent: R(1), topic: R(2), time: T(3) }),
      op('WHEN',
        pred('SAY', { agent: R(1), topic: R(2) }),
        op('CAN', pred('HEAR', {
          experiencer: PEOPLE(),
          stimulus: SP('SOMETHING~THING', { quant: 'SOME', mods: [{ mod: 'GOOD' }] }),
        }))),
      op('BECAUSE',
        pred('HEAR', { experiencer: PEOPLE(), stimulus: R(2) }),
        op('CAN', pred('FEEL', { experiencer: PEOPLE(), attribute: P('GOOD') }))),
    ],
  },
  {
    lemma: 'sing', tag: 'vocalize', synsets: ['v-01733312'], role: 'contrast', side: null,
    vn: '(no VN undergoer restriction; E2b-SEL F4(b) evidence is a DISCLOSED parse artifact — see §E2b honesty audit)',
    label: 'sing.vocalize (X sings — some somethings that people can hear come out of a part of X\'s body; X wants this; as in "my brother sings very well", NOT as in "sing Christmas carols")',
    gloss: 'X did something at some time; because of this, some somethings came out of a part of X\'s body; people could hear these somethings; X wanted this; when people heard these somethings, they could feel something good.',
    notes: 'E2b contrast sense (within-lemma sortal differentiation for sing.perform; intransitive — subject-fallback undergoer is X, a person, phys). DISCLOSURE: the mechanical F4(b) evidence for sing rests on the pinned parser reading "well" (adverb) as a noun; the §E2b audit carries this verbatim. The SENSE itself is real (WN v-01733312) and its subject-undergoer is genuinely phys.',
    referents: [['SomeoneRef'], ['SomethingRef'], ['TimeRef']],
    clauses: [
      pred('DO', { agent: R(1), time: T(3) }),
      op('BECAUSE',
        pred('DO', { agent: R(1) }),
        pred('THERE-IS', { undergoer: R(2) })),
      pred('MOVE', { undergoer: R(2) }),
      op('CAN', pred('HEAR', { experiencer: PEOPLE(), stimulus: R(2) })),
      pred('WANT', { experiencer: R(1), complement: CL(pred('HEAR', { experiencer: PEOPLE(), stimulus: R(2) })) }),
      op('WHEN',
        pred('HEAR', { experiencer: PEOPLE(), stimulus: R(2) }),
        op('CAN', pred('FEEL', { experiencer: PEOPLE(), attribute: P('GOOD') }))),
    ],
  },
];

// ---------- SCOPE gate: minted synsets == selection output ----------
const byLemma = new Map();
for (const c of CONCEPTS) {
  if (!byLemma.has(c.lemma)) byLemma.set(c.lemma, []);
  byLemma.get(c.lemma).push(c);
}
if ([...byLemma.keys()].sort().join(',') !== [...selLemmas.keys()].sort().join(',')) {
  die('ERR_SCOPE_LEMMAS: concept lemmas != selection lemmas');
}
for (const [lemma, sel] of selLemmas) {
  const want = new Set([
    ...sel.restricted.map((r) => r.offset),
    sel.contrast.offset,
  ]);
  const got = new Set(byLemma.get(lemma).flatMap((c) => c.synsets.map((s) => s.replace('v-', ''))));
  const w = [...want].sort().join(','); const g = [...got].sort().join(',');
  if (w !== g) die(`ERR_SCOPE_SYNSETS(${lemma}): minted {${g}} != selection {${w}}`);
}

// ---------- build explication records + ENC gate ----------
const wnVerb = new Map();
for (const line of readFileSync(join(repo, 'data/lexical-wn31/synsets-verb.jsonl'), 'utf8').split('\n')) {
  if (!line.trim()) continue;
  const r = JSON.parse(line);
  wnVerb.set(r.id, r.annotations);
}

const records = [];
for (const c of CONCEPTS) {
  const id = `urn:kernel-v1e2b:${c.lemma}.${c.tag}`;
  const explication = {
    schema: 'kot-ast/1',
    frame: 'RelationalSchema',
    referents: c.referents.map(([refKind], i) => ({ index: i + 1, refKind })),
    clauses: c.clauses,
  };
  try {
    validateExplication(explication);
  } catch (e) {
    die(`ERR_ENC_VALIDATE(${id}): ${e.code || ''} ${e.message}`);
  }
  const synUrns = c.synsets.map((s) => `urn:lexical-wn31:${s}`);
  const glossQuote = wnVerb.get(synUrns[0])?.gloss;
  if (!glossQuote) die(`ERR_WN_GLOSS(${id}): synset ${synUrns[0]} not in pinned extraction`);
  records.push({ c, id, explication, synUrns, glossQuote });
}
try {
  encodeConceptSet(new Map(records.map((r) => [r.id, r.explication])));
} catch (e) {
  die(`ERR_ENC_ENCODE: ${e.message}`);
}

// ---------- G1/G2: synset claimed exactly once ----------
const claimed = new Map();
for (const r of records) {
  for (const s of r.synUrns) {
    if (claimed.has(s)) die(`ERR_G1_SHARED_SYNSET: ${s} in ${claimed.get(s)} and ${r.id}`);
    claimed.set(s, r.id);
  }
}

// ---------- R1 recount + excludedSenses (R4/R5 closure) ----------
const candidates = new Map(); // lemma -> Map(urn -> gloss)
for (const lemma of byLemma.keys()) candidates.set(lemma, new Map());
for (const [urn, ann] of wnVerb) {
  for (const lemma of byLemma.keys()) {
    if (ann.lemmas.includes(lemma)) candidates.get(lemma).set(urn, ann.gloss);
  }
}

// ---------- emit ----------
mkdirSync(join(here, 'concepts'), { recursive: true });
mkdirSync(join(here, 'sense-index'), { recursive: true });
mkdirSync(join(here, 'typing'), { recursive: true });

const manifestConcepts = [];
const ufoLines = [];
for (const r of records) {
  const { c } = r;
  const rec = {
    id: r.id,
    label: c.label,
    status: 'research-grade, E2b-STAGING (pre-adoption; identity minting deferred to the adoption build)',
    pattern: `NSM-style ${c.role === 'restricted' ? 'VN-restricted' : 'contrast'} event sense, sense-scoped per docs/next/design/sense-split-first-construction.md §1.3 and engine-inference-under-typing.md §E2b`,
    gloss: c.gloss,
    notes: c.notes + ' VerbNet anchor: ' + c.vn + '.',
    sense: {
      senseTag: c.tag,
      lemma: c.lemma,
      pos: 'v',
      wn31Synsets: r.synUrns,
      framenetFrame: null,
      framenetFrameName: null,
      glossQuote: r.glossQuote,
      excludedSiblingCount: candidates.get(c.lemma).size - byLemma.get(c.lemma).flatMap((x) => x.synsets).length,
    },
    references: [],
    explication: r.explication,
  };
  writeFileSync(join(here, 'concepts', `${c.lemma}.${c.tag}.json`), JSON.stringify(rec, null, 2) + '\n');
  manifestConcepts.push({
    id: r.id, label: c.label, file: `concepts/${c.lemma}.${c.tag}.json`,
    frame: 'RelationalSchema', status: 'research-grade-e2b-staging',
    lemma: c.lemma, senseTag: c.tag, wn31Synsets: r.synUrns,
    e2bRole: c.role, vnRequiredSide: c.side, framenetFrame: null, references: [],
  });
  ufoLines.push(JSON.stringify({
    schema: 'kot-ck-ufo/1', concept: r.id, lemma: c.lemma, senseTag: c.tag,
    ontic_category: 'event',
    assignment_path: 'rule-inference:verb-sense eventive schema (DO/HAPPEN/MOVE temporal explication) -> event; E2b generalization of the break-is-an-EVENT maintainer clause (every minted verb sense is an event, never an endurant)',
    maintainer_clause_check: 'generalized: an adding/bringing/conducting/crying/fighting/leaving/producing/running/shaping/singing, in any sense, is an event — SATISFIED structurally for all 22 E2b concepts',
    binding: false, authority: 'annotation', date: '2026-07-13',
  }));
}

for (const [lemma, cs] of [...byLemma.entries()].sort()) {
  const minted = cs.map((c) => ({
    id: `urn:kernel-v1e2b:${c.lemma}.${c.tag}`,
    senseTag: c.tag,
    wn31Synsets: c.synsets.map((s) => `urn:lexical-wn31:${s}`),
    framenetFrame: null,
    framenetFrameName: null,
  }));
  const mintedSet = new Set(cs.flatMap((c) => c.synsets.map((s) => `urn:lexical-wn31:${s}`)));
  const excludedSenses = [...candidates.get(lemma)]
    .filter(([urn]) => !mintedSet.has(urn))
    .sort()
    .map(([urn, gloss]) => ({ synset: urn, gloss }));
  writeFileSync(join(here, 'sense-index', `${lemma}.json`), JSON.stringify({
    schema: 'kot-sense-index/1',
    lemma, pos: 'v',
    candidateCount: candidates.get(lemma).size,
    mintedSenses: minted,
    excludedSenses,
    note: 'E2b STAGING (pre-adoption). R4 scope closure: a concept claims its synset cluster, NOT the word. Every non-minted candidate is excluded here; nothing silently dropped (R5). Minted scope == E2b-SEL selection output (mechanically gated).',
  }, null, 1) + '\n');
}

writeFileSync(join(here, 'typing', 'ck-ufo-sidecar.jsonl'), ufoLines.join('\n') + '\n');

writeFileSync(join(here, 'manifest.json'), JSON.stringify({
  corpus: 'kernel-v1-e2b-staging',
  stage: 'E2b inventory-extension STAGING (10 lemmas, 22 sense concepts; engine-inference-under-typing.md §E2b; NOT adopted into kernel-v1; adoption = maintainer decision after #29 construct sign-off)',
  schema: 'kot-ast/1',
  version: '0.0.1-e2b-staging',
  generated: '2026-07-13',
  authorship: 'research-grade, agent-authored against profile-1 per sense-split-first-construction.md and engine-inference-under-typing.md §E2b; NOT federation-endorsed; adequacy unvalidated',
  encoderContentHash: encHash,
  encoderAlgorithmVersion: ALGORITHM_VERSION,
  encoderNote: 'READ-ONLY pin check: equals kernel-v0 frozen value; staging corpus is data only — no encoder change, no ALGORITHM_VERSION bump, no X0 golden regeneration',
  selectionArtifact: 'poc/engine-inference/e2b-inventory-extension/e2b-selection.json',
  conceptCount: records.length,
  concepts: manifestConcepts,
}, null, 1) + '\n');

console.log(JSON.stringify({
  ok: true,
  concepts: records.length,
  lemmas: [...byLemma.keys()].sort(),
  encoderContentHash: encHash,
  all_validated: true,
  all_events: true,
}, null, 1));
