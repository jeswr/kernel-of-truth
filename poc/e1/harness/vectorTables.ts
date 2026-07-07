/**
 * E1 vector tables at d_model = 512 (docs/poc-design.md E1 + Common rules
 * 2-4; bead kernel-of-truth-bk0).
 *
 * Emits inputs/vector-tables-d512.json with the four pre-registered tables:
 *
 *   kernel        — kot-enc-Bq/1 @ D=512 vectors for the 54 kernel-v0
 *                   concepts (toy-native dimension policy, path (i)).
 *                   Encoder hash VERIFIED against the pin in poc-design.md
 *                   line "PINNED (2026-07-07...)"; mismatch fails closed.
 *   kernelInit    — the SAME vectors, stamped for the kernel-init-TRAINABLE
 *                   arm (MINOR 20: separates "head start that washes out"
 *                   from "content + fixedness"). Stored by reference
 *                   (identical floats, no duplication).
 *   shuffled      — same vectors, seeded permutation of the concept<->vector
 *                   assignment (BLOCKER 2 control: isolates assignment
 *                   correctness). One permutation per experiment seed 0..4;
 *                   each is checked to be a DERANGEMENT (no concept keeps its
 *                   own vector); a fixed point triggers a deterministic
 *                   labelled redraw, recorded in the artifact.
 *   randomFrozen  — i.i.d. N(0, INIT_STD^2) per element, the documented
 *                   trainable-arm init distribution (Common rule 4
 *                   "norm-matched to the trainable arm's init distribution");
 *                   one table per experiment seed 0..4, Box-Muller over the
 *                   encoder's own DetStream (bit-reproducible).
 *
 * SCALE POLICY (pre-registered here, applied by train_e1.py at load time):
 * encoder vectors are unit-norm; trainable init rows have E[||row||] =
 * INIT_STD*sqrt(D) ~= 0.4525. Kernel/kernelInit/shuffled rows are multiplied
 * by INIT_STD*sqrt(D) at load so that ALL arms' concept rows live at the same
 * norm scale — otherwise kernel-vs-random/trainable comparisons would be
 * confounded by trivial row-norm mismatch. The primary comparison
 * (kernel vs shuffled) is norm-identical under any choice; this affects only
 * secondary arms and is flagged in poc/e1/README.md.
 */

import {
  DetStream,
  QUASI_DIMS,
  encodeConceptSetQ,
  encoderContentHashQ,
} from '@jeswr/kernel-encoder';
import type { Explication } from '@jeswr/kernel-encoder';
import { readFileSync, readdirSync } from 'node:fs';
import { join } from 'node:path';
import {
  E1_D_MODEL,
  INIT_STD,
  KERNEL_V0_DIR,
  PINNED_BQ512_HASH,
  corpusPin,
  isMain,
  writeInput,
} from './common.js';

export const N_SEEDS = 5;

/** Round to float32 precision: python loads these as float32; make the JSON exact. */
function f32(x: number): number {
  return Math.fround(x);
}

/** Seeded derangement of [0,n) via the encoder's DetStream (Fisher-Yates + labelled redraws). */
export function seededDerangement(
  baseLabel: string,
  n: number,
): { perm: number[]; label: string; redraws: number } {
  for (let attempt = 0; ; attempt++) {
    const label = attempt === 0 ? baseLabel : `${baseLabel}/retry${attempt}`;
    const stream = new DetStream(`perm/${label}`);
    const p = Array.from({ length: n }, (_, i) => i);
    for (let i = n - 1; i > 0; i--) {
      const j = stream.nextBelow(i + 1);
      const t = p[i]!;
      p[i] = p[j]!;
      p[j] = t;
    }
    if (p.every((v, i) => v !== i)) return { perm: p, label, redraws: attempt };
  }
}

/** Deterministic N(0, std^2) matrix via Box-Muller over DetStream floats. */
export function seededGaussianRows(
  label: string,
  rows: number,
  cols: number,
  std: number,
): number[][] {
  const stream = new DetStream(label);
  const out: number[][] = [];
  let spare: number | null = null;
  const next = (): number => {
    if (spare !== null) {
      const v = spare;
      spare = null;
      return v;
    }
    // Box-Muller; u1 in (0,1] to avoid log(0).
    const u1 = 1 - stream.nextFloat();
    const u2 = stream.nextFloat();
    const r = Math.sqrt(-2 * Math.log(u1));
    spare = r * Math.sin(2 * Math.PI * u2);
    return r * Math.cos(2 * Math.PI * u2);
  };
  for (let i = 0; i < rows; i++) {
    const row: number[] = [];
    for (let j = 0; j < cols; j++) row.push(f32(next() * std));
    out.push(row);
  }
  return out;
}

