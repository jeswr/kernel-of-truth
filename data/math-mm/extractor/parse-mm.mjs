// parse-mm.mjs — minimal, correct Metamath (.mm) parser for the Kernel of Truth
// bulk-mining pipeline (bead kernel-of-truth-hvu).
//
// Scope (deliberate): statements and their dependency structure ONLY.
//   - tokenizer (Metamath spec: whitespace-separated tokens; $( ... $) comments)
//   - $c / $v / $f / $e / $a / $p / $d handling with ${ ... $} scoping
//   - $p proofs are SKIPPED (both normal and compressed form) — this is an
//     extractor, not a verifier; over a dozen independent verifiers already
//     check set.mm (docs/design-math-sector.md §1.1).
//   - $[ ... $] file inclusions are REJECTED (fail closed): set.mm is a single
//     file; silently resolving includes would un-pin the source.
//
// Spec source: Metamath book (metamath.pdf) §4.1 "Specification of the
// Metamath Language"; us.metamath.org. The format is simple by design.
//
// Zero runtime dependencies (project convention: encoder/ is zero-dep too).
// No silent fallbacks; fail closed with ERR_* codes (project convention).

'use strict';

export class MMParseError extends Error {
  constructor(code, message, line) {
    super(`${code}: ${message}${line !== undefined ? ` (line ${line})` : ''}`);
    this.code = code;
    this.line = line;
  }
}

const KEYWORDS = new Set([
  '$c', '$v', '$f', '$e', '$a', '$p', '$d', '$.', '$=', '$(', '$)', '$[', '$]', '${', '$}',
]);

// Per spec §4.1.1: math symbols may use any printable non-whitespace ASCII
// except '$'; labels use [A-Za-z0-9._-].
const LABEL_RE = /^[A-Za-z0-9._-]+$/;

/**
 * Tokenize .mm source. Yields {tok, line} with 1-based line numbers.
 * Comments are NOT stripped here (the parser handles $( ... $) so that it can
 * attach the last comment preceding a statement as annotation-layer material).
 */
export function* tokenize(src) {
  const re = /\S+/g;
  let line = 1;
  let lastIndex = 0;
  let m;
  while ((m = re.exec(src)) !== null) {
    // count newlines between lastIndex and m.index
    for (let i = lastIndex; i < m.index; i++) {
      if (src.charCodeAt(i) === 10) line++;
    }
    lastIndex = m.index;
    yield { tok: m[0], line };
  }
}

/**
 * Parse a .mm database.
 *
 * Returns {
 *   constants: Map<name, {line, declIndex}>,        // $c (outermost only, enforced)
 *   assertions: [ {                                  // every $a and $p, database order
 *     label, kind: 'a'|'p', typecode, symbols: [..], // symbols EXCLUDES the typecode
 *     line, comment,                                 // comment = last $( .. $) before it (or null)
 *     mandatoryVars: [ {name, typecode, fLabel} ],   // first-occurrence order
 *     eHyps: [ {label, typecode, symbols, line} ],   // active $e (mandatory by definition)
 *     dPairs: [ [v1, v2], ... ],                     // mandatory $d pairs, canonically ordered
 *     index                                          // 0-based database order among assertions
 *   } ],
 *   labels: Map<label, {kind, line}>,                // all labels ($f/$e/$a/$p) for dup detection
 *   stats: { tokenCount, commentCount, pProofsSkipped, maxScopeDepth }
 * }
 *
 * Proof token streams of $p statements are consumed and discarded.
 */
