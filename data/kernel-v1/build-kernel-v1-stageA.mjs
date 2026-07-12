#!/usr/bin/env node
/**
 * kernel-v1 Stage-A corpus build — sense-split-first construction
 * (docs/next/design/sense-split-first-construction.md; maintainer requirement
 * ASM-1884; Stage A scope: break/make/find/friend, ASM-1909).
 *
 * FAIL-CLOSED GATES (design §2.1), every one aborts the build with ERR_*:
 *   R1  mechanical sense enumeration recount against the pinned WN31 files;
 *       every minted wn31Synset must be a candidate of its lemma+POS.
 *   R2/R3  every non-null framenetFrame must exist in the pinned FrameNet
 *       file AND carry a lexical unit of the concept's lemma (frame
 *       selection IS sense selection); all synsets of a cluster share ONE
 *       frame by construction (a concept has a single frame field).
 *   R4  scope closure: sense-index per lemma = minted senses + the FULL
 *       excludedSenses list (candidates minus cluster-covered), no silence.
 *   G1  no shared identity: duplicateIdentityGroups must be 0, else
 *       ERR_SENSE_SHARED_IDENTITY (a merge must be REPORTED, never silent).
 *   G2  no unacknowledged polysemy: every lemma with >=2 same-POS senses
 *       needs >=2 minted senses or 1 + non-empty excludedSenses, else
 *       ERR_SENSE_UNDERDETERMINED.
 *   TYPING  ck-ufo sidecar total over the corpus; every break.* MUST be
 *       ontic_category=event (maintainer clause, ERR_BREAK_NOT_EVENT); all
 *       soft-type records binding:false with the 5 forbidden effects; the
 *       pi:011 defect class is UNMINTABLE: any break.violate range record
 *       anchored at material entity aborts (ERR_PI011_CLASS_REMINT).
 *   ENC  every explication passes the encoder's validateExplication and one
 *       encodeConceptSet pass; the encoder pin is READ, never written:
 *       encoderContentHash must equal kernel-v0's frozen value.
 *   CONTINUITY  the mint algorithm is proven unchanged by re-minting the 4
 *       kernel-v0 lemma concepts from their committed bytes and comparing to
 *       the frozen data/kernel-v0/minted-urns.jsonl rows; carried-byte
 *       explications must reproduce their v0 URNs exactly.
 *
 * Uses the pinned mint tool's dist modules UNMODIFIED (tools/mint/dist);
 * records the tool hash it observed. kernel-v0 is frozen forever and is
 * only READ here. No encoder file, no ALGORITHM_VERSION, no X0 golden is
 * touched — kernel-v1 is a data corpus (design §2.1).
 */
