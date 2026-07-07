// extract.mjs — set.mm -> profile-M (pm-mm/1) bulk extraction
// Bead: kernel-of-truth-hvu. Contract: docs/design-bulk-kernel.md (honesty
// architecture + verification bar), docs/design-math-sector.md (profile-M;
// §1.1 chose Metamath grounding for exactly this pipeline).
//
// Record rule (principled, no silent truncation): EVERY $a statement of
// set.mm is emitted —
//   - typecode != '|-'                    -> status "syntax-former"
//   - typecode == '|-' and label df-*     -> status "definition"
//   - typecode == '|-' and label ax-*     -> status "axiom"
// Any |- $a matching neither prefix would be listed in manifest.excluded
// (empirically: zero at the pinned commit). $p theorems are out of scope by
// design (no proof layer — design-math-sector.md L1).
//
// Dependency semantics (stated rule):
//   introducedBy(c)  = the FIRST syntax former (database order) whose
//                      statement contains constant c. Punctuation constants
//                      ('(' , ')' ...) therefore attribute to their first
//                      user (e.g. wi) — deterministic, documented noise.
//   dependencies.syntax       = { introducedBy(c) : c in statement+$e hyps } \ self
//   dependencies.definitional = { definitionOf(introducedBy(c)) :
//                                 c in DEFINIENS (whole statement when the
//                                 definiendum split fails or for ax/syntax
//                                 records) } \ self
//   definitionOf(S) = the df-* whose definiendum's newest constant is
//                     introduced by S (latest-introduction rule; see
//                     assignSyntaxFormers below). Primitive syntax (wi, wn,
//                     wal, cv, wcel ...) has no definitionOf — reported.
//
// Determinism: output is a pure function of (set.mm bytes, this extractor,
// CLI pins --commit and --date). Byte-identical re-extraction is a
// verification gate (design-bulk-kernel.md §Verification bar); run twice
// and diff.
//
// Usage:
//   node extract.mjs --src /path/to/set.mm \
//     --commit <git-commit-sha> --date YYYY-MM-DD --out data/math-mm
//
// Zero runtime deps. Fail closed with ERR_* codes.

import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { parseMM } from './parse-mm.mjs';

const EXTRACTOR_VERSION = '1.0.0';
const SCHEMA = 'pm-mm/1';
const URN_PREFIX = 'urn:math-mm:';
const MATHBOX_MARKER = 'Mathboxes for user contributions';

// ---------- args ----------
function arg(name, required = true) {
  const i = process.argv.indexOf(`--${name}`);
  if (i === -1 || i + 1 >= process.argv.length) {
    if (required) { console.error(`ERR_ARGS: missing --${name}`); process.exit(2); }
    return null;
  }
  return process.argv[i + 1];
}
const srcPath = arg('src');
const commit = arg('commit');
const datePin = arg('date');
const outDir = arg('out');
if (!/^[0-9a-f]{40}$/.test(commit)) { console.error('ERR_ARGS: --commit must be a 40-hex git sha'); process.exit(2); }
if (!/^\d{4}-\d{2}-\d{2}$/.test(datePin)) { console.error('ERR_ARGS: --date must be YYYY-MM-DD'); process.exit(2); }

// ---------- extractor content-hash (over its own sources, sorted by name) ----------
const selfDir = path.dirname(fileURLToPath(import.meta.url));
const extractorFiles = ['parse-mm.mjs', 'extract.mjs'];
const extractorHash = crypto.createHash('sha256')
  .update(extractorFiles.map((f) => fs.readFileSync(path.join(selfDir, f))).reduce((a, b) => Buffer.concat([a, b])))
  .digest('hex');

// ---------- load + parse ----------
const srcBuf = fs.readFileSync(srcPath);
const sourceSha256 = crypto.createHash('sha256').update(srcBuf).digest('hex');
const src = srcBuf.toString('utf8');
const db = parseMM(src);

// mathbox boundary: line of the marker comment (statements after it are mathbox)
let mathboxStartLine = null;
{
  const idx = src.indexOf(MATHBOX_MARKER);
  if (idx !== -1) mathboxStartLine = src.slice(0, idx).split('\n').length;
}

