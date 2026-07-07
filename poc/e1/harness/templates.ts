/**
 * E1 cloze template-type inventory + held-out split (docs/poc-design.md E1:
 * "Primary endpoint: concept cloze on held-out template *types* (the
 * held-out unit is template-type x concept, not instance — MAJOR 6)").
 * Bead kernel-of-truth-bk0. Generated and committed BEFORE any training run.
 *
 * TWO FAMILIES:
 *
 * 1. DEFINITIONAL cloze types (the primary-endpoint instrument): 16 frame
 *    types, each embedding the concept's kernel-v0 `gloss` field followed by
 *    a single `{c}` slot (slot strictly AFTER the gloss so a causal LM can
 *    be scored at the slot). The (type x concept) grid is mechanical:
 *    16 x 54 items; the held-out split is over TYPES (8 dev / 8 held-out,
 *    seeded, recorded here). Scoring = candidate-restricted argmax over the
 *    54 concept-token logits at the slot position.
 *    NOTE (documented): glosses come verbatim from data/kernel-v0; some
 *    glosses contain OTHER concepts' surface words (reference-bearing
 *    kernel entries). Frames are machine-checked leak-free; glosses are
 *    fixed data, identical across arms, and covered by the step-0
 *    circularity baseline (MAJOR 5).
 *
 * 2. PROBE stimulus types (secondary): bank-specific usage frames (POS bank
 *    per concept transcribed from poc/e2/harness/items.ts, + a `rel` bank
 *    for the three multiword relational concepts). The concept TOKEN
 *    occupies the `{c}` slot mid-sentence with >= 2 word tokens after it;
 *    the linear probe reads MID-LAYER states at NON-concept positions only
 *    (pre-registered probe position: the final word token of the sentence),
 *    per the E1 circularity guard. Split 4 probe-train / 4 probe-test types
 *    per bank, seeded.
 *
 * FAIL-CLOSED CHECKS (run at generation): every frame has exactly one {c}
 * (definitional: exactly one {gloss}, before {c}); no frame text maps to any
 * kernel CONCEPT (running the real mapper), nor abstains with a concept
 * candidate — a frame word that collides with a concept exponent would leak
 * concept-token training signal into the eval instrument.
 */

import { join } from 'node:path';
import {
  buildLexicon,
  loadManifestConcepts,
  mapText,
} from '@jeswr/kernel-mapper';
import { DetStream } from '@jeswr/kernel-encoder';
import { KERNEL_V0_DIR, corpusPin, isMain, loadConcepts, mapperPin, slugOf, writeInput } from './common.js';

// ---------------------------------------------------------------------------
// POS bank per concept — transcribed from poc/e2/harness/items.ts PROBE
// (test/e1prep.test.ts cross-checks this transcription against the e2 source
// text, read-only). The three multiword relational concepts, excluded from
// E2's word probing, get the `rel` bank here: their concept TOKEN can fill a
// relational slot even though no single surface word could.
// ---------------------------------------------------------------------------

export type Bank = 'adjPerson' | 'adjThing' | 'verb' | 'noun' | 'prep' | 'rel';

export const CONCEPT_BANK: Record<string, Bank> = {
  afraid: 'adjPerson', alive: 'adjPerson', angry: 'adjPerson', archived: 'adjThing',
  begin: 'verb', believe: 'verb', birth: 'noun', bookmark: 'noun', break: 'verb',
  broken: 'adjThing', cause: 'verb', celebration: 'noun', change: 'noun',
  condolence: 'noun', conversation: 'noun', dead: 'adjPerson', death: 'noun',
  end: 'verb', event: 'noun', find: 'verb', forget: 'verb', friend: 'noun',
  gift: 'noun', give: 'verb', grieving: 'adjPerson', happy: 'adjPerson',
  'has-part': 'rel', help: 'verb', helpful: 'adjPerson', inside: 'prep',
  kind: 'noun', learn: 'verb', liar: 'noun', lie: 'noun', lose: 'verb',
  lost: 'adjThing', make: 'verb', 'maker-of': 'rel', memory: 'noun',
  near: 'prep', 'part-of': 'rel', promise: 'noun', remember: 'verb',
  reminder: 'noun', repair: 'verb', right: 'adjThing', sad: 'adjPerson',
  take: 'verb', teacher: 'noun', thief: 'noun', trustworthy: 'adjPerson',
  useful: 'adjThing', visible: 'adjThing', wrong: 'adjThing',
};

// ---------------------------------------------------------------------------
// Definitional cloze frames ({gloss} then {c}; lowercase TinyStories register)
// ---------------------------------------------------------------------------

