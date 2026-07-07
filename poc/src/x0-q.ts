/**
 * X0-q — golden vectors / byte-determinism for the toy-native variant
 * kot-enc-Bq/1 at D ∈ {512, 576} (bead kernel-of-truth-5xo).
 *
 * Pre-registered bar RESTATED for the variant (same as poc-design X0):
 * byte-determinism across runs/platforms, golden vectors under concept-hash
 * discipline — but in a SEPARATE fixture file (fixtures/golden-vectors-q.json)
 * keyed by the variant's own per-D content-hashes; the kot-enc-B/1 D=8192
 * fixture is untouched. Same test shapes as harness/x0.ts (two hand-authored
 * explications, a concept-reference pair, seven synthetic shapes), duplicated
 * here because importing harness/x0.ts would execute its main().
 *
 * `npm run x0:q:write` (re)creates the fixture — a deliberate encoder-version
 * act; `npm run x0:q` verifies and exits nonzero on any mismatch.
 */

import { mkdirSync, readFileSync, writeFileSync, existsSync } from 'node:fs';
import { join } from 'node:path';
import {
  encodeExplicationQ,
  encodeConceptSetQ,
  encoderContentHashQ,
  generateExplication,
  ALGORITHM_VERSION_Q,
  QUASI_DIMS,
  AST_SCHEMA,
  type Explication,
} from '@jeswr/kernel-encoder';
import { hasFlag, vectorSha256, vectorBytes } from '../harness/common.js';
import { POC_DIR, writeCorpusReport } from './corpus-common.js';

// NOT harness/common.js's FIXTURES_DIR: that resolves relative to the
// compiled dist-corpus/ tree (see corpus-common.ts note); anchor at poc/.
const FIXTURES_DIR = join(POC_DIR, 'fixtures');
const FIXTURE_FILE = join(FIXTURES_DIR, 'golden-vectors-q.json');

interface GoldenEntry {
  name: string;
  ast: Explication;
  sha256: string;
  head8: number[];
}

interface DimGoldens {
  D: number;
  encoderContentHash: string;
  entries: GoldenEntry[];
}

interface GoldenFixtureQ {
  algorithmVersion: string;
  dims: DimGoldens[];
}

/** Hand-authored explication: "someone X wants to see the same thing, and X does not die". (= harness/x0.ts HAND_1) */
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

/** Hand-authored: quote + temporal anchor + frame variety. (= harness/x0.ts HAND_2) */
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

/** Concept-reference case (= harness/x0.ts LEAF/MID). */
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

function buildEntries(D: number): GoldenEntry[] {
  const entries: GoldenEntry[] = [];
  const push = (name: string, ast: Explication, v: Float64Array): void => {
    entries.push({ name, ast, sha256: vectorSha256(v), head8: [...v.slice(0, 8)] });
  };
  push('hand-1-want-see-not-die', HAND_1, encodeExplicationQ(HAND_1, { params: { D } }));
  push('hand-2-say-quote-temporal', HAND_2, encodeExplicationQ(HAND_2, { params: { D } }));
  const { vectors } = encodeConceptSetQ(
    new Map([
      ['urn:concept:x0-leaf', LEAF],
      ['urn:concept:x0-mid', MID],
    ]),
    { params: { D } },
  );
  entries.push({ name: 'concept-x0-leaf', ast: LEAF, sha256: vectorSha256(vectors.get('urn:concept:x0-leaf')!), head8: [...vectors.get('urn:concept:x0-leaf')!.slice(0, 8)] });
  entries.push({ name: 'concept-x0-mid', ast: MID, sha256: vectorSha256(vectors.get('urn:concept:x0-mid')!), head8: [...vectors.get('urn:concept:x0-mid')!.slice(0, 8)] });
  for (const [tc, dep] of [
    [1, 1], [2, 2], [4, 3], [8, 4], [16, 2], [32, 1], [3, 6],
  ] as const) {
    const ast = generateExplication({ seed: `x0/golden/${tc}/${dep}`, topClauses: tc, depth: dep });
    push(`synth-c${tc}-d${dep}`, ast, encodeExplicationQ(ast, { params: { D } }));
  }
  return entries;
}

