/**
 * X0 — verification (poc-design.md Phase X):
 *  - golden vectors: a committed fixtures file of explication -> vector
 *    sha-256 digests (concept-hash discipline);
 *  - byte-determinism: re-encode in-process twice and against the fixture,
 *    require byte-identical output;
 *  - the encoder content-hash pin is stored in the fixture and must match.
 *
 * Run `npm run x0:write` ONCE to (re)create fixtures (this is an encoder
 * version change and must be deliberate); `npm run x0` verifies.
 */

import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { join } from 'node:path';
import {
  encodeExplication,
  encodeConceptSet,
  encoderContentHash,
  generateExplication,
  ALGORITHM_VERSION,
  AST_SCHEMA,
  type Explication,
} from '@jeswr/kernel-encoder';
import { FIXTURES_DIR, ensureDirs, hasFlag, vectorSha256, vectorBytes, writeReport } from './common.js';

const FIXTURE_FILE = join(FIXTURES_DIR, 'golden-vectors.json');

interface GoldenEntry {
  name: string;
  ast: Explication;
  sha256: string;
  head8: number[]; // first 8 components, for human diffing
}

interface GoldenFixture {
  encoderContentHash: string;
  algorithmVersion: string;
  D: number;
  entries: GoldenEntry[];
}

/** Hand-authored explication: "someone X wants to see the same thing, and X does not die". */
const HAND_1: Explication = {
  schema: AST_SCHEMA,
  frame: 'InstanceSchema',
  referents: [{ index: 1, refKind: 'SomeoneRef' }],
  clauses: [
    {
      type: 'pred',
      pred: 'WANT',
      roles: {
        experiencer: { kind: 'ref', index: 1 },
        complement: {
          kind: 'clause',
          clause: {
            type: 'pred',
            pred: 'SEE',
            roles: {
              experiencer: { kind: 'ref', index: 1 },
              stimulus: { kind: 'sp', det: 'THE-SAME', head: { kind: 'primeHead', prime: 'SOMETHING~THING' } },
            },
          },
        },
      },
    },
    { type: 'op', op: 'NOT', args: [{ type: 'pred', pred: 'DIE', roles: { undergoer: { kind: 'ref', index: 1 } } }] },
  ],
};

/** Hand-authored: quote + temporal anchor + frame variety. */
const HAND_2: Explication = {
  schema: AST_SCHEMA,
  frame: 'WhenTrue',
  referents: [
    { index: 1, refKind: 'SomethingRef' },
    { index: 2, refKind: 'SomeoneRef' },
  ],
  clauses: [
    {
      type: 'pred',
      pred: 'SAY',
      roles: {
        agent: { kind: 'sp', head: { kind: 'primeHead', prime: 'SOMEONE' }, bind: 2 },
        quote: {
          kind: 'quote',
          clauses: [
            {
              type: 'pred',
              pred: 'FEEL',
              roles: { experiencer: { kind: 'prime', prime: 'I' }, attribute: { kind: 'prime', prime: 'GOOD' } },
            },
          ],
        },
        time: { kind: 'temporal', op: 'BEFORE', anchor: { kind: 'prime', prime: 'NOW' } },
      },
    },
    {
      type: 'pred',
      pred: 'BE-SPEC',
      roles: {
        undergoer: { kind: 'ref', index: 1 },
        attribute: {
          kind: 'sp',
          quant: 'ONE',
          head: { kind: 'kindFrame', of: { kind: 'sp', head: { kind: 'primeHead', prime: 'SOMETHING~THING' } } },
        },
      },
    },
  ],
};

/** Concept-reference case: mid references leaf; both go in the fixture. */
const LEAF: Explication = {
  schema: AST_SCHEMA,
  frame: 'InstanceSchema',
  referents: [{ index: 1, refKind: 'SomethingRef' }],
  clauses: [
    { type: 'pred', pred: 'THERE-IS', roles: { undergoer: { kind: 'ref', index: 1 } } },
    {
      type: 'pred',
      pred: 'BE-SPEC',
      roles: {
        undergoer: { kind: 'ref', index: 1 },
        attribute: { kind: 'sp', mods: [{ mod: 'BIG', intensifier: 'VERY' }], head: { kind: 'primeHead', prime: 'SOMETHING~THING' } },
      },
    },
  ],
};
const MID: Explication = {
  schema: AST_SCHEMA,
  frame: 'InstanceSchema',
  referents: [{ index: 1, refKind: 'SomeoneRef' }],
  clauses: [
    {
      type: 'pred',
      pred: 'KNOW',
      roles: { experiencer: { kind: 'ref', index: 1 }, topic: { kind: 'concept', id: 'urn:concept:x0-leaf' } },
    },
  ],
};