export const DEFINITIONAL_TYPES: readonly string[] = [
  'people say : {gloss} they call this {c} .',
  'the old man said : {gloss} the word for this is {c} .',
  'listen : {gloss} we say it like this : {c} .',
  'mom says : {gloss} there is a word for this . the word is {c} .',
  '{gloss} this is what people call {c} .',
  'think about this : {gloss} people have one word for it : {c} .',
  '{gloss} when it is like this , people say the word {c} .',
  'a book says : {gloss} the name for this is {c} .',
  'i will tell you something . {gloss} people call it {c} .',
  'here is a riddle : {gloss} the answer is {c} .',
  '{gloss} because of this , the best word is {c} .',
  'dad said : {gloss} so we say {c} .',
  'someone says : {gloss} another word for all this is {c} .',
  'you know it : {gloss} its name is {c} .',
  '{gloss} all of this is called {c} .',
  'the wise woman said : {gloss} this thing is {c} .',
];

// ---------------------------------------------------------------------------
// Probe stimulus frames per bank ({c} mid-sentence, >= 2 word tokens after)
// ---------------------------------------------------------------------------

export const PROBE_TYPES: Record<Bank, readonly string[]> = {
  adjPerson: [
    'the little girl was very {c} that day , and everyone could see it .',
    'tom felt {c} when he came home , so he told his mom about it .',
    'my sister was {c} all morning , but then things got better .',
    'the old man seemed {c} , and the children saw it too .',
    'she was so {c} that she could not say a word .',
    'he looked {c} while he walked to the park with his dog .',
    'the boy felt very {c} after the long trip , and he sat down .',
    'grandma was {c} , so the kids stayed with her all day .',
  ],
  adjThing: [
    'the toy was {c} , so tom put it on the table .',
    'her cup looked {c} after the fall , and she showed it to dad .',
    'the big box in the room was {c} , and everyone knew it .',
    'that book seemed {c} to the little girl , but she kept it .',
    'the wall was very {c} , so the man looked at it for a long time .',
    'his bike was {c} , and he wanted to ride it again .',
    'the door was {c} that morning , so mom opened it slowly .',
    'the picture on the wall was {c} , and the kids talked about it .',
  ],
  verb: [
    'tom wanted to {c} the ball , so he went to the garden .',
    'she tried to {c} her toys before dinner , and mom smiled at her .',
    'the boy could {c} the little bird , and he was glad about it .',
    'we will {c} the cake together , said the girl to her brother .',
    'dad had to {c} the old car , so he got up early .',
    'they did not {c} the door , because it was late .',
    'can you {c} the song with me , asked the small boy ?',
    'every day the kids would {c} something new at school .',
  ],
  noun: [
    'tom saw the {c} in the garden , and he ran to it .',
    'the {c} was big and bright , so the kids looked at it .',
    'she put the {c} on the table next to the cup .',
    'everyone talked about the {c} for a long time after dinner .',
    'the little girl drew a picture of the {c} for her mom .',
    'a {c} is something people think about , said the old man .',
    'the children liked the {c} all afternoon .',
    'dad told a story about a {c} before bed .',
  ],
  prep: [
    'the cat sat {c} the box , and the kids laughed .',
    'her ball was {c} the house , so she went to get it .',
    'tom put the toy {c} the bag before school .',
    'the bird stayed {c} the tree all morning .',
    'they played {c} the garden until it got dark .',
    'the dog slept {c} the door every night .',
    'mom kept the keys {c} the drawer , away from the baby .',
    'the fish swam {c} the pond , and the boy watched it .',
  ],
  rel: [
    'the wheel is {c} the car , said the man to his son .',
    'every window is {c} the house , and the kids know it .',
    'the old woman is {c} the chair , said tom with a smile .',
    'this door is {c} the barn , the farmer said .',
    'a leg is {c} the table , and that is easy to see .',
    'the roof is {c} the home , dad said to the twins .',
    'the man is {c} the toy , because he worked on it all day .',
    'each page is {c} the book , the girl said .',
  ],
};

// ---------------------------------------------------------------------------
// Fail-closed leak checks
// ---------------------------------------------------------------------------

function checkFrame(frame: string, family: string, needsGloss: boolean): void {
  const cCount = frame.split('{c}').length - 1;
  if (cCount !== 1) throw new Error(`ERR_TEMPLATE: '${frame}' (${family}) has ${cCount} {c} slots`);
  const gCount = frame.split('{gloss}').length - 1;
  if (needsGloss) {
    if (gCount !== 1) throw new Error(`ERR_TEMPLATE: '${frame}' has ${gCount} {gloss} slots`);
    if (frame.indexOf('{gloss}') > frame.indexOf('{c}')) {
      throw new Error(`ERR_TEMPLATE: '${frame}' — {c} must FOLLOW {gloss} (causal scoring)`);
    }
  } else if (gCount !== 0) {
    throw new Error(`ERR_TEMPLATE: probe frame '${frame}' must not contain {gloss}`);
  }
  if (!needsGloss) {
    const after = frame.slice(frame.indexOf('{c}') + 3);
    const words = after.match(/[a-z]+/g) ?? [];
    if (words.length < 2) {
      throw new Error(`ERR_TEMPLATE: probe frame '${frame}' needs >= 2 word tokens after {c}`);
    }
  }
}

