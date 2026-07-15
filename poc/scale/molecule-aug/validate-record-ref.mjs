#!/usr/bin/env node
/**
 * validate-record-ref.mjs -- S5 (reference-augmented) variant of the
 * concept-def mechanical gate. DESIGN ARTEFACT of poc/scale/molecule-aug/
 * (see DESIGN.md §5): the pinned poc/scale/concept-def-agent/validate-record.mjs
 * is NOT modified; this file lives alongside and is used ONLY by the S5 arm.
 *
 * Differences from the pinned gate (each cited in DESIGN.md §5.2):
 *   1. The encode map is not a single-entry map: the referenceable lexicon's
 *      explications (kernel-v0 54 + molecule-aug bridge records) are loaded
 *      into the defs map, so ConceptRef fillers RESOLVE (encoder.ts
 *      encodeConceptSetWith walks the reference DAG; ERR_CONCEPT_UNRESOLVED /
 *      ERR_CYCLIC_CONCEPT_REF still fail closed).
 *   2. references-policy check moves here from define_concept.py check_record:
 *      the record's top-level `references` array must EXACTLY equal the set of
 *      concept ids mentioned in the explication AST (sorted), and every id
 *      must be in the referenceable lexicon (ERR_REF_NOT_IN_LEXICON) --
 *      no free-floating concept ids, no self-reference (ERR_SELF_REF).
 *   3. Reference-count cap: <= 8 distinct referenced ids per record
 *      (STIPULATED-not-MEASURED, DESIGN.md §5.2 R4) so records stay
 *      explications, not bag-of-concepts tag lists.
 *
 * usage: node validate-record-ref.mjs <record.json> [--lexicon <dir>]...
 *   default lexicons: ../../../data/kernel-v0/concepts +
 *                     ./lexicon/records (the molecule-aug bridge records)
 * Prints one JSON line; exit 0 iff the record passes. Zero encoder changes:
 * D=8192 profile-1 encoder, same content hash, no ALGORITHM_VERSION bump.
 */
import { readFileSync, readdirSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  validateExplication,
  encodeConceptSet,
  AST_SCHEMA,
} from '../../../encoder/dist/src/index.js';

const HERE = dirname(fileURLToPath(import.meta.url));
const MAX_REFS = 8; // STIPULATED (DESIGN.md §5.2 R4)

const out = (o, code) => {
  console.log(JSON.stringify(o));
  process.exit(code);
};

const args = process.argv.slice(2);
const path = args[0];
if (!path || path.startsWith('--')) {
  out({ ok: false, code: 'ERR_USAGE', error: 'usage: validate-record-ref.mjs <record.json> [--lexicon <dir>]...' }, 2);
}
const lexDirs = [];
for (let i = 1; i < args.length; i++) {
  if (args[i] === '--lexicon' && args[i + 1]) lexDirs.push(args[++i]);
}
if (lexDirs.length === 0) {
  lexDirs.push(join(HERE, '../../../data/kernel-v0/concepts'));
  const bridge = join(HERE, 'lexicon/records');
  if (existsSync(bridge)) lexDirs.push(bridge);
}

// -- load the referenceable lexicon (fail closed on any unreadable record) --
const lexicon = new Map(); // id -> explication
for (const dir of lexDirs) {
  let files;
  try {
    files = readdirSync(dir).filter((f) => f.endsWith('.json') && !f.endsWith('.report.json'));
  } catch (e) {
    out({ ok: false, code: 'ERR_LEXICON_DIR', error: `${dir}: ${e.message}` }, 1);
  }
  for (const f of files) {
    let d;
    try {
      d = JSON.parse(readFileSync(join(dir, f), 'utf8'));
    } catch (e) {
      out({ ok: false, code: 'ERR_LEXICON_JSON', error: `${dir}/${f}: ${e.message}` }, 1);
    }
    if (typeof d.id !== 'string' || d.explication?.schema !== AST_SCHEMA) {
      out({ ok: false, code: 'ERR_LEXICON_RECORD', error: `${dir}/${f}: not a kot-ast/1 concept record` }, 1);
    }
    // kernel-v0 REPAIR override (adjudication closure; lexicon/build_manifest.mjs
    // §2b): a molecule-aug-LOCAL file named kernel-v0-<slug>.json whose id is
    // urn:kernel-v0:<slug> REPLACES the canonical entry loaded from an earlier
    // --lexicon dir — the shared corpus data/kernel-v0/ stays byte-stable and
    // is repaired here, for this arm only. Any other duplicate id still fails
    // closed (ERR_LEXICON_DUP).
    const ovm = /^kernel-v0-([a-z0-9-]+)\.json$/.exec(f);
    const isOverride = ovm !== null && d.id === `urn:kernel-v0:${ovm[1]}`;
    if (lexicon.has(d.id) && !isOverride) {
      out({ ok: false, code: 'ERR_LEXICON_DUP', error: `duplicate lexicon id ${d.id}` }, 1);
    }
    lexicon.set(d.id, d.explication);
  }
}

