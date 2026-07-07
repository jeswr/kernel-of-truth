/**
 * E9-defl vector table (poc/e9/README.md; bead kernel-of-truth-xj2): the 524
 * scrambled explications through the SAME pinned pipeline as poc/e5 —
 * kot-enc-B/1 @ D=8192 (fail-closed hash gate) -> verbatim X4 JL 8192->576
 * -> unit-norm rows -> inputs/vectors/defl-jl576.f32 + manifest. Row order =
 * the E5 ids list (identical to the true kernel table), so the E5 items'
 * `row` indices address the deflationary table unchanged.
 */

import { DEFAULT_PARAMS, encodeConceptSet, encoderContentHash } from '@jeswr/kernel-encoder';
import type { Explication } from '@jeswr/kernel-encoder';
import { mkdirSync } from 'node:fs';
import { join } from 'node:path';
import type { DeflRecord } from './deflVocab.js';
import {
  D_FULL,
  D_MODEL,
  INPUTS_DIR,
  PINNED_B8192_HASH,
  isMain,
  jlProject,
  readInput,
  writeF32,
  writeInput,
} from './common.js';

function main(): void {
  const hash = encoderContentHash();
  if (hash !== PINNED_B8192_HASH) {
    throw new Error(
      `ERR_ENCODER_PIN: kot-enc-B/1 content-hash ${hash} != pinned ${PINNED_B8192_HASH}`,
    );
  }
  if (DEFAULT_PARAMS.D !== D_FULL) {
    throw new Error(`ERR_DIMENSION: DEFAULT_PARAMS.D=${DEFAULT_PARAMS.D} != ${D_FULL}`);
  }

  const defl = readInput<{ artifact: string; ids: string[]; records: DeflRecord[] }>(
    'defl-concepts.json',
  );
  if (defl.artifact !== 'e9-defl-concepts') throw new Error('ERR_ARTIFACT: defl-concepts.json');

  // Scrambles are pure prime structures (no cross-references): encode as a set
  // keyed by the TRUE concept id each scramble replaces.
  const defs = new Map<string, Explication>();
  for (const r of defl.records) defs.set(r.id, r.explication);
  console.log(`encoding ${defs.size} scrambled explications at D=${D_FULL} (kot-enc-B/1)`);
  const { vectors } = encodeConceptSet(defs);

  const fullD: Float64Array[] = defl.ids.map((id) => {
    const v = vectors.get(id);
    if (v === undefined) throw new Error(`ERR_VECTOR: no vector for ${id}`);
    return v;
  });

  console.log(`JL-projecting ${fullD.length} vectors ${D_FULL} -> ${D_MODEL}`);
  const proj = jlProject(fullD, D_FULL, D_MODEL);
  const preNorms = proj.map((v) => Math.sqrt(v.reduce((a, x) => a + x * x, 0)));
  const table = new Float32Array(defl.ids.length * D_MODEL);
  proj.forEach((v, r) => {
    const n = preNorms[r]!;
    if (!(n > 0)) throw new Error(`ERR_NORM: zero-norm projection row ${r}`);
    for (let c = 0; c < D_MODEL; c++) table[r * D_MODEL + c] = Math.fround(v[c]! / n);
  });

  mkdirSync(join(INPUTS_DIR, 'vectors'), { recursive: true });
  const sha = writeF32(join(INPUTS_DIR, 'vectors', `defl-jl${D_MODEL}.f32`), table);

  const pn = preNorms.map((n) => Number(n.toFixed(6)));
  writeInput('defl-tables-manifest.json', {
    artifact: 'e9-defl-tables',
    date: new Date().toISOString(),
    DFull: D_FULL,
    d: D_MODEL,
    rows: defl.ids.length,
    algorithmVersion: 'kot-enc-B/1',
    encoderContentHash: hash,
    pinnedHash: PINNED_B8192_HASH,
    jlDerivation:
      'Achlioptas sign matrix, entries ±1/sqrt(d), signs from SHA-256 stream label jl/<D>/<d>; ' +
      'verbatim copy of poc/harness/x4.ts jlProject (Common rule 3) — identical to poc/e5',
    layout:
      'row-major float32 little-endian (<f4), one row per concept, row order = poc/e5 ids ' +
      '(the E5 items\' row indices address this table unchanged)',
    ids: defl.ids,
    defl: {
      file: `vectors/defl-jl${D_MODEL}.f32`,
      sha256: sha,
      note: 'rows unit-norm AFTER JL projection (E5 O1 operationalisation, inherited)',
      postProjectionPreNormalisation: {
        min: Math.min(...pn),
        max: Math.max(...pn),
        mean: Number((pn.reduce((a, b) => a + b, 0) / pn.length).toFixed(6)),
      },
    },
  });
}

if (isMain(import.meta.url)) main();
