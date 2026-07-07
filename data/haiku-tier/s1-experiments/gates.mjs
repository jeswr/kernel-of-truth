#!/usr/bin/env node
/**
 * haiku-tier stage 1 — mechanical gate evaluation of model outputs.
 *
 * For each outputs/<FW>/<lemma>.json (claude -p envelope), parses the model's
 * JSON and runs the REAL validators:
 *   - kind "explication": encoder validateExplication (profile-1 grammar /
 *     valency / referent / caps gates), plus ref policy: concept refs must be
 *     catalog kernel-v0 ids and never the concept being defined.
 *   - kind "molecule": the §3.5 mechanical gate, ported verbatim from
 *     data/molecules-v0/validate.mjs (ALLOWED / PHRASES / PUNCT / REF_RE and
 *     rule 1/3/4/5 logic), with the ref universe = kernel-v0 ids + molecules-v0
 *     ids of depth <= 3, self-reference banned, depth = 1 + max(ref depth).
 *   - kind "cannot-formalise": requires a non-empty "why".
 *
 * Usage: node gates.mjs <FW> [...]   -> writes gate-results-<FW>.json
 */
import { readFileSync, readdirSync, writeFileSync, existsSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { validateExplication } from '../../../encoder/dist/src/index.js';

const HERE = dirname(fileURLToPath(import.meta.url));
const REPO = join(HERE, '..', '..', '..');

// --- ref universe -----------------------------------------------------------
const kman = JSON.parse(readFileSync(join(REPO, 'data', 'kernel-v0', 'manifest.json'), 'utf8'));
const kernelIds = new Set(kman.concepts.map((c) => c.id));
const mman = JSON.parse(readFileSync(join(REPO, 'data', 'molecules-v0', 'manifest.json'), 'utf8'));
const molDepth = new Map();
for (const m of mman.molecules) {
  const rec = JSON.parse(readFileSync(join(REPO, 'data', 'molecules-v0', m.file), 'utf8'));
  molDepth.set(rec.id, rec.moleculeDepth);
}

// --- §3.5 controlled lexicon (verbatim from data/molecules-v0/validate.mjs) --
const src = readFileSync(join(REPO, 'data', 'molecules-v0', 'validate.mjs'), 'utf8');
const STR_LIT = /'((?:[^'\\]|\\.)*)'|"((?:[^"\\]|\\.)*)"/g; // both quote styles ("someone's"!)
function grabSet(name) {
  const m = src.match(new RegExp(`const ${name} = new Set\\(\\[([\\s\\S]*?)\\]\\)`));
  return new Set([...m[1].matchAll(STR_LIT)].map((x) => x[1] ?? x[2]));
}
const ALLOWED = grabSet('ALLOWED');
const PHRASES = [...src.match(/const PHRASES = \[([\s\S]*?)\]/)[1].matchAll(STR_LIT)].map((x) => x[1] ?? x[2]);
const PUNCT = /[.,;:()]/g;
const REF_RE = /\{(urn:(kernel-v0|molecule-v0):[a-z0-9-]+)\|([^{}|]+)\}( \[m\])?/g;

/**
 * opts.normalize — pipeline-side normalization of DERIVED/mechanical fields
 * only (no semantic change): NFC + lowercase the note, and recompute
 * groundingRefs from the note instead of trusting the model's list. The
 * volume runner applies this before gating; s1 reports both raw and
 * normalized gate-pass.
 */
