/**
 * E1 mapper-lexicon artifact (docs/poc-design.md E1; bead kernel-of-truth-bk0).
 *
 * The E1 data pipeline runs in python on the GPU box; the mapper is
 * TypeScript. This generator compiles everything the python port
 * (poc/e1/pipeline/kernel_mapper.py) needs into ONE committed JSON artifact:
 *
 *   - the deterministic lexicon (concept labels + prime exponents), taken
 *     LIVE from @jeswr/kernel-mapper's exported buildLexicon() — never
 *     transcribed;
 *   - the lemmatizer tables (IRREGULAR, NO_STRIP) and tokenizer tables
 *     (SPECIAL contractions, PRONOUN_S_IS). These are module-private in
 *     mapper/src, so they are TRANSCRIBED here — and then every entry is
 *     VERIFIED behaviourally against the exported mapper functions
 *     (irregularBase, lemmaCandidates, tokenize). Any mismatch throws:
 *     if the mapper changes, this generator fails closed instead of
 *     shipping a stale port.
 *
 * With a corpus path argument it additionally emits a PARITY fixture:
 * the sha-256 of the mapper's canonical decision stream over the whole
 * slice, per-norm lemma-candidate lists for every distinct word norm in the
 * slice, and inline annotations for the first stories. The python port must
 * reproduce the stream hash bit-for-bit before any shard it produces is
 * trusted (fail-closed gate in build_data.py).
 *
 * AMENDMENT A1 (docs/poc-design.md Phase M, coordinator-signed 2026-07-07;
 * bead kernel-of-truth-9qm): every E1 data build runs the mapper under the
 * `a1-hybrid` policy preset (sense-priority tiers for {inside, near, broken},
 * evaluated-set exclusion for {kind, lost}; policy sha e13dc838…). This
 * generator therefore (i) embeds the full policy declaration in the lexicon
 * artifact so the python port can apply the tiers bit-exactly, (ii) annotates
 * the parity fixture UNDER the policy, and (iii) stamps preset name + policy
 * sha into both artifacts. The preset hash is verified against the
 * amendment's pin at generation time (fail closed in policyPreset()).
 *
 * Provenance stamped: mapper package version + sha-256 of the six mapper
 * source files (incl. policy.ts), kernel-v0 corpus pin, corpus-file sha-256.
 */

import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import {
  A1_PRESET_NAME,
  buildLexicon,
  irregularBase,
  lemmaCandidates,
  loadManifestConcepts,
  mapText,
  policyHash,
  policyPreset,
  targetKey,
  tokenize,
} from '@jeswr/kernel-mapper';
import type { AnnotatedToken } from '@jeswr/kernel-mapper';
import { createHash } from 'node:crypto';
import { KERNEL_V0_DIR, corpusPin, isMain, mapperPin, sha256Hex, writeInput } from './common.js';

// ---------------------------------------------------------------------------
// Transcribed tables (from mapper/src/lemmatize.ts and tokenize.ts,
// mapper v0.1.0). VERIFIED below against exported behaviour — do not edit
// without re-running `npm run lexicon`, which fail-closes on drift.
// ---------------------------------------------------------------------------

const IRREGULAR: Record<string, string> = {
  is: 'be', are: 'be', am: 'be', was: 'be', were: 'be', been: 'be', being: 'be',
  has: 'have', had: 'have', having: 'have',
  does: 'do', did: 'do', done: 'do',
  could: 'can', might: 'may', would: 'will', should: 'shall',
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
  children: 'child', men: 'man', women: 'woman', feet: 'foot',
  teeth: 'tooth', mice: 'mouse', geese: 'goose', leaves: 'leaf',
  wolves: 'wolf', lives: 'life', knives: 'knife', shelves: 'shelf',
  better: 'good', best: 'good', worse: 'bad', worst: 'bad',
  bigger: 'big', biggest: 'big', littler: 'little', littlest: 'little',
  sadder: 'sad', saddest: 'sad', happier: 'happy', happiest: 'happy',
  angrier: 'angry', angriest: 'angry',
};

const NO_STRIP: string[] = [
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
];

const SPECIAL: Record<string, string[]> = {
  "won't": ['will', 'not'],
  "can't": ['can', 'not'],
  cannot: ['can', 'not'],
  "shan't": ['shall', 'not'],
  "ain't": ['is', 'not'],
  "let's": ['let', 'us'],
  "o'clock": ['oclock'],
};

const PRONOUN_S_IS: string[] = [
  'it', 'that', 'he', 'she', 'there', 'what', 'who', 'where', 'here', 'this',
];