import { readFileSync, readdirSync, writeFileSync, mkdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const repo = join(here, '..', '..');

const { validateExplication, encodeConceptSet, encoderContentHash, ALGORITHM_VERSION } =
  await import(join(repo, 'encoder/dist/src/index.js'));
const { mintSingleton } = await import(join(repo, 'tools/mint/dist/src/mint-core.js'));
const { mintToolHash } = await import(join(repo, 'tools/mint/dist/src/cli.js'));
const { merkleRoot } = await import(join(repo, 'tools/mint/dist/src/merkle.js'));

const die = (msg) => { console.error('BUILD_KERNEL_V1_ABORT: ' + msg); process.exit(2); };
const PROFILE_HEADER = 'kot-ast/1\n';

// ---------- load concepts ----------
const conceptDir = join(here, 'concepts');
const files = readdirSync(conceptDir).filter((f) => f.endsWith('.json')).sort();
const concepts = files.map((f) => ({ file: f, rec: JSON.parse(readFileSync(join(conceptDir, f), 'utf8')) }));
if (concepts.length !== 11) die(`expected 11 Stage-A concepts, got ${concepts.length}`);

// ---------- encoder pin is READ-only and must match kernel-v0's frozen value ----------
const v0manifest = JSON.parse(readFileSync(join(repo, 'data/kernel-v0/manifest.json'), 'utf8'));
const encHash = encoderContentHash();
if (encHash !== v0manifest.encoderContentHash) {
  die(`ERR_ENCODER_PIN: live encoderContentHash ${encHash} != kernel-v0 frozen ${v0manifest.encoderContentHash} — the encoder MUST NOT change under this build`);
}

// ---------- ENC gate: validate + encode ----------
for (const { file, rec } of concepts) {
  try {
    validateExplication(rec.explication);
  } catch (e) {
    die(`ERR_ENC_VALIDATE(${file}): ${e.code || ''} ${e.message}`);
  }
}
const setInput = new Map(concepts.map(({ rec }) => [rec.id, rec.explication]));
let encoded;
try {
  encoded = encodeConceptSet(setInput);
} catch (e) {
  die(`ERR_ENC_ENCODE: ${e.message}`);
}

// ---------- R1: mechanical recount against pinned WN31 ----------
const LEMMA_POS = { break: 'v', make: 'v', find: 'v', friend: 'n' };
const POS_FILE = { v: 'synsets-verb.jsonl', n: 'synsets-noun.jsonl' };
const candidates = {}; // lemma -> Map(urn -> gloss)
for (const [lemma, pos] of Object.entries(LEMMA_POS)) {
  candidates[lemma] = new Map();
  const path = join(repo, 'data/lexical-wn31', POS_FILE[pos]);
  for (const line of readFileSync(path, 'utf8').split('\n')) {
    if (!line.trim()) continue;
    const r = JSON.parse(line);
    if (r.annotations.lemmas.includes(lemma)) candidates[lemma].set(r.id, r.annotations.gloss);
  }
}
const EXPECT_R1 = { break: 59, make: 49, find: 16, friend: 4 };
for (const [lemma, n] of Object.entries(EXPECT_R1)) {
  if (candidates[lemma].size !== n) die(`ERR_R1_RECOUNT(${lemma}): ${candidates[lemma].size} != pinned ${n} (ASM-1900/design §0)`);
}

// ---------- R2/R3: frame checks against pinned FrameNet ----------
const framesByUrn = new Map();
for (const line of readFileSync(join(repo, 'data/onto-framenet/frames.jsonl'), 'utf8').split('\n')) {
  if (!line.trim()) continue;
  const r = JSON.parse(line);
  framesByUrn.set(r.id, r);
}
for (const { file, rec } of concepts) {
  const s = rec.sense;
  if (!s) die(`ERR_SENSE_RECORD(${file}): missing sense block`);
  for (const syn of s.wn31Synsets) {
    if (!candidates[s.lemma].has(syn)) die(`ERR_R1_MEMBER(${file}): ${syn} is not a same-POS WN31 candidate of '${s.lemma}'`);
  }
  if (s.framenetFrame !== null) {
    const fr = framesByUrn.get(s.framenetFrame);
    if (!fr) die(`ERR_R2_FRAME(${file}): ${s.framenetFrame} not in pinned frames.jsonl`);
    if (fr.frame !== s.framenetFrameName) die(`ERR_R2_FRAME(${file}): name ${fr.frame} != ${s.framenetFrameName}`);
    const lus = (fr.annotations && fr.annotations.lexicalUnits) || [];
    const hasLU = lus.some((lu) => (lu.name || '') === `${s.lemma}.${s.pos}`);
    if (!hasLU) die(`ERR_R2_LU(${file}): frame ${fr.frame} carries no '${s.lemma}.${s.pos}' lexical unit — frame selection IS sense selection and must be lemma-licensed`);
  }
}

// ---------- minting (pinned tool modules, unmodified; all singletons, no intra-corpus refs) ----------
const toolHash = mintToolHash();
const knownIds = new Set(concepts.map(({ rec }) => rec.id));
const resolve = (s) => {
  if (knownIds.has(s)) die(`ERR_INTRA_REF: Stage-A explication references sibling ${s}; Stage A mints singletons only`);
  return s;
};
const minted = concepts.map(({ file, rec }) => {
  const { urn } = mintSingleton(rec.explication, PROFILE_HEADER, rec.id, resolve);
  return { file, id: rec.id, sourceId: rec.id.replace('urn:kernel-v1:', ''), urn };
});

// ---------- G1: no shared identity ----------
const byUrn = new Map();
for (const m of minted) {
  if (!byUrn.has(m.urn)) byUrn.set(m.urn, []);
  byUrn.get(m.urn).push(m.id);
}
const dupGroups = [...byUrn.values()].filter((g) => g.length > 1);
if (dupGroups.length > 0) {
  die(`ERR_SENSE_SHARED_IDENTITY (G1): ${JSON.stringify(dupGroups)} — byte-identical explications; senses are NOT split. Revise or merge WITH a reported merge census (design §2.1 G1); never silent.`);
}

// ---------- G2: no unacknowledged polysemy + R4 scope closure ----------
const byLemma = {};
for (const { rec } of concepts) (byLemma[rec.sense.lemma] ??= []).push(rec);
const senseIndex = {};
for (const [lemma, recs] of Object.entries(byLemma)) {
  const covered = new Set(recs.flatMap((r) => r.sense.wn31Synsets));
  const excluded = [...candidates[lemma].entries()]
    .filter(([urn]) => !covered.has(urn))
    .map(([urn, gloss]) => ({ synset: urn, gloss }));
  const nCand = candidates[lemma].size;
  if (nCand >= 2 && !(recs.length >= 2 || (recs.length === 1 && excluded.length > 0))) {
    die(`ERR_SENSE_UNDERDETERMINED (G2): lemma '${lemma}' has ${nCand} same-POS senses but ${recs.length} minted and ${excluded.length} excluded`);
  }
  for (const r of recs) {
    if (r.sense.excludedSiblingCount !== excluded.length) {
      die(`ERR_R4_COUNT(${r.id}): excludedSiblingCount ${r.sense.excludedSiblingCount} != computed ${excluded.length}`);
    }
  }
  senseIndex[lemma] = {
    schema: 'kot-sense-index/1',
    lemma, pos: LEMMA_POS[lemma],
    candidateCount: nCand,
    mintedSenses: recs.map((r) => ({
      id: r.id, senseTag: r.sense.senseTag, wn31Synsets: r.sense.wn31Synsets,
      framenetFrame: r.sense.framenetFrame, framenetFrameName: r.sense.framenetFrameName,
    })),
    excludedSenses: excluded,
    note: 'R4 scope closure: a concept claims its synset cluster, NOT the word. Every non-minted candidate is listed here; nothing is silently dropped (R5).',
  };
}

// ---------- TYPING gates ----------
const ufo = readFileSync(join(here, 'typing/ck-ufo-sidecar.jsonl'), 'utf8').split('\n').filter(Boolean).map((l) => JSON.parse(l));
const ufoByConcept = new Map(ufo.map((r) => [r.concept, r]));
for (const { rec } of concepts) {
  const t = ufoByConcept.get(rec.id);
  if (!t) die(`ERR_TYPING_COVERAGE: no ck-ufo record for ${rec.id}`);
  if (rec.sense.lemma === 'break' && t.ontic_category !== 'event') {
    die(`ERR_BREAK_NOT_EVENT: ${rec.id} typed '${t.ontic_category}' — maintainer clause: a breakage, in any sense, is an event, never a material entity`);
  }
  if (t.binding !== false) die(`ERR_TYPING_BINDING: ${rec.id} ck-ufo record must be binding:false (annotation)`);
}
const soft = readFileSync(join(here, 'typing/soft-type-per-sense.jsonl'), 'utf8').split('\n').filter(Boolean).map((l) => JSON.parse(l));
const FORBIDDEN = ['assert-type', 'reject-world', 'derive-disjointness', 'mint-entity', 'close-domain'];
for (const r of soft) {
  if (r.binding !== false || r.effect !== 'rank-only' || r.strength !== 'preference') die(`ERR_SOFT_AUTHORITY: ${r.id}`);
  for (const f of FORBIDDEN) if (!r.forbidden_effects.includes(f)) die(`ERR_SOFT_FORBIDDEN: ${r.id} missing ${f}`);
  if (!knownIds.has(r.concept)) die(`ERR_SOFT_SUBJECT: ${r.id} -> unknown concept ${r.concept}`);
  if (r.concept === 'urn:kernel-v1:break.violate' && r.position.form === 'range' && r.preferred_type.anchor === 'urn:onto-obo:BFO_0000040') {
    die('ERR_PI011_CLASS_REMINT: break.violate range anchored at material entity — the defect class this construction makes unmintable');
  }
}
const hardAxiomsEmitted = soft.filter((r) => r.binding === true).length;

// ---------- CONTINUITY: algorithm-unchanged proof + carried-bytes proof ----------
const v0urns = new Map(readFileSync(join(repo, 'data/kernel-v0/minted-urns.jsonl'), 'utf8')
  .split('\n').filter(Boolean).map((l) => { const r = JSON.parse(l); return [r.id, r.urn]; }));
const remintChecks = [];
for (const lemma of ['break', 'make', 'find', 'friend']) {
  const v0rec = JSON.parse(readFileSync(join(repo, `data/kernel-v0/concepts/${lemma}.json`), 'utf8'));
  const { urn } = mintSingleton(v0rec.explication, PROFILE_HEADER, v0rec.id, (s) => s);
  const frozen = v0urns.get(v0rec.id);
  if (urn !== frozen) die(`ERR_CONTINUITY_ALGO: re-mint of frozen v0 '${lemma}' gives ${urn} != frozen ${frozen} — mint algorithm drifted; ABORT`);
  remintChecks.push({ v0: v0rec.id, frozenUrn: frozen, remintedUrn: urn, equal: true });
}
const mintedById = new Map(minted.map((m) => [m.id, m.urn]));
const CARRIED = [
  ['urn:kernel-v1:make.create', 'urn:kernel-v0:make', true],
  ['urn:kernel-v1:find.locate', 'urn:kernel-v0:find', true],
  ['urn:kernel-v1:friend.person', 'urn:kernel-v0:friend', true],
  ['urn:kernel-v1:break.shatter', 'urn:kernel-v0:break', false], // agent sort deliberately broadened
];
const continuity = [];
for (const [v1id, v0id, expectEqual] of CARRIED) {
  const eq = mintedById.get(v1id) === v0urns.get(v0id);
  if (eq !== expectEqual) die(`ERR_CONTINUITY(${v1id}): mint ${eq ? '==' : '!='} v0 ${v0id}, expected ${expectEqual ? 'byte-identical carry' : 'a deliberate identity change'}`);
  continuity.push({ v1: v1id, v0: v0id, identicalMint: eq, expected: expectEqual });
}

// ---------- emit ----------
mkdirSync(join(here, 'sense-index'), { recursive: true });
for (const [lemma, idx] of Object.entries(senseIndex)) {
  writeFileSync(join(here, 'sense-index', `${lemma}.json`), JSON.stringify(idx, null, 1) + '\n');
}
writeFileSync(join(here, 'minted-urns.jsonl'),
  minted.map((m) => JSON.stringify({ id: m.id, sourceId: m.sourceId, urn: m.urn })).join('\n') + '\n');

const uniqueUrns = [...new Set(minted.map((m) => m.urn))];
const manifest = {
  corpus: 'kernel-v1',
  stage: 'A (sense-split break/make/find/friend; design §6.1 — stages B-D gated, not built)',
  schema: 'kot-ast/1',
  version: '0.1.0-stageA',
  generated: '2026-07-12',
  authorship: 'research-grade, agent-authored against profile-1 per docs/next/design/sense-split-first-construction.md; NOT federation-endorsed; adequacy unvalidated pending V-A/V-B',
  encoderContentHash: encHash,
  encoderAlgorithmVersion: ALGORITHM_VERSION,
  encoderNote: 'READ-ONLY pin check: equals kernel-v0 frozen value; kernel-v1 is a data corpus — no encoder change, no schema change, no ALGORITHM_VERSION bump, no X0 golden regeneration (design §2.1)',
  conceptCount: concepts.length,
  concepts: concepts.map(({ file, rec }) => ({
    id: rec.id, label: rec.label, file: `concepts/${file}`, frame: rec.explication.frame,
    status: rec.status, lemma: rec.sense.lemma, senseTag: rec.sense.senseTag,
    wn31Synsets: rec.sense.wn31Synsets, framenetFrame: rec.sense.framenetFrame,
    references: rec.references,
  })),
  senseIndexFiles: Object.keys(senseIndex).sort().map((l) => `sense-index/${l}.json`),
  excludedSensesTotal: Object.values(senseIndex).reduce((a, i) => a + i.excludedSenses.length, 0),
  gates: {
    G1_duplicateIdentityGroups: dupGroups.length,
    G1_note: 'must be 0; a merge is reported as a measured profile-1 expressivity limit, never silently absorbed',
    G2_senseUnderdetermined: 0,
    R1_recount: EXPECT_R1,
    typing_breakAllEvent: true,
    softTypeRecords: soft.length,
    hard_operational_axioms_emitted: hardAxiomsEmitted,
    pi011_class_unmintable_check: 'PASS (no break.violate range record anchored at material entity)',
  },
  supersedes: {
    'urn:kernel-v0:break': { disposition: 'SEED', v1: 'urn:kernel-v1:break.shatter', identityCarried: false, note: 'agent sort deliberately broadened SomeoneRef->SomethingRef per design §3.2; sibling senses authored fresh' },
    'urn:kernel-v0:make': { disposition: 'SEED', v1: 'urn:kernel-v1:make.create', identityCarried: true },
    'urn:kernel-v0:find': { disposition: 'SEED', v1: 'urn:kernel-v1:find.locate', identityCarried: true },
    'urn:kernel-v0:friend': { disposition: 'REVIEW', v1: 'urn:kernel-v1:friend.person', identityCarried: true, note: 'figurative sibling minted per adjudication §B.iii 040/041 flag' },
  },
  deprecationNote: 'kernel-v0 is frozen forever and is NOT modified; these four v0 concepts are superseded for NEW consumers only. Stage C owns the total deprecation map + repo grep gate (design §6.2 risk 6).',
  typing: {
    ckUfoSidecar: 'typing/ck-ufo-sidecar.jsonl',
    softTypePerSense: 'typing/soft-type-per-sense.jsonl',
    maintainerClause: 'every break.* sense is ontic_category=event (checked fail-closed at build)',
  },
  minting: {
    profileHeader: PROFILE_HEADER,
    mintedCount: minted.length,
    uniqueUrnCount: uniqueUrns.length,
    mintToolHash: toolHash,
    mintToolHashNote: 'sha256 over tools/mint/src/*.ts AT BUILD TIME. kernel-v0 was minted at e07bc2ac…; the tool sources have since gained corpus specs (physics/math/etc). The ALGORITHM is proven unchanged by the continuityChecks block: re-minting the four frozen v0 concepts from committed bytes reproduces their frozen URNs exactly.',
    corpusIdentityRoot: merkleRoot(uniqueUrns),
    identityRootAlgorithm: v0manifest.minting.identityRootAlgorithm,
    urnScheme: v0manifest.minting.urnScheme,
    referenceMode: 'substitute (no intra-corpus references in Stage A; all singletons)',
    identityPayload: 'Identity = the kot-ast/1 `explication` object (content-addressed by meaning). label/gloss/notes/pattern/status/references AND the `sense` block are annotation (design §2.1: senseTag/alias outside identity).',
    duplicateIdentityGroups: dupGroups.length,
    cyclicComponents: [],
    mintDate: '2026-07-12',
  },
  continuityChecks: { remintOfFrozenV0: remintChecks, carriedExplications: continuity },
};
writeFileSync(join(here, 'manifest.json'), JSON.stringify(manifest, null, 1) + '\n');

console.log(JSON.stringify({
  ok: true, concepts: concepts.length, encoderContentHash: encHash,
  algorithmVersion: ALGORITHM_VERSION, mintToolHash: toolHash,
  G1_duplicateIdentityGroups: dupGroups.length,
  excludedSensesTotal: manifest.excludedSensesTotal,
  continuity: continuity.map((c) => `${c.v1}${c.identicalMint ? ' == ' : ' != '}${c.v0}`),
  vectors: encoded && encoded.size ? encoded.size : (Array.isArray(encoded) ? encoded.length : 'ok'),
}, null, 1));