export function checkMolecule(lemma, out, opts = {}) {
  const errors = [];
  const fail = (code, msg) => errors.push(`${code}: ${msg}`);
  let note = out.groundingNote;
  if (typeof note !== 'string' || note.length === 0) {
    fail('ERR_GROUNDING_NOTE', 'exactly one groundingNote string required (rule 3)');
    return { errors };
  }
  if (opts.normalize) note = note.normalize('NFC').toLowerCase();
  if (note.normalize('NFC') !== note) fail('ERR_NFC', 'not NFC-normalized');
  const bytes = Buffer.byteLength(note.normalize('NFC'), 'utf8');
  if (bytes > 1024) fail('ERR_GROUNDING_SIZE', `${bytes} bytes > 1024 (rule 3)`);
  if (note !== note.toLowerCase()) fail('ERR_CASE', 'note must be lowercase');
  const refs = [];
  const stripped = note.replace(REF_RE, (all, urn, ns, gloss, mflag) => {
    refs.push(urn);
    if (ns === 'molecule-v0' && !mflag) fail('ERR_M_FLAG', `molecule ref ${urn} not followed by " [m]" (rule 1)`);
    if (ns === 'kernel-v0' && mflag) fail('ERR_M_FLAG', `kernel ref ${urn} wrongly flagged [m]`);
    return ' ';
  });
  if (/[{}|[\]]/.test(stripped)) fail('ERR_GROUNDING_LEXICON', 'stray {, }, |, [ or ] outside a linked ref');
  let depth = 1;
  for (const r of new Set(refs)) {
    const slug = r.split(':').pop();
    if (slug === lemma) fail('ERR_SELF_REF', `grounding note references the concept being defined (${r})`);
    if (r.startsWith('urn:kernel-v0:')) {
      if (!kernelIds.has(r)) fail('ERR_REF', `unknown kernel-v0 ref ${r} (rule 4)`);
    } else if (!molDepth.has(r)) {
      fail('ERR_REF', `unknown molecule ref ${r} (rule 4)`);
    } else {
      if (molDepth.get(r) > 3) fail('ERR_DEPTH', `ref ${r} has depth ${molDepth.get(r)} > 3 (rule 5)`);
      depth = Math.max(depth, 1 + molDepth.get(r));
    }
  }
  if (opts.normalize) {
    out.groundingRefs = [...new Set(refs)].sort();   // recomputed, not trusted
  } else {
    const declared = JSON.stringify([...new Set(out.groundingRefs ?? [])].sort());
    const parsed = JSON.stringify([...new Set(refs)].sort());
    if (declared !== parsed) fail('ERR_REF_LIST', `groundingRefs ${declared} != refs in note ${parsed}`);
  }
  let text = ` ${stripped.replace(PUNCT, ' ')} `;
  for (const ph of PHRASES) {
    text = text.replaceAll(` ${ph} `, ' ').replaceAll(` ${ph} `, ' ');
  }
  for (const tok of text.split(/\s+/)) {
    if (tok.length === 0) continue;
    if (!ALLOWED.has(tok)) fail('ERR_GROUNDING_LEXICON', `token "${tok}" not allowed (rule 3)`);
  }
  if (depth > 4) fail('ERR_DEPTH', `molecule depth ${depth} > 4 (rule 5)`);
  return { errors, depth, bytes, refCount: new Set(refs).size };
}

function collectConceptRefs(node, out) {
  if (Array.isArray(node)) { node.forEach((n) => collectConceptRefs(n, out)); return; }
  if (node === null || typeof node !== 'object') return;
  if (node.kind === 'concept' || node.kind === 'conceptHead') out.add(node.id);
  for (const v of Object.values(node)) collectConceptRefs(v, out);
}

export function checkExplication(lemma, out) {
  const errors = [];
  const rec = out.record;
  if (!rec || typeof rec !== 'object') return { errors: ['ERR_SHAPE: no record object'] };
  try {
    validateExplication(rec);
  } catch (e) {
    errors.push(`${e.code ?? 'ERR'}: ${e.message}`);
  }
  const refs = new Set();
  collectConceptRefs(rec, refs);
  for (const r of refs) {
    if (!kernelIds.has(r)) errors.push(`ERR_REF: explication references ${r} (must be a catalog kernel-v0 id)`);
    else if (r.split(':').pop() === lemma) errors.push(`ERR_SELF_REF: references itself (${r})`);
  }
  return { errors, refCount: refs.size };
}

export function stripFences(s) {
  const m = s.match(/```(?:json)?\s*([\s\S]*?)```/);
  return (m ? m[1] : s).trim();
}

