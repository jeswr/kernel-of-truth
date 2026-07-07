/**
 * Small rule-based English lemmatizer. Zero dependencies, no dictionary.
 *
 * Because suffix-stripping without a dictionary is genuinely ambiguous
 * ("making" -> mak/make; "running" -> runn/run), the lemmatizer returns a
 * deterministic ORDERED CANDIDATE LIST rather than pretending to know the
 * answer. The mapper checks every candidate against the lexicon and applies
 * the abstain-on->1-target policy; corpus statistics (M0b) resolve
 * candidates by corpus attestation.
 *
 * Coverage: plural/3sg -s/-es, -ies; past -ed/-ied; progressive -ing (with
 * consonant-undoubling and e-restoration candidates); comparative -er /
 * superlative -est (candidates only — agentive -er nouns like "teacher" stay
 * intact because the unsuffixed form is just a lower-priority candidate);
 * irregular verb/noun/adjective tables for common child-register English.
 *
 * Deliberate omissions (documented): "lay" is NOT folded to "lie" (would
 * collide recline-lie with the kernel concept lie-the-words); "people" is
 * NOT folded to "person" (PEOPLE is the prime exponent); derivational
 * morphology (-ness, -ful, -ly) is out of scope for v0.
 */

/** Irregular form -> base. Verbs (past/participle/3sg oddities), nouns, adjectives. */
const IRREGULAR: ReadonlyMap<string, string> = new Map(Object.entries({
  // be/have/do/modals
  is: 'be', are: 'be', am: 'be', was: 'be', were: 'be', been: 'be', being: 'be',
  has: 'have', had: 'have', having: 'have',
  does: 'do', did: 'do', done: 'do',
  could: 'can', might: 'may', would: 'will', should: 'shall',
  // common irregular verbs (child-register heavy)
  said: 'say', saw: 'see', seen: 'see', went: 'go', gone: 'go',
  got: 'get', gotten: 'get', came: 'come', ran: 'run', sat: 'sit',
  stood: 'stand', held: 'hold', kept: 'keep', slept: 'sleep', left: 'leave',
  met: 'meet', fell: 'fall', fallen: 'fall', flew: 'fly', flown: 'fly',
  ate: 'eat', eaten: 'eat', drank: 'drink', drunk: 'drink',
  sang: 'sing', sung: 'sing', swam: 'swim', swum: 'swim',
  began: 'begin', begun: 'begin', brought: 'bring', bought: 'buy',
  caught: 'catch', taught: 'teach', fought: 'fight', thought: 'think',
  felt: 'feel', heard: 'hear', told: 'tell', knew: 'know', known: 'know',
  took: 'take', taken: 'take', gave: 'give', given: 'give',
  found: 'find', lost: 'lose', made: 'make', broke: 'break', broken: 'break',
  spoke: 'speak', spoken: 'speak', wore: 'wear', worn: 'wear',
  grew: 'grow', grown: 'grow', threw: 'throw', thrown: 'throw',
  blew: 'blow', blown: 'blow', drew: 'draw', drawn: 'draw',
  hid: 'hide', hidden: 'hide', bit: 'bite', bitten: 'bite',
  lit: 'light', meant: 'mean', paid: 'pay', sent: 'send', spent: 'spend',
  built: 'build', lent: 'lend', bent: 'bend',
  understood: 'understand', became: 'become', forgot: 'forget',
  forgotten: 'forget', woke: 'wake', woken: 'wake', rode: 'ride',
  ridden: 'ride', wrote: 'write', written: 'write', dug: 'dig',
  hung: 'hang', shone: 'shine', sold: 'sell', shook: 'shake',
  shaken: 'shake', stuck: 'stick', swept: 'sweep', wept: 'weep',
  died: 'die', dying: 'die', lied: 'lie', lying: 'lie',
  tied: 'tie', tying: 'tie',
  // irregular plurals
  children: 'child', men: 'man', women: 'woman', feet: 'foot',
  teeth: 'tooth', mice: 'mouse', geese: 'goose', leaves: 'leaf',
  wolves: 'wolf', lives: 'life', knives: 'knife', shelves: 'shelf',
  // irregular comparatives
  better: 'good', best: 'good', worse: 'bad', worst: 'bad',
  bigger: 'big', biggest: 'big', littler: 'little', littlest: 'little',
  sadder: 'sad', saddest: 'sad', happier: 'happy', happiest: 'happy',
  angrier: 'angry', angriest: 'angry',
}));

/** Table-driven irregular base for a form, or undefined (exported for M0b vocab folding). */
export function irregularBase(word: string): string | undefined {
  return IRREGULAR.get(word);
}

