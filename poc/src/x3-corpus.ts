/**
 * X3 on the AUTHORED kernel-v0 corpus (bead kernel-of-truth-138): the polarity
 * pathology + weighting-sensitivity numbers of poc-design X3, measured on
 * authored data, with one corpus-specific sharpening — meaning-INVERTING
 * single edits are compared against the corpus's OWN nearest distinct pairs
 * (the give/take/gift cluster): the pathology is quantified as how many
 * inverting edits leave a concept CLOSER to its edited self than the two
 * nearest genuinely-different authored concepts are to each other.
 *
 * The four edit constructors are copied verbatim from poc/harness/x3.ts
 * (module-private there, and importing that file would execute its synthetic
 * main(); the no-modification rule for existing harnesses keeps them
 * unexported). Provenance: poc/harness/x3.ts notWrap/polarityFlip/
 * alphaRename/modsReorder.
 *
 * No pass/fail criterion — measurement deliverable, as pre-registered.
 * Writes results/x3-kernel-v0-report.{json,md} — never x3-report.*.
 */

import {
  encodeConceptSet,
  encodeExplication,
  validateExplication,
  canonicalJson,
  encoderContentHash,
  SeededRng,
  type Explication,
  type Clause,
  type EncoderParams,
} from '@jeswr/kernel-encoder';
import { cosine, fmt, spearman, summarise } from '../harness/common.js';
import { corpusStamp, loadCorpus, slug, stampMd, writeCorpusReport } from './corpus-common.js';

type Mutable = { [k: string]: unknown };

function deepClone<T>(x: T): T {
  return JSON.parse(JSON.stringify(x)) as T;
}

/** Meaning-inverting: wrap top-level clause i in NOT. Null if caps would break. (= harness/x3.ts) */
function notWrap(e: Explication, rng: SeededRng): Explication | null {
  const clone = deepClone(e) as unknown as Mutable;
  const clauses = clone.clauses as Clause[];
  const i = rng.int(clauses.length);
  clauses[i] = { type: 'op', op: 'NOT', args: [clauses[i]!] };
  try {
    validateExplication(clone as unknown as Explication);
    return clone as unknown as Explication;
  } catch {
    return null;
  }
}

/** Meaning-inverting: flip one WANT<->DON'T-WANT or GOOD<->BAD occurrence. (= harness/x3.ts) */
function polarityFlip(e: Explication, rng: SeededRng): Explication | null {
  const clone = deepClone(e);
  const hits: (() => void)[] = [];
  const walk = (node: unknown): void => {
    if (node === null || typeof node !== 'object') return;
    if (Array.isArray(node)) {
      node.forEach(walk);
      return;
    }
    const obj = node as Mutable;
    if (obj.type === 'pred' && (obj.pred === 'WANT' || obj.pred === "DON'T-WANT")) {
      hits.push(() => {
        obj.pred = obj.pred === 'WANT' ? "DON'T-WANT" : 'WANT';
      });
    }
    if (obj.kind === 'prime' && (obj.prime === 'GOOD' || obj.prime === 'BAD')) {
      hits.push(() => {
        obj.prime = obj.prime === 'GOOD' ? 'BAD' : 'GOOD';
      });
    }
    if (typeof obj.mod === 'string' && (obj.mod === 'GOOD' || obj.mod === 'BAD')) {
      hits.push(() => {
        obj.mod = obj.mod === 'GOOD' ? 'BAD' : 'GOOD';
      });
    }
    for (const v of Object.values(obj)) walk(v);
  };
  walk(clone);
  if (hits.length === 0) return null;
  hits[rng.int(hits.length)]!();
  try {
    validateExplication(clone);
    return canonicalJson(clone) === canonicalJson(e) ? null : clone;
  } catch {
    return null;
  }
}

/** Meaning-preserving: swap two non-frame-implicit referent indices everywhere. (= harness/x3.ts) */
function alphaRename(e: Explication, rng: SeededRng): Explication | null {
  const implicit = e.frame === 'RelationalSchema' ? 2 : 1;
  const free = e.referents.filter((r) => r.index > implicit).map((r) => r.index);
  if (free.length < 2) return null;
  const a = free[rng.int(free.length)]!;
  let b = a;
  while (b === a) b = free[rng.int(free.length)]!;
  const clone = deepClone(e);
  const swapIdx = (n: number): number => (n === a ? b : n === b ? a : n);
  const walk = (node: unknown): void => {
    if (node === null || typeof node !== 'object') return;
    if (Array.isArray(node)) {
      node.forEach(walk);
      return;
    }
    const obj = node as Mutable;
    if (typeof obj.index === 'number' && (obj.kind === 'ref' || obj.kind === 'refHead')) {
      obj.index = swapIdx(obj.index);
    }
    if (typeof obj.bind === 'number') obj.bind = swapIdx(obj.bind);
    for (const v of Object.values(obj)) walk(v);
  };
  walk((clone as unknown as Mutable).clauses);
  const decls = (clone as unknown as Mutable).referents as { index: number; refKind: string }[];
  const ka = decls.find((r) => r.index === a)!;
  const kb = decls.find((r) => r.index === b)!;
  const t = ka.refKind;
  ka.refKind = kb.refKind;
  kb.refKind = t;
  try {
    validateExplication(clone);
    return canonicalJson(clone) === canonicalJson(e) ? null : clone;
  } catch {
    return null;
  }
}