export function parseMM(src) {
  const constants = new Map();
  const assertions = [];
  const labels = new Map();
  const stats = { tokenCount: 0, commentCount: 0, pProofsSkipped: 0, maxScopeDepth: 0 };

  // Scope stack. Each frame: vars:Set, fHyps:[{label,typecode,var,line}],
  // eHyps:[...], dPairs:[[a,b],...]
  const scopes = [{ vars: new Set(), fHyps: [], eHyps: [], dPairs: [] }];

  const it = tokenize(src);
  let cur = it.next();
  let lastComment = null; // most recent comment text (annotation layer)
  let declIndex = 0;

  const next = () => {
    const v = cur;
    cur = it.next();
    if (!v.done) stats.tokenCount++;
    return v.done ? null : v.value;
  };
  const peek = () => (cur.done ? null : cur.value);

  const err = (code, msg, line) => { throw new MMParseError(code, msg, line); };

  const readComment = (openLine) => {
    // spec: comments may not nest; $( must be matched by $)
    const parts = [];
    for (;;) {
      const t = next();
      if (t === null) err('ERR_MM_UNCLOSED_COMMENT', 'EOF inside $( ... $)', openLine);
      if (t.tok === '$)') break;
      if (t.tok === '$(') err('ERR_MM_NESTED_COMMENT', 'comments may not nest', t.line);
      parts.push(t.tok);
    }
    stats.commentCount++;
    return parts.join(' ');
  };

  const readUntilDot = (what, startLine) => {
    const out = [];
    for (;;) {
      const t = next();
      if (t === null) err('ERR_MM_UNCLOSED_STATEMENT', `EOF inside ${what}`, startLine);
      if (t.tok === '$.') return out;
      if (t.tok === '$(') { readComment(t.line); continue; } // comments legal inside statements; discarded
      if (KEYWORDS.has(t.tok)) {
        err('ERR_MM_KEYWORD_IN_STATEMENT', `unexpected ${t.tok} inside ${what}`, t.line);
      }
      out.push(t.tok);
    }
  };

  const isVarActive = (name) => scopes.some((s) => s.vars.has(name));
  const activeFHyp = (name) => {
    for (let i = scopes.length - 1; i >= 0; i--) {
      for (let j = scopes[i].fHyps.length - 1; j >= 0; j--) {
        if (scopes[i].fHyps[j].var === name) return scopes[i].fHyps[j];
      }
    }
    return null;
  };

  const registerLabel = (label, kind, line) => {
    if (!LABEL_RE.test(label)) err('ERR_MM_BAD_LABEL', `illegal label token '${label}'`, line);
    if (labels.has(label)) err('ERR_MM_DUP_LABEL', `duplicate label '${label}'`, line);
    if (constants.has(label) || isVarActive(label)) {
      err('ERR_MM_LABEL_CLASHES_SYMBOL', `label '${label}' clashes with active math symbol`, line);
    }
    labels.set(label, { kind, line });
  };

  const buildAssertion = (label, kind, typecode, symbols, line, comment) => {
    // Mandatory frame per spec §4.2.7: variables occurring in the assertion's
    // math string or in any ACTIVE $e hypothesis; their active $f hypotheses
    // are mandatory; all active $e are mandatory; $d pairs over mandatory vars.
    const activeE = [];
    for (const s of scopes) for (const e of s.eHyps) activeE.push(e);

    const varSeen = new Map(); // name -> order of first occurrence
    const noteVars = (syms) => {
      for (const sym of syms) {
        if (!varSeen.has(sym) && isVarActive(sym)) varSeen.set(sym, varSeen.size);
      }
    };
    noteVars(symbols); // (typecode is already gate-checked as a declared constant at all call sites)
    for (const e of activeE) noteVars(e.symbols);

    const mandatoryVars = [];
    for (const [name] of [...varSeen.entries()].sort((a, b) => a[1] - b[1])) {
      const f = activeFHyp(name);
      if (f === null) err('ERR_MM_NO_FLOATING_HYP', `variable '${name}' has no active $f`, line);
      mandatoryVars.push({ name, typecode: f.typecode, fLabel: f.label });
    }

    const mand = new Set(varSeen.keys());
    const dSeen = new Set();
    const dPairs = [];
    for (const s of scopes) {
      for (const [a, b] of s.dPairs) {
        if (mand.has(a) && mand.has(b)) {
          const key = a < b ? `${a} ${b}` : `${b} ${a}`;
          if (!dSeen.has(key)) { dSeen.add(key); dPairs.push(key.split(' ')); }
        }
      }
    }
    dPairs.sort((p, q) => (p[0] === q[0] ? (p[1] < q[1] ? -1 : 1) : p[0] < q[0] ? -1 : 1));

    return {
      label, kind, typecode, symbols, line, comment,
      mandatoryVars,
      eHyps: activeE.map((e) => ({ label: e.label, typecode: e.typecode, symbols: e.symbols, line: e.line })),
      dPairs,
      index: assertions.length,
    };
  };

  for (;;) {
    const t = next();
    if (t === null) break;
    const { tok, line } = t;

    if (tok === '$(') { lastComment = readComment(line); continue; }
    if (tok === '$[') err('ERR_MM_INCLUDE_UNSUPPORTED', 'file inclusion $[ ... $] not supported (set.mm is a single pinned file)', line);
    if (tok === '${') {
      scopes.push({ vars: new Set(), fHyps: [], eHyps: [], dPairs: [] });
      stats.maxScopeDepth = Math.max(stats.maxScopeDepth, scopes.length - 1);
      continue;
    }
    if (tok === '$}') {
      if (scopes.length === 1) err('ERR_MM_UNMATCHED_SCOPE_CLOSE', '$} without ${', line);
      scopes.pop();
      continue;
    }
    if (tok === '$c') {
      if (scopes.length !== 1) err('ERR_MM_C_IN_INNER_SCOPE', '$c only legal in outermost scope', line);
      for (const c of readUntilDot('$c', line)) {
        if (constants.has(c)) err('ERR_MM_DUP_CONSTANT', `constant '${c}' redeclared`, line);
        if (isVarActive(c)) err('ERR_MM_CONST_VAR_CLASH', `'${c}' already an active variable`, line);
        constants.set(c, { line, declIndex: declIndex++ });
      }
      continue;
    }
    if (tok === '$v') {
      for (const v of readUntilDot('$v', line)) {
        if (constants.has(v)) err('ERR_MM_VAR_CONST_CLASH', `'${v}' already a constant`, line);
        if (isVarActive(v)) err('ERR_MM_DUP_VAR', `variable '${v}' already active`, line);
        scopes[scopes.length - 1].vars.add(v);
      }
      continue;
    }
    if (tok === '$d') {
      const vars = readUntilDot('$d', line);
      if (vars.length < 2) err('ERR_MM_D_TOO_SHORT', '$d needs >= 2 variables', line);
      const pairs = [];
      for (let i = 0; i < vars.length; i++) {
        if (!isVarActive(vars[i])) err('ERR_MM_D_NOT_VAR', `'${vars[i]}' in $d is not an active variable`, line);
        for (let j = i + 1; j < vars.length; j++) {
          if (vars[i] === vars[j]) err('ERR_MM_D_REPEATED_VAR', `variable '${vars[i]}' repeated in $d`, line);
          pairs.push([vars[i], vars[j]]);
        }
      }
      scopes[scopes.length - 1].dPairs.push(...pairs);
      continue;
    }
    if (KEYWORDS.has(tok)) err('ERR_MM_UNEXPECTED_KEYWORD', `unexpected '${tok}' at top level`, line);

    // Otherwise: a label, followed by $f / $e / $a / $p.
    const label = tok;
    const kw = next();
    if (kw === null) err('ERR_MM_EOF_AFTER_LABEL', `EOF after label '${label}'`, line);

    if (kw.tok === '$f') {
      registerLabel(label, 'f', line);
      const body = readUntilDot('$f', line);
      if (body.length !== 2) err('ERR_MM_F_ARITY', '$f must be exactly: typecode var', line);
      const [typecode, v] = body;
      if (!constants.has(typecode)) err('ERR_MM_F_TYPECODE', `$f typecode '${typecode}' not a declared constant`, line);
      if (!isVarActive(v)) err('ERR_MM_F_NOT_VAR', `$f symbol '${v}' not an active variable`, line);
      if (activeFHyp(v) !== null) err('ERR_MM_F_DUP', `variable '${v}' already has an active $f`, line);
      scopes[scopes.length - 1].fHyps.push({ label, typecode, var: v, line });
      continue;
    }
    if (kw.tok === '$e') {
      registerLabel(label, 'e', line);
      const body = readUntilDot('$e', line);
      if (body.length < 1) err('ERR_MM_E_EMPTY', '$e needs a typecode', line);
      const typecode = body[0];
      if (!constants.has(typecode)) err('ERR_MM_E_TYPECODE', `$e typecode '${typecode}' not a declared constant`, line);
      scopes[scopes.length - 1].eHyps.push({ label, typecode, symbols: body.slice(1), line });
      continue;
    }
    if (kw.tok === '$a') {
      registerLabel(label, 'a', line);
      const body = readUntilDot('$a', line);
      if (body.length < 1) err('ERR_MM_A_EMPTY', '$a needs a typecode', line);
      const typecode = body[0];
      if (!constants.has(typecode)) err('ERR_MM_A_TYPECODE', `$a typecode '${typecode}' not a declared constant`, line);
      assertions.push(buildAssertion(label, 'a', typecode, body.slice(1), line, lastComment));
      lastComment = null;
      continue;
    }
    if (kw.tok === '$p') {
      registerLabel(label, 'p', line);
      // math symbols until $=, then SKIP proof tokens until $.
      // (compressed proofs are '( labels ) AAAB...' blobs — skipped identically)
      const symbols = [];
      let typecode = null;
      let sawProof = false;
      for (;;) {
        const u = next();
        if (u === null) err('ERR_MM_UNCLOSED_STATEMENT', `EOF inside $p '${label}'`, line);
        if (u.tok === '$(') { readComment(u.line); continue; }
        if (u.tok === '$=') { sawProof = true; break; }
        if (u.tok === '$.') break; // $p without $= is illegal per spec; tolerate for stats? -> fail closed:
        if (KEYWORDS.has(u.tok)) err('ERR_MM_KEYWORD_IN_STATEMENT', `unexpected ${u.tok} in $p statement`, u.line);
        if (typecode === null) typecode = u.tok; else symbols.push(u.tok);
      }
      if (!sawProof) err('ERR_MM_P_WITHOUT_PROOF', `$p '${label}' has no $= proof`, line);
      if (typecode === null) err('ERR_MM_P_EMPTY', '$p needs a typecode', line);
      if (!constants.has(typecode)) err('ERR_MM_P_TYPECODE', `$p typecode '${typecode}' not a declared constant`, line);
      // skip proof
      for (;;) {
        const u = next();
        if (u === null) err('ERR_MM_UNCLOSED_PROOF', `EOF inside proof of '${label}'`, line);
        if (u.tok === '$.') break;
        if (u.tok === '$(') { readComment(u.line); continue; }
      }
      stats.pProofsSkipped++;
      assertions.push(buildAssertion(label, 'p', typecode, symbols, line, lastComment));
      lastComment = null;
      continue;
    }
    err('ERR_MM_BAD_STATEMENT', `label '${label}' followed by '${kw.tok}', expected $f/$e/$a/$p`, kw.line);
  }

  if (scopes.length !== 1) err('ERR_MM_UNCLOSED_SCOPE', `${scopes.length - 1} unclosed \${`, undefined);
  return { constants, assertions, labels, stats };
}
