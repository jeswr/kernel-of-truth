/**
 * E2 item registry (docs/poc-design.md E2: "Item set: explicated concepts
 * only ... item counts and tie policy published").
 *
 * kernel-v0 contains 54 explicated concepts and zero bare primes, so the
 * pre-registered prime-block exclusion removes nothing. Three concepts have
 * multi-word labels with no single surface word to probe (`has-part`,
 * `maker-of`, `part-of`); they are EXCLUDED from the word-probe analysis set
 * (published here and in poc/e2/README.md) but still included in the shipped
 * 54x54 kernel similarity matrices for completeness. Analysis item count: 51.
 *
 * Each probe item carries a hand-authored context bank assignment (the POS /
 * frame class its label word is used in, matching the *explicated sense*):
 *   adjPerson — predicative adjective of a person ("Maria was <w>.")
 *   adjThing  — predicative adjective of a thing  ("The clock was <w>.")
 *   verb      — infinitive / bare-form verb frames ("... wanted to <w> ...")
 *   noun      — definite-NP noun frames ("... the <w> ...")
 *   prep      — locative relation frames ("The cup was <w> the box.")
 * Bank assignments follow the sense named in the concept label (e.g. `lie
 * (the words)` and `promise (the words)` are nouns; `change (the event)` is
 * a noun; `right`/`wrong` "(of a doable something)" are thing-adjectives).
 */

export type Bank = 'adjPerson' | 'adjThing' | 'verb' | 'noun' | 'prep';

/** WordNet POS files accepted for frequency-pool candidates per bank. */
export const BANK_WORDNET_POS: Record<Bank, readonly string[]> = {
  adjPerson: ['adj'],
  adjThing: ['adj'],
  verb: ['verb'],
  noun: ['noun'],
  prep: [], // closed class; WordNet does not index prepositions — see freqPools.ts
};

export interface ProbeItem {
  /** kernel-v0 concept id (urn:kernel-v0:<slug>). */
  readonly id: string;
  /** Single surface word probed in contexts + baselines. */
  readonly word: string;
  readonly bank: Bank;
}

/** slug -> [word, bank] for the 51 analysis items. */
const PROBE: Record<string, [string, Bank]> = {
  afraid: ['afraid', 'adjPerson'],
  alive: ['alive', 'adjPerson'],
  angry: ['angry', 'adjPerson'],
  archived: ['archived', 'adjThing'],
  begin: ['begin', 'verb'],
  believe: ['believe', 'verb'],
  birth: ['birth', 'noun'],
  bookmark: ['bookmark', 'noun'],
  break: ['break', 'verb'],
  broken: ['broken', 'adjThing'],
  cause: ['cause', 'verb'],
  celebration: ['celebration', 'noun'],
  change: ['change', 'noun'], // label: "change (the event)"
  condolence: ['condolence', 'noun'],
  conversation: ['conversation', 'noun'],
  dead: ['dead', 'adjPerson'],
  death: ['death', 'noun'],
  end: ['end', 'verb'], // label: "end (happening X ends at time T)"
  event: ['event', 'noun'],
  find: ['find', 'verb'],
  forget: ['forget', 'verb'],
  friend: ['friend', 'noun'],
  gift: ['gift', 'noun'],
  give: ['give', 'verb'],
  grieving: ['grieving', 'adjPerson'],
  happy: ['happy', 'adjPerson'],
  help: ['help', 'verb'],
  helpful: ['helpful', 'adjPerson'],
  inside: ['inside', 'prep'],
  kind: ['kind', 'noun'], // label: "kind (gufo:Kind, sortal type)" — the noun sense
  learn: ['learn', 'verb'],
  liar: ['liar', 'noun'],
  lie: ['lie', 'noun'], // label: "lie (the words)"
  lose: ['lose', 'verb'],
  lost: ['lost', 'adjThing'],
  make: ['make', 'verb'],
  memory: ['memory', 'noun'],
  near: ['near', 'prep'],
  promise: ['promise', 'noun'], // label: "promise (the words)"
  remember: ['remember', 'verb'],
  reminder: ['reminder', 'noun'],
  repair: ['repair', 'verb'],
  right: ['right', 'adjThing'], // "(of a doable something)"
  sad: ['sad', 'adjPerson'],
  take: ['take', 'verb'],
  teacher: ['teacher', 'noun'],
  thief: ['thief', 'noun'],
  trustworthy: ['trustworthy', 'adjPerson'],
  useful: ['useful', 'adjThing'],
  visible: ['visible', 'adjThing'],
  wrong: ['wrong', 'adjThing'],
};

/** Multi-word labels: no single surface word to probe; excluded from analysis. */
export const EXCLUDED_MULTIWORD: readonly string[] = ['has-part', 'maker-of', 'part-of'];

export function slugOf(id: string): string {
  return id.replace(/^urn:kernel-v0:/, '');
}

/**
 * Build the ordered item lists from the corpus ids (alphabetical by slug —
 * the same order every shipped matrix uses).
 */
export function buildItems(allIds: readonly string[]): {
  allItemIds: string[];
  probeItems: ProbeItem[];
  excludedIds: string[];
} {
  const allItemIds = [...allIds].sort();
  const probeItems: ProbeItem[] = [];
  const excludedIds: string[] = [];
  for (const id of allItemIds) {
    const slug = slugOf(id);
    if (EXCLUDED_MULTIWORD.includes(slug)) {
      excludedIds.push(id);
      continue;
    }
    const p = PROBE[slug];
    if (p === undefined) throw new Error(`E2 item registry has no probe entry for '${id}' — corpus changed?`);
    probeItems.push({ id, word: p[0], bank: p[1] });
  }
  const words = probeItems.map((p) => p.word);
  if (new Set(words).size !== words.length) throw new Error('duplicate probe words');
  return { allItemIds, probeItems, excludedIds };
}
