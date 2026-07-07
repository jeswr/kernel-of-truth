#!/usr/bin/env node
// extract.mjs — deterministic doc-gen4 HTML -> lean-ref/1 sample records.
//
// Deliverable of bead kernel-of-truth-vn8 (Mathlib/Lean extraction route:
// feasibility + sample). See docs/design-lean-route.md for the route survey
// and the honesty argument for why these are *formal reference records*
// (annotation-layer, identity anchored on (mathlibCommit, name)), NOT
// concept-definitional records: nothing in a Lean pretty-printed signature is
// canonical under Lean's identity-modulo-definitional-equality (see
// docs/design-math-sector.md §1.2/§2.4), so no field of these records enters
// any concept-hash boundary.
//
// Determinism contract (docs/design-bulk-kernel.md, provenance rule): given
// the byte-identical snapshots in source-snapshot/, this script re-emits
// records.jsonl and manifest.json byte-identically. No timestamps here;
// fetch time lives in fetch-log.json (written once at fetch time, by hand).
//
// Usage:  node extract.mjs            (reads source-snapshot/, writes
//                                      records.jsonl + manifest.json)
//
// Zero dependencies (node:crypto, node:fs only) per repo convention.

import { createHash } from 'node:crypto';
import { readFileSync, writeFileSync, readdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const EXTRACTOR = { name: 'kernel-of-truth/data/math-lean-sample/extract.mjs', version: '0.1.0' };
const SITE = 'https://leanprover-community.github.io/mathlib4_docs/';

// ---------- tiny HTML helpers (doc-gen4 output is machine-generated and
// well-nested, so balanced-div scanning is sound; fail closed otherwise) ----

/** Find the index just past the matching </div> for the <div at `start`. */
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

const ENTITIES = { amp: '&', lt: '<', gt: '>', quot: '"', apos: "'", nbsp: ' ' };
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

/** Strip tags, decode entities, collapse whitespace.
 * Inline tags (span/a/code/...) vanish — the pretty-printer's own spaces in
 * text nodes carry token separation (e.g. <span>Nat</span>.<span>succ</span>
 * must yield "Nat.succ"). Block tags become a space so adjacent blocks
 * (decl_args | decl_type) don't fuse. */
function flatText(fragment) {
  const detagged = fragment
    .replace(/<\/?(?:div|p|li|ul|ol|details|summary|blockquote|br|h[1-6])\b[^>]*>/g, ' ')
    .replace(/<[^>]*>/g, '');
  return decodeEntities(detagged).replace(/\s+/g, ' ').trim();
}

// ---------- per-declaration parse ----------

const GH_RE = /https:\/\/github\.com\/leanprover-community\/mathlib4\/blob\/([0-9a-f]{40})\/([^#"]+)#L(\d+)-L(\d+)/;

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

    // Signature-level references: every hyperlinked identifier in the header.
    const refs = new Set();
    for (const rm of headerHtml.matchAll(/href="[^"#]*#([^"]+)"/g)) {
      const ref = decodeEntities(rm[1]);
      if (ref !== name) refs.add(ref);
    }

    // Docstring: content after the header, minus <details> blocks (equations,
    // instances) — doc-gen4 renders the docstring as sibling <p>/<ul>/... .
    const tail = declHtml.slice(hEnd)
      .replace(/<details[\s\S]*?<\/details>/g, ' ')
      .replace(/<\/?div[^>]*>/g, ' ');
    const docstring = flatText(tail);

    records.push({
      record: 'lean-ref/1',
      status: 'formal-reference',            // annotation-layer; never hash-boundary
      name,
      kind: kindM[1],
      module: moduleName,
      attributes: attrM ? flatText(attrM[1]) : '',
      signaturePretty: flatText(headerHtml), // NON-CANONICAL (notation, implicit args, pp settings)
      docstring,                             // '' when the declaration has none
      referencesPretty: [...refs].sort(),    // signature-level deps only (not proof/value deps)
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

const snapDir = join(HERE, 'source-snapshot');
const files = readdirSync(snapDir).filter((f) => f.endsWith('.html')).sort();
if (files.length === 0) throw new Error('ERR_NO_SNAPSHOTS');

const all = [];
const moduleEntries = [];
let commit = null;
for (const f of files) {
  const moduleName = f.replace(/\.html$/, '');
  const bytes = readFileSync(join(snapDir, f));
  const { records, commit: c } = parseModule(moduleName, bytes.toString('utf8'));
  if (commit === null) commit = c; else if (commit !== c) throw new Error('ERR_CROSS_MODULE_COMMIT_MISMATCH');
  all.push(...records);
  moduleEntries.push({
    module: moduleName,
    sourceUrl: `${SITE}${moduleName.replaceAll('.', '/')}.html`,
    snapshotSha256: createHash('sha256').update(bytes).digest('hex'),
    declCount: records.length,
  });
}

const kindCounts = {};
for (const r of all) kindCounts[r.kind] = (kindCounts[r.kind] ?? 0) + 1;

writeFileSync(join(HERE, 'records.jsonl'), all.map((r) => JSON.stringify(r)).join('\n') + '\n');
writeFileSync(join(HERE, 'manifest.json'), JSON.stringify({
  sample: 'math-lean-sample/v0',
  extractor: EXTRACTOR,
  identityNote: 'Records are formal references (annotation layer). Identity anchor is (source.mathlibCommit, name). No field is concept-hash-boundary content; see docs/design-lean-route.md.',
  mathlibCommit: commit,
  modules: moduleEntries,
  totalRecords: all.length,
  kindCounts,
}, null, 2) + '\n');

console.log(`extracted ${all.length} records from ${files.length} modules at mathlib@${commit.slice(0, 12)}`);
