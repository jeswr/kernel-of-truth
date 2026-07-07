/**
 * E2 context generation (docs/poc-design.md E2 protocol: "each word in >=20
 * contexts, mean-pooled over word tokens").
 *
 * Design (published):
 *   - 5 hand-authored template banks (one per item frame class, items.ts),
 *     24 templates each -> every word gets 24 contexts (>= the pre-registered
 *     20). Simple naturalistic English, deliberately TinyStories-compatible
 *     (short sentences, concrete scenes) so the smallest model family is not
 *     disadvantaged.
 *   - Each template contains the slot `{w}` exactly once; the target word is
 *     substituted verbatim (no inflection), and the character span of the
 *     substitution is shipped so the runner can map it to token positions
 *     via tokenizer offset mappings.
 *   - Generation is fully deterministic: every word of a bank receives ALL
 *     24 templates of that bank (no sampling, so no seed is consumed; the
 *     brief's "seeded" requirement is satisfied vacuously and this is
 *     documented in README.md).
 *   - Frequency-matched random words (freqPools.ts) are substituted into the
 *     SAME bank templates, so the random-set null sees identical contexts.
 *   - FAIL-CLOSED CHECK: no template may contain any probe word as an exact
 *     token (would contaminate other items' representations). Inflected
 *     forms of probe words are additionally avoided by authoring but only
 *     exact forms are machine-checked (documented limitation).
 *   - Known naturalism compromises (documented, accepted): `kind` (sortal
 *     noun) reads awkwardly in definite-NP frames; `inside`/`near` share a
 *     locative bank in which a few frames fit one better than the other.
 */

import { encoderContentHash } from '@jeswr/kernel-encoder';
import { corpusPin, isMain, writeInput } from './common.js';
import { loadCorpus } from './corpus.js';
import { buildItems } from './items.js';
import type { Bank } from './items.js';

export const TEMPLATE_BANKS: Record<Bank, readonly string[]> = {
  adjPerson: [
    'Maria was very {w} that day.',
    'The old man seemed {w} when we spoke to him.',
    'Everyone could see that the boy was {w}.',
    'She told me she felt {w} after the long journey.',
    'My grandmother was {w} for a long time.',
    'The children were {w}, and nobody knew why.',
    'He looked {w} as he walked into the room.',
    'I think the new neighbour is {w}.',
    'Her father sounded {w} on the phone last night.',
    'The little girl felt {w} when the lights went out.',
    'People in the village said the shepherd was {w}.',
    'Before the week was over, the whole family was {w}.',
    'You seem {w} today, my sister said quietly.',
    'The soldier remained {w} through the winter.',
    'Being {w} is hard for anyone.',
    'Nobody wanted to admit they were {w}.',
    'The young woman appeared {w} at the meeting.',
    'After the storm, the farmer was still {w}.',
    'Our coach was clearly {w} this morning.',
    'The baby seemed less {w} once the music played.',
    'His brother had always been {w}.',
    'Those two sisters were both {w} back then.',
    'The king grew {w} as the years passed.',
    'Why is your uncle so {w} lately?',
  ],
  adjThing: [
    'The old clock was {w} when we got it.',
    'Everyone agreed that the plan was {w}.',
    'The door seemed {w} to me.',
    'Her answer was {w}, and we all knew it.',
    'That old bridge has been {w} for years.',
    'The map turned out to be {w}.',
    'What he did that night was {w}.',
    'The little machine was {w} again.',
    'Most of the letters were {w}.',
    'The photograph was {w} after all those years.',
    'This part of the record is {w}.',
    'The instructions were {w} from the very start.',
    'It was {w}, and nothing could be done about it.',
    'The old road was {w} in several places.',
    'They said the files were {w} now.',
    'The toy was {w} when the box arrived.',
    'His story was {w} in every detail.',
    'The window latch was {w} once more.',
    'The whole system was {w} by then.',
    'The recipe was {w}, just as she had warned.',
    'The ladder looked {w} to everyone.',
    'The results were {w} this time.',
    'The engine was {w} after the trip.',
    'The agreement was {w} from the start.',
  ],
  verb: [
    "She didn't want to {w} the old clock.",
    'He said he would {w} it before dinner.',
    'The boy tried to {w} something new every day.',
    'We had to {w} it before the rain came.',
    'Nobody could {w} anything that summer.',
    'They will {w} the little house next spring.',
    'I did not {w} it, she said.',
    'You should {w} this one first.',
    'The workers wanted to {w} more than before.',
    'Sometimes it is hard to {w} what matters.',
    'Her mother taught her how to {w} things properly.',
    'The men decided to {w} the boat at dawn.',
    'It took courage to {w} anything back then.',
    'Would you {w} this for me tomorrow?',
    'The plan was simple: {w} first, talk later.',
    'He can {w} almost anything with his hands.',
    'The sisters chose to {w} the garden gate.',
    'No one dared to {w} the stone wall.',
    'We might {w} the whole thing next week.',
    'To {w} well, you need patience.',
    'The farmer went out to {w} the fence.',
    'She hoped to {w} it without any trouble.',
    'Every child manages to {w} in a different way.',
    'They never meant to {w} anything at all.',
  ],
  noun: [
    'Everyone talked about the {w} for days.',
    'She wrote about the {w} in her diary.',
    'The {w} surprised the whole village.',
    'Nobody mentioned the {w} at dinner.',
    'He could not stop thinking about the {w}.',
    'The {w} was all anyone spoke of that winter.',
    'After the {w}, things were never the same.',
    'The old woman described the {w} well.',
    'They planned the {w} for many weeks.',
    'The {w} took place by the river.',
    'Her letter was mostly about the {w}.',
    'The {w} meant a great deal to my family.',
    'We heard about the {w} from a neighbour.',
    'The {w} came earlier than expected.',
    'His book opens with the {w}.',
    'The {w} altered how people saw the town.',
    'That {w} is still talked about today.',
    'The {w} happened on a cold morning.',
    'She kept a record of the {w}.',
    'The {w} brought the two families together.',
    'Looking back, the {w} mattered most.',
    'The {w} was announced at noon.',
    'My grandfather often spoke of the {w}.',
    'The {w} was the talk of the whole street.',
  ],
  prep: [
    'The cat was {w} the box all morning.',
    'She left the keys {w} the drawer.',
    'The children played {w} the old barn.',
    'He stood {w} the gate for an hour.',
    'The letters were kept {w} the wooden chest.',
    'A small bird nested {w} the tower.',
    'They waited {w} the station until dark.',
    'The dog slept {w} the shed last night.',
    'Her shoes were {w} the cupboard.',
    'The coins had been hidden {w} the well.',
    'We sat {w} the fire and talked.',
    'The ladder was left {w} the barn.',
    'The village lay {w} the forest.',
    'His workshop was {w} the mill.',
    'The lamp hung {w} the doorway.',
    'The boat stayed {w} the harbour.',
    'Fresh bread was stored {w} the pantry.',
    'The horses stood {w} the fence.',
    'A note was tucked {w} the book.',
    'The old map was kept {w} the cabin.',
    'The tools were stored {w} the shed.',
    'She waited {w} the church for the others.',
    'The lantern was placed {w} the tent.',
    'The chickens stayed {w} the coop.',
  ],
};