// -- load the candidate record --
let doc;
try {
  doc = JSON.parse(readFileSync(path, 'utf8'));
} catch (e) {
  out({ ok: false, code: 'ERR_JSON', error: e.message }, 1);
}

// -- collect concept ids actually mentioned in the AST (mirror of
//    encoder.ts collectConceptRefs, reimplemented here so the policy check
//    does not depend on an unexported encoder internal) --
function conceptIds(node, acc) {
  if (node === null || typeof node !== 'object') return acc;
  if (Array.isArray(node)) { for (const x of node) conceptIds(x, acc); return acc; }
  if ((node.kind === 'concept' || node.kind === 'conceptHead') && typeof node.id === 'string') acc.add(node.id);
  for (const v of Object.values(node)) conceptIds(v, acc);
  return acc;
}

try {
  if (doc.explication?.schema !== AST_SCHEMA) {
    throw Object.assign(new Error(`explication.schema must be '${AST_SCHEMA}'`), { code: 'ERR_SCHEMA' });
  }
  const stats = validateExplication(doc.explication);

  // references-policy gates (§5.2 R1-R4)
  const mentioned = [...conceptIds(doc.explication, new Set())].sort();
  const declared = Array.isArray(doc.references) ? [...doc.references].sort() : null;
  if (declared === null) {
    throw Object.assign(new Error('references must be an array'), { code: 'ERR_REFERENCES_FIELD' });
  }
  if (JSON.stringify(declared) !== JSON.stringify(mentioned)) {
    throw Object.assign(
      new Error(`references [${declared}] != AST concept ids [${mentioned}]`),
      { code: 'ERR_REF_MISMATCH' });
  }
  if (mentioned.includes(doc.id)) {
    throw Object.assign(new Error('record references itself'), { code: 'ERR_SELF_REF' });
  }
  for (const id of mentioned) {
    if (!lexicon.has(id)) {
      throw Object.assign(new Error(`'${id}' is not in the referenceable lexicon`), { code: 'ERR_REF_NOT_IN_LEXICON' });
    }
  }
  if (mentioned.length > MAX_REFS) {
    throw Object.assign(new Error(`${mentioned.length} distinct references exceeds cap ${MAX_REFS}`), { code: 'ERR_REF_CAP' });
  }

  // encode with the WHOLE lexicon in the defs map (the one-line fix that
  // makes references resolve; everything else is unchanged from the pinned gate)
  const defs = new Map(lexicon);
  defs.set(doc.id, doc.explication);
  const { vectors } = encodeConceptSet(defs);
  const v = vectors.get(doc.id);
  if (!v) throw Object.assign(new Error('no vector produced'), { code: 'ERR_ENCODE' });
  if (v.some((x) => Number.isNaN(x))) throw Object.assign(new Error('NaN in vector'), { code: 'ERR_ENCODE' });
  const norm = Math.sqrt(v.reduce((a, x) => a + x * x, 0));
  if (!(norm > 0) || !Number.isFinite(norm)) throw Object.assign(new Error('bad norm'), { code: 'ERR_ENCODE' });
  out({ ok: true, stats, D: v.length, norm, references: mentioned, lexiconSize: lexicon.size }, 0);
} catch (e) {
  out({ ok: false, code: e.code ?? null, error: e.message }, 1);
}
