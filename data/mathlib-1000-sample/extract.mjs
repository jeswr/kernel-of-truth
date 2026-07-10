#!/usr/bin/env node
// extract.mjs — deterministic doc-gen4 HTML -> lean-ref/1 records for the g8
// mathlib-1000-sample (D-ML input to experiment g8; registry/experiments/g8.json).
//
// This is the bulk sibling of data/math-lean-sample/extract.mjs (bead
// kernel-of-truth-vn8): same proven doc-gen4 parser, extended to (a) read the
// gzipped module-page archive under source-snapshot/, (b) select exactly the
// 1,000 declarations named in sample.json (the seed-0 SHA-256-keyed random
// sample), and (c) fail closed unless every sampled declaration is accounted
// for. See docs/design-lean-route.md (route survey; §5.2 fallback doc-gen4
// crawl, the route used here) and docs/design-dl-from-nsm-and-lean-reconstruction.md
// §5.3 (the fragment-gate / forward-map / round-trip protocol g8 measures).
//
// Records are lean-ref/1 formal-reference records: annotation-layer, identity
// anchored on (source.mathlibCommit, name), minting NO urn:concept: ids. No
// field is concept-hash-boundary content (design-lean-route §2).
//
// Determinism contract (docs/design-bulk-kernel.md provenance rule): given the
// byte-identical source-snapshot/*.html.gz + sample.json, this script re-emits
// records.jsonl + manifest.json byte-identically. No timestamps here; fetch
// time lives in fetch-log.json.
//
// Usage:  node extract.mjs      (reads source-snapshot/ + sample.json,
//                                writes records.jsonl + manifest.json)
// Zero dependencies (node:crypto, node:fs, node:zlib only) per repo convention.

import { createHash } from 'node:crypto';
import { readFileSync, writeFileSync, readdirSync } from 'node:fs';
import { gunzipSync } from 'node:zlib';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const EXTRACTOR = { name: 'kernel-of-truth/data/mathlib-1000-sample/extract.mjs', version: '0.1.0' };
const SITE = 'https://leanprover-community.github.io/mathlib4_docs/';

// ---------- tiny HTML helpers (identical to math-lean-sample/extract.mjs) ----------

function divSpanEnd(html, start) {
  const re = /<\/?div\b/g;
  re.lastIndex = start;
  let depth = 0, m;
  while ((m = re.exec(html)) !== null) {
    depth += m[0] === '<div' ? 1 : -1;
    if (depth === 0) {
      const close = html.indexOf('>', m.index);
      if (close === -1) break;
      return close + 1;
    }
  }
  throw new Error(`ERR_UNBALANCED_DIV at ${start}`); // fail closed
}

const ENTITIES = { amp: '&', lt: '<', gt: '>', quot: '"', apos: "'", nbsp: ' ' };
function decodeEntities(s) {
  return s.replace(/&(#x?[0-9a-fA-F]+|[a-zA-Z]+);/g, (whole, body) => {
    if (body[0] === '#') {
      const cp = body[1] === 'x' || body[1] === 'X'
        ? parseInt(body.slice(2), 16) : parseInt(body.slice(1), 10);
      return Number.isFinite(cp) ? String.fromCodePoint(cp) : whole;
    }
    return ENTITIES[body] ?? whole;
  });
}

function flatText(fragment) {
  const detagged = fragment
    .replace(/<\/?(?:div|p|li|ul|ol|details|summary|blockquote|br|h[1-6])\b[^>]*>/g, ' ')
    .replace(/<[^>]*>/g, '');
  return decodeEntities(detagged).replace(/\s+/g, ' ').trim();
}