// ---------- classify $a statements ----------
const aStmts = db.assertions.filter((a) => a.kind === 'a');
const syntaxFormers = aStmts.filter((a) => a.typecode !== '|-');
const dfs = aStmts.filter((a) => a.typecode === '|-' && a.label.startsWith('df-'));
const axs = aStmts.filter((a) => a.typecode === '|-' && a.label.startsWith('ax-'));
const excluded = aStmts.filter((a) => a.typecode === '|-' && !a.label.startsWith('df-') && !a.label.startsWith('ax-'));

// ---------- introducedBy: constant -> first syntax former containing it ----------
const introducedBy = new Map(); // constant -> assertion (syntax former)
for (const s of syntaxFormers) {
  for (const sym of s.symbols) {
    if (db.constants.has(sym) && !introducedBy.has(sym)) introducedBy.set(sym, s);
  }
}

// constants used in emitted statements: collect the used-constant set per record
function usedConstantsOf(a) {
  const out = new Set();
  for (const sym of a.symbols) if (db.constants.has(sym)) out.add(sym);
  for (const e of a.eHyps) {
    if (db.constants.has(e.typecode)) out.add(e.typecode); // '|-' etc.
    for (const sym of e.symbols) if (db.constants.has(sym)) out.add(sym);
  }
  out.delete(a.typecode);
  out.delete('|-'); // hypothesis typecode is judgement punctuation, not grammar
  return out;
}

// ---------- definiendum/definiens split (standard set.mm definition shapes) ----------
// wff-def:   |- ( D <-> E )   -- '<->' at paren depth 1, outer parens wrap all
// class-def: |- D = E         -- first '=' (definienda never contain '=')
function splitDefinition(symbols) {
  if (symbols[0] === '(' && symbols[symbols.length - 1] === ')') {
    let depth = 0;
    let outerClosesAtEnd = false;
    for (let i = 0; i < symbols.length; i++) {
      if (symbols[i] === '(') depth++;
      else if (symbols[i] === ')') { depth--; if (depth === 0) { outerClosesAtEnd = i === symbols.length - 1; break; } }
    }
    if (outerClosesAtEnd) {
      let d = 0;
      for (let i = 0; i < symbols.length; i++) {
        const s = symbols[i];
        if (s === '(') d++;
        else if (s === ')') d--;
        else if (s === '<->' && d === 1) {
          return { definiendum: symbols.slice(1, i), connective: '<->', definiens: symbols.slice(i + 1, -1) };
        }
      }
    }
  }
  const eq = symbols.indexOf('=');
  if (eq > 0) {
    return { definiendum: symbols.slice(0, eq), connective: '=', definiens: symbols.slice(eq + 1) };
  }
  return null;
}

