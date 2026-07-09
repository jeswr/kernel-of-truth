#!/usr/bin/env node
/**
 * URN scheme cross-check: the encoder-side composite mint (encoder/src/rollup.ts,
 * reimplemented for dependency-direction reasons) must agree BYTE-FOR-BYTE
 * with the canonical minting implementation (tools/mint, the one that minted
 * every committed corpus URN), on the singleton path with profile header
 * "kot-ast/1\n" — for generated composites across the synth strata.
 *
 * Usage: node poc/compression-census/cross-check-urn.mjs
 */
import { strict as assert } from 'node:assert';
import {
  generateExplication,
  mutateExplication,
  mintCompositeUrn,
} from '../../encoder/dist/src/index.js';
import { mintSingleton } from '../../tools/mint/dist/src/mint-core.js';

const HEADER = 'kot-ast/1\n';
let n = 0;
for (const depth of [1, 2, 3, 4, 6, 8, 12]) {
  for (const topClauses of [1, 2, 4, 8, 16, 32]) {
    if (depth - 1 > 32 - topClauses) continue;
    for (let s = 0; s < 10; s++) {
      const e = generateExplication({ seed: `xchk/${depth}/${topClauses}/${s}`, topClauses, depth });
      const ours = mintCompositeUrn(e);
      // identity resolver: composite payloads carry no intra-batch refs
      const theirs = mintSingleton(JSON.parse(JSON.stringify(e)), HEADER, '__no_self__', (x) => x).urn;
      assert.equal(ours, theirs, `URN divergence at d=${depth} c=${topClauses} s=${s}`);
      n++;
      const m = mutateExplication(e, `xchk-mut/${depth}/${topClauses}/${s}`);
      if (m !== null) {
        const o2 = mintCompositeUrn(m.mutant);
        const t2 = mintSingleton(JSON.parse(JSON.stringify(m.mutant)), HEADER, '__no_self__', (x) => x).urn;
        assert.equal(o2, t2, `mutant URN divergence at d=${depth} c=${topClauses} s=${s}`);
        n++;
      }
    }
  }
}
console.log(`URN cross-check: ${n}/${n} encoder-mint == tools/mint (profile ${JSON.stringify(HEADER)})`);
