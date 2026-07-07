#!/usr/bin/env node
/**
 * SUMO (SUO-KIF) -> onto-sumo tier extractor (kernel-of-truth-cgh).
 *
 * Sources (source/, gitignored): Merge.kif (SUMO upper ontology) and
 * Mid-level-ontology.kif (MILO). A PRINCIPLED SUBSET rule: we extract SUMO's
 * language-independent upper + mid-level core (Merge + MILO), which is where
 * the definitional axioms live; the ~100 domain .kif files (Cars, Hotel, ...)
 * are out of scope for this ingestion (follow-up filed).
 *
 * Two deliverables, mm-canonical style (cf. data/math-mm):
 *   axioms.jsonl — EVERY top-level KIF statement as a canonical one-line string
 *     (form:"sumo-kif-canonical"), with the SUMO terms it mentions and, for
 *     declarations, its subject. NO semantic translation.
 *   terms.jsonl  — the term inventory: every term SUMO DECLARES, with its
 *     structured declaration axioms (subclass/instance/subrelation/subAttribute/
 *     domain/range/partition/disjoint), documentation + termFormat annotations,
 *     axiom statistics, and refs to the <=> biconditional axioms that DEFINE it
 *     (SUMO's genuinely-definitional statements, analogous to set.mm df-*).
 *
 * Honesty architecture: semanticStatus AxiomsOnly; structural axioms + canonical
 * strings only, NO semantic-adequacy claim. documentation/termFormat are
 * annotations OUTSIDE identity. provenance mandatory; extraction byte-deterministic.
 *
 * Usage: nice -n 10 node data/onto-sumo/extractor/extract.mjs
 */
import { createHash } from 'node:crypto';
import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { parseKif, canonical, op, isTerm, mentionedTerms } from './parse-kif.mjs';

export const EXTRACTOR_NAME = 'kot-sumo-extractor';
export const EXTRACTOR_VERSION = '0.1.0';
export const EXTRACTION_DATE = '2026-07-07';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const SRC = join(ROOT, 'source');

export const SOURCE = {
  repository: 'https://github.com/ontologyportal/sumo',
  commit: 'ceb2954bccf98b3d113ea82797493a2b92b3e987',
  license: 'IEEE / Articulate Software SUMO licence (permissive; redistribution + derivative works permitted with IEEE attribution)',
  licenseVerdict: 'REDISTRIBUTABLE: the IEEE licence header in each .kif grants a "perpetual, non-exclusive, royalty-free, world-wide right and license to copy, publish and distribute the Document in any way, and to prepare derivative works ... provided that the IEEE is appropriately acknowledged as the source and copyright owner." Derived records may be redistributed with IEEE attribution. NOT public domain (IEEE remains copyright holder).',
};

export const FILES = [
  { file: 'Merge.kif', tag: 'M', sha256: '532d9b2c6f0ab2309c58c72ca9b137e896474a8637a711c5fda09f96a235c307', role: 'SUMO upper ontology' },
  { file: 'Mid-level-ontology.kif', tag: 'MILO', sha256: '6bd907c1c2d038a4c0f4b85887dd50dfa84eb311e4265a40ff5cef102368067e', role: 'Mid-Level Ontology (MILO)' },
];

/** Declaration ops whose arg1 is the declared subject term. */
const SUBJECT_ARG1 = new Set([
  'instance', 'subclass', 'subrelation', 'subAttribute', 'domain', 'domainSubclass',
  'range', 'rangeSubclass', 'documentation', 'partition', 'disjointDecomposition',
  'successorClass', 'trichotomizingOn', 'identityElement', 'format',
]);
/** Symmetric declaration ops: every atom arg is a subject. */
const SUBJECT_ALL = new Set(['disjoint', 'contraryAttribute', 'disjointRelation']);

const LOGICAL_HEADS = new Set(['=>', '<=>', 'and', 'or', 'not', 'forall', 'exists', 'equal']);

function sha256(buf) { return createHash('sha256').update(buf).digest('hex'); }
function atomArg(form, i) {
  const a = form.list[i];
  return a && a.atom !== undefined ? a.atom : null;
}