// ---------- df -> syntax former assignment (definiendum pattern matching) ----------
// By set.mm's definitional-soundness convention a definition's definiendum is
// exactly its syntax former's pattern applied to distinct variables. So the
// assignment is EXACT pattern matching: same length, identical constants at
// constant positions, a variable of the same sort at variable positions.
// (A latest-constant-introduction rule fails here: formers like w3o reuse
// existing constants — '( ph \/ ps \/ ch )' introduces no new token.)
// Fallback for irregular shapes (no definiendum split, e.g. df-bi): the
// used constant whose introducing former is latest in database order.
// Validated: the assignment must be injective (one df per former); pattern
// ambiguity or collision is fatal.
const varSortKey = (sort) => `?${sort}`;
const formerByPattern = new Map(); // pattern key -> syntax former assertion
for (const s of syntaxFormers) {
  const varSorts = new Map(s.mandatoryVars.map((v) => [v.name, v.typecode]));
  const key = s.typecode + ' | ' + s.symbols.map((sym) => (varSorts.has(sym) ? varSortKey(varSorts.get(sym)) : sym)).join(' ');
  if (formerByPattern.has(key)) {
    console.error(`ERR_AMBIGUOUS_FORMER_PATTERN: '${key}' declared by both ${formerByPattern.get(key).label} and ${s.label}`);
    process.exit(1);
  }
  formerByPattern.set(key, s);
}
const splitByLabel = new Map();       // df label -> split | null
const formerOfDf = new Map();         // df label -> syntax former assertion
const definitionOfFormer = new Map(); // syntax former label -> df assertion
const fallbackAssignedDfs = [];
for (const d of dfs) {
  const split = splitDefinition(d.symbols);
  splitByLabel.set(d.label, split);
  let former = null;
  if (split) {
    const varSorts = new Map(d.mandatoryVars.map((v) => [v.name, v.typecode]));
    const wantTc = split.connective === '<->' ? 'wff' : 'class';
    const key = wantTc + ' | ' + split.definiendum.map((sym) => (varSorts.has(sym) ? varSortKey(varSorts.get(sym)) : sym)).join(' ');
    former = formerByPattern.get(key) ?? null;
  }
  if (former === null) {
    // irregular shape (or pattern not found): latest-introduced constant rule
    fallbackAssignedDfs.push(d.label);
    for (const sym of (split ? split.definiendum : d.symbols)) {
      if (!db.constants.has(sym)) continue;
      const intro = introducedBy.get(sym);
      if (intro && (former === null || intro.index > former.index)) former = intro;
    }
  }
  if (former === null) { console.error(`ERR_DF_NO_FORMER: ${d.label} has no assignable syntax former`); process.exit(1); }
  formerOfDf.set(d.label, former);
  if (definitionOfFormer.has(former.label)) {
    console.error(`ERR_DF_FORMER_COLLISION: ${former.label} claimed by ${definitionOfFormer.get(former.label).label} and ${d.label}`);
    process.exit(1);
  }
  definitionOfFormer.set(former.label, d);
}

// ---------- dependencies ----------
const emitted = [...syntaxFormers, ...dfs, ...axs].sort((a, b) => a.index - b.index);
const emittedLabels = new Set(emitted.map((a) => a.label));
const unintroducedConstants = new Set();

function depsOf(a) {
  const used = usedConstantsOf(a);
  const syn = new Set();
  for (const c of used) {
    const intro = introducedBy.get(c);
    if (!intro) { unintroducedConstants.add(c); continue; }
    if (intro.label !== a.label) syn.add(intro.label);
  }
  // A definition's definiendum instantiates its syntax former's pattern: that
  // former is a syntactic dependency even when it introduces no new constant
  // token (w3o, wral, ... reuse existing constants and are otherwise invisible
  // to constant-introduction scanning).
  const own = formerOfDf.get(a.label);
  if (own && own.label !== a.label) syn.add(own.label);
  // definitional deps: definiens constants only, when this is a split definition
  const split = splitByLabel.get(a.label) ?? null;
  let defScanSyms;
  if (a.typecode === '|-' && a.label.startsWith('df-') && split) defScanSyms = split.definiens;
  else defScanSyms = null; // whole statement
  const defScan = new Set();
  if (defScanSyms) { for (const s of defScanSyms) if (db.constants.has(s)) defScan.add(s); }
  else { for (const c of used) defScan.add(c); }
  const def = new Set();
  for (const c of defScan) {
    const intro = introducedBy.get(c);
    if (!intro) continue;
    if (intro.label === a.label) continue; // self-introduced constant: its defining df is NOT a dependency of this former (it is the reverse edge)
    const d = definitionOfFormer.get(intro.label);
    if (d && d.label !== a.label) def.add(d.label);
  }
  return { syntax: [...syn].sort(), definitional: [...def].sort() };
}

const depsByLabel = new Map();
for (const a of emitted) depsByLabel.set(a.label, depsOf(a));