/** No frame word may map to a concept or abstain with a concept candidate. */
function checkNoConceptLeak(frames: readonly string[], family: string): void {
  const lexicon = buildLexicon(loadManifestConcepts(join(KERNEL_V0_DIR, 'manifest.json')));
  for (const frame of frames) {
    const text = frame.replace(/\{c\}/g, ' ').replace(/\{gloss\}/g, ' ');
    for (const t of mapText(text, lexicon)) {
      if (!t.isWord) continue;
      const d = t.decision;
      if (d.kind === 'concept') {
        throw new Error(
          `ERR_TEMPLATE_LEAK (${family}): '${t.norm}' in '${frame}' maps to ${d.conceptId}`,
        );
      }
      if (d.kind === 'abstain' && d.candidates.some((c) => c.kind === 'concept')) {
        throw new Error(
          `ERR_TEMPLATE_LEAK (${family}): '${t.norm}' in '${frame}' abstains with a concept candidate`,
        );
      }
    }
  }
}

/** Seeded split of [0,n) into two halves via the encoder DetStream (Fisher-Yates). */
export function seededSplit(label: string, n: number): { first: number[]; second: number[] } {
  const stream = new DetStream(`perm/${label}`);
  const p = Array.from({ length: n }, (_, i) => i);
  for (let i = n - 1; i > 0; i--) {
    const j = stream.nextBelow(i + 1);
    const t = p[i]!;
    p[i] = p[j]!;
    p[j] = t;
  }
  const half = Math.floor(n / 2);
  return { first: p.slice(0, half).sort((a, b) => a - b), second: p.slice(half).sort((a, b) => a - b) };
}

function main(): void {
  for (const f of DEFINITIONAL_TYPES) checkFrame(f, 'definitional', true);
  checkNoConceptLeak(DEFINITIONAL_TYPES, 'definitional');
  for (const [bank, frames] of Object.entries(PROBE_TYPES)) {
    for (const f of frames) checkFrame(f, `probe/${bank}`, false);
    checkNoConceptLeak(frames, `probe/${bank}`);
  }

  const concepts = loadConcepts();
  const slugs = concepts.map((c) => slugOf(c.id));
  for (const s of slugs) {
    if (CONCEPT_BANK[s] === undefined) {
      throw new Error(`ERR_BANK: concept '${s}' has no bank assignment — corpus changed?`);
    }
  }
  for (const s of Object.keys(CONCEPT_BANK)) {
    if (!slugs.includes(s)) throw new Error(`ERR_BANK: stale bank entry '${s}'`);
  }

  const defSplit = seededSplit('e1/templates/def-heldout', DEFINITIONAL_TYPES.length);
  const probeSplit: Record<string, { train: number[]; test: number[] }> = {};
  for (const bank of Object.keys(PROBE_TYPES)) {
    const s = seededSplit(`e1/templates/probe-split/${bank}`, PROBE_TYPES[bank as Bank].length);
    probeSplit[bank] = { train: s.first, test: s.second };
  }

  writeInput('cloze-templates.json', {
    artifact: 'e1-cloze-templates',
    date: new Date().toISOString(),
    provenance: { mapper: mapperPin(), kernelV0: corpusPin() },
    heldOutUnit:
      'template-type x concept (MAJOR 6): the PRIMARY endpoint is concept cloze accuracy ' +
      'computed ONLY over heldOut definitional types x all scoreable concepts; dev types are ' +
      'for tuning/monitoring and are descriptive',
    scoring:
      'candidate-restricted cloze: logits at the {c} slot position, argmax over the 54 ' +
      'concept-token ids; teacher-forced left context = frame text up to the slot with ' +
      '{gloss} filled from kernel-v0 gloss (verbatim, lowercased by the tokenizer)',
    glossNote:
      'glosses may contain other concepts\' surface words (reference-bearing kernel entries); ' +
      'frames are machine-checked concept-leak-free, glosses are fixed data identical across ' +
      'arms and covered by the step-0 circularity baseline',
    definitional: {
      types: DEFINITIONAL_TYPES,
      split: {
        label: 'perm/e1/templates/def-heldout (encoder DetStream)',
        dev: defSplit.first,
        heldOut: defSplit.second,
      },
    },
    probe: {
      note:
        'probe stimuli; linear probe reads MID-LAYER hidden state at the pre-registered ' +
        'NON-concept position = final word token of the sentence (circularity guard: probes ' +
        'only on mid-layer states at non-concept positions)',
      types: PROBE_TYPES,
      split: probeSplit,
      splitLabel: 'perm/e1/templates/probe-split/<bank> (encoder DetStream)',
    },
    conceptBank: CONCEPT_BANK,
    concepts: concepts.map((c) => ({ id: c.id, slug: slugOf(c.id), bank: CONCEPT_BANK[slugOf(c.id)], gloss: c.gloss })),
  });
  console.log(
    `definitional: ${DEFINITIONAL_TYPES.length} types (dev [${defSplit.first}] heldOut [${defSplit.second}]); ` +
      `probe banks: ${Object.keys(PROBE_TYPES).join(', ')}`,
  );
}

if (isMain(import.meta.url)) main();