const GH_RE = /https:\/\/github\.com\/leanprover-community\/mathlib4\/blob\/([0-9a-f]{40})\/([^#"]+)#L(\d+)-L(\d+)/;

// Parse every TOP-LEVEL <div class="decl" id="..."> in a module page.
function parseModule(moduleName, html) {
  const records = [];
  const marker = '<div class="decl" id="';
  let commit = null;
  let at = html.indexOf(marker);
  while (at !== -1) {
    const declHtml = html.slice(at, divSpanEnd(html, at));
    const name = decodeEntities(declHtml.slice(marker.length, declHtml.indexOf('"', marker.length)));

    const kindM = declHtml.match(/<span class="decl_kind">([a-z ]+)<\/span>/);
    if (!kindM) throw new Error(`ERR_NO_KIND ${name}`);

    const gh = declHtml.match(GH_RE);
    if (!gh) throw new Error(`ERR_NO_SOURCE_LINK ${name}`);
    if (commit === null) commit = gh[1];
    else if (commit !== gh[1]) throw new Error(`ERR_COMMIT_MISMATCH ${name}`);

    const attrM = declHtml.match(/<div class="attributes">([\s\S]*?)<\/div>/);

    const hStart = declHtml.indexOf('<div class="decl_header">');
    if (hStart === -1) throw new Error(`ERR_NO_HEADER ${name}`);
    const hEnd = divSpanEnd(declHtml, hStart);
    const headerHtml = declHtml.slice(hStart, hEnd);

    const refs = new Set();
    for (const rm of headerHtml.matchAll(/href="[^"#]*#([^"]+)"/g)) {
      const ref = decodeEntities(rm[1]);
      if (ref !== name) refs.add(ref);
    }

    const tail = declHtml.slice(hEnd)
      .replace(/<details[\s\S]*?<\/details>/g, ' ')
      .replace(/<\/?div[^>]*>/g, ' ');
    const docstring = flatText(tail);

    records.push({
      record: 'lean-ref/1',
      status: 'formal-reference',
      name,
      kind: kindM[1],
      module: moduleName,
      extraction: 'doc-gen4-decl',
      attributes: attrM ? flatText(attrM[1]) : '',
      signaturePretty: flatText(headerHtml), // NON-CANONICAL rendering (design-lean-route §2)
      docstring,
      referencesPretty: [...refs].sort(),
      hasEquations: /<details[^>]*><summary>Equations/.test(declHtml),
      equationsUnrendered: declHtml.includes('did not get rendered due to their size'),
      source: {
        mathlibCommit: gh[1],
        file: gh[2],
        lineStart: Number(gh[3]),
        lineEnd: Number(gh[4]),
      },
    });
    at = html.indexOf(marker, at + marker.length);
  }
  return { records, commit };
}

// ---------- main ----------

const sample = JSON.parse(readFileSync(join(HERE, 'sample.json'), 'utf8'));
const wantByModule = new Map();       // moduleFile -> Set(name)
const idxByName = new Map();          // name -> {docLink, indexKind, moduleFile}
for (const e of sample.selected) {
  const modPath = e.docLink.split('#')[0];               // ./Mathlib/....html
  const moduleFile = modPath.slice(2).replaceAll('/', '.'); // Mathlib.....html
  if (!wantByModule.has(moduleFile)) wantByModule.set(moduleFile, new Set());
  wantByModule.get(moduleFile).add(e.name);
  idxByName.set(e.name, { docLink: e.docLink, indexKind: e.indexKind, moduleFile });
}

const snapDir = join(HERE, 'source-snapshot');
const gzs = readdirSync(snapDir).filter((f) => f.endsWith('.html.gz')).sort();
if (gzs.length === 0) throw new Error('ERR_NO_SNAPSHOTS');

const extracted = new Map();          // name -> record
let commit = null;
const moduleHtml = new Map();         // moduleFile -> html (kept only for anchor checks on misses)
for (const gz of gzs) {
  const moduleFile = gz.replace(/\.gz$/, '');            // Mathlib.....html
  const moduleName = moduleFile.replace(/\.html$/, '');  // Mathlib.....
  const html = gunzipSync(readFileSync(join(snapDir, gz))).toString('utf8');
  const want = wantByModule.get(moduleFile);
  if (!want) continue;                                   // module not in sample (defensive)
  moduleHtml.set(moduleFile, html);
  const { records, commit: c } = parseModule(moduleName, html);
  if (c) { if (commit === null) commit = c; else if (commit !== c) throw new Error('ERR_CROSS_MODULE_COMMIT_MISMATCH ' + moduleName); }
  for (const r of records) if (want.has(r.name)) extracted.set(r.name, r);
}
if (!commit) throw new Error('ERR_NO_COMMIT');

// Account for every sampled declaration; flag the ones with no top-level decl div.
const all = [];
let nDecl = 0, nSub = 0, nIndexOnly = 0;
for (const e of sample.selected) {
  if (extracted.has(e.name)) { all.push(extracted.get(e.name)); nDecl++; continue; }
  const info = idxByName.get(e.name);
  const html = moduleHtml.get(info.moduleFile) || '';
  const anchorPresent = html.includes(`id="${e.name}"`);
  const status = anchorPresent ? 'sub-declaration' : 'index-only';
  if (anchorPresent) nSub++; else nIndexOnly++;
  all.push({
    record: 'lean-ref/1',
    status: 'formal-reference',
    name: e.name,
    kind: e.indexKind,
    module: info.moduleFile.replace(/\.html$/, ''),
    extraction: status, // doc-gen4 signature-layer limitation; resolve via ntp-toolkit primary route (design-lean-route §5.1)
    attributes: '',
    signaturePretty: '',
    docstring: '',
    referencesPretty: [],
    hasEquations: false,
    equationsUnrendered: false,
    source: { mathlibCommit: commit, docLink: e.docLink },
    note: anchorPresent
      ? 'Auto-generated sub-declaration (structure field / constructor / class-projection): doc-gen4 renders it inside its parent decl div, not as a top-level decl. Signature not extracted at the doc-gen4 layer.'
      : 'Declaration present in declaration-data.bmp but not rendered as an anchor on the module page (auto-generated projection). Signature unavailable at the doc-gen4 layer.',
  });
}
if (all.length !== 1000) throw new Error(`ERR_SAMPLE_COUNT ${all.length} != 1000`);

// Deterministic order: by UTF-8 bytes of name.
all.sort((a, b) => Buffer.compare(Buffer.from(a.name, 'utf8'), Buffer.from(b.name, 'utf8')));

const kindCounts = {};
for (const r of all) kindCounts[r.kind] = (kindCounts[r.kind] ?? 0) + 1;
const extractionCounts = { 'doc-gen4-decl': nDecl, 'sub-declaration': nSub, 'index-only': nIndexOnly };

const moduleEntries = [];
for (const gz of gzs) {
  const moduleFile = gz.replace(/\.gz$/, '');
  const bytes = readFileSync(join(snapDir, gz));
  moduleEntries.push({
    module: moduleFile.replace(/\.html$/, ''),
    snapshot: `source-snapshot/${gz}`,
    snapshotGzSha256: createHash('sha256').update(bytes).digest('hex'),
  });
}

writeFileSync(join(HERE, 'records.jsonl'), all.map((r) => JSON.stringify(r)).join('\n') + '\n');
writeFileSync(join(HERE, 'manifest.json'), JSON.stringify({
  sample: 'mathlib-1000-sample/v0',
  purpose: 'D-ML input for experiment g8 (registry/experiments/g8.json); the 1,000-declaration random Mathlib sample = the fragment-gate null denominator (HS8/NF3).',
  extractor: EXTRACTOR,
  route: 'doc-gen4 fallback crawl (design-lean-route.md §5.2); signature-layer only, HTML-derived.',
  identityNote: 'Records are formal references (annotation layer). Identity anchor is (source.mathlibCommit, name). No field is concept-hash-boundary content; see docs/design-lean-route.md §2.',
  seed: sample.seed,
  seedLabel: sample.sampling_algorithm.seed_label,
  enumerationIndexSha256: sample.enumeration_index.sha256,
  mathlibCommit: commit,
  populationSize: sample.n_mathlib_proper,
  totalRecords: all.length,
  distinctModules: moduleEntries.length,
  kindCounts,
  extractionCounts,
  modules: moduleEntries,
}, null, 2) + '\n');

console.log(`extracted ${all.length} records (${nDecl} decl / ${nSub} sub-declaration / ${nIndexOnly} index-only) from ${gzs.length} modules at mathlib@${commit.slice(0, 12)}`);