// ---------- dependency graph: SCCs, acyclicity, depth distribution ----------
// Edges point record -> dependency. Acyclicity is VERIFIED, not assumed:
// Tarjan SCC (iterative). Empirical finding at the pinned commit: the graph
// is acyclic EXCEPT set.mm's documented class-theory bootstrap, the 2-cycle
// {df-cleq, df-clel} (df-cleq defines '=' for classes using 'e.'; df-clel
// defines 'e.' using '='). set.mm itself marks df-clab/df-cleq/df-clel (and
// df-bi) as not definitions in the strict sense and exempts them from its
// definitional soundness check — the cycle is the source's real structure,
// reported as a finding per design-bulk-kernel.md ("failures are findings").
// Depths are computed on the condensation DAG (SCC members share a depth).
const adj = new Map();
for (const a of emitted) {
  adj.set(a.label, [...new Set([...depsByLabel.get(a.label).syntax, ...depsByLabel.get(a.label).definitional])]);
}
const idxByLabel = new Map(emitted.map((a) => [a.label, a.index]));
let edgeCount = 0;
let backEdgeViolations = [];
for (const a of emitted) {
  for (const t of adj.get(a.label)) {
    edgeCount++;
    if (idxByLabel.get(t) >= a.index) backEdgeViolations.push([a.label, t]);
  }
}
// Tarjan SCC, iterative
const sccOf = new Map(); // label -> scc id
const sccMembers = [];   // scc id -> [labels]
{
  let counter = 0;
  const index = new Map(), low = new Map(), onStack = new Set();
  const S = [];
  for (const root of emitted.map((a) => a.label)) {
    if (index.has(root)) continue;
    const work = [[root, 0]];
    while (work.length) {
      const frame = work[work.length - 1];
      const [v, pi] = frame;
      if (pi === 0) {
        index.set(v, counter); low.set(v, counter); counter++;
        S.push(v); onStack.add(v);
      }
      let recursed = false;
      const nbrs = adj.get(v);
      for (let i = pi; i < nbrs.length; i++) {
        const w = nbrs[i];
        if (!index.has(w)) {
          frame[1] = i + 1;
          work.push([w, 0]);
          recursed = true;
          break;
        }
        if (onStack.has(w)) low.set(v, Math.min(low.get(v), index.get(w)));
      }
      if (recursed) continue;
      if (low.get(v) === index.get(v)) {
        const comp = [];
        for (;;) {
          const w = S.pop(); onStack.delete(w);
          sccOf.set(w, sccMembers.length); comp.push(w);
          if (w === v) break;
        }
        comp.sort();
        sccMembers.push(comp);
      }
      work.pop();
      if (work.length) {
        const [p] = work[work.length - 1];
        low.set(p, Math.min(low.get(p), low.get(v)));
      }
    }
  }
}
const nontrivialSccs = sccMembers.filter((m) => m.length > 1);
const selfLoops = emitted.filter((a) => adj.get(a.label).includes(a.label)).map((a) => a.label);
const acyclic = nontrivialSccs.length === 0 && selfLoops.length === 0;
// condensation depths (Tarjan emits SCCs in reverse topological order:
// every dependency's SCC is emitted BEFORE the dependent's SCC)
const sccDepth = new Array(sccMembers.length).fill(0);
for (let s = 0; s < sccMembers.length; s++) {
  let dmax = -1;
  for (const v of sccMembers[s]) {
    for (const w of adj.get(v)) {
      const t = sccOf.get(w);
      if (t !== s) dmax = Math.max(dmax, sccDepth[t]);
    }
  }
  sccDepth[s] = dmax + 1;
}
const depth = new Map(emitted.map((a) => [a.label, sccDepth[sccOf.get(a.label)]]));
const depthHist = {};
for (const a of emitted) {
  const d = depth.get(a.label);
  depthHist[d] = (depthHist[d] || 0) + 1;
}
let maxDepth = 0, maxDepthLabel = null;
for (const a of emitted) {
  if (depth.get(a.label) > maxDepth) { maxDepth = depth.get(a.label); maxDepthLabel = a.label; }
}
// witness chain for max depth (descends one depth level per step)
const witness = [];
{
  let cur = maxDepthLabel;
  while (cur !== null) {
    witness.push(cur);
    let next = null;
    for (const t of adj.get(cur)) if (depth.get(t) === depth.get(cur) - 1) { next = t; break; }
    cur = next;
  }
}

