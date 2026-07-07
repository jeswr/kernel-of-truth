#!/usr/bin/env node
/**
 * molecules-v0 validation harness — mechanical enforcement of the molecule
 * rules in concept-hash-design.md §3.5 (as far as they are mechanizable):
 *
 *  rule 1  — `semanticStatus: "Molecule"` present and the `[m]` flag surfaced
 *            (record field + every molecule ref in a grounding note is
 *            followed by the `[m]` token; kernel refs must NOT carry it).
 *  rule 3  — exactly one groundingNote; ≤ 1,024 bytes after NFC; every token
 *            is (a) an exponent from the pinned prime lexicon incl. the
 *            pinned closed function-word allolex/glue table below,
 *            (b) punctuation from a closed set, or (c) a linked reference
 *            `{urn:...|gloss}` — anything else is ERR_GROUNDING_LEXICON.
 *  rule 4  — refs resolve to already-minted concepts only: kernel-v0 ids or
 *            molecules EARLIER in manifest mint order (=> no grounding
 *            cycles, mechanically).
 *  rule 5  — molecule depth ≤ 4, where primes and explicated molecule-free
 *            kernel-v0 concepts have depth 0 and a molecule's depth is
 *            1 + max(depth of referenced concepts).
 *
 * The gist pins the prime lexicon (§4.1) but leaves the closed
 * function-word allolex table to the profile bundle, which does not exist
 * yet; the table below IS molecules-v0's pinned choice (a documented v0
 * judgement — see docs/design-molecule-tier.md §3). Any change to it is a
 * corpus version change.
 *
 * Usage: node data/molecules-v0/validate.mjs   (exit 0 iff all pass)
 */
import { readFileSync, readdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));

// ---------------------------------------------------------------------------
// The pinned controlled grounding lexicon (single tokens).
// Sections mirror the 65-prime chart (gist §4.1); each token is either a
// chart exponent, an enumerated inflection of one (plurals of substantives,
// 3sg/participle forms of predicate exponents — notes are generic-present
// prose), or a member of the pinned GLUE set at the end.
// ---------------------------------------------------------------------------
const ALLOWED = new Set([
  // substantives (+ possessive/plural inflections)
  'i', 'me', 'you', 'someone', "someone's", 'somebody', 'something', 'thing',
  'things', 'people', "people's", 'body', 'bodies',
  // relational substantives
  'kind', 'kinds', 'part', 'parts',
  // determiners
  'this', 'these', 'same', 'other', 'another', 'else',
  // quantifiers
  'one', 'two', 'some', 'all', 'many', 'much', 'few', 'little',
  // evaluators / descriptors
  'good', 'bad', 'big', 'small',
  // mental predicates
  'think', 'thinks', 'know', 'knows', 'want', 'wants', 'feel', 'feels',
  'see', 'sees', 'hear', 'hears', 'hearing',
  // speech
  'say', 'says', 'said', 'words', 'word', 'true',
  // actions / events / movement
  'do', 'does', 'did', 'doing', 'happen', 'happens', 'happened',
  'move', 'moves', 'moving',
  // location / existence / specification (copula exponents per mapper primes.ts)
  'is', 'are', 'was', 'were', 'be', 'being', 'been',
  // possession
  'mine',
  // life / death
  'live', 'lives', 'lived', 'living', 'die', 'dies', 'died',
  // time
  'when', 'time', 'times', 'now', 'before', 'after', 'moment', 'moments',
  // space (somewhere = WHERE~PLACE allolex, chart function-word allolexy)
  'where', 'somewhere', 'place', 'places', 'here', 'above', 'below', 'far',
  'near', 'side', 'sides', 'inside', 'touch', 'touches', 'touching', 'touched',
  // logical
  'not', 'cannot', 'maybe', 'can', 'because', 'if',
  // intensifier / augmentor
  'very', 'more',
  // similarity
  'like', 'as', 'way', 'ways',
  // GLUE — the pinned closed function-word allolex table (v0 judgement;
  // the gist delegates this to the profile bundle, §3.5 rule 3):
  // articles, case/infinitive/locative particles, pronominal allolexes of
  // THIS/SOMETHING/SOMEONE, NOT-fusions, and NSM-canonical "toward/about".
  'a', 'an', 'the', 'of', 'to', 'with', 'in', 'on', 'at', 'for', 'from',
  'out', 'into', 'about', 'toward', 'it', 'its', 'they', 'them', 'their',
  'what', 'who', 'no', 'nothing',
]);

