/**
 * X3 — similarity pathology, documentation (poc-design.md Phase X; the two
 * known weaknesses of architecture.md §1.2):
 *
 *  1. POLARITY: cosine shift under meaning-INVERTING single edits (NOT-wrap
 *     of a clause; WANT<->DON'T-WANT; GOOD<->BAD) vs meaning-PRESERVING edits
 *     (referent alpha-renaming — DRT indices are arbitrary labels; mods-list
 *     reorder — pure serialisation order). The pathology to document: the
 *     inverting shifts are small relative to how much they invert meaning.
 *  2. WEIGHTING SENSITIVITY: the superposition weighting free parameters
 *     (alphaStruct, notBoost) are pinned by content-hash; this harness
 *     measures how much the geometry moves as they move (RDM Spearman vs the
 *     default), and whether notBoost (the simple polarity-aware variant)
 *     widens the NOT-edit shift, i.e. "a variant must dominate before any
 *     consumer uses kernel similarity" (poc-design X3).
 *
 * No pass/fail criterion — this is a measurement deliverable.
 */

import {
  encodeExplication,
  generateExplication,
  validateExplication,
  canonicalJson,
  encoderContentHash,
  SeededRng,
  type Explication,
  type Clause,
  type EncoderParams,
} from '@jeswr/kernel-encoder';
import { argValue, cosine, ensureDirs, fmt, spearman, summarise, writeReport } from './common.js';

type Mutable = { [k: string]: unknown };

function deepClone<T>(x: T): T {
  return JSON.parse(JSON.stringify(x)) as T;
}

/** Meaning-inverting: wrap top-level clause i in NOT. Null if caps would break. */
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

/** Meaning-inverting: flip one WANT<->DON'T-WANT or GOOD<->BAD occurrence. */
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

/** Meaning-preserving: swap two non-frame-implicit referent indices everywhere. */
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
  // Swap the declared kinds so declaration i keeps index i (dense list).
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
    return null; // introduction-order constraints can break; skip
  }
}

/** Meaning-preserving (serialisation-level): reverse a >=2-element mods list. */
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

function main(): void {
  ensureDirs();
  const m = Number(argValue('--n') ?? 200);
  const corpus: Explication[] = [];
  for (let i = 0; i < m; i++) {
    const tc = [2, 3, 4, 6, 8][i % 5]!;
    const dep = [1, 2, 2, 3, 4][Math.floor(i / 5) % 5]!;
    corpus.push(generateExplication({ seed: `x3/${i}`, topClauses: tc, depth: dep }));
  }
  const paramSweep: Partial<EncoderParams>[] = [
    {}, // default (alphaStruct 1, notBoost 1) — the pinned setting
    { alphaStruct: 0.5 },
    { alphaStruct: 2.0 },
    { notBoost: 2.0 },
    { notBoost: 4.0 },
  ];
  const paramName = (p: Partial<EncoderParams>): string =>
    Object.keys(p).length === 0 ? 'default' : Object.entries(p).map(([k, v]) => `${k}=${v}`).join(',');

  interface EditShifts {
    notWrap: number[];
    polarityFlip: number[];
    alphaRename: number[];
    modsReorder: number[];
  }
  const perParam: Record<string, EditShifts & { rdmSpearmanVsDefault: number | null }> = {};

  // Precompute edited ASTs once (edits are param-independent).
  const rng = new SeededRng('x3-edits');
  const edited = corpus.map((e) => ({
    notWrap: notWrap(e, rng),
    polarityFlip: polarityFlip(e, rng),
    alphaRename: alphaRename(e, rng),
    modsReorder: modsReorder(e),
  }));

  let defaultVecs: Float64Array[] | null = null;
  for (const p of paramSweep) {
    const name = paramName(p);
    console.log(`X3: params ${name}`);
    const vecs = corpus.map((e) => encodeExplication(e, { params: p }));
    const shifts: EditShifts = { notWrap: [], polarityFlip: [], alphaRename: [], modsReorder: [] };
    for (let i = 0; i < corpus.length; i++) {
      for (const key of ['notWrap', 'polarityFlip', 'alphaRename', 'modsReorder'] as const) {
        const ed = edited[i]![key];
        if (ed === null) continue;
        shifts[key].push(cosine(vecs[i]!, encodeExplication(ed, { params: p })));
      }
    }
    // RDM Spearman vs default geometry (how much the free parameter moves similarity).
    let rho: number | null = null;
    if (defaultVecs === null) {
      defaultVecs = vecs;
    } else {
      const rdmA: number[] = [];
      const rdmB: number[] = [];
      for (let i = 0; i < vecs.length; i++) {
        for (let j = i + 1; j < vecs.length; j++) {
          rdmA.push(cosine(defaultVecs[i]!, defaultVecs[j]!));
          rdmB.push(cosine(vecs[i]!, vecs[j]!));
        }
      }
      rho = spearman(rdmA, rdmB);
    }
    perParam[name] = { ...shifts, rdmSpearmanVsDefault: rho };
  }

  const sum = (xs: number[]) => (xs.length > 0 ? summarise(xs) : null);
  const json = {
    date: new Date().toISOString(),
    encoderContentHash: encoderContentHash(),
    corpus: m,
    editCounts: {
      notWrap: edited.filter((e) => e.notWrap !== null).length,
      polarityFlip: edited.filter((e) => e.polarityFlip !== null).length,
      alphaRename: edited.filter((e) => e.alphaRename !== null).length,
      modsReorder: edited.filter((e) => e.modsReorder !== null).length,
    },
    perParam: Object.fromEntries(
      Object.entries(perParam).map(([k, v]) => [
        k,
        {
          cosineAfterEdit: {
            notWrap: sum(v.notWrap),
            polarityFlip: sum(v.polarityFlip),
            alphaRename: sum(v.alphaRename),
            modsReorder: sum(v.modsReorder),
          },
          rdmSpearmanVsDefault: v.rdmSpearmanVsDefault,
        },
      ]),
    ),
    reading:
      'cosineAfterEdit close to 1 = edit barely moves the vector. The pathology is documented if ' +
      'meaning-INVERTING edits (notWrap/polarityFlip) sit near meaning-PRESERVING ones (alphaRename). ' +
      'A polarity-aware variant (notBoost>1) must push inverting edits further from 1 WITHOUT degrading ' +
      'the rest of the geometry (rdmSpearmanVsDefault) to count as dominating.',
  };
  const table = (name: string): string => {
    const v = json.perParam[name]!;
    const c = v.cosineAfterEdit;
    const row = (lbl: string, s: ReturnType<typeof sum>) =>
      s === null ? `| ${lbl} | - | - | - | - |` : `| ${lbl} | ${s.n} | ${fmt(s.min)} | ${fmt(s.median)} | ${fmt(s.max)} |`;
    return [
      `### params: ${name}${v.rdmSpearmanVsDefault !== null ? ` (RDM Spearman vs default: ${fmt(v.rdmSpearmanVsDefault)})` : ''}`,
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
    '# X3 — polarity pathology + weighting sensitivity (documentation)',
    '',
    `date: ${json.date}`,
    `encoder content-hash: \`${json.encoderContentHash}\` (weighting params pinned therein)`,
    `corpus: ${m} synthetics`,
    '',
    ...Object.keys(json.perParam).map(table),
    `> ${json.reading}`,
    '',
    '> Consumers of kernel similarity remain BANNED (architecture.md §1.2, panel O9)',
    '> until a polarity-aware variant dominates on these measurements.',
  ].join('\n');
  writeReport('x3-report', json, md);
  console.log('X3 done (measurement deliverable; no pass/fail).');
}

main();