export interface ContextInstance {
  readonly text: string;
  /** Character span [start, end) of the substituted word in `text`. */
  readonly charStart: number;
  readonly charEnd: number;
}

export function instantiate(template: string, word: string): ContextInstance {
  const at = template.indexOf('{w}');
  const count = template.split('{w}').length - 1;
  if (at < 0 || count !== 1) throw new Error(`template must contain {w} exactly once: ${template}`);
  return {
    text: template.slice(0, at) + word + template.slice(at + 3),
    charStart: at,
    charEnd: at + word.length,
  };
}

/** Fail closed if any template contains a probe word as an exact token. */
export function checkNoProbeWordLeak(templates: readonly string[], probeWords: readonly string[]): void {
  const probe = new Set(probeWords.map((w) => w.toLowerCase()));
  for (const t of templates) {
    for (const tok of t.toLowerCase().replace('{w}', ' ').split(/[^a-z']+/)) {
      if (probe.has(tok)) throw new Error(`template leaks probe word '${tok}': "${t}"`);
    }
  }
}

function main(): void {
  const corpus = loadCorpus();
  const { probeItems } = buildItems(corpus.map((c) => c.id));
  const probeWords = probeItems.map((p) => p.word);
  for (const bank of Object.values(TEMPLATE_BANKS)) checkNoProbeWordLeak(bank, probeWords);

  const perWord: Record<string, ContextInstance[]> = {};
  for (const p of probeItems) {
    perWord[p.word] = TEMPLATE_BANKS[p.bank].map((t) => instantiate(t, p.word));
  }

  writeInput('contexts.json', {
    date: new Date().toISOString(),
    encoderContentHash: encoderContentHash(),
    corpusPin: corpusPin(),
    design:
      '5 hand-authored banks x 24 templates; every word receives all 24 templates of its bank (deterministic, no sampling); slot {w} substituted verbatim; charStart/charEnd = span of the word; random-pool candidates reuse the same bank templates. Fail-closed: templates contain no probe word (exact-form check).',
    contextsPerWord: 24,
    banks: TEMPLATE_BANKS,
    items: probeItems.map((p) => ({ id: p.id, word: p.word, bank: p.bank })),
    perWord,
  });
}

if (isMain(import.meta.url)) main();