// Multi-token exponent phrases (consumed before single-token checking);
// 'long'/'short'/'there' are legal ONLY inside these phrases.
const PHRASES = [
  'there is', 'there are', 'there was', 'there were',
  'a very long time', 'a very short time', // VERY over duration (gist §4.5)
  'a long time', 'a short time', 'for some time', 'the same',
];

// Closed punctuation set (rule 3(b)).
const PUNCT = /[.,;:()]/g;

const REF_RE = /\{(urn:(kernel-v0|molecule-v0):[a-z0-9-]+)\|([^{}|]+)\}( \[m\])?/g;

function fail(errors, id, code, msg) {
  errors.push(`${id}: ${code}: ${msg}`);
}

const kernelManifest = JSON.parse(
  readFileSync(join(HERE, '..', 'kernel-v0', 'manifest.json'), 'utf8'),
);
const kernelIds = new Set(kernelManifest.concepts.map((c) => c.id));

const manifest = JSON.parse(readFileSync(join(HERE, 'manifest.json'), 'utf8'));
const errors = [];
const depths = new Map(); // molecule id -> depth; kernel/primes are depth 0
const mintedSoFar = new Set();

if (!Array.isArray(manifest.molecules) || manifest.molecules.length === 0) {
  throw new Error('ERR_MANIFEST_SHAPE: no molecules[] in manifest.json');
}

