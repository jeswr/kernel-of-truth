/**
 * Generator fuzz regression (generator v2): the full X1 run (n=10^4)
 * surfaced seeds where generator v1 overflowed the 32-clause cap
 * (ERR_CAP_CLAUSES) because a stale per-clause `canEmbedClause` snapshot was
 * consulted after nested generation had spent the budget. v2 takes the
 * budget atomically at every embedding site; this test sweeps a wide seed
 * range (generation-only — cheap) across the X1 shape mixture plus
 * budget-extreme shapes, and requires every explication to pass the gates
 * (generateExplication validates internally and fails closed).
 */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { generateExplication, validateExplication, CAPS } from '../src/index.js';

// The X1 harness's shape mixture (poc/harness/x1.ts corpusShape) — the exact
// family the full run walks.
function x1Shape(i: number): { topClauses: number; depth: number } {
  const tc = [1, 2, 3, 4, 6, 8, 12, 16][i % 8]!;
  const dep = [1, 2, 2, 3, 3, 4, 5, 2][Math.floor(i / 8) % 8]!;
  return { topClauses: tc, depth: dep };
}

test('20k-seed fuzz: X1 shape mixture stays within all caps', () => {
  let maxClauses = 0;
  for (let i = 0; i < 20000; i++) {
    const { topClauses, depth } = x1Shape(i);
    // Same seed namespace shape as the X1 harness (x1/<i>), distinct label.
    const e = generateExplication({ seed: `fuzz/x1/${i}`, topClauses, depth });
    const stats = validateExplication(e);
    assert.ok(stats.clauseCount <= CAPS.maxClauses, `seed ${i}: ${stats.clauseCount} clauses`);
    assert.ok(stats.maxDepth <= CAPS.maxDepth, `seed ${i}: depth ${stats.maxDepth}`);
    if (stats.clauseCount > maxClauses) maxClauses = stats.clauseCount;
  }
  // The mixture should actually exercise the budget, not idle far below it.
  assert.ok(maxClauses >= 16, `fuzz never approached the cap (max ${maxClauses})`);
});

test('budget-extreme shapes: high top-clause counts and deep spines', () => {
  const shapes: [number, number][] = [
    [32, 1], // zero embedded budget: every quote/complement site must decline
    [31, 2],
    [28, 5],
    [24, 6],
    [16, 8],
    [8, 11],
    [1, 11],
  ];
  for (const [tc, dep] of shapes) {
    for (let i = 0; i < 300; i++) {
      const e = generateExplication({ seed: `fuzz/extreme/${tc}/${dep}/${i}`, topClauses: tc, depth: dep });
      const stats = validateExplication(e);
      assert.ok(stats.clauseCount <= CAPS.maxClauses, `(${tc},${dep}) seed ${i}: ${stats.clauseCount} clauses`);
    }
  }
});