export function evaluate(fw, opts = {}) {
  const dir = join(HERE, 'outputs', fw);
  const rows = [];
  for (const f of readdirSync(dir).filter((x) => x.endsWith('.json')).sort()) {
    const lemma = f.replace(/\.json$/, '');
    const env = JSON.parse(readFileSync(join(dir, f), 'utf8'));
    const mu = env.modelUsage ? Object.values(env.modelUsage)[0] : {};
    const row = { lemma, fw,
      usage: { in: mu.inputTokens, out: mu.outputTokens,
               cacheRead: mu.cacheReadInputTokens, cacheWrite: mu.cacheCreationInputTokens,
               costUSD: mu.costUSD, durationMs: env.duration_ms } };
    let parsed;
    try {
      parsed = JSON.parse(stripFences(env.result ?? ''));
    } catch (e) {
      rows.push({ ...row, kind: 'parse-failure', pass: false, errors: ['ERR_JSON: ' + e.message] });
      continue;
    }
    row.kind = parsed.kind;
    if (parsed.kind === 'molecule') {
      const r = checkMolecule(lemma, parsed, opts);
      rows.push({ ...row, ...r, pass: r.errors.length === 0 });
    } else if (parsed.kind === 'explication') {
      const r = checkExplication(lemma, parsed);
      rows.push({ ...row, ...r, pass: r.errors.length === 0 });
    } else if (parsed.kind === 'cannot-formalise') {
      const ok = typeof parsed.why === 'string' && parsed.why.trim().length > 0;
      rows.push({ ...row, pass: ok, errors: ok ? [] : ['ERR_WHY: empty why'] });
    } else {
      rows.push({ ...row, kind: String(parsed.kind), pass: false, errors: ['ERR_KIND: unknown kind'] });
    }
  }
  return rows;
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  // --one <lemma> <file-with-model-result-text>: gate a single output (used
  // by the volume runner); prints {kind, pass, errors, ...} JSON to stdout.
  if (process.argv.includes('--one')) {
    const args = process.argv.slice(2).filter((a) => a !== '--one' && a !== '--normalized');
    const oneNormalized = process.argv.includes('--normalized');
    const [lemma, file] = args;
    const text = stripFences(readFileSync(file, 'utf8'));
    let parsed, row;
    try { parsed = JSON.parse(text); } catch (e) {
      row = { lemma, kind: 'parse-failure', pass: false, errors: ['ERR_JSON: ' + e.message] };
    }
    if (!row) {
      if (parsed.kind === 'molecule') {
        const r = checkMolecule(lemma, parsed, oneNormalized ? { normalize: true } : {});
        row = { lemma, kind: 'molecule', ...r, pass: r.errors.length === 0,
                normalizedRefs: parsed.groundingRefs ?? null };
      } else if (parsed.kind === 'explication') {
        const r = checkExplication(lemma, parsed);
        row = { lemma, kind: 'explication', ...r, pass: r.errors.length === 0 };
      } else if (parsed.kind === 'cannot-formalise') {
        const ok = typeof parsed.why === 'string' && parsed.why.trim().length > 0;
        row = { lemma, kind: 'cannot-formalise', pass: ok, errors: ok ? [] : ['ERR_WHY: empty why'] };
      } else {
        row = { lemma, kind: String(parsed?.kind), pass: false, errors: ['ERR_KIND: unknown kind'] };
      }
    }
    console.log(JSON.stringify(row));
    process.exit(0);
  }
  const normalized = process.argv.includes('--normalized');
  for (const fw of process.argv.slice(2).filter((a) => a !== '--normalized')) {
    const rows = evaluate(fw, normalized ? { normalize: true } : {});
    const attempted = rows.filter((r) => r.kind === 'molecule' || r.kind === 'explication');
    const summary = {
      fw, n: rows.length,
      byKind: Object.fromEntries(['molecule', 'explication', 'cannot-formalise', 'parse-failure']
        .map((k) => [k, rows.filter((r) => r.kind === k).length])),
      gatePassOfAttempted: attempted.length
        ? +(attempted.filter((r) => r.pass).length / attempted.length).toFixed(3) : null,
      cannotFormaliseRate: +(rows.filter((r) => r.kind === 'cannot-formalise').length / rows.length).toFixed(3),
      meanCostUSD: +(rows.reduce((s, r) => s + (r.usage.costUSD ?? 0), 0) / rows.length).toFixed(5),
      meanDurationMs: Math.round(rows.reduce((s, r) => s + (r.usage.durationMs ?? 0), 0) / rows.length),
    };
    writeFileSync(join(HERE, `gate-results-${fw}${normalized ? '-normalized' : ''}.json`),
      JSON.stringify({ summary, rows }, null, 1));
    console.log(JSON.stringify(summary));
  }
}