// reachability of syntax formers from df/ax records
const reachable = new Set();
{
  const queue = [...dfs.map((d) => d.label), ...axs.map((x) => x.label)];
  for (const l of queue) reachable.add(l);
  while (queue.length) {
    const l = queue.pop();
    const deps = depsByLabel.get(l);
    for (const t of [...deps.syntax, ...deps.definitional]) {
      if (!reachable.has(t)) { reachable.add(t); queue.push(t); }
    }
  }
}
const unreachedSyntax = syntaxFormers.filter((s) => !reachable.has(s.label)).map((s) => s.label);

// ---------- record emission ----------
function urn(label) { return URN_PREFIX + label; }

function recordOf(a) {
  const status = a.typecode !== '|-' ? 'syntax-former' : (a.label.startsWith('df-') ? 'definition' : 'axiom');
  const deps = depsByLabel.get(a.label);
  const definition = {
    schema: SCHEMA,
    form: 'mm-canonical',
    typecode: a.typecode,
    symbols: a.symbols,
    variables: a.mandatoryVars.map((v) => ({ name: v.name, sort: v.typecode })),
  };
  if (a.dPairs.length > 0) definition.distinctVars = a.dPairs;
  if (a.eHyps.length > 0) {
    definition.hypotheses = a.eHyps.map((e) => ({ label: e.label, typecode: e.typecode, symbols: e.symbols }));
  }
  if (status === 'definition') {
    const split = splitByLabel.get(a.label);
    if (split) {
      definition.definiendum = split.definiendum;
      definition.connective = split.connective;
      definition.definiens = split.definiens;
    } else {
      definition.irregularShape = true; // e.g. df-bi; whole statement is the payload
    }
    definition.syntaxFormer = urn(formerOfDf.get(a.label).label);
  }
  if (status === 'syntax-former') {
    const d = definitionOfFormer.get(a.label);
    if (d) definition.definedBy = urn(d.label);
  }
  const references = [...new Set([...deps.syntax, ...deps.definitional])].sort().map(urn);
  const rec = {
    id: urn(a.label),
    label: a.label,
    status,
    references,
    dependencies: { syntax: deps.syntax.map(urn), definitional: deps.definitional.map(urn) },
    definition,
    sourceComment: a.comment, // annotation layer: the $( ... $) comment preceding the statement, whitespace-normalized
    provenance: {
      source: 'https://github.com/metamath/set.mm',
      sourceFile: 'set.mm',
      sourceVersion: commit,
      sourceSha256,
      sourceLine: a.line,
      mathbox: mathboxStartLine !== null && a.line > mathboxStartLine,
      extractorVersion: EXTRACTOR_VERSION,
      extractorHash,
      extractionDate: datePin,
    },
  };
  return rec;
}

fs.mkdirSync(outDir, { recursive: true });
function writeJsonl(name, stmts) {
  const lines = stmts.map((a) => JSON.stringify(recordOf(a)));
  fs.writeFileSync(path.join(outDir, name), lines.join('\n') + '\n');
  return lines.length;
}
const nSyn = writeJsonl('syntax.jsonl', syntaxFormers);
const nDf = writeJsonl('definitions.jsonl', dfs);
const nAx = writeJsonl('axioms.jsonl', axs);

// ---------- manifest ----------
const typecodeCounts = {};
for (const a of aStmts) typecodeCounts[a.typecode] = (typecodeCounts[a.typecode] || 0) + 1;
const mathboxCount = emitted.filter((a) => mathboxStartLine !== null && a.line > mathboxStartLine).length;
const primitiveSyntax = syntaxFormers.filter((s) => !definitionOfFormer.has(s.label)).map((s) => s.label).sort();
const irregularDfs = dfs.filter((d) => !splitByLabel.get(d.label)).map((d) => d.label).sort();