function buildEntries(): GoldenEntry[] {
  const entries: GoldenEntry[] = [];
  const push = (name: string, ast: Explication, v: Float64Array): void => {
    entries.push({ name, ast, sha256: vectorSha256(v), head8: [...v.slice(0, 8)] });
  };
  push('hand-1-want-see-not-die', HAND_1, encodeExplication(HAND_1));
  push('hand-2-say-quote-temporal', HAND_2, encodeExplication(HAND_2));
  const { vectors } = encodeConceptSet(
    new Map([
      ['urn:concept:x0-leaf', LEAF],
      ['urn:concept:x0-mid', MID],
    ]),
  );
  entries.push({ name: 'concept-x0-leaf', ast: LEAF, sha256: vectorSha256(vectors.get('urn:concept:x0-leaf')!), head8: [...vectors.get('urn:concept:x0-leaf')!.slice(0, 8)] });
  entries.push({ name: 'concept-x0-mid', ast: MID, sha256: vectorSha256(vectors.get('urn:concept:x0-mid')!), head8: [...vectors.get('urn:concept:x0-mid')!.slice(0, 8)] });
  // Synthetic sweep across depth/clause shapes.
  for (const [tc, dep] of [
    [1, 1], [2, 2], [4, 3], [8, 4], [16, 2], [32, 1], [3, 6],
  ] as const) {
    const ast = generateExplication({ seed: `x0/golden/${tc}/${dep}`, topClauses: tc, depth: dep });
    push(`synth-c${tc}-d${dep}`, ast, encodeExplication(ast));
  }
  return entries;
}

function main(): void {
  ensureDirs();
  const contentHash = encoderContentHash();
  if (hasFlag('--write')) {
    const fixture: GoldenFixture = {
      encoderContentHash: contentHash,
      algorithmVersion: ALGORITHM_VERSION,
      D: 8192,
      entries: buildEntries(),
    };
    writeFileSync(FIXTURE_FILE, JSON.stringify(fixture, null, 2));
    console.log(`wrote ${FIXTURE_FILE} (${fixture.entries.length} golden vectors)`);
    console.log(`encoder content-hash: ${contentHash}`);
    return;
  }
  if (!existsSync(FIXTURE_FILE)) {
    console.error('X0 FAIL: no golden fixture; run `npm run x0:write` once and commit the file.');
    process.exit(1);
  }
  const fixture = JSON.parse(readFileSync(FIXTURE_FILE, 'utf8')) as GoldenFixture;
  const failures: string[] = [];
  if (fixture.encoderContentHash !== contentHash) {
    failures.push(`content-hash mismatch: fixture ${fixture.encoderContentHash}, current ${contentHash}`);
  }
  // Re-encode everything and compare bytes; also encode twice for in-process determinism.
  const concepts = encodeConceptSet(
    new Map(
      fixture.entries
        .filter((e) => e.name.startsWith('concept-'))
        .map((e) => [`urn:concept:${e.name.replace('concept-', '')}`, e.ast]),
    ),
  ).vectors;
  for (const entry of fixture.entries) {
    let v: Float64Array;
    if (entry.name.startsWith('concept-')) {
      v = concepts.get(`urn:concept:${entry.name.replace('concept-', '')}`)!;
    } else {
      v = encodeExplication(entry.ast, { concepts });
      const v2 = encodeExplication(entry.ast, { concepts });
      if (!vectorBytes(v).equals(vectorBytes(v2))) {
        failures.push(`${entry.name}: two in-process encodes differ byte-wise`);
      }
    }
    const sha = vectorSha256(v);
    if (sha !== entry.sha256) failures.push(`${entry.name}: sha256 ${sha} != golden ${entry.sha256}`);
  }
  const pass = failures.length === 0;
  const md = [
    '# X0 — golden vectors / byte-determinism',
    '',
    `date: ${new Date().toISOString()}`,
    `encoder content-hash: \`${contentHash}\``,
    `algorithm: ${fixture.algorithmVersion}, D=${fixture.D}`,
    `golden vectors: ${fixture.entries.length}`,
    '',
    pass ? '**PASS** — all vectors byte-identical to the committed goldens.' : '**FAIL**',
    ...failures.map((f) => `- ${f}`),
    '',
    'Note: cross-PLATFORM determinism is asserted by re-running this harness on',
    'other machines against the same committed fixture (the fixture is the',
    'cross-platform witness); this run only proves cross-run determinism here.',
  ].join('\n');
  writeReport('x0-report', { pass, contentHash, failures, n: fixture.entries.length }, md);
  console.log(pass ? `X0 PASS (${fixture.entries.length} golden vectors)` : `X0 FAIL:\n${failures.join('\n')}`);
  process.exit(pass ? 0 : 1);
}

main();