/** Words that look inflected but are base forms — never strip. */
const NO_STRIP = new Set([
  'this', 'his', 'hers', 'its', 'is', 'was', 'has', 'does', 'yes', 'us',
  'thus', 'gas', 'bus', 'plus', 'always', 'perhaps', 'news', 'once',
  'during', 'thing', 'something', 'nothing', 'anything', 'everything',
  'king', 'ring', 'sing', 'wing', 'spring', 'string', 'bring', 'morning',
  'evening', 'ceiling', 'sibling', 'darling', 'duckling', 'young',
  'red', 'bed', 'sad', 'bad', 'dad', 'mad', 'glad', 'need', 'seed',
  'feed', 'speed', 'indeed', 'shed', 'sled', 'wed', 'bread', 'head',
  'friend', 'end', 'and', 'said', 'kid', 'did', 'god', 'good', 'food',
  'wood', 'hundred', 'old', 'cold', 'hold', 'bold', 'gold', 'told',
  'world', 'word', 'bird', 'weird', 'hard', 'yard', 'card', 'board',
  'toward', 'forward', 'backward', 'wizard', 'lizard', 'afraid',
  'her', 'never', 'ever', 'over', 'under', 'after', 'other', 'mother',
  'father', 'brother', 'sister', 'water', 'paper', 'super', 'later',
  'butter', 'letter', 'better', 'dinner', 'summer', 'winter', 'silver',
  'together', 'weather', 'flower', 'tower', 'power', 'river', 'tiger',
  'monster', 'hamster', 'spider', 'ladder', 'corner', 'wonder', 'remember',
  'number', 'answer', 'clever', 'either', 'neither', 'whether', 'per',
  'nest', 'best', 'rest', 'test', 'chest', 'west', 'east', 'forest',
  'interest', 'honest', 'fastest', 'must', 'just', 'first', 'last',
  'most', 'lost', 'past', 'cost', 'against', 'burst', 'trust', 'dust',
]);

const VOWELS = new Set(['a', 'e', 'i', 'o', 'u']);

function isConsonant(ch: string): boolean {
  return ch.length === 1 && ch >= 'a' && ch <= 'z' && !VOWELS.has(ch);
}

/**
 * Candidates after stripping a verbal/comparative suffix, in priority order:
 * 1. bare stem            (walk-ed, jump-ing, tall-er)
 * 2. stem + e             (mak-ing -> make, lik-ed -> like)
 * 3. undoubled stem       (runn-ing -> run, patt-ed -> pat) — never undouble
 *    ll/ss/ff/zz (telling -> tell, missing -> miss).
 */
function stemCandidates(stem: string): string[] {
  const out: string[] = [];
  if (stem.length >= 2) out.push(stem);
  const last = stem[stem.length - 1] ?? '';
  const prev = stem[stem.length - 2] ?? '';
  if (isConsonant(last) && stem.length >= 2) out.push(`${stem}e`);
  if (
    stem.length >= 3 &&
    last === prev &&
    isConsonant(last) &&
    !['l', 's', 'f', 'z'].includes(last)
  ) {
    out.push(stem.slice(0, -1));
  }
  return out;
}

/**
 * Deterministic ordered lemma candidates for a lowercased word token.
 * The surface form itself is always the FIRST candidate (surface-exact
 * lexicon entries take part in exactly the same ambiguity accounting).
 */
export function lemmaCandidates(word: string): string[] {
  const out: string[] = [word];
  const push = (w: string): void => {
    if (w.length >= 2 && !out.includes(w)) out.push(w);
  };

  const irr = IRREGULAR.get(word);
  if (irr !== undefined) push(irr);

  if (NO_STRIP.has(word) || word.length < 3) return out;

  // plural / 3sg -s, -es, -ies
  if (word.endsWith('ies') && word.length > 4) push(`${word.slice(0, -3)}y`);
  else if (word.endsWith('es') && /(?:s|x|z|ch|sh|o)es$/.test(word)) {
    push(word.slice(0, -2));
    push(word.slice(0, -1)); // horses -> horse
  } else if (word.endsWith('s') && !word.endsWith('ss') && !word.endsWith('us')) {
    push(word.slice(0, -1));
  }

  // past -ed, -ied
  if (word.endsWith('ied') && word.length > 4) push(`${word.slice(0, -3)}y`);
  else if (word.endsWith('ed') && word.length > 3) {
    for (const c of stemCandidates(word.slice(0, -2))) push(c);
  }

  // progressive -ing
  if (word.endsWith('ing') && word.length > 4) {
    for (const c of stemCandidates(word.slice(0, -3))) push(c);
  }

  // comparative -er / superlative -est (candidates only; agentive -er nouns
  // simply keep their surface form as candidate #1)
  if (word.endsWith('iest') && word.length > 5) push(`${word.slice(0, -4)}y`);
  else if (word.endsWith('est') && word.length > 4) {
    for (const c of stemCandidates(word.slice(0, -3))) push(c);
  }
  if (word.endsWith('ier') && word.length > 4) push(`${word.slice(0, -3)}y`);
  else if (word.endsWith('er') && word.length > 3) {
    for (const c of stemCandidates(word.slice(0, -2))) push(c);
  }

  return out;
}