function main(): void {
  mkdirSync(FIXTURES_DIR, { recursive: true });
  if (hasFlag('--write')) {
    const fixture: GoldenFixtureQ = {
      algorithmVersion: ALGORITHM_VERSION_Q,
      dims: QUASI_DIMS.map((D) => ({
        D,
        encoderContentHash: encoderContentHashQ({ D }),
        entries: buildEntries(D),
      })),
    };
    writeFileSync(FIXTURE_FILE, JSON.stringify(fixture, null, 2));
    console.log(`wrote ${FIXTURE_FILE} (${fixture.dims.map((d) => `${d.entries.length}@${d.D}`).join(', ')} golden vectors)`);
    for (const d of fixture.dims) console.log(`encoder content-hash @ D=${d.D}: ${d.encoderContentHash}`);
    return;
  }
  if (!existsSync(FIXTURE_FILE)) {
    console.error('X0-q FAIL: no golden fixture; run `npm run x0:q:write` once and commit the file.');
    process.exit(1);
  }
  const fixture = JSON.parse(readFileSync(FIXTURE_FILE, 'utf8')) as GoldenFixtureQ;
  const failures: string[] = [];
  if (fixture.algorithmVersion !== ALGORITHM_VERSION_Q) {
    failures.push(`algorithm-version mismatch: fixture ${fixture.algorithmVersion}, current ${ALGORITHM_VERSION_Q}`);
  }
  for (const dim of fixture.dims) {
    const D = dim.D;
    const contentHash = encoderContentHashQ({ D });
    if (dim.encoderContentHash !== contentHash) {
      failures.push(`D=${D}: content-hash mismatch: fixture ${dim.encoderContentHash}, current ${contentHash}`);
    }
    const concepts = encodeConceptSetQ(
      new Map(
        dim.entries
          .filter((e) => e.name.startsWith('concept-'))
          .map((e) => [`urn:concept:${e.name.replace('concept-', '')}`, e.ast]),
      ),
      { params: { D } },
    ).vectors;
    for (const entry of dim.entries) {
      let v: Float64Array;
      if (entry.name.startsWith('concept-')) {
        v = concepts.get(`urn:concept:${entry.name.replace('concept-', '')}`)!;
      } else {
        v = encodeExplicationQ(entry.ast, { params: { D }, concepts });
        const v2 = encodeExplicationQ(entry.ast, { params: { D }, concepts });
        if (!vectorBytes(v).equals(vectorBytes(v2))) {
          failures.push(`D=${D} ${entry.name}: two in-process encodes differ byte-wise`);
        }
      }
      const sha = vectorSha256(v);
      if (sha !== entry.sha256) failures.push(`D=${D} ${entry.name}: sha256 ${sha} != golden ${entry.sha256}`);
    }
  }
  const pass = failures.length === 0;
  const md = [
    '# X0-q — golden vectors / byte-determinism (toy-native variant kot-enc-Bq/1)',
    '',
    `date: ${new Date().toISOString()}`,
    `algorithm: ${ALGORITHM_VERSION_Q}, D ∈ {${fixture.dims.map((d) => d.D).join(', ')}}`,
    ...fixture.dims.map((d) => `encoder content-hash @ D=${d.D}: \`${d.encoderContentHash}\``),
    `golden vectors: ${fixture.dims.map((d) => `${d.entries.length}@${d.D}`).join(', ')}`,
    '',
    pass ? '**PASS** — all vectors byte-identical to the committed goldens.' : '**FAIL**',
    ...failures.map((f) => `- ${f}`),
    '',
    'Note: cross-PLATFORM determinism is asserted by re-running this harness on',
    'other machines against the same committed fixture. D=576 exercises the',
    'Bluestein chirp-z FFT path (Math.cos/Math.sin caveat, fft.ts), which is',
    'exactly what these goldens witness operationally.',
  ].join('\n');
  writeCorpusReport('x0-q-report', {
    pass,
    algorithmVersion: ALGORITHM_VERSION_Q,
    contentHashes: Object.fromEntries(fixture.dims.map((d) => [d.D, d.encoderContentHash])),
    failures,
    n: fixture.dims.reduce((s, d) => s + d.entries.length, 0),
  }, md);
  console.log(pass ? 'X0-q PASS' : `X0-q FAIL:\n${failures.join('\n')}`);
  process.exit(pass ? 0 : 1);
}

main();
