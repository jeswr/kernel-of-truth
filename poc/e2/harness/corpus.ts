/** Load the kernel-v0 corpus (read-only; the brief forbids modifying it). */

import { readFileSync, readdirSync } from 'node:fs';
import { join } from 'node:path';
import type { Explication } from '@jeswr/kernel-encoder';
import { KERNEL_V0_DIR } from './common.js';

export interface ConceptRecord {
  readonly id: string;
  readonly label: string;
  readonly gloss: string;
  readonly references: readonly string[];
  readonly explication: Explication;
}

export function loadCorpus(): ConceptRecord[] {
  const dir = join(KERNEL_V0_DIR, 'concepts');
  const files = readdirSync(dir).filter((f) => f.endsWith('.json')).sort();
  return files.map((f) => JSON.parse(readFileSync(join(dir, f), 'utf8')) as ConceptRecord);
}
