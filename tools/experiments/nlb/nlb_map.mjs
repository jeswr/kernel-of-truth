#!/usr/bin/env node
// nlb_map.mjs — mapper bridge for the NL-boundary harness (l3a-parse / a5-nl).
// DRAFT harness (docs/design-nl-boundary-l3a-parse-a5-nl.md §9). Reads JSONL
// {pid, text} on stdin (text with entity spans already masked to " @ " by
// nlb_frontend.py), runs @jeswr/kernel-mapper mapText under the a1-hybrid
// policy (pin verified by policyPreset itself), and emits JSONL
// {pid, concepts: [distinct concept URNs, phrase heads only], abstained}.
//
// --vertical l3a|a5 selects the pinned lexicon manifests (design doc §3):
//   l3a: kernel-v0 + molecules-v0 minted-urns (label = sourceId, '-' -> ' ')
//   a5 : kernel-v0 + molecules-v0 + code-v0
// --derange applies the registered seed-0 fixed-point-free permutation
// (rotation by 1 over the sorted concept-URN list) to every concept decision —
// the scramble-control arm's semantic-binding derangement (record G5).
// Deterministic: no RNG, no clock, no network.
import path from 'node:path';
import readline from 'node:readline';
import { readFileSync } from 'node:fs';
import { fileURLToPath, pathToFileURL } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, '..', '..', '..');
const mapper = await import(
  pathToFileURL(path.join(ROOT, 'mapper', 'dist', 'src', 'index.js')).href
);
const { buildLexicon, mapText, policyPreset } = mapper;

const args = process.argv.slice(2);
function flag(name) {
  return args.includes(name);
}
function opt(name, dflt) {
  const i = args.indexOf(name);
  return i >= 0 && i + 1 < args.length ? args[i + 1] : dflt;
}
const vertical = opt('--vertical', null);
if (vertical !== 'l3a' && vertical !== 'a5') {
  process.stderr.write('nlb_map: --vertical l3a|a5 required\n');
  process.exit(2);
}
const derange = flag('--derange');

function mintedConcepts(corpus) {
  const p = path.join(ROOT, 'data', corpus, 'minted-urns.jsonl');
  const out = [];
  for (const line of readFileSync(p, 'utf8').split('\n')) {
    if (!line.trim()) continue;
    const r = JSON.parse(line);
    // label = sourceId with hyphens as spaces ("maker-of" -> "maker of");
    // id = the content-hash URN so mapped decisions carry the URN directly.
    out.push({ id: r.urn, label: r.sourceId.replace(/-/g, ' ') });
  }
  return out;
}

const corpora =
  vertical === 'l3a'
    ? ['kernel-v0', 'molecules-v0']
    : ['kernel-v0', 'molecules-v0', 'code-v0'];
const concepts = corpora.flatMap(mintedConcepts);
const lexicon = buildLexicon(concepts);
const policy = policyPreset('a1-hybrid'); // fails closed on policy-hash drift

// Registered derangement (seed 0): rotation by 1 over the sorted URN list —
// fixed-point-free for n >= 2 by construction.
let perm = null;
if (derange) {
  const urns = [...new Set(concepts.map((c) => c.id))].sort();
  perm = new Map(urns.map((u, i) => [u, urns[(i + 1) % urns.length]]));
}

const rl = readline.createInterface({ input: process.stdin, terminal: false });
const out = [];
rl.on('line', (line) => {
  if (!line.trim()) return;
  const rec = JSON.parse(line);
  const tokens = mapText(rec.text, lexicon, policy);
  const seen = new Set();
  let abstained = false;
  for (const t of tokens) {
    if (t.decision.kind === 'abstain') abstained = true;
    if (t.decision.kind === 'concept' && t.phrasePos === 0) {
      const c = perm ? perm.get(t.decision.conceptId) ?? t.decision.conceptId
                     : t.decision.conceptId;
      seen.add(c);
    }
  }
  out.push(JSON.stringify({ pid: rec.pid, concepts: [...seen].sort(), abstained }));
});
rl.on('close', () => {
  process.stdout.write(out.join('\n') + (out.length ? '\n' : ''));
});