// ---------------------------------------------------------------------------
// Behavioural verification (fail closed on any mapper drift)
// ---------------------------------------------------------------------------

function fail(msg: string): never {
  throw new Error(`ERR_MAPPER_DRIFT: ${msg} — mapper changed; regenerate the transcribed tables`);
}

function verifyTables(): void {
  // IRREGULAR: every transcribed pair must match irregularBase.
  for (const [k, v] of Object.entries(IRREGULAR)) {
    if (irregularBase(k) !== v) fail(`irregular['${k}'] = '${v}' vs irregularBase = '${irregularBase(k)}'`);
  }
  // NO_STRIP: candidates must be exactly [word] + (irregular base if any) —
  // i.e. no suffix-stripped candidates appear.
  for (const w of NO_STRIP) {
    const expected = [w];
    const irr = irregularBase(w);
    if (irr !== undefined && irr.length >= 2 && !expected.includes(irr)) expected.push(irr);
    const got = lemmaCandidates(w);
    if (JSON.stringify(got) !== JSON.stringify(expected)) {
      fail(`noStrip '${w}': lemmaCandidates = [${got}] expected [${expected}]`);
    }
  }
  // Tokenizer SPECIAL + pronoun-'s expansions, checked through tokenize().
  for (const [w, parts] of Object.entries(SPECIAL)) {
    const norms = tokenize(w).filter((t) => t.isWord).map((t) => t.norm);
    if (JSON.stringify(norms) !== JSON.stringify(parts)) {
      fail(`special '${w}' -> [${norms}] expected [${parts}]`);
    }
  }
  for (const p of PRONOUN_S_IS) {
    const norms = tokenize(`${p}'s`).filter((t) => t.isWord).map((t) => t.norm);
    if (JSON.stringify(norms) !== JSON.stringify([p, 'is'])) {
      fail(`pronoun-'s '${p}'s' -> [${norms}] expected [${p}, is]`);
    }
  }
  // Generic contraction rules + possessive drop, spot-checked behaviourally.
  const cases: [string, string[]][] = [
    ["didn't", ['did', 'not']], // norm-level expansion only (lemma 'do' comes later)
    ["she'll", ['she', 'will']],
    ["they're", ['they', 'are']],
    ["we've", ['we', 'have']],
    ["i'm", ['i', 'am']],
    ["he'd", ['he', 'would']],
    ["tom's", ['tom']], // common-noun possessive: clitic dropped
    ["dogs'", ['dogs']],
  ];
  for (const [w, parts] of cases) {
    const norms = tokenize(w).filter((t) => t.isWord).map((t) => t.norm);
    if (JSON.stringify(norms) !== JSON.stringify(parts)) {
      fail(`contraction '${w}' -> [${norms}] expected [${parts}]`);
    }
  }
}

/**
 * Corpus-wide completeness check: for EVERY distinct word norm in the slice,
 * the transcribed-irregular lookup must agree with the live irregularBase.
 * (Catches irregular-table entries added to the mapper after transcription.)
 */
function verifyIrregularOverCorpus(norms: Iterable<string>): void {
  for (const w of norms) {
    const live = irregularBase(w);
    const ours = IRREGULAR[w];
    if (live !== ours) fail(`irregularBase('${w}') = '${live}' but transcription has '${ours}'`);
  }
}

// ---------------------------------------------------------------------------
// Canonical decision stream (the TS<->python parity contract)
// ---------------------------------------------------------------------------

/** One line per WORD token: norm|kind|target|phraseLen|phrasePos (see kernel_mapper.py). */
export function decisionLine(t: AnnotatedToken): string {
  const d = t.decision;
  const target =
    d.kind === 'concept' ? d.conceptId
    : d.kind === 'prime' ? `prime:${d.prime}`
    : d.kind === 'abstain' ? d.candidates.map(targetKey).sort().join(',')
    : '';
  return `${t.norm}|${d.kind}|${target}|${t.phraseLen}|${t.phrasePos}`;
}

