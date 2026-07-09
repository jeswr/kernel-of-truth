#!/usr/bin/env node
/**
 * kot-lint — Stage-0 kernel precision linter CLI (mode P only).
 * Design: docs/next/kernel-precision-linter.md (N-PL) §6 Stage 0.
 *
 * Usage:
 *   node tools/lint/kot-lint.mjs [options] <file...>
 *
 * Options:
 *   --json             stable-JSON report to stdout (byte-identical for same
 *                      input + same pinned kernel/pattern versions — S5)
 *   --tokens           include per-content-token band annotations (JSON only)
 *   --policy=<name>    mapper policy: a1-hybrid (default; N-PL §2 S2) | none
 *   --no-wn31          skip loading the wn31-aligned membership band (faster;
 *                      unmapped tokens then bottom out at 'out')
 *   --strip=markdown   offset-preserving markdown de-formatting before lint
 *   --mode=P           lint mode. Only P (permissive report) exists at
 *                      Stage 0; S (quarantine) and R (rewrite) fail closed.
 *   --max-flags=<n>    cap printed flags per file in text output (default 50)
 *
 * Exit codes: 0 = linted (mode P never blocks; N-PL §1.3); 2 = usage/input
 * error (ERR_*).
 *
 * VOCABULARY HONESTY (N-PL §9.6, binding): class U is reported as
 * "out of kernel coverage / unverifiable-here" — NEVER "hallucination".
 * Class M means "fully kernel-v0-mappable"; groundedness (G+/G−) is NOT
 * evaluated at Stage 0.
 */
import { readFileSync } from 'node:fs';
import { buildLintContext, lintDocument, stableStringify, lineColConverter } from './lib/lint.mjs';

function fail(code, msg) {
  console.error(`${code}: ${msg}`);
  process.exit(2);
}

const files = [];
const opts = { json: false, tokens: false, policy: 'a1-hybrid', wn31: true, strip: 'none', mode: 'P', maxFlags: 50 };
for (const arg of process.argv.slice(2)) {
  if (arg === '--json') opts.json = true;
  else if (arg === '--tokens') opts.tokens = true;
  else if (arg === '--no-wn31') opts.wn31 = false;
  else if (arg.startsWith('--policy=')) opts.policy = arg.slice('--policy='.length);
  else if (arg.startsWith('--strip=')) opts.strip = arg.slice('--strip='.length);
  else if (arg.startsWith('--mode=')) opts.mode = arg.slice('--mode='.length);
  else if (arg.startsWith('--max-flags=')) opts.maxFlags = Number(arg.slice('--max-flags='.length));
  else if (arg.startsWith('--')) fail('ERR_LINT_USAGE', `unknown option ${arg}`);
  else files.push(arg);
}
if (files.length === 0) fail('ERR_LINT_USAGE', 'usage: kot-lint.mjs [--json] [--tokens] [--policy=a1-hybrid|none] [--no-wn31] [--strip=markdown] [--mode=P] <file...>');
if (opts.mode !== 'P') {
  fail(
    'ERR_LINT_MODE_UNIMPLEMENTED',
    `mode ${opts.mode} is Stage-1+ (N-PL §6): S needs the quarantine contract + renderer, R needs the record->text renderer + round-trip gate. Only mode P exists at Stage 0. Fail-closed.`,
  );
}
if (!['a1-hybrid', 'none'].includes(opts.policy)) fail('ERR_LINT_USAGE', `--policy must be a1-hybrid or none, got ${opts.policy}`);
if (!['none', 'markdown'].includes(opts.strip)) fail('ERR_LINT_USAGE', `--strip must be markdown or none, got ${opts.strip}`);

const ctx = buildLintContext({ policyName: opts.policy, wn31: opts.wn31 });

const out = { schema: 'kot-lint-report/0', mode: 'P', pins: ctx.pins, files: [] };
for (const file of files) {
  let raw;
  try {
    raw = readFileSync(file, 'utf8');
  } catch (e) {
    fail('ERR_LINT_INPUT', `cannot read ${file}: ${e.message}`);
  }
  const { report, flags, tokenAnnotations } = lintDocument(raw, ctx, {
    strip: opts.strip,
    collectTokens: opts.tokens,
  });
  out.files.push({
    path: file,
    strip: opts.strip,
    report,
    flags,
    ...(opts.tokens ? { tokenAnnotations } : {}),
  });
}

if (opts.json) {
  process.stdout.write(stableStringify(out));
  process.exit(0);
}

// --- human-readable text report ---------------------------------------------
for (const f of out.files) {
  const toLC = lineColConverter(readFileSync(f.path, 'utf8'));
  const r = f.report;
  console.log(`\n${f.path}`);
  console.log('  '.padEnd(2) + '-'.repeat(Math.min(76, f.path.length + 2)));
  const fr = (x) => (x === null ? 'n/a' : `${(x * 100).toFixed(2)}%`);
  console.log(
    `  propositions=${r.propositions} sentences=${r.sentences} words=${r.tokens.expandedWordTokens} content=${r.tokens.contentTokens}`,
  );
  const pc = r.propositionCoverage.clause;
  console.log(
    `  proposition conjunctive coverage (clause proxy; UPPER BOUNDS — no frame check):`,
  );
  console.log(
    `    kernel-v0 strict ${fr(pc.kernelV0Strict.fraction)} | kernel-v0 member ${fr(pc.kernelV0Member.fraction)} | molecules-v0 ${fr(pc.moleculesV0.fraction)} | wn31 band ${fr(pc.wn31Aligned.fraction)}`,
  );
  console.log(
    `  engagement (Stage-0 lattice projection): M=${fr(r.engagement.fractions.M)} A=${fr(r.engagement.fractions.A)} U-mol=${fr(r.engagement.fractions['U-mol'])} U-wn31=${fr(r.engagement.fractions['U-wn31'])} U-out=${fr(r.engagement.fractions['U-out'])}`,
  );
  console.log(
    `  flags: V=${r.flagCounts.V.total} (filler=${r.flagCounts.V.filler} weasel=${r.flagCounts.V.weasel} hedge=${r.flagCounts.V.hedge}) A=${r.flagCounts.A} | warn/1000w=${r.rates.warnPer1000Words?.toFixed(2) ?? 'n/a'}`,
  );
  const shown = f.flags.slice(0, opts.maxFlags);
  for (const fl of shown) {
    const { line, col } = toLC(fl.start);
    console.log(`  ${f.path}:${line}:${col} [${fl.class}/${fl.severity}] ${fl.message}`);
  }
  if (f.flags.length > shown.length) console.log(`  … ${f.flags.length - shown.length} more flags (use --json for all)`);
  console.log(
    `  note: U (out of kernel coverage) is informational — "unverifiable-here", never "hallucination" (N-PL §9.6); groundedness is not evaluated at Stage 0.`,
  );
}
process.exit(0);
