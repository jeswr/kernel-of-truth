#!/usr/bin/env node
/**
 * onto-sumo random-sample audit (requires source/). Two independent-path
 * re-derivations:
 *   (a) axioms: a seeded sample is re-derived by RE-READING the source .kif and
 *       taking the ordinal-th top-level form; its canonical string must equal
 *       the emitted record's kif.
 *   (b) term documentation: a seeded sample of terms with a doc annotation is
 *       re-extracted by an INDEPENDENT hand-rolled quoted-string scan
 *       (`(documentation <Term> EnglishLanguage "..."`), NOT the S-expr parser,
 *       and must equal the emitted annotation.
 * Error rate printed. Usage: node .../sample-review.mjs [Nax] [Ndoc] [seedHex]
 */
import { readFileSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { parseKif, canonical } from './parse-kif.mjs';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const SRC = join(ROOT, 'source');
const NAX = parseInt(process.argv[2] || '150', 10);
const NDOC = parseInt(process.argv[3] || '100', 10);
const SEED = process.argv[4] || '0x5107';

function mulberry32(a) {
  return function () {
    a |= 0; a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
function shuffled(n, seed) {
  const rng = mulberry32(seed >>> 0);
  const a = Array.from({ length: n }, (_, i) => i);
  for (let i = n - 1; i > 0; i--) { const j = Math.floor(rng() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; }
  return a;
}

const FILE_OF = { M: 'Merge.kif', MILO: 'Mid-level-ontology.kif' };
const srcCache = {};
function srcText(file) {
  if (!srcCache[file]) {
    const p = join(SRC, file);
    if (!existsSync(p)) throw new Error(`ERR_SOURCE_MISSING: ${file} (re-download per README)`);
    srcCache[file] = readFileSync(p, 'utf8');
  }
  return srcCache[file];
}
/** Independent string-aware comment stripper (";" to EOL, not inside "..."),
 * so the doc scan does not read a ";;"-commented-out duplicate. Reimplemented
 * here (a plain char scan), deliberately not shared with the S-expr tokenizer. */
const strippedCache = {};
function srcNoComments(file) {
  if (!strippedCache[file]) {
    const text = srcText(file);
    let out = ''; let inStr = false;
    for (let i = 0; i < text.length; i++) {
      const c = text[i];
      if (inStr) { out += c; if (c === '\\') { out += text[i + 1] ?? ''; i++; continue; } if (c === '"') inStr = false; continue; }
      if (c === '"') { inStr = true; out += c; continue; }
      if (c === ';') { while (i < text.length && text[i] !== '\n') i++; out += '\n'; continue; }
      out += c;
    }
    strippedCache[file] = out;
  }
  return strippedCache[file];
}
const formsCache = {};
function srcForms(file) {
  if (!formsCache[file]) formsCache[file] = parseKif(srcText(file));
  return formsCache[file];
}

/** Independent hand-rolled reader of the doc string after a documentation head.
 * Whitespace-tolerant (the head may span source lines); regex-located, then a
 * hand-rolled quoted-string read — deliberately NOT the S-expr parser. */
function rawDoc(text, term) {
  const esc = term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const re = new RegExp(`\\(documentation\\s+${esc}\\s+EnglishLanguage\\s+"`);
  const m = re.exec(text);
  if (!m) return null;
  let i = m.index + m[0].length;
  let out = '';
  for (; i < text.length; i++) {
    const c = text[i];
    if (c === '\\') { out += (text[i + 1] === 'n' ? '\n' : text[i + 1] === 't' ? '\t' : text[i + 1]); i++; continue; }
    if (c === '"') break;
    out += c;
  }
  return out;
}

const axioms = readFileSync(join(ROOT, 'axioms.jsonl'), 'utf8').trim().split('\n').map(JSON.parse);
const terms = readFileSync(join(ROOT, 'terms.jsonl'), 'utf8').trim().split('\n').map(JSON.parse);

// (a) axiom re-derivation
let axErr = 0; const axLog = [];
const axIdx = shuffled(axioms.length, parseInt(SEED, 16)).slice(0, Math.min(NAX, axioms.length));
for (const k of axIdx) {
  const a = axioms[k];
  const tag = a.id.match(/ax-(M|MILO)-\d+$/)[1]; // urn:onto-sumo:ax-<TAG>-<ord>
  const forms = srcForms(FILE_OF[tag]);
  const form = forms[a.ordinal - 1];
  if (!form) { axErr++; axLog.push(`${a.id}: no form at ordinal`); continue; }
  const canon = canonical(form);
  if (canon !== a.kif) { axErr++; axLog.push(`${a.id}: canonical mismatch`); }
}

// (b) term-documentation re-derivation (independent scan)
let docErr = 0; const docLog = [];
const withDoc = terms.filter((t) => t.annotations && t.annotations.documentation);
const docIdx = shuffled(withDoc.length, (parseInt(SEED, 16) ^ 0x9e3779b9) >>> 0).slice(0, Math.min(NDOC, withDoc.length));
for (const k of docIdx) {
  const t = withDoc[k];
  // search both source files (term may be defined in either)
  let found = null;
  for (const file of Object.values(FILE_OF)) { const d = rawDoc(srcNoComments(file), t.term); if (d !== null) { found = d; break; } }
  if (found === null) { docErr++; docLog.push(`${t.term}: doc not found in source`); continue; }
  if (found !== t.annotations.documentation) { docErr++; docLog.push(`${t.term}: doc mismatch`); }
}

const axRate = ((axErr / axIdx.length) * 100).toFixed(2);
const docRate = ((docErr / docIdx.length) * 100).toFixed(2);
console.log(`onto-sumo sample audit (seed ${SEED}):`);
console.log(`  axioms: N=${axIdx.length}, errors=${axErr} (${axRate}%)`);
console.log(`  term docs: N=${docIdx.length}, errors=${docErr} (${docRate}%)`);
for (const e of [...axLog, ...docLog].slice(0, 20)) console.log('  ERR ' + e);
process.exit(axErr === 0 && docErr === 0 ? 0 : 1);