for (const entry of manifest.molecules) {
  const rec = JSON.parse(readFileSync(join(HERE, entry.file), 'utf8'));
  const id = rec.id;

  // --- record shape + rule 1 (visible second-class status) ---------------
  if (id !== entry.id) fail(errors, id, 'ERR_MANIFEST_MISMATCH', `manifest says ${entry.id}`);
  if (!/^urn:molecule-v0:[a-z0-9-]+$/.test(id)) fail(errors, id, 'ERR_ID', 'bad id shape');
  if (rec.semanticStatus !== 'Molecule') fail(errors, id, 'ERR_SEMANTIC_STATUS', 'must be "Molecule" (rule 1)');
  if (rec.flag !== '[m]') fail(errors, id, 'ERR_FLAG', '[m] flag must be surfaced (rule 1)');
  if (rec.researchGrade !== true) fail(errors, id, 'ERR_RESEARCH_GRADE', 'v0 records must carry researchGrade: true');
  if (typeof rec.label !== 'string' || rec.label.length === 0) fail(errors, id, 'ERR_LABEL', 'missing label');
  if (!Array.isArray(rec.corpusLemmas) || rec.corpusLemmas.length === 0) fail(errors, id, 'ERR_LEMMAS', 'corpusLemmas required');

  // --- rule 3: exactly one grounding note, byte cap, controlled lexicon --
  if (typeof rec.groundingNote !== 'string') {
    fail(errors, id, 'ERR_GROUNDING_NOTE', 'exactly one groundingNote string required (rule 3)');
    continue;
  }
  const note = rec.groundingNote.normalize('NFC');
  if (note !== rec.groundingNote) fail(errors, id, 'ERR_NFC', 'groundingNote not NFC-normalized');
  const bytes = Buffer.byteLength(note, 'utf8');
  if (bytes > 1024) fail(errors, id, 'ERR_GROUNDING_SIZE', `${bytes} bytes > 1024 (rule 3)`);
  if (note !== note.toLowerCase()) fail(errors, id, 'ERR_CASE', 'notes are lowercase by corpus convention (keeps tokenization exact)');

  // --- refs: extract, then rule 4 + [m] surfacing -------------------------
  const refs = [];
  const stripped = note.replace(REF_RE, (all, urn, ns, gloss, mflag) => {
    refs.push(urn);
    if (ns === 'molecule-v0' && !mflag) {
      fail(errors, id, 'ERR_M_FLAG', `molecule ref ${urn} not followed by " [m]" (rule 1)`);
    }
    if (ns === 'kernel-v0' && mflag) {
      fail(errors, id, 'ERR_M_FLAG', `kernel ref ${urn} wrongly flagged [m] (kernel-v0 records are explicated, molecule-free)`);
    }
    return ' ';
  });
  if (/[{}|[\]]/.test(stripped)) {
    fail(errors, id, 'ERR_GROUNDING_LEXICON', 'stray {, }, |, [ or ] outside a linked ref / [m] flag');
  }
  for (const r of new Set(refs)) {
    if (r.startsWith('urn:kernel-v0:')) {
      if (!kernelIds.has(r)) fail(errors, id, 'ERR_REF', `unknown kernel-v0 ref ${r} (rule 4)`);
    } else if (!mintedSoFar.has(r)) {
      fail(errors, id, 'ERR_REF', `molecule ref ${r} not minted earlier (rule 4: already-minted only => acyclic)`);
    }
  }
  const declared = JSON.stringify([...new Set(rec.groundingRefs ?? [])].sort());
  const parsed = JSON.stringify([...new Set(refs)].sort());
  if (declared !== parsed) fail(errors, id, 'ERR_REF_LIST', 'groundingRefs field != refs parsed from note');

  // --- rule 3 lexicon check over the remaining tokens ---------------------
  let text = ` ${stripped.replace(PUNCT, ' ')} `;
  for (const ph of PHRASES) {
    text = text.replaceAll(` ${ph} `, ' ').replaceAll(` ${ph} `, ' ');
  }
  for (const tok of text.split(/\s+/)) {
    if (tok.length === 0) continue;
    if (!ALLOWED.has(tok)) {
      fail(errors, id, 'ERR_GROUNDING_LEXICON', `token "${tok}" is not a pinned prime exponent, glue word, closed punctuation, or linked ref (rule 3)`);
    }
  }

  // --- rule 5: depth ------------------------------------------------------
  let depth = 1;
  for (const r of new Set(refs)) {
    depth = Math.max(depth, 1 + (depths.get(r) ?? 0)); // kernel refs: depth 0
  }
  depths.set(id, depth);
  if (depth > 4) fail(errors, id, 'ERR_DEPTH', `molecule depth ${depth} > 4 (rule 5)`);
  if (rec.moleculeDepth !== depth) fail(errors, id, 'ERR_DEPTH_FIELD', `record says depth ${rec.moleculeDepth}, computed ${depth}`);

  mintedSoFar.add(id);
}

// manifest-level cross-checks
if (manifest.moleculeCount !== manifest.molecules.length) {
  errors.push(`manifest: ERR_COUNT: moleculeCount ${manifest.moleculeCount} != ${manifest.molecules.length}`);
}
const files = readdirSync(join(HERE, 'molecules')).filter((f) => f.endsWith('.json'));
if (files.length !== manifest.molecules.length) {
  errors.push(`manifest: ERR_FILES: ${files.length} files vs ${manifest.molecules.length} manifest entries`);
}
const maxDepth = Math.max(...depths.values());
if (manifest.maxMoleculeDepth !== maxDepth) {
  errors.push(`manifest: ERR_MAX_DEPTH: manifest says ${manifest.maxMoleculeDepth}, computed ${maxDepth}`);
}

if (errors.length > 0) {
  console.error(`FAIL — ${errors.length} error(s):`);
  for (const e of errors) console.error(`  ${e}`);
  process.exit(1);
}
console.log(`OK — ${manifest.molecules.length} molecules pass §3.5 rules 1/3/4/5 mechanically (max depth ${maxDepth})`);
