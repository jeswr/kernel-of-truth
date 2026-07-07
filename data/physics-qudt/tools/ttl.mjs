/**
 * Minimal Turtle-subset parser for the QUDT vocabulary files (physics-qudt extractor).
 *
 * Zero-dep, deterministic, fail-closed (house rules; cf. encoder/ conventions).
 * Supports exactly the subset the TopBraid-serialized QUDT vocab files use:
 *   - @prefix directives
 *   - subject blocks: subject predicateObjectList .
 *   - objects: IRIs (<...>), prefixed names, the 'a' verb, booleans,
 *     numeric literals (integer | decimal | double; RAW LEXICAL FORM KEPT —
 *     exactness lives downstream in rational.mjs, never in JS floats),
 *     strings ('...', "...", '''...''', """...""") with \-escapes,
 *     optional @lang / ^^datatype,
 *     blank-node property lists [ ... ] (QUDT factor units)
 *   - comments (# to end of line, outside strings)
 * NOT supported (fail closed with ERR_TTL_*): collections ( ), @base,
 * SPARQL-style PREFIX/BASE, relative IRI resolution, anonymous top-level
 * subjects other than IRIs/prefixed names.
 *
 * parseTurtle(text) -> {
 *   prefixes: Map<string,string>,
 *   subjects: Map<subjectIRI, Map<predicateIRI, Term[]>>  (document order)
 * }
 * Term = { t:'iri', v }
 *      | { t:'lit', v, dt?, lang?, raw? }   (raw = numeric lexical form)
 *      | { t:'bnode', props: Map<predicateIRI, Term[]> }
 */

const err = (code, msg, pos, text) => {
  const line = pos != null && text ? text.slice(0, pos).split('\n').length : '?';
  const e = new Error(`${code}: ${msg} (line ${line})`);
  e.code = code;
  return e;
};

const RDF_TYPE = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type';
const isWS = (c) => c === ' ' || c === '\t' || c === '\n' || c === '\r';
const isPNChar = (c) => /[A-Za-z0-9_\-.%À-￿]/.test(c);