/**
 * Definiendum term(s) of a biconditional, by a PURELY SYNTACTIC pattern (no
 * semantic translation): a SUO-KIF definitional axiom is conventionally
 *   (<=> (instance ?x T) <body>)   -> defines class T
 *   (<=> (T ?a ?b ...) <body>)     -> defines relation/function T
 * We only fire when a whole side matches one of these shapes, so common
 * predicates merely MENTIONED inside a compound side are NOT counted.
 */
function definiendumTerms(form) {
  if (op(form) !== '<=>' || form.list.length !== 3) return [];
  const out = new Set();
  for (const side of [form.list[1], form.list[2]]) {
    if (!side.list) continue;
    const so = op(side);
    if (so === 'instance') { const c = atomArg(side, 2); if (c && isTerm(c)) out.add(c); }
    else if (so && isTerm(so) && !LOGICAL_HEADS.has(so)) out.add(so);
  }
  return [...out];
}
function strArg(form, i) {
  const a = form.list[i];
  return a && a.str !== undefined ? a.str : null;
}

function main() {
  const provenance = {
    source: 'SUMO (Suggested Upper Merged Ontology), SUO-KIF',
    repository: SOURCE.repository,
    commit: SOURCE.commit,
    license: 'IEEE SUMO licence (permissive, attribution)',
    extractor: EXTRACTOR_NAME,
    extractorVersion: EXTRACTOR_VERSION,
    extractionDate: EXTRACTION_DATE,
  };

  const axiomLines = [];
  const terms = new Map(); // term -> record-in-progress
  const axStats = { byForm: {}, total: 0 };
  const sourceFiles = {};
  const fileStats = {};

  function ensureTerm(t) {
    if (!terms.has(t)) {
      terms.set(t, {
        id: `urn:onto-sumo:${t}`, schema: 'kot-sumo/1', semanticStatus: 'AxiomsOnly',
        term: t, axioms: [], annotations: {}, _docLang: null,
        _asSubject: 0, _mentioned: 0, _rules: 0, _bicond: new Set(),
        _flags: { relation: false, klass: false, attribute: false, func: false, instance: false },
      });
    }
    return terms.get(t);
  }

  for (const f of FILES) {
    const path = join(SRC, f.file);
    if (!existsSync(path)) throw new Error(`ERR_SOURCE_MISSING: ${f.file} (re-download per README)`);
    const buf = readFileSync(path);
    const got = sha256(buf);
    if (got !== f.sha256) throw new Error(`ERR_SOURCE_HASH: ${f.file} ${got} != pin ${f.sha256}`);
    sourceFiles[f.file] = `sha256:${f.sha256}`;

    const forms = parseKif(buf.toString('utf8'));
    let ord = 0;
    let fileAx = 0;
    for (const form of forms) {
      if (!form.list) continue; // stray atom at top level (none expected)
      ord++;
      const axId = `urn:onto-sumo:ax-${f.tag}-${ord}`;
      const o = op(form);
      const kif = canonical(form);
      const mentioned = [...mentionedTerms(form)].sort();
      const subject = (o && SUBJECT_ARG1.has(o)) ? atomArg(form, 1)
        : (o === 'termFormat') ? atomArg(form, 2) : null;
      const definienda = definiendumTerms(form);
      const axRec = {
        id: axId, schema: 'kot-sumo/1', semanticStatus: 'AxiomsOnly',
        form: 'sumo-kif-canonical', operator: o, sourceFile: f.file, ordinal: ord,
        subject, terms: mentioned, kif, provenance,
      };
      if (definienda.length) axRec.definienda = definienda;
      axiomLines.push(JSON.stringify(axRec));
      axStats.byForm[o || '(non-atom-head)'] = (axStats.byForm[o || '(non-atom-head)'] || 0) + 1;
      axStats.total++;
      fileAx++;

      // register term mentions / definitional links
      for (const t of mentioned) ensureTerm(t)._mentioned++;
      if (o === '=>' || o === '<=>') for (const t of mentioned) ensureTerm(t)._rules++;
      for (const t of definienda) ensureTerm(t)._bicond.add(axId);

      // structured declaration axioms
      if (o === 'termFormat') {
        const t = atomArg(form, 2); const lang = atomArg(form, 1); const label = strArg(form, 3);
        if (t && isTerm(t) && label) { const r = ensureTerm(t); if (lang === 'EnglishLanguage' || !r.annotations.label) r.annotations.label = label; }
        continue;
      }
      if (o === 'documentation') {
        const t = atomArg(form, 1); const lang = atomArg(form, 2); const doc = strArg(form, 3);
        if (t && isTerm(t) && doc) {
          const r = ensureTerm(t); r._asSubject++;
          // Keep the FIRST documentation, preferring the first EnglishLanguage
          // one (SUMO occasionally ships duplicate docs; be deterministic).
          if (!r.annotations.documentation) { r.annotations.documentation = doc; r._docLang = lang; }
          else if (r._docLang !== 'EnglishLanguage' && lang === 'EnglishLanguage') { r.annotations.documentation = doc; r._docLang = lang; }
        }
        continue;
      }
      if (o && (SUBJECT_ARG1.has(o) || SUBJECT_ALL.has(o))) {
        const subs = SUBJECT_ALL.has(o)
          ? form.list.slice(1).filter((x) => x.atom !== undefined && isTerm(x.atom)).map((x) => x.atom)
          : (subject && isTerm(subject) ? [subject] : []);
        for (const s of subs) {
          const r = ensureTerm(s); r._asSubject++;
          const F = r._flags;
          if (o === 'subclass') { F.klass = true; r.axioms.push({ rel: 'subclass', target: atomArg(form, 2) }); }
          else if (o === 'instance') { F.instance = true; r.axioms.push({ rel: 'instance', target: atomArg(form, 2) }); }
          else if (o === 'subrelation') { F.relation = true; r.axioms.push({ rel: 'subrelation', target: atomArg(form, 2) }); }
          else if (o === 'subAttribute') { F.attribute = true; r.axioms.push({ rel: 'subAttribute', target: atomArg(form, 2) }); }
          else if (o === 'domain') { F.relation = true; r.axioms.push({ rel: 'domain', argIndex: atomArg(form, 2), class: atomArg(form, 3) }); }
          else if (o === 'domainSubclass') { F.relation = true; r.axioms.push({ rel: 'domainSubclass', argIndex: atomArg(form, 2), class: atomArg(form, 3) }); }
          else if (o === 'range') { F.relation = true; r.axioms.push({ rel: 'range', class: atomArg(form, 2) }); }
          else if (o === 'rangeSubclass') { F.relation = true; r.axioms.push({ rel: 'rangeSubclass', class: atomArg(form, 2) }); }
          else if (o === 'partition' || o === 'disjointDecomposition') { F.klass = true; r.axioms.push({ rel: o, members: form.list.slice(2).filter((x) => x.atom !== undefined).map((x) => x.atom) }); }
          else if (o === 'disjoint') { F.klass = true; r.axioms.push({ rel: 'disjoint', with: subs.filter((x) => x !== s) }); }
          else if (o === 'contraryAttribute') { F.attribute = true; r.axioms.push({ rel: 'contraryAttribute', with: subs.filter((x) => x !== s) }); }
          else r.axioms.push({ rel: o, target: atomArg(form, 2) });
        }
      }
    }
    fileStats[f.file] = { role: f.role, axioms: fileAx };
  }

  // finalise term records: only emit terms SUMO declares (asSubject > 0).
  const termLines = [];
  const termStats = { records: 0, byKind: {}, withDoc: 0, withBiconditionalDef: 0, danglingTargets: 0 };
  const emitted = new Set();
  // first pass: which terms are emitted (declared)
  for (const [t, r] of terms) if (r._asSubject > 0) emitted.add(t);

  for (const [t, r] of terms) {
    if (r._asSubject === 0) continue; // referenced-only; captured via axioms.jsonl
    const F = r._flags;
    const kind = F.relation ? 'relation' : F.func ? 'function' : F.attribute ? 'attribute'
      : F.klass ? 'class' : F.instance ? 'instance' : 'term';
    const rec = {
      id: r.id, schema: r.schema, semanticStatus: r.semanticStatus, term: t, kind,
      axioms: r.axioms,
    };
    const bicond = [...r._bicond].sort();
    if (bicond.length) rec.definitionalAxiomRefs = bicond;
    rec.axiomStats = { asSubject: r._asSubject, mentionedIn: r._mentioned, ruleMentions: r._rules, biconditionalDefs: bicond.length };
    rec.annotations = r.annotations;
    rec.provenance = provenance;
    termLines.push(JSON.stringify(rec));
    termStats.records++;
    termStats.byKind[kind] = (termStats.byKind[kind] || 0) + 1;
    if (r.annotations.documentation) termStats.withDoc++;
    if (bicond.length) termStats.withBiconditionalDef++;
  }
  // dangling structured-axiom targets (declared-term references to undeclared terms)
  for (const line of termLines) {
    const rec = JSON.parse(line);
    for (const ax of rec.axioms) {
      const tgts = [ax.target, ax.class, ...(ax.members || []), ...(ax.with || [])].filter(Boolean);
      for (const tg of tgts) if (isTerm(tg) && !emitted.has(tg)) termStats.danglingTargets++;
    }
  }

  const termsText = termLines.join('\n') + '\n';
  const axiomsText = axiomLines.join('\n') + '\n';
  writeFileSync(join(ROOT, 'terms.jsonl'), termsText);
  writeFileSync(join(ROOT, 'axioms.jsonl'), axiomsText);

  const manifest = {
    corpus: 'onto-sumo',
    schema: 'kot-sumo/1',
    version: EXTRACTOR_VERSION,
    semanticStatus: 'AxiomsOnly',
    statusNote:
      'SUMO SUO-KIF statements as canonical one-line strings (form:"sumo-kif-canonical") + a declared-term inventory with '
      + 'structured declaration axioms. NO semantic translation, NO semantic-adequacy claim. SUMO\'s <=> biconditional axioms '
      + 'are its genuinely-definitional statements (analogous to set.mm df-*) and are linked from each term they define. '
      + 'documentation/termFormat are annotations OUTSIDE identity. Not a mapper/pre-registration surface.',
    subsetRule: 'Merge.kif (SUMO upper ontology) + Mid-level-ontology.kif (MILO) only — SUMO\'s language-independent definitional core. The ~100 domain .kif files are out of scope for this ingestion (follow-up filed).',
    source: SOURCE,
    extractor: {
      name: EXTRACTOR_NAME, version: EXTRACTOR_VERSION,
      files: ['parse-kif.mjs', 'extract.mjs'], contentHash: extractorContentHash(),
      hashRule: 'sha256 over concatenated bytes of listed files, in listed order',
    },
    extractionDate: EXTRACTION_DATE,
    sourceFiles,
    files: { 'terms.jsonl': termLines.length, 'axioms.jsonl': axiomLines.length },
    perFile: fileStats,
    axiomStats: axStats,
    termStats,
    shards: {
      'terms.jsonl': { records: termLines.length, bytes: Buffer.byteLength(termsText), sha256: sha256(termsText) },
      'axioms.jsonl': { records: axiomLines.length, bytes: Buffer.byteLength(axiomsText), sha256: sha256(axiomsText) },
    },
  };
  writeFileSync(join(ROOT, 'manifest.json'), JSON.stringify(manifest, null, 2) + '\n');

  console.log(`onto-sumo: ${axiomLines.length} KIF axioms, ${termLines.length} declared terms`);
  console.log(`  terms by kind: ${Object.entries(termStats.byKind).map(([k, v]) => `${k}:${v}`).join(', ')}`);
  console.log(`  withDocumentation=${termStats.withDoc}, withBiconditionalDef=${termStats.withBiconditionalDef}, danglingTargets=${termStats.danglingTargets}`);
  console.log(`  axiom forms: ${Object.entries(axStats.byForm).sort((a, b) => b[1] - a[1]).slice(0, 10).map(([k, v]) => `${k}:${v}`).join(', ')}`);
}

export function extractorContentHash() {
  const here = dirname(fileURLToPath(import.meta.url));
  const h = createHash('sha256');
  for (const f of ['parse-kif.mjs', 'extract.mjs']) h.update(readFileSync(join(here, f)));
  return h.digest('hex');
}

if (import.meta.url === `file://${process.argv[1]}`) main();