const manifest = {
  corpus: 'math-mm',
  schema: SCHEMA,
  profile: 'profile-M formal-sector bulk tier (docs/design-bulk-kernel.md; docs/design-math-sector.md §1.1)',
  version: '0.1.0',
  extractionDate: datePin,
  authorship: 'bulk-extracted mechanically from set.mm; formal-sector records (the source is already definitional; full definitional force per design-bulk-kernel.md §honesty-architecture item 4); NOT federation-endorsed',
  recordRule: 'every $a statement of set.mm: typecode!=|- -> syntax-former; |- and df-* -> definition; |- and ax-* -> axiom; other |- $a excluded and listed (empirically zero). $p theorems out of scope (no proof layer, design-math-sector.md L1). No subset truncation: this is the complete $a inventory.',
  nsmBridgePolicy: 'none for all records (bulk mechanical extraction; NSM explication is hand-authored territory). Hand-checked links to the math-v0 corpus live in alignment-v0.json.',
  source: {
    repository: 'https://github.com/metamath/set.mm',
    file: 'set.mm',
    commit,
    sha256: sourceSha256,
    bytes: srcBuf.length,
    mathboxStartLine,
  },
  extractor: {
    version: EXTRACTOR_VERSION,
    contentHash: extractorHash,
    files: extractorFiles,
    hashRule: 'sha256 over the concatenated bytes of the listed files, in listed order',
  },
  counts: {
    records: nSyn + nDf + nAx,
    syntaxFormers: nSyn,
    definitions: nDf,
    axioms: nAx,
    mathboxRecords: mathboxCount,
    aStatementsTotal: aStmts.length,
    aStatementTypecodes: typecodeCounts,
    pStatementsSkipped: db.stats.pProofsSkipped,
    excludedProvableAStatements: excluded.map((a) => a.label),
    irregularDefinitionShapes: irregularDfs,
    fallbackAssignedSyntaxFormers: fallbackAssignedDfs.sort(),
    primitiveSyntaxFormers: { count: primitiveSyntax.length, note: 'syntax formers with no defining df-* (logical/set-theoretic primitives and purely notational formers)', labels: primitiveSyntax.slice(0, 40), truncatedListing: primitiveSyntax.length > 40 },
    unintroducedConstants: [...unintroducedConstants].sort(),
  },
  dag: {
    nodes: nSyn + nDf + nAx,
    edges: edgeCount,
    acyclic,
    nontrivialSccs,
    selfLoops,
    sccNote: nontrivialSccs.length > 0
      ? 'Cycles are the SOURCE\'s real structure, reported as findings: set.mm\'s class-theory bootstrap (df-cleq defines class = via e.; df-clel defines e. via =) is documented by set.mm itself as not-strict definitions, exempt from its definitional soundness check. Depths are computed on the SCC condensation (members share a depth).'
      : 'no cycles found',
    edgeRule: 'record -> dependencies.syntax ∪ dependencies.definitional (see extract.mjs header for the stated dependency semantics)',
    allEdgesPointToEarlierDatabasePosition: backEdgeViolations.length === 0,
    backEdgeViolations: backEdgeViolations.slice(0, 20),
    backEdgeViolationCount: backEdgeViolations.length,
    maxDepth,
    maxDepthWitness: witness,
    depthHistogram: depthHist,
    syntaxFormersUnreachableFromDfAx: unreachedSyntax,
    unreachabilityNote: 'cv (setvar-to-class coercion, "class x") is expected here: its pattern is a bare variable, so token-level constant scanning cannot see uses of it; grammatical parse-tree dependencies would require a full grammar parser (out of scope, stated rule).',
  },
  files: {
    'syntax.jsonl': nSyn,
    'definitions.jsonl': nDf,
    'axioms.jsonl': nAx,
  },
};
fs.writeFileSync(path.join(outDir, 'manifest.json'), JSON.stringify(manifest, null, 2) + '\n');

console.log(`extracted ${nSyn + nDf + nAx} records (${nSyn} syntax, ${nDf} df, ${nAx} ax); maxDepth=${maxDepth}; edges=${edgeCount}; acyclic=${acyclic}; nontrivialSccs=${JSON.stringify(nontrivialSccs)}; backEdgeViolations=${backEdgeViolations.length}; irregular dfs=${irregularDfs.length}; fallbackFormerAssignments=${fallbackAssignedDfs.length}; unintroduced=${unintroducedConstants.size}; unreachedSyntax=${unreachedSyntax.length}`);