export function parseTurtle(text) {
  let i = 0;
  const n = text.length;
  const prefixes = new Map();
  const subjects = new Map();

  const skipWS = () => {
    for (;;) {
      while (i < n && isWS(text[i])) i++;
      if (i < n && text[i] === '#') { while (i < n && text[i] !== '\n') i++; continue; }
      break;
    }
  };

  const readIriRef = () => {
    // at '<'
    const start = ++i;
    while (i < n && text[i] !== '>') {
      if (text[i] === '\n') throw err('ERR_TTL_IRI', 'newline in IRIREF', i, text);
      i++;
    }
    if (i >= n) throw err('ERR_TTL_IRI', 'unterminated IRIREF', start, text);
    const v = text.slice(start, i);
    i++; // consume '>'
    return v;
  };

  const readPName = () => {
    // prefixed name: PN_PREFIX? ':' PN_LOCAL?  — local may contain '.', not trailing.
    const start = i;
    while (i < n && isPNChar(text[i])) i++;
    if (i >= n || text[i] !== ':') throw err('ERR_TTL_PNAME', `expected ':' in prefixed name near ${JSON.stringify(text.slice(start, start + 24))}`, start, text);
    const prefix = text.slice(start, i);
    i++; // ':'
    const lstart = i;
    while (i < n && isPNChar(text[i])) i++;
    let local = text.slice(lstart, i);
    // Turtle: PN_LOCAL must not end with '.', backtrack trailing dots (statement terminator)
    while (local.endsWith('.')) { local = local.slice(0, -1); i--; }
    const ns = prefixes.get(prefix);
    if (ns === undefined) throw err('ERR_TTL_PREFIX', `undeclared prefix '${prefix}:'`, start, text);
    return ns + local;
  };

  const unescape = (s, pos) => {
    if (!s.includes('\\')) return s;
    let out = '';
    for (let j = 0; j < s.length; j++) {
      const c = s[j];
      if (c !== '\\') { out += c; continue; }
      const d = s[++j];
      switch (d) {
        case 't': out += '\t'; break;
        case 'b': out += '\b'; break;
        case 'n': out += '\n'; break;
        case 'r': out += '\r'; break;
        case 'f': out += '\f'; break;
        case '"': out += '"'; break;
        case "'": out += "'"; break;
        case '\\': out += '\\'; break;
        case 'u': out += String.fromCodePoint(parseInt(s.slice(j + 1, j + 5), 16)); j += 4; break;
        case 'U': out += String.fromCodePoint(parseInt(s.slice(j + 1, j + 9), 16)); j += 8; break;
        default: throw err('ERR_TTL_ESCAPE', `bad escape \\${d}`, pos, text);
      }
    }
    return out;
  };

  const readString = () => {
    const q = text[i];
    const long = text[i + 1] === q && text[i + 2] === q;
    const start = i;
    let body;
    if (long) {
      i += 3;
      const bstart = i;
      for (;;) {
        if (i >= n) throw err('ERR_TTL_STR', 'unterminated long string', start, text);
        if (text[i] === '\\') { i += 2; continue; }
        if (text[i] === q && text[i + 1] === q && text[i + 2] === q) break;
        i++;
      }
      body = text.slice(bstart, i);
      i += 3;
    } else {
      i += 1;
      const bstart = i;
      for (;;) {
        if (i >= n || text[i] === '\n') throw err('ERR_TTL_STR', 'unterminated string', start, text);
        if (text[i] === '\\') { i += 2; continue; }
        if (text[i] === q) break;
        i++;
      }
      body = text.slice(bstart, i);
      i += 1;
    }
    const lit = { t: 'lit', v: unescape(body, start) };
    // optional @lang or ^^datatype
    if (text[i] === '@') {
      i++;
      const ls = i;
      while (i < n && /[A-Za-z0-9-]/.test(text[i])) i++;
      lit.lang = text.slice(ls, i);
    } else if (text[i] === '^' && text[i + 1] === '^') {
      i += 2;
      lit.dt = text[i] === '<' ? readIriRef() : readPName();
    }
    return lit;
  };

  const readNumber = () => {
    const start = i;
    if (text[i] === '+' || text[i] === '-') i++;
    while (i < n && /[0-9]/.test(text[i])) i++;
    if (text[i] === '.' && /[0-9]/.test(text[i + 1])) { i++; while (i < n && /[0-9]/.test(text[i])) i++; }
    if (text[i] === 'e' || text[i] === 'E') {
      i++;
      if (text[i] === '+' || text[i] === '-') i++;
      while (i < n && /[0-9]/.test(text[i])) i++;
    }
    const raw = text.slice(start, i);
    if (!/^[+-]?\d+(\.\d+)?([eE][+-]?\d+)?$/.test(raw)) throw err('ERR_TTL_NUM', `bad numeric literal ${JSON.stringify(raw)}`, start, text);
    const dt = /[eE]/.test(raw) ? 'http://www.w3.org/2001/XMLSchema#double'
      : raw.includes('.') ? 'http://www.w3.org/2001/XMLSchema#decimal'
        : 'http://www.w3.org/2001/XMLSchema#integer';
    return { t: 'lit', v: raw, raw, dt };
  };

  const readObject = () => {
    skipWS();
    const c = text[i];
    if (c === '<') return { t: 'iri', v: readIriRef() };
    if (c === '"' || c === "'") return readString();
    if (c === '[') {
      i++; // '['
      const props = readPredicateObjectList(']');
      skipWS();
      if (text[i] !== ']') throw err('ERR_TTL_BNODE', 'unterminated blank node property list', i, text);
      i++;
      return { t: 'bnode', props };
    }
    if (c === '(') throw err('ERR_TTL_COLLECTION', 'RDF collections not supported by this subset parser', i, text);
    if (c === '+' || c === '-' || /[0-9]/.test(c)) return readNumber();
    // bare words: true/false, or prefixed name
    if (text.startsWith('true', i) && !isPNChar(text[i + 4])) { i += 4; return { t: 'lit', v: 'true', dt: 'http://www.w3.org/2001/XMLSchema#boolean' }; }
    if (text.startsWith('false', i) && !isPNChar(text[i + 5])) { i += 5; return { t: 'lit', v: 'false', dt: 'http://www.w3.org/2001/XMLSchema#boolean' }; }
    return { t: 'iri', v: readPName() };
  };

  const readVerb = () => {
    skipWS();
    if (text[i] === 'a' && (isWS(text[i + 1]) || text[i + 1] === '<')) { i++; return RDF_TYPE; }
    if (text[i] === '<') return readIriRef();
    return readPName();
  };

  // reads until '.' (terminator consumed by caller) or `end` char (not consumed)
  const readPredicateObjectList = (end) => {
    const props = new Map();
    for (;;) {
      skipWS();
      if (i >= n) throw err('ERR_TTL_EOF', 'unexpected EOF in predicate-object list', i, text);
      if (end && text[i] === end) return props;
      if (!end && text[i] === '.') return props;
      const pred = readVerb();
      const list = props.get(pred) ?? [];
      if (!props.has(pred)) props.set(pred, list);
      for (;;) {
        list.push(readObject());
        skipWS();
        if (text[i] === ',') { i++; continue; }
        break;
      }
      skipWS();
      if (text[i] === ';') {
        i++;
        continue; // possibly trailing ';' before end/'.' — loop re-checks
      }
      if (end && text[i] === end) return props;
      if (!end && text[i] === '.') return props;
      throw err('ERR_TTL_PUNCT', `expected ';' ${end ? `or '${end}'` : "or '.'"} after object, got ${JSON.stringify(text[i])}`, i, text);
    }
  };

  for (;;) {
    skipWS();
    if (i >= n) break;
    if (text.startsWith('@prefix', i)) {
      i += 7;
      skipWS();
      const ps = i;
      while (i < n && text[i] !== ':') i++;
      const prefix = text.slice(ps, i).trim();
      i++; // ':'
      skipWS();
      if (text[i] !== '<') throw err('ERR_TTL_PREFIX', '@prefix expects <IRI>', i, text);
      const iri = readIriRef();
      skipWS();
      if (text[i] !== '.') throw err('ERR_TTL_PREFIX', "@prefix missing terminating '.'", i, text);
      i++;
      prefixes.set(prefix, iri);
      continue;
    }
    if (text.startsWith('@base', i) || text.startsWith('PREFIX', i) || text.startsWith('BASE', i)) {
      throw err('ERR_TTL_DIRECTIVE', 'only @prefix directives are supported', i, text);
    }
    // subject
    const subj = text[i] === '<' ? readIriRef() : readPName();
    const props = readPredicateObjectList(null);
    skipWS();
    if (text[i] !== '.') throw err('ERR_TTL_PUNCT', "expected '.' terminating subject block", i, text);
    i++;
    // merge if subject re-appears (QUDT files do not, but be safe + deterministic)
    const existing = subjects.get(subj);
    if (existing) {
      for (const [p, terms] of props) {
        const l = existing.get(p) ?? [];
        if (!existing.has(p)) existing.set(p, l);
        l.push(...terms);
      }
    } else {
      subjects.set(subj, props);
    }
  }
  return { prefixes, subjects };
}

/** Convenience accessors (deterministic: document order preserved). */
export const objs = (props, pred) => props.get(pred) ?? [];
export const iris = (props, pred) => objs(props, pred).filter((t) => t.t === 'iri').map((t) => t.v);
export const lits = (props, pred) => objs(props, pred).filter((t) => t.t === 'lit');
export { RDF_TYPE };