function main(): void {
  verifyTables();

  // Amendment A1 policy: resolved by preset name; policyPreset() fails closed
  // if the declaration no longer hashes to the amendment's pinned sha.
  const policy = policyPreset(A1_PRESET_NAME);
  const policySha = policyHash(policy);
  const policyBlock = {
    preset: A1_PRESET_NAME,
    name: policy.name,
    sha256: policySha,
    amendment:
      'Amendment A1 (docs/poc-design.md Phase M, coordinator-signed 2026-07-07): ' +
      'sense-priority tiers for {inside, near, broken}; {kind, lost} excluded from ' +
      "E1's evaluated concept set (52 evaluated); mapper decisions for excluded " +
      'concepts are UNCHANGED (they stay abstained)',
    priorityTiers: (policy.priorityTiers ?? []).map((r) => ({
      decisionSet: [...r.decisionSet].sort(),
      winner: r.winner,
      evidence: r.evidence,
    })),
    excludeConcepts: [...(policy.excludeConcepts ?? [])].sort(),
  };

  const lexicon = buildLexicon(loadManifestConcepts(join(KERNEL_V0_DIR, 'manifest.json')));
  const artifact = {
    artifact: 'e1-mapper-lexicon',
    date: new Date().toISOString(),
    provenance: {
      mapper: mapperPin(),
      kernelV0: corpusPin(),
      note:
        'lexicon entries exported live from @jeswr/kernel-mapper buildLexicon(); ' +
        'lemmatizer/tokenizer tables transcribed from mapper/src and verified ' +
        'behaviourally against exported functions at generation time (fail-closed)',
    },
    policy: policyBlock,
    decisionStreamFormat:
      "per WORD token: 'norm|kind|target|phraseLen|phrasePos'; kind in " +
      "{concept,prime,abstain,none}; target = conceptId | 'prime:'+name | " +
      "sorted abstain candidate keys joined by ',' | ''; lines joined by \\n; " +
      "stories separated by a '#<storyIndex>' line; sha-256 over the utf-8 bytes; " +
      'decisions taken under the embedded `policy` (Amendment A1)',
    entries: lexicon.entries.map((e) => ({
      phrase: e.phrase,
      target: e.target,
      source: e.source,
    })),
    lemmatizer: { irregular: IRREGULAR, noStrip: NO_STRIP },
    tokenizer: { special: SPECIAL, pronounSIs: PRONOUN_S_IS },
  };
  writeInput('mapper-lexicon.json', artifact);

  // ---- optional parity fixture over a corpus slice ----
  const corpusPath = process.argv[2];
  if (corpusPath === undefined) {
    console.log('no corpus path given — parity fixture NOT regenerated');
    return;
  }
  const raw = readFileSync(corpusPath, 'utf8');
  const stories = raw.split('<|endoftext|>').map((s) => s.trim()).filter((s) => s.length > 0);
  const hash = createHash('sha256');
  const norms = new Set<string>();
  const counts = {
    stories: stories.length,
    wordTokens: 0,
    concept: 0,
    prime: 0,
    abstain: 0,
    none: 0,
    tierResolved: 0,
  };
  const tierResolutions: Record<string, number> = {};
  const sampleAnnotations: string[][] = [];
  for (let s = 0; s < stories.length; s++) {
    hash.update(`#${s}\n`);
    // Amendment A1: the canonical stream is the POLICY-annotated stream.
    const anns = mapText(stories[s]!, lexicon, policy);
    const lines: string[] = [];
    for (const t of anns) {
      if (!t.isWord) continue;
      counts.wordTokens += 1;
      counts[t.decision.kind] += 1;
      const d = t.decision;
      if ((d.kind === 'concept' || d.kind === 'prime') && d.resolvedFrom !== undefined) {
        counts.tierResolved += 1;
        const key = d.resolvedFrom.map(targetKey).sort().join('|');
        tierResolutions[key] = (tierResolutions[key] ?? 0) + 1;
      }
      norms.add(t.norm);
      lines.push(decisionLine(t));
    }
    const block = lines.join('\n') + '\n';
    hash.update(block);
    if (s < 25) sampleAnnotations.push(lines);
  }
  verifyIrregularOverCorpus(norms);

  const lemmaTable: Record<string, string[]> = {};
  for (const w of [...norms].sort()) lemmaTable[w] = lemmaCandidates(w);

  writeInput('mapper-parity-fixture.json', {
    artifact: 'e1-mapper-parity-fixture',
    date: new Date().toISOString(),
    corpus: {
      note: 'roneneldan/TinyStories TinyStories-valid.txt (HuggingFace) — the M0a slice',
      bytes: raw.length,
      sha256: sha256Hex(raw),
      stories: counts.stories,
    },
    provenance: { mapper: mapperPin(), kernelV0: corpusPin() },
    policy: { preset: A1_PRESET_NAME, name: policy.name, sha256: policySha },
    counts,
    tierResolutions,
    decisionStreamSha256: hash.digest('hex'),
    sampleAnnotations,
    lemmaTable,
  });
}

if (isMain(import.meta.url)) main();