function main(): void {
  const D = E1_D_MODEL;
  if (!(QUASI_DIMS as readonly number[]).includes(D)) {
    throw new Error(`ERR_DIMENSION: E1 d_model=${D} is not a pre-registered toy-native dimension`);
  }

  // ---- encoder pin verification (Common rule 2) — FAIL CLOSED on mismatch --
  const hash = encoderContentHashQ({ D });
  if (hash !== PINNED_BQ512_HASH) {
    throw new Error(
      `ERR_ENCODER_PIN: kot-enc-Bq/1@${D} content-hash ${hash} != pinned ${PINNED_BQ512_HASH} ` +
        '(docs/poc-design.md Common rule 2) — any E-run against a different encoder hash is a NEW pre-registration',
    );
  }

  // ---- encode the 54 concepts at D=512 (reference DAG; alphabetical ids) --
  const dir = join(KERNEL_V0_DIR, 'concepts');
  const files = readdirSync(dir).filter((f) => f.endsWith('.json')).sort();
  const defs = new Map<string, Explication>();
  for (const f of files) {
    const rec = JSON.parse(readFileSync(join(dir, f), 'utf8')) as {
      id: string;
      explication: Explication;
    };
    defs.set(rec.id, rec.explication);
  }
  console.log(`encoding ${defs.size} concepts at D=${D} (kot-enc-Bq/1, encodeConceptSetQ)`);
  const { vectors } = encodeConceptSetQ(defs, { params: { D } });
  const ids = [...defs.keys()].sort();
  const kernel = ids.map((id) => {
    const v = vectors.get(id);
    if (v === undefined) throw new Error(`no vector for ${id}`);
    const n = Math.sqrt(v.reduce((a, x) => a + x * x, 0));
    if (Math.abs(n - 1) > 1e-9) throw new Error(`ERR_NORM: ${id} has norm ${n}, expected unit`);
    return [...v].map(f32);
  });

  // ---- controls ------------------------------------------------------------
  const shuffled: { seed: number; label: string; redraws: number; perm: number[] }[] = [];
  for (let s = 0; s < N_SEEDS; s++) {
    const { perm, label, redraws } = seededDerangement(`e1/shuffle/${s}`, ids.length);
    shuffled.push({ seed: s, label, redraws, perm });
  }
  const randomFrozen: { seed: number; label: string; rows: number[][] }[] = [];
  for (let s = 0; s < N_SEEDS; s++) {
    const label = `e1/randfrozen/${s}`;
    randomFrozen.push({ seed: s, label, rows: seededGaussianRows(label, ids.length, D, INIT_STD) });
  }

  const frozenScale = INIT_STD * Math.sqrt(D);
  writeInput('vector-tables-d512.json', {
    artifact: 'e1-vector-tables',
    date: new Date().toISOString(),
    D,
    algorithmVersion: 'kot-enc-Bq/1',
    encoderContentHashQ: hash,
    pinnedHash: PINNED_BQ512_HASH,
    kernelV0: corpusPin(),
    initStd: INIT_STD,
    frozenScale,
    scalePolicy:
      `kernel/kernelInit/shuffled rows are unit-norm here and are multiplied by ` +
      `frozenScale = initStd*sqrt(D) = ${frozenScale} at load time (train_e1.py) so all arms' ` +
      `concept rows share the trainable-init norm scale; randomFrozen rows are stored at ` +
      `their natural N(0, initStd^2) draw (norm-matched in distribution, not per-row)`,
    ids,
    precision: 'float32 (Math.fround applied; python loads as float32 bit-exactly)',
    kernel,
    kernelInit: {
      note:
        'kernel-init-TRAINABLE arm (MINOR 20) uses the SAME vectors as `kernel` — stored by ' +
        'reference to avoid duplication; the arm differs only in trainability',
      tableRef: 'kernel',
    },
    shuffled: shuffled.map((s) => ({
      ...s,
      note: 'row i of the shuffled table = kernel[perm[i]]; derangement (no fixed points) enforced',
    })),
    randomFrozen,
  });

  // quick stats for the log
  const meanRandNorm =
    randomFrozen[0]!.rows.reduce((a, r) => a + Math.sqrt(r.reduce((x, y) => x + y * y, 0)), 0) /
    ids.length;
  console.log(
    `kernel rows unit-norm; frozenScale=${frozenScale.toFixed(6)}; ` +
      `randomFrozen seed0 mean row norm=${meanRandNorm.toFixed(6)}`,
  );
}

if (isMain(import.meta.url)) main();