/** Meaning-preserving (serialisation-level): reverse a >=2-element mods list. (= harness/x3.ts) */
function modsReorder(e: Explication): Explication | null {
  const clone = deepClone(e);
  let done = false;
  const walk = (node: unknown): void => {
    if (done || node === null || typeof node !== 'object') return;
    if (Array.isArray(node)) {
      node.forEach(walk);
      return;
    }
    const obj = node as Mutable;
    if (Array.isArray(obj.mods) && obj.mods.length >= 2) {
      obj.mods = [...(obj.mods as unknown[])].reverse();
      done = true;
      return;
    }
    for (const v of Object.values(obj)) walk(v);
  };
  walk(clone);
  return done ? clone : null;
}

const EDIT_KEYS = ['notWrap', 'polarityFlip', 'alphaRename', 'modsReorder'] as const;
type EditKey = (typeof EDIT_KEYS)[number];

function main(): void {
  const corpus = loadCorpus();
  const docs = corpus.docs;
  console.log(`X3-corpus: ${docs.length} authored concepts`);

  const paramSweep: Partial<EncoderParams>[] = [
    {}, // default (alphaStruct 1, notBoost 1) — the pinned setting
    { alphaStruct: 0.5 },
    { alphaStruct: 2.0 },
    { notBoost: 2.0 },
    { notBoost: 4.0 },
  ];
  const paramName = (p: Partial<EncoderParams>): string =>
    Object.keys(p).length === 0 ? 'default' : Object.entries(p).map(([k, v]) => `${k}=${v}`).join(',');

  // Edits precomputed once (param-independent), seeded as in harness/x3.ts.
  const rng = new SeededRng('x3-corpus-edits');
  const edited = docs.map((d) => ({
    notWrap: notWrap(d.explication, rng),
    polarityFlip: polarityFlip(d.explication, rng),
    alphaRename: alphaRename(d.explication, rng),
    modsReorder: modsReorder(d.explication),
  }));

  type Shifts = Record<EditKey, { id: string; cos: number }[]>;
  const perParam: Record<string, Shifts & { rdmSpearmanVsDefault: number | null }> = {};
  let defaultVecs: Map<string, Float64Array> | null = null;
  let defaultRdm: number[] | null = null;

  for (const p of paramSweep) {
    const name = paramName(p);
    console.log(`X3-corpus: params ${name}`);
    // Whole-corpus encode under these params (reference vectors re-derived
    // under the SAME params — encodeConceptSet threads opts through).
    const { vectors } = encodeConceptSet(corpus.defs, { params: p });
    const shifts: Shifts = { notWrap: [], polarityFlip: [], alphaRename: [], modsReorder: [] };
    for (let i = 0; i < docs.length; i++) {
      for (const key of EDIT_KEYS) {
        const ed = edited[i]![key];
        if (ed === null) continue;
        const vm = encodeExplication(ed, { params: p, concepts: vectors });
        shifts[key].push({ id: docs[i]!.id, cos: cosine(vectors.get(docs[i]!.id)!, vm) });
      }
    }
    const rdm: number[] = [];
    const ids = docs.map((d) => d.id);
    for (let i = 0; i < ids.length; i++) {
      for (let j = i + 1; j < ids.length; j++) rdm.push(cosine(vectors.get(ids[i]!)!, vectors.get(ids[j]!)!));
    }
    let rho: number | null = null;
    if (defaultVecs === null) {
      defaultVecs = vectors;
      defaultRdm = rdm;
    } else {
      rho = spearman(defaultRdm!, rdm);
    }
    perParam[name] = { ...shifts, rdmSpearmanVsDefault: rho };
  }

  // --- corpus-specific: inverting edits vs the corpus's own near-pairs ------
  const ids = docs.map((d) => d.id);
  const pairs: { a: string; b: string; cos: number }[] = [];
  for (let i = 0; i < ids.length; i++) {
    for (let j = i + 1; j < ids.length; j++) {
      pairs.push({ a: ids[i]!, b: ids[j]!, cos: cosine(defaultVecs!.get(ids[i]!)!, defaultVecs!.get(ids[j]!)!) });
    }
  }
  pairs.sort((x, y) => y.cos - x.cos);
  const nearest = pairs[0]!;
  const def = perParam['default']!;
  const inverting = [...def.notWrap, ...def.polarityFlip];
  const preserving = [...def.alphaRename, ...def.modsReorder];
  const worseThanNearestPair = inverting.filter((s) => s.cos > nearest.cos);

  const sum = (xs: { cos: number }[]) => (xs.length > 0 ? summarise(xs.map((x) => x.cos)) : null);
  const stamp = corpusStamp(corpus, encoderContentHash());
  const json = {
    ...stamp,
    suite: 'X3-corpus: polarity pathology + weighting sensitivity on authored kernel-v0',
    editCounts: Object.fromEntries(EDIT_KEYS.map((k) => [k, edited.filter((e) => e[k] !== null).length])),
    perParam: Object.fromEntries(
      Object.entries(perParam).map(([k, v]) => [
        k,
        {
          cosineAfterEdit: Object.fromEntries(EDIT_KEYS.map((key) => [key, sum(v[key])])),
          rdmSpearmanVsDefault: v.rdmSpearmanVsDefault,
        },
      ]),
    ),
    nearPairComparison: {
      nearestDistinctPair: nearest,
      top5NearestPairs: pairs.slice(0, 5),
      invertingEdits: inverting.length,
      invertingEditsCloserThanNearestPair: worseThanNearestPair.length,
      offendingConcepts: worseThanNearestPair.map((s) => ({ id: slug(s.id), cos: s.cos })).sort((a, b) => b.cos - a.cos),
      invertingSummary: sum(inverting),
      preservingSummary: sum(preserving),
    },
    reading:
      'cosineAfterEdit close to 1 = edit barely moves the vector. The pathology on authored data: ' +
      'every meaning-INVERTING single edit whose cosine exceeds the nearest distinct authored pair ' +
      "(give<->take cluster) means kernel similarity ranks 'concept vs its own negation' as MORE similar " +
      'than the two closest genuinely-different concepts. notBoost>1 must widen inverting shifts without ' +
      'degrading the rest of the geometry (rdmSpearmanVsDefault) to count as dominating.',
  };

  const table = (name: string): string => {
    const v = json.perParam[name]!;
    const c = v.cosineAfterEdit as Record<EditKey, ReturnType<typeof sum>>;
    const row = (lbl: string, s: ReturnType<typeof sum>) =>
      s === null ? `| ${lbl} | - | - | - | - |` : `| ${lbl} | ${s.n} | ${fmt(s.min)} | ${fmt(s.median)} | ${fmt(s.max)} |`;
    return [
      `### params: ${name}${v.rdmSpearmanVsDefault !== null ? ` (RDM Spearman vs default: ${fmt(v.rdmSpearmanVsDefault as number)})` : ''}`,
      '',
      '| edit class | n | min cos | median cos | max cos |',
      '|---|---|---|---|---|',
      row('NOT-wrap (inverting)', c.notWrap),
      row('polarity flip (inverting)', c.polarityFlip),
      row('alpha-rename (preserving)', c.alphaRename),
      row('mods reorder (preserving)', c.modsReorder),
      '',
    ].join('\n');
  };
  const md = [
    '# X3 on kernel-v0 — polarity pathology + weighting sensitivity',
    '',
    ...stampMd(stamp),
    '',
    ...Object.keys(json.perParam).map(table),
    '## Inverting edits vs the corpus\'s own near-pairs (default params)',
    '',
    `- nearest distinct authored pair: \`${slug(nearest.a)}\` <-> \`${slug(nearest.b)}\` at cos ${fmt(nearest.cos)}`,
    ...pairs.slice(1, 5).map((p, i) => `  - next: \`${slug(p.a)}\` <-> \`${slug(p.b)}\` cos ${fmt(p.cos)} (#${i + 2})`),
    `- meaning-inverting single edits measured: ${inverting.length}; of these, ` +
      `**${worseThanNearestPair.length} sit CLOSER to their original than the nearest distinct pair does**`,
    `- inverting-edit cosine: min ${fmt(json.nearPairComparison.invertingSummary!.min)}, ` +
      `median ${fmt(json.nearPairComparison.invertingSummary!.median)}, max ${fmt(json.nearPairComparison.invertingSummary!.max)}`,
    `- preserving-edit cosine: min ${fmt(json.nearPairComparison.preservingSummary!.min)}, ` +
      `median ${fmt(json.nearPairComparison.preservingSummary!.median)}, max ${fmt(json.nearPairComparison.preservingSummary!.max)}`,
    '',
    ...(worseThanNearestPair.length > 0
      ? [
          '| concept (inverting edit) | cos after edit |',
          '|---|---|',
          ...json.nearPairComparison.offendingConcepts.map((o) => `| ${o.id} | ${fmt(o.cos)} |`),
          '',
        ]
      : []),
    `> ${json.reading}`,
    '',
    '> Consumers of kernel similarity remain BANNED (architecture.md §1.2, panel O9)',
    '> until a polarity-aware variant dominates on these measurements.',
  ].join('\n');
  writeCorpusReport('x3-kernel-v0-report', json, md);
  console.log('X3-corpus done (measurement deliverable; no pass/fail).');
}

main();
