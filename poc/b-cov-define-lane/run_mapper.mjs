/**
 * Mapper-leg driver for the b-cov define-lane census. Drives the FROZEN compiled
 * mapper (mapper/dist/src/defineTemplates.js, parseDefineQuestion) over benchmark
 * question stems — the ready mapper-parse leg, invoked exactly as designed
 * (memo §5). Emits one parse per item (JSONL). The option-resolution helper is a
 * byte-faithful mirror of defineTemplates.ts resolveLabel()/normalize(), used
 * ONLY to resolve each MC option to a urn:kot: URN for the DEFINE-MATCH scoring
 * diagnostic (the census-checkability verdict itself is the §C5 filter in
 * census.py, computed from the candidate tuple parseDefineQuestion returns).
 *
 * Usage: node run_mapper.mjs <define-index.json> <items.jsonl> <out-parses.jsonl>
 * items.jsonl rows: {"id": str, "text": str, "options": [str,...]}
 */
import fs from 'node:fs';
import { parseDefineQuestion } from '../../mapper/dist/src/defineTemplates.js';

const [, , indexPath, itemsPath, outPath] = process.argv;
if (!indexPath || !itemsPath || !outPath) {
  console.error('usage: node run_mapper.mjs <index.json> <items.jsonl> <out.jsonl>');
  process.exit(2);
}

const raw = JSON.parse(fs.readFileSync(indexPath, 'utf-8'));
const labelToUrns = new Map(Object.entries(raw.labelToUrns));
const relationUrns = new Map(Object.entries(raw.relationUrns));
const index = { labelToUrns, relationUrns };

// --- byte-faithful mirror of defineTemplates.ts normalize()/resolveLabel() ---
const ARTICLES = ['the ', 'an ', 'a '];
function normalize(text) {
  return text.toLowerCase().replace(/\s+/g, ' ').trim().replace(/[?.!]+$/, '').trim();
}
function resolveLabel(surfaceRaw) {
  const surface = surfaceRaw.trim();
  let urns = labelToUrns.get(surface);
  if (urns === undefined) {
    for (const art of ARTICLES) {
      if (surface.startsWith(art)) {
        const hit = labelToUrns.get(surface.slice(art.length));
        if (hit !== undefined) { urns = hit; break; }
      }
    }
  }
  if (urns === undefined || urns.length === 0) return { kind: 'none' };
  const distinct = [...new Set(urns)].sort();
  if (distinct.length > 1) return { kind: 'abstain', urns: distinct };
  return { kind: 'urn', urn: distinct[0] };
}

const lines = fs.readFileSync(itemsPath, 'utf-8').split('\n').filter((l) => l.trim());
const out = [];
for (const line of lines) {
  const item = JSON.parse(line);
  const parse = parseDefineQuestion(item.text, index);
  // Option resolution (diagnostic only): normalize each option like a question
  // span, then resolveLabel. Options are MC answer strings (the candidate terms).
  const optionUrns = (item.options || []).map((o) => resolveLabel(normalize(o)));
  out.push(JSON.stringify({ id: item.id, parse, optionUrns }));
}
fs.writeFileSync(outPath, out.join('\n') + '\n');
console.error(`mapped ${out.length} items -> ${outPath}`);
